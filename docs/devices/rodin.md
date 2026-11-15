# Redmi Turbo 4 / POCO X7 Pro \(rodin\): Dimensity 8400-Ultra, 8/12/16 GiB LPDDR5X, 6.67" AMOLED 1220x2712, UFS

[dianjianhang/UniXNU-rodin](https://github.com/dianjianhang/UniXNU-rodin)

<div v-pre>

Redmi Turbo 4 / POCO X7 Pro \(rodin\): MediaTek Dimensity 8400-Ultra \(MT6899, 8x Cortex-A725 arm64\), 12 GiB LPDDR5X, UFS storage. Porting target: UniXNU UEFI + XNU boot chain for the ipados-17.7.11-21H461 profile; configuration chain and UEFI scaffold are in place, drivers are in progress.

Source record: [porting.toml](https://github.com/dianjianhang/UniXNU-rodin/blob/1269114a246fc2ab8fd6871d2c910c64939880c4/porting.toml), `1269114a246fc2ab8fd6871d2c910c64939880c4`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `implemented` |
| [Firmware and boot](#firmware) | `planned` |
| [CPU and interrupts](#cpu) | `implemented` |
| [Memory and DMA](#memory) | `planned` |
| [Storage and root](#storage) | `planned` |
| [Display](#display) | `planned` |
| [Input](#input) | `implemented` |
| [GPU](#gpu) | `planned` |
| [Network](#network) | `planned` |
| [cellular](#cellular) | `planned` |
| [Audio](#audio) | `implemented` |
| [Power](#power) | `planned` |
| [Image assembly](#packaging) | `planned` |
| [Diagnostics](#diagnostics) | `planned` |

## Configuration {#configuration}

`implemented`

Components: `ArmDTPlatform`, `ArmCpu`, `XnuPrelink`, `SoftwareAES`.

### Hardware and dependencies

- UniXNU-mt6899-common SoC repository \(created, values unreviewed\)
- OS profile selected: ipados-17.7.11-21H461 \(arm64, iPad7,1 identity; profile supplies \[ipsw\] and \[kernel.prelink\]\)
- Kernel sources: MiCode/Xiaomi\_Kernel\_OpenSource bsp-rodin-v-oss @ 2cd69ee4193920840ee3c837384716a66b1faecd; MiCode/MTK\_kernel\_device\_modules bsp-rodin-v-oss @ bc2dfc01f75b5fbc42d614c8c39700022cba9323 \(board DTS\)

### Configuration

- board.toml \[board\] os\_profile = ipados-17.7.11-21H461; \[ipsw\] and \[kernel.prelink\] inherited from the profile

### Procedure

- Choose the OS profile from UniXNU/profiles/os/
- Pin UniXNU-mt6899-common with a reviewed commit in feeds.toml
- Run ./unixnu defconfig, fetch, status --json, tree
- Verify the resolver chain on CI \(defconfig/fetch/status all passing\)

### Development findings

- Scaffold created 2026-11-15; SoC pin da0f6103bd3529a78c4ce1a2818190a07a6734c1 now resolved in feeds.toml.
- Board DTS sources identified in MTK\_kernel\_device\_modules: arch/arm64/boot/dts/mediatek/rodin.dts and companions.
- Resolver chain verified 2026-11-15: defconfig/fetch/status/tree exit 0 on Linux \(aarch64 host, CI pending toolchain\).

### Completion criteria

- Resolved profiles and patch order confirmed by ./unixnu status --json

### Current limits

- Toolchain build still running on CI; kernel/tree steps not yet end-to-end verified there.

### Next action

- Finish the cached UniXNU toolchain CI run, then verify build kernel and tree on the same host.

### Evidence

- `source`: [mt6899 pinned to UniXNU-mt6899-common da0f6103bd3529a78c4ce1a2818190a07a6734c1](https://github.com/dianjianhang/UniXNU-rodin/blob/1269114a246fc2ab8fd6871d2c910c64939880c4/feeds.toml)

## Firmware and boot {#firmware}

`planned`

### Hardware and dependencies

- Stock boot.img and vendor\_boot.img \(header v4\) dumped from the device
- Mu-Silicium fork target for rodin \(uefi-rodin\), not created yet

### Configuration

- board.toml \[bootimg.image\]: base=0x40000000, pagesize=4096, header\_version=4

### Procedure

- Create uefi-rodin from uefi-sheng / Mu-Silicium
- Describe the MTK boot chain handoff and PSCI method

### Development findings

- Stock images use Android boot image header version 4; kernel loads at 0x40000000, ramdisk at 0x66f00000, page size 4096.
- Vendor ramdisk is \~41 MiB and lives in vendor\_boot; boot.img carries only the kernel \(\~16.6 MiB\).
- The vendor DTB \(\~444 KiB, FDT v17\) sits inside vendor\_boot.img at 0x2965040, after the vendor ramdisk.
- Vendor bootargs: console=tty0, androidboot.hardware=mt6899, vmalloc=400M, swiotlb=noforce.

### Completion criteria

- Firmware builds and the stock bootloader jumps to BootShim

### Current limits

- UEFI firmware for rodin does not exist; the bootimg v4 tool support is unverified.

### Next action

- Survey the Mu-Silicium base for an MTK reference and map the vendor DTB into the UEFI device-tree flow.

### Evidence

- `source`: [Boot headers parsed and one FDT blob extracted; hashes pinned in proprietary-files.txt](https://github.com/dianjianhang/UniXNU-rodin/blob/1269114a246fc2ab8fd6871d2c910c64939880c4/docs/hardware-notes.md)

## CPU and interrupts {#cpu}

`implemented`

Components: `ArmCpu`.

### Hardware and dependencies

- Vendor DTB extracted from the stock vendor\_boot.img \(rodin-vendor.dtb\)

### Configuration

- mt6899.dtsi: GIC v3 at 0xc400000 \(dist 0x40000, redist 0xc440000/0x200000\), 4 cells
- mt6899.dtsi: armv8 timer, 13 MHz, vendor interrupt cells
- rodin.dts: MPIDR 0x000-0x700, capacities 0x400/0x3bb/0x3cb

### Procedure

- Extract the vendor DTB from vendor\_boot.img and decompile it with dtc
- Copy confirmed GIC, timer and CPU topology values into mt6899.dtsi

### Development findings

- 8x Cortex-A725 with enable-method psci; vendor DTB groups cpu0-3, cpu4-6 and cpu7 into three cpufreq domains.
- Timer clock is 13 MHz \(0xc65d40\) as declared by the vendor DTB.
- PSCI 1.0 with method smc, matching psci\_method = "smc" in board.toml.

### Completion criteria

- All cores enumerate in the kernel with the correct timer rate

### Current limits

- Values are read from the blob but not yet verified on hardware.
- Idle states and full CPU bindings not yet translated.

### Next action

- Verify GIC/timer behavior during the first UEFI bring-up, then translate idle states.

### Evidence

- `source`: [Vendor DTB values transcribed into UniXNU-mt6899-common/dts/mt6899.dtsi and dts/rodin.dts](https://github.com/dianjianhang/UniXNU-rodin/blob/1269114a246fc2ab8fd6871d2c910c64939880c4/docs/hardware-notes.md)

## Memory and DMA {#memory}

`planned`

Components: `ArmDTPlatform`.

### Hardware and dependencies

- Installed RAM confirmed: 12 GiB \(test device is the 12+256 variant\)

### Configuration

- board.toml \[payload\] dram\_size = "0x300000000" \(12 GiB\)

### Procedure

- Record DRAM size, reservations and DMA policy

### Development findings

- Test device: 12 GiB LPDDR5X + 256 GiB UFS.
- Vendor DTB declares only a 1 GiB window at 0x40000000; the 12 GiB map spans 0x40000000..0x340000000 and must be confirmed against the bootloader memory map.
- Reserved regions use MTK-specific "mediatek,reserved" nodes and need mapping to UniXNU reservations.

### Completion criteria

- Kernel maps full DRAM with required reservations

### Current limits

- Only the 1 GiB DTB window is known; the extended memory map is unconfirmed.

### Next action

- Survey the bootloader DRAM report and MTK DRAMC setup, then extend the memory description.

### Evidence

Collect evidence using the next action.

## Storage and root {#storage}

`planned`

### Hardware and dependencies

- Device GPT dump \(userdata first/last LBA\); UFS host and PHY details from vendor DTS

### Configuration

- board.toml \[userdata\]: first\_lba=0x354300, last\_lba=0x3d937f7, lba\_bytes=4096 \(from /dev/block/sdc GPT dump\)

### Procedure

- Adapt UFS storage per /porting/ufs; fill \[userdata\] in board.toml

### Development findings

- GPT parsed from /dev/block/sdc: 4096-byte logical blocks, disk 246.32 GiB, 'userdata' at LBA 0x354300..0x3d937f7 \(\~233 GiB\).
- Full partition table recorded in docs/hardware-notes.md; MTK A/B scheme with boot\_a/boot\_b, lk\_a/lk\_b \(LittleKernel\), super \(11 GiB dynamic\).

### Completion criteria

- APFS root and Data volumes mount from the device UFS

### Current limits

- UFS host/PHY adaptation not started; no UniXNU UFS component selected yet.

### Next action

- Select a UFS component from the catalog and map the MTK UFS host controller \(from mt6899.dts / vendor sources\) onto it.

### Evidence

- `source`: [userdata first\_lba/last\_lba/lba\_bytes filled into board.toml from the parsed GPT](https://github.com/dianjianhang/UniXNU-rodin/blob/1269114a246fc2ab8fd6871d2c910c64939880c4/docs/hardware-notes.md)

## Display {#display}

`planned`

Components: `GopFramebuffer`.

### Hardware and dependencies

- Panel driver and DSI configuration from the rodin kernel sources

### Configuration

- board.toml \[components\]: GopFramebuffer supplies the display component; panel timing from vendor DTS \(resolution 1220x2712 AMOLED\)

### Procedure

- Follow /porting/display: controller/GOP, panel, stride, backlight

### Development findings

- Panel: 6.67" AMOLED, 1220x2712, up to 120 Hz \(vendor specs\).
- DSI controller: mediatek,mt6899-dsi \(disp1\_dsi0\) with mmsys0/1 and GCE disp events, read from the vendor DTB.
- Panel variants referenced in the touch node: rodin\_42\_02\_0a\_dsc\_vdo and rodin\_36\_02\_0b\_dsc\_vdo \(DSC VDO\).
- DTBO overlay confirms the two panel drivers: o10\_42\_02\_0a\_dsc\_vdo,lcm \(panel1@0\) and o10\_36\_02\_0b\_dsc\_vdo,lcm \(panel2@1\) — dual-source panel strategy.

### Completion criteria

- Framebuffer visible at every boot stage with working brightness

### Current limits

- Panel driver sources live in MTK\_kernel\_modules \(LCM driver table\); not yet read.

### Next action

- Read the rodin LCM drivers in MTK\_kernel\_modules for the two panel variants, then design the display adaptation.

### Evidence

Collect evidence using the next action.

## Input {#input}

`implemented`

### Hardware and dependencies

- Board DTS source: MTK\_kernel\_device\_modules bsp-rodin-v-oss, arch/arm64/boot/dts/mediatek/xiaomi\_rodin\_mt6899\_touch.dtsi

### Configuration

- Touch IC: Goodix GT9916R \(gtp\), fallback Focaltech 3683g
- Bus: SPI1 @ 15 MHz; CLK GPIO50, CSB GPIO51, MISO GPIO52, MOSI GPIO53; SCP SPI2 alternate mode
- IRQ GPIO9, reset GPIO134, AVDD GPIO73 from mt6368\_vtp \(1.8 V\)

### Procedure

- Follow /porting/input: bus, sensor protocol, interrupts, contact IDs

### Development findings

- Touch driver is not in the vendor DTB blob but in module sources: xiaomi,touch-spi on spi1, coordinates 1220x2712 \(panel-max-x 121999, super-resolution factor 100\).
- Panels referenced by the touch node: rodin\_42\_02\_0a\_dsc\_vdo and rodin\_36\_02\_0b\_dsc\_vdo.

### Completion criteria

- Touch, buttons and volume keys work

### Current limits

- Goodix GT9916R SPI protocol needs driver work; no UniXNU touch component exists for this IC yet.

### Next action

- Read the Goodix SPI driver in MTK\_kernel\_modules \(drivers/input/touchscreen/...\) and design the UEFI/XNU touch adaptation.

### Evidence

- `source`: [Touch IC, bus, GPIO wiring and firmware names recorded](https://github.com/dianjianhang/UniXNU-rodin/blob/1269114a246fc2ab8fd6871d2c910c64939880c4/docs/hardware-notes.md)

## GPU {#gpu}

`planned`

### Hardware and dependencies

- Mali-G720 driver design; no Mali driver exists in the UniXNU catalog

### Configuration

- board.toml \[components\]: input covered by the catalog HID components once selected

### Procedure

- Survey ArmMali userspace/kernelspace sources; define the smallest hardware-verifiable step

### Development findings

- UniXNU GPU components \(Adreno740, AdrenoMetal\) target Qualcomm Adreno; Mali-G720 requires a new driver from zero.
- Vendor DTB: mali@13000000, compatible "mediatek,mali", "arm,mali-valhall" — Valhall CSF architecture confirmed.

### Completion criteria

- Console-class rendering first; Metal acceleration later

### Current limits

- No existing implementation to reuse; long lead time expected.

### Next action

- Write a driver plan against the Mali CSF architecture and decide the first verifiable milestone.

### Evidence

Collect evidence using the next action.

## Network {#network}

`planned`

### Hardware and dependencies

- connsys\_wifi.img \(MT7902 Wi-Fi firmware, dumped, hash pinned\)
- connsys\_bt.img \(MT7902 BT firmware, dumped, hash pinned\)

### Configuration

- Adreno 740 \(MT6899 iGPU\); GopFramebuffer is the display component in board.toml \[components\]

### Procedure

- Follow /porting/network and /porting/bluetooth

### Development findings

- Chip confirmed as MT7902: gen4-mt79xx WLAN driver in MTK\_kernel\_modules bsp-rodin-v-oss \(connectivity/wlan/core/gen4-mt79xx/chips/mt7902\); BT over SDIO ID 0x790A, firmware BT\_RAM\_CODE\_MT7902\_1\_1\_hdr.bin.
- Vendor DTB: wifi@18000000, compatible "mediatek,wifi", emi-connac-ver 2 — Connac gen2 class silicon.
- Community mt76 porting for MT7902 exists \(built on this BSP\) and can inform a UniXNU adaptation.

### Completion criteria

- Association and packet transfer

### Current limits

- No UniXNU Wi-Fi component for MT7902; firmware package must be extracted from the vendor image.

### Next action

- Extract the MT7902 firmware blobs from the rodin vendor image and review the gen4-mt79xx driver interfaces.

### Evidence

Collect evidence using the next action.

## cellular {#cellular}

`planned`

### Hardware and dependencies

- Scope decision: modem bring-up is a large separate effort

### Configuration

- No network component selected yet; MTK connectivity handled via cellular/baseband scope

### Procedure

- Survey the vendor sources and map hardware onto a catalog component

### Development findings

- Area not yet surveyed in depth

### Completion criteria

- Component works on the device

### Current limits

- Integrated MT6899 modem; no plan yet.

### Next action

- Decide whether cellular is in scope; otherwise mark not-applicable with a reason.

### Evidence

Collect evidence using the next action.

## Audio {#audio}

`implemented`

### Hardware and dependencies

- DTBO overlay: 2x awinic,aw882xx\_smartpa on I2C 0x34/0x35
- MTK\_kernel\_modules bsp-rodin-v-oss sound/ drivers for the DSP and routes

### Configuration

- No baseband component selected yet; vendor modem userspace remains required

### Procedure

- Follow /porting/power

### Development findings

- SmartPA: 2x AW882XX \(stereo speakers\) on I2C addresses 0x34 and 0x35.
- Notification/RGB LED: AW21024 on I2C 0x30 \(power/driver ownership overlap\).

### Completion criteria

- Playback and capture

### Current limits

- Audio DSP \(audio\_dsp.img firmware present\) not yet surveyed.

### Next action

- Map the audio DSP service model from the module sources and audio\_dsp.img.

### Evidence

- `source`: [SmartPA addresses and LED controller read from dtbo.img](https://github.com/dianjianhang/UniXNU-rodin/blob/1269114a246fc2ab8fd6871d2c910c64939880c4/docs/hardware-notes.md)

## Power {#power}

`planned`

### Hardware and dependencies

- Regulators, battery units, firmware ownership from vendor DTS

### Configuration

- No audio component selected yet

### Procedure

- Follow /porting/power

### Development findings

- Area not yet surveyed in depth

### Completion criteria

- Battery reporting and supported transitions

### Current limits

- No plan yet.

### Next action

- Record the power tree from the vendor DTS.

### Evidence

Collect evidence using the next action.

## Image assembly {#packaging}

`planned`

### Hardware and dependencies

- Original kernelcache, IPSW, firmware inputs

### Configuration

- board.toml carries no power section yet; PSCI method smc recorded for handoff

### Procedure

- Complete \[kernel.prelink\], \[ipsw\], \[payload\] in board.toml; implement scripts/package.sh

### Development findings

- Area not yet surveyed in depth

### Completion criteria

- ./unixnu bootimg produces a flashable image from a clean checkout

### Current limits

- All REQUIRED\_ placeholders unfilled.

### Next action

- Supply the IPSW and kernelcache inputs and run the first ./unixnu build kernel attempt.

### Evidence

Collect evidence using the next action.

## Diagnostics {#diagnostics}

`planned`

### Hardware and dependencies

- UART/USB console access plan

### Configuration

- boot image header v4: kernel 0x40000000, ramdisk 0x66f00000, pagesize 4096 \(from stock boot/vendor\_boot\)

### Procedure

- Set up log capture per /porting/log-capture

### Development findings

- Area not yet surveyed in depth

### Completion criteria

- Boot logs captured from the first UEFI stage

### Current limits

- Console method untested on rodin.

### Next action

- Confirm the debug UART pinout for rodin and wire the log capture procedure.

### Evidence

Collect evidence using the next action.

</div>
