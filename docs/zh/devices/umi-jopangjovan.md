# Xiaomi Mi 10 standalone UniXNU bring-up \(JopangJovan\)

[JopangJovan/UniXNU-umi](https://github.com/JopangJovan/UniXNU-umi)

<div v-pre>

Standalone UniXNU migration. Early source-built XNU checkpoints are observed on UMI; full kernel boot remains incomplete. HakiOS results are reference evidence only.

源记录: [porting.toml](https://github.com/JopangJovan/UniXNU-umi/blob/cc1cdff2ef87ff4d1c346f9f6eea2f4ef9b26442/porting.toml), `cc1cdff2ef87ff4d1c346f9f6eea2f4ef9b26442`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `implemented` |
| [固件与启动](#firmware) | `implemented` |
| [CPU 与中断](#cpu) | `implemented` |
| [内存与 DMA](#memory) | `implemented` |
| [存储与根卷](#storage) | `planned` |
| [显示](#display) | `planned` |
| [输入](#input) | `planned` |
| [GPU](#gpu) | `planned` |
| [网络](#network) | `planned` |
| [音频](#audio) | `planned` |
| [电源](#power) | `planned` |
| [镜像组装](#packaging) | `implemented` |
| [诊断](#diagnostics) | `implemented` |

## 配置 {#configuration}

`implemented`

组件: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`, `DarwinBoot`.

### 硬件与依赖

- UniXNU arm64 profile, stock UMI DTB and pinned SM8250 platform source.

### 配置

- Format 2 board; iPadOS 17.7.11 / Darwin 23.6; umi\_defconfig; cpus=1.

### 操作步骤

- Run ./unixnu defconfig umi\_defconfig -D ../UniXNU-umi and ./unixnu status --json.

### 开发经验

- The layered arch/SoC/OS/device configuration resolves successfully with a local development SoC override. Remote feed pins the published SoC commit.

### 完成条件

- configuration is complete only after its hardware checkpoints are recorded with source/image identities.

### 当前范围

- configuration: no standalone UniXNU hardware result yet.

### 下一步

- Resolve the pinned feed without local overrides and build the kernel after toolchain installation.

### 证据

- `source`: [Standalone board and firmware interfaces implemented; host checks documented separately.](https://github.com/JopangJovan/UniXNU-umi/blob/cc1cdff2ef87ff4d1c346f9f6eea2f4ef9b26442/BRINGUP.md)

## 固件与启动 {#firmware}

`implemented`

组件: `DarwinBoot`.

### 硬件与依赖

- UMI firmware source 72279e8ff783bd108255097185415902d5c1f77e; 309 locally extracted UMI XBL files recorded by hash in the firmware repository.

### 配置

- FD 0x9fc00000 + 0x300000; 1080x2340 GOP; board-local SEC entry-argument HOB; UniXNU/DarwinBoot/ramdisk/FAT modules.

### 操作步骤

- ./unixnu firmware; ./unixnu package; ./unixnu bootimg --ramdisk &lt;smoke FAT payload&gt;.

### 开发经验

- DEBUG firmware builds. The reduced module set reaches the UniXNU menu and launches HelloPayload on UMI. RESULT PASS 0 passed 0 failed confirms basic EFI launch only.

### 完成条件

- firmware is complete only after its hardware checkpoints are recorded with source/image identities.

### 当前范围

- Local vendor files are not distributed. Device menu, FAT initrd discovery, basic EFI launch, XNU entry and several early initialization checkpoints are observed; full kernel boot remains unverified.

### 下一步

- Temporarily boot the standalone XNU diagnostic image and capture its last progress stage.

### 证据

- `source`: [Standalone board and firmware interfaces implemented; host checks documented separately.](https://github.com/JopangJovan/UniXNU-umi/blob/cc1cdff2ef87ff4d1c346f9f6eea2f4ef9b26442/BRINGUP.md)

## CPU 与中断 {#cpu}

`implemented`

组件: `ArmCpu`.

### 硬件与依赖

- Stock affinities 0x000 through 0x700; GICD 0x17a00000; GICR 0x17a60000; stride 0x20000; 19.2 MHz timer; PSCI SMC.

### 配置

- Enable only cpu0; retain disabled secondary topology and E/P tags for later qualification.

### 操作步骤

- scripts/check-hardware.py --stock-dtb /path/to/umi.dtb

### 开发经验

- The host check confirms CPU affinities, GIC resources, timer rate and PSCI match stock; ADT conversion succeeds.

### 完成条件

- cpu is complete only after its hardware checkpoints are recorded with source/image identities.

### 当前范围

- Timer delivery, PSCI startup and IPIs have not been tested in UniXNU on this device.

### 下一步

- Boot a source-built kernel and confirm timer ticks before enabling secondaries.

### 证据

- `source`: [Standalone board and firmware interfaces implemented; host checks documented separately.](https://github.com/JopangJovan/UniXNU-umi/blob/cc1cdff2ef87ff4d1c346f9f6eea2f4ef9b26442/BRINGUP.md)

## 内存与 DMA {#memory}

`implemented`

### 硬件与依赖

- Stock bank 0xc0000000+0xc0000000 and UMI XBL low-memory reservations.

### 配置

- Contiguous 3 GiB ADT handoff bank; DarwinBoot owned-memory request 512 MiB. Firmware reserves DDR hole and boot initrd/FDT arena.

### 操作步骤

- Compile hardware DTS; convert ADT; inspect firmware memory map before kernel handoff.

### 开发经验

- The stock tree has discontiguous RAM and must not be passed wholesale to the common one-bank ADT generator.

### 完成条件

- memory is complete only after its hardware checkpoints are recorded with source/image identities.

### 当前范围

- Actual DarwinBoot window allocation and DMA mappings have not been observed on hardware.

### 下一步

- Capture firmware memory map and DarwinBoot owned-window address.

### 证据

- `source`: [Standalone board and firmware interfaces implemented; host checks documented separately.](https://github.com/JopangJovan/UniXNU-umi/blob/cc1cdff2ef87ff4d1c346f9f6eea2f4ef9b26442/BRINGUP.md)

## 存储与根卷 {#storage}

`planned`

### 硬件与依赖

- Stock UMI DTB and local Xiaomi SM8250 4.19 source at ../../workspace/xiaomi\_sm8250, revision 4ae1f1e4c89ce26c09846655da746e2e7cd38901; see reports/hardware-inputs.json.

### 配置

- UFSHCI 0x1d84000/0x3000, ICE 0x1d90000/0x8000, QMP-v4 PHY 0x1d87000/0xe00, two lanes and 19.2 MHz reference clock. No XNU UFS driver is selected yet.

### 操作步骤

- Complete storage adaptation after CPU, timer and firmware handoff are device-qualified.

### 开发经验

- The vendor 4.19 board source confirms the UMI Kona UFS register, clock, reset and rail wiring. Its UFS node does not declare SMMU stream IDs; qcom,disable-lpm is commented out. Do not reuse another board's stream IDs or SM8550 clock values.

### 完成条件

- Host: register, clock, link and SMMU facts match the board inventory.
- Reads: SCSI capacity, GPT and known blocks are correct; OS/SystemOS windows stay within userdata.
- Root: the configured volume mounts and launchd starts. Persistence: writes survive reboot within the allocated Data region.

### 当前范围

- No UMI runtime SMMU stream/context capture, native XNU UFS implementation, block read or root mount has been verified.

### 下一步

- Continue XNU entry diagnosis; then implement UmiUfs in the device-owned source tree using the recorded 4.19 hardware facts.

### 证据

按下一步操作收集证据。

## 显示 {#display}

`planned`

### 硬件与依赖

- UMI display hardware information from the stock DTB and extracted firmware; UniXNU OS ABI adaptation remains required.

### 配置

- display: no peripheral driver enabled in the initial single-core bring-up.

### 操作步骤

- Complete display adaptation after CPU, timer and firmware handoff are device-qualified.

### 开发经验

- display: HakiOS hardware behavior is reference evidence only; no binary ABI compatibility assumed.

### 完成条件

- A known frame appears with correct geometry and colors, then userland presentation and backlight controls work.

### 当前范围

- display: no standalone UniXNU hardware result yet.

### 下一步

- Inspect the UniXNU display interface and build a UMI-specific implementation without editing shared templates.

### 证据

按下一步操作收集证据。

## 输入 {#input}

`planned`

### 硬件与依赖

- UMI input hardware information from the stock DTB and extracted firmware; UniXNU OS ABI adaptation remains required.

### 配置

- input: no peripheral driver enabled in the initial single-core bring-up.

### 操作步骤

- Complete input adaptation after CPU, timer and firmware handoff are device-qualified.

### 开发经验

- input: HakiOS hardware behavior is reference evidence only; no binary ABI compatibility assumed.

### 完成条件

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive, and buttons produce expected HID reports.

### 当前范围

- input: no standalone UniXNU hardware result yet.

### 下一步

- Inspect the UniXNU input interface and build a UMI-specific implementation without editing shared templates.

### 证据

按下一步操作收集证据。

## GPU {#gpu}

`planned`

### 硬件与依赖

- UMI gpu hardware information from the stock DTB and extracted firmware; UniXNU OS ABI adaptation remains required.

### 配置

- gpu: no peripheral driver enabled in the initial single-core bring-up.

### 操作步骤

- Complete gpu adaptation after CPU, timer and firmware handoff are device-qualified.

### 开发经验

- gpu: HakiOS hardware behavior is reference evidence only; no binary ABI compatibility assumed.

### 完成条件

- GPU submissions complete, mapping/fence handling is correct, a known image renders, and the selected Metal client presents it.

### 当前范围

- gpu: no standalone UniXNU hardware result yet.

### 下一步

- Inspect the UniXNU gpu interface and build a UMI-specific implementation without editing shared templates.

### 证据

按下一步操作收集证据。

## 网络 {#network}

`planned`

### 硬件与依赖

- UMI network hardware information from the stock DTB and extracted firmware; UniXNU OS ABI adaptation remains required.

### 配置

- network: no peripheral driver enabled in the initial single-core bring-up.

### 操作步骤

- Complete network adaptation after CPU, timer and firmware handoff are device-qualified.

### 开发经验

- network: HakiOS hardware behavior is reference evidence only; no binary ABI compatibility assumed.

### 完成条件

- Scanning, association, address configuration and sustained receive/transmit traffic pass with the selected firmware.

### 当前范围

- network: no standalone UniXNU hardware result yet.

### 下一步

- Inspect the UniXNU network interface and build a UMI-specific implementation without editing shared templates.

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`planned`

### 硬件与依赖

- UMI audio hardware information from the stock DTB and extracted firmware; UniXNU OS ABI adaptation remains required.

### 配置

- audio: no peripheral driver enabled in the initial single-core bring-up.

### 操作步骤

- Complete audio adaptation after CPU, timer and firmware handoff are device-qualified.

### 开发经验

- audio: HakiOS hardware behavior is reference evidence only; no binary ABI compatibility assumed.

### 完成条件

- Each declared route carries the selected audio format through playback or capture and handles start/stop correctly.

### 当前范围

- audio: no standalone UniXNU hardware result yet.

### 下一步

- Inspect the UniXNU audio interface and build a UMI-specific implementation without editing shared templates.

### 证据

按下一步操作收集证据。

## 电源 {#power}

`planned`

### 硬件与依赖

- UMI power hardware information from the stock DTB and extracted firmware; UniXNU OS ABI adaptation remains required.

### 配置

- power: no peripheral driver enabled in the initial single-core bring-up.

### 操作步骤

- Complete power adaptation after CPU, timer and firmware handoff are device-qualified.

### 开发经验

- power: HakiOS hardware behavior is reference evidence only; no binary ABI compatibility assumed.

### 完成条件

- Declared power controls and battery readings match observations; each claimed sleep/resume transition restores its dependent peripherals.

### 当前范围

- power: no standalone UniXNU hardware result yet.

### 下一步

- Inspect the UniXNU power interface and build a UMI-specific implementation without editing shared templates.

### 证据

按下一步操作收集证据。

## 镜像组装 {#packaging}

`implemented`

### 硬件与依赖

- UniXNU package, UMI FD, stock DTB and a 32 MiB FAT smoke payload.

### 配置

- Android boot header v1; gzip firmware with appended UMI DTB; no HakiOS XNUP payload.

### 操作步骤

- ./unixnu package; ./unixnu bootimg --ramdisk &lt;smoke FAT payload&gt;.

### 开发经验

- The package and Android boot image build; the boot packer checks firmware, shim, DTB and ramdisk bytes.

### 完成条件

- packaging is complete only after its hardware checkpoints are recorded with source/image identities.

### 当前范围

- Smoke payload tests EFI execution only; OS root and persistent Data are not implemented.

### 下一步

- Test the smoke image, then package a source-built XNU when its ABI inputs are available.

### 证据

- `source`: [Standalone board and firmware interfaces implemented; host checks documented separately.](https://github.com/JopangJovan/UniXNU-umi/blob/cc1cdff2ef87ff4d1c346f9f6eea2f4ef9b26442/BRINGUP.md)

## 诊断 {#diagnostics}

`implemented`

### 硬件与依赖

- Stock fastboot and user-observed UEFI screen output.

### 配置

- -v serial=3 debug=0x14e cpus=1 for initial XNU test.

### 操作步骤

- Use adb reboot bootloader; use fastboot boot for temporary images.

### 开发经验

- Firmware menu and basic EFI payload launch were observed on UMI. Timed source-built XNU probes reached MMU enable, initial platform setup, kernel startup, VM setup, serial initialization and KPRINTF startup. No device partitions were flashed.

### 完成条件

- diagnostics is complete only after its hardware checkpoints are recorded with source/image identities.

### 当前范围

- A later early-platform checkpoint did not return; the full kernel and userspace remain unverified. See reports/kernel-bringup.json.

### 下一步

- Verify the physical GOP framebuffer handoff and continue early XNU startup.

### 证据

- `source`: [Standalone board and firmware interfaces implemented; host checks documented separately.](https://github.com/JopangJovan/UniXNU-umi/blob/cc1cdff2ef87ff4d1c346f9f6eea2f4ef9b26442/BRINGUP.md)

</div>
