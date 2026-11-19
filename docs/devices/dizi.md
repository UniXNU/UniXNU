# Xiaomi Redmi Pad Pro \(dizi\); ruan unverified

[vildangil/UniXNU-Dizi-Ruan](https://github.com/vildangil/UniXNU-Dizi-Ruan)

<div v-pre>

Xiaomi Redmi Pad Pro \(dizi\), SM7435 \(Parrot\). Bring-up stage: CPU, interrupts, timer and GOP framebuffer through Mu-Silicium diziPkg. No hardware boot evidence yet.

Source record: [porting.toml](https://github.com/vildangil/UniXNU-Dizi-Ruan/blob/87bcefbff7bc922b74ececd4c04e5331dc353317/porting.toml), `87bcefbff7bc922b74ececd4c04e5331dc353317`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `implemented` |
| [Firmware and boot](#firmware) | `implemented` |
| [CPU and interrupts](#cpu) | `device-verified` |
| [Memory and DMA](#memory) | `device-verified` |
| [Storage and root](#storage) | `implemented` |
| [Display](#display) | `implemented` |
| [Input](#input) | `implemented` |
| [GPU](#gpu) | `planned` |
| [Network](#network) | `planned` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `implemented` |
| [Image assembly](#packaging) | `planned` |
| [Diagnostics](#diagnostics) | `planned` |

## Configuration {#configuration}

`implemented`

Components: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`, `DarwinBoot`.

### Hardware and dependencies

- Identify the configuration hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for configuration.

### Procedure

- Follow the configuration stage in the porting guide and record the actual commands.

### Development findings

- feeds.toml previously pinned an SM8550 commit, so status resolved the sm8550 SoC profile; it now pins sm7435-common and status reports soc sm7435.
- board.toml carries the bring-up component set, config fragments, patch series, device tree, Mu-Silicium firmware paths and a 56 MiB payload that fits the 100 MiB boot partition.
- The ADT declares vmm-present = 1: dizi firmware publishes no Apple PMGR and AMFI otherwise panics with 'AMFI: No PMGR?' at ConfigurationSettings.cpp:235.
- 2026-11-15: kernel\_args default to cpus=8 smp=1; \[kernel\] archives add ShengUfs, its KDK-free bindings \(candidate kernel without ShengUfs\), the PMGR bridge and the boot-progress page; \[userdata\] holds the GPT range 0x35a228-0x1d13ffa; ruan's 2.75 GiB window does not fit dizi's UEFI map, and the 1952 MiB window above 4 GiB stops at setconf, so the default window stays.
- 2026-11-17: board.toml adds the RamBlock component and its archives \(component:RamBlock, NativeRamBlock bindings\), packed\_data\_ramdisk = true, \[userdata\] partition = 'unixnu' with the unixnu range, native-ufs-partition=unixnu in kernel\_args, and records the failed memory windows; dizi\_defconfig links build/ram-block/libRamBlock.a.
- 2026-11-18: board.toml adds owned\_memory\_outside\_ranges = 16, owned\_memory\_outside\_reserved \(low bank, HYP Reserved, iomem holes 0x8bab00000+6M and 0x8bcf00000+49M\) and memory-outside=3 in kernel\_args.
- 2026-11-18: board.toml adds GopFramebuffer and AppleKeyStoreState, the keystore and display archive steps, the display and key store boot args \(no -v\) and \[adt.chosen.u32\] display-scale = 2; dizi\_defconfig sets CONFIG\_XNU\_NATIVE\_LEGACY\_DISPLAY=y and links libKeyStoreProbe.a.
- 2026-11-19: board.toml adds ruan\_touch=1, garnet\_buttons=1, ruan-cpufreq=2, ruan-usbdbg=1, offline-hid-input=1, sheng-touch-hid=1 and sheng-touch-split=1.

### Completion criteria

- All source pins resolve; every selected component has a record; status shows the intended overrides and patch order.

### Current limits

- Payload memory is the single 2 GiB DDR region0 at 0x80000000 that UniXNU's ADT generator requires; other RAM sizes are not checked.

### Next action

- Add the root filesystem inputs \(storage driver, userdata root image\).

### Evidence

- `source`: [unixnu status resolves soc sm7435, profile ipados-17.7.11-21H461 and the dizi patch order](https://github.com/vildangil/UniXNU-Dizi-Ruan/blob/87bcefbff7bc922b74ececd4c04e5331dc353317/board.toml)

## Firmware and boot {#firmware}

`implemented`

### Hardware and dependencies

- Identify the firmware and boot hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for firmware and boot.

### Procedure

- Follow the firmware and boot stage in the porting guide and record the actual commands.

### Development findings

- Mu-Silicium diziPkg embeds UniXNU, UniXNUDxe, UniXNURamDiskDxe and DarwinBoot; Silicium SEC saves the bootloader x0 \(FDT\) in the entry-argument HOB.
- On dizi the initrd starts with the vendor\_boot LZ4 legacy ramdisk \(0x184C2102\) followed by the FAT32 payload; UniXNURamDiskDxe now skips the LZ4 frames and publishes the payload, so the menu loads \\EFI\\UniXNU\\unixnu.toml.
- The Windows KEP ExitBootServices hook is left out with DISABLE\_KEP; BootShim's image size covers the shim plus the FD.
- Volume and power keys use the PMIC/SPMI reader from the old-ChatGPT branch in diziPkg/Library/UniXNULibDizi; Volume Down timing was shortened and is not yet re-tested.

### Completion criteria

- Firmware image builds, enters UniXNU, publishes the framebuffer and preserves the documented memory reservations.

### Current limits

- The UEFI vendor binaries in Mu-Silicium Binaries/dizi are documented as Redmi Note 13 Pro 5G firmware.

### Next action

- Test Volume Down in the menu with the shortened guard.

### Evidence

- `source`: [DarwinBoot handoff with the green bar observed on dizi on 2026-11-14](https://github.com/vildangil/Mu-Silicium/tree/dizi-bringup)

## CPU and interrupts {#cpu}

`device-verified`

### Hardware and dependencies

- Identify the cpu and interrupts hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for cpu and interrupts.

### Procedure

- Follow the cpu and interrupts stage in the porting guide and record the actual commands.

### Development findings

- 2026-11-14 on dizi with cpus=1: entry probe showed the blue \(kernel entry\) and magenta \(pre-MMU\) bands, and a reset after MMU-on.
- XNU then panicked at fiq\_context\_init writing CNTP\_CTL\_EL0: the hypervisor traps EL1 physical-timer access. sm7435-virtual-timer-only.patch removes that write.
- With the patch XNU passes arm\_init, IOKit and AMFI and stops at 'Failed to mount root device' \(IOKitBSDInit.cpp:984\), which is expected without a root filesystem.

### Completion criteria

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU.

### Current limits

- Secondary CPUs \(SMP\) are not started or tested; cpus=1 stays the default.

### Next action

- Test SMP with an explicit cpus=2 run after root mount works.

### Evidence

- `device`: [XNU reaches 'Failed to mount root device' at IOKitBSDInit.cpp:984 on the panic screen](https://github.com/vildangil/UniXNU-sm7435-common/commit/1765d1bc3601d288f00fa6f7be9b7634b4e10e18)
  Command: <code>fastboot boot out/dizi/ipados-17.7.11-21H461/dizi/boot/boot.img</code>. Revision: `1765d1bc3601d288f00fa6f7be9b7634b4e10e18`.

## Memory and DMA {#memory}

`device-verified`

### Hardware and dependencies

- Identify the memory and dma hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for memory and dma.

### Procedure

- Follow the memory and dma stage in the porting guide and record the actual commands.

### Development findings

- dizi's low DRAM bank has almost no free memory \(diziPkg MemoryMapLib\), so DarwinBoot's window starts in the 0x840000000 run \(UEFI: 0x7AB00000 bytes\).
- 2026-11-17: windows of 0x7A000000, 0x78000000 and 0x40000000 all froze the tablet about one second into BSD \(clock stopped, irq=0\), with or without the Data seed and with ShengUfs DMA kept below 0x850000000. The default 256 MiB window works; launchd's daemons then get jetsam-killed.
- Linux \(OrangeFox, /proc/iomem\) has 0x840000000-0x8baafffff, 0x8bb100000-0x8bcefffff and 0x8c0000000-0x8ffffffff as System RAM, so the larger windows lay in RAM given to HLOS; the 6 MB hole 0x8bab00000-0x8bb0fffff explains only the 0x7A000000 window. The cause of the freeze is open.
- 2026-11-18: dizi-memory-outside.patch \(ruan-memory-outside.patch, unchanged\) with memory-outside=3 adopts the DRAM above the 256 MiB window; board.toml lists 16 outside ranges and keeps out the low bank, HYP Reserved and the two iomem holes. The boot-progress page shows mem=3784M+352xM, about 104 processes run with no jetsam kills, and SpringBoard now crashes with SIGTRAP \(ns 2 code 5\) instead.
- 2026-11-19: package/SmmuBypass.h is the ruan port's current SMMU stream helper, used by the USB debug link \(replacing the sheng-era copy\); dizi's UFS keeps the firmware's mapping \(native-ufs-smmu-reuse=1\).

### Completion criteria

- All handoff regions are accounted for and each enabled DMA engine accesses its allocated range with the documented cache policy.

### Current limits

- The window itself stays at 256 MiB; windows above it froze the tablet one second into BSD, cause unknown.

### Next action

- Display and key store for SpringBoard; later find why larger DarwinBoot windows freeze.

### Evidence

- `source`: [ruan-memory-outside.patch, unchanged; owned\_memory\_outside\_\* in board.toml](https://github.com/vildangil/UniXNU-Dizi-Ruan/blob/87bcefbff7bc922b74ececd4c04e5331dc353317/patches/xnu/dizi-memory-outside.patch)
- `device`: [2026-11-18: mem=3784M+352xM on the boot-progress page, about 104 processes, no jetsam kills](https://github.com/vildangil/UniXNU-Dizi-Ruan/commit/f4c4e343845807456e71953d062e0d5d32d94ba1)
  Command: <code>fastboot boot boot.img</code>. Revision: `f4c4e343845807456e71953d062e0d5d32d94ba1`.

## Storage and root {#storage}

`implemented`

Components: `ShengUfs`, `VerifiedRoot`, `VirtioMmioBlock`, `RamBlock`, `AppleKeyStoreState`.

### Hardware and dependencies

- Identify the storage and root hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for storage and root.

### Procedure

- Follow the storage and root stage in the porting guide and record the actual commands.

### Development findings

- ShengUfs drives dizi's UFS host \(0x1d84000, SPI 265\) with SMMU stream 0x20 \(native-ufs-stream\). Gunyah blocks the SMMU's GR1 and context banks \(external abort\), so native-ufs-smmu-reuse=1 keeps the firmware's stream-to-bank-2 mapping.
- The GPT read gives userdata at 0x35a228-0x1d13ffa on LUN 0, matching fastboot's partition size.
- DMA straight into caller pages powered the tablet off; native-ufs-zero-copy=0 keeps all DMA in the host buffer.
- With native-ufs-allow-unverified=1 and dizi-ufs-unverified-root.patch the iPadOS 17.7.11 OS volume \(04769D26\) mounts read-only from userdata and launchd starts.
- Without SystemOS launchd stopped at dyld: libSystem.B.dylib is only in the dyld shared cache of the SystemOS cryptex. A DarwinBoot window above 4 GiB \(0x7A000000 at 0x840000000\) stops at setconf with no interrupts.
- 2026-11-16: dizi-systemos-union.patch turns on UniXNU's owner SystemOS union \(XNU\_OWNER\_CACHE\_MOUNT, CACHE\_STARTUP, UNION\_SYSTEMOS\) and boot manifest; ShengUfs answers native\_verified\_block\_volume\_device, root\_authorized and manifest\_sha384 for UFS window volumes only with native-ufs-allow-unverified=1. The SystemOS volume \(8846FE78\) mounts as a read-only union over / and launchd loads.
- mount\(8\) exited 66 on a missing boot-manifest-hash; /chosen now gets one built from placeholder per-volume digests \(SHA-384 of a tag and the UUID\). launchd then runs 17 processes \(fsck, mount, keybagd, usermanagerd, apfs\_boot\_util, seputil and others\) and stops at the critical tzinit: /private/var is read-only \(errno 30\), so there is no Data volume.
- 2026-11-17: writable Data on /private/var. dizi-data-volume.patch turns on the owner Data mount with XNU\_NATIVE\_RAM\_BLOCK; NativeRamBlock \(component RamBlock, KDK-free bindings\) serves the payload's packed Data seed \(make-data-seed.py\), whose APFS volume UUID comes from data-uuid=&lt;UUID&gt;. Without a persistent store a seed above 2 GiB refuses writes \(device is not ready\), and a seed of 512 MB or more hashes every page at start and resets the tablet at setconf; a 128 MB seed works.
- 2026-11-17: dual boot. GPT entry 21 \(userdata, 0x35a228-0x1d13ffa\) was split with sgdisk from an unofficial OrangeFox \(fox\_dizi\) started with fastboot boot: entry 22 unixnu \(0x35a228-0xb5a227, 32 GiB\) keeps the iPadOS root in place, entry 21 userdata \(0xb5a228-0x1d13ffa, 70.9 GiB, original GUIDs\) is Android's. ShengUfs finds the root by name with native-ufs-partition=unixnu. HyperOS 3 boots on the new userdata after fastboot erase userdata and metadata.
- ShengUfs reports each driver stage on the boot-progress page \(ufs: ...\); native-ufs-dma-max=&lt;address&gt; limits the host DMA memory \(off by default\).
- 2026-11-18: AppleKeyStore stand-in \(UniXNU AppleKeyStoreState + package/KeyStoreProbe.cpp from the ruan port, scripts/build-keystore-probe.py\) started before launchd by dizi-keystore-probe.patch with aks=1 offline-key-events=1, for keybagd, init\_data\_protection and usermanagerd. With it and the display, SpringBoard reaches the lock screen.

### Completion criteria

- Host: register, clock, link and SMMU facts match the board inventory.
- Reads: SCSI capacity, GPT and known blocks are correct; OS/SystemOS windows stay within userdata.
- Root: the configured volume mounts and launchd starts. Persistence: writes survive reboot within the allocated Data region.

### Current limits

- The OS and SystemOS volumes are not authenticated, and the boot-manifest-hash is a placeholder, not an Apple manifest digest. Data lives in RAM: 128 MB, lost on reboot.

### Next action

- Keep Data changes in a UFS store inside unixnu \(data-persist\), and hash only nonzero seed pages so a larger Data volume starts.

### Evidence

- `source`: [dizi changes to ShengUfs: stream, SMMU reuse, zero-copy switch, unverified root, unverified volume queries](https://github.com/vildangil/UniXNU-Dizi-Ruan/blob/87bcefbff7bc922b74ececd4c04e5331dc353317/patches/drivers/ShengUfs-dizi.patch)
- `device`: [2026-11-16: SystemOS mount returned; launchd ran 17 processes and stopped at tzinit \(read-only /private/var\)](https://github.com/vildangil/UniXNU-Dizi-Ruan/commit/0d560de946ba7ce41b4687677d3baabca165a677)
  Command: <code>fastboot boot boot.img</code>. Revision: `0d560de946ba7ce41b4687677d3baabca165a677`.
- `device`: [2026-11-17: root from unixnu, Data mount returned, about 85 processes, SpringBoard started; Android boots from the new userdata](https://github.com/vildangil/UniXNU-Dizi-Ruan/commit/357c534a38b3f527fb7736a5d326f81129211a0e)
  Command: <code>fastboot boot boot.img</code>. Revision: `357c534a38b3f527fb7736a5d326f81129211a0e`.

## Display {#display}

`implemented`

Components: `GopFramebuffer`.

### Hardware and dependencies

- The firmware GOP framebuffer: 1600x2560 32-bit at 0xB8000000 \(diziPkg Display Reserved\), the same as ruan's.

### Configuration

- CONFIG\_XNU\_NATIVE\_LEGACY\_DISPLAY=y; \[kernel\] archives build-gop-legacy-display.py; components GopFramebuffer.

### Procedure

- Follow the display stage in the porting guide and record the actual commands.

### Development findings

- 2026-11-18: GopFramebuffer NativeLegacyDisplay is bound to the original IOMobileFramebufferLegacy \(21H461\) by scripts/build-gop-legacy-display.py and package/LegacyDisplayProbe.cpp, both from the ruan port \(commit 5ce47b1, display path only\), with ruan's gopfb-vsync-poll, gopfb-fb-wc and gopfb-retire-transfer fixes. Every pinned address and instruction matched dizi's kernel.
- Boot args offline-mobile-graphics-load, offline-legacy-register/phase=4/gop/pm/validate/transfer/cpu-present, vsync=60 and fb-wc=1; no -v, which makes the console text mode so backboardd never presents. /chosen display-scale 2.
- 2026-11-18 on the tablet: backboardd drew the Apple logo, then the lock screen; 5765 frames copied, all accepted \(sw a5765 r0\), 12-30 ms per copy. SpringBoard then restarted \(spinner\).
- 2026-11-19: with the full ruan sync the lock screen shows the date, time and battery, SpringBoard stays up \(SB x1\); PosterBoard crashes \(NSInternalInconsistencyException\), so the background is black.
- 2026-11-19: the ruan port's SY7758 backlight driver \(RuanBacklight.cpp, GENI I2C\) is built and started by the display probe; its effect on dizi is not observed yet.

### Completion criteria

- A known frame appears with correct geometry and colors, then userland presentation and backlight controls work.

### Current limits

- CPU copy only \(no GPU\); no touch input yet; SpringBoard restarts after the lock screen.

### Next action

- Disable the crash-looping launchd jobs in the Data seed \(ruan list\), then port touch input.

### Evidence

- `source`: [binds NativeLegacyDisplay to the original IOMobileFramebufferLegacy; 50 pinned checks pass at build](https://github.com/vildangil/UniXNU-Dizi-Ruan/blob/87bcefbff7bc922b74ececd4c04e5331dc353317/scripts/build-gop-legacy-display.py)

## Input {#input}

`implemented`

### Hardware and dependencies

- Identify the input hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for input.

### Procedure

- Follow the input stage in the porting guide and record the actual commands.

### Development findings

- UniXNU menu: Volume Up, Volume Down and Power work through the PMIC/SPMI key reader in Mu-Silicium diziPkg/Library/UniXNULibDizi \(from the old-ChatGPT build\). Each press must be held about one second \(2026-11-15\).
- No touch or button input in XNU yet.
- 2026-11-19: the ruan port's HakiOS NT36532 touch driver \(RuanTouch.c, hakios.novatek\_ruan.h\) runs with ruan\_touch=1 and dizi's BOE firmware \(novatek\_ts\_fw\_boe.bin, the same panel as ruan: xiaomi n83 35 02 0a cphy nt36532 boe; scripts/make-touch-fw-header.py, kept out of git\). The controller reports \(tp305, raw coordinates\), but without offline-hid-input=1 the HID publisher stays at stage 0 \(hid0\), so iPadOS gets no touches; the args are added.
- garnet\_buttons=1 \(RuanButtons.c, PMIC power and volume keys\) works in iPadOS: the bottom banner counts presses.

### Completion criteria

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive, and buttons produce expected HID reports.

### Current limits

- Touch reaches the controller; delivery to iPadOS is not confirmed yet.

### Next action

- Confirm touches reach iPadOS with offline-hid-input=1 sheng-touch-hid=1 sheng-touch-split=1.

### Evidence

- `source`: [Menu keys confirmed on dizi 2026-11-15](https://github.com/vildangil/Mu-Silicium/tree/main/Platforms/Xiaomi/diziPkg/Library/UniXNULibDizi)

## GPU {#gpu}

`planned`

### Hardware and dependencies

- Identify the gpu hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for gpu.

### Procedure

- Follow the gpu stage in the porting guide and record the actual commands.

### Development findings

- 2026-11-19: the ruan port's Adreno 710 headers \(AdrenoHfi.h, RuanA710\*.h, RuanGmu\*.h, RuanGpuPowerBoard.h, UsbDebugGpu.h\) are copied because the USB debug link and display probe include them; the GPU code itself \(RuanGpuPower.c, AdrenoHfi.c\) is not built on dizi, needs Qualcomm's GPU firmware and is experimental on ruan. BootProgressRuanStubs.c answers its entry points with 'not ready'.

### Completion criteria

- GPU submissions complete, mapping/fence handling is correct, a known image renders, and the selected Metal client presents it.

### Current limits

- Hardware inputs and implementation are pending for dizi.

### Next action

- Inventory the required gpu inputs before implementation.

### Evidence

Collect evidence using the next action.

## Network {#network}

`planned`

### Hardware and dependencies

- Identify the network hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for network.

### Procedure

- Follow the network stage in the porting guide and record the actual commands.

### Development findings

- 2026-11-19: package/RuanWifiProbe.h is the ruan port's Wi-Fi status header, included by its boot-progress page; dizi does not build the probe \(ruan's review: a status stub\). Wi-Fi is not started.

### Completion criteria

- Scanning, association, address configuration and sustained receive/transmit traffic pass with the selected firmware.

### Current limits

- Hardware inputs and implementation are pending for dizi.

### Next action

- Inventory the required network inputs before implementation.

### Evidence

Collect evidence using the next action.

## Audio {#audio}

`planned`

### Hardware and dependencies

- Identify the audio hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for audio.

### Procedure

- Follow the audio stage in the porting guide and record the actual commands.

### Development findings

- 2026-11-19: package/RuanAudioProbe.h is the ruan port's audio status header, included by its boot-progress page; dizi does not build the probe \(ruan's review: a status stub that touches no hardware\). Audio is not started.

### Completion criteria

- Each declared route carries the selected audio format through playback or capture and handles start/stop correctly.

### Current limits

- Hardware inputs and implementation are pending for dizi.

### Next action

- Inventory the required audio inputs before implementation.

### Evidence

Collect evidence using the next action.

## Power {#power}

`implemented`

### Hardware and dependencies

- Identify the power hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for power.

### Procedure

- Follow the power stage in the porting guide and record the actual commands.

### Development findings

- 2026-11-19: the ruan port's fuel-gauge battery \(RuanBattery.c, HakiosBattery.cpp, PM7250B\) publishes an IOPMPowerSource; the lock screen shows the battery level \(81 %\). ruan-cpufreq=2 \(RuanCpuFreq.c\) votes 1958/2400 MHz.
- When iPadOS went to sleep, XNU panicked restarting a core \(cpu 1 failed to start @processor.c:774\). scripts/seed-data-ruan-prefs.py writes ruan's no-dim, no-lock-on-AC and no-idle-sleep preferences and 18 disabled launchd jobs into the Data seed; with it the screen stays on.

### Completion criteria

- Declared power controls and battery readings match observations; each claimed sleep/resume transition restores its dependent peripherals.

### Current limits

- CPU cores cannot be restarted after sleep, so sleep is turned off in the Data seed.

### Next action

- Find why a core does not come back after sleep \(PSCI CPU\_ON under Gunyah\).

### Evidence

- `source`: [ruan fuel gauge; battery level on the lock screen 2026-11-19](https://github.com/vildangil/UniXNU-Dizi-Ruan/blob/87bcefbff7bc922b74ececd4c04e5331dc353317/package/RuanBattery.c)

## Image assembly {#packaging}

`planned`

### Hardware and dependencies

- Identify the image assembly hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for image assembly.

### Procedure

- Follow the image assembly stage in the porting guide and record the actual commands.

### Development findings

- The kernel links ShengUfs with patches/drivers/ShengUfs-dizi.patch applied in drivers/ShengUfs; the patch now also carries the unverified volume queries for the SystemOS union \(2026-11-16\).
- The boot image is a 60.5 MB boot.img with the 56 MiB FAT payload after the LZ4 vendor ramdisk; it fits the 100 MiB boot partition and is only started with fastboot boot.
- 2026-11-17: the ShengUfs patch adds stage markers, native-ufs-dma-max and native-ufs-partition; package/BootProgressRuanStubs.c adds ml\_static\_mfree\_prepare for NativeRamBlock's weak import.
- 2026-11-18: dual boot from slot b. All slot-b firmware equals slot a \(sha256 per partition, OrangeFox\); boot\_b holds the UniXNU image and vbmeta\_b has verification off. fastboot set\_active b boots UniXNU. With boot\_b at one retry and not successful the bootloader boots it once and falls back to slot a \(Android\) on the next reboot.
- 2026-11-18: recovery\_a cannot start UniXNU: the bootloader drops to fastboot for a recovery image with its own kernel, also with stock os\_version \(stock recovery has no kernel\).
- dualboot/ksu-module is a KernelSU module whose Action runs the one-shot switch: bootctl \(AOSP, HIDL boot@1.2, bundled because HyperOS has none\) makes slot b active, sgdisk sets boot\_b to one retry, it checks the flags read 000F and otherwise switches back to slot a. Tested on HyperOS 3 with the Caramel v2 kernel \(KernelSU 3.3.0\): iPadOS once, then Android.
- 2026-11-18: patches/xnu/series adds dizi-memory-outside.patch \(ruan-memory-outside.patch from the ruan port, unchanged; it applies cleanly after the dizi patches\).
- 2026-11-18: patches/xnu/series adds dizi-keystore-probe.patch \(regenerated against dizi's tree; the ruan patch's context is its RAM-root code\).
- 2026-11-19: scripts/seed-data-ruan-prefs.py \(run as root\) adds ruan's Data preferences and disabled jobs to a packed seed; scripts/make-touch-fw-header.py builds the touch firmware header in .cache/hakios-fw.

### Completion criteria

- Kernel and prelink succeed, payload contains all declared inputs, and the boot image matches the bootloader format and size limit.

### Current limits

- Hardware inputs and implementation are pending for dizi.

### Next action

- Inventory the required image assembly inputs before implementation.

### Evidence

Collect evidence using the next action.

## Diagnostics {#diagnostics}

`planned`

### Hardware and dependencies

- Identify the diagnostics hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for diagnostics.

### Procedure

- Follow the diagnostics stage in the porting guide and record the actual commands.

### Development findings

- 2026-11-17: package/BootProgressRuanStubs.c gains ml\_static\_mfree\_prepare \(returns false: the loader keeps the Data seed pages\), which NativeRamBlock weak-imports and the static kernel link needs.
- 2026-11-18: BootProgressRuanStubs.c drops its arm\_vm\_outside\_\* and ml\_outside\_memory\_\* stand-ins; dizi-memory-outside.patch defines them, so the page shows the adopted outside memory \(mem=...+...M\).
- 2026-11-18: the native\_legacy\_\* stand-ins leave BootProgressRuanStubs.c; LegacyDisplayProbe.cpp and NativeLegacyDisplay define them, and the bottom banner shows copies, swaps and vsync.
- 2026-11-19: the ruan port's board code is synced \(scripts/build-boot-progress-ruan.py\): its current boot-progress page, crash banner \(BootFaultProbe.c\), boot reset \(BootReset.c\), touch, buttons, battery, backlight, CPU frequency, HID publisher and USB debug link. Left out: its RAM root, the Adreno 710 bring-up \(needs Qualcomm firmware\) and the Wi-Fi/audio status stubs; BootProgressRuanStubs.c stands in for them. The USB debug link runs \(usb e2829 r1110\) but the Mac never configures it \(c0\).

### Completion criteria

- Each claimed milestone has a reproducible command, a matching source/image revision and an accessible result.

### Current limits

- Hardware inputs and implementation are pending for dizi.

### Next action

- Inventory the required diagnostics inputs before implementation.

### Evidence

Collect evidence using the next action.

</div>
