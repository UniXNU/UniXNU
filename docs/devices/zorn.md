# Redmi K80 \(zorn\)

[kerrinz/UniXNU-zorn](https://github.com/kerrinz/UniXNU-zorn)

<div v-pre>

Redmi K80: iOS26 candidate reaches owner-confirmed lockscreen/desktop and basic touch;Settings-long-press freeze and low frame rate remain. Exact261 returns to TWRP automatically. GPU/Metal/display/touch full acceptance and format2 clean-build equivalence remain incomplete;default iPadOS17 profile is retained.

Source record: [porting.toml](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/porting.toml), `8067bd3836bde6a201f657109818562c3aa3f790`.

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
| [GPU](#gpu) | `implemented` |
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
- Root userdata capacity now describes dedicated64GiB unixnu; the immutable historical compatibility board stays SHA d65567ec. Publication checks validate format2/iOS17 resolution and complete path ownership.
- The public610093-byte record at0ca7f702 is complete and parses locally,while the official catalog reports EOF. Its Blob.text reader does not check truncation. Keep this entry concise;the full historical record is archived byte-for-byte.

### Completion criteria

- Identity, selected components, source pins, configuration fragments, patch order and board package match the intended build route.

### Current limits

- This migration checks configuration/DTS/tree on the host; full native kernel/payload equivalence through the new output layout is not qualified. Historical device runs remain attached to their original manifests.

### Next action

- Audit native recipes for format2 output paths before a complete format2 build; retain the fixed legacy diagnostic entry and all old archives.

### Evidence

- `source`: [Root board now uses schema2 with four profiles,9 components and explicit157-patch order. The retained diagnostic board is SHA-pinned; host migration checks do not qualify a new native kernel or device run.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/repository-format.md)
- `source`: [Format2 four-layer/9-component/157-patch resolution, DTS/ADT/tree, official catalog metadata simulation and fixed legacy-selection host checks passed. Source/record files remain uncommitted; this is not a new native kernel or phone result.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/evidence/format2-documentation-sync-2026-10-30.json)
- `source`: [Exact complete pre-compaction record,including all historical evidence and its original limits. Archive references retain their original device-repository base;this is history,not new qualification.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/history/porting-through-v261-2026-11-17.toml)
- `source`: [Current root parses and stays below48KiB;size guard and official-scanner regression reject truncated history and accept complete concise input. No published historical source revision is reassigned.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/catalog-ingestion-2026-11-17.md)

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

- Preserve the known FD and touch handoff. The closed checkpoint FD and distinct terminal media candidate are built/audited in isolation. The latter remains unexecuted pending exact owner permission and all fresh runtime guards.

### Evidence

- `source`: [Archived UEFI touch power/clock handoff supports the FT3683 kernel communication path; this update reused the recorded FD and made no firmware build.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/evidence/touch-power-handoff-result.json)
- `source`: [Publication reconciles current244 evidence,retained17/Data baselines and exact source ownership. Fixed official package entry only plans the default17 profile;26 source archive is not a generic release claim. Existing dated source/host/device scopes remain distinct;no historical revision is reassigned,no new firmware build or device action by publication.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/progress-2026-11-16-ios26.md)
- `source`: [Exact complete pre-compaction record,including all historical evidence and its original limits. Archive references retain their original device-repository base;this is history,not new qualification.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/history/porting-through-v261-2026-11-17.toml)

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
- The CPU-owned memory caller exports the original full preflight gate without reading accounting handles. Native-device path resolution follows the existing native symlink; no new CPU\_ON, mapping round or CPU/GUI trial is introduced by publication.

### Completion criteria

- Per-core identity/timer/IPI/bound work and mapping cleanup pass; startup failures remain preserved and stress/long-term stability are tested separately.

### Current limits

- The narrow publication evidence does not explain every historical GUI stall. a889 passed CPU/Data/dim64 but remained on the Apple logo. Accounting is cumulative and serial, not simultaneous utilization, idle%, MHz or FPS.

### Next action

- Preserve the existing iOS 26 CPU-rendered lockscreen baseline. Use the observed iOS 26 eight-core accounting result as the CPU checkpoint for the lockscreen branch.

### Evidence

- `source`: [Archived identical75b9ca39-kernel controls:0-fail/1-pass/0-fail/1-pass, with late TTBR1=0 versus the CPU0 root; original gates unchanged.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/evidence/cpu1-root-publication-controlled-2026-10-30.json)
- `source`: [The owner-accepted iOS 26 CPU desktop boot 996ff287 again reported eight online cores. All eight IDs showed increasing XNU USER and SYSTEM accounting. The boot returned automatically to TWRP.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/evidence/k80-ios26-cpu-desktop-touch-eightcore-milestone-2026-11-13.json)
- `source`: [Exact complete pre-compaction record,including all historical evidence and its original limits. Archive references retain their original device-repository base;this is history,not new qualification.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/history/porting-through-v261-2026-11-17.toml)

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

- `source`: [Board memory/VM-map investigation and compatibility limits are retained; the8GiB desktop result does not qualify the full nominal12GiB map.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/review-2026-10-28-official-houji.md)
- `source`: [Exact complete pre-compaction record,including all historical evidence and its original limits. Archive references retain their original device-repository base;this is history,not new qualification.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/history/porting-through-v261-2026-11-17.toml)

## Storage and root {#storage}

`implemented`

Components: `VerifiedRoot`, `RamBlock`, `AppleKeyStoreState`, `SoftwareAES`.

### Hardware and dependencies

- Actual UFS capacity/GPT evidence, SHNGROOT manifest and owner policy, original APFS/IOStorageFamily, immutable seed and retained Data marker.

### Configuration

- OS/SystemOS read-only. After owner stock reflash:slotA/OrangeFox, dedicated64GiB unixnu, exact GUID b279731f-ccad-4ef5-a8b7-e7440cd08de3 andLBA47271680..64048895. New8GiB Data window:unixnu-relative16GiB/2097217 blocks; same seedUUID C7D77FF3-6437-4C4A-8E05-E8E239AC1641, fresh metadata cookie1535636492. Old192GiB/cookie2dde8229 evidence is historical.

### Procedure

- Verify window/seed/marker and reject out-of-range access; preserve existing initialization and observe APFS mount and cross-boot retention.

### Development findings

- Historical8GiB Data/c50 results remain archived. The new unixnu64 installation completed its first initialization and retained-touch boot: identical new file-marker cookie2d931234, Data errors0, owner-confirmed unlock/taps and396.65s automatic Recovery. Android system/slotA preserved; Android boot itself was not tested.

### Completion criteria

- Read-only system identity, bounded Data reads/writes, retained metadata and refusal/recovery errors remain traceable.

### Current limits

- Dedicated dual-system storage is installed; full Android boot, cross-system switching, power-loss integrity, endurance and sustained storage stress are not qualified.64GiB partition currently uses an8GiB logical Data backend; never boot an old userdata-targeted image. board.toml userdata coordinates describe capacity-relative legacy input, not absolute GPT LBAs.

### Next action

- Keep Android/slotA and the dedicated unixnu64 profile. Root synchronization is limited to partition/Data/packer/log metadata per latest owner instruction; preserve the original compatibility board, baseline images and all historical proofs.

### Evidence

- `source`: [Archived8GiB UFS-backed Data mount/retention preserved the original UUID/cookie without RAM/Data errors. The older unresponsive touch result is retained.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/evidence/data8-retained-touch-result.json)
- `source`: [Exact complete pre-compaction record,including all historical evidence and its original limits. Archive references retain their original device-repository base;this is history,not new qualification.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/history/porting-through-v261-2026-11-17.toml)

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
- On 2026-11-13 the owner visually confirmed the iOS26 CPU-rendered system lock screen during the bounded b0da41e9 boot; the diagnostic runner does not set lockscreen\_proven, and no camera photo was saved.
- Exact261 owner confirms iOS desktop plus swipe,tap,long-press and unlock;Settings-long-press eventually freezes. Low frame rate and instability are unresolved. This is partial interaction evidence,not full contacts/edges/pixel/scanout acceptance.

### Completion criteria

- Correct stride/pixels, observed system output and bounded brightness readback; continuous presentation and recovery require separate tests.

### Current limits

- Single camera frames do not qualify the full observation window. Equal counters do not prove per-request pairing; independent relaxed timestamps are not consistent event pairs. Value64 is not calibrated nits/percent.

### Next action

- The bounded b0da41e9 run reached the CPU-rendered iOS system lock screen by owner visual confirmation. Keep that milestone distinct from the runner's false lockscreen flag and the missing camera frame; preserve the CPU baseline and prioritize GPU development.

### Evidence

- `source`: [Actual presenter separates pending work from terminal failures;terminal/cache refusal stops CPU worker through existing Mach C adapter,wakes producers and retains unknown frames.7 affected TUs/full1390-input kerneld9f6759d zero undefined;loader/nonZORN component checks pass. No GPU/DMA stop or hardware execution claim;bootc1132857 remains4b18a29f.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/evidence/gpu-k80-presenter-terminal26.json)
- `source`: [Historical evidence for its exact recorded inputs. The linked artifact and complete archive preserve the full original result,commands and limitations;no qualification is transferred to the current candidate.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/evidence/k80-gpu-v251-lazy-session-observed-2026-11-16.json)
- `source`: [Exact261:one boot/zero retries returned verifiedTWRP333.63s;39CDC frames and240s video pass. Owner confirms iOS desktop and basic gestures,then Settings-long-press freeze. First BoMap NoResources inner cause unknown. Both paths lowFPS,no ranking;full acceptance incomplete.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/evidence/k80-gpu-v261-client-failure-observed-2026-11-17.json)
- `source`: [Exact complete pre-compaction record,including all historical evidence and its original limits. Archive references retain their original device-repository base;this is history,not new qualification.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/history/porting-through-v261-2026-11-17.toml)

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
- Exact261 owner confirms iOS desktop plus swipe,tap,long-press and unlock;Settings-long-press eventually freezes. Low frame rate and instability are unresolved. This is partial interaction evidence,not full contacts/edges/pixel/scanout acceptance.

### Completion criteria

- Single-touch hit/release and gestures pass; system multi-touch, calibration and long-run responsiveness are distinct qualifications.

### Current limits

- GPIO polling is not proof of60/120Hz input. Two sensor IDs do not prove system pinch/zoom; physical keys, pixel calibration and complex gestures are unqualified.

### Next action

- Use the verified continuous FT3683 path on the iOS 26 CPU-rendered lockscreen branch. Retain the owner-accepted no-Home desktop and basic touch milestone. Settings interaction, multi-touch identity and edge behavior remain for later qualification.

### Evidence

- `source`: [Archived42f3 desktop/unlock/icon-tap owner confirmation is bound to boot/kernel/fresh log and124 inputs; no new device test is asserted here.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/evidence/touch-desktop-fast-qualified.json)
- `source`: [Actual251 selected TouchBoard/Source/Worker/Host object lineage traced to concrete source and original recipes;all independently rebuild byte-equal. Kernel resource-owner macros ARM\_PGSHIFT14;shared SPI/parser unit makes no CPU-page ownership claim. Source still uses readMatrixFrame/Detector,not qualified controller-reported contacts or complete physical gestures. No new touch operation or binary inspection;original17/Data baselines retained.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/evidence/k80-ft3683-selected-inputs-2026-11-16.json)
- `source`: [Exact261:one boot/zero retries returned verifiedTWRP333.63s;39CDC frames and240s video pass. Owner confirms iOS desktop and basic gestures,then Settings-long-press freeze. First BoMap NoResources inner cause unknown. Both paths lowFPS,no ranking;full acceptance incomplete.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/evidence/k80-gpu-v261-client-failure-observed-2026-11-17.json)
- `source`: [Exact complete pre-compaction record,including all historical evidence and its original limits. Archive references retain their original device-repository base;this is history,not new qualification.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/history/porting-through-v261-2026-11-17.toml)

## GPU {#gpu}

`implemented`

### Hardware and dependencies

- Cached K80 Adreno750v2/gen7-9-1 profile, fixed stock AQE/SQE/GMU/ZAP and KGSL hashes; pinned OEM and Xiaomi14/OnePlusAce5 partial references.

### Configuration

- CPU presentation remains selected. A default-off CPU-owned backing preflight is now integrated in main device sources; one canonical compatibility full build and bounded CPU-owned-memory device trial pass. The GPU frontend and hardware activation are not selected.

### Procedure

- Verify stock provenance and firmware requirements, explicit stopped ownership, Gen7 rings and per-command startup semantics before platform power/security/memory integration.

### Development findings

- The isolated iOS26 K80 direct-ring backend implements source-connected firmware/GMU/HFI,memory,SMMU,submit,fence,IOGPU/Metal and presentation integration. Exact bounded-image and dedicated Metal/image tests retain their own build identities in linked evidence;they are partial qualifications.
- Current261 rebuilds32actual objects and links1398inputs with0undefined;CPU16KiB is separate from GPU4KiB. Source-connected per-client error and close metadata preserves real backend returns and retained foreign-owner attribution.
- Exact261 reached the iOS lockscreen/desktop with owner-confirmed swipe,tap,long-press and unlock responses,but froze after Settings long press. Both CPU and GPU paths are low frame rate;no comparative ranking or measured FPS is claimed. One boot returned to verifiedTWRP333.63s with protected samples unchanged.
- First recorded backend error is PID10/client129 method3 BoMap NoResources;the inner branch and final freeze cause remain unknown. Second client Close/exit was not observed within the existing CDC window. Video shows late home-style UI.

### Completion criteria

- Firmware authentication, owned mappings, power/clock transitions, command submission, fences, recovery and actual rendering require matching K80 device evidence and native Darwin23 ABI/link audits.

### Current limits

- Implemented means source scope only;full GPU/Metal/display/client-lifecycle and FT3683 acceptance are incomplete. Published default17 format2 selection and isolated26 candidates are distinct;clean-checkout full26 release reproducibility remains unqualified.
- Sampled surface/access-fence/acquire/copy metadata does not prove per-frame GPU writes or physical scanout. No cross-task/concurrent isolation,full device/DMA-stop lifecycle or stability qualification. Metadata/legacy stderr may drop;no constant-success substitutes or instruction analysis.

### Next action

- Capture the real BoMap NoResources capacity/refusal branch and extend bounded log coverage to late Settings-long-press freeze while preserving frame/byte/panic/WDT budgets;then fix the evidenced backend cause and validate exact new kernel. Complete real render/presentation and FT3683 lifecycle acceptance.

### Evidence

- `source`: [Historical evidence for its exact recorded inputs. The linked artifact and complete archive preserve the full original result,commands and limitations;no qualification is transferred to the current candidate.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/evidence/k80-gpu-v247-known-present-observed-2026-11-16.json)
- `source`: [Historical evidence for its exact recorded inputs. The linked artifact and complete archive preserve the full original result,commands and limitations;no qualification is transferred to the current candidate.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/evidence/k80-gpu-v251-lazy-session-observed-2026-11-16.json)
- `source`: [Historical evidence for its exact recorded inputs. The linked artifact and complete archive preserve the full original result,commands and limitations;no qualification is transferred to the current candidate.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/evidence/k80-gpu-v260-platform-identity-observed-2026-11-16.json)
- `source`: [Exact261 offline source/32-object1398-input full link0undefined,CPU16KiB118headers,current identity and sanitizer checks,14zero-fuzz patches and full boot package pass. Host/source scope only;no final hardware acceptance.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/evidence/k80-gpu-v261-client-failure-offline-2026-11-17.json)
- `source`: [Exact261:one boot/zero retries returned verifiedTWRP333.63s;39CDC frames and240s video pass. Owner confirms iOS desktop and basic gestures,then Settings-long-press freeze. First BoMap NoResources inner cause unknown. Both paths lowFPS,no ranking;full acceptance incomplete.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/evidence/k80-gpu-v261-client-failure-observed-2026-11-17.json)
- `source`: [Exact complete pre-compaction record,including all historical evidence and its original limits. Archive references retain their original device-repository base;this is history,not new qualification.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/history/porting-through-v261-2026-11-17.toml)

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

- `source`: [Actual SMMU PM private claimant opens/retains real base controller and rechecks ownership around existing power transitions. Independent runtime/suspend grants and source PM algorithm retained. One iOS26 TU/full1390-input kernel5df5a34c zero compile warnings/undefined,loader parse passes. No PM/native/device execution or hardware permission supplied;bootc1132857 remains4b18a29f.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/evidence/gpu-k80-smmu-pm-provider-claim26.json)
- `source`: [Implemented PMGR compatibility covers service publication and original ABI/object lifetime. It does not claim charging, DVFS or sleep/wake support.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/native/pmgr/README.md)
- `source`: [Exact complete pre-compaction record,including all historical evidence and its original limits. Archive references retain their original device-repository base;this is history,not new qualification.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/history/porting-through-v261-2026-11-17.toml)

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
- The unixnu64 host entry pins its reviewed policy and compiled storage kernel; payload packing checks the matching descriptor/proof. Source relocation fixes replace workstation-specific paths; historical input manifests and validation grades remain unchanged.

### Completion criteria

- Every build uses known inputs and refuses stale objects, mismatched archives or failed audits.

### Current limits

- Historical ABI audit inputs and prepared SDK/cache are still required. Repeated incremental links are not clean-bootstrap/cross-machine reproducibility. The new format2 native output route has no fresh kernel/device qualification.

### Next action

- The fixed --gpu-unixnu64-closed-image --os 17 entry packages a source-bound closed FD and exact retained unixnu64 payload without boot. Finish native qualification/protection independently; do not relabel old manifests or overwrite42f3/3a baselines.

### Evidence

- `source`: [Current signed Metal/Turnip actually integrated into separate local rootef11f75a with numeric metadata/signature/HFSX checks. Exact digest bound into kernel4b18a29f+ADT+offline carrier;1390inputs/1 replacement/zero undefined. Original phone rootb56 preserved;new root NOT installed,no device/native execution or GPU qualification.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/evidence/gpu-k80-metal-root-integration26.json)
- `source`: [Exact261 offline source/32-object1398-input full link0undefined,CPU16KiB118headers,current identity and sanitizer checks,14zero-fuzz patches and full boot package pass. Host/source scope only;no final hardware acceptance.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/evidence/k80-gpu-v261-client-failure-offline-2026-11-17.json)
- `source`: [Exact complete pre-compaction record,including all historical evidence and its original limits. Archive references retain their original device-repository base;this is history,not new qualification.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/history/porting-through-v261-2026-11-17.toml)

## Diagnostics {#diagnostics}

`implemented`

### Hardware and dependencies

- Fixed92988a43/zorn/b; existing single4KiB log block and recovery BCB; independent watchdog and bounded automatic recovery.

### Configuration

- Owner explicitly resumed unattended GPU adaptation after the Git pause. Runtime logs remain hash-bound; original v18/v19/E20/v21 history and touch traces are preserved. No cross-core running-thread stack reads.

### Procedure

- Only interpret a recovered run with a changed raw log and exact boot/kernel/input/archive identity. Camera lock screen vs Apple logo is a separate result.

### Development findings

- The c50 run17:53:39..18:00:14 recovered in395s;120s frame was lock screen4:02. Two epochs63744/243896ms had error0,maskff/status0 and raw tick192000, converted to10ms.
- All8 USER/SYSTEM cumulative counters grew;8 accepted/transferred/retired with no rejection. No historical Apple-logo failure was reproduced or explained. The one planned observation is consumed.
- The dedicated unixnu64 media runner adds claim-before-first-USB and exact OrangeFox/GPT/Data/BCB checks, separate from completed installation claims; host-only doubles do not grant execution. Published host-only decoders and guarded runners preserve raw statuses and consumed claims. Reused unixnu64 claims are now refused before USB, input/archive closures and watchdog markers are checked before device action, and host test shims are versioned instead of read from a prior out tree.
- Exact261 captured39CDC frames/67975B and240s video successfully;camera requires the verified full-permission environment. Normal120s CDC poll misses late UI behavior;sampled first BoMap NoResources and final freeze are not yet causally linked.

### Completion criteria

- A fresh traceable log and bounded recovery exist, with unknown/error readings preserved and qualification limits explicit.

### Current limits

- No FPS/MHz/idle%/copy-vs-wait attribution or continuous-window/long-term qualification. Log I/O duration includes encoding, lock waits and preemption. No further CPU/GUI repeat is scheduled.

### Next action

- Preserve current261 raw observations and owner corrections;extend bounded late-window source diagnostics and locate the actual mapping resource branch before another exact single trial.

### Evidence

- `source`: [K80 GENI reported completion of the nonce-tagged transmit after qualifying the inherited UART, default master IRQ mask and disabled GIC interrupt. TWRP returned automatically and protected samples matched. Host wire capture requires an external adapter.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/evidence/k80-ios26-geni-send-observed-2026-11-13.json)
- `source`: [Exact261:one boot/zero retries returned verifiedTWRP333.63s;39CDC frames and240s video pass. Owner confirms iOS desktop and basic gestures,then Settings-long-press freeze. First BoMap NoResources inner cause unknown. Both paths lowFPS,no ranking;full acceptance incomplete.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/evidence/k80-gpu-v261-client-failure-observed-2026-11-17.json)
- `source`: [Exact complete pre-compaction record,including all historical evidence and its original limits. Archive references retain their original device-repository base;this is history,not new qualification.](https://github.com/kerrinz/UniXNU-zorn/blob/8067bd3836bde6a201f657109818562c3aa3f790/docs/history/porting-through-v261-2026-11-17.toml)

</div>
