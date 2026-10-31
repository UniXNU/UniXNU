# Redmi K80 \(zorn\)

[kerrinz/UniXNU-zorn](https://github.com/kerrinz/UniXNU-zorn)

<div v-pre>

Redmi K80: owner-confirmed desktop/basic touch, eight-core checks, retained8GiB Data and dim64. CPU1 narrow root publication has bounded controls; intermittent GUI stalls and long-term stability remain unresolved. Format2 host migration is separate from historical device qualification.

Source record: [porting.toml](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/porting.toml), `e5b5706023dbec02c20d7ec41df0e39e0e235636`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `implemented` |
| [Firmware and boot](#firmware) | `implemented` |
| [CPU and interrupts](#cpu) | `implemented` |
| [Memory and DMA](#memory) | `implemented` |
| [Storage and root](#storage) | `implemented` |
| [Display](#display) | `implemented` |
| [Input](#input) | `implemented` |
| [GPU](#gpu) | `planned` |
| [Network](#network) | `planned` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `implemented` |
| [Image assembly](#packaging) | `implemented` |
| [Diagnostics](#diagnostics) | `implemented` |

## Configuration {#configuration}

`implemented`

### Hardware and dependencies

- K80 / SM8650-AB; iPad7,1 / j120ap, iPadOS17.7.11 /21H461, XNU d8b80295118ef25ac3a784134bcf95cd8e88109f; source-pins.json and unixnu.lock bind the prepared dependencies.

### Configuration

- Root board schema2; record schema1. ARM64, tracked board-local SoC slice, OS and device layers; zorn\_union\_defconfig and explicit complete patch/archive arrays.

### Procedure

- Resolve with unixnu status --json in a separate output root; validate this record and compile dts/zorn.dts before building a new format2 image.

### Development findings

- README was not the catalog ingestion source: the scanner selects format2 from root board.toml, then validates porting.toml. The old root was format1 even though the record checker passed.

### Completion criteria

- Identity, selected components, source pins, configuration fragments, patch order and board package match the intended build route.

### Current limits

- This migration checks configuration/DTS/tree on the host; full native kernel/payload equivalence through the new output layout is not qualified. Historical device runs remain attached to their original manifests.

### Next action

- Audit native recipes for format2 output paths before a complete format2 build; retain the fixed legacy diagnostic entry and all old archives.

### Evidence

- `source`: [Root board now uses schema2 with four profiles,9 components and explicit157-patch order. The retained diagnostic board is SHA-pinned; host migration checks do not qualify a new native kernel or device run.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/repository-format.md)
- `source`: [Format2 four-layer/9-component/157-patch resolution, DTS/ADT/tree, official catalog metadata simulation and fixed legacy-selection host checks passed. Source/record files remain uncommitted; this is not a new native kernel or phone result.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/format2-documentation-sync-2026-10-30.json)

## Firmware and boot {#firmware}

`implemented`

Components: `DarwinBoot`.

### Hardware and dependencies

- uefi-zorn board package; existing Mu-Silicium/EDKII and giulia SM8650 DXE inputs; GOP and PSCI SMC handoff.

### Configuration

- FD base0xA7100000/size0x300000; shim window0xA8000000..0xB8000000; mailbox0xA7601000; menu countdown5s.

### Procedure

- Stage the board package, verify FD/module input manifests and use the guarded device packer; each device observation requires independent watchdog and bounded recovery.

### Development findings

- UEFI menu and DarwinBoot handoff reach the recorded kernel. Existing touch power/clock handoff supports the FT3683 kernel path. Latest CPU/display trials reused the bound FD.

### Completion criteria

- Firmware, menu, sidecars, memory window and actual kernel agree, and fresh recovery evidence is bound to the run.

### Current limits

- The board repository is not the full Mu-Silicium tree. Vendor DXE inputs remain proprietary; the exact hardware reset source was not separately established.

### Next action

- Preserve the known FD and touch handoff while validating any future firmware change separately.

### Evidence

- `source`: [Archived UEFI touch power/clock handoff supports the FT3683 kernel communication path; this update reused the recorded FD and made no firmware build.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/touch-power-handoff-result.json)

## CPU and interrupts {#cpu}

`implemented`

Components: `ArmCpu`, `ArmDTPlatform`.

### Hardware and dependencies

- Actual per-core MIDR/MPIDR, PSCI CPU\_ON, GIC,19.2MHz timer, IPIs and original XNU startup interfaces; all8 core gates and9 mapping rounds.

### Configuration

- Eight-core debug builds default to publication1, other profiles0; explicit0 remains a diagnostic control. Original2s gate and all preflight checks remain.

### Procedure

- Independently assemble current start.s, compare the complete object SHA, audit final code, and bind boot/kernel/inputs/fresh log before interpreting a run.

### Development findings

- Identical75b9ca39 kernel:0-fail/1-pass/0-fail/1-pass. With0 the late MRS TTBR1 was0; with1 it equaled CPU0 pre-start/final root and all8 cores/9 mapping rounds passed. The change cleans the single cache line containing cpu\_ttep,8bytes, without writing root/page tables.
- Two uninstrumented layouts16KiB apart passed preflight; e700 had2 lock-screen runs and936 had1. Early source-slot word4 was0 even on success and is not the actual MMU-off load value. The old5b uninstrumented claim was withdrawn because start.o was stale.
- c50 final capture had status0 on all8 cores in both epochs and USER/SYSTEM cumulative accounting increased on every core.

### Completion criteria

- Per-core identity/timer/IPI/bound work and mapping cleanup pass; startup failures remain preserved and stress/long-term stability are tested separately.

### Current limits

- The narrow publication evidence does not explain every historical GUI stall. a889 passed CPU/Data/dim64 but remained on the Apple logo. Accounting is cumulative and serial, not simultaneous utilization, idle%, MHz or FPS.

### Next action

- Preserve the bounded fix and original gates; do not repeat completed controls or add CPU/GUI probes without new direction.

### Evidence

- `source`: [Archived identical75b9ca39-kernel controls:0-fail/1-pass/0-fail/1-pass, with late TTBR1=0 versus the CPU0 root; original gates unchanged.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/cpu1-root-publication-controlled-2026-10-30.json)
- `source`: [Archived normal GUI observations:2 e700 runs and1 alternate936 layout, with all8 core gates, retained Data, dim64, fresh logs and camera lock-screen frames.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/cpu1-root-publication-gui-2026-10-30.json)
- `source`: [Archived a889900-second failure: CPU/Data/dim64 passed, but120/720-second camera frames remained on the Apple logo. GUI qualification failed and is preserved.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/cpu1-root-publication-stability-2026-10-30.json)
- `source`: [Archived25a same-full-kernel900-second lock-screen observation passed; this excludes the budget as a sufficient cause, not metadata/Data/timing causation.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/gui-budget-same-kernel-2026-10-30.json)
- `source`: [Archived single c50 trial recovered in395s;255 inputs/77 archive files and distinct log matched. Lock screen/all8/Data/dim64 passed and every core had USER/SYSTEM accounting progress; no performance/root-cause qualification.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/cpu-active-trial-2026-10-30.json)

## Memory and DMA {#memory}

`implemented`

### Hardware and dependencies

- Nominal12GiB SKU; actual UEFI memory ownership,4KiB page tables, PAN, DMA constraints and reserved regions.

### Configuration

- Qualified debug profile uses8192MiB. The256MiB decompression window is separate from XNU-owned RAM. The new DTS nominal map is not qualification of all12GiB.

### Procedure

- Check reserved regions, owned allocation, page tables and UFS DMA separately; use bound mapping/cleanup results.

### Development findings

- An8GiB window reached lock screen/desktop. Original VM-map initialization and audited cross-core mapping paths are retained.

### Completion criteria

- No region overlap or DMA escape, with repeated allocation/free, mapping and stress/error-path evidence.

### Current limits

- Full12GiB, long-term pressure and every historical lock/pmap/exec compatibility change remain unqualified.

### Next action

- Audit the migrated hardware description and reserved regions before any new memory-window qualification; do not enlarge the tested window or clear locks.

### Evidence

- `source`: [Board memory/VM-map investigation and compatibility limits are retained; the8GiB desktop result does not qualify the full nominal12GiB map.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/review-2026-10-28-official-houji.md)

## Storage and root {#storage}

`implemented`

Components: `VerifiedRoot`, `RamBlock`, `AppleKeyStoreState`, `SoftwareAES`.

### Hardware and dependencies

- Actual UFS capacity/GPT evidence, SHNGROOT manifest and owner policy, original APFS/IOStorageFamily, immutable seed and retained Data marker.

### Configuration

- OS/SystemOS read-only. Existing Data window:userdata-relative192GiB,2097217 blocks of4096B; original UUID C7D77FF3-6437-4C4A-8E05-E8E239AC1641/cookie2dde8229.

### Procedure

- Verify window/seed/marker and reject out-of-range access; preserve existing initialization and observe APFS mount and cross-boot retention.

### Development findings

- The8GiB UFS-backed Data volume persisted across the recorded desktop and later lock-screen boots; it does not require8GiB of dense RAM. c50 retained the same UUID/cookie with zero RAM/Data errors.

### Completion criteria

- Read-only system identity, bounded Data reads/writes, retained metadata and refusal/recovery errors remain traceable.

### Current limits

- No Android dual boot, automatic reset or window enlargement. Power-loss integrity, endurance and sustained storage stress are not qualified. board.toml userdata coordinates describe capacity-relative legacy input, not absolute GPT LBAs.

### Next action

- Preserve the existing window and seed; require separate evidence for long-term consistency rather than reinitializing Data.

### Evidence

- `source`: [Archived8GiB UFS-backed Data mount/retention preserved the original UUID/cookie without RAM/Data errors. The older unresponsive touch result is retained.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/data8-retained-touch-result.json)
- `source`: [Archived single c50 trial recovered in395s;255 inputs/77 archive files and distinct log matched. Lock screen/all8/Data/dim64 passed and every core had USER/SYSTEM accounting progress; no performance/root-cause qualification.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/cpu-active-trial-2026-10-30.json)

## Display {#display}

`implemented`

Components: `GopFramebuffer`.

### Hardware and dependencies

- GOP framebuffer0xFC400000,1440x3200,5760row bytes,32bpp; O11 DSI panel and DCS0x51/0x52.

### Configuration

- CPU presentation/display-mode3; brightness-mode3 fixes XNU panel value64 and reads it back. Optional v19 retirement/vsync observation retains old log fields.

### Procedure

- Bind actual linked display objects, menu and fresh log; qualify screen appearance independently of transfer counters.

### Development findings

- Brightness307-&gt;64 was read back. Two6aea lock-screen captures had accepted/transfer/retired9/9/9 and8/8/8; c50 had8/8/8, reject0/status0. Independent camera frames showed lock screen.
- Type5 registration/send queue offsets agree. At60Hz, properties0 does not mean no query; healthy lock screens also had started1 and zero observed sender callbacks.

### Completion criteria

- Correct stride/pixels, observed system output and bounded brightness readback; continuous presentation and recovery require separate tests.

### Current limits

- Single camera frames do not qualify the full observation window. Equal counters do not prove per-request pairing; independent relaxed timestamps are not consistent event pairs. Value64 is not calibrated nits/percent.

### Next action

- Keep CPU presentation and brightness baseline; preserve unresolved Apple-logo evidence without changing queues or forcing notifications.

### Evidence

- `source`: [Archived DCS307-to64 transition and fresh64 readback; this is a register value rather than calibrated luminance or a system brightness-slider implementation.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/brightness-dim-result.json)
- `source`: [Archived second6aea bounded run recovered with a camera lock screen and v19 accepted/transfer/retired8/8/8; first run9/9/9 remains separate.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/display-progress-repeat-2026-10-30.json)
- `source`: [Source/final-link audit found matching type5 queue offset5592;60Hz property counters do not prove client registration, receipt or GUI-stall causation.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/display-notification-contract-2026-10-30.json)

## Input {#input}

`implemented`

### Hardware and dependencies

- FT3683/firmware35,40TXx18RX matrix; existing power/GPIO SPI path and original IOHIDFamily parsing ABI.

### Configuration

- Retain touch-handoff/runtime/edges/kernel-parser/trace/fast-poll and the qualified portrait Y direction.

### Procedure

- Verify frame CRC, matrix/baseline, IDs and releases; qualify owner-visible taps/swipes separately from pre-HID traces.

### Development findings

- 42f3 owner confirmed desktop, unlock and icon taps. The second3a run recorded independent IDs0/1 for5188ms with normal release,2219 good frames and55 HID submissions without errors.

### Completion criteria

- Single-touch hit/release and gestures pass; system multi-touch, calibration and long-run responsiveness are distinct qualifications.

### Current limits

- GPIO polling is not proof of60/120Hz input. Two sensor IDs do not prove system pinch/zoom; physical keys, pixel calibration and complex gestures are unqualified.

### Next action

- Preserve usable touch; optimization and additional gesture qualification remain deferred.

### Evidence

- `source`: [Archived42f3 desktop/unlock/icon-tap owner confirmation is bound to boot/kernel/fresh log and124 inputs; no new device test is asserted here.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/touch-desktop-fast-qualified.json)
- `source`: [Archived second3a desktop run recorded2219 good frames,55 HID submissions without errors, and independent IDs0/1 for5188ms with release; system multi-touch remains unqualified.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/qualified-source-repeat-two-contacts.json)

## GPU {#gpu}

`planned`

### Hardware and dependencies

- Board-specific firmware, memory/security ownership and frontend ABI require separate qualification.

### Configuration

- This publication synchronization excludes GPU development progress and retains CPU presentation.

### Procedure

- Keep GPU work and its hardware qualification in a separate update.

### Development findings

- A CPU-rendered desktop does not establish hardware graphics acceleration.

### Completion criteria

- Firmware, isolated mappings, submission, fences, recovery and actual rendering have matching device evidence.

### Current limits

- No hardware graphics or Metal qualification is claimed by this non-GPU update. Existing GPU investigation files remain preserved separately.

### Next action

- Update this area only in a separately scoped GPU synchronization; autonomous work remains paused.

### Evidence

Collect evidence using the next action.

## Network {#network}

`planned`

### Hardware and dependencies

- Board WLAN/Bluetooth hardware, firmware, power/bus/IRQ/DMA and OS interface inputs still need independent qualification.

### Configuration

- Development Wi-Fi identity only supplies system metadata; existing explicit service policy is retained.

### Procedure

- Identify actual hardware and firmware before adding interfaces; qualify packet traffic and recovery independently.

### Development findings

- Desktop boot does not depend on a working radio. A MAC identity property is not a network driver.

### Completion criteria

- Real interface publication, association, transmit/receive and recovery have matching device evidence.

### Current limits

- Wi-Fi, Bluetooth and cellular networking are unimplemented or unqualified; Apple service exclusions are explicit.

### Next action

- Keep this area planned until hardware-specific inputs and an appropriate driver are established.

### Evidence

Collect evidence using the next action.

## Audio {#audio}

`planned`

### Hardware and dependencies

- Actual DSP, codec, amplifier, clocks, firmware and board routes remain required.

### Configuration

- Original Apple audio bundles may be retained for boot dependencies; no K80 audio endpoint is claimed.

### Procedure

- Qualify hardware/firmware, clocks and output/input routing before playback/record tests.

### Development findings

- No playback or capture acceptance result exists for this port.

### Completion criteria

- Device-backed endpoints, playback, recording, volume and error recovery pass separately.

### Current limits

- Audio and related DSP power management remain unimplemented.

### Next action

- Keep planned; identify board inputs before selecting a driver.

### Evidence

Collect evidence using the next action.

## Power {#power}

`implemented`

### Hardware and dependencies

- Original ApplePMGRNub ABI, board panel DSI and independent Gunyah watchdog; full PMIC/battery data is missing.

### Configuration

- PMGR compatibility covers object lifetime/AON methods/service publication; panel dimming uses the existing DCS path.

### Procedure

- Audit the actual ABI and final calls, use bounded operations/readback and preserve independent recovery.

### Development findings

- PMGR service publication and hardware dimming have results; these do not implement complete Qualcomm power/charging/DVFS.

### Completion criteria

- Local ABI/panel scope is accurate; battery, charging, thermal and sleep/wake each need real hardware qualification.

### Current limits

- Battery/charging policy, thermal management, DVFS and full sleep/wake are unqualified.

### Next action

- Preserve dimming/watchdog behavior and keep complete power management separate.

### Evidence

- `source`: [Implemented PMGR compatibility covers service publication and original ABI/object lifetime. It does not claim charging, DVFS or sleep/wake support.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/native/pmgr/README.md)

## Image assembly {#packaging}

`implemented`

Components: `XnuPrelink`.

### Hardware and dependencies

- Pinned donor kernelcache/trust cache, owner policy, seed, ADT, FD, SDK and audited board archives.

### Configuration

- 192MiB FAT32 with512B clusters; Android header4/gzip; no Android ramdisk or appended DTB. Canonical debug builder retains flat output via fixed compatibility board.

### Procedure

- Require source/object/final-link/FAT/ready audits and complete immutable input archives before a new temporary boot.

### Development findings

- 157 patches replayed twice and1011 fresh XNU objects linked;3a entered desktop twice. Controlled tool dates yielded identical full kernels across2 actual incremental links in one prepared workspace.
- c50 complete kernel5310b1dd and bootc50ca7ea passed independent start.o,7-object correspondence,26 pre-pack functions/14 call edges/46 GOT/4 callbacks; the full preflight publisher was separately audited as a27th function.255 input hashes and77 immutable archive files matched at run completion.

### Completion criteria

- Every build uses known inputs and refuses stale objects, mismatched archives or failed audits.

### Current limits

- Historical ABI audit inputs and prepared SDK/cache are still required. Repeated incremental links are not clean-bootstrap/cross-machine reproducibility. The new format2 native output route has no fresh kernel/device qualification.

### Next action

- Finish recipe/output-path equivalence checks before a format2 kernel build; do not relabel old manifests or overwrite42f3/3a baselines.

### Evidence

- `source`: [Archived2 independent157-patch replays and1011 fresh XNU objects reached prelink/packaging; subsequent device failures are separate evidence.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/clean-source-replay-2026-10-29.json)
- `source`: [Archived path-normalized source-control image3a reached owner-confirmed desktop/taps with221 inputs and fresh log; no general layout/root-cause claim.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/qualified-source-desktop-3a8ac966.json)
- `source`: [Archived controlled ar/ld probes and2 actual incremental native links produced identical complete kernel bytes in one prepared workspace; clean-bootstrap/cross-machine claims are excluded.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/tool-date-reproducibility-2026-10-30.json)
- `source`: [Archived c50 build passed independent start/object/FAT and26 pre-pack functions/14 call edges/46 GOT/4 callbacks; preflight publisher supplement was separately bound as a27th function.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/cpu-active-linked-2026-10-30.json)
- `source`: [Format2 four-layer/9-component/157-patch resolution, DTS/ADT/tree, official catalog metadata simulation and fixed legacy-selection host checks passed. Source/record files remain uncommitted; this is not a new native kernel or phone result.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/format2-documentation-sync-2026-10-30.json)

## Diagnostics {#diagnostics}

`implemented`

### Hardware and dependencies

- Fixed92988a43/zorn/b; existing single4KiB log block and recovery BCB; independent watchdog and bounded automatic recovery.

### Configuration

- Autonomous work is paused by owner. Runtime logs remain hash-bound; v19 and experimental E/20-ZCLA/2 preserve old fields. No cross-core running-thread stack reads.

### Procedure

- Only interpret a recovered run with a changed raw log and exact boot/kernel/input/archive identity. Camera lock screen vs Apple logo is a separate result.

### Development findings

- The c50 run17:53:39..18:00:14 recovered in395s;120s frame was lock screen4:02. Two epochs63744/243896ms had error0,maskff/status0 and raw tick192000, converted to10ms.
- All8 USER/SYSTEM cumulative counters grew;8 accepted/transferred/retired with no rejection. No historical Apple-logo failure was reproduced or explained. The one planned observation is consumed.

### Completion criteria

- A fresh traceable log and bounded recovery exist, with unknown/error readings preserved and qualification limits explicit.

### Current limits

- No FPS/MHz/idle%/copy-vs-wait attribution or continuous-window/long-term qualification. Log I/O duration includes encoding, lock waits and preemption. No further CPU/GUI repeat is scheduled.

### Next action

- Keep automation paused until owner direction. Documentation checks must not build/boot or restart the completed diagnostic.

### Evidence

- `source`: [Archived single c50 trial recovered in395s;255 inputs/77 archive files and distinct log matched. Lock screen/all8/Data/dim64 passed and every core had USER/SYSTEM accounting progress; no performance/root-cause qualification.](https://github.com/kerrinz/UniXNU-zorn/blob/e5b5706023dbec02c20d7ec41df0e39e0e235636/docs/evidence/cpu-active-trial-2026-10-30.json)

</div>
