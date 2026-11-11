# OnePlus Ace 3 PJE110

[MoyuZJ912/UniXNU-aston](https://github.com/MoyuZJ912/UniXNU-aston)

<div v-pre>

OnePlus Ace 3 PJE110 \(aston\), SM8550, iPadOS 27.0.1 \(24A446\). CPU and persistent Data fixes are source changes awaiting device verification. Inherited sheng observations are reference-board evidence only.

源记录: [porting.toml](https://github.com/MoyuZJ912/UniXNU-aston/blob/e0f721be3f2e8438b94395bd8e3a456f8cacc80b/porting.toml), `e0f721be3f2e8438b94395bd8e3a456f8cacc80b`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `implemented` |
| [固件与启动](#firmware) | `planned` |
| [CPU 与中断](#cpu) | `implemented` |
| [内存与 DMA](#memory) | `planned` |
| [存储与根卷](#storage) | `implemented` |
| [显示](#display) | `planned` |
| [输入](#input) | `planned` |
| [GPU](#gpu) | `implemented` |
| [bluetooth](#bluetooth) | `planned` |
| [usb](#usb) | `planned` |
| [网络](#network) | `planned` |
| [音频](#audio) | `planned` |
| [电源](#power) | `implemented` |
| [镜像组装](#packaging) | `implemented` |
| [诊断](#diagnostics) | `implemented` |
| [arm64e-os](#arm64e-os) | `implemented` |

## 配置 {#configuration}

`implemented`

### 硬件与依赖

- UniXNU 5dc00d201496a1e7a72d1f5db23f041eb94ace1c, SM8550 97665e28578483082b674e8375a8fa65f4cf49cf, XNU ac9718fb1af618d5ce8678d0dc6e8a58f252216f.

### 配置

- board.name=aston, kit=sheng, os\_profile=ios-27.0.1-24A446, kernel.defconfig=aston\_ios27\_defconfig \(branch ios27\).
- The first archive stages the pinned RamBlock publication patch before either source-storage or RamBlock compilation.

### 操作步骤

- Run the package workflow with the original installation seed, then inspect effective source pins and patch order.

### 开发经验

- ArmCpu 93a5030 defaults armcpu-edge to zero, skipping ml\_cpu\_init\_completed. Aston now selects armcpu-edge=1 after fixing the board Edge matrix.
- The RamBlock fix is applied to an isolated build-tree copy; revision and normalized source SHA-256 are checked and source.json records the patched input. Shared checkouts and source pins are unchanged.

### 完成条件

- All source pins resolve; every selected component has a record; status shows the intended overrides and patch order.

### 当前范围

- No local.toml or unixnu.lock was present during this change. Full macOS kernel compilation and device results remain pending.

### 下一步

- Build the branch on the pinned macOS runner using the existing Data seed.

### 证据

- `source`: [Implementation and configuration described in this section](https://github.com/MoyuZJ912/UniXNU-aston/blob/e0f721be3f2e8438b94395bd8e3a456f8cacc80b/board.toml)
- `source`: [The sheng-lite=2 profile disables com.apple.iconservices.iconservicesagent in addition to the sheng-lite=1 jobs.](https://github.com/MoyuZJ912/UniXNU-aston/blob/e0f721be3f2e8438b94395bd8e3a456f8cacc80b/scripts/check-boot-watchdog-policy.py)
- `device`: [Reference sheng observation, not aston verification: Boot 50d4021e7 with sheng-lite=2 recorded no iconservicesagent PID or associated main-thread wait. Settings opened. All app icon artwork was missing from the photographed Home Screen and Dock. The continuous-HID flip median changed from 15.358 to 9.631 ms and P99 from 43.232 to 46.384 ms.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/reports/ipados27-touch-frame-gaps.md)
  Command: <code>fastboot boot sch4.img</code>. Revision: `fe636ce2c24b5f5ef406e2dc70504d2573f00092`.
- `source`: [On 24A446, iconservicesagent runs on demand with FORCE\_SOFTWARE\_RENDERER=0 and CI\_ENABLE\_METAL\_GPU=0. The stock J820 Jetsam profile sets a 15 MiB inactive hard limit and a 1,224 MiB active soft limit.](https://github.com/MoyuZJ912/UniXNU-aston/blob/e0f721be3f2e8438b94395bd8e3a456f8cacc80b/board.toml)
- `device`: [Reference sheng observation, not aston verification: On 24A446 boot 41dcdcce, iconservicesagent PID 168 obtained the Adreno 740 Metal device and created a command queue. Eight completed command buffers contained 149 draws. The kernel recorded 495 paired submissions and retirements with zero replays. No fault or exit of that agent was recorded through the 240-second export.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/reports/ipados27-touch-frame-gaps.md)
  Command: <code>fastboot boot ico4.img</code>. Revision: `1c0d9770f6b3cf8de565ba793146c8d5427b979f`.
- `device`: [Reference sheng observation, not aston verification: On cold-cache boot 41ee75ce, the Home Screen displayed complete Settings and App Store icons. The 56 px Wi-Fi, Battery and About cache variants were transparent. All 488 GPU submissions from iconservicesagent PID 139 retired. Launchd recorded a per-process Jetsam termination after 173.752 s.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/reports/ipados27-touch-frame-gaps.md)
  Command: <code>fastboot boot ico4-lock-fix.img</code>. Revision: `571fcc972a4ea3e8c402183ba98a0a8f67a4750a`.
- `source`: [Aston CPU and storage candidate fix; host checks and remaining device checkpoints are described in reports/cpu-storage-fix.md.](https://github.com/MoyuZJ912/UniXNU-aston/blob/e0f721be3f2e8438b94395bd8e3a456f8cacc80b/board.toml)

## 固件与启动 {#firmware}

`planned`

组件: `ShengPreflight`.

### 硬件与依赖

- uefi-sheng firmware, stock firmware DTB, GOP handoff, PSCI SMC interface and vendor firmware inventory.

### 配置

- firmware.dsc = Platforms/Xiaomi/shengPkg/sheng.dsc; firmware.config = sheng.
- proprietary-files.txt records input paths and provenance.
- The firmware DSC and FDF embed UniXNU, UniXNUDxe, DarwinBoot, UniXNURamDiskDxe, DiskIoDxe and FAT support.

### 操作步骤

- Run ./unixnu build firmware -D ../UniXNU-sheng --uefi ../uefi-sheng.
- Record the firmware commit, output FD and handoff memory map before a boot attempt.
- Build the payload, then run ./unixnu bootimg with the firmware DTB. Inspect boot.json ramdisk\_bytes and the required firmware modules.

### 开发经验

- The firmware DTB is an input to boot-image assembly. XNU consumes the separately generated ADT.
- The sheng preflight component belongs with board integration and its firmware requirements.
- The shared UniXNURamDiskDxe reads the Mu-Silicium entry-argument HOB and FDT initrd range to publish the payload block device. ShengBootMemoryDxe owns memory expansion.
- Configured menu entries require a payload FAT filesystem containing EFI/UniXNU/unixnu.toml. Check the UNIXNURAMDISK initrd block-device status when entries are absent.
- fetch-sheng-dts.py writes the firmware device tree at build/sheng/sheng.dtb and the copy the GPU generators bind to at build/adreno-firmware/sheng.dtb.
- firmware/novatek/novatek\_nt36532\_n81a\_fw\_csot.bin is the pinned touch firmware of proprietary-files.txt; the build reads the extracting machine cache first and this copy on a clean checkout.
- board.toml \[firmware.image\] pins the official fastboot archive \(url, SHA-256, MD5, bytes\); the firmware preflight downloads it, streams out only the porting inputs, deletes the archive and generates Binaries/sheng in the firmware checkout from them. No extracted binaries live in any repository.
- A completed extraction skips both scripts: porting-inputs.json records the archive as deleted with the pinned source url and SHA-256, so a rerun rebuilds Binaries/sheng without downloading again.
- The extraction skip sits after the board.toml \[firmware.image\] load: it compares against the pinned table, which the first lines of the script have not read yet.
- import-sheng-uefi.py regenerates Binaries/sheng only when its manifest differs from the cache: a matching tree is left in place.
- Wi-Fi firmware files are pinned by firmware/wcn7850/manifest.json and packaged under the shared Data directory; VFS loading waits for addon installation.
- Bluetooth firmware and NVM files are pinned by firmware/bluetooth/manifest.json and staged by scripts/stage-bluetooth-firmware.py under firmware/qca in the Data addon.

### 完成条件

- Firmware image builds, enters UniXNU, publishes the framebuffer and preserves the documented memory reservations.

### 当前范围

- Inherited sheng implementation notes below are reference material, not an aston hardware qualification.
- Boot-image assembly requires the selected firmware DTB and proprietary input files.

### 下一步

- Capture firmware revision and memory reservations with the next image verification.

### 证据

- `source`: [Implementation and configuration described in this section](https://github.com/MoyuZJ912/UniXNU-aston/blob/e0f721be3f2e8438b94395bd8e3a456f8cacc80b/proprietary-files.txt)
- `source`: [Shared FDT initrd block-device publication; board memory policy remains in uefi-sheng.](https://github.com/UniXNU/UniXNU/blob/8d157ee18ae9c4d518aba28cb3040a84e860dcd1/package/UniXNUPkg/Driver/UniXNURamDiskDxe/UniXNURamDiskDxe.c)
- `host`: [Reference sheng observation, not aston verification: 2026-10-26: DEBUG firmware and a 219283456-byte boot image built for the minimal arm64e kernel. DarwinBoot accepts arm64e capability bits. The kernel was relinked with legacy threaded starts, all 103192 fixups were walked, and the source corecrypto HMAC was regenerated after the entry and panic probes. Prior notes report fastboot download and boot returned OKAY; kernel and userspace execution remain unobserved. This handoff only rechecked the existing image SHA-256 against the archived manifest; it did not boot this image. The recorded base revision has uncommitted build changes.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/reports/ipados26-boot-build.json)
  Command: <code>shasum -a 256 ../UniXNU/out/sheng/ipados-26.5.2-23F84/sheng_ipados26/boot/boot.img</code>. Revision: `2ab05c11ae80e8b59dac2d312f627e78cacc0fca`.

## CPU 与中断 {#cpu}

`implemented`

组件: `ArmCpu`, `ArmDTPlatform`.

### 硬件与依赖

- Eight SM8550 CPUs: cpu0-2 A510, cpu3-6 A715/A710, cpu7 X3. EPSS frequency domains contain 3, 4 and 1 CPUs.

### 配置

- dts/aston.dts exports E/P cluster types. armcpu-edge=1 enables cross-cluster scheduler initialization. sheng-cpufreq=4 uses the governor.

### 操作步骤

- Apply the complete selected patch series and run scripts/check-aston-cpu-storage.py against the patched XNU and pinned RamBlock.
- On the phone, record per-CPU startup, idle counts, busy share, frequency votes, frame latency and battery current.

### 开发经验

- The former policy forbids P-to-E migration for high QoS but allows it for lower QoS, violating the XNU non-decreasing-strictness invariant used by early-exit searches.
- The replacement preserves P preference for foreground work, permits weighted P-to-E spill at all QoS levels and keeps E work from being stolen onto P cores. The XNU matrix assertion is restored.
- Missing or offline processors return UINT64\_MAX. The governor rebases those samples and regressing counters instead of treating a parked CPU as 100 percent busy.

### 完成条件

- The ordered patch series applies, native policy fixtures pass, all enabled CPUs start, and measured UI latency and power improve without scheduler warnings.

### 当前范围

- No device boot or thermal result from this branch. L3 remains at the inherited maximum vote; deep idle and thermal feedback are not implemented by this change.

### 下一步

- Compare the same workload on this branch and the previous image; retain the CPU and battery logs.

### 证据

- `source`: [Implementation and configuration described in this section](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/dts/sheng.dts)
- `device`: [Reference sheng observation, not aston verification: Boot da1dbd496 recorded 6,680 exact SpringBoard samples with CPU IDs, 6,679 ready Arm PMU readings, 8,485 DVFS windows and main-thread Mach wait durations. The five busy long flips had maximum votes in all 82 governor windows. A synchronous XPC wait involving iconservicesagent overlapped 4.444 seconds of a flip gap.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/reports/ipados27-touch-frame-gaps.md)
  Command: <code>fastboot boot sch3.img</code>. Revision: `948a8b8696e56c0ab74a4a1ee22753744ea462e3`.
- `source`: [Aston CPU and storage candidate fix; host checks and remaining device checkpoints are described in reports/cpu-storage-fix.md.](https://github.com/MoyuZJ912/UniXNU-aston/blob/e0f721be3f2e8438b94395bd8e3a456f8cacc80b/patches/xnu-12377/aston-edge-policy.patch)
- `host`: [Windows native policy, publication and capacity fixtures passed. API stand-ins do not qualify XNU, APFS or phone hardware; area remains implemented.](https://github.com/MoyuZJ912/UniXNU-aston/blob/e0f721be3f2e8438b94395bd8e3a456f8cacc80b/reports/cpu-storage-fix.md)
  Command: <code>python scripts/check-aston-cpu-storage.py --xnu .cache/xnu-verify --ramblock .cache/RamBlock --cc .cache/toolchain/ziglang/zig.exe cc</code>. Revision: `c72ab4e2aa75727569162823cac20100b4c36703`.

## 内存与 DMA {#memory}

`planned`

### 硬件与依赖

- Handoff DRAM at 0x80000000 with size 0x80000000; splash reservation at 0xb8000000 with size 0x2b00000.
- Payload owned-memory request is 0x130000000. Device DMA requires controller stream IDs, address widths and ownership.

### 配置

- device\_tree.source = device:dts/sheng.dts; include\_dirs = \[soc:dts\].
- payload.adt.owned\_memory\_size and firmware reservations describe separate allocations.

### 操作步骤

- Compare firmware RAM ranges, reserved regions, DTS ranges and ADT memory-map entries.
- Check DMA buffers against controller address width, cache policy and SMMU mapping before submitting work.

### 开发经验

- The sheng WLAN node exports the wlan ADT name used by wifid matching. It adds service-discovery metadata to the shared DTS; DRAM reservations and DMA resource ownership continue to use the existing board and controller descriptions.
- Physical register translation and CPU virtual mappings have different purposes. Preserve physical resource ranges in hardware descriptions.
- GPU and UFS use different SMMU instances and stream assignments.
- The DTS carries each CPU's cluster type for the ADT \(see the cpu area\).
- The GPU memory host fixture uses the current trace and task-role interfaces. Image backing reuse and deferred physical release are bounded by the Metal runtime; foreground placement and room-worker allocations can still overlap.
- The exported Bluetooth node carries transport encoding and baud as little-endian u32 properties; its runtime MAC address is derived from the chosen platform identity.

### 完成条件

- All handoff regions are accounted for and each enabled DMA engine accesses its allocated range with the documented cache policy.

### 当前范围

- Inherited sheng implementation notes below are reference material, not an aston hardware qualification.
- The DTS declares the current handoff window and splash region; memory sizing requires the selected firmware map.

### 下一步

- Record the firmware memory map and each DMA consumer when changing reserved memory.

### 证据

- `source`: [Implementation and configuration described in this section](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/dts/sheng.dts)

## 存储与根卷 {#storage}

`implemented`

组件: `ShengUfs`, `VirtioMmioBlock`, `RamBlock`, `VerifiedRoot`.

### 硬件与依赖

- The unixnu GPT partition spans LBA 115424000..123812607 at 4096 bytes per block. The Data seed is 8 GiB.
- RamBlock 4be2d7eb05ef5a98126c91e0302c149140c0e3e1 and the existing installation seed.

### 配置

- native-source-storage=1 native-ufs-root=1 sheng-data-persist=2. Android userdata is not the root partition.

### 操作步骤

- Preserve the existing Data seed. Stage the RamBlock patch before compiling either storage archive.
- Record the data persistence row, the Data mount capacity checkpoint and Files crash reason; verify a file survives reboot.

### 开发经验

- The pinned RamBlock publishes its seed before selectVolumeSeed attaches persistent pages. APFS can cache seed checkpoint metadata before the block backend changes.
- Aston starts UFS before RamBlock, so the persistent window is available before RamBlock registerService. The patch attaches it before publication and removes late attachment from volume lookup.
- A refused, mismatched or unavailable writable store is not published as an apparently writable seed-only disk. Reset remains explicit; no automatic reformat, seed replacement or GPT change is added.
- This ordering defect is established from source. Its contribution to the reported zero-capacity UI and Files crashes needs an aston boot log.
- Device 2026-11-09 \(boot 5, root 158d94bc, diag\): the Data mount reports status 0, total 8589934592, free 6893985792 bytes, and the store row D st=2 er=0, so the kernel capacity and persistence are sound; Settings' 0 KB is a userland symptom.
- The Data store read back with scripts/pull-aston-data.py and opened with scripts/apfs-read.py has no /containers/Data/Application and no /containers/Shared/AppGroup. The seed carries com.apple.migration.plist \(buildVersion 24A446\), so datamigrator skipped the first-boot migration that registers the system apps. Files and DockFolderViewService crash in +\[FILocalStorageNode sharedNodeWithDomain:\] on a nil local-storage URL \(10 and 78 reports\) and dasd aborts in -\[NSURL initFileURLWithPath:\] \(50 reports\).
- patches/xnu-12377/aston-migration-rerun.patch removes the marker before launchd starts when sheng-rerun-migration=1 \(menu entry Rebuild app data\), so that boot runs the migration once; the BootLog capacity row reports migration=&lt;status&gt;.

### 完成条件

- The first APFS probe reads the persisted checkpoint, Data reports nonzero capacity, Files opens and can save a file, and the same file survives reboot without persistence errors.

### 当前范围

- Native fixtures use API stand-ins. They do not mount APFS or establish that existing on-device Data is undamaged. The reported storage symptoms are not yet confirmed resolved.

### 下一步

- Boot without init\_data or an erase menu choice using the original seed, inspect capacity and persistent state, and exercise Files across a reboot.

### 证据

- `source`: [Implementation and configuration described in this section](https://github.com/UniXNU/ShengUfs/blob/e2b32cc429e8cf1501161c1d8c517f8994ceb9b2/NativeUfs.cpp)
- `host`: [Reference sheng observation, not aston verification: Source-interface compile audit with uncommitted workspace changes; source and object hashes are recorded. Link/runtime/edge qualification remain false. Historical device results in this area apply to iOS 17.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/reports/ipados26-source-drivers.json)
  Command: <code>cd ../UniXNU &amp;&amp; python3 scripts/build-sheng-source-drivers.py --tree out/sheng/ipados-26.5.2-23F84/sheng_ipados26/tree --device ../UniXNU-sheng --storage-source out/driver-sources/IOStorageFamily --hid-source out/driver-sources/IOHIDFamily --with-storage-family</code>. Revision: `2ab05c11ae80e8b59dac2d312f627e78cacc0fca`.
- `source`: [Aston CPU and storage candidate fix; host checks and remaining device checkpoints are described in reports/cpu-storage-fix.md.](https://github.com/MoyuZJ912/UniXNU-aston/blob/e0f721be3f2e8438b94395bd8e3a456f8cacc80b/scripts/patches/ramblock-publish-after-store.patch)
- `host`: [Windows native policy, publication and capacity fixtures passed. API stand-ins do not qualify XNU, APFS or phone hardware; area remains implemented.](https://github.com/MoyuZJ912/UniXNU-aston/blob/e0f721be3f2e8438b94395bd8e3a456f8cacc80b/reports/cpu-storage-fix.md)
  Command: <code>python scripts/check-aston-cpu-storage.py --xnu .cache/xnu-verify --ramblock .cache/RamBlock --cc .cache/toolchain/ziglang/zig.exe cc</code>. Revision: `c72ab4e2aa75727569162823cac20100b4c36703`.

## 显示 {#display}

`planned`

组件: `GopFramebuffer`.

### 硬件与依赖

- UEFI GOP framebuffer, stride, pixel format, splash reservation and board panel/backlight controls.

### 配置

- Select GopFramebuffer; CONFIG\_XNU\_NATIVE\_LEGACY\_DISPLAY=y; artwork-display-gamut = sRGB.
- sheng-vsync=120 requests board display timing.
- sheng-dpu-scanout=2 lets the display pipes fetch the compositor surface through a stage 1 window of the display bank \(TCR2 SEP 7\); off by default. The flip waits for the GPU fence of the frame \(always on\).
- sheng-backlight=1 starts the backlight driver; sheng-backlight-control=0 leaves out backlight-control and the AppleARMBacklight metaclass answer.

### 操作步骤

- Verify GOP address, dimensions, stride and pixel layout before enabling presentation.
- Build the late display archive with the selected OS ABI records, then check display publication and frame presentation.

### 开发经验

- iPadOS 27 reads the nits range from IODisplayParameters.BrightnessMilliNits and sets brightness-nits as signed 16.16. CoreBrightness needs backlight-marketing-table and backlight-calibration-parameters to create the display. BrightnessControl reads LmaxProduct as 4 bytes of 16.16 and LmidProduct and LminProduct as numbers; a zero LmaxProduct makes every slider position the maximum. iPadOS 17 uses brightness and FadePeriod; the service accepts both.
- ADT vmm-present makes MobileGestalt answer IsVirtualDevice, and iPadOS 27 CoreBrightness then selects VMBLControl, which drops every brightness request. AMFI and many frameworks need the answer, so UniXNU scripts/appsync/BacklightMode.m changes only backboardd: initBLControl: gets mode 1 instead of 3.
- The board archive records SmmuBypass.h and AppsSmmuLock.h from the resolved board package directory as Bluetooth build dependencies.
- The 24A446 display adapter declares fixed original targets. XnuPrelink relocates BTI/B stubs after native segment placement; a cached native-slide value is no longer used. The 2026-11-02 device log showed the unrelocated constructor branch jumping to 0xfffffff00dbb4c74 instead of 0xfffffff00a288c74, an excess of 0x392c000.
- The display source and ABI binding are selected independently from the physical panel configuration.
- The board configuration declares sRGB for the current 8-bit framebuffer path.
- scripts/build-gop-legacy-display.py also builds the board driver objects in the display archive, including the ADSP, IPC router, FAT reader and battery manager.
- With sheng-dpu=2 DisplayTimingProbe reads the VIG 0 and 1 pipes, CTL 0 and the tear checks; sheng-dpu=3 also rewrites the pipe addresses and times the flush latch \(5.4 ms, no start needed: the panel refreshes by itself\).
- Direct scanout: the compositor submits a swap when the command buffer is scheduled, so the flip waits until the GPU wrote the frame; the wait removes the flicker \(content changes of the shown surface fell from 808 to 2 per run\). Direct scanout needs the 8-bit BGRA framebuffer.
- The GENI I2C core also moves 1 to 8 byte writes and 1 to 4 byte reads \(the audio amplifiers use 32-bit registers\); the backlight keeps its 8-bit transfers.
- The legacy display builder now refuses arm64e/iOS 26 before reading original ABI addresses. Its existing use of kernel\_target.TRIPLE does not qualify the iOS 17 class layout for 23F84. Source input transport compilation is independent of this builder.
- The 24A446 adapter creates a BGRA IOSurface through the original IOSurfaceRoot factory, checks allocation and geometry, and transfers its reference to the family default-surface field. The void create\_default\_fb\_surface slot is invoked by the original start method.
- build-gop-legacy-display-27.py reads the device checkout from UNIXNU\_DEVICE \(set by the release\) before the sibling directory name, so a checkout under any name works., and the HID source is the tree pin \(refer/IOHIDFamily of the feed\) instead of a hand-placed driver-sources copy.
- The 24A446 board archive resolves QcaBluetooth from the assembled tree before the device fallback, matching the selected runtime component.
- The late probe starts USB through the weak sheng\_usb\_probe, and the board package build compiles QcomDwc3.
- package/AstonBootScreen.cpp draws a boot screen into the firmware framebuffer from the board probes \(bsd\_init\) until iOS draws: title, a moving bar, elapsed time, the stage \(Data mounted, data migration asked for\) and the newest kernel message buffer lines \(18x42 pixel cells, 70 columns\). It stops without clearing once the legacy display accepts a swap or its sentinel pixel changes; aston-boot-screen=0 turns it off. Host run on a 1264x2780 buffer with the boot 5 message buffer, ASan and UBSan clean; not yet on the device.

### 完成条件

- A known frame appears with correct geometry and colors, then userland presentation and backlight controls work.

### 当前范围

- Inherited sheng implementation notes below are reference material, not an aston hardware qualification.
- The late display builder needs qualified prelink candidates and ABI records. A timing request requires a measured presentation result. The 24A446 default-surface adapter still requires a hardware boot result.
- On iPadOS 27 backlight off on sleep is not verified. The range of 2, 140 and 500 nits is not measured and only sets the slider's scale.

### 下一步

- Record frame timing, pixel format and presentation evidence for each image used to qualify display.
- On iPadOS 27, verify that sleep turns the backlight off.

### 证据

- `source`: [Implementation and configuration described in this section](https://github.com/MoyuZJ912/UniXNU-aston/blob/e0f721be3f2e8438b94395bd8e3a456f8cacc80b/package/LegacyDisplayProbe.cpp)
- `source`: [The diagnostic ring timestamps VSync timer arms, sends, idle stops, late ticks, starts and refresh-rate reports.](https://github.com/MoyuZJ912/UniXNU-aston/blob/e0f721be3f2e8438b94395bd8e3a456f8cacc80b/package/LegacyDisplayProbe.cpp)

## 输入 {#input}

`planned`

组件: `ShengHidInput`, `ShengNovatekTouch`, `QcomGeniSpi`.

### 硬件与依赖

- Novatek NT36532 sensor, GENI SPI controller, pin configuration, reset/interrupt lines, firmware and touch coordinate geometry.

### 配置

- Select ShengHidInput, ShengNovatekTouch and QcomGeniSpi; sheng-touch=4 and sheng-touch-hid=1 select board integration.

### 操作步骤

- Read TouchBoard.h and verify the SPI clock and mode against the controller setup.
- Validate protocol reports, contact tracking and coordinate orientation before publishing HID events.

### 开发经验

- backboardd caches the event service's usage pair when it first sees the service, and drops every touch if that pair is not 0x0d/4. The DriverKit driver writes 1/6 and registers the service, so HidInputProbe checks every 2 ms until the service has been registered for 10 s.
- The shared SMMU fixture adds UART14 stream 0x423 beside touch without modifying its route and accepts a 64-bit DMA buffer address.
- The arm64e HID adapter uses the same fixed-target stub contract as the display adapter. Host verification checks all 51 IOHIDFamily stub destinations after fileset placement.
- Controller transfer logic, sensor protocol and board sensor geometry are separate inputs.
- Track contact IDs across movement and lift events; a register read alone covers only transport access.
- sheng\_buttons\_press\(\) holds a button mask for a given time through the HID sink, for unattended tests \(the audio lock sound test uses it\).
- iPadOS 26 source-interface build: IOHIDDevice reports and independent touch/button, GENI SPI, Novatek and firmware archives compile. Four host model suites pass ASan/UBSan. The source path does not patch a foreign vtable.
- On arm64e the event driver's vtable is copied and every slot is re-signed with the 220 discriminators read from the 24A446 kernelcache; each slot is checked against the original table first, and AppleUserHIDEventService, this device's event driver, takes the copy as well. A search over 16-bit values can accept a second discriminator with the same 24-bit signature and stops touch events.
- With latency capture enabled, the HID input path records the time of each touch report handed to the event driver; these times bound the analysed touch windows. Contact IDs and coordinates are not recorded.

### 完成条件

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive, and buttons produce expected HID reports.

### 当前范围

- Inherited sheng implementation notes below are reference material, not an aston hardware qualification.
- Sensor firmware and board dimensions remain sheng inputs.
- 23F84 HID linking/startup and edge gestures remain unqualified. Apple IOHIDFamily 2238.120.5 omits event-type/struct headers and the complete device build needs private reporting/analytics dependencies.

### 下一步

- Attach contact and orientation observations when firmware or geometry changes.

### 证据

- `source`: [The joint latency capture exports vsync tick events and CPU frequency windows alongside HID report times. Exact user-stack samples are marked with peer -2.](https://github.com/MoyuZJ912/UniXNU-aston/blob/e0f721be3f2e8438b94395bd8e3a456f8cacc80b/package/BootDiagExport.c)
- `host`: [Reference sheng observation, not aston verification: Host replays cover adjacent-key taps, bottom-edge tip-down coordinates and four- and five-finger pinches with stable IDs.](https://github.com/UniXNU/ShengNovatekTouch/blob/3b44b1b7603eaadae942ea44ddc51bdcc48ad060/Test/touch-core.c)
  Command: <code>python3 scripts/check-touch-host.py</code>. Revision: `3b44b1b7603eaadae942ea44ddc51bdcc48ad060`.
- `source`: [Implementation and configuration described in this section](https://github.com/MoyuZJ912/UniXNU-aston/blob/e0f721be3f2e8438b94395bd8e3a456f8cacc80b/package/TouchBoard.h)
- `host`: [Reference sheng observation, not aston verification: Source-interface compile audit with uncommitted workspace changes; source and object hashes are recorded. Link/runtime/edge qualification remain false. Historical device results in this area apply to iOS 17.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/reports/ipados26-source-drivers.json)
  Command: <code>cd ../UniXNU &amp;&amp; python3 scripts/build-sheng-source-drivers.py --tree out/sheng/ipados-26.5.2-23F84/sheng_ipados26/tree --device ../UniXNU-sheng --storage-source out/driver-sources/IOStorageFamily --hid-source out/driver-sources/IOHIDFamily --with-storage-family</code>. Revision: `2ab05c11ae80e8b59dac2d312f627e78cacc0fca`.
- `device`: [Reference sheng observation, not aston verification: Boot 532856a9 retained 6,195 HID report timestamps. The median interval between reports was 8.334 ms.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/package/TouchProbe.cpp)
  Command: <code>fastboot boot sch1.img</code>. Revision: `8fcf9a4e0f3c5a23a820f85fd25189e2c7e83f87`.
- `device`: [Reference sheng observation, not aston verification: Five fingers retained distinct IDs through a 250 ms pause. All 57 rapid typing contacts released. Both App Switcher gestures failed and rapid taps sometimes selected alternate characters.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/reports/ipados27-touch-frame-gaps.md)
  Command: <code>fastboot boot sch2.img</code>. Revision: `8ec842f38c21ef1d73e12000fae16df7442e0c73`.

## GPU {#gpu}

`implemented`

组件: `Adreno740`, `AdrenoMetal`, `AirNir`, `Sm8550Platform`, `AdrenoPM4`, `AdrenoFirmware`, `ArmSmmu4K`.

### 硬件与依赖

- A740 GPU/GMU registers, GPU SMMU streams 0/1 and GMU stream 5, signed ZAP firmware and board power votes.
- Turnip, metal2vulkan, AIR translation and the selected OS GPU/Metal ABI.

### 配置

- Select Adreno740, AdrenoMetal and AirNir; shared SM8550 operations arrive through component dependencies.
- Board scripts combine shared GMU code with package/ShengGmuVotes.c.
- sheng-gpu-preempt defaults to 2: requested high priorities use ring 0, normal/low work uses ring 1. Mode 1 sends only low/background to ring 1; mode 0 selects one ring.

### 操作步骤

- Qualify power, firmware, SMMU and GMU startup before command submission.
- Check memory mapping, command completion and a known rendered image before staging the Metal plugin.

### 开发经验

- Each ring restores its executed page-table snapshot, saves GMEM and runs the SRAM postamble. GMU keepalive covers restore-register writes through the incoming WPTR update; board writes retry AHB-fence drops.
- The shared process queue keeps FIFO across priority changes. Current live Metal requests determine priority, with task GPU role selecting foreground or background.
- All AdrenoMetal clients use one sample by default; NATIVE\_METAL\_SINGLE\_SAMPLE=0 preserves a process's requested sample counts. The frontend implements heap aliasing, swizzles, mip/slice copies, function constants and callbacks, specialized link names, backing-allocation statistics, queue capacity and full viewport/scissor arrays.
- Writable same-user caches cover frontend, runtime and Turnip IR3 artifacts; restricted clients use private caches. Normal builds enable Mesa disk caching and apply the recorded vendor patches.
- The optional sheng-wallpaper-freeze=1 mode retains a Poster renderer's first completed large IOSurface draw and parks later runtime commits. PosterBoard and compositor clients keep running. Event 60 identifies the completion boundary and parked commands.
- The current sheng iPadOS 27 image boots and accepts touch interaction, and shader priming covers 280 of 280 selected libraries. Foreground and room-worker 64 MiB allocations still overlap. Focused latency capture retains full-width runtime memory phases, command and pass timings, paired callbacks and allocation roles. GPU pixel collection and per-frame content scans are disabled.
- The kernel GPU ring keeps submission, retirement, display arrival, fence, latch, build identity and the render server's render, encode and completion thread identities; client processes forward nothing else. The decoders read only these records and write touch-window subsets.
- check-gpu-trace.py checks that Turnip's GMEM swap trace \(passes, transfers, attachments\) leaves only the render server, and the kernel store keeps events 36, 37 and 44.
- AdrenoMetal carries 25 patches over metal2vulkan 963f0e64. The lowering thread, commit submission and pipeline warm pass are off by default and sheng-metal-flow=1 enables them for testing. They showed no measured frame rate gain, and one of four boots with them stopped presenting at the logo. pipeline\_waits stays Exact because the upstream default drops draws of a pipeline not made in time.
- iOS 27 \(iPhone17,2\), stage B: the GPU arguments of iPadOS b5bb234 under the names their readers use since UniXNU 47ec6a5 \(sheng-gpu-power=9, sheng-gpu-metal=1, sheng-gpu-dcvs=1 and sheng-fb-gpu=1 for this board; fb-gpu=1 for GopFramebuffer, fb-bgra=1 for the Metal plugin, gpu-addon=1 for the addon mount\) and the Metal addon built \(\[payload.runtime\] gpu\_addon\). The GMU, SQE and ZAP images \(151 KiB\) are in the native \_\_TEXT: the iPhone17,2 collection has 125 KiB left for \_\_DATA\_CONST and 432 KiB for \_\_TEXT.
- The Metal plugin writes QuartzCore options at fixed addresses of the iPad 24A446 shared cache \(CE33B2BA\). The iPhone17,2 cache \(1892D244\) has the same QuartzCore code at the same addresses, and its \_\_DATA\_DIRTY, \_\_AUTH and \_\_AUTH\_CONST 0x4000 higher. Every ADRP reference of QuartzCore's \_\_text into those segments \(7978 and 6450\) differs by exactly 0x4000 at the same instruction, those into \_\_DATA \(7027\) by 0. unixnu-patches/AdrenoMetal keys the addresses by the cache UUID read from the mapped cache header, after UniXNU-asteroids 5650eda. An unknown cache gets only the environment \(marker 0x6EF0\). The caches were read from the IPSWs' sealed SystemOS images with scripts/apfs-read.py, which now follows sealed trees \(hashed nodes, child ids relative to the tree root, fext extents\).

### 完成条件

- GPU submissions complete, mapping/fence handling is correct, a known image renders, and the selected Metal client presents it.

### 当前范围

- Inherited sheng implementation notes below are reference material, not an aston hardware qualification.
- A740 coverage depends on the selected firmware and OS ABI; board qualification requires its own memory and power evidence.

### 下一步

- Qualify concurrent Metal clients, repeated preemption, rendered pixels and frame pacing on sheng with iPadOS 27.
- Run third-party Metal applications with cryptid 0 on the metal2vulkan 963f0e64 build. Find why backboardd stopped presenting with sheng-metal-flow=1 before enabling any of its three paths.

### 证据

- `host`: [Reference sheng observation, not aston verification: Address/undefined-behavior checks pass for ring packets, preemption power sequencing, per-ring tables, queue FIFO, fence-history rollover and CPU-table fallback. Kernel, board, Turnip and Metal bridge builds target arm64e iPadOS 27. Hardware qualification of these changes is pending.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/reports/ipados27-gpu.md)
  Command: <code>python3 scripts/check-native-adreno-scheduling.py</code>. Revision: `509bd695c4f58dab8d2d005d1b92f5ba85312595`.
- `device`: [Reference sheng observation, not aston verification: iPadOS 27 build 24A446, capture 532856a9, panicked while idle on the home screen. The interrupted stack reached lck\_mtx\_unlock\_contended from native\_adreno\_preempt\_irq via gpuIrq. The board now queues preemption completion on a serialized thread call.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/package/GpuPowerProbe.cpp)
  Command: <code>fastboot boot sch1.img</code>. Revision: `8fcf9a4e0f3c5a23a820f85fd25189e2c7e83f87`.
- `device`: [Reference sheng observation, not aston verification: Boot 5cfa7b18a recorded a responsive desktop through 360 s with deferred CP preemption and cross-core stack sampling disabled.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/reports/ipados27-touch-frame-gaps.md)
  Command: <code>fastboot boot sch2.img</code>. Revision: `8ec842f38c21ef1d73e12000fae16df7442e0c73`.
- `host`: [Reference sheng observation, not aston verification: The patch series check passes for 25 patches over metal2vulkan 963f0e64. The frontend host check passes through the scanout presenter on Apple M1 through MoltenVK with the lowering thread, commit submission and warm pass enabled. The Turnip host simulation does not link, so its driver cache and plugin bridge phases did not run.](https://github.com/UniXNU/AdrenoMetal/tree/c333f988df1196a19abbe756f6e199984300a487/bridge/patches)
  Command: <code>python3 scripts/check-metal2vulkan-pin.py --latest; python3 scripts/check-native-metal-frontend-host.py</code>. Revision: `642c4fef77c28c5f9f32a3eb862fe8bea9ed0339`.
- `device`: [Reference sheng observation, not aston verification: iPadOS 27 build 24A446, same manual sequence in each boot. sheng-metal-flow=0: fps average 72.1 and 68.2, low 41.5 and 35.2. sheng-metal-flow=1: fps average 67.4 and 73.2, low 30.5 and 32.3. No swap-to-GPU delay data. A further sheng-metal-flow=1 boot did not reach the desktop: backboardd stopped at 4 commits about 81 s after the boot marker, with the warm pass at 1271 records and no panic. No stacks were captured, so its cause is unknown. In all sheng-metal-flow=1 boots the warm pass added no driver data.](https://github.com/UniXNU/AdrenoMetal/blob/6d7f73437087c57ee54a41adceb1735daaea405e/bridge/NativeMetalObjects.rs)
  Command: <code>fastboot boot m2v-flow-off.img; fastboot boot m2v-flow-on.img</code>. Revision: `8d96e320996cdf33aa739ad8bf336cff0459a268`.

## bluetooth {#bluetooth}

`planned`

组件: `QcaBluetooth`.

### 硬件与依赖

- WCN7850 firmware and NVM pinned by firmware/bluetooth/manifest.json.
- Linux reference https://github.com/ianchb/sm8550-mainline at 1fb56e66091e71160d7c7f8e13b065d5b6ab8b8c and https://github.com/ianchb/debian-sheng.
- Original iPadOS 27 build 24A446 bluetoothd and BlueTool for native ABI adaptation.

### 配置

- UART14 is QUP2 SE6 at 0x898000, GIC INTID 493, wrapper 0x8c0000 and apps-SMMU stream 0x423; CTS/RTS/TX/RX use GPIO 76/77/78/79 and BT\_EN uses GPIO 81.
- The board's 3.2 Mbaud operating rate uses a 51.2 MHz serial source and 16x oversampling.
- package/BluetoothFirmware.h and stage-bluetooth-firmware.py share firmware/qca under the Data addon.
- sheng-bluetooth=1 starts the bound UART14 worker after Data addon installation; log-bluetooth=1 enables initialization messages. The drivers/QcaBluetooth submodule or an explicit --local-module checkout supplies kernel and runtime sources.

### 操作步骤

- Stage firmware with scripts/stage-bluetooth-firmware.py OUTPUT --source FIRMWARE\_QCA\_DIRECTORY.
- Run scripts/check-wcn-power.py and scripts/check-bluetooth-board.py ASSEMBLED\_TREE after changing shared power.
- Build the protocol, GENI DMA and Skywalk sources with the selected arm64e kernel command, then package BlueTool and the native controller adapter.
- Boot the integrated image with log-bluetooth=1, then check pairing, reconnection, audio, sleep and recovery.

### 开发经验

- On iPadOS 27.0.1 \(24A446\) the device pairs AirPods Pro, reconnects after reboot without pairing again, toggles power, plays A2DP at normal volume and quality, and shows noise control and battery. Music over Bluetooth during 2.4 and 5 GHz speed tests stays normal.
- WcnPower records independent WLAN and Bluetooth ownership of the six shared supplies; the last owner releases them. Bluetooth-only startup omits the PCIe NoC vote. Wi-Fi startup uses this ownership interface.
- The firmware VFS reader waits for Data addon installation, accepts controller firmware names, bounds file size and rejects short reads.
- The protocol core uses the byte-identical Linux btqca.c initialization through namespaced host services. H4 backpressure retains input, and IBS control bytes enter only between TX packets.
- The GENI engine provides bounded DMA buffers, deferred IRQ work, wire drain checks, quiesce/resume and error reporting. UART.SK and BlueTool sources compile for the 27 target.
- BluetoothProbe binds UART14 clocks, 32 KiB of DMA buffers through the firmware-managed bypass bank, IRQ 493 and GPIO79 wake. The 64-bit physical DMA addresses use the same shared mapping planner as touch and audio; Bluetooth uses no private page tables. Shared configuration locks preserve touch and audio resources; GIC routes dispatch directly to registered handlers. Hardware faults abort command waiters immediately.
- The version-locked 27 adapter selects type zero, clears vendor hooks, preserves generic callbacks and skips the empty H4 pre-stop hook. Real HCI reports supply eleven capabilities, including coded and 2M PHY; an asynchronous 0x203b query supplies up to six native advertising sets. Model, cache, lower flags and broadcaster mode agree.
- The board publishes a bluetooth IOService before userland starts, with H4 encoding, 3.2 Mbaud and a private stable MAC. Public addresses use network order and convert to Linux bdaddr\_t at initialization. The runtime signs three arm64e binaries, preserves bluetoothd entitlements and uses read-only system-path overlays; BlueTool runs as root with transactions enabled.
- The kernel archive and runtime builder accept the same resolved QcaBluetooth checkout. UART clock-restore failures end the transport, preserve the hardware error and stop command waits and wake retries. The board startup entry uses C linkage to match the late platform probe. The archive record hashes the Bluetooth board, core, shim and SoC inputs before kernel linkage.
- Controller shutdown and faults clear the UART.SK queues, wake both rings and return the controller error from sync callbacks before data movement. In-flight notifications retain both rings until disconnect can release them.
- BlueTool starts the controller by reading kern.qbt\_power\_on because its sandbox denies sysctl writes; connecting to UART.SK also starts a stopped controller. Closing state belongs to the nexus that owns the session, so a channel torn down after its control socket closed cannot block the next connection.
- Extended scanning uses 0x2041 and 0x2042, because the controller rejects legacy scan commands once extended advertising commands have been used. Apple's scan extension stays off because it has no type zero backend.
- A random address \(0x2005\) is queued before a scan can be enabled, and starting an advertising set always sends its address \(0x2035\). When no resolvable address can be generated, the refresh uses a non-resolvable address and completes, so the daemon does not restart on the busy flag.
- Pairing keys need the keychain, which needs AppleKeyStoreState software key wrapping. The board returns /chosen/unique-chip-id through native\_aks\_device\_id.

### 完成条件

- The integrated kernel and payload boot with independent Bluetooth power and live UART DMA/IRQ.
- The native stack scans, pairs, reconnects, stores keys, supports BLE and plays Bluetooth audio.
- Idle power, audio continuity, recovery and Wi-Fi coexistence have device measurements tied to the image revision.

### 当前范围

- Inherited sheng implementation notes below are reference material, not an aston hardware qualification.
- Calls and microphone \(HFP/SCO\), sleep and wake, idle power and recovery are not tested.
- The kern.qbt\_\* sysctl names compile but have not run on the device; the device results use the earlier names. A build that resolves the driver from the submodule has not been run.
- Features that need Apple vendor commands are unavailable. Non-connectable advertising uses a non-resolvable address because the secondary IRK is zero.

### 下一步

- Boot an image built from the submodule to confirm the kern.qbt\_\* sysctls, then test calls and microphone, sleep and wake, idle power and recovery.

### 证据

- `host`: [Reference sheng observation, not aston verification: Production ownership code passes ASan/UBSan for both startup orders, idempotent votes, independent release, Bluetooth-only PCIe exclusion and failed transitions. The power operations are simulated.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/scripts/check-wcn-power.py)
  Command: <code>python3 scripts/check-wcn-power.py</code>. Revision: `bea420e4520654670b95549fb4d3ecb6511ae8e1`.
- `host`: [Reference sheng observation, not aston verification: WifiProbe, BluetoothProbe, ArmCpu, touch, audio and boot-log sources compile using the selected iPadOS 27 arm64e kernel commands. The Bluetooth builder compiles eight protocol and SM8550 objects.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/scripts/check-bluetooth-board.py)
  Command: <code>python3 scripts/check-bluetooth-board.py ASSEMBLED_TREE --extra-source ../UniXNU/drivers/ArmCpu/ArmCpu.cpp --extra-source package/TouchProbe.cpp --extra-source package/AudioProbe.cpp --extra-source package/BootLog.c</code>. Revision: `d846103b491c082ebf3f7928e5d8de12f7f1c343`.
- `source`: [Data firmware prefix shared by the VFS reader and staging tool; firmware/bluetooth/manifest.json pins both WCN7850 firmware inputs.](https://github.com/MoyuZJ912/UniXNU-aston/blob/e0f721be3f2e8438b94395bd8e3a456f8cacc80b/package/BluetoothFirmware.h)
- `host`: [Reference sheng observation, not aston verification: ASan/UBSan register models pass exact rate ratios, DFS handoff, native DMA page translation, ASID conflicts, bounded timeouts and preserved storage/touch routes.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/scripts/check-bluetooth-platform.py)
  Command: <code>python3 scripts/check-bluetooth-platform.py</code>. Revision: `d846103b491c082ebf3f7928e5d8de12f7f1c343`.
- `host`: [Reference sheng observation, not aston verification: Production GIC/GCC code passes ASan/UBSan for shared level IRQs, edge/exclusive checks, direct dispatch, masking, concurrent registration and shared clock lifetime.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/scripts/check-bluetooth-shared.py)
  Command: <code>python3 scripts/check-bluetooth-shared.py</code>. Revision: `d846103b491c082ebf3f7928e5d8de12f7f1c343`.
- `host`: [Reference sheng observation, not aston verification: The QcaBluetooth native adapter passes 144 AArch64 instruction cases at two ASLR slides and 58 ASan/UBSan HCI/policy cases. The arm64e library builds and passes signature verification. PAC operations are modeled without device keys; runtime installation and device checks are pending.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/reports/ipados27-bluetooth-native.md)
  Command: <code>cd drivers/QcaBluetooth &amp;&amp; out/native-venv/bin/python tools/test-native.py ORIGINAL_BLUETOOTHD &amp;&amp; python3 tools/test-type0.py ORIGINAL_BLUETOOTHD</code>. Revision: `97f48bf20bd47f233681668d50e5f5638e72384b`.
- `host`: [Reference sheng observation, not aston verification: The combined runtime verifies 45 files, three signed arm64e Bluetooth binaries, 716 launchd jobs, preserved native entitlements, 12 unchanged input trust modules and the original Data seed. Host libxpc accepts the cache. Bluetooth UART properties encode as little-endian values; platform sources and the executable/library mount patch compile for the target. Protocol simulation covers the Linux address conversion. Device execution and a complete image rebuild are pending.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/reports/ipados27-bluetooth-native.md)
  Command: <code>python3 scripts/check-bluetooth-runtime.py --runtime RUNTIME --os-root ORIGINAL_OS --seed-record ORIGINAL_RUNTIME_INPUTS</code>. Revision: `1258c87da0cdbb0a25f59b030cd48997c2793548`.
- `host`: [Reference sheng observation, not aston verification: The complete kernel and fileset link; the 176 MiB FAT payload and temporary boot image build. Actual payload extraction verifies nine Bluetooth exports, six packed files, runtime/trust hashes, H4/3.2 Mbaud ADT, preserved Data seed and no automatic reset. Device operation is pending.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/reports/ipados27-bluetooth-native.md)
  Command: <code>python3 drivers/QcaBluetooth/out/recovery-image/resume.py; python3 drivers/QcaBluetooth/out/recovery-image/verify-payload.py</code>. Revision: `b2c0146caafe7d23d57479ed401c7f4790e6c154`.
- `device`: [Reference sheng observation, not aston verification: Device log untagged-55f92f8343 records successful cache and Bluetooth overlays, an AMFI cache-hash query, PID 1 No service cache and Bluetooth DMA allocation ENOSPC before UART startup. The log writer reports zero write errors; device Bluetooth operation is not verified.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/reports/ipados27-bluetooth-startup.md)
  Command: <code>fastboot boot UniXNU/out/sheng/inputs/sheng-linux-log.img; python3 UniXNU-sheng/scripts/read-sheng-log.py --wait 50 --out CAPTURE</code>. Revision: `8f2af527c7204b07535b9e015a53c05d8029c0ee`.
- `device`: [Reference sheng observation, not aston verification: AirPods Pro pair, reconnect after reboot and play A2DP at normal volume and quality; noise control and battery work; one bluetoothd process for the whole run with no panic and no UART errors. The images predate the kern.qbt\_\* rename and the board and driver were local checkouts.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/scripts/read-sheng-log.py)
  Command: <code>fastboot boot boot.img (sheng-bluetooth=1 log-bluetooth=2); pair and play AirPods Pro; python3 scripts/read-sheng-log.py --wait 240</code>. Revision: `cc895db196751e155831d58e23a6e33984360367`.

## usb {#usb}

`planned`

组件: `QcomDwc3`.

### 硬件与依赖

- AppleUSBXDCI, AppleUSBXHCI, IOUSBDeviceFamily, IOUSBHostFamily and AppleUSBDeviceMux from the 24A446 kernelcache.
- Linux reference https://github.com/ianchb/sm8550-mainline for the SoC sequences and sm8550-xiaomi-sheng.dts for the board.

### 配置

- drivers/QcomDwc3 is a submodule of https://github.com/UniXNU/QcomDwc3.
- sheng-usb=1 runs the driver; 2 adds register sampling; 3 also takes the controller off the bus and back once.
- sheng-usb-host=&lt;s&gt; forces host mode after a delay; sheng-usb-back=&lt;s&gt; then returns to the cable's role.
- sheng-aks-sls=3 reports no passcode.
- board.toml adds the USB device and host stacks to the prelink roots for iPadOS 27 and leaves out AppleOnboardSerial and AppleSMC.
- chip\_id 0x8142 comes from board.toml; board-id 0xc and security-domain 1 come from the OS profile.
- The provider's configuration-string is standardMuxOnly.

### 操作步骤

- Generate the class layouts again after the kernelcache changes.
- Boot and connect to a Mac: the device lists as 05ac:12ab and lockdownd answers QueryType.
- Unlock the tablet and tap Trust: the Mac reports the device as paired and starts a lockdown session.

### 开发经验

- This CPU/storage change does not enable USB on aston. Existing sheng USB observations below are retained only as reference.
- payload.runtime.appsync and appsync=1 in board.toml do not change the USB stacks.
- AppleUSBXDCI programs the DWC3 itself; a subclass supplies the register window at base + 0xc000, one interrupter, power and PHYs. AppleUSBXDCI has no personality, so it needs an explicit kext load before the subclass registers.
- The driver does no cache maintenance. Stream 0x40 needs a stage 1 identity context with write-back inner shareable blocks; through the shared bypass bank the CPU reads stale event words.
- The eUSB2 reference is 38.4 MHz \(xo\_board 76.8 MHz, RPMH\_CXO\_CLK divides by 2\). With the 19.2 MHz table chirp passes and high-speed data fails.
- Slot 179 of the class keeps the family's configuration list when true, which leaves bNumConfigurations 0; it must stay false without an IOPort transport object.
- lockdownd starts on the IOResources property AppleUSBCableType=USBHost, one of its launch events; configd's USBDeviceConfiguration plug-in then sets the description and the family goes on the bus.
- UCSI reports the cable partner and selects the role. Until it answers, the charger's online value stands in for a host.
- In host mode the family's desired power is 0 once ports are idle, so the xHCI subclass answers on. The device stack answers 0 while the host role owns the core.
- A Mac looks up chip-id, board-id and security-domain in MobileDevice's device map. A pair that is missing makes it ask for a software update.
- SpringBoard accepts a CFUserNotification from a process on the system partition: it compares statfs f\_fsid of the executable with /System. The SystemOS union layer has its own number, so native-union-statfs-fsid reports the root volume's number for that layer.
- lockdownd completes Trust directly only in lock state 3. Any other state asks for a passcode.

### 完成条件

- A Mac enumerates the device, usbmuxd lists it and lockdownd answers, at 10 Gbps on a USB 3 cable and 480 Mbps on a USB 2 cable.
- A physical reconnect re-enumerates.
- Trust appears on the panel, the Mac pairs and starts a session, and lockdownd starts installation\_proxy, afc, atc and diagnostics\_relay.

### 当前范围

- Inherited sheng implementation notes below are reference material, not an aston hardware qualification.
- Sustained transfers and app installation have not run.
- One cable orientation has run on USB 3.
- Host mode runs Apple's xHCI stack and completes commands; enumerating a peripheral is not verified.
- MobileDeviceMinimumVersion has no answer; a Mac treats that as no update needed.
- fairplayd.A2 and adid stay disabled: with both enabled, SpringBoard does not finish starting.

### 下一步

- Run a sustained transfer and an app installation.
- Test the reverse cable orientation on USB 3.
- Verify peripheral enumeration in host mode.

### 证据

- `device`: [Reference sheng observation, not aston verification: 05ac:12ab at Device Speed 4 with a USB 3 cable; Trust accepted on the panel; a Mac reported Device Paired, then AMDeviceValidatePairing and AMDeviceStartSession succeeded.](https://github.com/UniXNU/QcomDwc3/blob/e4efe95c903a737e0f5955e5b50a8fb4d2a7d718/README.md)
  Command: <code>fastboot boot boot.img</code>. Revision: `1edc1ca7fc87defa8b2231254667ad4085320706`.

## 网络 {#network}

`planned`

组件: `Ath12kWifi`.

### 硬件与依赖

- WCN7850 PCIe endpoint, MSI routing, DMA callbacks and hash-pinned amss.bin, m3.bin and board-2.bin.

### 配置

- sheng-wifi=5 selects the mainline cfg80211/mac80211/ath12k runtime; wpa\_supplicant 2.12 owns userspace authentication.
- WifiProbe supplies power/PCIe/MSI and the 128 MiB DMA window; WifiNet exposes en0/Apple80211. The DTS exports /arm-io/wlan for wifid.
- The signed service runs at /usr/libexec/unixnu-wpa\_supplicant. package/WifiFirmware.h defines the shared loader/packer directory /private/var/ngpu/firmware/ath12k/WCN7850/hw2.0/.

### 操作步骤

- Run host checks affected by source changes, build the kernel/payload/boot image and verify packed inputs.
- Check scanning, association, DHCP, traffic, cancellation and signal display on the device; measure throughput, jitter and heat.

### 开发经验

- Device verification covers Wi-Fi toggling, SSID scanning, WPA2 association, DHCP, traffic and join-result delivery.
- Accepted joins complete after port authorization, cancel once and time out after 30 seconds. Association and cached peer RSSI supply signal updates.
- TX/RX use direct copies, shared DMA storage, bounded reuse and batching; mac80211 supplies aggregation, reordering, FQ and AQL.
- Data firmware reads wait for addon installation. Packaging validates file hashes, service/cache signatures, stock jobs, trust modules and the preserved Data seed.
- The shared runtime cache retains the native Wi-Fi jobs and adds the supplicant alongside the Bluetooth service configuration; the original Data seed and existing trust modules are preserved.

### 完成条件

- Scanning, association, address configuration and sustained bidirectional traffic pass with the selected firmware.

### 当前范围

- Inherited sheng implementation notes below are reference material, not an aston hardware qualification.
- Current-image device checks pending: cancellation/timeout completion, runtime signal display, Data firmware startup, throughput, jitter and heat.

### 下一步

- Complete the pending device checks and tune packet processing, scheduling and power from the measured results.

### 证据

- `host`: [Reference sheng observation, not aston verification: ASan/UBSan fixtures pass with simulated radio operations; the lifecycle releases 287 tracked allocations. Production audit: 125 objects, 13 XNU imports, zero missing imports and zero duplicate definitions. Kernel, payload and packed-image checks pass.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/reports/ipados27-wifi-mainline-migration.md)
  Command: <code>python3 scripts/check-wifi-association.py</code>. Revision: `fa9af675a5c56e27e1aaf0693c77939a4641a3ef`.
- `device`: [Reference sheng observation, not aston verification: Wi-Fi toggling, SSID scanning, WPA2 association, DHCP, traffic and join-result delivery are verified. The current image has been accepted for temporary boot.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/reports/ipados27-wifi-association.md)
  Command: <code>fastboot boot build/wifi-mainline/fix9/boot.img</code>. Revision: `fa9af675a5c56e27e1aaf0693c77939a4641a3ef`.
- `source`: [The launchd cache fixture checks that the Wi-Fi job and other stock jobs retain their settings when the icon service environment is applied.](https://github.com/MoyuZJ912/UniXNU-aston/blob/e0f721be3f2e8438b94395bd8e3a456f8cacc80b/scripts/check-wifi-launchd.py)

## 音频 {#audio}

`planned`

### 硬件与依赖

- ADSP firmware from modem\_a, SMEM, SMP2P, GLINK, the GPR channel adsp\_apps.
- Speakers: six CS35L43 amplifiers on QUP1 SE5 and QUP2 SE0 \(I2C 0x40 to 0x42\), shared reset gpio90, secondary MI2S \(gpio121 to 124\).
- Microphones: WCD938x codec on the TX SoundWire master \(0x6d30000\), reset gpio108, supply ldob15; TX and VA macros.

### 配置

- sheng-audio takes bits \(sheng-adsp=2 is required\): any nonzero value serves the audio service, 2 plays a 1.5 s 750 Hz test tone at boot, 4 brings up the microphone path and reads two seconds of capture, 8 runs the lock sound test.
- sheng-audio-pa moves the DSP period buffer \(default 0xd0000000\); sheng-audio-tone-ms and sheng-audio-atten set the tone.
- The payload addon carries hal/ShengAudio.driver under audio/; patches/xnu/zzyd-sheng-audio-addon-mount.patch mounts it over /System/Library/Audio/Plug-Ins/HAL. Its CDHash joins the owner trust cache.

### 操作步骤

- Read the \[audio\], \[amps\], \[audio-glink\], \[audio-buffer\], \[mic\], \[mic regs\] and \[mic capture\] log lines with scripts/read-sheng-log.py.
- Read \[audio-props\], \[audio-service\], \[audio-io\], \[audio-thread\], \[audio-clock\], \[audio-requests\] and \[audio-sync\] for the iOS path: the plug-in's volume and peak, late and silent periods, write-ahead and read-behind, IO cycle intervals, clock skew, the audio server's IO thread scheduling and host clock, and the plug-in's last start and stop requests.
- Run scripts/check-audioreach-host.py, scripts/check-cs35l43-host.py and scripts/check-geni-i2c-host.py after changing the codecs.

### 开发经验

- The ADSP image loads in place from the split adsp and adsp\_dtb files in /image of the modem\_a FAT volume.
- The DSP offers 24 intents of 128 bytes on adsp\_apps and grants a 4 KiB one on request; the GLINK remote intent table keeps it.
- The amplifiers play ASP RX1 directly \(DSP bypassed, no amplifier firmware\): top three slot 0, bottom three slot 1, gain 18 dB, 16-bit I2S at 48 kHz from the SoC as clock master.
- The DSP takes buffers as a 32-bit address with the stream index \(0x1001 &amp; 0xf\) in the upper word. The period buffer is low DRAM outside the kernel's window, mapped write-combined; the audio streams stay in SMMU pass-through.
- Programming a translating SMMU context for the audio streams resets the board; the hypervisor keeps those context banks.
- PRM commands go from the PRM port \(2\) and use PRM clock ids: the TX core clock is 0x30c. The macro and digital codec votes make the LPASS registers accessible.
- The VA macro gates the TX SoundWire master's clock on SM8550; with its gate and the TX macro's on, the link comes up and the codec enumerates as device 1.
- The primary microphone is AMIC3 on micbias 3 into ADC2, codec data port 1 channel 2, master port 2, TX decimator 0 from SWR\_MIC1 and codec DMA TX3, mono 48 kHz.
- iOS sees the plug-in device only with the Thunderbolt transport type: VirtualAudio makes it a driver device with one output and one input port. Built-in devices need Apple port descriptions, and a USB device needs a location the audio server does not take from a plug-in.
- The plug-in and the service share one timeline anchored at boot on the 19.2 MHz host timer \(400 ticks per frame, computed in 128-bit\). Playback and capture rings hold 65536 frames; the service takes 480-frame periods and keeps four in flight.
- The DSP answers a playback buffer once it has copied it, so the steady lead is measured per run \(about 1600 to 2000 frames\) and the published lead is at least 300 ms.
- Capture answers carry a byte count and an offset; only those bytes are taken, and a short period is normal.
- CoreAudio takes the host clock to be 24 MHz \(one constant behind AudioGetHostClockFrequency\). The plug-in finds that constant and the service sets it to 19.2 MHz on its shared page; without it the audio server's IO cycles ran 25 percent long and playback and recording stuttered.
- The zero time stamps start at the frame IO starts on, every 65536 frames, with the raw clock algorithm. A period under the safety offset stops the audio server's IO.
- The audio server's IO thread runs with a time constraint \(priority 97, period 409600 ticks, computation 204800\).
- The audio server is arm64e on iPadOS 27: dlsym signs the pointer it returns, so the plug-in strips the signature to read the two instructions behind AudioGetHostClockFrequency and calls through the signed pointer. The VirtualAudio image-added rebind is built for arm64 only, because the slot pointers there are authenticated with their slot address and a plain rebind faults.
- The audio overlay hides the system HAL plug-in directory from audiomxd. board.toml audio\_system\_plugins lists BTAudioHALPlugin.driver, and the runtime builder copies its unchanged bundle from the OS image. Other system plug-ins stay hidden.
- Audio takes AppsSmmuLock and uses sm8550\_gcc\_update32 for its GCC clock vote when present, so the vote and shared SMMU setup do not race Bluetooth and touch.
- The microphone rail request holds AppsSmmuLock because TCS 2 is shared with the USB rails. ADSP messages reach 560 bytes to fit UCSI.

### 完成条件

- Each declared route carries the selected audio format through playback or capture and handles start/stop correctly.

### 当前范围

- Inherited sheng implementation notes below are reference material, not an aston hardware qualification.
- Playback sounds harsh in places; no speaker equalization or protection runs.

### 下一步

- Qualify iOS playback and capture across apps and routes, then add speaker equalization and protection.

### 证据

- `source`: [Implementation and configuration described in this section](https://github.com/MoyuZJ912/UniXNU-aston/blob/e0f721be3f2e8438b94395bd8e3a456f8cacc80b/package/AudioProbe.cpp)
- `host`: [Reference sheng observation, not aston verification: PASS audioreach: 182 checks; PASS cs35l43: 225 checks; PASS GENI I2C: 2169 checks](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/scripts/check-audioreach-host.py)
  Command: <code>python3 scripts/check-audioreach-host.py; python3 scripts/check-cs35l43-host.py; python3 scripts/check-geni-i2c-host.py</code>. Revision: `9e9971883be72b2fd76b8fb552367a9e4940aa63`.
- `device`: [Reference sheng observation, not aston verification: Speaker test tone: DSP mapped the buffer, 155 periods sent and 151 returned, all six amplifiers PLL-locked with no error interrupts. WCD938x enumerated \(manufacturer 0x0217, part 0x010d\). Capture: 200 of 200 periods returned, 191328 bytes, 97 percent non-zero samples, peak 128 in a quiet room.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/scripts/read-sheng-log.py)
  Command: <code>fastboot boot boot.img (sheng-adsp=2 sheng-audio=6); python3 scripts/read-sheng-log.py --wait 240</code>. Revision: `9e2e6de1e63d9493e841d51c6b41108e75c7d537`.
- `device`: [Reference sheng observation, not aston verification: Playback and recording smooth from the start. Host clock set to 19200000 Hz, IO thread period 409600 ticks. 4822 of 4843 IO cycles 15 to 25 ms apart. Write-ahead 16501 to 19638 frames, skew -474 to 1 frames, 0 late periods.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/scripts/read-sheng-log.py)
  Command: <code>fastboot boot boot.img (sheng-adsp=2 sheng-audio=14); play music and record in Voice Memos; python3 scripts/read-sheng-log.py --wait 240</code>. Revision: `dea464ef093349dd746582691b0eaa3807fe1441`.

## 电源 {#power}

`implemented`

组件: `AppleKeyStoreState`.

### 硬件与依赖

- The existing EPSS governor and bq28z610 read-only battery telemetry.

### 配置

- sheng-cpufreq-boost-ms=80; sheng-cpufreq-frame-ms=0; sheng-battery=2.

### 操作步骤

- Compare idle, touch scrolling and sustained work with battery current and per-domain frequency logs.

### 开发经验

- Aston previously inherited a 1000 ms maximum-frequency touch hold and a 300 ms GPU frame floor. The phone now requests an 80 ms hold and disables the frame floor.
- These are board policy choices, not measured energy savings. The load governor and its existing downscale hysteresis remain active.
- Device 2026-11-09 \(boot 5, diag\): the pack current stayed negative for the whole run and every \[charger\] and \[usb\] row was zero. Charging on this SoC is the battery manager in the audio DSP, which was never started.
- sheng-adsp=2 now starts the DSP with the firmware of modem\_a \(read in place\). The board's adspslpi region is 0x9ea00000 + 0x4880000 \(devicetree and adsp.mdt span\); sheng's 0x4680000 leaves one of the 57 load segments outside, so package/AdspProbe.cpp uses the aston size.

### 完成条件

- Measured idle current and temperature stabilize, with no new frame stalls under the same workload.

### 当前范围

- No thermal sensor feedback or deep idle implementation is added. L3 still uses the inherited maximum vote.

### 下一步

- Collect temperature, current and frequency measurements before further tuning.

### 证据

- `source`: [Implementation and configuration described in this section](https://github.com/MoyuZJ912/UniXNU-aston/blob/e0f721be3f2e8438b94395bd8e3a456f8cacc80b/package/ShengBattery.cpp)
- `host`: [Reference sheng observation, not aston verification: PASS battery manager: 4074 checks](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/scripts/check-battery-host.py)
  Command: <code>python3 scripts/check-battery-host.py</code>. Revision: `8719a19294bc79eed72366a19070acfd8e131737`.
- `device`: [Reference sheng observation, not aston verification: PPS adapter: 8.72 V at 1.3 A in, battery +1.99 A, 1 to 3 percent in 3 minutes. Mac: PD 5 V at 1.1 A in \(1.2 A limit\), battery +0.25 to +0.4 A on the desktop, 20 to 21 percent. Temperature 31.4 to 32.9 C; full 9353 mAh, design 9800 mAh, 172 cycles.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/scripts/read-sheng-log.py)
  Command: <code>fastboot boot boot.img; python3 scripts/read-sheng-log.py --wait 240</code>. Revision: `8f5d921d7a3b71a20a97f551cad546dc8e2f3700`.
- `device`: [Reference sheng observation, not aston verification: CPU: domain 1 between 499 and 2803 MHz, domain 2 between 595 and 2956 MHz, about 1.2 GHz and 620 MHz mean when idle. GPU: every vote accepted, 61 percent of the time at 680 MHz at 7 percent mean busy.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/scripts/read-sheng-log.py)
  Command: <code>fastboot boot boot.img (sheng-cpufreq=4 sheng-gpu-dcvs=1); python3 scripts/read-sheng-log.py --wait 240</code>. Revision: `a338c71a6f83809c84686b4996478f1c4cd3f3ab`.
- `source`: [The GPU hard interrupt schedules CP preemption completion on a high-priority thread call that can take the submission mutex.](https://github.com/MoyuZJ912/UniXNU-aston/blob/e0f721be3f2e8438b94395bd8e3a456f8cacc80b/package/GpuPowerProbe.cpp)
- `source`: [Aston CPU and storage candidate fix; host checks and remaining device checkpoints are described in reports/cpu-storage-fix.md.](https://github.com/MoyuZJ912/UniXNU-aston/blob/e0f721be3f2e8438b94395bd8e3a456f8cacc80b/board.toml)

## 镜像组装 {#packaging}

`implemented`

组件: `DarwinBoot`, `XnuPrelink`, `SoftwareAES`.

### 硬件与依赖

- Prelinked kernel, hardware DTB, generated ADT, trust cache, Data seed, platform identity and firmware DTB.

### 配置

- Use aston\_ipados27\_defconfig and the package workflow; Ace3-UniXNU owns firmware and boot-image assembly.

### 操作步骤

- Build kernel and package, then payload with --unique-chip-id and the selected trust-cache/Data inputs.
- Run ./unixnu bootimg -D ../UniXNU-sheng --uefi ../uefi-sheng --dtb &lt;firmware.dtb&gt; and inspect the assembly report.

### 开发经验

- The build stages a hash-checked RamBlock copy before all consumers. source.json records its source revision and patch digest.
- Existing Data seed identity is preserved; a normal rebuild must not request init\_data or choose an erase action.
- XnuPrelink keeps retained kexts at their collection addresses, so each native segment must fit before the first retained kext segment of its root. The iPhone17,2 24A446 collection, with this board's roots, leaves 11872 KiB for \_\_TEXT\_EXEC and \_\_KLD, 1165 KiB for \_\_DATA\_CONST and \_\_LASTDATA\_CONST \(to AppleARMPlatform\), and 1872 KiB for \_\_DATA \(to Libm, which IOAVFamily needs\). The iPad17,3 collection leaves 11968, 1571 and 1952 KiB.
- The iPadOS build b5bb234 needs 11888, 1392 and 1920 KiB there. The iOS build leaves out the WiFi stack \(893 KiB code, 75 KiB data\), the embedded GPU firmware \(151 KiB of constants, ASTON\_GPU\_FIRMWARE=1 restores it\) and the sparse IOUserServer dispatch table \(160 KiB of constants\). An offline run of XnuPrelink's Layout with those sizes leaves 864, 93 and 16 KiB.
- CI 42832522940's native kernel needed 1904 KiB of \_\_DATA: BootLog's weak WiFi rings \(native\_wifi\_text, \_note, \_pmic, \_dump\) still got zero defaults of their declared sizes \(72 KiB\) from the source storage build. package/WifiAbsent.c defines them with one element; a ld64.lld check shows the strong definitions drop the weak ones. Recomputed with section alignments, \_\_DATA is 1840 KiB of 1872.
- Prelink of that kernel against the iPhone17,2 kernelcache, run offline with emit\_prelink.py: without reviewed pins 206 kext calls bind to the unmapped-call stub and 30 kext pointers stay unmapped. With UniXNU-ishtar's ported iPad17,3 pins, 23 and 25 remain. scripts/derive-fileset-pins.py adds 11 function and 9 data pins \(e.g. task\_is\_privileged, csm\_resolve\_os\_entitlements\_from\_proc, IOService::Start\_Invoke, OSObject::metaClass, gIOParentMatchKey\). It reads each unmapped target's kext slots at the same place in the iPad17,3 collection and takes the iPad pairing. With scripts/fileset-24A446-d94ap-symbols.json, 10 stubbed calls and 2 unmapped pointers remain. Each of those is unpaired on iPad17,3 too, where the b5bb234 build left 19 and 2 and booted.

### 完成条件

- Kernel and prelink succeed, payload contains all declared inputs, and the boot image matches the bootloader format and size limit.

### 当前范围

- Windows host checks do not compile the arm64e kernel. The pinned macOS/Xcode build and phone boot are pending.

### 下一步

- Build the kernel and payload on macOS, then pack with the matching aston firmware.

### 证据

- `source`: [Implementation and configuration described in this section](https://github.com/MoyuZJ912/UniXNU-aston/blob/e0f721be3f2e8438b94395bd8e3a456f8cacc80b/patches/xnu/series)
- `source`: [The 27 archive recipe explicitly selects --lto for the fileset reference. The common builder invalidates stale references and handles LTO link objects; XnuPrelink records the recovered 24A446 ABI identities.](https://github.com/MoyuZJ912/UniXNU-aston/blob/e0f721be3f2e8438b94395bd8e3a456f8cacc80b/board.toml)
- `source`: [Historical working-tree observation: sheng b714917c, iPadOS 27.0.1 24A446, boot-prelink-fixed.img: instruction fetch abort at 0xfffffff00dbb4c74 with LR 0xfffffff00b5a3340 in native\_legacy\_display\_allocate. Corecrypto and SourceStorage initialization had completed.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/reports/ipados27-startup-repair-2026-11-02.md)
- `source`: [Historical working-tree observation: 62 prelink regressions pass. The packed kernel has 266 fixed original-function branches \(205 mobile graphics, 51 HID, eight IOSurface, two GPU\), preserved absolute GOT values and no additional native external branch instructions. This is host evidence, not a desktop boot result.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/reports/ipados27-startup-repair-2026-11-02.md)
- `source`: [Historical working-tree observation: sheng b714917c, 24A446: NativeLegacyDisplay and NativeHidInput initialized, APFS mounted the root OS and SystemCryptex, then load\_init\_program stopped with offline scratch Data mount failed: 2. The payload lacked initrd and PackedRAMDisk.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/reports/ipados27-startup-repair-2026-11-02.md)
- `source`: [Historical working-tree observation: Recovered runtime inputs match boot-framepath.img: seed 1bde7901df3acd0e8a14cd89928bedc12c07ef2128c6bce18ffccf3611a666a3 equals the existing data-seed-215g-skipca/data.dbr. The payload includes the original owner trust cache and GPU addon, required ADT placeholders and 870-byte normal arguments without autoreset or data-reset. Checks cover 266 branches, five absolute data symbols and 189 vnode descriptor pointer sites. Local inputs are stored in the ignored UniXNU unixnu.local.toml.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/reports/ipados27-startup-repair-2026-11-02.md)
- `source`: [Historical working-tree observation: The repaired v4 kernel and restored runtime inputs ran to the 120-second auto-reset deadline: log state 2, 61 rounds, zero write errors and no panic. SpringBoard PID 30, backboardd PID 61 and wifid PID 49 are present. The diagnostic image differs from the normal payload only by sheng-autoreset=120. Visual presentation was not verified. Two unresolved data imports and 24 trap references remain outside this boot qualification.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/reports/ipados27-startup-repair-2026-11-02.md)
- `source`: [The iPadOS 27 payload runtime prepares IPSW trust modules, source-built GPU/audio addons and explicit first-install Data before kernel compilation. Existing installations reuse the original seed; its content hash and UUID are recorded. The normal board arguments now include the validated persistence, GPU, display and log switches without relying on unixnu.local.toml.](https://github.com/MoyuZJ912/UniXNU-aston/blob/e0f721be3f2e8438b94395bd8e3a456f8cacc80b/board.toml)
- `source`: [The package workflow selects the repair UniXNU revision, restores or imports the original Data seed, and preserves a seed backup. Cache loss fails unless first-install generation is explicitly selected. Rebuilding the full reference exposed lost order matches for IOCircularDataQueueCopyLatest and get\_aiotask; the fixture now fixes both identities and the profile rejects new unresolved references.](https://github.com/MoyuZJ912/UniXNU-aston/blob/e0f721be3f2e8438b94395bd8e3a456f8cacc80b/.github/workflows/package.yml)
- `source`: [The iPadOS 27 payload sets two environment variables for iconservicesagent in the launchd service cache.](https://github.com/MoyuZJ912/UniXNU-aston/blob/e0f721be3f2e8438b94395bd8e3a456f8cacc80b/board.toml)
- `source`: [Global AppSync scope, on-device signature repair, dynamic kernel trust, native ABI observations and successful host/kernel/payload/boot-image builds with the concurrent backlight sources. Original Data is preserved. The combined image was accepted by fastboot boot on b714917c; desktop and application behavior remain to be observed.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/reports/ipados27-appsync.md)
- `source`: [Aston CPU and storage candidate fix; host checks and remaining device checkpoints are described in reports/cpu-storage-fix.md.](https://github.com/MoyuZJ912/UniXNU-aston/blob/e0f721be3f2e8438b94395bd8e3a456f8cacc80b/board.toml)

## 诊断 {#diagnostics}

`implemented`

### 硬件与依赖

- Serial or framebuffer diagnostics, panic region, boot checkpoints and a recovery path.

### 配置

- boot-progress=2 enables checkpoints; source and image revisions accompany every log.
- On the iPadOS 27 native source path, sheng-log=1 plus boot-ui-trace=1 starts a separate process-capture worker. boot-ui-focus3=chronod adds the display-query client to backboardd and SpringBoard. Arm64e return-address PAC is stripped for diagnostic stacks.

### 操作步骤

- Run the existing check for the changed area and keep its command, output and input revision.
- Record the last completed checkpoint and the first failing operation; link the captured output.

### 开发经验

- The boot log records APFS Data capacity at mount separately from persistence state, with a status code for missing attributes or invalid geometry. It never substitutes invented capacity.
- Files, fileproviderd and diskspaced exit reasons join the existing exit diagnostics. A successful block read does not prove that the storage UI or application containers work.
- Windows native fixtures cover publication order, failure gates, CPU samples and XNU QoS rules; no WSL or QEMU is used.
- Every restart panicked in vnode\_rele\_ext \(usecount -ve, v\_type VBAD\) during vfs\_unmountall's system pass on the sealed OS volume under the SystemOS union \(dounmount, vflush, vclean, vnode\_update\_identity\); sheng records the same panic on low-battery shutdown. patches/xnu-12377/aston-reboot-readonly-unmount.patch leaves read-only mounts mounted in that last pass; Data is unmounted and synced in the first pass as before.
- scripts/pull-aston-data.py copies the changed Data pages from TWRP read only \(hashes compared on the phone\), scripts/build-aston-data-image.py lays them over the seed and scripts/apfs-read.py lists and extracts files \(unencrypted APFS, stdlib\), so iPadOS's own crash reports can be read after a test.

### 完成条件

- Each claimed milestone has a reproducible command, a matching source/image revision and an accessible result.

### 当前范围

- A Data mount capacity row is a boot-time snapshot, not live free-space accounting. No new device log is available.

### 下一步

- Read \[data mount capacity\], \[data\] and sheng-exit records after testing the new image.

### 证据

- `source`: [Implementation and configuration described in this section](https://github.com/MoyuZJ912/UniXNU-aston/blob/e0f721be3f2e8438b94395bd8e3a456f8cacc80b/scripts/read-sheng-log.py)
- `source`: [CLI1 header flag 1 identifies exact user-mode samples with the interrupting CPU ID in the wait field. The target CPU records its own timestamp, PC, LR and FP. CPF1 records the policy vote and EPSS domain state per governor window.](https://github.com/MoyuZJ912/UniXNU-aston/blob/e0f721be3f2e8438b94395bd8e3a456f8cacc80b/package/BootUiTraceProbe.c)
- `host`: [Reference sheng observation, not aston verification: The shared sampler retains the three expected return addresses for a blocked thread. The regression covers the TH\_WAIT \| TH\_RUN transition observed in boot 6ba5a54e, terminating threads, missing or out-of-stack saved state and a wrapping frame address.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/scripts/check-boot-ui-trace.py)
  Command: <code>python3 scripts/check-boot-ui-trace.py</code>. Revision: `571fcc972a4ea3e8c402183ba98a0a8f67a4750a`.
- `source`: [With cs-profile=1, exact cross-calls target the SpringBoard main thread. The trace includes Mach wait durations and destinations, per-core PMU availability, EL0 instructions and cycles, and sampler time.](https://github.com/MoyuZJ912/UniXNU-aston/blob/e0f721be3f2e8438b94395bd8e3a456f8cacc80b/scripts/sheng-springboard-profile.py)
- `source`: [Aston CPU and storage candidate fix; host checks and remaining device checkpoints are described in reports/cpu-storage-fix.md.](https://github.com/MoyuZJ912/UniXNU-aston/blob/e0f721be3f2e8438b94395bd8e3a456f8cacc80b/patches/xnu-12377/aston-data-diagnostics.patch)
- `host`: [Windows native policy, publication and capacity fixtures passed. API stand-ins do not qualify XNU, APFS or phone hardware; area remains implemented.](https://github.com/MoyuZJ912/UniXNU-aston/blob/e0f721be3f2e8438b94395bd8e3a456f8cacc80b/reports/cpu-storage-fix.md)
  Command: <code>python scripts/check-aston-cpu-storage.py --xnu .cache/xnu-verify --ramblock .cache/RamBlock --cc .cache/toolchain/ziglang/zig.exe cc</code>. Revision: `c72ab4e2aa75727569162823cac20100b4c36703`.
- `device`: [Boot 5: 240 rounds, 0 write errors; reboot panic vnode\_rele\_ext symbolized against the CI 42596717622 kernel; 152 CrashReporter and 142 DiagnosticReports files read from Data.](https://github.com/MoyuZJ912/UniXNU-aston/blob/e0f721be3f2e8438b94395bd8e3a456f8cacc80b/reports/aston-boot5-20261109.md)
  Command: <code>python3 scripts/read-sheng-log.py --decode log.bin; python scripts/pull-aston-data.py; python3 scripts/apfs-read.py data.img find .ips</code>. Revision: `1ed895b0299f38274ca15657b9d9eca3c3ad6c39`.

## arm64e-os {#arm64e-os}

`implemented`

### 硬件与依赖

- iPadOS 26.5.2 build 23F84 IPSW for iPad17,1 to iPad17,4; target identity iPad17,3 J820AP.
- Public XNU source xnu-12377.121.6; arm64e profile requirements in https://unixnu.com/porting/arm64e.

### 配置

- iPadOS 27.0.1 \(24A446\) on XNU 12377.121.6 with the selected ordered compatibility patches.

### 操作步骤

- Check FEAT\_PAuth, EL1 key register writes and PAC instruction behavior on all eight CPUs.
- Build the arm64e kernel from xnu-12377.121.6 with the ported 4 KiB patches, then prelink the 23F84 kexts.
- Follow the bring-up order: arm\_init, bsd\_init, root mount, launchd, SpringBoard.

### 开发经验

- The CPU and Data diagnostic patches apply after the existing device series. They do not change the XNU source pin or claim a new OS ABI qualification.

### 完成条件

- The arm64e kernel reaches launchd on sheng from the 23F84 root volume, then SpringBoard.

### 当前范围

- Full kernel link and device ABI qualification remain pending for this branch.

### 下一步

- Build the current OS profile on the pinned Xcode runner.

### 证据

- `host`: [Reference sheng observation, not aston verification: IPSW SHA-256 f7f55fa36097a0c8f8784eefcd9eabfce3a1c55ecd470f6885f4862a9446f9c3; kernel Darwin 25.5.0, xnu-12377.122.8\~1/RELEASE\_ARM64\_T8142; 317 kexts.](https://updates.cdn-apple.com/2026SpringFCS/fullrestores/140-25976/000BB0A6-045B-47FF-AE4E-D8BF722E24FD/iPad17%2C1%2CiPad17%2C2%2CiPad17%2C3%2CiPad17%2C4_26.5.2_23F84_Restore.ipsw)
  Command: <code>shasum -a 256 &lt;ipsw&gt;; ipsw extract --kernel &lt;ipsw&gt;; ipsw kernel version &lt;kernelcache&gt;</code>. Revision: `759eb61b6b8d475de5b3d1b39e1de1f5294e8d9a`.
- `host`: [Reference sheng observation, not aston verification: dyld cache iOS 26.5, 4261 images, 83 subcaches; 1208 SMSTART SM and 1287 SMSTART ZA in 11 subcaches. Sampled functions with names include \_sme\_sgemm, \_sme\_strsm and \*\_SME2.](https://updates.cdn-apple.com/2026SpringFCS/fullrestores/140-25976/000BB0A6-045B-47FF-AE4E-D8BF722E24FD/iPad17%2C1%2CiPad17%2C2%2CiPad17%2C3%2CiPad17%2C4_26.5.2_23F84_Restore.ipsw)
  Command: <code>ipsw extract --dyld -a arm64e &lt;ipsw&gt;; scan 4-byte aligned words for SMSTART SM (0xd503437f) and SMSTART ZA (0xd503457f)</code>. Revision: `759eb61b6b8d475de5b3d1b39e1de1f5294e8d9a`.
- `host`: [Reference sheng observation, not aston verification: 27 patches on xnu-12377.121.6; mach.development.bcm2837 links, 19789128 bytes, arm64e MH\_EXECUTE with LC\_DYLD\_CHAINED\_FIXUPS \(pointer format 7\). The prelink step stops: the input is MH\_FILESET.](https://github.com/UniXNU/UniXNU-sheng/blob/689400177f93219a38bd7cf5ae2e9f5782adc594/configs/sheng_ipados26_defconfig)
  Command: <code>./unixnu defconfig sheng_ipados26_defconfig -D ../UniXNU-sheng; ./unixnu kernel -D ../UniXNU-sheng</code>. Revision: `4ed86f68213ed7dc83726987c2d3a78b7c16114a`.
- `host`: [Reference sheng observation, not aston verification: 298 entries, base 0xfffffe0007004000, 585131 fixups in pointer format 8, 0 symbols in every entry. For the 31 prelink roots \(30 with code, 7 kernel resources\): 1864 kernel targets, 47807 pointer sites, 42027 branch sites.](https://updates.cdn-apple.com/2026SpringFCS/fullrestores/140-25976/000BB0A6-045B-47FF-AE4E-D8BF722E24FD/iPad17%2C1%2CiPad17%2C2%2CiPad17%2C3%2CiPad17%2C4_26.5.2_23F84_Restore.ipsw)
  Command: <code>parse LC_FILESET_ENTRY, LC_DYLD_CHAINED_FIXUPS and kext __TEXT_EXEC branches of the decompressed kernelcache</code>. Revision: `4ed86f68213ed7dc83726987c2d3a78b7c16114a`.
- `source`: [The XNU patch records Mach receive waits for the selected thread and handles trapped PMU reads during profiling.](https://github.com/MoyuZJ912/UniXNU-aston/blob/e0f721be3f2e8438b94395bd8e3a456f8cacc80b/patches/xnu-12377/sheng-main-thread-profile.patch)
- `source`: [Aston CPU and storage candidate fix; host checks and remaining device checkpoints are described in reports/cpu-storage-fix.md.](https://github.com/MoyuZJ912/UniXNU-aston/blob/e0f721be3f2e8438b94395bd8e3a456f8cacc80b/board.toml)

</div>
