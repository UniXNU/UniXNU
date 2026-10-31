# 小米平板 7 / POCO Pad X1（uke）

[Allenwdk/UniXNU-uke](https://github.com/Allenwdk/UniXNU-uke)

<div v-pre>

Xiaomi Pad 7 \(SM7675/cliffs\) port: format-2 repository migration verified by from-scratch kernel builds; the shared patch set is fully upstream-aligned \(73 patches, four-layer chain\); the bring-up runs through GPU mode 9, a real on-screen UI and touch scanning, with host-only migration verification on 2026-10-28.

源记录: [porting.toml](https://github.com/Allenwdk/UniXNU-uke/blob/89c5dfa9ff61f90cdc3362e492a3fc0c5248af07/porting.toml), `89c5dfa9ff61f90cdc3362e492a3fc0c5248af07`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `host-verified` |
| [固件与启动](#firmware) | `device-verified` |
| [CPU 与中断](#cpu) | `device-verified` |
| [内存与 DMA](#memory) | `device-verified` |
| [存储与根卷](#storage) | `device-verified` |
| [显示](#display) | `device-verified` |
| [输入](#input) | `device-verified` |
| [GPU](#gpu) | `device-verified` |
| [网络](#network) | `not-applicable` |
| [音频](#audio) | `not-applicable` |
| [电源](#power) | `device-verified` |
| [镜像组装](#packaging) | `host-verified` |
| [诊断](#diagnostics) | `device-verified` |

## 配置 {#configuration}

`host-verified`

组件: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`.

### 硬件与依赖

- Format-2 resolver of the shared UniXNU checkout \(schema\_version = 2\).
- UniXNU-sm7675-common SoC layer and the ipados-17.7.11-21H461 OS profile.
- Catalog components with the board's fork pins in feeds.toml.

### 配置

- board.toml: schema\_version 2, soc\_source sm7675, os\_profile ipados-17.7.11-21H461, kit uke.
- The validated 68-patch set as one explicit series \(device:patches/xnu/series\).
- Nine board defconfigs; uke-gpu-userland\_defconfig is the active GPU track.

### 操作步骤

- ./unixnu defconfig uke-gpu-userland\_defconfig -D ../UniXNU-uke-format2
- ./unixnu fetch -D ../UniXNU-uke-format2 &amp;&amp; ./unixnu status --json -D ../UniXNU-uke-format2
- ./unixnu tree -D ../UniXNU-uke-format2

### 开发经验

- The format-1 patch path never applied the shared patches from a cold tree \(the board module shadowed them\); the format-2 series replays the set statelessly.
- Catalog archive recipes equal the board's legacy builder commands; the component aliases keep the old script names working.
- P2 \(gpucomp26\): the compositor's two-plane 'b3a8' frame is scanned by the DPU natively. Plane 0's 4 B/texel colour words \(rows 4\*width apart\) are XRGB2101010, whose SSPP SRC\_FORMAT 0x000276ff is the firmware's own ARGB8888 word 0x000237ff \(unpack 0x03020001\) with alpha bit 8 clear and DX bit 14 set, per the stock dpu\_hw\_sspp\_setup\_format/dpu\_formats.c in the reference kernel; plane 1 is the alpha byte, whose row is the record's stride field. The 34,177,024-byte frame maps only its 27,340,800-byte plane-0 prefix into one slot; the CPU decode remains the fallback when the display-bank window is unavailable.
- gpucomp26 log \(recovery, userdata window, t=16..917 s\): UKE DPU: direct ready fmt=000237ff/000237ff unpack=03020001 tenbit=000276ff; four b3a8 frames mapped by their plane-0 prefix \(direct slot ... bytes=27340800\); UKE DPU: tenbit sample p0=18060180 p0c=37edfb7e alpha=ff/ff -- the alpha plane is 0xFF, so the frame is opaque and the XRGB2101010 word order is the right one. One stall snapshot at t=78.4 s and none after; GPU commit-to-complete still averages 50.9 ms over 8884 commits in 893 s \(about 9.9/s\).
- gpucomp27 ports the upstream display's refresh tick \(GopFramebuffer 33e941a\): startVsync/vsyncTick/armVsync, getRefreshAttributes at slot 301 and setDisplayRefreshProperties in registerService, with the builder binding \_native\_legacy\_vsync\_notify \(0xfffffff005796720\) and \_native\_legacy\_set\_refresh\_properties \(0xfffffff00579ebb8\) after checking the original bytes; board.toml sets sheng-vsync=120 \(armcpu-diagnostics dropped to stay at 987 of 1000 command-line bytes\). The direct path now prints UKE DPU: flip n=... tb=... skip=... fb=... latch=...us max=...us vsync=... every 120 frames and the first eight UKE DPU: skip lines, so the next log separates compositor starvation from display-path loss.

### 完成条件

- Status resolves arch, soc, os and device layers with the intended pins; the patch order lists 68 unique patches; the output path is out/uke/ipados-17.7.11-21H461/&lt;config&gt;/.

### 当前范围

- The adopted shared patches \(five evolutions and seven additions\) are host-verified only; their userland behavior is unproven on hardware.

### 下一步

- Flash gpucomp38 \(uke-port/releases/2026-10-29-gpu-upstream-feat: kernel f050cf35, payload be3f7cc8, vendor\_boot 29ddb27b\) when the device can come out of TWRP, and check first whether B fill/copy rises above the 1.76/3.75 GB/s gpucomp37 measured; UKE GPU: maint then shows which cache-maintenance phase the driver still pays.
- If the throughput holds, keep the feat-based driver \(upstream cache maintenance, on-demand page tables, hangcheck\) and re-measure the compositor's frame time; the DPU direct path with the client fence \(gpucomp31-36 findings\) stays as the display side.

### 证据

- `host`: [schema\_version 2 resolves with 23 component specs, 37 modules and a 68-entry patch order](https://github.com/Allenwdk/UniXNU-uke/blob/89c5dfa9ff61f90cdc3362e492a3fc0c5248af07/board.toml)
  Command: <code>./unixnu status --json -D ../UniXNU-uke-format2</code>. Revision: `23c2926941405e7df8097a6bca6ee8348a39c787`.
- `source`: [the validated patch set in application order, shared entries prefixed arch:](https://github.com/Allenwdk/UniXNU-uke/blob/89c5dfa9ff61f90cdc3362e492a3fc0c5248af07/patches/xnu/series)

## 固件与启动 {#firmware}

`device-verified`

组件: `DarwinBoot`.

### 硬件与依赖

- Mu-Silicium UEFI checkout \(uefi-uke\) with the ukePkg platform.
- Payload FAT volume UKEESP with kernel.macho, its ADT and the trust cache.

### 配置

- \[firmware\]: config uke, dsc Platforms/Xiaomi/ukePkg/uke.dsc, FD 3 MiB at FD\_BASE 0xa7100000, ENABLE\_SECUREBOOT=1, MEMORY\_PROTECTION=TRUE.

### 操作步骤

- ./unixnu build firmware --skip-preflight --uefi ../uefi-uke -D ../UniXNU-uke-format2
- fastboot boot boot.img \(or flash vendor\_boot+boot on the inactive slot\)

### 开发经验

- The boot manager displays the DT/initrd status through gUkeMemStatusGuid and the previous XNU panic line through the DXE memory driver.
- gUkeMemStatusGuid must be declared under \[Guids\] in both the DEC and the library INF.

### 完成条件

- The FD builds, the menu boots the payload entry, and the device reaches the XNU entry point.

### 当前范围

- Verification here is host-only; the format-2 chain has not yet been flashed.

### 下一步

- Flash the format-2 boot.img on hardware and confirm the menu and first boot match the previous image.

### 证据

- `device`: [the firmware menu and the uke boot entry run on hardware through the bring-up images](https://github.com/Allenwdk/UniXNU-uke/blob/89c5dfa9ff61f90cdc3362e492a3fc0c5248af07/docs/PROGRESS.md)
  Command: <code>fastboot boot boot.img</code>. Revision: `c77d613dc91fb54479242aa5d5902c48662b80d7`.
- `host`: [SILICIUM\_UEFI.fd builds 3,145,728 bytes with the board defines](https://github.com/Allenwdk/UniXNU-uke/blob/89c5dfa9ff61f90cdc3362e492a3fc0c5248af07/board.toml)
  Command: <code>./unixnu build firmware --skip-preflight --uefi ../uefi-uke -D ../UniXNU-uke-format2</code>. Revision: `4f4bf7e1f4ad56743562777becd7ac7d6714216c`.

## CPU 与中断 {#cpu}

`device-verified`

组件: `ArmCpu`, `ArmDTPlatform`, `ArmVirtPlatform`.

### 硬件与依赖

- Eight Kryo cores at affinity 0..7 \(SM7675 cliffs\).
- PSCI over SMC for secondary bring-up.

### 配置

- dts/uke.dts: eight arm,cortex-a720 nodes, timebase 19200000, psci method smc.
- Kernel arguments sheng-smp=1 armcpu-spi-ipi=1 armcpu-diagnostics=1.

### 操作步骤

- Build the kernel with uke-gpu-userland\_defconfig and boot with the SMP arguments.

### 开发经验

- Single-CPU runs are stable past t=877s; SMP died around t=117s in early runs \(SMP/IPI or UFS concurrency\), mitigated by the SPI-IPI path and watchdog policy.

### 完成条件

- All eight cores enter the scheduler and the system stays up under load.

### 当前范围

- Long-run SMP stability under UFS load is still being watched.

### 下一步

- Keep the single-CPU fallback argument documented in the record for bisecting resets.

### 证据

- `device`: [SMP boots with the SPI-IPI path; single-CPU profile stable past t=877s](https://github.com/Allenwdk/UniXNU-uke/blob/89c5dfa9ff61f90cdc3362e492a3fc0c5248af07/docs/PROGRESS.md)
  Command: <code>fastboot boot boot.img</code>. Revision: `c77d613dc91fb54479242aa5d5902c48662b80d7`.

## 内存与 DMA {#memory}

`device-verified`

组件: `RamBlock`.

### 硬件与依赖

- High DRAM window at 0x8C0000000 sized 0x240000000 \(9 GiB\) with the owned window at 0x130000000.
- GMU pool 0xC8000000/32 MiB reserved in the UEFI map and adopted over IODeviceMemory::withRange.

### 配置

- \[payload.adt\]: owned\_memory\_size 0x130000000, chip\_id 207, cpu\_regs 0..0x700, boot-manifest-hash pinned.
- dts/uke.dts memory node: one contiguous range, as the ADT hand-off requires.

### 操作步骤

- Build the payload and read the UKE MEM counters from the menu and the kernel log.

### 开发经验

- owned\_memory\_size, not dram\_size, sizes the XNU VM; the 320 MiB ceiling was lifted by the static high-bank MemoryMapLib entries \(UKE MEM \~1.11M 4K pages, free \~645 MiB\).
- A sheng-style external abort can appear at the 6 GiB top; the full 6 GiB board map is configured in board.toml.

### 完成条件

- The kernel owns the 4.75 GiB window and jetsam no longer fires at the old ceiling.

### 当前范围

- Host-only verification of the migrated ADT; the on-device counters come from the pre-migration images.

### 下一步

- Re-read the UKE MEM counters after flashing the format-2 image.

### 证据

- `device`: [UKE MEM \~1.11M 4K pages with free \~645 MiB; no jetsam past t=538s where earlier runs died at \~500s](https://github.com/Allenwdk/UniXNU-uke/blob/89c5dfa9ff61f90cdc3362e492a3fc0c5248af07/docs/PROGRESS.md)
  Command: <code>fastboot boot boot.img</code>. Revision: `c77d613dc91fb54479242aa5d5902c48662b80d7`.
- `host`: [the generated ADT matches the make-uke-adt.py baseline: identical chosen, cpus, defaults, pram and gmu-memory](https://github.com/Allenwdk/UniXNU-uke/blob/89c5dfa9ff61f90cdc3362e492a3fc0c5248af07/board.toml)
  Command: <code>python3 scripts/make-uke-adt.py (baseline diff)</code>. Revision: `23c2926941405e7df8097a6bca6ee8348a39c787`.

## 存储与根卷 {#storage}

`device-verified`

组件: `ShengUfs`, `RamBlock`, `VirtioMmioBlock`, `VirtioMmioConsole`, `VerifiedRoot`.

### 硬件与依赖

- UFS host at 0x1d84000 \(GCC windows 0x177000/0x19e000\).
- userdata GPT windows \(first\_lba 0x2d3000..\) with the OS and SystemOS components.

### 配置

- NativeUfs builds with --unverified \(bring-up transport without the verified-root policy bundle\).
- Kernel arguments native-ufs-root=1 native-ufs-allow-unverified=1, owner Data persist level 2.

### 操作步骤

- ./unixnu build package -D ../UniXNU-uke-format2; ./unixnu build userdata \(macOS\) or the recorded seed images.

### 开发经验

- TLMM per-GPIO base is 0x0f100000; reading 0x0f000000 hits unbacked space and hangs the bus.
- The owner root-binding audit is the base of the bsd\_init owner block; the other probes expect its result.

### 完成条件

- UFS enumerates, the owner Data mounts and the SystemOS volume appears.

### 当前范围

- The verified-root transport is not yet the default; userdata imaging needs macOS hdiutil.

### 下一步

- Switch the UFS transport to the verified-root policy bundle before shipping.

### 证据

- `device`: [UFS root boots and the owner Data volume mounts on hardware](https://github.com/Allenwdk/UniXNU-uke/blob/89c5dfa9ff61f90cdc3362e492a3fc0c5248af07/docs/PROGRESS.md)
  Command: <code>fastboot boot boot.img</code>. Revision: `c77d613dc91fb54479242aa5d5902c48662b80d7`.

## 显示 {#display}

`device-verified`

组件: `GopFramebuffer`, `NativeUfs`.

### 硬件与依赖

- UEFI GOP framebuffer; panel O82 3200x2136 with the splash at 0xe3940000/0x2b00000.
- Overlay-present Legacy driver and the recorded mobile-graphics ABI candidates.
- DPU track: cliffs DTB mdss\_mdp@0xae00000 \(sde-off 0x1000, VIG 0x5000/0x7000, CTL0 0x16000, INTF1/2 0x36000/0x37000, PP0 0x6a000, LM0 0x45000\), apps\_smmu 0x15000000 display streams SID 0x1c00 mask 0x02.

### 配置

- Kernel arguments offline-legacy-\* \(register, gop, phase 4\), offline-mobile-graphics-load=1.
- offline-legacy-base-present=1 and offline-legacy-noconsole=1 gate the own-present path \(the gpu-framepresent v2/v3 verified set\); without base-present presentBase returns at its first line and the screen stays on the boot frame.
- The GPU track arguments \(sheng-gpu-power=9, sheng-gpu-metal=1, offline-mobile-graphics-client=1, sheng-gpu-pool=0, sheng-fb-gpu=0\) restore the compositor's 1200-byte overlay records whose layer 6 frame the own-present path resolves.
- The default-surface fallback is disabled so only resolved overlay surfaces present.
- DPU track: uke-dpu=&lt;1\|2&gt; runs the read-only live DPU snapshot \(default off\); uke-dpu-test=&lt;1..4&gt; runs the bounded controlled-pipe test \(default off\); uke-dpu-scanout&gt;=1 builds the display bank's stage-1 window in NativeUfs \(default off\).

### 操作步骤

- Build the legacy display archive and boot with the offline-legacy arguments.

### 开发经验

- The present chain resolved the overlay layer and put real UI on screen \(white lock screen, home indicator, swipe prompt\).
- A blank after a few seconds was the blank/idle transaction falling back to the pure-black default surface; v3 presents only resolved overlay surfaces.
- 2026-10-28 fmt2 boot: the swap path rejects every frame \(UKE: swap accepted=0 reason=2 surface=0\) and the screen stays on the boot console while the system runs fully in userland; identical to the 2026-10-27 session, so the patch adoption is not the cause.
- 2026-10-28 root cause: those frozen-screen runs never set offline-legacy-base-present=1, so presentBase returned before doing anything and never logged; the accepted=0 reason=2 surface=0 line is the self-kick's pre-translation validation \(the request's +2624 surface slots fill only inside the original swap\_submit\), not an own-present resolution failure.
- presentBase now also honors the family's own second rule from swap\_submit: a record ID equal to the default surface's ID names fb+0x1618 directly \(the CPU-renderer 1288-byte records name that surface on layer 0\).
- The Data seed handoff is closed out: the scratch Data mount panic \(ENOENT at kern\_exec.c:8196\) was a missing PackedRAMDisk/TrustCache handoff in the test payload, fixed by wiring data-seed-200/owner-data-200.dbr and the owner trust cache into unixnu.local.toml.
- DPU archaeology: the cliffs DTS block offsets minus sde-off \(0x1000\) equal the DPU 9.x anchors sheng's DisplayTimingProbe uses \(VIG0/1 0x4000/0x6000, CTL0 0x15000, INTF1/2 0x35000/0x36000, PP0 0x69000, LM0 0x44000\); the stock DPU driver in this drop stops at DPU 7.x, so the DTB plus the live firmware snapshot are the register authority.
- DPU surface addressing: the display streams are SID 0x1c00/0x1c02 with qcom,handoff-smrs in the cliffs apps\_smmu node; the pipe address registers are 32-bit while XNU memory starts at 0x8C0000000, so scanout needs the ShengUfs display-bank stage-1 window \(ported as native\_ufs\_dpu\_map in NativeUfs\).
- P2 \(gpucomp26\): the compositor's two-plane 'b3a8' frame is scanned by the DPU natively. Plane 0's 4 B/texel colour words \(rows 4\*width apart\) are XRGB2101010, whose SSPP SRC\_FORMAT 0x000276ff is the firmware's own ARGB8888 word 0x000237ff \(unpack 0x03020001\) with alpha bit 8 clear and DX bit 14 set, per the stock dpu\_hw\_sspp\_setup\_format/dpu\_formats.c in the reference kernel; plane 1 is the alpha byte, whose row is the record's stride field. The 34,177,024-byte frame maps only its 27,340,800-byte plane-0 prefix into one slot; the CPU decode remains the fallback when the display-bank window is unavailable.
- gpucomp26 log \(recovery, userdata window, t=16..917 s\): UKE DPU: direct ready fmt=000237ff/000237ff unpack=03020001 tenbit=000276ff; four b3a8 frames mapped by their plane-0 prefix \(direct slot ... bytes=27340800\); UKE DPU: tenbit sample p0=18060180 p0c=37edfb7e alpha=ff/ff, so the alpha plane is 0xFF, the frame is opaque and the XRGB2101010 word order is the right one. One stall snapshot at t=78.4 s and none after; GPU commit-to-complete still averages 50.9 ms over 8884 commits in 893 s \(about 9.9/s\).
- gpucomp27 ports the upstream display's refresh tick \(GopFramebuffer 33e941a\): startVsync/vsyncTick/armVsync, getRefreshAttributes at slot 301 and setDisplayRefreshProperties in registerService, with the builder binding \_native\_legacy\_vsync\_notify \(0xfffffff005796720\) and \_native\_legacy\_set\_refresh\_properties \(0xfffffff00579ebb8\) after checking the original bytes; board.toml sets sheng-vsync=120 \(armcpu-diagnostics dropped to stay at 987 of 1000 command-line bytes\). The direct path now prints UKE DPU: flip n=... tb=... skip=... fb=... latch=...us max=...us vsync=... every 120 frames and the first eight UKE DPU: skip lines, so the next log separates compositor starvation from display-path loss.
- gpucomp27 counters: flips ran at 10-28 fps with skip=0 and fb=0, so the display path drops nothing; the latch waits for the frame boundary \(mean 4.1 ms, max 8.4 ms, one 120 Hz frame\) and the flip is tear-free. The compositor commits every 85-100 ms when idle and 12-30 ms in bursts, one full-screen pass with 60 draws over 6.68 Mpx per frame, commit-to-complete 27-41 ms; the GMU perf vote is accepted \(X v0/0, index 9 = 950 MHz, bandwidth 6\), so the frame cost is fill work, not clock.
- Flicker root cause found in the display code: dpuSlot rotated the four slots round-robin and could pick the slot the pipes were scanning, remapping that IOVA to a new surface while the pipe still fetched the old frame, one mixed frame per burst of new surfaces \(app transitions, blur effects\). gpucomp28 selects by LRU and never the shown slot \(upstream directSlot rule\) and records it after each flip.
- gpucomp28 also removes the one-frame delay: CoreAnimation completes its command buffer before submitting the swap \(the runtime WC row is its waitUntilCompleted, 29 calls, 738 ms\), and upstream flips the submitted surface; the delay only added up to a whole frame of display latency \(about 100 ms at 10 fps\).
- Open on the GPU side: SR 5 refusals of 3200x2136 surface textures \(pf80 BGRA / pf554 ten-bit\) with OutOfMemory\(Device\), and 220 GB of shadow copy-backs \(J surface cache\) over a 320 s run; both may add cost to the compositor path and need a separate look.
- gpucomp29 counted 22 drained and 1298 busy flips: the GPU ring was non-empty in 98 percent of flips, so holding each frame one swap longer did not mean holding a complete one \(the compositor submits before its work retires\). That is why transitions and blur effects kept flickering and why the first seconds after boot flashed black.
- gpucomp30 gives the direct path a completion fence: dpuPrepareFrame does the sleepable work \(slot mapping, source format\) at swap time, a work-loop timer polls native\_gpu\_idle \(the CP ring drained\) every 500 us and only then writes the registers \(dpuFlipPrepared\), forcing the flip after 30 ms and counting it \(fence=drained/forced\) so a ring that never drains cannot freeze the panel; dpuSlot now avoids both the shown and the pending slot and a newer frame replaces one still waiting.
- The CPU levels are logged again without a new boot argument: CpuFreqProbe runs its read-only mode on the GPU track \(sheng-gpu-power&gt;=9\), reports the level each EPSS domain runs at \(f&lt;MHz&gt;, LUT\[perf\_state\]\) and logs UKE CPU: ...; the windows are 0x17d91000/0x17d92000/0x17d93000, referenced by the vendor crash-dump link lists.
- gpucomp30 showed that CP\_RB\_RPTR==CP\_RB\_WPTR is not a completion signal \(the CP has read the commands, the pixel work may still run\), so that fence behaved like the unfenced gpucomp28: everything that moved flickered.
- gpucomp31 takes the fence from the only party that knows: the plugin Metal runtime. NativeGOPWire gains NGP\_DIRECT \('DIRC'\), the presenter offers it when sheng-fb-gpu=1 and uke-dpu-scanout&gt;=3, the client waits in NBWaitInFlight for every command buffer committed before the offer \(exactly this frame's work, the earlyOn gate removed\) and completes, and the display flips its pipes in that completion \(completeDirect\) with a 100 ms watchdog that drops an unanswered frame; clients without the mode are refused and the display keeps its own timing.
- The plugin had to be rebuilt for the direct mode \(CDHashes c063675e/4be6b25b/ee022a5f, owner trust regenerated, addon blob 21,178,648 bytes, 12 entries\). On Linux the plugin build must not pass -fuse-ld=lld: the iOS xcrun wrapper already injects --ld-path to its ld shim, and the two together hand clang driver flags to ld64.lld.
- gpucomp37 measured the GPU path itself: a 27 MB fill takes 14.8 ms \(1.76 GB/s\) and a copy 13.9 ms \(3.75 GB/s\), so the compositor's \~67 MB of shadow traffic per frame is about 18 ms before any rendering. The bottleneck is GPU-to-host memory throughput, not shading.
- Upstream was fetched with its feature branches: NativeAdreno feat/ipados27-gpu-parity \(14 commits, 2026-10-29 02:39\) carries the work that targets this exactly - cache maintenance counted per phase with uncached imports skipped \(its message: the 1.5 GiB pool took 41 ms with preemption off\), no XNU contiguous search when the pool exists, BO pool growth in chunks, on-demand GPU page tables, msm hangcheck with restart. ArmSmmu4K has the matching feat branch \(30ec63b, page tables on demand\).
- gpucomp38 is those branches merged: our nine A732/GMU commits rebased onto the adreno feat branch with the conflicts resolved \(borrow and adopt side by side, the GMU pool adopt taking only the five payloads because page tables are on demand now, the GPU pool adopt for the five buffers, at\(i\) for the grown entry table, dropViews split into a locked form and a wrapper\), plus a weak native\_pmap\_user\_mappings stub and a UKE GPU: maint phase row. The SMMU kit is the feat commit; the build needs --local-module kit:ArmSmmu4K= that checkout.
- Local toolchain fixes on the way: build-arm-driver.py dropped the recipe's -Wno-missing-designated-field-initializers and -Wno-unused-but-set-global, which made clang reject the XNU headers and then assert inside RecordLayoutBuilder \(the earlier 'clang frontend command failed due to signal'\); both are back, and a compile that dies by signal is retried.
- The upstream feature branch was merged and boots: gpucomp46 \(kernel 15ad83d8, payload 48967bf0\) ran 918 s with conn switch=0 cp=0 mode=1 mount=0/0 shared=0 tables=10/1 in=31 out=40, o2/0/1 and fence=4892/28 \(99.4 percent fenced, drops down from 11-12 percent\), gpu=12.1 ms offer-to-completion. The per-process client address space works on the fused 31-bit aperture because clientWindow\(\) places every client at 0x10000000 + 1.75 GiB \(its own page tables make the same window free for all of them\); createVm, setScope and the client opens then all succeed.
- A later boot of the same image panicked with OSMetaClass::applyToInstances+0xf4 \(caller OSKext::loadExecutable, pc 0xfffffff007904548, esr 0x56000004 SVC, x8 NativeLegacyDisplay::getMetaClass\); the string resolves to '&gt;maxDepth' at libkern/c++/OSMetaClass.cpp:1118, i.e. a metaclass superclass chain deeper than sDeepestClass. That is kernel data being overwritten, and it appeared only after the feature branch's per-process address spaces and on-demand page tables, intermittently \(one boot 918 s clean, the next panics during kext load\).
- The gpu\_qcom\_scm aperture call \(SVC\_MP 0x0c / cmd 0x1b, ARGS\(4\)\) succeeds for context banks 0-3 but the SMMU keeps reporting a 31-bit stage-1 input \(in=31\), so the upstream 2^ias model cannot be used here; the client window is what adapts instead.
- Panic capture: the pram hand-off \(uke\_panic\_flush\) produced no UKE PANIC line and a variadic call to the kernel printf printed only the prefix \(Darwin passes variadic arguments on the stack\), so the panic screen now copies its text into uke\_panic\_shadow \(exported by the probe\) and the probe heartbeat prints it; the screen also mutes the console on entry and draws only the message at scale 3.
- The revert to the bootable baseline exposed how a local build picks its driver: feeds.toml's Adreno740 commit \(f1a2aee, the m9f-era tip\) is documentation only for a local= source, and the build stages whatever that checkout has. gpucomp47/48 therefore built with f1a2aee and rendered on the CPU, while the image that rendered on the GPU was gpucomp37, built from uke-a732-single @ c950906 \(the local A732 commits rebased onto upstream perf/gpu-smoothness\). The two payloads' kernel.macho symbol tables settle it: gpucomp37 has retiredReaper, NativeAdrenoRing::kick/writeWptr, native\_adreno\_stall\*/ring\_window/wptr\_fence/unstick, AGXDeviceUserClient::dropViewsLocked and NativeAdrenoHandleIndex; f1a2aee has none of them. gpucomp49 \(driver c950906, plus the probe's pool\_mib write before bring-up and the &\#123;1,9,6&\#125; initial HFI vote that the same commit had\) has exactly gpucomp37's kernel size \(52,281,344 B\) and differs only in \_\_LINKEDIT \(216 B\) and the six omitted feat telemetry symbols; user-verified on device on 2026-10-29.

### 完成条件

- A known frame appears with correct geometry and colors and stays up.

### 当前范围

- The GPU compositor now renders through the mainline stack \(Adreno740 5c8c145, ArmSmmu4K 3ba9245, AdrenoMetal ce5e19e, Turnip rebuilt for the new driver ABI\); uke-dpu-scanout=3 scans the compositor's BGRA surfaces directly with a one-frame delay, about 15 fps on device.
- GPU commit-to-complete averages 51 ms \(9.7 commits/s, worst 1.1 s\) over 8892 commits, with 6 failed commits; STATUS3 bit24 \(SMMU stalled\) during KaleidoscopePoster blur effects, recovered by the upstream stall handler after about 1 s.
- b3a8 two-plane frames now present through the direct path; the CPU plane decode remains only for a board without the display bank's stage-1 window.
- The direct path still polls CTL\_FLUSH synchronously \(cap 100 ms, measured about 1 ms\) and delays one frame; the upstream non-blocking latch timer is not ported yet and the display/DRAM bandwidth vote is still missing.

### 下一步

- The baseline is gpucomp49 \(driver c950906, display cd8a7b2, metal 739de5b, feeds pinned to c950906\): GPU compositing through the DPU direct path with the plugin fence, about 30 fps on device.
- The parked feature track \(docs/DPU-TASKS.md §28\) resumes with isolation tests: single client, forced shared VM, sheng-gpu-ttbr=1/2, then TTBR0 switching timing and a memory canary, to explain the OSMetaClass &gt;maxDepth corruption before the per-process address spaces are adopted again.

### 证据

- `device`: [real UI on screen: white lock screen, home indicator and the swipe prompt; then v3 presents only resolved overlay surfaces](https://github.com/Allenwdk/UniXNU-uke/blob/89c5dfa9ff61f90cdc3362e492a3fc0c5248af07/docs/GPU-PORT.md)
  Command: <code>fastboot boot boot.img</code>. Revision: `c77d613dc91fb54479242aa5d5902c48662b80d7`.
- `device`: [the verified gpu-framepresent v2/v3 argument set \(recorded from uke-port/releases/2026-10-24-gpu-framepresent-v3/README.md\), now restored in board.toml](https://github.com/Allenwdk/UniXNU-uke/blob/89c5dfa9ff61f90cdc3362e492a3fc0c5248af07/docs/GPU-PORT.md)
  Command: <code>fastboot boot boot.img</code>. Revision: `ad87339f293a0e55c4a5be25188bdfca8ecea700`.
- `source`: [kernel\_args carry that set; the joined boot-args string is 881 bytes, under the 1000-byte limit](https://github.com/Allenwdk/UniXNU-uke/blob/89c5dfa9ff61f90cdc3362e492a3fc0c5248af07/board.toml)
- `source`: [A1/A2 register map: DTS block offsets, MDP-relative anchors, SSPP/CTL/INTF/PP/LM registers, dispcc/GCC clocks, GDSC, apps\_smmu SIDs, stock init sequence with source lines](https://github.com/Allenwdk/UniXNU-uke/blob/89c5dfa9ff61f90cdc3362e492a3fc0c5248af07/docs/dts-reference/mdss-cliffs-map.md)
- `source`: [M1 gate: DTS anchors, stock register defines, NativeUfs window symbols and the built DpuProbe.o all pass \(source-only and archive checks\); a deliberately wrong kVig constant turns it red](https://github.com/Allenwdk/UniXNU-uke/blob/89c5dfa9ff61f90cdc3362e492a3fc0c5248af07/scripts/check-dpu-probe-host.py)
- `source`: [A3/C1/B2/C2/C3 implementation and the test ladder; boot identical to framepresent4](https://github.com/Allenwdk/UniXNU-uke/blob/89c5dfa9ff61f90cdc3362e492a3fc0c5248af07/docs/DPU-PORT.md)
- `device`: [M1 PASS: UKE DPU probe=1 snapshot shows GOP e3940000 3200x2136, VIG0/VIG1 1600x2136, 120 Hz, display SMMU bank 2 CBAR type 1 / SCTLR 0xe0](https://github.com/Allenwdk/UniXNU-uke/blob/89c5dfa9ff61f90cdc3362e492a3fc0c5248af07/docs/DPU-PORT.md)
  Command: <code>fastboot boot vendor_boot_uke_dpu_a3.img</code>. Revision: `3c65101d7ce614a3c2520c4fb5c2b5ac2dd42657`.
- `device`: [M2/C3 PASS: redirecting VIG0/VIG1 to gop+0x800000 \(1600x1068, stride 0x3200\) drew red/green/blue/checker correctly for 2 s each, src0 readback e4140000, auto-restore; low-DRAM e5400000 shows gray \(outside the display-readable GOP range\)](https://github.com/Allenwdk/UniXNU-uke/blob/89c5dfa9ff61f90cdc3362e492a3fc0c5248af07/docs/DPU-PORT.md)
  Command: <code>fastboot boot vendor_boot_uke_dpu_c3c.img</code>. Revision: `3c65101d7ce614a3c2520c4fb5c2b5ac2dd42657`.
- `device`: [B2 PASS: stage-1 window state=80000002 on bank 2; test=3 mapped a 27.3 MB BGRA buffer at IOVA 0x10000000 and the DPU scanned it \(latch 1196 us\); fix was Linux arm-smmu SCTLR 0x10e7 / TCR 0x803519 / TCR2 0x38015 with a 4xL2 2MB-block table; the S2CR bypass experiment b2v4 crashed and was reverted](https://github.com/Allenwdk/UniXNU-uke/blob/89c5dfa9ff61f90cdc3362e492a3fc0c5248af07/docs/DPU-PORT.md)
  Command: <code>fastboot boot vendor_boot_uke_dpu_b2v8.img</code>. Revision: `3c65101d7ce614a3c2520c4fb5c2b5ac2dd42657`.
- `device`: [D1b PASS: presentBase maps each BGRA IOSurface into a stage-1 window slot and flips VIG0/VIG1 with no CPU copy; user reports clearly smoother \~10 fps and mostly correct output, with artifacts in some scenes \(suspect GPU in-flight surface reuse; next: fence or one-swap delay\)](https://github.com/Allenwdk/UniXNU-uke/blob/89c5dfa9ff61f90cdc3362e492a3fc0c5248af07/docs/DPU-PORT.md)
  Command: <code>fastboot boot vendor_boot_uke_dpu_d1b.img</code>. Revision: `3c65101d7ce614a3c2520c4fb5c2b5ac2dd42657`.

## 输入 {#input}

`device-verified`

组件: `ShengHidInput`, `ShengNovatekTouch`, `QcomGeniSpi`.

### 硬件与依赖

- Novatek NT36532 \(o82 firmware, csot and tm variants\) over Qcom Geni SPI.
- HID delivery through the workloop \(NativeHidInput runAction on the touch thread\).

### 配置

- 60x40 scan geometry; TLMM per-GPIO base 0x0f100000; poll mode frames flow after first valid frame type 4.
- Kernel arguments offline-hid-home=1 offline-hid-input=1 offline-key-events=1.

### 操作步骤

- Boot with the touch diagnostics and read the UKE TCH counters.

### 开发经验

- Full bring-up runs on device through stage 4: firmware download CRC-ok and scanning 60x40.
- The v3 argument set is sheng-fb-gpu=0 plus offline-legacy-base-present=1; the desktop-era fb-gpu=1 hangs identically.

### 完成条件

- Frames reach HID and the on-screen swipe responds.

### 当前范围

- The on-screen swipe and coordinate mapping are the remaining break after the migration.

### 下一步

- Fix HID delivery/coordinate mapping, then re-enable base-present with the v3 argument set.

### 证据

- `device`: [UKE TCH: scanning v11 pid5993 60x40 with hb/drv/rpt counters advancing](https://github.com/Allenwdk/UniXNU-uke/blob/89c5dfa9ff61f90cdc3362e492a3fc0c5248af07/docs/TOUCH-PORT.md)
  Command: <code>fastboot boot boot.img</code>. Revision: `c77d613dc91fb54479242aa5d5902c48662b80d7`.

## GPU {#gpu}

`device-verified`

组件: `Adreno740`, `AdrenoMetal`, `AdrenoFirmware`, `AdrenoPM4`, `ArmSmmu4K`, `Sm8550Platform`, `AirNir`.

### 硬件与依赖

- Adreno 732 \(chip 0x43030b00, gen7-11-0\) with the gen71100 firmware triplet pinned in proprietary-files.txt.
- GMU pool 0xC8000000/32 MiB adopted with a write-combine mapping \(a plain mapping aborts on DC ZVA\).

### 配置

- \[gpu\]: the A732 clock plan \(9 power levels\), gmu\_chip\_id 0x70b0000, ubwc 4, highest\_bank\_bit 16.
- Kernel arguments offline-mobile-graphics-client=0 sheng-gpu-power=9 sheng-gpu-metal=1 \(the desktop track\).

### 操作步骤

- Build the GPU archives and boot the staged modes; read the G1..G0/P0/S0/heartbeat counters.

### 开发经验

- Staged modes 1/3/4/5/6/7/8/9 pass: GMU SMMU context Ready, command DB v1 parses p0, PLL1 locked, GX off/on with the perf vote, the Metal publish, and the user stream with F0 r3b/3b G0 q3 u0.
- A successful pool adopt needs an adopted\_pool guard or the VM fallback returns kIOReturnBusy; the secure SMMU stream SMR write aborts, so the context is single-route.

### 完成条件

- The Metal accelerator publishes and a user stream renders; the scanout shows frames.

### 当前范围

- The format-2 kernel has not yet run the mode ladder on hardware \(host-only verification\).

### 下一步

- Flash and re-run modes 7-9, then continue the Metal accelerator plus scanout work.

### 证据

- `device`: [mode 9 passes with the kernel Metal publish \(M ... s5/0 r1\) and the user stream heartbeat F0 r3b/3b G0 q3 u0](https://github.com/Allenwdk/UniXNU-uke/blob/89c5dfa9ff61f90cdc3362e492a3fc0c5248af07/docs/GPU-PORT.md)
  Command: <code>fastboot boot vendor_boot_uke_gpu_m9l.img</code>. Revision: `c77d613dc91fb54479242aa5d5902c48662b80d7`.
- `host`: [the gen71100 firmware triplet hashes match the board pins](https://github.com/Allenwdk/UniXNU-uke/blob/89c5dfa9ff61f90cdc3362e492a3fc0c5248af07/proprietary-files.txt)
  Command: <code>sha256sum .cache/firmware/uke-gpu/*</code>. Revision: `23c2926941405e7df8097a6bca6ee8348a39c787`.

## 网络 {#network}

`not-applicable`

### 硬件与依赖

- The board has no network driver in this port.

### 配置

- No network component is selected; the kernel runs with IF\_HEADLESS.

### 操作步骤

- Nothing to run.

### 开发经验

- The port boots and tests over serial and the local display only.

### 完成条件

- Out of scope: no network bring-up is planned for the first boot target.

### 当前范围

- Wi-Fi and Bluetooth are not in scope; the catalog lists Ath12kWifi for boards that need it.

### 下一步

- Revisit if userland networking becomes a goal.

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`not-applicable`

### 硬件与依赖

- No audio codec bring-up in this port.

### 配置

- The ADT product node keeps the audio routing properties of the OS identity only.

### 操作步骤

- Nothing to run.

### 开发经验

- Audio is carried by the OS identity properties; no board codec work has started.

### 完成条件

- Out of scope for the current bring-up goals.

### 当前范围

- The speaker path is untested.

### 下一步

- Revisit after the display and input goals.

### 证据

按下一步操作收集证据。

## 电源 {#power}

`device-verified`

组件: `Adreno740`, `AppleKeyStoreState`.

### 硬件与依赖

- PMGR power policy and the GMU voltage/clock voting over the AOSS/RPMH path.
- Hardware watchdog policy \(sheng-disable-watchdogd=1\) and the gh\_virt\_wdt pet.

### 配置

- Kernel arguments sheng-pmgr=2 sheng-lite=1 sheng-aks=1 sheng-disable-watchdogd=1.
- GMU core 220 MHz / hub 200 MHz with the validated vote sequence.

### 操作步骤

- Boot the staged power modes and read the GX/S0 heartbeat rows.

### 开发经验

- Mode 8 passed: GX off/on and the perf vote acked with the heartbeat H0.. every 2 s.
- The scm secure-watchdog path is a dead end; the gh\_virt\_wdt pet is accepted and disable is refused.

### 完成条件

- GPU power states transition and the board keeps running with the watchdog policy applied.

### 当前范围

- Suspend/resume is not implemented \(the ADT defaults pin sleep-disabled=1\).

### 下一步

- Keep the watchdog policy documented; revisit sleep only after userland is stable.

### 证据

- `device`: [mode 8 passes: GX off/on with the perf vote and the H0.. heartbeat every 2 s](https://github.com/Allenwdk/UniXNU-uke/blob/89c5dfa9ff61f90cdc3362e492a3fc0c5248af07/docs/GPU-PORT.md)
  Command: <code>fastboot boot vendor_boot_uke_gpu_m8.img</code>. Revision: `c77d613dc91fb54479242aa5d5902c48662b80d7`.

## 镜像组装 {#packaging}

`host-verified`

组件: `DarwinBoot`, `XnuPrelink`, `VerifiedRoot`.

### 硬件与依赖

- Stock vendor\_boot DTB with the board's dtb\_node patches \(splash reservation, payload at 0x1000000\).
- Trust cache bundle and the recorded Data seed.

### 配置

- \[payload\]: volume UKEESP, 80 MiB, loader firmware, panic\_screen true, 35 kernel arguments.
- \[bootimg.image\]: v4 header, page 4096; the stock DTB keeps its /chosen and gains the initrd nodes.

### 操作步骤

- ./unixnu build payload --kernel kernel.macho --unique-chip-id HEX -D ../UniXNU-uke-format2
- ./unixnu bootimg --uefi ../uefi-uke --dtb ../uke-port/data/vendor\_boot.dtb --ramdisk none -D ../UniXNU-uke-format2

### 开发经验

- The v4 header parsing and the existing-/chosen fdtput tolerance stay board-side; upstream expects a fresh /chosen.
- payload.img and boot.img build on Linux; userdata imaging and skip-setup still need macOS.

### 完成条件

- payload.img contains unixnu.toml, kernel.macho and its ADT; boot.img boots from the stock DTB.

### 当前范围

- Host-only verification; the platform seed is not stored in any repository and was substituted for the structural build.

### 下一步

- Build with the real unique\_chip\_id and flash the inactive slot.

### 证据

- `host`: [payload.img 80 MiB with the UKEESP volume and boot.img 1,515,520 bytes over the stock vendor\_boot DTB](https://github.com/Allenwdk/UniXNU-uke/blob/89c5dfa9ff61f90cdc3362e492a3fc0c5248af07/board.toml)
  Command: <code>./unixnu build payload &amp;&amp; ./unixnu bootimg --uefi ../uefi-uke --dtb ../uke-port/data/vendor_boot.dtb --ramdisk none</code>. Revision: `4f4bf7e1f4ad56743562777becd7ac7d6714216c`.
- `device`: [the fmt2 test image booted to userland on hardware with the recovered platform seed and the Data seed handoff](https://github.com/Allenwdk/UniXNU-uke/blob/89c5dfa9ff61f90cdc3362e492a3fc0c5248af07/docs/GPU-PORT.md)
  Command: <code>fastboot flash boot_a vendor_boot_a &amp;&amp; fastboot set_active a &amp;&amp; fastboot reboot</code>. Revision: `bdb1af9a7100367cde283ff5408681de8fbbcfe3`.

## 诊断 {#diagnostics}

`device-verified`

组件: `AppleKeyStoreState`, `XnuPrelink`.

### 硬件与依赖

- Embedded panic log at 0xFF800000/0x380000 read by the menu before XNU clears it.
- Boot progress stages and the uke log ring \(sheng-log=1\).

### 配置

- panic\_screen true with the vendored Font.h; boot-progress=2 for the stage bars.
- UKE MEM counters \(gUkeMemStatusGuid\) and the previous panic line on the menu.

### 操作步骤

- Boot with boot-progress=2 and read the menu status, then the kernel log.

### 开发经验

- The panic screen, ramoops print and the last-panic line work; the jetsam OOM vs corpse messages are distinguished in the log.
- The migration's own diagnostics: from-scratch kernel builds and the ADT baseline diff run on the host.

### 完成条件

- Failures leave a readable panic line on screen and in the log.

### 当前范围

- The unattended reset cycle covers the GPU track only.

### 下一步

- Wire the format-2 boot into the unattended test loop.

### 证据

- `device`: [the panic screen and last-panic line read back from the reserved pram log on hardware](https://github.com/Allenwdk/UniXNU-uke/blob/89c5dfa9ff61f90cdc3362e492a3fc0c5248af07/docs/RECOVERY-LOG.md)
  Command: <code>fastboot boot boot.img</code>. Revision: `c77d613dc91fb54479242aa5d5902c48662b80d7`.
- `host`: [kernel, payload and boot images build end to end at the format-2 output path](https://github.com/Allenwdk/UniXNU-uke/blob/89c5dfa9ff61f90cdc3362e492a3fc0c5248af07/board.toml)
  Command: <code>./unixnu build kernel &amp;&amp; ./unixnu build payload &amp;&amp; ./unixnu bootimg</code>. Revision: `4f4bf7e1f4ad56743562777becd7ac7d6714216c`.

</div>
