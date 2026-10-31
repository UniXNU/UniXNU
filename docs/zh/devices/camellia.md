# Redmi Note 10 5G（camellia）

[stanveyjiang/UniXNU-camellia](https://github.com/stanveyjiang/UniXNU-camellia)

<div v-pre>

Redmi Note 10 5G UEFI bring-up is device-verified through a Linux preboot handoff. UEFI, GOP and the UniXNU payload menu work; native UFS, XNU root, input, GPU, network, audio and XNU power remain incomplete.

源记录: [porting.toml](https://github.com/stanveyjiang/UniXNU-camellia/blob/0139bf0315f709e4efbd6f5b44ad19e8c9496087/porting.toml), `0139bf0315f709e4efbd6f5b44ad19e8c9496087`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `implemented` |
| [固件与启动](#firmware) | `device-verified` |
| [CPU 与中断](#cpu) | `implemented` |
| [内存与 DMA](#memory) | `implemented` |
| [存储与根卷](#storage) | `implemented` |
| [显示](#display) | `device-verified` |
| [输入](#input) | `planned` |
| [GPU](#gpu) | `planned` |
| [网络](#network) | `planned` |
| [音频](#audio) | `planned` |
| [电源](#power) | `planned` |
| [镜像组装](#packaging) | `device-verified` |
| [诊断](#diagnostics) | `device-verified` |

## 配置 {#configuration}

`implemented`

组件: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`, `DarwinBoot`.

### 硬件与依赖

- MT6833 platform identity, iPad7,1 / iPadOS 17.7.11 build 21H461 target identity and the Camellia bootstrap defconfig.

### 配置

- board.soc = MT6833; board.os\_profile = ipados-17.7.11-21H461; schema\_version = 2.
- camellia\_bootstrap\_defconfig enables the shared ARM DT platform, FDT CPU, software AES, mockfs, panic region and prelinked crypto paths.

### 操作步骤

- Run ./unixnu defconfig camellia\_bootstrap\_defconfig --device ../UniXNU-camellia from a UniXNU checkout.
- Run ./unixnu status --device ../UniXNU-camellia --json and inspect the effective component and source pins.

### 开发经验

- The internal kit name remains sheng because Camellia reuses shared prelink and diagnostic helper sources. This does not select Sheng hardware or an SM8550 device tree.
- The hardware SoC identity and the shared Apple image identity are independent configuration inputs.

### 完成条件

- Source pins resolve, the effective configuration contains the intended Camellia overrides and every selected component has an owning area.

### 当前范围

- The Camellia bootstrap profile is intentionally minimal and does not yet select native MT6833 storage, display, input, GPU, network or power components.

### 下一步

- Keep the bootstrap profile reproducible while adding one MT6833 hardware component at a time.

### 证据

- `source`: [Camellia board identity, iPadOS target and prelink roots.](https://github.com/stanveyjiang/UniXNU-camellia/blob/0139bf0315f709e4efbd6f5b44ad19e8c9496087/board.toml)
- `source`: [Current minimal XNU bring-up configuration.](https://github.com/stanveyjiang/UniXNU-camellia/blob/0139bf0315f709e4efbd6f5b44ad19e8c9496087/configs/camellia_bootstrap_defconfig)

## 固件与启动 {#firmware}

`device-verified`

组件: `DarwinBoot`.

### 硬件与依赖

- Camellia UEFI source, a Linux kernel with the jump2 entry, a minimal initramfs, the 64 MiB UniXNU payload and the matching Camellia DTB.

### 配置

- Linux hot-jump FD base is 0xA0000000 and the UEFI stack is 0xA0200000.
- The pre-Android boot image uses Android boot header v2 with kernel 0x40080000, ramdisk 0x51100000 and DTB 0x47C80000.
- The payload is written raw to vendor\_boot\_a and read through /dev/block/sdc31.

### 操作步骤

- Build the hot-jump FD with build-camellia-hotjump.sh and verify C entry and SEC stack.
- Build the boot image with build-boot-image.sh, then flash boot\_a and vendor\_boot\_a.
- Boot from LK through the minimal Linux initramfs, drm\_linear and uefi\_jump into UEFI.

### 开发经验

- LK does not execute a directly embedded BootShim/UEFI FD; that route reset at about 30 seconds.
- The verified route is LK to Linux, minimal initramfs, drm\_linear, uefi\_jump, UEFI and the UniXNU payload menu.
- fastboot boot is unavailable on this device, including with a stock boot image; validation must use fastboot flash boot\_a.

### 完成条件

- UEFI starts from the fixed pre-Android handoff, publishes GOP, reaches BDS and the matching payload reaches the UniXNU menu.

### 当前范围

- The Linux kernel and private Magisk-patched boot input are firmware-specific and are not distributed as the public UEFI source baseline.
- A correct payload is required for UniXNU; without it UEFI reaches only the firmware boot-manager options.

### 下一步

- Optional only: preserve the current verified image, then implement one MT6833 runtime component at a time.
- Do not rebuild the paid BootShim or cold-boot route before reaching the next hardware milestone.

### 证据

- `source`: [Documented verified pre-Android UEFI path and rejected routes.](https://github.com/stanveyjiang/uefi-camellia/blob/31f482a209bd04fd2b264d1fa180fa862966a1a6/BOOT-IMAGE.zh-CN.md)
- `device`: [Device reached UEFI and the Camellia UniXNU payload menu through the pre-Android Linux handoff.](https://github.com/stanveyjiang/uefi-camellia/releases/tag/v2026.10.26)
  Command: <code>fastboot flash boot_a camellia-preboot-uefi-v2026.10.26.img; fastboot flash vendor_boot_a payload.img; fastboot reboot</code>. Revision: `31f482a209bd04fd2b264d1fa180fa862966a1a6`.

## CPU 与中断 {#cpu}

`implemented`

组件: `ArmCpu`, `ArmDTPlatform`.

### 硬件与依赖

- Eight-core MT6833 CPU topology, GIC distributor at 0x0C000000, GIC redistributors at 0x0C040000 and a 13 MHz architectural timer.

### 配置

- CONFIG\_XNU\_ARMCPU=y and CONFIG\_XNU\_ARM\_DT\_PLATFORM=y.
- The hot-jump UEFI patch wakes and resets the interrupted Linux GICv3 redistributor and registers only the physical timer PPI.

### 操作步骤

- Record CPU affinities, GIC ranges and timer frequency from the stock DTB.
- Verify that the hot-jump UEFI path resets GIC PPIs/SGIs and does not claim the interrupted Linux virtual timer.

### 开发经验

- Linux leaves GICv3 redistributor and private interrupt state behind; leaving that state unchanged can stop early DXE.
- The interrupted Linux virtual timer source must not be registered by the UEFI timer driver.

### 完成条件

- UEFI runs with stable timer and interrupt state on the boot CPU, and later XNU observes every enabled CPU with working timer/IPI delivery.

### 当前范围

- UEFI boot-CPU interrupt stabilization is implemented; full XNU SMP affinity and IPI behavior has not been device-verified.

### 下一步

- Add per-CPU entry and IPI evidence when an XNU image reaches multiprocessor startup.

### 证据

- `source`: [GICv3 redistributor reset and physical-timer registration fixes.](https://github.com/stanveyjiang/uefi-camellia/blob/31f482a209bd04fd2b264d1fa180fa862966a1a6/Resources/MuPatches/Camellia-Essential.patch)

## 内存与 DMA {#memory}

`implemented`

### 硬件与依赖

- DRAM, payload storage, DTB, ATF/TEE reservations, high-DDR windows and the MTK DRM framebuffer physical page runs.

### 配置

- UEFI FD base 0xA0000000, UEFI stack 0xA0200000, framebuffer handoff page 0xA4000000 and payload RAM at 0x98000000.
- The hot-jump path opens a conventional high-DDR window at 0x200000000 with size 0x03FFF0000 while retaining the high-DDR tail reservation.

### 操作步骤

- Read the framebuffer run map before UEFI MMU setup and add uncached or write-through descriptors for runs outside the static map.
- Validate the FD destination, framebuffer page map and payload handoff before stopping secondary CPUs.

### 开发经验

- The DRM framebuffer is contiguous in IOVA, not necessarily in CPU physical memory. A single translated base address is insufficient.
- Some scanout pages lie outside the original static UEFI memory map, so the hot-jump path must publish their physical runs.

### 完成条件

- Every framebuffer and payload page maps to the intended physical range, and UEFI reaches BDS without an address translation fault.

### 当前范围

- DMA ownership and SMMU mappings for MT6833 storage, display and GPU are not yet implemented.

### 下一步

- Convert the verified handoff map into explicit DMA and IOMMU ownership records for each future hardware driver.

### 证据

- `source`: [Camellia memory reservations, high-DDR window and framebuffer run-map handling.](https://github.com/stanveyjiang/uefi-camellia/blob/31f482a209bd04fd2b264d1fa180fa862966a1a6/Platforms/Xiaomi/camelliaPkg/Library/MemoryMapLib/MemoryMapLib.c)

## 存储与根卷 {#storage}

`implemented`

组件: `RamBlock`.

### 硬件与依赖

- UFS is the device boot storage. The current verified path additionally uses vendor\_boot\_a as a raw 64 MiB payload store.

### 配置

- The pre-Android initramfs creates /dev/block/sdc31 and uefi\_jump copies exactly 0x4000000 payload bytes to RAM.
- A RAM block device and FAT volume make the UniXNU payload visible without native UFS support.

### 操作步骤

- Write the 64 MiB payload to vendor\_boot\_a and verify its hash.
- Load uefi\_jump with payload\_path=/dev/block/sdc31 and payload\_bytes=67108864.
- Confirm the RAM block device and UniXNU menu enumerate the payload.

### 开发经验

- Native UFS reads are not available in the current Camellia UEFI path.
- RAM payload publication is sufficient for the verified UniXNU menu and avoids depending on UFS during bring-up.

### 完成条件

- RAM payload publication works for the selected image, and a later native UFS implementation reads the GPT, root windows and persistent Data correctly.

### 当前范围

- The UFS controller, PHY, clocks, reset, power, SMMU stream and LUN path are not implemented.
- XNU root-device lookup and persistent user data are not verified on Camellia.

### 下一步

- Measure the MT6833 UFS host/PHY registers, clock and power ownership, link state and SMMU stream before implementing native UFS.

### 证据

- `source`: [Fixed-length payload block read and RAM payload handoff.](https://github.com/stanveyjiang/uefi-camellia/blob/31f482a209bd04fd2b264d1fa180fa862966a1a6/module/uefi_jump/uefi_jump.c)

## 显示 {#display}

`device-verified`

组件: `GopFramebuffer`.

### 硬件与依赖

- Tianma NT36672C panel, 1080x2400 mode, MTK DRM scanout, 32 bpp BGRX pixels and GOP.

### 配置

- SimpleFbDxe presents a logical 1088x2400 BGRX GOP using the framebuffer run map.
- UEFI writes through the scattered physical page map instead of assuming one contiguous physical framebuffer.

### 操作步骤

- Start drm\_linear from the initramfs, let uefi\_jump publish the run map and enter UEFI.
- Verify UEFI text, GOP geometry, colors and BDS presentation on the phone.

### 开发经验

- The verified display transport is the Linux-built linear framebuffer carried into UEFI GOP.
- The full MTK DSI/DRM driver stack is not initialized by UEFI and is not required for the current UEFI and UniXNU menu.

### 完成条件

- UEFI and the UniXNU menu render with correct geometry and colors, and a later XNU display path presents userland frames.

### 当前范围

- XNU native display, backlight control and GPU composition are not implemented.
- Display output depends on the matching Linux DRM framebuffer handoff.

### 下一步

- Preserve GOP presentation while implementing the first MT6833 XNU display provider.

### 证据

- `source`: [Framebuffer and GOP handoff design.](https://github.com/stanveyjiang/uefi-camellia/blob/31f482a209bd04fd2b264d1fa180fa862966a1a6/GUIDE.zh-CN.md)
- `device`: [Device displayed the verified framebuffer stages, UEFI and the Camellia UniXNU menu.](https://github.com/stanveyjiang/uefi-camellia/releases/tag/v2026.10.26)
  Command: <code>fastboot flash boot_a camellia-preboot-uefi-v2026.10.26.img; fastboot flash vendor_boot_a payload.img; fastboot reboot</code>. Revision: `31f482a209bd04fd2b264d1fa180fa862966a1a6`.

## 输入 {#input}

`planned`

### 硬件与依赖

- FocalTech touch controller over SPI4, volume/power keys and display coordinate geometry.

### 配置

- The current UEFI boot options use a timer because no input device is published.

### 操作步骤

- Identify the touch bus, reset and interrupt GPIOs, panel coordinates and keypad GPIOs from the stock DTB.

### 开发经验

- No UEFI input device is available in the current verified image; the boot menu relies on its default timed selection.

### 完成条件

- Keys navigate UEFI, touch reports map to display coordinates, contacts keep stable IDs and release events arrive.

### 当前范围

- Touch and keypad integration are absent from the current boot path.

### 下一步

- Map FocalTech SPI4 and the keypad GPIOs from the stock DTB before implementing a UEFI input driver.

### 证据

按下一步操作收集证据。

## GPU {#gpu}

`planned`

### 硬件与依赖

- MT6833 Mali GPU, power domains, clocks, IOMMU and the selected Apple graphics ABI.

### 配置

- CONFIG\_XNU\_NATIVE\_MOBILE\_DISPLAY=n; no XNU GPU component is selected in camellia\_bootstrap\_defconfig.

### 操作步骤

- Inventory MT6833 GPU power, clock and IOMMU inputs before selecting a frontend ABI.

### 开发经验

- Shared Adreno components are not applicable to the MediaTek GPU.

### 完成条件

- GPU commands complete, synchronization and memory mapping work, and a known image is presented.

### 当前范围

- No MT6833 GPU driver or Apple graphics frontend is implemented.

### 下一步

- Collect the MT6833 GPU/GMU and IOMMU hardware inventory after XNU reaches IOKit initialization.

### 证据

按下一步操作收集证据。

## 网络 {#network}

`planned`

### 硬件与依赖

- MT6833 Wi-Fi controller, firmware, bus, interrupts, DMA and the selected XNU network interface.

### 配置

- No XNU network component is selected in the Camellia bootstrap profile.

### 操作步骤

- Identify the Wi-Fi bus and firmware loading path from the stock DTB and vendor services.

### 开发经验

- The shared Ath12k path is Qualcomm-specific and does not describe the Camellia controller.

### 完成条件

- The controller initializes, associates, obtains an address and carries sustained receive/transmit traffic.

### 当前范围

- Network support is not implemented.

### 下一步

- Inventory the MT6833 Wi-Fi device and firmware interface.

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`planned`

### 硬件与依赖

- MT6833 audio DSP, codec, clocks, routing, firmware services and XNU audio ABI.

### 配置

- No Camellia audio component is selected in the bootstrap defconfig.

### 操作步骤

- Identify the audio DSP, codec and routing resources from the stock DTB.

### 开发经验

- Shared Qualcomm ADSP and audio components are not applicable to Camellia.

### 完成条件

- A declared route carries playback or capture through start, stop and format changes.

### 当前范围

- Audio is not implemented.

### 下一步

- Inventory the MediaTek audio hardware after XNU reaches the relevant IOKit phase.

### 证据

按下一步操作收集证据。

## 电源 {#power}

`planned`

### 硬件与依赖

- MT6359 PMIC, MT6833 clocks and power domains, charger, battery and XNU power management.

### 配置

- Camellia uses inherited MT6789 PMIC-wrapper code as a bring-up placeholder.
- No XNU battery or board power component is selected.

### 操作步骤

- Map PMIC rails, clocks and power domains before enabling XNU power transitions.

### 开发经验

- The current boot path does not initialize a complete MT6359 power stack.
- Earlier forced display and power paths could stop early boot; the verified path keeps vendor hardware untouched where possible.

### 完成条件

- Power rails, clocks, battery units and suspend/resume transitions match device observations.

### 当前范围

- Native MT6359 power management and XNU battery/charging support are incomplete.

### 下一步

- Inventory MT6359 rails and ownership, then implement one power domain at a time.

### 证据

按下一步操作收集证据。

## 镜像组装 {#packaging}

`device-verified`

组件: `DarwinBoot`, `XnuPrelink`, `SoftwareAES`.

### 硬件与依赖

- iPad7,1 iPadOS 17.7.11 build 21H461 kernelcache, prelink roots, ADT, trust cache, Data seed, firmware FD and 64 MiB payload.

### 配置

- The public firmware release pairs FD sha256 68184f8a1451d08a90fafc61b1163e6e2056469bac174ebc5c71b38f23bfc406 with uefi\_jump sha256 bec844cf909a8032efe33b58c879ba6ff499036263c824672a47afdc9f3a71c6.
- Release boot image sha256 is 1fc459383672b0e1c6df7687bba8342e9ec12bf230a7df98b461407190d1b939.

### 操作步骤

- Build the 4 KiB XNU/prelink inputs, ADT and payload and keep their hashes with the image record.
- Assemble the Android boot v2 image and verify kernel, ramdisk and DTB offsets.
- Flash boot\_a and the raw payload to vendor\_boot\_a, then confirm the UniXNU menu.

### 开发经验

- The boot image contains UEFI handoff, KO and drm\_linear but not the XNU payload.
- Without a payload UEFI shows only firmware boot-manager entries; with the matching payload the Camellia UniXNU menu appears.
- XNU 4 KiB page-table work is separate from the verified UEFI handoff.

### 完成条件

- The generated boot image and payload have stable hashes, match the target boot format and reach the expected XNU entry or UI milestone.

### 当前范围

- A usable Camellia XNU kernel/root path is not yet verified to userland.
- The private Magisk/jump2 boot build input is intentionally not published.

### 下一步

- Record the kernel, ADT, trust cache and payload hashes with the next 4 KiB XNU image used on the phone.

### 证据

- `source`: [Boot v2 geometry, payload layout and flash procedure.](https://github.com/stanveyjiang/uefi-camellia/blob/31f482a209bd04fd2b264d1fa180fa862966a1a6/BOOT-IMAGE.zh-CN.md)
- `device`: [Device reached UEFI and the Camellia UniXNU payload menu.](https://github.com/stanveyjiang/uefi-camellia/releases/tag/v2026.10.26)
  Command: <code>fastboot flash boot_a camellia-preboot-uefi-v2026.10.26.img; fastboot flash vendor_boot_a payload.img; fastboot reboot</code>. Revision: `31f482a209bd04fd2b264d1fa180fa862966a1a6`.

## 诊断 {#diagnostics}

`device-verified`

### 硬件与依赖

- Framebuffer debug console, UEFI stage colors, podman/pstore notes where available, Linux hot-jump dmesg and fastboot recovery.

### 配置

- CONFIG\_XNU\_DT\_PANIC\_REGION=y and CONFIG\_XNU\_NATIVE\_PAN=y.
- The pre-Android stage uses red, green, cyan and magenta framebuffer states; UEFI uses the framebuffer-backed console.

### 操作步骤

- Record FD, KO, payload and boot-image hashes before every device test.
- Record the last visible stage, UEFI driver name, exception PC/ESR/FAR or the first failing operation.
- Keep original boot\_a and vendor\_boot\_a images available before flashing.

### 开发经验

- A fixed approximately 25-30 second reset can identify a loader or early UEFI failure and should not be assumed to be a DXE watchdog.
- The direct BootShim route and a base-only hot-jump FD both fail; checking FD entry and stack prevents misdiagnosis.
- The final boot image can show a short pause before continuing, so a brief delay is not by itself a failure.

### 完成条件

- Each claimed milestone has an image hash, source revision, command and observed device result, with a tested recovery route.

### 当前范围

- Phone UART is not available for all early paths; some diagnostics rely on framebuffer stages and Android dmesg.

### 下一步

- Add a pstore or USB serial transport when the next XNU milestone needs logs beyond the framebuffer.

### 证据

- `source`: [Boot-stage diagnostics, recovery and hash requirements.](https://github.com/stanveyjiang/uefi-camellia/blob/31f482a209bd04fd2b264d1fa180fa862966a1a6/GUIDE.zh-CN.md)
- `device`: [Final boot image reached UEFI after a short initial pause and was recoverable with the stock partitions.](https://github.com/stanveyjiang/uefi-camellia/releases/tag/v2026.10.26)
  Command: <code>fastboot flash boot_a camellia-preboot-uefi-v2026.10.26.img; fastboot flash vendor_boot_a payload.img; fastboot reboot</code>. Revision: `31f482a209bd04fd2b264d1fa180fa862966a1a6`.

</div>
