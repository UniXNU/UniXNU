# Xiaomi Redmi Note 14 Pro+ 5G \(BluedMC-Amethyst\) \(IOS4Amethyst\)

[IOS4Amethyst/UniXNU-amethyst](https://github.com/IOS4Amethyst/UniXNU-amethyst)

<div v-pre>

Xiaomi Redmi Note 14 Pro+ 5G on SM7635 running iPadOS 17.7.11 from RAM: home screen without the lock screen, GPU-composited UI on the Adreno 810, touch, buttons, SMP and CPU frequency scaling \(V52\).

Source record: [porting.toml](https://github.com/IOS4Amethyst/UniXNU-amethyst/blob/9a9a7cb628209d79a81d63e6e936c3e5735d9a59/porting.toml), `9a9a7cb628209d79a81d63e6e936c3e5735d9a59`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `implemented` |
| [Firmware and boot](#firmware) | `device-verified` |
| [CPU and interrupts](#cpu) | `device-verified` |
| [Memory and DMA](#memory) | `implemented` |
| [Storage and root](#storage) | `device-verified` |
| [Display](#display) | `device-verified` |
| [Input](#input) | `device-verified` |
| [GPU](#gpu) | `device-verified` |
| [Network](#network) | `planned` |
| [cellular](#cellular) | `planned` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `implemented` |
| [Image assembly](#packaging) | `device-verified` |
| [Diagnostics](#diagnostics) | `device-verified` |

## Configuration {#configuration}

`implemented`

Components: `ArmDTPlatform`.

### Hardware and dependencies

- SoC SM7635 \(soc\_source sm7635\), OS profile ipados-17.7.11-21H461 \(A10 iPad kernelcache, arm64 without PAC\).
- UniXNU core branch IOS4Amethyst/UniXNU:amethyst-embedded-payload at or after 20437c1.
- UEFI IOS4Amethyst/uefi-amethyst:amethyst at or after 4e6782ba.

### Configuration

- board.toml \[board\] kit = "amethyst"; \[components\] include ArmDTPlatform, ArmCpu, SoftwareAES, RamBlock, XnuPrelink, DarwinBoot, AppleKeyStoreState, AdrenoFirmware, ShengUfs.
- configs/amethyst\_defconfig with arch, sm7635 and ipados config fragments; patch\_series arch, soc \(xnu-12377\), os and device patches/xnu/series.
- \[payload\] kernel\_args keep sheng-data-persist=0 and sheng-log=0; test images enable the log explicitly.

### Procedure

- ./unixnu defconfig amethyst\_defconfig -D ../UniXNU-amethyst
- ./unixnu status --json to confirm the resolved overrides and patch order.

### Development findings

- Sm7635Platform is not selected: board services are provided by board-package code and test kernels instead.
- The board ADT keeps arm\_io\_base 0x01000000; a zero parent base made pe\_identify\_machine return early and skip clock-frequency initialisation.
- drivers/Adreno740 is fetched from IOS4Amethyst/NativeAdreno \(main = 38227e7, the A810 branch of rootstockos/NativeAdreno\); the add-on and seed workflows run by hand from main.

### Completion criteria

- All source pins resolve; every selected component has a record; status shows the intended overrides and patch order.

### Current limits

- Hardware-tested images are packed from local, partly proprietary inputs by scripts/log/pack-log.py; a clean-checkout reproduction is not available.

### Next action

- Pin the core and UEFI revisions used by the latest hardware-tested image in this repository.

### Evidence

- `source`: [Board identity, component selection, payload and ADT settings.](https://github.com/IOS4Amethyst/UniXNU-amethyst/blob/9a9a7cb628209d79a81d63e6e936c3e5735d9a59/board.toml)
- `device`: [V52 \(staging amethyst-addon2-v52, SHA-256 b1a1c8ab...; kernel kernel-swapdiag-v49, add-on c8d14d93...\): iPadOS 17.7.11 reaches the home screen without the lock screen; GPU-composited UI renders correctly; swaps every \~15 ms, done in 10-11 ms; 326 s, 162 log rounds, 0 write errors.](https://github.com/IOS4Amethyst/UniXNU-amethyst/blob/9a9a7cb628209d79a81d63e6e936c3e5735d9a59/scripts/log/WORKING-BOOT.md)
  Command: <code>fastboot -s &lt;serial&gt; boot &lt;image&gt;.img (RAM only); in LineageOS Recovery: python3 scripts/log/pull-log.py --out &lt;result-dir&gt; --serial &lt;serial&gt;</code>. Revision: `8bd7b0d9f312ac5ade7fcacd1404a6e5b4acb7fa`.

## Firmware and boot {#firmware}

`device-verified`

Components: `DarwinBoot`.

### Hardware and dependencies

- Mu-Silicium UEFI for amethyst \(uefi-amethyst:amethyst\), stock Amethyst ClockDxe.
- Android boot image header v4, pagesize 4096, kernel\_offset 0x8000; the bootloader exposes the installed vendor ramdisk, so the payload is embedded in the image.

### Configuration

- \[bootimg.image\] header\_version = 4; \[payload\] loader = "firmware", size\_mib = 80, dram\_size 0x1FFE00000.
- panic\_screen = false: entry/MMU detours are not inserted.

### Procedure

- ./unixnu build firmware --uefi ../uefi-amethyst -D ../UniXNU-amethyst
- ./unixnu bootimg --uefi ../uefi-amethyst --dtb &lt;amethyst.dtb&gt; -D ../UniXNU-amethyst
- fastboot -s &lt;serial&gt; boot &lt;image&gt;.img \(never flash\).

### Development findings

- Enlarging the FAT32 payload requires rebuilding the BootShim: the ARM64 image length and the embedded payload size passed in x2 must match the actual bytes, otherwise UEFI reports no boot entry.
- GPU images use firmware whose PrePi reserves a GMU\_Pool region \(DXE\_Heap1 entry patched in place\).

### Completion criteria

- Firmware image builds, enters UniXNU, publishes the framebuffer and preserves the documented memory reservations.

### Current limits

- The GMU\_Pool firmware patch is a local tool and not part of uefi-amethyst yet.

### Next action

- Move the GMU\_Pool reservation into the uefi-amethyst platform configuration.

### Evidence

- `device`: [Redmi Note 14 Pro+ 5G \(amethyst\), iPadOS 17.7.11 21H461: image amethyst-cpu-present-scale2 \(SHA-256 6913b06f...\) reached the Apple UI on 2026-11-02; kernel UUID E37ABB7B-1B56-31D9-9351-90EDCD61DEDB; 144 log rounds, zero write errors.](https://github.com/IOS4Amethyst/UniXNU-amethyst/blob/9a9a7cb628209d79a81d63e6e936c3e5735d9a59/scripts/log/WORKING-BOOT.md)
  Command: <code>fastboot -s &lt;serial&gt; boot &lt;image&gt;.img (RAM only); in LineageOS Recovery: python3 scripts/log/pull-log.py --out &lt;result-dir&gt; --serial &lt;serial&gt;</code>. Revision: `140c844d1118e55e570d2f0ee39113d7635bf211`.
- `device`: [V52 \(staging amethyst-addon2-v52, SHA-256 b1a1c8ab...; kernel kernel-swapdiag-v49, add-on c8d14d93...\): iPadOS 17.7.11 reaches the home screen without the lock screen; GPU-composited UI renders correctly; swaps every \~15 ms, done in 10-11 ms; 326 s, 162 log rounds, 0 write errors.](https://github.com/IOS4Amethyst/UniXNU-amethyst/blob/9a9a7cb628209d79a81d63e6e936c3e5735d9a59/scripts/log/WORKING-BOOT.md)
  Command: <code>fastboot -s &lt;serial&gt; boot &lt;image&gt;.img (RAM only); in LineageOS Recovery: python3 scripts/log/pull-log.py --out &lt;result-dir&gt; --serial &lt;serial&gt;</code>. Revision: `8bd7b0d9f312ac5ade7fcacd1404a6e5b4acb7fa`.

## CPU and interrupts {#cpu}

`device-verified`

Components: `ArmCpu`.

### Hardware and dependencies

- 8 CPUs: cpu0 boots running \(Cortex-A520 little core\), cpu1-7 waiting in the ADT.
- EPSS cpufreq domains 0x17d91000/0x17d92000/0x17d93000 with 4/3/1 CPUs \(volcano.dtsi\).

### Configuration

- sheng-smp=1 armcpu-spi-ipi=1 armcpu-self-ipi=1 bring up and signal the secondaries.
- sheng-cpufreq=4 enables the governor \(16 ms windows, schedutil margin, 4-window step-down\).

### Procedure

- Add the SMP and cpufreq arguments \(pack-log.py --smp --cpufreq 4\), boot, pull the log, read the AmethystSmp and \[clocks\]/\[cpu gov\] rows.

### Development findings

- Without armcpu-self-ipi=1 the secondaries keep SIGPdisabled until their first IPI, so a stackshot \(DebuggerXCallEnter\) could not signal them and the boot hung.
- Booting all 8 cores cut time to the lock screen from about 272 s to about 152 s.
- scripts/log/AmethystSmc.c carries the SMC call helper used by the GPU zap load.

### Completion criteria

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU.

### Current limits

- Idle states beyond the AmethystCpuIdle helper are not implemented.

### Next action

- Measure idle residency and power with the governor active.

### Evidence

- `device`: [V25: IPIs taken on all 8 cores, sigpoff=00, no cpu\_signal failures. V23: governor scales d0 441-1804 MHz, d1 1286-2400 MHz, d2 1324-2304 MHz.](https://github.com/IOS4Amethyst/UniXNU-amethyst/blob/9a9a7cb628209d79a81d63e6e936c3e5735d9a59/scripts/log/WORKING-BOOT.md)
  Command: <code>fastboot -s &lt;serial&gt; boot &lt;image&gt;.img (RAM only); in LineageOS Recovery: python3 scripts/log/pull-log.py --out &lt;result-dir&gt; --serial &lt;serial&gt;</code>. Revision: `3fae65e8701c70db957c701f0873fa48d9196846`.

## Memory and DMA {#memory}

`implemented`

### Hardware and dependencies

- DRAM size 0x1FFE00000; owned memory 0x130000000.
- GPU SMMU context bank and GMU pool reservations.

### Configuration

- \[payload\] dram\_size = "0x1FFE00000"; \[payload.adt\] owned\_memory\_size = "0x130000000".
- dts/amethyst.dts describes the board memory and peripherals.

### Procedure

- Build the payload and check the ADT with scripts/check-adt-spmi.py ../UniXNU &lt;hardware.dtb&gt;.

### Development findings

- PMIC/RTC SPMI-local registers cannot be flattened into MMIO, so the board omits their ADT export markers.
- The GMU pool round trip \(32 MiB, write-combined\) passed with 0 pattern errors once firmware reserved it.

### Completion criteria

- All handoff regions are accounted for and each enabled DMA engine accesses its allocated range with the documented cache policy.

### Current limits

- UFS controller DMA/SMMU ownership is not taken over \(native-ufs-root=0 by default\).

### Next action

- Record SMMU stream ownership for UFS before enabling controller takeover.

### Evidence

- `source`: [Board device tree used for the ADT.](https://github.com/IOS4Amethyst/UniXNU-amethyst/blob/9a9a7cb628209d79a81d63e6e936c3e5735d9a59/dts/amethyst.dts)

## Storage and root {#storage}

`device-verified`

Components: `ShengUfs`, `VirtioMmioBlock`, `VerifiedRoot`, `RamBlock`, `SoftwareAES`, `AppleKeyStoreState`.

### Hardware and dependencies

- Dedicated unixnu partition holding the signed OS and SystemOS windows; Android userdata \(F2FS\) is never written.
- Root volume UUID 04769D26-2CA0-4825-B443-E2E5F88300F2; pinned 21H461 Static/System trust caches.

### Configuration

- \[payload.adt\] root\_match\_volume\_uuid, packed\_data\_ramdisk = true, persistent\_data = false.
- Board default native-ufs-root=0 \(takeover off\); sheng-data-persist=0.
- Data is a RAM seed packed into the image \(skip-setup-seed branch\).

### Procedure

- Pack the image with a Data seed \(pack-log.py --data-seed\), fastboot boot, confirm launchd and SpringBoard in the pulled log.

### Development findings

- Mounting SystemOS alone did not satisfy the shared-region carrier policy; the owner cache carrier requires read-only root/cache mounts with the exact signed UUIDs.
- On split devices persistent Data and log/export opens stay disabled; the log uses only the last 32 MiB of unixnu.
- The AppleKeyStore stand-in \(sheng-aks=1\) reports no keybag and no passcode, so the lock screen dismisses; it protects nothing.

### Completion criteria

- Host: register, clock, link and SMMU facts match the board inventory.
- Reads: SCSI capacity, GPT and known blocks are correct; OS/SystemOS windows stay within the root partition.
- Root: the configured volume mounts and launchd starts. Persistence: writes survive reboot within the allocated Data region.

### Current limits

- No persistence: Data is rebuilt from the RAM seed on every boot.
- A validated write plan for a persistent Data region does not exist.

### Next action

- Design and review a persistent Data allocation inside the unixnu partition.

### Evidence

- `device`: [Redmi Note 14 Pro+ 5G \(amethyst\), iPadOS 17.7.11 21H461: image amethyst-cpu-present-scale2 \(SHA-256 6913b06f...\) reached the Apple UI on 2026-11-02; kernel UUID E37ABB7B-1B56-31D9-9351-90EDCD61DEDB; 144 log rounds, zero write errors.](https://github.com/IOS4Amethyst/UniXNU-amethyst/blob/9a9a7cb628209d79a81d63e6e936c3e5735d9a59/scripts/log/WORKING-BOOT.md)
  Command: <code>fastboot -s &lt;serial&gt; boot &lt;image&gt;.img (RAM only); in LineageOS Recovery: python3 scripts/log/pull-log.py --out &lt;result-dir&gt; --serial &lt;serial&gt;</code>. Revision: `140c844d1118e55e570d2f0ee39113d7635bf211`.
- `source`: [Root, SystemOS and cache-carrier bring-up record.](https://github.com/IOS4Amethyst/UniXNU-amethyst/blob/9a9a7cb628209d79a81d63e6e936c3e5735d9a59/ROOT-BRINGUP.md)
- `device`: [V52 \(staging amethyst-addon2-v52, SHA-256 b1a1c8ab...; kernel kernel-swapdiag-v49, add-on c8d14d93...\): iPadOS 17.7.11 reaches the home screen without the lock screen; GPU-composited UI renders correctly; swaps every \~15 ms, done in 10-11 ms; 326 s, 162 log rounds, 0 write errors.](https://github.com/IOS4Amethyst/UniXNU-amethyst/blob/9a9a7cb628209d79a81d63e6e936c3e5735d9a59/scripts/log/WORKING-BOOT.md)
  Command: <code>fastboot -s &lt;serial&gt; boot &lt;image&gt;.img (RAM only); in LineageOS Recovery: python3 scripts/log/pull-log.py --out &lt;result-dir&gt; --serial &lt;serial&gt;</code>. Revision: `8bd7b0d9f312ac5ade7fcacd1404a6e5b4acb7fa`.

## Display {#display}

`device-verified`

### Hardware and dependencies

- 1220x2712 panel exposed by UEFI GOP; IOMobileFramebufferLegacy ABI of 21H461.

### Configuration

- offline-mobile-graphics-load=1 offline-legacy-register=1 offline-legacy-phase=4 offline-legacy-gop=1 offline-legacy-pm=1 offline-legacy-unit-scale=2 offline-legacy-validate=1 offline-legacy-transfer=1 offline-legacy-cpu-present=1.
- amethyst-panel=3 \(pack-log --panel 3\): the iOS brightness service over DSI0 DCS.

### Procedure

- pack-log.py --display-probe --display-pm --display-unit-scale 2 --display-validate --display-cpu-present, then boot.

### Development findings

- NativeLegacyDisplay rejects pipeline-disabled swaps and keeps accepted requests in its tracking table.
- validateSwap accepts plain BGRA or one-plane &amp;BGA only; Apple-compressed two-plane framebuffers are refused, so the Data seed disables CA framebuffer compression.
- Presenting by CPU copy costs about 170 ms per frame; the GPU hand-off presenter \(sheng-fb-gpu=1, sheng-vsync=120\) brings swaps to about 10 ms.
- The o16u AMOLED has no backlight chip \(bl\_ctrl\_dcs\): brightness is DCS 0x51 hi lo, 8..4095. Commands go through DSI0's TPG command FIFO on the first front-porch line \(ported from UniXNU-asteroids PanelProbe.cpp, same SM7635 DSI0 0x0ae94000\), with no DMA buffer or display SMMU mapping.
- AmethystBacklight conforms to AppleARMBacklight with backlight-control; level 0 turns the panel off \(28, 10\) and the next level on \(11, 120 ms, 29\).

### Completion criteria

- A known frame appears with correct geometry and colors, then userland presentation and backlight controls work.

### Current limits

- Brightness is the panel's normal range \(max 4095\); the panel's high-brightness range and nits calibration are not used.

### Next action

- Publish nits calibration for iPadOS 27's brightness-nits path.

### Evidence

- `device`: [Redmi Note 14 Pro+ 5G \(amethyst\), iPadOS 17.7.11 21H461: image amethyst-cpu-present-scale2 \(SHA-256 6913b06f...\) reached the Apple UI on 2026-11-02; kernel UUID E37ABB7B-1B56-31D9-9351-90EDCD61DEDB; 144 log rounds, zero write errors.](https://github.com/IOS4Amethyst/UniXNU-amethyst/blob/9a9a7cb628209d79a81d63e6e936c3e5735d9a59/scripts/log/WORKING-BOOT.md)
  Command: <code>fastboot -s &lt;serial&gt; boot &lt;image&gt;.img (RAM only); in LineageOS Recovery: python3 scripts/log/pull-log.py --out &lt;result-dir&gt; --serial &lt;serial&gt;</code>. Revision: `140c844d1118e55e570d2f0ee39113d7635bf211`.
- `device`: [V52 \(staging amethyst-addon2-v52, SHA-256 b1a1c8ab...; kernel kernel-swapdiag-v49, add-on c8d14d93...\): iPadOS 17.7.11 reaches the home screen without the lock screen; GPU-composited UI renders correctly; swaps every \~15 ms, done in 10-11 ms; 326 s, 162 log rounds, 0 write errors.](https://github.com/IOS4Amethyst/UniXNU-amethyst/blob/9a9a7cb628209d79a81d63e6e936c3e5735d9a59/scripts/log/WORKING-BOOT.md)
  Command: <code>fastboot -s &lt;serial&gt; boot &lt;image&gt;.img (RAM only); in LineageOS Recovery: python3 scripts/log/pull-log.py --out &lt;result-dir&gt; --serial &lt;serial&gt;</code>. Revision: `8bd7b0d9f312ac5ade7fcacd1404a6e5b4acb7fa`.
- `device`: [V60 \(staging amethyst-tap-v60, SHA-256 fbfd6f43...\): the Control Center brightness slider changes the panel, and lock and unlock turn it off and on.](https://github.com/IOS4Amethyst/UniXNU-amethyst/blob/9a9a7cb628209d79a81d63e6e936c3e5735d9a59/scripts/log/WORKING-BOOT.md)
  Command: <code>fastboot -s &lt;serial&gt; boot &lt;image&gt;.img (RAM only); in LineageOS Recovery: python3 scripts/log/pull-log.py --out &lt;result-dir&gt; --serial &lt;serial&gt;</code>. Revision: `a0c98e8c859b4cb2dcc65f57a9afb367b9e0e0dc`.

## Input {#input}

`device-verified`

### Hardware and dependencies

- Goodix Berlin touch controller on a GENI SPI bus; 18x40 sensor grid.
- Volume and power keys on the PMIC \(SPMI\).

### Configuration

- sheng-touch-hid=1 publishes touches as a HID digitizer; amethyst-touch-ids=N cycles contact identifiers 1..N \(default 8\); amethyst-touch-record-button=1 records frames until a button press.

### Procedure

- pack-log.py --touch-snapshot --touch-goodix --touch-frames --touch-hid --buttons, boot, read the AmethystTouch and AmethystHid rows in the pulled log.

### Development findings

- The grid starts 20 bytes after head+attr+log; the 18 axis is screen x \(0 left\), the 40 axis screen y \(0 top\).
- Boot UI animation shifts whole drive lines by +-500 counts; the detector removes each line's shift and needs an adjacent-line neighbour, which removed all false presses.
- backboardd drops digitizer events unless the driver publishes Built-In, DisplayIntegrated and PrimaryUsage 0x0D/4.
- Touch stopped after \~30 presses with contact identifiers 1..200; cycling 1..8 fixed it \(V54\). The corner guard was removed \(V55\).
- Without the In Range usage iOS took a lift for a hover and continued an old touch on the next press with that identifier \(a tap reopened Search\); patches/ShengHidInput/0001 adds it.
- A lifting finger's position jumped to a weak dip on the bottom line, so swipes up stuttered; a press now follows only its finger's neighbourhood \(41 jumps to 0 on V56's recording\).
- Taps wandered 10-47 pt as the finger rolled off; a 17 pt tap slop that ignores roll-off frames and a depth-past-floor centroid cut them from 16 of 29 to 7 of 37 without slowing swipes \(V58 recording\).

### Completion criteria

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive, and buttons produce expected HID reports.

### Current limits

- Single contact only.
- Some taps still move up to \~20 pt along the 18-row axis.

### Next action

- Track a second contact for multi-touch.

### Evidence

- `device`: [V29: exactly one press for one tap, none during boot. V30: IOHIDEventDriver attached, 3595 touch reports rc=0. V37: replay matches the user's taps; all 64 presses reported.](https://github.com/IOS4Amethyst/UniXNU-amethyst/blob/9a9a7cb628209d79a81d63e6e936c3e5735d9a59/scripts/log/WORKING-BOOT.md)
  Command: <code>fastboot -s &lt;serial&gt; boot &lt;image&gt;.img (RAM only); in LineageOS Recovery: python3 scripts/log/pull-log.py --out &lt;result-dir&gt; --serial &lt;serial&gt;</code>. Revision: `3fae65e8701c70db957c701f0873fa48d9196846`.
- `device`: [V52 \(staging amethyst-addon2-v52, SHA-256 b1a1c8ab...; kernel kernel-swapdiag-v49, add-on c8d14d93...\): iPadOS 17.7.11 reaches the home screen without the lock screen; GPU-composited UI renders correctly; swaps every \~15 ms, done in 10-11 ms; 326 s, 162 log rounds, 0 write errors.](https://github.com/IOS4Amethyst/UniXNU-amethyst/blob/9a9a7cb628209d79a81d63e6e936c3e5735d9a59/scripts/log/WORKING-BOOT.md)
  Command: <code>fastboot -s &lt;serial&gt; boot &lt;image&gt;.img (RAM only); in LineageOS Recovery: python3 scripts/log/pull-log.py --out &lt;result-dir&gt; --serial &lt;serial&gt;</code>. Revision: `8bd7b0d9f312ac5ade7fcacd1404a6e5b4acb7fa`.
- `device`: [V60 \(staging amethyst-tap-v60, SHA-256 fbfd6f43...\): taps, scrolling, swipes up from the bottom, brightness and lock/unlock confirmed by the user.](https://github.com/IOS4Amethyst/UniXNU-amethyst/blob/9a9a7cb628209d79a81d63e6e936c3e5735d9a59/scripts/log/WORKING-BOOT.md)
  Command: <code>fastboot -s &lt;serial&gt; boot &lt;image&gt;.img (RAM only); in LineageOS Recovery: python3 scripts/log/pull-log.py --out &lt;result-dir&gt; --serial &lt;serial&gt;</code>. Revision: `5b9c6ed8b9e7329e12c4da2a338a2ed0295adbe8`.

## GPU {#gpu}

`device-verified`

Components: `AdrenoFirmware`.

### Hardware and dependencies

- Adreno 810 \(chip 44010000, gen80300\): gen80300\_sqe.fw and gen80300\_gmu.bin match UniXNU-asteroids; gen80300\_zap.mbn is the OEM-signed amethyst copy.
- GMU\_Pool reserved by firmware.

### Configuration

- sheng-gpu-power=19 sheng-gpu-addon=1 sheng-gpu-irq=0 sheng-fb-gpu=1 sheng-vsync=120.
- GPU add-on \(Metal plugin + Turnip\) and owner trust bundle built by the gpu-addon branch CI.

### Procedure

- Build the add-on on the gpu-addon branch, pack with pack-log.py --gpu-power 19 --gpu-addon &lt;addon&gt; --owner-trust &lt;bundle&gt; --fb-gpu, boot.

### Development findings

- CX GDSC, SMMU vote and the GMU pool round trip pass once firmware reserves GMU\_Pool.
- Zap loads through SCM PAS 13 with amethyst's own gen80300\_zap.mbn; CP init, CP\_MEM\_WRITE and the first IB pass.
- The sandbox grant matches exact process names: it must name backboardd for the render server to open the GPU.
- backboardd composited into Apple-compressed two-plane framebuffers until the Data seed set CAEnableFramebufferCompression, CAEnableDeepFramebuffer and CAEnableIOSurfaceCompression false.
- An add-on built against an older UniXNU drew garbled text and hung the GPU; rebuilding it from rootstockos/UniXNU bd4766ae with NativeAdreno 38227e7 fixed both.
- A submission pins only its IBs: freeing a texture a queued job still read left the GPU on a translation fault and the CP stuck \(V56, spamming Spotlight\). NativeAdreno 26c1da7 keeps a freed BO mapped until the client's pending jobs pass it.
- NativeAdreno detects hangs but nothing installs its restart hook, so a hang is counted and never recovered.

### Completion criteria

- GPU submissions complete, mapping/fence handling is correct, a known image renders, and the selected Metal client presents it.

### Current limits

- Some GPU clients \(mediaserverd, widget and poster renderers\) report Vulkan -3.
- Occasional GPU stalls are recovered by a kick.
- No GPU restart after a hang \(a8xx recovery is a CX GDSC collapse and GMU cold start\).

### Next action

- Investigate the clients without a Vulkan device and the stall/kick events.

### Evidence

- `device`: [V42: modes 12-16 pass, first IB and a bar drawn into the console framebuffer \(pixels read back\). V43: user-client test 115/115 steps, 32/32 burst submissions matched.](https://github.com/IOS4Amethyst/UniXNU-amethyst/blob/9a9a7cb628209d79a81d63e6e936c3e5735d9a59/scripts/log/WORKING-BOOT.md)
  Command: <code>fastboot -s &lt;serial&gt; boot &lt;image&gt;.img (RAM only); in LineageOS Recovery: python3 scripts/log/pull-log.py --out &lt;result-dir&gt; --serial &lt;serial&gt;</code>. Revision: `3fae65e8701c70db957c701f0873fa48d9196846`.
- `device`: [V52 \(staging amethyst-addon2-v52, SHA-256 b1a1c8ab...; kernel kernel-swapdiag-v49, add-on c8d14d93...\): iPadOS 17.7.11 reaches the home screen without the lock screen; GPU-composited UI renders correctly; swaps every \~15 ms, done in 10-11 ms; 326 s, 162 log rounds, 0 write errors.](https://github.com/IOS4Amethyst/UniXNU-amethyst/blob/9a9a7cb628209d79a81d63e6e936c3e5735d9a59/scripts/log/WORKING-BOOT.md)
  Command: <code>fastboot -s &lt;serial&gt; boot &lt;image&gt;.img (RAM only); in LineageOS Recovery: python3 scripts/log/pull-log.py --out &lt;result-dir&gt; --serial &lt;serial&gt;</code>. Revision: `8bd7b0d9f312ac5ade7fcacd1404a6e5b4acb7fa`.
- `device`: [V58: 1638 freed BOs deferred and all reaped, 16 maps waited for one, no SMMU fault and no hang in 7 minutes of use including repeated Spotlight.](https://github.com/IOS4Amethyst/UniXNU-amethyst/blob/9a9a7cb628209d79a81d63e6e936c3e5735d9a59/scripts/log/WORKING-BOOT.md)
  Command: <code>fastboot -s &lt;serial&gt; boot &lt;image&gt;.img (RAM only); in LineageOS Recovery: python3 scripts/log/pull-log.py --out &lt;result-dir&gt; --serial &lt;serial&gt;</code>. Revision: `b2a18ee8dd69c2db5781b6af82b2d2b1bd54c063`.

## Network {#network}

`planned`

### Hardware and dependencies

- Wi-Fi and Bluetooth hardware, bus and firmware are not inventoried yet.

### Configuration

- No network component is selected.

### Procedure

- Inventory the Wi-Fi/Bluetooth chip, bus and firmware from the Android device tree and vendor partitions.

### Development findings

- No network work has been started.

### Completion criteria

- Scanning, association, address configuration and sustained receive/transmit traffic pass with the selected firmware.

### Current limits

- Not implemented.

### Next action

- Identify the Wi-Fi chip and its bus from the Android DTB.

### Evidence

Collect evidence using the next action.

## cellular {#cellular}

`planned`

### Hardware and dependencies

- The device has a modem; firmware, EFS/NV and QRTR/QMI interfaces are not inventoried.

### Configuration

- No cellular component is selected.

### Procedure

- Inventory the modem firmware and the remoteproc/QRTR path on Android.

### Development findings

- No cellular work has been started.

### Completion criteria

- The modem boots, the SIM is identified, the network registers and a data session carries traffic.

### Current limits

- Not implemented.

### Next action

- Record the modem firmware files and remoteproc layout from the Android vendor partitions.

### Evidence

Collect evidence using the next action.

## Audio {#audio}

`planned`

### Hardware and dependencies

- ADSP firmware, codec and routes are not inventoried.

### Configuration

- No audio component is selected.

### Procedure

- Inventory the ADSP firmware and codec from the Android device tree.

### Development findings

- Only the sheng audio ABI header is carried for log tooling.

### Completion criteria

- Each declared route carries the selected audio format through playback or capture and handles start/stop correctly.

### Current limits

- Not implemented.

### Next action

- Identify the codec and ADSP firmware.

### Evidence

Collect evidence using the next action.

## Power {#power}

`implemented`

### Hardware and dependencies

- ApplePMGR provider required by AMFI; RPMh votes for touch and GPU clocks.

### Configuration

- sheng-pmgr=2; package/ShengPlatformPower.cpp built by scripts/build-amethyst-platform-power.py.

### Procedure

- Build the kernel; the platform power archive is linked from board.toml archives.

### Development findings

- The guarded ApplePMGR provider only publishes what AMFI needs; unimplemented power operations panic rather than touch unqualified registers.
- watchdogd traps without a backend, so the Data seed disables it.
- GPU power-up \(CX GDSC, SMMU vote clock, GMU votes\) runs from GpuPowerProbe modes 1-19; scripts/log/check-gpu-power.c covers the GMU pool round trip on the host.

### Completion criteria

- Declared power controls and battery readings match observations; each claimed sleep/resume transition restores its dependent peripherals.

### Current limits

- No battery, charging, suspend or watchdog backend.

### Next action

- Inventory the battery manager interface and add a watchdog backend.

### Evidence

- `source`: [Guarded ApplePMGR provider.](https://github.com/IOS4Amethyst/UniXNU-amethyst/blob/9a9a7cb628209d79a81d63e6e936c3e5735d9a59/package/ShengPlatformPower.cpp)

## Image assembly {#packaging}

`device-verified`

Components: `XnuPrelink`.

### Hardware and dependencies

- XNU xnu-12377 with arch, soc, os and device patch series; iPadOS 17.7.11 21H461 kernelcache for prelink.

### Configuration

- Payload FAT32, 80 MiB; embedded in the Android v4 boot image.

### Procedure

- ./unixnu build kernel -D ../UniXNU-amethyst
- ./unixnu build payload --unique-chip-id &lt;hex&gt; --uefi ../uefi-amethyst --edk2 ../uefi-amethyst/Mu\_Basecore -D ../UniXNU-amethyst
- For test images: compile -&gt; link -&gt; prelink -&gt; scripts/log/pack-log.py.

### Development findings

- Test kernels use the unchanged original pe\_init.o object; hand-assembled pe\_init flags caused an earlier regression.
- pack-log.py --aks adds sheng-aks=1; --fb-gpu adds sheng-fb-gpu=1 sheng-vsync=120 and requires --gpu-addon.

### Completion criteria

- Kernel and prelink succeed, payload contains all declared inputs, and the boot image matches the bootloader format and size limit.

### Current limits

- pack-log.py needs the local owner-union baseline and firmware shim; this is packaging replay, not a portable build.

### Next action

- Make the hardware-tested image reproducible from a clean checkout plus documented local inputs.

### Evidence

- `device`: [Redmi Note 14 Pro+ 5G \(amethyst\), iPadOS 17.7.11 21H461: image amethyst-cpu-present-scale2 \(SHA-256 6913b06f...\) reached the Apple UI on 2026-11-02; kernel UUID E37ABB7B-1B56-31D9-9351-90EDCD61DEDB; 144 log rounds, zero write errors.](https://github.com/IOS4Amethyst/UniXNU-amethyst/blob/9a9a7cb628209d79a81d63e6e936c3e5735d9a59/scripts/log/WORKING-BOOT.md)
  Command: <code>fastboot -s &lt;serial&gt; boot &lt;image&gt;.img (RAM only); in LineageOS Recovery: python3 scripts/log/pull-log.py --out &lt;result-dir&gt; --serial &lt;serial&gt;</code>. Revision: `140c844d1118e55e570d2f0ee39113d7635bf211`.
- `device`: [V52 \(staging amethyst-addon2-v52, SHA-256 b1a1c8ab...; kernel kernel-swapdiag-v49, add-on c8d14d93...\): iPadOS 17.7.11 reaches the home screen without the lock screen; GPU-composited UI renders correctly; swaps every \~15 ms, done in 10-11 ms; 326 s, 162 log rounds, 0 write errors.](https://github.com/IOS4Amethyst/UniXNU-amethyst/blob/9a9a7cb628209d79a81d63e6e936c3e5735d9a59/scripts/log/WORKING-BOOT.md)
  Command: <code>fastboot -s &lt;serial&gt; boot &lt;image&gt;.img (RAM only); in LineageOS Recovery: python3 scripts/log/pull-log.py --out &lt;result-dir&gt; --serial &lt;serial&gt;</code>. Revision: `8bd7b0d9f312ac5ade7fcacd1404a6e5b4acb7fa`.

## Diagnostics {#diagnostics}

`device-verified`

### Hardware and dependencies

- LineageOS Recovery with adb; the last 32 MiB of the unixnu partition as the log window.

### Configuration

- sheng-log=1 \(test images\) writes the message buffer and periodic snapshot slots to the log window.

### Procedure

- Boot the image, reboot to recovery, run python3 scripts/log/pull-log.py --out &lt;dir&gt; --serial &lt;serial&gt;, read latest.txt, slots.txt and msgbuf.txt.

### Development findings

- The panic hook does not write UFS; periodic writes continue during normal operation.
- The log is found by partition name in recovery because this device keeps its root image in a split partition.
- Row 48 shows the swap rejection reason \(why=, surface format and planes\) once a swap is refused.

### Completion criteria

- Each claimed milestone has a reproducible command, a matching source/image revision and an accessible result.

### Current limits

- Raw boot logs are kept locally and are not published as artifacts.

### Next action

- Publish redacted boot logs for each milestone as release or CI artifacts.

### Evidence

- `device`: [Redmi Note 14 Pro+ 5G \(amethyst\), iPadOS 17.7.11 21H461: image amethyst-cpu-present-scale2 \(SHA-256 6913b06f...\) reached the Apple UI on 2026-11-02; kernel UUID E37ABB7B-1B56-31D9-9351-90EDCD61DEDB; 144 log rounds, zero write errors.](https://github.com/IOS4Amethyst/UniXNU-amethyst/blob/9a9a7cb628209d79a81d63e6e936c3e5735d9a59/scripts/log/WORKING-BOOT.md)
  Command: <code>fastboot -s &lt;serial&gt; boot &lt;image&gt;.img (RAM only); in LineageOS Recovery: python3 scripts/log/pull-log.py --out &lt;result-dir&gt; --serial &lt;serial&gt;</code>. Revision: `140c844d1118e55e570d2f0ee39113d7635bf211`.
- `device`: [V52 \(staging amethyst-addon2-v52, SHA-256 b1a1c8ab...; kernel kernel-swapdiag-v49, add-on c8d14d93...\): iPadOS 17.7.11 reaches the home screen without the lock screen; GPU-composited UI renders correctly; swaps every \~15 ms, done in 10-11 ms; 326 s, 162 log rounds, 0 write errors.](https://github.com/IOS4Amethyst/UniXNU-amethyst/blob/9a9a7cb628209d79a81d63e6e936c3e5735d9a59/scripts/log/WORKING-BOOT.md)
  Command: <code>fastboot -s &lt;serial&gt; boot &lt;image&gt;.img (RAM only); in LineageOS Recovery: python3 scripts/log/pull-log.py --out &lt;result-dir&gt; --serial &lt;serial&gt;</code>. Revision: `8bd7b0d9f312ac5ade7fcacd1404a6e5b4acb7fa`.

</div>
