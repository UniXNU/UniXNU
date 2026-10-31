# Xiaomi Mi 8 SE \(HuajiFruit\)

[HuajiFruit/UniXNU-sirius](https://github.com/HuajiFruit/UniXNU-sirius)

<div v-pre>

Xiaomi Mi 8 SE running the UniXNU source kernel through its own U-Boot UEFI: entry, MMU, timer, PSCI, platform expert and the boot-progress console work on hardware; IOKit is blocked on AppleARMCPU claiming /cpus.

源记录: [porting.toml](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/porting.toml), `ac0c900485f3c0cd18de9707579a1cdcd3365503`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `implemented` |
| [固件与启动](#firmware) | `implemented` |
| [CPU 与中断](#cpu) | `implemented` |
| [内存与 DMA](#memory) | `implemented` |
| [存储与根卷](#storage) | `device-verified` |
| [显示](#display) | `implemented` |
| [输入](#input) | `device-verified` |
| [GPU](#gpu) | `planned` |
| [网络](#network) | `planned` |
| [音频](#audio) | `planned` |
| [电源](#power) | `planned` |
| [镜像组装](#packaging) | `implemented` |
| [诊断](#diagnostics) | `implemented` |
| [boot-chain](#boot-chain) | `implemented` |

## 配置 {#configuration}

`implemented`

组件: `ArmDTPlatform`, `DarwinBoot`.

### 硬件与依赖

- SoC: SDM710 \(Kryo 360, 2x Cortex-A75 + 6x Cortex-A55\), GIC-500 GICv3, 19.2 MHz Qualcomm XO counter, PSCI over SMC.
- DRAM: 6 GiB model, 2 GiB at 0x80000000 plus 0xfd6c0000 at 0x100000000, 0x17d6c0000 usable.
- Target OS: the unchanged iPad7,1 iPadOS 17.7.11 \(21H461\) restore image, the same kernelcache as fajita and sheng.
- Hardware sources: mainline sdm670.dtsi, the vendor kernel tree and measurements on the phone.

### 配置

- board.toml is format 2 \(schema\_version = 2\) and selects soc\_source = sdm710 and os\_profile = ipados-17.7.11-21H461.
- dts/sirius.dts describes memory, the eight cores and their affinities, and includes the SoC DTSI for the GIC, PSCI and counter.
- configs/sirius\_defconfig keeps the first-console kernel configuration and turns off the profile settings the image does not use yet.
- The prelink roots, slide, early security initializer and Apple device-tree identity come from the OS profile; the board adds sleep-disabled, the product model and the button set.

### 操作步骤

- From a UniXNU checkout: ./unixnu defconfig sirius\_defconfig -D ../UniXNU-sirius.
- Then ./unixnu fetch, ./unixnu status --json and ./unixnu tree; the output is out/sirius/ipados-17.7.11-21H461/sirius/.
- Compile the hardware tree through the payload step \(prototype: dtc -I dts -O dtb -i &lt;soc&gt;/dts dts/sirius.dts\).

### 开发经验

- kernel\_args pass sirius-gpu=2 \(phases 1 and 2: CX power, the GMU SMMU context, the GMU firmware boot and HFI\); build-sirius-gpu.py now also embeds a630\_gmu.bin \(see the gpu area\).
- \[adt.chosen.bytes\] adds the zeroed darwinboot-efi-map report slot \(see the memory area\).
- \[payload.adt\] owned\_memory\_size is 0xaa000000 \(2.66 GiB\) instead of 0x40000000 \(see the memory area\).
- kernel\_args pass sirius-skip-setup=1 \(see the diagnostics area\).
- kernel\_args add sheng-touch-hid=1 \(NativeHidInput adds the touch collection to its combined device; see the input area\).
- kernel\_args pass dk=0 so DriverKit dexts do not match \(see the input area\).
- \[components\] include adds ShengHidInput, \[kernel\] archives add component:ShengHidInput before build-native-legacy-display.py, and kernel\_args pass sirius-touch-hid=1 \(see the input area\).
- \[kernel\] archives build build-sirius-gpu.py into libShengPlatformPower.a and kernel\_args pass sirius-gpu=1 for the Adreno 616 phase-1 probe \(see the gpu area\).
- \[kernel\] archives build build-sirius-touch.py into libShengPlatformPower.a and kernel\_args pass sirius-touch=1 for the FTS521 touch probe \(see the input area\).
- \[adt.chosen.u32\] sets ephemeral-storage = 1 so datamigrator skips the first-boot migration: kernel ca828cc / payload 95bcb3a showed the migration bar unfinished at t=2177 s with the CPU 87% idle and the plugin wrapper killed by signal 9; the staged system apps are not installed while it is set \(see the diagnostics area\).
- kernel\_args pass validation\_disables=0x10 so user stackshots are refused \(see the diagnostics area\).
- \[payload\] text\_fixups repeats the OS profile's four fixups \(a board list replaces the profile's\) and adds the CoreUI sharedCIContext fixup for iconservicesagent \(see the display area\); kernel\_args pass sirius-spawn-log=1 for the SPAWN console lines \(see the diagnostics area\).
- board.toml gained build-sirius-emmc.py in the archive list next to the USB console entry.
- board.toml selects AppleKeyStoreState in \[components\] include and passes offline-key-events=1 and sheng-aks=1 for the AppleKeyStore stand-in \(see the power area\).
- kernel\_args pass sirius-fb-cached=1 for the GopFramebuffer board fork's cacheable source reads \(see the display area\).
- .gitignore ignores tmp/: downloaded kernels and payload images for flashing go there, not on the Desktop.
- kernel\_args pass sirius-cpufreq=1 and \[kernel\] archives build build-sirius-cpufreq.py into libShengPlatformPower.a \(see the power area\).
- kernel\_args pass sirius-fb-wc=1 for the GopFramebuffer board fork \(drivers/GopFramebuffer\): the scanout is mapped write-combined instead of uncached \(see the display area\).
- A selected component with a kernel build recipe needs a component: entry in \[kernel\] archives, or unixnu stops with 'archives needs component entries'; that recipe runs the tree's build-arm-driver.py, which is this repository's copy, so it has to know the component's name. The recipe's archive is not linked: the kernel force-loads only the archives build-xnu-4k-baseline.sh names.
- board.toml lists build-sirius-emmc.py alongside the other archives, because the SDCC1 probe is compiled the same way as the USB console and joins the same force-loaded archive.
- Format 2 replaced the hand-written ADT generator of the legacy port \(scripts/make-sirius-adt.py\) with a board DTS: the payload step compiles the tree and derives kernel.macho.adt from it.
- The arm-io base is derived from the exported nodes, not written by hand: the GIC at 0x17a00000 makes the window start at 0x17000000, which XNU reads as the SoC base.
- The legacy port set ipad\_identity = true; in format 2 the same identity is the OS profile's \[adt\] tables, so the board only states its deviations.
- configs/sirius\_defconfig keeps the ARM64 profile's CONFIG\_XNU\_NATIVE\_PAN=y: Kryo 360 implements PAN and SCTLR\_EL1 leaves SPAN clear, so every exception entry sets PSTATE.PAN, and only the PAN build clears it around copyin/copyout \(see the diagnostics area\).
- CONFIG\_XNU\_NATIVE\_CS\_HASH\_CACHE=y is back on: iPadOS signs code in 16 KiB pages, and this 4 KiB kernel accepts the dyld shared cache's signature only through the native 4K hash cache.
- The SystemOS cryptex mount \(OWNER\_CACHE\_MOUNT, OWNER\_CACHE\_STARTUP, OWNER\_UNION\_SYSTEMOS\) builds in the bring-up mode BRINGUP\_OWNER\_CACHE, as the uke port does, and its volume is authorized by the boot argument sirius-allow-unverified=1, not by an owner root policy.
- sirius\_emmc\_hs=3 lets the eMMC driver climb to 25, 50 and 100 MHz, each step proven against blocks read at 400 kHz; the card settles at 50 MHz \(HS\_TIMING 1\).
- The Data volume: OWNER\_DATA\_MOUNT with SIRIUS\_DATA\_SEED \(NativeEmmc serves the seed instead of RamBlock\) and CONFIG\_XNU\_OWNER\_DATA\_VOLUME\_UUID = EB6CBBA0-ECB9-4556-A483-4B60D54D4306, the volume of the seed that .github/workflows/data-seed.yml built; \[payload.adt\] owned\_memory\_size gives the kernel a 1 GiB window to hold the seed. On the phone the window lands below 4 GiB \(seed at 0xa3cc1000\), the seed is published as the Data window and the kernel mounts its volume \(disk3s1, OwnerData\) at /private/var before launchd.
- With the Data volume mounted, launchd's mount -P 1 still exits 66: apfs logs 'DT\_get\_fstab\_entries: failed to get filesystem entry at: /filesystems/fstab', and the uke port traced the fatal error to the missing /chosen/boot-manifest-hash. \[adt.chosen.bytes\] boot-manifest-hash now carries uke's explicit bring-up boot-set identity \(SHA-384 of 'UkeBringup.BootSet.v1\\0'\), as asteroids does. On the phone mount-phase-1 and mount-phase-2 then pass and launchd reports 'Early boot complete. Continuing system boot.'
- Past early boot the 32 MiB Data volume runs out of space \(ENOSPC\) and watchdogd traps \(brk \#1\), which panics the boot. kernel\_args now pass sheng-disable-watchdogd=1 and sheng-lite=1 to package/BootWatchdogPolicy.c \(already linked and called after the Data mount\), which disables watchdogd and the network/iCloud/photo daemons through launchd's disabled.plist, and the seed workflow grows the container to size\_mib \(256 MiB, held in RAM inside the 1 GiB window\); the volume UUID stays across the grow. Not yet booted.
- Each seed workflow run formats a new volume, so the 256 MiB seed \(run 40621149780, owner-data.cdr 48a10f78...\) has UUID E06A21C1-6686-49B8-B242-ED82B00F4AF8, which the defconfig now names; with the seed inside, the payload files take 306 MiB, so \[payload\] size\_mib is 512 \(the vendor partition holds 3 GiB\).
- Persistent Data configuration: kernel\_args now passes sirius-data-write=1 so NativeEmmc publishes the persistent Data container behind the root image in userdata read-write; \[payload\] size\_mib is reset to 256 MiB because the Data container no longer travels in the vendor payload volume; .github/workflows/data-seed.yml default container size is updated to 8192 MiB.
- Display configuration: board.toml adds GopFramebuffer to \[components\] include, replaces build-sirius-probes.py with build-native-legacy-display.py in \[kernel\] archives, adds offline-legacy-register=1, offline-legacy-gop=1, offline-legacy-unit-scale=2, offline-legacy-pm=1, offline-legacy-validate=1, offline-legacy-transfer=1, offline-legacy-cpu-present=1, offline-legacy-phase=4, offline-mobile-graphics-client=1, offline-mobile-graphics-load=1, offline-apfs-load=1, sheng-vsync=60 to kernel\_args, and sets artwork-display-gamut=sRGB in \[adt.product.string\]; configs/sirius\_defconfig enables CONFIG\_XNU\_NATIVE\_LEGACY\_DISPLAY=y, clears CONFIG\_XNU\_EXTRA\_LD\_ARCHIVES, and updates CONFIG\_XNU\_OWNER\_DATA\_VOLUME\_UUID to match the persistent Data volume.

### 完成条件

- status --json resolves the ARM64, sdm710, iPadOS and device layers, prints a non-empty patch order and shows the device package as kits/sirius.
- The compiled hardware tree carries one contiguous memory range equal to payload.dram\_size, eight enabled CPUs and a PSCI method.

### 当前范围

- The SoC profile is new: only the GIC, PSCI, counter and the timer INTID are shared, everything else is still board-local.
- The Data seed holds files from the IPSW, so the workflow uploads it encrypted \(ARTIFACT\_PASSPHRASE\) and the payload step takes it from a local path; a new seed has a new volume UUID that the defconfig must follow.
- The 1 GiB window must start below 4 GiB for the eMMC's 32-bit ADMA2; whether this unit's memory map offers one such run is not yet observed.

### 下一步

- Run status --json and tree against this repository and commit the resulting unixnu.lock.
- Rebuild the payload from dts/sirius.dts and compare the generated ADT with the legacy one before the next hardware boot.

### 证据

- `source`: [Hardware values, the boot chain and the bring-up history of the legacy port, from which this configuration is carried over.](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/docs/HANDOFF.zh-CN.md)
- `device`: [With CONFIG\_XNU\_NATIVE\_PAN=y the driver reads PAN as 4194304, all eight CPUs pass the init copyout and launchd's first syscalls return.](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/docs/evidence/sirius-usb-console-20261027-pan.log)
  Command: <code>fastboot flash vendor payload-E-pan-noclear.img; fastboot reboot; python scripts/capture-usb-console.py --follow --wait 180 --duration 420</code>. Revision: `b1a11c4f4eb0bfd28b2dd3dfc59b3c7e3a3e742f`.
- `device`: [With the SystemOS mount, the 4K hash cache and sirius\_emmc\_hs=3 the shared cache is verified in about 104 s at 50 MHz and dyld maps it.](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/docs/evidence/sirius-usb-console-20261027-fast-emmc.log)
  Command: <code>fastboot flash vendor payload-H-fast.img; fastboot reboot; python scripts/capture-usb-console.py --follow --wait 180 --duration 900</code>. Revision: `1163990229f446753ef006126e55922aa23bda6a`.
- `host`: [Run 40615426205 built owner-data-32.cdr \(33554432 bytes, sha256 5679d2cf59eba99aa048be0c0e253581aa5bfb1fdff7ff431ed9e91c2bd58c63\) with APFS volume EB6CBBA0-ECB9-4556-A483-4B60D54D4306.](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/.github/workflows/data-seed.yml)
  Command: <code>gh workflow run data-seed.yml -R HuajiFruit/UniXNU-sirius --ref main</code>. Revision: `9562de8b362e6bbae9844052826c609996866aed`.

## 固件与启动 {#firmware}

`implemented`

组件: `DarwinBoot`.

### 硬件与依赖

- The device runs sirius-distro \(mainline Linux\) and its boot partition carries U-Boot 2026.07 with EFI\_LOADER, the UEFI boot manager, GOP through vidconsole and EFI block volumes over FAT.
- UniXNU.efi is built on the host by ./unixnu build package; DarwinBoot.efi is built from drivers/DarwinBoot.
- The payload volume goes to the unused vendor partition mmcblk0p80 \(3 GiB\) and is selected by a marker file.

### 配置

- board.toml has no \[firmware\] table: there is no Mu-Silicium firmware and no boot image on this port.
- \[payload\] loader = "payload" makes the generated unixnu.toml load Payloads/DarwinBoot.efi as a \[\[driver\]\] instead of expecting it in the firmware volume.
- scripts/make-uboot-payload.py adds \\EFI\\BOOT\\BOOTAA64.EFI \(UniXNU.efi\) and the DarwinBoot.efi driver to the payload FAT volume.

### 操作步骤

- fastboot flash boot the U-Boot image, fastboot flash vendor the finished payload volume, then select the UniXNU menu entry in U-Boot.
- U-Boot boots UniXNU when /EFI/UniXNU/BOOTUNIXNU exists on the vendor partition and boots Linux otherwise.

### 开发经验

- DarwinBoot \(drivers/DarwinBoot board fork\) fills /chosen/darwinboot-efi-map with the final UEFI memory map before ExitBootServices \(see the memory area\).
- DarwinBoot \(board fork\) appends the free conventional-memory runs of at least 64 MiB it sees before placing the window to the kernel command line as db-runs=&lt;start&gt;+&lt;bytes&gt;,... \(hex, up to eight\); the kernel prints them, so the real layout can size owned\_memory\_size without the NO WINDOW screen.
- The eMMC work adds no firmware component: the payload still boots through U-Boot with the same marker file.
- U-Boot's UEFI services are enough for UniXNU, DarwinBoot and XNU: no Mu-Silicium platform port is needed for this board.
- DarwinBoot's GIC-500 pre-configuration \(the iBoot role\) is what lets the kernel pass lockdown and start kexts on this SoC.
- The pre-configuration must not enable the EL1 virtual timer PPI early: on SDM710 that is INTID 19 and it fires before ArmCpu installs its handler.

### 完成条件

- U-Boot starts UniXNU from the FAT volume, the menu lists the xnu entry, and DarwinBoot hands control to the kernel with the device tree, framebuffer and command line.

### 当前范围

- The boot chain is U-Boot specific: it is not reproducible with the Mu-Silicium flow of the other ports and is not covered by ./unixnu firmware or ./unixnu bootimg.

### 下一步

- Keep the U-Boot side \(sirius-distro\) pinned by revision in the handoff document; it is the firmware for this port.

### 证据

- `source`: [Boot-chain diagram, the marker-file boot rule and the DarwinBoot GIC pre-configuration rationale.](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/docs/HANDOFF.zh-CN.md)

## CPU 与中断 {#cpu}

`implemented`

组件: `ArmCpu`.

### 硬件与依赖

- Eight Kryo 360 cores at Affinity1 0x000..0x700, boot CPU cpu0; cpu0-5 Cortex-A55, cpu6-7 Cortex-A75.
- GIC-500 distributor 0x17a00000/0x10000, redistributor 0x17a60000/0x100000, stride 0x20000.
- The EL1 virtual timer is GIC PPI 3 / INTID 19 \(Apple uses PPI 11 / INTID 27\); the SoC counter runs at 19.2 MHz.

### 配置

- dts/sirius.dts lists all eight cores in boot order with their compatible strings; the ADT carries the same order.
- The kernel command line selects the board behaviour: sheng-smp=1, cpus=8, armcpu-self-ipi=1, armcpu-timer-intid=19.
- drivers/ArmCpu/ArmCpu.cpp is the board copy of the component: it adds the non-Apple timer INTID, the /cpus probe counters and the sheng-smp claim path.

### 操作步骤

- Build the kernel, then read the boot-progress TOPO line to confirm the topology and the probe decision.

### 开发经验

- The eMMC bring-up does not touch the CPU selection or the ArmCpu driver; board.toml only gained an archive entry.
- The boot-progress TOPO row confirms the kernel topology on hardware: boot=0 max=7 nums=01234567.
- With sheng-smp=1 the native ArmCpu claims every /cpus nub; without it the kernelcache AppleARMCPU takes the nubs and panics with "CPU configuration in device tree is invalid" because it requires /cpus/max\_cpus.
- AppleARMCPU still wins the nubs at the current stage, which is the open IOKit blocker.

### 完成条件

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU with the board INTID.

### 当前范围

- IOKit attach of the native ArmCpu is not yet proven; the last trusted snapshot shows AppleARMCPU holding /cpus.

### 下一步

- Stop pre-enabling the timer PPI in DarwinBoot, re-read the probe row, and confirm ArmCpu installs its IRQ handler before the timer fires.

### 证据

- `source`: [Timer INTID measurement, the TOPO checkpoint and the AppleARMCPU panic analysis.](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/docs/HANDOFF.zh-CN.md)

## 内存与 DMA {#memory}

`implemented`

### 硬件与依赖

- Usable DRAM 0x17d6c0000 from 0x80000000 \(6 GiB model: 2 GiB then 0xfd6c0000 at 0x100000000\).
- The framebuffer handed over by U-Boot sits at 0x9c000000 \(1080x2240 splash\).

### 配置

- The DTS memory node is a single contiguous range and board.toml repeats the size as \[payload\] dram\_size; the driver refuses a mismatch.
- The ADT receives dram-base, dram-size and the CHRP NVRAM proxy from the payload step.

### 操作步骤

- Read the MEM row of the boot-progress panel and compare it with the DTS range.

### 开发经验

- The final UEFI memory map \(kernel 10cc072 / payload 3361ec2, docs/evidence/sirius-memory-20261029-efimap.log\): below the window only reserved firmware ranges and small free gaps; the window 0x9f87c000+0xaa000000 is type 1 \(loader code\); above it 0x14987c000+0x7b84000 free, then U-Boot's ranges: 0x1515ac000+0x1baa8000 boot-services data \(443 MiB\), 0x16d054000+0x105c000 and 0x16e0b1000+0xffcf000 boot-services code \(the second is about the 256 MiB payload volume\), runtime code from 0x17e080000. Boot-services memory is free after ExitBootServices, so DarwinBoot could extend the window over it if it copies its sources out first. The map ends near 0x17e2c0000: the about 2 GiB up to the configured end of DRAM \(0x1fd6c0000\) is not in U-Boot's map at all, so U-Boot's memory description has to be checked before that range can be used.
- To find what keeps the 2.7 GiB above 0x14e1e4000 out of the window, DarwinBoot now fills a zeroed /chosen/darwinboot-efi-map placeholder \(board.toml \[adt.chosen.bytes\], 32 x 24 bytes\) from the final UEFI memory map right after the last GetMap before ExitBootServices \(stack only, no allocation\): adjacent descriptors of one type merged, the 32 largest ranges kept in address order \(start, bytes, EFI type, descriptors merged\). NativeEmmc's memory report logs them as NEMMC efi-map lines \(first three reports\). The kernel command line \(883 + about 60 characters of XNU's 1024\) has no room for the map. Not run yet.
- With SpringBoard running in the 1 GiB window the phone is very laggy \(kernel 8a6e9fc / payload 5a5ba94: LOAD sys 69%, swap file creation fails at 50 s, compressor active\). \[payload.adt\] owned\_memory\_size is now 0xaa000000 \(2.66 GiB\), nearly all of the largest free run 0x9f800000+0xae9e7000 \(to 0x14e1e7000\), leaving about 70 MiB of it for DarwinBoot's later allocations. Of the 6 GiB model's 0x17d6c0000 bytes from 0x80000000, the firmware's reserved regions below 0x9f800000 stay unavailable to any OS, and the 2.7 GiB from 0x14e1e7000 to 0x1fd6c0000 is not free when DarwinBoot allocates the window \(what holds it is not known yet\); XNU takes one contiguous window.
- DarwinBoot's free runs on this unit \(kernel 130bf97, payload 216ef03\): 0x80000000+0x5700000, 0x97c00000+0x4400000 and 0x9f800000+0xae9e7000 \(2.73 GiB, crossing 4 GiB at 0x100000000\); the 1 GiB window sits at 0x9f87c000. A window up to about 2.7 GiB fits that run, with the part above 0x100000000 out of the eMMC's DMA reach.
- A window larger than 1 GiB is bounded by the eMMC's 32-bit ADMA2: the kernel image's static descriptor and single-block buffers and the run bounce buffer \(IOMalloc\) must stay below 4 GiB, and sirius\_emmc\_read\_blocks refuses a page above it; DarwinBoot takes the first free run that fits. The heartbeat now prints the window \(NEMMC window base/size\) and DarwinBoot's free runs \(NEMMC db-runs\) so the next size is chosen from the measured layout.
- The eMMC probe maps two register windows \(GCC and SDCC1\) and reads only; the payload memory map is unchanged.
- The single contiguous range is what DarwinBoot's window allocation and the ADT handoff require; the two physical banks are described as one range on purpose.

### 完成条件

- The kernel memory map accounts for every handoff region, and no DMA engine or framebuffer range overlaps the kernel window.

### 当前范围

- DMA and SMMU behaviour is untested: there is no storage or GPU driver yet.

### 下一步

- Capture the kernel's memory map row after the next IOKit break-through and reconcile it with the DTS.

### 证据

- `source`: [DRAM split, framebuffer address and the memory-map checkpoint.](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/docs/HANDOFF.zh-CN.md)

## 存储与根卷 {#storage}

`device-verified`

### 硬件与依赖

- The reference unit is eMMC, not UFS: the UFS transport and its sheng integration points do not apply to this board.
- The original kernelcache is the only source of IOStorageFamily's addresses; its kext images carry no symbol table, so they are derived from the dispatch table itself.

### 配置

- board.toml lists build-sirius-emmc.py \(the SDCC1 probe\) and build-native-emmc.py \(the IOKit block driver\) in \[kernel\] archives; CONFIG\_XNU\_NATIVE\_UFS stays off.
- \[userdata\] carries the 512-byte geometry and the OS/SystemOS windows read from the device's own GPT.

### 操作步骤

- Build the kernel with that archive list: the driver's storage imports are bound at the prelink slide and archived with it.
- Read the evidence off the boot-progress console: the probe prints the GPT rows, the driver logs the block count it publishes.

### 开发经验

- NativeEmmc's memory report also logs /chosen/darwinboot-efi-map as NEMMC efi-map lines \(see the memory area\).
- Read rate from the NEMMC alive blocks counter \(kernel f222029\): flat 30 MiB/s from 55 to 150 s \(the card's limit at 50 MHz 8-bit SDR, mostly the shared-cache verification\), 13-23 MiB/s to about 330 s, then under 2 MiB/s while the Apple logo stays up: the first five minutes are storage-bound, the rest is not. Linux runs this card in HS400; DDR52 \(controller clock twice the card clock, BUS\_WIDTH 6, UHS DDR50, no DLL or tuning below 100 MHz per sdhci-msm\) is the next rung that needs no tuning.
- The run bounce buffer comes from IOBufferMemoryDescriptor::inTaskWithPhysicalMask \(contiguous, mask 0xfffff000\) instead of IOMalloc, so it stays below 4 GiB where the 32-bit ADMA2 reaches when the window grows past 0x100000000.
- NativeEmmc's heartbeat also carries the display copy counters every fourth beat \(NEMMC fb copies, copy last/mean/max us, read last us, cache source/scanout/wimg\) and every sixteenth beat the clock of the core it runs on \(NEMMC cpu mpidr, NEMMC cpu MHz\), the cpufreq-hw state of both clusters, the memory layout \(NEMMC window base/size, NEMMC db-runs\) and the CPU load \(NEMMC load user/sys/idle %\), because past about 220 s the console has no other source for them; the storage path is unchanged. realhost is declared locally there: kern/host.h exposes it only to MACH\_KERNEL\_PRIVATE code and the IOKit recipe does not define that.
- The data path works: ADMA2 reads return EFI PART from LBA 1, the GPT header parses \(entries\_lba=2, count=84, size=128\) and 81 partitions with geometry are listed; boot 1179648..1310719, vendor 11010048..17301503, userdata 17301504..122142686.
- Five conditions had to hold at once: the RCG2 encoding \(CFG=0x2017, M=1, N=0xfc, D=0xfb\), 1.8 V I/O \(the board's vqmmc\), the 32-bit interrupt/error map at 0x30/0x32/0x36, the ADMA descriptor address at 0x58/0x5c rather than 0x00, and cache maintenance \(flush\_dcache64\) because the engine reads memory and not the CPU cache.
- SMMU is not the blocker: the boot chain leaves it disabled \(scr0=0x00230406, bit0=0\) and writing S2CR hung the SoC twice, so the driver only reads SMMU state.
- IOStorageFamily is a kext of the original kernelcache, so the archive form of the driver left IOBlockStorageDevice undefined at the kernel link \(ld: 'a missing vtable usually means the first non-inline virtual member function has no definition'\).
- The prelink slides every component by a constant: extents\[\].va = original + slide for each segment and bindings\[\] carries new\_site = site + slide, so the addresses the driver needs are the kernelcache's plus the slide.
- The dispatch table is identifiable without a live snapshot: of the 190 pinned slot names 176 are kernel exports, exactly one \_\_DATA\_CONST table matches all of them, the other 14 slots point at the kext's own BRK traps, the single constructor that stores table+16 forwards to the actual IOService constructor and the base destructor resolves to IOService's.
- Eleven imports are bound \(dispatch table, metaclass, protected constructor, base destructor and seven methods\); when the prelinked kernel exists the derivation also checks it holds the same constructor at the slid address, so a wrong slide cannot pass.
- The SHNGROOT manifest at userdata LBA 17301504 describes two windows \(OS 17303552+11870275, SystemOS 29175808+6451200\); publishing them as their own IOBlockStorageDevice makes APFS mount disk0, disk1s1 and disk2s1 \(the OS volume DawnUpdate21H461.J120J121J207J208OS\) and bsd\_init completes.
- A thread\_call has a single pending slot: thread\_call\_enter1 neither queues a second call nor preserves the first parameter, so passing requests there silently dropped completions and any caller waiting on such a request hung with the kernel otherwise idle. Requests now sit on a software queue that one drain services.
- Completing a block request from another thread deadlocks this stack the same way the drop did \(reads and blocks frozen at the same point, no error, the drain asleep\), so doAsyncReadWrite completes inline by default.
- The recurring 'Taking non-sleepable RW lock with preemption enabled' panic is the trust cache runtime lock, not a pmap lock: lock 0xfffffff007b3b548 resolves to \_trust\_cache\_rt\_lock and the first caller to \_query\_trust\_cache+0x70. trust\_cache\_runtime\_init\(\) is not compiled into this build, so the lock word reads all zeros \(lck\_rw\_can\_sleep == false\) and lck\_rw\_lock\_shared panics at lock\_rw.c:1400; the driver's heartbeat now mirrors the panic text into the USB ring, which is how the addresses were read.
- With the runtime guarded to answer KERN\_NOT\_FOUND, AMFI refuses every image and the kernel kills launchd with namespace 9 \(OS\_REASON\_EXEC\) code 8 \(EXEC\_EXIT\_REASON\_SECURITY\_POLICY\); recording and clearing that answer with sirius-skip-cs=1 makes exec\_activate\_image return 0, so execve of /sbin/launchd completes.
- The card clock can be raised from the identification rate with the same table U-Boot programs: the RCG divider field holds \(div \* 2 - 1\) and DUAL\_EDGE is set when n \!= m, so the 400 kHz entry \(CXO, div 12, m 1, n 4\) is CFG 0x2017 and 25 MHz \(GPLL0\_EVEN, div 6, m 1, n 2\) is CFG 0x260B; 25 MHz stays inside default speed, 50 MHz would need the CMD6 high-speed switch.
- With the original trust-cache bundle in the payload and the runtime initialised at startup, AMFI answers the exec policy itself: the boot prints execve activate 0 without the sirius-skip-cs bypass line, so the Apple-signed launchd is trusted rather than skipped into.
- The 25 MHz switch reads the GPT signature back at the new rate on device \(the probe prints EMMC clock25=ok\), so the RCG encoding above is confirmed rather than assumed.
- Throughput at the identification clock is about 550 blocks/s \(0x3FC to 0x84A in two seconds\), the expected ceiling for 400 kHz on a four-bit bus, so the 400 kHz setting is a speed problem and not the cause of the stalls.
- The init exec returns 0 and then nothing asks the driver for another block: reads stop at 0x10D \(269 requests, 0x98F blocks\) while the heartbeat keeps counting, so the wait is past the storage stack. The caller side is now instrumented \(sirius-post-exec-trace.patch\): the exec thread-switch state, every new user thread start at thread\_bootstrap\_return, the first pid 1 syscalls with their returns, each bsd\_ast for pid 1 and the first user faults after the exec, all written to the same USB ring and summarised by the heartbeat.
- The caller-side probe closes that question: the pid 1 thread stays in load\_init\_program\_at\_path, inside copyout\(\) of the launchd path, and takes 62.6 million faults in about a minute. The stall is a fault loop in the exec path, not a storage wait.
- That fault loop was PAN \(see the diagnostics area\). With CONFIG\_XNU\_NATIVE\_PAN=y and the driver no longer clearing PAN, all eight CPUs pass the copyout, the exec returns 0 and launchd issues its first syscalls, every one of them returning: 74, 372, 294, 20, 427, 381, 5, 90, 4 and 202. Syscall 294 \(shared\_region\_check\_np\) returns ENOMEM with 'vm\_shared\_region\_start\_address\(\) failed', i.e. dyld finds no shared cache mapped; afterwards the launchd thread waits and the read count stays at 0x113.
- The shared cache is in the SystemOS cryptex. Building the ARM64 series' owner SystemOS mount \(OWNER\_CACHE\_MOUNT, OWNER\_CACHE\_STARTUP, OWNER\_UNION\_SYSTEMOS, with BRINGUP\_OWNER\_CACHE as the uke port has it\) and answering its two block hooks from NativeEmmc \(sirius-allow-unverified=1\) mounts disk4s1 \(SystemCryptex, 8846FE78-2910-4297-AF97-D59BB6F8FC16\) as a union over / before launchd starts; dyld then opens the cache, fstats it and preads its header.
- Registering the cache's code signature \(fcntl, syscall 92\) then returned 85 \(EBADEXEC\): iPadOS signs code in 16 KiB pages, and this 4 KiB kernel only accepts that through native-4k-signature-hash-cache.patch, which the first-console configuration had off. With CONFIG\_XNU\_NATIVE\_CS\_HASH\_CACHE=y the call returns 0 after the kernel reads the whole cache once, and dyld maps it \(197 and 73 return 0\).
- The block driver ran at the 400 kHz identification clock all along: sirius\_emmc\_prepare\(\) reprogrammed it after the probe's 25 MHz switch, and every 512-byte block was its own CMD17 with five ring lines. On this 8-bit bus that is about 770 blocks/s, and the 2.81 GiB cache took two hours. Multi-block reads \(CMD18 with Auto-CMD12, 256 blocks per command through an ADMA2 table\) and a clock ladder proven against blocks read at 400 kHz bring it to 50 MHz: EXT\_CSD reports rev 8, width 2 \(8-bit\), HS\_TIMING 1 and DEVICE\_TYPE 0x57, runs pass with EIS 0, and the whole cache is read in about 104 s \(27 MiB/s on average, 30 MiB/s peak\).
- Past the shared cache launchd runs its boot tasks: mount \(pid 3\) exits with status 66 \(EX\_NOINPUT\) and the boot panics with 'mount\[3\] exited'. There is no Data volume yet, which is the mount it needs.
- NativeEmmc serves the Data seed itself instead of RamBlock: the payload's /chosen/memory-map/RAMDisk becomes a read-write RAM window named Data, and the driver answers the two RamBlock entry points kern\_exec.c calls once its seed path is compiled in, native\_ram\_block\_volume\_seed\(\) \(the Data volume on that window\) and native\_ram\_block\_gpu\_addon\(\) \(none on this board; the first link failed on it as an undefined symbol although its declaration is weak\). IOMaximumBlockCountRead is 2048 blocks now that transfers run in 256-block commands.
- Once userland read in parallel, APFS reported data hash mismatches on the sealed SystemOS volume \(disk6s1\). The block driver drains requests on their callers' threads through one shared bounce buffer, and released the transport lock between the read into it and the copy out of it, so a second reader could refill it first and the first request received the other one's blocks. The copy now happens under the lock \(the request's memory is wired for the I/O, so it cannot fault back into the driver\). Not yet booted.
- native\_ram\_block\_volume\_seed\(\) takes the one APFS volume on the RAM window instead of looking the kernel's UUID up, since a Data seed can only be there and every seed build has a new UUID; a differing UUID is reported, not refused, so a new seed no longer needs a new kernel.
- With the copy under the lock, a 256 MiB seed, sheng-disable-watchdogd=1 and sheng-lite=1, the boot runs without a panic for the whole capture \(heartbeat at 336 s\): no data hash mismatch is reported, the watchdog policy disables watchdogd, early boot completes at 170 s and only liveactivitiesd crashes. The Data volume then fills about a minute after early boot; containermanagerd \(first-boot data containers\), launchd, analyticsd and APFS itself hit ENOSPC.
- Persistent Data write path and fences: package/sirius\_emmc.c implements block writes via CMD24/CMD25 with Auto-CMD12 over ADMA2, polls CMD13 until the card exits programming state with error checking, and issues CMD6 FLUSH\_CACHE when EXT\_CSD CACHE\_CTRL is active. Writes are strictly fenced twice: once to the single window opened by sirius\_emmc\_set\_write\_window\(\), and globally to the userdata partition boundary minus its first MiB \(protecting the SHNGROOT manifest\).
- Persistent Data container window: package/NativeEmmc.cpp implements prepareDataWindow\(\), locating the first MiB boundary behind the root image \(userdata LBA 35627008\) and verifying the NXSB APFS superblock before publishing a read-write eMMC block device when sirius-data-write=1. Writes are drained through the software queue keeping the bounce buffer under the transport lock in both directions, doSynchronizeCache flushes the eMMC write cache, and native\_ram\_block\_volume\_seed\(\) resolves the Data volume on whichever window exists.
- scripts/make-data-window-image.py converts the grown 8 GiB APFS Data container into a fastboot sparse image for userdata: a DONT\_CARE chunk leaves the root image untouched, RAW chunks write nonzero blocks, and FILL chunks write zero blocks so free space reads as zero on device.
- Persistent Data volume verified on hardware: with sirius-data-write=1 and the 8 GiB container flashed via data-window.simg behind the root image, NativeEmmc opens the write window at LBA 35627008 \(16777216 blocks\), mounts disk3s1 \(OwnerData, 0C28586B-...\), early boot completes at 159.6 s, and APFS commits transactions up to xid 85 with 0 ENOSPC errors across the entire capture.

### 完成条件

- The eMMC registers, GPT and the SHNGROOT windows are correct; APFS mounts the OS volume, bsd\_init completes, init execs /sbin/launchd and execve returns 0.

### 当前范围

- Writes are strictly fenced to the persistent Data window on userdata \(LBA 35627008, 8 GiB\); the rest of the card remains read-only.
- The card runs at 50 MHz in high-speed SDR on 8 bits \(about 30 MiB/s\). It supports DDR52 and HS200 \(DEVICE\_TYPE 0x57\), but DDR needs the host's DDR mode and HS200 needs tuning, and neither is implemented; 100 MHz is only tried when the boot chain already left HS200 timing.
- The SystemOS volume is authorized by a bring-up boot argument \(sirius-allow-unverified=1\), not by an owner root policy.
- The exec policy no longer needs a boot argument: the payload carries the original trust-cache bundle and the kernel initialises its runtime at startup. The sirius-skip-cs bypass is kept in the patch series, unused, in case a future image falls outside the bundle.

### 下一步

- Display driver: U-Boot leaves a 1080x2240 splash framebuffer at 0x9c000000; bind GopFramebuffer or NativeLegacyDisplay to get screen output past SpringBoard.
- Touch driver: Synaptics S3706 adapter from the fajita reference.
- Keep the trust-cache bundle in step with the OS build when the IPSW changes \(its sha256 is pinned in board.toml \[payload\] trust\_cache\_sha256\).
- Raise the pid 1 syscall log beyond 24 entries and mirror launchd's stderr writes into the USB ring, so later boot-task failures name their call and message.
- For more storage speed: DDR52 \(8-bit DDR at 52 MHz, no tuning\) roughly doubles the rate; HS200 needs the msm tuning sequence.

### 证据

- `device`: [kernel.macho 66d0319c718f6faf894d1d713759b5d82d8da010c3bd2ad2c2c13bd195574a88, payload c0d2e62c0738d6c851eeeebccf0236a310bcd14194df0ea1735efaef647420e6: EMMC write window opened at LBA 35627008 \(16777216 blocks, 8 GiB\), NativeEmmc discovers NXSB container and mounts persistent Data volume disk3s1 \(OwnerData, 0C28586B-...\), early boot complete at 159.6 s, APFS transactions commit through xid 85 with 0 ENOSPC errors up to 280 s.](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/docs/evidence/sirius-usb-console-20261028-pdata.log)
  Command: <code>fastboot -S 512M flash userdata data-window.simg; fastboot flash vendor payload-M-pdata.img; fastboot reboot; python scripts/capture-usb-console.py --follow --wait 120 --duration 280 --match 'NEMMC PANIC TEXT END' --idle-stop 20</code>. Revision: `e73a8ecda8998ec36573c5bd2a9d7b6389305b2d`.
- `device`: [NativeEmmc starts from bsd\_init, publishes 0x747BFDF blocks of 512 bytes, and IOStorageFamily reads block 0, block 1 and block 2 with 21 sectors \(the 84 GPT entries\) through doAsyncReadWrite; the heartbeat keeps ticking with the transfer count fixed at seven, so the boot ends at the root-device wait. Log in docs/HANDOFF.zh-CN.md.](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/docs/HANDOFF.zh-CN.md)
  Command: <code>fastboot flash vendor sirius-obs.img; fastboot reboot; capture-usb-console.py --duration 240</code>. Revision: `d867b1d6498dc4d0f4ae4e18060762dcae6c5847`.
- `host`: [The kernel links with NativeEmmc in the image \(kernel.macho sha256 372820eb1b2cd9ecee15d769d1296771d0c8141c2681626d54651a62473446b8\); the GitHub macOS runner builds the same archive \(kernel workflow run 40386710258\).](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/docs/HANDOFF.zh-CN.md)
  Command: <code>./scripts/xnu-container.sh run bash -lc './unixnu build kernel --skip-setup -D ../sirius'</code>. Revision: `a47f0d6b4615c3cdebf92102400a1bc302eb6d73`.
- `device`: [APFS mounts disk0/disk1s1/disk2s1, bsd\_init completes, execve of /sbin/launchd prints activate enter, namei 0, 'exec policy answered 1, skipped by boot arg' and finally 'execve activate 0'; the driver then has no transfer in flight and the read count stops at 0x10D, so the remaining wait is past storage.](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/docs/HANDOFF.zh-CN.md)
  Command: <code>fastboot flash vendor sirius-if.img; fastboot reboot; capture-usb-console.py --duration 220</code>. Revision: `bb812428dccd1f676455813ad198ed2bee4a8e3e`.
- `device`: [kernel.macho 6f0d59b13e4ac3861c902962df8043c3bccac959cffcd859c5f965f697194d17, payload 00c8f4d7feba7982c1fcdcb2f072121d6b7a227fc38ebc0edd229bbd00b5bb08, eight CPUs: PAN reads 4194304, init path copyout 0, execve activate 0, two user thread starts, then launchd syscalls 74 372 294 20 427 381 5 90 4 202 all return; 294 returns 12 with 'vm\_shared\_region\_start\_address\(\) failed' and reads stay at 0x113.](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/docs/evidence/sirius-usb-console-20261027-pan.log)
  Command: <code>fastboot flash vendor payload-E-pan-noclear.img; fastboot reboot; python scripts/capture-usb-console.py --follow --wait 180 --duration 420</code>. Revision: `b1a11c4f4eb0bfd28b2dd3dfc59b3c7e3a3e742f`.
- `device`: [kernel.macho 5d045f1a6d6ddad44331a7e6ea8b1cc74a8c84058916287a83603ab912a66038, payload 6b6c562c1e8c91eb2c776fc6ef5f58227fd9eb000872ddb6e2fff6844886515a: NEMMC owner volume /dev/disk4s1, disk4s1 \(SystemCryptex, 8846FE78-...\) mount-complete before launchd; dyld opens, fstats and preads the cache, then fcntl \(92\) returns 85.](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/docs/evidence/sirius-usb-console-20261027-systemos.log)
  Command: <code>fastboot flash vendor payload-F-systemos.img; fastboot reboot; python scripts/capture-usb-console.py --follow --wait 180 --duration 420</code>. Revision: `24f6094010c728ecfdf3e3bbacd0effaeec60fb5`.
- `device`: [kernel.macho a10c51aa4fab72faf86912e1ca6736c0d068432ceff1b233f47948197848b8c4, payload 8402424eb1d9d4126cfe19ab2eb3742aad40d7ba5149267534ae94a7e745c2ce: fcntl \(92\) no longer fails and stays in the kernel's whole-file hash check, reading about 770 blocks/s \(400 kHz on 8 bits\) with the pid 1 fault count flat.](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/docs/evidence/sirius-usb-console-20261027-systemos.log)
  Command: <code>fastboot flash vendor payload-G-cshash.img; fastboot reboot; python scripts/capture-usb-console.py --follow --wait 180 --duration 1800</code>. Revision: `86fe9ffbc700915e006fce11474b0d277f0d7dc3`.
- `device`: [kernel.macho 3452714ae8b3ef3b775bed9cde5f93c11fc2d147e0375eec22430fb0dcf70999, payload 24118c6275d90fba6dd3e684353d4525640c7d627042092868a413609686f110: ext\_csd rev 8 width 2 timing 1 type 0x57, multi=ok eis 0, 25 and 50 MHz ok; 5898655 blocks \(2.81 GiB\) in about 104 s; fcntl 92, mmap 197 and munmap 73 return 0, then 'mount\[3\] exited ... exit status 66' panics the boot.](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/docs/evidence/sirius-usb-console-20261027-fast-emmc.log)
  Command: <code>fastboot flash vendor payload-H-fast.img; fastboot reboot; python scripts/capture-usb-console.py --follow --wait 180 --duration 900</code>. Revision: `1163990229f446753ef006126e55922aa23bda6a`.
- `device`: [kernel.macho 2e6e1ddc51b1f8b2d58c607477f81b0327d95f301382d8d4c1180096b402408a, payload 2bd98aa417ab6007b8c95c2071f4907dee5b4afcd09ac3899604e73dc9d21bff: NEMMC data seed at 0xa3cc1000 \(33554432 bytes\), Data volume disk3s1 \(OwnerData, EB6CBBA0-...\) mount-complete before launchd, shared cache verified; at 157.7 s mount \(pid 3\) exits 66 after 'DT\_get\_fstab\_entries: failed to get filesystem entry at: /filesystems/fstab'.](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/docs/evidence/sirius-usb-console-20261028-data.log)
  Command: <code>fastboot flash vendor payload-I-data.img; fastboot reboot; python scripts/capture-usb-console.py --follow --wait 120 --duration 280 --match 'NEMMC PANIC TEXT END' --idle-stop 20</code>. Revision: `33509e84db86517ff9bf349408dc66ab39c43d18`.
- `device`: [kernel.macho 2e6e1ddc51b1f8b2d58c607477f81b0327d95f301382d8d4c1180096b402408a, payload aa917c707d2f0a8f46ae44e635b838e7e3892822c115c0233bdb5bd3e2bae323: launchd runs every boot task through mount-phase-2 and logs 'Early boot complete' at 161.5 s; driverkitd, MobileGestaltHelper, mobileassetd and SpringBoard start; the Data volume reaches ENOSPC at 175.6 s, APFS reports three data hash mismatches on disk6s1, and watchdogd's brk \#1 exit panics the boot at 191.9 s.](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/docs/evidence/sirius-usb-console-20261028-early-boot.log)
  Command: <code>fastboot flash vendor payload-J-bmh.img; fastboot reboot; python scripts/capture-usb-console.py --follow --wait 120 --duration 280 --match 'NEMMC PANIC TEXT END' --idle-stop 20</code>. Revision: `09096e3738c618bb18a51af50cdfbc7f6431aa59`.
- `device`: [kernel.macho dd22531c552b5e87208268f3faf793b7acd2516961d45f44e82d3e15b9d86e8c, payload f93d3f9b72b45bb4a4248bd7637e0e8d616472eb28da2d4d5cf479c3574f36b6: seed of 268435456 bytes at 0xa3cc1000, Data volume disk3s1, watchdogd policy applied, early boot complete at 170 s, no hash mismatch, no panic up to 336 s; ENOSPC on disk3s1 from 230 s.](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/docs/evidence/sirius-usb-console-20261028-data256.log)
  Command: <code>fastboot flash vendor payload-L-data256.img; fastboot reboot; python scripts/capture-usb-console.py --follow --wait 120 --duration 280 --match 'NEMMC PANIC TEXT END' --idle-stop 20</code>. Revision: `396fdab90dc5b94a830e5a43e5a9084313796683`.
- `source`: [SDCC1 bring-up, the ADMA2 read path and the GPT parse.](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/package/sirius_emmc.c)

## 显示 {#display}

`implemented`

组件: `GopFramebuffer`.

### 硬件与依赖

- U-Boot hands over a 1080x2240 splash framebuffer at 0x9c000000 through GOP \(vidconsole\).
- The panel is 1080x2244 DSI; there is no backlight or display driver in the kernel yet.
- GopFramebuffer driver subclasses IOMobileFramebufferLegacy with GOP backend mapped at 0x9c000000.

### 配置

- drivers/GopFramebuffer is a board fork of GopFramebuffer at 33e941a878dcf01b98dbd9160d798bd56e7551ea \(the whole component: the tree links drivers/&lt;ID&gt; in place of the catalog checkout\). Its only change: sirius-fb-wc=1 maps the scanout write-combined instead of uncached in NativeLegacyDisplay.cpp; without the argument it behaves as the catalog revision.
- CONFIG\_XNU\_BOOT\_PROGRESS=y links the boot-progress layer; boot-progress=2 on the command line draws the kernel console lines.
- package/Font.h is vendored from Mu-Silicium, so the archive builds without a UEFI checkout.
- CONFIG\_XNU\_NATIVE\_LEGACY\_DISPLAY=y links libNativeLegacyDisplay.late.a built via scripts/build-native-legacy-display.py.
- board.toml enables offline-legacy-register=1, offline-legacy-gop=1, offline-legacy-unit-scale=2, offline-legacy-pm=1, offline-legacy-phase=4, and artwork-display-gamut=sRGB.

### 操作步骤

- Build kernel, payload and volume, boot, and read the panel: stage lines, TOPO, PROBE, MEM and panic text.

### 开发经验

- LegacyDisplayProbe.cpp defines sirius\_gpu\_dma\_alloc\(\) for package/sirius\_gpu.c phase 2: a physically contiguous IOBufferMemoryDescriptor below 4 GiB \(the NativeEmmc bounce pattern\), kept for the boot; native\_legacy\_display\_late\_probe still starts the GPU probe \(sirius-gpu=2 now\).
- The live banner \(package/BootProgress.c crash\_banner\) has a TOUCH row after UFS; the work-interval log keeps two rows instead of three so the banner still fits.
- build-native-legacy-display.py also compiles package/SiriusHidProbe.cpp and links build/sheng-hid-input/NativeHidInput.late.o and hid-original-bindings.o into the late display archive; native\_legacy\_display\_late\_probe calls sirius\_hid\_touch\_start\(\) \(see the input area\).
- native\_legacy\_display\_late\_probe also calls sirius\_gpu\_start\(\) \(package/sirius\_gpu.c, sirius-gpu=1; see the gpu area\).
- native\_legacy\_display\_late\_probe also calls sirius\_touch\_start\(\) \(package/sirius\_touch.c, sirius-touch=1; see the input area\).
- With the CoreUI fixup the panel shows crashes=0 at 335 s \(iconservicesagent no longer dies\) and the migration progress bar at about half; console: every load of dyld\_shared\_cache\_arm64.11 logs text-fixup +0x34f3b84 \(8 bytes\) applied.
- iconservicesagent's crash is CI::GLContext::init+220 calling blr x8 with x8 from the GL dispatch table that GetMacroContext left zeroed \(no OpenGL ES driver\), reached from +\[CUIShapeEffectStack sharedCIContext\] = \[CIContext contextWithOptions:\[CUIShapeEffectStack preferredCIContextOptions\]\]. CoreImage has no environment switch to a CPU renderer \(its CI\_\* strings checked\). board.toml \[payload\] text\_fixups patches that bl \(dyld\_shared\_cache\_arm64.11 file offset 0x34f3b84, unslid 0x1a31d7b84\) to mov x0, xzr: -\[\_CUIGraphicVariantVectorGlyph \_createGraphicVariantImageAtScale:\] then returns the NULL of \[nil createCGImage:fromRect:\] and -\[IFSymbol imageForGraphicSymbolDescriptor:\] branches on it \(cbz x26\), so the symbol draws empty.
- Kernel afdb4b1 / payload e167d8c \(commit 05f5aa8\), photo at t=345 s: the panel stays readable above the Apple logo; FB 65 swaps/s, copy mean 9.7 ms, max 15.6 ms; LOAD user 0%, sys 13%, idle 85%; storage idle. The boot is not CPU-, storage- or copy-bound: it waits. An earlier photo at t=3500 s showed the progress bar full and then 0 swaps/s at 99% idle. The bar is iOS's data migration \(DataMigrator; its done marker is LastSystemVersion in /var/mobile/Library/Preferences/com.apple.DataMigration.plist, and it kills a plugin after a watchdog timeout\): the panel shows com.apple.migrationpluginwrapper ended by signal 9 \(exit-reason namespace 2\).
- package/BootProgress.c publishes the live panel's first row \(boot\_progress\_panel\_top\) and the GopFramebuffer fork copies frames only above it, so the panel stays readable between repaints instead of flashing under 16 frames/s of full-frame copies.
- With sirius-fb-cached=1 \(kernel f222029, payload 952ab40, commit 01d06b4c7826c80fde7c4c2562b153188267b641\) the copy drops from 182 ms to 9.3 ms mean over the first 211 frames and 13.7 ms over 9276 frames in about 560 s \(about 16 frames/s\), and the source page reads VM\_WIMG 0x2 \(copyback\) after the cacheable mapping \(docs/evidence/sirius-usb-console-20261028-cached.log\). The panel now shows only briefly: each full-frame copy overwrites it and it repaints every few seconds.
- The source surface is write-combined \(VM\_WIMG 0x6 on its first page\) and the copy stays at 182 ms mean with the write-combined scanout \(kernel 130bf97\), so the source loads set the cost. sirius-fb-cached=1 maps the source with kIOMapCopybackCache and runs flush\_dcache64 \(clean and invalidate to PoC\) over it before the content scan and the copy; NEMMC fb cache ... wimg shows the page attribute after that mapping.
- With sirius-fb-wc=1 the screen looked the same and the console cannot show the copy time, so the board fork now times a read-only pass over the source \(the content scan of the first 32 frames\) and records the cache mode of both mappings and the source page's pmap attribute: a slow read pass with a copy of the same order means the uncached source, not the scanout stores, sets the cost.
- With the keystore stand-in iOS presented 14954 frames by t=3500 s, every one a full 9450 KiB CPU copy at a mean of 201.7 ms \(max 209.6 ms\) into the uncached scanout, about 47 MB/s: the copy ran nearly the whole time the Apple logo and progress bar were up \(docs/evidence/sirius-panel-20261028-keystore.log\).
- The late display probe calls native\_keystore\_probe\(\) first, and the late archive carries KeyStoreProbe.o and NativeKeyStoreEvents.late.o, whose static constructor is removed and run by the probe between preModLoad and postModLoad.
- The panel gained an EMMC row \(step, version, capabilities, state, clock, power, clock-branch halts\) next to the USB row, so the storage bring-up is visible without a serial link.
- The USB row \(drawn by this panel\) labels its six values after what they now carry - step, txev, rxev, chars, echo, poll - because they were first wired to register names and had drifted.
- The panel is the readable kernel log of this port: it renders the console, the TOPO/PROBE rows and panic\(\) output.
- Since the panic snapshot patch the panel re-renders at panic time, so the rows are not a stale frame.
- NativeLegacyDisplay and NativeGOPPresenter compile as a late archive \(libNativeLegacyDisplay.late.a\) via scripts/build-native-legacy-display.py, stripping static constructors from \_\_DATA,\_\_mod\_init\_func and globalizing them so the board display probe in LegacyDisplayProbe.cpp runs them safely after prelinked kexts have been admitted.
- The archive build script filters out C++ language and standard flags \(-std=gnu++2b, -fapple-kext, -nostdinc++\) when compiling C source units such as LegacyDisplayStubs.c.
- The audited ABI data for iOS 17.7.11 21H461 is stored in scripts/data/mobile-graphics-legacy-abi.json, allowing build-native-legacy-display.py to bind all \~170 inherited virtual methods in original-bindings.S without needing the raw kernelcache during CI.
- Audit against the 21H461 kernelcache proved the exact 13 dispatch table / constructor / method targets for IOMobileFramebufferLegacy and its 358-entry vtable with 9 abstract leaves.
- The GOP framebuffer nub publishes under /arm-io as display-subsystem in phase 4, registering power management and publishing the display service so SpringBoard stops crash-looping.

### 完成条件

- A known frame appears with correct geometry, and the kernel console and panic output stay readable on the panel.

### 当前范围

- IOMobileFramebufferLegacy scans out nothing of its own: it wraps the U-Boot GOP framebuffer, with no backlight, no modesetting and no DSI panel control.
- Frames reach the GOP buffer but are black: the on-screen panel counts 8 swaps accepted and 6 full frames \(9450 KiB\) copied by the CPU, with no GPU offers, so nothing renders content into the surfaces backboardd presents.
- The CPU copy takes 180-190 ms per full frame, which caps presentation at about 5 frames per second.

### 下一步

- Find why the presented frames are black: with no Adreno GPU driver CoreAnimation gets no GPU work done \(gpu offers=0\); check whether backboardd can fall back to software rendering or needs a GPU, and whether the default\_fb\_surface miss at 224.9 s matters.

### 证据

- `device`: [kernel.macho 8f831f8ff72e49470a26483ae9337f7dd66c74f77a09bc9fc47cc1a0da0a91d3, payload 51c18b0a22c619de9359b29b39ab5af22be4f9532d65341365f3f83e1699bb42: IOMobileFramebufferLegacy starts and registers the GOP display \(1080x2240 at 0x9c000000, rowBytes 4320\) at 51.1 s, a client opens IOMobileFramebufferUserClient with display type 0 at 189.2 s, display power goes to state 1 at 221.5 s and 0 at 260.5 s, 'default\_fb\_surface: No Default FB Surface found' at 224.9 s; no crashed, corpse, panic or ENOSPC line up to 280 s \(SpringBoard crashed at 202.8 s on the previous run\).](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/docs/evidence/sirius-usb-console-20261028-display.log)
  Command: <code>fastboot flash vendor payload-N-display.img; fastboot reboot; python scripts/capture-usb-console.py --follow --wait 120 --duration 280 --match 'NEMMC PANIC TEXT END' --idle-stop 20</code>. Revision: `076f63cee39bdb4ab11b4f85f6ffff15427ed948`.
- `device`: [kernel.macho 3698df4257565c676b3827e0448058d85745da61533a6ac9aac7f33aa3531395, payload 5bd4510a40955a44dd5c0314c9b45313bd4c77432438a40e18f7bcd3bb0258d7 \(sirius-fb-wc=1\): same path as before \(display at 53.6 s, early boot complete at 163.2 s, display client at 178.3 s, power state 1 at 210.5 s, default\_fb\_surface miss at 214.1 s, not\_in\_kdp text at 215.5 s\); the heartbeat runs through all four windows \(beats 0x71 to 0x216\) with only 547 eMMC reads after the first window; no crash and no DISPLAY COPY FAILED. The copy time is read from the panel, not the console.](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/docs/evidence/sirius-usb-console-20261028-fbwc.log)
  Command: <code>fastboot flash vendor payload-P-fbwc.img; fastboot reboot; four python scripts/capture-usb-console.py --follow --duration 280 --idle-stop 20 windows in a row, without --match</code>. Revision: `79c63f63bcdd2223791ed4e499b1668deeb9c20e`.
- `device`: [kernel.macho 1a8a1511ad225f51760442fd657596218406c87e6b9c5d43929f33d2c8449b99, payload 6b03df13c9036952722a51f1bf1fe06691508dcea0daeda90e27082b3c15ab4c: at t=3500 s iOS shows its Apple logo and progress bar; SWAP calls=14954 accepted=14954, FB total=14954 full copies at 201.7 ms mean \(max 209.6 ms\), swaps/s=0 and 99% idle at the photo; no crash, 11 exits \(xpcproxy exit 78, two UARPUpdaterService daemons killed with signal 9\).](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/docs/evidence/sirius-panel-20261028-keystore.log)
  Command: <code>fastboot flash vendor payload-O-keystore.img; fastboot reboot; photograph the on-screen live diagnostics panel</code>. Revision: `f5b179d6bf746cf80028cd222823a048f8d6e905`.
- `device`: [kernel.macho 8f831f8ff72e49470a26483ae9337f7dd66c74f77a09bc9fc47cc1a0da0a91d3, payload 51c18b0a22c619de9359b29b39ab5af22be4f9532d65341365f3f83e1699bb42: at t=1470 s, no panic; SWAP calls=8 accepted=8 rejected=0, gpu offers=0; FB total=6 copies of 9450 KiB at 177-190 ms each, swaps/s=0; the screen above the panel is black; liveactivitiesd crashed with SIGTRAP at PC 0x1ca09a4f8 \(17 crashes, 32 exits\), xpcproxy exited 78; backboardd \(pid 56\) creates work intervals without error; load 99% idle.](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/docs/evidence/sirius-panel-20261028-display.log)
  Command: <code>fastboot flash vendor payload-N-display.img; fastboot reboot; photograph the on-screen live diagnostics panel</code>. Revision: `076f63cee39bdb4ab11b4f85f6ffff15427ed948`.
- `source`: [Boot-progress panel behaviour, the panic snapshot fix and the geometry of the U-Boot framebuffer.](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/docs/HANDOFF.zh-CN.md)

## 输入 {#input}

`device-verified`

组件: `ShengHidInput`, `ShengNovatekTouch`, `QcomGeniSpi`.

### 硬件与依赖

- The board has no Home button; volume keys are reported by the button node of the ADT.
- 57UU/linux-sirius \(feat/sirius-7.2, sdm710-xiaomi-sirius.dts\): the touch controller is an ST FTS521 \(st,fts521\) at I2C 0x49 on i2c9 = QUP1 SE1 at 0xa84000 \(GCC\_QUPV3\_WRAP1\_S1\_CLK, SPI 354, SDA/SCL gpio6/gpio7 function qup9\), interrupt gpio125 active low, reset gpio99, vdd = tp\_vddio\_vreg \(gpio26, regulator-boot-on\), avdd = PM660L LDO6 \(vreg\_l6b\_3p3, RPMh\); touchscreen-size 1080 x 2244, keys 158/139. Not the Synaptics S3706 the earlier notes assumed.

### 配置

- board.toml writes \[adt.buttons\] with hold, voldown, volup and home-button-type = 2.

### 操作步骤

- Follow the input guide once a touch controller is known, then select an implementation.

### 开发经验

- Confirmed on the phone \(kernel 67b65eb / payload 1611d2a\): Setup reacts to touch. The touch path is the FTS521 driver \(package/sirius\_touch.c\) feeding ShengHidInput's combined keyboard+touch device \(package/SiriusHidProbe.cpp, sirius-touch-hid=1, sheng-touch-hid=1\), taken by the in-kernel IOHIDEventDriver with dk=0.
- Kernel 67b65eb \(commit fb84613\) / payload 1611d2a, combined device, dk=0 \(docs/evidence/sirius-touch-hid-20261029-combined.log\): the in-kernel IOHIDEventDriver attaches and is published as the built-in touch screen; the chip reads 31072 down/up transitions. At 328 s about twenty daemons exit cleanly and restart \(languageassetd starts\), and at 345 s SpringBoard and every process it hosts \(Setup, PosterBoard, the poster and widget extensions\) exit with signal 9, exit-reason namespace 10 \(SpringBoard\) and code 0x5bc1ea44; SpringBoard starts again at once and Setup at 376 s, after which the system stays quiet to the end of the capture \(about 860 s\). That sequence looks like Setup applying a choice made by touch \(likely the language\), not yet confirmed from the screen.
- Kernel b5a62b2 \(commit 96cfbd3\) / payload 7656d0e, dk=0 \(docs/evidence/sirius-touch-hid-20261029-dk0.log; the console stayed up for all four windows\): the touch-only device starts but no event driver attaches below it in about 20 minutes. This kernelcache's in-kernel IOHIDEventDriver has no digitizer personality \(game-controller pointers 1/5 and 1/4, Peppy display 0xc/1, buttons 0xb/1, keyboards 1/6 and 1/7, sensor 0xff0c/3\), so a Digitizer/Touch Screen device is only matched by the DriverKit AppleUserHIDEventService. SiriusHidProbe.cpp therefore publishes sheng's default combined device \(native\_hid\_input\_allocate with sheng-touch-hid=1: keyboard collection first, then the touch screen\), whose keyboard usage matches HID Keyboard Driver; native\_hid\_live\_checkpoint then publishes Digitizer/Touch Screen as the primary usage on the event service for backboardd. sirius-touch-hid=2 keeps the touch-only device.
- Kernel 985facb / payload 8e16490 \(dk=0, commit 75efc08\): no DK lines any more and the touch screen device starts, but touches still have no effect on Setup \(panel photo at t=330 s\); the USB console stopped at about 170 s, before Setup, so whether the in-kernel IOHIDEventDriver attached and whether reports reached it is not known. The live banner now carries a TOUCH row: chip stage, FTS events read, contacts begun, I2C errors, the iOS device stage, the class of the event driver attached below it \(or none\) and the touch reports handed to it with the last handleReport result.
- Kernel 985facb \(commit bd74e96\) / payload d7f5ce4 \(docs/evidence/sirius-touch-hid-20261029.log\): the touch screen device starts on IOHIDResource \(metaclass status 0\) and the FTS521 driver reads 3240 down/up transitions, but Setup does not react. The event driver that matched is the DriverKit AppleUserHIDEventService: "DK: AppleUserHIDEventDriver-0x100000249 waiting for server com.apple.driverkit.AppleUserHIDDrivers-100000249", then "user server timeout"; driverkitd is exec'd at 142 s but no AppleUserHIDDrivers process is ever exec'd, so no IOHIDEvent leaves the kernel. kernel\_args now pass dk=0 \(XNU gIODKDebug, IOUserServer.cpp: without kIODKEnable no dext personality matches, IOService.cpp:3910\), so the in-kernel IOHIDEventDriver that SiriusHidProbe.cpp loads matches instead. Cost: no DriverKit driver can run while it is set; none other is needed on this board yet, and why the dext is not launched is still open.
- CI run 40834974797 \(commit 34ee775\) built the ShengHidInput objects but the final kernel link failed on one undefined symbol, \_native\_buttons\_set\_sink: NativeHidInput declares it weak\_import, which a static kernel link still requires to be defined \(sheng's button driver defines it\). package/SiriusHidProbe.cpp now defines it as a no-op; this board has no button driver yet.
- ShengHidInput brings its catalog dependencies ShengNovatekTouch and QcomGeniSpi into the tree; both are source-only \(no build recipe, no outputs\), nothing of theirs is compiled or linked, and the record lists them in this area.
- The touches reach no iOS process: Setup stays on its hello page however often the screen is swiped \(kernel 86b616b / payload f2ba289\), because no IOHIDDevice exists. board.toml now selects ShengHidInput and package/SiriusHidProbe.cpp \(sirius-touch-hid=1, from native\_legacy\_display\_late\_probe\) publishes its touch-only NativeHidInput: IOHIDFamily and IOHIDEventDriver loaded, IOHIDResource awaited \(10 s\), the class registered between preModLoad and postModLoad, then init/attach/start on IOHIDResource; native\_hid\_live\_checkpoint publishes Built-In, DisplayIntegrated, PrimaryUsagePage 0x0d and PrimaryUsage 4 on the IOHIDEventDriver and its interface, as UniXNU-sheng package/HidInputProbe.cpp does for backboardd. The contacts are the FTS521 driver's native\_touch\_\* in ShengHidInput's 30480 x 20320 units \(exact for 1080 x 2244\). UniXNU's recipe needs a sheng-only prelinked reference candidate, so scripts/build-sheng-hid-input.py replaces it: it binds against scripts/data/hid-device-abi.json, the original 207-slot IOHIDDevice vtable read from this board's kernel 86b616b after the recipe's own checks passed against it \(constructor bytes, the 18 IOService overrides, pure slot 180, handleStart; handleReport at slot 181 = 0xfffffff004add0c4\), and requires the compiled overrides to be exactly \[0,1,7,14,86,87,111,171,173,180\]. Not built or run yet.
- Kernel 26ed024 \(commit e02fa17\) / payload 3f16296 \(docs/evidence/sirius-touch-gpu-20261029-probe2.log\): the touch controller works. cmd-db ldob6 = 0x41b00; RSC drv-2 id 0x00010100 \(version 1.1, the 2.7 register layout\), TCS 0 idle; the LDO6 request completed in 1 ms with CMD\_STATUS 0x00010101 on all three commands; after the power cycle the chip reports CONTROLLER\_READY with no bus error, chip id 36 39 \(FTM5\), firmware 0x5400; sensing on, and touches arrive as enter/motion/leave events with x 0..1080, y 0..2244 \(673 down/up lines in the first window\). iOS does not react yet: no IOHIDDevice is published.
- Second probe, after a review against Linux \(not run yet\): the analog rail is voted on through RPMh \(cmd-db "ldob6" lookup with zero-padded 8-byte ids, VRM slave id 4 = CMD\_DB\_HW\_VRM; apps RSC drv-2 at 0x179e0000, the first ACTIVE TCS at +0xd00, voltage 3300 mV, mode 7 \(PMIC4 LDO HPM\), enable, each with a response requested, completion polled on IRQ\_STATUS bit 0, command-enable mask written exactly, per rpmh-rsc.c ver 2.7/3.0 offsets\), in fts\_chip\_powercycle\(\) order \(reset low, vdd, 1 ms, avdd, 5 + 10 ms, reset high\); the chip reset is the gpio toggle \(fts\_system\_reset with a reset gpio\), followed by pollForEvent\(EVT\_ID\_CONTROLLER\_READY\) for up to 1 s before the chip id read. Also: 5 broken string literals from a scripted edit were found by re-reading and fixed; both C files pass clang -fsyntax-only -Wall -Wextra.
- Kernel 66d1272 \(commit 10f440b\) / payload 7995ea8, at 77 s \(docs/evidence/sirius-touch-20261028-probe1.log\): the QUP1 clocks run after the vote \(m\_ahb, s\_ahb, s1 CBCR CLK\_OFF clear, vote 0x45b00000\), the SE1 RCG already selects XO \(cfg 0x00100000\), QUP1 hw\_ver 0x10010000, SE1 runs I2C firmware \(proto 3\) with FIFO mode and a 16-word TX FIFO; the chip acks 0x49 \(no NACK on any transfer\) but every read returns zeros and the reset never reports ready, while gpio125 stays low \(events pending\). The FIFO packing was LSB-first; i2c-qcom-geni.c packs MSB-first \(geni\_se\_config\_packing\(..., true, true, true\)\), so every byte reached the chip bit-reversed. Fixed: TX/RX packing 0x0007f8fe/0x000ffefe, and the RX FIFO is drained after CMD\_DONE.
- package/sirius\_touch.c \(sirius-touch=1, started from native\_legacy\_display\_late\_probe\): votes the QUP1 M/S AHB and SE1 clocks \(GCC 0x5200c bits 20/21/23\), checks their CBCRs before any SE access, sets the SE1 RCG to XO, programs FIFO-mode GENI I2C at 400 kHz \(Linux geni\_i2c\_clk\_map\_19p2mhz: divider 2, 5/11/22\), sets the pins, drives gpio26 high, pulses reset on gpio99, reads the FTM5 chip id \(0xfa 0x20000000, expected 0x36 0x39\), resets the chip \(0x80 to 0x20000024, waits for event 0x03\), turns sensing on \(0xa0 0x00 0x01\) and polls the event FIFO \(0x86, 8-byte events: enter 0x13, motion 0x23, leave 0x33\). Contacts go out as TOUCH console lines and through native\_touch\_\* \(the board side of ShengHidInput, in its 30480 x 20320 units\). Not run on hardware yet.
- The SDCC1 probe does not touch the ADT buttons, so the input row and its hold/voldown/volup mapping are unchanged.
- No input component is selected; the button node exists so that BSPlatform and MobileGestalt read a coherent product.

### 完成条件

- Touches map to the display with stable contacts and the volume keys produce the expected HID reports.

### 当前范围

- No hardware buttons yet \(native\_buttons\_set\_sink is a no-op\), and dk=0 keeps every DriverKit dext off; why the AppleUserHIDDrivers server is never launched is not known.

### 下一步

- Hardware buttons \(power and volume\) through native\_buttons\_set\_sink, then find why the DriverKit HID server is never launched so dk=0 can go.

### 证据

- `device`: [Kernel 67b65eb / payload 1611d2a: the in-kernel IOHIDEventDriver attaches to the combined keyboard+touch device and is published as the built-in touch screen; 31072 touch transitions read; Setup reacts to touch \(confirmed on the phone\) and applies a choice \(SpringBoard restart at 345 s\).](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/docs/evidence/sirius-touch-hid-20261029-combined.log)
  Command: <code>fastboot flash vendor tmp/payload-AD-combined.img; fastboot reboot; four python scripts/capture-usb-console.py --follow --duration 280 --idle-stop 20 windows; touch the Setup screen</code>. Revision: `fb84613a61cf55e48e30f2e126fd6b3183820def`.

## GPU {#gpu}

`planned`

### 硬件与依赖

- Adreno 616 \(A6xx gen1, the A615 family with A615/A618/A619\): GPU at 0x05000000 \(0x40000\) with cx\_mem 0x0509e000, GPU SPI 300; GMU at 0x0506a000 \(0x30000\) with SPI 304 \(hfi\) and 305 \(gmu\); GMU PDC at 0x0b280000 and its sequencer at 0x0b480000 \(0x10000 each\); GPU CC \(sdm845-gpucc\) at 0x05090000 \(0x9000\); the GPU's own SMMUv2 at 0x05040000 \(0x10000\), global SPIs 229/231, context SPIs 364-371, GPU stream 0, GMU stream 5; ZAP region 0x95c15000 \(0x2000\). Values from mainline sdm670.dtsi; the SDM710 board's own reserved-memory and chip ID are not yet read on hardware.
- Firmware: 57UU/sirius-distro firmware/gpu carries a615\_zap.mbn \(14272 bytes, from ellyq/firmware-mainline-pyxis f2e4f88, README: GPU init verified on this phone\), a630\_sqe.fw and a630\_gmu.bin \(Debian trixie firmware-qcom-soc 20250410-2\). Linux loads the ZAP as qcom/sdm710/pyxis/a615\_zap.mbn.
- On sirius the ZAP region is at 0x97615000 \(0x2000\), not sdm670.dtsi's 0x95c15000: 57UU/linux-sirius sdm710-xiaomi-sirius.dts \(17601ca5198a736f696447a9b6c568e4be97cc9c\) deletes gpu\_mem and redefines it, enables &amp;gpu \(qcom,adreno-615.0, the upstream msm driver\) and names the ZAP firmware. That kernel runs the GPU on this phone and is the working reference for the A616 backend.

### 配置

- Nothing is configured: the CPU renders the boot-progress panel through the firmware framebuffer.

### 操作步骤

- Start from Adreno6xx \(RigoLigoRLC/unixnu-adreno6xx, branch unixnu-sm-t733\): the Adreno740 service, BO/VM, ring, submission, fences and NativeAdreno ABI v1 with an A6xx power, GMU, SMMU, ZAP and register-init backend, so AdrenoMetal stays usable unchanged.
- Keep the component's split: A6xx procedures in the component \(an A616 generation next to A642L\), board windows, interrupts and stream IDs in this repository through native\_adreno\_a6xx\_resources and an /arm-io/adreno ADT node, as sm-t733 does in package/T733GpuResources.cpp.
- First milestone, in order: CX GDSC and GMU clocks, GMU firmware boot and an HFI reply, GX on, CP start, one bounded submission whose fence completes. Metal and presentation come after.

### 开发经验

- Phase 2 on hardware \(kernel 20050dd / payload a41130b, commit 8c3c2df, docs/evidence/sirius-gpu-20261029-gmu.log\), first boot: the GMU boots and HFI v1 answers. The 64 KiB DMA block lands at 0xa684b000; context bank 1 reads back CBAR 0x1f300, CBA2R 1, SCTLR 0x1027, TCR 0x802020, TCR2 0x38001, TTBR0 0x00010000a684b000, MAIR0 0xf404ff44, FSR 0x400 \(FORMAT = AArch64, no fault\), both TLB syncs complete, SMR1 0x80000005, S2CR1 1, and ATS1PR of 0x60009000 returns PA 0xa6857000 as wanted; writing the GPU SMMU did not hang the SoC. The RSCC and PDC sequencer words read back, the 8192 firmware words read back identical from ITCM, the version marker reads 0 so the CM3 is expected to report 0xbabeface, and FW\_INIT\_RESULT reads 0xbabeface. The GX rail vote \(gfx index 5 = level 192, mx index 3 = 256\) is acknowledged \(GMU2HOST\_INTR\_INFO 0x40000000\) and the GX GDSC is then powered \(GDSCR 0xf8222000, was 0x00222001\), SPTPRAC reports 0x28, HFI\_CTRL\_STATUS 1, HFI INIT replies error 0 \(header 0x0002047e\) and FW\_VERSION replies error 0 with version 0x10060000. The GMU log buffer stays zero. The rest of the boot is unchanged \(SpringBoard at 139 s, no panic in 280 s\).
- On SDM710 cmd-db puts gfx.lvl at 0x30050 \(cx.lvl 0x30000, mx.lvl 0x30010; gfx.lvl levels 0 16 48 64 128 192 256 320 384 416\), not at the 0x30080 that a6xx\_gmu\_rpmh\_init uses for the A615 as the third PDC TCS command address \(the A618 and A619 use their own SoC values\). Phase 2 still writes Linux 0x30080 and the GMU boots; the PDC sleep/wake commands only run when the GPU power-collapses, so phase 3 should use the cmd-db address before enabling any GMU power collapse.
- scripts/build-sirius-gpu.py fetches a630\_gmu.bin from 57UU/sirius-distro at 010ce33d65e9bcbefa2af35714fe49810189eaa8 \(32768 bytes, sha256 da8d9b1b1f5c1a0b311f32567093b4828f3c80031dd8435f91ac13c664e173a6\), refuses any other content and compiles it in as sirius\_gmu\_fw\[\] next to sirius\_gpu.o; the firmware is not committed.
- Phase 2 \(sirius-gpu=2\) boots the GMU as a6xx\_gmu\_resume\(\) does for a legacy A630-family GMU, without GX: 64 KiB physically contiguous below 4 GiB \(sirius\_gpu\_dma\_alloc, cached and cleaned/invalidated around each exchange\) holds three page-table pages and the GMU dummy page plus its 16 KiB debug, log and HFI buffers at iova 0x60000000/0x60001000/0x60005000/0x60009000 \(Linux order\); the GPU SMMU gets context bank 1 \(bank 0 stays for the GPU CP\) as a stage-1 AArch64 context \(CBAR 0x1f300, CBA2R VA64, TCR 0x802020 = T0SZ 32 with non-cacheable walks, TCR2 0x38001, MAIR0 0xf404ff44, SCTLR 0x1027 without the fault IRQ\), then S2CR1 = bank 1 and SMR1 = valid \| stream 5, with an ATS1PR check of the HFI iova; then the HFI queue table \(command 0, response 4, debug 5\), the RSCC and PDC sequences of a6xx\_gmu\_rpmh\_init \(A615 values: PDC address 0x30080, TCS3 wake data 3\), a630\_gmu.bin into ITCM \(0x1b400\) with a read-back, the fw\_start registers \(BOOT\_CONFIG 2, HFI\_QTBL, AHB fence 0x802800a0, CM3\_CFG 0x4052, chip id 0x06015000, log iova \| 3, power\_config for idle level ACTIVE\), the CM3 out of reset waiting for 0xbabeface or 0x100 in FW\_INIT\_RESULT, the GX rail vote \(OOB BOOT\_SLUMBER with gfx.lvl/mx.lvl indexes for level 192 read from cmd-db\), SPTPRAC, HFI\_CTRL\_INIT, and the HFI v1 INIT and FW\_VERSION messages \(polled; a zero-size or out-of-range reply ends the exchange instead of spinning a CPU\). The result is the panel GPU7 row \(GMU phase=N init=... hfi=... ver=...\).
- Phase 2a on hardware \(kernel 4f8ea4d / payload 75dcdf0, docs/evidence/sirius-gpu-20261029-smmu.log\): the boot chain leaves the GPU SMMU empty. All 5 SMRs read 0 \(VALID clear\), all 5 S2CRs 0x000200ff \(TYPE 2 = fault, CBNDX 0xff\), all 5 context banks unconfigured \(CBAR, CBA2R, SCTLR, TTBR0, TCR, MAIR0, FSR 0\), and sCR0 0x00200626 has USFCFG set, so an unmatched stream faults too. The GMU \(stream 5\) therefore has no path to memory until this port programs an SMR, an S2CR and, for translation, a context bank; nothing of the boot chain's is in use there, as on Linux, which programs this SMMU from scratch.
- Phase 2a \(read-only, not run yet\): after the phase-1 reads, package/sirius\_gpu.c dumps the GPU SMMU stream mapping the boot chain left: SMR and S2CR of each of the IDR0.NUMSMRG groups \(5\) and, per context bank \(IDR1.NUMCB = 5, 4 KiB pages, context banks after 2 &lt;&lt; NUMPAGENDXB = 8 global pages\), CBAR, CBA2R, SCTLR, TTBR0, TCR, MAIR0 and FSR. It decides whether the GMU stream \(5\) can reuse a boot-chain mapping, needs bypass or needs a context bank of its own before the GMU firmware is loaded.
- Kernel 86b616b \(commit 54e6ffe\) / payload f2ba289: GPU phase 1 done \(docs/evidence/sirius-gpu-20261029-phase1.log\). With only the GPLL0 votes and gpu\_cfg\_ahb before it, the CX GDSC powers up \(GDSCR 0x00222001 -&gt; 0xf8288000, gds\_hw\_ctrl 0x80001fe0\); after it memnoc\_gfx \(0x00004221\), snoc\_dvm\_gfx and ddrss\_gpu\_axi run; the GMU RCG takes cfg 0x602 \(GPLL0 main div / 1.5\) and cx\_gmu and cxo run. GMU: CM3\_SYSRESET 1 \(CM3 held in reset\), FW\_INIT\_RESULT 0, CORE\_FW\_VERSION reads 0xccf3d6df \(no firmware loaded\), SPTPRAC\_PWR\_CLK\_STATUS 0xd4, RPMH\_POWER\_STATE 0xf; GMU\_ALWAYS\_ON\_COUNTER\_L advances 2019368 in a 10 ms sleep, about 200 MHz, so on this GMU it counts the GMU clock and confirms the 200 MHz source. GPU SMMU: sCR0 0x00200626 \(CLIENTPD clear: enabled by the boot chain\), IDR0 0x48016605, IDR1 0x20008005, IDR2 0x00007511, IDR7 0 \(SMMUv2\). Next: phase 2, GMU firmware boot and HFI v1, which needs GMU-visible memory through the GPU SMMU \(GMU stream 5\).
- Kernel 26ed024 / payload 3f16296: phase 1 stopped safely at its first gate. GCC vote 0x52004 = 0x01601d7b, gpu\_cfg\_ahb 0x00000001 \(on\), but gpu\_memnoc\_gfx reads 0x80004221 after enabling and snoc\_dvm\_gfx 0x80000001: both enabled and CLK\_OFF. They feed the collapsed GPU CX domain \(memnoc\_gfx and ddrss\_gpu\_axi are BRANCH\_VOTED, enabled in Linux as GMU/SMMU clocks after the CX GDSC\), so the probe now enables only the GPLL0 votes and gpu\_cfg\_ahb before the CX GDSC, the other branches after it, and reads the GPU SMMU only with memnoc\_gfx running.
- Phase 1 of the A616 bring-up is a standalone probe, package/sirius\_gpu.c \(sirius-gpu=1, from native\_legacy\_display\_late\_probe\), before the Adreno6xx fork: GCC votes 0x52004 bits 15/16 \(GPLL0 and its divided output to the GPU\) and the gpu\_cfg\_ahb \(0x71004\), gpu\_memnoc\_gfx \(0x7100c\), gpu\_snoc\_dvm\_gfx \(0x71018\) and ddrss\_gpu\_axi \(0x44038\) branches, each checked for CLK\_OFF; then the GPU CC CX GDSC \(0x106c: wait values EN\_REST 2, EN\_FEW 8, CLK\_DIS 8, SW\_COLLAPSE cleared, PWR\_ON polled in gds\_hw\_ctrl 0x1540, gdsc.c\); then the GMU RCG \(0x1120\) at 200 MHz \(source 6 = GPLL0 main div, divider 1.5, rcg2\_shared force-on around the update\) and the cx\_gmu \(0x1098\) and cxo \(0x109c\) branches. It then only reads: GMU registers at 0x05000000 + 4 x dword offset \(a6xx\_gmu.xml: CM3\_SYSRESET 0x1f800, FW\_INIT\_RESULT 0x1f81c, CORE\_FW\_VERSION 0x1d3f8, ALWAYS\_ON\_COUNTER\_L 0x1f888 twice 10 ms apart, SPTPRAC 0x1f8d0, RPMH\_POWER\_STATE 0x1f8ec, HFI\_CTRL\_STATUS 0x1f980\) and the GPU SMMU global sCR0/IDR0/IDR1/IDR2/IDR7. Adreno6xx is not in this UniXNU catalog and its build needs ArmSmmu4K, AdrenoPM4, AdrenoFirmware and generated ABI bindings, so the fork follows once the CX sequence is proven on hardware. Not run on hardware yet.
- Without a Metal device CoreImage falls back to an OpenGL context and crashes there: iconservicesagent dies with SIGSEGV at PC 0 in CI::GLContext::init\(\) + 220, reached from IconServices -\[ISGraphicSymbolResource imageForSize:scale:\] through CoreUI +\[CUIShapeEffectStack sharedCIContext\] while rasterizing an SF Symbol glyph \(docs/evidence/sirius-crash-symbols-20261028.log\). launchd restarts it; any process that rasterizes symbol glyphs through CoreUI can hit the same path until a GPU driver exists.
- The catalog's Adreno740 targets the A740 of SM8550, and Adreno6xx's backend is written for the A642L of SM7325 \(A660 firmware, QSMMUv500 with TBUs, AOP-hosted PDC, ACD through AOP QMP, Yupik clocks\).
- For the A616 the backend needs: the legacy GMU/HFI protocol \(Linux sets gmu-&gt;legacy for the A630 family\), PDC and RSCC sequences with the PDC in its own MMIO window rather than in AOP, the a615\_hwcg clock-gating table and a630 protect list, sdm845 GPU CC clock and GDSC handling, and a plain SMMUv2 \(no TBU windows\).
- Linux's A6xx catalog has no separate A616 entry; the A615 entry \(chip ID 0x06010500\) uses a630\_sqe.fw, a630\_gmu.bin and a615\_zap.mdt with 512 KiB GMEM and ADRENO\_QUIRK\_4GB\_VA, so the chip ID must be read from RBBM on this phone.
- The S2CR writes that hung the SoC were on the apps SMMU, which the boot chain leaves disabled; the GPU SMMU is a separate instance in the GPU CX power domain and must not be touched before CX is on.
- On SDM710 touching a branch clock before its source is programmed has stalled the bus and rebooted the phone \(sirius\_usb\_power\), so the GPU CC sequence must program sources before enabling branches.

### 完成条件

- GPU submissions complete, fences work and a known image renders.

### 当前范围

- The GMU boots and answers HFI v1, and GX is powered through its boot vote, but the GPU core is not started \(no perf or bandwidth table, ZAP, SQE or CP\) and nothing renders on it; the GMU stays in its boot state \(OOB BOOT\_SLUMBER set\).
- Adreno6xx's power, GMU and SMMU sources carry GPL-2.0-only notices \(adapted Qualcomm procedures\); the rest of the component is MIT.

### 下一步

- Phase 3: the HFI v1 perf and bandwidth tables \(a6xx\_hfi\_send\_perf\_table\_v1, the A615 bw table\), the GPU register init for the A615 \(hwcg, protect list, GBIF\), the ZAP shader through SCM \(a615\_zap.mbn at 0x97615000\), a630\_sqe.fw and a CP start with one ring and a fence, using the cmd-db gfx.lvl address in the PDC sequence. Then the Adreno6xx fork with an A616 generation.

### 证据

- `device`: [Kernel 20050dd / payload a41130b with sirius-gpu=2: the GPU SMMU context for stream 5 translates \(ATS1PR ok, no fault\), a630\_gmu.bin loads into ITCM, FW\_INIT\_RESULT 0xbabeface, the GX rail vote is acknowledged and the GX GDSC powers on, HFI starts, and HFI v1 INIT and FW\_VERSION reply with error 0 \(version 0x10060000\). The boot continues to SpringBoard without a panic.](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/docs/evidence/sirius-gpu-20261029-gmu.log)
  Command: <code>fastboot flash vendor tmp/payload-AI-gmu.img; fastboot reboot; python scripts/capture-usb-console.py --follow --wait 120 --duration 280 --match 'NEMMC PANIC TEXT END' --idle-stop 20</code>. Revision: `8c3c2df22a19fc6cefebcf374e4442377d6e54fd`.
- `source`: [A6xx backend for A642L/SM7325 on the Adreno740 service: NativeAdrenoA6xxResources lists the board windows \(gpu, gmu, smmu, gpucc, gcc, pdc, rscc, command-db, rpmh, aop, ipcc, cx-misc, zap, smmu-tcu/tbu\), interrupts and SMMU bank/SID assignments; power, GMU and SMMU are SM7325-specific.](https://github.com/RigoLigoRLC/unixnu-adreno6xx/tree/89cd057d60499e2ee4f844db507ebb00d679ec5e)
- `source`: [SDM670/710 GPU, GMU, GPU CC and adreno SMMU nodes with registers, interrupts, stream IDs, the 0x95c15000 ZAP region and the OPP table; drivers/gpu/drm/msm/adreno/a6xx\_catalog.c and a6xx\_gmu.c at the same revision give the A615-family firmware names, hwcg table and legacy GMU handling.](https://github.com/torvalds/linux/blob/65ba8f34ec886ec72b2c07ddc8cf3d815c32869d/arch/arm64/boot/dts/qcom/sdm670.dtsi)

## 网络 {#network}

`planned`

### 硬件与依赖

- The Wi-Fi chip of this unit is not identified in the port record yet.

### 配置

- No network component is selected.

### 操作步骤

- Follow the network guide once the chip and its firmware are known.

### 开发经验

- No network work has started; the first console image does not need it.

### 完成条件

- Scanning, association and sustained traffic pass with the selected firmware.

### 当前范围

- No network support at any layer.

### 下一步

- Identify the WCN chip from the vendor DTS and the firmware partition before selecting a driver.

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`planned`

### 硬件与依赖

- No audio path is documented for this unit yet.

### 配置

- No audio component is selected.

### 操作步骤

- Follow the audio guide once the codec and DSP path are known.

### 开发经验

- No audio work has started.

### 完成条件

- Each declared route carries the selected format through playback or capture.

### 当前范围

- No audio support at any layer.

### 下一步

- Inventory the codec and the DSP layout from the vendor tree.

### 证据

按下一步操作收集证据。

## 电源 {#power}

`planned`

组件: `AppleKeyStoreState`.

### 硬件与依赖

- No suspend/resume path exists; the boot-progress panel is the only power-facing behaviour so far.
- There is no SEP: nothing answers AppleKeyStore, which the unchanged libaks/MobileKeyBag ask for the device and lock state.

### 配置

- board.toml writes \[adt.defaults\] sleep-disabled = 1 so the CPU does not park forever.
- PSCI is declared in the SoC DTSI and used for reset and secondary-core start.
- AppleKeyStoreState is selected as sheng and asteroids select it: package/KeyStoreProbe.cpp \(sheng's, at 08cde20edc3254ed6f7df8d0f5384fb887786e8f\) publishes its service from the display late probe with offline-key-events=1, and sheng-aks=1 lets its user client answer the state queries \(no passcode, unlocked\). scripts/build-native-legacy-display.py compiles both into libNativeLegacyDisplay.late.a. It stores no key and protects nothing.

### 操作步骤

- Follow the power guide to add the PMIC and battery controls once the platform expert is stable.

### 开发经验

- The eMMC probe does not vote any RPMH resource; it re-enables the GCC SDCC1 branches that the boot chain had already set.
- Reset works through PSCI \(the stage-3 reset loop proved it\).
- Measured with the PMU cycle counter \(kernel 5df62c0, payload 8a04814\): the Cortex-A55s run at 1516 MHz and the Cortex-A75s at 300 MHz, the cpufreq-hw source-0 row \(GPLL0/2\) the boot chain leaves \(out/Q-cpuclk captures, NEMMC cpu MHz\).
- With sirius-cpufreq=1 \(kernel 130bf97, payload 216ef03, commit fb12af48938b7de333ca29b41195486b95e790ac\) the A55 domain \(enable 1, 9 rows\) moves from row 6 to row 8 and every A55 measures 1708 MHz; the A75 domain reads enable 0 \(13 rows, best 2208 MHz\), so the firmware never put it under hardware DCVS, the request is skipped as Linux would, and the A75s stay at 300 MHz.
- With the retry \(kernel f222029, payload 952ab40\) the A75 domain reads enable 1 after boot and gets row 12 \(2208 MHz\): NEMMC cpufreq enable/rows/before/request 0001000d0000000c; the A55s stay at 1708 MHz. No heartbeat ran on an A75 in that capture, so the A75 clock is requested but not yet measured \(docs/evidence/sirius-usb-console-20261028-cached.log\).
- sirius\_cpufreq\_retry\(\), called from the heartbeat every sixteenth beat once the secondary cores run, re-reads each domain's enable bit and makes the request a domain did not get at EARLY\_BOOT; NEMMC cpufreq ... enable shows the live bit.
- Under Linux on this phone \(57UU/sirius-distro docs/CPU-POWER-STRESS-TEST.md\) the same cpufreq-hw driver, which refuses a domain whose enable bit is 0, holds the A75s at 2208 MHz, so the A75 domain does become enabled; the enable 0 read at EARLY\_BOOT is likely taken before cpu6-7 are started \(not yet verified\).
- package/sirius\_cpufreq.c \(sirius-cpufreq=1\) reads each cluster's cpufreq-hw table \(0x17d43000 cpu0-5, 0x17d45800 cpu6-7; rows at 0x110 + 32 i, PERF\_STATE 0x920, current vote 0x704, the Linux qcom-cpufreq-hw layout for sdm670\) at EARLY\_BOOT and requests the highest non-boost row; the hardware sets voltage and its limits. The register bases are SoC facts that belong in the sdm710 SoC repository once proven.
- On asteroids SpringBoard never finished booting on persistent Data without the AppleKeyStore stand-in and reached its first picture with it \(UniXNU docs/devices/asteroids.md, T20-T29\); sirius shows the same state: persistent Data, SpringBoard no longer crashing, a few black frames and then no swaps.

### 完成条件

- Declared power controls and battery readings match observations and sleep/resume restores the dependent peripherals.

### 当前范围

- No battery reporting, no CPU frequency policy and no PMIC driver.

### 下一步

- Measure what makes the Apple-logo stage slow \(the live panel's LOAD, SCHED, FB and storage rows, captured without --match so the log runs past the assert text\), and find what stored the not\_in\_kdp assert.
- Keep sleep-disabled until a resume path exists.

### 证据

- `source`: [PSCI reset evidence and the reason sleep is disabled.](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/docs/HANDOFF.zh-CN.md)
- `device`: [kernel.macho 1a8a1511ad225f51760442fd657596218406c87e6b9c5d43929f33d2c8449b99, payload 6b03df13c9036952722a51f1bf1fe06691508dcea0daeda90e27082b3c15ab4c: the same path as without the stand-in \(display at 51.8 s, early boot complete at 163.0 s, display client at 178.4 s, power state 1 at 210.3 s, default\_fb\_surface miss at 213.9 s\), then 'pmap.c:3514 Assertion failed: not\_in\_kdp' appears in the panel's panic buffer at 215.7 s \(pmap\_tt1\_deallocate ran while the debugger flag was set\). The boot did not stop there: the heartbeat kept running and, with the cable unplugged and no reboot, the screen went on to iOS's Apple logo with a moving progress bar, the first picture the OS has drawn on this phone. The capture ended only because --match stops on the panic marker. No crash or ENOSPC line; the console carries no keystore line.](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/docs/evidence/sirius-usb-console-20261028-keystore.log)
  Command: <code>fastboot flash vendor payload-O-keystore.img; fastboot reboot; python scripts/capture-usb-console.py --follow --wait 120 --duration 280 --match 'NEMMC PANIC TEXT END' --idle-stop 20</code>. Revision: `f5b179d6bf746cf80028cd222823a048f8d6e905`.

## 镜像组装 {#packaging}

`implemented`

组件: `XnuPrelink`.

### 硬件与依赖

- The payload FAT volume is the flashed artifact of this port; there is no boot.img.
- The prelink inputs \(kernel path, roots, slide, early security initializer\) come from the OS profile; the board does not override them.

### 配置

- \[payload\] sets volume SIRIUSESP, 256 MiB, loader = payload, dram\_size and the kernel command line.
- \[payload.adt\] keeps only chip\_id: the platform seed is supplied per build with --unique-chip-id when the userland stages need it.

### 操作步骤

- ./unixnu build kernel, ./unixnu build package, then bash scripts/build-darwinboot.sh \(or the CI workflow\), ./unixnu build payload, and finally make-uboot-payload.py --output the volume to flash.

### 开发经验

- scripts/build-sirius-touch.py compiles package/sirius\_touch.c like build-sirius-cpufreq.py and adds it to libShengPlatformPower.a.
- The eMMC probe ships in the same force-loaded archive as the USB console, so the package list and payload layout are unchanged.
- scripts/build-arm-driver.py replaces the tree's copy, so a component recipe that names it must be one of its choices: AppleKeyStoreState builds drivers/AppleKeyStoreState/NativeKeyStoreEvents.cpp into build/apple-key-store-state/libAppleKeyStoreState.a.
- Format 2 generates kernel.macho.adt from the DTS, so the legacy ADT script is retired; make-uboot-payload.py still finishes the volume because U-Boot needs the EFI binaries inside it.
- scripts/build-xnu-4k-baseline.sh is a copy of the UniXNU script with one board deviation: the boot-progress interlock only requires the source crypto provider.
- The legacy build applied patches/xnu/\*.patch by glob \(56 files\); format 2 applies only what the series list names, and the ARM64 and OS series assume the two files they omit are present. native-smp-secondary.patch sets MAX\_CPUS 8 and Affinity1 core numbering; sheng-platform-power.patch supplies the bsd\_init.c block that zzz-boot-progress.patch quotes as context \(CONFIG\_XNU\_SHENG\_PMGR is off, so its code compiles to nothing\). Both now live in the sdm710 SoC series, which applies before the OS series.
- The first format 2 kernel build on Linux failed at the last patch, zzz-boot-progress.patch, with a bsd\_init.c context mismatch: the missing piece was sheng-platform-power.patch, not the moved native-smp-secondary. With both in the SoC series the whole series applies and the kernel prelinks: kernel.macho 50 MB, \_\_TEXT 0xfffffff007004000, 30 kernelcache components, 69294 bindings.
- The kernel step also runs on Linux through UniXNU's toolchain installer, which builds a patched LLVM, cctools-port ld64, MIG, iig and lzfse. That installer writes /opt/unixnu-linux, /usr/bin shims and distribution packages, so this port runs it inside a Podman image \(containers/xnu-linux/\) and leaves the host untouched. The alternative, Allenwdk/xnu-linux-toolchain, uses the system clang with portable-kalloc-type-builtins.patch and cctools-port, but needs a path-layout adapter for the driver's checks.
- The first flashed build hung on hardware with the entry probe's blue bar and no magenta bar. The cause was a defconfig override, not the kernel sources: CONFIG\_XNU\_NATIVE\_ARCH\_TIMER=n. build-xnu-4k-baseline.sh sets NATIVE\_ARCH\_TIMER=$&\#123;XNU\_NATIVE\_ARCH\_TIMER:-$&\#123;XNU\_ARMCPU:-0&\#125;&\#125;, so the legacy build ran with 1; at 0, architectural-timer-entry.patch compiles the BCM2837 local interrupt router write \(0x40000040 + cpu\*4, Raspberry Pi local peripherals\) into start.s. SDM710 has nothing at that address, and the store aborts before the MMU is on. The defconfig now leaves the ARM64 profile value \(y\) alone and documents why.
- Diagnosis method worth repeating: the legacy kernel from payload-full.img boots with this repository's new UniXNU.efi, DarwinBoot.efi and DTS-generated ADT \(it reaches \_sleh\_irq and panics on the known early timer PPI\), so the EFI side and the ADT are sound and the regression is in the kernel build. Comparing the two kernels' start\_first\_cpu bodies then showed the extra router write as the only semantic difference.
- With the timer override removed the Linux-built kernel boots past the MMU on hardware: the boot-progress panel reports TOPO boot=0 max=7 nums=01234567, the console reaches IOKit \(PE\_init\_iokit, IONVRAM initImageFormat\) and then the CPU takes an IRQ it cannot dispatch. lr 0xfffffff00741754c is \_sleh\_irq+0x70, the same NULL per-CPU handler the legacy kernel hit.
- That IRQ is DarwinBoot's early timer PPI. GIC\_SGI\_PPI\_ENABLE included bit 19, so the EL1 virtual timer fired before ArmCpu::start installed the handler. DarwinBoot now enables SGIs 0..15 only and leaves INTID 19 to ArmCpu \(armcpu-timer-intid=19\), which is what the handoff's next step asked for.
- With the timer PPI left to ArmCpu the next stop was AppleARMPlatform's CPU class: it matches cpu0..cpu7 because IODTPlatformExpert compares IONameMatch by prefix \('cpu' matches 'cpu0'\), starts first, and panics with 'CPU configuration in device tree is invalid' \(its AppleARMCPU.cpp validates max\_cpus, cpu-id, interrupts and function-\* properties that an Apple device tree carries\). The native ArmCpu personality \(IOPlatformDevice, probe score 2000\) did not win that match even after probe\(\) added 40000, so make-uboot-payload.py rewrites the AppleARMCPU IONameMatch from cpu to xpu in the personality plist inside kernel.macho \(equal length, nothing moves\).
- A frozen panel is not proof of a hang: the panel repaints from the timer interrupt, so before ArmCpu enables the timer PPI the last painted second stays on screen while the kernel may still be running. Checkpoints \(armcpu-panic=N, panics at entry/prepareGic/registration/controller/initCPU/registerService\) are what distinguish the two.
- ArmCpu::start then failed inside initDistributor: it re-ran the quiesce sequence \(GICD\_CTLR &amp;= \~3, wait, restore with ARE\) over the state DarwinBoot had already programmed, which clears the group enables and leaves the core with no interrupts at all; the boot then sits in IOKit matching with a frozen panel. The fix keeps the firmware state when GICD\_CTLR already reports affinity routing plus group 1 and only quiesces the SPIs. After it the panel advances \(time=31s, IRQ=1076\) and the kernel reaches bsd\_init with TOPO boot=0 max=7, PROBE calls=17 acc=8 num=7 reg=700 - eight CPUs online.
- The next blocker is AMFI: 'AMFI: No PMGR?' @ConfigurationSettings.cpp:235. The unchanged target AMFI finds the PMGR through IOService::serviceMatching\("ApplePMGRNub"\) + waitForMatchingService, then reads the provider at nub+0x88 and calls its readAon/writeAon slots \(OR bit 2\). The original classes are ApplePMGR \(storage 0x4b8a8\) and ApplePMGRNub \(0x740\); UniXNU/scripts/audit-amfi-pmgr-contract.py pins the exact instructions. amfi\_get\_out\_of\_my\_way=1 does not skip the check. Two routes remain: instantiate the original classes the way UniXNU-sheng does \(OSKextLoadKextWithIdentifier + a generated OriginalPMGRABI.h + a published nub\), or patch the AMFI block in the prelinked kernel.
- AMFI is cleared without touching the target kernel: the nub helpers behind AMFI's readAon/writeAon return 0 when the provider stored at nub+0x88 is NULL, so publishing a real but provider-less ApplePMGRNub satisfies the latch \(read 0, OR 4, write no-op\). package/SiriusPmgr.cpp allocates the class through OSMetaClass::getMetaClassWithName + alloc + init, attaches it to the platform and registers it from the sheng\_pmgr\_run hook in bsd\_init \(CONFIG\_XNU\_SHENG\_PMGR=1, sheng-pmgr=2\), and its build script writes the archive to build/sheng-platform-power/libShengPlatformPower.a because build-xnu-4k-baseline.sh force-loads exactly that path.
- With AMFI satisfied the boot passes bsd\_init and stops at 'Failed to mount root device' @IOKitBSDInit.cpp:984 with 8 CPUs, IRQ=2145, 61 s of live uptime: the kernel now runs to the point where it needs a storage driver and a root filesystem, which this board does not have yet \(no UFS or VirtIO block component, no APFS container on the payload volume\).

### 完成条件

- The kernel prelinks against the pinned 21H461 kernelcache, the payload contains the kernel, the ADT and the DarwinBoot driver, and the flashed volume boots from U-Boot.

### 当前范围

- The kernel step needs macOS and Xcode, or the container image with UniXNU's Linux toolchain; the board script must be re-based on the upstream script when UniXNU changes it.

### 下一步

- Run the new payload once and diff the generated ADT against the legacy one before flashing.
- Boot the prelinked kernel on the phone and record the stage rows; the build side is now reproducible on Linux \(container image, see downloads\).

### 证据

- `source`: [Build and deploy loop, the CI kernel artifact and the payload layout on the vendor partition.](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/docs/HANDOFF.zh-CN.md)

## 诊断 {#diagnostics}

`implemented`

### 硬件与依赖

- The panel and the serial console are the two evidence channels; since the DWC3 CDC console works, the host captures the kernel log directly and photographs are only a fallback.

### 配置

- panic\_screen = true patches the entry probe and the panic screen into the payload kernel.
- boot-progress=2 draws the kernel console lines; debug=0x14e keeps the debug output on.

### 操作步骤

- Record the last checkpoint printed on the panel and in the U-Boot/XNU log for every boot, with the kernel and payload hashes of that run.

### 开发经验

- docs/evidence/sirius-gpu-20261029-gmu.log is the GPU phase 1, 2a and 2 lines of kernel 20050dd / payload a41130b \(see the gpu area\).
- package/sirius\_gpu.c phase 2 logs each GMU boot step \(and a corrupt HFI response queue\) as a GPU console line and writes its result into boot\_progress\_ext\_wide\[0\], the panel GPU7 row \(see the gpu area\).
- The final UEFI memory map of kernel 10cc072 / payload 3361ec2 is docs/evidence/sirius-memory-20261029-efimap.log.
- The heartbeat's memory report adds NEMMC efi-map lines from /chosen/darwinboot-efi-map \(see the memory area\).
- The GPU SMMU stream-mapping dump of kernel 4f8ea4d is docs/evidence/sirius-gpu-20261029-smmu.log.
- package/BootWatchdogPolicy.c \(sirius-skip-setup=1, kernel\_args\) writes, on every boot before launchd, the preference values of UniXNU scripts/seed-data-skip-setup.py \(from dipa-studio/ios-sweet, established on hardware\) into the persistent Data volume as XML plists owned by mobile \(501\), mode 0600: com.apple.purplebuddy SetupDone, SetupFinishedAllSteps, SetupVersion 11, daemonizeNeedsToRun false; the purplebuddy.notbackedup mini-buddy flags false; managedconfiguration.notbackedup LockdownActivationIndicatesCloudConfigurationAvailable false; com.apple.springboard BKNoWatchdogs, FBLaunchWatchdogExceptions &\#123;com.apple.purplebuddy: 100&\#125;, MCForceShowCloudConfigurationUI false and SBDisableAutoDim, SBDontDimOrLockOnAC, SBDisableIdleSleep \(no power button driver to wake the display\). The seed tool edits a packed RAM Data seed on a Mac and cannot reach this board's eMMC Data volume. sheng-setup=1 still wins \(the Hello page\). Each write logs sirius skip setup: &lt;path&gt; &lt;errno&gt;. Not run yet.
- package/sirius\_gpu.c also logs the GPU SMMU stream-mapping dump as GPU smmu smrN/cbN lines \(see the gpu area\).
- The HID and SpringBoard-restart lines of kernel 67b65eb / payload 1611d2a are docs/evidence/sirius-touch-hid-20261029-combined.log.
- The HID lines of the dk=0 touch-only boot are docs/evidence/sirius-touch-hid-20261029-dk0.log.
- The live banner shows the touch path in a TOUCH row \(see the input area\).
- The HID-path lines of kernel 985facb / payload d7f5ce4 are docs/evidence/sirius-touch-hid-20261029.log.
- package/SiriusHidProbe.cpp defines a no-op native\_buttons\_set\_sink for the static kernel link \(see the input area\).
- package/SiriusHidProbe.cpp logs its result as TOUCH hid lines \(IOLog\).
- The GPU phase-1 and touch lines of kernel 86b616b / payload f2ba289 are docs/evidence/sirius-gpu-20261029-phase1.log.
- The TOUCH and GPU lines of the second probe boot are docs/evidence/sirius-touch-gpu-20261029-probe2.log; the USB console dropped out at about 155 s of the first window and later windows found no port, while the phone kept running \(panel photo at t=328 s\).
- package/sirius\_gpu.c logs each GPU phase-1 step as a GPU console line \(see the gpu area\).
- The TOUCH lines of the first probe are docs/evidence/sirius-touch-20261028-probe1.log; the chip-id line now also prints the transfer's M\_IRQ status and the bytes read.
- Kernel ca828cc / payload 38305ff \(commit c54ee19, ephemeral-storage = 1\): iOS reaches the Setup welcome screen \("hei", status bar, clock, battery icon\) at about 358 s without a GPU driver \(docs/evidence/sirius-spawn-20261028-ephemeral.log\): com.apple.datamigrator now exits 0 after 18 to 35 s \(four runs between 150 and 302 s\), Setup is exec'd at 225 s, PosterBoard at 208 s; the wallpaper poster extensions crash-loop \(KaleidoscopePoster signal 11, AegirPoster signal 6, CollectionsPoster killed by libxpc\), crashes=20 at 358 s. Touch does nothing: there is no touch driver yet.
- package/sirius\_touch.c logs each touch bring-up step as a TOUCH console line \(see the input area\).
- Kernel ca828cc \(commit 144de65\) / payload 95bcb3a \(commit 1ce0478\): no panic. SPAWN timeline \(docs/evidence/sirius-spawn-20261028-nostackshot.log\): launchd's boot tasks at 139 s, SpringBoard at 142 s, backboardd 148 s, com.apple.datamigrator 151 s, iconservicesagent 154 s \(it no longer crashes\), com.apple.migrationpluginwrapper 193 s and still running at 244 s; after 200 s only about 20 more execs. The console heartbeat stopped at about 258 s and later windows only trickled the old buffer \(1.1 MB in 5 min\), but the kernel kept running: the panel at t=2177 s shows crashes=0, the migration bar full, 62 swaps/s, idle 87%, RepackagingWorker killed by RunningBoard \(signal 9, namespace 15\) and the plugin wrapper by a signal 9. The same console stop came before the 335 s stackshot panic of payload cac4a55, so a stopped heartbeat alone is not a hung kernel.
- Kernel afdb4b1 / payload cac4a55 \(commit 144de65, the CoreUI fixup\) panicked at 335 s with "thread wait info count mismatch while capturing snapshots for task ..." \(kern\_stackshot.c:3451\); the console carried no panic text, the heartbeat stopped at beat 0x84. That check is DEVELOPMENT-only and fires when a thread's wait state changes between the count and the capture of a user stackshot, so not every CPU holds still during a stackshot on this port. kernel\_args now pass validation\_disables=0x10 \(KF\_STACKSHOT\_OVRD\): kern\_stack\_snapshot\_internal returns KERN\_NOT\_SUPPORTED to every stackshot request.
- package/BootProgress.c prints SPAWN &lt;second&gt;s exec &lt;pid&gt; &lt;name&gt; after an exec passes its signature check and SPAWN &lt;second&gt;s exit &lt;pid&gt; &lt;name&gt; status= ns= code= at every exit when sirius-spawn-log=1: the panel keeps only the last three failures, and the console carried no userspace timeline, so which job the idle boot waits on \(and the migration plugins' watchdog interval\) was not visible.
- The boot of kernel 5df62c0 / payload 8a04814 froze at about 244 s: the heartbeat stopped at beat 0x50, after that beat's clock measurement had returned and printed, with no panic text mirrored \(out/Q-cpuclk captures\). The cause is not known; the earlier boots without the PMU read ran 19 minutes.
- Crash records on the panel symbolize against the 21H461 arm64 shared cache: unslid address = recorded address - the record's slide \(+...\), looked up with ipsw dyld a2s; three cache files \(.symbols, .34 and .52 .dyldlinkedit\) are LZBITMAP-compressed in the SystemOS image and need apfs-fuse to extract. liveactivitiesd's SIGTRAP is a Swift runtime trap in SessionSyncEngine under SessionCore.Daemon.workloop \(docs/evidence/sirius-crash-symbols-20261028.log\).
- Every sixteenth beat the heartbeat also prints the CPU load since the previous sample \(NEMMC load user/sys/idle %, host\_statistics64 HOST\_CPU\_LOAD\_INFO\), to tell a CPU-bound late boot from one that waits. The first build of it failed: 'use of undeclared identifier realhost' in NativeEmmc.cpp \(kernel run 40695562209\).
- Every sixteenth beat the heartbeat also prints each cluster's cpufreq-hw state \(NEMMC cpufreq enable/rows/before/request, row0 and best kHz, vote MHz\) and the memory layout \(NEMMC window base/size, NEMMC db-runs\).
- NEMMC cpu MHz counts the architectural PMU cycle counter \(PMCCNTR\_EL0, PMCR\_EL0.E set and .D cleared, restored afterwards\) over 10 ms of the system counter with interrupts off, and NEMMC cpu mpidr names the core: Affinity1 0x000-0x500 are the Cortex-A55s, 0x600-0x700 the Cortex-A75s. No CPU frequency driver exists, so it shows the clock the boot chain left.
- The NEMMC fb rows print the copy cost on the console: copies, last/mean/max copy time, the last timed read-only pass over a source frame, and the source map options, scanout map options and the source page's pmap attribute \(VM\_WIMG\_\*\), packed as source&lt;&lt;40 \| scanout&lt;&lt;20 \| wimg.
- Heartbeat lines are re-mirrored too, so the last NEMMC alive line of a window is not the newest: compare the highest beat count per window before concluding the phone rebooted \(S-cached: 0x70 then 0xe9, the same boot\).
- Past about 220 s the USB console only re-mirrors fragments of the kernel log buffer: iOS userspace does not log to it, so four 280 s windows after the not\_in\_kdp text add no new event \(docs/evidence/sirius-usb-console-20261028-fbwc.log\). Later stages are read from the screen and the panel.
- The NEMMC heartbeat mirrors boot\_progress\_panic\_text once it is non-empty, not only on a fatal panic: with the stand-in it carried 'pmap.c:3514 Assertion failed: not\_in\_kdp' at 215.7 s while the kernel kept running and iOS went on to draw its Apple logo, so --match 'NEMMC PANIC TEXT END' can end a capture of a boot that is still alive \(docs/evidence/sirius-usb-console-20261028-keystore.log\).
- KeyStoreProbe.cpp writes the AppleKeyStore counters \(opens, calls, selector:count\) into extension slots 0-1, which the boot page draws and BootLog exports as X0/X1.
- A register write-and-read-back test is the next diagnostic for the eMMC data phase, because SDHCI\_TRANSFER\_MODE reads back 0x33 after writing 0x13, which separates a write the vendor layer ignores from a command that is never sent.
- The eMMC probe reports every step \(controller registers, the clock tree, the response registers around CMD0/CMD1 and each failure\) into the USB console ring, which is how the card clock and CMD2 findings above were obtained without a photograph.
- The eMMC probe reports through sirius\_usb\_log\_char\(\) straight into the USB console ring, because kernel console output stops reaching the ring long before bsd\_init runs.
- Stage bands \(entry, pre-MMU, panic\) and the TOPO/PROBE/MEM rows replaced the LED and UART guessing of earlier bring-up.
- A panic snapshot forces a panel re-render at panic time; before it, rows could show a stale frame.
- The USB panel row names its fields after what they hold \(step, txev, rxev, chars, echo, poll\) instead of the register names they were first wired to, so a photograph can be read without the source.
- The CDC console hands the console ring to the host once per attach: the pump timing that works \(a short inline poll loop that breaks after the ring is drained\) delivered the 3813-byte boot log on every attempt, while longer loops and a DTR-gated pump delivered nothing, so that timing is treated as load-bearing until the periodic path runs during bsd\_init.
- The post-exec wait is instrumented on the kernel side rather than through the driver: sirius-post-exec-trace.patch prints the exec thread-switch flags, every user thread start \(from thread\_bootstrap\_return, so one line means the exec'd thread never ran and two mean it did\), the first pid 1 syscalls with their returns, every bsd\_ast for pid 1 and the first user faults after the exec, and the eMMC heartbeat prints the counters so one capture answers the question.
- The exec does not stall after activate: load\_init\_program prints the scratch page \(0x1000, the first free page of the init map\), then the init thread is inside copyout\(\) and takes 62,673,044 faults in about a minute while it stays TH\_RUN, so the wait is a tight fault-retry loop, not a sleep.
- PAN was the cause after all. The 0 read at driver start was a snapshot: Kryo 360 implements PAN and XNU's SCTLR\_EL1\_DEFAULT leaves SPAN clear, so the CPU sets PSTATE.PAN on every exception entry to EL1, and with CONFIG\_XNU\_NATIVE\_PAN=n nothing clears it again. A copyout that runs with PAN set takes a permission fault that AT S1E1W \(which ignores PAN\) and vm\_fault both consider resolved, so it retries forever; PAN is not part of the switched context, which is why the loop moved with timing \(kernel 91 passed, 93 hung, cpus=1 got past the copyout\). With CONFIG\_XNU\_NATIVE\_PAN=y the driver reads PAN as 4194304 \(set\) and the loop is gone.
- The mapping is not missing either: the first fault is a level-1 translation fault, but afterwards pmap\_find\_phys finds the page, AT S1E1W resolves the same address and vm\_fault returns KERN\_SUCCESS, while the retried store faults again as a level-3 permission fault; the raw leaf PTE the pmap holds is now dumped next to ESR/FAR/PC to see which AP bits it carries.
- The pid 1 kernel stack, dumped out of band by the heartbeat and symbolized against mach.development.bcm2837.unstripped, shows \_bcopyout+0x38 under \_load\_init\_program\_at\_path+0x6c under \_bsdinit\_task+0x74, which is the copyout of the launchd path.
- The loop is not limited to the copyout: with the trust-cache bundle back in the payload the exec completes \(execve activate 0, AMFI answers nothing\) and the exec'd thread enters userland at pc 0x100924e50, where it takes 92 million instruction aborts in about a minute on three addresses \(ESR 0x82000007, level-3 translation faults\) without ever issuing a syscall or a single block read; the entry point is right, the code pages are simply not visible to the CPU.
- Both loops have the same shape: vm\_fault opens the page in thread-&gt;map's pmap and returns KERN\_SUCCESS, while the CPU keeps taking the fault. AT S1E1W and pmap\_find\_phys disagree about the physical page behind 0x1000, which points at the CPU running with a pmap that is not the thread's after the exec task switch.
- A payload built without --trust-cache leaves the ring reporting no external trust caches found and AMFI kills launchd with namespace 9 \(OS\_REASON\_EXEC\) code 8; the same kernel with the bundle present reaches execve activate 0 without an exec-policy line, so that panic is a build-argument slip, not a regression.
- The console can be captured on Windows: usbser.sys binds it as a COM port \(USB\\VID\_1209&amp;PID\_0001, serial SIRIUS01\) and capture-usb-console.py opens it with plain Win32 calls, because the gadget does not answer SET\_LINE\_CODING and SetCommState \(and pyserial\) fail with error 121.
- The ring has no timestamps and is replayed whole on every poke, so capture-usb-console.py --timeline records when each distinct line first arrives; a timed boot shows 51 s from fastboot reboot to the eMMC driver, the shared-cache check until about 168 s and the mount panic at 171.7 s. A hard panic stops the kernel before the heartbeat mirrors its text, so --idle-stop ends a capture after a silence instead.
- NativeEmmc reports the Data seed as 'NEMMC data seed at/bytes' when it publishes the RAM window and 'NEMMC data volume /dev/...' when the owner Data mount asks for it, or 'NEMMC data volume not found on the seed'.
- When the seed's volume UUID differs from CONFIG\_XNU\_OWNER\_DATA\_VOLUME\_UUID the driver logs 'NEMMC data volume is &lt;seed UUID&gt;, the kernel names &lt;configured UUID&gt;' and mounts it anyway.
- capture-usb-console.py --duration counts from the script's start: counted from the port, which a boot brings up after about a minute, a 280 s capture ran about 5.6 minutes.
- Persistent Data diagnostics: the driver logs 'EMMC write window lba=... blocks=... cache=...' on window configuration, reports EXT\_CSD CACHE\_CTRL in the probe, logs fallback to single-block writes if a multi-block write command fails, logs 'NEMMC data window lba=... blocks=...' when the persistent container is discovered, logs 'NEMMC data volume \(eMMC\) ...' or 'NEMMC data volume \(RAM\) ...' when resolved, and logs 'NEMMC write failed lba ...' on write errors.
- With the persistent 8 GiB Data volume, the entire boot capture runs past early boot \(159.6 s\) up to 280 s with zero ENOSPC lines \(vs 187 on the 256 MiB RAM seed\); containermanagerd, launchd, and analyticsd write without running out of disk space; APFS transaction flushes advance through xid 85; SpringBoard \(pid 118\) and liveactivitiesd \(pid 128\) crash for want of a display/framebuffer driver.
- Display driver diagnostics: LegacyDisplayProbe.cpp and LegacyDisplayStubs.c interpose on native\_legacy\_display\_probe and native\_legacy\_display\_late\_probe, mapping the 1080x2240 GOP framebuffer at 0x9c000000, setting up the display-subsystem platform device under /arm-io, and providing weak stubs for boot progress scanout and DPU mappings.

### 完成条件

- Each claimed milestone has a reproducible command, a matching source and image revision and an accessible result.

### 当前范围

- The CDC console delivers the console ring as it stood when the host attached; making the whole boot stream live is the remaining work.

### 下一步

- Add the boot row and hash triple to every hardware result recorded here, and attach the captured console log rather than a photograph whenever one exists.

### 证据

- `source`: [Entry probe, panic screen, panel rows and the evidence convention of the port.](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/docs/HANDOFF.zh-CN.md)
- `device`: [3813 bytes of kernel log read from /dev/ttyACM0 over the DWC3 CDC console.](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/docs/evidence/sirius-usb-console-20261026-1605.log)
  Command: <code>sudo python3 scripts/capture-usb-console.py --wait 60 --duration 190 --output /tmp/boot.log</code>. Revision: `366abe2948fdb0c1554f7e0b89b731160f4527a4`.
- `device`: [Captured on Windows \(COM7\) with --timeline: the Data seed and both owner volumes appear at 52 s after fastboot reboot, the mount panic text at 158.3 s, and the capture stopped on its marker after 5.4 MB.](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/docs/evidence/sirius-usb-console-20261028-data.log)
  Command: <code>python scripts/capture-usb-console.py --follow --wait 120 --duration 280 --timeline out/I-data.timeline --match 'NEMMC PANIC TEXT END' --idle-stop 20</code>. Revision: `33509e84db86517ff9bf349408dc66ab39c43d18`.
- `device`: [launchd's own \[System Event\] boot-task lines reach the USB ring, so the timeline shows each task as it starts; the heartbeat mirrored watchdogd's panic text at 191.9 s and the capture stopped on it.](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/docs/evidence/sirius-usb-console-20261028-early-boot.log)
  Command: <code>python scripts/capture-usb-console.py --follow --wait 120 --duration 280 --timeline out/J-bmh.timeline --match 'NEMMC PANIC TEXT END' --idle-stop 20</code>. Revision: `09096e3738c618bb18a51af50cdfbc7f6431aa59`.
- `device`: [Timeline capture of the 8 GiB persistent eMMC Data volume: write window logged at 44.8 s, Data volume disk3s1 \(eMMC\) mounted at 45.0 s, early boot complete at 159.6 s, tx\_flush commits through xid 85, no ENOSPC or panics up to 280 s.](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/docs/evidence/sirius-usb-console-20261028-pdata.log)
  Command: <code>python scripts/capture-usb-console.py --follow --wait 120 --duration 280 --timeline out/M-pdata.timeline --match 'NEMMC PANIC TEXT END' --idle-stop 20</code>. Revision: `e73a8ecda8998ec36573c5bd2a9d7b6389305b2d`.
- `device`: [The 280 s capture ran to 27 MB because the heartbeat re-mirrors the whole kernel log buffer \(382 copies of the Darwin banner\); the excerpt keeps the first arrival of the display, Data and boot-task lines and the crash, corpse, panic and ENOSPC counts.](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/docs/evidence/sirius-usb-console-20261028-display.log)
  Command: <code>python scripts/capture-usb-console.py --follow --wait 120 --duration 280 --timeline out/N-display.timeline --match 'NEMMC PANIC TEXT END' --idle-stop 20</code>. Revision: `076f63cee39bdb4ab11b4f85f6ffff15427ed948`.
- `device`: [Once a userspace swap has been presented the live diagnostics panel repaints at the bottom of the GOP frame: crash and exit records, FB copy cost, SWAP and GPU counters, load, scheduler lateness and backboardd work intervals, readable without the USB console.](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/docs/evidence/sirius-panel-20261028-display.log)
  Command: <code>photograph the screen after boot</code>. Revision: `076f63cee39bdb4ab11b4f85f6ffff15427ed948`.

## boot-chain {#boot-chain}

`implemented`

### 硬件与依赖

- Boot chain: ABL -&gt; U-Boot \(boot partition\) -&gt; UEFI -&gt; UniXNU.efi on the vendor partition -&gt; DarwinBoot.efi -&gt; XNU.
- The U-Boot fork github.com/57UU/u-boot branch sirius/v2.0 carries the board support for sdm710-xiaomi-sirius and sirius-build.sh's ENV\_FILE option; the UniXNU boot chain itself is environment text, not source.
- The EDK II package that builds UniXNU.efi, the DXE drivers and DarwinBoot comes from the UniXNU framework's package/ directory.

### 配置

- uboot/src is a submodule of that fork at branch sirius/v2.0 \(shallow\), pinned to a2a847b1a84.
- uboot/unixnu-sirius.env is the board's stock default environment plus unixnu\_boot/unixnu\_check, the bootmenu entry they need and the bootcmd chain; uboot/build.sh builds boot-unixnu.img from the submodule and that file.
- efi/ is a vendored copy of the framework's package/ \(UniXNUPkg, Scripts, build.sh\) taken at f85b5a6, so the repository can build the whole chain on its own.

### 操作步骤

- U-Boot: git submodule update --init --depth 1 uboot/src, then uboot/build.sh \(needs CROSS\_COMPILE and mkbootimg\); fastboot flash boot uboot/boot-unixnu.img.
- Payload: assemble the kernel, efi/ and the EDK II build output with scripts/make-uboot-payload.py --marker, then fastboot flash vendor.
- Recovery: flash sirius-distro's build/boot.img, which ignores the marker and boots Linux.

### 开发经验

- drivers/DarwinBoot: AdtNode records /chosen/darwinboot-efi-map \(exactly 768 bytes\) and FillEfiMapReport writes the final UEFI memory map into it before the hand-off \(see the memory area\); built locally \(DarwinBoot.efi 29696 bytes\).
- U-Boot needs no source change for this port: with the environment file above, bootcmd runs unixnu\_check first and falls back to the Linux path when /EFI/UniXNU/BOOTUNIXNU is absent on p80.
- mmc 0:50 is a hexadecimal partition number \(0x50 = 80 = the vendor partition\); 0:80 is read as 0x80 = 128 and fails with 'Invalid partition 128'.
- bootflow scan cannot find p80: it stops after the first 30 partitions of each device, so the boot chain uses load/bootefi with the partition spelled out.
- The UniXNU boot chain used to live only in an unversioned scratch directory \(the environment file and boot-unixnu.img\), so the boot image could not be rebuilt from any repository; both the file and the recipe are in uboot/ now.
- U-Boot's fastboot gadget answers the whole getvar dialogue but flashing the vendor partition hangs; the repeated 'request ... was not queued to ep1in-bulk' line is fastboot\_tx\_write\(\) cancelling the IN request before every queue, a dequeue miss rather than a rejected transfer, and stock 2026.07 never received the modern dwc3 ENDTRANSFER/dequeue rework, so that cancel can strand a TRB the controller still owns. Removing the dequeue is the candidate fix.
- Writing the BCB command 'uboot-fastboot' before booting UniXNU does bring the next start into U-Boot's own fastboot on the phone, so entering it is solved while flashing from it is not; the PMIC spare ABL actually reads \(PON\_SOFT\_RB\_SPARE, 0x88f = 0x04 in U-Boot's PID/offset encoding\) still needs CONFIG\_CMD\_PMIC and a verified pmic device name.
- U-Boot's fastboot reports slot a, so the host appends \_a to every partition name it flashes; fastboot\_partition\_alias\_&lt;name&gt;\_a=&lt;name&gt; in the environment maps both spellings onto the real GPT names.

### 完成条件

- uboot/build.sh reproduces boot-unixnu.img from a fresh clone; with the marker in the payload U-Boot starts UniXNU.efi, and without it the phone boots Linux.
- The payload volume holds UniXNU.efi, DarwinBoot.efi, kernel.macho, kernel.macho.trustcache and the marker.

### 当前范围

- The EDK II package is a copy, not a submodule: keeping it in step with the framework is a manual diff of package/.
- The U-Boot submodule is shallow and pinned by commit; rebasing onto a newer sirius/v2.0 is a deliberate update.

### 下一步

- Test the f\_fastboot dequeue removal end to end: after a power cycle, flash boot from U-Boot's own fastboot and, if that works, arm the BCB before booting UniXNU so a hung run comes back to a usable fastboot without the chord.
- Build UniXNU.efi from efi/ once and compare it with the framework's output, so the vendored copy is known good rather than assumed.

### 证据

- `source`: [The build recipe, the four environment lines that add the UniXNU chain, and the two partition/short-scan traps.](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/uboot/README.md)
- `source`: [Provenance of the vendored EDK II package \(framework commit f85b5a6\) and what the payload takes from it.](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/efi/README.md)

</div>
