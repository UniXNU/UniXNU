# Xiaomi Redmi K40S \(munch, 22021211RC\) \(ErodeNine\)

[ErodeNine/unixnu-munch](https://github.com/ErodeNine/unixnu-munch)

<div v-pre>

Redmi K40S \(munch\) bring-up derived from UniXNU-alioth: SM8250-AC, GOP framebuffer, FocalTech SE4 touch, UFS root. Hardware results are inherited from alioth and not yet measured on a K40S.

源记录: [porting.toml](https://github.com/ErodeNine/unixnu-munch/blob/42514dbf4b6a34f7a65171fcd02fa6c240a25038/porting.toml), `42514dbf4b6a34f7a65171fcd02fa6c240a25038`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `planned` |
| [固件与启动](#firmware) | `planned` |
| [CPU 与中断](#cpu) | `implemented` |
| [内存与 DMA](#memory) | `planned` |
| [存储与根卷](#storage) | `device-verified` |
| [显示](#display) | `implemented` |
| [输入](#input) | `implemented` |
| [GPU](#gpu) | `implemented` |
| [网络](#network) | `implemented` |
| [音频](#audio) | `planned` |
| [电源](#power) | `planned` |
| [镜像组装](#packaging) | `planned` |
| [诊断](#diagnostics) | `device-verified` |

## 配置 {#configuration}

`planned`

组件: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`, `DarwinBoot`, `AppleKeyStoreState`.

### 硬件与依赖

- Identify the configuration hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for configuration.

### 操作步骤

- Follow the configuration stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first configuration observation, its cause when established, and the resulting implementation decision.

### 完成条件

- All source pins resolve; every selected component has a record; status shows the intended overrides and patch order.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required configuration inputs before implementation.

### 证据

按下一步操作收集证据。

## 固件与启动 {#firmware}

`planned`

### 硬件与依赖

- Identify the firmware and boot hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for firmware and boot.

### 操作步骤

- Follow the firmware and boot stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first firmware and boot observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Firmware image builds, enters UniXNU, publishes the framebuffer and preserves the documented memory reservations.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required firmware and boot inputs before implementation.

### 证据

按下一步操作收集证据。

## CPU 与中断 {#cpu}

`implemented`

### 硬件与依赖

- kona: four Cortex-A55 \(cpu0-3\) and four Cortex-A77 \(cpu4-7\), MPIDR core number in Affinity1 so phys ids are 0x000-0x700. Interrupts and timers come from the ArmCpu component; secondary start is PSCI CPU\_ON over smc.

### 配置

- board.toml: sheng-smp=1 starts secondary CPUs, armcpu-spi-ipi=1 routes IPIs through software-pended SPIs, armcpu-self-ipi=1 makes each core signal itself so XNU enables its IPI \(a component argument, not one of the documented boot arguments\), armcpu-diagnostics=1 reports the bring-up. dts: unixnu,cluster-type E on cpu0-3 and P on cpu4-7.

### 操作步骤

- Apply both SoC patches \(native-smp-secondary, native-smp-type-clusters\) through the SoC repository's patch series, then build kernel, payload and boot image and boot over USB. Verify in the build tree that MAX\_CPUS is 8 in the BCM2837 block, MAX\_CPU\_CLUSTERS is 2 and \_\_ARM\_AMP\_\_ survives the later \#undef.

### 开发经验

- Without native-smp-secondary.patch the reset vector masks MPIDR with 0xFF, which is Aff0 and is zero for every kona core, so every secondary core picked the boot CPU's cpu\_data and reset handler. The boot either panicked with Invalid kernel stack pointer or hard-locked with interrupts off in early initialisation.
- unixnu,cluster-type must never ship without native-smp-type-clusters.patch. With MAX\_CPU\_CLUSTERS still 1 the topology parser takes phys\_cluster\_id = \(cluster\_type == P\), which is 1, and writes cluster\_phys\_to\_logical\[1\] past the end of a one-element stack array. Release builds do not assert: the kernel dies before the console comes up. scripts/check-smp-topology.py refuses that combination.
- Both patches are private to UniXNU-pipa, not present in UniXNU/UniXNU. They live in the SM8250 SoC repository because the topology they describe is a property of the SoC, which is why the pins differ from the SM8550 device's.

### 完成条件

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU.

### 当前范围

- Secondary CPUs have not been brought up on hardware yet. The two patches are applied only in the build feed checkout, not yet committed to FFT-infra/UniXNU-sm8250-common, so a fetch or tree refresh loses them.
- unixnu,cluster-type is still declared in the board DTS rather than the SoC DTSI.

### 下一步

- Boot the image carrying both patches and read SMP run count, armcpu\_smp\_step, psci\_rc and the boot time.

### 证据

- `source`: [Refuses a device tree that declares cluster-type without the cluster patch applied and MAX\_CPU\_CLUSTERS &gt;= 2, the combination that killed three boots silently.](https://github.com/ErodeNine/unixnu-munch/blob/42514dbf4b6a34f7a65171fcd02fa6c240a25038/scripts/check-smp-topology.py)

## 内存与 DMA {#memory}

`planned`

### 硬件与依赖

- Identify the memory and dma hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for memory and dma.

### 操作步骤

- Follow the memory and dma stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first memory and dma observation, its cause when established, and the resulting implementation decision.

### 完成条件

- All handoff regions are accounted for and each enabled DMA engine accesses its allocated range with the documented cache policy.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required memory and dma inputs before implementation.

### 证据

按下一步操作收集证据。

## 存储与根卷 {#storage}

`device-verified`

组件: `ShengUfs`, `VerifiedRoot`, `VirtioMmioBlock`, `RamBlock`.

### 硬件与依赖

- UFS 3.1 host on SM8250, bound through ShengUfs, plus the two authenticated volume windows \(OS and SystemOS\) inside userdata.
- The Data seed is a raw APFS container: scripts/prepare-owner-data-fixture.py requires NXSB at 0x20, so the ADT reserves RAMDisk rather than PackedRAMDisk.

### 配置

- CONFIG\_XNU\_NATIVE\_UFS=y, CONFIG\_XNU\_VERIFIED\_ROOT\_PROBE=y, CONFIG\_XNU\_OWNER\_ROOT\_AUDIT=y, CONFIG\_XNU\_OWNER\_ROOT\_TRUST=y.
- CONFIG\_XNU\_NATIVE\_RAM\_BLOCK=y and CONFIG\_XNU\_OWNER\_DATA\_MOUNT=y; the Data mount must go through the RamBlock IOKit device, not /dev/md0.

### 操作步骤

- ./unixnu build payload --data-ramdisk &lt;seed&gt;, then bootimg, then fastboot flash boot\_b.
- The panel reports UFS read progress and the RAMDisk capacity; the USB console carries exit records.

### 开发经验

- UFS reads run through ShengUfs and the panel reports verified blocks; the root is published only with an owner-signed policy, so CONFIG\_XNU\_VERIFIED\_ROOT\_PROBE must stay on or IOFindBSDRoot times out ten times and panics.
- The Data mount fails with ENOENT through /dev/md0 \(measured 2026-10-26, panic screen offline scratch Data mount failed: 2\); publishing the seed through RamBlock as a real IOMedia is the path that mounts.
- The Data volume is 32 MiB and holds the original private/var excluding staged\_system\_apps \(39 files, 611715 bytes\). Measured 2026-10-27: 20000 directories fit in 5.8 MiB, so capacity and inodes are not the limit for the services that fail.
- cryptexd aborts with mkdirat \[28: No space left on device\] while that volume reports 31 MiB free, so the ENOSPC names a different mount than /private/var.

### 完成条件

- The configured OS volume mounts and launchd starts; the Data volume mounts read-write as apfs and is accepted by native\_owner\_data\_prepare.
- Persistence within the allocated Data region is not yet demonstrated across a reboot.

### 当前范围

- The write that fails with ENOSPC is not yet identified: the mkdir probe that prints its path is built but has not run on hardware.
- The Data seed cannot simply be enlarged: boot\_a and boot\_b are 192 MiB and the payload is a FAT volume, so a seed larger than that does not fit.

### 下一步

- Run the mkdir probe build and read the path it prints, then decide whether the failing write is on /private/var or elsewhere.

### 证据

- `device`: [The kernel reports cryptexd aborting with mkdirat ENOSPC while the Data volume reports 31 MiB free, which places the failing write on a mount other than /private/var.](https://github.com/ErodeNine/unixnu-munch/blob/42514dbf4b6a34f7a65171fcd02fa6c240a25038/docs/evidence/2026-10-27-boot-diagnostics.md)
  Command: <code>read /dev/tty.usbmodem&lt;N&gt; at 115200 8N1 and collect EXITLOG records</code>. Revision: `24d127c47217eb580dbe3f3a94c32ad25cbaae00`.

## 显示 {#display}

`implemented`

组件: `GopFramebuffer`.

### 硬件与依赖

- The panel is 1080x2400 and the loader hands over a framebuffer at 0x9c000000 with 4320-byte rows and 32 bpp, so the display path starts from that memory rather than from a GPU.
- IOMobileFramebufferLegacy is prelinked and exports nothing, so the board archive binds each name to its original absolute address.

### 配置

- CONFIG\_XNU\_NATIVE\_LEGACY\_DISPLAY=y; offline-component-load-probes.patch calls both display entry points, so the archive must resolve them or the link fails.
- build-xnu-4k-baseline.sh force-loads libNativeLegacyDisplay.late.a and re-proves every address against this kernel on each run.

### 操作步骤

- Boot the image and read the diagnostic page rows for DISPLAY stage, CLIENT and SWAP; the USB console carries the exit records.
- A photograph of the panel is the frame evidence until a swap is submitted.

### 开发经验

- Measured 2026-10-27 on boot-usb34: the lock screen is stable, SWAP calls=7 ok=7 rej=0, and backboardd creates its resources with kret=0. Earlier builds never submitted a frame at all.
- The panel is driven directly by the kernel's own renderer, which is why the boot-progress page and the colour bands are visible before any userspace renderer runs.

### 完成条件

- A known frame appears with correct geometry and colors, then userland presentation and backlight controls work.

### 当前范围

- No wallpaper: the lock screen draws its date and time over a black field, so composition reaches the text layer only. gpu offered=0 confirms the GPU stack takes no part.

### 下一步

- Get backboardd to start before investigating frame submission: with no render server there is no client that could call Swap.

### 证据

- `device`: [DISPLAY stage=10 with CLIENT calls=4 class=IOMobileFramebufferUserClient, and SWAP calls=0: a client connects but no frame is submitted.](https://github.com/ErodeNine/unixnu-munch/blob/42514dbf4b6a34f7a65171fcd02fa6c240a25038/docs/evidence/2026-10-27-boot-diagnostics.md)
  Command: <code>read the diagnostic page and the USB console after booting the image</code>. Revision: `24d127c47217eb580dbe3f3a94c32ad25cbaae00`.

## 输入 {#input}

`implemented`

组件: `QcomGeniSpi`, `ShengHidInput`, `ShengNovatekTouch`.

### 硬件与依赖

- FocalTech FT5652 on GENI SE4 \(QUPv3 wrapper 0\), per munch-sm8250.dtsi: spi-max-frequency 6000000, interrupts &lt;39 0x2008&gt;, reset GPIO 33, irq GPIO 39, vdd L10C, vcc\_i2c L1C, display-coords 0 0 8640 19200, max-touch-number 10.

### 配置

- board.toml: native-touch=1 starts kits/munch-touch, sheng-touch-hid=1 enables the publication path in ShengHidInput, native-touch-diag=1 is a measurement-only round and must be removed for release images. SPI clock is the device tree's 6 MHz; the source is TCXO 19.2 MHz on DFS level 0.

### 操作步骤

- Build with component ShengHidInput selected and the board display recipe, which invokes build-sheng-hid-input.py and archives NativeHidInput.late.o plus hid-original-bindings.o into the force-loaded libNativeLegacyDisplay.late.a. Then build payload and boot image, verify the payload carries the built kernel, and boot over USB.

### 开发经验

- The part answers register reads \(ID 0x5652\) and returns a CRC-correct all-0xFF buffer while it has no report; an earlier version of FocalTouchProtocol.c treated that buffer as a successful empty frame, which is why every image reported frames=valid with contacts=0.
- Frame reads gated on GPIO 39 going low produced real contacts: at t=100 s two contacts, low count 284, raw 0002805f4598; the part's interrupt counter 0x8F rose from 01 to e0 and its work counter 0x91 advances 60 per second, so the sensor, the SPI link, the CRC and the interrupt line are all working.
- The HID publisher was never in the kernel: ShengHidInput compiles NativeHidInput.cpp but nothing archived it, and an object with no inbound reference is dropped from a plain archive. Selected as a component and archived by the display recipe, as UniXNU-sheng does, it links.

### 完成条件

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive, and buttons produce expected HID reports.

### 当前范围

- No HID report has reached the OS yet: native\_touch\_hid\_reports stays 0 while contacts arrive, so the remaining work is the publication path, not the sensor.
- Buttons are not implemented on this board.

### 下一步

- Boot the image that carries the archived HID objects and confirm native\_touch\_hid\_reports rises and the UI responds to a swipe.

### 证据

- `source`: [Frame parsing treats an all-0xFF payload as no data, decodes 15-bit coordinates with the low bits in the pressure byte, and records the CRC it compared so 'passed' is visible rather than inferred.](https://github.com/ErodeNine/unixnu-munch/blob/42514dbf4b6a34f7a65171fcd02fa6c240a25038/kits/munch-touch/FocalTouchProtocol.c)

## GPU {#gpu}

`implemented`

组件: `Adreno650`.

### 硬件与依赖

- Adreno 650 on SM8250-AC; chip id 0x06050002; blocks GPU 0x3d00000, GMU 0x3d6a000, GPUCC 0x3d90000, SMMU 0x3da0000.
- Firmware already embedded in package/GpuFirmwareA650.c: gmu 41548 B, sqe 31632 B, zap.mdt 6860 B + zap.b02 1676 B, concatenated for the probe's single zap image.
- The pipa fork's A650 driver \(reference/repo/Adreno650\) is the same generation as this board; the upstream Adreno740 is not.

### 配置

- board.toml passes pipa-gpu=&lt;mode&gt;; CONFIG\_XNU\_NATIVE\_ADRENO=y links the archive, which must be produced at build/adreno740/libAdreno740.a because build-xnu-4k-baseline.sh hard-codes that name and ignores CONFIG\_XNU\_NATIVE\_ADRENO\_ARCHIVE.
- CONFIG\_XNU\_NATIVE\_ADRENO\_ARCHIVE uses the &\#123;tree&\#125; token so the path is absolute and satisfies both the checkout-rooted check in scripts/unixnu/kernel.py and the tree-rooted check in the shell script.
- Mode 12 \(the Metal accelerator\) is compiled out with PIPA\_GPU\_ACCELERATOR=0: the accelerator is an IOAccelerator subclass and this kernel has no IOAccelerator class \(IOAcceleratorFamily2 is absent\).

### 操作步骤

- Build with --local-module driver:Adreno650=&lt;checkout&gt;, ADRENO650\_DRIVER, ADRENO650\_KITS and ADRENO650\_PACKAGE set; the kits and the driver are not in the generated tree because Adreno650 is not in UniXNU's catalogue.
- Boot with pipa-gpu=&lt;n&gt; and read the GPUROW lines on the console; native\_gpu\_rows is not rendered by this board's page.

### 开发经验

- Mode 1 \(read only\) runs: GPU m1 gcc=ok cc=ok smmu=skip gpu=skip io=0.
- Mode 6 powers the GPU: GPU m6 gcc=ok cc=ok smmu=ok io=0 cx1 clocks1 — the CX domain comes out of collapse and the SMMU/GMU clocks run.
- Mode 7 stops at the GMU context's Attach step: status e00002ca, routes 0, programme phase 5 with 13 writes issued and no global fault.
- Two writes to the SMMU, each with a value different from the one present, are accepted and do not take effect: SMR slot 5 0x8000007f reads back 0, sCR0 0x0026040e reads back 0x00260406. Reads through the same mapping are correct \(IDR0 0x4c017e06\) and GPUCC writes through an identically constructed window do take effect. The readable, silently unwritable register file is what a resource owned above EL1 looks like.

### 完成条件

- GPU submissions complete, mapping/fence handling is correct, a known image renders, and the selected Metal client presents it.

### 当前范围

- The GMU context cannot be built because this SMMU accepts no writes from EL1; every later step depends on it.
- Metal is unreachable for the same reason plus the missing IOAccelerator class, so the wallpaper overlay and poster rendering stay on the CPU path.

### 下一步

- Decide the route past the SMMU's EL1 write refusal: an EL2-side channel, a presentation path that needs no SMMU programming, or accepting CPU presentation on this board.

### 证据

- `device`: [Mode 1 reads and mode 6 powers the CX domain with the SMMU and GMU clocks running: gcc=ok cc=ok smmu=ok cx1 clocks1.](https://github.com/ErodeNine/unixnu-munch/blob/42514dbf4b6a34f7a65171fcd02fa6c240a25038/docs/evidence/2026-10-28-gpu-wifi-bringup.md)
  Command: <code>sh scripts/run-sheng-unattended.sh &lt;boot.img&gt; 180, then read GPUROW lines from the console capture of that run</code>. Revision: `002ccaa75267bcc70ea1ba97dfefea14c6f7211d`.
- `device`: [Writes to SMR slot 5 \(0x8000007f\) and sCR0 \(0x0026040e\) both read back the pre-existing value while IDR0 reads 0x4c017e06 through the same window.](https://github.com/ErodeNine/unixnu-munch/blob/42514dbf4b6a34f7a65171fcd02fa6c240a25038/docs/evidence/2026-10-28-gpu-wifi-bringup.md)
  Command: <code>boot a pipa-gpu=7 image and read the GPUROW14 line from the console capture</code>. Revision: `e240b0e810988bf1012b2aa37bd3ae4fd6d84e67`.

## 网络 {#network}

`implemented`

### 硬件与依赖

- QCA6390 at 17cb:1101 behind qcom,pcie@1c00000; parf 0x01c00000+0x3000, phy 0x01c06000+0x1000, dm\_core 0x60000000+0xf1d, ELBI 0x60000f20+0xa8, IATU 0x60001000+0x1000, conf 0x60100000+0x100000.
- package/munch\_pcie.c is the 723-line bring-up measured on this phone in the ios-sweet series.

### 配置

- board.toml passes pcie=&lt;steps&gt;; pcie\_skip=&lt;mask&gt; skips a step, and pcie\_skip=32 skips the PHY sequence.
- The file was wrapped in \#if defined\(ARM64\_BOARD\_CONFIG\_SWEET\) and compiled to an empty object under this board; the guard now accepts BCM2837 as well.
- The kernel's C record carries -Werror and the driver leaves struct fields implicit, so the recipe passes -Wno-missing-field-initializers; sweet\_log\_flush is shimmed because that log belongs to the ios-sweet tree.
- printf does not reach this board's console, so the driver's line\(\) tees to qcom\_usb\_debug\_write and the rows appear as PCIE &lt;step&gt;: &lt;text&gt;.

### 操作步骤

- Build with the archive entry and call munch\_pcie\_init\(\) from the late display probe; a run is pcie=&lt;n&gt; on the kernel command line.

### 开发经验

- Step 1 reads gcc pcie\_0\_gdscr = 0x22f001: PWR\_ON clear, SW\_COLLAPSE set, the controller fully off — the same value the ios-sweet series recorded.
- Step 2 powers it: writing 0x22f000 reads back 0xf822f000 within a millisecond.
- Step 3 finds the halt registers already zero; step 2's power-up cleared them.
- Step 4 reports phy\_status 0x68 with bit 6 set before any PHY write, so the bootloader left the PHY initialised and the sequence can be skipped.
- Step 9 with pcie\_skip=32 reaches the PARF: parf\_mhi\_clock\_reset\_ctrl 0x3 written to 0x13, parf\_axi\_mstr\_wr\_addr\_halt\_v2 unchanged at 0x80000014, both matching the reference.

### 完成条件

- Scanning, association, address configuration and sustained receive/transmit traffic pass with the selected firmware.

### 当前范围

- Step 10 \(DBI, configuration space, link training\) has never run here or in the reference: it needs the pipe clock the skipped PHY step would produce, and accessing DBI without it is expected to hang the bus.
- No link has ever trained \(parf\_ltssm 0\) and no endpoint has been enumerated; MHI, QMI and ath11k do not exist in this tree, and the local reference Ath12kWifi is ath12k, a different driver for a different part.

### 下一步

- Establish the pipe clock without the PHY sequence that hangs this phone, then run step 10 and read the configuration space for 17cb:1101.

### 证据

- `device`: [gcc pcie\_0\_gdscr reads 0x22f001, the value the ios-sweet series recorded for a fully collapsed controller.](https://github.com/ErodeNine/unixnu-munch/blob/42514dbf4b6a34f7a65171fcd02fa6c240a25038/docs/evidence/2026-10-28-gpu-wifi-bringup.md)
  Command: <code>boot a pcie=1 image and read the PCIE 1 lines from the console capture</code>. Revision: `dc3ab04aa4b05d38a1c372fa2ec257b3ae8547ce`.
- `device`: [Writing 0x22f000 reads back 0xf822f000 within a millisecond: the controller has power.](https://github.com/ErodeNine/unixnu-munch/blob/42514dbf4b6a34f7a65171fcd02fa6c240a25038/docs/evidence/2026-10-28-gpu-wifi-bringup.md)
  Command: <code>boot a pcie=2 image and read the PCIE 2 lines from the console capture</code>. Revision: `28be364f4dc9223a006770635dbc0f352d230401`.
- `device`: [With pcie\_skip=32 the PARF setup completes and parf\_mhi\_clock\_reset\_ctrl 0x3 becomes 0x13, matching the reference.](https://github.com/ErodeNine/unixnu-munch/blob/42514dbf4b6a34f7a65171fcd02fa6c240a25038/docs/evidence/2026-10-28-gpu-wifi-bringup.md)
  Command: <code>boot a pcie=9 pcie_skip=32 image and read the PCIE 9 lines from the console capture</code>. Revision: `eeda5a8139786ca8029044708679c40e7382eb1e`.

## 音频 {#audio}

`planned`

### 硬件与依赖

- Identify the audio hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for audio.

### 操作步骤

- Follow the audio stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first audio observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Each declared route carries the selected audio format through playback or capture and handles start/stop correctly.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required audio inputs before implementation.

### 证据

按下一步操作收集证据。

## 电源 {#power}

`planned`

### 硬件与依赖

- Identify the power hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for power.

### 操作步骤

- Follow the power stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first power observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Declared power controls and battery readings match observations; each claimed sleep/resume transition restores its dependent peripherals.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required power inputs before implementation.

### 证据

按下一步操作收集证据。

## 镜像组装 {#packaging}

`planned`

### 硬件与依赖

- Identify the image assembly hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for image assembly.

### 操作步骤

- Follow the image assembly stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first image assembly observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Kernel and prelink succeed, payload contains all declared inputs, and the boot image matches the bootloader format and size limit.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required image assembly inputs before implementation.

### 证据

按下一步操作收集证据。

## 诊断 {#diagnostics}

`device-verified`

组件: `QcomXnuUsbDebug`.

### 硬件与依赖

- The board's DWC3 controller, its apps SMMU stream, and the boot arguments qcom-usb-debug=1 and qcom-usb-ctl=1 in board.toml.
- The diagnostic page is boot-progress=2 with boot-diag-resume=10, so it returns after scanout stops.

### 配置

- board.toml selects the QcomXnuUsbDebug component and passes qcom-usb-debug=1 and qcom-usb-ctl=1.
- configs/munch\_defconfig sets CONFIG\_XNU\_BOOT\_PROGRESS=y and CONFIG\_XNU\_QCOM\_USB\_DEBUG=y.
- The apps SMMU is iommu@15000000 with qcom,skip-init; the USB node's iommus = &lt;0x47 0x00 0x00&gt; gives SID 0.

### 操作步骤

- ./unixnu build kernel, then build payload and bootimg, then fastboot flash boot\_b.
- Read the console at /dev/tty.usbmodem&lt;N&gt; with a raw 115200 8N1 tty; the dock's SN234567892 node is not the phone.
- Control frames are SXNU1 &lt;16 hex session&gt; &lt;8 hex seq&gt; &lt;VERB&gt; &lt;8 hex crc32&gt;, HELLO first to learn the session.
- One unattended round is scripts/run-sheng-unattended.sh &lt;image&gt; \[timeout\]: fastboot boot the image, wait for the board's own return, boot the reader from slot a, read and decode into build/sheng-logs/&lt;tag&gt;-&lt;boot id&gt;/, then restore the slot. Fail-closed, and the timeout must exceed sheng-autoreset by 60 s.

### 开发经验

- The CDC-ACM console refused to start with error=10 core=0 domain=5. QcomUsbDomainInstall calls halted\(\) before scan\(\), so a PRTCAPDIR of 3 would have returned CoreRunning=4; it returned 5, which proves the controller already reported device mode.
- Firmware leaves an SMR entry for SID 0 pointing at context bank 5 with SCTLR=0xe0 \(M=0\) and TTBR0=0: the stream is programmed but no table exists under it. scan\(\) now reclaims that slot only when translation is off and there is no table, and still refuses a bank that holds a live mapping.
- With that, the console enumerates as 1209:316d named QcomXnuUsbDebug and the kernel log is readable on the host. It is the only channel that keeps a record after the panel has moved on.
- printf and kprintf both fail to reach the console: a DEVELOPMENT kernel leaves disable\_kprintf\_output true without -enable\_kprintf\_spam, and printf's console path did not reach the \_cnputs tee either. qcom\_usb\_debug\_write\(\) is the entry point that works.
- Exit records measured over 420 s: 180 xpcproxy exits with status=0 \(normal fork and exit\), 13 cryptexd SIGABRT with ns=18 code=2 \(OS\_REASON\_LIBSYSTEM\_CODE\_FAULT\), 11 liveactivitiesd SIGTRAP, 2 lsd SIGSEGV. Each process crashes at one fixed PC repeated, so the fault is deterministic rather than a race.
- A software REBOOT via the control channel is acknowledged \(state=queued\) but does not reach fastboot: the worker calls reboot\_kernel\(0, NULL\), an orderly restart that unmounts every filesystem and returns through UEFI. Entering fastboot needs the ABL IMEM handshake, whose address is not measured here.
- The persistent log writer runs: boot-usb101 recorded 273 rounds over 546 s with zero write errors after the console had already stopped, so the medium is the only record past the link's death.
- Returning to fastboot works with sheng-log=1 and sheng-autoreset=&lt;seconds&gt; together: boot-usb102 rebooted at 153 s and boot-usb103 at 120 s, both landing in the board's own bootloader with the PON spare cell written \('pon: subtype 04 shift 1 spare 00 -&gt; 04 want 04 rc=0 ok pon\_rc=0'\) and IMEM reading the reason back \(known=1\). PSCI alone cannot do it: SYSTEM\_RESET, SYSTEM\_RESET2\(32\) and SYSTEM\_RESET2\(64\) all report NOT\_SUPPORTED, so PS\_HOLD is the path that works.
- The reader must seek relative to the partition: /dev/block/by-name/userdata starts at LBA 0x2a8000, so the window's last 8192 blocks are skip=59086843, not the absolute LBA 61872123 the header records. Passing the absolute value reads nothing at all and looks like a hung read.
- The console's death is a latch, not a transient: dwc3\_poll\(\) returns -1 forever once d-&gt;failed is set \(Dwc3.c:570/581/584\), and nothing in the driver clears it, so the worker's retry path cannot revive the link.

### 完成条件

- The console enumerates and answers HELLO and STATUS on the board; STATUS reports usb=3 er=0.
- Every process exit and crash reaches the host console, which is what the exit-loop investigation needs.

### 当前范围

- cryptexd's fault is not yet attributed: OWNER\_CRYPTEX\_FILES is 0 by design because UNION\_SYSTEMOS requires it off, so cryptexd's expected paths do not exist. Its crash PC is captured but not symbolicated.
- The MAC exec refusal is intermittent. One boot showed backboardd, imagent, lockdownd, cfprefsd, sharingd and nfcd exiting with status=9 ns=9 code=8; the next showed none of them, so the errno the patch now reports has not been observed yet.
- Symbolication of the crash PCs against the extracted dyld shared cache was attempted and produced implausible image names, so it is not reported as a result.

### 下一步

- Make the console survive its first error: clear d-&gt;failed and re-initialise the controller from the worker, with backoff, and draw the worker's retry and error counters on the diagnostic page so the failure is readable without the link it is about.
- Attribute cryptexd's fault, then decide whether the fix is a stub, a mount change, or accepting the crash.
- Wait for the MAC refusal to reproduce and read the ip\_mac\_return value it now prints.

### 证据

- `device`: [Console enumerated as 1209:316d named QcomXnuUsbDebug; STATUS returned usb=3 er=0 with the worker polling, so the port is live in both directions.](https://github.com/ErodeNine/unixnu-munch/blob/42514dbf4b6a34f7a65171fcd02fa6c240a25038/docs/evidence/2026-10-27-boot-diagnostics.md)
  Command: <code>read /dev/tty.usbmodem&lt;N&gt; at 115200 8N1 and send SXNU1 ... HELLO / STATUS</code>. Revision: `15a15d7cc526262a64531ff56b3a33bdbc46379c`.
- `device`: [215 exit records captured. 180 xpcproxy status=0 \(normal\), 13 cryptexd ns=18 code=2, 11 liveactivitiesd sig5, 2 lsd sig11; each process repeats one fixed crash PC, so the faults are deterministic.](https://github.com/ErodeNine/unixnu-munch/blob/42514dbf4b6a34f7a65171fcd02fa6c240a25038/docs/evidence/2026-10-27-serial-exit-records.log)
  Command: <code>./unixnu build kernel; ./unixnu bootimg; fastboot flash boot_b; read the CDC-ACM console for 420 s</code>. Revision: `15a15d7cc526262a64531ff56b3a33bdbc46379c`.

</div>
