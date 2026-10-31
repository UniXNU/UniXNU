# Nothing Phone \(2\) \(pong\)

[Chengdong-Yu/UniXNU-pong](https://github.com/Chengdong-Yu/UniXNU-pong)

<div v-pre>

Nothing Phone \(2\), iPadOS18 Darwin24 local format2 migration and board adaptation

Source record: [porting.toml](https://github.com/Chengdong-Yu/UniXNU-pong/blob/64ddf288ab6f7fa38eab36a31a599dbaf051534a/porting.toml), `64ddf288ab6f7fa38eab36a31a599dbaf051534a`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `implemented` |
| [Firmware and boot](#firmware) | `implemented` |
| [CPU and interrupts](#cpu) | `implemented` |
| [Memory and DMA](#memory) | `implemented` |
| [Storage and root](#storage) | `implemented` |
| [Display](#display) | `implemented` |
| [Input](#input) | `implemented` |
| [GPU](#gpu) | `implemented` |
| [Network](#network) | `implemented` |
| [Audio](#audio) | `implemented` |
| [Power](#power) | `implemented` |
| [Image assembly](#packaging) | `implemented` |
| [Diagnostics](#diagnostics) | `implemented` |

## Configuration {#configuration}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- Pong live Android DT、NothingOSS SM8475源码与匹配22H374 restore

### Configuration

- board.toml、pong\_ipados18\_defconfig 与对应板级配置

### Procedure

- 选择 ARM64、SM8475、22H374 和 Pong 四层配置，数组完整列出。

### Development findings

- 格式2解析、DTS编译、Darwin24内核及启动镜像构建成功；公开源固定版本已补齐。

### Completion criteria

- 在设备上观察该接口的实际工作结果并保存对应日志

### Current limits

- SM8475公共层与Pong聚合源码分目录固定；平台组件进一步拆分待完成。

### Next action

- 读取本轮启动日志并继续完成板级接口

### Evidence

- `source`: [格式2解析、DTS、内核和启动镜像已构建；services73未安装或启动。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/64ddf288ab6f7fa38eab36a31a599dbaf051534a/migration/ipados18/services73-smmu-audio.md)

## Firmware and boot {#firmware}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- Pong live Android DT、NothingOSS SM8475源码与匹配22H374 restore

### Configuration

- board.toml、pong\_ipados18\_defconfig 与对应板级配置

### Procedure

- 复用 Pong UEFI，DarwinBoot24 接管真实可分配区间并使用 PSCI。

### Development findings

- 现有设备可进入桌面，物理内存与可分配内存分别记录。

### Completion criteria

- 在设备上观察该接口的实际工作结果并保存对应日志

### Current limits

- 固件输入与UEFI源码在独立仓库。

### Next action

- 读取本轮启动日志并继续完成板级接口

### Evidence

- `source`: [现有设备可进入桌面，物理内存与可分配内存分别记录。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/64ddf288ab6f7fa38eab36a31a599dbaf051534a/migration/format2/README.zh.md)

## CPU and interrupts {#cpu}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- Pong live Android DT、NothingOSS SM8475源码与匹配22H374 restore

### Configuration

- board.toml、pong\_ipados18\_defconfig 与对应板级配置

### Procedure

- 使用 0x000..0x700 affinity、GICv3 和 19.2 MHz timer。

### Development findings

- CPU 4/3/1 拓扑保持 SM8475；受管内存沿用已启动实现。

### Completion criteria

- 在设备上观察该接口的实际工作结果并保存对应日志

### Current limits

- 没有声明新的多核稳定性测试结果。

### Next action

- 读取本轮启动日志并继续完成板级接口

### Evidence

- `source`: [CPU 4/3/1 拓扑保持 SM8475；受管内存沿用已启动实现。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/64ddf288ab6f7fa38eab36a31a599dbaf051534a/migration/format2/README.zh.md)

## Memory and DMA {#memory}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- Pong live Android DT、NothingOSS SM8475源码与匹配22H374 restore

### Configuration

- board.toml、pong\_ipados18\_defconfig 与对应板级配置

### Procedure

- 从实际不连续 DRAM 和保留区接管已取得所有权的 RAM。

### Development findings

- 物理容量12GiB；此前受管容量9728MiB，不能将物理空洞分配给VM。

### Completion criteria

- 在设备上观察该接口的实际工作结果并保存对应日志

### Current limits

- 尚未接通全部物理内存。

### Next action

- 读取本轮启动日志并继续完成板级接口

### Evidence

- `source`: [物理容量12GiB；此前受管容量9728MiB，不能将物理空洞分配给VM。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/64ddf288ab6f7fa38eab36a31a599dbaf051534a/migration/format2/README.zh.md)

## Storage and root {#storage}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- Pong live Android DT、NothingOSS SM8475源码与匹配22H374 restore

### Configuration

- board.toml、pong\_ipados18\_defconfig 与对应板级配置

### Procedure

- 原生 UFS + 22H374 IOStorageFamily，独立 OS/SystemOS/Data 窗口。

### Development findings

- 8GiB可写UFS Data已有启动记录；本轮只准备本机OS更新，未写入手机。

### Completion criteria

- 在设备上观察该接口的实际工作结果并保存对应日志

### Current limits

- 分区与镜像输入本地保存。

### Next action

- 读取本轮启动日志并继续完成板级接口

### Evidence

- `source`: [本机OS中init及音频策略已更新，设备仍保留services72。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/64ddf288ab6f7fa38eab36a31a599dbaf051534a/migration/ipados18/services73-smmu-audio.md)

## Display {#display}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- Pong live Android DT、NothingOSS SM8475源码与匹配22H374 restore

### Configuration

- board.toml、pong\_ipados18\_defconfig 与对应板级配置

### Procedure

- Pong 1080x2412、stride4320；DCS背光和原有显示服务。

### Development findings

- 桌面与壁纸已有显示；120Hz是请求值，不代表测得帧率。

### Completion criteria

- 在设备上观察该接口的实际工作结果并保存对应日志

### Current limits

- 实际高刷新率和背光仍需设备反馈。

### Next action

- 读取本轮启动日志并继续完成板级接口

### Evidence

- `source`: [桌面与壁纸已有显示；120Hz是请求值，不代表测得帧率。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/64ddf288ab6f7fa38eab36a31a599dbaf051534a/migration/format2/README.zh.md)

## Input {#input}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- Pong live Android DT、NothingOSS SM8475源码与匹配22H374 restore

### Configuration

- board.toml、pong\_ipados18\_defconfig 与对应板级配置

### Procedure

- Goodix Berlin-D，PM8350实体按键转HID/原生音量控制。

### Development findings

- services72真实音量press/release到达SBVolumeControl，电源down到达Consumer HID；本轮核对22H374事件接口，未新增虚构设备。

### Completion criteria

- 在设备上观察该接口的实际工作结果并保存对应日志

### Current limits

- 音量实际生效及独立电源按下/释放后的锁屏动作尚未确认。

### Next action

- 读取本轮启动日志并继续完成板级接口

### Evidence

- `source`: [services72已观察真实输入事件，系统动作仍需设备结果。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/64ddf288ab6f7fa38eab36a31a599dbaf051534a/migration/ipados18/services73-smmu-audio.md)

## GPU {#gpu}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- Pong live Android DT、NothingOSS SM8475源码与匹配22H374 restore

### Configuration

- board.toml、pong\_ipados18\_defconfig 与对应板级配置

### Procedure

- SM8475 A730、实际固件、SMMU、Turnip与22H374 Metal ABI。

### Development findings

- 已有桌面硬件渲染记录，保留此前高RAM BO和copy分配修补。

### Completion criteria

- 在设备上观察该接口的实际工作结果并保存对应日志

### Current limits

- 复杂壁纸和长时间稳定性没有新增结论。

### Next action

- 读取本轮启动日志并继续完成板级接口

### Evidence

- `source`: [已有桌面硬件渲染记录，保留此前高RAM BO和copy分配修补。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/64ddf288ab6f7fa38eab36a31a599dbaf051534a/migration/format2/README.zh.md)

## Network {#network}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- Pong live Android DT、NothingOSS SM8475源码与匹配22H374 restore

### Configuration

- board.toml、pong\_ipados18\_defconfig 与对应板级配置

### Procedure

- Pong PCIe0/QCA6490，82项PHY序列、GPIO80/94/95/96/204、RPMh。

### Development findings

- services72 PCIe link/BAR及128MiB散页DMA建表成功，停在SMMU context readback；services73按SM8475实现修正先TCR2/TCR后TTBR，编译通过。

### Completion criteria

- 在设备上观察该接口的实际工作结果并保存对应日志

### Current limits

- 本轮未启动；SMMU启用、QMI固件、扫描与联网仍未确认。

### Next action

- 读取本轮启动日志并继续完成板级接口

### Evidence

- `source`: [services72日志定位SMMU写序；services73复用ArmSmmu4K公共编程原语，未实机启动。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/64ddf288ab6f7fa38eab36a31a599dbaf051534a/migration/ipados18/services73-smmu-audio.md)

## Audio {#audio}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- Pong live Android DT、NothingOSS SM8475源码与匹配22H374 restore

### Configuration

- board.toml、pong\_ipados18\_defconfig 与对应板级配置

### Procedure

- ADSP/GPR/APM、TFA9873双扬声器、MI2S LPAIF0 tertiary/SD0。

### Development findings

- services72 APM、功放和现代HAL初始化成功；audiomxd因独立AirPlay路由RPC超时退出。services73在launchd前选择原生集成音频provider，运行时已编译。

### Completion criteria

- 在设备上观察该接口的实际工作结果并保存对应日志

### Current limits

- 尚无StartIO、PCM完成或实际出声证据；不公开麦克风。

### Next action

- 读取本轮启动日志并继续完成板级接口

### Evidence

- `source`: [services72的audiomxd堆栈定位CoreMedia路由等待，services73策略与launchd服务门控保持一致。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/64ddf288ab6f7fa38eab36a31a599dbaf051534a/migration/ipados18/services73-smmu-audio.md)

## Power {#power}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- Pong live Android DT、NothingOSS SM8475源码与匹配22H374 restore

### Configuration

- board.toml、pong\_ipados18\_defconfig 与对应板级配置

### Procedure

- SM8475 ADSP/RPMh、PMIC battery管理和Pong电源策略。

### Development findings

- DSP readiness和电池协议已有日志；控制器值保持Pong板级来源。

### Completion criteria

- 在设备上观察该接口的实际工作结果并保存对应日志

### Current limits

- 系统挂起恢复尚未完成。

### Next action

- 读取本轮启动日志并继续完成板级接口

### Evidence

- `source`: [DSP readiness和电池协议已有日志；控制器值保持Pong板级来源。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/64ddf288ab6f7fa38eab36a31a599dbaf051534a/migration/format2/README.zh.md)

## Image assembly {#packaging}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- Pong live Android DT、NothingOSS SM8475源码与匹配22H374 restore

### Configuration

- board.toml、pong\_ipados18\_defconfig 与对应板级配置

### Procedure

- Darwin24/XNU11417与22H374原始组件，格式2硬件输入与固定ABI。

### Development findings

- services73使用匹配22H374的IOStorage/IOGPU导入；内核43834376字节，启动镜像102514688字节，构建完成。

### Completion criteria

- 在设备上观察该接口的实际工作结果并保存对应日志

### Current limits

- Apple镜像、固件和ABI二进制均需本机准备。

### Next action

- 读取本轮启动日志并继续完成板级接口

### Evidence

- `source`: [内核、运行时与启动镜像已构建，产物留在本机；未安装、未启动。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/64ddf288ab6f7fa38eab36a31a599dbaf051534a/migration/ipados18/services73-smmu-audio.md)

## Diagnostics {#diagnostics}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- Pong live Android DT、NothingOSS SM8475源码与匹配22H374 restore

### Configuration

- board.toml、pong\_ipados18\_defconfig 与对应板级配置

### Procedure

- 保留屏幕启动日志和ramoops，REC抓取完整console。

### Development findings

- services72的REC日志与audiomxd超时堆栈已分析，services73修补只构建、未启动。

### Completion criteria

- 在设备上观察该接口的实际工作结果并保存对应日志

### Current limits

- 本轮未启动，SMMU、联网、PCM声音和按键动作仍需设备结果确认。

### Next action

- 读取本轮启动日志并继续完成板级接口

### Evidence

- `source`: [services72的REC日志与audiomxd超时堆栈已分析，services73修补只构建、未启动。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/64ddf288ab6f7fa38eab36a31a599dbaf051534a/migration/format2/README.zh.md)

</div>
