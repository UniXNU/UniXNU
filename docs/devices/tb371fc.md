# Lenovo Xiaoxin Pad Pro 12.7 \(2023\) / TB371FC

[xiuyityer/UniXNU-tb371fc](https://github.com/xiuyityer/UniXNU-tb371fc)

<div v-pre>

V135 实机基线；应用、设置、触摸和 GPU 正常；壁纸仍黑并暂停调试。公开构建入口需要本地私有输入，完整 XNU 源码重编译及电池/音量键仍未完成。

Source record: [porting.toml](https://github.com/xiuyityer/UniXNU-tb371fc/blob/e6eeb91a3971a43bad2de09154c0b8dba51a2551/porting.toml), `e6eeb91a3971a43bad2de09154c0b8dba51a2551`.

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
| [Network](#network) | `planned` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `implemented` |
| [Image assembly](#packaging) | `implemented` |
| [Diagnostics](#diagnostics) | `implemented` |

## Configuration {#configuration}

`implemented`

### Hardware and dependencies

- TB371FC / bootloader product spinel；Snapdragon 870、SM8250 系列、Adreno 650；测试配置 8 GB + 128 GB。

### Configuration

- board.name=tb371fc，os\_profile=ipados-17.7.11-21H461；example=true，components.include=\[\]。

### Procedure

- 先阅读 BUILDING 与来源锁，再运行源码及官网记录检查。

### Development findings

- V129 已整理为公开源码快照；设备身份与上游来源已有独立记录。

### Completion criteria

- 官网设备标识与适配记录一致，来源固定且公开内容不包含私有输入。

### Current limits

- 本 board 仅提供目录身份，不是通用构建器的完整入口；不复制旧工作区过时的 host-only 说明。

### Next action

- 整理实际 XNU、UEFI 和组件构建配方后再接通完整 board 配置。

### Evidence

- `source`: [公开实现或维护者验证摘要；实机范围与重建限制见正文。](https://github.com/xiuyityer/UniXNU-tb371fc/blob/e6eeb91a3971a43bad2de09154c0b8dba51a2551/board.toml)
- `source`: [公开实现或维护者验证摘要；实机范围与重建限制见正文。](https://github.com/xiuyityer/UniXNU-tb371fc/blob/e6eeb91a3971a43bad2de09154c0b8dba51a2551/upstream/source-manifest.json)

## Firmware and boot {#firmware}

`implemented`

### Hardware and dependencies

- 目标 UEFI、原始 boot 恢复备份及手动菜单；本仓库不分发固件。

### Configuration

- 保留内嵌 FAT 与 fastboot 返回实现；不提供自动选择 XNU 的配置。

### Procedure

- 由维护者用独立审计过的本地镜像手动启动并保留原始恢复入口。

### Development findings

- V127 修复大 FFS 早期解析后恢复菜单与桌面；V129 实机桌面已有用户回报。

### Completion criteria

- 设备能从手动菜单进入系统，并有可用的原始 bootloader 恢复路径。

### Current limits

- 完整 UEFI 配方及设备恢复绑定尚未公开；历史操作记录不能重放。

### Next action

- 整理当前实际固件配方与重新生成的恢复说明。

### Evidence

- `source`: [公开实现或维护者验证摘要；实机范围与重建限制见正文。](https://github.com/xiuyityer/UniXNU-tb371fc/blob/e6eeb91a3971a43bad2de09154c0b8dba51a2551/package/Tb371fcEmbeddedFat/Tb371fcEmbeddedFat.c)
- `source`: [公开实现或维护者验证摘要；实机范围与重建限制见正文。](https://github.com/xiuyityer/UniXNU-tb371fc/blob/e6eeb91a3971a43bad2de09154c0b8dba51a2551/docs/VALIDATION.md)

## CPU and interrupts {#cpu}

`implemented`

### Hardware and dependencies

- 目标八核平台和原移植工作区的 SMP/中断集成。

### Configuration

- 当前实测基线启用八核；公开快照尚未包含全部 XNU CPU 补丁配方。

### Procedure

- 用匹配运行日志逐核核对计时器与 IPI，再确认用户空间运行。

### Development findings

- V128 匹配日志记录八核活动；V129 用户确认桌面可用。

### Completion criteria

- 各启用核有计时器/IPI 活动且桌面保持响应。

### Current limits

- 完整 CPU 构建集成、调频与各类长期负载未在此公开仓库独立复现。

### Next action

- 迁入当前实际 CPU/XNU 构建配方；不因建站重复跑已通过的实机测试。

### Evidence

- `source`: [公开实现或维护者验证摘要；实机范围与重建限制见正文。](https://github.com/xiuyityer/UniXNU-tb371fc/blob/e6eeb91a3971a43bad2de09154c0b8dba51a2551/docs/VALIDATION.md)

## Memory and DMA {#memory}

`implemented`

### Hardware and dependencies

- 设备内存映射与 GPU SMMU；测试机标称 8 GB RAM。

### Configuration

- V129 普通 BO 仅在显式请求时使用连续物理内存；其余分配沿当前 GPU 路径。

### Procedure

- 校验源清单，按相同运行归属核对映射、分配和 GPU 完成记录。

### Development findings

- V128 存储与 GPU 在桌面阶段推进；V129 用户反馈滑动改善约 5–10 FPS。

### Completion criteria

- 声明的映射/分配路径能支持已验证的桌面工作负载。

### Current limits

- 标称 8 GB 不等于全部 RAM 均由 XNU 拥有；无全内存压力或全部 DMA 设备验证。

### Next action

- 整理所有保留内存/所有权清单；GPU 进一步性能优化按用户要求暂停。

### Evidence

- `source`: [公开实现或维护者验证摘要；实机范围与重建限制见正文。](https://github.com/xiuyityer/UniXNU-tb371fc/blob/e6eeb91a3971a43bad2de09154c0b8dba51a2551/docs/VALIDATION.md)
- `source`: [公开实现或维护者验证摘要；实机范围与重建限制见正文。](https://github.com/xiuyityer/UniXNU-tb371fc/blob/e6eeb91a3971a43bad2de09154c0b8dba51a2551/drivers/Adreno650/NativeAdrenoUserClient.cpp)

## Storage and root {#storage}

`implemented`

### Hardware and dependencies

- 目标 UFS、原工作区原生存储驱动和用户自行准备的系统/Data 输入。

### Configuration

- 保留 UFS producer gate 与来源锁；不公开设备分区身份及实际数据内容。

### Procedure

- 通过匹配日志核对根卷启动和持久写入，并由独立 TWRP 回读确认。

### Development findings

- 原生 UFS 已用于系统桌面；V128 Data 89613 次写入、零错误有匹配日志。

### Completion criteria

- 系统根卷支持用户空间启动，持久数据可在独立恢复环境回读。

### Current limits

- 完整存储/root 构建流程未导出；不声称用户 128 GB 全部作为 Data 可用。

### Next action

- 整理可重建的系统根卷与 Data 配方，保持每台设备独立绑定。

### Evidence

- `source`: [公开实现或维护者验证摘要；实机范围与重建限制见正文。](https://github.com/xiuyityer/UniXNU-tb371fc/blob/e6eeb91a3971a43bad2de09154c0b8dba51a2551/docs/VALIDATION.md)
- `source`: [公开实现或维护者验证摘要；实机范围与重建限制见正文。](https://github.com/xiuyityer/UniXNU-tb371fc/blob/e6eeb91a3971a43bad2de09154c0b8dba51a2551/package/UfsProducerGate/ProducerGate.c)

## Display {#display}

`implemented`

### Hardware and dependencies

- 目标显示帧缓冲与当前 GPU/Metal 路径。

### Configuration

- 使用 V128 恢复输入启动的 DisplayLifecycle；GPU 与输入生命周期同时保留。

### Procedure

- 启动到桌面并观察真实帧与滑动；显示日志与运行产物分别归属。

### Development findings

- V120 起用户确认桌面；V128/V129 用户确认显示与滑动。

### Completion criteria

- 真实屏幕显示桌面并随操作更新。

### Current limits

- 壁纸、亮度和全部显示模式尚未逐项验证；可显示桌面不代表应用均正常。

### Next action

- 优先复核壁纸和系统应用显示，保留已通过的桌面路径。

### Evidence

- `source`: [公开实现或维护者验证摘要；实机范围与重建限制见正文。](https://github.com/xiuyityer/UniXNU-tb371fc/blob/e6eeb91a3971a43bad2de09154c0b8dba51a2551/package/Tb371fcDisplay/DisplayLifecycle.cpp)
- `source`: [公开实现或维护者验证摘要；实机范围与重建限制见正文。](https://github.com/xiuyityer/UniXNU-tb371fc/blob/e6eeb91a3971a43bad2de09154c0b8dba51a2551/docs/VALIDATION.md)

## Input {#input}

`implemented`

### Hardware and dependencies

- 目标 Novatek 触摸、GENI SPI、PM8150 电源/音量输入和 HID 路径。

### Configuration

- 保留目标触摸实现、组合 HID 生命周期和 DisplayLifecycle 的 input\_start。

### Procedure

- 用匹配运行日志核对触摸到 HID，再由用户确认桌面滑动及电源键。

### Development findings

- V128 5323 次有效触摸读取、4784 次 HID 上报，错误为零；用户确认电源键息屏/亮屏。

### Completion criteria

- 触摸能控制桌面，按键按声明功能产生可观察行为。

### Current limits

- 音量键未正常工作；完整多指手势、长时间睡眠唤醒仍未逐项验证。

### Next action

- 保持现有触摸/电源键结果，后续修复音量键。

### Evidence

- `source`: [公开实现或维护者验证摘要；实机范围与重建限制见正文。](https://github.com/xiuyityer/UniXNU-tb371fc/blob/e6eeb91a3971a43bad2de09154c0b8dba51a2551/package/Tb371fcInput/Tb371fcHidLifecycle.cpp)
- `source`: [公开实现或维护者验证摘要；实机范围与重建限制见正文。](https://github.com/xiuyityer/UniXNU-tb371fc/blob/e6eeb91a3971a43bad2de09154c0b8dba51a2551/docs/VALIDATION.md)

## GPU {#gpu}

`implemented`

### Hardware and dependencies

- Adreno 650、目标 GMU/SMMU 与锁定版本 Metal/Turnip 转译路径；固件需自行准备。

### Configuration

- 当前 A650 后端、Pipa 21 项补丁与 V129 显式连续分配策略。

### Procedure

- 核对提交/完成日志并观察桌面滑动帧率；不要以初始化消息替代真实显示。

### Development findings

- V128 GPU 提交/完成推进；V129 用户观察滑动提高约 5–10 FPS。

### Completion criteria

- GPU 命令完成并能支撑真实桌面呈现。

### Current limits

- 未建立统一帧时间基准；V129 精确日志未回读；各应用/Metal 特性并未全面验证。

### Next action

- 按用户要求暂停 GPU 性能优化，转向剩余可用性问题。

### Evidence

- `source`: [公开实现或维护者验证摘要；实机范围与重建限制见正文。](https://github.com/xiuyityer/UniXNU-tb371fc/blob/e6eeb91a3971a43bad2de09154c0b8dba51a2551/drivers/Adreno650/NativeAdrenoUserClient.cpp)
- `source`: [公开实现或维护者验证摘要；实机范围与重建限制见正文。](https://github.com/xiuyityer/UniXNU-tb371fc/blob/e6eeb91a3971a43bad2de09154c0b8dba51a2551/docs/VALIDATION.md)

## Network {#network}

`planned`

### Hardware and dependencies

- 目标无线芯片、固件和 iPadOS 网络接口尚待整理。

### Configuration

- 公开快照没有已验证的目标网络构建配置。

### Procedure

- 先确定芯片与总线，再设计扫描/连接/收发验证。

### Development findings

- 没有公开可确认的 Wi-Fi 或蓝牙实机通过结果。

### Completion criteria

- 完成连接、地址分配及持续收发后才能声称支持。

### Current limits

- 当前不声称网络或蓝牙可用。

### Next action

- 在核心系统可用后整理目标无线接口证据。

### Evidence

Collect evidence using the next action.

## Audio {#audio}

`planned`

### Hardware and dependencies

- 目标 codec/DSP、时钟电源与音频服务接口尚待整理。

### Configuration

- 公开快照没有已验证的目标音频路由配置。

### Procedure

- 先确认目标音频路由与 ABI，再验证播放/录音及启停。

### Development findings

- 没有实机扬声器或麦克风通过结果。

### Completion criteria

- 各声明路由可播放或录制所需音频格式。

### Current limits

- 当前不声称音频可用。

### Next action

- 整理目标 codec/DSP 的上游实现与接口。

### Evidence

Collect evidence using the next action.

## Power {#power}

`implemented`

### Hardware and dependencies

- 目标平台电源、PM8150 按键与 iPadOS 电源管理接口。

### Configuration

- 保留平台发布及电源键 HID 路径。

### Procedure

- 分别验证电源键、充电/电量与睡眠恢复，不能用单项结果替代全部。

### Development findings

- 用户已确认电源键息屏/亮屏；系统可进入桌面。

### Completion criteria

- 每项声明的电源操作有对应观察；容量和充电状态需与实机一致。

### Current limits

- 电池容量和充电状态仍未正常识别；完整休眠、热管理和调频未验证。

### Next action

- 修复容量与充电状态，并保留现有电源键行为。

### Evidence

- `source`: [公开实现或维护者验证摘要；实机范围与重建限制见正文。](https://github.com/xiuyityer/UniXNU-tb371fc/blob/e6eeb91a3971a43bad2de09154c0b8dba51a2551/package/PlatformPower/Tb371fcPlatformPower.cpp)
- `source`: [公开实现或维护者验证摘要；实机范围与重建限制见正文。](https://github.com/xiuyityer/UniXNU-tb371fc/blob/e6eeb91a3971a43bad2de09154c0b8dba51a2551/docs/VALIDATION.md)

## Image assembly {#packaging}

`implemented`

### Hardware and dependencies

- 真实 macOS/Xcode 工具与维护者自行准备的系统/固件输入。

### Configuration

- V135 从保留父 kernel 作定点二进制派生；公开脚本在原生 macOS 重编 EDK2 固件、BootShim 和 boot 镜像。

### Procedure

- 构建后校验实际镜像，再将源、产物哈希、运行与物理结果对应。

### Development findings

- V135 quick-pack 使用本地私有输入复现已确认镜像 SHA；干净固件源码构建生成未实机测试的不同候选。

### Completion criteria

- 有精确的快速恢复入口及清晰标注的源码构建边界。

### Current limits

- 完整 XNU 源码构建未接通；生成完整系统仍需私有 Apple 系统、ABI、固件、Data 与恢复输入；CI 不构建 iPadOS。

### Next action

- 后续从 V135 稳定基准继续接通 XNU 构建，按用户指定恢复实机任务。

### Evidence

- `source`: [公开实现或维护者验证摘要；实机范围与重建限制见正文。](https://github.com/xiuyityer/UniXNU-tb371fc/blob/e6eeb91a3971a43bad2de09154c0b8dba51a2551/docs/BUILDING.md)
- `source`: [公开实现或维护者验证摘要；实机范围与重建限制见正文。](https://github.com/xiuyityer/UniXNU-tb371fc/blob/e6eeb91a3971a43bad2de09154c0b8dba51a2551/docs/VALIDATION.md)

## Diagnostics {#diagnostics}

`implemented`

### Hardware and dependencies

- 原生日志区域、独立恢复环境回读与匹配的产物归属。

### Configuration

- 通用 RootLog 源码公开，设备专属令牌和分区绑定保留本地。

### Procedure

- 按当次 logger/运行和产物哈希回读；公开部分只运行源码与记录检查。

### Development findings

- V128 原生日志已独立回读；V129 用户结果与精确日志回读状态分开记录。

### Completion criteria

- 每项结论可追溯到对应运行或明确标注的用户报告。

### Current limits

- 日志时长有限，不保证记录最后一次 panic；公开摘要不是原始完整证据。

### Next action

- 完善公开可复核的去标识摘要；不重放一次性历史测试记录。

### Evidence

- `source`: [公开实现或维护者验证摘要；实机范围与重建限制见正文。](https://github.com/xiuyityer/UniXNU-tb371fc/blob/e6eeb91a3971a43bad2de09154c0b8dba51a2551/package/RootLog/Journal32.h)
- `source`: [公开实现或维护者验证摘要；实机范围与重建限制见正文。](https://github.com/xiuyityer/UniXNU-tb371fc/blob/e6eeb91a3971a43bad2de09154c0b8dba51a2551/docs/VALIDATION.md)

</div>
