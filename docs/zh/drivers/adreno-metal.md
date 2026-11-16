# AdrenoMetal

启用 `diag=1` 时，编码批次结束记录（类型 14、阶段 3）的 `d` 字段保存编码线程使用的 CPU 微秒数。将它与配对开始、结束记录的实际耗时比较，可区分计算与等待。`TUC` 行记录 Turnip BO 缓存的查询、命中、插入、淘汰和完整清空次数。

AdrenoMetal 通过 `MTLAddDevice` 发布 Metal 设备。metal2vulkan 将 AIR 翻译为 SPIR-V，Turnip 完成编译，并向 [Adreno740](/zh/drivers/adreno740) 提交任务。固件、电源投票和显示集成由设备仓库提供。

## 渲染和接口

| 项目 | 当前行为 |
| --- | --- |
| MSAA 策略 | 所有客户端的纹理、管线和渲染通道默认使用单采样。resolve 目标接收渲染结果，load 和 store-and-resolve 保留源内容。`NATIVE_METAL_SINGLE_SAMPLE=0` 让进程保留请求的采样数，`1` 强制单采样。 |
| Heap 资源 | buffer 和 texture 的 `makeAliasable` 归还 heap 区间。 |
| 纹理布局 | 创建纹理、查询 heap 大小和创建 view 时保留调用方的 `allowGPUOptimizedContents` 设置。 |
| 纹理通道 | 纹理描述符和 view 保留全部四个 swizzle，包括显式零和一。 |
| 复制和光栅状态 | blit 覆盖指定 mip 和 slice 范围。viewport、scissor 传递完整数组，最多 16 项。 |
| 压缩纹理输入 | 长度为零的 no-copy 压缩纹理按 DroidVM 布局推导大小，使用结束后调用所有者的 deallocator。 |
| 源码编译 | `mathMode` 选择 safe、relaxed 或 fast 算术模式，`mathFloatingPointFunctions` 独立选择 fast 或 precise FP32 函数。旧版选项对象使用 `fastMathEnabled`。 |
| 函数 | 函数常量字典提供名称、索引和类型。函数及计算管线的完成回调返回结果。`specializedName` 用作导出名称，源码查找保留原函数名。 |
| 常量表 | 超过 4 KiB 的动态索引常量表使用共享常量存储。常量指针转换和 GEP 表达式保留偏移。 |
| 内存统计 | 设备用量统计池、独立和导入分配。纹理大小来自实际 backing allocation。建议工作集为 RAM / 4，上限 2 GiB。 |
| 队列容量 | `newCommandQueueWithMaxCommandBufferCount:` 使用 runtime 的未完成缓冲数量限制。未提交缓冲销毁时释放名额，已提交缓冲在完成回调返回后释放名额。 |

渲染通道编码失败时仍返回 encoder，通过 command buffer 报错，支持缓存 encoder 方法的调用方。

## 原生 half 运算

A740 的 half FMA 使用 float32 乘加后转换为 half，正常 half 操作数和结果的误差不超过一个 half ULP。half 除法先将两个操作数按相同的二次幂缩放，使原生除数位于 `[2^-14, 2^14]`：大除数使用 `2^-2`，小除数使用 `2^10`。正常操作数和结果遵循 Vulkan 的 2.5 half ULP 界限，非正规数行为由设备浮点控制决定。

其他适用的 half 运算通过 `RelaxedPrecision` 和 `HalfChainPolicy::AtExits` 使用原生精度。源码枚举的算术清单记录每项运算的 `PrecisionNote`，runtime 策略日志记录实际选用的设备能力。

## 缓存和优先级

相同 UID 的客户端在可写时共用账户 home 下的 `Library/Caches/org.unixnu.metal`。沙箱限制写入时使用私有缓存。`NATIVE_METAL_SHARED_CACHE_DIR` 可指定共享目录，空值关闭共享。缓存覆盖 Apple 前端结果、runtime 产物和 Turnip IR3。并发导入使用独立临时文件，管线日志按进程分开。

