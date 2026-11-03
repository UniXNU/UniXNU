# DSP、音频与电源驱动

先完成[平台内存、中断和 DMA](/zh/porting/platform)。分别实现传输层、设备协议和 OS 服务。
按硬件与固件接口选择下面的源码参考，每一步都对应具体接口或可观察结果。

## 1. 确认目标接口

从目标 DTS、固件源码和厂商驱动收集以下输入：

| 功能 | 输入 | 实现产物 |
| --- | --- | --- |
| DSP | 固件/PAS ID、内存预留、邮箱中断、共享内存布局、时钟和电源归属 | 固件加载器和消息传输 |
| 音频 | codec/功放 ID、总线、时钟、路由、DSP 拓扑、支持格式和 OS 音频 ABI | 端点配置、流引擎和 OS 服务 |
| 电池 | 电量计或固件协议、属性 ID、单位、电流符号和通知消息 | 测量值解码器和 power-source 服务 |
| 电源 | 时钟域、OPP 表、稳压器、固件投票和温控限制 | 调用相应控制器接口的板级策略 |

在[固件清单](/zh/porting/device-repository)中记录每个二进制的来源和版本。
直接连接 I2C 电量计的板型实现该芯片的寄存器协议，使用 DSP 电池管理器的板型实现其消息协议。
先确定传输方式，再选择参考代码。

## 2. 实现 DSP 传输 {#dsp}

