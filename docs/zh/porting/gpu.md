# GPU 与 Metal 适配

先完成[平台 DMA](/zh/porting/platform)和基础[显示呈现](/zh/porting/display)。
阅读 [Adreno740 运行路径](/zh/drivers/adreno740)与 [AdrenoMetal 接口](/zh/drivers/adreno-metal)。

实现后按[驱动接入步骤](/zh/porting/drivers#build-integration)连接初始化调用、归档配方和 OS ABI，
再执行本页对应的硬件验证。

## 源码与接口 {#source-map}

以下链接固定到已核对的源码版本。使用所选 SoC、组件和 OS 版本核对接口；
`UniXNU-sheng` 中的文件提供板级集成示例。

| 实现部分 | 源码 | 阅读与实现内容 |
| --- | --- | --- |
| 电源与固件 | [NativeAdrenoGmuPlatform.h](https://github.com/UniXNU/Adreno740/blob/4e0314df8ad29d52f6fa3f9383a540adcd618b87/NativeAdrenoGmuPlatform.h#L15), [build-adreno740-kits.py](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/scripts/build-adreno740-kits.py) | `NativeAdrenoGmuPlatform::bind/services`、映射窗口、计时器和固件输入 |
| 提交与内存 | [NativeAdrenoClient.h](https://github.com/UniXNU/Adreno740/blob/4e0314df8ad29d52f6fa3f9383a540adcd618b87/NativeAdrenoClient.h#L14), [NativeAdrenoVm.h](https://github.com/UniXNU/Adreno740/blob/4e0314df8ad29d52f6fa3f9383a540adcd618b87/NativeAdrenoVm.h) | `NativeAdrenoTransport`、BO 生命周期、GPU 映射和完成 |
| OS/前端接口 | [NativeOfflineAccelerator.cpp](https://github.com/UniXNU/AdrenoMetal/blob/454ff2ce83766ce7b3e0f355e83f1d72907708b3/NativeOfflineAccelerator.cpp), [OfflineMetalWire.h](https://github.com/UniXNU/AdrenoMetal/blob/454ff2ce83766ce7b3e0f355e83f1d72907708b3/OfflineMetalWire.h) | 加速器发布及配套前端使用的请求结构 |

## 1. 匹配 GPU 代际与 OS ABI

Adreno740 实现 A740 内核接口。AdrenoMetal 使用该接口、Turnip、metal2vulkan
和选定的 OS GPU/IOSurface ABI。确认目标 GPU 版本，对照寄存器、固件、命令包和内存接口。
其他 GPU 代际需要先实现对应内核后端和编译器支持，再选择前端。

另一块 A740 设备需要收集 GPU/GMU 寄存器、中断、SMMU context 与 stream ID、固件、
电源域、时钟/电压档位、互连投票、RAM 保留区和扫描输出布局，并与选定固件核对。

## 2. 适配电源和固件输入

阅读 [SM8550 平台源码](https://github.com/UniXNU/UniXNU-sm8550-common/tree/main/kits)
和 [sheng package](https://github.com/UniXNU/UniXNU-sheng/tree/main/package)。
`Sm8550Platform` 提供共享 GMU 操作和 command database 处理，
`ShengGmuVotes.c` 与 `ShengGmuVotesSource.h` 提供板级 OPP 和带宽策略。
根据目标电源和 command database 适配这些输入。

sheng 的 `scripts/build-adreno740-kits.py` 嵌入以下本地输入：

| 固件 | 用途 |
| --- | --- |
| `qcom/gmu_gen70200.bin` | GMU 镜像 |
| `qcom/a740_sqe.fw` | 命令处理器固件 |
| `qcom/sm8550/sheng/a740_zap.mbn` | 板级签名 ZAP 镜像 |

配方读取 `.cache/firmware/sheng-gpu/`，核对 `scripts/data/adreno-inputs.json` 中的固定值。
按目标设备已确认的固件修改提取路径与固定值，在 `proprietary-files.txt` 中记录来源。

**预期结果：** 板级电源输入和固件匹配目标 GPU。提交命令前确认 GMU 启动和 HFI 响应。

## 3. 建立内存和命令提交路径

1. 核对 ArmSmmu4K context 所有权、stream 选择、地址宽度和缓存维护。
   使用目标硬件描述中的 GPU 和固件 stream ID。
2. 适配保留内存和 GPU 虚拟地址窗口，确保扫描输出、固件、ring 和客户端分配位于各自拥有的范围。
3. 使用有界任务确认 CP 初始化、ring 推进和 fence 完成。
4. 渲染已知图像并检查结果，再运行 UI 工作负载。
5. 验证客户端退出、映射生命周期和 fence 失败处理。

使用 AdrenoFirmware 的固件/HFI 操作和 AdrenoPM4 支持的命令包编码。
sheng 配方把这些 kit、ArmSmmu4K 和板级投票链接到 `libAdreno740.a`，再通过
`build-adreno740-accelerator.py` 构建 accelerator。创建目标配方时保留该顺序。

**预期结果：** 命令完成、fence 推进、已知图像正确。GPU 结果与桌面呈现结果分别记录。

### 降低映射与提交开销 {#memory-path}

桌面每帧都会分配、映射和释放大量缓冲区，单次调用的开销决定流畅度。Adreno740
和 ArmSmmu4K 遵循以下规则，移植时保持不变：

| 操作 | 规则 |
| --- | --- |
| 对象查找 | 客户端的对象数只受内存限制，通过 handle 索引查找。 |
| 分配 | BO 来自系统内存：不带 task、缓存模式为 write-combined 的可分页 `IOBufferMemoryDescriptor`，由 `prepare()` 锁定。VM 一次批量设置页属性，释放时恢复；客户端视图映射该描述符。只有要求连续内存的调用方才走连续的内核分配。 |
| 映射自有内存 | `ArmSmmu4KLiveMapContextBatchExclusive`：不与已有区间做别名检查。 |
| 映射导入内存 | 已映射的导入都属同一缓存类别，且其页都不在本驱动的 BO 中（覆盖 DRAM 的页位图）时，使用同一调用；否则使用完整检查的批量映射。 |
| 解除映射 | 不超过 512 页时每页一次 TLBIVAL，更多时按 ASID 失效。 |
| 提交 | 不做 TLB 失效。映射只填写无效叶子，解除映射会失效自己的页，上层页表不变。fence 卡住时仍会失效。 |

启动日志的 `[vm map]`、`[vm unmap]`、`[vm kinds]` 和 `[bo memory]` 行给出每种操作的
次数和耗时。修改前后对比这些行。

使用 `NativeAdrenoClient` 接口时，按以下顺序实现一次有界提交：
查询 ABI/能力，分配 BO，将其映射到允许的 IOVA，填写命令，再提交并等待返回的 fence。
通过 `NativeAdrenoTransport.call` 连接实际内核分发端，保留各请求的输入/输出大小。
CPU 读取结果前完成缓存同步；fence 超时时先停止队列并确认 DMA 已停止，再释放 BO 和映射。
在错误返回中保留失败的请求类型、句柄和 fence，便于定位分配、映射或执行阶段。

### 8 位 BGRA 帧缓冲的渲染模式 {#render-mode}

`sheng-fb-bgra=1` 时插件设置 `TU_DEBUG=sysmem,nocb`，所有 pass 在系统内存中渲染。tile 内存里的颜色已是渲染目标写出的字节序，
GMEM 的加载和存储在内存侧必须用恒等 swap 搬运字节；记录的 Mesa 补丁 `turnip-gmem-mutable-swap.patch` 对 resolve、2D 与 3D 存储、
3D 加载做了这一处理。打补丁后锁屏在 tile 内存下与 RGhA 画面一致度为 99.5 %，但每个命令缓冲区的 GPU 时间并不优于系统内存
（均值 17.8 ms、p95 56.1 ms，系统内存为 17.1 与 52.1），主屏仍有一帧红蓝互换，因此默认保持系统内存。
`sheng-tu-debug=` 可用于实验覆盖。

### 定位慢帧的耗时 {#frame-path}

修改之前，先把慢帧拆成各层占用的时间。下面每一段都用主机的 uptime 时钟测量；GPU 的 always-on 计数器通过拟合直线换算到同一时钟。

| 段 | 测量位置 |
| --- | --- |
| 提交到调度器 | 运行时阶段记录（commit、prepared、handed、taken）。 |
| 调度器到提交 | 运行时阶段记录，以及批次被扣住的原因。 |
| 提交到 GPU 开始 | 驱动任务时间线：按进程统计排在前面的任务。 |
| GPU 开始到结束 | 每个任务的 CP 起止时间戳；Turnip 每个 render pass 的时间戳。 |
| GPU 结束到回调 | 驱动的 retire 时间、完成等待线程、completed 回调。 |

sheng 上 iPadOS 27 的测量结果（小组件页、设置、Safari）：

- 驱动锁的等待都在 7 ms 以下。render pass 的 GPU 时间中位数 0.5 ms，全屏 pass 1.1 ms。
- 多数慢帧在 GPU 队列里排在其他进程的任务后面：一个海报扩展提交的任务每个约 77 ms，而队列按顺序执行，不分优先级。
- 运行时中把命令缓冲区送到回调的线程使用默认 QoS：设置 QoS 的代码只在 macOS 上生效。
- 打开设置和 Safari 时，94 到 112 MiB 的内存块锁定需要 281 到 340 ms。

## 4. 构建并加入 Metal

准备匹配的 SDK、编译器依赖和 ABI 输入后，在目标构建树执行：

```sh
python3 scripts/build-turnip-darwin.py --target ios
python3 scripts/build-adreno-metal-plugin.py
python3 scripts/add-gpu-plugin-data.py --publish /path/to/base.dbr /path/to/gpu.dbr
```

加入插件的命令使用 macOS 镜像工具，生成 Data seed 副本。
构建 payload 时将输出传给 `--data-ramdisk`，再重建启动镜像。
如需指定应用进程，还可传入 `--clients NAME,...`。运行时插件名为 `NativeAdrenoMetal`。

核对所选 OS profile 的 sandbox、user-client 和 trust-cache 集成。
Metal 桥接层从不返回 nil encoder：无法编码的 pass 会得到一个命令缓冲区被拒绝的
encoder，因为 RenderBox 会缓存 encoder 的方法。进程的第一个问题写在驱动的进程
文本行上（启动日志中的 `[gpu client text]`）。
AirNir 是离线编译器 kit；运行时前端使用组件页说明的 AIR → SPIR-V → NIR → IR3 路径。

**预期结果：** Metal 设备发现、客户端连接、pipeline 创建、渲染和呈现分别成功。
随画面结果记录固件、编译器和插件版本，分别测量首次 pipeline 编译和缓存复用时间。

### 预热着色器缓存 {#shader-warmup}

pipeline 在第一次被请求时才从 Apple 的 AIR 编译，会让画面卡顿。预先预热缓存，桌面就能直接命中。有两项输入，所有 OS 配置都用同一机制（iOS/iPadOS 17 用 `--target ios`，27 用 `--target ios27`）；只有库列表不同，因为它列出的是该 OS 镜像的库。

1. **预编译列表。** 把 OS 镜像中每个 `.metallib` 的绝对路径按 render server 看到的形式（`/System/Library/...`）逐行写出。放在 `build/prime-list.txt`，`build-adreno-metal-plugin.py` 会把它嵌入插件的 `__DATA,__primelist` 段，`make-gpu-addon.py --prime-list FILE` 把它作为 `addons/NativeAdrenoMetal.primelist` 带上。有列表时 render server 不扫描目录，因为沙盒让它看不到大部分目录。
2. **Pipeline 包。** 启动用 `make-gpu-addon.py --cache-export` 构建的镜像，插件会把缓存目录写进板级日志。用 `scripts/read-sheng-log.py` 读取这次运行，用 `scripts/make-m2vpack.py OUT EXPORT_DIR...` 合并一个或多个导出（靠后的目录优先），再用 `make-gpu-addon.py --pipeline-pack OUT` 带上。插件在运行时打开缓存目录之前先把包导入其中。

预编译的运行方式：

- render server 打开设备 90 s 后在后台线程启动，线程栈 8 MiB。
- 每个 kernel 函数生成一个 compute pipeline；每个 vertex 函数生成一个 render pipeline，配同名前缀的 fragment 函数（`_vert_` 换成 `_frag_`）和一个 BGRA8 附件。之后用其他常量或附件创建的 pipeline 仍按需编译。
- 桌面有动画时等待：250 ms 内超过 8 个命令缓冲区算忙，120 Hz 空闲桌面约提交 6 个。动画结束后再静默 2 s，每次等待最多 10 s，所以桌面一直不安静时仍每 10 s 编译一个 pipeline。
- 进度保存在缓存目录：`prime-done`（已完成的库）、`prime-fn`（未完成库里已完成的函数）、`prime-current`（正在编译的函数）、`prime-bad`（曾使进程结束的函数；启动时发现 `prime-current` 就移入这里）和 `prime.log`。重启后可在有数千个函数的库内部继续。
- 每个已完成条目带构建标识：运行时转换器的构建加 Turnip 库的 `LC_UUID`。重建运行时或 Turnip 会让所有库重新预编译，只重建插件则保留已完成的工作。
- 板级日志的 PR 行显示线程在做什么（编译、等待、打开库）、列表中已完成的库数、已生成的 pipeline 数，以及一次等待内见到的最高提交速率。

**预期结果：** PR 行达到列表中的全部库，第二次启动时相同场景不再出现新的 pipeline 编译。记录列表规模、构建标识以及冷启动和热启动的帧时间。

## 下一步

继续 [Wi-Fi](/zh/porting/network)，或返回[驱动清单](/zh/porting/drivers)。
