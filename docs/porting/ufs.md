# UFS porting

Start with the storage section of the device's `porting.toml` and the
[component catalog](/reference/components). The official implementation is
[ShengUfs](/drivers/sheng-ufs), with runtime class `NativeUfs`.

ShengUfs combines SM8550 controller access, firmware adoption, SMMU handling,
GPT/window parsing and board persistence policy. Its hardware constants and
board policy require review for each target.

Use [driver build integration](/porting/drivers#build-integration) to connect
initialization, archive recipes and the OS ABI, then run this page's hardware checks.

## Sources and interfaces {#source-map}

These links identify reviewed source revisions. Match interfaces to the selected
SoC, component and OS versions. The linked device sources provide board integration
examples.

| Implementation | Source | What to read and implement |
| --- | --- | --- |
| Controller and DMA | [NativeUfs.cpp](https://github.com/UniXNU/ShengUfs/blob/e2b32cc429e8cf1501161c1d8c517f8994ceb9b2/NativeUfs.cpp), [SmmuTakeover.h](https://github.com/UniXNU/ShengUfs/blob/e2b32cc429e8cf1501161c1d8c517f8994ceb9b2/SmmuTakeover.h) | Request-list ownership, mappings and context takeover |
| Command completion | [RootCommands.h](https://github.com/UniXNU/ShengUfs/blob/e2b32cc429e8cf1501161c1d8c517f8994ceb9b2/RootCommands.h#L33) | `hostSubmit`: descriptors, doorbell, timeout, OCS, response and SCSI status |
| Storage policy | [RootLayout.h](https://github.com/UniXNU/ShengUfs/blob/e2b32cc429e8cf1501161c1d8c517f8994ceb9b2/RootLayout.h), [RootPublication.h](https://github.com/UniXNU/ShengUfs/blob/e2b32cc429e8cf1501161c1d8c517f8994ceb9b2/RootPublication.h) | GPT/window bounds and root IOMedia publication |
| Clock state | [GccUfs.h](https://github.com/UniXNU/ShengUfs/blob/e2b32cc429e8cf1501161c1d8c517f8994ceb9b2/GccUfs.h) | Branch enable and hardware-gating interpretation |

## Procedure {#procedure}

1. Fill the [hardware inventory](#hardware-inventory) from target sources. Resolve controller, PHY, clocks, resets, SMMU and DMA ownership before programming them.
2. Implement or adapt the [initialization sequence](#initialization-and-ownership). Check the [recorded findings](#findings-to-reuse) against the target controller and firmware state.
3. Add the matching component, archive recipe, kernel flags and root settings using [Configuration](#configuration). Build the selected kernel with the matching storage ABI inputs.
4. Verify the [milestones](#completion-criteria) in order: register access, DMA, command completion, known-block reads, root mount, then persistence. Record the result of each completed milestone.
5. Update the storage area of `porting.toml`, run its checker, and continue with [display and brightness](/porting/display).

## Hardware inventory

| Input | Record before implementation |
| --- | --- |
| Controller | Compatible value, revision, MMIO base/length, capabilities and interrupt routing |
| PHY | Register ranges, lanes, reference clock, tuning source and initialization owner |
| Clocks | Provider, clock IDs, rates, parent selection, branch gates and interconnect votes |
| Reset and power | Reset lines, regulators, power domains, sequence and firmware ownership |
| SMMU | Instance, stream IDs, stream masks, context banks, address width and existing mappings |
| DMA | Buffer allocation, physical/IOVA relationship, alignment, coherency and cache maintenance |
| Handoff | HCE/HCS, link state, power mode, request-list base and outstanding commands |
| Storage layout | LUNs, block sizes, capacity, GPT, root windows, Data and log reservations |
| OS interface | Storage ABI, prelink inputs, publication/matching and completion behavior |

Cite the board DTS, SoC documentation, firmware code or measured state for each
value. Put shared controller resources in the SoC DTSI and board wiring or
policy in the device repository. Describe register widths, parent address cells,
`ranges`, interrupt providers and IOMMU references using the
[device-tree bindings](/porting/device-tree).

The SM8550 reference DTSI exports host `0x01d84000/0x3000` and PHY
`0x01d80000/0x2000`. GCC at `0x00100000` and apps-SMMU handling for stream
`0x60` are implemented in ShengUfs. The current driver reads those resources
through its C++ constants and operations. Converting a resource to a DTS property
also requires changing its consumer and validating the generated ADT value.

## Initialization and ownership

1. Read controller, clock, PHY, link and SMMU state using the documented access widths.
2. Establish which clocks, resets and power domains firmware has configured.
3. Select firmware-state adoption or a fully specified controller/PHY initialization sequence.
4. Allocate request descriptors and data buffers; establish their DMA reachability.
5. Establish exclusive ownership of the request list and selected SMMU context.
6. Submit a bounded command and inspect transfer, response and SCSI status.
7. Read capacity and known blocks before publishing a root device.

ShengUfs adopts an existing firmware request list and uses a polled request slot.
Porting this path requires the request-list state and ownership checks in
`NativeUfs.cpp`. A board requiring cold initialization needs its PHY, reset,
clock and power sequence implemented and recorded.

## Findings to reuse

- An idle hardware-gated AHB branch can report `CLK_OFF`. Inspect the branch
  enable and hardware-gating bits together. See `GccUfs.h`.
- SMMU bypass is bounded by supported address widths. Check the complete DMA
  range and existing stream/context-bank ownership. See `SmmuTakeover.h`.
- Capacity, GPT and root-window bounds are separate checks. Keep all LBA-to-byte
  conversions tied to the observed logical block size. See `RootLayout.h`.
- Root reads, persistent Data writes and reset handling have separate completion
  criteria. Record the allocation and recovery method for each write exercise.
- The driver that takes over the apps SMMU also owns any stage 1 window another
  device needs. ShengUfs sets one up for the display bank (`sheng-dpu-scanout`)
  and one for the WiFi endpoint (`sheng-wifi=2` or more); both are off by default.
  Audio streams stay in pass-through: a translating context resets the reference board.

The [reference storage record](/devices/sheng#storage) supplies board values,
implementation references and current limits.

## Configuration

Select the matching storage component in the complete `[components] include`
array. Add its recipe at the required position in `[kernel] archives`. Arrays
replace inherited arrays. A reference selection includes:

```toml
# Entries within the complete device selections:
# [components] include: "ShengUfs"
# [kernel] archives: "component:ShengUfs"

[userdata]
# Set first_lba, last_lba and lba_bytes from the target GPT.

[payload.adt]
# Set root_match_volume_uuid from the selected APFS volume.
```

Obtain the target geometry from its GPT and the root UUID from the selected volume.
Preserve other required `payload.adt` fields. Enable `CONFIG_XNU_NATIVE_UFS=y` in the selected defconfig and include
`native-ufs-root=1` in the complete kernel argument array for this runtime.

The component source is pinned in the device repository. Shared build tools
assemble it into the target's `drivers/ShengUfs` path. Storage ABI bindings need
the selected kernelcache and matching audit inputs.

## Completion criteria

| Milestone | Required observation |
| --- | --- |
| Hardware inventory | Controller, PHY, clock/reset/power and SMMU values have sources and ownership |
| Host access | Registers are readable and clock/link state matches the chosen initialization path |
| DMA and commands | Buffers are reachable; command completion and failures are handled |
| Block reads | Capacity and known-block reads match the selected LUN and logical block size |
| Root | GPT and root windows are bounded; the configured root mounts and starts userland |
| Persistence | Writes remain in the allocated Data region and survive the documented reboot/reset sequence |

Update the storage record at each milestone. Keep source, host and device
results at their corresponding [completion levels](/porting/records#completion-levels).

```sh
./unixnu defconfig myboard_defconfig -D /path/to/device
./unixnu status --json -D /path/to/device
./unixnu build kernel -D /path/to/device
python3 scripts/porting-record.py check --device /path/to/device
```

## Next step

[Adapt display and brightness](/porting/display) after the root path is ready. The [driver checklist](/porting/drivers) covers the remaining subsystems.

For the arm64e public-source build path and its current linking/runtime limits, see [public-source driver builds](/porting/migration#source-drivers). Historical iOS 17 device results do not qualify this path.
