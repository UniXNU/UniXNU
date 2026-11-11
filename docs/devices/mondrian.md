# Redmi K60 \(mondrian/SM8475\): UniXNU UEFI bring-up

[Emilelu/UniXNU-mondrian](https://github.com/Emilelu/UniXNU-mondrian)

<div v-pre>

Redmi K60 \(mondrian/SM8475\). Format 2 device: UEFI, UniXNU loader, XNU and launchd boot to userland; configuration, memory, input and GPU are implemented; firmware, CPU, storage, display, power and diagnostics are device-verified; network, audio and cellular are planned.

Source record: [porting.toml](https://github.com/Emilelu/UniXNU-mondrian/blob/f92dbda6ca0356a6823b92fe0d85d466fb4a1db5/porting.toml), `f92dbda6ca0356a6823b92fe0d85d466fb4a1db5`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `implemented` |
| [Firmware and boot](#firmware) | `device-verified` |
| [CPU and interrupts](#cpu) | `device-verified` |
| [Memory and DMA](#memory) | `implemented` |
| [Storage and root](#storage) | `device-verified` |
| [Display](#display) | `device-verified` |
| [Input](#input) | `implemented` |
| [GPU](#gpu) | `implemented` |
| [Network](#network) | `planned` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `device-verified` |
| [Image assembly](#packaging) | `host-verified` |
| [cellular](#cellular) | `planned` |
| [Diagnostics](#diagnostics) | `device-verified` |

## Configuration {#configuration}

`implemented`

Components: `ArmDTPlatform`, `ArmCpu`, `XnuPrelink`.

### Hardware and dependencies

- SM8475 SoC source pinned in feeds.toml; the ipados-16.6.1-20G81 OS profile supplies the kernel and prelink inputs.
- board.toml selects ArmDTPlatform, ArmCpu, XnuPrelink and PongUfs; dts/mondrian.dts supplies the board wiring.
- patches/xnu/series is the ordered kernel patch series: 211 entries at this revision.

### Configuration

- board.toml schema\_version = 2; \[board\] name = "mondrian", soc = "SM8475", soc\_source = "sm8475", os\_profile = "ipados-16.6.1-20G81", kit = "mondrian".
- \[components\] include = \["ArmDTPlatform", "ArmCpu", "XnuPrelink", "PongUfs"\].
- \[kernel\] defconfig = "mondrian\_defconfig"; config\_fragments = \["arch:configs/common.config", "soc:configs/sm8475.config", "os:configs/ipados.config"\]; patch\_series = \["device:patches/xnu/series"\].
- \[userdata\] first\_lba = 53342976, last\_lba = 61731583, lba\_bytes = 4096, windows = \[OS, SystemOS\]; \[device\_tree\] source = "device:dts/mondrian.dts", include\_dirs = \["soc:dts"\].

### Procedure

- Read board.toml against the SM8475 common tree and the 20G81 OS profile before changing any component selection.
- Keep dts/mondrian.dts limited to board wiring; the SoC dtsi owns the CPU and peripheral nodes.
- Build the kernel with \`./unixnu build kernel -D ../UniXNU-mondrian\` and check the applied patch count in the build log.

### Development findings

- Migrated from format 1 on 2026-10-28: board.toml is schema\_version = 2 with soc\_source sm8475 and os\_profile ipados-16.6.1-20G81; the SM8475 resources live in UniXNU-sm8475-common and the board wiring in dts/mondrian.dts.
- Fork audit 2026-10-31: mzyxsl daed6b5d44e3c62978cc0fce4e876ded2a57afc9 imported with provenance. board.toml uses an exact trust-cache list; unixnu.lock matches the explicit SM8475 feed pin. The current payload reader also accepted an exactly equal scalar hash, so the list is schema hardening rather than a proven former build blocker.
- The current series has 211 ordered patches, ending with 0506-k60-120hz-refresh.patch. The earlier record's 83-patch count is obsolete.

### Completion criteria

- All source pins resolve; every selected component has a record; status shows the intended overrides and patch order.

### Current limits

- Configuration is build-verified; the remaining work is runtime validation of the selected components, not the board.toml wiring.

### Next action

- Re-run the configuration check after any board.toml, feeds.toml or series change and keep this record's patch count in sync.

### Evidence

- `source`: [schema\_version = 2; soc\_source = sm8475; os\_profile = ipados-16.6.1-20G81; \[components\] lists ArmDTPlatform, ArmCpu, XnuPrelink, PongUfs.](https://github.com/Emilelu/UniXNU-mondrian/blob/f92dbda6ca0356a6823b92fe0d85d466fb4a1db5/board.toml)
- `source`: [211 non-empty entries; last entry 0506-k60-120hz-refresh.patch.](https://github.com/Emilelu/UniXNU-mondrian/blob/f92dbda6ca0356a6823b92fe0d85d466fb4a1db5/patches/xnu/series)

## Firmware and boot {#firmware}

`device-verified`

### Hardware and dependencies

- UEFI firmware built from board.toml \[firmware\]: config = mondrian, DSC Platforms/Xiaomi/mondrianPkg/mondrian.dsc, FD Build/mondrianPkg/&\#123;target&\#125;\_CLANGPDB/FV/SILICIUM\_UEFI.fd.
- 192 MiB UNIXNU payload volume, kernel\_args from \[payload\], and the ADT fields chip\_id = 8015, root\_match\_volume\_uuid and owned\_memory\_size.
- UEFI package set includes &\#123;uefi&\#125;/Binaries/pong for the K60 GOP and DXE binaries.

### Configuration

- \[firmware\] config = "mondrian"; dsc = "Platforms/Xiaomi/mondrianPkg/mondrian.dsc"; fd = "Build/mondrianPkg/&\#123;target&\#125;\_CLANGPDB/FV/SILICIUM\_UEFI.fd"; patches = \[AsmMacroLib.patch, Boot-Manager.patch\].
- \[firmware.defines\] DEVICE\_MODEL = "0", ENABLE\_SECUREBOOT = "0", MEMORY\_PROTECTION = "TRUE", SHIP\_MODE = "FALSE", BUILDID\_STRING = "UniXNU-Mondrian".
- \[payload\] volume = "UNIXNU", size\_mib = 192, loader = "firmware", title = "UniXNU"; \[payload.adt\] chip\_id = "8015", owned\_memory\_size = "0x130000000".

### Procedure

- Build the UEFI firmware from the board.toml \[firmware\] block and package the 192 MiB UNIXNU payload with the kernel\_args list.
- Boot the image with \`scripts/k60-device.sh boot &lt;image&gt;\` and capture the USB CDC console; verify the stage bars, ADT handoff and launchd exec.
- Keep the payload volume under its 192 MiB limit and keep the ADT root\_match\_volume\_uuid aligned with the installed OS.

### Development findings

- UEFI to UniXNU loader to XNU to launchd boots every time: green bar from Entry.S, then the upstream probe's blue and magenta bars at the kernel entry and just before the MMU comes on. This confirms the 0x480 boot\_args ABI, ADT handoff and framebuffer are live on hardware.
- usblog-20261111-233246 reaches \`Pong init: exec original /sbin/launchd\` with max pid 196; the UEFI image and the payload volume are complete.
- A readable kernel panic followed at k60\_fontscale=4 until the CPU start order was fixed; that panic is gone.

### Completion criteria

- Firmware image builds, enters UniXNU, publishes the framebuffer and preserves the documented memory reservations.

### Current limits

- UEFI and payload are complete and the chain reaches launchd. The 2026-11-11 capture has no recorded source revision; revision pending.

### Next action

- Record the image hash and source revision for the next boot, then re-check the payload size and ADT UUID after any firmware change.

### Evidence

- `device`: [usblog-20261111-233246 \(boot-v15-20261108.img, sha256 A6165F2404568C1D3D6C44EC1E71DB59039FF03CC2A1FE573692D231336EA51A\): \`Pong init: exec original /sbin/launchd\`; max pid 196; UEFI to UniXNU loader to XNU to launchd chain complete.](https://github.com/Emilelu/UniXNU-mondrian/blob/f92dbda6ca0356a6823b92fe0d85d466fb4a1db5/README.md)
  Command: <code>scripts/k60-device.sh boot E:/k60-work/usb-a-stage/out/boot-v15-20261108.img</code>. Revision: `0000000000000000000000000000000000000000`.
- `device`: [Historical route-a-18 milestone: Darwin 24 loader boots the board every time; green bar from Entry.S, then the upstream probe's blue and magenta bars at the kernel entry and just before the MMU comes on. Confirms the 0x480 boot\_args ABI, ADT handoff and framebuffer on hardware.](https://github.com/Emilelu/UniXNU-mondrian/blob/f92dbda6ca0356a6823b92fe0d85d466fb4a1db5/docs/reference/ROUTE-A-18-STATE.md)
  Command: <code>scripts/k60-device.sh boot /mnt/d/Android/k60-ios/boot-darwin24-bc8.img</code>. Revision: `d2af811a6dc9c6225de586e1615ca3824e2edce4`.

## CPU and interrupts {#cpu}

`device-verified`

### Hardware and dependencies

- SM8475 eight-core MPIDR table from the vendor device tree: 0x000..0x700 with Aff1 equal to the core index.
- PSCI CPU\_ON targets and the ADT per-CPU reg values; GIC range, timer frequency and IPI configuration from the SoC dtsi.

### Configuration

- board.toml \[payload\] cpus = 8.
- dts/mondrian.dts must not override the SoC dtsi cpu nodes; the ADT generator needs their compatible string and unixnu,cluster-type.
- PSCI CPU\_ON uses the same MPIDR value as the ADT per-CPU reg.

### Procedure

- Start the boot CPU, then start CPU 1..7 through PSCI and record each \`ArmCpu: CPU N PSCI start PASS result=0\` line.
- Verify that each secondary reaches its own entry checkpoint and serves a timer interrupt before claiming per-core completion.

### Development findings

- The SM8475 hardware MPIDRs are flat: 0x000..0x700, Aff1 = core index. The vendor device tree and the Android tree carry the same table, and this firmware rejects every CPU\_ON target outside it. The 4/3/1 A510/A710/X2 grouping in Android sysfs is L2/L3 cache topology, not MPIDR affinity.
- A starting core is matched to its cpu data by MPIDR &amp; 0xFFFF against the ADT per-CPU reg, and the same value is the PSCI target, so the ADT must carry the real MPIDRs.
- usblog-20261111-233246 reports \`ArmCpu: CPU 1 PSCI start PASS result=0\` through \`CPU 7\`, so all eight cores start.

### Completion criteria

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU.

### Current limits

- All eight cores start through PSCI; per-secondary timer/IPI checkpoints beyond the entry are not yet instrumented. The 2026-11-11 capture has no recorded source revision; revision pending.

### Next action

- Add a per-secondary timer/IPI checkpoint and record it on the next boot.

### Evidence

- `device`: [usblog-20261111-233246 \(sha256 A6165F2404568C1D3D6C44EC1E71DB59039FF03CC2A1FE573692D231336EA51A\): ArmCpu CPU 1..7 PSCI start PASS result=0; all eight cores online.](https://github.com/Emilelu/UniXNU-mondrian/blob/f92dbda6ca0356a6823b92fe0d85d466fb4a1db5/README.md)
  Command: <code>scripts/k60-device.sh boot E:/k60-work/usb-a-stage/out/boot-v15-20261108.img</code>. Revision: `0000000000000000000000000000000000000000`.

## Memory and DMA {#memory}

`implemented`

### Hardware and dependencies

- SM8475 DRAM map from live serial: six RAM banks with a 28 GiB hole at 4..32 GiB; the unit has 12 GiB installed.
- Reserved regions owned by UEFI/DXE and the loader's DarwinBoot window; SMMU and DMA ownership.

### Configuration

- board.toml \[payload\] dram\_size = 0x140000000; \[payload.adt\] owned\_memory\_size = 0x130000000 \(4.75 GiB window\).
- dts/mondrian.dts memory nodes and the loader memory map must describe the same banks and reservations.

### Procedure

- Read /memory/reg from live serial and rooted /proc/iomem; compare with the loader window before changing owned\_memory\_size.
- Boot a candidate window and record mem=actual=managed plus the loader's \`window ... bytes at pa ...\` line.

### Development findings

- Live serial-6033dbec /memory/reg and rooted /proc/iomem give six RAM banks with a 28 GiB hole at 4..32 GiB. The installed 12 GiB cannot be one XNU window: the longest contiguous unreserved run is 8.65 GiB \(0x840000000..0xa69b78000\).
- The 4 GiB window booted XNU at mem=actual=managed=4096 MiB. An 8 GiB window \(arena equal to the whole 8 GiB\) was refused: DXE occupies part of the arena, so DarwinBoot returned to the UniXNU menu.
- An 8.625 GiB arena \[0x840000000,0xa68000000\) with a 7 GiB window is accepted: the loader printed window 0x1c0000000 bytes at pa 0x8400200000 and HANDOFF EXIT RETURN 0. DarwinWindowSizeValid caps a window at 8 GiB, so 12 GiB is not reachable at all.
- board.toml now declares the next ladder step, a 4.75 GiB window \(owned\_memory\_size = 0x130000000\), after a 5 GiB window reported NO WINDOW.

### Completion criteria

- All handoff regions are accounted for and each enabled DMA engine accesses its allocated range with the documented cache policy.

### Current limits

- The 4 GiB window and the 8.625 GiB arena are the measured configurations; the current 4.75 GiB window has no device capture yet, and 12 GiB is physically impossible as one window. The 2026-11-11 capture has no recorded source revision; revision pending.

### Next action

- Boot the 4.75 GiB window and record mem=actual=managed plus the loader window line before updating this area to device-verified.

### Evidence

- `host`: [8.625 GiB arena and 7 GiB window; strict v4 round trip PASS; image sha256 8ea52daf4b3e926d4840e13a73fa00c9cadf9b3f1e97e1ececfdaa446e1afc34.](https://github.com/Emilelu/UniXNU-mondrian/blob/f92dbda6ca0356a6823b92fe0d85d466fb4a1db5/docs/audits/MEASURED-HIGH-WINDOW-2026-11-02.md)
  Command: <code>python3 repair-high-window.py; build-uefi-8g.sh; build-kernel-summary.sh; package-textonly.py</code>. Revision: `48abe35d0a0a57f5fea9f9ba1e570800021ae6b1`.
- `device`: [Loader accepted window 0x1c0000000 bytes at pa 0x8400200000 and HANDOFF EXIT RETURN 0; console output from XNU not yet observed.](https://github.com/Emilelu/UniXNU-mondrian/blob/f92dbda6ca0356a6823b92fe0d85d466fb4a1db5/docs/audits/MEASURED-HIGH-WINDOW-2026-11-02.md)
  Command: <code>fastboot boot /mnt/e/k60-work/candidates/7g/boot-ios16-7g-textonly.img</code>. Revision: `e06211de59325bbd086c312324bdbf40e21d1045`.

## Storage and root {#storage}

`device-verified`

Components: `PongUfs`.

### Hardware and dependencies

- UFS controller at ufshc@D84000 through NativeUfs/PongUfsBlock; APFS OS, SystemOS and Data windows.
- board.toml \[userdata\] geometry and the GPT-wrapped APFS Data window installed into the unixnu SHNGROOT.

### Configuration

- \[userdata\] first\_lba = 53342976, last\_lba = 61731583, lba\_bytes = 4096; windows = \[&\#123; name = "OS", component = "OS" &\#125;, &\#123; name = "SystemOS", component = "Cryptex1,SystemOS" &\#125;\].
- PongUfsTransport gates every write on pong\_ufs\_readwrite=1; the Data window is mounted at /private/var with pong\_data\_mount=1 and pong\_data\_rw=1.

### Procedure

- Boot with \`pong\_ufs\_readwrite=1 pong\_data\_mount=1 pong\_data\_rw=1\` and capture the APFS binding and mount lines.
- Verify \`PONG APFS: OS root binding PASS\`, the SystemOS union mount, and \`K60DATA mount returned error=0 result=0 rw=1\`.

### Development findings

- usblog-20261111-233246 binds the OS UUID C5DAF029-2070-4F68-B3CC-1D1320344CF0 to /dev/disk5s1: \`PONG APFS: OS root binding PASS dev=900000a\`.
- SystemOS UUID 15B507FA-21B7-4EE5-B55D-0F3445DE0752 mounts read-only union at /: \`PONG APFS: SystemOS mounted dev=9000006 ro=1 union=1 flags=14809021\`.
- Data UUID 1BCD69FF-24A5-48B1-94B6-8FE592B2F597 binds to /dev/disk4s1 and mounts read-write: \`K60DATA mount returned error=0 result=0 rw=1\`; \`K60UFS write\#0..\#7 result=0 done=4096..12288 ready=1 poison=0\`.
- The 2026-10-31 user console reported APFS Data ENOSPC \(free\_blocks around 1208 below threshold\_blocks 1310\). The 2026-11-11 capture shows successful writes, but the 256 MiB APFS container in a 258 MiB Data window remains a capacity risk.

### Completion criteria

- Host: register, clock, link and SMMU facts match the board inventory.
- Reads: SCSI capacity, GPT and known blocks are correct; OS/SystemOS windows stay within userdata.
- Root: the configured volume mounts and launchd starts. Persistence: writes survive reboot within the allocated Data region.

### Current limits

- Data is read-write on hardware. The 2026-11-11 capture has no recorded source revision; revision pending. The 256 MiB Data container's free space is still a risk under sustained userland load.

### Next action

- Record the image hash and source revision, then measure free blocks after a sustained launchd/userland run.

### Evidence

- `device`: [usblog-20261111-233246 \(sha256 A6165F2404568C1D3D6C44EC1E71DB59039FF03CC2A1FE573692D231336EA51A\): PONG APFS: OS root binding PASS dev=900000a; SystemOS mounted dev=9000006 ro=1 union=1; K60DATA mount returned error=0 result=0 rw=1; K60UFS write\#0..\#7 result=0.](https://github.com/Emilelu/UniXNU-mondrian/blob/f92dbda6ca0356a6823b92fe0d85d466fb4a1db5/README.md)
  Command: <code>scripts/k60-device.sh boot E:/k60-work/usb-a-stage/out/boot-v15-20261108.img</code>. Revision: `0000000000000000000000000000000000000000`.
- `source`: [\[userdata\] first\_lba = 53342976, last\_lba = 61731583, lba\_bytes = 4096; OS and SystemOS windows declared; unixnu userdata geometry matches the installed GPT.](https://github.com/Emilelu/UniXNU-mondrian/blob/f92dbda6ca0356a6823b92fe0d85d466fb4a1db5/board.toml)

## Display {#display}

`device-verified`

### Hardware and dependencies

- UEFI GOP framebuffer from the firmware; panel 1440x3200; MiniIOMobileFramebuffer and the DCS backlight sequence 0x11/0x29/0x51.

### Configuration

- board.toml \[payload\] kernel\_args fb\_threads=3, k60\_textonly=1, k60\_fontscale=3; display source in package/MiniIOMobileFramebuffer.cpp and the display patch series 0210/0213.

### Procedure

- Boot with the display patches and capture \`MiniIOMobileFramebuffer: N frames in ... ms\`; verify the panel geometry and the swap surface lines.

### Development findings

- usblog-20261110-234429: \`MiniIOMobileFramebuffer: 301 frames in 5002 ms \(60 a second\)\` on the 1440x3200 panel; \`swap 8 layer 0: surface 16 \(1440x3200 'BGRA'\)\` shows surfaces switching.
- The 2026-11-11 boot shows \`21 frames in 39585 ms \(0 a second\)\` with the GPU path, so the verified 60 fps result is the 2026-11-10 software path, not the current GPU composition path.

### Completion criteria

- A known frame appears with correct geometry and colors, then userland presentation and backlight controls work.

### Current limits

- 60 fps is verified on the 2026-11-10 software path. The 2026-11-11 boot shows 0 fps with the GPU path; GPU scanout is not enabled. The 2026-11-10 capture has no recorded source revision; revision pending.

### Next action

- Re-run the software path to confirm 60 fps after the Metal changes, then enable pong\_gpu\_scanout=1 only after the accelerator publishes.

### Evidence

- `device`: [usblog-20261110-234429 \(sha256 A2C00973DDAC5F897E9C5D991AC90C73756EDBF504D505ED4B3B496DFFA08642\): MiniIOMobileFramebuffer: 301 frames in 5002 ms \(60 a second\); swap 8 layer 0 surface 16 1440x3200 BGRA.](https://github.com/Emilelu/UniXNU-mondrian/blob/f92dbda6ca0356a6823b92fe0d85d466fb4a1db5/docs/audits/MEASURED-HIGH-WINDOW-2026-11-02.md)
  Command: <code>scripts/k60-device.sh boot E:/k60-work/usb-a-stage/out/boot-v15-20261108.img</code>. Revision: `0000000000000000000000000000000000000000`.

## Input {#input}

`implemented`

### Hardware and dependencies

- Goodix GT9916R Berlin-D on SPI SE4 \(990000.spi\); TLMM GPIO 20 reset and GPIO 21 INT; IOVDD pm8350c\_l2 and AVDD GPIO71.
- Config blob goodix\_cfg\_group\_m11a.bin \(ic=Berlin, cfg\_type=1, sensor=255, pid=9916R, 1488-byte payload\).

### Configuration

- board.toml kernel\_args k60\_touch\_se=19; dts/mondrian.dts touch node compatible xiaomi,m11a-spi.
- Poll cadence changed from 2 ms to 20 ms in the touch patch; the read window is 0x10000..0x107FF.

### Procedure

- Power the rails through RPMh ACTIVE TCS4; use GPIO bit-bang SPI mode 0 with a 2 us half-period; probe 0x10000 for the BRL identity string.
- Download the 1488-byte config to fw\_buffer\_addr 0x1205c, then poll touch\_data\_addr 0x10308 every 20 ms and snapshot 0x10400 for raw frames.

### Development findings

- The chip is a Goodix GT9916R Berlin-D. The protocol is BRL: 0x10000 reads \`BERLIN 9916R 05.80.02.63\`, while GTP registers 0x8140, 0x8047, 0x804E and 0x814E all return 0x00. \`goodix\_ts\` is only the module name, not the protocol.
- Power: TLMM window 0x80000 + RPMh ACTIVE TCS4 + CMD\_STATUS criterion; rails come on without timeout.
- SPI: SE4 \(990000.spi\) is GSI-only and its FIFO is disabled by hardware, so the driver uses GPIO bit-bang \(mode 0, 2 us half-period\). dev\_confirm writes 8 x 0xAA to 0x10000 and reads them back consistently.
- Config: \`CFG-START state=80 ack=80 OK-config-ready\`; \`CFG-DL wrote=1488/1488 bad=0 -&gt; DATA-OK\`; \`CFG-WRITE ack=80 OK\`; \`CFG-EXIT ack=80 OK-config-applied\`; \`CFG-RESET re-handshake OK \(rb=01\)\`.
- The chip is scanning: INT goes low 16 times and the 0x10400 raw-frame area changes by 551 bytes between snapshots. The 0x10308 touch report area never changes and its first byte stays 0x00, so no touch point is produced.

### Completion criteria

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive, and buttons produce expected HID reports.

### Current limits

- Touch points remain zero: 0x10308 first byte stays 0x00 although 0x10400 raw frames change by 551 bytes. The 20 ms poll cadence is not yet device-verified; the 2026-11-11 capture has no recorded source revision \(revision pending\).

### Next action

- Boot with the 20 ms poll, snapshot 0x10000..0x107FF on each INT-low event, and record whether 0x10308 becomes non-zero; if it stays zero, decompile vendor goodix\_core.ko for the real startup sequence.

### Evidence

- `device`: [usblog-20261111-233246 \(sha256 A6165F2404568C1D3D6C44EC1E71DB59039FF03CC2A1FE573692D231336EA51A\): BRL 0x10000 reads BERLIN 9916R 05.80.02.63; GTP 0x8140/0x8047/0x804E/0x814E all 0x00; CFG-START state=80 ack=80; CFG-DL wrote=1488/1488 bad=0.](https://github.com/Emilelu/UniXNU-mondrian/blob/f92dbda6ca0356a6823b92fe0d85d466fb4a1db5/docs/engineering/ANDROID-HW-TRUTH.md)
  Command: <code>scripts/k60-device.sh boot E:/k60-work/usb-a-stage/out/boot-v15-20261108.img</code>. Revision: `0000000000000000000000000000000000000000`.
- `device`: [P-124/P-125: INT low 16 times; 0x10308 64-byte snapshot identical; 0x10400 changed 551 bytes between snapshots; touch points stay 0.](https://github.com/Emilelu/UniXNU-mondrian/blob/f92dbda6ca0356a6823b92fe0d85d466fb4a1db5/docs/engineering/PITFALLS.md)
  Command: <code>scripts/k60-device.sh boot E:/k60-work/usb-a-stage/out/boot-v15-20261108.img</code>. Revision: `0000000000000000000000000000000000000000`.
- `device`: [P-129: same-SoC PHK110 reference requires a \~20 ms cadence; the poll loop was changed from 2 ms to 20 ms and is pending verification.](https://github.com/Emilelu/UniXNU-mondrian/blob/f92dbda6ca0356a6823b92fe0d85d466fb4a1db5/docs/engineering/PITFALLS.md)
  Command: <code>scripts/k60-device.sh boot E:/k60-work/usb-a-stage/out/boot-v15-20261108.img</code>. Revision: `0000000000000000000000000000000000000000`.

## GPU {#gpu}

`implemented`

### Hardware and dependencies

- Adreno 730v3 in SM8475; GPU firmware a730\_sqe.fw \(74,676 B\), gmu\_gen70000.bin \(57,272 B\), a730\_zap.mdt/.b01/.b02; GPU SMMU and 42-step Adreno bring-up.
- Metal plugin bundle PongAdrenoMetal.bundle deployed to /private/var/pong/PongAdrenoMetal.bundle.

### Configuration

- board.toml kernel\_args pong\_adreno\_start=1 and pong\_metal=2; drivers/PongAdreno and drivers/PongMetal; script scripts/generate-pong-cp-profile.py.
- Metal plugin deploy bytes=94928; bundle owner 0; Info.plist and PongMetalBridge.dylib deployed by the init seed path.

### Procedure

- Boot with pong\_adreno\_start=1 and capture the Adreno bring-up lines; count the \`result=0\` lines \(42 expected\) and check \`K60METALPLUGIN deploy bytes=94928 resid=0 error=0\`.
- Check \`IOAcceleratorES provider published\` count and the \`native Metal entry\` line before enabling pong\_gpu\_scanout=1.

### Development findings

- Kernel Adreno initialization succeeds: 42 lines \`result=0\`, including CP ME\_INIT / CP ready / CP-user-client startup / CX clocks / Cape GPU PLL / GBIF traffic / GMU firmware+HFI / GMU native4K context / GMU power handshake / GPU IRQ332 owner / GPU SMMU IDs / GPU native4K+SQE / GX OOB+START / LPAC shared context / PAS13 ZAP auth / CP\_ME\_INIT bootstrap / native BO pool / parent ARC votes.
- The Metal plugin is deployed: \`K60METALPLUGIN deploy bytes=94928 resid=0 error=0\`; \`Pong init: Metal seeds ready=2 failed=0\`.
- The accelerator is not published: \`IOAcceleratorES provider published\` count is 0, \`native Metal entry\` is absent, and the framebuffer reports \`21 frames in 39585 ms \(0 a second\)\`.
- The startup switches were previously absent: drivers/PongAdreno/PongAdrenoPlatform.cpp:392 requires pong\_adreno\_start=1, and PongAdrenoClient.cpp:202 / PongAdrenoNativeGlue.cpp:30 require pong\_metal=1; board.toml and packv15.sh had neither, so the driver never ran. The current boot uses pong\_metal=2, which avoids the backboardd plugin-injection crash documented in P-120.
- The GPU firmware set is complete under D:/Android/k60-ios/firmware/k60-gpu: a730\_sqe.fw \(74,676 B\), gmu\_gen70000.bin \(57,272 B\), a730\_zap.mdt/.b01/.b02. The Metal userspace bridge comes from zizhan \(same SM8475/Adreno 730\): patches/metal2vulkan 14 patches, patches/mesa 4 patches, drivers/PongMetal.

### Completion criteria

- GPU submissions complete, mapping/fence handling is correct, a known image renders, and the selected Metal client presents it.

### Current limits

- Kernel initialization and plugin deployment pass; IOAcceleratorES publishes 0 times, native Metal entry is absent and frame rate is 0. Display remains on the software path; boot-args use 593/608 bytes. The 2026-11-11 capture has no recorded source revision \(revision pending\).

### Next action

- Boot with pong\_metal=1 and confirm the provider publication and native Metal entry before enabling pong\_gpu\_scanout=1; keep the boot-args budget under 608 bytes.

### Evidence

- `device`: [PONG ADRENO: 22-step initialization complete with 42 result=0 lines \(CP ready, GMU, CX clocks\); K60METALPLUGIN deploy bytes=94928 resid=0 error=0.](https://github.com/Emilelu/UniXNU-mondrian/blob/f92dbda6ca0356a6823b92fe0d85d466fb4a1db5/docs/engineering/K60-TOUCH-CHECKLIST.md)
  Command: <code>scripts/k60-device.sh boot E:/k60-work/usb-a-stage/out/boot-v15-20261108.img</code>. Revision: `0000000000000000000000000000000000000000`.
- `device`: [usblog-20261111-233246 \(sha256 A6165F2404568C1D3D6C44EC1E71DB59039FF03CC2A1FE573692D231336EA51A\): IOAcceleratorES provider published 0 times; native Metal entry absent; 21 frames in 39585 ms \(0 a second\).](https://github.com/Emilelu/UniXNU-mondrian/blob/f92dbda6ca0356a6823b92fe0d85d466fb4a1db5/docs/engineering/PITFALLS.md)
  Command: <code>scripts/k60-device.sh boot E:/k60-work/usb-a-stage/out/boot-v15-20261108.img</code>. Revision: `0000000000000000000000000000000000000000`.

## Network {#network}

`planned`

### Hardware and dependencies

- WCN6855/QCA6490 over PCIe0: six register windows, BAR0 0x60200000/2 MiB, GPIO 80/81/82/94/95/96/204, SID 0x1c01, IOVA 0xA0000000/256 MiB and MSI SPI140.
- Firmware amss.bin 5,470,128 B, amss20.bin 5,296,128 B, Data.msc 889,524 B, Data20.msc 916,071 B; Bluetooth BDF bd\_m11agf.elf 60,000 B.

### Configuration

- board.toml declares no network component yet; dts/mondrian.dts does not describe PCIe0, the WCN power rails or the Bluetooth UART.

### Procedure

- Bring up PCIe0 enumeration and BAR0 first, then load Ath12kWifi and its MHI/QRTR transport.
- Bluetooth follows the QcaBluetooth path over GENI UART; record the firmware and BDF actually loaded.

### Development findings

- Official Ath12kWifi shared station component is available \(https://github.com/UniXNU/Ath12kWifi.git at f6bf561f92cc42761bdd417fce1d53fe1db9477c\), docs/plans/WIFI-PORT-PLAN.md:32.
- K60 PCIe/BAR0/GPIO/SID match the Pong reference: PCIe0 six reg windows, BAR0 0x60200000/2 MiB, GPIO 80/81/82/94/95/96/204, SID 0x1c01, IOVA 0xA0000000/256 MiB and MSI SPI140 \(docs/plans/WIFI-PORT-PLAN.md:15\).
- Android truth: WiFi qca6490 connects to 5G with rssi -53 at 5180 MHz; Bluetooth uses bd\_m11agf.elf 60,000 B under qbt\_handler/btpower.

### Completion criteria

- Scanning, association, address configuration and sustained receive/transmit traffic pass with the selected firmware.

### Current limits

- WiFi and Bluetooth are not implemented under XNU; only the Android-side truth and the official component mapping are recorded.

### Next action

- Implement PCIe0/BAR0 enumeration and record the first config-space read before loading Ath12kWifi.

### Evidence

Collect evidence using the next action.

## Audio {#audio}

`planned`

### Hardware and dependencies

- ADSP, LPASS and the WCD938x codec; 2x AW882xx smartpa at I2C 0x34/0x35; CS35L41; swr\_dmic.

### Configuration

- board.toml declares no audio component yet; dts/mondrian.dts does not describe the ADSP, codec or smartpa routes.

### Procedure

- Bring up ADSP firmware, GPR/SMEM/SMP2P, then the codec and smartpa routes; verify playback and capture separately.

### Development findings

- K60 has 2x AW882xx smartpa at I2C 0x34/0x35 \(\`awinic,aw882xx\_smartpa@34\` and \`@35\`\), not TFA9873: docs/plans/BT-AUDIO-PORT-PLAN.md:38,192-194,207-210.
- Android truth: wcd938x\_dlkm + wcd937x\_dlkm codecs, aw882xx\_dlkm + cs35l41\_dlkm amplifiers, swr\_dmic\_dlkm digital mic, adsp\_loader\_dlkm + lpass\_cdc\_\* ADSP stack.

### Completion criteria

- Each declared route carries the selected audio format through playback or capture and handles start/stop correctly.

### Current limits

- Audio is not implemented under XNU; only the Android codec topology is inventoried.

### Next action

- Inventory the ADSP firmware partition and GPR services from an Android boot, then record the playback route.

### Evidence

Collect evidence using the next action.

## Power {#power}

`device-verified`

### Hardware and dependencies

- RPMh, TLMM, pm8350c LDOs, GPIO71 AVDD, and the qti\_battery\_charger\_main\_m81 charger.

### Configuration

- board.toml \[payload\] kernel\_args include pong\_ufs\_readwrite=1; dts/mondrian.dts power rails; PongRpmh.cpp uses ACTIVE TCS4 at 0xd00 + 4\*0x2a0.

### Procedure

- Write RPMh TCS4 and wait for CMD\_STATUS\(&amp;0x10100\) == 0x10100 with the TCS idle; map the TLMM window at 0x80000 so GPIO71 is inside it.
- Read battery capacity, temperature, status, current\_now and voltage\_now from the charger path.

### Development findings

- RPMh writes use ACTIVE TCS4 \(0xd00 + 4\*0x2a0, PongRpmh.cpp:8\); completion is CMD\_STATUS\(&amp;0x10100\) == 0x10100 and TCS idle, not IRQ\_STATUS \(P-87\).
- usblog-20261111-233246: \`goodix: RPMh caps=0x800c8104 count=8 ncpt=16 ver=0x20700 tcs4\_idle=1\`; \`goodix: rails on \(ldoc2=0x42c00, AVDD gpio71=1\)\`.
- TLMM window must be 0x80000: 0x20000 covers only gpio32, and the gpio71 \(AVDD\) address 0x147000 falls outside the window, so writes fail silently \(P-82\).
- Android truth: battery capacity 100, temp 358 \(35.8 C\), status Charging, current\_now 836 mA, voltage\_now 4,333 mV; charger qti\_battery\_charger\_main\_m81.

### Completion criteria

- Declared power controls and battery readings match observations; each claimed sleep/resume transition restores its dependent peripherals.

### Current limits

- pm8350c LDO readback offsets are not confirmed: +0x40/+0x41/+0x46 are MT6360 offsets, and applying them to pm8350c reads common registers \(P-85\). GPIO71 output voltage has not been measured. The 2026-11-11 capture has no recorded source revision \(revision pending\).

### Next action

- Read back ldoc2/ldoc3 through RPMh and record the measured voltages.

### Evidence

- `device`: [P-86/P-87; usblog-20261111-233246 \(sha256 A6165F2404568C1D3D6C44EC1E71DB59039FF03CC2A1FE573692D231336EA51A\): RPMh caps=0x800c8104 count=8 ncpt=16 ver=0x20700 tcs4\_idle=1; rails on \(ldoc2=0x42c00, AVDD gpio71=1\).](https://github.com/Emilelu/UniXNU-mondrian/blob/f92dbda6ca0356a6823b92fe0d85d466fb4a1db5/docs/engineering/PITFALLS.md)
  Command: <code>scripts/k60-device.sh boot E:/k60-work/usb-a-stage/out/boot-v15-20261108.img</code>. Revision: `0000000000000000000000000000000000000000`.
- `device`: [Battery capacity 100, temp 358 \(35.8 C\), status Charging, current\_now 836 mA, voltage\_now 4,333 mV; charger qti\_battery\_charger\_main\_m81.](https://github.com/Emilelu/UniXNU-mondrian/blob/f92dbda6ca0356a6823b92fe0d85d466fb4a1db5/docs/engineering/ANDROID-HW-TRUTH.md)
  Command: <code>adb shell cat /sys/class/power_supply/battery/*</code>. Revision: `0000000000000000000000000000000000000000`.

## Image assembly {#packaging}

`host-verified`

### Hardware and dependencies

- XNU kernel, prelink, payload, ADT and the 211-patch series; macOS build host with the iPhoneOS SDK and DriverKit caches.

### Configuration

- board.toml \[payload\] volume/size/loader and \[firmware\] fd; patches/xnu/series is the authoritative patch order.

### Procedure

- Build the kernel and prelink with the documented unixnu commands, then assemble the boot image and run \`scripts/verify-boot-img-payload.py\`.

### Development findings

- The three local trees use different userland models: ours keeps an OS+SystemOS read-only APFS union from the unixnu partition; ios-sweet-k60 rewrites a writable HFSX image at build time; UniXNU-pong prepares at run time inside its own static init that becomes PID 1 and then execs launchd. Selected approach: diagnose first and do not replace PID 1, because the launchd chain is already verified and the pong adapter targets Darwin 24 ABI.
- The kernel links and prelinks on macOS CI. Format 1 run 40631225483 produced 54349824 bytes; format 2 run 40650877574 produced 54419456 bytes at the same slide -0xb9c000 and the same lowest component extent 0xfffffff004426600.
- The 69632-byte difference is a real fix, not noise: the format-1 glob applied zzzzzz-pong-init-scratch-allocation.patch through fuzz and the panic string it adds is absent from that kernel, while the strict format-2 series applies it at its intended place and the string is present.

### Completion criteria

- Kernel and prelink succeed, payload contains all declared inputs, and the boot image matches the bootloader format and size limit.

### Current limits

- The build and payload chain is host-verified; device flashing is covered by the firmware area. Rebuild the payload after any patch-series change.

### Next action

- Rebuild and rerun scripts/verify-boot-img-payload.py after the next series update.

### Evidence

- `host`: [Build kernel succeeded on macOS from this revision: prelink slide -0xb9c000, 54419456 bytes, lowest component extent 0xfffffff004426600.](https://github.com/Emilelu/UniXNU/actions/runs/40650877574)
  Command: <code>./unixnu build kernel -D ../UniXNU-mondrian</code>. Revision: `6a10bf5e42ecfad7eed2789cc091287d31009623`.
- `host`: [Route a-18 chain reproduces end to end: kernel 20,872,544 B \(15966fcd\) -&gt; prelink 54,808,576 B -&gt; payload 201,326,592 B -&gt; boot-darwin24-bc6.img; the verifier checks the kernel slot, ramdisk slot and kernel.macho.](https://github.com/Emilelu/UniXNU-mondrian/blob/f92dbda6ca0356a6823b92fe0d85d466fb4a1db5/scripts/verify-boot-img-payload.py)
  Command: <code>python3 scripts/k60-prelink-darwin24.py &amp;&amp; python3 scripts/verify-boot-img-payload.py --img /mnt/d/Android/k60-ios/boot-darwin24-bc6.img --payload /tmp/k60build/out/mondrian/ipados-18.7.10-22H374/mondrian/payload/payload.img --kernel /tmp/k60build/out/mondrian/ipados-18.7.10-22H374/mondrian/kernel/kernel.macho</code>. Revision: `e636e445b621bed4fac0069f3604b87061350a8d`.

## cellular {#cellular}

`planned`

### Hardware and dependencies

- K60 carries a Snapdragon X65-class modem inside the SM8475 package; it is not an external modem over PCIe.
- Modem firmware, EFS/NV data and the SIM identity live on the Android side of this dual-system unit and have not been inventoried from a live boot.
- No QRTR/QMI endpoint, IPA path or SIM slot has been exercised under XNU on this board.

### Configuration

- board.toml declares the SM8475 SoC but no cellular component; the modem is not yet listed in \[components\].
- dts/mondrian.dts does not describe the modem's memory regions, QRTR transport or IPA queues.

### Procedure

- Inventory the modem firmware partition and the QRTR/QMI services from an Android boot before writing any driver.
- Record the IPA/QMAP configuration and the SIM identity source \(physical slot or eSIM\) for this unit.
- Only then decide whether the baseband path is in scope for this port.

### Development findings

- The port currently has no baseband support at all; Android's own modem stack is untouched on the other side of the dual-system split.
- Recording it as planned rather than not-applicable keeps the gap visible: this board does have a modem, it is simply not implemented.

### Completion criteria

- A device boot shows the modem enumerated over QRTR with a readable firmware revision.
- A data session or at least a registered network is observed, with the command and image revision recorded.

### Current limits

- No modem firmware, EFS/NV or SIM data has been read from this unit.
- The IPA and QMAP paths are unexamined; nothing in this repository touches them.

### Next action

- Read the modem firmware partition and the QRTR service list from an Android boot, then record them here.

### Evidence

- `source`: [Android truth table records the SoC and the peripherals that were actually measured; the modem is not among them, which is why this area stays planned.](https://github.com/Emilelu/UniXNU-mondrian/blob/f92dbda6ca0356a6823b92fe0d85d466fb4a1db5/docs/engineering/ANDROID-HW-TRUTH.md)

## Diagnostics {#diagnostics}

`device-verified`

### Hardware and dependencies

- USB CDC console \(k60\_usblog=2\), applog, panic breadcrumbs, k60-device.sh capture and ramoops.

### Configuration

- board.toml kernel\_args k60\_usblog=2, k60\_console\_export=1, applog=1, applog\_name=runningboardd,backboardd,lsd, debug=0x140.
- scripts/k60-device.sh captures console.log and capture.json with the image hash and log hash.

### Procedure

- Capture a boot with \`scripts/k60-device.sh boot &lt;image&gt;\` and parse console.log; use the breadcrumbs and panic reset to locate a fault.
- Record the image name, image sha256, log name, log sha256 and source revision for every claimed milestone.

### Development findings

- The USB CDC console \(k60\_usblog=2\) is the primary log channel; scripts/k60-device.sh captures a bounded run and writes capture.json with the image name, image sha256, log sha256 and completion flag.
- Imported the source-only offline path/evidence checker from mzyxsl 76552b88441757defce4080a241c2f0ea7464538, preserving current milestone statuses instead of copying its outdated runtime records. scripts/audit-forks.py enumerates public forks and all branches, pins comparison SHAs, and reports candidates without executing or merging fork code. KX SIGKILL records alone do not prove a sender or pressure; 0238 adds committed reason scalars and bounded fallback logging. See docs/audits/FORK-REVIEW.md and docs/audits/BOOT-STALL-2026-10-31.md.
- usblog-20261111-233246 is 229,326 B \(log sha256 21B30DC341A5497DC721D3A12477E78CAE969E60686F8F644014143F4DB12F84\) and capture.json records image boot-v15-20261108.img with sha256 A6165F2404568C1D3D6C44EC1E71DB59039FF03CC2A1FE573692D231336EA51A; the capture is marked incomplete because the budget was exhausted while data was still arriving.

### Completion criteria

- Each claimed milestone has a reproducible command, a matching source/image revision and an accessible result.

### Current limits

- The 2026-11-11 capture is incomplete \(\`budget exhausted while data was still arriving\`\) and its source revision is not recorded; revision pending.

### Next action

- Extend the capture budget and record the image hash plus source revision for the next run.

### Evidence

- `device`: [Breadcrumbs turned a silent reset into a located fault: column 1 showed six squares, column 2 zero, column 3 one, which put the death inside ml\_parse\_cpu\_topology\(\). The first carrier \(u64 slots at 0xA73FF000\) was useless because a hung board never returns DRAM, so the markers moved into the framebuffer; 0245 then produced a readable panic on hardware.](https://github.com/Emilelu/UniXNU-mondrian/blob/f92dbda6ca0356a6823b92fe0d85d466fb4a1db5/patches/xnu-ipados18/0244-k60-breadcrumbs.patch)
  Command: <code>scripts/k60-device.sh boot /mnt/d/Android/k60-ios/boot-darwin24-bc4.img; count the breadcrumb squares</code>. Revision: `e636e445b621bed4fac0069f3604b87061350a8d`.
- `device`: [The upstream entry probe installs on this kernel: stage 1 blue bar, stage 2 magenta bar, stage 3 resets the board through PSCI six seconds after the MMU comes on. The board walked back to fastboot and then to Android by itself, so a hung kernel no longer needs a manual power cycle.](https://github.com/Emilelu/UniXNU-mondrian/blob/f92dbda6ca0356a6823b92fe0d85d466fb4a1db5/docs/reference/ROUTE-A-18-UPSTREAM.md)
  Command: <code>scripts/k60-device.sh boot /mnt/d/Android/k60-ios/boot-darwin24-bc7.img</code>. Revision: `350d1c57c86d2fc562c7fa7529271fdae3af95bc`.
- `device`: [usblog-20261111-233246 \(sha256 A6165F2404568C1D3D6C44EC1E71DB59039FF03CC2A1FE573692D231336EA51A\): full boot reached launchd with max pid 196; capture.json records image boot-v15-20261108.img and log sha256 21B30DC341A5497DC721D3A12477E78CAE969E60686F8F644014143F4DB12F84.](https://github.com/Emilelu/UniXNU-mondrian/blob/f92dbda6ca0356a6823b92fe0d85d466fb4a1db5/README.md)
  Command: <code>scripts/k60-device.sh boot E:/k60-work/usb-a-stage/out/boot-v15-20261108.img</code>. Revision: `0000000000000000000000000000000000000000`.

</div>
