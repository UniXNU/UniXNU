# Redmi K60 \(mondrian/SM8475\): UniXNU UEFI bring-up

[Emilelu/UniXNU-mondrian](https://github.com/Emilelu/UniXNU-mondrian)

<div v-pre>

Redmi K60 \(mondrian/SM8475\). Format 2 device: the kernel builds and prelinks, the payload and the boot image still need the board ADT and the hardware bring-up.

Source record: [porting.toml](https://github.com/Emilelu/UniXNU-mondrian/blob/5d8a09a58c86585f008ecb0c12611c2145c03f3f/porting.toml), `5d8a09a58c86585f008ecb0c12611c2145c03f3f`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `implemented` |
| [Firmware and boot](#firmware) | `device-verified` |
| [CPU and interrupts](#cpu) | `implemented` |
| [Memory and DMA](#memory) | `implemented` |
| [Storage and root](#storage) | `implemented` |
| [Display](#display) | `implemented` |
| [Input](#input) | `device-verified` |
| [GPU](#gpu) | `planned` |
| [Network](#network) | `planned` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `planned` |
| [Image assembly](#packaging) | `host-verified` |
| [Diagnostics](#diagnostics) | `device-verified` |
| [cellular](#cellular) | `planned` |

## Configuration {#configuration}

`implemented`

Components: `ArmDTPlatform`, `ArmCpu`, `XnuPrelink`.

### Hardware and dependencies

- Identify the configuration hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for configuration.

### Procedure

- Follow the configuration stage in the porting guide and record the actual commands.

### Development findings

- Migrated from format 1 on 2026-10-28: board.toml is schema\_version = 2 with soc\_source sm8475 and os\_profile ipados-16.6.1-20G81, the SM8475 resources live in UniXNU-sm8475-common, and the board wiring in dts/mondrian.dts.
- Fork audit 2026-10-31: mzyxsl daed6b5d44e3c62978cc0fce4e876ded2a57afc9 imported with provenance. board.toml uses an exact trust-cache list; unixnu.lock matches the explicit SM8475 feed pin. The current payload reader also accepted an exactly equal scalar hash, so the list is schema hardening rather than a proven former build blocker.

### Completion criteria

- All source pins resolve; every selected component has a record; status shows the intended overrides and patch order.

### Current limits

- Hardware inputs and implementation are pending for this board.

### Next action

- Inventory the required configuration inputs before implementation.

### Evidence

- `source`: [schema\_version = 2 resolves through the arch, SM8475, 20G81 and device layers; status reports three components and 83 ordered patches](https://github.com/Emilelu/UniXNU-mondrian/blob/5d8a09a58c86585f008ecb0c12611c2145c03f3f/board.toml)

## Firmware and boot {#firmware}

`device-verified`

### Hardware and dependencies

- Identify the firmware and boot hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for firmware and boot.

### Procedure

- Follow the firmware and boot stage in the porting guide and record the actual commands.

### Development findings

- 2026-11-12 boot packaging regression: cand12 \(cba1c0ecad1858a251abc241f5a17989580749a233d5d0cdacc8764869e70c4f\) returned to fastboot without a CDC console. The v4 header declares a 1584-byte structure, but firmware starts at the fixed 4096-byte page; work/touch-gpu/repack-boot.py incorrectly used 1584 as the slot start. The resulting payload begins at 550448 instead of 552960, overwriting the compressed firmware tail. zlib.decompressobj\(31\) accepts cand7 with EOF and an appended FDT, but rejects cand12 with an incorrect data check. The cand12 FAT payload is byte-identical to the current payload.img \(49b60bcbc51307ff449e24e72e1c76dd12621c3ff8d156ebceac4a3d9a126a95\), so recovery can retain all current kernel and userland changes.
- Prior art: scripts/build-bootimg.py:29-47 and the same-SoC work/refs/pong-ios16/scripts/build-bootimg.py:29-47 already use a 4096-byte firmware start, aligned ramdisk and signature offsets. Reuse that v4 layout rather than rolling back functional patches.

### Completion criteria

- Firmware image builds, enters UniXNU, publishes the framebuffer and preserves the documented memory reservations.

### Current limits

- cand15 restores actual iOS desktop with the current functional kernel unchanged. Touch remains unavailable: live log reaches SE4 protocol1/interfaces1 \(FIFO disabled\) and stops because bitbang-pins roles are absent; no device handshake or contact was observed. Battery correctly reports no authenticated PAS1 handoff and does not publish a fabricated source. GPU execution is not qualified.

### Next action

- Keep the repaired v4 layout, UFS-only payload and complete CPU/UFS ADT contracts. cand16 native lockscreen is verified, but user sees Press Home to Open, black wallpaper and no touch. Native buttons type2/no menu plus stale MobileGestalt cache invalidation and genuine WallpaperKit7410 selection are implemented for the next candidate; verify actual policy and wallpaper pixels.

### Evidence

- `device`: [Darwin 24 loader boots the board every time: green bar from Entry.S, then the upstream probe's blue and magenta bars at the kernel entry and just before the MMU comes on. Confirms the 0x480 boot\_args ABI, ADT handoff and framebuffer are live on hardware. A readable kernel panic followed at k60\_fontscale=4 until the CPU start order was fixed; that panic is gone.](https://github.com/Emilelu/UniXNU-mondrian/blob/5d8a09a58c86585f008ecb0c12611c2145c03f3f/docs/reference/ROUTE-A-18-STATE.md)
  Command: <code>scripts/k60-device.sh boot /mnt/d/Android/k60-ios/boot-darwin24-bc8.img</code>. Revision: `d2af811a6dc9c6225de586e1615ca3824e2edce4`.
- `device`: [console-20261112-103539.log68357B: CDC COM8, original launchd, framebuffer swaps and heartbeats through150s. User confirms iOS desktop, no touch. Image7489cf3172bfd15db989775d900cff367bbac0172f0c5c65b23e745256b5043d; payload kernel994ad402ad8571ef67e732a3d02e3c02abe82608b6612d6b8c8cc8a29aa63f9a unchanged from cand12. Recovery changed packaging and ADT/backend contracts only.](https://github.com/Emilelu/UniXNU-mondrian/blob/5d8a09a58c86585f008ecb0c12611c2145c03f3f/docs/ops/PITFALLS.md)
  Command: <code>fastboot -s be74ba07 boot E:/k60-ios/boot-cand15-20261112.img; boot_capture2.py --seconds 240 --idle 0</code>. Revision: `5abea9af361ac2331c18f275567915125dc0d5f6`.

## CPU and interrupts {#cpu}

`implemented`

### Hardware and dependencies

- Identify the cpu and interrupts hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for cpu and interrupts.

### Procedure

- Follow the cpu and interrupts stage in the porting guide and record the actual commands.

### Development findings

- The SM8475 hardware MPIDRs are flat: 0x000..0x700, Aff1 = core index. That is what the vendor device tree and the Android tree carry, and this firmware rejects every CPU\_ON target outside that table. The 4/3/1 A510/A710/X2 grouping seen in Android's sysfs is L2/L3 cache topology, not MPIDR affinity, and the kernel's cluster-type property \(all 'P'\) is what collapses the eight cores into one topology cluster.
- A starting core is matched to its cpu data by MPIDR &amp; 0xFFFF against the ADT's per-CPU reg, and the same value is the PSCI target, so the ADT must carry the real MPIDRs. The board dts must not override the SoC dtsi's cpu nodes: the ADT generator needs their compatible string and their unixnu,cluster-type.

### Completion criteria

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU.

### Current limits

- The eight cores register and the boot CPU takes its first IPI, but no secondary has yet been seen past its own entry checkpoint on hardware.

### Next action

- Confirm that each secondary CPU runs its own entry checkpoint and serves a timer on the unit.

### Evidence

- `device`: [Android's device tree carries the eight hardware MPIDRs flat, 0x000..0x700, and boots all eight through PSCI; Android's sysfs reports a 4/3/1 A510/A710/X2 split by cache grouping, not by MPIDR. Our board dts had overridden the cpu nodes with packed 0x0-0x3/0x100-0x102/0x200 values, which broke both the firmware target table and the reset vector's match; the override is removed and the SoC dtsi's nodes are inherited again.](https://github.com/Emilelu/UniXNU-mondrian/blob/5d8a09a58c86585f008ecb0c12611c2145c03f3f/dts/mondrian.dts)
  Command: <code>adb shell 'cat /sys/devices/system/cpu/cpu*/topology/physical_package_id; cat /proc/device-tree/cpus/cpu@*/reg'</code>. Revision: `e636e445b621bed4fac0069f3604b87061350a8d`.
- `device`: [The Darwin 22 start order in ArmCpu::start\(\) called initCPU\(\) itself, whose trailing signalCPU\(this\) sent the boot CPU a self IPI before cpu\_machine\_init\(\) had set StartedState, so the first IPI tripped the assertion at cpu\_common.c:586 with cpu\_flags 0x2000 against the expected 0x3000. Switching to the Darwin 24 first-boot path \(pong\_cpu\_first\_boot, pong\_cpu\_first\_boot\_wait, ml\_cpu\_init\_completed\) makes the kernel call initCPU\(\) during processor\_boot\(\). The unit now paints all three probe bars, never reaches the assertion, and walks back to Android on its own through the probe's timed PSCI reset.](https://github.com/Emilelu/UniXNU-mondrian/blob/5d8a09a58c86585f008ecb0c12611c2145c03f3f/drivers/ArmCpu/ArmCpu.cpp)
  Command: <code>scripts/k60-device.sh boot /mnt/d/Android/k60-ios/boot-darwin24-bc8.img</code>. Revision: `d2af811a6dc9c6225de586e1615ca3824e2edce4`.
- `device`: [With the flat targets every CPU\_ON was granted and AFFINITY\_INFO answered 'on', yet no core joined: the arrival flag showed MPIDR 0x81000200 in the reset vector, and the core then hung on start.s's Lskip\_cpu\_reset\_handler because the cpu data it matched \(by its real MPIDR\) had no reset handler yet. The flat targets are the firmware's table; the pairing was the defect.](https://github.com/Emilelu/UniXNU-mondrian/blob/5d8a09a58c86585f008ecb0c12611c2145c03f3f/patches/xnu-ipados18/0247-k60-psci-flat-targets.patch)
  Command: <code>scripts/k60-device.sh boot /mnt/d/Android/k60-ios/boot-darwin24-bc11.img</code>. Revision: `e636e445b621bed4fac0069f3604b87061350a8d`.

## Memory and DMA {#memory}

`implemented`

### Hardware and dependencies

- Identify the memory and dma hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for memory and dma.

### Procedure

- Follow the memory and dma stage in the porting guide and record the actual commands.

### Development findings

- Live serial-6033dbec /memory/reg and rooted /proc/iomem give six RAM banks with a 28 GiB hole at 4..32 GiB. The installed 12 GiB cannot be one XNU window: the longest contiguous unreserved run is 8.65 GiB \(0x840000000..0xa69b78000\).
- The 4 GiB window booted XNU at mem=actual=managed=4096 MiB. An 8 GiB window \(arena equal to the whole 8 GiB\) was refused: DXE occupies part of the arena, so DarwinBoot returned to the UniXNU menu.
- A 8.625 GiB arena \[0x840000000,0xa68000000\) with a 7 GiB window is accepted: loader printed window 0x1c0000000 bytes at pa 0x8400200000 and HANDOFF EXIT RETURN 0. DarwinWindowSizeValid caps a window at 8 GiB, so 12 GiB is not reachable at all.
- Screen trace of the 4 GiB boot: suggestd exits with status 163 signal 0 and ns=0 code=0x0, i.e. a normal exit status, not jetsam or a sandbox denial; disk5s APFS transactions keep completing \(xid 2512, 140/140 finished\), so the Data volume is not stuck.

### Completion criteria

- All handoff regions are accounted for and each enabled DMA engine accesses its allocated range with the documented cache policy.

### Current limits

- The 4 GiB window is the proven configuration; 7 GiB was accepted by the loader but XNU did not start, and 12 GiB is physically impossible as one window. The display/CA prerequisites from the reference project are present in our kernel; the open wall is userland contract/container handling, evidenced by ns=2 SIGABRT/SIGTRAP.

### Next action

- Read the STR heap lines from the crash-string image to name the failing framework contract \(container path, MobileGestalt, activation\), then fix that one contract; display/CoreAnimation prerequisites are already audited as present.

### Evidence

- `host`: [8.625 GiB arena and 7 GiB window; strict v4 round trip PASS; image sha256 8ea52daf4b3e926d4840e13a73fa00c9cadf9b3f1e97e1ececfdaa446e1afc34.](https://github.com/Emilelu/UniXNU-mondrian/blob/5d8a09a58c86585f008ecb0c12611c2145c03f3f/docs/audits/MEASURED-HIGH-WINDOW-2026-11-02.md)
  Command: <code>python3 repair-high-window.py; build-uefi-8g.sh; build-kernel-summary.sh; package-textonly.py</code>. Revision: `48abe35d0a0a57f5fea9f9ba1e570800021ae6b1`.
- `device`: [Loader accepted window 0x1c0000000 bytes at pa 0x8400200000 and HANDOFF EXIT RETURN 0; console output from XNU not yet observed.](https://github.com/Emilelu/UniXNU-mondrian/blob/5d8a09a58c86585f008ecb0c12611c2145c03f3f/docs/audits/MEASURED-HIGH-WINDOW-2026-11-02.md)
  Command: <code>fastboot boot /mnt/e/k60-work/candidates/7g/boot-ios16-7g-textonly.img</code>. Revision: `e06211de59325bbd086c312324bdbf40e21d1045`.

## Storage and root {#storage}

`implemented`

Components: `PongUfs`.

### Hardware and dependencies

- Identify the storage and root hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for storage and root.

### Procedure

- Follow the storage and root stage in the porting guide and record the actual commands.

### Development findings

- K60DATA kernel window is /dev/disk5s1 at bytes=0x4f8200000 and mounts /private/var read-write: device log \`K60DATA RW mount enter path=/private/var\` \(patches/xnu/offline-owner-systemos-mount.patch:490\), followed by \`K60DATA mounted ro=0 fstype=apfs\` and \`mount returned error=0 result=0 rw=1\` \(docs/reference/DECISIONS.md:260\); docs/reference/PITFALLS-FROM-HISTORY.md:1031 records the binding \`K60DATA UFS window dev=900000a path=/dev/disk5s1 bytes=4f8200000\`.
- board.toml:31-35 defines the unixnu userdata geometry first\_lba=53342976, last\_lba=61731583, lba\_bytes=4096 with the OS and SystemOS windows; scripts/install-k60-ufs-data.py installs the GPT-wrapped APFS Data window into the unixnu SHNGROOT \(constants at :21-28\).
- 2026-10-31 user console reports APFS Data ENOSPC: free\_blocks around 1208 below threshold\_blocks 1310, affecting launchd/usermanagerd/logd\_helper. Latest saved installation is a 256 MiB APFS container in a 258 MiB Data GPT window at unixnu offset 7420 MiB, leaving about 24.502 GiB outside windows. Historical images are checksum/CRC verified but do not establish current live occupancy; capture in root recovery is pending. Read-only inspector validates saved 256/512 MiB images and can back up current Data with second-read hash comparison and optional local directory-allocation summary. No device storage writes or resize performed.

### Completion criteria

- Host: register, clock, link and SMMU facts match the board inventory.
- Reads: SCSI capacity, GPT and known blocks are correct; OS/SystemOS windows stay within userdata.
- Root: the configured volume mounts and launchd starts. Persistence: writes survive reboot within the allocated Data region.

### Current limits

- Hardware inputs and implementation are pending for this board.

### Next action

- Inventory the required storage and root inputs before implementation.

### Evidence

- `device`: [The unixnu three-window partition is what every successful bring-up boot runs from: usblog-20261114-150931 reached SpringBoard 254 with the Data window mounted out of /dev/block/sda38 and no storage error, and the same image family held SpringBoard 128-133 through the 2026-11-16 and 11-17 flights. The earlier silent deaths were explained as P-215: the wifi patch took the Apps SMMU lease before pong\_rpmh\_init\(\) had allocated the lock, so UFS gave up before the console worker existed.](https://github.com/Emilelu/UniXNU-mondrian/blob/5d8a09a58c86585f008ecb0c12611c2145c03f3f/docs/research/storage/RESEARCH.md)
  Command: <code>bash scripts/flash.sh /mnt/e/k60-work/artifacts/touch-20261114a/boot.img 240</code>. Revision: `43c4fc3cf288f0c6545cb2447fc4d285cfb6d3c7`.
- `host`: [feat/ufs-verified-table carries the ShengUfs@9d527ae VerifiedTableCache, RootPublication and RootWindowRead headers with their host tests, all passing. The kernel-side signed-root header is still missing, so the cache cannot be wired yet: implemented work with evidence recorded, verified-root handshake still open.](https://github.com/Emilelu/UniXNU-mondrian/blob/5d8a09a58c86585f008ecb0c12611c2145c03f3f/docs/research/storage/RESEARCH.md)
  Command: <code>python3 scripts/tests/test-k60-verified-root.py</code>. Revision: `43c4fc3cf288f0c6545cb2447fc4d285cfb6d3c7`.

## Display {#display}

`implemented`

### Hardware and dependencies

- Identify the display hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for display.

### Procedure

- Follow the display stage in the porting guide and record the actual commands.

### Development findings

- Software framebuffer implementation is live at 60 Hz: patches/xnu/0210-k60-display-native-canvas.patch:10-31 fixes the K60 panel contract at 1440x3200 with refreshHz\(\) defaulting to 60; patches/xnu/0211-k60-display-startup.patch starts the display services, 0213-k60-display-first-frame.patch publishes TimingElements and the first frame, and 0236-k60-managed-memory-and-panel.patch carries the panel/VM handoff. All four are enabled in patches/xnu/series:86,87,89,115.
- Device log reaches the SpringBoard main loop: \`\[SpringBoard\] \_checkIn returned\` -&gt; \`UIApplication \_run entered\` -&gt; \`main queue reached locked=0 screen=0 dim=1\` \(docs/state/TRUST-LEDGER.md:41; docs/state/STATE-2026-11-07.md:17-19\).
- Board-level chosen display-scale=3 adapted from XTOM0706 9d1a14f83d1050a042313f30dc9d5b7e80d31f7a. Parsing generated ADTs before/after gives identical properties except random-seed with the current 20G81 profile. Its additional sweet display node is not copied because MiniIOMobileFramebuffer already publishes a disp0 display-subsystem child at runtime.

### Completion criteria

- A known frame appears with correct geometry and colors, then userland presentation and backlight controls work.

### Current limits

- cand18 captured78716B of actual native UI logs: locked=1, screen=1, homeButtonType=2 and live main-loop turns3868 at120s. Wallpaper bootstrap skipped because existing-content=1; no native wallpaper submission or restored pixels is proven. Physical touch transport remains unqualified.

### Next action

- Verified recovery image E:/k60-ios/boot-cand19-20261112.img SHA256e53b7a6b3487334144f18151b3f11ca0fbecf6f20c9306e2dfd6a5c7b1d502d4 retains the fixed4096-byte header page, FAT offset552960, UFS-only Data and native HomeButtonType2. Its actual FAT kernel and113424-byte signed UI library match the build inputs; args596bytes carry k60\_wallpaper\_reset=1 exactly once. Native submission and pixels remain unverified because fastboot/ADB/CDC are unavailable. Reconnect in fastboot, boot this image temporarily, and inspect content classes/assets/submission before qualifying the picture; ordinary boots preserve existing wallpaper.

### Evidence

- `device`: [console-20261111-204210.log \(74090 bytes\): main queue reached, delayed home request accepted, first frame and subsequent BGRA swaps presented, main snapshot turns=3889. User observes desktop, status bar, App Store, Settings and Dock. Software rendering only; touch and GPU not implied.](https://github.com/Emilelu/UniXNU-mondrian/blob/5d8a09a58c86585f008ecb0c12611c2145c03f3f/patches/xnu/0394-k60-launchd-cache.patch)
  Command: <code>fastboot -s be74ba07 boot E:/k60-ios/boot-cand7-20261111.img</code>. Revision: `5198a67999208658bd06d227ef14cfa7efeffb3e`.

## Input {#input}

`device-verified`

### Hardware and dependencies

- Identify the input hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for input.

### Procedure

- Follow the input stage in the porting guide and record the actual commands.

### Development findings

- cand7 skips touch because the actual FAT ADT has no /arm-io/pong-touch. The format-2 converter accepts typed metadata children; board.toml defines K60 SE4 0x990000, TLMM 0xf000000+0x100000, GPIO16-21 and AVDD71, raw axes14400x32000. No RSC/cmd-db access is permitted in the touch driver.
- Read-only rooted Android be74ba07 confirms Goodix BERLIN/9916R firmware05800263, LDOC2 enabled at1800000uV, 193-byte IC-info with checksum5185 and touch address0x10308. IC-info dimensions1440x3200 must not replace the raw evdev14400x32000 axis contract. The actual Android transfer log uses GPI callbacks with FIFO disabled.
- The compiled GPIO fallback carries the 2us half period, boot-option write/readback and 1488-byte captured config package, but cand15 never entered that transport because bitbang-pins metadata was absent. No XNU handshake, config ACK or touch sample is established. Earlier whole-image diagnostic string checks proved only code inclusion, not controller response.
- The real blocker was not power or the pin map but a missing second command: the driver sent 0x90/0x00 \(raw frames off\) and never 0x91/0x01 \(coordinate reports on\), which the on-device Android goodix\_htc\_enable\(false\) sends as a pair. It also checked only ack\[1\] instead of waiting for reply\[0\] == 0x80, so a config that had not completed looked finished. Both are fixed in the touch patch; the retained module's brl\_hw\_ops disassembly \(dev\_confirm at 0x11d44, read\_version at 0x136e8, brl\_send\_config's 20x20 ms state poll\) is what pinned the exact order.

### Completion criteria

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive, and buttons produce expected HID reports.

### Current limits

- 2026-11-14 boot touch-20261114a \(boot.img 0b2003f4…, kernel c78a5cc9…\) qualifies single-finger touch: CFG-START/WRITE/EXIT complete at state=0x80, RAW-OFF and COORD-ON both ack=0x80, the chip reports BERLIN 9916R 05.80.02.63 with active config 0x640fdf7d, and eight \`goodix: type=1\` samples reach \`Pong touch HID: type=1\|3\` for the display-integrated digitizer. Console E:/k60-work/evidence/usblog-20261114-150931/console.log, 268,137 B, 254 SpringBoard lines, no panic marker. NOT yet accepted: two simultaneous contacts, edge gestures, tap-to-wake, and sustained frame rate under a moving finger; the 0x10308 header length is read from misc+48 but the retained module only proves misc+44 \(data address\) and misc+50 \(point struct length\).

### Next action

- Accept multi-touch next: hold two fingers and confirm two distinct contact IDs with independent coordinates and separate release events, then exercise the screen edges for the system gestures. If a second contact never appears, inspect the point-struct stride against misc+50 before touching the parser. Tap-to-wake \(touch detection mode 0xff/0xfe/0x1/0\) is logged but not verified against a sleeping panel.

### Evidence

- `device`: [Actual live FDT SHA2385d2a84ce920b5694b4cfcd8366d8bf6a7c39a0c0d2d02e988c1bc22ff94b1; BERLIN/9916R verified and raw axes14400x32000. This is Android hardware evidence, not XNU touch qualification.](https://github.com/Emilelu/UniXNU-mondrian/blob/5d8a09a58c86585f008ecb0c12611c2145c03f3f/board.toml)
  Command: <code>adb -s be74ba07 exec-out su -c 'cat /sys/firmware/fdt'; read Goodix chip_info and r:10014:28/r:10070 IC-info selectors</code>. Revision: `fb24cf99ad97ab14313284000000000000000000`.
- `host`: [boot-touch9-input-20261112.img \(201883648 B, e7e4e90ab556a3e5\) carries the handshake, 2 us bit-bang, config download and coordinate-mode strings; the packet carries no pong\_touch argument so the driver runs at its stage-6 default. Not sent: the board was off the USB bus.](https://github.com/Emilelu/UniXNU-mondrian/blob/5d8a09a58c86585f008ecb0c12611c2145c03f3f/patches/xnu/zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz-pong-touch-console.patch)
  Command: <code>python3 work/touch-gpu/repack-boot.py --template gpu8-start.img --ramdisk payload.img; inspect strings in the resulting image</code>. Revision: `04a819c4b9050bf4d37dff64c5357d4efea7e3b1`.
- `device`: [console.log 268137 B / 3870 lines, capture.json complete=true panicMarker=null, SpringBoard 254. line 683 \`goodix: COORD-ON ack=80\`; lines 2490-2601 eight \`goodix: type=1 finger=0 raw=... normalized=...\`; lines 2491-2496 four \`Pong touch HID: type=1\|3 finger=0 xy=...\`; line 1425 display-integrated digitizer opened. User present, screen responded to a real finger. Single contact only; multi-touch and gestures remain unaccepted.](https://github.com/Emilelu/UniXNU-mondrian/blob/5d8a09a58c86585f008ecb0c12611c2145c03f3f/docs/research/EIGHT-STEPS.toml)
  Command: <code>bash scripts/flash.sh /mnt/e/k60-work/artifacts/touch-20261114a/boot.img 240</code>. Revision: `0143b465721b47804cebc3d51cd76fa34fbfac37`.

## GPU {#gpu}

`planned`

### Hardware and dependencies

- Identify the gpu hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for gpu.

### Procedure

- Follow the gpu stage in the porting guide and record the actual commands.

### Development findings

- cand7 renders through CPU composition; CONFIG\_XNU\_PONG\_ADRENO\_PLATFORM=n disables the real archive. The enabled scanout callsites currently resolve to explicit software-only weak functions, not GPU execution.
- Read-only device evidence confirms Adreno730v3 chip0x07030002 and the actual GMU/SQE/ZAP firmware. The build provider now resolves its real kernel tree, uses the retained register header and captured K60 firmware directory. K60 RSC EL1 accesses historically hang; the actual backend now uses documented Qualcomm monitor secure-IO calls for TCS reads/writes, propagates authorization failures, and retains real fence prerequisites.

### Completion criteria

- GPU submissions complete, mapping/fence handling is correct, a known image renders, and the selected Metal client presents it.

### Current limits

- gpu8-start reaches the actual Adreno startup entry but every TCS access went through the Qualcomm secure-IO service, which the monitor denied \(return -2\), so parent votes failed before GMU/HFI, ZAP or CP. The change to a direct RSC mapping and retained highest AUX corner is compiled and packaged but has not run: the board left the USB bus after that trial and did not return. No GPU or Metal presentation is qualified; CPU desktop frames do not establish acceleration.

### Next action

- Boot the candidate with the board reconnected and read the PONG ADRENO steps. Upstream initialised this same hardware with a direct APSS RSC mapping, reporting result=0 for all 22 steps including the parent ARC votes, so the secure-IO route was the deviation; the direct mapping is now used and must be judged by those steps, not by reaching the desktop. GPU publication still requires real GMU/HFI/ZAP/CP fences.

### Evidence

- `device`: [console-20261112-013119.log 72314B: startup requested, secure RSC read refused at0x17a2000c return0xfffffffffffffffe, FAIL parent votes. No accelerator published. Authentic K60 GMU/SQE/ZAP firmware is embedded, but GMU/CP/fence execution did not begin.](https://github.com/Emilelu/UniXNU-mondrian/blob/5d8a09a58c86585f008ecb0c12611c2145c03f3f/scripts/build-pong-adreno-platform-linux.py)
  Command: <code>fastboot -s be74ba07 boot E:/k60-ios/boot-gpu8-start-20261112.img; boot_capture2.py --seconds 240 --idle 0</code>. Revision: `61544e3f6736506485b10a3f635a6d2e87a95a10`.
- `source`: [The upstream driver maps 0x17a20000/0x10000 directly and never calls secure I/O, and its record reports all 22 startup steps result=0 with parent ARC votes acknowledged and the accelerator published. That is the evidence the local secure-IO route was the deviation, so the direct mapping and retained-highest-corner selection are adopted. Upstream still reports rendering unverified and scanout off.](https://github.com/Emilelu/UniXNU-mondrian%20%28upstream/main%20in%20work/up-device%29)
  Command: <code>git show upstream/main:drivers/PongAdreno/PongAdrenoPlatform.cpp; git show upstream/main:porting.toml</code>. Revision: `609e51aec8ffc5b06d844d3444ad1349abf598be`.
- `host`: [Linux cross-build completed rc=0: Turnip 687/687 objects compiled and libvulkan\_freedreno.dylib linked, the metal2vulkan crates compiled to the bridge staticlib and linked into PongMetalBridge.dylib, and PongAdrenoMetal linked; all three are arm64 Mach-O dylibs with NOUNDEFS, and the publication marker is 0. Build evidence only: the kernel publishes no accelerator, so no device execution happened.](https://github.com/Emilelu/UniXNU-mondrian/blob/5d8a09a58c86585f008ecb0c12611c2145c03f3f/scripts/build-pong-userspace-linux.py)
  Command: <code>python3 scripts/build-pong-userspace-linux.py --core core --mesa work/refs/mesa --translator work/refs/metal2vulkan --sdk-root work/iPhoneOS16.5.sdk --venv venv --output-dir work/gpu-userspace</code>. Revision: `0eb295a0256d9548567eae347eb763ce6e46392d`.
- `device`: [2026-11-17 flight usblog-20261117-130912: K60GPUADDON addons stage=5 status=0, the addon mount reads the plugin bundle, and for the first time a real device comes up - Pong Metal: real Vulkan-backed device created status=0x0, 91 Pong Metal lines, Turnip Adreno \(TM\) 725 enumerated, crashed: backboardd 0. Nothing presents yet: present \# 0 and the SpringBoard main thread then blocks in a synchronous Mach call to backboardd \(main snapshot turns=0\). The accelerator is reachable, the frame path is not.](https://github.com/Emilelu/UniXNU-mondrian/blob/5d8a09a58c86585f008ecb0c12611c2145c03f3f/patches/xnu/0610-k60-metal-plugin-deploy.patch)
  Command: <code>bash scripts/flash.sh /mnt/e/k60-work/artifacts/gpu-addon4-20261117/boot.img 240</code>. Revision: `b76c724857b2711eb6e461d3b9f46f86d5fe4ffc`.

## Network {#network}

`planned`

### Hardware and dependencies

- Identify the network hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for network.

### Procedure

- Follow the network stage in the porting guide and record the actual commands.

### Development findings

- Official Ath12kWifi shared station component is available \(https://github.com/UniXNU/Ath12kWifi.git at f6bf561f92cc42761bdd417fce1d53fe1db9477c\), docs/plans/WIFI-PORT-PLAN.md:32.
- K60 PCIe/BAR0/GPIO/SID match the Pong reference: PCIe0 six reg windows, BAR0 0x60200000/2 MiB, GPIO 80/81/82/94/95/96/204, SID 0x1c01, IOVA 0xA0000000/256 MiB and MSI SPI140 \(docs/plans/WIFI-PORT-PLAN.md:15\).

### Completion criteria

- Scanning, association, address configuration and sustained receive/transmit traffic pass with the selected firmware.

### Current limits

- Hardware inputs and implementation are pending for this board.

### Next action

- Inventory the required network inputs before implementation.

### Evidence

- `source`: [Ten patches; wifi-20261116c5 proved the read-only RSC probe returns caps=0x800c8104 from TCS4 on DRV-2 with panic 0 and SpringBoard 132, and c6 reached QCA6490 PCI enumeration, MHI READY and then timed out \(-110\) inside mhi\_sync\_power\_up. Not working: MHI never entered mission mode, so no MSI was delivered and no interface exists. c8 is held until the failure snapshot is bounded.](https://github.com/Emilelu/UniXNU-mondrian/blob/5d8a09a58c86585f008ecb0c12611c2145c03f3f/patches/wifi/series)

## Audio {#audio}

`planned`

### Hardware and dependencies

- Identify the audio hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for audio.

### Procedure

- Follow the audio stage in the porting guide and record the actual commands.

### Development findings

- K60 has 2x AW882xx smartpa at I2C 0x34/0x35 \(\`awinic,aw882xx\_smartpa@34\` and \`@35\`\), not TFA9873: docs/plans/BT-AUDIO-PORT-PLAN.md:38,192-194,207-210.

### Completion criteria

- Each declared route carries the selected audio format through playback or capture and handles start/stop correctly.

### Current limits

- Hardware inputs and implementation are pending for this board.

### Next action

- Inventory the required audio inputs before implementation.

### Evidence

- `source`: [ADSP PAS1 groundwork: the 24 PT\_LOAD segments spanning 0x86300000..0x89400000 were verified offline, kernel-side PAS/boot/FAT walkers and the platform ownership callbacks are in the tree, and the host suite for the rail sampler is recorded under package/tests/rail-sampler/proposed. Not working: resources\_cb still refuses with K60BoardUnsupported\(-63\) because the LCX/LMX rail vote cannot happen before the Data mount \(HR-01\), so no PAS1 image is authenticated and no codec is powered.](https://github.com/Emilelu/UniXNU-mondrian/blob/5d8a09a58c86585f008ecb0c12611c2145c03f3f/docs/research/audio)

## Power {#power}

`planned`

### Hardware and dependencies

- Identify the power hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for power.

### Procedure

- Follow the power stage in the porting guide and record the actual commands.

### Development findings

- PMIC/PON historical observations are recorded in docs/archive/HANDOFF-2026-10-31.md:55 and docs/archive/HANDOFF-k60-work-2026-11-06.md:210; they do not prove battery GLINK ownership.
- 2026-11-15: five injected PAS1-owner stages and a persistent wrapper pass 77 named host scenarios around real MDT/SMEM/build/parser code. Exact required=15, independent public facts/internal stage mask, poisoned uncertain shutdown and retained published ownership are enforced; see docs/research/battery/PAS1-PROVIDER-CONTRACT.md.
- 2026-11-15: bounded blob/FAT named reader and immutable owner adapter are implemented. Captured-firmware host checks cover 24 segments, exact payload/BSS counts, unaligned b10, BSS-only missing b24, error codes and lifetime; this was the earlier reader-only source checkpoint. See docs/research/battery/PAS1-PROVIDER-CARRIER.md.
- 2026-11-15: Lead froze production K60A as a 12-byte LE header and sequential 24-byte records, NUL names \(name\_len=9\), mode0644, packed\_size=size and 8-byte zero padding. The production generator/checker and reader exist. The 26 inputs total23505092 bytes and the single cursor gives23506184 bytes; no flat format, compression or second dispatch is accepted. Copy23494284+BSS25925684=49419968 bytes; mapped span51380224 includes1960256 bytes of intersegment gaps. See docs/research/battery/CARRIER-BLOB-PLAN.md.
- 2026-11-16: complete version-1 platform ops, persistent linked-reader context and idempotent install are wired before runtime acquire. Native mapping/TCSR/serialized SCM/coherent metadata code is implemented; board aggregate ownership/resources/stopped/shared-SCM-lock service has no production supplier, so available=0 before physical access. Platform host cases pass31 absent and34 actual-linked; see docs/research/battery/PAS1-PROVIDER-INSTALL.md.

### Completion criteria

- Declared power controls and battery readings match observations; each claimed sleep/resume transition restores its dependent peripherals.

### Current limits

- Power remains planned and battery verify/local\_verified/device remain false. The platform adapter is installed before first acquire after RAM/chosen/OSData preflight; missing board ownership service still fails closed before SMC/SMEM/TCSR. Native mapping, coherent metadata and serialized/resumed SCM have arm64 SDK syntax coverage only, not native execution. Complete host suite exits0 with platform31/34, owner77, reader5x31 and unchanged integration assertions. Lead-owned run e proved the earlier uninstalled attempt, not PAS failure. No kernel/image build or device action occurred in this task. Nine scoped checks pass; candidate and unchanged-HEAD porting checks retain the same54 exact inherited errors, introduced0/resolved0, not waived. Full results are in PAS1-PROVIDER-INSTALL.md.

### Next action

- Lead supplies or commissions audited board aggregate PAS1/GLINK/reset ownership, retained power/XO/ICC/QMP votes, independent stopped/live proofs and the shared SCM transaction lock via k60\_adsp\_platform\_ownership\_install before first acquire. Preserve missing-service refusal and Poisoned/Published retention. Lead owns archive/kernel/image integration and any device validation; do not infer battery/audio/charger readiness from install or publication logs. Resolve inherited porting debt independently.

### Evidence

- `source`: [Five-stage API, 77 host test paths, failure/lock/lifetime boundaries and uninstalled production backend are documented; hardware verification remains false.](https://github.com/Emilelu/UniXNU-mondrian/blob/5d8a09a58c86585f008ecb0c12611c2145c03f3f/docs/research/battery/PAS1-PROVIDER-CONTRACT.md)
- `source`: [Root verified final host suite exit0: owner77 \(17/11/12/15/22\), five reader variants with31 scenarios each, all five blob assertions with negative mutations, publisher49/builder10/MDT16/notify21/battery27/dispatch14/5sections/3mirrors. All26 inputs exactcopy/borrow and generated binary equals independent builder. Host log E:/k60-work/artifacts/adsp-carrier-20261115/final/host-tests.log, SHA256 51bf1696ec950e112b29f92972e7e9f596c2a91180080e1c9ba79417921e22c1. Reader/stages/Boot arm64 SDK syntax SHA256 6d3b5f1cc1bfbfdca7ba3cb9172317bed19469f26b12defbfeba2afb4817055e; runtime C++ syntax also passes. Ten scoped checks pass \(docs193/table/owner/secrets/battery/patch parse/diff/staged-diff/build-call fragment/checker negatives\). Candidate and unchanged-HEAD porting checks both have the same54 inherited errors, introduced0; not waived. Lead confirms generator/checker output23506184 bytes,26 records,raw23505092 bytes,SHA256 663369461a9def3105884b34a574c119aaa2b95111c185a6f12de34158bcd319. This is not carrier installation, kernel-link or hardware verification.](https://github.com/Emilelu/UniXNU-mondrian/blob/5d8a09a58c86585f008ecb0c12611c2145c03f3f/docs/research/battery/CARRIER-BLOB-PLAN.md)
- `source`: [Complete callback/source/log evidence matrix and runtime:47 install. Host exit0 SHA256891636f504b0d5cf3f2d42f43369e90cc4c55d209fc60b38aa534e8ff897dbe7; arm64 platform/native/runtime/reader/stages SDK syntax SHA2564b4193b1fb0ed2c72647afad7733970ccab8f530b91dbd29709a83dff0ec12f8. Host services are fake; native ownership service absent. Supported-pre0619 isolated fixture fixed already-applied-input autoreversal without changing canonical checks or global tree.](https://github.com/Emilelu/UniXNU-mondrian/blob/5d8a09a58c86585f008ecb0c12611c2145c03f3f/docs/research/battery/PAS1-PROVIDER-INSTALL.md)

## Image assembly {#packaging}

`host-verified`

### Hardware and dependencies

- Identify the image assembly hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for image assembly.

### Procedure

- Follow the image assembly stage in the porting guide and record the actual commands.

### Development findings

- The three local trees use different userland models: ours keeps an OS+SystemOS read-only APFS union from the unixnu partition; ios-sweet-k60 rewrites a writable HFSX image at build time; UniXNU-pong prepares at run time inside its own static init that becomes PID 1 and then execs launchd. Selected approach: diagnose first and do not replace PID 1, because the launchd chain is already verified and the pong adapter targets Darwin 24 ABI. Our kernel already carries exec\_inject and bindfs, so the pong model remains available if the blocker turns out to need run-time preparation. See docs/USERLAND-ROUTES-2026-11-02.md.
- The kernel links and prelinks on macOS CI. Format 1 run 40631225483 produced 54349824 bytes; format 2 run 40650877574 produced 54419456 bytes at the same slide -0xb9c000 and the same lowest component extent 0xfffffff004426600.
- The 69632-byte difference is a real fix, not noise: the format-1 glob applied zzzzzz-pong-init-scratch-allocation.patch through fuzz and the panic string it adds is absent from that kernel, while the strict format-2 series applies it at its intended place and the string is present. The checked scratch allocation had never reached a qualified kernel before.
- mzyxsl daed6b5 fixes the local prelink helper to merge the OS-profile prelink table and board overrides. A real prelink of the 0238 native kernel succeeded with 32 roots and automatic slide -0xb9c000, 53788672 bytes, SHA-256 bb33682837f1807ef28d385cf09acf94f2749f49b3f7337d22348dcbf6c4b9df. Use --profile/--kit for non-sibling checkouts.

### Completion criteria

- Kernel and prelink succeed, payload contains all declared inputs, and the boot image matches the bootloader format and size limit.

### Current limits

- cand7 reaches the desktop after restoring notifyd/lsd PublishesEvents. Touch skips for incompatible Pong DT and Adreno is disabled in the kernel configuration; neither subsystem is device-verified.

### Next action

- Preserve cand7 as the known-working desktop baseline; verify K60 touch and Adreno changes independently using RAM-only fastboot boot candidates.

### Evidence

- `host`: [Build kernel succeeded on macOS from this revision: prelink slide -0xb9c000, 54419456 bytes, lowest component extent 0xfffffff004426600](https://github.com/Emilelu/UniXNU/actions/runs/40650877574)
  Command: <code>./unixnu build kernel -D ../UniXNU-mondrian</code>. Revision: `6a10bf5e42ecfad7eed2789cc091287d31009623`.
- `host`: [Route a-18 chain reproduces end to end: kernel 20,872,544 B \(15966fcd\) -&gt; prelink 54,808,576 B -&gt; payload 201,326,592 B -&gt; boot-darwin24-bc6.img. The verifier confirms the kernel slot is the 112-byte shim plus the rebuilt FD, the ramdisk slot is byte-identical to payload.img, and the in-volume kernel.macho matches the built kernel.](https://github.com/Emilelu/UniXNU-mondrian/blob/5d8a09a58c86585f008ecb0c12611c2145c03f3f/scripts/verify-boot-img-payload.py)
  Command: <code>python3 scripts/k60-prelink-darwin24.py &amp;&amp; python3 scripts/verify-boot-img-payload.py --img /mnt/d/Android/k60-ios/boot-darwin24-bc6.img --payload /tmp/k60build/out/mondrian/ipados-18.7.10-22H374/mondrian/payload/payload.img --kernel /tmp/k60build/out/mondrian/ipados-18.7.10-22H374/mondrian/kernel/kernel.macho</code>. Revision: `e636e445b621bed4fac0069f3604b87061350a8d`.
- `host`: [Real iOS SDK build succeeds; 0340 array is regenerated with the current deferred-preferences source. Library 95856 bytes, SHA-256 b3289bcb5768a5c6f9d4b3ee0e35abaafb3b8a00f00f5167049109ee71c5aa2b; all 24 4096-byte signature-page hashes verify. Rebuilt/prepared kernel SHA-256 67d0f5bbdfb7422be72b89e1d0bf76057d9f1ac94944772df3f75d078f83f4c7 contains the new blob exactly once and no old blob. cand6 FAT preserves firmware, ADT and arguments; image SHA-256 a7070e6af739565d4829c3de62f7a1687626bd88c9eb2d7f8eb0812593c37871. cand6 device run is recorded separately; no UI readiness is implied.](https://github.com/Emilelu/UniXNU-mondrian/blob/5d8a09a58c86585f008ecb0c12611c2145c03f3f/userland/build.py)
  Command: <code>python3 userland/build.py ui --sdk /root/k60/work/iPhoneOS16.5.sdk --out /root/k60/work/ui-v3</code>. Revision: `c6e555c1895e6096c32ab396485ee7d61221a86c`.
- `device`: [console-20261111-194438.log \(64717 bytes\): K60UILIB deploy bytes=95856 resid=0 error=0 and all ten SpringBoard hooks install. Main snapshots at 60/120 seconds have turns=0 and identical Firehose/logd registration frames, symbolicated using the matching cache-symbol UUID. notifyd SIGTRAP maps to BUG IN LIBNOTIFY: Event publisher error; the selected cache drops PublishesEvents present in the original descriptor. UI not established.](https://github.com/Emilelu/UniXNU-mondrian/blob/5d8a09a58c86585f008ecb0c12611c2145c03f3f/userland/build.py)
  Command: <code>fastboot -s be74ba07 boot E:/k60-ios/boot-cand6-20261111.img</code>. Revision: `c6e555c1895e6096c32ab396485ee7d61221a86c`.

## Diagnostics {#diagnostics}

`device-verified`

### Hardware and dependencies

- Identify the diagnostics hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for diagnostics.

### Procedure

- Follow the diagnostics stage in the porting guide and record the actual commands.

### Development findings

- Collect the first diagnostics observation, its cause when established, and the resulting implementation decision.
- Imported the source-only offline path/evidence checker from mzyxsl 76552b88441757defce4080a241c2f0ea7464538, preserving current milestone statuses instead of copying its outdated runtime records. scripts/audit-forks.py enumerates public forks and all branches, pins comparison SHAs, and reports candidates without executing or merging fork code. KX SIGKILL records alone do not prove a sender or pressure; 0238 adds committed reason scalars and bounded fallback logging. See docs/FORK-REVIEW.md and docs/BOOT-STALL-2026-10-31.md.

### Completion criteria

- Each claimed milestone has a reproducible command, a matching source/image revision and an accessible result.

### Current limits

- The current USB gadget is XNU CDC-ACM VID1209/PID0001, not Apple usbmux. Only documented help/reboot commands are exposed; no remote debugserver or LLDB single-stepping connection has been established.

### Next action

- cand18 verifies the selected kern.pong\_diagnostic endpoint: actual K60UI SpringBoard/backboardd messages reached COM8, including locked state, HomeButtonType2, wallpaper preservation and Mach main-thread snapshots. Continue through this bounded text endpoint; a full remote debugger still needs a target debugserver and transport.

### Evidence

- `device`: [Breadcrumbs turned a silent reset into a located fault: column 1 showed six squares, column 2 zero, column 3 one, which put the death inside ml\_parse\_cpu\_topology\(\). The first carrier \(u64 slots at 0xA73FF000\) was useless because a hung board never returns DRAM, so the markers moved into the framebuffer; 0245 then produced a readable panic on hardware.](https://github.com/Emilelu/UniXNU-mondrian/blob/5d8a09a58c86585f008ecb0c12611c2145c03f3f/patches/xnu-ipados18/0244-k60-breadcrumbs.patch)
  Command: <code>scripts/k60-device.sh boot /mnt/d/Android/k60-ios/boot-darwin24-bc4.img; count the breadcrumb squares</code>. Revision: `e636e445b621bed4fac0069f3604b87061350a8d`.
- `device`: [The upstream entry probe installs on this kernel: stage 1 blue bar, stage 2 magenta bar, stage 3 resets the board through PSCI six seconds after the MMU comes on. The board walked back to fastboot and then to Android by itself, so a hung kernel no longer needs a manual power cycle. The probe's panic screen stays off because it installs code in the padding after panic\(\), at an address fixed for the reference kernel.](https://github.com/Emilelu/UniXNU-mondrian/blob/5d8a09a58c86585f008ecb0c12611c2145c03f3f/docs/reference/ROUTE-A-18-UPSTREAM.md)
  Command: <code>scripts/k60-device.sh boot /mnt/d/Android/k60-ios/boot-darwin24-bc7.img</code>. Revision: `350d1c57c86d2fc562c7fa7529271fdae3af95bc`.

## cellular {#cellular}

`planned`

### Hardware and dependencies

- K60 carries a Snapdragon X65-class modem inside the SM8475 package; it is not an external modem on this board.
- Modem firmware, EFS/NV data and the SIM identity live on the Android side of the dual-system unit.
- No QRTR/QMI endpoint, IPA path or SIM slot has been exercised under XNU.

### Configuration

- board.toml declares the SM8475 SoC but no cellular component.
- dts/mondrian.dts does not describe the modem memory regions, QRTR transport or IPA queues.

### Procedure

- Inventory the modem firmware partition and the QRTR/QMI services from an Android boot.
- Record the IPA/QMAP configuration and the SIM identity source.
- Only then decide whether the baseband path is in scope for this port.

### Development findings

- The port currently has no baseband support at all; Android modem stack is untouched.
- Recording it as planned rather than not-applicable keeps the gap visible.

### Completion criteria

- A device boot shows the modem enumerated over QRTR with a readable firmware revision.

### Current limits

- Nothing has been measured on this board beyond the Android-side inventory.

### Next action

- Read the Android modem partitions before writing any cellular code.

### Evidence

- `source`: [The carrier side is implemented outside this tree: uefi-mondrian ImageCarrierLib decompresses 27 LZMA streams into 0x8bc00000 with a 0x13200000 window and publishes a 16-byte all-zero K60ModemImage placeholder, and UniXNU feat/modem-carrier 92bb60f stages the same 27 streams under EFI/UniXNU/MODEM with a build-time name guard. Offline acceptance is 11/11 on real inputs plus 14 framework cases. Not attempted: no modem boot, so the status stays planned.](https://github.com/Emilelu/UniXNU-mondrian/blob/5d8a09a58c86585f008ecb0c12611c2145c03f3f/porting.toml)

</div>
