# Adreno740

Adreno740 实现 SM8550 上的 A740 内核 GPU 接口，负责内存映射、命令提交、fence 和 CP/GMU 初始化。设备仓库提供固件、电源投票和显示集成。适配入口见 [GPU 适配流程](/zh/porting/gpu)。

## 运行路径

Metal → AdrenoMetal → metal2vulkan → Turnip → Darwin KMD → Adreno740 → A740。

每个客户端拥有独立地址空间和队列编号范围。GPU 使用 4 KiB SMMU 页。自有 buffer 使用系统内存，导入页保留所有者。分配容量随可用内存变化。映射句柄通过索引查找，解除映射时失效对应转换。

## 调度

| 请求优先级 | 模式 2 使用的环 |
| --- | --- |
| High（0）、normal-high（4）、real-time（5） | ring 0 |
| Normal（1）、low（2）、background（3）、未指定 | ring 1 |

任务的 GPU role 决定采用前台还是后台请求。ring 0 优先；ring 0 空闲，或 ring 1 最早的任务等待超过 250 ms 时，调度 ring 1。超时等待获得的执行时间片为 2 ms，避免立即来回切环。切换完成后重新检查排队中的高优先级任务。显示端使用两个环共同完成的连续 fence 范围。队列在已有任务完成前保持原来的环，改优先级时仍按提交顺序执行。IB 句柄只标识命令存储，不用于推断资源依赖。Turnip 客户端的队列共用一个内核 FIFO，未解析的同步等待生产者提交。

每个环独立记录已排队的上下文和页表。CP 在 `CP_SMMU_TABLE_UPDATE` 后记录实际执行的页表，抢占恢复该快照。切环保存 GMEM，执行性能计数器 SRAM postamble，并保持 GMU keepalive，直到目标环 WPTR 恢复。读指针使用各环自己的 shadow。fence 历史表绕回后，未完成任务仍保留正确的环归属。

参考实现用 `sheng-gpu-preempt=2` 启用模式 2。模式 1 仅将 low/background 请求送往 ring 1，模式 0 使用单环。由 CPU 切换页表时也仅使用 ring 0。切环超时为 1 秒。切换失败后停止抢占，恢复流程在 ring 0 重放待执行任务，诊断记录保留失败信息。

## 构建和验证

在解析后的 iOS 27 目标构建树中设置 `UNIXNU_XNU_ARCH=arm64e`、`UNIXNU_IOS_VERSION=27.0` 后执行：

```sh
python3 scripts/build-arm-driver.py Adreno740
python3 scripts/build-adreno740-kits.py
python3 scripts/check-native-adreno-scheduling.py
```

主机调度检查使用软件寄存器模型运行实际 ring、preemption 和 submit 代码，并开启地址及未定义行为检查。覆盖命令包、GMEM、keepalive 顺序、超时、页表快照、优先级分环、FIFO 和 fence 历史表绕回。上机验证项目包括并发客户端、反复切环、像素正确性和帧间隔。

Metal 接口、缓存和插件打包见 [AdrenoMetal](/zh/drivers/adreno-metal)。

帧诊断保留分配、命令、完成处理及 GPU、显示时间线，像素抓取关闭。使用方法见 [GPU 帧诊断](/zh/porting/gpu-diagnostics)。
