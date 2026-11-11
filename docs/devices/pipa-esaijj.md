# Xiaomi Pad 6 \(pipa, SM8250-AC\) UniXNU bring-up \(EsaiJJ\)

[EsaiJJ/UniXNU-pipa](https://github.com/EsaiJJ/UniXNU-pipa)

<div v-pre>

Xiaomi Pad 6 \(pipa / SM8250-AC\) porting record for UniXNU iPadOS 17.7.11. The board data comes from the public xVanTuring/UniXNU-pipa and xVanTuring/uefi-pipa ports; this fork's build has not been booted on hardware.

Source record: [porting.toml](https://github.com/EsaiJJ/UniXNU-pipa/blob/7442e5a5f0f1d6c87edc75e7cdc25250b601f7d6/porting.toml), `7442e5a5f0f1d6c87edc75e7cdc25250b601f7d6`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `host-verified` |
| [Firmware and boot](#firmware) | `implemented` |
| [CPU and interrupts](#cpu) | `implemented` |
| [Memory and DMA](#memory) | `implemented` |
| [Storage and root](#storage) | `implemented` |
| [Display](#display) | `implemented` |
| [Input](#input) | `implemented` |
| [GPU](#gpu) | `implemented` |
| [Network](#network) | `planned` |
| [Power](#power) | `implemented` |
| [Image assembly](#packaging) | `implemented` |
| [Diagnostics](#diagnostics) | `implemented` |
| [Audio](#audio) | `planned` |

## Configuration {#configuration}

`host-verified`

Components: `XnuPrelink`, `DarwinBoot`, `SoftwareAES`, `AppleKeyStoreState`.

### Hardware and dependencies

- Xiaomi Pad 6 board identity \(SM8250-AC, 16 GB measured unit\), iPadOS 17.7.11 \(21H461 / j120ap\) OS profile, pipa\_defconfig, and device:dts/pipa.dts.

### Configuration

- board.toml uses schema\_version = 2, name = pipa, kit = pipa, soc = SM8250, soc\_source = sm8250, os\_profile = ipados-17.7.11-21H461, and device:dts/pipa.dts.
- configs/pipa\_defconfig selects ArmDTPlatform, ArmCpu, SoftwareAES, RamBlock, VirtioMmioBlock \(Verified\), VerifiedRoot, ShengUfs, GopFramebuffer, Adreno 650, BootProgress and PMGR.
- The boot image uses the pipa UEFI values: base 0x10000000, kernel\_offset 0x8000, tags\_offset 0x100, pagesize 2048, header\_version 1.

### Procedure

- Run dtc -I dts -O dtb -i socs/sm8250/dts dts/pipa.dts -o /tmp/pipa.dtb, then python3 scripts/check-pipa.py.

### Development findings

- 2026-11-11 Replaced the TB-J716F board file, defconfig, DTS, patch names and workflow paths with the pipa equivalents; removed the TB-J716F DTS and backlight sources from the build tree.
- 2026-11-10 Read the pipa DRAM banks, userdata window, boot-image parameters and ADT values from xVanTuring/uefi-pipa \(Resources/Configs/pipa.toml, Resources/DTBs/pipa.dts\) and from Android's /memory on the measured 16 GB unit.

### Completion criteria

- The board identity, source paths, defconfig and patch series resolve, and the fallback DTB compiles.

### Current limits

- Only static and host checks have run; nothing in this fork has been booted on a Xiaomi Pad 6.

### Next action

- Boot the packaged image and record the first pipa hardware evidence.

### Evidence

- `host`: [The pipa fallback tree compiles with the shared SM8250 CPU, GICv3, timer and PSCI nodes.](https://github.com/EsaiJJ/UniXNU-pipa/blob/7442e5a5f0f1d6c87edc75e7cdc25250b601f7d6/dts/pipa.dts)
  Command: <code>dtc -I dts -O dtb -i socs/sm8250/dts dts/pipa.dts -o /tmp/pipa.dtb</code>. Revision: `421c34bdcaf116bd15b8a895fa81ee483d4d8f31`.
- `host`: [Stages build/pipa/pipa.dtb from uefi-pipa when available \(or compiles dts/pipa.dts\) and writes build/pipa/check.json with hardware\_boot\_demonstrated = false.](https://github.com/EsaiJJ/UniXNU-pipa/blob/7442e5a5f0f1d6c87edc75e7cdc25250b601f7d6/scripts/check-pipa.py)
  Command: <code>python3 scripts/check-pipa.py</code>. Revision: `421c34bdcaf116bd15b8a895fa81ee483d4d8f31`.

## Firmware and boot {#firmware}

`implemented`

### Hardware and dependencies

- Mu-Silicium uefi-pipa platform \(Platforms/Xiaomi/pipaPkg/pipa.dsc, pipa.fdf, Resources/Configs/pipa.toml\) and the pipa UEFI memory map.

### Configuration

- board.toml \[firmware\] builds Platforms/Xiaomi/pipaPkg/pipa.dsc and expects Build/pipaPkg/&\#123;target&\#125;\_CLANGPDB/FV/SILICIUM\_UEFI.fd.
- check-pipa.py verifies the dsc/fdf/includes, the pipa.toml \[uefi\_fd\] and \[boot\_image\] values, the page alignment and non-overlap of MemoryMapLib descriptors, and the Binaries/pipa inputs.

### Procedure

- Clone xVanTuring/uefi-pipa branch pipa, then run python3 scripts/check-pipa.py with UNIXNU\_UEFI pointing at it.

### Development findings

- 2026-11-10 Replaced the TB-J716F firmware paths with pipaPkg and the pipa memory descriptors \(UEFI FD 0x9fc00000+0x300000, stack 0x9ff90000+0x40000, display reserved 0x9c000000+0x2400000\).

### Completion criteria

- The pipa firmware source builds with UniXNU, the boot memory driver and DarwinBoot added.

### Current limits

- The uefi-pipa checkout and its Binaries submodule are external; the static firmware checks are skipped when the checkout is absent.

### Next action

- Run check-pipa.py against a full uefi-pipa checkout and build the FD.

### Evidence

- `host`: [Validates the pipa platform files, the pipa.toml boot-image keys, the UEFI FD/stack descriptors and the Resources/DTBs/pipa.dtb splash region.](https://github.com/EsaiJJ/UniXNU-pipa/blob/7442e5a5f0f1d6c87edc75e7cdc25250b601f7d6/scripts/check-pipa.py)
  Command: <code>UNIXNU_UEFI=../uefi-pipa python3 scripts/check-pipa.py</code>. Revision: `421c34bdcaf116bd15b8a895fa81ee483d4d8f31`.

## CPU and interrupts {#cpu}

`implemented`

Components: `ArmCpu`, `ArmDTPlatform`.

### Hardware and dependencies

- 8-core Kryo 585 topology \(4x Cortex-A55 at MPIDR 0x000..0x300, 4x Cortex-A77 at 0x400..0x700\), GICv3 \(0x17a00000 / 0x17a60000, stride 0x20000\), PSCI SMC and the 19.2 MHz arch timer.

### Configuration

- socs/sm8250/dts/sm8250.dtsi exports the CPU, GICv3, timer and PSCI nodes; board.toml sets sheng-smp=1, armcpu-self-ipi=1, armcpu-spi-ipi=1, armcpu-diagnostics=1 and pipa-cpufreq=1.

### Procedure

- Boot with sheng-smp=1 and read the CPU/GIC rows from the ramoops log or the USB CDC-ACM status command.

### Development findings

- 2026-11-10 Kept the shared SM8250 CPU/GIC/timer facts and the pipa cpufreq governor argument \(pipa-cpufreq=1\); the fork's extra governor mode stays dormant.

### Completion criteria

- All 8 cores register with XNU and deliver GICv3 timer/IPI/SPI interrupts.

### Current limits

- The upstream pipa port reports all 8 cores and cpufreq working on hardware; this fork has not reproduced it.

### Next action

- Verify the secondary-core bring-up and EPSS clock transitions on hardware.

### Evidence

- `host`: [The tree compiles with 8 CPU nodes and the GICv3 redistributor stride.](https://github.com/EsaiJJ/UniXNU-pipa/blob/7442e5a5f0f1d6c87edc75e7cdc25250b601f7d6/socs/sm8250/dts/sm8250.dtsi)
  Command: <code>dtc -I dts -O dtb -i socs/sm8250/dts dts/pipa.dts -o /tmp/pipa.dtb &amp;&amp; fdtget /tmp/pipa.dtb /cpus/cpu@700 compatible</code>. Revision: `421c34bdcaf116bd15b8a895fa81ee483d4d8f31`.

## Memory and DMA {#memory}

`implemented`

### Hardware and dependencies

- Measured 16 GB memory map: 0x80000000+0x37700000, 0xc0000000+0x1c0000000, 0x800000000+0x200000000; owned\_memory\_size 0x170000000; dram\_size 0x980000000.

### Configuration

- dts/pipa.dts declares the three banks; board.toml \[payload\] uses dram\_size 0x980000000 and \[payload.adt\] uses dram\_base 0x80000000, dram\_size 0x980000000 and owned\_memory\_size 0x170000000.
- The boot-log reservation is 0xb0000000+0x400000; BootRamoops maps the first 512 KiB.

### Procedure

- Compare the /memory banks with Android on the target unit before flashing a different DRAM capacity.

### Development findings

- 2026-11-10 Replaced the 6 GiB TB-J716F span with the measured pipa banks.

### Completion criteria

- XNU receives the pipa DRAM range and the Apps/GPU SMMU mappings cover the devices used by the port.

### Current limits

- The values describe the measured 16 GB unit; 8 GB units need their own bank list.

### Next action

- Confirm /memory on the actual target unit.

### Evidence

- `source`: [The \[payload\] and \[payload.adt\] DRAM values match the three measured banks \(base 0x80000000, end 0x980000000\).](https://github.com/EsaiJJ/UniXNU-pipa/blob/7442e5a5f0f1d6c87edc75e7cdc25250b601f7d6/board.toml)

## Storage and root {#storage}

`implemented`

Components: `ShengUfs`, `RamBlock`, `VerifiedRoot`, `VirtioMmioBlock`.

### Hardware and dependencies

- SM8250 UFS 3.1 host controller at 0x01d84000, Apps SMMU streams 0x0e0 and 0x4e0, and the pipa userdata partition sda34 / LBA 0x293000..0x1d387fa.

### Configuration

- ShengUfs keeps the SM8250/pipa GCC registers and both UFS stream IDs; board.toml \[userdata\] uses the pipa GPT window; pipa\_defconfig enables NativeUfs, the Verified virtio block query, VerifiedRoot and the owner chain.
- native-ufs-root=1 and sheng-data-persist=2 are in the pipa kernel arguments.

### Procedure

- Build libShengUfs.a through scripts/build-arm-driver.py ShengUfs, then boot and mount the APFS OS, SystemOS and Data volumes.

### Development findings

- 2026-11-11 Renamed the leftover J716F UFS symbols/files to PipaSmmuTakeover/PipaNativeUfsHost; the stream IDs \(0x0e0, 0x4e0\), host base and userdata window are already pipa's.
- 2026-11-10 Adopted the pipa userdata window \(0x293000..0x1d387fa\) and the pipa root volume UUID.

### Completion criteria

- The UFS controller initializes and mounts the iPadOS root, SystemOS and persistent Data volumes.

### Current limits

- Flashing the userdata image erases Android's data; no pipa storage run exists for this fork.

### Next action

- Boot with native-ufs-root=1 and check the APFS mount.

### Evidence

- `host`: [The SMMU plan uses the SM8250 UFS streams 0x0e0 and 0x4e0, matching the pipa DT's iommus.](https://github.com/EsaiJJ/UniXNU-pipa/blob/7442e5a5f0f1d6c87edc75e7cdc25250b601f7d6/drivers/ShengUfs/PipaSmmuTakeover.h)
  Command: <code>grep -n 'kPipaUfsStreams' drivers/ShengUfs/PipaSmmuTakeover.h</code>. Revision: `421c34bdcaf116bd15b8a895fa81ee483d4d8f31`.

## Display {#display}

`implemented`

Components: `GopFramebuffer`.

### Hardware and dependencies

- 1800x2880 UEFI GOP scanout at 0x9c000000, the pipa display reserved region 0x9c000000+0x2400000, and the upstream pipa GPU scanout path.

### Configuration

- board.toml sets CONFIG\_XNU\_NATIVE\_LEGACY\_DISPLAY, display-scale = 2, display-rotation = 0, sheng-vsync=60 and sheng-fb-gpu=1; the GOP frame buffer and the GPU copy\_rows presenter are built into libNativeLegacyDisplay.late.a.

### Procedure

- Boot with the pipa UEFI GOP initialized and check the framebuffer rows and the scanout copy in the log.

### Development findings

- 2026-11-10 Set the pipa 1800x2880 GOP aperture and UI scale; removed the TB-J716F RM692E6 backlight sources from the archive.
- The KTZ8866 brightness controller \(I2C11 0x11, enable GPIO139\) is not ported, so sheng-backlight stays unset and the panel brightness is whatever the firmware left.

### Completion criteria

- WindowServer presents the desktop through the GOP framebuffer with GPU scanout copies.

### Current limits

- No runtime brightness control and no native MDSS mode setting; the bootloader's panel state is used.

### Next action

- Port the KTZ8866 backlight driver and then enable sheng-backlight.

### Evidence

- `host`: [The builder no longer copies or compiles AppleARMBacklight.cpp / BacklightProbe.cpp; the backlight symbols stay weak in the other objects.](https://github.com/EsaiJJ/UniXNU-pipa/blob/7442e5a5f0f1d6c87edc75e7cdc25250b601f7d6/scripts/build-gop-legacy-display.py)
  Command: <code>python3 -m py_compile scripts/build-gop-legacy-display.py</code>. Revision: `421c34bdcaf116bd15b8a895fa81ee483d4d8f31`.

## Input {#input}

`implemented`

Components: `ShengHidInput`, `ShengNovatekTouch`, `QcomGeniSpi`.

### Hardware and dependencies

- Novatek NT36532 on QUPv3\_0 SE4 GENI SPI \(0x990000, wrapper 0x9c0000, 9.6 MHz, IRQ GPIO39 rising, CS 11, reset GPIO33, 40x60 matrix, coordinates 0..17999 x 0..28799\) and the PM8150 PON keys \(kpdpwr, resin, GPIO6 volume up\).

### Configuration

- board.toml sets pipa-touch=5, pipa-buttons=1, sheng-touch-hid=1, offline-hid-input=1 and offline-hid-home=1.
- The NT36532 point-report firmware \(novatek\_nt36532\_m82\_fw\_tm.bin\) is embedded by the archive builder; Buttons.c is the pipa version without the TB-J716F volume-key swipe injection.

### Procedure

- Boot with pipa-touch=5, then test multi-touch, the on-screen keyboard and the Power/Volume keys.

### Development findings

- 2026-11-10 Replaced the Goodix GT7386 I2C driver with the pipa Novatek NT36532 GENI SPI path \(TouchBoard.h, TouchProbe.cpp, NvtProtocol, NvtTouchCore, GeniSpi\) and the upstream pipa Buttons.c.

### Completion criteria

- Touch reports reach IOHIDFamily and the PON keys generate power/volume events.

### Current limits

- The reference port reports touch working on hardware; this fork's integration is untested and the touch firmware is not in the tree.

### Next action

- Boot and verify the axes, the 40x60 matrix and the attention-line timing.

### Evidence

- `host`: [The GENI SPI register-model test and the Novatek protocol/point-report/touch-core host tests pass; hardware is not involved.](https://github.com/EsaiJJ/UniXNU-pipa/blob/7442e5a5f0f1d6c87edc75e7cdc25250b601f7d6/drivers/QcomGeniSpi/Test/geni-spi.c)
  Command: <code>gcc -std=c11 -O2 -Wall -Wextra -Werror drivers/QcomGeniSpi/Test/geni-spi.c drivers/QcomGeniSpi/GeniSpi.c -o /tmp/geni-spi &amp;&amp; /tmp/geni-spi</code>. Revision: `421c34bdcaf116bd15b8a895fa81ee483d4d8f31`.

## GPU {#gpu}

`implemented`

Components: `AdrenoPM4`, `AdrenoFirmware`, `ArmSmmu4K`, `AirNir`.

### Hardware and dependencies

- Adreno 650 \(chip id 0x06050002\), GMU firmware a650\_gmu.bin, SQE a650\_sqe.fw and the TZ PAS 13 zap shader a650\_zap.elf.

### Configuration

- board.toml sets pipa-gpu=12, sheng-gpu-addon=1 and sheng-fb-gpu=1; pipa\_defconfig enables CONFIG\_XNU\_NATIVE\_ADRENO with libAdreno650.a.
- GpuProbe keeps the upstream pipa defaults: Turnip "nocb", the upstream sandbox grant list, and no GPU DCVS block.

### Procedure

- Run pipa-gpu=12 with the GPU addon, then exercise SpringBoard/Settings and read the gpu.status counters.

### Development findings

- 2026-11-10 Adopted the upstream pipa GpuProbe.cpp, NativeBatteryBoard.h, and the pipa GPU addon script name; the pipa GPU defaults replace the TB-J716F DCVS/backlight add-on.

### Completion criteria

- The Adreno 650 KMD, GMU, GPU SMMU and NativeAdrenoMetal/Turnip render the desktop.

### Current limits

- No pipa GPU run in this fork; GMU/SQE/zap firmware files are external.

### Next action

- Boot pipa-gpu=12 on hardware and capture the GPU log rows.

### Evidence

- `source`: [Uses the Adreno 650 chip id, GMEM geometry, hwcg and a650\_protect tables from the upstream pipa port; no TB-J716F-only DCVS block is compiled.](https://github.com/EsaiJJ/UniXNU-pipa/blob/7442e5a5f0f1d6c87edc75e7cdc25250b601f7d6/package/GpuProbe.cpp)

## Network {#network}

`planned`

Components: `Ath12kWifi`, `QcaBluetooth`.

### Hardware and dependencies

- QCA6390 Wi-Fi on PCIe0 and Bluetooth on QUPv3\_0 SE6 GENI UART; BRCM/WCNSS board data and firmware from the pipa vendor partitions.

### Configuration

- The Wi-Fi/Bluetooth sources remain in the tree but board.toml does not set sheng-wifi or sheng-bluetooth, so neither driver starts.
- proprietary-files.txt records the expected images and leaves their pipa digests UNMEASURED.

### Procedure

- Only after the base port boots: extract the QCA6390 firmware, confirm the pipa rails/pins, then set sheng-wifi=4 / sheng-bluetooth=1.

### Development findings

- 2026-11-11 Kept the TB-J716F QCA6390 implementation as an unverified carry-over; the pipa DT's pins \(WLAN\_EN GPIO20, BT\_EN GPIO21, PERST GPIO79, PCIe0 CLKREQ GPIO80, BT SW\_CTRL GPIO124\) match the probe's constants, but nothing has been run.

### Completion criteria

- en0/wifid and BlueTool/bluetoothd start on the QCA6390.

### Current limits

- Default-off and unverified; the QCA6390 firmware is not in the tree.

### Next action

- Extract and hash the QCA6390 firmware, then validate the rail/pin sequence on pipa.

### Evidence

Collect evidence using the next action.

## Power {#power}

`implemented`

### Hardware and dependencies

- PM8150B fuel gauge \(SID 2, 0x4000..0x4400\), SMB5 charger and the 8840 mAh pipa pack.

### Configuration

- NativeBatteryBoard.h uses BAT\_DESIGN\_MAH 8840; NativeBattery and ShengPlatformPower build into the boot-progress and platform-power archives.

### Procedure

- Read IOPMPowerSource or the USB battery.status command and compare with Android.

### Development findings

- 2026-11-10 Replaced the TB-J716F battery board values with the pipa 8840 mAh profile and renamed the optional diagnostic argument to pipa-battery.

### Completion criteria

- The status bar and Settings show a live pipa battery percentage and charging state.

### Current limits

- No pipa hardware reading yet.

### Next action

- Compare the gauge with Android over a charge/discharge cycle.

### Evidence

- `host`: [The PM8150B gauge/charger decoding \(SOC ramp, voltage, current, temperature, charge stage\) passes against Android's recorded values; no hardware is read.](https://github.com/EsaiJJ/UniXNU-pipa/blob/7442e5a5f0f1d6c87edc75e7cdc25250b601f7d6/package/NativeBatteryTests.c)
  Command: <code>gcc -std=c11 -Wall -Wextra -Werror -I package package/NativeBatteryTests.c -o /tmp/pipa-battery &amp;&amp; /tmp/pipa-battery</code>. Revision: `421c34bdcaf116bd15b8a895fa81ee483d4d8f31`.

## Image assembly {#packaging}

`implemented`

Components: `XnuPrelink`, `DarwinBoot`.

### Hardware and dependencies

- The prelinked iPadOS 17.7.11 kernel, Format 2 ADT, trust caches, the pipa DTB, the NGPUADD2 addon and the UEFI FD.

### Configuration

- scripts/package.sh drives ./unixnu release with the pipa defconfig and build/pipa/pipa.dtb; the payload volume is PIPAESP and the image uses Android header v1.

### Procedure

- Run bash scripts/package.sh --no-deps --uefi ../uefi-pipa with UNIXNU\_UNIQUE\_CHIP\_ID set.

### Development findings

- 2026-11-11 Added scripts/extract-pipa-firmware.py, which pulls /vendor, modem and Bluetooth firmware from a booted pipa, records the ROM fingerprint as provenance and writes a SHA-256 manifest for proprietary-files.txt; it deliberately leaves the built-in Novatek image UNMEASURED.
- 2026-11-11 Renamed the pipa patch series, updated the GitHub workflows to xVanTuring/uefi-pipa and UniXNU/out/pipa, and added the pipa DTB and driver checks to CI.

### Completion criteria

- One command builds the kernel, archives, firmware, payload and boot.img.

### Current limits

- The build needs the external UniXNU and uefi-pipa checkouts plus the firmware caches.

### Next action

- Run the package workflow and flash boot.img to slot B.

### Evidence

- `host`: [Compiles dts/pipa.dts, validates board.toml and proprietary-files.txt, and runs the GopFramebuffer, QcomRpmh, QcomGeniSpi and ShengNovatekTouch host tests.](https://github.com/EsaiJJ/UniXNU-pipa/blob/7442e5a5f0f1d6c87edc75e7cdc25250b601f7d6/.github/workflows/xnu-source-macos.yml)
  Command: <code>Run the Pipa XNU source checks workflow</code>. Revision: `421c34bdcaf116bd15b8a895fa81ee483d4d8f31`.
- `host`: [The extractor parses and exits with a clear error when no adb device is present; it has not run against a tablet, so no firmware digest is claimed yet.](https://github.com/EsaiJJ/UniXNU-pipa/blob/7442e5a5f0f1d6c87edc75e7cdc25250b601f7d6/scripts/extract-pipa-firmware.py)
  Command: <code>python3 -m py_compile scripts/extract-pipa-firmware.py</code>. Revision: `efd421170a2b99be7f5146d6b678d696f8f23abd`.

## Diagnostics {#diagnostics}

`implemented`

### Hardware and dependencies

- SM8250 DWC3 USB0 at 0x0a600000, HS PHY 0x88e3000, EUD 0x88e1000, PS\_HOLD 0xc264000 and the ramoops zone at 0xb0000000.

### Configuration

- USB diagnostics use the PIPA\_ macros, the pipa-usb boot argument and the Xiaomi Pad 6 strings; PS\_HOLD is 0xc264000.
- BootRamoops parses pipa-restart-after, pipa-panic-restart-after, pipa-restart-crashes and pipa-cpufreq.

### Procedure

- Boot with pipa-usb=1 and connect the CDC-ACM interface, or read the ramoops zone with scripts/read-pipa-log.py.

### Development findings

- 2026-11-11 Renamed the USB diagnostics from J716F/TB-J716F to PIPA/Xiaomi Pad 6 and pointed the touch diagnostic at native\_touch\_stage\_done.

### Completion criteria

- A live USB console and a persistent ramoops log exist for bring-up.

### Current limits

- The USB path is default-off and unverified on pipa; the ramoops reader is host-side only.

### Next action

- Enable pipa-usb=1 on the first hardware round and capture the log.

### Evidence

- `source`: [The ramoops writer keeps 512 KiB of the pipa boot-log region at 0xb0000000, parses the pipa-restart-\* arguments, and preserves the zone across the warm reset into fastboot.](https://github.com/EsaiJJ/UniXNU-pipa/blob/7442e5a5f0f1d6c87edc75e7cdc25250b601f7d6/package/BootRamoops.c)

## Audio {#audio}

`planned`

### Hardware and dependencies

- Qualcomm ADSP PAS, SoundWire and the pipa codec/amplifier topology.

### Configuration

- No audio driver or boot argument is enabled.

### Procedure

- Implement ADSP remoteproc/GPR audio or USB audio first.

### Development findings

- 2026-11-11 Left audio out of the first pipa port; the TB-J716F CS35L41 manifest entries were removed because they do not describe pipa's amplifiers.

### Completion criteria

- IOAudio2Family outputs PCM audio to the speakers or headphones.

### Current limits

- Not started.

### Next action

- Identify the pipa codec/amplifier parts and their firmware.

### Evidence

Collect evidence using the next action.

</div>
