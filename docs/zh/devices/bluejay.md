# Google Pixel 6a \(Tensor G1\)

[tuxmanxd/UniXNU-bluejay](https://github.com/tuxmanxd/UniXNU-bluejay)

<div v-pre>

Google Pixel 6a \(bluejay, Tensor G1\) port scaffold. Hardware values come from the pixelios-kernel research port, which boots XNU 8796 with the iOS 16.7 userland on this phone; this repository restates them in UniXNU format. No UniXNU image has been built or booted for this board yet.

源记录: [porting.toml](https://github.com/tuxmanxd/UniXNU-bluejay/blob/3b0c11f78352d3399d1c603d951a6fcbebca2ab7/porting.toml), `3b0c11f78352d3399d1c603d951a6fcbebca2ab7`.

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
| [cellular](#cellular) | `not-applicable` |
| [音频](#audio) | `planned` |
| [电源](#power) | `planned` |
| [镜像组装](#packaging) | `implemented` |
| [usb](#usb) | `planned` |
| [诊断](#diagnostics) | `planned` |

## 配置 {#configuration}

`implemented`

组件: `ArmDTPlatform`, `ArmCpu`, `XnuPrelink`, `DarwinBoot`, `GopFramebuffer`.

### 硬件与依赖

- Google Pixel 6a \(bluejay\), Tensor G1 \(GS101\), 6 GiB DRAM \(2 GiB low bank + 4 GiB high pair, measured\), 128 GiB UFS, 1080x2400 panel.
- pixelios-kernel hardware descriptions: soc/google/gs101/soc.json, device/google/bluejay/board.json, docs/research/05-fact-check.md.

### 配置

- board.soc\_source = gs101 pins UniXNU-gs101-common; board.os\_profile = ipados-17.7.11-21H461.
- config\_fragments apply in order arch, soc, os; the resolved defconfig bluejay\_defconfig applies last.
- patch\_series is arch, soc, os, device; every series except device is inherited and currently empty for this SoC.

### 操作步骤

- From a UniXNU checkout: ./unixnu defconfig bluejay\_defconfig -D ../UniXNU-bluejay
- ./unixnu fetch -D ../UniXNU-bluejay; ./unixnu status --json -D ../UniXNU-bluejay
- python3 scripts/porting-record.py check --device ../UniXNU-bluejay

### 开发经验

- UniXNU ships only iPadOS 17.7.11, iPadOS 26.5.2, iPadOS 27.0.1 and macOS 27.3 OS profiles. There is no iPhone/iOS 16.7-20H19 profile, so this scaffold selects the oldest shipped profile; a native iPhone profile is required before the result is a real phone port.
- pixelios boots XNU 8796 \(iOS 16 generation\). UniXNU pins a newer XNU and its own ordered patch series, so the pixelios patch stack is not reused as-is.
- The pixelios shim is a bare-metal EL2 loader, not UEFI. Its hardware facts \(UFS cold re-init, HS-G4 link, memory map, device tree\) are reusable; its code is not a UniXNU component.
- The SoC commit pinned in feeds.toml is the first commit of UniXNU-gs101-common and must be replaced with the reviewed published commit.
- The device owns no board driver submodules yet: Gs101Ufs, FTM5 touch and GS101 power are unassigned.

### 完成条件

- Every source pin resolves; status shows the intended profiles, components and patch order; the porting record check passes.

### 当前范围

- No component build has been attempted; UniXNU, uefi-bluejay and a working IPSW profile are missing.

### 下一步

- Clone UniXNU beside this repository, run defconfig, fetch and status, and record the resolved output.

### 证据

- `source`: [Board hardware values \(DRAM banks, framebuffer, userdata geometry, keys, touch\).](https://github.com/PixOS-Project/pixelios-kernel/blob/main/device/google/bluejay/board.json)
- `source`: [SoC register bases, GIC/timer, UFS, USB, UART, WLAN and GPU resources.](https://github.com/PixOS-Project/pixelios-kernel/blob/main/soc/google/gs101/soc.json)

## 固件与启动 {#firmware}

`implemented`

组件: `DarwinBoot`.

### 硬件与依赖

- tuxmanxd/uefi-bluejay: the Mu-Silicium GS101/Pixel 6a platform \(bluejayPkg + GS101Pkg\), installed with scripts/apply.sh.
- Google Pixel 6a factory image for vendor firmware inputs.
- ABL hands over a linear framebuffer at 0xfac00000 and a live FDT.

### 配置

- \[firmware\] config = bluejay, dsc = Platforms/Google/bluejayPkg/bluejay.dsc, fd = Build/bluejayPkg/&\#123;target&\#125;\_CLANGPDB/FV/SILICIUM\_UEFI.fd.
- \[firmware.defines\] DEVICE\_MODEL = bluejay. \[bootimg.image\] header\_version 4, kernel\_compression none: ABL rejects a nonzero arm64 text\_offset, so the shim is built with text\_offset 0.
- \[bootimg\] dtb is written by the firmware preflight: a 4 KiB FDT envelope followed by the real payload volume, because the pack stage appends only that file to the kernel field.
- \[payload\] size\_mib 54: the volume carries kernel.macho \(49.5 MiB\) plus the ADT; boot.img is checked against boot\_partition\_bytes 67108864.

### 操作步骤

- Install uefi-bluejay into a Mu-Silicium checkout with scripts/apply.sh, following https://unixnu.com/porting/uefi-firmware, then build the firmware volume with build\_uefi.py -d bluejay.
- Run scripts/package.sh --check --os 17.
- Boot the artifact with fastboot boot and read the panel.

### 开发经验

- The stock bootloader boots Android boot images only, so UniXNU must be packaged as a boot image first \(layer 1\) before the firmware volume is reachable; the pixelios fastboot boot flow proves this path on the phone.
- ABL sets up the panel framebuffer and provides no framebuffer node in its FDT; the address and size are measured \(0xfac00000, 0x9e3400\).
- The phone is read-only toward storage in the pixelios pre-kernel path; any UniXNU firmware must preserve that property until the userdata install is explicit.
- Tensor ABL caps the boot image ramdisk at 32 MiB \(measured 2026-11-15: 4 and 32 MiB boot, 36/40/42/44/46/48/54/56 MiB are refused, header v0 and v4 alike\), while the prelinked kernel alone is 49.5 MiB. The payload therefore travels in the kernel field, which accepts 56 MiB.
- ABL does not parse bytes appended after the FD: a kernel field with 54 MiB of 0xAA after the FD still boots the firmware, so the field can carry the payload volume behind a 4 KiB envelope.

### 完成条件

- The firmware volume builds, UniXNU.efi runs from it, the menu appears on the panel and the memory map matches the DTS reservations.

### 当前范围

- The menu scrolls without input on hardware; the xnu boot entry has not been reached yet. No firmware archive pin and no proprietary file hashes yet.

### 下一步

- Boot the kernel-field payload image, confirm that UniXNU finds EFI/UniXNU/unixnu.toml on the payload volume, then fix the menu input/redraw bug.

### 证据

- `source`: [Boot chain, ABL handoff, framebuffer and boot image parameters.](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/01-boot-path.md)

## CPU 与中断 {#cpu}

`implemented`

组件: `ArmCpu`.

### 硬件与依赖

- 8 cores: 4x Cortex-A55, 2x Cortex-A76, 2x Cortex-X1.
- GICD 0x10400000 \(64 KiB\), GICR 0x10440000 \(1 MiB, 8 redistributors, stride 0x20000\).
- CNTFRQ 24.576 MHz; virtual timer PPI 11 = INTID 27.

### 配置

- cpus/timebase-frequency = &lt;24576000&gt;; psci method smc.
- unixnu,cluster-type = E for cpu0-3 and P for cpu4-7 in the board DTS.
- CONFIG\_XNU\_ARMCPU=y and CONFIG\_XNU\_ARM\_DT\_PLATFORM=y.

### 操作步骤

- Compile dts/bluejay.dts against soc:dts, boot, and read the CPU and interrupt bring-up lines from the kernel log.

### 开发经验

- The big cluster mixes A76 and X1 cores; treating cpu4-7 as one P cluster is a scheduling policy choice, not a hardware boundary.
- GICv3 needs both the distributor and all eight redistributor frames; a truncated GICR size leaves secondary CPUs unable to start.
- pixelios boots all 8 CPUs with a custom boot-CPU driver \(XNU patch 0018\), which UniXNU ArmCpu replaces.

### 完成条件

- All 8 CPUs come online, IPIs work, the timer ticks at 24.576 MHz and secondary CPUs survive idle.

### 当前范围

- Not run on hardware in this configuration; cluster mapping has not been validated under UniXNU.

### 下一步

- Boot the firmware and kernel and record the CPU startup and timer lines.

### 证据

- `source`: [GIC and timer values confirmed against the vendor DTS.](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/05-fact-check.md)

## 内存与 DMA {#memory}

`implemented`

组件: `ArmDTPlatform`.

### 硬件与依赖

- DRAM banks measured: 0x80000000 \(2 GiB, carve-outs\), 0x880000000 and 0x900000000 \(2 GiB each, contiguous, no reserved range inside\).
- XNU range: 0x884000000 size 0xf0000000 \(the high pair after the firmware payload window, 3840 MiB, 137.9 MiB under the 0xF89F6000 run measured with the kernel image still held\).
- USB DMA carve-out: 0xf8800000 size 0x1000000 \(ABL, no-map\).

### 配置

- One memory node for the high range only: reg = &lt;0x8 0x84000000 0x0 0xf0000000&gt;.
- payload.adt.owned\_memory\_size = 0xf0000000; dram\_size = 0xf0000000.
- The first 64 MiB of the high range \(0x880000000\) is the firmware payload window: reserved in the UEFI map, outside XNU's node.
- reserved-memory/framebuffer@fac00000 is no-map.

### 操作步骤

- Compare the firmware memory map with the DTS, then check that XNU boots with the full 4 GiB and no overlap.

### 开发经验

- XNU maps \[kernel, physBase+memSize\) cacheable, so the range must contain no carve-out and its base and size must be multiples of 32 MiB \(16K-granule L2 block\). The high pair, minus the 64 MiB payload window, satisfies both.
- The payload volume travels in the boot image kernel field because Tensor ABL caps the ramdisk at 32 MiB; BootShim copies it to 0x880000000 before the MMU is on, and the firmware maps that window as reserved.
- The low bank cannot be handed over whole: ABL reserves several no-map ranges, including its 16 MiB USB event buffer. Its allocation moves between boots \(0xF8B92000, 0xF8D12000 observed\).
- The 0xfac00000 framebuffer is below the XNU range, so it needs a reservation for firmware/DarwinBoot but does not fragment owned memory.

### 完成条件

- XNU sees 0xf0000000 bytes of owned memory, boots past pmap setup, and the framebuffer, USB carve-outs and payload window stay untouched.

### 当前范围

- The low bank is not adopted; memory outside the window is unavailable to the OS.

### 下一步

- Measure the firmware memory map in the UniXNU boot log and confirm the DTS reservations.

### 证据

- `source`: [DRAM banks, XNU RAM range, framebuffer and USB DMA range with measurement notes.](https://github.com/PixOS-Project/pixelios-kernel/blob/main/device/google/bluejay/board.json)

## 存储与根卷 {#storage}

`planned`

### 硬件与依赖

- UFS host controller 0x14700000, vendor HCI +0x1100, UNIPRO 0x14780000, PHY/PMA 0x14704000.
- UFS LUN 0 GPT: userdata first 0x22F1E6, last 0x1DC03FA, 4096-byte LBAs.
- Cold re-init after the bootloader shuts the controller down, then HS-G4 link.

### 配置

- &amp;ufs and &amp;ufsphy status = okay; CONFIG\_XNU\_NATIVE\_UFS=y.
- \[userdata\] first\_lba/last\_lba/lba\_bytes in board.toml.

### 操作步骤

- Implement a Gs101Ufs component \(or a board driver\) from the pixelios UFS cold-init sequence, then mount the iOS root read-only and verify the GPT geometry.

### 开发经验

- The bootloader leaves the UFS controller off; a plain HCI reset is not enough and the pixelios shim reprograms vendor HCI, UNIPRO and the PHY before the link trains.
- The link is switched to HS-G4 \(12x read throughput\); the gear change is part of bring-up, not a later optimisation.
- The root lives in userdata, so the partition geometry is fixed by the phone GPT and is recorded in board.toml.
- No shared UniXNU UFS component supports Exynos/GS101 UFS yet; ShengUfs is Qualcomm-specific and cannot be reused.

### 完成条件

- The kernel enumerates the UFS LUNs, reads the GPT and mounts the root; a full read of userdata completes without CRC errors.

### 当前范围

- No driver code; the pixelios implementation is bare-metal C in the shim, not an XNU kext.

### 下一步

- Port shim ufsinit.c to a UniXNU storage component and prove a read-only userdata read.

### 证据

- `source`: [UFS cold re-init, vendor HCI/UNIPRO/PHY windows and HS-G4 sequence.](https://github.com/PixOS-Project/pixelios-kernel/blob/main/soc/google/gs101/shim/ufsinit.c)

## 显示 {#display}

`planned`

组件: `GopFramebuffer`.

### 硬件与依赖

- Framebuffer 0xfac00000, size 0x9e3400, 1080x2400, stride 4320, a8r8g8b8, set up by ABL.
- No framebuffer node in the firmware FDT.

### 配置

- reserved-memory/framebuffer@fac00000 label cont\_splash\_region, no-map.
- CONFIG\_XNU\_NATIVE\_LEGACY\_DISPLAY=y.

### 操作步骤

- Describe the scanout buffer as the GOP handoff, boot, and check that the boot logo and the first frames appear.

### 开发经验

- ABL programs the panel and leaves a linear buffer; there is no display controller driver in the pixelios pre-kernel path.
- 1080x2400 with a 4320-byte stride is 4 bytes per pixel with no padding beyond the width.
- The pixelios kernel only patches an early framebuffer console \(XNU patch 0003\) and later hands off to a software-rendered UI.

### 完成条件

- The firmware menu and the XNU boot text render, and the framebuffer is not reclaimed as free memory.

### 当前范围

- No panel, backlight or DPU driver; brightness control is absent.

### 下一步

- Map the measured buffer into GopFramebuffer and confirm the handoff on hardware.

### 证据

- `source`: [Framebuffer base, size, width, height and stride.](https://github.com/PixOS-Project/pixelios-kernel/blob/main/device/google/bluejay/board.json)

## 输入 {#input}

`planned`

### 硬件与依赖

- STMicro FTM5 touch, chip ID bytes 0x36 0x48, SPI11 / USI11 at 0x10D40000, USI mode register 0x10C2100C, max 10 MHz.
- Pins: gpp23-0..2 SPI function 2, CS gpp23-3, IRQ gpa9-0 \(XEINT\_20\), reset gpp26-0, TS\_SPI\_SEL gpp26-1.
- Power: S2MPG10 LDO25M/LDO26M. Keys: power gpa10, vol+ gpa8, vol- gpa7, all active low.

### 配置

- DTS touch node with st,max-coords and spi-max-frequency, currently disabled.
- \[adt.buttons\] button-names = hold, voldown, volup.

### 操作步骤

- Implement the FTM5 SPI driver and pinctrl/rail setup, then verify contacts and the three buttons.

### 开发经验

- Touch works on hardware under pixelios \(2026-10-22\): the lock screen and home screen respond, so the wiring and firmware protocol are proven.
- The touch controller is behind USI in SPI mode; the USI mode register must be programmed before the SPI transfers.
- GPIO keys are read directly through the pinctrl banks; uniXNU uses the ADT buttons node instead of the pixelios /sweet-keys node.

### 完成条件

- Contacts reach the HID stack with correct coordinates and all three buttons generate events.

### 当前范围

- No FTM5 driver or pinctrl component; the DTS node is disabled.

### 下一步

- Write a board input driver from the pixelios touchpoke/touchprobe code and enable the DTS node.

### 证据

- `source`: [Touch chip, bus, pins, rails and key pins confirmed against vendor sources.](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/05-fact-check.md)
- `device`: [Touch reported working on the iOS 16.7 lock and home screen.](https://github.com/PixOS-Project/pixelios-site/blob/main/docs/STATUS.md)
  Command: <code>fastboot boot shim-boot-avb.img</code>. Revision: `04457e5ddae2164778bd5e75c352a34dac916de9`.

## GPU {#gpu}

`planned`

### 硬件与依赖

- Mali-G78 MP20 at 0x1C500000 size 0x5000, three SPIs \(job 420, mmu 421, gpu 419\).
- Power: PMU G3D 0x17461E00/0x17461E04, CMU\_G3D 0x1C400000, S2MPU windows 0x20080000-0x200B0000.
- Firmware loaded by the shim/kbase; no Apple GPU stack.

### 配置

- gpu node present but status = disabled; no GPU component selected.

### 操作步骤

- Decide between a native Mali component and no GPU, then enable the node only when a driver exists.

### 开发经验

- UniXNU GPU components target Adreno \(Adreno740/AdrenoMetal\) and cannot drive Mali-G78.
- pixelios has substantial GS101 GPU power and job-submission research, but the UI is software-rendered and slow; this is not a working Metal stack.
- The framebuffer path does not depend on the GPU.

### 完成条件

- Either a Mali component renders and presents, or the area stays not-applicable with the software path documented.

### 当前范围

- No Mali driver component; GPU is not part of the first boot milestone.

### 下一步

- Scope a Mali-G78 component or mark the area not-applicable for bring-up.

### 证据

- `source`: [GPU MMIO, interrupts, power domains and clock resources.](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/17-gpu-kernel-gs101.md)

## 网络 {#network}

`planned`

### 硬件与依赖

- Broadcom PCIe Wi-Fi behind the GS101 PCIe controller; firmware and NVRAM from the phone's vendor partition.
- pixelios shim WLAN bring-up: link training, PMU/CMU sequences, firmware container packing.

### 配置

- No wlan node or component selected yet.

### 操作步骤

- Add a wlan node, port the PCIe link and firmware loader, then run the iOS Wi-Fi stack.

### 开发经验

- pixelios implemented PCIe link bring-up and a USB network log path, but Wi-Fi association is still listed as outstanding.
- The WLAN register sequences are captured as data \(soc/google/gs101/wlan\_seq.json\) with per-row citations; they are reusable facts, not a driver.
- GS101 has no UniXNU network component.

### 完成条件

- The interface associates, obtains an address and passes traffic under the target OS.

### 当前范围

- No driver, no firmware hashes, no association evidence.

### 下一步

- Port the PCIe/WLAN sequence into a component and capture firmware inputs.

### 证据

- `source`: [Cited PCIe/PMU/CMU/pin sequences for the GS101 WLAN block.](https://github.com/PixOS-Project/pixelios-kernel/blob/main/soc/google/gs101/wlan_seq.json)

## cellular {#cellular}

`not-applicable`

### 硬件与依赖

- GS101 modem and the Pixel 6a baseband are out of scope for the first UniXNU bring-up.

### 配置

- No modem node and no baseband component is selected.

### 操作步骤

- Revisit only after storage, display, input and network work.

### 开发经验

- pixelios lists the modem as outstanding; no QMI/QRTR or IPA path exists for this board.
- UniXNU has QcomBaseband for Qualcomm platforms; it does not cover the GS101 modem.

### 完成条件

- Not applicable while the modem is outside the port scope.

### 当前范围

- No cellular function; the area is deliberately empty.

### 下一步

- Keep out of scope until the base platform boots.

### 证据

- `source`: [Modem listed as future work.](https://github.com/PixOS-Project/pixelios-kernel/blob/main/ROADMAP.md)

## 音频 {#audio}

`planned`

### 硬件与依赖

- GS101 audio subsystem: ACPM IPC, DSP firmware, S2MPG10/11 PMIC, speaker/headset codec paths.
- pixelios shim ACPM protocol work and DVFS notes.

### 配置

- No audio nodes or components selected.

### 操作步骤

- Describe the DSP/IPC nodes, port the firmware loader, then enable the OS audio stack.

### 开发经验

- pixelios has ACPM host-tested protocol code but no audio playback on the phone; audio remains on the roadmap.
- ACPM is the shared IPC transport for power and audio on GS101, so the power and audio areas share the same firmware interface.

### 完成条件

- The OS audio server starts and produces playback through the speaker or headset.

### 当前范围

- No DSP firmware, codec driver or mixer configuration.

### 下一步

- Port ACPM transport first, then the codec path.

### 证据

- `source`: [Host-tested ACPM IPC implementation and message layout.](https://github.com/PixOS-Project/pixelios-kernel/blob/main/shim/acpm.c)

## 电源 {#power}

`planned`

### 硬件与依赖

- S2MPG10/S2MPG11 PMICs over ACPM Speedy; PMU alive 0x17460000, G3D 0x17461E00.
- pixelios regulator, DVFS and rail sequences, including the GPU rail suspend write.

### 配置

- No PMIC or regulator nodes selected; no XNU PMGR replacement.

### 操作步骤

- Add PMIC/ACPM nodes, implement rail and clock control, then verify idle, suspend and thermal behaviour.

### 开发经验

- GS101 has no Apple PMGR; the ADT reports vmm-present so AMFI does not wait for ApplePMGRNub.
- The GPU rail sequence in pixelios performs a single guarded FUNC\_UPDATE and refuses on unexpected mode or voltage, a pattern to preserve in any driver.
- Charging, battery and thermal ownership are unresolved.

### 完成条件

- Rails and clocks are owned deterministically; the OS boots without a PMGR timeout and can idle.

### 当前范围

- No PMIC driver, no suspend/resume, no thermal policy.

### 下一步

- Port the ACPM/PMIC rail layer and record the first idle-power measurement.

### 证据

- `source`: [ACPM Speedy rail protocol and guarded GPU rail sequence.](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/AUTOMATION.md)

## 镜像组装 {#packaging}

`implemented`

组件: `XnuPrelink`, `DarwinBoot`.

### 硬件与依赖

- Target IPSW and its disk images; the pixelios port used iOS 16.7 \(20H19\).
- Android boot image geometry from the pixelios shim.
- GPT userdata geometry from the phone.

### 配置

- \[userdata\] first\_lba 2290150, last\_lba 31130618, lba\_bytes 4096.
- \[payload\] volume BLUEJAY, 54 MiB \(kernel field, not ramdisk\), loader firmware, dram\_size 0xf0000000, kernel\_args -v serial=3 debug=0x14e keepsyms=1.
- \[bootimg.image\] base 0, kernel\_offset 0x8000, tags\_offset 0x100, pagesize 4096, header\_version 4, kernel\_compression none.

### 操作步骤

- scripts/package.sh --check --os 17
- scripts/package.sh --os 17 --uefi ../uefi-bluejay

### 开发经验

- The payload ADT uses chip id 0x8015, the Apple platform identity pixelios emits, not the GS101 id.
- The pixelios port stores the iOS root in userdata and mounts it read-only; the UniXNU payload must keep the same partition contract.
- No uefi-bluejay checkout exists, so package.yml names a repository placeholder and cannot run yet.

### 完成条件

- A clean checkout produces boot.img, payload.img, kernel.macho and the manifest, and the images boot on the phone.

### 当前范围

- The OS profile is iPadOS 17.7.11, not iOS 16.7; the IPSW pin and SHA-256 members are absent.

### 下一步

- Create uefi-bluejay, then pin the IPSW, its member hashes and the payload runtime values.

### 证据

- `source`: [Android boot image parameters used to load the shim.](https://github.com/PixOS-Project/pixelios-kernel/blob/main/shim/build.sh)

## usb {#usb}

`planned`

### 硬件与依赖

- DWC\_usb31 at 0x11110000 size 0x10000, GSNPSID 0x33313130, global block at +0xC100.
- ABL USB DMA region 0xf8800000 size 0x1000000 with a moving event buffer.

### 配置

- usb node present but disabled; no USB component selected.

### 操作步骤

- Enable the DWC3 node, port the XDCI/device mode path and verify enumeration as a network gadget.

### 开发经验

- pixelios proves USB device mode on this phone: the running iOS appears as an Ethernet gadget and streams the kernel log over UDP.
- The event buffer address changes between boots and must be checked against the 16 MiB ABL region before DMA is enabled.
- UniXNU has QcomDwc3 for Qualcomm; a GS101 variant is not selected.

### 完成条件

- The phone enumerates, a host sees the gadget, and the log transport works.

### 当前范围

- No driver component; USB is not on the first boot path.

### 下一步

- Port the DWC3 device-mode bring-up and reuse the USB log transport.

### 证据

- `source`: [DWC3 identity, base, event buffer behaviour and device-mode evidence.](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/09-xnu-usb-gs101.md)

## 诊断 {#diagnostics}

`planned`

### 硬件与依赖

- pixelios log channels: on-screen console, RAM log, USB serial gadget, USB network log and QR-code log.

### 配置

- kernel\_args include -v, serial=3, debug=0x14e, keepsyms=1.

### 操作步骤

- Bring up one transport at a time, starting with the framebuffer console, then capture a full boot log with the image revision.

### 开发经验

- The QR log channel exists because reading a phone screen by eye is unreliable; its encoder needed SHA3 removal because GS101 lacks those instructions.
- A software-driven test loop \(build, boot, read log, reset\) works without button presses and is the model to keep.

### 完成条件

- A boot log survives a failed boot and identifies the image revision.

### 当前范围

- No log transport is integrated into UniXNU for this board.

### 下一步

- Enable the framebuffer console first, then add USB or QR capture.

### 证据

- `source`: [QR log design, encoder constraints and camera decoder.](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/QR_LOG.md)

</div>
