# OPPO R11 \(CPH1707\): SDM660, PM660/PM660L, 1080x1920 AMOLED, 64 GiB eMMC \(appleiPodTouch4\)

[appleiPodTouch4/unixnu-r11](https://github.com/appleiPodTouch4/unixnu-r11)

<div v-pre>

OPPO R11 \(CPH1707 / 16051\) on SDM660 + PM660/PM660L. Board inputs, firmware and boot image are derived from the device's own OFP package; the storage, display, input and power drivers are not written yet.

Source record: [porting.toml](https://github.com/appleiPodTouch4/unixnu-r11/blob/93ab51e474b3845b660677bb16280060de709e85/porting.toml), `93ab51e474b3845b660677bb16280060de709e85`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `implemented` |
| [Firmware and boot](#firmware) | `implemented` |
| [CPU and interrupts](#cpu) | `implemented` |
| [Memory and DMA](#memory) | `implemented` |
| [Storage and root](#storage) | `planned` |
| [Display](#display) | `planned` |
| [Input](#input) | `planned` |
| [Power](#power) | `planned` |
| [Image assembly](#packaging) | `implemented` |
| [Diagnostics](#diagnostics) | `planned` |
| [GPU](#gpu) | `planned` |
| [Network](#network) | `planned` |
| [Audio](#audio) | `planned` |

## Configuration {#configuration}

`implemented`

### Hardware and dependencies

- SDM660 shared support \(../UniXNU-sdm660-common\), iOS 16.5 build 20F66 profile, r11 defconfig.
- OFP package model 16051: boot.img, gpt\_main0.bin, xbl.elf.

### Configuration

- schema\_version = 2; board.soc\_source = sdm660; board.os\_profile = ios-16.5-20F66.
- kernel.defconfig = r11\_defconfig; fragments arch + soc + os; device patch series present but empty.
- kernel.archives lists the arch-profile scripts because arrays replace inherited arrays.

### Procedure

- python3 scripts/extract-inputs.py --ofp ../ofp\_extracted
- ./unixnu defconfig r11\_defconfig -D ../UniXNU-r11
- ./unixnu status --json -D ../UniXNU-r11

### Development findings

- The OFP boot image carries three appended device trees for board-id subtypes 0x3eb3, 0x3ee7 and 0x3ef6; 0x3eb3 is the 16051 tree and is the one committed as inputs/r11-stock.dtb.
- The stock device tree leaves /memory at zero because ABL patches it from SMEM, so the 4 GiB window is taken from hardware measurement and must be confirmed on the target device.
- The SoC layer has no published repository yet; feeds.toml points at a sibling checkout, so the build is not reproducible from a clean clone until it is pushed and pinned.
- The arm-io window is derived, not declared: arm\_io\_window\(\) takes the lowest and highest exported register range and aligns them to 16 MiB, and it rejects a zero base. With the cpu, i2c-slave and DSI-panel nodes untagged the window is base 0x03000000 size 0x84000000, and arm-io gets ten children \(interrupt-controller, timer, tlmm, spmi, emmc, i2c1, mdss, dsi0, smem, imem\).
- boot-irq12 panicked in NativeAES::MetaClass::alloc\(\) -&gt; bsd\_init -&gt; IOKitBSDInit -&gt; doServiceMatch because scripts/data/native-aes-original-bindings.S binds IOAESAccelerator's methods to absolute addresses from a different prelink layout: 0xfffffff004a80038 holds zeros both at its recorded value and 16 MiB above it in this board's kernel.macho, while the original kernelcache has code at 0xfffffff005a80038. emit\_prelink repacks kext code, and com.apple.iokit.IOCryptoAcceleratorFamily IS in the --root list, so the failure is the binding table, not a missing root. CONFIG\_XNU\_NATIVE\_AES=n in configs/r11\_defconfig removes the personality so IOKit never instantiates the class.
- Editing configs/r11\_defconfig alone changes nothing: the build reads out/&lt;device&gt;/&lt;profile&gt;/&lt;config&gt;/.config, which 'unixnu defconfig r11\_defconfig -D ../UniXNU-r11' generates by appending the defconfig after the arch/SoC/OS fragments. parse\_config keeps the LAST value, so the defconfig wins -- but only after the file is regenerated. boot-irq13 proved this the hard way: identical panic with CONFIG\_XNU\_NATIVE\_AES=n in the defconfig and =y still in .config.

### Completion criteria

- defconfig and status resolve arch, SoC, OS and device layers; every referenced file exists.

### Current limits

- SoC source is local, not pinned. No unixnu.lock yet: nothing git-hosted is selected besides the UniXNU defaults.
- With CONFIG\_XNU\_NATIVE\_AES=n there is no hardware AES accelerator and NativeVirtioBlock/NativeRamBlock stay unavailable; the binding table must be re-audited against this board's own prelink output before any of them can be enabled.

### Next action

- Push UniXNU-sdm660-common, switch feeds.toml to git plus a commit, run unixnu fetch and commit unixnu.lock.

### Evidence

- `source`: [Format 2 board configuration with values traced to inputs/hw.json](https://github.com/appleiPodTouch4/unixnu-r11/blob/93ab51e474b3845b660677bb16280060de709e85/board.toml)

## Firmware and boot {#firmware}

`implemented`

Components: `DarwinBoot`.

### Hardware and dependencies

- uefi-r11 platform package in Mu-Silicium layout, adapted from the SDM660 reference platform.
- Stock XBL memory reservation strings, stock boot image geometry, stock device tree.

### Configuration

- firmware.dsc = Platforms/OPPO/r11Pkg/r11.dsc; firmware.config = r11; fd = Build/r11Pkg/&\#123;target&\#125;\_CLANGPDB/FV/R11\_UEFI.fd.
- FD base 0x9FC00000 and size 0x300000 in Resources/Configs/r11.toml, r11.dsc and the BootShim compile flags.
- The FDF embeds UniXNU, UniXNUDxe, UniXNURamDiskDxe, DarwinBoot, DiskIoDxe, PartitionDxe and Fat.

### Procedure

- uefi-r11/scripts/prepare-base.sh \(Mu-Silicium + Mu\_Basecore + vendor binaries\).
- ./unixnu build firmware -D ../UniXNU-r11 --uefi ../uefi-r11-base --edk2 ../Mu\_Basecore
- python3 scripts/check-r11.py \(also runs as the firmware preflight\).

### Development findings

- The stock xbl.elf is UEFI 4.1 \(SDM660 LA\) and reserves exactly the windows the platform uses: DXE Heap 0x94000000+0x09400000, UEFI FD 0x9FC00000+0x00300000, UEFI Stack 0x9FF90000+0x00040000.
- SimpleFbDxe locates the framebuffer by the memory-map region name Display Reserved; the stock splash reservation 0x9D400000+0x02400000 matches that region, so the menu can be drawn over the vendor boot logo without an MDSS driver.
- The panel driver is the one vendor piece that cannot be reused: the reference SDM660 DisplayDxe targets a different panel, so USE\_CUSTOM\_DISPLAY\_DRIVER stays 0.
- No ACPI tables are built: UniXNU hands XNU an ADT and nothing else consumes ACPI on this target.

### Completion criteria

- The FD builds at exactly 0x300000 bytes, BootShim carries the same base and size, and the boot image round-trips through unixnu bootimg.

### Current limits

- Vendor DXE binaries are seeded from a sibling SDM660 UEFI device; charger and battery profiles and the button GPIO map are not R11 values yet.
- No R11 panel driver, so DisplayDxe is disabled.

### Next action

- Build the FD on a macOS or Linux host and record the output size, then boot it with fastboot boot and capture the framebuffer checkpoint.

### Evidence

- `source`: [Preflight checks the Display Reserved region the SDM660 memory map must keep; the map itself lives in the sibling uefi-r11 repository](https://github.com/appleiPodTouch4/unixnu-r11/blob/93ab51e474b3845b660677bb16280060de709e85/scripts/check-r11.py)

## CPU and interrupts {#cpu}

`implemented`

Components: `ArmCpu`, `ArmDTPlatform`, `SoftwareAES`.

### Hardware and dependencies

- 8 cores in two clusters: MPIDR 0x0-0x3 \(A53 class, part 0x801\) and 0x100-0x103 \(A73 class, part 0x800\).
- GICv3 distributor 0x17a00000 and redistributors 0x17b00000 \(8 x 0x20000\), 19.2 MHz arch timer, PSCI over SMC.

### Configuration

- dts/r11.dts includes sdm660.dtsi and tags cpu0-3 as E and cpu4-7 as P with unixnu,cluster-type.
- Kernel arguments r11-smp=1 and armcpu-spi-ipi=1.

### Procedure

- Compile dts/r11.dts, inspect the ADT cpu nodes and the /arm-io ranges.
- Record per-CPU entry and timer/IPI delivery on the device.

### Development findings

- SDM660 exposes both clusters with 4 cores each; per-CPU reg values are affinities, not indices, so ADT output must keep 0x100-0x103 for the gold cluster.
- The arch timer interrupts are PPI 13/14/11/10, matching the SDM660 platform include used by the firmware.
- The cpu@N nodes carry no unixnu,adt-name: the generator exports a tagged node as a direct child of /arm-io and rewrites reg as physical address minus the arm-io base, so an exported cpu would place affinity 0x0 below the 16 MiB base. /cpus is built from these same children instead, and the resulting ADT has cpu0-7 in MPIDR order under /cpus.
- Device, boot-irq10: ArmCpu::start\(\) reaches step 0x10 \(IRQ action registered\) and initCPU\(\) gets through both enableCPUTimeBase\(true\) calls and the \(false\) between them, then stops with T=0x26 -- the marker written immediately before armcpu\_gic\_snapshot\(\). The panel rows are a 48 s snapshot: they are repainted when the console is written, not by the event timer, so the boot stopped at 48 s and the panel stopped with it. The S=/T= text is written straight to scanout and stays live.
- The two independent stops of this bring-up are the only two places that touch ICC\_HPPIR0/1\_EL1 in the whole kext: boot-irq7 stopped at T=0x24 \(armcpu\_sgi\_selfprobe polls it after sending its SGIs\) and boot-irq10 at T=0x26 \(armcpu\_gic\_snapshot reads it first\). That correlation, not the timer, is the current best lead on 'the GIC never delivers'.
- THE INTERRUPT WALL, found by the boot-irq16 AUD panel row: pend=40200000 \(ISPENDR0 bit 30 asserted\), isen=8000001 \(bit 27 only\), daif=200 \(I clear\), wak=0, act=0, tirq=0. The arch timer had been firing into INTID 30 the whole time while the driver enabled INTID 27 -- Apple GIC numbering, not SDM660. soc/dts/sdm660.dtsi gives the four arch-timer PPIs as &lt;1 13&gt; &lt;1 14&gt; &lt;1 11&gt; &lt;1 10&gt; = INTIDs 29/30/27/26, and in the arm,armv8-timer order the second entry is the EL1 virtual timer that CNTV drives. ArmCpu now takes the PPI from armcpu-timer-intid \(default 30\) instead of hardcoding 27, and the AUD row carries tid= so a photograph always names the INTID in use.
- Correction to the earlier DS note: GICD\_TYPER.SecurityExtn is bit 10 of GICD\_TYPER and dtyp=7b04f3 has it SET, which means the GIC implements the security extensions \(two security states\), not a single-security-state GIC. From a Non-secure access GICD\_CTLR.EnableGrp0 \(bit 0\) and EnableGrp1S \(bit 2\) are RAZ/WI, which is why dctl reads 0x12 \(EnableGrp1NS + ARE\_NS\) after writing 0x13. IGROUPR0 reading back 0 has the same cause: a Non-secure read of a Group 0 register.

### Completion criteria

- All eight CPUs reach their entry checkpoint and the timer ticks on every core.

### Current limits

- No CPU frequency or idle driver: r11-cpufreq is passed but no board driver implements it.
- Secondary cores stay off \(no sheng-smp\): the boot CPU's GIC and machine timer are not delivering yet.

### Next action

- Boot boot-irq17.img \(armcpu-timer-intid=30\): read the panel row 45 AUD tid=/tirq=/pend=. tirq rising and pend bit30 clearing means the EL1 virtual timer is finally delivered; then bsd\_init should print calling dlil\_init and reach vfs\_mountroot, where qcom\_emmc\_rootdev\(\) takes over.

### Evidence

- `device`: [S=0x12 / T=0x2A on the panel: initCPU\(\) and registerService\(\) returned, ArmCpu::start\(\) finished. The frame was frozen by the panel's own 120 s observation limit \(boot-progress=1\), so it says nothing about the kernel after that point.](https://github.com/appleiPodTouch4/unixnu-r11/blob/93ab51e474b3845b660677bb16280060de709e85/docs/evidence/boot-irq11.img)
  Command: <code>fastboot boot docs/evidence/boot-irq11.img</code>. Revision: `9a193a520b30c7263d31189426052c5e5e50938f`.
- `device`: [S=0x10 / T=0x26, hp=deadbeef, IRQ=0, gic=0.6: the stop is inside armcpu\_gic\_snapshot\(\), after both timer enables returned](https://github.com/appleiPodTouch4/unixnu-r11/blob/93ab51e474b3845b660677bb16280060de709e85/docs/evidence/boot-irq10.img)
  Command: <code>fastboot boot docs/evidence/boot-irq10.img</code>. Revision: `9a193a520b30c7263d31189426052c5e5e50938f`.
- `source`: [Two-cluster MPIDR layout \(0x0-0x3, 0x100-0x103\) with E/P cluster types, taken from the stock device tree](https://github.com/appleiPodTouch4/unixnu-r11/blob/93ab51e474b3845b660677bb16280060de709e85/dts/r11.dts)

## Memory and DMA {#memory}

`implemented`

Components: `XnuPrelink`.

### Hardware and dependencies

- Handoff window 0x80000000 + 0xFE4C0000 \(bank0 2 GiB plus bank1 0x7E4C0000, adjacent\).
- Reservations: splash 0x9D400000+0x02400000, removed\_regions 0x85800000+0x03700000, modem 0x8AC00000+0x07E00000, ADSP 0x92A00000+0x02000000, CDSP 0x94C00000+0x00600000.

### Configuration

- payload.dram\_size = 0xFE4C0000 must equal the /memory reg, the ADT generator rejects a mismatch.
- payload.adt.owned\_memory\_size = 0xC0000000 \(3 GiB\).

### Procedure

- Compare the firmware memory map, the DTS reservations and the ADT /chosen/dram-base and dram-size.
- Check that the FD window 0x9FC00000+0x300000 stays outside every reservation.

### Development findings

- The ADT generator accepts exactly one contiguous DRAM range, so the two adjacent banks are described as one range.
- The FD window sits above the splash reservation and below the stack window, matching the stock XBL layout.
- The stock tree zeroes /memory: any value here is an assumption about the retail unit and must be confirmed.

### Completion criteria

- XNU reports the expected physical memory and no driver allocates inside a reserved region.

### Current limits

- 3 GiB owned memory is a first-bring-up value; the remaining \~1 GiB stays with the firmware and reservations.

### Next action

- Read the real SMEM DRAM size on the device and update dts/r11.dts, payload.dram\_size and owned\_memory\_size together.

### Evidence

- `source`: [DRAM window and every reserved region decoded from the stock device tree and GPT images](https://github.com/appleiPodTouch4/unixnu-r11/blob/93ab51e474b3845b660677bb16280060de709e85/inputs/hw.json)

## Storage and root {#storage}

`planned`

### Hardware and dependencies

- eMMC 5.1 on sdhci@c0c4000 \(0x0C0C4000, core 0x0C0C5000\), 512-byte LBA, non-A/B.
- GPT \(inputs/partitions.json\): boot 245760-376831 \(64 MiB\), userdata grow from 10944512, 69 partitions.

### Configuration

- \[userdata\] first\_lba 0x14E000, last\_lba 0xE8F7FA, lba\_bytes 4096.
- CONFIG\_XNU\_NATIVE\_UFS=n and CONFIG\_XNU\_NATIVE\_RAM\_BLOCK=n for the first bring-up; the root is mockfs.

### Procedure

- Write a board eMMC driver \(SDHCI v5 with SDM660 clocks and GDSC\), then enable CONFIG\_XNU\_NATIVE\_RAM\_BLOCK.
- Build the userdata image with unixnu build userdata and record the volume UUID back into board.toml.

### Development findings

- userdata is a grow partition in the shipped GPT \(size 0\), so its end LBA depends on the eMMC capacity; the value here is the 64 GiB mapping.
- root\_match\_volume\_uuid is zero until the userdata image exists.
- bsd/dev/qcom\_emmc.c \(837 lines, added by patches/xnu/qcom-emmc-root.patch\) had never executed before boot-irq18: its only entry point is qcom\_emmc\_rootdev\(\), called from vfs\_mountroot\(\), and bsd\_init never reached vfs\_mountroot\(\) because IOKitBSDInit\(\) panicked first while waiting for an IOMedia with Content=Apple\_HFS. boot-irq18 adds patches/xnu/zzz-no-root-media-panic.patch so the mount loop runs and the probe reports its verdict on the boot panel.
- The IOMedia wait is the real gate, not just a panic: IOService::waitForService matches IOMedia+Apple\_HFS by default \(IOKitBSDInit.cpp:906\), so a storage driver that merely assigns rootdev is not enough -- something must publish an IOMedia.
- Reference implementation: the OPPO R11T Arch Linux package \(HEDC2333, 2026-07-24\). Its kernel carries an appended DTB and, decompiled, it is the only known-good description of this board's eMMC. mmc@c0c4000 there requires clocks iface/core/xo/ice \(GCC 0x16008 / 0x16004 / xo\_board / 0x1600c\), a GCC reset, rpmpd power-domain 0, vmmc = pm660l l4 at 2.95 V, vqmmc = pm660 l8 at 1.8 V, 8-bit bus, HS200/HS400. Both rails sit under regulators-0 with compatible = "qcom,rpm-pm660l-regulators" and carry no regulator-always-on, so Linux enables them through the RPM co-processor -- which XNU has no driver for. The unmodified boot image is staged at boot-control/boot-archlinux-r11t-ref.img and a repack in this board's geometry at boot-control/boot-archlinux-r11t-oppo.img; booting the repack leaves the panel dark because that kernel only reaches console=ttyMSM0/earlycon, so it cannot be used as an on-screen diagnostic. Never boot the installer recovery: its cmdline carries r11t.install\_target=all r11t.storage\_write=1.
- boot-irq35 cleared CORE\_VENDOR\_SPEC to its POR value 0xa9c and CMD1 answered, so the probe moved to the data phase. irq51/52/54 read LBA 1 at 1 MHz and 4.2 MHz with correct bs/bc/sdm and always got 0x4546492045464920 \("EFI " twice\); irq55 forced the card back to 1-bit with CMD6 and broke the data phase \(all-zero + EIO\), so that hypothesis is dead. boot-irq56 \(tag irq56\) drops zzz-emmc-1bit.patch from the series, returns the block clock to \~400 kHz, enables real SDMA \(address written and DMA Enable set\) with a TC-gated PIO copy of the same block, and adds a CMD13 after the data phase.
- Enceka/UniXNU-e5 \(Rongyue E5, Unisoc UMS9621\) is the same UniXNU shape with a working eMMC path: scripts/emmc/NativeEmmc.cpp reads LBA0/LBA1, validates the GPT and publishes 70 partitions, all on SDHCI in 1-bit default speed. Its header documents the failure class this board hit: an SDHCI 4.x host \(HC2 V4EN\) keeps the 32-bit block count at 0x00 and the system address at 0x58/0x5c, while this driver wrote the v3 count at 0x06 and the v3 address at 0x00, leaving the real count zero and the buffer port returning its previous word \("EFI EFI "\). boot-irq57 \(tag irq57\) programs HC2=0x3000, uses the v4 count/address and the v4 10-bit clock divider, selects SDMA explicitly, and drops the CMD6 width/HS switch like NativeEmmc.
- boot-irq57 photo \(tag irq57\): hc2=3000/0003 -- the bootloader left V4EN clear, and forcing it made PIO time out \(e=3c\) and SDMA fail with EIO \(e2=05\), d1=d2=0, while CMD13 still reported Transfer \(st=00000900\). The host is v3 in practice; the v4 forcing is reverted and the boot HC2 selects the layout. boot-irq58 takes E5's other lesson: warm-inherit first \(CMD13 on RCA 1 + SDMA LBA1 before any SWRST\_ALL/CORE\_VENDOR\_SPEC/clock/power change\), keeps the boot state only when EFI PART arrives, and otherwise falls back to the v3 re-identification path.
- boot-irq58 \(tag irq58\) black-screened on device: fastboot boot returned OKAY, then the panel went black with no photo. The warm probe ran before emmc\_clocks\(\) and issued CMD13+SDMA from an unknown bootloader HS400/8-bit state, the likely bus hang. boot-irq59 \(tag irq59\) is read-only: enable the GCC gates, publish hc1/hc2/clock/present-state/CORE\_VENDOR\_SPEC, issue no card command or data transfer, then run the ordinary v3 re-identification.
- boot-irq59 photo: bootloader left HC1=0x38 \(8-bit + ADMA2 64-bit\), HC2=0x0003 \(V4EN=0\), CLK=0x0007 \(\~100 MHz\), PRESENT\_STATE=0x01f800f0 \(card inserted, lines high\), CORE\_VENDOR\_SPEC=0x240a0e \(HS400 select-in/DLL\). So the card is in 8-bit HS400, while the normal re-identification path sets the host to 1-bit SDMA/400 kHz without first clearing HS\_TIMING; irq55 forced only BUS\_WIDTH=0 and left HS400 timing on a 1-bit bus, which explains its all-zero/EIO result. The two correct paths are \(a\) warm ADMA2 with HC1=0x38/8-bit/100 MHz/DLL preserved, or \(b\) CMD6 EXT\_CSD\[185\]=0 then EXT\_CSD\[183\]=0, then host 1-bit/400 kHz.
- boot-irq60 also blacked \(user correction\), so the charger watchdog is not the cause and EnableChargerWdog=0 is not a fix. irq55 did not black; every later image did, so the black screen is a regression of the eMMC normal path \(most likely HS400/1-bit mismatch wedging SDCC\). boot-irq61/62 added the warm ADMA2 path but irq61 fell back to the normal path \(REG row hid w\); the next test must isolate the normal path instead of adding more transfers.
- boot-irq61 photo \(tag irq61\): row 3 was overwritten by the match-pass REG row \(BootProgress line\(3\) from the ArmCpu/IOKit register block\), so the eMMC w/hc1/hc2/st/de line was invisible. The stage history shows hc2 v3 -&gt; pwrctl ack -&gt; sw reset ok, i.e. the ordinary re-identification path ran, so the warm probe did not succeed; d1=d2=0 and e=e2=0 only mean the normal path had not reached its data command at 281 s. boot-irq62 \(tag irq62\) is a panel-only fix: move the REG row to row 28, keep the eMMC row on row 3, same warm-ADMA2 kernel as irq61.
- boot-irq62 photo \(tag irq62\): the eMMC row is visible again and shows w=1, hc1=00/38, hc2=0000/0003, bs=bc=sdm=ok=0, st=00000000, de=0. w=1 means the warm probe failed at CMD13 before the ADMA read: UEFI/SdccDxe left the card deselected/not in Transfer even though the controller still had HC1=0x38/HS400/DLL. Next warm step: send CMD7 RCA1 \(R48\) first, then CMD13 and the ADMA2 LBA1 read. If CMD7 also fails, the RCA is not 1 or UEFI reset the card; then either preserve the selected state in UEFI or go through re-identification with the correct HS\_TIMING/BUS\_WIDTH order.
- boot-irq63 \(tag irq63\) adds CMD7 RCA1 \(R48, no busy\) before the warm CMD13 and ADMA2, because irq62 showed w=1/st=0 and the card was deselected at handoff. HC1=0x38, CLK=0x0007 and VSPEC=0x240a0e stay untouched. Expected stages are warm c7 ok -&gt; warm c13 ok -&gt; w=3 with d2=EFI PART; warm c7 err means the RCA is not 1 or UEFI reset the card, and warm c13 state/err means the card is selected but not in Transfer. The black screen remains a separate irq55-vs-irq56+ normal-path regression \(irq60 also blacked\).
- boot-irq63 photo \(tag irq63\): w=1/st=0, but that build was flawed -- the original CMD13 still ran before CMD7 and the code compared the CMD7 response against 0x900, so the result is not a valid RCA test \(the stray CMD13 could also wedge the command line\). boot-irq64 \(tag irq64\) corrects the order to CMD7 RCA1 -&gt; CMD13 -&gt; ADMA2 and uses single-step w codes: 1 boot state/precondition, 2 CMD7 failed, 3 CMD13 failed, 4 ADMA failed, 5 EFI PART kept. HC1=0x38/CLK/VSPEC still untouched.
- boot-irq64 photo \(tag irq64\): w=2, st=00000000, hc1=00/38, hc2=0000/0003, bs=bc=sdm=ok=0. w=2 is CMD7 RCA1 failing -- the card does not answer the bootloader RCA at handoff, consistent with UEFI/SdccDxe deselecting or powering the card down. The normal path then runs \(EMMC st=1266 power/voltage probe, e=0001, p=00\). irq55 \(PIO, no SDMA\) did not black; irq56+ added the normal SDMA LBA1 probe and every later image did. boot-irq65 \(tag irq65\) removes that normal SDMA probe: LBA1 is PIO-only, d2/r2 stay zero, emmc\_read\_blocks stays PIO, while the warm CMD7/ADMA2 code remains diagnostic \(expected w=2\).
- boot-irq65 photo \(tag irq65\): PIO-only stayed alive to time=308s \(no black\), so the normal-path SDMA LBA1 probe added in irq56 was the black-screen regression. But LBA1 still read 4546492045464920 \("EFI " twice, n=512, s=0\), EXT\_CSD read as rev0/sec0 and init failed 6; CMD13 stayed Transfer/no error. The card is still HS400 while the host is 1-bit default speed. boot-irq66 \(tag irq66\) adds the correct CMD6 order after CMD7/CMD13: EXT\_CSD\[185\]=0 \(HS\_TIMING\) then EXT\_CSD\[183\]=0 \(BUS\_WIDTH\), before the PIO LBA1 read. irq55 only did the width half, hence its invalid HS400-on-1-bit result.
- boot-irq66 photo \(tag irq66\): the HS\_TIMING=0 then BUS\_WIDTH=0 reset did not change the result -- d1 is still 4546492045464920, n=512, s=0, EXT\_CSD rev0/sec0 and init failed 6 -- but the panel stayed alive at time=412s, so PIO-only fixed the black screen and the card-state switch did not fix the data. The hs0/bw1 stage lines had already scrolled out. boot-irq67 \(tag irq67\) stores each CMD6 as \(error&lt;&lt;24\)\|busy-timeout\|R1 and prints c6=&lt;hs&gt;/&lt;bw&gt; on the EMMC2 row, so the next photo says whether the card accepted the switch, returned SWITCH\_ERROR, or the command/busy failed.
- boot-irq67 photo \(tag irq67\): EMMC2 c6=00800900/00800900. Decode: high byte error 0, bit23 0x800000 set \(DAT0 busy not released in 200 ms\), low 24 bits R1=0x900 \(Transfer, no SWITCH\_ERROR\). So both CMD6 commands were accepted by the card, but the driver continued while the switch was still busy; the PIO LBA1 then timed out at Transfer Complete \(e=cc04\) and returned the stale word. boot-irq68 \(tag irq68\) waits up to 2 s per R1b busy, stops before data if still busy, and settles 1 ms before the PIO read.
- boot-irq68 photo \(tag irq68\): c6 first value 00000900 = HS\_TIMING=0 succeeded with no busy/error, but init then returned 60 \(ETIMEDOUT\), bs=bc=0 and no data command; the bottom state had CMD inhibit set. The BUS\_WIDTH=0 step is what wedged -- forcing the bootloader 8-bit card to 1-bit was wrong. boot-irq69 \(tag irq69\) keeps HS\_TIMING=0 only, drops BUS\_WIDTH entirely, sets host HC1 to 8-bit \(0x20\), and keeps the PIO-only data path.
- HuajiFruit/UniXNU-sirius \(Xiaomi Mi 8 SE, SDM710/SDCC1 eMMC\) is the closest working reference: package/sirius\_emmc.c documents that vqmmc is fixed 1.8 V while the controller was left at 3.0 V, so commands work but multi-line data does not; its probe sets POWER\_CONTROL=0x0b and HOST\_CONTROL2 bit3 before PIO and then reads EFI PART. It stays 8-bit, uses HS\_TIMING=1 at 25/50 MHz \(EXT\_CSD rev8 width2 timing1\), uses 32-bit ADMA2 with 8-byte descriptors \(the 64-bit form walked past END\), scans RCA 1..8 and sends CMD7 R1b, and package/NativeEmmc.cpp publishes IOBlockStorageDevice so IOStorageFamily makes the IOMedia root window. Our irq65-69 ran POWER\_CONTROL=0x0f \(3.3 V\) and HC2 bit3 clear; boot-irq70 \(tag irq70\) forces 0x0b + HC2 bit3 before the PIO read, keeping 8-bit/default speed/PIO-only.
- boot-irq70 photo \(tag irq70\): c7 ok st=00000900, hs0 ok, hs0 busy, init failed 60. HS\_TIMING=0 was accepted but DAT0 busy did not clear in 2 s, and the 1.8 V write was placed after HS0, so irq70 never executed the sirius voltage fix. boot-irq71 \(tag irq71\) moves POWER\_CONTROL=0x0b + HC2 bit3 to after CMD3 and before CMD7/CMD13/HS0, matching sirius prepare order; the late duplicate is removed.
- boot-irq72 \(tag irq72\) adds a diagnostic auto-reboot: BootProgress monitor sees qcom\_emmc\_err \!= 0, keeps the panel alive for 30 s, then calls reboot\_kernel\(RB\_QUICK\|RB\_NOSYNC, NULL\). This is a reset to the current boot partition \(TWRP right now\), not fastboot; it only removes the manual power cycle after a failed eMMC run.
- boot-irq72 photo \(tag irq72\): the autoreboot stage fired, but reboot\_kernel\(RB\_QUICK\|RB\_NOSYNC\) went through IOPlatformExpert shutdown notifications and panicked "Halt/Restart Timed Out" after 30 s; the device did not reset. boot-irq73 \(tag irq73\) calls PE\_halt\_restart\(kPERestartCPU\) directly, bypassing the notification timer, and logs PE restart/PE returned/no PE restart on the panel.
- boot-irq74 \(tag irq74\) removes the autoreboot and adds a native polling USB2 CDC ACM console ported from UniXNU-zeta \(pexpert/arm/native-dwc3-console.c\). It registers as a pe\_serial backend, polls from the rtclock tick, and reads ADT /chosen/unixnu,dwc3-console = &\#123;0x0a800000, 0x100000&\#125; \(R11 ssusb@a800000\). Product is r11 XNU log, VID:PID 0525:a4a7. It relies on firmware leaving DWC3 clocks/PHY alive; the zeta QSCRATCH qcom-usb0 override is not enabled for this base.
- boot-irq75 \(tag irq75\) adds the R11 QUSB2 PHY init at 0xc012000 using the stock DTS qcom,qusb-phy-init-seq, QSCRATCH session bits at 0xa8f8810, and panel diagnostics u=phase/error/gsnpsid. This is a port of the hardware init sequence, not a Linux driver injection; GCC USB clocks/GDSC/VBUS are still not initialized in XNU.

### Completion criteria

- The kernel mounts an APFS root from eMMC and the payload can address block slices.

### Current limits

- No XNU eMMC driver has completed a read on hardware yet. UEFI storage exists through the vendor SdccDxe, which is enough to read the payload but not to run the kernel stack.
- Nothing publishes an IOMedia yet, so IOKitBSDInit cannot find a root media; boot-irq18 only stops it from panicking there.

### Next action

- Boot boot-control/boot-irq75.img manually and read the EMMC2 u=phase/error/gsnpsid field plus the host USB tree. u=0/0/0 means the driver never ran; u=1 with a nonzero gsnpsid is the DWC3 core ID \(expect high 16 bits 0x5533 or 0x3331\); u=4 means active and the host should show 0525:a4a7 / r11 XNU log.
- If u shows an error or no host port appears, add the GCC USB clocks/GDSC and VBUS/QSCRATCH details from the stock DTS; the PHY/QSCRATCH sequence alone assumes UEFI left those supplies on. If u=4 but no tty, check the CDC descriptors/macOS binding.
- No auto-reboot: the panel stays up for reading.

### Evidence

- `host`: [userdata-root.img 8357150720 bytes \(7.78 GiB\), sha256 818e4e37…, in a partition of 56933462016 bytes: OS 5628790272 B at 0x100000, SystemOS 2726297600 B at 0x14fa00000. Built in 1m52s from the local IPSW; the flash command is printed by the step.](https://github.com/appleiPodTouch4/unixnu-r11/blob/93ab51e474b3845b660677bb16280060de709e85/docs/evidence/userdata-build.txt)
  Command: <code>./unixnu build userdata --ipsw iPhone10,3,iPhone10,6_16.5_20F66_Restore.ipsw</code>. Revision: `9a193a520b30c7263d31189426052c5e5e50938f`.
- `source`: [GPT geometry: boot 245760-376831, userdata grow from LBA 10944512, 69 partitions](https://github.com/appleiPodTouch4/unixnu-r11/blob/93ab51e474b3845b660677bb16280060de709e85/inputs/partitions.json)

## Display {#display}

`planned`

Components: `GopFramebuffer`.

### Hardware and dependencies

- Samsung S6E3FA3 AMOLED 1080x1920, command mode, single DSI, 60 Hz \(qcom,mdss\_dsi\_oppo16051samsung\_s6e3fa3\_1080p\_cmd\).
- MDSS 0xc900000+0x90000, DSI PLL/PHY 0xc994400, MMSS SMMU 0xcd00000.
- Continuous splash buffer 0x9D400000+0x02400000.

### Configuration

- Firmware: USE\_CUSTOM\_DISPLAY\_DRIVER = 0, SimpleFbDxe over PcdFrameBuffer 1080x1920x32.
- Kernel: offline-legacy-gop=1 renders the console into GOP; CONFIG\_XNU\_NATIVE\_LEGACY\_DISPLAY=n.

### Procedure

- Boot the FD and confirm the menu over the OPPO boot logo.
- Then write a DSI panel driver replaying the init sequence from inputs/r11-stock.dts.

### Development findings

- The panel node in the stock tree holds 79 properties including the full init, timing and PHY tables, so the sequence does not have to be reverse engineered from the kernel binary.
- SimpleFbDxe finds its buffer by the Display Reserved region name, which is why MemoryMapLib keeps that exact string.

### Completion criteria

- Menu, then XNU console, then a framebuffer handoff at native resolution over the real MDSS driver.

### Current limits

- No MDSS/DSI driver. Display works only as long as the vendor bootloader leaves the panel on and the framebuffer untouched.
- No backlight control: r11-backlight is passed but unimplemented.

### Next action

- Extract the panel init sequence into driver tables and bring up DSI in command mode with a test pattern.

### Evidence

- `source`: [Panel node with its full init, timing and PHY tables and the splash reservation](https://github.com/appleiPodTouch4/unixnu-r11/blob/93ab51e474b3845b660677bb16280060de709e85/inputs/r11-stock.dts)

## Input {#input}

`planned`

### Hardware and dependencies

- Synaptics S3508 touch at i2c@c175000 \(0x0C175000\), address 0x20, node synaptics16051@20, compatible synaptics-s3508.
- Interrupt on TLMM GPIO 67 \(from the stock device tree\).

### Configuration

- i2c1 is enabled in dts/r11.dts with a touchscreen@20 child tagged unixnu,adt-name = touchscreen.

### Procedure

- Read the RMI4 product info over the vendor I2CDxe first, then implement the XNU HID driver.

### Development findings

- The touch controller is an RMI4 device, so the driver needs function 0x11 \(2D\) plus firmware query, not a register map.
- No UART is exposed on this board, so early diagnostics rely on the framebuffer.

### Completion criteria

- Touch events reach the XNU HID stack with correct coordinates in both orientations.

### Current limits

- No driver. r11-touch and r11-touch-hid are passed but unimplemented.

### Next action

- Dump RMI4 function descriptors through UEFI I2CDxe to confirm the sensor generation.

### Evidence

- `source`: [Synaptics S3508 at i2c@c175000 address 0x20 and its interrupt line from the stock tree](https://github.com/appleiPodTouch4/unixnu-r11/blob/93ab51e474b3845b660677bb16280060de709e85/inputs/hw.json)

## Power {#power}

`planned`

### Hardware and dependencies

- PM660 + PM660L over SPMI \(0x0800F000\), charger MCU pic16f/stm8s at 0x25/0x26 on i2c@c176000, fuel gauge bq27541 at 0x55.
- Stock XBL PSHOLD at 0x010AC000, PSHOLD offset 0xC000.

### Configuration

- Firmware: vendor PmicDxeLa, AdcDxe, TsensDxe, ChargerExDxe and QcomChargerDxeLA are included.
- Kernel: r11-pmgr=2 and r11-disable-watchdogd=1 are passed but have no board implementation.

### Procedure

- Verify charger detection and battery readings from the firmware menu before adding kernel power management.

### Development findings

- Charging is not PMIC-only: OPPO VOOC runs through an external MCU, so the vendor charger profile must be replaced with R11 values.
- The watchdog must be disabled or serviced before XNU reaches launchd; the board passes r11-disable-watchdogd=1.
- The minutes-later black screen was first attributed to the PMIC charger watchdog \(QcomChargerCfg.cfg EnableChargerWdog=1, no XNU charger driver\), but boot-irq60 with EnableChargerWdog=0 also blacked, so that hypothesis is disproved. irq55 is the only non-blacking control: the black screen is a regression introduced by the eMMC normal path changes after irq55 \(irq56+ removed CMD6/1-bit, then 400 kHz and the new probe\), most likely the HS400/1-bit mismatch wedging SDCC. Keep EnableChargerWdog=0 \(harmless\), but do not treat the charger watchdog as the cause.
- boot-irq60 also blacked \(user correction\), so the charger watchdog is excluded. irq55 did not black; every image after it did. The next test must isolate the normal eMMC path: read-only boot state and no emmc\_device\_init/data command, then see whether the black screen disappears before touching APSS/TZ/PMIC watchdog reasoning.

### Completion criteria

- Battery level, charger state and thermal readings are correct; the device survives a full boot without a watchdog reset.

### Current limits

- Vendor charger and battery profiles are inherited from the reference SDM660 device.

### Next action

- Charger watchdog is excluded: irq60 with EnableChargerWdog=0 still blacked. irq55 is the only non-blacking control. Isolate the eMMC normal path before building anything else: a boot image that publishes the boot state and never runs emmc\_device\_init / any card data command. If that stays alive, the normal path data phase is the black-screen cause; if it also blacks, investigate APSS WDT / TZ / PMIC reset reason.
- Do not re-enable the charger watchdog, but do not claim it as the fix.

### Evidence

- `source`: [Kernel arguments and the vendor DXE list currently selected for power and charging](https://github.com/appleiPodTouch4/unixnu-r11/blob/93ab51e474b3845b660677bb16280060de709e85/board.toml)

## Image assembly {#packaging}

`implemented`

Components: `XnuPrelink`, `DarwinBoot`.

### Hardware and dependencies

- Stock boot image header: version 0, page 4096, kernel 0x8000, ramdisk 0x1000000, tags 0x100, second 0xf00000.
- IPSW: iPhone X 16.5 \(20F66\), product iPhone10,3, chip\_id 0x8011.

### Configuration

- \[bootimg.image\] mirrors the stock header; \[payload\] volume R11ESP, size 192 MiB, loader firmware.
- No \[\[bootimg.dtb\_node\]\]: the stock tree already has /reserved-memory/splash\_region.

### Procedure

- ./unixnu build kernel -D ../UniXNU-r11 \(macOS 12 host, scripts/xnu-clang\)
- ./unixnu build payload --unique-chip-id &lt;hex&gt; --trust-cache &lt;bundle&gt;
- ./unixnu bootimg -D ../UniXNU-r11 --uefi ../uefi-r11-base --dtb ../uefi-r11-base/Platforms/OPPO/r11Pkg/DeviceTree/r11.dtb

### Development findings

- OPPO uses tags 0x100 rather than the usual 0x1e00000; bootimg verifies the load addresses and rejects a wrong offset.
- The boot partition is 64 MiB while the payload is 192 MiB, so the image must go through fastboot boot, not fastboot flash boot.
- The stock boot image is gzip\(Image\) plus a multi-DTB block of three trees; the firmware DTB for bootimg is the single 16051 tree.
- Measured on this host: kernel.macho 53,792,768 bytes \(prelinked, sha256 7cf8d413d5c7edcf...\), ADT 15,688 bytes, payload.img 201,326,592 bytes, boot.img 202,670,080 bytes with kernel \(BootShim\) 1,338,688 bytes at 0x8000 and the payload as ramdisk at 0x1000000. The payload volume holds EFI/UniXNU/unixnu.toml, Payloads/kernel.macho and Payloads/kernel.macho.adt.
- The ramdisk address in the boot header is an offset from ABL's DRAM base 0x80000000, not a physical address: 0x01000000 lands at 0x81000000. The firmware memory map reserves 0x80000000+0x05800000 for kernel and ramdisk and puts SMEM at 0x86000000, so a 192 MiB payload spans 0x81000000-0x8D000000 and covers SMEM, while a 64 MiB payload \(boot.img 68,452,352 bytes\) stops at 0x85000000. The first device boot of the 192 MiB image showed no output at all after fastboot reported OKAY.

### Completion criteria

- boot.json reports the expected kernel address, tags address and a nonzero ramdisk size, and the image boots to the UniXNU menu.
- Device run of boot-payload-lzma3.img \(8,802,304 bytes, LZMA-packed 56 MiB payload\): the menu shows the payload entry, selecting xnu runs BootShim to ExitBootServices, prints the CPU state \(CurrentEL 1, TCR\_EL1 0x2b00803510, ID\_AA64MMFR0\_EL1 0x1122\) and draws the green handoff bar -- the kernel branch was reached on 2026-11-01.

### Current limits

- Payload size assumes fastboot boot with max-download 512 MiB \(reported by getvar on the reference unit\).
- The ramdisk is placed by ABL at ramdisk\_addr + DRAM base, so size\_mib is bounded by the firmware memory map, not only by the download limit: 192 MiB lands on 0x81000000-0x8D000000 and covers SMEM at 0x86000000. 64 MiB keeps the payload inside the 0x80000000+0x05800000 kernel/ramdisk window.
- ABL silently refuses ramdisks above \~32-56 MiB: 8/32 MiB payloads boot the menu, 64 MiB produces no output. The working payload is LZMA-packed \(raw stream, hand-built 13-byte header, dict 32 KiB to fit the LZMA library 64 KiB scratch\) and UniXNURamDiskDxe expands it into the kernel window.

### Next action

- XNU branch was reached but the kernel printed nothing after the handoff bar. Observe whether the device reboots on its own \(panic watchdog\) or stays dark, then bring up a serial console \(SDM660 debug UART\) or an early framebuffer console in XNU to capture the first kernel output.

### Evidence

- `source`: [Stock boot image header fields that board.toml \[bootimg.image\] mirrors](https://github.com/appleiPodTouch4/unixnu-r11/blob/93ab51e474b3845b660677bb16280060de709e85/inputs/hw.json)
- `source`: [The 60 arch/SoC patches and the archive builders pass on macOS 12, and so does the kernel step: scripts/xnu-clang hides the three Xcode 15 arguments, two board patches replace the mig static\_asserts, CCC\_OVERRIDE\_OPTIONS clears the archive -Werror pair, and an iig patch declares IORPCMessageFromMach in the generated sources. .github/workflows/macos.yml stays available but is no longer required.](https://github.com/appleiPodTouch4/unixnu-r11/blob/93ab51e474b3845b660677bb16280060de709e85/docs/host-toolchain.md)

## Diagnostics {#diagnostics}

`planned`

### Hardware and dependencies

- No UART pads on the R11; the framebuffer is the only early output.
- Stock bootargs keep printk.disable\_uart=1.

### Configuration

- boot-progress=2 and offline-legacy-gop=1 run the console through the framebuffer.
- serial=3 is still passed for the case where a UART is soldered on.

### Procedure

- Save the framebuffer checkpoint after each stage; use unixnu/scripts for log extraction.

### Development findings

- With no serial console, every firmware checkpoint must be visible on screen; the UniXNU menu over the vendor logo is the first such checkpoint.

### Completion criteria

- Each bring-up stage is observable and recorded with the image revision.

### Current limits

- Advanced Logger and QR log export are not integrated into the r11 firmware yet.

### Next action

- Add AdvancedLogDxe and the Tools menu entry to the FD so firmware logs can be exported without a UART.

### Evidence

- `source`: [Boot arguments that route the console through the framebuffer](https://github.com/appleiPodTouch4/unixnu-r11/blob/93ab51e474b3845b660677bb16280060de709e85/board.toml)

## GPU {#gpu}

`planned`

### Hardware and dependencies

- Adreno 512 at 0x05000000, GPU SMMU 0x05040000, GPUCC 0x05065000, GMU 0x00780000.

### Configuration

- dts/r11.dts keeps the GPU nodes disabled; no GPU kernel argument is passed.

### Procedure

- Only after display and storage are device-verified.

### Development findings

- Adreno 512 is a different generation from the Adreno 740 path the project uses today, so the existing GPU kits do not apply directly.

### Completion criteria

- Metal or IOKit GPU services come up on the device.

### Current limits

- Out of scope for the first bring-up.

### Next action

- Evaluate the Adreno 5xx firmware and PM4 packet format against kits/AdrenoPM4.

### Evidence

- `source`: [Adreno 512, GPU SMMU and GPUCC addresses decoded from the stock tree](https://github.com/appleiPodTouch4/unixnu-r11/blob/93ab51e474b3845b660677bb16280060de709e85/inputs/hw.json)

## Network {#network}

`planned`

### Hardware and dependencies

- WCN3990 class combo at 0x18800000, integrated in the SoC.

### Configuration

- wlan node disabled in the SoC dtsi.

### Procedure

- After storage and input.

### Development findings

- The R11 uses the integrated WLAN block, so no SDIO card detection is needed.

### Completion criteria

- Association and packet transfer through the XNU network stack.

### Current limits

- No driver, no firmware extraction.

### Next action

- Identify the WCN3990 firmware partition and the calibration data location.

### Evidence

- `source`: [Integrated WLAN block address from the stock tree](https://github.com/appleiPodTouch4/unixnu-r11/blob/93ab51e474b3845b660677bb16280060de709e85/inputs/hw.json)

## Audio {#audio}

`planned`

### Hardware and dependencies

- AK4376 DAC at 0x10 on i2c@c1b6000, TFA98xx amplifier at 0x36, ADSP 0x15700000.

### Configuration

- No audio nodes enabled.

### Procedure

- After the core bring-up stages.

### Development findings

- Playback needs the ADSP firmware, which is a reserved region in the stock tree \(0x92A00000\).

### Completion criteria

- Playback and capture through the XNU audio stack.

### Current limits

- Out of scope for the first bring-up.

### Next action

- Extract the ADSP firmware from the OFP package and confirm the region ownership.

### Evidence

- `source`: [AK4376, TFA98xx and ADSP addresses decoded from the stock tree](https://github.com/appleiPodTouch4/unixnu-r11/blob/93ab51e474b3845b660677bb16280060de709e85/inputs/hw.json)

</div>
