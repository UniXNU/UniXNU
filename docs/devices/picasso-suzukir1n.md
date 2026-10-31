# Redmi K30 5G targeting iPhone X iOS 16; Darwin 22 ABI and firmware pending \(SuzukiR1n\)

[SuzukiR1n/UniXNU-Picasso](https://github.com/SuzukiR1n/UniXNU-Picasso)

<div v-pre>

独立的 Redmi K30 5G / SM7250 早期移植：宿主机构建与设备运行结果分别记录。

Source record: [porting.toml](https://github.com/SuzukiR1n/UniXNU-Picasso/blob/c9c833a3fd9efaa11b6b98a0778b50a162540698/porting.toml), `c9c833a3fd9efaa11b6b98a0778b50a162540698`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `host-verified` |
| [Firmware and boot](#firmware) | `planned` |
| [CPU and interrupts](#cpu) | `implemented` |
| [Memory and DMA](#memory) | `planned` |
| [Storage and root](#storage) | `planned` |
| [Display](#display) | `planned` |
| [Input](#input) | `planned` |
| [GPU](#gpu) | `planned` |
| [Network](#network) | `planned` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `planned` |
| [Image assembly](#packaging) | `implemented` |
| [Diagnostics](#diagnostics) | `host-verified` |

## Configuration {#configuration}

`host-verified`

Components: `XnuPrelink`, `DarwinBoot`.

### Hardware and dependencies

- 官方 UniXNU 格式 2、ARM64 构建工具和本仓库独立 iPhone X iOS 16.7.16 profile，SM7250 资源单独保存在本仓库。

### Configuration

- 提供固定源码版本、13 项移植记录、Actions 校验/UEFI 应用/iPhone X iOS 16 Apple 输入审计。

### Procedure

- 按 README 的校验和构建步骤执行；真机阶段见 docs/bring-up.md。

### Development findings

- 提供固定源码版本、13 项移植记录、Actions 校验/UEFI 应用/iPhone X iOS 16 Apple 输入审计。
- 首轮 CI 验证与 EFI 应用成功；内核发现官方可选 boot-progress 补丁冲突，当前禁用该插桩并保留 OS 预链接补丁。
- 默认目标改为 iPhone X iOS 16.7.16 / 20H392；Apple manifest 与 IM4P 摘要已独立核对。Darwin 22 补丁/驱动/预链接未移植，Darwin 23 内核成功只作为历史构建证据。

### Completion criteria

- 运行 Actions 并记录各任务的结果和提交版本。

### Current limits

- 配置可解析不代表硬件已支持；iOS 16 / Darwin 22 ABI 尚未移植，内核与预链接入口明确拒绝使用 Darwin 23 配方。

### Next action

- 运行 Actions 并记录各任务的结果和提交版本。

### Evidence

- `source`: [提供固定源码版本、13 项移植记录、Actions 校验/UEFI 应用/iPhone X iOS 16 Apple 输入审计。](https://github.com/SuzukiR1n/UniXNU-Picasso/blob/c9c833a3fd9efaa11b6b98a0778b50a162540698/docs/source-audit.md)
- `host`: [配置/DTS/C++、EFI 应用、iPhone X Apple 内核摘要与 Darwin 22 arm64 审计成功；目标 ABI 与设备启动仍待完成。](https://github.com/SuzukiR1n/UniXNU-Picasso/actions/runs/40262916511)
  Command: <code>GitHub Actions: Picasso build and validation</code>. Revision: `e0941c2eaffdbe4868b939fc0c472881595676e9`.

## Firmware and boot {#firmware}

`planned`

### Hardware and dependencies

- Project-Silicium/Mu-Silicium 审计版本没有 Picasso 平台。候选原厂输入基线为 MIUI V12.5.9.0.RGICNXM / Android 11。

### Configuration

- 没有从其他设备或社区移植复制 FD、DSC、FDF、内存映射或启动镜像。

### Procedure

- 按 README 的校验和构建步骤执行；真机阶段见 docs/bring-up.md。

### Development findings

- 没有从其他设备或社区移植复制 FD、DSC、FDF、内存映射或启动镜像。

### Completion criteria

- 提取原厂输入，编写平台内存图并按官方指南集成 UniXNU、DarwinBoot、RamDisk、DiskIo、FAT。

### Current limits

- 缺少独立 SM7250/Picasso UEFI 平台及原厂 boot/dtbo/UEFI 二进制。

### Next action

- 提取原厂输入，编写平台内存图并按官方指南集成 UniXNU、DarwinBoot、RamDisk、DiskIo、FAT。

### Evidence

Collect evidence using the next action.

## CPU and interrupts {#cpu}

`implemented`

### Hardware and dependencies

- MiCode picasso-r-oss qcom/lito.dtsi：CPU affinities 0..0x700，19.2 MHz，GICD 0x17a00000，GICR 0x17a60000，stride 0x20000；虚拟 PPI 3。

### Configuration

- 直接基于官方 ArmCpu 增加定时器描述解析，GIC 使能和 IRQ 分派统一使用 PPI+16；DTS 仅启用 CPU0。

### Procedure

- 按 README 的校验和构建步骤执行；真机阶段见 docs/bring-up.md。

### Development findings

- 直接基于官方 ArmCpu 增加定时器描述解析，GIC 使能和 IRQ 分派统一使用 PPI+16；DTS 仅启用 CPU0。
- 默认目标改为 iPhone X iOS 16.7.16 / 20H392；Apple manifest 与 IM4P 摘要已独立核对。Darwin 22 补丁/驱动/预链接未移植，Darwin 23 内核成功只作为历史构建证据。

### Completion criteria

- 完整编译驱动后，在真机核对定时器中断计数与 GIC 状态，再逐个启用其他 CPU。

### Current limits

- 源文件中的定时器号还未通过目标设备的 CNTV/中断计数读回验证；SMP 未验证。

### Next action

- 完整编译驱动后，在真机核对定时器中断计数与 GIC 状态，再逐个启用其他 CPU。

### Evidence

- `source`: [直接基于官方 ArmCpu 增加定时器描述解析，GIC 使能和 IRQ 分派统一使用 PPI+16；DTS 仅启用 CPU0。](https://github.com/SuzukiR1n/UniXNU-Picasso/blob/c9c833a3fd9efaa11b6b98a0778b50a162540698/docs/source-audit.md)

## Memory and DMA {#memory}

`planned`

### Hardware and dependencies

- MiCode Lito 源码 memory.reg 为零；原厂 bootloader 会修正 RAM。用户只确认了 128 GB 存储。

### Configuration

- 没有生成猜测的 RAM、DarwinBoot 分配窗口或保留内存；缺少内存时 ADT 生成必须失败。

### Procedure

- 按 README 的校验和构建步骤执行；真机阶段见 docs/bring-up.md。

### Development findings

- 没有生成猜测的 RAM、DarwinBoot 分配窗口或保留内存；缺少内存时 ADT 生成必须失败。

### Completion criteria

- 采集 bootloader FDT、UEFI memory map 和目标固件保留区，求出不重叠的连续窗口。

### Current limits

- RAM 容量、bootloader 修正的 FDT、UEFI EfiConventionalMemory 与保留区均未实测。

### Next action

- 采集 bootloader FDT、UEFI memory map 和目标固件保留区，求出不重叠的连续窗口。

### Evidence

Collect evidence using the next action.

## Storage and root {#storage}

`planned`

### Hardware and dependencies

- 官方 lito.dtsi UFS HCI 0x01d84000/0x3000、ICE 0x01d90000/0x8000、SPI 265（INTID 297）。

### Configuration

- 仅保留禁用的 UFS 资源描述；没有选择 SM8550 存储实现，也没有填写 userdata LBA。

### Procedure

- 按 README 的校验和构建步骤执行；真机阶段见 docs/bring-up.md。

### Development findings

- 仅保留禁用的 UFS 资源描述；没有选择 SM8550 存储实现，也没有填写 userdata LBA。

### Completion criteria

- 读取目标 GPT 和 UFS 版本，先实现容量与只读已知块校验，再讨论根卷。

### Current limits

- 128 GB 标称容量不能确定 GPT、扇区大小或 UFS 控制器供电/时钟/SMMU 设置。

### Next action

- 读取目标 GPT 和 UFS 版本，先实现容量与只读已知块校验，再讨论根卷。

### Evidence

Collect evidence using the next action.

## Display {#display}

`planned`

### Hardware and dependencies

- 官方 Picasso DTS 选择多个 G7A 面板变体；实际面板 ID 和 GOP 布局需要原厂/设备证据。

### Configuration

- 没有选择 SM8550 面板或背光代码，也没有把静态 splash 区直接当成 framebuffer。

### Procedure

- 按 README 的校验和构建步骤执行；真机阶段见 docs/bring-up.md。

### Development findings

- 没有选择 SM8550 面板或背光代码，也没有把静态 splash 区直接当成 framebuffer。

### Completion criteria

- 先验证 UEFI GOP 已知色块及 framebuffer handoff，再适配亮度。

### Current limits

- 无目标设备 GOP、stride、像素格式、背光和供电结果。

### Next action

- 先验证 UEFI GOP 已知色块及 framebuffer handoff，再适配亮度。

### Evidence

Collect evidence using the next action.

## Input {#input}

`planned`

### Hardware and dependencies

- 官方 Picasso DTS：GENI SPI SE7 0x984000，Novatek SPI touch，reset GPIO4、IRQ GPIO5，多个 NT36672C 固件变体。

### Configuration

- 触控仅登记源事实；没有启用未经确认的控制器和固件。

### Procedure

- 按 README 的校验和构建步骤执行；真机阶段见 docs/bring-up.md。

### Development findings

- 触控仅登记源事实；没有启用未经确认的控制器和固件。

### Completion criteria

- 提取目标固件并读取供应商 ID，先验证单触点按下/抬起，再进行多点 HID。

### Current limits

- 实际面板/触控供应商 ID、触控固件哈希和 HID 桥未验证。

### Next action

- 提取目标固件并读取供应商 ID，先验证单触点按下/抬起，再进行多点 HID。

### Evidence

Collect evidence using the next action.

## GPU {#gpu}

`planned`

### Hardware and dependencies

- SM7250 使用 Adreno 620；官方组件中的 Adreno740 没有覆盖本芯片的证据。

### Configuration

- 明确禁用原生 Adreno 加速。

### Procedure

- 按 README 的校验和构建步骤执行；真机阶段见 docs/bring-up.md。

### Development findings

- 明确禁用原生 Adreno 加速。

### Completion criteria

- 在 CPU/显示/内存稳定后核对 A620 硬件与固件接口。

### Current limits

- GMU、SMMU、GPU 固件和 Metal 路径均未适配。

### Next action

- 在 CPU/显示/内存稳定后核对 A620 硬件与固件接口。

### Evidence

Collect evidence using the next action.

## Network {#network}

`planned`

### Hardware and dependencies

- 官方 Lito/板级 DTS 的 WLAN 路径需要匹配目标设备固件和共享内存。

### Configuration

- 未选择 ath12k PCI/MHI 组件。

### Procedure

- 按 README 的校验和构建步骤执行；真机阶段见 docs/bring-up.md。

### Development findings

- 未选择 ath12k PCI/MHI 组件。

### Completion criteria

- 确认 WLAN 型号、CNSS/固件协议和 DMA 所有权。

### Current limits

- 扫描、连接、DHCP 和流量均没有运行结果。

### Next action

- 确认 WLAN 型号、CNSS/固件协议和 DMA 所有权。

### Evidence

Collect evidence using the next action.

## Audio {#audio}

`planned`

### Hardware and dependencies

- 官方 Picasso 音频 DTS 与原厂 DSP 固件尚需独立移植。

### Configuration

- 未声明音频支持。

### Procedure

- 按 README 的校验和构建步骤执行；真机阶段见 docs/bring-up.md。

### Development findings

- 未声明音频支持。

### Completion criteria

- 取得目标 ADSP 固件版本与播放/录音路由。

### Current limits

- DSP、时钟、路由和 codec 运行结果缺失。

### Next action

- 取得目标 ADSP 固件版本与播放/录音路由。

### Evidence

Collect evidence using the next action.

## Power {#power}

`planned`

### Hardware and dependencies

- 官方 PMIC/调压器/电池节点可作输入，不能等同于 XNU 电源管理实现。

### Configuration

- 未声明充电、电量或休眠恢复支持。

### Procedure

- 按 README 的校验和构建步骤执行；真机阶段见 docs/bring-up.md。

### Development findings

- 未声明充电、电量或休眠恢复支持。

### Completion criteria

- 先核对安全的启动电压/时钟继承，再实现电池和温控读数。

### Current limits

- 无目标设备电源和温控测量。

### Next action

- 先核对安全的启动电压/时钟继承，再实现电池和温控读数。

### Evidence

Collect evidence using the next action.

## Image assembly {#packaging}

`implemented`

### Hardware and dependencies

- UniXNU 官方构建接口要求目标固件、boot header、完整 payload 与内存 handoff。

### Configuration

- 入口阻止 payload/firmware/userdata/bootimg/all，直到 hardware.toml 的输入资格项通过；允许 package 构建与 Apple IPSW 审计；kernel/prelink 需要先完成 Darwin 22 ABI 移植。

### Procedure

- 按 README 的校验和构建步骤执行；真机阶段见 docs/bring-up.md。

### Development findings

- 入口阻止 payload/firmware/userdata/bootimg/all，直到 hardware.toml 的输入资格项通过；允许 package 构建与 Apple IPSW 审计；kernel/prelink 需要先完成 Darwin 22 ABI 移植。
- 首轮 CI 验证与 EFI 应用成功；内核发现官方可选 boot-progress 补丁冲突，当前禁用该插桩并保留 OS 预链接补丁。
- 默认目标改为 iPhone X iOS 16.7.16 / 20H392；Apple manifest 与 IM4P 摘要已独立核对。Darwin 22 补丁/驱动/预链接未移植，Darwin 23 内核成功只作为历史构建证据。

### Completion criteria

- 补齐真实输入后建立包内容、地址、大小和哈希验证，再解除镜像门槛。

### Current limits

- 本仓库当前没有可启动的 boot.img；UniXNU.efi 是应用而非固件。

### Next action

- 补齐真实输入后建立包内容、地址、大小和哈希验证，再解除镜像门槛。

### Evidence

- `source`: [入口阻止 payload/firmware/userdata/bootimg/all，直到 hardware.toml 的输入资格项通过；允许 package 构建与 Apple IPSW 审计；kernel/prelink 需要先完成 Darwin 22 ABI 移植。](https://github.com/SuzukiR1n/UniXNU-Picasso/blob/c9c833a3fd9efaa11b6b98a0778b50a162540698/docs/source-audit.md)

## Diagnostics {#diagnostics}

`host-verified`

### Hardware and dependencies

- 官方 DTS、格式 2 resolver 与 FDT/ADT 编码器可做独立宿主机交叉检查。

### Configuration

- 校验 GIC 地址/stride、CPU0 选择、定时器字节序与中断号、未测量内存的拒绝行为；提供只读输入采集和 boot header 检查。

### Procedure

- 按 README 的校验和构建步骤执行；真机阶段见 docs/bring-up.md。

### Development findings

- 校验 GIC 地址/stride、CPU0 选择、定时器字节序与中断号、未测量内存的拒绝行为；提供只读输入采集和 boot header 检查。
- 默认目标改为 iPhone X iOS 16.7.16 / 20H392；Apple manifest 与 IM4P 摘要已独立核对。Darwin 22 补丁/驱动/预链接未移植，Darwin 23 内核成功只作为历史构建证据。

### Completion criteria

- 保存 Actions 产物和原厂镜像检查报告，再采集第一阶段 UEFI 日志。

### Current limits

- 没有连接手机；没有本仓库的真机启动证据。

### Next action

- 保存 Actions 产物和原厂镜像检查报告，再采集第一阶段 UEFI 日志。

### Evidence

- `source`: [校验 GIC 地址/stride、CPU0 选择、定时器字节序与中断号、未测量内存的拒绝行为；提供只读输入采集和 boot header 检查。](https://github.com/SuzukiR1n/UniXNU-Picasso/blob/c9c833a3fd9efaa11b6b98a0778b50a162540698/docs/source-audit.md)
- `host`: [配置/DTS/C++、EFI 应用、iPhone X Apple 内核摘要与 Darwin 22 arm64 审计成功；目标 ABI 与设备启动仍待完成。](https://github.com/SuzukiR1n/UniXNU-Picasso/actions/runs/40262916511)
  Command: <code>GitHub Actions: Picasso build and validation</code>. Revision: `e0941c2eaffdbe4868b939fc0c472881595676e9`.

</div>
