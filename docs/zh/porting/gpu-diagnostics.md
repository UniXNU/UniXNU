# GPU 帧诊断

参考延迟采集只记录七个帧延迟问题所需的证据：前台分配、后台预留、提交前延迟、释放与完成处理、后台并发与异常、GPU pass 耗时、显示更新空档。启动参数：

```text
log=1 gpu-trace=1 gpu-perf=1 diag-export=240
```

导出在指定的启动日志时间执行一次。这些参数不设置自动重启。保持系统运行至导出完成，再回 fastboot 读取。正常构建默认关闭 GPU 跟踪。

## 保留的证据

| 排查项目 | 记录 |
| --- | --- |
| 前台大块分配 | 内存池、申请量和可用量 KiB、backing 句柄、复用或新分配、页准备、设备锁耗时及调用栈。 |
| 后台内存预留 | 相同的内存操作编号和池信息，区分前台与 room worker。 |
| 提交前延迟 | command 创建与 commit、编码批次入队与执行、慢编码调用、runtime 转换、调度交接、Vulkan 提交，以及渲染服务编码线程每 4 ms 的采样。 |
| 释放及完成处理 | 延迟物理释放、资源和所有者析构、GPU 等待返回、状态处理、回调、保留资源释放、最终准备，以及完成线程每 4 ms 的采样。 |
| 后台并发及异常 | 进程 CPU 时间、各核占用、最忙线程、异常寄存器、镜像 UUID、退出原因、指定服务的崩溃报告，以及共享区 unnest 及其内核和用户态调用者。 |
| GPU 绘制耗时 | 每个 pass 的硬件耗时、尺寸、渲染模式、附件（surface、尺寸、格式、load/store）、着色器指标、提交与完成、GPU 调频投票和有效 A7XX 计数器区间。 |
| 显示更新空档 | 校验、GPU 等待、flip、latch、退役和 blank；渲染服务渲染线程和 SpringBoard 主线程每 4 ms 的采样；阻塞线程的等待对象和 Mach 对端。 |

分析区间以触控上报时间为界。

## 不开追踪时的板级行

`log=1` 加 `log-gpu=1` 时，板级日志每个槽位都会输出下列行，不需要 `gpu-trace`。
`diag=1` 保留这些行，并以 `[diag msgs]` 加上每轮新增的内核消息中与延迟有关的行。

| 行 | 内容 |
| --- | --- |
| `[gpu jobs]`、`[gpu long]`、`[gpu slow]` | 超过 8、16、33、100 毫秒的任务数，最长的 8 个任务，以及最近超过 8 毫秒的任务，各带进程、队列、环、优先级、IB 数量和大小。`gpu-timeline=1` 时时长取自 CP 时间戳，否则是驱动时钟给出的上限。 |
| `[gpu kick]` | 第一次等待超时、停顿处理时和 500 微秒后 CP 的 IB 位置，以及任务何时完成。位置始终不动是 CP 卡住，有移动则是任务本身长。 |
| `[gpu pool views]` | 通过内核"最后一个映射消失"通知跟踪的池映射，以及归还给池的页面。 |
| `[log round]` | 板级日志写入线程最近一轮和最长一轮的耗时及最慢的步骤。一轮超过 10 秒会写入内核日志，panic 时会记下当时所在的步骤。 |

`gpu-audit=1` 打开对已提交 IB 和同步缓冲的 CPU 缓存行审计。审计只负责发现残留的缓存行，
写合并的修正每次提交都会执行。

## 采集策略

内核 GPU 环只保存提交、完成、显示到达、显示 fence 和 latch、构建标识，以及渲染服务的渲染、编码、完成线程标识。其他进程不写入。渲染服务的其余记录写入自己的 `frames.trace`，不再每条记录一次系统调用。

不采集 Mach 消息流、user client 调用环、连续物理内存环、逐触点触控记录、dispatch 跟踪、队列优先级、环切换、重启和卡顿行、其他进程的 pass 与管线记录、状态与遥测行、截图和像素样本。

短于 250 微秒的资源释放不记录。完成回调和所有者回调保留成对记录。

LAT1 为异常、unnest、退出原因和进程身份保留 32,768 个槽位，普通延迟事件使用 491,519 个槽位，另有一条汇总记录。普通事件不能覆盖异常区。

