# OnePlus 6 \(A6003\), 8 GB RAM / 128 GB storage, arm64 only \(no FEAT\_PAuth\) \(dragon120820\)

[dragon120820/UniXNU-enchilada](https://github.com/dragon120820/UniXNU-enchilada)

<div v-pre>

OnePlus 6 \(A6003\) / SDM845 / Cortex-A75+A55, arm64 only \(no FEAT\_PAuth\). Skeleton record: every area is planned; inputs below are measured facts, not verified implementation.

Source record: [porting.toml](https://github.com/dragon120820/UniXNU-enchilada/blob/c8404873d590fbbe43d81ed7c181d5142550a63c/porting.toml), `c8404873d590fbbe43d81ed7c181d5142550a63c`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `planned` |
| [Firmware and boot](#firmware) | `device-verified` |
| [CPU and interrupts](#cpu) | `planned` |
| [Memory and DMA](#memory) | `planned` |
| [Storage and root](#storage) | `planned` |
| [Display](#display) | `planned` |
| [Input](#input) | `planned` |
| [GPU](#gpu) | `planned` |
| [Network](#network) | `planned` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `planned` |
| [Image assembly](#packaging) | `planned` |
| [Diagnostics](#diagnostics) | `planned` |

## Configuration {#configuration}

`planned`

Components: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`, `DarwinBoot`.

### Hardware and dependencies

- SoC: SDM845 \(Qualcomm codename Napali\) \[MU\]. No upstream UniXNU-sdm845-common exists; this SoC layer must be created \[DOC\].
- CPU: 4x Cortex-A75 \(part 0x803, rev 12\) + 4x Cortex-A55 \(part 0x802, rev 13\); MIDR\_EL1\(cpu0\) = 0x00000000517f803c \[LOCAL\].
- CPU features: fp asimd evtstrm aes pmull sha1 sha2 crc32 atomics fphp asimdhp. No sha3/sha512/dcpop/sve, no FEAT\_PAuth -&gt; arm64 profile only \[LOCAL\].
- OS profile: ipados-17.7.11-21H461, kernelcache\_sha256 f18b4df865405f2a287b84977d7aca745e056d656d9fc9df1662970ce2969de7, slide -0x1000000 \[DOC\].
- SKU: 8 GB RAM / 128 GB storage -&gt; dram\_size 0x200000000; do NOT inherit the 6 GB 0x180000000 value from bringup \[LOCAL\]\[PORT\].
- DTS: dts/enchilada.dts does not exist in any candidate repository; it must be authored. Required ADT roots: /cpus /arm-io /defaults /options \[DOC\].

### Configuration

- Pin the SDM845 SoC commit and record every board.toml override; no REQUIRED\_ placeholder may remain before build.

### Procedure

- Fill board.toml \[board\] \[components\] \[kernel\] \[kernel.prelink\] \[firmware\] \[bootimg\] \[payload\] \[payload.adt\] from the inputs above, then run scripts/package.sh --check --os ipados-17.7.11-21H461.

### Development findings

- Upstream registers all three enchilada repositories as format 1 legacy, so a format 2 device repository must be created rather than migrated in place.
- Format 2 key names differ from the skeleton draft: \[device\_tree\] takes source/include\_dirs \(not path\), \[kernel\] patch\_series is a list of series files \(a bare string is iterated character by character by scripts/unixnu/patches.py:12\), and \[package\] unixnu plus \[package.defconfig\] are required by templates/package.sh and scripts/unixnu/config.py:154-159 \[DOC\]
- A board.toml that restates \[kernel.prelink\] roots or kernel replaces the 31 roots and the kernel path the OS profile supplies, because profiles.load\(\) merges dicts per key; the skeleton therefore sets only slide and early\_security\_init \[DOC\]
- board.toml must carry schema\_version = 2: scripts/unixnu/config.py:127 defaults to 1 and then loads a legacy board, which silently skips the whole device-tree and payload path \[DOC\]
- The package workflow under .github/ runs the device repository on a GitHub macOS runner because no local host has Xcode or compression\_tool: the check mode passed in 1m42s and the check-deps mode passed after downloading the 4.7 GiB IPSW and decompressing its kernelcache \[HOST\]
- The kernel mode needs the workflow token, not just a macOS host: scripts/prepare-xnu-source.py restores 26 DriverKit headers through the anonymous GitHub contents API, which returned HTTP 403 rate limit exceeded on the fourth run, so the preflight step now exports GITHUB\_TOKEN \[HOST\]
- profiles.load\(\) merges dicts per key but replaces ordinary arrays, so board.toml must repeat the complete arch, SoC, OS and device lists: a two-entry patch\_series dropped all 56 arm64 patches and 3 IPSW patches, and a one-entry config\_fragments dropped arch:configs/common.config. The first kernel run failed on make\_symbol\_aliasing.sh looking for availability.pl inside the Xcode SDK, which patches/xnu/local-availability.patch exists to fix; the check now reports 60 patches instead of 0 \[DOC\]
- kernel.archives has the same replace-not-append rule and archive\_plan\(\) also rejects a selected component that no component: entry names: selecting RamBlock without adding it to archives failed the second kernel run with \[kernel\] archives needs component entries for: RamBlock, so board.toml now repeats the eight arch entries and appends component:RamBlock \[SRC\]
- The firmware stage does not need the 41 proprietary inputs published anywhere: Mu-Silicium and its Device-Binaries submodule are public repositories, and Device-Binaries HEAD equals the pinned 9f4dbfd7, so a CI job can clone exactly what upstream already serves. The workflow therefore gained a firmware mode that checks out Project-Silicium/Mu-Silicium at 8471e47f, applies the UniXNU payload patch in the checkout only, and runs unixnu build firmware \[HOST\]
- The firmware FD is not uploaded \(the workflow publishes logs only\), so the firmware step prints sha256sum of SILICIUM\_UEFI.fd; without that the build has no recordable identity \[HOST\]
- mode=bootimg packs the built FD with BootShim, the device DTB and mkbootimg into boot.img, uploads it as an artifact \(with boot.json recording image\_sha256, fd\_sha256, dtb\_sha256\), and never touches a device; the device-side fastboot boot remains a separately authorised step \[HOST\]; the B7 pin repair now runs in every build mode \(bootimg needs it too\) \[HOST\]
- SUPERSEDED \(2026-11-07 14:16\): an earlier patch dropped the ARM64 kernel header from the boot shim; that direction was wrong. The ABL inflates the gzip kernel package and requires an ARM64 Image header, so a headerless shim dead-loops in fastboot. Now fixed by mu-silicium-bootshim-image-header.patch: BootShim.S Image Size = FD\_SIZE + \(\_Payload - \_Head\), keeping requires\_kernel\_header = true; header\_version aligned to 1; community one-byte placeholder ramdisk added. Root cause and sources: evidence/device/20261107\_bootimg/root\_cause\_pivot.md \[HOST\]
- mode=bootimg first success \(run 42342820777, commit 3bc0509\): boot.img 1196032 bytes sha256 6b68183c..., fd\_sha256 53893e2f..., dtb\_sha256 0371d596... \(byte-identical to the local dtc build\), ramdisk\_bytes 0, header\_version 0, hardware\_tested false \[HOST\]
- A git -C DIR apply patch resolves the patch name inside DIR, so the firmware step must hand it an absolute path: the first firmware run died with cant open patch device/firmware/mu-silicium-unixnu-integration.patch after sha256sum had already hashed that same relative path from the workspace root \[HOST\]
- The firmware FDT is not the format 2 device tree: a control experiment booted the community edk2-msm 2301.1 boot-enchilada.img to a UEFI Shell on the same ABL, which proves fastboot boot, the gzip kernel shape, the trailing DTB and the v1 header all work, so the remaining difference is our FD. Mu ships Resources/DTBs/enchilada.dtb at 555398 bytes \(the same size the community image appends\), while dts/enchilada.dtb is a 2697-byte working draft that starves SEC/PlatformPei of the DRAM map and reserved-memory nodes; the bootimg step now passes Mu's tree as the firmware FDT and keeps ours for the UniXNU ADT \[HOST\]
- UNIXNU\_PAYLOAD = "1" reaches the DSC through \[firmware.defines\], because firmware.py:38-39 forwards that table as build -D KEY=VALUE and a command-line -D overrides the DSC default; the workflow asserts board.toml carries the key so a firmware built without the payload cannot pass silently \[SRC\]
- The firmware and bootimg steps now pass --target RELEASE to unixnu build firmware: unixnu --target defaults to DEBUG \(cli.py:46\), and the DEBUG DXE ran out of page pool on the device after APRIORI index 31, so 14 drivers failed LoadImage with Out of Resources and the six architectural protocols never appeared. Both steps keep RELEASE so a boot.img is always packed from a firmware that can actually dispatch \[HOST\]
- The stock Silicium SEC discards the x0 the previous stage enters with and never builds gSiliciumEntryArgHobGuid, so UniXNURamDiskDxe \(UniXNURamDiskDxe.c:215\) finds no HOB, prints "UNIXNURAMDISK: no entry argument HOB" and returns without publishing the payload volume: the menu keeps showing the built-in configuration and reports no boot entry found even when a payload ramdisk is present. A probe boot with a 2 MiB FAT12 volume carrying EFI/UniXNU/unixnu.toml with a RAMDISK PROBE entry still drew the built-in menu, which rules out ramdisk size and load address and points at the missing handoff. The same fault is recorded for marble in docs/devices/marble-milacy.md; the fix follows hanzi123-bilp/uefi-fuxi \(ModuleEntryPoint.S stores x0, Sec.c reserves the tree with BuildMemoryAllocationHob because DXE otherwise maps an image over it, then publishes the GUID HOB after PlatformPeim\) \[HOST\]

### Completion criteria

- All source pins resolve; every selected component has a record; status shows the intended overrides and patch order.

### Current limits

- Blocked on a Linux or macOS build host \(Windows native builds are unsupported\) and on git for pinning.

### Next action

- Decide between the official format 2 route \(build the SDM845 SoC layer\) and the community format 1 baseline plus minimal completion.

### Evidence

Collect evidence using the next action.

## Firmware and boot {#firmware}

`device-verified`

### Hardware and dependencies

- Candidate: Project-Silicium/Mu-Silicium commit 8471e47f5248ebbffc2e6196b683204163efe155; platform package Platforms/OnePlus/enchiladaPkg \(10 files\) \[MU\].
- DSC: PLATFORM\_GUID F8A6C376-C5D3-4F61-B911-CE778BCB5DEB, USE\_CUSTOM\_DISPLAY\_DRIVER=1, includes NapaliPkg/NapaliPkg.dsc.inc \[MU\].
- Memory: PcdSystemMemoryBase 0x80000000; PcdCPUCoresStackBase 0x9FF90000; primary stack 0x40000; FD 0x9FC00000 + 0x300000 \[MU\].
- Display PCD: 1080x2280x32; SMBIOS OnePlus/6/enchilada/A6003/17819 \[MU\].
- Enchilada builds ACPI, not DTB: enchilada.fdf includes INF RuleOverride = ACPITABLE enchilada/AcpiTables.inf, and the DtPlatformDxe plus FdtBlob lines are commented out \[MU\].
- Required Mu patches: Auth-Service.patch, Boot-Manager.patch, Timer.patch, Usb-Bus.patch. AsmMacroLib.patch must NOT be applied \(it reverts an MdePkg fix\) \[PORT\].
- RAW.inc references Binaries/enchilada/RawFiles/&\#123;SecParti.cfg,QcomChargerCfg.cfg,BATTERY.PROVISION&\#125;; the Binaries submodule is not present locally \[MU\].
- Mu ConfigurationMapLib.c sets ImageFVFlashed = 0x0 and its consumer is not in the source tree; neither Mu nor edk2 uses the ImageFv partition \[MU\].

### Configuration

- Record the firmware defines: DEVICE\_MODEL=enchilada, ENABLE\_SECUREBOOT=0, MEMORY\_PROTECTION=TRUE, SHIP\_MODE=FALSE.

### Procedure

- Build via DeviceBuild.py on a host with git \(build\_uefi.py runs submodule update plus four git apply steps\).

### Development findings

- Neither UEFI candidate contains any UniXNU, DarwinBoot or initrd integration; that work is entirely ours to add.
- The integration gap is four INF plus one library mapping, not a rewrite: enchilada.dsc \[Components\] appends only enchilada/AcpiTables.inf while SiliciumPkg.dsc.inc:379 already supplies SEC, the DXE core and the runtime services, and same-named sections merge under EDK II semantics \[MU\]
- FdtLib and HobLib need no board-level mapping: enchilada.dsc:28 includes NapaliPkg.dsc.inc, which includes QcomPkg.dsc.inc, which includes SiliciumPkg.dsc.inc, where :322 maps FdtLib and :184 maps HobLib. Only UniXNULib is absent from the whole Mu-Silicium tree \[MU\]
- Include/DXE.inc:42-45 already lists DiskIoDxe, PartitionDxe, Fat and EnglishDxe unconditionally, so only the four UniXNU INF are missing from the FV, and APRIORI.inc needs no change because UniXNURamDiskDxe declares \[Depex\] TRUE \[MU\]
- PcdDxe self-deadlock: PcdDxe links DxePcdLib whose depex is gEfiPcdProtocolGuid; BaseTools merges library depex into module depex \(FfsInfStatement.py:132-163, ModuleAutoGen.py:559-602\), so the as-built PcdDxe depex is PUSH gEfiPcdProtocolGuid END and the driver never dispatches. 29 PCD-dependent drivers then starve \(VariableRuntimeDxe, RealTimeClock, ResetSystem, Metronome, CapsuleRuntimeDxe, UniXNUDxe\), all architectural protocols go missing and DxeCore asserts at DxeMain.c\(581\). Observed on-device 2026-11-07: six 'Arch Protocol not present' lines and four 'discovered but not loaded' drivers \[HOST\]
- CORRECTION 2026-11-07: the PcdDxe self-deadlock was real and is fixed \(as-built depex is now TRUE END, re-checked in the FV; the probe reports LocateProtocol\(gEfiPcdProtocol\)=Success iface=9B763350\), but it was not what starved the runtime drivers. A DXE dispatcher probe records LoadImage failures = 14, every one of them Out of Resources, for VariableRuntimeDxe, EmbeddedMonotonicCounter, ResetSystemRuntimeDxe, RealTimeClock, CapsuleRuntimeDxe and nine more. Cause: the workflow built the DEBUG target \(cli.py --target defaults to DEBUG, firmware.py:23 target='DEBUG'\), whose PE images are several times larger than RELEASE, so the DXE page pool ran out after APRIORI index 31 and the six architectural protocols never appeared, which is what DxeCore reports at DxeMain.c\(581\). The community image boot-enchilada-2301.1 is a RELEASE build and starts for exactly that reason. Fix: build with --target RELEASE \[HOST\]
- Fix: mu-silicium-pcddxe-depex.patch overrides PcdLib with BasePcdLibNull for MdeModulePkg/Universal/PCD/Dxe/Pcd.inf in enchilada.dsc, the same override upstream OvmfPkgX64.dsc carries for the same module; applied on both firmware and bootimg CI runs \[MU\]
- The depex override alone did not fix the device: the fifth boot \(2026-11-07 16:03, image sha256 0634f37d\) reached the DXE self-check with the same six missing arch protocols, and the disassembly of that image shows PcdDxe's as-built depEX is now 'TRUE END' while VariableRuntimeDxe/MonotonicCounter/ResetSystem/RTC/Capsule still wait on gEfiPcdProtocolGuid. The community boot-enchilada-2301.1 image carries byte-identical depEX for the same six drivers and does boot, so the difference is not the depEX: either PcdDxe's entry point never completes or the PCD database section cannot be read at runtime \[HOST\]
- Diagnostic: mu-edk2-pcddxe-probe.patch adds four DEBUG prints on PcdDxe's entry path and in PcdDatabaseLoaderLoad's GetSectionFromFfs call, so the next serial capture says which of the two fails. It is wired through Resources/MuPatches/ and \[firmware\] patches and removed once answered \[MU\]
- UniXNURamDiskDxe published no payload volume because the SEC never handed over the device tree. grep -rni daee82e6 over Mu-Silicium returns nothing: Sec.c never calls BuildGuidDataHob, ModuleEntryPoint.S discards the x0 a Linux-style boot loader uses for the flattened device tree, and UniXNURamDiskDxe returns EFI\_SUCCESS with no volume when GetFirstGuidHob misses, so the menu falls back to the built-in configuration \[MU\]
- SEC entry-argument fix, first attempt, crashed the device: firmware/mu-silicium-sec-entryarg.patch v1 stored x0 as the very first instruction of \_ModuleEntryPoint, before PlatformAssemblyInitialize installs the exception vectors and before MainEntryPoint sets SP, and Sec.c read the tree header and reserved it with BuildMemoryAllocationHob before ProcessLibraryConstructorList ran. On 2026-11-07 23:32 the image carrying it \(sha256 b72ee9bd\) went from Booting OKAY to no USB enumeration at all, and the phone reset into the Android boot screen with no UEFI output; the same build without the patch \(sha256 58cf21ae has it, bootimg9 does not\) still reaches the menu. Isolated by flashing out/bootimg10/boot/boot.img, which has the patch and a one-byte ramdisk, and losing USB, against the earlier menu run \[HOST\]
- SEC entry-argument fix, second attempt: the patch now moves x0 into the callee-saved x19 at entry, writes it to gSecEntryArg0 only inside MainEntryPoint after the stack is live, and in Sec.c does a single BuildGuidDataHob after ProcessLibraryConstructorList, reading no memory and reserving nothing, so a junk value is rejected by the driver instead of killing the firmware. SiliciumPkg.dec and Sec.inf declare gSiliciumEntryArgHobGuid; the integration, PcdDxe and SEC patches apply cleanly in that order on 8471e47f \[MU\]

### Completion criteria

- Firmware image builds, enters UniXNU, publishes the framebuffer and preserves the documented memory reservations.

### Current limits

- Blocked on git \(build\_uefi.py requires it\) and on a non-Windows host for edk2; bootloader lock state also unknown.

### Next action

- Package the built firmware into a boot image \(the package and bootimg stages are still unimplemented\), then boot it once on the device; that last step needs its own authorisation.

### Evidence

- `host`: [2026-11-07: run 42380779873 succeeded, SILICIUM\_UEFI.fd sha256 5bd55aa8..., packed into a 1,626,112 byte boot.img](https://github.com/dragon120820/UniXNU-enchilada/blob/c8404873d590fbbe43d81ed7c181d5142550a63c/firmware/mu-silicium-unixnu-integration.patch)
  Command: <code>python3 ./unixnu build firmware --device ../device --os 17 --uefi ../Mu-Silicium --target RELEASE</code>. Revision: `aaaff2dfbfde8969f10ee543da40f99c919e99b1`.
- `device`: [2026-11-07 22:22: the UniXNU 0.1.0 boot menu appeared on the enchilada screen; no boot entry found because no payload volume exists; zero partition writes](https://github.com/dragon120820/UniXNU-enchilada/blob/c8404873d590fbbe43d81ed7c181d5142550a63c/evidence/20261107_unixnu_menu.md)
  Command: <code>fastboot boot out/bootimg9/boot/boot.img</code>. Revision: `2b9e37c84f9e4d94de311b70c3594216bfd01801`.

## CPU and interrupts {#cpu}

`planned`

Components: `ArmCpu`.

### Hardware and dependencies

- 8 cores, all AArch64: cpu0-3 Cortex-A75, cpu4-7 Cortex-A55 \[LOCAL\].
- Timer interrupt id 19 \(armcpu-timer-intid=19\) \[PORT\].
- CPU frequency control uses OSM: MemoryMapLib OSM 0x17D20000 + 0xB0000; GOLD\_SAW4\_SRM 0x17830000, SILVER\_SAW4\_SRM 0x17840000 \[MU\].
- GIC: GICD 0x17A00000 + 0x10000, GICR 0x17A60000 + 0x100000 \[MU\].
- PSCI via SMC \(psci\_method = smc in the port board.toml\) \[PORT\].
- Observed kernel args: cpus=8, armcpu-self-ipi=1, pcpu=0xf0, sheng-smp=1 \[PORT\].

### Configuration

- Record the CPU register list 0,0x100,0x200,0x300,0x400,0x500,0x600,0x700 used by the ADT payload.

### Procedure

- Bring up one CPU first, then the remaining cores, verifying timer and IPI on each.

### Development findings

- Community bisect shows the CPU reaches past msr SCTLR\_EL1 and its ISB compare loop, and pmap/VM init completes; the stall is later, in root mounting.
- The kernel reports CPU part 0x803 for cpu0-3 and 0x802 for cpu4-7, but cpuinfo\_max\_freq says 1766400 kHz for cpu0-3 and 2803200 kHz for cpu4-7. SDM845 is 4x A75 at 2.80 GHz and 4x A55 at 1.77 GHz, so the cluster assignment follows the clocks: 0x000-0x300 are the A55 \(cluster type E\) and 0x400-0x700 the A75 \(type P\) \[LOCAL\]
- timebase-frequency does not appear on /cpus in the live device tree; the only clock-frequency is 0x124F800 = 19200000 on /soc/timer, and the board DTS sets timebase-frequency to that value on /cpus \[LOCAL\]

### Completion criteria

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU.

### Current limits

- No device verification; the community evidence is from a different unit \(serial 4eeb4492\).

### Next action

- Confirm the A75/A55 mask revision against the SoC layer once it exists.

### Evidence

Collect evidence using the next action.

## Memory and DMA {#memory}

`planned`

Components: `ArmDTPlatform`, `RamBlock`, `ArmSmmu4K`.

### Hardware and dependencies

- MemTotal 7,814,464 kB \(7.45 GiB\); CmaTotal 204,800 kB; dram\_size must be 0x200000000 \[LOCAL\]\[PORT\].
- Authoritative MMIO map: Mu MemoryMapLib.c, 66 entries, which carries lengths the device tree does not \[MU\].
- DDR layout: Kernel 0x80000000+0x600000, DBI Dump 0x80600000+0xD20000, Hypervisor 0x85700000+0x600000, AOP CMD DB 0x85FE0000+0x20000, SMEM 0x86000000+0x200000, QSEE 0x86200000+0x4900000, DXE Heap 0x97C00000+0x5730000, Display Reserved 0x9D400000+0x2400000, FV 0x9F800000+0x400000, FD 0x9FC00000+0x300000, SEC Heap 0x9FF00000+0x8C000, PageTables 0x9FF8D000+0x3000, UEFI Stack 0x9FF90000+0x40000, Log Buffer 0x9FFF7000+0x8000, Info Blk 0x9FFFF000+0x1000 \[MU\].
- Six of these were confirmed independently on this unit: Hypervisor 0x85700000, SMEM 0x86000000, QSEE end 0x8AB00000, Display Reserved 0x9D400000, Log Buffer 0x9FFF7000, AOP 0x0C300000 \[LOCAL\].
- SMMU: Apps SMMU 0x15000000 + 0xD0000; ARM\_SMMU\_V3 is disabled, so this is SMMUv2 \[LOCAL\]\[MU\].
- sheng owned\_memory\_size 0x130000000 \(4.75 GiB\): 3 GiB ran out of memory 2 minutes into userland \[PORT\].
- CONFINFLICT: Mu maps pinctrl as TLMM\_EAST/NORTH/SOUTH at 0x03500000/0x03900000/0x03D00000 \(11 MiB total\), but Linux DT binds pinctrl@3400000 with reg 0x03400000 + 0xC00000 \(12 MiB\). The missing low 1 MiB holds every GPIO register \(150 GPIOs at 0x1000 stride end at 0x96000\). Use 0x03400000 + 0x00C00000 \[LOCAL\]\[MU\].

### Configuration

- Record every handoff region and the cache policy each DMA engine is given.

### Procedure

- Reconcile the 66 MemoryMapLib entries against the device tree reserved-memory nodes before flashing anything.

### Development findings

- The TLMM discrepancy would send every GPIO access to unmapped memory, breaking touch pinmux, buttons, panel reset and backlight enable.
- TLMM is one 12 MiB window at 0x03400000, confirmed twice: /proc/iomem reports pinctrl\_regs 03400000-03ffffff and the device tree gives reg &lt;0x03400000 0x00C00000&gt; \[LOCAL\]. The firmware memory map splits it into three 3 MiB windows starting at 0x03500000, which omits the first MiB, the block holding the control registers for GPIO 0..15 \[MU\]\[LOCAL\]
- apps-smmu is compatible qcom,qsmmu-v500 with reg &lt;0x15000000 0x80000 0x150c2000 0x20&gt; and \#iommu-cells = 2, i.e. a V500 generation controller; XNU has no qsmmu-v500 driver, so ArmSmmu4K cannot be reused as-is \[LOCAL\]
- The ufshc node in the live device tree has no iommus property and no stream id 0x100 appears anywhere in the tree, so the community kernel arguments native-ufs-smmu-stream/mask/size/adopt have no device tree backing on this handset \[LOCAL\]

### Completion criteria

- All handoff regions are accounted for and each enabled DMA engine accesses its allocated range with the documented cache policy.

### Current limits

- /proc/iomem is unreadable without root, so the TLMM base still lacks a direct device read.

### Next action

- Adopt 0x03400000 + 0x00C00000 in the SoC layer and confirm with su when root is available.

### Evidence

Collect evidence using the next action.

## Storage and root {#storage}

`planned`

Components: `VerifiedRoot`.

### Hardware and dependencies

- UFS HC 0x01D84000 \(node 1d84000.ufshc\), UFS PHY 0x01D87000 \(1d87000.ufsphy\_mem\), UFS ICE 0x01D90000 \(1d90000.ufsice\) \[LOCAL\].
- Mu maps the whole controller block as UFS REGS 0x01D80000 + 0x20000, which covers HC, PHY and ICE. This differs in meaning from ShengUfs \(SM8550\), whose PHY base is also 0x01d80000; never copy that constant \[MU\].
- ICE is compiled in on the Android kernel \(CONFIG\_SCSI\_UFS\_QCOM\_ICE=y\); the bypass or disable decision is still open \[CFG\].
- Kernel uses 4 KiB pages and VA\_BITS=39 \(CONFIG\_ARM64\_4K\_PAGES=y, CONFIG\_ARM64\_VA\_BITS=39\) \[CFG\].
- SMMU for UFS: stream 0x100, mask 0xf, apps\_smmu reg size 0x80000; firmware retains 0x800f0100 in bank 2 with translation off \[PORT\].
- Six normal LUNs 0-5 map to sda-sdf; three well-known LUNs 49456/49476/49488 also exist \[LOCAL\].
- Partition map: system\_a sda13, userdata sda17, boot\_a sde11, boot\_b sde39, vendor\_a sde16, dtbo\_a sde18, vbmeta\_a sde17, ImageFv sde72, modemst1 sdf2 \[LOCAL\].
- userdata: first\_lba 0x186f40, last\_lba 0x1d06ffa, lba\_bytes 4096 -&gt; 28,836,027 blocks = 118,112,366,592 B = 110.00 GiB \[LOCAL\]\[PORT\].
- Write windows are derived from last\_lba at runtime \(NativeUfs.cpp:1289-1340, 1498-1532\). For 128 GB: log \[30,429,179, 30,437,370\] 8192 blocks; export \[30,363,643, 30,429,178\] 65536 blocks; store last LBA 30,175,226 \(reserve 1024 MiB\) \[PORT\].
- The community driver reports write protection unconditionally \(NativeUfs.cpp:1681\) while still containing three code paths that write into userdata; native-data-writeback=1 sends Data writes without FUA \[PORT\].

### Configuration

- Record the LUN geometry, the SHNGROOT manifest policy for OS and SystemOS, and the exact reserve value.

### Procedure

- Probe capacity and read the same block repeatedly before any write; derive every window from the measured last\_lba.

### Development findings

- Community bisect on a sibling unit isolates the XNU stall to \_vfs\_mountroot: NativeUfs.cpp:1093 finds \!gStoreGeometry.valid \|\| \!gHost.ready, so no root layout is published without a SHNGROOT manifest.
- The storage partitions are not all on the first LUN: boot\_a, boot\_b, dtbo\_a, dtbo\_b, vbmeta\_a, vbmeta\_b, vendor\_a and vendor\_b live on LUN 4 \(sde\), while sda carries only system, odm, userdata, persist and the small configuration partitions \[LOCAL\]
- The userdata geometry of the 8 GB / 128 GB SKU is first\_lba 0x186f40, last\_lba 0x1d06ffa at 4096 bytes, 28836027 blocks = 118112366592 bytes = 110.00 GiB, which matches the formatted ext4 size df reports; the community port records the 64 GB SKU values 0x186f40..0xe217fa, 50.41 GiB, and those must not be used here \[LOCAL\]\[PORT\]
- ImageFv on LUN 4 is 2 MiB of zeros, checked block by block at 4096 bytes with no non-zero block, which agrees with the firmware configuration ImageFVFlashed = 0x0; the first round does not use that channel \[LOCAL\]\[MU\]

### Completion criteria

- Host: register, clock, link and SMMU facts match the board inventory.
- Reads: SCSI capacity, GPT and known blocks are correct; OS/SystemOS windows stay within userdata.
- Root: the configured volume mounts and launchd starts. Persistence: writes survive reboot within the allocated Data region.

### Current limits

- GPT bytes and partition sizes unreadable without root; the 128 GB windows above are computed, not measured on this unit.

### Next action

- Measure last\_lba with sgdisk once root is available and re-check every window against the table in NEXT\_TASKS.md T-008.

### Evidence

Collect evidence using the next action.

## Display {#display}

`planned`

Components: `GopFramebuffer`.

### Hardware and dependencies

- MDP 0x0AE00000; DSI ctrl0 0x0AE94000; DSI PHY0 0x0AE94400; DSI PLL 0x0AE94A00; DP PLL 0x088EA000; four CSIPHY at 0x0AC65000/66000/67000/68000 \[LOCAL\].
- Mu maps MDSS as 0x0AE00000 + 0x134000, which covers the DSI blocks above \[MU\].
- Panel 1080x2280, density 420 dpi \(override 300\); single backlight panel0-backlight \[LOCAL\].
- Community identifies the panel as samsung,sofef00 at 60 Hz; this is a third-party claim not read from this unit's device tree \[PORT\].
- Framebuffer: stride 4320 bytes, BGRA8888, GOP base 0x9D400000; the firmware GOP is the only early framebuffer path \[PORT\]\[MU\]\[LOCAL\].
- BootVideo.h:31 hardcodes Video\[1\]=1 and NativeLegacyDisplay.cpp:611 takes the firmware framebuffer, so boot-progress=2 is the only on-screen progress channel \[PORT\].
- Known limitation: logical resolution is widened to 2048x2732 and on-screen text is about 4 px, effectively unreadable \[PORT\].

### Configuration

- Record DSI lane count and panel timings once they can be read; all 23 dsi-display@N nodes exist but dtbo\_idx=5 selects one unspecified variant.

### Procedure

- Bring up the firmware framebuffer first; DSI and panel power are a later stage.

### Development findings

- The official template's KTZ8866 backlight does not apply; this board exposes a single panel0-backlight node.

### Completion criteria

- A known frame appears with correct geometry and colors, then userland presentation and backlight controls work.

### Current limits

- Panel compatible, DSI lane count and timings unverified on this unit; modes and edid are empty as expected for DSI.

### Next action

- Read the active dsi-display node and its panel timing once root access exists.

### Evidence

Collect evidence using the next action.

## Input {#input}

`planned`

### Hardware and dependencies

- Touch controller: Synaptics RMI on I2C-3 at address 0x20; controller i2c@a90000 at 0x0A90000; DT node soc/i2c@a90000/synaptics-rmi-ts@20 \[LOCAL\].
- Part number is S3706B \(GENI I2C\), per the community build script build-enchilada-touch.py producing libEnchiladaTouch.a. The Android kernel enables CONFIG\_TOUCHSCREEN\_SYNAPTICS\_S3320\_I2C\_RMI, i.e. it reuses the S3320 driver family, which does not make the part an S3320 \[PORT\]\[CFG\].
- The official ShengNovatekTouch template does not apply; this is not a Novatek panel \[DOC\]\[LOCAL\].
- Buttons: soc/gpio\_keys \[LOCAL\].
- Fingerprint: both fpc\_fpc1020 and goodix\_fp exist in the tree, persist.vendor.oem.fp.version=3 \[LOCAL\].
- Eight input event nodes event0-event7 exist, but their names are unreadable \[LOCAL\].

### Configuration

- Record the RMI function pages actually exposed by S3706B before writing a register map.

### Procedure

- Bind I2C, read the product and firmware IDs, then map touch coordinates onto the 1080x2280 panel.

### Development findings

- Assuming an S3320 register layout is unsafe: the same RMI family can expose different function page layouts per part number.

### Completion criteria

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive, and buttons produce expected HID reports.

### Current limits

- No device verification; the S3706B identification comes from a third-party build script.

### Next action

- Read the touch product ID through the I2C bus once a driver can bind.

### Evidence

Collect evidence using the next action.

## GPU {#gpu}

`planned`

### Hardware and dependencies

- GPU is Adreno 630 at 5000000.qcom,kgsl-3d0; KGSL 0x05000000, GPU SMMU 0x05040000, GMU 0x0506A000 \[LOCAL\].
- Upstream components.toml has no Adreno 630 entry; only Adreno 740 is supported \[DOC\].
- First round keeps the GPU off by project decision.

### Configuration

- No configuration in the first round.

### Procedure

- Not applicable until the GPU stage opens.

### Development findings

- GPU acceleration requires a new component and is out of scope for the first round.

### Completion criteria

- GPU submissions complete, mapping/fence handling is correct, a known image renders, and the selected Metal client presents it.

### Current limits

- Deliberately out of scope for the first round.

### Next action

- Record as not-applicable for the first round once the plan confirms GPU stays off.

### Evidence

Collect evidence using the next action.

## Network {#network}

`planned`

### Hardware and dependencies

- Wi-Fi and Bluetooth are Qualcomm ICNSS with an integrated WCN3990-class part, not a PCIe card: ICNSS 0x18800000 \(18800000.qcom,icnss\), wlan0 driver symlinks to /sys/bus/platform/drivers/icnss, module qca\_cld3\_wlan.ko \[LOCAL\].
- /sys/bus/pci/devices is empty, confirming there is no discrete Wi-Fi card \[LOCAL\].
- Firmware region wlan\_fw\_region@0x8df00000; Bluetooth transport uses BTFM SLIM \(CONFIG\_BTFM\_SLIM=y, CONFIG\_BTFM\_SLIM\_WCN3990=y\) \[LOCAL\]\[CFG\].
- MSS 0x04080000 and IPA 0x01E00000 are present for modem/IPA paths \[LOCAL\].
- NFC is an NXP PN5xx on I2C-1 at 0x28, controller i2c@88c000 \[LOCAL\].
- The official Ath12kWifi and MhiBoot components target a different \(PCIe/MHI\) class of hardware \[DOC\].

### Configuration

- Record the ICNSS firmware names and the BT transport selection.

### Procedure

- Treat networking as out of scope until the platform and storage stages pass.

### Development findings

- The upstream network component match is wrong for this board; an ICNSS-class component would be required.

### Completion criteria

- Scanning, association, address configuration and sustained receive/transmit traffic pass with the selected firmware.

### Current limits

- Out of scope for the first round; no component exists upstream.

### Next action

- Defer until boot, storage and display are verified.

### Evidence

Collect evidence using the next action.

## Audio {#audio}

`planned`

### Hardware and dependencies

- LPASS 0x17300000; SLIMbus buses at 0x171C0000 and 0x17240000 \[LOCAL\].
- Codec: WCD934x \(snd-soc-wcd934x.ko, wcd-core.ko, snd-soc-wcd-mbhc.ko\); speaker amps WSA881x \(snd-soc-wsa881x.ko\) \[LOCAL\].
- Smart amp: Maxim MAX98927 on I2C-2 at 0x3A \(max98927@3a\) \[LOCAL\].
- Also loaded: snd-soc-wcd-spi.ko, wcd-dsp-glink.ko, swr-wcd-ctrl.ko, pinctrl-wcd.ko, snd-soc-sdm845.ko \[LOCAL\].

### Configuration

- Record the codec, amp and SLIMbus topology if audio is ever brought up.

### Procedure

- Not applicable until the earlier stages pass.

### Development findings

- No upstream audio component matches WCD934x plus MAX98927.

### Completion criteria

- Each declared route carries the selected audio format through playback or capture and handles start/stop correctly.

### Current limits

- Out of scope for the first round.

### Next action

- Defer.

### Evidence

Collect evidence using the next action.

## Power {#power}

`planned`

### Hardware and dependencies

- SPMI 0x0C440000 \(c440000.qcom,spmi\); PMIC arbiter block 0x0C400000 + 0x2800000 \[LOCAL\]\[MU\].
- PMICs: pm8998, pm8005 and pmi8998 are all present in the SPMI tree \[LOCAL\].
- Fuel gauge: TI BQ27541 on I2C-0 at 0x55; chargers smb1355 at 0x8 and 0xc; oneplus\_fastchg at 0x26 \[LOCAL\].
- power\_supply nodes: battery, bms, dc, main, pc\_port, usb \[LOCAL\].
- Sample reading during capture: 59 percent, 3958 mV, 33.6 C, status charging, health good \[LOCAL\].
- Thermal: TSENS0 0x0C222000, TSENS1 0x0C223000; 72 thermal zones and 22 cooling devices exposed \[LOCAL\]\[MU\].
- APPS RSC 0x179C0000 + 0x30000 and QMP AOP 0x0C300000 are the sleep/resume path \[MU\]\[LOCAL\].

### Configuration

- Record the regulator and charger topology before enabling any power management.

### Procedure

- Defer until the platform and storage stages pass.

### Development findings

- The official ShengPlatformPower inputs are board specific and must be re-derived from the PMIC inventory above.

### Completion criteria

- Declared power controls and battery readings match observations; each claimed sleep/resume transition restores its dependent peripherals.

### Current limits

- Out of scope for the first round.

### Next action

- Defer.

### Evidence

Collect evidence using the next action.

## Image assembly {#packaging}

`planned`

Components: `DarwinBoot`, `XnuPrelink`.

### Hardware and dependencies

- Boot image format measured on the stock OnePlus boot.img and on LineageOS 22.2: header\_version 0, pagesize 4096, base 0x0, kernel\_offset 0x8000, ramdisk\_offset 0x1000000, tags\_offset 0x100 \[PORT\].
- header\_version is deliberately 0; the device rejects v1 loading v0, and postmarketOS does the same \[PORT\].
- initrd window reserved by the bootloader is 0x8454D000-0x856FEF79, about 18 MiB, reported by EnchiladaBootMemoryDxe \[PORT\].
- Four measured payload sizes: none gives a menu with a red no-boot-entry message; 16 MiB reaches the menu and exposes USB 05C6:F000; 32 MiB resets into EDL 9008 after 68 s; 192 MiB shows no USB for 118 s and returns to fastboot \[PORT\].
- The linked kernel with libVerifiedRootProbe.a is 120.0 MiB \(two manifests totalling 69.9 MiB\), so a ramdisk-carried payload cannot fit the 18 MiB window \[PORT\].
- Route 2 therefore applies: flash the payload into system\_b \(2,998,927,360 B\) and build a boot image with no ramdisk \[PORT\].
- kernel\_args are 970 bytes against a 1000-byte limit and a 1024-byte DarwinBoot buffer, leaving 30 bytes \[PORT\].
- ABL refuses fastboot boot after the active slot fails to boot \(Load Error\) and each reset consumes a retry, so set\_active must precede every attempt \[PORT\].
- The bundled fastboot in C:\\platform-tools is a 32-bit binary and raises std::bad\_alloc on an 8.74 GiB raw image; sparse chunks are required \[PORT\].

### Configuration

- Record the boot image fields and the payload volume once Route 2 is confirmed on this unit.

### Procedure

- Build the payload, write it to system\_b, build a boot image with ramdisk none, then fastboot set\_active before each boot attempt.

### Development findings

- The 18 MiB initrd window, not the ABL image size limit, is what forbids carrying the payload in the ramdisk.
- The live device tree writes linux,initrd-start 0x841c9000 and linux,initrd-end 0x856fe8cb, a 0x15358cb = 21.21 MiB window that is byte-identical to the ramdisk\_size field of the boot\_a header, so 21.21 MiB is what this boot actually loaded and not a ceiling. The community figure of about 18 MiB is neither: it starts 3.52 MiB higher and ends 0x6ae lower than this range, and no measurement on this unit supports it as an upper bound \[LOCAL\]
- boot\_a parses as header\_version = 1 \(kernel 14770103 bytes at 0x8000, ramdisk 22254283 bytes at 0x01000000, tags at 0x100, page size 4096\), which contradicts the community note that this handset refuses v1 boot images: the live slot is v1 and Android boots from it \[LOCAL\]

### Completion criteria

- Kernel and prelink succeed, payload contains all declared inputs, and the boot image matches the bootloader format and size limit.

### Current limits

- No build host; bootloader lock state unknown, which may forbid fastboot entirely.

### Next action

- Confirm system\_b is free and its size matches 2,998,927,360 B before planning any write.

### Evidence

Collect evidence using the next action.

## Diagnostics {#diagnostics}

`planned`

Components: `DarwinBoot`.

### Hardware and dependencies

- Diagnostic log lives in the last kLogReserveBlocks of userdata \(8192 blocks = 32 MiB\) with a 256 MiB export region below it \(NativeUfs.cpp:1289-1292, 1498-1532\) \[PORT\].
- For this 128 GB unit those regions are log \[30,429,179, 30,437,370\] and export \[30,363,643, 30,429,178\] \[PORT\].
- Boot progress reaches the screen only through boot-progress=2; DarwinBoot prints DARWINBOOT: lines and refuses with 'boot refused: &lt;status&gt;; firmware retained' \[DOC\].
- Community probe arguments already exist: entry\_probe\_reset\_after, entry\_probe\_reset\_in, entry\_probe\_reset\_occurrence, panic\_screen \[PORT\].
- Community bisect history records 22 numbered runs narrowing the stall to \_vfs\_mountroot; the \_load\_context no-reset result is a false positive because that function does not return on success \[PORT\].

### Configuration

- Record each probe argument and the stage it targets.

### Procedure

- One probe per boot; record the last confirmed stage and the log path before reflashing.

### Development findings

- No SHLOG001 dump exists in any candidate repository, so there is currently no reproducible device log to compare against.

### Completion criteria

- Each claimed milestone has a reproducible command, a matching source/image revision and an accessible result.

### Current limits

- No device verification on this unit; all bisect evidence comes from a sibling device.

### Next action

- Establish a local log capture path before the first boot attempt.

### Evidence

Collect evidence using the next action.

</div>
