# Xiaomi 17 \(pudding, qcom,canoe, SM8850\)

[daisukiKaffuChino/UniXNU-pudding](https://github.com/daisukiKaffuChino/UniXNU-pudding)

<div v-pre>

Xiaomi 17 \(p11u\). SoC values dual-verified \(pandora live + pudding vendor DTB\); board values from p11u-family dtbo. Pending: userdata GPT, RAM size, PON APID.

Source record: [porting.toml](https://github.com/daisukiKaffuChino/UniXNU-pudding/blob/1c357b4c91865c6d8fcfa7e01e0bdc03b81b5815/porting.toml), `1c357b4c91865c6d8fcfa7e01e0bdc03b81b5815`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `planned` |
| [Firmware and boot](#firmware) | `planned` |
| [CPU and interrupts](#cpu) | `planned` |
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

`planned`

Components: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`, `DarwinBoot`.

### Hardware and dependencies

- Identify the configuration hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for configuration.

### Procedure

- Follow the configuration stage in the porting guide and record the actual commands.

### Development findings

- 2026-10-26: SoC feed sm8850 drafted \(UniXNU-sm8850-common local\). Board config written from p11u dtbo + pandora cross-checks.
- bootimg header v4 confirmed \(TWRP BoardConfig BOARD\_BOOT\_HEADER\_VERSION=4, pagesize 4096, boot partition 0x6000000\).

### Completion criteria

- All source pins resolve; every selected component has a record; status shows the intended overrides and patch order.

### Current limits

- feeds.toml commit is REQUIRED\_SOC\_COMMIT until the sm8850 repo is published.
- userdata first/last\_lba are zeros pending live GPT export.

### Next action

- Publish UniXNU-sm8850-common and pin its commit; read-only GPT export from live device.

### Evidence

Collect evidence using the next action.

## Firmware and boot {#firmware}

`planned`

### Hardware and dependencies

- Identify the firmware and boot hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for firmware and boot.

### Procedure

- Follow the firmware and boot stage in the porting guide and record the actual commands.

### Development findings

- Collect the first firmware and boot observation, its cause when established, and the resulting implementation decision.

### Completion criteria

- Firmware image builds, enters UniXNU, publishes the framebuffer and preserves the documented memory reservations.

### Current limits

- Hardware inputs and implementation are pending for this example board.

### Next action

- Inventory the required firmware and boot inputs before implementation.

### Evidence

Collect evidence using the next action.

## CPU and interrupts {#cpu}

`planned`

### Hardware and dependencies

- Identify the cpu and interrupts hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for cpu and interrupts.

### Procedure

- Follow the cpu and interrupts stage in the porting guide and record the actual commands.

### Development findings

- Collect the first cpu and interrupts observation, its cause when established, and the resulting implementation decision.

### Completion criteria

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU.

### Current limits

- Hardware inputs and implementation are pending for this example board.

### Next action

- Inventory the required cpu and interrupts inputs before implementation.

### Evidence

Collect evidence using the next action.

## Memory and DMA {#memory}

`planned`

### Hardware and dependencies

- Identify the memory and dma hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for memory and dma.

### Procedure

- Follow the memory and dma stage in the porting guide and record the actual commands.

### Development findings

- Collect the first memory and dma observation, its cause when established, and the resulting implementation decision.

### Completion criteria

- All handoff regions are accounted for and each enabled DMA engine accesses its allocated range with the documented cache policy.

### Current limits

- Hardware inputs and implementation are pending for this example board.

### Next action

- Inventory the required memory and dma inputs before implementation.

### Evidence

Collect evidence using the next action.

## Storage and root {#storage}

`planned`

Components: `VerifiedRoot`.

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

Components: `GopFramebuffer`.

### Hardware and dependencies

- Identify the display hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for display.

### Procedure

- Follow the display stage in the porting guide and record the actual commands.

### Development findings

- 2026-10-26: p11u-family dtbo primary panel = 'xiaomi p11u 42 0d 0a cmd mode dsc dsi panel' \(NT37801 DDIC + CSOT AMOLED, LTPS\): active area 1200x2608 \(0x4b0 x 0xa30\), 4 DSI lanes, DSC v1.2 \(600x16 slices, 2/pkt, 8bpp\), 60/90/120Hz timings.
- Panel GPIOs: reset 98, ESD IRQ 97, nt336-ason08 212, ason18 214. Backlight: bl\_ctrl\_dcs, bl-inverted-dbv, min 5 / max 0x3fff.
- splash/cont\_splash\_region 0xfc800000/0x2b00000 - three-way agreement \(p11u dtbo fragment@179, pandora live, infiniti Display\_Reserved\).
- GOP handoff path chosen \(GopFramebuffer\); MDSS top-level registers must never be touched \(unclocked reads reset the chip\).

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

- 2026-10-26: vol+ = TLMM GPIO 101 \(pudding DTB pinctrl key-vol-up-default-state + p11u dtbo gpio\_keys vol\_up, dual-confirmed\). TLMM real base 0x0f100000 \(vendor DT 0x0f000000 is wrong; wrong read = bus hang + reset\).
- Touch primary \(p11u dtbo fragment@46\): FocalTech focaltech\_ts@0 on QUP4 SE0 SPI @0x1a80000, irq GPIO 158, reset GPIO 66, max 1200x2608, RX18xTX39, 15MHz SPI, trusted-touch vm\_mode.
- TWRP tree shows Synaptics S3910P + Novatek NT38773 alternates \(production multi-sourcing\). FocalTech first, Synaptics fallback.
- power/vol- on PMK8850 PON SPMI \(pandora APID 465 assumed; pudding APID not in available DTBO - live verify needed\).

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

- 2026-10-26: pudding DTB confirms Adreno840v2 \(gpu-model 'Adreno840v2', chipid 0x44050a01, qcom,ubwc-mode 6, compatible qcom,adreno-gpu-gen8-2-1\), reg set kgsl\_3d0 0x3d00000/0x40000 + rscc 0x3d50000 + cx\_dbgc 0x3d61000 + cx\_misc 0x3d9e000, IRQ SPI 300 + cx\_host SPI 80.
- GMU gen8 @0x3d37000/0x68000 + ao\_blk 0x3d40000, hfi SPI 304 / gmu SPI 305, hub OPP 150-400MHz; gpu\_microcode\(zap\) region 0x9959a000/0x2000.
- GPU SMMU 0x3da0000 \(qsmmu-v500/adreno-smmu, stream 5 for GMU\).

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

Components: `AppleKeyStoreState`.

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
