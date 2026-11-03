# Nothing Phone \(2\) \(pong\)

[Chengdong-Yu/UniXNU-pong](https://github.com/Chengdong-Yu/UniXNU-pong)

<div v-pre>

Nothing Phone \(2\), iPadOS18 Darwin24 local format2 migration and board adaptation

Source record: [porting.toml](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/porting.toml), `941aa2de07615a55d487f8f93188ff751ea8436a`.

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
| [mobilegestalt-device-information](#mobilegestalt-device-information) | `implemented` |
| [native-category-volume](#native-category-volume) | `implemented` |
| [native-ringtone-display-wake](#native-ringtone-display-wake) | `implemented` |
| [main-gpu-metal-ringer149](#main-gpu-metal-ringer149) | `implemented` |
| [adreno-ringer-freeze150](#adreno-ringer-freeze150) | `implemented` |
| [control-center-native-ringtone151](#control-center-native-ringtone151) | `implemented` |
| [upstream-metal-keyboard152](#upstream-metal-keyboard152) | `implemented` |
| [gpu-guide-memory-bgra153](#gpu-guide-memory-bgra153) | `implemented` |
| [gpu-real-execution-hotpath155](#gpu-real-execution-hotpath155) | `implemented` |
| [metal-interface-ui-stalls156](#metal-interface-ui-stalls156) | `implemented` |
| [gpu-priority-timing160](#gpu-priority-timing160) | `implemented` |
| [audio-wake-active-acquire162](#audio-wake-active-acquire162) | `implemented` |
| [audio-prepare-command-stages163](#audio-prepare-command-stages163) | `implemented` |
| [lock-sound-admission164](#lock-sound-admission164) | `implemented` |
| [scheduling-metal-audio-clock165](#scheduling-metal-audio-clock165) | `implemented` |
| [submit-retirement-publication166](#submit-retirement-publication166) | `implemented` |
| [frame-ownership-pac167](#frame-ownership-pac167) | `implemented` |
| [local-runtime-integration](#local-runtime-integration) | `implemented` |
| [cumulative-runtime-pr167](#cumulative-runtime-pr167) | `implemented` |

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

- 格式2原生构建依赖已补齐公开固定来源、local.toml路径和配置前置条件；本轮为未发布的本地源码审计。

### Completion criteria

- 在设备上观察该接口的实际工作结果并保存对应日志

### Current limits

- SM8475公共层与Pong聚合源码分目录固定；平台组件进一步拆分待完成。

### Next action

- 读取本轮启动日志并继续完成板级接口

### Evidence

- `source`: [Explicit CDC REC/Fastboot commands and a physical DWC3 Mux bridge to native lockdownd implemented; root-only queues and real iOS pairing retained. Pong MI2S playback hardware endpoint direction/container adapted. Automatic restart remains off; device results pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services136-usb-mux-manual-reset-audio.md)
- `source`: [services129: UniXNU core fast-forward 066c8d8 -&gt; f0721e9; upstream delta contains device records only. Existing core overrides and user scripts preserved. Matching Darwin24 kernel compiled; hardware effects pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services129-prm-usb-dma.md)
- `source`: [配置、获取入口和实际编译器路径已对齐。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services74-source-audit.md)
- `source`: [UniXNU同步至40d21cc，构建记录保存真实上游HEAD与本地修改状态。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services76-upstream-audit.md)

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

- `source`: [现有设备可进入桌面，物理内存与可分配内存分别记录。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/format2/README.zh.md)

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

- services90基于services89八核first boot完成记录，新增非RT/非绑定线程的空闲核心排序X2→A710→A510；保留全部native推荐核心、RT和绑定规则，编译通过，实机性能待确认。
- services81实际启动8核，EPSS最高非boost请求为CPU0-3 1804800kHz、CPU4-6 2496000kHz、CPU7 2995200kHz；性能问题不能简单归因于没有开启多核。

### Completion criteria

- 在设备上观察该接口的实际工作结果并保存对应日志

### Current limits

- 请求频率并非持续有效频率测量；未运行性能基准。

### Next action

- 读取本轮启动日志并继续完成板级接口

### Evidence

- `source`: [依据services98阻塞栈拆开网络开启与SC配置；原生VAD实际端口路由、GLINK48项、SCM共享锁、GPU512MiB池及锁外fence等待已编译。用户授权重建Data；设备结果待观察。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services99-speaker-network-data.md)
- `source`: [CPU 4/3/1 拓扑保持 SM8475；受管内存沿用已启动实现。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/format2/README.zh.md)
- `source`: [固定高频请求已编译；实际频率与持续负载未实机确认。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services75-performance.md)
- `source`: [基于services81日志的板级与运行时实际修补已完整编译；设备效果待确认。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services82-runtime-performance.md)

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

- `source`: [依据services98阻塞栈拆开网络开启与SC配置；原生VAD实际端口路由、GLINK48项、SCM共享锁、GPU512MiB池及锁外fence等待已编译。用户授权重建Data；设备结果待观察。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services99-speaker-network-data.md)
- `source`: [物理容量12GiB；此前受管容量9728MiB，不能将物理空洞分配给VM。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/format2/README.zh.md)

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

- `source`: [services129 REC stops during root SID e0 -&gt; bank74 migration before APFS/APM. services130 serializes UFS Apps-SMMU plan/configuration with the shared lease and delays optional USB until actual root readiness. Kernel compiled; restored boot pending device observation.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services130-root-smmu-order.md)
- `source`: [services115/116：OS-only rootful 授权及真实根卷写探针通过；SystemOS 保持只读，UFS Data 保留。可写 OS 的后续主机更新采用完整一致代际，不叠加旧主机元数据到 guest 改写后的 APFS。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services116-runtime-adapters.md)
- `source`: [依据services98阻塞栈拆开网络开启与SC配置；原生VAD实际端口路由、GLINK48项、SCM共享锁、GPU512MiB池及锁外fence等待已编译。用户授权重建Data；设备结果待观察。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services99-speaker-network-data.md)
- `source`: [本机OS中init及音频策略已更新，设备仍保留services72。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services73-smmu-audio.md)

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

- services83驱动耗时约40–52ms/帧；services84复用线性纹理并将scanout导入限定为三帧，保留缓存维护和真实fence。
- services85 DBV写入后回读32并永久停用；services86加入LP优先、锁存等待和有界重试，保留真实错误及后续请求。
- services86显示服务连续SIGSEGV引发SpringBoard/replicatord退出；services87修复GPU连接所有权回退，桌面结果待实机确认。
- services87 写00b4后读22/00/b4，services88修正GET字节序，保留原始DBV和真实错误，允许后续请求。

### Completion criteria

- 在设备上观察该接口的实际工作结果并保存对应日志

### Current limits

- 120Hz为显示模式；新一轮实际帧率与滑块调光未确认。

### Next action

- 读取本轮启动日志并继续完成板级接口

### Evidence

- `source`: [services141 REC: wake stalls display after scanout kNoResource while keys/WLAN/services continue. services142 retains bounded valid idle imports and releases real surface completion before asynchronous optional cache eviction; device result pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services142-wake-usb-audio.md)
- `source`: [services131 REC: power HID events delivered, swap3783/3786 surface183 incomplete and no-submit scanout resource refusal; other services continued. services132 implements paired user/kernel source retirement on idle or not-submitted copies, after draining temporary objects. Kernel, matching bundle and loader compiled; sleep/wake result pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services132-wake-usb-ownership.md)
- `source`: [services111 REC identifies null ath11k split-BSS callback panic, mobile HAL default setters rejected, native input modes persisted but phone keyboard layout absent. services112 real BSS adapters, UID-selected VAD ports, native kbd startup and same-build phone resources compiled/staged; stock arm64e Phone deferred, baseband still absent. Device effects pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services112-wifi-audio-phone-input.md)
- `source`: [services109 REC: ADSP stage9 ENOMEM removed physical audio/battery sources, SBRenderer Neutrino abort follows refused Metal connection, keyboard list persisted but not shown. services110 early PAS/bounce allocation, 10 isolated GPU client scopes and native TextInput refresh compiled; device effects unverified. Timed restart stays off.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services110-adsp-poster-textinput.md)
- `source`: [services107 timed REC complete: native InterfaceNamer timeout completion unblocks wifid manager and SpringBoard; real device count1, 29 scanned BSS, first visible frame and continuing swaps. Native audio UID preference and PowerUI retained; Settings association, PCM route and audible output remain unconfirmed.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services107-interface-namer-handshake.md)
- `source`: [首帧 SwapWait 零ID与原生轮询语义已修复；audiomxd stderr权限回归修复，576项服务缓存与独立plist一致。自动重启实现已删除，真机效果待观察。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services98-first-frame-launch-policy.md)
- `source`: [services97: native en0 SC service/arrival, exact preferences entitlements, real VirtualAudio UID defaults, authorized IOSurface GPU/CPU handoff and actual swap retirement compiled. Device effects remain unconfirmed; base build scripts and Data retained.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services97-native-endpoint-handoff.md)
- `source`: [桌面与壁纸已有显示；120Hz是请求值，不代表测得帧率。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/format2/README.zh.md)
- `source`: [基于services81日志的板级与运行时实际修补已完整编译；设备效果待确认。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services82-runtime-performance.md)
- `source`: [按官方四份文档核对传输、服务和Darwin24接口，实际修补已完整编译，设备结果待确认。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services83-official-peripherals.md)
- `source`: [本轮板级接口、按键去抖、音频插件和显示资源复用已完整编译，实际功能效果待设备反馈。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services84-peripheral-interfaces.md)
- `source`: [已按真实backboardd IPS修复22H374背光默认映射初始化，并在真实UFS根卷补齐标准匹配属性；完整内核和运行时已编译，界面恢复待设备反馈。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services85-backlight-startup.md)
- `source`: [完整内核与匹配运行时已编译，56MiB OS差量安装完成；临时启动Sending 2.341s/Booting 10.177s均OKAY，实际外设效果待确认。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services88-native-peripherals.md)
- `source`: [services92 completed timed REC capture after 72 MiB OS update. User confirms brightness adjustment works; native IOHID report device now opens. Wi-Fi remains unavailable to user, no association or PCM StartIO observed; no BV/OOM error in this capture. Source repairs and remaining interface faults recorded separately.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services92-peripherals-latency.md)

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

- services83已有真实音量按下/释放与共享增益更新；services84将待确认边沿的去抖读取缩短为8ms，回退轮询16ms。
- services86实体gain显示独立短暂HUD，达到上下限停止重复，保留PMIC transition来源。
- services88删除notify直改增益/HUD，实体音量键经标准键盘/Consumer报告进入原生HID parser；电源与触控路径保留。
- 用户确认services112系统输入法正常；该结论不等于音量键已验证。services113保留原输入法和按键实现。

### Completion criteria

- 在设备上观察该接口的实际工作结果并保存对应日志

### Current limits

- 短按和音频联动需设备确认。

### Next action

- 读取本轮启动日志并继续完成板级接口

### Evidence

- `source`: [services132 keeps native HID and the PCM/control lock split, no panic in this capture. services133 preserves those changes; no new user confirmation of wake/volume behavior.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services133-parity-audio-usb.md)
- `source`: [services109 REC: ADSP stage9 ENOMEM removed physical audio/battery sources, SBRenderer Neutrino abort follows refused Metal connection, keyboard list persisted but not shown. services110 early PAS/bounce allocation, 10 isolated GPU client scopes and native TextInput refresh compiled; device effects unverified. Timed restart stays off.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services110-adsp-poster-textinput.md)
- `source`: [Native audio plugin-ID AudioValueTranslation and prts/rtcf target corrected; Consumer-only volume HID and missing keyboard defaults built. Wi-Fi retained; audible output and keyboard device result pending. Timed restart disabled by latest user request.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services109-audio-plugin-keyboard.md)
- `source`: [按键入口与用户态/HID链路编译通过，动作效果未实机确认。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services74-source-audit.md)
- `source`: [基于services81日志的板级与运行时实际修补已完整编译；设备效果待确认。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services82-runtime-performance.md)
- `source`: [按官方四份文档核对传输、服务和Darwin24接口，实际修补已完整编译，设备结果待确认。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services83-official-peripherals.md)
- `source`: [本轮板级接口、按键去抖、音频插件和显示资源复用已完整编译，实际功能效果待设备反馈。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services84-peripheral-interfaces.md)
- `source`: [完整内核与匹配运行时已编译，56MiB OS差量安装完成；临时启动Sending 2.341s/Booting 10.177s均OKAY，实际外设效果待确认。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services88-native-peripherals.md)
- `source`: [services92 completed timed REC capture after 72 MiB OS update. User confirms brightness adjustment works; native IOHID report device now opens. Wi-Fi remains unavailable to user, no association or PCM StartIO observed; no BV/OOM error in this capture. Source repairs and remaining interface faults recorded separately.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services92-peripherals-latency.md)
- `source`: [services94: 72 MiB OS update and temporary boot completed; timed REC captured. QCA6490 registered en0 and scanned 19 BSS with Pong firmware; Settings/association remain unconfirmed. Native HID and physical audio ASPL registered; no button press or PCM StartIO in this capture. Brightness repair retained.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services94-native-volume-wlan.md)
- `source`: [services94 REC shows AppleUserHIDEventDriver waiting about 120 seconds before kernel HID fallback. services95 adds an exact Pong SPMI volume-key personality without IOMatchDefer, retaining native Consumer reports and stock HID rules. Prelink boot image built from the completed Darwin24 kernel; device result pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services95-hid-driverkit-wait.md)

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

- services89桌面后出现BV opcode fault（0x2000/0x70970001）；services90按Nothing gen7与Linux a7xx补齐IB1LIST起止标记，保留fence、同步和故障BO所有权，编译通过，是否消除故障待确认。
- services81已有实际GPU scanout完成记录；一段日志为49帧/7873ms，驱动约55ms/帧。
- services82配套内核与Metal前端使用8项源映射/导入缓存和独立source\_id，保留实际fence和DMA隔离；已编译。
- services86为scanout建立独立Vulkan上下文，缩小缓存维护范围，真实fence和错误保留策略不变。
- services86独立Vulkan device与Turnip全局dw连接冲突，导致backboardd空指针崩溃；services87撤销该路径，复用单一真实设备/独立queue。
- services113: actual compiled NativeAdrenoUserClient now allocates stable 128-entry chunks on demand; preserves BO/queue/fence ownership. Device refusal reason and original status retained. Wallpaper outcome pending.

### Completion criteria

- 在设备上观察该接口的实际工作结果并保存对应日志

### Current limits

- 未进行性能基准；尚未取得services82设备帧率或稳定性结果。

### Next action

- 读取本轮启动日志并继续完成板级接口

### Evidence

- `source`: [services134 has global \* discovery and real Vulkan device, GPU scanout and1030 actual completed command buffers at60s, mean18.9ms. services135 retains global ABI1/A730/22H374 and fills two missing SPI limits from actual runtime capabilities. New build completed; no fabricated family/core capabilities.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services135-codecs-usb-global-metal.md)
- `source`: [services133 compiled: adapted 88604d0/278333f BGRA opaque GPU scanout, bounded contiguous BO fallback, frame/format accounting and resumable idle priming to A730/22H374 ABI1; preserved source retirement and real fences. Device effects pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services133-parity-audio-usb.md)
- `source`: [services128 preserves working ABI1/bridge/Turnip and merges overlapping same-phase CPU maintenance ranges; does not skip coherency or fence retirement. Device performance pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services128-speaker-identity-usb.md)
- `source`: [services125 REC: actual GPU copy completion, no retained three-refusal exit; high optional-service churn and 8-18fps driver stats. services126 builds IRQ sleep-race fix, preserves ABI1 and scanout2 source reuse; throttles confirmed respawn storms, reduces broad debug logging. Performance improvement unconfirmed.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services126-audio-package-latency.md)
- `source`: [services124 REC confirms real scanout worker and completed GPU copies. After power-key sleep/wake, three kNoResource frames stop the old worker; user reports flicker.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services125-wake-scanout-usb.md)
- `source`: [services125 kernel/plugin compile completed: bounded retained source mappings and private scanout wire2 generations enable actual three-source import reuse; no-submission pressure backoff/recovery preserves genuine DMA quarantine. BO/submit ABI1 retained. OS install complete, Data/SystemOS retained; services125 temporary Fastboot Sending 2.333s / Booting 10.129s OKAY. Wake flicker result pending. Native Apple USB still lacks board device-controller backend; actual Pong eUSB2/repeater/SID0 inputs captured, not marked functional.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services125-wake-scanout-usb.md)
- `source`: [services123 REC: native CP/firmware/IRQ and backboardd Metal creation succeeded, boot policy scanout=0; zero framebuffer swaps, no new panic or late process snapshots. User reports no desktop/freeze. VM-backed BO regression suspected, precise blocked stack unavailable.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services124-scanout-startup.md)
- `source`: [services124 restores services122 wired BO/client-view ownership and retains its bounded shared-ring retirement fixes. Existing compatible services123 Metal bundle retained. Darwin24 kernel and prelinked image built. services124 temporary Fastboot Sending 2.337s / Booting 10.176s OKAY, GPU scanout=1 and 128MiB pool. Existing OS/Data retained; actual first-frame and scanout completion pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services124-scanout-startup.md)
- `source`: [services122 用户确认桌面可启动，但输入慢/可能冻结；REC 发现 backboardd repeated texture OutOfMemory\(Device\)，未证实 kbd 自身崩溃。services123 保留 ABI1，改用共享 VM-backed BO descriptor、移植 bounded IOSurface reuse/pressure reclamation、MTL object interfaces 和 22H374 UUID-qualified 8-bit compositor policy。Darwin24 kernel + final 22H374 runtime compiled/linked. OS install complete, Data/SystemOS retained; Fastboot services123 Sending 2.332s / Booting 10.176s OKAY. No automatic reboot. Keyboard responsiveness/freeze fix remains unconfirmed on device.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services123-keyboard-gpu-memory.md)
- `source`: [services115/116：Pong SMMU/GMU/CP 认证 fence 和真实加速器发布通过。Metal 查询返回成功但参数全零，定位并修复普通分支漏掉核心 dispatch；services117 编译/设备结果待记录。未确认实际渲染。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services116-runtime-adapters.md)
- `source`: [services110 REC: actual scan but no association, native audio ports present without PCM/volume, GPU waits dominate display copies. services111 corrects 22H374 association offsets, native VAD defaults and upstream Metal tile-store/query/TLB overhead; actual device results pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services111-association-metal-route.md)
- `source`: [依据services98阻塞栈拆开网络开启与SC配置；原生VAD实际端口路由、GLINK48项、SCM共享锁、GPU512MiB池及锁外fence等待已编译。用户授权重建Data；设备结果待观察。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services99-speaker-network-data.md)
- `source`: [首帧 SwapWait 零ID与原生轮询语义已修复；audiomxd stderr权限回归修复，576项服务缓存与独立plist一致。自动重启实现已删除，真机效果待观察。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services98-first-frame-launch-policy.md)
- `source`: [services97: native en0 SC service/arrival, exact preferences entitlements, real VirtualAudio UID defaults, authorized IOSurface GPU/CPU handoff and actual swap retirement compiled. Device effects remain unconfirmed; base build scripts and Data retained.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services97-native-endpoint-handoff.md)
- `source`: [已有桌面硬件渲染记录，保留此前高RAM BO和copy分配修补。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/format2/README.zh.md)
- `source`: [GPU高频请求和提交范围优化已编译，未实机确认。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services75-performance.md)
- `source`: [上游句柄索引、16384对象容量和64次诊断取样已移植，保留Pong批量ABI与V500同步；完整Darwin24编译通过。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services76-upstream-audit.md)
- `source`: [基于services81日志的板级与运行时实际修补已完整编译；设备效果待确认。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services82-runtime-performance.md)
- `source`: [services92 completed timed REC capture after 72 MiB OS update. User confirms brightness adjustment works; native IOHID report device now opens. Wi-Fi remains unavailable to user, no association or PCM StartIO observed; no BV/OOM error in this capture. Source repairs and remaining interface faults recorded separately.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services92-peripherals-latency.md)

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

- services89在物理电源采样中提前退出、未加载固件；services90在既有稳定期限内重试失败的完整SPMI样本，仍需真实物理供电就绪，继续使用Pong活动槽QCA6490固件，编译通过。
- services83完成真实station和13个热点扫描，未再见RDDM；services84修补19字节能力枚举、媒体列表和物理接口查询。
- services86实际扫描15个BSS，未见关联/DHCP成功；界面缺失主因为显示服务崩溃。
- services88根据22H374 IO80211原生用户客户端补齐selector0请求转交、selector1/7能力查询，移除自制设置页面和board私有控制API；扫描/连接复用真实station。
- services89修补新增原生请求15KiB OOL描述符在readBytes/writeBytes前未prepare的错误，输入输出配对prepare/complete；保留services88接口与运行时，启动恢复待实机确认。
- 用户确认services112 Wi-Fi连接正常，services113不改动QCA6490固件、关联路径或现有Data配置。

### Completion criteria

- 在设备上观察该接口的实际工作结果并保存对应日志

### Current limits

- 扫描已确认；设置列表、关联与IP联网仍需新一轮实机结果。

### Next action

- 读取本轮启动日志并继续完成板级接口

### Evidence

- `source`: [services111 REC identifies null ath11k split-BSS callback panic, mobile HAL default setters rejected, native input modes persisted but phone keyboard layout absent. services112 real BSS adapters, UID-selected VAD ports, native kbd startup and same-build phone resources compiled/staged; stock arm64e Phone deferred, baseband still absent. Device effects pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services112-wifi-audio-phone-input.md)
- `source`: [services110 REC: actual scan but no association, native audio ports present without PCM/volume, GPU waits dominate display copies. services111 corrects 22H374 association offsets, native VAD defaults and upstream Metal tile-store/query/TLB overhead; actual device results pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services111-association-metal-route.md)
- `source`: [User confirms services108 Wi-Fi fixed after native InterfaceNamer handshake. Device count1 and real scan observed; association/DHCP/throughput not independently confirmed.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services108-native-audio-port-query.md)
- `source`: [services107 timed REC complete: native InterfaceNamer timeout completion unblocks wifid manager and SpringBoard; real device count1, 29 scanned BSS, first visible frame and continuing swaps. Native audio UID preference and PowerUI retained; Settings association, PCM route and audible output remain unconfirmed.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services107-interface-namer-handshake.md)
- `source`: [services103: ADSP ready/channel up, actual battery 100% 4428mV republished, QCA6490 en0 scanned 10 BSS after 64MiB DMA fix. Native Wi-Fi manager still timed out; no audio StartIO or confirmed VAD route. services104 runtime corrections pending device evidence.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services104-system-peripheral-order.md)
- `source`: [services99实际在加载固件前128MiB DMA分配失败；本轮改用VM内存对象并显式固定页面，保留WC/SID隔离与512MiB GPU池，完整编译通过；注册、开关和联网待确认。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services100-native-speaker.md)
- `source`: [依据services98阻塞栈拆开网络开启与SC配置；原生VAD实际端口路由、GLINK48项、SCM共享锁、GPU512MiB池及锁外fence等待已编译。用户授权重建Data；设备结果待观察。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services99-speaker-network-data.md)
- `source`: [首帧 SwapWait 零ID与原生轮询语义已修复；audiomxd stderr权限回归修复，576项服务缓存与独立plist一致。自动重启实现已删除，真机效果待观察。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services98-first-frame-launch-policy.md)
- `source`: [services97: native en0 SC service/arrival, exact preferences entitlements, real VirtualAudio UID defaults, authorized IOSurface GPU/CPU handoff and actual swap retirement compiled. Device effects remain unconfirmed; base build scripts and Data retained.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services97-native-endpoint-handoff.md)
- `source`: [网络入口、station边界和native4K函数均有定义；尚未验证扫描或联网。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services74-source-audit.md)
- `source`: [MSI/TX wake接入有界事件等待，登记后复查避免丢失通知；无线编译通过，链路和扫描未实机确认。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services76-upstream-audit.md)
- `source`: [已合并用户上游并完成完整Darwin24编译，包含本轮SMMU策略修复。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services79-upstream-runtime-audit.md)
- `source`: [Pong当前modem\_b固件、延后MAC启动与RDDM请求终结已完整编译打包；Fastboot Sending/Booting均OKAY，设置/扫描/联网待实机确认。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services81-wifi-firmware.md)
- `source`: [基于services81日志的板级与运行时实际修补已完整编译；设备效果待确认。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services82-runtime-performance.md)
- `source`: [按官方四份文档核对传输、服务和Darwin24接口，实际修补已完整编译，设备结果待确认。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services83-official-peripherals.md)
- `source`: [本轮板级接口、按键去抖、音频插件和显示资源复用已完整编译，实际功能效果待设备反馈。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services84-peripheral-interfaces.md)
- `source`: [完整内核与匹配运行时已编译，56MiB OS差量安装完成；临时启动Sending 2.341s/Booting 10.177s均OKAY，实际外设效果待确认。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services88-native-peripherals.md)
- `source`: [services92 completed timed REC capture after 72 MiB OS update. User confirms brightness adjustment works; native IOHID report device now opens. Wi-Fi remains unavailable to user, no association or PCM StartIO observed; no BV/OOM error in this capture. Source repairs and remaining interface faults recorded separately.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services92-peripherals-latency.md)

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

- services83实体HAL已连接但未见StartIO；services84删除插件内非法重入客户端HAL的路由线程，补齐身份和class qualifier过滤。
- services86实体gain/mute变化通知HAL属性缓存，记录真实设备发现结果；尚无StartIO或出声确认。
- services88删除SpringBoard直改增益客户端，补齐标准HAL静音对象、OwnedObjects/ControlList与通知；现有UID匹配通用驱动，尚无StartIO或PCM出声证据。
- services113 preserves the repaired real HAL port selection; fixes the ADSP mapping failure that prevented physical output readiness. Audible PCM remains unconfirmed.

### Completion criteria

- 在设备上观察该接口的实际工作结果并保存对应日志

### Current limits

- 实体PCM播放尚未确认；不发布不存在的输入端口。

### Next action

- 读取本轮启动日志并继续完成板级接口

### Evidence

- `source`: [services142 native0..16 volume applies linear amplitude and matching piecewise dB metadata; avoids exponential attenuation of already scaled CoreAudio PCM. Physical speaker gain/protections retained; audible output unconfirmed.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services142-wake-usb-audio.md)
- `source`: [services141 temporary boot succeeded; native CoreAudio S16-&gt;Q31 produced nonzero peak66496 at volume4/gain1039/mute0; both real TFA9873 AMPS/SWS and hard\_mute0 observed. Audible output remains unconfirmed.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services141-native-usb-pcm.md)
- `source`: [services141 native S16 ring explicitly converts to physical Q31; ASBD, byte counts and volume curve agree. Kernel/init compiled; factory amp gains and protections retained. Actual audible output unconfirmed.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services141-native-usb-pcm.md)
- `source`: [Live Pong DT tertiary RX data line is BIT\(1\), SD1, while TX feedback is SD0. Corrected AudioReach SD index from1 to2; matching native kernel compiled. Prior PCM/WRITE\_DONE was real but did not prove analog output. Audible result pending device observation.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services137-native-mux-speaker-sd1.md)
- `source`: [services134 native AudioConverterService/IOAudio2 starts, nonzero committed PCM and DSP WRITE\_DONE confirmed; TFA status11 remains8040 after PCM, audible output still absent. services135 removes the unreturned self-HAL graph query and builds an independent software-first installed Apple decoder adapter for audio-only targets. Actual decoding/audible result pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services135-codecs-usb-global-metal.md)
- `source`: [services133 REC confirms native Speaker discovery, nonzero committed CoreAudio PCM and DSP WRITE\_DONE; audible output absent per user. services134 adds real TFA9873 KEY2 volatile configuration, checked format/amp state, native stream active state and restart position reset, plus audiomxd-local HAL route inspection. Kernel and HAL compiled; actual audible result pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services134-speaker-usb-qup.md)
- `source`: [services132 REC has native Speaker, PRM clock, real DSP completions and nonzero PCM. services133 explicitly enables TFA9873 TDMSPKE and observes amp state after initial PCM; audible result pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services133-parity-audio-usb.md)
- `source`: [services132 volume follow-up: hardware DSP start wait no longer holds PCM/volume gate; registry controls publish through a separate lock. Native volume HID and controls retained, no fabricated running state. Kernel compiled; actual key/HUD result pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services132-wake-usb-ownership.md)
- `source`: [services131 restores the original exclusive 64KiB UEFI audio DMA contract, preserving native PCM/MI2S clock/retry fixes. Audible output remains unconfirmed.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services131-usb-conflict-isolation.md)
- `source`: [services130 preserves real native PCM and tertiary MI2S clock path. Keeps the original failure across cleanup, reports start failure to CoreAudio and allows explicit retry only after proven graph/amp retirement; unknown DMA remains retained. No audible output confirmed.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services130-root-smmu-order.md)
- `source`: [services128 real nonzero native PCM and DSP WRITE\_DONE confirmed, audible output still absent by user report. services129 adds actual tertiary MI2S PRM clock 0x104 at 3.072 MHz, dedicated PRM replies and release lifecycle. Pong TFA profile retained; actual sound pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services129-prm-usb-dma.md)
- `source`: [services127 no longer crashes audiomxd; native and legacy PCM devices coexisted. services128 makes native Speaker the sole owner, retains clock adapter, consumes only committed sample ranges. Actual speaker sound remains pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services128-speaker-identity-usb.md)
- `source`: [services126 real PCM output started, then audiomxd SIGBUS on read-only native status+0x18; services127 corrects shared RW status. Slider and HID keys work by user observation; audible PCM after fix remains pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services127-native-audio-rootful.md)
- `source`: [services126 builds true builtin Speaker UID/transport, writable native controls, native/legacy stream mapping IDs and transport-matched VAD queries; no fake Hawking/capture. Actual PCM/StartIO/output remains unconfirmed.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services126-audio-package-latency.md)
- `source`: [services116：物理 TFA9873/ADSP 端点存在，真实 HAL 确认 rtcf 32 字节且可写；原生路由配置返回 -12986，VAD 音量能力仍0，PCM/声音尚未确认。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services116-runtime-adapters.md)
- `source`: [services111 REC identifies null ath11k split-BSS callback panic, mobile HAL default setters rejected, native input modes persisted but phone keyboard layout absent. services112 real BSS adapters, UID-selected VAD ports, native kbd startup and same-build phone resources compiled/staged; stock arm64e Phone deferred, baseband still absent. Device effects pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services112-wifi-audio-phone-input.md)
- `source`: [services110 REC: actual scan but no association, native audio ports present without PCM/volume, GPU waits dominate display copies. services111 corrects 22H374 association offsets, native VAD defaults and upstream Metal tile-store/query/TLB overhead; actual device results pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services111-association-metal-route.md)
- `source`: [services109 REC: ADSP stage9 ENOMEM removed physical audio/battery sources, SBRenderer Neutrino abort follows refused Metal connection, keyboard list persisted but not shown. services110 early PAS/bounce allocation, 10 isolated GPU client scopes and native TextInput refresh compiled; device effects unverified. Timed restart stays off.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services110-adsp-poster-textinput.md)
- `source`: [Native audio plugin-ID AudioValueTranslation and prts/rtcf target corrected; Consumer-only volume HID and missing keyboard defaults built. Wi-Fi retained; audible output and keyboard device result pending. Timed restart disabled by latest user request.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services109-audio-plugin-keyboard.md)
- `source`: [services107 timed REC complete: native InterfaceNamer timeout completion unblocks wifid manager and SpringBoard; real device count1, 29 scanned BSS, first visible frame and continuing swaps. Native audio UID preference and PowerUI retained; Settings association, PCM route and audible output remain unconfirmed.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services107-interface-namer-handshake.md)
- `source`: [services103: ADSP ready/channel up, actual battery 100% 4428mV republished, QCA6490 en0 scanned 10 BSS after 64MiB DMA fix. Native Wi-Fi manager still timed out; no audio StartIO or confirmed VAD route. services104 runtime corrections pending device evidence.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services104-system-peripheral-order.md)
- `source`: [22H374原生IOAudio2输出、S32环、原生音量/静音、DSP硬件启动后时钟已完整编译。保持实际Pong功放与DMA，无输入端点；出声与系统路由待真机确认。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services100-native-speaker.md)
- `source`: [依据services98阻塞栈拆开网络开启与SC配置；原生VAD实际端口路由、GLINK48项、SCM共享锁、GPU512MiB池及锁外fence等待已编译。用户授权重建Data；设备结果待观察。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services99-speaker-network-data.md)
- `source`: [首帧 SwapWait 零ID与原生轮询语义已修复；audiomxd stderr权限回归修复，576项服务缓存与独立plist一致。自动重启实现已删除，真机效果待观察。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services98-first-frame-launch-policy.md)
- `source`: [services97: native en0 SC service/arrival, exact preferences entitlements, real VirtualAudio UID defaults, authorized IOSurface GPU/CPU handoff and actual swap retirement compiled. Device effects remain unconfirmed; base build scripts and Data retained.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services97-native-endpoint-handoff.md)
- `source`: [音频服务、用户客户端和现代HAL编译链接通过，PCM播放仍未验证。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services74-source-audit.md)
- `source`: [物理DMA交接、音量/静音对应和配套HAL已编译，实际出声仍待确认。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services79-upstream-runtime-audit.md)
- `source`: [基于services81日志的板级与运行时实际修补已完整编译；设备效果待确认。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services82-runtime-performance.md)
- `source`: [按官方四份文档核对传输、服务和Darwin24接口，实际修补已完整编译，设备结果待确认。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services83-official-peripherals.md)
- `source`: [本轮板级接口、按键去抖、音频插件和显示资源复用已完整编译，实际功能效果待设备反馈。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services84-peripheral-interfaces.md)
- `source`: [完整内核与匹配运行时已编译，56MiB OS差量安装完成；临时启动Sending 2.341s/Booting 10.177s均OKAY，实际外设效果待确认。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services88-native-peripherals.md)
- `source`: [services94: 72 MiB OS update and temporary boot completed; timed REC captured. QCA6490 registered en0 and scanned 19 BSS with Pong firmware; Settings/association remain unconfirmed. Native HID and physical audio ASPL registered; no button press or PCM StartIO in this capture. Brightness repair retained.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services94-native-volume-wlan.md)

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

- services90对照Nothing qti\_battery\_charger修正0x04通知订阅为TYPE\_NOTIFY，兼容精确匹配的订阅响应，继续向IOPMPowerSource发布真实状态；充电显示待实机确认。
- services84按Nothing协议使用USB\_ADAP\_TYPE=7识别源，并按最大电流/输入限值描述适配器；不改固件充电控制。
- services86同轮fresh快照、真实VBUS存在判断、两轮source确认和5秒刷新，充电控制仍归固件。
- services112 REC: ADSP stage9 failed at whole-carveout CPU mapping, leaving battery/audio unavailable. services113 loads bounded physical slices with original Pong PAS/MDT inputs; device result pending.

### Completion criteria

- 在设备上观察该接口的实际工作结果并保存对应日志

### Current limits

- 动态充电图标、充放电和插拔更新仍需设备观察。

### Next action

- 读取本轮启动日志并继续完成板级接口

### Evidence

- `source`: [services126 logs external VBUS through charging/FULL; services127 separates completed-cycle charger validity and retains real state across timeout/debounce; actual UI state after temporary boot pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services127-native-audio-rootful.md)
- `source`: [services109 REC: ADSP stage9 ENOMEM removed physical audio/battery sources, SBRenderer Neutrino abort follows refused Metal connection, keyboard list persisted but not shown. services110 early PAS/bounce allocation, 10 isolated GPU client scopes and native TextInput refresh compiled; device effects unverified. Timed restart stays off.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services110-adsp-poster-textinput.md)
- `source`: [services107 timed REC complete: native InterfaceNamer timeout completion unblocks wifid manager and SpringBoard; real device count1, 29 scanned BSS, first visible frame and continuing swaps. Native audio UID preference and PowerUI retained; Settings association, PCM route and audible output remain unconfirmed.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services107-interface-namer-handshake.md)
- `source`: [services103: ADSP ready/channel up, actual battery 100% 4428mV republished, QCA6490 en0 scanned 10 BSS after 64MiB DMA fix. Native Wi-Fi manager still timed out; no audio StartIO or confirmed VAD route. services104 runtime corrections pending device evidence.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services104-system-peripheral-order.md)
- `source`: [共享资源与启动调用已实际链接，未进行设备运行。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services74-source-audit.md)
- `source`: [按官方四份文档核对传输、服务和Darwin24接口，实际修补已完整编译，设备结果待确认。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services83-official-peripherals.md)
- `source`: [本轮板级接口、按键去抖、音频插件和显示资源复用已完整编译，实际功能效果待设备反馈。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services84-peripheral-interfaces.md)
- `source`: [services92 completed timed REC capture after 72 MiB OS update. User confirms brightness adjustment works; native IOHID report device now opens. Wi-Fi remains unavailable to user, no association or PCM StartIO observed; no BV/OOM error in this capture. Source repairs and remaining interface faults recorded separately.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services92-peripherals-latency.md)

## Image assembly {#packaging}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- UniXNU c96b299（release 与 templates/package.sh）、uefi-pong 固件树、匹配 22H374 restore、UNIXNU\_UNIQUE\_CHIP\_ID 平台种子

### Configuration

- board.toml 的 \[package\]/\[package.defconfig\]/\[bootimg\]/\[userdata\]，os-profiles/ipados-18.7.10-22H374，configs/pong\_ipados18\_ci\_defconfig

### Procedure

- scripts/package.sh --check 走 deps/preflight/patches；CI 的 package job 跑 scripts/package.sh --os … --skip-prelink，再跑 scripts/finalize-pong-adt.py：用本地同一份 make-pong-adt-ipados18.py 与同一组参数（12 GiB DRAM、4 GiB 窗口、单 CPU）重写 payload 里的 ADT，并重打 boot.img 与 PONGFAT1 包装的 boot.img.pong。

### Development findings

- scripts/package.sh --check --no-deps 在 Linux 上通过：1 个补丁、pong\_ipados18\_defconfig、OS ipados-18.7.10-22H374。release 只跑 kernel/package/firmware/payload，不含 userdata；本板内核需要 MACHINE\_CONFIGS=PONG，共享 kernel 步骤写死 BCM2837，因此由 kits/PongPlatform24 作为组件 recipe 编译；共享 kernel 步骤的 tree 已有真实 drivers/ 目录，设备 builder 另用一棵树并在编完后回填 mach.development.pong。bootimg 的 validate 只认 v0-v2 头，board 覆写 header\_version = 0。本板固件只认 PONGFAT1 包装的 ramdisk，故规范产物 boot/boot.img 之外另出 boot.img.pong。userdata 不走 unixnu userdata：它写 SHNGROOT v2 且缺 Data 窗口，本板 RootLayout.h 只接受 v1 且强制 OS/SystemOS/Data 三窗口。

### Completion criteria

- 在 macOS runner 上跑通 package.yml 两个 job，并取得 boot.img、boot.img.pong、payload.img、kernel.macho、package.manifest.json 与 userdata 分片

### Current limits

- CI 尚未在 macOS runner 上运行；真机未刷入。prelink slide 尚未在本板表达，流水线用 --skip-prelink。devicetree.generate\(\) 要求单段 /memory，自定义 DT 属性不透传。

### Next action

- 在 fork 上手动触发 package.yml，带 ipsw\_url，核对两处产物再上真机

### Evidence

- `source`: [board.toml、os-profiles 与 PongPlatform24 kit 已按 docs/porting/packaging.md 组织；package.sh --check 通过，CI 未跑。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/format2/README.zh.md)

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

- 已读取services81 REC console及Data中的Sileo/音频诊断，按具体错误修补。
- services82保留内核启动日志，减少launchd额外活动日志，并限制没有实际蓝牙传输层的反复拉起。
- services86已提取REC console和对应IPS，区分显示主故障与后续进程退出；可选softwareupdated重复SIGSEGV已设置停用。

### Completion criteria

- 在设备上观察该接口的实际工作结果并保存对应日志

### Current limits

- 没有运行测试、性能基准、镜像哈希或镜像回读比较。

### Next action

- 读取本轮启动日志并继续完成板级接口

### Evidence

- `source`: [services142 native lockdownd matches actual Pong Mux service with real IsActive/configuration interest events; same actual board-derived software identity used by descriptor and native service. Native trust/TLS retained; Finder pairing unconfirmed.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services142-wake-usb-audio.md)
- `source`: [services141 Mac automatically configured iPhone05ac:12a8 at480Mbps with CDC. Real native QueryType returned com.apple.mobile.lockdown; GetValue returned iPhone17,1/iPhone/18.7.10/22H374. Pairing unconfirmed; native UID remains all-f placeholder and protected identity GetProhibited.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services141-native-usb-pcm.md)
- `source`: [services140 auto-enumerates iPhone config1/480Mbps with CDC, but QueryType times out. services141 adapts exact22H374 optional CESM startup and preserves native pairing/TLS; device outcome pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services141-native-usb-pcm.md)
- `source`: [services139 automatic Mac Apple/iPhone05ac12a8 configuration1 at480Mbps and CDC logging confirmed; explicit CDC fastboot returned the phone to Fastboot. Native62078 accepted real request bytes but did not reply. services140 compiled explicit native lockdownd root context and audio media-format length/hard-mute handling; actual sound remains unconfirmed.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services140-native-lockdown-audio-volume.md)
- `source`: [services138 actual Apple/iPhone05ac12a8 High-Speed enumeration and retained CDC observed after manual host configuration; native62078 QueryType timed out. services139 compiled native PreferredConfig response, DWC3 EP0 stall fix and root-only in-kernel loopback socket backing. Native trust/TLS and all unrelated working features retained; actual139 result pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services139-usb-native-configuration.md)
- `source`: [services136 physical CDC captured454884bytes. macOS usbmuxd claimed the real Mux interface and VERSION2 negotiated, then frame parsing failed. Explicit CDC reboot rec accepted, synced reset marker committed, actual ADB REC returned and1254275bytes pstore captured. Automatic restart remains off. services137 adapts native directional v2 magic and v1 VERSION framing.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services137-native-mux-speaker-sd1.md)
- `source`: [services135 real USB CDC enumerates as Pong XNU console and cu.usbmodemPONG\_SM84751; received108518 bytes of real console in12s without REC. Live log confirms GPU scanout completions and25 completed actual buffers. Codec/audible output not yet observed. Apple Mux remains unimplemented; phone left running.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services135-codecs-usb-global-metal.md)
- `source`: [services135 final matching OS 9663676416 bytes installed complete, pending cleared, Data/SystemOS retained. Temporary boot Sending2.424s / Booting10.178s OKAY, no permanent boot write. Codec rule precedes ElleKit refresh. Actual new audio/USB/GPU effects unconfirmed; automatic restart remains off.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services135-codecs-usb-global-metal.md)
- `source`: [services134 real NXP/eUSB2 and DWC3 running confirmed, but no host configuration. services135 adds PMIC BmUsbOnline-driven Qualcomm QSCRATCH session and actual RUN\_STOP lifecycle, preserving disjoint USB DMA/SID0/root-ready. Compiled; CDC/Apple Mux not claimed working. Automatic restart off.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services135-codecs-usb-global-metal.md)
- `source`: [services134 matching HAL OS installation completed, 9663676416 bytes; Data/SystemOS retained. Fastboot temporary boot Sending 2.320s / Booting 5.023s OKAY. Device left running, auto reboot off. Audible output and USB enumeration not confirmed by the boot command.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services134-speaker-usb-qup.md)
- `source`: [services133 USB fails before repeater access: QUP clock idle 0x80000002 is legal HWCG, confirmed in live REC. services134 fixes readiness and restores Pong GPIO206/207 plus actual DFS timing; compiled with independent USB DMA and quiesced firmware handoff retained. CDC enumeration unconfirmed; Apple Mux remains unimplemented. Automatic reboot off.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services134-speaker-usb-qup.md)
- `source`: [services132 console/pmsg captured in REC. USB firmware StopController stage2 status0, flags2; actual frame and PCM completions recorded. Automatic reboot remains off.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services133-parity-audio-usb.md)
- `source`: [services132 loader allocates independent reserved USB DMA and attempts standard USB Function StopController with actual status recorded. It does not certify PHY/repeater retention, so MMIO remains guarded; no claim of CDC or Apple Mux enumeration.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services132-wake-usb-ownership.md)
- `source`: [services130 REC confirms OS/SystemOS/Data mount and init before stopping immediately after USB takeover begins. services131 requires real independent USB DMA and quiesced-controller handoff before any MMIO; current loader lacks these records, so hardware takeover is skipped. USB is not working yet; boot recovery pending device observation.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services131-usb-conflict-isolation.md)
- `source`: [services129 console/pmsg captured \(8990 bytes\), no panic or audio init reached. services130 fixes optional USB/root-storage SMMU concurrency and bounds root-ready wait in USB worker; automatic reboot stays disabled.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services130-root-smmu-order.md)
- `source`: [services129 fixes USB runtime low32 contiguous allocation failure with disjoint UEFI-reserved 32KiB audio / 32KiB DWC3 partitions, preserving exclusive SID0. CDC enumeration and Apple Mux remain unconfirmed / incomplete.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services129-prm-usb-dma.md)
- `source`: [services114、115、116 均由临时启动后定时同步重启自动返回 REC；取得匹配本轮 ID 的 console/pmsg 和 reset-commit 标记。已有独立强制复位期限；完全硬件/调度器失效仍不由软件计时器保证。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services116-runtime-adapters.md)
- `source`: [审计结论与硬件结果分开记录，没有运行测试或镜像校验。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services74-source-audit.md)
- `source`: [基于services81日志的板级与运行时实际修补已完整编译；设备效果待确认。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services82-runtime-performance.md)
- `source`: [已按真实backboardd IPS修复22H374背光默认映射初始化，并在真实UFS根卷补齐标准匹配属性；完整内核和运行时已编译，界面恢复待设备反馈。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services85-backlight-startup.md)
- `source`: [services91 timed return: native filesystem sync, matching console/pmsg boot ID and reset commit marker; automatic REC pull completed. RESET2 unsupported, standard SYSTEM\_RESET succeeded. A total scheduler hard hang remains outside software timer coverage.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services91-autocapture-wifi.md)
- `source`: [services94: 72 MiB OS update and temporary boot completed; timed REC captured. QCA6490 registered en0 and scanned 19 BSS with Pong firmware; Settings/association remain unconfirmed. Native HID and physical audio ASPL registered; no button press or PCM StartIO in this capture. Brightness repair retained.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services94-native-volume-wlan.md)
- `source`: [services94 REC shows AppleUserHIDEventDriver waiting about 120 seconds before kernel HID fallback. services95 adds an exact Pong SPMI volume-key personality without IOMatchDefer, retaining native Consumer reports and stock HID rules. Prelink boot image built from the completed Darwin24 kernel; device result pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services95-hid-driverkit-wait.md)

## mobilegestalt-device-information {#mobilegestalt-device-information}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- 22H374 native lockdownd call sites
- actual Pong IOPMPowerSource and Speaker IOAudio2Device

### Configuration

- root-owned Pong board identity seed; existing native USB pairing retained

### Procedure

- Scoped USB model presentation; fresh measured power/audio capability answers; native DiskUsage Data uses actual statfs SInt64

### Development findings

- services142 Finder recognition and native pairing/session succeeded. Old disk\_usage contained negative free capacity and wrapped Data capacity.

### Completion criteria

- Read real paired USB information and actual driver state after boot

### Current limits

- No synthetic IMEI, activation, Apple fuse identity or audio calibration. Actual audible output and wake require device observation.

### Next action

- Preserve native pairing and expanded Data; continue native audio volume repair

### Evidence

- `source`: [services144 native paired queries confirm disk128000000000, Data127790243840 and available125038678016 bytes; user hears a quiet lock sound. Media sound remains unresolved.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services144-data128-components-audio.md)
- `source`: [Live 8GiB Data preserved with UUID; APFS expanded to 127790243840 bytes and installed in an independent 128000000000-byte SHNGROOT window at40GiB. Original Data/OS/SystemOS retained. New native boot/capacity query pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services144-data128-components-audio.md)
- `source`: [Native22H374 make\_level\_map traverses all16 ranges; mapping retained. Bounded real audio tail drain and old-running-state invalidation compiled. Synthetic PONG component identifiers and real Data media capacity runtime staged; no factory database alteration.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services144-data128-components-audio.md)
- `source`: [MobileGestalt adapter and static init compiled; existing services142 kernel/Metal retained. Device effects pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services143-mobilegestalt-device-information.md)

## native-category-volume {#native-category-volume}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- 22H374 AVSystemController and CoreAudio native control ABI
- services144 user audible lock sound and actual integer volume1

### Configuration

- One-time native media/ringer low-volume migration; retain full mute and subsequent user volume choices

### Procedure

- Run outside SpringBoard main/dyld callbacks, validate method ABI, require real native readback

### Development findings

- Native selector2 scalar order matches driver. The actual endpoint is not muted but runs at1/16 gain.

### Completion criteria

- Native category readback plus audible media and system playback

### Current limits

- No analog gain/protection/calibration changes, no external competing HAL

### Next action

- Temporarily boot services146 with modest digital gain and higher native volume defaults

### Evidence

- `source`: [Matched curve/runtime compiled; 78 native ringtones present, persistent synthetic component metadata22/17/17/21 saved. Fresh guest OS baseline captured and40MiB changed-band update prepared; no image hashes/comparison.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services146-volume-ringtones-incremental.md)
- `source`: [Native media0.6473/ringer0.2974, physical control1/mute0; user confirms normal but quiet sound. Native pairing/session retained.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services145-native-category-volume.md)
- `source`: [Signed4KiB iPhoneOS runtime compiled; existing services144 kernel, USB pairing and128GB Data retained. Native volume restoration pending device result.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services145-native-category-volume.md)

## native-ringtone-display-wake {#native-ringtone-display-wake}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- services146 native volume preferences and real PCM/DSP completions
- services146 wake scanout not-submitted and surface timeout logs

### Configuration

- Serialized bounded IOAudio2 restart; native ringtone config; CPU/GPU opaque scanout; existing128GB Data/pairing retained

### Procedure

- Compile complete matching kernel/runtime and install only changed OS bands

### Development findings

- Ringer native volume0.6763 is nonzero; missing sound not resolved by another global gain boost. Existing78 ringtone resources retained.
- CPU scanout copied source alpha while GPU supplied opaque alpha; idle optional import retention and start/stop Busy window corrected.

### Completion criteria

- Native ringtone selection/decoder and repeated sleep/wake actual audio/display observations

### Current limits

- No synthetic DSP/GPU completions, analog gain or factory protection changes

### Next action

- Temporarily boot services147 and read native ringtone/USB/display state

### Evidence

- `source`: [Darwin24 kernel and native UI/codec/Metal frontend compiled. Expanded bounded injection configuration matches init and tweak-refresh. Device effect pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services147-ringtone-wake.md)

## main-gpu-metal-ringer149 {#main-gpu-metal-ringer149}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- core6790e7c, AdrenoMetal a0f0287, Adreno740 a9a2cbb
- actual22H374 SBRingerControl method ABI and148 logs

### Configuration

- A730/SM8475 ABI1 and22H374 kept; diagnostics opt-in

### Procedure

- Native ringer full selector; &lt;=128KiB optional contig/backoff, advisory unlocked fence polls, async runtime room keeper and pressure release

### Development findings

- 148 default ringtone file resolves; objc\_direct short setter/getter prevented native ringer adaptation.

### Completion criteria

- Native ringer request and audible ringtone; post-update UI GPU/Metal operation

### Current limits

- A740-specific CP two-ring preemption, ABI2 address-space switching and Darwin26 offsets not applied to SM8475/22H374

### Next action

- Inspect services149 native ringtone request and real post-update GPU/Metal boot logs

### Evidence

- `source`: [Core fast-forward completed with local Pong overrides preserved. Matching Darwin24 kernel, native ringer runtime, Rust Metal bridge and plugin compiled. Installed64MiB changed OS bands; temporary boot Sending2.335s/Booting10.179s OKAY. Device sound/GPU effect pending runtime logs.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services149-ringer-main-gpu.md)

## adreno-ringer-freeze150 {#adreno-ringer-freeze150}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- services149 REC CP opcode cause1/device-lost/backboardd crash
- native ringer accepted cached mute false, ringtone scalar0.6763
- Adreno740 main a9a2cbb/36c4e44 and Qualcomm KGSL ring allocation

### Configuration

- Pong SM8475/A730, 22H374 arm64/native4KiB; board.toml and pong\_ipados18\_defconfig; matching per-round kernel/runtime recipes documented in the evidence reference.

### Procedure

- Object-indexed ABI1 VM, CP\_NOP ring wrap padding, bounded background pipeline creation, per-process native mute reconciliation, qualified native software decoder selection

### Development findings

- Matching kernel, UI, init, independent codec and Metal bridge compiled; deployment in progress.

### Completion criteria

- Ringtone audible and actual frame completion without CP faults after interaction

### Current limits

- No fake GPU completions or borrowed A740 firmware/ABI2; hardware result needs device runtime

### Next action

- Install only changed OS bands and temporarily boot matching150 kernel/runtime

### Evidence

- `source`: [Matching kernel, UI, init, independent codec and Metal bridge compiled; deployment in progress.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services150-adreno-freeze-ringer.md)

## control-center-native-ringtone151 {#control-center-native-ringtone151}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- 150 live USB log: compressed MTLReplayer shader page-in failure and backboardd SIGBUS
- 150 live USB log: scalar DisplayBrightness consumed by CBSliderCommitTelemetry as dictionary; cache slide resolved from actual objc export
- Native ringer request accepted, actual DSP PCM and TFA state

### Configuration

- Pong SM8475/A730, 22H374 arm64/native4KiB; board.toml and pong\_ipados18\_defconfig; matching per-round kernel/runtime recipes documented in the evidence reference.

### Procedure

- Qualified telemetry-only omission; bounded small UI warmup; bounded idle memory reuse; native M4R catalog audio transcoding to software ALAC

### Development findings

- 78 native M4R ringtone tracks transcoded to ALAC; UI telemetry adaptation, Metal plugin and matching bounded-memory Rust bridge compiled. Device deployment pending.

### Completion criteria

- Audible native ringtone and stable control-center interactions

### Current limits

- Hardware results cannot be inferred from compilation or nonzero PCM; real native GPU and audio errors preserved

### Next action

- Install changed151 system bands and temporarily boot; inspect real USB/display/audio evidence

### Evidence

- `source`: [78 native M4R ringtone tracks transcoded to ALAC; UI telemetry adaptation, Metal plugin and matching bounded-memory Rust bridge compiled. Device deployment pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services151-ringtone-control-center.md)

## upstream-metal-keyboard152 {#upstream-metal-keyboard152}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- UniXNU6790e7c/Adreno740a9a2cbb/AdrenoMetal831a9dc/Sheng28b3028
- 151 real backboardd SIGSEGV: null device after unchecked constant-stream reservation
- Native keyboard resources and user-reported phone keyplane offset/123 failure

### Configuration

- Pong SM8475/A730, 22H374 arm64/native4KiB; board.toml and pong\_ipados18\_defconfig; matching per-round kernel/runtime recipes documented in the evidence reference.

### Procedure

- Conservative owned-page index, disjoint larger UI VA windows, bounded retired BO cache, checked Vulkan draw errors, A730 MPS count, independent InputUI phone idiom

### Development findings

- Darwin24 kernel, boot, Turnip, Metal frontend/plugin, UI and init compiled; boot command967bytes. No tests, benchmarks or image verification. Device outcome pending.

### Completion criteria

- Stable real GPU composition and native keyboard123 transitions after interaction

### Current limits

- A740 preemption/ABI2/coherence/Darwin26 offsets not claimed; no synthetic GPU success

### Next action

- Install changed OS bands and temporarily boot matching152 kernel/runtime

### Evidence

- `source`: [Darwin24 kernel, boot, Turnip, Metal frontend/plugin, UI and init compiled; boot command967bytes. No tests, benchmarks or image verification. Device outcome pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services152-upstream-metal-keyboard.md)

## gpu-guide-memory-bgra153 {#gpu-guide-memory-bgra153}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- Official GPU adaptation guide
- 152 moving color-region report
- 152 actual GPU scanout and presentation timings

### Configuration

- Pong SM8475/A730, 22H374 arm64/native4KiB; board.toml and pong\_ipados18\_defconfig; matching per-round kernel/runtime recipes documented in the evidence reference.

### Procedure

- System pageable WC BOs and same-descriptor CPU maps; prepare outside shared gate; no global drain on new maps; scoped actual-job free drain
- GPU sysmem BGRA default and official GMEM resolve/load/store/input-attachment swap corrections
- Retain main firmware/ABI/fence/TLBI ownership and152 native keyboard path

### Development findings

- Matching Darwin24 kernel, Turnip GMEM paths and153 Metal frontend/plugin compiled; native4K signatures; boot command965bytes. No tests, benchmarks or image verification.

### Completion criteria

- Real device colors, sustained frame progress and native keyboard interaction

### Current limits

- No A740 firmware/ASID/preemption substitution or fake fences; no claim of measured120fps

### Next action

- Install changed OS bands and temporarily boot matched153 kernel/runtime

### Evidence

- `source`: [Matching Darwin24 kernel, Turnip GMEM paths and153 Metal frontend/plugin compiled; native4K signatures; boot command965bytes. No tests, benchmarks or image verification.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services153-gpu-guide-memory-bgra.md)

## gpu-real-execution-hotpath155 {#gpu-real-execution-hotpath155}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- 153 actual first-IB opcode fault
- 154 real908/908 GPU completion with continued user-reported slow UI
- official GPU guide and actual compiled Turnip backend

### Configuration

- Pong SM8475/A730, 22H374 arm64/native4KiB; board.toml and pong\_ipados18\_defconfig; matching per-round kernel/runtime recipes documented in the evidence reference.

### Procedure

- Initial Darwin24 aperture cache handoff, same WC VM descriptor, outside-gate free, indexed client publication and actual uncached imports
- Restore missing negotiated128IB batch transport in actual Mesa

### Development findings

- 155 actual GPU scanout and827/827 completions; no CP fault in captured boot. User still reports slow UI; not a performance success claim.

### Completion criteria

- Sustained real GPU execution and improved interactive frame delivery

### Current limits

- A730/ABI1 kept; no fake fences, A740 preemption or all-feature claims

### Next action

- Retain functional155 kernel while deploying156 runtime/UI-stall fixes

### Evidence

- `source`: [155 actual GPU scanout and827/827 completions; no CP fault in captured boot. User still reports slow UI; not a performance success claim.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services155-gpu-hot-path-and-priming.md)

## metal-interface-ui-stalls156 {#metal-interface-ui-stalls156}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- 155 slow UI with working GPU
- Native prime journal:184 paths, only1 eligible library
- Native cameracaptured jetsam at27MiB/5s respawn

### Configuration

- Pong SM8475/A730, 22H374 arm64/native4KiB; board.toml and pong\_ipados18\_defconfig; matching per-round kernel/runtime recipes documented in the evidence reference.

### Procedure

- Actual asynchronous pipeline/function creation and user-interactive frontend completion
- Runtime heap size/alignment, compute descriptor entries, family-backed legacy queries and declared constant warmup
- Host expansion of141 real framework shader assets; bounded192MiB camera service policy

### Development findings

- Optimized Rust/front-end/plugin built; only624MiB changed OS bands installed. Fastboot Sending2.328s/Booting10.175s OKAY; device observation pending.

### Completion criteria

- Real GPU remains connected; native services stable; warm shader cache and interactive frame progress

### Current limits

- Unknown private capabilities remain unadvertised; no blanket Apple family spoofing; not all Metal features are implemented

### Next action

- Observe156 GPU completions, warmup and native service exits after temporary boot

### Evidence

- `source`: [Optimized Rust/front-end/plugin built; only624MiB changed OS bands installed. Fastboot Sending2.328s/Booting10.175s OKAY; device observation pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services156-metal-entrypoints-and-ui-stalls.md)

## gpu-priority-timing160 {#gpu-priority-timing160}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- official GPU guide
- 159 real GPU completion with24-30ms frontend/8-12ms wait and user low-FPS report

### Configuration

- Pong SM8475/A730, 22H374 arm64/native4KiB; board.toml and pong\_ipados18\_defconfig; matching per-round kernel/runtime recipes documented in the evidence reference.

### Procedure

- Pong DT max900MHz/DDR11 request with existing GMU ACK
- Real ABI1 method18 priority using Darwin24 task policy
- Single-ring1/2/8 process admission, preserve FIFO/fences
- Actual CP timestamp and bounded cache/queue/execution/retirement logs

### Development findings

- Darwin24 kernel, Metal frontend and Turnip linked;80MiB changed OS bands installed; temporary Fastboot boot succeeded. Device timing pending.

### Completion criteria

- Real native GPU frames and slower-stage identification followed by concrete fixes

### Current limits

- No A740 dual-ring/preemption claim
- HFI vote is not physical clock measurement
- No blanket cache-maintenance skip

### Next action

- Capture160 slow-frame evidence and fix dominant latency

### Evidence

- `source`: [Darwin24 kernel, Metal frontend and Turnip linked;80MiB changed OS bands installed; temporary Fastboot boot succeeded. Device timing pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services160-gpu-clock-priority-timeline.md)

## audio-wake-active-acquire162 {#audio-wake-active-acquire162}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- User161 sleep/unlock still silent
- 161 actual GPU complete with remaining10-23ms imported completion cache work
- Nothing native TFA9873 B0 state definitions and shutdown order
- Official GPU timing and ownership guide

### Configuration

- Pong SM8475/A730, 22H374 arm64/native4KiB; board.toml and pong\_ipados18\_defconfig; matching per-round kernel/runtime recipes documented in the evidence reference.

### Procedure

- Resume actual output stream for retained or new HAL clients on running engine
- Power down amps with live source clock before APM/MI2S shutdown; restore volatile TDM route on real start
- Separate negotiated active-import acquire after genuine Metal completion and before CPU/display release

### Development findings

- Substantive HAL stream-resume, TFA clock/stop order and real-completion ownership changes; device result pending.

### Completion criteria

- Audible playback after sleep/unlock
- Real GPU frames without cache faults and reduced completion overhead

### Current limits

- No fabricated hardware success
- Unparticipating imports keep conservative kernel acquire
- No global IOSurface cache changes or factory amplifier gain modifications

### Next action

- Temporary boot162 and capture ordinary GPU/audio startup and wake status

### Evidence

- `source`: [Substantive HAL stream-resume, TFA clock/stop order and real-completion ownership changes; device result pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services162-sleep-audio-active-acquire.md)

## audio-prepare-command-stages163 {#audio-prepare-command-stages163}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- services162 user-confirmed unlock silence
- real PCM/WRITE\_DONE/amp engagement
- poster scheduled waits406ms
- official GPU stage guide

### Configuration

- Pong SM8475/A730, 22H374 arm64/native4KiB; board.toml and pong\_ipados18\_defconfig; matching per-round kernel/runtime recipes documented in the evidence reference.

### Procedure

- Restore AudioReach endpoint/converter/shmem media before prepare
- 5s real silent-DMA warm hold and full native first-period consumption
- Honor requested command queue capacity
- Only omit duplicate VA flush after complete-import physical sync
- Capture actual runtime phases with bounded ring

### Development findings

- Matched kernel/Rust/ObjC compiled;56MiB OS changed bands installed; Fastboot Sending2.331s/Booting10.174s OKAY; native USB auto-configured. Audible wake recovery still requires device observation.

### Completion criteria

- Audible playback after screen sleep and unlock
- Identify and reduce dominant real frame stage

### Current limits

- No calibration/protection gain changes
- No dropped commands or fake GPU completion
- Noncovered imports keep conservative maintenance

### Next action

- Read163 device timing and audio recovery evidence

### Evidence

- `source`: [Matched kernel/Rust/ObjC compiled;56MiB OS changed bands installed; Fastboot Sending2.331s/Booting10.174s OKAY; native USB auto-configured. Audible wake recovery still requires device observation.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services163-audio-prepare-command-stages.md)

## lock-sound-admission164 {#lock-sound-admission164}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- 163 runtime scheduled backlog434ms
- 163 real restart/PCM/WRITE\_DONE but audible unlock recovery not confirmed
- native short-sound StopIO ownership audit

### Configuration

- Pong SM8475/A730, 22H374 arm64/native4KiB; board.toml and pong\_ipados18\_defconfig; matching per-round kernel/runtime recipes documented in the evidence reference.

### Procedure

- Serialize retained StartIO with last StopIO
- Per-client start/stop ownership lock with real client/user logs
- Drain frozen committed HAL tail up to400ms before physical stop
- Remove only genuinely observed completed admission fences

### Development findings

- Darwin24 kernel and matched Turnip compiled;48MiB OS changed bands installed; Fastboot Sending2.332s/Booting10.177s OKAY. Native audio client/tail and GPU stage capture pending.

### Completion criteria

- Actual audible wake and short sounds
- Reduced Busy retries and submission backlog without lost GPU work

### Current limits

- No lock-sound removal
- No fabricated PCM/fences
- Bounded drain keeps actual mappings until stop returns

### Next action

- Build and temporarily boot164; capture native client/PCM and GPU phase logs

### Evidence

- `source`: [Darwin24 kernel and matched Turnip compiled;48MiB OS changed bands installed; Fastboot Sending2.332s/Booting10.177s OKAY. Native audio client/tail and GPU stage capture pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services164-lock-sound-admission.md)

## scheduling-metal-audio-clock165 {#scheduling-metal-audio-clock165}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- upstream fix/gpu-scheduling-and-metal d6bd3dd complete core merge
- 164 poster scheduler2.3s vs CP8.7-14.5ms
- native audio PCM/DSP/TFA normal-looking but unlock silence confirmed

### Configuration

- Pong SM8475/A730, 22H374 arm64/native4KiB; board.toml and pong\_ipados18\_defconfig; matching per-round kernel/runtime recipes documented in the evidence reference.

### Procedure

- Adapt full generic Metal/compiler/cache delta to22H374
- Enable actual Mesa shader-cache and live priority lowering
- Batch physical cache maintenance across fragmented spans
- Restore independent native audio clock adaptation
- Only changed96MiB/12OSbands installed; temporary boot

### Development findings

- Darwin24/Rust/Metal/Turnip/codec builds complete;96MiB changed-band installation; Fastboot Sending2.333s/Booting10.172s OKAY; actual device results pending.

### Completion criteria

- Real GPU frames and lower scheduler/cache time
- Audible lock/unlock recovery; actual clock observation

### Current limits

- A730 remains single-ring admission; A740 two-ring source present in core but not falsely enabled
- No fake fences or cache-coherence shortcuts
- Existing user build scripts preserved
- Data128GB and pairing preserved

### Next action

- Capture native CoreAudio actual frequency and genuine GPU submissions/slow phases

### Evidence

- `source`: [Darwin24/Rust/Metal/Turnip/codec builds complete;96MiB changed-band installation; Fastboot Sending2.333s/Booting10.172s OKAY; actual device results pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services165-scheduling-metal-audio-clock.md)

## submit-retirement-publication166 {#submit-retirement-publication166}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- 165-final real nested-IB FSR80000402/FAR0xe0d4100
- kernel-accepted submit precedes user last\_fence publication
- BO retirement/cache reuse samples last\_fence concurrently

### Configuration

- Pong SM8475/A730, 22H374 arm64/native4KiB; board.toml and pong\_ipados18\_defconfig; matching per-round kernel/runtime recipes documented in the evidence reference.

### Procedure

- Serialize actual submission/fence publication with retirement snapshots
- Keep Busy waits outside mutex
- Retain shader cache, single-sample resolve and page batching
- Keep165-final actual native audio clock/conversions

### Development findings

- Final166 rebuilt matchedDarwin24/Rust/Metal/Turnip after latest135b0da merge;112MiB changedOS bands installed; actual9216submits without capturedCP/SMMU fault; frame traces reveal CPU handoff overhead.

### Completion criteria

- Sustained real GPU submissions without SMMU fault
- Audible lock/unlock recovery remains separate observation

### Current limits

- No false fault recovery or fake fences
- A730 ABI1/actual firmware unchanged
- Data128GB and native USB pairing preserved

### Next action

- Install matching changed Turnip bands and temporary boot166

### Evidence

- `source`: [Final166 rebuilt matchedDarwin24/Rust/Metal/Turnip after latest135b0da merge;112MiB changedOS bands installed; actual9216submits without capturedCP/SMMU fault; frame traces reveal CPU handoff overhead.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services166-submit-retirement-publication.md)

## frame-ownership-pac167 {#frame-ownership-pac167}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- official GPU,diagnostics and arm64e documents
- core135b0da includes latest main04573c5
- 166 native60/180/300s frame links
- backboardd35.890ms command with actual4.617ms CP execution

### Configuration

- Pong SM8475/A730, 22H374 arm64/native4KiB; board.toml and pong\_ipados18\_defconfig; matching per-round kernel/runtime recipes documented in the evidence reference.

### Procedure

- Batch up to64 real retained host-import ownership ranges in one gate/table pass
- Preserve full cache operations and exact coverage before omitting duplicate VA flush
- Record actual synchronization phases and useO3 frontend
- Port upstream nativePAC key source to conditional Darwin24 path
- Read PAC feature registers on every enabledCPU without enabling an unqualified architecture

### Development findings

- Darwin24 kernel,Turnip,O3 Metal frontend and matched plugin compiled;96MiB changed OS bands installed.
- Real scanout; no captured CP/SMMU error through5120submits.30216ranges became1793requests/473105us; typical handoff0.3-0.4ms, poster41-267ms backlog remains.8CPUs report address/genericPAC, key-access unprobed. Native audio clock corrected24MHz to19.2MHz; audible wake recovery unresolved.

### Completion criteria

- Actual reduced CPU handoff latency without GPU faults
- PerCPU PAC requirements recorded before anyarm64e enablement
- Audible wake recovery remains separate

### Current limits

- 22H374 remainsarm64; no claim of arm64e execution
- PAC key access and EL0/EL1 instruction roundtrip not qualified
- No cache skips,fake fences,benchmarks or image hashes
- 128GB Data and working board services preserved

### Next action

- Continue reducing measured poster inbox/admission/cache latency
- Qualify PAC key access and EL0/EL1 roundtrips before arm64e
- Confirm audible audio recovery after lock

### Evidence

- `source`: [Darwin24 kernel,Turnip,O3 Metal frontend and matched plugin compiled;96MiB changed OS bands installed.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services167-frame-ownership-and-pac.md)
- `source`: [Real scanout; no captured CP/SMMU error through5120submits.30216ranges became1793requests/473105us; typical handoff0.3-0.4ms, poster41-267ms backlog remains.8CPUs report address/genericPAC, key-access unprobed. Native audio clock corrected24MHz to19.2MHz; audible wake recovery unresolved.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services167-frame-ownership-and-pac.md)

## local-runtime-integration {#local-runtime-integration}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- Pong live Android DT、NothingOSS SM8475源码与匹配22H374 restore

### Configuration

- board.toml、pong\_ipados18\_defconfig 与对应板级配置

### Procedure

- Darwin24/XNU11417与22H374原始组件，格式2硬件输入与固定ABI。

### Development findings

- services85完整内核与匹配运行时已编译，96MiB OS更新已安装；Fastboot Sending/Booting均OKAY，Data/SystemOS保留。
- services113: official rootful Procursus/Sileo, genuine iphoneos-arm repository indices and mobile sileolists permissions staged; expanded writable OS and real package configuration required before qualifying installation.

### Completion criteria

- 在设备上观察该接口的实际工作结果并保存对应日志

### Current limits

- 新一轮外设及性能效果仍待设备反馈；构建脚本未修改。

### Next action

- 读取本轮启动日志并继续完成板级接口

### Evidence

- `source`: [services127 stages real arm64 rootful ElleKit libraries, native exec composition, maintainer integration and recovery switch; preserves device-generated actual package records, existing Sileo/root helper and DNS. Real tweak execution remains to be observed.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services127-native-audio-rootful.md)
- `source`: [services126 kernel/runtime compiled and full OS installed; Data/SystemOS retained. Temporary Fastboot Sending 2.319s / Booting 10.176s OKAY. Automatic reboot off; actual audio/package installation/performance unconfirmed; native USB backend remains unimplemented.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services126-audio-package-latency.md)
- `source`: [services125 rootful log: real root write/Sileo registration/configuration succeeds but repository DNS fails. services126 adds configd-selected conventional resolver bridge and bounded native name resolution, Data configuration marker and idempotent dpkg state; actual package install unconfirmed.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services126-audio-package-latency.md)
- `source`: [services116：rootful Sileo dpkg configure 完成，实际架构 iphoneos-arm，mobile LS proxy 有效且路径 /Applications/Sileo.app。真实 APT 索引保留；在线刷新报 DNS 解析失败。实际新包安装仍待证据。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services116-runtime-adapters.md)
- `source`: [首帧 SwapWait 零ID与原生轮询语义已修复；audiomxd stderr权限回归修复，576项服务缓存与独立plist一致。自动重启实现已删除，真机效果待观察。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services98-first-frame-launch-policy.md)
- `source`: [services97: native en0 SC service/arrival, exact preferences entitlements, real VirtualAudio UID defaults, authorized IOSurface GPU/CPU handoff and actual swap retirement compiled. Device effects remain unconfirmed; base build scripts and Data retained.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services97-native-endpoint-handoff.md)
- `source`: [services90内核与预链接打包完成，临时启动Sending 2.326s/Booting 6.828s均OKAY；OS/Data/永久boot未写入，八核调度和外设实际效果待确认。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services90-gpu-wlan-power-cpu.md)
- `source`: [最终原生内核无未解析符号，配套用户态保留在本机。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services74-source-audit.md)
- `source`: [Sileo/Procursus已暂存并签名；静态init已编译，独立本机Data候选与OS副本已更新，未启动手机。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/sileo.md)
- `source`: [基于services81日志的板级与运行时实际修补已完整编译；设备效果待确认。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services82-runtime-performance.md)
- `source`: [按官方四份文档核对传输、服务和Darwin24接口，实际修补已完整编译，设备结果待确认。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services83-official-peripherals.md)
- `source`: [本轮板级接口、按键去抖、音频插件和显示资源复用已完整编译，实际功能效果待设备反馈。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services84-peripheral-interfaces.md)
- `source`: [144MiB OS更新已安装；Fastboot Sending 2.316s、Booting 10.172s均OKAY，设备留在运行状态。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services84-peripheral-interfaces.md)
- `source`: [已按真实backboardd IPS修复22H374背光默认映射初始化，并在真实UFS根卷补齐标准匹配属性；完整内核和运行时已编译，界面恢复待设备反馈。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services85-backlight-startup.md)
- `source`: [96MiB OS写入完成；临时启动Sending 2.322s、Booting 10.127s均OKAY，桌面恢复待用户观察。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services85-backlight-startup.md)
- `source`: [显示单设备修正版编译完成，120MiB OS差量安装完成；services87 Sending/Booting均OKAY，设备留在运行状态，桌面恢复待确认。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services87-display-recovery.md)
- `source`: [services94 REC shows AppleUserHIDEventDriver waiting about 120 seconds before kernel HID fallback. services95 adds an exact Pong SPMI volume-key personality without IOMatchDefer, retaining native Consumer reports and stock HID rules. Prelink boot image built from the completed Darwin24 kernel; device result pending.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/services95-hid-driverkit-wait.md)

## cumulative-runtime-pr167 {#cumulative-runtime-pr167}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- Remote main aaa2d739 packaging and AppCryptex changes
- All accumulated local board/runtime repairs through167
- Pinned public Mesa and metal2vulkan sources

### Configuration

- Pong SM8475/A730, 22H374 arm64/native4KiB; board.toml and pong\_ipados18\_defconfig; matching per-round kernel/runtime recipes documented in the evidence reference.

### Procedure

- Preserve existing remote scripts and workflows
- Select required merged recipes in an output-only source overlay
- Prepare the complete compiled Mesa and translator source deltas
- Compile merged frontend, CPU/GPU objects and native userland helpers

### Development findings

- Merged native helper/UI/audio/sleep/Sileo/phone/route binaries, frontend,ArmCpu and changed GPU units compiled. Prepared Mesa source reproduces all25 changed source files; current device results remain separately recorded.

### Completion criteria

- Reviewable source-only pull request with cumulative WiFi,brightness,input,audio,battery,USB,storage,userland,GPU/Metal and conditional PAC changes

### Current limits

- No private binaries,firmware,restore images,Data or credentials
- Full hosted build and packaging pipeline not run
- Poster frame backlog and audible wake recovery still unresolved
- Running22H374 remainsarm64

### Next action

- Review and run the preserved hosted packaging workflow with required local inputs

### Evidence

- `source`: [Merged native helper/UI/audio/sleep/Sileo/phone/route binaries, frontend,ArmCpu and changed GPU units compiled. Prepared Mesa source reproduces all25 changed source files; current device results remain separately recorded.](https://github.com/Chengdong-Yu/UniXNU-pong/blob/941aa2de07615a55d487f8f93188ff751ea8436a/migration/ipados18/runtime-fixes-and-build-overlay.md)

</div>
