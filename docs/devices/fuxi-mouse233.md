# Xiaomi 13 \(mouse233\)

[mouse233/unixnu-fuxi](https://github.com/mouse233/unixnu-fuxi)

<div v-pre>

Xiaomi 13 \(fuxi\). XNU for iPad7,1 iPadOS 17.7.11 boots from RAM: a UEFI USB bulk receiver takes the payload into DRAM, the UniXNU menu starts DarwinBoot, and XNU switches its root from the RAM block device to the APFS system volume.

Source record: [porting.toml](https://github.com/mouse233/unixnu-fuxi/blob/4545692515a54d8bfc94597a7ba72fd9b25bead5/porting.toml), `4545692515a54d8bfc94597a7ba72fd9b25bead5`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `implemented` |
| [Firmware and boot](#firmware) | `host-verified` |
| [CPU and interrupts](#cpu) | `planned` |
| [Memory and DMA](#memory) | `device-verified` |
| [Storage and root](#storage) | `device-verified` |
| [Display](#display) | `planned` |
| [Input](#input) | `planned` |
| [GPU](#gpu) | `planned` |
| [Network](#network) | `planned` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `planned` |
| [Image assembly](#packaging) | `host-verified` |
| [Diagnostics](#diagnostics) | `device-verified` |

## Configuration {#configuration}

`implemented`

Components: `ArmDTPlatform`.

### Hardware and dependencies

- Xiaomi 13 \(fuxi\), SM8550, fastboot serial fcde91e with an unlocked bootloader.
- iPad\_Pro\_HFR\_17.7.11\_21H461\_Restore.ipsw as the unchanged OS payload.
- The UniXNU tree that provides the build driver, plus edk2 and XNU sources resolved into unixnu.lock.

### Configuration

- board.toml: \[board\] name fuxi, soc SM8550, soc\_source sm8550, os\_profile ipados-17.7.11-21H461, kit sheng.
- board.toml: \[ipsw\] product iPad7,1, version 17.7.11, build 21H461, device\_class j120ap, chip\_id 0x8011, board\_id 12, fetched members KernelCache, DeviceTree, StaticTrustCache and Cryptex1,SystemTrustCache.
- board.toml: \[kernel\] defconfig fuxi\_defconfig, with fuxi\_full\_defconfig, fuxi\_ramroot\_defconfig and sheng\_defconfig also present in configs/.
- board.toml: \[firmware\] config fuxi and dsc Platforms/Xiaomi/fuxiPkg/fuxi.dsc; \[payload\] volume FUXIPAYL.
- feeds.toml declares the IOStorageFamily refer source at ref IOStorageFamily-315, commit e45fbe30a7879e0b16e26dddb78538f1b00e0bff, because scripts/audit-storage-interface.py needs the IOBlockStorageDevice description that the UniXNU feeds do not carry.
- unixnu.lock pins xnu d8b80295118ef25ac3a784134bcf95cd8e88109f and edk2 cfb93724a06ff86ff5ba971413368a7809ee42a5.

### Procedure

- Record the working state first: git status --short, because several sessions share this checkout.
- Parse the board: python3 -c 'import tomllib,pathlib; print\(tomllib.loads\(pathlib.Path\("board.toml"\).read\_text\(\)\)\["board"\]\)'.
- Resolve the board with the driver of the tree the candidates use: ./unixnu status -D ../UniXNU-fuxi.
- Validate this record: python3 scripts/porting-record.py check --device ../UniXNU-fuxi, and add --base &lt;revision&gt; on a proposed branch.

### Development findings

- The board was format 1: board.toml carried no schema\_version, so scripts/sync-devices.py classified it as a legacy entry and the generated device page was a repository link only. The identity fields schema\_version = 2, soc\_source and os\_profile are what the catalog needs to render this record.
- kit stays sheng on purpose. The archive builders inherited from sheng address the device package as kits/sheng, so the value is a link name in the assembled tree, not the board identity.
- The upstream OS profile profiles/os/ipados-17.7.11-21H461/profile.toml already carries the same \[ipsw\] values \(iPad7,1, 17.7.11, 21H461, j120ap, chip\_id 32785, board\_id 12\) and the same xnu revision, so the board level \[ipsw\] is now a redundant override rather than the only source of those values.
- \[components\] include is empty and stays empty in this change. The board still builds the Native\* sources \(NativeRamBlock, NativeUfs, NativeAES, NativePrelink\) that the pre-format-2 driver resolves from its own tree; those names are not in components.toml, and the record checker runs with strict catalog mode. The catalog IDs used in this record \(RamBlock, ShengUfs, SoftwareAES, XnuPrelink, ArmSmmu4K\) are the canonical names of the same implementations.
- Adding schema\_version = 2 does not disturb the recovered candidates: the pre-format-2 driver ignores the key and ./unixnu status still exits 0, while the format-2 driver stops at feeds.toml needs a source with kind = "soc" and name = "sm8550".

### Completion criteria

- board.toml, feeds.toml, the defconfigs and unixnu.lock resolve together, and the record identity matches the board name, soc and os\_profile.
- The device page is generated from this record instead of a bare repository link.

### Current limits

- The layered format 2 build path is not adopted. It needs a SoC source entry pinned in feeds.toml, a component selection, and a \[device\_tree\] source, and this repository has no dts/ directory.
- The board.toml header comment described the Xiaomi Pad 6S Pro \(sheng\) after the fork; it now names the Xiaomi 13 \(fuxi\).
- The README now documents the fuxi RAM receiver workflow. Keep its build steps aligned with this record when the board workflow changes.

### Next action

- Add the sm8550 SoC source with a pinned commit to feeds.toml, author dts/fuxi.dts, and fill \[components\] include with catalog IDs once the board builds through the layered driver; then rerun ./unixnu status and the record check.
- Keep the README scope, dependencies, build entry points and link to this record aligned with the current fuxi workflow.

### Evidence

- `source`: [Parses with schema\_version = 2 and keeps the format 1 tables \(ipsw, userdata, kernel, firmware, payload\), so the board's own scripts and the pre-format-2 driver keep working.](https://github.com/mouse233/unixnu-fuxi/blob/4545692515a54d8bfc94597a7ba72fd9b25bead5/board.toml)
- `source`: [Recorded source pins for xnu and edk2 that the candidate builds resolve.](https://github.com/mouse233/unixnu-fuxi/blob/d67e18aec56a21b2e2e81f647b8444f3222ec53d/unixnu.lock)
- `host`: [Exits 0 with the board resolved to fuxi and every driver and kit listed at base.](https://github.com/mouse233/unixnu-fuxi/commit/e5a7d450c159ae662e7d5785eef19d1ba4cb5fec)
  Command: <code>./unixnu status -D ../UniXNU-fuxi</code>. Revision: `e5a7d450c159ae662e7d5785eef19d1ba4cb5fec`.

## Firmware and boot {#firmware}

`host-verified`

Components: `DarwinBoot`.

### Hardware and dependencies

- fuxiPkg DSC and FDF in the uefi-fuxi repository, EDK2 at the pinned commit, and the Mu\_Basecore tree with the BaseTools built as Linux ELF binaries.
- The Docker container unixnu-fuxi-build-arm64, which hosts BaseTools, the EDK2 checkout and the build Python environment.
- A device in fastboot mode, sequence number fcde91e, with an unlocked bootloader.

### Configuration

- \[firmware\] config fuxi, dsc Platforms/Xiaomi/fuxiPkg/fuxi.dsc, fd Build/fuxiPkg/&\#123;target&\#125;\_CLANGPDB/FV/SILICIUM\_UEFI.fd.
- \[firmware.defines\] carries the receiver switches: TRY\_SID\_ROUTE, KEEP\_PHY, SYSTEM\_HANDOFF, DATA\_PORT\_UFS, DATA\_PORT\_PROBE, SCM\_QUERY and USB\_EP0\_TRACE.
- The delivered artifact Mu-fuxi-usb-ram.img is a combined image, so a repack is not a UEFI-only change.

### Procedure

- Build the firmware entry inside the container with scripts/build-fuxi-usb-ram.py, keeping --try-usb-route --keep-phy and adding --system-handoff for system payloads.
- Run the four host checks \(SMMU audit, USB route, receiver, image\) and record real exit codes.
- Boot one window with fastboot boot after confirming the device with fastboot devices, then transfer.

### Development findings

- The receiver ends the transfer after 180 s without host traffic and then attempts shutdown. Whether it returns to the menu or stays resident depends on the candidate, so automatic return to Android cannot be assumed.
- While the receiver window is open, fastboot lists no device. An empty list is not evidence of shutdown and must not trigger a retry boot.
- kernel\_handoff in the build configuration is a configuration bit, not proof that control reached XNU.
- The M1 native UFS diagnostic build was disassembled and contains zero SMC instructions in the native UFS module, and the no-SMC and query variants differ by exactly one SMC site as intended.
- USB\_EP0\_TRACE=0 earlier meant the branch produced no EP0 trace at all because the FUXI\_TRACE\(Arg\) macro expanded wrongly, not merely that logging was reduced. Opening the trace did not even compile: the macro is defined as DEBUG Arg while the call sites already carry their own parentheses, so DEBUG received two arguments. It was corrected to DEBUG \(Arg\) at four sites in Dwc3Endpoint.c and two in FuxiUsbRamDxe.c, and the delivered EFI now contains four FUXI EP0 strings and one USBRAM: setup rt where the parent candidate had none.
- Receiver shutdown is still not achieved: V-A, V-C and V-B each ended the window with STOP status=Time out and buffers retained, and the host showed no VID\_1209 in 278, 109 and 250 samples across the three runs.

### Completion criteria

- The image builds in the container, passes the host checks with exit 0, and on device reaches the UniXNU menu and DarwinBoot and calls ExitBootServices.

### Current limits

- Framebuffer presentation and full reservation preservation are not verified on this board, so this area is not claimed as device verified.
- Receiver shutdown is unverified for the later XNU handoff attempts summarized here: they record normal\_controller\_stop\_verified=false, and the corrected stop readback DSTS=0x0010FFD1 with DEVCTRLHLT=0 and USBLINKST=4 shows the core never confirmed halt. The earlier standalone v23 receiver run did confirm normal controller stop.
- USB disappearance alone does not prove the receiver stopped; a photograph of HALTED, restored routing and USBRAM QUIESCE: Success is required.

### Next action

- Capture photographs of HALTED, route restoration and USBRAM QUIESCE: Success in one receiver attempt, then raise this area to device-verified with that attempt directory as the reference.

### Evidence

- `host`: [Receiver image builds in the container and the SMMU audit, route, receiver, EP0 and stop checks exit 0 on that branch.](https://github.com/mouse233/uefi-fuxi/commit/32b3b57e4bb542136e1a932062e5b10c81b5f287)
  Command: <code>docker exec -w /work/uefi-fuxi unixnu-fuxi-build-arm64 /opt/fuxi-venv/bin/python3 scripts/build-fuxi-usb-ram.py --try-usb-route --keep-phy</code>. Revision: `32b3b57e4bb542136e1a932062e5b10c81b5f287`.
- `source`: [fuxi branch holds the merged upstream fixes with the verified FD and memory layout, SEC FDT range check, restricted payload entry, USB routing and quiesce retained.](https://github.com/mouse233/uefi-fuxi/commit/4fbf22ace7614a0c10ad85930a011acbb8c36302)
- `device`: [V-A with the corrected trace macro prints the real EP0 sequence, including complete ep=0 reg=00000908, so an EP0 EndTransfer does complete, and the window still ends with STOP status=Time out and buffers retained.](https://github.com/mouse233/unixnu-fuxi/blob/1d071dae4618b0676d313cfbe1fc39689e6f139e/diagnostics/ram-root/usb-bulk.md)
  Command: <code>fastboot boot &lt;candidate image&gt;; python3 scripts/boot-ram-window-once.py</code>. Revision: `1d071dae4618b0676d313cfbe1fc39689e6f139e`.

## CPU and interrupts {#cpu}

`planned`

Components: `ArmCpu`.

### Hardware and dependencies

- SM8550 core layout, GIC distributor and redistributor ranges, and the timer rate, all taken from the vendor ABL device tree.
- The boot progress markers compiled into the payload package.

### Configuration

- The kernel configuration comes from configs/fuxi\_defconfig; no board specific affinity or core enablement is recorded for fuxi.

### Procedure

- Enable the boot progress CPU markers, run one RAM receiver attempt, and record which cores report their entry checkpoint in the console log.

### Development findings

- The RAM root chain, including launchd and the later xpcproxy and watchdogd processes, runs and reaches userland, so the primary core path works. Nothing in the logs records secondary core bring-up on this board.

### Completion criteria

- Every enabled CPU reaches its entry checkpoint, and timer and IPI handling work on each enabled core.

### Current limits

- No fuxi specific CPU or interrupt verification exists. The board inherits the configuration carried over from the sheng derived package.

### Next action

- Collect per CPU boot markers from one attempt log and record the enabled core set and GIC ranges actually observed.

### Evidence

Collect evidence using the next action.

## Memory and DMA {#memory}

`device-verified`

Components: `ArmSmmu4K`, `RamBlock`.

### Hardware and dependencies

- The SMEM RAM table, read on device.
- The receiver RAM window that holds the transferred payload, and the KMEM region the kernel reserves for the RAM block device.
- SMMU context banks used by the USB controller and the UFS host.

### Configuration

- \[payload\] dram\_size 0x80000000, the value observed in the SMEM RAM table on this device.
- The handoff window skew must stay congruent with the lowest non empty segment of the delivered kernel.macho modulo 2 MiB. For the recorded build that segment is 0xfffffff00427c000 and the skew is 0x7c000; any kernel layout change requires re-deriving it.
- The RAM block device and KMEM reserve are enabled by the RAM probe macros in the compiled objects, not by patch text alone.

### Procedure

- Read the SMMU state with the audit and route scripts before boot, and record the context bank snapshot after the attempt.
- Recompute the skew from the delivered kernel.macho after every kernel layout change and verify it against the window before packaging.

### Development findings

- SMMU snapshot on the M1 native UFS build: stream ID 60 transitions 0 to 1 as routed, and the final state is SCTLR=0, CBAR=10000 with CBA2R=1, GFSR=0 and FSR=400.
- FSR 400 holds only the format bit. Masked with the ARM\_SMMU\_CB\_FSR\_FAULT definition of c00001fe there is no fault bit, so a non zero FSR or FAR by itself is not evidence of a DMA fault.
- KMEM headroom measured 662548480 bytes with dram\_size 0x80000000, which is what the RAM root and the transferred payload are sized against.
- Before the switch the root is the RAM block device md0 and after the switch it is the APFS system volume, so memory held by the receiver payload is the same memory the root switch walks.

### Completion criteria

- All handoff regions are accounted for, and each enabled DMA engine accesses only its allocated range with the documented cache policy.

### Current limits

- SMMU stream stop and readback after quiesce are not confirmed on device, so DMA teardown during shutdown is unproven.
- These memory values were read on this device and must not be applied to another board or firmware variant without checking.

### Next action

- Take a SMMU snapshot after a confirmed receiver stop, so teardown state can be compared with the recorded SCTLR=0 result.

### Evidence

- `device`: [Records the SID 60 0 to 1 transition and the final SCTLR=0, CBAR=10000, CBA2R=1, GFSR=0 and FSR=400 snapshot for the M1 native UFS receiver run.](https://github.com/mouse233/unixnu-fuxi/blob/9644d94e6bb050e4bde5f50f94312dd10cd3f416/diagnostics/ram-root/usb-bulk.md)
  Command: <code>python3 scripts/test-usb-ram-full.py --expected-sha256 &lt;image-sha&gt; --output out/&lt;candidate&gt;/attempt-NN</code>. Revision: `9644d94e6bb050e4bde5f50f94312dd10cd3f416`.
- `source`: [The probe that reports context bank state is in the device package and builds with the receiver image.](https://github.com/mouse233/unixnu-fuxi/blob/4545692515a54d8bfc94597a7ba72fd9b25bead5/package/ArmSmmu4KProbe.c)

## Storage and root {#storage}

`device-verified`

Components: `RamBlock`, `ShengUfs`, `VerifiedRoot`.

### Hardware and dependencies

- The IPSW members transferred into RAM, including KernelCache, DeviceTree, StaticTrustCache and the SystemOS and system volume payloads.
- The RAM block device the kernel exposes for the receiver window, and the UFS LUN that holds GPT, userdata and the APFS volumes.
- A host with the USB bulk tooling and the device in the receiver window.

### Configuration

- \[payload\] volume FUXIPAYL marks the tagged payload so the firmware boot entry is found.
- Attempts use a per candidate boot profile, for example --boot-profile usb-system, and a separate out/&lt;candidate&gt;/attempt-NN directory with the expected image SHA256.
- The RAM watchdog used by the v46 and v47 work is a software timing backend selected in the build. It is not the SM8550 hardware watchdog, it does not cover a CPU or scheduler hang, and it writes no hardware registers.

### Procedure

- Confirm no receiver, sender or boot task is already running, then confirm fcde91e with fastboot devices.
- Boot one window with fastboot boot, transfer the image, and keep the cable connected until the receiver reports its state.
- Read the console log, then photograph the screen and record the reached stage before writing any conclusion.

### Development findings

- v34 and v35 could not switch roots. /mnt1 was only a secondary read-only mount while the root stayed md0, and the on-system-volume test needs either vnode\_mount to reach vfs\_flags with the MNT\_ROOTFS bit or the authorized APFS leaf check, whose VNOP\_IOCTL returns 80. Neither condition held, so adding a root bit, changing argv or using chroot would not have been a fix.
- v36 reached native SystemOS root authentication with auth=80.
- v37 switched the root natively: pivot=OK old=md0 newroot=apfs, rootfs=1 with the old root rootfs flag cleared, outgoing=/Developer, dev=devfs, /sbin/launchd SHA256 verified, auth=80 and userland=0, with flags 0x14909001 combined with 0x4000 giving 0x1490d001.
- v38 released PID 1 to EL0. v40 completed cache preparation but dyld had no cache and the process ended before main.
- v41 mapped the shared region: SYS\_shared\_region\_map\_and\_slide\_2\_np returned 0, stage=10, main=PASS, PID 1 spawned xpcproxy as child 69, exec=65, and pids 41, 57, 63 and 69 were observed at EL0.
- v42 passed PT\_DENY\_ATTACH up to the SVC observation limit. v43 reached the first natural stop: a watchdogd critical exit panic with namespace 2 and subcode 0x5 \(SIGTRAP\), matching proc\_handle\_critical\_exit, with exec counts moving from 95 to 129 and PID 121 spawning /usr/libexec/watchdogd.
- v44 captured the brk forensics. v46 failed at RAM\_WATCHDOG prepare with errno=6 at RamSystemCache.c:163. v47 fixed the asynchronous registerService race by taking MatchedState immediately.
- The M1 native UFS host reads the GPT and the F2FS metadata header of userdata. Two boots read the 4096 byte metadata first block byte for byte the same \(e77426cf7e4e7d0c2af46e8c8434a358a6c8f923c7b614ec8a72ec288446e51d\) and the same magic 964cc46e 60ab062f each time, while the userdata first block differs between boots \(545471f32e59c962688f8ae078fd768ea54750fa9c14f0a160859c31c3aa8c3e against an earlier ad3ccf81 reading\). The narrowed reading is that Android wrote /data between the two boots, not that the read is unstable or that the volume is damaged. The screen states metadata-decrypt=UNIMPLEMENTED and file-read=UNIMPLEMENTED, so neither read is mounting or decryption, and the historical magic f673c25f 7086bec0 stays unexplained.

### Completion criteria

- Host: register, clock, link and SMMU facts match the board inventory.
- Reads: capacity, GPT and known blocks are correct, and transferred windows stay inside the reserved memory.
- Root: the configured volume mounts and launchd starts. Persistence: writes survive reboot inside the allocated Data region.

### Current limits

- The chain stops at a watchdogd panic, so full userland and the home screen are not reached and persistence is untested.
- errno 6 is ENXIO and three stages share it, and the photograph does not name the stage, so the v46 failing stage is not identified from that evidence. The v47 race fix does not establish the cause of the v46 branch.
- usb-system-mount-v48-linux and usb-system-reference-linux-v1 state that build, full checks and device acceptance are pending and that no v47 conclusion is inherited, so both stay planned for this area.
- The later XNU handoff attempts summarized here record normal\_controller\_stop\_verified=false, so receiver stop is unverified for that attempt series. The earlier standalone v23 receiver run passed normal controller stop.

### Next action

- Capture per call errno and stage names so the v46 prepare failure can be attributed to one stage, then run the v47 image and record the reached stage from a photograph.

### Evidence

- `device`: [pivot=OK old=md0 newroot=apfs with rootfs=1, outgoing=/Developer, dev=devfs and /sbin/launchd SHA256 verified. The iteration log records this as the reading of photo IMG\_6987; the photo file itself is not committed.](https://github.com/mouse233/unixnu-fuxi/blob/9644d94e6bb050e4bde5f50f94312dd10cd3f416/diagnostics/ram-root/usb-bulk.md)
  Command: <code>fastboot boot &lt;receiver-image&gt;; python3 scripts/test-usb-ram-full.py --boot-profile usb-system --expected-sha256 &lt;image-sha&gt; --output out/usb-system-mount-v37/attempt-01</code>. Revision: `38bdf3ebc29dcb29bf7fa0cedc105cec75bc289d`.
- `device`: [Shared region map returned 0, stage=10, main=PASS, PID 1 spawned xpcproxy as child 69 and pids 41, 57, 63 and 69 ran at EL0. Delivered image SHA256 d9111f8b934df910a67bf6787a83b618988aa4cef3cd77eee2de985ab4f31468. The iteration log records photo IMG\_6990 \(its own SHA256 962cbfe9b45ed3d8872949f4443d6f4b37b136f760814db5e3be5d57971d8ccc\) as the source of these readings; the photo file is not committed.](https://github.com/mouse233/unixnu-fuxi/blob/9644d94e6bb050e4bde5f50f94312dd10cd3f416/diagnostics/ram-root/system-root-audit.md)
  Command: <code>python3 scripts/test-usb-ram-full.py --boot-profile usb-system --output out/usb-system-mount-v41/attempt-01</code>. Revision: `4975e049f0bca1d7289f41e6f4c97033fba0212b`.
- `device`: [First natural stop: watchdogd critical exit panic, namespace 2 subcode 0x5, consistent with proc\_handle\_critical\_exit, with exec counts moving from 95 to 129.](https://github.com/mouse233/unixnu-fuxi/blob/9644d94e6bb050e4bde5f50f94312dd10cd3f416/diagnostics/ram-root/watchdog-service.md)
  Command: <code>python3 scripts/test-usb-ram-full.py --boot-profile usb-system --output out/usb-system-mount-v43/attempt-01</code>. Revision: `29f20999162187546d1e32192bceaf20b142ca96`.
- `device`: [RAM\_WATCHDOG prepare failed with errno=6 at RamSystemCache.c:163. The iteration log records this as the reading of photo IMG\_6997, which is not committed. The stage is not identified because three stages share ENXIO and the log entry does not name the stage.](https://github.com/mouse233/unixnu-fuxi/blob/9644d94e6bb050e4bde5f50f94312dd10cd3f416/diagnostics/ram-root/usb-bulk-evidence.json)
  Command: <code>python3 scripts/test-usb-ram-full.py --boot-profile usb-system --output out/usb-system-mount-v46/attempt-01</code>. Revision: `6d3234fdfef8dc5164dcd7f00ff853e355030150`.
- `host`: [System mount host checks run against the candidate output directory and are recorded with their real exit codes.](https://github.com/mouse233/unixnu-fuxi/blob/d67e18aec56a21b2e2e81f647b8444f3222ec53d/diagnostics/ram-root/README.md)
  Command: <code>python3 scripts/check-usb-system-mount.py --output out/&lt;candidate&gt; --base ../unixnu-source</code>. Revision: `d67e18aec56a21b2e2e81f647b8444f3222ec53d`.

## Display {#display}

`planned`

### Hardware and dependencies

- The panel and controller description from the vendor ABL device tree, and the framebuffer handed over by the firmware.

### Configuration

- No fuxi display configuration is recorded. The board inherits the display package files carried over from the sheng derived tree.

### Procedure

- Capture the GOP and handoff framebuffer geometry on device, then compare it with the panel timing the device tree describes.

### Development findings

- The boot chain reaches DarwinBoot and XNU with the console, so an early framebuffer exists, but no log entry records presented frames, stride, format or backlight control on this board.
- The repository holds sheng inherited diagnostics such as analyze-sheng-frame-timing.py and the framebuffer probe files. They are scaffolding and are not display results for fuxi.

### Completion criteria

- A known frame appears with correct geometry and colors, then userland presentation and backlight control work.

### Current limits

- No device evidence for display on fuxi. The last 1300 lines of the receiver log contain no display, touch or backlight entries.

### Next action

- Record the framebuffer address, stride and pixel format that the firmware publishes on this board before selecting any display component.

### Evidence

Collect evidence using the next action.

## Input {#input}

`planned`

### Hardware and dependencies

- The touch controller, its bus, pins and interrupt line, and its firmware, all of which must be read from the vendor device tree for this panel.

### Configuration

- No fuxi input configuration is recorded. The only input related submodule in this repository is drivers/NativeNovatekTouch, inherited from the sheng tree.

### Procedure

- Identify the touch controller and bus on fuxi, then bring up contacts and compare reported coordinates with the display geometry.

### Development findings

- The board is a phone, so its panel and touch parts differ from the tablet the inherited package was written for. Nothing in the logs shows a touch controller being probed on fuxi.

### Completion criteria

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive, and buttons produce the expected HID reports.

### Current limits

- No device evidence for input on fuxi.

### Next action

- Read the touch controller node and interrupt mapping out of the vendor device tree and record them before writing any input configuration.

### Evidence

Collect evidence using the next action.

## GPU {#gpu}

`planned`

### Hardware and dependencies

- The GPU and GMU generation, its firmware, power votes, SMMU stream and submission path.

### Configuration

- No fuxi GPU configuration is recorded. The GPU package files and the many check scripts in this repository come from the sheng tree.

### Procedure

- Establish the GPU and GMU identity on the device, then bring up firmware load and submission before any presentation work.

### Development findings

- The receiver log contains no GPU, Metal or Adreno milestone for fuxi, and the observed userland stop is watchdogd rather than a graphics failure.

### Completion criteria

- GPU submissions complete, mapping and fence handling are correct, a known image renders, and the selected Metal client presents it.

### Current limits

- No device evidence for GPU on fuxi. The Adreno scripts in the repository target the tablet configuration and were not run against this board.

### Next action

- Record the observed GPU and GMU identity and the SMMU stream used by it on fuxi before selecting Adreno components.

### Evidence

Collect evidence using the next action.

## Network {#network}

`planned`

### Hardware and dependencies

- The Wi-Fi function, its bus, firmware, interrupts and DMA, and the OS interface it attaches to.

### Configuration

- No fuxi network configuration is recorded, and this repository declares no Wi-Fi component source.

### Procedure

- Identify the Wi-Fi function and bus on the device, load its firmware, then bring up association and packet transfer.

### Development findings

- The receiver log contains no ath12k, MHI or Wi-Fi entry for this board.

### Completion criteria

- Scanning, association, address configuration and sustained receive and transmit traffic pass with the selected firmware.

### Current limits

- No device evidence for network on fuxi.

### Next action

- Record the Wi-Fi function, bus and firmware path observed on this device, then select the network component.

### Evidence

Collect evidence using the next action.

## Audio {#audio}

`planned`

### Hardware and dependencies

- The DSP, codec, clocks and firmware services, plus the routes the board declares.

### Configuration

- No fuxi audio configuration is recorded.

### Procedure

- Bring up the DSP and its service transport, then move one declared route through playback and capture.

### Development findings

- The receiver log contains no ADSP, GPR or audio entry for this board.

### Completion criteria

- Each declared route carries the selected audio format through playback or capture and handles start and stop correctly.

### Current limits

- No device evidence for audio on fuxi.

### Next action

- Determine whether audio is in the board scope. If it is not, set this area to not-applicable with the reason in limits and keep the component list empty.

### Evidence

Collect evidence using the next action.

## Power {#power}

`planned`

### Hardware and dependencies

- Regulators, clocks, battery units, and the split of ownership between firmware and XNU.

### Configuration

- The watchdog backend selected for the v46 and v47 work is software timing based. It is not the SM8550 hardware watchdog, it does not cover a CPU or scheduler hang, and it writes no hardware registers.

### Procedure

- Identify which power controllers the firmware keeps, then read the battery and regulator units XNU sees and test each claimed transition.

### Development findings

- Only the software watchdog policy and its check script are recorded for this board. No regulator, clock or battery reading was verified on fuxi, and the watchdogd critical exit is an OS level observation rather than power hardware evidence.

### Completion criteria

- Declared power controls and battery readings match observations, and each claimed sleep and resume transition restores its dependent peripherals.

### Current limits

- No device evidence for power on fuxi beyond the software watchdog backend selection and its policy check.

### Next action

- Record the firmware owned power controllers and one regulator reading taken on the device before choosing power components.

### Evidence

Collect evidence using the next action.

## Image assembly {#packaging}

`host-verified`

Components: `XnuPrelink`, `SoftwareAES`.

### Hardware and dependencies

- The XNU revision from unixnu.lock, the DarwinBoot component, the IPSW members, the device tree, the trust cache and the ADT inputs.
- A FAT payload volume tag the firmware loader recognizes.

### Configuration

- \[kernel.prelink\] tool kits/NativePrelink/emit\_prelink.py with kernel macho DEVELOPMENT\_ARM64\_BCM2837/mach.development.bcm2837.unstripped.noctf, slide -0x1000000 and an early\_security\_init address for com.apple.driver.AppleMobileFileIntegrity.
- \[payload\] volume FUXIPAYL, loader firmware, title, and dram\_size taken from the SMEM reading.
- \[payload.adt\] carries the ADT inputs, with the identity seed supplied through --unique-chip-id.

### Procedure

- Build the kernel for the candidate with its own build-kernel.py, then run its finalize.py.
- Package the system payload only through scripts/package-fuxi-xnu-boot.py so the FAT OEM field is FUXIPAYL.
- Run the four host checks plus the image check against the delivered output directory and record each real exit code.

### Development findings

- Calling unixnu.bootimg.build directly writes no OEM tag, and the loader then reports no boot entry found, which is why the packager is mandatory for system payloads.
- v47 deliverables: Mu-fuxi-usb-ram.img 203190272 bytes with SHA256 a95d8052863380289bd16a99813beb927b1dfb82c15b424e808f697c9a50f78b, kernel.macho 52076544 bytes with SHA256 ceafad072116db1018a40ccb3e289ac63c5e87c7efb9335f58739451e8098299, payload.img 201326592 bytes with SHA256 1c347bc832f29c8d3cb6f378f59fb53040513d1c0f03d062ad35e7e9a860a001, and the FUXIPAYL payload ead908fdfdb4d87203b221a01e32f8906e9365491dbdc9c9159ac3e75aa57f61. Eighteen checks under run\_id 20261025T074819.554188Z exited 0.
- Image hashes change between rebuilds of the same configuration, so hash equality does not prove that a define left behavior unchanged. The firmware build log is the reference instead: the first V-A build after the macro fix hashed f7eeeeff and the rebuild with the define added hashed b64dfe07, and the define presence is read from logs/firmware.log \(V-C carries five -DFUXI\_USB\_EP0\_FORCERM=0 lines, V-A none and uses the source default\).
- The EP0 A/B candidates are the delivered artifacts of this round: V-A m1-ab-ep0trace-v3 Mu-fuxi-ufs-m1.img 1871872 bytes b64dfe070131f6fedcb3b08fe92437204fcfb08da72f68bd365cffb68ec2e697, V-B m1-ab-usbonly-v3 Mu-fuxi-usb-ram.img 1863680 bytes ba22cc22bb3f8d7012a1c55168b209d03f2444b6000ed4abca02ddf91f802eb2, V-C m1-ab-ep0noforcerm-v4 1871872 bytes 82925412455da1c76e9e74c73c386bbd0813587d763d620e9785affa0be92723, and V-E m1-ab-ep0snapshot-v6, whose SHA256 the iteration log records only as the prefix 3790775f. V-A and V-B differ from their parent by exactly three files, the two macro corrections and the build tool, so the parent's UFS conclusions carry over.
- For the system volume entry points, the verification that matters is that the compiled kern\_exec.o defines both XNU\_RAM\_ROOT\_PROBE=1 and XNU\_RAM\_USER\_ENTRY=1 and actually references the system-init override and the pre-exec path check. Matching patch text is not that proof.
- The receiver window skew is derived from the delivered kernel, so a kernel layout change invalidates a previously recorded skew.

### Completion criteria

- Kernel and prelink succeed, the payload contains every declared input, the boot image matches the bootloader format and size limit, and the compiled objects carry the required probe macros.

### Current limits

- There is no new delivered image on this host that passed the full check set, so packaging is not claimed as device verified.
- usb-system-mount-v48-linux is rebuilt with a separate toolchain and its own usb-system-mount-v48-linux build. The RAM root, user entry and main entry protections and the compiled object verification are kept, and its candidate REVIEW states that build, checks and device acceptance are pending.

### Next action

- Finish the v48-linux rebuild and its packaging, run the checks with recorded real exit codes, and add the delivered SHA256 here before any boot attempt.

### Evidence

- `host`: [Delivered image v47 hashes recorded above, with eighteen checks at run\_id 20261025T074819.554188Z exiting 0 and bound to that image and source.](https://github.com/mouse233/unixnu-fuxi/blob/283834986151e0911a88ffcb3d5fe8531558f8a7/diagnostics/ram-root/README.md)
  Command: <code>PYTHONDONTWRITEBYTECODE=1 python3 scripts/check-fuxi-usb-ram-image.py --uefi ../uefi-fuxi --output out/usb-system-mount-v47 &amp;&amp; PYTHONDONTWRITEBYTECODE=1 python3 scripts/check-usb-ram.py --uefi ../uefi-fuxi --report out/usb-system-mount-v47/host-tests.json</code>. Revision: `283834986151e0911a88ffcb3d5fe8531558f8a7`.
- `source`: [The packaging entry that writes the tagged payload volume used by the firmware boot entry.](https://github.com/mouse233/unixnu-fuxi/blob/4545692515a54d8bfc94597a7ba72fd9b25bead5/scripts/package-sheng-xnu-boot.py)

## Diagnostics {#diagnostics}

`device-verified`

Components: `ShengPreflight`.

### Hardware and dependencies

- The USB bulk console log from the receiver window, the device screen for photographed state, and the host check reports for each candidate.
- The device identity preflight: serial, product and unlocked state, plus the expected image SHA256.

### Configuration

- Each attempt writes to its own out/&lt;candidate&gt;/attempt-NN directory with the boot profile named. The test host may keep photographs and raw reports there, but those directories are not committed. The iteration log transcribes selected readings from device photographs and is the evidence available in the repository.
- The canonical iteration log is diagnostics/ram-root/usb-bulk.md, appended in order, with conclusions backfilled into the candidate REVIEW.

### Procedure

- Run the host checks in the order the candidate REVIEW gives, and record each real exit code rather than the exit status of a pipeline.
- Boot a single window with scripts/boot-ram-window-once.py or a full transfer with scripts/test-usb-ram-full.py, passing --expected-sha256.
- Read the log, photograph the reached stage, then append the candidate and conclusion to the iteration log.

### Development findings

- Committed records available to a reader: diagnostics/ram-root/usb-bulk.md \(181901 bytes\), usb-bulk-evidence.json \(39315 bytes\), commandcode-evidence.json, full-os-audit.json, watchdog-service.md, apfs-ram-model.md, uefi-ram-transfer.md, wsl-linux-rebuild.md and windows-wsl-migration.md.
- An archived stop reading was corrected from 0010ff11 to DSTS=0x0010FFD1 for photograph IMG\_7055. Both readings support the same conclusion: DEVCTRLHLT=0, USBLINKST=4, and the core never confirmed halt.
- The later XNU handoff attempts summarized here record normal\_controller\_stop\_verified=false, so receiver stop is unverified for that attempt series. The earlier standalone v23 receiver run passed normal controller stop.
- The EP0 and stop model checks compile without -DFUXI\_USB\_DMA32 and without the two macros of the current build, so they do not test the delivered translation unit, and their fixtures are not committed. They cannot serve as host verified evidence.
- The ForceRM difference against the upstream dwc3\_ep0\_end\_control\_data\(\) is a command construction difference only. V-C, which drops ForceRM, still reaches the same Endpoint Command 0x8 on Physical EP 0 timeout, and the photograph shows the difference directly: the submitted command word is cmd=108 where V-A and V-B submit cmd=908, the delta being DWC3\_DEPCMD\_HIPRI\_FORCERM \(BIT11, 0x800\). With the trace macro, the UFS prefix \(V-B, FUXI\_DATA\_PORT\_UFS=0, same sequence shape\) and ForceRM all tested, those three axes are closed.
- An intermittent failure must not be recorded as a certain one: in V-C two EndTransfer completions succeeded at the same endpoint and call site before the third failed, and the earlier reading that EP0 ENDTRANSFER never completes was wrong.
- A proposed fix that clears Ep0RestartFailed together with the EndTransferPending flags was rejected by the driver's own host model, which asserts at dwc3-ep0-host.c:329 that CommandWrites equals Commands and at :325 that Dwc3SetHalt on EP0 returns EFI\_DEVICE\_ERROR. Six of the 19 cases guard exactly this: no further DEPCMD may be written to a block whose CMDACT might never clear, which is also the suspected physical cause here. The change was withdrawn instead of deleting the protection, and the model is back to 19/19.
- One real consequence was confirmed while withdrawing it: the early-out at Dwc3Endpoint.c:895 returns before the DWC3\_DCFG device address is cleared and before the unstall loop, so after the first END failure every later bus reset only sends messages to the receiver and changes nothing in hardware, which keeps the old device address. The conclusion is narrowed to the first failed END being the first cause and the lockout being an amplifier, so clearing the lockout is not the fix.
- Where a log line is ambiguous the record keeps the ambiguity: the v41 last cache-open err=2 does not contradict the successful map because several paths are probed, child=-1 with pe=-1 means the PID was not captured rather than a failed spawn, the abbreviated Rep name is unconfirmed, and the v43 SIGTRAP has no faulting PC or ESR so its direct cause is unproven.

### Completion criteria

- Each claimed milestone has a reproducible command, a matching source or image revision, and an accessible result.

### Current limits

- Candidate REVIEW.md files, the check JSON reports and the photographs live in out/ or on the host and are not committed, so evidence links point at the committed iteration log instead of the primary artifact.
- Board records live on feat/ramdisk-test while the catalog reads the default branch, so this area cites pinned blob URLs rather than repository-relative paths.
- The top level UniXNU-fuxi clone tracks only main, so it needs a fetch before the experiment branch can be inspected there.

### Next action

- Commit each candidate's REVIEW.md and its check reports beside the iteration log so that evidence can reference the primary artifact by path.

### Evidence

- `device`: [Iteration log records the reached stage of each attempt together with the readings transcribed from device photographs, and holds the corrected EP0 stop readings and the false stop verified flags. The photo files themselves are not committed to this repository.](https://github.com/mouse233/unixnu-fuxi/blob/9644d94e6bb050e4bde5f50f94312dd10cd3f416/diagnostics/ram-root/usb-bulk.md)
  Command: <code>python3 scripts/test-usb-ram-full.py --boot-profile usb-system --expected-sha256 &lt;image-sha&gt; --output out/&lt;candidate&gt;/attempt-NN</code>. Revision: `9644d94e6bb050e4bde5f50f94312dd10cd3f416`.
- `host`: [Linux host checks run in the WSL workspace with real exit codes recorded for the rebuild.](https://github.com/mouse233/unixnu-fuxi/blob/0e9eb2196efc5974feed2817e6f56e080e6c68be/diagnostics/ram-root/wsl-linux-rebuild.md)
  Command: <code>PYTHONDONTWRITEBYTECODE=1 python3 scripts/check-usb-smmu-audit.py --uefi ../uefi-fuxi --report out/&lt;candidate&gt;/smmu-tests.json</code>. Revision: `0e9eb2196efc5974feed2817e6f56e080e6c68be`.
- `source`: [Component and source pins recorded for the RAM root path are committed on the default branch.](https://github.com/mouse233/unixnu-fuxi/blob/4545692515a54d8bfc94597a7ba72fd9b25bead5/diagnostics/ram-root/pins.json)
- `device`: [Three receiver runs with one fastboot boot each, plus the V-E read-only failure snapshot, are recorded with host sampling counts and readings transcribed from device photographs. The photo files are not committed to this repository.](https://github.com/mouse233/unixnu-fuxi/blob/1d071dae4618b0676d313cfbe1fc39689e6f139e/diagnostics/ram-root/usb-bulk.md)
  Command: <code>fastboot boot m1-ab-ep0snapshot-v6; python3 scripts/boot-ram-window-once.py</code>. Revision: `1d071dae4618b0676d313cfbe1fc39689e6f139e`.

</div>
