# OnePlus 13 / dodge / PJZ110: format 2 port \(Biaogo\)

[Biaogo/UniXNU-dodge](https://github.com/Biaogo/UniXNU-dodge)

<div v-pre>

OnePlus 13 PJZ110 \(dodge, SM8750\). Skip Setup and turn the on-screen HUD off for normal use. Display, touch, storage boot, and GPU scanout are device-observed. Network, audio, and long-term stability are not claimed.

源记录: [porting.toml](https://github.com/Biaogo/UniXNU-dodge/blob/e9f298d0c6b66a7aa22eca1a3c2852227dfff309/porting.toml), `e9f298d0c6b66a7aa22eca1a3c2852227dfff309`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `implemented` |
| [固件与启动](#firmware) | `implemented` |
| [CPU 与中断](#cpu) | `implemented` |
| [内存与 DMA](#memory) | `implemented` |
| [存储与根卷](#storage) | `implemented` |
| [显示](#display) | `implemented` |
| [输入](#input) | `implemented` |
| [GPU](#gpu) | `implemented` |
| [网络](#network) | `not-applicable` |
| [音频](#audio) | `not-applicable` |
| [电源](#power) | `implemented` |
| [镜像组装](#packaging) | `implemented` |
| [诊断](#diagnostics) | `implemented` |

## 配置 {#configuration}

`implemented`

组件: `NativeKeyStoreEvents`.

### 硬件与依赖

- OnePlus 13 PJZ110, OPLUS codename dodge, SM8750, iPadOS 17.7.11 \(21H461\).

### 配置

- schema\_version=2. Board name dodge. Defconfig dodge\_defconfig.

### 操作步骤

- From a UniXNU checkout: defconfig dodge\_defconfig -D &lt;this repository&gt;; fetch; status.

### 开发经验

- The published board name is dodge. Process logs stay in the private backup.

### 完成条件

- board.toml, feeds, and the defconfig name the same device.

### 当前范围

- This record does not publish private build logs or device identifiers.

### 下一步

- Keep the public tree limited to the files needed to build and boot.

### 证据

- `source`: [Board name, SoC, and OS profile are dodge / SM8750 / ipados-17.7.11-21H461.](https://github.com/Biaogo/UniXNU-dodge/blob/e9f298d0c6b66a7aa22eca1a3c2852227dfff309/board.toml)

## 固件与启动 {#firmware}

`implemented`

组件: `PaganiDarwinBoot`.

### 硬件与依赖

- Embedded UEFI payload. Firmware binaries are not stored in this repository.

### 配置

- The boot image embeds the payload. Firmware hashes stay in proprietary-files.txt.

### 操作步骤

- Build firmware, then payload and bootimg from the selected device tree.

### 开发经验

- Temporary boot is the supported trial path. Do not flash the partition that holds the installed system.

### 完成条件

- Firmware publishes a framebuffer and the documented memory reservations.

### 当前范围

- The standard initrd path is not separately claimed.

### 下一步

- Keep firmware blobs out of the public tree.

### 证据

- `source`: [Required firmware inputs are listed by hash, not embedded.](https://github.com/Biaogo/UniXNU-dodge/blob/e9f298d0c6b66a7aa22eca1a3c2852227dfff309/proprietary-files.txt)

## CPU 与中断 {#cpu}

`implemented`

组件: `PaganiArmCpu`, `PaganiArmDTPlatform`.

### 硬件与依赖

- SM8750 CPU topology and GICv3 from the board device tree.

### 配置

- Eight CPUs are selected by the board kernel arguments.

### 操作步骤

- Resolve the device tree, then build the kernel with the device patch series.

### 开发经验

- The board boots far enough to reach Setup and the desktop on this device.

### 完成条件

- All selected CPUs come online without a scheduler lock panic.

### 当前范围

- Sustained multi-core stress is not claimed.

### 下一步

- Leave scheduler experiments in the private tree.

### 证据

- `source`: [The board DTS identifies OnePlus 13 PJZ110 on SM8750.](https://github.com/Biaogo/UniXNU-dodge/blob/e9f298d0c6b66a7aa22eca1a3c2852227dfff309/dts/dodge.dts)

## 内存与 DMA {#memory}

`implemented`

组件: `NativeRamBlock`.

### 硬件与依赖

- Board memory window from the device tree.

### 配置

- RAM disk and reserved ranges follow board.toml.

### 操作步骤

- Build the payload with the selected RAM Data input. Do not commit that input.

### 开发经验

- The desktop path uses the packed RAM disk already selected by the board.

### 完成条件

- The kernel accepts the documented memory window.

### 当前范围

- A larger allocation is not claimed.

### 下一步

- Do not publish RAM Data images.

### 证据

- `source`: [Memory and payload settings stay in the board file.](https://github.com/Biaogo/UniXNU-dodge/blob/e9f298d0c6b66a7aa22eca1a3c2852227dfff309/board.toml)

## 存储与根卷 {#storage}

`implemented`

组件: `NativeUfs`, `NativeVirtioBlock`, `PaganiVerifiedRoot`, `NativeAES`.

### 硬件与依赖

- UFS root and a packed APFS RAM disk. Partition images are local inputs.

### 配置

- native-ufs-root=1 and offline-apfs-load=1.

### 操作步骤

- Prepare RAM Data locally, then build payload and bootimg.

### 开发经验

- The device reaches userspace from the packed root. Erase can reboot. Swipe-to-power-off can power off.

### 完成条件

- Root mount and shutdown do not hit the dead-parent vnode underflow.

### 当前范围

- Write qualification of the installed userdata partition is not claimed.

### 下一步

- Keep backup and shrink tools in the private tree.

### 证据

- `source`: [The device patch series includes the dead-parent vnode fix.](https://github.com/Biaogo/UniXNU-dodge/blob/e9f298d0c6b66a7aa22eca1a3c2852227dfff309/patches/xnu/series)

## 显示 {#display}

`implemented`

组件: `NativeMobileDisplay`, `PaganiPanel`.

### 硬件与依赖

- OnePlus 13 panel timing and the legacy framebuffer.

### 配置

- Panel and legacy display arguments are in board.toml. Normal use turns the HUD off.

### 操作步骤

- Boot with the published arguments. Skip Setup. Disable the on-screen HUD.

### 开发经验

- With the HUD off, the low frame-rate symptom is resolved for normal use on this device.

### 完成条件

- The panel shows Setup and the desktop without the diagnostic overlay.

### 当前范围

- This record does not publish frame traces or probe output.

### 下一步

- Keep display probes in the private tree.

### 证据

- `source`: [Panel and peripheral wiring is board-owned.](https://github.com/Biaogo/UniXNU-dodge/blob/e9f298d0c6b66a7aa22eca1a3c2852227dfff309/package/PaganiPeripherals.h)

## 输入 {#input}

`implemented`

组件: `PaganiInput`, `QcomGeniSpi`.

### 硬件与依赖

- Buttons and the board touch controller.

### 配置

- pagani-buttons=1 and pagani-touch=1.

### 操作步骤

- Boot and confirm buttons and touch after Setup is skipped.

### 开发经验

- Touch and buttons are usable on the device-observed desktop path.

### 完成条件

- Press, release, and basic navigation work.

### 当前范围

- Gesture coverage and long sessions are not claimed.

### 下一步

- Do not publish touch-debug captures.

### 证据

- `source`: [Input rails and the touch bus are described with the board peripherals.](https://github.com/Biaogo/UniXNU-dodge/blob/e9f298d0c6b66a7aa22eca1a3c2852227dfff309/package/PaganiPeripherals.h)

## GPU {#gpu}

`implemented`

组件: `Adreno830`, `AdrenoNext`.

### 硬件与依赖

- SM8750 Adreno 830. The Metal addon is a local input and is not stored here.

### 配置

- GPU handoff and the addon switch are in board.toml. Color correction stays on the scanout path.

### 操作步骤

- Supply the addon locally, build payload, and boot.

### 开发经验

- GPU scanout is part of the device-observed path. Later GPU probes stay private.

### 完成条件

- Frames reach the panel through the GPU handoff without falling back to the CPU copy.

### 当前范围

- Addon binaries, pipeline caches, and shader packs are not published.

### 下一步

- Keep addon build history in the private repository.

### 证据

- `source`: [The A830 kernel components are selected by this device repository.](https://github.com/Biaogo/UniXNU-dodge/blob/e9f298d0c6b66a7aa22eca1a3c2852227dfff309/components.toml)

## 网络 {#network}

`not-applicable`

### 硬件与依赖

- No network controller is selected.

### 配置

- No network component is enabled.

### 操作步骤

- Do not claim Wi-Fi, cellular, or USB networking from this tree.

### 开发经验

- Network is outside this publication.

### 完成条件

- No network component is required for the published boot path.

### 当前范围

- Network is not implemented here.

### 下一步

- Add a network area only when a controller is selected.

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`not-applicable`

### 硬件与依赖

- No audio controller is selected.

### 配置

- No audio component is enabled.

### 操作步骤

- Do not claim speaker, headphone, or microphone support.

### 开发经验

- Audio is outside this publication.

### 完成条件

- No audio component is required for the published boot path.

### 当前范围

- Audio is not implemented here.

### 下一步

- Add an audio area only when a controller is selected.

### 证据

按下一步操作收集证据。

## 电源 {#power}

`implemented`

组件: `ShengPlatformPower`, `Sm8750Platform`.

### 硬件与依赖

- PSCI system off and reset.

### 配置

- Shutdown uses the platform halt path.

### 操作步骤

- Verify erase reboot and swipe-to-power-off on a temporary boot.

### 开发经验

- Erase can reboot. Swipe-to-power-off can power the device off.

### 完成条件

- The halt timer calls the platform restart path before panic.

### 当前范围

- Battery gauge and charging control are not claimed.

### 下一步

- Do not publish power-management probe logs.

### 证据

- `source`: [The device patch series includes the platform halt and reset timeout fix.](https://github.com/Biaogo/UniXNU-dodge/blob/e9f298d0c6b66a7aa22eca1a3c2852227dfff309/patches/xnu/series)

## 镜像组装 {#packaging}

`implemented`

组件: `NativePrelink`.

### 硬件与依赖

- Kernel, trust cache, RAM Data, and optional GPU addon. Only the source pins are published.

### 配置

- Output is out/dodge/ipados-17.7.11-21H461/dodge/.

### 操作步骤

- defconfig, fetch, kernel, payload, bootimg. Keep generated images out of git.

### 开发经验

- The public tree does not contain IPSW, kernelcache, trust cache, RAM Data, or addon binaries.

### 完成条件

- A temporary boot image can be assembled from local inputs.

### 当前范围

- Image bytes are not part of this repository.

### 下一步

- Ignore generated output.

### 证据

- `source`: [Source pins are recorded without build products.](https://github.com/Biaogo/UniXNU-dodge/blob/e9f298d0c6b66a7aa22eca1a3c2852227dfff309/feeds.toml)

## 诊断 {#diagnostics}

`implemented`

组件: `BootProgress`, `Stage7Probe`.

### 硬件与依赖

- Boot progress can draw an overlay. Normal use does not need it.

### 配置

- Turn the HUD off after Setup. Do not publish probe switches.

### 操作步骤

- Skip Setup, then disable the HUD.

### 开发经验

- The usable path is skip Setup and HUD off. Probe history stays in the private backup.

### 完成条件

- The desktop remains usable with the HUD disabled.

### 当前范围

- This repository does not publish HUD captures or probe logs.

### 下一步

- Remove probe code from the public tree only after the boot path no longer references it.

### 证据

- `source`: [The public instructions name the device and keep process history out of this record.](https://github.com/Biaogo/UniXNU-dodge/blob/e9f298d0c6b66a7aa22eca1a3c2852227dfff309/README.md)

</div>
