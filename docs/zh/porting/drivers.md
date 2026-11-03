# 适配驱动

完成[设备仓库创建与解析](/zh/porting/steps)后使用本清单。先准备平台服务，再逐项接入外设。
选择组件或复用板级代码前，阅读对应指南。

## 1. 定义驱动接口

阅读[组件目录](/zh/reference/components)及下面子系统的源码索引，为选定实现写明：

| 接口 | 必需定义 |
| --- | --- |
| 硬件 | 寄存器范围、访问宽度、中断、时钟、复位和电源所有者 |
| 传输 | 请求格式、响应匹配、超时、重试和断开处理 |
| 内存 | CPU/DMA 地址、缓冲大小/对齐、缓存策略和释放时机 |
| OS | provider 类、属性、ABI 版本、入口和完成通知 |
| 构建 | 源文件、依赖、归档输出、链接输入和初始化调用方 |

硬件值采用目标 DTS、固件和驱动源码，在配置旁记录来源文件及版本。
SoC 操作放入共享支持，板级连接和策略放入设备仓库，OS ABI 绑定放入对应 OS 集成。
指南链接的设备源码作为实现示例。

从主仓库解析目标：

```sh
./unixnu status --json
./unixnu tree
```

底层构建命令在输出的目标树运行。组件位于 `drivers/` 或 `kits/`，
设备 package 链接到 `kits/<board.kit>`。

## 2. 按硬件依赖顺序操作

| 顺序 | 能力 | 适配指南 | 需要检查的实现 |
| --- | --- | --- | --- |
| 1 | CPU、中断、定时器、RAM、DMA | [平台与内存](/zh/porting/platform) | ArmDTPlatform、ArmCpu、ArmSmmu4K、SoC DTSI |
| 2 | 存储、根卷、持久 Data | [UFS](/zh/porting/ufs)与[块设备和根卷集成](/zh/porting/platform#block-and-os-services) | ShengUfs、RamBlock、VirtioMmioBlock、VerifiedRoot |
| 3 | 帧缓冲、刷新、亮度 | [显示与亮度](/zh/porting/display) | GopFramebuffer、DisplayTimingProbe、AppleARMBacklight、GeniI2c |
| 4 | 触控与实体按键 | [输入](/zh/porting/input) | QcomGeniSpi、ShengNovatekTouch、ShengHidInput、ButtonProbe |
| 5 | GPU 与 Metal | [GPU](/zh/porting/gpu) | Adreno740、AdrenoMetal、Sm8550Platform、AdrenoFirmware、AdrenoPM4、AirNir |
| 6 | Wi-Fi | [网络](/zh/porting/network) | Ath12kWifi、WifiProbe、WifiNet、MhiBoot |
| 6a | 基带与移动网络，有基带时适配 | [基带](/zh/porting/baseband) | QcomBaseband、modem 启动、QRTR、IPA/GSI |
| 7 | DSP、音频、电池、CPU 调频、平台电源 | [DSP 与电源](/zh/porting/power) | AdspProbe、AudioProbe、ShengBattery、CpuFreqProbe、ShengPlatformPower |
| 8 | OS 服务和打包 | [OS 集成](/zh/porting/platform#block-and-os-services)与[固件](/zh/porting/uefi-firmware) | SoftwareAES、AppleKeyStoreState、XnuPrelink、DarwinBoot、ShengPreflight |

每篇指南的源码索引列出所需接口和参考实现。按目标硬件实现控制器、电源和 DMA 操作，
再使用选定 OS 的 kernelcache 确认私有 ABI 绑定。

## 3. 接入初始化、ABI 和构建输入 {#build-integration}

阅读以下集成参考：

| 源码 | 需要追踪的内容 |
| --- | --- |
| [board.toml](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/board.toml) | 组件选择与有序归档命令 |
| [build-gop-legacy-display.py](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/scripts/build-gop-legacy-display.py#L253) | 内核编译记录复用、源码对象、ABI 输入和归档生成 |
| [LegacyDisplayProbe.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/LegacyDisplayProbe.cpp#L493) | `native_legacy_display_late_probe` 中的板级初始化调用和依赖顺序 |
| [BatteryProbe.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/BatteryProbe.cpp#L16) | 后期类初始化前后的 `OSMetaClass::preModLoad/postModLoad` |
| [内置驱动示例](/zh/drivers/xnu-drivers) | `IOService` 生命周期、provider 匹配和归档/链接配置 |

1. **选择启动路径。** 由 provider 匹配的服务需要 personality、`probe/start` 和
   [匹配规则](/zh/drivers/device-tree-matching)要求的 provider 属性。
   板级主动启动的服务需要在资源和 OS 依赖就绪后显式调用。
   类初始化应与所选构建的正常注册或后期注册方式一致。
2. **完成资源清理。** 为每项映射、中断、工作循环事件源、计时器、DMA 缓冲和服务引用明确所有者及释放操作。
   初始化失败、设备移除和复位时，先停止新请求，取消或完成未结束工作，再释放资源。
3. **按选定 OS 编译。** 按 [XNU 驱动指南](/zh/drivers/xnu-drivers)使用该内核生成的头文件和编译记录。
   私有接口需要根据选定 kernelcache 记录类布局、虚方法槽位、selector、参数结构和符号绑定。
   通过[构建输入](/zh/porting/migration#build-inputs)提供所选配方需要的候选内核和审计文件。
4. **加入配方。** 设备构建脚本放入 `scripts/`，硬件源码放入 `package/`。
   根据参考配方修改编译记录查找、源码列表、include 路径、类初始化处理和归档目标，
   生成链接配置指定的 archive。可复用组件同时更新目录中的 `build`、`outputs`、依赖和 OS ABI。
5. **连接选择与链接。** 将组件 ID 加入完整的 `[components] include`，按依赖顺序将
   `component:<ID>` 或设备脚本命令加入 `[kernel] archives`。
   需要构建归档时启用 `CONFIG_XNU_BUILD_ARCHIVES=y`，设置消费端读取的驱动开关、归档路径和
   [链接输入](/zh/drivers/xnu-drivers)。新增开关应追踪到构建脚本及初始化调用方。
6. **检查解析结果。** 从主仓库运行 `./unixnu status --json`，确认源码版本、依赖顺序和归档路径。
   运行 `./unixnu kernel`，检查相应归档日志和预链接输出。
7. **检查已链接实现。** 在输出的目标树使用选定 LLVM 工具链中的工具：

   ```sh
   llvm-ar t <archive.a>
   llvm-nm --defined-only <archive.a>
   ```

   找到预期驱动对象和启动符号，再确认内核预链接报告包含该归档。
   从主仓库使用目标本地输入执行 `./unixnu payload` 和 `./unixnu bootimg`。
8. **执行一次完整操作。** 按子系统步骤检查请求、硬件完成、OS 可见结果，再释放或重复。
   用[日志](/zh/porting/log-capture)保存返回码和最后完成阶段。

**结果：** 驱动启动路径可追踪，选定 OS ABI 已解析，驱动已链接入内核，并完成本次验证的操作。

## 4. 记录结果

每项能力在 `porting.toml` 中记录源码版本、固件、启动参数、命令、产物路径、最后成功阶段和结果。
按[完成级别](/zh/porting/records#completion-levels)区分源码检查、主机检查和设备观测。

输入缺失时，记录需要执行的下一步。确认前置条件后再进入下一设备阶段。
返回[启动验证](/zh/porting/bring-up)集成已完成的路径。
