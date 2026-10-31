# Redmi K80（zorn）

[kerrinz/UniXNU-zorn](https://github.com/kerrinz/UniXNU-zorn)

<div v-pre>

Redmi K80: owner-confirmed desktop/basic touch, eight-core checks, retained8GiB Data and dim64. CPU1 narrow root publication has bounded controls; intermittent GUI stalls and long-term stability remain unresolved. Format2 host migration is separate from historical device qualification.

源记录: [porting.toml](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/porting.toml), `e5b5706023dbec02c20d7ec41df0e39e0e235636`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `implemented` |
| [固件与启动](#firmware) | `implemented` |
| [CPU 与中断](#cpu) | `implemented` |
| [内存与 DMA](#memory) | `implemented` |
| [存储与根卷](#storage) | `implemented` |
| [显示](#display) | `implemented` |
| [输入](#input) | `implemented` |
| [GPU](#gpu) | `planned` |
| [网络](#network) | `planned` |
| [音频](#audio) | `planned` |
| [电源](#power) | `implemented` |
| [镜像组装](#packaging) | `implemented` |
| [诊断](#diagnostics) | `implemented` |

## 配置 {#configuration}

`implemented`

### 硬件与依赖

- K80 / SM8650-AB; iPad7,1 / j120ap, iPadOS17.7.11 /21H461, XNU d8b80295118ef25ac3a784134bcf95cd8e88109f; source-pins.json and unixnu.lock bind the prepared dependencies.

### 配置

- Root board schema2; record schema1. ARM64, tracked board-local SoC slice, OS and device layers; zorn\_union\_defconfig and explicit complete patch/archive arrays.

### 操作步骤

- Resolve with unixnu status --json in a separate output root; validate this record and compile dts/zorn.dts before building a new format2 image.

### 开发经验

- README was not the catalog ingestion source: the scanner selects format2 from root board.toml, then validates porting.toml. The old root was format1 even though the record checker passed.

### 完成条件

- Identity, selected components, source pins, configuration fragments, patch order and board package match the intended build route.

### 当前范围

- This migration checks configuration/DTS/tree on the host; full native kernel/payload equivalence through the new output layout is not qualified. Historical device runs remain attached to their original manifests.

### 下一步

- Audit native recipes for format2 output paths before a complete format2 build; retain the fixed legacy diagnostic entry and all old archives.

### 证据

- `source`: [Root board now uses schema2 with four profiles,9 components and explicit157-patch order. The retained diagnostic board is SHA-pinned; host migration checks do not qualify a new native kernel or device run.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/repository-format.md)
- `source`: [Format2 four-layer/9-component/157-patch resolution, DTS/ADT/tree, official catalog metadata simulation and fixed legacy-selection host checks passed. Source/record files remain uncommitted; this is not a new native kernel or phone result.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/format2-documentation-sync-2026-10-30.json)

## 固件与启动 {#firmware}

`implemented`

组件: `DarwinBoot`.

### 硬件与依赖

- uefi-zorn board package; existing Mu-Silicium/EDKII and giulia SM8650 DXE inputs; GOP and PSCI SMC handoff.

### 配置

- FD base0xA7100000/size0x300000; shim window0xA8000000..0xB8000000; mailbox0xA7601000; menu countdown5s.

### 操作步骤

- Stage the board package, verify FD/module input manifests and use the guarded device packer; each device observation requires independent watchdog and bounded recovery.

### 开发经验

- UEFI menu and DarwinBoot handoff reach the recorded kernel. Existing touch power/clock handoff supports the FT3683 kernel path. Latest CPU/display trials reused the bound FD.

### 完成条件

- Firmware, menu, sidecars, memory window and actual kernel agree, and fresh recovery evidence is bound to the run.

### 当前范围

- The board repository is not the full Mu-Silicium tree. Vendor DXE inputs remain proprietary; the exact hardware reset source was not separately established.

### 下一步

- Preserve the known FD and touch handoff while validating any future firmware change separately.

### 证据

- `source`: [Archived UEFI touch power/clock handoff supports the FT3683 kernel communication path; this update reused the recorded FD and made no firmware build.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/touch-power-handoff-result.json)

## CPU 与中断 {#cpu}

`implemented`

组件: `ArmCpu`, `ArmDTPlatform`.

### 硬件与依赖

- Actual per-core MIDR/MPIDR, PSCI CPU\_ON, GIC,19.2MHz timer, IPIs and original XNU startup interfaces; all8 core gates and9 mapping rounds.

### 配置

- Eight-core debug builds default to publication1, other profiles0; explicit0 remains a diagnostic control. Original2s gate and all preflight checks remain.

### 操作步骤

- Independently assemble current start.s, compare the complete object SHA, audit final code, and bind boot/kernel/inputs/fresh log before interpreting a run.

### 开发经验

- Identical75b9ca39 kernel:0-fail/1-pass/0-fail/1-pass. With0 the late MRS TTBR1 was0; with1 it equaled CPU0 pre-start/final root and all8 cores/9 mapping rounds passed. The change cleans the single cache line containing cpu\_ttep,8bytes, without writing root/page tables.
- Two uninstrumented layouts16KiB apart passed preflight; e700 had2 lock-screen runs and936 had1. Early source-slot word4 was0 even on success and is not the actual MMU-off load value. The old5b uninstrumented claim was withdrawn because start.o was stale.
- c50 final capture had status0 on all8 cores in both epochs and USER/SYSTEM cumulative accounting increased on every core.

### 完成条件

- Per-core identity/timer/IPI/bound work and mapping cleanup pass; startup failures remain preserved and stress/long-term stability are tested separately.

### 当前范围

- The narrow publication evidence does not explain every historical GUI stall. a889 passed CPU/Data/dim64 but remained on the Apple logo. Accounting is cumulative and serial, not simultaneous utilization, idle%, MHz or FPS.

### 下一步

- Preserve the bounded fix and original gates; do not repeat completed controls or add CPU/GUI probes without new direction.

### 证据

- `source`: [Archived identical75b9ca39-kernel controls:0-fail/1-pass/0-fail/1-pass, with late TTBR1=0 versus the CPU0 root; original gates unchanged.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/cpu1-root-publication-controlled-2026-10-30.json)
- `source`: [Archived normal GUI observations:2 e700 runs and1 alternate936 layout, with all8 core gates, retained Data, dim64, fresh logs and camera lock-screen frames.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/cpu1-root-publication-gui-2026-10-30.json)
- `source`: [Archived a889900-second failure: CPU/Data/dim64 passed, but120/720-second camera frames remained on the Apple logo. GUI qualification failed and is preserved.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/cpu1-root-publication-stability-2026-10-30.json)
- `source`: [Archived25a same-full-kernel900-second lock-screen observation passed; this excludes the budget as a sufficient cause, not metadata/Data/timing causation.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/gui-budget-same-kernel-2026-10-30.json)
- `source`: [Archived single c50 trial recovered in395s;255 inputs/77 archive files and distinct log matched. Lock screen/all8/Data/dim64 passed and every core had USER/SYSTEM accounting progress; no performance/root-cause qualification.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/cpu-active-trial-2026-10-30.json)

## 内存与 DMA {#memory}

`implemented`

### 硬件与依赖

- Nominal12GiB SKU; actual UEFI memory ownership,4KiB page tables, PAN, DMA constraints and reserved regions.

### 配置

- Qualified debug profile uses8192MiB. The256MiB decompression window is separate from XNU-owned RAM. The new DTS nominal map is not qualification of all12GiB.

### 操作步骤

- Check reserved regions, owned allocation, page tables and UFS DMA separately; use bound mapping/cleanup results.

### 开发经验

- An8GiB window reached lock screen/desktop. Original VM-map initialization and audited cross-core mapping paths are retained.

### 完成条件

- No region overlap or DMA escape, with repeated allocation/free, mapping and stress/error-path evidence.

### 当前范围

- Full12GiB, long-term pressure and every historical lock/pmap/exec compatibility change remain unqualified.

### 下一步

- Audit the migrated hardware description and reserved regions before any new memory-window qualification; do not enlarge the tested window or clear locks.

### 证据

- `source`: [Board memory/VM-map investigation and compatibility limits are retained; the8GiB desktop result does not qualify the full nominal12GiB map.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/review-2026-10-28-official-houji.md)

## 存储与根卷 {#storage}

`implemented`

组件: `VerifiedRoot`, `RamBlock`, `AppleKeyStoreState`, `SoftwareAES`.

### 硬件与依赖

- Actual UFS capacity/GPT evidence, SHNGROOT manifest and owner policy, original APFS/IOStorageFamily, immutable seed and retained Data marker.

### 配置

- OS/SystemOS read-only. Existing Data window:userdata-relative192GiB,2097217 blocks of4096B; original UUID C7D77FF3-6437-4C4A-8E05-E8E239AC1641/cookie2dde8229.

### 操作步骤

- Verify window/seed/marker and reject out-of-range access; preserve existing initialization and observe APFS mount and cross-boot retention.

### 开发经验

- The8GiB UFS-backed Data volume persisted across the recorded desktop and later lock-screen boots; it does not require8GiB of dense RAM. c50 retained the same UUID/cookie with zero RAM/Data errors.

### 完成条件

- Read-only system identity, bounded Data reads/writes, retained metadata and refusal/recovery errors remain traceable.

### 当前范围

- No Android dual boot, automatic reset or window enlargement. Power-loss integrity, endurance and sustained storage stress are not qualified. board.toml userdata coordinates describe capacity-relative legacy input, not absolute GPT LBAs.

### 下一步

- Preserve the existing window and seed; require separate evidence for long-term consistency rather than reinitializing Data.

### 证据

- `source`: [Archived8GiB UFS-backed Data mount/retention preserved the original UUID/cookie without RAM/Data errors. The older unresponsive touch result is retained.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/data8-retained-touch-result.json)
- `source`: [Archived single c50 trial recovered in395s;255 inputs/77 archive files and distinct log matched. Lock screen/all8/Data/dim64 passed and every core had USER/SYSTEM accounting progress; no performance/root-cause qualification.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/cpu-active-trial-2026-10-30.json)

## 显示 {#display}

`implemented`

组件: `GopFramebuffer`.

### 硬件与依赖

- GOP framebuffer0xFC400000,1440x3200,5760row bytes,32bpp; O11 DSI panel and DCS0x51/0x52.

### 配置

- CPU presentation/display-mode3; brightness-mode3 fixes XNU panel value64 and reads it back. Optional v19 retirement/vsync observation retains old log fields.

### 操作步骤

- Bind actual linked display objects, menu and fresh log; qualify screen appearance independently of transfer counters.

### 开发经验

- Brightness307-&gt;64 was read back. Two6aea lock-screen captures had accepted/transfer/retired9/9/9 and8/8/8; c50 had8/8/8, reject0/status0. Independent camera frames showed lock screen.
- Type5 registration/send queue offsets agree. At60Hz, properties0 does not mean no query; healthy lock screens also had started1 and zero observed sender callbacks.

### 完成条件

- Correct stride/pixels, observed system output and bounded brightness readback; continuous presentation and recovery require separate tests.

### 当前范围

- Single camera frames do not qualify the full observation window. Equal counters do not prove per-request pairing; independent relaxed timestamps are not consistent event pairs. Value64 is not calibrated nits/percent.

### 下一步

- Keep CPU presentation and brightness baseline; preserve unresolved Apple-logo evidence without changing queues or forcing notifications.

### 证据

- `source`: [Archived DCS307-to64 transition and fresh64 readback; this is a register value rather than calibrated luminance or a system brightness-slider implementation.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/brightness-dim-result.json)
- `source`: [Archived second6aea bounded run recovered with a camera lock screen and v19 accepted/transfer/retired8/8/8; first run9/9/9 remains separate.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/display-progress-repeat-2026-10-30.json)
- `source`: [Source/final-link audit found matching type5 queue offset5592;60Hz property counters do not prove client registration, receipt or GUI-stall causation.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/display-notification-contract-2026-10-30.json)

## 输入 {#input}

`implemented`

### 硬件与依赖

- FT3683/firmware35,40TXx18RX matrix; existing power/GPIO SPI path and original IOHIDFamily parsing ABI.

### 配置

- Retain touch-handoff/runtime/edges/kernel-parser/trace/fast-poll and the qualified portrait Y direction.

### 操作步骤

- Verify frame CRC, matrix/baseline, IDs and releases; qualify owner-visible taps/swipes separately from pre-HID traces.

### 开发经验

- 42f3 owner confirmed desktop, unlock and icon taps. The second3a run recorded independent IDs0/1 for5188ms with normal release,2219 good frames and55 HID submissions without errors.

### 完成条件

- Single-touch hit/release and gestures pass; system multi-touch, calibration and long-run responsiveness are distinct qualifications.

### 当前范围

- GPIO polling is not proof of60/120Hz input. Two sensor IDs do not prove system pinch/zoom; physical keys, pixel calibration and complex gestures are unqualified.

### 下一步

- Preserve usable touch; optimization and additional gesture qualification remain deferred.

### 证据

- `source`: [Archived42f3 desktop/unlock/icon-tap owner confirmation is bound to boot/kernel/fresh log and124 inputs; no new device test is asserted here.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/touch-desktop-fast-qualified.json)
- `source`: [Archived second3a desktop run recorded2219 good frames,55 HID submissions without errors, and independent IDs0/1 for5188ms with release; system multi-touch remains unqualified.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/qualified-source-repeat-two-contacts.json)

## GPU {#gpu}

`planned`

### 硬件与依赖

- Board-specific firmware, memory/security ownership and frontend ABI require separate qualification.

### 配置

- This publication synchronization excludes GPU development progress and retains CPU presentation.

### 操作步骤

- Keep GPU work and its hardware qualification in a separate update.

### 开发经验

- A CPU-rendered desktop does not establish hardware graphics acceleration.

### 完成条件

- Firmware, isolated mappings, submission, fences, recovery and actual rendering have matching device evidence.

### 当前范围

- No hardware graphics or Metal qualification is claimed by this non-GPU update. Existing GPU investigation files remain preserved separately.

### 下一步

- Update this area only in a separately scoped GPU synchronization; autonomous work remains paused.

### 证据

按下一步操作收集证据。

## 网络 {#network}

`planned`

### 硬件与依赖

- Board WLAN/Bluetooth hardware, firmware, power/bus/IRQ/DMA and OS interface inputs still need independent qualification.

### 配置

- Development Wi-Fi identity only supplies system metadata; existing explicit service policy is retained.

### 操作步骤

- Identify actual hardware and firmware before adding interfaces; qualify packet traffic and recovery independently.

### 开发经验

- Desktop boot does not depend on a working radio. A MAC identity property is not a network driver.

### 完成条件

- Real interface publication, association, transmit/receive and recovery have matching device evidence.

### 当前范围

- Wi-Fi, Bluetooth and cellular networking are unimplemented or unqualified; Apple service exclusions are explicit.

### 下一步

- Keep this area planned until hardware-specific inputs and an appropriate driver are established.

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`planned`

### 硬件与依赖

- Actual DSP, codec, amplifier, clocks, firmware and board routes remain required.

### 配置

- Original Apple audio bundles may be retained for boot dependencies; no K80 audio endpoint is claimed.

### 操作步骤

- Qualify hardware/firmware, clocks and output/input routing before playback/record tests.

### 开发经验

- No playback or capture acceptance result exists for this port.

### 完成条件

- Device-backed endpoints, playback, recording, volume and error recovery pass separately.

### 当前范围

- Audio and related DSP power management remain unimplemented.

### 下一步

- Keep planned; identify board inputs before selecting a driver.

### 证据

按下一步操作收集证据。

## 电源 {#power}

`implemented`

### 硬件与依赖

- Original ApplePMGRNub ABI, board panel DSI and independent Gunyah watchdog; full PMIC/battery data is missing.

### 配置

- PMGR compatibility covers object lifetime/AON methods/service publication; panel dimming uses the existing DCS path.

### 操作步骤

- Audit the actual ABI and final calls, use bounded operations/readback and preserve independent recovery.

### 开发经验

- PMGR service publication and hardware dimming have results; these do not implement complete Qualcomm power/charging/DVFS.

### 完成条件

- Local ABI/panel scope is accurate; battery, charging, thermal and sleep/wake each need real hardware qualification.

### 当前范围

- Battery/charging policy, thermal management, DVFS and full sleep/wake are unqualified.

### 下一步

- Preserve dimming/watchdog behavior and keep complete power management separate.

### 证据

- `source`: [Implemented PMGR compatibility covers service publication and original ABI/object lifetime. It does not claim charging, DVFS or sleep/wake support.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/native/pmgr/README.md)

## 镜像组装 {#packaging}

`implemented`

组件: `XnuPrelink`.

### 硬件与依赖

- Pinned donor kernelcache/trust cache, owner policy, seed, ADT, FD, SDK and audited board archives.

### 配置

- 192MiB FAT32 with512B clusters; Android header4/gzip; no Android ramdisk or appended DTB. Canonical debug builder retains flat output via fixed compatibility board.

### 操作步骤

- Require source/object/final-link/FAT/ready audits and complete immutable input archives before a new temporary boot.

### 开发经验

- 157 patches replayed twice and1011 fresh XNU objects linked;3a entered desktop twice. Controlled tool dates yielded identical full kernels across2 actual incremental links in one prepared workspace.
- c50 complete kernel5310b1dd and bootc50ca7ea passed independent start.o,7-object correspondence,26 pre-pack functions/14 call edges/46 GOT/4 callbacks; the full preflight publisher was separately audited as a27th function.255 input hashes and77 immutable archive files matched at run completion.

### 完成条件

- Every build uses known inputs and refuses stale objects, mismatched archives or failed audits.

### 当前范围

- Historical ABI audit inputs and prepared SDK/cache are still required. Repeated incremental links are not clean-bootstrap/cross-machine reproducibility. The new format2 native output route has no fresh kernel/device qualification.

### 下一步

- Finish recipe/output-path equivalence checks before a format2 kernel build; do not relabel old manifests or overwrite42f3/3a baselines.

### 证据

- `source`: [Archived2 independent157-patch replays and1011 fresh XNU objects reached prelink/packaging; subsequent device failures are separate evidence.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/clean-source-replay-2026-10-29.json)
- `source`: [Archived path-normalized source-control image3a reached owner-confirmed desktop/taps with221 inputs and fresh log; no general layout/root-cause claim.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/qualified-source-desktop-3a8ac966.json)
- `source`: [Archived controlled ar/ld probes and2 actual incremental native links produced identical complete kernel bytes in one prepared workspace; clean-bootstrap/cross-machine claims are excluded.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/tool-date-reproducibility-2026-10-30.json)
- `source`: [Archived c50 build passed independent start/object/FAT and26 pre-pack functions/14 call edges/46 GOT/4 callbacks; preflight publisher supplement was separately bound as a27th function.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/cpu-active-linked-2026-10-30.json)
- `source`: [Format2 four-layer/9-component/157-patch resolution, DTS/ADT/tree, official catalog metadata simulation and fixed legacy-selection host checks passed. Source/record files remain uncommitted; this is not a new native kernel or phone result.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/format2-documentation-sync-2026-10-30.json)

## 诊断 {#diagnostics}

`implemented`

### 硬件与依赖

- Fixed92988a43/zorn/b; existing single4KiB log block and recovery BCB; independent watchdog and bounded automatic recovery.

### 配置

- Autonomous work is paused by owner. Runtime logs remain hash-bound; v19 and experimental E/20-ZCLA/2 preserve old fields. No cross-core running-thread stack reads.

### 操作步骤

- Only interpret a recovered run with a changed raw log and exact boot/kernel/input/archive identity. Camera lock screen vs Apple logo is a separate result.

### 开发经验

- The c50 run17:53:39..18:00:14 recovered in395s;120s frame was lock screen4:02. Two epochs63744/243896ms had error0,maskff/status0 and raw tick192000, converted to10ms.
- All8 USER/SYSTEM cumulative counters grew;8 accepted/transferred/retired with no rejection. No historical Apple-logo failure was reproduced or explained. The one planned observation is consumed.

### 完成条件

- A fresh traceable log and bounded recovery exist, with unknown/error readings preserved and qualification limits explicit.

### 当前范围

- No FPS/MHz/idle%/copy-vs-wait attribution or continuous-window/long-term qualification. Log I/O duration includes encoding, lock waits and preemption. No further CPU/GUI repeat is scheduled.

### 下一步

- Keep automation paused until owner direction. Documentation checks must not build/boot or restart the completed diagnostic.

### 证据

- `source`: [Archived single c50 trial recovered in395s;255 inputs/77 archive files and distinct log matched. Lock screen/all8/Data/dim64 passed and every core had USER/SYSTEM accounting progress; no performance/root-cause qualification.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/cpu-active-trial-2026-10-30.json)

</div>