`metal-flow=<位>` 选择渲染工作路径。位 1 使用 lowering 线程，位 2 在 commit 线程直接提交；macOS 默认为 3。iPadOS 还支持位 4，用于预热历史管线记录，默认值为 7。

`metal-flow=` 取任一值时，都会在 `FL` 计数变化后写入 os_log，每十秒最多一次。

Turnip 为每个渲染通道选择瓦片内存或系统内存，并发分箱默认打开。`tu-debug=<标志>` 为所有 Metal 进程设置 `TU_DEBUG`：`gmem` 让每个通道都在瓦片内存中渲染，`nocb` 关闭并发分箱。`tum=a` 每八秒在 Turnip 的选择和瓦片内存之间轮换，用于测量。

同一进程的 Metal 逻辑队列共用一个 Vulkan 队列和内核队列。前端汇总存活队列的当前请求，采用其中最高的优先级；队列降级或销毁后撤回提升。getter 返回各队列自身的请求，setter 返回后端是否接受。内核根据任务的 GPU role 选择前台或后台优先级，策略不使用进程名。


已空闲的自有图像内存可供池化和独立图像复用。额外缓存没有字节上限，十秒后过期，遇到内存压力或无法分配新块时提前释放。内存块在 runtime 的释放线程上释放，不占用发起释放的线程，超过队列上限时由发起线程释放。分配失败时先释放保留内存并等待已提交的释放完成，再重试。导入内存和外部所有者回调保留原有释放顺序。首次使用仍可能需要准备新内存页。

## 着色器预编译和诊断

