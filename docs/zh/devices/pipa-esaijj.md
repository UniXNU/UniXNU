# Xiaomi Pad 6 \(pipa, SM8250-AC\) UniXNU bring-up \(EsaiJJ\)

[EsaiJJ/UniXNU-pipa](https://github.com/EsaiJJ/UniXNU-pipa)

<div v-pre>

Xiaomi Pad 6 \(pipa / SM8250-AC\) porting record for UniXNU iPadOS 17.7.11. The board data comes from the public xVanTuring/UniXNU-pipa and xVanTuring/uefi-pipa ports; this fork's build has not been booted on hardware.

源记录: [porting.toml](https://github.com/EsaiJJ/UniXNU-pipa/blob/7442e5a5f0f1d6c87edc75e7cdc25250b601f7d6/porting.toml), `7442e5a5f0f1d6c87edc75e7cdc25250b601f7d6`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `host-verified` |
| [固件与启动](#firmware) | `implemented` |
| [CPU 与中断](#cpu) | `implemented` |
| [内存与 DMA](#memory) | `implemented` |
| [存储与根卷](#storage) | `implemented` |
| [显示](#display) | `implemented` |
| [输入](#input) | `implemented` |
| [GPU](#gpu) | `implemented` |
| [网络](#network) | `planned` |
| [电源](#power) | `implemented` |
| [镜像组装](#packaging) | `implemented` |
| [诊断](#diagnostics) | `implemented` |
| [音频](#audio) | `planned` |

## 配置 {#configuration}

`host-verified`

组件: `XnuPrelink`, `DarwinBoot`, `SoftwareAES`, `AppleKeyStoreState`.

### 硬件与依赖

- Xiaomi Pad 6 board identity \(SM8250-AC, 16 GB measured unit\), iPadOS 17.7.11 \(21H461 / j120ap\) OS profile, pipa\_defconfig, and device:dts/pipa.dts.

### 配置

- board.toml uses schema\_version = 2, name = pipa, kit = pipa, soc = SM8250, soc\_source = sm8250, os\_profile = ipados-17.7.11-21H461, and device:dts/pipa.dts.
- configs/pipa\_defconfig selects ArmDTPlatform, ArmCpu, SoftwareAES, RamBlock, VirtioMmioBlock \(Verified\), VerifiedRoot, ShengUfs, GopFramebuffer, Adreno 650, BootProgress and PMGR.
- The boot image uses the pipa UEFI values: base 0x10000000, kernel\_offset 0x8000, tags\_offset 0x100, pagesize 2048, header\_version 1.

### 操作步骤

- Run dtc -I dts -O dtb -i socs/sm8250/dts dts/pipa.dts -o /tmp/pipa.dtb, then python3 scripts/check-pipa.py.

### 开发经验

- 2026-11-11 Replaced the TB-J716F board file, defconfig, DTS, patch names and workflow paths with the pipa equivalents; removed the TB-J716F DTS and backlight sources from the build tree.
- 2026-11-10 Read the pipa DRAM banks, userdata window, boot-image parameters and ADT values from xVanTuring/uefi-pipa \(Resources/Configs/pipa.toml, Resources/DTBs/pipa.dts\) and from Android's /memory on the measured 16 GB unit.

### 完成条件

- The board identity, source paths, defconfig and patch series resolve, and the fallback DTB compiles.

### 当前范围

- Only static and host checks have run; nothing in this fork has been booted on a Xiaomi Pad 6.

### 下一步

- Boot the packaged image and record the first pipa hardware evidence.

### 证据

- `host`: [The pipa fallback tree compiles with the shared SM8250 CPU, GICv3, timer and PSCI nodes.](https://github.com/EsaiJJ/UniXNU-pipa/blob/7442e5a5f0f1d6c87edc75e7cdc25250b601f7d6/dts/pipa.dts)
  Command: <code>dtc -I dts -O dtb -i socs/sm8250/dts dts/pipa.dts -o /tmp/pipa.dtb</code>. Revision: `421c34bdcaf116bd15b8a895fa81ee483d4d8f31`.
- `host`: [Stages build/pipa/pipa.dtb from uefi-pipa when available \(or compiles dts/pipa.dts\) and writes build/pipa/check.json with hardware\_boot\_demonstrated = false.](https://github.com/EsaiJJ/UniXNU-pipa/blob/7442e5a5f0f1d6c87edc75e7cdc25250b601f7d6/scripts/check-pipa.py)
  Command: <code>python3 scripts/check-pipa.py</code>. Revision: `421c34bdcaf116bd15b8a895fa81ee483d4d8f31`.

## 固件与启动 {#firmware}

`implemented`

### 硬件与依赖

- Mu-Silicium uefi-pipa platform \(Platforms/Xiaomi/pipaPkg/pipa.dsc, pipa.fdf, Resources/Configs/pipa.toml\) and the pipa UEFI memory map.

### 配置

- board.toml \[firmware\] builds Platforms/Xiaomi/pipaPkg/pipa.dsc and expects Build/pipaPkg/&\#123;target&\#125;\_CLANGPDB/FV/SILICIUM\_UEFI.fd.
- check-pipa.py verifies the dsc/fdf/includes, the pipa.toml \[uefi\_fd\] and \[boot\_image\] values, the page alignment and non-overlap of MemoryMapLib descriptors, and the Binaries/pipa inputs.

### 操作步骤

- Clone xVanTuring/uefi-pipa branch pipa, then run python3 scripts/check-pipa.py with UNIXNU\_UEFI pointing at it.

### 开发经验

- 2026-11-10 Replaced the TB-J716F firmware paths with pipaPkg and the pipa memory descriptors \(UEFI FD 0x9fc00000+0x300000, stack 0x9ff90000+0x40000, display reserved 0x9c000000+0x2400000\).

### 完成条件

- The pipa firmware source builds with UniXNU, the boot memory driver and DarwinBoot added.

### 当前范围

- The uefi-pipa checkout and its Binaries submodule are external; the static firmware checks are skipped when the checkout is absent.

### 下一步

- Run check-pipa.py against a full uefi-pipa checkout and build the FD.

### 证据

- `host`: [Validates the pipa platform files, the pipa.toml boot-image keys, the UEFI FD/stack descriptors and the Resources/DTBs/pipa.dtb splash region.](https://github.com/EsaiJJ/UniXNU-pipa/blob/7442e5a5f0f1d6c87edc75e7cdc25250b601f7d6/scripts/check-pipa.py)
  Command: <code>UNIXNU_UEFI=../uefi-pipa python3 scripts/check-pipa.py</code>. Revision: `421c34bdcaf116bd15b8a895fa81ee483d4d8f31`.

## CPU 与中断 {#cpu}

`implemented`

组件: `ArmCpu`, `ArmDTPlatform`.

### 硬件与依赖

- 8-core Kryo 585 topology \(4x Cortex-A55 at MPIDR 0x000..0x300, 4x Cortex-A77 at 0x400..0x700\), GICv3 \(0x17a00000 / 0x17a60000, stride 0x20000\), PSCI SMC and the 19.2 MHz arch timer.

### 配置

- socs/sm8250/dts/sm8250.dtsi exports the CPU, GICv3, timer and PSCI nodes; board.toml sets sheng-smp=1, armcpu-self-ipi=1, armcpu-spi-ipi=1, armcpu-diagnostics=1 and pipa-cpufreq=1.

### 操作步骤

- Boot with sheng-smp=1 and read the CPU/GIC rows from the ramoops log or the USB CDC-ACM status command.

### 开发经验

- 2026-11-10 Kept the shared SM8250 CPU/GIC/timer facts and the pipa cpufreq governor argument \(pipa-cpufreq=1\); the fork's extra governor mode stays dormant.

### 完成条件

- All 8 cores register with XNU and deliver GICv3 timer/IPI/SPI interrupts.

### 当前范围

- The upstream pipa port reports all 8 cores and cpufreq working on hardware; this fork has not reproduced it.

### 下一步

- Verify the secondary-core bring-up and EPSS clock transitions on hardware.

### 证据

- `host`: [The tree compiles with 8 CPU nodes and the GICv3 redistributor stride.](https://github.com/EsaiJJ/UniXNU-pipa/blob/7442e5a5f0f1d6c87edc75e7cdc25250b601f7d6/socs/sm8250/dts/sm8250.dtsi)
  Command: <code>dtc -I dts -O dtb -i socs/sm8250/dts dts/pipa.dts -o /tmp/pipa.dtb &amp;&amp; fdtget /tmp/pipa.dtb /cpus/cpu@700 compatible</code>. Revision: `421c34bdcaf116bd15b8a895fa81ee483d4d8f31`.

## 内存与 DMA {#memory}

`implemented`

### 硬件与依赖

- Measured 16 GB memory map: 0x80000000+0x37700000, 0xc0000000+0x1c0000000, 0x800000000+0x200000000; owned\_memory\_size 0x170000000; dram\_size 0x980000000.

### 配置

- dts/pipa.dts declares the three banks; board.toml \[payload\] uses dram\_size 0x980000000 and \[payload.adt\] uses dram\_base 0x80000000, dram\_size 0x980000000 and owned\_memory\_size 0x170000000.
- The boot-log reservation is 0xb0000000+0x400000; BootRamoops maps the first 512 KiB.

### 操作步骤

- Compare the /memory banks with Android on the target unit before flashing a different DRAM capacity.

### 开发经验

- 2026-11-10 Replaced the 6 GiB TB-J716F span with the measured pipa banks.

### 完成条件

- XNU receives the pipa DRAM range and the Apps/GPU SMMU mappings cover the devices used by the port.

### 当前范围

- The values describe the measured 16 GB unit; 8 GB units need their own bank list.

### 下一步

- Confirm /memory on the actual target unit.

### 证据

- `source`: [The \[payload\] and \[payload.adt\] DRAM values match the three measured banks \(base 0x80000000, end 0x980000000\).](https://github.com/EsaiJJ/UniXNU-pipa/blob/7442e5a5f0f1d6c87edc75e7cdc25250b601f7d6/board.toml)

## 存储与根卷 {#storage}

`implemented`

组件: `ShengUfs`, `RamBlock`, `VerifiedRoot`, `VirtioMmioBlock`.

### 硬件与依赖

- SM8250 UFS 3.1 host controller at 0x01d84000, Apps SMMU streams 0x0e0 and 0x4e0, and the pipa userdata partition sda34 / LBA 0x293000..0x1d387fa.

### 配置

- ShengUfs keeps the SM8250/pipa GCC registers and both UFS stream IDs; board.toml \[userdata\] uses the pipa GPT window; pipa\_defconfig enables NativeUfs, the Verified virtio block query, VerifiedRoot and the owner chain.
- native-ufs-root=1 and sheng-data-persist=2 are in the pipa kernel arguments.

### 操作步骤

- Build libShengUfs.a through scripts/build-arm-driver.py ShengUfs, then boot and mount the APFS OS, SystemOS and Data volumes.

### 开发经验

- 2026-11-11 Renamed the leftover J716F UFS symbols/files to PipaSmmuTakeover/PipaNativeUfsHost; the stream IDs \(0x0e0, 0x4e0\), host base and userdata window are already pipa's.
- 2026-11-10 Adopted the pipa userdata window \(0x293000..0x1d387fa\) and the pipa root volume UUID.

### 完成条件

- The UFS controller initializes and mounts the iPadOS root, SystemOS and persistent Data volumes.

### 当前范围

- Flashing the userdata image erases Android's data; no pipa storage run exists for this fork.

### 下一步

- Boot with native-ufs-root=1 and check the APFS mount.

### 证据

- `host`: [The SMMU plan uses the SM8250 UFS streams 0x0e0 and 0x4e0, matching the pipa DT's iommus.](https://github.com/EsaiJJ/UniXNU-pipa/blob/7442e5a5f0f1d6c87edc75e7cdc25250b601f7d6/drivers/ShengUfs/PipaSmmuTakeover.h)
  Command: <code>grep -n 'kPipaUfsStreams' drivers/ShengUfs/PipaSmmuTakeover.h</code>. Revision: `421c34bdcaf116bd15b8a895fa81ee483d4d8f31`.

## 显示 {#display}

`implemented`

组件: `GopFramebuffer`.

### 硬件与依赖

- 1800x2880 UEFI GOP scanout at 0x9c000000, the pipa display reserved region 0x9c000000+0x2400000, and the upstream pipa GPU scanout path.

### 配置

- board.toml sets CONFIG\_XNU\_NATIVE\_LEGACY\_DISPLAY, display-scale = 2, display-rotation = 0, sheng-vsync=60 and sheng-fb-gpu=1; the GOP frame buffer and the GPU copy\_rows presenter are built into libNativeLegacyDisplay.late.a.

### 操作步骤

- Boot with the pipa UEFI GOP initialized and check the framebuffer rows and the scanout copy in the log.

### 开发经验

- 2026-11-10 Set the pipa 1800x2880 GOP aperture and UI scale; removed the TB-J716F RM692E6 backlight sources from the archive.
- The KTZ8866 brightness controller \(I2C11 0x11, enable GPIO139\) is not ported, so sheng-backlight stays unset and the panel brightness is whatever the firmware left.

### 完成条件

- WindowServer presents the desktop through the GOP framebuffer with GPU scanout copies.

### 当前范围

- No runtime brightness control and no native MDSS mode setting; the bootloader's panel state is used.

### 下一步

- Port the KTZ8866 backlight driver and then enable sheng-backlight.

### 证据

- `host`: [The builder no longer copies or compiles AppleARMBacklight.cpp / BacklightProbe.cpp; the backlight symbols stay weak in the other objects.](https://github.com/EsaiJJ/UniXNU-pipa/blob/7442e5a5f0f1d6c87edc75e7cdc25250b601f7d6/scripts/build-gop-legacy-display.py)
  Command: <code>python3 -m py_compile scripts/build-gop-legacy-display.py</code>. Revision: `421c34bdcaf116bd15b8a895fa81ee483d4d8f31`.

## 输入 {#input}

`implemented`

组件: `ShengHidInput`, `ShengNovatekTouch`, `QcomGeniSpi`.

### 硬件与依赖

- Novatek NT36532 on QUPv3\_0 SE4 GENI SPI \(0x990000, wrapper 0x9c0000, 9.6 MHz, IRQ GPIO39 rising, CS 11, reset GPIO33, 40x60 matrix, coordinates 0..17999 x 0..28799\) and the PM8150 PON keys \(kpdpwr, resin, GPIO6 volume up\).

### 配置

- board.toml sets pipa-touch=5, pipa-buttons=1, sheng-touch-hid=1, offline-hid-input=1 and offline-hid-home=1.
- The NT36532 point-report firmware \(novatek\_nt36532\_m82\_fw\_tm.bin\) is embedded by the archive builder; Buttons.c is the pipa version without the TB-J716F volume-key swipe injection.

### 操作步骤

- Boot with pipa-touch=5, then test multi-touch, the on-screen keyboard and the Power/Volume keys.

### 开发经验

- 2026-11-10 Replaced the Goodix GT7386 I2C driver with the pipa Novatek NT36532 GENI SPI path \(TouchBoard.h, TouchProbe.cpp, NvtProtocol, NvtTouchCore, GeniSpi\) and the upstream pipa Buttons.c.

### 完成条件

- Touch reports reach IOHIDFamily and the PON keys generate power/volume events.

### 当前范围

- The reference port reports touch working on hardware; this fork's integration is untested and the touch firmware is not in the tree.

### 下一步

- Boot and verify the axes, the 40x60 matrix and the attention-line timing.

### 证据

- `host`: [The GENI SPI register-model test and the Novatek protocol/point-report/touch-core host tests pass; hardware is not involved.](https://github.com/EsaiJJ/UniXNU-pipa/blob/7442e5a5f0f1d6c87edc75e7cdc25250b601f7d6/drivers/QcomGeniSpi/Test/geni-spi.c)
  Command: <code>gcc -std=c11 -O2 -Wall -Wextra -Werror drivers/QcomGeniSpi/Test/geni-spi.c drivers/QcomGeniSpi/GeniSpi.c -o /tmp/geni-spi &amp;&amp; /tmp/geni-spi</code>. Revision: `421c34bdcaf116bd15b8a895fa81ee483d4d8f31`.

## GPU {#gpu}

`implemented`

组件: `AdrenoPM4`, `AdrenoFirmware`, `ArmSmmu4K`, `AirNir`.

### 硬件与依赖

- Adreno 650 \(chip id 0x06050002\), GMU firmware a650\_gmu.bin, SQE a650\_sqe.fw and the TZ PAS 13 zap shader a650\_zap.elf.

### 配置

- board.toml sets pipa-gpu=12, sheng-gpu-addon=1 and sheng-fb-gpu=1; pipa\_defconfig enables CONFIG\_XNU\_NATIVE\_ADRENO with libAdreno650.a.
- GpuProbe keeps the upstream pipa defaults: Turnip "nocb", the upstream sandbox grant list, and no GPU DCVS block.

### 操作步骤

- Run pipa-gpu=12 with the GPU addon, then exercise SpringBoard/Settings and read the gpu.status counters.

### 开发经验

- 2026-11-10 Adopted the upstream pipa GpuProbe.cpp, NativeBatteryBoard.h, and the pipa GPU addon script name; the pipa GPU defaults replace the TB-J716F DCVS/backlight add-on.

### 完成条件

- The Adreno 650 KMD, GMU, GPU SMMU and NativeAdrenoMetal/Turnip render the desktop.

### 当前范围

- No pipa GPU run in this fork; GMU/SQE/zap firmware files are external.

### 下一步

- Boot pipa-gpu=12 on hardware and capture the GPU log rows.

### 证据

- `source`: [Uses the Adreno 650 chip id, GMEM geometry, hwcg and a650\_protect tables from the upstream pipa port; no TB-J716F-only DCVS block is compiled.](https://github.com/EsaiJJ/UniXNU-pipa/blob/7442e5a5f0f1d6c87edc75e7cdc25250b601f7d6/package/GpuProbe.cpp)

## 网络 {#network}

`planned`

组件: `Ath12kWifi`, `QcaBluetooth`.

### 硬件与依赖

- QCA6390 Wi-Fi on PCIe0 and Bluetooth on QUPv3\_0 SE6 GENI UART; BRCM/WCNSS board data and firmware from the pipa vendor partitions.

### 配置

- The Wi-Fi/Bluetooth sources remain in the tree but board.toml does not set sheng-wifi or sheng-bluetooth, so neither driver starts.
- proprietary-files.txt records the expected images and leaves their pipa digests UNMEASURED.

### 操作步骤

- Only after the base port boots: extract the QCA6390 firmware, confirm the pipa rails/pins, then set sheng-wifi=4 / sheng-bluetooth=1.

### 开发经验

- 2026-11-11 Kept the TB-J716F QCA6390 implementation as an unverified carry-over; the pipa DT's pins \(WLAN\_EN GPIO20, BT\_EN GPIO21, PERST GPIO79, PCIe0 CLKREQ GPIO80, BT SW\_CTRL GPIO124\) match the probe's constants, but nothing has been run.

### 完成条件

- en0/wifid and BlueTool/bluetoothd start on the QCA6390.

### 当前范围

- Default-off and unverified; the QCA6390 firmware is not in the tree.

### 下一步

- Extract and hash the QCA6390 firmware, then validate the rail/pin sequence on pipa.

### 证据

按下一步操作收集证据。

## 电源 {#power}

`implemented`

### 硬件与依赖

- PM8150B fuel gauge \(SID 2, 0x4000..0x4400\), SMB5 charger and the 8840 mAh pipa pack.

### 配置

- NativeBatteryBoard.h uses BAT\_DESIGN\_MAH 8840; NativeBattery and ShengPlatformPower build into the boot-progress and platform-power archives.

### 操作步骤

- Read IOPMPowerSource or the USB battery.status command and compare with Android.

### 开发经验

- 2026-11-10 Replaced the TB-J716F battery board values with the pipa 8840 mAh profile and renamed the optional diagnostic argument to pipa-battery.

### 完成条件

- The status bar and Settings show a live pipa battery percentage and charging state.

### 当前范围

- No pipa hardware reading yet.

### 下一步

- Compare the gauge with Android over a charge/discharge cycle.

### 证据

- `host`: [The PM8150B gauge/charger decoding \(SOC ramp, voltage, current, temperature, charge stage\) passes against Android's recorded values; no hardware is read.](https://github.com/EsaiJJ/UniXNU-pipa/blob/7442e5a5f0f1d6c87edc75e7cdc25250b601f7d6/package/NativeBatteryTests.c)
  Command: <code>gcc -std=c11 -Wall -Wextra -Werror -I package package/NativeBatteryTests.c -o /tmp/pipa-battery &amp;&amp; /tmp/pipa-battery</code>. Revision: `421c34bdcaf116bd15b8a895fa81ee483d4d8f31`.

## 镜像组装 {#packaging}

`implemented`

组件: `XnuPrelink`, `DarwinBoot`.

### 硬件与依赖

- The prelinked iPadOS 17.7.11 kernel, Format 2 ADT, trust caches, the pipa DTB, the NGPUADD2 addon and the UEFI FD.

### 配置

- scripts/package.sh drives ./unixnu release with the pipa defconfig and build/pipa/pipa.dtb; the payload volume is PIPAESP and the image uses Android header v1.

### 操作步骤

- Run bash scripts/package.sh --no-deps --uefi ../uefi-pipa with UNIXNU\_UNIQUE\_CHIP\_ID set.

### 开发经验

- 2026-11-11 Added scripts/extract-pipa-firmware.py, which pulls /vendor, modem and Bluetooth firmware from a booted pipa, records the ROM fingerprint as provenance and writes a SHA-256 manifest for proprietary-files.txt; it deliberately leaves the built-in Novatek image UNMEASURED.
- 2026-11-11 Renamed the pipa patch series, updated the GitHub workflows to xVanTuring/uefi-pipa and UniXNU/out/pipa, and added the pipa DTB and driver checks to CI.

### 完成条件

- One command builds the kernel, archives, firmware, payload and boot.img.

### 当前范围

- The build needs the external UniXNU and uefi-pipa checkouts plus the firmware caches.

### 下一步

- Run the package workflow and flash boot.img to slot B.

### 证据

- `host`: [Compiles dts/pipa.dts, validates board.toml and proprietary-files.txt, and runs the GopFramebuffer, QcomRpmh, QcomGeniSpi and ShengNovatekTouch host tests.](https://github.com/EsaiJJ/UniXNU-pipa/blob/7442e5a5f0f1d6c87edc75e7cdc25250b601f7d6/.github/workflows/xnu-source-macos.yml)
  Command: <code>Run the Pipa XNU source checks workflow</code>. Revision: `421c34bdcaf116bd15b8a895fa81ee483d4d8f31`.
- `host`: [The extractor parses and exits with a clear error when no adb device is present; it has not run against a tablet, so no firmware digest is claimed yet.](https://github.com/EsaiJJ/UniXNU-pipa/blob/7442e5a5f0f1d6c87edc75e7cdc25250b601f7d6/scripts/extract-pipa-firmware.py)
  Command: <code>python3 -m py_compile scripts/extract-pipa-firmware.py</code>. Revision: `efd421170a2b99be7f5146d6b678d696f8f23abd`.

## 诊断 {#diagnostics}

`implemented`

### 硬件与依赖

- SM8250 DWC3 USB0 at 0x0a600000, HS PHY 0x88e3000, EUD 0x88e1000, PS\_HOLD 0xc264000 and the ramoops zone at 0xb0000000.

### 配置

- USB diagnostics use the PIPA\_ macros, the pipa-usb boot argument and the Xiaomi Pad 6 strings; PS\_HOLD is 0xc264000.
- BootRamoops parses pipa-restart-after, pipa-panic-restart-after, pipa-restart-crashes and pipa-cpufreq.

### 操作步骤

- Boot with pipa-usb=1 and connect the CDC-ACM interface, or read the ramoops zone with scripts/read-pipa-log.py.

### 开发经验

- 2026-11-11 Renamed the USB diagnostics from J716F/TB-J716F to PIPA/Xiaomi Pad 6 and pointed the touch diagnostic at native\_touch\_stage\_done.

### 完成条件

- A live USB console and a persistent ramoops log exist for bring-up.

### 当前范围

- The USB path is default-off and unverified on pipa; the ramoops reader is host-side only.

### 下一步

- Enable pipa-usb=1 on the first hardware round and capture the log.

### 证据

- `source`: [The ramoops writer keeps 512 KiB of the pipa boot-log region at 0xb0000000, parses the pipa-restart-\* arguments, and preserves the zone across the warm reset into fastboot.](https://github.com/EsaiJJ/UniXNU-pipa/blob/7442e5a5f0f1d6c87edc75e7cdc25250b601f7d6/package/BootRamoops.c)

## 音频 {#audio}

`planned`

### 硬件与依赖

- Qualcomm ADSP PAS, SoundWire and the pipa codec/amplifier topology.

### 配置

- No audio driver or boot argument is enabled.

### 操作步骤

- Implement ADSP remoteproc/GPR audio or USB audio first.

### 开发经验

- 2026-11-11 Left audio out of the first pipa port; the TB-J716F CS35L41 manifest entries were removed because they do not describe pipa's amplifiers.

### 完成条件

- IOAudio2Family outputs PCM audio to the speakers or headphones.

### 当前范围

- Not started.

### 下一步

- Identify the pipa codec/amplifier parts and their firmware.

### 证据

按下一步操作收集证据。

</div>
