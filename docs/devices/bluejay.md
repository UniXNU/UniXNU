# Google Pixel 6a \(Tensor G1\)

[tuxmanxd/UniXNU-bluejay](https://github.com/tuxmanxd/UniXNU-bluejay)

<div v-pre>

Google Pixel 6a \(bluejay, Tensor G1\) port scaffold. Hardware values come from the pixelios-kernel research port, which boots XNU 8796 with the iOS 16.7 userland on this phone; this repository restates them in UniXNU format. No UniXNU image has been built or booted for this board yet.

Source record: [porting.toml](https://github.com/tuxmanxd/UniXNU-bluejay/blob/3b0c11f78352d3399d1c603d951a6fcbebca2ab7/porting.toml), `3b0c11f78352d3399d1c603d951a6fcbebca2ab7`.

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
| [cellular](#cellular) | `not-applicable` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `planned` |
| [Image assembly](#packaging) | `implemented` |
| [usb](#usb) | `planned` |
| [Diagnostics](#diagnostics) | `planned` |

## Configuration {#configuration}

`implemented`

Components: `ArmDTPlatform`, `ArmCpu`, `XnuPrelink`, `DarwinBoot`, `GopFramebuffer`.

### Hardware and dependencies

- Google Pixel 6a \(bluejay\), Tensor G1 \(GS101\), 6 GiB DRAM \(2 GiB low bank + 4 GiB high pair, measured\), 128 GiB UFS, 1080x2400 panel.
- pixelios-kernel hardware descriptions: soc/google/gs101/soc.json, device/google/bluejay/board.json, docs/research/05-fact-check.md.

### Configuration

- board.soc\_source = gs101 pins UniXNU-gs101-common; board.os\_profile = ipados-17.7.11-21H461.
- config\_fragments apply in order arch, soc, os; the resolved defconfig bluejay\_defconfig applies last.
- patch\_series is arch, soc, os, device; every series except device is inherited and currently empty for this SoC.

### Procedure

- From a UniXNU checkout: ./unixnu defconfig bluejay\_defconfig -D ../UniXNU-bluejay
- ./unixnu fetch -D ../UniXNU-bluejay; ./unixnu status --json -D ../UniXNU-bluejay
- python3 scripts/porting-record.py check --device ../UniXNU-bluejay

### Development findings

- UniXNU ships only iPadOS 17.7.11, iPadOS 26.5.2, iPadOS 27.0.1 and macOS 27.3 OS profiles. There is no iPhone/iOS 16.7-20H19 profile, so this scaffold selects the oldest shipped profile; a native iPhone profile is required before the result is a real phone port.
- pixelios boots XNU 8796 \(iOS 16 generation\). UniXNU pins a newer XNU and its own ordered patch series, so the pixelios patch stack is not reused as-is.
- The pixelios shim is a bare-metal EL2 loader, not UEFI. Its hardware facts \(UFS cold re-init, HS-G4 link, memory map, device tree\) are reusable; its code is not a UniXNU component.
- The SoC commit pinned in feeds.toml is the first commit of UniXNU-gs101-common and must be replaced with the reviewed published commit.
- The device owns no board driver submodules yet: Gs101Ufs, FTM5 touch and GS101 power are unassigned.

### Completion criteria

- Every source pin resolves; status shows the intended profiles, components and patch order; the porting record check passes.

### Current limits

- No component build has been attempted; UniXNU, uefi-bluejay and a working IPSW profile are missing.

### Next action

- Clone UniXNU beside this repository, run defconfig, fetch and status, and record the resolved output.

### Evidence

- `source`: [Board hardware values \(DRAM banks, framebuffer, userdata geometry, keys, touch\).](https://github.com/PixOS-Project/pixelios-kernel/blob/main/device/google/bluejay/board.json)
- `source`: [SoC register bases, GIC/timer, UFS, USB, UART, WLAN and GPU resources.](https://github.com/PixOS-Project/pixelios-kernel/blob/main/soc/google/gs101/soc.json)

## Firmware and boot {#firmware}

`implemented`

Components: `DarwinBoot`.

### Hardware and dependencies

- tuxmanxd/uefi-bluejay: the Mu-Silicium GS101/Pixel 6a platform \(bluejayPkg + GS101Pkg\), installed with scripts/apply.sh.
- Google Pixel 6a factory image for vendor firmware inputs.
- ABL hands over a linear framebuffer at 0xfac00000 and a live FDT.

### Configuration

- \[firmware\] config = bluejay, dsc = Platforms/Google/bluejayPkg/bluejay.dsc, fd = Build/bluejayPkg/&\#123;target&\#125;\_CLANGPDB/FV/SILICIUM\_UEFI.fd.
- \[firmware.defines\] DEVICE\_MODEL = bluejay. \[bootimg.image\] header\_version 4, kernel\_compression none: ABL rejects a nonzero arm64 text\_offset, so the shim is built with text\_offset 0.
- \[bootimg\] dtb is written by the firmware preflight: a 4 KiB FDT envelope followed by the real payload volume, because the pack stage appends only that file to the kernel field.
- \[payload\] size\_mib 54: the volume carries kernel.macho \(49.5 MiB\) plus the ADT; boot.img is checked against boot\_partition\_bytes 67108864.

### Procedure

- Install uefi-bluejay into a Mu-Silicium checkout with scripts/apply.sh, following https://unixnu.com/porting/uefi-firmware, then build the firmware volume with build\_uefi.py -d bluejay.
- Run scripts/package.sh --check --os 17.
- Boot the artifact with fastboot boot and read the panel.

### Development findings

- The stock bootloader boots Android boot images only, so UniXNU must be packaged as a boot image first \(layer 1\) before the firmware volume is reachable; the pixelios fastboot boot flow proves this path on the phone.
- ABL sets up the panel framebuffer and provides no framebuffer node in its FDT; the address and size are measured \(0xfac00000, 0x9e3400\).
- The phone is read-only toward storage in the pixelios pre-kernel path; any UniXNU firmware must preserve that property until the userdata install is explicit.
- Tensor ABL caps the boot image ramdisk at 32 MiB \(measured 2026-11-15: 4 and 32 MiB boot, 36/40/42/44/46/48/54/56 MiB are refused, header v0 and v4 alike\), while the prelinked kernel alone is 49.5 MiB. The payload therefore travels in the kernel field, which accepts 56 MiB.
- ABL does not parse bytes appended after the FD: a kernel field with 54 MiB of 0xAA after the FD still boots the firmware, so the field can carry the payload volume behind a 4 KiB envelope.

### Completion criteria

- The firmware volume builds, UniXNU.efi runs from it, the menu appears on the panel and the memory map matches the DTS reservations.

### Current limits

- The menu scrolls without input on hardware; the xnu boot entry has not been reached yet. No firmware archive pin and no proprietary file hashes yet.

### Next action

- Boot the kernel-field payload image, confirm that UniXNU finds EFI/UniXNU/unixnu.toml on the payload volume, then fix the menu input/redraw bug.

### Evidence

- `source`: [Boot chain, ABL handoff, framebuffer and boot image parameters.](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/01-boot-path.md)

## CPU and interrupts {#cpu}

`implemented`

Components: `ArmCpu`.

### Hardware and dependencies

- 8 cores: 4x Cortex-A55, 2x Cortex-A76, 2x Cortex-X1.
- GICD 0x10400000 \(64 KiB\), GICR 0x10440000 \(1 MiB, 8 redistributors, stride 0x20000\).
- CNTFRQ 24.576 MHz; virtual timer PPI 11 = INTID 27.

### Configuration

- cpus/timebase-frequency = &lt;24576000&gt;; psci method smc.
- unixnu,cluster-type = E for cpu0-3 and P for cpu4-7 in the board DTS.
- CONFIG\_XNU\_ARMCPU=y and CONFIG\_XNU\_ARM\_DT\_PLATFORM=y.

### Procedure

- Compile dts/bluejay.dts against soc:dts, boot, and read the CPU and interrupt bring-up lines from the kernel log.

### Development findings

- The big cluster mixes A76 and X1 cores; treating cpu4-7 as one P cluster is a scheduling policy choice, not a hardware boundary.
- GICv3 needs both the distributor and all eight redistributor frames; a truncated GICR size leaves secondary CPUs unable to start.
- pixelios boots all 8 CPUs with a custom boot-CPU driver \(XNU patch 0018\), which UniXNU ArmCpu replaces.

### Completion criteria

- All 8 CPUs come online, IPIs work, the timer ticks at 24.576 MHz and secondary CPUs survive idle.

### Current limits

- Not run on hardware in this configuration; cluster mapping has not been validated under UniXNU.

### Next action

- Boot the firmware and kernel and record the CPU startup and timer lines.

### Evidence

- `source`: [GIC and timer values confirmed against the vendor DTS.](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/05-fact-check.md)

## Memory and DMA {#memory}

`implemented`

Components: `ArmDTPlatform`.

### Hardware and dependencies

- DRAM banks measured: 0x80000000 \(2 GiB, carve-outs\), 0x880000000 and 0x900000000 \(2 GiB each, contiguous, no reserved range inside\).
- XNU range: 0x884000000 size 0xf0000000 \(the high pair after the firmware payload window, 3840 MiB, 137.9 MiB under the 0xF89F6000 run measured with the kernel image still held\).
- USB DMA carve-out: 0xf8800000 size 0x1000000 \(ABL, no-map\).

### Configuration

- One memory node for the high range only: reg = &lt;0x8 0x84000000 0x0 0xf0000000&gt;.
- payload.adt.owned\_memory\_size = 0xf0000000; dram\_size = 0xf0000000.
- The first 64 MiB of the high range \(0x880000000\) is the firmware payload window: reserved in the UEFI map, outside XNU's node.
- reserved-memory/framebuffer@fac00000 is no-map.

### Procedure

- Compare the firmware memory map with the DTS, then check that XNU boots with the full 4 GiB and no overlap.

### Development findings

- XNU maps \[kernel, physBase+memSize\) cacheable, so the range must contain no carve-out and its base and size must be multiples of 32 MiB \(16K-granule L2 block\). The high pair, minus the 64 MiB payload window, satisfies both.
- The payload volume travels in the boot image kernel field because Tensor ABL caps the ramdisk at 32 MiB; BootShim copies it to 0x880000000 before the MMU is on, and the firmware maps that window as reserved.
- The low bank cannot be handed over whole: ABL reserves several no-map ranges, including its 16 MiB USB event buffer. Its allocation moves between boots \(0xF8B92000, 0xF8D12000 observed\).
- The 0xfac00000 framebuffer is below the XNU range, so it needs a reservation for firmware/DarwinBoot but does not fragment owned memory.

### Completion criteria

- XNU sees 0xf0000000 bytes of owned memory, boots past pmap setup, and the framebuffer, USB carve-outs and payload window stay untouched.

### Current limits

- The low bank is not adopted; memory outside the window is unavailable to the OS.

### Next action

- Measure the firmware memory map in the UniXNU boot log and confirm the DTS reservations.

### Evidence

- `source`: [DRAM banks, XNU RAM range, framebuffer and USB DMA range with measurement notes.](https://github.com/PixOS-Project/pixelios-kernel/blob/main/device/google/bluejay/board.json)

## Storage and root {#storage}

`planned`

### Hardware and dependencies

- UFS host controller 0x14700000, vendor HCI +0x1100, UNIPRO 0x14780000, PHY/PMA 0x14704000.
- UFS LUN 0 GPT: userdata first 0x22F1E6, last 0x1DC03FA, 4096-byte LBAs.
- Cold re-init after the bootloader shuts the controller down, then HS-G4 link.

### Configuration

- &amp;ufs and &amp;ufsphy status = okay; CONFIG\_XNU\_NATIVE\_UFS=y.
- \[userdata\] first\_lba/last\_lba/lba\_bytes in board.toml.

### Procedure

- Implement a Gs101Ufs component \(or a board driver\) from the pixelios UFS cold-init sequence, then mount the iOS root read-only and verify the GPT geometry.

### Development findings

- The bootloader leaves the UFS controller off; a plain HCI reset is not enough and the pixelios shim reprograms vendor HCI, UNIPRO and the PHY before the link trains.
- The link is switched to HS-G4 \(12x read throughput\); the gear change is part of bring-up, not a later optimisation.
- The root lives in userdata, so the partition geometry is fixed by the phone GPT and is recorded in board.toml.
- No shared UniXNU UFS component supports Exynos/GS101 UFS yet; ShengUfs is Qualcomm-specific and cannot be reused.

### Completion criteria

- The kernel enumerates the UFS LUNs, reads the GPT and mounts the root; a full read of userdata completes without CRC errors.

### Current limits

- No driver code; the pixelios implementation is bare-metal C in the shim, not an XNU kext.

### Next action

- Port shim ufsinit.c to a UniXNU storage component and prove a read-only userdata read.

### Evidence

- `source`: [UFS cold re-init, vendor HCI/UNIPRO/PHY windows and HS-G4 sequence.](https://github.com/PixOS-Project/pixelios-kernel/blob/main/soc/google/gs101/shim/ufsinit.c)

## Display {#display}

`planned`

Components: `GopFramebuffer`.

### Hardware and dependencies

- Framebuffer 0xfac00000, size 0x9e3400, 1080x2400, stride 4320, a8r8g8b8, set up by ABL.
- No framebuffer node in the firmware FDT.

### Configuration

- reserved-memory/framebuffer@fac00000 label cont\_splash\_region, no-map.
- CONFIG\_XNU\_NATIVE\_LEGACY\_DISPLAY=y.

### Procedure

- Describe the scanout buffer as the GOP handoff, boot, and check that the boot logo and the first frames appear.

### Development findings

- ABL programs the panel and leaves a linear buffer; there is no display controller driver in the pixelios pre-kernel path.
- 1080x2400 with a 4320-byte stride is 4 bytes per pixel with no padding beyond the width.
- The pixelios kernel only patches an early framebuffer console \(XNU patch 0003\) and later hands off to a software-rendered UI.

### Completion criteria

- The firmware menu and the XNU boot text render, and the framebuffer is not reclaimed as free memory.

### Current limits

- No panel, backlight or DPU driver; brightness control is absent.

### Next action

- Map the measured buffer into GopFramebuffer and confirm the handoff on hardware.

### Evidence

- `source`: [Framebuffer base, size, width, height and stride.](https://github.com/PixOS-Project/pixelios-kernel/blob/main/device/google/bluejay/board.json)

## Input {#input}

`planned`

### Hardware and dependencies

- STMicro FTM5 touch, chip ID bytes 0x36 0x48, SPI11 / USI11 at 0x10D40000, USI mode register 0x10C2100C, max 10 MHz.
- Pins: gpp23-0..2 SPI function 2, CS gpp23-3, IRQ gpa9-0 \(XEINT\_20\), reset gpp26-0, TS\_SPI\_SEL gpp26-1.
- Power: S2MPG10 LDO25M/LDO26M. Keys: power gpa10, vol+ gpa8, vol- gpa7, all active low.

### Configuration

- DTS touch node with st,max-coords and spi-max-frequency, currently disabled.
- \[adt.buttons\] button-names = hold, voldown, volup.

### Procedure

- Implement the FTM5 SPI driver and pinctrl/rail setup, then verify contacts and the three buttons.

### Development findings

- Touch works on hardware under pixelios \(2026-10-22\): the lock screen and home screen respond, so the wiring and firmware protocol are proven.
- The touch controller is behind USI in SPI mode; the USI mode register must be programmed before the SPI transfers.
- GPIO keys are read directly through the pinctrl banks; uniXNU uses the ADT buttons node instead of the pixelios /sweet-keys node.

### Completion criteria

- Contacts reach the HID stack with correct coordinates and all three buttons generate events.

### Current limits

- No FTM5 driver or pinctrl component; the DTS node is disabled.

### Next action

- Write a board input driver from the pixelios touchpoke/touchprobe code and enable the DTS node.

### Evidence

- `source`: [Touch chip, bus, pins, rails and key pins confirmed against vendor sources.](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/05-fact-check.md)
- `device`: [Touch reported working on the iOS 16.7 lock and home screen.](https://github.com/PixOS-Project/pixelios-site/blob/main/docs/STATUS.md)
  Command: <code>fastboot boot shim-boot-avb.img</code>. Revision: `04457e5ddae2164778bd5e75c352a34dac916de9`.

## GPU {#gpu}

`planned`

### Hardware and dependencies

- Mali-G78 MP20 at 0x1C500000 size 0x5000, three SPIs \(job 420, mmu 421, gpu 419\).
- Power: PMU G3D 0x17461E00/0x17461E04, CMU\_G3D 0x1C400000, S2MPU windows 0x20080000-0x200B0000.
- Firmware loaded by the shim/kbase; no Apple GPU stack.

### Configuration

- gpu node present but status = disabled; no GPU component selected.

### Procedure

- Decide between a native Mali component and no GPU, then enable the node only when a driver exists.

### Development findings

- UniXNU GPU components target Adreno \(Adreno740/AdrenoMetal\) and cannot drive Mali-G78.
- pixelios has substantial GS101 GPU power and job-submission research, but the UI is software-rendered and slow; this is not a working Metal stack.
- The framebuffer path does not depend on the GPU.

### Completion criteria

- Either a Mali component renders and presents, or the area stays not-applicable with the software path documented.

### Current limits

- No Mali driver component; GPU is not part of the first boot milestone.

### Next action

- Scope a Mali-G78 component or mark the area not-applicable for bring-up.

### Evidence

- `source`: [GPU MMIO, interrupts, power domains and clock resources.](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/17-gpu-kernel-gs101.md)

## Network {#network}

`planned`

### Hardware and dependencies

- Broadcom PCIe Wi-Fi behind the GS101 PCIe controller; firmware and NVRAM from the phone's vendor partition.
- pixelios shim WLAN bring-up: link training, PMU/CMU sequences, firmware container packing.

### Configuration

- No wlan node or component selected yet.

### Procedure

- Add a wlan node, port the PCIe link and firmware loader, then run the iOS Wi-Fi stack.

### Development findings

- pixelios implemented PCIe link bring-up and a USB network log path, but Wi-Fi association is still listed as outstanding.
- The WLAN register sequences are captured as data \(soc/google/gs101/wlan\_seq.json\) with per-row citations; they are reusable facts, not a driver.
- GS101 has no UniXNU network component.

### Completion criteria

- The interface associates, obtains an address and passes traffic under the target OS.

### Current limits

- No driver, no firmware hashes, no association evidence.

### Next action

- Port the PCIe/WLAN sequence into a component and capture firmware inputs.

### Evidence

- `source`: [Cited PCIe/PMU/CMU/pin sequences for the GS101 WLAN block.](https://github.com/PixOS-Project/pixelios-kernel/blob/main/soc/google/gs101/wlan_seq.json)

## cellular {#cellular}

`not-applicable`

### Hardware and dependencies

- GS101 modem and the Pixel 6a baseband are out of scope for the first UniXNU bring-up.

### Configuration

- No modem node and no baseband component is selected.

### Procedure

- Revisit only after storage, display, input and network work.

### Development findings

- pixelios lists the modem as outstanding; no QMI/QRTR or IPA path exists for this board.
- UniXNU has QcomBaseband for Qualcomm platforms; it does not cover the GS101 modem.

### Completion criteria

- Not applicable while the modem is outside the port scope.

### Current limits

- No cellular function; the area is deliberately empty.

### Next action

- Keep out of scope until the base platform boots.

### Evidence

- `source`: [Modem listed as future work.](https://github.com/PixOS-Project/pixelios-kernel/blob/main/ROADMAP.md)

## Audio {#audio}

`planned`

### Hardware and dependencies

- GS101 audio subsystem: ACPM IPC, DSP firmware, S2MPG10/11 PMIC, speaker/headset codec paths.
- pixelios shim ACPM protocol work and DVFS notes.

### Configuration

- No audio nodes or components selected.

### Procedure

- Describe the DSP/IPC nodes, port the firmware loader, then enable the OS audio stack.

### Development findings

- pixelios has ACPM host-tested protocol code but no audio playback on the phone; audio remains on the roadmap.
- ACPM is the shared IPC transport for power and audio on GS101, so the power and audio areas share the same firmware interface.

### Completion criteria

- The OS audio server starts and produces playback through the speaker or headset.

### Current limits

- No DSP firmware, codec driver or mixer configuration.

### Next action

- Port ACPM transport first, then the codec path.

### Evidence

- `source`: [Host-tested ACPM IPC implementation and message layout.](https://github.com/PixOS-Project/pixelios-kernel/blob/main/shim/acpm.c)

## Power {#power}

`planned`

### Hardware and dependencies

- S2MPG10/S2MPG11 PMICs over ACPM Speedy; PMU alive 0x17460000, G3D 0x17461E00.
- pixelios regulator, DVFS and rail sequences, including the GPU rail suspend write.

### Configuration

- No PMIC or regulator nodes selected; no XNU PMGR replacement.

### Procedure

- Add PMIC/ACPM nodes, implement rail and clock control, then verify idle, suspend and thermal behaviour.

### Development findings

- GS101 has no Apple PMGR; the ADT reports vmm-present so AMFI does not wait for ApplePMGRNub.
- The GPU rail sequence in pixelios performs a single guarded FUNC\_UPDATE and refuses on unexpected mode or voltage, a pattern to preserve in any driver.
- Charging, battery and thermal ownership are unresolved.

### Completion criteria

- Rails and clocks are owned deterministically; the OS boots without a PMGR timeout and can idle.

### Current limits

- No PMIC driver, no suspend/resume, no thermal policy.

### Next action

- Port the ACPM/PMIC rail layer and record the first idle-power measurement.

### Evidence

- `source`: [ACPM Speedy rail protocol and guarded GPU rail sequence.](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/AUTOMATION.md)

## Image assembly {#packaging}

`implemented`

Components: `XnuPrelink`, `DarwinBoot`.

### Hardware and dependencies

- Target IPSW and its disk images; the pixelios port used iOS 16.7 \(20H19\).
- Android boot image geometry from the pixelios shim.
- GPT userdata geometry from the phone.

### Configuration

- \[userdata\] first\_lba 2290150, last\_lba 31130618, lba\_bytes 4096.
- \[payload\] volume BLUEJAY, 54 MiB \(kernel field, not ramdisk\), loader firmware, dram\_size 0xf0000000, kernel\_args -v serial=3 debug=0x14e keepsyms=1.
- \[bootimg.image\] base 0, kernel\_offset 0x8000, tags\_offset 0x100, pagesize 4096, header\_version 4, kernel\_compression none.

### Procedure

- scripts/package.sh --check --os 17
- scripts/package.sh --os 17 --uefi ../uefi-bluejay

### Development findings

- The payload ADT uses chip id 0x8015, the Apple platform identity pixelios emits, not the GS101 id.
- The pixelios port stores the iOS root in userdata and mounts it read-only; the UniXNU payload must keep the same partition contract.
- No uefi-bluejay checkout exists, so package.yml names a repository placeholder and cannot run yet.

### Completion criteria

- A clean checkout produces boot.img, payload.img, kernel.macho and the manifest, and the images boot on the phone.

### Current limits

- The OS profile is iPadOS 17.7.11, not iOS 16.7; the IPSW pin and SHA-256 members are absent.

### Next action

- Create uefi-bluejay, then pin the IPSW, its member hashes and the payload runtime values.

### Evidence

- `source`: [Android boot image parameters used to load the shim.](https://github.com/PixOS-Project/pixelios-kernel/blob/main/shim/build.sh)

## usb {#usb}

`planned`

### Hardware and dependencies

- DWC\_usb31 at 0x11110000 size 0x10000, GSNPSID 0x33313130, global block at +0xC100.
- ABL USB DMA region 0xf8800000 size 0x1000000 with a moving event buffer.

### Configuration

- usb node present but disabled; no USB component selected.

### Procedure

- Enable the DWC3 node, port the XDCI/device mode path and verify enumeration as a network gadget.

### Development findings

- pixelios proves USB device mode on this phone: the running iOS appears as an Ethernet gadget and streams the kernel log over UDP.
- The event buffer address changes between boots and must be checked against the 16 MiB ABL region before DMA is enabled.
- UniXNU has QcomDwc3 for Qualcomm; a GS101 variant is not selected.

### Completion criteria

- The phone enumerates, a host sees the gadget, and the log transport works.

### Current limits

- No driver component; USB is not on the first boot path.

### Next action

- Port the DWC3 device-mode bring-up and reuse the USB log transport.

### Evidence

- `source`: [DWC3 identity, base, event buffer behaviour and device-mode evidence.](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/09-xnu-usb-gs101.md)

## Diagnostics {#diagnostics}

`planned`

### Hardware and dependencies

- pixelios log channels: on-screen console, RAM log, USB serial gadget, USB network log and QR-code log.

### Configuration

- kernel\_args include -v, serial=3, debug=0x14e, keepsyms=1.

### Procedure

- Bring up one transport at a time, starting with the framebuffer console, then capture a full boot log with the image revision.

### Development findings

- The QR log channel exists because reading a phone screen by eye is unreliable; its encoder needed SHA3 removal because GS101 lacks those instructions.
- A software-driven test loop \(build, boot, read log, reset\) works without button presses and is the model to keep.

### Completion criteria

- A boot log survives a failed boot and identifies the image revision.

### Current limits

- No log transport is integrated into UniXNU for this board.

### Next action

- Enable the framebuffer console first, then add USB or QR capture.

### Evidence

- `source`: [QR log design, encoder constraints and camera decoder.](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/QR_LOG.md)

</div>
