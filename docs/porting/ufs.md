# UFS porting

Start with the storage section of the device's `porting.toml` and the
[component catalog](/reference/components). The official implementation is
`ShengUfs`, with runtime class `NativeUfs`.

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
| Controller and DMA | [NativeUfs.cpp](https://github.com/UniXNU/ShengUfs/blob/fd420df000f43213d9cd019725abff0849c98c72/NativeUfs.cpp#L1108), [SmmuTakeover.h](https://github.com/UniXNU/ShengUfs/blob/fd420df000f43213d9cd019725abff0849c98c72/SmmuTakeover.h), [RootTransportLayout.h](https://github.com/UniXNU/ShengUfs/blob/fd420df000f43213d9cd019725abff0849c98c72/RootTransportLayout.h) | Request-list ownership, slot layout, mappings and context takeover |
| Command completion | [RootCommands.h](https://github.com/UniXNU/ShengUfs/blob/fd420df000f43213d9cd019725abff0849c98c72/RootCommands.h#L89), [NativeUfs.cpp](https://github.com/UniXNU/ShengUfs/blob/fd420df000f43213d9cd019725abff0849c98c72/NativeUfs.cpp#L1017) | `hostIssue`/`hostAwait`: descriptors, doorbell, completion interrupt, hybrid polling, OCS, response and SCSI status |
| Queueing and DMA | [RootCommands.h](https://github.com/UniXNU/ShengUfs/blob/fd420df000f43213d9cd019725abff0849c98c72/RootCommands.h#L377) | Slot pool, zero-copy PRDT (`hostBuildPrds`), busy retries |
| Storage policy | [RootLayout.h](https://github.com/UniXNU/ShengUfs/blob/fd420df000f43213d9cd019725abff0849c98c72/RootLayout.h), [RootPublication.h](https://github.com/UniXNU/ShengUfs/blob/fd420df000f43213d9cd019725abff0849c98c72/RootPublication.h) | GPT/window bounds and root IOMedia publication |
| Clock state | [GccUfs.h](https://github.com/UniXNU/ShengUfs/blob/fd420df000f43213d9cd019725abff0849c98c72/GccUfs.h) | Branch enable and hardware-gating interpretation |

## Procedure {#procedure}

1. Fill the [hardware inventory](#hardware-inventory) from target sources. Resolve controller, PHY, clocks, resets, SMMU and DMA ownership before programming them.
2. Implement or adapt the [initialization sequence](#initialization-and-ownership). Check the [recorded findings](#findings-to-reuse) against the target controller and firmware state.
3. Add the matching component, archive recipe, kernel flags and root settings using [Configuration](#configuration). Build the selected kernel with the matching storage ABI inputs.
4. Verify the [milestones](#completion-criteria) in order: register access, DMA, command completion, known-block reads, root mount, persistence, then [performance](#performance). Record the result of each completed milestone.
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

ShengUfs adopts the firmware's controller and link state, then moves the request
list to its own write-combined page and runs up to 32 commands at once, one per
slot. Completion uses the controller interrupt with hybrid polling, and
page-aligned buffers are transferred by zero-copy DMA. Porting this path
requires the request-list state and ownership checks in `NativeUfs.cpp`. A board
requiring cold initialization needs its PHY, reset, clock and power sequence
implemented and recorded.

## Findings to reuse

- An idle hardware-gated AHB branch can report `CLK_OFF`. Inspect the branch
  enable and hardware-gating bits together. See `GccUfs.h`.
- SMMU bypass is bounded by supported address widths. Check the complete DMA
  range and existing stream/context-bank ownership. See `SmmuTakeover.h`.
- Capacity, GPT and root-window bounds are separate checks. Keep all LBA-to-byte
  conversions tied to the observed logical block size. See `RootLayout.h`.
- Root reads, persistent Data writes and reset handling have separate completion
  criteria. Record the allocation and recovery method for each write exercise.
- Request list entries are 32 bytes, so two share a 64-byte cache line. On a
  non-coherent stream, cleaning one entry can write a stale copy over the
  controller's completion of its neighbour. Put the list on a write-combined page
  (Linux uses coherent DMA memory), or give each slot an entry of its own line.
- UTRCS, and with it the completion interrupt, is raised only for descriptors
  with the UTRD interrupt bit (dword 0 bit 24) set. Enable UTRCE alone and find
  completed commands by their cleared doorbell bits, as Linux ufshcd does.
- Sleeping on every completion costs more than the command at small sizes. A
  wait that polls for its first 200 microseconds, then sleeps, keeps small-block
  throughput at queue depth 8 and 32 while long commands leave the CPU.
- Read the link state with DME_GET (`PA_TxGear`, `PA_RxGear`, `PA_HSSeries`,
  `PA_PWRMode`) before changing it. The reference firmware leaves HS-G5 Rate A
  on two lanes in FAST mode.
- The driver that takes over the apps SMMU also owns any stage 1 window another
  device needs. ShengUfs sets one up for the display bank (`dpu-scanout`)
  and one for the WiFi endpoint (`wifi=2` or more); both are off by default.
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
| Performance | Every read test matches or exceeds the mainline Linux driver on the same device and LBAs |

Update the storage record at each milestone. Keep source, host and device
results at their corresponding [completion levels](/porting/records#completion-levels).

```sh
./unixnu defconfig myboard_defconfig -D /path/to/device
./unixnu status --json -D /path/to/device
./unixnu build kernel -D /path/to/device
python3 scripts/porting-record.py check --device /path/to/device
```

## Performance {#performance}

Compare the driver with the mainline Linux driver on the same device, the same
LBAs and the same test sequence. The reference board provides both sides:

| Side | Tool | Output |
| --- | --- | --- |
| Linux | `scripts/linux-ufsbench.py` boots the read-only Linux reader, runs `package/linux-log/ufsbench.c` with O_DIRECT and returns to fastboot | `bench.txt` and the kernel's UFS link and queue facts |
| XNU | `ufs-bench=1` runs the same tests in the kernel before the boot goes on, checks zero-copy reads against the data-area path and restarts into fastboot | `ufsbench` lines in the UFS log's message buffer |

Each side reads 4 KiB, 16 KiB, 128 KiB and 1 MiB at random at queue depth 1, 8
and 32, then sequentially, inside the flashed root image. Run each side at least
three times and compare the means:

```sh
python3 scripts/linux-ufsbench.py --reader <reader.img> --out out/linux-bench-1
python3 scripts/compare-ufsbench.py --linux out/linux-bench-*/bench.txt --xnu <log>/msgbuf.txt ...
```

On the reference board every test matches or exceeds mainline Linux 7.2
(`ufshcd-qcom`). The closest is 4 KiB at queue depth 8 (ratio 1.01); 1 MiB reads
reach 2.2 GB/s at queue depth 1 and 3.7 GB/s at 8, against 1.3 and 1.9 GB/s.

## Next step

[Adapt display and brightness](/porting/display) after the root path is ready. The [driver checklist](/porting/drivers) covers the remaining subsystems.

For the arm64e public-source build path and its current linking/runtime limits, see [public-source driver builds](/porting/migration#source-drivers). Historical iOS 17 device results do not qualify this path.
