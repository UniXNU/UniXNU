# Lenovo Xiaoxin Pad 12.1 \(2025\), Lenovo TB365FC \(board cava\_prc\_consumer\_wifi\)

[LittleStar-OuO/UniXNU-tb365fc](https://github.com/LittleStar-OuO/UniXNU-tb365fc)

<div v-pre>

Lenovo Xiaoxin Pad 12.1 \(2025\), Lenovo TB365FC, board cava\_prc\_consumer\_wifi. The stock ZUXOS 1.1.10.122 package is unpacked and the unit itself has been inventoried over rooted adb \(8 GB DRAM, 128 GB UFS, BOE HX83122B 1600x2560 @90 Hz, MT6631 combo\). The UEFI firmware from uefi-tb365fc boots on the unit and shows the UniXNU menu with the Advanced Logger viewer; no XNU image has been built or booted yet.

源记录: [porting.toml](https://github.com/LittleStar-OuO/UniXNU-tb365fc/blob/b13016b5088c91819dd4350f733a938e109723ad/porting.toml), `b13016b5088c91819dd4350f733a938e109723ad`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `implemented` |
| [固件与启动](#firmware) | `implemented` |
| [CPU 与中断](#cpu) | `planned` |
| [内存与 DMA](#memory) | `planned` |
| [存储与根卷](#storage) | `planned` |
| [显示](#display) | `implemented` |
| [输入](#input) | `implemented` |
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

- MT6835 platform identity, Lenovo TB365FC \(cava\_prc\_consumer\_wifi\) board identity, iPad7,1 / iPadOS 17.7.11 build 21H461 target identity and the TB365FC bootstrap defconfig.
- Stock package ZUXOS 1.1.10.122 \(Android 15, build TB365FC\_CN\_OPEN\_USER\_M1317.3\_V\_ZUXOS\_1.1.10.122\_ST\_250828\), hashed in proprietary-files.txt.

### 配置

- board.soc = MT6835; board.soc\_source = mt6835; board.os\_profile = ipados-17.7.11-21H461; schema\_version = 2.
- tb365fc\_defconfig enables the shared ARM DT platform, ARMCPU, architected timer, panic and prelinked crypto paths.
- feeds.toml pins the published UniXNU-mt6835-common commit; the workstation override lives in the git-ignored local.toml.

### 操作步骤

- Run ./unixnu defconfig tb365fc\_defconfig -D ../UniXNU-tb365fc from a UniXNU checkout.
- Run ./unixnu status --json -D ../UniXNU-tb365fc and inspect the effective SoC layer and source pins.

### 开发经验

- The device identifies as MT6835 with stock board name cava\_prc\_consumer\_wifi, Android 15, build TB365FC\_CN\_OPEN\_USER\_M1317.3\_V\_ZUXOS\_1.1.10.122\_ST\_250828.
- The stock SP Flash Tool package provides boot, init\_boot, vendor\_boot, dtbo, lk and preloader images; their hashes and the values derived from them are recorded across the firmware, cpu, memory, storage, display, input, gpu, network, audio, power and packaging areas.
- No public Lenovo kernel source or DTS for this board was found; every hardware value so far comes from the stock firmware and the live device inventory.
- The unit reports ro.product.device TB365FC, ro.product.name TB365FC\_PRC, ro.board.platform mt6835 and ro.boot.hardware mt8755 on Android 15 build AP3A.240905.015.A2/250828\_122 \(kernel 5.15.170\), with ro.boot.verifiedbootstate orange and ro.boot.flash.locked 0.

### 完成条件

- Source pins resolve, the effective configuration contains the intended TB365FC overrides and every selected component has an owning area.

### 当前范围

- The APFS Data volume UUID and the unique chip ID are payload inputs and still unmeasured; the panel variant, the self-built boot image and the FD base are settled on hardware \(see firmware and display\). example stays true until the payload inputs are measured.

### 下一步

- Measure the APFS Data volume UUID and the unique chip ID once XNU is installed, then clear example = true.

### 证据

- `device`: [Collected the redacted identity and hardware inventory that the areas below now cite.](https://github.com/LittleStar-OuO/UniXNU-tb365fc/blob/b13016b5088c91819dd4350f733a938e109723ad/tools/collect-device-info.sh)
  Command: <code>tools/collect-device-info.sh</code>. Revision: `5ba47e6284567baa3450f9d82b5d56963cd14035`.

## 固件与启动 {#firmware}

`implemented`

### 硬件与依赖

- Stock TB365FC firmware package \(Android 15, build TB365FC\_CN\_OPEN\_USER\_M1317.3\_V\_ZUXOS\_1.1.10.122\_ST\_250828\), unlocked bootloader state, fastboot mode, the stock boot/vendor\_boot/dtbo partitions and the UEFI firmware from uefi-tb365fc.
- Measured boot geometry: boot.img header v4 \(4096-byte pages\); vendor\_boot header v4 with kernel\_addr 0x40000000, ramdisk\_addr 0x66F00000, tags\_addr/dtb\_addr 0x47C80000 and cmdline "bootopt=64S3,32N2,64N2".

### 配置

- Plan A implemented: the FD is packed as the gzip kernel of an Android boot v4 image, LK decompresses it to kernel\_addr 0x40000000 and jumps into the SEC entry; no shim is needed.
- Resources/Configs/tb365fc.toml keeps header\_version = 4, the FD window 0x40000000/0x400000 and the 1 MiB FAT12 UNIXNU ramdisk; the stock init\_boot and vendor\_boot ramdisks and DTB stay in place.
- Firmware paths in board.toml \[firmware\] point at Platforms/Lenovo/tb365fcPkg; the five Mu base-core fixes are applied from uefi-tb365fc Resources/MuPatches at build time over the upstream Mu\_Basecore pin.

### 操作步骤

- Extract the stock boot, vendor\_boot and dtbo partitions and read them with tools/unpack\_boot\_image.py and tools/extract\_fdt.py.
- Build the UEFI FD, flash the boot image, and record the first screen, last confirmed stage and log source.

### 开发经验

- init\_boot.img is header v4 with a 2,066,170-byte ramdisk; vendor\_boot.img is header v4 with vendor\_ramdisk\_size 27,731,435 and dtb\_size 190,500.
- dtbo.img holds one 240,233-byte DTBO with 208 fragments; the vendor\_boot DTB is the MT6835 base tree \(model "MT6835"\) and the overlay targets use unresolved 0xffffffff phandles until LK merges them.
- lk.img \(2,897,568 bytes\) carries kernel\_load\_addr and dtb\_addr as runtime variables rather than text-form constants; the few 32-bit words equal to 0x40080000 have no established role, so the FD base stays the Plan A convention proven on merlinx and camellia until a hardware log confirms it.
- The stock boot images are padded to their partition sizes \(boot and vendor\_boot 64 MiB, init\_boot and dtbo 8 MiB\); the hashes in proprietary-files.txt cover the padded files.
- On the tablet the boot, vendor\_boot and dtbo images match the pinned stock hashes, and /proc/iomem reserves the header addresses: dtb at 0x47c80000 and the ramdisk at 0x66f00000-0x68be2fff.
- init\_boot\_a does not match the pinned stock hash: the unit runs SukiSU Ultra in LKM mode \(a kernelsu module is loaded and the stock kernel carries no KernelSU strings\), so the pin still describes the package, not this unit's rooted boot partition.
- The stock cmdline carries fastboot\_enable=1 and bootopt=64S3,32N2,64N2; neither demonstrates fastboot boot support.
- The first bring-up image booted on the unit: LK accepted the self-built v4 image, SEC cleared the LK scanout, the Project Silicium logo appeared and the UniXNU menu followed at 1600x2560; the 1.7 MiB image is far below the 64 MiB boot\_a limit.
- The FD base is 0x40000000 \(the stock vendor\_boot kernel\_addr\), not the earlier 0x40080000 plan; the primary stack sits at 0x40400000 and the LK reservations \(DTB 0x47C80000, ramdisk 0x66F00000\) survive the handoff.
- In the booted firmware Volume Up/Down move the menu selection, Power and Enter activate entries, and Tools opens the Advanced Logger viewer with QR pages, five speed gears and Power/Enter to exit.

### 完成条件

- Firmware image builds, enters UniXNU, publishes the framebuffer and preserves the documented memory reservations.

### 当前范围

- The XNU/DarwinBoot handoff and the ADT payload are not implemented; the image was flashed to this unit's boot\_a only, boot\_b stays stock as the recovery path.

### 下一步

- Build the XNU payload and boot image, then record the DarwinBoot handoff and the first XNU checkpoint.

### 证据

- `source`: [SHA-256 pins for the stock boot, init\_boot, vendor\_boot, dtbo, lk and preloader images this area derives its geometry from.](https://github.com/LittleStar-OuO/UniXNU-tb365fc/blob/b13016b5088c91819dd4350f733a938e109723ad/proprietary-files.txt)
- `source`: [Parsed the stock boot, init\_boot and vendor\_boot headers; produced the header versions, sizes and load addresses recorded above.](https://github.com/LittleStar-OuO/UniXNU-tb365fc/blob/b13016b5088c91819dd4350f733a938e109723ad/tools/unpack_boot_image.py)
- `device`: [boot\_a, vendor\_boot\_a and dtbo\_a match the pins; init\_boot\_a differs because of the SukiSU LKM patch.](https://github.com/LittleStar-OuO/UniXNU-tb365fc/blob/b13016b5088c91819dd4350f733a938e109723ad/proprietary-files.txt)
  Command: <code>sha256sum stock/boot_a.img stock/vendor_boot_a.img stock/dtbo_a.img stock/init_boot_a.img</code>. Revision: `5ba47e6284567baa3450f9d82b5d56963cd14035`.
- `source`: [The bootable firmware sources: v4 boot path, MuPatches applied over the upstream Mu\_Basecore pin, FD window and panel settings described in the README.](https://github.com/LittleStar-OuO/uefi-tb365fc/commit/7cf23b62ad34ab4c71b502299fc049fb8af6786e)

## CPU 与中断 {#cpu}

`planned`

### 硬件与依赖

- Measured from the stock vendor\_boot DTB: 6x Cortex-A55 at MPIDR affinities 0x0-0x500, 2x Cortex-A76 at 0x600-0x700, GIC distributor 0x0C000000 \(256 KiB\), redistributors 0x0C040000 \(2 MiB\) and a 13 MHz architected timer.

### 配置

- CONFIG\_XNU\_ARMCPU=y and CONFIG\_XNU\_ARM\_DT\_PLATFORM=y.
- dts/mt6835.dtsi carries the measured cluster layout, the PSCI conduit and the GIC ranges; tb365fc.dts enables the CPUs.

### 操作步骤

- Compare dts/mt6835.dtsi with the stock FDT /cpus, interrupt-controller and timer nodes.
- After the first boot, check the PSCI conduit and per-CPU bring-up against /proc/cpuinfo and the stock dmesg.

### 开发经验

- The stock topology is one GICv3 domain: A55 at affinity 0x0 and 0x100-0x500 \(cluster type E\), A76 at 0x600/0x700 \(cluster type P\). The earlier MT6833-style 0x0-0x1 / 0x100-0x105 guess was wrong.
- The architected timer runs at 13 MHz \(clock-frequency 0xc65d40\), and GICD spans 0x40000 bytes rather than 64 KiB.
- The stock tree has a /psci node \(compatible arm,psci-1.0, method smc\) and every CPU uses enable-method = "psci"; the dtsi conduit matches it.
- The stock tree uses four-cell interrupt specifiers whose trailing cell is a MediaTek wakeup flag; the ADT keeps the standard three-cell GIC form.
- The on-device /proc/cpuinfo lists 8 CPUs: six 0xd05 \(Cortex-A55\) and two 0xd0b \(Cortex-A76\), matching the DTB affinities.

### 完成条件

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU.

### 当前范围

- SMP is not enabled in UniXNU; the PSCI conduit and cluster types are untested there, although Android already runs all eight cores.

### 下一步

- Boot the first CPU on hardware, confirm the PSCI conduit, then enable the remaining cores one cluster at a time.

### 证据

- `device`: [Core count and part numbers \(0xd05 x6, 0xd0b x2\) match the cluster layout in the device tree.](https://github.com/LittleStar-OuO/UniXNU-tb365fc/blob/b13016b5088c91819dd4350f733a938e109723ad/dts/tb365fc.dts)
  Command: <code>adb shell cat /proc/cpuinfo</code>. Revision: `5ba47e6284567baa3450f9d82b5d56963cd14035`.

## 内存与 DMA {#memory}

`planned`

### 硬件与依赖

- DRAM base and size, reserved-memory carveouts and the IOMMU/SMMU stream inventory.
- The stock tree declares CMA pools \(ssmr and ssheap, 256 MiB each, 16 MiB/2 MiB alignment\) and dynamic carveouts whose final addresses are assigned by LK.

### 配置

- tb365fc.dts must expose exactly one enabled memory node with one contiguous range; the shared ADT generator rejects anything else.
- Reserved regions stay outside the contiguous DRAM range reported to XNU.

### 操作步骤

- Read the stock DTB memory and reserved-memory nodes and reconcile them with /proc/iomem and /proc/meminfo on the rooted device.
- Regenerate the ADT and confirm chosen/dram-base and dram-size match the extracted values.

### 开发经验

- The stock DTB memory node is a 1 GiB stub at 0x40000000 \(0x0 0x40000000 0x0 0x40000000\) that LK replaces at boot, so the DRAM size cannot be read from the DTB.
- Measured on the tablet: MemTotal is 7,991,068 kB, CmaTotal 737,280 kB, and /proc/iomem maps DRAM from 0x40000000 to 0x23fffffff, confirming the 8 GiB range in tb365fc.dts.
- The live map reserves 0x47c80000-0x47ce6fff \(DTB\), 0x66f00000-0x68be2fff \(vendor ramdisk\) and a large block from 0x20888f000 to 0x23e5fffff; the ADT must keep such ranges out of the region handed to XNU.

### 完成条件

- All handoff regions are accounted for and each enabled DMA engine accesses its allocated range with the documented cache policy.

### 当前范围

- The reserved ranges are LK-assigned and this is Android's post-LK view, not a UniXNU handoff contract; the final carveouts remain unknown.

### 下一步

- Regenerate the ADT once the UEFI FD runs and diff its memory map against this inventory.

### 证据

- `source`: [Extracted the base DTB from the stock vendor\_boot image and dumped its memory and reserved-memory nodes.](https://github.com/LittleStar-OuO/UniXNU-tb365fc/blob/b13016b5088c91819dd4350f733a938e109723ad/tools/extract_fdt.py)
- `device`: [MemTotal and the System RAM interval 0x40000000-0x23fffffff confirm the 8 GiB memory node.](https://github.com/LittleStar-OuO/UniXNU-tb365fc/blob/b13016b5088c91819dd4350f733a938e109723ad/dts/tb365fc.dts)
  Command: <code>adb shell cat /proc/meminfo; adb shell su -c cat /proc/iomem</code>. Revision: `5ba47e6284567baa3450f9d82b5d56963cd14035`.

## 存储与根卷 {#storage}

`planned`

### 硬件与依赖

- Storage host candidates in the stock DTB: ufshci@112b0000 \("mediatek,mt8183-ufshci", reg 0x112b0000/0x2300, IRQ 0x189\) is enabled, while mmc@11230000 \("mediatek,mt6835-mmc", reg 0x11230000/0x10000 + 0x11e70000/0x1000, IRQ 0x183\) and mmc@11240000 are explicitly disabled.
- Stock scatter: boot\_a 0x28F00000, vendor\_boot\_a 0x2CF00000, init\_boot\_a 0x30F00000, dtbo\_a 0x31700000, super 0x4B000000 \(0x2C0000000 bytes\), userdata at byte 0x34C800000 in both the EMMC and UFS layout.
- The userdata partition geometry and the Data volume UUID.

### 配置

- \[userdata\] first\_lba = 0x34C800, last\_lba = 0x1DC8FF7 and lba\_bytes = 4096 come from the on-device GPT; the APFS Data volume UUID is still REQUIRED.
- A storage component is selected only after the host-controller inventory; no storage gate is enabled in tb365fc\_defconfig yet.

### 操作步骤

- Read /proc/partitions, the GPT \(sgdisk -p on the boot LUN: /dev/block/sda\* for UFS or /dev/block/mmcblk0\* for eMMC\) and the queue/logical\_block\_size on the rooted device.
- Record the userdata entry LBA range and the APFS volume UUID used for root matching.

### 开发经验

- The stock DTB enables a UFS host \(ufshci@112b0000\) and disables both MSDC hosts; the dtbo also carries the mt6377\_vufs rail. The earlier "eMMC on MSDC\_0" reading came from the scatter's first layout section and is not established.
- The scatter is a download map, not the GPT: its pgpt entry is NONE and the userdata size 0xC0000000 is the factory image, so the real partition may extend further.
- Measured on the tablet: the UFS host 112b0000.ufshci drives a Samsung KLUDG2R1JF-B0F1 LUN with 4096-byte logical sectors; /dev/block/sdc reports 249,921,536 512-byte sectors \(127.96 GB\) and a 71-entry GPT.
- GPT entries: userdata 0x34C800-0x1DC8FF7 \(111,091,680 KiB\), boot\_a 0x28F00 and vendor\_boot\_a 0x2CF00 \(64 MiB each\), init\_boot\_a 0x30F00 and dtbo\_a 0x31700 \(8 MiB each\), super 0x4B000 \(11 GiB\); the init\_boot\_b entry is 11,776 KiB, an asymmetry in the factory table.
- The LK log reports the UFS link as "HS-G3-2, 1 lane".

### 完成条件

- Host: register, clock, link and SMMU facts match the board inventory.
- Reads: SCSI capacity, GPT and known blocks are correct; OS/SystemOS windows stay within userdata.
- Root: the configured volume mounts and launchd starts. Persistence: writes survive reboot within the allocated Data region.

### 当前范围

- UniXNU's firmware has no UFS driver \(MsdcDxe is the only storage path\) and the SMMU stream wiring is unknown; the Data volume UUID cannot be set until APFS is installed.

### 下一步

- Port a UFS host path into the firmware, then record the GPT and the Data volume UUID once APFS is installed.

### 证据

- `source`: [Identified the enabled UFS host, the disabled MSDC hosts and their register windows in the stock base DTB.](https://github.com/LittleStar-OuO/UniXNU-tb365fc/blob/b13016b5088c91819dd4350f733a938e109723ad/tools/extract_fdt.py)
- `device`: [GPT at 4096-byte sectors: the userdata LBA range and the A/B boot partition sizes match the board.toml \[userdata\] values.](https://github.com/LittleStar-OuO/UniXNU-tb365fc/blob/b13016b5088c91819dd4350f733a938e109723ad/tools/pull-stock-images.sh)
  Command: <code>adb shell su -c 'dd if=/dev/block/sdc bs=4096 count=34' with a local GPT parse</code>. Revision: `5ba47e6284567baa3450f9d82b5d56963cd14035`.

## 显示 {#display}

`implemented`

### 硬件与依赖

- DSI panel variant from the stock overlay: panel1@0 "boe,hx83122b,vdo" or panel2@1 "tm,nt36532,vdo", both video-mode with TE.
- Panel rails and GPIOs: power enable GPIO 0x22, backlight enables 0x15/0x19, reset GPIO 0x56 \(86\), bias GPIOs 0x7c \(124\) and 0x97 \(151\).
- Backlight controllers ST7758 and AW99706 at I2C addresses 0x2e and 0x76 on two panel channels.
- Panel resolution, refresh rate and init sequence from the vendor LCM driver; the device tree carries no timings.

### 配置

- Bootstrap relies on the firmware GOP framebuffer only; no XNU display provider is selected yet.

### 操作步骤

- Record the active panel compatible, wm size and wm density on the tablet and match them with the stock LCM driver name from the LK/kernel log.
- Record the GOP mode from the UEFI boot log when the first firmware image runs.

### 开发经验

- The board ships with either a BOE HX83122B or a Tianma NT36532 video-mode panel using the same rails, reset and TE wiring.
- Measured on the tablet: 1600x2560 at 90.00 Hz with a physical density of 249.46 dpi \(ro.sf.lcd\_density 320\), so the panel is portrait 1600x2560.
- Both panel1@0 and panel2@1 stay enabled in the live merged FDT; LK picks the variant at runtime from the panel ID.
- The LK log \(/proc/pl\_lk\) names the active driver: lcm\_compare\_id matches "hx83122b\_boe AF" and LK uses "cava\_hx83122b\_boe\_vdo\_cphy\_dsc\_90hz\_lcm\_drv" \(BOE HX83122B, video mode, CPHY, DSC, 90 Hz\) with fps=9009.
- The same log reads the backlight ids: AW99706 answers on I2C 0x76 with id 0x7 while ST7758 returns 0, so this unit uses the AW99706 controller on both channels.
- The UEFI firmware reuses the stock LK scanout 1600x2560x32 at 0xFCF2B000 \(0xFA0000 bytes\) through SimpleFbDxe; the boot logo and the UniXNU menu render with correct geometry and colors on the unit, so the GOP mode is 1600x2560x32.

### 完成条件

- A known frame appears with correct geometry and colors, then userland presentation and backlight controls work.

### 当前范围

- XNU has no display provider yet; the DSI timings and init sequence still live inside the vendor LCM driver and UniXNU does not drive the backlight.

### 下一步

- Extract the DSI timings and init sequence for cava\_hx83122b\_boe\_vdo\_cphy\_dsc\_90hz\_lcm\_drv and write the XNU display provider; the firmware GOP path is already verified.

### 证据

- `source`: [Extracted the stock dtbo overlay that declares both panel variants, their rails and the backlight controllers.](https://github.com/LittleStar-OuO/UniXNU-tb365fc/blob/b13016b5088c91819dd4350f733a938e109723ad/tools/extract_fdt.py)
- `device`: [Active mode 1600x2560 at 90.00 Hz, dpi 249.46, matching wm size and ro.sf.lcd\_density 320.](https://github.com/LittleStar-OuO/UniXNU-tb365fc/blob/b13016b5088c91819dd4350f733a938e109723ad/tools/collect-device-info.sh)
  Command: <code>adb shell dumpsys SurfaceFlinger | grep activeMode</code>. Revision: `5ba47e6284567baa3450f9d82b5d56963cd14035`.
- `device`: [LK log names the selected BOE HX83122B LCM driver, reports fps 9009, and identifies AW99706 as the backlight controller.](https://github.com/LittleStar-OuO/UniXNU-tb365fc/blob/b13016b5088c91819dd4350f733a938e109723ad/tools/collect-device-info.sh)
  Command: <code>adb shell su -c cat /proc/pl_lk</code>. Revision: `ce3fb214d55f674ef937781e076c8f8f36ed08a5`.

## 输入 {#input}

`implemented`

### 硬件与依赖

- Touch over SPI at 10 MHz \(0x989680\) with spi-cpha: IRQ GPIO 4 \(active low\), reset GPIO 43 \(0x2b\), dual driver set himax,hxcommon and novatek,NVT-ts-spi, Novatek 40x64 node grid \(mp-criteria-6096\).
- Pogo keyboard node "lenovo,lenovo\_keyboard" and MT6377 PMIC keys.

### 配置

- Input components are selected only after the SPI bus and GPIO inventory; no input gate is enabled yet.

### 操作步骤

- Read the stock overlay touch/keys nodes and /sys/class/input on the rooted device.
- Record which touch firmware variant the unit actually runs and the pogo keyboard protocol.

### 开发经验

- Touch is a Himax/Novatek SPI part on IRQ GPIO 4 with reset on GPIO 43.
- A Lenovo pogo keyboard and MT6377 PMIC keys \(power, volume\) are present.
- Measured on the tablet: /dev/input exposes himax-touchscreen \(event2\), lenovo-stylus \(event3\), mtk-kpd \(event1\), mtk-pmic-keys \(event0\), hall\_irq \(event5\) and the MT6377 headset jack \(event4\); the Himax driver is the one bound on this unit.
- In the UEFI menu Volume Up/Down move the selection and Power or Enter activate the highlighted entry, including the Tools viewer \(Up/Down change the QR speed, Power/Enter exit\); the KPD matrix bit 0 carries Volume Up and the MT6377 PMIC keys carry Volume Down and Power.

### 完成条件

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive, and buttons produce expected HID reports.

### 当前范围

- Touch, stylus and the pogo keyboard have no XNU driver yet; the pogo keyboard protocol and the stylus HID descriptor are not recorded.

### 下一步

- Port the Himax touch SPI path for XNU and map the 16000x25600 range onto the panel.

### 证据

- `source`: [Extracted the stock overlay touch node with its SPI frequency, GPIOs and driver compatibles.](https://github.com/LittleStar-OuO/UniXNU-tb365fc/blob/b13016b5088c91819dd4350f733a938e109723ad/tools/extract_fdt.py)
- `device`: [Input devices match: himax-touchscreen, lenovo-stylus, mtk-kpd, mtk-pmic-keys, hall\_irq and the headset jack.](https://github.com/LittleStar-OuO/UniXNU-tb365fc/blob/b13016b5088c91819dd4350f733a938e109723ad/dts/tb365fc.dts)
  Command: <code>adb shell getevent -pl</code>. Revision: `5ba47e6284567baa3450f9d82b5d56963cd14035`.

## GPU {#gpu}

`planned`

### 硬件与依赖

- Valhall GPU at 0x13000000 \("mediatek,mali", "arm,mali-valhall"\), five interrupts 0x10D-0x111 \(GPU/MMU/JOB/EVENT/PWR\), OPP table and GED supply from the stock base DTB.

### 配置

- No GPU component is selected; the bootstrap image does not initialize the GPU.

### 操作步骤

- Record GPU registers, power and clock inputs from the stock DTB before selecting an accelerated frontend.

### 开发经验

- The stock tree places the GPU at 0x13000000 with GPU/MMU/JOB/EVENT/PWR interrupts and an operating-points table.
- GPU bring-up is deferred until XNU reaches IOKit initialization.

### 完成条件

- GPU submissions complete, mapping/fence handling is correct, a known image renders, and the selected Metal client presents it.

### 当前范围

- The GPU model, firmware and IOMMU wiring are only identified by compatible string.

### 下一步

- Inventory the GPU, IOMMU and power domain inputs after the first successful XNU boot.

### 证据

按下一步操作收集证据。

## 网络 {#network}

`planned`

### 硬件与依赖

- MediaTek connsys block: wifi@18000000 \("mediatek,wifi", 1 MiB register window, IRQ 0x83, 6 MiB EMI window\) and consys@18002000 \("mediatek,mt6835-consys"\) behind the MT6377 connsys power gate.
- Bluetooth firmware connsys\_bt.img from the stock package.

### 配置

- No network component is selected; the bootstrap image has no network stack input.

### 操作步骤

- Identify the combo chip and firmware variant from the vendor kernel log and /sys/kernel/debug on the tablet, then record hashes in proprietary-files.txt.

### 开发经验

- Wi-Fi is a MediaTek connsys block at 0x18000000, not an SDIO/PCIe part.
- connsys\_bt.img \(4,287,968 bytes\) embeds the Wi-Fi PHY path phy/6631 and the "MTK SOC2\_2" connectivity revision.
- Measured on the tablet: persist.vendor.connsys.chipid is 0x6835 \(the SoC\) while vendor.connsys.adie.chipid is 0x6631 for Wi-Fi, BT, GPS and FM; the BT firmware names MT6631 ASIC MINIROM with patch 20250110150354, so the combo die is MT6631.
- Android's wlan\_drv\_gen4m\_6835 is running and carrying traffic, so the stock hardware path works.

### 完成条件

- Scanning, association, address configuration and sustained receive/transmit traffic pass with the selected firmware.

### 当前范围

- The UniXNU side has no firmware ABI or MAC provisioning; the firmware files live on the vendor partition and are not in this repository.

### 下一步

- When network work starts, inventory the vendor firmware names and hashes and the connsys power/EMI windows.

### 证据

- `source`: [Records the SHA-256 of connsys\_bt.img and its source partition.](https://github.com/LittleStar-OuO/UniXNU-tb365fc/blob/b13016b5088c91819dd4350f733a938e109723ad/proprietary-files.txt)
- `device`: [ADIE chip id 0x6631 for Wi-Fi/BT/GPS/FM and an MT6631 BT firmware banner settle the combo die.](https://github.com/LittleStar-OuO/UniXNU-tb365fc/blob/b13016b5088c91819dd4350f733a938e109723ad/proprietary-files.txt)
  Command: <code>adb shell getprop | grep -i connsys</code>. Revision: `5ba47e6284567baa3450f9d82b5d56963cd14035`.

## 音频 {#audio}

`planned`

### 硬件与依赖

- MT6377 PMIC codec \("mediatek,mt6377-sound"\) with accessory detection \("mediatek,mt6377-accdet"\).
- Four AW883XX smart amplifiers \("awinic,aw883xx\_smartpa", I2C 0x34, reset GPIOs 0x20/0x21/0x5c/0x23, sound channels 0-3\) on I2S3, plus an alternative Richtek RT5512 speaker amp at I2C 0x5c.
- The DMIC set from the stock overlay.

### 配置

- No audio component is selected.

### 操作步骤

- Record the codec/amp wiring and firmware from the stock DTB and vendor files.

### 开发经验

- The audio path is built around the MT6377 codec with four AW883XX smart amplifiers configured per speaker channel; the skeleton's MT6359 assumption was wrong.
- The stock overlay also declares a Richtek RT5512 speaker amp at 0x5c, so two amplifier variants may exist across board revisions.
- The stock overlay also carries the MT6377 auxadc, gauge and regulator children that feed the audio rails.

### 完成条件

- Each declared route carries the selected audio format through playback or capture and handles start/stop correctly.

### 当前范围

- The speaker topology and firmware are not fully inventoried.

### 下一步

- Inventory the codec, amplifiers and DMIC wiring.

### 证据

- `source`: [Extracted the stock overlay PMIC and codec nodes.](https://github.com/LittleStar-OuO/UniXNU-tb365fc/blob/b13016b5088c91819dd4350f733a938e109723ad/tools/extract_fdt.py)

## 电源 {#power}

`planned`

### 硬件与依赖

- MT6377 PMIC \(bucks, LDOs, charger, gauge, RTC, keys, accdet\), MT6685 RTC/clock buffer, the MT6319 external buck \(mt6315\_3 regulator\) and the RT5133 GPIO expander.
- MM8013 fuel gauge, a PPS charger path built on the Southchip SC89890H plus an SGM charger, and the AW35615 USB-PD controller.

### 配置

- The bootstrap image runs without a battery/charger driver; sleep-disabled defaults stay in place.

### 操作步骤

- Record PMIC registers, regulator rails and battery thresholds from the stock DTB before writing a power driver.

### 开发经验

- The PMIC is MT6377, not MT6359; it also provides the MT6377-keys used for the power and volume buttons.
- The stock overlay lists the full regulator set \(vbuck1-6, vs1/vs2, vsram, va12/vaud18/vaud28, vaux18, vbif28, vcn33/vcn18, vxo22, vm18, vemc, vio18, vrf rails, vmc, vusb, vmch\) and the gauge/RTC/charger children.
- Charging is a PPS path \("mediatek,charger,pps"\) with a two-charger configuration: Southchip SC89890H at I2C 0x6a and an SGM charger at 0x6c, with the AW35615 PD controller at 0x22.
- Measured on the tablet: the MM8013 gauge driver fg\_mm801310c reports VBAT/VBUS, and the charger stack runs sc8989x on I2C 7-006a plus sc8541 on 5-006a under the PPS policy; MT6377 supplies the PMIC keys and the headset-jack codec path.

### 完成条件

- Declared power controls and battery readings match observations; each claimed sleep/resume transition restores its dependent peripherals.

### 当前范围

- No power driver is written; charger, gauge and RTC register maps are unverified for UniXNU.

### 下一步

- Record the PMIC I2C addresses and the rails the panel, touch and storage depend on.

### 证据

- `source`: [Extracted the stock overlay PMIC, regulator and gauge nodes.](https://github.com/LittleStar-OuO/UniXNU-tb365fc/blob/b13016b5088c91819dd4350f733a938e109723ad/tools/extract_fdt.py)
- `device`: [fg\_mm801310c, sc8989x 7-006a and sc8541 5-006a report battery and charger state.](https://github.com/LittleStar-OuO/UniXNU-tb365fc/blob/b13016b5088c91819dd4350f733a938e109723ad/tools/collect-device-info.sh)
  Command: <code>adb shell su -c dmesg</code>. Revision: `5ba47e6284567baa3450f9d82b5d56963cd14035`.

## 镜像组装 {#packaging}

`implemented`

### 硬件与依赖

- The payload image, the boot/vendor\_boot layout accepted by the TB365FC LK, the flash method \(fastboot flash boot\_a\) and the partition size limits.
- Stock boot image v4 \(no load addresses\); stock vendor\_boot addresses tags/dtb 0x47C80000 and ramdisk 0x66F00000; partition sizes boot/vendor\_boot 64 MiB, dtbo/init\_boot 8 MiB.

### 配置

- The bring-up boot image is Android header v4 \(4096-byte pages\) with the gzip FD as kernel and the 1 MiB FAT12 UNIXNU ramdisk; v4 carries no load addresses, so LK places the kernel at the stock vendor\_boot kernel\_addr 0x40000000.
- The future payload volume is FAT, labelled TB365FC, 192 MiB, and will ride in the same v4 image once the XNU build exists.

### 操作步骤

- Build the payload and boot image, then verify the header fields and offsets against the stock boot image before flashing.
- Record every flash command and the exact image revision.

### 开发经验

- The stock header is v4 while UniXNU builds v2 so that LK honours kernel\_addr = 0x40080000; v2 is proven on merlinx and camellia \(same MTK family\) but not on this LK yet.
- The stock images are padded to the partition sizes, so image hashes cover the padding as well.
- The on-device GPT confirms boot\_a and vendor\_boot\_a are 64 MiB and init\_boot\_a and dtbo\_a 8 MiB, so a self-built boot image must stay below 64 MiB; the init\_boot\_b entry is 11,776 KiB.
- The self-built v4 image \(1.7 MiB\) was flashed to boot\_a with fastboot and accepted by the TB365FC LK; it boots to the UniXNU menu, so the v4 flash path is proven and boot\_b stays stock as the recovery path.

### 完成条件

- Kernel and prelink succeed, payload contains all declared inputs, and the boot image matches the bootloader format and size limit.

### 当前范围

- The payload volume has not been built; the flashed image carries only the empty UNIXNU ramdisk and the UEFI FD.

### 下一步

- Once the XNU payload exists, extend the ramdisk or payload volume and verify the menu reads it.

### 证据

- `source`: [Verified the Android boot header fields used to derive the image geometry.](https://github.com/LittleStar-OuO/UniXNU-tb365fc/blob/b13016b5088c91819dd4350f733a938e109723ad/tools/unpack_boot_image.py)
- `device`: [boot\_a and vendor\_boot\_a are 64 MiB, init\_boot\_a and dtbo\_a 8 MiB, bounding the self-built image sizes.](https://github.com/LittleStar-OuO/UniXNU-tb365fc/blob/b13016b5088c91819dd4350f733a938e109723ad/tools/pull-stock-images.sh)
  Command: <code>local GPT parse of adb shell su -c 'dd if=/dev/block/sdc bs=4096 count=34'</code>. Revision: `5ba47e6284567baa3450f9d82b5d56963cd14035`.

## 诊断 {#diagnostics}

`implemented`

### 硬件与依赖

- adb/fastboot access on the rooted tablet, the stock boot/vendor\_boot/dtbo images, serial or pstore log capture, and the UEFI boot log from uefi-tb365fc.

### 配置

- The UEFI Advanced Logger ring mirrors to UART0 \(115200 8N1\) and the Tools menu exports it as 752-byte QR frames at five speed gears; Power or Enter exits the viewer.
- tools/collect-device-info.sh writes a local, privacy-filtered inventory; tools/unpack\_boot\_image.py and tools/extract\_fdt.py read Android boot images and extract their DTBs.
- The scripts export MSYS\_NO\_PATHCONV on Git Bash so /dev/block paths reach adb unmangled, and the property filter drops psn and bootloader serial keys.

### 操作步骤

- Run the collection script over adb and archive the output outside the repository.
- Record the last confirmed boot stage and the matching image revision for every hardware checkpoint.

### 开发经验

- The stock package was unpacked on the host with the tools in this repository; the UEFI checkpoints \(logo, fingerprint-matched menu, Advanced Logger pages\) are confirmed on the unit by screen photos kept outside the repository, and no XNU checkpoint exists yet.
- The script ran on the unit after two fixes: MSYS path conversion was rewriting /dev paths \(173564d\) and the property filter missed psn/bootload\_sn \(5ba47e6\); the clean inventory stays outside the repository because the FDT embeds device-unique data.
- Root came from SukiSU Ultra in LKM mode: adb su works only with SU compat enabled and yields u:r:ksu:s0; the stock kernel has no KernelSU strings.
- fastboot getvar all ran in bootloader mode and reported an unlocked bootloader; the dump stays local because it carries the bootloader serial.
- The pstore partition \(sdc19\) is zero-filled, but after a reboot /sys/fs/pstore exposes the previous kernel console tail \(console-ramoops-0\) and /proc/pl\_lk exposes the preloader/LK ring; the LK ring is the reliable source for boot-stage facts because wlan traffic overruns the kernel console in about a second.

### 完成条件

- Each claimed milestone has a reproducible command, a matching source/image revision and an accessible result.

### 当前范围

- The inventory is a local snapshot; reproducing it needs the scripts at 5ba47e6 or later. Boot photos and serial captures stay local because they can carry device-identifying data, so the record has no published log yet. The kernel ring buffer keeps only about a second of logs at wlan rates, so kernel-stage evidence needs an immediate post-boot capture; pl\_lk and console-ramoops are the retained sources.

### 下一步

- Capture /proc/pl\_lk and console-ramoops after every boot change and archive them locally.

### 证据

- `source`: [Ran against the stock boot, init\_boot and vendor\_boot images.](https://github.com/LittleStar-OuO/UniXNU-tb365fc/blob/b13016b5088c91819dd4350f733a938e109723ad/tools/unpack_boot_image.py)
- `source`: [Extracted the base DTB and the DTBO entry from the stock images.](https://github.com/LittleStar-OuO/UniXNU-tb365fc/blob/b13016b5088c91819dd4350f733a938e109723ad/tools/extract_fdt.py)
- `device`: [Produced the clean inventory \(identity, meminfo, GPT head, iomem, filtered dmesg, FDT\) used across the areas above.](https://github.com/LittleStar-OuO/UniXNU-tb365fc/blob/b13016b5088c91819dd4350f733a938e109723ad/tools/collect-device-info.sh)
  Command: <code>tools/collect-device-info.sh</code>. Revision: `5ba47e6284567baa3450f9d82b5d56963cd14035`.
- `device`: [pstore partition holds only zeroes; the live console-ramoops files appear only in /sys/fs/pstore after a reboot.](https://github.com/LittleStar-OuO/UniXNU-tb365fc/blob/b13016b5088c91819dd4350f733a938e109723ad/tools/collect-device-info.sh)
  Command: <code>adb shell su -c 'dd if=/dev/block/sdc19 bs=1M count=1 | od -An -tx1'; adb shell su -c 'ls -la /sys/fs/pstore'</code>. Revision: `5ba47e6284567baa3450f9d82b5d56963cd14035`.
- `device`: [Captured the LK ring and the previous kernel console tail; the LK ring carries the panel and backlight facts recorded above.](https://github.com/LittleStar-OuO/UniXNU-tb365fc/blob/b13016b5088c91819dd4350f733a938e109723ad/tools/collect-device-info.sh)
  Command: <code>adb shell su -c cat /proc/pl_lk; adb shell su -c cat /sys/fs/pstore/console-ramoops-0</code>. Revision: `ce3fb214d55f674ef937781e076c8f8f36ed08a5`.
- `source`: [The UniXNU UI changes: scale-4 menu with ScrollFirst and the Advanced Logger viewer with five speed gears and the key-drain fix.](https://github.com/LittleStar-OuO/UniXNU/commit/794bd2de672d886b980c2a8f5b9e64eace34fd33)

</div>
