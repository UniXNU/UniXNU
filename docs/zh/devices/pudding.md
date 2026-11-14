# Xiaomi 17 \(pudding, qcom,canoe, SM8850\)

[daisukiKaffuChino/UniXNU-pudding](https://github.com/daisukiKaffuChino/UniXNU-pudding)

<div v-pre>

Xiaomi 17 \(p11u\). SoC values dual-verified \(pandora live + pudding vendor DTB\); board values from p11u-family dtbo. Pending: userdata GPT, RAM size, PON APID.

源记录: [porting.toml](https://github.com/daisukiKaffuChino/UniXNU-pudding/blob/1028ed6b6c1984d7897933333e84a1a09942b80f/porting.toml), `1028ed6b6c1984d7897933333e84a1a09942b80f`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `planned` |
| [固件与启动](#firmware) | `planned` |
| [CPU 与中断](#cpu) | `planned` |
| [内存与 DMA](#memory) | `planned` |
| [存储与根卷](#storage) | `implemented` |
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

组件: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`, `DarwinBoot`, `AppleKeyStoreState`.

### 硬件与依赖

- Identify the configuration hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for configuration.

### 操作步骤

- Follow the configuration stage in the porting guide and record the actual commands.

### 开发经验

- 2026-10-26: SoC feed sm8850 drafted \(UniXNU-sm8850-common local\). Board config written from p11u dtbo + pandora cross-checks.
- bootimg header v4 confirmed \(TWRP BoardConfig BOARD\_BOOT\_HEADER\_VERSION=4, pagesize 4096, boot partition 0x6000000\).
- 2026-11-11: board.toml pins the iPadOS 17.7.11 OS volume UUID and adds rd=puddingufs0 plus logger kernel arguments; the defconfig documents why the pinned-file root device is a BSD driver.

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

组件: `GopFramebuffer`.

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

`implemented`

组件: `VerifiedRoot`.

### 硬件与依赖

- SM8850 UFS host reuses bootloader-initialized UTRL; UFS LUN 0xD0; SMMU SID 0x60 remains bootloader passthrough; 4 KiB native blocks; userdata GPT range 3535360..128627706.
- Persistent diagnostics are limited to the pinned iosroot file's unused tail, after the 2,290,688-block image boundary; no Android partition or slot writes.

### 配置

- BSD bdevsw root reader is selected; ShengUfs/IOStorageFamily static linkage is disabled because required private symbols are not exported.
- READ CAPACITY\(10\) requires 4096-byte blocks; GPT header/entry CRCs, type GUID and exact userdata bounds are validated.
- Pinned extents map file blocks \[2290688,2290945\) to userdata-relative blocks \[40995328,40995585\); all 257 blocks are unique, contiguous, within userdata, and the extent set has no overlap.
- Logger-owned UFS commands use try-lock and return EBUSY on lock contention; ordinary BSD root reads retain blocking command-lock semantics.
- Logger bootstrap is serialized with an atomic start guard; header write/sync failures schedule delayed callout retry, and syscall pump retries initialization if thread-call allocation fails.

### 操作步骤

- Generate bsd/dev/pudding\_ufs.c with scripts/patch-pudding-ufs.py.
- Run device-dump/check\_log\_extents.py, device-dump/test\_pudding\_gpt\_guard.py and device-dump/verify\_all\_patches.sh; focused-compile with device-dump/compile\_any.py pudding\_ufs.c.
- Boot only with fastboot boot; retrieve the pinned log region read-only from Android after return.

### 开发经验

- 2026-11-11 23:20: Implemented compact signed-prefix BSD VerifiedRoot integration. Shared C adapter reconstructed both complete source windows read-only \(2,290,185 hashes\), byte-identical to original authenticated envelopes; exact generation1, imageSHA256, full-envelopeSHA384, OS1536-byte final block and GPT slice+17408 checked. Fresh blocks are verified within bounce lock before copying. Original verifier/crypto sources remain hash-pinned and unchanged. APFS selected volume UUID plus actual readonly root/cache devices bind original owner publisher; callback readiness fails closed. Host negative/sanitizer tests and six affected focused ARM64 translation units pass; publisher independent review passed after errno inversion repair. Full build/UFS review pending; no device runtime authentication/publication claim and no device operations. See device-dump/pudding-verified-root-runtime-report.md and docs/PROGRESS.md in workspace.
- 2026-11-11: Host-only staging repair limits payload to DATA\_BYTES - in\_block so the OS slice remainder cannot overflow the actual 128 KiB allocation. A separate static bounce mutex spans all fragmented reads through successful copy; strategy lock order is bounce then command, logger remains log then command without bounce, and probe uses staging only before ready. Six host tests cover 45,056 bounds cases, exact bytes, concurrency/failure models and original-defect negative controls; independent review and focused generated pudding\_ufs.c compilation passed. No full rebuild or hardware validation of this repair yet; pinned-tail write boundaries are unchanged.
- The BSD bdevsw path reaches real UFS GPT/manifest and APFS root reads; it avoids unsupported static IOStorageFamily linkage.
- Screen evidence reached periodic log flush and ring read, but did not show a return marker. The read path can block on pudding\_ufs\_cmd\_lock before its bounded UFS command poll, so logger requests now try-lock and should retry on the next scheduled interval.
- The earlier raw ring had header v1/seq=0/total=0 and SHA-256 2ad7d9db9c7270e957232d795c36cb2c33e8c06cac965979331dbd4876e428a4; it was stale, not current-boot evidence.
- 2026-11-10: Replaced logger destination read-modify-write with a full 4 KiB RAM-ring block copy. Device boot committed header seq=99,total=42884; ring write, ring sync, header write/sync and final flush all returned 0. Fresh raw log SHA-256 400063aff2b3cc90858630089f3c4513cf50213869a64c81f8d4b6cb7ca2adaf.
- The same boot reached launchd and dyld shared-region mapping; syscall 536 returned 0. It then entered \_DebuggerTrapWithState+0xec \(ESR EC=0/TRAP\_DEBUGGER\); the original panic message is not present in the committed ring and remains unresolved.

### 完成条件

- Host: capacity, GPT, pinned extents, write allowlist and focused compilation pass.
- Device: current RAM boot produces a fresh committed logger header/ring and periodic try-lock retries do not stall root reads.
- Root: the configured APFS root mounts and launchd continues beyond the last recorded syscall.

### 当前范围

- Fresh logger persistence is device-verified, but panic snapshot capture/clean-sync gate and original panic cause remain unverified.
- No display, touch, GPU, Wi-Fi, audio or sustained power-management milestone is claimed here.

### 下一步

- Trace panic snapshot generation, debugger clean-sync eligibility, lock/controller preflight and panic-log commit without widening the pinned-tail write allowlist; then continue beyond shared-region syscall 536.

### 证据

- `source`: [BSD UFS reader, GPT/capacity validation, bounded logger write window, and logger-only try-lock implementation.](https://github.com/daisukiKaffuChino/UniXNU-pudding/blob/1028ed6b6c1984d7897933333e84a1a09942b80f/scripts/pudding_ufs.c.txt)
- `source`: [Static FIEMAP extent table for the pinned image, including the dedicated log tail.](https://github.com/daisukiKaffuChino/UniXNU-pudding/blob/1028ed6b6c1984d7897933333e84a1a09942b80f/scripts/pudding_ufs_extents.h)
- `source`: [Generates the maintained UFS implementation into the active XNU work tree.](https://github.com/daisukiKaffuChino/UniXNU-pudding/blob/1028ed6b6c1984d7897933333e84a1a09942b80f/scripts/patch-pudding-ufs.py)

## 显示 {#display}

`planned`

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

- 2026-11-11: Host fixture scripts/test-pudding-verified-root-image.c was added to exercise the storage image layout; payload and image assembly are unchanged.

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

- 2026-11-11: check-pudding.py now requires owned\_memory\_size in 256 MiB..8 GiB at 2 MiB steps, not exceeding dram\_size, and the DTS memory node must match dram\_size.

### 完成条件

- Each claimed milestone has a reproducible command, a matching source/image revision and an accessible result.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required diagnostics inputs before implementation.

### 证据

按下一步操作收集证据。

</div>
