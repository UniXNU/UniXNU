# Redmi K30 5G targeting iPhone X iOS 16; Darwin 22 ABI and firmware pending \(SuzukiR1n\)

[SuzukiR1n/UniXNU-Picasso](https://github.com/SuzukiR1n/UniXNU-Picasso)

<div v-pre>

独立的 Redmi K30 5G / SM7250 早期移植：宿主机构建与设备运行结果分别记录。

源记录: [porting.toml](https://github.com/SuzukiR1n/UniXNU-Picasso/blob/c9c833a3fd9efaa11b6b98a0778b50a162540698/porting.toml), `c9c833a3fd9efaa11b6b98a0778b50a162540698`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `host-verified` |
| [固件与启动](#firmware) | `planned` |
| [CPU 与中断](#cpu) | `implemented` |
| [内存与 DMA](#memory) | `planned` |
| [存储与根卷](#storage) | `planned` |
| [显示](#display) | `planned` |
| [输入](#input) | `planned` |
| [GPU](#gpu) | `planned` |
| [网络](#network) | `planned` |
| [音频](#audio) | `planned` |
| [电源](#power) | `planned` |
| [镜像组装](#packaging) | `implemented` |
| [诊断](#diagnostics) | `host-verified` |

## 配置 {#configuration}

`host-verified`

组件: `XnuPrelink`, `DarwinBoot`.

### 硬件与依赖

- 官方 UniXNU 格式 2、ARM64 构建工具和本仓库独立 iPhone X iOS 16.7.16 profile，SM7250 资源单独保存在本仓库。

### 配置

- 提供固定源码版本、13 项移植记录、Actions 校验/UEFI 应用/iPhone X iOS 16 Apple 输入审计。

### 操作步骤

- 按 README 的校验和构建步骤执行；真机阶段见 docs/bring-up.md。

### 开发经验

- 提供固定源码版本、13 项移植记录、Actions 校验/UEFI 应用/iPhone X iOS 16 Apple 输入审计。
- 首轮 CI 验证与 EFI 应用成功；内核发现官方可选 boot-progress 补丁冲突，当前禁用该插桩并保留 OS 预链接补丁。
- 默认目标改为 iPhone X iOS 16.7.16 / 20H392；Apple manifest 与 IM4P 摘要已独立核对。Darwin 22 补丁/驱动/预链接未移植，Darwin 23 内核成功只作为历史构建证据。

### 完成条件

- 运行 Actions 并记录各任务的结果和提交版本。

### 当前范围

- 配置可解析不代表硬件已支持；iOS 16 / Darwin 22 ABI 尚未移植，内核与预链接入口明确拒绝使用 Darwin 23 配方。

### 下一步

- 运行 Actions 并记录各任务的结果和提交版本。

### 证据

- `source`: [提供固定源码版本、13 项移植记录、Actions 校验/UEFI 应用/iPhone X iOS 16 Apple 输入审计。](https://github.com/SuzukiR1n/UniXNU-Picasso/blob/c9c833a3fd9efaa11b6b98a0778b50a162540698/docs/source-audit.md)
- `host`: [配置/DTS/C++、EFI 应用、iPhone X Apple 内核摘要与 Darwin 22 arm64 审计成功；目标 ABI 与设备启动仍待完成。](https://github.com/SuzukiR1n/UniXNU-Picasso/actions/runs/40262916511)
  Command: <code>GitHub Actions: Picasso build and validation</code>. Revision: `e0941c2eaffdbe4868b939fc0c472881595676e9`.

## 固件与启动 {#firmware}

`planned`

### 硬件与依赖

- Project-Silicium/Mu-Silicium 审计版本没有 Picasso 平台。候选原厂输入基线为 MIUI V12.5.9.0.RGICNXM / Android 11。

### 配置

- 没有从其他设备或社区移植复制 FD、DSC、FDF、内存映射或启动镜像。

### 操作步骤

- 按 README 的校验和构建步骤执行；真机阶段见 docs/bring-up.md。

### 开发经验

- 没有从其他设备或社区移植复制 FD、DSC、FDF、内存映射或启动镜像。

### 完成条件

- 提取原厂输入，编写平台内存图并按官方指南集成 UniXNU、DarwinBoot、RamDisk、DiskIo、FAT。

### 当前范围

- 缺少独立 SM7250/Picasso UEFI 平台及原厂 boot/dtbo/UEFI 二进制。

### 下一步

- 提取原厂输入，编写平台内存图并按官方指南集成 UniXNU、DarwinBoot、RamDisk、DiskIo、FAT。

### 证据

按下一步操作收集证据。

## CPU 与中断 {#cpu}

`implemented`

### 硬件与依赖

- MiCode picasso-r-oss qcom/lito.dtsi：CPU affinities 0..0x700，19.2 MHz，GICD 0x17a00000，GICR 0x17a60000，stride 0x20000；虚拟 PPI 3。

### 配置

- 直接基于官方 ArmCpu 增加定时器描述解析，GIC 使能和 IRQ 分派统一使用 PPI+16；DTS 仅启用 CPU0。

### 操作步骤

- 按 README 的校验和构建步骤执行；真机阶段见 docs/bring-up.md。

### 开发经验

- 直接基于官方 ArmCpu 增加定时器描述解析，GIC 使能和 IRQ 分派统一使用 PPI+16；DTS 仅启用 CPU0。
- 默认目标改为 iPhone X iOS 16.7.16 / 20H392；Apple manifest 与 IM4P 摘要已独立核对。Darwin 22 补丁/驱动/预链接未移植，Darwin 23 内核成功只作为历史构建证据。

### 完成条件

- 完整编译驱动后，在真机核对定时器中断计数与 GIC 状态，再逐个启用其他 CPU。

### 当前范围

- 源文件中的定时器号还未通过目标设备的 CNTV/中断计数读回验证；SMP 未验证。

### 下一步

- 完整编译驱动后，在真机核对定时器中断计数与 GIC 状态，再逐个启用其他 CPU。

### 证据

- `source`: [直接基于官方 ArmCpu 增加定时器描述解析，GIC 使能和 IRQ 分派统一使用 PPI+16；DTS 仅启用 CPU0。](https://github.com/SuzukiR1n/UniXNU-Picasso/blob/c9c833a3fd9efaa11b6b98a0778b50a162540698/docs/source-audit.md)

## 内存与 DMA {#memory}

`planned`

### 硬件与依赖

- MiCode Lito 源码 memory.reg 为零；原厂 bootloader 会修正 RAM。用户只确认了 128 GB 存储。

### 配置

- 没有生成猜测的 RAM、DarwinBoot 分配窗口或保留内存；缺少内存时 ADT 生成必须失败。

### 操作步骤

- 按 README 的校验和构建步骤执行；真机阶段见 docs/bring-up.md。

### 开发经验

- 没有生成猜测的 RAM、DarwinBoot 分配窗口或保留内存；缺少内存时 ADT 生成必须失败。

### 完成条件

- 采集 bootloader FDT、UEFI memory map 和目标固件保留区，求出不重叠的连续窗口。

### 当前范围

- RAM 容量、bootloader 修正的 FDT、UEFI EfiConventionalMemory 与保留区均未实测。

### 下一步

- 采集 bootloader FDT、UEFI memory map 和目标固件保留区，求出不重叠的连续窗口。

### 证据

按下一步操作收集证据。

## 存储与根卷 {#storage}

`planned`

### 硬件与依赖

- 官方 lito.dtsi UFS HCI 0x01d84000/0x3000、ICE 0x01d90000/0x8000、SPI 265（INTID 297）。

### 配置

- 仅保留禁用的 UFS 资源描述；没有选择 SM8550 存储实现，也没有填写 userdata LBA。

### 操作步骤

- 按 README 的校验和构建步骤执行；真机阶段见 docs/bring-up.md。

### 开发经验

- 仅保留禁用的 UFS 资源描述；没有选择 SM8550 存储实现，也没有填写 userdata LBA。

### 完成条件

- 读取目标 GPT 和 UFS 版本，先实现容量与只读已知块校验，再讨论根卷。

### 当前范围

- 128 GB 标称容量不能确定 GPT、扇区大小或 UFS 控制器供电/时钟/SMMU 设置。

### 下一步

- 读取目标 GPT 和 UFS 版本，先实现容量与只读已知块校验，再讨论根卷。

### 证据

按下一步操作收集证据。

## 显示 {#display}

`planned`

### 硬件与依赖

- 官方 Picasso DTS 选择多个 G7A 面板变体；实际面板 ID 和 GOP 布局需要原厂/设备证据。

### 配置

- 没有选择 SM8550 面板或背光代码，也没有把静态 splash 区直接当成 framebuffer。

### 操作步骤

- 按 README 的校验和构建步骤执行；真机阶段见 docs/bring-up.md。

### 开发经验

- 没有选择 SM8550 面板或背光代码，也没有把静态 splash 区直接当成 framebuffer。

### 完成条件

- 先验证 UEFI GOP 已知色块及 framebuffer handoff，再适配亮度。

### 当前范围

- 无目标设备 GOP、stride、像素格式、背光和供电结果。

### 下一步

- 先验证 UEFI GOP 已知色块及 framebuffer handoff，再适配亮度。

### 证据

按下一步操作收集证据。

## 输入 {#input}

`planned`

### 硬件与依赖

- 官方 Picasso DTS：GENI SPI SE7 0x984000，Novatek SPI touch，reset GPIO4、IRQ GPIO5，多个 NT36672C 固件变体。

### 配置

- 触控仅登记源事实；没有启用未经确认的控制器和固件。

### 操作步骤

- 按 README 的校验和构建步骤执行；真机阶段见 docs/bring-up.md。

### 开发经验

- 触控仅登记源事实；没有启用未经确认的控制器和固件。

### 完成条件

- 提取目标固件并读取供应商 ID，先验证单触点按下/抬起，再进行多点 HID。

### 当前范围

- 实际面板/触控供应商 ID、触控固件哈希和 HID 桥未验证。

### 下一步

- 提取目标固件并读取供应商 ID，先验证单触点按下/抬起，再进行多点 HID。

### 证据

按下一步操作收集证据。

## GPU {#gpu}

`planned`

### 硬件与依赖

- SM7250 使用 Adreno 620；官方组件中的 Adreno740 没有覆盖本芯片的证据。

### 配置

- 明确禁用原生 Adreno 加速。

### 操作步骤

- 按 README 的校验和构建步骤执行；真机阶段见 docs/bring-up.md。

### 开发经验

- 明确禁用原生 Adreno 加速。

### 完成条件

- 在 CPU/显示/内存稳定后核对 A620 硬件与固件接口。

### 当前范围

- GMU、SMMU、GPU 固件和 Metal 路径均未适配。

### 下一步

- 在 CPU/显示/内存稳定后核对 A620 硬件与固件接口。

### 证据

按下一步操作收集证据。

## 网络 {#network}

`planned`

### 硬件与依赖

- 官方 Lito/板级 DTS 的 WLAN 路径需要匹配目标设备固件和共享内存。

### 配置

- 未选择 ath12k PCI/MHI 组件。

### 操作步骤

- 按 README 的校验和构建步骤执行；真机阶段见 docs/bring-up.md。

### 开发经验

- 未选择 ath12k PCI/MHI 组件。

### 完成条件

- 确认 WLAN 型号、CNSS/固件协议和 DMA 所有权。

### 当前范围

- 扫描、连接、DHCP 和流量均没有运行结果。

### 下一步

- 确认 WLAN 型号、CNSS/固件协议和 DMA 所有权。

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`planned`

### 硬件与依赖

- 官方 Picasso 音频 DTS 与原厂 DSP 固件尚需独立移植。

### 配置

- 未声明音频支持。

### 操作步骤

- 按 README 的校验和构建步骤执行；真机阶段见 docs/bring-up.md。

### 开发经验

- 未声明音频支持。

### 完成条件

- 取得目标 ADSP 固件版本与播放/录音路由。

### 当前范围

- DSP、时钟、路由和 codec 运行结果缺失。

### 下一步

- 取得目标 ADSP 固件版本与播放/录音路由。

### 证据

按下一步操作收集证据。

## 电源 {#power}

`planned`

### 硬件与依赖

- 官方 PMIC/调压器/电池节点可作输入，不能等同于 XNU 电源管理实现。

### 配置

- 未声明充电、电量或休眠恢复支持。

### 操作步骤

- 按 README 的校验和构建步骤执行；真机阶段见 docs/bring-up.md。

### 开发经验

- 未声明充电、电量或休眠恢复支持。

### 完成条件

- 先核对安全的启动电压/时钟继承，再实现电池和温控读数。

### 当前范围

- 无目标设备电源和温控测量。

### 下一步

- 先核对安全的启动电压/时钟继承，再实现电池和温控读数。

### 证据

按下一步操作收集证据。

## 镜像组装 {#packaging}

`implemented`

### 硬件与依赖

- UniXNU 官方构建接口要求目标固件、boot header、完整 payload 与内存 handoff。

### 配置

- 入口阻止 payload/firmware/userdata/bootimg/all，直到 hardware.toml 的输入资格项通过；允许 package 构建与 Apple IPSW 审计；kernel/prelink 需要先完成 Darwin 22 ABI 移植。

### 操作步骤

- 按 README 的校验和构建步骤执行；真机阶段见 docs/bring-up.md。

### 开发经验

- 入口阻止 payload/firmware/userdata/bootimg/all，直到 hardware.toml 的输入资格项通过；允许 package 构建与 Apple IPSW 审计；kernel/prelink 需要先完成 Darwin 22 ABI 移植。
- 首轮 CI 验证与 EFI 应用成功；内核发现官方可选 boot-progress 补丁冲突，当前禁用该插桩并保留 OS 预链接补丁。
- 默认目标改为 iPhone X iOS 16.7.16 / 20H392；Apple manifest 与 IM4P 摘要已独立核对。Darwin 22 补丁/驱动/预链接未移植，Darwin 23 内核成功只作为历史构建证据。

### 完成条件

- 补齐真实输入后建立包内容、地址、大小和哈希验证，再解除镜像门槛。

### 当前范围

- 本仓库当前没有可启动的 boot.img；UniXNU.efi 是应用而非固件。

### 下一步

- 补齐真实输入后建立包内容、地址、大小和哈希验证，再解除镜像门槛。

### 证据

- `source`: [入口阻止 payload/firmware/userdata/bootimg/all，直到 hardware.toml 的输入资格项通过；允许 package 构建与 Apple IPSW 审计；kernel/prelink 需要先完成 Darwin 22 ABI 移植。](https://github.com/SuzukiR1n/UniXNU-Picasso/blob/c9c833a3fd9efaa11b6b98a0778b50a162540698/docs/source-audit.md)

## 诊断 {#diagnostics}

`host-verified`

### 硬件与依赖

- 官方 DTS、格式 2 resolver 与 FDT/ADT 编码器可做独立宿主机交叉检查。

### 配置

- 校验 GIC 地址/stride、CPU0 选择、定时器字节序与中断号、未测量内存的拒绝行为；提供只读输入采集和 boot header 检查。

### 操作步骤

- 按 README 的校验和构建步骤执行；真机阶段见 docs/bring-up.md。

### 开发经验

- 校验 GIC 地址/stride、CPU0 选择、定时器字节序与中断号、未测量内存的拒绝行为；提供只读输入采集和 boot header 检查。
- 默认目标改为 iPhone X iOS 16.7.16 / 20H392；Apple manifest 与 IM4P 摘要已独立核对。Darwin 22 补丁/驱动/预链接未移植，Darwin 23 内核成功只作为历史构建证据。

### 完成条件

- 保存 Actions 产物和原厂镜像检查报告，再采集第一阶段 UEFI 日志。

### 当前范围

- 没有连接手机；没有本仓库的真机启动证据。

### 下一步

- 保存 Actions 产物和原厂镜像检查报告，再采集第一阶段 UEFI 日志。

### 证据

- `source`: [校验 GIC 地址/stride、CPU0 选择、定时器字节序与中断号、未测量内存的拒绝行为；提供只读输入采集和 boot header 检查。](https://github.com/SuzukiR1n/UniXNU-Picasso/blob/c9c833a3fd9efaa11b6b98a0778b50a162540698/docs/source-audit.md)
- `host`: [配置/DTS/C++、EFI 应用、iPhone X Apple 内核摘要与 Darwin 22 arm64 审计成功；目标 ABI 与设备启动仍待完成。](https://github.com/SuzukiR1n/UniXNU-Picasso/actions/runs/40262916511)
  Command: <code>GitHub Actions: Picasso build and validation</code>. Revision: `e0941c2eaffdbe4868b939fc0c472881595676e9`.

</div>
