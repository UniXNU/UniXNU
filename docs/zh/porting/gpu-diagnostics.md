# GPU 帧诊断

sheng 使用以下启动参数记录 GPU 绘制与显示过程：

```text
sheng-gpu-trace=1 sheng-gpu-pixels=1 sheng-diag-export=180
```

日志按 boot-log 计时，在指定秒数导出一次。启用帧诊断后默认 180 秒导出。这些开关不设置自动重启。导出完成后进入日志读取镜像取回数据。正常编译默认关闭帧诊断。

## 记录内容

| 层级 | 字段 |
| --- | --- |
| 构建和配置 | 内核源码 ID、Metal 源码 SHA-256、Turnip 构建 ID、进程名、单采样策略、分环和页表模式、`TU_DEBUG`。 |
| 显示等待 | 请求编号、目标 fence、两个环的完成 fence、共同完成范围、查询结果、锁忙、等待时长、超时和放行原因。 |
| 显示缓冲区 | surface 内存地址、尺寸、格式、当前和待显示槽位、验证、提交切换、硬件确认和归还。 |
| 调度 | PID、队列请求优先级、最终优先级、任务 role、实际环、提交和完成 fence、抢占及恢复。 |
| 共享 surface | IOSurface ID、纹理和 view、导入地址及物理页、command buffer 使用、提交和完成阶段、event/fence 等待及信号。 |
| 渲染 pass | 原始和实际采样数、附件与 resolve 目标、load/store、实际绘制目标和 resolve 复制数量。 |
| 颜色和内存 | Metal/Vulkan 格式、swizzle、GMEM/sysmem 模式、每个附件的状态、GMEM 转换位置和颜色交换设置。 |
| 像素 | GPU 完成后的 Poster 输出、backboardd 输出和显示内存，附尺寸、原始行跨度、格式、传递编码，以及 surface 提供的颜色空间描述和 profile 哈希。 |

每个进程为 Metal command buffer 编号。runtime ID 将其关联到 Vulkan command buffer，Turnip 再关联到内核 fence。跨进程使用 IOSurface ID；内核导入记录将它关联到显示内存。Shared event handle 当前仅在进程内使用，跨进程 handle 请求失败会单独记录。

显示 fence 的 `reason`：0 表示未链接 GPU fence 接口，1 表示目标完成，2 表示等待达到 250 毫秒，3 表示目标未完成，4 表示查询不可用并安排重试。2、3、4 均保留当前显示帧。`query_reason`：0 表示 GPU 尚未发布，1 表示锁忙，2 表示查询成功，3 表示完成状态不可用，4 表示旧查询接口。

开启 `sheng-wallpaper-freeze=1` 时，事件 60（`wallpaper_freeze`）记录阶段、命令、surface ID、触发冻结的命令、冻结时间（微秒）、已放行数量和已拦下数量。阶段 0 表示启用，1 表示放行，2 表示 GPU 完成后冻结，3 表示拦下 runtime 提交。按壁纸 PID 对照内核提交事件，确认冻结后停止产生新的 GPU 工作；此前放行的工作仍可完成。

## 读取和解析

`read-sheng-log.py` 提取 `diag/files/gpu.trace.bin` 和 `gpu.pixels.bin`，并生成 `diag/gpu/events.jsonl`、`links.jsonl`、`summary.json` 及像素文件。已有导出可以单独解析：

```sh
python3 scripts/decode-gpu-trace.py RUN/diag/files
```

脚本位于 UniXNU-sheng 和解析后的构建目录。`decode-gpu-trace.py` 定义版本化字段。事件使用内核启动后微秒，GPU 任务时间戳保留硬件 tick 单位。关联使用明确的句柄和 fence；缺少记录的关联保持未解析。

实时环保留最近 16,384 条事件。配置和有效导入使用 4,096 个元数据槽。每次像素抓取另保留之前 4,096 条事件，避免对应记录被实时环覆盖。导出器先固定这些数据，再扫描其他诊断文件。头部记录丢弃数量，前端另记录传输失败次数。

像素以最多 64 × 64 的原始采样网格保存。每个进程、每个阶段最多三份，间隔至少 30 秒；内核最多保留 24 份。采样在 GPU 实际完成后进行，直接显示路径还要求硬件 flush 清除，复制显示路径等待 GPU 复制确认。不支持的布局只记录元数据。`.raw` 保留原始像素，`.json` 保留布局，`.png` 用于预览。半浮点预览裁剪到 0–1 并编码为 sRGB。格式的传递编码和 IOSurface 颜色空间分开记录；CPU 两次采样间变化会标记。

Metal bundle 内包含 `gpu-build.json`。打包器的 `sheng-uefi-xnu.json` 记录镜像和 payload 的 SHA-256。将这两个文件与日志一起保存，用于核对测试镜像。

## 检查

