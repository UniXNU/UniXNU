# Redmi Note 12 Turbo / POCO F5 \(marble\), Qualcomm SM7475 \(Snapdragon 7+ Gen 2\) \(MiLacy\)

[MiLacy/UniXNU-marble](https://github.com/MiLacy/UniXNU-marble)

<div v-pre>

Format-2 first-console port for the Redmi Note 12 Turbo / POCO F5 \(SM7475\). The UEFI image and UniXNU menu are buildable; XNU kernel entry needs user-supplied IPSW inputs; system entry is a documented later stage.

源记录: [porting.toml](https://github.com/MiLacy/UniXNU-marble/blob/78f4e7bf00e88129f8b6ef5680d81770d386832d/porting.toml), `78f4e7bf00e88129f8b6ef5680d81770d386832d`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `implemented` |
| [固件与启动](#firmware) | `device-verified` |
| [CPU 与中断](#cpu) | `planned` |
| [内存与 DMA](#memory) | `planned` |
| [存储与根卷](#storage) | `device-verified` |
| [显示](#display) | `planned` |
| [输入](#input) | `planned` |
| [GPU](#gpu) | `not-applicable` |
| [网络](#network) | `not-applicable` |
| [音频](#audio) | `not-applicable` |
| [电源](#power) | `planned` |
| [镜像组装](#packaging) | `device-verified` |
| [诊断](#diagnostics) | `planned` |

## 配置 {#configuration}

`implemented`

### 硬件与依赖

- Board identity, SM7475 SoC profile, iPadOS 17.7.11 OS profile, component selection and external source pins.

### 配置

- board.toml selects soc\_source=sm7475, kit=marble and the iPadOS 17.7.11 profile. The SM7475 DTSI and SMP/cluster patches are pinned through feeds.toml from the sibling UniXNU-sm7475-common repository.

### 操作步骤

- Run ./unixnu defconfig marble\_defconfig, fetch, status and tree from the main UniXNU checkout; inspect the resolved sources and output path.

### 开发经验

- The legacy ios-port-marble tree is an iOS 16 / XNU 8796 / 16 KiB-page shim port; this repository is a source-backed Format-2 migration to the upstream iPadOS 17 / XNU 10063 / 4 KiB UEFI profile. The subsystem-by-subsystem mapping and the deliberately unported audio/GPU/touch work are recorded in docs/MIGRATION.md.
- The common ADT generator now emits AAPL,phandle instead of the FDT spelling phandle. XNU's AddPHandle/IODTFindInterruptParent look up AAPL,phandle; without the rename the UFS interrupt-parent resolved to NULL and IODTGetICellCounts\(\) data-aborted at PC 0xfffffff0078ec2d4 \(ESR 0x96000005, FAR 0\).
- The board is SM7475-AB \(Cape\), not SM8550. The CPU topology is 4x A510, 3x A710 and 1x X2, so the shared DTSI differs from SM8550 even though GIC and UFS addresses match.
- The apps-SMMU stream from the vendor DT is 0xE0, while upstream ShengUfs programs 0x60. The local drivers/ShengUfs fork adds native-ufs-stream with a 0xE0 default.
- The stock marble UEFI port provides Resources/DTBs/marble.dtb. The port adds Resources/DTBs/marble-unixnu.dtb with the stale /chosen initrd properties removed, keeping the splash region, so the bootloader can publish the actual payload range and the board does not add a duplicate \[\[bootimg.dtb\_node\]\].

### 完成条件

- All source pins resolve; status shows the intended SoC, OS and device layers; the device tree compiles.

### 当前范围

- The SM7475 shared repository is published at https://github.com/MiLacy/UniXNU-sm7475-common and pinned to fc78deda27304248186fec2320c5678c45d8e431.

### 下一步

- Run the status check on a clean clone of the published repositories.

### 证据

- `source`: [Board identity, component selection, firmware paths and payload inputs.](https://github.com/MiLacy/UniXNU-marble/blob/78f4e7bf00e88129f8b6ef5680d81770d386832d/board.toml)
- `source`: [Board memory, splash reservation and CPU cluster tags.](https://github.com/MiLacy/UniXNU-marble/blob/78f4e7bf00e88129f8b6ef5680d81770d386832d/dts/marble.dts)
- `source`: [First-console kernel configuration.](https://github.com/MiLacy/UniXNU-marble/blob/78f4e7bf00e88129f8b6ef5680d81770d386832d/configs/marble_defconfig)
- `source`: [Source-backed hardware inventory.](https://github.com/MiLacy/UniXNU-marble/blob/78f4e7bf00e88129f8b6ef5680d81770d386832d/docs/HARDWARE.md)

## 固件与启动 {#firmware}

`device-verified`

组件: `DarwinBoot`.

### 硬件与依赖

- Mu-Silicium-marble Platforms/Xiaomi/marblePkg, Resources/Configs/marble.toml, the stock Resources/DTBs/marble.dtb and the derived Resources/DTBs/marble-unixnu.dtb, and the four Mu edk2 patches.

### 配置

- \[firmware\] selects config=marble, the marble DSC, the 3 MiB FD path and the four Mu patches. UniXNU, UniXNUDxe, UniXNURamDiskDxe and DarwinBoot are listed in the DSC and DXE.inc.

### 操作步骤

- Build the firmware with ./unixnu build firmware, then pack an empty-ramdisk boot.img with the marble DTB and boot it with fastboot boot.

### 开发经验

- The stock marble DSC already includes DiskIoDxe, PartitionDxe, Fat and EnglishDxe; the UniXNU integration adds the four modules and the UniXNULib, FdtLib and HobLib mappings.
- The FD is 3 MiB at 0xA7100000, the same window the stock Mu-Silicium marble port uses.
- Host build 2026-11-01 from upstream fc9e410d plus integration d1f18525: the DEBUG FD is exactly 0x300000 bytes \(one build SHA-256 9a0a727f136cd7e97d4a6aaf43adee6517f637b122f09e444d9db090c6a51f2a; a later rebuild produced 7bce194a... because EDK II embeds a timestamp\). The build log lists UniXNU.efi, UniXNUDxe.efi, UniXNURamDiskDxe.efi and DarwinBoot.efi, and FVMAIN used 99% of its space.
- The stock BootShim header did not describe the complete shim plus payload; bootimg rejected the image. BootShim.S now writes \`FD\_SIZE + \_Payload - \_Head\` as the ARM64 image size.
- The marble SEC did not save the previous stage's x0 or build gSiliciumEntryArgHobGuid, so UniXNURamDiskDxe could not publish the payload volume and the menu reported no boot entry found. ModuleEntryPoint.S now keeps x0 in x19 and passes it as the third CEntryPoint argument; Sec.c builds the HOB after InitializeMemory. The GUID is present in the FD. DarwinBoot also detects EL2 and returns to EL1h \(SPSR\_EL2/ELR\_EL2 eret, HCR\_EL2.RW=1, CNTHCTL\_EL2=3, CNTVOFF\_EL2=0, CPTR\_EL2=0, CPACR\_EL1 FPEN\) as a defensive guard. The observed fiq\_context\_init panic was already at EL1 and persisted with that guard; the actual cause is Gunyah trapping the EL1 \`CNTP\_CTL\_EL0\` write as UNDEF \(instr d51be228, PC 0xfffffff0074204fc\), fixed by the device kernel patch marble-virtual-timer-only.patch.
- Resources/DTBs/marble-unixnu.dtb removes the stock /chosen linux,initrd-start/end values so the bootloader's real payload range is the only one the driver sees.

### 完成条件

- Firmware volume builds at the configured size and contains UniXNU, UniXNUDxe, UniXNURamDiskDxe and DarwinBoot; the menu appears on the phone.

### 当前范围

- The DEBUG FVMAIN is 99% full; a later module needs RELEASE or removal of an unused vendor driver. The console image deliberately has no UFS or root device.

### 下一步

- Build the unverified UFS root image, then decide whether to flash userdata for the root stage.

### 证据

- `host`: [DEBUG FD built at 0x300000 bytes from upstream fc9e410d plus the integration patch; build log and FVMAIN.inf list UniXNU.efi, UniXNUDxe.efi, UniXNURamDiskDxe.efi and DarwinBoot.efi; the SEC entry-argument HOB GUID is present in Sec.efi.](https://github.com/MiLacy/UniXNU-marble/blob/78f4e7bf00e88129f8b6ef5680d81770d386832d/firmware/README.md)
  Command: <code>./unixnu build firmware -D ../UniXNU-marble --uefi ../uefi-marble --edk2 ../uefi-marble/Mu_Basecore</code>. Revision: `d1f18525135544426fae87c9497155df7f9e1fc7`.
- `device`: [POCO F5 / Redmi Note 12 Turbo booted the 3 MiB FD, UniXNU and DarwinBoot into XNU. The console kernel then reached IOKitBSDInit.cpp:984 with \`Failed to mount root device\` \(frames IOFindBSDRoot+0xc88, bsd\_init+0x6e8\), which is the expected no-root stop. Image SHA-256 d169cb16d8d9bb25b6184bd544ce0d831a6f01499f037ab1424972b67b696b7e.](https://github.com/MiLacy/UniXNU-marble/blob/78f4e7bf00e88129f8b6ef5680d81770d386832d/docs/REAL-DEVICE-TESTS.md)
  Command: <code>fastboot boot artifacts/marble-xnu-console/boot.img</code>. Revision: `0a6717c3212147f65c1b59a173dfd1565e9c5adb`.

## CPU 与中断 {#cpu}

`planned`

组件: `ArmDTPlatform`, `ArmCpu`.

### 硬件与依赖

- Eight CPU affinities, PSCI smc, GIC distributor 0x17100000/0x10000, redistributors 0x17180000/0x200000, stride 0x40000, 19.2 MHz timer.

### 配置

- sm7475.dtsi declares cpu0-7, the GIC and the PSCI node. marble.dts tags cpu0-3 E and cpu4-7 P. The SoC patch series adds MAX\_CPUS=8, MAX\_CPU\_CLUSTERS=2 and the Edge scheduler policy.

### 操作步骤

- Apply the SoC patch series, build the kernel and payload, boot the phone and read the ArmCpu SMP counters and per-CPU work rows.

### 开发经验

- The vendored stock DT reports Affinity1 core numbers 0x000 through 0x700, so the native-smp-secondary patch is required for secondary CPUs.
- The UFS interrupt specifier now resolves to the GIC: the ADT GIC node carries AAPL,phandle=1 and ufshc interrupt-parent=1. IODTMapInterruptsSharing no longer calls IODTGetICellCounts\(NULL\).
- Gunyah traps the EL1 CNTP\_CTL\_EL0 write as UNDEF \(device witness PC 0xfffffff0074204fc, instruction d51be228, @sleh.c:1045\). marble-virtual-timer-only.patch keeps CNTV enabled and removes the CNTP write, matching the legacy marble port. The kernel now passes fiq\_context\_init.
- The E/P flags must not be enabled without the AMP patch; MAX\_CPU\_CLUSTERS would remain 1 and the topology parser would write past its array.

### 完成条件

- Every enabled CPU reaches its entry checkpoint; timer interrupts and IPIs work on each core; the P cluster carries the UI workload.

### 当前范围

- Only the boot CPU was enabled in the verified console image \(cpus=1\). SMP, IPIs and the P cluster are still untested.

### 下一步

- Enable the remaining CPUs and IPI paths, then record per-core counters.

### 证据

- `source`: [CPU, GIC and timer values with their vendor-DT source.](https://github.com/MiLacy/UniXNU-marble/blob/78f4e7bf00e88129f8b6ef5680d81770d386832d/docs/HARDWARE.md)
- `source`: [E/P cluster tags and enabled UFS nodes.](https://github.com/MiLacy/UniXNU-marble/blob/78f4e7bf00e88129f8b6ef5680d81770d386832d/dts/marble.dts)

## 内存与 DMA {#memory}

`planned`

### 硬件与依赖

- UEFI memory map, stock DDR banks, PIL/display/TZ reservations and the firmware FD window at 0xA7100000.

### 配置

- marble.dts declares a 2 GiB handoff memory node at 0x80000000 and the 0x2B00000 splash reservation at 0xB8000000. payload.adt requests a 4 GiB owned window.

### 操作步骤

- Compare the DTS handoff, the UEFI memory map and the DarwinBoot free-memory runs; adjust owned\_memory\_size only after a real-device NO WINDOW or memory-pressure result.

### 开发经验

- The stock 12 GiB DTB has six DDR banks, but only the low region is a contiguous 2 GiB handoff. The owned window is separate and is placed by DarwinBoot in free memory.
- The memory map reserves 0x1C200000 bytes of PIL, 0x2B00000 display/Demura, 0x10000000 kernel, 0x5000000 OEM VM and 0x20000000 MTE space below 4 GiB.

### 完成条件

- Memory reservations reconcile with the actual UEFI map; every enabled DMA engine stays inside a mapped range.

### 当前范围

- No device memory reading exists; owned\_memory\_size is a conservative 4 GiB choice, not a measured value.

### 下一步

- Read the DarwinBoot window and the kernel RAM/free/available counters on the phone before increasing the window.

### 证据

- `source`: [Memory map and reservation table.](https://github.com/MiLacy/UniXNU-marble/blob/78f4e7bf00e88129f8b6ef5680d81770d386832d/docs/HARDWARE.md)

## 存储与根卷 {#storage}

`device-verified`

组件: `SoftwareAES`, `ShengUfs`, `VirtioMmioBlock`, `RamBlock`, `VerifiedRoot`, `AppleKeyStoreState`.

### 硬件与依赖

- UFS host 0x1d84000/0x3000, PHY 0x1d80000/0x2000, apps SMMU 0x15000000, UFS stream 0xE0, GCC 0x100000, userdata GPT.

### 配置

- The local ShengUfs fork adds native-ufs-stream with a 0xE0 default, native-ufs-smmu-takeover and NATIVE\_UFS\_PROBE\_ONLY guards. marble\_defconfig selects CONFIG\_XNU\_NATIVE\_UFS and CONFIG\_XNU\_NATIVE\_UFS\_FULL; the full build links NativeUfsBlock against the original IOBlockStorageDevice ABI through scripts/data/native-storage-original-bindings.S and scripts/build-storage-bindings.py. The verified-root and Data chains stay off.

### 操作步骤

- Build the full UFS component with XNU\_NATIVE\_UFS\_FULL=1, boot with native-ufs-stream=0xe0, native-ufs-smmu-takeover=1 and native-ufs-root=1, then read the root-matching line and launchd/authentication result.

### 开发经验

- 2026-11-01 verified image: macOS GitHub artifact verified-root-data \(OS policy 04769D26..., SystemOS 8846FE78..., Data seed 6f984785..., owner public key\) was used on Linux to build libVerifiedRootProbe.a and a verified kernel with OS/SystemOS policies and Data. kernel.macho SHA-256 46873b37e857dd9f5e8ec58a1f6e01b5bc0f58af2f38e4c02edfae3821b478ed; payload cdf90334d3076338ff58ed5f1791d420d9b7e387d646779227d9db21903b8c89; boot.img 23592cd6ad4b3b2db96c6c825605dc0bde5e562dc0e9ddc298ba3c3493af9e4d. No device test yet. The macOS-15 workflow run failed at seed-data-grow.py \(No APFS container found on the attached seed\); the image uses the previous successful artifact.
- 2026-11-01 unverified tail-root build: marble-root\_defconfig enables ShengUfs and links NativeUfsBlock without the verified-root bundle; kernel.macho SHA-256 b1ae430bf1105e433f780ae88c762ddfcb2ab39d96963da4a98ae174f6105918, payload SHA-256 531158dfcc33aed5797ad3bbd9f5c74d4fb16236de39c4bb562f5bee7047a2db, boot.img SHA-256 ce31ab2fa3a8bdf7109ce59c0dc6f653e3fcf05d776b869450c1142538caa611. The userdata image is 9,382,658,048 bytes \(SHA-256 fd43ee7035ce185ce4215ac93fdc006fd784a54b3b7442e21457c226cbe03093\) and is written only at LBA 59589627..61880314, leaving Android ext4 data at the start intact. The payload opts in with native-ufs-allow-unverified=1 and root-unverified=1.
- The first launchd mount phase exited 66 with \`failed to get boot-manifest-hash\`; the unverified kernel did not publish \`/chosen/boot-manifest-hash\`. board.toml now supplies a development-only 48-byte value \(SHA-384 of \`MarbleBringup.BootSet.v1\\0\`\) in \[adt.chosen.bytes\], which the common ADT generator emits at \`/chosen\`; the boot image changed from 6ac2fc9e... to ce31ab2f.... This is an opaque bring-up identity, not an owner signature. Retest pending.
- The first tail-root boot mounted OS and reached load\_init\_program, then initproc failed with \`Library not loaded: /usr/lib/libSystem.B.dylib\` and \`no dyld cache\` because CONFIG\_XNU\_OWNER\_CACHE\_MOUNT and CONFIG\_XNU\_OWNER\_UNION\_SYSTEMOS were off. A development-only build now enables both and resolves the SystemOS APFS UUID through package/MarbleUnverifiedRoot.cpp without the owner signature; the verified path stays fail-closed. This is still unverified and has no Data seed.
- Upstream ShengUfs hardcodes stream 0x60; the vendor marble DT uses 0xE0. The fork changes the stream argument and the SMR match scan.
- Device probe 2026-10-31 \(read-only, no writes\): UFS host/GCC and the SMMU bank-2 takeover work. userdata first=0x2f6a00 last=0x3b037fa \(4096-byte LBAs, 224.2 GiB\); block0 has no SHNGROOT manifest \(manifest status=1, windows=0\), so it is the Android ext4 userdata. The geometry is now in board.toml \[userdata\].
- The first UFS probe reached SMMU planning and stopped at \`conflicting UFS stream mapping\`. The device reported slot=2 bank=74 smr=800000e0 s2cr=2 id2=5111: the firmware leaves an exclusive SMR for stream 0xE0 mapped to translating context bank 2.
- The fork now accepts that exclusive bank with native-ufs-smmu-takeover=1 and clears SCTLR/CBAR before using it as the driver bypass context. The first takeover build still failed because planUfsSmmu only scanned the top eight banks; the retry range is now the full context-bank count, so it reaches firmware bank 2. The rebuilt probe should continue to the GPT/userdata read.
- The full \(non-probe\) UFS block class subclasses IOBlockStorageDevice, whose vtable, ctors, dtors, metaclass and inherited methods live in the prelinked IOStorageFamily kext. The bindings were recovered from the reference IOBlockStorageDevice.o \(190 slots, 14 pure virtual\) and the built kernel.macho: vtable 0xfffffff005cb44c0, metaclass 0xfffffff006add1d0, ctor 0xfffffff00496ed98, D2 0xfffffff00496edb8, D1 0xfffffff00496edbc, D0 0xfffffff00496edc0. They are absolute symbols in scripts/data/native-storage-original-bindings.S, archived into libShengUfs.a by scripts/build-storage-bindings.py when XNU\_NATIVE\_UFS\_FULL=1.
- Host build 2026-10-31: the full UFS root kernel links and prelinks \(kernel.macho SHA-256 c3ea36a2b438f2f84bca0e342699b9640dfb61a7631463576674a1b63a1795bd\). The IOStorageFamily \_\_DATA\_CONST table address in the built kernel still matches the binding, and NativeUfsBlock is present. The matching boot.img is ce8b5f6e57c716ecf0605839734bd2806d4ae470c83d96eb829842caff6147cc and the userdata-root.img is fd43ee7035ce185ce4215ac93fdc006fd784a54b3b7442e21457c226cbe03093 \(9,382,658,048 bytes\).
- The root is unverified: CONFIG\_XNU\_VERIFIED\_ROOT\_PROBE, CONFIG\_XNU\_OWNER\_ROOT\_AUDIT and CONFIG\_XNU\_OWNER\_ROOT\_TRUST are off and there is no Data seed. The expected device results are a root-authentication panic or a launchd stop on missing /private/var; both identify the next stage.
- The controller, GCC and SMMU bases match the SM8550 layout, but the per-controller clock/power state and the UFS PHY ownership are not measured on marble.
- A probe-only attempt exposed an upstream compile error: timerTicks\(\) and native\_ufs\_read\_ticks were inside the NATIVE\_VERIFIED\_BLOCK guard. The fork moves them outside it so the transport can be compiled without the verified-root bundle.

### 完成条件

- UFS registers read, GPT and capacity match, root mounts and launchd starts, Data writes stay inside the measured window.

### 当前范围

- The unverified tail root reaches launchd and the SystemOS union; launchd then spawns /sbin/mount as PID 3 and the child exits 66 because no boot-manifest-hash is published. The root remains unauthenticated, there is no Data seed, and no verified-root/owner policy is present.

### 下一步

- Provide the verified-root bundle and Data seed, enable XNU\_OWNER\_BOOT\_MANIFEST, then rerun the tail root and record whether mount -P 1 passes. Do not use fastboot flash userdata for this layout.

### 证据

- `device`: [UFS host/GCC/SMMU takeover and userdata GPT read on marble 2026-10-31; manifest status=1 windows=0.](https://github.com/MiLacy/UniXNU-marble/blob/78f4e7bf00e88129f8b6ef5680d81770d386832d/docs/REAL-DEVICE-TESTS.md)
  Command: <code>fastboot boot boot.img (native-ufs-probe=10)</code>. Revision: `7f9a3e506235bf69479faf8f47dcda663fa9e658`.
- `device`: [OS root mounted from the userdata tail and launchd started with the SystemOS union \(libSystem resolved\). launchd then spawned /sbin/mount as PID 3; the child exited 66 with \`mount\[3\] exited -- no exit reason available\`, the known missing boot-manifest-hash checkpoint. Image SHA-256 6ac2fc9e...; Android first userdata block had remained UNCHANGED after the tail write.](https://github.com/MiLacy/UniXNU-marble/blob/78f4e7bf00e88129f8b6ef5680d81770d386832d/docs/REAL-DEVICE-TESTS.md)
  Command: <code>fastboot boot artifacts/marble-root/boot.img</code>. Revision: `7b8f56b4b3c6464c242ec213f835050f118bcc44`.
- `host`: [Verified kernel/payload/boot image linked from the GitHub macOS owner-policy artifact and local libVerifiedRootProbe.a; verified-root symbols present, Data seed included; hardware\_tested=false.](https://github.com/MiLacy/UniXNU-marble/blob/78f4e7bf00e88129f8b6ef5680d81770d386832d/package/BootProgress.c)
  Command: <code>./unixnu build payload ... --data-ramdisk artifacts/verified-root-data-old/owner-data/data-3g.dbr &amp;&amp; ./unixnu bootimg ...</code>. Revision: `7f74d9e0564f7c917e325c25f85515fc106cfa62`.
- `host`: [Unverified UFS root kernel \(NativeUfsBlock, no verified-root bundle\) and 9,382,658,048-byte tail image built and header-checked on the host; no device write.](https://github.com/MiLacy/UniXNU-marble/blob/78f4e7bf00e88129f8b6ef5680d81770d386832d/configs/marble-root_defconfig)
  Command: <code>./unixnu build kernel -D ../UniXNU-marble --ipsw ../iPad_Pro_HFR_17.7.11_21H461_Restore.ipsw &amp;&amp; ./unixnu build userdata -D ../UniXNU-marble --ipsw ../iPad_Pro_HFR_17.7.11_21H461_Restore.ipsw</code>. Revision: `0a6717c3212147f65c1b59a173dfd1565e9c5adb`.
- `host`: [Absolute IOBlockStorageDevice ABI bindings recovered from IOBlockStorageDevice.o and the 21H461 prelink; full kernel links with NativeUfsBlock at kernel.macho SHA-256 c3ea36a2b438f2f84bca0e342699b9640dfb61a7631463576674a1b63a1795bd.](https://github.com/MiLacy/UniXNU-marble/blob/78f4e7bf00e88129f8b6ef5680d81770d386832d/scripts/data/native-storage-original-bindings.S)
  Command: <code>./unixnu build kernel -D ../UniXNU-marble</code>. Revision: `f0721e9745c45ad2600cd69c74730f1cca55d56a`.
- `source`: [Stream override implementation and SM8550 register constants.](https://github.com/MiLacy/UniXNU-marble/blob/78f4e7bf00e88129f8b6ef5680d81770d386832d/drivers/ShengUfs/NativeUfs.cpp)
- `source`: [UFS, SMMU and GCC sources.](https://github.com/MiLacy/UniXNU-marble/blob/78f4e7bf00e88129f8b6ef5680d81770d386832d/docs/HARDWARE.md)

## 显示 {#display}

`planned`

组件: `GopFramebuffer`.

### 硬件与依赖

- 1080x2400 GOP framebuffer, splash region 0xB8000000/0x2B00000, UEFI SimpleFbDxe.

### 配置

- GopFramebuffer is selected but CONFIG\_XNU\_NATIVE\_LEGACY\_DISPLAY is off in the first-console defconfig. The legacy archive and board probe are described in docs/FULL-SYSTEM.md.

### 操作步骤

- Enable the legacy display archive, add offline-legacy-register=1 and offline-legacy-gop=1, then verify geometry, colors and the userland transition.

### 开发经验

- The stock Mu-Silicium marble platform publishes a 1080x2400 32-bit GOP on the ABL framebuffer.
- The sheng/alioth display stack binds the original IOMobileFramebufferLegacy; it is OS-version-specific and must be re-proved against this kernel at build time.

### 完成条件

- A known frame appears with correct geometry and colors, then the boot progress and Hello screen present.

### 当前范围

- The legacy display archive is not wired into this repository yet; the first console relies on the XNU framebuffer console.

### 下一步

- Port the display-only parts of the alioth legacy archive, then test the panel on the phone.

### 证据

- `source`: [Panel and splash values.](https://github.com/MiLacy/UniXNU-marble/blob/78f4e7bf00e88129f8b6ef5680d81770d386832d/docs/HARDWARE.md)

## 输入 {#input}

`planned`

组件: `QcomGeniSpi`.

### 硬件与依赖

- Goodix GT9916S on SPI 0x990000, SPI 605, IRQ GPIO21, reset GPIO20, GPI 0x900000, clocks 94/134/135.

### 配置

- QcomGeniSpi is selected as the controller component. No Goodix protocol or IOHIDDevice publisher is enabled.

### 操作步骤

- Implement the GENI SPI + GPI DMA + Goodix protocol path, publish IOHID digitizer events and verify contacts and release events.

### 开发经验

- The vendor DT gives a complete wiring description, but the GPI/SMMU mapping and the Goodix firmware/config images are not implemented.
- The legacy port reached register reads and a clock snapshot but no physical touch.

### 完成条件

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive and Setup is usable.

### 当前范围

- No touch driver or firmware image is present. Setup cannot be completed with touch on this image.

### 下一步

- Build a minimal Goodix probe that reads the product ID and one touch event before integrating HID.

### 证据

- `source`: [Touch wiring and source values.](https://github.com/MiLacy/UniXNU-marble/blob/78f4e7bf00e88129f8b6ef5680d81770d386832d/docs/HARDWARE.md)

## GPU {#gpu}

`not-applicable`

### 硬件与依赖

- Adreno 725 GPU and firmware; no catalog component covers this GPU generation.

### 配置

- No GPU component is selected. CONFIG\_XNU\_NATIVE\_ADRENO is off.

### 操作步骤

- Inventory the GPU/GMU/firmware and define a submit/fence checkpoint before selecting a driver.

### 开发经验

- The catalog Adreno740 component is SM8550-specific and does not cover the Adreno 725.

### 完成条件

- A GPU driver matches the Adreno 725 and completes a known submission.

### 当前范围

- No GPU acceleration is implemented or claimed.

### 下一步

- Inventory the A725 GMU and SMMU interfaces from the vendor kernel before writing a driver.

### 证据

按下一步操作收集证据。

## 网络 {#network}

`not-applicable`

### 硬件与依赖

- Wi-Fi/cellular controller, firmware and transport.

### 配置

- No network component is selected.

### 操作步骤

- Identify the exact WCN/ath12k part and its firmware before implementation.

### 开发经验

- No network association or packet transfer is implemented.

### 完成条件

- The device associates and transfers packets through the OS interface.

### 当前范围

- No network support is claimed.

### 下一步

- Identify the Wi-Fi part from the vendor DT and firmware partition.

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`not-applicable`

### 硬件与依赖

- ADSP firmware, codec, GPR/GLINK/SMEM transport and routes.

### 配置

- No audio component is selected.

### 操作步骤

- Trace the DSP/codec dependencies and define a playback or loopback checkpoint.

### 开发经验

- No DSP/codec route or playback/capture is implemented.

### 完成条件

- At least one documented playback or capture route works.

### 当前范围

- No audio support is claimed.

### 下一步

- Inventory the ADSP and codec firmware before selecting a driver.

### 证据

按下一步操作收集证据。

## 电源 {#power}

`planned`

### 硬件与依赖

- PMIC, RPMh, battery, charger and CPU frequency domains.

### 配置

- No power component is selected. The first console boots on external power.

### 操作步骤

- Add the PMGR placeholder for AMFI, then implement battery/charger and CPU frequency policy.

### 开发经验

- Unmodified AMFI expects an ApplePMGR provider and panics at ConfigurationSettings.cpp:235 with \`No PMGR?\` when none exists. The board package now carries ShengPlatformPower.cpp and scripts/build-platform-power.py; CONFIG\_XNU\_SHENG\_PMGR=y plus sheng-pmgr=2 publishes the guarded placeholder from the original ApplePMGR ABI. It implements no hardware power operation and panics on any power call, so it is a bring-up bridge, not power management.
- No suspend/resume, battery or charger support exists in this image.

### 完成条件

- Rails/clocks are owned, a supported power transition recovers, and battery readings match the device.

### 当前范围

- No power management is implemented or claimed.

### 下一步

- Run the PMGR-enabled image on hardware and record whether AMFI passes and which root/IOKit checkpoint follows.

### 证据

- `source`: [PMGR placeholder and staged power work.](https://github.com/MiLacy/UniXNU-marble/blob/78f4e7bf00e88129f8b6ef5680d81770d386832d/docs/FULL-SYSTEM.md)

## 镜像组装 {#packaging}

`device-verified`

组件: `XnuPrelink`.

### 硬件与依赖

- XNU source, iPadOS kernelcache, trust cache, Data seed, firmware DTB and UEFI FD.

### 配置

- \[kernel\] prelink comes from the iPadOS 17.7.11 profile. \[payload\] selects a 160 MiB FAT16 volume, panic screen and the full UFS root arguments. \[firmware\] supplies the FD path.

### 操作步骤

- Build kernel, payload and boot image in order; inspect boot.json and payload.json before booting.

### 开发经验

- 2026-11-01 on-screen boot log: CONFIG\_XNU\_BOOT\_PROGRESS=y links libBootProgress.a and routes vcputc/PE\_kputc to the GOP framebuffer. The screen-log kernel is SHA-256 51f44694f19cf829a87462f0c431b2dfa00cf7c7914c355fa90a13e074be2716 and its boot.img is 99998e8a5b9b72d2d7143ddab699e785791a2d9a8dcbe9dcad9e5b62cde84f7b; userdata is unchanged. This gives stage and exec lines on screen but still no host log channel.
- 2026-11-01 unverified tail-root package: 51,146,752-byte kernel b1ae430b..., 160 MiB payload 992815d5..., 169,607,168-byte boot.img ce31ab2f..., and 9,382,658,048-byte userdata image fd43ee70.... The boot image uses cpus=1, native-ufs-root=1, LBA 59589627, 2290688 blocks, stream 0xE0, SMMU takeover, native-ufs-allow-unverified=1 and root-unverified=1.
- 2026-11-01 first-entry console build: marble-console\_defconfig \(no UFS/root/Data/display\) with the 21H461 IPSW, kernel.macho SHA-256 5270a0b93bea8db7de01f56440f8142430df4395954bf18335f8f5806c32e6df, 160 MiB payload SHA-256 4a416b4ef506ea69279cde3e7ebe5ffeacc9fbb3a77630f54b0d43612e36f1c9, and 169,607,168-byte boot.img SHA-256 d169cb16d8d9bb25b6184bd544ce0d831a6f01499f037ab1424972b67b696b7e. The image passes cpus=1 and zeroed UFS arguments; it is host-built only.
- The first console boot reached IOKit and data-aborted at IODTGetICellCounts+0x2c \(PC 0xfffffff0078ec634, ESR 0x96000005, FAR 0\), with IODTMapInterruptsSharing+0x290 in the stack. The generated ADT had only \`phandle\`; AddPHandle records \`AAPL,phandle\`, so interrupt-parent resolved to NULL. The ADT generator now maps phandle/linux,phandle to AAPL,phandle; the regenerated ADT contains the property and the payload hash changed. The kernel itself was unchanged.
- The OS profile pins the same 21H461 kernelcache and trust caches used by sheng and alioth.
- The payload path is resolved relative to \\EFI\\UniXNU, so the builder writes \\EFI\\UniXNU\\Payloads\\kernel.macho; a file at the FAT root is not found.
- mformat -F produced a FAT32 BPB that the EDK2 FAT driver refused \(TotSec16 nonzero with TotSec32 zero\). The builder now creates FAT16 \(mkfs.fat -F 16, or mformat without -F\) and rejects FAT32 or a missing 0x55AA signature.
- UniXNURamDiskDxe validates the FAT boot sector, aligns initrd-end down to 512 bytes and calls ConnectController after installing BlockIo. UniXNU also connects all controllers before scanning for unixnu.toml, so the payload volume appears without relying on BDS enumeration order.
- The working fastboot boot path is an Android v0 image: kernel 0x80008000, 160 MiB payload at 0xA8000000, DTB /chosen initrd 0xA8000000-0xB2000000. The earlier v4 image did not load the ramdisk reliably.
- Host build 2026-10-30 produced the historical two-module original trust bundle \(SHA-256 7416ca4f...\); that file is not in this checkout. The 2026-11-01 empty-ramdisk Stage 1 image is 1,835,008 bytes \(SHA-256 8adf6380c2991c389b6c08cbfc86036543f2fa647c71c34e3d52523c69f891cd\) and is derived from the current FD and DTB.
- Host build 2026-10-31 \(full UFS root\): kernel.macho SHA-256 c3ea36a2b438f2f84bca0e342699b9640dfb61a7631463576674a1b63a1795bd; boot.img 68947968 bytes with the Android v0 header \(SHA-256 ce8b5f6e57c716ecf0605839734bd2806d4ae470c83d96eb829842caff6147cc\); payload.img 64 MiB FAT16 \(historical build\); userdata-root.img 9382658048 bytes \(SHA-256 fd43ee7035ce185ce4215ac93fdc006fd784a54b3b7442e21457c226cbe03093\) with OS/SystemOS windows.
- The payload FAT volume contains EFI/UniXNU/unixnu.toml, Payloads/kernel.macho, kernel.macho.adt and kernel.macho.trustcache; the packed command line includes native-ufs-stream=0xe0, native-ufs-smmu-takeover=1, native-ufs-root=1 and sheng-pmgr=2.

### 完成条件

- Kernel and prelink succeed, the payload contains all declared inputs, and the boot image matches the Android v0 header, the fixed ramdisk range and the userdata partition.

### 当前范围

- The console boot image has no UFS/root driver, so it stops at IOKitBSDInit.cpp:984 as expected. The userdata image has not been flashed and no launchd result exists.

### 下一步

- Build an unverified root kernel/image first; only then decide whether to back up and flash userdata.

### 证据

- `host`: [Stage 1 firmware and empty-ramdisk boot image built and round-trip verified on the host; boot.json records ramdisk\_bytes=0, kernel\_address=0x80008000, hardware\_tested=false.](https://github.com/MiLacy/UniXNU-marble/blob/78f4e7bf00e88129f8b6ef5680d81770d386832d/firmware/README.md)
  Command: <code>./unixnu build firmware -D ../UniXNU-marble --uefi ../uefi-marble --edk2 ../uefi-marble/Mu_Basecore &amp;&amp; ./unixnu bootimg -D ../UniXNU-marble --uefi ../uefi-marble --fd ../uefi-marble/Build/marblePkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd --dtb ../uefi-marble/Resources/DTBs/marble-unixnu.dtb --ramdisk none</code>. Revision: `d1f18525135544426fae87c9497155df7f9e1fc7`.
- `host`: [Console kernel, 160 MiB payload and 169,607,168-byte boot.img built and round-trip verified on the host; no verified-root/Data inputs; hardware\_tested=false.](https://github.com/MiLacy/UniXNU-marble/blob/78f4e7bf00e88129f8b6ef5680d81770d386832d/configs/marble-console_defconfig)
  Command: <code>./unixnu build kernel -D ../UniXNU-marble --ipsw ../iPad_Pro_HFR_17.7.11_21H461_Restore.ipsw &amp;&amp; ./unixnu build payload ... --kernel-arg cpus=1 ... &amp;&amp; ./unixnu bootimg ...</code>. Revision: `466b025c2d8c74dc60c3122e9eb8766de9f783c0`.
- `host`: [Screen-log kernel and 169,607,168-byte boot image built; BootProgress symbols link and the payload retains the tail-root arguments. Not yet device-tested.](https://github.com/MiLacy/UniXNU-marble/blob/78f4e7bf00e88129f8b6ef5680d81770d386832d/package/BootProgress.c)
  Command: <code>./unixnu build kernel -D ../UniXNU-marble --ipsw ../iPad_Pro_HFR_17.7.11_21H461_Restore.ipsw &amp;&amp; ./unixnu build payload ... &amp;&amp; ./unixnu bootimg ...</code>. Revision: `12e6d2977166292b5a5898234162e338265b665f`.
- `host`: [Unverified UFS tail-root payload and boot image built; payload record names LBA 59589627/2290688 blocks and zeroed Data inputs.](https://github.com/MiLacy/UniXNU-marble/blob/78f4e7bf00e88129f8b6ef5680d81770d386832d/configs/marble-root_defconfig)
  Command: <code>./unixnu build payload ... --kernel .../marble-root/kernel/kernel.macho ... &amp;&amp; ./unixnu bootimg ...</code>. Revision: `0a6717c3212147f65c1b59a173dfd1565e9c5adb`.
- `device`: [XNU booted from the 169,607,168-byte console image and failed at IOFindBSDRoot+0xc88 \(\`IOKitBSDInit.cpp:984\`\) because UFS/root is deliberately absent. This is the Stage 2 success checkpoint, not a regression.](https://github.com/MiLacy/UniXNU-marble/blob/78f4e7bf00e88129f8b6ef5680d81770d386832d/docs/REAL-DEVICE-TESTS.md)
  Command: <code>fastboot boot artifacts/marble-xnu-console/boot.img</code>. Revision: `0a6717c3212147f65c1b59a173dfd1565e9c5adb`.
- `host`: [Previous full UFS root kernel, payload and 8.8 GiB userdata image; not present in this checkout and not a current verification.](https://github.com/MiLacy/UniXNU-marble/blob/78f4e7bf00e88129f8b6ef5680d81770d386832d/docs/REAL-DEVICE-TESTS.md)
  Command: <code>./unixnu build kernel -D ../UniXNU-marble &amp;&amp; ./unixnu build payload ... &amp;&amp; ./unixnu bootimg ...</code>. Revision: `e13cbdc5da195f9e52ac72d406fadeac3107fb57`.

## 诊断 {#diagnostics}

`planned`

### 硬件与依赖

- Serial/UART access, firmware log exporter and panic screen.

### 配置

- The first-console command line enables -v, serial=3 and debug=0x14e. panic\_screen is true. The firmware log exporter is not added yet.

### 操作步骤

- Capture the firmware log, the UniXNU menu counts, DarwinBoot output and the panic screen at each stage.

### 开发经验

- The phone has no exposed UART; the framebuffer console and panic screen are the primary diagnostics.
- A QR log exporter is recommended before storage and kernel handoff; it is not integrated into the marble DSC/FDF yet.

### 完成条件

- Each claimed milestone has a reproducible command, an exact image revision and an accessible log or photo.

### 当前范围

- No real-device log has been captured.

### 下一步

- Integrate Advanced Logger/AdvancedLogDxe and capture the Stage 1 menu log.

### 证据

按下一步操作收集证据。

</div>
