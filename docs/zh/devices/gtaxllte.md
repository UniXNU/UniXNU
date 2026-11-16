# Samsung Galaxy Tab A 10.1 \(2016\) LTE \(SM-T585\)

[ahmedraafat-official/UniXNU-gtaxllte](https://github.com/ahmedraafat-official/UniXNU-gtaxllte)

<div v-pre>

Samsung Galaxy Tab A 10.1 \(2016\) LTE \(SM-T585\). S-Boot loads the UniXNU UEFI, the menu and DarwinBoot hand off to XNU, and the prelinked kernel reaches PE\_init\_iokit. Storage, display, input and GPU drivers are the remaining work.

源记录: [porting.toml](https://github.com/ahmedraafat-official/UniXNU-gtaxllte/blob/bcd4771270ce62815985d89ed17d17cf1099e38d/porting.toml), `bcd4771270ce62815985d89ed17d17cf1099e38d`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `planned` |
| [固件与启动](#firmware) | `device-verified` |
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

- The prelinked payload is the working architecture: it is written to HIDDEN \(mmcblk0p21, 60 MiB FAT16, label UNIXNU\) and loaded from EFI/UniXNU/Payloads/kernel.macho because the 49 MiB image cannot fit the 14 MiB ramdisk.
- The prelinked AppleARMPlatform ships an AppleARMCPU personality with IONameMatch cpu; IODTPlatformExpert matches by prefix and would claim the Exynos /cpus. The kernel artifact is rewritten byte-for-byte to xpu before it is written to HIDDEN.
- The prelink roots are trimmed to the software, security and storage closure plus AppleARMPlatform and ApplePMGR; the display, GPU and media kexts wait for Apple hardware and are excluded until the Exynos drivers exist.

### 完成条件

- All source pins resolve; every selected component has a record; status shows the intended overrides and patch order.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required configuration inputs before implementation.

### 证据

按下一步操作收集证据。

## 固件与启动 {#firmware}

`device-verified`

### 硬件与依赖

- Identify the firmware and boot hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for firmware and boot.

### 操作步骤

- Follow the firmware and boot stage in the porting guide and record the actual commands.

### 开发经验

- S-Boot loads the UniXNU UEFI, the menu entries run, and DarwinBoot reports the prelinked kernel virtual address, entry point and boot args before branching to XNU.
- Early kernel progress is visible through direct framebuffer bars at y=400/500/600/700: green after arm\_vm\_init, red after the console init, blue at PE\_init\_iokit, yellow at bsd\_init. Green, red and blue appear; yellow does not yet.

### 完成条件

- Firmware image builds, enters UniXNU, publishes the framebuffer and preserves the documented memory reservations.

### 当前范围

- The prelinked kernel stops inside IOKit before bsd\_init; storage and display drivers are not built yet.

### 下一步

- Name the IOKit sub-phase that stops the prelinked kernel with the traced framebuffer squares.

### 证据

- `device`: [S-Boot loads the UniXNU UEFI, the menu boots, DarwinBoot hands off to the prelinked kernel, and the early framebuffer bars appear on the panel.](https://github.com/ahmedraafat-official/UniXNU-gtaxllte/blob/bcd4771270ce62815985d89ed17d17cf1099e38d/PHASE0.md)
  Command: <code>manual boot of the SM-T585; the photos are recorded in the workspace</code>. Revision: `f45b68897f5f48da0026881847d9204680c9dd24`.

## CPU 与中断 {#cpu}

`planned`

### 硬件与依赖

- Identify the cpu and interrupts hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for cpu and interrupts.

### 操作步骤

- Follow the cpu and interrupts stage in the porting guide and record the actual commands.

### 开发经验

- ArmCpu owns /cpus and the architectural timer; the prelinked AppleARMCPU IONameMatch is rewritten to xpu so it cannot claim the Exynos cores.
- The ADT must describe the GIC cell counts the kernel expects; the missing counts were fixed before the prelinked path became primary.

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

- The kernel direct-maps the UEFI framebuffer at 0x67000000 \(1200x1920, 32 bpp, 4800-byte rows\) with ml\_io\_map\_wcomb; the green/red/blue stage bars are direct writes there.
- The prelinked kernel cannot use the corecrypto kernel RNG before the kext providers start, so the kmem size-class randomization and the platform UUID are guarded and crypto-free in the prelinked series.

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

### 硬件与依赖

- Identify the storage and root hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for storage and root.

### 操作步骤

- Follow the storage and root stage in the porting guide and record the actual commands.

### 开发经验

- The eMMC is a Samsung MSHC at 0x13540000: VERID 0x6c, RINTSTS 0x44, STATUS 0x48, FIFO 0x100 or 0x200, 32-bit FIFO items, 8-bit bus; Mu-Silicium MshcDxe initializes it and leaves the card selected with 512-byte blocks.
- USERDATA is mmcblk0p23 at LBA 8,013,824 with 53,043,200 sectors; HIDDEN is mmcblk0p21 at LBA 7,880,704 with 122,880 sectors. The read-only bsd\_init probe prints the controller state and reads LBA 0/1 through the PIO FIFO.
- No block driver or root mount exists yet; the first goal is the GPT signature \(EFI PART\) from the probe, then IOBlockStorageDevice publication.
- The same probe is also reachable from arm\_init behind an emmc-probe=1 boot argument, so the eMMC state can be read even while the prelinked kernel still hangs inside IOKit.

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

### 硬件与依赖

- Identify the display hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for display.

### 操作步骤

- Follow the display stage in the porting guide and record the actual commands.

### 开发经验

- Only the UEFI GOP framebuffer is used: DECON/DSI, backlight and touch are not programmed by XNU.
- The stage bars prove the framebuffer mapping and the UEFI mode are usable before the display driver exists.

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

- Collect the first input observation, its cause when established, and the resulting implementation decision.

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

- The Mali-T830 is Midgard v5 with a Job Manager; Mesa PanVK has no arch 5 backend, so the GPU needs a new PanVK backend and a NativeMali JM driver.
- The GPU plan lives in a separate repository; no GPU code or hardware access runs in this image yet.

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

- The prelink build overrides the device patch series: native-only workarounds are excluded, while the early framebuffer bars, the NULL-safe kmem wrapper, the crypto-free platform UUID, the read-only eMMC probe and the IOKit trace squares stay in.
- The package step always fails at strip on the 49 MiB prelinked Mach-O; the prelinked-kernel artifact is uploaded with if: always\(\) and is the image written to HIDDEN.
- The payload step patches a copy of the prelinked kernel with the entry bars and the framebuffer panic screen before strip fails; that stage copy is uploaded with the raw kernel and is preferred when staging, because it renders panic arguments on the panel without a serial console.
- The prelink series now also carries the boot-phase trace squares \(startup/bootstrap\) and the boot-argument-gated early eMMC probe, so one image answers both the IOKit hang and the storage question.
- The payload builder now generates the ADT sidecar before the strip step, so a failed prelinked package still yields a fresh kernel.macho.adt next to the patched kernel; staging the ADT is opt-in until it is compared with the working one.
- Device XNU patches are generated against the post-arch-series source, not the pristine XNU tree: offline-component-load-probes.patch inserts its probes between the bsd\_init comment and the function, so a context built from the pristine file no longer applies.
- The boot-phase squares showed the prelinked kernel completing PE\_lockdown\_iokit and then stopping before bsd\_init. The only blocking call between them is kperf\_init\_early\(\)-&gt;ml\_wait\_max\_cpus\(\); the native ArmCpu path does not call ml\_set\_max\_cpus\(\) on this board, so the boot now marks the maximum CPU count set explicitly before the VM restrictions and kperf.
- The first eMMC read completed with zero data: HCON\[9:7\]=2 means a 64-bit FIFO, and the probe consumed one 32-bit word per FIFO item. The probes now take the item width from HCON, read both words per item, and require RINTSTS DTO before reporting success.

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

- The direct framebuffer bars are the primary early-boot diagnostic because the Apple console/panic path waits for hardware and can stay dark.
- The prelinked kernel reaches PE\_init\_iokit \(blue\); the IOKit trace squares now mark IOLibInit, OSlibkernInit, IOMachPortInitialize, the root nub and ConfigureIOKit to name the next stop.

### 完成条件

- Each claimed milestone has a reproducible command, a matching source/image revision and an accessible result.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required diagnostics inputs before implementation.

### 证据

按下一步操作收集证据。

</div>
