# Samsung Galaxy S9 \(starlte, SM-G960F, Exynos 9810\): HakiOS, iOS 16.5 on XNU; not built on the UniXNU tree

[Scion-Project/scion-starlte](https://github.com/Scion-Project/scion-starlte)

<div v-pre>

Samsung Galaxy S9 \(SM-G960F, Exynos 9810\) running iOS 16.5 on XNU through HakiOS. Upstream: based on HakiOS \(Scion-Project/scion-kernel, from oosexgang's HakiOS\), not on the UniXNU tree; no UniXNU components are used. Seen on the phone 1-3 November 2026, and on by default on every image \(configs/starlte.config, README.md, Defaults\): six cores, touch, battery, haptics, USB console, the S6E3HA8 panel through the DPP's scaler with zero-copy scan-out, brightness slider, Mali-G72 through Mesa Panfrost, CPU DVFS governor with touch boost and TMU throttling, native UFS root and persistent /var, RTC, Wi-Fi joined from iOS's Settings with DHCP, the front camera in the stock Camera app at 30 fps, speaker audio through ABOX and the MAX98512s, the CS47L93 codec's main microphone recorded through ABOX. Seen working but not a default \(no room on the line\): the sensor hub's six sensors and iOS's orientation and proximity \(shub=6, SENSORS.md\); Bluetooth patched at 4 Mbaud with an LE scan from the USB console \(bt=7, BLUETOOTH.md\); the codec's microphone as iOS's \(abox\_mic=1, AUDIO.md\). Not yet: headphones, Bluetooth in iOS, modem, rear cameras, core 1, the low RAM bank.

源记录: [porting.toml](https://github.com/Scion-Project/scion-starlte/blob/5cd68c99b5987c3283243a6a079b652d8c156614/porting.toml), `5cd68c99b5987c3283243a6a079b652d8c156614`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `implemented` |
| [upstream](#upstream) | `not-applicable` |
| [固件与启动](#firmware) | `device-verified` |
| [CPU 与中断](#cpu) | `device-verified` |
| [内存与 DMA](#memory) | `device-verified` |
| [存储与根卷](#storage) | `device-verified` |
| [显示](#display) | `device-verified` |
| [输入](#input) | `device-verified` |
| [GPU](#gpu) | `device-verified` |
| [网络](#network) | `device-verified` |
| [音频](#audio) | `device-verified` |
| [电源](#power) | `device-verified` |
| [镜像组装](#packaging) | `device-verified` |
| [诊断](#diagnostics) | `device-verified` |
| [camera](#camera) | `device-verified` |
| [modem](#modem) | `planned` |

## 配置 {#configuration}

`implemented`

### 硬件与依赖

- Samsung Galaxy S9 SM-G960F \(starlte\), Exynos 9810 \(S5E9810\): 4 Cortex-A55 \(MPIDR 0x000-0x003\) and 4 Exynos M3 \(0x100-0x103\), Mali-G72 MP18, 4 GB RAM.
- Kernel tree: Scion-Project/scion-kernel main, which pins this repository by revision in devices/manifest.conf.

### 配置

- configs/starlte\_defconfig and configs/starlte.config \(EXYNOS\_M3, EXYNOS\_CAMERA and the S9 drivers built\); soc/configs/exynos9810.config; soc/soc.conf.
- The S9's defaults, the configuration seen working on the phone, are CONFIG\_ symbols at the end of configs/starlte.config: devices/starlte/mkimage.sh puts them on every image's command line \(cpus=6 bootcpu=2 m3\_prep=3 pan=0 isa\_floor=1 ... ufs=3 ... fb\_zc=1 cam\_s9=7 cam=5 abox=8 max98512=3 wifi\_pcie=6 brcmfmac=8 wifi=1\), and a run's own arguments go over them by name. Drivers not yet seen working stay off until their argument is given.

### 操作步骤

- tools/hakios-device.py sync starlte in the kernel tree, then make starlte\_defconfig &amp;&amp; make kernel.

### 开发经验

- Each driver goes up in logged steps \(driver=N\) so a first phone run is safe; device.conf records each subsystem as seen on the phone, or written and not yet seen. Diagnostics \(fps\_log, systrace, \*\_probe, \*\_log\) are never defaults.

### 完成条件

- The kernel builds with starlte\_defconfig and the image boots iOS 16.5 on the phone \(see firmware and cpu\).

### 当前范围

- The kernel's command line holds 607 characters: the defaults take 422 and a run about 155 more \(CONFIG\_CMDLINE\_RUN\), so a run's added diagnostics have about 30 left; mkimage.sh warns past that.

### 下一步

- Add each driver to the defaults once it is seen working on the phone \(the torch, the headphones; the sensors, Bluetooth and the microphone in iOS once the line has room\).

### 证据

- `source`: [Per-subsystem status of the S9 port, with the boot-args that enable each driver.](https://github.com/Scion-Project/scion-starlte/blob/cf33958052eea2d50f0d6f8225ada7b8b3f2d9b8/device.conf)
- `source`: [The S9's kernel configuration fragment.](https://github.com/Scion-Project/scion-starlte/blob/cf33958052eea2d50f0d6f8225ada7b8b3f2d9b8/configs/starlte.config)

## upstream {#upstream}

`not-applicable`

### 硬件与依赖

- HakiOS: Apple's open-source XNU \(xnu-8796.121.2\) on Android phones, with its own loader \(xnuloader\) and drivers. The S9 port lives in Scion-Project/scion-kernel \(common tree, descended from oosexgang/hakios-xnu-kernel\) and this repository \(device files, checked out at devices/starlte\).

### 配置

- No UniXNU source pin, component, kit, OS profile or package script is used. board.toml lists no components and exists only so the catalog can identify the board.

### 操作步骤

- Build and boot with the HakiOS tree as README.md \(Build, On the phone\) describes: make starlte\_defconfig, make kernel, make loader, devices/starlte/mkimage.sh.

### 开发经验

- This record follows UniXNU's porting-record format so the S9 can be listed; the port is not built on the UniXNU tree and shares no code with it.

### 完成条件

- The catalog page links to this repository and states that the port is HakiOS-based.

### 当前范围

- UniXNU's build, package and checker scripts do not build this board; its component IDs do not apply.

### 下一步

- Keep this record in step with device.conf when an area's state changes.

### 证据

按下一步操作收集证据。

## 固件与启动 {#firmware}

`device-verified`

### 硬件与依赖

- Samsung S-Boot \(bootloader unlocked\) loads an Android boot image \(header v1\) from BOOT.
- Project Silicium's Mu-Silicium starltePkg UEFI with HakiOS's changes \(uefi/\), and Silicium's Carbon Hypervisor at EL2 \(Hyp.bin, GPL-2.0\), which answers PSCI.

### 配置

- uefi/BASE pins the Silicium commit; uefi/files/.../MemoryMapLib.c reserves 0xF0000000 + 64 MB where the boot shim copies the payload.
- The boot image kernel is BootShim + UEFI FD + payload, uncompressed, without a device tree \(S-Boot uses the phone's dtb partition\).

### 操作步骤

- S-Boot -&gt; boot image -&gt; Silicium UEFI \(GOP on the panel's buffer at 0xCC000000\) -&gt; xnuloader \(platform starlte\) -&gt; XNU at EL1.

### 开发经验

- The Exynos 9810's own firmware does not do PSCI properly; Carbon at EL2 provides it and forwards CPU\_ON to EL3.
- The payload lands in the CP's region \(modem\_if\); the loader moves it to 0xD0000000 first thing \(payload\_move\) and keeps the CP's and ABOX's memory from UEFI and XNU.

### 完成条件

- The phone boots from S-Boot through UEFI and the loader into XNU and iOS's user space.

### 当前范围

- The prebuilt UEFI's Silicium base predates Carbon's update of 2026-10-13.

### 下一步

- Rebase uefi/ on a newer Silicium and rebuild prebuilt/SILICIUM\_UEFI.fd.

### 证据

- `device`: [Device run, 2 November 2026: the loader moved the payload out of the modem's region and the boot reached iOS; the CP and ABOX regions were left out of XNU's memory. The capture is kept privately \(it holds iOS's own log lines\); this entry describes it.](https://github.com/Scion-Project/scion-kernel/commit/226d304eb28203b3068a2bc774d18bd1910d89a3)
  Command: <code>USB console capture: the phone's CDC-ACM port (1209:0001, usb_gadget=5) read on the host with a serial terminal, the run's boot-args and kernel log recorded; boot-args: cpus=6 bootcpu=2 m3_prep=3 pan=0 isa_floor=1</code>. Revision: `226d304eb28203b3068a2bc774d18bd1910d89a3`.
- `source`: [How it starts: S-Boot, the boot image, Silicium with Carbon at EL2 \(PSCI\), xnuloader, XNU.](https://github.com/Scion-Project/scion-starlte/blob/cf33958052eea2d50f0d6f8225ada7b8b3f2d9b8/README.md)

## CPU 与中断 {#cpu}

`device-verified`

### 硬件与依赖

- GIC-400 \(GICv2\); 4 Cortex-A55 and 4 Exynos M3; PSCI from Carbon at EL2.
- PMU fields of the big cluster written by Samsung's kernel before any CPU\_ON \(BSP flexpmu\_cal\_system\_exynos9810.h, read for facts only\).

### 配置

- cpus=6 bootcpu=2 m3\_prep=3 pan=0 \(isa\_floor on by m3\_prep=3\): A55s 2 and 3 plus the four M3s; core 1 is parked by S-Boot and left out by the loader.

### 操作步骤

- m3\_prep=1 reads the cluster's PMU state, 2 writes the six fields with read-back, 3 lets the M3s start; each step is logged before it is taken \(drivers/core/hakios.exynos\_m3.c, patch 1508\).

### 开发经验

- An M3's CPU\_ON hung until the big cluster's PMU fields were written as Samsung's kernel does.
- PAN is ARMv8.1 and UNDEFINED on the ARMv8.0 M3, so pan=0 \(patch 1509\).
- launchd got SIGILL on an M3 when told the A55's 8.2 features; isa\_floor \(patch 1510\) reports only the ARMv8.0 set all cores share.
- A cache-coherency check across clusters \(cohtest=1, every A55 against every M3 both ways\) passed.

### 完成条件

- Six cores run iOS: two A55s and four M3s, booted on an A55.

### 当前范围

- Core 1 is unavailable \(parked by S-Boot\); an M3 does not return from CPU\_OFF, so the kernel idles with WFI; booting on an M3 \(bootcpu=4\) has not been tried.

### 下一步

- Try bootcpu=4 cpus=8 and recover core 1.

### 证据

- `device`: [Device run, 2 November 2026: six cores \(2 A55 + 4 M3\) running iOS 16.5, launchd and SpringBoard up. The capture is kept privately \(it holds iOS's own log lines\); this entry describes it.](https://github.com/Scion-Project/scion-kernel/commit/73ea2ba822b832ebc4cbd44541560a73b6492532)
  Command: <code>USB console capture: the phone's CDC-ACM port (1209:0001, usb_gadget=5) read on the host with a serial terminal, the run's boot-args and kernel log recorded; boot-args: cpus=6 bootcpu=2 m3_prep=3 pan=0 isa_floor=1</code>. Revision: `73ea2ba822b832ebc4cbd44541560a73b6492532`.
- `device`: [Device run, 2 November 2026: cohtest reported 2 A55s and 4 M3s, every pair both ways, all checks passed. The capture is kept privately \(it holds iOS's own log lines\); this entry describes it.](https://github.com/Scion-Project/scion-kernel/commit/2606efc508fc9a3a3dd9ee2a67bb45022a4bc0a6)
  Command: <code>USB console capture: the phone's CDC-ACM port (1209:0001, usb_gadget=5) read on the host with a serial terminal, the run's boot-args and kernel log recorded; boot-args: cpus=6 bootcpu=2 m3_prep=3 pan=0 isa_floor=1 cohtest=1</code>. Revision: `2606efc508fc9a3a3dd9ee2a67bb45022a4bc0a6`.

## 内存与 DMA {#memory}

`device-verified`

### 硬件与依赖

- RAM 0x80000000-0xFFFFFFFF and 0x880000000-0x8FFFFFFFF \(4 GB\); secure holes removed by Silicium's RamManagerLib.
- reserved-memory of Samsung's device tree: modem\_if 0xF0000000-0xF91FFFFF, cp\_ram\_logging, exynos\_ss, ABOX.

### 配置

- Payload at 0xD0000000 + 64 MB after payload\_move; the display's scan-out buffers 0xD4000000-0xD6FFFFFF; the camera's frames 0xD8000000-0xD9FFFFFF; UFS's own mode 0xDA000000 + 4 MB; Wi-Fi's optional DMA pool 0xDC000000 + 44 MB; fb\_zc's pool 0xDEC00000-0xE18FFFFF; one table with build-time non-overlap checks in the kernel's sys/hakios.exynos9810\_mem.h. XNU's RAM the largest free block at 0x880000000 + 2 GB.

### 操作步骤

- The loader reserves the CP, ABOX and exynos\_ss pages from UEFI \(keep\_out\_reserve\) and chooses XNU's window around them \(choose\_window\).

### 开发经验

- None of XNU's RAM is below 4 GB, so 32-bit DMA engines \(DECON's DPP, the camera's WDMA, DWC3 descriptors\) use fixed buffers below 4 GB mapped through IOKit.
- An 11 MB ml\_io\_map\_wcomb of the display buffers panicked; mapping them through IOKit works.

### 完成条件

- Boots with the payload out of the modem region and the 32-bit DMA buffers below 4 GB.

### 当前范围

- No SMMU \(SysMMU\) programming; devices use physical addresses.

### 下一步

- Program the SysMMUs where a driver needs more than a fixed buffer.

### 证据

- `device`: [Device run, 2 November 2026: the display's buffers at 0xD4000000 mapped through IOKit, frames shown by the DPP, no panic. The capture is kept privately \(it holds iOS's own log lines\); this entry describes it.](https://github.com/Scion-Project/scion-kernel/commit/f5c5dcae6501aa8990db5f2e34ac50be56b2cfa5)
  Command: <code>USB console capture: the phone's CDC-ACM port (1209:0001, usb_gadget=5) read on the host with a serial terminal, the run's boot-args and kernel log recorded; boot-args: cpus=6 bootcpu=2 m3_prep=3 pan=0 isa_floor=1 fb_dpp=1</code>. Revision: `f5c5dcae6501aa8990db5f2e34ac50be56b2cfa5`.

## 存储与根卷 {#storage}

`device-verified`

### 硬件与依赖

- UFS 2.1 host on the Exynos 9810 \(0x11120000\), as Silicium's UEFI leaves it; GPT on LUN 0 \(SYSTEM, USERDATA and the rest\).

### 配置

- ufs=3 system\_apfs=ufs\_SYSTEM ufs\_write=1 var\_hfs=ufs\_USERDATA\_data, the defaults: the kernel's own UFS driver takes the controller after a self-test against the loader's reads \(kernel PR 155, scion-starlte PR 33\), writes fenced to USERDATA, /private/var on an HFS+ volume in USERDATA made once from TWRP.
- ufs=2: block I/O through the loader and the UEFI's block service, ufs=3's fallback.

### 操作步骤

- ufs=3: references read through the loader, the controller taken as UEFI left it, every unit's head, GPTs and partition blocks compared byte for byte, writes fenced by a whitelist, then the switch; any failure falls back to ufs=2.

### 开发经验

- Loader-backed UFS reads and writes carry the root and a persistent /private/var.
- ufs=3 on the phone: the self-test and the fence test \(68 writes judged, none sent\) passed and the kernel switched to native reads \(read only\); some runs fell back to ufs=2 after a read failed past the switch, which the branch's later commits address.

### 完成条件

- iOS mounts its system from SYSTEM through the kernel's own driver and keeps /private/var in USERDATA across boots.

### 当前范围

- The controller is taken as UEFI left it \(never reset\); the loader keeps core 0 to serve ufs=2's fallback.

### 下一步

- Keep the self-test's fallback count at zero across daily runs; a reset of the controller of the kernel's own.

### 证据

- `source`: [ufs=3 merged \(kernel PR 155\): the kernel's own UFS driver after a self-test against the loader's reads, writes fenced to USERDATA.](https://github.com/Scion-Project/scion-kernel/commit/0b50896ab167da00fd92a7ed400765ff962c8a94)
- `device`: [Device runs, 2 November 2026: hfs mounted Data on ufs\_USERDATA\_data; /private/var's contents kept from one boot to the next. The capture is kept privately \(it holds iOS's own log lines\); this entry describes it.](https://github.com/Scion-Project/scion-kernel/commit/9561e4516cae85fa4839ae02ad4803aede9b03b6)
  Command: <code>USB console capture: the phone's CDC-ACM port (1209:0001, usb_gadget=5) read on the host with a serial terminal, the run's boot-args and kernel log recorded; boot-args: cpus=6 bootcpu=2 m3_prep=3 pan=0 isa_floor=1 system_apfs=ufs_SYSTEM ufs_write=1 var_hfs=ufs_USERDATA_data</code>. Revision: `9561e4516cae85fa4839ae02ad4803aede9b03b6`.
- `device`: [Device runs, 2 November 2026 \(PR branch s9/ufs-native-3\): self-test passed, fence test passed \(68 writes judged, none sent\), mode NATIVE read only; other runs fell back to ufs=2 after a read failure. The capture is kept privately \(it holds iOS's own log lines\); this entry describes it.](https://github.com/Scion-Project/scion-kernel/commit/e5bc2eb48c85b5c8317476a3ffcaf26bb5afe44d)
  Command: <code>USB console capture: the phone's CDC-ACM port (1209:0001, usb_gadget=5) read on the host with a serial terminal, the run's boot-args and kernel log recorded; boot-args: cpus=6 bootcpu=2 m3_prep=3 pan=0 isa_floor=1 ufs=3 ufs_native_ro=1</code>. Revision: `e5bc2eb48c85b5c8317476a3ffcaf26bb5afe44d`.

## 显示 {#display}

`device-verified`

### 硬件与依赖

- Samsung S6E3HA8 AMOLED, 1440 x 2960, on DSIM0; DECON with DPP channel VGF0 \(hardware scaler\).

### 配置

- fb\_dpp=1 fb\_zc=1, defaults: VGF0 scales to the panel the window server's own surface, made in fb\_zc's pool \(0xDEC00000-0xE18FFFFF\), with nothing copied \(kernel PR 160\); the scan-out buffers at 0xD4000000 otherwise; panel=1 backlight=2 brightness\_bridge=1 for brightness, defaults.

### 操作步骤

- UEFI's GOP framebuffer at 0xCC000000 at boot; fb\_dpp takes the DPP's VGF0 and flips frames at the DECON's refresh \(drivers/gpu/hakios.exynos\_dpu.c\).

### 开发经验

- The S6E3HA8 has no DCS brightness command; brightness is set by gamma and AOR through DSIM0.
- iOS 16.5's Control Center slider needed to be made operative and its value read from the slider.

### 完成条件

- iOS's frames scaled to the full panel by the DPP; the brightness slider changes the panel's brightness.

### 当前范围

- No DSIM/DECON bring-up of its own: the controller is used as UEFI leaves it.

### 下一步

- Measure frame pacing \(fps\_log\) and remove late frames.

### 证据

- `source`: [fb\_zc and mali\_gov merged \(kernel PR 160\): the window server's surface scanned out with nothing copied, the GPU's clock after its load.](https://github.com/Scion-Project/scion-kernel/commit/5a361c56cd2aa7dd117c184fd445f4057479336c)
- `device`: [Device run, 2 November 2026: exynos\_dpu attached VGF0's scaler, 3 buffers of 1125x2436 at 0xd4000000; the display's frames scaled to the panel. The capture is kept privately \(it holds iOS's own log lines\); this entry describes it.](https://github.com/Scion-Project/scion-kernel/commit/f5c5dcae6501aa8990db5f2e34ac50be56b2cfa5)
  Command: <code>USB console capture: the phone's CDC-ACM port (1209:0001, usb_gadget=5) read on the host with a serial terminal, the run's boot-args and kernel log recorded; boot-args: cpus=6 bootcpu=2 m3_prep=3 pan=0 isa_floor=1 panel=1 fb_dpp=1</code>. Revision: `f5c5dcae6501aa8990db5f2e34ac50be56b2cfa5`.
- `device`: [Device run, 2 November 2026: the Control Center brightness slider changed the panel's brightness. The capture is kept privately \(it holds iOS's own log lines\); this entry describes it.](https://github.com/Scion-Project/scion-kernel/commit/b387fc685063716f31c5f450a0917620538cbcf8)
  Command: <code>USB console capture: the phone's CDC-ACM port (1209:0001, usb_gadget=5) read on the host with a serial terminal, the run's boot-args and kernel log recorded; boot-args: cpus=6 bootcpu=2 m3_prep=3 pan=0 isa_floor=1 panel=1 backlight=2 brightness_bridge=1</code>. Revision: `b387fc685063716f31c5f450a0917620538cbcf8`.

## 输入 {#input}

`device-verified`

### 硬件与依赖

- Samsung S6SY761 touch controller on USI03's HSI2C, ten contacts.
- Power, volume and Bixby keys \(exynos\_keys\).

### 配置

- s6sy761=1; exynos\_keys=1.

### 操作步骤

- drivers/input/hakios.s6sy761.c reads contacts over HSI2C \(drivers/core/hakios.exynos\_hsi2c.c\) and feeds iOS's HID stack.

### 开发经验

- A touch read retry fixed lost events on the first live session; the touch thread runs at priority 92.

### 完成条件

- Touch drives SpringBoard.

### 当前范围

- The hardware keys are written and not yet confirmed on the phone.

### 下一步

- Confirm the keys on the phone.

### 证据

- `device`: [Device run, 1 November 2026: touch worked in SpringBoard. The capture is kept privately \(it holds iOS's own log lines\); this entry describes it.](https://github.com/Scion-Project/scion-kernel/commit/a4458d524738a4eaba424d5b73b96ac2a7830e63)
  Command: <code>USB console capture: the phone's CDC-ACM port (1209:0001, usb_gadget=5) read on the host with a serial terminal, the run's boot-args and kernel log recorded; boot-args: cpus=2 bootcpu=2 s6sy761=1</code>. Revision: `a4458d524738a4eaba424d5b73b96ac2a7830e63`.

## GPU {#gpu}

`device-verified`

### 硬件与依赖

- Mali-G72 MP18 \(Bifrost\); ACPM for its clock; Mesa's Panfrost in user space.

### 配置

- mali=9 \(nine logged steps\); HakiosMali as the kernel interface for Panfrost.

### 操作步骤

- drivers/gpu/hakios.mali.c powers and starts the GPU; CoreAnimation draws through Mesa's Panfrost \(OpenGL ES\).

### 开发经验

- CoreAnimation renders through Panfrost; the kernel logs GPU busy time and job counts every 5 s.

### 完成条件

- iOS's UI is rendered on the Mali-G72.

### 当前范围

- Metal is not yet run; nothing throttles the GPU thermally.

### 下一步

- Run Metal through the Panfrost path \(GPU.md\).

### 证据

- `device`: [Device run, 1 November 2026: mali=9 ran and CoreAnimation drew through Mesa's Panfrost. The capture is kept privately \(it holds iOS's own log lines\); this entry describes it.](https://github.com/Scion-Project/scion-kernel/commit/a4458d524738a4eaba424d5b73b96ac2a7830e63)
  Command: <code>USB console capture: the phone's CDC-ACM port (1209:0001, usb_gadget=5) read on the host with a serial terminal, the run's boot-args and kernel log recorded; boot-args: cpus=2 bootcpu=2 mali=9</code>. Revision: `a4458d524738a4eaba424d5b73b96ac2a7830e63`.

## 网络 {#network}

`device-verified`

### 硬件与依赖

- Broadcom BCM4361 \(Murata/SEMCO module\) on PCIe channel 0; firmware, NVRAM and CLM from firmware/wifi or the phone's own VENDOR partition.
- Bluetooth on UART\_BT with BT\_EN on the PCAL6524 expander.

### 配置

- wifi\_pcie=6 brcmfmac=8 brcmfmac\_poll=1 brcmfmac\_tcm\_idx=1 wifi=1, all defaults \(Linux's brcmfmac through the kernel's Linux compatibility layer, the station for iOS's Apple80211\); bt=7 for Bluetooth, not a default \(it would take the line's last 5 characters\).

### 操作步骤

- Stage 1: PMU isolation, PERST\#, WLAN\_REG\_ON, PHY PLL, root complex, LTSSM, link. Stage 2: brcmfmac probe, chip ID and OTP module ID, firmware and NVRAM into the chip's RAM, interrupt, command interface, the phone's address, the station, joining \(WPA2 by the kernel's lx\_wpa.c\); configd's DHCP on en0.

### 开发经验

- On the phone the link comes up \(Gen1 x1\), the chip reads as 4361 revision 5, the firmware runs, a scan hears the access points, and a WPA2 network is joined from iOS's Settings, with an address from DHCP and the Internet answering.

### 完成条件

- Wi-Fi joined from iOS's Settings, DHCP and the Internet: done.

### 当前范围

- Bluetooth: the chip patched at 4 Mbaud and an LE scan from the USB console \(bt=7, phone 2, 3 November\); in iOS, bluetoothd waits on BlueTool's boot.

### 下一步

- BlueTool's boot for iOS's bluetoothd \(BLUETOOTH.md, iOS\).

### 证据

- `device`: [Device runs wifi-d1 to wifi-d4, 3 November 2026 \(kernel PR 157, merged\): WPA2 joined, configd's DHCP, the gateway and the Internet answering the console's wifi ping; then iOS's Settings join. The captures are kept privately \(they hold iOS's own log lines\); this entry describes them.](https://github.com/Scion-Project/scion-kernel/commit/e4d1341140464659270bc617fea4b64c097c2533)
  Command: <code>USB console capture: the phone's CDC-ACM port (1209:0001, usb_gadget=5) read on the host with a serial terminal, the run's boot-args and kernel log recorded; boot-args: cpus=6 bootcpu=2 m3_prep=3 pan=0 isa_floor=1 ufs=3 wifi_pcie=6 brcmfmac=8 brcmfmac_poll=1 brcmfmac_tcm_idx=1 wifi=1</code>. Revision: `e4d1341140464659270bc617fea4b64c097c2533`.
- `source`: [Every Wi-Fi run on the phone and what each showed \(stages a to e\).](https://github.com/Scion-Project/scion-starlte/blob/57d00d3392ecefaddd6cecdff7617e07739d89a0/WIFI.md)

## 音频 {#audio}

`device-verified`

### 硬件与依赖

- ABOX audio subsystem; two MAX98512 amplifiers on I2C; Cirrus CS47L93 codec on SPI \(headphones, microphones\).

### 配置

- abox=8 max98512=3, defaults \(ABOX's CPU off: RDMA0 -&gt; SIFS1 -&gt; UAIF1, I2S 48 kHz 2 x 16 bits; the amplifiers on and off with UAIF1\).
- cs47l93=6, a default \(the CS47L93 on PERIC0's SPI: its ID, FLL1, MICBIAS1, IN3L, AIF1 a slave I2S\); abox rec S on the USB console records UAIF0 -&gt; WDMA1.

### 操作步骤

- Bring up the ABOX route, play a tone \(abox=7\), then hand iOS's output and volume to it \(abox=8\).

### 开发经验

- ABOX's DMA runs without its firmware at 192000 bytes a second; a 1 kHz tone and iOS's own sounds play through both amplifiers \(frames from iOS, none lost\).
- The CS47L93 answers on SPI \(ID 6371\), FLL1 locks, and its main microphone records through UAIF0 -&gt; WDMA1 at 192480 bytes a second; its tone generator came back as a clean 1 kHz sine \(phone 1, 3 November\).

### 完成条件

- A tone, then iOS's sound, from the speakers: done.

### 当前范围

- The proof is the DMA's rate, the guard's peaks and the amplifiers' registers; the microphone reaches iOS only with abox\_mic=1, not a default; the headphones are written behind cs47l93\_hp=1, not yet tried.

### 下一步

- The headphones' first run \(cs47l93\_hp=1, AUDIO.md, The headphones\).

### 证据

- `device`: [Device runs a1-b3, 3 November 2026, phone 2 \(kernel PR 163, merged\): the tone and iOS's sounds through ABOX and both MAX98512s. The captures are kept privately \(they hold iOS's own log lines\); this entry describes them.](https://github.com/Scion-Project/scion-kernel/commit/44a5cf50f72ccac9f494418ee2a9711dc49d0228)
  Command: <code>USB console capture: the phone's CDC-ACM port (1209:0001, usb_gadget=5) read on the host with a serial terminal, the run's boot-args and kernel log recorded; boot-args: cpus=6 bootcpu=2 m3_prep=3 pan=0 isa_floor=1 ufs=3 abox=8 max98512=3</code>. Revision: `44a5cf50f72ccac9f494418ee2a9711dc49d0228`.
- `source`: [The audio driver's steps, the runs and how to hear them.](https://github.com/Scion-Project/scion-starlte/blob/e600c8216ec8b43a0c7bd2f4982ac77ef2ce5e3b/AUDIO.md)

## 电源 {#power}

`device-verified`

### 硬件与依赖

- MAX77705 \(fuel gauge 0x36, charger, haptic block, MUIC USB switch\); S2MPS18 PMIC with RTC; ACPM DVFS; Exynos 9810 TMU.

### 配置

- max77705=1, max77705\_haptic=1, max77705\_usbsw=1; cpufreq\_gov=1 \(its touch and frame boosts\); tmu=3; rtc\_pmic=1: all defaults. cpufreq\_lit/cpufreq\_big fix the rates when the governor is off.

### 操作步骤

- The governor moves both clusters' rates through ACPM's DVFS within Samsung's limits, and slows them from the TMU's temperatures \(83 C big, 76 C little\).

### 开发经验

- The APM reports 0 for the CPU rates, so the governor runs on the rate it asked for; its temperatures come from the TMU driver itself.
- The battery level and charger state reach iOS; haptics are felt; the RTC read gives the time of day.

### 完成条件

- Battery, haptics, DVFS with thermal throttling and the RTC working under iOS.

### 当前范围

- Read-only PMIC/charger access; no suspend; the GPU is not throttled.

### 下一步

- Throttle the GPU from the TMU's G3D zone.

### 证据

- `device`: [Device run, 1 November 2026: battery level and charger state in iOS, vibration felt, the A55s at 1.79 GHz through ACPM DVFS. The capture is kept privately \(it holds iOS's own log lines\); this entry describes it.](https://github.com/Scion-Project/scion-kernel/commit/9aee90ff931e88447611b896543fa3cfc4b45ea4)
  Command: <code>USB console capture: the phone's CDC-ACM port (1209:0001, usb_gadget=5) read on the host with a serial terminal, the run's boot-args and kernel log recorded; boot-args: cpus=2 bootcpu=2 max77705=1 max77705_haptic=1 cpufreq_lit=1794000</code>. Revision: `9aee90ff931e88447611b896543fa3cfc4b45ea4`.
- `device`: [Device run, 2 November 2026: cpufreq\_gov logged both clusters' loads and rates each second; tmu read 8 sensors. The capture is kept privately \(it holds iOS's own log lines\); this entry describes it.](https://github.com/Scion-Project/scion-kernel/commit/569e11701ca9b1b789c18c4540c17bca29b9fd10)
  Command: <code>USB console capture: the phone's CDC-ACM port (1209:0001, usb_gadget=5) read on the host with a serial terminal, the run's boot-args and kernel log recorded; boot-args: cpus=6 bootcpu=2 m3_prep=3 pan=0 isa_floor=1 cpufreq_gov=1 tmu=3</code>. Revision: `569e11701ca9b1b789c18c4540c17bca29b9fd10`.
- `device`: [Device run, 2 November 2026: the S2MPS18 RTC read gave the time of day. The capture is kept privately \(it holds iOS's own log lines\); this entry describes it.](https://github.com/Scion-Project/scion-kernel/commit/86ec08357fb16d9bf5820b619a9e3f88cf042d1c)
  Command: <code>USB console capture: the phone's CDC-ACM port (1209:0001, usb_gadget=5) read on the host with a serial terminal, the run's boot-args and kernel log recorded; boot-args: cpus=6 bootcpu=2 m3_prep=3 pan=0 isa_floor=1 rtc_pmic=1</code>. Revision: `86ec08357fb16d9bf5820b619a9e3f88cf042d1c`.

## 镜像组装 {#packaging}

`device-verified`

### 硬件与依赖

- XNU xnu-8796.121.2 with HakiOS's patches; iOS 16.5 \(20F66\) from the user's own IPSW \(iPhone10,3/10,6\); nothing of Apple's is in this repository.

### 配置

- mkxnuimg.py UEFI\_TARGET=starlte; mkimage.sh -s SECONDS boot-args.

### 操作步骤

- make unpack IPSW=...; make starlte\_defconfig &amp;&amp; make kernel; make loader; build the user space; devices/starlte/mkimage.sh -s 120.

### 开发经验

- S-Boot will not unpack gzip and takes the device tree from the phone's dtb partition, so the image is uncompressed and carries none.

### 完成条件

- xnu-starlte.img flashed to BOOT boots iOS.

### 当前范围

- Every try is a flash: Samsung has no fastboot boot.

### 下一步

- Keep the image script in step with the loader's payload layout.

### 证据

- `device`: [Device run, 2 November 2026: an image made by mkimage.sh, flashed to BOOT from TWRP, booted iOS 16.5 on six cores. The capture is kept privately \(it holds iOS's own log lines\); this entry describes it.](https://github.com/Scion-Project/scion-kernel/commit/bcea30101a03970da042bdb1dcb29f7699f5a8c4)
  Command: <code>USB console capture: the phone's CDC-ACM port (1209:0001, usb_gadget=5) read on the host with a serial terminal, the run's boot-args and kernel log recorded; boot-args: cpus=6 bootcpu=2 m3_prep=3 pan=0 isa_floor=1</code>. Revision: `bcea30101a03970da042bdb1dcb29f7699f5a8c4`.

## 诊断 {#diagnostics}

`device-verified`

### 硬件与依赖

- DWC3 USB in device mode \(CDC-ACM 1209:0001\) with the 2.0 PHY; exynos\_ss log\_kernel for TWRP \(esslog=1\); PMU SWRESET and INFORM3.

### 配置

- usb\_gadget=5 max77705\_usbsw=1; esslog=1; mkimage.sh -s N \(loader\_return\_after\).

### 操作步骤

- The kernel's log streams live over USB with a line console; after N seconds the run ends, INFORM2/3 are written and the PMU's software reset restarts the phone into TWRP, where the log is read.

### 开发经验

- The watchdog's reset lands in BOOT; the PMU's SWRESET with INFORM3 returns to TWRP.

### 完成条件

- Each run gives a live log over USB and returns to TWRP by itself.

### 当前范围

- No resident loader to send runs to; each run is a flash.

### 下一步

- Keep every new driver's steps logged before they are taken.

### 证据

- `device`: [Device run, 1 November 2026: enumerated at high speed as 1209:0001, the log streamed live and the console answered. The capture is kept privately \(it holds iOS's own log lines\); this entry describes it.](https://github.com/Scion-Project/scion-kernel/commit/a4458d524738a4eaba424d5b73b96ac2a7830e63)
  Command: <code>USB console capture: the phone's CDC-ACM port (1209:0001, usb_gadget=5) read on the host with a serial terminal, the run's boot-args and kernel log recorded; boot-args: cpus=2 bootcpu=2 usb_gadget=5 max77705_usbsw=1</code>. Revision: `a4458d524738a4eaba424d5b73b96ac2a7830e63`.
- `device`: [Device run, 2 November 2026: the run ended on time and the phone restarted into TWRP through the PMU's software reset. The capture is kept privately \(it holds iOS's own log lines\); this entry describes it.](https://github.com/Scion-Project/scion-kernel/commit/63c51c6c1c0b1eee9198fd18ed78d5bb984749d1)
  Command: <code>USB console capture: the phone's CDC-ACM port (1209:0001, usb_gadget=5) read on the host with a serial terminal, the run's boot-args and kernel log recorded; boot-args: cpus=6 bootcpu=2 m3_prep=3 pan=0 isa_floor=1 loader_return_after=150</code>. Revision: `63c51c6c1c0b1eee9198fd18ed78d5bb984749d1`.

## camera {#camera}

`device-verified`

### 硬件与依赖

- Front S5K3H1 sensor: supplies on the S2MPB02, MCLK, I2C; ISPPRE domain, CSIS1 and its D-PHY, VC0's DMA.

### 配置

- cam\_s9=7 cam=5, defaults: the sensor streaming into a ring of four frames at 0xD8000000, /dev/hakios-camera, and iOS's camera stack through libhakios.media.

### 操作步骤

- Supplies and model ID, then the domain, the CSIS test pattern, one sensor frame in RAW10 1632 x 1224, camshot, then streaming at 30 frames a second.

### 开发经验

- The front camera auto-exposed, demosaiced at 1632 x 1224, streams at 30 frames a second into the stock Camera app's preview.

### 完成条件

- The stock Camera app shows the front camera: done.

### 当前范围

- No ISP firmware \(the processing is the kernel's and user space's own\); rear cameras not started.

### 下一步

- The rear cameras \(CAMERA.md\).

### 证据

- `device`: [Device run cn3-7, 3 November 2026 \(kernel PR 162, merged\): the front camera streaming at 30 frames a second into the stock Camera app's preview. The capture is kept privately \(it holds iOS's own log lines\); this entry describes it.](https://github.com/Scion-Project/scion-kernel/commit/faeb2ec93aac73365372245ab72403179775d537)
  Command: <code>USB console capture: the phone's CDC-ACM port (1209:0001, usb_gadget=5) read on the host with a serial terminal, the run's boot-args and kernel log recorded; boot-args: cpus=6 bootcpu=2 m3_prep=3 pan=0 isa_floor=1 ufs=2 cam_s9=7 cam=5</code>. Revision: `faeb2ec93aac73365372245ab72403179775d537`.
- `source`: [The camera's hardware, its steps and how iOS's camera stack is fed.](https://github.com/Scion-Project/scion-starlte/blob/a4ca1f72f5c005c03a4e7865aa1a20d4cb0a6907/CAMERA.md)

## modem {#modem}

`planned`

### 硬件与依赖

- Samsung Shannon CP; modem\_if memory 0xF0000000-0xF91FFFFF kept free by the loader; cbd/RIL behaviour from the LineageOS 24 build.

### 配置

- None yet.

### 操作步骤

- Staged milestones in docs/modem-plan.md.

### 开发经验

- The payload was moved out of the CP's region so a modem driver can have it whole.

### 完成条件

- The CP boots from its image and answers on its IPC channel.

### 当前范围

- Not started in code.

### 下一步

- Load the CP image into modem\_if and start the CP as cbd does.

### 证据

按下一步操作收集证据。

</div>
