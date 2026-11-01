# Rockchip RK3588 EVB10 V10

[Ken-u/UniXNU-evb10](https://github.com/Ken-u/UniXNU-evb10)

<div v-pre>

Rockchip RK3588 EVB10 V10 runs the iPadOS 17.7.11 userland on a source-built XNU, started from edk2-rk3588 firmware \(uefi-evb10\). Shared SoC support is in UniXNU-rk3588-common; this repository owns the memory layout, the eMMC root, the VOP2 display, touch, the Mali-G610 integration and the packaging. Every area in scope is device-verified on the board with a system built from these repositories \(docs/reproduce.md\): it boots to SpringBoard with the eMMC root and the Data volume mounted, the Mali composites the interface at about 50 frames per second while scrolling, and the panel and the touch screen were checked by hand and work normally. Wi-Fi works at 2.4 GHz and the audio path is implemented; the CPU clusters are under a frequency and voltage governor. Not done: GPU frequency control, interrupt-driven GPU completion, 5 GHz Wi-Fi, an audible check of the audio path, thermal limits and a measurement of the power the governor saves.

源记录: [porting.toml](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/porting.toml), `37befa9162d6b4b080cb63a95cccff0ebb4d34f5`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `device-verified` |
| [固件与启动](#firmware) | `device-verified` |
| [CPU 与中断](#cpu) | `device-verified` |
| [内存与 DMA](#memory) | `device-verified` |
| [存储与根卷](#storage) | `device-verified` |
| [显示](#display) | `device-verified` |
| [输入](#input) | `device-verified` |
| [GPU](#gpu) | `device-verified` |
| [网络](#network) | `device-verified` |
| [音频](#audio) | `implemented` |
| [电源](#power) | `device-verified` |
| [镜像组装](#packaging) | `device-verified` |
| [诊断](#diagnostics) | `device-verified` |

## 配置 {#configuration}

`device-verified`

### 硬件与依赖

- ARM64 profile, rk3588 SoC source pinned in feeds.toml, iPadOS 17.7.11 build 21H461 profile, evb10\_defconfig and evb10\_display\_defconfig, submodules package/Mali and package/Rk3588Emmc.

### 配置

- board.soc\_source = rk3588; board.os\_profile = ipados-17.7.11-21H461; schema\_version = 2.
- kernel.config\_fragments = arch common, soc rk3588, os ipados; the defconfig applies last and switches off what the OS profile enables for other hardware \(NATIVE\_ADRENO, SOURCE\_MOCKFS\).
- kernel.patch\_series = arch, soc, os, device in that order.
- payload.kernel\_args carries the frame-rate group as defaults: zero-copy scanout with the GPU job as the fence \(evb10-vop-direct=1, evb10-vop-fence=1\), the GPU at 750 MHz \(mali-pll=1, mali-div=1\), the device's YCbCr filter \(mali-ycbcr-filter=device\), asynchronous surface flush \(mali-aflush=1\), cpumask=31, mali-epri=50 and sched-slowcpus=240; the comment above the list says what each one does.

### 操作步骤

- From the UniXNU checkout run ./unixnu defconfig evb10\_defconfig -D ../UniXNU-evb10, then ./unixnu fetch and ./unixnu status --json with the same -D.
- For a local SoC checkout copy local.toml.example to local.toml.
- Run scripts/build-evb10-kernel.sh for the two-pass kernel build.

### 开发经验

- The \[adt.defaults.u32\] table of board.toml must carry sleep-disabled = 1 and vmm-present = 1; the OS profile only supplies kern.maxvnodes. vmm-present backs kern.hv\_vmm\_present: without it watchdogd traps with SIGTRAP three times and the kernel panics when the third instance exits \(seen in a rebuild from a clean tree, fixed in the clean-directory rerun\).
- Arrays replace inherited values, so board.toml lists every archive, fragment and trust-cache digest it needs.
- The display archive is made from the kernel of an earlier display-less pass, which is why two defconfigs exist and why the build script runs them in order.
- A device script named like a UniXNU script shadows it in the build tree; the board driver builder is therefore named build-evb10-drivers.py and does not replace build-arm-driver.py.
- A boot with the committed defaults and nothing else but the scripted swipes and the command-buffer timeline \(run v1\) held the GPU at 750 MHz, the Cortex-A76 cores at 2.23 GHz and 52.6 frames per second while the finger was down \(swipes 3 to 11\), and ended its 235 s capture without a panic or a stalled GPU group.
- The evidence/ directory holds one curated excerpt per verified checkpoint, named &lt;topic&gt;-&lt;date&gt;.txt. Excerpts of kernel runs name the run command and tag; the Wi-Fi identity excerpt \(evidence/wifi-sdio-id-20261030.txt\) comes from U-Boot with no kernel running, so it names the probe script and the uefi-evb10 revision that holds it.
- libEvb10Wifi.a \(package/Evb10Wifi, built by a board.toml step like the touch archive\) is linked by configs/evb10\_display\_defconfig only, because the display probe is its only caller; evb10-wifi=1 is a per-run argument, not part of the 884-byte defaults.
- board.toml runs scripts/build-wifi-firmware.py before build-evb10-drivers.py Evb10Wifi: it turns the AP6398S firmware and nvram of .cache/firmware \(scripts/extract-files.py --section "AP6398S Wi-Fi"\) into the git-ignored package/Evb10Wifi/wifi\_fw.inc; without the files the driver embeds nothing and level 2 of evb10-wifi stops after the bus switch.
- board.toml builds SoftwareAES and the Wi-Fi network side \(build-evb10-wifinet.py\), \[components\] include lists SoftwareAES, and configs/evb10\_display\_defconfig force-loads libEvb10WifiNet.a next to libEvb10Wifi.a; the SoC repository's rk3588.config keeps CONFIG\_XNU\_NATIVE\_AES=y \(the earlier comment claiming the RK3588 has no such device described the Qualcomm crypto engine, not this software implementation\).
- The audio codec driver is a step of board.toml \(build-evb10-drivers.py Evb10Audio\) and an archive of configs/evb10\_display\_defconfig, like the touch and Wi-Fi drivers; the display kernel with it built and booted \(docs/audio.md, evidence/audio-es8388-i2s0-20261101.txt\).
- board.toml carries evb10-audio=4 and evb10-audio-hal=1: the audio service and the audio server plug-in that the payload tool carries in the GPU addon \(uefi-evb10 merge-addons.py\); the command line is 930 of the 1000 bytes the loader keeps \(rk3588-dvfs=6 included\). usertest/build.sh in MaliMetal takes out/audio/Evb10Audio.driver/Evb10Audio into the owner trust bundle when it exists, so scripts/build-evb10-audio-hal.py runs before it \(docs/reproduce.md\).
- The frequency governors need no argument beyond the committed rk3588-dvfs=6: board.toml's comment for the cpu group now names what it starts \(the CPU and GPU governors and the over-temperature limit\) and what turns them off \(rk3588-dvfs=0 for everything, rk3588-gpu=0 for the GPU only\); the run v1 finding above predates them, the committed defaults now start the governors \(docs/power.md\).

### 完成条件

- Every source pin resolves, ./unixnu status lists the intended patch order, and both defconfigs materialise.

### 当前范围

- The format 2 configuration has been materialised and checked with status and tree; a full kernel build with it is recorded under Image assembly.

### 下一步

- Pin the Mali and Rk3588Emmc submodules to released commits when they change.

### 证据

- `source`: [Implementation and configuration described in this section](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/board.toml)
- `device`: [Boot with the committed default arguments \(run v1\): GPU 750 MHz by the cycle counter, Cortex-A76 cores at 2.23 GHz, 504 heavy command buffers took 14.9 ms \(median\) and 18.9 ms \(90th percentile\) from commit to completion, 52.6 frames per second with the finger down in the scripted swipes 3 to 11, no panic and no stalled GPU group in a 235 s capture](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/evidence/boot-v1-20261030.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; CAPTURE_SECS=235 EARLY_STOP=0 EXTRA_KERNEL_ARGS="evb10-touch-demo=120 mali-timeline=1" tools/xnu-probe/run-kernel.sh v1; python3 tools/xnu-probe/cb_table.py v1 --latency; python3 tools/xnu-probe/frame_phases.py v1</code>. Revision: `833f90fb52890090ad2bdd79285cc527b00d3ead`.

## 固件与启动 {#firmware}

`device-verified`

### 硬件与依赖

- edk2-rk3588 firmware built by uefi-evb10 \(SPI NOR image\), TF-A at EL3 with PSCI over SMC, UEFI GOP frame buffer and the Mali CSF firmware listed in proprietary-files.txt.

### 配置

- board.toml has no \[firmware\] section: the unixnu firmware step builds Mu-Silicium, and this board boots edk2-rk3588 built by uefi-evb10.
- payload.loader = firmware: DarwinBoot is inside the firmware volume.
- proprietary-files.txt pins mali\_csffw.bin by SHA-256; scripts/extract-files.py places it in .cache/firmware.

### 操作步骤

- Build the firmware in uefi-evb10 \(build.sh\) and flash or boot it as that repository describes.
- Run scripts/extract-files.py SOURCE, then the kernel step; scripts/build-mali-firmware.py writes package/Mali/mali\_csffw.inc.

### 开发经验

- The firmware hands the kernel EL1 with the MMU off and PSCI on SMC; secondary cores started by CPU\_ON arrive at EL2 and the SoC patch drops them to EL1.
- The firmware leaves the eMMC in HS400 and UART2 at 1.5 Mbaud; the drivers rely on both.
- proprietary-files.txt also lists the AP6398S Wi-Fi firmware and nvram from the Rockchip Android vendor tree as optional entries \(fw\_bcm4359c0\_ag.bin for the BCM4359 C0, revision 9, read over SDIO\); no driver loads them yet. The fw\_bcm4359c51a2\_ag.bin of that directory is a 4362a2 build and does not fit this module.

### 完成条件

- Firmware enters DarwinBoot, publishes the GOP frame buffer and keeps the memory reservations of the board.

### 当前范围

- Firmware and its boot flow are documented in uefi-evb10; this repository only pins the inputs.

### 下一步

- Record the firmware commit next to each image verification.

### 证据

- `source`: [Firmware inputs and their digests](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/proprietary-files.txt)
- `device`: [UEFI built from uefi-evb10 94ec4bd with the GPU rail at 0.75 V started from U-Boot's fastboot, the UniXNU menu booted the xnu entry, DarwinBoot published the 640x480 GOP frame buffer and kept the reserved regions of the device tree, boot services ended at 20.8 s and the kernel printed 'kprintf initialized' 0.4 s later \(run v1\)](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/evidence/boot-v1-20261030.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; CAPTURE_SECS=235 EARLY_STOP=0 EXTRA_KERNEL_ARGS="evb10-touch-demo=120 mali-timeline=1" tools/xnu-probe/run-kernel.sh v1</code>. Revision: `94ec4bd00d4d755623ce6cedd84172cbcd238dbd`.

## CPU 与中断 {#cpu}

`device-verified`

组件: `ArmCpu`, `ArmDTPlatform`.

### 硬件与依赖

- Four Cortex-A55 and four Cortex-A76 at affinities 0x000 to 0x700, GICv3 at 0xfe600000 with redistributors at 0xfe680000 \(128 KiB stride\), 24 MHz architected timer, PSCI over SMC.

### 配置

- The CPU, GIC and PSCI nodes come from the SoC dtsi \(rk3588-common dts/rk3588.dtsi\); the board DTS enables nothing extra.
- Kernel arguments sheng-smp=1, armcpu-self-ipi=1 and armcpu-mmio-sgi=0 select the secondary-core and IPI paths.
- cpumask=31 starts logical cores 0 to 4 only: the four Cortex-A76 cores, which the SoC device tree lists first, and the boot core, a Cortex-A55. sched-slowcpus=240 marks logical cores 4 to 7 \(the Cortex-A55 cores\) as slow for the scheduler.

### 操作步骤

- Compile dts/evb10.dts through ./unixnu tree and inspect /cpus, /psci and /arm-io/intc in the generated device tree.
- Boot and read the per-core entry lines on the serial console.

### 开发经验

- Inline assembly in this target goes through the Darwin assembler, where ';' starts a comment: "dsb ishst; msr icc\_sgi1r\_el1, %0; isb" assembled to a lone dsb. Earlier conclusions that the GIC ignores ICC\_SGI1R, that the A55 CNTFRQ is zero and that counters differ per core all came from this mistake and were withdrawn. The SoC repository carries the ArmCpu fix; scripts/build-evb10-kernel.sh refuses new inline assembly with ';'.
- With the fix all eight cores run and inter-processor interrupts go through ICC\_SGI1R\_EL1.
- XNU takes the lowest-numbered idle core and the device tree order numbers the cores, so the SoC device tree lists the Cortex-A76 cores first \(logical 0 to 3\) and the boot core, the fifth node, is found by matching its MPIDR with reg. The render server's encoding thread replays a command buffer in 4 ms on a Cortex-A76 and 11 to 14 ms on a Cortex-A55; sched-slowcpus keeps user-interface threads off an idle slow core while a fast one is free or can be preempted \(rk3588-slow-cores.patch, SoC repository\).
- The firmware's regulator table for the Cortex-A76 clusters was compiled as zeros \(the DSC used a macro that exists only in C\), so the clusters were clocked up without more voltage and calibrated at 1.78 GHz. With the table fixed in uefi-evb10 the A76 cores calibrate at 2.23 GHz \(the A55 at 1.86 GHz\); a Cortex-A76 integer loop takes 20 % less time, the 4 ms replay stays the same because it waits for memory.

### 完成条件

- Every enabled core reaches its entry checkpoint and receives timer and inter-processor interrupts.

### 当前范围

- CPU frequency and voltage are managed by the governor of the power area \(docs/power.md\); with rk3588-dvfs=0 the cores run at the clock the firmware left \(Cortex-A76 2.23 GHz measured under the 2.4 GHz request, Cortex-A55 1.86 GHz: the PVTPLL clocks follow the rail voltage, which the firmware leaves at 1.0 V\). No cluster-type properties are set, so the scheduler sees one cluster type, and the slow-core mask is a boot argument. cpumask=31 leaves three Cortex-A55 cores off.

### 下一步

- Decide whether to describe the A55 and A76 clusters to the scheduler.

### 证据

- `source`: [Board device tree on top of the shared SoC description](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/dts/evb10.dts)
- `device`: [The four Cortex-A76 cores reported running at 2230, 2230, 2223 and 2223 MHz with cpumask=31 and sched-slowcpus=240 on the command line; the render server's encoding thread ran on the Cortex-A55 core for 6 of the 504 heavy command buffers and on an A76 core for the other 498, with no panic in 235 s \(run v1\)](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/evidence/boot-v1-20261030.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; CAPTURE_SECS=235 EARLY_STOP=0 EXTRA_KERNEL_ARGS="evb10-touch-demo=120 mali-timeline=1" tools/xnu-probe/run-kernel.sh v1; python3 tools/xnu-probe/cb_table.py v1 --latency</code>. Revision: `833f90fb52890090ad2bdd79285cc527b00d3ead`.

## 内存与 DMA {#memory}

`device-verified`

### 硬件与依赖

- DRAM bank 0x1\_00000000 with size 0x1\_00000000 in the firmware memory map, 2 GiB owned window for the kernel, eMMC controller with 32-bit DMA.

### 配置

- dts/evb10.dts declares the memory node; payload.dram\_size must equal it.
- payload.adt.owned\_memory\_size = 0x80000000: DarwinBoot allocates this contiguous window from the low bank.

### 操作步骤

- Compare the firmware memory map, dts/evb10.dts and the owned window reported by DarwinBoot.
- Check DMA buffers of the eMMC driver against the 4 GiB address limit.

### 开发经验

- The 4 GiB bank above 4 GiB is the one large region without TF-A, OP-TEE, firmware or Rockchip carve-outs.
- A 256 MiB window left too little memory for the iPadOS userland; 2 GiB fits the firmware's low bank, 3 GiB was refused with Out of Resources. All pages sit below 4 GiB, where the eMMC DMA reaches.
- No IOMMU is used for the eMMC controller; the driver allocates a bounce window below 4 GiB.
- dts/evb10.dts also carries the wlan node that makes the userland start wifid \(a launchd job limited to devices with such a node in the Apple device tree\); it has no registers and no interrupts and is described in the network area.

### 完成条件

- All handoff regions are accounted for and every DMA engine works inside its allocated range.

### 当前范围

- Memory above the 2 GiB window is unused.

### 下一步

- Test a larger window by placing the kernel window above 4 GiB.

### 证据

- `source`: [Memory node and handoff window](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/dts/evb10.dts)
- `device`: [The hand-off kept cma, drm-logo, vendor-storage and ramoops reserved and gave the kernel a window of 0x80000000 bytes; the eMMC reads \(111 block requests, 0 failures\), the VOP2 scanout behind its IOMMU \(paging on\) and the Mali jobs ran inside it for 235 s without a fault or a panic \(run v1\)](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/evidence/boot-v1-20261030.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; CAPTURE_SECS=235 EARLY_STOP=0 EXTRA_KERNEL_ARGS="evb10-touch-demo=120 mali-timeline=1" tools/xnu-probe/run-kernel.sh v1</code>. Revision: `833f90fb52890090ad2bdd79285cc527b00d3ead`.

## 存储与根卷 {#storage}

`device-verified`

组件: `AppleKeyStoreState`.

### 硬件与依赖

- DesignWare MSHC at 0xfe2e0000, 8-bit eMMC, GPT with userdata at LBA 8459264 to 122142655 \(512-byte blocks\), SHNGROOT manifest image written by unixnu build userdata.

### 配置

- userdata.first\_lba, last\_lba and windows \(OS, SystemOS\) describe the root image.
- Kernel arguments: emmc=4, emmc-root-trust=1, emmc-systemos-union=1, emmc-data-mount=1, emmc-data-size=2048, emmc-data-persist=1.
- payload.adt.root\_match\_volume\_uuid names the OS volume; packed\_data\_ramdisk = false.

### 操作步骤

- Build with build-evb10-drivers.py Rk3588Emmc followed by bind-emmc-storage.py; regenerate scripts/data/evb10-storage-interface-audit.json with audit-evb10-storage.py when the kernelcache pin changes.
- scripts/peek-root-image.py reads the manifest of a userdata image without a board.

### 开发经验

- The driver subclasses the original IOBlockStorageDevice, so its archive is made by binding the object to the original code at audited addresses.
- Only the last 2049 MiB of userdata, the Data window, is ever written: the first start formats it and the kernel copies /private/var once, after which restarts mount it. Writes showed zero failures in the observed runs.
- A 256 MiB Data volume ran out of space \(ENOSPC\) and stalled SpringBoard; 512 MiB was enough to reach the lock screen, 2048 MiB is the configured size. vnode jetsam killed daemons until /defaults/kern.maxvnodes was set to 66560, which the OS profile now provides.
- The tools directory is split by owner: the thread-sample include belongs to the diagnostics area, while the userland-mounts include keeps, next to the mounts, the periodic process table and the screenshot over the serial line.
- The Data window is a persistent volume: the kernel keeps the tree and preferences of earlier boots \(evb10: Data: persistent volume, seeded by an earlier boot\) and, because a run ends by resetting the board, mounts the container after an unclean unmount by reloading its newest checkpoint.
- The addon mount is generalised \(evb10\_ngpu\_mount\): a second bindfs union of /private/var/ngpu/audio over /System/Library/Audio/Plug-Ins/HAL \(boot argument evb10-audio-hal=1, after the Metal plug-in's mount\) and an mmap grant for /System/Library/Audio/Plug-Ins/HAL/Evb10Audio.driver/, the same as for the Metal bundle. Observed on the board: the mount reaches stage 5 \(the sealed BuiltinAudioPlugin.driver and Evb10Audio.driver/Info.plist both visible\) and the audio server loads the plug-in \(evidence/audio-ipados-20261101.txt\).

### 完成条件

- The root volume mounts read-only from the OS window and the Data volume mounts read-write across restarts.

### 当前范围

- Only eMMC is supported; PCIe NVMe is not used. Every run ends by resetting the board, so the Data container has always been mounted after an unclean unmount; a mount after an orderly shutdown was not exercised.

### 下一步

- Repeat the persistence check after a clean unmount, which no run has exercised.

### 证据

- `source`: [Binding of the eMMC block device to the original storage class](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/scripts/bind-emmc-storage.py)
- `device`: [The SystemOS window is published read-only \(111 block requests, 0 failures\), the root volume of the OS window is accepted read-only, the 2 GiB Data window is published writable and /private/var mounts on it as a persistent volume. Across 56 boots of 2026-10-30, each run ending by a board reset, the transaction id of the Data container rose from 10018 to 16586 and 47 of the boots recovered it after an unclean unmount \(run v1 and the table in the log\)](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/evidence/boot-v1-20261030.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; CAPTURE_SECS=235 EARLY_STOP=0 EXTRA_KERNEL_ARGS="evb10-touch-demo=120 mali-timeline=1" tools/xnu-probe/run-kernel.sh v1</code>. Revision: `833f90fb52890090ad2bdd79285cc527b00d3ead`.

## 显示 {#display}

`device-verified`

组件: `GopFramebuffer`.

### 硬件与依赖

- VOP2 with the Esmart3 window on the DSI panel, 1080x1920; UEFI GOP frame buffer; original IOMobileFramebufferLegacy bound to NativeLegacyDisplay.

### 配置

- Kernel arguments evb10-vop=2, evb10-vop-es2=1, evb10-fb-w=1072, evb10-fb-h=1904, offline-legacy-\* and sheng-vsync=60.
- evb10\_display\_defconfig links the display archive and the link stubs.

### 操作步骤

- Build both passes with scripts/build-evb10-kernel.sh and boot with a monitor or panel attached.

### 开发经验

- The firmware assigns Esmart3 to VP2; writing back the layer-mixer policy of U-Boot makes the window take effect.
- Underruns \(POST\_BUF\_EMPTY\) on the panel path came from the firmware's HDMI0 window \(Esmart2\) fetching at the same time; disabling it with evb10-vop-es2=1 gave zero underruns.
- A frame size of exactly 1080x1920 makes backboardd render the 1242x2208 geometry of other devices and ask for scaling, which the full-frame swap validation rejects; 1072x1904 avoids it.
- Tearing in scanout was removed by waiting for the GPU jobs of a frame before the page flip.
- The kernel prints the gaps of every moving window of frames \(evb10: display gaps\), on the clock of the Metal plug-in's command-buffer timeline, so the hitches of a swipe can be matched with the command buffers. A screenshot over the serial line \(evb10-shot-img\) reads the live frame buffer row by row for several seconds, so moving content tears in it; compare static frames only.
- The late probe of package/LegacyDisplayProbe.cpp also calls evb10\_wifi\_start \(package/Evb10Wifi\), next to the touch and Mali starts; it does nothing unless evb10-wifi=1.
- The display probe also starts package/Evb10Audio \(evb10-audio=N\), after the touch and Wi-Fi drivers; the display kernel's archive list gained libEvb10Audio.a and the display kernel booted with it \(docs/audio.md\).
- The display probe \(package/LegacyDisplayProbe.cpp\) is also where the board starts its late drivers, among them the SoC's frequency governor \(rk3588\_dvfs\_start, power area\); evb10\_display\_defconfig force-loads libRk3588Dvfs.a next to the touch, Wi-Fi, audio and Mali archives, and board.toml builds it before them.

### 完成条件

- The panel shows the lock screen without flicker or tearing.

### 当前范围

- Frame rate while scrolling is limited by how fast a heavy frame is encoded and drawn against its deadline \(see GPU\). The panel timing is the firmware's.

### 下一步

- Shorten the encoding of heavy frames \(see GPU\), take screenshots from a snapshot, and move presentation to vsync interrupts.

### 证据

- `source`: [VOP2 scanout presenter](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/package/Evb10Display/NativeLegacyDisplay.cpp)
- `device`: [Checked by hand on the board \(reported 2026-10-30\): the panel works normally](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/evidence/boot-v1-20261030.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; tools/xnu-probe/run-kernel.sh TAG, then look at the panel</code>. Revision: `833f90fb52890090ad2bdd79285cc527b00d3ead`.
- `device`: [The kernel frame buffer \(1072x1904\) is scanned out by VOP2 behind its IOMMU and the display gap log shows 16.6 ms between frames: 52.6 frames per second with the finger down in the scripted swipes 3 to 11 \(run v1\)](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/evidence/boot-v1-20261030.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; CAPTURE_SECS=235 EARLY_STOP=0 EXTRA_KERNEL_ARGS="evb10-touch-demo=120 mali-timeline=1" tools/xnu-probe/run-kernel.sh v1; python3 tools/xnu-probe/frame_phases.py v1</code>. Revision: `833f90fb52890090ad2bdd79285cc527b00d3ead`.

## 输入 {#input}

`device-verified`

### 硬件与依赖

- Goodix GT1158 on I2C5, polled; coordinate grid 720x1280 on a 1080x1920 panel.

### 配置

- Kernel arguments evb10-touch=1, evb10-touch-xmax=720, evb10-touch-ymax=1280, evb10-hid=1, evb10-hid-input=1, sheng-touch-hid=1.
- evb10-touch-khz sets the I2C5 clock \(100 to 400, default 100\). evb10-touch-demo=SECS plays scripted gestures without a finger from SECS seconds after the first poll \(a swipe up, then left and right swipes of 0.8 s every 7 s\), which is how the frame rate is measured without a person.

### 操作步骤

- Boot and watch the evb10: touch lines on the console; touch the panel and check the pointer in SpringBoard.

### 开发经验

- The controller reports a configured 800x480 but delivers X 9..696 and Y 10..1270: the real grid is 720x1280.
- The input device is one HID device on the IOHIDResource; the original IOHIDEventDriver attaches to it and feeds backboardd.
- The poll runs as a thread call at priority 93 about every 11.5 ms and the master busy-waits: at 100 kHz one tick costs 535 us on average \(the slowest tick of a window of 1000 was 1.2 to 6.4 ms when it was preempted\), about 4.6 % of a fast core; at 400 kHz it costs 150 us \(191 us at most\). The kernel prints the average and the maximum every 1000 ticks.
- At 400 kHz the bus scan still sees 0x14 and 0x5d, reads Goodix product id 1158 and ten touch points, and counts no bus errors.
- evb10-touch-script=SECS plays taps and swipes from a script compiled in from the git-ignored package/Evb10Touch/touch\_script.inc \(scripts/gen-wifi-touch-script.py writes it from the join file\), to drive screens without a person; with evb10-ps and evb10-shot-img the serial log carries screenshots. On the board the lock screen needs two swipes up \(the first is always lost\); taps then open Settings, the Wi-Fi pane, a network's row, the password sheet and its keyboard, so the Settings Wi-Fi flow was checked this way \(docs/network.md, checkpoint 7\). The taps that earlier seemed to miss were Settings failing to start \(see GPU\). One launch in nine of the clean runs \(t45\) showed no Preferences process after the Dock tap and was not explained; a row that disappears from a list because the signal is weak makes a fixed tap land on the next row.
- The touch tick line is followed by a line from the event driver \(package/Evb10Hid\): wrapper installed, contacts begun, contacts at an edge, skipped events and reports with two or more fingers.

### 完成条件

- Touch coordinates map to the panel and SpringBoard reacts.

### 当前范围

- No keyboard, buttons or pen; the controller is polled every 10 ms. The 400 kHz setting was checked on the bus only: a finger on the panel at that speed was not tried.

### 下一步

- Use the controller interrupt instead of polling.

### 证据

- `source`: [I2C master and touch controller driver](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/package/Evb10Touch/Evb10Touch.cpp)
- `device`: [With evb10-touch-khz=400 the poll tick took 150 us on average and 191 us at most over 1000 ticks, the I2C scan found 0x14 and 0x5d, the controller reported product id 1158, and there were no bus errors \(run tk4\)](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/evidence/touch-400khz-tk4-20261030.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; EXTRA_KERNEL_ARGS="evb10-touch-khz=400" tools/xnu-probe/run-kernel.sh tk4</code>. Revision: `11d08ffb699a5a3e8140b27d0dc943ff5b129986`.
- `device`: [Checked by hand on the board \(reported 2026-10-30\): the touch screen works normally](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/evidence/boot-v1-20261030.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; tools/xnu-probe/run-kernel.sh TAG, then touch the screen</code>. Revision: `833f90fb52890090ad2bdd79285cc527b00d3ead`.
- `device`: [The Goodix GT1158 answered at 0x14 on I2C5 at 100 kHz \(product id 1158, axes 720x1280 mapped to 1080x1920\), a poll tick took 536 us on average, and 352 HID reports by t+130 s drove the scripted swipes on the home screen \(run v1\)](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/evidence/boot-v1-20261030.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; CAPTURE_SECS=235 EARLY_STOP=0 EXTRA_KERNEL_ARGS="evb10-touch-demo=120 mali-timeline=1" tools/xnu-probe/run-kernel.sh v1</code>. Revision: `833f90fb52890090ad2bdd79285cc527b00d3ead`.

## GPU {#gpu}

`device-verified`

### 硬件与依赖

- Mali-G610 \(Valhall CSF\) at 0xfb000000, CSF firmware from proprietary-files.txt, MaliMetal user-space stack \(PanVK, metal2vulkan, Metal plug-in\).

### 配置

- Kernel arguments mali=8 and mali-metal=1; evb10-gpu-addon=1 makes the payload tool carry the Metal plug-in.
- mali-pll and mali-div choose the clock source and the divider minus one \(default mali-pll=1 mali-div=1: CPLL 1500 MHz over two, 750 MHz\); mali-npll=MHz \(400 to 1100\) retunes NPLL for source 3; mali-epri sets the priority of the encoding thread; mali-aflush=1 flushes surfaces asynchronously. The UEFI build option GPU\_RAIL\_UV sets the GPU rail in microvolts \(default 750000\).
- package/Mali is a submodule; scripts/build-mali-firmware.py generates the firmware include.

### 操作步骤

- Provide the firmware, build the kernel, then build the user-space stack from MaliMetal and the add-on it describes.

### 开发经验

- The stack composites the iPadOS lock screen on the Mali: backboardd, AGXAccelerator, NativeMaliMetal, metal2vulkan, PanVK and the Mali driver.
- PanVK counts a colour attachment with write mask 0 as written; a Mesa patch in MaliMetal fixes the black rectangle behind the lock screen clock.
- Scrolling the home screen with the frame-rate arguments, now the defaults of board.toml, gets about 50 frames per second in the steady state on the board, 58 at best; the scripted swipes 3 to 11 of run v1 gave 52.6 frames per second with the finger down and 57.5 at best.
- The heavy render passes scale with the GPU clock \(84.9, 28.4 and 22.5 ms at 198, 594 and 750 MHz\). The wallpaper pass was metal2vulkan's bit-exact YCbCr filter \(about 570 instructions a sample\), not memory: the device's own linear filter takes it from 22.5 to 7.9 ms.
- PanVK let a draw kill the fragments of earlier draws only if it wrote every bound colour attachment, which CoreAnimation's passes never do \(they bind a write-masked memoryless second one\). A Mesa patch in MaliMetal lets a draw kill when its write set covers the earlier draw's: a matrix of nine write-set pairs on the board shows the pixels only the earlier draw writes never differ, and the median command-buffer GPU time falls from 14.1 to 9.7 ms.
- What is left of a heavy frame is on the CPU: the render server's encoding thread replays the command buffer \(4 ms on a Cortex-A76, 11 ms on an A55\) and submits it \(1.4 ms\) before the GPU starts, 0.7 ms after the submit returns.
- A heavy command buffer \(50 draws or more\) has to go from commit to completion in about 19.3 ms to be shown on the second vsync after it. At 750 MHz the 504 of run v1 took 14.9 ms \(median\) and 18.9 ms \(90th percentile\) and 8.7 % were over 19.3 ms; at 1 GHz \(run v2\) 12.7 and 15.6 ms and 2.5 % \(1.6 % in an earlier run\); the median GPU time of a heavy command buffer is 10.1 ms at 750 MHz and 7.9 ms at 1 GHz.
- The encoding thread landed on a Cortex-A55 for 8 % of the heavy command buffers \(replay 11 to 14 ms instead of 4 ms\), the main source of late frames. Listing the Cortex-A76 cores first, raising the thread's priority to 50 \(mali-epri\) and keeping user-interface threads off idle slow cores \(sched-slowcpus\) together bring that to 0.5 to 1.8 %; neither of the last two helps alone.
- mali-npll=1000 retunes NPLL before the GPU is switched onto it and needs the GPU rail at 0.85 V \(vendor operating points: 0.75 V up to 800 MHz, 0.85 V for 1 GHz\), so the firmware is built with GPU\_RAIL\_UV=850000; 750 MHz at 0.75 V is the default. A 12-minute capture at 1 GHz \(81 scripted swipes, 3553 heavy command buffers\) ended without a panic or a stalled group and with vkpipe failed=0 throughout.
- From the start of a swipe to the first command buffer takes about 60 ms for a left swipe and 150 to 170 ms for a right swipe at every GPU clock. The CPU times of the processes suggest the Today View widgets are rendered on each right swipe \(WidgetRenderer\_Default used 0.17 s of CPU per 13 s of swiping against 0.003 s idle\), but no thread stack was taken to confirm it.
- A host buffer \(BO\_CREATE\_HOST\) over a file's pages, such as an application's mapped assets that the render server shares, is copied instead of pinned: the pin holds the file object's activity count, and unmapping the file's last mapping waits for it in the thread that retires the GPU work holding the pin, so the render server stopped at the first application launch \(run t17\). The Mali driver's sandbox grant and the plug-in's process list also name iconservicesagent and Preferences: without a Metal device the icon agent of Settings falls back to OpenGL ES, which this device has none of, and crashes in CI::GLContext::init \(run t19\). A build without these two changes starts Settings and leaves its main thread waiting in CASGetDisplays for the render server \(runs t39 to t41\); with them Settings is on the screen within 4 seconds of the tap \(runs t35 to t38, t42 to t44\).

### 完成条件

- The lock screen and its animations render on the Mali at a steady frame rate.

### 当前范围

- No DVFS: the GPU clock is fixed \(750 MHz by default at the 0.75 V the firmware sets; 1 GHz with a firmware built for 0.85 V, not tried on the 0.75 V rail\); no interrupt-driven completion \(waits poll\), at most eight groups. At 750 MHz 8.7 % of the heavy command buffers miss their 19.3 ms deadline \(1.6 to 2.5 % at 1 GHz\) and a right swipe starts about 100 ms later than a left one. The panel was checked by hand and works normally \(see Display\).

### 下一步

- Submit a command buffer while it is still being replayed, find what SpringBoard does in the 100 ms after a right swipe starts, and move completion to the GPU interrupts.

### 证据

- `source`: [Mali driver source is the package/Mali submodule](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/.gitmodules)
- `device`: [The 1 GHz steps of docs/reproduce.md with a firmware built from uefi-evb10 94ec4bd with GPU\_RAIL\_UV=850000 \(run v2\): the console shows npll 1000000 kHz locked, the cycle counter reads 1000 MHz, 511 heavy command buffers took 12.7 ms \(median\) and 15.6 ms \(90th percentile\), 2.5 % were over 19.3 ms, 53.8 frames per second with the finger down in swipes 3 to 11, no panic and no stalled GPU group in 235 s](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/evidence/gpu-1ghz-v2-20261030.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; env -i HOME=$HOME USER=$USER PATH=/usr/local/bin:/usr/bin:/bin GPU_RAIL_UV=850000 ./build.sh &amp;&amp; tools/stub/build.sh &amp;&amp; CAPTURE_SECS=235 EARLY_STOP=0 EXTRA_KERNEL_ARGS="mali-pll=3 mali-div=0 mali-npll=1000 evb10-touch-demo=120 mali-timeline=1" tools/xnu-probe/run-kernel.sh v2; python3 tools/xnu-probe/cb_table.py v2 --latency</code>. Revision: `833f90fb52890090ad2bdd79285cc527b00d3ead`.
- `device`: [Boot with the committed default arguments: the Mali at 750 MHz \(cycle counter\) composited the interface for backboardd and SpringBoard, vkpipe n=76 failed=0, 504 heavy command buffers took 14.9 ms \(median\) and 18.9 ms \(90th percentile\) from commit to completion, 52.6 frames per second with the finger down in the scripted swipes 3 to 11, no panic in 235 s \(run v1\)](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/evidence/boot-v1-20261030.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; CAPTURE_SECS=235 EARLY_STOP=0 EXTRA_KERNEL_ARGS="evb10-touch-demo=120 mali-timeline=1" tools/xnu-probe/run-kernel.sh v1; python3 tools/xnu-probe/cb_table.py v1 --latency; python3 tools/xnu-probe/frame_phases.py v1</code>. Revision: `833f90fb52890090ad2bdd79285cc527b00d3ead`.

## 网络 {#network}

`device-verified`

### 硬件与依赖

- AP6398S module \(Broadcom BCM4359 C0, Wi-Fi on SDIO 3.0 and Bluetooth on UART9\) behind the DW-MSHC at 0xfe2d0000 \(SPI 204\); WL\_REG\_ON = GPIO0\_C4, 32.768 kHz low-power clock from the HYM8563 RTC CLKOUT, WL\_HOST\_WAKE = GPIO0\_B2 \(stock device tree\).
- Firmware fw\_bcm4359c0\_ag.bin and nvram\_ap6398s.txt from the Rockchip Android vendor tree, listed as optional entries in proprietary-files.txt; the network to join \(SSID, passphrase\) in the local, git-ignored .cache/firmware/join.txt.
- The catalog has no SDIO or Broadcom component \(Ath12kWifi is Qualcomm PCIe\); the protocol follows Linux brcmfmac; package/Evb10Wifi/nw\_abi.h is the interface of Ath12kWifi and WifiNet.cpp is adapted from UniXNU-sheng.

### 配置

- package/Evb10Wifi is built by build-evb10-drivers.py Evb10Wifi and Evb10WifiNet \(steps of board.toml; build-evb10-wifinet.py removes the static initializer from the WifiNet.cpp object and archives it\), linked by configs/evb10\_display\_defconfig only, and started by the display probe when the boot argument evb10-wifi=N is given \(not a default\): 1 identify, 2 download and start the firmware, 3 talk to it and scan, 4 join the network of the join file and run a self-test \(DHCP, ARP, ping\), 5 join and serve the interface en0 to the OS without the self-test. The images and the join file are embedded by build-wifi-firmware.py \(output git-ignored\).
- The bus: sdiom0 pins on function 2 through GPIO2A\_IOMUX\_SEL\_H / GPIO2B\_IOMUX\_SEL\_L in BUS\_IOC, WL\_REG\_ON high, identification at 400 kHz 1-bit from xin24m, then CCCR 0x07 = 0x82 \(4-bit\), CTYPE 1, CLKSEL\_CON\(172\) = 0x5c \(GPLL / 24, about 24.75 MHz at the card\), function 1 block size 64, function 2 enabled \(IOEx = 6\) after the firmware starts.
- The network side needs the software AES of the board configuration \(CONFIG\_XNU\_NATIVE\_AES=y in the SoC repository's rk3588.config and the SoftwareAES component\) so that IOKit goes quiet; see Image assembly.
- evb10-wifi-join=0 \(with 4 or 5\) does not join the join file's network at boot, so the join comes from the OS \(Settings\); 2 is the same and the scans list only the join file's network, which puts it in a fixed row of the Settings list for scripted taps.

### 操作步骤

- Fill UniXNU-evb10/.cache/firmware: scripts/extract-files.py &lt;vendor dir&gt; --section "AP6398S Wi-Fi" for the images, and a join.txt with the SSID on the first line and the passphrase on the second.
- Build with scripts/build-evb10-kernel.sh, then cd uefi-evb10 &amp;&amp; EXTRA\_KERNEL\_ARGS="evb10-wifi=5" CAPTURE\_SECS=200 EARLY\_STOP=0 tools/xnu-probe/run-kernel.sh TAG and read the evb10: wifi and wifi-net lines of runs/TAG.kernel.log \(level 3 lists access points, level 4 runs the self-test, level 5 lets the userland use en0\).
- U-Boot: reset the board \(uefi-evb10 tools/board/hw-reset.sh reset\) and run uefi-evb10 tools/board/sdio-probe.py --enter for the identity checkpoint.
- Settings: cd UniXNU-evb10 &amp;&amp; scripts/gen-wifi-touch-script.py forget \(or join, info, rejoin\), rebuild the kernel, then cd uefi-evb10 &amp;&amp; EXTRA\_KERNEL\_ARGS="evb10-wifi=5 evb10-wifi-join=2 evb10-ps=12 evb10-touch-script=99 evb10-shot-img=1 evb10-shot-scale=2" CAPTURE\_SECS=420 tools/xnu-probe/run-kernel.sh TAG and python3 tools/xnu-probe/shot2png.py runs/TAG.kernel.log OUTDIR \(the passphrase of the join file can show in a screenshot if a tap misses its row: keep the images out of commits\).

### 开发经验

- The module answers: CMD5 returns OCR 0xb0ffff00 \(3 IO functions\), the CIS manufacturer ID is 02d0:4359 and ChipCommon CHIPID is 0x17294359, chip 0x4359 revision 9 \(C0\), with the ALP clock available after the request \(CHIPCLKCSR 0x48\).
- The IOMUX registers of GPIO2 are in BUS\_IOC \(0xfd5f8044 and 0xfd5f8048\). The offsets of the rk3588\_ds\_regs and rk3588\_p\_regs tables of pinctrl-rockchip.c are drive strength and pull in other IOC blocks; written as function selects they leave the SDIO CLK pad low and the card never answers CMD5.
- The HYM8563 CLKOUT \(the module's low-power clock\) is enabled after reset, so U-Boot and the kernel need no setup for it.
- CMD53 in byte mode with a count above the function 1 block size answers R5 OUT\_OF\_RANGE and a data timeout and leaves the host FIFO full; set the block size \(64\), use block mode for 64 bytes and up and reset the FIFO before each transfer.
- The firmware of the C0 module starts with the reset values of SDIO\_CON0/1 at about 25 MHz in 4-bit mode: after the CR4 release the HT clock is available in 34 ms and function 2 ready in 232 ms, with the images written in 90 ms and read back identical.
- The firmware \(wl0 9.87.51.11.102\) answers SDPCM/BCDC on function 2 with bus:txglom 0 and mpc 0; cur\_etheraddr is the module's OTP address, not the default in the nvram. An escan lists 35 to 43 networks of both bands in 1.5 to 1.7 s.
- Without WLC\_SET\_INFRA 1 / WLC\_SET\_AP 0 before WLC\_UP a join makes an ad-hoc network \(a link-up event with a random BSSID and no key exchange\). With them, bsscfg:wpa\_auth 0x80, wsec 4, sup\_wpa 1 and WLC\_SET\_WSEC\_PMK, the firmware's supplicant keys the link \(event 46 status 6\) 2.1 s after the join command and the driver's own DHCP, ARP and ping through the BCDC data path work.
- SDPCM transmit is credit based; under a bulk download the chip's credits arrive slowly and a 32-frame queue without waiting dropped 12006 of 38850 frames. The queue holds 128 frames and if\_output waits up to 40 ms for room: 19 of 2315 frames were given up in a run that received 8 MB; the 105 MB case was not repeated.
- en0 is an ifnet made with IFNET\_INIT\_LEGACY \| IFNET\_INIT\_NX\_NOAUTO and bpf\_attach; IONetworkStack, IO80211Controller and IO80211Interface are classes registered late \(static initializer run between OSMetaClass::preModLoad and postModLoad\). With it the userland's DHCP client, DNS and TCP work: one run received 105 MB in 240 s \(best 10 s interval 34 Mbit/s\).
- The userland's interface namer and wireless daemon wait for IOKit to go quiet. The original AppleImage4 matches on /defaults and its start waits without a timeout for IOAESAccelerator, which nothing provided, so the registry never went quiet \(the first lease came at 330 s\); with SoftwareAES IOKit is quiet 26 s into the boot log.
- With a network the system downloads assets in the background and the 2 GiB Data window \(about 250 MB free after a normal boot\) fills within minutes \(ENOSPC for those daemons; the next boot had its free space back\).
- wifid is a launchd job limited to devices whose device tree has a node named wlan \(\_LimitLoadToDeviceTree\), so it never started on this board; dts/evb10.dts now carries a wlan node \(no registers, no interrupts\), and from run set3 on wifid is in the process table at about 75 s and sends Apple80211 requests to en0.
- The daemon asks for the current network \(103\) while the link is up, and the file's join leaves the access point out of the BSS list, so the answer is now built from the link state; the property lists \(383\) and two flags \(470, 471\) it sets at every state change are accepted. The channels-info structure \(207\) and a few other types are still refused.
- Scripted touches \(evb10-touch-script, runs set4 to set10\) unlocked the screen with two swipes up \(the first one is always lost\) but taps on the Settings icon did not open the app; that was Settings failing to start \(a Metal device for iconservicesagent and Preferences, and the copy of file-backed host buffers in the Mali driver\), not the taps.
- Settings drives the whole join through the driver: the Wi-Fi pane lists the network, the password sheet takes the typed passphrase, Join arrives as an association request \(type 20, cipher 6: the 32-byte key the daemon derived from the SSID and passphrase\), the firmware joins 1.7 s later, DHCP binds about 3 s after that, and the check mark replaces the spinner when IO80211InterfaceIPConfigurationBusy goes false 4.5 to 9.5 s after the link \(runs t37, t42, t43\). Forget This Network arrives as a disassociate 0.6 s after the confirmation tap and the pane returns to the list \(run t43\).
- Settings has a Wi-Fi row only if MobileGestalt's wifi capability is true, and in a virtual machine \(vmm-present\) it reads that from the property mac-address-wifi0 of /chosen; WifiNet.cpp sets it from the module's address once the firmware reports it. MobileGestalt caches the answer on the Data volume at the first boot, so a Data volume that booted without the property keeps answering false until the cache file is deleted or the volume rebuilt.
- The spinner stayed 64 s \(run t36\) because the address configuration's ARP monitor reads the router's replies through /dev/bpf and the interface gave the packet filter no frames: an ifnet that is not a stock Ethernet driver must supply set\_bpf\_tap and call it with every frame in both directions, Ethernet header included. With the tap the busy flag clears in 4.5 to 9.5 s. The firmware also passes only the multicast groups it was told about, so allmulti is set to 1; IPv6 neighbour discovery then arrives.
- 5 GHz does not work yet. After a successful join to the 2.4 GHz access point \(-80 dBm\) the firmware roamed to the same network's 5 GHz access point \(event 19\) and the TCP payload counter then rose by 96 bytes in 30 s, from 188826 to 188922 \(run t42\); a join after Forget This Network went to the 5 GHz access point and its association was not acknowledged \(event 7 status 5\), so the pane said "Unable to join the network" \(run t43\). The scan lists the 2.4 GHz access point at -44 dBm in one run and -80 dBm in another, and the firmware's link reading is -80 dBm. The CLM blob is not loaded \(the vendor's is data 1.39.1 of 2021, the firmware's built-in one 9.7.7 of 2023\) and the nvram has ccode=0; neither was tried. Locking the radio to 2.4 GHz with WLC\_SET\_BAND \(tried as a boot argument and removed again\) did not help: the scans then listed only 2412 MHz entries, but both joins of run t46 ended after 0.5 s with event 0 status 3 \(no network found\), where the first joins of runs t36, t37, t42 and t43, without the lock, took 1.7 to 1.8 s and succeeded.

### 完成条件

- Device-verified for the join and the data path: a scan lists access points, a WPA2-PSK join carries traffic, and iPadOS's own DHCP client, DNS and TCP use the interface for a whole run without a panic. wifid is attached to en0 and answered, and the Settings Wi-Fi pane lists the network, joins it with a typed passphrase, shows the address and forgets it \(scripted touches and screenshots, runs t37 to t43\); throughput was not looked at.

### 当前范围

- Opt-in with evb10-wifi=N and a network from the local join file; the committed arguments leave the module off. One module and one 2.4 GHz network at -80 dBm, in a series of runs; 5 GHz, WPA3 and open networks were not tried. The SDIO host is polled at about 25 MHz with no DMA and no SPI 204 interrupt; WL\_HOST\_WAKE and power save are not used; the Settings pane was checked with the passphrase of a WPA2-PSK network on one test router: open networks, WPA3, hidden networks and whether a joined network is remembered across boots were not tried, and the pane's Private Wi-Fi Address is not programmed into the firmware; 5 GHz fails \(a roam to it stops the traffic, a join to it is not acknowledged\) so the pane can report "Unable to join" when the firmware picks the 5 GHz access point; the CLM blob is not loaded; Bluetooth is not part of this area.

### 下一步

- Interrupt \(SPI 204 and the in-band interrupt\), the host's DMA and 50 MHz so the data path no longer polls, and 5 GHz. First find why 5 GHz fails \(CLM blob, nvram regulatory settings, TX power\); then an open network and WPA3 from the pane.

### 证据

- `device`: [From a freshly reset board at the U-Boot prompt, the AP6398S answered on SDIO: OCR 0xb0ffff00 with 3 IO functions, RCA 1, CIS manufacturer 02d0:4359, ChipCommon CHIPID 0x17294359 \(BCM4359 revision 9\), CHIPCLKCSR 0x48; the CLK pad toggled in 7 of 10 samples.](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/evidence/wifi-sdio-id-20261030.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; tools/board/hw-reset.sh reset; sleep 25; python3 tools/board/sdio-probe.py --enter --log LOG</code>. Revision: `0d553069b92a5181ea5f41250f755e8aba96cda0`.
- `device`: [The kernel \(display pass, evb10-wifi=1\) powered the AP6398S and read OCR ffff00 with 3 IO functions, RCA 1, MANFID 02d0:4359 and ChipCommon CHIPID 17294359 \(BCM4359 revision 9\) 0.43 s after the driver started; the CLK pad toggled in 10 of 20 samples and the 120 s capture ran on to SpringBoard without a panic.](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/evidence/wifi-kernel-id-20261030.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; CAPTURE_SECS=120 EARLY_STOP=0 EXTRA_KERNEL_ARGS="evb10-wifi=1" tools/xnu-probe/run-kernel.sh wifi1</code>. Revision: `1396eba965fe210555e3c6e24b4dd720eaf15e65`.
- `device`: [The kernel \(display pass, evb10-wifi=2\) switched the AP6398S to 4 bits at about 25 MHz, halted the ARM CR4, wrote fw\_bcm4359c0\_ag.bin \(673934 bytes\) at 0x160000 and the nvram \(4896 bytes\) at 0x23ece0 with CMD53 in 90 ms, read both back identical in 82 ms, released the core, and saw the HT clock available after 34 ms \(CHIPCLKCSR 0xd0\) and function 2 ready \(IORx 0x06\) 232 ms after the release; the 120 s capture ran on to SpringBoard without a panic.](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/evidence/wifi-firmware-run-20261030.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; CAPTURE_SECS=120 EARLY_STOP=0 EXTRA_KERNEL_ARGS="evb10-wifi=2" tools/xnu-probe/run-kernel.sh wifi3</code>. Revision: `32ab3cd072d1447a06f714f593792675d7328242`.
- `device`: [The firmware answered SDPCM/BCDC \(version 9.87.51.11.102, CLM API 15.0, scan version 1\), accepted WLC\_UP and listed 35, 38 and 43 networks of both bands in three escans of 1.5 to 1.7 s \(run wifi5\).](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/evidence/wifi-scan-20261030.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; EXTRA_KERNEL_ARGS="evb10-wifi=3" CAPTURE_SECS=100 EARLY_STOP=0 tools/xnu-probe/run-kernel.sh wifi5</code>. Revision: `7552f8602bf3ca5022e917501bf5ea7b4b40ae93`.
- `device`: [The firmware's supplicant joined a WPA2-PSK network 2.1 s after the join command \(events 3, 16, 7, 46 status 6\); the driver's own DHCP bound 3.1 s later, resolved the router and received 4 of 4 ping replies, 11 frames sent with none failed or dropped \(run wifi9b, signal -81 dBm on 2.4 GHz\).](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/evidence/wifi-join-20261030.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; EXTRA_KERNEL_ARGS="evb10-wifi=4" CAPTURE_SECS=100 EARLY_STOP=0 tools/xnu-probe/run-kernel.sh wifi9b</code>. Revision: `7552f8602bf3ca5022e917501bf5ea7b4b40ae93`.
- `device`: [iPadOS used the module as en0: IOKit quiet 26 s into the boot log, the userland's DHCP client had its address by the 83 s status line, then DNS and 36 outgoing TCP connections \(run wifi19, 200 s, no panic\); an earlier 240 s run \(wifi17\) received 105 MB of TCP payload through en0 with the link up throughout.](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/evidence/wifi-os-20261030.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; EXTRA_KERNEL_ARGS="evb10-wifi=5" CAPTURE_SECS=200 EARLY_STOP=0 tools/xnu-probe/run-kernel.sh wifi19</code>. Revision: `7552f8602bf3ca5022e917501bf5ea7b4b40ae93`.
- `device`: [wifid started with the wlan node and sent its Apple80211 requests to en0 \(run set5, evb10-wifi=5, no panic\); two swipes unlocked the screen and taps on the Settings icon did not open the app \(run set9\); the Wi-Fi pane itself was not seen](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/evidence/wifi-settings-20261031.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; EXTRA_KERNEL_ARGS="evb10-wifi=5 evb10-ps=12 evb10-shot-img=1 evb10-shot-scale=2 evb10-touch-script=125" CAPTURE_SECS=300 tools/xnu-probe/run-kernel.sh set9</code>. Revision: `760112b407ec0823fef97caeb69733434580b85e`.
- `source`: [Hardware, the six checkpoints, findings, firmware, what is missing and the next step](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/docs/network.md)
- `device`: [Settings on the board, driven by scripted touches and read from screenshots in the serial log: the Wi-Fi row, the network list, the password sheet with the typed passphrase, Join \(the firmware joined 1.7 s later, DHCP bound, the busy flag went false 4.5 to 9.5 s after the link and the row showed the check mark\), Forget This Network \(disassociate 0.6 s after the confirmation, the pane back to the list\), and a join to the 5 GHz access point that was not acknowledged and ended in "Unable to join the network" \(runs t36, t37, t42, t43; no panic\); also the two joins of run t46 with the radio locked to 2.4 GHz, which found no network and made the lock useless](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/evidence/wifi-settings-pane-20261031.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; EXTRA_KERNEL_ARGS="evb10-wifi=5 evb10-wifi-join=2 evb10-ps=12 evb10-touch-script=99 evb10-shot-img=1 evb10-shot-scale=2" CAPTURE_SECS=480 tools/xnu-probe/run-kernel.sh t43</code>. Revision: `bd28d8a3de879530bd8afaa36c15d6d3299be54e`.

## 音频 {#audio}

`implemented`

### 硬件与依赖

- The board's es8388-sound card: an Everest ES8388 at 0x11 of I2C7 \(0xfec90000\) and the I2S0 controller \(0xfe470000, power domain 38\) as its digital side, MCLK 12.288 MHz from the SoC, from the stock device tree; the clock tree and register layout of the vendor kernel \(clk-rk3588.c, rockchip\_i2s\_tdm.c, es8328.c\).
- UniXNU-sheng's audio \(ShengAudioService, ShengAudioPlugIn.c, ShengAudioAbi.h, BSD-2-Clause-Patent\) as the design reference for the kernel service, the ring protocol and the properties the audio server needs; Apple's AudioServerPlugIn.h, AudioHardwareBase.h and AudioHardware.h from the macOS 11.3 SDK \(fetched at build time, not stored\); the board's amplifier enables hp-con-gpio GPIO4\_A7 and spk-con-gpio GPIO4\_A2 and the jack detect GPIO1\_C4 from the stock device tree.

### 配置

- package/Evb10Audio is built by build-evb10-drivers.py Evb10Audio \(a step of board.toml\), linked by the display kernel only \(configs/evb10\_display\_defconfig\) and started by the display probe with evb10-audio=N \(1: the codec over I2C; 2: also the I2S side with a polled tone and capture, evb10-audio-ms=N sets its length; 4: the audio service for iPadOS\). board.toml carries evb10-audio=4 and evb10-audio-hal=1 \(the plug-in, with evb10-gpu-addon=1\). Tuning: evb10-audio-out \(0 by the headphone detect, 1 headphone, 2 speaker, 3 both\), evb10-audio-vol \(0..36, default 28\), evb10-audio-linger \(ms, default 3000\), evb10-audio-grant, evb10-audio-selftest=N \(a tone through the service's own rings, no audio server\).
- hal/Evb10AudioPlugIn.c is built by scripts/build-evb10-audio-hal.py \(LLVM\_BIN and IOS\_SDK from the environment or ../MaliMetal/.env; Apple's CoreAudio headers are fetched into .cache/coreaudio-headers against pinned sha256\) into out/audio/Evb10Audio.driver and out/audio/audio.addon. uefi-evb10 tools/board/make-payload-boot.sh merges the addon into the GPU addon \(merge-addons.py\), MaliMetal usertest/build.sh adds the executable's CDHash to the owner trust bundle and pins it in board.toml, and the kernel mounts audio/ over /System/Library/Audio/Plug-Ins/HAL.

### 操作步骤

- Build scripts/build-evb10-audio-hal.py, then MaliMetal usertest/build.sh \(trust bundle and board.toml pin\), then the kernel \(scripts/build-evb10-kernel.sh\); run uefi-evb10 tools/xnu-probe/run-kernel.sh and read the evb10: audio lines of the serial log: the service line, 'audiomxd opens the service', the \[props\] and \[trace\] lines, the hardware on/off lines and the statistics of the engine and of the plug-in every 5 s while a sound plays. A sound needs a client: the scripted touch run of docs/network.md \(evb10-wifi=5 evb10-wifi-join=2 evb10-touch-script=99, CAPTURE\_SECS=330\) types on the on-screen keyboard and the keyboard clicks play.
- evb10-audio=2 alone repeats checkpoint 2 \(the codec and a tone, no service\); evb10-audio-selftest=N with evb10-audio=4 exercises the engine without the audio server.

### 开发经验

- The codec answers: one device on I2C7, 0x11; all 53 registers \(0x00 to 0x34\) read; a write to LOUT1VOL reads back and is put back. The firmware leaves the I2C7 clocks and pins ready. The registers are those of a configured, stopped codec \(presumably an earlier Linux or Android boot's\), not of a freshly reset one.
- The I2S side works as the master of a 48 kHz, 16 bit, two channel link: power domain 38 is on at the hand-over; 12.288 MHz comes from GPLL \(1188 MHz / 4, fraction 512/12375\) once CLKGATE\_CON\(7\) is open, the MCLK out mux takes the transmit clock and SYS\_GRF 0x318 bit 0 is cleared. The transmit FIFO took 48012 words/s \(a word is a frame\) with no underrun, and the receive FIFO delivered 47998 words/s of varying small values, which the slave codec only sends when it gets MCLK, BCLK and LRCK.
- No sound was heard: the headphone and speaker enable GPIOs of the card are not driven and nobody was at the board. Nothing is connected to iPadOS: the HAL directory has no plug-in for this codec and audiomxd runs without an output device. iPadOS decodes H.264 and HEVC through the kernel service behind AppleAVDUserClient, which this kernel does not have \(read from the entitlements of videodecodeservice and videocodecd\); only the AV1 software decoder \(a Metal program\) is in the image.
- Checkpoint 3: the kernel service Evb10Audio and the plug-in work together on the board. The mount shows Evb10Audio.driver next to the sealed BuiltinAudioPlugin.driver \(stage 5\), audiomxd opens the service, the audio server reads the device, sets the output volume and starts it; its IO thread \(priority 97, time constraint\) writes 1024-frame blocks every 21 ms always ahead of the play position \(write-ahead 1531 to 2049 frames\); the largest sample put into the transmit FIFO was 727 for a plug-in mix peak of 8748 under a -21.6 dB volume, so the sound of iPadOS reaches the I2S0 FIFO with the volume applied; both FIFOs run at 48 kHz \(1890782 and 1890791 frames in 39 s\); the audio server reports the 24 MHz host clock the timer already has, so nothing of its clock is patched.
- The engine is a polled kernel thread at priority 95 waking every 200 us: in 171906 ticks 171901 were under 300 us and 4 were over 2 ms \(longest 4.1 ms\), each of which ran the 667 us FIFO dry once, 643 frames \(13 ms\) in 39 s. The first version printed its statistics and the plug-in's 106 trace lines from that thread and stalled 68 ms: the printing moved to its own thread.
- The audio server accepts the device with the properties UniXNU-sheng found it needs \(Thunderbolt transport type, private 'accs' and 'auto' answered, empty custom-property, box and clock lists\); it asks one more it is not answered \('cfsz'\) and keeps the device. Its routing layer's own HAL calls fail on objects that are not this plug-in's and that does not stop playback.

### 完成条件

- The kernel reads the codec and passes frames between I2S0 and the codec at 48 kHz \(run a2\), and iPadOS's audio server plays into and records from it through a kernel service and a HAL plug-in: PCM from the audio server reaches the I2S0 transmit FIFO at 48 kHz with the volume applied and the capture ring fills \(runs aud1 to aud3, no panic\). Hearing it is not done.

### 当前范围

- Polled \(no DMA, no interrupt\): a kernel scheduling stall over 667 us drops frames \(4 in 39 s with the display running\). Nobody has listened: the headphone detect polarity \(the pin read 0 with nothing known to be plugged in\), the amplifier pin functions \(left as the firmware set them\), pops at start and stop, the volume curve and the capture quality are unchecked, and only the keyboard clicks were played. The audio power domain is not turned on by this driver \(it was on\). Other rates and formats and the HDMI, DisplayPort and S/PDIF audio paths are not done. The plug-in is built against the macOS 11.3 CoreAudio headers and the iOS 17 audio server; arm64e servers \(newer iPadOS\) are not covered. Video codecs are not started.

### 下一步

- A person with headphones or a speaker listens \(evb10-audio-selftest=10 plays a tone without iPadOS; evb10-audio-out=3 drives both amplifiers\) and reports the jack detect polarity and pops; then DMA for the transmit and receive rings \(PL330, the device tree names the channels and SPI 180\) to remove the drop-outs.

### 证据

- `device`: [The ES8388 on I2C7 \(one device, 0x11, 53 registers, a write that reads back\) and the I2S0 link at 48 kHz: the transmit FIFO took 48012 words/s, the receive FIFO delivered 47998 words/s of varying values, no underrun, no panic \(run a2\)](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/evidence/audio-es8388-i2s0-20261101.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; EXTRA_KERNEL_ARGS="evb10-audio=2" CAPTURE_SECS=150 tools/xnu-probe/run-kernel.sh a2</code>. Revision: `fdc202033cc15cae50c8c44a4d80a88518194ca2`.
- `device`: [iPadOS audio on the board: the plug-in is mounted next to the sealed one, audiomxd opens the service, the audio server sets the volume and starts the device for the keyboard clicks of the scripted touches, and 1890782 transmit frames \(peak 727 under the volume, mix peak 8748\) reach the I2S0 FIFO at 48 kHz with 4 drop-outs of 13 ms in all; the first version's own log printing stalled the engine for 68 ms; no panic \(runs aud1 to aud3\). Not listened to](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/evidence/audio-ipados-20261101.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; EXTRA_KERNEL_ARGS="evb10-wifi=5 evb10-wifi-join=2 evb10-touch-script=99" CAPTURE_SECS=330 tools/xnu-probe/run-kernel.sh aud3</code>. Revision: `9eed7da2f16e8dff3b7cd21d3e85787ada54d454`.
- `source`: [The audio server plug-in \(CoreAudio HAL interface\), derived from UniXNU-sheng's; builds with scripts/build-evb10-audio-hal.py to an ad hoc signed arm64 iOS 17 bundle](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/hal/Evb10AudioPlugIn.c)

## 电源 {#power}

`device-verified`

### 硬件与依赖

- SCMI over SMC clock service of the firmware's BL31 \(CPUL, DSU, CPUB01, CPUB23, DDR, GPU, NPU clocks\); RK806 PMIC on SPI2 \(the Cortex-A55 rail is its DCDC2, the GPU rail its DCDC1\); RK8602 and RK8603 on I2C0 \(the Cortex-A76 rails at 0x42 and 0x43\); the TSADC at 0xfec00000; the Mali-G610's GPU\_STATUS and cycle counter; vendor operating-point tables and regulator limits. The board is mains powered and has no power meter.

### 配置

- package/Rk3588DvfsBoard.cpp holds the rails \(clock, regulator, limits, ramp; three CPU rails and the GPU rail\) and the input-activity counter; board.toml builds the SoC's build-rk3588-dvfs.py with it and carries rk3588-dvfs=6; configs/evb10\_display\_defconfig force-loads libRk3588Dvfs.a; the display probe calls rk3588\_dvfs\_start\(\). rk3588-dvfs=0 turns everything off, rk3588-gpu=0 only the GPU governor; rk3588-dvfs-min=MHz, rk3588-dvfs-boost-ms=N \(default 300\), rk3588-dvfs-tmax=C \(default 85\), rk3588-gpu-min/-max=MHz and rk3588-gpu-boost-ms=N tune the governors. The ADT keeps sleep-disabled=1.

### 操作步骤

- Boot with rk3588-dvfs=1 to 5 for the staged CPU probes \(clock report, rate sweep, read-only regulator probe, operating-point sweep with voltage, DSU latency\), 7 for the temperature sensors, 8 to 10 for the GPU probes \(rates of the clock service, busy share, voltage walk\), then rk3588-dvfs=6 for the governors; compare the scripted swipes with and without them \(docs/power.md, Reproduce\).

### 开发经验

- The rate the clock service reports is a PVTPLL setting: with the Cortex-A76 rails at the firmware's 1.0 V every setting from 1608 MHz up measures 2230 MHz and 816 MHz measures 1220 MHz; with the table's voltage written first the measured clock is within 5 % of the rate on all three clusters from 400 MHz to 2.4 GHz \(run dvfs5\). The RK806 \(SPI2\) and RK8602/03 \(I2C0\) are read and written from the kernel with the firmware's bus setup kept.
- The DSU follows the Cortex-A55 clock and sits on its rail: a Cortex-A76 core's L3 load takes 18.1 ns with the DSU at 1800 MHz and 51.9 ns at 396 MHz, memory 120 and 181 ns \(run dvfs7; run gd6 after the probe's compiler-removed-loop fix gives 18.0 and 51.7 ns\), so the governor holds the DSU at three quarters of the faster A76 cluster.
- The CPU governor \(16 ms windows from the CPUs' idle time, rate and voltage ordered, touch boost\) ran with the scripted swipes at 52.9 frames per second against 52.8 without it \(gestures 3 to 11, runs gov2 and base1\), and for 600 s with 63 swipes at 52.1 frames per second and no panic \(gov3\). In the last 300 s of gov3 CPUB01 spent 23 % of the time at 408, 44 % at 1200 and 30 % at 2400 MHz, CPUL 91 % at 408 MHz, the DSU averaged 1161 MHz.
- The first governor run \(gov1\) lowered the voltage but did not raise it again on the way up \(the DSU bookkeeping of a domain without a DSU held a stale point\): the cores then ran at the lower clock the PVTPLL allowed and the swipes still reached 51.1 frames per second, with no fault; the governor lines now show the rail voltage next to each cluster's point, which is how it was found.
- The GPU's clock is a PVTPLL as well: the settings 300 to 900 MHz of the clock service set bit 14 of CLKSEL\_CON\(158\), 200 MHz is GPLL / 6, 1000 MHz is ignored, and the Mali driver sets CPLL / 2 = 750 MHz itself and never uses the service. Measured against the cycle counter at the vendor table's voltage: 310 MHz at 300 \(675 mV\), 396 at 400, 502 at 500, 598 at 600, 719 at 700 \(700 mV\), 852 at 800 \(750 mV\) and 957 at 900 \(800 mV\); about 2.1 to 2.3 MHz per millivolt \(runs gs1, gv1\).
- The GPU's busy share is readable from GPU\_STATUS: 0 % idle, 45 to 84 % in the 50 ms windows of the scripted swipes \(run gw1\). The GPU governor built on it \(200 to 800 MHz settings, top at 40 % busy, otherwise the lowest point that keeps it about 30 % busy, up at once, down after 75 ms, touch hold 200 ms\) kept the frame rate \(53.8 frames per second on swipes 3 to 11 in gg1 against 52.8 before; 53.2 over 61 swipes in the 600 s run gf1, no panic\) and shortened the median command buffer from 9.8 ms to 8.7 ms \(852 MHz at the 750 mV the GPU has today\); the GPU sat at 200 MHz and 675 mV for 65 to 100 % of each ten seconds. The 900 setting \(gm900\) gave 7.8 ms and 53.3 frames per second, so the ceiling stays at 800.
- The TSADC was clocked but not sampling when the kernel got it; with sampling on it reads 30 C on the idle board with 0.93 C per step. The over-temperature limit \(one point off the top of every cluster and the GPU per 128 ms at or above rk3588-dvfs-tmax, one back below tmax minus 2 C\) took up to five points off with the limit at 33 C and gave them back as the sensors fell \(run gt33, hottest reading 34.2 C\); at the default 85 C it did not act in the idle runs tb1 and tg1 \(hottest 36.0 C\).
- Idle temperature does not say what the governor saves \(0.4 C between tb1 and tg1, less than the 0.9 C between their starting temperatures, one step is 0.93 C\). The log carries a model of the busy power of the cores \(P = C f V^2 with the vendor device tree's coefficients\) against the same work at the top points: 12 % lower with a 1000 ms touch boost \(gg1\), 15 % with 300 ms \(gb300\), 23 % with none \(gb0\), 13 % over the 600 s run gf1 with the 300 ms default; frame rate on swipes 3 to 11 53.8 / 53.3 / 51.1 and gaps over 25 ms 4 / 6 / 16 \(single runs\). The GPU's idle saving is not in the model.
- The DDR clock was not changed: the clock service lists no rates for clock 4, and the vendor kernel sets the DDR rate with a SIP call into BL31 after waiting for the display's vertical blank, which would have to be coordinated with the VOP scanout.

### 完成条件

- The three CPU clusters, the DSU and the GPU change rate and voltage together under load without a panic or a lost frame rate on the board; the temperature sensors are read and the limit lowers and restores the points; the governors' per-point times, the model power and the temperatures are in the serial log. What they save in watts is not measured.

### 当前范围

- Power was not measured \(no meter\): the saving is known as time at each point and as a model of the cores' busy power, and the GPU's idle saving is in neither; the temperature does not resolve it. The operating points are Rockchip's typical-die tables \(a die that needs more voltage at a point runs it slower, not wrongly, and nothing reports it\). The DDR clock is not managed; suspend and resume are not implemented and there is no battery. Cortex-A55 cores 5 to 7 are off under cpumask=31. Frame rates are single runs; the run-to-run spread was not measured.

### 下一步

- Measure the supply power with and without the governors on the scripted swipes \(an external meter\), then the DDR clock through the SIP call and the display's vertical blank.

### 证据

- `source`: [The EVB10's rails \(RK806 DCDC2 and DCDC1, RK8602 0x42 and RK8603 0x43\) with the vendor limits and ramp rates, and the touch report counter as the input activity; the mechanism is UniXNU-rk3588-common scripts/data/Rk3588Dvfs](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/package/Rk3588DvfsBoard.cpp)
- `device`: [Each cluster walked down its operating points and back up with the voltage written in the right order: the rail read back the voltage asked for, the clock service the rate, and the core measured 395 MHz at 408, 1135 MHz at 1200 \(675 mV\), 1909 MHz at 1800 \(850 mV\) and 2229 MHz at 2304 \(1.0 V\) on CPUB01, 1862 MHz at 1800 \(950 mV\) on CPUL; no fault \(run dvfs5\)](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/evidence/dvfs-operating-points-20261101.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; EXTRA_KERNEL_ARGS="rk3588-dvfs=4" tools/xnu-probe/run-kernel.sh dvfs5</code>. Revision: `82bce68ca0d021a4fe538fb10a5313c86ba28b09`.
- `device`: [A Cortex-A76 core's load from the L3 took 18.1 ns with the DSU at 1800 MHz, 26.1 ns at 1008 MHz and 51.9 ns at 396 MHz, from memory 120.4, 134.3 and 180.8 ns; a DSU rate set on its own with the A55 cores at 408 MHz read back 1800 MHz \(run dvfs7\); the probe after its fix gave 18.0, 26.4 and 51.7 ns, memory 120.5, 134.3 and 180.7 ns \(run gd6\)](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/evidence/dvfs-dsu-20261101.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; EXTRA_KERNEL_ARGS="rk3588-dvfs=5" tools/xnu-probe/run-kernel.sh dvfs7</code>. Revision: `82bce68ca0d021a4fe538fb10a5313c86ba28b09`.
- `device`: [Scripted swipes 3 to 11: 52.9 frames per second with the CPU governor \(gov2\) and 52.8 without \(base1\); 63 swipes in a 600 s run at 52.1 frames per second, 64 touch boosts, no panic, CPUB01 23 % of the time at 408, 44 % at 1200, 30 % at 2400 MHz \(gov3\)](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/evidence/dvfs-governor-20261101.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; CAPTURE_SECS=600 EARLY_STOP=0 EXTRA_KERNEL_ARGS="evb10-touch-demo=120 mali-timeline=1" tools/xnu-probe/run-kernel.sh gov3; python3 tools/xnu-probe/frame_phases.py gov3</code>. Revision: `82bce68ca0d021a4fe538fb10a5313c86ba28b09`.
- `device`: [The TSADC read 31.4 C at the first reading with sampling switched on by the kernel and 30 C idle for 600 s with and without the governor \(29.64 and 30.04 C mean after 200 s, runs tg1 and tb1\); with the limit at 33 C the governor took up to five points off the top and restored them as the sensors fell, hottest reading 34.2 C \(run gt33\)](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/evidence/dvfs-thermal-20261101.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; EXTRA_KERNEL_ARGS="rk3588-dvfs=7" CAPTURE_SECS=600 EARLY_STOP=0 tools/xnu-probe/run-kernel.sh tb1; CAPTURE_SECS=235 EXTRA_KERNEL_ARGS="evb10-touch-demo=120 mali-timeline=1 rk3588-dvfs-tmax=33" tools/xnu-probe/run-kernel.sh gt33</code>. Revision: `caa32691f315e6c7f013b3c31df63aedf3fbd03c`.
- `device`: [The GPU's clock service settings measured against the cycle counter: 197 MHz at 200 \(GPLL / 6\), 310 at 300, 396 at 400, 502 at 500, 598 at 600 \(675 mV\), 719 at 700 \(700 mV\), 852 at 800 \(750 mV\), 957 at 900 \(800 mV\), 1000 ignored; 1053 MHz for the 900 setting at 850 mV and 679 at 675 mV; GPU busy 0 % idle and 45 to 84 % in the swipes' 50 ms windows \(runs gs1, gv1, gw1\)](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/evidence/gpu-clock-20261101.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; EXTRA_KERNEL_ARGS="rk3588-dvfs=8" CAPTURE_SECS=110 EARLY_STOP=0 tools/xnu-probe/run-kernel.sh gs1 (rk3588-dvfs=10 for gv1, rk3588-dvfs=9 evb10-touch-demo=120 mali-timeline=1 for gw1)</code>. Revision: `caa32691f315e6c7f013b3c31df63aedf3fbd03c`.
- `device`: [The GPU governor with the scripted swipes: 53.8 frames per second on gestures 3 to 11 and a median command buffer of 8.7 ms \(gg1\) against 52.8 and 9.8 ms before; the 600 s run with 64 swipes at 53.2 frames per second over 61 moving gestures, the GPU 65 to 100 % of each ten seconds at 200 MHz and 675 mV, no panic \(gf1\); touch boost 1000 / 300 / 0 ms: 53.8 / 53.3 / 51.1 frames per second, model power of the cores 12 / 15 / 23 % under the top points; the 900 setting 7.8 ms and 53.3 frames per second \(gm900\)](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/evidence/gpu-governor-20261101.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; CAPTURE_SECS=600 EARLY_STOP=0 EXTRA_KERNEL_ARGS="evb10-touch-demo=120 mali-timeline=1" tools/xnu-probe/run-kernel.sh gf1; python3 tools/xnu-probe/frame_phases.py gf1</code>. Revision: `caa32691f315e6c7f013b3c31df63aedf3fbd03c`.

## 镜像组装 {#packaging}

`device-verified`

组件: `XnuPrelink`, `DarwinBoot`, `SoftwareAES`.

### 硬件与依赖

- XNU of the OS profile, ARM64, SoC and device patch series, generated Apple device tree, payload volume of 96 MiB, owner trust-cache digests.

### 配置

- payload.\* in board.toml and the \[adt\] tables; the device tree is generated from dts/evb10.dts.
- payload.kernel\_args lists the boot arguments grouped by purpose.

### 操作步骤

- Run scripts/build-evb10-kernel.sh, then ./unixnu build payload with --unique-chip-id.

### 开发经验

- A rebuild from the six pushed repositories in an empty directory \(docs/reproduce.md\) reaches launchd with about 110 processes and Mali-composited frames; the feeds.toml pin of the SoC repository has to include the dts change that stops exporting interrupts on the eMMC and UART nodes, because an exported interrupts property without AAPL,phandle makes IOKit start-up take a data abort. The second trust\_cache\_sha256 entry changes with every rebuild because the user-space binaries are not bit-for-bit reproducible.
- The device series must not touch the context of the hunks of earlier series: the userland-mounts patch is generated by patches/tools/make-patches.py from a tree that has the earlier series applied.
- The Mali driver carries weak fallbacks for the display driver's GPU hand-off, because the display-less pass links it too \(kernel patches call its test hooks\); the display archive's strong definitions replace them.
- Changing the XNU patch list recreates the prepared source tree, and preparing it downloads the DriverKit headers the feed leaves out, so that rebuild needs network access \(through the proxy, if there is one, even when the build runs under env -i\).
- Each defconfig name is its own output directory \(out/evb10/&lt;os&gt;/evb10 and .../evb10\_display\), so the display scripts read the display-less kernel from the sibling directory.
- The payload rides in a boot image through U-Boot's fastboot, whose download buffer is 112 MiB; 96 MiB of payload fits, 128 MiB was refused.
- The payload step of unixnu refuses a kernel command line longer than 1000 bytes \('the kernel command line is 1018 bytes; the limit is 1000'\) before the board is touched. The defaults of board.toml are 884 bytes, so debugging arguments are added per run through EXTRA\_KERNEL\_ARGS, which replaces defaults of the same name.
- A driver that only the display probe calls \(Evb10Wifi\) is built by a plain build-evb10-drivers.py step and force-loaded by the display defconfig alone; a build with only the display-less defconfig does not contain it, and its log strings \(evb10: wifi\) tell which kernel a run used.
- package/Evb10Wifi gained CMD53, 4-bit mode, backplane and ARM CR4 control and the firmware download \(evb10-wifi=2\); the images enter the kernel as wifi\_fw.inc, generated into the build tree's kits/evb10 \(a link to package/\) and ignored by git.
- The original AppleImage4 \(it matches on /defaults\) waits without a timeout for IOAESAccelerator while it starts; without a provider IOKit never goes quiet and the userland's network configuration waits for it. The SoftwareAES component \(a software AES-CBC behind IOAESAccelerator, CONFIG\_XNU\_NATIVE\_AES=y in the SoC repository's rk3588.config, build-software-aes-bindings.py in board.toml\) provides it: IOKit is quiet 26 s into the boot log.
- package/Evb10Audio is a third driver of this kind \(after Evb10Touch and Evb10Wifi\): kernel-side code with a polled I2C master for the ES8388 and the I2S0 controller, built into the display kernel and started with evb10-audio=N; the OS image and the userland are not changed \(docs/audio.md\).
- package/Evb10Audio is a driver archive like the others \(build-evb10-drivers.py Evb10Audio, force-loaded by the display kernel\): checkpoint 3 adds the IOService Evb10Audio with its user client and a polled engine thread, and the header Evb10AudioAbi.h that the audio server plug-in \(hal/\) shares. Observed on the board: audiomxd opens the service and the audio server's PCM reaches the I2S0 transmit FIFO \(evidence/audio-ipados-20261101.txt\).
- board.toml builds the SoC's frequency management with build-rk3588-dvfs.py kits/evb10/Rk3588DvfsBoard.cpp \(the board's rail table, package/Rk3588DvfsBoard.cpp\) after the audio driver; it needs the kernel record of the first pass like the other driver archives, so it sits in the same archive list. The SoC series gained rk3588-cpu-idle.patch \(a CPU's idle time for the governor\): scripts/build-evb10-kernel.sh re-clones and re-applies the series on every run, so a patch that fails to apply or to compile stops the build, and a failed compile of an XNU object leaves the archive steps without it until the object is built again \(compile it from its .o.json record, then rerun\).
- The rail table of package/Rk3588DvfsBoard.cpp has a fourth entry, the GPU rail \(RK806 DCDC\_REG1, 550 to 950 mV, 12.5 mV/us\); the SoC series' GPU governor \(Rk3588Gpu.cpp, compiled by the same build-rk3588-dvfs.py step\) uses it, and the display kernel with it ran for 600 s with the governors without a panic \(run gf1, docs/power.md\).

### 完成条件

- The payload boots on the board to the lock screen.

### 当前范围

- The two-pass kernel build of this layout completes on Linux \(evb10\_defconfig, then evb10\_display\_defconfig; kernel.macho 55.0 MB, sha256 db5e4c058e6516d9cb886d2819d1ca02366a29b9748fbd6b15123e0023e5bf2f, the one booted in run v1\). The payload needs a platform seed and the owner trust-cache digests, which are in no repository.

### 下一步

- Make the user-space build reproducible, or compute the second trust\_cache\_sha256 entry in the payload step, so that board.toml does not change with every rebuild.

### 证据

- `source`: [Device patch order](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/patches/xnu/series)
- `device`: [A payload assembled from this layout \(96 MiB in a 106553344-byte boot image\) booted through U-Boot's fastboot to a running backboardd and SpringBoard with Mali-composited frames and no panic in 235 s; kernel.macho 55017472 bytes, sha256 db5e4c05 \(run v1\)](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/evidence/boot-v1-20261030.txt)
  Command: <code>cd UniXNU-evb10 &amp;&amp; scripts/build-evb10-kernel.sh; cd ../uefi-evb10 &amp;&amp; CAPTURE_SECS=235 EARLY_STOP=0 EXTRA_KERNEL_ARGS="evb10-touch-demo=120 mali-timeline=1" tools/xnu-probe/run-kernel.sh v1</code>. Revision: `833f90fb52890090ad2bdd79285cc527b00d3ead`.

## 诊断 {#diagnostics}

`device-verified`

### 硬件与依赖

- UART2 serial console at 1.5 Mbaud; DEVELOPMENT kernel.

### 配置

- Kernel arguments -v, serial=3, vc\_mirror=1, debug=0x10014e, -enable\_kprintf\_spam.
- evb10-ps=N, evb10-bt, evb10-bt2, evb10-bt3, evb10-bt4 and mali-timeline=1 are added per run through EXTRA\_KERNEL\_ARGS: the process table costs the serial line about 3 MB a run and moves the frame rate, and the command line is limited to 1000 bytes.
- evb10-thr=N sets how many threads of each process the table shows \(default 8\): the thread that holds the lock or the paging reference is often not among the first eight.

### 操作步骤

- Read the serial console. evb10-ps prints the process table, evb10-bt prints user stacks of the named processes for symbolication on the host.

### 开发经验

- Console lines longer than about 255 characters lose their tail.
- The serial input of XNU is dead on this board, so there is no command channel; judge the kernel's progress from the serial output only.
- The reset-path breadcrumbs of a secondary core are 16 words \(128 bytes\) per core, as rk3588-smp-el2.patch stores them; the dump reads them with that stride and prints the TTBR1, TCR and TTBR0 the core had when it was about to enable the MMU.
- A thread that waits in vm\_object\_destroy \(a file's last mapping went away and its vnode is reclaimed\) waits for the object's paging and activity counts; the table now prints the object \(references, paging, activity, resident and wired pages, the first wired pages\) next to such a thread, which is how a buffer object pinning a file's pages was found to hold up the render server.
- evb10\_range\_is\_file\_backed \(in the same patch\) tells a driver whether a task's address range sits on a vnode pager's pages; package/Mali uses it to copy such pages instead of pinning them.

### 完成条件

- Every boot stage prints a checkpoint to the serial console.

### 当前范围

- Panics reset the board after the text is out; no panic screen is drawn.

### 下一步

- Add a panic screen on the frame buffer.

### 证据

- `source`: [Process exit trace](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/patches/xnu/evb10-exit-trace.patch)
- `device`: [Every stage of the boot printed a time-stamped checkpoint: U-Boot hand-off 4.6 s, UEFI 4.8 s, the UniXNU menu entry 20.7 s, hand-off to the kernel 20.8 s, first kernel line 21.3 s, root accepted 24.0 s, launchd 54.9 s, backboardd on the Mali 69.4 s and SpringBoard 96.1 s \(run v1\)](https://github.com/Ken-u/UniXNU-evb10/blob/37befa9162d6b4b080cb63a95cccff0ebb4d34f5/evidence/boot-v1-20261030.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; CAPTURE_SECS=235 EARLY_STOP=0 EXTRA_KERNEL_ARGS="evb10-touch-demo=120 mali-timeline=1" tools/xnu-probe/run-kernel.sh v1</code>. Revision: `833f90fb52890090ad2bdd79285cc527b00d3ead`.

</div>
