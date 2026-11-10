# Redmi K70 \(qusno1\)

[qusno1/UniXNU-vermeer](https://github.com/qusno1/UniXNU-vermeer)

<div v-pre>

Redmi K70 \(vermeer, SM8550, 16 GiB, UFS 4.0\). Port state: the firmware volume builds and runs, the UniXNU menu appears, and the prelinked iPadOS 27 kernel enters on the phone and runs through IOKit and bsd\_init to the root-device lookup. The boot stops there because no storage driver is selected, so stage 6 \(root mount\) and stage 7 \(launchd\) are still ahead.

源记录: [porting.toml](https://github.com/qusno1/UniXNU-vermeer/blob/ecd77f51b57d808d55f94691f9dfc986f36075ea/porting.toml), `ecd77f51b57d808d55f94691f9dfc986f36075ea`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `implemented` |
| [固件与启动](#firmware) | `device-verified` |
| [CPU 与中断](#cpu) | `planned` |
| [内存与 DMA](#memory) | `planned` |
| [存储与根卷](#storage) | `implemented` |
| [显示](#display) | `planned` |
| [输入](#input) | `planned` |
| [GPU](#gpu) | `planned` |
| [网络](#network) | `planned` |
| [音频](#audio) | `planned` |
| [电源](#power) | `planned` |
| [镜像组装](#packaging) | `implemented` |
| [诊断](#diagnostics) | `planned` |

## 配置 {#configuration}

`implemented`

### 硬件与依赖

- SoC source UniXNU/UniXNU-sm8550-common pinned at a9f45dc60c035084b95463781538380f4c3606c9 in feeds.toml.
- OS profile ipados-27.0.1-24A446: arm64e, XNU 12377.121.6, iPadOS 27.0.1 build 24A446.
- Target restore image from the OS profile: iPadOS 27.0.1 build 24A446 for iPad17,3 \(J820AP\), the same image the reference SM8550 device qualifies. The board does not override \[ipsw\].
- Profile identity values: device\_class j820ap, chip\_id 0x8142, board\_id 12, and the profile's prelink pins, root volume UUIDs and trust-cache inputs all describe this product.
- Board hardware facts measured on the device and in the stock ABL device tree: 16 GiB DRAM, 8 cores with A510/A715/A710/X3 clusters, GICv3 at 0x17100000 with 0x40000 redistributor stride, 19.2 MHz architectural timer, UFS host at 0x1d84000 and PHY at 0x1d80000.
- userdata measured on the phone: /dev/block/by-name/userdata -&gt; sda29, 512-byte sectors, start 20562432, size 906909184; in 4096-byte LBAs first 2570304, last 115933951, 113363648 LBAs \(432.4 GiB\). The whole disk reports 474.3 GiB.
- Platform seed: kept outside every repository; supply it with --unique-chip-id or the UNIXNU\_UNIQUE\_CHIP\_ID secret.
- CPU identity read from /proc/cpuinfo: implementer 0x41 \(ARM\), parts 0xd46 \(Cortex-A510\), 0xd4d \(Cortex-A715\), 0xd47 \(Cortex-A710\), 0xd4e \(Cortex-X3\), matching the stock device tree split.
- PAC is present in the CPU features: the core reports paca and pacg, so the arm64e profile's FEAT\_PAuth requirement is satisfied by the hardware. Whether EL1 key registers are programmed correctly under XNU is still untested.
- Display: 1440x3200 internal panel, 60/90/120 Hz modes, HDR types 1-4, density 560 dpi, brightness range 8.5e-4 to 1.0 with default 0.075, from dumpsys display.
- UFS device descriptor: manufacturer\_id 0x0198, number\_of\_luns 6; the host exposes gear and clkscale controls at /sys/devices/platform/soc/1d84000.ufshc.

### 配置

- board.soc\_source = sm8550; board.os\_profile = ipados-27.0.1-24A446; schema\_version = 2; kit = vermeer.
- \[components\] include = ArmDTPlatform, ArmCpu, XnuPrelink, DarwinBoot, GopFramebuffer, AppleKeyStoreState, ShengUfs.
- \[kernel\] config\_fragments = arch:configs/common.config, soc:configs/sm8550.config, os:configs/ipados.config; the device defconfig applies last and replaces earlier values for the same key.
- \[kernel\] patch\_series = arch:patches/xnu/series, soc:patches/xnu-12377/series, os:patches/xnu/series, device:patches/xnu/series; the device series carries vermeer-kernel-stack-shift.patch, vermeer-framebuffer-console.patch and vermeer-mountroot-diagnostic.patch.
- configs/vermeer\_defconfig leaves CONFIG\_XNU\_NATIVE\_ADRENO unset, so the kernel does not link the GPU archive, and sets CONFIG\_XNU\_NATIVE\_UFS=y, so it does link the UFS one.
- \[firmware\] names Platforms/Xiaomi/vermeerPkg/vermeer.dsc and Build/vermeerPkg/&\#123;target&\#125;\_CLANGPDB/FV/SILICIUM\_UEFI.fd in the uefi-vermeer checkout.
- \[payload.adt\] carries the required platform-seed placeholder and a 256 MiB owned-memory request that fits the single 2 GiB DRAM range the DTS declares; the ADT identity comes from the OS profile \(iPad17,3 / J820 / J820AP\).
- \[adt.chosen.bytes\] boot-manifest-hash carries a 48-byte development-only bring-up identity so launchd's mount phase does not exit 66. It is not an owner signature; the record says so next to the value.
- \[payload\] kernel\_args carries native-source-storage=1, native-ufs-root=1 and vermeer-root-partition=unixnu: the first is what makes the source-storage runtime do anything at all, the second selects the UFS root path, and the third names the GPT partition that holds the root image on this board. The whole command line is 151 bytes.
- \[payload\] root\_policies points at build/sheng-source-storage/root-policies.bin, the VROOTB01 container that build-sheng-source-storage.py assembles from scripts/policies. Setting it is what makes devicetree.py emit the /chosen/memory-map/RootPolicies placeholder that DarwinBoot fills and that native\_source\_root\_policies\_load\(\) reads; without it the runtime panics rather than starting unauthenticated storage.
- feeds.toml pins the UFS driver to https://github.com/qusno1/ShengUfs.git at bf21739 rather than the catalog's upstream repository, because the fork is what makes the root partition's name a runtime value.
- The UFS driver is linked and selected by four settings that must move together: ShengUfs in \[components\], component:ShengUfs in \[kernel\] archives, CONFIG\_XNU\_NATIVE\_UFS=y in the defconfig, and native-ufs-root=1 in kernel\_args. Any one of them alone does nothing, and the failure modes differ: a component without an archive entry stops the archive plan, an archive without the config flag links dead code, and the flag without the argument never starts the driver.
- The catalog's ShengUfs cannot be used as-is on a board that keeps Android's userdata. Its RootLayout.h compiled in the partition name "userdata", which is only right where the root image was flashed over that whole partition. feeds.toml therefore pins the fork at qusno1/ShengUfs, whose only behavioural change is a runtime partition name defaulting to "userdata".

### 操作步骤

- Run ./unixnu defconfig vermeer\_defconfig -D ../UniXNU-vermeer from the UniXNU checkout.
- Run ./unixnu fetch -D ../UniXNU-vermeer to resolve the SoC source and write unixnu.lock.
- Run ./unixnu status --json -D ../UniXNU-vermeer and review profiles, component sources, overrides and patch order.
- Run python3 scripts/porting-record.py check --device ../UniXNU-vermeer from the UniXNU checkout.

### 开发经验

- Arrays replace inherited arrays in every profile layer, so \[components\] include and \[kernel\] archives must each name the complete set; a component left out of archives but selected in components fails the kernel archive plan with 'needs component entries for'.
- soc:configs/sm8550.config sets CONFIG\_XNU\_NATIVE\_ADRENO=y, and the device defconfig applies after the fragments, so leaving the flag out of the defconfig silently enables the GPU archive that the board cannot build yet.
- The kernel archive plan adds a component's dependencies before the component, and refuses a component that is selected but has no archive entry; AppleKeyStoreState therefore needs an explicit component:AppleKeyStoreState entry.
- Overriding \[ipsw\] to another product is not free: the prelink step stopped with 'the kernelcache of this IPSW does not match the pin' because the profile's kernelcache digest, AMFI initializer address, root volume UUIDs and trust-cache inputs all belong to the profile's own image. The board therefore keeps the profile image.
- \[kernel\] archives is also where a profile input that nothing else produces has to be built. The profile's prelink extra\_args name build/xnu/fileset-reference/mach.release.bcm2837.unstripped.noctf as --fileset-reference, and the build failed with FileNotFoundError until build-fileset-release-reference.py --tree . --lto was appended to the list, as UniXNU-sheng does for the same profile.
- \[kernel.prelink\] roots replaces the profile's array instead of extending it. The profile ships 31 roots; the reference board on this profile states 44 by adding the USB device and host stacks, and the profile's prelink-regression policy matches that set. With 31 roots, one AppleM2ScalerCSCDriver reference resolves to nothing and the prelink stubs it, which the policy allows 0 of.
- \[os\_overrides."ipados-27.0.1-24A446"\] removes kernel.prelink.regression\_policy for this board. The profile's policy is written against a kernel that links the legacy-display stack, which this board does not; the resulting stub is recorded in the display area and stays visible in kernel/kernel.macho.json.
- \[payload.adt\] must state chip\_id. The ADT generator reads that key and not the profile's \[ipsw\] table, so leaving it out failed the payload step with KeyError: 'chip\_id'; 0x8142 is the ApChipID of the profile's restore image.
- \[payload.adt\] owned\_memory\_size must fit the single DRAM range the ADT declares. At 0x130000000 \(4.75 GiB\) no run below 4 GiB qualified, so DarwinBoot placed the kernel at physical 0x8c0190000 and the boot page tables, built for the declared 2 GiB, faulted arm\_vm\_init.c:1107. 0x10000000 \(256 MiB\) is DarwinBoot's default and fits.
- \[adt.chosen.u32\] kernel-ctrr-to-be-enabled = 0 is what lets the kernel survive its first /chosen read. ml\_unsafe\_kernel\_text\_init \(osfmk/arm64/machine\_routines.c:3385\) reads that iBoot property at STARTUP TUNABLES rank and leaves \_unsafe\_kernel\_text\_initialized false when it is absent, so dtrace\_sdt\_probes\_restricted\(\) -- the first code that asks, called from sdt\_init\(\) during bsd\_init -- asserts at machine\_routines.c:3379. The assert surfaces through the brk trap handler, which is why the screen shows the machine\_routines.c:3379 text followed by a register dump: pc 0xfffffff00b5b1a48 is \_ml\_unsafe\_kernel\_text.cold.1+0xc and the stack holds \_dtrace\_sdt\_probes\_restricted+0x10, \_sdt\_init+0x34 and \_bsd\_init+0x674. The value 0 means the SoC has no CTRR, so kernel text stays writable by hardware; the reference board declares the same property with the same value for the same reason.
- .github/workflows/package.yml pins the UniXNU checkout to 95ad78129203442c3c14c02336303adbddf8d0a3, the revision the recorded images were built from, instead of tracking the upstream default branch. Upstream main now pins drivers/AppleKeyStoreState to 6ff4f11d, a commit that the UniXNU/AppleKeyStoreState repository does not contain, so an unpinned run dies in its third checkout step with 'upload-pack: not our ref 6ff4f11d' before the tools step. The pin also makes a run reproducible; bump it together with the images it produces.
- With the 256 MiB window the kernel passes arm\_vm\_init and then takes a same-EL data abort with DFSC 0x10, a synchronous external abort, at FAR 0x218f44000 \(about 8.4 GiB\). That address is a hole: the low extents end at 0x1c04b0000 and the high banks start at 0x880000000. \[payload\] entry\_probe\_reset\_delay is a diagnostic that answers whether the core reaches the MMU enable, because the fault address alone does not place the stage.
- The stage-3 probe never fired, so the core faults before the MMU is enabled. That fault names the two values this board supplies: x9 = 0x10000000 \(owned\_memory\_size\) and x1 = 0x100000000 \(dram-base + dram-size\), with FAR 0xe8004000. The early walk covers the whole declared range, and the low 4 GiB is not contiguous: the stock device tree has holes at 0x80e00000..0x811d0000, 0xd8000000..0xd8140000 and 0xd8160000..0xe7cb0000. The DTS memory node therefore has to describe one contiguous range inside that map; it currently states 0x80000000 + 0x80000000 \(2 GiB\), which is the range the ADT and the boot page tables are built from.
- The entry probe and the panic screen share one code cave and cannot be enabled together: the probe writes stage code into the zero padding after the kernel entry, and the panic screen is assembled after the last probe cave under a fixed PANIC\_CAVE\_END. With stage 3 on, the 0xa2f-byte panic screen did not fit the remaining padding and the payload step refused it. One diagnostic per run.

### 完成条件

- The defconfig, feeds and component selection resolve with no required-input placeholder.
- unixnu status reports the intended profiles, sources, overrides and patch order.
- The porting record checker reports no identity, coverage or evidence error.

### 当前范围

- The record lists implementation and host results only; nothing in this repository has been verified on the phone.
- Panel and touch identities come from the stock device tree and from Android userspace, not from an XNU boot; the EL1 PAC key-register state is untested even though the CPU reports paca and pacg.
- The board runs the profile's iPad17,3 image, so its ADT identity is J820AP rather than a Redmi product identity; anything that keys on the Apple product class sees an iPad.

### 下一步

- Produce the boot image on a macOS host and record the first UEFI, UniXNU and loader checkpoints.

### 证据

- `source`: [Board, IPSW identity, component selection, firmware paths and payload inputs described in this area.](https://github.com/qusno1/UniXNU-vermeer/blob/ecd77f51b57d808d55f94691f9dfc986f36075ea/board.toml)
- `source`: [SoC source URL and commit pin.](https://github.com/qusno1/UniXNU-vermeer/blob/ecd77f51b57d808d55f94691f9dfc986f36075ea/feeds.toml)
- `source`: [Stock ABL device tree pulled from the device with adb pull /sys/firmware/fdt on HyperOS OS3.0.307.0.WNKCNXM; 808716 bytes, DTB version 17.](https://github.com/qusno1/UniXNU-vermeer/blob/ecd77f51b57d808d55f94691f9dfc986f36075ea/firmware/dtb/vermeer.dtb)
- `host`: [All source pins resolved: xnu ac9718fb1af618d5ce8678d0dc6e8a58f252216f, sm8550 a9f45dc60c035084b95463781538380f4c3606c9, edk2 cfb93724a06ff86ff5ba971413368a7809ee42a5.](https://github.com/qusno1/UniXNU-vermeer/blob/ecd77f51b57d808d55f94691f9dfc986f36075ea/unixnu.lock)
  Command: <code>./unixnu fetch -D ../UniXNU-vermeer</code>. Revision: `c8027115706c3ceac37e45c9b81db447bbc5ceba`.

## 固件与启动 {#firmware}

`device-verified`

组件: `DarwinBoot`.

### 硬件与依赖

- uefi-vermeer checkout with Platforms/Xiaomi/vermeerPkg, adapted from the sheng SM8550 reference platform.
- Firmware volume window 0xA7100000, 3 MiB, inside the stock 4 MiB FD window at 0xA7000000; the stock uefi.elf loads at 0xA7000000 with 0x2CD000 bytes.
- Firmware inputs: stock ABL device tree at firmware/dtb/vermeer.dtb for the boot image and the firmware preflight.
- Mu-Silicium submodules Common/Mu, Common/Mu\_OEM\_Sample, Silicium-ACPI and the OpenSSL library, plus Resources/MuPatches/Gic-Spurious.patch.

### 配置

- \[firmware\] config = vermeer, dsc = Platforms/Xiaomi/vermeerPkg/vermeer.dsc, fd = Build/vermeerPkg/&\#123;target&\#125;\_CLANGPDB/FV/SILICIUM\_UEFI.fd.
- \[firmware.defines\] ENABLE\_SECUREBOOT = 1, DEVICE\_MODEL = vermeer, MEMORY\_PROTECTION = TRUE, BUILDID\_STRING = vermeer-research.
- \[firmware\] preflight runs scripts/prepare-vermeer-firmware-dtb.py, which copies the stock device tree to build/vermeer/vermeer.dtb for the boot image step.
- \[bootimg\] dtb = build/vermeer/vermeer.dtb and one dtb\_node that restores /reserved-memory/splash\_region \(0xb8000000, 0x2b00000\) because the stock ABL powers the panel off without it.
- \[payload\] loader = firmware: DarwinBoot lives in the firmware volume, and UniXNURamDiskDxe with DiskIoDxe and FAT publishes the payload volume.

### 操作步骤

- Run ./unixnu build firmware --uefi ../uefi-vermeer -D ../UniXNU-vermeer.
- Inspect the log for the FV space report and the SILICIUM\_UEFI.fd size, which must equal the \[uefi\_fd\] size of Resources/Configs/vermeer.toml.
- Record the FD and boot image hashes before any device run.

### 开发经验

- The firmware volume builds: FVMAIN reports 99 percent used with 880 bytes free, and FVMAIN\_COMPACT 33 percent used, inside a 3 MiB FD; the compressed volume, not FVMAIN, bounds growth.
- The firmware runs on the phone and reaches the UniXNU menu: fastboot accepts the v0 image, BootShim hands over the 3 MiB volume at 0xa7100000, SEC reaches DXE without the stall at 'MMU: enabled' the reference platform hit before PcdBuildXblHobs was turned off, and the boot manager draws on the GOP.
- The boot image device tree is the stock ABL blob, which already carries /reserved-memory/splash\_region as &lt;0 0xb8000000 0 0x2b00000&gt; with the label cont\_splash\_region. A \[bootimg\] dtb\_node for the same path failed the pack step with FDT\_ERR\_EXISTS, so the entry is gone and the stock node is used unchanged.
- The reference platform disables its vendor hardware stack \(VERMEER\_VENDOR\_HW = 0\) so that the previous stage's display keeps scanning out; enabling the stock vendor drivers reaches ClockDxe and leaves the panel black with the backlight on, a failure inherited from sheng and not diagnosed on this board.
- Memory additions come from VermeerBootMemoryDxe, which adds DRAM in pieces of at least 16 MiB and at most 1 GiB below 4 GiB; the three banks above 4 GiB are already conventional memory in MemoryMapLib.
- The platform package still carries sheng panel and vendor-import text \(N81A panel XMLs, the sheng firmware archive hash\); those inputs are unused while USE\_CUSTOM\_DISPLAY\_DRIVER and VERMEER\_VENDOR\_HW are 0 and must be replaced before enabling the vendor stack.

### 完成条件

- The firmware volume builds at the declared size and enters UniXNU on the device.
- The framebuffer shows the UniXNU menu and the payload volume is visible as a block device.
- The memory reservations from the stock device tree survive the handoff.

### 当前范围

- The payload volume is not visible yet: the verified image has an empty ramdisk, so stages 3 to 7 are untested.
- No log transcript exists. The firmware log export is not wired and the board has no UART, so the only record of a boot attempt is a photograph of the screen.
- The stock vermeer uefiplat.cfg has not been imported; MemoryMapLib's 78 descriptors are the reference platform's layout candidates, extended with this board's three high DRAM banks.
- The vendor hardware stack is disabled, so vendor clocks, RPMh, UFS and charger drivers are not exercised.

### 下一步

- Pack the payload and boot image with the prelinked kernel on a macOS host, then boot it and record the payload, loader and kernel checkpoints.

### 证据

- `source`: [Firmware inputs and their consumers; the SecParti.cfg entry is a placeholder from another platform and nothing consumes it while VERMEER\_VENDOR\_HW = 0.](https://github.com/qusno1/UniXNU-vermeer/blob/ecd77f51b57d808d55f94691f9dfc986f36075ea/proprietary-files.txt)
- `host`: [SILICIUM\_UEFI.fd built at 3145728 bytes; FVMAIN 5565584 of 5566464 bytes used, FVMAIN\_COMPACT 1056872 of 3145728.](https://github.com/UniXNU/UniXNU/blob/main/docs/porting/uefi-firmware.md)
  Command: <code>./unixnu build firmware --uefi ../uefi-vermeer -D ../UniXNU-vermeer</code>. Revision: `009f9f7b5b3ff59d3109fa6f5bce9911adbb2d62`.
- `device`: [The bootloader sent 1788 KB and booted the image; the screen then showed the UniXNU menu with its UNIXNU: output. Image 1830912 bytes, SHA-256 4a2994d4792c41e72a3efc4da6484cde6289cd36f366faae0366e21eabc9c2a4, header v0, ramdisk none.](https://github.com/qusno1/UniXNU-vermeer/blob/ecd77f51b57d808d55f94691f9dfc986f36075ea/reports/2026-11-09-uefi-menu.md)
  Command: <code>fastboot boot boot.img</code>. Revision: `b1c88c0808db7955a9ffd0e55ff35489e34bc25b`.

## CPU 与中断 {#cpu}

`planned`

组件: `ArmCpu`, `ArmDTPlatform`.

### 硬件与依赖

- 8 cores: cpu0-2 Cortex-A510, cpu3-4 Cortex-A715, cpu5-6 Cortex-A710, cpu7 Cortex-X3, all taken from the stock device tree.
- GICv3 distributor at 0x17100000, redistributor stride 0x40000; PDC qcom,kalama-pdc at 0xb220000.
- Architectural timer at 19200000 Hz, always on.
- PSCI 1.0 over SMC.

### 配置

- dts/vermeer.dts marks cpu0-2 unixnu,cluster-type = E and cpu3-7 = P; ArmCpu reads the cluster type as an integer character.
- soc dtsi declares /cpus with timebase-frequency 19200000 and /psci with method smc; the ADT generator requires a PSCI method when more than one CPU is enabled.
- SoC patch series applies native-smp-secondary.patch, which takes the CPU number from Affinity1 because SM8550 numbers cores there.

### 操作步骤

- Read the stock device tree for CPU reg values, GIC ranges and the timer frequency.
- Compare the generated ADT /cpus nodes and their cluster-type values with the intended E/P split.
- On the device, confirm every enabled CPU reaches its entry checkpoint and that timer and IPI handling works per core.

### 开发经验

- The stock tree exposes generic qcom,kryo compatibles; the core types in the SoC dtsi and the stock ABL node names both give the same A510/A715/A710/X3 split.
- Without native-smp-secondary.patch the secondary cores decode their index from Affinity0, which is empty on SM8550.
- configs/vermeer\_defconfig also carries the kernel switches that this profile needs and the shared fragments do not supply: CONFIG\_XNU\_CRYPTO\_BOOTSTRAP="source" over the profile's "prelinked", because prelinked leaves OSKext.cpp calling source\_corecrypto14\_original and source\_corecrypto14\_start\_once while prng\_random.o no longer defines them, and the first pass links no crypto archive. CONFIG\_XNU\_NATIVE\_ADRENO and CONFIG\_XNU\_NATIVE\_UFS stay unset until their board inputs exist.
- kernel\_args carries three switches beyond -v/serial/debug that the reference board also passes: use\_contiguous\_hint=0, kt\_fixed\_zones=120 and -no\_slto\_panic. The first is required because 4 KiB kernel pages plus native-4k-block-split.patch make the pmap hint asserts unsatisfiable; the other two are kernel-internal memory and startup tunables with no board dependency. The command line is 79 bytes, well inside DarwinBoot's 1000-byte limit.
- \[adt.defaults.u32\] vmm-present = 1 tells AMFI that no ApplePMGRNub will appear. The firmware runs with VERMEER\_VENDOR\_HW = 0 and publishes no vendor PMIC/RPMh stack, so without the flag AMFI waits for a PMGR that cannot exist and panics with "AMFI: No PMGR" at ConfigurationSettings.cpp:392.
- \[adt.chosen.u32\] kernel-ctrr-to-be-enabled = 0 is what lets the kernel survive its first /chosen read. ml\_unsafe\_kernel\_text\_init \(osfmk/arm64/machine\_routines.c:3385\) reads that iBoot property at STARTUP TUNABLES rank and leaves \_unsafe\_kernel\_text\_initialized false when it is absent, so dtrace\_sdt\_probes\_restricted\(\) -- the first code that asks, called from sdt\_init\(\) during bsd\_init -- asserts at machine\_routines.c:3379. The assert surfaces through the brk trap handler, which is why the screen shows the machine\_routines.c:3379 text followed by a register dump: pc 0xfffffff00b5b1a48 is \_ml\_unsafe\_kernel\_text.cold.1+0xc and the stack holds \_dtrace\_sdt\_probes\_restricted+0x10, \_sdt\_init+0x34 and \_bsd\_init+0x674. The value 0 means the SoC has no CTRR, so kernel text stays writable by hardware; the reference board declares the same property with the same value for the same reason.
- .github/workflows/package.yml pins the UniXNU checkout to 95ad78129203442c3c14c02336303adbddf8d0a3, the revision the recorded images were built from, instead of tracking the upstream default branch. Upstream main now pins drivers/AppleKeyStoreState to 6ff4f11d, a commit that the UniXNU/AppleKeyStoreState repository does not contain, so an unpinned run dies in its third checkout step with 'upload-pack: not our ref 6ff4f11d' before the tools step. The pin also makes a run reproducible; bump it together with the images it produces.
- With the CTRR property the kernel runs all the way through IOKit and stops on a message rather than an assert: 'Failed to mount root device @IOKitBSDInit.cpp:1001'. frames decode to IOFindBSDRoot.cold.6, IOFindBSDRoot+0xfa0, bsd\_init+0x70c and kernel\_bootstrap\_thread+0x3ec, so the call chain is kernel\_bootstrap\_thread -&gt; bsd\_init -&gt; setconf -&gt; IOFindBSDRoot -&gt; panic. Stage 5 passes; the boot now stops at the first step of stage 6 because no block-storage driver exists to publish an IOMedia for /chosen/root-matching to match.
- The same boot with the framebuffer console enabled adds the missing half of that picture: APFS reports 'apfs: Successfully initialized' and AppleFSCompression reports 'load succeeded' before the root lookup starts. Both components that mount a root are therefore already resident and healthy, so the remaining gap is exactly one block-storage device and nothing else in the filesystem stack.
- With vmm-present set, the boot leaves the boot page tables and AMFI behind and reaches BSD initialisation. The run before this one stopped on kernel\_bootstrap\_thread -&gt; bsd\_init -&gt; sdt\_init -&gt; dtrace\_sdt\_probes\_restricted -&gt; an assertion in machine\_routines.c, which is the CTRR property recorded in the configuration area; the kernel itself, its entry, the ADT handoff and AMFI all run before that point.

### 完成条件

- Every enabled CPU reaches its entry checkpoint.
- Timer and IPI handling works on each enabled CPU.

### 当前范围

- Secondary CPUs have not been started under XNU on this board: the boot is uniprocessor up to the root-device panic, so timer and IPI handling per core is unverified even though the boot CPU runs with interrupts and the platform timer.
- CPU frequency scaling, idle states and the exact GIC redistributor count per cluster are not recorded for vermeer.

### 下一步

- Record the GIC redistributor count and the secondary CPU entry checkpoints once a root device exists; until then the boot panics in IOFindBSDRoot before SMP start.

### 证据

- `source`: [Cluster assignment for cpu0-7 and the enabled UFS, GPU, GMU and GPU SMMU nodes.](https://github.com/qusno1/UniXNU-vermeer/blob/ecd77f51b57d808d55f94691f9dfc986f36075ea/dts/vermeer.dts)

## 内存与 DMA {#memory}

`planned`

### 硬件与依赖

- 16 GiB part. The stock ABL memory node lists usable extents starting at 0x80000000 with carveouts, a 0x38700000 extent at 0x880000000, 0x140000000 at 0x8C0000000 and 0x200000000 at 0xA00000000.
- Splash carveout 0xb8000000 with size 0x2b00000, label cont\_splash\_region, identical to the reference board.
- The stock reserved-memory table has 65 child nodes including PIL gaps, display and Demura memory, the trusted-UI VM regions, ramoops and CPU vectors.

### 配置

- dts/vermeer.dts declares one memory node at 0x80000000 with size 0x80000000 and the splash\_region reservation; the ADT generator requires exactly one contiguous DRAM range, so the high banks are described by the firmware memory map, not by the ADT memory node.
- uefi-vermeer MemoryMapLib adds the high banks as conventional memory: 0x880000000+0x38700000, 0x8C0000000+0x140000000 and 0xA00000000+0x200000000.
- VermeerBootMemoryDxe adds the holes the GCD does not know, in pieces of at least 16 MiB, capped at 1 GiB and below 4 GiB.

### 操作步骤

- Compare the board device tree reservations with the stock reserved-memory node.
- Confirm the GCD map after VermeerBootMemoryDxe reports the expected conventional runs.
- Record the contiguous window DarwinBoot actually receives against \[payload.adt\] owned\_memory\_size.

### 开发经验

- The reference board aborted while clearing memory above 0x8BB300000, so vermeer keeps the small 0x8B8900000 extent \(0x1E00000\) out of the UEFI map until it is verified here.
- The owned-memory request must fit inside the ADT's single contiguous DRAM range, because DarwinBoot places the kernel window there and the boot page tables are built from the ADT. A 4.75 GiB request did not fit the declared 2 GiB and moved the kernel to a high bank, which the configuration area records; the board now requests 256 MiB.
- payload.dram\_size must equal the DTS memory range; the ADT generator refuses a mismatch.

### 完成条件

- All handoff regions are accounted for and the splash region is preserved.
- DarwinBoot reports the intended contiguous window and the kernel enters with the intended DRAM size.

### 当前范围

- The UEFI memory map has not been observed on this board.
- The 0x8B8900000 extent and the top of the first high bank remain untested.

### 下一步

- Read the memory map from the first boot log and reconcile it with the stock reserved-memory table.

### 证据

- `source`: [Stock ABL device tree: memory extents, 0xb8000000 splash carveout and reserved-memory entries.](https://github.com/qusno1/UniXNU-vermeer/blob/ecd77f51b57d808d55f94691f9dfc986f36075ea/firmware/dtb/vermeer.dtb)

## 存储与根卷 {#storage}

`implemented`

组件: `ShengUfs`, `VerifiedRoot`, `VirtioMmioBlock`.

### 硬件与依赖

- UFS host at 0x1d84000 and PHY at 0x1d80000, both standard SM8550 positions confirmed in the stock device tree.
- userdata starts at LBA 2570304 with 4096-byte LBAs and ends at LBA 115933951, measured on the phone.
- UFS device descriptor on the phone: manufacturer\_id 0x0198, number\_of\_luns 6; the host exposes gear and clkscale controls.
- Root volume: the OS and Cryptex1,SystemOS disk images of the target restore image, addressed through the OS profile \[userdata\] windows.
- The apps SMMU context and clocks are shared with the display and WiFi windows the UFS driver owns on request.
- The root image lives in this board's own GPT partition \(unixnu, sda30, start 927471616 x 512B, 67108864 sectors\), holding a SHNGROOT v1 image; Android's userdata is untouched.
- ShengUfs from https://github.com/qusno1/ShengUfs.git at bf21739 in feeds.toml, a fork of the catalog component.

### 配置

- \[userdata\] first\_lba = 2570304, last\_lba = 115936099, lba\_bytes = 4096; these are the OS profile window bounds, not the root partition's.
- \[components\] includes ShengUfs, \[kernel\] archives includes component:ShengUfs, and configs/vermeer\_defconfig sets CONFIG\_XNU\_NATIVE\_UFS=y.
- \[payload\] kernel\_args carries native-ufs-root=1 and vermeer-root-partition=unixnu.
- feeds.toml pins the ShengUfs fork by commit, because that name is not in UniXNU's own feeds and the catalog points at the upstream repository.

### 操作步骤

- Confirm the userdata extent on the device with fastboot getvar partition-size:userdata.
- Verify register access, link state, command completion and known-block reads before attempting a root mount.

### 开发经验

- payload.py refuses native-ufs-root=1 unless the kernel links \_sheng\_pmgr\_run and exactly one sheng-pmgr=2 is present, because the unchanged target AMFI panics with No PMGR otherwise. That check is skipped when the device tree declares vmm-present, which this board does, so native-ufs-root=1 works here with no PMGR stand-in and no sheng-pmgr argument.
- The SoC patch series provides sheng-platform-power.patch, which calls sheng\_pmgr\_run from bsd\_init under XNU\_SHENG\_PMGR.
- The stock GPT image carries no userdata extent: the flasher patches the last partition to NUM\_DISK\_SECTORS-6, so the usable size depends on the phone's part, not on the archive.
- ShengUfs cannot be used unmodified on this board. Its RootLayout.h compiled in the partition name "userdata" because on sheng the root image was flashed over the whole userdata partition; this board keeps Android's userdata and puts the root image in its own partition, so the driver would have looked in the wrong place and reported a manifest mismatch. The fork makes the name a runtime value read from the boot argument vermeer-root-partition, with "userdata" as the default so upstream behaviour is unchanged, and adds the terminator check that the old fixed-size comparison got for free.
- On arm64e the driver is not a standalone kext. build-arm-driver.py routes ShengUfs to build-sheng-source-storage.py, which builds a deferred IOBlockStorageDevice adapter plus the SourceStorage runtime that loads the original IOStorageFamily and APFS and authenticates the root volumes against a signed policy bundle. The first build with the component selected stopped with FileNotFoundError on scripts/policies/ipados-27.0.1-24A446/OS/trusted-key.bin, so the bundle is a build input, not an optional extra.
- scripts/policies/ipados-27.0.1-24A446 holds OS/ and SystemOS/, each with manifest.header.bin \(544 bytes\), trusted-key.bin \(395 bytes\) and verification.json. These are the same files sheng uses, and reusing them is correct rather than convenient: the OS profile pins the same restore image, so os\_image\_sha256 8a12cdad... and systemos\_image\_sha256 d5b4873d... match exactly, both trusted-key.bin files are the same 395-byte anchor \(sha256 73090c0a...\), and the volume UUIDs match the profile. The headers are the header-only form, which is what CONFIG\_XNU\_SOURCE\_STORAGE\_TABLES="userdata" wants: 544 bytes per volume in the boot image, block tables in the userdata image.
- The CONFIG\_XNU\_OWNER\_\* family stays off for now. Those add the owner-signed root audit, the Data volume, the cache mount and the SystemOS union, each of which needs a matching Data seed. They are a separate step from publishing a block device, and enabling them together would make a transport failure indistinguishable from a policy failure.
- The runtime that starts the adapter is board code, not a prelinked kext. patches/xnu/vermeer-source-storage.patch calls native\_source\_storage\_start\(\) from bsd\_init right after vfsinit\(\), guarded by a weak import so a kernel without the runtime still links. That position is required, not convenient: the adapter subclasses the source IOBlockStorageDevice and registers its metaclasses at run time, which only works once the original IOStorageFamily is loaded and the platform expert is published.
- package/SourceStorage.cpp is a reduced copy of sheng's. The sequence is identical - load IOStorageFamily, verify the base-class size against the source header, authenticate the policies, load APFS, register the three deferred metaclasses, then create and start the UFS service - but sheng's boot-log writer, UFS benchmark, process and UI trace probes, diagnostic export and WiFi and Bluetooth staging are left out. Those need a log window, a mounted root and drivers this board does not have yet; carrying them would add 300 KB of board-specific code whose hardware assumptions do not hold here.
- The remaining board files the source-storage build requires are stubs that document what they replace: BootLog.c keeps the writer contract \(state 3 means no log\) so callers can still tell "not configured" from "stuck", and BootReset.c, BootProcessProbe.c, BootUiTraceProbe.c, BootProcessWorker.c, BootWatchdogPolicy.c, BootDiagExport.c, WifiFirmware.c and BluetoothFirmware.c are empty translation units. build-sheng-source-storage.py only checks that each file exists, so an empty one is honest where a fake implementation would not be.
- \[payload\] root\_policies points at build/sheng-source-storage/root-policies.bin and kernel\_args carries native-source-storage=1. Both are required together: without the argument native\_source\_storage\_start\(\) returns immediately, and without the bundle native\_source\_root\_policies\_load\(\) fails and the runtime panics. The bundle is a VROOTB01 container of the OS and SystemOS signed headers, and DarwinBoot writes &\#123;physical, length&\#125; into /chosen/memory-map/RootPolicies, a placeholder that only exists when root\_policies is set.
- One failure in the first storage run was not the blocker it looked like: the bootstrap pass reported "\_corecrypto\_kext\_start, referenced from \_sourcecrypto14\_bootstrap in prng\_random.o" and make exited 2, but build-xnu-4k-baseline.sh continues past that pass and the archive steps run afterwards. The real stop was the missing policy bundle.

### 完成条件

- Host: register, clock, link and SMMU facts match the board inventory.
- Reads: capacity, GPT and known blocks are correct and the OS/SystemOS windows stay inside the root partition.
- Root: the configured volume mounts and launchd starts; writes survive a reboot inside the Data region.

### 当前范围

- No storage driver has run on the phone yet, so nothing about the transport is device-verified. The defconfig and component selection resolve and package.sh --check passes with 76 ordered patches.
- UFS negotiated gear and link speed have not been read from the device; only the descriptor \(manufacturer\_id 0x0198, 6 LUNs\) and the gear/clkscale controls are known.
- Whether the boot chain leaves the UFS power domains and link usable for XNU is unmeasured. If it does not, the QMP-PHY sequence has to be written, and the sheng driver's own header marks that part unqualified.

### 下一步

- Build with ShengUfs linked and read the boot log for the controller bring-up stages: cap/version, SMMU slot, NOP OUT, power mode, LUN ready.

### 证据

- `source`: [userdata geometry, the root-partition argument and the per-profile defconfig selection.](https://github.com/qusno1/UniXNU-vermeer/blob/ecd77f51b57d808d55f94691f9dfc986f36075ea/board.toml)
- `source`: [Pins https://github.com/qusno1/ShengUfs.git at bf21739416d3c28c77e371d5565652b876efe2ce, the fork that selects the root partition by name.](https://github.com/qusno1/UniXNU-vermeer/blob/ecd77f51b57d808d55f94691f9dfc986f36075ea/feeds.toml)

## 显示 {#display}

`planned`

组件: `GopFramebuffer`.

### 硬件与依赖

- 1440x3200 OLED, 32-bit, reported by Android dumpsys display with 60, 90 and 120 Hz modes and HDR support.
- The stock boot argument names the panel qcom,mdss\_dsi\_n11\_42\_02\_0a\_dsc\_cmd.
- Framebuffer handoff: ABL leaves a linear framebuffer and requires /reserved-memory/splash\_region for the panel to keep scanning out.

### 配置

- GopFramebuffer publishes the UEFI GOP framebuffer to the kernel; the firmware sets PcdFrameBufferWidth 1440, PcdFrameBufferHeight 3200 and 32-bit depth from the stock panel timing.
- \[bootimg\] declares only dtb; the boot image device tree is the stock ABL blob, which already carries /reserved-memory/splash\_region, so no dtb\_node re-adds it.
- VERMEER\_VENDOR\_HW = 0 keeps the previous stage's scanout and loads no vendor display driver.
- The kernel links no display stack: CONFIG\_XNU\_NATIVE\_LEGACY\_DISPLAY and CONFIG\_XNU\_NATIVE\_MOBILE\_DISPLAY are unset, so build-xnu-4k-baseline.sh links neither libNativeLegacyDisplay nor libGopFramebuffer.

### 操作步骤

- Confirm the framebuffer base, stride and pixel format as ABL hands them over.
- Check that a known frame appears with correct geometry and colors before enabling any panel driver.
- Record brightness and backlight behaviour separately from scanout.

### 开发经验

- The firmware's own panel constants come from the stock N81A panel XML, but the boot argument of this board names an n11 panel; the XML set and the panel name do not correspond and must be re-imported for vermeer.
- Enabling the stock vendor display chain \(VERMEER\_VENDOR\_HW = 1\) reaches ClockDxe and blanks the panel while the backlight stays on, as on the reference board.
- The prelink reported one stub for com.apple.driver.AppleM2ScalerCSCDriver at original 0xfffffe000ad94128. The address is in the native kernel's space, not in any component: AppleM2ScalerCSCDriver is the referencing owner, and the missing side is the legacy-display binding that provides IOMobileFramebufferLegacy. Supplying it means importing the reference board's kernel-side display integration \(build-gop-legacy-display-27.py, kits/sheng sources and the three arm64e ABI fixtures\), so the profile's prelink regression policy is suspended for this board in board.toml \[os\_overrides\] and the stub count stays visible in kernel/kernel.macho.json.

### 完成条件

- A known frame appears with correct geometry and colors.
- Userland presentation and backlight control work.

### 当前范围

- No frame has been shown from an image built in this repository.
- The framebuffer stride is assumed equal to the width; it is unverified for this panel.
- The panel XML and the vendor display chain are not imported for vermeer.
- The kernel-side display integration is absent, so the prelink stubs AppleM2ScalerCSCDriver's reference to IOMobileFramebufferLegacy and the profile's regression policy cannot pass; it is suspended in \[os\_overrides\] until this stage provides the archive.

### 下一步

- Import the legacy-display binding and its ABI fixtures, enable CONFIG\_XNU\_NATIVE\_LEGACY\_DISPLAY, then restore the profile's regression policy and confirm its required IOMobileFramebufferLegacy branch.

### 证据

- `source`: [splash\_region reservation matching the stock device tree.](https://github.com/qusno1/UniXNU-vermeer/blob/ecd77f51b57d808d55f94691f9dfc986f36075ea/dts/vermeer.dts)

## 输入 {#input}

`planned`

### 硬件与依赖

- Touch controller goodix,gt9916 on the active I2C bus, from qcom,i2c-touch-active in the stock device tree.
- Touch panel maxima in the stock tree: goodix,panel-max-x 0x438, goodix,panel-max-y 0x960.
- Trusted-touch configuration: SPI IRQ 0x239 and the pvm touch environment.

### 配置

- No input driver is selected; the current image has no touch or button path.
- ShengHidInput and ShengNovatekTouch are sheng drivers for a different controller and are not selected here.

### 操作步骤

- Confirm the touch IC and its bus, interrupt and reset lines from the stock device tree.
- Select an input component that matches the controller, or implement one for gt9916.
- Verify contact mapping to the display, stable IDs and release events.

### 开发经验

- The touch controller is goodix,gt9916, not the Novatek part the reference board uses, so ShengNovatekTouch does not apply.
- The stock tree also carries a second touch node with much larger maxima, which is the firmware's own scaling of a different panel variant; only the active node counts.

### 完成条件

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive, and buttons produce expected HID reports.

### 当前范围

- No input driver exists for this board and no touch input has been observed.

### 下一步

- Implement or select a gt9916 input driver and record its bus, interrupt and coordinate mapping.

### 证据

- `source`: [qcom,i2c-touch-active = goodix,gt9916 and the active touch node maxima.](https://github.com/qusno1/UniXNU-vermeer/blob/ecd77f51b57d808d55f94691f9dfc986f36075ea/firmware/dtb/vermeer.dtb)

## GPU {#gpu}

`planned`

### 硬件与依赖

- Adreno 740 in the SM8550 GPU subsystem. The stock device tree names it qcom,adreno-gpu-gen7-2-1 at 0x3d00000.
- GMU at 0x3d69000 on this board, with IPC, HFI and GMU interrupts at SPI 0x130 and 0x131.
- GPU SMMU at 0x3da0000 with gfx3d\_user, gfx3d\_lpac and gfx3d\_secure contexts.
- ZAP firmware, GPU power votes and reserved GPU memory, none of which are imported for this board.

### 配置

- Adreno740 and AdrenoMetal are not selected in \[components\]; \[kernel\] archives has no entry for them, and configs/vermeer\_defconfig turns CONFIG\_XNU\_NATIVE\_ADRENO off over the SoC fragment.
- dts/vermeer.dts keeps the gpu, gmu and gpu\_smmu nodes enabled so the hardware description is exported.

### 操作步骤

- Import the ZAP and GPU firmware inputs and record their hashes in proprietary-files.txt.
- Record GPU and GMU power votes and the GPU SMMU window layout for this board.
- Select Adreno740, its dependencies and AdrenoMetal together with their archive entries and turn CONFIG\_XNU\_NATIVE\_ADRENO back on.

### 开发经验

- The shared SoC dtsi names GMU at 0x3d6a000 with an rscc window at 0x3d50000, but the stock vermeer device tree places GMU at 0x3d69000 with reg &lt;0x3d68000 0x37000&gt;, &lt;0xb280000 0x10000&gt;, &lt;0x3d40000 0x10000&gt;: the same end address, a different rscc window. The shared register set cannot be reused for this board without correcting that offset.
- The GPU is the same Adreno 740 generation as the reference board, so the driver family applies, but its board inputs are not transferable.

### 完成条件

- GPU submissions complete, mapping and fence handling are correct, a known image renders, and the selected Metal client presents it.

### 当前范围

- No GPU driver is selected and no GPU work has run on this board.
- The GMU offset difference against the shared SoC description is unresolved.

### 下一步

- Record the GMU and GPU register windows from the stock device tree and reconcile them with the shared SoC dtsi.

### 证据

- `source`: [qcom,gmu@3d69000, qcom,kgsl-3d0@3d00000 and qcom,kgsl-iommu@3da0000 with their interrupts and register ranges.](https://github.com/qusno1/UniXNU-vermeer/blob/ecd77f51b57d808d55f94691f9dfc986f36075ea/firmware/dtb/vermeer.dtb)

## 网络 {#network}

`planned`

### 硬件与依赖

- FastConnect 7800 \(WCN7850\), the SM8550 connectivity pair.
- DMA window requirement: 128 MiB at IOVA 0x10000000 in a dedicated SMMU context, owned by the storage driver's SMMU takeover on the reference board.

### 配置

- dts/vermeer.dts exports a wlan node with compatible qcom,wcn7850 and unixnu,adt-name wlan, so the radio is visible to launchd.
- No WiFi component is selected; Ath12kWifi and the MHI boot path are not in \[components\].

### 操作步骤

- Confirm the WCN7850 variant and its firmware package for this board.
- Provide the SMMU stage 1 window the endpoint needs before scanning.
- Verify scanning, association and sustained traffic.

### 开发经验

- The radio is exported in the device tree but nothing binds to it yet, so the node is inert.

### 完成条件

- Scanning, association, address configuration and sustained receive/transmit traffic pass with the selected firmware.

### 当前范围

- No network driver or firmware input exists for this board.

### 下一步

- Select Ath12kWifi with the board's firmware package and record the SMMU window requirement.

### 证据

- `source`: [wlan and bluetooth nodes with the WCN7850 compatible values.](https://github.com/qusno1/UniXNU-vermeer/blob/ecd77f51b57d808d55f94691f9dfc986f36075ea/dts/vermeer.dts)

## 音频 {#audio}

`planned`

### 硬件与依赖

- ADSP, GPR, GLINK and shared memory services of SM8550.
- The stock tree names a kalama-mtp-snd-card, which is the reference sound card and not this board's codec wiring.

### 配置

- No audio component is selected and no audio route is declared.

### 操作步骤

- Record the codec, its bus and its power supplies for vermeer.
- Select the audio components and declare each route before playback tests.

### 开发经验

- The stock sound card name comes from the reference platform, so it does not describe the K70 codec wiring.

### 完成条件

- Each declared route carries the selected audio format through playback or capture and handles start and stop.

### 当前范围

- Audio hardware and routes are not inventoried for this board.

### 下一步

- Identify the codec and its bus before selecting any audio component.

### 证据

- `source`: [Stock audio node names, which reference the kalama-mtp sound card.](https://github.com/qusno1/UniXNU-vermeer/blob/ecd77f51b57d808d55f94691f9dfc986f36075ea/firmware/dtb/vermeer.dtb)

## 电源 {#power}

`planned`

组件: `AppleKeyStoreState`.

### 硬件与依赖

- PMIC, RPMh and regulator ownership are inherited from the SM8550 platform; the vendor drivers that would drive them are disabled in the firmware.
- AppleKeyStore platform state callbacks are needed by the kernel for keystore initialisation.

### 配置

- AppleKeyStoreState is selected in \[components\] and takes its archive entry in \[kernel\] archives.
- No board power service is implemented; sleep and resume are not supported, so the ADT does not declare sleep support.

### 操作步骤

- Record the regulators and power domains each peripheral needs.
- Verify battery and charger readings against Android before claiming any power result.

### 开发经验

- With the vendor hardware stack disabled, nothing in the firmware programs RPMh or the regulators, so the board runs on the state the previous boot stage left.
- Because there is no PMGR to publish, the ADT declares vmm-present in \[adt.defaults.u32\]. Without it AMFI waits for an ApplePMGRNub and panics with "AMFI: No PMGR" at ConfigurationSettings.cpp:392, which is exactly what the board hit once the kernel got past the pmap. payload.py states the same rule for native-root boots, and the reference board declares the flag for the same reason.

### 完成条件

- Declared power controls and battery readings match observations, and each claimed sleep or resume transition restores its dependent peripherals.

### 当前范围

- No power, battery or sleep result exists for this board.
- AppleKeyStoreState is selected but has not run on the device.

### 下一步

- Record the regulator and PMIC ownership from the stock device tree before adding a power service.

### 证据

- `source`: [AppleKeyStoreState selection and the absence of board power services.](https://github.com/qusno1/UniXNU-vermeer/blob/ecd77f51b57d808d55f94691f9dfc986f36075ea/board.toml)

## 镜像组装 {#packaging}

`implemented`

组件: `XnuPrelink`.

### 硬件与依赖

- Target restore image from the OS profile: iPadOS 27.0.1 build 24A446 for iPad17,3, including the profile's url and fetch list.
- Platform seed supplied at build time, never stored in the repository.
- Prelink inputs from the OS profile: kernelcache pin, slide, early security init address, roots and the fileset reference.
- The fileset reference kernel named by the profile's prelink extra\_args. It is not a profile input that ships ready: \[kernel\] archives builds it with build-fileset-release-reference.py --tree . --lto, which must run before the prelink step.

### 配置

- \[ipsw\] comes from the OS profile; board.toml has no \[ipsw\] table, so the profile's url, product, device\_class, chip\_id and fetch list apply unchanged.
- \[payload\] volume VERMEER, size\_mib 192, loader firmware, panic\_screen on, kernel\_args -v, serial=3, debug=0x14e.
- scripts/package.sh runs the fixed steps deps, preflight, patches, build, pack and verify, and reads every board value from board.toml.

### 操作步骤

- Run scripts/package.sh --check --os 27 --uefi ../uefi-vermeer to resolve dependencies, configuration and patches without building.
- Run scripts/package.sh --os 27 --uefi ../uefi-vermeer on macOS to produce the kernel, payload and boot image.
- Inspect payload.json, boot.json and package.manifest.json before flashing anything.

### 开发经验

- The kernel step needs Xcode; this repository cannot produce kernel.macho on a Linux or Windows host.
- The payload must stay under the DarwinBoot command-line limit of 1000 bytes and every argument must match the accepted character set.
- scripts/package.sh and the board preflight script must keep mode 100755. Committed as 100644 they made the packaging workflow stop at its first command with 'scripts/package.sh: Permission denied', because the workflow runs the file directly rather than through an interpreter.
- scripts/package.sh --check --os 27 --uefi ../uefi-vermeer resolves dependencies, configuration and the ordered patch series and stops before building.
- patches/xnu/vermeer-kernel-stack-shift.patch publishes \_unixnu\_kernel\_stack\_shift. XnuPrelink's kit fixture fileset-24A446-symbols.json binds the original AppleMobileFileIntegrity GOT slot 0xfffffe0008136458 to that name, and the fixture is keyed by the same kernelcache pin as this profile; reviewed\_sites rejects the build rather than falling back, and --allow-missing does not cover reviewed sites.
- patches/xnu/vermeer-mountroot-diagnostic.patch bounds bsd\_init.c's root retry loop: after eight failed vfs\_mountroot\(\) calls it panics with the last errno. The loop only prints through kprintf, and this board has neither a UART nor a video console, so a boot that reaches the loop would sit there silently and look exactly like a hang earlier in bsd\_init. The panic screen turns that into a photograph, which is what tells stage 5 apart from a failure before it. The patch exists only for the pre-storage state and is expected to go away once the UFS root path works; it applies after the whole shared series, and its context was rebuilt from the same ordered patches the kernel step applies \(offline-\*, sheng-platform-power, zzz-boot-progress\).
- patches/xnu/vermeer-framebuffer-console.patch keeps XNU's text console on the framebuffer, which is what turns one panic message per boot into a scrolling kernel log. The mechanism is Apple's own: PE\_create\_console\(\) calls PE\_initialize\_console\(&amp;PE\_state.video, kPEGraphicsMode\) because DarwinBoot fills boot\_args.Video, so gc\_graphics\_boot is TRUE when startup\_initialize\(\) runs initialize\_screen\(NULL, kPEAcquireScreen\); the kPEAcquireScreen branch then computes graphics\_now = gc\_graphics\_boot &amp;&amp; \!gc\_desire\_text = TRUE and calls gc\_enable\(\!graphics\_now\) = gc\_enable\(FALSE\), and gc\_enable\(FALSE\) sets disableConsoleOutput = TRUE unless the console is serial. Every kprintf and IOLog after that point is discarded, which is exactly what IOFindBSDRoot's 30 s service wait and its ROOTDEVICETIMEOUT \(120 s in a DEBUG build\) produced: two and a half minutes with no output at all. kPETextScreen is XNU's switch for this and calls gc\_enable\(TRUE\) after checking console\_is\_serial\(\) == FALSE, gc\_acquired == TRUE and gc\_graphics\_boot == TRUE - all three true one line after kPEAcquireScreen, which is why the patch adds case kPETextScreen immediately after it, preceded by switch\_to\_video\_console\(\) to keep the switch off its serial early-out. gc\_enable\(TRUE\) allocates its character buffers behind a vm\_initialized guard, so it is safe at that point in startup. Nothing on ARM calls kPETextScreen \(its only caller is bsd/dev/i386/km.c\), which is why every ARM port of this tree shows no kernel output. Verified on hardware: the built kernel carries the patch as mov w1,\#3 followed by the call at 0xfffffff00b57facc/0xfffffff00b57fad0 inside kernel\_bootstrap\_thread, and the phone now prints the whole boot.
- The visible log turns the boot into evidence. It shows iBoot 7.0.0 starting the task, AMFI reporting 'Booted in a VM' \(which is the vmm-present property doing its job\), AMFI/Sandbox/vnguard loading, the MRC framework, zone\_init with a 164 MB pool, apfs\_module\_start and 'apfs: Successfully initialized', AppleFSCompressionTypeZlib loading, and finally the serialised root match carrying IOProviderClass = IOMedia with the profile's OS volume UUID. The two components that mount a root are therefore already running; what is missing is only a block device for them to sit on.
- The kernel reached the pmap hint asserts and panicked there. arm\_vm\_init.c sets ARM\_PTE\_HINT in ptmp only when use\_contiguous\_hint is true, and the two asserts immediately below assume 16 KiB granule semantics. This port maps 4 KiB kernel pages, and native-4k-block-split.patch pre-fills the L3 entries of a split 2 MiB block without a hint, so the compare at arm\_vm\_init.c:1113 failed with kva\_active=1, i=400, va=0xfffffff007190000. The board now passes use\_contiguous\_hint=0, the switch PE\_parse\_boot\_argn reads at arm\_vm\_init.c:2077 and the same value the reference board uses, so the hint branch and both asserts are skipped. kt\_fixed\_zones=120 and -no\_slto\_panic ride along: both are memory/startup switches with no board hardware dependency, and the reference board passes them for this profile.
- scripts/patch-xnu-entry-probe.py overrides the UniXNU copy because the device scripts directory is assembled into the tree last. The upstream parser takes any three-field llvm-nm line, and an MH\_FILESET kernel makes llvm-nm print 'Symbols for &lt;bundle id&gt;:' headings that match that shape, so the payload step failed with int\('Symbols', 16\).
- Overriding \[ipsw\] with another product broke the prelink pin: the profile's kernelcache digest belongs to its own image. Keeping the profile image keeps every pin valid.

### 完成条件

- Kernel and prelink succeed, the payload contains all declared inputs, and the boot image matches the bootloader format and size limit.

### 当前范围

- No image has been produced in this repository: out/ holds only a firmware build and an unresolved tree.
- The 192 MiB payload size may exceed this ABL's fastboot buffer; a community port for the same phone reports using 64 MiB.

### 下一步

- Run the packaging script on a macOS host with the platform seed and record the three image hashes.

### 证据

- `source`: [Fixed packaging steps and the board.toml keys they read.](https://github.com/qusno1/UniXNU-vermeer/blob/ecd77f51b57d808d55f94691f9dfc986f36075ea/scripts/package.sh)
- `host`: [Profiles, component sources and patch order resolve; the kernel archive plan reported the missing Adreno740 and AppleKeyStoreState entries before this record.](https://github.com/qusno1/UniXNU-vermeer/blob/ecd77f51b57d808d55f94691f9dfc986f36075ea/unixnu.lock)
  Command: <code>./unixnu status --json -D ../UniXNU-vermeer</code>. Revision: `c8027115706c3ceac37e45c9b81db447bbc5ceba`.

## 诊断 {#diagnostics}

`planned`

### 硬件与依赖

- The phone has no UART; the firmware must expose its log on screen.
- The boot path reports through the framebuffer and the panic screen.

### 配置

- kernel\_args include -v, serial=3 and debug=0x14e.
- \[payload\] panic\_screen = true, so the panic screen is patched into the payload copy of the kernel.

### 操作步骤

- Capture the screen at each bring-up checkpoint: firmware output, UniXNU menu, payload parsing, loader handoff, kernel entry, root mount, launchd.
- Record the last confirmed stage and the image hash for every attempt.
- Run fastboot boot, since it writes no partition and can be retried; reboot to the bootloader with the hardware keys when the firmware stops responding.

### 开发经验

- The reference platform documents an Advanced Logger with QR export as the fallback log channel; this board's firmware has not wired it.
- After the firmware starts, the phone disappears from both adb and fastboot: the firmware replaces those USB stacks, so the screen is the only channel until a log export exists.
- The panic screen is what makes the last two failures readable at all. Each run it delivered a message plus a frame chain that resolves to symbols in the same kernel.macho, which is enough to name an entire call path without a serial port: the CTRR assert resolved to machine\_routines.c:3379 with dtrace\_sdt\_probes\_restricted and sdt\_init on the stack, and the root-device stop resolved to IOFindBSDRoot.cold.6, IOFindBSDRoot+0xfa0, bsd\_init+0x70c and kernel\_bootstrap\_thread+0x3ec.
- Keep notes/kernel-&lt;image&gt;.nm.txt \(llvm-nm -n of that image's kernel.macho\) next to each build: the panic screen prints VAs, and one kernel symbol table turns them into names. The kernel is an MH\_FILESET, so llvm-nm prints per-bundle 'Symbols for' headings and a naive three-field parser reads the heading as a symbol. The addresses shift between builds, so a symbol table is only valid for the image it was taken from - the root-device frames moved by 0x10 between two builds of the same source.
- A defect that only prints through kprintf is invisible here. IOFindBSDRoot waits ROOTDEVICETIMEOUT \(120 s in a DEBUG build\) after a 30 s service wait before it panics, so a run that looks frozen may still be inside a timeout; with the console enabled the wait is now visible as it happens.
- patches/xnu/vermeer-framebuffer-console.patch makes the kernel log visible on the panel, and hardware confirmed it: the first boot with it showed the entire path from 'iBoot version 7.0.0' through APFS initialisation to the serialised root match. The panic screen and the text console are complementary: the console scrolls everything, the panic screen survives a panic that happens before or after the console is up. Both read and write the same framebuffer DarwinBoot advertises in boot\_args.Video, so neither needs a serial port.
- The same log surfaces /chosen properties XNU probes and does not find: AppleARMBootPerf cannot find its profile handoff region, and AppleARMSFRManifest cannot open /chosen/secure-boot-hashes or find /chosen/iBoot, so it fails to publish the SFR manifest. \(Read carefully: the component is the ARM SFR manifest, not an RSK one, and the strings were confirmed against kernel.macho rather than the photograph.\) None of those errors is fatal and the boot passes them, so they do not block a root device. They bite one stage later: launchd runs /sbin/mount and the child exits 66 without a published /chosen/boot-manifest-hash. \[adt.chosen.bytes\] boot-manifest-hash now carries a development-only 48-byte bring-up identity, the SHA-384 of 'VermeerBringup.BootSet.v1\\0', following the same pattern marble uses for 'MarbleBringup.BootSet.v1\\0' and sirius for 'UkeBringup.BootSet.v1\\0'; sirius records that supplying it made mount-phase-1 and mount-phase-2 pass and launchd report 'Early boot complete'. It is opaque bring-up material, not an owner signature, and it authenticates nothing: this board's root stays unauthenticated.
- Three boot attempts are recorded for this board, covering stages 1 through 5.

### 完成条件

- Each claimed milestone has a reproducible command, a matching source and image revision, and an accessible result.

### 当前范围

- No text log has been captured from this board; every result rests on a screen observation.
- Stage 6 has no checkpoint beyond the root-device panic, and stage 7 has none.

### 下一步

- Wire the firmware log export, which is what would turn the current one-message-per-run cycle into a trace of the whole boot.

### 证据

- `source`: [Kernel arguments, panic screen setting and the serial console selection.](https://github.com/qusno1/UniXNU-vermeer/blob/ecd77f51b57d808d55f94691f9dfc986f36075ea/board.toml)
- `device`: [The UniXNU menu appeared after the bootloader sent 1788 KB, confirming the UEFI and UniXNU checkpoints of the bring-up order.](https://github.com/qusno1/UniXNU-vermeer/blob/ecd77f51b57d808d55f94691f9dfc986f36075ea/reports/2026-11-09-uefi-menu.md)
  Command: <code>fastboot boot boot.img</code>. Revision: `b1c88c0808db7955a9ffd0e55ff35489e34bc25b`.
- `device`: [With the framebuffer console patch the panel scrolled the whole kernel boot: iBoot 7.0.0 task start, AMFI 'Booted in a VM', AMFI/Sandbox/vnguard, the MRC framework, zone\_init 164 MB, apfs successfully initialized, AppleFSCompressionTypeZlib load succeeded, then the serialised root match and the root-device panic. Image boot.img sha256 7078c8ca065827ee72aaf13eef6be557b45eee5c38beec2f864af450768238d2.](https://github.com/qusno1/UniXNU-vermeer/blob/ecd77f51b57d808d55f94691f9dfc986f36075ea/reports/2026-11-10-framebuffer-console-and-apfs.md)
  Command: <code>fastboot boot boot.img</code>. Revision: `44c5e2579fd0b6a35b0bbbe3d6a1f5a0f4e0e6c3`.

</div>
