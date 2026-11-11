# umi Adreno 650 bring-up: hand-off for the next session

## The kernel bring-up (2026-10-26, patches 0160-0170): all 23 steps green

The Xiaomi Mi 10 (umi, SM8250) runs iOS 16.7 on our XNU port. The Adreno 650 bring-up lives in
`bsd/dev/sweet_adreno.c` (kernel patches 0160-0170 in `xnu/patches/`). It runs only with boot-arg
`sweetgpu=N` (steps 1..N). **All steps 1-23 have worked on the phone (0170: step 22's 2D fill and step 23's
indirect-buffer submission with fence both pass).**

| Steps | Patch | What | Result |
|---|---|---|---|
| 1-3 | 0160 | read GCC GPU clocks, cmd-db rails, speed-bin fuse, gpucc | clean, unpowered GPU; speed bin 0 |
| 4-6 | 0161 | CX GDSC on, GMU clocks (200 MHz), first GMU reads | GMU always-on counter counts |
| 7-11 | 0162 | RSCC, SMMU (MMU-500, 5 contexts), GMU memory test, TrustZone queries | TrustZone answers our SMCs |
| 12 | 0163 | zap shader signature (pas_init_image 13) | accepted |
| 13-15 | 0164-0165 | SMMU context 1 for the GMU, a650_gmu.bin, RPMh/PDC init, GMU start | firmware runs (0x100) |
| 16-17 | 0165 | HFI queues, perf + A650 bw tables, start, 305 MHz, oob GPU_SET | 3D core has power |
| 18 | 0166-0167 | SMMU context 0 for the core: ring, a650_sqe.fw, scratch | works with SMR stream 0 / mask 0x401 |
| 19 | 0166 | zap shader loaded through TrustZone (0x8681a000) | authenticated and started |
| 20 | 0166 | A650 hw_init, CP_SQE_CNTL 1, CP_ME_INIT | command processor runs |
| 21 | 0166 | CP_SET_SECURE_MODE 0, CP_MEM_WRITE | 0x600dc0de read back |
| 22 | 0168 | 2D-engine solid fill (red/green/blue) into the panel framebuffer | seen on the panel, pixels exact |
| 23 | 0169-0170 | memory objects above 4 GB, CP_INDIRECT_BUFFER submit, CACHE_FLUSH_TS fence | magenta/yellow/cyan + data words exact, fence signalled |

Logs: `research/logs/umi-016x-gpu*.txt` (`umi-0167-gpu21`, `umi-0168-gpu22`, `umi-0169-gpu23`, `umi-0170-gpu23`).
Full history with every value: NOTES.md (umi section, top).

Lessons:
- The hypervisor grants an SMMU stream match only for the device tree's exact stream/mask pair (GMU 5/0x400,
  GPU 0/0x401). Stream 0 with mask 0x400 was silently refused (SMR reads back 0).
- The SMMU context's SCTLR keeps bit 8 (HUPCF) but drops bit 12.
- The phone's own a650_sqe.fw is version 0x093 (Linux wants >= 0x095 for security fixes); it runs.
- On the last step every announce/put waits `sweetgpupause` ms (2.2 s). Hold anything time-based until
  after the work (step 22: `sweet_fb_gpu_begin` holds 60 s at most, `sweet_fb_gpu_show(ms)` after drawing).
- The 2D engine's pitch must be a multiple of 64 bytes; the panel's rows are 4320, so step 22 treats
  two rows as one (8640 = 135 x 64).
