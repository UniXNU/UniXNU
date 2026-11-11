Continue the Adreno 650 GPU bring-up for the Xiaomi Mi 10 (umi) iOS port.

Read these first, in this order:
1. $HOME/ios-sweet-port/ios-sweet/AGENTS.md
2. $HOME/ios-sweet-port/ios-sweet/docs/GPU-HANDOFF.md (state, lessons, open problem, plan, how to build and boot)
3. The umi section at the top of $HOME/ios-sweet-port/ios-sweet/NOTES.md (entries 0160-0169 have every value used)

Where things stand: `bsd/dev/sweet_adreno.c` (kernel patches 0160-0169) brings the GPU up step by step with
boot-arg `sweetgpu=N`. Steps 1-22 have worked on the phone (0168: the GPU's 2D engine drew red/green/blue bands
into the panel framebuffer, pixels read back exact). Step 23 (0169: GPU memory objects above 4 GB,
CP_INDIRECT_BUFFER submission, CACHE_FLUSH_TS fence, self-test drawing magenta/yellow/cyan) has never run: in
the 0169 boot step 22's check failed first because the CPU wrote an opaque black pixel (0xff000000) over the
GPU's green band. Most likely writers: the kernel text console (draws into the same framebuffer until iOS's
first frame) or a frame copy in AppleCLCD::present() racing the hold. Log `research/logs/umi-0169-gpu23.txt`.

Your task:
1. Patch 0170 in `iokit/Kernel/arm/SweetFramebuffer.cpp`, as GPU-HANDOFF.md "Fix to do first" describes:
   `sweet_fb_gpu_begin()` sets the hold and cleans the framebuffer from the CPU cache inside the framebuffer
   workloop's gate (`fWorkLoop->runAction`), mutes the console for the hold (`sweet_console_muted`, restored
   when the hold ends in `vsyncFired`), and the power-off fade is skipped while held. Optionally add a
   `mach_absolute_time()` stamp to the GPU and FB log lines so their order can be read (printf and IOLog
   lines do not interleave reliably in the persistent log).
2. Compile-check locally with xnu-cc-sys.py (both changed files), commit in
   $HOME/ios-sweet-port/xnu-work/bt/xnu, export the patch into ios-sweet/xnu/patches/, commit and push
   `umi-scanout`, run the xnu.yml CI build and download the kernel. If CI says "job was not acquired by
   Runner", start a new run.
3. Build a RAM-boot image with `sweetgpu=23` (recipe in GPU-HANDOFF.md "How to work").
4. Boot it with `fastboot boot` (the phone is usually in TWRP: `adb reboot bootloader` first). Tell the user
   what the panel should show (red/green/blue bands, a few seconds later magenta/yellow/cyan, each ~10 s),
   ask them to watch and then put the phone back into TWRP, pull the log with `tools/umi-log-pull.sh NAME`
   and report the SWEET GPU lines of steps 22 and 23 (fence value, data-object words, pixel readbacks).
   Trust the log over what anyone remembers seeing.
5. Record the result in NOTES.md (umi section, newest entry under 0169) and update GPU-HANDOFF.md.
6. If step 23 passes, continue with the plan in GPU-HANDOFF.md: an IOUserClient that mirrors Linux's msm
   DRM uAPI (GET_PARAM, GEM_NEW / GEM_INFO / GEM_CLOSE, GEM_SUBMIT, WAIT_FENCE) for Mesa freedreno. Set up
   the A650 CP protect table (Linux a6xx_catalog.c `a650_protect`) before any user-space client can submit.
   Ask the user how test binaries should reach the phone's HFS root before building the user-space side.

Rules:
- Phone: use the adb serial in tools/umi-log-pull.sh (two phones are attached). Only `fastboot boot` (RAM);
  never flash or wipe anything; the user flashes `boot` themselves when asked.
- Take every A650 value from Linux v6.12 (drivers/gpu/drm/msm) or Mesa 24.2 (src/freedreno), never from
  another Adreno; say which file each value comes from.
- One kernel commit per patch; commit messages end with
  "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" (or your own attribution line).
- Keep GPU firmware, Apple files, Wi-Fi network names and device serials out of git.
