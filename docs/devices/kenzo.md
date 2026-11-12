# Xiaomi Redmi Note 3 \(Kenzo\) Snapdragon 650

[CodeDevB7/UniXNU-kenzo](https://github.com/CodeDevB7/UniXNU-kenzo)

<div v-pre>

Xiaomi Redmi Note 3 \(kenzo\) Snapdragon 650 porting record.

Source record: [porting.toml](https://github.com/CodeDevB7/UniXNU-kenzo/blob/3042b7540a21aa19a2e7ee4220fcf339efe8edaa/porting.toml), `3042b7540a21aa19a2e7ee4220fcf339efe8edaa`.

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
- Shared SoC feed points to CodeDevB7/UniXNU-msm8956-common at d6845aea8fc3e5c14993b269fcca92927e85fb45, corrected from the connected device's active FDT.

### Configuration

- board.toml selects ArmDTPlatform, ArmCpu, SoftwareAES, XnuPrelink and DarwinBoot; kenzo\_defconfig; SoC and OS config fragments; ordered arch, SoC, OS and device patch series.
- \[package\] unixnu is ../UniXNU and \[package.defconfig\] maps ipados-17.7.11-21H461 to kenzo\_defconfig.

### Procedure

- Resolve board configuration from the UniXNU checkout with unixnu status -D UniXNU-kenzo.
- Run scripts/package.sh --check --os ipados-17.7.11-21H461 from the device repository after required local sources are available.
- Use .github/workflows/dts-adt.yml to compile the board DTS and generate the ADT on a macOS runner; use kernel.yml for the kernel build.

### Development findings

- The current repository uses format 2 and the shared SoC feed; the older handoff's build workflow description predates the current package interface.
- The package script previously stopped immediately because \[package\].unixnu was absent; after recording the path and profile-to-defconfig mapping, host preflight resolved kenzo\_defconfig and all 59 patches.
- The extracted 86-DTB QCDT set contains reference roots only, but a live device-tree capture now identifies the bootloader-populated MSM8956 MTP tree and matching reference selector DTB 0.
- The kernel-only macOS workflow checks out UniXNU at c34f018aafd6befd5dc93c05a8dccd5bdce6724b and uploads the kernel binary and redacted text logs. Its pre-build helper removes only the optional Sheng PMGR probe hunk from the generic boot-progress patch; it fails closed if the upstream hunk layout changes.
- Run 43170315275 completed successfully on macOS. The final build and prelink produced kernel.macho with SHA-256 43bad77f58e9a3582f330ebb3c70ad4b48d0c350188d17c2bd38ed8454b7650f. The bootstrap pass first reported unresolved mockfs symbols before the configured archive build; the later main kernel link succeeded. The first successful run retained redacted logs but did not yet publish the kernel as an artifact.

### Completion criteria

- The pinned SoC source resolves; package preflight writes the selected configuration and patch resolution completes for the selected OS profile.

### Current limits

- Package preflight, patch resolution, standalone DTS-to-ADT generation and kernel compilation/prelink are host-verified. UEFI firmware, payload, image assembly and device boot are unverified. Firmware repository, image inputs and device seed are not configured.

### Next action

- Integrate and validate the live-FDT-grounded SoC map in the ADT, then identify a Kenzo UEFI source and verify board firmware paths before attempting a complete package build.

### Evidence

- `source`: [Format 2 board selection and package path/defconfig mapping.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/3042b7540a21aa19a2e7ee4220fcf339efe8edaa/board.toml)
- `source`: [Pinned MSM8956 shared SoC feed at d6845aea8fc3e5c14993b269fcca92927e85fb45.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/3042b7540a21aa19a2e7ee4220fcf339efe8edaa/feeds.toml)
- `source`: [Local extracted roots identify Qualcomm reference platforms only; the live device FDT selector matches extracted DTB 0.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/3042b7540a21aa19a2e7ee4220fcf339efe8edaa/evidence/2026-11-12-dtb-inventory.md)
- `source`: [Local XNU patching needed a Sheng-only hunk workaround; builds on /mnt/c failed during atomic header replacement, and the ext4 retry was interrupted before completion.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/3042b7540a21aa19a2e7ee4220fcf339efe8edaa/evidence/2026-11-12-local-kernel-attempt.md)
- `source`: [Pre-build helper removes only the optional Sheng PMGR progress hunk and fails if its recognized layout changes.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/3042b7540a21aa19a2e7ee4220fcf339efe8edaa/scripts/prepare-kernel-patches.py)
- `source`: [Compiles Kenzo DTS and generates the OS-specific ADT on macOS Actions using the pinned SoC feed.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/3042b7540a21aa19a2e7ee4220fcf339efe8edaa/.github/workflows/dts-adt.yml)
- `source`: [Reusable macOS workflow provides a kernel-only build with redacted text logs and no image artifacts.](https://github.com/UniXNU/UniXNU/blob/c34f018aafd6befd5dc93c05a8dccd5bdce6724b/.github/workflows/macos.yml)
- `host`: [Historical pass on WSL/Linux against SoC pin 894aea231e7ac7133b2947777b2dbc89bdd4c6aa \(not the corrected current pin\): wrote config for kenzo\_defconfig, extracted profile IPSW inputs, resolved 59 patches. UniXNU source revision 5a00e20157f3975d155f13ced7593347f9f5bf73.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/3042b7540a21aa19a2e7ee4220fcf339efe8edaa/evidence/2026-11-12-package-check.md)
  Command: <code>bash scripts/package.sh --check --os ipados-17.7.11-21H461</code>. Revision: `b9280aaa8c6f7fd2622bdc0b28aea8b9c35438a7`.
- `host`: [DTS compiled and generated a 12,888-byte ADT on WSL/Linux against the earlier SoC revision 894aea231e7ac7133b2947777b2dbc89bdd4c6aa; this does not validate the corrected current pin or verify UEFI/device boot. SoC revision 894aea231e7ac7133b2947777b2dbc89bdd4c6aa; UniXNU revision 5a00e20157f3975d155f13ced7593347f9f5bf73.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/3042b7540a21aa19a2e7ee4220fcf339efe8edaa/evidence/2026-11-12-adt-preflight.md)
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

- No UEFI build or physical boot evidence is recorded. Research found no public Kenzo/MSM8956 EDK2 or Mu-Silicium config; the closest Xiaomi \`jason\` and \`nitrogen\` configs in edk2-msm target SDM660, and their values are not transferable. \`board.toml\` firmware paths remain template placeholders.
- The live active FDT identifies the current MSM8956 MTP selector. Read-only partition inspection identifies SBL1 target strings for 8976A/MSM8952/MSM8956, TrustZone \`TZ.BF.3.0.3-00047\`, and a Kenzo/MSM8952 LK aboot whose strings include \`fastboot boot command is not available\`. The user reports repeatedly booting both \`boot.img\` and \`recovery.img\` successfully with \`fastboot boot\`, so the string does not establish that the path is unavailable. Exact SBL1, aboot and HYP release tags remain unknown. The user-reported boot was Android/recovery, not a UEFI payload test; no UEFI FD is present, and the Android FDT is not a UEFI handoff map. See the live tree, aboot and boot-chain evidence files.

### Completion criteria

- Firmware image builds, enters UniXNU, publishes the framebuffer and preserves the documented memory reservations.

### Current limits

- UEFI source, its revision, required Mu-Silicium modules, memory reservations, framebuffer handoff and firmware build output are unknown.

### Next action

- Record the exact images and output for the user's working temporary fastboot-boot path, determine the Android boot-image wrapper required for a UEFI payload, and match SBL1, aboot, HYP and TZ hashes to vendor releases; then implement and build a pinned Kenzo UEFI package without changing firmware paths until its memory handoff is verified.

### Evidence

- `source`: [No public Kenzo/MSM8956 EDK2/Mu-Silicium board config was found; near-match SDM660 configs and the lk2nd/MSM8956 references do not provide a verified UEFI path.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/3042b7540a21aa19a2e7ee4220fcf339efe8edaa/evidence/2026-11-12-uefi-research.md)
- `device`: [Read-only aboot hash recorded. Its binary has a fastboot-boot-unavailable string, but the user reports repeatedly booting boot.img and recovery.img successfully; no such command was run during this task.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/3042b7540a21aa19a2e7ee4220fcf339efe8edaa/evidence/2026-11-12-aboot-readonly.md)
  Command: <code>adb exec-out su -c 'dd if=/dev/block/mmcblk0p19 bs=1M status=none'</code>. Revision: `0ea480d8cd8f025754767d74cae3a83e84acf960`.
- `device`: [User confirms fastboot boot works for Android boot and recovery images on this device; this is not yet a UEFI payload test.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/3042b7540a21aa19a2e7ee4220fcf339efe8edaa/evidence/2026-11-12-aboot-readonly.md)
  Command: <code>User report: repeated successful fastboot boot boot.img and fastboot boot recovery.img; exact image hashes/output not captured</code>. Revision: `01be3c57b1e45149acf85aac68860f62dbf22af0`.
- `device`: [Recorded SBL1, TZ and HYP partition hashes; TZ exposes version TZ.BF.3.0.3-00047. No partition was written.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/3042b7540a21aa19a2e7ee4220fcf339efe8edaa/evidence/2026-11-12-boot-chain-readonly.md)
  Command: <code>adb exec-out su -c 'dd if=/dev/block/mmcblk0p4 bs=1M status=none'; adb exec-out su -c 'dd if=/dev/block/mmcblk0p8 bs=1M status=none'; adb exec-out su -c 'dd if=/dev/block/mmcblk0p10 bs=1M status=none'</code>. Revision: `0ea480d8cd8f025754767d74cae3a83e84acf960`.

## CPU and interrupts {#cpu}

`implemented`

Components: `ArmCpu`.

### Hardware and dependencies

- The connected Kenzo reports six online Linux CPUs and soc\_id 266 \(MSM8956\). Its active FDT identifies MSM8956 MTP, qcom,msm-id &lt;0x10a 0&gt;, qcom,board-id &lt;8 0&gt;; these selectors match extracted DTB 0. A draft postmarketOS Kenzo DTS requests revision 1.1 instead and does not match the live tree.
- The captured active FDT reports CPU MPIDRs 0-3, 0x100 and 0x103 as CPUs; 0x101 and 0x102 are NAK placeholders.

### Configuration

- The shared SoC DTSI sets /cpus/timebase-frequency to 19200000, observed CPU affinity values 0-3 and 0x100/0x103, PSCI method smc, GICv2 ranges 0x0b000000/0x1000 and 0x0b002000/0x1000, and exports the controller as intc. The debug UART uses captured range 0x078b0000/0x200 and interrupt &lt;0 0x6c 0&gt;.
- The board configuration selects ArmCpu; the SoC fragment enables the GIC and architectural timer.

### Procedure

- Compile dts/kenzo.dts with the pinned SoC include using dtc -I dts -O dtb.
- Generate the selected OS/device ADT with scripts/make-adt.py and inspect the output against required XNU nodes.
- After the UEFI path exists, boot XNU and capture per-core entry, timer and IPI logs against the captured Android FDT CPU/GIC data.

### Development findings

- The active device FDT confirms MSM8956 MTP selector cells, six CPU MPIDRs \(0-3, 0x100, 0x103\), PSCI SMC, the configured GIC ranges, timer tuples and debug UART range/interrupt. The shared SoC DTSI was corrected for MPIDR 0x103 and the UART resources. No XNU secondary-core or IPI bring-up has been measured.

### Completion criteria

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU.

### Current limits

- The capture is the running Android kernel FDT; CPU entry, XNU timer/IPI behavior, and whether a future UEFI payload receives the same nodes are unverified.

### Next action

- Build and inspect the ADT with the corrected pinned SoC tree, then validate XNU CPU entry, timer and IPI after a UEFI boot path exists.

### Evidence

- `source`: [SoC DTSI provides the timebase, interrupt-parent and exported GIC node required by the ADT generator.](https://github.com/CodeDevB7/UniXNU-msm8956-common/commit/d6845aea8fc3e5c14993b269fcca92927e85fb45)
- `source`: [The live device selector matches reference DTB 0; its source memory values are zeroed and bootloader-populated at runtime.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/3042b7540a21aa19a2e7ee4220fcf339efe8edaa/evidence/2026-11-12-dtb-inventory.md)
- `source`: [The draft Linux DTS requests MSM8956 v1.1, which differs from the live device tree revision.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/3042b7540a21aa19a2e7ee4220fcf339efe8edaa/evidence/2026-11-12-kenzo-mainline-dts.md)
- `source`: [The board DTS compiled and standalone ADT generation completed on the host; physical XNU CPU/GIC behavior remains unverified.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/3042b7540a21aa19a2e7ee4220fcf339efe8edaa/evidence/2026-11-12-adt-preflight.md)
- `device`: [Captured the running Kenzo Android FDT; root selectors match DTB 0, and CPU/GIC/PSCI/UART values ground the SoC DTS correction. This does not verify XNU boot.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/3042b7540a21aa19a2e7ee4220fcf339efe8edaa/evidence/2026-11-12-live-device-tree.md)
  Command: <code>adb exec-out su -c 'toybox tar -C /proc/device-tree -cf - .' (SELinux temporarily Permissive with user authorization, restored to Enforcing)</code>. Revision: `1ebf05c7198156efb47a25aa8b6879b9e338b374`.

## Memory and DMA {#memory}

`planned`

### Hardware and dependencies

- The live active FDT reports /memory/reg &lt;0 0x80000000 0 0x80000000&gt;, matching the current DTS 2 GiB window; Linux reports CPUs 0-5 online.
- The live tree exposes no /reserved-memory node; bootargs mention ramoops\_memreserve=4M. This Android FDT does not establish complete UEFI carveouts.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for memory and dma.

### Procedure

- Follow the memory and dma stage in the porting guide and record the actual commands.

### Development findings

- The active Android FDT confirms the 2 GiB DRAM range at 0x80000000. It has no reserved-memory node, and the ramoops\_memreserve=4M bootarg is not a complete UEFI memory map.

### Completion criteria

- All handoff regions are accounted for and each enabled DMA engine accesses its allocated range with the documented cache policy.

### Current limits

- Complete DRAM banks, firmware carveouts, DMA addressability, cache policy and SMMU ownership remain unverified.

### Next action

- Capture and reconcile the future UEFI memory map and firmware carveouts before setting payload memory values.

### Evidence

- `source`: [The live device selector matches generic DTB 0; the source memory reg is zeroed and bootloader-populated at runtime.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/3042b7540a21aa19a2e7ee4220fcf339efe8edaa/evidence/2026-11-12-dtb-inventory.md)
- `device`: [Live /memory confirms the 2 GiB physical window. No reserved-memory node is exposed; UEFI carveouts remain unknown.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/3042b7540a21aa19a2e7ee4220fcf339efe8edaa/evidence/2026-11-12-live-device-tree.md)
  Command: <code>adb exec-out su -c 'toybox tar -C /proc/device-tree -cf - .' (SELinux temporarily Permissive with user authorization, restored to Enforcing)</code>. Revision: `1ebf05c7198156efb47a25aa8b6879b9e338b374`.

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

- The MSM8956 feed lock now pins the live-FDT-grounded SoC correction d6845aea8fc3e5c14993b269fcca92927e85fb45; it corrects CPU MPIDR 0x103 and UART resources. This updates source resolution only and does not add an on-device XNU diagnostic probe.

### Completion criteria

- Each claimed milestone has a reproducible command, a matching source/image revision and an accessible result.

### Current limits

- Hardware inputs and implementation are pending for this example board.

### Next action

- Inventory the required diagnostics inputs before implementation.

### Evidence

- `source`: [MSM8956 feed is pinned to the corrected shared SoC revision.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/3042b7540a21aa19a2e7ee4220fcf339efe8edaa/feeds.toml)
- `source`: [Resolved MSM8956 lock matches feeds.toml at d6845aea8fc3e5c14993b269fcca92927e85fb45.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/3042b7540a21aa19a2e7ee4220fcf339efe8edaa/unixnu.lock)
- `device`: [Live FDT capture supplied the board evidence used for the SoC feed correction; XNU diagnostics remain unimplemented.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/3042b7540a21aa19a2e7ee4220fcf339efe8edaa/evidence/2026-11-12-live-device-tree.md)
  Command: <code>adb exec-out su -c 'toybox tar -C /proc/device-tree -cf - .' (SELinux temporarily Permissive with user authorization, restored to Enforcing)</code>. Revision: `1ebf05c7198156efb47a25aa8b6879b9e338b374`.

</div>
