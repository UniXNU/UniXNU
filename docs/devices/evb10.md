# Rockchip RK3588 EVB10 V10

[Ken-u/UniXNU-evb10](https://github.com/Ken-u/UniXNU-evb10)

<div v-pre>

Rockchip RK3588 EVB10 V10 runs the iPadOS 17.7.11 userland on a source-built XNU, started from edk2-rk3588 firmware \(uefi-evb10\). Shared SoC support is in UniXNU-rk3588-common; this repository owns the memory layout, the eMMC root, the VOP2 display, touch, the Mali-G610 integration and the packaging. Every area in scope is device-verified on the board with a system built from these repositories \(docs/reproduce.md\): it boots to SpringBoard with the eMMC root and the Data volume mounted, the Mali composites the interface at about 50 frames per second while scrolling, and the panel and the touch screen were checked by hand and work normally. Not done: GPU and CPU frequency control, interrupt-driven GPU completion, network, audio and power management.

Source record: [porting.toml](https://github.com/Ken-u/UniXNU-evb10/blob/e03f9880ae8fc420fa337366a444c8888b0e3fdc/porting.toml), `e03f9880ae8fc420fa337366a444c8888b0e3fdc`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `device-verified` |
| [Firmware and boot](#firmware) | `device-verified` |
| [CPU and interrupts](#cpu) | `device-verified` |
| [Memory and DMA](#memory) | `device-verified` |
| [Storage and root](#storage) | `device-verified` |
| [Display](#display) | `device-verified` |
| [Input](#input) | `device-verified` |
| [GPU](#gpu) | `device-verified` |
| [Network](#network) | `planned` |
| [Audio](#audio) | `not-applicable` |
| [Power](#power) | `not-applicable` |
| [Image assembly](#packaging) | `device-verified` |
| [Diagnostics](#diagnostics) | `device-verified` |

## Configuration {#configuration}

`device-verified`

### Hardware and dependencies

- ARM64 profile, rk3588 SoC source pinned in feeds.toml, iPadOS 17.7.11 build 21H461 profile, evb10\_defconfig and evb10\_display\_defconfig, submodules package/Mali and package/Rk3588Emmc.

### Configuration

- board.soc\_source = rk3588; board.os\_profile = ipados-17.7.11-21H461; schema\_version = 2.
- kernel.config\_fragments = arch common, soc rk3588, os ipados; the defconfig applies last and switches off what the OS profile enables for other hardware \(NATIVE\_ADRENO, SOURCE\_MOCKFS\).
- kernel.patch\_series = arch, soc, os, device in that order.
- payload.kernel\_args carries the frame-rate group as defaults: zero-copy scanout with the GPU job as the fence \(evb10-vop-direct=1, evb10-vop-fence=1\), the GPU at 750 MHz \(mali-pll=1, mali-div=1\), the device's YCbCr filter \(mali-ycbcr-filter=device\), asynchronous surface flush \(mali-aflush=1\), cpumask=31, mali-epri=50 and sched-slowcpus=240; the comment above the list says what each one does.

### Procedure

- From the UniXNU checkout run ./unixnu defconfig evb10\_defconfig -D ../UniXNU-evb10, then ./unixnu fetch and ./unixnu status --json with the same -D.
- For a local SoC checkout copy local.toml.example to local.toml.
- Run scripts/build-evb10-kernel.sh for the two-pass kernel build.

### Development findings

- The \[adt.defaults.u32\] table of board.toml must carry sleep-disabled = 1 and vmm-present = 1; the OS profile only supplies kern.maxvnodes. vmm-present backs kern.hv\_vmm\_present: without it watchdogd traps with SIGTRAP three times and the kernel panics when the third instance exits \(seen in a rebuild from a clean tree, fixed in the clean-directory rerun\).
- Arrays replace inherited values, so board.toml lists every archive, fragment and trust-cache digest it needs.
- The display archive is made from the kernel of an earlier display-less pass, which is why two defconfigs exist and why the build script runs them in order.
- A device script named like a UniXNU script shadows it in the build tree; the board driver builder is therefore named build-evb10-drivers.py and does not replace build-arm-driver.py.
- A boot with the committed defaults and nothing else but the scripted swipes and the command-buffer timeline \(run v1\) held the GPU at 750 MHz, the Cortex-A76 cores at 2.23 GHz and 52.6 frames per second while the finger was down \(swipes 3 to 11\), and ended its 235 s capture without a panic or a stalled GPU group.
- The evidence/ directory holds one curated excerpt per verified checkpoint, named &lt;topic&gt;-&lt;date&gt;.txt. Excerpts of kernel runs name the run command and tag; the Wi-Fi identity excerpt \(evidence/wifi-sdio-id-20261030.txt\) comes from U-Boot with no kernel running, so it names the probe script and the uefi-evb10 revision that holds it.

### Completion criteria

- Every source pin resolves, ./unixnu status lists the intended patch order, and both defconfigs materialise.

### Current limits

- The format 2 configuration has been materialised and checked with status and tree; a full kernel build with it is recorded under Image assembly.

### Next action

- Pin the Mali and Rk3588Emmc submodules to released commits when they change.

### Evidence

- `source`: [Implementation and configuration described in this section](https://github.com/Ken-u/UniXNU-evb10/blob/e03f9880ae8fc420fa337366a444c8888b0e3fdc/board.toml)
- `device`: [Boot with the committed default arguments \(run v1\): GPU 750 MHz by the cycle counter, Cortex-A76 cores at 2.23 GHz, 504 heavy command buffers took 14.9 ms \(median\) and 18.9 ms \(90th percentile\) from commit to completion, 52.6 frames per second with the finger down in the scripted swipes 3 to 11, no panic and no stalled GPU group in a 235 s capture](https://github.com/Ken-u/UniXNU-evb10/blob/e03f9880ae8fc420fa337366a444c8888b0e3fdc/evidence/boot-v1-20261030.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; CAPTURE_SECS=235 EARLY_STOP=0 EXTRA_KERNEL_ARGS="evb10-touch-demo=120 mali-timeline=1" tools/xnu-probe/run-kernel.sh v1; python3 tools/xnu-probe/cb_table.py v1 --latency; python3 tools/xnu-probe/frame_phases.py v1</code>. Revision: `833f90fb52890090ad2bdd79285cc527b00d3ead`.

## Firmware and boot {#firmware}

`device-verified`

### Hardware and dependencies

- edk2-rk3588 firmware built by uefi-evb10 \(SPI NOR image\), TF-A at EL3 with PSCI over SMC, UEFI GOP frame buffer and the Mali CSF firmware listed in proprietary-files.txt.

### Configuration

- board.toml has no \[firmware\] section: the unixnu firmware step builds Mu-Silicium, and this board boots edk2-rk3588 built by uefi-evb10.
- payload.loader = firmware: DarwinBoot is inside the firmware volume.
- proprietary-files.txt pins mali\_csffw.bin by SHA-256; scripts/extract-files.py places it in .cache/firmware.

### Procedure

- Build the firmware in uefi-evb10 \(build.sh\) and flash or boot it as that repository describes.
- Run scripts/extract-files.py SOURCE, then the kernel step; scripts/build-mali-firmware.py writes package/Mali/mali\_csffw.inc.

### Development findings

- The firmware hands the kernel EL1 with the MMU off and PSCI on SMC; secondary cores started by CPU\_ON arrive at EL2 and the SoC patch drops them to EL1.
- The firmware leaves the eMMC in HS400 and UART2 at 1.5 Mbaud; the drivers rely on both.
- proprietary-files.txt also lists the AP6398S Wi-Fi firmware and nvram from the Rockchip Android vendor tree as optional entries \(fw\_bcm4359c0\_ag.bin for the BCM4359 C0, revision 9, read over SDIO\); no driver loads them yet. The fw\_bcm4359c51a2\_ag.bin of that directory is a 4362a2 build and does not fit this module.

### Completion criteria

- Firmware enters DarwinBoot, publishes the GOP frame buffer and keeps the memory reservations of the board.

### Current limits

- Firmware and its boot flow are documented in uefi-evb10; this repository only pins the inputs.

### Next action

- Record the firmware commit next to each image verification.

### Evidence

- `source`: [Firmware inputs and their digests](https://github.com/Ken-u/UniXNU-evb10/blob/e03f9880ae8fc420fa337366a444c8888b0e3fdc/proprietary-files.txt)
- `device`: [UEFI built from uefi-evb10 94ec4bd with the GPU rail at 0.75 V started from U-Boot's fastboot, the UniXNU menu booted the xnu entry, DarwinBoot published the 640x480 GOP frame buffer and kept the reserved regions of the device tree, boot services ended at 20.8 s and the kernel printed 'kprintf initialized' 0.4 s later \(run v1\)](https://github.com/Ken-u/UniXNU-evb10/blob/e03f9880ae8fc420fa337366a444c8888b0e3fdc/evidence/boot-v1-20261030.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; CAPTURE_SECS=235 EARLY_STOP=0 EXTRA_KERNEL_ARGS="evb10-touch-demo=120 mali-timeline=1" tools/xnu-probe/run-kernel.sh v1</code>. Revision: `94ec4bd00d4d755623ce6cedd84172cbcd238dbd`.

## CPU and interrupts {#cpu}

`device-verified`

Components: `ArmCpu`, `ArmDTPlatform`.

### Hardware and dependencies

- Four Cortex-A55 and four Cortex-A76 at affinities 0x000 to 0x700, GICv3 at 0xfe600000 with redistributors at 0xfe680000 \(128 KiB stride\), 24 MHz architected timer, PSCI over SMC.

### Configuration

- The CPU, GIC and PSCI nodes come from the SoC dtsi \(rk3588-common dts/rk3588.dtsi\); the board DTS enables nothing extra.
- Kernel arguments sheng-smp=1, armcpu-self-ipi=1 and armcpu-mmio-sgi=0 select the secondary-core and IPI paths.
- cpumask=31 starts logical cores 0 to 4 only: the four Cortex-A76 cores, which the SoC device tree lists first, and the boot core, a Cortex-A55. sched-slowcpus=240 marks logical cores 4 to 7 \(the Cortex-A55 cores\) as slow for the scheduler.

### Procedure

- Compile dts/evb10.dts through ./unixnu tree and inspect /cpus, /psci and /arm-io/intc in the generated device tree.
- Boot and read the per-core entry lines on the serial console.

### Development findings

- Inline assembly in this target goes through the Darwin assembler, where ';' starts a comment: "dsb ishst; msr icc\_sgi1r\_el1, %0; isb" assembled to a lone dsb. Earlier conclusions that the GIC ignores ICC\_SGI1R, that the A55 CNTFRQ is zero and that counters differ per core all came from this mistake and were withdrawn. The SoC repository carries the ArmCpu fix; scripts/build-evb10-kernel.sh refuses new inline assembly with ';'.
- With the fix all eight cores run and inter-processor interrupts go through ICC\_SGI1R\_EL1.
- XNU takes the lowest-numbered idle core and the device tree order numbers the cores, so the SoC device tree lists the Cortex-A76 cores first \(logical 0 to 3\) and the boot core, the fifth node, is found by matching its MPIDR with reg. The render server's encoding thread replays a command buffer in 4 ms on a Cortex-A76 and 11 to 14 ms on a Cortex-A55; sched-slowcpus keeps user-interface threads off an idle slow core while a fast one is free or can be preempted \(rk3588-slow-cores.patch, SoC repository\).
- The firmware's regulator table for the Cortex-A76 clusters was compiled as zeros \(the DSC used a macro that exists only in C\), so the clusters were clocked up without more voltage and calibrated at 1.78 GHz. With the table fixed in uefi-evb10 the A76 cores calibrate at 2.23 GHz \(the A55 at 1.86 GHz\); a Cortex-A76 integer loop takes 20 % less time, the 4 ms replay stays the same because it waits for memory.

### Completion criteria

- Every enabled core reaches its entry checkpoint and receives timer and inter-processor interrupts.

### Current limits

- CPU frequency is not managed: cores run at the clock the firmware left \(Cortex-A76 2.23 GHz, although the firmware asks for 2.4 GHz and the gap was not investigated; Cortex-A55 1.86 GHz\). No cluster-type properties are set, so the scheduler sees one cluster type, and the slow-core mask is a boot argument. cpumask=31 leaves three Cortex-A55 cores off.

### Next action

- Add CPU frequency control and decide whether to describe the A55 and A76 clusters to the scheduler.

### Evidence

- `source`: [Board device tree on top of the shared SoC description](https://github.com/Ken-u/UniXNU-evb10/blob/e03f9880ae8fc420fa337366a444c8888b0e3fdc/dts/evb10.dts)
- `device`: [The four Cortex-A76 cores reported running at 2230, 2230, 2223 and 2223 MHz with cpumask=31 and sched-slowcpus=240 on the command line; the render server's encoding thread ran on the Cortex-A55 core for 6 of the 504 heavy command buffers and on an A76 core for the other 498, with no panic in 235 s \(run v1\)](https://github.com/Ken-u/UniXNU-evb10/blob/e03f9880ae8fc420fa337366a444c8888b0e3fdc/evidence/boot-v1-20261030.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; CAPTURE_SECS=235 EARLY_STOP=0 EXTRA_KERNEL_ARGS="evb10-touch-demo=120 mali-timeline=1" tools/xnu-probe/run-kernel.sh v1; python3 tools/xnu-probe/cb_table.py v1 --latency</code>. Revision: `833f90fb52890090ad2bdd79285cc527b00d3ead`.

## Memory and DMA {#memory}

`device-verified`

### Hardware and dependencies

- DRAM bank 0x1\_00000000 with size 0x1\_00000000 in the firmware memory map, 2 GiB owned window for the kernel, eMMC controller with 32-bit DMA.

### Configuration

- dts/evb10.dts declares the memory node; payload.dram\_size must equal it.
- payload.adt.owned\_memory\_size = 0x80000000: DarwinBoot allocates this contiguous window from the low bank.

### Procedure

- Compare the firmware memory map, dts/evb10.dts and the owned window reported by DarwinBoot.
- Check DMA buffers of the eMMC driver against the 4 GiB address limit.

### Development findings

- The 4 GiB bank above 4 GiB is the one large region without TF-A, OP-TEE, firmware or Rockchip carve-outs.
- A 256 MiB window left too little memory for the iPadOS userland; 2 GiB fits the firmware's low bank, 3 GiB was refused with Out of Resources. All pages sit below 4 GiB, where the eMMC DMA reaches.
- No IOMMU is used for the eMMC controller; the driver allocates a bounce window below 4 GiB.

### Completion criteria

- All handoff regions are accounted for and every DMA engine works inside its allocated range.

### Current limits

- Memory above the 2 GiB window is unused.

### Next action

- Test a larger window by placing the kernel window above 4 GiB.

### Evidence

- `source`: [Memory node and handoff window](https://github.com/Ken-u/UniXNU-evb10/blob/e03f9880ae8fc420fa337366a444c8888b0e3fdc/dts/evb10.dts)
- `device`: [The hand-off kept cma, drm-logo, vendor-storage and ramoops reserved and gave the kernel a window of 0x80000000 bytes; the eMMC reads \(111 block requests, 0 failures\), the VOP2 scanout behind its IOMMU \(paging on\) and the Mali jobs ran inside it for 235 s without a fault or a panic \(run v1\)](https://github.com/Ken-u/UniXNU-evb10/blob/e03f9880ae8fc420fa337366a444c8888b0e3fdc/evidence/boot-v1-20261030.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; CAPTURE_SECS=235 EARLY_STOP=0 EXTRA_KERNEL_ARGS="evb10-touch-demo=120 mali-timeline=1" tools/xnu-probe/run-kernel.sh v1</code>. Revision: `833f90fb52890090ad2bdd79285cc527b00d3ead`.

## Storage and root {#storage}

`device-verified`

Components: `AppleKeyStoreState`.

### Hardware and dependencies

- DesignWare MSHC at 0xfe2e0000, 8-bit eMMC, GPT with userdata at LBA 8459264 to 122142655 \(512-byte blocks\), SHNGROOT manifest image written by unixnu build userdata.

### Configuration

- userdata.first\_lba, last\_lba and windows \(OS, SystemOS\) describe the root image.
- Kernel arguments: emmc=4, emmc-root-trust=1, emmc-systemos-union=1, emmc-data-mount=1, emmc-data-size=2048, emmc-data-persist=1.
- payload.adt.root\_match\_volume\_uuid names the OS volume; packed\_data\_ramdisk = false.

### Procedure

- Build with build-evb10-drivers.py Rk3588Emmc followed by bind-emmc-storage.py; regenerate scripts/data/evb10-storage-interface-audit.json with audit-evb10-storage.py when the kernelcache pin changes.
- scripts/peek-root-image.py reads the manifest of a userdata image without a board.

### Development findings

- The driver subclasses the original IOBlockStorageDevice, so its archive is made by binding the object to the original code at audited addresses.
- Only the last 2049 MiB of userdata, the Data window, is ever written: the first start formats it and the kernel copies /private/var once, after which restarts mount it. Writes showed zero failures in the observed runs.
- A 256 MiB Data volume ran out of space \(ENOSPC\) and stalled SpringBoard; 512 MiB was enough to reach the lock screen, 2048 MiB is the configured size. vnode jetsam killed daemons until /defaults/kern.maxvnodes was set to 66560, which the OS profile now provides.
- The tools directory is split by owner: the thread-sample include belongs to the diagnostics area, while the userland-mounts include keeps, next to the mounts, the periodic process table and the screenshot over the serial line.
- The Data window is a persistent volume: the kernel keeps the tree and preferences of earlier boots \(evb10: Data: persistent volume, seeded by an earlier boot\) and, because a run ends by resetting the board, mounts the container after an unclean unmount by reloading its newest checkpoint.

### Completion criteria

- The root volume mounts read-only from the OS window and the Data volume mounts read-write across restarts.

### Current limits

- Only eMMC is supported; PCIe NVMe is not used. Every run ends by resetting the board, so the Data container has always been mounted after an unclean unmount; a mount after an orderly shutdown was not exercised.

### Next action

- Repeat the persistence check after a clean unmount, which no run has exercised.

### Evidence

- `source`: [Binding of the eMMC block device to the original storage class](https://github.com/Ken-u/UniXNU-evb10/blob/e03f9880ae8fc420fa337366a444c8888b0e3fdc/scripts/bind-emmc-storage.py)
- `device`: [The SystemOS window is published read-only \(111 block requests, 0 failures\), the root volume of the OS window is accepted read-only, the 2 GiB Data window is published writable and /private/var mounts on it as a persistent volume. Across 56 boots of 2026-10-30, each run ending by a board reset, the transaction id of the Data container rose from 10018 to 16586 and 47 of the boots recovered it after an unclean unmount \(run v1 and the table in the log\)](https://github.com/Ken-u/UniXNU-evb10/blob/e03f9880ae8fc420fa337366a444c8888b0e3fdc/evidence/boot-v1-20261030.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; CAPTURE_SECS=235 EARLY_STOP=0 EXTRA_KERNEL_ARGS="evb10-touch-demo=120 mali-timeline=1" tools/xnu-probe/run-kernel.sh v1</code>. Revision: `833f90fb52890090ad2bdd79285cc527b00d3ead`.

## Display {#display}

`device-verified`

Components: `GopFramebuffer`.

### Hardware and dependencies

- VOP2 with the Esmart3 window on the DSI panel, 1080x1920; UEFI GOP frame buffer; original IOMobileFramebufferLegacy bound to NativeLegacyDisplay.

### Configuration

- Kernel arguments evb10-vop=2, evb10-vop-es2=1, evb10-fb-w=1072, evb10-fb-h=1904, offline-legacy-\* and sheng-vsync=60.
- evb10\_display\_defconfig links the display archive and the link stubs.

### Procedure

- Build both passes with scripts/build-evb10-kernel.sh and boot with a monitor or panel attached.

### Development findings

- The firmware assigns Esmart3 to VP2; writing back the layer-mixer policy of U-Boot makes the window take effect.
- Underruns \(POST\_BUF\_EMPTY\) on the panel path came from the firmware's HDMI0 window \(Esmart2\) fetching at the same time; disabling it with evb10-vop-es2=1 gave zero underruns.
- A frame size of exactly 1080x1920 makes backboardd render the 1242x2208 geometry of other devices and ask for scaling, which the full-frame swap validation rejects; 1072x1904 avoids it.
- Tearing in scanout was removed by waiting for the GPU jobs of a frame before the page flip.
- The kernel prints the gaps of every moving window of frames \(evb10: display gaps\), on the clock of the Metal plug-in's command-buffer timeline, so the hitches of a swipe can be matched with the command buffers. A screenshot over the serial line \(evb10-shot-img\) reads the live frame buffer row by row for several seconds, so moving content tears in it; compare static frames only.

### Completion criteria

- The panel shows the lock screen without flicker or tearing.

### Current limits

- Frame rate while scrolling is limited by how fast a heavy frame is encoded and drawn against its deadline \(see GPU\). The panel timing is the firmware's.

### Next action

- Shorten the encoding of heavy frames \(see GPU\), take screenshots from a snapshot, and move presentation to vsync interrupts.

### Evidence

- `source`: [VOP2 scanout presenter](https://github.com/Ken-u/UniXNU-evb10/blob/e03f9880ae8fc420fa337366a444c8888b0e3fdc/package/Evb10Display/NativeLegacyDisplay.cpp)
- `device`: [Checked by hand on the board \(reported 2026-10-30\): the panel works normally](https://github.com/Ken-u/UniXNU-evb10/blob/e03f9880ae8fc420fa337366a444c8888b0e3fdc/evidence/boot-v1-20261030.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; tools/xnu-probe/run-kernel.sh TAG, then look at the panel</code>. Revision: `833f90fb52890090ad2bdd79285cc527b00d3ead`.
- `device`: [The kernel frame buffer \(1072x1904\) is scanned out by VOP2 behind its IOMMU and the display gap log shows 16.6 ms between frames: 52.6 frames per second with the finger down in the scripted swipes 3 to 11 \(run v1\)](https://github.com/Ken-u/UniXNU-evb10/blob/e03f9880ae8fc420fa337366a444c8888b0e3fdc/evidence/boot-v1-20261030.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; CAPTURE_SECS=235 EARLY_STOP=0 EXTRA_KERNEL_ARGS="evb10-touch-demo=120 mali-timeline=1" tools/xnu-probe/run-kernel.sh v1; python3 tools/xnu-probe/frame_phases.py v1</code>. Revision: `833f90fb52890090ad2bdd79285cc527b00d3ead`.

## Input {#input}

`device-verified`

### Hardware and dependencies

- Goodix GT1158 on I2C5, polled; coordinate grid 720x1280 on a 1080x1920 panel.

### Configuration

- Kernel arguments evb10-touch=1, evb10-touch-xmax=720, evb10-touch-ymax=1280, evb10-hid=1, evb10-hid-input=1, sheng-touch-hid=1.
- evb10-touch-khz sets the I2C5 clock \(100 to 400, default 100\). evb10-touch-demo=SECS plays scripted gestures without a finger from SECS seconds after the first poll \(a swipe up, then left and right swipes of 0.8 s every 7 s\), which is how the frame rate is measured without a person.

### Procedure

- Boot and watch the evb10: touch lines on the console; touch the panel and check the pointer in SpringBoard.

### Development findings

- The controller reports a configured 800x480 but delivers X 9..696 and Y 10..1270: the real grid is 720x1280.
- The input device is one HID device on the IOHIDResource; the original IOHIDEventDriver attaches to it and feeds backboardd.
- The poll runs as a thread call at priority 93 about every 11.5 ms and the master busy-waits: at 100 kHz one tick costs 535 us on average \(the slowest tick of a window of 1000 was 1.2 to 6.4 ms when it was preempted\), about 4.6 % of a fast core; at 400 kHz it costs 150 us \(191 us at most\). The kernel prints the average and the maximum every 1000 ticks.
- At 400 kHz the bus scan still sees 0x14 and 0x5d, reads Goodix product id 1158 and ten touch points, and counts no bus errors.

### Completion criteria

- Touch coordinates map to the panel and SpringBoard reacts.

### Current limits

- No keyboard, buttons or pen; the controller is polled every 10 ms. The 400 kHz setting was checked on the bus only: a finger on the panel at that speed was not tried.

### Next action

- Use the controller interrupt instead of polling.

### Evidence

- `source`: [I2C master and touch controller driver](https://github.com/Ken-u/UniXNU-evb10/blob/e03f9880ae8fc420fa337366a444c8888b0e3fdc/package/Evb10Touch/Evb10Touch.cpp)
- `device`: [With evb10-touch-khz=400 the poll tick took 150 us on average and 191 us at most over 1000 ticks, the I2C scan found 0x14 and 0x5d, the controller reported product id 1158, and there were no bus errors \(run tk4\)](https://github.com/Ken-u/UniXNU-evb10/blob/e03f9880ae8fc420fa337366a444c8888b0e3fdc/evidence/touch-400khz-tk4-20261030.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; EXTRA_KERNEL_ARGS="evb10-touch-khz=400" tools/xnu-probe/run-kernel.sh tk4</code>. Revision: `11d08ffb699a5a3e8140b27d0dc943ff5b129986`.
- `device`: [Checked by hand on the board \(reported 2026-10-30\): the touch screen works normally](https://github.com/Ken-u/UniXNU-evb10/blob/e03f9880ae8fc420fa337366a444c8888b0e3fdc/evidence/boot-v1-20261030.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; tools/xnu-probe/run-kernel.sh TAG, then touch the screen</code>. Revision: `833f90fb52890090ad2bdd79285cc527b00d3ead`.
- `device`: [The Goodix GT1158 answered at 0x14 on I2C5 at 100 kHz \(product id 1158, axes 720x1280 mapped to 1080x1920\), a poll tick took 536 us on average, and 352 HID reports by t+130 s drove the scripted swipes on the home screen \(run v1\)](https://github.com/Ken-u/UniXNU-evb10/blob/e03f9880ae8fc420fa337366a444c8888b0e3fdc/evidence/boot-v1-20261030.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; CAPTURE_SECS=235 EARLY_STOP=0 EXTRA_KERNEL_ARGS="evb10-touch-demo=120 mali-timeline=1" tools/xnu-probe/run-kernel.sh v1</code>. Revision: `833f90fb52890090ad2bdd79285cc527b00d3ead`.

## GPU {#gpu}

`device-verified`

### Hardware and dependencies

- Mali-G610 \(Valhall CSF\) at 0xfb000000, CSF firmware from proprietary-files.txt, MaliMetal user-space stack \(PanVK, metal2vulkan, Metal plug-in\).

### Configuration

- Kernel arguments mali=8 and mali-metal=1; evb10-gpu-addon=1 makes the payload tool carry the Metal plug-in.
- mali-pll and mali-div choose the clock source and the divider minus one \(default mali-pll=1 mali-div=1: CPLL 1500 MHz over two, 750 MHz\); mali-npll=MHz \(400 to 1100\) retunes NPLL for source 3; mali-epri sets the priority of the encoding thread; mali-aflush=1 flushes surfaces asynchronously. The UEFI build option GPU\_RAIL\_UV sets the GPU rail in microvolts \(default 750000\).
- package/Mali is a submodule; scripts/build-mali-firmware.py generates the firmware include.

### Procedure

- Provide the firmware, build the kernel, then build the user-space stack from MaliMetal and the add-on it describes.

### Development findings

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

### Completion criteria

- The lock screen and its animations render on the Mali at a steady frame rate.

### Current limits

- No DVFS: the GPU clock is fixed \(750 MHz by default at the 0.75 V the firmware sets; 1 GHz with a firmware built for 0.85 V, not tried on the 0.75 V rail\); no interrupt-driven completion \(waits poll\), at most eight groups. At 750 MHz 8.7 % of the heavy command buffers miss their 19.3 ms deadline \(1.6 to 2.5 % at 1 GHz\) and a right swipe starts about 100 ms later than a left one. The panel was checked by hand and works normally \(see Display\).

### Next action

- Submit a command buffer while it is still being replayed, find what SpringBoard does in the 100 ms after a right swipe starts, and move completion to the GPU interrupts.

### Evidence

- `source`: [Mali driver source is the package/Mali submodule](https://github.com/Ken-u/UniXNU-evb10/blob/e03f9880ae8fc420fa337366a444c8888b0e3fdc/.gitmodules)
- `device`: [The 1 GHz steps of docs/reproduce.md with a firmware built from uefi-evb10 94ec4bd with GPU\_RAIL\_UV=850000 \(run v2\): the console shows npll 1000000 kHz locked, the cycle counter reads 1000 MHz, 511 heavy command buffers took 12.7 ms \(median\) and 15.6 ms \(90th percentile\), 2.5 % were over 19.3 ms, 53.8 frames per second with the finger down in swipes 3 to 11, no panic and no stalled GPU group in 235 s](https://github.com/Ken-u/UniXNU-evb10/blob/e03f9880ae8fc420fa337366a444c8888b0e3fdc/evidence/gpu-1ghz-v2-20261030.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; env -i HOME=$HOME USER=$USER PATH=/usr/local/bin:/usr/bin:/bin GPU_RAIL_UV=850000 ./build.sh &amp;&amp; tools/stub/build.sh &amp;&amp; CAPTURE_SECS=235 EARLY_STOP=0 EXTRA_KERNEL_ARGS="mali-pll=3 mali-div=0 mali-npll=1000 evb10-touch-demo=120 mali-timeline=1" tools/xnu-probe/run-kernel.sh v2; python3 tools/xnu-probe/cb_table.py v2 --latency</code>. Revision: `833f90fb52890090ad2bdd79285cc527b00d3ead`.
- `device`: [Boot with the committed default arguments: the Mali at 750 MHz \(cycle counter\) composited the interface for backboardd and SpringBoard, vkpipe n=76 failed=0, 504 heavy command buffers took 14.9 ms \(median\) and 18.9 ms \(90th percentile\) from commit to completion, 52.6 frames per second with the finger down in the scripted swipes 3 to 11, no panic in 235 s \(run v1\)](https://github.com/Ken-u/UniXNU-evb10/blob/e03f9880ae8fc420fa337366a444c8888b0e3fdc/evidence/boot-v1-20261030.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; CAPTURE_SECS=235 EARLY_STOP=0 EXTRA_KERNEL_ARGS="evb10-touch-demo=120 mali-timeline=1" tools/xnu-probe/run-kernel.sh v1; python3 tools/xnu-probe/cb_table.py v1 --latency; python3 tools/xnu-probe/frame_phases.py v1</code>. Revision: `833f90fb52890090ad2bdd79285cc527b00d3ead`.

## Network {#network}

`planned`

### Hardware and dependencies

- AP6398S module \(Broadcom BCM4359 C0, Wi-Fi on SDIO 3.0 and Bluetooth on UART9\) behind the DW-MSHC at 0xfe2d0000 \(SPI 204\); WL\_REG\_ON = GPIO0\_C4, 32.768 kHz low-power clock from the HYM8563 RTC CLKOUT, WL\_HOST\_WAKE = GPIO0\_B2 \(stock device tree\).
- Firmware fw\_bcm4359c0\_ag.bin and nvram\_ap6398s.txt from the Rockchip Android vendor tree, listed as optional entries in proprietary-files.txt.
- The catalog has no SDIO or Broadcom component \(Ath12kWifi is Qualcomm PCIe\); the reference for the protocol is Linux brcmfmac.

### Configuration

- No kernel driver is built for it yet. The identity probe runs from U-Boot: sdiom0 pins on function 2 through GPIO2A\_IOMUX\_SEL\_H / GPIO2B\_IOMUX\_SEL\_L in BUS\_IOC, WL\_REG\_ON high, cclk\_src\_sdio from xin24m, DW-MSHC CLKDIV 0x1e \(400 kHz\), 1-bit.

### Procedure

- Reset the board \(uefi-evb10 tools/board/hw-reset.sh reset\) and run uefi-evb10 tools/board/sdio-probe.py --enter; it powers the module, runs CMD0, CMD5, CMD3, CMD7, reads CCCR and the CIS with CMD52 and reads the ChipCommon CHIPID through the backplane window.

### Development findings

- The module answers: CMD5 returns OCR 0xb0ffff00 \(3 IO functions\), the CIS manufacturer ID is 02d0:4359 and ChipCommon CHIPID is 0x17294359, chip 0x4359 revision 9 \(C0\), with the ALP clock available after the request \(CHIPCLKCSR 0x48\).
- The IOMUX registers of GPIO2 are in BUS\_IOC \(0xfd5f8044 and 0xfd5f8048\). The offsets of the rk3588\_ds\_regs and rk3588\_p\_regs tables of pinctrl-rockchip.c are drive strength and pull in other IOC blocks; written as function selects they leave the SDIO CLK pad low and the card never answers CMD5.
- The HYM8563 CLKOUT \(the module's low-power clock\) is enabled after reset, so U-Boot and the kernel need no setup for it.
- The response register read right after a command write can still hold the previous response at 400 kHz; read RINTSTS a few times first.

### Completion criteria

- Planned. The first checkpoint \(power up and read the chip identity\) is reached from U-Boot. Done means the kernel brings the card up the same way, the firmware runs, a scan lists access points and a WPA2 join carries traffic.

### Current limits

- Nothing runs in the kernel: no SDIO host driver, no firmware download, no network interface. Only 400 kHz 1-bit was tried; 4-bit, high speed, the SDIO interrupt \(SPI 204 and the in-band interrupt\) and WL\_HOST\_WAKE were not exercised.

### Next action

- Write the DW-MSHC SDIO host for the kernel and read the same identity through it.
- Add a Broadcom FullMAC component \(backplane access, firmware and nvram download, SDPCM/BCDC, events\) with the station interface of nw\_abi.h, then adapt WifiNet.cpp.

### Evidence

- `device`: [From a freshly reset board at the U-Boot prompt, the AP6398S answered on SDIO: OCR 0xb0ffff00 with 3 IO functions, RCA 1, CIS manufacturer 02d0:4359, ChipCommon CHIPID 0x17294359 \(BCM4359 revision 9\), CHIPCLKCSR 0x48; the CLK pad toggled in 7 of 10 samples.](https://github.com/Ken-u/UniXNU-evb10/blob/e03f9880ae8fc420fa337366a444c8888b0e3fdc/evidence/wifi-sdio-id-20261030.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; tools/board/hw-reset.sh reset; sleep 25; python3 tools/board/sdio-probe.py --enter --log LOG</code>. Revision: `0d553069b92a5181ea5f41250f755e8aba96cda0`.
- `source`: [Hardware, the checkpoint, findings, firmware candidates and what is missing](https://github.com/Ken-u/UniXNU-evb10/blob/e03f9880ae8fc420fa337366a444c8888b0e3fdc/docs/network.md)

## Audio {#audio}

`not-applicable`

### Hardware and dependencies

- No audio driver is part of this port.

### Configuration

- None.

### Procedure

- None.

### Development findings

- The userland runs without an audio device.

### Completion criteria

- Out of scope.

### Current limits

- Audio is outside the current scope of the board.

### Next action

- Choose a codec path when the scope extends.

### Evidence

Collect evidence using the next action.

## Power {#power}

`not-applicable`

### Hardware and dependencies

- The board is mains powered.

### Configuration

- The ADT sets sleep-disabled through the OS profile defaults.

### Procedure

- None.

### Development findings

- Suspend and resume are not implemented. The GPU runs at a fixed clock and the CPUs at the firmware clock.

### Completion criteria

- Out of scope.

### Current limits

- No battery, regulator or clock management beyond what the drivers need to start.

### Next action

- Add CPU and GPU frequency control.

### Evidence

Collect evidence using the next action.

## Image assembly {#packaging}

`device-verified`

Components: `XnuPrelink`, `DarwinBoot`.

### Hardware and dependencies

- XNU of the OS profile, ARM64, SoC and device patch series, generated Apple device tree, payload volume of 96 MiB, owner trust-cache digests.

### Configuration

- payload.\* in board.toml and the \[adt\] tables; the device tree is generated from dts/evb10.dts.
- payload.kernel\_args lists the boot arguments grouped by purpose.

### Procedure

- Run scripts/build-evb10-kernel.sh, then ./unixnu build payload with --unique-chip-id.

### Development findings

- A rebuild from the six pushed repositories in an empty directory \(docs/reproduce.md\) reaches launchd with about 110 processes and Mali-composited frames; the feeds.toml pin of the SoC repository has to include the dts change that stops exporting interrupts on the eMMC and UART nodes, because an exported interrupts property without AAPL,phandle makes IOKit start-up take a data abort. The second trust\_cache\_sha256 entry changes with every rebuild because the user-space binaries are not bit-for-bit reproducible.
- The device series must not touch the context of the hunks of earlier series: the userland-mounts patch is generated by patches/tools/make-patches.py from a tree that has the earlier series applied.
- The Mali driver carries weak fallbacks for the display driver's GPU hand-off, because the display-less pass links it too \(kernel patches call its test hooks\); the display archive's strong definitions replace them.
- Changing the XNU patch list recreates the prepared source tree, and preparing it downloads the DriverKit headers the feed leaves out, so that rebuild needs network access \(through the proxy, if there is one, even when the build runs under env -i\).
- Each defconfig name is its own output directory \(out/evb10/&lt;os&gt;/evb10 and .../evb10\_display\), so the display scripts read the display-less kernel from the sibling directory.
- The payload rides in a boot image through U-Boot's fastboot, whose download buffer is 112 MiB; 96 MiB of payload fits, 128 MiB was refused.
- The payload step of unixnu refuses a kernel command line longer than 1000 bytes \('the kernel command line is 1018 bytes; the limit is 1000'\) before the board is touched. The defaults of board.toml are 884 bytes, so debugging arguments are added per run through EXTRA\_KERNEL\_ARGS, which replaces defaults of the same name.

### Completion criteria

- The payload boots on the board to the lock screen.

### Current limits

- The two-pass kernel build of this layout completes on Linux \(evb10\_defconfig, then evb10\_display\_defconfig; kernel.macho 55.0 MB, sha256 db5e4c058e6516d9cb886d2819d1ca02366a29b9748fbd6b15123e0023e5bf2f, the one booted in run v1\). The payload needs a platform seed and the owner trust-cache digests, which are in no repository.

### Next action

- Make the user-space build reproducible, or compute the second trust\_cache\_sha256 entry in the payload step, so that board.toml does not change with every rebuild.

### Evidence

- `source`: [Device patch order](https://github.com/Ken-u/UniXNU-evb10/blob/e03f9880ae8fc420fa337366a444c8888b0e3fdc/patches/xnu/series)
- `device`: [A payload assembled from this layout \(96 MiB in a 106553344-byte boot image\) booted through U-Boot's fastboot to a running backboardd and SpringBoard with Mali-composited frames and no panic in 235 s; kernel.macho 55017472 bytes, sha256 db5e4c05 \(run v1\)](https://github.com/Ken-u/UniXNU-evb10/blob/e03f9880ae8fc420fa337366a444c8888b0e3fdc/evidence/boot-v1-20261030.txt)
  Command: <code>cd UniXNU-evb10 &amp;&amp; scripts/build-evb10-kernel.sh; cd ../uefi-evb10 &amp;&amp; CAPTURE_SECS=235 EARLY_STOP=0 EXTRA_KERNEL_ARGS="evb10-touch-demo=120 mali-timeline=1" tools/xnu-probe/run-kernel.sh v1</code>. Revision: `833f90fb52890090ad2bdd79285cc527b00d3ead`.

## Diagnostics {#diagnostics}

`device-verified`

### Hardware and dependencies

- UART2 serial console at 1.5 Mbaud; DEVELOPMENT kernel.

### Configuration

- Kernel arguments -v, serial=3, vc\_mirror=1, debug=0x10014e, -enable\_kprintf\_spam.
- evb10-ps=N, evb10-bt, evb10-bt2, evb10-bt3, evb10-bt4 and mali-timeline=1 are added per run through EXTRA\_KERNEL\_ARGS: the process table costs the serial line about 3 MB a run and moves the frame rate, and the command line is limited to 1000 bytes.

### Procedure

- Read the serial console. evb10-ps prints the process table, evb10-bt prints user stacks of the named processes for symbolication on the host.

### Development findings

- Console lines longer than about 255 characters lose their tail.
- The serial input of XNU is dead on this board, so there is no command channel; judge the kernel's progress from the serial output only.
- The reset-path breadcrumbs of a secondary core are 16 words \(128 bytes\) per core, as rk3588-smp-el2.patch stores them; the dump reads them with that stride and prints the TTBR1, TCR and TTBR0 the core had when it was about to enable the MMU.

### Completion criteria

- Every boot stage prints a checkpoint to the serial console.

### Current limits

- Panics reset the board after the text is out; no panic screen is drawn.

### Next action

- Add a panic screen on the frame buffer.

### Evidence

- `source`: [Process exit trace](https://github.com/Ken-u/UniXNU-evb10/blob/e03f9880ae8fc420fa337366a444c8888b0e3fdc/patches/xnu/evb10-exit-trace.patch)
- `device`: [Every stage of the boot printed a time-stamped checkpoint: U-Boot hand-off 4.6 s, UEFI 4.8 s, the UniXNU menu entry 20.7 s, hand-off to the kernel 20.8 s, first kernel line 21.3 s, root accepted 24.0 s, launchd 54.9 s, backboardd on the Mali 69.4 s and SpringBoard 96.1 s \(run v1\)](https://github.com/Ken-u/UniXNU-evb10/blob/e03f9880ae8fc420fa337366a444c8888b0e3fdc/evidence/boot-v1-20261030.txt)
  Command: <code>cd uefi-evb10 &amp;&amp; CAPTURE_SECS=235 EARLY_STOP=0 EXTRA_KERNEL_ARGS="evb10-touch-demo=120 mali-timeline=1" tools/xnu-probe/run-kernel.sh v1</code>. Revision: `833f90fb52890090ad2bdd79285cc527b00d3ead`.

</div>
