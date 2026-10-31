# 小米 10 Ultra（cas）

[ht94911/UniXNU-cas](https://github.com/ht94911/UniXNU-cas)

<div v-pre>

Xiaomi 10 Ultra: UEFI menu and CPU0 platform start verified; moving to the standard UniXNU build with a UFS root, eight CPUs and touch.

源记录: [porting.toml](https://github.com/ht94911/UniXNU-cas/blob/5cba1411b76170abf027e312afee15669b9541d9/porting.toml), `5cba1411b76170abf027e312afee15669b9541d9`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `implemented` |
| [固件与启动](#firmware) | `device-verified` |
| [CPU 与中断](#cpu) | `device-verified` |
| [内存与 DMA](#memory) | `implemented` |
| [存储与根卷](#storage) | `planned` |
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

组件: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`, `DarwinBoot`.

### 硬件与依赖

- UniXNU format 2 layers: arm64, sm8250 SoC source, ipados-17.7.11-21H461 OS profile and the cas board.

### 配置

- board.toml schema 2 with soc\_source sm8250 and defconfig cas\_defconfig.

### 操作步骤

- Run ./unixnu defconfig cas\_defconfig, fetch, status and tree from the UniXNU checkout.

### 开发经验

- The layered configuration resolves with the pinned SoC source and component revisions.

### 完成条件

- The configuration builds a kernel, firmware, payload and boot image with the standard commands.

### 当前范围

- Only CPU0 and the minimal component set are selected; storage, display and input are pending.

### 下一步

- Add boot-progress, a 4.75 GiB owned window and the standard payload settings.

### 证据

- `source`: [Format 2 board configuration with the SM8250 and iPadOS 17.7.11 layers.](https://github.com/ht94911/UniXNU-cas/blob/5cba1411b76170abf027e312afee15669b9541d9/board.toml)

## 固件与启动 {#firmware}

`device-verified`

组件: `DarwinBoot`.

### 硬件与依赖

- uefi-cas Mu-Silicium firmware with the bounded CasBootShim, inherited framebuffer and SPMI buttons.

### 配置

- FD 0x9f000000 / 8 MiB; Android boot image header v2, page 4096; stock SoC DTB index 2.

### 操作步骤

- Boot the image with fastboot boot; ABL applies the existing DTBO.

### 开发经验

- The UniXNU menu, buttons, RAM FAT, EFI run and return and the return to Android passed three complete runs.

### 完成条件

- The firmware enters UniXNU, exposes the framebuffer and the payload volume, and starts DarwinBoot.

### 当前范围

- The standard firmware profile cas-upstream.dsc has not been booted on the phone yet.

### 下一步

- Add the static high-RAM descriptor and boot the standard firmware profile.

### 证据

- `device`: [Three complete runs of the UniXNU menu, buttons, RAM FAT, EFI return and Android return.](https://github.com/ht94911/UniXNU-cas/blob/15bc58bb060a1e3c3cd15d4220997e4e54953d0a/docs/validation.md)
  Command: <code>fastboot boot boot.img (cas-complete-001)</code>. Revision: `346a404f6cee464e3e95f6ded464caf804a1f89e`.

## CPU 与中断 {#cpu}

`device-verified`

组件: `ArmCpu`.

### 硬件与依赖

- Eight CPUs with MPIDR 0x000 to 0x700, PSCI smc, GICv3 0x17a00000/0x17a60000 and a 19.2 MHz timer.

### 配置

- CPU0 enabled; ArmCpu with the Darwin assembler separator fix.

### 操作步骤

- Boot the kernel and read the CPU0 platform checkpoints.

### 开发经验

- CPU0 returned from arm\_vm\_init, early platform expert setup, cpu\_timebase\_init and PE\_init\_cpu with CNTFRQ 19.2 MHz.

### 完成条件

- All eight CPUs run with working timer and IPI handling.

### 当前范围

- Timer interrupts after machine\_startup and the secondary CPUs are not verified yet.

### 下一步

- Enable the remaining seven CPUs after the kernel reaches the root mount.

### 证据

- `device`: [CPU0 completed VM setup and early platform and timebase initialization.](https://github.com/ht94911/UniXNU-cas/blob/15bc58bb060a1e3c3cd15d4220997e4e54953d0a/docs/cpu0-platform-clock.md)
  Command: <code>fastboot boot boot.img (candidate 005)</code>. Revision: `bae4311fe0a8c9b8d4258fe66a19b2615c3d4adb`.

## 内存与 DMA {#memory}

`implemented`

组件: `ArmDTPlatform`.

### 硬件与依赖

- DRAM banks 0x80000000+0x39900000, 0xc0000000+5 GiB and 0x200000000+6 GiB with 31 reserved regions.

### 配置

- dts/cas.dts describes the banks and reservations; DarwinBoot owns the kernel window.

### 操作步骤

- Compile the board DTS through the format 2 payload step.

### 开发经验

- A 512 MiB window at 0x100000000 maps on the phone and 256 MiB of it allocates with full read-back.

### 完成条件

- A 4.75 GiB owned window at 0x100000000 is published by UEFI and used by XNU.

### 当前范围

- The large owned window for userland has not been run yet.

### 下一步

- Publish 0x100000000 to 0x240000000 as conventional memory in UEFI.

### 证据

- `source`: [Board DRAM banks and reserved regions.](https://github.com/ht94911/UniXNU-cas/blob/5cba1411b76170abf027e312afee15669b9541d9/dts/cas.dts)

## 存储与根卷 {#storage}

`planned`

### 硬件与依赖

- UFS host 0x1d84000; userdata is LUN0 LBA 0x2c0000 to 0x3b4b7fa with 4 KiB blocks.

### 配置

- The OS and SystemOS images go to userdata; the root is read-only and Data stays in RAM.

### 操作步骤

- Port the UniXNU-umi SM8250 UFS adaptation onto the ShengUfs component.

### 开发经验

- UniXNU-umi mounts OS and SystemOS from UFS on the same SoC.

### 完成条件

- The root volume mounts from userdata and launchd starts.

### 当前范围

- No UFS driver is selected yet.

### 下一步

- Build the userdata root image and port the read-only UFS driver.

### 证据

按下一步操作收集证据。

## 显示 {#display}

`planned`

### 硬件与依赖

- DSC command-mode panel, 1080x2340, inherited framebuffer at 0x9c000000.

### 配置

- CPU presentation into the inherited framebuffer; no display controller programming.

### 操作步骤

- Port the UniXNU-umi legacy display path with GopFramebuffer.

### 开发经验

- The UEFI menu draws through the inherited framebuffer on the phone.

### 完成条件

- The Apple logo and the Hello screen appear under XNU.

### 当前范围

- No XNU display service is selected yet.

### 下一步

- Add GopFramebuffer and the legacy display package.

### 证据

按下一步操作收集证据。

## 输入 {#input}

`planned`

### 硬件与依赖

- ST FTS at 0x49 on the QUP I2C at 0xa94000, GPIO38 reset, GPIO39 interrupt; same wiring as the Xiaomi Mi 10.

### 配置

- Native GPI DMA I2C with the PM8150B GPIO5 supply, as in UniXNU-umi.

### 操作步骤

- Port the UniXNU-umi ST FTS and HID implementation.

### 开发经验

- Volume and power buttons work in the UEFI menu.

### 完成条件

- Physical touches operate the Hello screen.

### 当前范围

- No touch driver is selected yet.

### 下一步

- Port the UniXNU-umi touch package after the Hello screen appears.

### 证据

按下一步操作收集证据。

## GPU {#gpu}

`planned`

### 硬件与依赖

- Adreno 650 on SM8250.

### 配置

- No GPU component is selected.

### 操作步骤

- Evaluate the HackiOS A650 driver and the UniXNU Adreno components.

### 开发经验

- The first userland uses CPU presentation.

### 完成条件

- GPU submissions render the system interface.

### 当前范围

- GPU work starts after touch works.

### 下一步

- Inventory A650 firmware and registers after the Hello screen.

### 证据

按下一步操作收集证据。

## 网络 {#network}

`planned`

### 硬件与依赖

- QCA6390 on PCIe0.

### 配置

- No network component is selected.

### 操作步骤

- Use the HackiOS QCA6390 driver as the reference.

### 开发经验

- The cas cmd-db has no smpf2 rail, unlike the Xiaomi Mi 10.

### 完成条件

- The device scans, joins and passes traffic.

### 当前范围

- Network work starts after touch works.

### 下一步

- Map the cas power rails for QCA6390.

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`planned`

### 硬件与依赖

- ADSP audio and the AW8697 haptics.

### 配置

- No audio component is selected.

### 操作步骤

- Use the HackiOS audio references.

### 开发经验

- Audio is outside the first interactive milestone.

### 完成条件

- Playback and capture work on the selected routes.

### 当前范围

- Audio work starts after touch works.

### 下一步

- Inventory the cas audio graph after the Hello screen.

### 证据

按下一步操作收集证据。

## 电源 {#power}

`planned`

### 硬件与依赖

- PM8150 PMICs and the ApplePMGR service contract.

### 配置

- The UniXNU-umi platform power service provides the ApplePMGR interface.

### 操作步骤

- Port UmiPlatformPower for the root and userland stage.

### 开发经验

- Battery and sleep are outside the first interactive milestone.

### 完成条件

- The PMGR service matches and userland starts.

### 当前范围

- No power service is selected yet.

### 下一步

- Port the platform power service with the UFS root.

### 证据

按下一步操作收集证据。

## 镜像组装 {#packaging}

`implemented`

组件: `XnuPrelink`.

### 硬件与依赖

- Prelinked kernel, ADT, payload FAT, UEFI FD and the stock SoC DTB.

### 配置

- The payload FAT holds unixnu.toml, the kernel and its ADT.

### 操作步骤

- Run ./unixnu payload and ./unixnu bootimg.

### 开发经验

- The prelinked iPadOS 17.7.11 kernel links with the selected components.

### 完成条件

- The standard bootimg step produces the image booted on the phone.

### 当前范围

- The framework bootimg step does not support the cas header v2 DTB area and CasBootShim, so scripts/cas\_bootimg.py packs the image.

### 下一步

- Add the Data seed and trust cache to the payload for the root and userland stage.

### 证据

- `source`: [Payload and kernel settings for the standard payload step.](https://github.com/ht94911/UniXNU-cas/blob/5cba1411b76170abf027e312afee15669b9541d9/board.toml)

## 诊断 {#diagnostics}

`planned`

### 硬件与依赖

- Framebuffer at 0x9c000000 and the XNU console mapping.

### 配置

- boot-progress=2 and the panic screen.

### 操作步骤

- Port the UniXNU-umi boot-progress package.

### 开发经验

- Earlier retained-RAM trace readers are replaced by the on-screen diagnostic page.

### 完成条件

- Each boot shows its last stage, interrupt count or panic on the screen.

### 当前范围

- The boot-progress package is not ported yet.

### 下一步

- Port boot-progress and enable panic\_screen.

### 证据

按下一步操作收集证据。

</div>
