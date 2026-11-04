# OnePlus Pad 2 Pro \(OPD2413\) \(xingxing19035\)

[xingxing19035/UniXNU-erhai](https://github.com/xingxing19035/UniXNU-erhai)

<div v-pre>

OnePlus Pad 2 Pro \(OPD2413\) bring-up on SM8750. The board follows the official device repository format: an iPad7,1 / iPadOS 17.7.11 userland, one boot CPU, a prelinked kernel without AMFI, and no root file system yet.

源记录: [porting.toml](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/porting.toml), `1d6a90ee37874082a5bd53bfa92321ead20a52ee`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `host-verified` |
| [固件与启动](#firmware) | `host-verified` |
| [CPU 与中断](#cpu) | `planned` |
| [内存与 DMA](#memory) | `planned` |
| [存储与根卷](#storage) | `planned` |
| [显示](#display) | `planned` |
| [输入](#input) | `host-verified` |
| [GPU](#gpu) | `planned` |
| [网络](#network) | `planned` |
| [cellular](#cellular) | `not-applicable` |
| [音频](#audio) | `planned` |
| [电源](#power) | `planned` |
| [镜像组装](#packaging) | `host-verified` |
| [诊断](#diagnostics) | `device-verified` |

## 配置 {#configuration}

`host-verified`

组件: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`, `DarwinBoot`.

### 硬件与依赖

- The board identity: OnePlus Pad 2 Pro, OPD2413, SM8750, and the iPad7,1 / iPadOS 17.7.11 profile the board runs.
- The SoC source that owns the SM8750 DTSI, the SoC configuration fragment and the SoC patch series.
- The component catalog in the UniXNU checkout, and the archive recipes each selected component needs.

### 配置

- board.toml selects the SM8550-free SM8750 path: soc\_source = sm8750, os\_profile = ipados-17.7.11-21H461, defconfig erhai\_defconfig, and the complete config fragment and patch series lists.
- The component selection is the official template set: ArmDTPlatform, ArmCpu, SoftwareAES, XnuPrelink and DarwinBoot. Every one of them has an area in this record.
- feeds.toml pins the SM8750 SoC source by repository and a 40-character commit.

### 操作步骤

- Copy the official device template with cp -R examples/device, rename configs/example\_defconfig to configs/erhai\_defconfig and dts/board.dts to dts/erhai.dts, then complete every file the template marks.
- Run ./unixnu defconfig erhai\_defconfig -D ../UniXNU-erhai, then ./unixnu fetch -D ../UniXNU-erhai, ./unixnu status --json and ./unixnu tree.
- Read the resolved ARM64, SoC, OS and device profiles, the component revisions, the overrides and the patch order in the status output.

### 开发经验

- SM8750 has no shared SoC repository under the UniXNU organization, so the port pins a community SoC repository by commit, the same way the other SM8750 ports do. The shared repository has to own the SoC layer before release.
- The prelink roots of the OS profile include AMFI and the Apple policy manager. On this board AMFI panics with "AMFI: No PMGR" because nothing publishes a policy manager nub, so the board replaces the root set with the reduced set the other SM8750 ports use.
- The early security initializer of the OS profile runs the original AppleMobileFileIntegrity initializer, so the board removes that key for its own OS profile instead of leaving it in place.
- Every source pin resolves on the host. The official fetch wrote unixnu.lock with the nine upstream commits, and a second run of the same command resolves all of them from the cache without contacting a remote, which is the documented behaviour of a clone that already sits on the wanted commit.
- The direct route of the build host to github.com sustained about 13 kB/s and aborted the pack transfer of the XNU source with an early EOF, so the fetch only completed through a proxy with a Japan exit node. The pins are the upstream commits either way, and the proxy is a property of the host, not of the board.
- The build line of this board runs on the macOS runner of the workflow of this repository. The workflow checks out the device repository, the UniXNU checkout at the revision this record was written against and the firmware checkout of the board with its submodules, installs the toolchain the official requirements guide names, checks the platform seed of the unit and runs the official packaging script. The seed check accepts the 64-bit Qualcomm chip serial of the unit and the workflow stops before the build when the secret is missing.
- That build line has run to success on the workflow: run 41692537288 at this head published the four artifacts the packaging area records, and the same head built successfully twice from two clean checkouts.
- The workflow of this repository carried a temporary diagnostic step that printed the generated files of the firmware build, because the run of the diagnostics area needed the generated code of the DXE core read back. The step was reverted in the same day, the workflow is the official form again, and the change of the workflow is recorded in the configuration area rather than left in the history alone.
- The workflow pins the firmware checkout of the board to a revision, so the firmware volume of every run is built from the same commit instead of from the head of the branch at the moment of the run.
- The packaging workflow of this repository builds the firmware of the board at revision 18a9d7bb5c0bb42f6dd57406b5882ae23388d4f8, the revision that runs the DXE phase without the driver stack of the vendor.

### 完成条件

- Every source pin resolves and unixnu status shows the intended profiles, overrides and patch order.
- Every selected component has a record area, an archive recipe and a board hook.
- The record checker reports fourteen structured areas checked and no error.

### 当前范围

- The pins, the board configuration and the patch order are host verified, and the kernel, the firmware volume and the boot image of this board have built successfully on the macOS runner of the workflow. The unit has run the firmware volume of this port once and that run stops in the DXE phase, so the configuration of the board is not verified on the unit yet.
- The SoC source is still a community repository and not a repository under the UniXNU organization. That stays a release blocker.

### 下一步

- Move the SM8750 SoC layer into a reviewed repository under the UniXNU organization before the release.
- Record the result of the next bring-up of the unit in the diagnostics area, once the DXE phase of the firmware runs past the assert.
- Record the run of the packaging workflow that builds the firmware revision 18a9d7bb in the diagnostics area, once the unit has run it.

### 证据

- `source`: [The eight porting steps, the template copy command and the completion requirements this record follows.](https://unixnu.com/porting/steps)
- `source`: [The tracked file list, the resolve and verify commands, and the format 2 board configuration fields used in board.toml.](https://unixnu.com/porting/device-repository)
- `source`: [The official format 2 board of a working SM8550 device, used as the reference for the section layout of board.toml.](https://github.com/UniXNU/UniXNU-sheng/blob/main/board.toml)
- `source`: [The SM8750 SoC layer that supplies the DTSI, the SoC configuration fragment and the SoC patch series pinned in feeds.toml.](https://github.com/IssacL04/UniXNU-sm8750-common/blob/main/soc.toml)
- `device`: [The unit of this port identifies itself as OPD2413 with the SM8750P SoC on build OPD2413\_16.0.10.600\(CN01\), and reports the platform seed 0000045a67bdf5ff that payload.adt.unique\_chip\_id reads from the environment.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-03-device-probe.md)
  Command: <code>adb shell getprop ro.product.model ro.boot.chipecid ro.soc.model ro.build.display.id</code>. Revision: `585c5adca2c34624f42342550a18e995354049fd`.
- `host`: [The official fetch resolves the nine pinned sources and writes unixnu.lock, a second run of the same command resolves them from the cache without a remote, every clone sits on the commit of the lock, the record checker reports no error, and the packaging script in check mode lists the 61 patches of the series in application order.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-03-fetch-lock.md)
  Command: <code>python3 unixnu fetch -D ../UniXNU-erhai &amp;&amp; python3 unixnu status --json -D ../UniXNU-erhai &amp;&amp; python3 unixnu tree -D ../UniXNU-erhai &amp;&amp; python3 scripts/porting-record.py check --device ../UniXNU-erhai &amp;&amp; scripts/package.sh --check --os 17</code>. Revision: `3fa5ff5f409398c0555a9561d6437ce5d4c3b3b7`.
- `host`: [The workflow checks out the firmware repository of the board at revision e2b37af0a12b6c57cd18a015c181fafb41bdb99b, the revision that builds DevicePathDxe, DiskIoDxe and PartitionDxe from upstream source instead of the vendor binaries.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/.github/workflows/package.yml)
  Command: <code>grep -n uefi-erhai -A2 .github/workflows/package.yml</code>. Revision: `e2b37af0a12b6c57cd18a015c181fafb41bdb99b`.

## 固件与启动 {#firmware}

`host-verified`

组件: `DarwinBoot`.

### 硬件与依赖

- The official OnePlus fastboot archive that carries the firmware inputs of this board.
- The Mu-Silicium device configuration, the DSC path and the firmware volume path of the board.
- The firmware volume layout the stock bootloader expects: the flash descriptor base and the boot shim.

### 配置

- board.toml \[firmware\] names the erhai device configuration, the OnePlus erhaiPkg DSC, the SILICIUM\_UEFI.fd firmware volume path and the Mu submodules the board needs.
- \[firmware.defines\] sets the board model and the secure boot, memory protection and ship mode values of the board.
- \[bootimg\] publishes the splash region node the stock bootloader expects, with the address and size read from the live device tree of the unit.
- \[payload\] sets tools = true, which adds the Tools entry to the generated boot menu. The firmware log exporter publishes its QR pages under that entry, so the first bring-up can be read from the phone itself.

### 操作步骤

- Fill the \[firmware.image\] archive entry with the OnePlus release URL, the SHA-256, the MD5 and the byte count of the official fastboot archive.
- List every extracted firmware input with its source and its SHA-256 in proprietary-files.txt.
- Wire the UniXNU modules into the platform package: the boot menu, the boot option registration and the firmware log exporter in the DSC \[Components\] and in the FDF, the RAM disk driver and the XNU loader in the DXE module list, the UniXNULib and FdtLib and HobLib mappings in the DSC \[LibraryClasses\], and the Advanced Logger access, QR encoder, assert and hardware port libraries with the DXE core instance of the logger. The board name goes into gUniXNUPkgTokenSpaceGuid.PcdUniXNUDeviceModel.
- Run the packaging script, which runs the preflight checks, the firmware build, the payload build and the boot image assembly.

### 开发经验

- The firmware build of this board has run on the macOS runner of the workflow of this repository: run 41692537288 at this head completed to success and published the four artifacts the packaging area records, and the same head completed an earlier run of the same script to success 83 minutes before it, from a second clean checkout. The firmware volume rides in the kernel field of the boot image and the volume built is exactly the window the device configuration names.
- The boot image of the run round-trips against its inputs: the header is version 0 with a 4096 byte page, the kernel slot is the gzip stream of the BootShim plus the firmware volume followed by the compiled device tree of 3410 bytes with a valid FDT header, the gzip stream decompresses to 2785472 bytes with the BootShim header carrying FD\_BASE 0xA7000000, and the firmware volume that follows the 192 byte shim declares FvLength 0x2A8000 with a file length of exactly 2785280 bytes. The ramdisk slot is byte for byte the payload.img of the run and nothing follows it in the image.
- The firmware inputs of this board are not published as a separate archive by the vendor. They are in the official over the air update of the unit: the uefi partition carries the firmware volume of the vendor and the vendor partition carries the firmware of the graphics controller. Both partitions are pinned by hash in proprietary-files.txt.
- The official boot image builder places the payload in the ramdisk field of the boot image. Whether the stock bootloader of this board replaces that field with the init\_boot ramdisk during a fastboot boot is not established: the first bring-up of this port did not answer it, because the image the official builder writes carries the header version 0 and the bootloader of the board loads that image without starting the firmware. The question stays open until the payload rides in an image the bootloader starts.
- The window of the firmware volume of this board is measured on the unit from the official package: the uefi partition holds an ELF image whose single program segment is loaded at 0xA7000000 and is 0x2A8000 bytes long, and the header of the volume inside it declares 680 blocks of 0x1000 bytes, which is exactly the size of that window. The configuration of the firmware of this board and the memory map follow that measurement.
- Every published SM8750 platform of the official firmware repository, the OnePlus 13 \(dodge\) and the OnePlus 13T \(pagani\) of the same vendor and the Xiaomi Pad 6S Pro \(sheng\) of the official reference board among them, places the firmware volume at 0xA7100000 with a size of 0x300000 and reserves the megabyte below it as FD\_Reserved. That is the window of their flash descriptor layout. The stock volume of this board starts at the base of that region instead, so the map of this board does not carry the FD\_Reserved entry and the Qualcomm PEI library that looks that region up by name finds nothing. The region the previous stage of this board occupies is not in the official package and is not described.
- The bootloader of this unit does not implement fastboot fetch, so the firmware inputs cannot be pulled from the device; they come from the official package.
- The vendor binary set of this board is not published: the Binaries submodule of the firmware repository is the public repository Project-Silicium/Device-Binaries and it has no erhai directory, at the pinned commit and at the head of the repository. The stock firmware volume of the unit holds the whole set: 111 modules of the DXE phase, the security core of the vendor and 94 raw files, among them the panel configuration of this board. All 111 modules of the DXE phase carry the file GUID of the same module of the OnePlus 13 \(dodge\) set, so the path of each of them in the layout of that repository is known, and scripts/extract-vendor-binaries.py writes the set into Binaries/erhai of the firmware repository with the INF wrappers that name it. The images are the ones of this board, not the ones of the sibling board.
- The 91 entries of Include/RAW.inc of the platform package, which was written from the published sets of the same vendor, are all in the stock volume of this board and every one of them carries the same name there. Two raw files of the volume are not in that list, the boot menu configuration and the logo, and the published platforms of the vendor do not ship them either.
- The firmware of the graphics controller of this board is in the vendor partition of the official package, under firmware/ of the erofs image: gen80000\_gmu.bin, gen80000\_sqe.fw, gen80000\_aqe.fw and gen80000\_zap.mbn. The first three are byte for byte the files the official firmware repository pins for this SoC generation. The fourth has the size the pin names and a different content, because the pin is the file of the OnePlus 13T board. The touch firmware is in the odm partition of the same package, under firmware/tp/24924/ of the erofs image, pinned in proprietary-files.txt.
- The touch controller of this board is the Novatek NT36536: the vendor device tree declares the compatible string novatek,nf\_nt36536 for the touch node of every overlay of this model, and the firmware name 0x2XN242CN00. The touch driver of the official project, ShengNovatekTouch, is a driver for the NT36532E controller, so it is a worked example and not a driver for this board. The panel of this board is the CSOT NT36532 2120 x 3000 at 144 Hz with dual DSC in video mode, and the panel configuration of it is in the stock firmware volume of the unit.
- The UniXNU integration of the firmware is modelled on the sheng platform of the official firmware repository, not on the dodge and pagani platforms. Only sheng carries the boot menu, the boot option registration, the RAM disk driver and the XNU loader; the two OnePlus platforms of the same SoC generation do not, because they are firmware-only ports.
- The vendor binary set of this board cannot be read out of the unit. The block devices of the phone are brw------- root root, the shell user is in no group that owns them, and the shell process cannot read them: a read of uefi\_a and of the boot LUN both return zero bytes. The bootloader of the unit does not implement fastboot fetch either, so the uefi partition of the official package is the only source of the vendor drivers of this board.
- The firmware volume of the unit holds no firmware of the graphics or of the touch controller: it carries the modules of the vendor and the raw files of the board, and nothing else. The firmware of the graphics controller is in the vendor partition of the package, under firmware/ of the erofs image. The touch firmware 0x2XN242CN00 is not in the volume and not in the vendor partition: it is in the odm partition of the package, and scripts/gen-touch-firmware.py extracts it from the FwUp container there.
- The Advanced Logger of the firmware log exporter is mapped to the DXE phases only. Its assert library and its debug library both consume the Advanced Logger library itself, whose instance is a DXE one, so a mapping for the whole build would leave the SEC phase without a library of the right type. The SEC and the PEI phase keep the serial and the null debug library of the platform. The scoping follows the recipe of the alioth record of the project.
- Every module the platform package names resolves in the tree it is built from, and every library class those modules consume is mapped by the DSC for the module type that consumes it. The check is in the device repository and runs before every firmware build.
- The touch firmware of the board is extracted by scripts/gen-touch-firmware.py from the FwUp container of the odm partition: the container carries a header that names the source path, the raw NT36536 image of 0x3F000 bytes and a trailer of 128 bytes, and the raw image is byte for byte the factory image FW\_NT36536\_HUAXING\_FAE.img of the same directory. The script verifies the pins of proprietary-files.txt and writes the image to firmware/novatek/ and the build cache; the extracted binaries stay out of the repository.
- The touch driver of the board owns the firmware it downloads: drivers/ErhaiNovatekTouch parses the header of the NT36536 image, verifies the file with the byte sum of the vendor check, and writes the ILM, the DLM and the two header copies to the SRAM of the controller.
- The firmware repository of this board is a fork of the upstream firmware repository, Project-Silicium/Mu-Silicium, with the platform package of this board and its boot shim configuration added. The submodules the firmware volume builds from are the public trees the upstream names: the Mu tree, the OEM sample tree, the basecore tree, the Silicium ACPI tree and the openssl tree of the Silicium package.
- The vendor binary set of this board cannot be fetched from the vendor, because the vendor does not publish it. It is extracted from the stock firmware volume of the official package of the unit and published as a release asset of this repository, so that a build on another machine uses the same bytes without a vendor archive. The bundle is deterministic: the same set packs to the same bytes on every run.
- The board check of the preflight reads the name of the device repository from its remote when the checkout directory does not carry it. The workflow of this repository checks the device repository out as "device", the layout the workflow of the official reference device repository uses, and the first build of the board failed on that rule. The rule itself is unchanged: the name of the board has to be the name of the repository or the repository name with the UniXNU- prefix in front of it, and a repository that belongs to another board is refused.
- The boot image the official builder writes is not the shape the vendor writes on this board. The stock boot image of the unit carries the version 4 in the field the legacy layout keeps the header version in, its boot shim is a PE image at 0x1000 and its kernel starts at 0x2000, and it has no ramdisk of its own: the ramdisk of the vendor, 2,720,615 bytes, sits in the init\_boot partition. The image this port builds carries the header version 0, the boot shim and the firmware volume in the kernel field at the offset the device configuration names, and the payload in the ramdisk field behind it, the shape the official reference board uses. Whether the bootloader of this board accepts that shape, and whether it replaces the ramdisk field with the ramdisk of the init\_boot partition, is measured on the first bring-up.
- The DXE phase of the firmware of this board runs without the driver stack of the vendor, because the shared memory of the system the stack reads lives in the internal memory of the secure world and cannot be reached in this boot path; the stack is kept in the firmware repository as Platforms/OnePlus/erhaiPkg/Include/DXE.vendor.inc and comes back when the board is entered the way the vendor enters it.
- The firmware revision of this board is 18a9d7bb5c0bb42f6dd57406b5882ae23388d4f8, the revision that drops the vendor stack from the phase, and the packaging workflow of this repository builds that revision.

### 完成条件

- The firmware image builds, enters UniXNU, publishes the framebuffer and preserves the documented memory reservations.
- Every firmware input in proprietary-files.txt is pinned by hash and the preflight check passes on a clean checkout.
- The boot image round-trips: the gzip payload, the appended device tree and the ramdisk bytes match their inputs.

### 当前范围

- The vendor binary set is pinned and the preflight fetches it, and the firmware build has run on the macOS runner: the volume in the boot image of run 41692537288 is exactly the 0x2A8000 bytes the window of the device configuration names. What has run on the unit is the boot itself, once: the firmware volume of this port executes on the board, the platform banner reaches the panel and the DXE core stops on an assert before the first driver is dispatched, so the volume has not entered UniXNU and has not published the framebuffer yet.
- The Mu-Silicium device configuration of this board exists in the firmware repository of the board, Resources/Configs/erhai.toml, next to the platform package Platforms/OnePlus/erhaiPkg. The upstream firmware repository does not carry this board, so the firmware repository of the board is a fork of it.
- The vendor binary set of this board is not published by the vendor. It is extracted from the stock firmware volume of the unit and published as the release asset erhai-firmware.tar.gz of the release firmware-1 of this repository, pinned by size and by hash in board.toml \[firmware.image\]. The preflight script scripts/fetch-erhai-firmware.py downloads it, checks the hashes and unpacks it under .cache/firmware, where the firmware checkout reads it from Binaries/erhai. The preflight check of the device repository verifies every file of the set against vendor-binaries.txt.
- The firmware volume window of this board is measured, but the region the previous stage occupies is not: the FD\_Reserved entry of the published platforms is not in the map of this board, so the addresses of the previous stage are not picked up by the Qualcomm PEI library.
- The ramdisk handling of the stock bootloader is not measured on this unit. The payload rides in the ramdisk field of the boot image, as the official boot image builder places it, and whether the bootloader replaces that field with the init\_boot ramdisk during a fastboot boot is an open question. A community port of the same board reports that it does; this port has not confirmed that and does not rely on it.
- The firmware volume of this board has not entered the boot manager yet: the revision that drops the vendor stack from the phase has not run on the unit.

### 下一步

- Measure the ramdisk handling of the stock bootloader on the first bring-up: boot the generated boot.img with fastboot boot, check whether the payload in the ramdisk field is the one that starts, and record whether the payload has to ride in the kernel field of the boot image instead.
- Read the region the previous stage of this board occupies, if the official fastboot package carries it, and describe it in the memory map of the board.
- Boot the generated boot image on the unit and record whether the firmware volume enters UniXNU and publishes the framebuffer, the criterion of this area that only the unit can answer.
- Boot the firmware volume of revision 18a9d7bb on the unit and record whether the phase reaches the menu of the boot manager.

### 证据

- `source`: [The firmware integration requirements the DSC and FDF have to meet, including the ram disk and file system support.](https://unixnu.com/porting/uefi-firmware)
- `source`: [A community port of the same board, kept as a lead and not as evidence: it reports the flash descriptor base 0xA7000000, the splash region at 0xfc800000 with size 0x2b00000, and that the bootloader replaces the ramdisk field. The first two are confirmed independently by the device evidence of this record, and the third is not: it is an open question in the limits of this area.](https://github.com/wally001012-cyber/UniXNU-erhai/blob/main/board.toml)
- `source`: [The packaging steps the device script runs, in the order the record reports them.](https://unixnu.com/porting/packaging)
- `source`: [The boot shim, flash descriptor window and boot image parameters of the OnePlus 13T platform of the official firmware repository, the model the firmware of this board follows.](https://github.com/UniXNU/uefi-sheng/blob/main/Resources/Configs/pagani.toml)
- `device`: [The unit of this port exposes the uefi, uefisecapp and splash partitions, the same set the firmware update of this device flashes, and its bootloader answers the read-only queries. The bootloader of this unit does not implement fastboot fetch: the command transfers nothing, so the firmware inputs have to come from the official package instead of from the device.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-03-device-probe.md)
  Command: <code>adb shell ls -l /dev/block/by-name/ and fastboot getvar all</code>. Revision: `585c5adca2c34624f42342550a18e995354049fd`.
- `device`: [The memory map of the board: forty-four reserved regions read out of the reserved-memory node of the vendor device tree, the window of the firmware volume that every published SM8750 platform uses, the display regions the board overlay confirms, and the two places where this board differs from the published platforms, the unreserved high frame rate compensation region and the region by region description of the radio region.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-03-firmware-memory-map.md)
  Command: <code>python3 scripts/extract-reserved-map.py --dts board.dts and python3 scripts/check-memory-map.py --map MemoryMapLib.c --config erhai.toml</code>. Revision: `585c5adca2c34624f42342550a18e995354049fd`.
- `device`: [Which firmware inputs of this board are reachable without the official fastboot package. The Adreno 830 firmware and the touch firmware are in none of the five images of the unit, the raw block devices are unreadable for the shell user and the bootloader does not implement fastboot fetch, so the vendor drivers of the stock uefi\_a cannot be pulled out of the phone. The bootloader does report the logical block size of the storage, 4096 bytes, and the size of every partition.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-03-firmware-inputs.md)
  Command: <code>grep -a -o -i -E 'XN242CN00|gen80000' &lt;image&gt; and adb exec-out dd if=/dev/block/by-name/uefi_a and fastboot getvar all</code>. Revision: `585c5adca2c34624f42342550a18e995354049fd`.
- `device`: [The stock firmware volume of this board, read out of the uefi partition of the official package of the unit: it is loaded at 0xA7000000 and is 0x2A8000 bytes long, its header declares 680 blocks of 0x1000 bytes, the modules of the DXE phase sit in two LZMA compressed volumes inside it, and the set of the board is 111 modules, the security core of the vendor and 94 raw files. Every file GUID of the DXE phase is the file GUID of the same module of the OnePlus 13 set of the public firmware binary repository, and the 91 entries of the raw file list of the platform package are all in it with the same names. The firmware of the graphics controller is in the vendor partition of the same package.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-03-firmware-volume.md)
  Command: <code>python3 scripts/extract-vendor-binaries.py --image uefi.img --out Binaries/erhai and dump.erofs --path /firmware/gen80000_gmu.bin vendor.img</code>. Revision: `0ef5e306c5b700432ffe3e1779d222ead3913c4d`.
- `source`: [The firmware log exporter integration this port follows: the exporter in the DSC \[Components\] and in the FDF, the Advanced Logger access and QR encoder libraries mapped from the Mu revision, the board name in gUniXNUPkgTokenSpaceGuid.PcdUniXNUDeviceModel and the Tools entry of the generated menu.](https://unixnu.com/porting/log-capture)
- `source`: [The UniXNU integration of the official reference board, which is the platform that carries the boot menu, the boot option registration, the RAM disk driver and the XNU loader. The two OnePlus platforms of the official firmware repository do not carry them.](https://github.com/UniXNU/uefi-sheng/blob/main/Platforms/Xiaomi/shengPkg/sheng.dsc)
- `host`: [The firmware configuration of this board checked against the trees it builds in: forty-two modules of the platform package resolve, the fifty-eight vendor paths are all in the manifest of the vendor binary set, and every library class those modules consume is mapped by the DSC for the module type that consumes it. The check runs as a preflight step of every firmware build. The revision is the commit of the UniXNU checkout the check reads the shared drivers from.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/scripts/check-firmware-modules.py)
  Command: <code>python3 scripts/check-firmware-modules.py</code>. Revision: `3fa5ff5f409398c0555a9561d6437ce5d4c3b3b7`.
- `host`: [The touch firmware extraction of the board: the FwUp container of the odm partition unpacks to the raw NT36536 image, which is byte for byte the factory image of the same directory, and the extracted image keeps the vendor bytes untouched with the sha256 proprietary-files.txt pins. The record map of the image and the download set ILM, DLM and the two header copies are in the evidence file.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-03-touch-firmware.md)
  Command: <code>python3 scripts/gen-touch-firmware.py</code>. Revision: `b9989e121cf85ecb9bb8557b5edc0f1c4630da7f`.
- `host`: [The vendor inputs of the firmware build travel through the preflight: the asset is downloaded, its size, its SHA-256 and its MD5 are checked against the pins of board.toml, it is unpacked under .cache/firmware and linked into the firmware checkout, and the archive is deleted afterwards. A second run reports the inputs as already fetched, and a bundle that does not match the pins is refused before anything is unpacked.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/scripts/fetch-erhai-firmware.py)
  Command: <code>python3 scripts/fetch-erhai-firmware.py</code>. Revision: `93cd4d06e6ccd5bb04d63cafa159cec026fc5bb0`.
- `host`: [The board configuration of this board passes the preflight check in three layouts: the local checkout, the checkout under the name the workflow gives it, and a repository of another board, which the check refuses.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/scripts/check-board.py)
  Command: <code>python3 scripts/check-board.py</code>. Revision: `b79a8d3e6c32927134538a22230f3bff1e410ba7`.
- `device`: [The boot image of the unit and the one the official builder writes: the stock boot image carries the header version 4, the boot shim of the vendor at 0x1000 and the kernel at 0x2000, and no ramdisk, while the stock init\_boot image carries the 2,720,615 byte ramdisk of the vendor and no kernel. The builder writes the header version 0, puts the boot shim and the firmware volume in the kernel field and the payload in the ramdisk field. The shapes differ, and the difference is measured on the first bring-up.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-03-boot-image-layout.md)
  Command: <code>python3 scripts/extract-dtb.py and the header dump of the stock boot images</code>. Revision: `585c5adca2c34624f42342550a18e995354049fd`.
- `host`: [The device tree of the boot image is built from the source and the include directories of board.toml \[device\_tree\], resolved through the same path contract the official build uses, because the assembled build tree never carries the SoC modules that the include needs. Run in the build tree of this checkout the script emits build/erhai/erhai.dtb of 3326 bytes from dts/erhai.dts with the dtsi files of the pinned sm8750 feed checkout as include.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/scripts/build-dts.py)
  Command: <code>python3 scripts/build-dts.py</code>. Revision: `93d282319d32e1d93005e6c717f6e71e049f2a92`.
- `host`: [The firmware build of this board on the macOS runner: run 41692537288 at this head published boot.img, kernel.macho, payload.img and package.manifest.json, and the boot image was measured against its inputs. The header is version 0 with a 4096 byte page, the kernel slot is the gzip of the 192 byte BootShim plus the firmware volume followed by a valid FDT of 3410 bytes, the volume declares FvLength 0x2A8000 with a file length of exactly 2785280 bytes, and the ramdisk slot is byte for byte the payload.img of the run.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-04-ci-package.md)
  Command: <code>gh run view 41692537288 --repo xingxing19035/UniXNU-erhai --json status,conclusion,headSha &amp;&amp; python3 verify-ci-boot.py</code>. Revision: `8b44290640f5e348891b59658d497b23972b0e7d`.
- `device`: [The firmware volume of this port on the unit: the volume of the run, carried in the kernel field of a boot image with the header version 4 and an empty signature region, executes on the board, prints the platform banner with the entry point of the DXE core, and then stops on an assert of the DXE core before the first driver is dispatched. The framebuffer is published by the platform before the assert, because the panel carries the banner.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-04-first-device-run.md)
  Command: <code>adb reboot bootloader &amp;&amp; fastboot boot boot-v4-sig0.img</code>. Revision: `246f1c4232a87df0d18b0406748937036d403713`.
- `host`: [The driver stack of the vendor is unreachable in this boot path, so the phase of the firmware of this board runs without it and the stack is kept in the firmware repository for the way the vendor enters the board.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-04-dxe-assert-root-cause.md)
  Command: <code>git -C ../uefi-erhai show --stat 18a9d7bb</code>. Revision: `18a9d7bb5c0bb42f6dd57406b5882ae23388d4f8`.

## CPU 与中断 {#cpu}

`planned`

组件: `ArmCpu`.

### 硬件与依赖

- The CPU topology of the board, measured on the unit: eight cores, cores 0 to 5 in cluster 0 at up to 3532800 kHz and cores 6 and 7 in cluster 1 at up to 4320000 kHz, with the two clusters on separate frequency policies.
- The GIC layout: GICD at 0x16000000 with size 0x10000, the redistributor region at 0x16080000 with size 0x200000 and a 0x40000 stride.
- The architectural timebase of the SoC: 19.2 MHz.

### 配置

- dts/erhai.dts enables the boot CPU only and keeps the seven secondary cores disabled.
- The ADT publishes one core through payload.adt.cpu\_regs = 0, and the kernel command line carries cpus=1.
- The SoC configuration fragment enables the architectural timer and the PAN handling the Oryon cores need.

### 操作步骤

- Read the core list and the MPIDRs from the board, and check them against the SoC DTSI.
- Bring the board up with one CPU, then confirm the kernel reaches the platform expert and the timer ticks.
- Enable the secondary cores one cluster at a time, with the secondary entry path, the per-core stacks and the redistributor bring-up qualified first.

### 开发经验

- The SMP patch of the SoC series stays in the patch order, but the board publishes one core: the secondary-core entry path has not been exercised on this board.
- The timebase of the SoC DTSI, 19.2 MHz, matches the CNTFRQ\_EL0 value measured on the unit.
- The measured topology of the unit puts the prime cluster in cluster 1: cores 6 and 7 reach 4320000 kHz, while cores 0 to 5 stop at 3532800 kHz. The boot core cpu0 is therefore a 3.53 GHz core of the six-core cluster, and the two 4.32 GHz cores are the ones a later stage has to publish together with the secondary entry path.
- The two clusters are separate frequency policies with separate 16 step tables, so the board power policy has to treat cluster 1 as the prime cluster.

### 完成条件

- Every enabled CPU reaches its entry checkpoint and the timer and IPI handling work on each enabled CPU.
- The published CPU count matches the enabled CPU count in the device tree.
- The GIC and redistributor layout of the board matches the memory map of the firmware.

### 当前范围

- Only the boot CPU is published; the SMP path is untested.
- The interrupt controller layout and the timer rate could not be read from the unit, but the vendor device tree of the official fastboot images confirms the GICD, the GICR, the ITS and the 19.2 MHz timebase that the pinned SoC device tree carries.
- The CPU frequency scaling and the board power policy are not part of this port yet, although the frequency tables of both clusters are now measured.

### 下一步

- Bring the board up with one CPU and record the first checkpoint, then enable the second core and repeat.
- Record the GIC state that the ArmCpu diagnostics report.

### 证据

- `source`: [The SoC device tree: eight CPUs at MPIDR 0, 0x100 to 0x500, 0x10000 and 0x10100, a 19.2 MHz timebase, the GIC at 0x16000000 and the PSCI method smc.](https://github.com/IssacL04/UniXNU-sm8750-common/blob/main/dts/sm8750.dtsi)
- `source`: [A community port of the same board, kept as a lead and not as evidence: it reports the same GICD, GICR and timebase values. The values of this record come from the vendor device tree of the unit, and the single-CPU bring-up profile is a decision of this port.](https://github.com/wally001012-cyber/UniXNU-erhai/blob/main/board.toml)
- `source`: [The checkpoint order the CPU area reports against.](https://unixnu.com/porting/bring-up)
- `device`: [The bootloader of the unit of this port reports hardware revision 20000 and the SM8 UFS storage variant, and the unit runs the SM8750P SoC that the pinned SoC device tree describes.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-03-device-probe.md)
  Command: <code>fastboot getvar all and adb shell getprop ro.soc.model</code>. Revision: `585c5adca2c34624f42342550a18e995354049fd`.
- `device`: [The core topology of the unit: cores 0 to 5 in cluster 0 at up to 3532800 kHz and cores 6 and 7 in cluster 1 at up to 4320000 kHz, with separate frequency policies for the two clusters.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-03-hardware-inventory.md)
  Command: <code>for c in 0 1 2 3 4 5 6 7; do echo cpu$c $(cat /sys/devices/system/cpu/cpu$c/topology/cluster_id) $(cat /sys/devices/system/cpu/cpu$c/cpufreq/cpuinfo_max_freq); done</code>. Revision: `585c5adca2c34624f42342550a18e995354049fd`.
- `device`: [The vendor device tree confirms the MPIDR of every core, the capacity of 0x700 for the six cores of cluster 0 against 0x766 for the two cores of cluster 1, the GICD at 0x16000000 with the redistributor region at 0x16080000 and the stride 0x40000, the ITS at 0x16040000 and the 19.2 MHz timebase of the timer.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-03-vendor-device-tree.md)
  Command: <code>dtc -I dtb -O dts on the device tree carved out of vendor_boot.img</code>. Revision: `585c5adca2c34624f42342550a18e995354049fd`.

## 内存与 DMA {#memory}

`planned`

组件: `ArmDTPlatform`.

### 硬件与依赖

- The DRAM window of the board at 0x80000000 and the size the iPad7,1 kernelcache is qualified against.
- The reserved regions the stock bootloader and the firmware volume need.
- The SMMU and the DMA engines of the SoC.

### 配置

- dts/erhai.dts declares one contiguous DRAM range of 2 GiB at 0x80000000, and board.toml carries the same size as payload.dram\_size.
- The reserved memory nodes of the board carry the splash region at 0xfc800000 with size 0x2b00000.
- The ADT hands a 256 MiB window to DarwinBoot through payload.adt.owned\_memory\_size.

### 操作步骤

- Compile the board device tree and inspect the ADT resources the drivers consume.
- Compare the memory map of the firmware with the DRAM range and the reservations of the device tree.
- Check every DMA engine against its allocated range and its cache policy.

### 开发经验

- The firmware memory map of this board holds no contiguous run large enough for a 4 GiB window: the largest single reserved descriptor is the 256 MiB kernel reservation, so a larger request can never be satisfied and the loader reports EFI\_OUT\_OF\_RESOURCES.
- The window is taken from the reservation, not from the conventional heap, so the request has to match the reservation exactly.
- The 16 KiB slide bias of the window is cosmetic: the loader copies each segment relative to the reservation base, so any 16 KiB aligned address works.
- The unit of this port carries 16 GB of DRAM: the kernel reports 15803076 kB of total memory. The board still declares 2 GiB, because the physmap and the page allocator must not reach addresses that no DRAM backs and the iPad7,1 kernelcache is qualified against that window. The reference boards declare less than the fitted DRAM for the same reason.
- The live device tree of the unit lists 64 reserved regions. Their names carry the addresses of the static ones, and the ports of the port have to stay clear of the firmware areas: the hypervisor region at 0x80000000, the AOP regions at 0x81c00000 to 0x81c80000, the TZ region at 0xd8000000, the xBL ramdump region at 0xb8000000 and the camera, video and GPU firmware regions between 0x9b000000 and 0x9cb00000.

### 完成条件

- All handoff regions are accounted for and the ADT resources match the memory map of the firmware.
- Every enabled DMA engine accesses its allocated range with the documented cache policy.
- The kernel memory map matches the DRAM range published in the device tree.

### 当前范围

- The size of the reserved regions could not be read on the unit: the shell user may list the node names but not the property values, so only the addresses of the static regions are confirmed there. The vendor device tree of the official fastboot images supplies the sizes of all of them.
- The SMMU takeover for the GPU and the display engines is not part of this port yet.

### 下一步

- Confirm the address and the size of the splash region against the firmware memory map of the official package.
- Record the reserved regions with their sizes from a device tree dump of the official package and compare them with the device tree of this repository.

### 证据

- `source`: [A community port of the same board, kept as a lead and not as evidence: it reports the same DRAM base 0x80000000 and the same 256 MiB kernel window. The base is confirmed by the live device tree of the unit and the window by the memory map of this board in the firmware repository.](https://github.com/wally001012-cyber/UniXNU-erhai/blob/main/board.toml)
- `source`: [The device tree conversion rules and the ADT resource layout the memory area reports against.](https://unixnu.com/porting/device-tree)
- `device`: [The live device tree of the unit of this port places the hypervisor region at gunyah\_hyp\_region@80000000, which confirms the DRAM base the board device tree uses. The shell user may list the reserved-memory node names but not read their properties, so the size of the DRAM window and the address of the splash region are still not confirmed on this unit.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-03-device-probe.md)
  Command: <code>adb shell ls /sys/firmware/devicetree/base/reserved-memory</code>. Revision: `585c5adca2c34624f42342550a18e995354049fd`.
- `device`: [The total memory of the unit is 15803076 kB, so the board carries 16 GB of DRAM, and the live device tree lists 64 reserved regions with the addresses of the static ones in their node names.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-03-hardware-inventory.md)
  Command: <code>adb shell cat /proc/meminfo and adb shell ls /sys/firmware/devicetree/base/reserved-memory/</code>. Revision: `585c5adca2c34624f42342550a18e995354049fd`.
- `device`: [The vendor device tree of the official fastboot images gives the size of every static reserved region, and the board overlay gives the splash region as 0xfc800000 with the size 0x2b00000 and the label cont\_splash\_region, which are the values the board device tree of this repository declares.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-03-vendor-device-tree.md)
  Command: <code>dtc -I dtb -O dts on the device trees carved out of dtbo.img and vendor_boot.img</code>. Revision: `585c5adca2c34624f42342550a18e995354049fd`.

## 存储与根卷 {#storage}

`planned`

### 硬件与依赖

- The UFS host of the board at 0x1d84000 and its QMP PHY, and the storage geometry of the unit.
- The partition layout: the userdata range, the logical block size and the OS and SystemOS windows.
- The root volume policy of the target OS profile.

### 配置

- No storage component is selected in board.toml yet, and CONFIG\_XNU\_NATIVE\_UFS is not set in the defconfig.
- The UFS nodes of the device tree stay disabled.
- The OS profile supplies the userdata windows and the root volume UUID.

### 操作步骤

- Read the storage geometry of the unit and add the userdata range to board.toml \[userdata\].
- Select the UFS component, add its archive recipe and its board hooks, and enable the matching defconfig entries.
- Qualify the host, the reads and the root mount separately, and record the result of each one.

### 开发经验

- This port targets the XNU entry, not a root file system: the storage path is not enabled yet, so the payload reaches the platform expert and stops there, and neither the root volume nor the userland is configured.
- The unit of this port uses six block devices: the dynamic partition container and the user data partition are on sda, the boot chain and the firmware partitions are on sde, and sdb, sdc, sdd and sdf carry the remaining stages. The UFS host exposes six logical units and three vendor units, and the logical and the erase block size are both 0x1000.
- The bootloader of the unit reports the size of 119 of the 129 partitions, and the running system names every partition and says which logical unit and which position it has. Together they give the complete inventory of the storage: the data unit sda carries fifteen partitions and adds up to 124196853 sectors, and the boot chain sits on sde, which holds the paired slots of the unit.
- The user data partition is the fifteenth and the last partition of the data unit, with 0x72FE4C9000 bytes, 120579273 sectors of 4096 bytes, which is 460 GiB. The file system on it covers the whole partition apart from two megabytes that the file system reserves for itself.
- The bootloader of this unit is a UEFI implementation, it reports the platform name sun, and it runs a two slot boot scheme where the current slot is b. The system partitions are not slotted, so only the boot chain is paired.
- The bootloader does not implement fastboot fetch, so the first and last LBA of the user data partition cannot be pulled from the unit and come from the partition table of the official package.
- The official way to read that geometry is the one of the tb365fc record of the project: the partition table of the boot LUN with sgdisk, on a rooted device. The unit of this port is not rooted, adb root is refused and there is no su, so the record of this area names the partition table of the official package as the source.
- The logical block size of the storage is measured, not assumed: the bootloader reports logical-block-size 0x1000, which is the lba\_bytes of the userdata section of board.toml. The user data partition holds 0x72FE4C9000 bytes, which is 120579273 blocks of 4096 bytes.

### 完成条件

- Host: the register, clock, link and SMMU facts match the board inventory.
- Reads: the SCSI capacity, the GPT and the known blocks are correct, and the OS and SystemOS windows stay inside the userdata range.
- Root: the configured volume mounts and launchd starts, and the writes survive a reboot inside the allocated data region.

### 当前范围

- No storage driver is selected and no partition geometry is pinned.
- The GPT geometry could not be read on the unit: the shell user is not in the disk group, so the raw device, /proc/partitions, the size and start attributes of the block devices in /sys and /proc/diskstats are all denied.
- The root file system and the userland are out of scope for this first stage.

### 下一步

- Take the partition table from the official package and fill board.toml \[userdata\] with the userdata range, checking the offsets against the partition inventory of this record.
- Select the UFS component and write the host probe that registers the controller before anything else.

### 证据

- `source`: [The UFS host of the SoC at 0x1d84000, the node the board device tree would enable.](https://github.com/IssacL04/UniXNU-sm8750-common/blob/main/dts/sm8750.dtsi)
- `source`: [The host, read and root checkpoints the storage area reports against.](https://unixnu.com/porting/ufs)
- `device`: [The unit of this port stores its user data on /dev/block/sda15, the metadata on sda10 and the dynamic partitions in super on sda14. The shell user may not read the block devices, so the GPT geometry that board.toml \[userdata\] needs has to come from the partition table of the official package.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-03-device-probe.md)
  Command: <code>adb shell ls -l /dev/block/by-name/</code>. Revision: `585c5adca2c34624f42342550a18e995354049fd`.
- `device`: [The full partition map of the unit over the six block devices, the six logical units of the UFS host and the 0x1000 logical and erase block size.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-03-hardware-inventory.md)
  Command: <code>adb shell ls -l /dev/block/by-name/ and adb shell ls /sys/class/scsi_device/</code>. Revision: `585c5adca2c34624f42342550a18e995354049fd`.
- `device`: [The complete partition inventory: the size of 119 of the 129 partitions from the bootloader, the unit and the position of every partition from the running system, the 460 GiB user data partition as the last partition of the data unit, and the UEFI boot state of the unit. The first and last LBA still come from the partition table of the official package.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-03-partition-map.md)
  Command: <code>fastboot getvar all and adb shell ls -l /dev/block/by-name/ and adb shell stat -f /data</code>. Revision: `585c5adca2c34624f42342550a18e995354049fd`.

## 显示 {#display}

`planned`

### 硬件与依赖

- The panel of the board: 3392x2400 on the XN242\_P\_D\_A0024 DSI panel, with the vendor timing of the 120 Hz mode and the dynamic frame rate table.
- The framebuffer the firmware publishes through the graphics output protocol.
- The backlight and the brightness control of the unit.

### 配置

- No display component is selected in board.toml yet: the first stage uses the framebuffer the firmware hands over.
- The board does not set a display compatible of its own; the OS profile supplies the platform identity.
- The splash region of the device tree carries the address and the size the bootloader paints into.

### 操作步骤

- Confirm the GOP framebuffer geometry and colour format in the firmware log of the first boot.
- Program the panel mode of the vendor timing in the firmware and compare the measured refresh with the requested one.
- Select the display component, add its archive recipe and its board hooks, and enable the matching defconfig entries.
- Qualify the brightness control and the panel power sequence after the framebuffer is stable.

### 开发经验

- The first stage reaches the video console of the platform expert, which is drawn straight into the framebuffer the loader fills from the UEFI graphics output protocol. No display accelerator is involved yet.
- The panel geometry of this board model is 3392x2400; the firmware framebuffer has to be checked against it.
- The unit of this port reports the same geometry: the display service publishes 3392x2400 in portrait with a default refresh of 120 Hz, and the connector is the DSI-1 of the sde controller, which exposes eight CRTCs. The panel offers 30, 48, 50, 60, 90, 120 and 144 Hz modes, and the backlight is exposed as panel0-backlight.
- The vendor device tree names the panel of this board: the display controller is qcom,mdss\_mdp@ae00000 and the panel is the qcom,mdss\_dsi\_panel\_XN242\_P\_D\_A0024\_vid node, with a second variant of the same family for the 2120 x 3000 panel at 144 Hz with dual DSC.
- The panel timing is not readable on the unit: the DRM mode file of the DSI connector is denied to the shell user. The vendor device tree carries it, and the port has extracted it: the default mode is 120 Hz with a payload of 1696 by 2400 pixels, a horizontal line of 1842 pixels and a vertical line of 2658 pixels, a panel clock of 1362553947 Hz, four DSI lanes at 24 bits per pixel, and DSC 1.2 with eight bits per pixel, two slices of 848 pixels per packet.
- The payload width of the device tree is half of the width of the panel: four DSC slices of 848 pixels are the 3392 pixels the unit measures, and the panel carries two DSI PHYs, so each of them carries half of the picture. The device tree describes the payload of one link, not the panel.
- All sixteen board overlays of the vendor package carry the same timing, so the mode does not depend on the variant of the overlay the bootloader picks.
- The panel runs the dynamic frame rate table of the vendor, with 30, 48, 50, 60, 90, 120 and 144 Hz, and changes the rate by changing the porch rather than by a panel command. The unit reports the same mode list.

### 完成条件

- A known frame appears with the correct geometry and colours, then the userland presentation and the backlight controls work.
- The framebuffer geometry of the firmware matches the panel of the board.
- The brightness control matches the measured backlight values.

### 当前范围

- Only the video console is qualified; no display accelerator and no backlight control is in this port yet.
- The timing of the panel is recorded from the vendor device tree, but the firmware does not program it yet, so no mode has been measured on the unit.
- The port does not derive a link rate from the vendor clock value; the mode the firmware programs is checked against the framebuffer it publishes instead.

### 下一步

- Capture the GOP framebuffer information from the first firmware boot and compare it with the panel geometry.
- Program the 120 Hz mode of the vendor timing in the firmware, then compare the measured refresh with the requested one.
- Select the display component and record its board inputs.

### 证据

- `source`: [A community port of the same board, kept as a lead and not as evidence: it reports the same panel geometry, 3392x2400 on the XN242\_P\_D\_A0024 DSI panel. This record confirms the geometry on the unit and the panel node in the vendor device tree.](https://github.com/wally001012-cyber/UniXNU-erhai/blob/main/board.toml)
- `source`: [The framebuffer component the display area selects once its inputs are satisfied.](https://unixnu.com/drivers/gop-framebuffer)
- `source`: [The display checks of the port: the firmware scanout comes first, the XNU display backend follows, and the requested refresh and the measured frame timing are recorded separately.](https://unixnu.com/porting/display)
- `device`: [The unit of this port reports a physical display of 2400x3392 at density 420, and its bootloader reports the SM8 UFS storage variant. The framebuffer geometry the firmware publishes still has to be compared with the panel.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-03-device-probe.md)
  Command: <code>adb shell wm size and adb shell wm density</code>. Revision: `585c5adca2c34624f42342550a18e995354049fd`.
- `device`: [The display service of the unit publishes 3392x2400 at 120 Hz with the DSI-1 connector of the sde controller, the 30 to 144 Hz mode list and the panel0-backlight device.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-03-hardware-inventory.md)
  Command: <code>adb shell dumpsys SurfaceFlinger and adb shell ls /sys/class/drm/ /sys/class/backlight/</code>. Revision: `585c5adca2c34624f42342550a18e995354049fd`.
- `device`: [The vendor device tree names the display controller qcom,mdss\_mdp@ae00000 and the panel qcom,mdss\_dsi\_panel\_XN242\_P\_D\_A0024\_vid of this board.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-03-vendor-device-tree.md)
  Command: <code>dtc -I dtb -O dts on the device trees carved out of dtbo.img</code>. Revision: `585c5adca2c34624f42342550a18e995354049fd`.
- `device`: [The vendor timing of the panel: the 120 Hz default mode with a 1696 by 2400 payload, the horizontal and vertical porch values, the DSC 1.2 topology of four 848 pixel slices across two DSI PHYs, the dynamic frame rate table from 30 to 144 Hz, the brightness range and the reset and error detection wiring. All sixteen board overlays carry the same timing.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-03-panel-timing.md)
  Command: <code>python3 scripts/extract-panel.py --dts board.dts and python3 scripts/extract-panel.py --compare dtb/</code>. Revision: `585c5adca2c34624f42342550a18e995354049fd`.

## 输入 {#input}

`host-verified`

### 硬件与依赖

- The touch controller of the board: a Novatek NT36536 on the serial peripheral interface.
- The buttons of the unit and their key codes.
- The HID stack the OS profile expects.

### 配置

- No input component is selected in board.toml yet.
- No touch or button node is exported in the device tree.
- The ADT button node of the OS profile stays as the profile defines it.
- The touch protocol library of the board is drivers/ErhaiNovatekTouch: it is the NT36536 adaptation of the ShengNovatekTouch protocol library of the official project, with the header parser of the NT36536 image, the memory map of the controller and the integrity check of the vendor. It runs against a model chip on the host; the SPI transport of the board is not bound yet.

### 操作步骤

- Read the touch controller and the button wiring of the unit.
- Select the input components, add their archive recipes and their board hooks, and enable the matching defconfig entries.
- Qualify the touch mapping, the simultaneous contacts and the release events, then the buttons.

### 开发经验

- The touch controller of this board model is a Novatek NT36536, the same family as the controller of the reference board. Its wiring is given by the vendor device tree and confirmed on the unit below.
- The input stack of the OS profile expects the HID kexts, which are not in the prelink root set of this stage, so the input path cannot be qualified before the root set grows.
- The unit of this port confirms the controller: the SPI bus of the running system carries the driver novatek,nf\_nt36536. The same bus also carries the alternative touch families the platform supports, synaptics-s3910 and fts\_ts, the fingerprint sensor tms,ese and the infrared blaster oplus\_kookong\_ir\_spi.
- The vendor device tree gives the board wiring of the controller: the node nt36536@0 with the interrupt 0xa2 in the SPI interrupt space, a chip select of 0x33, a maximum SPI frequency of 12 MHz and a maximum of ten contacts. The coordinate mapping runs from the 24000 x 33920 panel grid to the 2400 x 3392 display, and the firmware of the controller is named 0x2XN242CN00. The controller also drives a pen with a maximum pressure of 0x4000.
- The touch firmware of the board is in the odm partition of the official package, under firmware/tp/24924/ of the erofs image, in the container with the magic FwUp: a header that names the source path, the raw NT36536 image of 0x3F000 bytes and a trailer of 128 bytes. The raw image is byte for byte the factory image of the same directory and both files are pinned by hash in proprietary-files.txt; scripts/gen-touch-firmware.py owns the extraction, as the contract of this area states.
- The image keeps the vendor bytes untouched and its header is a record map: the ILM and DLM regions, bookmark pairs that carry no size, two header copy descriptors of 0xFF bytes each that the download writes to SRAM 0x1159f8 and 0x115af8, and a trailing metadata block between the second copy and the ILM data. The download set is ILM, DLM and the two header copies.
- The parser of the official driver rejects this image: the NT36532 cascade rule of nvt\_fw\_parse reads the record at end-0x10 as an info record, and on this image that offset is the terminator of the trailing metadata block. The protocol harness of the official driver passes the pinned reference image end to end in the model chip and rejects this one at nvt\_fw\_parse, and the vendor-derived parser of the public NT36xxx driver rejects the trailer block as well. The driver port follows the record map of evidence/2026-11-03-touch-firmware.md.
- The register facts of the NT36536 come from the kernel module of the vendor, oplus\_bsp\_tp\_nt36536\_noflash.ko of the vendor\_dlkm partition of the official package: its memory map is the map of the NT36532 single chip, so the framing, the identification sequence and the download handshake of the official driver apply to this board unchanged. The module is not stripped.
- The integrity check of the firmware file is not a CRC: the vendor check sums the bytes of the file before the last four and the last four bytes hold 5 - \(sum + size\). The image of this board satisfies it. The values 0xa6b863ae and 0xdf14ad7e of the header are not checksums of the file: they are the checksums the boot ROM of the chip computes with its own hardware CRC over the regions it received, and the driver programs them into the golden registers of the chip instead of computing them.

### 完成条件

- Touches map to the display, simultaneous contacts keep stable identifiers, release events arrive, and the buttons produce the expected HID reports.
- The touch and the button board inputs are recorded with their sources.
- The touch protocol library of the board parses the firmware of the board, verifies it and downloads it in the model chip of the host test, with the retry and the timeout paths covered.

### 当前范围

- No input component is selected.
- The protocol library of the board runs against the model chip on the host and passes the full chain \(firmware parse, vendor byte-sum check, four-partition download, on-chip check, boot-ready\) with the retry, timeout and rejection paths covered; it has not run against the controller of the unit because the SPI transport is not bound and the touch component is not selected.
- The axis mapping of the panel of this board has not been qualified against the unit.
- The touch firmware is pinned in proprietary-files.txt and extracted by scripts/gen-touch-firmware.py, but no touch driver component is selected yet: ShengNovatekTouch is a driver for the NT36532E controller and its parser rejects the NT36536 header form of this board. The download flow of the board image is established on the host but has not run against hardware.
- The HID stack is not available in the current prelink root set.

### 下一步

- Bind the SPI transport of the board to the protocol library of the board and select the touch component in board.toml.
- Qualify the axis mapping of the panel of this board against the unit.
- Decide whether the prelink root set grows before the input work starts.

### 证据

- `source`: [A community port of the same board, kept as a lead and not as evidence: it reports the same touch controller, novatek,nf\_nt36536. This record confirms the controller on the unit and the node nt36536@0 in the vendor device tree.](https://github.com/wally001012-cyber/UniXNU-erhai/blob/main/board.toml)
- `source`: [The board inputs and the observations the input area reports against.](https://unixnu.com/porting/input)
- `device`: [The SPI bus of the unit of this port has the driver novatek,nf\_nt36536 bound, which confirms the touch controller of this board on the port's own unit.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-03-hardware-inventory.md)
  Command: <code>adb shell ls /sys/bus/spi/drivers/</code>. Revision: `585c5adca2c34624f42342550a18e995354049fd`.
- `device`: [The vendor device tree gives the touch controller node nt36536@0 with the interrupt 0xa2, the chip select 0x33, the 12 MHz SPI rate, the coordinate mapping from the 24000 x 33920 panel grid to the 2400 x 3392 display and the firmware name 0x2XN242CN00.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-03-vendor-device-tree.md)
  Command: <code>dtc -I dtb -O dts on the device trees carved out of dtbo.img</code>. Revision: `585c5adca2c34624f42342550a18e995354049fd`.
- `host`: [The firmware of the touch controller: the record map of the NT36536 image, the download set ILM, DLM and the two header copies, and the divergence from the parser of the official driver. The protocol harness of the official driver passes the pinned reference image end to end in the model chip and rejects the board image at nvt\_fw\_parse, so the driver port follows the record map of the evidence file.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-03-touch-firmware.md)
  Command: <code>python3 scripts/gen-touch-firmware.py and the Test/nvt-protocol.c harness of ShengNovatekTouch against the reference image and the board image</code>. Revision: `b9989e121cf85ecb9bb8557b5edc0f1c4630da7f`.
- `host`: [The touch driver of the board: the register map, the identification sequence and the download handshake of the NT36536 read out of the kernel module of the vendor, the header parser of the NT36536 image and the integrity check of the vendor, which is a byte sum and not a CRC. The protocol library of the board parses the real image, verifies it and downloads the four partitions into the model chip of the host test, with the retry and the timeout paths covered.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-03-touch-driver.md)
  Command: <code>gcc -O1 -Wall -Wextra -o nt36536-protocol Test/nt36536-protocol.c NvtProtocol.c &amp;&amp; ./nt36536-protocol firmware/novatek/novatek_nt36536_erhai_fw_huaxing.bin</code>. Revision: `0383eb08ab2136a680491d8dc47fe3abf28b0967`.

## GPU {#gpu}

`planned`

### 硬件与依赖

- The GPU of the board and the firmware it needs.
- The SMMU and the power path of the GPU, and the GMU command database of the SoC.
- The Apple graphics ABI the OS profile declares.

### 配置

- No GPU component is selected in board.toml yet, and CONFIG\_XNU\_NATIVE\_ADRENO is not set in the defconfig.
- The GPU and the GMU nodes of the device tree stay disabled.
- The GPU node of the SM8750 SoC device tree carries the chip identifier and the model of the board.

### 操作步骤

- Read the GPU hardware revision and the firmware files the board needs.
- Select the GPU components and the SoC platform kit, and add their archive recipes and their board hooks.
- Qualify the submissions, the mappings and the fences before the Metal client is attempted.

### 开发经验

- This stage stops at the XNU entry, so the GPU is not part of it: the accelerator, the firmware and the SMMU takeover all need a qualified storage and display path first.
- The shared SM8750 platform kit is not in the official component catalog, so the GPU work needs either a catalog entry or a board-local implementation before it can be selected.
- The accelerator of the unit of this port is the Adreno 830: the graphics stack of the running system reports Qualcomm, Adreno \(TM\) 830, OpenGL ES 3.2, and the KGSL device node of the board is present. The GPU firmware regions are reserved in the live device tree at 0x9b09a000, and the vendor driver runs on the display engine of the SoC.

### 完成条件

- The GPU submissions complete, the mapping and the fence handling are correct, a known image renders, and the selected Metal client presents it.
- The GPU firmware inputs are pinned by hash.
- The SMMU takeover of the GPU is qualified with its cache policy.

### 当前范围

- No GPU component is selected and the accelerator is not qualified.
- The GPU firmware of the board is not pinned; it comes from the official package.
- The Metal client path is out of scope for this stage.

### 下一步

- Take the GPU firmware files of the board from the official package and pin them by hash.
- Decide between a board-local platform kit and a catalog entry for the shared SM8750 platform kit.

### 证据

- `source`: [The accelerator component and its inputs, which the GPU area would select once the board requirements are met.](https://unixnu.com/drivers/adreno740)
- `source`: [The shared SM8750 platform kit with the GPU power, the SMMU and the GMU command database; it is not in the official component catalog yet.](https://github.com/IssacL04/UniXNU-sm8750-common/blob/main/kits/Sm8750Platform/README.md)
- `device`: [The accelerator of the unit is an Adreno 830, with the KGSL device node present and the GPU microcode region reserved at 0x9b09a000 in the live device tree.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-03-hardware-inventory.md)
  Command: <code>adb shell dumpsys SurfaceFlinger and adb shell ls /dev/kgsl-3d0</code>. Revision: `585c5adca2c34624f42342550a18e995354049fd`.

## 网络 {#network}

`planned`

### 硬件与依赖

- The wireless controller of the board and its firmware.
- The PCIe resources the radio owns.
- The MAC address the radio publishes to the userland.

### 配置

- No network component is selected in board.toml yet.
- No radio node is exported in the device tree.
- The wireless node stays out of the ADT export until the radio resources are known.

### 操作步骤

- Read the wireless hardware and its firmware files.
- Select the wireless component, add its archive recipe and its board hooks, and enable the matching defconfig entries.
- Qualify the scan, the association, the address configuration and the sustained traffic.

### 开发经验

- The radio of this board model is a Qualcomm WCN7850 on PCIe, but the port has not read its resources yet.
- The radio has to publish its local MAC address to the userland before the network stack can bring the interface up.
- The unit of this port confirms the radio: the Wi-Fi firmware of the running system reports the hardware revision PEACH\_V2 with the firmware version 1.0.0.0.32767.127 and the build WLAN.GNG.1.0-03342-QCAGNGSWPL\_V1.0\_V2.0\_SILICONZ-1.81206.153, the driver version is 5.2.1.119O and the module is qca\_cld3\_wlan.ko. The cnss2 driver owns the radio over the PCIe function 0000:01:00.0 and exposes the MHI device mhi\_110e\_00.01.00, and the wireless firmware region is reserved in the live device tree as cnss\_wlan\_region.
- The vendor device tree agrees: the radio is the node qcom,cnss-peach@b0000000, the cnss block is at 0xa3380000 with the size 0x10000 and the PCIe host of the radio is the controller pcie@1c00000.

### 完成条件

- Scanning, association, address configuration and sustained receive and transmit traffic pass with the selected firmware.
- The radio resources and the firmware files are pinned by hash.

### 当前范围

- No network component is selected and no radio firmware is pinned.
- The Wi-Fi firmware of the board comes from the official package; the vendor module of the running system is not part of the port.
- The network path is out of scope for this stage.

### 下一步

- Take the radio firmware files from the official package and pin them by hash, then read the radio resources of the unit from the device tree dump of that package.
- Select the wireless component once its inputs are satisfied.

### 证据

- `source`: [How the reference board exports the radio to the userland before launchd evaluates the wireless condition.](https://github.com/UniXNU/UniXNU-sheng/blob/main/dts/sheng.dts)
- `source`: [The board inputs and the observations the network area reports against.](https://unixnu.com/porting/network)
- `device`: [The wireless controller of the unit is the Qualcomm PEACH\_V2 with firmware 1.0.0.0.32767.127 and driver 5.2.1.119O, driven by cnss2 over the PCIe function 0000:01:00.0 with the MHI device mhi\_110e\_00.01.00.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-03-hardware-inventory.md)
  Command: <code>adb shell dumpsys wifi and adb shell ls -l /sys/class/net/wlan0/device/driver/</code>. Revision: `585c5adca2c34624f42342550a18e995354049fd`.
- `device`: [The vendor device tree names the radio qcom,cnss-peach@b0000000, places the cnss block at 0xa3380000 and the PCIe host of the radio at the controller pcie@1c00000.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-03-vendor-device-tree.md)
  Command: <code>dtc -I dtb -O dts on the device trees carved out of dtbo.img and vendor_boot.img</code>. Revision: `585c5adca2c34624f42342550a18e995354049fd`.

## cellular {#cellular}

`not-applicable`

### 硬件与依赖

- The cellular hardware of the board, if it is fitted.

### 配置

- No cellular component is selected in board.toml, and no modem node is exported in the device tree.

### 操作步骤

- Check the feature list, the SIM state and the radio devices of the unit.
- If a modem is fitted, read its firmware, its EFS and its reset path and give the area its own configuration.

### 开发经验

- This board has no cellular radio. The feature list of the running system carries android.hardware.telephony.ims and android.hardware.telephony.mbms but no android.hardware.telephony feature, there is no /dev/radio node, the SIM state is ABSENT and the baseband reports a Virtual RILD Modem.
- The modem\_a and the modem\_b partitions exist in the partition layout of the unit, but nothing in the running system brings up a modem, and the telephony registry reports OUT\_OF\_SERVICE with no operator and no radio technology.

### 完成条件

- The record states that the board has no modem, so no cellular component, firmware or interface is required for this port.

### 当前范围

- The board is Wi-Fi only. The cellular area does not apply to this port, and the modem partitions of the layout are unused.

### 下一步

- Revisit the area if a variant of this board carries a modem.

### 证据

- `source`: [The required areas and the rule that an area outside the scope of the board is recorded as not-applicable with the reason in its limits.](https://unixnu.com/porting/records)
- `device`: [The unit of this port has no cellular radio: no telephony feature, no radio device, no SIM and a virtual RILD modem.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-03-hardware-inventory.md)
  Command: <code>adb shell pm list features and adb shell getprop gsm.sim.state</code>. Revision: `585c5adca2c34624f42342550a18e995354049fd`.

## 音频 {#audio}

`planned`

### 硬件与依赖

- The audio hardware of the board and its firmware.
- The DSP, the shared memory and the remote processor channels of the SoC.
- The audio routes the OS profile declares.

### 配置

- No audio component is selected in board.toml yet.
- No audio node is exported in the device tree.
- The audio related platform tables stay out of the board configuration.

### 操作步骤

- Read the audio hardware, the DSP firmware and the shared memory layout of the unit.
- Select the audio components, add their archive recipes and their board hooks, and enable the matching defconfig entries.
- Qualify each declared route separately, with playback and capture.

### 开发经验

- The audio path of this board needs the DSP, the shared memory and the remote processor channels of the SoC, and none of them is in this port yet.
- The prelink root set of this stage carries no audio client, so the audio path cannot be reached before the root set grows.
- The audio hardware of the unit of this port is the aw882xx\_smartpa and the aw87xxx\_pa amplifiers with the aw\_haptic driver, and the proximity sensors are the ams-OSRAM tmf8806 and the ams-tof. The DSP firmware regions are reserved in the live device tree at 0x9ed80000 for the ADSP, at 0x9eb00000 for the CDSP and at 0x9ec00000 for the SoCCP.

### 完成条件

- Each declared route carries the selected audio format through playback or capture and handles start and stop correctly.
- The audio firmware inputs are pinned by hash.

### 当前范围

- No audio component is selected and no route is qualified.
- The audio path is out of scope for this stage.

### 下一步

- Read the audio hardware and the DSP firmware of the unit.
- Plan the growth of the prelink root set that the audio and the input paths need.

### 证据

- `source`: [The DSP, the audio and the power guide that the audio area follows, including the shared memory and the remote processor channels.](https://unixnu.com/porting/power)
- `source`: [The component catalog, which holds the QcomGlink, QcomMdt, QcomSmem and QcomSmp2p components the audio path selects.](https://unixnu.com/reference/components)
- `device`: [The audio hardware of the unit: the aw882xx\_smartpa and aw87xxx\_pa amplifiers, the haptic driver and the time of flight sensors, with the DSP firmware regions reserved in the live device tree.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-03-hardware-inventory.md)
  Command: <code>adb shell ls /sys/bus/i2c/drivers/</code>. Revision: `585c5adca2c34624f42342550a18e995354049fd`.

## 电源 {#power}

`planned`

### 硬件与依赖

- The power management hardware of the SoC: the RPMh, the QMP and the secure controller.
- The battery and the fuel gauge of the board.
- The sleep and resume paths the unit has to survive.

### 配置

- No power component is selected in board.toml yet.
- No power node is exported in the device tree.
- The kernel command line does not carry any power related argument yet.

### 操作步骤

- Read the power management hardware and the shared memory tables of the unit.
- Select the power components, add their archive recipes and their board hooks, and enable the matching defconfig entries.
- Qualify the declared power controls, the battery readings and each sleep and resume transition.

### 开发经验

- The board has no Apple policy manager, so the kernel runs against a virtual platform instead of waiting for a policy manager nub.
- The sleep transitions of this board are not qualified, and the declared controls of the record have no evidence yet.
- The battery hardware of the unit of this port is the bq27541 and the bq27z561 gauges, and the board has a cps-wls-charger for the wireless charging. The unit reports 4822 mV on the charger and 4363 mV at the battery at a full charge, and the SoC exposes 42 thermal zones with 42 cooling devices.

### 完成条件

- The declared power controls and the battery readings match the observations, and each claimed sleep and resume transition restores its dependent peripherals.
- The power management hardware of the board is documented with its sources.

### 当前范围

- No power component is selected and no transition is qualified.
- The power path is out of scope for this stage.

### 下一步

- Read the power management hardware of the unit and record the shared memory tables it needs.
- Plan the sleep and resume qualification once the board services exist.

### 证据

- `source`: [The component catalog that holds the QcomQmp and QcomRpmh components the power path selects.](https://unixnu.com/reference/components)
- `source`: [The board inputs, the build integration and the expected observations of the power area.](https://unixnu.com/porting/power)
- `device`: [The battery gauges and the wireless charger of the unit, the charger and the battery voltages and the thermal zones of the SoC.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-03-hardware-inventory.md)
  Command: <code>adb shell dumpsys battery and adb shell ls /sys/class/thermal/</code>. Revision: `585c5adca2c34624f42342550a18e995354049fd`.

## 镜像组装 {#packaging}

`host-verified`

### 硬件与依赖

- The build inputs of the board: the UniXNU checkout, the firmware checkout, the SoC source and the platform seed.
- The OS profile and the defconfig of each supported profile.
- The boot image parameters of the stock bootloader.

### 配置

- board.toml \[package\] names the UniXNU checkout relative to this repository, and \[package.defconfig\] maps the OS profile to the defconfig of the board.
- The device packaging script is the official script, unchanged: a board changes board.toml, never the script.
- The payload volume, its size, the kernel command line and the ADT inputs come from board.toml.

### 操作步骤

- Run scripts/package.sh --check --os 17 from this repository: it resolves the dependencies, runs the preflight scripts and applies the patches without building.
- Run scripts/package.sh --os 17 --uefi ../uefi-erhai to build the kernel, the package, the firmware, the payload and the boot image.
- Check every output of the run before the board is booted.

### 开发经验

- The build of this board has run on the macOS runner of the workflow: run 41692537288 at this head completed to success and uploaded the four outputs as the artifact images-17, and the same head completed an earlier run of the same script to success from a second clean checkout 83 minutes before it. The script and the workflow ran unchanged between the two runs.
- The manifest of the run records every input the build resolved: configuration erhai\_defconfig, the OS profile ipados-17.7.11-21H461, a kernel command line of 123 bytes, the 61 patches of the series in application order, and the revisions of the device package, the UniXNU checkout, the SM8750 source, the selected components and the references. The three image hashes of the manifest match the downloaded artifacts hash for hash.
- The script is the same in every device repository, so the board configuration is the only thing that changes between boards.
- The platform seed never belongs in a repository: the workflow reads it from the UNIXNU\_UNIQUE\_CHIP\_ID secret and the artifacts of a run belong to one device alone.
- The boot image carries a device tree of its own, and the packaging guide requires the firmware preflight to compile it. The preflight of this board runs scripts/build-dts.py, which compiles dts/erhai.dts against the device tree include directories of board.toml \[device\_tree\], resolved through the same path contract the official build uses, into the path board.toml \[bootimg\] dtb names.
- The build of this board runs on the macOS runner of the workflow of this repository. The workflow checks out the firmware repository of the board with its submodules, installs the toolchain, checks the platform seed of the unit and runs the official packaging script against the firmware checkout; the vendor inputs of the firmware build are fetched by the preflight from the release asset of this repository.
- The official builder of the boot image does not produce an image the bootloader of the board runs. It writes the header version 0, and the bootloader of the board loads a version 0 image without starting the firmware. The same payload with the header version 4 and an empty signature region does start it, and the same payload with the 4096 byte signature region that mkbootimg.py writes by default is refused by the bootloader with a Load Error. The builder of the base tree exposes neither the header version nor the signature region, so the image the unit runs needs a header rewrite outside the official script until the base tree supports it.
- The header of version 3 and version 4 of mkbootimg.py is not the classic layout. The kernel size sits at +8, the header size at +20, the version at +40 and the size of the signature region at +1580, and the page size of 4096 is implied by the padding of the header. The classic layout of a version 0 header puts the page size at +36 and the version at +40, so a version 4 image read with the classic layout reports an empty page size. The payload of a version 4 image starts after the header page and the signature page.
- The boot image builder of the base tree writes the header version 0 only and does not expose the signature region or the option to embed the payload in the image. The community port of the same board carries a patch of its own that adds the header versions 3 and 4 and the embedded payload. That patch is written against an older revision of the base tree and does not apply to the revision this record was written against, so the gap is a change the base tree has to take rather than a change this repository can carry.

### 完成条件

- The kernel and the prelink succeed, the payload contains all declared inputs, and the boot image matches the bootloader format and the size limit.
- The same script produces the same two artifacts from a clean checkout without an edit.
- The generated unixnu.lock is committed.

### 当前范围

- The build has run on the macOS runner with the toolchain the workflow installs and the platform seed of the unit as the repository secret UNIXNU\_UNIQUE\_CHIP\_ID, and it produced the four artifacts of run 41692537288. Those artifacts carry the seed of this unit, so the workflow keeps them for one day and the run is meant to be deleted after the download.
- The check step of the script runs to completion on a Linux host and the generated unixnu.lock is committed. The reproducibility criterion of this area is evidenced by two successful builds of the same revision from two clean checkouts, not by an equality of hashes: the artifact of the earlier success had expired behind the one-day retention when the comparison was made.
- The workflow pins the firmware checkout of the board to the revision the firmware volume of the run was built from, so the inputs of the firmware build are pinned by a commit. The manifest of the run still records no firmware revision, because the manifest is written by the official packaging script, which a board does not change.
- The artifact of the workflow carries the header version 0 and the bootloader of the board does not start it, so the published artifact is not the image the unit runs. The image the unit runs is the same payload with the header rewritten to the version 4 and the empty signature region the bootloader of the board accepts, a rewrite the official script does not make and the base tree of the builder does not support yet.

### 下一步

- Compare the artifact hashes of two successful runs while both artifacts are still inside the one-day retention, to close the reproducibility criterion of this area with an equality of hashes.
- Have the base tree of the boot image builder write the header version 4 with an empty signature region, so the artifact of the workflow is the image the unit runs.
- Record the firmware revision in the manifest of the run, so every input of the build is pinned by a commit in the manifest itself and not only in the workflow.

### 证据

- `source`: [The packaging script contract, the check mode and the artifact list the packaging area reports against.](https://unixnu.com/porting/packaging)
- `source`: [The official device packaging script, used unchanged in this repository.](https://github.com/UniXNU/UniXNU/blob/main/examples/device/scripts/package.sh)
- `host`: [The check step of the official packaging script resolves the dependencies from unixnu.lock, writes the configuration and lists the 61 patches of the series in application order, and exits without an error.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-03-fetch-lock.md)
  Command: <code>scripts/package.sh --check --os 17</code>. Revision: `3fa5ff5f409398c0555a9561d6437ce5d4c3b3b7`.
- `host`: [The full build of the packaging script on the macOS runner of the workflow: run 41692537288 at this head completed to success and published the four artifacts of the manifest, the same head completed an earlier run of the same script to success from a second clean checkout, the manifest records the 61 patches and every input revision with the three image hashes matching the downloaded artifacts, and the boot image round-trips against its inputs down to the ramdisk slot.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-04-ci-package.md)
  Command: <code>gh run view 41692537288 --repo xingxing19035/UniXNU-erhai --json status,conclusion,headSha &amp;&amp; python3 verify-ci-boot.py</code>. Revision: `8b44290640f5e348891b59658d497b23972b0e7d`.
- `device`: [The boot image of the workflow against the bootloader of the unit: the header version 0 of the artifact is loaded without starting the firmware, the same payload rebuilt with the header version 4 and an empty signature region starts the firmware and reaches the DXE core of the platform, and the same payload with the 4096 byte signature region that mkbootimg.py writes by default is refused by the bootloader with a Load Error. The stock boot image of the unit starts Android under the same path.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-04-first-device-run.md)
  Command: <code>adb reboot bootloader &amp;&amp; fastboot boot boot-v4-sig0.img</code>. Revision: `246f1c4232a87df0d18b0406748937036d403713`.

## 诊断 {#diagnostics}

`device-verified`

### 硬件与依赖

- The serial console of the firmware and of the kernel.
- The boot checkpoints that tell how far the board came.
- The device observations that a bring-up run produces.

### 配置

- The kernel command line selects the serial console, the debug mask and the kprintf spam that makes an early hang visible.
- The panic screen patch is enabled, so a kernel panic paints the screen instead of vanishing.
- The preflight script checks the board configuration before the firmware build starts.

### 操作步骤

- Export the firmware log during the first bring-up, before the kernel handoff.
- Read the kernel log over the serial console and compare the last confirmed checkpoint with the bring-up order.
- Store every run as evidence: the command, the revision, the output and the result.

### 开发经验

- The board publishes one CPU, so the early boot is the only stage that is easy to read: the serial console and the panic screen carry it.
- Without the screen checkpoints a silent hang and a kernel that never started look the same, so the checkpoints have to come before the next stage.
- The preflight scripts of the build belong to this area as well, because they are the scripts the build runs before it starts. The board check of the firmware area is one of them: it reads the name of the device repository from its remote when the checkout directory does not carry it, so that the layout of the workflow of this repository passes, and it refuses a repository that belongs to another board.
- The first bring-up of this port ran on the unit of this port. The image with the header version 4 and an empty signature region starts the firmware, the panel carries the banner of the platform and then the assert of the DXE core, and the unit leaves the bus right after the image is accepted. The assert is the last state of the firmware, so the DXE core stops before the first driver is dispatched.
- The line number of the assert does not identify the library on its own. The generated file of the DXE core of the firmware build of the run has 567 lines, holds none of the asserts of the library type that produces this message, and no generated file of the whole firmware build holds an assert at that line. The build of the run was read back in full to establish this, with a temporary step in the workflow that printed the generated files; the step was reverted afterwards and the workflow is the official form again.
- The diagnostic build maps the debug library of the DXE phases to the serial debug library of the platform instead of the Advanced Logger, so the whole DXE phase writes to the panel and the last message before the assert names the library that returns EFI\_NOT\_FOUND.
- The screen checkpoint layer of the community port of the same board is not adopted. Its build script drives the platform build of the base tree and depends on a tool that only exists on macOS, and its kernel patches are written against an older revision of the kernel than the one this port builds. The kernel side of the hook is already in the base tree through the patch series of the operating system profile, so what is missing here is the driver implementation, which is open work in this repository.
- The assert of the DXE phase of the first run is raised by the vendor driver of the environment, EnvDxe, and not by a module of this port: the 54 modules the phase compiles carry 17 assertions on the return value of a call and the highest line number among them is 487, so the line 649 of AutoGen.c of the assert cannot be one of them.
- The constructor of that driver fails because the shared memory of the system is not initialized: the library of the vendor reads the pointer to it from the internal memory of the secure world at 0x01FD4000, the generic startup code of this port runs outside the secure world and reads zero, the library reports "SMEM is not initialized by Boot." and the constructor returns EFI\_NOT\_FOUND.
- The startup code of the vendor, QcomPkg/XBLCore/XBLCore.te, parses the device tree the bootloader hands over and builds the memory map of the platform out of it, while the generic startup code of this port does neither; the board is entered through the fastboot bootloader of the system, which leaves no such handoff behind.
- The boot of the board does not need the driver stack of the vendor: the payload arrives in the handoff of the boot image, the panel is left on by the bootloader and the shared memory of the system is only read by the drivers of the vendor. The DXE phase of the firmware of this board therefore runs without that stack, and the stack is kept in the firmware repository as Include/DXE.vendor.inc for the way the vendor enters the board.
- The analysis of the assert of the DXE phase is in the repository, in the scripts of the analysis: they name the module of the vendor that raises the assert, they show the code path of its shared memory library and the compile-time constants that place its target in the internal memory of the secure world, and they name the modules a build carries.
- The second assert of the DXE phase belongs to the library constructor list of the vendor DevicePathDxe, which asks for the kernel protocol of the vendor and the scheduler interface HOB that the minimal phase does not publish, so DevicePathDxe, DiskIoDxe and PartitionDxe are built from upstream source instead of the vendor binaries.

### 完成条件

- Each claimed milestone has a reproducible command, a matching source or image revision and an accessible result.
- The firmware log of every run is saved before the kernel handoff.
- The storage verification, the persistent capture, the manual cycle and the automated tests pass once the storage path exists.

### 当前范围

- The unit has run the firmware volume of this port once, and that run stops in the DXE phase: the assert of the DXE core is the first failure of this port on the unit. The kernel, the payload and the handoff have not run on the unit yet, so no kernel log of this port exists.
- The screen checkpoints are not in this repository yet: the base tree has no archive script for them, and this port implements its own instead of adopting the implementation of a community port of the same board.
- The shared memory of the system stays out of reach in this boot path: the pointer to it lives in the internal memory of the secure world, so the drivers of the vendor that read it cannot run until the board is entered the way the vendor enters it.

### 下一步

- Add the board checkpoint archive to this repository, or adopt the base tree equivalent, so a hang is distinguishable from a kernel that never started.
- Boot the diagnostic build, read the last message of the DXE phase on the panel and name the library that returns EFI\_NOT\_FOUND.
- Store the firmware log of the run that reaches the kernel handoff as evidence, once the DXE phase runs to the menu.
- Boot the firmware volume of revision 18a9d7bb on the unit and record whether the DXE phase reaches the menu of the boot manager without the driver stack of the vendor.

### 证据

- `source`: [The firmware log exporter and the persistent capture procedure the diagnostics area follows.](https://unixnu.com/porting/log-capture)
- `source`: [A community port of the same board carries a screen checkpoint implementation. This port does not adopt it: the checkpoints are implemented in this repository, and that work is open in the limits of this area.](https://github.com/wally001012-cyber/UniXNU-erhai/tree/main/drivers/BootProgress)
- `device`: [The bootloader of the unit of this port answers read-only queries over USB, but the Windows fastboot cannot bind its bootloader interface. The working path on this host is USB over IP into Linux, where the fastboot of the current platform-tools talks to the unit. Any maintainer that boots an image has to know this.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-03-device-probe.md)
  Command: <code>usbipd attach --wsl --busid 1-3 and fastboot getvar all</code>. Revision: `585c5adca2c34624f42342550a18e995354049fd`.
- `host`: [The board configuration of this board passes the preflight check in three layouts: the local checkout, the checkout under the name the workflow gives it, and a repository of another board, which the check refuses.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/scripts/check-board.py)
  Command: <code>python3 scripts/check-board.py</code>. Revision: `b79a8d3e6c32927134538a22230f3bff1e410ba7`.
- `host`: [The device tree preflight of the build resolves its inputs through the official path contract, so a wrong path fails the run instead of compiling nothing: the include directory of the SoC comes from the pinned sm8750 feed checkout, and the run in the build tree of this checkout emits build/erhai/erhai.dtb of 3326 bytes.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/scripts/build-dts.py)
  Command: <code>python3 scripts/build-dts.py</code>. Revision: `93d282319d32e1d93005e6c717f6e71e049f2a92`.
- `host`: [The firmware configuration check resolves vendor-binaries.txt, the manifest of the vendor binary set, through UNIXNU\_DEVICE when the official preflight runs it from the build tree, the way the sibling preflight scripts locate the device repository; a direct run falls back to the repository of the script. Before this fix the run from the tree copy found no manifest next to it and refused the set that was present, checking zero files of it.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/scripts/check-firmware-modules.py)
  Command: <code>python3 scripts/check-firmware-modules.py</code>. Revision: `2bb6c1303e041f86ecbb24fcad99f4a13835fe04`.
- `device`: [The first bring-up of this port on the unit of this port: the boot image of the packaging workflow carries header version 0 and the bootloader of the board loads it without starting the firmware; the same payload rebuilt with header version 4 and an empty signature region starts the firmware, the panel carries the banner of the platform and then the assert of the DXE core, and the unit leaves the bus right after the image is accepted. The stock boot image of the unit starts Android under the same path, so the temporary boot path itself is sound. The screen of the unit is the only output the run produces: the DXE phase of this board writes to the Advanced Logger of the platform, which keeps its output in memory, and not to the panel.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-04-first-device-run.md)
  Command: <code>adb reboot bootloader &amp;&amp; fastboot boot boot-v4-sig0.img</code>. Revision: `246f1c4232a87df0d18b0406748937036d403713`.
- `device`: [The assert of the DXE phase belongs to the vendor driver of the environment and fails on the shared memory of the secure world, which the startup code of this port cannot reach; the phase of this board therefore runs without the driver stack of the vendor.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-04-dxe-assert-root-cause.md)
  Command: <code>llvm-objdump -d --triple=aarch64 Binaries/erhai/QcomPkg/Drivers/EnvDxe/EnvDxeEnhanced.efi</code>. Revision: `221433eea14168e512d748f7fa1e622d474d815f`.
- `host`: [The module of the vendor that raises the assert of the DXE phase: four modules of the vendor carry the immediate of the line number 649 and the description of the macro, and the one that comes first in the phase is the driver of the environment.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/scripts/analysis/find-vendor-assert.py)
  Command: <code>python3 scripts/analysis/find-vendor-assert.py</code>. Revision: `221433eea14168e512d748f7fa1e622d474d815f`.
- `host`: [The code path of the shared memory library of that driver: the strings of the library, the assertion of the library at the line 646 of smem\_target.c, and the constants 0x01f00000, 0x000d4000 and 0x000d4004 that place its target in the internal memory of the secure world.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/scripts/analysis/dis-vendor-driver.py)
  Command: <code>python3 scripts/analysis/dis-vendor-driver.py</code>. Revision: `221433eea14168e512d748f7fa1e622d474d815f`.
- `host`: [The modules a build carries: the volume of the run 41822503782 carries the modules of this port and no module of the driver stack of the vendor, and its compressed kernel field is 631664 bytes against 1293688 bytes for the run before it.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/scripts/analysis/fv-modules.py)
  Command: <code>python3 scripts/analysis/fv-modules.py boot.img</code>. Revision: `18a9d7bb5c0bb42f6dd57406b5882ae23388d4f8`.
- `device`: [The second bring-up of this port stops at an assert in the library constructor list of the vendor DevicePathDxe: the constructor asks for the kernel protocol of the vendor and the scheduler interface HOB, neither of which the minimal DXE phase publishes, and the three affected modules are built from upstream source in the firmware revision this record pins.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/evidence/2026-11-04-devicepath-assert.md)
  Command: <code>adb reboot bootloader &amp;&amp; fastboot boot boot-v4-minimal-sig0.img</code>. Revision: `e2b37af0a12b6c57cd18a015c181fafb41bdb99b`.
- `host`: [The disassembly of the vendor DevicePathDxe carries the immediate 364 in the seventh library constructor of the module, which is the constructor that reports EFI\_NOT\_FOUND to the assert of AutoGen.c.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/scripts/analysis/dis-devicepath-assert.py)
  Command: <code>python3 scripts/analysis/dis-devicepath-assert.py</code>. Revision: `e2b37af0a12b6c57cd18a015c181fafb41bdb99b`.
- `host`: [The GUID constants the failing constructor builds are gEfiKernelProtocolGuid at rva 0x10148 and gEfiSchedulerInterfaceHobGuid at rva 0x106d8; the first is installed by the driver stack of the vendor and the second is produced by the secure world.](https://github.com/xingxing19035/UniXNU-erhai/blob/1d6a90ee37874082a5bd53bfa92321ead20a52ee/scripts/analysis/read-devicepath-guid.py)
  Command: <code>python3 scripts/analysis/read-devicepath-guid.py</code>. Revision: `e2b37af0a12b6c57cd18a015c181fafb41bdb99b`.

</div>
