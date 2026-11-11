# Xiaomi Pad 8 Pro: first XNU boot from RAM \(OnePlus 13T base\) \(donyanchen\)

[donyanchen/UniXNU-piano](https://github.com/donyanchen/UniXNU-piano)

<div v-pre>

Xiaomi Pad 8 Pro \(piano, SM8750\) boots iPadOS 17.7.11 from RAM through a Mu-Silicium based UEFI, using the SM8750 support and the board-owned storage, PMGR and firmware integration. Not booted on the device yet.

源记录: [porting.toml](https://github.com/donyanchen/UniXNU-piano/blob/f37b9f3866df66105c93483df2551e528b61836a/porting.toml), `f37b9f3866df66105c93483df2551e528b61836a`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `implemented` |
| [固件与启动](#firmware) | `implemented` |
| [CPU 与中断](#cpu) | `implemented` |
| [内存与 DMA](#memory) | `planned` |
| [存储与根卷](#storage) | `implemented` |
| [显示](#display) | `planned` |
| [输入](#input) | `planned` |
| [GPU](#gpu) | `not-applicable` |
| [网络](#network) | `not-applicable` |
| [音频](#audio) | `not-applicable` |
| [电源](#power) | `implemented` |
| [镜像组装](#packaging) | `planned` |
| [诊断](#diagnostics) | `planned` |

## 配置 {#configuration}

`implemented`

### 硬件与依赖

- SM8750 SoC support from the OnePlus 13T port \(UniXNU-sm8750-common\), an iPadOS 17.7.11 \(21H461\) IPSW, and a UniXNU checkout pinned by the packaging workflow.

### 配置

- board.soc\_source = sm8750; board.os\_profile = ipados-17.7.11-21H461; board.kit = piano; schema\_version = 2.
- configs/piano\_defconfig selects the native UFS, AES, virtio block and ram block archives plus CONFIG\_XNU\_SHENG\_PMGR; configs/piano\_bootstrap\_defconfig is the same selection with CONFIG\_XNU\_SHENG\_PMGR off.
- \[kernel\].archives is read from board.toml, not from the defconfig, so a selection change has to touch both files.

### 操作步骤

- Run ./unixnu defconfig piano\_defconfig -D ../device from the UniXNU checkout.
- Run ./unixnu fetch, ./unixnu ipsw fetch -D ../device and ./unixnu tree -D ../device.
- Trigger .github/workflows/package-bare-metal.yml with os=17 and jobs=4.

### 开发经验

- The kernel step runs as two passes. configs/piano\_bootstrap\_defconfig builds a kernel without the sheng PMGR binder and stages it as build/xnu-prelink/native-owner-ufs-rootauth3-candidate.macho, because build-sheng-platform-power.py refuses to start without a reference candidate \('No reference candidate available'\).
- The PMGR binder is listed in \[kernel\].archives, which the bootstrap pass also reads, so the candidate step removes that line from board.toml with python \(macOS sed -i treats the next argument as the suffix\), builds, and restores the file.
- build-sheng-platform-power.py compiles $TREE/kits/sheng/ShengPlatformPower.cpp, while the board ships the source at package/ShengPlatformPower.cpp; the defconfig step now copies it into both out/.../piano/tree/kits/sheng and out/.../piano\_bootstrap/tree/kits/sheng.
- audit-amfi-pmgr-contract.py reads tree/.cache/firmware/kernelcache.macho/kernelcache.release.ipad7.decompressed, so the candidate step copies out/ipsw/21H461/kernelcache.decompressed there.
- The UEFI checkout is read-only, and its piano.dsc lacks the UniXNULib mapping \(error 4000\), so patches/uefi/piano-dsc-unixnulib.patch is applied in the prep step with the two-level uefi/uefi/pianoPkg/piano.dsc path.
- patches/xnu/series on the SoC side already carries sheng-platform-power.patch; adding it to the device series applies it twice and fails at bsd\_init.c:688.
- The device release is driven by scripts/package.sh, which only resolves \[package\] unixnu from board.toml and hands everything else to the pinned UniXNU checkout.

### 完成条件

- All source pins resolve, every selected component is covered by an area, and the two-pass kernel build links with the sheng PMGR archive force-loaded.

### 当前范围

- The UniXNU revision is pinned in the workflow; the effective component set is only visible through ./unixnu status.

### 下一步

- Compare ./unixnu status --json output whenever a defconfig, fragment or source pin changes.

### 证据

- `source`: [candidate pass, ShengPlatformPower.cpp staging and the fixed kernelcache path for the PMGR audit; the prep step also applies patches/uefi/piano-dsc-unixnulib.patch and patches/uefi/piano-fastboot-payload.patch, patches/uefi/bootshim-image-size.patch and patches/uefi/mu-sec-entry-arg.patch \(the last two against uefi/deps/Mu-Silicium, because that checkout and its BootShim and SEC sources only exist after tools/setup-deps.sh\), and patches/unixnu-bootimg-text-offset.patch against the pinned UniXNU checkout \(the last one also carries the USB bring-up trace and the payload channel\), and runs scripts/prepare-unixnu-diagnostics.py on its UniXNULib/Config.c](https://github.com/donyanchen/UniXNU-piano/blob/f37b9f3866df66105c93483df2551e528b61836a/.github/workflows/package-bare-metal.yml)
- `source`: [bootstrap selection: identical to piano\_defconfig except CONFIG\_XNU\_SHENG\_PMGR](https://github.com/donyanchen/UniXNU-piano/blob/f37b9f3866df66105c93483df2551e528b61836a/configs/piano_bootstrap_defconfig)
- `source`: [board identity, component selection, \[kernel\].archives and \[package\].unixnu the packaging workflow consumes](https://github.com/donyanchen/UniXNU-piano/blob/f37b9f3866df66105c93483df2551e528b61836a/board.toml)

## 固件与启动 {#firmware}

`implemented`

### 硬件与依赖

- Mu-Silicium based UEFI for SM8750, spliced through tools/setup-deps.sh, plus the board UEFI repository pinned by the workflow.

### 配置

- \[firmware\] config = piano, dsc = Platforms/Xiaomi/pianoPkg/piano.dsc, fd = Build/pianoPkg/&\#123;target&\#125;\_CLANGPDB/FV/SILICIUM\_UEFI.fd.
- \[firmware\].packages lists the UEFI root, &\#123;tree&\#125;/package, &\#123;tree&\#125;/kits, &\#123;tree&\#125;/drivers/DarwinBoot and the EDK II/Mu trees.
- \[firmware.defines\] UNIXNU = 1 and DEVICE\_MODEL = piano.

### 操作步骤

- Run uefi/tools/setup-deps.sh in the UEFI checkout.
- Apply patches/uefi/piano-dsc-unixnulib.patch at the repository root.
- Run ./unixnu build firmware -D ../device --uefi ../uefi/deps/Mu-Silicium.

### 开发经验

- The firmware volume failed with error 4000 \('Instance of library class \[UniXNULib\] is not found for module ... UniXNU.inf'\) because pianoPkg/piano.dsc had no LibraryClasses mapping for UniXNULib; the patch adds it.
- ENABLE\_SECUREBOOT defined empty made '\#if ENABLE\_SECUREBOOT == 1' an invalid token; the DSC now defines it as 0.
- The firmware packages list needs drivers/DarwinBoot rather than the older PaganiDarwinBoot path.
- The payload cannot travel in the boot image: a vendor ABL refuses the 160 MiB ramdisk \(oem debuglog shows UNIXNURAMDISK publishing the stale 38.9 MB Android initrd the device tree still names\), and vendor\_boot is only 96 MiB, so neither field fits a 125 MB kernel. The fastboot path carries it instead: FB\_MAX\_DOWNLOAD rises to 256 MiB, 'oem ramdisk' publishes the staged bytes as a read-only BlockIo volume for the FAT driver, and DeviceBootManagerAfterConsole waits up to 20 s for that volume before UniXNU scans the volumes once. The patch also keeps the fastboot bring-up trace: the UsbDevice protocol and StartEx results are printed and held, and both are retried \(10 x 200 ms and 5 x 300 ms\). PmicDxe stays disabled: its SPMI channel 690 access faults because ABL no longer grants that channel to the apps execution environment, and the fault is what the vendor comment records. UFS still enumerates, so the protocols the storage path needs are provided by the unconditionally loaded charger and platform drivers; a StartEx failure would point at the rails rather than at a missing protocol.
- The stock boot manager never started UniXNU.efi: DeviceBootManagerAfterConsole ran PianoDtbInstall, PianoFastbootStart, StartEspLoader and StartFvApp\(AndroidBoot\), so the menu built into the firmware volume was unreachable. The first patch added a StartFvApp call with UniXNU's FILE\_GUID; the board then booted UEFI all the way to the console and dropped into the UEFI Shell instead of the menu, because StartFvApp built its device path from DevicePathFromHandle\(LoadedImage-&gt;DeviceHandle\), which inside BDS does not carry a usable firmware volume path, so EfiBootManagerBoot failed silently. StartFvApp now reads the PE32 section with GetSectionFromAnyFv and calls LoadImage/StartImage itself, and prints each outcome on the console so the next boot states whether the image is in a volume, failed to load, or returned.

### 完成条件

- The firmware step emits SILICIUM\_UEFI.fd for pianoPkg with the UniXNU application linked in.

### 当前范围

- No firmware image has been booted on the device yet; the GOP handover is unverified.

### 下一步

- Boot the firmware and capture its serial output before claiming the UEFI stage.

### 证据

- `source`: [reports the USB device protocol lookup and StartEx result on the console, each held for two seconds, so the piano-uefi fastboot bring-up can be diagnosed without a serial port](https://github.com/donyanchen/UniXNU-piano/blob/f37b9f3866df66105c93483df2551e528b61836a/patches/uefi/piano-fastboot-payload.patch)
- `source`: [starts UniXNU.efi from the firmware volume before the ESP loader and AndroidBoot fallbacks \(loading it with GetSectionFromAnyFv plus LoadImage/StartImage rather than a device path built from the BDS loaded image\), and carries the payload over USB instead of the boot image ramdisk: FB\_MAX\_DOWNLOAD rises to 256 MiB, oem ramdisk publishes the staged bytes as a read-only BlockIo volume, and the boot manager waits up to 20 s for it before UniXNU scans the volumes](https://github.com/donyanchen/UniXNU-piano/blob/f37b9f3866df66105c93483df2551e528b61836a/patches/uefi/piano-fastboot-payload.patch)
- `source`: [adds the UniXNULib LibraryClasses mapping that fixes the error 4000 firmware build failure](https://github.com/donyanchen/UniXNU-piano/blob/f37b9f3866df66105c93483df2551e528b61836a/patches/uefi/piano-dsc-unixnulib.patch)

## CPU 与中断 {#cpu}

`implemented`

组件: `ArmCpu`, `ArmDTPlatform`.

### 硬件与依赖

- SM8750 CPU nodes in the device tree, the ARM generic timer, and the GICv3 ranges of the SoC.

### 配置

- CONFIG\_XNU\_ARMCPU, CONFIG\_XNU\_ARM\_DT\_PLATFORM and CONFIG\_XNU\_NATIVE\_ARCH\_TIMER in piano\_defconfig.
- board.toml \[components\].include selects ArmCpu and ArmDTPlatform; \[kernel\].archives builds both as components.

### 操作步骤

- Run ./unixnu build kernel -D ../device and inspect logs/component-ArmCpu.log.
- Boot with cpus=1 in the kernel arguments \(board.toml \[payload\].kernel\_args\).

### 开发经验

- The first RAM boot is limited to one CPU through the cpus=1 kernel argument, so smp bring-up is not exercised yet.
- The BCM2837 panic buffer address in the shared code is not mapped on this device, so CONFIG\_XNU\_DT\_PANIC\_REGION is enabled to take the panic region from the device tree.

### 完成条件

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works.

### 当前范围

- Only one CPU is expected to be online on the first boot.

### 下一步

- Raise cpus once one CPU boots to user space.

### 证据

- `source`: [ArmCpu, ArmDTPlatform, native arch timer and DT panic region selections](https://github.com/donyanchen/UniXNU-piano/blob/f37b9f3866df66105c93483df2551e528b61836a/configs/piano_defconfig)

## 内存与 DMA {#memory}

`planned`

### 硬件与依赖

- DRAM layout, the reserved regions of the SM8750 firmware, and the owned memory size handed over by UEFI.

### 配置

- \[payload\] dram\_size = 0x180000000; \[payload.adt\] owned\_memory\_size = 0x100000000.
- \[adt.defaults.u32\] sleep-disabled = 1.

### 操作步骤

- Read the UEFI memory map from the firmware serial output and compare it with dts/piano.dts reservations.

### 开发经验

- The owned memory size is 4 GiB while the payload DRAM size is 6 GiB; no device boot has validated the split yet.

### 完成条件

- The kernel boots with the retained reservations intact and DMA of the storage and display controllers stays inside the owned range.

### 当前范围

- A device memory map has not been captured yet.

### 下一步

- Capture the UEFI memory map on the first boot and reconcile it with the device tree.

### 证据

按下一步操作收集证据。

## 存储与根卷 {#storage}

`implemented`

组件: `ShengUfs`, `VirtioMmioBlock`, `RamBlock`, `VerifiedRoot`.

### 硬件与依赖

- iPadOS 17.7.11 \(21H461\) IPSW, the signed verified-root policies from 044-76040-038.dmg and 044-76034-038.dmg, and the original kernelcache as the ABI reference.

### 配置

- CONFIG\_XNU\_NATIVE\_UFS, CONFIG\_XNU\_NATIVE\_VIRTIO\_BLOCK, CONFIG\_XNU\_NATIVE\_RAM\_BLOCK and CONFIG\_XNU\_VERIFIED\_ROOT\_PROBE.
- CONFIG\_XNU\_NATIVE\_UFS\_ARCHIVE, CONFIG\_XNU\_NATIVE\_VIRTIO\_BLOCK\_ARCHIVE, CONFIG\_XNU\_NATIVE\_RAM\_BLOCK\_ARCHIVE and CONFIG\_XNU\_VERIFIED\_ROOT\_ARCHIVE point at the archives the kernel step builds.
- \[payload\].kernel\_args carries native-ufs-root=1; \[payload.adt\].root\_match\_volume\_uuid names the APFS volume 04769D26-2CA0-4825-B443-E2E5F88300F2 of 044-76040-038.dmg.

### 操作步骤

- Run ./unixnu ipsw fetch -D ../device to place the IPSW under out/ipsw/21H461.
- Run python3 scripts/prepare-ufs-policies.py --tree &lt;tree&gt; --inputs &lt;ipsw&gt; --openssl-prefix $\(brew --prefix openssl@3\).
- Run ./unixnu build kernel -D ../device, which builds ShengUfs, VirtioMmioBlock and RamBlock and their bindings against kernelcache.decompressed.

### 开发经验

- The three storage components share one set of binding objects: 468d1fd put the raw bindings only in libShengUfs.a and let VirtioMmioBlock and RamBlock reuse them, which removed twelve duplicate symbols at link time.
- 67ad370 dropped a native\_ufs\_store\_write stub already provided by NativeUfs.o, and 2b1e6ec kept only the weak native\_ufs\_store\_write\_cached stub.
- The policies step has to read the DMG files from out/ipsw/21H461, not from the device output directory \(e04d7c2\).
- The verified-root probe needs -Wno-missing-include-dirs because the probe compiles outside the SDK include set \(70c6fc7\).
- The binding scripts take the kernelcache as the ABI reference and the PMGR audit reads it from tree/.cache/firmware/kernelcache.macho/, so the candidate step copies it there.

### 完成条件

- The kernel links with the storage archives, the prelink succeeds, and the payload declares the native UFS root.

### 当前范围

- No UFS controller has been probed on the device; the APFS root has never been mounted.

### 下一步

- Boot with native-ufs-root=1 and capture the first UFS probe output.

### 证据

- `source`: [extracts and signs the verified-root policies from the two iPadOS DMG inputs](https://github.com/donyanchen/UniXNU-piano/blob/f37b9f3866df66105c93483df2551e528b61836a/scripts/prepare-ufs-policies.py)
- `source`: [storage selections and archive paths the kernel links](https://github.com/donyanchen/UniXNU-piano/blob/f37b9f3866df66105c93483df2551e528b61836a/configs/piano_defconfig)

## 显示 {#display}

`planned`

组件: `GopFramebuffer`.

### 硬件与依赖

- UEFI GOP framebuffer handed over by the firmware, panel timing of the Pad 8 Pro and the ktz8866 backlight.

### 配置

- \[components\].include selects GopFramebuffer.
- \[payload\].kernel\_args carries offline-legacy-gop=1.
- \[adt.chosen.u32\] display-scale = 2 and display-rotation = 0.

### 操作步骤

- Read the framebuffer base and size from the UEFI output, then boot with offline-legacy-gop=1.

### 开发经验

- The splash region of the device is 0xfc800000 with a size of 0x2b00000, the same base the Pagani 13T port uses for FB\_BASE.
- The native Adreno path is disabled \(CONFIG\_XNU\_NATIVE\_ADRENO is not set\) and the legacy display path is disabled too, so the first boot is expected to use the GOP framebuffer.

### 完成条件

- The verbose XNU boot log is visible on the panel from a RAM boot.

### 当前范围

- No framebuffer handover has been observed on the device.

### 下一步

- Confirm the GOP base and stride against the firmware output on the first boot.

### 证据

- `source`: [GOP selection, display scale and rotation, and the offline-legacy-gop=1 argument](https://github.com/donyanchen/UniXNU-piano/blob/f37b9f3866df66105c93483df2551e528b61836a/board.toml)

## 输入 {#input}

`planned`

### 硬件与依赖

- Novatek touch controller, the pogo keyboard cover and the volume/power keys of the Pad 8 Pro.

### 配置

- \[adt.buttons.string\] compatible = buttons; \[adt.buttons.strings\] button-names = \[hold, voldown, volup\]; \[adt.buttons.u32\] home-button-type = 2.

### 操作步骤

- Boot with the buttons node present and read the HID devices from the boot log.

### 开发经验

- The device tree only describes the physical buttons; no touch or keyboard driver is selected yet.

### 完成条件

- Buttons and touch report events under XNU.

### 当前范围

- The touch controller is not part of the first RAM boot scope.

### 下一步

- Inventory the Novatek touch node and its interrupts for a later pass.

### 证据

按下一步操作收集证据。

## GPU {#gpu}

`not-applicable`

### 硬件与依赖

- Adreno 830 GMU and SMMU, which are out of scope for the first RAM boot.

### 配置

- CONFIG\_XNU\_NATIVE\_ADRENO is not set in piano\_defconfig.

### 操作步骤

- Not applicable until the first boot reaches user space.

### 开发经验

- The first RAM boot only needs a framebuffer console, so no GPU component is selected.

### 完成条件

- Not applicable while the GPU component set is empty.

### 当前范围

- SM8750 GPU support would need the Adreno 830 GMU, SMMU and firmware integration that the shared SM8750 support does not carry yet.

### 下一步

- Revisit after the first boot reaches a user session.

### 证据

按下一步操作收集证据。

## 网络 {#network}

`not-applicable`

### 硬件与依赖

- The Pad 8 Pro Wi-Fi module, which is not identified in the device tree yet.

### 配置

- No network component is selected in board.toml.

### 操作步骤

- Not applicable for the first RAM boot.

### 开发经验

- The community SM8750 support has no working Wi-Fi component for this platform, so the first boot is offline.

### 完成条件

- Not applicable while the network component set is empty.

### 当前范围

- The Wi-Fi module and its firmware are unidentified.

### 下一步

- Identify the Wi-Fi module from the hardware once boot is stable.

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`not-applicable`

### 硬件与依赖

- Pad 8 Pro speaker amplifiers, which are out of scope for the first RAM boot.

### 配置

- No audio component is selected in board.toml.

### 操作步骤

- Not applicable for the first RAM boot.

### 开发经验

- Audio is not needed to observe the verbose boot log.

### 完成条件

- Not applicable while the audio component set is empty.

### 当前范围

- The amplifier and codec parts of the Pad 8 Pro are not integrated.

### 下一步

- Revisit with the measured codec I2C addresses after boot.

### 证据

按下一步操作收集证据。

## 电源 {#power}

`implemented`

组件: `AppleKeyStoreState`.

### 硬件与依赖

- The original ApplePMGR implementation of the reference kernelcache, and the 340-entry provider table of IOPMGR.

### 配置

- CONFIG\_XNU\_SHENG\_PMGR in piano\_defconfig; the bootstrap defconfig leaves it off.
- \[payload\].kernel\_args carries sheng-pmgr=2.

### 操作步骤

- Build the bootstrap kernel without the PMGR binder and stage it as the reference candidate.
- Run ./unixnu build kernel -D ../device, which runs build-sheng-platform-power.py against that candidate.
- Read logs/archive-15-build-sheng-platform-power.log.

### 开发经验

- build-sheng-platform-power.py audits the AMFI read/OR/write sequence and the AppleT8011PMGR provider slots of the reference candidate before it emits the archive, and refuses to build when either check fails.
- The instrument inherits only the two original AON slots \(320, 321\) from ApplePMGR and refuses every unimplemented slot through unavailable\(\), so a missing power backend stops instead of writing.
- The bootstrap pass cannot run the same binder because the binder is the thing that needs the candidate it produces; the candidate step therefore strips it from \[kernel\].archives for that pass only.
- The archive is registered late \(llvm-objcopy removes \_\_DATA,\_\_mod\_init\_func\) and the script asserts the late registration cannot change the instructions of the object.

### 完成条件

- The kernel links with libShengPlatformPower.a force-loaded and keeps the original AMFI and PMGR dispatch unchanged.

### 当前范围

- The instrument is a refusal-first integration, not a functional power backend, and is not runtime qualified \(runtime\_qualified = false in its build report\).

### 下一步

- Read the sheng-pmgr=2 output on the first boot and record which slots refuse.

### 证据

- `source`: [guarded PMGR provider that inherits only the original AON slots](https://github.com/donyanchen/UniXNU-piano/blob/f37b9f3866df66105c93483df2551e528b61836a/package/ShengPlatformPower.cpp)
- `source`: [candidate-backed audit, original bindings and late registration of the PMGR archive](https://github.com/donyanchen/UniXNU-piano/blob/f37b9f3866df66105c93483df2551e528b61836a/scripts/build-sheng-platform-power.py)

## 镜像组装 {#packaging}

`planned`

组件: `DarwinBoot`, `XnuPrelink`, `SoftwareAES`.

### 硬件与依赖

- The linked XNU kernel, the prelink tool at kits/XnuPrelink, the iPadOS 17.7.11 kernelcache as the prelink hash reference, and the DarwinBoot booter.

### 配置

- \[kernel.prelink\] tool = kits/XnuPrelink/emit\_prelink.py, kernel = build/xnu/ios-obj/DEVELOPMENT\_ARM64\_BCM2837/mach.development.bcm2837.unstripped.noctf, slide = -0x1000000.
- \[kernel.prelink\].kernelcache\_sha256 pins the 21H461 kernelcache; \[kernel.prelink\].roots lists the eleven IOKit and kext roots the prelink closure keeps.
- \[bootimg\] embed\_payload = true, partition = unixnu, lba 44928768..61705983 at 4096 bytes per LBA, with OS and SystemOS windows.

### 操作步骤

- Run ./unixnu build kernel -D ../device, then ./unixnu build package -D ../device.
- Run ./unixnu build firmware --uefi ../uefi/deps/Mu-Silicium, ./unixnu build payload -D ../device and ./unixnu bootimg -D ../device.

### 开发经验

- The kernel links and prelinks successfully on the macOS runner: kernel.macho sha256 4c9dcef0... was produced in run 42755922774.
- The DarwinBoot firmware package registers the board store hooks and the VerifiedRoot policy archive \(5e6b930\).
- The payload requires the linked kernel to carry the sheng PMGR integration; dropping CONFIG\_XNU\_SHENG\_PMGR or the archive makes it fail with 'native UFS root kernel lacks the linked sheng PMGR integration'.
- The boot image targets a unixnu partition, but the device currently has only userdata, super and metadata. The Partition Manager layout and the DSU-style approach of the Pagani port are both still open.

### 完成条件

- Kernel and prelink succeed, the payload contains every declared input, and boot.img matches the bootloader format and size limit.

### 当前范围

- payload and bootimg have not completed yet, and no boot img has been flashed or RAM-booted.

### 下一步

- Complete the payload and bootimg steps, then decide between a unixnu partition and a DSU-style RAM boot before touching the device.

### 证据

- `source`: [prelink tool, kernel path, slide, roots and the boot image partition geometry](https://github.com/donyanchen/UniXNU-piano/blob/f37b9f3866df66105c93483df2551e528b61836a/board.toml)
- `source`: [kernel, package, firmware and payload steps pass on run 42812944686 \(head 0c76f70\); the payload step emits payload/payload.img at 160 MiB and the hardware device tree at device-tree/hardware.dtb, and the boot image step takes both --uefi and --dtb because it compiles BootShim, runs the Mu-Silicium mkbootimg.py and embeds the device tree in the image header](https://github.com/donyanchen/UniXNU-piano/blob/f37b9f3866df66105c93483df2551e528b61836a/.github/workflows/package-bare-metal.yml)
- `source`: [bootimg rejected run 42816650617 with 'the ARM64 image header does not describe the shim plus the firmware volume': the pinned Mu-Silicium writes FD\_SIZE alone into the image\_size field \(0x300000\), while bootimg requires len\(shim\) + FD\_SIZE \(0x300070\). The patch sets the field to 'FD\_SIZE + \_Payload - \_Head'. It also writes 0 into the text\_offset field instead of FD\_BASE, because piano's ABL reads text\_offset as a displacement from the load address: the absolute 0xA7100000 made it place the image outside its reservation and the tablet returned to fastboot with a black screen after 'Booting OKAY'. The stock piano kernel reports text\_offset 0x0; an aarch64-none-elf build of the patched shim gives 112 shim bytes with \_Payload at 0x70, text\_offset 0x0 and image\_size 0x300070](https://github.com/donyanchen/UniXNU-piano/blob/f37b9f3866df66105c93483df2551e528b61836a/patches/uefi/bootshim-image-size.patch)
- `source`: [piano's DeviceBootManagerAfterConsole starts the ESP loader and AndroidBoot and never started UniXNU.efi, so the menu the board builds into its own firmware volume was unreachable; the patch calls StartFvApp with UniXNU.efi's FILE\_GUID \(9B665204-A133-47A2-9396-9E2B370A4E25\) before the ESP and Android fallbacks](https://github.com/donyanchen/UniXNU-piano/blob/f37b9f3866df66105c93483df2551e528b61836a/patches/uefi/piano-fastboot-payload.patch)
- `source`: [Mu-Silicium SEC overwrites x0 before it reads it, so the device tree pointer the Android bootloader passes is lost; UniXNURamDiskDxe then reports 'no entry argument HOB' and never publishes the payload volume, which leaves the boot menu without an entry. The patch keeps x0 in x19 across the platform initialisation, passes it to SecEntry and builds the DAEE82E6-8090-4E72-BFB9-78C13CD4E359 HOB once the HOB list exists \(the same fix the marble port needed\)](https://github.com/donyanchen/UniXNU-piano/blob/f37b9f3866df66105c93483df2551e528b61836a/patches/uefi/mu-sec-entry-arg.patch)
- `source`: [bootimg.py required text\_offset to equal FD\_BASE, which is the Mu-Silicium convention, while the ARM64 specification defines the field as a displacement from the load address and piano's ABL reads it that way \(its stock kernel reports 0\). The shim now writes 0, so the patch accepts 0 or the firmware base and keeps the image-size check strict](https://github.com/donyanchen/UniXNU-piano/blob/f37b9f3866df66105c93483df2551e528b61836a/patches/unixnu-bootimg-text-offset.patch)
- `source`: [\[bootimg.image\] kernel\_compression = none follows uefi/piano.toml \[boot\_image\_kernel\] kernel\_compression = none; without it bootimg falls back to its gzip default for a board that asks for an uncompressed kernel field](https://github.com/donyanchen/UniXNU-piano/blob/f37b9f3866df66105c93483df2551e528b61836a/board.toml)

## 诊断 {#diagnostics}

`planned`

组件: `VerifiedRoot`, `AppleKeyStoreState`.

### 硬件与依赖

- UEFI serial output, the XNU verbose boot log, and the boot\_progress\_poll weak stub added in d185787.

### 配置

- CONFIG\_XNU\_EARLY\_BOOT\_PROGRESS is enabled; CONFIG\_XNU\_BOOT\_PROGRESS is not set.
- \[payload\].kernel\_args carries -v, debug=0x14e, startup\_debug=0 and pagani-platform-status=1.

### 操作步骤

- Capture the UEFI serial console during fastboot boot.
- Read the panic and progress lines from the captured output.

### 开发经验

- The early boot progress path needs boot\_progress\_poll, which a weak stub provides until a board implementation exists \(d185787\).
- Several patch series add panic output for early boot \(zzzz-early-boot-progress, zzzzz-root-panic-progress, zzzz-boot-progress-panic-output\), so a failure before serial init still reaches the screen.
- piano has no serial console, so the first UEFI boots gave no evidence about the payload: UniXNURamDiskDxe publishes nothing and the menu only said 'no boot entry found'. scripts/prepare-unixnu-diagnostics.py rewrites that line during packaging so it reads 'payload volume missing' or 'config unreadable', which separates a missing initrd handoff from an unreadable FAT volume without any cabling.

### 完成条件

- Each claimed milestone has a reproducible command, a matching image revision and an accessible result.

### 当前范围

- No serial capture of a device boot exists yet.

### 下一步

- Set up a serial or pstore capture before the first RAM boot.

### 证据

- `source`: [makes the built-in fallback message report whether the payload volume is reachable, so a board without a serial console can be diagnosed from the menu alone](https://github.com/donyanchen/UniXNU-piano/blob/f37b9f3866df66105c93483df2551e528b61836a/scripts/prepare-unixnu-diagnostics.py)
- `source`: [early boot progress and panic output patches applied to the XNU tree](https://github.com/donyanchen/UniXNU-piano/blob/f37b9f3866df66105c93483df2551e528b61836a/patches/xnu/series)

</div>
