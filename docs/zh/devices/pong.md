# Nothing Phone \(2\)（pong）

[Chengdong-Yu/UniXNU-pong](https://github.com/Chengdong-Yu/UniXNU-pong)

<div v-pre>

Nothing Phone \(2\), iPadOS18 Darwin24 local format2 migration and board adaptation

源记录: [porting.toml](https://github.com/Chengdong-Yu/UniXNU-pong/blob/aaa2d739522ef98142fb83f6bf2ce7ad70e4a7a8/porting.toml), `aaa2d739522ef98142fb83f6bf2ce7ad70e4a7a8`.

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
| [网络](#network) | `implemented` |
| [音频](#audio) | `implemented` |
| [电源](#power) | `implemented` |
| [镜像组装](#packaging) | `implemented` |
| [诊断](#diagnostics) | `implemented` |

## 配置 {#configuration}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- Pong live Android DT、NothingOSS SM8475源码与匹配22H374 restore

### 配置

- board.toml、pong\_ipados18\_defconfig 与对应板级配置

### 操作步骤

- 选择 ARM64、SM8475、22H374 和 Pong 四层配置，数组完整列出。

### 开发经验

- 格式2解析、DTS编译、Darwin24内核及启动镜像构建成功；公开源固定版本已补齐。

### 完成条件

- 在设备上观察该接口的实际工作结果并保存对应日志

### 当前范围

- SM8475公共层与Pong聚合源码分目录固定；平台组件进一步拆分待完成。

### 下一步

- 读取本轮启动日志并继续完成板级接口

### 证据

- `source`: [格式2解析、DTS、内核和启动镜像已构建；services73未安装或启动。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/aaa2d739522ef98142fb83f6bf2ce7ad70e4a7a8/migration/ipados18/services73-smmu-audio.md)

## 固件与启动 {#firmware}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- Pong live Android DT、NothingOSS SM8475源码与匹配22H374 restore

### 配置

- board.toml、pong\_ipados18\_defconfig 与对应板级配置

### 操作步骤

- 复用 Pong UEFI，DarwinBoot24 接管真实可分配区间并使用 PSCI。

### 开发经验

- 现有设备可进入桌面，物理内存与可分配内存分别记录。

### 完成条件

- 在设备上观察该接口的实际工作结果并保存对应日志

### 当前范围

- 固件输入与UEFI源码在独立仓库。

### 下一步

- 读取本轮启动日志并继续完成板级接口

### 证据

- `source`: [现有设备可进入桌面，物理内存与可分配内存分别记录。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/aaa2d739522ef98142fb83f6bf2ce7ad70e4a7a8/migration/format2/README.zh.md)

## CPU 与中断 {#cpu}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- Pong live Android DT、NothingOSS SM8475源码与匹配22H374 restore

### 配置

- board.toml、pong\_ipados18\_defconfig 与对应板级配置

### 操作步骤

- 使用 0x000..0x700 affinity、GICv3 和 19.2 MHz timer。

### 开发经验

- CPU 4/3/1 拓扑保持 SM8475；受管内存沿用已启动实现。

### 完成条件

- 在设备上观察该接口的实际工作结果并保存对应日志

### 当前范围

- 没有声明新的多核稳定性测试结果。

### 下一步

- 读取本轮启动日志并继续完成板级接口

### 证据

- `source`: [CPU 4/3/1 拓扑保持 SM8475；受管内存沿用已启动实现。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/aaa2d739522ef98142fb83f6bf2ce7ad70e4a7a8/migration/format2/README.zh.md)

## 内存与 DMA {#memory}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- Pong live Android DT、NothingOSS SM8475源码与匹配22H374 restore

### 配置

- board.toml、pong\_ipados18\_defconfig 与对应板级配置

### 操作步骤

- 从实际不连续 DRAM 和保留区接管已取得所有权的 RAM。

### 开发经验

- 物理容量12GiB；此前受管容量9728MiB，不能将物理空洞分配给VM。

### 完成条件

- 在设备上观察该接口的实际工作结果并保存对应日志

### 当前范围

- 尚未接通全部物理内存。

### 下一步

- 读取本轮启动日志并继续完成板级接口

### 证据

- `source`: [物理容量12GiB；此前受管容量9728MiB，不能将物理空洞分配给VM。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/aaa2d739522ef98142fb83f6bf2ce7ad70e4a7a8/migration/format2/README.zh.md)

## 存储与根卷 {#storage}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- Pong live Android DT、NothingOSS SM8475源码与匹配22H374 restore

### 配置

- board.toml、pong\_ipados18\_defconfig 与对应板级配置

### 操作步骤

- 原生 UFS + 22H374 IOStorageFamily，独立 OS/SystemOS/Data 窗口。

### 开发经验

- 8GiB可写UFS Data已有启动记录；本轮只准备本机OS更新，未写入手机。

### 完成条件

- 在设备上观察该接口的实际工作结果并保存对应日志

### 当前范围

- 分区与镜像输入本地保存。

### 下一步

- 读取本轮启动日志并继续完成板级接口

### 证据

- `source`: [本机OS中init及音频策略已更新，设备仍保留services72。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/aaa2d739522ef98142fb83f6bf2ce7ad70e4a7a8/migration/ipados18/services73-smmu-audio.md)

## 显示 {#display}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- Pong live Android DT、NothingOSS SM8475源码与匹配22H374 restore

### 配置

- board.toml、pong\_ipados18\_defconfig 与对应板级配置

### 操作步骤

- Pong 1080x2412、stride4320；DCS背光和原有显示服务。

### 开发经验

- 桌面与壁纸已有显示；120Hz是请求值，不代表测得帧率。

### 完成条件

- 在设备上观察该接口的实际工作结果并保存对应日志

### 当前范围

- 实际高刷新率和背光仍需设备反馈。

### 下一步

- 读取本轮启动日志并继续完成板级接口

### 证据

- `source`: [桌面与壁纸已有显示；120Hz是请求值，不代表测得帧率。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/aaa2d739522ef98142fb83f6bf2ce7ad70e4a7a8/migration/format2/README.zh.md)

## 输入 {#input}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- Pong live Android DT、NothingOSS SM8475源码与匹配22H374 restore

### 配置

- board.toml、pong\_ipados18\_defconfig 与对应板级配置

### 操作步骤

- Goodix Berlin-D，PM8350实体按键转HID/原生音量控制。

### 开发经验

- services72真实音量press/release到达SBVolumeControl，电源down到达Consumer HID；本轮核对22H374事件接口，未新增虚构设备。

### 完成条件

- 在设备上观察该接口的实际工作结果并保存对应日志

### 当前范围

- 音量实际生效及独立电源按下/释放后的锁屏动作尚未确认。

### 下一步

- 读取本轮启动日志并继续完成板级接口

### 证据

- `source`: [services72已观察真实输入事件，系统动作仍需设备结果。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/aaa2d739522ef98142fb83f6bf2ce7ad70e4a7a8/migration/ipados18/services73-smmu-audio.md)

## GPU {#gpu}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- Pong live Android DT、NothingOSS SM8475源码与匹配22H374 restore

### 配置

- board.toml、pong\_ipados18\_defconfig 与对应板级配置

### 操作步骤

- SM8475 A730、实际固件、SMMU、Turnip与22H374 Metal ABI。

### 开发经验

- 已有桌面硬件渲染记录，保留此前高RAM BO和copy分配修补。

### 完成条件

- 在设备上观察该接口的实际工作结果并保存对应日志

### 当前范围

- 复杂壁纸和长时间稳定性没有新增结论。

### 下一步

- 读取本轮启动日志并继续完成板级接口

### 证据

- `source`: [已有桌面硬件渲染记录，保留此前高RAM BO和copy分配修补。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/aaa2d739522ef98142fb83f6bf2ce7ad70e4a7a8/migration/format2/README.zh.md)

## 网络 {#network}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- Pong live Android DT、NothingOSS SM8475源码与匹配22H374 restore

### 配置

- board.toml、pong\_ipados18\_defconfig 与对应板级配置

### 操作步骤

- Pong PCIe0/QCA6490，82项PHY序列、GPIO80/94/95/96/204、RPMh。

### 开发经验

- services72 PCIe link/BAR及128MiB散页DMA建表成功，停在SMMU context readback；services73按SM8475实现修正先TCR2/TCR后TTBR，编译通过。

### 完成条件

- 在设备上观察该接口的实际工作结果并保存对应日志

### 当前范围

- 本轮未启动；SMMU启用、QMI固件、扫描与联网仍未确认。

### 下一步

- 读取本轮启动日志并继续完成板级接口

### 证据

- `source`: [services72日志定位SMMU写序；services73复用ArmSmmu4K公共编程原语，未实机启动。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/aaa2d739522ef98142fb83f6bf2ce7ad70e4a7a8/migration/ipados18/services73-smmu-audio.md)

## 音频 {#audio}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- Pong live Android DT、NothingOSS SM8475源码与匹配22H374 restore

### 配置

- board.toml、pong\_ipados18\_defconfig 与对应板级配置

### 操作步骤

- ADSP/GPR/APM、TFA9873双扬声器、MI2S LPAIF0 tertiary/SD0。

### 开发经验

- services72 APM、功放和现代HAL初始化成功；audiomxd因独立AirPlay路由RPC超时退出。services73在launchd前选择原生集成音频provider，运行时已编译。

### 完成条件

- 在设备上观察该接口的实际工作结果并保存对应日志

### 当前范围

- 尚无StartIO、PCM完成或实际出声证据；不公开麦克风。

### 下一步

- 读取本轮启动日志并继续完成板级接口

### 证据

- `source`: [services72的audiomxd堆栈定位CoreMedia路由等待，services73策略与launchd服务门控保持一致。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/aaa2d739522ef98142fb83f6bf2ce7ad70e4a7a8/migration/ipados18/services73-smmu-audio.md)

## 电源 {#power}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- Pong live Android DT、NothingOSS SM8475源码与匹配22H374 restore

### 配置

- board.toml、pong\_ipados18\_defconfig 与对应板级配置

### 操作步骤

- SM8475 ADSP/RPMh、PMIC battery管理和Pong电源策略。

### 开发经验

- DSP readiness和电池协议已有日志；控制器值保持Pong板级来源。

### 完成条件

- 在设备上观察该接口的实际工作结果并保存对应日志

### 当前范围

- 系统挂起恢复尚未完成。

### 下一步

- 读取本轮启动日志并继续完成板级接口

### 证据

- `source`: [DSP readiness和电池协议已有日志；控制器值保持Pong板级来源。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/aaa2d739522ef98142fb83f6bf2ce7ad70e4a7a8/migration/format2/README.zh.md)

## 镜像组装 {#packaging}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- UniXNU c96b299（release 与 templates/package.sh）、uefi-pong 固件树、匹配 22H374 restore、UNIXNU\_UNIQUE\_CHIP\_ID 平台种子

### 配置

- board.toml 的 \[package\]/\[package.defconfig\]/\[bootimg\]/\[userdata\]，os-profiles/ipados-18.7.10-22H374，configs/pong\_ipados18\_ci\_defconfig

### 操作步骤

- scripts/package.sh --check 走 deps/preflight/patches；CI 的 package job 跑 scripts/package.sh --os … --skip-prelink，再跑 scripts/finalize-pong-adt.py：用本地同一份 make-pong-adt-ipados18.py 与同一组参数（12 GiB DRAM、4 GiB 窗口、单 CPU）重写 payload 里的 ADT，并重打 boot.img 与 PONGFAT1 包装的 boot.img.pong。

### 开发经验

- scripts/package.sh --check --no-deps 在 Linux 上通过：1 个补丁、pong\_ipados18\_defconfig、OS ipados-18.7.10-22H374。release 只跑 kernel/package/firmware/payload，不含 userdata；本板内核需要 MACHINE\_CONFIGS=PONG，共享 kernel 步骤写死 BCM2837，因此由 kits/PongPlatform24 作为组件 recipe 编译；共享 kernel 步骤的 tree 已有真实 drivers/ 目录，设备 builder 另用一棵树并在编完后回填 mach.development.pong。bootimg 的 validate 只认 v0-v2 头，board 覆写 header\_version = 0。本板固件只认 PONGFAT1 包装的 ramdisk，故规范产物 boot/boot.img 之外另出 boot.img.pong。userdata 不走 unixnu userdata：它写 SHNGROOT v2 且缺 Data 窗口，本板 RootLayout.h 只接受 v1 且强制 OS/SystemOS/Data 三窗口。

### 完成条件

- 在 macOS runner 上跑通 package.yml 两个 job，并取得 boot.img、boot.img.pong、payload.img、kernel.macho、package.manifest.json 与 userdata 分片

### 当前范围

- CI 尚未在 macOS runner 上运行；真机未刷入。prelink slide 尚未在本板表达，流水线用 --skip-prelink。devicetree.generate\(\) 要求单段 /memory，自定义 DT 属性不透传。

### 下一步

- 在 fork 上手动触发 package.yml，带 ipsw\_url，核对两处产物再上真机

### 证据

- `source`: [board.toml、os-profiles 与 PongPlatform24 kit 已按 docs/porting/packaging.md 组织；package.sh --check 通过，CI 未跑。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/aaa2d739522ef98142fb83f6bf2ce7ad70e4a7a8/migration/format2/README.zh.md)

## 诊断 {#diagnostics}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- Pong live Android DT、NothingOSS SM8475源码与匹配22H374 restore

### 配置

- board.toml、pong\_ipados18\_defconfig 与对应板级配置

### 操作步骤

- 保留屏幕启动日志和ramoops，REC抓取完整console。

### 开发经验

- services72的REC日志与audiomxd超时堆栈已分析，services73修补只构建、未启动。

### 完成条件

- 在设备上观察该接口的实际工作结果并保存对应日志

### 当前范围

- 本轮未启动，SMMU、联网、PCM声音和按键动作仍需设备结果确认。

### 下一步

- 读取本轮启动日志并继续完成板级接口

### 证据

- `source`: [services72的REC日志与audiomxd超时堆栈已分析，services73修补只构建、未启动。](https://github.com/Chengdong-Yu/UniXNU-pong/blob/aaa2d739522ef98142fb83f6bf2ce7ad70e4a7a8/migration/format2/README.zh.md)

</div>
