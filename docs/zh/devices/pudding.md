# Xiaomi 17 \(pudding, qcom,canoe, SM8850\)

[daisukiKaffuChino/UniXNU-pudding](https://github.com/daisukiKaffuChino/UniXNU-pudding)

<div v-pre>

Xiaomi 17 \(p11u\). SoC values dual-verified \(pandora live + pudding vendor DTB\); board values from p11u-family dtbo. Pending: userdata GPT, RAM size, PON APID.

源记录: [porting.toml](https://github.com/daisukiKaffuChino/UniXNU-pudding/blob/1c357b4c91865c6d8fcfa7e01e0bdc03b81b5815/porting.toml), `1c357b4c91865c6d8fcfa7e01e0bdc03b81b5815`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `planned` |
| [固件与启动](#firmware) | `planned` |
| [CPU 与中断](#cpu) | `planned` |
| [内存与 DMA](#memory) | `planned` |
| [存储与根卷](#storage) | `planned` |
| [显示](#display) | `planned` |
| [输入](#input) | `planned` |
| [GPU](#gpu) | `planned` |
| [网络](#network) | `planned` |
| [音频](#audio) | `planned` |
| [电源](#power) | `planned` |
| [镜像组装](#packaging) | `planned` |
| [诊断](#diagnostics) | `planned` |

## 配置 {#configuration}

`planned`

组件: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`, `DarwinBoot`.

### 硬件与依赖

- Identify the configuration hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for configuration.

### 操作步骤

- Follow the configuration stage in the porting guide and record the actual commands.

### 开发经验

- 2026-10-26: SoC feed sm8850 drafted \(UniXNU-sm8850-common local\). Board config written from p11u dtbo + pandora cross-checks.
- bootimg header v4 confirmed \(TWRP BoardConfig BOARD\_BOOT\_HEADER\_VERSION=4, pagesize 4096, boot partition 0x6000000\).

### 完成条件

- All source pins resolve; every selected component has a record; status shows the intended overrides and patch order.

### 当前范围

- feeds.toml commit is REQUIRED\_SOC\_COMMIT until the sm8850 repo is published.
- userdata first/last\_lba are zeros pending live GPT export.

### 下一步

- Publish UniXNU-sm8850-common and pin its commit; read-only GPT export from live device.

### 证据

按下一步操作收集证据。

## 固件与启动 {#firmware}

`planned`

### 硬件与依赖

- Identify the firmware and boot hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for firmware and boot.

### 操作步骤

- Follow the firmware and boot stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first firmware and boot observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Firmware image builds, enters UniXNU, publishes the framebuffer and preserves the documented memory reservations.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required firmware and boot inputs before implementation.

### 证据

按下一步操作收集证据。

## CPU 与中断 {#cpu}

`planned`

### 硬件与依赖

- Identify the cpu and interrupts hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for cpu and interrupts.

### 操作步骤

- Follow the cpu and interrupts stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first cpu and interrupts observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required cpu and interrupts inputs before implementation.

### 证据

按下一步操作收集证据。

## 内存与 DMA {#memory}

`planned`

### 硬件与依赖

- Identify the memory and dma hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for memory and dma.

### 操作步骤

- Follow the memory and dma stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first memory and dma observation, its cause when established, and the resulting implementation decision.

### 完成条件

- All handoff regions are accounted for and each enabled DMA engine accesses its allocated range with the documented cache policy.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required memory and dma inputs before implementation.

### 证据

按下一步操作收集证据。

## 存储与根卷 {#storage}

`planned`

组件: `VerifiedRoot`.

### 硬件与依赖

- Identify the storage and root hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for storage and root.

### 操作步骤

- Follow the storage and root stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first storage and root observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Host: register, clock, link and SMMU facts match the board inventory.
- Reads: SCSI capacity, GPT and known blocks are correct; OS/SystemOS windows stay within userdata.
- Root: the configured volume mounts and launchd starts. Persistence: writes survive reboot within the allocated Data region.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required storage and root inputs before implementation.

### 证据

按下一步操作收集证据。

## 显示 {#display}

`planned`

组件: `GopFramebuffer`.

### 硬件与依赖

- Identify the display hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for display.

### 操作步骤

- Follow the display stage in the porting guide and record the actual commands.

### 开发经验

- 2026-10-26: p11u-family dtbo primary panel = 'xiaomi p11u 42 0d 0a cmd mode dsc dsi panel' \(NT37801 DDIC + CSOT AMOLED, LTPS\): active area 1200x2608 \(0x4b0 x 0xa30\), 4 DSI lanes, DSC v1.2 \(600x16 slices, 2/pkt, 8bpp\), 60/90/120Hz timings.
- Panel GPIOs: reset 98, ESD IRQ 97, nt336-ason08 212, ason18 214. Backlight: bl\_ctrl\_dcs, bl-inverted-dbv, min 5 / max 0x3fff.
- splash/cont\_splash\_region 0xfc800000/0x2b00000 - three-way agreement \(p11u dtbo fragment@179, pandora live, infiniti Display\_Reserved\).
- GOP handoff path chosen \(GopFramebuffer\); MDSS top-level registers must never be touched \(unclocked reads reset the chip\).

### 完成条件

- A known frame appears with correct geometry and colors, then userland presentation and backlight controls work.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required display inputs before implementation.

### 证据

按下一步操作收集证据。

## 输入 {#input}

`planned`

### 硬件与依赖

- Identify the input hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for input.

### 操作步骤

- Follow the input stage in the porting guide and record the actual commands.

### 开发经验

- 2026-10-26: vol+ = TLMM GPIO 101 \(pudding DTB pinctrl key-vol-up-default-state + p11u dtbo gpio\_keys vol\_up, dual-confirmed\). TLMM real base 0x0f100000 \(vendor DT 0x0f000000 is wrong; wrong read = bus hang + reset\).
- Touch primary \(p11u dtbo fragment@46\): FocalTech focaltech\_ts@0 on QUP4 SE0 SPI @0x1a80000, irq GPIO 158, reset GPIO 66, max 1200x2608, RX18xTX39, 15MHz SPI, trusted-touch vm\_mode.
- TWRP tree shows Synaptics S3910P + Novatek NT38773 alternates \(production multi-sourcing\). FocalTech first, Synaptics fallback.
- power/vol- on PMK8850 PON SPMI \(pandora APID 465 assumed; pudding APID not in available DTBO - live verify needed\).

### 完成条件

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive, and buttons produce expected HID reports.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required input inputs before implementation.

### 证据

按下一步操作收集证据。

## GPU {#gpu}

`planned`

### 硬件与依赖

- Identify the gpu hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for gpu.

### 操作步骤

- Follow the gpu stage in the porting guide and record the actual commands.

### 开发经验

- 2026-10-26: pudding DTB confirms Adreno840v2 \(gpu-model 'Adreno840v2', chipid 0x44050a01, qcom,ubwc-mode 6, compatible qcom,adreno-gpu-gen8-2-1\), reg set kgsl\_3d0 0x3d00000/0x40000 + rscc 0x3d50000 + cx\_dbgc 0x3d61000 + cx\_misc 0x3d9e000, IRQ SPI 300 + cx\_host SPI 80.
- GMU gen8 @0x3d37000/0x68000 + ao\_blk 0x3d40000, hfi SPI 304 / gmu SPI 305, hub OPP 150-400MHz; gpu\_microcode\(zap\) region 0x9959a000/0x2000.
- GPU SMMU 0x3da0000 \(qsmmu-v500/adreno-smmu, stream 5 for GMU\).

### 完成条件

- GPU submissions complete, mapping/fence handling is correct, a known image renders, and the selected Metal client presents it.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required gpu inputs before implementation.

### 证据

按下一步操作收集证据。

## 网络 {#network}

`planned`

### 硬件与依赖

- Identify the network hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for network.

### 操作步骤

- Follow the network stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first network observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Scanning, association, address configuration and sustained receive/transmit traffic pass with the selected firmware.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required network inputs before implementation.

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`planned`

### 硬件与依赖

- Identify the audio hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for audio.

### 操作步骤

- Follow the audio stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first audio observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Each declared route carries the selected audio format through playback or capture and handles start/stop correctly.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required audio inputs before implementation.

### 证据

按下一步操作收集证据。

## 电源 {#power}

`planned`

组件: `AppleKeyStoreState`.

### 硬件与依赖

- Identify the power hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for power.

### 操作步骤

- Follow the power stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first power observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Declared power controls and battery readings match observations; each claimed sleep/resume transition restores its dependent peripherals.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required power inputs before implementation.

### 证据

按下一步操作收集证据。

## 镜像组装 {#packaging}

`planned`

### 硬件与依赖

- Identify the image assembly hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for image assembly.

### 操作步骤

- Follow the image assembly stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first image assembly observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Kernel and prelink succeed, payload contains all declared inputs, and the boot image matches the bootloader format and size limit.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required image assembly inputs before implementation.

### 证据

按下一步操作收集证据。

## 诊断 {#diagnostics}

`planned`

### 硬件与依赖

- Identify the diagnostics hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for diagnostics.

### 操作步骤

- Follow the diagnostics stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first diagnostics observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Each claimed milestone has a reproducible command, a matching source/image revision and an accessible result.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required diagnostics inputs before implementation.

### 证据

按下一步操作收集证据。

</div>
