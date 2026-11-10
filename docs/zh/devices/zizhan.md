# Xiaomi MIX Fold 2 \(zizhan, SM8475\): UniXNU bring-up derived from Pong

[qiumochen/UniXNU-zizhan](https://github.com/qiumochen/UniXNU-zizhan)

<div v-pre>

Xiaomi MIX Fold 2: iPadOS 18.7.10 inner display, touch, Adreno 730 rendering and battery readings, derived from UniXNU-pong. A 120 Hz panel and 95.3 moving fps in one synthetic workload; native Wi-Fi Settings join, automatic association and cross-band reconnect have bounded device evidence; thermal control, sleep/wake and daily-use qualification remain open.

源记录: [porting.toml](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/porting.toml), `034a0b0037b28f4ff4e46703cbd4d9bb75db25e5`.

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
| [网络](#network) | `device-verified` |
| [cellular](#cellular) | `planned` |
| [音频](#audio) | `planned` |
| [电源](#power) | `implemented` |
| [镜像组装](#packaging) | `host-verified` |
| [诊断](#diagnostics) | `implemented` |

## 配置 {#configuration}

`host-verified`

组件: `PongPlatform24`.

### 硬件与依赖

- zizhan \(22061218C\) live /sys/firmware/fdt; MIUI V14.0.15.0.TLRCNXM, Android 13, kernel 5.10.136.
- SM8475 shared support and PongPlatform24 from UniXNU-pong \(Nothing Phone \(2\)\).
- iPad7,11 iPadOS 18.7.10 / 22H374 restore.

### 配置

- board.toml: name=zizhan; device\_tree.source=device:dts/zizhan.dts; kernel.defconfig=zizhan\_ipados18\_gpu\_defconfig.
- Default GPU config: CONFIG\_XNU\_PONG\_ADRENO\_PLATFORM=y, CONFIG\_XNU\_PONG\_POWER=y, CONFIG\_XNU\_PONG\_WIFI=y, CONFIG\_XNU\_PONG\_BACKLIGHT=y.
- Apply patches/xnu-ipados18/series in order: 0001-0006 and 0008-0021.

### 操作步骤

- Generate dts/zizhan.dts from the live DT with tools/gen\_reserved.py, replacing model, compatible, DRAM and reserved-memory in the Pong layout.
- Select uefi-zizhan Platforms/Xiaomi/zizhanPkg/zizhan.dsc; retain ARM64, SM8475, 22H374 and board layers.

### 开发经验

- The second DRAM bank is 0xf4600000+0xba00000, versus Pong 0xf1400000+0xec00000. ADSP uses 0x9fd00000+0x3100000, versus Pong 0x85700000+0x2800000. SMEM, IPCC, AOSS and cmd-db addresses agree.
- The Pong build scripts do not depend on the board name.
- The device default now enables GPU and Wi-Fi together. The old Wi-Fi defconfig is a relative symlink to the canonical GPU defconfig; local default build/packaging no longer needs separate profile or radio-enable options. The board-specific Wi-Fi hardware inputs remain in zizhan-wifi-sm8475.json.
- One canonical device defconfig enables GPU and Wi-Fi; the previous Wi-Fi name is a compatibility symlink. Default and explicit reduced CI kernels built successfully.
- The canonical device profile now also enables verified L18 backlight. A board-specific version-2 ADT uses the live primary-panel maximum 2047, minimum nonzero 4, DSI0 and VC0; mismatched Pong panel parameters are rejected.
- THERM-01 adds a zizhan-only TSENS/EPSS input JSON from live Android FDT; it contains no adopted thermal policy. The 11-07 default-off observer now gets reviewed physical resources through an ADT contract. A separate explicit 22H374 service-presence control can stage the installed OS370 fairplayd selection without changing default exclusions.
- The publication records the zizhan-only fixed display-domain board resource and its guarded ADT encoding; foreign or changed apertures are rejected. Host resource/transport replays and both kernel configurations passed; no new display power qualification is claimed.

### 完成条件

- Compile the board DTS, kernel and boot image, then reach the iPadOS Home Screen on the phone.

### 当前范围

- Outer display and audio remain disabled. Default GPU/Wi-Fi integration does not qualify untested long-duration or broader network cases; see the network limits.

### 下一步

- Keep build and device evidence separate and reproduce the published configuration before changing board inputs.

### 证据

- `source`: [Publication ownership reconciliation for the cumulative 11-08/09 configuration change; host and device evidence remain separated, with runtime limits retained.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-09-publication.md)
- `source`: [Live board inputs and isolated service-policy catalogs; no new kernel configuration or default runtime capability.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-06-daily-use-development.md)
- `host`: [The default enables GPU, Wi-Fi and verified primary L18 brightness with board-owned limits. Reduced CI still builds without GPU-only references.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-05-display-and-backlight.txt)
  Command: <code>ci_kernel.sh default/reduced; inspect compiled settings and ADT; UI/helper compile/sign</code>. Revision: `88e5106dca99c03b9be1af02ceae5b041480a83d`.
- `device`: [Combined device defaults without DEFCONFIG/PROFILE/WIFI overrides passed native automatic association, keys, DHCP and HTTPS 200. Zero link loss or canvas-mapping errors; three complete Settings screenshots, deadline return and fresh UFS log.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-05-default-gpu-wifi.txt)
  Command: <code>cycle.sh out/g344-default-combined/pong-xnu-initial.img g344-default-combined 480</code>. Revision: `cc016a5c44c1ed074e98ea7c1104c1e5cbdff88f`.
- `host`: [One canonical device defconfig enables GPU and Wi-Fi; the previous Wi-Fi name is a compatibility symlink. Default and explicit reduced CI kernels built successfully.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-05-default-gpu-wifi.txt)
  Command: <code>ci_kernel.sh default and explicit CI; ci_boot_ufs.sh default/WIFI=0/explicit CI; check-wifi-host.py</code>. Revision: `cc016a5c44c1ed074e98ea7c1104c1e5cbdff88f`.
- `source`: [Live hardware, partition backup and stock UEFI memory-map comparison.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-10-28-device-prep.md)
- `source`: [Board-specific addresses and differences from Pong.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-01-battery.md)
- `host`: [Hosted macos-15-intel runner resolved four layers, compiled the DTS, applied 13 XNU patches and linked the CI kernel; pong-macos-products uploaded.](https://github.com/qiumochen/UniXNU-zizhan/actions/runs/41304992346)
  Command: <code>GitHub Actions zizhan macOS build (macos-15-intel, Xcode 16.4, pong_ipados18_ci_defconfig)</code>. Revision: `28d9f4fe869293e7a384b18b800ceb8dd56c1244`.

## 固件与启动 {#firmware}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- uefi-zizhan: uefi-pong plus Platforms/Xiaomi/zizhanPkg.
- Stock uefi\_b uefiplat.cfg memory map.

### 配置

- PIL Reserved size=0x1DC00000; remove Demura and QTEE.
- SimpleFbDxe: framebuffer=0xb8000000, 2160x1916, inherited cont\_splash\_region.
- Temporary fastboot boot only; do not flash partitions.

### 操作步骤

- build\_fw.sh builds the zizhanPkg FD with EDK II; build\_bootimg.py combines BootShim, FD and the device DTB into boot v4.
- DarwinBoot24 reads the UniXNU menu and arms pong\_autoreset before XNU handoff.
- ci\_boot\_ufs.sh rejects command lines above its 1020-byte limit; DarwinBoot24 requires fewer than 1024 bytes.

### 开发经验

- The inner panel shows the Silicium logo and UniXNU menu with correct color and orientation; DarwinBoot24 hands off to XNU.
- On refusal, DarwinBoot24 appends the reason to logfs:\\BOOTFAIL.TXT, retries, then returns to fastboot.
- A Wi-Fi kernel with larger embedded firmware occupied the temporary low-memory ReadFile buffer while the loader requested scanout pages. Free copied kernel/ADT inputs before reserving the optional 96 MiB pool. g299/g300 used the same kernel with radio disabled; the changed loader restored the real pool and complete screenshots.
- The zizhan DarwinBoot24 panel pool reservation is 128 MiB below 4 GiB, leaving five canvas slots with the default two display buffers. v6 and subsequent ordinary-display trials exercised this loader; this does not qualify DSI power-off or sleep.

### 完成条件

- Temporary boot reaches the menu and XNU; failures retain an automatic return path.

### 当前范围

- Qualcomm DXE binaries still come from uefi-pong Binaries/pong. There is no zizhan DisplayDxe and the outer panel stays off.

### 下一步

- Audit the stock FV Panel\_L18\_38\_0c\_0a\_sec\_dsc\_cmd.xml before attempting outer-panel support.

### 证据

- `source`: [Publication ownership reconciliation for the cumulative 11-08/09 firmware change; host and device evidence remain separated, with runtime limits retained.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-08-panelpool-128.md)
- `device`: [Loader-only comparison changed no-pool fallback into a real 96 MiB zero-copy pool and full sampled screenshot.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-04-wifi-settings-and-roaming.txt)
  Command: <code>cycle.sh g299-wifi-kernel-radio-off; cycle.sh g300-loader-radio-off</code>. Revision: `03363797d9ffb10fd35ad5823331e89b4bb3c624`.
- `source`: [Device record of UEFI, DarwinBoot24 handoff and early XNU boot.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-10-29-xnu-bringup.md)

## CPU 与中断 {#cpu}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- SM8475: four Cortex-A510, three Cortex-A710, one Cortex-X2; GICv3, 19.2 MHz timer and PSCI.

### 配置

- ADT cluster-type is required with PONG\_ADT\_CLUSTERS=1; build two clusters with \_\_ARM\_AMP\_\_.
- pong\_fast\_pri=47 and pong\_fast\_cpu=7 by default.
- ml-timeout-lock-panic-scale=40; interrupt-masked-debug-mode=1.

### 操作步骤

- 0008 exposes E/P clusters to AMP, 0014 prefers an idle X2 for UI-priority threads, and 0003 bounds qsort recursion to avoid early stack overflow.

### 开发经验

- All eight CPUs start. An AMP kernel without ADT cluster-type stalls early \(g97\).
- Under Gunyah, ordinary pauses can exceed the DEVELOPMENT 500 us interrupt-masking threshold. Following sheng, scale timeouts by 40 and log masking violations; preserve genuine fatal panic handling.
- In g170, a stalled app-opening workload used 0.73 CPU on A710 and 0.09 on X2 for the SpringBoard main thread; 0014 gives UI work X2 preference.
- Read-only Android inventory found 81 thermal zones, 62 cooling devices and three CPU frequency policies; four temperature reads failed and remain explicit errors. Live FDT identifies two TSENS-v2 providers and confirms the current three EPSS/PDMEM domain addresses. These are input observations, not XNU thermal control.
- THERM-01 default-off one-shot TSENS-v2 observation is qualified in g396: two 2.8 banks, 32 unique VALID last-temperature words, independently checked signed deciC decoding and 35.5-46.9 C range. g395 temperature SKIP is retained; its extra TRDY gate was removed according to the actual v2 getter. This proves a bounded register observation, not update freshness, calibration, continuous monitoring or thermal control.
- POWER-02 source review found that ArmCpu halt directly affects the executing CPU, while the native XNU sleep coordinator calls halt on CPU objects; correct target-CPU shutdown/idle continuation and boot-CPU resume are prerequisites. Live DT has rail-pc and shared l3-off/llcc-off states with local-timer-stop; declared parameters and Android cumulative idle counts are inputs, not XNU suspend qualification. Scheduling, EPSS and physical PSCI-domain topologies must remain distinct.

### 完成条件

- Start eight cores and place UI threads on X2 when available.

### 当前范围

- No thermal control. Repeated trials heat the phone and can corrupt DRAM ramoops logs.

### 下一步

- Design bounded multi-time sampling, update/age/error semantics and cross-system sensor mapping checks before any continuous temperature service or policy. Vendor normal/map policies are not readable as plaintext in this audit; do not adopt DT high-temperature trips or Android scaling maxima as the XNU thermal policy.

### 证据

- `source`: [POWER-02 candidate corrects the Darwin24 remote haltCPU/local quiesceCPU contract. Host builds and normal ADSP trial do not qualify CPU suspend, context restore or target-state wake.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-07-power-unattended.md)
- `source`: [POWER-02 complete design and read-only audit only; runtime code, kernel/image, OS installation and sleep qualification unchanged.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/plan/2026-11-07-lockscreen-suspend-design.md)
- `source`: [Sanitized two-bank version/control and 32 raw VALID words with decoded temperatures, source dirty-snapshot and actual kernel/image identity. One-shot read-only scope; no freshness or thermal-policy claim.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-07-tsens-readonly.txt)
- `source`: [Uncommitted candidate: full/reduced builds and 34 host cases PASS; g395 temperature SKIP, g396 32 VALID observations PASS. Original supervisor FAIL remains preserved; Android completion was independently witnessed 46.224 seconds later within a 120-second window.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-07-tsens-readonly.md)
- `source`: [Android-only bounded read-only inventory, explicit error handling, reproducible board-input generation and host replay. No new XNU MMIO or thermal-policy qualification.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-06-daily-use-development.md)
- `source`: [Eight-core boot \(k4\), E/P scheduling comparison and tsample thread records.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-10-30-root-and-autoloop.md)
- `source`: [X2 preference and cadence measurements.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-01-120hz-and-cadence.md)

## 内存与 DMA {#memory}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- Live device-tree memory and reserved-memory nodes.

### 配置

- dts/zizhan.dts memory@80000000 and reserved-memory.

### 操作步骤

- DarwinBoot24 passes only owned RAM ranges to XNU.

### 开发经验

- XNU reports Pong RAM: 4 owned banks, 9728 MiB. The phone has 12 GiB; holes are excluded from VM.

### 完成条件

- XNU boots and reports managed memory.

### 当前范围

- Managed RAM is 9728 MiB; not all physical memory is used.

### 下一步

- Check whether ranges above 0x9\_0000\_0000 can safely be given to XNU.

### 证据

- `source`: [k1 reports 9728 MiB of managed RAM.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-10-29-xnu-bringup.md)

## 存储与根卷 {#storage}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- UFS 3.1 and Android userdata \(f2fs\).
- OS, SystemOS and Data images prepared locally from 22H374 on macOS.

### 配置

- pong\_shngroot\_4k=&lt;4K block&gt; identifies the root image extent.
- pong\_ufs\_async=0; pong\_ufs\_defer enabled by default.

### 操作步骤

- install\_pinned.py uses pinalloc to allocate a contiguous 19.4 GiB /data/hackios/root.img, writes OS/SystemOS/Data windows and reports its first block.
- RootLayout publishes each window as separate IOMedia.
- 0006 immediately sends matched notifications when publishResource finds IOResources still configuring.

### 开发经验

- Before 0006, roughly three of four boots failed to mount root. APFS probing held its lock while waiting for IOBSD, forming a cycle with IOResources configuration; waiting-thread dumps identified it in g28. g36-g39 mounted root in 4/4 trials after the fix.
- OS, SystemOS and writable Data mount; stock 22H374 launchd starts.
- Existing SmmuTakeover WIP selects SMR/S2CR validity and SID mask from IDR0.EXIDS. APPSSMMU on this phone has EXIDS disabled; g272-retry through g275 mounted root, wrote fresh UFS klog and returned to Android. EXIDS-enabled behavior has host build coverage only.

### 完成条件

- Mount root reliably and preserve Data writes across boots.

### 当前范围

- The root image is a pinned f2fs file. Never move or defragment it in Android; a 40 GiB placeholder was used to preserve a contiguous extent.

### 下一步

- Provide a software IOAESAccelerator for AppleImage4 to resolve its wait on /defaults.

### 证据

- `source`: [Root layout, root-mount deadlock analysis and before/after 0006 results.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-10-30-root-and-autoloop.md)

## 显示 {#display}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- Inner DSI-1 panel: 2160x1916, command mode, DSC, 60/120 Hz.
- Bootloader cont\_splash\_region: 0xb8000000+0x2b00000.

### 配置

- ADT display-scale=2 and artwork-scale-factor=2 \(1080x958 points\).
- pong\_panel\_hz=120 by default.
- Kernel defaults: pong\_dpu\_flip=1, pong\_dpu\_bufs=2, pong\_zc=2, fb\_swapwait=1.

### 操作步骤

- Send timing@1 timing-switch commands through the DSI command FIFO to select 120 Hz.
- Flip DPU directly to CoreAnimation surfaces using triple buffering and no scanout GPU copy.

### 开发经验

- At scale 3, 1916/3 is fractional and SpringBoard status-bar Auto Layout recurses until crash; scale 2 reaches Home Screen \(u3\).
- INTF\_1 counters changed from 60.5/s to 120.2/s and latch ceiling from 16.6 to 8.3 ms. The early synthetic workload improved from 44.6 to 54-55 fps; later display-link measurements are in gpu.
- Removing the 2.5 ms per-frame scanout copy presented every submitted frame without counted tears.
- Pre-create and retain cached mappings for actual reserved panel slots, then lease bounded subdescriptors to canvases; failed reservations are not offered. DSI timing and asynchronous brightness share an owner lease. Real read/write/readback and native Settings slider targets 512/1331/1024 passed; no photometry is invented.
- POWER-02's immediate deliverable is the native request-to-inner-panel-off/wake-to-visible-first-frame slice; CPU deep idle and unrelated device runtime PM are later increments. MiniIOMobileFramebuffer RequestPowerChange still has no hardware transaction. The public IOGraphics power enum is Off=0, MinUsable=1, On=2; one prior device observation saw only scalar=1, so the off/on request and completion ABI remain unqualified.
- A bounded DSI command DMA path now consumes one dedicated DarwinBoot24 low-address page, requires a fresh fixed display group/context snapshot with identity mode before each long packet, and restores controller registers only after DMA completion and idle. Host replay and builds pass; no long packet or panel transition has run on device.

### 完成条件

- Display iPadOS Home Screen on the inner panel with stable presentation at 120 Hz.

### 当前范围

- Outer display is unsupported. Inner brightness uses real DCS readback and the native Settings chain; panel photometric calibration and automatic ambient sensing are not provided.
- Old screenshot log lines were truncated to about 39/135 sampled columns. The segmented format was device-verified in g248/g249; sampled screenshots do not replace pixel-level panel inspection.

### 下一步

- Do not repeat memory-v2 unchanged: its normal-display device boot returned to fastboot after about 59 seconds and produced an empty fresh XNU console \(0 screenshots\); the supervisor's transport return is not feature PASS. First localize the pre-console boot failure using the retained candidate, loader, ADT and short ramoops evidence; fix the smallest source/packaging issue and rebuild. Once ordinary boot is restored, verify the reserved command-page handoff and identity-gated mapping on device. Then connect the observed native Off/On request ABI to a serialized bounded panel transaction, drain real producers, and verify a visible first frame. Do not claim the MVP until an attended device off/wake round returns without reboot. CPU/SoC sleep and network wake remain later POWER-02 stages.

### 证据

- `source`: [POWER-02's opt-in ordinary timing FIFO and owner controls passed on device, and v5 confirmed a bounded fixed group/context snapshot. A low-address command page handoff and identity-gated long-command DMA implementation pass host replay, final reduced/full kernel builds and DarwinBoot24 build. memory-v2 then attempted the first ordinary-display device boot with that loader/ADT/kernel; after fastboot boot it returned to fastboot in about 59 seconds, but fresh ramoops contained only an empty console descriptor, no XNU boot log and no screenshots. Supervisor returned Android and cycle rc=0, but feature review classifies the device round FAIL; no command-page/DMA or panel transition is qualified.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-07-power-unattended.md)
- `source`: [POWER-02 complete design and read-only audit only; runtime code, kernel/image, OS installation and sleep qualification unchanged.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/plan/2026-11-07-lockscreen-suspend-design.md)
- `device`: [Normal 120/60 Hz trials returned complete screenshots and HTTPS200 with direct CP completion763/763 and665/665. Older wait snapshots do not prove hangs. Actual clean OS/UI/helper and manifest were verified and promoted with retained rollback artifacts, without further phone writes.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-05-display-and-backlight.txt)
  Command: <code>cycle.sh g374-live-fence-control, g375-live-60hz; clean prepared-state promotion</code>. Revision: `9d7afd134e56d14dcdd2d0862f3a18f49427b49a`.
- `device`: [Real cached canvas mapping reuse; initial 307, writes 64/512/restored307; native slider512/1331/restored1024; real HID targets1986/back1028 and native1024 restoration passed. Normal 60/120 modes are measured separately; incomplete g367 screenshot is retained as a limitation.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-05-display-and-backlight.txt)
  Command: <code>cycle.sh g346, g350-read-repeat, g351, g361, g364-hid-thumb, g367, g368</code>. Revision: `88e5106dca99c03b9be1af02ceae5b041480a83d`.
- `source`: [Inner-panel iPadOS Home Screen \(u3\).](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-10-30-u3-ipados-homescreen.jpg)
- `source`: [120 Hz transition and cadence measurements.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-01-120hz-and-cadence.md)
- `source`: [DPU zero-copy triple-buffer implementation and measurements.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-01-zero-copy-and-return-paths.md)
- `device`: [Six images per trial decoded all 135/135 columns and 120/120 rows. Home Screen and Weather span the image; the old right black region was missing log data.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-02-shot-and-watermark.md)
  Command: <code>cycle.sh g248, g249; tools/zizhan/mac/shot.py</code>. Revision: `c9c8fd274c279a8571b525a1e1dbdf8eddf84d9d`.

## 输入 {#input}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- Inner ST FTS touch \(spi0.0 fts-pri\), st\_fts\_l18.ubin firmware.
- PMIC power key.

### 配置

- pong\_touch=1; touch\_flip=2 \(mirror Y\) by default.
- Hold the power key for pong\_button\_reset milliseconds \(default 3000\) to reset to fastboot.

### 操作步骤

- 0002 adds bsd/dev/pong\_fts.c. SE4 is GSI-only, so SPI is bit-banged through GPIO.
- Deliver events to backboardd through the inherited Pong HID path.

### 开发经验

- POWER-02 bring-up isolation now keeps unmarked SBDisableAutoDim and startup wake/unlock behavior unchanged by default; explicit ownership marker and migration are opt-in and preserve external preference changes. No device UI qualification or OS installation occurred.
- Touch opened Settings from Home Screen \(t4\).
- A three-second power-key hold resets running iOS to fastboot.
- ui\_compat18.c also owns presentation hooks. The 22H374 UIKit.InProcessAnimationManager class match was corrected and exercised in g298; synthetic-animation evidence does not establish additional physical-touch coverage.
- Optional touch\_lat diagnostics correlate actual kernel samples, HID read/dispatch and native pan gesture states without changing recognition thresholds. FTS synthetic tests support bounded delay, vertical scrolling and finite actual HID control drags. Default input remains physical.
- An opt-in pong\_open URL entry was added to the UI adapter and rebuilt/signed on the host. Recorded device attempts returned false; current installed OS uses the retained older UI. Original native Settings navigation remains separately observed; arbitrary URL launch is not device-verified.

### 完成条件

- Use touch to open apps and scroll pages.

### 当前范围

- Outer touch \(spi2.0 fts-sec\) is unsupported; volume keys remain unaudited. g298 measures synthetic input, not real-finger latency.

### 下一步

- Audit volume-key PMIC addresses and measure physical-touch latency separately from synthetic cadence.

### 证据

- `source`: [Publication ownership reconciliation for the cumulative 11-08/09 input change; host and device evidence remain separated, with runtime limits retained.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-08-panelpool-128.md)
- `source`: [Host UI bring-up preference ownership replay, signed UI candidate only; automatic lock/screen-off remains unverified on hardware.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-07-power-first-implementation.md)
- `device`: [Actual sample/read/dispatch/gesture/swap/panel timestamps separate transport and native recognition. Real HID thumb drag changed physical brightness and restored the known UI value; probe actions alone do not establish hardware success.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-05-display-and-backlight.txt)
  Command: <code>touch_lat=1; cycle.sh g349-settings-scroll, g352-home-gesture, g363-pan-control; finite HID g364-hid-thumb</code>. Revision: `88e5106dca99c03b9be1af02ceae5b041480a83d`.
- `source`: [Settings opened by touch.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-10-30-t4-settings-by-touch.jpg)
- `source`: [Touch-driver trial records.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-10-30-root-and-autoloop.md)
- `source`: [Historical display-link WIP in ui\_compat18.c: not built on November 2, host-built on November 3; device validation was added later without upgrading input status.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-02-gpu-astc-and-fairplayd.md)
- `source`: [g296-g298 compare the actual UIKit class match, synthetic scrolling and first-frame limits; physical-touch qualification remains separate.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-04-displaylink-device.md)

## GPU {#gpu}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- Adreno730v3; local device a730\_sqe.fw, gmu\_gen70000.bin and a730\_zap.\* firmware, excluded from Git.
- Turnip and metal2vulkan.

### 配置

- PONG\_ADRENO\_FIRMWARE selects the local firmware directory.
- pong\_gpu\_level=9 \(710 MHz initial GMU level\) by default.
- MercuryPosterEx is denied GPU access by default; pong\_gpu\_deny=- restores it.

### 操作步骤

- Start Adreno after rootvnode exists and publish the Metal provider after root mount.
- Cache surface mappings and scanout imports.

### 开发经验

- User photos confirm GPU-rendered Home Screen and animations.
- MercuryPosterEx competes with backboardd: 5/13 baseline trials lost the GPU. Denying it yielded 6/6 without loss and an early mean scrolling rate of 54.5 fps.
- Fixed 900 MHz did not outperform DCVS; GPU clock was not the limiting factor.
- A ledger-killed GPU client \(SBRendererService on Battery\) freed BO pages with user mappings alive, causing pmap\_assert\_free. PongAdrenoClient::dropViews now unmaps/releases mappings; NativeAdrenoMemory::release calls pmap\_disconnect per page before returning pages to VM.
- After ASTC layout fixes, g248/g249 opened Weather with DeviceSupportsASTC=1; six segmented images per run had 135/135 columns across the screen. g251 Clock and g252 Settings also had complete app images.
- g253/g254 completed 592/592 and 403/403 GPU submissions. A one-submit deadline difference was backboardd work issued 26 ms before reset, not persistent fence blockage.
- Tungsten called PXCreateContext with 0x0, triggering Photos assertions. A Photos-only hook clamps zero axes to 1; g262/g263 and final-kernel g264 reached Photos with ASTC both off and on.
- g296 observed UIKit.InProcessAnimationManager; the old UIViewInProcessAnimationManager-only hook missed it. g298 matched the actual class, filtered 121 requests and reached 95.3 moving fps versus 56.7-58.4 baseline. Trace presentation gaps p50/p90 improved from about 16.6/33.3 to 8.3/16.6 ms.
- Cold-start and late-allocation controls distinguish actual cached-map reuse from ordinary allocation. The rare g342 display failure remains unqualified, and wait-time snapshots are now distinguished from live completion. Main-screen idle first frame remains about 80 ms; the early CA flush candidate regressed to about 302 ms and was removed rather than enabled.

### 完成条件

- Render Home Screen and apps through the GPU without GPU loss during sustained scrolling.

### 当前范围

- Wallpaper extensions cannot use the GPU; metal2vulkan still spends about 10-20 ms CPU time per submission.
- Sampled screenshots verified Home Screen, Weather, Clock, Settings and Photos after ASTC fixes. Multitasking, touch animations and Photos album/search/edit paths need manual checks; ASTC remains off by default. Stuck-copy and poison detection remain enabled for previously observed GPU losses.
- Photos launch and album landing page are verified; grid, search, edit and image viewing after first-use prompts need manual interaction. IOSurfaceSharedEvent listeners are still missing.
- g298 improves the synthetic animation tail; first frame after idle remains about 75-80 ms. g363 measured 79.76 ms median and a controlled early-flush candidate regressed to 301.68 ms, so it was removed. This is not a global 120 fps or resolved first-frame claim.
- g342 had failed canvas mappings and an old wait snapshot that appeared one fence behind. That snapshot is not the live CP timestamp; revised summaries read actual completion separately. Early slot mappings remove late physical pager recreation, but the rare display failure was not reproduced under control; do not claim every GPU hang fixed.

### 下一步

- Implement IOSurfaceSharedEvent listeners before restoring dependent services and wallpaper GPU access.
- Use retained HID/gesture/swap/panel segments to investigate the remaining main-screen front-end delay; native Settings scroll samples were substantially faster. Preserve the rejected early-flush control and qualify fairplayd/wallpaper independently.

### 证据

- `source`: [POWER-02 scanout candidate keeps the existing timing control as default and adds opt-in packet-type-preserving FIFO execution. Software presenter drain does not acknowledge GPU/DPU latch or release live surfaces for power collapse.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-07-power-unattended.md)
- `device`: [Normal 120/60 Hz trials returned complete screenshots and HTTPS200 with direct CP completion763/763 and665/665. Older wait snapshots do not prove hangs. Actual clean OS/UI/helper and manifest were verified and promoted with retained rollback artifacts, without further phone writes.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-05-display-and-backlight.txt)
  Command: <code>cycle.sh g374-live-fence-control, g375-live-60hz; clean prepared-state promotion</code>. Revision: `9d7afd134e56d14dcdd2d0862f3a18f49427b49a`.
- `device`: [Legacy wait snapshot 763/762 differed from direct CP completion763/763 at deadline, with original ring protocol unchanged. Corrected report distinguishes old waits from live hardware completion; three complete screenshots and HTTPS passed, no actual stale-fence watch fired.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-05-display-and-backlight.txt)
  Command: <code>cycle.sh g372-stall-watch, g374-live-fence-control</code>. Revision: `9d7afd134e56d14dcdd2d0862f3a18f49427b49a`.
- `device`: [Persistent panel mappings were reused on real canvases. Rare g342 display failure was not reproduced; old wait snapshots alone do not prove a hardware stall. Idle first panel median79.76ms; early flush regressed301.68ms and was removed. Healthy trace/deadline work is distinguished from long fence stalls.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-05-display-and-backlight.txt)
  Command: <code>cycle.sh g345, g346, g347, g348, g363, g365, g368; frame-latency.py</code>. Revision: `88e5106dca99c03b9be1af02ceae5b041480a83d`.
- `device`: [Matching the real UIKit animation class activated filtering; moving fps 56.7-58.4 to 95.3. All trace submissions completed, zero lost events. Animation tail improved; first frame did not. All three trials returned to Android.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-04-g298-displaylink.txt)
  Command: <code>cycle.sh g296-gpu-default, g297-gpu-native; replace UI library and reuse g296 image for g298-gpu-fixed</code>. Revision: `42629e5d8d86ead5c4b57d752e3b3187e702ed6f`.
- `source`: [GPU bring-up, GPU-loss diagnosis and wallpaper-denial controls.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-10-30-root-and-autoloop.md)
- `source`: [Per-frame GPU submission timeline.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-10-31-frame-timeline.md)
- `host`: [Final Metal bridge/plugin builds passed; ASTC format numbers checked against the iPhoneOS SDK.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-02-astc-layout.md)
  Command: <code>metal-refresh.sh astc-final (bridge/plugin build)</code>. Revision: `e3be89264924267a610e472e559c9d4d8a66b803`.
- `device`: [ASTC=1: Weather appeared in the left region of three old-format screenshots; automatic Android return. Right-side data was missing.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-02-astc-layout.md)
  Command: <code>round.sh g247 pong_touch_synth=3 tsa=1118 touch_lat=1 pong_shot=60 pong_shot_ms=1000 pong_astc=1</code>. Revision: `e3be89264924267a610e472e559c9d4d8a66b803`.
- `device`: [With the watermark bridge and ASTC=1, Weather started and all six Home/Weather images were complete; automatic Android return. Fence-stall diagnosis remained open at that point.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-02-shot-and-watermark.md)
  Command: <code>metal-refresh.sh watermark; cycle.sh g249</code>. Revision: `c9c8fd274c279a8571b525a1e1dbdf8eddf84d9d`.
- `device`: [Clock and Settings started with complete screenshots. Photos repeatedly exited with PXPixelSizeAreaIsZero. Each trial returned to Android.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-02-shot-and-watermark.md)
  Command: <code>cycle.sh g250–g252</code>. Revision: `caa3a06b6b809be46146fc890995b16d51c8a99c`.
- `device`: [Both traces had no lost events; all submissions completed and zero-copy fences did not time out. Deadline fence was normal work issued 26 ms before reset.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-02-fence-diagnostics.md)
  Command: <code>cycle.sh g253, g254; pong_gtrace_delay, pong_gtrace, pong_gtrace_ib</code>. Revision: `a0eb276866aee06a31189f182335760d5a39d4a9`.
- `source`: [Historical ASTC follow-ups, installed fairplayd state and unverified display-link WIP.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-02-gpu-astc-and-fairplayd.md)
- `device`: [The hook clamps Tungsten 0x0 to 1x1; Photos stopped hitting the zero-size assertion. Final ASTC=1 trial stayed running and returned to Android.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-03-photos-context.md)
  Command: <code>cycle.sh g262-g264; pong_astc=0/1; Photos PXCreateContext hook</code>. Revision: `1ebf568205630bc5fa25737ae95392d2908f0e8a`.
- `host`: [Prepared image contained the hook; UI, bridge/plugin and CI/GPU builds passed. With no device the refresh script left the image untouched. No new device fps or screenshots.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-03-displaylink-host.md)
  Command: <code>Read-only prepared OS/UI inspection; build/sign UI library and Metal bridge/plugin; CI/GPU kernel builds; ui-refresh.sh no-device preflight</code>. Revision: `103d97f1ecc7c874429ae1003d29c4a45c4eb383`.
- `source`: [Earlier clock-only image interpretations were withdrawn: all 16 original captures match the raw pixel records and macOS independently decodes complete static home content. g380/g381 add bounded normal-boot coverage without resolving the rare g342 cause. Temporary shot diagnostics and presentation candidates were removed from maintained source; no graphics fix is claimed. A genuine CS4K allocation panic remains a separate boot limitation.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-06-overnight.md)

## 网络 {#network}

`device-verified`

组件: `PongPlatform24`.

### 硬件与依赖

- QCA6490 \(PCI 17cb:1103\); read-only device firmware export and Linux v7.0.14 ath11k sources kept outside this repository.

### 配置

- Default zizhan\_ipados18\_gpu\_defconfig enables GPU and Wi-Fi together; the legacy Wi-Fi name is only a compatibility symlink. Build/package defaults select that profile and startup follows actual compiled settings. WIFI=0 remains an explicit diagnostic override. Private association inputs remain disabled.
- Optional pong\_wifi\_hold=1 requires the native UI-test witness and excludes kernel association/cycle fixtures. It observes real HTTPS, route/DNS, link/IP and lease generation without requesting renewal or reconnect. Default is off.

### 操作步骤

- Check PCIe0, WLAN GPIOs and SIDs against the Android live DT; build and pack the isolated Wi-Fi configuration.
- Temporarily fastboot boot over rear USB-A with automatic return. Diagnose power, PCIe, DMA, MHI, firmware, MSI and scan in order; preserve the first failure.

### 开发经验

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
- GPU/backlight changes preserve the verified Wi-Fi default and native service binding. Existing Wi-Fi host regressions passed and normal display/brightness trials retain independent HTTPS evidence; display build success is not network proof.
- 11-07 publication corrected record ownership: Wi-Fi regressions use tools/zizhan/tests/wifi-\*; power and other daily-use tests no longer belong to the network area. Network runtime behavior is unchanged.

### 完成条件

- Scan and associate with a real network.
- On en0, verify DHCP, requested renewal, disconnect route/DNS cleanup, reconnect and three public HTTPS responses \(g290 default network path\).

### 当前范围

- The default GPU configuration now includes Wi-Fi. Current radio processing still depends on polling; actual GIC MSI delivery is unverified.
- Bidirectional cross-band tests and one Settings join passed against the current WPA2 APs. Natural T1 expiry, different SSIDs/subnets, long-duration roaming, enterprise/SAE and broader device coverage remain unqualified.
- DHCP ACK compensation remains available for missing route/DNS state; g309 observed native takeover. UI fixture files and firmware stay local, and the optional UI test is disabled unless explicitly requested.
- Automatic join, short connection hold and one native radio off/on lifecycle passed. This is not long-duration qualification. One logging boot failed before userland with shared-cache ENOMEM; preserve that genuine panic as a failed prerequisite.

### 下一步

- Keep the verified clean prepared OS, UI/helper and manifest aligned; old prepared artifacts are retained and canonical/trial descriptors match. Investigate the separate no-Settings canvas-mapping failure without treating it as a successful UI trial.
- Qualify natural T1, different subnets, long-duration reconnect and actual MSI separately before changing the shipping default.

### 证据

- `source`: [POWER-02 owner-control trial retained one 64MiB WLAN DMA allocation failure. Same frozen kernel with owner disabled and the FIFO timing trial subsequently allocated the arena and reached firmware/station/scan milestones; one-sample controls do not establish causality or network long-term qualification.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-07-power-unattended.md)
- `device`: [Independent HTTPS200 remained available with real GPU/backlight services; current Wi-Fi regressions pass. No broader network qualification is inferred.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-05-display-and-backlight.txt)
  Command: <code>cycle.sh g346, g350-read-repeat, g367-default-60hz, g368-default-cold120; check-wifi-host.py</code>. Revision: `88e5106dca99c03b9be1af02ceae5b041480a83d`.
- `device`: [Combined device defaults without DEFCONFIG/PROFILE/WIFI overrides passed native automatic association, keys, DHCP and HTTPS 200. Zero link loss or canvas-mapping errors; three complete Settings screenshots, deadline return and fresh UFS log.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-05-default-gpu-wifi.txt)
  Command: <code>cycle.sh out/g344-default-combined/pong-xnu-initial.img g344-default-combined 480</code>. Revision: `cc016a5c44c1ed074e98ea7c1104c1e5cbdff88f`.
- `host`: [Default device packaging now starts the compiled radio without WIFI=1; explicit WIFI=0 disables only the radio, and reduced CI packaging does not claim a compiled radio.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-05-default-gpu-wifi.txt)
  Command: <code>ci_kernel.sh default and explicit CI; ci_boot_ufs.sh default/WIFI=0/explicit CI; check-wifi-host.py</code>. Revision: `cc016a5c44c1ed074e98ea7c1104c1e5cbdff88f`.
- `device`: [Both clean-stock-wifid boots returned HTTPS 200 with continued UP status. No-Settings g342 had a canvas-mapping failure and a wrapped early log, so no UI pass is claimed. g343 retained one association/key handshake, zero link loss and three complete Settings screenshots with no fixture or temporary test UI/helper.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-05-wifi-lifecycle.txt)
  Command: <code>cycle.sh out/g342-clean-native/pong-xnu-initial.img g342-clean-native 600; cycle.sh out/g343-clean-settings/pong-xnu-initial.img g343-clean-settings 480</code>. Revision: `959b00b1b81186c40b75b16a1c27c512062a2e1a`.
- `host`: [Three kernel configurations built; actual old timer pass hangs under nested removal, adapted pass handles recursion, cancellation, running rearm, budget and future deadlines. FIFO ordering/full/wrap and existing regressions pass.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-05-wifi-lifecycle.txt)
  Command: <code>check-wifi-host.py --shared Ath12kWifi; ci_kernel.sh Wi-Fi/CI/GPU</code>. Revision: `959b00b1b81186c40b75b16a1c27c512062a2e1a`.
- `device`: [Real service binding and deferred notifications eliminated repeated short-run disconnects. Timer fix passed native radio off/on: two distinct DHCP ACK transactions, two HTTPS 200 responses, cleanup and continued worker progress. g340 failure is retained as the control.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-05-wifi-lifecycle.txt)
  Command: <code>cycle.sh g335-fixed, g337-deferred-events, g340-progress-watch, g341-timer-reentry</code>. Revision: `959b00b1b81186c40b75b16a1c27c512062a2e1a`.
- `device`: [Stored credential reuse and real 64 MiB operation passed. Native automatic join and HTTPS 200 passed; original-wifid/no-Settings/default-128 MiB repeated HTTPS, but periodic disconnects remain.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-04-wifi-settings-and-roaming.txt)
  Command: <code>cycle.sh g312, g314, g331, g332</code>. Revision: `718f73ce424d427c2ecdc757b9c64eb7cd4f3dca`.
- `host`: [Three kernel configurations, loader/UI/helper builds and host regression suites passed. Native metadata staging preserves stock endpoints and rejects other OS builds.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-04-wifi-settings-and-roaming.txt)
  Command: <code>ci_kernel.sh Wi-Fi/CI/GPU; LLVM 18 loader build; UI/helper compile and codesign; check-wifi-host.py on macOS and Ubuntu</code>. Revision: `92ef6d2de5419ce5c5aa8bfe36ab25a9fadeffb7`.
- `device`: [Both frequency directions passed three HTTPS 200 responses and disconnect cleanup without RDDM. Native Settings join independently passed WPA2, DHCP and HTTPS with kernel auto-association disabled.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-04-wifi-settings-and-roaming.txt)
  Command: <code>cycle.sh g304-rate-crossband, g306-rate-2g-to-5g, g309-native-settings-join</code>. Revision: `92ef6d2de5419ce5c5aa8bfe36ab25a9fadeffb7`.
- `host`: [Bounded waits under a busy pump, skb ownership, lease and USB regressions passed. Native interface and firmware-failure cleanup built; host and device findings remain separate.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-04-wifi-native-repair.md)
  Command: <code>ci_kernel.sh CI/GPU/Wi-Fi configs; check-wifi-host.py; wifid plist/cache staging replay; compile/sign UI library</code>. Revision: `fbac25628cfd36365c2850407bc77c3121b36780`.
- `device`: [Local repair snapshots based on the recorded commit: first connection and renewal on 2.4 GHz returned HTTPS 200; cross-band RDDM failed. Native IO80211 binding worked and manager-port lookup errors disappeared; Settings/native join failed. Vdev experiment reverted.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-04-wifi-native-repair.txt)
  Command: <code>cycle.sh g292, g293, g294, g295 (local repair snapshots)</code>. Revision: `3ca641b749e9fbba116f7eebcde349e4f8ce81e5`.
- `device`: [Same-image control: firmware crashed, MHI recovery returned -110 and association failed. Early logs were overwritten; initial fault stage unknown. Deadline returned the phone to Android.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-04-g291-cross-ap.txt)
  Command: <code>cycle.sh out/g291/pong-xnu-initial.img g291-retry 480</code>. Revision: `616bb5eb8d5d622b90c51c06d10486063ecb3bcd`.
- `device`: [Initial connection and requested renewal returned HTTPS 200; disconnect cleanup passed. WPA2 authenticated to a different BSSID, but no DHCP Offer/ACK arrived. Cross-AP networking failed; returned to Android.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-04-g291-cross-ap.txt)
  Command: <code>cycle.sh out/g291/pong-xnu-initial.img g291 480; cycle-resume.sh recovery after interruption</code>. Revision: `616bb5eb8d5d622b90c51c06d10486063ecb3bcd`.
- `device`: [Credential-free boot reached station-ready, scanned 11 networks and returned to Android; no automatic association or public probe.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-04-g290-default-wifi.txt)
  Command: <code>cycle.sh out/g290-default-wifi/pong-xnu-initial.img g290-default-wifi 420</code>. Revision: `ade79e8088f089b7145b9139e410b6115c7ef3ce`.
- `device`: [Default Wi-Fi path passed initial networking, native requested renewal, disconnect cleanup, reconnect and three HTTPS 200 responses.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-04-g290-lifecycle.txt)
  Command: <code>cycle.sh out/g290/pong-xnu-initial.img g290 480</code>. Revision: `ade79e8088f089b7145b9139e410b6115c7ef3ce`.
- `device`: [Existing en0 configuration acquired default route and DNS, native HTTPS 200; compensation released after native configuration recovered. Renewal trigger was not run.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-04-g289-https.txt)
  Command: <code>cycle.sh out/g289/pong-xnu-initial.img g289 460</code>. Revision: `da8e7cbacf1c73f8aff14ba39fed9ea2ebf45d0e`.
- `device`: [Live ACK matched kernel IPv4. After service-state compensation en0 became primary; native HTTPS returned 200 / 577 bytes; returned to Android.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-04-g287-https.txt)
  Command: <code>cycle.sh out/g287/pong-xnu-initial.img g287 420</code>. Revision: `64c4b52a4081802f9f75e5ca2c963f99df623156`.
- `device`: [Live ACK was readable; consistency checks rejected compensation. HTTPS failed.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-04-g286-routing.txt)
  Command: <code>cycle.sh out/g286/pong-xnu-initial.img g286 420</code>. Revision: `c405db767cfc2f21016a0bde10c6559c6d84cd7e`.
- `device`: [Five power rails, association and IPv4 passed. configd had no en0 IPv4 entity and the kernel had no default route.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-04-g285-routing.txt)
  Command: <code>cycle.sh out/g285/pong-xnu-initial.img g285 420</code>. Revision: `3b54df270354f46b9c330622e7a6b238ea5a9faf`.
- `device`: [Real association and IPv4 passed; kernel returned ENETUNREACH. Dynamic-store IPv4 service lacked Router; disk lease did not pass validation.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-04-g283-routing.txt)
  Command: <code>cycle.sh out/g283/pong-xnu-initial.img g283-retry 420</code>. Revision: `cb2667293f5720ef93b5926e1a49df2730513145`.
- `device`: [IPv4 acquired. Experimental ACK-based route/DNS compensation was not applied; HTTPS failed. Returned to Android.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-04-g282-wifi.txt)
  Command: <code>cycle.sh out/g282/pong-xnu-initial.img g282 480</code>. Revision: `9f9423f25e91d26be43476053f49bd7a77f55282`.
- `device`: [Session DHCP service succeeded; ACK contained router/DNS while published service lacked Router.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-04-g281-wifi.txt)
  Command: <code>cycle.sh out/g281/pong-xnu-initial.img g281 480</code>. Revision: `70f56e325df7ea2a9f851d53136784d0461169e7`.
- `device`: [WPA2 and DHCP repeated successfully; four public probes had no primary interface, route or DNS. Returned to Android.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-04-g280-wifi.txt)
  Command: <code>cycle.sh out/g280/pong-xnu-initial.img g280 480</code>. Revision: `0959812c992522b084bfb80a587e888cfd8bee53`.
- `device`: [WPA2 association and IPv4 DHCP lease succeeded; first HTTPS probe failed.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-04-g279-wifi-usb.txt)
  Command: <code>cycle.sh out/g279/pong-xnu-initial.img g279-retry 480</code>. Revision: `333c5defb04af1d5f48fa3c83e912d352869441f`.
- `device`: [Station ready and scan found 15 networks. Fresh UFS klog was 941005 bytes; returned to fastboot after 168 seconds, then Android. Association/DHCP unverified.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-03-g275-wifi.txt)
  Command: <code>cycle.sh out/g275/pong-xnu-initial.img g275 480</code>. Revision: `32ee207bd5b585d79bc25181f69757aefeab9256`.
- `device`: [Returned automatically with 1133944 bytes of fresh UFS klog; TCR2 passed, SCTLR ASIDPNE readback mismatched.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-03-g273-wifi.txt)
  Command: <code>cycle.sh g273; three kernel configurations and register replay</code>. Revision: `0acd5e0f55cf37635fb333f9735ae7592747403e`.
- `device`: [Returned automatically with 1105249 bytes of fresh UFS klog; SMMU/DMA and firmware/QMI passed, WMI\_INIT=-11. Wi-Fi incomplete.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-03-g274-wifi.txt)
  Command: <code>cycle.sh g274; three kernel configurations and register replay</code>. Revision: `239d5403defdec0d9dde3c1cc4d11c5e3b2326bd`.
- `device`: [Temporary boot passed; fastboot return after 107 seconds and 995985 bytes of fresh UFS klog \(deadline\), then Android. Power/PCIe passed, SMMU status=7; Wi-Fi incomplete.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-03-g272-retry-wifi.txt)
  Command: <code>cycle.sh out/g272/pong-xnu-initial.img g272-retry 420 (existing local WIP image)</code>. Revision: `4927a4b459c6a025d12af96da3265b5c74a1458f`.
- `source`: [Device Wi-Fi chipset identification.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-10-28-device-prep.md)
- `host`: [Three old-profile configs built. Images withdrawn because board inputs mismatched; g265/g266 never booted.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>ci_kernel.sh: zizhan_ipados18_wifi_defconfig, pong_ipados18_ci_defconfig, zizhan_ipados18_gpu_defconfig</code>. Revision: `79ae5b1d7b92f621ac549aec80e73e30e404d649`.
- `host`: [Full live-DT profile audit and three builds passed. g267 had one Wi-Fi switch and automatic return; no device boot.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>PONG_WIFI_DTB=&lt;local live DT&gt; ci_kernel.sh (Wi-Fi); ci_kernel.sh CI/GPU; ci_boot_ufs.sh boot-g267</code>. Revision: `ae24f8a89f41fe2864d997ea3b8005fb1824ae89`.
- `host`: [After QMI extended-ID naming fix, all three configs built; g268 command-line and automatic-return checks passed. No device result.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>ci_kernel.sh Wi-Fi/CI/GPU; ci_boot_ufs.sh boot-g268</code>. Revision: `2eab51d14ecc79b3e9b34a4adf65a2b0a81322d8`.
- `host`: [Three builds passed again. Visible, unauthorized, blocked adb and fastboot boot success/failure simulations passed; g268 had no device boot.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>ci_kernel.sh CI/GPU/Wi-Fi; USB tool simulations</code>. Revision: `890ec93c136a23bbc0e857d0879c3119bf945b83`.
- `host`: [213/213 firmware files matched; kernel and final image contained the full package. No high-board-ID file; actual QMI ID was then unknown.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>Parse PWF2 and compare each SHA-256 with local firmware export; inspect embedded g268 package</code>. Revision: `0949ebe471d258965f2ef2ae21b44cd1eda13576`.
- `host`: [Distinguished no log, power failure, post-PCIe ath11k failure, multiple boots and scan. CI/GPU builds passed; no g268 device result.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>wifi-stage.py: five isolated log fixtures and g264 non-Wi-Fi replay; ci_kernel.sh CI/GPU</code>. Revision: `eb2fe973a6611582c6ad31f45d7c8b9389094a6a`.
- `host`: [Three builds passed. g269 command line was 913 bytes with one Wi-Fi switch, screenshots and automatic return; new subsystem log marker and PWF2 embedded. Device absent; no device result.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>ci_kernel.sh CI/GPU/Wi-Fi; ci_boot_ufs.sh boot-g269; inspect command line and firmware package</code>. Revision: `5b695938a42495d517be09d43b3ecaa2cb4eb59c`.
- `host`: [Only last cold-start subsystem values were reported; corrupt values rejected. g264 retained NO\_WIFI\_LOG. CI/GPU builds passed; no g269 device log.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>wifi-stage.py multi-boot/corrupt-value fixtures and g264 replay; ci_kernel.sh CI/GPU</code>. Revision: `2b7966cb95f2572f5b28dee8e8d89e49b384ec1d`.
- `source`: [Original normal-image hold resumes after file-level verification disproved the viewer-based graphics alarm. A default-off native periodic HTTPS witness is host-tested and compiled/signed for a helper-only trial; post-baseline failure stops that probe without changing network configuration. Prepared, installed and device-qualified states remain separate. Natural T1, distinct SSID/subnet and end-of-window HTTPS remain independent qualifications.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-06-overnight.md)
- `device`: [On the original image, a bounded hold returned to Android with live CP17079/17079; the early HTTPS record was overwritten. The helper-only OS trial then recorded 28/28 successful native HTTPS witnesses across 1673.6 seconds, en0 route/DNS valid at each accepted result, no witness/link-loss failures, unchanged lease sequence and three complete late captures. The image was restored and the original live OS SHA256 verified. Natural T1, distinct SSID/subnet and helper-off device behavior remain untested.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-06-overnight.md)
  Command: <code>cycle.sh g386-network-hold; signed g387 helper-only native HTTPS witness</code>. Revision: `6d074ef09e5777cecfa23612e626ce2c3878153e`.
- `source`: [A genuine g384 CS4K storage allocation of 1949696 bytes returned KERN\_NO\_SPACE before initproc and preserved a panic klog; the identical image later booted. This is not attributed to total physical RAM exhaustion and remains an open boot resource limitation. No signature or panic bypass was introduced.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-06-overnight.md)

## cellular {#cellular}

`planned`

### 硬件与依赖

- SM8475 phone with a cellular modem; unlike a Wi-Fi-only board this area is applicable.
- Board-specific modem firmware, EFS/NV, QRTR/QMI, SIM, IPA/QMAP and OS ABI inputs require an audit. Keep identities and device dumps private.

### 配置

- No cellular component is selected or enabled in board.toml; no modem initialization is added by this record.

### 操作步骤

- Read the upstream baseband guide and sibling implementation before selecting a shared component.
- Audit the live board resources and firmware dependencies; isolate read-only transport/identity checks before registration or data-session work.

### 开发经验

- No cellular implementation or device verification has been performed in this repository; a Wi-Fi HTTPS result does not validate modem transport or data.

### 完成条件

- Establish firmware/transport ownership, valid SIM state and network registration.
- Verify IPA/QMAP data sessions, routing and teardown/reset with separate host/device evidence.

### 当前范围

- Modem firmware loading, EFS/NV, SIM, registration, IPA/QMAP and data sessions are not implemented or verified. No IMEI/ICCID or raw modem dump is published.

### 下一步

- Inventory the actual zizhan modem transport, firmware and OS dependencies against the upstream QcomBaseband guide, then choose the first bounded read-only probe.

### 证据

- `source`: [The current upstream record guide lists cellular separately; this modem-equipped phone is planned, not not-applicable.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-04-upstream-ci-audit.md)

## 音频 {#audio}

`planned`

组件: `PongPlatform24`.

### 硬件与依赖

- Two CS35L41 amplifiers at 0x40/0x42. Public zizhan Android DT gives SE15 I2C 0x880000, GPIO56/57 SDA/SCL, GPIO88/118 IRQ and shared GPIO1 reset. Recheck the live phone DT before enabling; Pong uses TFA9873 with different bus/pins/addresses.

### 配置

- pong\_audio=0; without tfa98xx.cnt build an empty amplifier table.

### 操作步骤

- Keep audio off; audit live DT and I2C prerequisites, run an isolated read-only identity probe, then implement CS35L41 initialization and ADSP playback routing.

### 开发经验

- Pong TFA9873 initialization cannot be reused by changing addresses.
- PongAudio.cpp uses SE13 0xa94000, GPIO48/49 and addresses 0x34/0x35, unlike the public zizhan SE15 description.
- GeniI2c supports multi-byte transfers but amplifier wrappers and writes remain TFA9873-specific.

### 完成条件

- Play audible sound through the speakers.

### 当前范围

- No CS35L41 driver. Public extracted DT still needs live-device revalidation; no audio device-boot or playback evidence.

### 下一步

- Verify live SE15 clocks, pins, reset and IRQ, then read CS35L41 identity in an isolated config. Audit tuning/firmware and ADSP routing before staged device tests.

### 证据

- `source`: [Reason audio stays disabled and empty-amplifier-table behavior.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-01-battery.md)
- `source`: [Public extracted Android DT describes SE15, GPIO56/57, CS35L41 addresses, reset and IRQ; live-phone recheck pending.](https://github.com/sm8450-mainline/fdt/blob/3e347601d9e91dd2f1f48e51499823225f7bc0bc/zizhan.dts)
- `source`: [PongAudio.cpp comparison, isolated-probe prerequisites and unverified boundaries.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-03-audio-board-audit.md)

## 电源 {#power}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- Local ADSP /vendor/firmware\_mnt/image/adsp.mdt and b00..b25, merged by mdt2mbn.py into adsp.mbn; not committed.
- UniXNU-sheng ShengBattmgr protocol.

### 配置

- CONFIG\_XNU\_PONG\_POWER=y.
- pong\_adsp=2 starts DSP and battery; 1 maps/investigates only; 0 disables.

### 操作步骤

- PongAdsp loads/authenticates ADSP in the zizhan carveout and reads battery through PMIC GLINK.
- Shift ShengBattmgr Xiaomi property IDs by one after 12; temperature is already in 0.01 C.
- PongRpmh.cpp supplies shared RPMh votes when Wi-Fi is not built.

### 开发经验

- The POWER-02 unattended candidate adds opt-in zizhan\_adsp\_events=1: idle ADSP waits on IPCC/client events without a periodic deadline, while queued sends keep a bounded 1000-ms retry. The production wait template is exercised across event-arrival races on the host; runtime and battery-update qualification remain separate.
- L18 timing@0 and timing@1 each contain 7 off packets with 130 ms total post-waits and 55 on packets with 120 ms waits. One 90-byte on payload exceeds the vendor controller's 64-byte FIFO-store limit. The new program parser/encoder preflights complete off/resume programs and rejects FIFO-only shutdown when resume needs DMA; no panel power executor is enabled.
- g397 query-only device audit passed normal temporary boot/return and fresh klog: PSCI 1.1 via SMC, CPU\_SUSPEND feature raw 3, SYSTEM\_SUSPEND and SET\_SUSPEND\_MODE raw 0, root-domain/owner inventory and one display request observation. No suspend/mode/RTC/display hardware transition was executed; all power contracts remain unqualified.
- g206 agreed with Android sysfs: 100%, 4444 mV, charging 426 mA, 34.40 C, full capacity 3507 mAh, design 4500 mAh and 907 cycles.
- Rename the battery service AppleSmartBattery because PerfPowerServices PLBatteryAgent and powerd health calculation select that class. Publish Serial, BatteryData and MaximumCapacityPercent. Settings Battery Health reported 78% \(3483/4500 mAh\).
- The health spinner follows batteryDataUnavailable: thermalmonitord never publishes com.apple.thermalmonitor.ageAwareMitigationState and powerd lacks Battery Service State.
- USB plug/unplug changes charge state and current direction \(+300/-520 mA, v7\).
- Settings checks MobileGestalt D6/BMDrlb8V3WSiqL8gL+w then AppleAuthCPRelay isTrustedForUI for battery authentication. This battery has no Apple authentication chip; ui\_compat18.c reports the capability false, without inventing genuine-part status.
- The primary L18 panel uses real DCS reads and verified nonzero writes/restoration. CoreBrightness service publication is gated on actual readback and native class readiness; asynchronous DSI transactions retain ownership through completion and quarantine still-active failed DMA.
- POWER-02 now separates lockscreen, display-off, individual-device quiesce and platform suspend, with per-owner drain/resume/rollback contracts. Current custom owners lack a complete paired power transition chain; target-state independent return remains unknown. This is host design, not suspend/resume implementation.
- The complete POWER-02 design covers native lock/screen-off policy, runtime PM, per-CPU/context and shared-domain idle, with SYSTEM\_SUSPEND as a feature-dependent alternative. Read-only Android reports freeze/mem and default s2idle, RTC wake enabled and enabled rail-pc states; no system sleep was performed. Live vendor TCS tuple order/type4 conflicts with existing sleep/active slot assumptions under the mainline binding; matching vendor ownership must be resolved before programming sleep/wake sets. Periodic workers and retained high votes are explicit work, not solved by black pixels or lower CPU frequency.
- Power inventory regression now uses a synthetic FDT rather than a private captured DTB. Seven parser cases cover resource shapes, unresolved IRQs, board identity, missing CPUs and cyclic domains; local full daily-use coverage is 67 cases. These are host-only checks, with no additional sleep/wake qualification.
- The November 9 publication retained the first Linux Daily-use CI failure: GCC rejects mixed enum/integer mock return values under -Wextra. The DSI command test now explicitly returns uint32\_t/unsigned values, preserving fault/completion replay semantics; runtime drivers are unchanged.

### 完成条件

- Status bar and Settings Battery show accurate charge and plug/unplug changes; Battery opens without blocking.

### 当前范围

- Battery Health still spins due to missing management/service state. Usage graphs need long-term collection. Sleep/wake is unsupported.

### 下一步

- Implement thermalmonitord ageAwareMitigationState and powerd Battery Service State from actual services; do not fabricate a normal status in Settings.

### 证据

- `source`: [GCC enum/unsigned portability fix in the actual DSI command mock, with the failed first CI retained and final exact-SHA checks tracked separately; no runtime or device qualification change.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-09-publication.md)
- `source`: [POWER-02 ADSP event candidate passed one normal device boot/return. Actual framebuffer accounting, packet preflight and finite FIFO failure replay remain distinct from panel/SoC power transitions; long DMA requires the real display IOVA owner.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-07-power-unattended.md)
- `source`: [g397 query-only device audit with fresh klog, registry/PSCI/display-request logs and no power-state writes; hardware power contracts remain unqualified.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-07-power-audit.txt)
- `source`: [Sanitized read-only power interface and DT declarations, polling/display/CPU contract gaps and unresolved vendor TCS interpretation. No new power-transition result.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-07-power-design-audit.txt)
- `source`: [POWER-02 complete design and read-only audit only; runtime code, kernel/image, OS installation and sleep qualification unchanged.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/plan/2026-11-07-lockscreen-suspend-design.md)
- `source`: [Host source review and staged restoration contract only; no power transition executed and no new sleep/wake qualification.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/plan/2026-11-07-power-resume-contract.md)
- `device`: [Normal 120/60 Hz trials returned complete screenshots and HTTPS200 with direct CP completion763/763 and665/665. Older wait snapshots do not prove hangs. Actual clean OS/UI/helper and manifest were verified and promoted with retained rollback artifacts, without further phone writes.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-05-display-and-backlight.txt)
  Command: <code>cycle.sh g374-live-fence-control, g375-live-60hz; clean prepared-state promotion</code>. Revision: `9d7afd134e56d14dcdd2d0862f3a18f49427b49a`.
- `device`: [Primary-panel DCS read/write/readback, native service and UI/HID chain passed with restoration. FIFO ownership spans asynchronous transactions; still-busy failed DMA is never reused. No measured panel photometry is claimed.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-05-display-and-backlight.txt)
  Command: <code>cycle.sh g350-read-repeat, g351-backlight-levels, g361-native-packet, g364-hid-thumb</code>. Revision: `88e5106dca99c03b9be1af02ceae5b041480a83d`.
- `source`: [ADSP startup stages 1-13 passed; battery readings agree with Android.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-01-battery.md)

## 镜像组装 {#packaging}

`host-verified`

组件: `PongPlatform24`.

### 硬件与依赖

- xnu-11417.140.69 \(Darwin 24.6.0\) and stock 22H374 restore components.

### 配置

- patches/xnu-ipados18/series.
- PROFILE=zizhan\_ipados18\_gpu; local prelink/userdata inputs documented under migration/ipados18.

### 操作步骤

- ci\_prep.sh prepares dependencies; ci\_kernel.sh builds; ci\_boot\_ufs.sh prelinks and creates the boot image.
- build-xnu-ipados18.sh uses patch --forward in series order to avoid reversing already-applied hunks.

### 开发经验

- After the series is applied, clean xnu-11417.140.69 matches the actual build tree file by file.
- Disable three newer-clang warnings under -Werror; support both Intel and arm64 macOS hosts.
- ADT /chosen requires unique-chip-id and chip-id. Without IOPlatformUUID, gethostuuid blocks and timed/locationd/contextstored/PowerUIAgent lead to a frozen Battery page. build-ipados18-bootimg-local.py supplies a software seed, not an Apple hardware identity.
- fairplayd.A2 exits immediately in this port; launchd KeepAlive retains its port and queued requests have no response. EXCLUDED18 removes it on a full rebuild.
- The packer enforces 1020 command-line bytes. Omit default pong\_ui\_software=0, pong\_software\_ui=0 and pong\_ram\_banks=1 to save about 54 bytes.
- ADT /product udid-version=1 requires SerialNumber, ECID, WifiAddress and BluetoothAddress; disabled Wi-Fi stalls MobileGestalt and Settings ISDefaults. With a /chosen seed, use the stock iPhone17,1 version 2 \(ChipID-ECID\); first Settings screen fell from 6.4 to 1.2 seconds.
- On November 2, fairplayd was restored from pre-g213 OS for Weather diagnosis. g245 recorded 2560 frames, 2453 moving at 72.0 fps and no failed lookups, but respawn persisted. EXCLUDED18 still removes it on full rebuild.
- Read-only inspection found fairplayd cache/plist in current OS and g213, absent in f245. Kernel builds do not change that installed service state; use the same kernel and B1-A-B2 ordering for a device control.
- g279 installed a signed native DHCP helper/job into the 22H374 OS after old-window/block prechecks, then read back blocks against the manifest. The phone launched the service.
- The November 4 compliance audit found that the existing local and macOS build pipelines had not adopted the latest upstream package interface. This round adds the upstream package.sh template and the 22H374 defconfig mapping; template parity and TOML mapping pass.
- The release command is absent from the current local UniXNU checkout \(0fc0fc1\). The available release implementation \(e67a79e\) has no 22H374 profile, and its generic build/pack steps do not select the device's Darwin24 prelink and UFS image scripts; --check therefore cannot pass and a full package workflow is not yet valid.
- Full 22H374 preparation copies stock InterfaceNamer bundle metadata into the overlay with its documented native 30/10-second fallback. The signed UI helper is opt-in; tests use local-only credential files, verified OS delta preflights and readbacks. No fake dynamic-store Quiet state is injected.
- Local build and package defaults select the combined device profile. Runtime GPU/Wi-Fi enablement follows the kernel report; explicit overrides produce a single value per key. Reduced cloud CI remains explicitly selected.
- Panel parameters are selected from the zizhan display JSON. New patches retain bounded VM/signature-cache failure stages without bypassing genuine failures. The power archive receives the actual GPU macro so CPU-only CI and full kernels coordinate the correct DSI owner.
- BASE-01 now records explicit 22H374 service policy and policy hash in build plans/job reports; refresh\_jobs inherits a recorded policy and the legacy default still excludes fairplayd. Isolated stage\_jobs catalogs from matching stock inputs differ only by fairplayd presence. A local APFS/overlay/runtime audit reports the default rebuild mismatch; no complete image rebuild or device behavior is qualified by catalog staging.
- Fixed three missing unified-diff context prefixes in the uncommitted BOOT-01 patch0019; generated C is unchanged. Forward/reverse replay and corrupted-format control pass, as do reduced and repeated full kernel builds. The packaged g395 ADT TSENS bytes match reviewed board JSON; no OS installation occurred.
- On November 8, an isolated OS370 clone removing only the fairplayd launchd job was installed with full-window readback. With the same kernel/loader/UI/helper, v23r5 removed the captured locationd MIG1203 stall, restored its main run loop, and started weatherd on demand; a location-settings prompt was observed by the user and in the partial screenshot. Weather remained --; no permission grant, GPS fix, or weather data success was demonstrated.

### 完成条件

- Build a bootable image reproducibly from a published device revision and record host and device results separately.

### 当前范围

- Apple images, firmware and ABI binaries are prepared locally.
- The generic job-restore.sh had static checking only. The installed diagnostic candidate now follows the default fairplayd exclusion, while canonical OS370 still retains the job. The first same-runtime exclusion trial unblocked locationd; no B1-A-B2 re-add control or default promotion has completed.
- scripts/package.sh now matches the upstream template and board.toml maps 22H374 to the GPU defconfig, but package.yml is not present and upstream release cannot select this Darwin24 profile or its UFS-specific build chain. Current CI builds the reduced kernel by default, not a clean end-to-end release or a full Wi-Fi/GPU image.

### 下一步

- Add a supported configuration-driven Darwin24 kernel/prelink/payload/boot recipe to the upstream release interface; then validate 22H374 --check, wire local UEFI/Apple inputs and package.yml, and complete a full local package before claiming adoption.
- Inspect native Location Services state and the remaining weatherd/fairplay dependencies without granting permissions or fabricating replies; retain the same-runtime re-add control and Battery regression before any default promotion.

### 证据

- `device`: [Fresh deadline log and Android return passed. locationd main moved from 1000/1000 dispatch queue waits to its normal CF run loop; the old captured MIG1203 stack disappeared. weatherd spawned on Mach demand. User observed a location-settings prompt and tapped Cancel; partial screenshot retained the modal and Beijing --. Weather/GPS/grant and full-frame integrity remain unqualified.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-08-weather-authorization.md)
  Command: <code>OS370 isolated fairplayd job removal; OS-only delta install and full live readback; cycle.sh out/weather-auth-v22/pong-xnu-initial.img weather-fairplay-v23r5 450; gsym.py locationd</code>. Revision: `fb1b927d1c741f1958ee7e1f62ff5b0261bac712`.
- `source`: [POWER-02 patch0021 is applied after the existing patch chain; its controlled owner header is copied into the generated XNU tree without editing reference sources. Actual patch-chain host replay passes; early failed base-patch attempt is retained as a negative result.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-07-power-unattended.md)
- `source`: [Host TSENS ADT wire validation, actual final package identity, patch-format regression, full/reduced/repeated default builds; no new installed OS or release/CI claim.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-07-tsens-readonly.md)
- `source`: [Actual job-builder regression and read-only stock-source staging under legacy versus explicit OS370 service-presence policies; source mounts detached, images/phone unchanged.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-06-daily-use-development.md)
- `device`: [Normal 120/60 Hz trials returned complete screenshots and HTTPS200 with direct CP completion763/763 and665/665. Older wait snapshots do not prove hangs. Actual clean OS/UI/helper and manifest were verified and promoted with retained rollback artifacts, without further phone writes.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-05-display-and-backlight.txt)
  Command: <code>cycle.sh g374-live-fence-control, g375-live-60hz; clean prepared-state promotion</code>. Revision: `9d7afd134e56d14dcdd2d0862f3a18f49427b49a`.
- `host`: [Board version2 ADT and new patch series built; matched actual UI/helper and stock-wifid clean OS verified. The signature-cache stage patch records real errors and does not bypass validation or panic.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-05-display-and-backlight.txt)
  Command: <code>ci_kernel.sh default/CI; native UI/helper compile and strict signature; verify-native-os.py</code>. Revision: `88e5106dca99c03b9be1af02ceae5b041480a83d`.
- `device`: [Combined device defaults without DEFCONFIG/PROFILE/WIFI overrides passed native automatic association, keys, DHCP and HTTPS 200. Zero link loss or canvas-mapping errors; three complete Settings screenshots, deadline return and fresh UFS log.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-05-default-gpu-wifi.txt)
  Command: <code>cycle.sh out/g344-default-combined/pong-xnu-initial.img g344-default-combined 480</code>. Revision: `cc016a5c44c1ed074e98ea7c1104c1e5cbdff88f`.
- `host`: [Local build and package defaults select the combined device profile. Runtime GPU/Wi-Fi enablement follows the kernel report; explicit overrides produce a single value per key. Reduced cloud CI remains explicitly selected.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-05-default-gpu-wifi.txt)
  Command: <code>ci_kernel.sh default and explicit CI; ci_boot_ufs.sh default/WIFI=0/explicit CI; check-wifi-host.py</code>. Revision: `cc016a5c44c1ed074e98ea7c1104c1e5cbdff88f`.
- `host`: [Root and overlay staging passed with preserved stock metadata and wifid services. UI/helper built and signed; OS-only device deltas were checked before and after writing.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-04-wifi-settings-and-roaming.txt)
  Command: <code>check-wifi-host.py; compile/sign native UI and wifi-service18; actual OS delta manifest/hash preflight and readback</code>. Revision: `92ef6d2de5419ce5c5aa8bfe36ab25a9fadeffb7`.
- `source`: [Build-chain description.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-10-29-xnu-bringup.md)
- `host`: [A clean Apple-silicon Mac Studio build \(Xcode 26.6.0\) produced an 18321080-byte DEVELOPMENT\_ARM64\_PONG kernel with the same zizhan boot-argument strings as device trials.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/host-build-zizhan_ipados18_gpu.txt)
  Command: <code>ZIZHAN_SRC=&lt;work dir&gt; ci_prep.sh &amp;&amp; DEFCONFIG=zizhan_ipados18_gpu_defconfig JOBS=10 ci_kernel.sh</code>. Revision: `1ec1190f4e3467a36a7a7402bc766dfdf688adf1`.
- `source`: [Installed-image fairplayd restoration is distinguished from EXCLUDED18 full-rebuild policy; no additional device-verified status.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-02-gpu-astc-and-fairplayd.md)
- `source`: [Local Wi-Fi inputs, three kernel builds and experimental-image packaging; no device result at that historical stage.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-03-wifi-bringup.md)
- `host`: [Current/g213 contained fairplayd; f245 did not. No-device, backup-conflict and missing-label paths refused safely. CI/GPU builds passed; device behavior unverified.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-03-fairplayd-baseline.md)
  Command: <code>Read-only mount current/g213/f245 OS; jobs-refresh.sh failure injection; ci_kernel.sh CI/GPU</code>. Revision: `06d28dbf2c30652b63ab3f24be6664fd790d275f`.
- `source`: [Current-upstream compliance audit identifies the unified packaging interface as pending; existing build evidence remains scoped to the recorded pipeline.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-04-upstream-ci-audit.md)

## 诊断 {#diagnostics}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- ramoops at 0x85200000, logfs and USB adb/fastboot.

### 配置

- pong\_autoreset=&lt;seconds&gt; \(default 300\), pong\_autoreset\_sb.
- pong\_klog\_4k copies kernel logs into a fixed UFS file.
- pong\_gtrace, pong\_gtrace\_delay, pong\_gtrace\_ib and touch\_lat provide timed per-frame traces.

### 操作步骤

- cycle.sh temporarily boots, waits for watchdog fastboot return, uses RamoopsDump to write logfs, returns to Android and pulls logs.
- Panic, a three-second power-key hold and deadline reset all return to fastboot while retaining DRAM logs.

### 开发经验

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
- New display host regression checks actual brightness-helper initialization/forwarding and concurrent DSI ownership without hardware. Frame-latency analysis reports retained matches and sample counts; failed hypotheses and genuine shared-cache ENOMEM panic remain evidence, not success.
- BOOT-01 adds failure-path kernel\_map total/free/largest-space diagnostics only; both reduced CI and full default kernels built successfully. g393 reached the autoreset deadline, returned fresh klog and Android, but did not reproduce the CS4K allocation failure; no root cause or repair is claimed.
- Daily-use host regressions cover thermal input errors/units/FDT references, preserved partial captures, local service-policy drift and actual catalog generation. Android captures use bounded non-PTY shell stdin; raw data stays outside the public repository. Daily-use host workflow is included in the 11-07 publication; cloud results are recorded separately from local checks. Its first cloud run failed because power-inventory tests required a private local DTB. A synthetic FDT now supplies the same parser shapes without private inputs, with foreign-board, missing-CPU and domain-cycle rejection controls; isolated replay and all 67 local daily-use tests pass. See docs/progress/2026-11-07-publication.md for exact-SHA CI results.
- 11-07 daily-use host runner passes 34 cases, including exhaustive TSENS signed/invalid decoding under sanitizers, gated finite reads, identity-ranges evidence, ADT resources and actual BOOT-01 patch roundtrip/negative control. g395 temperature SKIP and the changed g396 32-sensor PASS are separately retained. g396 original supervisor FAIL at cycle rc0 was caused by an immediate Android-completion check; a bounded follow-up witnessed boot\_completed=1 46.224 seconds later. The original result is not overwritten.
- Post-g396 cycle.sh now preserves logs then requires a bounded Android-ready witness \(target product and boot\_completed=1\), instead of equating ADB visibility with framework readiness. Six mock race/timeout/identity cases and a current-device read-only invocation pass; final daily-use host count is 40. The later g397 query-only cycle passed the integrated bounded Android-completion witness; g396 original supervisor FAIL is retained.
- POWER-02 research reviewed native XNU, 18 fixed Linux primary files, saved live FDT and bounded Android read-only interface/CPU inventory. An initial stdin transfer timed out and is recorded as input failure; narrow direct reads succeeded. No suspend/alarm/cpuidle write, reboot or kernel rebuild was requested. Acceptance requires functional recovery, real device/SoC residency and matched energy measurements; original unsolved hardware limits remain visible.
- The November 9 direct-fastboot Weather trial retained both the empty 167-byte ramoops and a fresh 2111718-byte pinned deadline copy. Native Location Services URL navigation was accepted and Preferences spawned; the black image was captured on the first frame because the hardware absolute clock was already 579 seconds, beyond pong\_shot=150. This is early capture, not proof of Settings rendering failure.
- The November 9 publication retained the first Linux Daily-use CI failure: GCC rejects mixed enum/integer mock return values under -Wextra. The DSI command test now explicitly returns uint32\_t/unsigned values, preserving fault/completion replay semantics; runtime drivers are unchanged.

### 完成条件

- Every trial automatically returns to Android and yields fresh complete logs.

### 当前范围

- pong\_shot currently compares a requested second count with the hardware absolute clock rather than a per-boot relative origin. A long fastboot stay can trigger it on the first frame, before requested UI content. A second frame-relative interval is prepared as a diagnostic compensation; it has not yet been device-verified. The same trial failed all Wi-Fi DMA arena budgets, so it cannot qualify Weather networking.
- Direct USB-C can still fail enumeration and lacks supported host-port probing. Rear USB-A is the verified path. Port-state bits do not prove VBUS power-off; prefer current-trial UFS klog over corrupt ramoops.

### 下一步

- Use rear USB-A for unattended trials; retry only once for an explicit USB write failure during transfer. Follow the actually triggered checks at the published SHA; run cloud kernel builds manually for staged releases or toolchain/build changes while retaining both local kernel configurations. BOOT-01 awaits a naturally occurring CS4K allocation failure to collect map free-space diagnostics; do not manufacture memory exhaustion or repeat g393 unchanged.

### 证据

- `source`: [GCC enum/unsigned portability fix in the actual DSI command mock, with the failed first CI retained and final exact-SHA checks tracked separately; no runtime or device qualification change.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-09-publication.md)
- `device`: [Direct temporary boot and independent pinned-log collection returned Android. Preferences navigation accepted=1 with real spawn; weatherd sampled dispatch\_sigsuspend/workqueue. Image timing preceded page launch, so location-switch state is SKIP. Wi-Fi arena failed, so service networking is not qualified. The two-time screenshot candidate never booted due NO\_FASTBOOT.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-08-weather-authorization.md)
  Command: <code>fastboot-boot.sh out/weather-location-v24b/pong-xnu-initial.img; cycle-resume.sh; klog.py read; round-report.py; gsym.py weatherd</code>. Revision: `a92bb6c25b06c1580ea978bb27129872ccdca7c3`.
- `source`: [POWER-02 host runner includes actual framebuffer-patch concurrent accounting, DSI FIFO register replay and panel/ADSP cases. Workflow path filters cover these exact inputs. No observation/model success is promoted to sleep or wake completion.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-07-power-unattended.md)
- `source`: [CI-01 keeps record checks automatic, scopes host regressions to subsystem and shared inputs, and makes cloud kernel and disk diagnostics separate manual tasks. Local dual-configuration kernel validation remains required; no device capability changes.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-07-ci-efficiency.md)
- `source`: [POWER-02 complete design and read-only audit only; runtime code, kernel/image, OS installation and sleep qualification unchanged.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/plan/2026-11-07-lockscreen-suspend-design.md)
- `source`: [g395 SKIP versus g396 sensor PASS, original automatic supervisor FAIL versus separate 120-second-bounded Android completion PASS. Both launchd tasks/locks were cleaned; final Android state was rechecked.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-07-tsens-readonly.txt)
- `source`: [Host validation, g395 SKIP, corrected g396 32 valid readings and independently reconciled Android return. No thermal-control, freshness or daily-use promotion.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-07-tsens-readonly.md)
- `source`: [Initial 22-case host coverage and failed capture/transport controls are retained; final 64-case daily-use runner passed locally. See the 11-07 publication record for exact-SHA cloud results.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-06-daily-use-development.md)
- `device`: [Normal 120/60 Hz trials returned complete screenshots and HTTPS200 with direct CP completion763/763 and665/665. Older wait snapshots do not prove hangs. Actual clean OS/UI/helper and manifest were verified and promoted with retained rollback artifacts, without further phone writes.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-05-display-and-backlight.txt)
  Command: <code>cycle.sh g374-live-fence-control, g375-live-60hz; clean prepared-state promotion</code>. Revision: `9d7afd134e56d14dcdd2d0862f3a18f49427b49a`.
- `device`: [Legacy wait snapshot 763/762 differed from direct CP completion763/763 at deadline, with original ring protocol unchanged. Corrected report distinguishes old waits from live hardware completion; three complete screenshots and HTTPS passed, no actual stale-fence watch fired.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-05-display-and-backlight.txt)
  Command: <code>cycle.sh g372-stall-watch, g374-live-fence-control</code>. Revision: `9d7afd134e56d14dcdd2d0862f3a18f49427b49a`.
- `host`: [Actual helper extraction and concurrent DSI ownership replay pass. Native failure handlers preserve fatal signals; timestamp analysis reports only retained matching samples. A fourth display host workflow runs without private inputs.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-05-display-and-backlight.txt)
  Command: <code>check-display-host.py; check-wifi-host.py; frame-latency.py</code>. Revision: `88e5106dca99c03b9be1af02ceae5b041480a83d`.
- `device`: [Combined device defaults without DEFCONFIG/PROFILE/WIFI overrides passed native automatic association, keys, DHCP and HTTPS 200. Zero link loss or canvas-mapping errors; three complete Settings screenshots, deadline return and fresh UFS log.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-05-default-gpu-wifi.txt)
  Command: <code>cycle.sh out/g344-default-combined/pong-xnu-initial.img g344-default-combined 480</code>. Revision: `cc016a5c44c1ed074e98ea7c1104c1e5cbdff88f`.
- `host`: [Default and radio-off package paths were run with the system bash, including unset PROFILE/WIFI; no empty-array nounset failure remains. Device evidence is collected from an actual default package with automatic return.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-05-default-gpu-wifi.txt)
  Command: <code>ci_kernel.sh default and explicit CI; ci_boot_ufs.sh default/WIFI=0/explicit CI; check-wifi-host.py</code>. Revision: `cc016a5c44c1ed074e98ea7c1104c1e5cbdff88f`.
- `host`: [Actual original/adapted timer traversal replay plus notification FIFO, SMMU, WMI, DHCP, staging and USB regressions passed; no phone or private input needed.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-05-wifi-lifecycle.txt)
  Command: <code>check-wifi-host.py --shared Ath12kWifi</code>. Revision: `959b00b1b81186c40b75b16a1c27c512062a2e1a`.
- `device`: [Busy worker and unchanged progress generation localized the failed control; fixed kernel completed native off/on, independent DHCP/HTTPS/cleanup, full screenshots and deadline return with a fresh UFS log.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-05-wifi-lifecycle.txt)
  Command: <code>cycle.sh g339-kernel-sample, g340-progress-watch, g341-timer-reentry; decode-shots.sh</code>. Revision: `959b00b1b81186c40b75b16a1c27c512062a2e1a`.
- `device`: [Native service wait chain and actual Settings controls were observed. g307/g308 UI deadlines were failures; g309 native Join produced an actual association and HTTPS 200. Complete and incomplete screenshot extents are kept distinct.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-04-wifi-settings-and-roaming.txt)
  Command: <code>gesture sampler gs_proc=SpringBoard/wifid/configd; cycle.sh g307-g309; decode-shots.sh</code>. Revision: `92ef6d2de5419ce5c5aa8bfe36ab25a9fadeffb7`.
- `device`: [Ten full mode transitions passed; after port settling the 100168 KB image sent once and booted.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/evidence/2026-11-04-g279-wifi-usb.txt)
  Command: <code>adb reboot bootloader / fastboot getvar product / fastboot reboot x10; usbkick.sh kick + g279-usba-settle</code>. Revision: `3f93d0cd7ee552fd580003abcf569984d9cc3373`.
- `source`: [Unattended-loop design and trial history.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-10-30-root-and-autoloop.md)
- `source`: [Four reset/return path fixes.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-01-zero-copy-and-return-paths.md)
- `source`: [Sanitized Mac clone workflow, diagnostic defaults and verification boundaries; retired old-host sync instructions.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/CLAUDE.md)
- `source`: [USB absence prevented g265 boot. Six-second fastboot probing and explicit-image waiting passed host fixtures; device loop recovery was then pending.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-03-wifi-bringup.md)
- `host`: [Failed starts no longer report booted; three configs built. Phone absent, no device trial.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>adb-visible.sh and fastboot-boot.sh fixtures; CI/GPU/Wi-Fi kernel builds</code>. Revision: `890ec93c136a23bbc0e857d0879c3119bf945b83`.
- `host`: [launchd owned the waiter and logs had heartbeats. Phone still absent; no device logs/screenshots.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>launchctl submit g268 when-back; launchctl list and log inspection</code>. Revision: `5eaa262d46cdb2c3d7a56de28805d57cea548185`.
- `host`: [Export failure, partial pull and empty files removed stale copies and failed. Success retained fresh data. Three configs built; device unverified.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>pull-logfs.sh four failure fixtures; ci_kernel.sh CI/GPU/Wi-Fi</code>. Revision: `0a03bab9a4876f1490e453559a24244ffca76958`.
- `host`: [g264 replay decoded six PNGs; a new same-name log without screenshots removed old PNGs. CI/GPU builds passed; g268 not booted.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>decode-shots.sh g264 and no-screenshot replay; ci_kernel.sh CI/GPU</code>. Revision: `bcfaddf0e1ed31bed1ab99a29e4854e144d01801`.
- `host`: [No marker or mismatched marker selected ramoops; matching current marker selected klog. Failed boot left no success marker. CI/GPU builds passed; phone absent.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>cycle.sh/cycle-resume.sh four klog-marker fixtures; ci_kernel.sh CI/GPU</code>. Revision: `2f1f10aea4b3d65691a7e0cd72c6f79d2623928a`.
- `host`: [Absent phone, adb failure/timeout and missing image failed promptly. Missing image was rejected before device actions; nonzero fastboot did not count as visible. CI/GPU builds passed; g268 had no device result.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>boot.sh/fastboot-visible.sh isolated failure fixtures; ci_kernel.sh CI/GPU</code>. Revision: `1a2ec083bab2242f0da0247f17eae02104796491`.
- `host`: [Export/pull failure, timeout and empty outputs removed stale/partial images; success retained fresh data. CI/GPU builds passed; no device logs/screenshots.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>pull-logfs.sh six failure fixtures; ci_kernel.sh CI/GPU</code>. Revision: `ee84c10b22da2f6bbf1382de3bac1874c15a2b52`.
- `source`: [Audit of checker version, push/PR comparison bases, public catalog revision and build-CI scope.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-04-upstream-ci-audit.md)
- `source`: [Idle phase analysis now reports the same retained gesture cohort and its actual GPU trace overlap. Historical g363/g365 idle samples have no overlap with their GPU traces; no first-frame optimization is claimed. Host replay covers missing gestures, invalid frames and nonoverlapping windows.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-06-overnight.md)
- `device`: [One full-profile temporary boot reached deadline autoreset after 228 s, retrieved 1,830,726 bytes of fresh klog and returned to Android. No panic or CS4K allocation failure; new map summary did not execute. BOOT-01 root cause remains unverified; no same-condition retry.](https://github.com/qiumochen/UniXNU-zizhan/blob/034a0b0037b28f4ff4e46703cbd4d9bb75db25e5/docs/progress/2026-11-06-boot-release-followup.md)
  Command: <code>cycle.sh out/boot-g393-boot-map/pong-xnu-initial.img g393-boot-map 420; fresh UFS klog</code>. Revision: `6d074ef09e5777cecfa23612e626ce2c3878153e`.

</div>