源码与打包：[AdrenoMetal](https://github.com/UniXNU/AdrenoMetal/pull/38)、[UniXNU](https://github.com/UniXNU/UniXNU/pull/271)、[sheng](https://github.com/UniXNU/UniXNU-sheng/pull/107)。

macOS 用户打开 **Shader Cache**，点击“开始”编译系统清单。窗口显示库进度、已编译函数、失败和缺失数量。“停止”会在当前编译结束后停止任务；再次开始时保留成功的 checkpoint 并重试失败条目。工作进程通过管理员授权写入系统共享缓存。关闭窗口后，已启动的任务继续执行。

App 安装在 `/Library/GPUBundles/Shader Cache.app`，sheng lab 同时在 `/Applications` 提供入口。随 macOS 插件构建：

```sh
python3 scripts/build-adreno-metal-plugin.py --target macos27 --no-replay
```

runtime 构建枚举 OS、SystemOS 和 App 中的 `.metallib`。工作进程根据反射的常量和顶点输入，编译默认计算管线及 BGRA8、RGBA16Float 渲染变体。Apple GPU 机器码归档单独计数。一个库的适用变体全部编译成功后，才写入 `prime-done`；输入缺失或变体被拒绝时，结果为未完成。

状态保存在 `/private/var/tmp/NativeAdrenoMetal.cache/shader-cache.plist`，运行锁为 `shader-cache.lock`，checkpoint 与 `prime.log` 保存在同一目录。checkpoint 包含翻译器和 Turnip 标识。各 Metal 客户端通过 `/Library/GPUBundles/NativeAdrenoMetal.cache` 读取共享缓存。

读取状态或汇总导出的缓存：

```sh
'/Applications/Shader Cache.app/Contents/MacOS/ShaderCache' --status
python3 scripts/analyze-metal-prime.py CAPTURED_CACHE_DIRECTORY
```

iPadOS 的渲染服务在空闲时编译清单，通过 `PR`、`PRb` 和 `PRc` 报告进度。

`FP` 记录合并提交与批次数量、创建与复用的 command pool 数量、原位渲染与经过复制的线性通道数量，以及被淘汰的区域管线数量。`CM` 记录 commit 调用次数，以及总耗时、lowering、命令记录、管线等待、锁等待、调度和提交的累计微秒数。在相同受控工作负载内比较计数差值。

使用 `diag=1` 或 `gpu-trace=1` 时，系统缓存还保存有大小限制的 `timing.log`（512 KiB）和 `runtime-policy.log`（64 KiB）。前者记录各 encoder 耗时和至少 8 ms 的 command buffer，后者记录实际设备策略、浮点控制能力和 runtime 路径检查。sheng 的诊断导出包含这两个文件。

导入的 surface 和带行间距的纹理，在设备检查接受其布局与用途后使用 runtime 的原位路径。提交合并与队列共享根据设备支持的能力和提交检查结果选择。空闲资源清理线程等待下一次过期时间。

## 性能验收

固定场景、显示模式、电量范围和温度范围，在采集中记录源码版本和窗口状态。性能目标按以下条件验收：

| 范围 | 目标 |
| --- | --- |
| 着色器覆盖 | 本次启动的全系统 pass 显示完成，全部适用库成功，失败和缺失条目均为零。预热后的场景没有新增编译 miss。 |
| Fast path | 每个策略字段都有设备能力判断记录，支持的原生近似运算保留其精度语义。 |
| 帧间隔 | 持续动画期间，显示间隔的第 99 百分位不超过一个扫描周期，允许时间戳分辨率误差。120 Hz 对应 8.333 ms。 |
| 调度 | GPU 任务就绪后，可消除的调度延迟第 99 百分位不超过 0.25 ms。更长的区间都有标明依赖或瓶颈的 trace。 |
| 硬件吞吐 | 独立算术和带宽探测在相同格式、精度、时钟和温度下，达到本机校准原生吞吐的至少 95%。 |
| 正确性 | 场景完成、输出一致、GPU 故障和恢复次数为零、客户端崩溃次数为零。 |

CPU 和 GPU 时长各自在其时钟域内比较，合并时间戳前先校准。保留每项未达目标的采集结果，据此确定下一项修改。

## 构建和检查

在解析后的 iOS 27 目标构建树中执行：

```sh
python3 scripts/build-turnip-darwin.py --target ios27
python3 scripts/build-adreno-metal-plugin.py --target ios27
python3 scripts/check-native-metal-frontend-host.py
```

正常构建应用记录在仓库中的翻译器、Turnip 补丁，并开启 Mesa 磁盘 shader cache。主机检查覆盖渲染像素、resolve、资源回收、swizzle、复制、回调、队列容量及优先级汇总。上机验证项目是并发客户端下的帧间隔和抢占行为。

设备输入和打包方式见 [GPU 适配流程](/zh/porting/gpu)。

帧诊断保留分配、命令、完成处理及 GPU、显示时间线，像素抓取关闭。使用方法见 [GPU 帧诊断](/zh/porting/gpu-diagnostics)。

启用 `gpu-trace=1` 后，内核事件 65 记录 `iconservicesagent` 获取的 Metal 设备和创建的命令队列。对于含绘制或计算任务的命令缓冲区，最多记录八条 `metal-work`，包含完成状态、绘制次数和计算派发次数。

`wallpaper-freeze=1` 用于隔离壁纸渲染。名字包含 Poster 的渲染进程首次成功绘制并保存至少 200 万像素的 IOSurface 后，保留该输出，拦下后续 command buffer 的 runtime 提交。被拦下的缓冲保持已 commit、未调度状态，继续持有资源和队列名额；此前已提交的工作正常完成。PosterBoard、backboardd 和其他客户端继续提交。此模式默认关闭。

细分延迟记录标出慢编码调用、回调入口地址和资源析构耗时。内核对渲染、编码和完成线程的采样关联上游等待。

`python3 scripts/package-metal-bridge.py OUTPUT.tar.zst --target macos27` 将当前静态库、构建标识和组件源码打包，供 CI 复用。
