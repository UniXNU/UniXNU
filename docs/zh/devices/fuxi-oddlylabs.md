# Xiaomi 13 \(OddlyLabs\)

[OddlyLabs/unixnu-fuxi](https://github.com/OddlyLabs/unixnu-fuxi)

<div v-pre>

Xiaomi 13 \(fuxi\). Board files from the UniXNU device template, the FTM5 touch driver and its staged kernel probe; CI builds the kernel, the payload, the DEBUG firmware and the fastboot boot image. On 2026-11-02 the image boots on the device to bsd\_init \(e901139\), and the touch probe's stage 3 reads the controller's chip id 36 40 there.

源记录: [porting.toml](https://github.com/OddlyLabs/unixnu-fuxi/blob/484a6508b6b37c780500a9742f2e2b4cee3cd4a7/porting.toml), `484a6508b6b37c780500a9742f2e2b4cee3cd4a7`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `implemented` |
| [固件与启动](#firmware) | `host-verified` |
| [CPU 与中断](#cpu) | `implemented` |
| [内存与 DMA](#memory) | `implemented` |
| [存储与根卷](#storage) | `planned` |
| [显示](#display) | `planned` |
| [输入](#input) | `implemented` |
| [GPU](#gpu) | `planned` |
| [网络](#network) | `planned` |
| [音频](#audio) | `planned` |
| [电源](#power) | `implemented` |
| [镜像组装](#packaging) | `device-verified` |
| [诊断](#diagnostics) | `implemented` |

## 配置 {#configuration}

`implemented`

组件: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`, `DarwinBoot`.

### 硬件与依赖

- UniXNU examples/device template \(SM8550, iPadOS 17.7.11 profile\).
- UniXNU-sm8550-common at 23b2049fcd9e30356161def84231334fb55ecca9.

### 配置

- board.toml: name fuxi, kit fuxi, soc\_source sm8550, os\_profile ipados-17.7.11-21H461, device\_tree.source device:dts/fuxi.dts.
- configs/fuxi\_defconfig: the template options, CONFIG\_XNU\_NATIVE\_ADRENO off \(the SoC fragment turns it on\), and CONFIG\_XNU\_EXTRA\_LD\_ARCHIVES for the touch archive. The arch fragment sets CONFIG\_XNU\_BUILD\_ARCHIVES, CONFIG\_XNU\_NATIVE\_AES, CONFIG\_XNU\_NATIVE\_ARCH\_TIMER and CONFIG\_XNU\_NATIVE\_PAN; the OS fragment sets CONFIG\_XNU\_SOURCE\_MOCKFS.
- \[kernel\] archives in build order: corecrypto \(plain and namespaced\), ArmDTPlatform, ArmCpu, SoftwareAES and its bindings, libpthread, the mockfs fixture, build-fuxi-touch.py.

### 操作步骤

- ./unixnu defconfig fuxi\_defconfig -D ../unixnu-fuxi
- ./unixnu status --json
- ./unixnu build kernel

### 开发经验

- CI \(.github/workflows/build.yml\) pins OddlyLabs/UniXNU and OddlyLabs/uefi-fuxi at full revisions; after merging upstream into either fork, update UNIXNU\_REF or UEFI\_REF and let the image job run again.
- The image job installs Homebrew's openssl@3 itself rather than relying on the runner image: the encryption step uses OpenSSL 3 \(PBKDF2 for the image, RSA-OAEP with SHA-256 for its key\).
- configs/fuxi\_defconfig sets CONFIG\_XNU\_DT\_PANIC\_REGION. The template and the arch, SoC and OS fragments leave it off, and then the BCM2837 target uses its fixed panic log address \(see memory\); every other SM8550 defconfig in reach \(UniXNU-sheng, Kerfand, MinecraftVM\) sets it. On the device the kernel with it passes PE\_create\_console and reaches bsd\_init \(evidence/2026-11-02-first-boot.md\). The kernel check of the image job fails if PE\_create\_console mentions 0x3c0f.
- configs/fuxi\_defconfig sets CONFIG\_XNU\_SHENG\_PMGR and board.toml adds build-fuxi-platform-power.py to the archives and sheng-pmgr=2 to the boot arguments, as UniXNU-sheng and the community fuxi ports do: AMFI needs an ApplePMGRNub \(see power\).
- The image job also uploads the unpatched prelinked kernel \(gzip\) and payload.json, the kernel encrypted with the image key, so payload variants such as entry-probe images are built without macOS.
- The host tests byte-compile scripts/\*.py and ci/\*.py and parse ci/decrypt-boot-image.sh with bash -n, so the image tools are checked on every push.
- The merged configuration is the arch, SoC and OS fragments followed by the defconfig; the archive list has to cover every archive the merged options require, not only those of the template defconfig.
- CONFIG\_XNU\_SOURCE\_MOCKFS \(OS fragment\) makes vfs\_conf.o reference mockfs, so the link needs build/mockfs-fixture/libmockfs\_fixture.a: the first CI kernel build at 450f518 applied all 62 patches and built every listed archive, then stopped at that missing archive.
- ArmCpu needs the source corecrypto provider, so corecrypto is built before the components, as in UniXNU-sheng.

### 完成条件

- All source pins resolve; every selected component has a record; status shows the intended overrides and patch order.

### 当前范围

- unixnu.lock is not committed yet.

### 下一步

- Run ./unixnu fetch and commit unixnu.lock.

### 证据

- `source`: [Board selection and archive order](https://github.com/OddlyLabs/unixnu-fuxi/blob/484a6508b6b37c780500a9742f2e2b4cee3cd4a7/board.toml)
- `host`: [All sources resolved, 62 patches applied, nine archives built, kernel linked and prelinked](https://github.com/OddlyLabs/unixnu-fuxi/actions/runs/41261795785)
  Command: <code>./unixnu defconfig fuxi_defconfig; ./unixnu build kernel</code>. Revision: `8b4c03f69fc15878d7ee92c0f157215fa235d78d`.

## 固件与启动 {#firmware}

`host-verified`

组件: `DarwinBoot`.

### 硬件与依赖

- OddlyLabs/uefi-fuxi, branch fuxi: a fork of UniXNU/uefi-sheng \(the official Mu-Silicium fork for UniXNU\) with the nine fuxi bring-up commits of matejkoo217/uefi-fuxi cherry-picked \(authors kept, cherry-pick -x\); its fuxiPkg derives from Silicium's SM8550 nuwa \(Xiaomi 13 Pro\).
- fastboot boot of the image \(temporary, nothing is written to the device\).

### 配置

- board.toml \[firmware\]: config fuxi, dsc Platforms/Xiaomi/fuxiPkg/fuxi.dsc, fd Build/fuxiPkg/&\#123;target&\#125;\_CLANGPDB/FV/SILICIUM\_UEFI.fd, and the submodules, edk2 patch and package path list of UniXNU-sheng's \[firmware\].
- fuxi.dsc: FUXI\_VENDOR\_HW = 0 \(Mu drivers only; the previous stage keeps the panel scanning out\), framebuffer 1080x2400x32, DDR base 0x80000000, the UniXNU menu, UniXNUDxe, DarwinBoot, DiskIo, Partition and FAT; FuxiBootMemoryDxe publishes the payload volume the shim hands over.

### 操作步骤

- ./unixnu build firmware --uefi ../uefi-fuxi --target DEBUG \(CI: the image job of .github/workflows/build.yml\).

### 开发经验

- UniXNU provides the boot menu \(UniXNUPkg\) and the XNU loader \(DarwinBoot\) as UEFI modules; the board firmware that runs them on the phone is a Mu-Silicium platform, and upstream Mu-Silicium has no fuxi platform.
- Measured on hardware in matejkoo217/uefi-fuxi: with text offset 0 in the shim's ARM64 header the ABL loads the image and the firmware's DEBUG console prints on the panel; with the firmware address there the ABL answers Load Error.
- The firmware's FdtBlob \(sm8550-xiaomi-fuxi.dtb, model 8550 fuxi, msm-id 0x207, board-id 0x10008\) carries the root properties the ABL selects an appended DTB by; the DTB merged from OS3.0.309 keeps the base DTB's board-id 0 and is not used for the boot image.
- fuxiPkg Include/RAW.inc listed the vendor raw files SecParti.cfg, uefipil.cfg and QcomChargerCfg.cfg outside the FUXI\_VENDOR\_HW gate, so the first firmware build in CI \(run 41268231266 at 72300f2\) stopped at the missing Binaries/nuwa/RawFiles/SecParti.cfg; uefi-fuxi 87554bf9 gates them with their drivers.
- With FUXI\_VENDOR\_HW = 0 the volume holds UniXNU, UniXNUDxe, DarwinBoot, FuxiBootMemoryDxe, SimpleFbDxe, FAT, PartitionDxe and DiskIoDxe. FuxiGopLogDxe and FuxiDisplayDepexDxe are compiled but enter the volume only with USE\_CUSTOM\_DISPLAY\_DRIVER = 1.
- On the device \(2026-11-02, image 931ac958 of run 41273003819\): the ABL accepts the v0 image \(fastboot boot answers OKAY\), the DEBUG firmware log appears on the panel, the UniXNU entry starts DarwinBoot, and DarwinBoot exits boot services and paints its green band. The log ends with SecurityLock LockCapsuleInterface, the normal exit-boot-services message; the DARWINBOOT lines above it are covered by the bands.
- DarwinBoot's hand-off page \(photographed on 2026-11-02\): kernel va 0xFFFFFFF00427C000 at pa 0x8C007C000 \(the start of the 0x8C0000000 run, 2 MiB aligned, plus the kernel's offset in its 2 MiB block\), window 0x130000000, video 0xB8000000 1080x2400 with 4320-byte rows at 32 bpp, EL1, PARange 2 \(40-bit\).
- The firmware of run 41378843724 \(the same code as 627fe52a\) hands over a kernel that reaches bsd\_init and draws its panic screen on the framebuffer DarwinBoot passes \(e901139\).

### 完成条件

- Firmware image builds, enters UniXNU, publishes the framebuffer and preserves the documented memory reservations.

### 当前范围

- The fuxiPkg memory map lists two ranges as conventional memory that are not RAM on this 12 GB unit \(see memory\); nothing is known to have allocated from them, but the map is wrong for this unit. Reservations after the hand-off are not checked.

### 下一步

- Fix the two ranges in the fuxiPkg memory map \(or derive the map from the device tree the ABL passes\), rebuild the firmware and boot the image again.

### 证据

- `source`: [Firmware fork with the fuxi platform](https://github.com/OddlyLabs/uefi-fuxi/tree/fuxi)
- `device`: [ABL Sending OKAY, Booting OKAY \(product fuxi, unlocked, slot a\); panel: DEBUG firmware log, then the DarwinBoot green band](https://github.com/OddlyLabs/unixnu-fuxi/actions/runs/41273003819)
  Command: <code>fastboot boot boot.img</code>. Revision: `2bbd3993e97081db16d8ecc00c58c78f53200b8e`.
- `host`: [DEBUG SILICIUM\_UEFI.fd built at 0x300000 bytes with the UniXNU menu, UniXNUDxe, DarwinBoot and FuxiBootMemoryDxe in the volume](https://github.com/OddlyLabs/uefi-fuxi/commit/87554bf90a6f5707ceeb3720b3dc507de914db94)
  Command: <code>./unixnu build firmware --uefi ../uefi-fuxi --target DEBUG (Ubuntu 26.04, clang 21.1.8, uefi-fuxi 87554bf90a6f5707ceeb3720b3dc507de914db94, UniXNU 6ae4c252937ae1920ab68eaded10fc78447e0194)</code>. Revision: `72300f2b07ccee230e07caa7b31f5af269b4f942`.
- `host`: [DEBUG firmware from uefi-fuxi 87554bf9 built on macOS 26 at 0x300000 bytes \(fd\_sha256 627fe52af360...\) and packed into the boot image](https://github.com/OddlyLabs/unixnu-fuxi/actions/runs/41273003819)
  Command: <code>./unixnu build firmware --uefi ../uefi-fuxi --target DEBUG</code>. Revision: `2bbd3993e97081db16d8ecc00c58c78f53200b8e`.
- `device`: [Firmware log, UniXNU entry, DarwinBoot hand-off \(kernel pa 0x8C007C000, window 0x130000000, video 0xB8000000 1080x2400\); the kernel reaches bsd\_init and its panic screen draws on that framebuffer](https://github.com/OddlyLabs/unixnu-fuxi/blob/484a6508b6b37c780500a9742f2e2b4cee3cd4a7/evidence/2026-11-02-first-boot.md)
  Command: <code>fastboot boot of the run 41378843724 image (SHA-256 e360c41aa4057d27)</code>. Revision: `e90113974b1186120e4eb4c3f77bfb8d909934bf`.

## CPU 与中断 {#cpu}

`implemented`

### 硬件与依赖

- CPU layout and GIC ranges of SM8550 v2 \(soc\_id 519\) from the stock device tree.

### 配置

- The template ArmCpu and ArmDTPlatform selection.

### 操作步骤

- Boot to the XNU entry checkpoint and record the enabled CPUs.

### 开发经验

- On the device the boot CPU runs the XNU entry with the MMU off \(blue band\) and reaches the instruction before the MMU enable \(magenta band\). The image has no reset probe, so nothing marks later progress; no XNU console text and no panic screen appear, and the phone stays off USB. The stop therefore lies between the MMU enable and PE\_init\_printf in arm\_init, the first point that can draw \(xnu d8b80295 arm\_init order: Apple register setup, DT init, ml\_parse\_cpu\_topology, thread and CPU bootstrap, arm\_vm\_init, serial\_init, PE\_create\_console, PE\_init\_printf\).
- Entry-probe resets located the stop \(2026-11-02\): the kernel reaches the MMU enable, arm\_init, cpu\_data\_init, PE\_init\_platform and configure\_misc\_apple\_regs, and never returns from ml\_parse\_cpu\_topology. The ADT gives cpu0-2 cluster-type E and cpu3-7 P \(dts/fuxi.dts, copied from sheng\), so the parser builds two clusters, while BCM2837 keeps MAX\_CPU\_CLUSTERS 1 \(sm8550-common raises only MAX\_CPUS to 8\); the DEVELOPMENT kernel asserts cluster\_id &lt; MAX\_CPU\_CLUSTERS and panics before any console exists. UniXNU-sheng carries the fix as its board patch zzyf-sheng-amp.patch \(\_\_ARM\_AMP\_\_, MAX\_CPU\_CLUSTERS 2, Edge scheduler defaults without a performance controller\); fuxi now carries it unchanged.
- With the AMP patch \(65c4f4e\) the reset probes after ml\_parse\_cpu\_topology, thread\_bootstrap, cpu\_bootstrap, rtclock\_early\_init, kernel\_startup\_bootstrap, timer\_call\_init, cpu\_init, processor\_bootstrap, arm\_vm\_init, serial\_init, kernel\_startup\_initialize\_upto and PE\_create\_console all rebooted the phone. The probe after PE\_init\_printf, the next call, did not \(one run\), and the official image stayed on the bands with no kernel text and no panic screen. The cause was PE\_create\_console's access to the Raspberry Pi panic log address \(see memory\): with CONFIG\_XNU\_DT\_PANIC\_REGION and no other kernel change \(e901139\) the boot reaches bsd\_init. Why the probe after PE\_create\_console still reset is not explained; an asynchronous fault would fit.
- On e901139 the boot CPU runs arm\_init to machine\_startup and on to bsd\_init. Kernel threads, IOSleep, IOMalloc and IODeviceMemory mappings work: the touch probe uses them, and its panic frames are touchThread and Call\_continuation. Only the boot CPU runs: sheng-smp is not set, so ArmCpu does not start the other seven cores.
- Two community fuxi kernels get past this point on the same SoC with the same dram-size and window size: mouse233 \(iPadOS 17.7.11, own firmware with a USB RAM receiver\) and Kerfand \(iOS 16.7.16, the same payload-in-image layout\). Both build the sheng kit; this board builds the template components ArmDTPlatform and ArmCpu.

### 完成条件

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU.

### 当前范围

- Hardware inputs are not recorded in dts/fuxi.dts beyond the SoC DTSI.
- The secondary cores are not started; timer and IPI handling are seen on the boot CPU only.

### 下一步

- Start the secondary cores with sheng-smp=1 armcpu-spi-ipi=1 armcpu-diagnostics=1, the arguments of UniXNU-sheng and ishtar \(SM8550 under Gunyah\), and record which cores come up.

### 证据

- `device`: [Blue band \(XNU entry, MMU off\) and magenta band \(before the MMU enable\) appear; nothing after them](https://github.com/OddlyLabs/unixnu-fuxi/actions/runs/41273003819)
  Command: <code>fastboot boot boot.img</code>. Revision: `2bbd3993e97081db16d8ecc00c58c78f53200b8e`.
- `device`: [Reset 6 s after the MMU enable and after arm\_set\_kernel\_tbi, cpu\_data\_init, PE\_init\_platform and configure\_misc\_apple\_regs in arm\_init \(the phone rebooted to the system each time\); no reset after ml\_parse\_cpu\_topology, processor\_bootstrap, set\_mmu\_ttb or arm\_vm\_init](https://github.com/OddlyLabs/unixnu-fuxi/actions/runs/41363175206)
  Command: <code>fastboot boot of entry-probe reset images (local payloads from the run 41363175206 kernel, firmware 627fe52a)</code>. Revision: `12f9f38d63e4642d335583e159603cfcea2c3744`.
- `device`: [Reset after ml\_parse\_cpu\_topology through PE\_create\_console \(12 images\); no reset after PE\_init\_printf \(one run\); official image: panel photograph shows the three bands and the end of the firmware log, no kernel text, no panic screen, no USB device for 5 min](https://github.com/OddlyLabs/unixnu-fuxi/actions/runs/41372182658)
  Command: <code>fastboot boot of entry-probe reset images and of the official image (run 41372182658, AMP patch)</code>. Revision: `65c4f4e4c59f08e81b6790fe75d4c3eaaf04e794`.
- `device`: [The boot CPU reaches bsd\_init; the touch probe's kernel thread runs and panics with its report \(frames touchThread, Call\_continuation\)](https://github.com/OddlyLabs/unixnu-fuxi/blob/484a6508b6b37c780500a9742f2e2b4cee3cd4a7/evidence/2026-11-02-first-boot.md)
  Command: <code>fastboot boot of the run 41378843724 image (SHA-256 e360c41aa4057d27)</code>. Revision: `e90113974b1186120e4eb4c3f77bfb8d909934bf`.

## 内存与 DMA {#memory}

`implemented`

### 硬件与依赖

- DRAM and reserved-memory nodes of the stock device tree; the apps SMMU at 0x15000000.

### 配置

- dts/fuxi.dts includes sm8550.dtsi and sets model and compatible; package/SmmuBypass.h is the UniXNU-sheng pass-through stream helper the touch probe uses for stream 0xa3.

### 操作步骤

- Fill the memory map from the stock device tree and the firmware's memory map.

### 开发经验

- fuxi and sheng share the touch engine's SMMU stream \(0xa3\).
- The kernel at 65c4f4e had no CONFIG\_XNU\_DT\_PANIC\_REGION, so PE\_create\_console \(check\_for\_panic\_log, xnu d8b80295 pexpert/arm/pe\_init.c\) mapped BCM2837's PLATFORM\_PANIC\_LOG\_PADDR 0x3C0FC000 write-combined, read a word there and called bzero for 16 KiB, before initialize\_screen \(disassembly of the CI kernel\). No RAM range in /proc/iomem and no node of the live device tree covers that address; the nearest nodes are the NSP interconnect at 0x320C0000 and the CDSP at 0x32300000. Three boots ran this code on 2026-11-02 \(probes a2-console and b11-createcons, and the official image\); after each of them the phone booted Android normally \(checked after the third: boot completed, /data mounted\). With CONFIG\_XNU\_DT\_PANIC\_REGION, the only kernel change, the boot reaches bsd\_init \(e901139\), so this access stopped the earlier boots. Whether it faults, hangs or is ignored was not measured.
- At the touch probe's panic the kernel manages 0x127068 pages \(4.61 GiB\) with 0x125ccd free \(vm\_page\_pages, vm\_page\_free\_count\): the 4.75 GiB window minus the kernel image and boot data.
- This unit has 12 GB and its /memory node differs from the firmware map \(from an 8 GB unit\): in the map 0x8B9D00000 + 2 MiB and 0x8BBD00000 up to 0x8BD300000 are conventional memory, but on this phone they are not RAM. UniXNU-sheng records a synchronous external abort from touching such a range at 0x8BB300000, so these holes differ per unit. The window DarwinBoot takes \(0x8C007C000 + 0x130000000\) is inside the /memory node of this phone. Live data: /proc/iomem and /sys/firmware/fdt read with root on OS4.0.0.32.

### 完成条件

- All handoff regions are accounted for and each enabled DMA engine accesses its allocated range with the documented cache policy.

### 当前范围

- The DTS memory map is the SoC default.

### 下一步

- Remove the two ranges above from the fuxiPkg memory map, or derive the map from the device tree the ABL passes, and rebuild the firmware.

### 证据

- `device`: [With CONFIG\_XNU\_DT\_PANIC\_REGION the kernel passes PE\_create\_console and reaches bsd\_init; vm\_page\_pages 0x127068 and vm\_page\_free\_count 0x125ccd at the panic](https://github.com/OddlyLabs/unixnu-fuxi/blob/484a6508b6b37c780500a9742f2e2b4cee3cd4a7/evidence/2026-11-02-first-boot.md)
  Command: <code>fastboot boot of the run 41378843724 image (SHA-256 e360c41aa4057d27)</code>. Revision: `e90113974b1186120e4eb4c3f77bfb8d909934bf`.

## 存储与根卷 {#storage}

`planned`

### 硬件与依赖

- UFS host of SM8550; the GPT of LUN 0 \(userdata\) on the device.

### 配置

- CONFIG\_XNU\_NATIVE\_UFS is not set.

### 操作步骤

- Select a UFS component after the firmware boots.

### 开发经验

- Other fuxi ports report the UFS controller hand-off from the firmware as usable; not reproduced here.

### 完成条件

- Host: register, clock, link and SMMU facts match the board inventory.

### 当前范围

- No storage driver is selected.

### 下一步

- Choose the root path \(RAM root or UFS\) once the firmware boots.

### 证据

按下一步操作收集证据。

## 显示 {#display}

`planned`

### 硬件与依赖

- Panel xiaomi m3 38 0c 0a \(Samsung DDIC by its command set\), 1080x2400, DSI0 command mode with DSC 8 bpp, slices 540x40, 1.1 GHz.
- Splash framebuffer 0xb8000000 \(0x2b00000\), 32 bpp, stride 1080 pixels, the same region as sheng.

### 配置

- package/FuxiPanelBoard.h holds the panel and controller constants with their sources; no display component is selected.

### 操作步骤

- First stage: keep the firmware framebuffer \(GopFramebuffer route\), as sheng does.

### 开发经验

- 73 DSI command sequences of the panel are decoded in facts/panel\_cmds\_\*.txt.
- The PPS in the on-command gives pic\_height 2520 while the timing and page address give 2400; unresolved.

### 完成条件

- A known frame appears with correct geometry and colors, then userland presentation and backlight controls work.

### 当前范围

- No device evidence for display.

### 下一步

- Read the framebuffer the firmware publishes on fuxi \(address, stride, format\).

### 证据

- `source`: [Panel facts with sources \(section 3\)](https://github.com/OddlyLabs/unixnu-fuxi/blob/484a6508b6b37c780500a9742f2e2b4cee3cd4a7/fuxi_touch_panel_porting.md)

## 输入 {#input}

`implemented`

组件: `QcomGeniSpi`, `FuxiFtsTouch`.

### 硬件与依赖

- Stock device tree \(OS3.0.309 vendor\_boot DTB\[2\] with dtbo\[4\], merged with fdtoverlay\): /soc/qcom,qupv3\_1\_geni\_se@ac0000/spi@a90000/fts@0, compatible st,spi, 12 MHz, SPI mode 0.
- Controller ST FingerTip FTM5, chip id 36 40, firmware 53.42 kept in its own flash \(/proc/tp\_fw\_version on Android\), tp-vendor 0x38.
- Bus QUP1 SE4 at 0xa90000, wrapper 0xac0000, SMMU stream 0xa3; pins 44-47 \(qup1\_se4\); interrupt GPIO 25 \(active low, TLMM summary SPI 208\); reset GPIO 24.
- Rails vdd ldob12 1.8 V \(RPMh 0x40900\) and avdd ldom6 3.2 V \(RPMh 0x41b00\), measured with root on Android; their only consumer is spi0.0.

### 配置

- board.toml \[components\] selects QcomGeniSpi and FuxiFtsTouch; \[kernel\] archives runs scripts/build-fuxi-touch.py.
- configs/fuxi\_defconfig links build/fuxi-touch/libFuxiTouch.a through CONFIG\_XNU\_EXTRA\_LD\_ARCHIVES; patches/xnu/fuxi-touch-probe.patch calls native\_touch\_probe\(\) from bsd\_init after IOKitInitializeTime\(\).
- Boot arguments: fuxi-touch=1..4, fuxi-touch-panic=1 or 2, fuxi-touch-hz, fuxi-touch-power, fuxi-touch-tcs, fuxi-touch-poll, fuxi-touch-map. board.toml sets fuxi-touch=3 fuxi-touch-panic=1.

### 操作步骤

- Stage 1: snapshot of the QUP clocks, the pins and the two rails in the command database.
- Stage 2: RPMh votes vdd then avdd in active TCS 2 of apps RSC DRV2 \(tcs-offset 0xd00\), wait 3 ms, vote the QUP clocks, configure the pins.
- Stage 3: GENI SPI at 12 MHz; reset low 10 ms; wait for event 03 \(2 ms polls, 100 ms, three tries, then the ICR 4-wire fallback and the chip id\); read the chip id.
- Stage 4: A0 00 00, 50 ms, A0 00 01; falling-edge interrupt; drain the FIFO; publish contacts in the ShengHidInput ABI.
- Host: run the FuxiFtsTouch tests and tests/board\_test.c \(README\).

### 开发经验

- The fts\_spi driver dispatches events on the high nibble of byte 0, whose bits 2-3 carry the top of the major axis, so 0x13 to 0x1F are all enter events.
- Coordinates are ten times the panel pixels \(fts,support-super-resolution\): 0..10800 x 0..24000; the probe maps them to the 30480 x 20320 range that ShengHidInput scales from.
- Both touch rails stay on while Android runs, also with the screen off, and carry no boot-on property, so the probe votes them before it touches the controller.
- Stage 3 on the device \(e901139, evidence/2026-11-02-first-boot.md\): the command database gives ldob12 0x40900 and ldom6 0x41b00, the RPMh request in TCS 2 returns 0 \(done bit not seen within 10 ms\), the QUP branches run, pins 44-47 read 0x85 0x85 0x85 0x87 \(function 1, 6 mA, CS pulled up\), the reset pin is driven high, GENI is QUP 3.9 at exactly 12 MHz, the controller answers the first reset with CONTROLLER\_READY \(03 00 00\) and reads chip id 36 40, and no SPI transfer failed.

### 完成条件

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive, and buttons produce expected HID reports.

### 当前范围

- Stage 4 \(sensing, interrupt, touch events\) has not run on the device: its first image \(2026-11-02\) ended in AMFI's PMGR panic before a touch was reported, because in stage 4 the probe waits for a touch and AMFI's check comes first \(see power\). Unverified: whether the RPMh votes are needed \(the bootloader may leave both rails on; fuxi-touch-power=0 would tell\), whether the done bit latches without the TCS interrupt, the axis directions, and the HID orientation on a portrait panel.
- GENI has no setting for the 10 us chip-select hold the vendor driver uses \(SPI\_DELAY\_CS\).

### 下一步

- Boot fuxi-touch=4 fuxi-touch-panic=2 and touch the screen once: the probe panics after the first complete touch with its event counters and the last coordinates.

### 证据

- `source`: [FTM5 protocol and contact tracking with host tests](https://github.com/OddlyLabs/FuxiFtsTouch)
- `source`: [Staged board probe](https://github.com/OddlyLabs/unixnu-fuxi/blob/484a6508b6b37c780500a9742f2e2b4cee3cd4a7/package/FuxiTouchProbe.cpp)
- `source`: [Touch facts with sources and the Android measurements \(sections 2 and 6\)](https://github.com/OddlyLabs/unixnu-fuxi/blob/484a6508b6b37c780500a9742f2e2b4cee3cd4a7/fuxi_touch_panel_porting.md)
- `device`: [Stage 3 report on the panic screen: reset status 0 after 1 attempt, last event 03 00 00 \(ready\), chip id 36 40, SPI at 12000000 Hz, no transfer error](https://github.com/OddlyLabs/unixnu-fuxi/blob/484a6508b6b37c780500a9742f2e2b4cee3cd4a7/evidence/2026-11-02-first-boot.md)
  Command: <code>fastboot boot of the run 41378843724 image (SHA-256 e360c41aa4057d27)</code>. Revision: `e90113974b1186120e4eb4c3f77bfb8d909934bf`.

## GPU {#gpu}

`planned`

### 硬件与依赖

- Adreno 740 of SM8550, the same GPU as sheng.

### 配置

- CONFIG\_XNU\_NATIVE\_ADRENO is not set.

### 操作步骤

- Reuse the sheng GPU components after display and storage work.

### 开发经验

- No fuxi GPU observation yet.

### 完成条件

- GPU submissions complete, mapping/fence handling is correct, a known image renders, and the selected Metal client presents it.

### 当前范围

- Not started.

### 下一步

- None before the first boot.

### 证据

按下一步操作收集证据。

## 网络 {#network}

`planned`

### 硬件与依赖

- The Wi-Fi chip of the board, from the stock device tree.

### 配置

- No network component is selected.

### 操作步骤

- Identify the Wi-Fi chip and its bus.

### 开发经验

- No fuxi network observation yet.

### 完成条件

- Scanning, association, address configuration and sustained receive/transmit traffic pass with the selected firmware.

### 当前范围

- Not started.

### 下一步

- None before the first boot.

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`planned`

### 硬件与依赖

- The audio DSP and codec of the board.

### 配置

- No audio component is selected.

### 操作步骤

- Identify the codec and amplifiers from the stock device tree.

### 开发经验

- No fuxi audio observation yet.

### 完成条件

- Each declared route carries the selected audio format through playback or capture and handles start/stop correctly.

### 当前范围

- Not started.

### 下一步

- None before the first boot.

### 证据

按下一步操作收集证据。

## 电源 {#power}

`implemented`

### 硬件与依赖

- RPMh command database \(/sys/kernel/debug/cmd-db on Android\) and the regulator summary with the screen on and off.

### 配置

- package/QcomRpmh.c and QcomRpmh.h are the UniXNU-sheng RPMh helpers; the touch probe uses them for its two rails.
- PMGR bridge for AMFI: package/ShengPlatformPower.cpp is an unchanged copy of UniXNU-sheng's \(08cde20\); scripts/build-fuxi-platform-power.py builds it into build/sheng-platform-power/libShengPlatformPower.a, which build-xnu-4k-baseline.sh force-loads with CONFIG\_XNU\_SHENG\_PMGR=y; the SoC patch sheng-platform-power.patch calls sheng\_pmgr\_run\(\) in bsd\_init after bsd\_bufferinit, and the boot argument sheng-pmgr=2 makes it publish the original ApplePMGRNub with a ShengPlatformPower provider.

### 操作步骤

- Record each rail a driver needs from the command database and the regulator summary.
- PMGR bridge: ci/check-pmgr-bridge.py checks the linked kernel \(the image job runs it after the prelink\).

### 开发经验

- Panel rails vci 3.0 V, vddio 1.8 V and vddd 1.5 V are off while the screen is off; the touch rails stay on.
- Without a PMGR the boot panics with 'AMFI: No PMGR?' at ConfigurationSettings.cpp:235 \(2026-11-02, the first stage 4 image\): AMFI, prelinked unchanged, waits for an ApplePMGRNub service from a thread call. Stage 3 images never showed it because the touch probe panics first, within a second of bsd\_init.
- What AMFI does with the nub \(UniXNU scripts/audit-amfi-pmgr-contract.py, checked in this kernel by ci/check-pmgr-bridge.py\): it reads through the nub, ORs in bit 2 and writes the value back; the nub dispatches to the provider at nub+0x88, slots 320 and 321, and ApplePMGR's own implementations return 0xffffffff and do nothing, as the iPad's AppleT8011PMGR does. No power hardware is involved.
- UniXNU-sheng's build script checks the provider table against a prelinked candidate left by an earlier local build, which a fresh CI tree lacks \(Kerfand published such a kernel as a release asset, which this repository does not do: it holds Apple's kernelcache\). scripts/build-fuxi-platform-power.py keeps every object check and binds slots 320 and 321 to the audited addresses; ci/check-pmgr-bridge.py checks the provider table, the instruction contract and the bsd\_init call in the kernel that ships.

### 完成条件

- Declared power controls and battery readings match observations; each claimed sleep/resume transition restores its dependent peripherals.

### 当前范围

- Only the touch rails are used.
- The PMGR bridge is not power management: every power operation of ShengPlatformPower panics \(ShengPlatformPower: unimplemented operation N\), so anything that asks the PMGR for CPU, clock or sleep control stops the boot with that message.

### 下一步

- Boot the image with the bridge: AMFI should pass, and the touch probe's stage 4 should get its window until the root device wait ends \(60 s\).

### 证据

- `device`: [Panic screen: AMFI: No PMGR? at ConfigurationSettings.cpp:235, from a thread call; no touch report](https://github.com/OddlyLabs/unixnu-fuxi/blob/484a6508b6b37c780500a9742f2e2b4cee3cd4a7/evidence/2026-11-02-first-boot.md)
  Command: <code>fastboot boot of the stage 4 image t4-touch (SHA-256 a43145873cbdfd7e): the run 41378843724 kernel with fuxi-touch=4 fuxi-touch-panic=2</code>. Revision: `d7aaf7d94f7ef6ec44abab4f60f61013a969e374`.
- `source`: [UniXNU-sheng PMGR bridge, unchanged](https://github.com/OddlyLabs/unixnu-fuxi/blob/484a6508b6b37c780500a9742f2e2b4cee3cd4a7/package/ShengPlatformPower.cpp)

## 镜像组装 {#packaging}

`device-verified`

组件: `XnuPrelink`.

### 硬件与依赖

- The iPadOS 17.7.11 restore image of the OS profile \(members fetched with range requests\), a platform seed, the firmware volume, the firmware's FdtBlob.

### 配置

- patches/xnu/series applies zzyf-sheng-amp.patch \(unchanged from UniXNU-sheng 08cde20\) and fuxi-touch-probe.patch after the arch, SoC and OS series.
- \[payload\] kernel\_args set the touch probe stage and its panic report; panic\_screen = true; \[payload.adt\] owned\_memory\_size 0x130000000.
- \[bootimg\] payload = "image" and \[bootimg.image\]: header v0 \(fuxi-legacy.toml's container\), text\_offset 0. The options are in OddlyLabs/UniXNU branch fuxi \(scripts/unixnu/bootimg.py\).

### 操作步骤

- ./unixnu build kernel; ./unixnu build payload --uefi ../uefi-fuxi --unique-chip-id &lt;seed&gt;; ./unixnu build firmware --uefi ../uefi-fuxi --target DEBUG; ./unixnu bootimg --uefi ../uefi-fuxi --target DEBUG --dtb &lt;FdtBlob&gt;.
- CI encrypts boot.img to ci/boot-image-recipient.pem; ci/decrypt-boot-image.sh decrypts it with the owner's private key.
- Probe variants: probe keys in \[payload\] of a scratch copy of board.toml, ./unixnu build payload --kernel &lt;decrypted kernel.macho&gt;, ./unixnu bootimg --fd &lt;firmware volume from check-boot-image.py --fd-out&gt; \(README, probe images\).

### 开发经验

- fuxi-touch-probe.patch keeps only original XNU lines as context, so changes to the shared series around it do not break it.
- Measured on hardware in matejkoo217/uefi-fuxi: the ABL's fastboot boot refuses a header v4 image \(Invalid Parameter\), so the fastboot image uses the v0 container; and the ABL keeps the boot image ramdisk in vendor\_boot, so the payload follows the firmware volume and the image size at header offset 0x10 covers it \(Kerfand: 0x0C300200 for a 192 MiB payload\).
- The first kernel build in CI at 8b4c03f linked and prelinked; bsd\_init calls native\_touch\_probe in the linked kernel.
- The CI image at 2bbd399 advertises image size 0x0C300200 \(shim 0x200, firmware 0x300000, payload 0xC000000\), the value Kerfand measured for a booting 192 MiB payload. gzip brings the whole image to 11.1 MiB because the payload volume is mostly free space.
- The payload's ADT has dram-size 0x80000000 and darwinboot-memory-size 0x130000000, the values of UniXNU-sheng and of both community fuxi ports.
- zzyf-sheng-amp.patch belongs with the E/P cluster types of dts/fuxi.dts: without it the kernel panics in ml\_parse\_cpu\_topology \(see cpu\). Both boards pin sm8550-common 23b2049, so the patch context is the same.
- On the device \(e901139\) the ABL accepts the v0 image, the firmware finds the payload after its volume, the UniXNU menu reads EFI/UniXNU/unixnu.toml from it, and DarwinBoot loads kernel.macho and its ADT: the kernel reaches bsd\_init.
- Probe variants reuse the tested firmware: ci/check-boot-image.py --fd-out writes the firmware volume of a checked image \(627fe52a for run 41273003819\), and ci/decrypt-boot-image.sh writes the unpatched kernel next to the image when the artifact carries it.

### 完成条件

- Kernel and prelink succeed, payload contains all declared inputs, and the boot image matches the bootloader format and size limit.

### 当前范围

- The platform seed in CI is a fixed bring-up value, not the phone's own; replace it before booting to userland.
- Only the path to bsd\_init is exercised: the payload carries no root volume and no Data seed yet.

### 下一步

- Before a payload carries user data, replace the bring-up platform seed with the phone's own \(--unique-chip-id\).

### 证据

- `host`: [Kernel linked and prelinked; bsd\_init calls \_native\_touch\_probe](https://github.com/OddlyLabs/unixnu-fuxi/actions/runs/41261795785)
  Command: <code>./unixnu build kernel --device fuxi</code>. Revision: `8b4c03f69fc15878d7ee92c0f157215fa235d78d`.
- `host`: [boot.img v0, 11677696 bytes \(sha256 931ac9582632...\), uploaded encrypted; decrypted with ci/decrypt-boot-image.sh, ci/check-boot-image.py passes: text offset 0, firmware and 192 MiB FUXIESP payload in the kernel image, FdtBlob appended, kernel.macho with the touch probe, its ADT and the boot arguments of board.toml](https://github.com/OddlyLabs/unixnu-fuxi/actions/runs/41273003819)
  Command: <code>./unixnu build payload --uefi ../uefi-fuxi --unique-chip-id 0x0123456789abcdef; ./unixnu bootimg --uefi ../uefi-fuxi --target DEBUG --dtb &lt;FdtBlob&gt;</code>. Revision: `2bbd3993e97081db16d8ecc00c58c78f53200b8e`.
- `device`: [The image boots: ABL OKAY, firmware and UniXNU menu, DarwinBoot loads kernel.macho and kernel.macho.adt from the payload, the kernel reaches bsd\_init and shows the touch probe report](https://github.com/OddlyLabs/unixnu-fuxi/blob/484a6508b6b37c780500a9742f2e2b4cee3cd4a7/evidence/2026-11-02-first-boot.md)
  Command: <code>fastboot boot of the run 41378843724 image (SHA-256 e360c41aa4057d27)</code>. Revision: `e90113974b1186120e4eb4c3f77bfb8d909934bf`.

## 诊断 {#diagnostics}

`implemented`

### 硬件与依赖

- The panic screen of the payload \(panic\_screen = true\) while no display driver runs.

### 配置

- fuxi-touch-panic=1 ends the boot with a panic whose message is the probe's four diagnostic rows; the rows are also printed to the kernel log at each stage.

### 操作步骤

- Photograph the panic screen and compare the FTS rows with fuxi\_touch\_panel\_porting.md section 7.2.

### 开发经验

- The other fuxi ports read their results from panic screen photographs as well.
- The DEBUG firmware prints its log on the panel before the handoff \(matejkoo217/uefi-fuxi\), the only console before the touch report.
- The earlier ci/ scripts compiled the probe inside a UniXNU-sheng build; the fuxi kernel build replaces them.
- ci/check-boot-image.py checks a decrypted image before fastboot boot against boot.json, board.toml and the firmware checkout: container and load addresses, the shim header, the firmware volume, the payload files, the ADT root and /chosen values, and the boot arguments.
- The panic screen draws through the kernel's frame buffer mapping in vinfo, which initialize\_screen sets at the end of PE\_create\_console, so a panic before that leaves the panel as it was. A reset probe cannot tell its own reset from one caused by the code it wraps.
- The entry probe bands work on this panel: DarwinBoot's green band and the probe's blue and magenta bands appear in order, each 1/16 of the screen height, so the probe's use of the boot-args video geometry is right for fuxi.
- ci/decrypt-boot-image.sh also decrypts the kernel \(kernel.macho.gz.enc\) when the artifact carries it.
- ci/check-pmgr-bridge.py reads the prelinked kernel without tools \(Mach-O segments and symbol table in Python\); with --contract-only it checks only the AMFI -&gt; PMGR contract, which passes on the e901139 kernel.
- The panic screen draws the touch report on fuxi: the probe's four rows, the panic frames and the page counters, below the green and blue bands \(it paints over the magenta band\).

### 完成条件

- Each claimed milestone has a reproducible command, a matching source/image revision and an accessible result.

### 当前范围

- Device records are panel photographs, transcribed in evidence/2026-11-02-first-boot.md; the photographs stay with the owner. No kernel log is kept: there is no serial console, and the ADT has no /pram node, so no panic region survives the reset.

### 下一步

- Capture the stage 4 touch report \(event counters and coordinates\).

### 证据

- `source`: [Panic report and kernel log rows](https://github.com/OddlyLabs/unixnu-fuxi/blob/484a6508b6b37c780500a9742f2e2b4cee3cd4a7/package/FuxiTouchProbe.cpp)
- `device`: [Panel photograph: green, blue and magenta bands, then the end of the firmware log; no kernel text or panic screen; no USB device for 2.5 min](https://github.com/OddlyLabs/unixnu-fuxi/actions/runs/41273003819)
  Command: <code>fastboot boot boot.img</code>. Revision: `2bbd3993e97081db16d8ecc00c58c78f53200b8e`.
- `host`: [The image artifact decrypts with the owner's key \(sha256 matches boot.img.sha256\) and every check passes; a tampered boot.json fails two checks](https://github.com/OddlyLabs/unixnu-fuxi/actions/runs/41273003819)
  Command: <code>bash ci/decrypt-boot-image.sh &lt;key&gt; &lt;artifact&gt;; python3 ci/check-boot-image.py boot.img boot.json ../uefi-fuxi</code>. Revision: `2bbd3993e97081db16d8ecc00c58c78f53200b8e`.
- `device`: [Reset probes located the two stops \(table in the evidence file\); the panic screen shows the touch report](https://github.com/OddlyLabs/unixnu-fuxi/blob/484a6508b6b37c780500a9742f2e2b4cee3cd4a7/evidence/2026-11-02-first-boot.md)
  Command: <code>fastboot boot of 22 reset-probe images and the run 41372182658 and 41378843724 images</code>. Revision: `e90113974b1186120e4eb4c3f77bfb8d909934bf`.

</div>
