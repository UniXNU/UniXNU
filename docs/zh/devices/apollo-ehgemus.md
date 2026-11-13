# Xiaomi Mi 10T / Mi 10T Pro / Redmi K30S Ultra \(apollo\), SM8250 \(Ehgemus\)

[Ehgemus/UniXNU-apollo](https://github.com/Ehgemus/UniXNU-apollo)

<div v-pre>

Migrated from HakiOS, where iOS 16.5 reaches the home screen with touch, GPU, audio, Wi-Fi and battery. Format 2 configuration and hardware description in place; no UniXNU build and no UniXNU device boot yet.

源记录: [porting.toml](https://github.com/Ehgemus/UniXNU-apollo/blob/3b46798676eb1e523efd3fcfebfb75cec0950caa/porting.toml), `3b46798676eb1e523efd3fcfebfb75cec0950caa`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `planned` |
| [固件与启动](#firmware) | `implemented` |
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

组件: `ArmDTPlatform`, `XnuPrelink`.

### 硬件与依赖

- Pistachio-Project/UniXNU-sm8250-common at 90fa1fd; xnu-8796.121.2 \(c54f35c\); the iOS 16.5 20F66 iPhone10,3 IPSW.

### 配置

- board.toml selects SoC sm8250, OS profile ios-16.5-20F66 \(os-profiles/, linked by scripts/install-os-profile.sh\) and apollo\_defconfig.

### 操作步骤

- scripts/install-os-profile.sh; then from UniXNU: ./unixnu defconfig apollo\_defconfig -D ../UniXNU-apollo; ./unixnu fetch; ./unixnu status --json.

### 开发经验

- UniXNU reads OS profiles only from its own profiles/os/, so the iOS 16.5 profile is linked in until it is contributed upstream.
- The OS cryptex hash 2279bf44... was measured on the HakiOS image and matches UniXNU-nio's published pin for the same IPSW.
- The OS profile now carries its own 51-patch kernel series for xnu-8796, so board.toml no longer selects the xnu-10063 ARM64 series.
- unixnu fetch resolves every source and unixnu status resolves without local overrides \(unixnu.lock committed 2026-11-12\).
- board.toml \[payload.adt\] chip\_id is the Qualcomm SoC ID, 0x164 \(356\) as /sys/devices/soc0/soc\_id reports on the phone; the ADT generator requires it.
- TOML keys with a dot \(kern.maxvnodes\) must be quoted in the profile's \[adt\] tables, or they become nested tables and the ADT generator fails.
- The root image \(64354ba3...\) matches its pin too; its APFS volume UUID is 97A3EB1A-5218-4936-BC85-9574EC2C8CC9. Both images are seeded in UniXNU's out/ipsw/20F66 cache.

### 完成条件

- defconfig, fetch and status resolve; status shows arm64, sm8250, ios-16.5-20F66 and device profiles in order with the intended patch order.

### 当前范围

- The firmware and boot image values have not been through unixnu firmware/bootimg yet.

### 下一步

- Rebase the arch series onto xnu-8796 so ./unixnu kernel can run \(area packaging\).

### 证据

按下一步操作收集证据。

## 固件与启动 {#firmware}

`implemented`

组件: `DarwinBoot`.

### 硬件与依赖

- Pistachio-Project/uefi-apollo: Mu-Silicium apolloPkg from HakiOS \(KonaPkg, XBL BOOT.XF.3.2-00304-SM8250-2 drivers\).
- The phone's firmware, pulled by scripts/pull-firmware.sh into .cache/firmware \(42 files in proprietary-files.txt\).

### 配置

- \[firmware\] config apollo, apollo.dsc, FD at 0x9FC00000 size 0x300000.

### 操作步骤

- scripts/pull-firmware.sh with the phone in LineageOS, rooted adb; ./unixnu firmware -D ../UniXNU-apollo --uefi ../uefi-apollo.

### 开发经验

- On the phone \(2026-11-12, fastboot boot from RAM\): the RELEASE firmware reaches the UniXNU menu. Bisected on hardware: with the MdeModulePkg DiskIoDxe/PartitionDxe the firmware hangs on a blank screen, with the phone's prebuilt pair it reaches the menu \(uefi-apollo ab70992\).
- UniXNU's default boot image header \(base 0, 4096-byte pages, tags at 0x1e00000\) makes apollo's ABL boot Android instead; Mu-Silicium's mkbootimg values in \[bootimg.image\] work. A firmware-only image also needs a non-empty ramdisk \(uefi-apollo Resources/ramdisk\).
- A DEBUG build stops on ASSERT\_EFI\_ERROR \(Out of Resources\) in a prebuilt Qualcomm driver's uncached allocation; seen with the MdeModulePkg disk drivers, not retested with the prebuilt pair.
- Under HakiOS the same apolloPkg boots via fastboot boot and hands off to HakiOS's own XNU loader; UniXNU replaces that loader with UniXNU.efi and DarwinBoot.
- uefi-apollo needed sheng's SEC device-tree handoff \(entry-argument HOB\) and BootShim for UniXNURamDiskDxe and bootimg.py; DiskIo/Partition now come from MdeModulePkg instead of the XBL binaries.

### 完成条件

- Firmware image builds, enters the UniXNU menu, publishes the framebuffer and preserves the documented memory reservations.

### 当前范围

- Only the firmware is verified: no payload, DarwinBoot handoff or XNU yet.
- uefi-apollo bc8f586 builds \(RELEASE and DEBUG, 0x300000-byte FD\) but has not been booted. The payload must stay inside ABL's reserved Kernel window at 0xA0000000 \(256 MiB\); check the UNIXNURAMDISK initrd address on first boot.

### 下一步

- Retest the DEBUG build with the prebuilt disk drivers, then boot a payload through DarwinBoot once the kernel builds.

### 证据

- `device`: [Xiaomi Mi 10T M2007J3SY, LineageOS ABL: the UniXNU menu appears \(no boot entries, no payload\).](https://github.com/Pistachio-Project/uefi-apollo/commit/ab70992cdf353d7531df77649740bcce405365f4)
  Command: <code>./unixnu firmware --target RELEASE; ./unixnu bootimg --ramdisk ../uefi-apollo/Resources/ramdisk; fastboot boot</code>. Revision: `ab70992cdf353d7531df77649740bcce405365f4`.

## CPU 与中断 {#cpu}

`planned`

组件: `ArmCpu`.

### 硬件与依赖

- GICv3 at 0x17a00000 / 0x17a60000; eight cores, Affinity1 ids 0x0-0x700; 4 Cortex-A55 + 4 Cortex-A77; EPSS cpufreq domains.

### 配置

- All eight cpu nodes enabled; E/P cluster types from the SoC DTSI.

### 操作步骤

- Follow https://unixnu.com/porting/bring-up for CPU entry checkpoints.

### 开发经验

- HakiOS runs all eight cores and the big cores at full speed \(apollo\_cpufreq=1\) on xnu-8796 with its own SMP patch.

### 完成条件

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU.

### 当前范围

- The SMP numbering and cluster patches for xnu-8796 are not in the SoC series yet.

### 下一步

- Split HakiOS's SMP changes into UniXNU-sm8250-common/patches/xnu.

### 证据

按下一步操作收集证据。

## 内存与 DMA {#memory}

`planned`

### 硬件与依赖

- XBL memory map from uefi-apollo MemoryMapLib.c: HYP, AOP CMD DB, SMEM, TZApps, PIL, display regions.

### 配置

- dts/apollo.dts: DRAM 0x80000000 + 6 GiB, reserved-memory nodes for each firmware region.

### 操作步骤

- Compile with dtc -i ../UniXNU-sm8250-common/dts and inspect the generated ADT.

### 开发经验

- dtc compiles dts/apollo.dts with the SoC DTSI without warnings; scripts/make-adt.py produces a 14 KiB ADT with dram-base 0x80000000, dram-size 0x200000000, cpu0-3 E and cpu4-7 P, iPhone10,3 identity, sRGB, chip-id 0x164, and only intc under arm-io \(2026-11-12\).
- Measured on an 8 GiB M2007J3SY: the bootloader reports three DRAM banks with a 69 MiB hole at 0xbbb00000-0xc0000000; the DTS describes 8 GiB from 0x80000000 and reserves the hole.

### 完成条件

- All handoff regions are accounted for and each enabled DMA engine accesses its allocated range with the documented cache policy.

### 当前范围

- 6 GiB units need their own memory node. Reserved regions reach XNU through the firmware memory map, not the ADT; not checked on hardware.

### 下一步

- On the first DarwinBoot handoff, compare the memory map XNU reports with the reserved-memory nodes.

### 证据

按下一步操作收集证据。

## 存储与根卷 {#storage}

`planned`

组件: `RamBlock`.

### 硬件与依赖

- UFS on SM8250 at 0x1d84000; HakiOS's Darwin partition carved from userdata \(entry 34 of LUN 0\).

### 配置

- RamBlock root for bring-up, as HakiOS runs from RAM; \[userdata\] points at the darwin partition, LBAs 25691904-30935034 \(4096-byte\).

### 操作步骤

- Follow https://unixnu.com/porting/dual-system-partition with scripts/gpt-carve-darwin.py.

### 开发经验

- HakiOS keeps the system in RAM for a session; persistent /private/var is still in progress on apollo.

### 完成条件

- Root: the configured volume mounts and launchd starts. Persistence: writes survive reboot within the allocated Data region.

### 当前范围

- No UFS driver for SM8250 in the catalog; ShengUfs is SM8550-only.

### 下一步

- Check unixnu userdata against the darwin partition, then the UFS path.

### 证据

按下一步操作收集证据。

## 显示 {#display}

`planned`

组件: `GopFramebuffer`.

### 硬件与依赖

- Video-mode DSC panel mdss\_dsi\_j3s\_37\_02\_0a\_dsc\_video, 1080x2400 at 0x9c000000, DPU INTF\_1 at 0xae6b800, PM8150L WLED backlight.

### 配置

- GopFramebuffer on the firmware's framebuffer; board ADT artwork-display-gamut sRGB, oled-display 0.

### 操作步骤

- Boot to the UniXNU menu, then XNU; check the framebuffer geometry and colors.

### 开发经验

- Under HakiOS, iOS draws black with the iPhone's P3 gamut on this sRGB panel; sRGB fixes it.
- HakiOS drives the refresh rate \(60-144 Hz\) and WLED brightness from patches/xnu/0001.

### 完成条件

- A known frame appears with correct geometry and colors, then userland presentation and backlight controls work.

### 当前范围

- Backlight and refresh control are in the unapplied HakiOS patches.

### 下一步

- Verify the GOP framebuffer path, then move the WLED driver to a board service.

### 证据

按下一步操作收集证据。

## 输入 {#input}

`planned`

### 硬件与依赖

- Novatek NT36675 \(j3s\) on QUPv3 SE4 SPI; PM8150 power-on block and GPIO6 for the keys.

### 配置

- Touch firmware from .cache/firmware/touch \(proprietary-files.txt\).

### 操作步骤

- Apply patches/xnu/0001-0002 once their base is available; boot with apollo\_touch=1 apollo\_buttons=1.

### 开发经验

- HakiOS has working multitouch and power/volume keys on apollo through /dev/hakios-touch.

### 完成条件

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive, and buttons produce expected HID reports.

### 当前范围

- ShengNovatekTouch targets NT36532 over a different transport; the HakiOS driver is not a catalog component.

### 下一步

- Port hakios.apollo\_touch.c onto QcomGeniSpi and an IOHIDDevice source.

### 证据

按下一步操作收集证据。

## GPU {#gpu}

`planned`

### 硬件与依赖

- Adreno 650 with GMU at 0x3d6a000; a650\_gmu.bin, a650\_sqe.fw, a650\_zap.\* from .cache/firmware/gpu.

### 配置

- No catalog component; HakiOS's A650 driver is in patches/xnu/0001 \(apollo\_adreno, ApolloGPU\).

### 操作步骤

- Boot with apollo\_gpu=21 apollo\_gpu\_use=1 once the driver patches apply.

### 开发经验

- HakiOS renders the iOS UI on the A650 through Mesa freedreno \(OpenGL ES\); Metal is not available.

### 完成条件

- GPU submissions complete, mapping/fence handling is correct, a known image renders, and the selected Metal client presents it.

### 当前范围

- Adreno740 and AdrenoMetal are A740/SM8550-only.

### 下一步

- Move the A650 driver into an Adreno650 component.

### 证据

按下一步操作收集证据。

## 网络 {#network}

`planned`

### 硬件与依赖

- QCA6390 on PCIe0; amss.bin \(WLAN.HST.1.0.1.r1-01134\), m3.bin, bd\_j3s.elf, regdb.bin, board-2.bin.
- QCA6390 Bluetooth on QUPv3 SE6 UART \(0x998000, GPIO 16-19\), BT\_EN GPIO 21, SW\_CTRL GPIO 124, rails shared with Wi-Fi; htbtfw20.tlv and htnv20.bin from the bluetooth partition.

### 配置

- Linux ath11k built by scripts/mk-ath11k.sh over HakiOS's lx layer with package/ath11k-lx.

### 操作步骤

- git clone -b apollo https://github.com/enesuzun2002/hakios-apollo \(archived\); HAKIOS=&lt;that clone&gt; scripts/mk-ath11k.sh; boot with apollo\_wifi=5 wifi\_station=1.

### 开发经验

- HakiOS lists and joins Wi-Fi networks from Settings on apollo.
- The HakiOS checkout was removed from the porting host; mk-ath11k.sh now takes a clone of the archived hakios-apollo.
- aTechGeekDev/ios-apollo \(MIT\) runs Bluetooth on apollo under iOS 16.7.16: on/off, scan, pairing kept across reboots, A2DP, HFP and AVRCP. Kernel: xnu 0136/0137/0141-0143/0145 \(UART at 921600, HCI H4 endpoint, answers to bluetoothd's Broadcom vendor commands and 0x204a to keep legacy LE\). Userland: libsweet-bt replaces BlueTool and sets bluetoothd's H4 transport.
- UniXNU's QcaBluetooth does the same btqca bring-up over GENI UART but is verified only on WCN7850 with iPadOS 27's bluetoothd.

### 完成条件

- Scanning, association, address configuration and sustained receive/transmit traffic pass with the selected firmware.

### 当前范围

- Ath12kWifi does not cover the QCA6390; the build still needs a HakiOS checkout for its shared lx layer.

### 下一步

- Make an Ath11kWifi component from the lx layer and package/ath11k-lx.
- Bluetooth: extend QcaBluetooth to the QCA6390 with the apollo inputs above, and carry the iOS 16 bluetoothd shims from ios-apollo as a board service \(firmware hashes recorded 2026-11-12\).

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`planned`

### 硬件与依赖

- ADSP firmware \(adsp.mdt/.bNN\), two CS35L41 B2 on QUPv3 SE3, the WCD938x/bolero microphones, Tutu ACDB calibration.

### 配置

- Firmware from .cache/firmware/audio; mic topology generated by scripts/acdb-mic.py.

### 操作步骤

- Boot with apollo\_audio=5 apollo\_mic=4 once the driver patches apply.

### 开发经验

- HakiOS plays through the speakers and records from both microphones \(Voice Memos\).

### 完成条件

- Each declared route carries the selected audio format through playback or capture and handles start/stop correctly.

### 当前范围

- Cirrus speaker-protection firmware does not run; HakiOS limits levels in software \(apollo\_guard\).

### 下一步

- Split the ADSP/APR transport into the SoC repository and the codec/amplifier setup into board services.

### 证据

按下一步操作收集证据。

## 电源 {#power}

`planned`

### 硬件与依赖

- PM8150B fuel gauge \(fg-gen4\) through the SPMI observer; AW8697 haptics on QUPv3 SE11; EPSS cpufreq.

### 配置

- Haptics waveforms from .cache/firmware/haptic.

### 操作步骤

- Boot with apollo\_battery=1 apollo\_charger=3 apollo\_haptic=5 apollo\_cpufreq=1 once the driver patches apply.

### 开发经验

- HakiOS shows battery level and charging, and vibrates through the AW8697, on apollo.

### 完成条件

- Declared power controls and battery readings match observations; each claimed sleep/resume transition restores its dependent peripherals.

### 当前范围

- No sleep/resume under HakiOS.

### 下一步

- Move the SPMI fuel-gauge reader to a board service.

### 证据

按下一步操作收集证据。

## 镜像组装 {#packaging}

`planned`

组件: `SoftwareAES`, `AppleKeyStoreState`.

### 硬件与依赖

- patches/xnu/0001-0002 from HakiOS \(against xnu-8796.121.2 plus HakiOS's core patch\); UniXNU's arch series \(written for xnu-10063\).

### 配置

- board.toml selects soc, os and device series; the OS series os-profiles/ios-16.5-20F66/patches/xnu/series replaces arch:patches/xnu/series. Device patch series lists the HakiOS patches commented out.

### 操作步骤

- scripts/package.sh --check --os ios-16.5-20F66, then scripts/package.sh --os ios-16.5-20F66 --uefi ../uefi-apollo.

### 开发经验

- UniXNU's 56 ARM64 patches against xnu-8796.121.2 \(2026-11-12\): 44 apply unchanged and are referenced from UniXNU \(arch:\); 5 are ported in os-profiles/ios-16.5-20F66/patches/xnu-8796 \(apple-only-cpu-tunables, external-archive-dependencies, native-aes-personality, source-machine-layer, zzx-pmap-sync-64bit-pa\); 3 do not apply to xnu-8796 \(pgz-aligned-validation, public-entitlements-header, published-freezer-condition\); 4 iPadOS 17 owner/addon/cryptex patches are left out. Both XnuPrelink patches apply unchanged. The resolved 51-patch order applies cleanly to a fresh xnu-8796.121.2 tree.
- zzx-pmap-sync-64bit-pa matters on apollo: 4 GiB of DRAM lies above 4 GiB.
- With UniXNU's Linux toolchain \(2026-11-12\) xnu-8796.121.2 compiles and links \(mach.development.bcm2837\) after seven more OS-profile patches: clang-drop-auto-var-init-acknowledgement and clang-uio-stackbuf \(current clang\), iorpc-kernel-content \(the toolchain's iig emits xnu-10063 DriverKit glue\), kalloc-pointee-type \(os\_get\_pointee\_type backport for C++ void pointers\), arm64-kpc-from-xnu-10063 \(the 8796 source release omits osfmk/arm64/kpc.c; non-Apple stubs\), compile-records \(clang -MJ, which the archive builders read\) and pthread-jit-entitled-callback \(UniXNU's libpthread 519.120.4\). ArmDTPlatform, ArmCpu, SoftwareAES, RamBlock, AppleKeyStoreState, corecrypto and libpthread then build against xnu-8796.
- Prelink stops on the iOS 16.5 kernelcache \(sha256 e6fa7559...\): emit\_prelink finds external PC-relative encodings in inline data. With its existing catalogue applied \(SHA-256 K, Adler-32 vectors and the Libm pools all match iOS 16.5 too\), only 8 words remain, all in com.apple.kec.Libm \_\_TEXT\_EXEC \(va 0xfffffff005b8d000\): 0x11cc, 0x11dc, 0x11ec, 0x11fc and 0x1490, 0x14a0, 0x14d4, 0x14ec. They lie in one block of double-precision constants that starts after the RET at 0x1050 and is read through ADR \(targets 0x1068, 0x107c, 0x1088, 0x109c, 0x10c4, 0x14cc\). Libm has no symbols, LC\_FUNCTION\_STARTS or ADRP data references, and no BL target delimits the block end yet.
- UniXNU build caching: patches that change exported headers do not reach .cache/fakeroot until its .xnu-&lt;version&gt;-headers stamp and the startup.o.json record are removed.
- The HakiOS apollo drivers depend on HakiOS's shared core patch \(input, QMI, lx, audio plug-in layers\), which is not in this repository.

### 完成条件

- Kernel and prelink succeed, payload contains all declared inputs, and the boot image matches the bootloader format and size limit.

### 当前范围

- kernel.macho is not produced yet: prelink is blocked \(see findings\). Nothing has run on hardware.

### 下一步

- Find the end of the Libm constant block after 0x1054 \(first real instruction after 0x14ec\), catalogue that span \(prefix, size, SHA-256\) in a device prelink wrapper that extends emit\_prelink.MATH\_LITERAL\_POOLS, set \[kernel.prelink\] tool to it, then finish ./unixnu kernel.

### 证据

按下一步操作收集证据。

## 诊断 {#diagnostics}

`planned`

### 硬件与依赖

- HakiOS's driver traces \(frame pacing, hitch tracer\) and the firmware log exporter.

### 配置

- apollo\_frames=1 apollo\_hitch=1 in the HakiOS patches.

### 操作步骤

- Follow https://unixnu.com/porting/log-capture.

### 开发经验

- HakiOS traced animation hitches of 65-235 ms to frames arriving late from CoreAnimation, not to the display or GPU path.

### 完成条件

- Each claimed milestone has a reproducible command, a matching source/image revision and an accessible result.

### 当前范围

- No UniXNU log capture yet.

### 下一步

- Enable the firmware log exporter in uefi-apollo and capture the first boot.

### 证据

按下一步操作收集证据。

</div>
