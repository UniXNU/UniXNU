# 三星 Galaxy S7 Edge（hero2lte）

[DokuroMitsukai/UniXNU-hero2lte](https://github.com/DokuroMitsukai/UniXNU-hero2lte)

<div v-pre>

Samsung Galaxy S7 Edge \(SM-G935F\) on Exynos 8890. Phase 1 is a Mu-Silicium UEFI firmware with display and keypad input. XNU uses ArmCpu's GICv2 path and still requires native storage, display, input and power drivers, plus verified EFS/CPEFS backups before any wipe.

源记录: [porting.toml](https://github.com/DokuroMitsukai/UniXNU-hero2lte/blob/33ca6933fc94aeced28610b9e1fe5743e7f172dd/porting.toml), `33ca6933fc94aeced28610b9e1fe5743e7f172dd`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `host-verified` |
| [固件与启动](#firmware) | `device-verified` |
| [CPU 与中断](#cpu) | `implemented` |
| [内存与 DMA](#memory) | `planned` |
| [存储与根卷](#storage) | `planned` |
| [显示](#display) | `device-verified` |
| [输入](#input) | `device-verified` |
| [GPU](#gpu) | `planned` |
| [网络](#network) | `planned` |
| [音频](#audio) | `planned` |
| [电源](#power) | `planned` |
| [镜像组装](#packaging) | `host-verified` |
| [诊断](#diagnostics) | `planned` |

## 配置 {#configuration}

`host-verified`

### 硬件与依赖

- SM-G935F \(hero2lte\), Exynos 8890, bootloader G935FXXS6ESI4, framebuffer at 0xE2A00000.
- iPadOS 17.7.11 build 21H461 is the only OS profile in this UniXNU revision.

### 配置

- board.soc = Exynos 8890; board.soc\_source = exynos8890; board.os\_profile = ipados-17.7.11-21H461; schema\_version = 2.
- Firmware paths select the DokuroMitsukai/Mu-Silicium hero2lte package and the five Mu\_Basecore patches that package requires.

### 操作步骤

- Run ./unixnu defconfig hero2lte\_defconfig -D ../UniXNU-hero2lte from UniXNU.
- Run ./unixnu fetch -D ../UniXNU-hero2lte to resolve base sources and write unixnu.lock.
- Run ./unixnu status --json -D ../UniXNU-hero2lte and review profiles, components, source pins and patch order.

### 开发经验

- The ARM64, SoC, OS and device tables merge in that order. Ordinary arrays replace inherited arrays, so board.toml repeats the complete component, fragment and patch-series lists.
- The SM-G935F keeps TWRP on RECOVERY. No configuration step touches that partition.

### 完成条件

- All source pins resolve; every selected component has an area; status shows the intended profiles and patch order.

### 当前范围

- The published SoC feed is pinned in feeds.toml and unixnu.lock; fetch succeeds without a local source override.
- The UEFI checkpoint exists; no XNU kernel, payload or storage checkpoint exists yet.

### 下一步

- Keep the published SoC revision synchronized between feeds.toml and unixnu.lock.

### 证据

- `source`: [Board identity, component selection, firmware paths and boot image parameters](https://github.com/DokuroMitsukai/UniXNU-hero2lte/blob/33ca6933fc94aeced28610b9e1fe5743e7f172dd/board.toml)
- `host`: [schema\_version 2 resolved the arch, exynos8890, iPadOS and device profiles with the selected components and patch series](https://github.com/DokuroMitsukai/UniXNU-hero2lte/blob/33ca6933fc94aeced28610b9e1fe5743e7f172dd/unixnu.lock)
  Command: <code>./unixnu status --json -D ../UniXNU-hero2lte</code>. Revision: `e9fb02f99c4cc2e6c882b1c2b6443fd342bc85e0`.

## 固件与启动 {#firmware}

`device-verified`

组件: `DarwinBoot`.

### 硬件与依赖

- Mu-Silicium hero2lte firmware, S-Boot framebuffer at 0xE2A00000 with size 0xE10000, UEFI FD base 0xB1200000 and size 0x200000.
- Firmware version G935FXXS6ESI4 and the five Mu\_Basecore patches used by the package.

### 配置

- firmware.config = hero2lte; DSC = Platforms/Samsung/hero2ltePkg/hero2lte.dsc; FD = Build/hero2ltePkg/&\#123;target&\#125;\_CLANGPDB/FV/SILICIUM\_UEFI.fd.
- The package list mirrors the working Mu-Silicium build and adds &\#123;tree&\#125;/package and &\#123;tree&\#125;/drivers/DarwinBoot for UniXNU.

### 操作步骤

- The standalone build runs ./build-hero2lte.sh -c at the workspace root; test\_bootshim.py and test\_hero2lte\_keypad.py pass.
- The DSC and DXE.inc add UniXNU.inf, UniXNUDxe.inf, UniXNURamDiskDxe.inf, DarwinBoot.inf, DiskIoDxe, PartitionDxe, EnglishDxe and Fat behind UNIXNU\_PAYLOAD=1.
- ./unixnu build firmware --uefi ../Mu-Silicium --target RELEASE -D ../UniXNU-hero2lte applies the five base patches and builds the 2 MiB FD.
- Flash the 40 MiB Android v0 boot image to BOOT from TWRP, verify the partition readback hash, and boot it.

### 开发经验

- The standalone image is an Android v0 header at 0x10000000 with kernel at 0x10008000 and tags at 0x10000100; the kernel field is exactly BootShim plus the 2 MiB FD.
- S-Boot accepts both the stock-form image with DTBH and footer and the standalone v0 image; both reached the UEFI UI.
- The standalone build is bit-for-bit reproducible and the DECON trigger is preserved instead of writing the Exynos 8895 value 0x1281.
- With UNIXNU\_PAYLOAD=1 the UniXNU firmware build links UniXNU, UniXNUDxe, UniXNURamDiskDxe and DarwinBoot. FVMAIN grows from 0x20a000 to 0x235000 inside the 2 MiB FD.
- The safemem image with FD, stack and heap at 0xB1200000-0xBFF40000 reached UEFI. The bring-up image then toggled the timer block, accepted volume, home and power keys, and advanced the counter.

### 完成条件

- Firmware builds, enters UniXNU, publishes the framebuffer, keeps the payload FAT readable and preserves the reserved-memory ranges.

### 当前范围

- The UniXNU-integrated firmware \(UNIXNU\_PAYLOAD=1\) has not been booted; no payload or boot image exists yet.
- No ARM generic-timer interrupt has been delivered through the XNU path.

### 下一步

- Boot each firmware change to the UEFI UI; the next milestone is the XNU handoff with the GICv2 path now implemented.

### 证据

- `source`: [hero2lte firmware package, keypad library, host tests and optional UniXNU payload integration](https://github.com/DokuroMitsukai/Mu-Silicium/commit/5790015a98714044d72d5037cea300b40f66a2e0)
- `host`: [2 MiB SILICIUM\_UEFI.fd contains UniXNU, UniXNUDxe, UniXNURamDiskDxe and DarwinBoot; FVMAIN used 0x235000 and FVMAIN\_COMPACT kept 0x194998 free](https://github.com/DokuroMitsukai/UniXNU-hero2lte/blob/33ca6933fc94aeced28610b9e1fe5743e7f172dd/board.toml)
  Command: <code>./unixnu build firmware --uefi ../Mu-Silicium --target RELEASE -D ../UniXNU-hero2lte</code>. Revision: `5790015a98714044d72d5037cea300b40f66a2e0`.
- `device`: [readback matched 011d3abf...; timer block toggled magenta/cyan, volume/home/power keys were accepted, counter advanced, manual reboot to TWRP](https://github.com/DokuroMitsukai/UniXNU-hero2lte/blob/33ca6933fc94aeced28610b9e1fe5743e7f172dd/evidence/uefi-bringup-20261026.txt)
  Command: <code>adb push out/boot-uefi-samsung-bringup.img /tmp/boot-bringup.img; adb shell 'dd if=/tmp/boot-bringup.img of=/dev/block/sda5 bs=1M; sync; sha256sum /dev/block/sda5'; adb reboot</code>. Revision: `9f984f86636492269fff9297163d98b89c3cea65`.

## CPU 与中断 {#cpu}

`implemented`

组件: `ArmCpu`, `ArmDTPlatform`, `SoftwareAES`.

### 硬件与依赖

- Four Mongoose cores at MPIDR 0x0-0x3 and four Cortex-A53 cores at MPIDR 0x100-0x103 with a 26 MHz generic timer.
- GIC-400 at 0x11001000: distributor 0x11001000, CPU interface 0x11002000, GICH 0x11004000 and GICV 0x11006000; PPIs 13, 14, 11 and 10.

### 配置

- exynos8890.dtsi declares all eight CPUs, PSCI 0.2 over SMC, GICv2 and the generic timer. hero2lte.dts enables only cpu0 for the first bring-up.
- ArmCpu and ArmDTPlatform come from the UniXNU catalog. SoftwareAES keeps the shared ARM64 component set complete.

### 操作步骤

- Compile the board DTS and inspect /cpus, /psci, /arm-io/intc and timebase-frequency in the generated ADT.
- Record per-CPU entry, timer interrupts and IPI delivery on hardware.

### 开发经验

- ArmCpu accepts arm,cortex-a15-gic and maps the distributor plus the banked GICC, uses PPI 27 for the virtual timer, sends SGI 0 through GICD\_SGIR, and leaves GICD\_IGROUPR to firmware. A standalone QEMU GIC-400 test passes the timer and self-SGI path.
- The stock timer node sets use-clocksource-only and Android uses MCT ticks for events. The architectural timer PPI is unvalidated on hardware.
- Cluster 0 is Mongoose and cluster 1 is Cortex-A53 on this SoC, the opposite of the usual big-little numbering.
- UEFI's ArmGicDxe path handled the GIC-400 and timer interrupts during the bring-up test: the probe toggled every 200 ms and key notifies arrived.

### 完成条件

- Every enabled CPU reaches its entry checkpoint and timer and IPI handling works on each enabled CPU.

### 当前范围

- ArmCpu's GICv2 path enables only the boot CPU interface; secondary-core bring-up is not implemented.
- The XNU kernel handoff and timer delivery through ArmCpu have not been observed on hardware.
- Only one CPU is enabled.

### 下一步

- Boot the built XNU image on the device and observe GICv2 timer and IPI delivery, then extend GICv2 secondary-core startup.

### 证据

- `source`: [Board CPU selection on top of the shared exynos8890.dtsi](https://github.com/DokuroMitsukai/UniXNU-hero2lte/blob/33ca6933fc94aeced28610b9e1fe5743e7f172dd/dts/hero2lte.dts)
- `source`: [UEFI GICv2 and timer interrupt handling observed on hardware; ArmCpu's own GIC path was not used](https://github.com/DokuroMitsukai/UniXNU-hero2lte/blob/33ca6933fc94aeced28610b9e1fe5743e7f172dd/evidence/uefi-bringup-20261026.txt)
- `source`: [Four-range GICv2 device tree, 24-byte arm-io range translation, distributor, banked CPU interface, PPI 27 timer, GICD\_SGIR IPI, firmware-owned interrupt group and QEMU GIC-400 test](https://github.com/DokuroMitsukai/ArmCpu/commit/c9c4bd87cabc1fe6736e171cd2540313ac4b7883)
- `host`: [clean macOS clone: submodule update fetched ArmCpu c9c4bd8 without an override, component-ArmCpu passed the -Werror object audit and kernel.macho sha256 d30e2c9f0cc5f6fd8853b107ee428c720e10103deec966797706fce5a75578c1](https://github.com/DokuroMitsukai/UniXNU/actions/runs/40278142422)
  Command: <code>./unixnu build kernel (workflow_dispatch, steps=kernel, pre_build empty)</code>. Revision: `14529f5d63bfd1f53ba3c8648fd354609c434762`.
- `host`: [local Linux host build with upstream clang: kernel.macho 51073024 bytes, Mach-O arm64 NOUNDEFS, sha256 680afe58f1c0fc53d387a61d1717827cb510ad59909892822deaba331bb7e58e](https://github.com/DokuroMitsukai/UniXNU/commit/7098f082321552babbec7fb1e1e09b740b90668f)
  Command: <code>UNIXNU_TOOLCHAIN=&lt;prefix&gt; ./unixnu build kernel -D ../UniXNU-hero2lte</code>. Revision: `7098f082321552babbec7fb1e1e09b740b90668f`.

## 内存与 DMA {#memory}

`planned`

### 硬件与依赖

- RAM ranges from the stock DTB: 0x80000000 with size 0x7e400000 and 0x880000000 with size 0x80000000.
- S-Boot framebuffer at 0xE2A00000 with size 0xE10000; the DT video\_frame and video\_scaler regions also reserve display buffers.

### 配置

- hero2lte.dts declares the low 0x7e400000 range as the XNU memory node and the framebuffer as reserved-memory.
- The upper 2 GiB range is not described yet because the common ADT generator currently expects one contiguous memory node.

### 操作步骤

- Compile the DTS and compare the generated ADT memory range with the stock DTB.
- Verify that DarwinBoot's owned window excludes the framebuffer and the DT video pools.

### 开发经验

- The earlier Mu-Silicium MemoryMapLib overlapped the DT video\_frame and video\_scaler pools. The safemem build now places the UEFI FD, stack and heap in the 0xB1200000-0xBFF40000 gap and reached UEFI on hardware.
- The framebuffer lies inside the low RAM range, so the XNU PMAP must reserve it before XNU maps RAM.

### 完成条件

- Every handoff and reserved range is accounted for and DMA masters use only their allocated windows.

### 当前范围

- Upper 2 GiB RAM is unused.
- The UEFI relocation is validated, but XNU reserved-memory conversion and framebuffer exclusion are unverified.

### 下一步

- Decide how the ADT generator represents the second RAM range and the display reservations, then verify the XNU PMAP.

### 证据

- `source`: [Memory range and framebuffer reservation](https://github.com/DokuroMitsukai/UniXNU-hero2lte/blob/33ca6933fc94aeced28610b9e1fe5743e7f172dd/dts/hero2lte.dts)
- `device`: [the 0xB1200000-0xBFF40000 UEFI layout reached the logo and missing-OS screen](https://github.com/DokuroMitsukai/UniXNU-hero2lte/blob/33ca6933fc94aeced28610b9e1fe5743e7f172dd/evidence/uefi-bringup-20261026.txt)
  Command: <code>adb shell 'sha256sum /dev/block/sda5'; observe UEFI after booting out/boot-uefi-samsung-safemem.img</code>. Revision: `9f984f86636492269fff9297163d98b89c3cea65`.

## 存储与根卷 {#storage}

`planned`

### 硬件与依赖

- UFS controller at 0x155A0000. The GPT uses 4096-byte logical sectors.
- USERDATA is partition 18, first LBA 2085544, last LBA 7806207.

### 配置

- The SoC DTSI describes the UFS controller and leaves it disabled.
- userdata geometry remains absent from board.toml until the storage milestone and wipe approval. EFS and CPEFS backups are now captured and verified.

### 操作步骤

- Capture EFS and CPEFS from TWRP with device-dump/capture-critical.py and verify both SHA-256 digests.
- Select or implement an Exynos UFS host driver before enabling the node.

### 开发经验

- ShengUfs targets Qualcomm UFS and cannot be reused directly.
- EFS and CPEFS were captured from TWRP and integrity-checked. The EFS images differ only in ext4 superblock counters; e2fsck reports the same 181 files and no errors.

### 完成条件

- Host facts match the board; reads return the expected GPT; the configured root volume mounts and launchd starts.

### 当前范围

- No storage driver.
- No wipe or repartition is allowed until the restore procedure is tested.

### 下一步

- Select or implement the Exynos UFS host driver, then validate read-only access before any mount or write.

### 证据

- `source`: [EFS and CPEFS captured from TWRP, hash-verified and checked with e2fsck](https://github.com/DokuroMitsukai/UniXNU-hero2lte/blob/33ca6933fc94aeced28610b9e1fe5743e7f172dd/evidence/efs-cpefs-backup-20261026.txt)

## 显示 {#display}

`device-verified`

### 硬件与依赖

- s6e3hf4 SVC\_OCTA panel at 1440x2560, 32 bpp, handed over at 0xE2A00000 by S-Boot.
- The stock DT reserves video\_frame and video\_scaler pools for the display pipeline.

### 配置

- Mu-Silicium SimpleFbDxe publishes a GOP from the S-Boot framebuffer address. No native display driver is selected yet.

### 操作步骤

- Build the Phase 1 firmware and boot it on the panel.
- Record geometry, colors and backlight behavior before adding a native driver.

### 开发经验

- The standalone firmware rendered the Project Silicium UI and the missing-OS screen on hardware. BringupTestDxe drew its timer, key bars and counter at the expected top-left positions.
- DECON's trigger register is logged and left untouched because the Exynos 8895 value is not evidence for 8890.

### 完成条件

- A known frame appears with correct geometry and colors, then userland presentation and backlight controls work.

### 当前范围

- Only the S-Boot framebuffer path is validated.
- No brightness, panel power or native scanout driver.

### 下一步

- Add panel power and backlight control, then validate a native scanout path.

### 证据

- `device`: [logo, missing-OS screen and the diagnostic timer/key/counter graphics appeared on the panel](https://github.com/DokuroMitsukai/UniXNU-hero2lte/blob/33ca6933fc94aeced28610b9e1fe5743e7f172dd/evidence/uefi-bringup-20261026.txt)
  Command: <code>boot out/boot-uefi-samsung-bringup.img and observe the panel</code>. Revision: `9f984f86636492269fff9297163d98b89c3cea65`.

## 输入 {#input}

`device-verified`

### 硬件与依赖

- gpio\_keys from the stock DTB: volume up GPA0-3, volume down GPA0-4, home GPA0-5, power GPA2-4, all active low.
- The keypad banks are at 0x10580000 with DAT at offset 0x04.

### 配置

- Mu-Silicium KeypadDeviceLib polls the GPA0 and GPA2 data registers, applies a 20 ms debounce and maps press-only events to the menu.
- The SoC DTSI does not export a pinctrl node because XNU has no Samsung pinctrl driver.

### 操作步骤

- Run Resources/Scripts/test\_hero2lte\_keypad.py in the firmware checkout.
- Press volume up, volume down, home and power in the Phase 1 firmware and record the response on hardware.

### 开发经验

- The keypad host test passes. On hardware each key produced its expected BringupTestDxe bar and advanced the accepted-event counter.
- Touch needs a separate component and has no driver yet.

### 完成条件

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive, and buttons produce expected HID reports.

### 当前范围

- The keypad path is validated only through BringupTestDxe; XNU gpio-keys integration is pending.
- Touch has no driver.

### 下一步

- Add the XNU gpio-keys path and validate release events; then inventory the touch controller.

### 证据

- `device`: [red, green, blue and white bars appeared and the accepted-event counter advanced](https://github.com/DokuroMitsukai/UniXNU-hero2lte/blob/33ca6933fc94aeced28610b9e1fe5743e7f172dd/evidence/uefi-bringup-20261026.txt)
  Command: <code>press Volume Up, Volume Down, Home and Power while BringupTestDxe runs</code>. Revision: `9f984f86636492269fff9297163d98b89c3cea65`.

## GPU {#gpu}

`planned`

### 硬件与依赖

- The stock DT exposes G3D power and DVS nodes but no Mali node.
- The GPU model, power sequence and SMMU inputs still need to be recorded from the vendor kernel.

### 配置

- No GPU component is selected. The Adreno components target Qualcomm hardware and do not apply.

### 操作步骤

- Inventory the GPU from the vendor kernel and board files before selecting a component.
- Record power-domain and SMMU requirements in this area.

### 开发经验

- No UniXNU component currently supports the Exynos 8890 GPU.

### 完成条件

- GPU submissions complete, mapping and fence handling are correct, a known image renders, and the selected Metal client presents it.

### 当前范围

- No GPU inventory, driver or hardware result.

### 下一步

- Identify the GPU and its power and SMMU inputs from the vendor kernel.

### 证据

按下一步操作收集证据。

## 网络 {#network}

`planned`

### 硬件与依赖

- The stock boot DT has no wireless controller node; the chip must be identified from the vendor kernel and board files.

### 配置

- No network component is selected.

### 操作步骤

- Inventory the wireless chip, firmware files and bus before selecting a driver.
- Add firmware paths and hashes to proprietary-files.txt.

### 开发经验

- Wi-Fi firmware and driver inputs are not collected yet.

### 完成条件

- Scanning, association, address configuration and sustained receive and transmit traffic pass with the selected firmware.

### 当前范围

- No wireless inventory or driver.

### 下一步

- Identify the wireless chip and its firmware from the vendor kernel.

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`planned`

### 硬件与依赖

- The stock boot DT describes no audio route; the codec and DSP inputs still need to be recorded.

### 配置

- No audio component is selected.

### 操作步骤

- Inventory the codec, DSP and amplifier wiring before selecting a component.

### 开发经验

- Audio hardware and firmware inputs are not collected yet.

### 完成条件

- Each declared route carries the selected audio format through playback or capture and handles start and stop correctly.

### 当前范围

- No audio inventory or driver.

### 下一步

- Identify the audio hardware from the vendor kernel and schematics.

### 证据

按下一步操作收集证据。

## 电源 {#power}

`planned`

### 硬件与依赖

- The stock DT names max77854 PMIC and MUIC, s2mpb02 sub-PMIC, max77838 and p9220 wireless charger.
- Battery and charger policy are not yet inventoried.

### 配置

- No power component is selected and no regulator or charger driver runs.

### 操作步骤

- Inventory regulators, charger and battery reporting from the vendor kernel.
- Record sleep and resume dependencies before claiming a power transition.

### 开发经验

- The firmware leaves power management to S-Boot and UEFI defaults.

### 完成条件

- Declared power controls and battery readings match observations; each claimed sleep or resume transition restores dependent peripherals.

### 当前范围

- No battery, charger or power-domain driver.

### 下一步

- Inventory the PMIC and charger topology from the vendor kernel.

### 证据

按下一步操作收集证据。

## 镜像组装 {#packaging}

`host-verified`

组件: `XnuPrelink`.

### 硬件与依赖

- XNU 10063.141.1 and Darwin 23.6.0 from the iPadOS profile.
- Android v0 boot image: base 0x10000000, kernel 0x10008000, tags 0x10000100, page size 2048.

### 配置

- patch\_series covers the arch, SoC, OS and device series in that order.
- kernel.defconfig = hero2lte\_defconfig.

### 操作步骤

- Run ./unixnu build kernel, ./unixnu build package and ./unixnu build payload once the kernel inputs exist.
- Pack the image with ./unixnu bootimg and inspect boot.json before flashing.

### 开发经验

- The standalone Mu-Silicium boot image uses the v0 layout and passes the BootShim host tests.
- A 40 MiB standalone image was written to BOOT, read back byte-for-byte and accepted by S-Boot, reaching UEFI.
- Kernel prelink succeeds against the IPSW kernelcache on both macOS CI and a Linux host, and links the GICv2 ArmCpu.
- payload.img is 201326592 bytes but BOOT holds 41943040 bytes, so the payload cannot be delivered as an Android ramdisk at the configured size\_mib.

### 完成条件

- Kernel and prelink succeed, the payload contains all declared inputs, and the boot image matches the bootloader format and size limit.

### 当前范围

- No trust cache or data ramdisk is available.
- The payload volume \(192 MiB\) is larger than the BOOT partition \(40 MiB\); delivery needs a smaller \[payload\] size\_mib or a partition with room for it.
- The UniXNU-integrated firmware with the payload has not been built or validated.

### 下一步

- Decide the payload delivery \(shrink size\_mib to the BOOT partition or use a larger partition\), then build the UniXNU firmware and boot image for the first XNU hardware checkpoint.

### 证据

- `host`: [kernel.macho sha256 680afe58f1c0fc53d387a61d1717827cb510ad59909892822deaba331bb7e58e; payload.img 201326592 bytes, payload sha256 2d9cb7e449c9353a84d55e0547d2a7eb12840035f96890854a01c7b4488162aa, kernel and ADT embedded](https://github.com/DokuroMitsukai/UniXNU/commit/7098f082321552babbec7fb1e1e09b740b90668f)
  Command: <code>./unixnu build kernel -D ../UniXNU-hero2lte; ./unixnu build payload --unique-chip-id &lt;seed&gt; -D ../UniXNU-hero2lte</code>. Revision: `7098f082321552babbec7fb1e1e09b740b90668f`.

## 诊断 {#diagnostics}

`planned`

### 硬件与依赖

- Porting record CI, UniXNU status output and firmware or kernel logs.

### 配置

- The record workflow from the template is kept. unixnu.lock pins the resolved sources.

### 操作步骤

- Run python3 scripts/porting-record.py check --device ../UniXNU-hero2lte after each record change.
- Capture the firmware log before kernel handoff once the log exporter is integrated.

### 开发经验

- Host build logs exist locally. The UEFI checkpoint was observed on the panel; no persistent firmware log was captured.
- The bring-up probe provided visual timer, key and counter evidence without a storage or serial log path.

### 完成条件

- Each claimed milestone has a reproducible command, a matching revision and an accessible result.

### 当前范围

- No QR log exporter or persistent capture in the firmware yet.
- XNU handoff and kernel logs cannot be captured on this board yet.

### 下一步

- Add a persistent firmware log path before the first XNU handoff.

### 证据

按下一步操作收集证据。

</div>
