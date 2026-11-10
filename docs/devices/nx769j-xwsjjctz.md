# nubia RedMagic 9 Pro / 9 Pro+ / 9S Pro / 9S Pro+ \(NX769J\) \(xwsjjctz\)

[xwsjjctz/UniXNU-NX769J](https://github.com/xwsjjctz/UniXNU-NX769J)

<div v-pre>

nubia RedMagic 9 Pro / 9 Pro+ / 9S Pro / 9S Pro+ \(NX769J\) on Qualcomm SM8650, targeting iOS 16.5 \(build 20F66, Darwin 22.5.0, XNU 8796\) with an iPhone X identity. The board shares the SM8550 SoC register map and owns its CPU topology, UFS root policy, Goodix touch input and Adreno 750 GPU work. This record states the implementation coverage of each area and the evidence each milestone requires.

Source record: [porting.toml](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/porting.toml), `841a86ace1caa36c0528fbf6133df36acc41b516`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `host-verified` |
| [Firmware and boot](#firmware) | `host-verified` |
| [CPU and interrupts](#cpu) | `device-verified` |
| [Memory and DMA](#memory) | `device-verified` |
| [Storage and root](#storage) | `device-verified` |
| [Display](#display) | `device-verified` |
| [Input](#input) | `device-verified` |
| [GPU](#gpu) | `implemented` |
| [Network](#network) | `planned` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `planned` |
| [Image assembly](#packaging) | `host-verified` |
| [Diagnostics](#diagnostics) | `device-verified` |

## Configuration {#configuration}

`host-verified`

Components: `ArmDTPlatform`, `SoftwareAES`, `XnuPrelink`.

### Hardware and dependencies

- SM8650 register map and CPU topology from mainline sm8650.dtsi.
- iOS 16.5 build 20F66 OS profile with XNU 8796.101.5.
- UniXNU-sm8550-common revision 23b2049fcd9e30356161def84231334fb55ecca9 as the SoC source.
- Board identity from the NX769J Android 14 vendor firmware and board configuration.

### Configuration

- board.name = nx769j; board.soc = SM8650; board.soc\_source = sm8550; board.os\_profile = ios-16.5-20F66; schema\_version = 2.
- components.include lists the complete selection; arrays replace the inherited ARM64, SoC and OS arrays.
- kernel.defconfig = nx769j\_defconfig; config\_fragments apply arch, soc, os in order and the device defconfig last.
- device\_tree.source = device:dts/nx769j.dts with include\_dirs = \[soc:dts\].
- Board submodules are not used; every driver comes from the component catalog at its pinned revision.

### Procedure

- Read https://unixnu.com/porting/device-repository and https://unixnu.com/porting/records.
- Run ./unixnu defconfig nx769j\_defconfig -D ../UniXNU-NX769J from the UniXNU checkout.
- Run ./unixnu fetch -D ../UniXNU-NX769J and commit the resulting unixnu.lock.
- Run ./unixnu status --json -D ../UniXNU-NX769J and review the resolved profiles, components, source pins and patch order, then ./unixnu tree -D ../UniXNU-NX769J.

### Development findings

- Tables merge in ARM64, SoC, OS, device order and arrays replace inherited arrays, so the device must list every required component and fragment.
- board.toml sets bootimg.image.header\_version to 0 rather than the 4 the NX769J board configuration records. unixnu bootimg verify\(\) reads the header at the v0/v1/v2 offsets and would reject a v4 image, and the tool defaults use 0. The reasoning and the open question about what the NX769J ABL accepts are recorded in the packaging area.
- soc:configs/sm8550.config sets CONFIG\_XNU\_NATIVE\_ADRENO=y. The device defconfig applies last and sets CONFIG\_XNU\_NATIVE\_ADRENO=n because the SM8550 GPU stack targets Adreno 740 while this board has Adreno 750.
- There is no UniXNU-sm8650-common. sm8550-common is usable as the SoC source because the register map of every resource this port drives is identical on both parts: GICD 0x17100000/0x10000, GICR 0x17180000/0x200000, UFS host 0x01d84000/0x3000, UFS PHY 0x01d80000/0x2000, GPU 0x03d00000/0x40000, GMU 0x03d6a000/0x35000 and GPU SMMU 0x03da0000/0x40000. The CPU core names and the Adreno generation do differ and are overridden in the board DTS and defconfig. The device confirms the UFS ranges in /proc/iomem and the MPIDR layout in its CPU nodes.
- board.os\_profile selects a directory under UniXNU/profiles/os/, and this port targets ios-16.5-20F66, which does not exist in UniXNU yet. The profile is kept in this repository at os-profiles/ios-16.5-20F66/ and the Build workflow installs it into the UniXNU checkout before resolving. The \[ipsw\] and \[kernel.prelink\] tables are inherited from that profile rather than repeated here, so the REQUIRED\_IPSW fields are filled in one file.
- board.toml selects only device:patches/xnu/series. The shared arch, soc and os series still target xnu-10063.141.1 while this port runs xnu-8796, so referencing them would either abort unixnu status with 'patch missing' or fail during application. The rebased copies are carried here and the four-series form goes back once the shared series are rebased.
- unixnu status resolves the complete ordered patch series, so it needs the source of every component named by a component: entry. The 17.7.11 OS series names XnuPrelink twice and status aborts with 'patch missing' when that source is absent, while defconfig alone succeeds because it only reads the configuration fragments. The resolve build test therefore runs fetch and tree before status, which is the step 4 order in the porting guide.
- unixnu fetch records component sources in unixnu.lock as well as feed sources when the device repository declares no git submodules. UniXNU-sheng pins its board drivers as submodules and its lock carries feed sources only; this repository carries both, and every component revision in the lock matches its pin in the component catalog.
- unixnu.lock is machine written: fetch rewrites it with a single header comment and drops any comment added by hand. Keep explanations out of the lock and record them here, so the file stays byte-identical to what fetch produces. The profile's explicit xnu\_revision takes priority over the lock, so the xnu entry follows the OS profile.
- The default install path writes the OS windows into userdata, which is Android's /data and leaves the system images intact but the stock install unusable. The dual-system partition tool instead carves a unixnu partition from the end of userdata, preserving userdata's start, type, GUID and attributes and leaving metadata, super and boot untouched. README.md records the four-step order that ends in adb reboot system, which is the check that the stock system still boots.
- The dual-system partition tests are documented for Linux, WSL and macOS. On a native Windows host the four RecoveryTests fail because they drive twrp.sh through a POSIX sh and a colon PATH, so they run in the partition-safety build job on ubuntu-latest instead. The seven layout tests that cover GPT entry and GUID preservation, reserved GPT space and F2FS section rounding pass on either host.
- The board hardware values that no public source provides were read from a physical device over read-only adb and recorded in device-inputs.md: the userdata GPT extents and block size, the splash reservation, the DRAM base and the panel geometry. The handset reports a spoofed Xiaomi identity through its userspace properties while its boot image, kernel and device tree identify NX769J, so the values came from the kernel, the device tree and the raw UFS partition table rather than from getprop.
- The kernel build runs in CI on ubuntu-latest with the UniXNU Linux toolchain, upstream clang and an open source Mach-O toolchain rather than Xcode. The toolchain is expensive to build and is cached under /opt/unixnu-linux keyed on scripts/linux. The job also asserts that the patch order unixnu resolves matches patches/xnu/series exactly, so a reordered or dropped patch fails the build rather than silently changing what gets compiled.
- The toolchain cache never persisted and every kernel run rebuilt clang from source, which is the whole 37 minutes. The kernel job is expected to fail while this port is being brought up and actions/cache's combined form only saves on success, so the entry was never written. save-always had no effect and was replaced with explicit restore and save steps, the save running on always\(\). Restoring the cache then skipped setup-toolchain.py and with it the apt packages the toolchain links against, so --check failed on missing libclang and libbsd; the host dependencies are now installed in their own step regardless of the cache. The installer itself must also run on a cache hit: it places /usr/bin/xcrun and the CLT shims in system paths the cache cannot hold, and scripts/unixnu/kernel.py requires xcrun, so a cache hit skipped the step and the build stopped at 'xcrun missing'. The installer is idempotent and skips each component that already exists, so running it always costs nothing when the cache hits. Installing under the runner's home rather than /opt is separate hygiene: the installer runs as root and the path is expanded before sudo because sudo resets HOME to /root. scripts/unixnu/kernel.py resolves the toolchain through UNIXNU\_TOOLCHAIN, so the same variable drives both the install and the build.
- The kernel step writes its compile errors to logs/kernel-bootstrap.log rather than stdout. Parallel make then interleaves that file so heavily that the diagnostic for the failing compile is garbled past reading, and a failing run was not diagnosable at all. The job uploads out/\*\*/logs as an artifact and repeats the build with -j 1 on failure, so the retry names the actual error. The retry is incremental because the objects from the parallel pass are reused.
- A change under .github/\*\*, unixnu.lock or os-profiles/\*\* is owned here or in the packaging area, so such a change has to land with a matching finding or evidence entry in the owning area to satisfy the record checker's changed-area rule.
- payload.adt.root\_match\_volume\_uuid is now filled, so \[payload.adt\] has no REQUIRED\_ placeholder left. It is the APFS volume UUID of the OS window, 97A3EB1A-5218-4936-BC85-9574EC2C8CC9, and not the container UUID c155fa03-68f4-42b0-8117-1915b6aa8e4c that sits in the same superblock: /chosen/root-matching matches IOMedia, and the container UUID belongs to the synthesized whole-disk IOMedia rather than to anything that mounts. scripts/extract-root-volume-uuid.py reads the value out of the userdata image the build writes, so it needs no device and no macOS.
- The Data seed workflow puts its diagnostics in the job summary rather than only in the log: the runner's free disk before the download, the disk again once the restore image is deleted, and the seed report. Job logs need repository access to read, so a summary plus an ERR trap in every run step is what makes a failed run diagnosable from the run page: the trap prints ::error title=&lt;step&gt;::&lt;command&gt; and the annotations block is public. The 6 GiB restore image is not cached either -- a cache entry that size doubles the disk peak of a step that is already holding the archive and its 4.7 GiB OS member, and the archive is deleted as soon as the member is out. The Data seed workflow ran twice and failed twice before it was right: cache keys reject commas and the product type iPhone10,3 was in the first key, and the seed script then made a 32 MiB container and grew it, which is both an extra round of attach and resize and a size the iOS 16.5 var tree may not fit into. It now creates the container at its target size and refuses up front when the tree would not fit. \[payload\] tools = true adds a Tools entry to the generated boot menu, which is where the firmware log exporter publishes its QR pages. The generated menu replaces the built-in one and with it its Restart and Power off, so payload.py adds those back; package/unixnu.toml is a hand-written menu and is not the one the payload carries. .github/workflows/data-seed.yml is the macOS runner job that builds the Data seed, and it reads its restore-image pins out of os-profiles/ios-16.5-20F66/profile.toml so the workflow and the profile cannot drift apart.
- board.toml packs a version 4 boot header now that bootimg.py verify\(\) reads the v3 and v4 layout, and the os\_version 16.0.0 and os\_patch\_level 2026-08 it declares reach mkbootimg instead of being dropped; kernel\_compression stays gzip.
- \[payload\] size\_mib is 64 and adt.owned\_memory\_size is 0xC0000000. The payload is capped by the 96 MiB vendor\_boot partition, whose rebuilt header places the ramdisk at 0x40000000. The 3 GiB window comes out of the High\_RAM bank at 0x8C0000000 that the minimal firmware describes; with 512 MiB jetsam killed daemons by the dozen.
- kernel\_args is "-v debug=0x8 native-ufs-probe=10". payload.py refuses native-ufs-root=1 without sheng-pmgr=2, so the images that reach the iOS userland replace the args line of the payload unixnu.toml after unixnu build payload; board.toml records the arguments. serial=3 selects the Apple SoC UART, which this board does not expose.
- \[payload\] size\_mib is 76 when the GPU addon is packed \(scripts/make-nx769j-gpu-addon.py, about 12 MiB\): the kernel and the Data seed left 7 MiB of 64, and the ramdisk still fits the 96 MiB vendor\_boot partition beside its header and DTB.

### Completion criteria

- All source pins resolve; every selected component has a record; status shows the intended overrides and patch order.

### Current limits

- local.toml can select a different source from the published pin; record the effective source in each verification result.
- The SoC source is the SM8550 repository. A dedicated UniXNU-sm8650-common would carry the SM8650 CPU topology and Adreno 750 platform operations instead of board-level overrides.

### Next action

- Compare the effective status output whenever a profile, source or component selection changes.
- Extract the SM8650 CPU topology and platform operations into UniXNU-sm8650-common once the board needs GPU power votes.

### Evidence

- `source`: [Board configuration, component selection, defconfig and patch order described in this section; \[firmware.defines\] for the EDK II build, and \[payload.adt\].root\_match\_volume\_uuid, which is the APFS volume UUID of the OS window, 97A3EB1A-5218-4936-BC85-9574EC2C8CC9, read out of the volume superblock of the built userdata image by scripts/extract-root-volume-uuid.py. Note the other UUID in the same container: c155fa03-68f4-42b0-8117-1915b6aa8e4c is the container's nx\_uuid and is what some tools label the APFS volume ID, but it sits at block+0x48 of the container superblock and matches the synthesized whole-disk IOMedia rather than anything that mounts. firmware.py drives EDK II build directly and so bypasses Mu-Silicium's build driver; an undefined ENABLE\_SECUREBOOT reaches SecureBootHandlerLib as an empty token and fails the preprocessor](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/board.toml)
- `source`: [SoC source URL and reviewed commit pinning the SM8550-common revision](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/feeds.toml)
- `source`: [Measured board inputs with the read-only adb commands that produced them](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/device-inputs.md)
- `source`: [The Build workflow sets CCACHE to scripts/compile-records.py for the kernel step, so the per-object compile recipes the archive builders replay are produced on CI as they are locally, and reports how many were written](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/.github/workflows/build.yml)
- `source`: [The \[kernel\] archives list drops build-mockfs-fixture.py, which the kernel only force-loads when MOCKFS\_MODE is 1, and \[firmware\] gains the full uefi-nx769j platform package table](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/board.toml)
- `host`: [2026-10-30: the resolve step ran to completion and reported the 64 patches of patches/xnu/series in order with every selected component at its pinned revision. python3 scripts/porting-record.py check --device ../UniXNU-NX769J then reported 13 structured areas checked, and scripts/check-repository.py reported the repository structure consistent.](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/docs/HOST-VERIFY.md)
  Command: <code>./unixnu status --json -D ../UniXNU-NX769J</code>. Revision: `dd97bc4b307f77df2f6189b7c92881133cc24ac3`.

## Firmware and boot {#firmware}

`host-verified`

Components: `DarwinBoot`.

### Hardware and dependencies

- uefi-nx769j Mu-Silicium platform package for the Pineapple QRD base board.
- Stock firmware DTB carried in the device vendor\_boot image.
- UEFI GOP handoff, PSCI SMC interface and the vendor firmware inventory from proprietary-files.txt.
- Android 14 ABL: boot header version 4, 4096-byte pages, kernel base 0x0.

### Configuration

- firmware.config = nx769j; firmware.dsc = Platforms/ZTE/nx769jPkg/nx769j.dsc; firmware.fd = Build/nx769jPkg/&\#123;target&\#125;\_CLANGPDB/FV/SILICIUM\_UEFI.fd. The vendor directory is ZTE, not Nubia: nubia is ZTE brand and the verified sibling package is Platforms/ZTE/nx729jPkg.
- firmware.preflight = \[scripts/check-nx769j-firmware.py\], which checks the Mu-Silicium layout, that Resources/Configs/nx769j.toml agrees with board.toml, that the DSC includes the SM8650 SoC package and that the vendor DXE drivers are present.
- firmware.submodules = \[Common/Mu, Common/Mu\_OEM\_Sample, Silicium-ACPI, Silicon/Silicium/OpensslPkg/Library/OpensslLib/openssl\]; Mu\_Basecore is the separate &\#123;edk2&\#125; checkout, not a submodule.
- firmware.patches = \[Resources/MuPatches/Gic-Spurious.patch\], applied to the shared edk2 tree for the build and reverted afterwards.
- firmware.packages = \[&\#123;uefi&\#125;, &\#123;uefi&\#125;/Platforms/ZTE, &\#123;tree&\#125;/package, &\#123;tree&\#125;/drivers/DarwinBoot, &\#123;edk2&\#125;, &\#123;uefi&\#125;/Common/Mu, &\#123;uefi&\#125;/Common/Mu\_OEM\_Sample, &\#123;uefi&\#125;/Silicon/Qualcomm, &\#123;uefi&\#125;/Silicon/Silicium, &\#123;uefi&\#125;/Silicium-ACPI, &\#123;uefi&\#125;/Silicium-ACPI/Platforms/ZTE, &\#123;uefi&\#125;/Silicium-ACPI/Silicon/Qualcomm\].
- firmware.defines.DEVICE\_MODEL = nx769j.
- The platform DSC includes LanaiPkg/LanaiPkg.dsc.inc with SOC\_TYPE = 2. LanaiPkg is Mu-Silicium SM8650 support and SOC\_TYPE 2 is SM8650-AB, Snapdragon 8 Gen 3 at 3.30 GHz with 8 cores.
- \[bootimg.image\] base = 0x0, pagesize = 4096, header\_version = 0. The ABL is a version 4 boot chain, and Resources/Configs/nx769j.toml records 4, but bootimg.py merges DEFAULTS, then the firmware config and then board.toml, so board.toml decides what is packed: bootimg.py verify\(\) only reads v0/v1/v2 headers and a v4 image fails its round-trip check. Extending verify\(\) for v4 is the fix if the ABL rejects the v0 image.

### Procedure

- Read https://unixnu.com/porting/uefi-firmware and create the uefi-nx769j platform package.
- Include UniXNU, UniXNUPkg, DarwinBoot and, for a Mu-Silicium initrd, UniXNURamDiskDxe, DiskIoDxe and FAT support in the DSC and FDF.
- Include the firmware log exporter from https://unixnu.com/porting/log-capture\#firmware-setup so logs can be scanned from the menu during bring-up.
- Run ./unixnu build firmware -D ../UniXNU-NX769J --uefi ../uefi-nx769j and record the firmware commit, output FD and handoff memory map.
- Run ./unixnu bootimg with the firmware DTB and inspect the payload report.

### Development findings

- Mu-Silicium names SoC packages by Qualcomm platform codename, not by part number. NX769J is Lanai: the device firmware reports baseband 5.0.c3-00030-LANAI\_GEN\_PACK and trustzone LANAIAAAAANAZT, and LanaiPkg.dsc.inc declares SM8650-AA through SM8650-AC together with the GIC bases 0x17100000 and 0x17180000 that this board measures. The KailuaPkg that nx729jPkg includes is SM8550 and is wrong for this board.
- UniXNU/uefi-sheng branch sheng already carries Platforms/ZTE/nx729jPkg, a complete platform package for a nubia RedMagic one SoC generation back whose boot.img reaches fastboot boot OKAY on hardware. Platforms/ZTE/nx769jPkg is the same derivation from the Pineapple QRD base board that nx729jPkg is, so the vendor directory is ZTE rather than Nubia.
- nx729j.toml sets boot\_image.header\_version = 4 where sheng and qrd8550 use 3 and 0, which confirms the NX769J ABL setting independently of the board configuration.
- The UniXNU boot chain modules are not a firmware-side gap: ./unixnu build package builds UniXNU.efi, UniXNUDxe.efi and UniXNURamDiskDxe.efi on Linux with CLANGPDB, which is what proves the DSC integration points this design specifies resolve. What the firmware step still needs is the vendor binary set.
- The firmware DTB is a separate input to boot-image assembly; XNU consumes the ADT generated from the board DTS.
- NX769J boots through UEFI: the board configuration sets TARGET\_USES\_UEFI := true and records BOARD\_BOOTIMG\_HEADER\_VERSION := 4. What the ABL does with the version 0 image unixnu packs is unverified; the sibling RedMagic port packs the same v0 image and fastboot-boots it on hardware, which is the evidence that this is the right shape.
- The stock bootloader keeps a contiguous-splash region. It is measured at 0xe3940000 with size 0x2b00000 and label cont\_splash\_region, and board.toml re-adds it to the boot image's device tree through a \[\[bootimg.dtb\_node\]\] entry, the way sheng declares /reserved-memory/splash\_region.
- The device tree model stays the Qualcomm reference name on this board family. This unit reports 'Qualcomm Technologies, Inc. Pineapple MTP' with compatible qcom,pineapple-mtp and qcom,pineapple, and the NX769J stock DTB overlay in the public dump targets qcom,pineapple-qrd. The board DTS therefore names nubia,nx769j with the qcom,pineapple fallbacks.
- The firmware step now runs end to end. All 52 vendor modules are extracted from uefi.img and laid out with their INF wrappers under Binaries/nx769j, the firmware DTB is extracted from vendor\_boot tree 2, and ./unixnu build firmware --uefi ../uefi-nx769j produces Build/nx769jPkg/DEBUG\_CLANGPDB/FV/SILICIUM\_UEFI.fd at exactly 3145728 bytes, which is \[uefi\_fd\] size and what firmware.py checks. Mu\_Basecore has to be initialised as a submodule before that: it is the &\#123;edk2&\#125; tree the build runs against and it is not in the four submodules firmware.submodules lists. boot.json records the same fd\_sha256 that the build produced, so the firmware packed into boot.img is the firmware that was built.
- firmware/ changes do not reach the build until they are lifted into the Mu-Silicium checkout: firmware.py drives EDK II against the checkout's copies and never copies from the device repository, so cp -R firmware/. ../uefi-nx769j/ is a required step and a missed one builds stale sources without any warning. The preflight cannot catch it either, because vendor\_drivers\(\) reads the platform Include/ from the device repository when the checkout's is absent. Adding the log exporter and rebuilding without lifting produced a byte-identical-looking FD that simply did not contain the module.
- The firmware log exporter is integrated and is in the firmware volume: AdvancedLogDxe builds as its own FFS, GenFfs names it 8D4E7F50-3A2C-4C9A-9E1B-50C4C8472D41 and FV/FVMAIN.inf lists it, so it rides in the compressed FvMain. board.toml \[payload\] tools = true adds the Tools entry to the generated menu, which is where it publishes the log. What is not done is step 2 of the log-capture procedure: nothing routes this platform's debug output into the Advanced Logger, so the buffer the exporter reads is whatever LanaiPkg's DebugLib happens to write.
- The version 4 boot header the board configuration records does boot on this ABL. The record packed header\_version 0 because bootimg.py verify\(\) only read the v0/v1/v2 layout; with verify\(\) extended for v3/v4 the image packs as v4 with no boot ramdisk at all and reaches the UniXNU menu, the loader and the kernel branch, which closes the open question about what this ABL does with a v0 image by not packing one.
- DarwinBoot has to be in the firmware volume when the payload comes from a vendor\_boot ramdisk. The xnu entry type resolves through UNIXNU\_LOADER\_PROTOCOL and only DarwinBoot installs it, so with loader = firmware and no DarwinBoot module in DXE.inc the entry fails with returned: Unsupported, an error that names neither the protocol nor the missing module.

### Completion criteria

- Firmware image builds, enters UniXNU, publishes the framebuffer and preserves the documented memory reservations.

### Current limits

- Library/MemoryMapLib.c is rebuilt from this board's firmware device tree rather than carried over. Every one of the 36 fixed-address reservations has a descriptor named after its node, and the check over the table reports no overlaps and no uncovered reservation. UEFI's own regions -- FD Reserved, UEFI Stack, SEC Heap, Sched Heap, FV Region, UEFI RESV, Kernel, DXE Heap -- are kept where nx729jPkg puts them, which fits this board's free band 0xa1f80000..0xd7e00000 exactly. Display Reserved moved to the measured splash at 0xE3940000, and DXE Heap now starts at 0xB8000000 because the region nx729j gave to its splash is ordinary RAM here and the device tree reserves nothing in it.
- The vendor UEFI DXE drivers are laid out and the firmware builds. scripts/extract-uefi-drivers.py recovers all 52 that the platform includes name, from uefi.img, where they sit in gzip-compressed nested firmware volumes under an outer volume holding only SEC and a platform configuration. Twelve carry a UI name different from the INF name the DSC uses -- I2CDxe's module is called plain I2C -- and the script maps them rather than guessing by prefix. The expected set is read from APRIORI.inc, DXE.inc and RAW.inc rather than kept in step with them: APRIORI.inc names one module that DXE.inc has commented out. They cannot be redistributed, so every build machine runs the extraction.
- The Silicium-ACPI SoC tables are Kailua's, which is SM8550. Silicium-ACPI has no Lanai set, and APIC, GTDT and PPTT describe Kailua's cores where this board has two A520, five A720 and one X4. XNU reads the Apple device tree rather than ACPI, so this does not affect the XNU boot, but the tables are wrong for an ACPI operating system.
- SOC\_TYPE is set to 2 from the board name and the 8-CPU topology. The device does not record the prime core maximum frequency, so 2 against 4 \(3.30 against 3.40 GHz\) is not measured.

### Next action

- Build a Lanai ACPI table set, or drop the tables from the DSC if XNU is the only target. Silicium-ACPI has none and the Kailua tables describe a different CPU topology.
- Read the prime core's maximum frequency from the device and settle SOC\_TYPE 2 against 4, which is 3.30 against 3.40 GHz.
- Then reach the UniXNU menu with a published 1116x2480x32 framebuffer, which is the first host-side observation that the firmware runs.

### Evidence

- `source`: [The uefi-nx769j platform package design: the Lanai SoC selection, every board.toml and DSC value with its provenance, the required UniXNU module integration, the vendor input list and the open items](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/docs/UEFI-FIRMWARE.md)
- `source`: [Device configuration staged for the Mu-Silicium checkout: uefi\_fd 0xA7100000 for 0x300000 and the version 4 boot header the NX769J ABL requires](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/firmware/Resources/Configs/nx769j.toml)
- `source`: [Recovers all twenty vendor UEFI DXE drivers from uefi.img: the image's outer volume holds only SEC and a platform configuration, and the modules sit in gzip-compressed nested volumes. Nine carry a UI name different from the INF name the DSC uses, and the script maps them](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/scripts/extract-uefi-drivers.py)
- `source`: [Recovers all 52 vendor UEFI DXE drivers from uefi.img and lays each out with its EDK II INF wrapper and depex under Binaries/nx769j. The outer volume holds only SEC and a platform configuration; the modules are in gzip-compressed nested volumes. Twelve carry a UI name different from the INF name and the script maps them](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/scripts/extract-uefi-drivers.py)
- `source`: [Splits the vendor\_boot dtb field into its device trees and prints each one's model, qcom,msm-id and reservations. This is where the memory map data comes from: 49 reserved-memory nodes, 36 at fixed addresses, and the four Pineapple trees byte-identical in that set](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/scripts/extract-firmware-dtb.py)
- `source`: [The board memory map, rebuilt from the firmware device tree: every one of the 36 fixed-address reservations has a descriptor named after its node, UEFI's own regions sit in the free band the device tree leaves open, and the table has no overlaps and no uncovered reservation](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/firmware/Platforms/ZTE/nx769jPkg/Library/MemoryMapLib/MemoryMapLib.c)
- `source`: [Platform DSC staged for the Mu-Silicium checkout: LanaiPkg with SOC\_TYPE 2, the measured framebuffer geometry and DRAM base, the board SMBIOS identity and the UniXNU and DarwinBoot components](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/firmware/Platforms/ZTE/nx769jPkg/nx769j.dsc)
- `source`: [Preflight that firmware.py runs before EDK II: layout, board.toml agreement, the SoC package include, UniXNU module coverage and the vendor DXE inventory. With the extraction done it reports 52/52 present and the tree consistent with board.toml](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/scripts/check-nx769j-firmware.py)
- `source`: [The flattened-device-tree reader the firmware tools share: the node walk and the reserved-memory extents. extract-firmware-dtb.py and check-memory-map.py both read reservations through it, so the listing and the check cannot drift apart](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/scripts/fdt.py)
- `source`: [Compares MemoryMapLib.c with the reservations of the firmware device tree and with the ones board.toml \[\[bootimg.dtb\_node\]\] adds. It refuses an uncovered reservation, two descriptors covering one range, a DDR descriptor outside the DRAM window and a descriptor that covers nothing and is not a UEFI region. Over the built tree: 64 descriptors, 37 fixed reservations, 37 covered exactly once, 0 unexplained](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/scripts/check-memory-map.py)
- `source`: [The hash of every extracted vendor module and of the two flash-package images they come from, so a build machine can prove it extracted from the right uefi.img rather than from a different firmware](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/proprietary-files.txt)
- `source`: [The firmware log exporter of https://unixnu.com/porting/log-capture\#firmware-setup: UniXNUPkg/Driver/AdvancedLogDxe/AdvancedLogDxe.inf in \[Components\], AdvancedLoggerAccessLib and QrEncoderLib mapped from Common/Mu, and PcdUniXNUDeviceModel set to nx769j so the exported log pages are named after the board. Its Depex is gAdvancedLoggerProtocolGuid, so it loads only when the platform's Advanced Logger is configured and the Tools entry appears then](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/firmware/Platforms/ZTE/nx769jPkg/nx769j.dsc)
- `host`: [2026-10-30: EDK II built Platforms/ZTE/nx769jPkg/nx769j.dsc with CLANGPDB and produced Build/nx769jPkg/DEBUG\_CLANGPDB/FV/SILICIUM\_UEFI.fd at 3145728 bytes, exactly \[uefi\_fd\] size, sha256 b06906387e20df18f2eef45267ccc11160af4b3ed8e30887a4b1c6d4df7a4fbc. The preflight reported 52/52 vendor drivers present and the tree consistent with board.toml, and AdvancedLogDxe is in the volume: its FFS is 8D4E7F50-3A2C-4C9A-9E1B-50C4C8472D41 and FV/FVMAIN.inf lists it. Nothing here is booted.](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/docs/HOST-VERIFY.md)
  Command: <code>./unixnu build firmware -D ../UniXNU-NX769J --uefi ../uefi-nx769j</code>. Revision: `dd97bc4b307f77df2f6189b7c92881133cc24ac3`.
- `device`: [A 3145728-byte FD sha256 8ecc5f0400c0369c, header\_version 4 without a boot ramdisk and vendor\_boot carrying a 64 MiB payload: the firmware reaches the UniXNU menu, reports payload initrd with fs 1 and follows the UniXNU entry to the DarwinBoot hand-off. Photographs of the menu, the payload line and the hand-off summary are the accessible result.](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/docs/DEVICE-EVIDENCE.md)
  Command: <code>adb reboot fastboot; fastboot flash boot_a boot.img; fastboot flash vendor_boot_a vendor_boot.img; fastboot reboot</code>. Revision: `2a265afdbd95d45e4a90664157e793c3bfee3755`.

## CPU and interrupts {#cpu}

`device-verified`

Components: `ArmCpu`.

### Hardware and dependencies

- SM8650 CPU topology from mainline sm8650.dtsi: cpu0-1 arm,cortex-a520, cpu2-6 arm,cortex-a720, cpu7 arm,cortex-x4.
- MPIDR affinities 0x0, 0x100, 0x200, 0x300, 0x400, 0x500, 0x600, 0x700.
- GICv3 distributor 0x17100000/0x10000, redistributors 0x17180000/0x200000 with \#redistributor-regions = 1 and redistributor-stride 0x40000, ITS at 0x17140000/0x40000.
- 19.2 MHz timer. PSCI uses SMC. GIC PPI partitions group cpu0-1, cpu2-6 and cpu7.

### Configuration

- dts/nx769j.dts includes sm8550.dtsi and replaces each cpuN compatible with the SM8650 core name, keeping the DTSI MPIDR values.
- unixnu,cluster-type is not set: this kernel has MAX\_CPU\_CLUSTERS 1 and no native-smp-type-clusters patch, so all eight CPUs run as one SMP cluster.
- CONFIG\_XNU\_ARMCPU=y and CONFIG\_XNU\_NATIVE\_ARCH\_TIMER=y from the ARM64 common fragment.
- Boot arguments sheng-smp=1 armcpu-spi-ipi=1. drivers/ArmCpu starts the secondary cores only with sheng-smp=1; armcpu-spi-ipi=1 is the IPI path sheng uses under the same Gunyah hypervisor.
- package/cpu/SmpReport.cpp and package/cpu/CpuDvfs.cpp build into libNX769JProbes.a \(scripts/build-nx769j-probes.py, CONFIG\_XNU\_EXTRA\_LD\_ARCHIVES\). patches/xnu/nx769j-probes.patch starts the governor from bsd\_init and prints both in the 15 s heartbeat.
- Boot argument nx769j-dvfs: 1 runs the governor \(default\), 2 holds every domain at its highest non-boost row, 0 only reports.

### Procedure

- Compile the board DTS and inspect enabled CPUs, GIC ranges and timer properties in the generated ADT.
- Record per-CPU entry, timer interrupts and inter-processor interrupt delivery at the checkpoints in https://unixnu.com/porting/bring-up.

### Development findings

- unixnu,cluster-type stopped the kernel silently in ml\_parse\_cpu\_topology. With MAX\_CPU\_CLUSTERS 1 the first P core gives phys\_cluster\_id 1 and fails assert\(phys\_cluster\_id &lt;= MAX\_CPU\_CLUSTER\_PHY\_ID\), before any console exists. Progress strips located it on the device and removing the property moved the last strip to the set\_mmu\_ttb call in arm\_vm\_init; see docs/DEVICE-EVIDENCE.md.
- The SM8550 DTSI declares three A510 cores followed by A715, A710 and X3 cores. SM8650 instead has two A520 cores first and a single X4 prime core last, so the compatible strings must be replaced per node while the MPIDR layout is unchanged at 0x100 spacing.
- The GIC PPI partitions in sm8650.dtsi confirm the grouping independently of the core names: partition 0 is cpu0-1, partition 1 is cpu2-6 and partition 2 is cpu7.
- CPU affinity values are hardware identifiers; enabled CPU count and MPIDR affinities must be checked together.
- The device confirms the MPIDR affinities 0x0, 0x100, 0x200, 0x300, 0x400, 0x500, 0x600, 0x700 across its eight cpu@N nodes. Its vendor kernel names the cores qcom,kryo rather than the mainline ARM core names; the board DTS keeps the mainline names that sm8650.dtsi declares and that the UniXNU CPU driver matches on.
- Without sheng-smp=1 every boot ran on cpu0 alone: the Setup stackshot showed a single idle thread and Setup was killed by the FrontBoard scene-create watchdog while that CPU was at 100 %. With sheng-smp=1 armcpu-spi-ipi=1 all seven secondaries reach ArmCpu step 7 with PSCI CPU\_ON returning 0, and 152 processes run at 66 s instead of 105 s.
- SM8650 has four EPSS performance domains at 0x17d91000 + domain \* 0x1000 \(qcom,freq-domain of each cpu node\): domain 0 is cpu0-1 \(A520\), 3 is cpu2-4 \(A720\), 1 is cpu5-6 \(A720\) and 2 is cpu7 \(X4\). Each domain has its enable at +0x0, its state at +0x20, its control at +0xb0, a 40-row factory LUT at +0x100 \(frequency = L\_VAL x 19.2 MHz, core count 1 marks a boost row\) and the perf-state request at +0x320. EPSS selects the voltage, so the governor writes only the request.
- Before the governor the domains kept the request the boot chain left. CpuDvfs.cpp samples each core's idle ticks every 50 ms, requests 1.25 x the busy share of the current frequency, raises at once, lowers after four low samples and holds 75 % of the cap for a second after a touch report.

### Completion criteria

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU.

### Current limits

- Only the CPU perf-state requests are written. CPU idle states, thermal limits and the L3 and DDR votes are not implemented.
- All eight CPUs run as one SMP cluster because this kernel has MAX\_CPU\_CLUSTERS 1.

### Next action

- Measure frequency under load per domain from the heartbeat, then add thermal limits before raising the cap to the boost rows.

### Evidence

- `source`: [SM8650 CPU topology, MPIDR affinities and GIC handoff described in this section](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/dts/nx769j.dts)
- `source`: [Measured MPIDR affinities across the eight cpu@N nodes and the vendor core naming](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/device-inputs.md)
- `device`: [cpus 8 avail 8; all seven secondaries at ArmCpu step 7, PSCI CPU\_ON 0; 152 processes at 66 s against 105 s on one core; the lock screen wallpaper loads \(row smp2\).](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/docs/DEVICE-EVIDENCE.md)
  Command: <code>EDL (9008) write of the run's vendor_boot image to vendor_boot_a (LUN 4, start sector 281670, 24576 sectors); payload unixnu.toml args "-v debug=0x8 native-ufs-root=1 launchd_unsecure_cache=1 sheng-aks=1 sheng-data-persist=2 sheng-data-reset=1 sheng-smp=1 armcpu-spi-ipi=1"</code>. Revision: `7ec306eb682ff9a6488bd8439d9b53af9942ab17`.
- `device`: [The governor runs with nx769j-dvfs=1 by default and the UI is clearly smoother \(user report, row dvfs\).](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/docs/DEVICE-EVIDENCE.md)
  Command: <code>EDL (9008) write of the run's vendor_boot image to vendor_boot_a (LUN 4, start sector 281670, 24576 sectors); payload unixnu.toml args "-v debug=0x8 native-ufs-root=1 launchd_unsecure_cache=1 sheng-aks=1 sheng-data-persist=2 sheng-data-reset=1 sheng-smp=1 armcpu-spi-ipi=1"</code>. Revision: `e3870a17481273c46616ba80559c1ae574ef5960`.

## Memory and DMA {#memory}

`device-verified`

### Hardware and dependencies

- ARM64 Qualcomm DRAM base 0x80000000, confirmed on the device by gunyah\_hyp\_region@80000000 and the lowest System RAM range.
- Handoff window 0x80000000 bytes at 0x80000000, matching payload.dram\_size.
- Measured contiguous-splash reservation at 0xe3940000 with size 0x2b00000, label cont\_splash\_region.
- Apps SMMU at 0x15000000/0x100000 and GPU SMMU at 0x03da0000/0x40000, both qcom,sm8650-smmu-500.
- UFS host and PHY register ranges shared with SM8550.

### Configuration

- device\_tree.source = device:dts/nx769j.dts; include\_dirs = \[soc:dts\].
- memory@80000000 declares one contiguous DRAM range; payload.adt.owned\_memory\_size and payload.dram\_size are both 0x80000000.
- reserved-memory declares splash\_region at 0xe3940000 with size 0x2b00000 and no-map, and board.toml re-adds the same node to the boot image tree.

### Procedure

- Compare firmware RAM ranges, reserved regions, DTS ranges and ADT memory-map entries.
- Check DMA buffers against controller address width, cache policy and SMMU mapping before submitting work.
- Record the measured reservations in device-inputs.md with the command that produced each value.

### Development findings

- The memory node describes the contiguous DRAM range handed to XNU, not the installed RAM. This unit reports MemTotal 15705424 kB, about 15.0 GiB usable from a 16 GiB SKU, with System RAM ranges above 4 GiB at 0x880000000, 0x8b0000000, 0x8c0000000 and 0xa00000000. UniXNU takes one contiguous window from that map.
- The handoff window and payload.dram\_size are still 2 GiB at 0x80000000, following sheng and caihong. UniXNU-nx729j, a RedMagic 8 Pro+ port built on the same code base, instead passes the full 16 GiB computed from the device ddr-regions 0x80000000/2G plus 0x880000000/6G plus 0xa00000000/8G, and this unit's measured System RAM shows the same three-region shape. The two parameters are independent, so they need deciding together against the firmware memory map before the first kernel boot rather than assumed from either port.
- The splash reservation is the one board value that only the device can give: node name splash\_region, label cont\_splash\_region, reg 0xe3940000 with size 0x2b00000. The node name and label match UniXNU-sheng and the size also matches sheng and shennong, so only the address is board specific.
- Physical register translation and CPU virtual mappings have different purposes. Preserve physical resource ranges in hardware descriptions.
- The Apps SMMU and GPU SMMU register ranges are identical between SM8550 and SM8650, so the shared SMMU kit is applicable to this board.
- An exported register below 16 MiB is an error: the common generator reads the arm-io window base as the SoC base and requires it to be non-zero.
- The kernel memory node is split into System RAM ranges with reservations removed, not the raw DRAM extent. Do not copy it into the board DTS; the board declares the handoff window.
- DRAM above 4 GiB is not reachable from this firmware. Describing 0x100000000 + 0x200000000 in MemoryMapLib.c makes the next access fault with a synchronous external abort at FAR 0x1001D0000, so the 12 GiB unit only offers what sits below 4 GiB until whatever protects the high range is understood.
- The window DarwinBoot hands XNU is owned\_memory\_size carved out of the largest contiguous conventional run, so the map and \[payload.adt\] have to agree. With the DXE heap alone at 0xB8000000 there are 508.8 MiB of conventional memory and a 2 GiB owned\_memory\_size fails with NO WINDOW 80000000 BIG RUN 12845000; making the 1 GiB Kernel region conventional raises the run to 764.8 MiB and a 512 MiB window is allocated.
- check-memory-map.py tells DDR descriptors from MMIO by the ResourceType field and only accepts MMAP\_IO for the latter, so register regions written with a numeric resource type are parsed as DDR and reported as covering no reservation.
- SM8650 has no RAM at 0x100000000, which is why describing that range faulted. The minimal firmware describes one bank above 4 GiB, High\_RAM, 4 GiB at 0x8C0000000, and DarwinBoot takes the 3 GiB XNU window \(owned\_memory\_size 0xC0000000\) out of it. UEFI, DarwinBoot and XNU run from that bank.
- With memSize above 1 GiB arm\_init selected 16K pages and pmap panicked with "write\_pte\_fast: PTE write is unaligned" at load\_init\_program. arm\_init.c includes apple\_arm64\_common.h, which defines APPLE\_ARM64\_ARCH\_FAMILY, so the 4K guard never fired. patches/xnu/nx769j-native-4k-page-shift.patch decides 4K pages before that include.

### Completion criteria

- All handoff regions are accounted for and each enabled DMA engine accesses its allocated range with the documented cache policy.

### Current limits

- The removed regions listed by the firmware are not all enumerated here; only the splash reservation is consumed by the current configuration.
- Of the installed 12 GiB only the 4 GiB High\_RAM bank is described, and XNU receives 3 GiB of it.

### Next action

- Describe the remaining DRAM banks from the device ddr-regions once the firmware can map them, then raise owned\_memory\_size.

### Evidence

- `source`: [DRAM handoff window and reserved-memory node state described in this section](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/dts/nx769j.dts)
- `source`: [Measured DRAM base, System RAM ranges and the splash reservation at 0xe3940000 with the commands that produced them](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/device-inputs.md)
- `source`: [The UEFI memory map is now checked against the reservations rather than reviewed. It compares MemoryMapLib.c with the firmware device tree and with the splash board.toml \[\[bootimg.dtb\_node\]\] adds, and reports 64 descriptors with 37 fixed reservations each covered exactly once and 0 unexplained. scripts/test\_check\_memory\_map.py covers the four ways the map can be wrong](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/scripts/check-memory-map.py)
- `device`: [Two failed hand-offs and one successful one bracket the rule: owned\_memory\_size 0x80000000 against 0x12845000 of conventional memory drew NO WINDOW 80000000 BIG RUN 12845000 on screen, describing memory above 4 GiB drew a synchronous external abort at FAR 0x1001D0000, and Kernel as Conv with owned\_memory\_size 0x20000000 reaches the hand-off with owned 20000000. check-memory-map reports 64 descriptors, 37 reservations covered once and 0 unexplained over the final table.](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/firmware/Platforms/ZTE/nx769jPkg/Library/MemoryMapLib/MemoryMapLib.c)
  Command: <code>python3 scripts/check-memory-map.py --dtb ../uefi-nx769j/Resources/DTBs/nx769j.dtb --map firmware/Platforms/ZTE/nx769jPkg/Library/MemoryMapLib/MemoryMapLib.c --board board.toml</code>. Revision: `2a265afdbd95d45e4a90664157e793c3bfee3755`.
- `device`: [With High\_RAM and owned\_memory\_size 0xC0000000 the first boot panics in write\_pte\_fast \(16K pages\); with nx769j-native-4k-page-shift.patch there are no jetsam kills and 152 processes run at 105 s \(rows highmem and highmem4k\).](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/docs/DEVICE-EVIDENCE.md)
  Command: <code>EDL (9008) write of the run's vendor_boot image to vendor_boot_a (LUN 4, start sector 281670, 24576 sectors); payload unixnu.toml args "-v debug=0x8 native-ufs-root=1 launchd_unsecure_cache=1 sheng-aks=1 sheng-data-persist=2 sheng-data-reset=1"</code>. Revision: `bda619dd71ea24ada381a44c375354cb37930534`.

## Storage and root {#storage}

`device-verified`

Components: `ShengUfs`, `VirtioMmioBlock`, `VerifiedRoot`, `AppleKeyStoreState`, `RamBlock`.

### Hardware and dependencies

- UFS host 0x01d84000/0x3000 \(qcom,sm8650-ufshc, jedec,ufs-2.0, SPI 265\) and UFS PHY 0x01d80000/0x2000 \(qcom,sm8650-qmp-ufs-phy\).
- GCC AXI, AHB, UniPro, symbol and PHY auxiliary branches; power domains and firmware link state.
- Apps SMMU at 0x15000000, UFS stream assignment, context-bank ownership, DMA width and cache maintenance.
- NX769J is an A/B device with dynamic partitions; userdata is a f2fs volume at /dev/block/bootdevice/by-name/userdata and the super partition is 9126805504 bytes.

### Configuration

- Select ShengUfs, VirtioMmioBlock and VerifiedRoot; CONFIG\_XNU\_NATIVE\_UFS=y and CONFIG\_XNU\_NATIVE\_VIRTIO\_BLOCK=y.
- dts/nx769j.dts sets &amp;ufs and &amp;ufsphy status = okay.
- board.toml \[userdata\] carries the measured extents: first\_lba 3302184, last\_lba 124002298, lba\_bytes 4096, with OS and SystemOS windows.

### Procedure

- Read https://unixnu.com/porting/ufs with this storage record.
- Inspect clock enables, power state, HCE/HCS, link state, request-list base and SMMU mappings before changing controller ownership.
- Validate SCSI capacity and GPT reads, then publish the OS and SystemOS windows within the userdata range.
- Verify persistent Data writes on the documented Data allocation with a recovery image available.

### Development findings

- UFS host and PHY addresses are identical between SM8550 and SM8650, and the compatible differs only in the SoC name \(qcom,sm8550-ufshc versus qcom,sm8650-ufshc\). The shared ShengUfs controller access applies to this board; the board owns its userdata policy. The device confirms both ranges in /proc/iomem.
- An idle AHB branch may report CLK\_OFF with hardware gating enabled. Check enable and gating bits together.
- SMMU bypass still has address-width constraints. Validate every DMA range and context-bank assignment.
- recovery.fstab mounts /data as f2fs on userdata, so the persistent Data path must handle f2fs rather than the ext4 layout assumed by some board configurations.
- The measured GPT has userdata as the last occupied partition ending exactly on the last usable sector, with 32 table entries of which 12 are used. Those are the preconditions the dual-system partition tool requires, so a unixnu partition can be carved without altering any other entry.
- The device publishes five regular UFS LUNs plus the RPMB and boot well-known LUNs \(49456, 49476, 49488\).
- The public NX769J board configurations record BOARD\_SUPER\_PARTITION\_SIZE := 9126805504 with a TODO saying the value is hardcoded. The measured super partition is 12.0 GiB; that guess is not the real size.
- The OS and SystemOS windows of userdata-root.img are authenticated by owner-signed header-only policies linked into the kernel \(scripts/make-root-policies.py, scripts/policies/ios-16.5-20F66\); the block hash tables travel in the image. The key is .cache/verified-root/owner.pem and is never committed. bsd\_init accepts the owner-verified read-only root when FSIOC\_KERNEL\_ROOTAUTH returns 80, and SystemOS is union-mounted over / so dyld finds the shared cache.
- keybagd needs a system keybag and this board has no SEP. AppleKeyStoreState is the stand-in \(package/KeyStoreBoard.cpp, sheng-aks=1\); it holds no keys.
- A 32 MiB Data seed served from RAM by RamBlock brings up about 130 processes and then fills \(ENOSPC\). The current Data is a 4 GiB seed served from a window at the end of userdata \(sheng-data-persist=2, sheng-data-reset=1\).
- Booting stock Android reformats userdata and with it the OS, SystemOS and Data windows; the next boot reports "no valid root manifest". Charging in Android therefore requires reflashing userdata-root.img afterwards. Charge with the phone powered off.

### Completion criteria

- Host: register, clock, link and SMMU facts match the board inventory.
- Reads: SCSI capacity, GPT and known blocks are correct; OS/SystemOS windows stay within userdata.
- Root: the configured volume mounts and launchd starts. Persistence: writes survive reboot within the allocated Data region.

### Current limits

- payload.adt.root\_match\_volume\_uuid is read out of the built userdata image rather than measured on a device, so it is correct for the image that gets flashed and does not follow a repartitioned or differently imaged device.
- ShengUfs contains sheng Data and log policy that is board specific and is not reused here.
- The GPT extents are measured on one unit. Re-read them before writing, since a different SKU or a repartitioned device has different bounds.
- Data writes persist inside the 4 GiB window; the rest of userdata is unused.

### Next action

- Confirm the SCSI capacity reported by the controller matches the measured GPT: the probe read userdata last 0x3aabffa where device-inputs.md records 0x7641ffa.

### Evidence

- `source`: [UFS host and PHY register ranges, node enables and the A/B userdata layout described in this section](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/dts/nx769j.dts)
- `source`: [Measured GPT extents for userdata, the UFS LUN topology and the /proc/iomem confirmation of the controller ranges](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/device-inputs.md)
- `source`: [Reads the APFS volume UUIDs out of the userdata image the build writes, attributing each to the window it belongs to by reading userdata-root.json. It finds the containers by their NXSB magic and block size, the volumes by theirs, and rejects a candidate whose UUID is not a version 4 UUID. Over the built image it reports the OS window volume 97A3EB1A-5218-4936-BC85-9574EC2C8CC9 and the SystemOS window volume 556915A0-5005-4DE5-B3E4-6B489DBB4C1A, and marks a third container embedded inside the OS volume rather than the window's own](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/scripts/extract-root-volume-uuid.py)
- `device`: [The owner-verified root and the SystemOS union mount: launchd loads without a root panic \(rows policy, rootok and cache\).](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/docs/DEVICE-EVIDENCE.md)
  Command: <code>EDL (9008) write of the run's vendor_boot image to vendor_boot_a (LUN 4, start sector 281670, 24576 sectors); boot arguments as the cache row of docs/DEVICE-EVIDENCE.md states</code>. Revision: `eb6e47b410f65478410e2e55e473d9414c90a468`.
- `device`: [The 4 GiB Data window removes the ENOSPC failures and the system runs for minutes \(row persist\).](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/docs/DEVICE-EVIDENCE.md)
  Command: <code>EDL (9008) write of the run's vendor_boot image to vendor_boot_a (LUN 4, start sector 281670, 24576 sectors); payload unixnu.toml args "-v debug=0x8 native-ufs-root=1 launchd_unsecure_cache=1 sheng-aks=1 sheng-data-persist=2 sheng-data-reset=1"</code>. Revision: `54ba591a41b45d41f0ea33227421fe4e1595a2b0`.

## Display {#display}

`device-verified`

Components: `GopFramebuffer`.

### Hardware and dependencies

- UEFI GOP framebuffer published by uefi-nx769j, its stride, pixel format and handoff.
- NX769J panel: 1116x2480 at 480 dpi \(TARGET\_SCREEN\_DENSITY := 480\).
- MDSS and DPU at qcom,sm8650-mdss / qcom,sm8650-dpu with two qcom,sm8650-dsi-ctrl and qcom,sm8650-dsi-phy-4nm instances.
- Backlight controls through the board panel driver.

### Configuration

- GopFramebuffer is selected, but CONFIG\_XNU\_NATIVE\_LEGACY\_DISPLAY and CONFIG\_XNU\_NATIVE\_MOBILE\_DISPLAY are off: the late archive that defines their probes has no builder in this tree.
- package/display builds houji's IOSurfaceRoot \(SweetSurface\) and AppleCLCD \(SweetFramebuffer\) into the kernel \(scripts/build-nx769j-display.py\). They scan out of the GOP framebuffer. The OS profile leaves out IOSurface, IOMobileGraphicsFamily, IOGPUFamily and AppleM2ScalerCSCDriver, whose classes would clash.
- The board DTS adds /arm-io/disp0 with device\_type display-subsystem, matched by name nx769j,display. The OS profile sets /chosen/display-scale = 3 and display-rotation = 0.
- sweetfb\_noconsole=1 with patches/xnu/nx769j-console-mute.patch stops the text console at the first GUI frame; a panic draws again.

### Procedure

- Verify GOP address, dimensions, stride and pixel layout before enabling presentation.
- Build the late display archive with the selected OS ABI records, then check display publication and frame presentation.
- Record frame timing and pixel format at the checkpoints in https://unixnu.com/porting/bring-up.

### Development findings

- The display source and ABI binding are selected independently of the physical panel configuration; the GOP path presents whatever geometry the firmware publishes.
- The panel geometry is measured on the device: card0-DSI-1 reports 1116x2480x60cmd. That matches the value recorded from the public NX769J board configurations, which also give 480 dpi.
- SM8650 carries two DSI controllers and a DSI PHY per controller; a native scanout path would bind to those rather than to the SM8550 display nodes.
- FrontBoard asserted "FBSDisplayMode cannot be configured as requested" with scale 0 at any canvas size. FrontBoard takes the scale from CADisplayMode.preferredScale, QuartzCore from MobileGestalt main-screen-scale, and MobileGestalt from /chosen/display-scale, which iBoot normally writes. With display-scale 3 backboardd creates a 1125 x 2436 BGRA surface and swaps frames into AppleCLCD.
- iOS renders the 1125 x 2436 iPhone X canvas centred on the 1116 x 2480 panel. Every frame is a CPU copy into the GOP framebuffer.
- watchdogd exits with reason 2/0x5 before it opens IOWatchdog, and the kernel panicked on that exit. houji's IOWatchdog \(package/display/SweetWatchdog.cpp\) replaces AppleARMWatchdogTimer, and patches/xnu/nx769j-watchdogd-not-fatal.patch keeps the exit from rebooting the board.

### Completion criteria

- A known frame appears with correct geometry and colors, then userland presentation and backlight controls work.

### Current limits

- Presentation is a CPU copy into the firmware framebuffer: no GPU composition, no DSI or panel control and no backlight control.

### Next action

- Hand backboardd a Metal device once the GPU area provides one, then measure the frame time against the CPU copy.

### Evidence

- `source`: [GopFramebuffer selection and the native legacy display flag described in this section](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/configs/nx769j_defconfig)
- `source`: [Measured panel geometry 1116x2480 from the DRM connector mode list](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/device-inputs.md)
- `device`: [The Apple logo is drawn: backboardd creates a 1125x2436 BGRA surface and swaps frames into AppleCLCD \(rows display to scale\).](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/docs/DEVICE-EVIDENCE.md)
  Command: <code>EDL (9008) write of the run's vendor_boot image to vendor_boot_a (LUN 4, start sector 281670, 24576 sectors); payload unixnu.toml args "-v debug=0x8 native-ufs-root=1 launchd_unsecure_cache=1 sheng-aks=1 sheng-data-persist=2 sheng-data-reset=1"</code>. Revision: `54ba591a41b45d41f0ea33227421fe4e1595a2b0`.
- `device`: [The iOS 16 lock screen with date, clock, camera button and home indicator; the wallpaper fills in over a minute \(row skipsetup\).](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/docs/DEVICE-EVIDENCE.md)
  Command: <code>EDL (9008) write of the run's vendor_boot image to vendor_boot_a (LUN 4, start sector 281670, 24576 sectors); payload unixnu.toml args "-v debug=0x8 native-ufs-root=1 launchd_unsecure_cache=1 sheng-aks=1 sheng-data-persist=2 sheng-data-reset=1"</code>. Revision: `bda619dd71ea24ada381a44c375354cb37930534`.

## Input {#input}

`device-verified`

### Hardware and dependencies

- NX769J touch controller is a Goodix 9916R. The device firmware ships goodix\_firmware\_9916r.bin and the running kernel registers a goodix\_ts input device at goodix\_ts/input0.
- The catalog input stack is ShengNovatekTouch, written for the Novatek NT36532E on sheng, with ShengHidInput publishing IOHIDDevice reports.
- Buttons register as gpio-keys\_nubia with pmic\_pwrkey and pmic\_resin. Awinic SAR sensing registers as nubia\_tgk\_aw\_sar0\_ch0 and nubia\_tgk\_aw\_sar1\_ch0, and the fingerprint sensor is goodix\_fp.
- Goodix GT9916R \(goodix,brl-d\) on the QUP1 SE4 pins: GPIO 48 MISO, 49 MOSI, 50 CLK, 51 CS; reset GPIO 161, interrupt GPIO 162 \(falling edge\), IO supply switch GPIO 28, analog supply L14B \(pm\_humu\_l14, 3.2 V, RPMh resource ldob14\). Values from the stock dtbo.
- Command DB at 0x81c60000 \(aop\_cmd\_db\_region\) and the apps RSC DRV2 at 0x17a20000 with TCS offset 0xd00.

### Configuration

- No catalog input component is selected. package/touch \(Goodix bus and driver\) and package/hid \(houji's built-in HID event services and SweetHID.cpp\) build into libNX769JInput.a \(scripts/build-nx769j-input.py, CONFIG\_XNU\_EXTRA\_LD\_ARCHIVES\).
- The OS profile leaves com.apple.iokit.IOHIDFamily out of the prelink roots. patches/xnu/nx769j-hid-personality.patch matches SweetHIDButtons and SweetHIDTouch on IOResources.
- patches/xnu/nx769j-probes.patch starts the driver from bsd\_init; nx769j-touch=0 skips it.
- Touch firmware paths and hashes are recorded in proprietary-files.txt.

### Procedure

- Read https://unixnu.com/porting/input.
- Boot with the default arguments and read the touch status lines in the heartbeat: the RPMh vote, the Berlin handshake and the version block.
- Touch the lock screen and the home screen and confirm the contact position, simultaneous contacts and release.

### Development findings

- The Novatek driver's sensor protocol does not match the Goodix 9916R on this board, so reusing it would require replacing the transport and the report parser rather than a configuration change.
- ShengHidInput publishes IOHIDDevice reports from a board touch event source, so the HID layer is reusable once a Goodix event source exists.
- The device confirms the touch controller family: the kernel registers goodix\_ts and goodix\_fp, and the SAR sensors are Awinic parts behind nubia\_tgk\_aw\_sar\* drivers. That matches the goodix\_firmware\_9916r.bin and aw9620x\_\* firmware already recorded in proprietary-files.txt.
- QUP1 SE4 runs SPI firmware 0x102 with if\_disable 0x1: the FIFO interface is off and only GSI DMA is available, so geni\_spi\_init returns -95. houji recorded the same state on SM8650. package/touch drives the four pins as GPIO SPI instead.
- L14B is off at boot and the Berlin handshake reads all 00 without it. The driver reads ldob14 from the command DB \(0x41600\) and votes it through the apps RSC; the vote completes on TCS 0. VRM resources are cmd-db slave 4 \(ARC is 3, BCM is 5\): a check for slave 3 refused the vote. With the vote the handshake returns aa x8, version block BERLIN, patch 9916R.
- The controller reports 16 units per panel pixel \(goodix,panel-max-x/y 17856 x 39680 on the 1116 x 2480 panel\). The display centres the 1125 x 2436 iOS canvas on the panel, so canvas = raw / 16 + \(4, -22\).
- Contacts reach backboardd through houji's in-kernel IOHIDEvent, IOHIDEventServiceQueue and IOHIDEventServiceUserClient. They take the class names IOHIDFamily uses, so IOHIDFamily cannot load next to them. The catalog ShengHidInput is not used.
- Contact frames are read by polling the TLMM edge latch of GPIO 162; no interrupt is attached. Each touch report also feeds the CPU governor's touch hold.

### Completion criteria

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive, and buttons produce expected HID reports.

### Current limits

- SweetHIDButtons is published but no button source feeds it: the power and volume keys do nothing.
- Contact frames are polled rather than interrupt driven.
- Haptics and SAR sensing are out of scope for the first input milestone.

### Next action

- Feed SweetHIDButtons from pmic\_pwrkey, pmic\_resin and gpio-keys\_nubia, then attach the GPIO 162 interrupt in place of the latch poll.

### Evidence

- `source`: [Kernel input device inventory confirming goodix\_ts, goodix\_fp, gpio-keys\_nubia and the Awinic SAR channels](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/device-inputs.md)
- `device`: [Touch works on the lock screen and the home screen \(row touch3\).](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/docs/DEVICE-EVIDENCE.md)
  Command: <code>EDL (9008) write of the run's vendor_boot image to vendor_boot_a (LUN 4, start sector 281670, 24576 sectors); payload unixnu.toml args "-v debug=0x8 native-ufs-root=1 launchd_unsecure_cache=1 sheng-aks=1 sheng-data-persist=2 sheng-data-reset=1 sheng-smp=1 armcpu-spi-ipi=1"</code>. Revision: `3cf0e11617b39ab8c7ff4d91910ce7fd5d2875d9`.

## GPU {#gpu}

`implemented`

### Hardware and dependencies

- Adreno 750, compatible qcom,adreno-43051401 at 0x03d00000/0x40000 with SPI 300.
- GMU qcom,adreno-gmu-750.1 at 0x03d6a000/0x35000 with rscc and gmu\_pdc ranges, SPI 304 and 305 for hfi and gmu.
- GPU SMMU qcom,sm8650-smmu-500 at 0x03da0000/0x40000 with stream assignments 0 and 1 on the GPU and 5 on the GMU.
- ZAP shader firmware and GMU firmware for the Adreno 750 generation.
- gmu\_gen70900.bin, gen70900\_sqe.fw and gen70900\_zap.mbn from the stock vendor partition, and the Linux v6.16 GMU, HFI and a6xx sources, pinned in scripts/data/nx769j-adreno-inputs.json and kept in .cache.
- data-a-live \(MIT\) vktest/mtltest and the metal2vulkan patches, kept in third\_party/data-a-live; the iOS 16 Turnip, the NativeAdrenoMetal plugin and the test programs are built on a Mac by scripts/build-nx769j-metal.sh into .cache/gpu-user \(not committed\).

### Configuration

- No GPU component is selected in components.include. scripts/build-nx769j-gpu.py compiles the needed Adreno740, AdrenoFirmware, ArmSmmu4K, AdrenoPM4 and Sm8550Platform sources by path into libNX769JGpu.a, with patches/drivers/Adreno740/\*.patch applied to a copy of Adreno740.
- CONFIG\_XNU\_NATIVE\_ADRENO=n overrides the y set by soc:configs/sm8550.config.
- dts/nx769j.dts leaves &amp;gpu, &amp;gmu and &amp;gpu\_smmu disabled; package/gpu maps the register windows itself.
- Boot argument nx769j-gpu=&lt;1..9&gt; selects the last bring-up mode; it is unset by default.
- Modes 10 and 11 extend nx769j-gpu: 10 loads the zap shader through TrustZone and leaves secure mode off, 11 publishes the user-client service and the Metal accelerator. nx769j-gpu-zap=0 skips the zap; pandora\_gpu\_metal=1 makes the test programs use the AGX accelerator path; nx769j-gpu-nocgc=1 leaves GPU clock gating at reset \(a bring-up A/B switch\).
- patches/xnu/nx769j-exec-swap.patch runs a test binary in place of a RunAtLoad job \(boot-arg nx769j-execswap\), ignoring the platform Sandbox exec verdict and the AMFI launch-constraint refusal only for binaries below /private/var/ngpu/bin. scripts/make-nx769j-gpu-addon.py packs the plugin and test programs into the GPU addon and appends their CDHashes to the trust bundle.
- patches/drivers/Adreno740/: gen70900-sqe-size \(A750 SQE\), ios16-no-gpu-role \(no task\_get\_gpu\_role on xnu-8796\), and nx769j-submit-trace \(logs each client submission\). execReport in package/gpu prints the live GPU/ring state every heartbeat.

### Procedure

- Read https://unixnu.com/porting/gpu.
- Run python3 scripts/build-nx769j-gpu.py through the kernel build with the firmware in .cache/gpu-firmware.
- Boot with nx769j-gpu=9 and read the NX769J GPU lines of the heartbeat; mode 9 ends at stage fa.

### Development findings

- The catalog Adreno740 driver declares hardware Adreno 740 and SM8550 and is verified only on sheng. This board has Adreno 750, whose GMU reports qcom,adreno-gmu-750.1 where SM8550 reports qcom,adreno-gmu-740.1.
- GPU, GMU and GPU SMMU register ranges are identical between SM8550 and SM8650, so the SMMU and platform kits have matching register inputs; the firmware protocol and the PM4 packet generation are the parts that need qualification for this generation.
- sm8650.dtsi gives the GPU as qcom,adreno-43051401 while sm8550.dtsi gives qcom,adreno-43050a01; the chip ID is what distinguishes the two parts to the driver.
- The Adreno 750 is gen7\_9\_1 \(chip 0x43051401, GMU chip ID 0x7090100\). Linux v6.16 runs it through the a740-family GMU, HFI and hw\_init code, so package/gpu ports UniXNU-sheng GpuPowerProbe \(SM8550 / A740\) with the A750 values: CX GDSC hw\_ctrl at 0x9168, PLL1 L 0x1b alpha 0x1555, hub 200 MHz, GMU 260 MHz, and the global clock-gating path with the P2S handshake in hw\_init.
- Linux v6.16 numbers GMU registers from the gmu block, not from the GPU base. Subtracting the GPU-to-GMU delta again made the cold start stop at status 4 phase 1. The generator now checks that CM3\_SYSRESET lands at gmu + 0x14000.
- gen70900\_sqe.fw is 85360 bytes without its first dword and Adreno740 reserves 77824 bytes for the SQE. patches/drivers/Adreno740/gen70900-sqe-size.patch raises GpuSqeBytes to 0x16000.
- Mode 9 runs CP\_INIT and a CP\_MEM\_WRITE on ring 0 with polled fences. GPU bank 0 reports smmu-fsr 0x400 although the write lands; the cause is not established. gcc\_gpu\_memnoc\_gfx\_clk reads CLK\_OFF with the GPU running.
- With GX powered \(mode 8\) the UI showed screen corruption and black stalls; with mode 9 they did not recur. The cause is not isolated.
- Mode 11 publishes UniXNU's NativeAdrenoPublish service \(class NativeAdrenoGpuPublished\) and a self-defined IOAcceleratorES/AGXAccelerator with MetalPluginName NativeAdrenoMetal, since this kernelcache has no IOGPUFamily. Turnip reaches it with TU\_DARWIN\_SERVICE=IOAcceleratorES, open type 0x4147 \(data-a-live's vktest defaults to the name PandoraAdrenoGpu, which this kernel does not register; pandora\_gpu\_metal=1 selects the AGX path\). Clients connect: the heartbeat shows clients opened.
- On the device Turnip enumerates the GPU \('Turnip Adreno \(TM\) 750', chip 0x43051401, Vulkan 1.4.354\), creates the device, allocates and maps memory, and compiles shaders. \*\*Image clear and compute dispatch run correctly\*\* \(vktest part 3 and part 4, 0 of 4096 words wrong\).
- KNOWN ISSUE, graphics draw hangs \(vktest part 5\). The client submit succeeds and the ring accepts it, but the fence never signals \(vkWaitForFences times out\). execReport at the hang: RBBM\_STATUS 0x00800005 \(GPU busy\), cp-int bit 0, and the ring at rptr holds the submit epilogue \(a Type-4 register write, CP\_THREAD\_CONTROL, CP\_EVENT\_WRITE7 event 0x18\). The CP ran the draw and is wedged at the colour-cache \(CCU\) flush; compute, which does not touch the CCU, completes. This is the blocker for GPU desktop composition \(iOS compositing is Metal render passes\).
- KNOWN ISSUE, buffer fill/update reads back wrong data \(vktest part 2\): the submit completes and the fence signals, but the CPU reads a wrong or zero pattern. A data or cache-coherency problem on the transfer path, distinct from the part 5 hang.
- GPU clock gating must stay enabled. nx769j-gpu-nocgc=1 \(clocks at reset\) makes every client submit hang, including the image clear and compute that otherwise pass, so the A750 global clock-gating path \(setHwcg\) is required, not the cause of the graphics hang.
- The Metal plugin picks its shader-cache directory with confstr\(\_CS\_DARWIN\_USER\_CACHE\_DIR/TEMP\_DIR\); a container-less test process as mobile falls back to /var/tmp \(root 0755\) and cannot create the cache \(EACCES\). Running the test as root \(swapping /usr/bin/IOMFB\_FDR\_Loader\) fixes it; backboardd has a container and is unaffected.
- The graphics draw hang was narrowed by elimination against houji \(same SM8650 / Adreno 750, which reaches GPU composition via a vendor UEFI handoff\). Ruled out: clock gating \(disabling it hangs every submit\), the GBIF bus interface \(writing GBIF\_QSB\_SIDE or GBIF\_CX\_CONFIG from the kernel wedges the bus, so it is firmware/GMU owned\), missing hwInit registers \(every register shared with houji's GpuGen7Table matches\), the ring submit epilogue \(NativeAdrenoRing's CCU\_INVALIDATE\_DEPTH/COLOR fence sequence is byte-identical to houji's\), the memory-path clocks \(gcc\_gpu\_memnoc\_gfx and gcc\_ddrss\_gpu\_axi are both voted on\), and GPU voltage/frequency \(voting the highest OPP does not help\). Everything comparable to houji matches; the remaining difference is the GMU-managed HFI startup state the vendor firmware sets up and this port hand-rolls, which needs offline study of houji's GMU bootstrap and HFI config \(ACD, startup votes\), not device iteration.

### Completion criteria

- GPU submissions complete, mapping/fence handling is correct, a known image renders, and the selected Metal client presents it. Reached so far: image clear and compute render correctly; graphics draw does not.

### Current limits

- Graphics draw hangs at the CCU cache flush and buffer fill/update returns wrong data; only image clear and compute are correct. iOS still composes on the CPU \(backboardd is not a GPU client\), so the desktop is unchanged.
- The A750 \(gen7\_9\_1\) CCU/cache behaviour that wedges the graphics draw is not resolved; the hwInit matches the sheng A740 reference, so the difference is the chip generation.
- No GPU DCVS or bandwidth scaling; only the lowest OPP is voted. The zap path \(mode 10\) is loaded but the graphics path it enables is not yet usable.

### Next action

- Study houji's GMU bootstrap and HFI startup config \(ACD mask, OPP and bandwidth votes\) against ShengGmuBuildStartup, since the graphics CCU-flush hang is in the GMU-managed memory-path state and every register/clock/ring difference has been ruled out.

### Evidence

- `device`: [nx769j-gpu=8: cold start status 0 phase 7, firmware and HFI ready, HFI startup acked, GX ON with RBBM\_STATUS 00000001 \(rows gpu1 and gpu2\).](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/docs/DEVICE-EVIDENCE.md)
  Command: <code>EDL (9008) write of the run's vendor_boot image to vendor_boot_a (LUN 4, start sector 281670, 24576 sectors); payload unixnu.toml args "-v debug=0x8 native-ufs-root=1 launchd_unsecure_cache=1 sheng-aks=1 sheng-data-persist=2 sheng-data-reset=1 sheng-smp=1 armcpu-spi-ipi=1 nx769j-gpu=8"</code>. Revision: `93b1a3302488ee3849adc9c0d837707c46346e99`.
- `device`: [nx769j-gpu=9: mode 9 stage fa, CP\_INIT done with HW\_FAULT 0 and rptr/wptr 11/11, mem write scratch 05e9a750 with fences 1 and 2 \(row gpu3\).](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/docs/DEVICE-EVIDENCE.md)
  Command: <code>EDL (9008) write of the run's vendor_boot image to vendor_boot_a (LUN 4, start sector 281670, 24576 sectors); payload unixnu.toml args "-v debug=0x8 native-ufs-root=1 launchd_unsecure_cache=1 sheng-aks=1 sheng-data-persist=2 sheng-data-reset=1 sheng-smp=1 armcpu-spi-ipi=1 nx769j-gpu=9"</code>. Revision: `8ab48551f7872571322b791bcf67feb3eb624ebf`.
- `device`: [Turnip enumerates the Adreno 750 and clients connect \(clients opened\); image clear and compute return 0 of 4096 words wrong; graphics draw times out with the CP wedged at the CCU flush \(execReport RBBM\_STATUS 00800005, cp-int 1\); buffer fill/update returns wrong data. Photographed across the gpu9..gpu16 images.](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/docs/DEVICE-EVIDENCE.md)
  Command: <code>EDL (9008) write of the run's vendor_boot image to vendor_boot_a (LUN 4, start sector 281670, 24576 sectors); payload unixnu.toml args "... nx769j-gpu=11 sheng-gpu-addon=1 nx769j-execswap=..."</code>. Revision: `abc0b21faa3e60d229baa86139bd094e711832c0`.

## Network {#network}

`planned`

### Hardware and dependencies

- WCN7850 \(FastConnect 7800\) reached over PCIe, with ath12k firmware and board data.
- The catalog Ath12kWifi transport declares hardware qcc2072, qcn9274 and wcn7850 build inputs and board dependencies on PCI configuration, BAR, MSI and DMA operations.
- Ath12kWifi declares os\_abi 'nw\_abi platform interface', which is not the ipados-17.7.11-21H461 ABI.

### Configuration

- No network component is selected. board.toml components.include omits Ath12kWifi.

### Procedure

- Read https://unixnu.com/porting/network and identify the bus, firmware, interrupts, DMA and OS interface.
- Qualify the ath12k transport against this OS profile's ABI, then select the component.
- Verify scanning, association, address configuration and sustained receive and transmit traffic.

### Development findings

- Ath12kWifi is the only Wi-Fi transport in the catalog and its hardware list includes wcn7850, which is the chip on this board, but its declared os\_abi does not match the selected OS profile. Selecting it would claim an ABI match that the catalog does not state.
- PCI configuration, BAR, MSI and DMA operations are board dependencies that this board has not implemented.

### Completion criteria

- Scanning, association, address configuration and sustained receive/transmit traffic pass with the selected firmware.

### Current limits

- No network driver is selected and no ath12k firmware is collected.
- PCIe enumeration and MSI delivery are unimplemented on this board.

### Next action

- Establish the OS ABI that the ath12k transport requires, then either adapt it to ipados-17.7.11-21H461 or record the gap in the component catalog.

### Evidence

Collect evidence using the next action.

## Audio {#audio}

`planned`

### Hardware and dependencies

- SM8650 LPASS: qcom,sm8650-adsp-pas, qcom,gpr, qcom,q6apm, qcom,q6prm with lpass rx, tx, wsa and va macros over soundwire v2.0.0.
- ADSP firmware and its firmware services, loaded through the PAS loader.
- Board audio routes and the codec configuration shipped in the NX769J vendor firmware.

### Configuration

- No audio component is selected. board.toml components.include omits the ADSP and audio IPC drivers.

### Procedure

- Read https://unixnu.com/porting/power and the audio section of https://unixnu.com/porting/drivers.
- Bring up the ADSP with its firmware, establish the GPR/IPC router transport and publish the audio routes.
- Verify each declared route carries the selected audio format through playback or capture.

### Development findings

- The ADSP is reached through the PAS loader and the GPR transport, so audio depends on firmware services and IPC routing before any codec work.
- The audio server keys its routing database and MediaExperience its per-board tables on the board name in the ADT, so the board name must be fixed before audio routes are qualified.

### Completion criteria

- Each declared route carries the selected audio format through playback or capture and handles start/stop correctly.

### Current limits

- ADSP firmware, IPC transport and codec routing are all unimplemented on this board.

### Next action

- Record the ADSP firmware revision and the IPC transport entry points from the vendor firmware before implementing the transport.

### Evidence

Collect evidence using the next action.

## Power {#power}

`planned`

### Hardware and dependencies

- PMIC regulators over SPMI with RPMh \(qcom,rpmh-rsc, qcom,sm8650-rpmhpd, qcom,sm8650-rpmh-clk, qcom,bcm-voter\).
- qcom,aoss-qmp and rpmh-stats for low power state transitions.
- NX769J battery and charging units, and the Awinic AW22xxx haptics driver.

### Configuration

- No power component is selected. board.toml components.include omits the PMGR and power drivers.
- CONFIG\_XNU\_SHENG\_PMGR is not set: the sheng PMGR driver is board specific and SM8650 has no Apple PMGR block.

### Procedure

- Read the power section of https://unixnu.com/porting/drivers.
- Record regulator ownership, clock parents and the firmware ownership boundary, then implement the power manager and battery units.
- Verify declared power controls and battery readings against observations and exercise each claimed sleep and resume transition.

### Development findings

- The SoC exposes RPMh and AOSS rather than an Apple PMGR block. The caihong SM8650 port reports that the AMFI early security init path panics with 'AMFI: No PMGR?' on this SoC family for that reason.
- SM8550 and SM8650 both expose the PMGR patch surface that UniXNU-sm8550-common patches, which is why the shared SoC source is usable here as well.
- AMFI waits 30 s for ApplePMGRNub and panics with "AMFI: No PMGR?". scripts/patch-amfi-no-pmgr.py branches past the lookup with the path the function's own one-time flag uses, on a copy of the kernel.
- Rails and clocks are voted by the drivers that need them: the touch driver votes L14B through the apps RSC, and package/gpu enables the GCC and GPUCC branches and votes the GPU through the GMU. No common power manager owns these votes.
- iOS shows the battery as empty: no battery or charger service exists. Charging in stock Android reformats userdata \(see storage\).
- package/gpu/GpuPower.cpp is the GPU bring-up and power-sequencing driver \(clocks, GMU, GX, DVFS fuse\), separate from the board power-management area; it matches this area's package/\*Power\* pattern only by name.

### Completion criteria

- Declared power controls and battery readings match observations; each claimed sleep/resume transition restores its dependent peripherals.

### Current limits

- Regulator ownership, battery units, charging and sleep transitions are unimplemented.

### Next action

- Read the battery state from the ADSP battery manager and publish it, so iOS stops reporting an empty battery.

### Evidence

Collect evidence using the next action.

## Image assembly {#packaging}

`host-verified`

Components: `XnuPrelink`.

### Hardware and dependencies

- XNU 8796.101.5 at revision aca3beaa3dfbd42498b42c5e5ce20a938e6554e5, the open-source drop closest to Darwin 22.5.0.
- iOS 16.5 restore image for iPhone10,3, build 20F66. Several profile fields are read out of it and are still marked REQUIRED\_IPSW.
- Android 14 boot image format: header version 4, 4096-byte pages, kernel base 0x0, LZ4 ramdisk.

### Configuration

- board.os\_profile = ios-16.5-20F66; the profile is os-profiles/ios-16.5-20F66/profile.toml and must land in UniXNU/profiles/os/ before a build resolves.
- kernel.prelink is inherited from the OS profile: tool kits/XnuPrelink/emit\_prelink.py, slide -0x1000000, and kernelcache\_sha256 and early\_security\_init are REQUIRED\_IPSW.
- kernel.config\_fragments apply arch:configs/common.config, soc:configs/sm8550.config and os:configs/ios.config, then the device defconfig.
- patch\_series resolves arch, soc, os, device in order; the OS series is empty and the device series carries no board patch yet.
- \[bootimg.image\] base = 0x0, pagesize = 4096, header\_version = 4.
- package/unixnu.toml defines the payload menu with a single xnu entry.

### Procedure

- Read https://unixnu.com/xnu/source-and-patches, https://unixnu.com/concepts/prelink and https://unixnu.com/concepts/payload.
- Run python3 scripts/extract-ipsw-pins.py iPhone10,3,iPhone10,6\_16.5\_20F66\_Restore.ipsw to reproduce every pin in the OS profile, including the ADT identity from the board device tree.
- Fill payload.text\_fixups from the OS image dyld cache once native-text-fixup.patch is rebased onto xnu-8796.
- Rebase the arch, soc and XnuPrelink patch series onto xnu-8796 before referencing any of them from the OS series, then build kernel, package, firmware and payload in order.
- After changing boot arguments, rebuild both the payload and the boot image as described in https://unixnu.com/xnu/boot-arguments\#apply-arguments.
- Run python3 scripts/porting-record.py check --device . from the UniXNU checkout before publishing.

### Development findings

- The storage bindings in scripts/prelink-storage-bindings.json are measured from the original kernelcache, while the emitted image moves the prelink closure by the profile slide of -0x1000000. Binding them unslid put IOBlockStorageDevice::gMetaClass in the kernel's own munger\_tests data, and OSMetaClass::postModLoad faulted on superClassLink 0xFEEDBEEF. build-storage-bindings.py now applies collection\_slide from the pin. The AES bindings had the same problem in a worse form: the UniXNU copy of scripts/data/native-aes-original-bindings.S holds iPadOS 17.7.11 addresses, and the IOAESAccelerator constructor call took an undefined instruction exception on zeroed memory. scripts/scan-prelink-aes.py measures them from this kernelcache and the device copy overrides that file.
- AppleImage4 panics during mac\_policy\_initmach without properties iBoot normally publishes. The OS profile now supplies /chosen/mix-n-match-prevention-status and its related u32 properties, /chosen/boot-manifest-hash and /chosen/manifest-properties/BNCH. The two hashes are fixed values because no signed manifest chain exists on this boot.
- XNU 8796 is the iOS 16 kernel. The 8796 train has three open-source drops, 8796.101.5, 8796.121.2 and 8796.141.3; 8796.101.5 is the earliest and the closest to Darwin 22.5.0, so it is the baseline for iOS 16.5. The community iOS 16 ports, dipa-studio/ios-sweet and the ios-topaz family, build the same train.
- osfmk/conf/files.arm64 lists osfmk/arm64/kpc.c as optional kpc nos\_arm\_asm, but the file is not in the xnu-8796 source drop; only kern/kpc\_common.c, kern/kpc\_thread.c and x86\_64/kpc\_x86.c are published. Removing the entry is not enough: cpu.c calls kpc\_idle and kpc\_idle\_exit and kpc\_common.c calls the arch hooks, so the link then fails on eight \_kpc\_\* symbols. xnu-8796-arm64-kpc-backend.patch provides the backend instead, reporting no counters and nothing running, which is what kpc\_common.c asks before it reads anything.
- The iig interface generator is newer than this XNU. It emits rpc.kernelContent, reads it back as IORPCMessage \* and initialises it with the kernel-resident message, while IORPC in xnu-8796 has only message, reply, sendSize and replySize. Adding IORPCMessage \* kernelContent to the struct satisfies the generator; the 8796 dispatch path reads message only and ignores the field.
- The first kernel build reached the XNU compile and stopped on a single cause repeated four times: clang rejects -enable-trivial-auto-var-init-zero-knowing-it-will-be-removed-from-clang, which makedefs/MakeInc.def adds beside -ftrivial-auto-var-init=zero. That companion flag was removed from clang. linux-clang-auto-var-init.patch drops it and keeps -ftrivial-auto-var-init=zero, which is the supported way to get the same zero-initialisation. The patch is last in the series so it cannot collide with the other MakeInc.def edits.
- The second build stopped on uio\_stackbuf\_t, which bsd/sys/uio\_internal.h declares as char aligned to union iovecs and then places in arrays sized by UIO\_SIZEOF. Upstream clang rejects an array whose element size is not a multiple of its alignment; Apple's clang accepts the idiom. linux-clang-uio-stackbuf-align.patch moves the alignment to the array declarations and leaves the typedef as plain char, so sizeof stays 1 and UIO\_SIZEOF still counts bytes. Verified on Ubuntu clang 18.1.3: the element is 1 byte, the buffer keeps its byte count, and the array is 8 byte aligned.
- zzz-boot-progress.patch inserted its boot\_progress\_user\_abort call between two lines of handle\_kernel\_abort's parameter list, which is a syntax error wherever that signature appears. Verifying a fuzzy application by comparing the added and removed lines caught nothing, because the change set was identical and only its placement was wrong. Comparing what changed is not enough; a re-anchored hunk needs its placement checked too. The call now goes at the top of the body, matching the other boot\_progress hooks.
- KALLOC\_TYPE\_IS\_COMPATIBLE\_PTR takes the pointee type with \_\_typeof\_\_\(\*\(ptr\)\). In C++ that is ill formed for a void pointer, which the macro explicitly documents as a wildcard, so any C++ translation unit that frees a void pointer fails. \_\_builtin\_choose\_expr does not help: clang still diagnoses the unselected branch. linux-clang-kalloc-pointee-type.patch derives the pointee type from the pointer type with a template in C++ and keeps the deref in C.
- The kernelcache pin covers the decompressed arm64 slice, not the whole fat image. scripts/unixnu/ipsw.py takes the IMG4 payload, LZFSE-decodes it, then keeps the single 0x0100000c fat slice and hashes that; hashing the fat image gives a different digest and fails the board pin check. scripts/extract-ipsw-pins.py mirrors that pipeline exactly.
- The prelink ABI is version bound and was read out of the 16.5 kernelcache rather than copied: AppleMobileFileIntegrity sits at 0xfffffff004e2b640 here against 0xfffffff005ab4ae0 in the 17.7.11 profile, and com.apple.iokit.IOHIDEventDriver, which the 17.7.11 roots list keeps, does not exist in this kernelcache at all.
- The ADT identity comes from the real board device tree, Firmware/all\_flash/DeviceTree.d22ap.im4p inside the restore image, not from libMobileGestalt and not from another profile. That tree gives product-id fd079b298144a7deb4d7c87fef3eb474d8f0e7eb and corrects three values that would otherwise be inherited from the iPadOS profile: artwork-device-subtype is 2436 rather than 2732, compatible-device-fallback is iPhone9,2 rather than iPhone10,6, and kern.maxvnodes is 10000 rather than 66560.
- The Apple device tree length field carries a flag in its high bit; the real length is the low 31 bits. Reading it unmasked overflows the parser.
- The rebase is complete and verified: all 59 patches apply strictly, in order, onto xnu-8796.101.5. 54 carried over unchanged, one needed the hunk re-anchored for a build-config file whose surrounding comments drifted, and two hunks were dropped because the include line they rewrite does not exist in this train.
- Patch order matters and patches depend on earlier ones creating their target code. zone\_id\_require\_aligned is introduced by offline-pgz-alignment-probe and FREEZE\_ENABLED\_DEFAULT by another patch in the series, so testing a patch in isolation against a clean tree gives the wrong answer. The series was regenerated by replaying it in order.
- pgz-aligned-validation and published-freezer-condition are dropped entirely. Both patch code that no patch in this train creates and that xnu-8796 does not have: zone\_id\_require\_aligned is only referenced inside the XNU\_ZONE\_PGZ\_ALIGNMENT\_PROBE block, which is off by default and has no definition in 8796, and the FREEZE\_ENABLED\_DEFAULT block does not exist here.
- zzx-pmap-sync-64bit-pa patch halves split by target: osfmk/arm64/sptm/pmap/pmap.c does not exist in 8796, so that half is dropped, while its osfmk/arm/pmap/pmap.c half applies and is kept.
- The two prelink patches, security-init and sparse-index, apply to xnu-8796 without modification. XnuPrelink only ships them under xnu-10063 file names, so the copies here are renamed to xnu-8796.101.5-\* to name the train they run on.
- board.toml selects only device:patches/xnu/series. The shared arch, soc and os series still target xnu-10063.141.1; referencing them would abort unixnu status with 'patch missing' or fail during application. Switch back to the four-series form once those are rebased.
- native-text-fixup.patch is among the rebased set, so payload.text\_fixups is the remaining input for that path rather than a separate track.
- The boot image header version is 0, not the 4 that the NX769J board configuration records. BOARD\_BOOTIMG\_HEADER\_VERSION is the Android build system setting for a stock boot.img; unixnu bootimg verify\(\) unpacks ten u32 words from offset 8 and reads header\_version and pagesize at the v0/v1/v2 offsets, so a v4 header fails the round-trip check. The tool defaults use 0. The sibling RedMagic port UniXNU-nx729j hit the same failure, fixed it the same way, and then fastboot-booted the image on hardware. If the NX769J ABL rejects v0 the fix is to extend verify\(\) rather than to set the value here.
- The caihong SM8650 port omits prelink early\_security\_init because running AMFI early security init on a SoC without an Apple PMGR panics with 'AMFI: No PMGR?'. NX769J is the same SoC family, so treat the hook as an open risk and record the observed behaviour rather than assuming it runs.
- The image assembly now runs end to end. build userdata writes userdata-root.img 8357150720 bytes with the OS window from 096-04088-077.dmg at 0x100000 and the SystemOS window from 096-04666-078.dmg at 0x14fa00000; build payload writes payload.img 218103808 bytes carrying the OS trust cache; bootimg packs boot.img 220332032 bytes and round-trips it. The order matters: build userdata before build payload, because scripts/extract-root-volume-uuid.py reads the root volume UUID out of the userdata image. On Linux the image steps need the toolchain bin directory on PATH, since build userdata decodes LZFSE chunks with the lzfse tool that scripts/linux/setup-toolchain.py installs.
- The payload belongs in vendor\_boot, not in boot. The GKI layout leaves boot ramdisk\_size at 0 and the ABL refuses a boot image carrying a large ramdisk, while the vendor\_ramdisk field takes the whole 64 MiB payload.
- A stock vendor\_boot header places the ramdisk at 0x01000000 and the device tree at 0x01f00000, so the ramdisk window is only 15 MiB and a larger payload overwrites the device tree. The address has to be relocated, 0x40000000 here, before the payload grows past that window.
- mformat -F writes a volume the firmware cannot open: a 4 MiB image is laid out as FAT32 with 8030 clusters, the initrd volume publishes no filesystem and payload discovery reports fs 0. mformat -T 8192 -h 64 -s 32 produces a FAT16 volume that mounts.
- The panic screen and a stage-4 entry probe share the zero padding after \_start and do not fit in this kernel build: with a reset probe armed the panic screen needs 0xa1f bytes against the 0x970 left, and patch-xnu-entry-probe.py refuses rather than truncating it, so bisecting needs panic\_screen off.
- scripts/make-ipsw-trust-bundle.py collects the IPSW trust caches into the bundle passed as --owner-trust-cache. The kernel loads them, and launchd and the system binaries pass AMFI with their Apple signatures.
- The GPU user path is staged by the boot payload: scripts/make-nx769j-gpu-addon.py packs NativeAdrenoMetal.bundle \(plugin + Turnip\) and bin/vktest,mtltest into a GPU addon and appends their CDHashes to the owner trust bundle; unixnu build payload --gpu-addon mounts it over /System/Library/Extensions. patches/xnu/nx769j-exec-swap.patch and the Adreno740 patches ride the device series. \[payload\] size\_mib rose to 76 to fit the 12 MiB addon beside the kernel and the Data seed.

### Completion criteria

- Kernel and prelink succeed, payload contains all declared inputs, and the boot image matches the bootloader format and size limit.

### Current limits

- The kernel compiles and links on xnu-8796 with this series: the build reaches 'built kernel at build/xnu/ios-obj/DEVELOPMENT\_ARM64\_BCM2837/mach.development.bcm2837'. Nine of the ten archive builders now pass - corecrypto twice, ArmDTPlatform, ArmCpu, SoftwareAES, the SoftwareAES bindings, the libpthread kernel component, ShengUfs and VirtioMmioBlock - and the missing per-object compile records are supplied by scripts/compile-records.py through the $\(CCACHE\) $\(CC\) hook that MakeInc.def leaves undefined. The Build workflow sets CCACHE so the same records appear on CI. XNU C rules compile without -o and let clang derive the object name, so the record states the output explicitly when the invocation leaves it implicit: build-mockfs-fixture.py and build-libpthread-kernel.py both substitute -o and otherwise write the object somewhere the consumer does not look. build-mockfs-fixture.py is also dropped from \[kernel\] archives, because the kernel only force-loads that archive when MOCKFS\_MODE is 1 and this board leaves CONFIG\_XNU\_SOURCE\_MOCKFS unset. The pinned libpthread is the iOS 17 drop and is one API ahead of xnu-8796 in exactly one place, proc\_get\_jit\_entitled; patches/libpthread/ adapts it and carries UniXNU's explicit-kernel-address.patch unchanged, since a device patches/libpthread directory shadows the upstream one. The kernel now builds and links: all eleven archives pass and mach.development.bcm2837 is produced with no undefined symbols. The three gaps the link first reported were closed without a device. The eleven IOBlockStorageDevice symbols come from scripts/build-storage-bindings.py, which binds the inherited slots to the original prelinked kext code with absolute symbols taken from scripts/prelink-storage-bindings.json -- measured statically out of the iOS 16.5 kernelcache by scripts/scan-prelink-storage.py, whose output records kernelcache\_sha256 e6fa7559... and so proves it read the pinned image. \_boot\_progress\_poll is the weak observer NativeUfs calls only while verifying, and is defined as a no-op. The six verified-root symbols come from scripts/build-verified-root.py, which compiles the real VerifiedRoot crypto rather than stubbing it and generates an empty policy table: verified\_root\_policy\_count is 0, which makes configureVerification return before it reads the key or calls vr\_open, so root verification is disabled rather than approximated. A signed policy bundle is the one input still genuinely missing, and it is policy data, not code. Prelink gets through plan\(\) and through the instruction inventory: the one literal pool that stopped it is known to scripts/emit-prelink-nx769j.py, which re-derives its boundary from the image and refuses to run if the pool no longer sits between a function epilogue and the next prologue. What remains is the early security initializer address -- see next\_action. The inventory was a safety check rather than a transform, and loosening it would let real code be classified as data and drop a genuine external encoding silently. emit\_prelink.py reports instruction\_relocation\_complete, abi\_qualified and loadable as false in every plan it writes, so the artifact it produces is an experimental candidate and not a qualified kernel however these questions are settled.
- payload.text\_fixups is an empty list, and that is the honest state rather than an approval. Entries disable code in a signed file after signature validation -- the worked example ends in c0035fd6, which is \`ret\` -- and each is a specific byte change in the dyld shared cache inside 096-04088-077.dmg, chosen to bypass whatever turns out to be in the way. None has been determined for this port. They are not derivable mechanically, and an empty list means none needed yet rather than none will be.
- The four inputs that only a device held are all collected now. The 52 vendor UEFI DXE drivers and the firmware DTB come out of the device flash package with scripts/extract-uefi-drivers.py and scripts/extract-firmware-dtb.py, and both are pinned by hash in proprietary-files.txt; the unique chip id is recorded in device-inputs.md and passed as --unique-chip-id; the root volume UUID comes out of the built userdata image with scripts/extract-root-volume-uuid.py. What assembling the images still needs is a local restore image and a local trust cache, neither of which is redistributable. The payload and the boot image now build: payload.img 218103808 bytes carrying the OS trust cache df0f60fd..., and boot.img 220344320 bytes with the FD and DTB that boot.json records. The payload and boot image are not byte-reproducible: the ADT carries a 64-byte random seed and the FD it packs is not either -- see docs/HOST-VERIFY.md.
- The Data seed is in the payload: gh run download fetches the nx769j-data-seed artifact and build payload takes it as --data-ramdisk. Each run formats a new volume, so the Data volume UUID changes with it and nothing pins one. The kernel refuses a seed whose store window does not fit the partition, so the container size has to follow the userdata geometry rather than be chosen freely.
- The rebased copies are duplicated here rather than in the owning ARM64, SoC and component repositories, which this repository does not control. They should move back once those series are rebased.
- The restore image is not redistributable, so ipsw.url carries the member name and the build takes a local copy through --ipsw or UNIXNU\_IPSW.

### Next action

- Measure the AppleMobileFileIntegrity early security initializer and set kernel.prelink.early\_security\_init to it. The contract is in patches/xnu/xnu-8796.101.5-security-init.patch: OSKext::start reads an \_NativePrelinkEarlySecurityInit OSNumber from the kext, adds vm\_kernel\_slide, checks the result is 4-aligned and inside a read-execute non-writable segment of that module, and calls it as void\(void\) before MAC policy lockdown. So the value is an unslid function address inside the module's \_\_TEXT\_EXEC, which for this kernelcache is 0xfffffff0056fe000..0xfffffff00571b764. Identifying which function is a reversing task on a stripped kext, not a field lookup -- the \_\_PRELINK\_INFO dictionary only names the kmod stub. Until it is measured the field stays unset and emit\_prelink skips the path; AMFI still starts through its ordinary start routine, but the pre-lockdown call does not happen. Separately, produce the owner-signed verified-root policy bundle over the root windows of the OS image that gets flashed and replace the generated empty table in scripts/build-verified-root.py with it, so root verification is enabled rather than disabled.
- Set the Data volume UUID the seed run reports in whichever configuration the block driver reads it from, and set the ARTIFACT\_PASSPHRASE secret so the seed is uploaded encrypted rather than holding restore-image files in the clear.
- Derive a payload.text\_fixup when a boot gets far enough to fail on one; there is nothing to derive before that.
- Upstream the rebased series to the ARM64, SoC and XnuPrelink repositories and restore the four-series patch\_series form.

### Evidence

- `source`: [Payload menu and boot entry definition for the assembled image](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/package/unixnu.toml)
- `source`: [iOS 16.5 XNU pins, Darwin version, IPSW identity, prelink ABI inputs and the ADT identity, with each field sourced in a comment](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/os-profiles/ios-16.5-20F66/profile.toml)
- `source`: [The complete rebased patch order, verified to apply strictly in sequence onto xnu-8796.101.5](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/patches/xnu/series)
- `source`: [Per-patch applicability against xnu-8796.101.5, the dropped hunks and their reasons, and the reproduce commands](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/os-profiles/ios-16.5-20F66/patch-rebase.md)
- `source`: [Reproducible extraction of chip\_id, board\_id, member hashes, kernelcache\_sha256 and the kext inventory and the ADT identity from the restore image](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/scripts/extract-ipsw-pins.py)
- `source`: [Stops libpthread advertising PTHREAD\_FEATURE\_JIT\_ENTITLED, whose proc\_get\_jit\_entitled callback xnu-8796 does not have; the other 59 of the 60 callbacks the pinned libpthread uses resolve against that kernel](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/patches/libpthread/xnu-8796-no-jit-entitlement.patch)
- `source`: [Why the device carries a patches/libpthread directory at all: module resolution is first-wins and it shadows UniXNU's, so explicit-kernel-address.patch is carried byte for byte rather than lost](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/patches/libpthread/README.md)
- `source`: [Measures the original IOBlockStorageDevice dispatch table out of the iOS 16.5 kernelcache: the vtable and its 190 slots, the metaclass, the protected constructor and the base destructor. No hardware, no live snapshot - every value is read from the image](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/scripts/scan-prelink-storage.py)
- `source`: [The measured pin, recording kernelcache\_sha256 e6fa75598f47b5a9460a60913e2ac8e4cd6cd60eb475bb31da65b68ffbcfdad5, which matches the kernelcache\_sha256 this repository already pins in the OS profile](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/scripts/prelink-storage-bindings.json)
- `source`: [The measured board inputs and, now, a cross-check of the splash reservation against the public firmware dump's DTBO overlay -- which agrees exactly and adds disp\_rdump\_region at 0xe3940000 for 0x800000](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/device-inputs.md)
- `source`: [payload.text\_fixups is an empty list rather than a placeholder: the entries disable code in a signed file and are discovered per problem, so there is nothing to derive before a boot reaches one](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/os-profiles/ios-16.5-20F66/profile.toml)
- `source`: [Runs emit\_prelink.py with this kernelcache's com.apple.kec.Libm coefficient table known, re-deriving the pool boundary from the image and refusing to run unless it still sits between a function epilogue and the next prologue](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/scripts/emit-prelink-nx769j.py)
- `source`: [Builds the real VerifiedRoot crypto together with a generated policy table that truthfully reports no signed bundle, so the UFS driver runs with root verification disabled rather than approximated](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/scripts/build-verified-root.py)
- `source`: [The prelink input is mach.development.bcm2837.unstripped, not the .unstripped.noctf that xnu-10063 names: xnu-8796 links no such output and its raw kernel carries no CTF to strip. early\_security\_init is left unset because the only address scripts/extract-ipsw-pins.py could derive, the kmod stub, is not the function the hook calls](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/os-profiles/ios-16.5-20F66/profile.toml)
- `source`: [Records each XNU compile as &lt;object&gt;.json and now states the output explicitly when the invocation leaves it implicit, which is what build-mockfs-fixture.py and build-libpthread-kernel.py need in order to substitute -o](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/scripts/compile-records.py)
- `source`: [Builds the writable Data seed for --data-ramdisk from the iOS 16.5 OS volume on macOS: an APFS OwnerData volume at the size asked for, holding the volume's initial /private/var without staged\_system\_apps, packed with DarwinBoot's DBRDISK1 writer so only the non-zero pages travel. UniXNU's own prepare-owner-data-fixture.py and seed-data-grow.py cannot do it: the first rejects any OS mount whose sbin/launchd does not hash to the iPadOS 17.7.11 image and the second grows a packed seed this port does not have. .github/workflows/data-seed.yml runs it on a hosted macOS runner and reports the new volume UUID. Several runs failed before it produced anything, and job logs need repository access, so each was diagnosed from the run page annotations instead: a cache key holding a comma, tee masking the exit code, a 32 MiB container grown rather than created at size, a missing DarwinBoot submodule, Path.symlink where the method is symlink\_to, and a log redirect into a directory that did not exist yet. scripts/test\_build\_data\_seed.py covers the copy, the tree measurement, the mount checks and the container check, which is everything that runs without hdiutil](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/scripts/build-data-seed.py)
- `host`: [Run 41026291337 on macos-26 built nx769j-data-seed, 567485 bytes, sha256 589fb90de70a9d5b5e367464a66674c659c7bd32ee93ced445ead9f2f77136bd, holding a 256 MiB APFS OwnerData container with the iOS 16.5 OS volume initial /private/var and Data volume UUID DA9A01BC-22A9-47B0-8EA0-27B3C35E37E4. It is uploaded unencrypted because ARTIFACT\_PASSPHRASE is not set, and downloading an artifact needs a token even for a public repository. gh run download fetched it as nx769j-data.dbr, 970848 bytes, sha256 e13f93e046ad2d60e8d3be706577be2d207df0c303b52682a2b54b6ad18da2bc holding 36 files and 589907 bytes of the OS volume initial /private/var, and build payload --data-ramdisk put it in the payload as scratch-data.img behind initrd = Payloads/scratch-data.img; the seeded payload.img is 8f5d75ff... and boot.img 834403f3... at 220344320 bytes. gh repo edit --add-topic unixnu published the repository to the device list](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/docs/HOST-VERIFY.md)
  Command: <code>./unixnu build payload -D ../UniXNU-NX769J --data-ramdisk nx769j-data.dbr --unique-chip-id 8abc5430 --uefi ../uefi-nx769j --ipsw &lt;restore.ipsw&gt; --trust-cache &lt;096-04088-077.dmg.trustcache&gt;</code>. Revision: `ed45ee86452bc50735625fcf124fa2911d364ef9`.
- `host`: [2026-10-30: all three image steps ran in order. userdata-root.img 8357150720 bytes sha256 818e4e37bc9061ac8f5a2103234adb1c1b945fa1f2f4255ac148731b9ebf2631 holds the OS window at 0x100000 and the SystemOS window at 0x14fa00000; payload.img 218103808 bytes sha256 a01c88e13681ff83ba3059c9bf0da00a4cdcceac041af24e28898d753ae1e6f9 carries kernel.macho 2458882f... and the OS trust cache df0f60fd..., and its menu lists xnu, reset, shutdown and tools; boot.img 220344320 bytes sha256 1b1f22c2513e16ec50463345daa45b2cf8244881d0841b174cdc4b1d6ea38a4a packs FD b0690638... and DTB f336a7d7... under an ANDROID\! v0 header at 4096-byte pages. bootimg round-trips the image and failed no check. The kernel itself stays an experimental candidate: emit\_prelink.py still records instruction\_relocation\_complete, abi\_qualified, loadable and runtime\_qualified as false.](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/docs/HOST-VERIFY.md)
  Command: <code>./unixnu build userdata -D ../UniXNU-NX769J --ipsw &lt;restore.ipsw&gt; &amp;&amp; ./unixnu build payload -D ../UniXNU-NX769J --unique-chip-id 8abc5430 --uefi ../uefi-nx769j --ipsw &lt;restore.ipsw&gt; --trust-cache &lt;096-04088-077.dmg.trustcache&gt; &amp;&amp; ./unixnu bootimg -D ../UniXNU-NX769J --uefi ../uefi-nx769j --dtb ../uefi-nx769j/Resources/DTBs/nx769j.dtb -o out/nx769j/ios-16.5-20F66/nx769j/boot/boot.img</code>. Revision: `dd97bc4b307f77df2f6189b7c92881133cc24ac3`.
- `device`: [The 64 MiB payload packed into vendor\_boot at ramdisk address 0x40000000 is opened as a FAT volume and yields fs 1, while the same payload as a boot ramdisk never reaches the menu and a 4 MiB payload built with mformat -F publishes no filesystem at all. Repacking the stock ramdisk reproduces the stock vendor\_boot byte for byte.](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/docs/DEVICE-EVIDENCE.md)
  Command: <code>python3 scripts/unixnu/vendor_boot.py --stock vendor_boot_a_stock.img --ramdisk payload.img --ramdisk-addr 0x40000000 --verify-against</code>. Revision: `2a265afdbd95d45e4a90664157e793c3bfee3755`.

## Diagnostics {#diagnostics}

`device-verified`

### Hardware and dependencies

- Firmware log exporter and QR log export from https://unixnu.com/porting/log-capture\#firmware-setup.
- Serial console over kernel argument serial=3.
- The NX769J device firmware revisions: baseband 5.0.c3-00030-LANAI\_GEN\_PACK-1.46586.20 and trustzone TZ.XF.5.0-07512.2-LANAIAAAAANAZT-1.46586.1.

### Configuration

- kernel\_args are '-v serial=3'; payload.panic\_screen = true and payload.timeout = 3.
- scripts/collect-device-inputs.sh gathers the board inputs that no public source provides.

### Procedure

- Read https://unixnu.com/porting/log-capture and https://unixnu.com/porting/bring-up.
- Set up QR log export during firmware integration and save the firmware log before the kernel handoff.
- Record each command, revision, output and result, and assign each area its completion level from https://unixnu.com/porting/records\#completion-levels.

### Development findings

- Each claimed milestone needs a reproducible command, a matching source and image revision, and an accessible result. Store large logs as linked release or CI artifacts.
- The firmware revisions identify a verification result on this device, so they belong in every device evidence entry once one exists.
- device-inputs.md records the board inputs measured over read-only adb, with the command behind each value. The handset reports a spoofed Xiaomi identity through its userspace properties while its boot image, kernel and device tree identify NX769J, so identity and hardware values were read from getprop of the bootimage properties, the kernel, the device tree and the raw UFS partition table rather than from the spoofed product properties.
- scripts/collect-device-inputs.sh is the same collection procedure in runnable form and remains the way to re-measure before writing to a device.
- The merged kernel configuration can carry either the CONFIG\_XNU\_ name from the defconfig syntax or the bare XNU\_ name the kernel build consumes, and a false value can appear as n, 0 or '\# NAME is not set'. scripts/check-merged-config.py accepts all of those forms so the check reports a real value mismatch instead of a format difference.
- The entry-probe bars are the only progress signal and they read downwards from the hand-off: green is DarwinBoot painting the top sixteenth before the branch, blue is stage 1 at the kernel entry with the MMU off, magenta is stage 2 just before the MMU is enabled. A screen holding green, blue and magenta means the kernel reached the MMU switch and stopped after it, which is a different fault from a kernel that never ran.
- There is no accessible serial console. kernel\_args carried serial=3, which selects the Apple SoC UART, and dropping it changes nothing: the same three bars and the same stall. The serial input this area lists is therefore not available and the argument should not be assumed to reach a log.
- A loader that fails after painting its own diagnostics has them overwritten when the menu redraws, so holding the screen for 20 to 25 seconds on the failure path is what makes NO WINDOW and the hand-off summary photographable.
- Because XNU replaces VBAR\_EL1 early, an exception during a hand-off is only reported by installing a vector table before the branch: painting the top band red and encoding ESR, ELR and FAR as 64-bit bar codes leaves a readable record without a console. The absence of a red band is what rules out an early fault and points at a spin.
- Without a serial console the boot is reported on the panel. scripts/add-progress-strips.py maps the framebuffer in the V=P bootstrap table and paints a strip at each checkpoint until the console exists; exceptions, panic\(\) and Assert\(\) draw their registers and callers as bar codes. Call sites are located by symbol, so a driver rebuild does not move them.
- With -v and debug=0x8 the kernel prints to the text console. A 15 s heartbeat repeats the board status lines \(CPU, touch, governor, GPU\), and exec, exit, user brk and launchd samples identify userland failures.
- The GPU bring-up carries its own on-panel diagnostics: package/gpu execReport prints RBBM\_STATUS, the CP read/write pointers, CP\_INTERRUPT\_STATUS, the offending opcode and a ring dump each heartbeat, patches/drivers/Adreno740/nx769j-submit-trace logs every client submission, and nx769j-quiet=1 drops the already-verified CPU/touch/governor lines so the GPU lines stay on screen.

### Completion criteria

- Each claimed milestone has a reproducible command, a matching source/image revision and an accessible result.

### Current limits

- The firmware log is not exported. Logs are photographs of the panel, and the Data window is read back over EDL.

### Next action

- Export the kernel log to a persistent region readable over EDL so runs need no photographs.

### Evidence

- `source`: [Measured identity, partition geometry, reserved memory, DRAM, register map, display and input facts with the read-only commands that produced them](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/device-inputs.md)
- `source`: [Preflight for the uefi-nx769j platform package, jointly owned with the firmware area because it matches the scripts/check-\* pattern as well as the firmware pattern: it checks the Mu-Silicium layout, board.toml agreement, the SM8650 SoC package include and the vendor DXE inventory. The vendor set is read from the platform's three includes rather than held in step with them, and both checkouts are found from the assembled tree the preflight runs in](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/scripts/check-nx769j-firmware.py)
- `source`: [A gate on the UEFI memory map, jointly owned with the memory area because it matches scripts/check-\* as well as scripts/\*memory\*. A wrong map lets the firmware write over what the bootloader or TrustZone owns and the failure is a corrupted boot rather than a build error, so the table is compared with the device tree instead of being reviewed](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/scripts/check-memory-map.py)
- `device`: [The framebuffer is the only output: the hand-off summary drawn by the loader, the conventional-memory counts and the probe bars were read from photographs of the panel. The runs so far show green, blue and magenta with no red band and no panic screen, which places the kernel past its MMU switch and rules out an early exception.](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/docs/DEVICE-EVIDENCE.md)
  Command: <code>fastboot flash vendor_boot_a vendor_boot_a.img; fastboot reboot, then photograph the panel</code>. Revision: `2a265afdbd95d45e4a90664157e793c3bfee3755`.
- `device`: [The strips locate the stall and the fault report gives PC, FAR 0xfeedbeff, ESR 0x96000005 and the class NativeUfsBlock \(rows strips to strips4\).](https://github.com/xwsjjctz/UniXNU-NX769J/blob/841a86ace1caa36c0528fbf6133df36acc41b516/docs/DEVICE-EVIDENCE.md)
  Command: <code>EDL (9008) write of the run's vendor_boot image to vendor_boot_a (LUN 4, start sector 281670, 24576 sectors); boot arguments as the strips rows of docs/DEVICE-EVIDENCE.md state</code>. Revision: `06e930b8261ece662e4950ee983459d618d8cf33`.

</div>
