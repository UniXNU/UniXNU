# Xiaomi 12 \(cupid\)

[obaosp/UniXNU-cupid](https://github.com/obaosp/UniXNU-cupid)

<div v-pre>

Xiaomi 12 \(cupid, SM8450\) running iOS 27.0.1 \(24A446, arm64e\) under an iPhone17,2 / D94AP identity. The kernel reaches BSD init; the active milestone is SM8450 UFS storage and the root volume.

源记录: [porting.toml](https://github.com/obaosp/UniXNU-cupid/blob/d4514c60f2788efa1677441c54de63820b17c1b0/porting.toml), `d4514c60f2788efa1677441c54de63820b17c1b0`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `implemented` |
| [固件与启动](#firmware) | `host-verified` |
| [CPU 与中断](#cpu) | `implemented` |
| [内存与 DMA](#memory) | `implemented` |
| [存储与根卷](#storage) | `planned` |
| [显示](#display) | `planned` |
| [输入](#input) | `planned` |
| [GPU](#gpu) | `planned` |
| [网络](#network) | `planned` |
| [音频](#audio) | `planned` |
| [电源](#power) | `planned` |
| [镜像组装](#packaging) | `host-verified` |
| [诊断](#diagnostics) | `planned` |

## 配置 {#configuration}

`implemented`

### 硬件与依赖

- SM8450 SoC source pin; iPhone-flavoured iOS 27.0.1 build 24A446 profile; cupid defconfig and device tree.
- UniXNU main does not ship an iPhone OS profile: this repository carries profiles/os/ios-27.0.1-24A446 and installs it into the checkout.

### 配置

- board.os\_profile = ios-27.0.1-24A446; board.soc = SM8450; board.soc\_source = sm8450; schema\_version = 2.
- profiles/os/ios-27.0.1-24A446 is the iPhone17,2 \(D94AP\) 24A446 profile with the upstream XnuPrelink 24A446 fixture retargeted to the iPhone collection. It is the only OS profile in this repository.
- NOT the shipped ipados-27.0.1-24A446 profile: different IPSW, original kexts and ADT identity.

### 操作步骤

- Read https://unixnu.com/porting/device-repository and https://unixnu.com/porting/records.
- Run scripts/install-os-profile.sh ../UniXNU to install the iPhone 27 profile into the UniXNU checkout.
- Run ./unixnu defconfig cupid\_ios27\_defconfig -D ../UniXNU-cupid, ./unixnu fetch -D ../UniXNU-cupid, ./unixnu status --json -D ../UniXNU-cupid.
- Run .github/workflows/userdata.yml on a macOS runner to build the iOS 27 userdata image; download the chunks and flash it with fastboot flash userdata.

### 开发经验

- The upstream 24A446 fixture's data entries: the 13 vnodeop\_desc descriptors are retargeted to the iPhone 27 collection by their unique vnop\_\* name strings and vdesc\_name slots; the 8 metaclass slots and \_gIODTPHandleKey, \_audio\_active, \_tk\_rawcc, \_tk\_nin and \_gPESerialBaud remain to be retargeted by the reference data map/source consumers. notes/IOS27-SHENG.md records the fixture/recipe, the generic sheng 24A446 bring-up hunks and the relevant 4 KiB/arm64e/prelink/security/bring-up docs.
- An iPhone profile is required for a phone: iPadOS presents iPad product identity, idiom and display assumptions that SpringBoard and UIKit read from /product.
- Arrays replace inherited arrays: board.toml repeats every selected component, configuration fragment and patch series entry.
- The macOS workflow repairs two stale UniXNU submodule gitlinks before fetch: ArmCpu 2e11cda/16040839 to the existing 93a5030, and AppleKeyStoreState 6ff4f11 \(gone from the remote\) to main 58e5461. The latter blocked build 42779052201 in the resolve step. The macOS workflow builds the EDK II package \(UniXNU.efi\) after the kernel, so a push that changes board.toml, profiles, configs or the workflow itself exercises image assembly without the phone.
- scripts/build-cupid-dtb.sh builds the firmware DTB from the LineageOS waipio-v2 + cupid overlay \(cpp + dtc + fdtoverlay\), sha256 6246e11cc2867946183b7e453797d5ec0fb3c49c6297115f2605a7bf8c0e0b50. It is not byte-identical to the stock vendor\_boot base+dtbo merge \(956745 bytes, sha256 ea574733...\): the stock base is a larger vendor tree. The device reports dtb\_idx 10 \(Waipio v2\) and revision 2.2. The live ABL FDT was pulled from the phone \(sha256 3d669081f48c6a810f0d95f7c5fa37d62dcb1c40a9d6fe4eb8b79bc24bebf7f0, 773371 bytes, model 'Cupid based on Qualcomm Technologies, Inc SM8450'\) and scripts/build-cupid-dtb.sh accepts it with UNIXNU\_CUPID\_LIVE\_FDT; the compiled tree now patches the cupid root identity and measures 451042 bytes \(sha256 7604f605...\).
- macOS cpp mis-parses -x assembler-with-cpp \(cc: no input files\); the DTB script now defaults to clang -E and the workflow builds cupid.dtb before the kernel so a tree failure is not hidden behind a 19-minute kernel step.
- notes/FASTBOOT.md records the one-boot procedure: fastboot boot loads the image into RAM, nothing is flashed, and the unlocked state must be confirmed before the Gunyah PAC test.
- The workflow applies patches/unixnu/\*.patch to the UniXNU checkout before building; patches/unixnu/0001-patch-xnu-entry-probe-skip-nm-headers.patch makes the entry-probe parser skip non-hex nm header lines.
- The payload step passes --uefi ../uefi-cupid: panic\_screen=true needs Mu-Silicium FrameBufferSerialPortLib/Font.h; without it patch-xnu-entry-probe.py aborts before writing the volume.
- notes/first-boot-2026-11-07.md is the first device boot result: fastboot accepted the image but the screen stayed black, traced to the FD base 0xA7100000 versus the stock UEFI ELF window at 0xA7000000 size 0x2A2000.
- notes/first-uefi-boot-2026-11-07.md records the first successful UEFI boot: header v4 reaches BootShim and the UniXNU menu on cupid; the payload volume is not published \(no SimpleFileSystem\), so the menu falls back to BDS.
- The workflow applies patches/darwinboot/0001 inside the DarwinBoot submodule after the kernel step has fetched it, so the firmware build sees the window diagnostics.
- notes/pac-trap-2026-11-07.md records the first XNU start and the Gunyah trap on the EL1 PAC key write; the next image disables the key-programming block.
- The panic instruction was decoded as 0xd51be228 \(msr CNTP\_CTL\_EL0\), not PAC: the screen wrapped instr=d5 onto the next line. The timer is the current blocker; the record was corrected.
- The macOS workflow uploads cupid-native-symbols \(unstripped native kernel, kernel.json and kernel.map.json\) so an unmatched target can be reviewed against real symbols offline.
- The iOS 27 kernel passes every remaining import stub and reaches BSD init. It now panics in IOKitBSDInit.cpp "Failed to mount root device": no IOMedia carries the iOS 27 OS volume UUID. CONFIG\_XNU\_NATIVE\_UFS is not set, package/Sm8450Ufs is only headers plus a host test, and the iOS 27 SHNGROOT userdata image is not installed. notes/ROOT-UFS.md records the milestone; patches/xnu/ufs-probe.patch reports the SM8450 GCC/UFSHCI state read-only.

### 完成条件

- status resolves ios-27.0.1-24A446 with arch arm64e, the sm8450 SoC source and the cupid\_ios27 defconfig; the iPhone17,2 24A446 kernelcache prelinks with the retargeted fixture and the kernel reaches BSD init.

### 当前范围

- The iPhone17,2 identity advertises a 1320x2868 display; cupid is 1080x2400. Display identity is corrected with the panel milestone.

### 下一步

- Boot the unixnu-ufs-probe build, record the GCC/UFSHCI values, then implement and enable the SM8450 UFS block driver and flash the iOS 27 userdata image.

### 证据

- `source`: [Resolve, arm64e kernel build, iPhone17,2 prelink and EDK II package steps used by the host-verified runs.](https://github.com/obaosp/UniXNU-cupid/blob/d4514c60f2788efa1677441c54de63820b17c1b0/.github/workflows/macos.yml)
- `device`: [ro.board.platform=taro, ro.boot.hardware.sku=cupid, dtb\_idx=10 \(Waipio v2\), dtbo\_idx=19, cpuid=0x0000043252a25a21, serialno=1cb22738; /sys/devices/soc0 revision 2.2.](https://github.com/obaosp/UniXNU-cupid/blob/d4514c60f2788efa1677441c54de63820b17c1b0/notes/device-2026-11-07.md)
  Command: <code>adb shell su -c 'getprop | grep ro.boot'</code>. Revision: `4730e3b1fb52e1238a5d370bdc1f381622033de9`.

## 固件与启动 {#firmware}

`host-verified`

组件: `DarwinBoot`.

### 硬件与依赖

- A Mu-Silicium UEFI fork for cupid \(uefi-cupid\), cupid's stock UEFI/ABL firmware and the live ABL device tree.
- PSCI SMC entry, GOP framebuffer handoff and the memory map UniXNU may own.

### 配置

- board.toml \[firmware\] names config cupid, dsc Platforms/Xiaomi/cupidPkg/cupid.dsc and the SILICIUM\_UEFI.fd path.
- Firmware DSC/FDF must embed UniXNU, UniXNUDxe, DarwinBoot, UniXNURamDiskDxe, DiskIoDxe and FAT support.

### 操作步骤

- Fork uefi-sheng into uefi-cupid, add cupidPkg and its Binaries/cupid module from the stock UEFI image.
- Build with ./unixnu build firmware -D ../UniXNU-cupid --uefi ../uefi-cupid.
- Record the firmware revision, FD size and the handoff memory map.

### 开发经验

- uefi-cupid is forked from UniXNU/uefi-sheng and carries Platforms/Xiaomi/cupidPkg: CUPID\_VENDOR\_HW = 0, USE\_CUSTOM\_DISPLAY\_DRIVER = 0, WaipioPkg.dsc.inc \(SM8450, 8 cores, GIC 0x17100000\), SimpleFbDxe on ABL's 1080x2400 scan-out, and UniXNUPkg + DarwinBoot + UniXNURamDiskDxe.
- The memory and configuration maps are copied from the SM8450 ingres platform \(same DRAM base, FD window and SoC carveouts\) and are REQUIRED to be replaced with cupid's stock uefiplat.cfg.
- The minimal configuration deliberately omits Binaries/cupid, so no stock vendor module is needed to build the firmware volume; vendor clocks, UFS, USB, charger and the stock display chain are a later CUPID\_VENDOR\_HW = 1 step.
- The stock splash\_region \(0xb8000000 + 0x2b00000\) is present in waipio display DTSI and is assumed in the payload and boot image.

### 完成条件

- Firmware image builds, enters UniXNU, publishes the framebuffer and preserves documented reservations.

### 当前范围

- cupidPkg builds and produces SILICIUM\_UEFI.fd, but the memory map and FD base are still the ingres SM8450 values and vendor hardware is off; neither is device-verified.

### 下一步

- Build firmware with ./unixnu build firmware --uefi ../uefi-cupid and record the FD size; then import Binaries/cupid from the HyperOS archive for CUPID\_VENDOR\_HW = 1.

### 证据

- `source`: [cupidPkg platform definition: WaipioPkg include, 1080x2400 frame buffer, UniXNU/DarwinBoot/UniXNURamDiskDxe components, CUPID\_VENDOR\_HW = 0.](https://github.com/obaosp/uefi-cupid/blob/bce96f77d07ec90a516432df466b8cd3af7272fc/Platforms/Xiaomi/cupidPkg/cupid.dsc)
- `host`: [Corrected FD window: firmware built with FD\_BASE=0xa7000000, FD\_SIZE=0x2a2000, FD\_BLOCKS=674; BootShim decompresses to 0x2a2000 with text\_offset 0xa7000000, image\_size 0x2a20c0 and the ARM64 magic; boot.img sha256 4b9643054648573c93fba74a8ae97e06bd39be3b789744cd4b92b7c14125f1d7 \(186036224 bytes\) and payload.img sha256 8792987fde257e3707530328756a17daf00b6f46687b68ebed31126e40971536 \(184549376 bytes\).](https://github.com/obaosp/UniXNU-cupid/actions/runs/42391718599)
  Command: <code>./unixnu build firmware -D ../device --uefi ../uefi-cupid &amp;&amp; ./unixnu build payload ... &amp;&amp; ./unixnu bootimg ...</code>. Revision: `b83e634bd63489b7c7ff3f976ca732ea80c98c03`.
- `host`: [payload.img 184549376 bytes sha256 f9daa8c8e136321ffe65f1f968284c58318f81751804f1ce7c9778a5f1e271ab; boot.img 186036224 bytes sha256 65cfa2fbe4c396f19ce19f58953c144e56240cd9e1c8fb01d9f5b50423c8f9a8. ANDROID\! header v0, pagesize 4096, kernel\_addr 0x8000, tags 0x1e00000, ramdisk equals payload, kernel region is gzip\(1028417\) plus cupid DTB\(451126, ends exactly at kernel\_size\). Payload FAT contains EFI/UniXNU/unixnu.toml with an iOS 27 entry and Payloads/kernel.macho 93667328 bytes plus kernel.macho.adt.](https://github.com/obaosp/UniXNU-cupid/actions/runs/42383457434)
  Command: <code>./unixnu build payload -D ../device --uefi ../uefi-cupid --unique-chip-id &lt;seed&gt; &amp;&amp; ./unixnu bootimg -D ../device --uefi ../uefi-cupid --dtb ../device/build/cupid/cupid.dtb</code>. Revision: `50a8c5d2998cec423adc356e824e8f2faba0a50c`.
- `host`: [macOS 26 DEBUG/CLANGPDB build of Platforms/Xiaomi/cupidPkg/cupid.dsc with FD\_BASE=0xa7100000 FD\_SIZE=0x300000 FD\_BLOCKS=768; output uefi-cupid/Build/cupidPkg/DEBUG\_CLANGPDB/FV/SILICIUM\_UEFI.fd. The Gic-Spurious edk2 patch applied.](https://github.com/obaosp/UniXNU-cupid/actions/runs/42371720139)
  Command: <code>./unixnu build firmware -D ../device --uefi ../uefi-cupid</code>. Revision: `14ab2c0527b2b808ac94afd66025fa56238b9168`.
- `source`: [Documents the ingres-derived memory map, the missing stock uefiplat.cfg replacement, and the vendor-hardware import that Binaries/cupid needs.](https://github.com/obaosp/uefi-cupid/blob/bce96f77d07ec90a516432df466b8cd3af7272fc/Platforms/Xiaomi/cupidPkg/README.md)
- `device`: [The live memory map and /sys/hypervisor \(gunyah, api 1, variant 81\) were read on the phone; the firmware has not been booted yet.](https://github.com/obaosp/UniXNU-cupid/blob/d4514c60f2788efa1677441c54de63820b17c1b0/notes/device-2026-11-07.md)
  Command: <code>adb shell su -c 'cat /proc/iomem'</code>. Revision: `4730e3b1fb52e1238a5d370bdc1f381622033de9`.
- `device`: [fastboot OKAY: Sending 181676 KiB in 4.2 s, Booting OKAY. Black screen, no text or colour, device stayed in fastboot; fastboot reboot returned to PixelOS. Header, ramdisk and payload verified; pstore empty and no last\_kmsg. cupid stock uefi.img is an ELF with PT\_LOAD 0xA7000000 memsz 0x2A0000, while the FD was based at 0xA7100000 with size 0x300000, i.e. 1 MiB past the window.](https://github.com/obaosp/UniXNU-cupid/blob/d4514c60f2788efa1677441c54de63820b17c1b0/notes/first-boot-2026-11-07.md)
  Command: <code>fastboot boot boot.img</code>. Revision: `b83e634bd63489b7c7ff3f976ca732ea80c98c03`.
- `device`: [BootShim and the cupidPkg UEFI run on the phone: console shows loading drivers and memory allocation, Project Silicium logo, then the UniXNU menu with four options. Header v4 was required; the v0 image stayed in fastboot. Payload missing, see packaging.](https://github.com/obaosp/UniXNU-cupid/blob/d4514c60f2788efa1677441c54de63820b17c1b0/notes/first-uefi-boot-2026-11-07.md)
  Command: <code>fastboot boot boot-v4.img</code>. Revision: `34134f4d1ee7a80cc67f940a08ae363b3904bce7`.

## CPU 与中断 {#cpu}

`implemented`

组件: `ArmCpu`, `ArmDTPlatform`.

### 硬件与依赖

- SM8450 CPU topology, MPIDR numbering, GICv3 windows and 19.2 MHz timebase from mainline Linux sm8450.dtsi.
- PSCI 1.0 over SMC.

### 配置

- dts/sm8450.dtsi: 8 CPUs at MPIDR Affinity1 0x000-0x700; 4x Cortex-A510, 3x Cortex-A710, 1x Cortex-X2.
- GIC distributor 0x17100000 \(0x10000\), redistributors 0x17180000 \(0x200000\), 0x40000 stride, interrupt cells 4.
- dts/cupid.dts marks cpu0-3 as the E cluster and cpu4-7 as the P cluster.
- soc:patches/xnu/series raises MAX\_CPUS to 8 and reads the core number from Affinity0/Affinity1 for BCM2837 targets.

### 操作步骤

- Compile the board DTS and inspect enabled CPUs, GIC ranges and timebase in the ADT.
- Record per-CPU entry, timer interrupts and IPI delivery on the phone.

### 开发经验

- SM8450 numbers cores in MPIDR Affinity1 exactly like SM8550, so the shared native-smp-secondary patch context applies unchanged.
- SM8450 UFS PHY is at 0x1d87000, not SM8550's 0x1d80000; SoC values cannot be copied across without checking.

### 完成条件

- Every enabled CPU reaches its entry checkpoint; timer and IPI handling work on each enabled CPU.

### 当前范围

- No CPU has entered XNU on this board yet; the topology is host-verified only.

### 下一步

- After the first boot, record each CPU's MPIDR and entry checkpoint.

### 证据

- `source`: [Board CPU clusters and memory/splash regions.](https://github.com/obaosp/UniXNU-cupid/blob/d4514c60f2788efa1677441c54de63820b17c1b0/dts/cupid.dts)
- `source`: [Mainline CPU nodes, GIC windows, UFS host and PHY addresses used by dts/sm8450.dtsi.](https://github.com/torvalds/linux/blob/f1586048fb1dabb91c82fbe11557e505587973d3/arch/arm64/boot/dts/qcom/sm8450.dtsi)
- `device`: [8 cores online; Features include paca and pacg on every core \(FEAT\_PAuth address and generic keys\); parts 0xd46/0xd47/0xd48.](https://github.com/obaosp/UniXNU-cupid/blob/d4514c60f2788efa1677441c54de63820b17c1b0/notes/device-2026-11-07.md)
  Command: <code>adb shell su -c 'grep -E "Features|CPU part" /proc/cpuinfo'</code>. Revision: `4730e3b1fb52e1238a5d370bdc1f381622033de9`.
- `device`: [XNU started on cupid for the first time and panicked on msr CNTP\_CTL\_EL0 \(word 0xd51be228 at pc=0xfffffff00ad881c0\): Gunyah leaves CNTHCTL\_EL2.EL1PCEN clear, so the EL1 physical-timer write traps. The earlier PAC-instr=d5 reading was a wrapped line; see the CORRECTION in notes/pac-trap-2026-11-07.md.](https://github.com/obaosp/UniXNU-cupid/blob/d4514c60f2788efa1677441c54de63820b17c1b0/notes/pac-trap-2026-11-07.md)
  Command: <code>fastboot boot boot-v4-win2g.img</code>. Revision: `d093c5c1292400209634b7b82c78cd39fd9faa98`.

## 内存与 DMA {#memory}

`implemented`

### 硬件与依赖

- cupid UEFI memory map \(largest contiguous run\), reserved regions, SMMU stream IDs and DMA widths.

### 配置

- board.toml \[payload.adt\] owned\_memory\_size = 0x80000000 \(2 GiB\) matches the measured run.
- dts/cupid.dts memory@80000000 describes a 2 GiB nominal handoff range.

### 操作步骤

- Dump the live ABL/UEFI memory map over UART or fastboot oem command.
- Set owned\_memory\_size to the largest run the firmware can hand over.

### 开发经验

- The stock bootloader memory layout has not been measured on cupid; the sheng/ishtar windows are 4.75 GiB and 9 GiB on different boards and are not evidence for this one.

### 完成条件

- Every handoff region is accounted for and DMA engines access only allocated ranges with the documented cache policy.

### 当前范围

- No memory-map measurement from the phone.

### 下一步

- Capture the cupid memory map before the first payload boot.

### 证据

- `device`: [System RAM runs measured; largest contiguous 0x840000000-0x97fffffff \(5 GiB\) with the reserved tail from 0x96ef68000; owned\_memory\_size set to 0x12e000000.](https://github.com/obaosp/UniXNU-cupid/blob/d4514c60f2788efa1677441c54de63820b17c1b0/notes/device-2026-11-07.md)
  Command: <code>adb shell su -c 'cat /proc/iomem'</code>. Revision: `4730e3b1fb52e1238a5d370bdc1f381622033de9`.

## 存储与根卷 {#storage}

`planned`

### 硬件与依赖

- SM8450 UFS host 0x1d84000 \(SPI 265\) and QMP PHY 0x1d87000; SM8450 GCC UFS clock/reset offsets; LUN 0 GPT geometry.

### 配置

- SoC DTSI publishes ufshc/ufsphy disabled; the cupid defconfig leaves CONFIG\_XNU\_NATIVE\_UFS unset.

### 操作步骤

- Add an SM8450 UFS component \(or parameterise ShengUfs by SoC compatible and GCC offsets\).
- Enable ufs/ufsphy in the board DTS, then record capacity, GPT and userdata window.

### 开发经验

- ShengUfs matches only qcom,sm8550-ufshc and hardcodes SM8550 GCC UFS registers, so it cannot drive cupid as-is.
- SM8450 UFS PHY is at 0x1d87000; SM8550 is at 0x1d80000.
- Measured from gcc-sm8450.c against ShengUfs/GccUfs.h: SM8450 branches are ufs\_phy\_axi 0x87018, ahb 0x87020, tx\_symbol\_0 0x87024, rx\_symbol\_0 0x87028, unipro\_core 0x87064, ice\_core 0x8706c, phy\_aux 0x870a4, rx\_symbol\_1 0x870c0, aggre\_ufs\_phy\_axi 0x870d4, ufs\_phy\_gdsc 0x87004. SM8450 has no separate UFS\_MEM\_PHY\_GDSC, so a per-SoC table is required.
- package/Sm8450Ufs/Sm8450UfsRegs.h is the first SM8450 UFS component: nine 0x87xxx branch offsets, GDSC 0x87004, HC 0x1d84000, PHY 0x1d87000 and a read-only probe; .github/workflows/ufs-regs.yml compiles it with a host test.
- package/Sm8450Ufs/Sm8450UfsHci.h adds the UFSHCI command path: HCE 0x34, IS 0x20, UIC 0x90, doorbell 0x58, controller enable/disable, UIC DME\_GET/link-startup, UTRD and command-UPIU layouts \(READ CAPACITY\(10\)\), transfer-list base and doorbell ring/clear, exercised against a fake controller.
- The UTRD keeps DW0-3 as raw words: the C bitfield header pads to 40 bytes, so the static asserts pin 32 bytes with the UCD base at 16 and PRDT at 28; the fake-controller test caught the padded layout.
- Fixed the UPIU header field order \(LUN b1, task tag b2, IID/CS b3, CDB b12\) and added ResponseUpiu \(52 bytes, residual and sense fields\), PrdtEntry \(16 bytes\), 4-byte PRDT padding and the UCD layout at 0/512/1024; the host test pins every offset.

### 完成条件

- Host: register, clock and link facts match the board inventory. Reads: capacity, GPT and known blocks are correct. Root: the OS volume mounts and launchd starts.

### 当前范围

- No SM8450 UFS driver exists in the component catalog.

### 下一步

- Add UCD/PRDT allocation, response-UPIU parsing and a SCSI READ\(10\) transfer to the host model; then map MMIO in a kext and verify the SM8450 GCC clocks and link startup on the phone.

### 证据

- `source`: [SM8450 UFS GCC branch table \(0x87018..0x870d4\), GDSC 0x87004, host 0x1d84000 and PHY 0x1d87000, with a read-only probe; no SM8550 0x77xxx/0x9e000 values.](https://github.com/obaosp/UniXNU-cupid/blob/d4514c60f2788efa1677441c54de63820b17c1b0/package/Sm8450Ufs/Sm8450UfsRegs.h)
- `device`: [iomem confirms ufshc 0x1d84000 \(ufs\_mem, ufs\_ice 0x1d88000, ufs\_ice\_hwkm 0x1d90000\) and PHY 0x1d87000; userdata is sda38, start512 25362432, size512 466862040 \(LBA 3170304..61528058 at 4096 bytes\).](https://github.com/obaosp/UniXNU-cupid/blob/d4514c60f2788efa1677441c54de63820b17c1b0/notes/device-2026-11-07.md)
  Command: <code>adb shell su -c 'sh /data/local/tmp/collect2.sh'</code>. Revision: `4730e3b1fb52e1238a5d370bdc1f381622033de9`.

## 显示 {#display}

`planned`

### 硬件与依赖

- Panel: Xiaomi L3 42 02 0a, 1080x2400, DSI command mode with DSC, 60/90/120 Hz timings.
- Cont splash framebuffer 0xb8000000 + 0x2b00000; backlight and panel supplies L7C \(AVDD\) and L2C \(VDD\).

### 配置

- \[payload\] does not yet bind a display component; CONFIG\_XNU\_NATIVE\_LEGACY\_DISPLAY stays unset.
- The iPhone17,2 profile advertises 1320x2868; it must be corrected for 1080x2400 when the panel binds.

### 操作步骤

- Port build-gop-legacy-display-26.py to the iPhone17,2 \(d94ap\) ABI record.
- Bind the panel timings and backlight, then verify geometry, colors and refresh.

### 开发经验

- cupid's panel is 1080x2400 and 120 Hz-capable; the iPad and iPhone 16 Pro Max profiles describe different sizes.
- Framebuffer handoff and splash region are shared with the waipio platform DTSI.

### 完成条件

- A known frame appears with correct geometry and colors; userland presentation and backlight control work.

### 当前范围

- No display ABI record for d94ap and no panel driver.

### 下一步

- Produce abi/legacy-display-23F84-d94ap.json and bind the L3 panel timing set.

### 证据

- `device`: [The firmware console and the UniXNU menu render on the 1080x2400 panel through SimpleFbDxe, so ABL scan-out and GOP handoff work on cupid. XNU display is still untested.](https://github.com/obaosp/UniXNU-cupid/blob/d4514c60f2788efa1677441c54de63820b17c1b0/notes/first-uefi-boot-2026-11-07.md)
  Command: <code>fastboot boot boot-v4.img</code>. Revision: `34134f4d1ee7a80cc67f940a08ae363b3904bce7`.

## 输入 {#input}

`planned`

### 硬件与依赖

- STMicroelectronics FTS touch over QUPv3 SE4 SPI, IRQ TLMM GPIO 21, reset GPIO 20, firmware st\_fts\_l3.ftb.
- Power/volume keys on PM8550/PMK8550.

### 配置

- No input component is selected; the SoC DTSI does not model SPI or TLMM yet.

### 操作步骤

- Add SPI/TLMM resources to the SoC layer, then port an FTS HID input component with the 1080x2400 coordinate map.
- Record contact IDs, release events and button reports.

### 开发经验

- cupid uses FTS \(st,spi\), not the Novatek NT36532 of sheng, so ShengNovatekTouch is not reusable.
- The vendor DTS gives fts,x-max 10800 and y-max 24000 \(12x scaling\) and FOD coordinates.

### 完成条件

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive, buttons produce HID reports.

### 当前范围

- No FTS component and no SPI/TLMM nodes in the SoC DTSI.

### 下一步

- Model QUPv3 SE4 SPI and TLMM in sm8450.dtsi, then write the FTS transport.

### 证据

按下一步操作收集证据。

## GPU {#gpu}

`planned`

### 硬件与依赖

- Adreno 730 at 0x3d00000, GMU 730.1 at 0x3d6a000, GPU SMMU 0x3da0000, signed ZAP firmware and GPU votes.
- iPhone17,2 ioaccelerator ABI record.

### 配置

- sm8450.dtsi describes GPU/GMU/SMMU; all nodes are disabled.
- CONFIG\_XNU\_NATIVE\_ADRENO must stay unset: the catalog's Adreno740 driver targets a different generation.

### 操作步骤

- Add an Adreno730 component \(or parametrise Adreno740 by GPU id\), its GMU command database and votes.
- Port the accelerator ABI to d94ap, then enable the nodes and verify submissions and presentation.

### 开发经验

- Adreno740/AdrenoMetal are the only GPU components and carry Adreno 740 register layouts; pointing them at a 730 is not a supported configuration.
- SM8450 GMU PDC window is 0xb290000; SM8550 uses 0xb280000.

### 完成条件

- GPU submissions complete, fences are correct, a known image renders and Metal presents it.

### 当前范围

- No Adreno 730 driver and no d94ap GPU ABI record.

### 下一步

- Inventory the Adreno 730 firmware and GMU register map from the vendor kernel, then scope an Adreno730 component.

### 证据

按下一步操作收集证据。

## 网络 {#network}

`planned`

### 硬件与依赖

- cupid WLAN/BT combo: confirm WCN6750 or WCN6855 from vendor firmware \(both qca6490 and qca6750 configs ship in the device tree\).
- PCIe or MHI transport, firmware, NVM and MAC address.

### 配置

- No network component is selected; no wlan node is exported in the board DTS.

### 操作步骤

- Confirm the chipset from vendor/etc/wifi and the stock DTB.
- Select a matching UniXNU Wi-Fi component, add bus resources and stage firmware.

### 开发经验

- The LineageOS sm8450-common package ships both qca6490 and qca6750 WCNSS configuration files, so the chipset cannot be inferred from the package list alone.

### 完成条件

- Scanning, association, address configuration and sustained traffic pass.

### 当前范围

- Chipset unconfirmed; no component selected.

### 下一步

- Read the stock DTB and vendor Wi-Fi firmware names to identify the chipset.

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`planned`

### 硬件与依赖

- ADSP firmware, LPASS macro codecs, Cirrus CS35L41 speakers \(from the vendor DTS\), audio routes.

### 配置

- No audio component is selected and no DSP firmware is staged.

### 操作步骤

- Add ADSP boot, GPR/GLINK transport and the codec routes from the vendor DTS.
- Verify playback and capture per declared route.

### 开发经验

- The vendor cupid DTS declares CS35L41 speaker amplifiers; the sheng audio HAL is a different board and cannot be copied.

### 完成条件

- Each declared route carries the selected format through playback or capture and handles start/stop.

### 当前范围

- Not started; blocked behind storage and power bring-up.

### 下一步

- Inventory ADSP firmware and codec wiring after stage 0 boots.

### 证据

按下一步操作收集证据。

## 电源 {#power}

`planned`

### 硬件与依赖

- PM8550/PMK8550 PMIC set, RPMh regulators, battery profile, charging and thermal limits.

### 配置

- No power component is selected; the board relies on firmware-provided regulators for stage 0.

### 操作步骤

- Add RPMh/PMIC access, battery readings and the supported sleep/resume transitions.
- Record each transition and its dependent peripherals.

### 开发经验

- cupid uses PM8550/PMK8550; sheng's sheng\_pmgr code is board-specific and is not selected.

### 完成条件

- Power controls and battery readings match observations; sleep/resume restores dependent peripherals.

### 当前范围

- Not started.

### 下一步

- Inventory PMIC rails and the battery profile from the vendor DTS.

### 证据

按下一步操作收集证据。

## 镜像组装 {#packaging}

`host-verified`

组件: `XnuPrelink`.

### 硬件与依赖

- iPhone17,2 26.5.2 kernelcache for prelink, the OS/SystemOS images for userdata, Data seed and the platform seed \(UNIXNU\_UNIQUE\_CHIP\_ID\).

### 配置

- board.toml \[payload\] builds a 176 MiB CUPIDESP FAT volume; \[bootimg\] packs header v0 at 4096-byte pages.
- scripts/package.sh is the standard UniXNU packaging script and reads \[package\] unixnu and \[package.defconfig\].

### 操作步骤

- Install the OS profile, then run scripts/package.sh --os ios-27.0.1-24A446 --uefi ../uefi-cupid once the firmware exists.
- Run the macOS workflow for kernel-only builds until then.

### 开发经验

- patches/xnuprelink/fileset-cupid-23F84-symbols.json is a reviewed fixture for the iPhone17,2 26.5.2 kernelcache. It binds sixteen kernel functions/thunks by string/call evidence, including the lck\_mtx\_gate open/steal/alloc/free family and the pmap PPL functions. The first batch paired the lck\_mtx\_gate allocator \(alloc\_init\) with the native destroy, and the native gate check panicked: 'Trying to destroy a gate that was allocated by gate\_alloc\_init; gate\_free should be used'. The corrected deallocator is \_lck\_mtx\_gate\_free. fileset-register-report.patch replaces the simple stub with a register-saving report \(x0-x30, x16/x17, data-slot candidates\) so any remaining stub names its slot instead of relying on the stale tail-branch return address.
- build-fileset-release-reference.py --tree . --lto is required for iOS 26: the stripped native kernel cannot shape-match the kernel-function imports of the original kexts, so without the symbol-bearing reference prelink left 1668 targets / 18367 sites. The reference cut that to 92 owner-site pairs / 766 sites; the sixteen-binding batch and --allow-missing write the candidate, and the register report names any remaining slot.
- The iPhone 26 prelink layout leaves only 0x119f40 before AppleARMPlatform \_\_DATA\_CONST; the DEVELOPMENT native \_\_DATA\_CONST plus \_\_LASTDATA\_CONST exceed it. patches/xnu/no-assert-strings.patch removes most of the \_\_assert strings so the native constants fit. MACH\_ASSERT stays defined: the ipc\_port ABI is 160 bytes, and a MACH\_ASSERT=0 build failed the genassym static assertion at 144. DTrace/LOCK\_STATS also stay on.
- Kernel and package steps do not need the firmware checkout; payload and boot image do because they embed the firmware volume.
- package/Sm8450Ufs is board-owned host-tested code, not yet part of the kernel archive: ufs-regs compiles Sm8450UfsRegs.h and Sm8450UfsHci.h with c++ -Werror on every change, and the package step continues to build only the EDK II drivers.
- The board package still carries the host-tested UFS transport model \(Sm8450UfsHci.h\); it does not enter the kernel archive, so the EDK II package step is unchanged.
- patches/unixnu/0001-patch-xnu-entry-probe-skip-nm-headers.patch is required for payload: the upstream parser crashed on a three-token nm header line \(int\(Symbols\)\) while reading the prelinked kernel.
- patches/unixnu/0002-ramdisk-find-fat-in-initrd.patch makes UniXNURamDiskDxe scan up to 256 MiB of the initrd, log the first two words at every 16 MiB boundary, and, if the 512-byte walk finds no boot sector, search byte-wise for the CUPIDESP volume label and derive the FAT start from offset 71. cupid v4 ABL publishes 0xBC8BE00 bytes starting with an LZ4 vendor ramdisk; 64 MiB and 256 MiB sector walks found no FAT although the bulk data is present.
- patches/darwinboot/0001-darwinboot-log-window-failure.patch prints NO WINDOW and the FREE runs to the console; owned\_memory\_size was lowered to 0x80000000 so a 2 GiB run can satisfy the kernel window while the log reports the real largest run.
- patches/xnu/timers-avoid-trapped-physical-timer.patch removes the precautionary CNTP\_CTL\_EL0 write in \_enable\_virtual\_timer; Gunyah traps EL1 physical-timer access. It is the only device XNU series entry after the pivot.
- The iOS 27 reviewed-symbol fixture \(30 shims\), the PAC key-write skip and the report-registers probe were removed: the iPhone 26 kernel is the same XNU major/minor as the source, so prelink must pair natively and --allow-missing/--fileset-reference are gone.
- The 13432-only shims \(corecrypto wrappers, AppleM2 clock/property, AppleImage4 flags/gates, sandbox checks, AppleARMPlatform lookup and the AMFI DRBG initializer\) are not part of the iOS 26 build; they were responses to the 24A446 source mismatch.

### 完成条件

- Kernel and prelink succeed with no missing targets, the payload contains all declared inputs, and the boot image matches the bootloader format and size limit.

### 当前范围

- Kernel, package and firmware are host-verified. Payload is blocked on the platform seed \(UNIXNU\_UNIQUE\_CHIP\_ID\); the boot image is blocked on a cupid firmware DTB. Neither is in the repository.

### 下一步

- Build payload and boot image once the owner supplies UNIXNU\_UNIQUE\_CHIP\_ID and cupid's firmware DTB; the macOS workflow already stages boot-v4 images.

### 证据

- `host`: [Pre-pivot iOS 27 run: rebuilt arm64e XNU and built the EDK II package \(DEBUG/CLANGPDB, UniXNU.efi and the shared drivers\). This evidence is kept as packaging history, not as the current profile.](https://github.com/obaosp/UniXNU-cupid/actions/runs/42371720139)
  Command: <code>./unixnu build kernel -D ../device &amp;&amp; ./unixnu build package -D ../device</code>. Revision: `14ab2c0527b2b808ac94afd66025fa56238b9168`.
- `device`: [userdata geometry measured from the live GPT \(sda38, 3170304..61528058 at 4096-byte LBA\).](https://github.com/obaosp/UniXNU-cupid/blob/d4514c60f2788efa1677441c54de63820b17c1b0/notes/device-2026-11-07.md)
  Command: <code>adb shell su -c 'sh /data/local/tmp/collect2.sh'</code>. Revision: `4730e3b1fb52e1238a5d370bdc1f381622033de9`.

## 诊断 {#diagnostics}

`planned`

### 硬件与依赖

- UART serial access, the firmware log exporter and reproducible build logs.

### 配置

- The payload kernel command line starts with -v serial=3 debug=0x14e.

### 操作步骤

- Attach UART, capture firmware and XNU logs, and store each result with its revision and command.

### 开发经验

- No phone is attached to the build host, so no firmware or kernel log exists yet.
- tools/diagnose-unmapped-call.py reproduces the fileset panic diagnosis from the emitted kernel.macho and the pinned decompressed kernelcache: it resolves the caller component, the direct BL or import-stub GOT slot, the original target and its function range, and prints the strings the original function references. On run 42471867225 it names the known site 0xfffffff00ab15578 as corecrypto -&gt; \_\_memcpy\_chk \(0xfffffff00ad05978\) and shows the emitted slot resolved from the stub 0xfffffff00b405c60 to native \_\_\_memcpy\_chk 0xfffffff00ad3f568.
- tools/match-unmapped-target.py searches the unstripped native kernel for the closest function to an unmatched original using the XnuPrelink relocation-masked shape. It found no candidate above 0.55 for AppleM2 0xad714b8/0xb0de1d8, confirming they are 13432-only; it also lets future targets be reviewed against real symbols instead of guessed.

### 完成条件

- Each claimed milestone has a reproducible command, a matching revision and an accessible result.

### 当前范围

- No device access from the current host \(no adb, fastboot or USB bus\).

### 下一步

- Attach the phone and capture the first firmware log.

### 证据

按下一步操作收集证据。

</div>