- `CP_EVENT_WRITE` with bit 30 (TIMESTAMP, as Mesa's A6XX event writes) stores a timestamp, not the
  packet's value; for a fence word use the event without bit 30 (Linux a6xx_submit).
- CP protect (0171): Linux's a650 table has 39 entries but 48 CP_PROTECT registers - entries 0..37 go
  into CP_PROTECT(0..37), the infinite-range entry into CP_PROTECT(47), 38..46 stay untouched. Writing the
  entries consecutively leaves register 47 = 0 and LAST_SPAN_INF_RANGE blocks every command register write.

Every step announces its accesses and waits `sweetgpupause` ms so the persistent log survives a reset.
Writes go through `sa_put()` and are recorded; at the end of a run they are undone in reverse order,
except once the 3D core has been powered (then everything is left on and TrustZone keeps the zap
shader; the next restart resets the SoC).

## The solved problem (0169/0170): the CPU wrote over the GPU's pixels

In the 0169 boot (`sweetgpu=23`) the GPU steps ran before iOS's first frame, and the green band read back
0xff000000: an opaque black pixel written by the CPU after `sweet_fb_gpu_begin()` cleaned the framebuffer from
the cache - the kernel text console (drawing until the first swap mutes it) or a `AppleCLCD::present()` frame
copy racing the hold; printf/IOLog order could not tell which. **0170 fixed it: `sweet_fb_gpu_begin()` now sets
the hold and cleans the cache inside the framebuffer workloop's gate (`fWorkLoop->runAction`, no present() at
the same time), mutes the console for the hold (`sweet_console_muted`, put back when the hold ends in
`vsyncFired`, also display-off), and the power-off fade is skipped while held.** Hold-related GPU and FB lines
carry `mach_absolute_time()` stamps. The 0170 boot passed all 23 steps (step 22's bands exact again). One
interplay to remember: backboardd turned the display off ~6 s into a hold, so step 23's `sweet_fb_gpu_begin`
was refused (it always refused display-off) and it drew anyway; the fade-skip kept the panel on the GPU's
picture through the "off", so the colours were still shown.

## GPU hang root cause (2026-10-29, patch 0200)

The intermittent CP_OPCODE_ERROR / stuck-fence hang was a race in the kernel's v2 (Turnip) client:
BoMap's page list (fPageBuf) and the BO table are one per client and were used without a lock while
Turnip calls from several threads. Concurrent BoMaps mapped each other's pages; the GPU ran other
buffers' memory as commands. Kernel 0200 serialises the v2 methods (WaitFence excepted). Diagnostics
0188-0199 (hang dump with IB positions, free history, submit-time IB walk, page comparison, map log)
remain in the kernel. **Confirmed on the phone: a 0200 boot ran to fence 5105 with zero diagnostic
hits (research/logs/umi-0200-run.txt).** Next: trim the diagnostics, the Turnip BO log and the
diagnostic boot-args; then direct scanout. See NOTES 0199/0200.

## Where things stand (2026-10-29, patches 0160-0187): THE UI IS ON THE PANEL

**The iOS home screen renders correctly through Metal -> metal2vulkan -> Turnip -> A650 (copy path,
sweetfb_direct=0), icons included.** The "present race" theory below was wrong: Turnip had two wrong
device-info values from SweetAdreno.

- **0186: gmem_base must be 0 on the A650** (Linux v6.12 adreno_gpu.c MSM_PARAM_GMEM_BASE: 0 for the
  a650 family). With 0x100000 every GMEM access through a texture (Turnip's unaligned tile stores,
  input attachments) read uninitialised SRAM: the full-screen noise (random words, ~63% bits set).
- **0187: macrotile_mode must be 1** (a6xx_calc_ubwc_config A650; step 20 already writes
  RBBM_NC_MODE_CNTL 1). With 0 tiled/UBWC textures were tile-shuffled (the icons).
- **0185: IOSurfaces are cleaned at CPU write-unlock** (trap 3), so CPU drawing into surfaces the GPU
  keeps mapped reaches memory. Keep: no submit-time clean of imports.
- Lesson: when output looks like never-written memory, check every value the kernel hands to
  Turnip (GetDeviceInfo / msm params) against Linux before suspecting sync.

Open, in order: (1) **random GPU hang**, two kinds seen: CP_OPCODE_ERROR on a zero dword (0187, fence
835) and CP busy in a wait with no error (0188, fence 713, IB1 starts with CP_COND_WRITE5). All captured opcode errors
are opcode 0: the CP executed zeros; 0191 shows IB1/IB2 valid, so the zeros are in a CP_SET_DRAW_STATE
group (pipeline/suballocated state freed or reused while referenced). 0193 (submit-time IB walk) found every IB
well-formed at submit, and CP_INTERRUPT_STATUS is never cleared by us (its opcode bit may be stale).
0195 + phone/turnip/0001 fixed overlapping iovas
between two Turnip devices per process; still open: fresh command BOs read zero at submit after a
host import's iova is reused (NOTES 0194/0195) - compare GPU PTE page vs the BO's own pages next; (2) direct scanout re-arm after the display off/on cycle; (3) drop the diagnostic
boot-args (sweetfb_dump, finwait 10000, finrounds 6) once the hang is understood. Current image:
`shim/out/umi-0187-macrotile.img`.

## Earlier state (2026-10-28 night, patches 0160-0183) - superseded

The Metal stack creates real Turnip A650 devices in backboardd and SpringBoard and compiles
CoreAnimation shaders/pipelines. **The UI is correct end to end SOMETIMES: the user photographed a
completely clean frame ("What's New in Photos" welcome card) alternating ~1 s good / 1 s glitchy.
The noise is a present-vs-render race, not broken output.** All "fundamentally broken" theories
(stride, layout, tiling, import mapping) are dead.

1. **The race (priority).** The frame the kernel copies is garbage in the middle (white noise,
   coherence ~75/255) and all-zero at the top-left, BOTH at present time and in idle samples
   (0182's idledump), and `finish ok` (the newest fence signalled) does not change that. Waiting
   10 s instead of 0.5 s for the newest fence before the copy (0183, `sweetfb_finwait=N ms`) did
   NOT fix the screen: the fence the kernel waits is not this frame's. The sync has to come from
   the presentation path in user space: CA's render server in backboardd sends the framebuffer
   swap (AppleCLCD sel 79/74) off the Metal command buffer's completion, but the drawable's
   composite is still running (or the double-buffered surface is already reused for the next
   frame) when the kernel copies it - one drawable holds the completed frame (the good 1 s), the
   other gets copied mid-render (the glitchy 1 s; the 4x4-duplicated glitch patterns are
   mid-render blur-chain content). The bridge does NOT implement drawables/presentation
   (NativeBridgeMetalFrontend.mm line 8) - trace where the swap is ordered against command
   buffer completion in the runtime and make it wait.
2. **Direct scanout** unchanged (CTL_FETCH never re-arms after the hold/off cycle; COPY is the
   workaround - do not spend time here before (1) is fixed).
3. **Intermittent CP_OPCODE_ERROR** unchanged; reproduce on a long interactive boot (the dump is
   armed; the 0182/0183 boots had none).

**vktest import test (A-E matrix)** is on the phone (/private/var/sweet/vktest): the drawable's
linear-import path measured for coherency in both directions; results tee to
/var/local/vktest-results.log (launchd's stdout redirect loses output; the run marker is
/var/local/vktest-run.log). It was SIGKILLed by memory pressure at 11 MB and shrunk to 512x512.
So far: device up, only VK_KHR_external_memory advertised of the three probed, empty/fill/compute
PASS; A-E pending a clean boot. **Gotchas: the UDP relay re-streams the persistent ring's tail
after each reboot (old-boot lines reappear); the Mac's en8 alias drops on USB re-enumeration
(re-run tools/umi-usbnet.sh); the phone's ue0 once died on re-enumeration (replug the cable);
kernel [t] stamps are mach_absolute_time ticks @19.2 MHz (verify with a copydump tns pair).**

Latest kernel commits:
- **0179, 761390e:** preserve the prior session's fix excluding imported BOs from submit-time
  cache cleaning. Imports are cleaned at BoMap. Never restore cleaning imports at every submit.
- **0180, 29b1da4:** preserve sweetfb_srcbpr and add opt-in `sweetfb_dump=1` COPY diagnostics.
  After GPU sync and source cache maintenance, three captures starting at 400 s uptime, at least
  30 s apart: two 64x32 pixel regions, row RGB/alpha/black-pixel sums, full geometry, and bounded
  rejection logs. Dumps are observational; they do not fix the corruption.

Both files passed per-file cross-compilation; local kernel build succeeded (log
`/tmp/umi-0180-build.log`). Image `shim/out/umi-0186-copydump.img` uses the 0184 boot line/ADT
with normal source stride and sweetfb_dump=1. Payload fits the existing ramdisk page count;
DTB verified byte-for-byte against check-0176m/dtb. RAM boot succeeded, but it panicked before capture: fence 2511 stalled near 350 s,
then FlushPoC_DcacheRegion faulted at PC 0xfffffe000748482c, LR 0xfffffe0007483c54,
FAR 0xfffffe002c868000 (user photo). No copydump records; neither UDP nor the last persistent
ring flush contains the hang header or panic. Logs: research/logs/umi-0186-panic-live.txt and
umi-0186-panic.txt (TWRP pull explicitly agreed).

**0181, 6675b52:** fix the old hang reader's invented pa-gPhysBase+gVirtBase mapping, which
bypassed arm_vm_init.c's ptov_table. Read-only GPU page-table walk under the service mutex;
valid PTE and managed RAM checks; phystokv translation verified against the kernel mapping;
copy eight words honoring the IB page offset. This addresses the diagnostic's unsafe read,
not the GPU hang itself. Also start COPY dumps at 180 s by default (sweetfb_dump=N>1 selects
another uptime in seconds), still three captures 30 s apart. Per-file checks and local build
passed (/tmp/umi-0181-build.log). Image shim/out/umi-0187-safe-copydump.img RAM-booted;
DTB matches check-0176m, payload page count unchanged. Capture pending in /tmp/umi-0187-live.log.
Decoder: python3 tools/umi-fb-copydump.py LOG OUTDIR (Pillow; flags missing UDP pixels).

**0182, kernel 8a31d99:** the 0187 boot proved the noise is in memory (see item 1 above), and
that the present-time dumps could not fire again: their gate wanted a >=64x32 present rect,
which CA only carries for a full-screen present (the lock screen ticks with small damage rects).
0182 makes `sweet_adreno_finish` report whether the newest fence signalled within the 500 ms cap
(present logs it), adds a per-present swap-rect log, moves the copydump's regions to the
surface's own fixed points so any present dumps, and adds the **idledump**: the vsync timer
samples the pending frame's surface every 30 s from 180 s uptime, away from present - what a
completed frame holds in memory (six captures, sweetfb_dump=N unchanged). Cross-compiles and
local build clean (/tmp/umi-0182-build.log). The extended vktest (test_import, A-E coherency
matrix on the drawable's exact IOSurface/import path) was pushed to the phone over the file
server as /private/var/sweet/vktest; it runs at boot and writes /var/local/vktest.log. Image
shim/out/umi-0182-copydump.img (0187's boot line, in-place payload swap, kernel+DTB verified
against check-0182-base/check-0176m) RAM-booted; 0187's live log saved as
research/logs/umi-0187-copydump-live.txt. Pending: the A-E matrix and the 0182 boot's
idledump/presrect/finish logs.

0179/0180 were pushed as ios-sweet commit 4e63ae2; CI 40754611687 remained queued with no
runner at the last check. 0181 publication and subsequent device evidence are pending.
Live listener is a Python UDP receive loop writing `/tmp/umi-0186-live.log`; unlike the earlier
nc listener it remains unconnected so a new phone source port after reboot is accepted.
The user must run tools/umi-usbnet.sh with sudo after USB re-enumeration.

Session scratchpad: `$HOME/ios-sweet-port/umi-gpu-session.md` (recreated because the old
one was not found). Retrieved 5120 logs under `/tmp/umi-0185-bpr5120-*`; journals accumulate
across boots, so their totals cannot be attributed to this boot alone.

## How to work

- Kernel tree: `$HOME/ios-sweet-port/xnu-work/bt/xnu` (git, one commit per patch).
  Compile check: `python3 $HOME/ios-sweet-port/xnu-work/xnu-cc-sys.py
  $HOME/ios-sweet-port/xnu-work/run-0152.log $HOME/ios-sweet-port/xnu-work/bt bsd/dev/sweet_adreno.c`
  (works for `iokit/...cpp` files too).
- Build locally: `bash tools/build-kernel-local.sh` (4-12 min incremental; trailing dSYM/python
  steps fail harmlessly - the kernel links). Kernel lands in
  `xnu-work/bt/build/xnu.obj/DEVELOPMENT_ARM64_SWEET/kernel.development.sweet`.
- Patch: `git -C .../bt/xnu format-patch -1 --stdout > xnu/patches/01NN-....patch` in
  `$HOME/ios-sweet-port/ios-sweet`, commit, push `umi-scanout`, `gh workflow run xnu.yml --ref umi-scanout`,
  download with `gh run download RUN -R qcom-toolbox/ios-sweet -n xnu-kernel -D xnu/out-01NN`.
  CI sometimes fails with "job was not acquired by Runner" (no macos-14 runner): start a new run.
- Boot image (no ARM cross compiler on this Mac): `bash tools/umi-boot-image.sh KERNEL OUT.img
  ufslogsecs=2 sweetusb=2 sweetwlan=8 sweetwlandelay=90 sweetwlanssid=<AP> sweetbattery=2
  sweetgpu=23 sweetmtl=2` - it fails at the shim's gcc but has already written
  `shim/out/payload-umi.bin`; then swap the payload into an existing metal image's ramdisk
  (boot image v2, sequential 4096-byte pages: kernel at page 1, ramdisk right after it,
  ramdisk_size at header offset 16; dtb and everything after the ramdisk's page count are kept -
  if the ramdisk grows, shift the DTB and tail by the page-count difference). Verify with `tools/unpack_bootv2.py` (compare the
  kernel/dtb with the base image, grep the cmdline out of the ramdisk).
- Phone: select the umi serial from `tools/umi-log-pull.sh` (two phones attached). Only `fastboot boot` (RAM). Never flash or
  wipe; the user flashes `boot` themselves when asked. Logs: from TWRP with `tools/umi-log-pull.sh NAME`;
  live over UDP: `nc -ulk 5140` on the Mac while iOS runs (IOLog only - printf stays in the video
  console / persistent ring; the relay only sees what happens after `tools/umi-usbnet.sh` brings
  the network up, so early-boot lines are missing from it). On-phone files:
  `tools/umi-files.py get/put` (`/var/local/mtl2.log`, `/var/local/turnip-<proc>.log`).
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` (or your own
  attribution line). GPU firmware, Apple files, Wi-Fi network names and device serials stay out of
  git.
- References used: Linux v6.12 `drivers/gpu/drm/msm` (a6xx_gpu.c, a6xx_catalog.c, a6xx.xml,
  adreno_pm4.xml), Mesa 24.2 (`src/freedreno/common/freedreno_devices.py`,
  `src/gallium/drivers/freedreno/a6xx/fd6_blitter.cc`, `fd6_screen.cc`, `fd6_emit.h`).