## 导出内容

导出 `gpu.trace.bin`、`kernel.latency.bin`、`kernel.rings.txt`（swap 环、GPU 时间线、采样目标、进程名、scanout 等待）、`kernel.boalloc.bin`、`kernel.cpus.bin`、`kernel.ptime.bin`、`kernel.touch.bin`、`kernel.client.bin`、backboardd 的 `frames.trace`，以及每个指定服务或小组件进程最多两份崩溃报告，总计不超过 8 MiB。消息缓冲只保留异常、内存压力和指定服务的行。`diag-skipped.txt` 列出未放入的文件和 dasd 模型资源的查找结果。

## 读取与解码

在参考设备仓库或其目标构建树中运行：

```sh
fastboot boot /path/to/linux-log.img
python3 scripts/read-sheng-log.py --wait 60 --out /path/to/logs
```

读取器让设备回到 fastboot，并写出 `diag/gpu/events.jsonl`、`diag/latency.jsonl`、分析结果、前端记录、触控区间，以及只含触控区间的 `*.touch.*` 文件。解码已保存的文件：

```sh
python3 scripts/decode-gpu-trace.py RUN/diag/files
python3 scripts/decode-sheng-latency.py RUN/diag/files/kernel.latency.bin --out RUN/latency.jsonl \
  --frames RUN/diag/files/private/var/mobile/Library/Caches/com.apple.backboardd/m2v/frames.trace \
  --touch RUN/diag/files/kernel.touch.bin
```

LAT1 为 16 字节头加 72 字节记录。事件 35 和 36 是 unnest 的范围、用户态寄存器和内核调用者；其用户态调用栈以相同编号的异常事件 8、9、12 给出。客户端采样记录在 state 第 12-13 位标出采样角色（1 渲染、2 编码、3 完成）。

sheng 采样器持有目标线程的调度锁，在线程已切出、处于等待状态且未进入终止流程时才回溯其内核栈。内核栈为空可能表示线程仍在切出，或保存的寄存器不可用。样本中仍保留等待事件和线程状态。

CPU 事件使用内核 uptime。GPU pass 时间戳使用硬件时钟，可在该时钟内计算耗时，与 CPU 事件的绝对对齐需要校准。

`gpu-perf=1` 启用 19 个 A7XX BR 计数器、GPU 调频和诊断。差值只使用有效区间。计数器描述全局 GPU 区间，pass 耗时提供负载上下文。

sheng 使用 `cpufreq=4` 时，可按内核运行时间把 `kernel.cpufreq.bin` 中的调频目标和 EPSS 读回值与翻屏对齐。CPU 0 至 2、3 至 6 和 7 分属三个调频域。`kernel.client.bin` 中 peer 为 −2 表示在目标核上中断正在运行的线程，取得了当时的用户态 PC 和 LR。当 CLI1 头部标志位 1 置位时，这些样本的 wait 字段保存实际执行的 CPU 编号。旧版精确样本没有核编号。`cs-exact=0` 关闭跨核采样。同时设置 `cs-exact=1 cs-profile=1` 时，跨核采样只中断 SpringBoard 主线程。板级采样使用两个空闲的 Arm PMUv3 计数器记录当前核心的 EL0 退休指令数和周期数，XNU 通用 CPU 计数器仍关闭。日志区分未暴露 PMU、寄存器访问陷入、事件不足和计数器已占用。计算每周期指令数时，只使用同一线程在同一核心上、上下文切换计数相同的相邻样本。

该配置还记录 SpringBoard 主线程耗时至少 250 µs 的 Mach 调用，包括目标 PID、消息 ID、接收开始时间和返回状态。普通接收没有指定发送者。导出时仍未返回的调用会单独标记。使用 `python3 scripts/sheng-springboard-profile.py kernel.latency.bin` 解码这些记录和采样耗时。

在设备仓库运行 `python3 scripts/sheng-latency-report.py RUN/diag --frames-only`，可仅用 HID 和翻屏记录比较不同启动的上报节奏和显示帧间隔。筛选持续上报区间时也会检查两端翻屏到相邻 HID 报告的间隔。

## 检查

```sh
python3 scripts/check-gpu-trace.py
python3 scripts/check-native-adreno-scheduling.py
```
