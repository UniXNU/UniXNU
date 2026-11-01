# Xiaomi Mi 11 M2011K2C: single-CPU platform bring-up

[Sulee7z/UniXNU-venus](https://github.com/Sulee7z/UniXNU-venus)

<div v-pre>

The WSL zeta XNU12377.121.6 build now passes real QEMU UEFI/DarwinBoot handoff and arm\_vm\_init return with a256-byte random seed, EL1/MMU and4KiB pages. Root/Data/userspace for this kernel remain unqualified; see ZETA-WSL-ENTRY.md. Earlier XNU10063 phone baseline:039 touch normal, Metal apparently inactive;040 diagnostic absent;041 prepared. iPhone11,8 iOS17.7 inputs/root are prepared but its MH\_FILESET arm64e conversion remains incomplete; see README.md.

Source record: [porting.toml](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/porting.toml), `9b1402a99d9ee37d8aa4a980eceff18a4c993e02`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `host-verified` |
| [Firmware and boot](#firmware) | `host-verified` |
| [CPU and interrupts](#cpu) | `host-verified` |
| [Memory and DMA](#memory) | `device-verified` |
| [Storage and root](#storage) | `device-verified` |
| [Display](#display) | `host-verified` |
| [Input](#input) | `device-verified` |
| [GPU](#gpu) | `device-verified` |
| [Network](#network) | `planned` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `host-verified` |
| [Image assembly](#packaging) | `host-verified` |
| [Diagnostics](#diagnostics) | `implemented` |

## Configuration {#configuration}

`host-verified`

Components: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`, `DarwinBoot`.

### Hardware and dependencies

- UniXNU 16e592abee8a550dec8154ed1f38b5ebc4f16213 and its component catalog
- Unpublished local SM8350 source selected by local.toml

### Configuration

- Format 2; ARM64 -&gt; SM8350 -&gt; ipados-17.7.11-21H461 -&gt; venus
- The venus\_ufs\_root\_defconfig adds the real owner-policy, Virtio and RAM providers through the audited board archive recipe
- Ordered source patches; missing compile objects trigger bootstrap recovery before archive symbol audits

### Procedure

- Run unixnu defconfig venus\_ufs\_root\_defconfig, status --json, check-stage-foundation.py and the official porting-record checker
- Resolve source pins and apply the recorded host ADT converter patch before generating new stage inputs

### Development findings

- The former device directory contained diagnostic notes rather than a standard board.toml
- The guide's SM8550 peripherals do not describe SM8350; only generic compatible components are selected
- The prerequisite series supplies the PMGR call site; the current profile now links the audited original-nub publication archive and enables XNU\_SHENG\_PMGR.
- After a changed series recreates xnu-work, retained compile records skip the bootstrap pass. Archive compilation then missed TrustCache/API.h; explicitly restoring the matching Apple headers before archives fixes the dependency order.

### Completion criteria

- Profiles and component revisions resolve; complete archive/patch plan is reproducible; source overrides are explicit

### Current limits

- Local SoC/device changes and the shared converter correction are unpublished; evidence records upstream base plus local input hashes

### Next action

- Use the current full-root board with explicit chosen display-scale2/rotation0; the lockscreen candidate explicitly requests6GiB
- Current generator comparison is recorded in LOCKSCREEN-SCALE.md; preserve historical exact-input checks for their original board revisions

### Evidence

- `source`: [Device profile and component selection implemented](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/board.toml)
- `host`: [Historical four-profile/initial configuration check](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/GUIDE-REVIEW.md)
  Command: <code>python3 /mnt/g/UniXNU-Port/tools/check-venus-guide.py</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.
- `host`: [Current full-root defaults and 1GiB owned window aligned; active converter fixed for AAPL,phandle and arm-io offsets; actual ADT/hardware and existing Data-core checks passed. New generated ADT not phone-tested.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/ORDERED-BRINGUP.md)
  Command: <code>python3 scripts/check-stage-foundation.py</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `host`: [WSL XNU12377 kernel17097288B/unstripped21818392B; newly built pinned EFI loaders and256B-seed ADT pass actual QEMU arm\_vm\_init return, matching stack, no timeout, EL1/MMU/native4KiB. Root/Data/userspace and phone boot are not established by this run.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/ZETA-WSL-ENTRY.md)
  Command: <code>python3 -B scripts/probe-zeta-wsl-entry.py --output /root/unixnu-build/zeta-qemu-entry-002 --checkpoint arm_vm_init_return --timeout 90</code>. Revision: `ac9718fb1af618d5ce8678d0dc6e8a58f252216f`.

## Firmware and boot {#firmware}

`host-verified`

### Hardware and dependencies

- Venus stock boot v3, matching vendor\_boot/dtbo, FD 0x9fd00000/2MiB
- Mu\_Basecore cfb93724a06ff86ff5ba971413368a7809ee42a5 with local Venus integration

### Configuration

- Existing venusPkg paths and Mu patch list in board.toml
- Stock header v3 uses vendor\_boot DTB rather than an appended foreign DTB

### Procedure

- Compare shared UniXNURamDiskDxe with the existing combined-initrd VenusPayloadDxe handling
- Integrate AdvancedLogDxe and required libraries; rebuild and round-trip-check the boot container

### Development findings

- ABL initrd overlapped the old DXE heap; the heap moved to 0xc6200000/256MiB
- PrePi AllocatePool rejects the 776555-byte FDT; page allocation fixed the earlier stall
- Shared UniXNURamDiskDxe assumes an integral-sector complete FAT initrd; Venus vendor concatenation requires retaining the bounded board adapter
- VENUS\_GUIDE\_LOGGING compiles DxeCore memory logging, framebuffer forwarding and AdvancedLogDxe QR export; buffer is 128 pages and locator-variable publication is disabled

### Completion criteria

- New profile builds firmware, discovers the RAM FAT and exports readable firmware logs

### Current limits

- The current package uses the external Mu build wrapper for board patch handling; new logger protocol/menu/QR runtime remains untested on phone

### Next action

- Obtain approval for the candidate RAM boot and observe Tools/Advanced Logger and the new kernel handoff

### Evidence

- `source`: [Recorded legacy input-reservation and page-allocation corrections](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/XNU-ENTRY.md)
- `host`: [Logger/QR libraries compiled; boot image round-trip and reservation checks passed](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/PRELINKED-RUNTIME.md)
  Command: <code>bash /mnt/g/UniXNU-Port/tools/make-venus-guide-candidate.sh</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.

## CPU and interrupts {#cpu}

`host-verified`

### Hardware and dependencies

- Affinities 0,0x100..0x700; initial boot CPU affinity zero
- GICD 0x17a00000/0x10000, GICR 0x17a60000/0x100000, stride 0x20000; timer 19.2MHz; PSCI SMC

### Configuration

- Default remains the device-proven boot core. Independent038 selects four affinities0/400/500/700 with cpus4/sheng-smp1
- Retained native BCM2837 arrays support only MAX\_CPUS4; eight-node037 is blocked
- The non-Apple reset entry now preserves Affinity1 and initializes PSCI reset state before debug access

### Procedure

- Compare shared DTSI with live FDT; boot matching profile; verify platform/CPU registration and first timer interrupt
- Enable secondary cores only after individual entry and IPI checks

### Development findings

- Legacy phone probes proved entry/MMU/arm\_vm\_init return only
- New prelinked kernel and its panic-screen payload copy both reached a real QEMU rtclock\_intr return with GIC ready, one running CPU and one timer IRQ
- First prelinked phone run panicked at PC fffffff00741a378, opcode d51be228: fiq\_context\_init wrote CNTP\_CTL\_EL0 after enabling CNTV\_CTL\_EL0. The SM8350 series now removes that inaccessible physical-timer write while retaining virtual timer operation.

### Completion criteria

- Boot CPU receives timer interrupts; every subsequently enabled CPU reaches entry and receives IPI

### Current limits

- 038 compiled-reset and QEMU startup checks observe four available CPUs; not a Venus hardware qualification
- The bounded timer sample does not cover every core and IPI delivered count is0; delivery remains unqualified
- CPU frequency and E/P scheduling are not yet implemented; no complete Apple CPU compatibility claim

### Next action

- See CPU-038-AND-IPHONE.md; complete per-core timer/IPI and device qualification for038
- A full eight-core configuration needs all MAX\_CPUS-dependent kernel objects rebuilt, not a boot-argument change

### Evidence

- `host`: [Exact base and payload kernels: QEMU GIC/timer operation and matched interrupt return, no timeout](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/PRELINKED-RUNTIME.md)
  Command: <code>python3 /mnt/g/UniXNU-Port/ports/UniXNU-venus/scripts/check-prelinked-evidence.py</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.
- `host`: [Photographed CNTP opcode matched old kernel; source rebuild and payload retain CNTV only and pass actual QEMU timer return](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/VIRTUAL-TIMER-FIX.md)
  Command: <code>python3 /mnt/g/UniXNU-Port/ports/UniXNU-venus/scripts/check-virtual-timer-fix.py</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.

## Memory and DMA {#memory}

`device-verified`

### Hardware and dependencies

- Hash-pinned live FDT contains two DRAM banks and 21 nonempty reservations
- Second bank is 0xc0000000 + 0x1c0000000; firmware remains responsible for allocatable regions

### Configuration

- Hardware DTS describes the measured upper DRAM bank; the independent default owned window is now the phone-tested 1GiB
- All 21 fixed live reservations retain their no-map attributes; venus.dsc enables the qualified high-memory region

### Procedure

- Compile DTS and compare CPU/GIC/timer/PSCI, bank and reservation values to live.dtb
- Generate ADT using the selected OS profile and audit each DMA engine before enabling it

### Development findings

- Adding bank lengths across the physical DRAM hole is unsuitable as a single contiguous DTS range
- The new phone run reached IODTGetICellCounts with a null interrupt parent because the shared converter emitted phandle without AAPL,phandle
- The QEMU shared-generator fixture reproduced the exact phone PC/LR/FAR/ESR. Emitting the Apple alias fixed platform discovery and timer return with the same kernel.
- The user-provided 2026-10-28 23:40 photograph reports MEM totalMiB=6144, root=1, 124 processes and OS t=172s; this is physical evidence of a reported 6GiB window at capture time. The photo does not show the full image SHA or prove execution after capture.
- At the same capture, SWAP/COPY are zero and three retained SpringBoard rows show SIGTRAP; UI remains unavailable. UFS read and integrity failure counters are zero.

### Completion criteria

- Handoff ownership matches UEFI; every enabled DMA engine reaches only its assigned memory

### Current limits

- The 6GiB photo has no embedded image SHA or associated RAM-boot log; association to candidate66f5314a follows the user-provided handoff context
- A single photograph cannot establish continued execution after capture or whether memory pressure caused SpringBoard SIGTRAP
- UFS private contiguous DMA and SIDe0 routing are verified by bounded phone reads; other peripheral DMA paths remain unqualified

### Next action

- Continue host-side analysis of the retained SpringBoard display-mode/service failure; do not infer a memory-related fix from the 6144MiB report
- Any further phone observation requires separate confirmation of the exact image and operation
- The new6GiB firmware branch reaches the measured DT bank end0x280000000; source/QEMU results do not replace device evidence

### Evidence

- `source`: [Target-FDT comparison and reservation import implemented](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/scripts/check-venus-hardware.py)
- `host`: [DTS compiled without diagnostics; CPU/GIC/timer/PSCI/DRAM and 21 reservations match retained live FDT; ADT generated](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/GUIDE-REVIEW.md)
  Command: <code>python3 /mnt/g/UniXNU-Port/tools/check-venus-guide.py</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.
- `host`: [Same-kernel QEMU A/B reproduces phone interrupt-parent fault and validates corrected generated ADT; six tests and bilingual docs build passed](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/ADT-IRQ-FIX.md)
  Command: <code>python3 /mnt/g/UniXNU-Port/ports/UniXNU-venus/scripts/check-adt-irq-fix.py</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.
- `device`: [Photo reports6144MiB/root1/procs124 at172s, with no UI, zero swaps/copies and recurring SpringBoard SIGTRAP. Exact boot image association and progress after capture are not independently established.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/MEMORY-6G.md)
  Command: <code>Manual transcription and SHA-256 of user-supplied G:/20261028_234010.JPG</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.

## Storage and root {#storage}

`device-verified`

### Hardware and dependencies

- Live UFS controller 0x01d84000/0x3000; Lahaina PHY 0x01d87000/0xe10
- Actual LUN/GPT, block size, clocks, resets, regulators and SMMU handoff must be reconciled

### Configuration

- Separate register-only, block-read and verified-root configurations retain their own evidence
- Root mode uses the real signed disk policies, persistent Data provider and exact existing 64GiB unixnu selection in GPT slot35
- The existing 1GiB tail reservation is explicitly fixed; 8GiB Data store placement and original seed identity remain stable

### Procedure

- Inventory target UFS/PHY/clock/SMMU ownership; implement bounded read commands
- Verify capacity and known blocks before root publication; derive root UUID from selected IPSW volume

### Development findings

- The user supplied the official dual-system guide for renewed evaluation; the pinned-file design stays deferred
- Android read-only inspection confirms matching primary/backup GPT, a tail userdata partition, spare GPT entries, and matching single-segment-section F2FS superblocks. Recovery/resize support is not yet verified.
- The pinned zeta SM8350 transport matches target resources and compiles against current XNU10063 headers
- Sheng's original IOBlockStorageDevice ABI was checked against actual compiled public metadata and live QEMU class state: 190 slots, sizes 0x90/0x88
- Both probe archives bind 190 concrete slots, 23 overrides and 11 original imports; remaining kernel imports resolve against native link inputs. Exact unixnu/userdata selection and no cross-target/prefix fallback passed ASan/UBSan.
- The initial survey returned err=0, ready UFSHCI3.0 and exact SIDe0/CB2. Unused banks had M clear but nonzero reset bits; restoring the successful reference's initialize-then-readback order fixed the extra pre-zero refusal.
- Approved 20537e4e image then completed 9 commands and 5 GPT reads through bank74. Capacity, both header CRCs, array CRC and primary-header SHA256 match retained Android blocks; final queues/doorbells/GFSR are zero. Evidence: ufs-read-device-verified.json.

### Completion criteria

- Known block reads match; correct root volume mounts; launchd starts; Data writes survive the defined reboot sequence

### Current limits

- The latest exact-image photo \(28051b5a\) demonstrates owner-root acceptance, userspace and zero reported UFS failures/integrity failures; it is not a complete readback or proof of Data persistence across reboot.
- GPT/reset/post-reset geometry and all 67 root sparse fragments completed earlier. The latest full-baseline RAM boot used the existing deployment; no additional root flash is required.

### Next action

- Controlled Data002 write/restart/readback now passes; preserve the kernel/seed/store/marker and exact evidence
- Advance to CPU display mode/known-frame/swap checks using current board-generated inputs without the opt-in Data qualification stop
- Keep broader UFS endurance/error recovery and old-marker cause separate from this one-file persistence result

### Evidence

- `host`: [Exact normal-boot args contain continuous boot-progress2 and no Data stop. Actual recorder core does not freeze at87/120/300s; final kernel's four optional monitor callbacks are mov0/ret. This excludes configured stops, not all possible runtime faults.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/MEMORY-6G.md)
  Command: <code>python3 scripts/check-userspace-stall.py</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `host`: [Preprocessed6GiB firmware descriptor0x100000000+0x180000000 lies within the retained live DT bank with no fixed-reservation overlap. Default4GiB branch checked independently; physical high-memory handoff pending.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/MEMORY-6G.md)
  Command: <code>python3 scripts/check-venus-highmem-map.py --six-gib</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `host`: [User-requested6GiB: same kernel actually sees6442450944B and mounts SystemOS in QEMU. New FD compiles the6GiB SEC descriptor;21 reservations/layout and payload/boot roundtrip pass. Kernel/Data/trust and three loader EFI modules preserved.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/MEMORY-6G.md)
  Command: <code>bash tools/check-userspace-6g-systemos.sh; python3 scripts/prepare-userspace-6g.py; bash tools/build-userspace-6g-firmware.sh; python3 scripts/prepare-userspace-6g.py --finish</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `device`: [At capture the screen reports6144MiB, root1, 124 processes and OS t=172s; UFS errors0, SWAP/COPY0, three SpringBoard SIGTRAP rows and no UI. No claim of progress after capture or memory-related root cause.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/MEMORY-6G.md)
  Command: <code>Manual transcription and SHA-256 of user-supplied G:/20261028_234010.JPG; image SHA and RAM-boot log are not embedded in the photograph</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `device`: [Normal image72630cd0: launchd exec signature accepted at early boot; procs1/failed0 at34s then procs86/failed7 near87s. Securityd p112 starts, UFS read/integrity errors0; no swaps/copies/UI. Visible watchdogd sig5 and IOMFB\_FDR\_Loader exit1 are unresolved observations.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/USERSPACE-BOOT.md)
  Command: <code>record-userspace-photo.py for G:/20261028_192645.JPG and G:/20261028_192932.JPG</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `host`: [Read-only exact21H461 OS plist/program inspection: FDR loader RunAtLoad and IOMFBLaunchFDR/UserCal event matching; watchdogd IOWatchdog event and unsuccessful-exit keepalive. Possible binary error strings retained; actual exit cause/UI dependency not established.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/USERSPACE-BOOT.md)
  Command: <code>python3 scripts/inspect-userspace-launch-jobs.py</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `device`: [User confirmed exact normal-start image, Android return and normal Data/userspace write scope. Devicevenus/55870427 matched; one RAM boot Sending3.688s/Booting0.193s OKAY total3.923s. Actual kernel/userland/UI observation pending; authorization consumed.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/USERSPACE-BOOT.md)
  Command: <code>python tools/test-venus-pooldiag.py --image G:/UniXNU-Port/artifacts/venus-userspace-001/phone/boot-venus-unixnu.img --sha256 72630cd0d5771caec5ce7c870a371fdd0c863dcd5c0b89b0261bccf97b5ca897 --log G:/UniXNU-Port/logs/venus-userspace-001-phone.txt --adb-port 5037</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `host`: [Normal launchd/CPU-display candidate72630cd0 removes Data-test phase/token, retains qualified kernel4b1ae1c0/ADT/seed/trust/firmware and current board args. Actual generator comparison, payload readback and boot roundtrip pass; normal Data/userspace writes expected; no phone UI result yet.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/USERSPACE-BOOT.md)
  Command: <code>python3 scripts/prepare-userspace-phone.py; python3 scripts/prepare-userspace-phone.py --check</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `device`: [Controlled persistence passed: write49s and confirmed-restart read63s both phase-correct/step11/rc0/match1/bytes53; same Data identity, store2, write sync all0, read sync uncalled and writes1to1. Exact images/photos and restart authorization verified. One53-byte file, not full UFS endurance/recovery.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/DATA-SYNC-QUALIFICATION.md)
  Command: <code>python scripts/check-data-persistence-result.py after recording G:/20261028_190037.JPG and G:/20261028_190612.JPG</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `device`: [User confirmed manual restart after write and exact read scope. Identityvenus/55870427 matched; one RAM boot Sending3.682s/Booting0.193s OKAY total3.914s. Actual file comparison still pending result photo.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/DATA-SYNC-QUALIFICATION.md)
  Command: <code>python tools/test-venus-pooldiag.py --image G:/UniXNU-Port/artifacts/venus-data-check-002/read/boot-venus-unixnu.img --sha256 eb1da7ff22e6f89a9afd6f98c8a1fb64b20667e71b715bad72a11c82318218e5 --log G:/UniXNU-Port/logs/venus-data-read-002-phone.txt --adb-port 5037</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `device`: [Write passed: mount/data/parent/file all1000009, stage4/status0/writable; persist writes0to32, fsync snapshot1/fullsync32, runs0to23/errors0, present47130to47136. File/dir/full/UFS sync all0; step11 rc0 match1 bytes53 token9d78d0cf store2. Reboot read still pending.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/DATA-SYNC-QUALIFICATION.md)
  Command: <code>record-data-check-result.py --out-name venus-data-check-002 --phase 1 --photo G:/20261028_190037.JPG --seconds 49 with complete DATA CHECK/DEV/IO/SYNC transcription</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `device`: [User confirmed exact write image/new53B file/sync scope and Android return. Identity matched; one RAM boot Sending3.691s/Booting0.193s OKAY total3.924s. File-operation result awaits four diagnostic rows; read phase not authorized.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/DATA-SYNC-QUALIFICATION.md)
  Command: <code>python tools/test-venus-pooldiag.py --image G:/UniXNU-Port/artifacts/venus-data-check-002/write/boot-venus-unixnu.img --sha256 53478a3ffd8799e958327b6a023be576bcaed38f72487fe2db23b353f2707409 --log G:/UniXNU-Port/logs/venus-data-write-002-phone.txt --adb-port 5037</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `host`: [Real transaction core separately models file/parent/checkpoint/medium sync, failures, same-device validation and read-only phase; ASan/UBSan pass. Kernel adapter uses openat, sys\_fcntl F\_FULLFSYNC and explicit UFS sync.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/DATA-SYNC-QUALIFICATION.md)
  Command: <code>python3 scripts/check-data-sync-contract.py</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `host`: [Kernel4b1ae1c0 and paired53478a3f/eb1da7ff images: current source/compile/model/pixel receipts, new token, post-SystemOS RamBlock, retained inputs and payload roundtrip verified. Actual QEMU SystemOS/AKS/HID pass, Data file operations not exercised on host.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/DATA-SYNC-QUALIFICATION.md)
  Command: <code>python3 scripts/check-data-sync-candidate.py</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `source`: [Re-read official UFS, ShengUfs/RamBlock, sheng storage and bring-up documents; mapped hardware/adoption/ABI/read/root/write/reset completion conditions to Venus sources and evidence. Identified missing physical write and checkpoint observations.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/UFS-GUIDE-RECHECK.md)
- `host`: [Pinned zeta transport resources match target sources](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/ZETA-REUSE.md)
  Command: <code>python3 /mnt/g/UniXNU-Port/ports/UniXNU-venus/scripts/audit-zeta-ufs-reuse.py</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.
- `host`: [Patched SMMU/GPT/manifest primitives pass under ASan/UBSan](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/ZETA-REUSE.md)
  Command: <code>python3 /mnt/g/UniXNU-Port/ports/UniXNU-venus/scripts/test-zeta-ufs-primitives.py</code>. Revision: `68c513467bb6c44106c053c410582c1d14f96dd7`.
- `host`: [Read-only GPT/F2FS evidence, live iOS17 storage ABI, explicit-partition archives and import gates checked](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/DUAL-SYSTEM-SHENG.md)
  Command: <code>python3 /mnt/g/UniXNU-Port/ports/UniXNU-venus/scripts/check-storage-preparation.py</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.
- `host`: [Register survey archive, QEMU controls and exact container verified; subsequent phone result recorded separately](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/UFS-SURVEY.md)
  Command: <code>python3 /mnt/g/UniXNU-Port/ports/UniXNU-venus/scripts/check-ufs-survey-candidate.py</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.
- `device`: [Approved a3080473 image: err=0, ready HCI3.0, idle queues, exact SIDe0/CB2, no storage commands](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/UFS-SURVEY.md)
  Command: <code>fastboot -s 55870427 boot G:/UniXNU-Port/artifacts/venus-ufs-survey/phone/boot-venus-unixnu.img</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.
- `host`: [Independent block-read archive/kernel/payload and default-off/refusal controls verified; five sanitizer suites pass; no physical block-read claim](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/UFS-BLOCK-READ.md)
  Command: <code>python3 /mnt/g/UniXNU-Port/ports/UniXNU-venus/scripts/check-ufs-survey-candidate.py --block-read</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.
- `host`: [Actual retained phone GPT passes the compiled parser; expected block SHA/CRCs recorded; linked SMMU store uses a real source register and barriers](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/UFS-BLOCK-READ.md)
  Command: <code>python3 /mnt/g/UniXNU-Port/ports/UniXNU-venus/scripts/check-ufs-read-reference.py</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.
- `device`: [Approved 5f2a8d47 image: contiguous DMA allocation and IDR2 observed; unqualified-bank refusal before configuration, command count zero](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/UFS-BLOCK-READ.md)
  Command: <code>fastboot -s 55870427 boot G:/UniXNU-Port/artifacts/venus-ufs-read/phone/boot-venus-unixnu.img</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.
- `host`: [Bounded strict bank fallback and full refusal reporting; sanitizer, kernel/payload QEMU and exact container checks passed; new phone approval pending](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/UFS-BLOCK-READ.md)
  Command: <code>python3 /mnt/g/UniXNU-Port/ports/UniXNU-venus/scripts/check-ufs-survey-candidate.py --block-read --suffix=-banks</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.
- `device`: [Eight unused M-clear/CBAR0/CBA2R0 states captured; extra full-SCTLR-zero precondition rejected all before initialization, commands=0](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/UFS-BLOCK-READ.md)
  Command: <code>fastboot -s 55870427 boot G:/UniXNU-Port/artifacts/venus-ufs-read-banks/phone/boot-venus-unixnu.img</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.
- `host`: [Successful-case initialization order restored for observed unused reset states; all eight photo-value regressions and blocked-write controls pass; exact kernel/payload/container revalidated](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/UFS-BLOCK-READ.md)
  Command: <code>python3 /mnt/g/UniXNU-Port/ports/UniXNU-venus/scripts/check-ufs-survey-candidate.py --block-read --suffix=-init</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.
- `device`: [Approved 20537e4e image completed 9 commands/5 GPT reads: 4096-byte blocks, 252555821056 bytes, 64 entries/34 used, CRCs/header SHA match prior Android raw blocks, bank74, final queues/doorbells/GFSR zero; no media write](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/UFS-BLOCK-READ.md)
  Command: <code>fastboot -s 55870427 boot G:/UniXNU-Port/artifacts/venus-ufs-read-init/phone/boot-venus-unixnu.img</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.
- `host`: [Actual root kernel/prelink and crypto controls pass; read-only APFS OS root reaches real owner acceptance in QEMU; signed root/Data/trust inputs and exact images match](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/DEPLOYMENT-64G.md)
  Command: <code>python3 /mnt/g/UniXNU-Port/ports/UniXNU-venus/scripts/check-venus-deployment-ready.py</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.
- `host`: [Compiled EFI application updates both exact synthetic GPT regions in QEMU with no non-GPT data; sanitizer fault tests cover all transaction boundaries; phone writes pending](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/DEPLOYMENT-64G.md)
  Command: <code>python3 /mnt/g/UniXNU-Port/ports/UniXNU-venus/scripts/test-venus-gpt-efi.py</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.
- `host`: [Corrected VENUSXNU FAT label passes actual board recognizer; complete UniXNU menu to EFI application chain updates and verifies the synthetic GPT. Old phone launch had no success result; erase remains blocked until approved corrected-image success](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/DEPLOYMENT-64G.md)
  Command: <code>python3 /mnt/g/UniXNU-Port/ports/UniXNU-venus/scripts/test-venus-gpt-efi.py --menu-chain</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.
- `device`: [Separately approved GPT update/readback, matching sizes, userdata/metadata erases and reboot completed; root flash not authorized by that sequence](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/DEPLOYMENT-64G.md)
  Command: <code>fastboot -s 55870427 boot G:/UniXNU-Port/artifacts/venus-deployment/gpt-apply-label/boot-venus-unixnu.img</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.
- `device`: [Android boot\_completed=1, slot\_a, mounted F2FS /data and named sda35 unixnu observed; exact post-reset size awaits fastboot](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/DEPLOYMENT-64G.md)
  Command: <code>python verify-android-reinitialized.py --boot-only</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.
- `host`: [Full RAW/FILL sparse image with no skipped blocks independently reconstructs the exact signed root hash; not flashed](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/IOS26-FLASH-REVIEW.md)
  Command: <code>python3 /mnt/g/UniXNU-Port/ports/UniXNU-venus/scripts/prepare-venus-root-flash.py</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.
- `device`: [Post-reset sizes matched; authorized 67-fragment unixnu flash and matching RAM boot returned success; actual loader observation is separate](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/DEPLOYMENT-64G.md)
  Command: <code>python flash-venus-root.py --execute-authorized</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.
- `device`: [DarwinBoot rejected 512MiB window before XNU entry; largest run 310MiB. Android16 slot\_a subsequently booted normally](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/DEPLOYMENT-64G.md)
  Command: <code>Read G:/20261027_114751.JPG and subsequent ADB boot properties</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.
- `host`: [288MiB actual QEMU root checkpoint passed, with two protected policy copies and 75218944 free bytes. New b017a79e boot preserves root kernel/trust/Data and changes only ADT window plus fresh random seed](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/DEPLOYMENT-64G.md)
  Command: <code>python3 check-venus-root-memory-candidate.py</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.
- `device`: [Locally adapted base plus original schema-2 Venus full defconfig: authorized 28051b5a image shows root=1, procs=112, UFS failures0/integrity0/published2 and 904112 verified blocks. Actual memory is 1024 MiB; SpringBoard still exits with signal5; Data persistence unverified.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/LEGACY-MIGRATION.md)
  Command: <code>fastboot -s 55870427 boot G:/UniXNU-Port/artifacts/venus-legacy/full-phone/boot-venus-unixnu.img</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `device`: [Android boot/venus/root and 64GiB unixnu size confirmed; read only 65 blocks of Data header/bitmap. SHNGDATA version, size, page count, seed hash, CRC and bitmap bounds matched; generation1/present47130. No phone reboot/write or known-file persistence test performed.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/ORDERED-BRINGUP.md)
  Command: <code>python scripts/check-data-foundation.py --read-android</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `host`: [Paired write/read images use the corrected board-generated ADT and common kernel. Exclusive 53-byte marker creation, fsync/reopen, modeled reboot/read-only verification and failures pass host tests; fixed result row, source receipts, payload readback and QEMU root/OS-service control pass. Phone persistence operation remains pending.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/DATA-QUALIFICATION.md)
  Command: <code>python3 scripts/check-data-check-candidate.py</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `device`: [Exclusive creation, 53-byte write, fsync, close/reopen and same-boot byte comparison passed. Test waits before launchd while kernel timers continue. Post-restart read phase remains pending.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/DATA-QUALIFICATION.md)
  Command: <code>Inspect G:/20261028_135005.JPG after authorized eddb17c4 write-image RAM boot; python3 scripts/record-data-check-result.py --phase 1 --photo G:/20261028_135005.JPG --seconds 263 --line 'DATA CHECK phase=1 step=11 rc=0 match=1 bytes=53 token=dbb03eb9 store=2'</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `device`: [At88s phase2 step6 rc2 match0 bytes0 store2: OpenRead returned ENOENT after confirmed restart. Controlled cross-reboot persistence failed; no retry.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/DATA-QUALIFICATION.md)
  Command: <code>Inspect G:/20261028_141312.JPG after authorized da4d54ff read-image RAM boot; record-data-check-result.py --phase 2</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `host`: [Actual publication tails with real Overlay/DirectDisk and a caching consumer reproduce the old seed/checkpoint view mismatch. Restoring before publication, failure refusal and mode0 controls pass ASan/UBSan. Not an APFS or phone reproduction.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/DATA-PUBLICATION.md)
  Command: <code>python3 scripts/check-data-publication.py</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `host`: [Device RamBlock patch compiled and installed through the root archive recipe; 190-slot ABI, 24 overrides, 11 original imports and shared aliases match. Full kernel aebf1da2 and actual QEMU owner-root/AKS/HID controls pass. Physical Data operation pending.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/DATA-PUBLICATION.md)
  Command: <code>bash tools/build-venus-data-publication.sh; bash tools/check-venus-data-publication-qemu.sh; python3 scripts/record-data-publication-build.py</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `host`: [New original-marker phase2 image6c1dff2d uses corrected RamBlock and board-generated ADT. Complete original token/content, unchanged compiled qualification code, provider object, retained Data/trust/firmware, payload readback and boot roundtrip verified. No authorization or phone execution.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/DATA-PUBLICATION.md)
  Command: <code>python3 scripts/prepare-data-read-recovery.py --kernel-sha256 aebf1da232089c88c0a2c1534fa72e06addd74c66cf69db18914c8b7b6795460; python3 scripts/check-data-read-recovery.py</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `device`: [User confirmed Android return and exact-image scope. Identityvenus/55870427 matched; one RAM boot Sending3.688s/Booting0.193s OKAY, total3.923s. Authorization consumed, no retry; kernel/Data readback pending photograph.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/DATA-PUBLICATION.md)
  Command: <code>python tools/test-venus-pooldiag.py --image G:/UniXNU-Port/artifacts/venus-data-read-recovery-001/phone/boot-venus-unixnu.img --sha256 6c1dff2d86b48ce5f811398db78d5929ed23eac82b9755d730cedbd3aeeca9ac --log G:/UniXNU-Port/logs/venus-data-read-recovery-001-phone.txt --adb-port 5037</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `device`: [Photo and user confirmation: root1/procs1, clock2s and SystemOS mount entry remain stuck. No Data test row; boot progression failed, file result unknown.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/DATA-PUBLICATION.md)
  Command: <code>record-data-recovery-photo.py --photo G:/20261028_174145.JPG --seconds 2 --last-stage 'SystemOS mount enter' --clock-stalled-confirmed</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `host`: [Real start/publication code with Overlay/DirectDisk: no Data media or I/O before modeled SystemOS boundary, then restored first read/nextboot; idempotent/duplicate/failure/mode0 controls pass ASan/UBSan.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/DATA-PUBLICATION.md)
  Command: <code>python3 scripts/check-deferred-data-publication.py</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `host`: [Post-SystemOS publisher compiles against190-slot storage ABI; full kernel a8f3d1bc links. Actual QEMU SystemOS mount/owner authorization reachesstage6/status0; AKS/HID pass. No UFS/Data hardware emulation.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/DATA-PUBLICATION.md)
  Command: <code>bash tools/build-venus-data-publication.sh; bash tools/check-venus-deferred-systemos.sh</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `host`: [fd22deba image uses corrected post-SystemOS Data publication, board-generated ADT, original token/marker and unchanged seed/trust/firmware. Source/object/patch receipts, payload readback and boot roundtrip pass; not phone-tested.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/DATA-PUBLICATION.md)
  Command: <code>python3 scripts/check-data-read-recovery.py --out-name venus-data-read-recovery-002</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `device`: [User confirmed Android return and exact002 scope; venus/55870427 matched, one RAM boot Sending3.705s/Booting0.194s OKAY, total3.940s. Authorization used; SystemOS/Data result awaiting photograph.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/DATA-PUBLICATION.md)
  Command: <code>python tools/test-venus-pooldiag.py --image G:/UniXNU-Port/artifacts/venus-data-read-recovery-002/phone/boot-venus-unixnu.img --sha256 fd22deba625e228bd1b5a57377d5a7ee77c8ecbcf864fc7e6d68c99a27086d23 --log G:/UniXNU-Port/logs/venus-data-read-recovery-002-phone.txt --adb-port 5037</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `device`: [SystemOS/Data mount progression passed and monitor continues, but OpenRead is still ENOENT. Post-SystemOS publication did not recover the original marker; controlled persistence remains failed.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/DATA-PUBLICATION.md)
  Command: <code>record-data-recovery-photo.py --out-name venus-data-read-recovery-002 --photo G:/20261028_181833.JPG --seconds 39 --line 'DATA CHECK phase=2 step=6 rc=2 match=0 bytes=0 token=dbb03eb9 store=2'</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `host`: [Exact compiled-source UFS store callbacks and RootCommands/Overlay with modeled DMA/medium pass successful FUA WRITE10, UPIU/UTRD/length, SYNCHRONIZE CACHE10, header/bitmap/page reopen, bounds, SCSI errors and timeout quarantine. Not physical UFS or APFS durability.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/UFS-GUIDE-RECHECK.md)
  Command: <code>python3 scripts/check-ufs-data-command-contract.py</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.

## Display {#display}

`host-verified`

Components: `GopFramebuffer`, `AppleKeyStoreState`.

### Hardware and dependencies

- Phone panel 1440x3200; retain actual GOP base, stride, format and reservation
- Target MobileFramebuffer/IOSurface ABI and panel brightness protocol

### Configuration

- The full defconfig links NativeLegacyDisplay with the audited original ABI and CPU presentation enabled
- AppleKeyStoreState is linked; per-candidate offline-key-events/sheng-aks gates select the offline state service

### Procedure

- Validate kernel console first; then bind GopFramebuffer using audited profile ABI and board initialization
- Test known-frame presentation and brightness separately

### Development findings

- Visible UEFI and entry bands establish scanout, not a functioning iOS graphics service
- The complete baseline now displays BootProgress and runs userspace, but SpringBoard retains signal-5 failures. The photograph does not identify a specific display/GPU dependency as their cause.
- The current full Venus kernel's original IOMobileGraphicsFamily text matches the sheng reference \(2e044ee6...\). Its 358-slot Legacy dispatch, constructor chain, nine pure slots, generic override set and newUserClient ABI pass the static audit; no runtime instance, display publication or scanout is claimed.
- The display archive is now linked into the full kernel. QEMU still reaches \_native\_owner\_root\_accepted\_checkpoint \(1 GiB owned, no timeout\) while NativeLegacyDisplay reports stage10, init/start success, probe/parent match, surface\_found and an 800x600 GOP mapping. NativeGOPPresenter.ready remains 0; no client, transfer, swap or frame is observed. Some display data-field reads remain unavailable \(E22\) in the probe.
- The exact display-enabled image was RAM booted on the phone once. It stopped on a BootProgress page with only top/bottom content; no SpringBoard or desktop appeared, and the panel did not show a presented frame. The image was not retried.
- The lock screen does not require Metal: the iPadOS 17 qemu and tb128fu records reach CPU-rendered UI \(others also do\), and both require the offline AppleKeyStore state service. Without it MKBEventsRegister fails, liveactivitiesd crashes at every start, chronod waits on it and SpringBoard on chronod, so the render server never takes the display. Venus showed exactly liveactivitiesd/SpringBoard SIGTRAP, DISPLAY stage10 and SWAP=0.
- The AppleKeyStoreState component and KeyStoreProbe.cpp are now linked into the display late archive with a deferred initializer; the final kernel's late probe calls the real native\_keystore\_probe. The service answers offline state queries only and provides no key storage. The 068e4ad1 kernel / 998bc56e boot candidate adds offline-key-events=1 sheng-aks=1 with all other inputs unchanged; phone result pending.
- Recorded before this repository was published \(local evidence artifact\): AKS symbols, the real late-probe call, deferred initializer, archive members and sources verified; kernel 068e4ad1 / boot 998bc56e reach the QEMU owner-root and start NativeLegacyDisplay. The offline state service adds offline-key-events=1 sheng-aks=1; no phone result yet.

### Completion criteria

- OS display service presents known frames and completes swaps; brightness controls match visible output

### Current limits

- iOS composition, display swaps and a frame are still unverified
- The AKS-only phone run at 150 s still shows SpringBoard SIGTRAP and SWAP=0. The recent-exit tail does not prove liveactivitiesd/watchdogd recovered; earlier pending-result and causal statements are superseded by HID-OS-SERVICES.md.
- QEMU in the HID candidate verifies AKS/HID initialization before root acceptance, not userspace health or a Venus panel
- AKS is an offline state/notification service and provides no key storage, keybag or data protection

### Next action

- After exact012 image/protected directory/3fixed cache backups/journal scope confirmation, measure invalidation and regenerated scale/UI
- 012 only accepts unowned UID-2/mode0 for exact shared MG path on Data; preserve original ownership checks for preferences and all backup/error evidence
- Keep010 normal original chain/IPS and separate actual APFS rename from QEMU medium absence or device UI success

### Evidence

- `host`: [Current full Venus original family text and 358-slot Legacy ABI match the static sheng reference; constructor chain, pure slots and overrides pass. Runtime display, scanout and desktop remain unverified.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/LEGACY-MIGRATION.md)
  Command: <code>python3 scripts/audit-venus-mobile-graphics.py</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `host`: [QEMU with the display archive linked reaches the real owner-root checkpoint and creates/starts NativeLegacyDisplay with an 800x600 GOP. NativeGOPPresenter.ready is 0 and no client/frame is observed; display data-field reads report E22.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/LEGACY-MIGRATION.md)
  Command: <code>python3 scripts/test-venus-root-mount.py --kernel .../kernel.macho --owned-memory-size 0x40000000 --inspect-memory-budget --out-name qemu-display-1g --extra-kernel-arg offline-legacy-register=1 ...</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `device`: [Authorized 279526f1 display image: RAM boot OKAY, phone stopped on BootProgress with only top/bottom content; no SpringBoard/desktop/frame. No partition write or retry; phone needs manual Android recovery.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/LEGACY-MIGRATION.md)
  Command: <code>fastboot -s 55870427 boot G:/UniXNU-Port/artifacts/venus-display-phone/phone/boot-venus-unixnu.img</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.

## Input {#input}

`device-verified`

Components: `ShengHidInput`, `ShengNovatekTouch`, `QcomGeniSpi`.

### Hardware and dependencies

- Venus touch chip/firmware, transport, reset/IRQ pins and physical orientation
- Selected IOHIDFamily ABI

### Configuration

- Format-2 defaults keep phone touch disabled; separately prepared 035 selects STM FTS SPI producer and the retained mainline HID consumer
- 035 enables sheng-touch-hid=1 and venus-st-custom-hid=0, replaces native\_touch stubs, and verifies unique producer symbols at link time

### Procedure

- Identify target sensor and bus from vendor DTS/source; implement bounded chip-ID and frame reads
- Publish consistent coordinates and contact IDs through matching HID ABI

### Development findings

- Sheng NT36532 matrix and wiring cannot be inferred from the Mi 11 panel size
- Actual original IOHIDFamily text, 207-slot IOHIDDevice dispatch, constructors and report ABI match the selected iOS17 kernel
- 035 vendor audit confirms STMicroelectronics fts\_spi, not FocalTech; motion 0x23 and lift 0x33 were reversed in the old codec and its tests
- 035 fixes reset OUT bit1 clearing, removes writes to the sampled GPIO input level, restores STM ready/scan-echo sequencing and corrects CS hold placement
- User confirms touch succeeds after the single035 boot, image db727796ae044c84feaf27fcc745357ddaee4ca064e60b7541b655ebac5fb98a; see TOUCH-035-AUDIT.md

### Completion criteria

- Correct press/move/release, stable multitouch IDs and physical-button HID events

### Current limits

- The user's confirmation does not enumerate every multitouch/edge gesture or physical button
- 035 does not reuse the old custom-HID QEMU qualification; host OS/SystemOS raw images are absent
- Prelaunchd counters do not observe later user input

### Next action

- Retain the exact035 producer/consumer in GPU candidates;036 link checks both binary hashes
- Keep historical phone artifacts and the user confirmation in TOUCH-035-AUDIT.md

### Evidence

- `host`: [Kernel 7a3f0b09 / boot 96a2c747: 207-slot HID ABI, callable hooks, writable state and source/archives verified; real QEMU AKS/HID initialized under enabled gates and remained off in the disabled control; host row39 repaint checked.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/HID-OS-SERVICES.md)
  Command: <code>python3 scripts/check-venus-hid-candidate.py</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `device`: [At 132 s, AKS=3/0 opens4 calls110 and HID=3/0/0 res1 meta0 start1/0, GPU a4; SpringBoard SIGTRAP and zero swaps/copies remain. The photo PC/slide maps to a verified BRK \#0 in the deployed FrontBoardServices. No physical-input or desktop result.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/HID-OS-SERVICES.md)
  Command: <code>Inspect G:/20261028_091241.JPG after the authorized 96a2c747 RAM boot; python3 scripts/record-venus-hid-photo.py</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.

## GPU {#gpu}

`device-verified`

### Hardware and dependencies

- SM8350 Adreno 660, GMU/ZAP firmware, SMMU, power and command submission ABI

### Configuration

- build-venus-a660.py links the A660 backend and the separately delayed generic original-IOAcceleratorES adapter against iOS17
- Mi 11 GMU/SQE/ZAP firmware is hash-checked and injected into the retained ADT;036 mode9/Metal1 and successful035 touch; GPU scanout handoff remains disabled
- 036 waits for GPU initialization before launchd and sets both Metal discovery properties before service registration
- 039 aligns the plugin entry with zeta's framebuffer/IOSurface constraints, persistent cache preference and failure reporting; its trust is one static module preserving all2554 original entries
- 040 adds a bounded plugin-written postlaunch JSONL diagnostic at /private/var/db/venus-metal-040/native.jsonl with root/mobile cache and tmp fallbacks

### Procedure

- Audit A660 generation requirements and implement matching platform/backend
- Verify bounded submissions, fences and known pixels before Metal/UI workloads

### Development findings

- Official Adreno740 implements A740/SM8550; Venus uses the SM8350/A660 reference with the Mi 11 ZAP image and the unit's measured fuse value \(0 here, not the previously assumed 4\)
- The old stage0/calls0 photographs used pulse-reserved row47 and are stale pixels, not runtime zero evidence. The new diagnostic uses rows24-29 and41 with real repaint regression.
- Cold-start trace retained a Duo 2 physical address; it now occupies an audited 8192-byte kernel BSS buffer, independent of the Venus ZAP region.
- The one authorized a660-live phone run reached GMU context Ready, parsed the command DB and built votes, completed the firmware cold start with HFI ready, powered GX, started the GPU context/SQE/ring/CP, ran the ZAP shader to stage 9, returned the expected CP\_MEM\_WRITE word \(05e9a660\), published the accelerator and completed two user-client submission rounds \(4/4 matches each\).
- The still-retained SpringBoard/watchdogd SIGTRAP exits have no timestamp, so their ordering relative to the successful GPU publish is unknown; publication did not by itself produce a frame, desktop or render server.

### Completion criteria

- DMA mappings and fences work; known rendering and OS presentation pass

### Current limits

- Historical GMU/GX/CP device results do not establish Metal rendering
- 039 was booted: touch normal, no performance change and Metal apparently inactive
- 040 was booted and read back; no plugin diagnostic file was present. This does not distinguish plugin-not-reached from filesystem denial
- 041 is host-verified but not booted; its prelaunch file is the next actual observation
- CPU scanout does not by itself imply CPU composition; hardware rendering and display tearing require distinct observations
- The current boot still uses the iPadOS17 root; iPhone11,8 iOS17.7 root/profile/inputs are prepared but arm64e prelink and matching Data seed are not

### Next action

- Boot041 only with separate authorization, then extract /private/var/db/venus-metal-041/startup.json and the040 plugin JSONL
- Continue zeta ordinary-pointer/arm64e prelink work for the checked iPhone11,8 iOS17.7 kernelcache and build its matching Data seed

### Evidence

- `host`: [Source-bound host pixel regression, A660/display/BootProgress archives, kernel BSS trace and final providers verified. New 9b1be886 image round-trips and QEMU reaches actual owner-root without timeout, GPU mode0.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/A660-LIVE-DIAGNOSTICS.md)
  Command: <code>python3 scripts/check-a660-live-screen.py; python3 scripts/prepare-venus-a660-phone.py --out-name venus-a660-live-phone --kernel-sha256 e9481d2ac32006d1e074651162a695202705f2ea6dd8eb8a14c73366f3179a47 --build-tag a660-live; python3 scripts/check-a660-live-candidate.py</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `device`: [Authorized once after Android recovery: Sending 3.692 s, Booting 0.194 s. At t\~99 s the live rows showed the full A660 bring-up: GMU context Ready, clocks configured, DB/votes built, cold start success with HFI ready, GX on, CP step10, ZAP stage9, CP write word 05e9a660, publish success and two 4/4 client rounds. No frame, desktop or Metal frontend; SIGTRAP exits remain.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/A660-LIVE-DIAGNOSTICS.md)
  Command: <code>python3 tools/test-venus-pooldiag.py --image G:/UniXNU-Port/artifacts/venus-a660-live-phone/phone/boot-venus-unixnu.img --sha256 9b1be886d5a934499f4f4659830f51146685c69f60412e1d46e520feaa6d1f32 --log G:/UniXNU-Port/logs/venus-a660-live-phone.txt --adb-port 5037</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.

## Network {#network}

`planned`

### Hardware and dependencies

- Venus WLAN endpoint identity, bus, board-data, firmware and interrupt/DMA ownership

### Configuration

- Ath12kWifi is not selected without checking the actual endpoint generation

### Procedure

- Identify endpoint and firmware family; validate bus/DMA/interrupts; then port protocol and OS network interface

### Development findings

- Sheng WCN7850 support is not evidence for the Mi 11 endpoint

### Completion criteria

- Scan, association, address configuration and sustained TX/RX pass

### Current limits

- WLAN transport and OS service not implemented

### Next action

- Identify enabled WLAN/PCIe resources from target inputs

### Evidence

Collect evidence using the next action.

## Audio {#audio}

`planned`

### Hardware and dependencies

- Target ADSP firmware, PAS/GLINK/APR or GPR protocol, codec/amplifier wiring and OS audio ABI

### Configuration

- No DSP or audio service selected

### Procedure

- Identify firmware protocol and one real route; establish bounded requests and DSP-visible buffers before OS publication

### Development findings

- Guide AudioReach/GPR examples require checking the firmware generation and route on Lahaina

### Completion criteria

- Known PCM playback/capture, correct format, buffer progression and repeatable stop/start

### Current limits

- DSP transport and codec route audit pending

### Next action

- Document target DSP protocol and codec topology after root/display bring-up

### Evidence

Collect evidence using the next action.

## Power {#power}

`host-verified`

### Hardware and dependencies

- Target RPMh/PMIC/clock ownership, battery protocol/units and CPU OPPs

### Configuration

- sleep-disabled=1; firmware-inherited resource state for initial single-core boot
- XNU\_SHENG\_PMGR=y with the audited original service publication archive; sheng-pmgr=2

### Procedure

- Identify resource owners and read-only battery/clock facts; implement measured transitions for dependent drivers

### Development findings

- After the timer and ADT fixes, original AMFI panicked with No PMGR at ConfigurationSettings.cpp:235
- Reused the 21H461 original-PMGR publisher from the pinned sheng source, preserving its exact ABI gates and original nub/methods
- Real QEMU lifecycle/release, publication/lookup, unsupported-operation and original AMFI call tests passed. Both kernel and final payload reached IOFindBSDRoot.

### Completion criteria

- Declared power transitions and battery readings match observations and preserve dependent devices

### Current limits

- Phone now passes the previous AMFI stop and reaches root-device discovery. Verification remains limited to logical original-PMGR compatibility; physical clocks, suspend/resume, battery and DVFS are not implemented.

### Next action

- Retain the working PMGR path while integrating the next physical-storage dependency

### Evidence

- `host`: [Original-provider ABI build and four QEMU modes passed; base and instrumented kernels reach the actual root finder](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/PMGR-DEPENDENCY.md)
  Command: <code>python3 /mnt/g/UniXNU-Port/ports/UniXNU-venus/scripts/test-venus-pmgr.py</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.

## Image assembly {#packaging}

`host-verified`

### Hardware and dependencies

- Profile-pinned XNU 10063.141.1 and iPad7,1/J120 21H461 IPSW/kernelcache
- Trust-cache bundle, storage ABI and Data seed

### Configuration

- Prelinked crypto path with inherited OS root components; 160MiB FAT leaves room in the 192MiB boot partition
- Root UUID and userdata ranges will be filled from verified inputs, not example values

### Procedure

- Use unixnu ipsw info/fetch, build kernel, package, firmware, userdata dry-run, payload and bootimg in dependency order

### Development findings

- The previous kernel is a source-only diagnostic build; complete userland requires prelinked Apple services and root/Data volumes
- The official build now links the generic archives and prelinks 30 executable Apple components plus codeless IOHIDEventDriver
- Windows-checked-out XnuPrelink patches needed LF restoration; patch contents match their index. High-volume compilation completed in the G-backed WSL filesystem after /mnt/g exceeded the runner timeout.

### Completion criteria

- Prelink resolves the selected ABI; payload inputs and userdata geometry agree; boot container round-trips

### Current limits

- The latest complete baseline reaches root acceptance and userspace; a functional desktop and Data persistence across reboot remain unverified. Its reused phone-highmem-1g payload is 1 GiB, despite an incorrect pre-boot 3 GiB description.

### Next action

- Keep exact kernel/payload/ADT identities and memory settings with each future candidate; preserve the tested control images

### Evidence

- `host`: [Historical complete kernel and prelink input checks](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/GUIDE-REVIEW.md)
  Command: <code>bash /mnt/g/UniXNU-Port/tools/build-venus-guide.sh</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.
- `host`: [Historical001 scale/cache candidate; phone later stalled before its cache phase](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/LOCKSCREEN-SCALE.md)
  Command: <code>python3 scripts/prepare-lockscreen-scale.py</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `host`: [Actual iOS17 ARM64 helper,17 ad-hoc4KiB page hashes, retained original trust modules, C API/JSON models, addon wire roundtrip, current ADT generator, kernel/seed/FD/EFI identity and008 boot roundtrip pass. No actual helper runtime or lockscreen result.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/MG-QUERY-OBSERVATION.md)
  Command: <code>python3 scripts/build-mg-query-probe.py; python3 scripts/check-mg-query-protocol.py; python3 scripts/prepare-mg-query-phone.py</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `host`: [Existing captures strictly re-extracted at DSTREAM EOF7477 rather than allocation8192. All three MG plists valid and byte-identical; MainScreenStaticInfo.scale0 present. Historical cache-truncation conclusion withdrawn.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/MG-QUERY-OBSERVATION.md)
  Command: <code>python tools/verify-mg-file-size.py; python scripts/recheck-data-forensics.py --run saved-capture --output new-evidence-directory</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `source`: [User-supplied iamOJZ/haydn at70ef03e5:15 files checked against Git blob/length; virtual timer/UART/SPI resource organization reviewed, no lockscreen result and different touch/memory/storage inputs.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/HAYDN-IAMOJZ-REFERENCE.md)
- `device`: [Exact image/query installation/output/normal Data scope approved; Androidvenus/55870427 matched, one RAM boot Sending4.327s/Booting0.193s OKAY total4.563s. Actual helper/API/lockscreen result unconfirmed; awaits report. Authorization consumed.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/MG-QUERY-OBSERVATION.md)
  Command: <code>python tools/test-venus-pooldiag.py --image G:/UniXNU-Port/artifacts/venus-mg-query-008/phone/boot-venus-unixnu.img --sha256 2ef531b07097c440dc51210548a8a3dfecd46a658c8e783c0e168376d590c71b --log G:/UniXNU-Port/logs/venus-mg-query-008-phone.txt --adb-port 5037</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `device`: [User authorized readonly after Android return.50255 pages/31 runs/stable metadata and hashes verified; exact installation persisted, JSON/stderr absent. Matching008 boot args log reaches normal launchd bootstrap/SpringBoard pid27. Signed OS launch cache has561 full definitions and excludes query; activation unqualified, no measured MG value.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/MG-QUERY-OBSERVATION.md)
  Command: <code>python scripts/collect-data-forensics.py --read-android; python scripts/collect-data-forensics.py --offline G:/UniXNU-Port/artifacts/venus-data-forensics/read-20261029T041826Z; python scripts/record-mg-query-readback.py</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `host`: [009-r2 newkernel/explicit task repair: actual C wrapper real fork/exec/mobile501/stdio/dedup/timeout and mount VFS models pass sanitizers.17 signed shim pages and original trust/query modules checked. Both rebuilt kernels reach real6GiB QEMU SystemOS/AKS/HID; Data/task not exercised there. Only policy member differs from rebuilt control, display/RamBlock retained. Exact34635bc4 image wire/FAT/input/boot checks pass, not device-tested.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/MG-TASK-ACTIVATION.md)
  Command: <code>python3 scripts/check-mg-task-launch.py; python3 scripts/build-mg-task-wrapper.py; python3 scripts/check-mg-task-qemu.py; python3 scripts/check-mg-task-qemu.py --baseline; python3 scripts/prepare-mg-task-phone.py; python3 scripts/prepare-mg-task-phone.py --check</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `device`: [Exact009-r2 image/3file installation/readonly union/normal Data scope confirmed; venus/55870427 matched. One RAM boot Sending4.331s/Booting0.193s OKAY total4.564s. Authorization consumed; actual task/API/lockscreen result awaits readonly report retrieval.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/MG-TASK-ACTIVATION.md)
  Command: <code>python tools/test-venus-pooldiag.py --image G:/UniXNU-Port/artifacts/venus-mg-query-009/phone-r2/boot-venus-unixnu.img --sha256 34635bc461ec668e87066a3d9bff58c07a7312ef40f8d656e3a989553d9f91c0 --log G:/UniXNU-Port/logs/venus-mg-query-009-r2-phone.txt --adb-port 5037</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `device`: [Authorized readonly50274 pages/31 runs stable/SHA/coverage verified. All009 files root:root0755 match;1083B policy XML exactly matches compiled source after MG hook. No3outputs;4launchd logs unchanged008. Installer/policy progressed; mount return/status and later exec unresolved, no measured MG answer.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/MG-TASK-ACTIVATION.md)
  Command: <code>python scripts/collect-data-forensics.py --read-android; python scripts/record-mg-task-readback.py --run G:/UniXNU-Port/artifacts/venus-data-forensics/read-20261029T052623Z</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `source`: [Requested official sheng HEAD/tree and19 blobs verified. Same21H461 common init order; old qualified policy equals upstream except local Data-check hook. Only kt\_fixed\_zones120/disable-watchdogd1 of four examined policies have4b1 implementations; board/storage/GPU/log/seed scope differs.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/SHENG-STARTUP-CHAIN.md)
  Command: <code>python scripts/fetch-sheng-startup-reference.py; python3 scripts/compare-sheng-startup.py</code>. Revision: `08cde20edc3254ed6f7df8d0f5384fb887786e8f`.
- `host`: [010 original4b1 normal launchd chain with two supported original policies. Kernel/ADT/seed/trust/6GiB FD/EFI preserved; actual new-args QEMU SystemOS/AKS/HID and FAT/boot checks pass. Original Data-policy/UI not exercised on host; image5f906121 not phone-tested.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/SHENG-STARTUP-CHAIN.md)
  Command: <code>python3 scripts/prepare-sheng-chain-control.py; python3 scripts/prepare-sheng-chain-control.py --check</code>. Revision: `08cde20edc3254ed6f7df8d0f5384fb887786e8f`.
- `device`: [Exact010 image/normal Data/original policy scope confirmed; venus/55870427 matched, one RAM boot Sending4.331s/Booting0.193s OKAY total4.564s. Authorization consumed. UI/new log/policy result awaits readonly retrieval.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/SHENG-STARTUP-CHAIN.md)
  Command: <code>python tools/test-venus-pooldiag.py --image G:/UniXNU-Port/artifacts/venus-sheng-chain-010/phone/boot-venus-unixnu.img --sha256 5f9061214acfd829ec893af61904d438844e1fb4ae584122565360653fb9a57d --log G:/UniXNU-Port/logs/venus-sheng-chain-010-phone.txt --adb-port 5037</code>. Revision: `08cde20edc3254ed6f7df8d0f5384fb887786e8f`.
- `device`: [User reports counters kept running then manual Android reboot; authorized readonly124248 pages/65runs/508919808B stable/SHA/coverage passed. Exact010 log bootstrap and watchdogd-disabled policy observed;19 SB SIGTRAP exits.5 actual IPS match PIDs/incidents/FBS UUID/offsetf744/BRK0 at display manager init. No measured UI/MG API success.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/SHENG-CHAIN-010-RESULT.md)
  Command: <code>python scripts/collect-data-forensics.py --read-android; python scripts/analyze-sheng-chain-readback.py --run G:/UniXNU-Port/artifacts/venus-data-forensics/read-20261029T063818Z</code>. Revision: `08cde20edc3254ed6f7df8d0f5384fb887786e8f`.
- `source`: [Official MG/display/Setup/device docs re-read; pinned umi3eb72578\(8files\) and tb128fua9c3863d\(3files\) verified by Git blob/length/SHA. Same21H461 CPU UI and typed scale paths documented. No inspected standalone exact FBS patch; choose documented cache invalidation with preserved backups.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/SCALE-REFRESH-011.md)
- `host`: [Actual cache/journal C models pass sanitizers incl durable-begin guard/exclusive backups/env preservation. Newc2f380ca kernel real QEMU SystemOS/AKS/HID plus packed Data4/status0 and post-policy checkpoint: sync refused without UFS, cache unmodified. Existing011 markers absent, retained RamBlock/ADT/seed/trust/FD/EFI checked, imagee5da7c4f roundtrip/FAT passed. Positive hardware rename/cache/UI unmeasured.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/SCALE-REFRESH-011.md)
  Command: <code>python3 scripts/check-scale-refresh011.py; python3 scripts/check-scale-refresh011-qemu.py; python3 scripts/check-scale-refresh011-qemu.py --data-checkpoint; python3 scripts/prepare-scale-refresh011-phone.py; python3 scripts/prepare-scale-refresh011-phone.py --check</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `device`: [Exact011 image/cache exclusive backup/journal/sync/normal Data scope confirmed; venus/55870427 matched. One RAM boot Sending4.329s/Booting0.193s OKAY total4.565s. Authorization consumed; actual backup/journal/fresh-cache/UI result awaits Android return and bounded1GiB readonly evidence.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/SCALE-REFRESH-011.md)
  Command: <code>python tools/test-venus-pooldiag.py --image G:/UniXNU-Port/artifacts/venus-scale-refresh-011/phone/boot-venus-unixnu.img --sha256 e5da7c4fd4acddb961f945a6d11d2d13b888843d56d59b47722401bea162cc41 --log G:/UniXNU-Port/logs/venus-scale-refresh-011-phone.txt --adb-port 5037</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `device`: [011 user photo/no UI, returned Android approved readonly.141394pages/72runs/579149824B stable/hash/coverage; original inode869/private869 and7477B SHA unchanged,3backups/tmp journal absent; new011 log bootstrap/3SB SIGTRAP. Missing tmp journal cannot identify exact operation branch; original OS cleanup target confirmed.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/SCALE-REFRESH-011.md)
  Command: <code>python scripts/collect-data-forensics.py --read-android --max-bytes 1073741824; python scripts/record-scale-refresh011-readback.py</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `host`: [Actual APFS snapshot metadata + exact MG data fixture: oldguard source UID-2/modeS\_IFREG0/7477 → EPERM/sourcevalidation/moved0. Fixed exact shared-path guard → requested1/moved1/missing6/journal0; real rename/2dirsync done, medium EIO retained without UFS. Pruned fixture is not production/user image.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/SCALE-REFRESH-012.md)
  Command: <code>python scripts/make-scale-snapshot-fixture.py; python3 scripts/check-scale-refresh011-qemu.py --version 012 --data-checkpoint</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `host`: [Protected root0700 db journal/backups, granular sync/error states, exact shared-cache unowned guard. Actual C models and real APFS positive namespace test/SystemOS/AKS/HID pass; retained RamBlock/ADT/seed/trust/FD/EFI and image38245b0e checks pass. No hardware cache/UI success yet.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/SCALE-REFRESH-012.md)
  Command: <code>python3 scripts/check-scale-refresh012.py; python3 scripts/check-scale-refresh011-qemu.py --version 012; python3 scripts/prepare-scale-refresh011-phone.py --version 012; python3 scripts/prepare-scale-refresh011-phone.py --version 012 --check</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `device`: [Exact012 image/protected directory/3fixed cache sources→backups/journal/sync/normal Data scope confirmed.venus/55870427 matched; one RAM boot Sending4.329s/Booting0.193s OKAY total4.566s. Authorization consumed; runtime protected status/cache/fresh scale/UI awaits readonly retrieval.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/SCALE-REFRESH-012.md)
  Command: <code>python tools/test-venus-pooldiag.py --image G:/UniXNU-Port/artifacts/venus-scale-refresh-012/phone/boot-venus-unixnu.img --sha256 38245b0ec67db7766f9ef91ce251569c199872bf94e133b53c81e6b7c17cda11 --log G:/UniXNU-Port/logs/venus-scale-refresh-012-phone.txt --adb-port 5037</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `device`: [User confirms system welcome page after exact012 authorized boot. Preserve38245b0e image/c1c16fbc kernel as UI baseline. Physical touch/Metal/cache-detail readback not part of this observation. New requested work: none24smu/zeta Metal and self-written ST touch.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/README.md)
  Command: <code>User observation: 成功！已经进入系统欢迎页面 after the recorded exact012 RAM boot</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `host`: [Pinned36blob zeta reference, same A660 board scope and explicit17/536-byte ABI. Real native17 frontend/Rust/Turnip compile/link; plugin+Turnip4K CodeDirectory pages verified and own additive trust preserves2old modules. Actual host softwareVulkan AIR compute/render/import bad0. Device Metal/GPU pixels still unverified.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/METAL-TOUCH-013-014.md)
  Command: <code>python3 scripts/fetch-zeta-metal-reference.py; python3 scripts/prepare-venus-metal-sources.py; python3 scripts/build-venus-metal-bridge.py; python3 scripts/compile-venus-metal-frontend.py; python3 scripts/build-venus-turnip.py; python3 scripts/link-venus-metal-plugin.py; python3 scripts/link-sign-venus-turnip.py; python3 scripts/package-venus-metal-addon.py; python3 scripts/check-venus-metal-runtime-host.py</code>. Revision: `eb489285a1d9153872f00c93ebb519a269b249b5`.
- `host`: [Own ST SPI5codec/state/HID/XO/GPIO/GENI message backend compiled and linked to original17 ABI; real FTB bounds/ID/multi/lift/dummy/IO failure Csanitizer tests and new default-off SystemOS/6GiB/AKS/HID/FAT/FD/EFI/boot roundtrip pass. Physical chip/PIO/power handoff/touch events await authorized014.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/METAL-TOUCH-013-014.md)
  Command: <code>python3 scripts/check-venus-st-protocol.py; python3 scripts/build-venus-st-touch.py; python3 scripts/link-venus-metal-touch-kernel.py; python3 scripts/prelink-mg-task-kernel.py --directory artifacts/venus-metal-touch/kernel-link-2; python3 scripts/check-venus-metal-touch-qemu.py; python3 scripts/prepare-venus-metal-touch-phone.py --kind touch; python3 scripts/prepare-venus-metal-touch-phone.py --kind touch --check</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `host`: [Separate013 mode9/Metal publish5file addon candidate82f242ac... prepared and independently checked; same newkernel5c9824..., original012 seed/geometry/FD/EFI preserved, no MG invalidation/Data reset/new job. No hardware boot yet.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/METAL-TOUCH-013-014.md)
  Command: <code>python3 scripts/prepare-venus-metal-touch-phone.py --kind metal; python3 scripts/prepare-venus-metal-touch-phone.py --kind metal --check</code>. Revision: `eb489285a1d9153872f00c93ebb519a269b249b5`.
- `device`: [Exact013 approved/booted once; venus/55870427 matched, Sending4.343s/Booting0.193s OKAY. User reports lag and uncertain GPU effect, requests touch test. Actual Metal discovery/GPU pixels unverified.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/METAL-TOUCH-013-014.md)
  Command: <code>python tools/test-venus-pooldiag.py --image G:/UniXNU-Port/artifacts/venus-metal-013/phone/boot-venus-unixnu.img --sha256 82f242ac57b6b214898c9e88d3f6aa6d01dd59efc334c9426df4d9f44015e9bd --log G:/UniXNU-Port/logs/venus-metal-013-phone.txt --adb-port 5037</code>. Revision: `eb489285a1d9153872f00c93ebb519a269b249b5`.
- `device`: [After manual Android return, exact014 XO/GPIO/GENI/MCUreset/volatile scan/HID/normalData scope approved.venus/55870427 matched, one RAM boot Sending4.342s/Booting0.193s OKAY total4.584s. Photo \~4min later still PID0/root0/display0/PE\_lockdown\_iokit. QEMU reproduced premature VenusHidTouch metaclass registration/panic; fixed with late initializer. Authorization consumed; physical touch never reached.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/METAL-TOUCH-013-014.md)
  Command: <code>python tools/test-venus-pooldiag.py --image G:/UniXNU-Port/artifacts/venus-touch-014/phone/boot-venus-unixnu.img --sha256 7f5f335a822dc70d22c9ac9a0a9d3eea7bf9d6edf84de4933198592f5bf75a48 --log G:/UniXNU-Port/logs/venus-touch-014-phone.txt --adb-port 5037</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `host`: [Raw VenusHidTouch.o automatic \_\_mod\_init\_func caused venus\_st\_hid\_start -&gt; OSMetaClass::postModLoad panic in QEMU. macho-late-init.py produced VenusHidTouch.late.o with no automatic init; new native mod\_init824B equals012. default-off and mode1 reach SystemOS/AKS/HID; mode1 \_venus\_st\_stage2/status0/hid\_status0. Phone untested.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/TOUCH-015-FIX.md)
  Command: <code>python3 scripts/build-venus-st-touch.py; python3 scripts/link-venus-metal-touch-kernel.py; python3 scripts/prelink-mg-task-kernel.py --directory artifacts/venus-metal-touch/kernel-link-5; python3 scripts/check-venus-metal-touch-qemu.py --touch-mode 0 --name qemu-metal-touch-default-off-r3; python3 scripts/check-venus-metal-touch-qemu.py --touch-mode 1 --name qemu-metal-touch-mode1-r4</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `host`: [Touch015 image92018c0f... kernel87145de7,168960000B;012 ADT/seed/trust/FD/EFI preserved; FAT/roundtrip/--check pass. Phone not booted.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/TOUCH-015-FIX.md)
  Command: <code>python3 scripts/prepare-venus-metal-touch-phone.py --kind touch --version 015; python3 scripts/prepare-venus-metal-touch-phone.py --kind touch --version 015 --check</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `host`: [Metal016 image82d3b33e... kernel87145de7,168960000B; same012 inputs plus own signed addon/trust and A660mode9/Metal publish scope; FAT/roundtrip/--check pass. Phone not booted; supersedes013.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/TOUCH-015-FIX.md)
  Command: <code>python3 scripts/prepare-venus-metal-touch-phone.py --kind metal --version 016; python3 scripts/prepare-venus-metal-touch-phone.py --kind metal --version 016 --check</code>. Revision: `eb489285a1d9153872f00c93ebb519a269b249b5`.
- `device`: [Exact015 deferred-initializer kernel approved/booted once; venus/55870427 matched, Sending4.347s/Booting0.193s OKAY total4.594s. Authorization consumed; welcome-page/physical touch/chip/FIFO/HID unverified.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/TOUCH-015-FIX.md)
  Command: <code>python tools/test-venus-pooldiag.py --image G:/UniXNU-Port/artifacts/venus-touch-015/phone/boot-venus-unixnu.img --sha256 92018c0fe7793fffca2e8c8e0dd23f91f5e5ac05f21fe17100fc871bec42eb45 --log G:/UniXNU-Port/logs/venus-touch-015-phone.txt --adb-port 5037</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `device`: [User confirms015 welcome UI but no tap/scroll. Authorized readonly capture169934pages/91runs/696582144B including metadata, checkpoint1115/stable/SHA/coverage; exact015 launchd args and IOHIDInterface string found. No hardware chip/GENI state inferred from absent logs.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/TOUCH-017.md)
  Command: <code>python scripts/collect-data-forensics.py --read-android --max-bytes 1073741824; python scripts/record-touch015-review.py</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `host`: [Actual original page13 matching lives in omitted codeless IOHIDEventDriverSafeBoot. Before:311timer ticks/onlyInterface/report0. After:originalEventDriver/ready1/reports3/status0 with QEMU-only producer and production-identical HID/codec objects. Report actual APFS write/pread/full/dirsync/env pass; mediumEIO retained without UFS. Mode1 never qualified HID registration.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/TOUCH-017.md)
  Command: <code>python scripts/inspect-venus-hid-personalities.py; python3 scripts/check-venus-hid-report-qemu.py --kernel-dir artifacts/venus-metal-touch/kernel-link-10 --output artifacts/venus-st-touch/qemu-hid-matching; python3 scripts/check-st-startup-report-qemu.py</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `host`: [017 f9937cf5.../a1701917... compiled with real backend plus original codeless matching and exclusive protected prelaunchd report. Production defaultoffSystemOS/6GiB/AKS/HID, APFS report and FAT/FD/EFI/roundtrip pass. No new phone boot yet.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/TOUCH-017.md)
  Command: <code>python3 scripts/prepare-venus-metal-touch-phone.py --kind touch --version 017 --kernel-dir /mnt/g/UniXNU-Port/artifacts/venus-metal-touch/kernel-link-11 --qemu-name qemu-touch017-default-off; python3 scripts/prepare-venus-metal-touch-phone.py --kind touch --version 017 --kernel-dir /mnt/g/UniXNU-Port/artifacts/venus-metal-touch/kernel-link-11 --qemu-name qemu-touch017-default-off --check</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `device`: [User confirmed exact017 plus protected startup.jsonl directory/file/readback/sync and015 ST hardware scope.venus/55870427 matched; one RAM boot Sending4.350s/Booting0.193s OKAY total4.602s. Authorization consumed; physical touch and startup state await observation/readback.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/TOUCH-017.md)
  Command: <code>python tools/test-venus-pooldiag.py --image G:/UniXNU-Port/artifacts/venus-touch-017/phone/boot-venus-unixnu.img --sha256 f9937cf513b2f455953b36380110969a9b66975878f3a4da31b02a414ac4a230 --log G:/UniXNU-Port/logs/venus-touch-017-phone.txt --adb-port 5037</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `device`: [Authorized readonly capture171115pages/93runs/701419520B including two metadata reads, checkpoint1159/stable/SHA/coverage. Exact017 startup report362B: stage5/status-19/chip\_id0/transfer0/cs0/fifo\_disabled0; HID match/meta/start/ready1/reports0. HID works; first failure is ST identify ID0, not HID/UIKit.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/TOUCH-017.md)
  Command: <code>python scripts/collect-data-forensics.py --read-android --max-bytes 1073741824; python scripts/collect-data-forensics.py --offline G:/UniXNU-Port/artifacts/venus-data-forensics/read-20261029T192825Z</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `source`: [Official staged GENI path uses geni\_spi\_transfer\(keep\_cs=0\), no manual CS opcode; FIFO-disabled boards need SMMU DMA but Venus reports fifo\_disabled0; Sheng S4 DFS/GPLL0 differs from Venus active XO/SE11 clock. Used to align018 CS/reset/retry, not copy touch geometry.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/TOUCH-018.md)
  Command: <code>Read https://github.com/UniXNU/UniXNU-sheng package/TouchProbe.cpp and TouchBoard.h at08cde20 plus official porting docs</code>. Revision: `08cde20edc3254ed6f7df8d0f5384fb887786e8f`.
- `host`: [018 image43b57431.../kernelb5d81d5b... changes CS to controller-managed,300ms reset,8ID retries,SALIXP0x4036/FTB0x3936,018 report. FAT/ADT/trust/FD/EFI/roundtrip/--check pass; QEMU018 not run because OS.raw/SystemOS.raw lost in workspace cleanup, so no QEMU pass claimed. Phone untested.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/TOUCH-018.md)
  Command: <code>python3 scripts/build-venus-st-touch.py --output artifacts/venus-st-touch/production-018 --startup-report --build-tag touch-018 --report-dir /private/var/db/venus-st-018; python3 scripts/link-venus-metal-touch-kernel.py --attempt 12 --touch-build artifacts/venus-st-touch/production-018; python3 scripts/prelink-mg-task-kernel.py --directory artifacts/venus-metal-touch/kernel-link-12 --hid-touch; python3 scripts/prepare-venus-metal-touch-phone.py --kind touch --version 018 --kernel-dir artifacts/venus-metal-touch/kernel-link-12 --skip-qemu; ... --check</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `device`: [Exact018 image/018 protected report/ST CS-reset-retry scope approved.venus/55870427 matched; one RAM boot Sending4.339s/Booting0.192s OKAY total4.588s. Physical touch unavailable; startup report still stage5/chip\_id0.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/TOUCH-018.md)
  Command: <code>python tools/test-venus-pooldiag.py --image G:/UniXNU-Port/artifacts/venus-touch-018/phone/boot-venus-unixnu.img --sha256 43b574316bfeae5212bf0fee0db576c90b9632aa1ead9610aab3a5487045b531 --log G:/UniXNU-Port/logs/venus-touch-018-phone.txt --adb-port 5037</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `device`: [Authorized readonly172832pages/91runs/708452352B including two metadata reads, checkpoint1204/stable/SHA/coverage.018 report392B stage5/status-19/chip\_id0/messages8/id\_attempts8/transfer0/cs0/cs\_manual0/fifo\_disabled0/HIDready1. Controller CS/reset/retry did not fix ID0.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/TOUCH-018.md)
  Command: <code>python scripts/collect-data-forensics.py --read-android --max-bytes 1073741824; python scripts/collect-data-forensics.py --offline G:/UniXNU-Port/artifacts/venus-data-forensics/read-20261030T014937Z</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `host`: [019 imagec7f4e46a.../kernel138ec757... adds GENI MOSI-&gt;MISO loopback and TLMM input enable, keeps controller CS/300ms/8 retries. FAT/ADT/trust/FD/EFI/roundtrip/--check pass; QEMU not run because OS.raw/SystemOS.raw lost, no QEMU claim.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/TOUCH-019.md)
  Command: <code>python3 scripts/build-venus-st-touch.py --output artifacts/venus-st-touch/production-019 --startup-report --build-tag touch-019 --report-dir /private/var/db/venus-st-019; python3 scripts/link-venus-metal-touch-kernel.py --attempt 13 --touch-build artifacts/venus-st-touch/production-019; python3 scripts/prelink-mg-task-kernel.py --directory artifacts/venus-metal-touch/kernel-link-13 --hid-touch; python3 scripts/prepare-venus-metal-touch-phone.py --kind touch --version 019 --kernel-dir artifacts/venus-metal-touch/kernel-link-13 --skip-qemu; ... --check</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `device`: [Exact019 image/loopback/input-enable/019 report scope approved.venus/55870427 matched; one RAM boot Sending4.334s/Booting0.193s OKAY total4.569s. Authorization consumed; loopback/ID and welcome-page touch await interaction/readback.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/TOUCH-019.md)
  Command: <code>python tools/test-venus-pooldiag.py --image G:/UniXNU-Port/artifacts/venus-touch-019/phone/boot-venus-unixnu.img --sha256 c7f4e46af15fe8dbc72fd3ea4110c3c564b5a8ba9d2b05645c7f7c279f1873a2 --log G:/UniXNU-Port/logs/venus-touch-019-phone.txt --adb-port 5037</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.

## Diagnostics {#diagnostics}

`implemented`

### Hardware and dependencies

- Legacy image hashes, screen observations and RAM-boot transcripts
- Official guide sequence and matching profile/firmware logs

### Configuration

- tools=true, timeout=5, panic\_screen=true; no automatic reset selected in board.toml

### Procedure

- Save source/configuration and image hashes; observe one checkpoint at a time
- Integrate Advanced Logger before persistent kernel logging, which depends on storage

### Development findings

- Historical stage and photo records are preserved; latest corrections in MG-QUERY-OBSERVATION.md
- The cache was incorrectly read at allocation length8192; actual DSTREAM EOF7477 yields a valid plist. Cached MainScreenStaticInfo.scale0 and oldP3 artwork answers match across three captures
- XNU parses plane prefix only with planeNULL; earlier DT0 never established an ADT root placement defect, and the later property2 is not an MG API return
- Legacy raw tracev3 scans decoded no chunks and lacked boot UUID/PID attribution; file names/object addresses cannot prove which phone run logged a failure
- Actual MG API helper reports default1/2/7 returns, copied static-info bytes, IOKit properties and boot UUID to one file; no repeated photo sequence required
- User-supplied haydn pin confirms similar virtual-timer workaround and offers UART/SPI resource organization; it has no lockscreen evidence and refusal-only owner policies

### Completion criteria

- Each claimed stage has source/image identity and readable logs or explicit observations

### Current limits

- Local overlays have no published revision; QR exporter runtime and persistent XNU logging remain unverified
- UFS survey intentionally uses the existing panic renderer to stop with read-only register results
- The CRASH formatter's 100-character chunks can split an address across rows; the photo transcription is manual and the local-symbols LZFSE stream was not decoded.

### Next action

- 019 booted once; await loopback/ID and welcome-page feedback. If loop\_match1 and ID0, inspect PM8350C L2/L3 vdd/avdd; if loop\_match0, fix GENI/pins
- Metal016 \(82d3b33e\) supersedes013; actual Metal discovery/GPU rendering unverified.012 welcome baseline retained
- New Data capture requires manual Android return/readonly scope with explicit1GiB bound; no reset/flash/automatic device retry.

### Evidence

- `source`: [Legacy probe implementation, hashes, transcript and user observation recorded](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/VM-INIT-PROBE.md)
- `device`: [Photo and image hashes recorded; BootProgress fields show root acceptance/userspace, 1024 MiB and 1932 free4K pages. SpringBoard has three retained signal5 exits; screenshot alone does not diagnose their cause or prove continuing liveness.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/LEGACY-MIGRATION.md)
  Command: <code>Inspect G:/b9ee504f-ad12-4660-99fe-99e561d41472~1.jpg against package/boot-progress/BootProgress.c and the exact-image RAM-boot transcript</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `host`: [Actual fault formatter and ordinary-page layout pass ASan/UBSan; source receipts and executable kernel symbols match. 1 GiB candidate preserves control ADT/Data/trust/args/firmware and reaches real QEMU owner-root acceptance on read-only host disks. New phone execution and SpringBoard diagnosis remain pending.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/SPRINGBOARD-FAULT-DIAGNOSTICS.md)
  Command: <code>python3 scripts/check-boot-fault-screen.py; python3 scripts/prepare-venus-exit-fault.py</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.
- `device`: [Authorized 32e385b5 run: SpringBoard p149 EL0 BRK, root=1, 1024 MiB, UFS failures0/integrity0. The photographed PC is not a BRK instruction in the matching cache, so image names are provisional; no retry was performed.](https://github.com/Sulee7z/UniXNU-venus/blob/9b1402a99d9ee37d8aa4a980eceff18a4c993e02/SPRINGBOARD-FAULT-DIAGNOSTICS.md)
  Command: <code>fastboot -s 55870427 boot G:/UniXNU-Port/artifacts/venus-exit-fault/phone/boot-venus-unixnu.img; inspect G:/43ae1a26-abd0-4064-90a3-ccc6d3726c72~1.jpg</code>. Revision: `8d157ee18ae9c4d518aba28cb3040a84e860dcd1`.

</div>
