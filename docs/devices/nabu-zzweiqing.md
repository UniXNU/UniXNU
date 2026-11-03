# Xiaomi Pad 5 \(zzweiqing\)

[zzweiqing/UniXNU-nabu](https://github.com/zzweiqing/UniXNU-nabu)

<div v-pre>

Xiaomi Pad 5 boots a source-built XNU with the original 21H16 userland: eight cores with working SGI IPI, UFS root windows, NT36523 touch, GOP framebuffer display with A640 Metal scanout compositing, and a persistent on-ESP boot log. Interactive SpringBoard UI was demonstrated; a bounded scanout stall after the first frames is under repair. Persistent Data, network, audio and power management are not yet implemented.

Source record: [porting.toml](https://github.com/zzweiqing/UniXNU-nabu/blob/54b4f98457f8e9e232cc0a077c20d08d0b2f0ac9/porting.toml), `54b4f98457f8e9e232cc0a077c20d08d0b2f0ac9`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `implemented` |
| [Firmware and boot](#firmware) | `device-verified` |
| [CPU and interrupts](#cpu) | `device-verified` |
| [Memory and DMA](#memory) | `device-verified` |
| [Storage and root](#storage) | `device-verified` |
| [Display](#display) | `device-verified` |
| [Input](#input) | `device-verified` |
| [GPU](#gpu) | `device-verified` |
| [Network](#network) | `planned` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `planned` |
| [Image assembly](#packaging) | `device-verified` |
| [Diagnostics](#diagnostics) | `device-verified` |

## Configuration {#configuration}

`implemented`

Components: `ArmDTPlatform`, `ArmCpu`, `device`.

### Hardware and dependencies

- SM8150 board of Xiaomi Pad 5, iPad7,11 21H16 restore inputs
- UniXNU core pin 245aca1a9ec5b730b1cad80fade295800d2981f1

### Configuration

- board.toml selects schema\_version 2, soc\_source sm8150 and os\_profile ipados-17.7-21H16.
- The component list covers platform, cpu, boot, storage, display, GPU, input and board glue; kernel defconfig is nabu\_ufs\_gpu\_metal\_defconfig.
- Device patch series order is arch, soc, os, device.

### Procedure

- Prepare pinned upstream source, apply the device series, run the profile archives and prelink, then package the ESP payload.
- Kernel builds are dispatched to a macOS GitHub Actions runner; local steps are host-side packaging and verification.

### Development findings

- The nabu bring-up line currently resolves through a project CI pipeline rather than ./unixnu; component pins match the recorded revisions in components.toml and feeds.toml.
- LLVM for Darwin ARM64 treats ';' as an asm comment marker, so multi-instruction one-line inline assembly silently drops instructions; this class of defect blocked SGI delivery until fixed.
- Selected components use canonical upstream catalog ids \(ShengUfs, RamBlock, VirtioMmioBlock, XnuPrelink, AppleKeyStoreState\) after the upstream Native\* repository renames; feeds.toml pins every selected component to the proven commits.
- Self-referential revisions in components.toml and this record point at the first public commit 12a07055; feeds.toml tracks the SoC repository at f363dcda.

### Completion criteria

- All source pins resolve, every selected component maps to an area, and the recorded defconfig produces a prelinked kernel candidate.

### Current limits

- Format 2 resolution through ./unixnu defconfig/fetch is not yet qualified; the board still builds through the project workflow.

### Next action

- Resolve the device through ./unixnu defconfig and porting-record check, then record the resolving commit.

### Evidence

- `source`: [Format 2 board selects the SM8150 soc source and the 21H16 OS profile with the full component list.](https://github.com/zzweiqing/UniXNU-nabu/blob/54b4f98457f8e9e232cc0a077c20d08d0b2f0ac9/board.toml)
- `source`: [The shipping defconfig enables owner UFS root, RAM Data, touch, legacy display and the A640 accelerator publish.](https://github.com/zzweiqing/UniXNU-nabu/blob/54b4f98457f8e9e232cc0a077c20d08d0b2f0ac9/configs/nabu_ufs_gpu_metal_defconfig)

## Firmware and boot {#firmware}

`device-verified`

Components: `DarwinBoot`.

### Hardware and dependencies

- Stock Xiaomi UEFI on nabu, rEFInd installed on the 334 MiB ESP
- UniXNU.efi menu and DarwinBoot.efi driver placed under /EFI/UniXNU on the ESP

### Configuration

- Boot menu version 1, timeout 20, default entry loads Payloads kernel.macho with its .adt and .trustcache.
- DarwinBoot requests a 1 GiB contiguous conventional-memory window \(darwinboot-memory-size 0x40000000\).

### Procedure

- Write payload files to the ESP, select the nabu entry, XNU hands off from DarwinBoot with GOP framebuffer and ADT.

### Development findings

- Boot, rollback and menu management on the ESP are routine; payloads of \~101 MiB Mach-O load within the reserved window.
- The stock UEFI framebuffer \(1600x2560 at 0x9c000000\) reaches XNU through boot\_args.Video.
- No firmware image is rebuilt for this board; the vendor UEFI and rEFInd are used as shipped.

### Completion criteria

- Payload loads, XNU starts, and the framebuffer plus memory reservations are published to the kernel.

### Current limits

- Mu-Silicium firmware build is not planned; the boot depends on rEFInd and ESP file layout.

### Next action

- Keep the firmware path unchanged; record any firmware-side regression in the run evidence.

### Evidence

- `device`: [Readback sequence 7831 committed with CRC pass: DarwinBoot handed the payload to XNU, kernel log captured from the ESP log extent.](https://github.com/zzweiqing/hackios-mac-batch/actions/runs/41287217331)
  Command: <code>py -3 -B tools/nabu_esp_log.py pull --root</code>. Revision: `12a070555a9ef321df367311b4812f2bfa87beac`.

## CPU and interrupts {#cpu}

`device-verified`

Components: `ArmCpu`.

### Hardware and dependencies

- Eight Kryo 485 cores, MPIDR affinities 0x000-0x700
- GICv3: distributor 0x17a00000, redistributors at 0x17a60000 stride 0x20000, virtual timer INTID 19, 19.2 MHz counter

### Configuration

- cpus=8 with armcpu-self-ipi=1; the ADT publishes all eight cpu nodes and the psci smc node.
- SGI delivery uses ICC\_SGI1R writes after dsb ishst; the earlier SPI IPI route \(intids 1008-1015\) was tested and rejected.

### Procedure

- Build the cpu profile, boot the candidate, read back the committed NABULOG2 capture and compare per-core step/fail/IPI counters.

### Development findings

- Inline-assembly comment semantics dropped all but the first instruction of the SGI sequence; the newline-separated form restored delivery.
- Device run 7831 shows all eight cores at step=7 fail=0 psci=0 with IPI growing past 1.3M and per-core SGI/timer counts increasing.
- A one-line asm template defect class was found in 17 sites and fixed by emitting instructions on separate lines.

### Completion criteria

- ncpus=avail=topo=8, every secondary reaches its startup checkpoint and SGI IPI is delivered to all cores.

### Current limits

- Scheduler-level CPU power management \(EPSS\) and idle states are not implemented.

### Next action

- Re-run the SMP sample set on the next candidate to confirm IPI delivery stays healthy.

### Evidence

- `device`: [Run 7831: ncpus=avail=topo=8 across 64 samples, seven secondaries step=7 fail=0, IPI 1,320,637 and rising with fail=0.](https://github.com/zzweiqing/hackios-mac-batch/actions/runs/41287217331)
  Command: <code>py -3 -B tools/nabu_esp_log.py pull --root</code>. Revision: `12a070555a9ef321df367311b4812f2bfa87beac`.
- `source`: [Board DTS publishes eight cpu nodes at affinities 0x000-0x700 with the psci smc method.](https://github.com/zzweiqing/UniXNU-nabu/blob/54b4f98457f8e9e232cc0a077c20d08d0b2f0ac9/dts/nabu.dts)

## Memory and DMA {#memory}

`device-verified`

Components: `device`.

### Hardware and dependencies

- DRAM banks \[0x80000000,0x3cc00000\], \[0xc0000000,0x80000000\], \[0x140000000,0xc0000000\] with a TrustZone hole at 0xb9900000..0xc0000000
- UFS SMMU at 0x15000000 with stream 0x300; A640 GPU SMMU at 0x02ca0000 with its own context

### Configuration

- chosen.dram-base 0xc0000000 and dram-size 0x140000000 \(5 GiB\) bound the XNU-owned window; darwinboot-memory-size is 0x40000000.
- Managed render-target IOSurface pages are mapped Normal NC under t733-managed-rt-normal=1 on this BCM2837 config.

### Procedure

- Publish the ADT memory contract, boot, and confirm the mapped windows plus SMMU translation from kernel counters.

### Development findings

- XNU accepts a single dram base/size window; Option A excludes bank 0 and the firmware hole while covering the DarwinBoot window.
- UFS DMA runs through the 0x15000000 SMMU on stream 0x300; GPU DMA runs through the A640 SMMU at 0x02ca0000.
- Framebuffer memory at 0x9c000000 sits in bank 0 and is accessed through the GOP-composited path rather than the XNU-owned window.

### Completion criteria

- All handoff regions are accounted for; UFS and GPU DMA engines translate through their documented SMMU contexts.

### Current limits

- Bank 0 low RAM and TrustZone hole handling for later stages is unresolved; SMMU fault recovery is not implemented.

### Next action

- Record any SMMU fault telemetry on the next GPU-heavy run.

### Evidence

- `device`: [Run 6229: UFS windows published and GPU scanout accepted 181 frames with zero fallbacks, exercising both SMMU paths.](https://github.com/zzweiqing/hackios-mac-batch/actions/runs/41265722207)
  Command: <code>py -3 -B tools/nabu_esp_log.py pull --root</code>. Revision: `12a070555a9ef321df367311b4812f2bfa87beac`.
- `source`: [Board DTS records the three DRAM banks and the reserved framebuffer/firmware ranges.](https://github.com/zzweiqing/UniXNU-nabu/blob/54b4f98457f8e9e232cc0a077c20d08d0b2f0ac9/dts/nabu.dts)

## Storage and root {#storage}

`device-verified`

Components: `ShengUfs`, `RamBlock`, `VirtioMmioBlock`, `AppleKeyStoreState`, `VerifiedRoot`.

### Hardware and dependencies

- SM8150 UFS host controller at 0x01d84000, GCC window 0x177000, SMMU 0x15000000 stream 0x300, 4096-byte blocks
- Unallocated LUN0 range LBA 2739747-18364746 after Ubuntu partition removal; OS window at LBA 2739968 and SystemOS window at LBA 4204809

### Configuration

- native-ufs-root=1 with direct window boot arguments publishes the OS and SystemOS windows as block devices.
- Data volume is a volatile RAM block seeded at boot with UUID 0A5EED00-0000-4000-8000-000000000001; the SystemOS cryptex union-mounts as the cache carrier C374ACD3-75FE-4FAD-B02E-FC3C9A86DA11.

### Procedure

- Stage the DMG windows into the UFS range, boot with the direct window arguments, and verify root mount plus launchd execution from the committed log.

### Development findings

- The driver publishes LUN0 as a 4K read/write block device and the original window reader performs the 512-byte unit conversion.
- System volume mount and launchd execution were captured in the committed log; the RAM Data seed lets SpringBoard reach the UI.
- Persistent on-disk Data is deliberately not in the current profile; the RAM block keeps the session volatile.
- The record uses the canonical upstream ids ShengUfs/RamBlock for the proven NativeUfs/NativeRamBlock pins; VerifiedRoot closes the ShengUfs dependency set at 2854c61f.

### Completion criteria

- Root mounts, launchd starts, and the Data seed behaves correctly for the boot session.

### Current limits

- No persistent Data writes yet; media writes outside the window are not implemented.
- UFS error recovery, multiple LUNs and power collapse remain unverified.

### Next action

- Add a bounded persistent Data region in the unallocated range once the current windows stay stable.

### Evidence

- `device`: [Committed log shows UFS requests completing and the system volume mounted before userland start.](https://github.com/zzweiqing/hackios-mac-batch/actions/runs/41265722207)
  Command: <code>py -3 -B tools/nabu_esp_log.py pull --root</code>. Revision: `12a070555a9ef321df367311b4812f2bfa87beac`.

## Display {#display}

`device-verified`

Components: `GopFramebuffer`, `NabuPlatform`, `device`.

### Hardware and dependencies

- Stock UEFI GOP framebuffer 1600x2560 32bpp at 0x9c000000, rowBytes 6400
- A640 scanout path imports GOP frames and blits to panel

### Configuration

- Native legacy display presents the framebuffer; the scanout handoff moves offered frames through up to eight fixed source-map slots with CPU fallback preserved.
- Boot progress and early console use the GOP path; panic\_screen stays off.

### Procedure

- Boot the candidate, count offered/done/fallback scanout frames and GPU command buffer completions in the committed capture.

### Development findings

- The board reached interactive SpringBoard UI in run 9048: 184 swaps accepted, 184 frames retired, scanout offered=done=1349, GPU command buffers 2752/2752.
- Runs 2550 and 10090 stall after five produced frames while the GPU reports 10/10 buffers done; a completion-wait coupling defect in the fixed frontend is patched and packaged but not yet installed.
- CPU copy and GPU blit both worked; the GPU path replaced CPU scanout copies after the handoff proof.

### Completion criteria

- Frames are produced, retired and visible; the scanout path accepts userland presentation end to end.

### Current limits

- An intermittent bounded stall after the first frames is unresolved; backlight control and native DPU scanout are absent.
- Reported frame rates are scanout completion rates between committed samples, not panel FPS.

### Next action

- Install the packaged completion-wait fix candidate and check scanout completion past the five-frame point.

### Evidence

- `device`: [Run 9048 \(v3\): interactive UI on hardware, scanout offered=done=1349 fallback=0 pending=0, GPU command buffers 2752/2752.](https://github.com/zzweiqing/hackios-mac-batch/actions/runs/41265722207)
  Command: <code>py -3 -B tools/nabu_esp_log.py pull --root</code>. Revision: `12a070555a9ef321df367311b4812f2bfa87beac`.
- `source`: [Scanout source cache keeps up to eight MTLBuffer imports bound to the kernel fixed slots with identity checks.](https://github.com/zzweiqing/UniXNU-nabu/blob/54b4f98457f8e9e232cc0a077c20d08d0b2f0ac9/platform/NabuScanoutSourceCache.h)

## Input {#input}

`device-verified`

Components: `NabuTouch`, `device`.

### Hardware and dependencies

- NT36523 Novatek touch digitizer on the board touch bus
- Generic digitizer IOHIDEventDriver personality from IOHIDEventDriverSafeBoot on 21H16

### Configuration

- The hardware CPU profile prelinks IOHIDFamily and IOHIDEventDriverSafeBoot; AppleMultitouchDriver stays out on this build.
- Touch events reach the published digitizer through the board service.

### Procedure

- Boot with touch enabled and confirm digitizer registration plus user-visible input in the UI session.

### Development findings

- Touch is functional in the interactive session; the prelink closure deliberately keeps the safe-boot driver only.
- Coordinate mapping details and multi-contact edge cases were not separately instrumented.

### Completion criteria

- Digitizer registers and touches reach SpringBoard.

### Current limits

- Physical buttons and key events are not implemented.
- Touch latency and firmware update paths are unmeasured.

### Next action

- Instrument digitizer event counters in a later capture round.

### Evidence

- `source`: [Board touch service for the NT36523 digitizer is compiled into the platform profile.](https://github.com/zzweiqing/UniXNU-nabu/blob/54b4f98457f8e9e232cc0a077c20d08d0b2f0ac9/platform/NabuTouch.cpp)
- `device`: [Run 9048 reached interactive UI with user navigation reported.](https://github.com/zzweiqing/hackios-mac-batch/actions/runs/41265722207)
  Command: <code>py -3 -B tools/nabu_esp_log.py pull --root</code>. Revision: `12a070555a9ef321df367311b4812f2bfa87beac`.

## GPU {#gpu}

`device-verified`

Components: `NabuAdreno`, `AdrenoMetal`, `metal2vulkan`, `ArmSmmu4K`, `AdrenoPM4`, `AdrenoFirmware`.

### Hardware and dependencies

- Adreno 640 v2, chip-id 0x06040001, GMEM 1 MiB
- GPU MMIO 0x02c00000, GMU 0x02c6a000, RSCC 0x02c8d000, GPU SMMU 0x02ca0000, gpucc 0x02c90000, GCC 0x00100000, PDC 0x0b290000/0x0b490000, command DB 0x85f20000, RPMh 0x18220000, AOP 0x0c300000 with doorbell 0x17c00000, ZAP region 0x98f15000
- Vendor firmware a630\_sqe.fw, a640\_gmu.bin, a640\_zap.&\#123;mdt,b02&\#125; from the device vendor partition

### Configuration

- nabu-gpu=1 gates GMU/SMMU/CP bring-up; the driver publishes the AGXAccelerator with MetalPluginName=NativeAdrenoMetal.
- The Metal plugin loads through the signed bundle path; Turnip runs the A640 backend through metal2vulkan.

### Procedure

- Build the metal profile with the plugin addon and trust, install the ESP payload, and count command buffers, imports and scanout completions in the committed capture.

### Development findings

- A640 compute graphs and scanout ran on hardware: run 9048 completed 2752/2752 command buffers and the Metal path composed the desktop.
- A waiting design defect coupled GPU completion to handler delivery \(dispatch\_group\_wait after runtime waits\), producing the observed five-frame stall; the decoupling patch is packaged, host-verified and held for installation.
- Five Metal async-creation APIs ran their callbacks synchronously on the calling thread; the fixed candidate passed 20 bounded regressions and is packaged.
- Six board patches to unixnu-adrenometal are kept in patches/components; upstream carries a different fixed-eight-slot import reuse model that does not fit this board contract.

### Completion criteria

- GPU submits command buffers through the CP, fences retire, Metal serves userland clients and the compositor presents frames.

### Current limits

- The stall defect is not proven resolved on hardware; CoreImage NBLibrary externFunctionNames gaps crash iconservicesagent without blocking the desktop.
- ZAP secure path, full power states and GMU frequency policy are not implemented.

### Next action

- Run the packaged async-fix/completion-wait candidate and confirm sustained frame production.

### Evidence

- `device`: [Run 9048: AGXAccelerator published, Metal plugin active, 2752/2752 command buffers, GPU-composited UI on hardware.](https://github.com/zzweiqing/hackios-mac-batch/actions/runs/41265722207)
  Command: <code>py -3 -B tools/nabu_esp_log.py pull --root</code>. Revision: `12a070555a9ef321df367311b4812f2bfa87beac`.
- `host`: [Async-creation fix candidate built, signed and packaged; 20 bounded regressions passed on the host harness.](https://github.com/zzweiqing/hackios-mac-batch/actions/runs/41388287775)
  Command: <code>workflow dispatch nabu-turnip.yml --turnip-only --async-fix</code>. Revision: `12a070555a9ef321df367311b4812f2bfa87beac`.
- `source`: [A640 board windows, firmware binding and GMU bring-up code for the SM8150 GPU block.](https://github.com/zzweiqing/UniXNU-nabu/blob/54b4f98457f8e9e232cc0a077c20d08d0b2f0ac9/gpu/a640/NabuGpuScanout.cpp)

## Network {#network}

`planned`

### Hardware and dependencies

- SM8150 Wi-Fi hardware \(WCN3998 family on nabu\) not yet inventoried for this port

### Configuration

- No network component is selected; the area records the required inputs only.

### Procedure

- Inventory the Wi-Fi chip, firmware files, bus and power sequence from the device firmware tree before implementation.

### Development findings

- No implementation exists; upstream ports on other SoCs use Ath12kWifi-class components.

### Completion criteria

- Packets transmit and receive through a published OS network interface.

### Current limits

- Hardware inventory and firmware handling are missing.

### Next action

- Read the vendor firmware tree for the Wi-Fi node and firmware partition requirements.

### Evidence

Collect evidence using the next action.

## Audio {#audio}

`planned`

### Hardware and dependencies

- SM8150 audio DSP, codec and clock fabric not yet inventoried

### Configuration

- No audio component is selected.

### Procedure

- Inventory ADSP/CDSP firmware, codec wiring and routing before implementation.

### Development findings

- No implementation exists.

### Completion criteria

- Playback and recording work through an OS audio interface.

### Current limits

- All inputs pending.

### Next action

- Inventory the audio subsystem from the device tree and vendor partition.

### Evidence

Collect evidence using the next action.

## Power {#power}

`planned`

### Hardware and dependencies

- SM8150 PMIC, RPMh and regulator tree; EPSS frequency LUTs; battery fuel gauge

### Configuration

- A PMGR stub and watchdog counter exist in the platform package; no power states or DVFS are enabled.

### Procedure

- Inventory regulator, clock and EPSS resources; implement CPU DVFS and device power states in that order.

### Development findings

- The board boots without power management; the watchdog hook is a counter only and hardware reset relies on Recovery entry.

### Completion criteria

- CPU frequency policy, device idle states and battery reporting work.

### Current limits

- Only stub services exist; no regulator or EPSS implementation.

### Next action

- Inventory RPMh and PMIC resources from the device firmware tree.

### Evidence

Collect evidence using the next action.

## Image assembly {#packaging}

`device-verified`

Components: `XnuPrelink`, `device`.

### Hardware and dependencies

- j171ap 21H16 kernelcache 2c395d03, DeviceTree.j171ap.im4p 1d5ce5ee, OS and SystemOS trust caches
- Prelink slide -0x1360000, early security init com.apple.driver.AppleMobileFileIntegrity=0xfffffff005b70ae0
- User-produced ipsw-21h16-small.zip \(source-ci/prepare\_ipsw\_input.py\), owner policies and the display reference; see docs/BUILD-INPUTS.zh-CN.md

### Configuration

- Compact loader keeps the original \_\_TEXT layout; prelink roots close APFS, AMFI, sandbox, IOSurface, IOMobileGraphicsFamily, IOHID and IOGPUFamily.
- The ESP payload is Payloads/&lt;entry&gt;.macho + .adt + .trustcache + initrd under the TOML menu; ESP files UniXNU.efi and DarwinBoot.efi are preserved during candidate installs.
- source-ci/nabu-build.sh mirrors the proven CI flow \(baseline board rewrite, prepare\_source.py, unixnu defconfig+build, collect\_outputs\); scripts/package.sh emits the ESP payload via unixnu payload on the resolved tree.

### Procedure

- Stage the baseline board with source-ci/nabu-build.sh, assemble and patch the pinned upstream with source-ci/prepare\_source.py, then ./unixnu defconfig + build kernel inside the resolved tree.
- Package the ESP file set with scripts/package.sh \(official path\) or the host packagers under device\_bringup/xnu\_stage \(per-profile proven packagers\), then install under a verified rollback receipt.

### Development findings

- Install replaces only the kernel file and menu text under transaction receipts; the ESP is unmounted and backups close before reboot.
- The packaged artifact is a \~101 MiB Mach-O; memory-budget checks bound kernel, ADT, trust and initrd inside the loader window.
- feeds.toml pins the full selected component set to the proven submodule commits so ./unixnu fetch resolves the recorded sources; nabu-only components remain declared in components.toml pending upstream registration.

### Completion criteria

- A clean checkout produces identical kernel and package outputs; hardware boots the packaged payload.

### Current limits

- The packaging pipeline is project-specific; migration to the shared package action is pending.
- Owner trust-cache signing flow is not part of the public path.

### Next action

- Wire scripts/package.sh to produce the ESP payload from a clean checkout under the package action.

### Evidence

- `device`: [Candidates install through receipt-verified ESP transactions and produce committed boot captures, e.g. sequences 7831 and 9048.](https://github.com/zzweiqing/hackios-mac-batch/actions/runs/41287217331)
  Command: <code>py -3 -B tools/nabu_esp_log.py pull --root</code>. Revision: `12a070555a9ef321df367311b4812f2bfa87beac`.

## Diagnostics {#diagnostics}

`device-verified`

Components: `device`.

### Hardware and dependencies

- Pre-allocated ESP log extent addressed by a 16-byte token in boot args
- Recovery/Android ADB readback path for the committed slots

### Configuration

- nabu-log=1 enables the NABULOG2 writer; two slots carry sequence, boot id, build id, CRC and loss counters.
- UI watch sampling, GPU problem stream and heartbeat counters are opt-in arguments.

### Procedure

- Boot a logging candidate, return to Recovery and read the ESP extent read-only over ADB; verify CRC, sequence, boot and build ids before decoding text.

### Development findings

- The ESP writer survived every experiment including panics; committed snapshots bound each run to its candidate build.
- Console contention drops bounded bytes under load; uncommitted tail output after the last commit is absent by design.
- USB CDC logging was prototyped but the proven path is ESP -&gt; Recovery -&gt; ADB.

### Completion criteria

- Each boot commits a verifiable record that identifies its kernel build and survives into readback.

### Current limits

- Snapshots are the last committed console state, not a complete boot log; uncommitted output and non-console writers are lost.
- No live debugging channel exists on hardware.

### Next action

- Keep the writer stable; extend coverage only behind explicit boot arguments.

### Evidence

- `device`: [Sequences 7831 through 10090 committed with CRC pass; text exports up to 377 KiB bound to their candidate build ids.](https://github.com/zzweiqing/hackios-mac-batch/actions/runs/41287217331)
  Command: <code>py -3 -B tools/nabu_esp_log.py pull --root</code>. Revision: `12a070555a9ef321df367311b4812f2bfa87beac`.
- `source`: [NABULOG2 record format: dual slots, sequence and boot/build identity, CRC, loss and ownership counters.](https://github.com/zzweiqing/UniXNU-nabu/blob/54b4f98457f8e9e232cc0a077c20d08d0b2f0ac9/ufs/NabuLogFormat.h)

</div>
