# Xiaomi Redmi Note 3 \(Kenzo\) Snapdragon 650

[CodeDevB7/UniXNU-kenzo](https://github.com/CodeDevB7/UniXNU-kenzo)

<div v-pre>

Xiaomi Redmi Note 3 \(kenzo\) Snapdragon 650 porting record.

Source record: [porting.toml](https://github.com/CodeDevB7/UniXNU-kenzo/blob/c472ccc1102a772f9e84261d8240be4eec6d7dca/porting.toml), `c472ccc1102a772f9e84261d8240be4eec6d7dca`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `host-verified` |
| [Firmware and boot](#firmware) | `planned` |
| [CPU and interrupts](#cpu) | `implemented` |
| [Memory and DMA](#memory) | `planned` |
| [Storage and root](#storage) | `planned` |
| [Display](#display) | `planned` |
| [Input](#input) | `planned` |
| [GPU](#gpu) | `planned` |
| [Network](#network) | `planned` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `planned` |
| [Image assembly](#packaging) | `planned` |
| [Diagnostics](#diagnostics) | `planned` |

## Configuration {#configuration}

`host-verified`

Components: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`, `DarwinBoot`.

### Hardware and dependencies

- Xiaomi Redmi Note 3, codename kenzo; Qualcomm MSM8956; selected profile ipados-17.7.11-21H461.
- Shared SoC feed points to CodeDevB7/UniXNU-msm8956-common at c9652aca1fe3c530ef79f5dae584dd85e61b1f8c.

### Configuration

- board.toml selects ArmDTPlatform, ArmCpu, SoftwareAES, XnuPrelink and DarwinBoot; kenzo\_defconfig; SoC and OS config fragments; ordered arch, SoC, OS and device patch series.
- \[package\] unixnu is ../UniXNU and \[package.defconfig\] maps ipados-17.7.11-21H461 to kenzo\_defconfig.

### Procedure

- Resolve board configuration from the UniXNU checkout with unixnu status -D UniXNU-kenzo.
- Run scripts/package.sh --check --os ipados-17.7.11-21H461 from the device repository after required local sources are available.
- Dispatch .github/workflows/kernel.yml to compile only the kernel on a macOS runner and inspect its redacted logs.

### Development findings

- The current repository uses format 2 and the shared SoC feed; the older handoff's build workflow description predates the current package interface.
- The package script previously stopped immediately because \[package\].unixnu was absent; after recording the path and profile-to-defconfig mapping, host preflight resolved kenzo\_defconfig and all 59 patches.
- The local set of 86 extracted DTBs contains Qualcomm MSM8956 reference platforms, but no root model/compatible identifying Kenzo; these files do not validate board wiring.
- The kernel-only macOS workflow calls UniXNU's reusable build and uploads text logs only. Its pre-build helper removes only the optional Sheng PMGR probe hunk from the generic boot-progress patch; it fails closed if the upstream hunk layout changes.
- Local compilation was stopped at the user's request after filesystem and bootstrap issues; no kernel artifact is claimed. The workflow run is the next build attempt.

### Completion criteria

- The pinned SoC source resolves; package preflight writes the selected configuration and patch resolution completes for the selected OS profile.

### Current limits

- Package preflight, patch resolution and standalone DTS-to-ADT generation are host-verified. Kernel, UEFI firmware, payload, image assembly and device boot are unverified. The macOS Actions kernel run is pending. Firmware repository, image inputs and device seed are not configured.

### Next action

- Run the macOS kernel workflow and record its result; identify the Kenzo UEFI source and verify board firmware paths and hardware inputs before attempting a complete package build.

### Evidence

- `source`: [Format 2 board selection and package path/defconfig mapping.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/c472ccc1102a772f9e84261d8240be4eec6d7dca/board.toml)
- `source`: [Pinned MSM8956 shared SoC feed.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/c472ccc1102a772f9e84261d8240be4eec6d7dca/feeds.toml)
- `source`: [No Kenzo-compatible root was found among 86 extracted DTBs; only Qualcomm MSM8956 reference platform trees matched.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/c472ccc1102a772f9e84261d8240be4eec6d7dca/evidence/2026-11-12-dtb-inventory.md)
- `source`: [Local XNU patching needed a Sheng-only hunk workaround; builds on /mnt/c failed during atomic header replacement, and the ext4 retry was interrupted before completion.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/c472ccc1102a772f9e84261d8240be4eec6d7dca/evidence/2026-11-12-local-kernel-attempt.md)
- `source`: [Pre-build helper removes only the optional Sheng PMGR progress hunk and fails if its recognized layout changes.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/c472ccc1102a772f9e84261d8240be4eec6d7dca/scripts/prepare-kernel-patches.py)
- `source`: [Reusable macOS workflow provides a kernel-only build with redacted text logs and no image artifacts.](https://github.com/UniXNU/UniXNU/blob/c34f018aafd6befd5dc93c05a8dccd5bdce6724b/.github/workflows/macos.yml)
- `host`: [Passed on WSL/Linux against SoC pin 894aea231e7ac7133b2947777b2dbc89bdd4c6aa: wrote config for kenzo\_defconfig, extracted profile IPSW inputs, resolved 59 patches. UniXNU source revision 5a00e20157f3975d155f13ced7593347f9f5bf73.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/c472ccc1102a772f9e84261d8240be4eec6d7dca/evidence/2026-11-12-package-check.md)
  Command: <code>bash scripts/package.sh --check --os ipados-17.7.11-21H461</code>. Revision: `b9280aaa8c6f7fd2622bdc0b28aea8b9c35438a7`.
- `host`: [DTS compiled and generated a 12,888-byte ADT on WSL/Linux. The standalone generator completed; this does not verify UEFI or device boot. SoC revision 894aea231e7ac7133b2947777b2dbc89bdd4c6aa; UniXNU revision 5a00e20157f3975d155f13ced7593347f9f5bf73.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/c472ccc1102a772f9e84261d8240be4eec6d7dca/evidence/2026-11-12-adt-preflight.md)
  Command: <code>dtc -I dts -O dtb -i &lt;msm8956 DTSI&gt; -o /tmp/kenzo-hardware.dtb dts/kenzo.dts; python3 scripts/make-adt.py --dtb /tmp/kenzo-hardware.dtb --os-profile profiles/os/ipados-17.7.11-21H461/profile.toml --board ../UniXNU-kenzo/board.toml --output /tmp/kenzo.adt</code>. Revision: `b9280aaa8c6f7fd2622bdc0b28aea8b9c35438a7`.

## Firmware and boot {#firmware}

`planned`

### Hardware and dependencies

- Kenzo stock Android boot image and extracted device-tree data are present in the sibling kenzo-dump directory; no Kenzo Mu-Silicium/EDK2 checkout is present in this workspace.

### Configuration

- board.toml currently names a provisional Kenzo DSC/FD path; there is no firmware image pin, preflight script or confirmed firmware output.

### Procedure

- Follow the UniXNU UEFI integration guide, then build and inspect the device FD and boot image on a supported host.

### Development findings

- No UEFI build or physical boot evidence is recorded. The current firmware fields were adapted from a template and must be replaced with paths verified against a Kenzo firmware checkout.

### Completion criteria

- Firmware image builds, enters UniXNU, publishes the framebuffer and preserves the documented memory reservations.

### Current limits

- UEFI source, its revision, required Mu-Silicium modules, memory reservations, framebuffer handoff and firmware build output are unknown.

### Next action

- Identify a maintained MSM8956/Kenzo Mu-Silicium port, inspect its DSC/FDF and board configuration, then replace provisional firmware paths and record the firmware revision.

### Evidence

Collect evidence using the next action.

## CPU and interrupts {#cpu}

`implemented`

Components: `ArmCpu`.

### Hardware and dependencies

- The local cpuinfo reports six processors; the shared SoC definition declares four Cortex-A53 and two Cortex-A72 cores. Earlier hardware notes list GICv2 and a 19.2 MHz architectural timer.
- The local extracted DTB set contains MSM8956 MTP/CDP/QRD/simulator reference trees but no root compatible identifying Kenzo.

### Configuration

- The shared SoC DTSI sets /cpus/timebase-frequency to 19200000, CPU affinity values 0-3 and 0x100-0x101, PSCI method smc, GICv2 ranges 0x0b000000/0x1000 and 0x0b002000/0x1000, and exports the controller as intc.
- The board configuration selects ArmCpu; the SoC fragment enables the GIC and architectural timer.

### Procedure

- Compile dts/kenzo.dts with the pinned SoC include using dtc -I dts -O dtb.
- Generate the selected OS/device ADT with scripts/make-adt.py and inspect the output against required XNU nodes.
- Before claiming hardware bring-up, compare the MPIDRs, PSCI and interrupt resources with a Kenzo-specific DTB and capture per-core XNU logs.

### Development findings

- The MSM8956 SoC DTSI now supplies /cpus/timebase-frequency, routes interrupts to the GIC, and exports the GIC as ADT node intc. DTC and standalone ADT generation pass. CPU MPIDR values and GIC ranges are based on MSM8956 reference data, not a Kenzo-compatible DTB; no XNU secondary-core or IPI bring-up has been measured.

### Completion criteria

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU.

### Current limits

- Per-core MPIDR values, GIC interrupt specifiers, PSCI availability and IPI behavior have not been verified from the selected board DTB or on-device logs.

### Next action

- Obtain the matching Kenzo DTB from stock firmware, then verify CPU reg/MPIDRs, GIC distributor and CPU-interface ranges, timer and PSCI nodes; validate on hardware after a UEFI boot path exists.

### Evidence

- `source`: [SoC DTSI provides the timebase, interrupt-parent and exported GIC node required by the ADT generator.](https://github.com/CodeDevB7/UniXNU-msm8956-common/commit/894aea231e7ac7133b2947777b2dbc89bdd4c6aa)
- `source`: [The extracted MSM8956 trees identify only reference platforms; they are insufficient evidence for Kenzo-specific CPU/GIC values.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/c472ccc1102a772f9e84261d8240be4eec6d7dca/evidence/2026-11-12-dtb-inventory.md)
- `source`: [The board DTS compiled and standalone ADT generation completed on the host; physical CPU/GIC behavior is unverified.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/c472ccc1102a772f9e84261d8240be4eec6d7dca/evidence/2026-11-12-adt-preflight.md)

## Memory and DMA {#memory}

`planned`

### Hardware and dependencies

- The local dump reports MemTotal 1889528 kB and the current Kenzo DTS declares RAM at 0x80000000 with a 0x80000000 size.
- Extracted MSM8956 reference DTBs do not identify Kenzo and cannot establish this board's DRAM banks or reservations.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for memory and dma.

### Procedure

- Follow the memory and dma stage in the porting guide and record the actual commands.

### Development findings

- MemTotal supports the 2 GiB board variant, but does not establish the complete physical bank or reserved regions. The earlier DTS comment mentioned a 3 GB variant while its reg entry described only 2 GiB; it now identifies the captured unit's 2 GiB range without making a claim about other variants.

### Completion criteria

- All handoff regions are accounted for and each enabled DMA engine accesses its allocated range with the documented cache policy.

### Current limits

- Complete DRAM banks, firmware carveouts, DMA addressability, cache policy and SMMU ownership remain unverified.

### Next action

- Extract /memory and /reserved-memory from the matching Kenzo DTB, then reconcile with the UEFI handoff map before setting payload memory values.

### Evidence

- `source`: [The local extracted set has no Kenzo-compatible root, so its Qualcomm memory nodes cannot validate this board's map.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/c472ccc1102a772f9e84261d8240be4eec6d7dca/evidence/2026-11-12-dtb-inventory.md)

## Storage and root {#storage}

`planned`

### Hardware and dependencies

- Identify the storage and root hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for storage and root.

### Procedure

- Follow the storage and root stage in the porting guide and record the actual commands.

### Development findings

- Collect the first storage and root observation, its cause when established, and the resulting implementation decision.

### Completion criteria

- Host: register, clock, link and SMMU facts match the board inventory.
- Reads: SCSI capacity, GPT and known blocks are correct; OS/SystemOS windows stay within userdata.
- Root: the configured volume mounts and launchd starts. Persistence: writes survive reboot within the allocated Data region.

### Current limits

- Hardware inputs and implementation are pending for this example board.

### Next action

- Inventory the required storage and root inputs before implementation.

### Evidence

Collect evidence using the next action.

## Display {#display}

`planned`

### Hardware and dependencies

- Identify the display hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for display.

### Procedure

- Follow the display stage in the porting guide and record the actual commands.

### Development findings

- Collect the first display observation, its cause when established, and the resulting implementation decision.

### Completion criteria

- A known frame appears with correct geometry and colors, then userland presentation and backlight controls work.

### Current limits

- Hardware inputs and implementation are pending for this example board.

### Next action

- Inventory the required display inputs before implementation.

### Evidence

Collect evidence using the next action.

## Input {#input}

`planned`

### Hardware and dependencies

- Identify the input hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for input.

### Procedure

- Follow the input stage in the porting guide and record the actual commands.

### Development findings

- Collect the first input observation, its cause when established, and the resulting implementation decision.

### Completion criteria

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive, and buttons produce expected HID reports.

### Current limits

- Hardware inputs and implementation are pending for this example board.

### Next action

- Inventory the required input inputs before implementation.

### Evidence

Collect evidence using the next action.

## GPU {#gpu}

`planned`

### Hardware and dependencies

- Identify the gpu hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for gpu.

### Procedure

- Follow the gpu stage in the porting guide and record the actual commands.

### Development findings

- Collect the first gpu observation, its cause when established, and the resulting implementation decision.

### Completion criteria

- GPU submissions complete, mapping/fence handling is correct, a known image renders, and the selected Metal client presents it.

### Current limits

- Hardware inputs and implementation are pending for this example board.

### Next action

- Inventory the required gpu inputs before implementation.

### Evidence

Collect evidence using the next action.

## Network {#network}

`planned`

### Hardware and dependencies

- Identify the network hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for network.

### Procedure

- Follow the network stage in the porting guide and record the actual commands.

### Development findings

- Collect the first network observation, its cause when established, and the resulting implementation decision.

### Completion criteria

- Scanning, association, address configuration and sustained receive/transmit traffic pass with the selected firmware.

### Current limits

- Hardware inputs and implementation are pending for this example board.

### Next action

- Inventory the required network inputs before implementation.

### Evidence

Collect evidence using the next action.

## Audio {#audio}

`planned`

### Hardware and dependencies

- Identify the audio hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for audio.

### Procedure

- Follow the audio stage in the porting guide and record the actual commands.

### Development findings

- Collect the first audio observation, its cause when established, and the resulting implementation decision.

### Completion criteria

- Each declared route carries the selected audio format through playback or capture and handles start/stop correctly.

### Current limits

- Hardware inputs and implementation are pending for this example board.

### Next action

- Inventory the required audio inputs before implementation.

### Evidence

Collect evidence using the next action.

## Power {#power}

`planned`

### Hardware and dependencies

- Identify the power hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for power.

### Procedure

- Follow the power stage in the porting guide and record the actual commands.

### Development findings

- Collect the first power observation, its cause when established, and the resulting implementation decision.

### Completion criteria

- Declared power controls and battery readings match observations; each claimed sleep/resume transition restores its dependent peripherals.

### Current limits

- Hardware inputs and implementation are pending for this example board.

### Next action

- Inventory the required power inputs before implementation.

### Evidence

Collect evidence using the next action.

## Image assembly {#packaging}

`planned`

### Hardware and dependencies

- Identify the image assembly hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for image assembly.

### Procedure

- Follow the image assembly stage in the porting guide and record the actual commands.

### Development findings

- Collect the first image assembly observation, its cause when established, and the resulting implementation decision.

### Completion criteria

- Kernel and prelink succeed, payload contains all declared inputs, and the boot image matches the bootloader format and size limit.

### Current limits

- Hardware inputs and implementation are pending for this example board.

### Next action

- Inventory the required image assembly inputs before implementation.

### Evidence

Collect evidence using the next action.

## Diagnostics {#diagnostics}

`planned`

### Hardware and dependencies

- Identify the diagnostics hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for diagnostics.

### Procedure

- Follow the diagnostics stage in the porting guide and record the actual commands.

### Development findings

- Collect the first diagnostics observation, its cause when established, and the resulting implementation decision.

### Completion criteria

- Each claimed milestone has a reproducible command, a matching source/image revision and an accessible result.

### Current limits

- Hardware inputs and implementation are pending for this example board.

### Next action

- Inventory the required diagnostics inputs before implementation.

### Evidence

Collect evidence using the next action.

</div>