| 源码 | 阅读内容 |
| --- | --- |
| [AdspProbe.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/AdspProbe.cpp) | 固件加载、SMEM、SMP2P、GLINK、邮箱和资源初始化 |
| [ShengAdsp.h](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/ShengAdsp.h#L15) | `ShengAdspClient`、通道注册和发送队列 |
| [LegacyDisplayProbe.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/LegacyDisplayProbe.cpp#L493) | DSP 与消费者的初始化顺序 |

链接的文件提供 Qualcomm GLINK 集成参考。使用该接口时：

1. 按目标硬件适配固件认证、预留内存和电源投票。打开通道前，先建立邮箱和 ready/crash 通知路径。
2. 实现 `ShengAdspClient` 的通道状态和接收回调。回调运行于 DSP 线程，应将收到的字节复制到
   有界队列，再唤醒消费者工作循环。请求处理和等待放在消费者侧。
3. 调用 `sheng_adsp_channel(name, intent_size, intent_count, initiator, callbacks, context)`
   注册目标通道。通道名、接收缓冲大小和打开方向采用目标服务协议的定义。
4. 处理 `sheng_adsp_send` 返回值：`0` 表示已入队，`-1` 表示队列已满或消息过长，`-2` 表示参数错误。
   参考 API 的消息上限是 `SHENG_ADSP_MAX_MESSAGE`，即 512 字节。
   更大消息的服务需要相应的传输和接收缓冲支持。
5. 断开时取消请求，使远端句柄失效；重连后重新协商通道并恢复订阅，再恢复消费者。

**结果：** 通道能够打开、完成一次有超时的请求/响应、报告失败并重连。
用[日志抓取](/zh/porting/log-capture)保存通道名称和响应字节。

## 3. 实现音频流 {#audio}

Qualcomm AudioReach/GPR 固件按执行顺序参考以下源码：

| 源码 | 用途 |
| --- | --- |
| [ShengGpr.h](https://github.com/UniXNU/UniXNU-sheng/blob/552b67499135bae191f415f444d782a6942c252e/package/ShengGpr.h)、[ShengAudioReach.h](https://github.com/UniXNU/UniXNU-sheng/blob/552b67499135bae191f415f444d782a6942c252e/package/ShengAudioReach.h) | 包头、APM 就绪查询、graph 打开与配置、内存映射、PRM 投票和时钟 |
| [AudioProbe.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/552b67499135bae191f415f444d782a6942c252e/package/AudioProbe.cpp)、[ShengCs35l43.c](https://github.com/UniXNU/UniXNU-sheng/blob/552b67499135bae191f415f444d782a6942c252e/package/ShengCs35l43.c) | 通过 I2C 配置功放、graph 启动、周期缓冲区流程、codec SoundWire 启动、麦克风采集 |
| [ShengAudioService.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/552b67499135bae191f415f444d782a6942c252e/package/ShengAudioService.cpp)、[ShengAudioPlugIn.c](https://github.com/UniXNU/UniXNU-sheng/blob/552b67499135bae191f415f444d782a6942c252e/hal/ShengAudioPlugIn.c) | 供系统音频服务使用的音频服务及其插件 |
| [Linux q6apm.h](https://github.com/torvalds/linux/blob/v6.12/sound/soc/qcom/qdsp6/q6apm.h)、[q6apm.c](https://github.com/torvalds/linux/blob/v6.12/sound/soc/qcom/qdsp6/q6apm.c) | 图生命周期、内存映射和读写请求 |
| [Linux audioreach.c](https://github.com/torvalds/linux/blob/v6.12/sound/soc/qcom/qdsp6/audioreach.c)、[topology.c](https://github.com/torvalds/linux/blob/v6.12/sound/soc/qcom/qdsp6/topology.c) | 模块配置、图连接、媒体格式和端点参数 |
| [Linux q6apm-dai.c](https://github.com/torvalds/linux/blob/v6.12/sound/soc/qcom/qdsp6/q6apm-dai.c) | `q6apm_dai_prepare`、流事件和周期缓冲区数据流 |

Linux 提供协议和流生命周期参考。使用选定 XNU 的接口实现其中的分配、调度、DMA 和完成通知，
复用代码时保留相应源码许可证。

1. **打开并识别服务。** 确认目标固件的 GPR domain、port、包大小和 opcode，用 token 匹配响应。
   先完成就绪查询，验证第一条协议交互。
2. **描述一条完整路由。** 为一个播放或采集端点记录图/子图 ID、模块实例 ID、连接、codec 端口、
   功放配置、时钟和声道映射。这些值来自目标固件拓扑和 codec 驱动。
   实现该路由的寄存器操作和上电顺序。
3. **实现图命令。** 参考 `q6apm_graph_*` 实现打开、配置、准备、启动、停止和关闭。
   检查每个响应，将图 ID 和状态保存在所属流中。后续操作失败时释放已经创建的对象。
4. **实现缓冲路径。** 分配 DSP 可访问的周期缓冲区，通过固件协议映射，设置 PCM 格式与声道映射，
   再准备并启动图。播放通过相当于 `q6apm_write_async` 的操作提交，采集通过 `q6apm_read` 提交空缓冲。
   完成时同步缓存、更新流位置并复用已完成的缓冲。解除映射和关闭图前，先停止未完成工作。
5. **接入 OS 服务。** 从选定 kernelcache 和框架中确认音频 provider、必需方法、请求布局、
   映射内存类型和完成通知。按[内置驱动集成](/zh/drivers/xnu-drivers)记录这些 ABI 输入。
   将格式选择、启停、位置和缓冲完成接到流引擎，仅发布端点已经实现的格式和路由。
6. **验证路由。** 播放已知 PCM 信号或录制已知输入，检查声道顺序、采样率、流位置和缓冲内容。
   重复启停，检查缓冲耗尽、超时和 DSP 重启。直接流路径成功后，再验证 OS 应用的播放或录音。

在 SM8550 上，以下固件细节决定通路能否启动：

- DSP 接收的缓冲区地址是 32 位地址，高 32 位放流索引（`0x1001 & 0xf`）。周期缓冲区要放在 4 GiB 以下。
- DSP 先提供小的 GLINK intent，请求后再给大的。远端 intent 表满时也要保留新给的 intent。
- PRM 请求从 PRM 自己的端口发出，使用 PRM 时钟 ID；TX core 时钟是 `0x30c`，不是设备树里的编号。
- VA macro 和 TX macro 都要打开 TX SoundWire master 的时钟门控。
- CoreAudio 假定 host clock 为 24 MHz。时基为 19.2 MHz 时，音频服务在启动时修正 CoreAudio 的这个常量，否则音频服务器的 IO 周期会长 25%，播放和录音都会卡顿。

**结果：** 一条完整路由传输 PCM 数据、报告进度并释放资源。
保存路由描述、格式、流计数和采集结果。下一端点使用自己的路由配置和观察记录。

### 麦克风采集 {#microphone}

采集路由在上面的流步骤之外，还需要 codec 和 SoundWire 链路。

1. **给 codec 上电。** 释放复位并打开供电。投票 TX 和 VA macro 时钟，再打开两者的
   门控：SM8550 上 VA macro 也门控 TX SoundWire master。
2. **建立 SoundWire 链路。** 启动 TX master，等待 codec 枚举。配置前先读取厂商和器件 ID。
3. **配置模拟通路。** 选择麦克风输入、偏置和 ADC，设置 ADC 增益，再把 ADC 映射到
   codec 数据端口和通道。
4. **配置数字通路。** 把 master 端口接到读取它的 TX decimator，再把 decimator 接到
   DSP graph 使用的 codec DMA 接口。
5. **读取缓冲区。** 通过读请求排队采集缓冲区。每个应答带有字节数和偏移，只取这些
   字节；周期不满是正常的。
6. **发布输入。** 直接采集已知声音成功后，再发布输入流。

参考路由见 [AudioProbe.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/main/package/AudioProbe.cpp)：

| 阶段 | 参考取值 |
| --- | --- |
| Codec | WCD938x，复位 gpio108，供电 ldob15，TX master（0x6d30000）上的 SoundWire 设备 1 |
| 模拟 | AMIC3、micbias 3、ADC2 |
| 链路 | codec 数据端口 1 通道 2 到 master 端口 2 |
| 数字 | TX decimator 0 读取 SWR_MIC1，codec DMA TX3 |
| 格式 | 单声道，48 kHz |
| iOS | HAL 插件的输入端口；iOS 只在 Thunderbolt 传输类型下接受它 |

用 `sheng-audio=4` 检查采集，它在启动时读取两秒：`[mic]` 和 `[mic capture]` 日志行
给出返回的周期、字节数、非零样本比例和峰值。随后在应用中录音并读取 `[audio-io]`。

## 4. 实现电池状态上报 {#battery}

| 源码 | 用途 |
| --- | --- |
| [ShengBattmgr.h](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/ShengBattmgr.h#L30)、[ShengBattmgr.c](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/ShengBattmgr.c) | 请求/响应格式、刷新状态机和单位转换 |
| [ShengBattery.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/ShengBattery.cpp#L39) | `IOPMPowerSource` 属性、工作循环、计时器和通知处理 |
| [BatteryProbe.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/BatteryProbe.cpp#L16) | 类注册与服务启动 |
| [XNU IOPMPowerSource.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-10063.141.1/iokit/IOKit/pwr_mgt/IOPMPowerSource.h) | power-source 属性设置与状态发布 API，使用时匹配选定 XNU 版本 |
| [Linux qcom_battmgr.c](https://github.com/torvalds/linux/blob/v6.12/drivers/power/supply/qcom_battmgr.c) | Qualcomm 电池管理器协议变体和属性处理 |

1. 实现目标电量计读取或固件请求。使用参考 PMIC GLINK 协议时，接收值前核对 owner、消息类型、
   opcode、属性 ID 和响应长度。每次保留一个未完成请求，处理其超时后再推进刷新周期。
2. 分别保存有效读数与缺失/失败状态。实现包含电池存在、外接电源、充电状态、容量、电压、电流、
   温度和剩余时间的快照，记录每项原始值到 OS 值的转换。
   参考实现将电压/电流从微单位转换为毫单位，将以 0.01% 为单位的容量值转换为百分比，将秒转换为分钟。
   使用前确认目标协议的单位和充电电流符号。
3. 使用选定 XNU 头文件继承 `IOPMPowerSource`，创建工作循环、响应队列和请求/刷新计时器。
   将收到的消息交给解码器，在快照完整后更新属性。
4. 初始有效属性准备好后调用 `registerService()`，后续变化调用 `updateStatus()`。
   电池存在、外接电源和充电状态应与容量及测量值一致。按目标 OS 属性定义填写适配器信息。
5. 订阅变化通知并安排周期刷新。传输断开时取消请求，在驱动中将读数标为过期；
   刷新成功前，按选定 OS 的规则处理不可用数据。
6. 将原始读数和发布属性与目标电量计或原厂系统读数比较。验证插拔电源、充放电、响应超时和服务重启。
   分别检查协议响应与 OS 可见更新。

**结果：** OS 收到单位明确、及时更新的测量值。
固件负责充电控制时保留其所有权，驱动实现测量值发布。
主机控制的充电器需要独立的控制协议、限值和温控策略。

## 5. 实现调频与电源操作 {#power}

阅读 [CpuFreqProbe.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/552b67499135bae191f415f444d782a6942c252e/package/CpuFreqProbe.cpp) 的 EPSS LUT 和 CPU/L3 工作点访问、[QcomRpmh.h](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/QcomRpmh.h) 的资源投票，
以及 [ShengPlatformPower.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/ShengPlatformPower.cpp) 的 OS 平台电源集成。这些实现供对应 Qualcomm 硬件接口参考。
[GpuPowerProbe.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/552b67499135bae191f415f444d782a6942c252e/package/GpuPowerProbe.cpp) 包含 GPU 调频。

1. 将 CPU affinity 映射到性能域。读取目标 LUT、参考时钟和使能状态，按该控制器编码换算频率。
2. 实现工作点请求和状态回读，按规定顺序执行目标稳压器、互连和温控要求。
3. 为外设电源投票明确所有权和引用计数。停止依赖的 DMA 和中断后再释放资源。
4. 接入选定 OS 电源回调。休眠/唤醒时保存所需状态，恢复时钟与映射、重新使能中断，再恢复消费者。
5. 在负载下测量频率，然后在依赖驱动运行时逐项验证外设转换和恢复。

SM8550 上的调频输入：

- CPU：每 16 ms 读取调度器记录的各 CPU 空闲时间。频域跟随其中最忙的 CPU，留 1.25 倍余量，连续四个较闲的窗口后才降频。
- GPU：读取 GMU XO 忙碌计数器，按让 GPU 约一半时间忙碌的档位通过 HFI 投票，同时投该档位的带宽。
- 触摸：收到触摸报告后，P 频域和 GPU 保持最高档，直到最后一次报告后 1 s（`sheng-cpufreq-boost-ms`、`sheng-gpu-dcvs-boost-ms`）。
- 帧：最近 4 个窗口中有 2 个有 GPU 提交时，所有 CPU 频域在 300 ms 内不低于各自最高档的 60%。GPU 从空闲降频后恢复工作时，50 ms 内以当前频率的两倍运行，至少 578 MHz。
- fence 等待：等待者睡眠到 fence 中断为止，最长 1 ms（`sheng-gpu-pause-us`），不再轮询。

**结果：** 频率请求和电源转换产生可观察效果，并保持依赖设备正常运行。

## 6. 构建并验证接口

按[驱动接入步骤](/zh/porting/drivers#build-integration)加入源码、ABI 绑定、初始化调用和归档输入。
参考 [build-gop-legacy-display.py](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/scripts/build-gop-legacy-display.py#L253) 中 DSP、电池服务和音频探测的编译方式，以及 [LegacyDisplayProbe.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/LegacyDisplayProbe.cpp#L493) 中的调用顺序。
为目标选择满足平台、传输和 OS 依赖的初始化时机。

选定目标后，从主仓库运行：

```sh
./unixnu status --json
./unixnu kernel
./unixnu payload
./unixnu bootimg
```

构建前准备选定 OS 和[本地输入](/zh/reference/configuration#local-build-inputs)，
使用目标文档中的启用参数。在[适配记录](/zh/porting/records)中保存协议响应、图或服务发布、
数据流和重启行为，再继续[启动验证](/zh/porting/bring-up)。
