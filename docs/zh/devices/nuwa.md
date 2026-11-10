# 小米 13 Pro（nuwa）

[wh1stl3/UniXNU-nuwa](https://github.com/wh1stl3/UniXNU-nuwa)

<div v-pre>

Xiaomi 13 Pro \(SM8550\) iOS 16.7.16 bring-up. Format 2 migration started 2026-11-06: device repo + UniXNU-sm8550-common + uefi-nuwa. Every area is planned until hardware evidence is recorded.

源记录: [porting.toml](https://github.com/wh1stl3/UniXNU-nuwa/blob/19d675e52197ecba200677af9f3eea71a037628f/porting.toml), `19d675e52197ecba200677af9f3eea71a037628f`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `planned` |
| [固件与启动](#firmware) | `planned` |
| [CPU 与中断](#cpu) | `planned` |
| [内存与 DMA](#memory) | `planned` |
| [存储与根卷](#storage) | `planned` |
| [显示](#display) | `planned` |
| [输入](#input) | `planned` |
| [GPU](#gpu) | `planned` |
| [网络](#network) | `planned` |
| [音频](#audio) | `planned` |
| [电源](#power) | `planned` |
| [镜像组装](#packaging) | `planned` |
| [诊断](#diagnostics) | `planned` |
| [cellular](#cellular) | `planned` |

## 配置 {#configuration}

`planned`

组件: `ArmDTPlatform`, `ArmCpu`, `XnuPrelink`, `DarwinBoot`.

### 硬件与依赖

- SM8550 common repository commit \(pinned in feeds.toml\).
- The iOS 16.7.16-20H392 OS profile at UniXNU/profiles/os/ios-16.7.16-20H392, authored locally in UniXNU commit 693f5d9cae8a408dd18b39f3f9fdc4228c934241; the official profiles/os tree ships iPadOS 17.7.11, iPadOS 26.5.2 and iOS/iPadOS 27.0.1 only.
- The donor KernelCache member hash for \[ipsw.sha256\]; the profile already carries the IPSW url, chip\_id, board\_id and the DeviceTree plus StaticTrustCache member hashes read from the donor BuildManifest.

### 配置

- board.toml schema\_version = 2 with \[board\], \[components\], \[kernel\], \[device\_tree\], \[firmware\], \[payload\], \[payload.adt\], \[package\].
- feeds.toml pins UniXNU-sm8550-common at a9f45dc60c035084b95463781538380f4c3606c9.
- dts/nuwa.dts includes soc:dts sm8550.dtsi and carries the measured DRAM span only.
- board.toml \[ipsw\] declares product, version, build, device\_class and fetch only; url, chip\_id, board\_id and the member hashes are inherited from the selected profile instead of being duplicated.
- \[payload\] tools = true adds the Tools entry to the generated payload boot menu.

### 操作步骤

- ./unixnu defconfig nuwa\_defconfig -D ../UniXNU-nuwa
- ./unixnu fetch -D ../UniXNU-nuwa
- ./unixnu status --json -D ../UniXNU-nuwa
- ./unixnu tree -D ../UniXNU-nuwa

### 开发经验

- The local iOS 16 OS profile lives at UniXNU/profiles/os/ios-16.7.16-20H392 \(UniXNU commit 693f5d9cae8a408dd18b39f3f9fdc4228c934241\): xnu 8796.141.3 \(1b191cb58250d0705d8a51287127505aa4bc0789\), the donor IPSW url/product/build/device\_class \(d22ap, chip 0x8015, board\_id 6\), the DeviceTree and StaticTrustCache sha256 pins, ADT identity D22AP, kernelcache sha256 and the 31 prelink roots verified against the donor \_\_PRELINK\_INFO; board.os\_profile and \[device\].os\_profile select it.
- board.toml sets \[firmware\] preflight and \[bootimg\] dtb = 'build/nuwa/sm8550-xiaomi-nuwa.dtb'; the dtb path is relative to the build tree, the base ctx.tree/dtb does not expand a &\#123;uefi&\#125; template, and an FDF-embedded DTB does not automatically become the appended DTB.
- Official step 4 is complete: defconfig, fetch, status --json and tree resolve the board against that profile, and the fetch is recorded on 279c990a0c7a238aa0a5818493c6cd6a46528749 \(unixnu.lock: xnu 1b191cb5, sm8550 a9f45dc6, edk2 cfb93724, libplatform a00a4cc3, libdispatch 30fe6a7d, libpthread c0e60fb5, AvailabilityVersions 933f9360, corecrypto-2023 11fba65b, IOStorageFamily e45fbe30\). Step 5 \(hardware description and firmware\) is in progress.
- The official profiles/os tree ships iPadOS 17.7.11, iPadOS 26.5.2 and iOS/iPadOS 27.0.1 only, which is why this profile is authored locally; profile selection is no longer blocked.
- board.toml \[payload\] tools = true adds the Tools entry \(id = tools, action = tools\) to the generated EFI/UniXNU/unixnu.toml, so the exported firmware log can be read from the boot menu; the entry has not been exercised on hardware.
- board.toml \[firmware.defines\] now sets ENABLE\_SECUREBOOT = 0 \(2026-11-07\): SiliciumPkg.dsc.inc:13 passes -D ENABLE\_SECUREBOOT=$\(ENABLE\_SECUREBOOT\) unconditionally, and unixnu runs the EDK II build directly instead of Mu-Silicium's build\_uefi.py \(default 0, --enable-secureboot is opt-in\), so an empty macro failed the preprocessing of SecureBootHandler.c:216 \(\#if ENABLE\_SECUREBOOT == 1\). Self-checked with the define in place: the firmware build recorded in the firmware area exited 0, and the Verifier subagent later re-ran it independently; nothing has run on hardware.
- dts/nuwa.dts comment corrected \(comment-only\): scripts/unixnu/devicetree.py takes exactly one /memory node with one contiguous reg range, so the previous nine-segment TODO was wrong; the 0x8c0000000/0x240000000 geometry and the owned-window contract are unchanged \(docs/step5-firmware.md\).
- Repo hygiene: removed the committed \_\_pycache\_\_ copies of the format-1 legacy tooling; no source behaviour changes.
- Repo hygiene: the committed \_\_pycache\_\_ blobs were untracked and are ignored; scripts/ keep format-1 legacy tooling that still points at deleted absolute paths and is not part of the official flow.
- The SM8550 shared series targets XNU 10063/12377, so soc:patches/xnu/series is deliberately not selected for the 8796 line.
- \[userdata\] is populated in board.toml from the 2026-11-07 read-only GPT capture \(docs/device-evidence-2026-11-07.md\): first\_lba = 3110976, last\_lba = 61850618, lba\_bytes = 4096, copied from the GPT dump parsed on the host; no GUID, serial, kernel command line content or chip seed is recorded.
- ADT identity values decided 2026-11-07 \(docs/step5-firmware.md, 'ADT identity values'\): ADT /chosen/chip-id \(u32\) and unique-chip-id \(u64\) are software identity seeds for IOPlatformUUID, not Apple silicon IDs; the generator checks only nonzero and width and never compares them against the SoC. The donor iPhone10,3 DeviceTree \(base out/ipsw/20H392/DeviceTree.d22ap.dtb, an LZFSE-compressed ADT\) carries chip-id = 0 and unique-chip-id = 0, template placeholders that iBoot fills at run time, so the donor offers no value to copy.
- chip\_id = 4acab8db was drawn at random on the host on 2026-11-07: nonzero, and different from sheng's 0x8142 and from the donor ApChipID 0x8015. It is written in board.toml \[payload.adt\] and stays fixed once images exist.
- The unique-chip-id u64 seed is drawn at random on the host as eight hex digits and kept only in the git-ignored unixnu.local.toml of the base UniXNU checkout; no seed value is committed. Every build must reuse the same value, and if it is lost the same device gets a different IOPlatformUUID, so the user must back it up.
- root\_match\_volume\_uuid is commented out in board.toml for bring-up stages 1-5: fastboot boot uses the in-memory Data seed, the generator omits /chosen/root-matching when the value is empty, and a non-empty placeholder fails UUID parsing. Before stage 6, read the OS APFS volume UUID \(not the container UUID and not the Data volume UUID\) from the built userdata image and write it to board.toml and to the OS profile \[root\] os\_volume\_uuid.
- Self-checked \(2026-11-07, in memory, no device\): generating the ADT from the real board.toml, the iOS 16 profile and the local seed returned 12984 bytes; /chosen carries chip-id = 0x4acab8db, an 8-byte nonzero unique-chip-id matching the local seed, dram-base = 0x8c0000000, dram-size = 0x240000000 and darwinboot-memory-size = 0x40000000, has no root-matching \(expected at this stage\), lists 8 cpu reg entries 0..1792, timebase-frequency = 0x124f800 and psci = smc, and arm-io holds only the intc child because nuwa.dts still describes CPU, memory and intc only \(step 6 work\). ephemeral-storage is absent because no Data seed was passed, which is a property of this run, not a stage 1-5 conclusion.

### 完成条件

- All source pins resolve; every selected component has a record; status shows the intended overrides and patch order.

### 当前范围

- The donor KernelCache member hash \(kernelcache.release.iphone10b\) is not pinned in \[ipsw.sha256\] yet; the OS and Cryptex1,SystemOS member hashes are taken at the userdata stage.
- No board DTS register set for storage, display, input, GPU, network, audio and power yet, so those components stay unselected.
- ADT identity: chip\_id is decided and written \(4acab8db\); root\_match\_volume\_uuid stays unset until the userdata image is built before stage 6; the unique-chip-id seed lives only in the base checkout's git-ignored unixnu.local.toml and needs a user backup.

### 下一步

- Official step 5: finish the uefi-nuwa firmware integration \(UniXNU, UniXNUDxe, DarwinBoot, RamDisk, DiskIo and FAT modules plus the Advanced Logger export\) and reconcile the board DTS with the firmware DTB before selecting step 6 drivers.

### 证据

- `source`: [board.os\_profile = ios-16.7.16-20H392 resolves to the profile at UniXNU commit 693f5d9cae8a408dd18b39f3f9fdc4228c934241, which carries the IPSW url, chip\_id 0x8015, board\_id 6 and the DeviceTree/StaticTrustCache sha256 pins; \[payload\] enables the Tools entry and \[firmware.defines\] sets ENABLE\_SECUREBOOT = 0 because SiliciumPkg.dsc.inc passes the macro unconditionally while unixnu bypasses build\_uefi.py.](https://github.com/wh1stl3/UniXNU-nuwa/blob/19d675e52197ecba200677af9f3eea71a037628f/board.toml)

## 固件与启动 {#firmware}

`planned`

### 硬件与依赖

- Identify the firmware and boot hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for firmware and boot.

### 操作步骤

- Follow the firmware and boot stage in the porting guide and record the actual commands.

### 开发经验

- Reviewed firmware facts \(2026-11-07, docs/step5-firmware.md\): the firmware DTB carries no splash\_region node, while the live machine reports 0xb8000000 with size 0x2b00000 and MemoryMapLib already describes a Display Reserved region. Whether ABL consumes that reservation is unproven, so nothing is injected into the DTB by this review; the firmware repository carries a separate DSC/FDF integration \(uefi-nuwa commit becd65b921553957899cc069d6ac6c1278dedd08\).
- Vendor inputs: the nuwa DXE set comes from the public Project-Silicium/Device-Binaries repository, path nuwa/, commit 4648d229f9bedf0d17ba6fe2bebd3fc6fb01422d \(git tree d8512b51f264cb4dc2114a788066a80fb77cf8b8, 333 files, 8.5 MB\), checked out sparsely into uefi-nuwa/Binaries and kept out of the firmware repository history. A local per-file SHA-256 manifest hashes to 6cff995a23b458bcbee0518dbe9b9d74eeea388e410b17413c913a361e702cab. With this tree present every Binaries/nuwa reference in nuwa.dsc/nuwa.fdf resolves \(static path check only\); the remaining unresolved references belong to the Mu and Mu\_Basecore submodules, whose contents are staged by hand for the build \(see the build-input finding below\). The repository declares no licence, and the upstream origin of these binaries is unverified.
- bootimg.dtb wiring stays deferred to a separate report. The ADT identity is decided: chip\_id = 4acab8db is written in board.toml \(see the configuration area\), and root\_match\_volume\_uuid stays commented out until the userdata image exists before stage 6.
- Step 5 firmware integration is recorded as an independently re-run build \(2026-11-07\): after an earlier self-checked run \(the Verifier subagent's first attempts returned 'Country, region, or territory not supported'\), the Verifier subagent re-ran the build against device repository b1064eb8 and uefi-nuwa e494c01b with PASS. uefi-nuwa commit becd65b921553957899cc069d6ac6c1278dedd08 holds the nuwaPkg DSC/FDF integration \(UniXNU, UniXNUDxe, UniXNURamDiskDxe, DarwinBoot and AdvancedLogDxe with DiskIo and FAT\). From the base checkout \(cwd /mnt/d/Code/PortingiOS/UniXNU\) \`./unixnu build firmware -D ../nuwa/UniXNU-nuwa --uefi ../nuwa/uefi-nuwa --edk2 /home/wh1stl3/nuwa-fw/mu\_basecore\` exited 0 and produced uefi-nuwa/Build/nuwaPkg/DEBUG\_CLANGPDB/FV/SILICIUM\_UEFI.fd, 3145728 bytes = 0x300000, matching \[firmware\] uefi\_fd.size in nuwa.toml; FVMAIN.inf lists UniXNU, UniXNUDxe, UniXNURamDiskDxe, DarwinBoot and AdvancedLogDxe. AdvancedLogDxe's producer is now wired in uefi-nuwa commit e494c01b2f679439fdaeaf2084b693c7220543f5: DXE\_CORE uses AdvLoggerPkg's DxeCore AdvancedLoggerLib \(its constructor installs gAdvancedLoggerProtocolGuid\), DXE\_DRIVER/UEFI\_DRIVER/UEFI\_APPLICATION use the Dxe instance and DXE\_RUNTIME\_DRIVER the Runtime instance, the real AdvancedLoggerHdwPortLib runs over SerialPortLib \(DEBUG keeps FrameBufferSerialPortLib so the screen log remains and is also written to the buffer\), DEBUG sets DebugLib = BaseDebugLibAdvancedLogger while RELEASE is unchanged, SEC keeps BaseDebugLibSerialPort because Sec.c calls BaseDebugLibSerialPortConstructor directly \(the first link attempt failed before that correction\), and PcdAdvancedLoggerBase = 0 with the DXE\_CORE library allocating a 4 MiB buffer via AllocateReservedPages instead of a fixed physical address. The independent rebuild passed and produced a 3145728-byte SILICIUM\_UEFI.fd; DxeMain links DxeCoreAdvancedLoggerLib, AdvancedLogDxe and UniXNUDxe link DxeAdvancedLoggerLib, Guid.xref contains gAdvancedLoggerProtocolGuid, and FVMAIN.inf still lists the five modules. Runtime dispatch and the Tools -&gt; Advanced Logger page remain unverified \(a device run is needed\), the assumption that the 4 MiB reserved-page allocation lands in the DXE heap is unconfirmed, the boot-chain review concluded APPROVE WITH CONDITIONS on 2026-11-07 scoped to the first fastboot boot \(deep not used; no candidate met ai-orchestration §2.3\), and the memory ownership gate is still open.
- Firmware build inputs \(2026-11-07\): Mu\_Basecore comes from the GitHub archive cfb93724a06ff86ff5ba971413368a7809ee42a5 extracted under WSL ext4 at \~/nuwa-fw/mu\_basecore; the archive carries no submodule contents, so five submodule directories were copied from the already-checked-out base out/feeds tree \(MdePkg/Library/BaseFdtLib/libfdt, MdePkg/Library/MipiSysTLib/mipisyst, BaseTools/Source/C/BrotliCompress/brotli, MdeModulePkg/Library/BrotliCustomDecompressLib/brotli, SecurityPkg/DeviceSecurity/SpdmLib/libspdm\). openssl \(archive 67b5686b4419b4cb8caa502711c41815f5279751\) sits at the uefi-nuwa gitlink path; Common/Mu b8d46c71, Common/Mu\_OEM\_Sample b70b4b7b and Silicium-ACPI 2d465ad7 come from the fixed pins; Binaries are listed in proprietary-files.txt. Inside WSL the link needs MTU 1400 and the proxy is passed through environment variables to the Windows host gateway port 7890 with allow-lan enabled. These staging steps are manual and not scripted yet; the command sequence is in docs/step5-firmware.md.
- \[firmware\] patches wire Resources/MuPatches/Gic-Spurious.patch from the Mu-Silicium checkout \(sheng uses the same one\); during the 2026-11-07 build \(built; independently re-run by the Verifier subagent on b1064eb8/e494c01b\) it applied cleanly to the shared edk2 tree and rolled back cleanly.
- Format-2 migration: \[firmware\] points at the device Mu-Silicium checkout and proprietary-files.txt lists the required inputs; the vendor input set is recorded and hashed in proprietary-files.txt.
- board.toml wires \[firmware\] preflight and \[bootimg\] dtb = 'build/nuwa/sm8550-xiaomi-nuwa.dtb' \(the dtb path is relative to the build tree; the base ctx.tree/dtb does not support a &\#123;uefi&\#125; template, and an FDF-embedded DTB does not automatically become the appended DTB\). scripts/prepare-nuwa-firmware.py only copies the generated DTB and does not edit any node.
- Self-checked \(2026-11-07, not independently verified: the Verifier subagent returned 'Country, region, or territory not supported' on both attempts\): in the base checkout, ./unixnu defconfig nuwa\_defconfig and ./unixnu tree -D ../nuwa/UniXNU-nuwa both exited 0 with the tree at UniXNU/out/nuwa/ios-16.7.16-20H392/nuwa/tree; in that tree, UNIXNU\_UEFI=.../uefi-nuwa python3 scripts/prepare-nuwa-firmware.py exited 0 and cmp showed tree/build/nuwa/sm8550-xiaomi-nuwa.dtb byte-identical to the firmware repository FdtBlob/sm8550-xiaomi-nuwa.dtb; dtc -I dts -O dtb -i UniXNU-sm8550-common/dts nuwa.dts exited 0; and unixnu.devicetree.generate returned 12552 bytes containing the dram-base, dram-size, timebase-frequency, psci, cpu0 and cpu7 substrings \(substring presence only; per-value CPU reg and GIC stride were not checked, so they stay unverified\). This is a hardware-side resource-encoding check, not a complete ADT: chip\_id and root\_match\_volume\_uuid were still placeholders at that run \(the later chip\_id decision is recorded in the configuration area\). No host-class evidence entry is added because it would require a command plus a full 40-character revision, and the device repository changes are uncommitted, so no revision is supplied rather than invented.
- MemoryMapLib reconciliation \(static, 2026-11-07, docs/step5-firmware.md section 'MemoryMapLib reconciliation \(static\)'; static analysis, not verified on hardware\): the static table has 41 entries, 27 inside DDR, while the live FDT has 35 fixed-reg reserved regions, 6 of them no-map regions the table does not describe. If RamManagerDxe pads uncovered System RAM gaps as Conventional, 16 fragments total about 10.80 GiB and a 1 GiB window first-fits in the 0x8c0000000 fragment inside the ADT dram-base. Do not shrink owned\_memory\_size: below about 925 MiB the window falls outside the ADT range, and any memory-number change needs user confirmation. The RAM Partition content is unknown.
- Reviewer verdict \(2026-11-07, read-only static, docs/step5-firmware.md section 'First fastboot boot: Reviewer verdict and conditions'\): window-allocation risk is Medium, APPROVE WITH CONDITIONS for the first fastboot boot only, and Deep Reviewer was not used because no candidate met docs/ai-orchestration-2026-11-06.md §2.3. The failure path writes no partition and prints NO WINDOW/FREE, the success path prints pa/va/entry/args/owned, and XNU's physical range comes from boot\_args. Still open: the RamPartition protocol producer \(RamManagerDxe is not in apriori, Depex = TRUE, runs at nuwa.fdf:87\), SEC HOB write confirmation, a DEBUG build, fastboot boot only with user authorisation, the capture plan, and the FD/ramoops overlap confirmation.
- Collect the first firmware and boot observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Firmware image builds, enters UniXNU, publishes the framebuffer and preserves the documented memory reservations.

### 当前范围

- The firmware build was independently re-run by the Verifier subagent on 2026-11-07 against device repository b1064eb8 and uefi-nuwa e494c01b: PASS \(exit 0, 0x300000-byte FV\).
- First hardware runs \(2026-11-07, three fastboot boot runs, no partition written, read from phone-camera video, see docs/step5-firmware.md\): the firmware starts, prints DXE logs and, since uefi-nuwa d7c97a7 \(DXE Heap 0xBAB00000+0x0D1C0000\), shows the UniXNU menu; Tools -&gt; Advanced Logger exports a log as 24 OneSend QR frames that decode on the host \(179 lines\); RamManagerDxe maps the high 9 GiB and UniXNURamDiskDxe publishes an initrd block device. Stage 1 and the menu part of stage 2 are met. Stage 3 half met \(2026-11-08\): with a placeholder payload written to the unused slot's vendor\_boot\_b, the menu reported config EFI/UniXNU/unixnu.toml and listed the xnu entry \(photo; see docs/step5-firmware.md\); payload hashes, the ADT sidecar, DarwinBoot and the memory window are not yet exercised and need a real kernel.
- The Advanced Logger producer is wired \(uefi-nuwa e494c01b2f679439fdaeaf2084b693c7220543f5\) and the image builds, but runtime dispatch and the Tools -&gt; Advanced Logger page are unverified, the 4 MiB reserved-page allocation's placement in the DXE heap is an assumption, and the boot-chain review concluded APPROVE WITH CONDITIONS on 2026-11-07, scoped to the first fastboot boot only \(deep not used; no candidate met ai-orchestration §2.3\).
- The memory ownership gate is open \(owner of 0xbe000000-0xd4c00000, tail 0xafffff000-0xb00000000, internal reservations\), so the XNU handoff stays withheld.
- The DTB has no splash\_region and ABL consumption of the MemoryMapLib Display Reserved entry is unproven, so the splash reservation stays undecided; \[bootimg\] dtb remains unset, chip\_id is decided \(4acab8db\) and root\_match\_volume\_uuid waits for the userdata image.
- Window allocation is Medium risk, not High \(static analysis, not verified on hardware\): the RAM-partition protocol producer is unconfirmed, XNU's use of the ADT dram-base/dram-size is unconfirmed, and the first boot will show NO WINDOW/FREE lines without writing a partition if it fails. 6 live no-map regions are not in MemoryMapLib, and do not shrink owned\_memory\_size \(below about 925 MiB a first-fit window falls outside the ADT range; memory-number changes need user confirmation\).

### 下一步

- Boot the image on hardware to verify Tools -&gt; Advanced Logger and runtime dispatch; the boot-chain review concluded APPROVE WITH CONDITIONS on 2026-11-07, scoped to the first fastboot boot only, so it is not a release to boot \(see docs/step5-firmware.md\).
- Resolve the RAM Partition protocol producer \(gEfiRamPartitionProtocolGuid\) by binary reference-point analysis and the first DEBUG boot log; decide with the user whether to add the 6 live no-map regions to MemoryMapLib, and do not shrink owned\_memory\_size.
- First boot must use a DEBUG build and fastboot boot only \(no partition write; user authorisation in that round\), and SEC writing the entry parameters into the HOB \(UniXNURamDiskDxe.c:215-233\) must be confirmed first.
- The Verifier re-run passed on 2026-11-07 against device repository b1064eb8 and uefi-nuwa e494c01b; repeat it only if the firmware changes, and keep the recorded command and revisions with the result.
- Collect memory ownership evidence before the XNU handoff: the active owner of 0xbe000000-0xd4c00000, the 0xafffff000-0xb00000000 tail and the internal reservations.
- Wire bootimg.dtb and the ADT identity from the separate report, and inject a splash reservation only once ABL consumption is proven.

### 证据

- `source`: [Firmware input review plus build records: the DTB has no splash\_region while live reports 0xb8000000/0x2b00000 and MemoryMapLib has Display Reserved; ABL consumption is unproven and bootimg.dtb stays unset; the ADT chip\_id is decided \(4acab8db\) and root\_match\_volume\_uuid waits for the userdata image; the firmware build was independently re-run by the Verifier subagent on 2026-11-07 against b1064eb8/e494c01b: PASS \(0x300000-byte FV\), and the firmware has since started on hardware without reaching the menu \(three fastboot boot runs, header v1 never left the bootloader, header v4 reached DXE, PIL AUTO ABL panic fixed with a local uefipil.cfg, then ASSERT DxeMain.c\(581\) after AllocatePoolPages failures; see docs/step5-firmware.md\), and the boot-chain review concluded APPROVE WITH CONDITIONS on 2026-11-07 scoped to the first fastboot boot only \(deep not used\).](https://github.com/wh1stl3/UniXNU-nuwa/blob/19d675e52197ecba200677af9f3eea71a037628f/docs/step5-firmware.md)

## CPU 与中断 {#cpu}

`planned`

### 硬件与依赖

- Identify the cpu and interrupts hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for cpu and interrupts.

### 操作步骤

- Follow the cpu and interrupts stage in the porting guide and record the actual commands.

### 开发经验

- Reviewed CPU facts \(2026-11-07, docs/step5-firmware.md\): the live MPIDR Affinity1 values 0x000..0x700 for the eight cores and the 3x A510, 2x A715, 2x A710 and 1x X3 cluster mix agree with the board tree, and \[payload.adt\] cpu\_regs = 0,256,512,768,1024,1280,1536,1792 already encodes that numbering.
- Reviewed GIC facts: GICD 0x17100000 + 0x10000 and GICR 0x17180000 + 0x200000 with an 0x40000 stride match the live machine; the 3-cell versus 4-cell interrupt encoding difference is legal because ArmCpu mapGic does not read interrupt-cells, so addresses and encoding stay unchanged.
- Reviewed timer facts: the live PPI set 13,14,11,12 differs from the DTB's 13,14,11,10 only in the fourth entry, which is an EL2 interrupt. The current path is EL1 only and CNTV\_CTL \(INTID 27, PPI 11\) does not consume that entry, so the IRQ table is unchanged; the 19.2 MHz reference comes from a live property, not a CNTFRQ read-back.
- Live CPU re-check, 2026-11-07 \(docs/device-evidence-2026-11-07.md\): MIDR is 0x411fd461 on cpu0-2 \(A510\), 0x411fd4d0 on cpu3-4 \(A715\), 0x412fd470 on cpu5-6 \(A710\) and 0x411fd4e0 on cpu7 \(X3\); soc\_id 519, machine KALAMA, family Snapdragon, revision 2.0; the live FDT has cpu@0..cpu@700 \(eight nodes\), psci method smc and compatible arm,psci-1.0.
- Interrupt and timer re-check: GICD 0x17100000 + 0x10000 and GICR 0x17180000 + 0x200000 with redistributor-stride 0x40000 and \#interrupt-cells = 3; the timer node lists PPI 13,14,11,12 with clock-frequency 0x124f800 \(19.2 MHz\). At Android runtime arch\_timer appears as GICv3 virq 11 \(virtual timer PPI 11, matching ArmCpu INTID 27\); the firmware DTB fourth entry is 10 against the live 12 and the current EL1-only path does not consume it.
- CNTFRQ was not read back: the boot-time dmesg record had already wrapped in the ring buffer when the capture ran, so cntfrq\_readback stays unverified and the 19.2 MHz value remains a live DTB property, not a measured counter frequency.
- Collect the first cpu and interrupts observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU.

### 当前范围

- The reviewed differences are inert only on the EL1-only path; nothing in this area has run on hardware, so the CPU and interrupt records remain source-level.
- Hardware inputs and implementation are pending for nuwa.

### 下一步

- Keep the DTB PPI set and \[payload.adt\] cpu\_regs as recorded, and validate the EL1-only timer path on hardware once a firmware build exists.

### 证据

- `source`: [CPU, GIC and timer review: MPIDR 0x000..0x700 and the cluster mix agree; GICD/GICR addresses and 0x40000 stride agree with a legal cell-count difference; the fourth live PPI is EL2-only and unused, so no IRQ change.](https://github.com/wh1stl3/UniXNU-nuwa/blob/19d675e52197ecba200677af9f3eea71a037628f/docs/step5-firmware.md)

## 内存与 DMA {#memory}

`planned`

### 硬件与依赖

- Identify the memory and dma hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for memory and dma.

### 操作步骤

- Follow the memory and dma stage in the porting guide and record the actual commands.

### 开发经验

- Reviewed memory facts \(2026-11-07, docs/step5-firmware.md\): the board DTS geometry 0x8c0000000 + 0x240000000 \(9 GiB\) is supported by the live high-end pair of adjacent ranges, but the last 4 KiB \(0xafffff000-0xb00000000\) and the internal/dynamic reservations inside the range are still open.
- Reviewed memory facts: the current FD window 0xa7100000-0xa7400000 lies inside the historical ramoops 0xa7000000-0xa7400000, and the DXE heap 0xbae00000-0xbf300000 intersects the historical iomem reserved range 0xbe000000-0xd4c00000 whose active owner is unknown. board.toml address, size and verified values stay unchanged; neither permanent Linux reserved ownership nor a full SystemRAM release is inferred.
- The delivered conventional window comes from RAM Partition -&gt; HOB/EFI map -&gt; DarwinBoot conventional allocation, not from an automatic ADT subtraction of reserved ranges; the XNU handoff stays withheld until the reservation owner question closes.
- scripts/unixnu/devicetree.py accepts exactly one /memory node with one contiguous reg range, so the nine-segment TODO in dts/nuwa.dts was corrected as a comment-only change; the geometry and the owned-window contract are unchanged.
- Live FDT re-check, 2026-11-07 \(docs/device-evidence-2026-11-07.md\): ddr\_size reads 0xc \(12 GiB\) and /memory carries nine reg ranges: 0x80000000+0xe00000, 0x811d0000+0x56e30000, 0xd8140000+0x20000, 0xd8800000+0x0, 0xe7cb0000+0x18350000, 0x880000000+0x39d00000, 0x8c0000000+0xc0000000, 0x980000000+0x180000000 and 0x8b9f00000+0x1e00000. The high pair 0x8c0000000+0xc0000000 and 0x980000000+0x180000000 is adjacent and spans 0x8c0000000..0xb00000000 \(9 GiB\), matching the board DTS geometry 0x8c0000000+0x240000000.
- reserved-memory in the live FDT \(not an exhaustive list\): ramoops@0xa7000000 reg 0xa7000000+0x400000 with no no-map, so it is a real node rather than a placeholder; splash\_region 0xb8000000+0x2b00000 \(cont\_splash\_region\); xbl\_dt\_log@81a00000 0x81a00000+0x40000 with no-map; smem 0x81d00000+0x200000. The FD window 0xa7100000-0xa7400000 still falls inside the ramoops range: that is recorded as an observation only, with no conclusion about who owns the range today, no board.toml or DTS change, and neither a reservation nor a release implied.
- Still missing for the memory gate: evidence for the current firmware version's RAM Partition -&gt; HOB -&gt; EFI memory map -&gt; DarwinBoot window, which needs a UEFI log taken after fastboot boot-ing our own firmware.
- Static code reading by the main agent, not verified on hardware \(2026-11-07, docs/step5-firmware.md\): DarwinBoot's window check \(UniXNU/drivers/DarwinBoot/DarwinBootPkg/Driver/WindowSize.h:6-8\) requires an address in 0x10000000..0x200000000 with 2 MiB alignment and accepts owned\_memory\_size = 0x40000000; the WINDOW\_SIZE default of 256 MiB at DarwinBoot.c:20 is only the parse upper bound; AllocateWindow \(DarwinBoot.c:495-546\) searches only contiguous EfiConventionalMemory and, on failure, takes the NO WINDOW branch \(DarwinBoot.c:531-544\) that prints the NO WINDOW/FREE lines on screen; DarwinBoot.c:745-748 sets boot\_args PhysicalBase to the window address and MemorySize to WindowSize, so XNU's physical memory range comes from boot\_args rather than from the ADT.
- Static code reading by the main agent, not verified on hardware: the nuwa MemoryMapLib static table \(uefi-nuwa Platforms/Xiaomi/nuwaPkg/Library/MemoryMapLib/MemoryMapLib.c:9-35\) has one Conventional entry that also produces a HOB, the DXE heap 0xBAE00000+0x4500000 \(about 69 MiB\), and no high DDR above 0x8c0000000. RamManagerDxe maps RAM-range gaps not covered by the existing EFI map as EfiConventionalMemory with no address or size filter \(Silicon/Silicium/SiliciumPkg/Drivers/RamManagerDxe/RamManager.c:48-113\), ManageRam cleans up directly when the RAM range lookup fails \(:187-215\), its depex is TRUE \(RamManagerDxe.inf:26-27\), and QcomPkg.dsc.inc:30 overrides RamManagerLib with QcomPkg/Library/RamManagerLib, whose RamManager.c:57 returns an error when LocateProtocol\(gEfiRamPartitionProtocolGuid\) fails. The protocol bytes appear in the nuwa vendor Binaries/nuwa .efi files only once each in EnvDxe.efi and QcomBds.efi, neither in a depex, and the producer is unconfirmed; if the protocol is not installed when RamManagerDxe runs, no high memory is added and DarwinBoot reaches NO WINDOW. This is a silent failure point and is unverified.
- Static code reading by the main agent, not verified on hardware: no consumer of dram-base/dram-size exists in UniXNU/drivers or the SoC repository \(documentation only\), and whether the XNU patch side consumes them is unconfirmed; official docs/zh/devices/luming-infinityex-rsxq.md:174 requires comparing the firmware memory map, the DTS memory node, the ADT chosen dram-base/size and the DarwinBoot owned window. Inference \(unverified\): with a 1 GiB window the low Conventional fragments are likely too small, so a first-fit search would land near 0x8c0000000, and whether XNU accepts a window outside the ADT dram range is unknown. Public reference, not nuwa evidence: official docs/zh/devices/alioth.md:193/200/226 records a Mu-Silicium Qualcomm port with 8 GiB DRAM using a 4 GiB owned window, measured on hardware. The failure is benign: the NO WINDOW path only prints the memory map on screen and writes no partition.
- MemoryMapLib reconciliation \(static, 2026-11-07, docs/step5-firmware.md section 'MemoryMapLib reconciliation \(static\)'; static analysis, not verified on hardware\): the uefi-nuwa table \(MemoryMapLib.c:9-35\) has 41 entries, 27 inside the DDR range; the live FDT has 35 fixed-reg reserved regions, 6 of them no-map regions the table does not describe \(xbl\_ramdump\_region 0x81200000+0x280000, global\_sync\_region 0x82600000+0x100000, mpss\_dsm\_region 0xd4d00000+0x3300000, xbl\_sc\_region 0xd8100000+0x40000, hwfence-shmem 0xe6440000+0x2dd000, llcc\_lpi\_region 0xff800000+0x600000\). If RamManagerDxe pads every uncovered System RAM gap as EfiConventionalMemory, 16 fragments total about 10.80 GiB \(largest 0x8c0000000 + about 9216 MiB ending at 0xafffff000, then 0x880000000 + about 925 MiB, 0xe7cb0000 + about 379 MiB, 0xbf300000 + about 346 MiB, 0x82800000 + about 128 MiB\). A 1 GiB window therefore cannot fit any low fragment and a first-fit lands in the 0x8c0000000 fragment inside the ADT dram-base; shrinking owned\_memory\_size below about 925 MiB would move it to a low address outside the ADT range, so it must not be shrunk, and any memory-number change needs user confirmation. 'No reserved/gap overlap' is not safety evidence because System RAM already excludes no-map regions; the RAM Partition content is unknown.
- Reviewer verdict on the first fastboot boot \(2026-11-07, docs/step5-firmware.md section 'First fastboot boot: Reviewer verdict and conditions'; read-only static\): the window-allocation risk is Medium rather than High, APPROVE WITH CONDITIONS scoped to the first fastboot boot only, and Deep Reviewer was not used because no candidate met docs/ai-orchestration-2026-11-06.md §2.3. The failure path writes no partition \(EFI\_OUT\_OF\_RESOURCES at DarwinBoot.c:531-545; the Fail path prints boot refused and the on-screen NO WINDOW/FREE lines at :534-541\), and the success path prints pa/va/entry/args/owned \(:785-790, :797-811\). XNU's physical range comes from boot\_args \(DarwinBoot.c:745-748\), so the earlier 'window outside the ADT DRAM' premise is withdrawn; whether dram-base/dram-size has an XNU-side consumer is unconfirmed. The gEfiRamPartitionProtocolGuid producer stays unresolved \(RamManagerDxe is not in apriori, Depex = TRUE, runs in FV order at nuwa.fdf:87\).
- Unresolved Medium hypothesis: MemoryMapLib was inherited from sheng and not reconciled item by item with nuwa; if the RAM Partition reports a no-map region that the table lacks as RAM, it would be padded as Conventional and used by DXE, giving a wrong access or reboot rather than flash corruption. The RAM Partition contents are unknown, so no conclusion is drawn.
- Collect the first memory and dma observation, its cause when established, and the resulting implementation decision.

### 完成条件

- All handoff regions are accounted for and each enabled DMA engine accesses its allocated range with the documented cache policy.

### 当前范围

- XNU handoff is withheld: the tail 4 KiB and the internal/dynamic reservations of the 9 GiB range are unclosed, and the owner of the 0xbe000000-0xd4c00000 reserved range that the DXE heap intersects is unknown.
- No board DTS register set for DMA, storage, display, input and power yet, so those components stay unselected.
- Window allocation is Medium risk, not High \(static analysis, not verified on hardware\): the gEfiRamPartitionProtocolGuid producer is unconfirmed and XNU's use of the ADT dram-base/dram-size is unconfirmed; the first boot will show NO WINDOW/FREE lines and write no partition if it fails. 6 live no-map regions are not in MemoryMapLib, and whether the RAM Partition reports them as RAM is unknown; adding them is a user decision. Do not shrink owned\_memory\_size: below about 925 MiB a first-fit window falls outside the ADT dram-base, and any memory-number change needs user confirmation.

### 下一步

- Resolve the RAM Partition protocol producer \(gEfiRamPartitionProtocolGuid\) by binary reference-point analysis of InstallProtocolInterface versus LocateProtocol and by the first boot's DEBUG log, because RamManagerDxe's LocateProtocol failure is silent.
- Decide with the user whether to add the 6 live no-map regions not described by MemoryMapLib to the static table; do not shrink owned\_memory\_size \(a low first-fit window would fall outside the ADT dram-base\).
- First boot must use a DEBUG build and fastboot boot only \(no partition write; device action needs user authorisation in that round\), then read the DarwinBoot screen text and the DXE-stage AdvancedLogger page, and confirm SEC writes the entry parameters into the HOB \(UniXNURamDiskDxe.c:215-233\).
- Close the High-memory gate: identify the active owner of the historical 0xbe000000-0xd4c00000 reserved range \(DXE heap 0xbae00000-0xbf300000\), account for the 0xafffff000-0xb00000000 tail and the internal reservations, then re-check the FD/ramoops overlap before allowing the XNU handoff.

### 证据

- `source`: [Memory High-gate review: the 9 GiB geometry is supported by the live high ranges, the tail 4 KiB and internal reservations are open, the FD/ramoops and DXE-heap/reserved overlaps are unresolved, and the delivered window is a DarwinBoot conventional allocation rather than an ADT subtraction.](https://github.com/wh1stl3/UniXNU-nuwa/blob/19d675e52197ecba200677af9f3eea71a037628f/docs/step5-firmware.md)

## 存储与根卷 {#storage}

`planned`

### 硬件与依赖

- Identify the storage and root hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for storage and root.

### 操作步骤

- Follow the storage and root stage in the porting guide and record the actual commands.

### 开发经验

- Launch route B decided 2026-11-06 \(docs/launch-route-2026-11-06.md\): bring-up runs from fastboot boot \(route A, no partition writes\), then the end state is the native UFS root with the userdata partition flashed as the root volume. B needs \[userdata\] LBA geometry from this board's GPT, root\_match\_volume\_uuid from the built userdata image, native-ufs-root=1, CONFIG\_XNU\_NATIVE\_UFS=y and the ShengUfs component; the flash overwrites Android data and requires explicit user authorisation.
- Repo hygiene: removed the committed \_\_pycache\_\_ copies of the format-1 legacy tooling; no source behaviour changes.
- Payload source decided 2026-11-07 \(docs/launch-route-2026-11-06.md, subsection in section 1\): route B keeps taking the boot payload \(kernel, ADT, trustcache and unixnu.toml inside the RamDisk\) from fastboot boot and does not flash boot.img into the boot partition. Observed: fastboot boot writes no partition, so the payload lives only for that boot. Inferred: every boot needs a host-supplied boot.img, and a device reboot returns to the Android boot partition instead of entering UniXNU, so the launch-route section 1 statement that a reboot goes straight into UniXNU and the host-free standalone boot end state do not hold today; standalone boot would need a separate decision plus explicit authorisation to flash boot. userdata remains the persistent root volume and flashing it still needs per-round authorisation; fastboot boot still needs a user confirmation before any device action.
- Read-only GPT capture, 2026-11-07 \(docs/device-evidence-2026-11-07.md\): six LUNs sda..sdf are present and report 4096-byte logical and physical block sizes; userdata is sda32 with first\_lba 3110976 and last\_lba 61850618, 58739643 LBAs = 240597577728 bytes \(about 224 GiB\) at 4096 bytes per LBA, and its last\_lba equals that disk's last usable LBA; peer entries are super sda31 751680..3110975, metadata sda17 16384..32767, persist sda18 32768..49151, boot\_a sde14 149126..198277 \(49152 LBAs = 201326592 bytes = 192 MiB\), vendor\_boot\_a sde24 217670..242245, abl\_a sde11, modem\_a sde7 and xbl\_a sdb1. board.toml \[userdata\] records the geometry; no GUID, serial or kernel command line is recorded.
- Unit trap: GPT LBAs are 4096-byte units taken from the GPT header parsed on the host, while /sys/block/\*/size and blockdev --getsz report 512-byte sectors, so the two must not be mixed without conversion \(a factor of 8; for sda 61850624 x 4096 = 494804992 x 512\). sda declares 32 GPT entries with usable LBAs 6..61850618. The recovery image does not support sgdisk -p \(invalid option -p\), so the GPT header and entry array were copied with dd to the host and parsed there; the device was only read.
- Collect the first storage and root observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Host: register, clock, link and SMMU facts match the board inventory.
- Reads: SCSI capacity, GPT and known blocks are correct; OS/SystemOS windows stay within userdata.
- Root: the configured volume mounts and launchd starts. Persistence: writes survive reboot within the allocated Data region.

### 当前范围

- Route B is partly unconfigured: the \[userdata\] LBA geometry is now measured and recorded in board.toml, but the root volume UUID \(only available once the root image is built\), the ShengUfs/archives inputs and the storage ABI inputs are still missing, so only route A \(RAM boot\) runs today.
- Hardware inputs and implementation are pending for nuwa.

### 下一步

- Inventory the required storage and root inputs before implementation.
- Keep bring-up on fastboot boot and do not flash boot.img; revisit host-free standalone boot only on a separate user decision plus explicit authorisation to flash boot.
- Flash timing confirmed 2026-11-07 \(docs/launch-route-2026-11-06.md section 8\): flashing userdata only validates persistence and comes after all first five bring-up stages, none of which writes a partition. Order: \(1\) firmware builds, memory ownership gate has evidence, and the boot-chain handoff passes independent review \(after the Astra High channel recovers\); \(2\) first fastboot boot observing UEFI, menu, payload and DarwinBoot, with the firmware log exported through the Tools QR path; \(3\) kernel entry through to platform expert; \(4\) read-only storage validation of the UFS controller, capacity, GPT and known data blocks, with the OS/SystemOS windows inside userdata; \(5\) build the root volume image, take the root UUID, check hashes and reach launchd on the in-memory boot path; \(6\) flash userdata and validate persistence. Before flashing, confirm item by item: the first five stages have real log evidence, the \[userdata\] geometry comes from a real read rather than an estimate, and the user has a usable stock fastboot package and confirms the Android data is no longer needed; the exact partitions, commands and impact are stated beforehand and executed only after explicit approval in that round. The boot partition is not flashed because the user decided to keep fastboot boot.

### 证据

按下一步操作收集证据。

## 显示 {#display}

`planned`

### 硬件与依赖

- Identify the display hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for display.

### 操作步骤

- Follow the display stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first display observation, its cause when established, and the resulting implementation decision.

### 完成条件

- A known frame appears with correct geometry and colors, then userland presentation and backlight controls work.

### 当前范围

- Hardware inputs and implementation are pending for nuwa.

### 下一步

- Inventory the required display inputs before implementation.

### 证据

按下一步操作收集证据。

## 输入 {#input}

`planned`

### 硬件与依赖

- Identify the input hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for input.

### 操作步骤

- Follow the input stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first input observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive, and buttons produce expected HID reports.

### 当前范围

- Hardware inputs and implementation are pending for nuwa.

### 下一步

- Inventory the required input inputs before implementation.

### 证据

按下一步操作收集证据。

## GPU {#gpu}

`planned`

### 硬件与依赖

- Identify the gpu hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for gpu.

### 操作步骤

- Follow the gpu stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first gpu observation, its cause when established, and the resulting implementation decision.

### 完成条件

- GPU submissions complete, mapping/fence handling is correct, a known image renders, and the selected Metal client presents it.

### 当前范围

- Hardware inputs and implementation are pending for nuwa.

### 下一步

- Inventory the required gpu inputs before implementation.

### 证据

按下一步操作收集证据。

## 网络 {#network}

`planned`

### 硬件与依赖

- Identify the network hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for network.

### 操作步骤

- Follow the network stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first network observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Scanning, association, address configuration and sustained receive/transmit traffic pass with the selected firmware.

### 当前范围

- Hardware inputs and implementation are pending for nuwa.

### 下一步

- Inventory the required network inputs before implementation.

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`planned`

### 硬件与依赖

- Identify the audio hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for audio.

### 操作步骤

- Follow the audio stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first audio observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Each declared route carries the selected audio format through playback or capture and handles start/stop correctly.

### 当前范围

- Hardware inputs and implementation are pending for nuwa.

### 下一步

- Inventory the required audio inputs before implementation.

### 证据

按下一步操作收集证据。

## 电源 {#power}

`planned`

### 硬件与依赖

- Identify the power hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for power.

### 操作步骤

- Follow the power stage in the porting guide and record the actual commands.

### 开发经验

- Repo hygiene: removed the committed \_\_pycache\_\_ copies of the format-1 legacy tooling; no source behaviour changes.
- Collect the first power observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Declared power controls and battery readings match observations; each claimed sleep/resume transition restores its dependent peripherals.

### 当前范围

- Hardware inputs and implementation are pending for nuwa.

### 下一步

- Inventory the required power inputs before implementation.

### 证据

按下一步操作收集证据。

## 镜像组装 {#packaging}

`planned`

### 硬件与依赖

- Identify the image assembly hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for image assembly.

### 操作步骤

- Follow the image assembly stage in the porting guide and record the actual commands.

### 开发经验

- Repo hygiene: removed the committed \_\_pycache\_\_ copies of the format-1 legacy tooling; no source behaviour changes.
- Format-2 migration: scripts/package.sh taken unmodified from the official template; patches/xnu/series created empty; package/ documents the empty device package.
- Collect the first image assembly observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Kernel and prelink succeed, payload contains all declared inputs, and the boot image matches the bootloader format and size limit.

### 当前范围

- Hardware inputs and implementation are pending for nuwa.

### 下一步

- Inventory the required image assembly inputs before implementation.

### 证据

按下一步操作收集证据。

## 诊断 {#diagnostics}

`planned`

### 硬件与依赖

- Identify the diagnostics hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for diagnostics.

### 操作步骤

- Follow the diagnostics stage in the porting guide and record the actual commands.

### 开发经验

- unixnu.lock committed from the first complete fetch of the iOS 16 profile: xnu 1b191cb5 \(8796.141.3\), sm8550 a9f45dc6, edk2 cfb93724, libplatform a00a4cc3, libdispatch 30fe6a7d, libpthread c0e60fb5, AvailabilityVersions 933f9360, corecrypto-2023 11fba65b, IOStorageFamily e45fbe30.
- The Tools entry is enabled in the payload configuration \(\[payload\] tools = true in board.toml\); the firmware log exporter now has a producer \(Advanced Logger wired in uefi-nuwa e494c01b2f679439fdaeaf2084b693c7220543f5, built; independently re-run by the Verifier subagent on b1064eb8/e494c01b\), but the Tools -&gt; Advanced Logger page and its runtime dispatch are unverified and the entry has not been exercised on hardware.
- Step 5 platform facts are recorded in docs/step5-firmware.md with provenance only: the backups MANIFEST is read before any other file, then recovery-cpu-20261021T005937467055Z/&\#123;running-fdt.dts,iomem.txt,cpuinfo.txt&\#125;, legacy-nuwa-artifacts/platform-inputs/20261020T124109389461Z/nuwa-platform-observed.json and memory-layout/nuwa-layout-tmlq93uo/report.json. No raw dump, device identifier, serial or seed is copied, and the archives were not re-scanned this round.
- This review ran no host command and touched no device, so it adds no host or device evidence; the report is a source-level record of an independent review \(UniXNU 693f5d9cae8a408dd18b39f3f9fdc4228c934241, device 279c990a0c7a238aa0a5818493c6cd6a46528749, SoC a9f45dc60c035084b95463781538380f4c3606c9, uefi-nuwa 322d742fd87d370aac96bb394d1feac61beb9b3a\).
- Recovery reader confirmed read-only on 2026-11-07 \(docs/device-evidence-2026-11-07.md\): a TWRP 3.7.1\_12 recovery with a root adb shell provides adb, dd, cat of /proc and /sys, dmesg and blockdev --get\*, so a recovery+adb log reader is available in practice; the only tooling gap seen was sgdisk -p, which that image does not support. The capture wrote no partition and ran no fastboot command.
- pstore backend observed: /dev/pmsg0 exists while /sys/fs/pstore is empty, so the Android kernel has a ramoops backend; whether ramoops contents survive a warm reboot was not tested, and the ramoops address range is the one whose overlap with the FD window is recorded in the memory area as an observation only.
- Collect the first diagnostics observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Each claimed milestone has a reproducible command, a matching source/image revision and an accessible result.

### 当前范围

- The Tools entry is configured and the Advanced Logger producer is wired \(uefi-nuwa e494c01b2f679439fdaeaf2084b693c7220543f5\); it was built and independently re-run by the Verifier subagent on b1064eb8/e494c01b; run-time unverified, so the Tools -&gt; Advanced Logger page is still unverified at runtime, the 4 MiB buffer placement is an assumption and the rework has no independent boot-chain review.
- The recorded platform facts are source-level only and carry no host or device verification.
- Persistent kernel logging is unavailable until the route B ShengUfs storage driver works: the log region is a reservation inside userdata, and although the \[userdata\] GPT geometry is now measured, no region has been reserved and no writer or reader is implemented.
- The log reader is still unselected between a minimal Linux image and recovery+adb, but the recovery option is no longer unknown: TWRP 3.7.1\_12 with root, adb, dd and blockdev reads the device read-only, and only sgdisk -p is unavailable.
- Unverified hypothesis, not a conclusion: historical evidence shows an Android ramoops region at 0xa7000000-0xa7400000, so a kernel log kept across a warm reboot could be read from Android /sys/fs/pstore without the storage driver; the current FD window 0xa7100000-0xa7400000 lies inside that region and the memory ownership gate is open, and there is no evidence whether a reboot clears DRAM.
- Writing the reserved log region is a device write and needs explicit user authorisation in the round that performs it.

### 下一步

- Re-run the record and diff checks after the commit, and add host or device evidence only when an actual build or device run produces it.
- User decision \(2026-11-07\): after the kernel checkpoint, capture kernel logs persistently instead of repeated screen colour-band or hex recordings, following docs/zh/porting/log-capture.md sections 4-6: reserve a log region inside userdata, connect the kernel writer to the storage driver's ranged read/write/sync path, and read it back with a minimal Linux image or a recovery+adb reader, with the writer, reader and host decoder sharing one block unit and byte range.
- Until the route B ShengUfs storage driver works, keep the firmware Tools -&gt; Advanced Logger QR export plus serial/screen checkpoints; the \[userdata\] first\_lba/last\_lba/lba\_bytes geometry is already recorded in board.toml, so the remaining step is to choose and reserve the log region inside it; reference the official UniXNU-sheng package/BootLog.c, BootReset.c and package/linux-log/ for structure only, because its PMIC addresses and watchdog calls are sheng board values that nuwa must replace with its own evidence. The Advanced Logger producer is now wired \(uefi-nuwa e494c01b2f679439fdaeaf2084b693c7220543f5\), so the next check is the runtime Tools -&gt; Advanced Logger page on hardware.

### 证据

- `source`: [Step 5 report with provenance: MANIFEST-first backup order, the three observation inputs and the memory-layout report named, no raw identifiers or seeds copied, and no host or device verification claimed.](https://github.com/wh1stl3/UniXNU-nuwa/blob/19d675e52197ecba200677af9f3eea71a037628f/docs/step5-firmware.md)

## cellular {#cellular}

`planned`

组件: `QcomBaseband`.

### 硬件与依赖

- Modem firmware and EFS/NV images extracted from the device.
- QRTR/QMI channel and IPA/QMAP data path evidence from the vendor DTS.

### 配置

- board.toml and DTS entries for the modem, plus the kernel command line switches selected for it.

### 操作步骤

- Follow the baseband guide after storage, display and input are device-verified.

### 开发经验

- No modem evidence recorded yet; SM8550 shared support does not carry this board's modem firmware. package/README.md added by the format-2 migration.
- proprietary-files.txt now lists only the Binaries/nuwa DXE set from the public Device-Binaries repository; no modem firmware or EFS/NV input is recorded in it yet.

### 完成条件

- SIM identity, network registration and a data session are observed on the device.

### 当前范围

- Planned; outside the first boot milestone.

### 下一步

- Extract modem firmware and EFS inputs, then record QRTR/QMI channels from the vendor DTS.

### 证据

按下一步操作收集证据。

</div>
