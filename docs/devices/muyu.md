# Xiaomi Pad 7 Pro

[yehua123-oos/UniXNU-muyu](https://github.com/yehua123-oos/UniXNU-muyu)

<div v-pre>

Muyu, iPadOS 27.0.1 \(24A446\) line as the repository's official format 2 board: payload reaches APFS SystemCryptex mount and owner-cache enumeration \(panel photo 2026-11-08 14:36\); the panel is the only log channel — USB CDC ACM \(blocked at DEPCFG, 16 probes accepted / 0 executed\) and the Linux pstore/init\_boot-reader were abandoned 2026-11-08 and their code removed the same day \(docs/ABANDONED-CHANNELS.md\); device restored to stock 2026-11-08 16:18 with no recorded reason. 17-line desktop \(CPU-composed \~1.4 fps\) predates this ledger. GMU cold start + full HFI device-verified 2026-10-30; GX rail blocked; GPU paused since 2026-11-02. The 17.7.11 \(21H461\) line boots to a CPU-composed desktop \(\~1.4 fps\) and is archived at tag line-ipados-17 \(docs/IPADOS17-ARCHIVE.md\). See docs/HANDOFF-2026-11-08.md and STATUS.md.

Source record: [porting.toml](https://github.com/yehua123-oos/UniXNU-muyu/blob/5e99d2b16421b469a9961ec872d74ab4466f97b8/porting.toml), `5e99d2b16421b469a9961ec872d74ab4466f97b8`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `host-verified` |
| [Firmware and boot](#firmware) | `implemented` |
| [CPU and interrupts](#cpu) | `implemented` |
| [Memory and DMA](#memory) | `planned` |
| [Storage and root](#storage) | `device-verified` |
| [Display](#display) | `device-verified` |
| [Input](#input) | `device-verified` |
| [GPU](#gpu) | `implemented` |
| [Network](#network) | `not-applicable` |
| [Audio](#audio) | `not-applicable` |
| [Power](#power) | `host-verified` |
| [Image assembly](#packaging) | `implemented` |
| [Diagnostics](#diagnostics) | `device-verified` |

## Configuration {#configuration}

`host-verified`

Components: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`.

### Hardware and dependencies

- board.toml is the board \(schema\_version = 2, soc\_source = sm7675, os\_profile = ipados-27.0.1-24A446\). It is the only board file in the repository; the 17 line is the tag line-ipados-17.
- The SoC layer is pinned in feeds.toml \(kind = "soc", name = sm7675\) at 7f857a8, and unixnu.lock records the same commit, so the two cannot drift.
- 24A446 kernelcache sha256 38e6d9fa5f789b82... — the same OS-profile member the uke line prelinks against \(kernel.json inputs.kernelcache\_sha256\).
- Framework: the ../UniXNU checkout \(one framework, upstream main merged plus the 27-line commits\), output under out/muyu/ipados-27.0.1-24A446/muyu-userland/.

### Configuration

- schema\_version = 2, SM8635 device on the sm7675 24A446 OS profile, muyu kit. Patch series is four layers, the shape UniXNU-uke uses: arch:patches/xnu/series \(64\) + soc:patches/xnu-12377/series \(2: sheng-platform-power, native-smp-secondary\) + os:patches/xnu/series \(4\) + device:patches/xnu-27/series \(4\) = 74. unixnu status --json prints the resolved order, and scripts/audit-27-config.py fails if its own count differs.
- 105-token boot config identical across u150-u157; u158/u159 drop exactly muyu\_usb=1 muyu\_usb\_panic=1.

### Procedure

- cd UniXNU; ./unixnu build kernel -D ../UniXNU-muyu; ./unixnu build payload -D ../UniXNU-muyu --data-ramdisk fw/data-seed.img --trust-cache fw/trust-24A446/24A446-original-trust.bundle
- python3 UniXNU-muyu/scripts/patch-vendor-boot.py --base /tmp/vendor\_boot\_base\_96m.img --payload &lt;out&gt;/payload/payload.img --output fw/vendor\_boot\_27-uNNN.img

### Development findings

- The repository builds the 27 line from a clean checkout since 2026-11-08 22:30. Before that the 27-line config lived only in a temp tree, then in a second board file that had to be copied over board.toml; the board was promoted in place and the temp path is no longer a build input.
- u152-u159 kernel version strings all read '\(u151\)': the device source was not bumped after u151; multi-MB image diffs between rounds are consistent with LTO/layout churn plus payload repack, and the u157-&gt;u158 delta is exactly 989 bytes \(FAT timestamps, random-seed, boot-args region\).
- Last build \(16:13\) reports mapping\_complete=false, runtime\_qualified=false, loadable=false, allow\_missing=true, missing AppleARMWatchdogTimer + IOHIDFamily, 26 stub sites, Image4 personality dropped; it was flashed anyway \(u159\) with no recorded decision.
- CLEANUP 2026-11-08 21:20, restructured 22:05, format 2 22:30 \(maintainer: 'the 27 line is many AIs handing over, keep it clean', then 'follow the 17 line structure', then 'the repository is not in the official format'\). The 27 line could not build itself from this repo, and four smaller faults hid behind that. \(1\) The series was declared by the board and here, but had never been committed; patches.py does not glob and does not fall back — it raises 'patch series missing' and stops — so every u-round was built from a temp tree whose copy of the file existed only there. \(2\) That recovered file pasted the framework patches in as 67 absolute paths plus 5 device patches \(72\). It has been replaced by the layered form the framework and uke actually use — arch/soc/os/device, each resolved into its own checkout — so the device layer is now only patches/xnu-27/series and nothing in it can fall out of step with the framework. \(3\) The two lines shared one patch directory, and a schema\_version 1 board globs patches/xnu/\*.patch: the 27 line's 4 patches were being applied to 17-line kernels, and a 17-line patch parked in a backlog/ subdirectory was silently dropped from them. Split now — patches/xnu/ = 17 line \(16 patches, archived with tag line-ipados-17\), patches/xnu-27/ = 27 line \(4 patches, listed\) — and scripts/audit-27-config.py fails if the two overlap or if the series and its directory disagree. \(4\) native-source-storage=1, -bravearkdeferredconsole and muyu-ignition-trace=1 had no parser in any checkout; the first two are uke's names \(-ukedeferredconsole / uke-ignition-trace\) and for ignition u44's sysctl two-liner only ever existed in the temp tree, so IPADOS27-MIGRATION §6.58.2 is not reproducible from here. All three are comments now. \(5\) configs/muyu-27-defconfig never existed; the board names configs/muyu-userland\_defconfig. \(6\) The SoC layer was documented as one patch from a private sm8635 repository while the board actually resolved sm7675 through feeds.toml; the audit now reads soc\_source and the count is 2, not 1.
- FRAMEWORK CONSOLIDATION 2026-11-08 22:40, which resolves the deviation recorded at 21:40: the 16:12 build resolved its compatibility patches through the core UniXNU checkout while this record said UniXNU-27, and the two had drifted \(offline-owner-boot-manifest, offline-owner-systemos-mount, zzz-boot-progress differ\). The fork was unshallowed, merged onto upstream f924843, and the eight 27-line commits that existed only in the old clone were merged in on top, so ../UniXNU is now the one framework for both lines. The old clone is frozen as a reference; the porting audit reports a single checkout and cross-checks its patch count against unixnu status --json.

### Completion criteria

- defconfig/kernel/payload build completes and the prelinked MH\_FILESET kernel.macho is produced; boot config embedded in the payload is machine-readable from the images.

### Current limits

- No manifest/hash verification of the packed image \(uke's release/verify step is not used\). The unqualified-final-build policy is undocumented.

### Next action

- Record why the 16:13 unqualified build was flashed; decide a policy for loadable=false candidates; keep board.toml the single board file \(the 17 line is a tag, not a second board\).

### Evidence

- `host`: [u158 = u157 + 989 bytes: FAT timestamps + chosen random-seed + boot-args region removing muyu\_usb/muyu\_usb\_panic; recorded images fw/vendor\_boot\_27-u157.img 27507b1e... / u158 0bf6ba5f... \[§3\]](https://github.com/yehua123-oos/UniXNU-muyu/blob/5e99d2b16421b469a9961ec872d74ab4466f97b8/docs/HANDOFF-2026-11-08.md)
  Command: <code>python3 diff-clusters vendor_boot_27-u157.img vendor_boot_27-u158.img</code>. Revision: `714179fd56cf909e3725e9c6681eb76fa253075b`.
- `host`: [kernelcache\_sha256 38e6d9fa... equals the uke-recorded 24A446 member; candidate 95,764,480 B sha256 7b083c24..., loadable=false; recorded 2026-11-08 16:13 build \[artefact: kernel/kernel.json\]](https://github.com/yehua123-oos/UniXNU-muyu/blob/5e99d2b16421b469a9961ec872d74ab4466f97b8/docs/HANDOFF-2026-11-08.md)
  Command: <code>cat out/muyu/ipados-27.0.1-24A446/muyu-userland/kernel/kernel.json</code>. Revision: `0000000000000000000000000000000000000000`.
- `source`: [format 2 board promoted in place: schema\_version = 2, soc\_source = sm7675, os\_profile = ipados-27.0.1-24A446, four-layer patch\_series](https://github.com/yehua123-oos/UniXNU-muyu/blob/5e99d2b16421b469a9961ec872d74ab4466f97b8/board.toml)

## Firmware and boot {#firmware}

`implemented`

Components: `DarwinBoot`, `Mu-Silicium`.

### Hardware and dependencies

- Mu-Silicium UEFI fd packed into boot.img \(2.1 MB\), built 2026-11-05 and reused since.
- Stock vendor\_boot template \(/tmp/vendor\_boot\_base\_96m.img\) patched with the payload ramdisk.

### Configuration

- boot partition carries the UEFI fd; vendor\_boot carries the XNU payload via patch-vendor-boot.py; ABL boots the init\_boot ramdisk \(stock Android\) — see diagnostics.

### Procedure

- tools/muyu-flash-mode.sh xnu fw/vendor\_boot\_27-uNNN.img \(preflight + flash vendor\_boot + fastboot boot boot.img, all ledgered\)

### Development findings

- The vendor\_boot patch pipeline has been exercised hundreds of times per the ledger \(2651 rows\) without a packaging failure.
- The EDK2/UEFI artifact is a 2026-11-05 build not regenerated by the current flow; UniXNU/out deletion would lose it \(UKE-FULL-WALKTHROUGH §5, unchanged\).

### Completion criteria

- UEFI menu boots the payload entry from vendor\_boot on this device.

### Current limits

- UEFI firmware itself is not rebuilt by the current flow; no verify step; 'firmware' here means the boot path, not a re-qualified FD build.

### Next action

- Regenerate boot.img from Mu-Silicium sources once, record its sha, and add it to the ledger as a build step rather than a reused artifact.

### Evidence

- `device`: [hundreds of preflight+flash vendor\_boot+boot rows with rc=0 through 2026-11-08; recorded u159 2026-11-08T08:14:20Z \[artefact: logs/flash-ledger.tsv\]](https://github.com/yehua123-oos/UniXNU-muyu/blob/5e99d2b16421b469a9961ec872d74ab4466f97b8/docs/HANDOFF-2026-11-08.md)
  Command: <code>grep -c preflight logs/flash-ledger.tsv</code>. Revision: `714179fd56cf909e3725e9c6681eb76fa253075b`.

## CPU and interrupts {#cpu}

`implemented`

Components: `ArmCpu`.

### Hardware and dependencies

- Boot args sheng-smp=0 armcpu-spi-ipi=0 \(present in every u150-u159 image\).

### Configuration

- Single-CPU runs; the SPI-IPI path and the SMP-enable isolation experiment from the uke audit \(§4\) have not been executed on muyu.

### Procedure

- Flash any u15x image; the panel log shows the scheduler running single-core.

### Development findings

- UKE-CODE-AUDIT.md §4 records that uke treats single-CPU as a bisect fallback, not a target, and fixed SMP with the SPI-IPI path; muyu has both args off and never ran the 'smp on, spi-ipi off' isolation.

### Completion criteria

- Single-CPU boots are stable enough to reach APFS/owner-cache stages.

### Current limits

- No multi-core run on the 27 line; no SMP stability data on this SoC for 24A446.

### Next action

- Run the one isolation experiment \(smp=1, spi-ipi=0\) once the observability channel is trustworthy.

### Evidence

- `host`: [args contain sheng-smp=0 armcpu-spi-ipi=0; recorded u159 \[artefact: fw/vendor\_boot\_27-u159.img\]](https://github.com/yehua123-oos/UniXNU-muyu/blob/5e99d2b16421b469a9961ec872d74ab4466f97b8/docs/HANDOFF-2026-11-08.md)
  Command: <code>extract boot-config TOML from the payload</code>. Revision: `714179fd56cf909e3725e9c6681eb76fa253075b`.

## Memory and DMA {#memory}

`planned`

Components: `ArmDTPlatform`.

### Hardware and dependencies

- board.toml \[kernel.prelink\] carries owned\_memory\_size = 0x130000000 \(4.75 GiB\) and dram\_size = 0x80000000, the SMEM RAM table value read from the device.
- Boot arg kt\_fixed\_zones=120 in the active config; no bank map, no jetsam or zone-growth observation has been recorded for either line.

### Configuration

- The kernel is given one owned-memory window; the rest of the physical map is governed by the device tree the payload generator compiles from dts/muyu.dts.

### Procedure

- Build the payload, boot, and read the owned-memory figure the kernel prints next to the page-table setup; compare it with 0x130000000.

### Development findings

- Nothing is measured. The 17 line boots with this window, which says the inherited braveark SM8635 layout is not obviously wrong, not that it is qualified.
- The 3 GiB and 2 GiB windows were tried on the 17 line and neither fixed the boot-task timeout \(board.toml comment next to owned\_memory\_size\); the window was returned to 4.75 GiB without a memory-side explanation.

### Completion criteria

- The owned-memory window the kernel reports equals the board's value on the 27 line, and one boot records the page-table size it implies.

### Current limits

- No owned-memory figure, no bank map check and no jetsam observation on the 27 line: this area is planned, not implemented.

### Next action

- Take the owned-memory line off the first trustworthy screen capture once the screen channel is re-planted \(docs/SCREEN-ONLY.md §4\), then record it here with the commit it was read at.

### Evidence

Collect evidence using the next action.

## Storage and root {#storage}

`device-verified`

Components: `ShengUfs`, `RamBlock`, `VirtioMmioBlock`, `VerifiedRoot`, `AppleKeyStoreState`, `SoftwareAES`.

### Hardware and dependencies

- SHNGROOT container on userdata: windows OS + SystemOS \(sparse images fw/userdata-root-preboot\*.sparse, 8.74-15.2 GiB variants, five flashes 2026-11-03..11-06 per ledger\).
- Persistent Data: packed\_data\_ramdisk/persistent\_data/sheng-data-persist=2; data-seed.img \(DBRDISK1, 1.04 MiB\) is only the first-boot seed.
- 24A446 trust cache bundle fw/trust-24A446/24A446-original-trust.bundle.

### Configuration

- native-ufs-allow-unverified=1 native-ufs-diagnostics=1 native-ufs-smmu-takeover=1 muyu-source-storage=1 native-ufs-root=1 \(all rounds u150-u159\). Note: native-source-storage=1 sat in this list by mistake and was dropped 2026-11-08 — that is uke's name, this repo's SourceStorage.cpp gates on muyu-source-storage. See docs/IPADOS27-MIGRATION.md §6.47.

### Procedure

- Flash userdata-root sparse + vendor\_boot; boot; read panel log; for persistence, reboot with sheng-data-persist=2 and compare page counts.

### Development findings

- Panel 2026-11-08 14:36 \(u155\): NativeUfs OS volume ready; apfs mounts Rave24A446...SystemCryptex requested by init \(pid 1\), vol-uuid F7914C52..., 4096x1465320 unencrypted; stable checkpoint indices desc 6 data 14 — the cryptex mount path works on hardware.
- Owner-cache enumeration reaches the dyld\_shared\_cache\_arm64e file list under /System/Library/Caches and /System/Cryptexes/OS \(probe/composed 0/0 — files listed, contents not yet composed\).
- Data persistence proven across boots on the 27 line \(HANDOFF-2026-11-07 §17-§25\): u102 d=7 \(Data doomed read-only with default layout\), u103 reset=1 makes Data writable \(Fresh, 91 pages, 0 errors\), u110 store Resumed 91-&gt;147 pages; limits: Data cannot be both the cryptex staging layer and /private/var \(IPADOS27-MIGRATION.md\).
- The 21H461 line used the same SHNGROOT container on device \(fw/userdata-root-preboot.sparse inspected: magic SHNGROOT, version 1, 2 windows\).

### Completion criteria

- OS/SystemOS windows authenticate, APFS mounts the SystemCryptex, Data persists across reboots when reset=1 is used.

### Current limits

- Cryptex contents not yet composed into the owner cache \(0/0\); Data-only-read-only tension with cryptex staging unresolved.

### Next action

- Compose the owner cache from the enumerated cryptex files; keep the Data layout decision \(reset policy\) explicit per boot.

### Evidence

- `device`: [panel shows NativeUfs OS volume ready + apfs mount of SystemCryptex + owner-cache enumeration; recorded u155, flashed 2026-11-08T06:35:19Z \[artefact: logs/2026-11-08-14-36-26-878.jpg\]](https://github.com/yehua123-oos/UniXNU-muyu/blob/5e99d2b16421b469a9961ec872d74ab4466f97b8/docs/HANDOFF-2026-11-08.md)
  Command: <code>photo transcription in docs/HANDOFF-2026-11-08.md §5</code>. Revision: `714179fd56cf909e3725e9c6681eb76fa253075b`.
- `device`: [u110: store Resumed across boot, 91-&gt;147 pages, boot reached dirs\_cleaner; recorded u110 2026-11-07 \[§25\]](https://github.com/yehua123-oos/UniXNU-muyu/blob/5e99d2b16421b469a9961ec872d74ab4466f97b8/docs/HANDOFF-2026-11-07.md)
  Command: <code>flash fw/vendor_boot_27-u110-family image</code>. Revision: `714179fd56cf909e3725e9c6681eb76fa253075b`.

## Display {#display}

`device-verified`

Components: `GopFramebuffer`.

### Hardware and dependencies

- UEFI GOP framebuffer; the panel is the primary readout channel \(no UART, and the USB console was removed 2026-11-08\).

### Configuration

- sheng-vsync=60; framebuffer log pages \(u143-u148 line: 28-row and later 56-row full-screen pages, version+command-engine state pinned into the last line\).

### Procedure

- Boot a u15x image; photograph the panel; images carry the round tag in their banner line \(MUYU USB\(uNNN\) / MUYU uNNN TABLE\).

### Development findings

- The framebuffer readout method is established: u143 moved state onto the panel, u148 made the whole screen a 56-row log page so one photo captures full context; u155 photo shows the full boot state including APFS and owner-cache lines.
- The 21H461 line reached the desktop with CPU composition at \~1.4 fps \(STATUS.md\); no GPU composition on either line.
- Exec-path printf is dropped by the panel: diagnostics must be printed before panic or baked into panic text \(HANDOFF-2026-11-07 §7 note\).

### Completion criteria

- Boot state is observable end-to-end via panel photographs at 60 Hz vsync, no extra hardware.

### Current limits

- CPU composition only; no DPU direct scanout, no GPU compositor on the 27 line; panel drops exec-path prints.

### Next action

- Keep the readout format; paint the previous panic as the first boot screen \(docs/SCREEN-ONLY.md §4, BravearkLastLog replay\) so panics before video are not lost. The pstore line-dump was the other candidate and is abandoned.

### Evidence

- `device`: [full-screen 56-row readout with round tag u155; recorded u155 \[artefact: logs/2026-11-08-14-36-26-878.jpg\]](https://github.com/yehua123-oos/UniXNU-muyu/blob/5e99d2b16421b469a9961ec872d74ab4466f97b8/docs/HANDOFF-2026-11-08.md)
  Command: <code>photograph after flash</code>. Revision: `714179fd56cf909e3725e9c6681eb76fa253075b`.

## Input {#input}

`device-verified`

Components: `ShengNovatekTouch`, `ShengHidInput`.

### Hardware and dependencies

- Novatek touch controller on GENI SPI 0xa90000 \(NVT-ts-spi\); physical buttons.

### Configuration

- muyu-touch-drv=1 muyu-touch-quiet=1 sheng-touch-hid=1 muyu-buttons=1 \(active in all u15x rounds\).

### Procedure

- Boot with muyu-touch-drv=1; use the touch screen on the 21H461 desktop.

### Development findings

- Touch works as native IOServices and buttons work on the 21H461 line \(STATUS.md, verified earlier in October; docs/TOUCH-PORT.md is 94 KB of probe history\).
- HID warning carried from uke applies: without sheng-touch-split the composite keyboard collection publishes first and backboardd drops digitizer events.

### Completion criteria

- Touch and buttons produce events into IOHIDFamily on the 17-line desktop.

### Current limits

- No touch interaction has been demonstrated on the 27 line \(userland never reached a UI there\).

### Next action

- Re-verify touch on the 27 line once userland reaches backboardd.

### Evidence

- `device`: [Novatek touch \(muyu-touch-drv=1\) works as native IOService; physical buttons work; recorded 21H461 line](https://github.com/yehua123-oos/UniXNU-muyu/blob/5e99d2b16421b469a9961ec872d74ab4466f97b8/STATUS.md)
  Command: <code>on-device use, October sessions</code>. Revision: `714179fd56cf909e3725e9c6681eb76fa253075b`.

## GPU {#gpu}

`implemented`

Components: `Adreno740`, `AdrenoPM4`, `AdrenoFirmware`.

### Hardware and dependencies

- GMU firmware chip id 0x070b0000 recovered from the CM3 image \(catalog formula gives 0x4303b000, rejected FW\_INIT\_RESULT=0x901\).
- Board OPP/BCM policy generated from the device's own downstream devicetree, 11 GPU levels 1100-&gt;255 MHz.
- GPU SMMU identity 24 SMR / 22 CB; GMU stage-1 context bank 2, SID 5; five GMU memory blocks + A735 firmware staged with SHA verified.

### Configuration

- Probe modes 1-17 in docs/GPU-PROBE-RUNBOOK.md; probe mode 17 = RPMh RSC ACTIVE TCS transfer with both ARC votes \(gfx.lvl sel 0x10, mxc.lvl sel 0x30\).

### Procedure

- docs/GPU-PROBE-RUNBOOK.md §11-§13; host gate scripts/check-muyu-rpmh-host.py before flashing.

### Development findings

- GMU cold start + full HFI startup device-verified 2026-10-30, repeated every probe run: cold=0 ph=7 proto=0 fw=0x00000100 hfi=0x00000001.
- GX rail blocker: gpu\_cc\_gx\_gdsc is a support-cfg GDSC; CFG\_GDSCR \(0x9038\) bit16 never sets \(cfg=0x050e0000\); parent supply is the RPMh ARC voter pm\_v6c\_s6\_gfx\_voter\_level; the OOB GPU\_SET handshake gets no ACK, consistent with GX unavailable. gx\_clkctl\_gx\_gdsc is DT-disabled, not the missing piece.
- MuyuRpmhRsc sender written and host-tested \(probe 17 + host tests\); flashing done per STATUS.md but the on-device panic readout was never collected.
- GPU work paused since 2026-11-02 by maintainer decision; the register tables and probe modes remain in-repo.
- This SoC is NOT SM8550/SM8650 register compatible; DT GDSC node names are leftovers \(GPU-CLIFFS-MMIO.md\).

### Completion criteria

- GMU firmware runs and answers HFI on hardware; nothing past GX power has been attempted.

### Current limits

- No CP, no command submission, no Metal on muyu; ACD and IFPC off; ShengGmu poll caps at 10 ms; GPLL0 GPU vote does not stick.

### Next action

- GPU stays paused; if resumed, first collect the probe-17 on-device readout that is still owed.

### Evidence

- `device`: [cold=0 ph=7 proto=0 fw=0x00000100 hfi=0x00000001, repeated every run; recorded 2026-10-30 \[§11\]](https://github.com/yehua123-oos/UniXNU-muyu/blob/5e99d2b16421b469a9961ec872d74ab4466f97b8/docs/GPU-PROBE-RUNBOOK.md)
  Command: <code>probe modes 7-11 with the GPU probe images</code>. Revision: `714179fd56cf909e3725e9c6681eb76fa253075b`.
- `host`: [CFG\_GDSCR bit16 never sets; parent is RPMh ARC voter; RSC sender host-tested; recorded probe 17 \[§12 + STATUS.md\]](https://github.com/yehua123-oos/UniXNU-muyu/blob/5e99d2b16421b469a9961ec872d74ab4466f97b8/docs/GPU-PROBE-RUNBOOK.md)
  Command: <code>python3 scripts/check-muyu-rpmh-host.py</code>. Revision: `714179fd56cf909e3725e9c6681eb76fa253075b`.

## Network {#network}

`not-applicable`

### Hardware and dependencies

- No Wi-Fi, Bluetooth or modem component is selected in board.toml \[components\]; the SM7675 SoC layer ships none either.

### Configuration

- Nothing to configure: \[components\] include has no Ath12kWifi \(or any other network\) entry, so no driver is built and no firmware is listed in proprietary-files.txt.

### Procedure

- Nothing to run. Adding network means selecting the component, adding its firmware to proprietary-files.txt and recording the result here, in that order.

### Development findings

- No network work on either line; Wi-Fi was only ever a uke-side topic \(uke branch fix/wifi-apple-cache-20261108\).

### Completion criteria

- Not-applicable for this port as published: the area becomes applicable the day a network component is selected.

### Current limits

- No intent to bring network up in the current spike; the not-applicable status is a decision, not a gap.

### Next action

- Keep it out of the board until the boot path is stable; revisit after the owner cache composes.

### Evidence

Collect evidence using the next action.

## Audio {#audio}

`not-applicable`

### Hardware and dependencies

- No audio component is selected in board.toml \[components\], and the 24A446 profile ships no audio kext for this SoC.

### Configuration

- Nothing to configure: no codec, no I2S/SoundWire controller and no audio firmware in proprietary-files.txt.

### Procedure

- Nothing to run. Enabling audio means a component entry, its firmware and a recorded device result, in that order.

### Development findings

- No audio work on either line; uke records the same not-applicable.

### Completion criteria

- Not-applicable for this port as published.

### Current limits

- Out of scope for the current spike; the limitation is scope, not hardware evidence.

### Next action

- Revisit only after display and storage reach a stable desktop.

### Evidence

Collect evidence using the next action.

## Power {#power}

`host-verified`

Components: `ArmCpu`.

### Hardware and dependencies

- ARC votes: gfx.lvl selector from init level 0x10, mxc.lvl from 0x30; single ACTIVE TCS transfer \(probe mode 17\).
- Thermal facts: TSENS survey built \(muyu-thermal=&lt;n&gt;\), not yet run; DT real trips 95 degC GPU, 110 degC CPU, reset-mon 115 degC.
- EPSS layout in package/CpuFreqProbe.cpp; the CPU frequency write is unvalidated on this board.

### Configuration

- wdt=-1, sheng-disable-watchdogd=1 \(both present in every u15x round\); no thermal zone, no DVFS in the running system.

### Procedure

- docs/THERMAL-PORT.md §5 runbook \(flash fw/vendor\_boot\_thermal1.img, read the THERM row\) — planned, not executed.

### Development findings

- The RPMh RSC sender passes its host tests and was flashed, but the on-device panic readout has not been collected \(STATUS.md\).
- The system currently cannot protect itself from sustained load: no thermal zone, no DVFS, watchdog disabled — this is the main line per STATUS.md, and long experiments heat the tablet.

### Completion criteria

- Host-verified: RSC transfer encoding and TSENS register map; nothing power-related is device-verified on the 27 line.

### Current limits

- No thermal policy, no throttle, no emergency action; the tablet can overheat during bring-up — keep sessions short and the charger monitored.

### Next action

- Run the read-only TSENS survey once \(thermal1 image\); it is one flash and zero risk relative to the USB work.

### Evidence

- `host`: [RSC sender host-tested; TSENS survey written and built, not run; wdt=-1 in every u15x image; recorded u159 args \[+ docs/THERMAL-PORT.md\]](https://github.com/yehua123-oos/UniXNU-muyu/blob/5e99d2b16421b469a9961ec872d74ab4466f97b8/STATUS.md)
  Command: <code>python3 scripts/check-muyu-rpmh-host.py; extract args from u159</code>. Revision: `714179fd56cf909e3725e9c6681eb76fa253075b`.

## Image assembly {#packaging}

`implemented`

Components: `XnuPrelink`, `DarwinBoot`.

### Hardware and dependencies

- Payload FAT volume with kernel.macho + ADT + trust cache + optional data seed; stock vendor\_boot template; stock init\_boot header \(used only by the reader images, since removed — docs/ABANDONED-CHANNELS.md\).

### Configuration

- Manual pipeline replaces uke's release/pack/verify: build kernel -&gt; build payload -&gt; patch-vendor-boot.py -&gt; tools/muyu-flash-mode.sh; every flash/boot/restore is ledgered with sha256 \(2651 rows\).

### Procedure

- See docs/HANDOFF-2026-11-08.md §2 for the exact per-round commands and ledger rows.

### Development findings

- The ledger discipline is real and complete back to 2026-10; sha256 per image makes any round's bytes recoverable.
- No manifest verification step; the final u159 build was flashed while the pipeline reported loadable=false \(see configuration area\).
- \[abandoned 2026-11-08\] log-reader-muyu.img \(39 MB, self-made boot header\) failed before any own code ran and the ABL fell back to recovery — measured 2026-11-08 14:59; the fix \(init\_boot-reader v4\) reused the stock init\_boot header verbatim, and then the whole channel was dropped without ever being flashed. Packing lesson kept: docs/ABANDONED-CHANNELS.md §3.

### Completion criteria

- Round-trip build-&gt;flash-&gt;ledger works and is auditable after the fact from artifacts alone.

### Current limits

- No hash verification of packed output; two pipelines \(boot=UEFI fd, vendor\_boot=payload\) with the firmware one stale since 11-05.

### Next action

- Add a post-pack sha256 manifest \(uke's release verify equivalent\) and wire boot.img regeneration into the same flow.

### Evidence

- `host`: [restore rows at 2026-11-08T08:18:44-49Z with stock shas bf68c1be.../69f1e38c.../c40dcb96...; recorded ledger head 2651 rows \[artefact: logs/flash-ledger.tsv\]](https://github.com/yehua123-oos/UniXNU-muyu/blob/5e99d2b16421b469a9961ec872d74ab4466f97b8/docs/HANDOFF-2026-11-08.md)
  Command: <code>grep restore logs/flash-ledger.tsv</code>. Revision: `714179fd56cf909e3725e9c6681eb76fa253075b`.
- `host`: [14:59 ABL-recovery fallback measured for the self-made header; stock init\_boot header adopted in v4 \(reader since removed\); recorded v4 2026-11-08 15:26; removed 2026-11-08 21:xx \[§3\]](https://github.com/yehua123-oos/UniXNU-muyu/blob/5e99d2b16421b469a9961ec872d74ab4466f97b8/docs/ABANDONED-CHANNELS.md)
  Command: <code>python3 build-initboot-reader.py --template fw/stock/init_boot.img ...</code>. Revision: `3ad15a9c23fbf73224f2ce1a827b22fa6c774028`.

## Diagnostics {#diagnostics}

`device-verified`

Components: `MuyuDebug`.

### Hardware and dependencies

- Stock kernel facts \(measured 2026-11-08\): CONFIG\_DEVTMPFS off, CONFIG\_VT off \(panel unusable from Linux\), CONFIG\_DEVMEM off, CONFIG\_PSTORE\_CONSOLE on -&gt; ramoops at 0xa7000000 readable by the XNU payload.
- DWC3 facts \(u136-u150\): GEVNTADRHI accepts the 37 GB ring \(awidth=64 real\); DEPSTARTCFG completes; DEPCFG accepted but never starts; DCTL.CSFTRST never self-clears \(u141 3000, u147 20000 tries\); reading GCC GDSCR stalls the bus \(u134\) and GDSCR is an absolute address, not base+offset \(u135\).
- ABL concatenates init\_boot ramdisk after the custom one; boot.img ramdisk is ignored \(ramdisk\_size=0\).

### Configuration

- u150-u157: muyu\_usb=1 muyu\_usb\_panic=1; u158/u159: both removed, and the arguments themselves were deleted 2026-11-08. Panel readout needs exec-path prints to be pre-panic.

### Procedure

- Panel only: boot, photograph the page, read the tag and the previous-panic replay. The USB reader \(tools/muyu-usb-log.py\) and the Linux init-boot reader no longer exist; their measured constants are archived in docs/ABANDONED-CHANNELS.md §2-§3.

### Development findings

- DECISION 2026-11-08 17:30: USB CDC ACM and the Linux-side log path \(init\_boot-reader v1-v4, pstore/ramoops\) are ABANDONED; the panel is the only output channel. Rationale: USB produced no conclusion in \~29 rounds, the Linux path was never even flashed, while the panel produced a conclusion every round since u143. See docs/SCREEN-ONLY.md.
- \[abandoned\] USB CDC ACM: \~29 rounds \(u128-u159\) without a working enumeration; final failure is DEPCFG queued-never-started with the UTMI/eUSB2 PHY apparently suspended \(ConnectSpeed reads Full-Speed while dcfg DevSpeed=0/High-Speed\); the SUSPHY clears were ordered after endpoint commands, too late for DEPCFG \(§60.3\).
- \[abandoned\] Twelve of the u136-u147 rounds measured a core that our own reset path had wedged — invalid readouts; the two effective turns were u143 \(state onto the framebuffer\) and u148 \(56-row log page\): after the observation method was fixed, three rounds reached 'only DEPCFG left'.
- \[abandoned\] The pstore/init\_boot-reader channel was built \(v3/v4\) and host-verified for header/layout only; it was never flashed or run.
- Panel readout is device-verified as THE working channel: every conclusion since u143 came from photographs of the framebuffer. Engine lives in osfmk/console/video\_console.c \(575 uncommitted lines\) and is now rescued into drivers/MuyuDebug + patches/xnu/wip/muyu-screen-wip-20261108.patch.
- Version tag discipline is broken: the round number is hardcoded per printf \(one image carries both '\(u151\)' and '\(u155\)'\), which made the 11-08 round reconstruction draw a wrong conclusion until corrected in HANDOFF-2026-11-08 §3.5.
- CORRECTION 2026-11-08 17:50 \(maintainer\): the screen capabilities were NOT missing — the iOS 17 line \(21H461\) already implemented single-source build tags \(sheng-build-tag -&gt; BootProgress.c:194,509\), auto page rotation \(BootUiTraceProbe.c page=\(seconds/8\)%pages with a 'STACK64 n/pages' label, present as a string in the flashed 17-line images\), panic replay \(BravearkLastLog.c pram FUNK printed by the next boot + ramoops ring\), crash-report rendering \(MuyuCrashLog.c, muyu-crash-\* in the flashed images\), watchdog autoreset \(sheng-autoreset\), the 48-row diagnostic page, and a dozen check-boot-\*.py validators — all archived verbatim in package/ \(= kits/muyu/ on the 27 tree\). The 27 kernel simply dropped them at link/config time: only \_boot\_progress\_poll/\_tag remain, no STACK64, 25 boot args vs the 17 line's 68. See docs/SCREEN-ONLY.md §3.
- Honest caveat: the flashed 17-line builds also ran the BootProgress layer as weak stubs \(LegacyDisplayStubs.c: 'the first-console configuration disables the BootProgress layer'; every muyu defconfig has CONFIG\_XNU\_BOOT\_PROGRESS unset; the one config that sets it, muyu-full-plus\_defconfig, self-declares 'does not build from a clean tree yet'\). The 17-line panel showed console text + STACK64 + MUYU probe rows, not the 48-row page. Porting = enabling the layer, not writing it.

### Completion criteria

- Framebuffer log pages give full boot context from a single photograph; that is the accepted, only channel.

### Current limits

- No real-time channel; information is capped by panel area \(\~230x40 chars per page\) and requires a person to photograph; nothing is machine-readable; event ordering relies on tick numbers printed on the page; a dark panel loses everything, so the pram panic page is the lifeline.

### Next action

- Per docs/SCREEN-ONLY.md §4, port back instead of designing new: set CONFIG\_XNU\_BOOT\_PROGRESS=y + CONFIG\_XNU\_NATIVE\_LEGACY\_DISPLAY=y on the 27 defconfig, relink BootProgress/BootUiTraceProbe/BravearkLastLog/MuyuCrashLog from kits/muyu via the existing build-native-legacy-display.py and build-boot-log.py, put sheng-build-tag on the vendor\_boot cmdline, then run the check-boot-\*.py suite as the flash gate. \(The files.arm64 USB registration was already dropped with the driver on 2026-11-08 — the wip screen patch now registers only muyu\_debug.c.\)

### Evidence

- `device`: [DEPCFG 16 probes accepted 0 executed \(panel table\); DCTL.CSFTRST never self-clears; framebuffer readout works; recorded u150-u155 \[§60 + logs/2026-11-08-14-36-26-878.jpg\]](https://github.com/yehua123-oos/UniXNU-muyu/blob/5e99d2b16421b469a9961ec872d74ab4466f97b8/docs/HANDOFF-2026-11-07.md)
  Command: <code>flash u155, photograph panel</code>. Revision: `714179fd56cf909e3725e9c6681eb76fa253075b`.
- `host`: [screen API surface enumerated \(block/glyph/bigchar/status/logdump/textdump/pram\_bigpage/bar/protected/bounded lock\) at video\_console.c:1314-1769; recorded ac9718f + working tree 2026-11-08 15:59 \[§2\]](https://github.com/yehua123-oos/UniXNU-muyu/blob/5e99d2b16421b469a9961ec872d74ab4466f97b8/docs/SCREEN-ONLY.md)
  Command: <code>grep -nE '^muyu_vc_[a-z_]+\(' osfmk/console/video_console.c</code>. Revision: `714179fd56cf909e3725e9c6681eb76fa253075b`.
- `source`: [the entire screen capability \(which lived only in tree/.cache/xnu-work, 126 uncommitted changes\) is now archived in the device repo: 4 source files + 2453-line patch over 7 files; recorded 2026-11-08 17:31 \[+ patches/xnu/wip/muyu-screen-wip-20261108.patch\]](https://github.com/yehua123-oos/UniXNU-muyu/blob/5e99d2b16421b469a9961ec872d74ab4466f97b8/drivers/MuyuDebug/muyu_debug.c)
  Command: <code>git diff HEAD -- osfmk/console/video_console.c pexpert/arm/pe_init.c bsd/conf/files.arm64 bsd/dev/arm/muyu_*.c</code>. Revision: `714179fd56cf909e3725e9c6681eb76fa253075b`.

</div>
