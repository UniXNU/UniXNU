# UFS 移植

先阅读设备 `porting.toml` 的存储部分和[组件目录](/zh/reference/components)。
官方实现为 [ShengUfs](/zh/drivers/sheng-ufs)，运行时类名为 `NativeUfs`。

ShengUfs 包含 SM8550 控制器访问、固件状态接管、SMMU、GPT/窗口解析和板级
持久存储策略。每个目标需要检查其硬件常量和板级策略。

实现后按[驱动接入步骤](/zh/porting/drivers#build-integration)连接初始化调用、归档配方和 OS ABI，
再执行本页对应的硬件验证。

## 源码与接口 {#source-map}

以下链接固定到已核对的源码版本。使用所选 SoC、组件和 OS 版本核对接口；
链接的设备源码提供板级集成示例。

| 实现部分 | 源码 | 阅读与实现内容 |
| --- | --- | --- |
| 控制器与 DMA | [NativeUfs.cpp](https://github.com/UniXNU/ShengUfs/blob/fd420df000f43213d9cd019725abff0849c98c72/NativeUfs.cpp#L1108), [SmmuTakeover.h](https://github.com/UniXNU/ShengUfs/blob/fd420df000f43213d9cd019725abff0849c98c72/SmmuTakeover.h), [RootTransportLayout.h](https://github.com/UniXNU/ShengUfs/blob/fd420df000f43213d9cd019725abff0849c98c72/RootTransportLayout.h) | 请求队列所有权、槽布局、映射和上下文接管 |
| 命令完成 | [RootCommands.h](https://github.com/UniXNU/ShengUfs/blob/fd420df000f43213d9cd019725abff0849c98c72/RootCommands.h#L89), [NativeUfs.cpp](https://github.com/UniXNU/ShengUfs/blob/fd420df000f43213d9cd019725abff0849c98c72/NativeUfs.cpp#L1017) | `hostIssue`/`hostAwait`：描述符、doorbell、完成中断、混合轮询、OCS、响应和 SCSI 状态 |
| 排队与 DMA | [RootCommands.h](https://github.com/UniXNU/ShengUfs/blob/fd420df000f43213d9cd019725abff0849c98c72/RootCommands.h#L377) | 槽池、零拷贝 PRDT（`hostBuildPrds`）、忙重试 |
| 存储策略 | [RootLayout.h](https://github.com/UniXNU/ShengUfs/blob/fd420df000f43213d9cd019725abff0849c98c72/RootLayout.h), [RootPublication.h](https://github.com/UniXNU/ShengUfs/blob/fd420df000f43213d9cd019725abff0849c98c72/RootPublication.h) | GPT/窗口边界和根 IOMedia 发布 |
| 时钟状态 | [GccUfs.h](https://github.com/UniXNU/ShengUfs/blob/fd420df000f43213d9cd019725abff0849c98c72/GccUfs.h) | 分支使能与硬件门控状态解析 |

## 操作步骤 {#procedure}

1. 根据目标资料填写[硬件清单](#硬件清单)，写寄存器前确认控制器、PHY、时钟、复位、SMMU 和 DMA 的所有权。
2. 实现或适配[初始化顺序](#初始化与所有权)，结合目标控制器和固件状态核对[已有经验](#可复用经验)。
3. 按[配置](#配置)加入匹配的组件、archive 配方、内核开关和根卷设置，提供匹配的存储 ABI 输入并构建内核。
4. 按[完成条件](#完成条件)依次验证寄存器访问、DMA、命令完成、已知块读取、根卷挂载、持久化和[性能](#performance)，逐项记录结果。
5. 更新 `porting.toml` 的存储部分，运行记录检查，再继续[显示与亮度](/zh/porting/display)。

## 硬件清单

| 输入 | 实现前记录 |
| --- | --- |
| 控制器 | compatible、版本、MMIO 基址/长度、能力和中断路由 |
| PHY | 寄存器范围、lane、参考时钟、调优来源和初始化责任方 |
| 时钟 | provider、clock ID、频率、父时钟、分支门控和互联带宽请求 |
| 复位与电源 | 复位线、稳压器、电源域、时序和固件所有权 |
| SMMU | 实例、stream ID、掩码、context bank、地址位宽和现有映射 |
| DMA | 缓冲区分配、物理地址/IOVA 关系、对齐、一致性和缓存维护 |
| 交接 | HCE/HCS、链路、电源模式、请求列表基址和未完成命令 |
| 存储布局 | LUN、块大小、容量、GPT、根卷窗口、Data 和日志保留区 |
| OS 接口 | 存储 ABI、预链接输入、发布/匹配和完成处理 |

每个值引用板级 DTS、SoC 资料、固件源码或测量记录。共享控制器资源放在 SoC DTSI，
板级连接和策略放在设备仓库。按[设备树绑定](/zh/porting/device-tree)描述寄存器宽度、
父节点 address cells、`ranges`、中断 provider 和 IOMMU 引用。

SM8550 参考 DTSI 导出控制器 `0x01d84000/0x3000` 和 PHY `0x01d80000/0x2000`。
GCC `0x00100000` 和 stream `0x60` 的 apps-SMMU 操作位于 ShengUfs。当前驱动通过
C++ 常量和操作访问这些资源。资源改为 DTS 属性时，还需要修改读取方并检查生成的 ADT 值。

## 初始化与所有权

1. 按规定宽度读取控制器、时钟、PHY、链路和 SMMU 状态。
2. 确认固件已配置的时钟、复位和电源域。
3. 选择固件状态接管，或完整定义的控制器/PHY 初始化序列。
4. 分配请求描述符和数据缓冲区，确认 DMA 可达范围。
5. 确认请求列表和所选 SMMU context 的独占所有权。
6. 提交有界命令并检查传输、响应和 SCSI 状态。
7. 发布根设备前读取容量和已知数据块。

ShengUfs 接管固件留下的控制器和链路状态，把请求列表移到单独的写合并页，
最多同时执行 32 条命令，每条命令占一个槽。命令完成使用控制器中断加混合轮询，
页对齐缓冲区走零拷贝 DMA。移植此流程需要检查 `NativeUfs.cpp` 中的请求列表状态与所有权。需要冷初始化的设备应实现并记录
PHY、复位、时钟和电源序列。

## 可复用经验

- 空闲且启用硬件门控的 AHB 分支可能报告 `CLK_OFF`，需要一起检查分支使能和
  硬件门控位。参见 `GccUfs.h`。
- SMMU bypass 受支持的地址位宽约束。检查完整 DMA 范围及已有 stream/context-bank
  所有权。参见 `SmmuTakeover.h`。
- 容量、GPT 和根卷窗口边界分别检查。LBA 转字节始终使用实际逻辑块大小。
  参见 `RootLayout.h`。
- 根卷读取、持久 Data 写入和复位处理分别定义完成条件。每次写入验证记录分配范围和恢复方法。
- 接管 apps SMMU 的驱动也负责其他设备需要的 stage 1 窗口。ShengUfs 为显示 bank
  （`sheng-dpu-scanout`）和 WiFi 端点（`sheng-wifi=2` 或更大）各建立一个，默认都关闭。
  音频流保持直通：给它们使用转换 context 会让参考板型复位。
- 请求列表项为 32 字节，两项共用一条 64 字节缓存行。在非一致性的 stream 上，
  清理一项可能把旧副本写回，覆盖控制器为相邻项写入的完成状态。请求列表应放在
  写合并页上（Linux 使用一致性 DMA 内存），或让每个槽的列表项独占一条缓存行。
- 只有 UTRD 中断位（dword 0 bit 24）置位的描述符才会置 UTRCS 并产生完成中断。
  只打开 UTRCE，按已清除的 doorbell 位找出完成的命令，与 Linux ufshcd 相同。
- 小块命令每次都睡眠等中断，开销比命令本身还大。等待先轮询 200 微秒再睡眠，
  可保持 8 和 32 队列深度下的小块吞吐，长命令也会让出 CPU。
- 修改链路前用 DME_GET 读取链路状态（`PA_TxGear`、`PA_RxGear`、`PA_HSSeries`、
  `PA_PWRMode`）。参考固件留下的是双通道 HS-G5 Rate A FAST 模式。

[参考存储记录](/zh/devices/sheng#storage)提供板级参数、实现引用和当前范围。

## 配置

在完整 `[components] include` 数组中选择匹配的存储组件，在 `[kernel] archives`
的适当位置加入构建项。数组会替换继承值。参考配置如下：

```toml
# 完整设备选择中的条目：
# [components] include: "ShengUfs"
# [kernel] archives: "component:ShengUfs"

[userdata]
# 按目标 GPT 设置 first_lba、last_lba 和 lba_bytes。

[payload.adt]
# 按所选 APFS 卷设置 root_match_volume_uuid。
```

目标分区参数取自本机 GPT，根卷 UUID 取自所选卷。
保留其他必需的 `payload.adt` 字段。所选 defconfig 启用 `CONFIG_XNU_NATIVE_UFS=y`，
该运行时的完整内核参数数组加入 `native-ufs-root=1`。

组件源码版本固定在设备仓库。共享构建工具将其放入目标的 `drivers/ShengUfs`。
存储 ABI 绑定需要所选 kernelcache 和匹配的审计输入。

## 完成条件

| 阶段 | 必需观察 |
| --- | --- |
| 硬件清单 | 控制器、PHY、时钟/复位/电源和 SMMU 参数有来源与责任方 |
| 控制器访问 | 寄存器可读，时钟和链路状态符合初始化方式 |
| DMA 与命令 | 缓冲区可达，命令完成和失败均被处理 |
| 块读取 | 容量和已知数据块匹配所选 LUN 与逻辑块大小 |
| 根卷 | GPT 和根卷窗口边界正确，配置的根卷挂载并启动用户态 |
| 持久化 | 写入位于分配的 Data 区域，经过规定重启/复位序列后保留 |
| 性能 | 在同一设备、同一 LBA 上，每项读取测试不低于主线 Linux 驱动 |

每个阶段更新存储记录。源码、主机和设备结果使用对应的
[完成等级](/zh/porting/records#completion-levels)。

```sh
./unixnu defconfig myboard_defconfig -D /path/to/device
./unixnu status --json -D /path/to/device
./unixnu build kernel -D /path/to/device
python3 scripts/porting-record.py check --device /path/to/device
```

## 性能 {#performance}

在同一设备上，用相同的 LBA 和相同的测试序列与主线 Linux 驱动对比。参考板型两侧都已提供：

| 一侧 | 工具 | 输出 |
| --- | --- | --- |
| Linux | `scripts/linux-ufsbench.py` 启动只读 Linux 读取镜像，以 O_DIRECT 运行 `package/linux-log/ufsbench.c`，然后回到 fastboot | `bench.txt`，以及内核的 UFS 链路和队列信息 |
| XNU | `sheng-ufs-bench=1` 在启动继续之前于内核中运行同样的测试，核对零拷贝读取与数据区路径，然后重启回 fastboot | UFS 日志消息缓冲区中的 `ufsbench` 行 |

两侧都在刷入的根镜像范围内，按 1、8、32 队列深度随机读取 4 KiB、16 KiB、
128 KiB 和 1 MiB，然后顺序读取。每侧至少运行三次，比较平均值：

```sh
python3 scripts/linux-ufsbench.py --reader <reader.img> --out out/linux-bench-1
python3 scripts/compare-ufsbench.py --linux out/linux-bench-*/bench.txt --xnu <log>/msgbuf.txt ...
```

在参考板型上，每项测试都不低于主线 Linux 7.2（`ufshcd-qcom`）。最接近的是
8 队列深度下的 4 KiB（比值 1.01）；1 MiB 读取在 1 队列深度下达到 2.2 GB/s，
8 队列深度下达到 3.7 GB/s，Linux 分别为 1.3 和 1.9 GB/s。

## 下一步

根卷路径就绪后[适配显示与亮度](/zh/porting/display)，其他子系统见[驱动清单](/zh/porting/drivers)。

arm64e 的公开源码构建方法及当前链接、运行时限制见[公开源码驱动构建](/zh/porting/migration#source-drivers)。历史 iOS 17 真机结果不代表该路径已通过验证。
