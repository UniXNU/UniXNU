# 小米平板 5 Pro 5G（enuma）

[wh1stl3/UniXNU-enuma](https://github.com/wh1stl3/UniXNU-enuma)

<div v-pre>

Xiaomi Pad 5 Pro 5G \(SM8250-AC\) iPadOS 17.7.11 bring-up. Format 2 migration started 2026-11-06: device repo + UniXNU-sm8250-common + uefi-enuma. Every area is planned until hardware evidence is recorded.

源记录: [porting.toml](https://github.com/wh1stl3/UniXNU-enuma/blob/74dc21dd5c323a763a225f98a6eefc3815272046/porting.toml), `74dc21dd5c323a763a225f98a6eefc3815272046`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `planned` |
| [固件与启动](#firmware) | `implemented` |
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

组件: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`, `DarwinBoot`.

### 硬件与依赖

- FFT-infra/UniXNU-sm8250-common at 166235ec2480ff0992627b7aafa15c65ce6b4efa.
- Vendor DTS for SM8250-AC register, interrupt and clock values.
- A device-verified memory map for \[payload\] dram\_size and the board DTS memory nodes.

### 配置

- board.toml schema\_version = 2 with \[board\], \[components\], \[kernel\], \[device\_tree\], \[firmware\], \[ipsw\], \[payload\], \[payload.adt\], \[package\].
- feeds.toml and unixnu.lock pin FFT-infra/UniXNU-sm8250-common at 166235ec2480ff0992627b7aafa15c65ce6b4efa.
- dts/enuma.dts includes soc:dts sm8250.dtsi; no unverified addresses are written.

### 操作步骤

- ./unixnu defconfig enuma\_defconfig -D ../UniXNU-enuma
- ./unixnu fetch -D ../UniXNU-enuma
- ./unixnu status --json -D ../UniXNU-enuma
- ./unixnu tree -D ../UniXNU-enuma

### 开发经验

- 2026-11-09: board.toml \[kernel\] config\_fragments gains "os:configs/ipados.config" and patch\_series gains a device-local OS layer \(patches/xnu/os-series\) that omits zzz-boot-progress.patch and keeps the two XnuPrelink ABI patches \(security-init + sparse-index\); the omitted patch needs the sheng XNU\_SHENG\_PMGR hook enuma does not select, per the upstream sm-t970 device record. The resolved set is 60 patches \(56 arch + 2 soc + 2 os\).
- 2026-11-07: corrected stale skeleton/feed notes and enabled payload Tools for the planned firmware logger. No new hardware driver is selected.
- Upstream HEAD check: UniXNU 10edc1efeeabc8c180b1a3ad9f96b7c8e36a385e, uefi-sheng 66421cb7bb5694843aec8de1ca3d1de4c20cca38, kona 166235ec2480ff0992627b7aafa15c65ce6b4efa. Independent UniXNU clone failed with TLS EOF; API comparison shows steps/log-capture unchanged. Existing pins remain active pending a successful isolated upgrade review.
- Repo hygiene: removed committed \_\_pycache\_\_ copies; format-1 legacy scripts are not part of the official flow.
- The official tree ships no SM8250 common repository; this board adopts FFT-infra/UniXNU-sm8250-common pinned at 166235ec \(alioth record used a6e7e36c\).
- The shared layer covers common registers, GIC, timer, CPU topology and controller bases; enuma CPU/GPU OPP, power votes and thermal zones stay board-owned.
- SM8250-AC is Snapdragon 870; the public device index archives it under the SM8250 family name.
- alioth \(Redmi K40\) is SM8250-AC \(Snapdragon 870\), the same SoC bin as enuma, not 865; its board-specific CPU/GPU votes remain non-portable to enuma.
- 2026-11-08: board.toml \[firmware\] submodules is commented out because the firmware inputs \(Mu\_Basecore, openssl, Common/Mu\) are hand-placed at their gitlink commits and git submodule update --init fails on a non-empty openssl directory; no other board.toml value changed. See the firmware area for the build evidence.
- 2026-11-08 device run \(user authorised, filmed; media in .cache/media, not in repo\): fastboot boot of stage12-simplefb/boot.img \(sha256 ef7822890e993e49a2d921b008f0bbb82db86c18894642b53ae37d1760096dca, firmware source 1070b371e95bf59cfc6f955a37fec3c26ad2e804\) walked SEC -&gt; DXE -&gt; BDS -&gt; the UniXNU built-in menu: MMU 48 regions / map valid / enabled, SEC entry x0 = 0xAFDFE000 \(the FDT handed by ABL, 980226 bytes, inside the Kernel reservation\), UFS INQUIRY SAMSUNG KLUEG8UHDC-B0E1, menu Return to firmware / Restart / Power off / Tools with countdown, volume keys move and power key confirms, Tools &gt; Advanced Logger QR carousel works. Not reached: \[payload\] is not built, bring-up stage 3 onward is untested, and the memory-reservation preservation clause is not yet device-verified \(hence implemented, not device-verified\).
- 2026-11-08 stage 3 \(payload\): \[payload\] dram\_size = 0x200000000 \(8 GiB; RamManagerDxe mapped 0x80000000-0x280000000 on device\). \[payload.adt\] chip\_id = 958bdc0f is a locally generated 32-bit software identity value \(not the hardware ECID and not the donor chip-id\); the platform seed stays in the git-ignored build config, never in the repository. root\_match\_volume\_uuid is commented out for stages 1-5 and is backfilled at stage 6 from the built userdata root volume UUID. dts/enuma.dts now declares one enabled memory node \(0x80000000, 0x200000000\).
- 2026-11-09 stage 3 first device run \(user authorised, filmed; media .cache/media/stage3-20261109T004402, git-ignored\): fastboot boot of out/enuma/stage3/boot.img \(sha256 141eaa7eacaa5865bb852cb435124a38b43abf92715de2609e7005297f32b7bb, 203505664 B, header v1, ramdisk = 192 MiB FAT payload; firmware source 1070b371e95bf59cfc6f955a37fec3c26ad2e804, same FD and candidate DTB as stage12-simplefb\) pushed in 4.5 s and returned OKAY with no partition flashed. The menu appeared and the board.toml \[payload\] dram\_size / \[payload.adt\] chip\_id and the dts memory node values now boot on device. The default UniXNU item counts down 3 s then calls DarwinBoot and shows Load Error \(32-byte placeholder kernel, expected, no kernel handoff\). Configuration stays capped at implemented \(not device-verified\): the ramdisk/FDT placement and the DarwinBoot window are stage-4 questions.
- 2026-11-09 stage 4 first device run \(user authorised, filmed; media .cache/media/stage4-20261109T181331, git-ignored\): fastboot boot of out/enuma/stage4-log/boot.img \(sha256 056a095f69876c552f2e71ebfb41fced08642032d04ff02e10e8302ed3eac1ac, 203505664 B, header v1, ramdisk = 192 MiB FAT payload; firmware source uefi-enuma fix/unixnu-debug-level commit 4db39e8fac0e6d76a1f0e9968e51f06f9b81e271, new FD sha256 e524988b8a05f15847ffc991170de8a5e0ead607400421e0835084497a71bf1e\) returned OKAY with no partition flashed. The same board.toml values that booted stage 3 \(dram\_size 0x200000000, chip\_id 958bdc0f, dts memory node\) now boot the real kernel to the DarwinBoot hand-off \(UNIXNU: menu: timeout, booting default 0 -&gt; UNIXNU: boot: entry 'xnu' \(UniXNU\) -&gt; DARWINBOOT: hand-off to the kernel -&gt; Exiting boot services, green bar\). Configuration stays planned \(not implemented\): the XNU entry and MMU enable are not yet proven.

### 完成条件

- All source pins resolve; every selected component has a record; status shows the intended overrides and patch order.

### 当前范围

- Board DTS has no verified memory or peripheral wiring; shared kona resources do not establish enuma reservations or AC power policy.

### 下一步

- Extract enuma vendor DTS and reconcile board memory and wiring before extending dts/enuma.dts.

### 证据

- `device`: [fastboot boot OKAY \(push 4.5 s\), no partition flashed. Log shows 'UNIXNURAMDISK: initrd block device 0xA3FFF000 size 0xC000000 Success' then '\[Bds\]Booting UniXNU', UniXNU.efi loaded, FAT mounted; no 'no initrd in /chosen', no ASSERT, no NO WINDOW. Menu default UniXNU item counts down 3 s then Load Error \(32-byte placeholder kernel, expected\). Confirms the board.toml \[payload\] dram\_size / \[payload.adt\] chip\_id and the dts memory node values boot on device.](https://github.com/wh1stl3/UniXNU-enuma/blob/74dc21dd5c323a763a225f98a6eefc3815272046/docs/firmware-log-capture.md)
  Command: <code>fastboot -s &lt;enuma&gt; boot out/enuma/stage3/boot.img</code>. Revision: `bf4eeffdde548ffafa813062bfaac52c01d38d56`.
- `device`: [fastboot boot OKAY, no partition flashed. Reached the DarwinBoot hand-off \(DARWINBOOT: hand-off to the kernel -&gt; Exiting boot services, green bar\), confirming the stage-4 board.toml values \(\[payload\] dram\_size, \[payload.adt\] chip\_id, dts memory node\) boot a real kernel. Does not prove the XNU entry executed or the MMU was enabled.](https://github.com/wh1stl3/UniXNU-enuma/blob/74dc21dd5c323a763a225f98a6eefc3815272046/docs/firmware-log-capture.md)
  Command: <code>fastboot -s &lt;enuma&gt; boot out/enuma/stage4-log/boot.img</code>. Revision: `829cf6a491ec2af86dc086410eea46d57b937408`.

## 固件与启动 {#firmware}

`implemented`

### 硬件与依赖

- Identify the firmware and boot hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for firmware and boot.

### 操作步骤

- Follow the firmware and boot stage in the porting guide and record the actual commands.

### 开发经验

- 2026-11-09: board.toml \[kernel\] config\_fragments/patch\_series changed for the stage-4 kernel build \(kernel layer only; no \[firmware\] key or firmware path changed, FD/DSC/preflight untouched\).
- 2026-11-07: preflight now rejects TODO REQUIRED and REQUIRED\_ENUMA markers even when copied FD values agree; missing memory map, invalid FD integer types and block misalignment are explicit failures. Five synthetic checks passed; the real skeleton still fails as expected.
- enumaPkg and Resources/Configs/enuma.toml derive from pipaPkg: KonaPkg, SOC\_TYPE = 2. FD, stack, memory map and SKU remain unverified placeholders.
- Binaries/enuma and firmware DTB are absent. Firmware .gitignore now excludes the cache, enuma vendor directory and generated DTB; a malformed UTF-8 ACPI comment was repaired.
- Gic-Spurious.patch remains configured; check application against the pinned edk2 tree at the first firmware build.
- 2026-11-07: enuma.dsc/enuma.fdf now carry UniXNU, UniXNUDxe, UniXNURamDiskDxe, DarwinBoot and AdvancedLogDxe, UniXNULib, PcdUniXNUDeviceModel = enuma, and per-module-type AdvancedLoggerLib mappings \(SEC PeilessArm, DXE\_CORE, DXE/UEFI driver and application, runtime\) with the logger buffer left dynamic \(PcdAdvancedLoggerBase stays 0\). Static source wiring only: no edk2 build was run, and in RELEASE DebugLib stays null so no firmware log is collected.
- Submodule gitlinks were restored in uefi-enuma \(the repo had .gitmodules but no gitlinks\) from the git tree of its baseline UniXNU/uefi-sheng 66421cb7bb5694843aec8de1ca3d1de4c20cca38: Common/Mu b8d46c71610318e36a661819e1e3c0b8bdda413a, Common/Mu\_OEM\_Sample b70b4b7bb02c43bf9db2172dfb3ed0457e2361d6, Silicium-ACPI 2d465ad77c25de908f0ec7bdfcb57f865b61233c, Mu\_Basecore cfb93724a06ff86ff5ba971413368a7809ee42a5 \(equals the edk2 pin in unixnu.lock\), openssl 67b5686b4419b4cb8caa502711c41815f5279751, Binaries a1501e0c2e642d6ac0d8f52c85af2a67b75a7799. Common/Mu and Common/Mu\_OEM\_Sample and Silicium-ACPI are checked out at those commits and the AdvLoggerPkg/QrEncoderLib instances named in enuma.dsc exist there; Binaries stays uninitialised because enuma vendor inputs come only from .cache/firmware; Mu\_Basecore and openssl are not checked out yet.
- 2026-11-07: scripts/enuma\_firmware\_inputs.py staged vendor\_boot\_a.img \(sha256 3da202d0c9a5b618b61cd1923e87810536c5f70c9da7875de80075290641daba, 100663296 B\) and pre-root fdt.stdout \(sha256 45a04e08f47245ca5ec4145faf35346e36c014e8425b7cad470a299a98f12472, 941659 B\) into .cache/firmware/ from the read-only backup \(backup-manifest §E\); measured provenance recorded in proprietary-files.txt.
- vendor\_boot v3 header: page 4096, vendor ramdisk 2230, dtb 1613832 at offset 8192. Structural DTB boundary walk \(advancing by each FDT totalsize, not a blind magic scan\) yields 4 dtc-clean blobs: kona v1/v2/v2.1 SoC base DTBs \(msm-id 0x164 subtype 0x10000/0x20000/0x20001, all board-id 0x00\) plus a 173-byte MP\_DATA blob. No board-id 0x2e candidate, so vendor\_boot carries no enuma board DTB.
- No XBL was in the backup, so on 2026-11-07 xbl\_a, xbl\_config\_a, abl\_a, dtbo\_a and imagefv\_a were read back from the connected rooted enuma with scripts/enuma\_live\_collect.py \(read-only, device-checked whitelist, host sha256 equals on-device sha256sum for all five, no device writes\); xbl\_a \(sha256 7ac67cbf4c7870a972cb4ffd9cc09d5db1c96b7f4a5abc7a80c0da9cabc65057\) equals the EXPECTED hash of scripts/extract\_enuma\_xbl.py. The community stock package xbl.img differs \(b82a5a00...\) and is not used for imports. Binaries/enuma is still not populated pending the extraction review.
- Board DTB candidate: dtbo\_a holds 29 overlay entries; entry 07 is xiaomi enuma \(board-id 0x2e, sha256 ba188a895780a100fa8be3bb9622b0b5d8e1a4b6ad3821260476029251c6362f\) and adds the k81\_42\_02\_0a\_dual\_cphy\_video panel that the live bootargs select. fdtoverlay of vendor\_boot blob0 \(kona v2.1, msm-id 0x164/0x20001\) plus entry 07 gives sm8250-xiaomi-enuma.dtb \(sha256 42d36a005024e1a7c55cb5da077a13bb17e9fb9a79dc9dfac8a61cf1e182f698\); its /reserved-memory \(35 nodes\) is identical to the live FDT and only the root board-id/model, /memory and vendor fstab status differ. Host-checked against one earlier live FDT dump, not booted.
- Astra High pre-logger review \(identifier ses\_e4e61aafcffeyH5oBsTu0pSMYe, not a git revision; firmware base a7c434cdd86d2bb503cd0a726f6b1018cf969be6, UniXNU 693f5d9cae8a408dd18b39f3f9fdc4228c934241\): source-only wiring PASS WITH CONDITIONS, never build/boot approval. Shared UniXNURamDiskDxe PublishInitrd 169-191 rounds the initrd size to 512 and RamBlockRead 90-95 exposes that padding without a verified owned extent/overflow check \(up to 511 B past the declared end\); not fixed in this device task.
- 2026-11-08: firmware builds \(DEBUG, CLANGPDB, preflight included\). Command \(WSL, cwd=/mnt/d/Code/PortingiOS/UniXNU\): ./unixnu build firmware -D ../enuma/UniXNU-enuma --uefi ../enuma/uefi-enuma --edk2 \~/enuma-fw/mu\_basecore \(PATH includes \~/.local/bin python3.11\), exit 0; product Build/enumaPkg/DEBUG\_CLANGPDB/FV/SILICIUM\_UEFI.fd = 3145728 B = 0x300000, matching the \[uefi\_fd\] size. Host-verified only for 'compiles', self-checked by the implementer; not independently re-run by the Verifier; no device evidence, so not device-verified.
- 2026-11-08 inputs pinned: Mu\_Basecore cfb93724a06ff86ff5ba971413368a7809ee42a5 \(WSL ext4 \~/enuma-fw/mu\_basecore, libfdt/mipisyst/brotli/libspdm submodules at their gitlinks\); openssl 67b5686b4419b4cb8caa502711c41815f5279751 \(archive, embedded commit matches, sha256 f7c4a5e19fa02056e2bff4240bf474a3935207eb8fce6ee56175350acc6e2c32\); Common/Mu b8d46c71610318e36a661819e1e3c0b8bdda413a.
- 2026-11-08: board.toml \[firmware\] submodules commented out because the inputs are hand-placed at gitlink commits and submodule update --init fails on a non-empty openssl dir; a fresh environment places inputs by gitlink commit. uefi-enuma \(bec84f0ad9ab167ed08d0ce2ff46ab8cd2d15610\) uses the enuma XBL flat vendor module paths, drops 19 modules absent from enuma XBL and 37 USE\_CUSTOM\_DISPLAY\_DRIVER=0 panel XMLs, resets via vendor ResetRuntimeDxe, and adds \[Rule.Common.DXE\_RUNTIME\_DRIVER.BINARY\].
- 2026-11-08: preflight DTB check now looks for the candidate in the device repo .cache/firmware/dtb/sm8250-xiaomi-enuma.dtb \(candidate sha256 42d36a005024e1a7c55cb5da077a13bb17e9fb9a79dc9dfac8a61cf1e182f698, UNVERIFIED\); pipa/alioth/sheng FDF FdtBlob are comments so the DTB rides bootimg append\_dtb.
- 2026-11-08: scripts/enuma\_vendor\_import.py now allows re-import over committed EnumaInputs/\*.inc \(the git-tracked guard was removed\); the per-file 'differing content -&gt; refuse unless --force' protection is kept. --self-test 7 items OK; --dry-run write=0 unchanged=111 overwrite=0 refused=0; RAW.inc gap 0 \(self-checked\).
- 2026-11-08 review fixes: APRIORI.inc reset slot switched to MdeModulePkg ResetSystemRuntimeDxe \(same as pipa/DXE.inc\); the vendor ResetRuntimeDxe was removed because it only appeared in APRIORI and was never in FV \(FVMAIN has no such GUID, found by reviewer Sol\). ConfigurationMapLib.c EnableUfsIOC 1-&gt;0 to match enuma XBL uefiplat.cfg L117=0 \(pipa/alioth use 1\); EnableLogFsSyncInRetail stays 1 \(vendor incidental writes equal stock\).
- 2026-11-08 write-tiering \(docs/launch-route\): 'startup writes nothing' was too strict and unprovable, revised to tier by who writes what - host-side flash and our own userdata writes need per-round authorisation; bootchain/security partitions are a red line; vendor/Mu-Silicium firmware incidental writes \(UEFI vars, vendor logs/counters, UFS link/device state\) are allowed and equal to stock, no zero-write proof required.
- Reviewer Sol 2026-11-08: INSUFFICIENT EVIDENCE on the pre-fix image \(not released\). Fixed: reset module not in FV; 'startup writes nothing' unprovable \(now write-tiering\); EnableUfsIOC mismatch. Stage 1-2 boot.img also built \(self-checked\): ./unixnu bootimg ... exits 0, boot.img 1986560 B, Android header v1, kernel gzip = 192 B shim + FD, tail 977523 B DTB; hardware\_tested=false.
- 2026-11-08 更正：此前判定 enuma XBL 无以下 19 个模块并从固件清单删除（SdccDxe, FeatureEnablerDxe, PILProxyDxe, PILDxe, SPSSDxe, AdcDxe, UsbPwrCtrlDxe, QcomChargerDxe, ChargerExDxe, UsbfnDwc3Dxe, XhciPciEmulationDxe, XhciDxe, UsbMsdDxe, UsbDeviceDxe, UsbConfigDxe, UsbInitDxe, ButtonsDxe, TsensDxe, LimitsDxe）。imagefv\_a 分析证明这 19 个模块实为 enuma 自己 xbl\_a 内的原件（xbl\_a sha256 7ac67cbf4c7870a972cb4ffd9cc09d5db1c96b7f4a5abc7a80c0da9cabc65057；xbl\_a 内 QcomChargerDxe 名为 QcomChargerDxeLA、XhciPciEmulationDxe 名为 XhciPciEmulation），只是 extract\_enuma\_xbl.py 的 SELECT 白名单遗漏；已按原件导入恢复，厂商模块总数 52。ButtonsDxe 的 3 个未命名 Qualcomm DEPEX GUID 提供者仍推断在已导入 PmicDxe 等模块内但未证明，DEPEX 能否满足须实机观察。
- 2026-11-08 stage 3: board.toml \[payload\] dram\_size and \[payload.adt\] chip\_id, plus dts/enuma.dts memory node, changed for the payload/ADT stage; these do not alter the firmware build \(FD and DXE modules unchanged\).
- 2026-11-09 stage 3 first device run \(user authorised, filmed\): firmware source 1070b371e95bf59cfc6f955a37fec3c26ad2e804 \(same FD and candidate DTB as stage12-simplefb\) booted a real 192 MiB ramdisk payload. UniXNURamDiskDxe published the initrd block device \('UNIXNURAMDISK: initrd block device 0xA3FFF000 size 0xC000000 Success'\), then \[Bds\]Booting UniXNU -&gt; UniXNU.efi loaded -&gt; FAT payload mounted; no 'no initrd in /chosen', no ASSERT, no NO WINDOW. SPSS/SMBIOS 'start failed' lines are known harmless. ABL writes initrd into /chosen \(previously unconfirmed, now confirmed\). Firmware stays capped at implemented \(not device-verified\): stage-4 DarwinBoot window and kernel handoff are still untested.
- 2026-11-09 stage 4 first device run \(user authorised, filmed\): the PcdUniXNUDebugLevel=0x4 firmware change \(uefi-enuma fix/unixnu-debug-level commit 4db39e8fac0e6d76a1f0e9968e51f06f9b81e271, new FD sha256 e524988b8a05f15847ffc991170de8a5e0ead607400421e0835084497a71bf1e\) is effective on device: this run logged 8 UNIXNU: lines \(previous runs logged 0\), and the DARWINBOOT Print output also lands in ramoops \(previously assumed ConOut-only\), so the ramoops console carries the loader hand-off lines \(DARWINBOOT: hand-off to the kernel ... Exiting boot services, A green bar across the top marks the loader handoff\).

### 完成条件

- Firmware image builds, enters UniXNU, publishes the framebuffer and preserves the documented memory reservations.

### 当前范围

- Vendor UEFI binaries \(Binaries/enuma\) and the board DTB stay outside the repo \(.cache/firmware\); FD base/size is now 0x9FC00000/0x300000 by XBL uefiplat.cfg reconciliation, not device-verified.
- Hardware inputs and implementation are pending for enuma.
- Selection is ambiguous: none of the vendor\_boot DTBs matches the live board-id 0x2e \(46\); the enuma board DTB must come from the boot-time overlay \(live FDT\) or the board DTS, not from vendor\_boot.
- Astra High \(ses\_e4e61aafcffeyH5oBsTu0pSMYe\): source-only conditions unresolved \(ramdisk padding exposure, no enuma FDT/initrd mapping/reservation contract\); root preflight remains blocked.
- Reviewer Sol 2026-11-08 open conditions, resolved by the 2026-11-08 device run: candidate DTB accepted by ABL \(fastboot boot OKAY, live FDT visible at 0xAFDFE000\) though its content is still unverified; RAM Partition protocol producer confirmed \(RamManagerDxe mapped the RAM regions\).
- \[payload\] dram\_size, the board DTS memory nodes and the memory-reservation preservation clause are not yet device-verified, so firmware completion is capped at implemented, not device-verified.

### 下一步

- Bring-up stage 3 \(kernel/package/payload\) next; the first stage-3 inputs are listed in the stage-3 readiness analysis in the README. Return-to-bootloader is now established via the warm fastboot reset \(ramoops log channel\).

### 证据

- `host`: [DEBUG/CLANGPDB firmware build with preflight exits 0; product SILICIUM\_UEFI.fd = 3145728 B = 0x300000 = \[uefi\_fd\] size. Host-verified only for 'compiles', self-checked by the implementer \(not independently re-run by the Verifier\); no device evidence, not device-verified.](https://github.com/wh1stl3/UniXNU-enuma/blob/74dc21dd5c323a763a225f98a6eefc3815272046/scripts/enuma_firmware_preflight.py)
  Command: <code>./unixnu build firmware -D ../enuma/UniXNU-enuma --uefi ../enuma/uefi-enuma --edk2 ~/enuma-fw/mu_basecore</code>. Revision: `bec84f0ad9ab167ed08d0ce2ff46ab8cd2d15610`.
- `host`: [DEBUG/CLANGPDB firmware build with preflight exits 0; SILICIUM\_UEFI.fd = 3145728 B. FV report: generic ResetSystemRuntimeDxe \(4B28E4C7-FF36-4E10-93CF-A82159E777C5\) in FV, vendor ResetRuntimeDxe \(3AE17DB7-3CC5-4B89-9304-9549211057EF\) absent; every APRIORI vendor INF in FV except the USE\_CUSTOM\_DISPLAY\_DRIVER==1 branch \(DisplayDxe/CPRDxe, currently 0\). Self-checked by the implementer \(not re-run by Verifier\); 'compiles' only, no device evidence. FD/boot.img hashes vary with HEAD commit time \(SOURCE\_DATE\_EPOCH\), not build instability.](https://github.com/wh1stl3/UniXNU-enuma/blob/74dc21dd5c323a763a225f98a6eefc3815272046/scripts/enuma_firmware_preflight.py)
  Command: <code>./unixnu build firmware -D ../enuma/UniXNU-enuma --uefi ../enuma/uefi-enuma --edk2 ~/enuma-fw/mu_basecore</code>. Revision: `c18e13f983b045824b8b36c1a85a8aca628069d9`.
- `host`: [DEBUG/CLANGPDB firmware build with preflight exits 0; SILICIUM\_UEFI.fd = 3145728 B. 52 vendor modules \(19 restored from enuma xbl\_a\). FVMAIN EFI\_FV\_TOTAL\_SIZE=0x6c5000, EFI\_FV\_TAKEN\_SIZE=0x6c4c88. Every APRIORI.inc INF present in DXE.inc; every APRIORI vendor INF FILE\_GUID in FVMAIN.Fv.txt except the USE\_CUSTOM\_DISPLAY\_DRIVER==1 branch \(DisplayDxe/CPRDxe\); generic ResetSystemRuntimeDxe \(4B28E4C7-FF36-4E10-93CF-A82159E777C5\) in FV, vendor ResetRuntimeDxe \(3AE17DB7-3CC5-4B89-9304-9549211057EF\) absent; ButtonsDxe \(5BD181DB-0487-4F1A-AE73-820E165611B3\), UsbfnDwc3Dxe, SdccDxe, QcomChargerDxeLA GUIDs in FV; MemoryMapLib.c 23 rows no overlap. Self-checked by implementer, compiles only, no device evidence, not device-verified. ButtonsDxe DEPEX satisfiability needs on-device observation.](https://github.com/wh1stl3/UniXNU-enuma/blob/74dc21dd5c323a763a225f98a6eefc3815272046/scripts/enuma_firmware_preflight.py)
  Command: <code>./unixnu build firmware -D ../enuma/UniXNU-enuma --uefi ../enuma/uefi-enuma --edk2 ~/enuma-fw/mu_basecore</code>. Revision: `098a70707a6315858fb903a171ad9ee692c216e1`.
- `device`: [fastboot boot OKAY \(ABL accepted the boot.img\); screen showed the Project Silicium splash, a full screen of DXE logs, then the UniXNU menu \(version 0.1.0 / built-in configuration, drivers 0 loaded / 0 failed kits 0 acpi 0\) with volume/power keys working and Tools &gt; Advanced Logger QR carousel. Read-back ramoops log \(.cache/media/simplefb-20261108T185916/console-ramoops-0.txt, 255 lines\) confirms SEC \(MMU 48 regions / map valid / enabled, entry x0 = 0xAFDFE000\), DXE \(UFS SAMSUNG KLUEG8UHDC-B0E1, RamManagerDxe RAM map, SimpleFbDxe, ButtonsDxe, BdsDxe\) and \[Bds\]Booting UniXNU. Reached the UniXNU menu only; \[payload\] not built and stage 3 onward untested. Tested firmware source 1070b371e95bf59cfc6f955a37fec3c26ad2e804, merged to uefi-enuma main as 5a7da1746f94eb4d431c84a49194c4bc49b958dc.](https://github.com/wh1stl3/UniXNU-enuma/blob/74dc21dd5c323a763a225f98a6eefc3815272046/docs/firmware-log-capture.md)
  Command: <code>adb -s &lt;enuma&gt; reboot bootloader; fastboot -s &lt;enuma&gt; boot UniXNU/out/enuma/stage12-simplefb/boot.img; (readback) fastboot -s &lt;enuma&gt; continue; adb shell su -c 'cp /sys/fs/pstore/console-ramoops-0 /data/local/tmp/ramoops'; adb pull</code>. Revision: `1070b371e95bf59cfc6f955a37fec3c26ad2e804`.
- `device`: [fastboot boot OKAY \(push 4.5 s\), no partition flashed. Ramoops log \(.cache/media/stage3-20261109T004402/console-ramoops-0.txt, 14516 B / 256 lines\): 'UNIXNURAMDISK: device tree at 0xA3DFE000, 980302 bytes', 'UNIXNURAMDISK: initrd block device 0xA3FFF000 size 0xC000000 Success', then \[Bds\]Booting UniXNU -&gt; UniXNU.efi loaded -&gt; FAT payload mounted. No 'no initrd in /chosen', no ASSERT, no NO WINDOW; SPSS/SMBIOS 'start failed' are known harmless. ABL wrote initrd into /chosen \(previously unconfirmed, now confirmed\). Tested firmware source 1070b371e95bf59cfc6f955a37fec3c26ad2e804, same FD/candidate DTB as stage12-simplefb \(no firmware rebuild for stage 3\).](https://github.com/wh1stl3/UniXNU-enuma/blob/74dc21dd5c323a763a225f98a6eefc3815272046/docs/firmware-log-capture.md)
  Command: <code>fastboot -s &lt;enuma&gt; boot UniXNU/out/enuma/stage3/boot.img</code>. Revision: `1070b371e95bf59cfc6f955a37fec3c26ad2e804`.
- `device`: [fastboot boot OKAY, no partition flashed. ramoops read-back \(console-ramoops-0.txt, 15732 B / 279 lines\) shows 8 UNIXNU: lines \(vs 0 before PcdUniXNUDebugLevel=0x4\) and the DARWINBOOT: hand-off block, proving DARWINBOOT Print reaches ramoops. Firmware stays implemented \(not device-verified\).](https://github.com/wh1stl3/UniXNU-enuma/blob/74dc21dd5c323a763a225f98a6eefc3815272046/docs/firmware-log-capture.md)
  Command: <code>fastboot -s &lt;enuma&gt; boot out/enuma/stage4-log/boot.img (then fastboot continue + pstore read-back)</code>. Revision: `4db39e8fac0e6d76a1f0e9968e51f06f9b81e271`.

## CPU 与中断 {#cpu}

`planned`

### 硬件与依赖

- Identify the cpu and interrupts hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for cpu and interrupts.

### 操作步骤

- Follow the cpu and interrupts stage in the porting guide and record the actual commands.

### 开发经验

- 2026-11-07 device observation \(rooted enuma, sysfs read-only, scripts/enuma\_live\_collect.py\): cpufreq steps in kHz. cpu0-3: 300000 403200 518400 614400 691200 787200 883200 979200 1075200 1171200 1248000 1344000 1420800 1516800 1612800 1708800 1804800. cpu4-6: 710400 825600 940800 1056000 1171200 1286400 1382400 1478400 1574400 1670400 1766400 1862400 1958400 2054400 2150400 2246400 2342400 2419200. cpu7 \(prime\): 844800 960000 1075200 1190400 1305600 1401600 1516800 1632000 1747200 1862400 1977600 2073600 2169600 2265600 2361600 2457600 2553600 2649600 2745600 2841600 3187200. The live FDT lists a 4+3+1 topology with qcom,kryo compatibles and no OPP table, matching shared sm8250.dtsi topology while the AC prime step \(3187200 kHz\) is board data.
- Collect the first cpu and interrupts observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU.

### 当前范围

- Hardware inputs and implementation are pending for enuma.

### 下一步

- Inventory the required cpu and interrupts inputs before implementation.

### 证据

按下一步操作收集证据。

## 内存与 DMA {#memory}

`planned`

### 硬件与依赖

- Identify the memory and dma hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for memory and dma.

### 操作步骤

- Follow the memory and dma stage in the porting guide and record the actual commands.

### 开发经验

- 2026-11-07: the live pre-root FDT \(fdt.stdout\) /memory reg carries three ranges - 0x80000000-0xBBB00000 \(0x3bb00000\), 0x180000000-0x280000000 \(0x100000000\), 0xC0000000-0x180000000 \(0xC0000000\), about 7.9 GiB usable; input provenance, not verified runtime ownership. The three vendor\_boot SoC DTBs all declare an empty memory reg \(0x00 0x00 0x00 0x00\).
- Astra High pre-logger review \(ses\_e4e61aafcffeyH5oBsTu0pSMYe\): SEC InitializeMemory \(Sec.c 97-122\) builds memory HOBs/MMU before SecMain builds the pointer-only entry HOB \(172-178\); RamManager fills uncovered RAM conventional; there is no enuma FDT/initrd mapping/reservation contract yet. RamManager.c ManageRam has an uninitialized memory-range local, narrowly fixed by the firmware worker, not in this device task.
- 2026-11-08: uefi-enuma MemoryMapLib.c DDR table now has 23 rows reconciled against enuma XBL uefiplat.cfg \[MemoryMap\] \(per-row 'cfg L&lt;n&gt;' citations; xbl\_a sha256 7ac67cbf4c7870a972cb4ffd9cc09d5db1c96b7f4a5abc7a80c0da9cabc65057\). HYP shortened to 0x5D0000 \(sheng hyp-region no-map form\); Kernel 0xA0000000/0x10000000 kept \(cfg L33\). Overlap check \(UniXNU-enuma/.cache/check-memorymap-overlap.py\) reports 23 rows with no overlaps, all inside enuma DRAM 0x80000000-0xbbb00000. Kernel reservation vs owned\_memory\_size window stays PENDING-STAGE4 \(DarwinBoot AllocateWindow failure shows 'NO WINDOW/BIG RUN/FREE'\).
- 2026-11-08 reviewer Sol open: RAM Partition protocol producer unconfirmed \(EnvDxe.efi has only a GUID reference, no producer identified\); Kernel reservation vs owned\_memory\_size window remains for stage 4 device observation before any value is committed.
- 2026-11-08 device run: DXE Heap 2 \(0x93200000/0x05700000\) merged with the DXE Heap to \~138 MiB \(was 51 MiB\) in uefi-enuma MemoryMapLib.c resolved the DxeCore DxeMain.c\(581\) AllocatePoolPages ASSERT seen in an earlier run. RamManagerDxe then mapped the DRAM regions spanning 0x80000000-0x280000000 \(8 GiB physical\): 0x805F0000-0x80600000, 0x80800000-0x80860000, 0x80880000-0x80884000, 0x80894000-0x80900000, 0x80B00000-0x82400000, 0x85E00000-0x86000000, 0x9E400000-0x9F800000, 0x9FFD0000-0x9FFF7000, 0xB0400000-0x280000000. A RAMOOPS row \(0xB0000000/0x400000\) reserves the stock kernel's ramoops console zone. Candidate \[payload\] dram\_size = 0x200000000 \(recorded as a candidate only, NOT written to board.toml; needs user confirmation\). Kernel reservation vs owned\_memory\_size window remains PENDING-STAGE4.
- 2026-11-08 stage 3: dts/enuma.dts adds memory@80000000 \(device\_type = memory, reg = &lt;0 0x80000000 0 0x200000000&gt;\). The shared ADT generator \(scripts/unixnu/devicetree.py\) requires exactly one DRAM range and \[payload\] dram\_size must equal it, so the live FDT /memory three ranges \(0x80000000-0xBBB00000, 0xC0000000-0x180000000, 0x180000000-0x280000000\) are represented as one 8 GiB span. Correction \(reviewer Sol 2026-11-09\): the single span is not a conservative carve-out and does not exclude the hole - reg 0x80000000 + 0x200000000 includes the reserved 0xBBB00000-0xC0000000 \(\~69 MiB\) hole inside the span, so it is a span, not proof of contiguous allocatable memory. Host build only; not device-verified.
- 2026-11-09 stage 3 first device run \(user authorised, filmed; log .cache/media/stage3-20261109T004402/console-ramoops-0.txt, 14516 B / 256 lines, git-ignored\): with the 192 MiB ramdisk, ABL placed the FDT at 0xA3DFE000 \(980302 bytes\) - with an empty ramdisk it was 0xAFDFE000 - and wrote the initrd into /chosen \(the previously unconfirmed ABL-initrd-into-/chosen item is now confirmed\). The initrd block device is 0xA3FFF000 size 0xC000000 \(0xA3FFF000-0xAFFFF000\), entirely inside the Kernel reservation 0xA0000000/0x10000000, with no overlap against the firmware FD \(0x9FC00000+0x300000\), the DXE Heap 2 \(0x93200000\), and 4 KiB clear of ramoops \(0xB0000000\). This 192 MiB initrd occupies most of the 256 MiB Kernel reservation, so stage 4 must reconsider the DarwinBoot window / owned\_memory\_size before committing a value \(pending stage 4 on-device\).
- 2026-11-09 stage 4 first device run \(user authorised, filmed\): DarwinBoot allocated the owned-memory window and handed off. DARWINBOOT: hand-off to the kernel -&gt; kernel va 0xFFFFFFF00427C000 pa 0xC007C000; entry pa 0xC321A488 \(entry words 140006F5\); args pa 0xC40B0000 window 0x20000000 bytes; video base 0x9C000000 1600x2560 row 6400 bytes 32 bpp; CurrentEL 1 SCTLR\_EL1 0xC0180D; Exiting boot services. No NO WINDOW / BIG RUN / FREE failure, so the \~512 MiB \(0x20000000\) window was allocated around 0xC0000000 \(immediately above the 0xBBB00000-0xC0000000 hole\) and the kernel was copied to pa 0xC007C000. This proves the DarwinBoot window allocation and ExitBootServices, NOT that the XNU entry executed or the MMU was enabled \(needs the entry probe, stage 5\).

### 完成条件

- All handoff regions are accounted for and each enabled DMA engine accesses its allocated range with the documented cache policy.

### 当前范围

- Hardware inputs and implementation are pending for enuma.
- Parser live-FDT evidence is input provenance, not proof of memory runtime ownership; \[payload\] dram\_size and the board DTS memory nodes still need runtime verification before any memory value is written.
- Astra High \(ses\_e4e61aafcffeyH5oBsTu0pSMYe\): source-only conditions unresolved - SEC memory init precedes the entry HOB, and no enuma FDT/initrd reservation contract exists.
- Reviewer Sol 2026-11-08: RAM Partition protocol producer and the Kernel reservation / owned\_memory\_size window are unconfirmed; they stay pending until stage 4 device observation.

### 下一步

- Confirm RAM Partition protocol producer and the Kernel reservation / owned\_memory\_size window at stage 4 \(device observation\) before writing any memory value.

### 证据

- `device`: [Log: 'UNIXNURAMDISK: device tree at 0xA3DFE000, 980302 bytes' and 'UNIXNURAMDISK: initrd block device 0xA3FFF000 size 0xC000000 Success'. ABL wrote initrd into /chosen; ramdisk 0xA3FFF000-0xAFFFF000 sits inside Kernel reservation 0xA0000000/0x10000000 with no overlap vs FD / DXE Heap 2 / ramoops. 192 MiB initrd occupies most of the 256 MiB Kernel reservation -&gt; stage-4 DarwinBoot window / owned\_memory\_size must be re-derived on device.](https://github.com/wh1stl3/UniXNU-enuma/blob/74dc21dd5c323a763a225f98a6eefc3815272046/docs/firmware-log-capture.md)
  Command: <code>fastboot -s &lt;enuma&gt; boot out/enuma/stage3/boot.img (then fastboot continue + pstore read-back)</code>. Revision: `bf4eeffdde548ffafa813062bfaac52c01d38d56`.
- `device`: [DARWINBOOT: hand-off to the kernel: kernel va 0xFFFFFFF00427C000 pa 0xC007C000, entry pa 0xC321A488 \(words 140006F5\), args pa 0xC40B0000 window 0x20000000 bytes, video base 0x9C000000 1600x2560 row 6400 32 bpp, CurrentEL 1 SCTLR\_EL1 0xC0180D; 'Exiting boot services'. No NO WINDOW / BIG RUN / FREE, so the 512 MiB window was allocated at \~0xC0000000. Does not prove XNU entry / MMU enable \(needs entry probe\).](https://github.com/wh1stl3/UniXNU-enuma/blob/74dc21dd5c323a763a225f98a6eefc3815272046/docs/firmware-log-capture.md)
  Command: <code>fastboot -s &lt;enuma&gt; boot out/enuma/stage4-log/boot.img (then fastboot continue + pstore read-back)</code>. Revision: `829cf6a491ec2af86dc086410eea46d57b937408`.

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
- 2026-11-07 device observation \(read-only readback of the first 32 KiB of each UFS LUN with scripts/enuma\_live\_collect.py\): userdata is on sda, logical block size 4096 B, GPT first LBA 2686976 and last LBA 61880314 \(59193339 blocks\). The other LUNs sdb-sdf carry no userdata entry. These are the values for \[userdata\] first\_lba/last\_lba/lba\_bytes; they are not yet written to board.toml.
- Collect the first storage and root observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Host: register, clock, link and SMMU facts match the board inventory.
- Reads: SCSI capacity, GPT and known blocks are correct; OS/SystemOS windows stay within userdata.
- Root: the configured volume mounts and launchd starts. Persistence: writes survive reboot within the allocated Data region.

### 当前范围

- Route B is unconfigured: \[userdata\] geometry, root volume UUID, ShengUfs/archives and the storage ABI inputs are missing, so only route A \(RAM boot\) runs today.
- Hardware inputs and implementation are pending for enuma.

### 下一步

- Inventory the required storage and root inputs before implementation.

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

- 2026-11-07 source-only: the enuma stock defconfig \(MiCode elish-r-oss 52a2f180865f8368828985d6384130acd093fa93, line 463\) enables CONFIG\_BACKLIGHT\_KTZ8866 \(drivers/video/backlight/ktz8866.c\). The branch has no panel names or timings; the stock UEFI image carries 36 Panel\_\*.xml resources \(stock xbl.img DXE volume, see proprietary-files.txt\) but which panel the enuma unit uses is not established.
- 2026-11-08 device run: with USE\_CUSTOM\_DISPLAY\_DRIVER = 0 \(SimpleFbDxe, reusing the ABL-left display\) the frame buffer is visible on-screen through the SEC/DXE logs and the UniXNU menu on the 1600x2560 panel; the vendor DisplayDxe hangs at entry and blanks the screen \(reverted to SimpleFb\). Framebuffer geometry/colour and backlight control remain unverified beyond the menu text being legible.
- Collect the first display observation, its cause when established, and the resulting implementation decision.

### 完成条件

- A known frame appears with correct geometry and colors, then userland presentation and backlight controls work.

### 当前范围

- Hardware inputs and implementation are pending for enuma.

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

- 2026-11-07 source-only: Xiaomi's public kernel branch MiCode/Xiaomi\_Kernel\_OpenSource elish-r-oss \(52a2f180865f8368828985d6384130acd093fa93, covering Pad 5 Pro and Pad 5 Pro 5G\) enables CONFIG\_TOUCHSCREEN\_NT36523\_HOSTDL\_SPI and TOUCHSCREEN\_XIAOMI\_TOUCHFEATURE in arch/arm64/configs/vendor/enuma\_user\_defconfig \(lines 356-359, 777\) with drivers/input/touchscreen/nt36523 and drivers/misc/spi-xiaomi-tp.c, so the 5G unit's touch is a Novatek NT36523 on SPI; the branch ships three firmware variants \(fw01-03\) and no panel-to-firmware mapping. The branch has no board DTS, so pins, SPI controller and interrupt remain unverified.
- 2026-11-08 device run: ButtonsDxe drives volume up/down \(menu selection\) and power \(confirm\) in the UniXNU built-in menu; the Tools &gt; Advanced Logger page cannot be exited with the power key because the base-repo AdvancedLogDxe.c exit key only accepts CR/LF/ESC, not SCAN\_SUSPEND \(base repo is read-only; recorded as a known limitation\). Touch is untested.
- Collect the first input observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive, and buttons produce expected HID reports.

### 当前范围

- Hardware inputs and implementation are pending for enuma.

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

- 2026-11-07 device observation \(rooted enuma, kgsl sysfs read-only\): gpu\_available\_frequencies 670000000 587000000 525000000 490000000 441600000 400000000 305000000 Hz, so this unit exposes the 670 MHz Adreno 650 step. The live FDT kgsl-3d0 node \(chipid 0x6050002\) carries speed-bin tables 0-4; bins 1, 2 and 4 contain 670 MHz, and the selected bin is not printed by the tree. GMU power votes and clock values for the 670 MHz step are still unmeasured and must not be copied from alioth.
- Collect the first gpu observation, its cause when established, and the resulting implementation decision.

### 完成条件

- GPU submissions complete, mapping/fence handling is correct, a known image renders, and the selected Metal client presents it.

### 当前范围

- Hardware inputs and implementation are pending for enuma.

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

- Hardware inputs and implementation are pending for enuma.

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

- Hardware inputs and implementation are pending for enuma.

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

- 2026-11-07 source-only: the enuma stock defconfig \(MiCode elish-r-oss 52a2f180865f8368828985d6384130acd093fa93, lines 406-407, 86, 412-426\) enables DUAL\_FUEL\_GAUGE\_BQ27Z561, BQ2597X\_CHARGE\_PUMP, ARM\_QCOM\_CPUFREQ\_HW and TSENS/SPMI temp-alarm thermal; CPU frequency therefore comes from the hardware frequency plan and the public kernel carries no numeric OPP or thermal table. The 870 frequency steps, power votes and thermal zones still need enuma evidence \(live FDT or dtbo\).
- Collect the first power observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Declared power controls and battery readings match observations; each claimed sleep/resume transition restores its dependent peripherals.

### 当前范围

- Hardware inputs and implementation are pending for enuma.

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

- 2026-11-09 stage-4 kernel build \(host, self-checked, not device-tested\): after the OS-layer patch fix \(patches/xnu/os-series\) the kernel step completed \(60 patches\), prelinked against the 21H461 kernelcache \(pin f18b4df8...\). kernel.macho sha256 39cecb2e3afdcf82884cf3db23d256d24e251a90511175fe26bb6ced8978ac26 \(51064832 B\). build payload --kernel &lt;kernel.macho&gt; --config .cache/stage3-build.toml produced payload.img \(192 MiB FAT, ENUMAESP\) carrying kernel.macho + kernel.macho.adt \(13488 B, sha256 a78b393e...\) + unixnu.toml, content 51078722 B \(\~48.7 MiB = 25.4% of size\_mib 192, under the 95% cap\), no trust cache / no data seed; payload\_sha256 4e601ff767f5a537503deb304c50a49713f1b19afb49e7ed960cdbf6b3bae6bd. bootimg --fd &lt;stage3 FD&gt; --dtb &lt;stage3 DTB&gt; -o out/enuma/stage4/boot.img produced boot.img \(203505664 B, header v1, ramdisk\_bytes 201326592\), sha256 bee177a208de5e1135817128eafe475792c3a5eaa8a0116d80cdbc0eed9599b8, fd\_sha256 96b50c78..., dtb\_sha256 42d36a00... \(same FD/DTB as stage3; firmware NOT rebuilt\). A WSL-only toolchain change was required: unifdef 2.10 \(system\) -&gt; 2.12 \(\~/.local/bin\) because v2.10 fails parsing bsd/net/pfvar.h during installhdrs; the base repo itself was not modified for this. All three commands exit 0.
- Format-2 migration: scripts/package.sh taken unmodified from the official template; patches/xnu/series created empty; package/ documents the empty device package.
- 2026-11-08 stage 3 host build \(self-checked, not device-verified\): ./unixnu tree; ./unixnu build payload --kernel &lt;32-byte placeholder kernel.macho, no Apple bytes&gt; --config &lt;git-ignored build config&gt;; ./unixnu bootimg \(ramdisk = payload\) all exit 0. payload.img \(192 MiB FAT, volume ENUMAESP\) carries unixnu.toml + kernel.macho + kernel.macho.adt; boot.img out/enuma/stage3/boot.img sha256 141eaa7eacaa5865bb852cb435124a38b43abf92715de2609e7005297f32b7bb with ramdisk\_bytes 201326592 \(&gt;0\). The real kernel/prelink step \(stage 5\) is still pending; this placeholder payload only exercises the stage-3 menu/ADT path.
- 2026-11-09 stage 3 first device run \(user authorised, filmed\): fastboot boot of out/enuma/stage3/boot.img \(sha256 141eaa7eacaa5865bb852cb435124a38b43abf92715de2609e7005297f32b7bb, 203505664 B, header v1, ramdisk = 192 MiB FAT payload\) returned OKAY in 4.5 s with no partition flashed; the FAT payload was mounted and reached the built-in menu. The default UniXNU item counts down 3 s then calls DarwinBoot and shows Load Error \(32-byte placeholder kernel, expected, no kernel handoff\). The real kernel/prelink \(stage 5\) is still pending; this run confirms the payload/ADT assembly and transport path, not a kernel handoff.
- Collect the first image assembly observation, its cause when established, and the resulting implementation decision.
- 2026-11-09 stage 4 first device run \(user authorised, filmed\): out/enuma/stage4-log/boot.img \(sha256 056a095f69876c552f2e71ebfb41fced08642032d04ff02e10e8302ed3eac1ac, 203505664 B, header v1, ramdisk\_bytes 201326592\) carrying the real kernel.macho \(sha256 39cecb2e3afdcf82884cf3db23d256d24e251a90511175fe26bb6ced8978ac26, 51064832 B; payload.img 4e601ff767f5a537503deb304c50a49713f1b19afb49e7ed960cdbf6b3bae6bd, 201326592 B\) booted via fastboot boot OKAY with no partition flashed. Firmware source uefi-enuma fix/unixnu-debug-level commit 4db39e8fac0e6d76a1f0e9968e51f06f9b81e271 \(new FD sha256 e524988b8a05f15847ffc991170de8a5e0ead607400421e0835084497a71bf1e\). The log reached 'UNIXNU: menu: timeout, booting default 0' -&gt; 'UNIXNU: boot: entry 'xnu' \(UniXNU\)' -&gt; 'DARWINBOOT: hand-off to the kernel' -&gt; 'Exiting boot services' \(green bar across the top\). This is the first real-kernel boot; it proves image assembly/transport and the DarwinBoot handoff, NOT that the XNU entry executed.
- 2026-11-09 stage 5 bisect \(user observed, filmed; the reset instant is not on video\): the entry probe walked 16 checkpoints from the XNU entry to just before the root-device wait. Passed \(three colour bars + \~6 s auto-reset into fastboot\): 04 \_early\_random, 05 \_vm\_mem\_bootstrap, 06 \_sched\_init, 09 \_PE\_init\_iokit; transitive 01-03, 07, 08, 12-14. 15 \(\_IOFindBSDRoot, reset-before\) reset, 16 \(\_vfs\_mountroot, reset-before\) stuck with no reset -&gt; the kernel stops inside IOFindBSDRoot waiting for the root device \(expected without a storage driver; not direct evidence, the bl's between 15 and 16 were not probed individually\). 10/11 \(reset-after\) cannot pass by design \(reset\_after fires only after the call returns; vfs\_mountroot never returns\). After an auto \(PSCI\) reset the pstore has no console-ramoops-0; after a manual long-press it is present \(firmware log up to DARWINBOOT hand-off / Exiting boot services\), so 'XNU zeroed ramoops' does not hold - more likely the kernel PSCI reset path does not preserve the log \(unverified\). No kernel-side blocking before the root-device wait; stage 6 \(storage/root\) not started.

### 完成条件

- Kernel and prelink succeed, payload contains all declared inputs, and the boot image matches the bootloader format and size limit.

### 当前范围

- Hardware inputs and implementation are pending for enuma.

### 下一步

- Inventory the required image assembly inputs before implementation.

### 证据

- `host`: [Host build, self-checked \(no device run, not device-verified\). kernel.macho sha256 39cecb2e... \(51064832 B\); payload.img 192 MiB FAT, content 51078722 B \(\~25% of size\_mib\); boot.img sha256 bee177a2... \(203505664 B, header v1\). build kernel / build payload / bootimg all exit 0.](https://github.com/wh1stl3/UniXNU-enuma/blob/74dc21dd5c323a763a225f98a6eefc3815272046/board.toml)
  Command: <code>./unixnu build kernel -D ../enuma/UniXNU-enuma &amp;&amp; ./unixnu build payload --kernel out/enuma/ipados-17.7.11-21H461/enuma/kernel/kernel.macho --config .cache/stage3-build.toml -D ../enuma/UniXNU-enuma &amp;&amp; ./unixnu bootimg --uefi ../enuma/uefi-enuma --fd &lt;stage3 FD&gt; --dtb &lt;stage3 DTB&gt; -o out/enuma/stage4/boot.img -D ../enuma/UniXNU-enuma</code>. Revision: `01500a9a38a4185306cb9f27df17677bb2307158`.
- `device`: [fastboot boot OKAY \(push 4.5 s\), no partition flashed. boot.img sha256 141eaa7eacaa5865bb852cb435124a38b43abf92715de2609e7005297f32b7bb \(203505664 B, header v1, ramdisk 192 MiB FAT payload\). Log: 'UNIXNURAMDISK: initrd block device 0xA3FFF000 size 0xC000000 Success' then '\[Bds\]Booting UniXNU', UniXNU.efi loaded, FAT mounted; no 'no initrd in /chosen', no ASSERT, no NO WINDOW. Menu default UniXNU item counts down 3 s then Load Error \(32-byte placeholder kernel, expected\).](https://github.com/wh1stl3/UniXNU-enuma/blob/74dc21dd5c323a763a225f98a6eefc3815272046/docs/firmware-log-capture.md)
  Command: <code>fastboot -s &lt;enuma&gt; boot out/enuma/stage3/boot.img</code>. Revision: `bf4eeffdde548ffafa813062bfaac52c01d38d56`.
- `device`: [fastboot boot OKAY, no partition flashed. stage4-log/boot.img sha256 056a095f... \(203505664 B, header v1\), kernel.macho 39cecb2e... \(51064832 B\), payload.img 4e601ff7... \(201326592 B\), firmware FD e524988b... \(3145728 B\). Log: UNIXNU: menu timeout -&gt; boot entry 'xnu' -&gt; DARWINBOOT: hand-off -&gt; Exiting boot services \(green bar\). Verifier \(Luna\) independently re-ran the hash/header/bootimg reproduction \(byte-identical\). Does not prove the XNU entry executed.](https://github.com/wh1stl3/UniXNU-enuma/blob/74dc21dd5c323a763a225f98a6eefc3815272046/docs/firmware-log-capture.md)
  Command: <code>fastboot -s &lt;enuma&gt; boot out/enuma/stage4-log/boot.img</code>. Revision: `829cf6a491ec2af86dc086410eea46d57b937408`.
- `host`: [Host build, self-checked \(no device run, not device-verified\). board.toml \[payload\] entry\_probe\_reset\_delay = 6 with panic\_screen omitted \(the panic screen code is 2607 B, exceeding this kernel's \_\_text padding 2512 B by 95 B, so only probe stages 1/2/3 are installed\). build payload exit 0; payload-patch.log: 'patched kernel.macho: stage 1 blue bar, stage 2 magenta bar, stage 3 reset 6 s after the MMU is on'. The source kernel.macho \(39cecb2e..., 51064832 B\) is copied, not modified in place; the patched payload kernel is b45918924d8e5399462be00de2ab087990a8b1146e36b39caf12b75c2a849cb9. payload.img sha256 7c42e252fab9955b3431da97b9191deca9dc42c667d2908ae7ec7826333de448 \(201326592 B; content \~48.7 MiB, under the 182 MiB 95% cap\). bootimg exit 0; boot.img sha256 5ee53cb0ded71248981d3df31133b9befd0f36197a26db3d4cee44fe5f8d656e \(203505664 B, header v1, ramdisk 201326592 B == payload.img, FD e524988b..., DTB 42d36a00...\).](https://github.com/wh1stl3/UniXNU-enuma/blob/74dc21dd5c323a763a225f98a6eefc3815272046/board.toml)
  Command: <code>./unixnu build payload -D ../enuma/UniXNU-enuma --kernel out/enuma/ipados-17.7.11-21H461/enuma/kernel/kernel.macho --config .cache/stage3-build.toml &amp;&amp; ./unixnu bootimg --uefi ../enuma/uefi-enuma --fd &lt;stage4 FD&gt; --dtb &lt;stage3 DTB&gt; -o out/enuma/stage5-probe/boot.img -D ../enuma/UniXNU-enuma</code>. Revision: `700772a915c40c75061087e977da2f950f66c427`.
- `device`: [fastboot boot OKAY \(push 4.5 s\), no partition flashed. Screen \(user observation, filmed; the reset itself was not captured on video\): after the countdown the green bar, then blue bar, then magenta bar appeared in order, and \~6 s later the device auto-reset into fastboot \(magenta bar -&gt; fastboot clearly &lt; 20 s, so not the \~20 s firmware watchdog\); bootreason=bootloader in Android. First device evidence that the XNU entry instruction executed \(blue bar, MMU off\), reached just before MMU-on \(magenta bar\), and the MMU was enabled \(stage 3 reset 6 s after\). This run had no console-ramoops-0 in pstore \(dmesg shows ramoops attached 0xb0000000/4 MiB; stages 3/4 had it\): hypothesis \(unverified\) - XNU ran and took/zeroed 0xB0000000, and the ADT does not reserve it, or the reset path did not retain RAM. Does not prove any execution past the MMU enable \(after \_arm\_init\).](https://github.com/wh1stl3/UniXNU-enuma/blob/74dc21dd5c323a763a225f98a6eefc3815272046/docs/firmware-log-capture.md)
  Command: <code>fastboot -s &lt;enuma&gt; boot out/enuma/stage5-probe/boot.img</code>. Revision: `b64e5564fc8be0213a52df65a479a7ff44d2ee07`.
- `host`: [Host build, self-checked \(no device run, not device-verified\). Six entry-probe bisect images built, each with entry\_probe\_reset\_delay=6 + entry\_probe\_reset\_after=&lt;symbol&gt; \(in \_arm\_init or \_kernel\_bootstrap\), occurrence 1. payload-patch.log for each: 'stage 1 blue bar, stage 2 magenta bar, stage 4 reset after call \#1 to &lt;symbol&gt; in &lt;fn&gt;'; panic\_screen false. Each boot.img is 203505664 B, header v1, ramdisk 201326592 B == its payload.img, FD e524988b..., DTB 42d36a00...; the patched payload kernel differs from the source 39cecb2e... . Checkpoint table, sha256 and read-out in docs/entry-probe-bisect.md.](https://github.com/wh1stl3/UniXNU-enuma/blob/74dc21dd5c323a763a225f98a6eefc3815272046/docs/entry-probe-bisect.md)
  Command: <code>./unixnu build payload -D ../enuma/UniXNU-enuma --kernel out/enuma/ipados-17.7.11-21H461/enuma/kernel/kernel.macho --config .cache/stage3-build.toml &amp;&amp; ./unixnu bootimg --uefi ../enuma/uefi-enuma --fd &lt;stage4 FD&gt; --dtb &lt;stage3 DTB&gt; -o out/enuma/stage5-bisect/&lt;NN&gt;-&lt;symbol&gt;/boot.img -D ../enuma/UniXNU-enuma</code>. Revision: `0fc2405d82a78fea9d3b813d9ecbdcde47a5eda2`.
- `host`: [Host build, self-checked \(no device run, not device-verified\). Five more entry-probe bisect images \(07-11\), larger steps: entry\_probe\_reset\_delay=6 + entry\_probe\_reset\_after=&lt;symbol&gt; with entry\_probe\_reset\_in in \_kernel\_bootstrap / \_kernel\_bootstrap\_thread / \_bsd\_init. payload-patch.log: 'stage 1 blue bar, stage 2 magenta bar, stage 4 reset after call \#1 to &lt;symbol&gt; in &lt;fn&gt;'; panic\_screen false. Each boot.img 203505664 B, header v1, ramdisk 201326592 B == its payload.img, FD e524988b..., DTB 42d36a00...; patched payload kernel differs from source 39cecb2e... . Checkpoints: \_kernel\_thread\_create, \_sched\_startup, \_PE\_init\_iokit, \_bsd\_init, \_vfs\_mountroot. Images 01-06 unchanged \(sha256 re-verified\). See docs/entry-probe-bisect.md.](https://github.com/wh1stl3/UniXNU-enuma/blob/74dc21dd5c323a763a225f98a6eefc3815272046/docs/entry-probe-bisect.md)
  Command: <code>./unixnu build payload -D ../enuma/UniXNU-enuma --kernel out/enuma/ipados-17.7.11-21H461/enuma/kernel/kernel.macho --config .cache/stage3-build.toml &amp;&amp; ./unixnu bootimg --uefi ../enuma/uefi-enuma --fd &lt;stage4 FD&gt; --dtb &lt;stage3 DTB&gt; -o out/enuma/stage5-bisect/&lt;NN&gt;-&lt;symbol&gt;/boot.img -D ../enuma/UniXNU-enuma</code>. Revision: `a27731a4ddf7def41f034c2943ed32b322f5574e`.
- `host`: [Host build, self-checked \(no device run, not device-verified\). Five entry-probe bisect images \(12-16\) with entry\_probe\_reset\_before=true + entry\_probe\_reset\_delay=6 + entry\_probe\_reset\_after=&lt;symbol&gt; \(in \_kernel\_bootstrap\_thread or \_bsd\_init\). payload-patch.log: 'stage 1 blue bar, stage 2 magenta bar, stage 4 reset before call \#1 to &lt;symbol&gt; in &lt;fn&gt;'; panic\_screen false. Each boot.img 203505664 B, header v1, ramdisk 201326592 B == its payload.img, FD e524988b..., DTB 42d36a00...; patched payload kernel differs from source 39cecb2e... . Checkpoints: \_bsd\_init, \_IOKitInitializeTime, \_IOKitBSDInit, \_IOFindBSDRoot, \_vfs\_mountroot \(all reset-before\). Images 01-11 unchanged \(sha256 re-verified\). See docs/entry-probe-bisect.md.](https://github.com/wh1stl3/UniXNU-enuma/blob/74dc21dd5c323a763a225f98a6eefc3815272046/docs/entry-probe-bisect.md)
  Command: <code>./unixnu build payload -D ../enuma/UniXNU-enuma --kernel out/enuma/ipados-17.7.11-21H461/enuma/kernel/kernel.macho --config .cache/stage3-build.toml &amp;&amp; ./unixnu bootimg --uefi ../enuma/uefi-enuma --fd &lt;stage4 FD&gt; --dtb &lt;stage3 DTB&gt; -o out/enuma/stage5-bisect/&lt;NN&gt;-before-&lt;symbol&gt;/boot.img -D ../enuma/UniXNU-enuma</code>. Revision: `a6295419cde9ab30cb01828edce109bc2d797dbe`.
- `device`: [fastboot boot OKAY, no partition flashed \(each image\). Three colour bars then \~6 s auto-reset into fastboot at 04/05/06/09 and 15 \(reset-before \_IOFindBSDRoot\); 16 \(reset-before \_vfs\_mountroot\) stuck with no reset \(10+ s, manual long-press back to fastboot\). Inferred: the kernel reaches IOFindBSDRoot and stops waiting for the root device \(expected without a storage driver\). Auto \(PSCI\) reset leaves no console-ramoops-0; manual long-press preserves it \(firmware log only, up to DARWINBOOT hand-off / Exiting boot services\). No kernel fault before the root-device wait.](https://github.com/wh1stl3/UniXNU-enuma/blob/74dc21dd5c323a763a225f98a6eefc3815272046/docs/entry-probe-bisect.md)
  Command: <code>fastboot -s &lt;enuma&gt; boot out/enuma/stage5-bisect/&lt;NN&gt;-&lt;symbol&gt;/boot.img (16 checkpoint images)</code>. Revision: `07664d7844c122ef34186fd3cb163697d52f362a`.

## 诊断 {#diagnostics}

`planned`

### 硬件与依赖

- Identify the diagnostics hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for diagnostics.

### 操作步骤

- Follow the diagnostics stage in the porting guide and record the actual commands.

### 开发经验

- unixnu.lock committed from the first complete fetch: xnu d8b80295, sm8250 166235ec, edk2 cfb93724, libplatform a00a4cc3, libdispatch 30fe6a7d, libpthread c0e60fb5, AvailabilityVersions 933f9360, corecrypto-2023 11fba65b, IOStorageFamily e45fbe30.
- 2026-11-07 feasibility \(source review only, no build or device I/O\): kernel-stage disk persistence is a separate mechanism from Advanced Logger. The reference \(UniXNU-sheng 516a780473a2ac59c8b438e132bb60204dda9e22, package/BootLog.c boot\_log\_tick\) writes msgbuf and panic snapshots through native\_ufs\_log\_open/write/sync into a reserved userdata tail window and reads them back with a Linux or recovery reader, so it needs ShengUfs, CONFIG\_XNU\_NATIVE\_UFS, CONFIG\_XNU\_BOOT\_PROGRESS and sheng-log=1, none of which enuma enables. It cannot run before UFS publishes a root layout, and its reset glue \(BootReset.c, PMIC reboot-reason cell\) is board-specific and must not be copied. Before UFS the only options are the firmware QR export, UART/screen capture, and an unproven RAM-reserved buffer \(the legacy R-002 Log Buffer 0x9fff7000/0x8000 note, warm-reset retention untested\).
- Official kernel-stage capture that needs no storage driver \(unixnu.com guide/debugging and porting/log-capture, checked 2026-11-07\): UART via \[payload\] kernel\_args serial=3 debug=0x14e \(UNIXNU:/DARWINBOOT: lines\), the framebuffer diagnostic page \(boot-progress=1 freezes after 30 s stall, =2 runs continuously; needs CONFIG\_XNU\_BOOT\_PROGRESS, which configs/enuma\_defconfig leaves disabled\), the pulse bar, the panic screen \(\[payload\] panic\_screen = true via patch-xnu-entry-probe.py, optional CONFIG\_XNU\_DT\_PANIC\_REGION\), the entry-probe colour bars and entry\_probe\_reset\_delay, and the USB debug terminal scripts/debug\_terminal.py \(CDC, giulia protocol only; enuma has no matching board backend\). Persistent disk logging stays storage-gated as recorded above.
- 2026-11-08 device run: firmware log channel established via RamoopsLogLib writing DEBUG output to the stock kernel's ramoops console zone \(0xB0000000, 4 MiB = console 2 MiB + pmsg 2 MiB, no ECC, DBGC header\). SEC sets the PON reset type to warm + bootloader reason, so an ASSERT or watchdog reset warm-restarts into fastboot with RAM preserved. Read-back flow: device in fastboot -&gt; fastboot -s &lt;enuma&gt; continue \(no reset\) -&gt; Android boots -&gt; root reads /sys/fs/pstore/console-ramoops-0 \(su -c cp to /data/local/tmp then adb pull, then delete the temp file\). A hard reset loses the log. See docs/firmware-log-capture.md.
- Collect the first diagnostics observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Each claimed milestone has a reproducible command, a matching source/image revision and an accessible result.

### 当前范围

- Hardware inputs and implementation are pending for enuma.

### 下一步

- Capture the firmware log through Tools &gt; Advanced Logger on the first DEBUG firmware boot, then decide the kernel log path after storage is verified: measure the userdata GPT and enuma reset/reboot-reason registers, and test RAM-buffer retention before any userdata write \(which needs explicit authorisation\).

### 证据

按下一步操作收集证据。

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

- No modem evidence recorded yet; the shared SM8250 support does not carry this board's modem firmware. package/README.md added by the format-2 migration.
- 2026-11-07: the stock firmware provenance inventory \(proprietary-files.txt and the vendor\_boot DTB candidates\) does not establish modem firmware or EFS/NV provenance; the kona SoC DTB only lists IPA/QMAP data-path nodes \(qcom,ipa, qcom,rmnet-ipa3, mhi\), which is SoC-level device-tree structure, not modem firmware evidence.
- 2026-11-07 source-only: the enuma stock defconfig \(MiCode elish-r-oss 52a2f180865f8368828985d6384130acd093fa93, lines 264-266, 282-287, 323, 555-560, 677-681\) enables QRTR\_MHI, MHI\_QCOM, IPA3/RMNET\_IPA3 and ESOC\_MDM\_4x, which the Wi-Fi sibling elish leaves off \(ESOC disabled\), so the 5G unit has an external modem on MHI with an IPA data path. That branch gives no node addresses. The community firmware repack's modem.img was corrupted by a resumed download and was not used.

### 完成条件

- SIM identity, network registration and a data session are observed on the device.

### 当前范围

- Planned; outside the first boot milestone.

### 下一步

- Extract modem firmware and EFS inputs, then record QRTR/QMI channels from the vendor DTS.

### 证据

按下一步操作收集证据。

</div>
