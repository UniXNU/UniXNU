# Novatek NT36532E 触控驱动

先按[适配流程](/zh/porting/input)准备板级输入、修改源码、接入构建并逐步验证。

ShengNovatekTouch 是 UniXNU 的独立模块，由 UniXNU-sheng 引入。它是 Novatek NT36532E 的完整触控驱动，也是新触控驱动的示例。

| 仓库 | 路径 | 内容 |
| --- | --- | --- |
| [ShengNovatekTouch](https://github.com/UniXNU/ShengNovatekTouch) | `NvtTouchCore.c` | 纯触控处理 |
| ShengNovatekTouch | `NvtProtocol.c` | 控制器协议 |
| ShengNovatekTouch | `NvtProtocol.h` | 协议常量和总线接口 |
| [QcomGeniSpi](https://github.com/UniXNU/QcomGeniSpi) | `GeniSpi.c` | GENI SPI 引擎 |
| [UniXNU-sheng](https://github.com/UniXNU/UniXNU-sheng) | `package/TouchBoard.h` | 板级常量和时钟辅助函数 |
| UniXNU-sheng | `package/TouchProbe.cpp` | 内核探针和帧循环 |
| UniXNU-sheng | `package/TouchBoardTests.c` | 板级辅助函数的主机测试 |
| [ShengHidInput](https://github.com/UniXNU/ShengHidInput) | `NativeHidInput.cpp` | HID digitizer 源 |

## 两层结构

驱动把纯逻辑和硬件访问分开。

```
NvtTouchCore.c      矩阵到触点，不分配，不做 I/O
NvtProtocol.c       芯片识别、固件、帧，通过 nvt_bus
TouchProbe.cpp      MMIO、时钟、引脚、DMA、SMMU、线程
NativeHidInput.cpp  触点到 HID 报告
```

纯核心和协议接收 `struct nvt_bus`：

```c
struct nvt_bus {
  void *ctx;
  int (*xfer)(void *ctx, const uint8_t *tx, uint8_t *rx, size_t len);
  void (*delay)(void *ctx, unsigned ms);
};
```

主机测试提供假总线，内核探针提供 GENI SPI 传输。

## 触控处理

`NvtTouchCore.c` 处理 40 乘 60 的 16 位矩阵：

1. 收集 72 帧启动数据。
2. 用启动帧的中位数形成每个节点的参考值。
3. 减去参考值得到 delta 矩阵。
4. 对高于噪声阈值的节点按最陡上升标记。
5. 找局部极大值并形成 blob。
6. 拒绝超过手掌节点数的 blob。
7. 计算每个 blob 的加权质心。
8. 应用边缘补偿。
9. 用半径和 down/up 阈值跨帧跟踪触点。
10. 从槽位第二帧开始报告触点。

核心不分配内存。临时数组位于 `struct nvt_touch_core`，探针只分配一次。注释记录原因：内核线程栈为 16 KiB，而临时数据更大。

## 控制器协议

`NvtProtocol.c` 提供：

| 函数 | 用途 |
| --- | --- |
| `nvt_identify` | 读取芯片 id 并选择映射 |
| `nvt_fw_parse` | 把固件镜像解析为 ILM 和 DLM 部分 |
| `nvt_download_firmware` | 复位 bootloader、写入部分、校验 SRAM |
| `nvt_start_scanning` | 读取固件版本和矩阵几何 |
| `nvt_peek_frame_header` | 读取 32 字节 THP 头 |
| `nvt_read_frame` | 读取完整 THP 帧 |
| `nvt_frame_header_valid` | 拒绝被撕裂的帧 |
| `nvt_frame_matrix` | 解码矩阵 |

传输长度、读取上限和帧长度来自厂商协议常量。

## 板级常量

`TouchBoard.h` 保存每个地址和位，并注明来源：

| 组 | 示例 |
| --- | --- |
| QUP wrapper 和 serial engine | 基址和大小 |
| SMMU | stream ID 和 apps SMMU 基址 |
| GCC | vote 寄存器、halt 寄存器、DFS 级 |
| TLMM | GPIO 编号、功能、驱动强度 |
| SPI | 模式和最高频率 |

时钟辅助函数是纯函数。`tb_choose_clock` 选择不超过目标频率的最高 DFS 级和分频。主机测试覆盖分频计算。

## 探针阶段

探针默认关闭。启动参数 `sheng-touch=<n>` 选择阶段：

| 阶段 | 工作 |
| --- | --- |
| 1 | 读取 GCC 分支、DFS 级、引脚和 serial engine 身份 |
| 2 | vote 并等待 QUP 时钟，配置引脚 |
| 3 | 初始化 GENI SPI，选择时钟，识别芯片 |
| 4 | 下载固件，开始扫描，处理帧 |

每个阶段在诊断页报告结果，首次失败停止后续阶段。

## 硬件路径

1. 在 GCC 中 vote GPLL0 和 QUP 分支。
2. 等待分支时钟离开 off 状态。
3. 在 TLMM 配置 SPI 引脚。
4. 映射 QUP wrapper 和 serial engine。
5. 初始化 GENI SPI。
6. 选择 DFS 级和分频。
7. 分配物理连续 DMA 缓冲。
8. 用 bypass stream 通过 apps SMMU 映射缓冲。
9. 每次传输前后维护缓存。
10. 复位触控 bootloader 并下载固件。
11. 轮询 THP 头，读取完整帧并发布触点。

SMMU 映射沿用 UFS 驱动的 bypass 模型。DMA 缓冲是 cached 的，驱动在每次传输前后显式 clean 和 invalidate。

## HID 发布

探针通过全局变量发布触点：

```c
volatile uint32_t native_touch_seq;
volatile uint32_t native_touch_count;
volatile int native_touch_xs[NVT_SLOTS];
volatile int native_touch_ys[NVT_SLOTS];
volatile int native_touch_ids[NVT_SLOTS];
```

写入方在更新前后递增序列号，读取方据此检测撕裂快照。`ShengHidInput` 读取快照并发出 digitizer 报告。

## 适配这个示例

1. 把纯处理层与总线分开。
2. 把每个板级常量放入头文件并注明来源。
3. 运行所复用处理逻辑和时钟辅助函数的现有主机检查。
4. 加入分阶段启动参数，让每个硬件步骤可观察。
5. 通过序列计数器和固定大小快照发布触点。
6. 在启动日志显示每个阶段前保持驱动默认关闭。

## 下一步

- [XNU 驱动](/zh/drivers/xnu-drivers)
- [设备树匹配](/zh/drivers/device-tree-matching)
- [参考设备记录](/zh/devices/sheng)
