# Redmi K20 Pro / Mi 9T Pro \(raphael, SM8150\) - arm64 port of iPadOS 18.7.12 \(22H390\). Kernel from the arm64 iPadOS restore, root image from the iOS 18.7.12 paylo \(Aruvelut-123\)

[Aruvelut-123/UniXNU-raphael](https://github.com/Aruvelut-123/UniXNU-raphael)

<div v-pre>

Redmi K20 Pro / Mi 9T Pro \(raphael, SM8150\) arm64 UniXNU port. Target build is ipados-18.7.12-22H390 \(Darwin 24.6.0\): the root image comes from the iOS 18.7.12 restore of iPhone11,2, the arm64 kernelcache from the iPadOS 18.7.12 restore of iPad7,11. Configuration and image-assembly tooling are in place; kernel, firmware and every hardware area still need device verification.

源记录: [porting.toml](https://github.com/Aruvelut-123/UniXNU-raphael/blob/577e2ceda172e41aad295deeda99f4eb3fb823e3/porting.toml), `577e2ceda172e41aad295deeda99f4eb3fb823e3`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `implemented` |
| [固件与启动](#firmware) | `planned` |
| [CPU 与中断](#cpu) | `planned` |
| [内存与 DMA](#memory) | `planned` |
| [存储与根卷](#storage) | `planned` |
| [显示](#display) | `planned` |
| [输入](#input) | `planned` |
| [GPU](#gpu) | `planned` |
| [网络](#network) | `planned` |
| [音频](#audio) | `planned` |
| [电源](#power) | `planned` |
| [镜像组装](#packaging) | `planned` |
| [诊断](#diagnostics) | `planned` |

## 配置 {#configuration}

`implemented`

组件: `ArmDTPlatform`.

### 硬件与依赖

- SM8150 device identity and partition plan from the raphael board configuration
- OS profile ipados-18.7.12-22H390 \(arm64\) carried by this repository and installed into the UniXNU checkout
- iOS 18.7.12 payload IPSW and the staged iPadOS 18.7.12 arm64 kernelcache, both build 22H390
- Shared SM8150 support pinned in feeds.toml

### 配置

- format 2 board: soc\_source=sm8150, kit=raphael, os\_profile=ipados-18.7.12-22H390
- upstream UniXNU has no 18.x profile, so os-profiles/ipados-18.7.12-22H390/ is copied in by scripts/install-device-profile.py
- the arm64 kernelcache is staged by scripts/stage-arm64-kernelcache.py into the path \[kernel.prelink\] kernelcache names
- kernel fragments arch:configs/common.config and soc:configs/sm8150.config
- arm64e-only profiles are intentionally not mapped: SM8150 has no FEAT\_PAuth

### 操作步骤

- From the UniXNU checkout: python3 ../UniXNU-raphael/scripts/install-device-profile.py --unixnu .
- python3 ../UniXNU-raphael/scripts/stage-arm64-kernelcache.py --unixnu .
- ./unixnu defconfig raphael\_defconfig -D ../UniXNU-raphael, ./unixnu fetch -D ../UniXNU-raphael, then ./unixnu status --json -D ../UniXNU-raphael

### 开发经验

- arm64e-only Apple OS profiles \(iPadOS 26/27\) cannot run on this SoC \(no FEAT\_PAuth\); iPadOS 18 still ships an arm64 kernelcache because the no-PAC A10 iPad 7 runs it
- UniXNU reads exactly one IPSW per run, so the iOS payload is \[ipsw\] and the arm64 kernelcache is passed to prelink by path instead
- iPadOS and iOS share the 22H390 build ID, so the staged kernelcache needs its own output path or the two would overwrite each other in out/ipsw/22H390/
- both 22H390 dmgs are AEA encrypted, so building the root image needs macOS /usr/bin/aea
- status resolves arch=arm64, soc=sm8150, os=ipados-18.7.12-22H390 and the device board.toml

### 完成条件

- Every profile root, source pin, component closure and patch order resolves without error

### 当前范围

- Resolution success is not a boot result; nothing here has run on raphael hardware

### 下一步

- Record the resolved status output as host evidence once the CI build produces it

### 证据

- `source`: [Format 2 board definition with the arm64 ipados-18.7.12-22H390 profile \(iOS 18.7.12 payload for the root image, staged iPadOS 18.7.12 arm64 kernelcache for prelink\) and raphael\_defconfig mapping.](https://github.com/Aruvelut-123/UniXNU-raphael/blob/577e2ceda172e41aad295deeda99f4eb3fb823e3/board.toml)
- `source`: [Pinned shared SM8150 source used as the soc profile.](https://github.com/Aruvelut-123/UniXNU-raphael/blob/577e2ceda172e41aad295deeda99f4eb3fb823e3/feeds.toml)

## 固件与启动 {#firmware}

`planned`

组件: `DarwinBoot`.

### 硬件与依赖

- Mu-Silicium platform support for SM8150
- Device memory map and reserved regions for the firmware volume

### 配置

- package/firmware is a placeholder: no DSC, FDF or platform code exists yet

### 操作步骤

- Add UniXNU, UniXNUDxe, DarwinBoot, UniXNURamDiskDxe, DiskIoDxe and FatPkg to the DSC and FDF, then run ./unixnu build firmware --uefi ../uefi-raphael

### 开发经验

- Firmware integration is documented upstream but no raphael platform port exists in this repository

### 完成条件

- A firmware volume builds and UniXNU draws its boot menu on raphael

### 当前范围

- Without a firmware volume only kernel, EFI package and boot image can be produced

### 下一步

- Create the uefi-raphael Mu-Silicium platform with the required DSC and FDF modules

### 证据

按下一步操作收集证据。

## CPU 与中断 {#cpu}

`planned`

组件: `XnuPrelink`.

### 硬件与依赖

- CPU topology for SM8150 \(four Cortex-A76 plus four Cortex-A55\) from the vendor DTS

### 配置

- raphael\_defconfig carries the kernel options; CPU enablement is not yet wired to a device tree

### 操作步骤

- Build the kernel, boot it and capture the CPU bring-up log

### 开发经验

- SM8150 Cortex-A76 and A55 do not implement ARMv8.3 FEAT\_PAuth, which is why arm64e is excluded

### 完成条件

- All eight CPUs come up and the interrupt controller delivers timer interrupts

### 当前范围

- No device log exists yet; the CPU area is unverified on hardware

### 下一步

- Boot the arm64 kernel and record the per-CPU startup log

### 证据

按下一步操作收集证据。

## 内存与 DMA {#memory}

`planned`

### 硬件与依赖

- RAM size and reserved region plan for raphael

### 配置

- dts/raphael.dts declares a 4 GiB memory node; reservations are not yet described

### 操作步骤

- Extend the device tree with the reserved-memory nodes and boot the kernel

### 开发经验

- Boot page table capacity for the native 4 KiB granule is handled by the arch profile patches, not by this device

### 完成条件

- XNU maps the full RAM range and the reserved regions stay out of the kernel map

### 当前范围

- The current device tree is a skeleton and has not been used for a boot

### 下一步

- Add reserved-memory nodes for firmware, display and modem regions

### 证据

按下一步操作收集证据。

## 存储与根卷 {#storage}

`planned`

### 硬件与依赖

- GPT entry for the root partition, from the device partition table
- Shared SM8150 UFS operations from the pinned SoC repository

### 配置

- Root image is built with ./unixnu build userdata from the board partition geometry and the OS profile's IPSW
- scripts/build-root.sh prefers a unixnu partition label and falls back to userdata at flash time

### 操作步骤

- scripts/build-root.sh --ipsw restore.ipsw --dry-run, then --flash

### 开发经验

- UniXNU selects root by APFS volume UUID written into the ADT, so a boot-time partition search is not available
- Kernel and root image must be the same build \(22H390 here\); the root is the iOS 18.7.12 payload and the kernelcache the same-build iPadOS 18.7.12 arm64 one, and builds must never be mixed across Darwin versions
- the payload dmgs are AEA encrypted, so the root image can only be assembled on macOS

### 完成条件

- XNU mounts the root volume read-only and starts launchd

### 当前范围

- No root image has been built or flashed for this device yet

### 下一步

- Decrypt the iOS 18.7.12 OS dmg on macOS and fill \[root\] os\_volume\_uuid and systemos\_volume\_uuid in the board's OS profile
- Download the payload IPSW once and fill the \[ipsw.sha256\] member pins

### 证据

按下一步操作收集证据。

## 显示 {#display}

`planned`

### 硬件与依赖

- Panel timing and DSI configuration for the raphael panel

### 配置

- No display nodes are described in the device tree yet

### 操作步骤

- Boot the kernel and capture the framebuffer handoff log

### 开发经验

- GopFramebuffer is not selected for this board, so there is no handoff path yet

### 完成条件

- The kernel console and SpringBoard both render on the panel

### 当前范围

- Display is unverified; no panel timing has been collected

### 下一步

- Collect panel timings and add a display node plus the framebuffer component

### 证据

按下一步操作收集证据。

## 输入 {#input}

`planned`

### 硬件与依赖

- GT9889 touch controller wiring and I2C address

### 配置

- No input driver is selected or declared

### 操作步骤

- Integrate a HID provider and verify touch events in userspace

### 开发经验

- Touch bring-up has not started; the upstream raphael port has an independent GT9889 note

### 完成条件

- Touch events reach userspace and SpringBoard responds

### 当前范围

- No input hardware work exists in this repository

### 下一步

- Select a HID input component and record its required inputs

### 证据

按下一步操作收集证据。

## GPU {#gpu}

`planned`

### 硬件与依赖

- Adreno 640 firmware and command stream interface

### 配置

- No GPU component is selected

### 操作步骤

- Add the Adreno component chain and verify a userspace Metal or Vulkan probe

### 开发经验

- The Adreno driver family exists upstream but no raphael GPU work has been done here

### 完成条件

- A GPU client allocates a buffer and completes a queue submission

### 当前范围

- GPU is unverified and unstarted

### 下一步

- Review the Adreno component catalog entries for SM8150 compatibility

### 证据

按下一步操作收集证据。

## 网络 {#network}

`planned`

### 硬件与依赖

- WCN3990 Wi-Fi and Bluetooth firmware plus calibration data

### 配置

- No network driver is selected

### 操作步骤

- Add the wireless component chain and verify an association and a Bluetooth HCI open

### 开发经验

- Network bring-up has not started

### 完成条件

- The device associates with an access point and reports an interface to userspace

### 当前范围

- No network hardware work exists in this repository

### 下一步

- Identify the WCN3990 firmware and calibration inputs for raphael

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`planned`

### 硬件与依赖

- Audio DSP firmware and codec wiring for raphael

### 配置

- No audio component is selected

### 操作步骤

- Add audio components and verify playback from userspace

### 开发经验

- Audio bring-up has not started

### 完成条件

- A userspace client plays audio through the device speaker

### 当前范围

- No audio hardware work exists in this repository

### 下一步

- Collect the DSP firmware inputs from the vendor partition

### 证据

按下一步操作收集证据。

## 电源 {#power}

`planned`

### 硬件与依赖

- PMIC and regulator topology for raphael

### 配置

- No power component is selected

### 操作步骤

- Add the power component chain and verify rail state across a suspend and resume

### 开发经验

- Power management has not started

### 完成条件

- The device suspends and resumes without losing the framebuffer

### 当前范围

- No power hardware work exists in this repository

### 下一步

- Record the PMIC topology from the vendor device tree

### 证据

按下一步操作收集证据。

## 镜像组装 {#packaging}

`planned`

### 硬件与依赖

- Kernel, payload and device tree produced by the build steps
- IPSW disk image or a raw root image to convert

### 配置

- scripts/build.sh runs defconfig, fetch, status, kernel, package, firmware and bootimg in order
- scripts/ipsw\_to\_sparse.py converts a raw image to libsparse chunks and self-verifies the result

### 操作步骤

- python3 scripts/ipsw\_to\_sparse.py --raw-image userdata-root.img --output unixnu.sparse
- scripts/build.sh for the full artifact chain

### 开发经验

- Sparse output is produced only from a raw image; AEA-encrypted IPSW payloads need macOS tooling and the script reports that instead of emitting a bad image

### 完成条件

- boot.img and UniXNU.efi are produced and published as separate artifacts

### 当前范围

- No boot.img or UniXNU.efi has been built from this device configuration on hardware

### 下一步

- Produce both artifacts in CI and attach the resulting log as host evidence

### 证据

按下一步操作收集证据。

## 诊断 {#diagnostics}

`planned`

### 硬件与依赖

- Serial or UART access path for raphael, or a framebuffer console fallback

### 配置

- No log transport is configured for this device

### 操作步骤

- Capture firmware and kernel output during a boot attempt and attach it as device evidence

### 开发经验

- Log capture is required before any hardware area can move past planned

### 完成条件

- A boot attempt produces a readable log that is committed as evidence

### 当前范围

- No log has been captured for this port

### 下一步

- Configure a log transport and record the first boot attempt output

### 证据

按下一步操作收集证据。

</div>
