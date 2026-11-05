# Xiaomi MIX Fold 2 \(zizhan, SM8475\): UniXNU bring-up derived from Pong

[qiumochen/UniXNU-zizhan](https://github.com/qiumochen/UniXNU-zizhan)

<div v-pre>

Xiaomi MIX Fold 2: iPadOS 18.7.10 inner display, touch, Adreno 730 rendering and battery readings, derived from UniXNU-pong. A 120 Hz panel and 95.3 moving fps in one synthetic workload; experimental Wi-Fi HTTPS works, Settings join and cross-band reconnect remain unresolved.

Source record: [porting.toml](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/porting.toml), `3b3c52fb5ba11b0a185703d7832fd567c94e770e`.

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
| [Network](#network) | `device-verified` |
| [cellular](#cellular) | `planned` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `implemented` |
| [Image assembly](#packaging) | `host-verified` |
| [Diagnostics](#diagnostics) | `implemented` |

## Configuration {#configuration}

`host-verified`

Components: `PongPlatform24`.

### Hardware and dependencies

- zizhan \(22061218C\) live /sys/firmware/fdt; MIUI V14.0.15.0.TLRCNXM, Android 13, kernel 5.10.136.
- SM8475 shared support and PongPlatform24 from UniXNU-pong \(Nothing Phone \(2\)\).
- iPad7,11 iPadOS 18.7.10 / 22H374 restore.

### Configuration

- board.toml: name=zizhan; device\_tree.source=device:dts/zizhan.dts; kernel.defconfig=zizhan\_ipados18\_gpu\_defconfig.
- Default GPU config: CONFIG\_XNU\_PONG\_ADRENO\_PLATFORM=y, CONFIG\_XNU\_PONG\_POWER=y, CONFIG\_XNU\_PONG\_WIFI=y, CONFIG\_XNU\_PONG\_BACKLIGHT=n.
- Apply patches/xnu-ipados18/series in order: 0001-0006 and 0008-0014.

### Procedure

- Generate dts/zizhan.dts from the live DT with tools/gen\_reserved.py, replacing model, compatible, DRAM and reserved-memory in the Pong layout.
- Select uefi-zizhan Platforms/Xiaomi/zizhanPkg/zizhan.dsc; retain ARM64, SM8475, 22H374 and board layers.

### Development findings

- The second DRAM bank is 0xf4600000+0xba00000, versus Pong 0xf1400000+0xec00000. ADSP uses 0x9fd00000+0x3100000, versus Pong 0x85700000+0x2800000. SMEM, IPCC, AOSS and cmd-db addresses agree.
- The Pong build scripts do not depend on the board name.
- The device default now enables GPU and Wi-Fi together. The old Wi-Fi defconfig is a relative symlink to the canonical GPU defconfig; local default build/packaging no longer needs separate profile or radio-enable options. The board-specific Wi-Fi hardware inputs remain in zizhan-wifi-sm8475.json.
- One canonical device defconfig enables GPU and Wi-Fi; the previous Wi-Fi name is a compatibility symlink. Default and explicit reduced CI kernels built successfully.

### Completion criteria

- Compile the board DTS, kernel and boot image, then reach the iPadOS Home Screen on the phone.

### Current limits

- Outer display and audio remain disabled. Default GPU/Wi-Fi integration does not qualify untested long-duration or broader network cases; see the network limits.

### Next action

- Keep build and device evidence separate and reproduce the published configuration before changing board inputs.

### Evidence

- `device`: [Combined device defaults without DEFCONFIG/PROFILE/WIFI overrides passed native automatic association, keys, DHCP and HTTPS 200. Zero link loss or canvas-mapping errors; three complete Settings screenshots, deadline return and fresh UFS log.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-05-default-gpu-wifi.txt)
  Command: <code>cycle.sh out/g344-default-combined/pong-xnu-initial.img g344-default-combined 480</code>. Revision: `cc016a5c44c1ed074e98ea7c1104c1e5cbdff88f`.
- `host`: [One canonical device defconfig enables GPU and Wi-Fi; the previous Wi-Fi name is a compatibility symlink. Default and explicit reduced CI kernels built successfully.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-05-default-gpu-wifi.txt)
  Command: <code>ci_kernel.sh default and explicit CI; ci_boot_ufs.sh default/WIFI=0/explicit CI; check-wifi-host.py</code>. Revision: `cc016a5c44c1ed074e98ea7c1104c1e5cbdff88f`.
- `source`: [Live hardware, partition backup and stock UEFI memory-map comparison.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-10-28-device-prep.md)
- `source`: [Board-specific addresses and differences from Pong.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-01-battery.md)
- `host`: [Hosted macos-15-intel runner resolved four layers, compiled the DTS, applied 13 XNU patches and linked the CI kernel; pong-macos-products uploaded.](https://github.com/qiumochen/UniXNU-zizhan/actions/runs/41304992346)
  Command: <code>GitHub Actions zizhan macOS build (macos-15-intel, Xcode 16.4, pong_ipados18_ci_defconfig)</code>. Revision: `28d9f4fe869293e7a384b18b800ceb8dd56c1244`.

## Firmware and boot {#firmware}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- uefi-zizhan: uefi-pong plus Platforms/Xiaomi/zizhanPkg.
- Stock uefi\_b uefiplat.cfg memory map.

### Configuration

- PIL Reserved size=0x1DC00000; remove Demura and QTEE.
- SimpleFbDxe: framebuffer=0xb8000000, 2160x1916, inherited cont\_splash\_region.
- Temporary fastboot boot only; do not flash partitions.

### Procedure

- build\_fw.sh builds the zizhanPkg FD with EDK II; build\_bootimg.py combines BootShim, FD and the device DTB into boot v4.
- DarwinBoot24 reads the UniXNU menu and arms pong\_autoreset before XNU handoff.
- ci\_boot\_ufs.sh rejects command lines above its 1020-byte limit; DarwinBoot24 requires fewer than 1024 bytes.

### Development findings

- The inner panel shows the Silicium logo and UniXNU menu with correct color and orientation; DarwinBoot24 hands off to XNU.
- On refusal, DarwinBoot24 appends the reason to logfs:\\BOOTFAIL.TXT, retries, then returns to fastboot.
- A Wi-Fi kernel with larger embedded firmware occupied the temporary low-memory ReadFile buffer while the loader requested scanout pages. Free copied kernel/ADT inputs before reserving the optional 96 MiB pool. g299/g300 used the same kernel with radio disabled; the changed loader restored the real pool and complete screenshots.

### Completion criteria

- Temporary boot reaches the menu and XNU; failures retain an automatic return path.

### Current limits

- Qualcomm DXE binaries still come from uefi-pong Binaries/pong. There is no zizhan DisplayDxe and the outer panel stays off.

### Next action

- Audit the stock FV Panel\_L18\_38\_0c\_0a\_sec\_dsc\_cmd.xml before attempting outer-panel support.

### Evidence

- `device`: [Loader-only comparison changed no-pool fallback into a real 96 MiB zero-copy pool and full sampled screenshot.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-04-wifi-settings-and-roaming.txt)
  Command: <code>cycle.sh g299-wifi-kernel-radio-off; cycle.sh g300-loader-radio-off</code>. Revision: `03363797d9ffb10fd35ad5823331e89b4bb3c624`.
- `source`: [Device record of UEFI, DarwinBoot24 handoff and early XNU boot.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-10-29-xnu-bringup.md)

## CPU and interrupts {#cpu}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- SM8475: four Cortex-A510, three Cortex-A710, one Cortex-X2; GICv3, 19.2 MHz timer and PSCI.

### Configuration

- ADT cluster-type is required with PONG\_ADT\_CLUSTERS=1; build two clusters with \_\_ARM\_AMP\_\_.
- pong\_fast\_pri=47 and pong\_fast\_cpu=7 by default.
- ml-timeout-lock-panic-scale=40; interrupt-masked-debug-mode=1.

### Procedure

- 0008 exposes E/P clusters to AMP, 0014 prefers an idle X2 for UI-priority threads, and 0003 bounds qsort recursion to avoid early stack overflow.

### Development findings

- All eight CPUs start. An AMP kernel without ADT cluster-type stalls early \(g97\).
- Under Gunyah, ordinary pauses can exceed the DEVELOPMENT 500 us interrupt-masking threshold. Following sheng, scale timeouts by 40 and log masking violations; preserve genuine fatal panic handling.
- In g170, a stalled app-opening workload used 0.73 CPU on A710 and 0.09 on X2 for the SpringBoard main thread; 0014 gives UI work X2 preference.

### Completion criteria

- Start eight cores and place UI threads on X2 when available.

### Current limits

- No thermal control. Repeated trials heat the phone and can corrupt DRAM ramoops logs.

### Next action

- Integrate SM8475 thermal sensors and CPU frequency limits.

### Evidence

- `source`: [Eight-core boot \(k4\), E/P scheduling comparison and tsample thread records.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-10-30-root-and-autoloop.md)
- `source`: [X2 preference and cadence measurements.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-01-120hz-and-cadence.md)

## Memory and DMA {#memory}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- Live device-tree memory and reserved-memory nodes.

### Configuration

- dts/zizhan.dts memory@80000000 and reserved-memory.

### Procedure

- DarwinBoot24 passes only owned RAM ranges to XNU.

### Development findings

- XNU reports Pong RAM: 4 owned banks, 9728 MiB. The phone has 12 GiB; holes are excluded from VM.

### Completion criteria

- XNU boots and reports managed memory.

### Current limits

- Managed RAM is 9728 MiB; not all physical memory is used.

### Next action

- Check whether ranges above 0x9\_0000\_0000 can safely be given to XNU.

### Evidence

- `source`: [k1 reports 9728 MiB of managed RAM.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-10-29-xnu-bringup.md)

## Storage and root {#storage}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- UFS 3.1 and Android userdata \(f2fs\).
- OS, SystemOS and Data images prepared locally from 22H374 on macOS.

### Configuration

- pong\_shngroot\_4k=&lt;4K block&gt; identifies the root image extent.
- pong\_ufs\_async=0; pong\_ufs\_defer enabled by default.

### Procedure

- install\_pinned.py uses pinalloc to allocate a contiguous 19.4 GiB /data/hackios/root.img, writes OS/SystemOS/Data windows and reports its first block.
- RootLayout publishes each window as separate IOMedia.
- 0006 immediately sends matched notifications when publishResource finds IOResources still configuring.

### Development findings

- Before 0006, roughly three of four boots failed to mount root. APFS probing held its lock while waiting for IOBSD, forming a cycle with IOResources configuration; waiting-thread dumps identified it in g28. g36-g39 mounted root in 4/4 trials after the fix.
- OS, SystemOS and writable Data mount; stock 22H374 launchd starts.
- Existing SmmuTakeover WIP selects SMR/S2CR validity and SID mask from IDR0.EXIDS. APPSSMMU on this phone has EXIDS disabled; g272-retry through g275 mounted root, wrote fresh UFS klog and returned to Android. EXIDS-enabled behavior has host build coverage only.

### Completion criteria

- Mount root reliably and preserve Data writes across boots.

### Current limits

- The root image is a pinned f2fs file. Never move or defragment it in Android; a 40 GiB placeholder was used to preserve a contiguous extent.

### Next action

- Provide a software IOAESAccelerator for AppleImage4 to resolve its wait on /defaults.

### Evidence

- `source`: [Root layout, root-mount deadlock analysis and before/after 0006 results.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-10-30-root-and-autoloop.md)

## Display {#display}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- Inner DSI-1 panel: 2160x1916, command mode, DSC, 60/120 Hz.
- Bootloader cont\_splash\_region: 0xb8000000+0x2b00000.

### Configuration

- ADT display-scale=2 and artwork-scale-factor=2 \(1080x958 points\).
- pong\_panel\_hz=120 by default.
- Kernel defaults: pong\_dpu\_flip=1, pong\_dpu\_bufs=2, pong\_zc=2, fb\_swapwait=1.

### Procedure

- Send timing@1 timing-switch commands through the DSI command FIFO to select 120 Hz.
- Flip DPU directly to CoreAnimation surfaces using triple buffering and no scanout GPU copy.

### Development findings

- At scale 3, 1916/3 is fractional and SpringBoard status-bar Auto Layout recurses until crash; scale 2 reaches Home Screen \(u3\).
- INTF\_1 counters changed from 60.5/s to 120.2/s and latch ceiling from 16.6 to 8.3 ms. The early synthetic workload improved from 44.6 to 54-55 fps; later display-link measurements are in gpu.
- Removing the 2.5 ms per-frame scanout copy presented every submitted frame without counted tears.

### Completion criteria

- Display iPadOS Home Screen on the inner panel with stable presentation at 120 Hz.

### Current limits

- Outer display is unsupported. Backlight retains bootloader state; system brightness control is absent.
- Old screenshot log lines were truncated to about 39/135 sampled columns. The segmented format was device-verified in g248/g249; sampled screenshots do not replace pixel-level panel inspection.

### Next action

- Integrate panel DCS brightness commands.

### Evidence

- `source`: [Inner-panel iPadOS Home Screen \(u3\).](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-10-30-u3-ipados-homescreen.jpg)
- `source`: [120 Hz transition and cadence measurements.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-01-120hz-and-cadence.md)
- `source`: [DPU zero-copy triple-buffer implementation and measurements.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-01-zero-copy-and-return-paths.md)
- `device`: [Six images per trial decoded all 135/135 columns and 120/120 rows. Home Screen and Weather span the image; the old right black region was missing log data.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-02-shot-and-watermark.md)
  Command: <code>cycle.sh g248, g249; tools/zizhan/mac/shot.py</code>. Revision: `c9c8fd274c279a8571b525a1e1dbdf8eddf84d9d`.

## Input {#input}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- Inner ST FTS touch \(spi0.0 fts-pri\), st\_fts\_l18.ubin firmware.
- PMIC power key.

### Configuration

- pong\_touch=1; touch\_flip=2 \(mirror Y\) by default.
- Hold the power key for pong\_button\_reset milliseconds \(default 3000\) to reset to fastboot.

### Procedure

- 0002 adds bsd/dev/pong\_fts.c. SE4 is GSI-only, so SPI is bit-banged through GPIO.
- Deliver events to backboardd through the inherited Pong HID path.

### Development findings

- Touch opened Settings from Home Screen \(t4\).
- A three-second power-key hold resets running iOS to fastboot.
- ui\_compat18.c also owns presentation hooks. The 22H374 UIKit.InProcessAnimationManager class match was corrected and exercised in g298; synthetic-animation evidence does not establish additional physical-touch coverage.

### Completion criteria

- Use touch to open apps and scroll pages.

### Current limits

- Outer touch \(spi2.0 fts-sec\) is unsupported; volume keys remain unaudited. g298 measures synthetic input, not real-finger latency.

### Next action

- Audit volume-key PMIC addresses and measure physical-touch latency separately from synthetic cadence.

### Evidence

- `source`: [Settings opened by touch.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-10-30-t4-settings-by-touch.jpg)
- `source`: [Touch-driver trial records.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-10-30-root-and-autoloop.md)
- `source`: [Historical display-link WIP in ui\_compat18.c: not built on November 2, host-built on November 3; device validation was added later without upgrading input status.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-02-gpu-astc-and-fairplayd.md)
- `source`: [g296-g298 compare the actual UIKit class match, synthetic scrolling and first-frame limits; physical-touch qualification remains separate.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-04-displaylink-device.md)

## GPU {#gpu}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- Adreno730v3; local device a730\_sqe.fw, gmu\_gen70000.bin and a730\_zap.\* firmware, excluded from Git.
- Turnip and metal2vulkan.

### Configuration

- PONG\_ADRENO\_FIRMWARE selects the local firmware directory.
- pong\_gpu\_level=9 \(710 MHz initial GMU level\) by default.
- MercuryPosterEx is denied GPU access by default; pong\_gpu\_deny=- restores it.

### Procedure

- Start Adreno after rootvnode exists and publish the Metal provider after root mount.
- Cache surface mappings and scanout imports.

### Development findings

- User photos confirm GPU-rendered Home Screen and animations.
- MercuryPosterEx competes with backboardd: 5/13 baseline trials lost the GPU. Denying it yielded 6/6 without loss and an early mean scrolling rate of 54.5 fps.
- Fixed 900 MHz did not outperform DCVS; GPU clock was not the limiting factor.
- A ledger-killed GPU client \(SBRendererService on Battery\) freed BO pages with user mappings alive, causing pmap\_assert\_free. PongAdrenoClient::dropViews now unmaps/releases mappings; NativeAdrenoMemory::release calls pmap\_disconnect per page before returning pages to VM.
- After ASTC layout fixes, g248/g249 opened Weather with DeviceSupportsASTC=1; six segmented images per run had 135/135 columns across the screen. g251 Clock and g252 Settings also had complete app images.
- g253/g254 completed 592/592 and 403/403 GPU submissions. A one-submit deadline difference was backboardd work issued 26 ms before reset, not persistent fence blockage.
- Tungsten called PXCreateContext with 0x0, triggering Photos assertions. A Photos-only hook clamps zero axes to 1; g262/g263 and final-kernel g264 reached Photos with ASTC both off and on.
- g296 observed UIKit.InProcessAnimationManager; the old UIViewInProcessAnimationManager-only hook missed it. g298 matched the actual class, filtered 121 requests and reached 95.3 moving fps versus 56.7-58.4 baseline. Trace presentation gaps p50/p90 improved from about 16.6/33.3 to 8.3/16.6 ms.

### Completion criteria

- Render Home Screen and apps through the GPU without GPU loss during sustained scrolling.

### Current limits

- Wallpaper extensions cannot use the GPU; metal2vulkan still spends about 10-20 ms CPU time per submission.
- Sampled screenshots verified Home Screen, Weather, Clock, Settings and Photos after ASTC fixes. Multitasking, touch animations and Photos album/search/edit paths need manual checks; ASTC remains off by default. Stuck-copy and poison detection remain enabled for previously observed GPU losses.
- Photos launch and album landing page are verified; grid, search, edit and image viewing after first-use prompts need manual interaction. IOSurfaceSharedEvent listeners are still missing.
- g298 improves the synthetic animation tail; first frame after idle remains about 75-80 ms. Real fingers, Settings scrolling, power and other apps have no independent qualification; this is not a global 120 fps claim.

### Next action

- Implement IOSurfaceSharedEvent listeners before restoring dependent services and wallpaper GPU access.
- Locate the roughly 80 ms first frame and measure Settings scrolling separately. Use segmented traces to prioritize BO/IOSurface work; qualify fairplayd and wallpaper independently.

### Evidence

- `device`: [Matching the real UIKit animation class activated filtering; moving fps 56.7-58.4 to 95.3. All trace submissions completed, zero lost events. Animation tail improved; first frame did not. All three trials returned to Android.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-04-g298-displaylink.txt)
  Command: <code>cycle.sh g296-gpu-default, g297-gpu-native; replace UI library and reuse g296 image for g298-gpu-fixed</code>. Revision: `42629e5d8d86ead5c4b57d752e3b3187e702ed6f`.
- `source`: [GPU bring-up, GPU-loss diagnosis and wallpaper-denial controls.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-10-30-root-and-autoloop.md)
- `source`: [Per-frame GPU submission timeline.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-10-31-frame-timeline.md)
- `host`: [Final Metal bridge/plugin builds passed; ASTC format numbers checked against the iPhoneOS SDK.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-02-astc-layout.md)
  Command: <code>metal-refresh.sh astc-final (bridge/plugin build)</code>. Revision: `e3be89264924267a610e472e559c9d4d8a66b803`.
- `device`: [ASTC=1: Weather appeared in the left region of three old-format screenshots; automatic Android return. Right-side data was missing.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-02-astc-layout.md)
  Command: <code>round.sh g247 pong_touch_synth=3 tsa=1118 touch_lat=1 pong_shot=60 pong_shot_ms=1000 pong_astc=1</code>. Revision: `e3be89264924267a610e472e559c9d4d8a66b803`.
- `device`: [With the watermark bridge and ASTC=1, Weather started and all six Home/Weather images were complete; automatic Android return. Fence-stall diagnosis remained open at that point.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-02-shot-and-watermark.md)
  Command: <code>metal-refresh.sh watermark; cycle.sh g249</code>. Revision: `c9c8fd274c279a8571b525a1e1dbdf8eddf84d9d`.
- `device`: [Clock and Settings started with complete screenshots. Photos repeatedly exited with PXPixelSizeAreaIsZero. Each trial returned to Android.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-02-shot-and-watermark.md)
  Command: <code>cycle.sh g250–g252</code>. Revision: `caa3a06b6b809be46146fc890995b16d51c8a99c`.
- `device`: [Both traces had no lost events; all submissions completed and zero-copy fences did not time out. Deadline fence was normal work issued 26 ms before reset.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-02-fence-diagnostics.md)
  Command: <code>cycle.sh g253, g254; pong_gtrace_delay, pong_gtrace, pong_gtrace_ib</code>. Revision: `a0eb276866aee06a31189f182335760d5a39d4a9`.
- `source`: [Historical ASTC follow-ups, installed fairplayd state and unverified display-link WIP.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-02-gpu-astc-and-fairplayd.md)
- `device`: [The hook clamps Tungsten 0x0 to 1x1; Photos stopped hitting the zero-size assertion. Final ASTC=1 trial stayed running and returned to Android.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-03-photos-context.md)
  Command: <code>cycle.sh g262-g264; pong_astc=0/1; Photos PXCreateContext hook</code>. Revision: `1ebf568205630bc5fa25737ae95392d2908f0e8a`.
- `host`: [Prepared image contained the hook; UI, bridge/plugin and CI/GPU builds passed. With no device the refresh script left the image untouched. No new device fps or screenshots.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-03-displaylink-host.md)
  Command: <code>Read-only prepared OS/UI inspection; build/sign UI library and Metal bridge/plugin; CI/GPU kernel builds; ui-refresh.sh no-device preflight</code>. Revision: `103d97f1ecc7c874429ae1003d29c4a45c4eb383`.

## Network {#network}

`device-verified`

Components: `PongPlatform24`.

### Hardware and dependencies

- QCA6490 \(PCI 17cb:1103\); read-only device firmware export and Linux v7.0.14 ath11k sources kept outside this repository.

### Configuration

- Default zizhan\_ipados18\_gpu\_defconfig enables GPU and Wi-Fi together; the legacy Wi-Fi name is only a compatibility symlink. Build/package defaults select that profile and startup follows actual compiled settings. WIFI=0 remains an explicit diagnostic override. Private association inputs remain disabled.

### Procedure

- Check PCIe0, WLAN GPIOs and SIDs against the Android live DT; build and pack the isolated Wi-Fi configuration.
- Temporarily fastboot boot over rear USB-A with automatic return. Diagnose power, PCIe, DMA, MHI, firmware, MSI and scan in order; preserve the first failure.

### Development findings

- Live DT confirms PCIe0, GPIO 80/94/95/96/204 and SID 0x1c00/0x1c01; Android runs Gen2 x1.
- The old Pong profile differed in six PHY entries and one extra power request. g265/g266 never booted. The corrected zizhan profile was checked against the full live DT; g267 was prepared but its waiter was removed before any device boot.
- Extended QMI board IDs preserve the chip-dependent bdwlan/bdwlang prefix. g268 PWF2 matched all 213 exported files; the kernel and boot image contained the complete package. USB tool failures meant no g268 device evidence.
- Remove the unverified Pong PCI subsystem gate; validate the primary ID and log actual subsystem values. The summary reports only the last cold start and does not infer association from scan milestones.
- g272-retry verified power, PCIe link/BAR and subsystem 0x010817cb. SMMU context returned StateMismatch \(7\), left the SID detached and let iOS continue; no scan.
- g273 passed TCR2 checks but failed SCTLR ASIDPNE readback. Explicit TBI and a coordinated shared ASID enabled SID1c01 DMA in g274; firmware/QMI reported chip\_id=0x12, board\_id=0xff and selected bdwlang.elf. WMI\_INIT returned -11; receiver setup alone did not prove MSI delivery.
- The host replay selects shim headers with -iquote: its first Linux run exposed -I shadowing glibc linux/errno.h and hiding EAGAIN. This is a host-harness fix; driver behavior is unchanged. A reproduced WMI wait bug resent after success. The fix in g275 reached station-ready, 102 channels, a completed 42-channel scan and 15 networks; Apple80211 queries followed. g276 never booted due to USB enumeration; g277 prepared private optional join inputs.
- g278 completed real WPA2 and key installation. g279 native IPConfiguration acquired DHCP; g280/g281 repeated it, but published service state lacked Router despite router/DNS in the ACK.
- g290 default Wi-Fi path used a separate lease compensation session and verified initial HTTPS, requested renewal, disconnect cleanup and reconnect, with three HTTPS 200 responses. A credential-free boot reached station-ready and scanned 11 networks without association or public probes.
- g291 authenticated to a different BSSID but received no DHCP Offer/ACK. A same-image retry crashed firmware into RDDM; repeated recovery messages overwrote early diagnostics.
- g292 verified first connection and requested renewal on 2.4 GHz, then hit RDDM on cross-band reconnect. g294 vdev recreation failed and was removed. g293/g295 bound the native IO80211 user client; after wifid job/cache repair manager-port lookup errors disappeared, but no native scan/join SET and no successful Settings launch were observed.
- g304 and g306 verified 5220-to-2452 MHz and 2452-to-5220 MHz reconnects to distinct BSSIDs: first connection, requested renewal and reconnect each returned HTTPS 200, with route/DNS cleanup and no RDDM. Publish target-band basic rates before assigning the channel context; ath11k reuses its cached management rate at vdev start.
- g301-g303 traced the native UI stall from SpringBoard wifi\_manager\_open to wifid waiting for InterfaceNamer completion. The stock 300/240-second stack/quiet fallback exceeded short device trials. Stock InterfaceNamer metadata now selects 30/10 seconds and configd publishes its actual TIMEOUT/COMPLETE state.
- g309 used only the native Settings UI: exact private network row, secure text input and navigation Join action. Stock wifid submitted the 900-byte association ABI, WPA2 key installation and DHCP completed, native HTTPS returned 200; ACK compensation released after native route/DNS took over. Kernel auto-association remained disabled.
- g312 reused native saved credentials from an SSID-only/no-password fixture and returned HTTPS 200; kernel credentials and kernel association test remained disabled.
- g311 failed a 128 MiB wired DMA allocation before station readiness. Retry a real 64 MiB arena with SMMU/allocator bounds from the actual size; g312/g314 verified that budget.
- 22H374 reads a 2264-byte scan record with a monotonic observation timestamp at 0x8d0. Preserve the legacy prefix and derive real observation time conservatively from frame age.
- RSSI\_BOUNDS type 106 was unsupported, leaving a zero legacy threshold that rejected negative-dBm candidates. Report signed decoder format limits after checking SIGNAL\_DBM, with no extra station admission floor; native quality policy and actual RSSI readings are preserved. g331 automatic association and HTTPS 200 passed. g332 repeated it with original wifid, no Settings launch and actual default 128 MiB DMA; its periodic disconnects were subsequently diagnosed as PrimaryTimeout.
- g334 native logs identified Not Primary Interface \(1005\). Bind the ACK compensation service to the existing real en0 Setup Interface in the same session; cleanup removes that binding with IPv4/DNS. g337 used original wifid, no fixture or Settings launch, a real default 64 MiB arena and asynchronous FIFO notifications: one native association, HTTPS 200, no link loss through approximately 309 seconds.
- g338-g340 failed the second DHCP after real radio off/on despite successful key installation. The shared timer traversal cached a successor across recursive callbacks; inner removal made that node self-linked. Adapt the generated timer pass to restart selection after each callback with a 256-callback budget. Host replay reproduces the old hang. g341 with the same local test OS passed two distinct DHCP REQUEST/ACK transactions, two HTTPS 200 responses and session/route/DNS cleanup, with continued worker progress.
- Default device packaging now starts the compiled radio without WIFI=1; explicit WIFI=0 disables only the radio, and reduced CI packaging does not claim a compiled radio.

### Completion criteria

- Scan and associate with a real network.
- On en0, verify DHCP, requested renewal, disconnect route/DNS cleanup, reconnect and three public HTTPS responses \(g290 default network path\).

### Current limits

- The default GPU configuration now includes Wi-Fi. Current radio processing still depends on polling; actual GIC MSI delivery is unverified.
- Bidirectional cross-band tests and one Settings join passed against the current WPA2 APs. Natural T1 expiry, different SSIDs/subnets, long-duration roaming, enterprise/SAE and broader device coverage remain unqualified.
- DHCP ACK compensation remains available for missing route/DNS state; g309 observed native takeover. UI fixture files and firmware stay local, and the optional UI test is disabled unless explicitly requested.
- Automatic join, short connection hold and one native radio off/on lifecycle passed. This is not long-duration qualification. One logging boot failed before userland with shared-cache ENOMEM; preserve that genuine panic as a failed prerequisite.

### Next action

- Keep the verified clean prepared OS, UI/helper and manifest aligned; old prepared artifacts are retained and canonical/trial descriptors match. Investigate the separate no-Settings canvas-mapping failure without treating it as a successful UI trial.
- Qualify natural T1, different subnets, long-duration reconnect and actual MSI separately before changing the shipping default.

### Evidence

- `device`: [Combined device defaults without DEFCONFIG/PROFILE/WIFI overrides passed native automatic association, keys, DHCP and HTTPS 200. Zero link loss or canvas-mapping errors; three complete Settings screenshots, deadline return and fresh UFS log.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-05-default-gpu-wifi.txt)
  Command: <code>cycle.sh out/g344-default-combined/pong-xnu-initial.img g344-default-combined 480</code>. Revision: `cc016a5c44c1ed074e98ea7c1104c1e5cbdff88f`.
- `host`: [Default device packaging now starts the compiled radio without WIFI=1; explicit WIFI=0 disables only the radio, and reduced CI packaging does not claim a compiled radio.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-05-default-gpu-wifi.txt)
  Command: <code>ci_kernel.sh default and explicit CI; ci_boot_ufs.sh default/WIFI=0/explicit CI; check-wifi-host.py</code>. Revision: `cc016a5c44c1ed074e98ea7c1104c1e5cbdff88f`.
- `device`: [Both clean-stock-wifid boots returned HTTPS 200 with continued UP status. No-Settings g342 had a canvas-mapping failure and a wrapped early log, so no UI pass is claimed. g343 retained one association/key handshake, zero link loss and three complete Settings screenshots with no fixture or temporary test UI/helper.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-05-wifi-lifecycle.txt)
  Command: <code>cycle.sh out/g342-clean-native/pong-xnu-initial.img g342-clean-native 600; cycle.sh out/g343-clean-settings/pong-xnu-initial.img g343-clean-settings 480</code>. Revision: `959b00b1b81186c40b75b16a1c27c512062a2e1a`.
- `host`: [Three kernel configurations built; actual old timer pass hangs under nested removal, adapted pass handles recursion, cancellation, running rearm, budget and future deadlines. FIFO ordering/full/wrap and existing regressions pass.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-05-wifi-lifecycle.txt)
  Command: <code>check-wifi-host.py --shared Ath12kWifi; ci_kernel.sh Wi-Fi/CI/GPU</code>. Revision: `959b00b1b81186c40b75b16a1c27c512062a2e1a`.
- `device`: [Real service binding and deferred notifications eliminated repeated short-run disconnects. Timer fix passed native radio off/on: two distinct DHCP ACK transactions, two HTTPS 200 responses, cleanup and continued worker progress. g340 failure is retained as the control.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-05-wifi-lifecycle.txt)
  Command: <code>cycle.sh g335-fixed, g337-deferred-events, g340-progress-watch, g341-timer-reentry</code>. Revision: `959b00b1b81186c40b75b16a1c27c512062a2e1a`.
- `device`: [Stored credential reuse and real 64 MiB operation passed. Native automatic join and HTTPS 200 passed; original-wifid/no-Settings/default-128 MiB repeated HTTPS, but periodic disconnects remain.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-04-wifi-settings-and-roaming.txt)
  Command: <code>cycle.sh g312, g314, g331, g332</code>. Revision: `718f73ce424d427c2ecdc757b9c64eb7cd4f3dca`.
- `host`: [Three kernel configurations, loader/UI/helper builds and host regression suites passed. Native metadata staging preserves stock endpoints and rejects other OS builds.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-04-wifi-settings-and-roaming.txt)
  Command: <code>ci_kernel.sh Wi-Fi/CI/GPU; LLVM 18 loader build; UI/helper compile and codesign; check-wifi-host.py on macOS and Ubuntu</code>. Revision: `92ef6d2de5419ce5c5aa8bfe36ab25a9fadeffb7`.
- `device`: [Both frequency directions passed three HTTPS 200 responses and disconnect cleanup without RDDM. Native Settings join independently passed WPA2, DHCP and HTTPS with kernel auto-association disabled.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-04-wifi-settings-and-roaming.txt)
  Command: <code>cycle.sh g304-rate-crossband, g306-rate-2g-to-5g, g309-native-settings-join</code>. Revision: `92ef6d2de5419ce5c5aa8bfe36ab25a9fadeffb7`.
- `host`: [Bounded waits under a busy pump, skb ownership, lease and USB regressions passed. Native interface and firmware-failure cleanup built; host and device findings remain separate.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-04-wifi-native-repair.md)
  Command: <code>ci_kernel.sh CI/GPU/Wi-Fi configs; check-wifi-host.py; wifid plist/cache staging replay; compile/sign UI library</code>. Revision: `fbac25628cfd36365c2850407bc77c3121b36780`.
- `device`: [Local repair snapshots based on the recorded commit: first connection and renewal on 2.4 GHz returned HTTPS 200; cross-band RDDM failed. Native IO80211 binding worked and manager-port lookup errors disappeared; Settings/native join failed. Vdev experiment reverted.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-04-wifi-native-repair.txt)
  Command: <code>cycle.sh g292, g293, g294, g295 (local repair snapshots)</code>. Revision: `3ca641b749e9fbba116f7eebcde349e4f8ce81e5`.
- `device`: [Same-image control: firmware crashed, MHI recovery returned -110 and association failed. Early logs were overwritten; initial fault stage unknown. Deadline returned the phone to Android.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-04-g291-cross-ap.txt)
  Command: <code>cycle.sh out/g291/pong-xnu-initial.img g291-retry 480</code>. Revision: `616bb5eb8d5d622b90c51c06d10486063ecb3bcd`.
- `device`: [Initial connection and requested renewal returned HTTPS 200; disconnect cleanup passed. WPA2 authenticated to a different BSSID, but no DHCP Offer/ACK arrived. Cross-AP networking failed; returned to Android.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-04-g291-cross-ap.txt)
  Command: <code>cycle.sh out/g291/pong-xnu-initial.img g291 480; cycle-resume.sh recovery after interruption</code>. Revision: `616bb5eb8d5d622b90c51c06d10486063ecb3bcd`.
- `device`: [Credential-free boot reached station-ready, scanned 11 networks and returned to Android; no automatic association or public probe.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-04-g290-default-wifi.txt)
  Command: <code>cycle.sh out/g290-default-wifi/pong-xnu-initial.img g290-default-wifi 420</code>. Revision: `ade79e8088f089b7145b9139e410b6115c7ef3ce`.
- `device`: [Default Wi-Fi path passed initial networking, native requested renewal, disconnect cleanup, reconnect and three HTTPS 200 responses.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-04-g290-lifecycle.txt)
  Command: <code>cycle.sh out/g290/pong-xnu-initial.img g290 480</code>. Revision: `ade79e8088f089b7145b9139e410b6115c7ef3ce`.
- `device`: [Existing en0 configuration acquired default route and DNS, native HTTPS 200; compensation released after native configuration recovered. Renewal trigger was not run.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-04-g289-https.txt)
  Command: <code>cycle.sh out/g289/pong-xnu-initial.img g289 460</code>. Revision: `da8e7cbacf1c73f8aff14ba39fed9ea2ebf45d0e`.
- `device`: [Live ACK matched kernel IPv4. After service-state compensation en0 became primary; native HTTPS returned 200 / 577 bytes; returned to Android.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-04-g287-https.txt)
  Command: <code>cycle.sh out/g287/pong-xnu-initial.img g287 420</code>. Revision: `64c4b52a4081802f9f75e5ca2c963f99df623156`.
- `device`: [Live ACK was readable; consistency checks rejected compensation. HTTPS failed.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-04-g286-routing.txt)
  Command: <code>cycle.sh out/g286/pong-xnu-initial.img g286 420</code>. Revision: `c405db767cfc2f21016a0bde10c6559c6d84cd7e`.
- `device`: [Five power rails, association and IPv4 passed. configd had no en0 IPv4 entity and the kernel had no default route.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-04-g285-routing.txt)
  Command: <code>cycle.sh out/g285/pong-xnu-initial.img g285 420</code>. Revision: `3b54df270354f46b9c330622e7a6b238ea5a9faf`.
- `device`: [Real association and IPv4 passed; kernel returned ENETUNREACH. Dynamic-store IPv4 service lacked Router; disk lease did not pass validation.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-04-g283-routing.txt)
  Command: <code>cycle.sh out/g283/pong-xnu-initial.img g283-retry 420</code>. Revision: `cb2667293f5720ef93b5926e1a49df2730513145`.
- `device`: [IPv4 acquired. Experimental ACK-based route/DNS compensation was not applied; HTTPS failed. Returned to Android.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-04-g282-wifi.txt)
  Command: <code>cycle.sh out/g282/pong-xnu-initial.img g282 480</code>. Revision: `9f9423f25e91d26be43476053f49bd7a77f55282`.
- `device`: [Session DHCP service succeeded; ACK contained router/DNS while published service lacked Router.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-04-g281-wifi.txt)
  Command: <code>cycle.sh out/g281/pong-xnu-initial.img g281 480</code>. Revision: `70f56e325df7ea2a9f851d53136784d0461169e7`.
- `device`: [WPA2 and DHCP repeated successfully; four public probes had no primary interface, route or DNS. Returned to Android.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-04-g280-wifi.txt)
  Command: <code>cycle.sh out/g280/pong-xnu-initial.img g280 480</code>. Revision: `0959812c992522b084bfb80a587e888cfd8bee53`.
- `device`: [WPA2 association and IPv4 DHCP lease succeeded; first HTTPS probe failed.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-04-g279-wifi-usb.txt)
  Command: <code>cycle.sh out/g279/pong-xnu-initial.img g279-retry 480</code>. Revision: `333c5defb04af1d5f48fa3c83e912d352869441f`.
- `device`: [Station ready and scan found 15 networks. Fresh UFS klog was 941005 bytes; returned to fastboot after 168 seconds, then Android. Association/DHCP unverified.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-03-g275-wifi.txt)
  Command: <code>cycle.sh out/g275/pong-xnu-initial.img g275 480</code>. Revision: `32ee207bd5b585d79bc25181f69757aefeab9256`.
- `device`: [Returned automatically with 1133944 bytes of fresh UFS klog; TCR2 passed, SCTLR ASIDPNE readback mismatched.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-03-g273-wifi.txt)
  Command: <code>cycle.sh g273; three kernel configurations and register replay</code>. Revision: `0acd5e0f55cf37635fb333f9735ae7592747403e`.
- `device`: [Returned automatically with 1105249 bytes of fresh UFS klog; SMMU/DMA and firmware/QMI passed, WMI\_INIT=-11. Wi-Fi incomplete.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-03-g274-wifi.txt)
  Command: <code>cycle.sh g274; three kernel configurations and register replay</code>. Revision: `239d5403defdec0d9dde3c1cc4d11c5e3b2326bd`.
- `device`: [Temporary boot passed; fastboot return after 107 seconds and 995985 bytes of fresh UFS klog \(deadline\), then Android. Power/PCIe passed, SMMU status=7; Wi-Fi incomplete.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-03-g272-retry-wifi.txt)
  Command: <code>cycle.sh out/g272/pong-xnu-initial.img g272-retry 420 (existing local WIP image)</code>. Revision: `4927a4b459c6a025d12af96da3265b5c74a1458f`.
- `source`: [Device Wi-Fi chipset identification.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-10-28-device-prep.md)
- `host`: [Three old-profile configs built. Images withdrawn because board inputs mismatched; g265/g266 never booted.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>ci_kernel.sh: zizhan_ipados18_wifi_defconfig, pong_ipados18_ci_defconfig, zizhan_ipados18_gpu_defconfig</code>. Revision: `79ae5b1d7b92f621ac549aec80e73e30e404d649`.
- `host`: [Full live-DT profile audit and three builds passed. g267 had one Wi-Fi switch and automatic return; no device boot.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>PONG_WIFI_DTB=&lt;local live DT&gt; ci_kernel.sh (Wi-Fi); ci_kernel.sh CI/GPU; ci_boot_ufs.sh boot-g267</code>. Revision: `ae24f8a89f41fe2864d997ea3b8005fb1824ae89`.
- `host`: [After QMI extended-ID naming fix, all three configs built; g268 command-line and automatic-return checks passed. No device result.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>ci_kernel.sh Wi-Fi/CI/GPU; ci_boot_ufs.sh boot-g268</code>. Revision: `2eab51d14ecc79b3e9b34a4adf65a2b0a81322d8`.
- `host`: [Three builds passed again. Visible, unauthorized, blocked adb and fastboot boot success/failure simulations passed; g268 had no device boot.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>ci_kernel.sh CI/GPU/Wi-Fi; USB tool simulations</code>. Revision: `890ec93c136a23bbc0e857d0879c3119bf945b83`.
- `host`: [213/213 firmware files matched; kernel and final image contained the full package. No high-board-ID file; actual QMI ID was then unknown.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>Parse PWF2 and compare each SHA-256 with local firmware export; inspect embedded g268 package</code>. Revision: `0949ebe471d258965f2ef2ae21b44cd1eda13576`.
- `host`: [Distinguished no log, power failure, post-PCIe ath11k failure, multiple boots and scan. CI/GPU builds passed; no g268 device result.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>wifi-stage.py: five isolated log fixtures and g264 non-Wi-Fi replay; ci_kernel.sh CI/GPU</code>. Revision: `eb2fe973a6611582c6ad31f45d7c8b9389094a6a`.
- `host`: [Three builds passed. g269 command line was 913 bytes with one Wi-Fi switch, screenshots and automatic return; new subsystem log marker and PWF2 embedded. Device absent; no device result.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>ci_kernel.sh CI/GPU/Wi-Fi; ci_boot_ufs.sh boot-g269; inspect command line and firmware package</code>. Revision: `5b695938a42495d517be09d43b3ecaa2cb4eb59c`.
- `host`: [Only last cold-start subsystem values were reported; corrupt values rejected. g264 retained NO\_WIFI\_LOG. CI/GPU builds passed; no g269 device log.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>wifi-stage.py multi-boot/corrupt-value fixtures and g264 replay; ci_kernel.sh CI/GPU</code>. Revision: `2b7966cb95f2572f5b28dee8e8d89e49b384ec1d`.

## cellular {#cellular}

`planned`

### Hardware and dependencies

- SM8475 phone with a cellular modem; unlike a Wi-Fi-only board this area is applicable.
- Board-specific modem firmware, EFS/NV, QRTR/QMI, SIM, IPA/QMAP and OS ABI inputs require an audit. Keep identities and device dumps private.

### Configuration

- No cellular component is selected or enabled in board.toml; no modem initialization is added by this record.

### Procedure

- Read the upstream baseband guide and sibling implementation before selecting a shared component.
- Audit the live board resources and firmware dependencies; isolate read-only transport/identity checks before registration or data-session work.

### Development findings

- No cellular implementation or device verification has been performed in this repository; a Wi-Fi HTTPS result does not validate modem transport or data.

### Completion criteria

- Establish firmware/transport ownership, valid SIM state and network registration.
- Verify IPA/QMAP data sessions, routing and teardown/reset with separate host/device evidence.

### Current limits

- Modem firmware loading, EFS/NV, SIM, registration, IPA/QMAP and data sessions are not implemented or verified. No IMEI/ICCID or raw modem dump is published.

### Next action

- Inventory the actual zizhan modem transport, firmware and OS dependencies against the upstream QcomBaseband guide, then choose the first bounded read-only probe.

### Evidence

- `source`: [The current upstream record guide lists cellular separately; this modem-equipped phone is planned, not not-applicable.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-04-upstream-ci-audit.md)

## Audio {#audio}

`planned`

Components: `PongPlatform24`.

### Hardware and dependencies

- Two CS35L41 amplifiers at 0x40/0x42. Public zizhan Android DT gives SE15 I2C 0x880000, GPIO56/57 SDA/SCL, GPIO88/118 IRQ and shared GPIO1 reset. Recheck the live phone DT before enabling; Pong uses TFA9873 with different bus/pins/addresses.

### Configuration

- pong\_audio=0; without tfa98xx.cnt build an empty amplifier table.

### Procedure

- Keep audio off; audit live DT and I2C prerequisites, run an isolated read-only identity probe, then implement CS35L41 initialization and ADSP playback routing.

### Development findings

- Pong TFA9873 initialization cannot be reused by changing addresses.
- PongAudio.cpp uses SE13 0xa94000, GPIO48/49 and addresses 0x34/0x35, unlike the public zizhan SE15 description.
- GeniI2c supports multi-byte transfers but amplifier wrappers and writes remain TFA9873-specific.

### Completion criteria

- Play audible sound through the speakers.

### Current limits

- No CS35L41 driver. Public extracted DT still needs live-device revalidation; no audio device-boot or playback evidence.

### Next action

- Verify live SE15 clocks, pins, reset and IRQ, then read CS35L41 identity in an isolated config. Audit tuning/firmware and ADSP routing before staged device tests.

### Evidence

- `source`: [Reason audio stays disabled and empty-amplifier-table behavior.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-01-battery.md)
- `source`: [Public extracted Android DT describes SE15, GPIO56/57, CS35L41 addresses, reset and IRQ; live-phone recheck pending.](https://github.com/sm8450-mainline/fdt/blob/3e347601d9e91dd2f1f48e51499823225f7bc0bc/zizhan.dts)
- `source`: [PongAudio.cpp comparison, isolated-probe prerequisites and unverified boundaries.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-03-audio-board-audit.md)

## Power {#power}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- Local ADSP /vendor/firmware\_mnt/image/adsp.mdt and b00..b25, merged by mdt2mbn.py into adsp.mbn; not committed.
- UniXNU-sheng ShengBattmgr protocol.

### Configuration

- CONFIG\_XNU\_PONG\_POWER=y.
- pong\_adsp=2 starts DSP and battery; 1 maps/investigates only; 0 disables.

### Procedure

- PongAdsp loads/authenticates ADSP in the zizhan carveout and reads battery through PMIC GLINK.
- Shift ShengBattmgr Xiaomi property IDs by one after 12; temperature is already in 0.01 C.
- PongRpmh.cpp supplies shared RPMh votes when Wi-Fi is not built.

### Development findings

- g206 agreed with Android sysfs: 100%, 4444 mV, charging 426 mA, 34.40 C, full capacity 3507 mAh, design 4500 mAh and 907 cycles.
- Rename the battery service AppleSmartBattery because PerfPowerServices PLBatteryAgent and powerd health calculation select that class. Publish Serial, BatteryData and MaximumCapacityPercent. Settings Battery Health reported 78% \(3483/4500 mAh\).
- The health spinner follows batteryDataUnavailable: thermalmonitord never publishes com.apple.thermalmonitor.ageAwareMitigationState and powerd lacks Battery Service State.
- USB plug/unplug changes charge state and current direction \(+300/-520 mA, v7\).
- Settings checks MobileGestalt D6/BMDrlb8V3WSiqL8gL+w then AppleAuthCPRelay isTrustedForUI for battery authentication. This battery has no Apple authentication chip; ui\_compat18.c reports the capability false, without inventing genuine-part status.

### Completion criteria

- Status bar and Settings Battery show accurate charge and plug/unplug changes; Battery opens without blocking.

### Current limits

- Battery Health still spins due to missing management/service state. Usage graphs need long-term collection. Sleep/wake is unsupported.

### Next action

- Implement thermalmonitord ageAwareMitigationState and powerd Battery Service State from actual services; do not fabricate a normal status in Settings.

### Evidence

- `source`: [ADSP startup stages 1-13 passed; battery readings agree with Android.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-01-battery.md)

## Image assembly {#packaging}

`host-verified`

Components: `PongPlatform24`.

### Hardware and dependencies

- xnu-11417.140.69 \(Darwin 24.6.0\) and stock 22H374 restore components.

### Configuration

- patches/xnu-ipados18/series.
- PROFILE=zizhan\_ipados18\_gpu; local prelink/userdata inputs documented under migration/ipados18.

### Procedure

- ci\_prep.sh prepares dependencies; ci\_kernel.sh builds; ci\_boot\_ufs.sh prelinks and creates the boot image.
- build-xnu-ipados18.sh uses patch --forward in series order to avoid reversing already-applied hunks.

### Development findings

- After the series is applied, clean xnu-11417.140.69 matches the actual build tree file by file.
- Disable three newer-clang warnings under -Werror; support both Intel and arm64 macOS hosts.
- ADT /chosen requires unique-chip-id and chip-id. Without IOPlatformUUID, gethostuuid blocks and timed/locationd/contextstored/PowerUIAgent lead to a frozen Battery page. build-ipados18-bootimg-local.py supplies a software seed, not an Apple hardware identity.
- fairplayd.A2 exits immediately in this port; launchd KeepAlive retains its port and queued requests have no response. EXCLUDED18 removes it on a full rebuild.
- The packer enforces 1020 command-line bytes. Omit default pong\_ui\_software=0, pong\_software\_ui=0 and pong\_ram\_banks=1 to save about 54 bytes.
- ADT /product udid-version=1 requires SerialNumber, ECID, WifiAddress and BluetoothAddress; disabled Wi-Fi stalls MobileGestalt and Settings ISDefaults. With a /chosen seed, use the stock iPhone17,1 version 2 \(ChipID-ECID\); first Settings screen fell from 6.4 to 1.2 seconds.
- On November 2, fairplayd was restored from pre-g213 OS for Weather diagnosis. g245 recorded 2560 frames, 2453 moving at 72.0 fps and no failed lookups, but respawn persisted. EXCLUDED18 still removes it on full rebuild.
- Read-only inspection found fairplayd cache/plist in current OS and g213, absent in f245. Kernel builds do not change that installed service state; use the same kernel and B1-A-B2 ordering for a device control.
- g279 installed a signed native DHCP helper/job into the 22H374 OS after old-window/block prechecks, then read back blocks against the manifest. The phone launched the service.
- The November 4 compliance audit found that the existing local and macOS build pipelines have not adopted the latest upstream templates/package.sh and package action. Record validity and successful builds do not establish compliance with that new packaging interface.
- Full 22H374 preparation copies stock InterfaceNamer bundle metadata into the overlay with its documented native 30/10-second fallback. The signed UI helper is opt-in; tests use local-only credential files, verified OS delta preflights and readbacks. No fake dynamic-store Quiet state is injected.
- Local build and package defaults select the combined device profile. Runtime GPU/Wi-Fi enablement follows the kernel report; explicit overrides produce a single value per key. Reduced cloud CI remains explicitly selected.

### Completion criteria

- Build a bootable image reproducibly from a published device revision and record host and device results separately.

### Current limits

- Apple images, firmware and ABI binaries are prepared locally.
- The generic job-restore.sh had static checking only. Installed fairplayd policy differs from full rebuild; no B1-A-B2 device comparison has completed.
- The latest unified scripts/package.sh and .github/workflows/package.yml are absent. Current CI builds the reduced kernel by default, not a clean end-to-end release or a full Wi-Fi/GPU image.

### Next action

- Migrate the fixed upstream package template, TOML-selected Darwin24 prelink/payload inputs and package action together; validate --check and a full local build before claiming adoption.
- Run the same-kernel fairplayd B1-A-B2 control and inspect exits, Weather and Battery independently of UI/plugin build success.

### Evidence

- `device`: [Combined device defaults without DEFCONFIG/PROFILE/WIFI overrides passed native automatic association, keys, DHCP and HTTPS 200. Zero link loss or canvas-mapping errors; three complete Settings screenshots, deadline return and fresh UFS log.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-05-default-gpu-wifi.txt)
  Command: <code>cycle.sh out/g344-default-combined/pong-xnu-initial.img g344-default-combined 480</code>. Revision: `cc016a5c44c1ed074e98ea7c1104c1e5cbdff88f`.
- `host`: [Local build and package defaults select the combined device profile. Runtime GPU/Wi-Fi enablement follows the kernel report; explicit overrides produce a single value per key. Reduced cloud CI remains explicitly selected.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-05-default-gpu-wifi.txt)
  Command: <code>ci_kernel.sh default and explicit CI; ci_boot_ufs.sh default/WIFI=0/explicit CI; check-wifi-host.py</code>. Revision: `cc016a5c44c1ed074e98ea7c1104c1e5cbdff88f`.
- `host`: [Root and overlay staging passed with preserved stock metadata and wifid services. UI/helper built and signed; OS-only device deltas were checked before and after writing.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-04-wifi-settings-and-roaming.txt)
  Command: <code>check-wifi-host.py; compile/sign native UI and wifi-service18; actual OS delta manifest/hash preflight and readback</code>. Revision: `92ef6d2de5419ce5c5aa8bfe36ab25a9fadeffb7`.
- `source`: [Build-chain description.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-10-29-xnu-bringup.md)
- `host`: [A clean Apple-silicon Mac Studio build \(Xcode 26.6.0\) produced an 18321080-byte DEVELOPMENT\_ARM64\_PONG kernel with the same zizhan boot-argument strings as device trials.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/host-build-zizhan_ipados18_gpu.txt)
  Command: <code>ZIZHAN_SRC=&lt;work dir&gt; ci_prep.sh &amp;&amp; DEFCONFIG=zizhan_ipados18_gpu_defconfig JOBS=10 ci_kernel.sh</code>. Revision: `1ec1190f4e3467a36a7a7402bc766dfdf688adf1`.
- `source`: [Installed-image fairplayd restoration is distinguished from EXCLUDED18 full-rebuild policy; no additional device-verified status.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-02-gpu-astc-and-fairplayd.md)
- `source`: [Local Wi-Fi inputs, three kernel builds and experimental-image packaging; no device result at that historical stage.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-03-wifi-bringup.md)
- `host`: [Current/g213 contained fairplayd; f245 did not. No-device, backup-conflict and missing-label paths refused safely. CI/GPU builds passed; device behavior unverified.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-03-fairplayd-baseline.md)
  Command: <code>Read-only mount current/g213/f245 OS; jobs-refresh.sh failure injection; ci_kernel.sh CI/GPU</code>. Revision: `06d28dbf2c30652b63ab3f24be6664fd790d275f`.
- `source`: [Current-upstream compliance audit identifies the unified packaging interface as pending; existing build evidence remains scoped to the recorded pipeline.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-04-upstream-ci-audit.md)

## Diagnostics {#diagnostics}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- ramoops at 0x85200000, logfs and USB adb/fastboot.

### Configuration

- pong\_autoreset=&lt;seconds&gt; \(default 300\), pong\_autoreset\_sb.
- pong\_klog\_4k copies kernel logs into a fixed UFS file.
- pong\_gtrace, pong\_gtrace\_delay, pong\_gtrace\_ib and touch\_lat provide timed per-frame traces.

### Procedure

- cycle.sh temporarily boots, waits for watchdog fastboot return, uses RamoopsDump to write logfs, returns to Android and pulls logs.
- Panic, a three-second power-key hold and deadline reset all return to fastboot while retaining DRAM logs.

### Development findings

- The loop needs no key presses. Missing pong\_autoreset in g152 was mistaken for a bus freeze.
- Repeated hot trials cause bit flips in DRAM ramoops; the pong\_klog\_4k UFS copy avoids that corruption.
- pong\_url and pong\_pane open Settings; settings\_compat18.c prints views/specifiers/spinners/accessibility at 6/12/20/30 seconds. settings-ui.py decodes escaped non-ASCII output.
- gs\_all=2 in 0005 also samples waiting threads; gsym.py resolves complete stacks. This traced synchronous XPC to timed waiting in gethostuuid.
- pong\_gtrace\_delay moves capture after SpringBoard startup. Fence age separates persistent stalls from in-flight work at reset.
- USB enumeration probes have six-second limits; fastboot boot has a 180-second transfer limit and preserves failure instead of claiming boot.
- The old g268 waiter ran under user-domain launchd with heartbeats but no device enumeration; this is historical evidence.
- Failed logfs export/pull removes stale and partial local copies. Screenshot decode removes old PNGs when the new trial has none.
- Only matching current arm/successful-boot markers permit UFS klog readback; otherwise recover ramoops, preventing old pinned klog reuse.
- boot.sh checks device/image before reboot; adb reboot is bounded to 30 seconds. fastboot visibility requires a successful command.
- logfs export/pull are limited to 60/120 seconds and remove stale/partial outputs on failure.
- g272-retry through g275 completed temporary boots, deadline return and fresh UFS logs. g276 never booted after USB vanished in the fastboot transition.
- Rear USB-A passed 10/10 Android-fastboot-Android transitions without replug. After the matching companion-port action and three-second settle, a 100168 KB image transferred and booted once.
- The host replay uses -iquote so Darwin shim headers do not shadow glibc linux/errno.h. Record CI now uses the reviewed e67a79eb64012e8f30ba04c56ea37753bdb720a2 checker and compares committed paths against the push-before or PR-base SHA, in addition to structural validation. All matched owner areas must update findings/evidence. A separate Ubuntu/clang job replays the existing SMMU, WMI, DHCP and USB regressions against pinned Ath12kWifi headers without private inputs.
- g301-g303 stack sampling separated SpringBoard wifi\_manager\_open, wifid SystemConfiguration quiet waiting and normal configd run loops. The optional bounded Settings probe selects only the exact private SSID, uses native secure-text and Join handlers, logs no credentials and requires independent association/HTTPS evidence. UISwitch dumps report actual on/enabled state.
- Optional read-only Wi-Fi progress diagnostics and kernel thread sampling distinguished an executing dispatcher stall from a sleeping waiter. The actual timer-pass regression now reproduces the original nested-removal hang and validates the generated fix; g341 native UI actions are accepted only alongside independent DHCP transactions, HTTPS and cleanup evidence.
- Default and radio-off package paths were run with the system bash, including unset PROFILE/WIFI; no empty-array nounset failure remains. Device evidence is collected from an actual default package with automatic return.

### Completion criteria

- Every trial automatically returns to Android and yields fresh complete logs.

### Current limits

- Direct USB-C can still fail enumeration and lacks supported host-port probing. Rear USB-A is the verified path. Port-state bits do not prove VBUS power-off; prefer current-trial UFS klog over corrupt ramoops.

### Next action

- Use rear USB-A for unattended trials; retry only once for an explicit USB write failure during transfer. Follow both record and kernel CI at the published SHA.

### Evidence

- `device`: [Combined device defaults without DEFCONFIG/PROFILE/WIFI overrides passed native automatic association, keys, DHCP and HTTPS 200. Zero link loss or canvas-mapping errors; three complete Settings screenshots, deadline return and fresh UFS log.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-05-default-gpu-wifi.txt)
  Command: <code>cycle.sh out/g344-default-combined/pong-xnu-initial.img g344-default-combined 480</code>. Revision: `cc016a5c44c1ed074e98ea7c1104c1e5cbdff88f`.
- `host`: [Default and radio-off package paths were run with the system bash, including unset PROFILE/WIFI; no empty-array nounset failure remains. Device evidence is collected from an actual default package with automatic return.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-05-default-gpu-wifi.txt)
  Command: <code>ci_kernel.sh default and explicit CI; ci_boot_ufs.sh default/WIFI=0/explicit CI; check-wifi-host.py</code>. Revision: `cc016a5c44c1ed074e98ea7c1104c1e5cbdff88f`.
- `host`: [Actual original/adapted timer traversal replay plus notification FIFO, SMMU, WMI, DHCP, staging and USB regressions passed; no phone or private input needed.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-05-wifi-lifecycle.txt)
  Command: <code>check-wifi-host.py --shared Ath12kWifi</code>. Revision: `959b00b1b81186c40b75b16a1c27c512062a2e1a`.
- `device`: [Busy worker and unchanged progress generation localized the failed control; fixed kernel completed native off/on, independent DHCP/HTTPS/cleanup, full screenshots and deadline return with a fresh UFS log.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-05-wifi-lifecycle.txt)
  Command: <code>cycle.sh g339-kernel-sample, g340-progress-watch, g341-timer-reentry; decode-shots.sh</code>. Revision: `959b00b1b81186c40b75b16a1c27c512062a2e1a`.
- `device`: [Native service wait chain and actual Settings controls were observed. g307/g308 UI deadlines were failures; g309 native Join produced an actual association and HTTPS 200. Complete and incomplete screenshot extents are kept distinct.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-04-wifi-settings-and-roaming.txt)
  Command: <code>gesture sampler gs_proc=SpringBoard/wifid/configd; cycle.sh g307-g309; decode-shots.sh</code>. Revision: `92ef6d2de5419ce5c5aa8bfe36ab25a9fadeffb7`.
- `device`: [Ten full mode transitions passed; after port settling the 100168 KB image sent once and booted.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/evidence/2026-11-04-g279-wifi-usb.txt)
  Command: <code>adb reboot bootloader / fastboot getvar product / fastboot reboot x10; usbkick.sh kick + g279-usba-settle</code>. Revision: `3f93d0cd7ee552fd580003abcf569984d9cc3373`.
- `source`: [Unattended-loop design and trial history.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-10-30-root-and-autoloop.md)
- `source`: [Four reset/return path fixes.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-01-zero-copy-and-return-paths.md)
- `source`: [Sanitized Mac clone workflow, diagnostic defaults and verification boundaries; retired old-host sync instructions.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/CLAUDE.md)
- `source`: [USB absence prevented g265 boot. Six-second fastboot probing and explicit-image waiting passed host fixtures; device loop recovery was then pending.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-03-wifi-bringup.md)
- `host`: [Failed starts no longer report booted; three configs built. Phone absent, no device trial.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>adb-visible.sh and fastboot-boot.sh fixtures; CI/GPU/Wi-Fi kernel builds</code>. Revision: `890ec93c136a23bbc0e857d0879c3119bf945b83`.
- `host`: [launchd owned the waiter and logs had heartbeats. Phone still absent; no device logs/screenshots.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>launchctl submit g268 when-back; launchctl list and log inspection</code>. Revision: `5eaa262d46cdb2c3d7a56de28805d57cea548185`.
- `host`: [Export failure, partial pull and empty files removed stale copies and failed. Success retained fresh data. Three configs built; device unverified.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>pull-logfs.sh four failure fixtures; ci_kernel.sh CI/GPU/Wi-Fi</code>. Revision: `0a03bab9a4876f1490e453559a24244ffca76958`.
- `host`: [g264 replay decoded six PNGs; a new same-name log without screenshots removed old PNGs. CI/GPU builds passed; g268 not booted.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>decode-shots.sh g264 and no-screenshot replay; ci_kernel.sh CI/GPU</code>. Revision: `bcfaddf0e1ed31bed1ab99a29e4854e144d01801`.
- `host`: [No marker or mismatched marker selected ramoops; matching current marker selected klog. Failed boot left no success marker. CI/GPU builds passed; phone absent.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>cycle.sh/cycle-resume.sh four klog-marker fixtures; ci_kernel.sh CI/GPU</code>. Revision: `2f1f10aea4b3d65691a7e0cd72c6f79d2623928a`.
- `host`: [Absent phone, adb failure/timeout and missing image failed promptly. Missing image was rejected before device actions; nonzero fastboot did not count as visible. CI/GPU builds passed; g268 had no device result.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>boot.sh/fastboot-visible.sh isolated failure fixtures; ci_kernel.sh CI/GPU</code>. Revision: `1a2ec083bab2242f0da0247f17eae02104796491`.
- `host`: [Export/pull failure, timeout and empty outputs removed stale/partial images; success retained fresh data. CI/GPU builds passed; no device logs/screenshots.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>pull-logfs.sh six failure fixtures; ci_kernel.sh CI/GPU</code>. Revision: `ee84c10b22da2f6bbf1382de3bac1874c15a2b52`.
- `source`: [Audit of checker version, push/PR comparison bases, public catalog revision and build-CI scope.](https://github.com/qiumochen/UniXNU-zizhan/blob/3b3c52fb5ba11b0a185703d7832fd567c94e770e/docs/progress/2026-11-04-upstream-ci-audit.md)

</div>
