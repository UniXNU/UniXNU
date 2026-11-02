# GPU 帧诊断

sheng 延迟采集覆盖内存分配、提交、完成处理、CPU 并发、GPU 执行和显示时间线。启动参数：

```text
sheng-log=1 sheng-gpu-trace=1 sheng-gpu-perf=1 sheng-diag-export=240
```

导出在指定的启动日志时间执行一次。这些参数不设置自动重启。保持系统运行至导出完成，再回 fastboot 读取。正常构建默认关闭 GPU 跟踪。

## 保留的证据

| 排查项目 | 记录 |
| --- | --- |
| 前台大块分配 | 内存池、申请量和可用量 KiB、backing 句柄、复用或新分配、页准备、设备锁耗时及调用栈。 |
| 后台内存预留 | 相同的内存操作编号和池信息，区分前台与 room worker。 |
| 提交前延迟 | command 创建与 commit、编码批次入队与执行、慢编码调用、runtime 转换、调度交接和 Vulkan 提交。 |
| 释放及完成处理 | 延迟物理释放、资源和所有者析构、GPU 等待返回、状态处理、回调、保留资源释放和最终准备。 |
| 后台并发及异常 | 进程 CPU 时间、各核占用、触摸区间、目标线程及服务对端调用栈、Mach 请求与回复、异常寄存器、镜像 UUID 和退出原因。 |
| GPU 绘制耗时 | 每个 pass 的硬件耗时、尺寸、渲染模式、附件条件、着色器指标、提交与 fence，以及有效 A7XX 计数器区间。 |
| 显示上游空档 | 验证、GPU 等待、flip、latch、retire 和 blank，与渲染线程及服务对端等待关联。 |

记录同时携带内核、Metal、Turnip 构建身份、进程名、运行配置、队列和环切换，以及采集覆盖计数。

## 采集策略

GPU 跟踪排除纹理与 view 清单、颜色转换细节、像素样本和屏幕图像，保留 command、pass 和同步关联。重复的未完成显示查询只保留状态变化、100 毫秒心跳和省略次数，完成结果保留。runtime 的空闲休眠、唤醒及全局调度轮次在写入前过滤。

IPC 保留被跟踪的请求、匹配的接收和回复端口返回。未配对的接收只计数。跟踪表有固定容量且不阻塞；表满或回复端口存在歧义时增加覆盖计数。重复 IPC 流水和通用 IOKit、GPU 调用环不采集，命令提交耗时及分配专用驱动阶段保留。

低于 250 微秒的快速资源释放记录省略，完成回调保留配对记录。CPU 占用、进程时间、慢编码调用和内核等待采样提供上下文，不运行独立的 2 毫秒渲染线程暂停采样器。

LAT1 为异常、退出原因和进程身份保留独立的 32,768 个槽位，普通延迟事件使用 491,519 个槽位，另有一条汇总记录。高频普通事件不会覆盖异常区。汇总记录包含两区的产生量与保留量、未配对 IPC 和跟踪失败数，解码器先报告覆盖情况。

## 导出内容

导出器优先保留完整的 backboardd `frames.trace`，再安排 CPU、分配、触摸和内核时间线。相关服务及小组件进程各保留最多两份崩溃报告，报告总预算为 8 MiB。当前轮异常现场通过独立异常区保留。

导出不包含着色器缓存清单和预热流水、框架文件、通用统一日志、截图及像素网格。周期文本槽只记录采集身份和时间，消息缓冲副本只保留异常、内存压力及相关服务诊断。未能容纳的文件列在 `diag-skipped.txt`。

## 读取与解码

在 UniXNU-sheng 或解析后的 sheng 构建树执行：

```sh
fastboot boot /path/to/sheng-linux-log.img
python3 scripts/read-sheng-log.py --wait 60 --out /path/to/logs
```

读取器将设备送回 fastboot，并生成 `diag/gpu/events.jsonl`、command 与 fence 的明确关联、`diag/latency.jsonl`、延迟分析及前端记录。已有文件可单独解码：

```sh
python3 scripts/decode-gpu-trace.py RUN/diag/files
python3 scripts/decode-sheng-latency.py RUN/diag/files/kernel.latency.bin --out RUN/latency.jsonl --frames RUN/diag/files/private/var/mobile/Library/Caches/com.apple.backboardd/m2v/frames.trace
```

LAT1 使用 16 字节头和 72 字节记录。事件 34 汇总两个保留区；事件 33 将收到的回复关联到请求。GPU 显示等待记录携带省略的重复查询次数。前端文件保留完整 command 摘要、批次与提交阶段、内存决策和逐 pass 硬件时间。

CPU 事件使用内核运行时间，GPU pass 使用硬件时钟。同一硬件时钟内可以计算耗时，绝对时间与 CPU 对齐需要校准。关联使用明确编号。触摸操作区间与匹配场景单独统计，静置和锁屏切换分别分析。

GPU DCVS 和诊断开启时，`sheng-gpu-perf=1` 采集 19 个 A7XX BR 计数器。原始值携带选择器回读、撕裂读取、复位和抢占有效性，解码器只对有效区间计算增量。计数器描述全局 GPU 区间，pass 时间线提供负载上下文。

## 检查

```sh
python3 scripts/check-gpu-trace.py
python3 scripts/check-native-adreno-scheduling.py
```

主机检查覆盖传输前的事件筛选、重复查询合并、请求回复配对、采集覆盖、异常隔离、runtime 阶段筛选及解码格式。目标 ABI 检查在准备好的 sheng iPadOS 27 构建树中编译受影响的内核、显示和 Metal 组件。