```sh
python3 scripts/check-gpu-trace.py
python3 scripts/check-native-adreno-scheduling.py
python3 scripts/build-adreno740-kits.py
python3 scripts/build-gop-legacy-display-27.py
python3 scripts/build-boot-progress.py
python3 scripts/build-turnip-darwin.py --target ios27
python3 scripts/build-adreno-metal-plugin.py --target ios27 --no-replay
```

构建命令在已准备好的 sheng iPadOS 27 目录运行，使用该目标的工具链与 UEFI 输入。主机检查覆盖并发写入、环回绕、像素所有权与分片顺序、ABI 副本、损坏导出和句柄复用。

## CPU 延迟记录

事件 61、62、63 分别关联编码批次、前端命令阶段和线程。批次日志保留入队时间、队列深度、任务数及开始和结束时间；命令阶段区分 submit、surface 刷新、runtime commit、资源释放及完成回调。`frames.trace` 的类型 14、15 持久保存这些阶段，类型 16 保存 pass 附件的 load/store、采样数、格式、尺寸及 IOSurface ID。runtime 阶段 40 至 52 记录内存池、KiB 数、复用、分配、缓存和实际释放；阶段 53 至 57 区分完成状态收集、回调、持有资源释放及最后的准备工作。内存操作编号与 command buffer 编号独立。类型 22 保存内存及完成阶段的完整 32 位参数，包括内存大小和 handle 的高低部分。

`kernel.latency.bin` 以 16 字节 `LAT1` 头记录总数、保留数和丢弃数，后接 72 字节记录。524,288 个槽位保存带相同内核消息 cookie 的 IPC 发送尝试和接收完成、用户异常码及 PC/LR/SP、GPU 调频投票、触摸报告中的接触点编号和 0.1 像素坐标。在保留的时间窗内按 cookie、接收方和消息 ID 配对；仅有发送尝试不能证明已送达。GPU 的 accepted level 表示调频请求获接受，不是硬件频率实测值。

```sh
python3 scripts/decode-sheng-latency.py RUN/diag/files/kernel.latency.bin --out RUN/latency.jsonl
```

启用诊断导出后，记录在显示完成 50 次换帧后开始。写入不等待槽位锁。导出先冻结此环，再收集文件，并优先保留崩溃报告。客户端采样通过事件 63 识别 Metal 渲染线程，选中时设置状态位 `0x1000`；进程 CPU 表在 exec 后刷新 `xpcproxy` 名称。性能比较按连续触摸和相同场景分别计算，静止及锁屏切换单列。

## 细分延迟记录

前端类型 17、18 记录至少 250 微秒的编码操作、闭包释放、逐个完成回调、各类 Metal 资源析构，以及外部所有者释放回调。析构覆盖缓冲区、纹理、函数、库、管线、sampler、状态、event、fence、encoder、command buffer、队列、heap 和 binary archive。记录包含操作编号、command、对象或回调地址、线程、源码行号、入队时间和父任务编号。类型 19 和事件 67 定义操作名称，事件 64 将对应计时送入内核 trace。

IPC 日志包含发出的请求、目标 task 和端口，以及回复端口。进程记录将 task 指针对应到 PID 和名称。采样线程每 100 ms 扫描 backboardd、SpringBoard 的阻塞线程，并跟随最多两个 Mach 服务对端。每轮每进程最多扫描 128 个线程、输出六个发生变化的等待者；未变化的等待每秒保留一次。记录用户态及内核栈、等待对象、上下文切换数、Mach 对端和采样覆盖计数。可用的 dispatch introspection v2 接口补充入队、取出、完成、父任务和队列名称；状态记录区分符号缺失和布局不支持。

Mach 异常保存 PC/LR/SP/FP、FAR/ESR 及 29 个通用寄存器。32 项有界队列交给采样线程读取最多 32 层调用栈、128 字节栈内容、shared cache UUID 和最多 64 个映像 UUID，同时记录读取错误、截断及采集延迟。致命信号退出另存退出原因 namespace、code、进程名和最多 96 字节的原因描述。寄存器对应异常现场，异步读取的栈另有采集时间。

启用 GPU DCVS 和诊断导出后，`sheng-gpu-perf=1` 在现有调频线程上每两个周期采集 19 个 A7XX BR 计数器，间隔约 32 ms。记录覆盖 GPU 时钟、UCHE 延迟及读取量、纹理缓存请求和未命中、shader 活动及指令、颜色读写数据，并附选择器回读、读取不稳定、计数重置和抢占 epoch。解码器只对有效区间计算差值。这些计数对应全局 BR 区间，具体负载由 command 和 pass 计时关联。寄存器和计数项与固定版本 Mesa XML 核对。

```sh
python3 scripts/decode-sheng-latency.py RUN/diag/files/kernel.latency.bin --out RUN/latency.jsonl --frames RUN/diag/files/private/var/mobile/Library/Caches/com.apple.backboardd/m2v/frames.trace
```

读取脚本输出解码记录、包含 IPC 和任务关联、计数器差值、异常快照的分析 JSON，以及前端细分计时。正常 source-storage 归档包含 `BootLatencyTrace.c`，并记录相关头文件的 hash。
