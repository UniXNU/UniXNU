# Xiaomi Pad 6 Pro \(liuqin\): UniXNU first boot on the SM8475 pong stack \(document97\)

[document97/UniXNU-liuqin](https://github.com/document97/UniXNU-liuqin)

<div v-pre>

Xiaomi Pad 6 Pro \(liuqin\) on the SM8475 stack of UniXNU-pong: board data, first-boot configuration and stage-1 firmware; nothing is device-verified yet

源记录: [porting.toml](https://github.com/document97/UniXNU-liuqin/blob/fe0e8d790e24120970083e20c1a7d9c86cdbb87c/porting.toml), `fe0e8d790e24120970083e20c1a7d9c86cdbb87c`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `implemented` |
| [固件与启动](#firmware) | `implemented` |
| [内存与 DMA](#memory) | `implemented` |
| [显示](#display) | `implemented` |
| [输入](#input) | `implemented` |
| [存储与根卷](#storage) | `planned` |
| [镜像组装](#packaging) | `implemented` |
| [CPU 与中断](#cpu) | `planned` |
| [GPU](#gpu) | `planned` |
| [网络](#network) | `implemented` |
| [音频](#audio) | `planned` |
| [电源](#power) | `implemented` |
| [诊断](#diagnostics) | `implemented` |

## 配置 {#configuration}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- UniXNU-pong e0ee6df \(same SM8475 SoC, PMIC family, UFS host, Adreno 730, QCA6490\)
- mainline liuqin tree yzddmr6/linux-sm8450-liuqin fe81794b \(not committed; scripts/gen-liuqin-memory.py --fetch caches it in the ignored reference/mainline\)
- stock uefiplat.cfg of V14.0.9.0.TMYCNXM \(the build on the tablet; read from its uefi.elf\), whose HYP/PIL/Demura/FD/splash regions equal OS3.0.7.0.VMYCNXM's \(1696108518/UniXNU-liuqin docs/vendor-inputs.md\)

### 配置

- board.toml selects dts/liuqin.dts, liuqin\_ipados18\_defconfig, uefi-liuqin liuqinPkg and configs/liuqin-board.json

### 操作步骤

- Keep the pong SM8475 implementation and its build entry points; replace board data only: memory, panel geometry and scale, touch wiring, identity, firmware package and boot DTB.

### 开发经验

- liuqin shares every SoC resource the pong ADT generator encodes \(GIC 0x17100000/0x17180000 stride 0x40000, UFS 0x1d84000 SID 0xe0 SPI 265, SMMU 0x15000000\).
- Touch is on the same bus as pong's \(QUP0 SE4 spi@990000, IRQ gpio21\); the controller differs \(Novatek NT36532, no reset line\).
- Power, volume-down \(PON\) and volume-up \(PM8350 GPIO6, PPID 0x18d\) match pong's keys.
- QCA6490 WLAN enable gpio80 and xo-clk gpio204 match pong's pcie0 node.
- A unified diff hunk is applied only as far as its @@ counts say, so a hunk whose counts are not updated after its body grows drops its last line without any error: scripts/check-xnu-patches.py recomputes both counts and package.yml runs it before anything is compiled.

### 完成条件

- The stage-1 image reaches the UniXNU menu on the tablet, then the stage-2 image reaches SpringBoard.

### 当前范围

- Internal component, kernel argument and script names stay pong\_\*: they name the shared SM8475 implementation.

### 下一步

- Run the stage-1 workflow of uefi-liuqin with a liuqin full OTA package and boot its image with fastboot boot.

### 证据

- `source`: [Board data file read by scripts/make-pong-adt-ipados18.py --board liuqin; pong's defaults are unchanged.](https://github.com/document97/UniXNU-liuqin/blob/fe0e8d790e24120970083e20c1a7d9c86cdbb87c/configs/liuqin-board.json)

## 固件与启动 {#firmware}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- uefi-liuqin branch liuqin: Platforms/Xiaomi/liuqinPkg derived from pongPkg
- stock Cape SoC base DTB of liuqin vendor\_boot \(ABL selects by msm-id 0x212/0x213/0x21c, board-id 0x10008\)

### 配置

- FD 0xA7100000 +0x300000 inside the stock UEFI FD window; SimpleFbDxe GOP on 0xB8000000 1800x2880 stride 7200; vendor modules Binaries/pong or Binaries/liuqin

### 操作步骤

- tools/fetch-liuqin-stock.py extracts vendor\_boot, uefi and dtbo from a full OTA package and selects the Cape SoC DTB.
- uefi-liuqin .github/workflows/liuqin-uefi.yml builds the firmware and the v4 boot image.

### 开发经验

- The stock PIL Reserved \(0x85200000 +0x1DC00000\) overlaps Display Demura; the first-listed-wins union equals the pong descriptors' union 0x85200000-0xA3F00000.
- A previous liuqin attempt with a Cape DTB from vendor\_boot reached the DarwinBoot handoff \(1696108518/UniXNU-liuqin docs/liuqin-boot-progress.md\).

### 完成条件

- fastboot boot of Mu-liuqin.img shows the UniXNU menu; with a payload it lists the entry and DarwinBoot hands off.

### 当前范围

- Built, not yet booted: the tablet's bootloader is still locked.

### 下一步

- Boot Mu-liuqin.img from the stage-1 workflow and photograph the panel.

### 证据

- `source`: [Host test with a synthetic full OTA \(stored zip, REPLACE and REPLACE\_XZ, three base DTBs\) wrote byte-identical partitions and selected the Cape SoC DTB.](https://github.com/document97/UniXNU-liuqin/blob/fe0e8d790e24120970083e20c1a7d9c86cdbb87c/tools/fetch-liuqin-stock.py)
- `source`: [Run 42217454136 \(77d2250, binaries=pong, DEBUG\): Mu-liuqin.img with boot header v4 and the kernel gzip\(BootShim + 3 MiB FD\) followed by a DTB byte-identical to the Cape SoC DTB of the V14.0.9.0.TMYCNXM vendor\_boot.](https://github.com/Document97/uefi-liuqin/actions/runs/42217454136)

## 内存与 DMA {#memory}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- 8 GB unit /memory from the stock ABL: 0x80000000+0x6A000000, 0xF1400000+0xEC00000, 0x800000000+0x39700000, 0x839D00000+0x1E00000, 0x840000000+0x140000000 \(1696108518/iPadOS-liuqin NOTES.md 6.2\)

### 配置

- Reserved = union of mainline liuqin reserved-memory, stock uefiplat.cfg and the pong SM8475 vendor capture; allocatable = DRAM minus that union

### 操作步骤

- python3 scripts/gen-liuqin-memory.py \[--fetch\] \[--dram base:size,...\] regenerates the file and the memory/reserved-memory of dts/liuqin.dts.

### 开发经验

- 7.81 GiB in five banks; 58 distinct reserved ranges; 12 allocatable ranges, 6.33 GiB.
- Every Reserv/RtData region of the V14.0.9.0.TMYCNXM uefiplat.cfg is excluded; HYP Reserved 0x830000000 +0x10000000 was allocatable before it was read.
- The kernel intersects every allocatable range with the boot's EfiConventionalMemory, so the union can only over-reserve.

### 完成条件

- DarwinBoot claims its window from these ranges and the kernel reaches launchd without a memory fault.

### 当前范围

- The 12 GB variant needs its own --dram; this tablet's /sys/firmware/fdt should replace the mainline input when captured.

### 下一步

- Capture /sys/firmware/fdt on the tablet and regenerate.

### 证据

- `source`: [Generated 5 banks 7.81 GiB, 99 reserved entries, 12 allocatable ranges 6.33 GiB; dts/liuqin.dts is written by the same run.](https://github.com/document97/UniXNU-liuqin/blob/fe0e8d790e24120970083e20c1a7d9c86cdbb87c/scripts/gen-liuqin-memory.py)

## 显示 {#display}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- CSOT m81\_42\_02\_0b NT36532 TDDI, dual DSI, DSC, video mode, 1800x2880
- KTZ8866 backlight at QUP0 SE1 \(i2c@984000, gpio4/gpio5\), address 0x11, 11-bit brightness \(0x04 bits 2:0, 0x05 bits 10:3, 0x08 bit 6 enable\)

### 配置

- The UI renders in software into the ABL framebuffer \(0xb8000000, display-scale 2\); no GPU scanout yet
- CONFIG\_XNU\_PONG\_BACKLIGHT=y builds LiuqinBacklight.cpp in place of pong's DSI backlight; pong\_backlight=0 keeps the ABL brightness

### 操作步骤

- Drive the KTZ8866 over the GENI I2C bus at 100 kHz the way Linux ktz8866.c does \(LSB, then MSB, enable bit cleared at 0\), leaving the ABL's bias, current sinks and ramp untouched, and keep PongBacklight's CoreBrightness layer above it.

### 开发经验

- pong dims an OLED with DSI DCS commands; liuqin's LCD has the KTZ8866 at a different bus, so the driver was replaced rather than extended.
- The ABL already configured the panel's bias and sinks, so the driver only touches the brightness registers.
- The ADT carries no backlight node: the driver uses fixed bus and GPIO numbers, and PongBacklight's /chosen property stays absent.

### 完成条件

- SpringBoard renders on the panel and the brightness slider changes it.

### 当前范围

- Built into kernel.macho \(run 42788427078\) but never booted.
- Software rendering only; no refresh-rate control and no GPU scanout.

### 下一步

- Boot it and move the brightness slider.

### 证据

- `source`: [KTZ8866 driver: register writes, GENI I2C setup, the CoreBrightness conformance, and the ABL-configured parts it deliberately leaves alone.](https://github.com/document97/UniXNU-liuqin/blob/fe0e8d790e24120970083e20c1a7d9c86cdbb87c/drivers/PongPower/LiuqinBacklight.cpp)
- `host`: [The kernel builds with PONG\_BACKLIGHT=y and the boot arguments carry pong\_backlight=0.](https://github.com/Document97/UniXNU-liuqin/actions/runs/42788427078)
  Command: <code>gh workflow run package.yml -R Document97/UniXNU-liuqin --ref liuqin -f os=ipados-18.7.10-22H374 -f prelink=false</code>. Revision: `df2dd999fb24fa462896b0240e4bad2ad6bff1dc`.

## 输入 {#input}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- NT36532 on spi@990000 CS0, 8 MHz by default \(9.6 MHz maximum\), IRQ gpio21, no reset line
- Novatek images from the stock release touch/: CSOT m81\_42\_02\_0b \(this tablet, liuqin\_touch\_fw=1\) and Tianma m81\_36\_02\_0a \(=2\), both checked against the release manifest

### 配置

- liuqin\_touch=1 selects the liuqin driver; pong\_touch=0 leaves pong's Goodix driver out
- liuqin\_touch\_fw, liuqin\_touch\_hz, liuqin\_touch\_flip and liuqin\_touch\_log are the other arguments
- build-xnu-ipados18.sh embeds the images found in LIUQIN\_TOUCH\_FW\_DIR into kernel.macho, so the kernel carries the firmware it downloads at boot

### 操作步骤

- Keep pong\_goodix.c's GENI/TLMM/clock path \(same SE4, same pins 16-19 and 21\) and add the NT36532 download and report protocol; samples go to /dev/pong-touch through pong\_touch\_post\(\).

### 开发经验

- The NT36532 is flashless: it waits in its boot loader until the host downloads the image, and it wants the status handshake within about 18 s.
- liuqin has no touch reset line and no touch supplies of its own: the panel's prepare resets the TDDI die and the firmware is downloaded after that.
- The device quirks \(GENI duplex opcode 3, the CRC reboot loop and its 0xa5 escape\) come from the earlier iPadOS-liuqin work on this tablet.

### 完成条件

- Touches reach SpringBoard; the pen and the keys behave.

### 当前范围

- Built into kernel.macho \(run 42788427078\) but never booted on the tablet.
- The report decode has only been exercised by the driver's own log so far.

### 下一步

- Boot it with liuqin\_touch\_log=8 and read the first reports.

### 证据

- `source`: [Polled NT36532 driver over QUP0 SE4: image download with the hardware CRC, the 65-byte point report, and the boot arguments above.](https://github.com/document97/UniXNU-liuqin/blob/fe0e8d790e24120970083e20c1a7d9c86cdbb87c/drivers/LiuqinTouch/liuqin_nvt.c)
- `host`: [kernel.macho 30,256,864 B carries both Novatek images \(names visible in the binary\) and the ADT carries /arm-io/liuqin-touch.](https://github.com/Document97/UniXNU-liuqin/actions/runs/42788427078)
  Command: <code>gh workflow run package.yml -R Document97/UniXNU-liuqin --ref liuqin -f os=ipados-18.7.10-22H374 -f prelink=false</code>. Revision: `df2dd999fb24fa462896b0240e4bad2ad6bff1dc`.

## 存储与根卷 {#storage}

`planned`

组件: `PongPlatform24`.

### 硬件与依赖

- UFS host 0x1d84000, SID 0xe0, SPI 265 \(same SoC\); this tablet's GPT

### 配置

- \[userdata\] carries this tablet's own window, 0x2A1600..0x1D143FA in 4 KiB sectors \(105.795 GiB\), and scripts/install-pong-ufs-data.py and scripts/prepare-ipados18-ufs-layout.py now read it from board.toml instead of hardcoding pong's

### 操作步骤

- Parse images/gpt\_both0.bin from the stock release that matches the build the tablet runs, with tools/parse-gpt.py; the entry gives the start and the grow-to-end marker, fastboot gives the size. Root, the stage-one UEFI and a reboot are all unnecessary.

### 开发经验

- The stock release carries the answer: images/gpt\_both0.bin of liuqin\_images\_V14.0.9.0.TMYCNXM\_13.0 is the LUN 0 table, and LUN 0 is the disk Android calls sda, so its entry 34 is the sda35 /dev/block/by-name reports.
- That table stores userdata as first\_lba 0x2A1600 with last\_lba = first\_lba - 1, the grow-to-end marker, so the end comes from fastboot: partition-size:userdata = 0x1A72DFB000 B = 0x1A72DFB 4 KiB sectors, hence 0x1D143FA.
- Three checks agree: all 34 partitions above userdata match fastboot's partition-size byte for byte, entries 13 and 24 of gpt\_both4.bin are boot\_a and vendor\_boot\_a \(the sde14 and sde25 of the 2026-11-12 adb session\), and boot\_a is 201,326,592 B like the release's boot.img.
- The window is 105.795 GiB, which is df -k /data \(110,930,924 KiB\) plus 3 MiB of f2fs metadata, and the extent implies a 124.89 GB LUN 0, the usable size of the 128 GB part.
- An unprivileged adb shell never had to be rooted: /proc/partitions, /proc/cmdline and /sys/class/block/\*/start stay denied on this ROM, but the GPT in the matching stock release needs neither root nor the stage-one UEFI.

### 完成条件

- The root and Data volumes mount from UFS.

### 当前范围

- The other installers, install-ipados18-ufs.py, install-pong-sparse-windows.py and install-pong-relocated-os.py, still name /dev/block/sda13 and pong's window in their own checks; only the layout writer and install-pong-ufs-data.py read board.toml today.
- liuqin has no recovery image yet, and every install script refuses to run outside recovery with userdata unmounted.

### 下一步

- Run package.yml with ipsw\_url for 22H374 so the userdata image and the kernel carry the real volume UUIDs, then boot stage two and check the Data volume.

### 证据

- `source`: [userdata 0x2A1600..0x1D143FA, 4 KiB sectors, 105.795 GiB, with the derivation recorded in the section comment.](https://github.com/document97/UniXNU-liuqin/blob/fe0e8d790e24120970083e20c1a7d9c86cdbb87c/board.toml)
- `source`: [35 partitions, userdata at entry 34 with last\_lba = first\_lba - 1; gpt\_main0.bin gives the same start and gpt\_both4.bin puts boot\_a and vendor\_boot\_a at entries 13 and 24, the sde14 and sde25 of 2026-11-12. The document also records the four cross-checks and why the device side could not supply the number.](https://github.com/document97/UniXNU-liuqin/blob/fe0e8d790e24120970083e20c1a7d9c86cdbb87c/docs/userdata-geometry.zh.md)
- `source`: [The reader the numbers came from: it validates the header CRC and the entry array CRC, detects 512 or 4096 B sectors and header-only files, and compares every partition against a fastboot getvar table.](https://github.com/document97/UniXNU-liuqin/blob/fe0e8d790e24120970083e20c1a7d9c86cdbb87c/tools/parse-gpt.py)
- `source`: [partition-size:userdata = 0x1A72DFB000 B, the measured end the grow-to-end marker needs, plus the 132 partition sizes the six LUN tables were checked against. The serial number is redacted.](https://github.com/document97/UniXNU-liuqin/blob/fe0e8d790e24120970083e20c1a7d9c86cdbb87c/device-info/fastboot-getvar-2026-11-14.txt)

## 镜像组装 {#packaging}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- macOS package workflow \(kernel, payload, PONGFAT1 boot image\) plus the encrypted stock release: Cape DTB, uefi.elf, touch/, fw/wlan/ and fw/adsp/
- The uefi-liuqin checkout for the firmware build \(ref liuqin, Mu\_Basecore cfb9372\)

### 配置

- package.yml runs the release against uefi-liuqin, merges adsp.mbn, embeds the touch and Wi-Fi firmware, takes the stock Cape DTB and passes --board liuqin to the ADT step
- Without ipsw\_url the run uses uuid5 placeholder volume UUIDs, so its kernel mounts no real volume

### 操作步骤

- Run the workflow, read the product check, then download the encrypted artifact and decrypt it with the password from the repository secret.

### 开发经验

- Runs 42781679150 and 42788427078 are green end to end: firmware, boot image, product check, encrypted upload.
- The bootable image is a v4 container assembled outside \`release\`: gzip\(BootShim + FD\) plus the stock Cape SoC DTB in the kernel slot, PONGFAT1 payload in the ramdisk slot, so one \`fastboot boot\` from the stock ABL is enough.
- The shared tree has no driver package for PACKAGES\_PATH; a firmware preflight copies &\#123;tree&\#125;/drivers/DarwinBoot24 out of the device repository \(5d09b75, still required\).
- The uEFI FD has 2632 B free in FVMAIN: the next module added to liuqinPkg will not fit.

### 完成条件

- boot/liuqin-xnu-initial.img boots to launchd.

### 当前范围

- The artifact is never device-tested \(hardware\_tested is false in pong-boot.json\).
- Placeholder volume UUIDs until a run is given the IPSW URL after the tablet's LBA layout is read.

### 下一步

- Run the workflow with -f ipsw\_url once the tablet's userdata geometry is known.

### 证据

- `source`: [Workflow: stock release steps for ADSP, touch and Wi-Fi firmware, then kernel, payload, firmware, boot image and the product check.](https://github.com/document97/UniXNU-liuqin/blob/fe0e8d790e24120970083e20c1a7d9c86cdbb87c/.github/workflows/package.yml)
- `host`: [Green run: liuqin-xnu-initial.img 102,162,432 B, kernel.macho 30,256,864 B, product check passed, artifact uploaded encrypted.](https://github.com/Document97/UniXNU-liuqin/actions/runs/42788427078)
  Command: <code>gh workflow run package.yml -R Document97/UniXNU-liuqin --ref liuqin -f os=ipados-18.7.10-22H374 -f prelink=false</code>. Revision: `df2dd999fb24fa462896b0240e4bad2ad6bff1dc`.

## CPU 与中断 {#cpu}

`planned`

组件: `PongPlatform24`.

### 硬件与依赖

- SM8475: one Cortex-X3 with three Cortex-A710 and four Cortex-A510 cores, the SoC of pong
- GIC distributor 0x17100000 and redistributors 0x17180000, stride 0x40000, from the stock uefiplat.cfg \(same pair pong's ADT encodes\)

### 配置

- cpus=1 in \[payload\] kernel\_args for the first boot
- CONFIG\_XNU\_ARMCPU=y, CONFIG\_XNU\_NATIVE\_ARCH\_TIMER=y, ARM\_DT\_PLATFORM=y, ARMVIRT\_PLATFORM=n

### 操作步骤

- Boot one CPU first; raise cpus after the kernel reaches launchd and read the secondary bring-up path of pong's ArmCpu driver on liuqin's GIC bases.

### 开发经验

- liuqin shares pong's GIC layout, so the ADT carries the same distributor and redistributor pair with stride 0x40000.
- The first boot runs on one CPU on purpose: the multi-core path is pong's, which no liuqin image has exercised.

### 完成条件

- The kernel reaches launchd on all eight CPUs, then on one CPU for the first desktop.

### 当前范围

- No SMP bring-up and no cpufreq or OPP data for liuqin yet.

### 下一步

- Raise cpus in board.toml after the first launchd boot and record the bring-up trace of the secondaries.

### 证据

- `source`: [kernel\_args pass cpus=1 for the liuqin first boot.](https://github.com/document97/UniXNU-liuqin/blob/fe0e8d790e24120970083e20c1a7d9c86cdbb87c/board.toml)

## GPU {#gpu}

`planned`

组件: `PongPlatform24`.

### 硬件与依赖

- Adreno 730 \(the GPU of pong\), GMU firmware and the a730 ZAP firmware of this board

### 配置

- pong\_gpu\_scanout=0 and pong\_gpu\_pool\_mib=0: the first boot renders in software into the ABL framebuffer
- CONFIG\_XNU\_PONG\_ADRENO\_PLATFORM=n, CONFIG\_XNU\_NATIVE\_ADRENO=n, NATIVE\_OFFLINE\_GPU=n

### 操作步骤

- Reach the desktop with software rendering; then extract liuqin's signed a730 ZAP firmware from the stock vendor partition and enable the pong A730 path.

### 开发经验

- The 22H374 binding profile needs a GPU ABI adaptation before a native Adreno archive can be linked; build-ipados18-pong-macos.py refuses the legacy GPU stages rather than linking them.
- pong's a730 ZAP firmware is signed for pong, so liuqin needs its own before the platform driver can start the GPU.

### 完成条件

- SpringBoard renders through the GPU with GPU scanout enabled.

### 当前范围

- No GPU acceleration, no Metal device; the first boot uses the software path.

### 下一步

- Extract liuqin's a730 ZAP firmware and add the ABI adaptation for 22H374.

### 证据

- `source`: [Adreno stages off: NATIVE\_ADRENO=n, PONG\_ADRENO\_PLATFORM=n, NATIVE\_OFFLINE\_GPU=n.](https://github.com/document97/UniXNU-liuqin/blob/fe0e8d790e24120970083e20c1a7d9c86cdbb87c/configs/liuqin_ipados18_defconfig)

## 网络 {#network}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- QCA6490 on PCIe0: wlan-enable gpio80, reset gpio94, clkreq gpio95, wake gpio96, xo-clk gpio204; the same registers, clocks and seven RPMh rails as pong
- Stock fw/wlan/ of the encrypted release: radio images plus Xiaomi's board calibration bd\_m81gf.elf \(the generic bdwlang.elf is what the radio would otherwise pick\)

### 配置

- pong\_wifi=1 and CONFIG\_XNU\_PONG\_WIFI=y
- &amp;pcie0 in dts/liuqin.dts carries the stock PHY sequence; six entries differ from pong and were replaced with liuqin's values \(0x60/0x64, 0x90/0x94/0x98, 0xe3c\)

### 操作步骤

- stage-liuqin-wifi-firmware.py copies the radio images and stages bd\_m81gf.elf under both bdwlang.elf and bdwlan.elf, writes local-inputs.json, and the Wi-Fi build embeds them in kernel.macho; the generic bdwlan.eXX set is left out on purpose.

### 开发经验

- The radio reports qmi-chip-id 18 and qmi-board-id 255, so ath11k asks for bdwlang.elf; the stock set's own bdwlang.elf is Qualcomm's reference calibration, and Xiaomi's bd\_m81gf.elf is the board's.
- The stock device tree shares pong's xo-clk line \(gpio204\) but has its own reset, clkreq and wake lines, which the driver takes as board data.

### 完成条件

- The interface appears and joins a network from SpringBoard.

### 当前范围

- Built into kernel.macho \(run 42788427078\) but never booted: the PCIe link, MHI and the firmware load are untested on this tablet.
- No Bluetooth: fw/bt/ is in the release but no driver uses it yet.

### 下一步

- Boot it, read the ath11k log for the PCIe link and the board-id request, then join a network.

### 证据

- `source`: [Stages amss.bin, amss20.bin, m3.bin, regdb.bin and bd\_m81gf.elf as bdwlang.elf/bdwlan.elf, with the provenance record the Wi-Fi build checks.](https://github.com/document97/UniXNU-liuqin/blob/fe0e8d790e24120970083e20c1a7d9c86cdbb87c/scripts/stage-liuqin-wifi-firmware.py)
- `host`: [kernel.macho carries bdwlang.elf, bdwlan.elf and amss.bin.](https://github.com/Document97/UniXNU-liuqin/actions/runs/42788427078)
  Command: <code>gh workflow run package.yml -R Document97/UniXNU-liuqin --ref liuqin -f os=ipados-18.7.10-22H374 -f prelink=false</code>. Revision: `df2dd999fb24fa462896b0240e4bad2ad6bff1dc`.

## 音频 {#audio}

`planned`

组件: `PongPlatform24`.

### 硬件与依赖

- CS35L41 smart amplifiers \(pong has the TFA9873\) and the ADSP audio path

### 配置

- pong\_audio=0 and pong\_adsp=0 in \[payload\] kernel\_args
- CONFIG\_XNU\_PONG\_POWER=n, so the audio service is off as well

### 操作步骤

- Write a CS35L41 codec layer under the PongAudioService client and enable it together with PongPower, which the audio path depends on.

### 开发经验

- PongAudio is written against the TFA9873 register map and cannot drive the CS35L41 without a new codec layer.
- The audio service needs PongPower, which stays off until liuqin's battery and PMIC readings are checked.

### 完成条件

- The boot chime and media playback come out of the speakers.

### 当前范围

- No audio on the first boot; the ADSP is left off.

### 下一步

- Compare the CS35L41 register sequence of the stock kernel driver with PongAudioService and port it.

### 证据

- `source`: [kernel\_args keep pong\_audio=0 and pong\_adsp=0 for the first boot.](https://github.com/document97/UniXNU-liuqin/blob/fe0e8d790e24120970083e20c1a7d9c86cdbb87c/board.toml)

## 电源 {#power}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- PM8350/PMK8350 family PMICs; PON and PM8350 GPIO6 keys
- Battery and charger state from the ADSP over PMIC GLINK \(SMEM, IPCC, SMP2P 443/429 and the GLINK entries are pong's\)
- ADSP PAS1 at liuqin's own adsp\_region 0x9fd00000/0x3100000 \(pong's 0x85700000 is video on this board\)
- adsp.mdt plus adsp.b00..b25 from the stock release fw/adsp/

### 配置

- pong\_adsp=2 starts PAS1 and the PMIC GLINK battery service; CONFIG\_XNU\_PONG\_POWER=y
- PongAdsp.cpp points at the liuqin adsp\_region; merge-qcom-mdt.py rebuilds one adsp.mbn \(23,708,072 B\) from the split stock form and the userdata step installs it at /pong/firmware
- pong\_buttons=1 keeps power, volume-down and volume-up working without the power service

### 操作步骤

- Merge the signed ADSP segments at their program-header offsets without altering them, stage adsp.mbn into the OS volume, and let PongPower read the battery over GLINK.

### 开发经验

- The split form is the stock one: each adsp.bNN is program header NN's bytes, so the merged image needs no re-signing; segments with no file bytes are skipped.
- PongPower builds without the ramoops console only with the weak pong\_ramoops\_console\_write that 3507c53 added.
- The TFA9873 audio path in PongPower is refused at runtime on this board: liuqin has CS35L41 amplifiers.

### 完成条件

- Charge level and charger state follow the system; the tablet suspends and resumes.

### 当前范围

- Built into kernel.macho \(run 42788427078\) but never booted: PAS1, the GLINK link and the battery readings are untested on this tablet.
- No charging control and no suspend/resume yet.

### 下一步

- Boot it and read the ADSP and battery logs \(pong\_adsp=2\).

### 证据

- `source`: [Rebuilds adsp.mbn from adsp.mdt plus adsp.bNN at the program-header offsets, checking every segment size and copying the hash segment as it is.](https://github.com/document97/UniXNU-liuqin/blob/fe0e8d790e24120970083e20c1a7d9c86cdbb87c/scripts/merge-qcom-mdt.py)
- `host`: [The ADSP merge step verified 26 segments of the stock release and the kernel command line carries pong\_adsp=2.](https://github.com/Document97/UniXNU-liuqin/actions/runs/42788427078)
  Command: <code>gh workflow run package.yml -R Document97/UniXNU-liuqin --ref liuqin -f os=ipados-18.7.10-22H374 -f prelink=false</code>. Revision: `df2dd999fb24fa462896b0240e4bad2ad6bff1dc`.

## 诊断 {#diagnostics}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- The applog ring of the kernel, the DT panic region, and the ramoops region the defconfig records for this board \(0xA7000000\)

### 配置

- pong\_init\_trace=1, applog=1 with launchd, backboardd, SpringBoard, containermanagerd, lsd, runningboardd, logd\_helper and powerd
- CONFIG\_XNU\_PONG\_RAMOOPS\_CONSOLE=y writing at 0xA7000000; \[payload\] panic\_screen is false
- CONFIG\_XNU\_PONG\_VOLATILE\_PANIC\_LOG=n: the 128 KiB fallback buffer is for a kernel without a DT panic region

### 操作步骤

- Read the boot trace through the applog ring; after a panic reboot to Android with Magisk root and read /sys/fs/pstore/console-ramoops-0 and pmsg-ramoops-0, which receive the panic text because the console path records before it checks disableConsoleOutput.

### 开发经验

- 0xA7000000 is not in XNU's managed memory: dts/liuqin.dts declares /memory@840000000 \(5 GiB\), so the 4 GiB owned window starts at 0x840000000 and the console region at 0xA7000000 is far below it, where the kernel never allocates.
- 0xA7000000 is the stock ramoops node of liuqin's dtbo.img \(reg 0x400000, console-size 0x200000, pmsg-size 0x200000\), so Android's pstore driver exposes the buffer as console-ramoops-0 after the tablet reboots; the 12-byte header and the 0x43474244 magic are persistent\_ram\_buffer's.
- The mainline liuqin DTS of the same address exists for this purpose: its comment says the zone sizes deliberately match the vendor firmware's ramoops node so a failed boot is readable from the stock kernel's /sys/fs/pstore, since a retail unit has no debug UART, and that pstore allocates dmesg, console then pmsg in that order, so an extra dmesg zone would move the console and break it. The node carries no ecc-size, mem-type or ftrace-size, so the buffer really is a plain persistent\_ram with console first.
- The firmware memory map puts the region on FD Reserved \(1 MiB\) and UEFI FD \(3 MiB\), both BsData: memory the OS may reclaim after ExitBootServices, and no RtData descriptor lies inside the 4 MiB.
- The pong ramoops address 0x85200000 falls inside the stock PIL reservation of liuqin, which is why the console stayed off until it was repointed.
- PongPower needs pong\_ramoops\_console\_write even with the console off; 3507c53 added a weak default so the build links.
- scripts/patch-xnu-entry-probe.py can patch this kernel: \_start\_first\_cpu, \_panic and \_vinfo are in the symbol table, the entry branches to \_start\_first\_cpu, the SCTLR/ISB/CPACR sequence is at \_start\_first\_cpu+0x2fc and the probe caves after the entry are NOP padding.
- The applog list is trimmed to the services the first-boot trace reads, and the assembled command line stays below 1000 bytes \(785 B in run 42788427078\).
- The cave the panic screen links into is NOP fill in this kernel, not zero fill: patch-xnu-entry-probe.py requires zero fill, so run 43184148347 linked the kernel and then stopped with "Padding at 0xfffffff007fe2518 is not empty"; panic\_screen is off and the ramoops console is the panic channel.

### 完成条件

- A panic and a boot trace can be read from the device without a serial cable.

### 当前范围

- The ramoops console is in the kernel of run 43190178662 and in liuqin-xnu-initial.img, but nothing has read it from the tablet.
- Android's pstore read needs Magisk root on the tablet after the unlock; without it /sys/fs/pstore is unreadable.

### 下一步

- Rebuild without panic\_screen, then boot the image after the unlock and read console-ramoops-0 from Android.

### 证据

- `source`: [RAMOOPS\_CONSOLE=y, VOLATILE\_PANIC\_LOG=n and the 0x85200000 and 0xA7000000 note.](https://github.com/document97/UniXNU-liuqin/blob/fe0e8d790e24120970083e20c1a7d9c86cdbb87c/configs/liuqin_ipados18_defconfig)
- `source`: [/memory@840000000 reg &lt;0x8 0x40000000 0x1 0x40000000&gt;: physBase 0x840000000 and 5 GiB, so the 4 GiB owned window does not reach 0xA7000000.](https://github.com/document97/UniXNU-liuqin/blob/fe0e8d790e24120970083e20c1a7d9c86cdbb87c/dts/liuqin.dts)
- `source`: [kernel.macho of run 42788427078: \_start\_first\_cpu, \_panic and \_vinfo present, the entry branches to \_start\_first\_cpu, the SCTLR/ISB/CPACR sequence is found and the probe cave is empty.](https://github.com/document97/UniXNU-liuqin/blob/fe0e8d790e24120970083e20c1a7d9c86cdbb87c/scripts/check-liuqin-kernel-probe.py)
- `host`: [The kernel links with PONG\_POWER=y and the command line is 785 B.](https://github.com/Document97/UniXNU-liuqin/actions/runs/42788427078)
  Command: <code>gh workflow run package.yml -R Document97/UniXNU-liuqin --ref liuqin -f os=ipados-18.7.10-22H374 -f prelink=false</code>. Revision: `df2dd999fb24fa462896b0240e4bad2ad6bff1dc`.
- `host`: [The kernel linked and carries PONG DIAGNOSTIC v92 and pong\_ramoops\_console, so the ramoops console is in it; the payload step then stopped at patch-xnu-entry-probe.py with Padding at 0xfffffff007fe2518 is not empty.](https://github.com/Document97/UniXNU-liuqin/actions/runs/43184148347)
  Command: <code>gh workflow run package.yml -R Document97/UniXNU-liuqin --ref liuqin -f os=ipados-18.7.10-22H374 -f prelink=false</code>. Revision: `be91815e91470a2d1d0ac27614a2193017121a0d`.
- `host`: [Green end to end: liuqin-xnu-initial.img 102,162,432 bytes, sha256 00f714b24ebc001c, carrying a 30,257,184-byte kernel whose symbol table has \_pong\_ramoops\_console\_init, \_pong\_ramoops\_console\_write and \_pong\_ramoops\_diagnostic\_write as real code \(the run with the console off has only the weak stubs four bytes apart\), and whose strings include PONG DIAGNOSTIC v92 and isolated pmsg recorder ready. The command line is 785 bytes.](https://github.com/Document97/UniXNU-liuqin/actions/runs/43190178662)
  Command: <code>gh workflow run package.yml -R Document97/UniXNU-liuqin --ref liuqin -f os=ipados-18.7.10-22H374 -f prelink=false</code>. Revision: `9050350664864cd84aed8b715cef1c70958242ba`.

</div>
