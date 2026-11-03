# iOS 16 on sweet (Redmi Note 10 Pro, SM7150) - working notes

## umi (Xiaomi Mi 10, SM8250) port - branch `umi` on qcom-toolbox/ios-sweet (2026-10-20)

- **🎉 2026-11-01 0230: SILEO ON THE HOME SCREEN AND IT OPENS (user: "Opens")** - stage 1 of the Sileo plan, no
  kernel change (boot `shim/out/umi-0230-sileo-lsreset.img` = the 0227 kernel, 0229b's line without
  `sweetadspprobe=0 sweetamp* sweetadsptone=1`, + `sweetlsreset=1`; booted twice, since the first boot's reset ran
  before the app was on the phone).
  - Survey: no bootstrap at all on the phone (no /var/jb, /etc/apt, /var/lib/dpkg, no shell: /bin = df, ps). What
    makes third-party code run: the SWEET AMFI policy (0035/0036) makes every signed binary on the root mount a
    platform binary with its own signature's entitlements, so a jailbreak app's ad-hoc signature is used as is
    (no re-signing); /Applications bundles are picked up when LaunchServices rebuilds (`sweetlsreset=1`).
  - Sileo 2.5.1 rootful deb (`org.coolstar.sileo_2.5.1_iphoneos-arm.deb`, GitHub Sileo/Sileo releases, SHA-256
    85f4d93c...) unpacked on the Mac -> /Applications/Sileo.app (279 files, 7.6 MB, giveMeRoot 4755). Its only
    non-iOS libraries: `@rpath/libzstd.1.dylib` and `@rpath/liblzma.5.dylib` (rpaths /usr/lib/swift,
    /opt/procursus/lib, /var/jb/...; liblzma is in the 20H392 shared cache as /usr/lib/liblzma.5.dylib, found
    through dyld's /usr/lib fallback). Added from Procursus rootful (`dists/iphoneos-arm64/1800`, arch
    iphoneos-arm; SHA-256 checked against its index): /usr/lib/libzstd.1.5.5.dylib + libzstd.1.dylib link
    (libzstd1 1.5.5), /usr/lib/libiosexec.1.dylib (libiosexec1 1.3.1, libzstd links it). All new paths, nothing
    replaced. Pushed with `tools/umi-push-tree.sh` (mkdir / rm + put / link, every file read back and compared).
  - Result: IconState.plist lists `org.coolstar.SileoStore`; log `exec Sileo`, IOSurfaces, AKS calls, no crash.
  - **2026-11-02: Procursus repo added, Sileo lists its packages (user: "Packages shown")** (normal boot
    `shim/out/umi-0230-normal.img` = 0230's line without `sweetlsreset=1`). New on the phone (file server, root):
    /private/etc/apt/sources.list.d/sileo.sources (deb822: `URIs: https://apt.procurs.us/`, `Suites:
    iphoneos-arm64/1800`, `Components: main`, the rootful iphoneos-arm repo), /private/var/lib/apt (755) with
    lists, lists/partial and sileolists at 777 (Sileo runs as mobile; tighten once dpkg/apt own them). After the
    refresh both list dirs were still empty, so Sileo kept the index somewhere else (not in Caches either). Installing
    still needs stage 2 (apt-get, dpkg-deb, a shell for giveMeRoot).
  - **🎉 2026-11-02: PROCURSUS BOOTSTRAP IN, SILEO INSTALLS PACKAGES (user: nano "Installed")** (boot
    `shim/out/umi-0230-normal.img`).
    - Bootstrap: Procursus rootful `bootstraps/iphoneos-arm64/1700/bootstrap-iphoneos-arm.tar.zst` (20.6 MB,
      SHA-256 8913a49e..., GPG signature checked against Procursus' key C59F3798...1B0E from ProcursusTeam/Procursus
      `build_misc/keyrings/procursus/memo.gpg`; there is no rootful 1800 bootstrap, palera1n rootful also starts
      from 1700). 4000 entries (3602 files, 397 dirs, 149 links, 105 MB), dpkg database in /Library/dpkg
      (/var/lib/dpkg -> /Library/dpkg). Only 5 paths already existed: Apple's /usr/bin/ltop and
      /usr/libexec/dirs_cleaner were KEPT (bootstrap copies skipped), libiosexec / libzstd (ours from 0230) replaced.
      Modes from the tarball, not from macOS tar (non-root extraction drops setuid / sticky: sudo, su, login,
      passwd, chpass, newgrp, quota, shshd 4755; /var/lib/ex 1777). Pushed in ~13 min by a one-process pusher
      (RM, PUT with mode, CHMOD, GET + compare, resumable log; now `tools/umi-push-staged.py`), 0 failures. The whole tree (bootstrap + Sileo + libkrw0-tfp0 + dpkg
      entries, final state) is rebuilt by `tools/umi-jailbreak-stage.sh OUT` (pinned SHA-256s; dry run matched the
      pushed status byte for byte and every bootstrap file / link).
    - Not copied: prep_bootstrap.sh (no way to run a shell from outside). Its useful parts done on the Mac instead:
      dpkg status entries that /usr/libexec/firmware writes (firmware 16.7.16, cy+os.ios 16.7.16, cy+cpu.arm64,
      cy+model.iphone 10.3, cy+kernel.darwin 22.6.0, cy+lib.corefoundation 1971.0, info/firmware.ver) and an
      org.coolstar.sileo entry (+ .list / postinst / prerm). Skipped: pwd_mkdb, chsh, terminal password (iOS's
      default master.passwd stays), /etc/shells.
    - Sources: the bootstrap's procursus.sources set to `Suites: iphoneos-arm64/1800`; the 0230 sileo.sources
      removed (same repo twice).
    - **apt refused everything until libkrw0 had a plugin:** the bootstrap's status has libkrw0 (Depends
      libkrw0-plugin), normally supplied by the jailbreak tool. Added Procursus' libkrw0-tfp0 1.1.1-2
      (/usr/lib/libkrw/libkrw-tfp0.dylib + status / .list / .md5sums; old status kept as
      /Library/dpkg/status.sweet-orig). Sileo's flow for reference: it fetches indexes into /var/lib/apt/lists,
      writes the queued packages' entries to /var/lib/apt/sileolists, downloads the debs, then giveMeRoot runs
      `apt-get install --no-download -f -oDir::State::lists=sileolists/` (so one broken installed package
      blocks every install).
    - Result: giveMeRoot's setuid works on this kernel; log shows exec apt-get / dpkg / dpkg-deb, /usr/bin/nano
      present, nano 7.2 + libmagic1 5.45 installed in dpkg status.
    - Leftovers: /var/lib/apt/lists and lists/partial are still 777 from 0230 (dpkg/apt are root now; can go back
      to 755). **Wi-Fi bug seen while testing (user): once Wi-Fi drops it never reconnects until a reboot.**
  - **Stages 2-4 done 2026-11-02 (entry above).** Original plan: (2) Procursus rootful bootstrap (thousands of files: a bulk TAR verb in the file server or
    tools/umi-push-tree.sh from an unpacked tarball; check clashes with Apple's /bin/ps, /bin/df, /usr/bin/* first,
    `*.sweet-orig` backups), (3) dpkg status entries for the libs + Sileo, /etc/apt/sources.list.d, check giveMeRoot
    gets root (setuid on HFS+), (4) refresh sources over Wi-Fi and install a test package from Sileo.
- **2026-11-03 0232: idle pause + 160 ms cushion: ringtones clean, no pops (user)** (patch
  `xnu/patches/0232-umi-audio-idle-pause.patch`, boot `shim/out/umi-0233b-audio.img` = 0231c's line).
  - ASM_SESSION_CMD_PAUSE after 1 s with nothing queued or in flight, RUN_V2 again when frames arrive (writes wait for
    its answer; 2 s timeout treats it as running): "paused (idle) -> 0" / "running again -> 0" for every tone, no
    ADSP crash in two boots (0233, 0233b).
  - 0233 (prefill 3 periods): plays, but "some little popping" during tones: the ADSP held only 2-3 periods (40-60
    ms). 0233b (prefill 8, 160 ms): 5-7 periods at the ADSP while playing, **no pops**.
- **2026-11-03 0231: ringtones play fully; one ADSP crash seen, not reproduced** (patch
  `xnu/patches/0231-umi-adsp-f3-dedup.patch`, boot `shim/out/umi-0232-audio.img` = 0231c's line).
  - Boot 0231c (2026-11-03 19:36), after ~15 min of tests: the ADSP died right after a ~1 s sound ("Opening" tapped
    in the Ringtone list): `crash reason (item 423): "SFR Init: wdog or kernel error suspected."`; afterwards the node
    accepts nothing (plug-in ring full, no write-dones) -> silence until a reboot. Its F3 messages were lost: the old
    3000-line budget had been used up by one QShrink message (L712 797f3f52) repeating every ~5 ms while idle.
  - 0231: each F3 hash prints 20 times, then every 1000th with its count. Boot 0232: "Opening" x several + "Seaside":
    **sound good (user), no crash**, tones ~7 s each (335872 frames). The volume buttons / slider showing the ringer
    HUD while a tone plays in Sounds & Haptics is normal iOS (they set the ringer volume there).
  - Open: why the ADSP crashed (watch for `crash reason` with the F3 lines before it); no ADSP restart after a crash
    yet (audio is gone until a reboot); idle stream = the ASM session keeps running on underruns (Linux pauses it).
- **2026-11-02 0230: no more glitches; iOS stops each sound after ~2 s (open)** (patch
  `xnu/patches/0230-umi-sweet-audio-queue.patch`, boot `shim/out/umi-0231c-audio.img`, plug-in from `phone/sweet-audio/`
  installed).
  - Kernel: 480 ms queue, max 8 ASM buffers in flight (24 -> ASM write result 0x12 ENEEDMORE and a jammed queue: the
    0231 "stops randomly"), prefill 3 periods, pad only after 200 ms idle, 1 s stats. User on 0231b: "no glitches".
  - Plug-in: 64 Ki-frame ring (the server hands over 16 Ki frames per cycle at first), a persistent writer that plays
    out the ring after StopIO, zero time stamps from elapsed time, DeviceIsRunning notifications, per-session stats.
  - **Resolved by the unified log: the ~2 s stops were Settings' ringer-volume slider previews.** Every session in the
    0231c boot is `Preferences(408)` in category `RingtonePreview`: SHSRingerControl setVolume steps every ~16 ms
    (a finger on the slider), SpringBoard `activateRingerHUD: tone` (the pop-up the user saw; it comes with each ringer
    volume change, not a fault), mediaserverd plays SSID 1107 `RingerSwitchIndication`, and ~2.5 s later Settings' own
    AVPlayer sets rate 0 -> "AudioToolboxServerHandleInterruption Stop Now". iOS previews that slider briefly by design.
    The route is right: VirtualAudio builds `d22_speaker_ringtone` over our Speaker (spp3 speaker protection runs
    open-loop: "Closed loop checks failed ... SpClProps.size=0"), software volume, 48 kHz, 1024-frame buffers.
    Next test: something that plays for long (a song, a video in Safari, a tapped ringtone in the Ringtone list).
  - **2026-11-03 (boot 0231c again): a ringtone tapped in Settings > Sounds & Haptics > Ringtone plays its full
    length (user: "Seaside plays fully for sure", "Opening" unsure).** Lead for "Opening": newer tones carry a haptic
    track (the log shows `Track ID 2 hapt` for a ringtone asset), which iOS plays on the "Actuator" device; ours
    accepts and discards it (no StartIO / I/O seen on dev 7 yet). Check the log of an "Opening" play for Actuator
    StartIO and errors. The "1 s and a glitch" report of that boot was again the ringer slider (SHSRingerControl steps,
    activateRingerHUD, Settings' own timeControlStatus=0 ~2 s after the finger lifts). No Music or Safari audio session
    appears in the unified log at all (clients: SpringBoard MediaPlayback, Preferences RingtonePreview): media apps
    never reached the audio system; video also needs the missing hardware decoder (VideoToolbox / AVD).
  - (Earlier reading: every sound gets StopIO from the server after ~1.5-3 s.) Our side is healthy: ~48
    kframes/s pushed and played, 0 left in the ring, zero time stamp calls every 21 ms (max gap 21 ms), 1024-frame I/O.
    The user also sees a "Do Not Disturb off" notice each time a sound starts. Suspects: speaker protection (the
    VirtualAudio binary has graph_configurations.plist and nospp_graph_configurations.plist; on iPhones the Speaker
    device's input carries the amp's I/V sense, ours is silence), or an interruption from elsewhere.
  - **Reading iOS's unified log on the Mac:** pull `/private/var/db/diagnostics` (version.plist, timesync/, the newest
    Persist / Special / HighVolume tracev3) and all of `/private/var/db/uuidtext` read-only with tools/umi-files.py into
    a `NAME.logarchive` folder (`research/logs/umi-unified-0231c.logarchive`, 404 MB, git-ignored), then write an
    `Info.plist` with OSArchiveVersion 4 and Persist/Special/HighVolume/Live/TTL `OldestTimeRef` + `EndTimeRef`
    ({ContinuousTime, UUID = boot UUID, WallTime ns}) taken from each tracev3 header (chunk 0x1000: continuous time at
    +24, wall seconds at +32; sub-chunk 0x6102 = boot UUID). Without those time refs `/usr/bin/log show --archive`
    prints nothing. With them: `log show --archive A --style compact --info --debug` = 1.5 M lines.
- **🎉 2026-11-02 0229: iOS PLAYS ITS OWN SOUNDS FROM THE SPEAKER (user heard ringtones; "a bit glitchy")** (patch
  `xnu/patches/0229-umi-sweet-audio-node.patch`, HAL plug-in `phone/sweet-audio/`, boot `shim/out/umi-0230c-audio.img` =
  0228's line with `sweetadsptone` replaced by `sweetaudio=1`: `... sweetadsp=1 sweetadspdelay=200 sweetadsprpc=0
  sweetadspprobe=0 sweetamp=1 sweetampstepms=200 sweetaudio=1`).
  - Kernel `/dev/sweet-audio` (0666, made when the stream runs ~200 s after boot): write() S16LE stereo 48 kHz into
    20 ms periods of the 0xd3800000 buffer, max 8 periods (160 ms) ahead, never blocks (EAGAIN / ENXIO); the GLINK
    loop sends ASM writes and frees on WRITE_DONE; ioctls 'A' 1 gain Q16, 2 stats, 3 log line. Both amps stay on.
  - `SweetAudio.driver` (our own AudioServerPlugIn, SDK header, ad-hoc ldid; `phone/sweet-audio/build.sh [install]`)
    in `/System/Library/Audio/Plug-Ins/HAL/`: **the four iPhone devices VirtualAudio knows by UID must all exist**
    or it never routes (one "Speaker" alone: enumerated, no client, no StartIO): "Speaker" 2 ch out (-> node) + 2 ch
    silent in + volume (-48..0 dB), "Hawking" 1 ch in, "Actuator" 1 ch out (dropped), "Codec" 1 ch in + data source
    'imic'; all 16-bit signed 48 kHz, zero time stamp period 16384, clock mach_absolute_time. I/O thread -> lock-free
    ring -> writer thread every 5 ms. Its bring-up trace goes to the kernel log as `SWEET AUDIO HAL:` (property
    queries once each, clients, StartIO/StopIO): mediaserverd (user mobile) cannot write /private/var/sweet.
  - **Phone state changed (user-approved):** SweetAudio.driver installed; **Apple's VirtualAudio.plugin copied back**
    from `/Library/Audio/Plug-Ins/HAL.disabled/` to `/Library/Audio/Plug-Ins/HAL/` (the HAL.disabled copy stays as the
    backup); with our devices present mediaserverd no longer crash-loops (one start, pid 28).
  - Seen: at load VirtualAudio adds clients to Speaker / Codec / Hawking, sets 'sact' on the streams, volume 100 %,
    one StartIO/StopIO; each ringtone tap = client add, StartIO, writes ("first write, 65536 bytes", "playing"), StopIO.
  - Next: glitches: the node pads a half period after only 40 ms without data and keeps only 160 ms queued (raise both),
    CPU load; then the ADSP start time (200 s), the receiver/earpiece amp as the second channel, microphones.
- **🎉 2026-11-02 0228: THE SPEAKER PLAYS FROM iOS (user heard the 1 kHz test tone)** (patch
  `xnu/patches/0228-umi-speaker-sd1-tone-heard.patch`, boot `shim/out/umi-0229d-sd1.img` = 0215d's line without
  `sweetsample` + `sweetadsprpc=0 sweetadspprobe=0 sweetamp=1 sweetampstepms=200 sweetampplay=1 sweetadsptone=1
  sweetadspsd=2`).
  - **The CS35L41s take their data on tertiary MI2S SD1 = gpio 137 (function 3, mi2s2_data1)**, not SD0 / gpio 134 as
    the base kona DT says (`qcom,msm-mi2s-rx-lines = <1>`): the umi dtbo overlay must change it (not pulled). AFE I2S
    config channel_mode 2 (AFE_PORT_I2S_SD1). SD1 is the kernel default now (`sweetadspsd=1` = SD0). TLMM read-back
    133/134/135 0xc4, 137 0xcc.
  - How it was found: with SD0 the ADSP rendered the whole tone (its F3 log counts 100 frames of 10 ms, write-dones
    0.8 s apart), the amps were powered, PLL-locked, DAC source ASPRX1, 0 dB: so the samples left on a pin the amps
    do not listen to.
  - Also learnt: the ADSP refuses ASM_CMD_SHARED_MEM_MAP_REGIONS with sid bits 3 (FastRPC's stream, status 1): ASM
    buffers must come through 0x1801 (bits 1). **Boot-args are cut at 607 characters** (shim BOOT_LINE_LENGTH 608): a
    boot lost `sweetadsptonepool=1` that way; `tools/umi-boot-image.sh` now refuses longer lines.
  - The tone stays opt-in (`sweetadsptone=1`), as do `sweetamp` / `sweetampplay`. Next: a `/dev` audio node that feeds
    this ASM stream, then an AudioServerPlugIn (our own code; design as HackiOS, MIT) so iOS's own sounds play.
- **2026-11-01 0227: test tone through the ADSP, not heard yet; paused** (patch `xnu/patches/0227-umi-adsp-test-tone.patch`,
  boots `shim/out/umi-0229-tone.img`, `umi-0229b-tone1k.img` = 0228b's line with `sweetadspprobe=0 sweetadsptone=1`).
  **The tone is opt-in (`sweetadsptone=1`, default off), as are `sweetamp` / `sweetampplay`: normal boots play nothing.**
  - PCM in low RAM 0xd3800000 (256 KiB), read by the ADSP through APPS SMMU stream 0x1801 (kona msm_audio_ion, routed to
    bypass, sid bits 1 in address bits 32+). ASM map (handle back), open write v3 session 1 (PP none, PCM v2), media
    format, ADM open v5 on 0x1004 (NULL topology, copp 0), matrix route, run, 4 writes: **every step 0, all writes
    done**; the ADSP F3 log shows both PP stages "Received first data buffer" and the AFE connecting the stream.
  - Not heard: 480 Hz / amplitude 1000 / 0.6 s, then 1 kHz / 4000 / 1 s (Linux lab tone: 1 kHz / 6000). Amp 0x40 at play:
    DAC source 0x4c00 = 0x8 (ASPRX1), volume 0x6000 = 0x8000 (0 dB), gain 0x6c04 = 0x273, PLL locked, powered up.
  - Next suspect: the amps' I2S data line. We configure SD0 (gpio 134); the stock DT's `qcom,msm-mi2s-rx-lines` for
    tertiary MI2S is in `shim/out/umi-stockkernel-twrp.img` (string at offset ~40 MB, not yet decoded).
  - iOS's own sounds (ringtones) need an audio device for CoreAudio on top of this kernel path: not started.
- **🎉 2026-11-01 0226: AFE ANSWERS, TERT_MI2S_RX RUNNING FROM iOS, BOTH AMPS PLL-LOCKED** (patch
  `xnu/patches/0226-umi-apr-seqcmd-afe-running.patch`, boot `shim/out/umi-0228b-clkv1-amp.img` = 0215d's line +
  `sweetadsprpc=0 sweetadspprobeevery=10 sweetadspproberounds=3 sweetamp=1 sweetampstepms=200 sweetampplay=1`).
  - **Root cause of the silent ASM / ADM / AFE (0215-0225): our APR header field was 0x150 = message type 1
    (APR_MSG_TYPE_CMD_RSP).** The ADSP executed the commands but, taking them for responses, sent no
    APR_BASIC_RSP_RESULT; only replies with their own opcode (core state, versions, LPASS hw votes) came back. Linux
    sends 0x250 (APR_MSG_TYPE_SEQ_CMD). Found through the ADSP's own F3 log: `AFEPortAprHandler.cpp:300 "Executing
    APR cmd with opcode"` for each of our commands, with the I2S config parsed, while nothing came back on GLINK.
  - Then: port stop 0, I2S config 0, **clock set via AFE_SVC_CMD_SET_PARAM 0x100f3 (param header v1) 0** (the V2 form
    0x100fc with a v3 header returns 0x2 EBADPARAM: this AFE has no instance-id support, Linux picks v1 then), port
    start 0x100e5 0 -> RUNNING (zeros: no stream yet). ASM / ADM / AFE unmap with handle 0 -> 0x2 (expected), core
    CREATE_LPASS_NPA_CLIENT -> 0x11.
  - **Amps: IRQ1 status 0x1401000 / 0 / 0x2000002f / 0x3 on both: power-up done (STATUS1 bit 24) and PLL lock (STATUS3
    bit 1)**, vs 0x401000 / 0x20000080 without a clock (0223). The bit clock reaches the CS35L41s; no sound yet.
  - Diag (boots 0227 / 0227b): time sync + one F3 mask per msm SSID range (diagchar.h MSG_SSID_0..26) + DIAGMODE v2 per
    diag id make the ADSP stream F3. Most messages are QShrink4 terse (0x92: line, SSID, ss mask, 32-bit hash,
    args); the hash database is not on the phone, plain-text ones still decode. Firmware rebuilt as an ELF from
    adsp.mdt + .bNN disassembles with Homebrew LLVM's Hexagon objdump (audio PD code = segment 11 at 0xb0200000).
  - Next for a test tone: an ASM stream into TERT_MI2S_RX (shared memory map, ASM open write, ADM COPP + matrix
    routing, as the Linux card), or an AFE-level source (RT proxy port / loopback) if simpler.
- **2026-11-01 0225: UAUDIO announced and every ADSP GLINK channel opened; still no ASM / ADM / AFE answer** (patch
  `xnu/patches/0225-umi-adsp-uaudio-glink-all.patch`, boots `shim/out/umi-0225-uaudio.img` and `umi-0226-openall.img` =
  0215d's line + `sweetadsprpc=0 sweetadspprobeevery=10 sweetadspproberounds=8`).
  - QMI 0x41d (UAUDIO_STREAM_SERVICE) announced to node 5 (boot-arg `sweetadspuaudio`): no QRTR traffic to it, no change.
  - The ADSP opens 6 channels itself (pcie_drv, mhi_sat, fastrpcglink-apps-dsp, IPCRTR, LOOPBACK_CTL_LPASS,
    apr_audio_svc); we accept all and open glink_ssr after VERSION_ACK (`sweetadspopenall`): **all 7 open both ways, no
    data on the extras**. Core / versions / LPASS hw votes still answer; AFE port stop, I2S config, the ASM / ADM / AFE
    UNMAP probes get nothing over 8 rounds. Ruled out: missing GLINK channels, glink_ssr handshake, UAUDIO.
  - Diag note: the ADSP sends CNTL msg 1 (registration tables, SSID ranges 0x12/0x0c/0x5a ...) after the F3 mask: the
    per-range masks Linux answers with are the next diag lead.
  - Live log tip: an unplugged / unenumerated USB cable gives an empty log on a working boot (no en8); replug and run
    `tools/umi-usbnet.sh` right after `fastboot boot`.
- **2026-11-01 0224: ADSP diag real-time mode; still no F3 stream** (patch `xnu/patches/0224-umi-adsp-diag-realtime.patch`,
  boot `shim/out/umi-0224-f3rt.img`). DIAGMODE v1 {3, 36, version 1, sleep vote 1, real time 1} after the F3 mask: taken,
  no data on LPASS:DATA. Linux sends DIAGMODE **v2** (with the diag id) when diag ids are in use, plus time sync, log and
  event masks per range; not tried.
  - The ADSP firmware's own strings (`strings adsp.b*`, 40k lines) are plain text, e.g. `AFEPortAprHandler.cpp:====PFT:
    AFESvc: Executing APR cmd with opcode: %8lx`, so F3 would be readable once it streams. Also present:
    `servreg_qmi_notifier_client.c: Wait for QMI server at instance ID %d` (the ADSP waits for remote servreg notifier
    servers), `servreg_notif_worker_task(): received ack from root`, `PDR DISABLED` / `Proceeding with PDR`,
    `fastrpc_uprocess.c ... audioPDR`. Worth following: which instance the ADSP waits for, and whether its audio PD
    gates its services on it.
- **2026-11-01 0223: BOTH CS35L41 AMPS CONFIGURED FROM iOS (Linux driver's writes replayed); they wait for a bit
  clock** (patch `xnu/patches/0223-umi-cs35l41-configure.patch`, boot `shim/out/umi-0223-ampinit.img` = 0222-amp's line
  + `sweetampstepms=200 sweetampplay=1`).
  - Source: Linux lab regmap traces (`research/audio-umi/twrp/regmap-probe.txt`: driver unbind/bind = the I2C probe;
    `regmap-full.txt`: tracing on before the card first comes up = the ASoC component probe, then one tone). Tables in
    `bsd/dev/sweet_cs35l41_umi.h` (generated, per chip: the OTP trims differ): init = probe + component writes
    (amp 0x40: 107, 0x42: 109), start = stream writes up to the global enable 0x2014 = 1, stop = the rest.
  - Component probe writes: 0x3808 = 0x40 (boost peak current), 0x4220 = 3, 0x480c = 1, 0x2018 0x3321 -> 0x3320, IRQ
    poll of 0x10010, 0x10010 = 0x800000, test key + 0x2084 = 0x2f1aa3, 0x2018 = 0x20, 0x201c = 0x1001000. Stream start:
    0x2c04 0x810 -> ... -> 0x10370 (PLL from SCLK), 0x4808 = 0x10200200, 0x4840 = 0x10, (0x40 only: 0x4820 0x101 -> 1),
    0x201c = 0x1001010, 0x4800 = 0x10000, 0x2018 = 0x21, test key + 0x2084 = 0x2f1aa0, 0x2014 = 1.
  - Phone: **all init writes OK, read-backs equal the Linux values** (0x3808 0x40, 0x4220 3, 0x480c 1, 0x2018 0x20,
    0x201c 0x1001000, 0x4c50-0x4c5c 0x28 / 0x21 / 0x3a / 0x3b, 0x6404 0x200530e) on both amps. Stream start OK, after 1 s
    IRQ1 status 0x401000 / 0 / 0x20000080 / 0x3: **PLL lock (STATUS3 bit 1) clear, no power-up done (STATUS1 bit 24)**
    -> the amps are ready but have no I2S bit clock: the remaining blocker is the ADSP's AFE (TERT_MI2S_RX) not
    answering our kernel.
- **🎉 2026-11-01: BOTH CS35L41 AMPS ANSWER FROM iOS** (boot `shim/out/umi-0222-amp.img` = 0215d's line + `sweetadsprpc=0
  sweetadspafe=0 sweetadspprobe=0 sweetamp=1`; kernel = patch 0222, the probe code is from 0216). Read-only: nothing
  configured or enabled, no sound.
  - Steps (1 s apart, all logged): reset gpio 114 cfg 0x1 io 0 (input, pull-down, low = amps in reset); GCC vote
    0x52008 0x0e3c007f -> 0x0e3c23ff (wrap0 m/s-ahb, core, core2x, s3), branches on, s3 RCG DFS (0x21) level 0 = XO/1;
    **QUP0 SE3 fw 0x303 (proto 3 = I2C), FIFO interface on (if-disable 0)**, tx 0x20102864 / rx 0x20104800 (32-bit,
    16-word FIFOs) -> FIFO-mode GENI I2C works, no GPI DMA; pins 119/120 qup3; reset low 3 ms, high 3 ms.
  - **0x40 speaker and 0x42 earpiece: IRQ1_STATUS4 0x3 (OTP boot done), DEVID 0x35a40, REVID 0xb2** = CS35L41 rev B2, as
    Linux reports. So the 0216c freeze was the I/O-map panic (fixed in 0217), not the probe.
  - Next for the amps: their static configuration as the Linux driver does at probe (boost 4000 mA / 1000 nH / 15 uF,
    ASP format, PCM source ASP) plus the per-stream sequence from the Linux lab trace. They still need SCLK from the
    AFE port to play, which the ADSP does not give us yet.
- **2026-11-01 0221: DIAG HANDSHAKE WITH THE ADSP WORKS; AUDIO SERVICES STILL SILENT** (patch
  `xnu/patches/0221-umi-adsp-diag-servers.patch`; boots `shim/out/umi-0221-diag.img`, `umi-0221b-diag-norpc.img`).
  - Linux lab `qrtr-lookup` (`research/audio-umi/twrp/qrtr-lookup-linux.txt`): APPS (node 1) serves DIAG 4097 for every
    peripheral (LPASS:CNTL 64, LPASS:DATA 66, LPASS:DCI 68 ...) and the ADSP (node 5) then publishes **4097/65
    LPASS:CMD**, which it never did for our kernel. Instances = base (LPASS 64) + type (CNTL 0, CMD 1, DATA 2, DCI 4).
  - Ours now: NEW_SERVER 4097/64 + 4097/66 on the ADSP's HELLO; control packets {u32 id, u32 len, data}: the ADSP sends
    feature mask (msg 8) -> we answer {8, 8, 4, bits FEATURE_MASK_SUPPORT + DIAGID_SUPPORT}; msg 12; **diag ID requests
    (msg 33, v1) for "msm/adsp/root_pd" and "msm/adsp/audio_pd"** -> {33, len, version 1, id, name}; then dozens of msg 1
    (command registrations), and 4097/65 appears. Diag works.
  - **ASM / ADM / AFE still never answer** (probes and AFE steps), with the audio PD FastRPC (0221) and without it
    (`sweetadsprpc=0`, 0221b). Votes still answered.
  - The downstream service-notifier registers exactly as we do (REGISTER_LISTENER, state from the reply), so servreg is
    not the difference either. Ruled out so far: timing, FastRPC, diag, servreg, packet size, root vs audio PD.
  - Linux's real APR bytes are out of reach in the lab: no /dev/mem, no /proc/kcore, no kprobes, no debugfs (only
    tracefs: regmap / i2c events, no glink/apr events). `tools/smem-apr-decode.py` is ready for an SMEM dump if one
    turns up.
  - 0222 (`xnu/patches/0222-umi-adsp-diag-f3.patch`, boot `shim/out/umi-0221c-f3.img`): after the diag IDs an F3 mask
    {11, 15, stream 1, status 2 ALL_ENABLED, mode 0, ssid 0-0xffff, size 1, 0x1f} goes to the ADSP and LPASS:DATA is
    HDLC-decoded; the mask is taken but **no F3 data arrives** in 4 minutes. Linux's diag also sends DIAGMODE (3, real
    time) / DTR (2) and per-SSID-range masks; probably needed before the ADSP streams.
  - Still open: why ASM / ADM / AFE ignore our commands while they answer Linux. Independent and now unblocked: the
    CS35L41 bring-up on iOS (I/O-map panic fixed; Linux's register sequence above).
- **🎉 2026-11-01: THE SPEAKER PLAYS UNDER LINUX ON THIS PHONE (user heard a 5 s 1 kHz tone)** - a reference lab for
  the iOS port, all from RAM, nothing written to the phone (read-only mounts, binaries in TWRP's RAM /tmp).
  - Image `shim/out/umi-stockkernel-twrp.img` (not in git): the kernel + dtb of the phone's own boot image backup
    (`~/ios-umi-backup/boot-read-2026-10-21.img`, a custom ROM's 4.19.325, audio techpack built in) + TWRP's ramdisk,
    no recovery dtbo (ABL then uses the dtbo partition), cmdline = the boot image's + `androidboot.selinux=permissive
    buildvariant=eng androidboot.usbconfigfs=true`, os_version 16.0.0 / 2026-02 (`mkbootimg` from toolbin). TWRP comes
    up with adb on this kernel. (TWRP's own kernel 4.19.157 has no audio stack at all.)
  - Bring-up by hand: modem partition vfat read-only on `/vendor/firmware_mnt` and `/firmware` (ueventd
    firmware_directories), `echo 1 > /sys/kernel/boot_adsp/boot` (ADSP ONLINE, apr_tal_rpmsg "apr_audio_svc" Up), then
    the vendor's own **`qrtr-ns -f`** and **`pd-mapper`** run from a read-only vendor mount
    (`LD_LIBRARY_PATH=/tmp/v/lib64:/system/lib64`): sysmon-qmi connects to the ADSP's SSCTL, diag connects, `servloc:
    Connection established with the Service locator`, `service-notifier: ... 74 service`, `msm/adsp/audio_pd ... is up
    on adsp`, **`apr_adsp_up: Q6 is Up`**, sound card **kona-mtp-snd-card** with `tert_mi2s_rx_cs35l41_dai_links`.
  - `tools/umi-atone.c` (+ `tools/umi-atone-build.sh`, libc-free static aarch64): ALSA controls by name + a 1 kHz S16
    stereo 48 kHz tone on pcmC0D0p (MultiMedia1). Settings: `TERT_MI2S_RX Channels` Two, `Format` S16_LE,
    `SampleRate` KHZ_48, **`PCM Source` = ASP and `RCV PCM Source` = ASP** (amp DSP bypassed: items {None, ASP, DSP}),
    `TERT_MI2S_RX Audio Mixer MultiMedia1` = 1, then `umi-atone tone 5 6000` -> heard.
  - Kernel log of a tone: cs35l41 1-0040 / 1-0042 hw_params + `set_sysclk freq=1536000` (our MI2S bit clock),
    `__afe_port_start: port id: 0x1004` (topology id -22 and missing cal blocks are harmless), `adm_open: port 0x1004
    ... topology 0x10312 bit_width 16`, unmute, 3 s, adm_close / afe_close. **So the ADSP's AFE/ADM/ASM answer Linux.**
  - CS35L41 per-stream writes (regmap trace, both amps; static config was written at probe): 0x2c04 0xb70 -> 0xb60 ->
    0x360 -> 0x370 -> 0x10370 (PLL from SCLK), 0x201c 0x1001010, 0x4800 0x10000, 0x2018 0x21, test key 0x40 = 0x55,
    0xaa, 0x2084 0x2f1aa0, 0x40 = 0xcc, 0x33, 0x2014 0x1 (global enable), 0x6000 0x8000 -> 0xa000; stop: 0x4800 0,
    0x2018 0x20, 0x2c04 0x370, 0x2014 0, read 0x10010 (IRQ1 status) / write 0x800000, 0x2084 0x2f1aa3 (test key around
    it), 0x201c 0x1001000. Files `research/audio-umi/twrp/` (dmesg, mixer list, regmap trace; not in git).
  - **What Linux does before its first APR command that we may not:** the APPS QRTR name service (qrtr-ns) runs, the
    kernel connects to the ADSP's SSCTL and DIAG services, the service locator is a separate APPS QRTR server, and the
    PDR notifier registers for instance 74. Next: diff this against our kernel's QRTR/servreg/APR sequence (and, if
    needed, trace more here: i2c events, the GLINK/QRTR control traffic) until the iOS side gets an AFE answer.
- **2026-11-01 0220: NOT TIMING, NOT OUR FASTRPC, NOT THE ROOT PD** (patch `xnu/patches/0220-umi-adsp-probe-rounds-rootpd.patch`).
  - `umi-0219b-norpc-longprobe.img` (`sweetadsprpc=0 sweetadspafe=0 sweetadspprobeevery=10 sweetadspproberounds=30`):
    no FastRPC at all, the five probes every ~15 s for 5+ minutes: the core answers GET_FWK_VERSION every round (22/22),
    ASM / ADM / AFE never. So a slow audio PD start or our createstaticpd disturbing it are ruled out.
  - `umi-0219c-rootpd.img` (`sweetadsppd=0`): FastRPC INIT_ATTACH to the ADSP **root PD** (pd bits 0, as postmarketOS
    hexagonrpcd) -> 0, listener registered, **no reverse calls at all**; ASM / ADM / AFE still silent over 10 rounds.
  - Upstream Linux runs this kind of Elite ADSP (RB5 / sm8250 boards) with q6core/q6afe/q6asm and no audiopd: it waits for
    the "avs/audio" PDR UP (ours is UP) and sends the same APR packets (same src/dest domain + svc addressing; apr_tal is
    plain rpmsg, no GLINK signals). Something else is different here.
  - **Next idea (read-only, needs the user's OK):** the phone's TWRP runs Xiaomi's own kernel with the whole downstream
    audio stack (apr, q6core, q6afe, adsp-loader). Boot TWRP from RAM and read its dmesg / debugfs (apr, q6core,
    audio_notifier, adsp ssr) to see the working APPS<->ADSP start-up order and any command we never send. Other
    options: ADSP-side logs (diag / QDSS / FARF via adspmsgd), or a deliberate ADSP crash to read the SFR.
  - **TWRP checked (2026-11-01, read-only, user OK'd):** TWRP's kernel (4.19.157-perf, Xiaomi build) has **no downstream
    audio stack**: no apr / q6core / q6afe / adsp-loader symbols in /proc/kallsyms, no /sys/kernel/boot_adsp, ADSP
    subsystem OFFLINING; only fastrpc probes ("service location enabled for avs/audio (audio_pdr_adsprpc)"; ION heap
    "adsp" at 0xecc00000 + 0x800000 = Android's adsp_mem placement). The vendor partition has only 3 .ko (gspca, rmnet):
    Xiaomi builds the audio techpack into the stock kernel. dmesg kept in `research/audio-umi/twrp/` (not in git).
    -> To see the working start-up: the stock boot image's kernel (`~/ios-umi-backup/boot-read-2026-10-21.img`) with
    TWRP's ramdisk, booted from RAM (not stock Android: it could try to wipe the unknown userdata), then
    `echo 1 > /sys/kernel/boot_adsp/boot` and read the downstream apr/q6core/audio_notifier log.
- **2026-11-01 0219: NO AUDIO-PD SERVICE ANSWERS ANYTHING** (patch `xnu/patches/0219-umi-adsp-service-probe.patch`, boot
  `shim/out/umi-0219-probe.img`, 0215d's line). After core ready, one harmless command a second:
  - core (svc 3, root PD) AVCS_CMD_GET_FWK_VERSION 0x1292c -> **answered** (0x1292d, 148 bytes, 9 services; note the
    response header field 0x181 = an 8-word header);
  - core AVCS_CMD_CREATE_LPASS_NPA_CLIENT 0x12985 {node 1 = sleep-island core driver, "SWEET"} -> no answer (it is only
    for island transitions anyway);
  - ASM (7) ASM_CMD_SHARED_MEM_UNMAP_REGIONS 0x10d94 {0}, ADM (8) ADM_CMD_SHARED_MEM_UNMAP_REGIONS 0x10324 {0}, AFE (4)
    AFE_SERVICE_CMD_SHARED_MEM_UNMAP_REGIONS 0x100ec {0} -> **none answered** (each should return an APR error result);
  - the AFE's LPASS core votes still answered (0x1b / 0x1c).
  - So the audio PD (servreg UP, createstaticpd 0, module loading through our apps_std) does not process APR commands
    for ASM, ADM or AFE; the vote path is evidently served elsewhere (LPASS resource manager). GET_STATE answered 1
    within 1 s of the ADSP's start, before createstaticpd, so it says nothing about the audio PD.
  - Open questions: does the audio PD wait for something from APPS before its APR services run (e.g. a PDR/servreg
    indication ack, an audio-PD restart notification, or Android's ACDB/AVS start-up through q6core), or does its
    APR need a separate route? Diagnostics would help: the PD's FARF/diag messages (none arrive over apps_std).
- **2026-11-01 0218: AFE ANSWERS THE LPASS CORE VOTES, BUT NOT ITS PORT/SERVICE COMMANDS** (patch
  `xnu/patches/0218-umi-adsp-appsmem-votes.patch`; boots `shim/out/umi-0218{,b,c,d,e,f}-*.img`, 0215d's line).
  - apps_mem request_map64 (4 KiB, rflags 8) answered: low RAM 0xd4c00000 (1 MiB, 16 KiB steps), FastRPC mmap on
    handle 1 **method 2** (the downstream umi adsprpc.c 64-bit call `REMOTE_SCALARS_MAKE(2, 2, 1)`; method 4 = its
    32-bit compat variant: the ADSP answered -1), {pgid, flags, vaddrin 0, num 1} + {pa, size} -> vaddr. 0218b got
    0x8000040e (DSP base 0x80000400 + 14 = AEE_EBADPARM).
  - **createstaticpd with pageslen 1** (downstream sets 1 when it passes the heap; upstream sends 0): with it the
    audio PD no longer asks apps_mem at all (0218c) - the heap was ignored before.
  - **LPASS core hardware votes** (Linux q6afe-clocks: AFE_CMD_REMOTE_LPASS_CORE_HW_VOTE_REQUEST 0x100f4 {block 3
    LPASS_HW_MACRO / 4 LPASS_HW_DCODEC, "SWEET"}) -> 0x100f5 with 0x1b / 0x1c (the client handles): **the first AFE
    answers ever** (0218d).
  - Still unanswered, every try: AFE_SVC_CMD_SET_PARAM clock set (0x100f3, and SVC_SET_PARAM_V2 0x100fc tried in
    0218e's plan), AFE_PORT_CMD_SET_PARAM_V2 I2S config (68 bytes, hex-dumped, byte-exact against the downstream
    los techpack structs), and a 24-byte AFE_PORT_CMD_DEVICE_STOP for 0x1004 (0218f) -> not a size problem: the AFE's
    port/service handler is not running while the vote path (resource manager) is.
  - Downstream sources for reference (not in git): LineageOS android_kernel_xiaomi_sm8250 lineage-20 techpack/audio
    `dsp/q6afe.c`, `dsp/q6core.c`, `include/dsp/apr_audio-v2.h`; Xiaomi umi-q-oss `drivers/char/adsprpc.c`
    (`research/linux-refs/`).
  - Next test, built: `umi-0218g-nocirrus1.img` (`sweetadspnocirrus=1`: our apps_std reports capi_v2_cirrus_sp.so
    missing - is the AFE stuck behind that module's load?) and `umi-0218g-nocirrus0.img` (loads it and logs each
    module fread). Other leads in q6core.c: AVCS_CMD_REGISTER_TOPOLOGIES / LOAD_TOPO_MODULES / MAP_MDF_SHARED_MEMORY
    / CREATE_LPASS_NPA_CLIENT, which the Android audio HAL drives before the first AFE port.
  - **0218g nocirrus1 (booted 15:24):** with capi_v2_cirrus_sp.so reported missing (fopen -2), the votes are answered
    as before and the DEVICE_STOP probe and every I2S config try are still unanswered -> **the speaker-protection
    module's load is not what blocks the AFE.** Remaining lead: the AVCS start-up commands the HAL sends (q6core.c).
- **2026-11-01 0217: THE ADSP AUDIO PD IS CREATED AND LOADS ITS MODULES FROM US; AFE still silent** (patch
  `xnu/patches/0217-umi-adsp-audiopd-fastrpc.patch`; boots `shim/out/umi-0217b..e-audiopd.img` = 0215d's line, last
  `umi-0217e-audiopd.img`; built not booted: `umi-0217f-audiopd.img` with apps_mem logging).
  - Phone files (user OK'd, new only, rm + put + read back): `/private/var/sweet/adsp-rpc/adsp/` = capi_v2_cirrus_sp.so,
    misound_res.bin, misound_karaoke_res.bin, misound_karaokemix_res.bin, hrtf5c.bin, libapps_mem_heap.so (vendor
    lib/rfsa/adsp) and `/private/var/sweet/adsp-rpc/acdb/adsp_avs_config.acdb`.
  - **The "freezes" were panics with the screen off:** `IO_MAP_SIZE` (osfmk/arm/io_map.c) is 8 MiB and the port's
    ml_io_maps (61 call sites, SMEM 2 MiB, 16 KiB pages) used it up; io_map allocates KMA_NOFAIL|PAGEABLE|PERMANENT =
    the `kmem_alloc(.., 0x100021): failed with 3` of 0215c. 0216c (amp probe: TLMM/GCC/SE3 maps) and 0217 (three
    SMMU route maps) died at that point with the panel already off (auto-lock), so no panic text. **64 MiB on
    SWEET** fixed it (0217b+: no freeze). The amp probe may simply have hit this too (not retried yet).
  - Sequence that works now: SMMU streams 0x1803-0x1805 routed (cb 3 in address bits 32+); heap 0xd4000000 +
    0xc00000 zeroed and **SCM MP_ASSIGN** (svc 0xc cmd 0x16, arginfo 0x1117, extra args via x5: src {HLOS 3}, mem
    {addr, size}, dest {LPASS 22 RWX, ADSP_HEAP 37 RWX}) -> 0; FastRPC method 8 on handle 1, pid 0, ctx pd 1 (USER_PD):
    {pgid, namelen 8, pageslen 0}, "audiopd", {heap pa, size} -> **createstaticpd 0**; remotectl open
    adsp_default_listener, register, init2 -> 0; then the audio PD's reverse calls.
  - GLINK gotcha: the ADSP advertises dozens of 0x80 intents per channel (apr_audio_svc, IPCRTR); the 128-entry remote
    intent table filled and the FastRPC channel never got one ("could not send", 0217b/c) -> 512 entries.
  - What the audio PD asks: apps_std open; fopen `adsp_avs_config.acdb` (ADSP_AVS_CFG_PATH -> acdb/) + **ftell** (method
    8, added with flen 10, rewind 11, feof 12); fopen **capi_v2_cirrus_sp.so** (loaded, 312952 bytes); the aptX
    encoder/decoder (not copied); **remotectl open "apps_mem" (refused)**, then a call on handle -1 method 2
    (apps_mem request_map64); fopens of voice modules `fluence_voiceplus_module.so.1`, `mmecns_module.so.1`,
    `custom_{sm,dm,qm}_ecns_{1,2}.so.1` (not on the vendor partition either: optional); then quiet.
  - **AFE clock set still never answered** (9 tries, sent right after the listener came up). Next: apps_mem.
    The PD wants heap from APPS: Android allocates an ION buffer and maps it into the ADSP with FastRPC INIT_MMAP
    (handle 1, method 4: {pgid, flags, vaddrin, num pages} + pages -> vaddrout), then answers request_map64 with
    {vapps, vadsp}. 0217f accepts apps_mem and logs each request's words, to size that pool.
  - **0217f (booted 14:13):** the audio PD asks apps_mem **method 2 = request_map64** once, words
    `0 0xa0000000 0x8 0 0 0 0x1000 0` = heapid 0, lflags 0xa0000000, **rflags 8 = ADSP_MMAP_REMOTE_HEAP_ADDR**, vin 0,
    **len 0x1000** (4 KiB). We fail it; the PD then goes on with the voice-module fopens and goes quiet, and the AFE
    clock set is again never answered. Next (Linux fastrpc_req_mmap): take 4 KiB of low RAM, FastRPC INIT_MMAP (handle
    1, method 4, sc (4, 2, 1), pid 0): in {s32 pgid, u32 flags 8, u64 vaddr 0, s32 num 1} + page {pa, 0x1000}, out
    {u64 vaddr}; then (REMOTE_HEAP_ADDR) MP_ASSIGN that page HLOS -> LPASS + ADSP_HEAP like the heap; answer
    request_map64 with {u64 vapps (our VA or 0), u64 vadsp = the returned vaddr}.
- **2026-11-01 (no boot): WHAT ANDROID RUNS FOR THE ADSP AUDIO PD** - read-only TWRP pull (user OK'd) of vendor
  `etc/init/vendor.qti.adsprpc-service.rc`, `bin/adsprpcd`, `lib/libadsprpc.so`, `etc/acdbdata/adsp_avs_config.acdb`
  + the ACDB list, and the audio modules of `lib/rfsa/adsp` (not in git, `research/audio-umi/{vendor-init,rfsa-adsp}`).
  - The rc starts two FastRPC daemons on the ADSP: `vendor.adsprpcd` (`/vendor/bin/adsprpcd`, default/root PD) and
    **`vendor.adsprpcd_audiopd` (`/vendor/bin/adsprpcd audiopd`, user media)**. adsprpcd only dlopens
    libadsp_default_listener.so and runs `adsp_default_listener_start`; libadsprpc.so does
    **`createstaticpd:audiopd`** (FastRPC create of the static audio PD, with a remote heap) and serves the PD's
    reverse calls: **apps_std** (file open/read; search path `ADSP_LIBRARY_PATH` =
    `/vendor/lib/rfsa/adsp;/vendor/lib/rfsa/dsp;/vendor/dsp`) and **apps_mem** (`apps_mem_request_map64`: the PD
    asks APPS for heap memory, mapped for the DSP).
  - This fits the silent AFE of 0216: the audio PD is "UP" for servreg, but without its listener it cannot get files
    or heap. Next kernel step: FastRPC on the ADSP edge (sweet_slpi.c's listener is SLPI-only): createstaticpd
    "audiopd" (Linux fastrpc.c FASTRPC_IOCTL_INIT_CREATE_STATIC: method 8 on handle 1 {namelen, memlen, name, mem
    page}, memory from the DT adsp remote heap `qcom,msm-adsprpc-mem` 0xc00000 bytes, hyp-assigned to the ADSP VMIDs
    `qcom,adsp-remoteheap-vmid` 0x16/0x25), then the listener with apps_std files from the iOS root and apps_mem from
    a low-RAM pool, and an ADSP SMMU stream route like the SLPI's 0x541.
  - `lib/rfsa/adsp` audio files: **`capi_v2_cirrus_sp.so`** (Cirrus speaker protection running on the ADSP, CSPL),
    misound_res.bin / karaoke / karaokemix, hrtf5c.bin, aptX encoder/decoder, libapps_mem_heap.so. `/vendor/dsp` is
    empty. `adsp_avs_config.acdb` (1120 bytes) = the AMDB list (QCMSNDDB/AMDB: capi_v2_cirrus_sp "CIRRUS_SP", aptX...)
    the audio HAL registers with the ADSP. ACDB: `etc/acdbdata/Tutu/Tutu_{Speaker,Handset,Headset,Bluetooth,
    General,Global,Hdmi}_cal.acdb` + workspace (not pulled).
- **2026-11-01 0216: AUDIO PD IS UP, BUT THE AFE NEVER ANSWERS; amp probe froze the phone** (patch
  `xnu/patches/0216-umi-adsp-afe-amp.patch`; boots `shim/out/umi-0216-afe.img`, `umi-0216b-afe.img`, `umi-0216c-amp.img`,
  all 0215d's line). No sound, nothing changed on the phone.
  - After core ready the kernel sends the AFE steps Linux q6afe uses for an MI2S port, each waiting for the
    APR_BASIC_RSP_RESULT: (1) AFE_SVC_CMD_SET_PARAM 0x100f3, AFE_MODULE_CLOCK_SET 0x1028f / AFE_PARAM_ID_CLOCK_SET 0x10290
    {version 1, clk id TER_MI2S_IBIT 0x104, 1536000 Hz, attr COUPLE_NO, root 0, enable}; (2) tert MI2S pins
    133/134/135 function 1 (mi2s2_sck/data0/ws, 8 mA), AFE_PORT_CMD_SET_PARAM_V2 0x100ef port 0x1004,
    AFE_MODULE_AUDIO_DEV_INTERFACE 0x1020c / AFE_PARAM_ID_I2S_CONFIG 0x1020d {1, 16 bit, SD0, stereo, WS internal,
    48000}; (3) AFE_PORT_CMD_DEVICE_START 0x100e5.
  - **Step 1 is never answered**: 9 sends 3 s apart, each consumed by the ADSP (GLINK RX_DONE on apr_audio_svc), no
    result, no error, no crash (0216, 0216b). The core (svc 3) answers in the same session.
  - Servreg notifier (QMI 0x42 at node 5 port 3, register listener 0x20 for "msm/adsp/audio_pd"): result 0,
    **audio PD state 0x1fffffff = UP**. So the AFE's domain runs; its service looks blocked rather than absent.
  - Leading hypothesis (unproven): the audio PD waits on its APPS FastRPC listener. The ADSP opens
    "fastrpcglink-apps-dsp" and nothing serves it; on SM8250 Android `audioadsprpcd audiopd` attaches to the audio PD
    and serves apps_std file reads (as hexagonrpcd/sscrpcd did for the SLPI's sensor PD, 0211). Next evidence: vendor
    `etc/init/*audio*` / `*adsprpc*` rc files and the lists of `/vendor/lib/rfsa/adsp`, `/vendor/dsp` (TWRP, read-only,
    needs the user's OK); then FastRPC to the audio PD (sweet_slpi.c's FastRPC listener for the ADSP edge).
    Other candidates: AFE_CMD_REMOTE_LPASS_CORE_HW_VOTE_REQUEST 0x100f4 first (Linux votes LPASS_HW_MACRO 3 /
    DCODEC 4 for the codec path), or a different AFE set-param version.
  - **Amp probe froze the phone (0216c):** the log stops ~1-2 s before the probe's first line would show (the last
    lines before a hard hang never reach the Mac), screen off, no input, needed Vol Down + Power. The probe maps TLMM
    north (gpio 114), votes GCC 0x52008 bits 6-9 + 13 (wrap0 m/s-ahb, core, core2x, s3), checks branches, then reads
    QUP0 SE3 (0x98c000). Unknown which access hangs. The probe is now opt-in (`sweetamp=1`) and logs + pauses 1 s per
    step (`sweetampstepms`); image `shim/out/umi-0216d-amp.img` has it on, not booted yet.
  - The GLINK service loop for the ADSP ends after `sweetadspsecs` (600 s); the ADSP stays up after that (0215d log,
    item 423 then only holds its boot placeholder "SFR Init: wdog or kernel error suspected.").
- **2026-11-01 0215: THE AUDIO DSP (ADSP) RUNS, Q6 CORE READY OVER APR** - first step to sound (patch
  `xnu/patches/0215-umi-adsp-start.patch`, boot `shim/out/umi-0215d-adsp.img` = umi-nofp-sample's line +
  `sweetadsp=1 sweetadspdelay=200`). Nothing plays yet; the amps are untouched.
  - Firmware (user OK'd, read-only in TWRP, not in git, `research/audio-umi/`): modem partition `image/adsp.mdt` +
    `adsp.b00-b18` (19 MB), copied to the new phone folder `/private/var/sweet/adsp/` (rm + put + read back, nothing
    overwritten); also vendor `etc/mixer_paths*.xml`, `audio_platform_info_intcodec.xml`, `audio_policy_configuration.xml`
    and `firmware/cs35l41-dsp1-*` (amp protection firmware + tunings) for later.
  - Kernel: `sweet_slpi.c` takes the remote processor as parameters; `sweet_adsp.c` compiles it again for the ADSP:
    pas 1, dt pil_adsp_region 0x8bb00000 + 0x2500000, SMEM host 2, IPCC client 3 (0 GLINK, 2 SMP2P), SMP2P items
    443 in / 429 out, crash reason item 423, AOP load_state "adsp"; GLINK channel "apr_audio_svc" (intents 20 x 0x200)
    instead of FastRPC. Boot-args `sweetadsp`, `sweetadspdelay`, `sweetadspsecs` (GLINK service time, default 600).
  - Result: TrustZone auth + reset 0; SMP2P ready+handover in 10 ms; the ADSP OPENs pcie_drv, mhi_sat,
    fastrpcglink-apps-dsp, IPCRTR, LOOPBACK_CTL_LPASS and **apr_audio_svc** (Elite APR; no "adsp_apps" = not
    AudioReach); QRTR node 5 announces 0x301, 0x42 (inst 0x4a01), 0x1005, 0x2b, 0xf x2, 0x33, 0x18 and asks our service
    locator for "avs/audio" (1 domain) and tms/pdr_enabled / pddump_disabled. APR (hdr 0x150, APPS domain 5 -> ADSP 4,
    svc 3) GET_STATE 0x1290c -> **1 = ready** on the first query; GET_VERSIONS 0x12905 -> core 0x3 (0x40002), **AFE 0x4
    (0x260000), ASM 0x7 (0x70002), ADM 0x8 (0x70000)**, voice 0x9-0xb, 0xc, 0xd.
  - Panics on the way (both fixed in 0215): (a) `vm_map_delete ... Attempting to remove permanent VM map entry`:
    kfree_data of whole-segment kalloc_data buffers (the ADSP has 2.4 and 11 MB segments, the SLPI none that big) -
    segments are now streamed from the file through a 16 KiB buffer; (b) `kmem_alloc(.., 2097152, 0x100021): failed
    with 3` = the ADSP's own `ml_io_map` of SMEM (2 MiB): I/O VA space is nearly full - both DSPs now share one cache
    of device maps (`sweet_dsp_io_map`). A plain (non-permanent) VA-only 2 MiB window also found no space (0215b), so
    the copy window stays KMA_PERMANENT. The SLPI still starts (auto-brightness readings in the same boot).
  - **Hardware path to the speaker** (umi dtbo overlay 9 + vendor mixer paths): two **Cirrus CS35L41** amps on
    QUP SE3 I2C (`i2c@98c000`, GSI DMA): 0x40 speaker (IRQ GPIO 113), 0x42 earpiece "RCV" (IRQ 112), shared reset
    GPIO 114; boost 4000 mA / 1000 nH / 15 uF. Android plays speaker through **TERT_MI2S_RX** (AFE port 0x1004,
    48 kHz, 2 ch, S16/S24) into the amps' ASPRX1, amp DSP running "Protection" firmware (`PCM Source DSP`, gain 18);
    the bolero/WSA881x speaker path in the base DT is unused on umi.
  - **iOS side:** no built-in HAL plug-in file on iOS; CoreAudio itself has `HALS_IOA2Device` / `HALS_IOA2UCDevice`,
    which match IOKit `IOAudio2Device` services and talk through a user client (stream formats, controls,
    MapIOBufferForStream, MapEngineStatus, config change); the ABI can be read out of CoreAudio in the 20H392 cache as
    was done for IOMFB. VirtualAudio.plugin (disabled since image v12: crashed without a device) builds the default
    'vdef' device on top of it and comes back once a real device exists.
  - **Plan:** (2) APR to AFE: Linux q6afe port start of TERT_MI2S_RX (0x1004) with the MI2S clock set over AFE
    (AFE_PARAM_ID_LPAIF_CLK_CONFIG / clock set), pinctrl for the tert MI2S pins; (3) CS35L41 over SE3 I2C (reuse the GPI
    I2C of touch): reset, DEVID 0x35a40, boost + ASP config, PCM source ASPRX1 (DSP bypassed first), unmute;
    (4) ASM stream + ADM route (or AFE's direct port path) with PCM from shared memory mapped for the ADSP (its SMMU
    streams, as FastRPC's 0x541 for the SLPI) -> a kernel test tone (boot-arg); (5) an IOAudio2Device + user client
    for CoreAudio feeding that buffer, VirtualAudio back, mediaserverd/audiomxd routing to the speaker.
- **🎉 2026-11-01: SETTINGS > PRIVACY & SECURITY > LOCATION SERVICES ROW IS BACK (user: "it show up all good")** -
  CommCenter is in launchd's job list again. Boot `shim/out/umi-nofp-sample.img` (unchanged).
  - Phone file changed (user OK'd): `/System/Library/xpc/launchd.plist` + job
    `/System/Library/LaunchDaemons/com.apple.CommCenter-noncellular.plist` (532 jobs), made with
    `tools/patch-launchd-plist.py IN OUT --add KEY=JOB.plist` (new option; the job plist is still on the phone's root,
    no IPSW download needed). Previous file on the phone as `launchd.plist.sweet-nofp` (`.sweet-orig` = the pre-fairplayd
    one, untouched); copies in `~/ios-umi-backup/root-edits-2026-10-31/` (not in git). Written with rm + put, read back
    identical.
  - Why noncellular: both CommCenter jobs have Label com.apple.CommCenter; the cellular one has
    `_LimitLoadToDeviceTree baseband`, the noncellular one `_LimitLoadFromDeviceTree baseband`. umi's ADT has no
    `baseband` node (only /product baseband-chipset), so only the noncellular job applies. (Image v13 had removed both.)
  - Result: CommCenter starts early (before runningboardd), Settings opens Privacy & Security without a hang and shows
    the Location Services row (`getSubscriptionInfoWithError:` now answers without an error, so
    `refreshLocationServicesAvailable` defaults to true). SpringBoard unaffected.
  - **CommCenter crash-loops but still answers** (KeepAlive relaunches it; 9 crashes in the first minutes, 10 execs):
    sig 6 = uncaught C++ exception (std::terminate <- _dispatch_client_callout) and sig 11 =
    `ApplePDPHelperInterface::callStructMethod` locking a never-set-up mutex (USB-C power-delivery helper, far 0,
    from CommCenter main+0xa2e9e8). Harmless for the Settings row; cost is CPU + ReportCrash. Not investigated:
    what the exception is (`sweetiolog=CommCenter` would show it) and whether Setup would now finish instead of hanging.
- **🎉 2026-10-31: LOCATION SERVICES WORK (user: Weather shows the city for My Location)** - no kernel change, no
  FairPlay work: fairplayd.H2 is simply not in launchd's job list any more. Boot `shim/out/umi-nofp-sample.img` =
  0213c's kernel and line (without `sweetmgreset=1`) + `sweetsample=locationd,wifid`; the plain 0213c image works the
  same (only launchd.plist and a prefs file changed).
  - Phone files changed (user OK'd each; originals next to them as `*.sweet-orig` and in
    `~/ios-umi-backup/root-edits-2026-10-31/`, not in git):
    1. `/System/Library/xpc/launchd.plist`: job `com.apple.fairplayd.H2` removed (531 jobs), made with
       `tools/patch-launchd-plist.py IN OUT --remove com.apple.fairplayd.H2` (new option). launchd no longer registers
       com.apple.fairplayd / .versioned / unfreed, so locationd's MIG call (msgh_id 1203, 2026-10-25) fails at once
       instead of queueing forever. No `exec fairplayd.H2` in the boot (was ~60-1000 per boot).
    2. `/private/var/mobile/Library/Preferences/com.apple.locationd.plist`: `LocationServicesEnabledIn8.0` = 1 added
       (the master switch Setup's Location page sets; Setup was skipped on this image, so it was off).
  - Result, first boot (launchd only): samples show locationd and wifid idle in their run loops, nothing in the
    FairPlay stub (locationd+0xc74f4) or in a CoreLocation call. **The wallpaper gallery's Featured row is back**
    (duetexpertd's ATXLocationManager init returns). Maps said Location Services is off.
  - Second boot (+ master switch): Maps shows the "Allow Maps to use your location?" prompt; after allowing, **Weather
    shows the user's city** (Wi-Fi positioning through Apple's server over en0; no GPS driver). Maps' map itself does
    not draw (blank; likely its Metal map renderer - ADRENO fence timeouts in the log - not location).
  - **Settings > Privacy & Security has no Location Services row**, and not because of locationd:
    `-[PUIPrivacyController refreshLocationServicesAvailable]` (PrivacySettingsUI) asks CoreTelephony
    `getSubscriptionInfoWithError:`; with no error and no carrier saying otherwise the value defaults to true, but
    the call fails because CommCenter is not in launchd.plist (removed in image v13: Setup hung on it), so the cached
    value stays nil and `-specifiers` removes the "LOCATION" specifier. Turning location on/off or per-app settings
    therefore needs CommCenter back (or the prefs key above). Not done.
  - **File server gotcha:** `umi-files.py put` over an existing, longer file leaves the old tail (vnode_open with
    O_TRUNC does not truncate here): the first launchd.plist write was 311 bytes too long (a broken binary plist,
    caught by reading it back). `rm` first, then `put`, and always read back and compare.
  - Not done: CoreLocationMigrator (removed 2026-10-30) can go back now that locationd answers (untested);
    `com.apple.fairplaydeviceidentityd` is still in launchd.plist (on demand, never seen to block anything).
- **🎉 2026-10-31 0213-0214: AUTO-BRIGHTNESS WORKS (user confirmed: dims when covered, brightens under a lamp)**
  (patches `xnu/patches/0213-umi-als-hid.patch`, `0214-umi-qrtr-resume-tx.patch`; boot
  `shim/out/umi-0213c-resume20.img` = 0204's line + `sweetslpi=1 sweetslpidelay=150`).
  - 0213 `SweetHIDALS` (SweetHID.cpp, matched on IOResources): the SEE lux as Apple's vendor-page ALS, PrimaryUsagePage
    0xff00 / PrimaryUsage 4, Built-In, DeviceUsagePairs; ambient light event (level + Illuminance) on change and at
    least every 2 s. backboardd opens it (CBABModuleiOS addHIDServiceClient -> AABC::open, AABC::registerService
    needs Built-In == true and DeviceUsagePairs; HandleALSEvent reads the level field as float).
  - Settings > Accessibility > Display & Text Size > Auto-Brightness only shows when MobileGestalt
    `ambient-light-sensor` (lo3szoQ4sLy7o3+ZD0GcAQ) is true = IOServiceGetMatchingService(IOPropertyMatch
    {PrimaryUsagePage 0xff00, PrimaryUsage 4}) (libMobileGestalt 0x19c575320). The answer is cached on disk, so the
    first boot with 0213 needs `sweetmgreset=1` once (done on the phone 2026-10-31, old cache kept as .sweet-old).
  - 0214: the SLPI's IPC router stops after 10 packets without RESUME_TX (confirm_rx on the 5th). RESUME_TX must be
    sent from the receiving port to the sender's port as a full 20-byte qrtr_ctrl_pkt; from the control port (0213b)
    or with 12 bytes it is ignored and the ALS went quiet after 6 readings.
  - Typical readings: room 40-90 lux, covered 0-15, desk lamp ~5000; AAB ramped 100 -> ~2 nits in the dark and
    ~9 -> 160+ nits under the lamp. No True Tone (the sensor reports lux only, no color).
- **🎉 2026-10-31 0212: THE AMBIENT LIGHT SENSOR READS** (patch `xnu/patches/0212-umi-als-see.patch`, boot
  `shim/out/umi-0212-see.img` = 0204's line + `sweetslpi=1 sweetslpidelay=150`; sensor files already on the phone).
  - SEE client in the kernel (QMI 400 at node 9 port 0xc, our QRTR port 0x4000): request 0x20 TLV 0x01 = u16 len +
    protobuf sns_client_request_msg {suid 1, fixed32 msg_id 2, susp_config 3 {APSS 1, WAKEUP 0}, request 4 {payload 2}};
    indications 0x21 TLV 0x02 = u16 len + sns_client_event_msg {suid 1, events 2 {fixed32 msg_id 1, fixed64 ts 2,
    bytes payload 3}}. SUID lookup msg 512 to SUID 0xabab..ab with {data_type "ambient_light", register_updates,
    default_only}; event 768 {data_type 1, suid 2 {fixed64 low 1, high 2}}; on-change config 514 (no payload); sensor
    event 1025 {repeated float data 1} (floats decoded without the FPU).
  - Phone: the first SUID event (5 s after the PD settled) is empty; the next one = 0x3733534354736d61 /
    0x5f5f5f534c413130 = "amsTCS3701ALS___". Enable answered 0; events: 163.8, 146.6, 132.4, 153.8, 132.8, 153.3 lux
    (3 floats each, 2nd close to the 1st) while the user covered the sensor and pointed at a lamp. The spread is small:
    an under-display sensor whose raw value Xiaomi's Android compensates for the screen's own light (guess).
  - Value in the kernel: `sweet_als_lux` / `sweet_als_time`. Next: an iOS ALS (HID ambient light) service for
    CoreBrightness, then auto-brightness.
- **2026-10-31 0211: FASTRPC - THE SLPI'S SENSOR PD INITIALIZES** (patch `xnu/patches/0211-umi-slpi-fastrpc.patch`,
  boot `shim/out/umi-0211-fastrpc.img` = 0204's line + `sweetslpi=1 sweetslpidelay=240`).
  - Files (user OK'd, read-only in TWRP; not in git, `research/sensors-umi/`): vendor (dynamic partition:
    `/dev/block/mapper/vendor`) `etc/sensors` (sns_reg_config, 47 config JSONs incl. sm8250_tcs3408 / tcs3701 = ams
    light sensors), persist `sensors` (registry/registry = 187 files, registry/config, sns_reg_version, calibration
    txt; the FIFO sns_diag_flush left out), sysfs `/sys/devices/soc0/*` (hw_platform UMI, soc_id 356). On the phone
    in `/private/var/sweet/sensors/{vendor-sensors,persist-sensors,soc0}`.
  - FastRPC over GLINK channel `fastrpcglink-apps-dsp` (our lcid 2, intents 64 x 0x64): Linux fastrpc.c message
    {pid, tid, ctx = id << 4 | 2 (sensors PD), handle, sc, addr, size}, payload in low RAM 0xd3000000 (1 MiB), SLPI
    reads it via SMMU streams 0x541-0x543 -> cb4 (non-translating), sid 1 in address bits 32+. Reply {ctx, retval}.
  - Sequence (hexagonrpcd behaviour): INIT_ATTACH (handle 1, pid 0, arg tgid) 0; remotectl open
    "adsp_default_listener" 0; register 0; adsp_listener init2 (handle 3) 0; next2 loop. The SLPI opens "apps_std"
    3 times, stats/opens soc0 files, sns_reg_config, `oemconfig.so` (missing, fine), opendir + reads the whole
    persist registry: **3393 reverse calls**, then quiet, **no fatal any more** (before: USER-PD DOG at 36.5 s).
  - That boot used a 30 s next2 wait and stopped serving at 120 s; the committed kernel waits for the next call
    without a deadline and keeps GLINK running (not booted yet).
  - Next: the SEE client over QRTR (service 400 at node 9 port 0xc, QMI + protobuf: suid lookup "ambient_light",
    enable, events in lux), then an iOS ALS HID service so CoreBrightness can do auto-brightness.
- **2026-10-31 0210: QRTR WITH THE SLPI + SERVICE LOCATOR; sensor PD still stalls (needs FastRPC)** (patch
  `xnu/patches/0210-umi-slpi-qrtr.patch`, boot `shim/out/umi-0210-qrtr.img`, 0208's boot line).
  - QRTR v1 over GLINK "IPCRTR" (our node 1; TX_DATA into the SLPI's intents, freed on RX_DONE): HELLO both ways. The
    SLPI (node 9) announces services 0x42 servreg notifier (inst 0x5a01 = 90), 0x2b SSCTL, 0x0f x2, **0x190 = 400 =
    SEE sensor client (port 0xc)**, 0x33 x2, 0x18.
  - Our service locator (0x40, inst 0x101, node 1 port 1; Linux qcom_pd_mapper.c sm8250 table) is used: the SLPI asks
    "tms/pdr_enabled" and "tms/pddump_disabled" (0 domains, as Linux for sm8250) and sends a PFR (0x24) fault report
    for sensor_process. The boot showed the names without their first letter: top-level QMI strings carry no length
    byte (fixed afterwards, not booted again).
  - **sensor_process still dies at 36.5 s** ("USER-PD DOG detects stalled initialization"). Most likely cause: the
    sensor user PD loads its configuration (sensor JSONs, registry) through reverse FastRPC calls to an APPS daemon
    (Android sscrpcd / postmarketOS hexagonrpcd serving `/vendor/etc/sensors` + `persist/sensors/registry` through the
    apps_std interface) over GLINK channel `fastrpcglink-apps-dsp`. Next: FastRPC over GLINK (attach the sensors PD,
    adsp_listener with apps_std file calls), then the SEE client (service 400, protobuf) for "ambient_light".
- **2026-10-31 0209: GLINK UP WITH THE SLPI, "IPCRTR" OPEN, QRTR HELLO RECEIVED** (patch
  `xnu/patches/0209-umi-slpi-glink.patch`, boot `shim/out/umi-0209-glink.img`, same boot line as 0208).
  - SMEM writes: hwspinlock = TCSR mutex 0x1f40000 + 3 * 0x1000 (write 1, read back 1; 0 to release); private
    entry at `offset_free_uncached`, must end at or before `offset_free_cached` (an OFFSET from the partition start,
    not a size: 0209 refused with "partition full"). Allocated 430 (SMP2P out, 340 bytes) and 479 (GLINK tx 16 KiB).
  - SMP2P: our item {"$SMP", version 1 written last, features SSR_ACK, pid 0 -> 3, entry "master-kernel" = 0},
    kick IPCC 4/2 -> the SLPI's item 481 gets "smp2p" = 0 and "slave-kernel" = 0x6 (ready + handover) in 10 ms.
  - GLINK (polled every 10 ms, kick IPCC 4/0; descriptor 478 = tx tail/head, rx tail/head): VERSION 1 both ways (SLPI
    features 0x7, ack 0x1); the SLPI OPENs mhi_sat (rcid 1), fastrpcglink-apps-dsp (2), IPCRTR (3),
    LOOPBACK_CTL_DSPS (4); our OPEN of IPCRTR (lcid 1) is acked; it advertises 30 intents (16x0x80, 8x0x200,
    5x0x480, 1x0x2080), asks RX_INTENT_REQ 0x34 and sends 52 bytes = QRTR v1 HELLO (type 2) from node 9 port
    0xfffffffe.
  - **Then, 36.5 s after start: SLPI fatal**, crash reason `err_qdi.c:1038:EF:sensor_process:0x1:TMR_CLNT_1:0x89:
    dog_virtual_user.c:240:USER-PD DOG detects stalled initialization` - the sensor user PD waits for APPS.
    Suspects: our QRTR HELLO answer + the service locator (pd-mapper, QMI service 0x40 that Linux hosts for the DSPs),
    then the sensor registry Android serves over FastRPC (sscrpcd; channel fastrpcglink-apps-dsp).
- **2026-10-31 0208: THE SENSOR DSP (SLPI) STARTS** - first step to the ambient light sensor / auto-brightness.
  Kernel 716839d, patch `xnu/patches/0208-umi-slpi-start.patch`, boot `shim/out/umi-0208-slpi.img` (0204's line +
  `sweetslpi=1 sweetslpidelay=150`). Firmware: the phone's `modem` partition `image/slpi.mdt` + `slpi.b00-b20`
  (8.1 MB; pulled read-only in TWRP into `research/slpi-fw/umi/`, not in git; copied with the user's OK to
  `/private/var/sweet/slpi/` on the iOS root, where the kernel reads it).
  - **Why the SLPI:** umi's DT has no light-sensor node; every sensor sits behind the SLPI (`qcom,ssc@5c00000`,
    pas-id 12, `pil_slpi_region` 0x88c00000 + 0x2f00000). Linux path: PAS boot -> GLINK over SMEM (`glink_slpi`,
    IPCC client 4 signal 0) -> QRTR ("IPCRTR", net 2) -> SEE (sensors QMI service, protobuf) -> "ambient_light".
    The SLPI also wants its registry from APPS user space (sscrpcd over FastRPC); unknown yet whether it works without.
  - **Sequence (all answered 0):** AOP QMP (msgram 0xc300000: magic 0x4d41494c v1, our link/channel were down ->
    opened; doorbell = IPCC 0x408000 + 0xc, client 0 signal 0) took `{class: image, res: load_state, name: slpi,
    val: on}`; lcx.lvl (0x30030) / lmx.lvl (0x30040) ARC level index 15 (top); `pas_init_image(12, slpi.mdt)`,
    `pas_mem_setup(12, 0x88c00000, 0x2f00000)`, 20 relocatable segments (linked at 0x88000000) copied in,
    `pas_auth_and_reset(12)` -> SLPI runs; phone stays up.
  - **Copy gotchas:** `ml_io_map` of the 47 MiB region panicked (kmem_alloc of I/O space, KERN_NO_SPACE); a 2 MiB
    ml_io_map window panicked on unmap (permanent map entry, vm_map_delete). Working: a KMA_VAONLY 2 MiB range whose
    pages are `pmap_enter`ed (WCOMB) / `pmap_remove`d per chunk. bcopy_phys/bzero_phys avoided (dc zva on device).
  - **After start (SMEM 0x80900000, partition hosts 0-3 at +0x17f000):** the SLPI created item 481 (its SMP2P out,
    340 bytes, no entries yet), 478 (GLINK descriptor), 480 (its GLINK FIFO, 16 KiB), 608, 611 (4 KiB), 613; item
    424 = "SFR Init: wdog or kernel error suspected." (the placeholder it writes at boot). Missing = ours: SMP2P out
    430 and GLINK FIFO 479 -> it waits for APPS. DT `qcom,smem = <481 430>` is { inbound, outbound } (smp2p.c).
  - **Next:** SMEM allocation (hwspinlock: TCSR mutex 0x1f40000 lock 3) for 430 / 479; SMP2P negotiation; GLINK
    native (version, channel "IPCRTR", intents); QRTR (reuse sweet_ipcr.c); SEE client for "ambient_light"; then an
    iOS ALS HID service for CoreBrightness.
- **2026-10-31 0207: NIGHT SHIFT WORKS** (user: "it works"; boot `shim/out/umi-0207-nightshift.img` = 0204's boot
  line + kernel 0289533, patch `xnu/patches/0207-umi-night-shift-pcc.patch`).
  - **What iOS sends:** QuartzCore `CA::WindowServer::IOMFBDisplay::update_color_matrix` (fed by CoreBrightness) calls
    `IOMobileFramebufferSetMatrix(fb, 9, m)` = selector 55, scalar 9, 72 bytes = nine **int64 S31.32** (fcvtzs #32 of
    each float, row-major; decoding them as doubles gave 0 diagonals and -8 entries, 0207/0207b). Devices with
    CADeviceUseHarmonyXYZD50 send it per frame instead (`swap_set_icc_matrix` -> SetBlock sel 78, block 0x32, 64 bytes
    {u32 1, IOMFBColorMatrix floats at +0x10}); also handled, never seen here. iOS ramps the matrix in steps.
  - **Hardware:** ABL's path is CTL0 -> LM0 (CTL0 layer0 0x1000005, only CTL0 active) -> DSPP0. PCC of DSPP0 at MDP
    0xae01000 + 0x54000 + 0x1700 (Linux v6.12 dpu_6_0_sm8250.h / dpu_hw_dspp.c): enable +0x0, coefficients
    +0x10..0x30 (RED_R 0x10, GREEN_R 0x14, BLUE_R 0x18, RED_G 0x1c, ...; "RED_G" = input red into output green),
    1.0 = 0x8000, 18 bits, no negatives (clamped to 0 as Linux does). Flush CTL0 CTL_FLUSH (+0x18) bit 13 (DSPP0,
    DPU 6.x); MDP autorefresh latches it. ABL leaves PCC off (en 0). Identity -> PCC off. `sweetpcc=0` only logs.
  - Log: `SWEET PCC: on r .. g .. b .. (/32768)` / `off (identity)`.
- **2026-10-31 0206: SCREEN OFF ON LOCK WORKS** (user: "Dark, then back"; boot `shim/out/umi-0206-paneloff.img` =
  0204's boot line + kernel f8da9ef, patch `xnu/patches/0206-umi-panel-off.patch`). iOS never lowers brightness when
  backboardd turns the display off (log: `display off` with no brightness-nits write), so RequestPowerChange(0) now
  also asks the backlight's thread call for level 0 + DCS 0x28; display on sends 0x29 + the wanted level (levels set
  while off wait). The panel is not put to sleep (no 0x10/0x11), so wake is immediate; CoreBrightness then fades up
  from 0 to the slider level by itself. Log lines `SWEET BL: panel off -> 0` / `panel on -> 0, level N`.
  Still open: auto-brightness (no ALS driver). Night Shift: done in 0207.
- **🎉 2026-10-31 0205: BRIGHTNESS SLIDER DRIVES THE REAL PANEL** (user: "Yes, it works", Control Center slider,
  boot `shim/out/umi-0205k-bl.img`). Kernel f9da73b (xnu-work/bt/xnu), patch `xnu/patches/0205-umi-backlight.patch`,
  final image `shim/out/umi-0205-bl.img` (= 0204's boot line + f9da73b; differs from the tested 0205k only by
  sweetbl_trace gating and comments, not booted itself). No phone files changed.
  - **Panel** (TWRP recovery dtbo overlay 9 = umi, `xiaomi 38 0c 0a cmd mode dsc dsi panel`): Samsung AMOLED on DSI0
    (0xae94000), command mode + DSC, brightness = DCS 0x51 long write, big-endian 11-bit (bl-min 2, max 0x7ff, init
    0x218), HS mode; no WLED. ABL leaves DSI0 ctrl 0x1f5, trig_ctrl 0x4 (DMA trigger SW), cmd_dma_ctrl 0x14000000.
  - **Kernel side** (SweetFramebuffer.cpp, end of file): DCS writes through DSI0's command DMA as Linux v6.12 msm
    dsi_host.c (MSM packet `03 00 39 c0 51 HI LO ff`, DMA_BASE/DMA_LEN/TRIG_DMA, poll CMD_DMA_DONE in INTR_CTRL);
    sent in 50 us - 49 ms (waits for the MDP frame). **The command buffer must be below 4 GB**: an
    IOBufferMemoryDescriptor with a 4 GB mask came back at 0x103f24000, DMA_BASE took 0x03f24000 and the phone
    froze (0205e); now the last cont_splash page 0x9e2ff000 (`sweetbl_buf`).
  - **iOS side** (CoreBrightness in backboardd, from the 20H392 cache): needs a service that `IOObjectConformsTo`
    AppleARMBacklight with `backlight-control` true and `IODisplayParameters` {brightness {min,max,value}}; with
    `new-backlight-architecture` true it writes `brightness-nits` (SInt32 nits x 65536) on every slider/ramp step.
    `DisplayCreateWithID` silently drops the display without `backlight-marketing-table` (CFData uint32 nits x 65536;
    ours: 21 points, quadratic 0.4 -> 420 nits), and without `backlight-calibration-parameters` (lMaxPanel/lMinPanel
    etc., read as float and divided by 65536) every slider position became NitsPhysical 1.0 (0205h), plain nits gave
    0.006 nits (0205i, black). Also `digital-dimming-min-nits` / `user-accessible-max-nits` (CFData x 65536). The
    `DisplayBrightness` dicts it writes too (NitsPhysical, Brightness, ...) are ignored (decoding them fought the
    ramp with level 0, 0205j). Mapping: level = nits x 2047 / 420 (`sweetbl_maxnits`), at least 16 (`sweetbl_minlevel`).
  - **QuartzCore EDR stall (0205b):** once a backlight exists, CA's IOMFBServer registers libEDR callbacks;
    `EDRGetDefaultMinScalingFactor` waits ~5 s (mach_msg timeout) per call on CoreBrightness's EDR server, which
    does not answer here -> one frame every ~5 s. Workaround: backboardd's `IOServiceGetMatchingService`
    (CADeviceHasBacklight) does not see AppleARMBacklight; CoreBrightness uses IOServiceGetMatchingServices and still
    finds it (`sweetbl_hideca=0` shows it to CA again; untested since the marketing table fix, CoreBrightness may now
    start its EDR server).
  - Debug: `sweetbl_trace=1` logs each property user space reads on the backlight with backboardd's user backtrace
    (`UBT key slide ... bt ...`, `sweet_user_bt_current()` in exception.c) - found the missing marketing table.
  - Not done / next: screen off on lock (done in 0206); **auto-brightness** needs an ambient light sensor driver (none) and locationd is
    stuck behind fairplayd; **Night Shift / True Tone** go through CoreBrightness CFX + IOMFB color matrix (sel 55
    SetMatrix is accepted and ignored); the 420-nit top and the curve are guesses (HBM via 0x53 not used).
  - Live log tip: after each boot the Mac lost 192.168.7.1 on en8 until `tools/umi-usbnet.sh` ran again.
- **2026-10-31 repo hygiene:** `umi-scanout` history rewritten (git filter-branch over the 156 commits not on main):
  the Mac's home path became `$HOME`, the phone's serial `${UMI_SERIAL}`; nothing else changed. Scripts now need
  `UMI_SERIAL` exported (serial from `fastboot devices`). Keep home paths and serials out of tracked files.

- **2026-10-30 evening: STOCK APPS RESTORED (31 apps) + kernel 0204 file-server LIST.** Phone files changed (backups in
  `~/ios-umi-backup/root-edits-2026-10-30/`, not in git): `com.apple.migration.plist` removed once (iOS rewrote it),
  `/System/Library/DataClassMigrators/CoreLocationMigrator.migrator/CoreLocationMigrator` removed (SHA-256 c9d3bdd1...,
  mode 0755; put back with `umi-files.py put`).
  - **Why the apps were missing:** nothing removed them when the root image was built (mkiosroot.sh copies the IPSW
    whole). iOS keeps the removable apps (Clock, Calendar, Mail, Maps, Notes, Reminders, Contacts, FaceTime, Find My,
    Files, Books, Music, Podcasts, TV, News, Stocks, Weather, Calculator, Compass, Measure, Magnifier, Translate, Voice
    Memos, Shortcuts, Tips, Freeform, iTunes Store, Wallet, Health, Fitness, Watch = 31) in
    `/private/var/staged_system_apps` (placeholders in `/System/Library/AppPlaceholders`); the first-boot data migration
    installs them (`/System/Library/DataClassMigrators/SystemAppMigrator.migrator`, MISystemAppMigrator ->
    installcoordinationd/installd, which moves each bundle out of the staging folder). Image v12 skips data migration
    (`LastSystemVersion` in `com.apple.migration.plist`), so they never got installed.
  - **Fix:** removed `com.apple.migration.plist` -> migration ran (Apple logo + progress bar). The apps were installed
    within the first boot (staging folder empty), but the migration never finished: backboardd waits in
    `DMPerformMigration` (sync XPC to datamigrator), SpringBoard waits in `-[BKSSystemShellService _checkIn]` on
    backboardd, and the plugin wrapper `com.apple.migrationpluginwrapper` waits in `_CLInternalPerformMigration`
    (CoreLocationMigrator, sync NSXPC to locationd, which is stuck behind fairplayd, see 2026-10-25). With
    CoreLocationMigrator's binary removed the migration finished in ~3 min: `LastSystemVersion` 20H392 written back,
    `DMLastMigrationResults` success false (the missing plugin), IconState lists all 31 apps; the user reported only the iOS 16 wallpaper as still missing.
  - **Wallpapers:** every poster extension was already there except Weather's (inside Weather.app; back with the app,
    user sees Weather & Astronomy, Emoji, Color, Photos, Collections, Unity, Pride). The 9 collections under
    `/Library/Wallpaper/Collections/*.wallpaperCollection` match the IPSW byte for byte (plists fetched with `ipsw extract
    --remote --files --pattern 'Library/Wallpaper/.*\.plist$'` into research/ipsw-fs, user OK'd). **Still missing: the
    iOS 16 (WWDC 2022, 7400) wallpaper** - PosterBoard has its descriptor (`/private/var/mobile/Library/Application
    Support/PRBPosterExtensionDataStore/59/Extensions/com.apple.WallpaperKit.CollectionsPoster/descriptors/0D4C2F5E...`),
    but its galleryOptions say `featuredConfidenceLevel` 2 (Clownfish/Stripe/Multicolored: 1), so it belongs in the
    gallery's Featured row, which Proactive (duetexpertd, ATXPosterDescriptorGalleryOptions) fills and which is absent.
    **Cause (boot `shim/out/umi-0204-featsample.img`, sweetsample=duetexpertd,PosterBoard,CollectionsPoster):**
    duetexpertd's threads wait in `+[ATXLocationManager(Singleton) sharedInstance]` (dispatch_once, from
    ATXUpdatePredictionsManager / ATXNotificationContextManager init) -> CoreLocation -> locationd, stuck behind fairplayd.
    Same root as the CoreLocationMigrator hang: fixing locationd (fairplayd) brings the Featured row and the iOS 16
    wallpaper back. Left as is (user: move on).
  - **0204** (kernel f1555f5, `xnu/patches/0204-umi-files-list.patch`): file server `LIST <dir>` (one "<d_type> <name>"
    line per entry); `tools/umi-files.py list DIR`. Boot `shim/out/umi-0204-list.img` = 0203's boot line + this kernel.
  - **Sampler gotcha:** `sweetsample` matches `p_comm`, 16 characters: com.apple.datamigrator is `com.apple.datami`,
    the plugin wrapper `com.apple.migrat` (the "exec" log lines and SWEET AKS print the longer p_name).
  - Logs: `research/logs/umi-apps-migr.txt` (TWRP pull of the first migration boot), live log /tmp/umi-apps-migr.log.
    The Mac's USB hub dropped the phone (no ue0, no fastboot): plug it straight into the Mac.

- **🎉 2026-10-30 0203: WPA2-PSK WORKS - Settings joins a password network, traffic over en0.** Kernel
  71d1fd4 (xnu-work/bt/xnu), patch `xnu/patches/0203-umi-wlan-wpa2-psk.patch`, image `shim/out/umi-0203-wpa2.img`.
  - New `bsd/dev/sweet_wlsec.c`: supplicant half of IEEE 802.11-2016 12.7 for AKM PSK + CCMP. PMK from wifid
    (ASSOCIATE key kind 6) or PBKDF2-SHA1(passphrase, SSID, 4096); PTK = PRF-384; EAPOL-Key descriptor v2
    (HMAC-SHA1 MIC, RFC 3394 unwrap of key data); 4-way messages 1-4 and the group key handshake. Crypto checked
    on the Mac against IEEE 802.11 PBKDF2/PRF vectors, RFC 2202 and RFC 3394 (libkern sha1.h / aes.h).
  - sweet_wlce.c (ath11k mac.c/wmi.c v6.12): only WPA2-PSK/CCMP APs (group + pairwise CCMP, AKM PSK, MFP not
    required); our RSN element (caps 0) in the association request and message 2; PEER_ASSOC flag
    NEED_PTK_4_WAY instead of AUTH; after message 4 VDEV_INSTALL_KEY 0x5009 (tag 0x60, AES_CCM 4; pairwise idx 0,
    then the GTK with its RSC) -> INSTALL_KEY_COMPLETE 0x5003, then PEER_AUTHORIZE; group rekeys installed from
    the poll. **Association request capability now carries Privacy (and the AP's short preamble), as mac80211's
    ieee80211_send_assoc does**: an 802.11ax phone hotspot (RSN caps 0x3c, HT/HE/WMM/WPS) refused every WPA2
    association with status 45 (INVALID_RSNE_CAPABILITIES) whatever RSN capabilities (0, 0xc, 0x3c, 0x80, 0x8c,
    0xbc) or HT + WMM elements we sent; with Privacy set it accepted at once. sweet_wldp.c: TCL encrypt type
    CCMP_128 (6) once the pairwise key is in, OPEN (7) otherwise. sweet_wlsta.c: EAPOL to the handshake, not the
    stack; a handshake that fails after message 1 (wrong password: AP deauth reason 15) -> EAUTH (wifid: invalid
    password). Also flame 0123's AppleKeyStore wrap/unwrap (HackiOS) so wifid can store passwords.
  - Tests (live logs /tmp/umi-0203*.log, TWRP pull `research/logs/umi-0203b.txt`; not in git: network names):
    0203 on a 2.4 GHz WPA2 hotspot: first try message 2 rejected (AP deauth reason 15, wrong key typed), second
    try keys in and authorized, encrypted DHCP/ARP/ICMP both ways. 0203b-f: the 802.11ax hotspot refused (status
    45, see above). **0203g (Privacy bit): user "Connected"** - status 0 first try, keys installed, link up, "1345
    frames sent (216 KB), 1785 received (1.5 MB), 0 dropped", 1739 transmit completions acked (TQM reason 0).
    The committed kernel is 0203g minus the retry experiments (RSN caps list, HT + WMM, sweetwlrsncap /
    sweetwlenc), which never ran on the successful join; that exact build was not booted again.
  - Debug tips: the Mac's `nc -ulk 5140` locks onto the first sender port and silently drops the stream when
    the phone's port changes; a plain Python UDP receiver (bind 5140, append every datagram) does not.
  - Next: 5 GHz channels; HT/VHT rates (peer assoc is legacy 11g); WPA3/SAE and PMF if wanted.

- **🎉 2026-10-29 0201/0202: Wi-Fi IN SETTINGS - wifid scans, Settings joins an open network, traffic over en0.**
  Ported from ios-flame (NWylynko/ios-flame, Pixel 4) patch 0123, whose Apple80211 code is ios-topaz 0900 from HackiOS
  (APSL 2.0, per ios-flame CREDITS.md). Kernel commits in xnu-work/bt/xnu: 3d44864 (0201), 82beb70 (0202).
  - **0201** takes flame's three generic files unchanged: `bsd/dev/redwood_net.c` (en0 via the ifnet KPI on a "link",
    SIOCGIFMEDIA says 802.11), `redwood_apple80211.c` (SIOCGA80211/SIOCSA80211 answered: power, channels, scan,
    scan results, associate, current network; kernel events class 6 for wifid), `redwood_sta.c` (one station
    thread). Not taken: RedwoodWLAN.cpp / MiniIONetworkStack.cpp (umi has the same in SweetWLAN.cpp /
    SweetFramebuffer.cpp; `RedwoodWLANStart` publishes umi's pair), topaz 0128 quiesce (already here), keystore
    wrap/unwrap (only for WPA passwords), flame_wlan (flame's radio is in userland).
  - **0202** `bsd/dev/sweet_wlsta.c`: umi's in-kernel QCA6390 as the station + en0's link. After stage 8's first
    scan, `sweet_wlce_htc` hands over to it (boot-arg **`sweetwifid`, default 1**; `sweetwifid=0` = the old kernel
    join + DHCP + en0 of 0140-0154). sweetwlanssid becomes a standing join request (rejoined after a failed
    join). sweet_wlce.c: BSS table with signal (snr - 95, ath11k wmi.c), beacon interval, capability, IEs, age;
    START_SCAN / association / leave callable again (leave = deauth, VDEV_DOWN 0x5007 tag 0x5e, PEER_DELETE 0x6002
    tag 0x62 -> 0x6007, VDEV_STOP 0x5006 tag 0x5d -> 0x5002, ath11k wmi.h v6.12); link loss from deauth/disassoc,
    PEER_STA_KICKOUT 0x6001, ROAM 0xb001 reason 2; one lock for poll / transmit / station (waits drop it). While
    joined a real scan at most every 20 s. With the station the IO80211 entries come with en0, not at
    AppleCLCD start (`sweetwlanearly=1` forces early). Built locally (tools/build-kernel-local.sh).
  - **Boot `shim/out/umi-0202-wifid.img`** (0200 image's ramdisk swapped; boot line = 0200's minus sweetfb_dump /
    finwait / finrounds; live log /tmp/umi-0202.log, not in git: holds network names). en0 attached ~2 min after
    boot; **wifid found it at once** (CARD_CAPABILITIES, POWER, HW_SUPPORTED_CHANNELS, SCAN_REQ every ~30 s, 8-9
    SCAN_RESULTs each; scans visit all 13 channels). **No user-space change was needed**: configd made a "Wi-Fi"
    service for en0 by itself (preferences.plist now holds only that one; ue0 still works, the kernel addresses
    it), and the wifid -> locationd -> fairplayd hang of 2026-10-25 did not block wifid (fairplayd.H2 still in
    the launchd cache; ios-flame removed it). The boot-line hotspot was not on the air (join -> ENOENT).
    **User: "sans mdp ça passe mais avec non"** - an open network picked in Settings joins: ASSOCIATE (23-byte
    name, no key) -> associated AID 2, link up, configd DHCP on en0, "715 frames sent (105 KB), 583 received
    (449 KB), 0 dropped". **Password networks fail as expected**: wifid sends the PMK (key kind 6, 32 bytes),
    sweet_wlsta refuses non-open joins (EAUTH) because the data path sends unencrypted.
  - Next: WPA2-PSK (EAPOL 4-way handshake with the PMK wifid already gives, then WMI VDEV_INSTALL_KEY for PTK/GTK
    and encrypt type in the TCL descriptor; ios-flame's phone/wifi/radio.c and ath11k mac.c as references; plus
    the keystore wrap from flame 0123 so wifid can store passwords); 5 GHz channels; wifid's refused requests
    (sets 383 / 25, gets 96 / 97 / 106) seem harmless.

- **2026-10-25 GPU (Adreno 650) bring-up started, base: HackiOS** (OOSEX GANG, github.com/oosexgang/hakios-os,
  kernel APSL 2.0 / user space MIT; ios-topaz's GPU work comes from it). `hakios.adreno.c` brings up the Adreno
  642L (SM7325) whose GPU block has the same layout as umi's (0x3d00000 / GMU 0x3d6a000 / gpucc 0x3d90000 / SMMU
  0x3da0000); umi chip ID 6.5.0.2, firmware `a650_gmu.bin`, `a650_sqe.fw`, `a650_zap.*` pulled read-only from
  vendor into `research/gpu-fw/umi/` (not in git). Linux gcc/gpucc-sm8250.c vs sc7280: same GCC GPU clocks and
  gpucc GDSC / GMU / AHB / CXO / SMMU-vote offsets; SM8250 has no gpucc PLL0 and no hub clocks; GMU 200 MHz =
  source 6 (GPLL0 div) / 1.5 (same setting).
  - **0160** (`bsd/dev/sweet_adreno.c`, `sweetgpu=N`, read-only steps 1-3), boot `umi-0160-gpu3.img`, log
    `research/logs/umi-0160-gpu3.txt`: booted normally. cmd-db `gfx.lvl` 0x30050 (levels 0 48 64 128 144 192 224
    256 320 384 416), `cx.lvl` 0x30000, `mx.lvl` 0x30010, no `mmcx.lvl`; speed bin 0 (qfprom 0x78419b = 0x10);
    CX and GX GDSC 0x222001 (collapsed), gcc gpu_cfg_ahb running, memnoc/snoc enabled-but-halted, ddrss_gpu_axi
    and the GPLL0 GPU taps not voted, gpucc ahb / cxo running, cx_gmu enabled-but-halted: clean, unpowered.
  - **0161:** steps 4 (CX GDSC on), 5 (GPLL0 div vote, GCC GPU bus clocks, GMU clock 200 MHz, gpucc cxo / ahb /
    cx_gmu / smmu vote), 6 (GMU reads: sysreset, fw init result, always-on counter counting?). Every write is
    recorded and undone in reverse order at the end of the run. **Boot `umi-0161-gpu6.img` (log
    `research/logs/umi-0161-gpu6.txt`): THE GPU BLOCK IS ALIVE, no hypervisor objection.** cx_gdscr 0x222001 ->
    0xf8222000 (CX on, cx_hw_ctrl 0x80001fe0); ddrss_gpu_axi 0x80100000 -> 0x100001; gmu_clk_src 0x602 took
    (update bit cleared); cxo / ahb / cx_gmu (0x4221) / smmu vote running. GMU: cm3_sysreset 1 (held), fw init 0,
    always-on counter counts, sptprac 0xc0 (GX no power / no clock), rpmh_power_state 0xf, hfi 0, fence 0. All 7
    writes put back, CX collapsed again.
  - **0162:** steps 7 (RSCC 0x3de0000 reads), 8 (SMMU ID / stream table / CBAR, pages mapped from the ID
    registers since umi's dt gives the SMMU only 0x10000), 9 (SMMU context 0), 10 (GMU DTCM two-word write /
    read-back, undone), 11 (TrustZone: is_call_available, PAS init / auth available, PAS is_supported for audio 1,
    modem 4, video 9, GPU 13). **Boot `umi-0162-gpu11.img` (log `research/logs/umi-0162-gpu11.txt`): all ran, phone
    fine.** RSCC readable (status0 0, pdc_slave_id 1, tcs0 status 1). SMMU MMU-500: idr0 0x4c017e06 (6 SMRs), idr1
    0x20000005 (8 x 4K global pages, 5 contexts, 0x10000 total = dt), scr0 0x220406; SMRs all 0 (invalid), S2CRs /
    cb0 registers hold power-on garbage, CBARs 0: unprogrammed, ours to set up (HackiOS step 13). **GMU DTCM takes
    writes.** **TrustZone answers this kernel:** is_call_available 1, pas_init_image / pas_auth_and_reset available;
    pas_is_supported answers 0 for audio / video / GPU (modem -3145792): uninformative, as HackiOS saw.
  - **0163:** step 12, zap signature: `tools/mkadt.py` puts `research/gpu-fw/umi/a650_*` into ADT node
    `/sweet-gpufw` (umi only, no compatible); the kernel copies `a650_zap.mdt` (148-byte ELF header, 3 segments +
    6712 bytes of hashes) into a contiguous page and calls pas_init_image(13); pas_shutdown(13) at the end of the run.
    **Boot `umi-0163-gpu12.img` (log `research/logs/umi-0163-gpu12.txt`): TRUSTZONE ACCEPTS THE ZAP SHADER'S
    SIGNATURE FROM THIS KERNEL** (smc 0x42000201 (13, pa 0x104960000) -> 0, answer 0); pas_shutdown(13) -> 0. ADT with
    the firmware is 116 KB (no shim / payload limit). Next: HackiOS steps 13-17 (GMU SMMU context + page tables,
    a650_gmu.bin into the GMU, GMU start, RPMh / HFI, power the 3D core).
  - **0164:** steps 13-15 (HackiOS, A650 values from Linux v6.12 a6xx_gmu.c): a650_gmu.bin is the block format
    (NEEDS blocks 0x4000/0x8000, 0x144000/0x13000, 0x157000/0x9000, kept 0x60000000/0x1000; TCM data at 0x0 and
    0x10004000); log 0x60001000 (16K), HFI 0x60005000 (16K); SMMU context 1, match 1, stream 5 (dt gmu iommus
    5/0x400; GPU 0/0x401, secure 2, GMU user 4). GMU chip ID 0x06050200, fence range 0xa/0xa0 (a660: 0x8a0),
    rpmh_start (RSCC_CONTROL_REQ bit 1) before the firmware; started = init result & 0x1ff == 0x100 (fw > 0x20010004).
    **Boot `umi-0164-gpu15.img` (log `research/logs/umi-0164-gpu15.txt`): THE GMU'S FIRMWARE RUNS.** The hypervisor
    took the SMMU writes (smr1 0x84000005, s2cr1 1, cbar1 0x1f300, cb1 sctlr 0x27, ttbr0 ours, tcr 0x803519, sgfsr 0).
    Firmware loaded and verified (versions 0x20010008 / 0x20010008 / HFI 0x20000001); fw_init_result 0x100,
    hfi_ctrl_status 1, the GMU writes its log through the SMMU (log head 0x21 0x3a05056a 0x1 ...). RSCC_CONTROL_ACK
    stayed 0 after the wake request (rsc status0 was 0 before): look at it in step 16. 48 writes undone.
  - **0165:** step 15 now first does Linux a6xx_gmu_rpmh_init (RSCC program, hidden_tcs_cmd2 0x80000000 for the A650
    (0x80000021 is a740), PDC gpu_seq_start 0 / gpu_enable 0x80000001 at 0xb294520 / 0xb294500, then rpmh_stop =
    channel asleep) so that rpmh_start's ack can come. Step 16 hfi_ctrl_init. Step 17 HFI (Linux order): perf table
    (umi gpu-opp-table_v2: 305 MHz @ 64, 400 @ 128, 490 @ 192; GMU 200 MHz @ 48), A650 bw table (ddr 0x50000 /
    0x50004 / 0x5007c, cnoc 0x500a4, wait masks 1), core fw start, start, GX_BW_PERF_VOTE (sweetgpuspeed, default
    305 MHz), then oob GPU_SET (host2gmu bit 30, ack gmu2host bit 31) and the first 3D-core register reads. Once
    the 3D core is asked for, nothing is undone (HackiOS: collapsing CX under a powered GX hung a phone).
    **Boot `umi-0165-gpu17.img` (log `research/logs/umi-0165-gpu17.txt`): THE 3D CORE HAS POWER AND ANSWERS.**
    rpmh_init: rsc_status0 -> 0x1010006 (asleep) after rpmh_stop; PDC gpu_enable_pdc was 0x100 -> 0x80000001; then
    rpmh_start ack 0x3 (the missing piece in 0164). GMU runs, HFI queues up; GMU accepts perf table (votes gx 0
    0x400202 0x800203 0xc00305, gmu 0 0x400202), A650 bw table, core fw start, start, GX_BW_PERF_VOTE 305 MHz; oob
    GPU_SET granted: sptprac 0xc0 -> 0, gx_gdscr 0x222001 -> 0xf8222800; rbbm_status 1, rbbm_int_0_status 0,
    cp_rb_base 0. Left on (64 writes); phone kept running. Next: HackiOS steps 18-22 (SMMU context 0 for the
    core, ring + a650_sqe.fw, zap load via PAS, a6xx hw_init for the A650, CP start, leave secure mode, first
    commands).
  - **0166 (2026-10-26):** steps 18-21 (docs/GPU-HANDOFF.md; A650 values from Linux v6.12): 18 SMMU context 0 for
    the core (SCTLR + bit 8 HUPCF; ring 32K at 0x1000000, a650_sqe.fw minus 4 bytes read-only at 0x1100000, scratch
    at 0x1200000; stream 0 via SMR 0, stream 1 via SMR 2, mask 0x400), 19 pas_shutdown + init_image again,
    pas_mem_setup(13, 0x8681a000, 0x1000), a650_zap.b02 copied there, pas_auth_and_reset, 20 A650 hw_init + CP_SQE_CNTL
    + CP_ME_INIT, 21 CP_SET_SECURE_MODE 0 + CP_MEM_WRITE 0x600dc0de to scratch. The zap shader is no longer released
    at the end once the core has power. **Boot `umi-0166-gpu21.img` (log `research/logs/umi-0166-gpu21.txt`): steps
    1-17 as in 0165 (3D core powered, rbbm_status 1); STEP 18 STOPS: THE HYPERVISOR REFUSES SMR 0.** Context 0 writes
    went through without a fault (cbar 0x1f300, cba2r 1, tcr 0x803519, ttbr0 ours, tlbsync done, sctlr 0x1127), but
    smr0 written 0x84000000 (stream 0, mask 0x400) reads back 0. The GMU's smr1 0x84000005 (stream 5, mask 0x400 =
    exactly dt `<5 0x400>`) was taken, so the hypervisor seems to allow only the dt's own pairs: the GPU's is
    `<0 0x401>` (gfx3d_user) -> next: one SMR 0x84010000 (stream 0, mask 0x401, covers stream 1 too) instead of two.
    Steps 19-21 did not run. a650_sqe.fw on this phone is version 0x093 (Linux v6.12 wants >= 0x095 for security
    fixes; it is the vendor's own and should run). Phone kept running; the run left 64 recorded writes in place.
  - **0167 (2026-10-26):** the 3D core gets one SMR with exactly its dt pair, stream 0 / mask 0x401 (covers stream 1);
    the GMU keeps 5 / 0x400. A refused SMR now logs both smr and s2cr. (CI: three runs failed with no macos-14 runner
    free, the fourth built.) **Boot `umi-0167-gpu21.img` (log `research/logs/umi-0167-gpu21.txt`): 🎉 THE 3D CORE
    EXECUTES OUR COMMANDS AND WRITES OUR MEMORY (all 21 steps).** 18: smr0 0x84010000 and s2cr0 0 taken (so the
    hypervisor wants the dt's exact pair), cbar0 0x1f300, cb0 sctlr reads 0x127 (HUPCF bit 8 kept; bit 12 dropped, as
    for cb1), ttbr0 / tcr ours, sgfsr 0 (cb0 fsr reads 0x400, outside the fault bits; was 0x400 before too). 19:
    pas_shutdown 0, pas_init_image 0, pas_mem_setup(13, 0x8681a000, 0x1000) 0 (the memory read zeroes), 1676 bytes
    of a650_zap.b02 copied, pas_auth_and_reset 0: TrustZone authenticated and started the zap shader. 20: A650 hw_init
    taken (before: qsb_side 0x70620, uche_cache_ways 0x40000, pc_dbg_eco_cntl 0x180000, hang_int_cntl 0xfffffff, nc_mode
    0x2); cp_sqe_instr_base 0x1100000, cp_rb_base 0x1000000, cp_rb_cntl 0x800020c read back; CP_SQE_CNTL 1: status 1,
    no fault / interrupt / protection; CP_ME_INIT read up to 9, idle. 21: CP_SET_SECURE_MODE 0 read up to 11, idle;
    CP_MEM_WRITE read up to 15; scratch reads 0x600dc0de. a650_sqe.fw 0x093 works. Phone kept running (log goes on
    ~2500 lines). Next (step 22): a 2D-engine solid fill into a buffer shown on the panel.
  - **0168 (2026-10-26):** step 22 (values: Mesa 24.2 fd6_blitter.cc fd6_clear_surface / emit_setup / fd6_clear_texture
    flushes, freedreno_devices.py A650, a6xx.xml): the panel's boot framebuffer (0x9c000000, 1080x2340, rows 4320) is
    mapped at 0x10000000 in the core's context 0 (TLBIASID + sync), and the 2D engine fills red / green / blue bands
    into it. Rows of 4320 bytes are not a multiple of 64 (2D pitch): the engine is told 2160x1170 with rows of 8640
    (two panel rows each). RB_CCU_CNTL 0x18000000 (sysmem: colour cache at 3 CCUs x 64K), blit cntl 0x10f03080 (solid,
    FMT6_8_8_8_8_UNORM, R2D_UNORM8, mask 0xf), SP_2D_DST_FORMAT 0xf180, RB_2D_DST_INFO 0x430 (WXYZ = BGRA),
    RB_DBG_ECO_CNTL 0x04100000 around CP_BLIT(SCALE); CCU clean/invalidate before, CCU clean + CACHE_FLUSH_TS after.
    SweetFramebuffer.cpp: `sweet_fb_gpu_begin()` (cleans the boot framebuffer from the CPU caches, holds it on the
    panel: direct scanout pointed back at it, no frames presented, 60 s at most) / `sweet_fb_gpu_show(ms)` (hold
    sweetgpuhold ms, default 10000, once drawn) / `sweet_fb_gpu_pixel()`. **Boot `umi-0168-gpu22.img` (log
    `research/logs/umi-0168-gpu22.txt`): 🎉 A PICTURE DRAWN BY THE GPU IS ON THE PANEL** - user saw red / green / blue
    bands. Ring read up to 162, idle; read back rows 390 / 1170 / 1950 left, middle, right = 0xffff0000 / 0xff00ff00 /
    0xff0000ff exactly, first pixel red, last blue; then "the GPU's picture has been shown; frames again", iOS kept
    running. Event stamps: CCU colour flush and CACHE_FLUSH_TS wrote timestamps, the two CCU depth flushes wrote 0
    (nothing in the depth cache?). Next: a kernel GPU service for Mesa freedreno in user space (buffer objects in
    the core's SMMU context, submit = ring IB, fences), then CoreAnimation's GL renderer.
  - **0169 (2026-10-26):** step 23: memory objects (kmem_alloc pages mapped 4K at a time into context 0 from
    0x100000000, unmapped + TLBIASID/TLBSYNC on free), submission as CP_INDIRECT_BUFFER (0x3f) from the ring after CCU
    invalidates (Linux a6xx_submit), fence = CP_EVENT_WRITE CACHE_FLUSH_TS without TIMESTAMP bit to scratch+0x200,
    polled. Self-test: magenta/yellow/cyan fill + CP_MEM_WRITE of 4 words into a data object, from an IB.
    `docs/GPU-HANDOFF.md` updated (state after 0168, plan for the GPU service). CI `40384399954`. **Boot
    `umi-0169-gpu23.img` (log `research/logs/umi-0169-gpu23.txt`): STEP 22 FAILED ITS CHECK, STEP 23 DID NOT RUN.**
    Steps 1-21 as before; step 22's fill ran (ring read up to 162, idle) but the green band read back 0xff000000 at
    left/middle/right (red and blue right) -> "does not hold what the 2D engine was told to draw". Cause (inferred):
    this time the GPU steps ran before iOS's first frame (`SWEET FB: display on` ~700 lines later), so the kernel
    text console still drew into the boot framebuffer (it is muted only from the first swap): its dirty CPU cache
    lines were written back over the GPU's pixels (sweet_fb_gpu_begin's cache clean ran before them). In 0168 the
    first swap came first. The user reported seeing red/green/blue then magenta/yellow/cyan; the log has no step 23
    line at all, so the second set cannot have come from this kernel - unexplained. Fix for 0170: sweet_fb_gpu_begin
    mutes the console for the hold (restored after) and does its work inside the framebuffer's workloop gate (no
    present() copying into the framebuffer at the same time).
  - **0170 (2026-10-26): the 0169 fix, `iokit/Kernel/arm/SweetFramebuffer.cpp`:** `sweet_fb_gpu_begin()` now sets the
    hold and cleans the framebuffer from the CPU cache inside the framebuffer workloop's gate (`fWorkLoop->runAction`,
    so no present() copies at the same time), mutes the kernel text console for the hold (`sweet_console_muted`, old
    value put back when the hold ends in `vsyncFired`, also when it ends display-off), and the power-off fade (with
    its copy-over of the last frame) is skipped while held. Hold-related GPU (printf) and FB (IOLog) lines now carry
    `mach_absolute_time()` stamps so their order can be read from the persistent log (timebase 19.2 MHz).
    CI `40388809568`, boot `shim/out/umi-0170-gpu23.img` (boot line as 0169, `sweetgpu=23`), log
    `research/logs/umi-0170-gpu23.txt`. **STEP 23 RAN AND PASSED: ALL 23 STEPS GREEN.** Step 22's bands exact again
    (rows 390/1170/1950 left/middle/right 0xffff0000 / 0xff00ff00 / 0xff0000ff; hold begins t 1019682728, readbacks
    t 1019703494..1019704360), so the 0169 failure was indeed a CPU writer (console or present) - stopped by the gate
    + mute. Step 23: commands object at the core's 0x100000000 (0x10000 bytes, ours 0x17e238000), data at 0x100020000
    (ours 0x17e418000) - above 4 GB, mapped 4K at a time; 149 words submitted as fence 1 (fence word was 0), fence
    word 0x1 SIGNALLED (ring read up to 175, status 0x1, no fault/interrupt/protection); the data object reads
    0x0b0b0001 0x0b0b0002 0x0b0b0003 0x0b0b0004 as written; magenta/yellow/cyan bands exact (0xffff00ff / 0xffffff00 /
    0xff00ffff); objects freed, TLB sync done. One interplay to remember: backboardd turned the display off ~6 s into
    step 22's 10 s hold (t 1132608310), so step 23's `sweet_fb_gpu_begin` was refused ("display off: not held") and it
    drew anyway - the new fade-skip kept the panel on the GPU's picture through the "off", so step 23's colours were
    on the panel for their 10 s all the same (hold end t 1338604283, "frames again"). iOS kept running. Next
    (docs/GPU-HANDOFF.md): the kernel GPU service for user space - an IOUserClient mirroring Linux's msm DRM uAPI
    (GET_PARAM, GEM_NEW / GEM_INFO / GEM_CLOSE, GEM_SUBMIT, WAIT_FENCE) for Mesa freedreno, with the A650 CP protect
    table (Linux v6.12 a6xx_catalog.c `a650_protect`) set up before any user-space client can submit; how test
    binaries reach the phone's HFS root (new root image the user flashes, or a kernel-side copy at boot) to be
    decided before the user-space side.
  - **0171 (2026-10-26): A650 CP protect table in step 20**, applied where Linux's a6xx_hw_init calls
    a6xx_set_cp_protect (a6xx_gpu.c), before the command processor starts - the precondition for an untrusted
    user-space client. Values: Linux v6.12 a6xx_catalog.c a650_protect_regs (39 entries; NORDWR/RDONLY encodings
    a6xx_gpu.h: NORDWR = 0x80000000 | len << 18 | reg), CP_PROTECT_CNTL reg 0x84f bits 0 (ACCESS_PROT_EN) / 1
    (ACCESS_FAULT_ON_VIOL_EN) / 3 (LAST_SPAN_INF_RANGE) = 0xb and CP_PROTECT 0x850..0x87f (a6xx.xml, v6.12;
    Mesa 24.2 agrees; the xml's "length 32" for the array is stale - Linux writes up to index count_max-1 = 47).
    **First boot (`umi-0171-gpu23.img`, log overwritten by the second): STEP 22 STOPPED BY OUR OWN PROTECTION**
    ("does not get through ... protection 0x608e07" - RB_CCU_CNTL 0x8e07, the first register step 22's commands
    write): the 39 entries had gone into CP_PROTECT(0..38) and the zero-filled rest left register 47 = 0, so
    LAST_SPAN_INF_RANGE extended the empty span 0 over the whole register space and blocked every command
    register write. Lesson: Linux's DECLARE_ADRENO_PROTECT(a650_protect, 48) is count_max = 48 against
    ARRAY_SIZE = 39 - a6xx_set_cp_protect writes entries 0..count-2 into CP_PROTECT(0..37) and the last
    (infinite-range) entry into CP_PROTECT(47), leaving 38..46 untouched. Fixed to exactly that.
    **Second boot (CI `40399500064`, log `research/logs/umi-0171-gpu23.txt`): ALL 23 STEPS PASS WITH REGISTER
    PROTECTION ON** - cp_protect_cntl 0xb, first 0x13fc0000, untouched (index 40) 0, last (47) 0x8001f8c0 read
    back right; step 22's bands exact, step 23's fence 1 signalled, data words right, magenta/yellow/cyan
    exact, objects freed. Test binaries to the phone (user's choice, ios-flame): a kernel file server over USB
    Ethernet, ios-flame patch 0091 (`bsd/dev/sweet_files.c`, TCP PUT/GET/MKDIR/LINK/RM/CHMOD on the running root,
    started from sweet_usb.c; Mac side tools/flame-files.py) - umi already has sweetusb=2. Next: port that file
    server, then the SweetAdreno IOUserClient (msm DRM uAPI: GET_PARAM, GEM_NEW/INFO/CLOSE, GEM_SUBMIT,
    WAIT_FENCE) for Mesa freedreno.
  - **0172 (2026-10-26): kernel file server over USB Ethernet, ported from ios-flame patch 0091** (`bsd/dev/sweet_files.c`,
    TCP 2223 on ue0 192.168.7.2; host side `tools/umi-files.py`, Mac 192.168.7.1 via `tools/umi-usbnet.sh`): PUT / GET /
    MKDIR / LINK / RM / CHMOD on the running root, one request per connection, started from `sweet_usb_gadget_start`
    (boot-arg `sweetfiles=0` off), with `sweet_vfs_mkdir/symlink/unlink` wrappers in `bsd/vfs/vfs_syscalls.c`. umi has no
    USB command channel, so unlike flame every request that changes the file system is followed by `sync()` (HFS+ journal
    flushed), and the reply goes out first. **Boot `shim/out/umi-0172-gpu23.img` (CI `40405804121`, log
    `research/logs/umi-0172-gpu23.txt`): the server works and pushes survive a reset** - 1 MB random-data PUT, GET back
    byte-exact; after a reboot into the same image the file was still there byte-exact (the sync path works);
    mkdir/put/chmod/rm all OK (RM of a directory is EPERM: no RMDIR in the protocol). The GPU self-test stayed green in
    the same boot (step 22 picture, step 23 IB + fence, "done"). Test binaries for the GPU user client now reach the
    phone without reflashing the root. Note: the 192.168.7.1 alias on the Mac's en8 survives phone re-enumerations, so
    only the first umi-usbnet.sh needs the sudo password; `adb kill-server; adb start-server` fixes TWRP not showing in
    adb. Next: the SweetAdreno IOUserClient (msm DRM uAPI) on top of steps 18-23 + the protect table.
  - **0173 (2026-10-26, evening): SweetAdreno - the GPU as an IOKit service for user space** (`iokit/Kernel/arm/
    SweetAdreno.cpp` + a C API exported from `bsd/dev/sweet_adreno.c`, one mutex over ring/table/VA): selectors in the
    shape of Linux's msm DRM uAPI - GET_PARAM (msm_drm.h MSM_PARAM ids; chip id 0x06050002, gmem 0x120000, VA start
    0x100000000 / size 0x8000000000-that, max freq 305 MHz, highest bank bit 16, UBWC swizzle 6, macrotile 0),
    GEM_NEW / GEM_INFO / GEM_CLOSE (step 23's objects: wired kmem pages mapped 4K at a time into context 0, unmapped
    + TLBIASID on close; clientMemoryForType maps them into the task, so IOConnectMapMemory(type=handle) reaches
    them), GEM_SUBMIT (step 23's CP_INDIRECT_BUFFER with the CACHE_FLUSH_TS fence, ring-room checked), WAIT_FENCE
    (polled). Opens are refused until the sweetgpu bring-up has the core running; the 0171 protect table keeps client
    commands off the registers; this XNU has no clientHasEntitlement, so opens are logged by process name. Published
    from AppleCLCD::start as IOServiceMatching("SweetAdreno") (`sweetadreno=0` off). CI `40408751046`, boot image
    `shim/out/umi-0173-gpu23.img` (sweetgpu=23) built and `fastboot boot`ed - **the boot itself was NOT verified
    tonight (stopping early): the service log line, the self-test and the user-space test are all still to check.**
    User space prepared but not run: `phone/sweet-gpu-test.c` (iPhoneOS SDK + ldid, `phone/build-gpu-test.sh`):
    opens SweetAdreno with a 4-minute retry (launchd starts before the GPU steps finish), GET_PARAMs, two GEM_NEWs,
    builds a CP_MEM_WRITE IB in the mapped command object, GEM_SUBMITs, WAIT_FENCEs, reads the data object back;
    writes /private/var/sweet/gpu-test.log; `phone/com.sweet.gputest.plist` + `build-gpu-test.sh install` push binary
    and LaunchDaemon over the file server. **Next session: on the 0173 boot (or a fresh one) `bash
    phone/build-gpu-test.sh install`, reboot the phone, then GET /private/var/sweet/gpu-test.log (expect PASS, the
    four 0x5eed000n words) and pull the kernel log (SWEET ADRENO published + opens + steps 21-23 green).**
  - **0174 (2026-10-27, evening): USER SPACE DRAWS WITH THE GPU.** Three bugs stood between the 0173 service and a passing
    user-space test, all found live through the file server (`tools/umi-files.py`, no TWRP needed):
    1. The test binary was built against the iPhoneOS 27.1 SDK with its default min version - `minos 27.0` - which iOS
       16.7's dyld refuses; `-miphoneos-version-min=16.0` fixes it (phone/build-gpu-test.sh).
    2. **iOS launchd does NOT scan /System/Library/LaunchDaemons: every job comes from the launchd cache
       /System/Library/xpc/launchd.plist** (binary plist, 531 LaunchDaemons entries with each job's parsed content;
       launchd_cache_loader sends it to launchd, and `launchd_unsecure_cache=1` skips only its signature check). A pushed
       plist is never read; the job must be added to the cache (plistlib: `d['LaunchDaemons'][path] = {Label, Program,
       RunAtLoad, ...}`, FMT_BINARY back), as done for com.sweet.gputest (with StandardOut/StandardErrorPath).
    3. `IOServiceOpen` on SweetAdreno returned kIOReturnUnsupported (0xe00002c7) on every retry: the IOUserClientClass
       property was set in `SweetAdreno::start()`, but nothing matches the service, so start() never runs -
       `newUserClient` needs the property to allocate the client class. Patch 0174 sets it at publish time, like the
       other SWEET stand-ins (IONetworkStack, IOAcceleratorES).
    Note: user-client opens do NOT call handleOpen (no `service->open()` in IOUserClient.cpp), so the "opens refused"
    wording is really "operations refused": every C API call checks `sweet_adreno_service_ready()` (steps 18 + 20 done).
    CI `40587489455` (one queued run cancelled with no runner), boot `shim/out/umi-0174-gpu23.img`, kernel log
    `research/logs/umi-0174-gputest.txt` (service published at line 99, steps 22+23 green, exec sweet-gpu-test at 1898).
    **The test (`phone/sweet-gpu-test.c`, launchd daemon com.sweet.gputest) PASSES from the running phone**:
    /private/var/sweet/gpu-test.log - SweetAdreno opened (pid 78), GET_PARAM chip id 0x6050002 / gmem 0x120000 / VA start
    0x100000000, GEM_NEW two objects (commands at the core's 0x100034000, data at 0x100048000), the IB built in the
    task-mapped memory (IOConnectMapMemory), GEM_SUBMIT -> fence 2, WAIT_FENCE signalled, the data object reads
    0x5eed0001 0x5eed0002 0x5eed0003 0x5eed0004 "as the core was told to write (USER SPACE DRAWS WITH THE GPU)", PASS.
    Caveat noted: the sweetgpu self-test and user clients share the kernel ring and fence word (the mutex covers kernel
    state, and the self-test is over long before real clients); fences are a single 32-bit sequence.
    **Next: Mesa freedreno with a libdrm-msm stand-in on the SweetAdreno selectors** (kernel hands out GPU addresses,
    objects map via IOConnectMapMemory(handle), submits are one IB + fence, WAIT_FENCE polls); after that CoreAnimation's
    GL renderer. The test daemon stays installed (re-runs each boot; remove the launchd.plist cache entry to stop it).
  - **0175 (2026-10-27, night): the NativeAdreno ABI on SweetAdreno + LOCAL KERNEL BUILDS - both proven.**
    Patch 0175 adds the ABI Turnip's darwin backend speaks (`iokit/Kernel/arm/SweetGPUABI.h`, UniXNU NativeAdrenoABI v1,
    MIT, served exactly as ios-flame serves it): v2 opens (type 0x4147 'AG' or 2) get a 4 GB GPU window of their own
    (from 0x200000000; `sweet_adreno_window_alloc`), client-chosen addresses mapped 4K at a time
    (`sweet_adreno_map_at`/`unmap_at`), multi-IB submits with one CACHE_FLUSH_TS fence and ring-room checks
    (`sweet_adreno_submit_v2`), ns fence waits, the CP always-on counter (0x0980/1) as GetTimestamp, and a fault
    counter for GetStatus; BoAlloc is an IOBufferMemoryDescriptor (kernel+user), BoCpuMap the clientMemoryForType
    token (WC), Submit cleans every BO overlapping the submitted buffers. The `sweetmtl` boot-arg points the
    IOAcceleratorES at metal2vulkan's SweetMetal2.bundle (MetalPluginName SweetMetal2, class SweetMTL2Device).
    A650 DeviceInfo: chip 0x06050002, gmem 0x120000 at 0x100000 (flame's A640 value - to verify against Mesa's
    fd_dev_info), uche trap 0x1fffffffff000 as step 20 programs it, hbb 16, UBWC 4 swizzle 6.
    **CI was cancelled twice by missing runners, so the kernel was BUILT LOCALLY** (`tools/build-kernel-local.sh`,
    the recipe in its header: the CI buildtree bt/ + apple-oss dtrace-397 CTF tools + libdispatch-1415.140.2
    libfirehose_kernel (kernel-variant firehose headers; KERNEL_PRIVATE define) + the toolchain's
    libclang_rt.cc_kext.a + the KDK 13.5 unpacked from the dortania mirror - no Xcode 15 needed: all generated
    files come pre-generated from the CI tree, touched so nothing (iig, mig, yacc) regenerates under Xcode 27;
    ~12 min, incremental). Boot `shim/out/umi-0175-local-gpu23.img` (fastboot), the locally built kernel passes
    the self-test AND **the daemon PASSES BOTH APIs** (pushed with the file server): v1 as in 0174, and v2 -
    open 'AG', Query (abi 1, 39-bit, 256 MB BOs), DeviceInfo, two BoAllocs, BoMap at the client's own
    0x200100000/0x200200000, one-IB Submit -> fence 3 signalled, data readback exact, GetTimestamp 138200011:
    "THE TURNIP ABI WORKS" (v1 PASS, v2 PASS). **Next: build Turnip (Mesa 85fda3b3 + UniXNU patches/mesa,
    -Dfreedreno-kmds=darwin, tu_knl_darwin.cc) and metal2vulkan (steelbrain @720ef1ce + flame's
    phone/metal2 bridge patches; Rust 1.98, aarch64-apple-ios) into SweetMetal2.bundle, push it over the file
    server, boot sweetmtl=2.** Tools needed locally: rustup + bison 3 (brew); flame's build scripts are the
    recipe (xnu-work/refs/flame-*).
  - **0175b (2026-10-28, night): METAL-ON-TURPIP BUILT AND ONE STEP FROM RENDERING.** All three components built locally
    and installed, with `sweetmtl=2` in the boot line (`shim/out/umi-0175-metal.img`, same locally built kernel):
    1. **Turnip**: Mesa 85fda3b36405 (gitlab.freedesktop.org, blobless clone) + UniXNU patches/mesa (all 9, fetched to
       xnu-work/refs/unixnu-mesa; turnip-darwin-kmd.patch = tu_knl_darwin.cc) + meson cross (arm64-apple-ios16.0,
       xnu-work/work/turnip/ios16.cross; needs glslangValidator (brew glslang), bison 3 (brew), python3.13 venv
       (mako/pyyaml/packaging/meson)) -> libvulkan_freedreno.dylib (17.9 MB, ~2 min build; vkGetInstanceProcAddr
       exported; only pthread_mutexattr weak refs, present on iOS 16).
    2. **metal2vulkan bridge**: steelbrain/metal2vulkan @720ef1ce + flame's 8 bridge patches (0001-0006, 0100/0101,
       from phone/metal2/bridge/patches) + flame's NativeMetalBridge.rs/.h/NativeMetalObjects.rs; Rust 1.98
       (brew rustup + `rustup target add aarch64-apple-ios --toolchain 1.98.0`), llvm-as .ll fixtures
       (metal2vulkan-validation) -> libnative_metal_bridge.a (cargo, 71 s).
    3. **SweetMetal2.bundle**: flame's SweetMetal2.mm + NativeBridgeMetalFrontend.mm (-x objective-c++ -bundle,
       -fobjc-arc, links the bridge + frameworks Foundation/Metal/IOSurface/IOKit/CoreFoundation; the sources expect
       a bridge/ subdir with the headers) + Info.plist (NSPrincipalClass SweetMTL2Device) + the Turnip dylib +
       ad-hoc codesign (dylib then bundle; _CodeSignature/CodeResources). Exports _OBJV_CLASS_$_SweetMTL2Device...
       (see log) and nmb_* bridge functions. **Installed on the phone** at /System/Library/Extensions/SweetMetal2.bundle
       (4 files, pushed one by one with the file server).
    **It WORKS up to the device: backboardd, SpringBoard, chronod, PosterBoard all load the plugin and try to create
    a Metal device** (log /var/local/mtl2.log: "MTL2[57 backboardd]..." - the plugin writes there when the file exists,
    mode 666; /var/local/mtl2-clients lists which processes get a device, backboardd always, "*" = all, "-NAME" =
    never; /var/local/m2v-cache 777 for the shader cache). Two failures found and fixed:
    1. shader cache PermissionDenied -> create /var/local (777) + m2v-cache (777) FIRST (the plugin mkdirs only the
       last component).
    2. `Vulkan(VkResultCode(-3))` on device creation: **Turnip's default opens IOServiceMatching("IOAcceleratorES")**
       (our empty "sgx" stand-in, no user client) - not SweetAdreno. **Fix installed but NOT YET BOOTED**:
       /var/local/mtl2-env with `TU_DARWIN_SERVICE=SweetAdreno` (SweetMetal2.mm injects the file's KEY=VALUE lines
       into the plugin process's environment before Turnip loads; tu_knl_darwin then opens SweetAdreno type 0x4147,
       tunnels {'NTNL', method, payload} through any selector and probes with method 0xffffffff - our v2 client
       handles exactly that). **Next session: reboot umi-0175-metal.img (run tools/umi-usbnet.sh after boot!), read
       /var/local/mtl2.log; expect backboardd/SpringBoard to get real devices and render.** The proper kernel fix
       (patch 0176, flame's architecture): make SweetAdreno itself subclass IOAcceleratorES with the Metal plugin
       properties and drop the empty sgx accelerator when sweetmtl is on - one service, no env file needed.
       Caveat logged for later: gmem_base 0x100000 (flame's A640 value) still to verify against Mesa's a6xx gmem base.
  - **0176 (2026-10-28, midday): BACKBOARDD HAS A METAL DEVICE.** Four kernel fixes, each found live on the phone
    (patch 0176, all in `sweet_adreno.c`/`SweetAdreno.cpp`/`pmap.c`):
    1. **GPU windows are per-TASK now, not per-connection** (SA_WINDOW_MAX 32): Turnip learns its VA range once
       (GetDeviceInfo), closes the connection and reopens for the device - a new connection of the same process must
       return the SAME window, or BoMap refuses with kIOReturnBadArgument ("iova outside window" in the kernel log:
       BoMap(0x200000000) refused because that connection's window was 0x300000000). This was THE v2/Turnip blocker.
    2. **pmap_sync_page_attributes_phys: ptoa, not pp << PAGE_SHIFT** - ppnum_t is 32 bits, so high pages lost bit 32
       and phystokv_range PANICKED on the truncated low PA (0x733c0000 etc.) the first time a BO page's cache
       attributes changed (Metal maps BOs write-combined). Same fix as flame's patch 0115 - we should have taken it
       with their other patches.
    3. sweet_adreno.c's phys-mode cache flushes (sa_to_memory, the page-table flushes, the fence word, the zap
       header) are VA-based: the physical form only knows the kernel image's pages and RAM from 4 GB up on this
       highmem kernel (ADT: RAM = 0x100000000..0x1fcc00000 ONLY; mkadt HIGH_PHYS_BASE/HIGH_MEM_SIZE).
    4. BoMap logs its request + which check refused - the instrument that found (1).
    **On the phone (`shim/out/umi-0176-metal.img`, sweetgpu=23 sweetmtl=2): `MTL2[57 backboardd]: device Turnip
    Adreno (TM) 650 in 1805 ms` - backboardd created a real Metal device through Metal -> SweetMetal2.bundle ->
    metal2vulkan -> Turnip -> SweetAdreno v2 -> the A650, and maps BOs in its window (69 seen).** Harmless fallbacks:
    "no device answer: isLargeMRTSupported ..." (feature queries) and "no-copy buffer refused: HostMemory
    NotRepresentable" (host no-copy buffers; BoImport is implemented but the runtime wants more).
    **Still open (next session):** (a) the daemon's v2 test REGRESSED this boot - submit ok, `WaitFence(8) signalled`,
    but the CP_MEM_WRITE data reads 0 0 0 0 (v1 PASSes the same flow; suspect the v2 readback path or a cache
    attribute of the WC-mapped IOBMD pages after fix (2)/(3) - check whether the GPU write landed at the iova
    through map_at or in the wrong pages); (b) **SpringBoard's device attempt wedges** (two connections into its
    0x500000000 window, 5 BoMaps, then nothing - its attempt runs >10 min; the panel shows only the kernel console
    because no frame swap ever happens, touch works); (c) the xpcproxy/bluetoothd exec loop looks busier than the
    usual background one when Metal clients are stuck - check for jetsam/memory pressure with every daemon in
    mtl2-clients "*" creating a full Vulkan stack (~trim "*" to backboardd+SpringBoard first). Debug aids in place:
    /var/local/mtl2.log (plugin), /var/local/turnip-<proc>.log (Mesa, via /var/local/mtl2-tu-debug "flushall"),
    kernel "SWEET ADRENO: BoMap..." lines in the live log, the retry loop in SweetMetal2.mm (60x5 s), the tunnel
    test in the daemon, vktest installed as com.sweet.vktest.
  - **0177 (2026-10-28, afternoon): THE METAL HANG IS CP_OPCODE_ERROR; UI STILL NEVER REACHES THE PANEL.** Patch
    0177 (kernel d41b836, CI `40694264105`), four parts:
    1. **The present path waits for the GPU and drops stale CPU lines of GPU-written memory**: present() and
       directPresent() call `sweet_adreno_finish()` (the latest fence, 500 ms cap) first; present's copy path
       clean+invalidates the source before memcpy and cleans the written panel range after; directPresent
       flushes (was: clean) the scanned-out range; both SweetSurface creation paths and SweetAdreno's BoAlloc
       flush after their bzero (BoAlloc's missing clean is why 0176's v2 test read back 0 0 0 0 - fixed, v2 PASS
       again).
    2. **SA_TABLES_MAX 64 -> 1024** (every 2 MB of dense window VA costs one L3 table; SpringBoard's 8 MB BoMaps
       hit NoResources at 64) and a fence wait "forever" fails after **120 s** instead of hanging the caller.
    3. **The stuck-fence dump**: after 2 s of failed waits on one fence (once per fence, IOLog so it reaches the
       live log): CP_RB_RPTR vs written WPTR, the fence word, RBBM status/interrupts (a6xx.xml 0x210),
       CP_HW_FAULT / CP_INTERRUPT_STATUS / CP_PROTECT_STATUS / CP_STATUS_1, the SQE's instruction address
       (CP_SQE_INSTR_BASE 0x0830, 64-bit), the SMMU's FSR/FAR/FSYNR0, the **last 8 submissions** (fence + every
       IB's iova and dwords), and the IB words the SQE is stopped on - read through context 0's PTEs from the
       kernel's own map (`sa_gpu_page`: PTE -> PA -> guarded gPhysBase/gVirtBase translation; the low RAM bank is
       outside the kernel's physmap on this highmem kernel, and `phystokv` PANICS on it, so the guard is not
       optional). Submits and BoCpuMaps get log budgets of their own (a shared budget never reached Submit).
    4. **The finding** (first 0177 boot, ~15 min in): fence 950 dead-stops; dump: *ring fully read (1674 of
       1674), fence word stuck at 949, RBBM 0x800005 = GPU_BUSY_IGN_AHB|CP_BUSY|CP_AHB_BUSY, CP interrupt
       status 0x1 = **CP_OPCODE_ERROR** (a6xx.xml A6XX_CP_INT), CP fault 0, protection 0, no SMMU fault bits* -
       the command processor hit a bad opcode in **backboardd's** IBs (the stuck fences' BoMaps are all in
       backboardd's 0x200000000 window; fences 932-950 were brief 0-ns poll timeouts right before, i.e. the
       workload was already slow, then 950 never came back). NOT a lost fence write (the core would be idle
       then). The hang is a command-stream bug somewhere around Turnip's ~950th submit - next: catch it with
       part 3's SQE address + IB words (that boot predates them; the second 0177 boot, with them, ran 30+ min
       and 1300+ fences with NO hang - it is intermittent, roughly once per 15 min of Metal workload).
    **Display status both 0177 boots: the panel never shows the UI** - it stays on the garbled console frame
    (user: "same artifacts except this time we don't even see a part of iOS ui"; the 0175 boot did show UI with
    artifacts, so the present path got SLOWER to reach: suspect `sweet_adreno_finish()` in present() making
    backboardd's frame loop miss, or the UI never presenting since). backboardd still loops "no-copy buffer
    refused" and logs "vertexFunction/fragmentFunction is not a MTLFunction" (118 in one boot) - its pipelines
    fail to build, likely the real reason nothing is presented. AegirPoster/CollectionsPoster/SiriTTS
    crash-loop (MTL2 answers "not listed" for them). Log: `research/logs/umi-0176-metal-hang-live.txt` (the
    0176 boot's fence-375 storm), `shim/out/umi-0177-metal.img` (boot line: umi-0176-metal's +
    build via `tools/build-kernel-local.sh` + `tools/umi-boot-image.sh KERNEL OUT <extras>` which fails at the
    shim's missing cross gcc, then swap `shim/out/payload-umi.bin` into the boot image's ramdisk: sequential
    pages, ramdisk_size at header offset 16). **Next: (a) reproduce the opcode hang with the SQE-address dump
    and read the offending opcode from the IB; (b) find why backboardd's pipelines fail (MTLFunction errors) and
    whether present is called at all - present()/directPresent() need count+path logging with their own budget;
    (c) then the artifact itself (faint vertical character columns = the console frame garbled, Image #6).**
  - **0178 (2026-10-28, evening): THE GLITCH WAS STALE MEMORY - AND THE PANEL STILL NEVER PICKS OUR FRAMES UP.**
    Patch 0178 (kernel 0abb880; all found with the new instruments):
    1. **The instruments** (SweetFramebuffer/SweetSurface): present() counts every frame swap and logs first
       8 + every 1024th + any gap > 1 s; directPresent logs each failure reason (layer count / missing surface /
       shape / address) and on success samples the scanned pixels (left/middle/right of nine rows every 128th
       present; the first two also walk 16 points across the whole allocation and print the panel geometry);
       `scanDump()` prints every SSPP's fetch address + stride and the CTL states; full-screen surface creations
       log without the 64-line budget. SweetAdreno: the stuck-fence dump reads the offending opcode Linux's
       way (a6xx_cp_hw_err_irq: CP_SQE_STAT_ADDR = 1 -> CP_SQE_STAT_DATA "possible opcode"; CP_SQE_INSTR_BASE
       turned out to be the SQE MICROCODE base we set at init, not the faulting address - the earlier dump read
       the firmware, useless), keeps the last 8 submissions and prints the newest IBs' first words.
    2. **The composited framebuffer was uniformly black (ff000000) or transparent**: CoreAnimation's own
       pipeline/function journal (`/var/local/m2v-cache/<client>/pipelines.log`, the bridge's S/R/F records)
       shows every CA pipeline and draw ok=1 - backboardd's compositor works, `com.apple.coreanimation.draw.*`
       labels, ~1000 draws per boot. The GPU wrote... a black/empty scene.
    3. **THE CAUSE: imports were never cache-cleaned.** BoImport passed kmap = NULL to v2NewSlot and the
       submit-path clean skips BOs without a kernel view, so the CPU's writes to an imported IOSurface (the
       decoded image, whatever another task drew) stayed dirty in the CPU's cache while the GPU sampled stale
       DRAM through the uncached window mapping. Fix: BoImport creates `md->map()` like BoAlloc, and BoMap
       cleans an import's pages through that view when they become GPU-visible. After it the scanned rows carry
       real, varied image data (3e2abf7f 7ef96961... - photo-like values, was: all ff000000).
    4. **But the panel still shows the boot console pattern (user: "identical to before")**: the DPU registers
       hold our fetch (scanDump: VIG0 src 0x9ca36050 stride 4608, CTL0 flush 0x20001) and the memory there has
       content - yet the command-mode panel's GRAM never picks it up. Suspect the DPU fetch/push stopped latching
       around the display off/on cycle while the GPU hold ran (every boot since 0176: hold until ~268 s, power
       off ~263 s, on ~272 s, presents from ~272 s; the 0092-era direct scanout worked at boot time with no hold
       and no power cycle, "user: looked normal, worked well" - and 0175's UI-with-artifacts came from the COPY
       path memcpy'ing into the boot framebuffer, which the panel does show). **Next: (a) power-cycle test -
       does the panel visibly fade at off, and what returns at on; (b) why CTL_FLUSH does not fetch: compare the
       0092 conditions (scanFrom before any off/hold), consider a CTL_START/KICKOFF trigger or re-arming
       autorefresh at display-on; (c) fallback test: `sweetfb_direct=0` to force the copy path (presents then
       memcpy into the boot FB, which the panel demonstrably displays) - if the UI shows up there, the bug is
       purely the direct-fetch latch and the copy path is the workaround; (d) the opcode hang (fence 78 this
       boot, CP_OPCODE_ERROR, opcode readout instrumented, intermittent ~1 per boot).** Logs:
       `research/logs/umi-0178b-hang-live.txt`, image `shim/out/umi-0181.img` (the fix), umi-0179/0180 (the
       pixel-sampling iterations).
  - **0179/0180 (2026-10-28, later evening): stride sweep and wider COPY diagnostics.**
    4500-byte stride: user reports same touch-responsive noise. 4096: denser noise, no UI.
    5120: photo shows static boot console; likely COPY's allocation bounds check rejects the
    enlarged span, not proof of a GPU freeze. No tested stride produced UI. Actual boot-header
    command lines verified (`sweetfb_direct=0`, corresponding source stride, sweetgpu=23,
    sweetmtl=2). Photo analysis: broad dark bands and bright low-saturation noise; cause unproven.
    Source inspection preserves IOSurfaceGetBytesPerRow through bridge/IoSurfacePlane, and the
    runtime's explicit linear host-image path checks Vulkan's returned pitch. Active path still
    needs runtime evidence. Retrieved 5120 Metal/Turnip/backboardd pipeline logs to /tmp;
    journal totals accumulate across boots (2106 R and 1503 S records ok=1), not a per-boot count.
    Kernel **761390e / 0179** commits the existing submit-time skip of imported BO cache cleaning
    (clean once at BoMap). **29b1da4 / 0180** commits the existing stride override plus new bounded
    `sweetfb_dump=1`: COPY geometry/rejection logs, two 64x32 pixel regions and row profiles,
    after sync/cache maintenance, three captures from 400 s uptime at least 30 s apart.
    Per-file compilation passed; full local build passed (/tmp/umi-0180-build.log). Image
    `shim/out/umi-0186-copydump.img` uses 0184's ADT/boot line, normal stride, sweetfb_dump=1;
    SHA256 0d0e9ac6914051450bba1ab81634933f826e4ae6d94f31606e8ff6d491a1a952.
    Ramdisk page count unchanged, DTB matches check-0176m/dtb. RAM boot succeeded; pixel capture
    pending in /tmp/umi-0186-live.log (Python UDP listener; user must configure USB Ethernet).
    Patch exports prepared; CI and device diagnostic results pending. Scratchpad recreated at
    $HOME/ios-sweet-port/umi-gpu-session.md.
  - **0181 (2026-10-28): 0186 hit a kernel panic while the GPU fence was stuck.**
    User reports touch-responsive artifacts, then panic. Live log: fence 2511/2512 timeouts;
    last present 1061 at t=6728861225 (~350 s), before the 400 s pixel-dump trigger. No copydump
    or hang header was received. Photo: Kernel data abort, PC fffffe000748482c
    (FlushPoC_DcacheRegion+0x1c), LR fffffe0007483c54 (flush_dcache+0xa4),
    FAR fffffe002c868000, ESR 96000146; 4 KB flush with gPhysBase/gVirtBase registers present.
    Old sa_gpu_page manually formed pa-gPhysBase+gVirtBase, ignoring XNU's ptov remappings:
    unsafe diagnostic. User agreed to TWRP; read-only log pull succeeded (ring total 753763,
    flush 124), but its last flush predates the fault too. Logs research/logs/umi-0186-panic*.txt.
    Fix **6675b52 / 0181**: read-only GPU page-table walk under service mutex, valid leaf and
    managed-PA checks, phystokv plus kernel-map verification, copy IB head at its actual page
    offset. Unavailable memory is skipped. COPY dumps now default to 180 s (or sweetfb_dump=N
    seconds for N>1), so pixel evidence can precede the hang. This is a diagnostic fix, not a
    confirmed GPU-hang fix. Both files cross-compiled and full local build passed.
    Image shim/out/umi-0187-safe-copydump.img, SHA256
    04ec637a25c5f9de3ec8d67426617bf3241d5d81fd585f4b47e9b60f2ee1adfd,
    unchanged payload page count and verified DTB, RAM-booted; user brought USB networking up.
    Pending capture: /tmp/umi-0187-live.log. Decoder tools/umi-fb-copydump.py renders raw BGRA
    regions and alpha separately, reports missing pixels and row profiles. CI 40754611687 for
    0179/0180 (ios-sweet 4e63ae2) is still queued; local builds remain canonical.
  - **0182/0183 (2026-10-28, night): THE PANEL SHOWS COMPLETELY CORRECT UI SOMETIMES - the noise is a
    PRESENT-VS-RENDER RACE, not broken output.** Kernel 0182 (8a31d99) proved the frame in memory is the
    problem, kernel 0183 (c7a597c) tested the wait; the user's photo settles it: the lock screen flashed a
    **perfect frame ("What's New in Photos" welcome card, clean text, blue Continue button, ~97% correct),
    alternating ~1 s good / 1 s glitchy** on the 0182 boot.
    - **0182's instruments (all verified live):** `sweet_adreno_finish` reports whether the newest fence
      signalled (present logs it); a per-present swap-rect log (CA presents carry FULL 1125x2436 rects);
      the copydump's regions moved to the surface's own fixed points (top-left, centre, clock band) so any
      present dumps; and the new **idledump** samples the pending frame's surface every 30 s away from
      present. Result: top-left and clock band ALL-ZERO (the clear works), centre WHITE NOISE (coherence
      ~75/255 both axes), at present time AND idle time - the frame the kernel copies is garbage in the
      middle, and `finish ok` does not change that.
    - **0183 (sweetfb_finwait=N ms boot-arg, default 500; boot with 10000):** waiting 10 s for the newest
      fence before the copy did NOT fix the screen ("not even alternating now, same glitchy ui") - the
      fence the kernel waits is not this frame's fence. The kernel cannot fix this alone: CA's swap record
      arrives while the drawable's composite is still running (or the surface is already being reused for
      the next frame) - **the sync has to come from the presentation path (user space): the swap must be
      ordered after the drawable's command buffer completes.** The bridge does not implement
      drawables/presentation (NativeBridgeMetalFrontend.mm line 8); Apple's CA render server in
      backboardd drives the framebuffer swap (sel 79/74) off the Metal command buffer's completion -
      trace that path in the runtime (command_buffer/drawable present) next.
    - The strict 1 s alternation on 0182 = the double-buffered drawables (surfaces 2/3): one holds a
      completed frame, the other gets copied mid-render; the 4x4-duplicated glitch patterns the user sees
      are mid-render blur-chain content sampled repeatedly.
    - **vktest extended** (import coherency test, the drawable's path): builds a linear
      DRM_FORMAT_MOD_LINEAR host-import image (pitch 4608, 1125x2436, later shrunk to 512x512/2048 after
      the daemon was SIGKILLed by memory pressure mid-test - `CRASH vktest[66] sig 9`) and measures
      A write-before-import GPU copy, B a GPU SAMPLE in a draw, C write-after-import with no cache push,
      D with dc civac, E a GPU clear INTO the import read back. Output went to launchd's redirect and was
      LOST (the job's stdout vanishes); it now tees to **/var/local/vktest-results.log** and appends a run
      marker to /var/local/vktest-run.log, retrying 12x30 s for the GPU service. Results so far: device up,
      Turnip advertises only VK_KHR_external_memory among the three probed; empty/fill/compute PASS; the
      A-E matrix itself was
    interrupted (sig 9, then the boot's USB gadget network died); after the 240 s storm-delay it
    reached the import (image pitch verified = the requested 2048) and then BLOCKED 12+ min inside
    vkAllocateMemory - the kernel's BoImport wiring never-faulted anonymous pages under memory
    pressure (CA's real imports are pre-wired IOSurface pages and do not hit this). To finish: memset
    the host memory right after mmap, or build the surface through the raw IOCoreSurfaceRoot user client
    (the IOSurface framework binary is not on disk - it lives in the dyld shared cache; the daemon's
    earlier total silence was launchd's lost stdout redirect, not the framework).
    - **Gotchas:** the UDP relay re-streams the persistent ring's last chunk after each reboot (old-boot
      lines reappear - do not read them as current); the Mac's en8 alias is dropped on USB
      re-enumeration (re-run tools/umi-usbnet.sh) and the phone's ue0 once DIED on re-enumeration (0183
      boot: relay stopped at 3 min, phone alive, unreachable - replug the cable); kernel [t] stamps are
      mach_absolute_time ticks, verified 19.2 MHz on 0182 (present 69's [t] = copydump 1's tns * 52.08).
    - Images: `shim/out/umi-0182-copydump.img` (0182) and `shim/out/umi-0183-finwait.img` (0183 +
      sweetfb_finwait=10000), both in-place payload swaps of the 0187 image (same 4174 pages), kernel and
      DTB verified against check-0182-base/check-0176m. Logs: research/logs/umi-0182-*,
      umi-0182d-vktest-*, umi-0183-finwait-live.txt. **Next: (a) the presentation sync - find where CA's
      swap is ordered and make it wait the drawable's command buffer (runtime/bridge); (b) the vktest A-E
      matrix (recover the network with a cable replug, reboot once); (c) then bug 3 (CP_OPCODE_ERROR)
      reproduction on a long interactive boot.**
  - **0182 (2026-10-28, evening): THE NOISE IS IN MEMORY, NOT IN THE COPY - and the dumps never fired again.**
    The 0187 boot was analyzed live (USB networking up the whole time): capture 1 (present 69, ~181 s)
    shows the presented surface holds TRANSPARENT BLACK at (20,48) and WHITE NOISE at (528,1202) -
    neighbor-pixel coherence ~75/255 both axes (a photo reads ~2), i.e. the memory itself is noise, so
    **the stride sweep was already conclusive: no read-geometry bug exists; the GPU's composited output
    is garbage in the middle and untouched (bzero'd) at the top-left**. Findings of the same boot:
    all BoMaps succeeded (the `kr 0xe00002be` lines in turnip-backboardd.log are STALE from a pre-0177
    boot); no window aliasing (per-task 4 GB windows); no CP hang (fences reached 5224). The user's
    panel: "moving noise with various color and some blue strips", and after a touch "the clock on the
    lockscreen shows and is really glitched" - small damage rects (the clock) DO render and copy; the
    rest is the frozen full-screen present from 181 s. Present rate collapsed to 0.76 fps and stopped
    181-1055 s (backboardd looping "vertexFunction is not a MTLFunction"), then touch restarted
    everything. CA frames take 15-60 s at 305 MHz while `sweet_adreno_finish()` caps at 500 ms, so
    present-time copies are MID-RENDER. Captures 2/3 never fired because the dump gate wanted a
    >=64x32 present rect and CA hands over small damage rects. gmem verified correct after all: A650
    `gmem = SZ_1M + SZ_128K` (0x120000, Linux v6.12 a6xx_catalog.c) at base 0x100000, and Linux
    SKIPS UCHE_GMEM_RANGE programming for the a650 family (a6xx_gpu.c) exactly like our hw_init - the
    0175 caveat closes. vktest ALL-PASSes every boot including a 256x256 draw, so basic Turnip
    rendering works; the IMPORT path (the drawable's own) was never tested. **Kernel 0182 (8a31d99)**:
    `sweet_adreno_finish` returns timed-out-or-not (present logs it, 32 lines), a per-present swap-rect
    log (64 lines), copydump regions fixed to the surface's own points (top-left/centre/clock band) so
    any present dumps, and a new **idledump**: every 30 s from 180 s the vsync timer samples the
    pending frame's surface at the same points away from present - what a COMPLETED frame holds.
    **vktest extended** (installed at /private/var/sweet/vktest, runs at boot, logs
    /var/local/vktest.log): `test_import` builds the drawable's exact shape (IOSurface 1125x2436 BGRA
    bpr 4608 via the SWEET IOSurface service), imports it as HOST_ALLOCATION (the runtime's path),
    makes a DRM_FORMAT_MOD_LINEAR image with explicit pitch and measures A write-before-import copy,
    B a GPU SAMPLE in a draw, C write-after-import with no cache push (what CA does), D the same +
    dc civac, E a GPU clear INTO the import read back by the CPU - the matrix that names the layer
    the noise comes from. Image `shim/out/umi-0182-copydump.img` (0187's boot line, copy path,
    sweetfb_dump=1, in-place payload swap, same 4174 pages, kernel+DTB verified), fastboot-booted;
    0187's live log saved as `research/logs/umi-0187-copydump-live.txt`. **Next: read
    /var/local/vktest.log's A-E matrix and the idledump/presrect/finish logs of the 0182 boot.**
  - **0184-0187 (2026-10-29): THE iOS UI IS ON THE PANEL, ICONS CLEAN.** The noise was never a
    present race: two device-info values SweetAdreno gave Turnip were wrong.
    - **0184** (kernel 2b78d5f, previous session, booted twice but unrecorded): `sweet_adreno_finish`
      waits for ring quiescence (`sweetfb_finrounds`, default 4). Both boots (/tmp/umi-0184*-live.log)
      still noise: no fix, harmless, kept.
    - **The decisive analysis (0184 dumps):** the centre words are uncorrelated in every channel
      including alpha, ~63% of bits set (bytes 0xef/0xbf/0xfe/0xf7 = single cleared bits), 5% opaque,
      and identical per surface across captures for minutes - the signature of never-written
      memory/SRAM, not of a mid-render frame (which stays locally smooth). The drawables are
      bzero'd+civac'd at creation (copy path: buffer memory, no pool), so the GPU WROTE this.
    - **0185** (kernel 62dd251): SweetSurface cleans+invalidates a surface at IOSurface write-unlock
      (trap 3 without kIOSurfaceLockReadOnly); first 32 large ones logged. The Metal runtime maps an
      IOSurface's texture once (BoMap clean) and keeps it, so later CPU drawing never reached the GPU.
      Verified live: SpringBoard, mediaserverd (1326x1326, 1271x1823 wallpapers), CollectionsPoster
      unlock through the kernel. Alone it did NOT fix the screen ("still noise").
    - **0186** (kernel 9709e90): **gmem_base 0, not 0x100000.** Linux v6.12 adreno_gpu.c
      MSM_PARAM_GMEM_BASE returns 0 for the A650 family (0x100000 is older A6xx; it is also why
      hw_init skips UCHE_GMEM_RANGE). Turnip adds gmem_base to every GMEM access made through a
      texture (tu_clear_blit.cc unaligned tile store - 1125 px is unaligned - and tu_cmd_buffer.cc
      input attachments): they read 1 MB past the tile data = uninitialised SRAM = the noise.
      **User: "UI visible"** - home screen, wallpaper, dock, Search, Photos widget, labels, clock.
    - **0187** (kernel 95d2dce): **macrotile_mode 1.** Step 20 programs RBBM_NC_MODE_CNTL = 1 as
      Linux v6.12 a6xx_calc_ubwc_config (A650: hbb 16, amsbc, rgb565 predicator, uavflagprd_inv 2,
      macrotile_mode 1), but both device-info paths told Turnip 0: tiled/UBWC textures came back
      tile-shuffled with checkered fringes (every app icon, photo in this session). **User: "Icons
      clean".** Linear surfaces were never affected.
    - Images (all 0184's boot line, in-place payload swaps of umi-0184-quiesce.img, 4174 pages,
      DTB = check-0176m): `shim/out/umi-0185-unlockclean.img`, `umi-0186-gmembase0.img`,
      `umi-0187-macrotile.img` (the current one). Logs: research/logs/umi-0185-unlockclean-live.txt,
      umi-0186-gmembase0-live.txt (local, research/ is not in git).
    - **Open:** (1) **random hang on 0187** (user report): fence 818 stuck; the UDP log starts with it
      already stuck, so the 2 s stuck-fence dump (CP state, possible opcode, IBs) went only to the
      persistent ring - pull it from TWRP (needs the user's OK) and decode against adreno_pm4.xml;
      (2) direct scanout (sweetfb_direct=0 copy path is still the workaround); (3) the stride/finwait
      boot-args are diagnostics and can be dropped from the boot line.
  - **0188/0189 (2026-10-29): the random hang has two faces; diagnostics sharpened.**
    - 0187 boot (TWRP pull, research/logs/umi-0187-hang.txt): fence 835, ring read 3488 of 3549, fence
      word 834, RBBM 0x800005, **CP_OPCODE_ERROR with possible opcode 0** (the CP fetched a zero dword
      as a packet header: an IB longer than written, freed/reused, or an IB2 into unwritten memory),
      no fault/protection/SMMU. The dump printed the newest submission's IB heads, not the stuck one's.
    - **0188** (kernel 52f042e): dump CP_IB1/IB2_BASE + REM_SIZE (Linux v6.12 a6xx.xml 0x928/0x92a/
      0x92b/0x92d, as a6xx_dump) and the stuck fence's IB heads. 0188 boot (live log
      research/logs/umi-0188-hang-live.txt): fence 713, ring 6720 of 7379, **CP busy, interrupts 0**
      (no opcode error this time), IB1 0x206374000 with 1100 dwords left, its first word 0x70450008 =
      CP_COND_WRITE5 (adreno_pm4.xml; Turnip's VSC overflow check). Fences 722-729 queued behind.
      Fence 713 had left the 8-entry history and the IB2 line was lost over UDP. CP_IB1_BASE read
      back page-aligned: it is the IB's start, not an advancing pointer.
    - Ruled out: cross-submission semaphore/event deadlocks (tu_knl_darwin.cc waits all syncs on the
      CPU before submit; metal2vulkan never uses VkEvents).
    - **0189** (kernel 6ab3d34): 64-entry history, only the stuck submission printed, the 64 dwords
      before start + (size - left) of the IB CP_IB1_BASE names, IB2's first 32 dwords. Image
      `shim/out/umi-0189-ibdump.img` (built, verified, NOT booted yet: the phone stayed frozen in iOS).
      **Next: boot it, reproduce, decode the packet at the fetch position against adreno_pm4.xml.**
  - **0190/0191 (2026-10-29): hang dumps that fire, and what they show.**
    - 0189 boot froze (app switcher; display off, frozen on unlock) with NO dump: clients alternated
      waits on fences 662/663 and the per-fence 2 s timer restarted on every call. **0190** (kernel
      commit after 6ab3d34): the trigger keys on the fence word standing still for 2 s, dumps done+1.
    - 0190 boot (research/logs/umi-0190-hang-live.txt): fence 1291, ring fully read, CP_OPCODE_ERROR,
      possible opcode 0; IB1 = IB 11 (2155 dwords, 32 fetched); **IB2 0x206470000, 0 left, memory all
      zero**; the live log shows that iova mapped by handles 424, 420, then 472 (fresh read-only
      command BO) ~200 lines before the hang. Not a write-visibility race: our doorbell follows
      flush_dcache's DSB, and the memory is still zero 2 s later.
    - **0191**: the kernel keeps the last 256 unmaps (iova, len, newest submitted fence, fence word);
      the dump prints frees covering the IB1/IB2 base. 0191 boot (USB net never came up; TWRP pull,
      research/logs/umi-0191-hang.txt): fence 349, CP_OPCODE_ERROR, opcode 0; IB1 = IB 3 of 3345
      dwords at ~1792 in, valid CP_COND_WRITE5 run (VSC overflow checks); IB2 0x2064cc000, 2072 left,
      begins with a valid CP_SET_DRAW_STATE (0x7043802d) of groups at 0x2010e1300, 0x2010de780,
      0x2010de838...; both IB bases lie in a range freed at fence 107 (normal reuse). **So the zero
      dword is in a draw-state group (pipeline/suballocated state), not in IB1/IB2.**
    - Ruled out so far: Turnip darwin BO free (deferred to the newest submitted fence), its chunked
      submit (signals the last chunk), metal2vulkan dropping a draw's pipeline (render.rs retains
      pipeline + made VkPipeline until completion). **Next: dump the CP_SET_DRAW_STATE groups of the
      stuck IB2 (address, first words, free-history lookup) to find which group is zero and whose
      BO it was; suspect pipeline/state suballocation reuse while a command buffer still refers to it.**
  - **0192/0193 (2026-10-29): the zero the CP runs is not in memory when the dump looks.**
    - **0192**: the dump walks IB1 (start to fetch position) and IB2 packet by packet and lists the
      CP_SET_DRAW_STATE groups in force. 0192 boot (live research/logs/umi-0192-hang-live.txt, TWRP
      pull umi-0192-hang.txt): fence 368, CP_OPCODE_ERROR, opcode 0; IB1 = IB 11 of 390 dwords, 96
      fetched, valid type-4 writes (same Turnip preamble as 0190's IB1 at +0x80); IB2 0x20631c000 had
      **0 dwords left** - a finished draw-state group (CP_SET_MARKER, CP_COND_REG_EXEC, register
      writes; 49 valid dwords = its length); no SET_DRAW_STATE in the walked range; the IB addresses'
      frees are early-boot reuse only.
    - Conclusion over 0191/0192: the CP faults on a zero dword while every command word the kernel
      reads 2 s later is valid. Our submit matches Linux a6xx_submit (CCU invalidates, IBs,
      CACHE_FLUSH_TS) and rings after flush_dcache's DSB. Leading theory: the GPU fetched a command
      buffer before the CPU's write-combined stores to it had landed (recording thread != submitting
      thread), or the buffer was rewritten after the fault.
    - **0193**: submit-time check - walk every IB (type 4/7 headers) before the doorbell; at the first
      non-header word log it and re-read 1 ms later (32 reports max). Image
      `shim/out/umi-0193-ibcheck.img`, booted. If it reports words that become valid 1 ms later, the
      fix is a write barrier on the recording side (Turnip darwin: dsb before handing a submit to
      the kernel, or the kernel IPI-DSB / reading back the IB tail before ringing).
  - **0193 result (2026-10-29, TWRP pull research/logs/umi-0193-hang.txt): no IB is malformed at submit.**
    The submit-time walk logged NOTHING - every IB was a valid type-4/7 packet stream when the
    doorbell rang - so the late-write theory is out for the IBs the kernel submits. Hang: fence 739,
    ring read 5456 of 5561, CP busy, "interrupts 0x1"; IB1 = IB 5 of 164 dwords with **0 dwords left**
    (fully fetched; its tail is a normal Turnip epilogue: CP_SET_DRAW_STATE disable-all, CP_WAIT_FOR_IDLE,
    CP_REG_TO_MEM, CP_MEM_WRITE, CP_EVENT_WRITEs); IB2 0x208a38000 (0 left) is a CP_SET_DRAW_STATE
    list in a range last freed at fence 688 (21 frees before; reallocated since).
    **Caveat found:** our kernel never clears CP_INTERRUPT_STATUS, so its OPCODE_ERROR bit may be
    stale from an earlier event (0188 hung with it 0). Do not read "possible opcode 0" as this hang's
    cause until the bit is cleared at init and its first rise is timestamped.
    **Next diagnostic:** clear CP_INTERRUPT_STATUS at init (and after every dump) and log, per submit,
    the moment it changes (fence, ring position); dump the ring words around CP_RB_RPTR (where the CP
    stands between IBs); walk the CP_SET_DRAW_STATE groups at submit time too (the only command
    memory the submit check does not see).
  - **0194/0195 (2026-10-29): two Turnip-side bugs behind the GPU hang; one fixed.**
    - **0194** (deep submit check: follows CP_INDIRECT_BUFFER calls and CP_SET_DRAW_STATE groups;
      CP_INTERRUPT_STATUS changes logged per submit; ring words at RPTR in the dump). Caught it:
      fence 540 IB 13 called 0x206448000 (281 dwords) whose memory held PIXELS (0xfff2f2f7) at
      submit, stable 1 ms later; fence 540 is the hang; the CP error bit rose right there.
    - **Bug 1 (fixed): overlapping iovas.** The kernel window is per task; Turnip's darwin backend
      keeps one connection per process but each tu_device ran its own vma heap over that window
      (backboardd and SpringBoard each make two devices), so devices handed out the same iovas and
      the second BoMap silently replaced the first's PTEs. Fix: phone/turnip/0001 (process-wide
      heap in tu_knl_darwin.cc), kernel **0195** (sweet_adreno_map_at refuses to map over a valid
      PTE; BoMap undoes only its own pieces). Installed: no "map refused" since.
    - **Bug 2 (open): fresh command BOs read zero at submit after a host import's iova is reused.**
      0195 boots still hang (user: stalls, recovers, then hangs, display off). Dump + BO log
      (phone/turnip/0002: /var/local/tu-bo-<pid>.log when /var/local/tu-bo exists; names fixed - the
      backend overwrote `name` with tu_debug_bos_add()'s NULL): host import h231 0x205354000+0xd8000
      freed at fence 921, reaped; its iova reused for new command BOs h748/h754 at fence 922; fence
      924's IB 3 = h754 (302 dwords) reads ALL ZERO from DRAM through the GPU PTE at submit (clean+
      invalidate first) although Turnip wrote it. Same 0xd8000 host-import pattern 3x per boot.
      **Next: at a failing submit compare the GPU PTE's physical page with the BO's own pages
      (getPhysicalSegment) and read the offset through the BO's kernel map** - CPU and GPU views of
      one BO disagreeing after a host-import free (unwire/complete of the import's pages? IOKit
      mapping reuse?). Logs: research/logs/umi-0195-hang.txt, umi-0195e-hang.txt,
      umi-0195e-tu-bo-backboardd.txt. Rollback dylib: xnu-work/work/m2v-bridge-src/out/
      libvulkan_freedreno.prev.dylib.
  - **0196 + ios-flame comparison (2026-10-29).** Kernel **0196** (5fc32a3): when the submit check
    finds a bad word, the client's Submit finds the BO covering it and logs the GPU PTE page, the BO's
    own page (getPhysicalSegment) and the word through the BO's kernel map. Booted
    (shim/out/umi-0196-pagecmp.img); the phone hung; result pending a TWRP pull (not in UDP).
    **github.com/NWylynko/ios-flame (Pixel 4, our bridge/Turnip source) does two things differently,
    one per bug:** (1) flame 0115 gives each v2 CONNECTION its own 4 GB window
    (sweet_gpu_window_alloc; METAL-NEXT.md: "a shared table would let processes collide") - ours is
    per task (bug 1, worked around by phone/turnip/0001); (2) flame's BoAlloc takes memory from a GPU
    pool XNU does not manage, zeroed through a WRITE-COMBINED kernel view ("no cacheable alias"),
    freed pool memory waiting as a zombie until IOKit drops every task mapping - ours is an
    IOBufferMemoryDescriptor of managed RAM zeroed through a CACHED kernel map (md->map()) and mapped
    WC to Turnip: mismatched memory attributes on one page, the prime suspect for bug 2 (fresh command
    BOs zero at submit). Next: read 0196's verdict; if the pages agree, make BoAlloc's kernel view WC
    (or flame's pool) and drop the cached alias; consider per-connection windows as flame does.
  - **0196 verdict (2026-10-29, research/logs/umi-0196-hang.txt): the GPU page table points at ANOTHER
    BO's page.** Three bad IBs, all fresh 16K command BOs (handles 453/477/490): "GPU PTE page
    0x1bd648000, BO page 0x1a281c000 (DIFFERENT); through the kernel map it reads 0x70460001" - Turnip
    wrote the commands into the BO, the CP fetched someone else's page. No map was refused.
    **Root cause (Turnip darwin backend, tu_knl_darwin.cc): the one per-process connection was not
    counted.** tu_knl_darwin_load (enumeration) opened and CLOSED it unconditionally, and every
    darwin_device_finish closed it, so a second instance/device in backboardd/SpringBoard (two "v2
    client" opens per process in every log) closed the connection under a live device: the kernel
    freed and unmapped all its BOs; the reopened client got the same per-task window and handles from
    1 again, and the live device's old handles named the new client's BOs (BoFree/BoMap on the wrong
    BO). Bug 1 (overlap) and bug 2 (zero IBs) are both this. **Fix phone/turnip/0003**: probe reuses
    an open connection; devices acquire/release a count; only the last release closes. Installed on
    the phone with 0196 (diagnostics on); test pending. Credit: ios-flame's per-connection windows and
    the user's pointer to it led to the connection lifetime. Rollback dylib unchanged (prev.dylib).
  - **0197 (2026-10-29): the refcounted Turnip connection did NOT fix it - the BO's own pages move.**
    0196 + phone/turnip/0003 boot (research/logs/umi-0196c-hang.txt): still "GPU PTE page X, BO page
    Y (DIFFERENT)" from fence 96 on, in fresh 16K command BOs whose kernel map holds the commands;
    the two client opens per process are now sequential (probe closed before the device opens), so
    the connection was not the cause (0003 kept: harmless, correct). Page tables cannot alias (each
    L3 is reached through its own L2 entry, all writes under the service lock), so the BO's backing
    page changed after BoMap: BoAlloc gave Turnip a WIRED KERNEL IOBufferMemoryDescriptor
    (kIOMemoryKernelUserShared), mapped cached in the kernel and WC into Turnip's task. **Kernel
    0197 (448f99e)**: BoAlloc = IOBMD kIOMemoryPageable | kIOMapWriteCombineCache (a VM object of
    its own in WC mode, as ios-flame 0115 describes), kernel view mapped WC too, prepare() wires.
    Image shim/out/umi-0197-wcbo.img (0196 diagnostics still on), booted; test pending.
  - **0198/0199 (2026-10-29): the PTE is REWRITTEN after BoMap.** 0197 (pageable WC BOs) still showed
    the mismatch (research/logs/umi-0197-hang-live.txt). **0198** (18102ad) records the page BoMap
    wrote: research/logs/umi-0198-hang.txt, three BOs (fences 680-686), all "BO page now == BO page at
    BoMap, GPU PTE page different" = PTE REWRITTEN after BoMap - the BO never moved; something
    later put another page at its GPU address, and no map was refused (so an unmap + map went over
    a live BO). Ruled out by reading: v1 bump allocator (sa_bo_next, never reused; no v1 client
    opened on these boots), L3 table aliasing (sa_phys keeps the in-page offset), import size
    mismatch (Turnip reserves/imports/maps/frees the same size). **0199** (9213a96): ring of the
    last 2048 map_at/unmap_at calls (iova, length, first page, process, fence); the bad-word report
    prints every record covering its address. Image shim/out/umi-0199-maplog.img, booted.
  - **0199/0200 (2026-10-29): ROOT CAUSE OF THE GPU HANG FOUND - an unlocked v2 client.** 0199's map
    log (research/logs/umi-0199-hang-live.txt), first bad BO at fence 30: "maplog 0x20461b080: map
    0x204618000+0x20000 first page 0x1b4467000 by backboardd" is the ONLY map of that address - the
    BO's own BoMap - yet the BO's descriptor page there is 0x1b49e7000. BoMap built its page list in
    fPageBuf, ONE buffer per client, and Turnip calls the v2 methods from several threads at once
    with no lock in the kernel: concurrent BoMaps overwrote each other's fPageBuf and each mapped the
    other's pages at its own address (the BO table, v2NewSlot, BoFree were racing too). Every symptom
    since 0177 follows: CP_OPCODE_ERROR on zero dwords, pixels as IBs, "PTE rewritten" with no
    refused map, worse with more GPU threads. **Kernel 0200 (d92a7df)**: per-client IOLock; every v2
    method but WaitFence runs alone; clientMemoryForType and teardown lock too. Image
    shim/out/umi-0200-v2lock.img (all diagnostics still on). **First 0200 boot: user "No hang"**;
    backboardd's BO log (research/logs/umi-0200-tu-bo-backboardd.txt) reaches fence 5015 at ~344 s
    uptime with no hang (earlier boots hung at fences 30-900). The UDP relay did not reach the Mac
    on that boot (file server fine). **Confirmed from the TWRP pull (research/logs/umi-0200-run.txt):
    7 clients, 62 presents logged (present 2592 at ~457 s), fences to 5105, and ZERO bad words,
    submit-check hits, stuck fences, refused maps or CP_INTERRUPT_STATUS changes - every earlier
    boot showed them by fence 30-900. The GPU hang is fixed.** Follow-up: drop the hang diagnostics
    (0188-0199 dump/walk/maplog, cost per submit), Turnip's BO log (phone/turnip/0002, marker
    /var/local/tu-bo) and the diagnostic boot-args (sweetfb_dump, finwait 10000, finrounds 6). The earlier fixes stay:
    0195 (refuse overlapping maps), 0197 (WC pageable BOs), Turnip 0001/0003 (process-wide heap,
    counted connection) - each correct on its own, none was this bug.
- **2026-10-25: untethered boot.** User flashed `shim/out/umi-0159-flash.img` (0159, `sweetbattery=2`, hotspot
  boot line, no one-shot resets; SHA-256 9776bd5c...) to `boot` (A-only, 128 MiB); the phone starts iOS on its own.
  Restore stock: `fastboot flash boot ~/ios-umi-backup/boot-read-2026-10-21.img`. `fastboot boot` still works for
  tests. Note: auto mode refuses `fastboot flash` from Claude; the user runs it.
- **🎉 2026-10-25 0159: WALLPAPER WORKS (user: "all good").** Cause: no MAC policy named "AMFI", so lsd's
  `__mac_syscall("AMFI", 0x60)` (boot-arg state) failed and it could not read the signed extension catalog ->
  0 extensions, empty Settings > Wallpaper. 0159 (`bsd/kern/sweet_amfi.c`) adds policy "AMFI": op 0x60 answers
  boot-arg `sweetamfistate` (default 0x86), other ops ENOPOLICY, first use of each op logged. Needed together with a
  fresh LaunchServices database (`sweetlsreset=1`, 0158; log `research/logs/umi-0158.txt`: 5 InternalDaemon
  containers, `com.apple.LaunchServices-4035-v2.csstore` moved aside). Drop `sweetlsreset` / `sweetmgreset` from
  normal boots (one-shot fixes).
  - Battery (0158 log): follows unplug / replug: `99% 4304mV -186mA external=0 charging=0` then `external=1
    charging=1`; user: "battery is all good".
- **2026-10-25 0157 boot (`shim/out/umi-0157.img`, persistent log `research/logs/umi-0157.txt`):**
  - **Settings > About shows "Xiaomi Mi 10"** (user). mkadt: umi `/product` product-name / product-description
    "Xiaomi Mi 10" (ProductType stays iPhone10,3). It needed `sweetmgreset=1` (0156): the MobileGestalt disk cache
    is only invalidated by build / host UUID, so the 0154 boot with the new ADT still showed "iPhone X".
    `SWEET MG: MobileGestalt cache moved aside: 0`.
  - **Battery (0157, `sweetbattery=2`) reads real values** that match TWRP's Linux (100 %, 4405 mV, taper):
    `BATT_SOC type 0xd/0x10 soc 255 (100%), BATT_INFO type 0xd/0x11 vbatt 0x8c9a (4393mV) ibatt 0xff86 (18mA),
    usb 0x10 path 0x95 chg 0x3 err 0x28 temp 0` -> external=1 charging=1. User: status bar 100 % and charging
    "even when not charging" - unplug not yet seen in a log (0157 only logged mode changes) -> 0158 logs every
    change and polls every 10 s.
  - **Wallpaper: none, and Settings > Wallpaper is empty.** Same symptom as Bergamota (ry-diffusion, Poco F1,
    no licence: ideas only): a LaunchServices database seeded while app extensions failed validation is kept
    (seeded + complete) and lists none. TWRP has no HFS+, so 0158 `sweetlsreset=1` renames
    `InternalDaemon/*/Library/Caches/com.apple.LaunchServices*` to `*.sweet-old` from the kernel at launchd start.
  - 0155 (console): on boards with `xiaomi,umi` the drawn console shows SWEET/sweet/Sweet as UMI/umi/Umi
    (`sweetrename=0` off); persistent / UDP logs keep SWEET.
  - Dropped the FairPlayIOKit stand-in (old 0155/0156, in git history): not continuing work that fakes Apple's
    FairPlay driver. wifid stays blocked behind locationd -> fairplayd.
  - Forks searched (357 forks of dipa-studio/ios-sweet, all changed branches): no usable SM8250 battery / flash
    work (Nexo9900 alioth battery guesses registers); Bergamota has real battery (SDM845), wallpaper, A630 GPU
    bring-up (not working yet). No flashlight anywhere.
- **2026-10-25 0155 boot (`research/logs/live-0155.txt`):** fairplayd.H2 now finds the stand-in (1 found), opens
  type 0 and calls sel 22 (struct out 4), sel 23 (struct out 4), sel 21 (struct in 552 / out 552); all refused, it
  still exits after sel 21 (23 execs instead of 59). wifid unchanged. **0156:** selectors in boot-arg
  `sweetfairplayok` (u64 bitmask, default all) return success - outputs zeroed, a struct output the size of the
  struct input gets the input echoed; first 32 bytes of struct inputs logged.
- **2026-10-25: 0155 FairPlayIOKit stand-in (CI, booted - see above).** Boot `sweetiolog=fairplayd.H2` (`research/logs/live-0154f.txt`):
  every instance does exactly one lookup, `IOProviderClass com_apple_driver_FairPlayIOKit` -> 0 found, and exits;
  its plist (`research/ipsw-fs/.../com.apple.fairplayd.H2.plist`): KeepAlive true, MachServices com.apple.fairplayd,
  com.apple.fairplayd.versioned, com.apple.unfreed (HostSpecialPort 17), user mobile. New
  `iokit/Kernel/arm/SweetFairPlay.cpp`: a `com_apple_driver_FairPlayIOKit` service published at boot from
  AppleCLCD::start (boot-arg `sweetfairplay=0` off) with user client `SweetFairPlayUserClient` that logs the opener
  and every external method (`SWEET FAIRPLAY: <proc> sel N scalars in/out, struct in/out`, first 200) and returns
  kIOReturnUnsupported. Aim: fairplayd stays up and answers (with errors), locationd and then wifid unblock; the
  log shows which FairPlay calls matter.
- **2026-10-25: root of the wifid hang = fairplayd.** locationd (extracted to `research/ipsw-fs/20H392__iPhone10,3_6/`
  with `ipsw extract --remote --files`) t3 frame locationd+0xc74f4 is a MIG client stub (`func_1000c7474`: mig reply
  port, msgh_id **1203**, send 0x18 / reply 0x3c bytes, MIG_SERVER_DIED handled), called through a function-pointer
  table from heavily obfuscated code (func_1000d77c0, flattened control flow) - FairPlay style; locationd embeds the
  "Apple FairPlay AAA Certification Authority" certificate and `FairPlayHWInfo`. fairplayd.H2 is exec'd **59 times**
  in this boot (crash/exit loop, never analysed; no CRASH line, so it exits rather than faulting). An on-demand
  port keeps the request queued while each instance dies, so locationd waits forever, and wifid's synchronous
  CoreLocation call waits on locationd. Chain: **wifid -> locationd -> fairplayd**. Next: why fairplayd.H2 exits
  (`sweetiolog=fairplayd.H2`, maybe an exit-status log).
- **2026-10-25 0154 boot `sweetiolog=locationd` (persistent log `research/logs/pull-0154t.txt`):** locationd's IOKit
  use is harmless - IONameMatch pressure / name gyro / AppleBaseband (none, handled), IOPMPowerSource (SweetBattery),
  AppleHIDKeyboardEventDriverV2 / IOAccessoryIDBusHIDDevice notifications, IOPMrootDomain + AppleKeyStore opens. No
  sandbox denials, no crash. So t3's mach_msg waits on another daemon, not a driver. Extracting
  /usr/libexec/locationd from the 20H392 IPSW (`ipsw extract --remote --files`, user OK'd the download) into
  git-ignored `research/ipsw-fs/` to disassemble locationd+0xc74f4. (The session scratchpad under /private/tmp was
  wiped as well; tools now live in `xnu-work/` and the repo.)
- **2026-10-25 0154 boot `sweetsample=wifid,locationd` (`research/logs/live-0154l.txt`): locationd is stuck too**
  (identical stacks 2 min apart, slide 0x39018000, mh 0x1027f8000): t0 main thread in `dispatch_sync_f_slow`
  (func_1a10a431c, from locationd+0x2f55a4 in a run-loop source); t2 the same synchronous CoreLocation NSXPC call as
  wifid's (from locationd+0x6ef180); t3 a dispatch worker in locationd's own code (locationd+0xc74f4 <- 0xd7d34 <-
  0xdadc8 <- 0xf3df4 <- 0x1e2928 <- 0x19601c) blocked in `mach_msg` for a reply. Likely chain: wifid -> locationd ->
  t3's Mach peer (hardware-backed service?) that never replies. Next: `sweetiolog=locationd`; the locationd binary is
  not local (needs the 20H392 root fs) for disassembling t3.
- **2026-10-25 0154 boot with `sweetsample=wifid` (`research/logs/live-0154s.txt`): wifid is blocked on
  CoreLocation.** t0 = main run loop (idle, NSRunLoop run). **t2 stuck in a synchronous NSXPC call**
  (`xpc_connection_send_message_with_reply_sync`) from CoreLocation (func_191d969f0 / func_191d95614 /
  func_191dbde88) called by WiFiPolicy `-[WiFiLocationManager createCoreLocationObjects]` - same stack and sp in two
  samples 2 min apart. locationd is running (exec + AKS calls) but does not answer. Presumably the device setup
  waits behind it. Next: sample locationd too (`sweetsample=wifid,locationd`) to see what locationd waits on.
- **2026-10-25 0154 boot (`research/logs/live-0154.txt`, sweetiolog=wifid):** entries published at boot (en0 later
  says "already published"), new MAC got a new lease, en0 + HTTP fine. wifid's trace is unchanged: the
  IO80211InterfaceRole notification is registered (our object exists by then) but wifid never opens or ioctls.
  IO80211.framework `__Apple80211ServiceMatchedCallback` (0x1d3ed577c) only calls `__Apple80211IOUCResume` for an
  already bound handle, so that notification is not how wifid finds a device; wifid never even matches
  IO80211Controller (MobileWiFi references it) - it stops earlier. Next: `sweetsample=wifid` stacks.
  Also seen: SIOCGIFDEVMTU ('i' 68) on en0, unhandled; driverkitd SIGKILL once (unrelated?).
- **2026-10-25: 0154 Wi-Fi IOKit entries published at boot + one MAC (CI, booted - see above).** Persistent log of the
  `sweetiolog=wifid` boot (pulled read-only from TWRP: `tools/sweet-log-pull.sh`; on macOS replace `stat -c %s` with
  `stat -f %z`; `research/logs/pull-0153i.txt`) shows wifid at launch registering `IOServiceMatched` + `IOServiceTerminate`
  for `IOPropertyMatch {IO80211InterfaceRole = Infrastructure}`, `IONameMatch wlan` (finds the ADT node), ApplePPM
  (none), IOPMPowerSource, IOPMrootDomain open, marconi-bt/bluetooth (none) - and nothing after en0's objects were
  published ~3 min later (no open, no ioctl). 0154: `sweet_wlan_publish_early()` from AppleCLCD::start (with the
  IONetworkStack stand-in; only if the ADT has /arm-io/wlan; `sweetwlanearly=0` off), the later call from en0 only
  logs. The radio (QMI MAC_ADDR, vdev, frames) and en0 now use the ADT's /chosen mac-address-wifi0
  (`sweet_wlan_mac`), so IOKit, en0 and the air agree; the hotspot will see a new client MAC.
  The live UDP log loses everything before the Mac's en8 has its address: run umi-usbnet.sh right after the boot.
- **2026-10-25 boot 0153 + wlan ADT (`research/logs/live-0153w.txt`): wifid now starts** (`exec wifid`, then
  wifianalyticsd, WiFiCloudAssetsXPCService; wifid talks to AppleKeyStore), en0 + HTTP fine as before, but **no
  ioctl reaches en0** within 10 min - wifid apparently does not bind to our IO80211Controller/IONetworkInterface.
  Strings: MobileWiFi / IO80211 / CoreWiFi reference "IO80211Controller", "IO80211InterfaceRole",
  "IOInterfaceName", CoreWiFi "_publishIO80211SkywalkInterface" (iOS 16 matches IO80211SkywalkInterface?), IO80211
  "No Matches for IO80211Controller, trying dk matching". Next boot: `sweetiolog=wifid` to see its IOKit lookups.
  Unrelated: Settings crashed once in PodcastsUI (Swift trap, brk #1 at func_1cdc47c58+336).
- **2026-10-25: umi ADT gets `/arm-io/wlan`** (`tools/mkadt.py`, umi only): device_type "wlan", compatible
  "wlan-pcie,qca6390", local-mac-address = /chosen mac-address-wifi0 (02:53:57:45:45:01). com.apple.wifid has
  `_LimitLoadToDeviceTree = wlan` (per ios-topaz's mkadt notes), so launchd should now start wifid. Rebuilt
  `shim/out/umi.adt` differs from the 2026-10-21 one only by this node, phandle renumbering and the random seed.
  Note: the kernel's Wi-Fi MAC (vdev, ARP/DHCP) is still 02:00:5e:77:ee:10, not the ADT's wifi0 address.
- **2026-10-25 0153 boot (with sweetwlanrenew=60): renewal works, en0 published, wifid never starts.**
  (`research/logs/live-0153.txt`.) "IO80211Controller + IONetworkInterface en0 published: 0", en0 up, default route,
  DNS, HTTP "HTTP/1.0 301 Redirect" (full status line now), stage 8 result 0; 60 s later "DHCP renewal REQUEST" ->
  "DHCP ACK (renewal), lease 3599 s", next renewal in 1799 s. **No ioctl at all reached en0** and the exec log shows
  configd but no `wifid`: launchd does not start it. Next: the `/arm-io/wlan` ADT node (CONTINUE-WIFI "Later"),
  then see which Apple80211 requests wifid sends.
- **2026-10-25: 0153 en0 + IOKit entries for configd / wifid (CI, booted - see above).** Own implementation (the user chose not to copy
  ios-topaz 0900, whose header marks it private). wl0 is renamed en0; new `iokit/Kernel/arm/SweetWLAN.cpp`
  publishes, under the platform expert, an `IO80211Controller` (IOMACAddress, SelfNamed = true so InterfaceNamer
  skips naming) with an `IONetworkInterface` child (BSD Name en0, IOInterfaceType 6, prefix en / unit 0,
  IOBuiltin, IOPrimaryInterface, IO80211InterfaceRole "Infrastructure", IOInterfaceName en0), per configd-1241.80.3
  SCNetworkInterface.c createInterface/processNetworkInterface. No user client, so IO80211.framework should fall back
  to SIOCGA80211/SIOCSA80211 ioctls; en0 logs every unhandled ioctl (Apple80211 ones with their request type), none
  answered yet. The kernel still sets the address itself. Caveat found in prefsmon.c / ifnamer.c: on iOS configd
  creates services only at first quiet when no configuration exists (per-interface defaults are macOS-only), and the
  phone's preferences already exist (USB Ethernet service), so en0 probably gets no configd service by itself.
  **Local compile check restored:** CI buildtree of 0152 at `~/ios-sweet-port/xnu-work/bt` (git repo, outside
  $TMPDIR), log `xnu-work/run-0152.log`, `xnu-work/xnu-cc-sys.py` = tools/xnu-cc.py with /usr/bin/clang:
  `python3 xnu-cc-sys.py run-0152.log bt <paths>`; patches = `git format-patch` there.
- **2026-10-25: 0152 DHCP lease renewal (CI).** sweet_wlip keeps option 51 (lease) and can send a REQUEST in the
  RENEWING state (ciaddr = our address, unicast to the server via the router's MAC, no options 50/54, new xid);
  sweet_wlif's receive path hands DHCP replies (UDP 67->68 to our MAC) to it instead of the stack. The poll thread
  renews at lease/2, then every 60 s until an ACK; boot-arg `sweetwlanrenew=<s>` sets the first renewal sooner (test
  with 60). HTTP check now reads the status line to its end. (The stub syntax check in the scratchpad had been
  skipping everything inside `#if defined(ARM64_BOARD_CONFIG_SWEET)`; now run with it defined: wlip/wldp clean.)
- **2026-10-25 0151 boot: first internet traffic over Wi-Fi.** (`research/logs/live-0151.txt`.) Default route via
  the router added unscoped (err 0: no other default route existed), DNS answered with an Apple address, kernel TCP
  connect to it on port 80 succeeded and the reply came back over wl0. The logged status line was cut to "HTTP/1"
  (the first receive returned only a few bytes; cosmetic - read until CRLF next time). Stage 8 result 0.
- **2026-10-25: 0151 default route + HTTP over wl0 (CI, booted - works).** rtrequest RTM_ADD 0/0 via the router (RTF_GATEWAY |
  RTF_STATIC); on EEXIST (a default route already there, e.g. ue0) the same route scoped to wl0 (RTF_IFSCOPE) and
  the test sockets bound with IP_BOUND_IF. Then the DNS A answer for apple.com is parsed and a kernel TCP socket
  sends `HEAD / HTTP/1.0` to it on port 80; the status line is logged. Stage 8: 70 no route, 71 no A record,
  72 no HTTP reply (66 no DNS reply, as before).
- **2026-10-25 0150 boot: wl0 works - DNS over a kernel socket through the BSD stack.** (`research/logs/live-0150.txt`.)
  DHCP lease + 4/4 pings as in 0149, then "wl0 <lease>/24 up", DNS A query for apple.com to the router: reply 43
  bytes, rcode 0, 1 answer (ARP, IP, UDP all through wl0). Stage 8 result 0. Poll thread keeps running: a minute
  later "wl0 rx 13 tx 11 frames, 0 tx dropped", no panic. Next: default route via the router (internet), lease
  renewal, then hand the interface to configd / the Apple80211 layer for wifid.
- **2026-10-25: 0150 BSD interface wl0 (CI, booted - works).** New `bsd/dev/sweet_wlif.c`, modelled on ue0 in sweet_usb.c: ifnet
  "wl0" (Ethernet family, legacy model), output copies the mbuf into a flat frame for sweet_wldp_tx, received
  frames go to ifnet_input; address/mask from the sweet_wlip DHCP lease (no renewal, no default route yet). After
  the join a kernel thread runs htc_poll every 2 ms under the mutex transmit takes. Check: a DNS A query to the
  router over a kernel UDP socket (stage 8 result 66 = no reply, 67-69 = interface create/attach/address failed).
  Note: `$TMPDIR/sweetwork/t-sweet` is now almost empty (17 .c files left); patches were made from the session's
  scratch rebuild repo, without a local compile.
- **2026-10-25 0149 boot: first IP traffic over Wi-Fi - DHCP lease, ARP, 4/4 pings.** (`research/logs/live-0149.txt`.)
  Unicast DHCP OFFER and ACK arrived at once (REO2SW1, 352 bytes), lease from the hotspot, router ARP answered,
  4 of 4 echo replies (2.4 / 4.7 / 6.9 / 40 ms); stage 8 result 0. Monitor summary: 7 unicast frames from the AP,
  all delivered; 3 broadcasts and 2 IPv6 multicasts decoded and again not delivered (open issue, see 0148).
  Next: an IOKit network interface on top of sweet_wldp (so BSD sockets use Wi-Fi), then the Apple80211 layer.
- **2026-10-25: 0149 DHCP asks for a unicast reply (CI, booted - works).** Broadcast flag cleared in DISCOVER/REQUEST, so the
  server sends OFFER/ACK to our MAC (RFC 2131 4.1); unicast receive works since 0147. Works around the broadcast
  loss below; the loss itself (also IPv6 multicast, so no IPv6 ND) is still open.
- **2026-10-25 0148 boot: broadcasts are decoded, then lost before any host ring.** (`research/logs/live-0148.txt`.)
  Monitor status saw every frame from the AP with FCS ok: 8 broadcasts (our DISCOVER echoes + the OFFERs, seq
  597-602), 2 IPv4 mcast, 2 IPv6 mcast. REO delivered exactly the IPv4 multicast ones (seq 594, 596 seen and
  delivered; IPv6 593, 595 not) plus the unicast ARP reply. Live read of the ring pointer words (sweet-mon `r
  0xd1800000`): only REO2SW2 (id 1) ever moved (8 entries); REO2SW1/3/4, REO exception, rx release all 0. So the
  broadcast / IPv6-multicast MPDUs are dropped or sent to the firmware between RXPCU and the REO destination rings.
  ath11k sends no mcast/bcast setup we skip (configure_filter is a no-op; MCAST/BCAST_DATA_RATE are TX).
- **2026-10-25: 0148 monitor-status frame detail (CI, booted - see above).** Monitor filter now ath11k's MON_STATUS_RING TLV set
  (0x1f01: + PPDU_START, PPDU_END_USER_STATS(_EXT)); for each data frame from the AP the log prints the addr1 class
  (us / bcast / v4-mcast / v6-mcast), seq, REO destination, mcast/directed/AST-miss bits and FCS ok/err counts, with
  a per-class summary after DHCP; REO receive log adds the seq. Question: does MAC 1 decode the broadcasts and IPv6
  multicast and lose them downstream (REO / firmware), or are they never accepted?
- **2026-10-25 0147 boot: unicast receive works, broadcast never arrives.** (`research/logs/live-0147.txt`.) Both mac
  buf rings stocked (255/255 after the scan), and the AP's unicast ARP reply reached REO ("ARP to the AP answered");
  DHCP still got no OFFER. Re-reading the 0146 capture: the AP **did** send a broadcast OFFER ~9 ms after each
  DISCOVER (FromDS, A1 ff:ff:ff:ff:ff:ff, 1 Mb/s, not protected), and our DISCOVERs are valid (IP checksum ok, UDP
  checksum 0, broadcast flag, client id). Across every boot 0140-0147 REO has delivered only IPv4 multicast
  (01:00:5e mDNS) and one unicast ARP - never a broadcast frame and never IPv6 multicast (33:33), although the AP
  sends IPv6 mDNS each time just before the IPv4 copy (consecutive sequence numbers). REO queue setup and hash
  routing match ath11k bit for bit.
- **2026-10-25: 0147 mac buf rings 256 (built on CI, booted - see above).** ath11k posts 4096 refill buffers so the
  firmware can stock both 1024-entry mac buf rings; we post 1023, and the firmware gave all of them to MAC 0's ring
  (129) - MAC 1's ring (144), the 2.4 GHz radio in DBS mode (monitor status ring 1 is the busy one), stayed empty.
  Now 256 entries each, so both MACs get buffers from 1023; per-ring fill printed after DHCP.
- **2026-10-25 0146 boot + Wi-Fi capture: the AP answers, unicast RX is what fails.** (logs
  `research/logs/live-0146b.txt`, capture `research/sniff/0146b-ch1.pcap` from the Mac's Wireless Diagnostics
  sniffer on channel 1, both git-ignored; parser in the session scratch `sniff.py`.) QMI MAC_ADDR result 0 - no
  change. Over the air our data frames are correct (ToDS, A1 AP, A2 our MAC, SNAP, DHCP/ARP), the AP acks them and
  re-broadcasts our DISCOVERs, and it **sends unicast ARP replies to us** (FromDS, A1 = our MAC) which our hardware
  ACKs (no retries) but which never reach REO; the AP's null frames every 11 s are acked too. REO queue descriptors
  read back untouched (all counters 0). Ring dump: refill empty (tp = hp), mac buf ring 129 full of our buffers,
  ring 144 empty -> MAC 1 has nothing to DMA into. Earlier attempts (PS off, encrypt OPEN, native WiFi TX, MAC
  address) were not the cause.
- **Work tree warning (2026-10-25):** macOS's temp cleanup (03:36) pruned `$TMPDIR/sweetwork` (t-sweet lost .git,
  xcc.py, apply.sh, run.log gone). The patch series in `xnu/patches/` is the source of truth; 0147 was made by
  re-applying the series' hunks for the two files. Move the work tree out of `$TMPDIR` before relying on it again.
  Also: Homebrew upgraded llvm to 23 while lld stayed 22 (ld.lld crashed, shim build failed); `brew upgrade lld`.
- **2026-10-24: 0146 give the firmware a MAC (CI run 40131477014, `xnu/out-0146`).** Hypothesis: hardware-built data
  frames carry the firmware's own (zero, OTP empty) MAC as transmitter address, so the AP acks them (RA matches)
  but drops them as from an unknown station; auth/assoc worked because WMI mgmt TX uses the frame bytes. Sends
  QMI WLFW_MAC_ADDR_REQ 0x33 (TLV 0x10, 6 bytes; from cnss2, not ath11k - refusal only logged) after FW_INIT_DONE,
  and WMI_PDEV_SET_BASE_MACADDR (0x400d, tag 0xac, {pdev_id, mac}; unused by ath11k) before the vdev is created,
  both with 02:00:5e:77:ee:10.
- **2026-10-24 0145 boot (CI run 40130623195, log `research/logs/live-0145.txt`): native WiFi made no
  difference.** The TX buffer holds a correct frame (FC 08 01, A1 BSSID, A2 our MAC, A3 broadcast, LLC/SNAP
  aa aa 03 00 00 00 08 00, DHCP), completions identical (FW HTT status 5 = MEC_NOTIFY, confirmed in hal_desc.h and
  ignored by ath11k except for WDS; TQM reason 0 = acked); no answer to DHCP or ARP; result 62.
- **2026-10-24: 0145 transmit as native WiFi (CI run 40130623195, `xnu/out-0145`).** ath11k only uses Ethernet encap
  with module parameter frame_mode=2 (mac.c clears the encap offload otherwise); its default and tested path is
  NATIVE_WIFI. So VDEV TX_ENCAP = 1 and the TCL encap = 1, frames = 802.11 header (FC 0x0108 data+ToDS, A1
  BSSID, A2 source, A3 destination) + LLC/SNAP + payload. RX decap stays Ethernet (it works).
- **2026-10-24 0144 boot (CI run 40129543318, log `research/logs/live-0144.txt`).** The hotspot's address was
  learned from its own mDNS frames (Ethernet source = BSSID, private 10.x address). An ARP request to it and a
  DISCOVER to its MAC were both acked but never answered; RXDMA error rings empty; multicast from the AP still
  arrives. Every stack answers ARP for itself, so the AP never got usable frames from us: the problem is our
  transmit framing, not receive. 12 sent / 12 acked. Stage 8 result 62.
- **2026-10-24: 0144 unicast receive probe (CI run 40129543318, `xnu/out-0144`).** RXDMA error-destination rings
  (133/148) counted and first entries dumped raw; IPv4 source/destination of the first received frames logged,
  and the hotspot's own IP learned from frames whose Ethernet source is the BSSID; then one DHCP DISCOVER to the
  AP's MAC (not broadcast) and an ARP probe to the learned AP address - a reply is a unicast frame to us.
- **2026-10-24 0143 boot (CI run 40128607979, log `research/logs/live-0143.txt`).** The test network is an open
  Xiaomi phone hotspot (Android; hotspot UI shows only MACs; our MAC appears in it). No management frames from the
  AP after the join (no deauth/disassoc), no WMI events except DIAG. Multicast IPv4 from the AP keeps arriving
  during DHCP (rx 7 frames total), so RX is not dead - only frames addressed to us are missing. TX completions
  decoded: FW source word 0x00000a03 = HTT status 5 (bits 12:9) = MEC_NOTIFY (multicast echo check, ath11k ignores
  it), then TQM source reason 0 = FRAME_ACKED. ARP probes to 5 guessed gateways unanswered (Android 11+ hotspot
  subnets are random). Encrypt OPEN made no difference. Stage 8 result 62.
- **2026-10-24: 0143 data diagnostics (CI run 40128607979, `xnu/out-0143`).** After the join: every management frame
  between us and the AP (subtype, reason / action category), all WMI events and HTT messages again (log cap
  reset), raw words of the first TX completions (the FW-source completion has its own status format, not the TQM
  reason), TCL encrypt type OPEN (7) explicitly (0 = WEP_40; ath11k leaves 0 for Ethernet frames), and if DHCP
  gets no answer, ARP probes (sender 0.0.0.0) for 192.168.0.1, 192.168.1.1, 192.168.43.1, 172.20.10.1, 10.0.0.1 -
  any reply proves unicast receive and names the router (the AP's BSSID is locally administered: phone hotspot
  or repeater?).
- **2026-10-24 0142 boot: same as 0141 (CI run 40126985508, log `research/logs/live-0142.txt`).** PS off did
  not change it: 3 DISCOVERs acked, the 5 frames in the first 2 s after association are multicast IPv4 (len 81 /
  54), then nothing on the REO rings while the radio heard 151 PPDUs (monitor status, beacons at ~10/s fit). The
  DISCOVER bytes read back from the TX buffer are a valid frame (broadcast, IPv4 0.0.0.0 -> 255.255.255.255,
  UDP 68 -> 67, BOOTP chaddr = our MAC, IP checksum ok). No WMI events after association (22 generic logs <
  cap 24). AID increases per boot (1, 2, 3): the AP keeps old sessions.
- **2026-10-24: 0142 STA power save off (CI run 40126985508, `xnu/out-0142`).** ath11k add_interface for a STA also
  sets VDEV_PARAM_NSS (0x22) = chains, STA_POWERSAVE_PARAM (0x9002) RX_WAKE_POLICY=WAKE, TX_WAKE_THRESHOLD=ALWAYS,
  PSPOLL_COUNT=NO_MAX and STA_POWERSAVE_MODE (0x9001) = DISABLED - 0141 left the firmware defaults. Leading guess
  for 0141's silence: the firmware went into power save. RX log now 12 frames with destination class (bcast /
  mcast / unicast) and EtherType (no addresses); monitor-status totals printed after DHCP too.
- **2026-10-24 0141 boot: data moves both ways, but nothing received after association (CI run 40126009508,
  log `research/logs/live-0141.txt`).** TX: each of 3 DHCP DISCOVERs completed twice (FW release source 3 and
  TQM source 0, reason 0 = acked by the AP): `tx 3 sent, 6 done, 3 acked`. RX: 5 frames through REO2SW2 (ring
  index 1) in the 2 s right after VDEV_UP/AUTHORIZE (len 81 / 54, push 1 routed, err 0, first+last, done,
  decap 2, L3 pad 2), buffers recycled. Then nothing for ~10 s - no OFFER (stage 8 result 62); no rx release /
  REO exception entries, no kickout event.
- **2026-10-24: 0141 data path + DHCP/ARP/ping (CI run 40126009508, `xnu/out-0141`).** Ethernet mode: VDEV_SET_PARAM
  TX_ENCAP (0x30) / RX_DECAP (0x5b) = 2 after VDEV_CREATE (ath11k add_interface with offload). After the peer map,
  ath11k_dp_peer_setup: PEER_SET_PARAM DEFAULT_ROUTING (0x13) = 3, REORDER_QUEUE_SETUP (0x6013) for TID 0-16 with
  REO queue descriptors at window +0x4c0000 (ath11k_hal_reo_qdesc_setup values). TX: TCL data entry (Ethernet,
  ADDRY, metadata 1, TID overwrite, RBM SW0, cookie msdu id << 2), 16 x 2 KiB buffers at +0x4c8000; completions
  from WBM2SW0. RX: REO2SW1-4 -> hal_rx_desc_ipq8074 (384 B: done +84, len +96, decap +100, L3 pad +24) -> frame,
  buffer back into the refill ring. New `bsd/dev/sweet_wlip.c`: DHCP DISCOVER/REQUEST (broadcast flag), ARP for
  the router (answers ARP for us), 4 pings. Logs `SWEET WLDP: tx done/rx ring ...` (first 6 each), `SWEET WLIP:`
  steps, `SWEET WLDP: data: ...` totals. Stage 8 codes 62-65 = no DHCP offer / no ACK / no ARP / no echo reply.
- **🎉 2026-10-24 0140 boot: the phone associates with the user's open 2.4 GHz network (CI run 40123694108, log
  `research/logs/live-0140.txt`, git-ignored).** Every step answered first time: HTT `peer map (type 0x3): vdev 0
  peer id 2`, `vdev 0 start response type 0 status 0`, `mgmt tx 1 done, status 0` (acked), `auth reply: algorithm
  0 seq 2 status 0`, `mgmt tx 2 done, status 0`, `assoc reply: status 0, AID 1, AP capability 0x1421`, `peer assoc
  confirmed`, VDEV_UP + AUTHORIZE, no kickout in the following 2 s, stage 8 result 0. Monitor status now reads
  -86..-20 dBm (signed fix works; the AP is about -20 dBm). The `HTC: CE2 endpoint 0, 0 bytes, flags 0x2` lines
  are HTC credit reports (trailer only, no payload) - harmless. **Next: data path** - TX: TCL data ring entries
  (hal_tcl_data_cmd) + WBM2SW completion, frames 802.3 or native-wifi with the peer's AST; RX: REO destination
  rings (rx_desc + payload), then DHCP / ARP / ping in the kernel, then an IOKit network interface.
- **2026-10-24: 0140 join an open network (CI run 40123694108, `xnu/out-0140`).** After the scan, if boot-arg
  `sweetwlanssid=NAME` (`_` = space) names a network that was heard: PEER_CREATE 0x6001 -> HTT PEER_MAP (T2H 0x3
  / 0x1e), VDEV_START 0x5003 on the AP's channel (MODE_11G, LDPC rx) -> VDEV_START_RESP 0x5001, open-system auth
  and assoc request (SSID, 8 + 4 legacy rates, listen interval 1) via MGMT_TX_SEND 0x7008 (frame at window
  +0x7c000, 64 bytes inline) -> MGMT_TX_COMPLETION 0x7006 + replies parsed from MGMT_RX, PEER_ASSOC 0x6005
  (41-word cmd, WMI_PEER_AUTH, MODE_11G, 12 legacy rates) -> PEER_ASSOC_CONF 0x6006, VDEV_UP 0x5005, PEER_SET_PARAM
  AUTHORIZE. Legacy 11g only (no HT/VHT/HE IEs). Stage 8 codes 51-61 = join steps 1-11 (51 = network not heard).
  The user's test network is open (2.4 GHz); its name goes only on the boot line, not into git. Also: rssi read
  as signed dBm.
- **2026-10-24 0139 boot: monitor-status reap works, two read-outs wrong (CI run 40122506135, log
  `research/logs/live-0139.txt`).** `monitor status: 9 buffers, 9 ppdus, 9 mpdus, ..., 0 not done` - every reaped
  buffer had STATUS_BUFFER_DONE and parsed to a PPDU end; buffers re-posted (status tp 20). Wrong: channel 0 (the
  ath11k default filter has no PPDU_START TLV - expected) and "signal 76..138 dBm": rssi_comb raw 171..233 is a
  signed byte already in dBm (-85..-23 dBm) - the firmware does the dB->dBm conversion (ath11k db2dbm path, no
  noise-floor add). Fix in the next patch. Scan 7 BSS / 10 frames, stage 8 result 0.
- **2026-10-24: 0139 monitor-status reap (CI run 40122506135, `xnu/out-0139`).** `sweet_wldp_mon_reap()` runs in every
  HTC poll once the receive rings exist (ath11k_dp_rx_reap_mon_status_ring + hal_rx_parse_mon_status): slot at
  host HP is reaped when the hardware TP has passed it, needs TLV STATUS_BUFFER_DONE 0x140 first, TLV walk (tag
  bits 9:1, len 25:10, 4-byte align, PPDU_END counted as 4), PPDU_START 0xcd channel, PHYRX_RSSI_LEGACY 0x4c
  rssi_comb (bits 15:8 at +140) - 95 dBm, MPDU_START 0xcf count, PPDU done at 0x13f / tag 0; same buffer
  re-posted (ath11k allocates new), one spare per status ring for the slot left empty at setup; host HP to wrp.
  Logs the first 8 PPDUs (channel, MPDUs, signal), after the scan listens 3 s more and prints
  `SWEET WLDP: monitor status: N buffers, N ppdus, N mpdus, signal a..b dBm, N not done`.
- **🎉 2026-10-24 0138 boot: receive DMA path writes into host memory (CI run 40120833902, log
  `research/logs/live-0138.txt`).** Report: `refill tp 2046/2046; macbuf filled 991 0 (wrp 0 0, rdp 0 0)` - the
  firmware moved 991 of our buffers into mac buf ring 0 (129) itself; neither pointer word is updated (the
  firmware keeps that producer pointer elsewhere), mac 1's ring stays empty. After the filter and the scan:
  `status tp 0 16` - mac 1's monitor-status ring (147) consumed 8 buffers; read back with sweet-mon, status1
  buffers 0-7 hold hardware TLVs (first words 0x280, 0x1819e, ...), buffer 8 untouched. Errdst rings empty.
  Scan 5 BSS / 8 frames, stage 8 result 0 (line start cut on UDP). **Log format changed: lines carry NUL bytes,
  so grep needs -a** (the 0138 watcher missed `stage 8 done` because grep saw a binary file).
  **Next:** reap + parse monitor-status TLVs (RSSI per PPDU, replenish), then the association path (vdev start
  on a channel, peer create, auth/assoc via WMI mgmt tx, then keys).
- **2026-10-24: 0138 monitor-status filter + receive report (CI run 40120833902, `xnu/out-0138`).** After the receive
  rings: report at 0.2 s, then ath11k_mac_config_mon_status_default: HTT RX_RING_SELECTION_CFG (H2T 0xc) for both
  status rings (pdev 1/2, HTT ring 1, buffer 2048, TLVs 0x1201 = MPDU_START|PPDU_END|PPDU_END_STATUS_DONE, packet
  flags 0x9049249/0x1249/0x9200000/0x1249249), report again 0.5 s later and after the scan. The report now counts
  filled entries in the mac buf / err dst rings' memory and prints both pointer words, to settle the 0137
  "macbuf hp 0" question; status TP should move once the filter is on. Generator fix: enum values written with
  BIT()/GENMASK() evaluated to 0 before (the 0136 table is unchanged, checked by diff).
- **2026-10-24 0137 boot: firmware takes the receive buffers (CI run 40112749946, log `research/logs/live-0137.txt`).**
  `7 receive rings at 0xd1a00000, 1277 buffers ..., HTT SRING_SETUP sent`, then `0.5 s after setup: refill tp
  2046/2046` - the firmware consumed all 1023 refill buffers (TP caught up with our HP) within 0.5 s, so the HTT
  ring setup was accepted. `macbuf hp 0 0, errdst hp 0 0, status tp 0 0` both times: unknown whether the firmware
  keeps the mac-buf producer pointer elsewhere (e.g. its own register) or the buffers sit in its own list - next
  boot should count non-zero entries in the mac buf rings' memory instead of reading the wrp word. Scan still 3
  BSS, stage 8 result 0. The log ends normally at 18:58 (no panic line); by 20:01 the phone was back in TWRP
  (cause not known - not checked whether it rebooted itself).
- **2026-10-24: 0137 receive rings + HTT SRING_SETUP (CI run 40112749946, `xnu/out-0137`).** After the HTT version
  (ath11k_core_pdev_create -> dp_pdev_alloc, qca6390: rx_mac_buf_ring, no rxdma1, 2 MACs, pdev 0): LMAC rings
  in memory only (host pointer in "wrp" words at window +0x7f000 by LMAC index = ring id - 128, target pointer in
  rdp by ring id): refill 128 (HTT HOST1_TO_FW_RXBUF, SW->SW, 1023 x 2 KiB buffers), mac buf 129/144 (RXDMA_HOST_
  BUF, SW->HW, pdev 1/2), RXDMA err dst 133/148 (NON_MONITOR_DEST, HW->SW), monitor status 132/147 (SW->HW, 127
  buffers each). Buffer cookie = buf id, RBM SW1 (4). HTT H2T 0xb htt_srng_setup_cmd per ring on CE4 (new
  `sweet_wlce_htt_send`), ath11k interrupt/low-threshold values, LOOP_CNT_DIS for SW->HW. Sizes: refill 1024
  (ath11k 4096), status 128 (1024). Check: `SWEET WLDP: 0.5 s after setup: refill tp ...` - the firmware moving
  refill buffers into the mac buf rings advances refill tp / macbuf hp. Stage codes: 50 RX rings, 51 DP rings
  (0136 code 50 moved to 51). Monitor-status RX filter (ath11k_mac_config_mon_status_default) not yet.
- **2026-10-24 0136 boot: DP rings accepted (CI run 40111446641, log `research/logs/live-0136.txt`).**
  `SWEET WLDP: 15 rings at 0xd1880000-0xd18f6d00, 8191 link descriptors at 0xd1900000, idle HP 16382, REO gen
  0xc0000dc, 0 bad`; then WLAN_INI/CFG result 0 (WLAN_MODE line lost on UDP, stage result shows it passed), WMI
  READY, HTT 3.90, country 00, scan 4 BSS / 5 frames, stage 8 result 0; chip afterwards MHISTATUS 0x201, errcode
  0. New `tools/umi-usbnet.sh`: start it right after a boot, it waits for en8 and sets 192.168.7.1 (one sudo).
- **2026-10-24: 0136 SoC data-path rings (CI run 40111446641, `xnu/out-0136`).** New `bsd/dev/sweet_wldp.c` = ath11k
  ath11k_dp_alloc + pdev_reo_setup, run after the CE rings and before WLAN_CFG (ath11k order). 15 rings: WBM idle
  link (+ 8191 link descriptors, 128 B, one bank at window +0x100000), SW2WBM release, TCL cmd/status/data0,
  TX completion (WBM2SW0), REO reinject, RX release (WBM2SW3), REO exception/cmd/status, REO2SW1-4; TCL data
  entries pre-tagged 0x144, REO cmd numbers, ipq8074 reo_setup (as qca6390_ops), 48 DSCP->TID maps. Table
  generated from ath11k headers with `tools/ath11k-gen-dp.py`. Deviations: link descs 8192 (32768), TX comp
  1024 (32768), REO dst 1024 (2048), REO status 512 (2048) - window space for RX buffers. Logs `SWEET WLDP:`
  ring count, idle HP, REO gen, ring-base readback mismatches; stage 8 code 50 = DP init failed. Also fixed
  the 0135 HTT connect log line. **Next (0137):** RXDMA refill/monitor rings per MAC (LMAC rings via HTT
  SRING_SETUP), RX buffers, HTT RX filter.
- **🎉 2026-10-24 0135 boot: HTT up, country world (CI run 40109099244, log `research/logs/live-0135.txt`).** HTT
  connect status 0 -> endpoint 1, WMI control now endpoint 2 (max message 2040), `HTT: target version 3.90` (CE1),
  `set country "00"` answered by REG_CHAN_LIST_CC `country "00" id 0 domain 0x60` on both phys (was CN, id 156,
  0x57). Active scan as in 0134: 3 BSS, 4 management frames, completed; stage 8 result 0. Cosmetic: the generic
  CONNECT_RESP printf prints the WMI fields, so the HTT response line shows "endpoint 0 max message 0"; the
  dedicated `(HTT) connect answered ... endpoint 1` line is the right one. **Next: data path** - ath11k dp.c
  ath11k_dp_alloc / pdev_alloc: WBM idle link + SW2WBM release, TCL data/completion, REO dest/exception/reinject/
  cmd/status, RXDMA refill/monitor rings, HTT SRING_SETUP for each, then peer/assoc (vdev start, auth/assoc via
  WMI mgmt tx), WPA keys.
- **2026-10-24: 0135 HTT connect + version, world regulatory country (CI run 40109099244, `xnu/out-0135`).** ath11k
  core-start order: after HTC READY connect HTT_DATA_MSG 0x300 (flags 0x8 = no credit flow) before WMI control;
  CE4 source ring added (HTT host->target); after SET_HW_MODE: HTT VERSION_REQ (u32 type 0) on CE4, wait for
  VERSION_CONF on CE1 (major must be 3, as ath11k). Then WMI_SET_CURRENT_COUNTRY 0x3a001 (tag 0x25f, pdev 0)
  with **"00" (world) - the user's choice 2026-10-24**; `sweetwlancc=XX` overrides; the firmware should answer
  with new REG_CHAN_LIST_CC events. Then the 0134 scan. Stage 8 codes: 48 HTT version, 49 country send.
- **🎉 2026-10-24 0134 boot: active scan works - the QCA6390 transmits (CI run 40102230856, log
  `research/logs/live-0134.txt`, git-ignored).** Both BSS answered our probe requests: `probe-resp` from ch 1
  (2412 MHz, snr 32) and ch 6 (2437 MHz, snr 12), scan completed (`0x2 reason 0`), stage 8 result 0. Channel
  numbers now right. **Regulatory: firmware says country "CN" (id 156, domain 0x57) on both phys** - the default
  from Xiaomi's board data / firmware, not where the phone is. CN allows 2.4 GHz ch 1-13 like the EU, but before
  5 GHz or longer use the host should set the real country (ath11k: WMI_SET_CURRENT_COUNTRY / init country,
  `ath11k_wmi_send_set_current_country_cmd`). Still 1 frame per BSS (firmware filters duplicates).
  **Next:** country setting, then the data path (HTT version, DP rings) and association.
- **2026-10-24: 0134 active scan (CI run 40102230856, `xnu/out-0134`).** Default now active (`sweetwlanscan=0` for the
  0133 passive scan): channel list without the PASSIVE flag (1-13 are active channels in the EU), START_SCAN with
  one wildcard SSID (wmi_ssid, length 0) and probe-request IEs Supported Rates + Extended Rates (ie_len 16), from
  vdev MAC 02:00:5e:77:ee:10. BSS lines now show the channel number (MGMT_RX +0) and MHz derived from it (this
  firmware leaves chan_freq 0), and beacon vs probe-resp. REG_CHAN_LIST_CC (0x3a001, tag 0x261) logged: country
  alpha2, country id, domain. The frequent 0x1d011 events are WMI_DIAG_EVENTID (firmware log, enabled by
  WLAN_INI enablefwlog 1).
- **🎉 2026-10-24 0133 boot: first Wi-Fi scan - the QCA6390 radio receives (CI run 40101164485, log
  `research/logs/live-0133.txt`, git-ignored; it holds nearby networks' names, keep them out of git).** After
  WMI_READY: SET_HW_MODE response 0x4010, then START_SCAN: `scan event 0x1` (started), BSS_CHANNEL / foreign
  channel events for 2412-2472 MHz, `scan event 0x2 reason 0` (completed), `scan completed: 13 channel visits, 2
  management frames, 2 BSS` (beacons with SNR 35 and 14, SSIDs decoded), stage 8 result 0. Open points: the MHz
  printed from the MGMT_RX header (+64, chan_freq) reads 0 - this firmware's wmi_mgmt_rx_hdr is probably shorter,
  check the TLV length; only 2 frames in 13 x 150 ms passive dwell (maybe the firmware forwards one beacon per BSS);
  frequent unknown event 0x1d011 (~1.5 KB, 13 of them). **Next:** active scan (probe requests, needs TX on a
  vdev with our MAC), then the data path (HTT version, DP rings) and association; later the Apple80211 side.
- **2026-10-24: 0133 hw mode, channel list, STA vdev, passive scan (CI run 40101164485, `xnu/out-0133`).** After WMI_READY
  (ath11k v6.6 core start / mac start / add_interface / hw_scan for qca6390): PDEV_SET_HW_MODE 0x401e (DBS, pdev 0),
  SCAN_CHAN_LIST 0x3003 (2412-2472 MHz, MODE_11G + PASSIVE + ALLOW_HE, 20 dBm; array TLV length 4 short as
  ath11k), VDEV_CREATE 0x5001 (vdev 0 STA, pdev 0 = SoC, MAC 02:00:5e:77:ee:10 locally administered, streams =
  rf chains), START_SCAN 0x3001 (scan id 0xa000, passive + chan stat, dwell 150 ms, broadcast BSSID). WMI sends
  wait up to 1 s for an HTC credit. Logs scan events, `SWEET WMI: BSS <bssid> <MHz> snr <n> "<ssid>"` once per
  BSS from MGMT_RX 0x7001 beacons/probe responses, and a summary. HTT version request (ath11k sends it after
  set_hw_mode) is left out: no data path yet. Stage 8 codes: 42-45 send of hw mode / chan list / vdev / scan
  failed, 46 scan never started, 47 not completed in 15 s.
- **🎉 2026-10-24 0132 boot: WMI initialized, WMI_READY status 0 (CI run 40099804000, log
  `research/logs/live-0132.txt`).** Service-ready set seen (0x3, 0x1, 0x4009, 0x4022), INIT sent with chain mask 0x3,
  then events 0x16005, 0x3a001 x2 (REG_CHAN_LIST_CC, 132 B each), 0x2 READY: `status 0, MAC 00:00:00:00:00:00`,
  stage 8 result 0. SERVICE_READY (read from CE2 buffer 3 with sweet-mon, its log line was lost): fw build
  0x1014046e, phy_cap 3, **2 RF chains**, ht_cap 0x381b, vht_cap 0x739139b2, tx power 0x3f, max_bcn_ie 0x300,
  **num_mem_reqs 0** (no host memory needed), 0xb6 scan channels, hw_bd_id 0. READY raw (CE2 buffer 9): fixed MAC 0,
  num_extra_mac_addr 1, num_total_peers 16, extra MAC array (TLV 0x13) also 0 -> no MAC in OTP (fits board id
  0xff). Android's cnss2 hands the firmware a MAC over QMI from Xiaomi's storage; for us the vdev can use a
  locally administered MAC. After READY a new QRTR service appeared: `service 0x39 instance 0x1 node 7 port 0x2`.
  **Next:** WMI pdev setup and a vdev (STA, own MAC), then WMI_START_SCAN and scan/channel events.
- **2026-10-24: 0132 WMI init + WMI_READY (CI run 40099804000, `xnu/out-0132`).** In `sweet_wlce.c`: HTC trailer credit
  reports counted for the WMI endpoint (starts at 1 credit after connect, as ath11k for qca6390); WMI send on CE3
  (HTC flag 1 need-credit-update, u32 cmd id, TLVs); SERVICE_READY parsed (fw build, num_rf_chains, num_mem_reqs,
  hw_bd_id); wait for SERVICE_READY + EXT 0x4009 + EXT2 0x4022, then WMI_INIT_CMDID 0x1: INIT_CMD TLV 0x4a (abi 0,
  0 host mem chunks - ath11k v6.6 never fills them), RESOURCE_CONFIG 0x4b (73 words, ath11k_init_wmi_config_qca6390
  values, chain mask from num_rf_chains, flag1 BIT5, use_pdev_id 1, flags2 BIT9), empty ARRAY_STRUCT 0x12; no hw-mode
  TLV (single pdev). Then wait 5 s for WMI_READY 0x2 (TLV 0x23: status, MAC address). Stage 8 codes: 39 no
  service-ready set, 40 INIT send failed, 41 no READY / status != 0.
- **🎉 2026-10-24 0131 boot: copy engines + HTC + WMI up (CI run 40098529455, log `research/logs/live-0131.txt`).**
  QMI as in 0130, then `SWEET WLCE: rings at 0xd1800000: CE0 base 0xd1801000 (want 0xd1801000), CE2 dst base
  0xd1802000 hp 62, 8 rings` (register writes through the window land; 31 buffers posted = hp 62 words),
  WLAN_INI/CFG/MODE result 0, `HTC: READY on CE2: 2 credits of 2176 bytes, 5 endpoints`, `service 0x100 connect
  status 0 endpoint 1 max message 2040`, CE0 hp 4 tp 4 (both sends completed), 4 WMI events, stage 8 result 0.
  The per-event lines were lost on the UDP log; CE2 receive buffers read with `tools/sweet-mon.py` (CE2 buffers at
  0xd1820000 + n*0x800): READY, CONNECT_RESP, then on endpoint 1 WMI 0x3 SERVICE_AVAILABLE (48 B), 0x1
  SERVICE_READY (332 B), 0x4009 SERVICE_READY_EXT (1028 B), 0x4022 SERVICE_READY_EXT2 (72 B) - ath11k's sequence.
  Direct HP/TP register writes work without shadow registers (at least while the MHI wake doorbell is held).
  **Next:** WMI init (ath11k wmi.c ath11k_wmi_cmd_init: resource config + host memory chunks the SERVICE_READY
  asks for), wait WMI_READY 0x2 (gives the MAC address), then pdev/vdev setup and a scan (WMI_START_SCAN_CMDID).
- **2026-10-24: 0131 copy engines + HTC (CI run 40098529455, `xnu/out-0131`).** New `bsd/dev/sweet_wlce.c` (ath11k v6.6
  ce.c/hal.c/htc.c, qca6390 values). After FW_INIT_DONE and **before** WLAN_CFG (ath11k order): MHI wake doorbell
  (CHDB 127), CE rings in the window's upper 8 MiB (0xd1800000: rdp words, rings, 2 KiB buffers): CE0 (16) and
  CE3 (32) source rings, CE1/CE2/CE5 destination (32) + status (32) rings, 31 buffers posted each. Registers via
  the PCIe window (0x310c, BAR0+0x80000): CE n src R0 0xa00000+n*0x2000, dst R0 +0x1000, status R0 dst+0x58, R2
  +0x400 / +0x408; TCL1 layout for source-direction rings, REO1 layout for status rings; no MSI, no shadow regs
  (HP/TP written directly). After WLAN_MODE: wait HTC READY (3 s), connect WMI_CONTROL 0x100 (1 credit, as ath11k
  for qca6390), SETUP_COMPLETE_EX, log WMI events for 3 s (SERVICE_READY = 0x1 expected). Stage 8 codes: 33 = CE
  init (ring base readback wrong), 34 no HTC READY, 35/36 connect send/response, 37 setup send, 38 no WMI event.
  m3.bin and segments now must end below window +0x800000.
- **🎉 2026-10-24 0130 boot: WLFW QMI complete, firmware in mission mode (CI run 40096953947, log
  `research/logs/live-0130.txt`).** IND_REGISTER, HOST_CAP, REQUEST_MEM (0x5e0000 + 0xd8000), CAP (board id
  0xff, otp 0x48001d), BDF bdwlan.elf 10/10 segments, m3.bin at 0xd1700000, FW_INIT_DONE 0x38 (arrived during
  the M3_INFO wait), WLAN_INI / WLAN_CFG / WLAN_MODE all result 0, `SWEET PCIE: stage 8 done, result 0`. Chip
  afterwards: linkctl 0xb0120008, MHICTRL 0x200, MHISTATUS 0x201, execenv 2, errcode 0. WLAN_CFG was accepted
  without shadow_reg_v2. **Next:** copy engines (CE 0-8 rings in DMA memory, HAL SRNG registers, then
  shadow_reg_v2 in WLAN_CFG), HTC connect, WMI init (ath11k ce.c/hal.c/htc.c/wmi.c), then the `/arm-io/wlan` ADT
  node and topaz 0900 Apple80211 for wifid.
- **2026-10-24: 0130 FW_INIT_DONE + WLAN_INI/CFG/MODE (CI run 40096953947, `xnu/out-0130`).** Ready = FW_READY 0x21 or
  FW_INIT_DONE 0x38 (ath11k qmi.c event handler treats both as firmware ready). Then, as
  ath11k_qmi_firmware_start for qca6390 hw2.0 (Linux v6.6 hw.c/core.c: target_ce_count 9, svc_to_ce_map_len 14,
  fw_wmi_diag_event true): WLAN_INI 0x2F (enablefwlog 1), WLAN_CFG 0x23 (host_version "WIN", 9 CE pipe configs,
  14 service->pipe entries), WLAN_MODE 0x22 (mode 0 mission, hw_debug 0), then listen 1 s. **No shadow_reg_v2
  (TLV 0x14) yet**, although qca6390 has supports_shadow_regs: the list is built from the host HAL rings, which
  come with the copy-engine patch. Stage 8 return codes 21-32 (30 INI, 31 CFG, 32 MODE).
- **2026-10-24 0129 boot: stage 8 result 29 = no FW_READY 0x21 in 10 s; firmware sent FW_INIT_DONE 0x38
  instead.** Log `research/logs/live-0129.txt` starts late (the Mac had no 192.168.7.1 yet), so steps 1-8 are
  only in memory, read with `tools/sweet-mon.py`: TX buffer holds M3_INFO (txn 0xf, addr 0xd1700000, size
  0x411bc), m3.bin is at 0xd1700000 (7f 45 4c 46), RX buffers hold the M3_INFO response (result 0) and an
  indication `04 0300 3800 0000` = msg 0x38 FW_INIT_DONE, no payload. Chip afterwards healthy: linkctl
  0xb0120008, MHICTRL 0x200, MHISTATUS 0x201, execenv 2, errcode 0. Next (0130): accept 0x38 as ready
  (ath11k handles FW_INIT_DONE like FW_READY), then WLAN_CFG 0x23 / WLAN_MODE 0x22.
- **2026-10-24: 0129 WLFW M3 + FW_READY (CI run 40094490013, `xnu/out-0129`).** After the board data: `m3.bin` (266684
  bytes, ELF) read from `image/qca6390` into the firmware memory window, 1 MiB aligned after the REQUEST_MEM
  segments (0xd1700000 with 0127/0128's sizes), M3_INFO 0x3C (TLV 0x01 u64 address, 0x02 u32 size), then wait
  up to 10 s for FW_READY 0x21. Stage 8 return codes 21-29 (28 = M3, 29 = no FW_READY).
- **2026-10-24 0128 boot: CAP + BDF OK (log `research/logs/live-0128.txt`).** Steps 1-5 as in 0127, CAP result
  shown only partly (UDP log cut the chip id / version lines; the build id `WLAN.HST.1.0.1.r1-01134-QCAHSTSWPL_
  SILICONZ-1` survived), otp version 0x48001d, **board id 0xff** -> `bdwlan.elf` (57868 bytes, ELF), 10 segments
  all result 0, `SWEET PCIE: stage 8 done, result 0`. Board id 0xff = OTP not programmed with a board id, so
  cnss2's default bdwlan.elf; Xiaomi's region files `bd_j1*.elf` differ from it (sweetwlanbdf= can pick one if
  calibration looks wrong later). Next: M3_INFO 0x3C (m3.bin) and wait FW_READY 0x21.
- **2026-10-24: 0128 WLFW CAP + BDF (CI run 40093588568, `xnu/out-0128`).** After FW_MEM_READY: CAP 0x24 (logs chip id,
  soc id, firmware version/build, otp, board id), then BDF_DOWNLOAD 0x25 of `image/qca6390/bdwlan.eXX` (XX = board
  id; `bdwlan.elf` for 0xff; override `sweetwlanbdf=NAME`, e.g. one of the Xiaomi `bd_j1*.elf`) in 6 KiB
  segments, file_id = board id, type 1 for ELF. New `sweet_wlan_read_file()` reads files next to amss20.bin.
  Stage 8 return codes now 21-27 (26 = CAP, 27 = BDF). Next: M3_INFO 0x3C (m3.bin), FW_READY 0x21.
- **2026-10-24 0127 boot: WLFW steps 1-5 all OK (CI run 40092013165, log `research/logs/live-0127.txt`).**
  IND_REGISTER result 0, HOST_CAP result 0, REQUEST_MEM ind 0x35 = 2 segments: 0x5e0000 type 1 (DDR) at
  0xd1000000 + 0xd8000 type 4 (CALDB) at 0xd1600000; `SWEET PCIE: stage 8 done, result 0`. The RESPOND_MEM /
  FW_MEM_READY log lines were lost on the UDP log (line 208 starts with a cut `SWE`; SpringBoard was logging at
  the same time), so I checked with `tools/sweet-mon.py` while it was up: IPCR receive buffers hold the
  RESPOND_MEM response (txn 3, msg 0x36, result 0 error 0) and the FW_MEM_READY indication 0x37 (confirm_rx,
  answered with RESUME_TX). Chip afterwards: PCIe linkctl 0xb0120008, MHICTRL 0x200, MHISTATUS 0x201 (M0, no
  SYS_ERR), BHI execenv 2, errcode 0. The UDP log can drop lines under load: check the stage result line.
  Next: CAP 0x24, BDF_DOWNLOAD 0x25, M3_INFO 0x3C, FW_READY 0x21.
- **2026-10-24: 0127 WLFW QMI steps 1-5 (built on CI).** 0127 = `research/ipcr-wlfw-wip.diff` +
  new `bsd/dev/sweet_wlfw.c`, run for `sweetwlan=8` after IPCR finds WLFW: IND_REGISTER 0x20, HOST_CAP 0x34,
  wait REQUEST_MEM 0x35 (segments logged), RESPOND_MEM 0x36 from low RAM `sweetwlfwmem` (default 0xd1000000,
  16 MiB, each segment aligned to its size up to 1 MiB, zeroed), wait FW_MEM_READY 0x37, then listen 500 ms.
  Return codes from stage 8: 21-25 = step 1-5 failed (log lines `SWEET WLFW:` say why). Boot:
  `sweetusb=2 sweetwlan=8 sweetwlandelay=90`, log `research/logs/live-0127.txt`. Next: CAP 0x24, BDF, M3.
- **WLFW next (in progress, not built).** `research/ipcr-wlfw-wip.diff` (local, applies to the t-sweet tree after
  0126): IPCR sends wait for completion, 8 KiB TX buffer at block +0xf000, received packets queued, QRTR DATA
  with RESUME_TX, `sweet_ipcr_send()` / `sweet_ipcr_service()` for a WLFW client on port 0x4001. Still to write:
  `bsd/dev/sweet_wlfw.c` (ath11k qmi.c, qca6390 hw2.0): IND_REGISTER 0x20 (TLV 0x10 fw_ready, 0x15 client_id
  0x4b4e454c, 0x16 request_mem, 0x17 fw_mem_ready, 0x18 fw_init_done, 0x1B cal_done), HOST_CAP 0x34 (0x10
  num_clients 1, 0x13 nm_modem 0x1e, 0x14 bdf 1, 0x16 m3 1, 0x17 m3_cache 1, 0x1A cal_done 0, 0x1C mem_cfg_mode 0),
  REQUEST_MEM_IND 0x35 -> RESPOND_MEM 0x36 (segments from low RAM, e.g. 0xd1000000 16 MiB), FW_MEM_READY 0x37,
  CAP 0x24, BDF 0x25 (bdwlan.e*), M3 0x3C (m3.bin), FW_READY 0x21, WLAN_CFG 0x23, WLAN_MODE 0x22.
- **2026-10-24: QRTR up to the QCA6390 firmware (0126, `sweetwlan=7`, log `research/logs/live-0126.txt`).**
  MHI channels 20/21 start (code 1), firmware QRTR v1 HELLO from node 7, `NEW_SERVER service 0x45 instance
  0x101 node 7 port 0x1` = WLFW. Fixes on the way: 0125 (channel types/event rings set before M0), 0126 (MHI
  contexts are 44 bytes packed, not 40: channel 20 and event ring 1 were misplaced -> START_CHAN code 16).
  Next: WLFW QMI (topaz 0122): ind_register, host_cap, respond_mem, cap, BDF (bdwlan.e*), M3 (m3.bin), mode.
  Wallpaper (user request): topaz's comes with its GPU stack (Mesa freedreno, Adreno 610); its README still lists
  wallpaper/widgets as being investigated. umi would need the Adreno 650 port first.
- **🎉 2026-10-24: QCA6390 firmware RUNNING under iOS (0123, log `research/logs/live-0123.txt`).** BHI (512 KiB SBL)
  -> SBL -> MHI READY -> contexts + M0 -> events `state 2` (M0), `ee 1` (SBL) -> BHIe 9 x 512 KiB -> `ee 2`
  (AMSS / mission mode), MHISTATUS 0x201. The blocker for 0116-0122 was **MSI**: without an enabled MSI
  capability the PBL reported BHI success, then ERRCODE 0xef0e0003 and never started the SBL. 0123 points
  the endpoint's MSI (cap 0x50, 32 vectors) at a polled word in the DMA pool - no interrupt controller needed.
  Also needed on the way: 0118 (pool and monitor windows in kernel_map: arm IO_MAP_SIZE is 8 MiB), 0119 (the
  modem FAT has random 8.3 names; find amss20.bin by VFAT long name), 0120 (polled MHI host), 0121
  (ath11k_pci_sw_reset), 0122 (PARF BDF->SID table). Ruled out: pool address (0xa0000000 same error), DMA data.
  TWRP's cnss2 only probes ("Powerup is ignored"); its ipc log is in `research/logs/twrp-cnss/`.
  **Next:** MHI channels 20/21 (IPCR) -> QRTR -> WLFW QMI (topaz 0122: cap, BDF bdwlan.e*, M3 m3.bin, mode),
  then copy engines / HTC / WMI (ath11k), then topaz 0900 Apple80211 for wifid.
- **Where Wi-Fi stopped (2026-10-23 evening).** 0115 tested: monitor works (`tools/sweet-mon.py`), stage 4 read
  BAR0 = 1 MiB, MHI CHDBOFF 0x300 ERDBOFF 0x700 BHIOFF 0x100 BHIEOFF 0x224, BHI execenv 0 (PBL waiting), serial
  0x2f180788 (log `research/logs/live-0115.txt`). **0116 (built, not yet booted):** stage 5 BHI (first 512 KiB of
  modem:image/qca6390/amss20.bin via a FAT reader, DMA pool 0xd0000000 32 MiB write-combined, SMMU 0x1c00/0x1c01),
  stage 6 BHIe (512 KiB segments); + USB Ethernet re-configures after a host bus reset (macOS reset the idle
  device and the link stayed dead). Next boot: `sweetusb=2 sweetwlan=6 sweetwlandelay=40`, then
  `sudo ifconfig en8 inet 192.168.7.1 netmask 255.255.255.0 alias` on the Mac. If SBL waits for MHI before
  BHIe: MHI context init (CCABAP/ECABAP/CRCBAP, M0). Then QRTR over MHI IPCR 20/21, WLFW (topaz 0122), m3.bin,
  ath11k CE/WMI, wifid (topaz 0900) for Settings > Wi-Fi. Untethered option discussed (flash the iOS image to
  `recovery`, Vol Up + Power; backup ~/ios-umi-backup/recovery-read-2026-10-23.img) - needs the user's go-ahead.
  Tweak-injection WIP (kern.exec_inject + AMFI dyld policy) parked in `research/exec-inject-wip.diff` (local).
- **🎉 2026-10-23: PCIe link to the QCA6390 UP under iOS (0114, log `research/logs/umi-0114-usb-wlan3.txt`).**
  `link UP: linkctl 0xb0120008 (gen 2 x1)`, `bus 1 dev 0: id 0x110117cb` 10 ms after LTSSM enable. 0113 stayed in
  LTSSM 0 (detect): the missing piece was **vdd-wlan-dig = PM8009 S2 (`smpf2`, 950 mV)** - voted through RPMh in
  0114. smpa4/5/6 and smpc8 have two cmd-db entries, so sweet_rpmh refuses them; they are on anyway.
  **USB Ethernet works on umi** (0112 SMMU stream 0, 0114 CONNECTION_SPEED_CHANGE before NETWORK_CONNECTION for
  macOS AppleUserECM): ping 192.168.7.2 ~1.5 ms, live log on udp/5140. 0115: UDP monitor on udp/5141
  (`tools/sweet-mon.py`: r/w physical registers, `wlan STAGE` re-runs the bring-up) and PCIe stage 4 (BAR0, MHI).
- **Wi-Fi plan (2026-10-23).** umi Wi-Fi is a **QCA6390 on PCIe0** (DT `qcom,cnss-qca6390`, pcie@1c00000; TWRP
  enumerates it as 0000:01:00.0 17cb:1101, driver cnss_pci), not topaz's modem-integrated WCN. Firmware: modem
  partition `image/qca6390/` (amss20.bin, m3.bin, bdwlan.e*, regdb.bin), copied to `research/umi-wlan-fw/` (local).
  Layers: WLAN_EN GPIO20 (rails S4A/S5A/S6A/S8C/pm8009 S2 are shared), PCIe0 (GDSC 0x6b004, GCC vote 0x52008
  bits 0-5, DT qcom,phy-sequence, PERST GPIO79, CLKREQ 80, LTSSM PARF 0x1b0 bit 8; PHY rails L5A/L9A = UFS PHY's),
  SMMU streams 0x1c00/0x1c01, MHI (BHI + BHIe full boot chain of amss20.bin), QRTR over MHI IPCR, WLFW QMI
  (topaz 0122 reusable), ath11k CE/HTC/WMI/HTT + DP rings, then topaz 0900's Apple80211 en0 for wifid.
  DMA: DT cnss_wlan_region asks 20 MiB below 4 GiB. **0113** = stage 1 (`sweetwlan=1` clocks, `=2` +PHY,
  `=3` +link and endpoint ID; `sweetwlandelay` s). 0112: umi USB stream 0 SMMU route (sweetusb=2 hung at the
  first DMA write right after the soft reset, log `research/logs/umi-0111-usb.txt`).
- **2026-10-23: all 8 CPUs on umi (0111 kernel, `cpus=8`, log `research/logs/umi-0111-cpus8.txt`).** `SWEET CPU:
  8/8 CPUs initialized, SGI1 verified`: cpu1-3 A55, cpu4-7 A77 (MPIDR 0x400-0x700, cpu7 = prime) via PSCI CPU_ON.
  User: works fine, Settings "superfast". `tools/umi-boot-image.sh` now defaults to `cpus=8 sweetfb_direct=1`.
  Next: cpufreq (the A77s likely still run at the bootloader's clock; SM8250 uses cpufreq-hw/EPSS).
  0111 verified: Settings > About opens at once.
- **About wait, root cause (0110 log `research/logs/umi-0110.txt` + dyld cache `research/dsc/20H392__iPhone10,3_6/`):**
  symbolicated: main thread -[PSGAboutDataSource _macAddress] -> __SCNetworkInterfaceCopyAllWithPreferences ->
  dispatch_once held by ____wait_for_IOKit_to_quiesce_block_invoke -> SCDynamicStoreNotifyWait (Settings' Ethernet
  watcher got there first). configd's InterfaceNamer (configd-1241.140.6 ifnamer.c) opens the **IONetworkStack**
  object (IONetworkingFamily, absent here) and only then posts `*QUIET*`; without it, WaitStackTimeout = 300 s. 0110
  showed root busy 0 throughout and no IOKitWaitQuiet callers. **0111:** empty IONetworkStack (+ user client that
  opens) published in AppleCLCD::start, before configd (InterfaceNamer checks once at launch); `sweetnetstack=0` off.
  0109 verified: bottom-edge touches now flagged (`448,2339 edge`), home swipe works in apps.
- **2026-10-23: main fast-forwarded to umi-scanout (2bb9a89)** at the user's request.

- **Settings > About "can't escape" (log `research/logs/umi-0108d.txt`, `sweetiolog=Preferences,MobileGestaltHelper
  sweetsample=Preferences`):** About queries IONetworkInterface/IOSerialBSDClient/bluetooth (none). First sample: main
  thread in semaphore_wait via libdispatch from a framework at 0x235d3xxxx; 2 min later back in its run loop (the wait
  ends). The real blocker: **bottom-edge touches never got kIOHIDDigitizerEventFromEdgeTip** (SweetHID used sweet's
  1079/2399; umi panel is 1080x2340, max y 2339 < 2351) -> no home gesture inside apps. **0109** uses fPanelW/fPanelH.
  Right edge verified: touches at x 991 and 977 registered (panel 1080 wide).
  Symbolication: `ipsw extract --remote --dyld --dyld-arch arm64 -o research/dsc <IPSW>` (20H392 cache).

- **🎉 MILESTONE 2026-10-23: TOUCH WORKS ON umi (kernel 0108, image `shim/out/umi-0108.img`, log
  `research/logs/umi-0108.txt`).** User: "TOUCHSCREEN WORKS". Chain: QUP1 SE5 GSI-only I2C through GPI DMA (0093-0098),
  SMMU routes for GPI stream 0x56 **and the QUP1 wrapper stream 0x43** (0102: without 0x43 every transfer faulted and
  the SoC reset), ST FTM5 at 0x49 with fts_521's probe sequence (0106), and **vdd_boost_vreg = PM8150B GPIO 5 driven
  high** (0107/0108: DT `regulator-always-on`, so Linux enables it at boot; under iOS it was found driven low, and the
  IC then talked over I2C but never sensed). Found by tracing Linux in TWRP (i2c ftrace on the recovery cmdline,
  regmap spmi0-02, enabled regulators) and ruling out polling (static `ftspoll` tool) and the display (mipi_reg B9,
  panel sleep). Log: boost `out 00 -> 80`, 554 FIFO events, multi-touch (id 1) and edge flags reach SweetHID.
  Open: Settings > About froze the UI (no panic; user forced fastboot), check what About queries.
  Touch x seen 0..676 only (y 0..2339): verify the right side of the screen maps correctly.

Hardware facts and partition backups live outside git in `~/ios-umi-backup/` (UMI-FACTS.md).
Build: `BOARD=umi shim/build.sh [payload]`, `tools/mkadt.py OUT --highmem --board umi`.

- **Shim diag (7fbacb9) on hardware:** red console shows on the DSI *command-mode* panel with no
  kick (ABL leaves MDP autorefresh on). UFS 3.0 at 0x1d84000 answers read-only SCSI; GPT parsed,
  userdata lba 0x680000 (4K), ~211 GiB. Reboot-to-bootloader (IMEM 0x146bf65c) works.
- **First XNU boot (upstream CI 39158169212 kernel = patch 0081, ADT --board umi, cmdline
  `debug=0xc serial=3 cpus=1 keepsyms=1 -enable_kprintf_spam -noprogress rd=ufsroot0 wdt=-1
  wdt_test=no_user_checkin sweetlog=0 sweettouch=0 sweetkeys=0 sweetusb=0`, read-only):**
  boots through zone init, platform expert, AKS, IOWatchdog, IOCoreSurfaceRoot, HID, battery stub,
  `SWEET FB: AppleCLCD 1080x2340 stride 4320 at 0x9c000000 ... presented as 1125x2436`, then
  stops there. Reproduced twice (18:01, 19:00). No SWEET UFS line (busy-poll path would print
  within 15 s), so the hang is before root lookup. Android uses `GICv3 27 Level arch_timer`.
- **Hypothesis (unconfirmed):** interrupt storm from sources ABL leaves enabled; XNU only EOIs
  unknown INTIDs. The first unguarded shim GIC diag (9dc804a) also hung. Patch **0082** (809516a):
  clean GIC slate + mask unhandled INTIDs + `SWEET GIC: bootloader left ...` log. Not built yet:
  fork workflows need enabling in the GitHub UI. Guarded shim diag 4b33137
  (`shim/out/shim-diag-gic2-umi.img`) booted once but no photo was taken.
- USB: fastboot drops (error -71) came from a bad cable and a low battery (19 %).
- **ROOT CAUSE of the SWEET FB hang: my mkadt umi change.** SweetCPU matches IONameMatch
  'qcom,kryo470' (0018); umi CPU nodes said only 'qcom,kryo585', so no CPU driver attached and
  boot waited forever for gIOAllCPUInitializedKey (no SWEET CPU lines). `startup_debug=1` showed
  the drivers start in PE_lockdown_iokit. Fixed in 511b765 (kryo585 + kryo470). The shim GIC diag
  (4b33137) showed ABL leaves no SGI/PPI enabled; VTIMER/PTIMER 30 irqs/300 ms, SGI 10/10,
  PSCI CPU_ON OK for CPUs 1-7 (MPIDR 0x81000100..0x81000700). 0082 was not the fix; harmless, kept.
- **MILESTONE (20:01, fork CI 39463125994 = 0082 kernel, image `shim/out/umi-xnu-0082b.img`,
  cmdline above + startup_debug=1, read-only):** `BSD root: ufsroot0, major 1, minor 0` ->
  `hfs_ValidateHFSPlusVolumeHeader: unknown Volume Signature : a165` (encrypted Android data) ->
  `cannot mount root, errno = 19`, mountroot retries. Kernel UFS driver works on SM8250.
  NEXT (destructive, needs explicit user OK right before): build the iOS 16.7.x iPhone X HFS+ root
  (README step 2) and flash it to userdata.
- **Root image built (2026-10-20 20:59, PC only):** `research/ios16-root.img` (16G, 11.6G used) from
  20H392 D22AP OS 087-86698-044 + SystemOS 087-86593-047 + AppOS 087-86715-047 (remotezip, no full
  IPSW), apfs-fuse built from source (`-DCMAKE_POLICY_VERSION_MINIMUM=3.5 -DCMAKE_CXX_FLAGS="-include
  cstdint"`), sweet-root-tweaks applied (7 _PanicOnCrash, 2 CommCenter; no mobileactivationd
  container -> data ark skipped). Linux fsck_hfs keeps reporting "Volume header needs minor repair"
  only. Sparse: `research/ios16-root.simg` (sha256 f6536bdd...). D22AP ADT from the IM4P (LZFSE) ->
  umi ADT has /product. Boot image `shim/out/umi-ios1.img` (sha256 f99ad339..., 0082 kernel, cmdline
  README + cpus=4 sweetfb_hz=30 sweettouch=0 sweetkeys=0 sweetusb=0, console kept on).
- **MILESTONE: iOS USERLAND ON umi (2026-10-20 22:00).** userdata flashed 21:35-21:41 with
  `fastboot -S 512M flash userdata research/ios16-root.img` (raw image; `-S` on the .simg fails with
  "Error reading sparse file"; without -S the bootloader's missing getvar max-download-size made
  fastboot send 3.4 GB at once). Writes ack in 0.001 s; the bootloader then ignored commands until a
  Power+VolDown restart. Front-panel USB gave error -71 on bulk transfers; rear port OK (512 MB in
  13.5 s). Boot of `umi-ios1.img`: Apple logo at ~1 min, then launchd, the expected crash/relaunch
  loop of bluetoothd / fairplayd.H2 / xpcproxy, and sampler output for backboardd and SpringBoard[26]
  (both alive). Console text covers the panel; next: `sweetfb_noconsole=1`.
- **First-boot wait (log `research/logs/umi-ios1.txt`, pulled from TWRP with sweet-log-pull.sh):**
  4/4 CPUs, UFS read-write, HFS mounted, backboardd display on + 1125x2436 surfaces + swaps; only
  CRASH driverkitd once. SpringBoard t0 waits in os_unfair_lock <- _LSContextInitCommon <-
  LSApplicationRecord <- CCSModuleRepository init; t1 in
  `___LAUNCH_SERVICES_IS_RESEEDING_ITS_DATABASE_AND_MAY_BLOCK__` -> sync XPC to lsd: first-boot
  LaunchServices database build. Symbolicated with `ipsw dyld a2s` (ipsw 3.1.739 in ~/.local/bin)
  on the SystemOS cryptex dyld cache (apfs-fuse -o ro), address - slide.
  Note: a normal reboot lands in TWRP (Android has no data); do not format data there.
- **lsd root cause (boot ios3, sweetsample=lsd):** lsd seeding -> MIInstalledInfoGatherer ->
  __GenerateBuiltInAppInstallSessionID -> MGCopyAnswer("re6Zb+zwFKJNlkQTUeT+/w" = UniqueDeviceID) ->
  WifiAddress getter (libMobileGestalt): reads IODeviceTree:/chosen `mac-address-wifi0`, then
  sdio/wlan/marconi-wifi nodes, else waits forever (MGIOKitSupport.c run loop) for
  IOServiceMatching("IONetworkController"). No Wi-Fi + sweetusb=0 -> lsd, SpringBoard, backboardd
  blocked, CPUs idle. Fix 7d47dc8: umi /chosen mac-address-wifi0/-bluetooth0 (synthetic).
- **MILESTONE: iOS LOCK SCREEN ON umi (2026-10-20 ~22:50, `shim/out/umi-ios4.img`, ADT 7d47dc8,
  0082 kernel, cmdline: README + cpus=4 sweetfb_noconsole=1 sweetfb_hz=30 sweettouch=0 sweetkeys=0
  sweetusb=0 sweetsample=lsd,SpringBoard sweetnull=lsd,SpringBoard,backboardd).** No input yet.
  NEXT: touch (FocalTech `fts` at I2C 3-0049, QUP 0xa94000 on umi; sweet driver has a FocalTech
  path but sweet MMIO/GPIO/RPMh constants), then PMIC keys (PM8150 family).
- **Patch 0083 (1613c08, CI 39496202549): umi touch + volume-up**, board chosen at runtime by
  `sweet_board_is_umi()` (sweet_rpmh.c; ADT root compatible "xiaomi,umi"). Touch IC is NOT
  FocalTech: DT `st,fts`, driver Xiaomi `fts_521` (CONFIG_TOUCHSCREEN_ST_FTS_V521) = ST FTM5,
  I2C 0x49, FIFO read 0x86 (8-byte events 0x13 enter / 0x23 motion / 0x33 leave, x=(e3&15)<<8|e2,
  y=e4<<4|e3>>4), scan on = A0 00 01. QUP1 SE5 0xa94000; GCC vote 0x52008 bits 18-21 + 27,
  RCG 0x18600 (DFS: pick the XO/1 level), branches 0x18004/0x18008/0x23138/0x23140/0x185fc;
  TLMM SOUTH 0xf500000: SDA/SCL 36/37 mux 1, reset 38, IRQ 39, avdd GPIO 69 (= disp_vddio, only
  driven if not already high); vdd RPMh ldoc1 1800 mV; umi cmd-db at reserved 0x80860000/0x20000.
  Keys: arbiter/PON identical to sweet; volume-up PM8150 GPIO6 = PPID 0x0c5. SweetHID maps with the
  boot framebuffer size. Sources: research/umi-src (Xiaomi umi-q-oss), live DT. Syntax-checked with
  `research/tools/xnu-cc-sys.py` (tools/xnu-cc.py using /usr/bin/clang) on the CI buildtree.
  Test boot: umi-ios4 cmdline without sweettouch=0/sweetkeys=0 (touch starts 45 s after UFS init).
- **0083 on hardware (23:04, `shim/out/umi-ios5.img`, log research/logs/umi-ios5.txt):** KEYS WORK
  (arb 0x50010000, pon-apid 13, volup apid 25 subtype 0x11; power/volup/voldown press+release).
  Touch stopped at `GCC branch 0x18008 halted (0x80000002)`: wrap1 s-ahb is in HW clock gating
  (CBCR bit 1) and reads CLK_OFF while idle. DFS level 0 is XO/1 on umi. **0084**: skip the halt
  check for HW-gated branches, as Linux clk_branch_check_halt() does.

- **Branch `umi-scanout` (2026-10-21): umi + 0086-0090 (ports from ios-topaz, see `topaz-ports`) + 0091 direct
  display scanout (topaz 0092-0099/0114 adapted). NOT booted yet; CI-built, compile-checked locally.**
  What 0091 does, only with boot-arg **`sweetfb_direct=1`** (off by default):
  - At AppleCLCD start it logs the apps SMMU (0x15000000) SMRs/S2CRs matching the MDP stream id (`sweetfb_sid`,
    default 0x820) and refuses if the display stream is translated (`sweetfb_direct=2` forces). Then it reads every
    SSPP (VIG0-3, DMA0-3 at MDP 0xae01000 + 0x4000.. / 0x24000..) and CTL0-5, picks the one pipe whose SRC0_ADDR is
    the boot framebuffer (0x9c000000) and the one CTL with LM0 stages set; anything else -> off, with a log line.
  - Full-screen BGRA surfaces of 1080x2340 or 1125x2436 get pixels from a pool of 16 MiB slots at
    **`sweetfb_pool` (default 0xc0000000) x `sweetfb_slots` (6)**: low RAM that XNU (highmem, above 4 GiB) does not
    manage, mapped cached (copyback) in kernel and tasks. **Check against umi's live DT /reserved-memory
    (checked 2026-10-21 in TWRP: 0xc0000000-0xc6000000 is free; 0xb0400000-0xb1400000 is disp_rdump_region).**
  - A frame that is one pool surface: clean dcache (dc cvac) over the panel window, write SRC0_ADDR/YSTRIDE0,
    CTL_FLUSH = pipe bit | bit 17; latched by the command-mode panel's MDP autorefresh. Direct frames go out every
    vsync (60 Hz) instead of `sweetfb_hz`; other frames use the CPU copy path and the pipe is pointed back at the
    boot framebuffer. On-screen surfaces stay "in use" (state page +0x18) until one vsync after replacement.
  - Panel window x offset rounded to 4 px (16-byte fetch alignment): logical offset is now 20,48 (touch the same).
  - Panic: PE_panic_hook points the pipe back at the boot framebuffer. Power off: the last direct frame is copied
    into the boot framebuffer, then faded as before. With direct scanout the kernel console is not visible over
    iOS frames (it still goes to the persistent log).
  Test: umi-ios4 cmdline + `sweetfb_direct=1 sweetbusy=60`; look for `SWEET FB: SMMU ...`, `SWEET FB: MDP ...`,
  `SWEET FB: direct scanout on: <pipe> via CTL<n>`. If the screen freezes on the Apple logo: flush not latched
  (autorefresh off?) -> next step would be a CTL_START kick (CTL+0x1c) per frame; if garbage: SMMU/pool issue.

- **First boot of 0091 on umi (2026-10-21 18:05, Mac build, `shim/out/umi-0091-direct.img`, log
  `research/logs/umi-0091-direct.txt`):** boots to iOS as before (shim built with Homebrew LLVM: wrappers for
  clang/ld.lld with `-fno-jump-tables` + a strcmp object; minimal mkbootimg v2, byte-identical to stock except
  second_addr). `SWEET BUSY: round 0: 0 busy services` (0088 works). Direct scanout refused itself as designed:
  `SMMU sCR0 0x270406 (unmatched streams fault), 87 SMRs`, `SMR4 id 0x820 mask 0x402 -> S2CR 0x4 (translate, cb 4)`:
  ABL runs the display through context bank 4 (the splash at 0x9c000000 is mapped there), not bypass.
  Live DT reserved-memory (TWRP): cont_splash 0x9c000000-0x9e300000, disp_rdump 0xb0400000-0xb1400000.
- **0092:** when the display stream is translated, walk cb4's stage-1 tables (4K granule) and log SCTLR/TCR/TTBR0
  and the translation of 0x9c000000, 0x9ca00000, 0x9e200000, 0xc0000000; direct scanout turns on only if every
  pool page is mapped 1:1. Without an explicit `sweetfb_pool`, the pool becomes the free tail of the splash region
  after the boot framebuffer: 0x9ca00000 + 2 x 12 MiB (`sweetfb_slotsize`, new). Two slots = backboardd's two
  alternating 1125x2436 surfaces (bpr 4608, 11.2 MB each).

- **0092 on hardware (2026-10-21, `research/logs/umi-0092-direct.txt`): DIRECT SCANOUT WORKS on umi** (user: looked
  normal, worked well). cb4 SCTLR 0xe0 (M=0: the display context does not translate), `direct scanout on: VIG0 via
  CTL0 (flush 0x20001), pool 0x9ca00000 x 2 slots`; no per-frame copy lines; display off/on fade fine.
- **Touch on umi: 0084 clocks OK, then `need ABL-loaded I2C firmware and 32-bit FIFOs`**: the failing test is
  GENI_IF_DISABLE_RO (SE+0x64) bit 0 = FIFO interface disabled. Live DT: i2c@a94000 has
  `dmas = <&gpi 0 5 3 0x40 0>, <&gpi 1 5 3 0x40 0>` (qcom,gpi-dma@a00000, gpi-ee-offset 0x6000, gpii-mask 0x3f,
  iommus <apps_smmu 0x56 0>): Xiaomi's i2c-qcom-geni runs this SE in GSI_ONLY mode.
- **0093:** `bsd/dev/sweet_gpi.c`, polled GPI DMA I2C after umi-q-oss gpi.c / i2c-qcom-geni.c (sources fetched from
  MiCode/Xiaomi_Kernel_OpenSource umi-q-oss): SMR for stream 0x56 -> display cb (translation off); GPII 0
  (`sweetgpii=N`), TX ch0 / RX ch1 / one event ring, rings + bounce buffers at 0x9e200000 (free end of the splash
  region, mapped uncached); SE5 into GSI mode; write = CONFIG0 + GO + DMA TRE, read = RX DMA TRE then CONFIG0 + GO;
  completion by polling the event ring RP (EOT on the last channel, QUP notify bit 10 = NACK). sweet_touch.c uses it
  when SE+0x64 bit 0 is set. Logs `SWEET GPI: ...` (first 24 events). Not booted yet.

- **0093 on hardware (`research/logs/umi-0093.txt`):** SMMU route OK (`SMR5 = 0x80000056, S2CR = 0x4`), gpii0 ready
  (ch0 0x1020000a ch1 0x10200102 ev 0x10110002 = started/allocated). First write (0x49, 1 byte, stretch) ended with
  XFER_COMPLETE code 16 status 0x4 on its DMA TRE; 0093 called that an error and the STOP hung in STOP_IN_PROC.
  Xiaomi's i2c-qcom-geni only fails on status & DM_I2C_CB_ERR (0x40 NACK, 0x100 proto, 0x200 arb) -> that write was
  fine. TWRP (same phone) drives the same IC through gpi_dmaa00000_gpii0; its pins: 36/37 in no pull 2 mA, 38 out
  high pull-up 8 mA, 39 in pull-up 8 mA, 69 out high (avdd = touch_vddio_vreg, fixed regulator on GPIO 69; no vdd).
- **0094:** status-based errors, completion matched to the TRE that asked for EOT (late events ignored), recovery
  resets channels even if STOP stays in progress, ST FTS probe retried 5x 100 ms over GPI.

- **0094 on hardware (`research/logs/umi-0094.txt`): touch still fails, and the phone RESETS itself (back to TWRP)
  ~1 s after the GPI attempts** (0093 too: log ends ~6 lines after `no ST FTS answer`; 0092 without GPI ran 4+ min).
  No panic text: a hardware/firmware reset. Every write ends XFER_COMPLETE code 16 (UNEXP_ERR) status 0x4 len 0 on
  its DMA TRE (mainline gpi.c treats code 16 as DMA_TRANS_ABORTED, so 0094's "code 16 is fine" was wrong); the
  following read's GO puts ch0 in state 0xf (ERROR) and times out. SE STATUS 0x41 after the write.
  Checked and matching the live DT/Xiaomi source: TREs (CONFIG0 0x220001, GO 0x200001/0x200900, DMA 0x100200),
  channel contexts, scratch (pair/proto 3/seid 5), pins (36/37 qup13 = mux 1, 2 mA, bias-disable), avdd = GPIO 69
  (touch_vddio_vreg, fixed regulator, no vdd-supply in DT: the ldoc1 vote is not from the DT).
  Open suspects: the SMR we add for stream 0x56 (hypervisor/TZ reaction), the IC not ACKing (len 0), the reset after
  errors. TWRP uses gpi_dmaa00000_gpii0 for the same IC.
- **0095:** GPI touch path only with `sweettouchgpi=1` (default: log and stop) so the default boot is stable again.

- **Reset cause found (0096 test stages, kernel CI 39641705846, logs `research/logs/umi-0096-stage{1..4}.txt`).**
  The persistent log flushes every **10 s** by default (SWEET_LOG_SECS), not 1 s: up to 10 s are lost at a reset,
  so use `ufslogsecs=1` when timing matters. Test boot-args: `sweetgpistage=N sweettouchdelay=20 ufslogsecs=1`;
  after step N the touch thread logs `SWEET TEST: stage N alive K s` for `sweettestsecs` (40) and reboots itself
  into recovery (IMEM 0x146bf65c = 0x77665502, PSCI SYSTEM_RESET), so runs need nobody at the phone
  (Mac runner script: boot, wait for adb recovery, pull log).
  Results: 1 SMMU SMR for stream 0x56 -> survived; 2 + GPII/channels started -> survived; 3 + touch powered
  (ldoc1, GPIO 69, reset) -> survived; **4 + one write/read (code 16 status 0x4 len 0, then ch0 ERROR) -> the
  phone resets 16 s after the failed transfer** (last line `alive 15 s`), no panic text. So the SMMU change, GPI
  setup and power-on are innocent; a transfer that fails and leaves the SE5 command active (GENI STATUS 0x41) /
  GPI ch0 in ERROR is what brings the SoC down ~16 s later (looks like a secure-side watchdog or bus timeout).
  Next: (a) make the transfer work (candidates: SE_GENI_CLK_SEL / M_CLK_CFG not written in GSI mode, GPII
  interrupt registers left at 0 instead of Linux defaults, no QUP bus bandwidth vote); (b) on failure, clean up
  like Linux (terminate: STOP/RESET channels) plus an SE M_CMD abort, so a failure cannot reset the phone.

- **0107 on hardware (`research/logs/umi-0107.txt`): under iOS the boost was OFF**: PM8150B GPIO 5 found as
  `mode 01 vin 00 pull 04 out 00 drv 01 en 80 status 80` (output driven low; Linux: out 80). The touch thread then
  stalled inside the first PMIC write: wrong channel stride (used 0x80*apid; Linux pmic_arb_offset_v5 RW channel is
  **0x10000 * apid**, the observer is 0x80*apid). **0108** fixes the stride (one mapped page per APID).

- **0106 hand test (`research/logs/umi-0106.txt`):** the full Linux replay got byte-identical replies (sysinfo,
  lockdown, `c0`, C1 05 -> 00 00 50 0f 02 0e 01, echoes, FORCE_CAL) and still no touches: not a command problem.
  TWRP experiments: our polling tool (`ftspoll`, static aarch64, W 86/R 8 at 100 Hz over /dev/i2c-3) read 254 touch
  events while Linux kept working -> polling is fine. Panel B9 (`00 00 14 18 00 00 00 11 03`, TSP-sync-like) zeroed
  via `/sys/class/drm/card0-DSI-1/mipi_reg` -> touch still worked (restored). Panel asleep (DCS 28 + 10) -> touch
  still worked: the IC does not need the display. Enabled regulators in TWRP that the touch driver does not own:
  `display_panel_vci` 3.0 V (TLMM GPIO 71, boot-on) and **`vdd_boost_vreg`: PM8150B GPIO 5, regulator-always-on,
  0 users** -> Linux switches it on at boot, nothing in our kernel does. Linux register state (regmap spmi0-02):
  c440=01 c441=01 c442=05 c444=80 c445=03 c446=80 (status c408=80).
- **0107:** PMIC writes (arbiter v5 EE 0 channel at 0xc600000, owner checked) in sweet_keys.c; umi touch start logs
  PM8150B GPIO 5 as found and, if off, writes Linux's values (`sweettouchboost=0` skips).

- **TWRP I2C trace of fts_521 probe (2026-10-23, `research/logs/twrp-fts-i2c-trace.txt`):** recovery image read
  from the phone (`~/ios-umi-backup/recovery-read-2026-10-23.img`), cmdline + `trace_event=i2c:i2c_write,i2c:i2c_read,
  i2c:i2c_reply,i2c:i2c_result trace_buf_size=8M` patched in place (header id recomputed), `fastboot boot` (RAM).
  Linux sends: reset -> FIFO until 03; A6 00 00 r208 (sysinfo); A6 00 00 r4; A4 06 70 (load lockdown); A6 00 00 r28;
  FA 20 00 00 78 r1 (=c0); reset; reset; A0 00 01; A2 03 00 00 00 03; A0 00 00; A0 00 01; C1 05 r7; A2 02 01.
  **In TWRP, `i2cset -f -y 3 0x49 0xa0 0x00 0x00 i` killed touch and our `... 0xa0 0x00 0x01 i` brought it back**
  (user-verified): our sense-on works once Linux has initialized the IC/environment.
- **0106:** `sweetftslinux=1` (default) replays that whole sequence in our kernel before sensing.

- **0105 hand tests (`research/logs/umi-0105.txt`, `umi-0105i.txt` with `sweettouchirq=1`):** pins after power-on
  avdd69 cfg 0x200 io 0x3 (output, high), reset38 out high, irq39 input pull-up (low only right after reset, then
  high). Sense off/on cycle answered (ECHO A0 00 00, FORCE_CAL, ECHO A0 00 01), then **no touch events and the
  IRQ line never asserted** in 18000 (10 ms polling) / 900 (IRQ-driven) samples while the user touched.
  So the IC itself does not sense. Ruled out: I2C transport, vdd (ldoc1) and avdd (GPIO 69) as Linux sets them,
  reset/IRQ pins, sense-on bytes, polling load, QUP0 BCM vote. Remaining guesses: a display-side requirement
  (on-cell touch synced to the DDIC), a supply shared with the panel, or an fts_521 init step not yet found.
  Next idea: replay sequences against the IC from TWRP (working Linux, /dev/i2c-3) with a small static tool.

- **0103/0104 hand test (`research/logs/umi-0104.txt`): touch I2C runs without errors but the IC reports no touches.**
  After A0 00 01 the FIFO gave `43 01 a0 00 01 ..` (STATUS_UPDATE ECHO of our command) and `43 05 01 00 00 00 00 01`
  (STATUS FORCE_CAL triggered), then nothing in 44000 reads (~7 min) while the user touched. fts_521 sends the
  same sense-on (A0 00 01; FOD build: A0 00 00, wait, A0 00 01, then gesture cmd A2 03 ..), so the command is right.
  Suspect: no analog supply (AVDD = GPIO 69 touch_vddio_vreg) or sensing otherwise stalled. **0105:** pin readback
  after power-on and every 10 s (avdd69, reset38, irq39), IRQ-line low sampling, sense off/on cycle,
  `sweetftsscan=N` for the active-scan bits.

- **UMI TOUCH I2C WORKS (0102, 2026-10-22/23).** Root cause of every failed transfer and of the PS_HOLD resets: the
  I2C *data* is moved as the QUP1 wrapper's SMMU stream **0x43** (DT `qcom,qupv3_1_geni_se@ac0000 iommus =
  <&apps_smmu 0x43 0>`, Linux maps the buffers on `gi2c->wrapper_dev`), while the GPI fetches TREs/writes events as
  0x56. Only 0x56 was routed; 0x43 hit `unmatched streams fault` -> code 16 len 0, then TZ/hyp reset. 0102 adds an
  SMR for 0x43 -> cb4 (translation off; `sweetqupsid=0` skips). Found via adb in TWRP: `/sys/kernel/debug/ipc_logging/
  {a94000.i2c,gpi_dmaa00000_gpii0}` (Linux does the same W1/R8 transfers, succeeds), msm-bus-dbg client
  `ac0000.qcom,qupv3_1_geni_se` (QUP0 BCM vote, 0101 adds it, not the cause), DT iommus of the wrapper.
  Runs: G (stage 7 FTS W1+R8) -> code 2 (EOT) len 1, GO EOB, RX len 8 = `03 00..` CONTROLLER_READY, survived;
  H (stage 5) -> probe, scan mode A0 00 01, `selected ST FTM5, 1080x2340`, 10 s polling 0 errors, survived.
  Linux powers the IC exactly like us (regulator.39 pm8150a_l1 1.8 V + regulator.77 disp_vddio/touch_vddio GPIO 69).
  **0103:** GPI touch path on by default (`sweettouchgpi=0` off). Image `shim/out/umi-0103.img` booted for a hand test.

- **0100 experiments (stage 7: one chosen transfer, kernel CI 39652288748, logs `research/logs/umi-0100-stage7-*.txt`):**
  A write 1 byte to absent 0x10 -> phone reset within ~1 s (log ends at the touch power line, not even the first
  trace line saved). B plain write (no stretch) to 0x49 -> code 16 status 0x4 len 0, SE status 0x41, reset 16 s
  later (thread alive meanwhile). C plain read 8 bytes from 0x49 -> GO completed cleanly (XFER_COMPLETE code 4 EOB,
  status 0 on TRE 0x9e200410) but then the touch thread **stalled inside a GPI register access** in gpi_wait (no
  1 s timeout ever printed; the rest of iOS kept logging) until the reset. D = A on gpii1 -> reset within ~1 s.
  Reading: every transfer we start on QUP1 SE5 ends in a PS_HOLD reset, immediately on a NACK, ~16 s otherwise;
  GPII choice does not matter. Consistent with this SE being protected/shared with the secure side (SE runs
  GSI-only firmware, FIFO disabled; the panel has FOD) and TZ/hyp reacting to our accesses or to SE error events.
  Blind experiments have stopped converging: next is ground truth from Linux (register reads of SE5/GPII0 while
  TWRP/Android drives touch: needs /dev/mem or a debug kernel), or touch parked.

- **0097-0099 (2026-10-21 evening, automated runs, logs `research/logs/umi-009{7,8,9}-stage*.txt`):**
  0097 = Linux gpi_config_interrupts defaults + polled acks, SE io-init + qcom_geni_i2c_conf (CLK_SEL 0,
  M_CLK_CFG 0x71, SCL 0xa02c1a; ABL left m_clk 0x11), gpi_terminate (STOP, SE M_CMD abort, RESET, reprogram,
  START), test stage 5 (full path + retries, then heartbeat/reboot). 0098 = per-step trace of the first transfers.
  0099 = stage 6, one NOP TRE.
  Results: the write still ends XFER_COMPLETE code 16 status 0x4 len 0 (status bit 2 is probably GENI
  M_ILLEGAL_CMD: the SE rejects the command), then the read GO puts ch0 in ERROR (timeout). The terminate now works
  (SE status back to 0, both channels STARTED again), but the phone **still resets ~15-16 s after the first real
  transfer**, whatever follows. TWRP after the reset: PMIC `Power-off reason: PS_HOLD (MSM Controlled Shutdown)`,
  `Power-on: Hard Reset, cold` = a deliberate reset by the SoC (TZ/hypervisor), not a PMIC fault. TWRP's
  /sys/kernel/debug/tzdbg/hyp_log shows the hypervisor virtualizes SMMU SMRs ("SMMU Virt SMR: Invalid SID ..."),
  so our SMR5 write went through hypervisor emulation; previous-boot TZ/hyp logs are not kept.
  Stage 6 (NOP TRE) survived 40 s but the GPI never completed the NOP (no event), so it does not separate a
  DMA/SMMU cause from an I2C/SE cause. Default build stays safe (`sweettouchgpi` off).
  Ideas not tried: a write to an absent address (bus activity, expect NACK); look for the SID 0x56 SMR that
  Linux/hyp use in TWRP (hyp_log lists SIDs it rejects); compare with an upstream-style GPI init (mainline gpi.c);
  ask the user for a TWRP with /dev/mem or a debug kernel to read SE5/GPII registers while Linux drives touch.

## Agent handoff / active work (2026-10-15, latest)

### >>> UPDATE 2026-10-18 (read first, then the 10-17 handoff below) <<<

**STATE at end of 2026-10-18 (evening):**
- On the phone: userdata = **image v15** (`/run/media/dipa/android/ios-sweet-ipsw/ios16-root-20H392-v15.img/.simg`; = v14 + `/private/var/preferences/SystemConfiguration/preferences.plist` with one network service "USB Ethernet": Interface DeviceName ue0 Type Ethernet, IPv4 Manual 192.168.7.2/24 router 192.168.7.1, DNS 1.1.1.1 8.8.8.8, set "Automatic" as CurrentSet). Fallback image v14 (v12/v13 deleted).
- Kernels: **0078** = all 8 cores (`cpus=8`, cpu6/7 = A76, homogeneous SMP; mkadt now emits 8 CPU nodes; ADT `shim/out/sweet-0078hi.adt`); **0079** = display off/on via IOMFB selector 12 kern_RequestPowerChange(state) (fade over 6 vsyncs, then black; verified: power button gives "SWEET FB: display off/on"); **0080** = `SWEET NET: <proc> route add/delete/change ...` and `... add/delete address ...` trace (built, `shim/out/shim-boot-0080s.img`, NOT booted yet).
- **Internet over USB: not working yet.** Host side is ready (temporary iptables: FORWARD accept for 192.168.7.0/24 + MASQUERADE, comment "ios-sweet"; lost on host reboot). With v15 the phone sent no DNS and no outbound traffic (only mDNS/ARP) -> configd probably did not apply the service (or did, without default route/DNS). Next: boot 0080s on v15, watch `SWEET NET` lines (does configd add 192.168.7.2 / default route on ue0?). If configd ignores ue0 (not an IOKit IONetworkInterface; configd 1241.140.6 source in `research/configd-1241`, SCNetworkInterface createInterface needs IONetworkInterface -> controller (IOMACAddress, SelfNamed) -> bus), add IOKit stand-ins and/or rename the ifnet to en*.
- Live log listener (`nc -ukl 5140`) may still be running, writing `logs/live-0078s.txt`.

**LIVE LOG over USB (0077, boot 0077s): no more recovery round-trips.** Boot an image with `sweetusb=2`, run `tools/sweet-usbnet.sh logs/live-NAME.txt` on the PC: it waits for the phone's CDC-ECM interface, sets 192.168.7.1/24 (sudo) and prints/saves the kernel console the phone streams every 100 ms as UDP to 192.168.7.1:5140 (starts with the last 64 KiB). `ping 192.168.7.2` checks the link. Current image: `shim/out/shim-boot-0077s.img` (kernel 0077, ADT sweet-0069hi, cpus=6, sweetfb_noconsole=1, sweetfb_hz=30, sweetusb=2). The recovery pull (`tools/sweet-log-pull.sh`) is still the way after a panic/hang before USB comes up.

**🎉 USB networking works (boot 0076s, 18:24 local): `ping 192.168.7.2` from the PC answers in ~1 ms, 0 % loss (200-packet burst, 1500-byte frames, 512/1024-byte frames).** 0075: CDC-ECM function (bulk 0x81/0x01, interrupt 0x82 NETWORK_CONNECTION; host MAC 02:00:5e:77:ee:01) + kernel ethernet ifnet `ue0` (legacy output, header strip like if_fake) with 192.168.7.2/24 set from the kernel (proto_plumb + SIOCAIFADDR on an in-kernel socket). 0076: received frames into one cluster mbuf (mbuf_allocpacket gave a first mbuf of length 0 -> panic "Failed mbuf validity check: len -14"). Host side (Linux cdc_ether, interface `enp0s20f0u3u1`): `nmcli dev set IF managed no; sudo ip addr add 192.168.7.1/24 dev IF; sudo ip link set IF up`. Boot image `shim/out/shim-boot-0076s.img` (`sweetusb=2`). iOS itself does not see ue0 yet (configd needs an IONetworkInterface in IOKit).

**USB device mode works (boot 0074s, 17:45 local): the host enumerates the phone at high speed as `1209:0001 ios-sweet "Sweet iOS (USB bring-up)"`.** 0072 read-only probe: ABL leaves the USB30_PRIM GDSC and all 7 USB clocks on, DWC3 v3.20a (GSNPSID 0x5533320a) in device mode (GCTL 0x00112000), halted (DCTL RUN_STOP 0, DSTS 0x00d3de04), event buffer still at ABL's 0xfdfc8000, QUSB2 PHY alive. 0073 (`sweetusb=2`): DCTL soft reset, own event buffer (polled, interrupt masked), ep0 DEPSTARTCFG/SETEPCONFIG/SETTRANSFRESOURCE, setup TRB, RUN_STOP; control-transfer state machine as Linux ep0.c; descriptors: vendor class, no data endpoints. It ran but no event came: **0074** forces the VBUS session in the Qualcomm wrapper (QSCRATCH 0xa6f8800: HS_PHY_CTRL |= UTMI_OTG_VBUS_VALID(20)|SW_SESSVLD_SEL(28), SS_PHY_CTRL |= LANE0_PWR_PRESENT(24), as Linux dwc3_qcom_vbus_override_enable) -> connect + enumeration. Image `shim/out/shim-boot-0074s.img`. Black Phone app: main thread waits in -[VMVoicemailManager fetchAccounts] (sync XPC; voicemail needs the modem).

**Navigation works (boot 0071s on v14, log `logs/boot-0071s.txt`):** swipe up from the bottom edge returns to the home screen; app switcher works. Two fixes: **0070** pid_hibernate (syscall 435 was nosys on the macOS config -> SIGSYS killed SpringBoard in -[SBToAppsWorkspaceTransaction _didComplete] when an app left the foreground; the only CONFIG_EMBEDDED-only entry in syscalls.master); **0071** touches starting within 48 px of an edge carry kIOHIDDigitizerEventFromEdgeTip (UIKit `_UIEventHIDTouchEdgeTypeForHIDEvent` reads the digitizer EventMask 0xb0007 bits 0x800/0x1000/0x2000/0x40000). Diagnosed, not fixed: Settings (Preferences) SIGTRAP in PodcastsUI func_1cdc47c58: force-unwrap of `URL.volumeTotalCapacity` (nil on our HFS+ root). Phone/Photos/Messages show black (MobilePhone launches, no crash) - next: stack samples via boot-arg `sweetsample=MobilePhone,MobileSlideShow,MobileSMS,SpringBoard` (image `shim/out/shim-boot-0071s.img`).

**🎉🎉 MILESTONE 2026-10-18 ~15:30 local: iOS 16.7 SPRINGBOARD HOME SCREEN ON THE PHONE** (boot `shim/out/shim-boot-0069s.img` = kernel 0069 + ADT `shim/out/sweet-0069hi.adt`, image **v14**; log `logs/boot-0069s-v14-HOMESCREEN.txt`). Home screen with a few apps, Settings opens, Control Center / lock screen / notification center work, touch + buttons work, 6 A55 cores (`cpus=6`), `sweetfb_noconsole=1 sweetfb_hz=30`. Known issue: cannot leave Settings (home gesture / AssistiveTouch home do nothing) - to investigate.
What it took today (in order): 0058 HID services (Apple IOHIDFamily-1915 user client), 0059 iPhone X identity (hw.product etc.), 0060 SPMI keys + GENI touch, 0061 1125x2436 presented display, 0062 RPMh L11C touch power + IOPMPowerSource battery, 0063 GENI FIFO packing (Goodix GT9896), 0064 PRIV_WORK_INTERVAL grant (SpringBoard "Failed to create work interval"), 0065 SMP via PSCI (6 A55), 0066 crash map regions, 0067 console mute without cons_ops write, 0068 IOSurface lookup of an already-mapped surface returns base -1 (backboardd snapshot crash), 0069 UFS log flush 10 s. Image v13: CommCenter removed from launchd.plist, BKNoWatchdogs. **Image v14** = v13 + Setup skipped (`/var/mobile/Library/Preferences/com.apple.purplebuddy.plist` SetupDone/SetupFinishedAllSteps true, SetupVersion 11, daemonizeNeedsToRun false; purplebuddy.notbackedup mini-buddy flags false; managedconfiguration.notbackedup LockdownActivationIndicatesCloudConfigurationAvailable false; springboard MCForceShowCloudConfigurationUI false) + mobileactivationd data ark seeded (`/private/var/containers/Data/System/D90C94C4-F94E-4FCF-8A28-A93BE3846D8E/Library/internal/data_ark.plist`, -ActivationState Activated etc.) + MediaToolbox D22/D221/Default SubServerConfiguration StartRecorderServer=false (mediaserverd crash loop: portrait-filter prewarm called NULL GL). **Activation:** ADT /chosen certificate-production-status 0, effective-production-status-ap 0, certificate-security-mode 1, effective-security-mode-sep 1 -> mobileactivationd's native Hactivation branch (Codex `codex/activation/report.md`; alternative 4-byte daemon patch documented there). Fallback image v13; v12 deleted.

**🎉 TOUCH WORKS (boot 0063u on image v13, 2026-10-18 ~13:15 local):** tapping (i) on Setup's Hello opens the device-info sheet; swipe-up is recognised (spinner, then back to Hello - under investigation). Chain: RPMh L11C vote (0062, `bsd/dev/sweet_rpmh.c`) -> GT9896 @0x5d on GENI SE7 (0063 fixed FIFO packing: register address went out byte-swapped) -> sweet_hid_touch -> SweetHIDTouch -> backboardd. Battery icon OK (0062 SweetBattery IOPMPowerSource, static 100 %). **Image v13** (= v12 + CommCenter jobs removed from launchd.plist + `BKNoWatchdogs`=true and `FBLaunchWatchdogExceptions{com.apple.purplebuddy:100}` in /var/mobile/Library/Preferences/com.apple.springboard.plist): Setup no longer killed by the scene-create watchdog (it blocked in CoreTelephony getSubscriptionInfo -> CommCenter, Codex `codex/setup/report.md`; that report also lists how to skip Setup: SetupDone/SetupFinishedAllSteps/SetupVersion=11 in com.apple.purplebuddy.plist + activation check). v9 deleted, fallback = v12. Input latency ~1 min with 1 CPU -> Codex task 11 = SMP via PSCI (`codex/smp/`).

**INPUT WORKS (boot 0060u on a freshly flashed v12, log `logs/boot-0060u.txt`):** power, volume up, volume down reach iOS (PMIC -> sweet_keys.c -> SweetHIDButtons -> backboardd). Power locks/unlocks (screen "off" shows the kernel console because the panel never really turns off). **Device identity fixed: iPhone X** (home indicator, Face-ID-style Setup). Earlier test (0059u, `sweethidtest=15` fake Home presses) advanced Setup from Hello to the language list.
- **0058** HID: `iokit/Kernel/arm/hid/`: IOHIDEventServiceUserClient + IOHIDEventServiceQueue + IOHIDEvent compiled UNCHANGED from Apple IOHIDFamily-1915.140.3 (= exact version of the iOS 16.7 IOHIDLib, clone in `research/iohid-1915`) over our minimal IOHIDEventService (SweetHID.cpp: SweetHIDButtons consumer page 0x0C power 0x30 / vol 0xE9/0xEA / menu 0x40; SweetHIDTouch digitizer collections). C hooks `sweet_hid_key(key, down)` (0 power, 1 vol+, 2 vol-, 3 home) and `sweet_hid_touch(finger, down, x, y)`. HID logs go to IOLog. Boot-arg `sweethidtest=N` = fake Home press every N s.
- **0059** identity: hw.machine/hw.model/hw.target/hw.product from the ADT (macOS-config kernel used to answer "iPad8,6"/"Redmi Note 10 Pro"). mkadt: root compatible `D22AP|iPhone10,3|xiaomi,sweet|...`, model iPhone10,3, target-type D22, `/product` copied from the real D22AP device tree (`research/ipsw-x/d22ap.adt`, extracted from the IPSW, NOT in git), `/buttons home-button-type 2`. Codex report `codex/mg/report.md`: MG ProductType = sysctl **hw.product** (unrecognized -> iPod), HWModelStr = hw.target, HomeButtonType = `/buttons/home-button-type`; disk cache `/private/var/containers/Shared/SystemGroup/systemgroup.com.apple.mobilegestaltcache/Library/Caches/com.apple.MobileGestalt.plist` (keyed by build + UUID only -> stale iPod answers survived; reflashed clean v12 to clear it).
- **0060** drivers by Codex (`codex/input/hw-report.md`): `bsd/dev/sweet_keys.c` (SPMI arbiter v5 observer reads, PON 0x810 bits KPDPWR/RESIN SID0, PM6150L GPIO2 SID4 0xc110; works), `bsd/dev/sweet_touch.c` (GENI SE7 I2C @0xa84000, starts 45 s after boot). Touch result: SE7 fw ok (proto 3) but **0x5d and 0x38 both time out -> touch IC unpowered** (L11C LDO needs an RPMh vote). Codex task 8 = RPMh client (`codex/rpmh/`), task 7 = battery (`codex/battery/`).
- **0061** (CI 39117078444): red status bar "rdar:45025538" = UIKit "No status bar visual provider for screen" (360x800 pt is no real iPhone). AppleCLCD now presents **1125x2436** (iPhone X) and shows the centered 1080x2400; touch mapped the same; ADT canvas 1125x2436. `sweetfb_native=1` reverts.
- Images: `shim/out/shim-boot-0060b.img` (0060 + /buttons ADT `sweet-0060hi.adt`). Next: 0061 image with ADT from current mkadt.

### >>> HANDOFF 2026-10-17 late (read this first) <<<

**STATE: iOS 16.7 Setup.app "Hello" screen is ON THE PHONE** (boot `shim/out/shim-boot-0057u.img` on image v12). Photo `/run/media/dipa/android/ios-sweet-work/MILESTONE-setup-hello-2026-10-17.jpg`. SpringBoard + backboardd + Setup run; nothing crashes in the GUI path. Remaining crash/relaunch loops: installcoordinationd (should be fixed by 0057, unverified), mediaserverd (VirtualAudio removed in v12, unverified), mobileactivationd (~100/boot, not analysed), bluetoothd + fairplayd.H2 relaunch constantly (no hardware).

**What is on the phone now:** userdata = image **v12** (`/run/media/dipa/android/ios-sweet-ipsw/ios16-root-20H392-v12.img` + `.simg` + `.sha256`; v9 kept as fallback, v8/v10/v11 deleted or superseded). Kernel **0057** (`xnu/out-0057`, CI `39067532732`). ADT **`shim/out/sweet-0057hi.adt`** (QEMU twin `research/q0057-hi.adt`). Boot image **`shim/out/shim-boot-0057u.img`**. Boot args: `debug=0xc serial=3 cpus=1 keepsyms=1 -enable_kprintf_spam -noprogress rd=ufsroot0 unentitled_ios_sim_launch=1 ignition_level=1 wdt_test=no_user_checkin ufsrw=1 rootrw=1 launchd_unsecure_cache=1 wdt=-1`.

**Build a phone image** (kernel K, ADT A): `python3 tools/mkpayload.py $K $A shim/out/payload-X.bin --cmdline "$B" && (cd shim && ./build.sh ../shim/out/payload-X.bin && cp out/shim-boot.img out/shim-boot-X.img)` then check `python3 tools/unpack_bootv2.py shim/out/shim-boot-X.img shim/out/check-X && cmp shim/out/check-X/ramdisk shim/out/payload-X.bin`. QEMU smoke test: `python3 tools/mkpayload.py $K research/q0057-hi.adt $S/csq/payloadX.bin --ramdisk $S/csq/root-fork.img --cmdline "debug=0xc serial=3 cpus=1 keepsyms=1 -enable_kprintf_spam -noprogress rd=md0"` + `PATH=~/swift/usr/bin:$PATH python3 tools/qemu-sweet.py ... --secs 40 --kernel $K --fail-on-panic` (S = scratchpad; root-fork.img lives in the session scratchpad csq/ dir and may be gone in a new session).

**Kernel workflow:** edit `research/bt28/xnu/...` (keep the pre-edit copy in `research/preNNNN/`), syntax check `python3 tools/xnu-cc.py research/run28.log research/bt28 <file>`, make `xnu/patches/NNNN-*.patch` with `diff -u pre bt28 | sed` path rewrite, add new/changed files to `research/check-patch-order.py` list, run it (must say applied + MATCH), commit + push -> GitHub Actions `xnu` builds (~8 min) -> `gh run download <id> -R dipa-studio/ios-sweet -n xnu-kernel -D xnu/out-NNNN`. **Repo is PUBLIC since 2026-10-17** (private macOS runner minutes ran out: "recent account payments have failed"); public = free runners. Commit trailer: only `Co-Authored-By: dipa-studio <183933817+dipa-studio@users.noreply.github.com>`.

**Phone workflow (user does buttons, Claude runs commands):**
- Boot test kernel: phone in fastboot -> `fastboot boot shim/out/shim-boot-X.img`. NEVER `fastboot getvar`.
- **Read logs WITHOUT filming:** after a test the user holds Power+VolDown -> fastboot -> `fastboot boot recovery/recovery.img` (OrangeFox, temp) -> wait for `adb shell true` -> `tools/sweet-log-pull.sh /run/media/dipa/android/ios-sweet-work/logs/<name>.txt` (reads the 4 MiB console ring the kernel keeps in the last 1025 blocks of userdata; patch 0047). Then `adb reboot bootloader` brings the phone back to fastboot without the user.
- **Flash a root image:** `fastboot flash -S 512M userdata <img>.simg` (7 min, 25 chunks). After a big flash the Xiaomi ABL fastboot hangs: next `fastboot boot` stalls at "Sending" -> the USER must re-enter fastboot by hand (Power+VolDown). Do not retry commands against the hung ABL. A flash right after `adb reboot bootloader` once failed on chunk 1 (USB protocol error): just retry. User must NOT unplug during flash (once interrupted at 25/25 -> reflash).
- **Edit the phone root without reflashing (same-length only):** find the file's raw offset in the local image (it is one extent; search the image for its first 4 KiB), compare with `adb exec-out dd if=/dev/block/sda34 ...`, then `adb push` changed 4 KiB blocks and `dd of=/dev/block/sda34 seek=... conv=notrunc,fsync`, read back. Recovery kernel has no hfsplus.
- **Pull the whole phone root** (12 min): `adb exec-out "dd if=/dev/block/sda34 bs=1048576 count=16384" > img`; mount ro with udisksctl or `sudo mount -t hfsplus -o loop,ro`. To write into a pulled image: `sudo fsck.hfsplus -fy` first (volume is never cleanly unmounted -> Linux mounts ro even with -o force), then `sudo mount -t hfsplus -o loop,force`.
- Making images: copy latest img with `cp --sparse=always`, mount rw with force, change, `sync; umount`, `sha256sum`, `img2simg`. Keep only the latest image + one fallback on the SSD (/home is ~98% full; big work files live in `/run/media/dipa/android/ios-sweet-work/`, old kernels/images archived in `.../ios-sweet-work/archive/`).

**Diagnostics built into the kernel (all SWEET-only):** persistent console log (0047, boot-arg sweetlog=0 off; flush every ~1 s); `|name| text` copies of /dev/null writes for processes in `sweetnull` (default backboardd,SpringBoard; 0048); `IOK name:` IOKit lookup/open trace for `sweetiolog` (default backboardd,SpringBoard; 0049/0054, 400 lines max); `SWEET Sandbox: proc op N` (0050); `STR ...` heap text dump on SIGABRT/SIGTRAP for `sweetscan` (default backboardd,SpringBoard; 0051/0053) - this is how NSException/BSAssert reasons were found; `SMP name tN pc .. bt ..` user stack sampler for `sweetsample` (default SpringBoard,backboardd; first at 90 s then every 120 s, 40 samples, 16 frames; 0054/0055); `SWEET FB: N swaps` every 1000 swaps; `CRASH name ...` crash reports (0043/0044). Symbolicate cache addresses with `ipsw dyld a2s research/dsc/dyld_shared_cache_arm64 <addr - slide>`; main-binary addresses: addr - mh + 0x100000000.

**Patches added today (0046-0057, all CI-built):** 0046 IOSurface (IOCoreSurfaceRoot) + IOMobileFramebuffer (AppleCLCD on /arm-io/disp0) + arm-io nubs; 0047 persistent log; 0048 /dev/null tee; 0049 IOKit trace; 0050 permissive "Sandbox" MAC policy; 0051/0053 heap text on crash; 0052 RENAME_SWAP via exchangedata on HFS; 0054/0055 sampler, swap counter, AKS selectors 35 (extended device state = 17) and 101; 0056 panel copy from the vsync timer at 10 Hz (sweetfb_hz) instead of every swap; 0057 no config_ext_resolver (ACL group entries resolve without memberd). ADT (tools/mkadt.py): /arm-io/disp0, /chosen/display-scale 3, /chosen/unique-chip-id (synthetic 0x5357454554000001) + chip-id 0x8015 -> IOPlatformUUID A9683613-3704-53F2-95D0-98A8FB574E78. Image v9-v12: /private/var/containers/{Bundle,Data/System,Shared/SystemGroup,Temp}; launchd.plist StandardOut/ErrorPath renamed to ...PatX (pointing jobs at /dev/console stops them launching: EACCES); v12: LastSystemVersion=20H392 in plain /var/mobile/Library/Preferences/com.apple.migration.plist (stops the 1-hour data migration that ran every boot), VirtualAudio.plugin moved to /Library/Audio/Plug-Ins/HAL.disabled/.

**Codex helper** (`codex exec --skip-git-repo-check -m gpt-6.1-sol -c model_reasoning_effort=high -s workspace-write -C /run/media/dipa/android/ios-sweet-work/codex -o OUT "$(cat task.md)" < /dev/null`, run detached with setsid nohup; config already defaults to gpt-6.1-sol high). Reports in `/run/media/dipa/android/ios-sweet-work/codex/`: mediaserverd-report.md, installcoordinationd-report.md (-> 0057), ufs-performance.md (ranked UFS speed plan), **ufs/0058-sweet-ufs-faster.patch** (READY, not yet applied: ufslogsecs default 10 s log flush batching, optional ufscache=1 directional cache ops, optional ufswait=1 spin-then-sleep; syntax-checked, host-stub verified; see ufs/README.md). Apply it as patch 0058 after review.

**Claude safety-classifier note:** several messages about QuartzCore renderer selection / writing an HFS reader tool were cut off by an automatic classifier (false positives, user agrees). Keep those topics short or let them be; they are not blockers now (rendering already works).

**NEXT STEPS (in order):**
1. **Input** (Setup stuck on Hello): touch + power + volume as IOHIDEventService/IOHIDDevice services backboardd matches (log shows backboardd matching IOHIDDevice with DeviceUsagePairs and IOService with HIDServiceSupport=true). Phone hardware: Goodix/Focaltech touch over I2C/SPI (check live DT `dtb/`), buttons via PMIC (pon) and GPIO keys. Start with a fake HID service (e.g. power button via a timer or boot-arg) to learn the ABI, then real drivers.
2. **Device identity**: MobileGestalt reports iPod + Home button. Add /product node / product-type (iPhone10,3, D22AP), device class iPhone, home-button-less (Face ID) properties in mkadt; find exact MG keys (MGIOMFBSupport.c, `IODeviceTree:/product` lookups seen in backboardd trace).
3. **Battery**: AppleSmartBattery/IOPMPowerSource style service (status bar shows empty red battery).
4. Apply Codex 0058 (UFS speed), consider cpus>1, check whether installcoordinationd/mediaserverd loops are gone, analyse mobileactivationd.
5. Hide kernel console over the GUI when not debugging: boot-arg sweetfb_noconsole=1 (but then panics are not on screen).

- **🎉 MILESTONE: iOS GUI ON THE PHONE - Setup.app "Hello" screen (2026-10-17 ~21:30 UTC, boot 0057u on image v12).** Photo: `/run/media/dipa/android/ios-sweet-work/MILESTONE-setup-hello-2026-10-17.jpg` (animated "dobar d(an)" hello lettering, status bar "iPod" + battery icon, bottom "Pritisnite Home za otvaranje" = "Press Home to open" (locale hr), (i) button). Rendered by iOS 16.7 SpringBoard/Setup through CoreAnimation -> backboardd -> kernel IOSurface (IOCoreSurfaceRoot) -> kernel AppleCLCD swaps -> ABL panel memory. What made it: data migration finally skipped (v12: `LastSystemVersion` 20H392 in the plain `/var/mobile/Library/Preferences/com.apple.migration.plist`; ADT `/chosen/unique-chip-id` + `chip-id` for IOPlatformUUID), 0057 (no ext resolver -> ACL containers work), plus everything before (0046 display/IOSurface, 0050 Sandbox policy, display-scale 3, containers dirs, RENAME_SWAP, AKS 35/101, 10 Hz present).
  **Missing (next work, in rough order):**
  - **Input: no touch, no power button, no volume buttons** (no HID drivers; backboardd looks for IOHIDDevice / HIDServiceSupport services). Setup is stuck on "Hello".
  - **Device identity: it thinks it is an iPod with a Home button** (status bar "iPod", "Press Home to open"): MobileGestalt has no product/model identity (no /product node, product-type, etc.) - give it iPhone10,3 / home-button-less (Face ID class) identity.
  - **No battery detection** (no battery/charger/PMIC service; status bar battery shows empty/red).
  - Locale came up Croatian (hr) - harmless.
  - Performance: cpus=1, polled UFS (Codex UFS patch in progress: `codex/ufs/`), backboardd presents at 60 Hz.
- **README refreshed (2026-10-17):** read the full notes and updated the public overview through patch 0045, v7 hardware observations and prepared v8 diagnostics. Documents real Apple userspace, the missing display/IOSurface GUI work, limited security services, highmem, persistent userdata root, current tooling and build examples. Documentation only; no kernel build, tests, flashing or phone boot performed.

- **v11 still migrated (boot 0056u, 20:32 UTC, `logs/boot-0056u-v11.txt`).** On iOS kCFPreferencesCurrentHost lands in the plain plist: all DMEnvironment setters (setLastBuildVersionPref, setUserDataDispositionPref, ...) use CurrentHost and the phone's `/var/mobile/Library/Preferences/com.apple.migration.plist` holds DMUserDataDisposition; datamigrator's XPC service runs with `_RoleAccount: mobile`. **Image v12** = v11 + `LastSystemVersion` = 20H392 added to that plain `com.apple.migration.plist` (keeps DMUserDataDisposition, 501:501 0600) + `/Library/Audio/Plug-Ins/HAL/VirtualAudio.plugin` moved to `/Library/Audio/Plug-Ins/HAL.disabled/` (Codex: stops the mediaserverd SIGSEGV loop; untested). **installcoordinationd loop explained (Codex `codex/installcoordinationd-report.md`):** os_crash "Failed to create data directory" EACCES for `/private/var/containers/Shared/SystemGroup/systemgroup.com.apple.installcoordinationd/Library/InstallCoordination`: `Library`/`Library/Caches` in the container are ACL-only (uid/gid 0xfffffffe, mode 0000, ACE for group GUID ...012B = gid 299 systemusers); with `config_ext_resolver` the kernel asks an identity resolver (memberd/opendirectoryd) that iOS does not run -> EWOULDBLOCK -> ACE skipped -> EACCES. **Patch 0057**: drop config_ext_resolver from FILESYS_BASE (compatibility UID/GID<->GUID mapping is used instead), likely fixes other ACL-protected containers too. Codex task 3: UFS driver performance design (`codex/ufs-performance.md`).
- **mediaserverd SIGSEGV loop explained (Codex report `/run/media/dipa/android/ios-sweet-work/codex/mediaserverd-report.md`):** the fault (FAR 0x390) is in the HAL plug-in `/Library/Audio/Plug-Ins/HAL/VirtualAudio.plugin/VirtualAudio` (ApplyBeamFormerPreference <- VirtualAudio_PlugIn::SetPropertyData <- HALS_AHPPlugIn::ObjectSetPropertyData <- AudioObjectSetPropertyData <- MediaExperience vaemVADSerializationListener): the default virtual audio device ('vdef', VirtualAudioDevice_Default) does not exist (no audio hardware/driver, no /product/audio). Proposed workaround for GUI bring-up: move VirtualAudio.plugin out of /Library/Audio/Plug-Ins/HAL/ in the next root image (untested). v11 reflashed OK after an interrupted flash (USB unplugged at chunk 25/25). Codex task 2: installcoordinationd crash loop.
- **ROOT CAUSE of the endless migration: no IOPlatformUUID (2026-10-17).** datamigrator's `-[DMMigrator isMigrationNeededWithBuildVersion:lastBuildVersion:clientPID:]` gets lastBuildVersion from `-[DMEnvironment lastBuildVersionPref]` = `CFPreferencesCopyValue("LastSystemVersion", "com.apple.migration", kCFPreferencesCurrentUser, kCFPreferencesCurrentHost)` -> a ByHost file. The phone had `/var/mobile/Library/Preferences/com.apple.migration.plist` (only DMUserDataDisposition) and NO `Preferences/ByHost` directory at all. On arm XNU publishes IOPlatformUUID (gethostuuid) only from `/chosen/unique-chip-id` (8 bytes) + `/chosen/chip-id` (4 bytes) (IOPlatformExpertDevice::generatePlatformUUID, called from IOPlatformExpert::start); the SWEET ADT had neither, so every CurrentHost preference write failed. Fix: mkadt adds `unique-chip-id` = 0x5357454554000001 (synthetic) and `chip-id` = 0x8015 -> UUID `A9683613-3704-53F2-95D0-98A8FB574E78` (same SHA1 namespace computation as the kernel). ADT `shim/out/sweet-0057hi.adt`, boot image `shim/out/shim-boot-0056u.img` (0056 kernel + 0057hi ADT, QEMU OK). **Image v11** = v10 + `Preferences/ByHost/com.apple.migration.<UUID upper and lower>.plist` {LastSystemVersion: 20H392} (501:501, dir 0755 files 0600). Flashing v11 2026-10-17 ~20:10 UTC. Codex (gpt-6.1-sol high) analysing the mediaserverd SIGSEGV loop in `/run/media/dipa/android/ios-sweet-work/codex/` (report `mediaserverd-report.md`).
- **v10 did NOT stop the migration (boot 0056n on v10, 19:18 UTC, `logs/boot-0056n-v10.txt`):** datamigrator + migrationpluginwrapper ran again, backboardd drew the progress UI (13000+ swaps in ~5 min). So `com.apple.DataMigration.plist`/LastSystemVersion is not the deciding input. What is known about the decision (datamigrator XPC service `DataMigration.framework/XPCServices/com.apple.datamigrator.xpc/com.apple.datamigrator`, strings): `Migration sentinel present. Migration necessary.` (sentinel `/private/var/datamigrator/migrate`, created and removed by datamigrator itself; absent in v10), `System build version changed from %@ to %@. Migration necessary.` / `...unchanged... not necessary`, `Disposition dictionary with build version %@ is out of date relative to current build version %@`, `SyntheticDidUpgrade`, DMUserDataDispositionManager; previous build source not found yet (not in the binary's plain strings; likely in DataMigration.framework's DMUserDataDispositionManager / preferences domain `com.apple.migration`). backboardd calls `DMPerformMigrationIfNeeded` and holds SpringBoard in `checkInAndWaitForDataMigration` until it returns. NEXT: find where the previous build version / disposition dictionary is stored (disassemble DataMigration.framework DMUserDataDispositionManager + datamigrator's isMigrationNeeded path), write it into the image; or get datamigrator's os_log out (OS_ACTIVITY_DT_MODE needs a launchd env change).
- **Data migration never records completion -> skip it (image v10, 2026-10-17).** Boot 0056n (18:16 UTC, `logs/boot-0056n.txt`, 30 min): 10 Hz panel copies, backboardd still presents at ~60 Hz (107k swaps), SpringBoard still in `BKSSystemShellService _checkIn` at sample 14. Every migration run takes 1+ hour on cpus=1 and repeats each boot. DataMigration decides from `/var/mobile/Library/Preferences/com.apple.DataMigration.plist` key `LastSystemVersion` (vs ProductBuildVersion 20H392); the pulled phone root (21:01 local) had NO such file. **v10** = that pulled phone state + fsck.hfsplus -fy (volume was marked not cleanly unmounted -> Linux mounts it read-only even with -o force; fsck found only hard-link counts + minor volume header, repaired) + `com.apple.DataMigration.plist` {LastSystemVersion: 20H392} (501:501 0600). `/run/media/dipa/android/ios-sweet-ipsw/ios16-root-20H392-v10.img` (+ .sha256, .simg); v8 files deleted, v9 kept as fallback.
- **Repo made PUBLIC (2026-10-17, user request) so GitHub-hosted macOS runners are free:** the 0056 CI run was refused ("recent account payments have failed or your spending limit needs to be increased"). Checked before: no device dumps, serials, IMEI or Apple binaries in the history (.gitignore keeps backup/, dtb/, recovery/, research/ out); commit author emails are public now. 0056 rerun `39056660104` passed -> `xnu/out-0056`, QEMU OK, image `shim/out/shim-boot-0056n.img` booted 18:16 UTC.
- **Boot 0055n (17:16 UTC, ~65 min, `logs/boot-0055n.txt`): migration bar reached 99% in ~30 min (was ~60), then crawled.** Root cause of the slowness: backboardd presents the progress UI at ~58 Hz (**167,000 swaps in ~48 min**) and AppleCLCD copied the full 10 MB frame into the panel on every swap -> ~600 MB/s memcpy on the single CPU (cpus=1), starving everything (polled UFS I/O too). Sampler (16 frames): **SpringBoard waits in `-[BKSSystemShellService _checkIn]`** (synchronous BSXPC call to backboardd, from FBSystemShellInitialize <- SBSystemAppMain) - backboardd holds the system shell check-in until the data migration ends, so the migration is the gate to SpringBoard UI. **Patch 0056**: swap only records the latest swap record; the vsync timer copies it to the panel every 60/sweetfb_hz ticks (default 10 Hz); `SWEET FB: N swaps` every 1000.
- **Boot 0054n (16:53 UTC, ~12 min, `logs/boot-0054n.txt`, patch 0054 sampler):** the data migration runs AGAIN on every boot (it completed once in the 0053s run) - completion is not being recorded. backboardd keeps swapping the progress UI (3700+ swaps in ~10 min, `SWEET FB: N swaps`). Sample during migration: SpringBoard main thread blocked in a synchronous XPC call (`mach_msg2_trap <- dispatch_mach_send_and_wait_for_reply <- xpc_connection_send_message_with_reply_sync <- -[BSXPCServiceConnectionMessage _sendSynchronously:] <- BSXPCServiceConnectionProxy ...`). Unsupported AKS selectors seen: 101 `aks_assert_consume`, 93 `aks_get_internal_info`, 34 `_aks_stash_load` (datamigrator), **35 `aks_get_extended_device_state`** (SpringBoard, chronod, remindd, searchd, symptomsd...). **Patch 0055**: AKS 35 answered like 17 (same DER device state), 101 succeeds; sampler backtraces 16 frames, 40 samples (~80 min).
- **MILESTONE: FIRST iOS PIXELS ON THE PANEL (boot 0053s long run, 15:33 UTC, ~60 min; photos IMG_20261017_183029/183222/183419; log `/run/media/dipa/android/ios-sweet-work/logs/boot-0053s-long.txt`, 407 KB, 1428 flushes).** The iOS data-migration boot screen (Apple logo + progress bar) was shown and the bar advanced to full in ~60 minutes. It is drawn by **backboardd through our kernel display path**: `SWEET SURF: backboardd create id 2/3 1080x2400 fmt 0x42475241 (BGRA) bpe 4 bpr 4352 size 10452992 keys 11`, IOSurface sels 9, 27, 5, 34 and traps 2/3 (lock/unlock), IOMFB SwapBegin (4) / SwapEnd (5, 1132-byte struct) / GetLayerDefaultSurface (3) / 68 / 55, then `SWEET FB: swap N layer 0 surface 2|3 1080x2400 ... a 0,0 1080x2400 b 0,0 1080x2400` alternating (double buffering; only the first 16 swaps are logged). Triggered by `com.apple.datamigrator` (AKS sels 101/93/34 return unsupported) and `com.apple.migrationpluginwrapper`. Probably ProgressUI-style CoreGraphics drawing into IOSurfaces (no GPU used). After the migration: SpringBoard and backboardd stay up (exec once each, no crash), nothing new drawn; crash loops only for mediaserverd, installcoordinationd, mobileactivationd (~108 each in the hour); bluetoothd and fairplayd.H2 relaunch constantly (no hardware). Kernel console text overlays the image (sweetfb_noconsole=1 would hide it).
- **MILESTONE: SpringBoard and backboardd both stay up (boot 0053s on v9, 15:29 UTC, `logs/boot-0053s.txt`).** With /chosen/display-scale = 3: `exec SpringBoard` once, `exec backboardd` once, no CRASH for either; MobileGestaltHelper reads IOMFB size/dot pitch; backboardd opens AppleCLCD (sels 57,15,22,29,33,79,74 as before). No IOSurface creates and no swaps: backboardd keeps polling `IOProviderClass IOAcceleratorES` (-> 0 found) and AGXAccelerator/IOAcceleratorESLegacy - no GPU, so no CoreAnimation renderer yet. Log goes quiet after ~47 s (only 47 flushes): the system idles. NEXT WALL: CoreAnimation rendering without a GPU (CPU path) so the window server produces frames.
- **SpringBoard's invalid mode = scale 0 (boot 0053n, 15:19 UTC, `logs/boot-0053n.txt`, heap scan):** `FBSDisplayMode cannot be configured as requested : <FBSDisplayMode: ...; infxinf@0x (1080x2400/0) 60Hz sRGB SDR>` - pixel size and 60 Hz are fine, scale is 0. libMobileGestalt (MGIOMFBSupport.c, sub_19c560a54) reads `display-scale` (u32, default 0) and `display-rotation` from **IODeviceTree:/chosen**, pixel size via IOMobileFramebufferGetDisplaySize (MobileGestaltHelper sel 8/28 in the log). mkadt now adds `/chosen/display-scale` = 3 (1080x2400 @3x = 360x800 pt). ADT `shim/out/sweet-0054hi.adt` (QEMU `research/q0054-hi.adt`), image `shim/out/shim-boot-0053s.img` = 0053 kernel + 0054hi ADT. Possible catch: MobileGestalt may have cached scale 0 in `/private/var/containers/Shared/SystemGroup/systemgroup.com.apple.mobilegestaltcache/...`.
- **MILESTONE: backboardd survives and opens the display (boot 0052n on v9, 15:07 UTC, `logs/boot-0052n.txt`).** No `CRASH backboardd`. It walks `IODeviceTree:/arm-io` children, matches IOMobileFramebuffer, `open AppleCLCD type 0 -> 0x0`, calls IOMFB selectors 57, 15, 22, 29, 33, 79 (GetBlock, out 1580/40), 74 (SupportedFrameInfo), 12, 6, 27, 17, 84, 50; opens IOCoreSurfaceRoot (sel 13); looks for AGXAccelerator / IOAcceleratorES / IOAcceleratorESLegacy (none, repeatedly), `IODeviceTree:/product` (none, repeatedly), `/buttons`, aop-smart-cover, IOPMrootDomain. No swaps yet. **SpringBoard now gets past display discovery** and dies (sig 5) in `-[FBSDisplayMode _initWithWidth:height:preferredScale:scaleOverride:refreshRate:gamut:hdr:rotation:virtual:validityCheck:]+580` <- `_initWithCADisplayMode:scale:rotation:` <- `FBSDisplayConfiguration _initWithImmutableDisplay:` <- `FBSDisplaySource initWithDisplay:` <- `FBSDisplayMonitor` (slide 0x14504000): "FBSDisplayMode cannot be configured as requested". Checks: width/height >= 2, preferredScale > 0, scaleOverride >= 0, refreshRate non-zero, valid gamut/HDR/rotation. Suspects: refresh rate 0 (IOMFB timing blocks answered with zeros) and/or scale 0 (MobileGestalt main-screen-scale; no /product node in the ADT). **Patch 0053**: heap text scan also on SIGTRAP and for SpringBoard (default sweetscan list backboardd,SpringBoard) to read the exact mode description.
- **Image v9 (2026-10-17) = v8 + `/private/var/containers/{Bundle,Data/System,Shared/SystemGroup,Temp}` (root:wheel 0755; on iOS these live on the data volume, absent from the rootfs) + launchd.plist with StandardOutPath/StandardErrorPath renamed to ...PatX (the in-place phone fix; daemons' stdout reaches the log via the 0048 /dev/null tee).** `/run/media/dipa/android/ios-sweet-ipsw/ios16-root-20H392-v9.img` SHA256 aa9f9139...6e67, `.simg` 12,145,303,864 bytes; written through `sudo mount -t hfsplus -o loop,force`. **Patch 0052** (`xnu/patches/0052-sweet-hfs-rename-swap.patch`, CI `39042761826` -> `xnu/out-0052`, QEMU OK, image `shim/out/shim-boot-0052n.img`): vn_rename falls back to VNOP_EXCHANGE when VNOP_RENAMEX(RENAME_SWAP) returns ENOTSUP for two regular files on one volume (HFS exchange swaps data and cnode descriptors = swap semantics). Flashing v9 started 2026-10-17 ~15:00 UTC.
- **backboardd EXCEPTION FOUND (boot 0051n, 14:41 UTC, `logs/boot-0051n.txt`, patch 0051 heap scan):** `*** Terminating app due to uncaught exception 'NSInvalidArgumentException', reason: '*** -[NSURL initFileURLWithPath:]: nil string parameter'`. First-throw stack (slide 0x337f0000): `+[NSURL fileURLWithPath:]` <- `-[BSSystemContainerForCurrentProcessPathProvider libraryPath]` <- `cachesPath` <- backboardd main+0x1d858 (StartWindowServer, shader cache path). BaseBoard: libraryPath = `BSSystemSharedResourcesDirectoryForIdentifier` = `BSSystemSharedDirectoryForIdentifier(id)` + "/Library"; that calls `container_system_path_for_identifier` (libsystem_containermanager -> `_container_legacy_lookup` -> containermanagerd XPC), which returned NULL (BaseBoard logs "Error getting shared system container ..."). With 0050 the sandbox denials are gone. containermanagerd.log.0 in the pulled (pre-0050) image: "Did not receive any persona attributes", "Expected to find at least one persona", notify_register_dispatch failed 9; `/private/var/containers` does NOT exist in the root image (on iOS it lives on the data volume). usermanagerd does create kernel personas 99/199/1000, but fails to save `/private/var/keybags/usersession.kb` and `persona.kb`: "Failed to atomically swap writing file: Operation not supported (45)" (HFS has no RENAME_SWAP). NEXT: create `/private/var/containers` (and check what containermanagerd needs for system group containers), fix or emulate RENAME_SWAP on HFS, then re-check backboardd.
- **Disk housekeeping (2026-10-17):** /home was at 4 GiB free. Moved (not deleted) `xnu/out-0010..0044` and old `shim/out/*.img`/`payload-*.bin` (everything before 0046) to `/run/media/dipa/android/ios-sweet-work/archive/{xnu,shim-out}` (6.3 GiB); /home now 8.7 GiB free. Large work files (phone-root.img 16 GiB, logs, tracev3 dumps) live in `/run/media/dipa/android/ios-sweet-work/`. **Patch 0051** (`xnu/patches/0051-sweet-crash-heap-strings.patch`, CI `39041440935`): on SIGABRT of a process in boot-arg `sweetscan` (default backboardd) the crash log prints heap text runs as `STR ...` (to find the NSException reason). Boot 0051n 14:41 UTC.
- **Boot 0049n (14:11 UTC, `logs/boot-0049n.txt`, patch 0049 trace): backboardd's IOKit lookups before it dies** (each run): `IODeviceTree:/arm-io/pearl-sep` -> none, matching ApplePearlSEPDriver -> none, `IOService:/IOResources/AppleKeyStore` open OK, matching IOHIDDevice (DeviceUsagePairs) / `HIDServiceSupport` notifications, `usb-drd,t8027` notification; **never any IOMobileFramebuffer / display lookup** - the exception happens before display detection. launchd (tracev3) shows backboardd's mach lookups denied with `error = 159: Sandbox restriction`: com.apple.mobilegestalt.xpc, com.apple.iohideventsystem, com.apple.system.notification_center, com.apple.logd, containermanagerd, ACCHWComponentAuthService, oscard. libsystem_sandbox uses `__mac_syscall("Sandbox", op, arg)` (ops: 1 init, 2 check, 3 note, 4 container path, 5/6/7/8 extensions, 0x15 check_bulk, ...); with no policy named "Sandbox" every call gets ENOPOLICY. **Patch 0050** (`xnu/patches/0050-sweet-sandbox-policy.patch`): built-in permissive MAC policy "Sandbox" in sweet_amfi.c (mpo_policy_syscall returns 0, container/extension ops ENOENT; logs first use of each op as `SWEET Sandbox: proc op N`).
- **Phone root pulled (16 GiB, 12 min, `adb exec-out dd if=/dev/block/sda34`) to `/run/media/dipa/android/ios-sweet-work/phone-root.img` (loop-mounted ro at /run/media/dipa/iOSRoot).** No .ips crash reports. logd tracev3 (Persist, LZ4 `bv41` blocks, decompressed strings in `ios-sweet-work/tracev3/all.txt`): /private/var/db/uuidtext is EMPTY so only launchd's own messages are readable. Findings: v8 launch failure = `Service could not initialize: posix_spawn(/usr/libexec/backboardd), error 0xd - Permission denied` (xpcproxy exit 78) - /dev/console not openable for the mobile user; backboardd[98] spawned `com.apple.MTLCompilerService` before SIGABRT; **launchd denies many mach lookups with `error = 159: Sandbox restriction`** (mediaserverd -> com.apple.backboard.display.services, remoted, mobiletimerd -> sleepd, identityservicesd -> apsd) and **tccd exits OS_REASON_SANDBOX "profile not found"** - no Sandbox kext/profiles on SWEET; likely cause of many daemon crash loops (next wall after the display). CF's uncaught-exception text never reaches stderr for daemons (no CF handler; libc++abi prints only the type). **Patch 0049** (`xnu/patches/0049-sweet-iokit-trace.patch`): `IOK name: ...` console lines for registry path lookups, child iterators, matching (with result count/class), matching notifications and IOServiceOpen of the processes in boot-arg `sweetiolog` (default backboardd), max 400 lines.
- **CONFIRMED: launchd StandardOut/ErrorPath=/dev/console stops backboardd from launching.** After the in-place rename (boot 0047n-b, log `logs/boot-0047n-b.txt`) backboardd launches again and dies as on v7: sig 6, `___pthread_kill <- abort <- demangling_terminate_handler <- _objc_terminate <- std::terminate <- _dispatch_client_callout <- _dispatch_once_callout <- main+0x9334` (window-server dispatch_once). It never opened AppleCLCD or IOCoreSurfaceRoot (no `SWEET FB/SURF: backboardd` lines) -> throws before/at display detection. **Patch 0048** (`xnu/patches/0048-sweet-devnull-tee.patch`, CI `39037749668` -> `xnu/out-0048`, image `shim/out/shim-boot-0048n.img`): writes to /dev/null by processes named in boot-arg `sweetnull` (default `backboardd,SpringBoard`) are printed as `|name| text`. Boot 0048n (13:48 UTC, log `logs/boot-0048n.txt`): only `|backboardd| libc++abi: terminating due to uncaught exception of type NSException` (CF's reason line goes to os_log, not stderr, despite CFLOG_FORCE_STDERR/OS_ACTIVITY_DT_MODE). Next: pull the whole 16 GiB root from recovery (`adb exec-out dd if=/dev/block/sda34`) to `/run/media/dipa/android/ios-sweet-work/phone-root.img` and read ReportCrash .ips files / logd tracev3 for the exception reason.
- **Persistent log WORKS (boot 0047n on v8, 13:31 UTC; pulled from OrangeFox: 70 KB, 111 flushes, `/run/media/dipa/android/ios-sweet-work/logs/boot-0047n.txt`).** In 3 min **backboardd was never exec'd** (v7 ran it), ~70 bare `exec xpcproxy`, SpringBoard loops on FBSDisplayMonitor (no display), mediaserverd sig 11 loop, locationd, lockdownd sig 5. Suspect the v8 plist (StandardOut/ErrorPath=/dev/console on backboardd). **In-place plist edit from recovery (no reflash):** launchd.plist is one extent at image/partition byte offset 0x1e025f000 (195 blocks; verified bytes identical on phone vs local v8 mount); renamed StandardOutPath->StandardOutPatX and StandardErrorPath->StandardErrorPatX (same length, both jobs) in blocks 68 and 105 via `adb push` + `dd of=/dev/block/sda34 seek=... conv=notrunc,fsync`, read back VERIFIED. Phone now differs from local v8 image in those 2 blocks (files in `/run/media/dipa/android/ios-sweet-work/`). Test boot 0047n 13:38:42 UTC. Recovery kernel has no hfsplus (raw block edits only).
- **Patch 0047: persistent console log (CI `39036478663` -> `xnu/out-0047`, QEMU no panic; phone image `shim/out/shim-boot-0047n.img` = 0047 + sweet-0046hi.adt + 0045n cmdline).** `_cnputs` (all console output: kernel printf + daemons' /dev/console) also appends to a 4 MiB ring in sweet_ufs.c; after the UFS partition is ready and writable (ufsrw=1) a thread writes new ring blocks + header to the LAST 1025 blocks (4 KiB) of userdata every ~1 s and SYNCHRONIZE CACHE (prints `SWEET LOG: console log to the last 4100 KiB ...`). Read: phone to fastboot -> `fastboot boot recovery/recovery.img` (OrangeFox) -> `tools/sweet-log-pull.sh OUT.txt` (adb dd of that area + `tools/sweet-log.py`). Not yet verified on the phone. Panics after the last flush are not in it (screen still shows them). 2x font attempt reverted: XNU's v_scale only scales the progress icon.
- **Boot 0046n on v8 (13:05 UTC, VID_20261017_150522_HSR_120):** phone prints `SWEET SURF: IOCoreSurfaceRoot registered` and `SWEET FB: AppleCLCD 1080x2400 stride 4320 at 0x9c000000, default surface 1` (nubs + match work on hardware). Visible userspace: early boot tasks, launchd_cache_loader, `exec SpringBoard`; no `exec backboardd` / `SWEET FB: backboardd` line seen in the readable frames (video blurry). Frame 00:47: lower half of the screen shows OLDER console text (16:01:12) below newer lines -> unconfirmed hint that a swap copied an old snapshot of the panel (CA reads the default/displayed surface = panel memory). SpringBoard still dies in `-[FBSDisplayMonitor _initWithBookendObserver:transformer:]+1160` (sig 5, slide 0x30960000). **Shim: 2x console font** (`shim/loader.c` Video.v_depth scale field = 1) so phone videos are readable; image `shim/out/shim-boot-0046b.img` = 0046n + 2x font.
- **Patch 0046: built-in IOSurface + IOMobileFramebuffer (2026-10-17, offline, NOT phone-tested).** `xnu/patches/0046-sweet-iosurface-iomfb.patch`: new `iokit/Kernel/arm/SweetSurface.{h,cpp}` (IOCoreSurfaceRoot + IOSurfaceRootUserClient: sel 13/0/4/34/35, traps 0-5, wired buffers mapped into the caller, per-client refs) and `SweetFramebuffer.cpp` (AppleCLCD : IOMobileFramebuffer on /arm-io/disp0: sizes, swap = CPU copy of enabled layers into the ABL panel memory, 60 Hz vsync via sendAsyncResult64WithOptions(CanDrop), panel memory published as the default IOSurface, kernel text console paused on the first swap only with `sweetfb_noconsole=1` (default keeps the console: pausing switches it to serial and would hide panics)); SweetPlatformExpert creates nubs for /arm-io children (not gic) attached to the platform expert (IOPlatformDevice::compareName casts its provider to IOPlatformExpert, so nubs under the arm-io nub never matched - first CI build showed that in QEMU). mkadt: /arm-io/disp0 {device_type display-subsystem, compatible sweet,display, canvas-width 1080, canvas-height 2400}. CI `39021572169` -> `xnu/out-0046`. **QEMU** (`research/q0046-hi.adt`, RAM disk init, msgbuf): `SWEET SURF: IOCoreSurfaceRoot registered`, `SWEET FB: AppleCLCD 1080x2400 stride 4320 at 0x9c000000, default surface 1`, init alive, no panic. Phone image **`shim/out/shim-boot-0046n.img`** (SHA256 9c4d2fe9..., CI `39024108588` with the review fixes: swap bounds check, zeroed 64-bit async ref, port release, 1.5 GiB wired budget, ref leak/race fixes; QEMU re-checked) = 0046 kernel + `shim/out/sweet-0046hi.adt` + the 0045n cmdline; boot it on image v8 (backboardd/SpringBoard log to console) and film. Expected new console lines: `SWEET SURF: <proc> create id ...`, `SWEET FB: backboardd sel N ...`, `SWEET FB: swap ...`. Open question for the next wall: QuartzCore's IOMFB server builds its renderer from Metal first (`CAMetalContextCreate`), GLES only when enabled; how the CPU renderer gets selected on a device without a GPU is not yet established.
- **IOSurface values ABI (offline RE, `/run/media/dipa/android/ios-sweet-work/iosurface-values.md`) - TODO in SweetSurface (0046 only accepts and drops values, so IOSurfaceCopyValue always returns NULL):** sel 9 SetValue in = {u32 id, u32 pad, IOCFSerialize([value, key]) or ([dict] = merge)}, sel 0xb RemoveValue in = {u32 id, u32 pad, key\0} (empty key = remove all); both out 4 bytes = new generation, client accepts only (gen+2)|1. Kernel after each change: gen = (gen+2)|1 (odd, never 0) -> state+0x20, serialized size (>=1) -> state+0x28. sel 0xa in {u32 id, u32 0, u8 0}, out {u32 ?, u32 gen, serialized non-bulk dict}; too small -> 0xe00002db + needed size (client retries x16). sel 0x1b in 0x88: bulk struct 0x70 @0, u64 valid size @0x70, u64 changed mask @0x78, u32 id @0x80 -> copy masked fields into state+0x30 (bit0 32B @0, bit1 16B @0x20, bit2 8B @0x30, bits3-10 1B @0x38..0x3f, bits11-14 24B @0x40/4B @0x58/8B @0x5c/1B @0x64).
- **IOMFB display matching confirmed (offline RE, `/run/media/dipa/android/ios-sweet-work/iomfb-match.md`):** the framework never matches on "AppleCLCD"; any registered IOMobileFramebuffer subclass works. `iomfb_match_callback` reads only `dfr`/`AppleTV`/`external` (CFBoolean, service itself, no parents); internal main display = all absent/false (type 0, name "primary"). Display count = /arm-io children whose device_type starts with "display-subsystem" (count 0 -> CreateDisplayList returns NULL; more nodes than services -> 30 s wait). IOMobileFramebufferOpen fails only on IOServiceOpen failure; canvas-width/height read as 4-byte CFData from the IOService-plane parent (optional). CopyProperty = IORegistryEntrySearchCFProperty on the service only. Patch 0046 (disp0 node, `external`=false, AppleCLCD : IOMobileFramebuffer) fits all of this.
- **IOMobileFramebuffer swap + notification ABI (2026-10-17, offline).** Swap record = fb+0x18, **0x46c bytes**, zeroed by SwapBegin and sent whole by `kern_SwapEnd` = IOConnectCallStructMethod(sel 5, rec, 0x46c, no output). **SwapBegin** = sel 4, no input, 1 scalar out = swap id (stored at rec+0x50). `kern_SwapSetLayer(fb, layer<4, IOSurfaceRef, CGRect a, CGRect b, flags)`: rec+0x54+4*layer = **IOSurface id**; rec+0x104 bit layer = layer enabled (rec+0x108 bit cleared); rect a (int x,y,w,h, scaled) at rec+0x64+16*layer, rect b at rec+0xc4+16*layer; rec+0x114+4*layer = transform from flags&0xf; flag bits 5/31/6/7/8/9 set bytes rec+0x2ca/0x2cc/0x2e3/0x2e5/0x2e6/0x467+layer. A NULL surface only sets the enable bit with zero id. SwapWait = sel 6 scalars [swap id, timeout, 0].
  - **Notifications**: `IOMobileFramebufferScheduleWithDispatchQueue`/`GetRunLoopSource` create an IONotificationPort and `IOConnectSetNotificationPort(conn, type, port, 0)` (kernel `registerNotificationPort`). `kern_EnableNotifications(fb, type, cb, ctx)` = **sel 72 scalars [NotifyCallbackFuncs[type], fb, type, 0]** -> the kernel keeps an async reference {port, func, refcon=fb} per type and fires it with `sendAsyncResult64`. Types: 0 HotPlug, 1 Power, 3 FrameInfo (args[0] = mask of 31-bit keys, args[1] u32, then values), 4 CRC, **5 Vsync**: 6 args, each a 32-bit half in a u64 slot: (ts lo, ts hi), (t2 lo, hi) passed through the time-ingest helper, (t3 lo, hi); the framework then calls the client's vsync callback(fb, ts, t2', t3, ctx). Vsync callbacks are dropped while the notification port has queued messages.

- **IOSurface.framework user-client ABI reversed (2026-10-17, offline, step 2 of the GUI plan).** `ipsw dyld disass research/dsc/dyld_shared_cache_arm64 --image IOSurface` (selector scan script: scratchpad `selscan.py`).
  - Connect (`_iosConnectInitalize`, pthread_once): `IOServiceGetMatchingService(IOServiceNameMatching("IOCoreSurfaceRoot"))`, retried with sleep(1) up to 241 times (a missing service stalls every client ~4 min, no crash); `IOServiceOpen(type 0)`; then **sel 13** (no inputs, struct out 0x18 bytes = `_ioSurfaceLimits`) and requires u16 at out+0x16 == 1 (ABI version); out+0 = offset/plane-base alignment mask, out+4 = bytes-per-row alignment mask (used as (x+m)&~m), +0..+0x14 also copied into IOSurface remote-method init, otherwise logs and closes the connection.
  - **Create = sel 0**: scalar in [parent id or 0], struct in = `IOCFSerialize(props, kIOCFSerializeToBinary)` (OSUnserializeBinary format; keys IOSurfaceWidth/Height/BytesPerRow/BytesPerElement/PixelFormat/AllocSize/PlaneInfo/CacheMode/IsGlobal/...), struct out **0xa68 bytes** ("lock result"). **Lookup = sel 4**: scalar in [id], same struct out. LookupFromMachPort = sel 0x22 (scalar in [port name]); CreateMachPort = sel 0x23 (scalar in [id, options], scalar out [port name]).
  - Lock result (copied to client+0x68, size 0x68 + planes*0x80, min 0xe8): 0x00 u64 base address **mapped in the caller's task**; 0x08 u64 task VA of a per-surface shared state page (+0 u64 registry id, +8/+0xa u16 bound accel ids, +0xc u32 seed, +0x14 u8 tiled, +0x20 u32 value generation, +0x24 YCbCr matrix, +0x28 u32 non-bulk values size, +0x2d u8 displayable, +0x2e u8 sysmem-only, +0x30 0x70 bytes bulk attachments); 0x10 u64 task VA of timestamp page (4 u64 indexed timestamps, +0x20 detach code); 0x18 u32 surface id; 0x1c u32 alloc size; 0x20 width; 0x24 height; 0x28 bytes per row; 0x2c buffer offset; 0x30 pixel format; 0x34 u32 (dcache flush length); 0x38 plane count; 0x40 u16 bytes/element; 0x42 u8 element width; 0x43 u8 element height; 0x44 cache mode; 0x4c u8 subsampling; 0x4d u8 prohibit-use count; 0x50 parent id; 0x54 slice count; 0x58 u64 trace id; 0x60 u64 protection options; planes[n] at 0x68+n*0x80 (+0 width, +4 height, +8 bytes/row, +0xc offset, +0x14 size, +0x18 u16 bpe, +0x1a/+0x1b u8 element w/h, +0x1c u8 component count, +0x1d address format, +0x54 u8 compression type (non-zero -> no CPU base address)).
  - **Traps** (IOConnectTrapN -> `IOUserClient::getTargetAndTrapForIndex`): 0 IncrementUseCount(id, category), 1 DecrementUseCount(id, category), 2 **Lock**(id, options, &seed_out), 3 **Unlock**(id, options, &seed_out), 4 Release(id), 5 Release after a failed create/lookup setup (id).
  - Other selectors: 5 SetYCbCrMatrix, 6 WrapClientImage, 7 WrapClientMemory, 9 SetValue (serialized), 0xa UpdateNonBulkValueCache (struct in 9), 0xb RemoveValue, 0xc BindAccel, 0x11 SetSurfaceNotify (async), 0x12 RemoveSurfaceNotify, 0x13 Log, 0x14 SetPurgeable, 0x15 SetOwnership, 0x16 SetTiled, 0x18 SetTimestamp, 0x19 GetTileFormat, 0x1a CopyDataValueBytes, 0x1b SetBulkAttachments (struct 0x88), 0x1e/0x2e-0x31 (via outlined helpers), 0x1f SetCompressedTileDataRegionMemoryUsed, 0x20 GetGraphicsCommPageAddress, 0x21 SetIndexedTimestamp, 0x24-0x26/0x2d IOSurfaceAccelerator, 0x27-0x29 shared events, 0x2a SignalEvent, 0x2b Set/InitDetachModeCode, 0x2c SetOwnershipIdentity, 0x32-0x34 data properties.
  - => SWEET kernel service: class/name **IOCoreSurfaceRoot** + IOSurfaceRootUserClient; minimum = sel 13, 0, 4, 9/0xa/0xb (values), traps 0-5, 0x22/0x23 later for cross-process surfaces (CA sends surfaces to backboardd by mach port). Memory: IOBufferMemoryDescriptor per surface, mapped into each task with createMappingInTask; ids from a global table.

- **Image v8: daemon logs on the console.** `tools/patch-launchd-plist.py IN OUT LABEL...` rewrites launchd.plist (binary, plistlib): renames every `_PanicOnCrash` to `_PanicOnCrasX` and gives the listed jobs `StandardOutPath`/`StandardErrorPath` `/dev/console` (devfs console is 0622, writable by mobile) plus `OS_ACTIVITY_DT_MODE=YES` (os_log mirrored to stderr) and `CFLOG_FORCE_STDERR=1`. v8 = v7 + that plist for com.apple.backboardd and com.apple.SpringBoard, written through the mount (796310 bytes, root:80 0644), SHA256 in `ios16-root-20H392-v8.img.sha256`, `.simg` ready; boot with `shim/out/shim-boot-0045n.img`. Goal: see backboardd's uncaught exception text and the window server's display probing. ODDITY (unresolved): the v5 raw-image rename at offset 0x1e025f000 is present in the v5-v7 image bytes, but the plist read through a Linux mount of v7 still had the original `_PanicOnCrash` keys; filefrag shows the file as one extent. Never patch file contents through raw offsets again; write through the mount.
- **IOMobileFramebuffer.framework reversed (step 1 of the GUI plan).** `ipsw dyld disass research/dsc/dyld_shared_cache_arm64 --image IOMobileFramebuffer`.
  - Display discovery (`IOMobileFramebufferCreateDisplayList` -> `getDisplayListNumber`): iterates children of `IODeviceTree:/arm-io`, counts nodes whose `device_type` is "display-subsystem" or "ext-display-subsystem" (or `compatible` "paravirtualizedgraphics,gpu"); then `iomfb_populate_display_infos` adds an IOServiceAddMatchingNotification(IOServiceFirstMatch, **IOServiceMatching("IOMobileFramebuffer")**) and runs the run loop up to 30 s until that many services matched. `iomfb_match_callback` reads service properties `dfr`, `AppleTV`, `external` (CFBoolean) and names displays (external ones "%s-%d").
  - `IOMobileFramebufferOpen(service, task, type, &fb)`: `__ioMobileFramebufferAlloc` (CFPreferences com.apple.iokit.IOMobileGraphicsFamily: canvas_width/height, override_display_width/height, override_panel_width/height, benchmark, enable_ktrace), `IOServiceOpen(service, task, type)` (GetMainDisplay passes type 0), `getEDTProperty` reads `canvas-width`/`canvas-height` from the service's IODeviceTree parent, then fills a table of `kern_*` function pointers.
  - User client selectors (`kern_*` -> IOConnectCall*): 3 _kern_GetLayerDefaultSurface[ScalarMethod_stub]; 4 _kern_SwapBegin[ScalarMethod_stub]; 5 _kern_SwapEnd[StructMethod_stub]; 6 _kern_SwapWaitWithTimeout[ScalarMethod_stub] _kern_SwapWait[ScalarMethod_stub]; 7 _kern_GetID[ScalarMethod_stub]; 8 _kern_GetDisplaySize[ScalarMethod_stub]; 10 _kern_SetTVOutMode[ScalarMethod_stub]; 11 _kern_SetWSSInfo[ScalarMethod_stub]; 12 _kern_RequestPowerChange[ScalarMethod_stub]; 13 _kern_EnableStatistics[ScalarMethod_stub]; 14 _kern_SetFlags[ScalarMethod_stub]; 15 _kern_SetDebugFlags[ScalarMethod_stub]; 16 _kern_SetTVOutSignalType[ScalarMethod_stub]; 17 _kern_SetGammaTable[StructMethod_stub]; 18 _IOMobileFramebufferIsMainDisplay[ScalarMethod_stub]; 19 _kern_SetWhiteOnBlackMode[ScalarMethod_stub]; 20 _kern_SwapSignal[ScalarMethod_stub]; 22 _kern_SetDisplayDevice[ScalarMethod_stub]; 23 _kern_SetDigitalOutMode[ScalarMethod_stub]; 24 _kern_GetHDCPDownstreamState[StructMethod_stub]; 25 _kern_GetDigitalOutState[ScalarMethod_stub]; 26 _kern_printDisplayRegs[ScalarMethod_stub]; 27 _kern_GetGammaTable[StructMethod_stub]; 28 _kern_GetDotPitch[ScalarMethod_stub]; 29 _kern_GetDisplayArea[StructMethod_stub]; 30 _kern_EnableDisableDithering[ScalarMethod_stub]; 31 _kern_SetUnderrunColor[ScalarMethod_stub]; 33 _kern_EnableDisableVideoPowerSavings[ScalarMethod_stub]; 34 _kern_SetVideoDACGain[ScalarMethod_stub]; 35 _kern_SetLine21Data[ScalarMethod_stub]; 41 _IOMobileFramebufferEnableMirroring[ScalarMethod_stub]; 42 _IOMobileFrameBufferGetMirroringCapability[StructMethod_stub]; 43 _IOMobileFramebufferSetRenderingAngle[StructMethod_stub]; 44 _IOMobileFramebufferSetMirrorContentRegion[StructMethod_stub]; 47 _kern_HDCPSendRequest[ScalarMethod_stub]; 48 _kern_HDCPGetReply[ScalarMethod_stub]; 49 _kern_SurfaceIsReplaceable[ScalarMethod_stub]; 50 _kern_SetBrightnessCorrection[ScalarMethod_stub]; 51 _kern_SetColorRemapMode[ScalarMethod_stub]; 52 _kern_SwapCancel[ScalarMethod_stub]; 53 _IOMobileFramebufferSetCanvasSize[ScalarMethod_stub]; 54 _IOMobileFramebufferGetMatrix[Method_stub]; 55 _IOMobileFramebufferSetMatrix[Method_stub]; 56 _IOMobileFramebufferKernelTests[StructMethod_stub]; 57 _kern_GetColorRemapMode[ScalarMethod_stub]; 66 _kern_SPLCSetBrightness[ScalarMethod_stub]; 67 _kern_SPLCGetBrightness[ScalarMethod_stub]; 68 _kern_SetParameter[Method_stub]; 69 _kern_SwapSetColorMatrix[StructMethod_stub]; 72 _kern_DisableNotifications[ScalarMethod_stub] _kern_EnableNotifications[ScalarMethod_stub]; 73 _kern_ChangeFrameInfo[ScalarMethod_stub]; 74 _kern_SupportedFrameInfo[Method_stub]; 75 _kern_FactoryPortal[StructMethod_stub]; 77 _kern_GetCurrentAbsoluteTime[ScalarMethod_stub]; 78 _kern_SetBlock[Method_stub]; 79 _kern_GetBlock[Method_stub]; 80 _kern_GetLinkQuality[ScalarMethod_stub]; 81 _kern_SwapCancelAll[ScalarMethod_stub]; 82 _kern_GetProtectionOptions[ScalarMethod_stub]; 83 _kern_CopyLayerDisplayedSurface[ScalarMethod_stub]; 84 _kern_SetContrast[StructMethod_stub]; 85 _kern_GetBufBlock[Method_stub]; 86 _IOMFBGainEncoderFinishEncoding[Method_stub]; UNKNOWN {}
  - => Kernel needs: an `/arm-io` child node with device_type "display-subsystem" (+ canvas-width/height) and an IOService of class **IOMobileFramebuffer** (subclass name match) attached under it, opened with type 0, implementing at least GetDisplaySize(8), IsMainDisplay(18), GetID(7), GetLayerDefaultSurface(3), SwapBegin(4)/SwapEnd(5 struct)/SwapWait(6), Enable/DisableNotifications(72), frame info(73/74), CopyLayerDisplayedSurface(83), plus IOSurface for the swapped buffers. NEXT: CoreAnimation's AppleDisplay/IOMFBDisplay usage of these (constructor, first swap, vsync), then IOSurface.framework's IOSurfaceRoot selectors.
- **GUI PLAN (decided 2026-10-16): CPU rendering + kernel IOMobileFramebuffer.** User: CPU rendering is fine for now (goal = prove the GUI runs), may later research an Apple-style GPU driver for the Adreno 618 -> keep display output and renderer separable. QuartzCore findings (symbols from the cache's .symbols subcache: `ipsw dyld symaddr research/dsc/dyld_shared_cache_arm64 --image QuartzCore`; strings: `ipsw dyld macho ... QuartzCore --strings`):
  - Renderers: `sw_new_context` (CA::OGL::SWContext, full CPU renderer incl. blur, images, IOSurface-backed surfaces, make_buffer_current(WindowServer::Surface)), `gles_new_context`, `metal_new_context`, `new_null_context`. Env knobs include CA_ENABLE_OGL, CA_DISPLAY_TYPE, CA_FORCE_LOCAL_SERVER, CA_FORCE_TIMER, CA_CANVAS_WIDTH/HEIGHT, CA_MAIN_DISPLAY_SCALE/ORIENTATION, CA_DISABLE_RENDER, CA_ALWAYS_RENDER (selection logic not traced yet).
  - `-[CAWindowServer _detectDisplays]` (0x1884e3150) iterates static tables `open_funcs`/`count_funcs` = AppleCLCDDisplay, AppleRGBOutDisplay, AppleWirelessDisplay only; each `count()` = `display_count_of_type(IOMFBDisplayType)` over **`IOMobileFramebufferCreateDisplayList()`**, `open(i)` = `create_display_of_type` -> `CA::WindowServer::AppleDisplay(CFString name, ..., IOMFBDisplayType)` (an IOMFBDisplay driven by IOMFBServer: vsync_callback, frame_info_callback, swaps). `CA::WindowServer::VirtualDisplay` exists but is never auto-detected (explicit API only). => the main display MUST come from an IOMobileFramebuffer kernel service.
  - NEXT: reverse IOMobileFramebuffer.framework: IOMobileFramebufferCreateDisplayList / IOMobileFramebufferOpen (service matching, display type property), the user-client selectors used by IOMFBServer (display size/modes, swap begin/set-layer/end with IOSurface ids, vsync notifications), then the IOSurface kernel side (IOSurfaceRoot user client: create/lookup/lock, memory mapping) that both IOMFB swaps and CA surfaces need. Kernel: SWEET IOMobileFramebuffer service that copies the swapped IOSurface to the 1080x2400 framebuffer at 0x9c000000.
- **logd fixed; backboardd = DISPLAY WALL (boot 0045n on v7, 21:08:57 UTC, frames VID_20261016_230850 00:55-01:28, slide 0x4c3ec000, `research/crash-0045n-v7.txt`).** No `CRASH logd` any more; new daemons run (runningboardd, WirelessRadioManagerd, networkserviceproxy, dasd, cloudpaird, magicswitchd, atc, askpermissiond, ManagedSettingsAgent, containermanagerd uses AKS 0/17). New: locationd sig 11 at CFRunLoopAddSource+132 (NULL source) from its main+0x2af138 in a dispatch_once. **backboardd** sig 6: abort <- std::terminate <- _objc_terminate <- dispatch_once <- main+0x9334 = the "start %{public}@..." wrapper (0x100009264) for **"window server"** (block 0x10000a770 -> dispatch_once body 0x10001d7f0 = StartWindowServer): MTLSetShaderCachePath, `[CAWindowServer serverWithOptions:@{kCAWindowServerDisableUpdatesOnMainDisplay: @YES}]`, `setRendererFlags:`, **`mainDisplay`** -> `displayId` -> `[CADisplay displayWithDisplayId:]`, setWindowServerDisplay:, bounds, pointScale, currentMode, preferredScale, nativeOrientation, touchScales... With no display, mainDisplay is nil and it throws. (HID system and GS start fine before it.) SpringBoard dies on the same missing display (FBSDisplayMonitor). QuartzCore display backends (from the cache's .symbols subcache, `ipsw dyld str`): `CA::WindowServer::AppleCLCDDisplay` (IOMobileFramebuffer hardware) and **`CA::WindowServer::VirtualDisplay`** (open(), new_server, clone_update). `CA_DISPLAY_TYPE` and `CA_FORCE_LOCAL_SERVER` strings exist in QuartzCore but have no direct xref (likely read via a table of CA_* env names). NEXT: find how CA::WindowServer::Server enumerates displays (IOMobileFramebuffer services vs VirtualDisplay / CA_DISPLAY_TYPE) and choose: (a) kernel IOMobileFramebuffer service + IOSurface, or (b) a VirtualDisplay rendered by CA's CPU path (CA::OGL::SW) and copied to the framebuffer.
- **watchdogd + CommCenter + identityservicesd fixed (boot 0045n on v6, 20:41:30 UTC, frames VID_20261016_224133 00:39-01:13, slide 0x20fec000).** `SWEET WDT: watchdogd sel 0 in 0/0 out 1/0 -> ok`, no watchdogd/CommCenter/identityservicesd crashes (CommCenter/identityservicesd now call AKS 0/17/7). usermanagerd boot task runs (UMD_INIT creates primary session uid 501 "mobile", personas 99 System and 199 Default registered with the kernel); `Failed to atomically swap writing file /private/var//keybags/usersession.kb: Operation not supported (45)` (HFS lacks the atomic swap rename; non-fatal so far). Remaining: SpringBoard (FBSDisplayMonitor, no display), backboardd (uncaught exception), mediaserverd, lockdownd (crash inside obfuscated code, main+0x4c1b4?), logd. **logd**: main+0x18160 = `BUG IN LIBTRACE: Failed to migrate directory` from 0x10001801c(dir 0): 0x100016538 requires the dir to exist with uid/gid/mode from the table at 0x10002df14 (0: /private/var/db/diagnostics 272:272 0751, 1: /private/var/db/uuidtext 272:272 0755, 2: /private/var/db/diagnostics/timesync 272:272 0755) plus a `.migrated` file, else XPC "operation 6" to a helper and crash. **Image v7** = v6 + those dirs/markers (also in mkiosroot.sh), SHA256 in `ios16-root-20H392-v7.img.sha256`, `.simg` ready. Boot with `shim/out/shim-boot-0045n.img`.
- **Exit-reason text works (boot 0044n, frames VID_20261016_221726 00:32-00:53, slide 0x22d5c000).** CommCenter/identityservicesd: `couldn't dlopen libobjc-trampolines.dylib: dlopen(/usr/lib/libobjc-trampolines.dylib, 0x0106): tried: '/usr/lib/libobjc-trampolines.dylib' (no such file, not in dyld cache)`: the file only exists in the OS cryptex and dyld does not search cryptexes at ignition_level=1. 19 cryptex files have no root counterpart (OS: DriverKit dyld cache + .symbols, VisualTestKit, libffi-trampolines, libobjc-trampolines, libstdc++ 6.0.9 + 2 symlinks; App: SafariSupport.bundle, AuthenticationServicesAgent, com.apple.Safari.History, passwordbreachd, safarifetcherd, webbookmarksd, webinspectord, webpushd) -> hard-linked (symlinks copied: Linux hfsplus cannot hard-link symlinks); `tools/mkiosroot.sh` does it generically. watchdogd still crashed: the `-wdt_no_pmu` / `/arm-io/wdt no-pmu` check (0x10000a01c) only runs when os_variant_has_internal_diagnostics; otherwise 0x100009b18 looks up IOServiceMatching("IOService") + IOPropertyMatch {IOPMUPrimary: 1} (NSConstantDictionary) and crashes if absent, then IORegistryEntrySetCFProperty(boot stage 0xff) (failure only logged). Patch **0045**: IOWatchdog sets IOPMUPrimary = 1 and accepts setProperties; CI `38961814194` -> `xnu/out-0045`. **Image v6** = v5 + the 19 cryptex links, SHA256 7c610c6a...297a, `ios16-root-20H392-v6.simg` (full flash needed). Boot image `shim/out/shim-boot-0045n.img` (0045 + sweet-0044hi.adt). Still open: SpringBoard (no display), backboardd (uncaught exception, reason none), mediaserverd (Fig NULL dict), logd (main+0x18160), lockdownd (main+0x4c1b4).
- **System survives daemon crashes (boot 0043p, video frames VID_20261016_215006 00:25/00:42/00:54).** With the v5 plist patch no panic: launchd keeps launching (runningboardd, powerd, tccd, healthd, peopled, cryptexd, routined, aksd, mediaremoted, familynotificationd, nanoprefsyncd, navd, cloudpaird, passd, amsaccountsd, accessoryupdaterd, wcd ...). Shared cache slide that boot 0x406b4000 (`research/crash-0043p.txt`). watchdogd still crashed at main+0xb82c from the PMU step: `-wdt_no_pmu` is only honored when os_variant_has_internal_diagnostics; customer builds read `no-pmu` from IODeviceTree:/arm-io/wdt (IORegistryEntrySearchCFProperty) -> mkadt adds /arm-io/wdt {no-pmu}. **cryptexd** sig 6: abort_with_payload <- os_crash_fmt <- `__darwin_arm_secure_boot_chip.cold.7` ("panic: failed to get crypto algorithm") <- `_img4_chip_select_personalized_ap`: reads /chosen use-ddi-secure-boot, allow-ecid-mismatch, crypto-hash-method ("sha1" | "sha2-384"), /chosen/asmb lp-smb0/1 -> mkadt adds crypto-hash-method "sha2-384". **identityservicesd** sig 6 = same `_objc_fatal` in imp_implementationWithBlock as CommCenter (block trampolines; message needed). lockdownd sig 5 at main+0x4c1b4. Patch **0044**: crash report adds `CRASH name reason ns N code X: text` (exit reason description = abort_with_payload text). CI `38959096811` -> `xnu/out-0044`, QEMU OK. Image `shim/out/shim-boot-0044n.img` = 0044 + `shim/out/sweet-0044hi.adt` (wdt no-pmu, crypto-hash-method) + cmdline (wdt=-1, no -wdt_no_pmu).
- **First symbolicated daemon crashes (boot 0043u on journaled v4, 19:38:53 UTC; video frame chat image 36; transcribed in `research/crash-0043u.txt`; shared cache slide 0x40d60000 for every process).** (Gemini's video transcription invented values, use frames only.) `tools/sweet-crash.py research/dsc/dyld_shared_cache_arm64 x research/crash-0043u.txt`:
  - **watchdogd** pc main+0xb82c (`_os_crash` trap helper) from 0x100009bb0 = set PMU boot stage via IORegistry (no PMU) -> fix: boot-args `wdt=-1 -wdt_no_pmu` (Apple's own test mode writes "%s wdt=-1 -wdt_no_pmu"; watchdogd logs "skipping setting PMU boot stage because -wdt_no_pmu found in boot-args or no-pmu found in EDT"). Kernel effect of wdt=-1: sched hygiene debug off, zone_exhausted_timeout -1 (harmless).
  - **SpringBoard** sig 5 in `-[FBSDisplayMonitor _initWithBookendObserver:transformer:]+1160` <- `+[FBDisplayManager sharedInstance]` <- `FBSystemShellInitialize` <- `SBSystemAppMain`: no main display. GUI WALL: display service (IOMobileFramebuffer / CoreAnimation display).
  - **backboardd** sig 6: abort <- std::terminate <- _objc_terminate (uncaught exception; message not shown).
  - **CommCenter** sig 6: `_objc_fatal` in `imp_implementationWithBlock` (from `+[_PFRoutines initialize]`, CoreData): objc block trampolines cannot be allocated -> likely kernel gap (trampoline page remap); will hit many processes.
  - **mediaserverd** sig 11: CFDictionaryGetValue(NULL) in FigNotificationListenerStartNotifications (routing session manager).
  - **logd** sig 5 at its main+0x18160 (bt main+0x9dfc); lockdownd sig 5 (not yet symbolicated).
  - Image v5 = v4 + launchd.plist (`/System/Library/xpc/launchd.plist`, contiguous at image offset 0x1e025f000, 1456980 bytes) with the 7 `_PanicOnCrash` keys renamed `_PanicOnCrasX` in place (raw image patch, no metadata change) -> `diff-v4-v5.simg` = 7 blocks; v5 SHA256 78f96974...185a. Boot image `shim/out/shim-boot-0043p.img` = 0043 + `wdt=-1 -wdt_no_pmu`.
- **0043 console crash reports (QEMU verified); image `shim/out/shim-boot-0043u.img`; NEXT: flash v4 + boot 0043u.** Boot 0042u (video photo IMG_20261016_211646): short exec lines work; watchdogd crashes with NO `SWEET WDT:` line (fails before its first IOWatchdog call: lookup or IOServiceOpen, or elsewhere); lockdownd, SpringBoard, mediaserverd, CommCenter, identityservicesd, backboardd, watchdogd all crash repeatedly ("Too many corpses being created" = corpse limit, no crash reports). AKS callers: lockdownd (0, 7), imagent/sleepd (0, 17, 7), backboardd (0, 17), UserEventAgent (0, 7, 102, 103 -> unsupported). Patch **0043**: `sweet_crash_log` (osfmk/kern/exception.c, called from proc_prepareexit for crash exits on the current proc) prints `CRASH name[pid] sig S code (exc<<32|code) sub X slide SR mh MH`, `CRASH name pc lr sp fp far`, `CRASH name bt` (10 fp frames); AKS sel 103 notify_state_is_set -> 0. CI `38954520419` -> `xnu/out-0043`. QEMU test: init forks, child `brk #1`: `CRASH launchd[2] sig 5 code 0x600000001 sub 0x1000004f0 slide 0x0`, pc correct, parent keeps running (pid 1 crashes panic before proc_prepareexit, so test with a child). `tools/sweet-crash.py CACHE ROOT [report]` symbolicates typed-in CRASH lines (`ipsw dyld a2s` with addr - slide; main binary offsets = addr - mh + 0x100000000).
- **v3 reflashed 18:50-18:55 UTC (`research/flash-userdata-v3b.log`, 24/24 OKAY); 0042u booted 19:01:17 UTC on the clean disk (`research/boot0042u-2.log`), SLOW MO VID pending (watchdogd failure reason).** ABL hangs on the first `fastboot boot` after every big flash; user re-enters fastboot. User gave standing approval to reflash/boot without asking (memory standing-flash-approval). Commits now end with `Co-Authored-By: dipa-studio <183933817+dipa-studio@users.noreply.github.com>` (user request; never a Claude trailer).
  - watchdogd flow: connect_to_kext (0x100005408): IOServiceGetMatchingService("IOWatchdog") fails -> "failed to discover" + _os_crash; IOServiceOpen(type 1) fails -> "IOServiceOpen failed with error : 0x%x" + _os_crash. Then sel 0 (out 1 scalar): 0 -> "userspace monitoring disabled", 0x100009bb0, sleep 2, exit(0); nonzero -> "userspace monitoring enabled", normal operation.
  - **Image v4 (JOURNALED):** `tools/mkiosroot.sh` now does `mkfs.hfsplus -J`, mounts with `-o loop,force`, adds the /System/Library/Caches/com.apple.dyld hard links (44) and /private/var/keybags/systembag.kb (0700/0600 root). Built from the IPSW dmgs (OS 087-86698-044, SystemOS 087-86593-047, AppOS 087-86715-047) -> `/run/media/dipa/android/ios-sweet-ipsw/ios16-root-20H392-v4.img` SHA256 fba4aeae...ec0f9 + `.simg`. Header: attr 0x80002100 (unmounted, journaled), journal info block 129, journal 8 MiB at 532480 flagged need-init. Linux `fsck.hfsplus -n` reports "Volume header needs minor repair" on any fresh journaled volume even after -y (quirk). QEMU: 64 MB journaled test root (`rd=md0 rootrw=1`, 0042 kernel): `hfs: Initializing the journal (joffset 0x3000 sz 0x80000)` -> mounted -> init runs, no panic. NEXT: flash v4 (full), boot 0042u.
- **SPRINGBOARD STARTS (boot 0041u 18:39:53 UTC, photo IMG_20261016_204142).** backboardd, bluetoothd, fairplayd.H2, SpringBoard (pid 111, crashed: "Too many corpses"), xpcproxy run; `SWEET AKS: backboardd sel 0 -> 0`, `sel 17 in 1/0 out 0/4096 -> 0`. Panic: watchdogd[113] exited, namespace 2 subcode 5 (SIGTRAP = its _os_crash): watchdogd crashes on purpose when IOServiceGetMatchingService("IOWatchdog") fails ("connect_to_kext() unexpectedly failed") or IOServiceOpen(type 1) fails ("IOServiceOpen failed with error"); IOWatchdog DOES register (QEMU msgbuf: `SWEET WDT: IOWatchdog registered`), cause not on screen yet -> need video. Note `wdt_test=no_user_checkin` makes watchdogd log "detected testing boot-args to not run, exiting" (path not reached here?). **HFS CORRUPTION:** `hfs_swap_BTNode: offset #0 invalid (0xBC1D) (blockSize 0x2000 numRecords 81)`, `node=19677 fileID=4` (catalog), `hfs_mark_inconsistent` repeated. Likely cause: non-journaled HFS + unclean panics while writing (0038e wrote a 2.7 GB core then panicked; every boot since ends in panic). Plan: reflash v3 (clean), longer term HFS journaling. Patch **0042**: one short `exec NAME` console line instead of the 3-line "Allowing spawn of iOS binary" notice; CI `38949451276` -> `xnu/out-0042`; image `shim/out/shim-boot-0042u.img` (same cmdline as 0041u).
- **LAUNCHD DAEMONS RUN (boot 0039u, 18:29:13 UTC, photo IMG_20261016_203052).** With `launchd_unsecure_cache=1` all boot tasks pass and launchd starts LaunchDaemons (pids > 100: identityservicesd 114 and lockdownd 106 crash, "Too many corpses being created"). Fatal: `watchdogd: ERROR: failed to discover watchdog KEXT service` -> exit (namespace 2 = signal, subcode 5) -> `_PanicOnCrash` panic. watchdogd: IOServiceMatching("IOWatchdog"), IOServiceOpen type 1, IOConnectCallScalarMethod sel 0/1 (check in)/3/4 (disable/enable userspace monitoring)/5, IOConnectCallStructMethod sel 2 (1 KiB in) and 9 (small out); VM path ("detected virtual machine environment and no watchdog KEXT found, exiting...") only when it detects a VM. Console also flooded with `hfs: set hardlink bit on vol=iOSRoot cnid=321318` (Linux-made hard links lack kHFSHasLinkChainBit; repaired only in memory on each lookup). Patches **0040** (`iokit/Kernel/arm/SweetWatchdog.cpp`: IOWatchdog + IOWatchdogUserClient, all selectors succeed with zeroed outputs, each logged once as `SWEET WDT: ...`) and **0041** (sweet_hfs hfs_catalog.c: the three link-repair printfs limited to 8 per boot); CI `38948245372` PASSED -> `xnu/out-0041` (QEMU regression OK). Image `shim/out/shim-boot-0041u.img` (0041 + sweet-0038hi.adt + ufsrw rootrw + launchd_unsecure_cache=1) booted 18:39:53 UTC (`research/boot0041u.log`), photo pending.
- **v3 FLASHED + keybag passes; next wall AMFI (launchd_cache_loader).** User said "flash, nothing to lose": `fastboot -S 512M flash userdata ios16-root-20H392-v3.simg` 17:51:52-17:57:01 UTC, 24/24 chunks OKAY (`research/flash-userdata-v3.log`). userdata = v3 (SHA256 fa84274c...22df) until the next rw boot. ABL fastboot then hung ("Sending" forever, `reboot bootloader` timed out) until the user re-entered fastboot by hand (common Xiaomi ABL crash). Boot 0038e 18:06:15 UTC (`research/boot0038e-3.log`), photos IMG_20261016_200812/200838: keybag OK, then boot tasks tzinit (`Bad zoneinfo link`, resets to system partition, OK), finish-restore, finish-demo-restore, sysstatuscheck, prng_seedctl (`failed to load kernel prng seed`, `failed to load virtual random (-147)`, AllowCrash), auearlyboot, then **launchd_cache_loader: `abort: Unable to find AMFI`** -> 2.7 GB core written to /cores in 91 s -> launchd panic `launchd_cache_loader[22] exited -- exit reason namespace 7 subcode 0x1`. launchd_cache_loader: SecStaticCodeCheckValidity of /System/Library/xpc/launchd.plist with detached .sig, then IOServiceMatching("AppleMobileFileIntegrity") + IOServiceOpen type 0 + IOConnectCallMethod sel 6 (1 scalar = 1, struct in = cdhash) = trust the cdhash, then sends the cache to launchd. Boot-arg `launchd_unsecure_cache=1` skips signature + AMFI ("Using unsecure cache"); the value is parsed with strtoul base 10 (helper 0x100002da8), so a path = 0 = off: boot 0039w (18:17:13 UTC, `=/System/Library/xpc/launchd.plist`, photo IMG_20261016_202008) still aborted `Unable to find AMFI` (core dump now skipped: `Failed to generate core file ... error 14`, so 0039 works). Image `shim/out/shim-boot-0039u.img` uses `launchd_unsecure_cache=1`. Patch **0039**: do_coredump = 0 on SWEET (kern.coredump sysctl still works); CI `38945267341` -> `xnu/out-0039` (_do_coredump now in __common). Image `shim/out/shim-boot-0039w.img` = 0039 + sweet-0038hi.adt + ufsrw rootrw + `launchd_unsecure_cache=/System/Library/xpc/launchd.plist`. TODO later: real AppleMobileFileIntegrity IOService (sel 6 trust cdhash etc.).
- **Image v3 ready, awaiting user "flash".** Boot 0038w 17:38:10 UTC, photo (chat image 30): `SWEET AKS: keybagd sel 0 -> 0x0`, `sel 14 out 1/0 -> 0x0` (x2), `MKB_INIT: mount is with NO CPROTECT ... does not support Data Protection`, `System Keybag loaded`; then keybagd still opens /private/var/keybags/systembag.kb (0x100012d3c, for BackupKeyBagKeys) -> ENOENT, `no-effaceable-storage` not set -> `Can't load the keybag. tears in rain... Time to die` -> `FATAL KEYBAG ERROR: kb_load` -> reboot -> Halt/Restart Timed Out panic. Fix: ADT `/defaults/no-effaceable-storage` (mkadt.py; `shim/out/sweet-0038hi.adt`, `research/q0038-hi.adt`, QEMU OK) + file `/private/var/keybags/systembag.kb` (0600 root, dir 0700; XML plist {KeyBagKeys: data}). **v3 image** `/run/media/dipa/android/ios-sweet-ipsw/ios16-root-20H392-v3.img` = v2 + that file, fsck OK, SHA256 fa84274c...22df; `ios16-root-20H392-v3.simg` (img2simg: zero blocks become FILL chunks, so a full flash overwrites every block the rw boots changed). Flash: `fastboot -S 512M flash userdata ios16-root-20H392-v3.simg`, then boot `shim/out/shim-boot-0038e.img` (0038 + sweet-0038hi.adt + ufsrw=1 rootrw=1).
- **0038 AppleKeyStore (CI 38938744130 PASSED -> `xnu/out-0038`; QEMU msgbuf: `SWEET AKS: AppleKeyStore registered (no passcode, unlocked)`; phone image `shim/out/shim-boot-0038w.img` booted 17:38:10 UTC, `research/boot0038w.log`, photo pending).** QEMU full kernel log trick (fb.txt is only the last screen): `llvm-nm KERNEL | grep _msgbufp` -> `--hmp "x /1gx ADDR"` gives struct msgbuf address (static, 0xfffffe0007b56678 on 0038) -> `--hmp "x /3gx STRUCT"` gives bufc (3rd quad) -> `--hmp "memsave BUFC 0x20000 \"FILE\""` (quote the file name), `tr -d "\0" < FILE`. Same inputs give the same addresses. Boot 0037w 17:08:35 UTC, photo IMG_20261016_191052: bindfs fixed mount; mount-phase-1/2 pass; `cc_fips_test` boot task: all corecrypto FIPS POST tests PASSED in userspace; then keybag boot task `keybagd --init`: `MKB_INIT: FATAL KEYBAG ERROR: failed to load system bag`, `Could not get options entry from the device tree` (x2, IODeviceTree:/options = NVRAM, non-fatal), `REBOOTING INTO RECOVERY MODE` -> reboot -> panic `Halt/Restart Timed Out @IOPlatformExpert.cpp:884` (no restart path on SWEET).
  - keybagd (static libaks): load_devicebag (0x100012c30) calls aks_get_system (sel 14, 0-1 scalar in, 1 out) and loads /private/var/keybags/systembag.kb only if the result is 0xe00002f0 (NotFound); any other error -> fatal; SUCCESS -> skip the file (userspace-reboot path). systembag.kb is a plist {KeyBagKeys}; decrypted with effaceable storage unless IODeviceTree:/defaults has `no-effaceable-storage`. Image has no /private/var/keybags. has_data_protection: statfs of /private/var; no cprotect on our HFS -> device-bag volume mapping skipped.
  - libaks connection: IORegistryEntryFromPath / IOServiceMatching("AppleKeyStore"), IOServiceOpen type 0, then selector 0 (no args) must succeed.
  - **AppleKeyStore selector map (iOS 16.7 AppleKeyStore.framework, via `ipsw dyld disass`):** 0 open, 2 create_bag, 3 save_bag, 4 unload_bag, 5 set_system_with_passcode, 6 load_bag, 7 get_lock_state (1 in, 1 out; bit 2 = unlocked since boot), 9 unlock_device, 10 wrap_key, 11 unwrap_key, 12 unlock_bag/test_stashed_kek, 13 lock_bag, 14 get_system, 15 change_secret_se, 16 internal_state, 17 get_device_state (1 in, struct out <=4K: DER SET of SEQUENCE{UTF8 key, INTEGER}: ss state, sls lock_state (MKBGetDeviceLockState returns it), sb backoff, sbo, sfa failed attempts, sfao, sgs generation, sas assertions, sgpe grace, srcd countdown, sr reserved), 18 recover_with_escrow_bag, 19 obliterate_class_d, 20 drain_backup_keys, 21/22 set/clear_backup_bag, 23 get_bag_uuid, 24 rewrap_key_for_backup, 26/27 assert_hold/drop, 30/31 set/get_configuration, 33-37 stash, 38 auth_token_create, 40 generation, 41 fdr_hmac_data, 42 verify_password, 43 _aks_operation, 44 remote_session, 49/50 signing keys, 51/53/54 stash enable/persist/escrow, 55 unload_session_bags, 57/58 remote peer, 59-62 smartcard, 63 migrate_s_key, 65 set_keybag_for_volume_with_cookie_persona, 66/67 sync bags, 68 copy_volume_cookie_persona, 69-73 se_*, 74-79/84/85/99 fv_* (FileVault/VEK), 80/81 absinthe, 82 make_public_backup_bag, 83 drop_auxiliary_auth, 86 kext get/set options, 87 invalidate_bag, 88-91/94/95/106/107 se_*, 92 lower_iteration_count, 93 get_internal_info, 96-98/117 keybag_persona create/list/delete, 100/101 assert promote/consume, 102/103 notify_state set/is_set, 104 fairplay, 105 change_secret_epilogue, 108 delete_xart_leak, 110-113 backup volume, 114 sealed_hashes_set, 115 prewarm_sps, 118-128 AKSIdentity*/AKSGetLastUser.
  - Patch **0038**: `iokit/Kernel/arm/SweetKeyStore.cpp` (class AppleKeyStore on IOResources, IOUserClientClass AppleKeyStoreUserClient; personality in KernelConfigTables.cpp): 0/4/5/9/12/13/26/27/55/102 success, 14 -> handle 0, 7 -> 0x4, 17 -> DER state (ss 4, sls 0), others kIOReturnUnsupported; logs `SWEET AKS: <proc> sel N arg0 in a/b out c/d -> ret` for every call.
  - Tools: shared cache copied to `research/dsc/` (git-ignored; ipsw needs a writable dir for its .a2s symbol cache); `ipsw dyld disass research/dsc/dyld_shared_cache_arm64 --image AppleKeyStore|MobileKeyBag`; scratchpad `annot2.py BIN DIS FIXUPS` annotates llvm-objdump output with strings and import names (`ipsw macho info --fixups`).
- **0037 bindfs (phone boot 0037w pending photo).** Boot 0036mw 16:57:47 UTC, photo IMG_20261016_190102: WRITABLE ROOT WORKS: `/dev/ufsroot0 on / (hfs, local, noatime)` after mount_hfs update (GetMasterBlock EBUSY harmless), coredump of mount written to /cores (rw). Then `mount: failed to mount /private/preboot/5CBE3601.../usr/standalone/firmware -> ...: Operation not supported by device (19)` -> exit 74 -> launchd panic `mount[2] exited`. Cause: the macOS-derived config had nullfs but no bindfs (ENODEV = unknown fs type). Caller passes env 0 -> bind not required, ENOENT (missing source dir) tolerated. Patch **0037** adds `bindfs` to FILESYS_BASE in MASTER.arm64.sweet; CI `38936550483` -> `xnu/out-0037` (bindfs_vfsops present; QEMU probe regression OK). Image `shim/out/shim-boot-0037w.img` (0037 + sweet-0036hi.adt + ufsrw=1 rootrw=1) booted 17:08:35 UTC (`research/boot0037w.log`). NOTE: userdata has now been modified by rw boots; it no longer equals the v2 image, so sparsediff with v2 as OLD is not safe any more (full reflash or a new baseline needed).
- **0036 phone: launchd boot tasks run; mount -P 1 needs /chosen/boot-manifest-hash.** Boot 0036hr 16:15:32 UTC, photo IMG_20261016_185236: platform check passes; fsck boot task runs (`fsck: not booting main or diagnostic OS. Skipping fsck on OS container`); mount-phase-1: `failed to get filesystem info` x2 (no IODeviceTree:/filesystems/fstab, non-fatal), `mount: data volume missing, but not required in env: 0`, mount_hfs update of /: `GetMasterBlock: Error 16 opening /dev/ufsroot0` (EBUSY, mounted block dev, non-fatal) then mount() EROFS (read-only boot) -> `mount: / failed with 1`; then `failed to get boot-manifest-hash` -> errx exit 66 -> launchd panic `mount[3] exited`. /sbin/mount: fn 0x100005f90 reads IODeviceTree:/chosen boot-manifest-hash (hex), bindfs-mounts /private/preboot/<HEX>/usr/standalone/firmware (ENOENT tolerated unless required). `tools/mkadt.py` now adds `boot-manifest-hash` = SHA-384("sweet boot manifest") (5CBE3601...5205). ADTs `shim/out/sweet-0036hi.adt`, `research/q0036-hi.adt` (QEMU probe OK, csops 0x26000001). Image `shim/out/shim-boot-0036mw.img` (0036 + new ADT + ufsrw=1 rootrw=1), booted 16:57:47 UTC (`research/boot0036mw.log`): FIRST WRITABLE BOOT of userdata (restore source: v2 image on SSD).
- **0036 CS_SIGNED (phone boot 0036hr pending photo).** Phone boot 0035hr 2026-10-16 15:57:02 UTC (`research/boot0035hr.log`, photo IMG_20261016_180249): highmem works on hardware; shared cache maps (trust-cache warnings only), Apple launchd runs (`Darwin Bootstrapper Version 7.0.0`, `entering ondemand mode`), starts boot task fsck, then userspace panic `boot task is not a platform binary (fsck, /sbin/fsck)`. launchd+0x3fea0: `csops(pid, CS_OPS_STATUS)` must have bit 0x04000000. Cause: nothing set CS_SIGNED (AMFI does it in vnode_check_signature), so csproc_get_blob() returns NULL for every process and csops never reports CS_PLATFORM_BINARY (also breaks per-process cdhash/entitlement queries). QEMU probe init (`csops` status printer, scratchpad csq/) on 0035: `0x02000001`; patch **0036** (`*cs_flags |= CS_SIGNED` in the SWEET AMFI hook), CI `38929635791` -> `xnu/out-0036`: `0x26000001`. Images `shim/out/shim-boot-0036hr.img` / `-0036hw.img` (same cmdlines as 0035). 0036hr booted 16:15:32 UTC (`research/boot0036hr.log`). Next launchd boot tasks (embedded __config plist): fsck -qL and mount -P 1/2 (RequireSuccess); no /etc/fstab on the image.
- **0035 ENTITLEMENTS + PLATFORM BINARIES (QEMU verified).** `xnu/patches/0035-sweet-amfi-entitlements-platform-binaries.patch`: new `iokit/Kernel/arm/SweetEntitlements.cpp` (OSObject subclass: OSDictionary from OSUnserializeXML of the signature's XML entitlements + original XML for CS_OPS_ENTITLEMENTS_BLOB); `bsd/kern/sweet_amfi.c` answers queryEntitlementBoolean/String(+WithProc, string also matches array members), copyEntitlementAsOSObject(+WithProc, retained), asdict (retained), get_xml (kalloc_data copy); built-in MAC policy "SWEET AMFI" (registered from bsd_init before vfs/exec) with mpo_vnode_check_signature: every signed binary on the MNT_ROOTFS mount gets CS_PLATFORM_BINARY (stand-in for AMFI's static trust cache: iOS system binaries are ad-hoc, cd_flags 0x2, platform byte 0), and attaches entitlements ONLY for the writable copy (cs_blob != csb_ro_addr; revalidation passes the RO blob). LESSON: first version attached in adjustContextWithoutMonitor -> QEMU `unable to adjust OSEntitlements context without monitor: 53` because ubc_cs_convert_to_multilevel_hash (4K-page signatures on 16K kernel) sets csb_entitlements_blob = NULL; ALL iOS 16 binaries (launchd, backboardd, SpringBoard) use 4K code pages, so this would have broken launchd on the phone. Boot-arg `sweet_amfi_debug=1` logs `SWEET AMFI: <ident>: N entitlements (test: ...)`. `tools/mkinit.py OBJ OUT [ENTS.plist]` adds an XML entitlements blob (special slot -5; default output byte-identical). QEMU `research/q0035-ent` (RAM disk `research/root-hfs-ent.img`, init with 3 test entitlements, highmem): `org.sweet.init: 3 entitlements (test: bool 1 string 1 array 1)` then init PID 1. MAC policies loaded: 0034 = 1, 0035 = 2 (QMP `mac_policy_list`). CI `38909807230` -> `xnu/out-0035`. Phone images: `shim/out/shim-boot-0035hr.img` (highmem, ro), `-0035hw.img` (highmem, +ufsrw=1 rootrw=1), `-0035r.img` (low mem fallback).
- **PHONE TEST ORDER (updated):** 0035hr -> if instant reset, 0035r -> then 0035hw.

- **HIGHMEM: XNU in the upper DDR bank, ~3.95 GiB (was 1.2 GiB).** Live FDT memory = <0x80000000 2G> + <0x1_00000000 0xfcc00000>; all fixed reserved-memory carve-outs are in the low bank (highest: ramdump_fb 0xaf000000, rmtfs ~0xfde01000), dynamic pools have alloc-ranges <= 0xffffffff, UFS node has no `iommus` (Linux DMAs anywhere). `tools/mkadt.py --highmem` sets /chosen dram-base 0x100000000 dram-size 0xfcc00000; `tools/mkpayload.py` now takes phys_base/mem_size from the ADT (default payloads byte-identical, verified); `tools/qemu-sweet.py` sizes -m from the payload (8G for highmem). Patch **0034** (`0034-sweet-ufs-dma-above-4g.patch`): UFS refuses DMA memory above 4G without UFSHCI CAP.64AS (bit 24), logs `DMA at 0x...`. CI `38905889883` success -> `xnu/out-0034`. **QEMU verified** (`research/q0034-hi`, ADT `research/q0034-hi.adt` --qemu --highmem, HFS RAM disk): phys_base 0x100000000, init PID 1 heartbeat, no panic; `max_mem` = `mem_size` = 0xfcc00000 read via QMP (`research/q0034-hi-mem`). Phone images: `shim/out/shim-boot-0034hr.img` (read-only) / `-0034hw.img` (+ufsrw=1 rootrw=1), ADT `shim/out/sweet-0034hi.adt` (asmb SIP + sweet-ufs + highmem). PHONE RISK: unknown runtime TZ/XPU protection in the upper bank would show as an instant reset; fall back to 0033r/w. Watchdog ruled out for the overnight reset: msm-watchdog bark is 20 s (qcom,bark-time 0x4e20) yet panic screens stay up for many minutes.

- **Offline research 2026-10-16 (user away, phone unavailable). Images rebuilt** `shim/out/shim-boot-0033r.img` / `-0033w.img` now also carry `wdt_test=no_user_checkin`. NEXT ON PHONE: boot 0033r (expect past in6_nigroup), then 0033w (first writes: rw root fixes HFS link-chain bits itself and gives /var for launchd sockets /var/run/syslog, /var/run/lockdown.sock).
- **launchd.plist** (`/System/Library/xpc/launchd.plist`, compiled; 532 daemons, 66 RunAtLoad/KeepAlive, list in scratchpad `early-daemons.txt`). `_PanicOnCrash` daemons: containermanagerd/usermanagerd (InternalOnly), lockdownd/remoted/trustd/remotepairingdeviced (AutomationOnly), **watchdogd unconditional** (KeepAlive SuccessfulExit=false). watchdogd needs IOKit `IOWatchdog` kext service; if absent it exits only when `kern.hv_vmm_present` (ADT `/defaults/vmm-present`, hvg_sysctl.c) or with boot-arg `wdt_test=no_user_checkin` ("detected testing boot-args to not run, exiting"; reads kern.bootargs). Using the boot-arg (vmm-present would change many daemons; keep as an option).
- **GUI path research (QuartzCore in the shared cache, `ipsw dyld str CACHE STR`, ~10 s/search):** CA::WindowServer has IOMFBServer/IOMFBDisplay (Apple DCP/IOMobileFramebuffer), AppleCLCDDisplay, AppleRGBOutDisplay, **VirtualServer/VirtualDisplay** and **MemorySurface**, EAGLServer. Renderers: CA::OGL::MetalContext, GLContext and a **CPU software rasterizer CA::OGL::SW** (samplers/blend modes; "image is too large for software renderer"). Env knobs: `CA_ENABLE_OGL`, `CA_DISPLAY_TYPE`, `CA_FORCE_LOCAL_SERVER` (249 CA_* vars). Hypothesis (unverified): backboardd's render server could run a VirtualServer/MemorySurface with the SW renderer and we copy the surface to the ABL framebuffer -> needs disassembly of CA::WindowServer server creation. Expected other GUI walls: IOSurface (closed-source kext; needs a reimplementation), IOMobileFramebuffer user client, IOHID touch events, AppleKeyStore/keybag (SEP) for lock state, MobileGestalt answers (AppleCLCD etc.).

- **0032r RESULT (boot 05:07:50 UTC, `research/boot0032r.log`, photo IMG_20261016_071200): SHARED CACHE MAPPED, LAUNCHD RUNS.** With SIP relaxed (ADT asmb) the `not in trust cache` lines are only warnings for every subcache (.31 ... .42.dyldlinkedit); no SIP rejection; libSystem loads; launchd configures networking (`skip attaching fsw to lo0 using legacy TX model`) -> kernel data abort far 0x28 in `SHA1Init` (symbolized as sha1_init) from `in6_nigroup` (IPv6 on lo0): g_crypto_funcs NULL. Kernel addresses are unslid: `~/swift/usr/bin/llvm-symbolizer --obj=KERNEL ADDR` works directly.
- **0032** BearSSL SHA-1 (`0032-sweet-bearssl-sha1.patch`), **0033** BearSSL SHA-384/512 (`0033-sweet-bearssl-sha384-sha512.patch`, BearSSL ctx stored in SHA512_CTX, static-asserted to fit; ubc_subr.c uses SHA-384 for code directories). `0020-stage-bearssl.sh` now also stages hash/sha1.c, hash/sha2big.c, codec/{dec,enc}{32,64}be.c. CI `38854909053` success (0032-only run `38854802073` superseded). Kernel `xnu/out-0033` (SHA1Init -> _br_sha1_init verified by disassembly; nm symbols have a leading underscore). Images (ADT sweet-0032): `shim/out/shim-boot-0033r.img` (read-only), `shim-boot-0033w.img` (+ufsrw=1 rootrw=1). Still NULL g_crypto_funcs users: des, chacha20poly1305, rsa, aesxts, rand, flow_divert.
- `research/check-patch-order.py` now skips patches touching CI-staged sweet_hfs sources (0031) instead of stopping.

- **0031r RESULT (boot 05:03:52 UTC 2026-10-16, `research/boot0031r.log`, photo IMG_20261016_070508): SHARED CACHE FOUND.** dyld now opens `dyld_shared_cache_arm64` (v2 image hard links), kernel refuses to map it: `shared_region: ... map(...'dyld_shared_cache_arm64'): not in trust cache` -> `vnode is not SIP-protected` (vm_unix.c: macOS arm64 path needs trust cache, else root-owned + SF_RESTRICTED unless CSR_ALLOW_UNRESTRICTED_FS) -> `dyld cache '(null)' not loaded: syscall to map cache into shared region failed` -> libSystem not loaded -> coredump to /cores fails error 30 (EROFS) -> panic initproc failed -> "MACH Reboot" (spins; screen kept). Lots of `hfs: set hardlink bit on vol=iOSRoot cnid=... linkid=...` spam (Linux-made hard links lack the link-chain bit; read-only mount cannot persist the fix). FIX: ADT `/chosen/asmb` with `lp-sip0`=0x6f (u64; incl. CSR_ALLOW_UNRESTRICTED_FS) and `lp-sip1`=1 (unauthenticated root), `tools/mkadt.py` -> `shim/out/sweet-0032.adt`. Images with kernel 0031: `shim/out/shim-boot-0032r.img` (read-only) and `shim-boot-0032w.img` (+ufsrw=1 rootrw=1).

- **2026-10-16 morning:** userdata now = **v2** image (`diff-v1-v2.simg` flashed 21:06:50 UTC 2026-10-15, OKAY, `research/flash-userdata-diff-v2.log`); future diffs use `ios16-root-20H392-v2.img` as OLD. Booted `shim-boot-0029k.img` (ignition_level=1) right after (`research/boot0029k-v2.log`); **no photo** (user asleep). Next morning the phone was in PixelOS recovery = some hardware reset (ABL then booted Android, which cannot use userdata). OBSERVATION: our kernel cannot reset the SoC itself (`PE_halt_restart` is never set; reboot/halt print "MACH Reboot"/"CPU halted" and spin), so the reset came from outside XNU: Qualcomm watchdog or a TZ/XPU violation. Unknown which; re-boot 0029k and watch/video until the reset. Do NOT tap factory reset/format data in recovery (would wipe the iOS image).
- **0030** (`xnu/patches/0030-sweet-ufs-writes.patch`, CI `38852655542`): UFS WRITE(10) + read-modify-write for partial 4 KiB blocks + SYNCHRONIZE CACHE (DKIOCSYNCHRONIZE), only with boot-arg `ufsrw=1`; `ufs_write_blocks` re-checks partition bounds before every write (only place data goes out).
- **0031** (`xnu/patches/0031-sweet-read-write-root.patch`, CI `38852837176`): boot-arg `rootrw=1` clears MNT_RDONLY before the root mount (no data volume on sweet: /private/var is on the root; image has no /etc/fstab); Apple HFS accepts a dirty non-journaled ROOT read-write on SWEET (logs "mounting dirty non-journaled root read-write"). Later: journaled HFS for crash safety. Kernel `xnu/out-0031` (CI `38852837176` success, 5m31s; 0030 run cancelled by the newer push). Boot images (phone ADT `sweet-0028.adt`, ramdisk byte-matched): `shim/out/shim-boot-0031r.img` = 0029k args (read-only, ignition_level=1) and `shim/out/shim-boot-0031w.img` = same + `ufsrw=1 rootrw=1`. PLAN: boot 0031r first and film until the reset (diagnose overnight reset), then 0031w (first ever writes to userdata; v2 image on the SSD is the restore source). `research/check-patch-order.py` cannot check 0031 (staged sweet_hfs files are not in its index); CI stage scripts run first, so CI is the check.

- **ignition_level=1 result** (boot 21:01:39 UTC, `research/boot0029k.log`, photo IMG_20261015_230308): preboot/cryptex stages skipped (need >= 2/3), `dylib_cache: finding shared cache on system volume: ignition level = 1, search root fd = 4, subpath = System/Library/Caches/com.apple.dyld/` -> not found -> `ignition boot failed: 19` -> no shared cache -> libSystem not loaded. FIX IN PROGRESS: image v2 = copy of the flashed image + `/System/Library/Caches/com.apple.dyld/` with HARD LINKS to the 44 cryptex cache files (no extra space; avoids symlink-following doubts), then `tools/sparsediff.py ios16-root-20H392.img ios16-root-20H392-v2.img diff.simg` and flash only the diff. Boot with `ignition_level=1` (shim-boot-0029k.img).
- **ignition_level=0 result** (boot 20:58:07 UTC, `research/boot0029j.log`, photo IMG_20261015_230037): all stages skipped as "ignition level insufficient" (hello/preboot/cryptex1 sniff >= 2, select os cryptex path/graft >= 3, **dyld_cache >= 1**), `ignition boot failed: 89`, "ignition partially disabled", then same `Library not loaded: /usr/lib/libSystem.B.dylib (no such file, no dyld cache)`. => dyld gets the shared cache directory from ignition's dyld_cache stage. Next: `ignition_level=1` (`shim/out/shim-boot-0029k.img`) to skip preboot/cryptex stages but run dyld_cache; its log "finding shared cache on %s ... subpath = %s" will show where it searches. If it searches rootfs /System/Library/Caches/com.apple.dyld, add a symlink there (image rebuild; consider a diff-only sparse flash tool to avoid rewriting 12 GB).
- **APPLE dyld/launchd RUNNING (libignition) with `unentitled_ios_sim_launch=1`** (boot 20:53:24 UTC, `research/boot0029i.log`, photo IMG_20261015_225617): kernel prints "Allowing spawn of iOS binary ... boot-arg set to true"; `shared_region: ... check_np ... vm_shared_region_start_address() failed` (no region yet, normal); dyld's built-in **libignition** (Darwin Ignition Sequence 1.0.0, libignition-51~1974; prints rd=ufsroot0, hardware target sweet, ignition level 0x5, platform 0x2, boot spec local, 7 stages): `hello from launchd.1` -> `preboot: mounting preboot` -> `failed to lookup preboot: 25` (ENOTTY: looks for a separate Preboot volume by role) -> ignition fails -> dyld `Library not loaded: /usr/lib/libSystem.B.dylib ... (no such file, no dyld cache)` -> launchd exit -> panic initproc failed. dyld boot-args found via strings: `ignition_level`, `ignition_force_dylib_root` (forced rootfs/livefs/cryptex fallback), `ignition_halt_after`, `ignition_live_app_graft`; dyld cache search paths include /System/Cryptexes/OS, /System/Volumes/Preboot/Cryptexes/OS/, /private/preboot/Cryptexes/OS/ (present in our image). Next try `ignition_level=0` (`shim/out/shim-boot-0029j.img`).
- **APPLE launchd EXECUTED FROM UFS (2026-10-15).** Flashed iOS image: `img2simg` -> `ios16-root-20H392.simg` (12.1 GB) then `fastboot -S 512M flash userdata ...simg` (24 chunks, 307 s, `research/flash-userdata-ios16.log`; a raw-image flash was killed by earlyoom at 2.6 GB RSS - always flash the sparse image). ABL fastboot hung on getvar after the flash; power+vol-down fixed it. Boot 0029u 20:49:04 UTC (`research/boot0029u-ios16.log`), photo IMG_20261015_225134: `hfs: mounted iOSRoot` -> load_init_program /sbin/launchd -> panic `unexpected SIGKILL of launchd (CS_KILLED) with reason -- namespace 9 code 0xe` = OS_REASON_EXEC / EXEC_EXIT_REASON_WRONG_PLATFORM: our kernel is XNU_TARGET_OS_OSX, iOS-platform binaries are "alien" and refused unless spawn attr platform set or DEVELOPMENT TUNABLE `unentitled_ios_sim_launch`. Next try: same kernel, cmdline + `unentitled_ios_sim_launch=1` (`shim/out/shim-boot-0029i.img`). LONGER TERM: macOS-config kernel marks iOS maps alien (vm_map_mark_alien) and differs from iOS in many policies; an iPhoneOS-config kernel build may eventually be needed.
- **iOS 16 ROOT IMAGE BUILT:** `/run/media/dipa/android/ios-sweet-ipsw/ios16-root-20H392.img` (16 GiB case-sensitive HFS+, label iOSRoot, 12 GB used, fsck OK after `fsck.hfsplus -y` rewrote 32 non-ASCII localized WorkflowKit Shortcut names Linux decomposes differently). Built by `tools/mkiosroot.sh OS.dmg SYSTEMOS.dmg APPOS.dmg OUT.img [SIZE]` (needs sudo; apfs-fuse as root; OS dmg is UDIF -> link must end .dmg). Contents: iPhone X 20H392 OS root + SystemOS cryptex at /private/preboot/Cryptexes/OS (so /System/Cryptexes/OS -> cache, 44 files, dyld_v1 arm64) + AppOS at .../App. /sbin/launchd and /usr/lib/dyld root:wheel 0755. NEXT: (confirm) `fastboot flash userdata ios16-root-20H392.img` (auto-sparse), boot 0029u (rd=ufsroot0) -> Apple launchd attempt.
- **MILESTONE ON HARDWARE: BOOT FROM INTERNAL FLASH.** 0029 CI `38797924912` PASSED, `xnu/out-0029` SHA256 `a68bc847...2a37`. Image `shim/out/shim-boot-0029u.img` (payload-0029u = 0029 kernel + `shim/out/sweet-0028.adt` + `rd=ufsroot0`, NO RAM disk). Boots 20:01:34 and 20:12:37 UTC (`research/boot0029u*.log`), photo IMG_20261015_221403: `SWEET UFS: "userdata" on LUN 0: first block 0x2b8c00, 109643 MiB, read-only` -> `BSD root: ufsroot0, major 1, minor 0` -> `hfs: mounted SweetRoot on device b(1, 0)` -> `SWEET: root volume is not authenticated (error 25); continuing unsealed` -> `load_init_program ... /sbin/launchd` -> `*** SWEET userspace: init running as PID 1 ***` -> heartbeat (ran for minutes unattended). userdata currently holds the 8 MB `research/root-hfs.img`. NEXT: build a multi-GB HFS+ image with the iOS 16 (iPhone X 20H392) userland (OS rootfs + SystemOS cryptex contents incl. dyld shared cache at /System/Library/Caches/com.apple.dyld; preserve modes/owners/symlinks; decompress LZBITMAP via apfs-fuse), flash it to userdata (sparse, needs user OK), then try Apple's dyld/launchd. Driver is read-only (root mounts RDONLY), fine for first launchd attempts.
- **userdata FLASHED with the 8 MB HFS test volume** (user said "flash it", 2026-10-15 19:53:17 UTC, `research/flash-userdata-hfs-test.log`: `fastboot flash userdata research/root-hfs.img` OKAY; pre-checks: one sweet device, partition-size:userdata 0x1AC4BFB000, partition-type f2fs, image fsck OK, SHA256 3626ea69...). Android userdata is now destroyed (expected/approved). Boot 0028u at 19:53:20 (`research/boot0028u-hfs.log`), photo IMG_20261015_215541: `BSD root: ufsroot0` -> **`hfs: mounted SweetRoot on device b(1, 0)` from internal UFS** -> panic `rootvp not authenticated after mounting @bsd_init.c:931` (arm64 macOS-config requires FSIOC_KERNEL_ROOTAUTH sealed root for non-ramdisk roots). Patch **0029** (`dd1c284`): SWEET logs `SWEET: root volume is not authenticated (error N); continuing unsealed` instead of panicking (Apple configs keep the panic; pivot_root still requires auth). CI **`38797924912`** running. Next: download out-0029, phone image with sweet-0028.adt + rd=ufsroot0 (no RAM disk), boot -> expect init from UFS.
- **UFS ROOT DRIVER VERIFIED ON HARDWARE (read-only).** 0028 CI `38796139570` PASSED, `xnu/out-0028` SHA256 `8b981640...9da6`; QEMU HFS RAM-disk regression `research/q0028-hfs` still runs init. Phone boot 2026-10-15 19:50:24 UTC (`research/boot0028u.log`, image `shim/out/shim-boot-0028u.img`, phone ADT `shim/out/sweet-0028.adt` with /sweet-ufs, NO RAM disk, `rd=ufsroot0`), photos IMG_20261015_215151/215220: `SWEET UFS: "userdata" on LUN 0: first block 0x2b8c00, 109643 MiB, read-only` -> `BSD root: ufsroot0, major 1, minor 0` -> `hfs_ValidateHFSPlusVolumeHeader: unknown Volume Signature : f188` (Android-encrypted data, as expected) -> `cannot mount root, errno = 19`, kernel retries mountroot (no panic). Nothing written to flash. NEXT (destructive, needs user confirmation right before): `fastboot flash userdata research/root-hfs.img` (8 MB HFS with test init) then boot rd=ufsroot0 -> expect init from internal flash.
- **PATCH 0028 (`33aceac`): XNU read-only UFS root device**, CI **`38796139570`** running (next artifacts xnu/out-0028, research/bt29, run29.log). `bsd/dev/sweet_ufs.c`: reuses ABL's UFSHCI state (like the shim probe), takes over UTRL at a kmem_alloc_contig region (DMA layout: UTRL 0x0, UCD 0x1000, 1 MiB bounce 0x4000), verifies UTRLBA readback before any doorbell, IE=0 polled, one SCSI cmd at a time on LUN0 (TUR x3, READ(10) via bounce, PRDT 256 KiB chunks), flush_dcache64 by PA around each command (host not dma-coherent per DT), finds GPT partition by name (`ufsroot=` boot-arg, default `userdata`), exposes `/dev/ufsroot0`/`rufsroot0` (512-byte logical sectors, physical 4 KiB, DKIOC* ioctls), refuses writes (EROFS). IOKitBSDInit: `rd=ufsroot0` -> sweet_ufs_rootdev() (lazy init) else panic. ADT: `tools/mkadt.py` adds `/sweet-ufs` reg <0x1d84000 0x3000> for the PHONE only (not --qemu). Local compile OK, imports resolve. Sandbox research/bt28 (pre0028 originals). FIRST PHONE TEST PLAN (non-destructive): boot 0028 with phone ADT + `rd=ufsroot0` and NO RAM disk: expect `SWEET UFS: "userdata" on LUN 0: first block 0x2b8c00, 109643 MiB` + `BSD root: ufsroot0`, then root mount failure (userdata is still Android-encrypted) -> panic. That validates the driver before flashing an HFS image into userdata (needs explicit user confirmation at that time).
- **SUPERSEDES the 64 GiB iosroot GPT plan: user said "u can delete android" (2026-10-15).** Use the existing `userdata` partition (LUN0 sda34, 4K LBA 0x2B8C00, 0x1AC4B MiB ~107 GiB) directly as the iOS root: NO GPT changes. Keep bootloaders, recovery (OrangeFox), modem/persist/fsg/modemst untouched. Write the HFS image later with `fastboot flash userdata` (sparse, auto-split under the 768 MiB limit). Android will no longer boot normally (expected; reinstallable). Order: XNU UFS driver first, read-only against the current GPT; flash only once it can locate userdata. Nothing erased yet.
- **DECIDED (user, 2026-10-15): 64 GiB `iosroot` on LUN0 (sda), taken from userdata (wipes Android user data; Android/super kept).** Planned GPT (4K LBAs): userdata 0x2B8C00..0xD7D6FF (~43 GiB, keep type/unique GUIDs and attributes); iosroot 0xD7D700..0x1D7D6FF (0x1000000 blocks = 64 GiB, 1 MiB aligned); backup GPT area unchanged. Procedure: user backs up phone data -> boot OrangeFox recovery (adb) -> back up GPT (sgdisk --backup + raw dd of LBA 0-5 and last 6 blocks) to research/ -> sgdisk edit -> Format Data -> verify Android boots to setup. NOT EXECUTED YET.
- **INTERNAL UFS WORKS FROM THE SHIM (read-only), user authorized internal-UFS approach incl. flashing (2026-10-15, "i allow everything").** Shim probe `shim/ufs.c` (commit `12ed3ed` + filter): ufshc@1d84000 is UFSHCI 2.1 (ver 0x210, cap 0x1587031F, 32 slots), ABL leaves HCE=1, HCS=0x10F (device present, lists ready, UIC ready); probe takes over UTRL at its own buffer (verifies UTRLBA readback before any doorbell), TEST UNIT READY/READ CAPACITY/READ(10) all succeed. LUN0 = 0x1D7D800 x 4 KiB (~126.6 GB), valid GPT (64 entries at LBA 2). Photos IMG_20261015_212916/213325/213429. Big LUN0 partitions (start in 4K LBAs / MiB): super 0xCA00/0x2200 (8.5 GiB), logdump 0x22CA00/64, minidump 0x230A00/128, rawdump 0x238A00/128, recovery 0x240C00/128, cache 0x248C00/384 ext4, exaid 0x260C00/384, cust 0x278C00/1024 ext4, **userdata 0x2B8C00/0x1AC4B MiB (~107 GiB), fs unreadable = encrypted (metadata encryption)**. cache..cust contiguous = only 1.75 GiB (too small for iOS ~10+ GiB). Plan needing user consent: shrink userdata in GPT (wipes Android data) and add an `iosroot` partition at the end of LUN0. LUNs 1-5 not listed yet (sdb..sdf backed up in backup/lun).
- **fastboot limit measured (2026-10-15, read-only getvar):** `max-download-size: 805306368` (768 MiB); `max-fetch-size` unsupported; `is-userspace: no` (ABL fastboot). A `fastboot boot` image (shim+kernel+RAM disk) must be < 768 MiB, so the 2.5 GiB iOS shared cache cannot ride in the boot RAM disk even if XNU gets all RAM. Real userland needs storage access (UFS driver, or USB host) or a much smaller cache. Unlocking full RAM is still needed later (GUI).
- **iOS 16 USERLAND SOURCE (Claude, 2026-10-15).** Chose **iPhone X (iPhone10,3/10,6, D22/D221AP)** iOS **16.7.16 (20H392)** over iPhone 8: same A11 (no PAC -> plain arm64, runs on Kryo 470/ARMv8.2), last iOS for A11; X userland is home-button-less and tall-screen (1125x2436 vs sweet 1080x2400), better fit for later GUI. Note the X has its OWN SystemOS cryptex (different digest from iPhone 8's). IPSW URL in `research/ipsw-x/URL.txt` (+ BuildManifest). Images on the user's external SSD (NOT in git, do not format that disk: it holds the user's photos): `/run/media/dipa/android/ios-sweet-ipsw/iPhone10,3_16.7.16_20H392/` — `087-86593-047.dmg` = Cryptex1,SystemOS (2,743,074,816 B), `087-86698-044.dmg` = OS rootfs (4,730,814,044 B), both zip CRC-32 verified, plus Firmware/*.root_hash/.trustcache/.mtree. AppOS cryptex is 087-86715-047.dmg (10 MB, same as iPhone 8).
  - Images are raw APFS; files use LZBITMAP (decmpfs type 14). 7z cannot decode. Tools: `ipsw` 3.1.738 (AUR ipsw-bin, user-approved) needs apfs-fuse on Linux; **apfs-fuse** built in user space (system cmake broken: cmake 4.4.4 wants libjsoncpp.so.27, jsoncpp 1.9.6 installed = partial upgrade, NOT fixed) with pip cmake + `-DCMAKE_POLICY_VERSION_MINIMUM=3.5 -DCMAKE_CXX_FLAGS="-include cstdint"`, installed to `~/.local/bin/apfs-fuse` (+apfs-dump-quick). Mount via a comma-free symlink (apfs-fuse splits options on ',' in `iPhone10,3`; exFAT has no symlinks -> put link elsewhere): `apfs-fuse LINK/087-86698-044.dmg MNT` -> `MNT/root/...`; unmount `fusermount3 -u MNT`.
  - Verified from headers: `dyld_shared_cache_arm64` magic `dyld_v1   arm64`; `/sbin/launchd`, `/usr/lib/dyld` = cputype 0x100000c subtype 0 (plain arm64). libSystem exists only inside the cache.
  - **BLOCKER for real userland via RAM disk:** shared cache = 3.10 GiB in 44 files (~2.5 GiB without the 592 MB `.symbols`), but the kernel manages only 1.20 GiB (0xb0000000..0xfd000000). Options: (A) give XNU the phone's full ~6 GB (banks 0x80000000+2G and 0x100000000+0xfcc00000, carve-out holes need pmap support) AND check fastboot max-download-size for a multi-GB boot image; (B) storage driver (Qualcomm UFS) to read a root from flash (no flashing allowed: would need a file/partition strategy); (C) run against individual dylibs extracted from the cache (uncertain).
- **MILESTONE ON HARDWARE: HFS+ ROOT FILESYSTEM -> PID 1.** Boot 2026-10-15 18:22:12 UTC (`research/boot0027b.log`, image `shim/out/shim-boot-0027b.img`), photo `IMG_20261015_202334.jpg`: `BSD root: md0` -> `hfs: mounted SweetRoot on device b(1, 0)` -> `load_init_program: attempting to load /sbin/launchd` -> `*** SWEET userspace: init running as PID 1 ***` -> repeated `SWEET init: still alive`, no panic. Kernel 0027 (built-in Apple OSS HFS + BearSSL MD5), init with SP alignment fix. NEXT: real iOS 16 userland on the HFS image (dyld, libSystem/dyld shared cache, launchd). Known gaps: entitlements (none granted), SHA-1/SHA-384/512 providers, no storage driver (RAM disk only), root mounted read-only.
- **PHONE HFS ROOT (0027) + SIGBUS ROOT-CAUSED.** Phone boot 2026-10-15 17:49:06 UTC (`research/boot0027.log`, photo `IMG_20261015_200031.jpg`): `hfs: mounted SweetRoot on device b(1, 0)` (HFS works on hardware), init printed its first line, then `pid 1 exited -- exit reason namespace 2 subcode 0xa` = SIGNAL/SIGBUS -> `initproc failed to start` panic. Diagnostic boot 18:08:13 UTC (`research/boot0027d.log`, image `shim/out/shim-boot-0027d.img`, diag init `research/diag-init` from scratch diag-init.S with [a][b][c] markers, `cs_debug=1`; photo `IMG_20261015_201547.jpg`): output `PID [a][b]` then SIGBUS -> fault at first `strb w21,[sp]`; no code-signing messages. Cause: kernel enters a static binary with sp at argc, not necessarily 16-aligned (depends on arg/apple string lengths, differs mockfs vs HFS); EL0 SP alignment check -> EXC_ARM_SP_ALIGN -> SIGBUS (sleh handle_sp_align). QEMU does not enforce SP alignment. NOT a kernel bug: real binaries start in dyld which aligns. Fix `1a8fc15`: sweet-init aligns sp at entry. Rebuilt `research/root-hfs.img`, QEMU `research/q0027-hfs2` OK. Phone image `shim/out/shim-boot-0027b.img` SHA256 `098ba46c...c5c` (payload-0027b, ramdisk match check-0027b) ready, awaiting FASTBOOT. Lesson: Assembly `;` is a comment in Apple arm64 asm (use .macro, not ;-joined #define).
- **HFS ROOT WORKS (QEMU).** 0027 CI `38779441895` PASSED, `xnu/out-0027` SHA256 `a8643886...5f6a`. QEMU `research/q0027-hfs` (RAM disk = `research/root-hfs.img`, rd=md0): `BSD root: md0` -> `hfs: mounted SweetRoot on device b(1, 0)` -> `load_init_program: attempting to load /sbin/launchd` -> `*** SWEET userspace: init running as PID 1 ***` + heartbeat, no panic. Phone image `shim/out/shim-boot-0027.img` (payload-0027 = 0027 kernel + sweet-0021.adt + root-hfs.img + rd=md0, ramdisk byte-match check-0027) ready; awaiting FASTBOOT for phone test.
- **HFS ROOT WORK (Claude), patches 0026-0027.**
  - 0026 (`f0e990c` + link fix `64c96f4`): Apple OSS **hfs-627.100.6** (commit `31d5ec238dfab485e78a9a30b8b92d13e8914f03`, paired with xnu-8796.141.3 in macos-135 release.json) staged by `xnu/patches/0026-stage-hfs.sh` into `bsd/sweet_hfs` (core + hfs_encodings; AppleKeyStore include/key prototypes guarded by CONFIG_PROTECT; SDK TargetConditionals copied). New config option `sweet_hfs` (MASTER + MASTER.arm64.sweet); 40 `optional sweet_hfs` files; Makefile.template foreach adds `_CFLAGS_ADD = -include sweet_hfs_compat.h -I...` (MUST come after kernel -D flags; compat undefs BSD/XNU_KERNEL_PRIVATE and the CONFIG_* HFS tests so kext-config.h decides: macOS profile, no content protection). `sweet_hfs_iokit.c` replaces hfs_iokit.cpp/hfs_encodings_kext.cpp: `sweet_hfs_register()` called in bsd_init after vfsinit (encodings init, vfs_fsadd VFS_TBLCANMOUNTROOT, zones, sysctls); is_ejectable 0, iterate_media none, serial KERN_NOT_SUPPORTED, OSKextGetCurrentLoadTag -> kOSKextInvalidLoadTag (renamed via compat macro). hfs_encodings' own `hfs_allocated` renamed per object (separate kexts on Apple; first CI `38777325964` failed on that duplicate at link). mockfs now validates Mach-O magic (its TODO) so non-Mach-O roots fall through to HFS (new fs entries come AFTER mockfs in vfsconf). CI `38778133720` PASSED, `xnu/out-0026` SHA256 `0b49170c...701a`, prints `SWEET HFS: hfs-627.100.6 registered`.
  - HFS+ image: `research/root-hfs.img` (8 MB, mkfs.hfsplus from AUR hfsprogs installed with user approval; loop-mounted with sudo; /sbin/launchd = research/sweet-init, /dev; fsck.hfsplus OK). QEMU `research/q0026-hfs`: `BSD root: md0` then data abort in MD5Init from hfs_getvoluuid (mount computes volume UUID).
  - 0027 (`14bf2b7`): 0020 stager also copies BearSSL hash/md5.c + codec/dec32le.c/enc32le.c; `corecrypto_md5.c` SWEET branch converts MD5_CTX <-> br_md5_context around br_md5_* calls; wrappers sweet_md5.c/sweet_dec32le.c/sweet_enc32le.c. Host test 40/40 match md5sum. CI **`38779441895`** running.
  - Local tooling: `tools/xnu-cc.py` has `XNU_CC_POST` (flags after logged ones). Sandbox `research/bt28/xnu` = 0025 CI tree + 0026/0027 edits; originals `research/pre0026`, `research/pre0027`. HFS local objects `research/hfs-objs`. Checker entries updated to bt28.
  - SHA-1 / SHA-384/512 still have no provider.
- **MILESTONE ON HARDWARE: USERSPACE PID 1 RUNS ON THE PHONE.** Boot 2026-10-15 17:16:00 UTC (`research/boot0025.log`: send OKAY0.410s, boot OKAY0.135s), image `shim/out/shim-boot-0025.img` SHA256 `9dbfa0b1...89db0`. Photo `IMG_20261015_191733.jpg`: `BSD root: md0` -> `load_init_program: attempting to load /sbin/launchd` -> `*** SWEET userspace: init running as PID 1 ***` -> repeated `SWEET init: still alive` (5 s heartbeat), no panic. Kernel 0025 + mockfs RAM disk + built-in no-entitlements AMFI. No flashing performed.
- **NEXT (toward real iOS userland):** real root filesystem with real binaries. Options: (a) build Apple OSS `hfs` (macOS 13.5 tag `hfs-627.100.6`) into SWEET like libpthread, then an HFS RAM disk image; (b) iOS 16 dyld + libSystem/dyld shared cache from the IPSW (needs APFS or repacking onto HFS). Expected hurdles: entitlements (sweet_amfi grants none), SHA-1/MD5/SHA-384/512 providers (BearSSL), missing kexts/daemons. Current init is a static test program, not launchd.
- **MILESTONE: USERSPACE RUNS (QEMU).** 0025 CI `38774788048` PASSED, `xnu/out-0025` SHA256 `5496069b...4877`. QEMU `research/q0025-rd` (150 s, no panic): `BSD root: md0` -> `load_init_program: attempting to load /sbin/launchd` -> `*** SWEET userspace: init running as PID 1 ***` -> `SWEET init: still alive` every 5 s. Exec, ad-hoc SHA-256 code signature, syscalls, devfs /dev/console, select timeouts all work. Phone image prepared: `shim/out/shim-boot-0025.img` 16,515,072 bytes SHA256 `9dbfa0b15140c0bd733a16c4f727f6a7df44a8741f98d8e266d5f2fa4f689db0` (payload-0025 = 0025 kernel + sweet-0021.adt + research/sweet-init + rd=md0; ramdisk byte-match check-0025). Waiting for user to put phone in FASTBOOT.
- **0024 CI `38773277811` PASSED**, `xnu/out-0024` SHA256 `a0ba964b...4348`. QEMU `research/q0024-rd` and **PHONE (boot 2026-10-15 17:05:55 UTC, `research/boot0024.log`, image `shim/out/shim-boot-0024.img` SHA256 `cf3dac86...6964`, 16,510,976 bytes, payload `shim/out/payload-0024.bin` = 0024 kernel + `shim/out/sweet-0021.adt` + RAM disk `research/sweet-init` + rd=md0; ramdisk byte-match `check-0024`)** agree: `Added memory device md0`, `BSD root: md0`, `load_init_program: attempting to load /sbin/launchd`, then data abort in accelerate_entitlement_queries (PC 0x...77d2458, FAR 0x1a0) = NULL AMFI interface. Photo `IMG_20261015_190715.jpg`. RAM disk root is physically verified.
- **0025 (`2518c79`)**: new `bsd/kern/sweet_amfi.c` registers a built-in AMFI interface at EARLY_BOOT/MIDDLE: no entitlements (adjustContextWithoutMonitor succeeds without creating a context, queries KERN_DENIED, copies NULL/KERN_NOT_FOUND, get_xml/transmuted false); WithMonitor KERN_NOT_SUPPORTED; OSEntitlements_query and query_context_to_object panic explicitly (CoreEntitlements closed; no kernel caller); TrustCache version 0 (0015 keys on trust_cache_rt==NULL, img4 absent -> still unavailable); CoreEntitlements table zero (PMAP_CS only). Compiles locally; checker updated (bt27 entries). CI **`38774788048`** running. Next artifacts `xnu/out-0025`, `research/bt29`, `research/run29.log`. Real iOS binaries will need real entitlements later (no OSS CoreEntitlements exists).
- **0021-0024 RAM-disk-root iteration (Claude), QEMU only so far, no new phone boot since 0020.** Each kernel tested with `tools/mkpayload.py KERNEL research/q0021.adt OUT --ramdisk research/sweet-init --cmdline "debug=0xc serial=3 cpus=1 keepsyms=1 -enable_kprintf_spam -noprogress rd=md0"` then `tools/qemu-sweet.py OUT DIR --secs 150 --kernel KERNEL --fail-on-panic` (PATH needs ~/swift/usr/bin for llvm-nm). Fresh ADTs: `research/q0021.adt` (QEMU), `shim/out/sweet-0021.adt` (phone).
  - 0021 CI `38769532000` PASSED, `xnu/out-0021` SHA256 `2b7500a1...962e`, `research/bt25`/`run25.log`. QEMU `research/q0021-rd`: md0 root, then assert `iomediaClass` in IOService::publishHiddenMedia.
  - 0022 (`20ece9c`, publishHiddenMedia without IOMedia class) CI `38770666158` PASSED, `xnu/out-0022` SHA256 `a4d0e787...30c5`, `research/bt26`/`run26.log`. QEMU `research/q0022-rd`: data abort in SHA256_Init (NULL g_crypto_funcs) from vm_kernel_addrhash_internal.
  - 0023 (`c8089d1`, libkern SHA256_Init/Update/Final use built-in ccsha256_ltc_di + ccdigest_init/update on SWEET; also serves code-signing SHA-256; SHA-1/MD5/SHA-384/512 still have NO provider - BearSSL from 0020 could supply them later) CI `38771876423` PASSED, `xnu/out-0023` SHA256 `d763fed7...1003`, `research/bt27`/`run27.log`. QEMU `research/q0023-rd`: **mockfs mounted md0, `load_init_program: attempting to load /sbin/launchd`**, then panic `mockfs_fsnode_vnode failed to create fictitious pages ... rvalue = 5` (mockfs.c:351).
  - 0024 (`3293c80`): mockfs used memdev mi_base (4K page number of a VIRTUAL kernel address for IOKit RAMDisk, truncated to 32 bits) << PAGE_SHIFT as a physical address. Now zero-copy pager mapping only when mi_phys (with 4K units); virtual md uses pagein/blockmap/strategy -> memdev bcopy. memdev's own mdPhys path assumes 4K ppnums (unsafe on 16K arm64), so do NOT switch the RAMDisk to physical. CI **`38773277811`** running. Next artifacts `xnu/out-0024`, `research/bt28`, `research/run28.log`.
  - Sandboxes: bt25/bt26/bt27 contain the next patch's edited files; pristine copies in `research/pre0022`..`pre0024`.
- **PATCH 0021 (Claude): RAM disk root via mockfs -> first userspace program.** Commits `9c37771` (initial; CI `38768500280` FAILED: mockfs_fsnode.c kfree_type(mockfs_fsnode_t) typed-alloc static assert; local xnu-cc stubs `__builtin_xnu_types_compatible` so it can't catch this) and `193772f` (fix), CI **`38769532000`** running: https://github.com/dipa-studio/ios-sweet/actions/runs/38769532000. Next artifacts: `xnu/out-0021`, `research/bt25`, `research/run25.log`.
  - Kernel: `config/MASTER.arm64.sweet` FILESYS_BASE += `mockfs` (XNU's built-in FS: root device is itself a Mach-O, served as /sbin/launchd, plus /dev for devfs). Upstream mockfs bit-rot fixed: kalloc_type/kfree_type used the POINTER typedef mockfs_fsnode_t (nodes were 8 bytes) -> `struct mockfs_fsnode`. `IOService::setRootMedia` asserted IOBlockStorageDriver class exists (IOStorageFamily absent): SWEET-only, a missing class means root=NULL (same as IOSetImageBoot); Apple path keeps assert. All 21 patches apply (`research/check-patch-order.py`); 5 TUs compile locally with -DMOCKFS (`research/mockfs-objs`), imports resolve vs 0020 kernel. Sandbox `research/bt24/xnu` now holds 0021 versions of those 3 files; pristine 0020 copies in `research/pre0021`.
  - Tools: `tools/mkpayload.py --ramdisk IMAGE` appends IMAGE as an extra payload segment right after the kernel, moves kernel_end past it (shim unchanged: ADT+boot_args follow it, image stays below topOfKernelData), and adds ADT `/chosen/memory-map` `RAMDisk`=<phys,size>. Boot with `rd=md0`. Without --ramdisk output is byte-identical to existing 0020 QEMU and phone payloads (verified). `tools/sweet-init.S` + `tools/mkinit.py`: PIC static init (open /dev/console, print PID, heartbeat every 5 s via select, never exits) wrapped into a static arm64 Mach-O (__PAGEZERO, __TEXT@0x100000000, LC_UNIXTHREAD, ad-hoc SHA-256 CodeDirectory v0x20400, 4K pages). Build: `~/swift/usr/bin/clang -target arm64-apple-ios16.0 -c tools/sweet-init.S -o X.o && tools/mkinit.py X.o research/sweet-init` (ld64.lld cannot link static iOS). Signature not verified by a real codesign; the kernel will tell.
  - QEMU with 0020 kernel + RAM disk (`research/q0020-rd.bin`, rd=md0, 150 s `research/q0020-rd150`): `Added memory device md0`, **`BSD root: md0, major 1, minor 0`** (plumbing works), then the setRootMedia assert (now fixed in 0021). NOTE: QEMU needs >60 s to reach IOFindBSDRoot (60 s run showed nothing after stf0; likely RTC/inittodr wait), so use --secs 150.
  - NEXT: download 0021, QEMU 150 s with ramdisk; expect mockfs mount then init exec -> `*** SWEET userspace: init running as PID 1 ***`. Then phone boot with same payload (phone ADT shim/out/sweet-0020.adt pattern + --ramdisk + rd=md0).
- **0020 PHONE RESULT (user transcription of screen, 2026-10-15): KERNEL INIT COMPLETE, WAITING FOR ROOT.** After Skywalk self-tests PASSED, kminit, ifnet_attach lo0/gif0/stf0, screen prints `BSD`, then `Waiting on <dict><key>IOProviderClass</key><string>IOMedia</string><key>Content</key><string>Apple_HFS</string></dict>` and `Failed to write boot-picker-bringup-reason to NVRAM.` No panic. This is IOFindBSDRoot waiting for a root device (none exists); NVRAM warning is expected (no NVRAM driver). QEMU `cpu_idle` snapshot is presumably the same wait (not GDB-confirmed; milestone GDB run was cancelled by user since phone answered it). Draft `research/check-milestones20.gdb` (hbreaks inittodr/vfs_mountroot/IOFindBSDRoot/bsd_utaskbootstrap) left uncommitted/ignored.
- **NEXT MILESTONE: root filesystem -> launchd.** Plan: (1) RAM disk: shim places an image in RAM, ADT /chosen/memory-map `RAMDisk` entry, boot-arg `rd=md0` (XNU md driver). (2) HFS is a separate kext on Apple; build Apple OSS `hfs` (tag paired with macOS 13.5 in distribution-macOS macos-135 release.json) into SWEET like libpthread 0019. APFS is closed. (3) Minimal HFS image with iOS 16 launchd (later: dyld/shared cache; AMFI/code-signing absent will be a later hurdle). User's end goal is full iOS GUI.
- **0020 (AES) VERIFIED + PHONE BOOTED (Claude took over after Codex usage limit).** Actions `38765422261` (`ab9e23f`) PASSED; kernel `xnu/out-0020/kernel.development.sweet` checksum OK; buildtree `research/bt24`, log `research/run24.log`. Actual-kernel AES checks PASS (`research/check-aes20.gdb` / `.log`, 12 extra CBC cases match OpenSSL). 45s QEMU `research/q0020`: no panic, zero unknown glyphs, past old TCP/AES panic -> Skywalk self-tests PASSED -> bsd_autoconf kminit -> ifnet_attach lo0/gif0/stf0; final snapshot PC in `cpu_idle` (idle or waiting; NOT yet diagnosed, could be root-device wait). Image `shim/out/shim-boot-0020.img` 16,461,824 bytes SHA256 `775200cb02d95fc750981516b79d91dcdc96184bbe67a38f9d57c59b4a391828`, ramdisk byte-matches `payload-0020.bin` (`check-0020`). **Phone temporarily booted 2026-10-15 16:10:00 UTC**: one FASTBOOT product sweet, send OKAY0.407s, boot OKAY0.134s, total0.549s, exit0 (`research/boot0020.log`). Awaiting user photo; do not reboot the phone before it. NEXT: read photo; diagnose what QEMU waits on after stf0 (GDB backtrace of threads / longer run). Codex's STOP request below is complete.
- User requests STOP after completing the current0020 AES iteration (Actions/QEMU/phone), then leave a precise committed handoff for another AI. User says FASTBOOT ready again after0019 photo. Do not start a new blocker fix after this iteration.
- Goal: iOS16-generation XNU on Redmi Note10Pro sweet/SM7150. Always commit, use gh/Actions for kernel builds, keep this handoff current. Temporary fastboot boot only; preserve Android/backups. No userland/root filesystem boot yet.
- **Patch0020 update:** initial `e71098d` / Actions `38765012466` superseded by scalar-only compile flags. Added -mgeneral-regs-only to all six provider/BearSSL TUs and corecrypto_aes.c; object disassembly now confirms no SIMD. Updated implementation `ab9e23f`, Actions `38765422261` queued/running: https://github.com/dipa-studio/ios-sweet/actions/runs/38765422261. Do not launch another run. portable BearSSL AES CBC and legacy one-block ECB wired directly into SWEET corecrypto_aes.c. Genuine bitslice implementation, no CPU AES/SIMD requirement, heap or fake global crypto table. Source fetched by `0020-stage-bearssl.sh` from official BearSSL git at immutable `7bea48e5e850ab4cafbe68d3765cdaba13a86d6f`; MIT license retained, downloaded source stays out of git. Kernel limits include adapter only. All128/192/256-bit keys, CBC encrypt/decrypt, copied contexts, in-place/out-of-place; zero block count and size overflow handled, invalid keys clear context. Seven TUs compile to arm64 objects (`research/aes-objs`), imports resolve, all20 patches apply and sources match (`research/patch0020-check.log`). Sandbox `research/bt23/xnu`, originals `research/pre0020`. NEXT: Actions then actual-kernel NIST/random CBC/ECB checks and >=45s QEMU before another phone boot. Next artifacts out-0020 / bt24 / run24.log. 0020 updated CI pending. Local sources/checks match the scalar-only patch.
- **Latest built kernel0019**, implementation `256d3f0`, patches0001-0019. Actions `38763072907` PASSED (4m5s): https://github.com/dipa-studio/ios-sweet/actions/runs/38763072907. Kernel `xnu/out-0019/kernel.development.sweet`, SHA256 `a27df7568f03fb541cf0e8024c0a594fa178a85054fcf9eba29158cbd4c5ecc0`; checksum verified. Log/source `research/run23.log` / `research/bt23` (no nested .git). Seven pthread source/build/header files and staged adaptations byte-match local compile inputs.
- **0019 hardware photo received** `IMG_20261015_175306.jpg`: pthread registration visible, passes mbinit and DLIL checksum/scheduling, same AES fault as QEMU: PC`0xfffffe00079174e0` (`aes_encrypt_key128`), LR`0xfffffe000767c3a4` (`tcp_init`), FAR0x78, x8=0. Disassembly proves NULL g_crypto_funcs->ccaes_cbc_encrypt. Photo processed; no more0019 observation pending. General crypto table remains absent, other hash/mode operations may still fault after0020. DO NOT bypass TCP or install fake crypto. XNU already contains SHA256/HMAC implementations; AES source there is a dispatch wrapper. Full future provider interface libkern/libkern/crypto/register_crypto.h. Apple/corecrypto default README describes evaluation-only licensing, so no external corecrypto was fetched or staged; BearSSL selected for this portable AES integration.
- **0019 pthread FIXED in QEMU and observed beyond its init on phone**: 45s QEMU `research/q0019`, zero unknown glyphs, then AES panic. Actual-kernel API checks PASS `research/check-pthread19.gdb` / `.log`, guest `research/q0019-api`: function/callback table identity, actual provider pthread_init returns, locks/global hash/threadcall/typed zones initialized, thread_selfid via syscall shim + buffer bounds, process hash init/delete via shims restores NULL. Monitor quit prints expected remote-disconnect after PASS. All fixture guests stopped.
- **0019 provider**: genuine Apple libpthread-514.100.2 commit `a6c70ca0e544347a0377babf748f831577ec24f9`, exact paired release with xnu8796.141.3 in distribution-macOS/macos-135/release.json (`research/macos-135-release.json`). 0019 shell stage runs before patches (workflow copies *.sh); three SWEET wrapper TUs use kext BSD header view, vm_fault_external, renamed provider-side pthread_kern/current_uthread; register real function table at EARLY_BOOT SECOND, real pthread_init later. Stager applies bounded address casts, zero user addresses, proper panic format. SWEET opaque ksyn storage enlarged48->56 for trailing kwe_uth, checked with provider static assertion. Local pre-CI TargetConditionals fixture was syntax-only; artifact bt23 carries actual SDK header and CI is authoritative.
- **Phone0019 temporarily booted** 2026-10-15 15:51:36 UTC: exactly one FASTBOOT/product sweet verified; send OKAY0.406s, boot OKAY0.134s, total0.546s, exit0 (`research/boot0019.log`). Image `shim/out/shim-boot-0019.img`, 16,457,728 bytes, SHA256 `19429a57e486b856880df9e27327ed488e0139345311fdb0350974e72103a9a1`. Phone ADT/payload `shim/out/sweet-0019.adt` / `payload-0019.bin` timer19, unpacked ramdisk byte-match (`check-0019`). EntryPA0xb146b488, kernelendPA0xb2000000, boot_argsPA0xb2004000/top0xb2008000. Last user FASTBOOT+USB reply preceded this boot; do not assume phone is still in FASTBOOT.
- **CPU0018 physically verified** by `IMG_20261015_173951 (2).jpg`: boot CPU0 registered, real SGI1 verified, initialization complete -> BSD/MAC/mbinit -> old pthread-table panic. SweetCPU uses legacy IOCPU, ml_processor_register/processor_start/initCPU, real SGI1 clears SIGPdisabled before max CPUs completion; no forced flags/skipped waits. CPU APIs and two-CPU rejection passed (`research/check-cpu18.gdb`, `q0018-api`, `q0018-smp`). Single core; SMP/suspend unsupported. CURRENT SWEET has NO USE_APPLEARMSMP.
- QEMU next run: generate fresh `tools/mkadt.py research/q0020.adt --qemu` (timer27), mkpayload with `debug=0xc serial=3 cpus=1 keepsyms=1 -enable_kprintf_spam -noprogress`, then `tools/qemu-sweet.py PAYLOAD OUT --secs 45 --kernel KERNEL --fail-on-panic`. 12s can miss later panics because IORTC waits30s. Runner snapshot only: panic exit2, blank/incomplete exit3; absence of panic does not mean complete boot. Qualcomm XPU/ABL/panel and phone SMC PSCI require hardware checks.
- Local checker `tools/xnu-cc.py research/run23.log research/bt23 FILTER --per-file`, XNU_CC_OBJDIR for objects. For new BearSSL TUs add XNU_CC_EXTRA with -I bt23/xnu/libkern/crypto/sweet_bearssl/{inc,src}. Patch checker `research/check-patch-order.py` uses temporary upstream index; source fixtures/artifacts ignored under research. GDB mask registers to unsigned64, use function-entry manual-call return traps, discard manipulated guests. No QEMU guest intentionally left running.

## Session log and earlier handoffs (superseded by the active summary above)

### Prior 0019 transition notes (superseded)

- Goal: iOS 16 generation XNU on sweet. Always commit completed work, use gh/Actions for kernel builds, keep this handoff current. Temporary fastboot boot only; preserve Android/backups.
- **0019 build PASSED** Actions `38763072907` (4m5s), implementation `256d3f0`. Kernel `xnu/out-0019/kernel.development.sweet`, SHA256 `a27df7568f03fb541cf0e8024c0a594fa178a85054fcf9eba29158cbd4c5ecc0`; checksum verified. Log/source `research/run23.log` / `research/bt23`; all seven patched files and staged provider adaptations match local compile inputs. Prefer bt23 as the next baseline.
- **0019 pthread FIXED in QEMU**: 45s run `research/q0019` registers provider, passes mbinit, DLIL SUM16 checks and DLIL thread scheduling. Actual-kernel GDB checks `research/check-pthread19.gdb` / `.log` PASS: function/callback table identity, real _pthread_init returns, locks/global hash/cleanup threadcall/typed zones non-NULL, thread_selfid via actual syscall shim with output bounds, process hash init/delete through actual shims restores NULL. Guest stopped after tests; no fixture left running. GDB monitor quit prints expected remote disconnect after PASS.
- **Current next blocker:** QEMU0019 panic data abort FAR0x78 at `aes_encrypt_key128` PC`0xfffffe00079174e0`, called by `tcp_init` LR`0xfffffe000767c3a4`. Disassembly confirms `g_crypto_funcs == NULL`, loading ccaes_cbc_encrypt at+0x78. General crypto registration is still absent; DO NOT bypass TCP or supply fake crypto. Next integrate a genuine compatible crypto implementation/provider (AES first needed here, other digest/mode APIs also used). XNU contains SHA256/HMAC but no AES implementation; its corecrypto_aes.c is a dispatch wrapper. Full crypto table is in libkern/libkern/crypto/register_crypto.h.
- **0019 phone image prepared and verified**, user reports FASTBOOT+USB again; exactly one device/product sweet verified. `shim/out/shim-boot-0019.img`, 16,457,728 bytes, SHA256 `19429a57e486b856880df9e27327ed488e0139345311fdb0350974e72103a9a1`; unpacked ramdisk matches phone payload (`shim/out/check-0019`, `payload-0019.bin`, `sweet-0019.adt`, timer19). EntryPA0xb146b488; kernelendPA0xb2000000; boot_argsPA0xb2004000/top0xb2008000. Usual debug cmdline cpus=1/-noprogress. **Temporarily booted 2026-10-15 15:51:36 UTC**: send OKAY0.406s, boot OKAY0.134s, total0.546s, exit0 (`research/boot0019.log`). User asked for photo after45s. Await the photo; DO NOT reboot again before observation. Bootloader acceptance only; no0019 physical progress observed yet.
- **Hardware photo confirms 0018 progress** (`IMG_20261015_173951 (2).jpg`): real phone prints `SWEET CPU: boot CPU 0 registered, SGI1 verified, initialization complete`, enters BSD/MAC, reaches `mbinit: done`, then the same missing-pthread-function-table panic as QEMU at pthread_shims.c:318. CPU completion/interrupt delivery is now physically observed. The photo was received; no further phone boot performed yet.
- **Patch0019 committed/pushed `256d3f0`; Actions `38763072907` queued/running:** https://github.com/dipa-studio/ios-sweet/actions/runs/38763072907. Do not launch a duplicate. genuine Apple OSS libpthread-514.100.2 provider (immutable commit `a6c70ca0e544347a0377babf748f831577ec24f9`), paired with xnu-8796.141.3 by Apple's `distribution-macOS/macos-135/release.json` (`research/macos-135-release.json`). `0019-stage-libpthread.sh` fetches/stages it before patches; workflow now copies shell scripts too. SWEET-only wrappers compile all three real kernel sources, rename provider-side symbols, use kext header view and vm_fault_external, register the real function table at EARLY_BOOT SECOND. Existing pthread_init then runs the actual provider initialization. No pthread wait/syscall is bypassed. Source staging includes bounded explicit address casts/zero user addresses and panic-format fixes. SWEET kernel opaque ksyn storage enlarged from48 to56 bytes to contain this provider's trailing kwe_uth, with a provider size assertion. Local compile of three provider TUs plus pthread_shims/kern_fork passed; imports resolve and provider exports do not collide with existing kernel symbols. All19 patches apply and changed sources match (`research/patch0019-check.log`). Source sandbox `research/bt22/xnu`, originals `research/pre0019`, objects `research/pthread-objs`. Local TargetConditionals fixture only has target macros for syntax; CI stages the real macOS SDK header and is authoritative. Next Actions artifacts: out-0019 / bt23 / run23.log; run QEMU >=45 seconds. 0019 CI is pending; no 0019 QEMU run yet.
- **Latest kernel implementation `e7d9550`, patches0001-0018; CI `38760004398` PASSED (3m56s)**: https://github.com/dipa-studio/ios-sweet/actions/runs/38760004398. No build is pending. Kernel `xnu/out-0018/kernel.development.sweet`, SHA256 `b3c8d59acc88f93a2c836eb2527a05ed4fbaac7c580a2ea8c3b795137f4aadf1`; checksum verified. Source/log `research/bt22` / `research/run22.log` (baseline for patch0019; no nested .git). New driver/config sources match CI exactly.
- **CPU wait FIXED in QEMU**: SweetCPU uses legacy IOCPU, validates single boot CPU, ml_processor_register -> processor_start -> initCPU real SGI1 -> scheduler/IOKit completion -> ml_set_max_cpus. It does NOT force a flag or skip a wait. CPU APIs passed: Running CPU0, processor_array[0] association, SGI signalling enabled, name, unsupported secondary-start error (`research/check-cpu18.gdb` / `.log`, `research/q0018-api`). Single-core only; SMP and suspend unsupported. Two-CPU topology fails explicitly (`research/q0018-smp`).
- **Next blocker reproduced in 45s QEMU** (`research/q0018-long`, zero unknown glyphs): BSD initialization reaches MAC framework, network mcache and `mbinit: done`, then **`pthread kernel extension not loaded (function table is NULL). @pthread_shims.c:318`**. Do not bypass pthread_init: find/integrate the matching open-source libpthread kernel implementation and register its real function table. A 12s run `research/q0018` looked panic-free before the 30s IORTC wait elapsed; use >=45s or GDB checkpoints for the next iteration. No userland/root filesystem boot yet.
- **Phone 0018 TEMPORARILY BOOTED** 2026-10-15 **15:31:15 UTC**: exactly one FASTBOOT device verified product sweet; send OKAY0.400s, boot OKAY0.134s, total0.539s, exit0. Local log `research/boot0018.log`. This confirms bootloader acceptance only. User was asked for a photo; await it, DO NOT reboot the phone again before their observation. No flashing performed.
- Current hardware image `shim/out/shim-boot-0018.img`, **16,437,248 bytes**, SHA256 **`b7a23595d143a76c72c9fe2cfcc5d77a8f16987b5af1a2703bbffdfa6922908c`**. Phone ADT/payload `shim/out/sweet-0018.adt` / `shim/out/payload-0018.bin` (timer19), unpacked ramdisk exactly matches payload (`shim/out/check-0018`). EntryPA0xb146b488; kernelendPA0xb1ffc000; boot_argsPA0xb2000000/top0xb2004000. Command line `debug=0xc serial=3 cpus=1 keepsyms=1 -enable_kprintf_spam -noprogress`.
- QEMU payload/ADT `research/q0018.bin` / `research/q0018.adt` (timer27). Run `python3 tools/qemu-sweet.py research/q0018.bin research/NEW-OUT --secs 45 --kernel xnu/out-0018/kernel.development.sweet --fail-on-panic`; fresh ADT seed for a new payload. Output fb.png/fb.txt/regs.txt/qemu.log/result.json. Visible panic exit2; blank/incomplete decode exit3; no_panic_observed is snapshot-only, not successful boot. -noprogress prevents the graphical indicator corrupting console text. Qualcomm XPU/bootloader/panel and SMC PSCI still need physical validation.
- Patches0014-0017 fixed PRNG registration/direct SHA256, explicit unavailable trust-cache service with rejected loads/no matches, built-in SweetPlatformExpert, and timer PPI from ADT (phone19/default19, QEMU27). All their checks/artifacts are preserved in the history below. CURRENT SWEET has NO USE_APPLEARMSMP; do not assume gCPUIC/gAIC/gPMGR AppleARMSMP globals exist.
- Local single-file checker: tools/xnu-cc.py research/run22.log research/bt22 FILTER --per-file, output via XNU_CC_OBJDIR. Patch checker `research/check-patch-order.py` applies all18 via temporary index, matches sandbox sources. Sandbox for0018 `research/bt21/xnu`, originals `research/pre0018`, objects `research/cpu-objs`. First compiler issues were missing machine/atomic.h and nonexistent getNameSymbol; fixed and both TUs compiled successfully before CI. Fixtures/artifacts under research are local-only/ignored.
- GDB: mask int(register)&((1<<64)-1) for unsigned kernel pointers; use function-entry manual-call return traps, discard manipulated guests. No QEMU fixture is intentionally left running.

### Earlier active handoff snapshot (superseded)


- **0018 milestone:** Actions `38760004398` PASSED (3m56s), checksums passed, new CPU/build files byte-match CI tree. Kernel `xnu/out-0018/kernel.development.sweet`, SHA256 `b3c8d59acc88f93a2c836eb2527a05ed4fbaac7c580a2ea8c3b795137f4aadf1`; log/tree `research/run22.log` / `research/bt22`. QEMU `research/q0018` 12s: boot CPU registered, SGI1 verified, CPU initialization complete, **BSD initialization entered** (copyright, MAC framework, buffer headers), no panic/zero unknown glyphs. Direct CPU API checks PASS (`research/check-cpu18.gdb`, `.log`, `research/q0018-api`): CPU0 Running, processor matches processor_array[0], real SGI enabled, CPU name correct, secondary-start returns KERN_NOT_SUPPORTED. Two-CPU ADT correctly panics before registration (`research/q0018-smp`). Longer 45s run `research/q0018-long` still running; next BSD wait/fault not yet identified.
- **Prepared 0018 phone image:** `shim/out/shim-boot-0018.img`, 16,437,248 bytes, SHA256 `b7a23595d143a76c72c9fe2cfcc5d77a8f16987b5af1a2703bbffdfa6922908c`. Phone ADT/payload `shim/out/sweet-0018.adt` / `shim/out/payload-0018.bin`, usual debug args with cpus=1 and -noprogress. Unpacked ramdisk byte-compared (`shim/out/check-0018`). Entry PA remains 0xb146b488; kernel end PA 0xb1ffc000, boot_args 0xb2000000/top0xb2004000. User reports FASTBOOT+USB ready; read-only check found exactly one product sweet. NEXT: temporary fastboot boot of this verified image, record send/boot results, then await hardware photo without rebooting again.
- Patch 0018 committed/pushed **`e7d9550`**; Actions **`38760004398`** queued/running: https://github.com/dipa-studio/ios-sweet/actions/runs/38760004398. Do not launch a duplicate run.
- Active continuation: patch **0018** implemented in `iokit/Kernel/arm/SweetCPU.cpp` + arm64 source list + exact qcom,kryo470 personality. Keeps legacy IOCPU, accepts ONLY the single boot CPU, fills ml_processor_info from parsed topology with CPU object as cpu_id, calls ml_processor_register and processor_start. initCPU sends SGI1 via ICC_SGI1R_EL1 and waits (1-second deadline) for real cpu_signal_handler to clear SIGPdisabled. Only after successful startup calls ml_cpu_init_completed/cpusRunning and publishes completion/max CPUs. Secondary startup/suspend are explicitly unsupported. Local C++ compile passed for both TUs (`research/cpu-objs`), all imports resolve, object contains dsb ishst / ICC_SGI1R / isb; all18 patches apply in order and match sources. Sandbox `research/bt21/xnu`, originals `research/pre0018`; next CI artifacts should use `xnu/out-0018`, `research/bt22`, `research/run22.log`. User has the phone available; first run QEMU, then prepare/temporarily boot useful hardware progress.
- Goal: iOS 16 generation XNU on Redmi Note 10 Pro / sweet. User wants persistent progress, commits, kernel builds via `gh` Actions, and this handoff kept current across agent switches. Temporary `fastboot boot` only; preserve Android and backups.
- Latest kernel implementation: **`aa3f991`**, patches **0001-0017**. All four new Actions builds PASSED: 0014 `38748543058` (4m0s), 0015 `38749549779` (4m3s), 0016 `38750733996` (4m3s), 0017 **`38751507437` (4m7s)**. Latest: https://github.com/dipa-studio/ios-sweet/actions/runs/38751507437. No build is pending.
- **Current blocker: CPU initialization has no SWEET CPU driver.** QEMU registers SweetPlatformExpert, then kernel_bootstrap_thread waits in **kperf_init_early -> ml_wait_max_cpus**. Confirmed via actual-kernel GDB call stack (`research/locate-cpu-wait2.log` / `.symbols`) and normal-run `max_cpus_initialized == 2` (MAX_CPUS_WAIT). Do not force the flag or remove the wait. Next implement real CPU registration and completion using XNU's CPU/processor interfaces. CURRENT SWEET uses legacy IOCPU (`USE_APPLEARMSMP` is absent); enabling AppleARMSMP is a separate architectural change requiring GIC/PMGR services. No userland/root filesystem boot yet.
- Fixed this session: PC=0 unregistered PRNG callback (0014, built-in HMAC-SHA256 provider + direct entropy/write_random hashing); absent Image4/AMFI trust-cache service (0015, unavailable runtime, loads rejected and queries no-match); missing platform driver (0016, SweetPlatformExpert exact personality); incorrect QEMU timer IRQ (0017, validated ADT PPI property, phone default19/QEMU27).
- **Latest kernel** `xnu/out-0017/kernel.development.sweet`, SHA256 `055a80190ab998b4df9203f1102072dcc78faad1779a537a514e522b682b582f`. Buildtree/log **`research/bt21` / `research/run21.log`**; all nine changed C/C++/header/config files byte-match local checked sources. Checksums passed. Entry PA `0xb146b488`, kernel end PA `0xb1ff4000`. Preferred baseline for patch 0018: `research/bt21/xnu` (no nested .git).
- **QEMU verified**: `research/q0017-noprogress` ran **30 seconds**, no visible panic, **zero unknown glyphs**, IRQ exceptions returned normally (4 IRQs, tickless idle). It still waits for CPU completion, so this is NOT a completed boot. Earlier 15s run `research/q0017` captured 122 IRQs, timer value27, GICR_ISENABLER0 `0x08000002`, and CPU WAIT; graphical progress overlay corrupted 13 glyphs. Add **`-noprogress`** to keep the console readable. New runner classifies incomplete/blank decoding explicitly (exit3 with --fail-on-panic), visible panic exits2. Snapshot-only; use regs/GDB to diagnose stalls.
- Current QEMU payload/ADT: **`research/q0017-noprogress.bin` / `research/q0017.adt`**. Run: `python3 tools/qemu-sweet.py research/q0017-noprogress.bin research/NEW-OUT --secs 30 --kernel xnu/out-0017/kernel.development.sweet --fail-on-panic`. Generate fresh seed with mkadt for a new payload. QEMU virt models generic ARM execution, not Qualcomm XPU/bootloader/panel or the phone's SMC PSCI conduit.
- **Prepared phone image**: **`shim/out/shim-boot-0017.img`**, 16,416,768 bytes, SHA256 `51ff7fe30b4a6668c3452ffe1da922c5ac30cb8de60625c2a652587ecbd0ec92`. Phone ADT/payload `shim/out/sweet-0017.adt` / `shim/out/payload-0017.bin` (timer19). Unpacked ramdisk exactly matches payload (`shim/out/check-0017`). Command line **`debug=0xc serial=3 cpus=1 keepsyms=1 -enable_kprintf_spam -noprogress`**. NOT sent to phone this session: known CPU-driver wait should be addressed in QEMU first. Last actual phone boot remains 0013; user's latest photo `IMG_20261015_160033.jpg` confirmed the old PRNG PC=0 panic.
- Direct QEMU/GDB API checks: PRNG 600-byte chunking, buffer bounds, changing output, zero-length reads/writes, user reseed, contended refresh, generator1 init/output PASS again on latest0017 (`research/check-prng17.gdb` / `.log`, guest `research/q0017-api`). Trust-cache unavailable-service/argument/output cases PASS on0015 (`research/check-trustcache.gdb` / `.log`). Platform registration + target/product normal/truncated/zero/null/bounds PASS on0016 (`research/check-platform.gdb`, `research/check-platform3.log`). Different platform ID correctly retains IOPanicPlatform fallback (`research/q0016-negative`). Timer PPI32 and size2 correctly panic (`research/q0017-badppi`, `research/q0017-badsize`); omitted property selects19 (`research/q0017-default`). These are API/bring-up checks, not crypto certification or SMP scheduling validation.
- Local checker **`research/check-patch-order.py`** verifies all17 patches and changed source equality using a temporary upstream git index. Fixtures/logs/artifacts under research are local-only and ignored. For GDB unsigned kernel pointers, mask `int(register_value) & ((1<<64)-1)`; x30/x29 may be rendered signed. Stop at a function entry for manual-call return traps, and discard each manipulated guest after API tests. All fixture QEMU guests have been stopped.


- User wants persistent progress toward iOS 16, commits for completed changes, builds through `gh` / GitHub Actions.
- Keep this file current at every milestone so another agent can resume immediately, including when usage limits interrupt a session.
- Patch 0017 committed/pushed `aa3f991`, Actions `38751507437` running: https://github.com/dipa-studio/ios-sweet/actions/runs/38751507437. Next artifacts: xnu/out-0017, research/bt21, research/run21.log. Do not duplicate.
- Patch 0016 kernel downloaded/checksum verified: SHA256 `d06336c54baa06e0df6561a8bd7df98a9b9f7502c9381c62d1a44c045cd1ce46`, `xnu/out-0016/kernel.development.sweet`; buildtree/log `research/bt20` / `research/run20.log`. QEMU `research/q0016` (10s) prints platform expert registered, zero unknown glyphs, no panic observed BUT stalls (timer mapping still wrong until 0017). Direct actual-kernel GDB tests passed for registered instance and target/product names, including maxLength=1/0 and NULL, sentinels intact (`research/check-platform.gdb`, `research/check-platform3.log`, `research/q0016-api3`). First two fixture attempts used premature/wrong return breakpoints; discarded, corrected fixture uses start-return observation then a function-entry return trap. No phone boot yet.
- Patch 0016 CI `38750733996` PASSED (4m3s); artifacts not yet downloaded/booted. Patch 0017 prepared to fix QEMU timer fidelity BEFORE interpreting future no-panic/stall runs: actual `qemu-system-aarch64 -M virt,gic-version=3,dumpdtb=research/qemu-virt.dtb ...` timer property has virtual PPI 11 => INTID 27, while phone uses INTID 19. Kernel formerly hardcoded 19. New optional /arm-io/gic virtual-timer-intid property selects the PPI (validate exact u32 and 16..31); missing property retains phone default 19. One RO-late global drives GIC enable and sleh_irq dispatch. tools/mkadt.py emits phone19/QEMU27. Both C TUs compile (`research/timer-objs`), ADT serialize/parse checks confirm values/addresses, all 17 patches apply and match. Sandbox `research/bt19/xnu`, originals `research/pre0017`; initial local sleh compile failed due read-only exported header not updated, fixed export and BOTH recompiled successfully. CI exports normally.
- Architecture correction for next agent: CURRENT SWEET board_config does NOT define USE_APPLEARMSMP; it compiles the legacy IOCPU path, not cpu_boot_thread/IOPMGR AppleARMSMP. Existing roadmap mentions AppleARMSMP as a future approach. Do not look for gCPUIC/gAIC/gPMGR globals in the current kernel: they are absent. Determine the actual CPU-init wait after platform registration before choosing the next driver architecture.
- Patch 0016 committed/pushed as `0dcdf5c`; Actions `38750733996` running: https://github.com/dipa-studio/ios-sweet/actions/runs/38750733996. Next artifacts: `xnu/out-0016`, `research/bt20`, `research/run20.log`.
- Patch 0016 implemented: new `iokit/Kernel/arm/SweetPlatformExpert.cpp`, arm64 source list, built-in personality in KernelConfigTables.cpp guarded by ARM64_BOARD_CONFIG_SWEET. Matches only xiaomi,sweet at score 10000, keeps IOPanicPlatform fallback for other hardware. Uses IODTPlatformExpert base initialization/power domain and createNubs CPU logical-ID annotation; overrides top-level publishing because base requires nonexistent Apple NVRAM /options. Publishes real CPU/top-level nodes, provides bounded target/product names, and registers the platform service. GIC/PMGR and arm-io child-bus drivers remain separate work. Both C++ TUs compile (`research/platform-objs`), all imports resolve against 0015/own objects, all 16 patches apply and sources match. Sandbox `research/bt19/xnu`; originals `research/pre0016`. NEXT: full Actions/QEMU; inspect CPU boot waits after the platform registers, do not equate absence of panic with successful boot.
- Patch 0015 CI `38749549779` PASSED (4m3s), checksum verified. Kernel `xnu/out-0015/kernel.development.sweet`, SHA256 `ca1b424a596c7058550ad1659080a333e7643270f019656401d80bf2b876645f`; buildtree/log `research/bt19` / `research/run19.log`. QEMU `research/q0015` (10s, zero unknown glyphs) passes trust-cache handling and machine lockdown, then panics `Unable to find driver for this platform: "xiaomi,sweet" @IOPlatformExpert.cpp:2319` (IOPanicPlatform fallback). Next concrete work: add a built-in SWEET IODTPlatformExpert personality/class; keep the fallback for mismatched platforms. No phone boot yet.
- Direct trust-cache API checks PASSED in the actual 0015 kernel under QEMU/GDB (`research/check-trustcache.gdb`, `research/check-trustcache.log`, `research/q0015-api`): runtime pointers NULL, hash/UUID queries return NOT_FOUND, typed/untyped/legacy loads return NOT_SUPPORTED, capabilities outputs zero and bounds preserved, invalid-argument cases still reject. Second PRNG check also verifies contended refresh returns immediately (`research/check-prng2.log`, `research/q0014-api2`).
- Patch 0015 committed/pushed `8f851d4`, Actions run `38749549779` running: https://github.com/dipa-studio/ios-sweet/actions/runs/38749549779. Do not duplicate.
- Direct PRNG API checks passed in the REAL 0014 kernel under QEMU/GDB, stopped before trust-cache init (`research/check-prng.gdb`, log `research/check-prng.log`, guest `research/q0014-api`). Invoked read_random for 600 bytes (chunking and buffer sentinel intact), repeated output differed, zero-length read/write succeeded, write_random(64-byte input) succeeded, secondary generator 1 initialized and generated distinct output. QEMU log has no exceptions during these checks; guest was discarded after the tests. This tests API behavior, not a cryptographic certification or SMP scheduling.
- Patch 0015 implemented in `bsd/kern/kern_trustcache.c`: SWEET with missing Image4/AMFI marks both runtime pointers NULL and logs service unavailability. Existing static loader handles NULL. Public load APIs return KERN_NOT_SUPPORTED; hash/UUID queries return KERN_NOT_FOUND; capabilities outputs are zero with KERN_NOT_SUPPORTED. Invalid-input checks remain, and Apple paths/available-provider initialization retain existing behavior. No trust is granted. Local arm64 compile passed (`research/trustcache-objs`), all 15 patches apply and sources match. Sandbox `research/bt18/xnu`, baseline `research/pre0015`. Next: Actions/QEMU and direct unavailable-service API checks using GDB.
- Patch 0014 CI `38748543058` PASSED (4m0s), artifact checksum passed. Kernel `xnu/out-0014/kernel.development.sweet`, SHA256 `741de20c851755d333759d7e668346f3edb4f325efac4cc7c142d80d1f5ff75c`; buildtree/log `research/bt18` / `research/run18.log`. QEMU run `research/q0014` (10s, zero unknown glyphs) prints `SWEET PRNG: HMAC-SHA256 registered`, passes commpage initialization, loads vnguard policy, THEN panics `image4 interface not available @kern_trustcache.c:253`. PC=0 fault FIXED IN QEMU. No new phone boot performed.
- Next work: SWEET currently has neither AppleImage4 nor AMFI. `trust_cache_runtime_init` unconditionally requires both; unlike BCM2837, SWEET enters this startup path. Investigate an explicitly unavailable trust-cache runtime with rejected loads/no query matches while providers are absent; preserve all Apple-platform checks. Merely skipping the startup call would leave later AMFI/IMG4 dereferences unsafe. Existing load_static_trust_cache already handles trust_cache_rt == NULL.
- QEMU runner now supports `--kernel MATCHING_KERNEL --fail-on-panic`: runtime font extraction from the payload produces exact `fb.txt`, plus `result.json`; a visible panic returns 2. Baseline 0013 re-run `research/q0013-text` detects the same NULL callback panic with zero unknown glyphs. Synthetic glyph roundtrip (including literal `?`) and invalid-VA rejection passed. Screen rows remain circular, not a full log; `no_panic_observed` does not prove successful boot. README has the invocation.
- Patch 0014 committed/pushed as `be61f99`; Actions run `38748543058` is running: https://github.com/dipa-studio/ios-sweet/actions/runs/38748543058. Do not start a duplicate build.
- 2026-10-15 active: hardware photo `IMG_20261015_160033.jpg` confirms the same PC=0 instruction-fetch abort as QEMU (LR `0xfffffe0007443fe4` = read_random). Independently reproduced with kernel 0013 in `research/q0013` (8-second run); prior allocator fix works. Latest tooling commit reviewed: `8d66d2d`.
- Patch 0014 implemented: registers a built-in HMAC-SHA256 DRBG provider at EARLY_BOOT/FIRST, before commpage creation. A shared mutex serializes output/reseed across CPUs (correctness first; no per-CPU scaling yet), initgen validates CPU identities, refresh uses try-lock and the existing entropy filter/health tests. SWEET entropy accumulation and write_random now use the built-in SHA256 directly; no incomplete g_crypto_funcs table is registered. The existing bootloader-seed requirement remains enforced.
- Local validation: both PRNG translation units compile to arm64 objects in `research/prng-objs`; no SHA256 wrapper imports remain. All 14 patches apply in CI order and resulting PRNG sources match local inputs. Sandbox `research/bt17/xnu`, originals `research/pre0014`, checker `research/check-patch-order.py`. NEXT: Actions kernel build, download to `xnu/out-0014`, run the QEMU payload before requesting another phone boot. Baseline QEMU ADT/payload are `research/q0013.adt` / `research/q0013.bin`.
- 2026-10-15 08:15 QEMU EMULATION WORKS (`tools/qemu-sweet.py`, see "QEMU emulation" below). Patch 0013 VERIFIED in QEMU: boot passes kmem_crypto_init and ulock_initialize. NEXT BLOCKER (reproduced in QEMU, expected on hardware too): `pmap_create_commpages -> random() -> RandomULong -> read_random -> prng_funcs.refresh == NULL` (instruction fetch abort at pc 0, lr read_random+0x34). Nobody calls `register_and_init_prng` (closed corecrypto kext does it on Apple). Fix = patch 0014: SWEET-registered cckprng_funcs provider (osfmk/prng/prng_random.c); note random_cpu_init also panics while !prng_ready. The 07:26 hardware boot of 0013 will most likely show this same panic.
- Previous hardware boot: patch 0013 (`a3a46e2`) CI `38686345689` PASSED (3m44s), image `shim/out/shim-boot-0013.img` was temporarily booted on 2026-10-15 at 05:26 UTC: send OKAY (0.407s), boot OKAY (0.134s), total 0.546s. Superseded by the hardware/QEMU PC=0 observation and patch 0014 work above.
- Latest kernel implementation commit: `8f851d4`. Latest successful kernel CI: `38749549779` (patch 0015), https://github.com/dipa-studio/ios-sweet/actions/runs/38749549779.
- CURRENT image: `shim/out/shim-boot-0013.img`, 16,412,672 bytes, SHA256 `110d1c46aee4b60253db24b6535e9781c4cf0fd25ca2a70e9016cf81378cea25`. Kernel `xnu/out-0013/kernel.development.sweet`, SHA256 `f0b1d375995316c550ce7014ff234d8271e9b9ac2857795ceff41b76ba2cd740`, plain arm64. CI log confirms 0013 applied; checksums passed. Entry PA `0xb146b488`, kernel end PA `0xb1ff4000`.
- Current log/buildtree: `research/run17.log`, `research/bt17` (extracted, no nested .git; preferred baseline for patch 0014). Payload/ADT: `shim/out/payload-0013.bin`, `shim/out/sweet-0013.adt` (includes /defaults). Unpacked ramdisk byte-compared with payload in `shim/out/check-0013`.
- Patch-0012 original image: `shim/out/shim-boot-0012.img`, 16,412,672 bytes, SHA256 `cf4b8ec4a65a51888d71c17d09cd0831d6b761b90e2531fdb8e575c32f4fd24a`. Kernel `xnu/out-0012/kernel.development.sweet`, SHA256 `69b78f49f6459cc63a0af44e7cf73c1779ef72130ef72b12ae86c88183ffc742`; checksums passed and sweet_early_relocate symbol present. Entry PA remains `0xb146b488`, kernel end PA `0xb1ff4000`.
- Patch-0012 log/tree: `research/run16.log`, `research/bt16` (extracted, no nested .git; preferred baseline for next patch). CI log confirms 0012 applied. Payload `shim/out/payload-0012.bin`, ADT `shim/out/sweet-0012.adt`; packed ramdisk byte-compared with payload in `shim/out/check-0012`.
- Active payload command line: `debug=0xc serial=3 cpus=1 keepsyms=1 -enable_kprintf_spam`.
- Latest observed photo: `/home/dipa/Downloads/IMG_20261015_071346.jpg` (local only). Stages 9 (kernel framebuffer VA), 10 (TTBR0 off/TLB flush), 11 (physmap table pointers) and 12 (calling pmap_bootstrap) all visible. Persistent diagnostics are VERIFIED ON HARDWARE.
- pmap.c:1987 is the assert after SecureDTLookupEntry(NULL, "/defaults", &entry). The pmap-max-asids property itself is optional; an empty /defaults uses XNU's MAX_ASIDS. Do not bypass the assertion or guess an ASID limit.
- Previous payload-only fix image: `shim/out/shim-boot-0012-defaults.img`, SHA256 `3ff61a268853c6ea7cbf284833f1346a1d791980ca366b6e1a215a86e040512b` (16,412,672 bytes). Same kernel/CI as 0012; ADT 2516 bytes (`shim/out/sweet-0012-defaults.adt`), root /defaults present with no ASID override. Payload `shim/out/payload-0012-defaults.bin`; unpacked ramdisk exactly matches payload (`shim/out/check-0012-defaults`). This boot reached the allocator crypto NULL-pointer fault below.
- Latest hardware photo: `/home/dipa/Downloads/IMG_20261015_071608.jpg` (local only). Normal serial framebuffer console works. VM bootstrap/zone initialization, logging, scheduler, IPC, KDP and ulock_initialize print before the kmem_crypto_init data abort. gPanicBase warnings are expected because PLATFORM_PANIC_LOG_DISABLED is configured, and are not the faulting call.
- Faulting instruction: `ldr x0, [x8, #0x150]` in crypto_random_kmem_ctx_size; x8 = NULL g_crypto_funcs. Source: libkern/crypto/corecrypto_rand.c and osfmk/vm/vm_kern.c:2448. rand.h explicitly permits NON-cryptographic kmem RNGs, but requires no locking in generation and context size <=256. Do not substitute read_random here: the global PRNG provider is also unregistered and kmem generation must remain lock-free. early_random may seed contexts during single-CPU bootstrap; it uses the built-in HMAC-SHA256 DRBG with the host-generated ADT seed.
- Patch 0013 keeps the replacement entirely private to vm_kern.c: SplitMix64 state is 8 bytes per CPU/sizeclass, initialized using early_random. Uniform selection uses rejection sampling to avoid modulo bias. Other platforms retain the original corecrypto calls; SWEET's generic crypto APIs/registration remain untouched. Reference: https://prng.di.unimi.it/splitmix64.c (Sebastiano Vigna, public domain).
- Validation: vm_kern.c compiles to arm64 (`research/kmem-rng-objs`, using `research/run16.log` + `research/bt16`). Undefined symbols include early_random and NO crypto_random_* references. All 13 patches apply in CI order and match the checked source. Original saved as `research/vm_kern.pre0013.c`.
- RNG host checks: extracted actual new helper in `research/kmem-rng-check.c`; 16,384 outputs match the author's downloaded reference (`research/splitmix64-reference.c`), 147,456 bounded outputs satisfy their limits (including 1 and UINT64_MAX), and a forced rejection advances correctly. Full kernel crypto services and the registered kernel PRNG provider remain future work; this patch only supplies the allocator RNG contract.
- Patch-0011 artifacts: kernel `xnu/out-0011/kernel.development.sweet`, log `research/run15.log`, extracted buildtree `research/bt15` (no nested .git). CI log confirms patch 0011 applied; artifact checksums passed. Kernel is plain arm64, entry VA `0xfffffe000746b488` -> PA `0xb146b488`, kernel end PA still `0xb1ff4000`.
- Patch-0011 image: 16,412,672 bytes, SHA256 `29ad5cbfc752473de4af2c471a24a8b34f92da4bff5afec65c614b90cd3ad53a`. Kernel SHA256 `8ac3a956894b09f7bd0d890de8c5de38c65513287feb1e1bcd12db8ca772ee5c`. Payload/ADT in `shim/out/payload-0011.bin`, `shim/out/sweet-0011.adt`. Header unpacked/checked in `shim/out/check-0011`.
- First patch-0011 attempt timed out waiting for FASTBOOT; superseded by the successful send/boot recorded above. Do not repeat the boot before the user reports the current screen.
- Patch-0011 photo: `/home/dipa/Downloads/IMG_20261015_070218.jpg` (local only). Visible stages 1-8 and old red shim text; entry PA B146B488, boot args PA B1FF8000 / top B1FFC000. No evidence yet locating execution after stage 8.
- Patch-0012 sandbox: `research/bt15/xnu` (NO nested .git). Proposed permanent debug VA: VM_MIN_KERNEL_ADDRESS + ARM_TT_L2_SIZE, in the reserved gap below gVirtBase and above low globals; map the same PA framebuffer as Normal-NC in the final TTBR1 before arm_vm_physmap_init changes phystokv(). Keep the early panic sink until normal kprintf startup.
- Patch 0012 validation: all 4 changed C translation units compiled to arm64 objects in `research/post-ttbr0-objs`; internal header export added to osfmk/arm64/Makefile and recreated locally in EXPORT_HDRS for pe_serial.c. All 12 patches apply in CI order and match all 6 edited files. Baselines are saved under `research/pre0012/`.
- Actual mapping-helper host model (`research/early-map-check.c`, barrier stubbed only for host compilation) confirms: VA `0xfffffe0002000000`, L1 index 2016, L2 index 1; descriptor `0x006000009c000605` = framebuffer PA, Normal-NC, outer-shareable, EL1 RW, PXN+UXN. All other L2 entries preserved. The gap is excluded by ARM_LARGE_MEMORY's pmap_virtual_region(0).
- Next boot command line MUST add `-enable_kprintf_spam`: DEVELOPMENT disables kprintf_output by default even when DB_KPRT is set (`pexpert/arm/pe_kprintf.c`). Planned command line: `debug=0xc serial=3 cpus=1 keepsyms=1 -enable_kprintf_spam`.

### Patch 0012 screen legend (after original stages 1-8)
- 9: kernel framebuffer VA live; 10: TTBR0 off / TLB flushed; 11: physmap pointers rebound.
- 12: calling pmap_bootstrap; 13: pmap_bootstrap returned; 14: early I/O page tables ready; 15: arm_vm_init returned.
- 16: calling serial_init; 17: fbcon config read / mapping; 18: fbcon mapping returned; 19: serial_init returned; 20: kprintf startup complete.
- Normal serial initialization clears the screen, so earlier stages may disappear before 19. If serial exists, early console disables after 20; otherwise early panic output stays enabled.
- Local source sandbox: `research/bt13/xnu` (git baseline `623b060`, patches 0001-0008 already in baseline; uncommitted export edits correspond to patch 0009). Preserve those edits when producing patch 0010.
- Previous compile log/tree: `research/run13.log`, `research/bt13`; previous kernel: `xnu/out/kernel.development.sweet`. New successful log/tree: `research/run14.log`, `research/bt14`; new kernel: `xnu/out-0010/kernel.development.sweet`.
- Current device access: patch-0012 image was temporarily started from FASTBOOT; no adb connection is expected. Never flash partitions for bring-up; use `fastboot boot` with the shim image.
- Patch `0010` lives in `xnu/patches/0010-sweet-early-framebuffer-debug.patch`. Its exact compiled sources are under `research/bt13/xnu`; generated objects are in `research/early-objs`.
- Local checks passed: all 5 changed/new translation units compiled to arm64 Mach-O objects; new console only imports `_doprnt` and `iso_font` (both exist in the previous kernel). All 10 patches applied to a temporary upstream git index in CI order, and all 7 resulting changed source files matched the local compile inputs.
- Reproduce changed-file compilation: `XNU_CC_OBJDIR="$PWD/research/early-objs" python3 tools/xnu-cc.py research/run13.log research/bt13 arm_init.c arm_vm_init.c kern/debug.c arm64/start.s osfmk/arm64/sweet_early.c --per-file` (create the output directory first). The helper now accepts explicit new source paths absent from the old artifact's Makefiles and rejects empty selections.
- Device command result: `adb reboot bootloader`, then `timeout 30s fastboot boot shim/out/shim-boot-0010.img`: send OKAY (16028 KB), boot OKAY, total 0.541s. This confirms bootloader acceptance only, not XNU progress.
- The successful boot above was on 2026-10-14. On 2026-10-15, `timeout 45s fastboot boot ...` timed out waiting for a device; no image was sent. Boot image SHA256 rechecked and unchanged. No new build is needed to repeat the trial.
- Earlier retry: `timeout 90s fastboot boot shim/out/shim-boot-0010.img` timed out (exit 124). This is superseded by the successful 2026-10-15 repeat boot recorded above; do not repeat it until the user reports the screen.
- User observation confirms MMU-on C entry, platform expert, CPU topology/bootstrap, startup bootstrap and cpu_init all complete. Failure is within arm_vm_physmap_init (non-XNU_MONITOR branch), before stage 8 / TTBR0 teardown. Old red shim text remains behind the early console; this is expected because only written rows are cleared.
- New edit/compile sandbox is `research/bt14/xnu` (extracted artifact, NO nested .git; `git diff` there would act on the parent project). Use a saved baseline file / generated unified diff, or explicitly initialize a local baseline before editing. `research/bt13/xnu` does have its own baseline git repo.
- Exact user-reported panic: `arm_vm_init.c:1606 Assertion failed: (temp_ptov_table[ptov_index - 1].va + temp_ptov_table[ptov_index - 1].len) <= physmap_end`.
- Root cause: MacOSX build sets `ARM_LARGE_MEMORY=1`; `XNU_MONITOR` is off. Block alignment in arm_vm_physmap_slide can add gaps, but the non-PPL large-memory physmap_end omitted the padding already present in the small-memory branch. Patch 0011 reserves PTOV_TABLE_SIZE*ARM_TT_TWIG_SIZE (8*32MB) in both the aperture bound and its L1 allocation; monitor/PPL builds retain zero padding. The assertion is preserved.
- Validation: `arm_vm_init.c` compiled to an arm64 object using `research/run14.log` + `research/bt14` (object in `research/physmap-objs`). All 11 patches apply in CI order and produce exactly that source. Host harness `research/physmap-check.c` extracts the real XNU slide function with page-table-write stubs: all 65,536 page-aligned slides within 1GB checked against the current kernel memory layout; old bound fails 65,504 cases, padded bound fails zero; worst overrun 0x1ffc000 bytes. Baseline source saved as `research/arm_vm_init.pre0011.c`.
- CI: https://github.com/dipa-studio/ios-sweet/actions/runs/38638702083 (success; artifacts and full log downloaded).
- New image: `shim/out/shim-boot-0010.img` (16,412,672 bytes, SHA256 `ed2c270e0081bad5ff517be415f9bfe8805463aea7866732203fa97ac737e64e`). Previous image preserved as `shim/out/shim-boot-pre0010.img`.
- New kernel SHA256: `3ee05270cc291c49589a101678f904b1b69cb2f2575e05398bce8a4e052f409a`. Artifact checksums passed; arm64 (not arm64e), early-console symbols present. Payload entry VA `0xfffffe000746a488` -> PA `0xb146a488`; kernel end PA `0xb1ff4000`. Command line remains `debug=0xc serial=3 cpus=1 keepsyms=1`.

### Patch 0010 screen legend
- Bottom-left white 64x32 tile: assembly entered `start_first_cpu`, before page tables/MMU.
- Text `SWEET EARLY 1`: entered `arm_init` with MMU on; 2: platform expert done; 3: CPU topology done; 4: CPU bootstrap done; 5: startup bootstrap done; 6: CPU init done; 7: entering `arm_vm_init`; 8: leaving bootstrap TTBR0.
- `SWEET EARLY PANIC:` prints a copy of panic arguments before normal panic handling needs per-CPU/thread state.
- In patches 0010/0011 the console disabled before TTBR0 invalidation; patch 0012 replaces that with a persistent kernel VA alias and diagnostics through normal serial/kprintf startup (see its legend above).
- Screen contents require a physical observation from the user: adb cannot capture a framebuffer after Android has been replaced by a bare-metal kernel.

## QEMU emulation (2026-10-15)
- `tools/mkadt.py OUT.adt --qemu` = same ADT with QEMU virt GICD 0x08000000 / GICR 0x080a0000 / CNTFRQ 62.5 MHz.
- `tools/qemu-sweet.py PAYLOAD OUTDIR [--secs N] [--hmp "x /8gx ADDR"] [--gdb]`: host-side copy of shim/loader.c
  (segments + ADT + boot_args at their PAs, 6-instruction stub sets x0 and jumps), `-M virt,gic-version=3 -cpu cortex-a76`
  (same ID_AA64MMFR0 as Kryo 470), 4G RAM so 0x9c000000 fb and 0xb0000000 kernel are plain RAM.
  Outputs `fb.png` (the screen), `regs.txt`, `qemu.log` (exceptions with ESR/FAR/ELR). `--gdb` halts with a stub on :1234
  (system `gdb` + `set architecture aarch64`, `hbreak *VA` works with the MMU on).
- Not emulated: Qualcomm XPUs, ABL, real panel, PSCI conduit (QEMU virt uses hvc). Hardware still decides those.
- Example: `python3 tools/mkadt.py /tmp/q.adt --qemu && python3 tools/mkpayload.py xnu/out-0013/kernel.development.sweet /tmp/q.adt /tmp/pq.bin --cmdline 'debug=0xc serial=3 cpus=1 keepsyms=1 -enable_kprintf_spam' && python3 tools/qemu-sweet.py /tmp/pq.bin /tmp/q`

## Layout
- `backup/`  partition dumps + full sdb..sdf LUNs, `SHA256SUMS` (all verified on-device == local)
- `dtb/`     live FDT (from OrangeFox), PixelOS boot.img dtb, dtbo, dts versions
- `shim/`    bare-metal boot shim (`./build.sh` -> `out/shim-boot.img`)
- `research/` mainline sm7150 dts, XNU pe_fiq.c etc, PocketDarwin patches
- `tools/unpack_bootv2.py`

## Device access
- No root in PixelOS 17 (user build, adb root disabled). Root = `fastboot boot recovery/recovery.img` (OrangeFox R12.0_2, temp boot, not flashed).
- `fastboot boot` works for stock boot.img, OrangeFox, and our shim.
- Shim resets itself via PSCI SYSTEM_RESET; IMEM restart_reason 0x77665500 is seen
  (bootreason=bootloader) but ABL still boots Android, so it does not stop in fastboot.

## Hardware facts (live DT + shim measurements)
- Framebuffer (ABL cont splash): 0x9c000000, 1080x2400, stride 4320, a8r8g8b8, panel is DSC *video* mode (no kick needed).
- RAM: 0x80000000+2G, 0x100000000+0xfcc00000. Live reserved-memory = PixelOS base dtb + sweet dtbo fixups.
- GICv3: GICD 0x17a00000, GICR 0x17a60000 (stride 0x20000, 8 PEs). GICD_TYPER 0x007B041D: SecurityExtn=1 (DS=0).
  ABL leaves GICD_CTLR = 0x10 (ARE_NS on, groups off). Writing 0x13 reads back 0x12: EnableGrp1A (bit1) is the one that matters.
- GIC Group 1 VERIFIED (shim 2c): vtimer INTID 19 = 30 IRQs/300ms, ptimer INTID 18 = 30, SGI 1 to self = 10/10.
  ICC_SRE=1 already, ICC_CTLR 0x8440, priority/enable writes stick. GICR_IGROUPR0 and GICD_IGROUPRn read 0 from NS
  even though Group 1 delivery works (RAZ in NS view) - do not use them as a health check.
  INTID 28 shows pending constantly (unknown PPI 12).
- Timer 19.2 MHz. Qualcomm PPI numbering: secure-phys/phys/virt/hyp = PPI 1/2/3/0 -> vtimer INTID 19, ptimer 18 (NOT 27/30).
- PSCI 1.1 via SMC, SMCCC 1.1. CPU_ON ok; SYSTEM_SUSPEND and SYSTEM_RESET2 unsupported.
- SMP: CPU_ON works for all 7 secondaries (MPIDR 0x81000n00).
- Entry EL1, MMU off, x0 = DTB (magic ok). ID_AA64MMFR0 = ...101122: 16K granule YES, 4K YES.
- No serial console: debug UART SE is in SPI mode on sweet. Screen is the only debug channel.

## XNU implications
- XNU GICv3 path (pexpert/arm/pe_fiq.c, VMAPPLE) puts the timer (PPI 27) in Group 0 = FIQ. With SecurityExtn=1,
  Group 0 is secure -> impossible from NS EL1. Need: Group 1 IRQ, ICC_IGRPEN1, INTID 19, and the timer handled in the IRQ path.
- XNU VMAPPLE PSCI uses `hvc`; sweet needs `smc`.
- PocketDarwin NonAppleGenericCpu.patch only swaps -mcpu=apple-h7 for -march=armv8-a.

## Milestone 3 (2026-10-14): 16K MMU verified
- ABL loads the Image at 0x80080000 (base 0x80000000 + 0x80000) regardless of text_offset=0.
- 16K granule, T0SZ=28 (L2 start, 32MB blocks), MAIR 0x44ff00, TCR 0x1409CB51C, PARange=2 (40-bit PA).
- Only own image pages WB (Qualcomm XPUs: never map carve-outs cacheable); fb Normal-NC; rest Device.
- AT S1E1R checks all as expected; unmapped -> translation fault L2.
- Fill fb: 110 ms (MMU off) -> 3.5 ms (NC). Memory loop 70 ms -> 0.7 ms. vtimer + SGI IRQs still fine with MMU on.

## XNU loader design notes (xnu-8796)
- Entry: `_start` -> `start_first_cpu`, x0 = boot_args (PA), MMU off, EL1. boot_args: Revision/Version 2,
  virtBase/physBase/memSize/topOfKernelData, Boot_Video (fb 0x9c000000, rowBytes 4320, 1080x2400, depth 32),
  deviceTreeP/Length (ADT), CommandLine[608], bootFlags, memSizeActual.
- start.s maps [kernel mach header .. physBase+memSize) with cacheable BLOCKS. On Qualcomm every XPU carve-out
  must therefore lie below the kernel: use physBase = 0xb0000000 (above ramdump_fb 0xaf000000+16M,
  cdsp_sec, qseecom), end before rmtfs 0xfde01000 -> memSize ~0x4d000000 for bring-up.
- Base ADT: iPhone 8 d20ap DeviceTree from iOS 16.7.16 IPSW (tools/remotezip.py + tools/adt.py; LZFSE payload).
  Template values are empty: the loader must fill chosen/*, memory-map, cpu*/reg etc. like iBoot.
- XNU build: GitHub Actions (dipa-studio/ios-sweet, xnu.yml) via blacktop/darwin-xnu-build, MACOS_VERSION=13.5.
  New-clang fixes in xnu/patches; Xcode 16 iig is incompatible (IORPC.kernelContent) -> macos-14 runner, oldest Xcode.

## Kernel architecture plan (SWEET machine config)
- First stock build (VMAPPLE) is arm64e (PAC). Kryo 470 = ARMv8.2, no PAC -> SWEET must build plain arm64
  (HAS_APPLE_PAC is only defined for __arm64e__, so arm64 drops PAC automatically).
- Template: VMAPPLE (16K pages, GICv3 code in pe_fiq.c) minus APPLEVIRTUALPLATFORM hypercalls/paravirt PAC,
  plus BCM2837 (generic ARM: no APPLE_ARM64_ARCH_FAMILY Apple sysregs). Do not link the KDK lib<cfg>.os.*.a.
- Timer: XNU expects it on FIQ (sleh_fiq -> rtclock_intr). SWEET: GIC Group 1, so sleh_irq must ack ICC_IAR1,
  route INTID 19 to the same timer path, SGIs to cpu_signal_handler, EOI via ICC_EOIR1.
- SMP/interrupts: open-source AppleARMSMP (USE_APPLEARMSMP) needs an IOInterruptController (AIC role) and an
  IOPMGR (CPU power -> PSCI CPU_ON via SMC). Plan: built-in IOKit classes (SweetGIC, SweetPMGR, platform
  expert) compiled into the kernel and matched via iokit/KernelConfigTables.cpp -> no closed kexts needed.
- Debug: xnu patch 0003 sweet-fbcon = kprintf drawn on the framebuffer (ADT node "sweet-fbcon").
- ADT /arm-io ranges must not map to parent 0 (pe_arm_get_soc_base_phys()==0 disables serial): use parent 0x1000000.

## Status 2026-10-14 late: first XNU boot attempt
- SWEET kernel builds (CI run 38635343732, patches 0001-0009). Verified offline: arm64, no PAC, no >v8.2 code,
  70300 classic relocs all in range (slide 0 = no loader work), entry = __start.
- Boot: shim loader worked (initrd 0x846F0000-0x855FE3E0, BOOTARG 0xB1FF8000, JUMP 0xB146A488) but screen stayed
  red -> xnu died/hung before serial_init (fbcon). kprintf is a no-op before STARTUP_SUB_KPRINTF.
- Historical next-step plan (patch 0010, now implemented and built; see active handoff above): early fb debug channel
  1. start.s start_first_cpu (after mov x20,x0 / mov x21,#0): PA marker band (MMU off, direct store to 0x9c000000).
  2. start.s after both create_bootstrap_mapping calls: add ONE block entry to the existing V=P L2 table
     (x25 + 2*PGBYTES; do NOT call create_bootstrap_mapping again: fb and RAM share L1 entry 0, it would replace
     the L2 table). Entry = TYPE_BLOCK|VALID|SH(OUTER)|ATTRINDX(CACHE_ATTRINDX_WRITECOMB=1)|AF|PNX|NX|0x9c000000,
     index = (va & ARM_TT_L2_INDEX_MASK) >> ARM_TT_L2_SHIFT.
  3. new osfmk/arm64/sweet_early.c (+files.arm64 entry): sweet_early_mark(n) colored bands at screen bottom and
     sweet_early_putc using iso_font via VA=PA while the bootstrap TTBR0 is live; disable before
     arm_vm_init's set_mmu_ttb(invalid_ttep) (arm_vm_init.c:2148).
  4. markers in arm_init after PE_init_platform, ml_parse_cpu_topology, cpu_bootstrap, kernel_startup_bootstrap,
     cpu_init, before arm_vm_init.
  5. panic hook at top of panic_trap_to_debugger: va_copy + _doprnt(fmt, &copy, sweet_early_putc, 16).
  Verify with tools/xnu-cc.py (compile+symbols) and patch-order simulation before the single CI run.
