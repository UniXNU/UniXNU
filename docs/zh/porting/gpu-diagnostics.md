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
