# 一加 5（cheeseburger）

[DinnerABC/UniXNU-cheeseburger](https://github.com/DinnerABC/UniXNU-cheeseburger)

<div v-pre>

iPadOS 17.7.11 desktop and touch run on OnePlus 5; A540 Metal rendering is under development, with system GPU composition not yet working.

源记录: [porting.toml](https://github.com/DinnerABC/UniXNU-cheeseburger/blob/3a10e39c01edb0bae551686df08bdd9f223627a3/porting.toml), `3a10e39c01edb0bae551686df08bdd9f223627a3`.

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
| [网络](#network) | `planned` |
| [音频](#audio) | `planned` |
| [电源](#power) | `planned` |
| [镜像组装](#packaging) | `implemented` |
| [诊断](#diagnostics) | `implemented` |
| [cellular](#cellular) | `planned` |

## 配置 {#configuration}

`implemented`

组件: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`.

### 硬件与依赖

- 捕获FDT及R7/P20历史证据；官方固定提交16e592abee8a550dec8154ed1f38b5ebc4f16213。

### 配置

- 见board.toml及docs/P21\_OFFICIAL\_ADAPTATION.md；未通过的配置保留guard。

### 操作步骤

- 按官方对应porting子系统文档，先来源与接口核对，再编译/打包门禁，最后实机验证。

### 开发经验

- 官方 format2 四层配置解析成功，本地SoC override如实标记未发布；构建guard仍开启。

### 完成条件

- 所选实现及全部板级依赖具有可重复构建记录与明确硬件证据等级。

### 当前范围

- 本记录描述迁移目标；planned不否认历史阶段已有实现，也不把历史结果冒充新源码验证。

### 下一步

- 补齐板级archive与patch计划后再解除guard。

### 证据

- `source`: [当前适配与待办记录，非新镜像实机成功声明](https://github.com/DinnerABC/UniXNU-cheeseburger/blob/3a10e39c01edb0bae551686df08bdd9f223627a3/docs/P21_OFFICIAL_ADAPTATION.md)

## 固件与启动 {#firmware}

`implemented`

组件: `DarwinBoot`.

### 硬件与依赖

- 捕获FDT及R7/P20历史证据；官方固定提交16e592abee8a550dec8154ed1f38b5ebc4f16213。

### 配置

- 见board.toml及docs/P21\_OFFICIAL\_ADAPTATION.md；未通过的配置保留guard。

### 操作步骤

- 按官方对应porting子系统文档，先来源与接口核对，再编译/打包门禁，最后实机验证。

### 开发经验

- 现有edk2-msm8998曾完成handoff；其不使用Mu-Silicium模板，官方固件入口尚待适配。

### 完成条件

- 所选实现及全部板级依赖具有可重复构建记录与明确硬件证据等级。

### 当前范围

- 本记录描述迁移目标；planned不否认历史阶段已有实现，也不把历史结果冒充新源码验证。

### 下一步

- 核对真实DSC/FDF和payload handoff，建立官方firmware recipe。

### 证据

- `source`: [当前适配与待办记录，非新镜像实机成功声明](https://github.com/DinnerABC/UniXNU-cheeseburger/blob/3a10e39c01edb0bae551686df08bdd9f223627a3/docs/P21_OFFICIAL_ADAPTATION.md)

## CPU 与中断 {#cpu}

`implemented`

### 硬件与依赖

- 捕获FDT及R7/P20历史证据；官方固定提交16e592abee8a550dec8154ed1f38b5ebc4f16213。

### 配置

- 见board.toml及docs/P21\_OFFICIAL\_ADAPTATION.md；未通过的配置保留guard。

### 操作步骤

- 按官方对应porting子系统文档，先来源与接口核对，再编译/打包门禁，最后实机验证。

### 开发经验

- 八核全部上线：持久日志 CPU0-3/CPU4-7 行 online=8，mpidr 0,1,2,3,0x100..0x103，PSCI SMC，SGI/timer 计数持续增长。

### 完成条件

- 所选实现及全部板级依赖具有可重复构建记录与明确硬件证据等级。

### 当前范围

- 本记录描述迁移目标；planned不否认历史阶段已有实现，也不把历史结果冒充新源码验证。

### 下一步

- 电源/频率策略与热调优未做。

### 证据

- `source`: [当前适配与待办记录，非新镜像实机成功声明](https://github.com/DinnerABC/UniXNU-cheeseburger/blob/3a10e39c01edb0bae551686df08bdd9f223627a3/docs/P21_OFFICIAL_ADAPTATION.md)

## 内存与 DMA {#memory}

`implemented`

### 硬件与依赖

- 捕获FDT及R7/P20历史证据；官方固定提交16e592abee8a550dec8154ed1f38b5ebc4f16213。

### 配置

- 见board.toml及docs/P21\_OFFICIAL\_ADAPTATION.md；未通过的配置保留guard。

### 操作步骤

- 按官方对应porting子系统文档，先来源与接口核对，再编译/打包门禁，最后实机验证。

### 开发经验

- 2 GiB 管理内存来自 ADT darwinboot 范围（P23 高内存窗口），实机 CPU/内存行与用户态可用。

### 完成条件

- 所选实现及全部板级依赖具有可重复构建记录与明确硬件证据等级。

### 当前范围

- 本记录描述迁移目标；planned不否认历史阶段已有实现，也不把历史结果冒充新源码验证。

### 下一步

- 更大内存窗口与持久 swap 未验证。

### 证据

- `source`: [当前适配与待办记录，非新镜像实机成功声明](https://github.com/DinnerABC/UniXNU-cheeseburger/blob/3a10e39c01edb0bae551686df08bdd9f223627a3/docs/P21_OFFICIAL_ADAPTATION.md)

## 存储与根卷 {#storage}

`implemented`

组件: `VerifiedRoot`, `RamBlock`.

### 硬件与依赖

- 捕获FDT及R7/P20历史证据；官方固定提交16e592abee8a550dec8154ed1f38b5ebc4f16213。

### 配置

- 见board.toml及docs/P21\_OFFICIAL\_ADAPTATION.md；未通过的配置保留guard。

### 操作步骤

- 按官方对应porting子系统文档，先来源与接口核对，再编译/打包门禁，最后实机验证。

### 开发经验

- UFS 读路径可用：分区发布、根卷/SystemOS 挂载、launchd 与桌面均从根卷启动。
- 持久 Data 已建立：按官方 ShengUfs 策略在 userdata 尾部预留区下方开 NativeRamBlock overlay 窗口（LBA 13620983，262153 块），mode1 只读校验、mode2 初始化后跨重启以 state=2 恢复，present=103367 页、err=0，GPT 前后 CRC 不变。
- 写路径仅对日志窗口与 Data store 窗口开放（WRITE\(10\)+FUA、读回校验、缓存同步），不是通用 UFS 写实现。

### 完成条件

- 所选实现及全部板级依赖具有可重复构建记录与明确硬件证据等级。

### 当前范围

- 本记录描述迁移目标；planned不否认历史阶段已有实现，也不把历史结果冒充新源码验证。

### 下一步

- Data 写窗口的掉电/复位一致性未做故障注入验证；seed 大小或 GPU 插件改变会更换持久化身份，需要 sheng-data-reset。
- 继续验证持久 Data 的一致性。

### 证据

- `source`: [当前适配与待办记录，非新镜像实机成功声明](https://github.com/DinnerABC/UniXNU-cheeseburger/blob/3a10e39c01edb0bae551686df08bdd9f223627a3/docs/P21_OFFICIAL_ADAPTATION.md)

## 显示 {#display}

`implemented`

组件: `GopFramebuffer`.

### 硬件与依赖

- 捕获FDT及R7/P20历史证据；官方固定提交16e592abee8a550dec8154ed1f38b5ebc4f16213。

### 配置

- 见board.toml及docs/P21\_OFFICIAL\_ADAPTATION.md；未通过的配置保留guard。

### 操作步骤

- 按官方对应porting子系统文档，先来源与接口核对，再编译/打包门禁，最后实机验证。

### 开发经验

- GOP CPU 呈现可达桌面；门控 GPU 系统设备的候选经用户确认可解锁。显示传输不等于 GPU 合成。

### 完成条件

- 所选实现及全部板级依赖具有可重复构建记录与明确硬件证据等级。

### 当前范围

- 本记录描述迁移目标；planned不否认历史阶段已有实现，也不把历史结果冒充新源码验证。

### 下一步

- 保持已验证的 CPU 呈现回退，后续验证 Metal 合成及显示交接。

### 证据

- `source`: [当前适配与待办记录，非新镜像实机成功声明](https://github.com/DinnerABC/UniXNU-cheeseburger/blob/3a10e39c01edb0bae551686df08bdd9f223627a3/docs/P21_OFFICIAL_ADAPTATION.md)

## 输入 {#input}

`implemented`

### 硬件与依赖

- 捕获FDT及R7/P20历史证据；官方固定提交16e592abee8a550dec8154ed1f38b5ebc4f16213。

### 配置

- 见board.toml及docs/P21\_OFFICIAL\_ADAPTATION.md；未通过的配置保留guard。

### 操作步骤

- 按官方对应porting子系统文档，先来源与接口核对，再编译/打包门禁，最后实机验证。

### 开发经验

- 触摸可用：S3320 over QUP v2.2.1，F01/F12 发现，10 指 80 字节包，HID 合并设备发布；实机 543 条报告、用户确认可点按滑动。
- 面板倒装曾使 X/Y 同时翻转（transform=3）：日志 HID 报告正常（rep=498，nodrv=0），但上/下、左/右都相反，用户误判为“触摸不可用”。改为 transform=0 后用户确认真实方向正常；boot arg cheeseburger-touch-transform 保留单轴复查。

### 完成条件

- 所选实现及全部板级依赖具有可重复构建记录与明确硬件证据等级。

### 当前范围

- 本记录描述迁移目标；planned不否认历史阶段已有实现，也不把历史结果冒充新源码验证。

### 下一步

- 按键仅电源/音量 + Home 组合；多点/边缘手势与 GPIO125 中断模式未验证。

### 证据

- `source`: [当前适配与待办记录，非新镜像实机成功声明](https://github.com/DinnerABC/UniXNU-cheeseburger/blob/3a10e39c01edb0bae551686df08bdd9f223627a3/docs/P21_OFFICIAL_ADAPTATION.md)

## GPU {#gpu}

`implemented`

### 硬件与依赖

- MSM8998 Adreno 540；vendor PM4/PFP、GPMU 和 ZAP 固件；sagit A540 与 UniXNU/sheng 参考实现。

### 配置

- GPU 4 KiB SMMU、ring/IB/fence 与 NativeAdreno 用户客户端；Metal 前端针对 iPadOS 17.7.11 / 21H461。

### 操作步骤

- 复用本机 GPU 初始化；通过用户客户端分配和映射 BO、提交 A540 命令并等待 fence；本机编译和候选打包见 docs/P21\_BUILD\_GUIDE.md。

### 开发经验

- 历史实机记录包括用户态提交与回读、2D 清屏和拷贝，以及受控 AIR 图形四帧颜色回读；详见 HANDOFF.md。
- 系统 Metal 设备启用时 backboardd 曾反复 SIGABRT；门控关闭的 CPU 呈现候选由用户确认可解锁进入桌面。

### 完成条件

- 真实系统 Metal 设备稳定注册，IOSurface / present 和系统 GPU 合成可用，支持连续交互。

### 当前范围

- 四帧受控回读不证明完整 Metal、应用兼容、流畅度或系统 GPU 合成；SIGABRT 的具体根因仍未确认。
- 本条仅附源码和项目交接；设备记录尚未发布，故状态不标为 device-verified。

### 下一步

- 对照 sagit 与 21H461 补齐真实支持的 Metal 设备、资源及 drawable/present 能力，定位系统设备启用后的 abort，并保留 CPU 呈现回退。

### 证据

- `source`: [记录受控 AIR 四帧回读、门控桌面和系统 Metal abort 的实机结果与限制。](https://github.com/DinnerABC/UniXNU-cheeseburger/blob/3a10e39c01edb0bae551686df08bdd9f223627a3/HANDOFF.md)
- `source`: [A540 用户客户端、BO 和 GPU 提交实现。](https://github.com/DinnerABC/UniXNU-cheeseburger/blob/3a10e39c01edb0bae551686df08bdd9f223627a3/package/BoardRuntime/CheeseburgerGpuService.cpp)
- `source`: [受控 Metal 图形与资源复用结果；非系统 GPU 合成。](https://github.com/DinnerABC/UniXNU-cheeseburger/blob/3a10e39c01edb0bae551686df08bdd9f223627a3/docs/P21_METAL_CONTINUOUS_20261106.md)

## 网络 {#network}

`planned`

### 硬件与依赖

- 捕获FDT及R7/P20历史证据；官方固定提交16e592abee8a550dec8154ed1f38b5ebc4f16213。

### 配置

- 见board.toml及docs/P21\_OFFICIAL\_ADAPTATION.md；未通过的配置保留guard。

### 操作步骤

- 按官方对应porting子系统文档，先来源与接口核对，再编译/打包门禁，最后实机验证。

### 开发经验

- 当前没有WiFi/蓝牙完整硬件支持证据。

### 完成条件

- 所选实现及全部板级依赖具有可重复构建记录与明确硬件证据等级。

### 当前范围

- 本记录描述迁移目标；planned不否认历史阶段已有实现，也不把历史结果冒充新源码验证。

### 下一步

- 取得本板控制器/固件/传输事实后再选择组件。

### 证据

- `source`: [当前适配与待办记录，非新镜像实机成功声明](https://github.com/DinnerABC/UniXNU-cheeseburger/blob/3a10e39c01edb0bae551686df08bdd9f223627a3/docs/P21_OFFICIAL_ADAPTATION.md)

## 音频 {#audio}

`planned`

### 硬件与依赖

- 捕获FDT及R7/P20历史证据；官方固定提交16e592abee8a550dec8154ed1f38b5ebc4f16213。

### 配置

- 见board.toml及docs/P21\_OFFICIAL\_ADAPTATION.md；未通过的配置保留guard。

### 操作步骤

- 按官方对应porting子系统文档，先来源与接口核对，再编译/打包门禁，最后实机验证。

### 开发经验

- 原始音频模块装入不等于实际codec/路由支持。

### 完成条件

- 所选实现及全部板级依赖具有可重复构建记录与明确硬件证据等级。

### 当前范围

- 本记录描述迁移目标；planned不否认历史阶段已有实现，也不把历史结果冒充新源码验证。

### 下一步

- 收集本机codec/时钟/路由事实，不复制sheng音频地址。

### 证据

- `source`: [当前适配与待办记录，非新镜像实机成功声明](https://github.com/DinnerABC/UniXNU-cheeseburger/blob/3a10e39c01edb0bae551686df08bdd9f223627a3/docs/P21_OFFICIAL_ADAPTATION.md)

## 电源 {#power}

`planned`

组件: `AppleKeyStoreState`.

### 硬件与依赖

- 捕获FDT及R7/P20历史证据；官方固定提交16e592abee8a550dec8154ed1f38b5ebc4f16213。

### 配置

- 见board.toml及docs/P21\_OFFICIAL\_ADAPTATION.md；未通过的配置保留guard。

### 操作步骤

- 按官方对应porting子系统文档，先来源与接口核对，再编译/打包门禁，最后实机验证。

### 开发经验

- PMGR板卡识别与iPad产品身份已解耦并通过340项ABI编译检查；AKS仅临时状态服务。

### 完成条件

- 所选实现及全部板级依赖具有可重复构建记录与明确硬件证据等级。

### 当前范围

- 本记录描述迁移目标；planned不否认历史阶段已有实现，也不把历史结果冒充新源码验证。

### 下一步

- 核对新archive最终链接与UUID就绪；不宣称SEP密钥或深睡唤醒支持。

### 证据

- `source`: [当前适配与待办记录，非新镜像实机成功声明](https://github.com/DinnerABC/UniXNU-cheeseburger/blob/3a10e39c01edb0bae551686df08bdd9f223627a3/docs/P21_OFFICIAL_ADAPTATION.md)

## 镜像组装 {#packaging}

`implemented`

### 硬件与依赖

- 捕获FDT及R7/P20历史证据；官方固定提交16e592abee8a550dec8154ed1f38b5ebc4f16213。

### 配置

- 见board.toml及docs/P21\_OFFICIAL\_ADAPTATION.md；未通过的配置保留guard。

### 操作步骤

- 按官方对应porting子系统文档，先来源与接口核对，再编译/打包门禁，最后实机验证。

### 开发经验

- 每轮 payload/UEFI/pins/门禁可重复通过，镜像 SHA 与 kernel/payload/ADT 三处 pin 命中。

### 完成条件

- 所选实现及全部板级依赖具有可重复构建记录与明确硬件证据等级。

### 当前范围

- 本记录描述迁移目标；planned不否认历史阶段已有实现，也不把历史结果冒充新源码验证。

### 下一步

- 构建 guard 仍开启，一键官方 recipe 未完成。

### 证据

- `source`: [当前适配与待办记录，非新镜像实机成功声明](https://github.com/DinnerABC/UniXNU-cheeseburger/blob/3a10e39c01edb0bae551686df08bdd9f223627a3/docs/P21_OFFICIAL_ADAPTATION.md)

## 诊断 {#diagnostics}

`implemented`

### 硬件与依赖

- 捕获FDT及R7/P20历史证据；官方固定提交16e592abee8a550dec8154ed1f38b5ebc4f16213。

### 配置

- 见board.toml及docs/P21\_OFFICIAL\_ADAPTATION.md；未通过的配置保留guard。

### 操作步骤

- 按官方对应porting子系统文档，先来源与接口核对，再编译/打包门禁，最后实机验证。

### 开发经验

- 持久日志窗口 + Recovery 回收可用（2s 轮询、多轮日志已归档）；UEFI 侧 NPA/GPU 时钟探针写入窗口尾部。
- 预置并回读 misc BCB 后，定时复位候选曾自动返回 Recovery；BCB 会被消费，不代表所有故障路径均可恢复。

### 完成条件

- 所选实现及全部板级依赖具有可重复构建记录与明确硬件证据等级。

### 当前范围

- 本记录描述迁移目标；planned不否认历史阶段已有实现，也不把历史结果冒充新源码验证。

### 下一步

- 无实时通道：USB CDC-ACM 仅完成阶段 0 只读探针，按用户要求暂停。

### 证据

- `source`: [当前适配与待办记录，非新镜像实机成功声明](https://github.com/DinnerABC/UniXNU-cheeseburger/blob/3a10e39c01edb0bae551686df08bdd9f223627a3/docs/P21_OFFICIAL_ADAPTATION.md)

## cellular {#cellular}

`planned`

### 硬件与依赖

- MSM8998 modem、SIM、固件及运营商网络接口尚需核实。

### 配置

- 未选择基带组件。

### 操作步骤

- 按官方基带移植指南核对固件、接口与设备资源。

### 开发经验

- 尚无本设备蜂窝网络可用记录。

### 完成条件

- SIM、网络注册与数据连接在设备上完成验证。

### 当前范围

- 尚未实现或验证。

### 下一步

- 盘点 modem、固件与系统接口。

### 证据

按下一步操作收集证据。

</div>
