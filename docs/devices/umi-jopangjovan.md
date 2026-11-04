# Xiaomi Mi 10 standalone UniXNU bring-up \(JopangJovan\)

[JopangJovan/UniXNU-umi](https://github.com/JopangJovan/UniXNU-umi)

<div v-pre>

Standalone UniXNU migration. Early source-built XNU checkpoints are observed on UMI; full kernel boot remains incomplete. HakiOS results are reference evidence only.

Source record: [porting.toml](https://github.com/JopangJovan/UniXNU-umi/blob/cc1cdff2ef87ff4d1c346f9f6eea2f4ef9b26442/porting.toml), `cc1cdff2ef87ff4d1c346f9f6eea2f4ef9b26442`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `implemented` |
| [Firmware and boot](#firmware) | `implemented` |
| [CPU and interrupts](#cpu) | `implemented` |
| [Memory and DMA](#memory) | `implemented` |
| [Storage and root](#storage) | `planned` |
| [Display](#display) | `planned` |
| [Input](#input) | `planned` |
| [GPU](#gpu) | `planned` |
| [Network](#network) | `planned` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `planned` |
| [Image assembly](#packaging) | `implemented` |
| [Diagnostics](#diagnostics) | `implemented` |

## Configuration {#configuration}

`implemented`

Components: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`, `DarwinBoot`.

### Hardware and dependencies

- UniXNU arm64 profile, stock UMI DTB and pinned SM8250 platform source.

### Configuration

- Format 2 board; iPadOS 17.7.11 / Darwin 23.6; umi\_defconfig; cpus=1.

### Procedure

- Run ./unixnu defconfig umi\_defconfig -D ../UniXNU-umi and ./unixnu status --json.

### Development findings

- The layered arch/SoC/OS/device configuration resolves successfully with a local development SoC override. Remote feed pins the published SoC commit.

### Completion criteria

- configuration is complete only after its hardware checkpoints are recorded with source/image identities.

### Current limits

- configuration: no standalone UniXNU hardware result yet.

### Next action

- Resolve the pinned feed without local overrides and build the kernel after toolchain installation.

### Evidence

- `source`: [Standalone board and firmware interfaces implemented; host checks documented separately.](https://github.com/JopangJovan/UniXNU-umi/blob/cc1cdff2ef87ff4d1c346f9f6eea2f4ef9b26442/BRINGUP.md)

## Firmware and boot {#firmware}

`implemented`

Components: `DarwinBoot`.

### Hardware and dependencies

- UMI firmware source 72279e8ff783bd108255097185415902d5c1f77e; 309 locally extracted UMI XBL files recorded by hash in the firmware repository.

### Configuration

- FD 0x9fc00000 + 0x300000; 1080x2340 GOP; board-local SEC entry-argument HOB; UniXNU/DarwinBoot/ramdisk/FAT modules.

### Procedure

- ./unixnu firmware; ./unixnu package; ./unixnu bootimg --ramdisk &lt;smoke FAT payload&gt;.

### Development findings

- DEBUG firmware builds. The reduced module set reaches the UniXNU menu and launches HelloPayload on UMI. RESULT PASS 0 passed 0 failed confirms basic EFI launch only.

### Completion criteria

- firmware is complete only after its hardware checkpoints are recorded with source/image identities.

### Current limits

- Local vendor files are not distributed. Device menu, FAT initrd discovery, basic EFI launch, XNU entry and several early initialization checkpoints are observed; full kernel boot remains unverified.

### Next action

- Temporarily boot the standalone XNU diagnostic image and capture its last progress stage.

### Evidence

- `source`: [Standalone board and firmware interfaces implemented; host checks documented separately.](https://github.com/JopangJovan/UniXNU-umi/blob/cc1cdff2ef87ff4d1c346f9f6eea2f4ef9b26442/BRINGUP.md)

## CPU and interrupts {#cpu}

`implemented`

Components: `ArmCpu`.

### Hardware and dependencies

- Stock affinities 0x000 through 0x700; GICD 0x17a00000; GICR 0x17a60000; stride 0x20000; 19.2 MHz timer; PSCI SMC.

### Configuration

- Enable only cpu0; retain disabled secondary topology and E/P tags for later qualification.

### Procedure

- scripts/check-hardware.py --stock-dtb /path/to/umi.dtb

### Development findings

- The host check confirms CPU affinities, GIC resources, timer rate and PSCI match stock; ADT conversion succeeds.

### Completion criteria

- cpu is complete only after its hardware checkpoints are recorded with source/image identities.

### Current limits

- Timer delivery, PSCI startup and IPIs have not been tested in UniXNU on this device.

### Next action

- Boot a source-built kernel and confirm timer ticks before enabling secondaries.

### Evidence

- `source`: [Standalone board and firmware interfaces implemented; host checks documented separately.](https://github.com/JopangJovan/UniXNU-umi/blob/cc1cdff2ef87ff4d1c346f9f6eea2f4ef9b26442/BRINGUP.md)

## Memory and DMA {#memory}

`implemented`

### Hardware and dependencies

- Stock bank 0xc0000000+0xc0000000 and UMI XBL low-memory reservations.

### Configuration

- Contiguous 3 GiB ADT handoff bank; DarwinBoot owned-memory request 512 MiB. Firmware reserves DDR hole and boot initrd/FDT arena.

### Procedure

- Compile hardware DTS; convert ADT; inspect firmware memory map before kernel handoff.

### Development findings

- The stock tree has discontiguous RAM and must not be passed wholesale to the common one-bank ADT generator.

### Completion criteria

- memory is complete only after its hardware checkpoints are recorded with source/image identities.

### Current limits

- Actual DarwinBoot window allocation and DMA mappings have not been observed on hardware.

### Next action

- Capture firmware memory map and DarwinBoot owned-window address.

### Evidence

- `source`: [Standalone board and firmware interfaces implemented; host checks documented separately.](https://github.com/JopangJovan/UniXNU-umi/blob/cc1cdff2ef87ff4d1c346f9f6eea2f4ef9b26442/BRINGUP.md)

## Storage and root {#storage}

`planned`

### Hardware and dependencies

- Stock UMI DTB and local Xiaomi SM8250 4.19 source at ../../workspace/xiaomi\_sm8250, revision 4ae1f1e4c89ce26c09846655da746e2e7cd38901; see reports/hardware-inputs.json.

### Configuration

- UFSHCI 0x1d84000/0x3000, ICE 0x1d90000/0x8000, QMP-v4 PHY 0x1d87000/0xe00, two lanes and 19.2 MHz reference clock. No XNU UFS driver is selected yet.

### Procedure

- Complete storage adaptation after CPU, timer and firmware handoff are device-qualified.

### Development findings

- The vendor 4.19 board source confirms the UMI Kona UFS register, clock, reset and rail wiring. Its UFS node does not declare SMMU stream IDs; qcom,disable-lpm is commented out. Do not reuse another board's stream IDs or SM8550 clock values.

### Completion criteria

- Host: register, clock, link and SMMU facts match the board inventory.
- Reads: SCSI capacity, GPT and known blocks are correct; OS/SystemOS windows stay within userdata.
- Root: the configured volume mounts and launchd starts. Persistence: writes survive reboot within the allocated Data region.

### Current limits

- No UMI runtime SMMU stream/context capture, native XNU UFS implementation, block read or root mount has been verified.

### Next action

- Continue XNU entry diagnosis; then implement UmiUfs in the device-owned source tree using the recorded 4.19 hardware facts.

### Evidence

Collect evidence using the next action.

## Display {#display}

`planned`

### Hardware and dependencies

- UMI display hardware information from the stock DTB and extracted firmware; UniXNU OS ABI adaptation remains required.

### Configuration

- display: no peripheral driver enabled in the initial single-core bring-up.

### Procedure

- Complete display adaptation after CPU, timer and firmware handoff are device-qualified.

### Development findings

- display: HakiOS hardware behavior is reference evidence only; no binary ABI compatibility assumed.

### Completion criteria

- A known frame appears with correct geometry and colors, then userland presentation and backlight controls work.

### Current limits

- display: no standalone UniXNU hardware result yet.

### Next action

- Inspect the UniXNU display interface and build a UMI-specific implementation without editing shared templates.

### Evidence

Collect evidence using the next action.

## Input {#input}

`planned`

### Hardware and dependencies

- UMI input hardware information from the stock DTB and extracted firmware; UniXNU OS ABI adaptation remains required.

### Configuration

- input: no peripheral driver enabled in the initial single-core bring-up.

### Procedure

- Complete input adaptation after CPU, timer and firmware handoff are device-qualified.

### Development findings

- input: HakiOS hardware behavior is reference evidence only; no binary ABI compatibility assumed.

### Completion criteria

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive, and buttons produce expected HID reports.

### Current limits

- input: no standalone UniXNU hardware result yet.

### Next action

- Inspect the UniXNU input interface and build a UMI-specific implementation without editing shared templates.

### Evidence

Collect evidence using the next action.

## GPU {#gpu}

`planned`

### Hardware and dependencies

- UMI gpu hardware information from the stock DTB and extracted firmware; UniXNU OS ABI adaptation remains required.

### Configuration

- gpu: no peripheral driver enabled in the initial single-core bring-up.

### Procedure

- Complete gpu adaptation after CPU, timer and firmware handoff are device-qualified.

### Development findings

- gpu: HakiOS hardware behavior is reference evidence only; no binary ABI compatibility assumed.

### Completion criteria

- GPU submissions complete, mapping/fence handling is correct, a known image renders, and the selected Metal client presents it.

### Current limits

- gpu: no standalone UniXNU hardware result yet.

### Next action

- Inspect the UniXNU gpu interface and build a UMI-specific implementation without editing shared templates.

### Evidence

Collect evidence using the next action.

## Network {#network}

`planned`

### Hardware and dependencies

- UMI network hardware information from the stock DTB and extracted firmware; UniXNU OS ABI adaptation remains required.

### Configuration

- network: no peripheral driver enabled in the initial single-core bring-up.

### Procedure

- Complete network adaptation after CPU, timer and firmware handoff are device-qualified.

### Development findings

- network: HakiOS hardware behavior is reference evidence only; no binary ABI compatibility assumed.

### Completion criteria

- Scanning, association, address configuration and sustained receive/transmit traffic pass with the selected firmware.

### Current limits

- network: no standalone UniXNU hardware result yet.

### Next action

- Inspect the UniXNU network interface and build a UMI-specific implementation without editing shared templates.

### Evidence

Collect evidence using the next action.

## Audio {#audio}

`planned`

### Hardware and dependencies

- UMI audio hardware information from the stock DTB and extracted firmware; UniXNU OS ABI adaptation remains required.

### Configuration

- audio: no peripheral driver enabled in the initial single-core bring-up.

### Procedure

- Complete audio adaptation after CPU, timer and firmware handoff are device-qualified.

### Development findings

- audio: HakiOS hardware behavior is reference evidence only; no binary ABI compatibility assumed.

### Completion criteria

- Each declared route carries the selected audio format through playback or capture and handles start/stop correctly.

### Current limits

- audio: no standalone UniXNU hardware result yet.

### Next action

- Inspect the UniXNU audio interface and build a UMI-specific implementation without editing shared templates.

### Evidence

Collect evidence using the next action.

## Power {#power}

`planned`

### Hardware and dependencies

- UMI power hardware information from the stock DTB and extracted firmware; UniXNU OS ABI adaptation remains required.

### Configuration

- power: no peripheral driver enabled in the initial single-core bring-up.

### Procedure

- Complete power adaptation after CPU, timer and firmware handoff are device-qualified.

### Development findings

- power: HakiOS hardware behavior is reference evidence only; no binary ABI compatibility assumed.

### Completion criteria

- Declared power controls and battery readings match observations; each claimed sleep/resume transition restores its dependent peripherals.

### Current limits

- power: no standalone UniXNU hardware result yet.

### Next action

- Inspect the UniXNU power interface and build a UMI-specific implementation without editing shared templates.

### Evidence

Collect evidence using the next action.

## Image assembly {#packaging}

`implemented`

### Hardware and dependencies

- UniXNU package, UMI FD, stock DTB and a 32 MiB FAT smoke payload.

### Configuration

- Android boot header v1; gzip firmware with appended UMI DTB; no HakiOS XNUP payload.

### Procedure

- ./unixnu package; ./unixnu bootimg --ramdisk &lt;smoke FAT payload&gt;.

### Development findings

- The package and Android boot image build; the boot packer checks firmware, shim, DTB and ramdisk bytes.

### Completion criteria

- packaging is complete only after its hardware checkpoints are recorded with source/image identities.

### Current limits

- Smoke payload tests EFI execution only; OS root and persistent Data are not implemented.

### Next action

- Test the smoke image, then package a source-built XNU when its ABI inputs are available.

### Evidence

- `source`: [Standalone board and firmware interfaces implemented; host checks documented separately.](https://github.com/JopangJovan/UniXNU-umi/blob/cc1cdff2ef87ff4d1c346f9f6eea2f4ef9b26442/BRINGUP.md)

## Diagnostics {#diagnostics}

`implemented`

### Hardware and dependencies

- Stock fastboot and user-observed UEFI screen output.

### Configuration

- -v serial=3 debug=0x14e cpus=1 for initial XNU test.

### Procedure

- Use adb reboot bootloader; use fastboot boot for temporary images.

### Development findings

- Firmware menu and basic EFI payload launch were observed on UMI. Timed source-built XNU probes reached MMU enable, initial platform setup, kernel startup, VM setup, serial initialization and KPRINTF startup. No device partitions were flashed.

### Completion criteria

- diagnostics is complete only after its hardware checkpoints are recorded with source/image identities.

### Current limits

- A later early-platform checkpoint did not return; the full kernel and userspace remain unverified. See reports/kernel-bringup.json.

### Next action

- Verify the physical GOP framebuffer handoff and continue early XNU startup.

### Evidence

- `source`: [Standalone board and firmware interfaces implemented; host checks documented separately.](https://github.com/JopangJovan/UniXNU-umi/blob/cc1cdff2ef87ff4d1c346f9f6eea2f4ef9b26442/BRINGUP.md)

</div>
