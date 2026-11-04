# 小米平板 7 / POCO Pad X1（uke）

[Allenwdk/UniXNU-uke](https://github.com/Allenwdk/UniXNU-uke)

<div v-pre>

Uke iPadOS27/24A446 GPU baseline CRC90B6BC701210D9DB: user confirms prior boot, icon/widget loading, Settings and Dock UI-restart symptoms resolved. No instrumented latency, long-run concurrency or repeated-cold-boot cache measurements inferred. See docs/GPU-IOS27.md.

源记录: [porting.toml](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/porting.toml), `fcf9fd3f31be4618a48d33fd7cf161e0da75b573`.

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
- UniXNU-sm7675-common SoC layer and the ipados-27.0.1-24A446 OS profile \(iPad17,3, XNU 12377.121.6, arm64e\).
- 24A446 kernelcache kernelcache.decompressed \(sha256 38e6d9fa...\) as the prelink reference.
- Catalog components with the board's fork pins in feeds.toml.

### 配置

- schema\_version2, sm7675 SoC, ipados-27.0.1-24A446 arm64e, uke kit and uke\_ipados27\_defconfig; GPU enabled.
- Four-layer XNU patch series; current Adreno740/Metal/GOP pins are reachable on the user forks. Workspace-only paths belong in ignored local.toml.

### 操作步骤

- ./unixnu defconfig uke\_ipados27\_defconfig -D ../UniXNU-uke-build
- ./unixnu fetch -D ../UniXNU-uke-build &amp;&amp; ./unixnu status --json -D ../UniXNU-uke-build
- ./unixnu build kernel -D ../UniXNU-uke-build &amp;&amp; ./unixnu build payload -D ../UniXNU-uke-build
- ./unixnu build userdata -D ../UniXNU-uke-build --object OS.vroot=&lt;policy&gt;/manifest.bin

### 开发经验

- The format-1 patch path never applied the shared patches from a cold tree \(the board module shadowed them\); the format-2 series replays the set statelessly.
- Catalog archive recipes equal the board's legacy builder commands; the component aliases keep the old script names working.
- P2 \(gpucomp26\): the compositor's two-plane 'b3a8' frame is scanned by the DPU natively. Plane 0's 4 B/texel colour words \(rows 4\*width apart\) are XRGB2101010, whose SSPP SRC\_FORMAT 0x000276ff is the firmware's own ARGB8888 word 0x000237ff \(unpack 0x03020001\) with alpha bit 8 clear and DX bit 14 set, per the stock dpu\_hw\_sspp\_setup\_format/dpu\_formats.c in the reference kernel; plane 1 is the alpha byte, whose row is the record's stride field. The 34,177,024-byte frame maps only its 27,340,800-byte plane-0 prefix into one slot; the CPU decode remains the fallback when the display-bank window is unavailable.
- gpucomp26 log \(recovery, userdata window, t=16..917 s\): UKE DPU: direct ready fmt=000237ff/000237ff unpack=03020001 tenbit=000276ff; four b3a8 frames mapped by their plane-0 prefix \(direct slot ... bytes=27340800\); UKE DPU: tenbit sample p0=18060180 p0c=37edfb7e alpha=ff/ff -- the alpha plane is 0xFF, so the frame is opaque and the XRGB2101010 word order is the right one. One stall snapshot at t=78.4 s and none after; GPU commit-to-complete still averages 50.9 ms over 8884 commits in 893 s \(about 9.9/s\).
- gpucomp27 ports the upstream display's refresh tick \(GopFramebuffer 33e941a\): startVsync/vsyncTick/armVsync, getRefreshAttributes at slot 301 and setDisplayRefreshProperties in registerService, with the builder binding \_native\_legacy\_vsync\_notify \(0xfffffff005796720\) and \_native\_legacy\_set\_refresh\_properties \(0xfffffff00579ebb8\) after checking the original bytes; board.toml sets sheng-vsync=120 \(armcpu-diagnostics dropped to stay at 987 of 1000 command-line bytes\). The direct path now prints UKE DPU: flip n=... tb=... skip=... fb=... latch=...us max=...us vsync=... every 120 frames and the first eight UKE DPU: skip lines, so the next log separates compositor starvation from display-path loss.

### 完成条件

- Status resolves arch, soc, os and device layers with the intended pins; the output path is out/uke/ipados-27.0.1-24A446/uke\_ipados27/; kernel.macho is MH\_FILESET/arm64e and prelinks against the 24A446 kernelcache.

### 当前范围

- The reported interactive GPU27 symptoms are user-accepted on CRC90B6BC701210D9DB; no broad multi-client stress or cross-cold-boot cache qualification inferred.

### 下一步

- Keep the accepted published pins and current GPU baseline; measure future stress/performance independently.

### 证据

- `host`: [swap-dispatch candidate CRCE989F0CE55D5EB3F: final original setter receives effective request0/1/0/1/1, schema74f2, original prelink gate and inputs preserved; not flashed.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>./unixnu build kernel &amp;&amp; ./unixnu build payload; python3 uke-port/fixes/2026-11-03-swap-dispatch/pack.py</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [display-submit diagnostic built, CRC804CD0D45D379053, original missing2/stubbed24 exact sets unchanged, final snapshot uses24A446 fields and actual source dispatch retains IPC/PAC/results; NOT FLASHED per user request.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>./unixnu build kernel &amp;&amp; ./unixnu build payload; python3 uke-port/fixes/2026-11-03-display-submit/pack.py</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [schema\_version 2 resolves the ipados-27.0.1-24A446 profile with the four-layer patch series; kernel.macho is MH\_FILESET/arm64e \(95,322,112 B, sha256 99a6b970...\)](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/board.toml)
  Command: <code>./unixnu status --json -D ../UniXNU-uke-build &amp;&amp; ./unixnu build kernel -D ../UniXNU-uke-build</code>. Revision: `a8da9009d43f6c679ebd46903810906afa8ce906`.
- `source`: [the active 27 track: CONFIG\_XNU\_BUILD\_ARCHIVES=y, CHAINED\_FIXUPS=y, native display backend, source storage with the OS root policy, NATIVE\_ADRENO off.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/configs/uke_ipados27_defconfig)
- `source`: [the device's xnu-12377 entries: Darwin 26 posix\_spawn attrs, ptrauth null portability, 4K stack shift and the source-storage runtime hook.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/patches/xnu-12377/series)

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
- 2026-11-02 source review: live ABL initrd 0xB2D51000..0xB7FFF41C overlaps the former DXE Heap 0xA8000000..0xC3A00000; sheng 66421cb reserves 0xA8000000..0xB8000000. Candidate reserves the handoff before SEC/DXE and starts the heap at 0xBAB00000; built; four partitions flashed and rebooted at 2026-11-02 01:38, user photo confirms kernel fold C43F1F3EC8168A4C and six tail samples, WINDOW delta=0 and overlap=0; later MMU/kernel execution unresolved.

### 完成条件

- The FD builds, the menu boots the payload entry, and the device reaches the XNU entry point.

### 当前范围

- Paired compressed-payload boot/vendor\_boot reached the user-accepted 24A446 GPU system. Other devices, suspend/resume and long repeated-boot stress are not qualified by this report.

### 下一步

- Use the paired UEFI decompression-capable boot and compressed vendor\_boot; preserve raw FAT fallback and runtime overlap checks.

### 证据

- `device`: [the firmware menu and the uke boot entry run on hardware through the bring-up images](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>fastboot boot boot.img</code>. Revision: `c77d613dc91fb54479242aa5d5902c48662b80d7`.
- `host`: [SILICIUM\_UEFI.fd builds 3,145,728 bytes with the board defines](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/board.toml)
  Command: <code>./unixnu build firmware --skip-preflight --uefi ../uefi-uke -D ../UniXNU-uke-format2</code>. Revision: `4f4bf7e1f4ad56743562777becd7ac7d6714216c`.
- `host`: [initrd-lifetime candidate on UEFI 1e2d12d plus uncommitted reservation/diagnostic changes: 42 DTS reservations, 77 descriptors, zero static errors; FD e4720db0 and boot db8a7d0b build successfully; not flashed](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>./unixnu build firmware -j 32 &amp;&amp; ./unixnu bootimg --ramdisk none -j 32</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [2026-11-02 01:38 authorized flash: product uke; boot db8a7d0b and vendor\_boot ef0635db written to both slots, all OKAY; active slot a confirmed; reboot OKAY; panel and kernel validation pending](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>fastboot -s b8a81f12 flash boot_a BOOT &amp;&amp; fastboot -s b8a81f12 flash vendor_boot_a VENDOR_BOOT &amp;&amp; fastboot -s b8a81f12 flash boot_b BOOT &amp;&amp; fastboot -s b8a81f12 flash vendor_boot_b VENDOR_BOOT &amp;&amp; fastboot -s b8a81f12 set_active a &amp;&amp; fastboot -s b8a81f12 getvar current-slot &amp;&amp; fastboot -s b8a81f12 reboot</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `device`: [2026-11-02 user photo IMG\_20261102\_013913: fold C43F1F3EC8168A4C and all six E1/E2 samples match, 95354880 bytes, WINDOW delta=0, BAD n=0, IMAGE overlap=0; initrd B1F51000..B7FFF4E8. Image-load-integrity gate passed; three bands alone do not prove post-MMU execution. Not Found is unrelated ConIn/key discovery.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>Compare user photo IMG_20261102_013913 against release payload-inspection.json and DarwinBoot address diagnostics</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `device`: [2026-11-02 stage3-reset \(vendor\_boot 2da67ff5\) flashed to four partitions at 02:07, slot A confirmed; user reports expected automatic reboot. Post-MMU checkpoint at fffffff00af14438 and timer/PSCI path passed; configured delay 6 seconds not instrumented; later arm\_init unverified.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>Authorized four-partition stage3-reset flash and compare user observation with probe-check.json</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [after-sif-reset candidate built, not flashed: BL \_static\_if\_init at fffffff00b62d98c redirected to verified 72-byte cave fffffff00af12620; old stage3 site restored. Vendor\_boot 0d339c62, complete kernel 115ec427, fold 1CEEAB8FEE60E2B8; board inputs restored.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>./unixnu build payload -j 32 with temporary entry_probe_reset_after=_static_if_init; verify final FAT kernel and call-site bytes</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `device`: [2026-11-02 02:22 after-sif-reset \(vendor\_boot 0d339c62, full kernel 115ec427\) flashed to both slots, A confirmed, reboot successful; user confirms automatic reset. \_static\_if\_init returned in \_arm\_init, covering prior TCR and slide/sign execution; deliberate reset precedes arm\_vm\_init and normal video console.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>Authorized four-partition after-sif-reset flash; correlate user automatic-reboot report with verified probe-check.json</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [after-vm-reset built, not flashed: \_arm\_vm\_init call fffffff00b62dce4 redirects to verified 72-byte cave fffffff00af12620; earlier stage3/static\_if sites restored and board restored byte-for-byte. Vendor\_boot 9efd154b, full kernel 23f7dd16, fold 5F24568B8CC3C9A9.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>./unixnu build payload -j 32 with temporary entry_probe_reset_after=_arm_vm_init; verify final FAT kernel and probe bytes</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [Release uke-port/releases/2026-11-02-ipados27-stage-ring: no-reset candidate host-built/prelinked from the 5ed4642 working-tree baseline; 6x96 B static ring drawn after framebuffer-console init. Reconstructed payload kernel 95,354,880 B sha256 6ff1317813160de0d92359e8069ebfa1b15cbce9fd4300095521db90677da310; post-MMU reset instruction and \_arm\_vm\_init call preserved. Not flashed/device-tested; see release stage-ring-check.json.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>./unixnu build kernel -j 32 &amp;&amp; ./unixnu build payload -j 32 &amp;&amp; ./unixnu bootimg --ramdisk none; patch-vendor-boot.py; extract and verify both kernel FAT extents</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [2026-11-02 11:57:38 authorized stage-ring flash: product uke, serial b8a81f12; boot db8a7d0b and vendor\_boot 110cf296 written to boot\_a/vendor\_boot\_a/boot\_b/vendor\_boot\_b, all OKAY. Active slot a read back and reboot OKAY. Panel/VM behavior not yet validated; release flash-20261102-115736.log and flash-result-20261102-115736.json retain command results.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>fastboot -s b8a81f12 flash boot_a BOOT &amp;&amp; fastboot -s b8a81f12 flash vendor_boot_a VENDOR_BOOT &amp;&amp; fastboot -s b8a81f12 flash boot_b BOOT &amp;&amp; fastboot -s b8a81f12 flash vendor_boot_b VENDOR_BOOT &amp;&amp; fastboot -s b8a81f12 set_active a &amp;&amp; fastboot -s b8a81f12 getvar current-slot &amp;&amp; fastboot -s b8a81f12 reboot</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `device`: [2026-11-02 IMG\_20261102\_120008: three entry bands remain, no new stage text, user reports stuck. Photo fold CB0692A4D2AED5C3 matches host FAT-chain reconstruction of stage-ring kernel 6ff13178 \(95354880 B\); WINDOW delta=0, BAD n=0. No additional execution checkpoint established. Source review: PE\_current\_console returns physical PE\_state.video, while mapped framebuffer is video\_console vinfo.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>Inspect original photo; inspect-payload.py vendor_boot_uke_ipados27_stage_ring.img --offset 4096; compare PE_current_console and initialize_screen</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [2026-11-02 live-vm diagnostic: kernel, fileset prelink, payload, bootimg and vendor\_boot builds pass. Source kernel 6fc74492, final FAT kernel 4409cead \(95371264 B\), expected fold EC568E478C79365A; vendor\_boot f71844a5, boot db8a7d0b. Actual target 4K/T1SZ\_BOOT=26 macros, mapper/renderer ASan/UBSan tests, 12 final code bodies, 48 stage labels and ordered startup/VM/console calls verified. Apple-target semicolon assembly defect was caught before flash, fixed, and final AT/ISB/MRS PAR plus DSB/TLBI/DSB/ISB sequences verified. noconsole=0, no-reset; hardware live output unverified, not flashed.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>check-live-stages.py; ./unixnu build kernel -j 32; ./unixnu build payload -j 32; ./unixnu bootimg --ramdisk none -j 32; patch-vendor-boot.py; inspect-payload.py; verify-release.py</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [2026-11-02 13:43:24..13:43:27 authorized live-vm flash: serial b8a81f12, product uke, partition sizes 96 MiB, release SHA256SUMS all pass. boot db8a7d0b and vendor\_boot f71844a5 written to boot\_a/vendor\_boot\_a/boot\_b/vendor\_boot\_b, all OKAY; active slot a read back and reboot OKAY. No userdata write; no automatic reset probe. Kernel/panel behavior pending. Evidence: live-vm release flash-20261102-134324.log and flash-result-20261102-134324.json.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>fastboot -s b8a81f12 flash boot_a BOOT; flash vendor_boot_a VENDOR_BOOT; flash boot_b BOOT; flash vendor_boot_b VENDOR_BOOT; set_active a; getvar current-slot; reboot</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `device`: [2026-11-02 IMG\_20261102\_134519: live-vm kernel 4409cead, CRC EC568E478C79365A, bytes 5AF4000, WINDOW delta=0, BAD n=0. Visible numbered rows 13,14,15,16,11,12 establish early high-VA framebuffer alias/live rendering and kernel\_startup\_bootstrap return. Highest 16 CPU processor bootstrap enter brackets timer\_call\_init, cpu\_init and processor\_bootstrap; single helper and final TTBR1/VM remain unverified. Original photo SHA256 1f2f2785d91465344fe96467013309edd627b7c6210116288cd13d227a79e9b6; release device-observation.json.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>Compare original user photo and payload-inspection.json; inspect checkpoint patch interval and final _arm_init call order</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [2026-11-02 cpu-bootstrap finer diagnostic built/prelinked/packaged, not flashed. Splits timer\_call\_init/cpu\_init/processor\_bootstrap and timer longterm/abstime, CPU ID/cache/debug, AMP pset and master processor locks. Verified mapper/renderer unchanged from device-tested live-vm. Actual preprocessor 97 active labels in final payload, 16 code bodies preserved, three original calls ordered, AT/ISB/PAR and DSB/TLBI complete, no reset. boot db8a7d0b, vendor\_boot 60f89243, source kernel c5d12261, final kernel 502586b1 \(95371264 B\), expected CRC 8746BA27C34E1E6A. Evidence release cpu-bootstrap-check.json and cpu-call-order.json.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>Six-file patch dry-run; ./unixnu build kernel -j 32; ./unixnu build payload -j 32; patch-vendor-boot.py; actual target compiler preprocessing; inspect-payload.py; verify-release.py</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [2026-11-02 CPU bootstrap photo max 43 at AMP psets entry; final prior payload ADT lacks cluster-type on all 8 CPUs, actual \_\_ARM\_AMP\_\_/CONFIG\_SCHED\_EDGE=1, source defaults to SMP and AMP classifier rejects that value \(panic string not captured\). Payload-only candidate adds E to CPU0..2 and P to CPU3..7 per stock CPU domains and sheng DTS; final ADT diff is 8 cluster-type fields plus normal random-seed only, other payload files and 95,371,264-byte kernel unchanged, CRC 8746BA27C34E1E6A. Candidate flashed at 2026-11-02 14:28:41..14:28:44 with user authorization: all four partitions OKAY, slot a confirmed, reboot OKAY. Await whether checkpoints 43/44 return; hardware root-cause fix not confirmed.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>inspect-payload.py; parse final FAT/ADT; verify-cluster-payload.py; porting-record.py check</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `device`: [2026-11-02 14:28:41..14:28:44 authorized AMP cluster-type payload fix flash: serial b8a81f12/product uke; boot db8a7d0b and vendor\_boot 9fcf4a5e written to boot\_a/vendor\_boot\_a/boot\_b/vendor\_boot\_b, all OKAY; active a read back, reboot OKAY; no userdata. Kernel unchanged 502586b1, expected fold 8746BA27C34E1E6A. Whether pset 43/44 passes is pending; fix not yet device-verified.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>fastboot -s b8a81f12 flash boot_a BOOT; flash vendor_boot_a VENDOR_BOOT; flash boot_b BOOT; flash vendor_boot_b VENDOR_BOOT; set_active a; getvar current-slot; reboot</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `device`: [2026-11-02 user approximate transcription after amp-cluster flash: screen refreshed, unmapped-call from 0xfffffff009019bd8 x0 fffffff00ba64230 x1 fffffff00751b025. No new photo. Host final image decodes x0 as com.apple.security.AppleImage4, x1 prefix com.apple.security.; LR-4 BL -&gt; thunk 0xfffffff00903a908 -&gt; original slot 0xfffffe00080e1a78 -&gt; original function 0xfffffe000ae8254c. This is not the function at the printed LR itself. Boot remains incomplete.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>Compare user report with exact amp-cluster kernel, caller/thunk code and chained fixups</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [Resolved active XnuPrelink kit 9cfa5f5 plus uncommitted one-anchor fixture change: strprefix original 40 B \(BTI + exact native 36-byte body\), sha256 8af8e336c9f47462aa6495b0238ecdb9e747287fde579fe65723b2f531389515. 59 tests pass; formal prelink/payload/vendor\_boot pass. Final 3 slots rebound from panic stub to fffffff00aecb7fc with PAC metadata retained, caller/thunk unchanged; E/P ADT and all 97 checkpoints retained. image4-strprefix vendor\_boot 70cb4c88/final kernel 7be51b1e/CRC 485AB76E1D008C12. Host verified, not flashed; later unrelated unresolved functions remain possible.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>identify.py; unittest discover; ./unixnu build prelink -j 32; ./unixnu build payload -j 32; verify-release.py; verify-binding.py</code>. Revision: `9cfa5f5e9b47eef102b80ad4be83692b4a3fe76b`.
- `source`: [2026-11-02 fetched upstream sheng 6a3d35c/core 04573c5/kit 2b39ff7; all 8 sheng XNU12377 patches identical to uke. Local DEVELOPMENT/no-LTO reference differs from upstream RELEASE-LTO; missing upstream 25 function anchors and 19 data anchors, N\_ABS original-stub relocation and regression policy. Flashed report missing 569 sites/stubbed 2501 vs policy 2/24 \(configs differ\). New user LR 0xfffffff009023d34 -&gt; original 0xfffffe000ad3e380 typed allocation for AppleImage4 nonce\_magazine. Root/userland not verified. Audit only, no new bindings, merge, build or flash.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>git fetch origin main in three repos; audit-upstream.py; inspect-next-panic.py; compare prelink JSON to upstream regression policy</code>. Revision: `6a3d35c02504b712897799c5481952a61761325d`.
- `host`: [2026-11-02 real Linux RELEASE/LTO and BTI rebuilt; native SHA256 1cb970866c9b25a0dc011cd58c5080cb0672c7b2c900cda8e40a3fcdf87927e5. Matcher v9 host regressions 66 pass. Missing data references 2 \(upstream policy\), stubbed 498; candidate 09b3adb4c4b36507fa96dea08278aa5d94c65b698795fadf68ddb1e810c98522 rejected by unchanged upstream regression policy. No payload or device flash. Detailed evidence in workspace uke-port/fixes/2026-11-02-prelink-linux-audit/progress-audit.json.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>./unixnu build kernel; python3 -m unittest discover -s kits/XnuPrelink -p test_*.py; ./unixnu build prelink</code>. Revision: `616c268da41c4608d233aee53f239ab99b7cbb36`.
- `host`: [2026-11-02 18:48 current matcher v9: 68 host regressions pass; reviewed fixture 182 functions/30 data, 264 original branches \(205 display/51 HID/8 IOSurface; GPU excluded\). Final missing 2 sites matches policy; stubbed 116 sites includes 92 excess references across 67 targets. Formal prelink exits 1; rejected candidate 6655a921757701f9ffd3fea009395ad3c2e48e4966a40f9facb43dbd041160de. Prior panic strprefix and kalloc\_type\_impl\_external resolve in final map. No payload or device flash.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>./unixnu build prelink; python3 -m unittest discover -s kits/XnuPrelink -p test_*.py; record-current.py</code>. Revision: `616c268da41c4608d233aee53f239ab99b7cbb36`.
- `host`: [2026-11-02 fixed-input upstream controls: native 7014bb4a/reference 91760a0d unchanged; pure upstream matcher/fixture missing 15, stubbed 904 versus current 2/116. IOEventSource gate source/PAC/offset cross-check shows 48 B Apple versus 44 B Linux register-allocation difference. Mac RELEASE/LTO input archive SHA256 ba82b51472be56d3c3d8ad6fd7d69664d2edfb66e5e8afc87596345f00a01a1e, 13590 file hashes verified; Mac execution unverified. No new fixture, runtime edit, payload or flash. Evidence in workspace upstream-reference-investigation/matrix-summary.json and compiler-difference.json.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>fileset_match.py fixed-input matrix; emit-audit.py; verify-inputs.py; bash -n run-macos.sh</code>. Revision: `2b39ff73dc4d49ad64e349c711ca4aa8d1dd64ea`.
- `host`: [2026-11-02 authorized GitHub Actions reference-only control: run 41448047750, commit 9935f291c01188d8496a0de76c361f9403aa03d4 on isolated research branch; one workflow file pushed. Draft input release has 143 verified transfer chunks totaling 37459394 bytes, original SHA256 ba82b51472be56d3c3d8ad6fd7d69664d2edfb66e5e8afc87596345f00a01a1e. Download/input hash/Apple toolchain steps pass; RELEASE LTO build in progress. No native code or firmware pushed/flashed.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>git push isolated research branch; gh run view 41448047750</code>. Revision: `9935f291c01188d8496a0de76c361f9403aa03d4`.
- `host`: [2026-11-02 upstream reference closure: Actions 41449626495 produces Apple clang 21/Xcode 26.6 RELEASE LTO reference with XNU\_KERNEL\_CHAINED\_FIXUPS=1, SHA256 2f9eabe43241bb9b64d367151d79d660e81e3ec7fee8399c3f37a0f5ba3b5aa8. Formal prelink exits 0, missing 2/stubbed 24 exactly match original policy. Supplemental 39 function/4 data anchors and v9 heuristics removed; strict C++ owner guard retained and changes no bindings or kernel bytes. Native 7014bb4a unchanged. 63 tests pass. Final release vendor\_boot d7f323e93508c4927698fa8916a948a1aa4a7af2d48480ab217577fae63c2c68, final kernel 7b7f78876665aae5d3d8dcc85eafca7d82d24042de1905b8c0ec90812046b75c, 95387648 B, CRC 0779B5A679B2FF5F. FAT/16 code bodies/97 labels/264 adapter branches/3 strprefix+2 kalloc+13 bool PAC slots/E-P ADT/trustcache and seed checks pass. Not flashed.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>./unixnu build prelink -j 8; ./unixnu build payload -j 8; unittest discover; release verify-release.py and verify-bindings.py</code>. Revision: `9141d399ea853b693433613eacf725c0e81dd69d`.
- `device`: [Authorized upstream-reference four-partition flash 2026-11-02T21:38:03+08:00..2026-11-02T21:38:12+08:00: serial b8a81f12, recovery/product uke, SHA256SUMS pass, boot\_a/vendor\_boot\_a/boot\_b/vendor\_boot\_b all OKAY, active a read back, reboot OKAY. boot db8a7d0b/vendor\_boot d7f323e9/final kernel 7b7f7887, expected CRC 0779B5A679B2FF5F. No userdata write. Kernel/GUI boot unverified; evidence release flash-result-20261102-213803.json.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>adb reboot bootloader; fastboot flash four boot/vendor_boot partitions; set_active a; getvar current-slot; reboot</code>. Revision: `9141d399ea853b693433613eacf725c0e81dd69d`.
- `device`: [IMG\_20261102\_213856 photo SHA256 b4f242fb1e77f09983e35617ede15107f76f857dd6a89cb09e1c4c87dc24799a: upstream-reference kernel 7b7f7887 reached IOService dispatch; IA PAC failure at PC fffffff00b464858/LR fffffff00b4635c4, ESR 72000000. x8 truncated by photo edge. No root/launchd/desktop pass.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>Symbolize the exact final flashed kernel and compare prelink-native call; inspect user photo</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [iig-pac candidate: native 1a234525, prelink 4b7c2959, final 6229de56/vendor\_boot 7b3bd88f, CRC 008FDA414816627C. Linux portable IIG PAC cast corrected; old QEMU conversion faults EC=1c, corrected returns 0; non-PAC assembly unchanged. Final direct call fffffff00b4644e0 -&gt; fffffff00b55f994; failure handler retained. 63 kit tests, original missing2/stubbed24 policy, check-unixnu, 13 areas, full-panel/text renderer and final FAT/PAC/AMP checks pass. Not flashed.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>./unixnu build kernel -j 8; ./unixnu build payload -j 8; check-member-cast-runtime.py; check-xnu-panic-screen.py; verify-release.py; verify-bindings.py</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [Authorized flash 2026-11-02T22:41:35+08:00 to 2026-11-02T22:41:39+08:00: recovery b8a81f12/uke, six SHA256SUMS checked, fastboot product uke and four 96 MiB partitions checked. boot db8a7d0b/vendor\_boot 7b3bd88f written to boot\_a/vendor\_boot\_a/boot\_b/vendor\_boot\_b, all OKAY. Active a read back; reboot OKAY; no userdata write. Final kernel 6229de56, expected CRC 008FDA414816627C. No hardware boot/PAC/root/launchd/desktop result yet. Log flash-20261102-224135.log and matching result JSON in iig-pac release.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>adb -s b8a81f12 reboot bootloader; fastboot flash boot_a/vendor_boot_a/boot_b/vendor_boot_b; set_active a; getvar current-slot; reboot</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `device`: [User transcription after 22:41 iig-pac: SourceStorage UFS start failed, root step3: root windows require distinct OS and SystemOS, SourceStorage.cpp:99. No fresh photo/CRC. Actual source order implies policy auth, family/APFS load, UFS hostBringUp and findRootLayout returned success with manifestStatus0. No root mount/launchd/desktop.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>Compare user transcription with pinned ShengUfs 78c93b0 NativeUfs::startRoot and RootPublication.h</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [Dual-root candidate unflashed: vendor\_boot c0c432631fc24fe74a82e172662e2e4360c741a5fd5bdad6d3932d63c5fc0cf0, final kernel 9c7339e5cbbdc6e3abf32ec0b26a6f6c79639513c60b76f783a901d0b3f4a7ab, CRC 6C8EF01FE60D264E; userdata 994f182477966ae3d84d808f1e4839d548cfdb7e0d75aad90c3ee6ba2e8a2b82, 15753805824 bytes. Two windows and two vroot tables fully reread against profile; SystemOS 1468928 blocks C-verified with same owner anchor, checksum-valid APFS UUID. Two signed headers in final FAT VROOTB01 1152B. Missing2/stubbed24 unchanged; 63 kit and 3 userdata regressions plus actual RootPublication tests pass. Btrfs EIO handled with scratch tmpfs decode and bounded fsync persistence; no filesystem-wide repair.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>./unixnu build kernel; build payload; build userdata with OS.vroot and SystemOS.vroot; verify-root-layout.py; verify-release.py; verify-bindings.py</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [Authorized dual-root write 2026-11-02T23:41:10+08:00 to 2026-11-02T23:42:36+08:00: recovery b8a81f12/uke, seven image hashes checked. Unmounted sda32 241617055744 bytes, start 23691264 and size 471908312 512B sectors. Backed up first1MiB manifest. dd seek=0, count\_bytes=15753805824, notrunc/fsync; full device readback 994f182477966ae3d84d808f1e4839d548cfdb7e0d75aad90c3ee6ba2e8a2b82. Boundary/reserve/tail samples unchanged; no userdata erase or writes beyond prefix. Four boot/vendor\_boot flash operations all OKAY, current-slot a read back, reboot OKAY. CRC 6C8EF01FE60D264E; actual OS boot unverified. See flash-result-20261102-234110.json and backup/log in systemos-root release.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>adb recovery bounded dd prefix with seek=0; complete prefix readback SHA256; adb reboot bootloader; fastboot four partitions; set_active a; getvar current-slot; reboot</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `device`: [User reports systemos-root: SourceStorage UFS start failed root step3 root window preparation failed, SourceStorage.app:99 \(actual source cpp\). No new photo. Passed manifest, distinct OS/SystemOS plan and root IOService start; failed allocation/init/configure/attach Prepare before Identity/Schedule. Exact first device substep unproven.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>Compare user transcription with exact flashed NativeUfs control flow</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [Confirmed vroot objects wrong: old full OS manifest 75104800 vs raw table75104256; SystemOS47006240 vs47005696. Both extra544B. Production readPolicyTable rejects old objects, reads corrected raw tables; actual C vr\_open returns0 for both after signed-header reconstruction. 5 userdata tests and actual old CLI rejection pass. Unflashed candidate vendor\_boot 286bd6d900c2f85df319f500ec713c5aa41b244b56fd6137ba9b64b4e8fb075d, userdata 981110dacccc9ee7fc6778b2b13a83473856665770aea929edf933b499677694; kernel/final bytes identical to flashed9c7339e5, CRC6C8EF01FE60D264E, only boot arg native-ufs-diagnostics1 added \(791B\). Three aligned patches122122240B virtually reproduce complete rebuilt userdata SHA; OS/SystemOS unchanged.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>./unixnu build userdata --object OS.vroot=manifest.bin:544 --object SystemOS.vroot=manifest.bin:544; build payload; check-consumer.py; make-delta.py; final FAT/ADT/binding gates</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [Authorized vroot-tables delta/flash 2026-11-03T00:00:33+08:00 to 2026-11-03T00:00:44+08:00: stock four-partition/reboot recovery command all OKAY. Recovery b8a81f12/uke, userdata unmounted241617055744B geometry verified. Before SHA/backup all3 passed. OS.vroot seek3816192 count18337, SystemOS.vroot seek3834624 count11477, manifest seek0 count1 \(bs4096\), conv notrunc/fsync; after hashes cfb16d73/48fe5a70/ebf57107 matched. Total122122240B, no erase; boundary/tail samples unchanged. Diagnostic boot/vendor\_boot4 allOKAY, activea read back, rebootOKAY. vendor\_boot286bd6d9, kernel9c7339e5, CRC6C8EF01FE60D264E, diagnostics1. No boot outcome yet. See flash-result-20261103-000033.json/log and preflash backup.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>user stock4/reboot recovery command; recovery bounded dd with seek plus fsync/readback; adb reboot bootloader; diagnostic4 flash; active a; reboot</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `device`: [IMG\_20261103\_000158 photo SHA7bec7d323768e5114b8e614597af72011ab7f2d421955d8e1aed090f82b3b276: machine\_routines.c3379 unsafe\_kernel\_text\_initialized assertion. PC fffffff00af1f194=ml\_unsafe\_kernel\_text+2c; LR fffffff00af4e73c=dtrace\_sdt\_probes\_restricted+10. ESR truncated to0x, no inferred value. Final SourceStorage call precedes pseudo\_init SDT slot, so synchronous Prepare/auth return inferred, not media/root mount qualification.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>Symbolize exact flashed final9c7339e5, parse final ADT and signed pseudo_init function pointer</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [Unflashed CTRR ADT-only candidate vendor\_boot 6d646b3634dd042d34c042e81b6f64965b71eab001b88a9e6a16448a2455400a; kernel/source identical, final9c7339e5/CRC6C8EF01FE60D264E. Added chosen kernel-ctrr-to-be-enabled4B u32=0; only other ADT change fresh random seed. Real XNU initializer four-case fixture validates missing/wrong width/unprotected/protected inputs. Assertion/PAC code and signed policy bundle/args/trustcache/Data seed unchanged. Final FAT/AMP/97 labels/264 branches checks pass. No userdata write required.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>./unixnu build payload -j8; check-init.py; verify-adt.py; verify-release.py; verify-bindings.py</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [Authorized CTRR ADT flash 2026-11-03T00:13:01+08:00 to 2026-11-03T00:13:05+08:00: fastboot b8a81f12 productuke/is-userspaceno; six SHA256SUMS checked, all four partitions0x6000000. bootdb8a7d0b/vendor\_boot6d646b36 flashed boot\_a/vendor\_boot\_a/boot\_b/vendor\_boot\_b allOKAY, activea readback, rebootOKAY. No userdata write; preserves prior pure-hash delta. Final kernel9c7339e5/CRC6C8EF01FE60D264E; chosen.kernel-ctrr-to-be-enabled4B u32=0. No new boot outcome. Evidence flash-result-20261103-001301.json and matchinglog.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>fastboot serial/product/partition checks; flash four boot/vendor_boot partitions; set_active a; getvar current-slot; reboot</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `device`: [Photo IMG\_20261103\_001417 SHA7a86e606fd76c6280f9ed5d43ac7fe8c9f84a7b6ebec5d21819af941cd47edcd: Ticket spinlock timeout, lock\_ticket.c398; visible ownerCPU4/thread fffffff75f4c30a8, start1221987748 now1222000546 timeout12000 irqtime0. First line overlaps, exact lock/ticket fields/call chain unreadable; no root/launchd result. User requests removal of initial wait.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>Inspect exact photo and flashed final9c7339e5 plus actual lock timeout source</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [Unflashed panic-owner-nowait: boot eada61328aebb0aab5e86f01cc3528a4025445e93c7f08a592be7b89889346dd, vendor\_boot 5f647fd8a54ac3b80840acb5eaaa0c6904f3ce8a0c88353c206845c425efc343, final f67f57f03024597c82f8aca3f894f541b4e60a3e30cbb4ea5bf97220f5664b8e, CRCC9630ACDF7253040. Removed DarwinBoot15s Stall; final FD LZMA extraction/PE Boot noStall and final boot gzip FD/shim/FDT verified. Atomic LDXR/STXR owner before clear plus STLR shadow length; old2CPU negative control failed/newpassed. Four QEMU cases match final2683B renderer including six highVA frame links; 3padding variants checked. Source kernel unchanged; final changes only diagnostic padding/4branches and correctly resealed32B POST HMAC. FAT97labels/264branches/PAC/AMP/CTRR/noreset pass. No userdata update, no hardware lock fix claimed.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>./unixnu build firmware; build payload; bootimg --ramdisk none; check-xnu-panic-screen.py basic/strings/race/frame controls; verify-final.py; final FAT/boot validations</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [Authorized panic-owner-nowait flash 2026-11-03T01:20:47+08:00 to 2026-11-03T01:20:50+08:00: fastboot b8a81f12 productuke/is-userspaceno; six SHA256SUMS and four0x6000000 sizes checked. booteada6132/vendor\_boot5f647fd8 flashed boot\_a/vendor\_boot\_a/boot\_b/vendor\_boot\_b allOKAY, activea readback/rebootOKAY. No userdata write; purehash delta preserved. Final kernelf67f57f0/CRC C9630ACDF7253040. No real wait-removal/panic-race/BT/lock/root/launchd result yet. Evidence flash-result-20261103-012047.json/log.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>fastboot identity/partition checks; four boot/vendor_boot flashes; set_active a; getvar current-slot; reboot</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `device`: [IMG\_20261103\_012307 SHA0db799f964289339f4abd3271d592682a1b6e7707833e2ecb08c76225883b8a3: no visible text overlap, 6BT entries. Lock fffffff00b967008 exactlyvcputc\_lock, ownerCPU4/threadfffffff3e10b8398, tickets e1/e3 waitinge2, 12765ticks/threshold12000, irqtime0, lock\_ticket.c398. Return-4 symbols show \_\_doprnt-&gt;vcputc\_options-&gt;ticket waits-&gt;timeout. HolderPC/cause and root/launchd not proven; 15s speedup not separately confirmed.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>Symbolize exact flashedf67f57f0, canonicalize rawPAC LRs and inspect callsites return-4</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [Unflashed graphics-console payload: vendor\_boot 923561306b4f0536fbf02867eb89667b341305ddb46c67f1e148ff311010733b, kernelf67f57f0/CRC C9630ACDF7253040. Removes only local -uketextconsole, all other args775B/kernel/source/boot/no15sFD/PAC/BT/policy/seed/userdata unchanged; final FAT only config and randomseed changed. Actual vcattach-prefix/vcputc controls show missing flag keeps graphics and no text-lock acquisition. Actual timeout controls reproduce IRQ-off/PANIC12000 clamp vs normal3000000, also present in final machine code. Final FAT97labels/264branches/PAC/AMP/CTRR/noreset pass. Hardware console isolation and root/launchd pending.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>./unixnu build payload; check-controls.py; verify-candidate.py; verify-release.py; verify-bindings.py</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [Authorized graphics-console flash 2026-11-03T01:33:45+08:00 to 2026-11-03T01:33:49+08:00: fastboot b8a81f12 productuke/is-userspaceno; six image hashes and four0x6000000 sizes passed. booteada6132/vendor\_boot92356130 flashed boot\_a/vendor\_boot\_a/boot\_b/vendor\_boot\_b allOKAY, setactivea/current-slota/rebootOKAY. No userdata write. Kernelf67f57f0/CRC C9630ACDF7253040; only -uketextconsole removed, other775B args/kernel/no15sFD/panicBT unchanged. Actual lock/root/launchd/desktop outcome pending. Evidence flash-result-20261103-013345.json and matchinglog.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>fastboot identity/partition checks; four boot/vendor_boot flashes; set_active a; getvar current-slot; reboot</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `device`: [Photo IMG\_20261103\_013449 SHA9929dd2bc69e05e70ee2f558c2155edb2a7009df3cfddee83470cb2f3c542e0d: unexpected SIGKILL launchd namespace9/code8 descriptionnone; BT bsdinit\_task/load\_init\_program/load\_init\_program\_at\_path/\_\_mac\_execve/process\_signature/psignal\_internal. Mounted-root executable loading/exec attempt reached and prior vcputc stop passed; launchd not normally running, SystemOS/Data mounts not separately proven. Specific refusing hook/errno unknown.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>Read photo and symbolize exact flashed finalf67f57f0, reason.h EXEC9/SECURITY_POLICY8</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [Unflashed target-trust payload vendor\_boot 2e5e5f4f7a63bec4356503ba4aa3520a2145b5e38e30af90b9e9f23b442d26bd, final f67f57f0/CRC C9630ACDF7253040 unchanged. Prior bundle037c77a1 contains3owner hashes and exact21H461 staticda88460e/Systemd121ba89 modules; target launchd3d2ccf3da81ca5ac44d8f073b9bcb81147ecf8e2 absent, present in24A446 static. Original launchd150codepages match; two target IM4Ps byte-match localIPSW and BuildManifestSHA384. Bundle dc655bcb copies original raw04bdc992\(3547\)/599a9c9d\(130\) unchanged, no ownhashes. Boardpin rejects wrong old normaltrust; actual loader tests and finalFAT bundle compare pass. Onlytrust and randomseed differ; all kernel/boot/args/Data/userdata and AMFI/MAC checks preserved. Causality/acceptance still requires hardware.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>bundle-ipsw-trust.py original24A446 caches; audit-launchd-trust.py; check-loader-trust.py; ./unixnu build payload; final FAT/binding gates</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [Authorized target-trust flash 2026-11-03T01:48:32+08:00 to 2026-11-03T01:48:35+08:00: fastbootb8a81f12 productuke/is-userspaceno; seven image hashes/four0x6000000 sizes verified. booteada6132/vendor\_boot2e5e5f4f flashed boot\_a/vendor\_boot\_a/boot\_b/vendor\_boot\_b allOKAY, activea/readback/rebootOKAY. No userdata write. Kernelf67f57f0/CRC C9630ACDF7253040; bundle dc655bcb original24A446 static3547/System130. Actual policy9/8/launchd/desktop outcome stillpending. Evidence flash-result-20261103-014832.json/log.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>fastboot identity/partition checks; four boot/vendor_boot flashes; set_active a; getvar current-slot; reboot</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `device`: [User reports CRC loader text remains visible after current boot; ordinary kernel progress unavailable. No fresh panic/user-mode success evidence. Source review distinguishes DarwinBoot DiagDraw from XNU vcputc\_lock; graphics gating can leave old pixels while kernel proceeds. Removing loader text alone cannot fix kernel text contention. No new build or flash this round.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>Review user report and active DarwinBoot Boot, XNU vcputc_options and PE_init_kprintf</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [Deferred kprintf host negative/control tests and formal kernel/payload/boot pass; final21bf53d889ea099de0e5bc9ee6ffddbbd20ee5dcd0af1e3cb02cb7413512d127/CRCA39DA0801DCB37ED, vendor\_boot5b78fef11eef85a27ed4d0fae8b05f64e0114dc158508160ababe5d4a15185d3. Existing console\_ring trylock, busy/full screen drops counted, os\_log remains; ONCE/EARLY\_BOOT background drain. Actual PAC callback, unlock/IRQ-restore-before-wakeup, STARTUP4/18, POST HMAC, FAT trust/root/Data, 264 branches and original missing2/stubbed24 pass. QEMU race/6frames renderer bytes match final. Mapping/timeouts/AMFI/MAC unchanged; canonical replay removed cache-only old panic replay. Authorized flash 2026-11-03T02:32:28.564166+08:00 all fourOKAY, activea/readback/rebootOKAY; sixSHA/four96MiB checked. No userdata; hardware logging/launchd/desktop pending.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>./unixnu build kernel; build payload; bootimg --ramdisk none; check-deferred.py; verify-console.py; four-partition authorized fastboot flash</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `device`: [IMG\_20261103\_023334 SHA36588cf8ff8ef8aa768ecc4c18cc43d1968cd4a5a542523d6421356f401c7a71: flashedfinal21bf53d8 root disk5s1 mount-complete and pid1 Darwin Ignition/libignition64 arguments level5/forceroot0/haltnone. Subsequent TCH heartbeats continue and user reports touch normal; no new panic reported. Confirms prior EXEC9/8 stop passed and visible logging progressed; does not prove LC\_MAIN/desktop or SystemOS graft/Data mount. Photo does not include loaderCRC.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>Inspect user photo, compare actual24A446 dyld call order and flashed kernel</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [Unflashed ignition-trace vendor\_bootb88e11147cf57fcb953fcf8a579b72890a0109aecbfff8afd80b8fc23fa21f7d/finald8a0ee8b4474866207215fe41c003aed3039c9f7672b4450d7144b9bb77f6b97/CRC21B43B437E708095, args832B. TCH IOLog max10s and firstHIDstate fix, acquisition/publication unchanged. PID1 ignition\_blob first8 query entry/MAC/dispatch/return observation only. Original Image4/AMFI/CoreTrust/sandbox TEXT\_EXEC byte-identical to flashed control; trust/root/Data/boot/timeout unchanged. Final producer/PAC/STARTUP/POST/FAT/264branches/original missing2stubbed24 gates and QEMU race6BT pass. Static dyld calls0x22598/225a4/225b0 and sysctl0x239c8 narrow next observation; actual wait not measured. No userdata or flash.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>audit-ignition.py; ./unixnu build kernel; build payload; verify-release.py; verify-bindings.py; verify-console.py; verify-diagnostics.py; QEMU renderer cases</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [Authorized ignition-trace flash 2026-11-03T02:45:29.022723+08:00 to 2026-11-03T02:45:32.860695+08:00: fastbootb8a81f12 productuke/is-userspaceno, sixSHA and four0x6000000 partition sizes passed. booteada6132/vendor\_bootb88e1114 written boot\_a/vendor\_boot\_a/boot\_b/vendor\_boot\_b allOKAY; setactivea/current-slota/rebootOKAY. No userdata. Finald8a0ee8b/CRC21B43B437E708095, bounded PID1 ignition\_blob trace, TCH screen heartbeat10s, original policy/security text preserved. Hardware query outcome/LC\_MAIN/desktop pending. Evidence flash-result-20261103-024529.json/matchinglog.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>fastboot identity/size checks; four-partition flash; set_active a; getvar current-slot; reboot</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `device`: [Photos024605 SHAcc4a2c916f5f9daa67d7b60d4018412e958541106cac3dc5553d2cb6ffb885a4 and024647 SHAebca54b4dc1a298985644ead62a68efb76fdb0f32f66cac51dacae221742560b: user reports temporary photo1 pause then progress; photo2 PID1 ignition\_blob enteroldlen132/newlen0 and dispatch, no returned/MAC rejected visible; TCHf3/f9/f16 and HIDstage3/load0/match0/res1/meta0. No newpanic reported. No thread snapshot, best-effort screen; exact gate/ready wait and LC\_MAIN/desktop not proven.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>Inspect exact user photos and flashed source dispatch location</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [Unflashed ignition-wait vendor\_boot222baafa18701c8b2f18d41702acef627d9bd9b8339151169cb3963d5823cc22/final72fd03d68bc0771cf267bace592f334e32e36330d82f9874a51e7566596d55da/CRC084340DD14DE8E90. Same832Bargs/boot/firmware/trust/root/Data/TCH rate as flashedtrace. Same-thread gate try/result/wait and IOSleep markers max2each, NULL/unrelated/recursive hooks quiet; original gate returns/sleep args preserved, gate\_wait sourcebranches unchanged except observation. Hostcontrols, finalnativehook/PAC/POST/FAT/264branches/originalmissing2stubbed24 and QEMU race6BT pass; original Image4/AMFI/CoreTrust/sandbox code byte-identical. No userdata or flash, actual wait kind pending.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>./unixnu build kernel; build payload; check-hooks.py; final-code/bindings/console/diagnostics verification; QEMU renderer cases</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [ignition-wait flash 2026-11-03T02:57:55.689449+08:00 to 2026-11-03T02:57:59.421523+08:00: user authorizes this flash plus future checked candidates directly in current task. fastbootb8a81f12 productuke/is-userspaceno, sixSHA/four0x6000000 sizes passed. boot\_a/vendor\_boot\_a/boot\_b/vendor\_boot\_b allOKAY, setactivea/current-slota/rebootOKAY. No userdata. booteada6132/vendor\_boot222baafa/final72fd03d6/CRC084340DD14DE8E90; original waiting/security unchanged. Wait-kind/LC\_MAIN/desktop hardware evidence pending. Log flash-result-20261103-025755.json.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>fastboot identity/size checks; four-partition flash; set_active a; getvar current-slot; reboot</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `device`: [IMG025922 SHA06ae3ff5176eea8bc785af44aba8676599bfcb77b21036966fd0faec104d4798 from flashedfinal72fd03d6: ignition\_blob enter132/dispatch, gate try-close0/result5, gate wait deadline0, then TCHf3/f9/f16/f23. Native KERN\_FAILURE5=already closed gate; no IOSleep/returned seen. Holder identity/producer state/LC\_MAIN/desktop not established.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>Read photo and exact native gate_try_close/wait semantics</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [Image4-provider finala0d03581e23e22ab592c3c93b14176a11d089af9ffb32ed8deb61a200eafe28e/vendor\_boot8f0c2735f4c891de49d31301b561cb64c4d6b17a92c132841137d9a4bb18d1ec/CRC6EA6C56C3254667F. Static actual Image4 startvtable2b0@9016cdc callsfinalize@9023838-&gt;serviceMatching\(IOAESAccelerator\)/waitUINT64MAX-&gt;gateopen@902392c; original personality retained. Added native service-start/AES-wait observation and protected gate-owner snapshot only; same832Bargs/trust/root/Data/boot/security text. SoftwareAES catalog17 ABI not enabled/changed. Formal build/finalcode/PAC/POST/FAT/264branches/2missing24stubbed/QEMUrace6BT pass. Standing-authorized flash 2026-11-03T03:10:52.557948+08:00 to 2026-11-03T03:10:54.132000+08:00 sixSHA/four96MiB checked, fourOKAY/activea/readback/rebootOKAY, no userdata; hardware service/AES result stillpending. flash-result-20261103-031052.json](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>audit-provider.py; formal kernel/payload; final verifications; authorized four-partition flash/A-slot/reboot</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [Concrete Image4 startup repair vendor\_bootd314dc6f7ff77ef7074b55f32918e612c5d40c97d7067669f6021cf884131e82/finalafdc535b6294c6e36487ab2d9741526b952e22d2a8f6d99c7824997509b17c16/CRCB42AAD6E20492AE3. Reuses full unchangedSoftwareAES, qualified24A446 instance120/181PACslots and original BTI/N\_ABS inherited bindings; getAlgorithmName belongsIOCryptoAccelerator. Late metaclass after realparent load/sizecheck, catalogue match on platformroot beforeIOBSD, original algorithm/interface KAT must pass beforepublication. Real defaults nub preserved/published ifabsent; OSKext rematches originalImage4. Sourcecrypto/globalordinaryAESoff, original security TEXT\_EXEC/832Bargs/trust/root/Data/boot preserved. Host fullAES NIST128/192/256/chunks/interfaces/badanswer/missingcrypto plus startupordering/refusal controls and finalPAC/POST/FAT/2missing24stubbed/QEMU passed. 2026-11-03T04:13:22.221558+08:00 to 2026-11-03T04:13:23.837870+08:00 standingauthorized sevenSHA/four96MiB/allfourOKAY/activea/readback/rebootOKAY,no userdata. Device KAT/gate/desktop not proven. flash-result-20261103-041322.json](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>defconfig; formal kernel/payload; check-aes.py; check-startup.py; final repair/console/diagnostic audits; authorized flash four/A-slot/reboot</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [aes-direct-start synchronous actualfactory/init/attach/start instead of catalogue+5s wait. Full AES runtime KAT retained, prior0/0/0 does not prove algorithm failure. Build/missing2stubbed24 gate and single final FAT/container/factory-call integrity check passed; no host/QEMU rerun. vendor34762ebe/final083f31c6/CRC36F27F36B4354A08. Flash2026-11-03T04:19:57.819121+08:00 fourOKAY/activea/readback/rebootOKAY,5SHA/four96MiB,no userdata; hardwareKAT/gate pending.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>formal kernel/payload; pack.py image check; authorized four flash/A-slot/reboot</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [Image4-ready vendorf8ef8b1be8430c6ae3e21fd5f0c789398806471266d417fb4f241c12e6c81ef7/final8dfa3c9cb8c56f8e4f999c18c12871ae41f830ff7310a0ad638b4656d7220452/CRC6AD2174F72C7F4C2. Photo042111 SHA4622614d7e6539859a8d9fbdef8cd03a1c74096b64e809d18a128586efeeb73b showsgate0/IOSleep1/TCH. Original ready writer@9023b4c callbackslot8479bb0 ownedbyImage4; this dependency personality was dropped. Added Image4 toroots and normalOSKext matchrequest, originalpersonality byte-equivalent, noflag/gate patch. Original832Bargs/trust/root/Data/AES/boot preserved. Build missing2stubbed24 +oneimagecheck, nohost/QEMU. Standingauthorization 2026-11-03T04:26:00.075217+08:00 to 2026-11-03T04:26:03.918685+08:00 fiveSHA/four96MiB/allfourOKAY/activea/readback/rebootOKAY,no userdata; device ready/desktop pending. flash-result-20261103-042600.json](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>formal kernel/payload; pack.py one image check; authorized flash four/A-slot/reboot</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [Magazine fix vendore7714e345933e9d72f4b40428fa3c46aeb1e9187ba03c5f5c5cf0772ec1c3ad6/final5eb093cb6a42aff912aade8fbbb8abed5efa99474f55b714b1e819244747b38d/CRC3A7F0A19B90C68FD. Usertranscribed magazineinternal7 atIOKit45, BTa9f13a0/a9e272c, originalstartfirst magazineinit; absentproperty helper returns7, currentboothash input missing. OwnerBootSet.v1 roles1/2 SHA384 completeverified envelopes -&gt;148316f0bb4484b19cda323503ffcb454fcc96d089087cd1f140725337c7cb8c435b86e560c193df76821ca121e262e9 explicitlyownerdomain, noAppleticket claim. SourceRootPolicies after originalRSA checks exact544Bheader pins/identity/domain. No fakezine/nonce/securityresult modifications. Build missing2stubbed24 and onefinalADT/FATcheck,nohost/QEMU. 2026-11-03T04:36:14.262323+08:00 to 2026-11-03T04:36:18.013358+08:00 standingauthorized fiveSHA/four96MiB/allfourOKAY/activea/readback/rebootOKAY,no userdata; deviceoutcomepending. flash-result-20261103-043614.json](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>formal kernel/payload; pack.py one final image check; authorized flash four/A-slot/reboot</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [Owner-startup vendorc62d8274703a6a21e193b90bd538b843e96fd6f18c6ca89d7c95c3c093b2b6ff/finalcab65c7015f034c5da4feba951d1e90819df4fde988c0a47e0d15bdb1bd687cb/CRC1E6629CA8DD40FEA. Actual original AES descriptorrequest selector2212/bits128/op0 unsupported0xe00002c7; nofakekey/result. Currentdyld at2217c testsbit3 skipsignite221bc; existingowner cache path only setsafteractualOS/SystemOSauth/readonlyAPFSmount/devcheck/rootrecheck. EnableexistingData292E72B9 path, retainseed. Earlyowneridentity idempotence onlyaftertwomediaproofs exactdomain/digest. SecondhardwareImage4 personalitynotmatched, code/securitypolicy preserved. Buildmissing2stubbed24 +oneimagecheck; 2026-11-03T04:44:11.136587+08:00 to 2026-11-03T04:44:14.826523+08:00 standingauthorized fiveSHA/four96MiB/fourOKAY/activea/readback/rebootOKAY. Nohostuserdatawrite; runtimeDatamaypersist. Actualmounts/choice/desktop pending. flash-result-20261103-044411.json](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>defconfig; formal kernel/payload; pack.py one final image check; authorized flash four/A-slot/reboot</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.

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

- `device`: [SMP boots with the SPI-IPI path; single-CPU profile stable past t=877s](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
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

- `device`: [UKE MEM \~1.11M 4K pages with free \~645 MiB; no jetsam past t=538s where earlier runs died at \~500s](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>fastboot boot boot.img</code>. Revision: `c77d613dc91fb54479242aa5d5902c48662b80d7`.
- `host`: [the generated ADT matches the make-uke-adt.py baseline: identical chosen, cpus, defaults, pram and gmu-memory](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/board.toml)
  Command: <code>python3 scripts/make-uke-adt.py (baseline diff)</code>. Revision: `23c2926941405e7df8097a6bca6ee8348a39c787`.

## 存储与根卷 {#storage}

`device-verified`

组件: `ShengUfs`, `RamBlock`, `VirtioMmioBlock`, `VirtioMmioConsole`, `VerifiedRoot`.

### 硬件与依赖

- UFS host at 0x1d84000 \(GCC windows 0x177000/0x19e000\).
- 24A446 OS disk image: raw APFS, 9,613,344,768 B, image sha256 8a12cdad... \(equals profile \[root\]\), volume UUID 2F8E6EED-...; the VerifiedRoot OS policy verified all 2,347,008 blocks.
- userdata SHNGROOT v2 image \(9,689,890,816 B\): OS window at 0x100000 \(block 512, read-only\) and the OS.vroot data object at 0x23D100000 \(75,104,800 B, block 4096\).

### 配置

- Source storage: ShengUfs + VerifiedRoot + RamBlock + VirtioMmioBlock; the 544-byte policy header travels as kernel.macho.vroot and the hash table as the OS.vroot userdata object.
- Kernel arguments native-source-storage=1 native-ufs-root=1; there is no unverified transport on this line.

### 操作步骤

- ./unixnu build kernel -D ../UniXNU-uke-build
- ./unixnu build userdata -D ../UniXNU-uke-build --object OS.vroot=&lt;policy&gt;/manifest.bin

### 开发经验

- The display bank's stage-1 window functions \(native\_ufs\_dpu\_map/table/l2\) belong to ShengUfs; the display builder stubs only their data when the source storage is absent, so the display backend and the storage link into one kernel \(the map stub is compiled only without storage\).
- The root policy hashes every 4 KiB block of the OS image: the host verification ran vr\_host\_block over all 2,347,008 blocks and the image sha256 equals the profile root \(8a12cdad...\); the 592-byte kernel.macho.vroot bundle's 544-byte manifest header is byte-identical to manifest.bin.
- The OS member of the IPSW is an 8.25 GB AEA archive that decrypts to the raw APFS image; on Linux build userdata reuses it through a .dmg.json cache record instead of the macOS aea tool \(rules 7.22\).

### 完成条件

- The kernel mounts the OS volume from the userdata window through the verified policy and bsd\_init reaches launchd.

### 当前范围

- Original OS/SystemOS and persistent Data were used for the accepted GPU27 system. Power-loss recovery/failure injection was not newly tested.

### 下一步

- Preserve the current authenticated OS/SystemOS and immutable Data seed; do not clear userdata during GPU publication.

### 证据

- `host`: [kernel.macho carries \_native\_source\_storage\_start and \_native\_ufs\_source\_create; userdata-root.img is a v2 SHNGROOT with the OS window \(8a12cdad...\) and OS.vroot \(575c24fb...\)](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/board.toml)
  Command: <code>./unixnu build kernel &amp;&amp; ./unixnu build userdata --object OS.vroot=&lt;policy&gt;/manifest.bin -D ../UniXNU-uke-build</code>. Revision: `a8da9009d43f6c679ebd46903810906afa8ce906`.
- `device`: [the 17.7.11 line mounted its owner Data volume through the NativeUfs transport \(historical; not the source-storage path\)](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
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

- 2026-11-03 ca-surface-track: user explicitly confirms normal upward-swipe entry without the previous freeze; CRC0485290E96ACC9B3/final988d162c/vendor150b5c06. Evidence is user report, not only flash or host checks.
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
- 2026-10-30 \(branch uke-b3a8-scanout, GopFramebuffer 4458e4d, image gpucomp72, built not flashed\): the upstream feat display refuses the render server's two-plane frame, so the spelling joins nativeScanoutFormat with its own 5-bytes-a-texel bound \(native\_legacy\_b3a8\_bounds\) instead of the 4 B/px model its pixel-unit stride can never satisfy; plane 0 is scanned through the same VIG pipes with the ten-bit source word \(\(firmware word &amp; \~0x100\) \| 0x4000 = 0x000276ff, unpack 0x03020001\) and only that plane's 27,340,800-byte prefix mapped, and native\_legacy\_convert\_xr10 decodes it on the CPU when the pipes are not reachable. The direct path also needed the display bank window back: its argument is NativeUfs's uke-dpu-scanout, which the 2026-10-30 02:16 move to the upstream chain dropped while keeping only the display's sheng-dpu-scanout, so from gpucomp50 on every frame took the copy path; board.toml now sets both \(sheng-dpu-scanout=2 uke-dpu-scanout=1\) at 974 of 1000 command-line bytes, dropping offline-legacy-base-present, which only the retired NativeMobileDisplay read.

### 完成条件

- A known frame appears with correct geometry and colors and stays up.

### 当前范围

- User confirms boot, icons/widgets and Settings/Dock interactions on GPU27 CRC90B6BC701210D9DB. Historical iOS17 frame-rate/stall numbers do not describe this build. No instrumented display throughput or long-run stress inference.

### 下一步

- Retain accepted upstream fence/cancellation and requested-scanout behavior; collect future timing under a separately defined workload.

### 证据

- `device`: [User report: 这次正常了，不会卡死。记录一下吧; ca-surface-track CRC0485290E96ACC9B3, final988d162c178a8b02eaffe7cc9aefe833918868e4f23567f10adc9cde5bdcb3e6. Original evidence: release/user-observation.json. Scope: current upward swipe without freeze, duration unspecified. Revision is the working-tree base; full image SHA identifies the tested local repair.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>python3 uke-port/fixes/2026-11-03-ca-surface-track/record-user-success.py</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [swap-dispatch candidate CRCE989F0CE55D5EB3F: final original setter receives effective request0/1/0/1/1, schema74f2, original prelink gate and inputs preserved; not flashed.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>./unixnu build kernel &amp;&amp; ./unixnu build payload; python3 uke-port/fixes/2026-11-03-swap-dispatch/pack.py</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [display-submit diagnostic built, CRC804CD0D45D379053, original missing2/stubbed24 exact sets unchanged, final snapshot uses24A446 fields and actual source dispatch retains IPC/PAC/results; NOT FLASHED per user request.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>./unixnu build kernel &amp;&amp; ./unixnu build payload; python3 uke-port/fixes/2026-11-03-display-submit/pack.py</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `device`: [real UI on screen: white lock screen, home indicator and the swipe prompt; then v3 presents only resolved overlay surfaces](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/GPU-PORT.md)
  Command: <code>fastboot boot boot.img</code>. Revision: `c77d613dc91fb54479242aa5d5902c48662b80d7`.
- `device`: [the verified gpu-framepresent v2/v3 argument set \(recorded from uke-port/releases/2026-10-24-gpu-framepresent-v3/README.md\), now restored in board.toml](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/GPU-PORT.md)
  Command: <code>fastboot boot boot.img</code>. Revision: `ad87339f293a0e55c4a5be25188bdfca8ecea700`.
- `source`: [kernel\_args carry that set; the joined boot-args string is 881 bytes, under the 1000-byte limit](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/board.toml)
- `source`: [A1/A2 register map: DTS block offsets, MDP-relative anchors, SSPP/CTL/INTF/PP/LM registers, dispcc/GCC clocks, GDSC, apps\_smmu SIDs, stock init sequence with source lines](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/dts-reference/mdss-cliffs-map.md)
- `source`: [M1 gate: DTS anchors, stock register defines, NativeUfs window symbols and the built DpuProbe.o all pass \(source-only and archive checks\); a deliberately wrong kVig constant turns it red](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/scripts/check-dpu-probe-host.py)
- `source`: [A3/C1/B2/C2/C3 implementation and the test ladder; boot identical to framepresent4](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/DPU-PORT.md)
- `device`: [M1 PASS: UKE DPU probe=1 snapshot shows GOP e3940000 3200x2136, VIG0/VIG1 1600x2136, 120 Hz, display SMMU bank 2 CBAR type 1 / SCTLR 0xe0](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/DPU-PORT.md)
  Command: <code>fastboot boot vendor_boot_uke_dpu_a3.img</code>. Revision: `3c65101d7ce614a3c2520c4fb5c2b5ac2dd42657`.
- `device`: [M2/C3 PASS: redirecting VIG0/VIG1 to gop+0x800000 \(1600x1068, stride 0x3200\) drew red/green/blue/checker correctly for 2 s each, src0 readback e4140000, auto-restore; low-DRAM e5400000 shows gray \(outside the display-readable GOP range\)](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/DPU-PORT.md)
  Command: <code>fastboot boot vendor_boot_uke_dpu_c3c.img</code>. Revision: `3c65101d7ce614a3c2520c4fb5c2b5ac2dd42657`.
- `device`: [B2 PASS: stage-1 window state=80000002 on bank 2; test=3 mapped a 27.3 MB BGRA buffer at IOVA 0x10000000 and the DPU scanned it \(latch 1196 us\); fix was Linux arm-smmu SCTLR 0x10e7 / TCR 0x803519 / TCR2 0x38015 with a 4xL2 2MB-block table; the S2CR bypass experiment b2v4 crashed and was reverted](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/DPU-PORT.md)
  Command: <code>fastboot boot vendor_boot_uke_dpu_b2v8.img</code>. Revision: `3c65101d7ce614a3c2520c4fb5c2b5ac2dd42657`.
- `device`: [D1b PASS: presentBase maps each BGRA IOSurface into a stage-1 window slot and flips VIG0/VIG1 with no CPU copy; user reports clearly smoother \~10 fps and mostly correct output, with artifacts in some scenes \(suspect GPU in-flight surface reuse; next: fence or one-swap delay\)](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/DPU-PORT.md)
  Command: <code>fastboot boot vendor_boot_uke_dpu_d1b.img</code>. Revision: `3c65101d7ce614a3c2520c4fb5c2b5ac2dd42657`.
- `host`: [the 24A446 Legacy backend binds IOMobileFramebufferLegacy \(379 slots, arm64e PAC diversities\) and links with the presenter, keystore and display/DPU/touch/boot probes; kernel.macho sha256 99a6b970...](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/board.toml)
  Command: <code>./unixnu build kernel -D ../UniXNU-uke-build</code>. Revision: `a8da9009d43f6c679ebd46903810906afa8ce906`.

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

- 2026-11-03 ca-surface-track: user explicitly confirms normal upward-swipe entry without the previous freeze; CRC0485290E96ACC9B3/final988d162c/vendor150b5c06. Evidence is user report, not only flash or host checks.
- Full bring-up runs on device through stage 4: firmware download CRC-ok and scanning 60x40.
- The v3 argument set is sheng-fb-gpu=0 plus offline-legacy-base-present=1; the desktop-era fb-gpu=1 hangs identically.

### 完成条件

- Frames reach HID and the on-screen swipe responds.

### 当前范围

- Current 27-line acceptance is user-confirmed upward swipe without freeze; duration, all-app coverage, cross-reboot stability and GPU acceleration are outside this report.
- Split touch HID delivery and visible swipe are now user-confirmed; the former weak-stub/no-delivery limit is superseded. Multi-touch, full direction coverage and latency were not measured in this report.

### 下一步

- Preserve ca-surface-track as the 27-line interactive baseline; continue other feature or longer-duration validation when requested.

### 证据

- `device`: [User report: 这次正常了，不会卡死。记录一下吧; ca-surface-track CRC0485290E96ACC9B3, final988d162c178a8b02eaffe7cc9aefe833918868e4f23567f10adc9cde5bdcb3e6. Original evidence: release/user-observation.json. Scope: current upward swipe without freeze, duration unspecified. Revision is the working-tree base; full image SHA identifies the tested local repair.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>python3 uke-port/fixes/2026-11-03-ca-surface-track/record-user-success.py</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `device`: [touch-split flashed13:43:32 after5SHA/four96MiB checks, all fourOKAY, activea/readback/rebootOKAY. vendor\_boot5d252ad4, CRC unchanged E989F0CE55D5EB3F. No host userdata writes; real gestures pending.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/TOUCH-PORT.md)
  Command: <code>python3 uke-port/fixes/2026-11-03-touch27/flash.py</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `device`: [13:33 readback66 new CRC records,304 HID reports result0 and changing coordinates. Same boot851FECBA backboardd rejects sender1000001A6 keyboard1/6 digitizer events \(73 rejection messages extracted\). Real swipes unresponsive.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/TOUCH-PORT.md)
  Command: <code>python3 uke-port/fixes/2026-11-03-touch27/read-ring.py; python3 uke-port/fixes/2026-11-03-touch27/parse-unified.py</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [touch-split adds only existing sheng-touch-split=1. Reused byte-identical source/final kernel; linked factory call and922B actual FAT args checked; vendor\_boot5d252ad4, not flashed, gestures not verified.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/board.toml)
  Command: <code>./unixnu build payload; python3 uke-port/fixes/2026-11-03-touch27/pack.py</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `device`: [UKE TCH: scanning v11 pid5993 60x40 with hb/drv/rpt counters advancing](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/TOUCH-PORT.md)
  Command: <code>fastboot boot boot.img</code>. Revision: `c77d613dc91fb54479242aa5d5902c48662b80d7`.

## GPU {#gpu}

`device-verified`

组件: `Adreno740`, `AdrenoMetal`, `AdrenoFirmware`, `AdrenoPM4`, `ArmSmmu4K`, `Sm7675Platform`, `Sm8550Platform`, `AirNir`.

### 硬件与依赖

- Real 0x43030b00/gen7\_11\_0, pinned gen71100 firmware, OEM DT and OEM gen7\_11\_0 source ed4ad0d1ad00.
- Upstream main Adreno740 6fa7bae, Metal 243d63c, GOP e47c1b8; existing 24A446 OS/SystemOS and immutable Data seed.

### 配置

- NATIVE\_ADRENO enabled; per-process VM, preemption mode2, DCVS, BGRA8/SYSMEM and upstream transient GMEM policy.
- 160 MiB raw FAT with standard UEFI compression; paired uke UEFI required.

### 操作步骤

- Build kernel, UEFI, Turnip ios27, Metal ios27, addon/trust and payload; pack boot/vendor\_boot.
- Only the compression round trip and required artifact/record checks; hardware tests follow delivery.

### 开发经验

- Real gen7\_11\_0 GPU stack preserves upstream features and uses original OS resources. Turnip chained fixups avoids prior dyld stack overflow; scoped CoreImage nil-result library retry is present.
- On CRC90B6BC701210D9DB the user confirms all previously reported boot/icon/widget/Settings/Dock UI-restart symptoms resolved. Device result, not just flash transport.

### 完成条件

- Real Metal rendering/presentation and unlock work on uke 24A446.
- Concurrent clients, CP preemption, teardown and persistent warm shader cache work on hardware.

### 当前范围

- Acceptance is the user's direct report on the exact flashed image; no fresh post-fix logs or instrumented frame-time figures were collected this turn.
- Long-run multi-client stress and cache reuse across repeated cold boots remain independently unmeasured.

### 下一步

- Current accepted GPU27 baseline CRC90B6BC701210D9DB is published to the seven user-fork mains; divergent old mains saved as documented. No remaining reported icon/widget/Settings/Dock blocker. Future frame-time, multi-client stress and repeated cold-boot cache measurements are separate work.

### 证据

- `host`: [Kernel/prelink, UEFI, Turnip ios27, Metal arm64e/4K signing and compressed payload builds passed; hardware pending.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/GPU-IOS27.md)
  Command: <code>./unixnu build kernel; ./unixnu build firmware; ./unixnu build payload</code>. Revision: `c131dd44c1f5aff6538251cd22b950e546d90647`.
- `device`: [2026-11-03 19:09:27: four boot/vendor\_boot flashes OKAY, slot a read back, reboot OKAY; actual boot and GPU pending. CRC EC654707C10583A5](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/GPU-IOS27.md)
  Command: <code>fastboot flash boot_a boot.img; fastboot flash vendor_boot_a vendor_boot.img; fastboot flash boot_b boot.img; fastboot flash vendor_boot_b vendor_boot.img; fastboot set_active a; fastboot reboot</code>. Revision: `0f436429f197779f72080076285468abda7948d3`.
- `host`: [SMMU single-user-route candidate builds; missing2/stubbed24 remain, compressed payload round trip passes. Not flashed. Six new ring records end57.760404s; no exact fault register persisted.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/GPU-IOS27.md)
  Command: <code>./unixnu build kernel; ./unixnu build payload</code>. Revision: `aefcb4dd002895c4452e6271d09e98ffad4b3965`.
- `device`: [SID0 candidate CRC374A60FF5A4F1D52: four partition flashes OKAY, current-slot a, reboot OKAY at2026-11-03 19:26:55; actual attach/GPU pending.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/GPU-IOS27.md)
  Command: <code>adb reboot bootloader; fastboot flash boot_a boot.img; fastboot flash vendor_boot_a vendor_boot.img; fastboot flash boot_b boot.img; fastboot flash vendor_boot_b vendor_boot.img; fastboot set_active a; fastboot reboot</code>. Revision: `741be11962dadb0e9925e578b35d9b1c71587843`.
- `device`: [User confirms SID0 no panic, observed30-90fps, icons missing; current Data disabled.plist sets both IconServices labels true. Sameboot24A446 icon cache os\_fault; old17 crash excluded. Enabling candidate not flashed.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/GPU-IOS27.md)
  Command: <code>Read recovery userdata tail and immutable-seed-plus-overlay Data snapshot; inspect disabled.plist</code>. Revision: `1dccbb62dd6a6d3acceee7ec4cad65d48819247a`.
- `host`: [52 original24A446 staged apps include WidgetKit extensions, existing publication flag was off. Combined candidate enables it and keeps IconServices per upstream; CRC7617327C1AD705CE built, missing2/stubbed24 and compression round trip pass, not flashed.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/GPU-IOS27.md)
  Command: <code>./unixnu build kernel; ./unixnu build payload</code>. Revision: `0ed8a86c3e2cf92d04d698e7ee38866bcac695f1`.
- `device`: [Apps/widgets combined candidate CRC7617327C1AD705CE: all four flashes OKAY, active a read back and reboot OKAY; actual app launch/icons/widgets pending.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/GPU-IOS27.md)
  Command: <code>adb reboot bootloader; fastboot flash boot_a boot.img; fastboot flash vendor_boot_a vendor_boot.img; fastboot flash boot_b boot.img; fastboot flash vendor_boot_b vendor_boot.img; fastboot set_active a; fastboot reboot</code>. Revision: `ed60178837d8da473b439adef1b0e6ab81658188`.
- `host`: [Combined widgets candidate failed on device; staged apps are visible, icons service enabled but repeatedly exits. Currentboot container protection class failsCode72. Existing upstream metadata compatibility enabled in a built unflashed repair CRC72D32647A9779337; freeze mechanism unresolved.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/GPU-IOS27.md)
  Command: <code>Read recovery logs/Data snapshot; ./unixnu build kernel; ./unixnu build payload</code>. Revision: `dea3d5467718e3bb850e148d07cd796a3303be3d`.
- `device`: [Data-class candidate CRC72D32647A9779337 four flashes OKAY, active a read back, reboot OKAY at2026-11-03 20:08:21; Code72/app/icons/widgets/freeze acceptance pending.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/GPU-IOS27.md)
  Command: <code>adb reboot bootloader; fastboot flash boot_a boot.img; fastboot flash vendor_boot_a vendor_boot.img; fastboot flash boot_b boot.img; fastboot flash vendor_boot_b vendor_boot.img; fastboot set_active a; fastboot reboot</code>. Revision: `0d52c01bda8dbf49ec22120c9f11a67f030aa1ef`.
- `device`: [Data-class fails user acceptance: missing icons/freeze; one Photos widget/clock hands. BootAAB5DAA8 actual pid406 IPS shows withChainStarts stack overflow while loading Turnip, x8=439304 exactly equals legacy dyld buffer calculation. Selected sameboot logs no longer contain previous containerCode72; scope limited to parsed selection.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/GPU-IOS27.md)
  Command: <code>Read-only recovery UKELLOG1 and Data overlay; parse sameboot trace/IPS</code>. Revision: `9d54f54240385ca15beef84f5702e2dff40ce272`.
- `host`: [ios27 chained-fixups Turnip/plugin/addon/trust/payload built. Final signed addon dylib has chained fixups, no legacy dyld info;4210 signature page hashes verified; old IPSW trust modules unchanged; compression roundtrip passes. vendor\_boot44859392B SHA896955d7; kernel identical CRC72D32647A9779337. Unflashed, no hardware repair acceptance.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/GPU-IOS27.md)
  Command: <code>python3 scripts/build-turnip-darwin.py --target ios27; python3 scripts/build-adreno-metal-plugin.py --target ios27 --no-replay; ./unixnu build payload</code>. Revision: `a8dd11057337d362a57a8457355ce77c50ed5e0c`.
- `device`: [Turnip chains flashed2026-11-03 20:29:32 under current explicit authorization;8SHA/uke/non-userspace/four96MiB prechecks pass, all four flash OKAY, active a read back/reboot OKAY. vendor\_boot896955d7, CRC72D32647A9779337 unchanged. No host userdata write; icons/widgets/freeze outcomes pending.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/GPU-IOS27.md)
  Command: <code>python3 uke-port/fixes/2026-11-03-ios27-gpu-render-failure/flash-chains.py</code>. Revision: `a8dd11057337d362a57a8457355ce77c50ed5e0c`.
- `device`: [Chains candidate partial: user sees slow icons and Dock respring. Fresh195 ring slots/1853 old excluded, sameboot027440E6 parsed2330230 log records. Two iconservices IPS CoreImage+0x1a82c FAR0x28; six CI libs fail loading; QuartzCore62 DeviceLost then SIGTERM400.583s/backboardd551 respawn. Preferences453 separate10s IOKit-wait watchdog. GPU loss and actual library-load root cause remain open; no speculative repair built, no host userdata writes.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/GPU-IOS27.md)
  Command: <code>Read recovery ring and immutable-seed-plus-overlay Data read-only; parse sameboot IPS/trace, inspect original CoreImage load path</code>. Revision: `a8dd11057337d362a57a8457355ce77c50ed5e0c`.
- `host`: [Formal kernel/prelink/payload passed;missing2/stubbed24 exact sets unchanged. Owner cryptex binds inherit source native-union lookup/enumeration. sheng policy aligned, GPU VM/preemption/recovery and signed chains userspace preserved. CRCED9AFCA7B8824CBE, vendor\_bootb2e3db81, 44859392B,160MiB FAT/one compression roundtrip pass. Not flashed; icons/Dock/Settings outcomes pending.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/GPU-IOS27.md)
  Command: <code>git fetch origin main (core/sheng/Adreno740/Metal/SM8550); ./unixnu build kernel; ./unixnu build payload</code>. Revision: `6a91677cbdc873cc5c2a63a33022b6e2262eee3a`.
- `device`: [2026-11-03 21:21:12 resource-view final repair flashed four partitions OKAY, current-slot a read back, reboot OKAY. CRCED9AFCA7B8824CBE, vendor\_bootb2e3db81. Two image SHA and necessary target/size checks only; no host userdata writes or extra host/QEMU test rounds. Icons/Settings/Dock actual acceptance pending.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/GPU-IOS27.md)
  Command: <code>python3 uke-port/fixes/2026-11-03-ios27-gpu-upstream-repair/flash-resource-view.py</code>. Revision: `6a91677cbdc873cc5c2a63a33022b6e2262eee3a`.
- `device`: [resource-view user reports Apple-logo boot failure. New88 CRC-valid ring records/1960 old excluded;bootDC81CB84 parsed2503065 entries. launchd Early boot83.933s,lsd99 high94pct CPU, kernel/Touch continues226.736s; actual lsd loop not proven. Broad changes reverted. User rejects rollback-only result; old image not flashed, stock four/TWRP retained for capture.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/GPU-IOS27.md)
  Command: <code>Read-only recovery ring/Data capture and sameboot trace parsing</code>. Revision: `0a22d26034642e6c4698783d6b1295ec89bb6c56`.
- `host`: [New scoped iOS27 CI original-nil standard-library retry compiled with original retained-return ABI; runtime/pins/features unchanged. Kernel1858e77 persists bounded failures; Metal10a077a signed with matching trust. Formal kernel/plugin/payload pass,missing2/stubbed24 exact unchanged;one compression roundtrip,160MiB FAT, vendor\_boot44859392B. CRC90B6BC701210D9DB; unflashed, actual icon latency/Dock/Settings outcomes unqualified.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/GPU-IOS27.md)
  Command: <code>./unixnu build kernel; python3 scripts/build-adreno-metal-plugin.py --target ios27 --no-replay; ./unixnu build payload</code>. Revision: `10a077a8b4de9b8333069089e808ab8ad2cba8bd`.
- `device`: [Scoped CI repair CRC90B6BC701210D9DB four boot/vendor\_boot flash OKAY/current-slot a/reboot OKAY at2026-11-03 22:31:33 under explicit new-repair authorization. Two SHA/uke/nonuserspace/four96MiB bounds pass; Data FUSE unmounted/no host userdata write. Boot/icons/Dock/Settings effects pending; no old rollback executed.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/GPU-IOS27.md)
  Command: <code>python3 uke-port/fixes/2026-11-03-ios27-gpu-coreimage-resources/flash.py</code>. Revision: `10a077a8b4de9b8333069089e808ab8ad2cba8bd`.
- `device`: [User explicitly confirms all prior reported symptoms resolved on the exact CRC90B6BC701210D9DB build flashed22:31:33: boot beyond Apple, desktop/Settings icons and widgets load, Settings upward Dock/app interaction no longer causes the reported UI restart. vendor\_bootcd41b67e. No extra long-run/frame-time/reboot-cache coverage inferred.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/GPU-IOS27.md)
  Command: <code>User hardware feedback after flash-result-20261103-223133.json; record user-observation-success.json</code>. Revision: `10a077a8b4de9b8333069089e808ab8ad2cba8bd`.

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

- `device`: [mode 8 passes: GX off/on with the perf vote and the H0.. heartbeat every 2 s](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/GPU-PORT.md)
  Command: <code>fastboot boot vendor_boot_uke_gpu_m8.img</code>. Revision: `c77d613dc91fb54479242aa5d5902c48662b80d7`.

## 镜像组装 {#packaging}

`host-verified`

组件: `DarwinBoot`, `XnuPrelink`, `VerifiedRoot`.

### 硬件与依赖

- Stock vendor\_boot DTB with the board's dtb\_node patches \(splash reservation, payload at 0x1000000\).
- Trust cache bundle and the recorded Data seed.

### 配置

- 160MiB raw FAT, payload.compression=uefi; EDK II standard UEFI compression transport in vendor\_boot. Paired uke UEFI expands into reserved0xA8000000..0xB2000000 after overlap checks.
- Android v4 vendor\_boot retains original DTB/table/bootconfig/vbmeta. Accepted boot1519616B and vendor\_boot44859392B fit the96MiB partitions.

### 操作步骤

- ./unixnu build payload --kernel kernel.macho --unique-chip-id HEX -D ../UniXNU-uke-build
- ./unixnu bootimg --uefi ../uefi-uke --dtb ../uke-port/data/vendor\_boot.dtb --ramdisk none -D ../UniXNU-uke-build

### 开发经验

- The v4 header parsing and the existing-/chosen tolerance are in unixnu bootimg \(core 5525d18\); the boot image carries an empty ramdisk because the payload is the vendor\_boot vendor ramdisk.
- payload, boot, vendor\_boot and userdata all build on Linux; only the Data skip-setup seed still needs macOS.

### 完成条件

- payload.img contains kernel.macho, its ADT, the trust cache, the Data seed and kernel.macho.vroot; boot.img boots from the stock DTB.

### 当前范围

- Exact binary identity is the accepted release manifest and CRC90B6BC701210D9DB; later documentation/pin commits do not imply a rebuilt image.

### 下一步

- Use the paired accepted images and preserved CPU rollback. Keep the original Data seed and owner trust inputs.

### 证据

- `host`: [payload.img 94 MiB \(sha256 e368e3f3...\) and boot.img 1,515,520 bytes \(sha256 9b04ce75...\) over the stock vendor\_boot DTB](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/board.toml)
  Command: <code>./unixnu build payload &amp;&amp; ./unixnu bootimg --uefi ../uefi-uke --dtb ../uke-port/data/vendor_boot.dtb --ramdisk none</code>. Revision: `a8da9009d43f6c679ebd46903810906afa8ce906`.
- `device`: [the fmt2 test image booted to userland on hardware with the recovered platform seed and the Data seed handoff](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/GPU-PORT.md)
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

- Fresh UKELLOG1 and sameboot Data reports were recovered for prior failing27 builds. Current success is direct user feedback; post-fix fault counters were not recaptured this publication turn.

### 下一步

- Keep bounded client/recovery reasons available for any new failure; high-cost frame/pixel capture remains disabled.

### 证据

- `device`: [swap-dispatch flashed13:27:56 after5SHA/four96MiB checks, all fourOKAY, set\_activea/current-slot a/rebootOKAY, CRCE989F0CE55D5EB3F. No host userdata writes; requested/backend/GUI outcomes pending.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>python3 uke-port/fixes/2026-11-03-swap-dispatch/flash.py</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `device`: [13:06:33 tail readback sha d8e8331b...,123 fresh CRC-valid slots0..122,1925 unchanged slots excluded. Backboardd original SwapBegin/End/Wait and default Mach port succeed, validate/transfer0; TWRP retained, no host userdata write.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>python3 uke-port/fixes/2026-11-03-display-submit-readback/read-ring.py</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `device`: [display-submit flashed12:59:27:5SHA/four96MiB bounds checked, boot\_a/vendor\_boot\_a/boot\_b/vendor\_boot\_b OKAY, activea/readback/rebootOKAY, CRC804CD0D45D379053. No host userdata writes; hardware GUI/trace outcome pending.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>python3 uke-port/fixes/2026-11-03-display-submit/flash.py</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `device`: [09:51:14 TWRP readback sha e5bde46c..., new slots0..136/137 records all CRC-valid,1911 unchanged old slots excluded; log49.664755s opens LBA61941755, last321.876064s. No host userdata writes.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/RECOVERY-LOG.md)
  Command: <code>ADB_LIBUSB=0 adb start-server; adb exec-out dd if=/dev/block/by-name/userdata bs=4096 skip=58980347 count=8192 status=none</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `host`: [Formal gate unchanged; writer UFS calls and both startup entries linked, actual payload enables log/crash probe; real 27 disk write pending.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/PROGRESS.md)
  Command: <code>python3 uke-port/fixes/2026-11-03-persistent-log/pack.py</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `device`: [Read-only TWRP dump 33554432B, 708 CRC-valid old records excluded from current 27 diagnosis, no userdata writes.](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/RECOVERY-LOG.md)
  Command: <code>adb shell dd if=/dev/block/by-name/userdata bs=4096 skip=58980347 count=8192 of=/tmp/ukelog-20261103.bin</code>. Revision: `5ed46420025be331b51d98207ea6aa679faac9c7`.
- `device`: [the panic screen and last-panic line read back from the reserved pram log on hardware](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/docs/RECOVERY-LOG.md)
  Command: <code>fastboot boot boot.img</code>. Revision: `c77d613dc91fb54479242aa5d5902c48662b80d7`.
- `host`: [kernel, payload and boot images build end to end at the format-2 output path](https://github.com/Allenwdk/UniXNU-uke/blob/fcf9fd3f31be4618a48d33fd7cf161e0da75b573/board.toml)
  Command: <code>./unixnu build kernel &amp;&amp; ./unixnu build payload &amp;&amp; ./unixnu bootimg</code>. Revision: `4f4bf7e1f4ad56743562777becd7ac7d6714216c`.

</div>
