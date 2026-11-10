# Xiaomi Redmi K70 Ultra \(rothko, MediaTek Dimensity 9300\)

[woaphone/UniXNU-rothko](https://github.com/woaphone/UniXNU-rothko)

<div v-pre>

Xiaomi Redmi K70 Ultra \(MT6989\) UniXNU port. Device testing reached the activation page with UFS HS-G5 root access, active CMD display presentation, Goodix/HID activity and eight-core SMP; touch interaction, key wake, Wi-Fi, Bluetooth, battery and stable post-activation behavior remain open.

Source record: [porting.toml](https://github.com/woaphone/UniXNU-rothko/blob/d5808a2aec900ff9b99c027e96f375a3bf120bf8/porting.toml), `d5808a2aec900ff9b99c027e96f375a3bf120bf8`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `implemented` |
| [Firmware and boot](#firmware) | `host-verified` |
| [CPU and interrupts](#cpu) | `device-verified` |
| [Memory and DMA](#memory) | `device-verified` |
| [Storage and root](#storage) | `device-verified` |
| [Display](#display) | `device-verified` |
| [Input](#input) | `implemented` |
| [GPU](#gpu) | `planned` |
| [Network](#network) | `planned` |
| [cellular](#cellular) | `planned` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `implemented` |
| [Image assembly](#packaging) | `host-verified` |
| [Diagnostics](#diagnostics) | `device-verified` |

## Configuration {#configuration}

`implemented`

Components: `ArmDTPlatform`, `ArmCpu`, `XnuPrelink`.

### Hardware and dependencies

- MT6989 / Dimensity 9300 board identity, eight CPUs, 13 MHz timer, GICv3 and the iPadOS 17.7.11 / 21H461 donor profile.
- Stock effective DT, board partition geometry and the reviewed component and patch inputs.

### Configuration

- board.toml selects the rothko board, published mt6989 common source, ipados-17.7.11-21H461 profile and device:dts/rothko.dts.
- rothko\_defconfig, soc:configs/mt6989.config and patches/xnu/series select the kernel configuration and ordered XNU changes.
- unixnu.lock pins woaphone/xnu-mtk branch rothko, immutable patch base 53bc420e5acda41c1689f6690a85841393a347cf and final fd4edc747395525a914987bb88f063b5e549ecc7.

### Procedure

- Run unixnu defconfig rothko\_defconfig -D ../UniXNU-rothko.
- Run unixnu fetch, unixnu status --json and unixnu tree, then run scripts/porting-record.py check.

### Development findings

- The device repository consumes published MT6989 CPU, PSCI, GICv3 and timer resources.
- The raw XNU feed names woaphone/xnu-mtk branch rothko at fd4edc7, but the OS profile currently overrides its effective revision with Apple d8b802.
- The selected arch/SoC/OS/device graph contains 77 patches; its full application and resulting kernel have not been qualified.
- The separate 18-patch replay from immutable 53bc420 reproduces exactly the source tree of fd4edc7.
- Board DTS is a hardware inventory/profile input; the minimal ADT generator does not parse it.

### Completion criteria

- Effective source revision, selected patch graph, archive recipes and generated ADT must reproduce the intended K70U inputs before build qualification.

### Current limits

- The full Format 2 release is not qualified: effective XNU pin, driver recipe registration and firmware build adapter remain open.
- The board DTS memory length currently differs from payload DRAM/owned-memory policy; a stock static memory node is not the live LK mblock map.
- The common layer currently covers CPU/PSCI/GIC/timer; clocks, power domains, SMMU/DMA and peripheral policy remain device-specific.

### Next action

- Move genuinely reusable MT6989 bus, clock or power resources into the common repository only after a second device or independent hardware trace confirms them.

### Evidence

- `source`: [Format 2 board identity and source contract are present.](https://github.com/woaphone/UniXNU-rothko/blob/d5808a2aec900ff9b99c027e96f375a3bf120bf8/board.toml)
- `host`: [Local profile/record inspection passed with cached common/XnuPrelink inputs; effective source revision and full build integration remain open.](https://github.com/woaphone/UniXNU-rothko/blob/d5808a2aec900ff9b99c027e96f375a3bf120bf8/docs/offline-audit-2026-11-07.md)
  Command: <code>unixnu status --json; release --no-deps --check; porting-record.py check</code>. Revision: `13e5973748a8447cbb90520c9a2dd5e65e272435`.

## Firmware and boot {#firmware}

`host-verified`

Components: `DarwinBoot`.

### Hardware and dependencies

- Separate ChallengeThePeak/Silicium-Rothko firmware repository, rothko DSC/FD paths, DarwinBoot handoff, GOP framebuffer and 56 MiB payload FAT volume.
- UEFI device reset, PHY, refclk and BlockIO state are treated as firmware-owned and audited separately from XNU.

### Configuration

- board.toml records the UEFI checkout, rothko.dsc, SILICIUM\_UEFI.fd path and firmware defines.
- The XNU payload uses firmware loader handoff, 8 GiB owned-memory intent and PSCI SMC.

### Procedure

- Build UEFI through the official DeviceBuild.py and stuart path in the UEFI checkout.
- Build the payload and boot image with the official UniXNU tools after the firmware FD is available.

### Development findings

- Official UEFI builds completed offline and the device reached the Darwin handoff; UFS link/DP success and later NOP/descriptor issues were observed in separate captures.
- An earlier firmware candidate ran with a mistaken UFS reference-clock setting and is recorded as unresolved; this repository does not claim that the boot LUN was written, and it does not claim that the current firmware is safe for another hardware run.
- The board now imports shared MT6989 CPU/GIC/timer resources from UniXNU-mt6989-common while keeping firmware paths and handoff policy board-specific.
- The complete arch/SoC/OS/device XNU patch sequence remains in the format 2 package graph.

### Completion criteria

- A reviewed firmware revision builds, enters DarwinBoot, publishes the documented framebuffer and preserves the handoff memory contract.

### Current limits

- The UEFI source and current unx18 safety candidate live in the separate ChallengeThePeak/Silicium-Rothko repository; current firmware runtime closure and the cause of the earlier reference-clock incident remain open.

### Next action

- Qualify the official DeviceBuild/stuart adapter and complete UFS command/state boundary before any future matched runtime claim.

### Evidence

- `source`: [Canonical ChallengeThePeak/Silicium-Rothko firmware repository, DSC, FD and package contract are recorded.](https://github.com/woaphone/UniXNU-rothko/blob/d5808a2aec900ff9b99c027e96f375a3bf120bf8/board.toml)
- `host`: [The imported unx18 source snapshot built the final PHY-skip FD SHA256 7fedccdf2097080689526b0fcea14caa22c70d9dcf14af035dd841128c921bf9; this does not validate later repository edits or the full release adapter.](https://github.com/woaphone/UniXNU-rothko/blob/d5808a2aec900ff9b99c027e96f375a3bf120bf8/docs/verification.md)
  Command: <code>DeviceBuild.py; stuart; official payload and boot_v4 packaging</code>. Revision: `7005848b8fad68ac2a74f18547a77d92ac3f11b8`.

## CPU and interrupts {#cpu}

`device-verified`

Components: `ArmCpu`, `MtkCpuFreq`.

### Hardware and dependencies

- Eight MT6989 CPUs, GICv3, 13 MHz timer, PSCI SMC, self-IPI and MMIO-IPI paths.
- The stock FDVFS interface and effective DT CPU vote table for the fixed boot-frequency request.

### Configuration

- payload kernel\_args enables cpus=8, sheng-smp, armcpu-self-ipi and armcpu-mmio-ipi.
- The board DTS records cpu-count=8 and timebase-frequency=13000000.

### Procedure

- Build ArmCpu and MtkCpuFreq archives, link the kernel and capture K1-K4, timer and IPI markers from pmsg.
- Compare the fixed FDVFS request path with the stock DT and firmware table.

### Development findings

- All eight CPU startup, timer and IPI activity were observed on the device.
- The CPU affinity, PSCI, GICv3 and 13 MHz timer description now comes from UniXNU-mt6989-common.
- MtkCpuFreq is a fixed boot request; it is not a dynamic governor and no XNU-side frequency measurement proves that it resolves the reported system slowness.

### Completion criteria

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works; any frequency claim must include a measured runtime frequency.

### Current limits

- Dynamic cpufreq/governor behavior and the cause of perceived system slowness remain unverified.

### Next action

- Capture a same-image runtime frequency/latency trace before changing CPU policy again.

### Evidence

- `source`: [ArmCpu startup and interrupt-controller implementation are present.](https://github.com/woaphone/UniXNU-rothko/blob/d5808a2aec900ff9b99c027e96f375a3bf120bf8/drivers/ArmCpu/ArmCpu.cpp)
- `device`: [unx8 captured eight-core startup, timer and IPI activity; fixed FDVFS performance was not validated by that run.](https://github.com/woaphone/UniXNU-rothko/blob/d5808a2aec900ff9b99c027e96f375a3bf120bf8/docs/verification.md)
  Command: <code>pull pmsg/pstore and inspect K1-K4, timer and IPI markers</code>. Revision: `142fc32699a9faeb9e81fb93705319ec76ae0aaf`.

## Memory and DMA {#memory}

`device-verified`

Components: `RamBlock`.

### Hardware and dependencies

- MT6989 DRAM map, 8 GiB owned-memory target, XNU 4 KiB page tables, DMA ranges and the packed seed ramdisk.
- The 4 GiB and 8 GiB bootstrap/page-table observations from the K70U bring-up captures.

### Configuration

- payload.adt.owned\_memory\_size is 0x200000000 and the board DTS records the DRAM range.
- NativeRamBlock supplies the packed Data seed without making the UEFI firmware a persistent disk writer.

### Procedure

- Generate the board ADT, link the kernel and replay/observe the native 4 KiB bootstrap table construction before payload handoff.
- Check the seed hash and logical Data size against the recorded source artifact.

### Development findings

- The 8 GiB bootstrap table pool was enlarged after a reproducible page-table boundary failure; the corrected path reached later XNU stages.
- The Data seed was imported in the root-matching captures; memory pressure and jetsam were still visible in earlier 2 GiB/4 GiB runs.
- CPU topology is inherited from the shared MT6989 DTSI; RAM ownership and reservations remain board-specific.

### Completion criteria

- The declared memory and DMA regions are represented in ADT, page tables are built for the selected memory size and the packed seed imports with its recorded identity.

### Current limits

- A complete long-duration memory-pressure comparison across 4 GiB and 8 GiB is not available; this area does not claim that RAM size alone fixes the UI stalls.

### Next action

- Repeat a same-image 8 GiB run with persistent pmsg and memory-pressure counters if the device is recovered.

### Evidence

- `source`: [The board memory range and CPU/DMA-facing hardware record are source-controlled.](https://github.com/woaphone/UniXNU-rothko/blob/d5808a2aec900ff9b99c027e96f375a3bf120bf8/dts/rothko.dts)
- `device`: [unx16 Build16 capture reached root and seed import; separate offline bootstrap replay proves the 8 GiB table correction, not complete long-duration memory qualification.](https://github.com/woaphone/UniXNU-rothko/blob/d5808a2aec900ff9b99c027e96f375a3bf120bf8/docs/verification.md)
  Command: <code>capture pmsg and inspect ADT/page-table and NativeRamBlock markers</code>. Revision: `fa4d518c74d62f0f603df1fde1a12bc91515ecce`.

## Storage and root {#storage}

`device-verified`

Components: `SoftwareAES`, `RamBlock`, `AppleKeyStoreState`, `VerifiedRoot`, `NativeMtkUfs`, `NativeAES`, `NativeRamBlock`.

### Hardware and dependencies

- MT6989 UFS host at 0x112b0000, UFS4 device, LU2 4096-byte user blocks, HS-G5 dual-lane XNU path, GPT unixnu window and root UUID.
- OS/SystemOS readonly windows, Data seed and the explicit distinction between XNU reads and UEFI BlockIO ownership.

### Configuration

- board.toml records the unixnu GPT LBA range, 4096-byte blocks, root-match UUID and readonly OS/SystemOS windows.
- NativeMtkUfs and NativeAES are included as separate XNU services; the UEFI repository is separately audited for refclk/reset/PHY writes.

### Procedure

- Build the UFS/AES/RamBlock archives, prelink the kernel and capture link, lane, capacity, GPT, root-match and read markers.
- Keep all persistence writes inside the declared unixnu Data/Log windows and review UEFI writes independently.

### Development findings

- Device evidence showed XNU UFS HS-G5 dual-lane reads, LU2 activity, root matching and sustained reads.
- An earlier firmware candidate that ran with a mistaken UFS reference-clock setting is not attributed to a proven boot-LUN write; the firmware-side refclk/reset/PHY audit remains separate from this XNU evidence.
- The board firmware contract now points to the published ChallengeThePeak/Silicium-Rothko unx18 read-only UFS baseline.
- UFS registers, driver selection, partitions and Data policy stay in the board repository after the common-resource split.
- The complete four-layer XNU patch sequence remains selected for the storage build graph.

### Completion criteria

- Host/link/read/root/persistence boundaries match the board inventory and no write path escapes the declared unixnu windows.

### Current limits

- Long-term UFS persistence and the earlier reference-clock incident remain unresolved; this record does not claim that the current firmware is safe to run on hardware again.

### Next action

- After device recovery, run a read-first UFS capture with the reviewed UEFI safety revision and record the exact firmware and image hashes.

### Evidence

- `source`: [MT6989 UFS host and readonly media implementation are present.](https://github.com/woaphone/UniXNU-rothko/blob/d5808a2aec900ff9b99c027e96f375a3bf120bf8/drivers/NativeMtkUfs/NativeMtkUfs.cpp)
- `device`: [unx16 Build16 follow-up confirms HS-G5 dual-lane reads and root matching; current UEFI command/state safety remains open.](https://github.com/woaphone/UniXNU-rothko/blob/d5808a2aec900ff9b99c027e96f375a3bf120bf8/docs/verification.md)
  Command: <code>pull pmsg and inspect UFS link, LU2 reads, GPT and root-match markers</code>. Revision: `fa4d518c74d62f0f603df1fde1a12bc91515ecce`.

## Display {#display}

`device-verified`

Components: `GopFramebuffer`, `NativeMobileDisplay`.

### Hardware and dependencies

- 1220x2712 panel geometry, 32 bpp GOP framebuffer, CMD-mode DSI and the firmware-to-XNU framebuffer handoff.
- The requirement to push each composed frame actively on the CMD panel.

### Configuration

- The board payload keeps the active CMD presentation flags and the DTS records 1220x2712x32 geometry.
- NativeMobileDisplay maps the framebuffer and performs the explicit post-composition push.

### Procedure

- Build the display archive, prelink and package the payload, then observe the first frame and activation UI on the physical device.
- Keep display and UFS logs in pmsg so a frozen screen can be separated from a reset.

### Development findings

- The device reached the activation page with the CMD active-push path.
- The board payload contract is paired with the published ChallengeThePeak/Silicium-Rothko firmware tree that provides the GOP handoff.
- The board DTS now imports the shared MT6989 CPU/GIC resources while retaining display geometry and panel policy locally.
- The complete arch/SoC/OS/device XNU patch sequence remains selected for the display build graph.
- Long-term presentation, unlock-to-desktop stability and the later black-screen behavior remain open; the evidence does not identify GPU as the cause.

### Completion criteria

- A known frame has correct geometry and colors, userland reaches the activation page and repeated frame pushes continue after handoff.

### Current limits

- Stable desktop presentation and wake-after-lock have not been demonstrated on the same final public repository revision.

### Next action

- Capture frame-push counters together with lock/unlock and wake-key events in one device run.

### Evidence

- `source`: [CMD presentation and framebuffer source are present.](https://github.com/woaphone/UniXNU-rothko/blob/d5808a2aec900ff9b99c027e96f375a3bf120bf8/drivers/NativeMobileDisplay/NativeMobileDisplay.cpp)
- `device`: [User observed the unx7 activation page; individual presentation counters were not captured for that observation.](https://github.com/woaphone/UniXNU-rothko/blob/d5808a2aec900ff9b99c027e96f375a3bf120bf8/docs/verification.md)
  Command: <code>boot the matched payload and observe the activation page</code>. Revision: `142fc32699a9faeb9e81fb93705319ec76ae0aaf`.

## Input {#input}

`implemented`

Components: `NativeHidInput`, `GoodixBerlin9916K`.

### Hardware and dependencies

- Goodix Berlin9916K on SPI6, reset GPIO3, IRQ GPIO4, 1220x2712 coordinate space and the corrected MT6363/GPIO key routes.
- Touch HID report format, contact IDs and the three physical key routes in the effective DT/DTBO.

### Configuration

- The board kit binds Goodix coordinates and firmware configuration; the kernel flags enable k70u-touch and HID input.
- The source records volume-up GPIO196 and MT6363 HOMEKEY/PWRKEY routes without treating the KPD fallback as the board's final mapping.

### Procedure

- Build NativeHidInput and the rothko kit, then capture sensor reports, HID queue movement, touch interactions and key wake.
- Compare reported coordinates and button events with the display geometry and effective DT resources.

### Development findings

- Goodix sensor reports and HID queue activity were observed on device.
- UI touch interaction and physical-key wake were not confirmed; the earlier three-second lock and black-screen report remains open.

### Completion criteria

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive and all three buttons produce the expected HID reports and wake behavior.

### Current limits

- Only the lower-level report/queue path is device-observed; successful UI interaction and wake-key behavior are pending.

### Next action

- Run a matched-image touch/volume-up/power/volume-down matrix and save the pmsg plus screen state for each event.

### Evidence

- `source`: [The board-specific Goodix and key input wiring is source-controlled.](https://github.com/woaphone/UniXNU-rothko/blob/d5808a2aec900ff9b99c027e96f375a3bf120bf8/kits/rothko/InputProbe.cpp)
- `device`: [unx8 sensor reports and HID activity were captured; UI touch and three-key wake remain unverified.](https://github.com/woaphone/UniXNU-rothko/blob/d5808a2aec900ff9b99c027e96f375a3bf120bf8/docs/verification.md)
  Command: <code>pull pmsg and inspect Goodix reports and HID queue head/tail</code>. Revision: `142fc32699a9faeb9e81fb93705319ec76ae0aaf`.

## GPU {#gpu}

`planned`

### Hardware and dependencies

- MT6989 GPU/firmware, SMMU, submission, fence and Metal client contract.

### Configuration

- The current display path uses GOP/CMD presentation and does not claim a native GPU implementation.

### Procedure

- Collect the board GPU firmware and SMMU ownership facts before selecting a driver; do not import Qualcomm GMU terminology as a MediaTek hardware fact.

### Development findings

- The observed UI and display path does not by itself prove a GPU implementation or a GPU root cause for the reported lag.
- The MT6989 common repository intentionally exports no GPU, SMMU, firmware or Metal policy.

### Completion criteria

- GPU submissions, mappings, fences and a selected Metal client render and present a known image.

### Current limits

- No native GPU driver, firmware contract or device rendering trace is recorded in this repository.

### Next action

- Inventory the stock GPU firmware, SMMU streams and Android reference implementation.

### Evidence

Collect evidence using the next action.

## Network {#network}

`planned`

### Hardware and dependencies

- MT6639 Wi-Fi over the board's ConnV3/PCIe/AXI/WFDMA path and its firmware/calibration inputs.

### Configuration

- No Wi-Fi component is selected in board.toml; proprietary firmware is not copied into this repository.

### Procedure

- Identify the bus, firmware, interrupts, DMA and OS interface, then implement scanning and packet transfer.

### Development findings

- MT6639 Wi-Fi and UART3 Bluetooth were documented during bring-up; neither has an implemented OS transport service.
- Wireless bus/power resources are recorded in the offline peripheral audit; the minimal board DTS does not yet describe the complete transport.

### Completion criteria

- Scanning, association, address configuration and sustained receive/transmit traffic pass with the selected firmware.

### Current limits

- The bus contract, firmware source and XNU network service are incomplete.

### Next action

- Collect the stock DT, firmware names and Android driver trace for MT6639.

### Evidence

Collect evidence using the next action.

## cellular {#cellular}

`planned`

### Hardware and dependencies

- Cellular/modem scope and firmware inventory for the Redmi K70 Ultra.

### Configuration

- No cellular component is selected and no modem firmware is copied into the device repository.

### Procedure

- Confirm whether this board's UniXNU scope includes modem support before selecting a protocol stack.

### Development findings

- No cellular implementation or device evidence was part of the current bring-up.
- The common MT6989 source contains no modem or cellular policy.

### Completion criteria

- If in scope, modem firmware, control/data protocol and network registration pass; otherwise document the board exclusion.

### Current limits

- The current port has no modem implementation or verified scope decision.

### Next action

- Record a not-applicable decision or inventory the modem interface before implementation.

### Evidence

Collect evidence using the next action.

## Audio {#audio}

`planned`

### Hardware and dependencies

- MT6989 audio DSP, codec, clocks, firmware services and playback/capture routes.

### Configuration

- No audio component is selected in the current board configuration.

### Procedure

- Inventory the audio DSP/codec and Android routes, then implement one playback and capture path.

### Development findings

- Audio was not part of the current device bring-up evidence.
- The common MT6989 source contains no DSP, codec or audio-route policy.

### Completion criteria

- Declared routes carry the selected audio format through playback and capture with correct start/stop behavior.

### Current limits

- No audio source, firmware or device result is recorded.

### Next action

- Collect stock audio DT, firmware and route information.

### Evidence

Collect evidence using the next action.

## Power {#power}

`implemented`

Components: `MtkCpuFreq`.

### Hardware and dependencies

- MT6989 FDVFS support table, per-core vote registers, firmware-owned voltage/PLL control and the active NFG1000A gauge address.

### Configuration

- MtkCpuFreq sends the fixed boot request supported by the board's FDVFS table; it is not a runtime governor.
- The active battery gauge is recorded as a separate pending backend and is not confused with the disabled MT6375 path.

### Procedure

- Build and link MtkCpuFreq, then compare request/readback logs with stock FDVFS metadata.
- Implement battery/IOP power source only after the I2C11/0x55 NFG1000A path is independently verified.

### Development findings

- The fixed CPU performance request is source- and host-verified; it does not establish the cause of the reported lag.
- Battery service is not connected to XNU and no sleep/resume transition is claimed.
- Clock, regulator, FDVFS and battery policy remain board-specific after the shared CPU-resource split.

### Completion criteria

- Declared power controls and battery readings match observations and each claimed sleep/resume transition restores dependent peripherals.

### Current limits

- Runtime governor, battery service and sleep/resume are incomplete; only the fixed CPU request is implemented.

### Next action

- Reuse the already tested NFG1000A read-only register backend, then implement I2C11 transport and IOPMPowerSource publication; retain runtime governor and sleep/resume as separate open items.

### Evidence

- `source`: [FDVFS request implementation and board-specific table are present.](https://github.com/woaphone/UniXNU-rothko/blob/d5808a2aec900ff9b99c027e96f375a3bf120bf8/drivers/MtkCpuFreq/MtkCpuFreq.cpp)
- `host`: [unx17 fixed FDVFS request compiled in the isolated board input archive; this does not qualify a standalone build-arm-driver.py recipe or measured frequency.](https://github.com/woaphone/UniXNU-rothko/blob/d5808a2aec900ff9b99c027e96f375a3bf120bf8/docs/verification.md)
  Command: <code>build the board input archive with MtkCpuFreq and link the kernel</code>. Revision: `fd4edc747395525a914987bb88f063b5e549ecc7`.

## Image assembly {#packaging}

`host-verified`

Components: `XnuPrelink`, `DarwinBoot`.

### Hardware and dependencies

- iPadOS 17.7.11 / 21H461 kernelcache, prelink ABI, payload FAT volume, UEFI FD and stock-compatible boot image envelope.

### Configuration

- board.toml records the kernelcache hash, prelink roots/slide, payload volume, memory size and root-match UUID.
- scripts/package.sh delegates to the official unixnu release path; package/unixnu.toml records the payload entry.

### Procedure

- Run the official kernel link, XnuPrelink, UEFI build, payload and boot\_v4 packer in order.
- Record every output hash and keep generated images outside the Git repository.

### Development findings

- The official offline build chain completed for the recorded unx15/unx16/unx17/unx18 candidates; the final public device repository intentionally contains no firmware or image binaries.
- The package contract consumes the published ChallengeThePeak/Silicium-Rothko firmware tree through the path configured in board.toml and CI.
- The package graph now resolves the MT6989 common commit recorded in unixnu.lock.
- The package graph preserves arch, SoC, OS and device patch-series arrays in their intended order.
- The packaging area owns .gitignore and the \*.toml.example templates so generated images, local build overrides and local module overrides stay out of Git; the CI changed-area check no longer sees an unowned path.

### Completion criteria

- Kernel and prelink succeed, payload contains declared inputs and boot images match the firmware's format and size constraints.

### Current limits

- The earlier isolated unx15-unx18 build results do not qualify the current Format 2 release graph.
- Current build-arm-driver.py rejects NativeMtkUfs and MtkCpuFreq; the main firmware adapter uses direct BaseTools/CLANGPDB rather than DeviceBuild/stuart.
- Source revision override, patch graph, board input archive integration and Linux toolchain inputs need qualification before full release.

### Next action

- Run scripts/package.sh --no-deps --check from a compatible main checkout for local plan inspection, then repair and qualify the source/recipe/firmware integration before claiming full release success.

### Evidence

- `source`: [The repository carries the official packaging wrapper.](https://github.com/woaphone/UniXNU-rothko/blob/d5808a2aec900ff9b99c027e96f375a3bf120bf8/scripts/package.sh)
- `host`: [Candidate-specific isolated build receipts for unx15 through unx18 are indexed in verification.md; the current Format 2 full release is not qualified.](https://github.com/woaphone/UniXNU-rothko/blob/d5808a2aec900ff9b99c027e96f375a3bf120bf8/docs/verification.md)
  Command: <code>kernel link; XnuPrelink; DeviceBuild/stuart; payload; boot_v4</code>. Revision: `fd4edc747395525a914987bb88f063b5e549ecc7`.

## Diagnostics {#diagnostics}

`device-verified`

### Hardware and dependencies

- pmsg/ramoops, UEFI console, dmesg, unixnu log ring, adb/fastboot capture and the persistent evidence reports.

### Configuration

- The payload enables serial/pmsg and the board keeps the logs needed to distinguish handoff, XNU, UFS, display and userland stages.

### Procedure

- Capture pstore/pmsg and firmware logs after each boot attempt; record image/source hashes and the last completed checkpoint.
- Run the official porting-record checker before publishing the device revision.

### Development findings

- The record distinguishes observed XNU entry, SMP, HID, UFS/root and activation-page milestones from unresolved UI wake, peripheral and firmware-state questions.
- The package workflow checks out the canonical UEFI repository ChallengeThePeak/Silicium-Rothko before the device release command.
- unixnu.lock records the same MT6989 common commit pinned by feeds.toml.

### Completion criteria

- Each claimed milestone has a reproducible command, matching source/image revision and an accessible result.

### Current limits

- The public repository does not contain the large proprietary logs or generated UEFI images; references point to the compact verification record and parent bring-up reports.

### Next action

- Publish a compact per-run evidence manifest alongside the next recovered-device test.

### Evidence

- `source`: [The compact verification record defines the evidence boundary.](https://github.com/woaphone/UniXNU-rothko/blob/d5808a2aec900ff9b99c027e96f375a3bf120bf8/docs/verification.md)
- `device`: [Earlier unx7/unx8/unx16 captures and user observations establish separate milestones; the earlier reference-clock report has no same-attempt command trace or boot-LUN readback.](https://github.com/woaphone/UniXNU-rothko/blob/d5808a2aec900ff9b99c027e96f375a3bf120bf8/docs/verification.md)
  Command: <code>inspect retained pstore/pmsg and candidate identities</code>. Revision: `fa4d518c74d62f0f603df1fde1a12bc91515ecce`.

</div>
