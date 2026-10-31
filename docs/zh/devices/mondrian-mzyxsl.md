# Redmi K60 \(mondrian/SM8475\): UniXNU UEFI bring-up \(mzyxsl\)

[mzyxsl/UniXNU-mondrian](https://github.com/mzyxsl/UniXNU-mondrian)

<div v-pre>

Redmi K60 \(mondrian/SM8475\). Format 2 device: the kernel builds and prelinks, the payload and the boot image still need the board ADT and the hardware bring-up.

源记录: [porting.toml](https://github.com/mzyxsl/UniXNU-mondrian/blob/76552b88441757defce4080a241c2f0ea7464538/porting.toml), `76552b88441757defce4080a241c2f0ea7464538`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `implemented` |
| [固件与启动](#firmware) | `implemented` |
| [CPU 与中断](#cpu) | `implemented` |
| [内存与 DMA](#memory) | `implemented` |
| [存储与根卷](#storage) | `implemented` |
| [显示](#display) | `implemented` |
| [输入](#input) | `planned` |
| [GPU](#gpu) | `implemented` |
| [网络](#network) | `planned` |
| [音频](#audio) | `planned` |
| [电源](#power) | `planned` |
| [镜像组装](#packaging) | `host-verified` |
| [诊断](#diagnostics) | `planned` |

## 配置 {#configuration}

`implemented`

组件: `ArmDTPlatform`, `ArmCpu`, `XnuPrelink`.

### 硬件与依赖

- Four layers merge in order: UniXNU profiles/arch/arm64, the SM8475 soc.toml from UniXNU-sm8475-common, the ipados-16.6.1-20G81 OS profile and this board.toml.
- Source pins are explicit 40-character commits in feeds.toml: xnu 8796.141.3 \(1b191cb5\), libplatform \(1b2b22f2\), libdispatch \(ca80d303\), AvailabilityVersions \(f3b52ca7\) and sm8475 \(d0c90f1e\).
- The OS profile carries \[ipsw\] \(iPad7,1, 16.6.1, 20G81, device class j120ap, chip 32785 = 0x8011, board 12, fetch KernelCache/DeviceTree/StaticTrustCache/Cryptex1,SystemTrustCache\) and \[kernel.prelink\] \(32 roots, slide 0 for the auto-slide wrapper\), so board.toml carries neither table.

### 配置

- board.toml schema\_version = 2; \[board\] name mondrian, soc SM8475, soc\_source sm8475, os\_profile ipados-16.6.1-20G81, kit mondrian, no example flag.
- \[components\] include replaces the arch list with ArmDTPlatform, ArmCpu, XnuPrelink and PongUfs; \[kernel\] defconfig mondrian\_defconfig with arch/soc/os fragments, patch\_series device:patches/xnu/series only, archives component:ArmDTPlatform/ArmCpu/PongUfs and driver\_records DEVELOPMENT\_ARM64\_PONG.
- \[device\_tree\] source device:dts/mondrian.dts with include\_dirs soc:dts; \[userdata\] first\_lba 53342976, last\_lba 61731583, lba\_bytes 4096 and windows OS + Cryptex1,SystemOS.
- patches/xnu/series holds 98 entries in application order: 4 of them are the 021x display patches, 13 are K60-specific \(trust cache, panic reporting, compiler fixes\) and the remaining 81 are the shared Darwin 22 / Pong bring-up patches; the other 22 files in the directory are intentionally unlisted and documented as switched off or version-bound.

### 操作步骤

- Clone UniXNU \(branch k60\) with submodules and place UniXNU-sm8475-common, UniXNU-mondrian and uefi-mondrian beside it.
- ../UniXNU-mondrian/scripts/k60-macos-preflight.sh; ./unixnu defconfig mondrian\_defconfig -D ../UniXNU-mondrian; ./unixnu fetch -D ../UniXNU-mondrian; ./unixnu status --json -D ../UniXNU-mondrian; ./unixnu tree -D ../UniXNU-mondrian.
- python3 scripts/porting-record.py check --device ../UniXNU-mondrian in the core checkout, and python3 ../UniXNU-mondrian/scripts/check-porting-paths.py for the offline identity, component, path and series checks.

### 开发经验

- Migrated from format 1 on 2026-10-28: the output directory became out/mondrian/ipados-16.6.1-20G81/mondrian/ and every pin moved into feeds.toml.
- The lock file still recorded the earlier sm8475 commit 70f20268 while feeds.toml pinned the later d0c90f1e \(2026-10-28 15:19Z, 'tag every CPU node with a Darwin cluster type'\). An explicit format-2 commit wins over the lock, so the lock entry was corrected to the feed value instead of leaving two answers.
- board.toml \[payload\] trust\_cache\_sha256 was a bare string. The payload step tests membership in a list, so a string made every --trust-cache fail the board allow-list; it is now the one-element array of the shipped bundle hash.
- docs/NEXT-STEPS.md kept the single-CPU first-boot line next to a board that sets cpus = 8. The note now says cpus=1 is the bring-up baseline and that the eight-CPU claim is still unmeasured, so the two documents no longer contradict each other.

### 完成条件

- Every pin resolves to an existing commit, status reports four components and the ordered device series, and both the official and the offline record check pass.

### 当前范围

- No core checkout or network in this workspace: the pins were confirmed through the GitHub API and the resolution of \[ipsw\]/\[kernel.prelink\] was read from the profile, not from a live status run.
- SoftwareAES from the arch profile is not selected by this board; the K60 links its platform archives through the pong build scripts instead of the format-2 archive recipes.

### 下一步

- Run status --json and tree on a host with all four checkouts and paste the resolved \[ipsw\], \[kernel.prelink\] and archive order into this area as host evidence.

### 证据

- `source`: [schema\_version 2 selects four components, the mondrian defconfig, the device-only patch series, 12 GiB DRAM and the cpus = 8 payload window](https://github.com/mzyxsl/UniXNU-mondrian/blob/76552b88441757defce4080a241c2f0ea7464538/board.toml)
- `source`: [five sources pinned to explicit commits: xnu 1b191cb5, libplatform 1b2b22f2, libdispatch ca80d303, AvailabilityVersions f3b52ca7, sm8475 d0c90f1e](https://github.com/mzyxsl/UniXNU-mondrian/blob/76552b88441757defce4080a241c2f0ea7464538/feeds.toml)
- `source`: [98 ordered entries, every referenced patch file present in patches/xnu](https://github.com/mzyxsl/UniXNU-mondrian/blob/76552b88441757defce4080a241c2f0ea7464538/patches/xnu/series)

## 固件与启动 {#firmware}

`implemented`

组件: `DarwinBoot`.

### 硬件与依赖

- Mu-Silicium platform tree uefi-mondrian: Resources/Configs/mondrian.toml, Platforms/Xiaomi/mondrianPkg/mondrian.dsc and the FD at Build/mondrianPkg/&\#123;target&\#125;\_CLANGPDB/FV/SILICIUM\_UEFI.fd.
- Firmware must embed UniXNU, UniXNUDxe, DarwinBoot and UniXNURamDiskDxe plus DiskIoDxe and FAT so the payload FAT volume is discoverable before the config is read.
- Boot inputs from the OS profile: kernelcache hash d260defc, the 20G81 trust cache bundle \(SHA-256 344ae644\) and the Data seed; the platform seed is only needed when a board passes --unique-chip-id.
- Vendor binaries for display, keypad and logger come from uefi-mondrian; this repository only lists them in proprietary-files.txt.

### 配置

- \[firmware\] config mondrian, dsc Platforms/Xiaomi/mondrianPkg/mondrian.dsc, fd Build/mondrianPkg/&\#123;target&\#125;\_CLANGPDB/FV/SILICIUM\_UEFI.fd, patches AsmMacroLib.patch and Boot-Manager.patch, and packages &\#123;uefi&\#125;, &\#123;tree&\#125;/package, &\#123;tree&\#125;/drivers/DarwinBoot22, &\#123;edk2&\#125;, Platforms/Xiaomi, Common/Mu, Silicon/Qualcomm, Silicon/Silicium, Silicium-ACPI and Binaries/pong.
- \[firmware.defines\] DEVICE\_MODEL 0, ENABLE\_SECUREBOOT 0, MEMORY\_PROTECTION TRUE, SHIP\_MODE FALSE, BUILDID\_STRING UniXNU-Mondrian.
- DarwinBoot22 contract: boot\_args 0x2e0 bytes with a 608-byte command line at 0x6c and Video\[6\] at 0x28; one 256 MiB EfiConventionalMemory window aligned to 2 MiB plus the kernel base; ADT capped at 16 MiB; trust cache sidecar 1..128 modules with strictly ascending SHA-1 entries.

### 操作步骤

- ./unixnu build firmware --uefi ../uefi-mondrian -D ../UniXNU-mondrian, or scripts/build-firmware.sh from a Pong-layout checkout.
- python3 scripts/verify-firmware.py --output-dir &lt;build&gt; checks the FV header, checksum, and the UniXNU \(9b665204\), UniXNUDxe \(29b950cf\), DarwinBoot \(1b64af87\) and PongBootMemoryDxe \(7b27b767\) FFS files plus ARM64 PE machine 0xaa64.
- scripts/build-darwinboot22-macos.py compiles the loader against the Darwin 22 headers without touching the saved FD; the resulting DarwinBoot22.efi is what a payload-side boot image stages.

### 开发经验

- The loader installs the UniXNULoader protocol in RAM only and restores the previous interface on unload; no firmware variable or partition is written, which is what keeps fastboot boot bring-up read-only.
- DarwinBoot must run at EL1: DarwinCurrentEl\(\) \!= 4 returns EFI\_UNSUPPORTED and keeps the firmware alive, so a payload started at EL2 never reaches XNU.
- The green bar is the trampoline, not the kernel: it paints the top 1/16 of the framebuffer 0xFF00FF00, clears SCTLR\_EL1 M/C/I, and branches to the kernel entry. README.md:19-20 therefore records payload entry as unconfirmed, which is why this area is not device-verified.
- The one-window layout is args at 16 KiB alignment after the kernel image, ADT one page later, page-aligned ramdisk, trust cache, then a copied trampoline page; Used must stay below WindowSize minus 2 MiB or the boot is refused.
- prebuilt/20G81-trustcache.bundle is a 61,764-byte bundle with two modules \(2510 and 61 entries, version word 2\) that satisfies the loader validator, and its SHA-256 equals the board allow-list entry.
- The host tests are real but narrow: Test/Validation.c drives 24 rejected loader requests \(6 kernel paths, 6 memory windows, 4 ramdisk layouts, 8 trust-cache layouts\) plus the GOP format check, Test/window-size.c asserts five accepted and six rejected window sizes, and scripts/test-window-qemu.py asserts the post-ExitBootServices pixel 12d4a6 with df2020 and aa33dd as failure controls. None of these ran in the last Mac round.

### 完成条件

- Firmware builds with the required modules, the FD passes verify-firmware.py, the menu appears, DarwinBoot prints its handoff lines and the owned window survives into XNU.

### 当前范围

- Device observation currently stops at the green bar: no serial, ramoops or framebuffer line proves that XNU executed after the trampoline.
- The boot image has not been packed for this board yet, so the documented payload path is exercised only by host-side tests and QEMU.
- USB log export is a design in docs/USB-LOGGING-PLAN.zh.md; no USB logger or host reader exists in the tree.

### 下一步

- Boot one image with the serial console enabled and capture the first XNU-side line after the green bar, then record it as device evidence with the firmware and payload revisions.

### 证据

- `source`: [loader validates the Mach-O, binds ADT/trust-cache/ramdisk sidecars through zero-filled /chosen placeholders and retries ExitBootServices three times before branching through the trampoline](https://github.com/mzyxsl/UniXNU-mondrian/blob/76552b88441757defce4080a241c2f0ea7464538/drivers/DarwinBoot22/DarwinBootPkg/Driver/DarwinBoot.c)
- `source`: [host QEMU assertion on the real post-ExitBootServices framebuffer: 12d4a6 pass with df2020 and aa33dd as the wrong-window and exception controls](https://github.com/mzyxsl/UniXNU-mondrian/blob/76552b88441757defce4080a241c2f0ea7464538/scripts/test-window-qemu.py)
- `source`: [61,764-byte two-module bundle, 2510 and 61 entries, SHA-256 344ae6445dfcb791ac838dbfec5c4d39a871cf58f91d8bee84ba57204f6727e6](https://github.com/mzyxsl/UniXNU-mondrian/blob/76552b88441757defce4080a241c2f0ea7464538/prebuilt/20G81-trustcache.bundle)

## CPU 与中断 {#cpu}

`implemented`

组件: `ArmCpu`.

### 硬件与依赖

- Eight SM8475 CPUs with MPIDR affinities 0x000..0x700 declared in the SoC dts/sm8475.dtsi, plus the PSCI conduit and the GICv3 distributor and redistributor windows.
- Measured on the unit: GIC distributor 0x17100000 and redistributor 0x17180000; the driver reads the real bases from /arm-io ranges and /arm-io/intc reg instead of hardcoding them.
- Redistributor stride is accepted only as 0x20000, 0x30000 or 0x40000 \(falling back to TYPER.VLPIS\), matching the 0x17180000 window of this SoC.

### 配置

- CONFIG\_XNU\_ARMCPU=y, CONFIG\_XNU\_ARM\_DT\_PLATFORM=y, CONFIG\_XNU\_NATIVE\_ARCH\_TIMER=y, CONFIG\_XNU\_ARMVIRT\_PLATFORM=n in configs/mondrian\_defconfig.
- \[payload\] cpus = 8 caps the ADT CPU list; the AppleARMCPU multi-CPU validation is bypassed by the kext patch on \_validateConfiguration.
- Kernel side: MAX\_CPUS 8, MAX\_CPU\_CLUSTERS 2, GENERIC\_PSCI\_SMP and ARM\_ARCH\_TIMER from the psci-smp patch's board\_config.

### 操作步骤

- python3 scripts/build-pong-armcpu-macos.py compiles the GICv3/PSCI provider against the Darwin 22 headers; the archive is linked through \[kernel\] archives component:ArmCpu.
- Prelink and boot, then read the XNU serial output for the per-CPU registration lines and the PSCI start results.

### 开发经验

- ArmCpu registers every device\_type = cpu nub first and panics if armcpu\_registered \!= ml\_get\_cpu\_count\(\), so a DTS that hides a CPU fails loudly instead of booting with fewer cores.
- MPIDR matching uses aff0-aff2 plus aff3 against GICR\_TYPER\[63:32\]; the boot affinity is mpidr &amp; 0xff00ffffff and SGIs are addressed through ICC\_SGI1R\_EL1 built from all four affinity fields.
- Only INTID 0 \(SGI0 IPI\) and INTID 27 \(CNTV PPI\) are enabled; 32..1019 dispatch to SPI owners with priority 0xa0, and the only in-tree SPI client is Adreno at 332.
- PSCI uses 0xC4000003 CPU\_ON and 0x84000002 CPU\_OFF with 5 s start and 3 s stop timeouts, cleaning \_\_TEXT, \_\_TEXT\_EXEC, \_\_DATA, \_\_DATA\_CONST, \_\_BOOTDATA and every cpu\_data\_t to the point of coherency before the call.
- The UFS controller declares SPI 265 in the DTS but never attaches it, so storage is polled rather than interrupt driven; that is a deliberate bring-up choice, not a missing GIC feature.
- docs/NEXT-STEPS.md documents the first bring-up with cpus=1 and warns against cpus=8, while board.toml has set cpus = 8 since the 2026-10-29 measurement. The note now marks the single-CPU line as the bring-up baseline and points at this area for the missing eight-CPU log; the board value stays.

### 完成条件

- Every enabled CPU reaches its entry checkpoint, the timer interrupt count advances on each CPU, and an IPI reaches every started secondary.

### 当前范围

- Implemented from source only: the eight-CPU start is unproven on hardware because no run log is stored here.
- The pong\_adt\_contract audit accepts exactly one running CPU, so an eight-CPU ADT can only be produced outside that audit; the incompatibility is unresolved.

### 下一步

- Capture one boot log with 'ArmCpu: CPU n MPIDR=0x... registered' for all eight CPUs, no 'psci: cpu n ... was not started' line, and the armcpu\_timer\_interrupts delta across a one-second sleep.

### 证据

- `source`: [GICv3 distributor/redistributor setup from DT ranges, MPIDR to GICR matching, INTID 0/27 enablement, SPI publication with four owners and eight-CPU registration with a mismatch panic](https://github.com/mzyxsl/UniXNU-mondrian/blob/76552b88441757defce4080a241c2f0ea7464538/drivers/ArmCpu/ArmCpu.cpp)
- `source`: [PSCI CPU\_ON/CPU\_OFF conduits \(SMC and HVC\), secondary entry with SCTLR\_EL1 0x30D00800 and its own VBAR, cache maintenance of every cpu\_data\_t and a 64-byte fault record](https://github.com/mzyxsl/UniXNU-mondrian/blob/76552b88441757defce4080a241c2f0ea7464538/patches/xnu/zzzzzzzzzzzzzzzzzzzzz-pong-psci-smp.patch)

## 内存与 DMA {#memory}

`implemented`

### 硬件与依赖

- One contiguous DRAM range: dts/mondrian.dts memory@80000000 reg = &lt;0x0 0x80000000 0x3 0x0&gt;, 12 GiB, matching \[payload\] dram\_size 0x300000000.
- The ADT generator requires exactly one enabled memory node with exactly one range; the five-bank 16 GiB layout reported in issue \#1 cannot be described and needs the narrowed bank0 form documented in README.md.
- DMA width and contiguity limits: the UFS engine needs one physically contiguous 139 KiB buffer below 4 GiB when CAP bit 24 is clear, and the window parser accepts 0x10000000..0x200000000 in 2 MiB steps.

### 配置

- \[payload\] dram\_size 0x300000000, cpus 8 and timeout 5; the DTS /memory range is the single source that the ADT generator checks against dram\_size.
- CONFIG\_XNU\_NATIVE\_RAM\_BLOCK=y, CONFIG\_XNU\_NATIVE\_PAN=y, CONFIG\_XNU\_DT\_PANIC\_REGION=y, CONFIG\_XNU\_PONG\_RAMOOPS\_CONSOLE=y and CONFIG\_XNU\_PONG\_VOLATILE\_PANIC\_LOG=y in configs/mondrian\_defconfig.
- Panic and ramoops: darwinboot-memory-size is requested through \[payload.adt\] owned\_memory\_size when set; the loaded window is capped at 0x200000000 and must be 2 MiB aligned.

### 操作步骤

- Build the board DTS with the SoC include path: dtc -I dts -O dtb -i ../UniXNU-sm8475-common/dts dts/mondrian.dts.
- scripts/build-window-probe.py and scripts/build-window-probe-local.py build the own MMU-off probe kernel, and scripts/build-pong-ram-block-macos.py builds the volatile RAM block provider.
- scripts/test-window-qemu.py reads the framebuffer after ExitBootServices and compares it with the pass and failure colours.

### 开发经验

- The handoff window is the first boot constraint, not a driver detail: docs/NEXT-STEPS.md records a working p0prime of dram-base 0xB9200000 with dram-size 0x26C0000 and exactly 145502 free 4 KiB pages \(36905 at 16 KiB\), and that a larger window dies silently at the XPU wall 0xE9F00000.
- docs/NEXT-STEPS.md recorded that window as '0x26C0000 \(620 MiB\)'. The page count proves the hex value was wrong: 145502 free 4 KiB pages is about 568 MiB after the kernel image, so the documented value is now 0x26C00000 with the correction noted in place.
- NativeRamBlock reads /chosen/memory-map RAMDisk or PackedRAMDisk \(mutually exclusive, 4 KiB aligned, at most 0x80000000 bytes\) and switches from sparse pages to a SeedDisk above 2 GiB, which is what keeps a 32 GiB Data window tolerable.
- The persistence overlay \('SHNGDATA' v1, 64-byte header with generation and CRC32\) only calls weak-imported native\_ufs\_store\_\* symbols that no file in this repository defines, so persistence cannot link as committed.
- probes/window-probe.c is an independent diagnostic kernel, not XNU: it asserts the boot-args magic 0x00020002, CurrentEL 4 and the SCTLR bits, requires the window to be exactly 0x10000000, and writes two patterns at every 4 KiB page of the unused window with an exception path that prints ESR/FAR/ELR.

### 完成条件

- All handoff and reserved regions are accounted for, the ADT carries the DRAM base/size and window size, and every enabled DMA engine reaches its allocated range with the documented cache policy.

### 当前范围

- The realised window, SMMU geometry and DMA addresses have not been measured on this unit; the 12 GiB / 620 MiB pair above comes from the maintainer notes, not from a captured boot log.
- The 16 GiB variant needs a different /memory form and a matching dram\_size; the ADT generator refuses multi-range memory, so that unit cannot boot until the narrowed form is selected.

### 下一步

- Capture a window-probe boot and record 'PONG WINDOW PASS' with PAGES CHECKED, then set \[payload.adt\] owned\_memory\_size from the measured value instead of the documented one.

### 证据

- `source`: [single 12 GiB /memory range at 0x80000000 plus the UFS host, GCC page and SMMU properties the storage driver equality-checks](https://github.com/mzyxsl/UniXNU-mondrian/blob/76552b88441757defce4080a241c2f0ea7464538/dts/mondrian.dts)
- `source`: [own diagnostic kernel that validates the window size, patterns every 4 KiB page and prints PASS/FAIL with ESR/FAR/ELR on fault](https://github.com/mzyxsl/UniXNU-mondrian/blob/76552b88441757defce4080a241c2f0ea7464538/probes/window-probe.c)
- `source`: [memory-map discovery, 4 KiB alignment and size limits, sparse versus SeedDisk selection and the weak persistence overlay](https://github.com/mzyxsl/UniXNU-mondrian/blob/76552b88441757defce4080a241c2f0ea7464538/drivers/NativeRamBlock/NativeRamBlock.cpp)

## 存储与根卷 {#storage}

`implemented`

组件: `PongUfs`.

### 硬件与依赖

- UFS host at 0x01d84000 \(0x3000\), GCC UFS page 0x00187000, SMMU 0x15000000 \(0x100000\) with stream ID 0xe0, 78 context banks and 120 stream-match groups declared in the DTS.
- SMMUv2 register facts: IDR1.NUMCB 75 on the reference device caps the declared 78, IDR2 must advertise A64, banks and pages must fit the 0x100000 window and masked stream IDs are refused.
- Root volumes come from the OS profile disks: OS 096-57366-083.disk.cdr and SystemOS 096-56782-083.dmg, wrapped in a SHNGROOT v1 manifest with 128-byte window records.
- The Data volume is the committed seed seed/k60-data-seed.dbr: 33,554,432 bytes of raw APFS whose volume is 'OwnerData', SHA-256 5fd2f3566e989d11cde74289151888392615a4771e5b616ff5e98ca3b24ffc03, regenerated by scripts/k60-make-data-seed.py on macOS.
- The dual-system plan needs an unlocked TWRP with root ADB, decryptable /data and F2FS online shrink support before any partition work; see docs/DUAL-SYSTEM.md.

### 配置

- \[userdata\] first\_lba 53342976, last\_lba 61731583, lba\_bytes 4096 with windows OS and Cryptex1,SystemOS: 8,388,608 blocks, 32 GiB starting at byte 218,492,829,696.
- CONFIG\_XNU\_NATIVE\_UFS=y, CONFIG\_XNU\_OWNER\_CACHE\_MOUNT=y, CONFIG\_XNU\_OWNER\_CACHE\_STARTUP=y, CONFIG\_XNU\_OWNER\_DATA\_MOUNT=y, CONFIG\_XNU\_OWNER\_UNION\_SYSTEMOS=y, CONFIG\_XNU\_OWNER\_DATA\_UFS=n.
- CONFIG\_XNU\_OWNER\_DATA\_VOLUME\_UUID 6DCCF70A-6FD6-403E-ACED-95313CD7CBB8 is the 'OwnerData' volume inside the committed seed \(the Pong constant 576A2203-F35D-45DA-80B0-11EF01DDA8C9 never matches it\); CONFIG\_XNU\_OWNER\_CACHE\_VOLUME\_UUID 15B507FA-21B7-4EE5-B55D-0F3445DE0752; \[payload.adt\] root\_match\_volume\_uuid C5DAF029-2070-4F68-B3CC-1D1320344CF0.
- Writes are refused unless the boot argument pong\_ufs\_readwrite=1 is present, and the SCSI allow-list is TUR, START STOP UNIT on LUN 0xd0, READ CAPACITY\(10\), READ\(10\), WRITE\(10\) with FUA and SYNCHRONIZE CACHE\(10\).

### 操作步骤

- ./unixnu build userdata --dry-run then ./unixnu build userdata for the SHNGROOT image, or scripts/build-userdata.py --component-dir out/ipsw/20G81 --os-disk &lt;cdr&gt; --systemos-disk &lt;dmg&gt;.
- scripts/derive-ios16-storage-bindings.py --tree &lt;tree&gt; derives the 190 IOBlockStorageDevice slots from the genuine kernelcache; scripts/audit-ios16-storage-abi.py checks 176 bindings and the 0x90 class size.
- scripts/k60-make-data-seed.py --profile &lt;profile&gt; --output k60-data-seed.dbr builds the 32 MiB APFS Data seed on macOS; scripts/install-pong-ufs-data.py installs a Data window over ADB in recovery.
- For the independent partition, follow docs/DUAL-SYSTEM.md: partition.py inspect, plan with the f2fs-shrink helper, apply, then verify.

### 开发经验

- The transport takes over an already-initialised controller: it requires HCE bit 0, HCS low nibble 0xf, zero doorbells and a clear fatal interrupt mask, then runs a polled command ring with no resubmission and a poisoned buffer on timeout.
- LUN 0 must report exactly 4096-byte blocks through READ CAPACITY\(10\); any other geometry is refused as 'unsupported LUN geometry', which is the first thing to check on a different UFS part.
- Every DT property is equality-checked against the compiled constants before the first MMIO read, so a mismatch between dts/mondrian.dts and drivers/NativeUfs fails at probe with a specific message instead of corrupting a controller.
- The Data mount names the board's own seed volume. With the inherited Pong constant the lookup could never match, so /private/var stayed unmounted and mkbinit could not write /private/var/keybags/systembag.kb. The committed seed really carries 6DCCF70A-6FD6-403E-ACED-95313CD7CBB8: its volume superblock at 0xa2020 holds that UUID at +0xd0 and the name 'OwnerData' at +0x2a0, and both survive in the checkpoint copies at 0x15c020 and 0x15f020.
- A 32 MiB seed stays far below the 2 GiB switch in NativeRamBlock, so the provider keeps sparse pages instead of building a SeedDisk; that is why the committed image can be this small and still hold a writable /private/var.
- Data persistence is deliberately off: CONFIG\_XNU\_OWNER\_DATA\_UFS=n compiles the Data window out, and patches/xnu/...-pong-ufs-data.patch is not in patches/xnu/series, so the in-tree Data branch never builds.
- install-pong-ufs-data.py still hardcodes Pong geometry \(sda13, 0x413248..0x75a40ea, 454 GiB\) and refuses anything else, so it cannot install the K60's own unixnu partition as written.
- docs/DUAL-SYSTEM.md fixes no size: the only concrete number in the repository is the 32 GiB \[userdata\] window, which the partition plan must match.

### 完成条件

- Host: register, clock, link and SMMU facts match the board inventory. Reads: READ CAPACITY, GPT and the SHNGROOT windows are correct. Root: the configured volume mounts and launchd starts. Persistence: writes survive a reboot inside the allocated Data region.

### 当前范围

- No device log exists for this board: the read path is implemented but unproven, the boot RAM seed is the only writable Data, and the persistent UFS Data window is not even compiled.
- The 32 GiB window is unverified against the real GPT; the scripts and the record disagree about which partition it describes.
- The dual-system partition has not been created, and the third-party TWRP has not been checked for F2FS online shrink or decryption.

### 下一步

- Run partition.py inspect on the unit, then align \[userdata\] first\_lba/last\_lba with the real unixnu GPT entry and capture one PONG\_UFS log with LUN, block size and manifest window counts.

### 证据

- `source`: [DT equality checks for the UFS host, GCC page and SMMU windows, controller power and bus verification, and the declared SMMU ownership limits](https://github.com/mzyxsl/UniXNU-mondrian/blob/76552b88441757defce4080a241c2f0ea7464538/drivers/NativeUfs/NativeUfs.cpp)
- `source`: [GPT parsing with CRC32 over header and entries, UTF-16LE matching of the unixnu partition name, SHNGROOT manifest records and the 0..7 manifest status codes](https://github.com/mzyxsl/UniXNU-mondrian/blob/76552b88441757defce4080a241c2f0ea7464538/drivers/NativeUfs/RootLayout.h)
- `source`: [33,554,432-byte raw APFS image: NXSB at 0x20, volume superblock at 0xa2020 with UUID 6DCCF70A-6FD6-403E-ACED-95313CD7CBB8 at +0xd0 and volname OwnerData at +0x2a0, SHA-256 5fd2f3566e989d11cde74289151888392615a4771e5b616ff5e98ca3b24ffc03](https://github.com/mzyxsl/UniXNU-mondrian/blob/76552b88441757defce4080a241c2f0ea7464538/seed/k60-data-seed.dbr)
- `source`: [dual-system plan: shrink F2FS online, add unixnu at the tail of userdata, keep Android data, with the TWRP prerequisites and the inspect/plan/apply/verify flow](https://github.com/mzyxsl/UniXNU-mondrian/blob/76552b88441757defce4080a241c2f0ea7464538/docs/DUAL-SYSTEM.md)

## 显示 {#display}

`implemented`

### 硬件与依赖

- Panel m11a\_42\_02\_0a: 1440x3200 native canvas, DSC video mode, stride taken from vinfo.v\_rowbytes, refresh reported through the panel driver.
- The firmware must publish an EFI\_GRAPHICS\_OUTPUT\_PROTOCOL surface \(ABL splash framebuffer plus SimpleFbDxe on this port\); DarwinBoot only accepts PixelBlueGreenRedReserved8BitPerColor.
- Userland presentation needs the 20G81 QuartzCore cache layout, which ui\_compat.c pins by address with a slide of base - 0x180000000.

### 配置

- K60\_PANEL\_WIDTH 1440 and K60\_PANEL\_HEIGHT 3200 with the k60\_panel tunable defaulting to 1 \(0210\); the canvas is forced to the panel only when vinfo reports exactly 1440x3200 and fbwidth/fbheight/fbscale are refused.
- kFBDisplayID 1 \(0 means no display\) and Timing/Color ids 1 \(0213\); display services start unless pong\_software\_ui=0 \(0211\).
- XNU\_K60\_ACCEL\_STUB=1 \(default under PONG &amp;&amp; \(DEVELOPMENT \|\| DEBUG\) &amp;&amp; \!SECURE\_KERNEL\) publishes the empty IOAcceleratorES stub with IOAcceleratorStub=true and no MetalPluginName, and accel\_stub=0 disables it at run time \(0212\).

### 操作步骤

- The 0210..0213 display patches are series entries 0209..0213 and are applied in that order; rebuild the kernel and the payload after changing them.
- Boot and read the XNU console for 'K60 DISPLAY: first frame presented \(swap n, WxH canvas ...\)' and inspect the published K60Display dictionary for Stride and RefreshHz.

### 开发经验

- The display stack intentionally starts from the firmware surface: 0210 publishes a K60Display dictionary \(PanelWidth, PanelHeight, CanvasWidth, CanvasHeight, Stride, RefreshHz, Native\) and refuses to scale a non-native canvas, so the first frame is never a stretched picture.
- An empty accelerator keeps clients alive without a GPU: 0212 answers up to 16 scalar outputs plus the structure output, logs the first 24 selectors and advertises IOAcceleratorStub, which is what lets SpringBoard present a software frame before the GPU port is enabled.
- The console has two fixes for the first UI frame: the touch-console patch releases the graphics console after kPEGraphicsMode so vcputc stops painting over the frame, and the console-sink-dedup patch removes duplicate sinks.
- Userland forces the framebuffer format to 'BGRA' \(0x42475241\), caches a null renderer and keeps display readiness, with four QuartzCore hooks at 0x1d586e000/0x18826a418, 0x1d586c7c0/0x1884aa47c, 0x1d586c7c8/0x1882787f4 and 0x1d586dfd8/0x1882df668.
- The 1080x2412 main screen selects PongStatusBarVisualProvider1080 \(a Split1080 subclass\), so the status bar geometry follows the hardware screen, not the 1440x3200 panel canvas.

### 完成条件

- A known frame appears with the correct geometry and colours, the panel reports its native stride and refresh, presentation survives window changes, and backlight control works.

### 当前范围

- No device log of a presented first frame exists in the repository; the area is implemented from source only.
- Backlight control is not implemented on this port; the panel driver only supplies the initial brightness.
- GPU-backed presentation depends on the gpu area and its accelerator stub replacement.

### 下一步

- Boot once and capture 'K60 DISPLAY: first frame presented \(swap 1, 1440x3200 ...\)' together with the K60Display Stride and RefreshHz values, then record it as device evidence.

### 证据

- `source`: [native 1440x3200 canvas, refusal of scaling fields and the K60Display dictionary with panel, canvas, stride and refresh values](https://github.com/mzyxsl/UniXNU-mondrian/blob/76552b88441757defce4080a241c2f0ea7464538/patches/xnu/0210-k60-display-native-canvas.patch)
- `source`: [display id 1 instead of 0, timing/colour ids 1 and the first-frame-presented log line](https://github.com/mzyxsl/UniXNU-mondrian/blob/76552b88441757defce4080a241c2f0ea7464538/patches/xnu/0213-k60-display-first-frame.patch)
- `source`: [IOAcceleratorES stub that zeroes up to 16 scalar outputs plus the structure output, logs 24 selectors and publishes IOAcceleratorStub=true](https://github.com/mzyxsl/UniXNU-mondrian/blob/76552b88441757defce4080a241c2f0ea7464538/patches/xnu/0212-k60-empty-accelerator.patch)

## 输入 {#input}

`planned`

### 硬件与依赖

- Goodix 'Berlin-D' touch controller behind GENI/QUP0 SE4 at 0x990000 with TLMM at 0xf000000, GCC at 0x100000, RSC at 0x17a20000 and cmd-db at 0x80860000; pins 16/17/18/19 are MISO/MOSI/CLK/CS, 21 is INT and 20 is RESET.
- The panel is 1080x2412 in touch coordinates, so the driver scales x and y to 0..65535 against max-x 1080 and max-y 2412.
- Physical keys come from the SPMI PMIC arbiter \(0xc400000 cnfg 0xc42d000, observer 0xc440000, EE 0\) with PON ppid 0x013 and GPIO6 ppid 0x18d.
- The XNU-side code only runs when the boot argument pong\_touch=1 is present and the DT node matches the compiled resources exactly.

### 配置

- pong\_touch=1 enables the driver; touch\_flip 1 mirrors left/right and 2 mirrors top/bottom for the panel orientation.
- The driver publishes /dev/pong-touch \(char, 0444, root:wheel, 512-entry ring\) with struct pong\_touch &\#123;u64 time; u32 type, finger, x, y&\#125; and /dev/pong-buttons on minor 1.
- userland/touch.c publishes virtual HID services: digitizer page 0x0d usage 0x04 and consumer page 0x0c usage 0x01, with key usages 0x30 power, 0xe9 volume up and 0xea volume down.

### 操作步骤

- Add the three patches to patches/xnu/series at their intended positions, rebuild the kernel, repack the payload and boot with pong\_touch=1.
- Read the XNU console for the Berlin-D probe line and the first finger report, then check /dev/pong-touch from the userspace bridge.

### 开发经验

- The driver is complete as source but is not built: pong-touch-console.patch, pong-physical-keys.patch and pong-goodix-resume.patch are absent from patches/xnu/series, so the documented kernel does not contain it. That is why this area stays planned while the firmware keypad path works.
- The resume patch exists because Android or recovery can leave the controller in sleep or gesture mode: it resets, re-probes and clears one report byte before publishing input.
- The GENI engine runs at 4 MHz, mode 0, cs0, 8-bit MSB first with a 200 ms deadline and a polled FIFO, and every clock and power vote is a direct register write \(GCC vote 0x62008 bits 6,7,8,9,14; RPMh ldoc12 1800 mV then ldoc3 2700 mV\).
- The same touch patch carries the only real RPMh regulator writer in the tree, so enabling touch would also give the first working regulator votes for the panel and controller rails.
- The firmware keypad \(K60KeypadDeviceLib over SPMI PON/GPIO\) already works in the UniXNU menu, which is why menu navigation is verified while XNU input is not.

### 完成条件

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive, and the power and volume keys produce the expected HID reports.

### 当前范围

- Nothing in this area is compiled by the current series, so there is no build or device result to report.
- No captured report proves that the Goodix controller answers on this unit.

### 下一步

- Add the three input patches to the series, boot with pong\_touch=1 and capture the Berlin-D probe line plus one finger report as device evidence.

### 证据

- `source`: [Goodix Berlin-D driver with GENI SPI, TLMM pin muxing, RPMh rail votes, the report parser and the /dev/pong-touch ring](https://github.com/mzyxsl/UniXNU-mondrian/blob/76552b88441757defce4080a241c2f0ea7464538/patches/xnu/zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz-pong-touch-console.patch)
- `source`: [SPMI PMIC arbiter reads of PON and GPIO6 with a 16 ms poll, publishing /dev/pong-buttons](https://github.com/mzyxsl/UniXNU-mondrian/blob/76552b88441757defce4080a241c2f0ea7464538/patches/xnu/zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz-pong-physical-keys.patch)

## GPU {#gpu}

`implemented`

### 硬件与依赖

- Adreno 730 v3 \(chip id 0x07030002, Mesa FD725 / A7XX Gen1\) with 2 MiB GMEM, HighestBankBit 16 and a 64x32 tile.
- Windows: GPU core 0x03d00000, GMU 0x03d68000, RSCC 0x03d50000, cx\_misc 0x0b290000, PDC 0x03d9e000, GPUCC 0x03d90000, GPU SMMU 0x03da0000 and AO 0x03d40000; GCC 0x100000 and RSC 0x17a20000.
- Firmware blobs are not stored here: gmu\_gen70000.bin, a730\_sqe.fw and a730\_zap.mdt/.b01/.b02 are supplied at build time, and ZAP uses PAS id 13 at 0x8b91a000.
- SPI 332 \(GPU\), 336 \(HFI\) and 337 \(GMU\) are the only interrupts the CP attaches today.

### 配置

- CONFIG\_XNU\_PONG\_ADRENO\_PLATFORM=n and CONFIG\_XNU\_NATIVE\_ADRENO=n in the committed defconfig: the GPU path is implemented but switched off until the display stack is verified without it.
- pong\_adreno\_start=1 enables the bring-up entry; ASIDs are 1 for the GMU and 2 for the GPU with shared\_asid 1, ignore\_top\_byte 1 and polled\_faults 1.
- Metal frontend: 20G81-only gate on sysctl kern.osversion, \_MTLDevice instance size 528, connection types 0x4147 and 0x4148, abi\_version 1 and 16 native methods.

### 操作步骤

- scripts/build-pong-adreno-platform.py --output-dir &lt;dir&gt; --firmware-dir &lt;dir&gt; regenerates the GEN7 register header, compiles the objects and embeds the five firmware blobs into libPongAdrenoPlatform.a; the report sets hardware\_qualified=false.
- scripts/build-pong-turnip.py and scripts/build-pong-metal-bridge.py/--plugin.py produce libvulkan\_freedreno.dylib and the PongAdrenoMetal bundle for the native Metal path.
- Boot with pong\_adreno\_start=1 and read the 'PONG ADRENO' records for the furthest passing phase.

### 开发经验

- The GPU port reuses Nothing Phone \(2\) SM8475 work: the register windows, GMU boot config, HFI table and CP firmware names are the Pong values, and the only K60-specific change is the SoC timer offsets 0x16220/0x16224.
- GMU bring-up requires CM3 held in reset \(GEN7\_GMU\_CM3\_SYSRESET == 1\), CM3\_CFG 0x4052, AHB\_FENCE\_RANGE\_0 0x80c808a0 and a firmware-ready poll of 0x1ff == 0x100 before HFI power commands 4, 3, 14 and 30 and the START10 handshake.
- The GPU SMMU is SMMUv2 LPAE with 4 KiB leaves and ACTLR 0x32b; it leases SID0\|0x400 and SID1\|0x401 in one context, excludes the secure SID2\|0x402 and routes the GMU on SID5\|0x405.
- The Metal shim is gated on IOS16.6.1: it requires the 528-byte \_MTLDevice, advertises abi\_version 1 with the exact chip and GMEM values and refuses other OS builds, and configs/pong-iogpu-20G81.json pins the 20G81 IOAcceleratorES metaclass and prelink base 0xfffffff004fbc000.
- The two metal2vulkan patches add the IOS16\_6\_1 level with a 7x64-bit MTLPixelFormatGetInfo ABI and optional surface row padding \(PONG\_IOSURFACE\_PADDING=1\); the two Mesa patches cap the heap at va\_size and retry allocations after a 250 ms fence wait.
- A link hazard sits behind the switch: PongAdrenoPlatform.cpp calls pong\_ramoops\_diagnostic\_write, which is defined only in the unlisted settings-pmsg patch, so enabling CONFIG\_XNU\_PONG\_ADRENO\_PLATFORM without also adding that patch cannot link.
- Nothing in the tree has produced a GPU frame: README.md records only that the v98 phone reached the iOS main UI with Adreno and Metal unconfirmed.

### 完成条件

- GPU submissions complete, mapping and fence handling are correct, a known image renders, and the selected Metal client presents it.

### 当前范围

- Switched off in the committed defconfig, and no device log records which bring-up phase was reached last.
- The firmware blobs are supplied externally with image\_verification skipped, so it is unknown whether they match the unit.
- The scanout path needs the display area verified first.

### 下一步

- Boot once with pong\_adreno\_start=1, read the 'PONG ADRENO: &lt;phase&gt; result=&lt;n&gt;' records and report the last passing phase, in particular whether 'CP ready; authenticated nonsecure fence' appears.

### 证据

- `source`: [CM3 reset gate, GMU boot config, firmware-ready mask, HFI power sequence and the START10 handshake after OOB\_GPU](https://github.com/mzyxsl/UniXNU-mondrian/blob/76552b88441757defce4080a241c2f0ea7464538/drivers/PongAdreno/PongAdrenoGmu.c)
- `source`: [register windows, GMU/SMMU/ASID setup, parent ARC votes through APSS DRV2 TCS3 and the pong\_adreno\_start entry](https://github.com/mzyxsl/UniXNU-mondrian/blob/76552b88441757defce4080a241c2f0ea7464538/drivers/PongAdreno/PongAdrenoPlatform.cpp)
- `source`: [20G81 IOAcceleratorES constants: instance 136 bytes, 168 virtual entries, metaclass 0xfffffff007a575c8, prelink base 0xfffffff004fbc000](https://github.com/mzyxsl/UniXNU-mondrian/blob/76552b88441757defce4080a241c2f0ea7464538/configs/pong-iogpu-20G81.json)

## 网络 {#network}

`planned`

### 硬件与依赖

- The K60 carries a WCN685x combo on PCIe with MHI firmware loading; neither the attachment nor the firmware partition has been enumerated for this port.
- A driver needs the PCIe or MHI window, the firmware partition name, its own SMMU stream and a matching OS-facing service such as the IO80211 family.

### 配置

- No configuration entry exists yet: neither board.toml \[components\] nor configs/mondrian\_defconfig selects a network component.

### 操作步骤

- Read the vendor DT and board files for the WCN685x node, then pick an existing component or plan a new driver before writing code.

### 开发经验

- Nothing exists in the tree for this area: no driver, patch, script or DTS node mentions Wi-Fi, WCN or MHI apart from the userspace About screen, which states that the port has no baseband/WLAN/BT transport.

### 完成条件

- Scanning, association, address configuration and sustained receive/transmit traffic pass with the selected firmware.

### 当前范围

- Scope only: the transport is not addressed, so no measurement is possible yet.

### 下一步

- Enumerate the WCN685x attachment \(PCIe or MHI\) and its firmware partition from the vendor DT, and record the window, interrupt and SMMU stream in this area.

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`planned`

### 硬件与依赖

- Audio needs the ADSP remoteproc reserved-memory range and PAS id, the GPR/GLink SMEM queues, the codec and its XO-derived clocks, and the routing table the OS expects for a J120 identity.
- The OS profile already provides the J120 AP identity that the audio server keys its routing database on, so the identity side is prepared.

### 配置

- No configuration entry exists yet: no component, defconfig option or DTS node covers ADSP, GPR or a codec.

### 操作步骤

- Read the ADSP and codec nodes from the vendor DT, then follow the DSP/audio guide before selecting or writing a driver.

### 开发经验

- Nothing exists in the tree for this area: the DTS has no ADSP node and no driver, patch or script mentions ADSP, GPR or a codec.
- The OS profile's product audio node \(wireless-splitter 1\) is the one audio-related artefact in the repository, and it is an ADT property from the OS side, not a driver.

### 完成条件

- Each declared route carries the selected audio format through playback or capture and handles start/stop correctly.

### 当前范围

- Scope only: no ADSP window, PAS id or codec has been recorded for this board.

### 下一步

- Record the ADSP reserved-memory range, its PAS id and the GPR/GLink SMEM addresses from the live device tree, which any future driver must use.

### 证据

按下一步操作收集证据。

## 电源 {#power}

`planned`

### 硬件与依赖

- PMIC and RPMh resources: APSS RSC at 0x17a20000 with TCS blocks at +0xd00, the command-db at 0x80860000 and the SPMI arbiter at 0xc400000 that the firmware keypad already drives.
- Battery and charger readings need the PMIC ADC channels and a fuel gauge service; neither has been enumerated here.

### 配置

- CONFIG\_XNU\_SHENG\_PMGR=n in the committed defconfig, so the single PMGR boot hook is compiled out.
- No battery, charger or regulator component is selected in board.toml \[components\].

### 操作步骤

- Follow the DSP/power guide: enumerate PMIC and RPMh resources, then enable the boot hook and the parent votes before claiming any state transition.

### 开发经验

- The only power code that exists is GPU-side: PongAdrenoPlatform.cpp votes the GPU parent corner through APSS DRV2 TCS3 and serialises the 58-word PERF and 159-word BW payloads from the command-db, and it explicitly notes that no generic RPMh driver is linked.
- patches/xnu/...-sheng-platform-power.patch is a 15-line hook that calls sheng\_pmgr\_run\(\) after bsd\_bufferinit\(\); the function is not defined in this repository and CONFIG\_XNU\_SHENG\_PMGR=n keeps the call out of the build.
- The only real RPMh regulator writer lives inside the touch patch \(pm8350c ldoc12 1800 mV then ldoc3 2700 mV\), which is not in the series; powering the panel and touch rails therefore depends on the input area landing first.
- Resource accounting is suppressed rather than implemented: the boot argument disable\_exc\_resource=1 stops the wakeups and disk-write monitors from reaching exception\_triage\(\), because on this board the services that would answer those exceptions are still missing and watchdogd was killed for a FATAL wakeups violation it could not answer. Removing the argument is the first power-side milestone.

### 完成条件

- Declared power controls and battery readings match observations, and each claimed sleep or resume transition restores its dependent peripherals.

### 当前范围

- No PMIC, charger, battery or RPMh aggregator exists; the GPU parent votes are the only implemented part and they are unproven on hardware, and resource accounting is switched off rather than provided.

### 下一步

- Capture the 'parent ARC votes acknowledged' record from PongAdrenoPlatform.cpp on a real boot, which would be the first hardware evidence for the RPMh path.
- Drop disable\_exc\_resource=1 once a service answers the wakeups monitor, and show watchdogd surviving without the suppression.

### 证据

- `source`: [APSS DRV2 TCS3 parent-corner vote with issue/completion message IDs, plus the statement that no generic RPMh driver is linked](https://github.com/mzyxsl/UniXNU-mondrian/blob/76552b88441757defce4080a241c2f0ea7464538/drivers/PongAdreno/PongAdrenoPlatform.cpp)

## 镜像组装 {#packaging}

`host-verified`

组件: `XnuPrelink`.

### 硬件与依赖

- XNU 8796.141.3 / Darwin 22.6.0 with the 4 KiB page configuration, target DEVELOPMENT\_ARM64\_PONG, and the 20G81 kernelcache \(SHA-256 d260defc\) as the prelink input.
- The prelink needs the XnuPrelink kit, the 32 OS-profile roots, the slide and the early-security-init address; the device preflight installs the auto-slide wrapper over the kit entry point.
- The payload needs the 20G81 trust cache bundle, the committed Data seed seed/k60-data-seed.dbr and, when a board requires a platform seed, --unique-chip-id.
- The boot image needs the firmware FD, the firmware DTB from uefi-mondrian and the payload FAT volume.

### 配置

- \[kernel.prelink\] from the OS profile: tool kits/XnuPrelink/emit\_prelink.py, kernel build/xnu/ios-obj/DEVELOPMENT\_ARM64\_PONG/mach.development.pong.unstripped, slide 0 \(the wrapper derives -0xb9c000\), 32 roots and kernelcache\_sha256 d260defc.
- \[payload\] volume UNIXNU, size\_mib 192, loader firmware, dram\_size 0x300000000, timeout 5, tools true and kernel\_args -v native-ufs=1 pong\_allow\_unauthenticated\_root=1 debug=0x144 cs\_enforcement\_disable=1 pong\_software\_keybag=1 disable\_exc\_resource=1.
- \[payload.adt\] root\_match\_volume\_uuid C5DAF029-2070-4F68-B3CC-1D1320344CF0 is the only board override; the rest of the ADT identity comes from the OS profile. packed\_data\_ramdisk stays unset, so the raw APFS seed goes through --data-ramdisk.

### 操作步骤

- ./unixnu build kernel -D ../UniXNU-mondrian, then ./unixnu build payload --trust-cache prebuilt/20G81-trustcache.bundle --data-ramdisk seed/k60-data-seed.dbr and ./unixnu bootimg.
- Without macOS: python3 scripts/k60-prelink-local.py --kernel mach.development.pong.unstripped --prelinked out/ipsw/20G81/kernelcache.decompressed --output kernel.macho; the script reads \[kernel.prelink\] from the OS profile and lets board.toml override it.
- python3 scripts/build-bootimg.py --ramdisk &lt;payload.ramdisk&gt; --output-dir &lt;dir&gt; --fd &lt;SILICIUM\_UEFI.fd&gt; packs and self-checks a v4 boot image without a device.
- Assemble the userspace data image with python3 userland/build.py prepare\|apply\|finish, which compiles with xcrun for arm64-apple-ios16.6.1 and packs DBRDISK1.

### 开发经验

- The kernel links and prelinks on macOS CI: run 40650877574 produced 54,419,456 bytes at slide -0xb9c000 with lowest component extent 0xfffffff004426600. README.md still showed 54,349,824 bytes for the earlier round, 69,632 bytes less; this record keeps the newer size.
- The format-2 prelink lives in the OS profile, not in board.toml: k60-prelink-local.py used to read only board.toml and therefore failed on this device. It now merges the profile table and lets a board \[kernel.prelink\] override individual keys.
- The profile keeps slide = "0" on purpose: the K60 \_\_DATA is 0x150000 against 0xb0000 on 20G81, so the components do not fit at slide 0 and the wrapper derives -0xb9c000 from the native segment table instead.
- The ADT generator refuses a platform seed without \[payload.adt\] chip\_id and refuses more than one memory range, so both the seed path and the 16 GiB multi-bank unit need a board decision before payload packing succeeds.
- Two boot arguments carry bring-up decisions rather than tuning. pong\_software\_keybag=1 selects the volatile no-passcode keybag from the software-keybag patch, because this board has no SEP and mkbinit otherwise forces a recovery-mode reboot. disable\_exc\_resource=1 keeps the wakeups and disk-write monitors from reaching exception\_triage\(\) while the services that would answer them are still missing.
- scripts/build-bootimg.py and build-native-bootimg-local.py both record hardware\_tested false: they verify structure and corruption controls but never claim a boot.
- The userland build pins 20G81 QuartzCore cache addresses, so it is tied to this OS profile and must be re-derived for another build.

### 完成条件

- Kernel and prelink succeed, the payload contains every declared input with 4 KiB alignment and a non-zero ramdisk\_bytes, and the boot image matches the bootloader format and size limit.

### 当前范围

- Only the kernel step is host-verified; payload and boot image have no recorded run for this board.
- The prelink helper needs a core checkout and a local XnuPrelink kit, neither present in the repository.
- The ADT platform-seed path needs \[payload.adt\] chip\_id, which is intentionally not set until the seed policy is decided.

### 下一步

- Run build payload and bootimg once with the trust cache and the Data seed, record ramdisk\_bytes from boot.json and the payload hashes, and promote this area to device-verified after one fastboot boot.

### 证据

- `host`: [Build kernel succeeded on macOS from this revision: prelink slide -0xb9c000, 54419456 bytes, lowest component extent 0xfffffff004426600](https://github.com/Emilelu/UniXNU/actions/runs/40650877574)
  Command: <code>./unixnu build kernel -D ../UniXNU-mondrian</code>. Revision: `6a10bf5e42ecfad7eed2789cc091287d31009623`.
- `source`: [prelink emitter that writes \_\_PRELINK\_INFO after the largest extent, records \_PrelinkKCID from kernel plus original and refuses to overwrite an existing output](https://github.com/mzyxsl/UniXNU-mondrian/blob/76552b88441757defce4080a241c2f0ea7464538/kits/NativePrelink/emit_prelink.py)
- `source`: [local prelink that merges \[kernel.prelink\] from the OS profile with the board override and runs the auto-slide wrapper](https://github.com/mzyxsl/UniXNU-mondrian/blob/76552b88441757defce4080a241c2f0ea7464538/scripts/k60-prelink-local.py)

## 诊断 {#diagnostics}

`planned`

### 硬件与依赖

- Firmware log channels: the UniXNU menu scans 4 MiB Advanced Logger output as QR frames, and the serial port carries UNIXNU: and DARWINBOOT: lines when a UART is available.
- Kernel log channels: IOLog plus the Pong ramoops console mirror at physical 0xA7000000 \(2 MiB with a 12-byte 'DBGC' header recording signature, start and size\), which the in-series patch provides. The second 2 MiB is the pmsg zone, and the helper pong\_ramoops\_diagnostic\_write that writes it exists only in the unlisted settings-pmsg patch.
- Checkpoint sources: the green-bar trampoline, the HANDOFF stage lines and the PongProbeRecord slot/state pairs.

### 配置

- CONFIG\_XNU\_PONG\_RAMOOPS\_CONSOLE=y, CONFIG\_XNU\_PONG\_VOLATILE\_PANIC\_LOG=y, CONFIG\_XNU\_PONG\_APFS\_DEBUG=y and CONFIG\_XNU\_PONG\_EARLY\_TRACE=n in the committed defconfig.
- Kernel arguments currently carry debug=0x144 and native-ufs=1; the documented first-boot set is -v keepsyms=1 debug=0x14e cpus=1.
- USB logging is designed but not wired: 40-byte frame header magic PNGLG001 v1, 1 MiB queue, 16 KiB batches and a 20 ms wait, with no usblog= argument in any code path.

### 操作步骤

- python3 scripts/audit-pong-adt.py &lt;adt&gt; --report &lt;json&gt; --boot-manifest &lt;json&gt; replays 14 negative ADT cases plus a byte-exact round trip.
- python3 scripts/verify-firmware.py --output-dir &lt;build&gt; checks the FV header, module GUIDs and PE images; scripts/build-probe-stage.sh runs the whole host-side chain without adb or fastboot.
- python3 scripts/check-porting-paths.py --device . checks this record offline: identity, required areas, evidence shape, component coverage, path ownership and series references.

### 开发经验

- The host-side audit tooling is real and reusable: audit-pong-adt.py rejects known-bad loader contracts, verify-firmware.py checks four FFS GUIDs and the PE machine type, and the window probe asserts the handoff contract with PASS/FAIL output.
- Several harnesses still point outside the repository: check-pong-probe-policy.py reads /Volumes/PongDev, build-window-probe-local.py defaults to that driver directory, and test-window-qemu.py expects UniXNU-pong and a qemu-run.py from the core checkout. They cannot run from a clean clone.
- The record previously attributed globs that match no file \(scripts/read-\*, scripts/probe-\*\) and named a package/Kit.toml that does not exist; the patterns now match the scripts that are actually here.
- No captured log is stored in the repository, so every hardware checkpoint above is described from the code that would print it, not from a transcript.

### 完成条件

- Each claimed milestone has a reproducible command, a matching source and image revision, and an accessible result.

### 当前范围

- There is no on-device transcript for any milestone, and the USB log path is still a design document.
- The host harnesses that depend on /Volumes/PongDev or on a Pong-layout checkout cannot be reproduced from a clean clone.

### 下一步

- Capture one fastboot boot of the window probe and publish the serial or QR transcript with the firmware and payload revisions, which would give the first device evidence in this record.

### 证据

- `source`: [byte-exact ADT round trip plus 14 rejected contracts and manifest mismatches, printing 'ADT PASS; N invalid-input cases rejected'](https://github.com/mzyxsl/UniXNU-mondrian/blob/76552b88441757defce4080a241c2f0ea7464538/scripts/audit-pong-adt.py)
- `source`: [FV header and checksum, UniXNU/UniXNUDxe/DarwinBoot/PongBootMemoryDxe GUIDs and ARM64 PE machine checks written to firmware-verification.json](https://github.com/mzyxsl/UniXNU-mondrian/blob/76552b88441757defce4080a241c2f0ea7464538/scripts/verify-firmware.py)

</div>
