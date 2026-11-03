# 平台、内存与 OS 服务

先完成[设备仓库解析](/zh/porting/steps)。阅读[设备树绑定](/zh/porting/device-tree)、
[匹配规则](/zh/drivers/device-tree-matching)、[ArmDTPlatform](/zh/drivers/arm-dt-platform)
和 [ArmCpu](/zh/drivers/arm-cpu)。

实现后按[驱动接入步骤](/zh/porting/drivers#build-integration)连接初始化调用、归档配方和 OS ABI，
再执行本页对应的硬件验证。

## 源码与接口 {#source-map}

以下链接固定到已核对的源码版本。使用所选 SoC、组件和 OS 版本核对接口；
链接的设备源码提供板级集成示例。

| 实现部分 | 源码 | 阅读与实现内容 |
| --- | --- | --- |
| 平台匹配 | [ArmDTPlatform.cpp](https://github.com/UniXNU/ArmDTPlatform/blob/417ff95d6a6e8607ddea9309ec45c3bfd4a67c60/ArmDTPlatform.cpp#L33) | `ArmDTPlatform`：ADT 根节点、子设备和 NVRAM 发布 |
| CPU 与中断 | [ArmCpu.cpp](https://github.com/UniXNU/ArmCpu/blob/9066b53bbc82e92a98ec44a11dd50fd13eaf1a1b/ArmCpu.cpp#L48) | `ArmCpu`：CPU 注册、计时器/GIC 初始化、次级核入口和 IPI |
| DMA 转换 | [ArmSmmu4K.h](https://github.com/UniXNU/ArmSmmu4K/blob/8bb168ad058c28d5c04f179ba407875eacba7ef3/ArmSmmu4K.h), [ArmSmmu4KContext.h](https://github.com/UniXNU/ArmSmmu4K/blob/8bb168ad058c28d5c04f179ba407875eacba7ef3/ArmSmmu4KContext.h) | 页表分配、映射和上下文编程，先匹配目标 SMMU 版本 |

## 1. 描述 CPU 和中断资源

记录 CPU MPIDR affinity、启动 CPU、启用的核、PSCI 方法、GIC 版本、distributor/redistributor
范围与步长、定时器频率和中断描述。共享拓扑放在 SoC DTSI，板级启用状态放在设备 DTS。

从主仓库使用已检出的 SoC DTSI 目录和目标板 DTS 编译，先填写下面两个路径：

```sh
SOC_DTS=/path/to/UniXNU-soc-common/dts
BOARD_DTS=/path/to/UniXNU-device/dts/board.dts
dtc -I dts -O dtb -i "$SOC_DTS" -o /tmp/board-hardware.dtb "$BOARD_DTS"
dtc -I dtb -O dts /tmp/board-hardware.dtb
```

检查 `reg`、`ranges`、phandle、中断 provider 和禁用节点，再按[ADT 转换](/zh/porting/device-tree)
生成 OS 所需属性。追踪平台源码中每个属性的读取位置，确保名称、字节序和宽度一致。

**预期结果：** platform expert 发布预期 nub，启动核收到定时器中断，启用的次级核完成入口并收到 IPI。
使用其他 GIC 或 PSCI 接口时，启用更多 CPU 前核对 ArmCpu 实现。

### 能效簇与性能簇 {#clusters}

SoC 有两类核心时，在板级 DTS 中给每个 CPU 节点加 `unixnu,cluster-type = "E"`
或 `"P"`。ADT 随后带上每个 CPU 的 `cluster-type`，调度器补丁让 XNU 的 Edge
调度器按一个 E 簇和一个 P 簇运行。SM8550 参考：

| 输入 | 参考取值 |
| --- | --- |
| E 簇 | cpu0 至 cpu2（Cortex-A510） |
| P 簇 | cpu3 至 cpu7（Cortex-A715、A710 和 X3） |
| DTS | [`dts/sheng.dts`](https://github.com/UniXNU/UniXNU-sheng/blob/main/dts/sheng.dts) |
| 调度器补丁 | [`patches/xnu/zzyf-sheng-amp.patch`](https://github.com/UniXNU/UniXNU-sheng/blob/main/patches/xnu/zzyf-sheng-amp.patch) |

该补丁让 UI 线程留在 P 簇。用 CPU 调频器各频域的忙碌比例检查结果：UI 负载应落在 P 频域。

## 2. 核对内存和 DMA

对照固件 RAM、安全保留区、帧缓冲、DSP/GPU 固件、payload 和内核分配。
硬件 DTS 使用连续交接 RAM 范围；加载器拥有的内存请求有独立大小与对齐约束。
两者都应与实际 UEFI 内存映射一致。

对每个 DMA 设备记录地址宽度、物理地址到 IOVA 的映射、SMMU 实例/stream/context 所有权和缓存策略。
目标匹配其转换模型时阅读 [ArmSmmu4K](/zh/drivers/arm-smmu4k)。
GPU、UFS、SPI 和 PCIe 可使用不同 stream 与分配策略。追踪消费端的 MMIO 与映射输入，确认其读取 DTS 属性还是板级常量。

**预期结果：** 每项交接分配有明确所有者，各外设在提交任务前能访问其 DMA 范围。
随后按 [UFS 适配](/zh/porting/ufs)处理存储控制器。

## 3. 接入块设备和 OS 服务 {#block-and-os-services}

| 组件 | 适配工作 | 预期观测 |
| --- | --- | --- |
| [RamBlock](/zh/drivers/ram-block) | 匹配 dense/packed Data 格式与 ADT 占位符，为目标存储策略实现 `native_ufs_store` 持久化回调 | Data 挂载，写入和重启行为符合选定持久化模式 |
| [VirtioMmioBlock](/zh/drivers/virtio-mmio-block) | 提供 VirtIO MMIO 设备、队列、DMA 和中断路由，确认存储 ABI 绑定 | 挂载根卷前确认容量和读取正确 |
| [VerifiedRoot](/zh/drivers/verified-root) | 提供选定镜像的 owner policy 与信任输入，接入存储策略归档 | 目标镜像通过策略验证 |
| [SoftwareAES](/zh/drivers/software-aes) | 匹配 XNU AES 辅助接口与 IOCryptoAcceleratorFamily ABI，为 OS profile 构建绑定 | 加密服务发布，需要的卷操作完成 |
| [AppleKeyStoreState](/zh/drivers/apple-key-store-state) | 根据 OS 确认 selector 和状态回调，接入初始化与事件调用方 | 所需状态查询与通知完成 |
| [XnuPrelink](/zh/drivers/xnu-prelink) | 选择匹配的 XNU、原始 kernelcache、归档绑定和补丁顺序 | 预链接解析选定驱动并生成内核 |
| [DarwinBoot](/zh/drivers/darwin-boot) | 将加载器加入固件或 payload，提供 Mach-O、ADT 和所需 sidecar | 加载器验证输入并报告内核交接 |
| [ShengPreflight](/zh/drivers/sheng-preflight) | 阅读其板级检查，再为目标固件和内存布局编写检查 | 目标固件输入通过对应检查 |

所需产物见[预链接](/zh/concepts/prelink)、[完整性策略](/zh/concepts/security)、
[payload](/zh/concepts/payload)和 [userdata](/zh/guide/userdata)。
根卷 UUID、分区布局、Data 持久化和日志分配保留在设备配置中，OS profile 提供对应版本的 ABI。

## 4. 检查组装后的选择

从主仓库执行：

```sh
./unixnu status --json
./unixnu build kernel
```

构建前检查依赖顺序、配置片段和补丁序列。每项归档需要对应 OS 输入及初始化调用方。
[内核指南](/zh/guide/build-kernel)说明构建输出和失败处理。

在[移植记录](/zh/porting/records)中分别记录源码/构建证据与设备结果。
接下来完成[存储](/zh/porting/ufs)，再进入[显示与亮度](/zh/porting/display)。
