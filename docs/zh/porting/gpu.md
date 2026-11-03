# GPU 与 Metal 适配

先完成[平台 DMA](/zh/porting/platform)和基础[显示呈现](/zh/porting/display)。
阅读 [Adreno740 运行路径](/zh/drivers/adreno740)与 [AdrenoMetal 接口](/zh/drivers/adreno-metal)。

实现后按[驱动接入步骤](/zh/porting/drivers#build-integration)连接初始化调用、归档配方和 OS ABI，
再执行本页对应的硬件验证。

## 源码与接口 {#source-map}

以下链接固定到已核对的源码版本。使用所选 SoC、组件和 OS 版本核对接口；
链接的设备源码提供板级集成示例。

| 实现部分 | 源码 | 阅读与实现内容 |
| --- | --- | --- |
| 电源与固件 | [NativeAdrenoGmuPlatform.h](https://github.com/UniXNU/Adreno740/blob/1030485546ef7ebb9abbfb7c17fbca93cca40971/NativeAdrenoGmuPlatform.h#L15), [build-adreno740-kits.py](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/scripts/build-adreno740-kits.py) | `NativeAdrenoGmuPlatform::bind/services`、映射窗口、计时器和固件输入 |
| 提交与内存 | [NativeAdrenoClient.h](https://github.com/UniXNU/Adreno740/blob/1030485546ef7ebb9abbfb7c17fbca93cca40971/NativeAdrenoClient.h#L14), [NativeAdrenoVm.h](https://github.com/UniXNU/Adreno740/blob/1030485546ef7ebb9abbfb7c17fbca93cca40971/NativeAdrenoVm.h) | `NativeAdrenoTransport`、BO 生命周期、GPU 映射和完成 |
| OS/前端接口 | [NativeOfflineAccelerator.cpp](https://github.com/UniXNU/AdrenoMetal/blob/816022307852de7e1741ac05ae9111982318763f/NativeOfflineAccelerator.cpp), [OfflineMetalWire.h](https://github.com/UniXNU/AdrenoMetal/blob/816022307852de7e1741ac05ae9111982318763f/OfflineMetalWire.h) | 加速器发布及配套前端使用的请求结构 |

## 1. 匹配 GPU 代际与 OS ABI

Adreno740 实现 A740 内核接口。AdrenoMetal 使用该接口、Turnip、metal2vulkan
和选定的 OS GPU/IOSurface ABI。确认目标 GPU 版本，对照寄存器、固件、命令包和内存接口。
其他 GPU 代际需要先实现对应内核后端和编译器支持，再选择前端。

另一块 A740 设备需要收集 GPU/GMU 寄存器、中断、SMMU context 与 stream ID、固件、
电源域、时钟/电压档位、互连投票、RAM 保留区和扫描输出布局，并与选定固件核对。

## 2. 适配电源和固件输入

阅读 [SM8550 平台源码](https://github.com/UniXNU/UniXNU-sm8550-common/tree/main/kits)
和 [参考板级 package](https://github.com/UniXNU/UniXNU-sheng/tree/main/package)。
`Sm8550Platform` 提供共享 GMU 操作和 command database 处理，
`ShengGmuVotes.c` 与 `ShengGmuVotesSource.h` 提供板级 OPP 和带宽策略。
根据目标电源和 command database 适配这些输入。

参考配方 `scripts/build-adreno740-kits.py` 嵌入以下本地输入：

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
参考配方把这些 kit、ArmSmmu4K 和板级投票链接到 `libAdreno740.a`，再通过
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

### 调度与内存复用 {#scheduling}

参考实现用 `sheng-gpu-preempt=2` 启用模式 2。高、普通偏高、实时请求进入 ring 0；普通、低、后台和未指定请求进入 ring 1。任务的 GPU role 决定使用前台还是后台请求。队列在优先级变化时保持 FIFO；抢占保存 GMEM 并恢复各环实际执行过的页表。详见 [Adreno740 调度](/zh/drivers/adreno740#调度)。

运行时调度与完成线程在 iOS、macOS 上都使用交互 QoS。渲染线程采用固定调度策略时，编码线程继承它的策略与优先级。

空闲自有图像 backing 可供后续池内分配和专用图像复用。room worker 先取合适的 spare，再申请新块。spare 在十秒后老化，也在分配失败或内存压力下回收。无使用者的普通 backing 可交给 room worker 释放；导入内存和所有者回调保持原有释放顺序。

### 8 位 BGRA 帧缓冲的渲染模式 {#render-mode}

`sheng-fb-bgra=1` 默认设置 `TU_DEBUG=sysmem,nocb`。带有尚未分配 backing 的 lazy transient 附件时，pass 在满足分块渲染条件后使用 GMEM；其余 pass 保持系统内存策略。`turnip-transient-attachments-in-gmem.patch` 在 SYSMEM 覆盖前作出此选择，让 memoryless 附件留在 tile 内存。

`turnip-gmem-mutable-swap.patch` 保持 GMEM 加载与存储的颜色字节序。附件大小、行填充、格式和 load/store 操作参与模式选择。`sheng-tu-debug=` 用于指定对照配置，并发 binning 保持关闭。

Metal 客户端默认使用单采样。`NATIVE_METAL_SINGLE_SAMPLE=0` 保留请求的采样数；纹理类型、pipeline 采样数和 resolve 处理遵循该策略。

### 定位慢帧的耗时 {#frame-path}

开启[帧诊断](/zh/porting/gpu-diagnostics)，用同一命令、分配、fence 和显示请求关联各阶段。CPU 事件使用 uptime；GPU 时间戳通过时钟校准后对齐。

| 阶段 | 证据 |
| --- | --- |
| 创建到 commit | 调用方工作、纹理分配与内存页准备。 |
| commit 到编码 | 批次入队、开始、结束与慢编码调用。 |
| 编码到运行时 commit | surface 刷新与运行时交接阶段。 |
| 运行时 commit 到提交 | prepared、handed、taken、批次等待原因和内核提交。 |
| 提交到 GPU 完成 | 队列与环时间线、CP 时间戳、逐 pass 硬件耗时。 |
| 完成到回调 | 状态收集、前端清理、回调、保留资源释放和 gate 准备。 |
| 显示更新 | validation、fence 等待、flip、latch、退役和 blank。 |

对比相同触摸操作场景，将静止桌面和锁屏切换单列。记录缓存构建标识与预热进度、事件保留时段和省略数量。全局 GPU 计数器描述采样区间，逐 pass 计时确定对应工作。

## 4. 构建并加入 Metal

在准备好 SDK、编译器依赖和 ABI 输入的目标构建树中运行。iOS 17：

```sh
python3 scripts/build-turnip-darwin.py --target ios
python3 scripts/build-adreno-metal-plugin.py --target ios
python3 scripts/make-gpu-addon.py --publish build/gpuaddon.bin
```

iOS 27：

```sh
python3 scripts/build-turnip-darwin.py --target ios27
python3 scripts/build-adreno-metal-plugin.py --target ios27
ADRENO_PLUGIN_DIR=build/adreno-metal-plugin27 python3 scripts/make-gpu-addon.py --publish build/gpuaddon.bin
```

通过 `--gpu-addon` 与 `--owner-trust-cache` 将 addon 和配套 owner trust bundle 交给 payload，并开启板级 addon 加载器（参考实现使用 `sheng-gpu-addon=1`）。保留已有 Data seed，让持久数据与缓存沿用原有身份。详见[打包流程](/zh/porting/packaging)。运行时插件名为 `NativeAdrenoMetal`。

核对所选 OS profile 的 sandbox、user-client 和 trust-cache 集成。
Metal 桥接层从不返回 nil encoder：无法编码的 pass 会得到一个命令缓冲区被拒绝的
encoder，因为 RenderBox 会缓存 encoder 的方法。进程的第一个问题写在驱动的进程
文本行上（启动日志中的 `[gpu client text]`）。
AirNir 是离线编译器 kit；运行时前端使用组件页说明的 AIR → SPIR-V → NIR → IR3 路径。

**预期结果：** Metal 设备发现、客户端连接、pipeline 创建、渲染和呈现分别成功。
随画面结果记录固件、编译器和插件版本，分别测量首次 pipeline 编译和缓存复用时间。

### 预热着色器缓存 {#shader-warmup}

pipeline 在第一次被请求时才从 Apple 的 AIR 编译，会让画面卡顿。预先预热缓存，桌面就能直接命中。有两项输入，所有 OS 配置都用同一机制（iOS 17 用 `--target ios`，27 用 `--target ios27`）；只有库列表不同，因为它列出的是该 OS 镜像的库。

1. **预编译列表。** 把 OS 镜像中每个 `.metallib` 的绝对路径按 render server 看到的形式（`/System/Library/...`）逐行写出。放在 `build/prime-list.txt`，`build-adreno-metal-plugin.py` 会把它嵌入插件的 `__DATA,__primelist` 段，`make-gpu-addon.py --prime-list FILE` 把它作为 `addons/NativeAdrenoMetal.primelist` 带上。有列表时 render server 不扫描目录，因为沙盒让它看不到大部分目录。
2. **Pipeline 包。** 启动用 `make-gpu-addon.py --cache-export` 构建的镜像，插件会把缓存目录写进板级日志。用 `scripts/read-sheng-log.py` 读取这次运行，用 `scripts/make-m2vpack.py OUT EXPORT_DIR...` 合并一个或多个导出（靠后的目录优先），再用 `make-gpu-addon.py --pipeline-pack OUT` 带上。插件在运行时打开缓存目录之前先把包导入其中。

预编译的运行方式：

- render server 打开设备 90 s 后在后台线程启动，线程栈 8 MiB。
- 每个 kernel 函数生成一个 compute pipeline；每个 vertex 函数生成一个 render pipeline，配同名前缀的 fragment 函数（`_vert_` 换成 `_frag_`）和一个 BGRA8 附件。之后用其他常量或附件创建的 pipeline 仍按需编译。
- 桌面有动画时等待：250 ms 内超过 8 个命令缓冲区算忙，120 Hz 空闲桌面约提交 6 个。动画结束后再静默 2 s，每次等待最多 10 s，所以桌面一直不安静时仍每 10 s 编译一个 pipeline。
- 进度保存在缓存目录：`prime-done`（已完成的库）、`prime-fn`（未完成库里已完成的函数）、`prime-current`（正在编译的函数）、`prime-bad`（曾使进程结束的函数；启动时发现 `prime-current` 就移入这里）和 `prime.log`。重启后可在有数千个函数的库内部继续。
- 每个已完成条目带构建标识：运行时转换器的构建加 Turnip 库的 `LC_UUID`。重建运行时或 Turnip 会让所有库重新预编译，只重建插件则保留已完成的工作。
- 从 `prime-done`、`prime-fn` 和 `prime.log` 检查已完成的库与函数。精简帧延迟包不包含这些文件，验证预热时单独读取。

**预期结果：** 当前构建的完成条目覆盖库列表，第二次启动复用相同场景的 pipeline。记录列表规模、构建标识以及冷启动和热启动的帧时间。

## 下一步

继续 [Wi-Fi](/zh/porting/network)，或返回[驱动清单](/zh/porting/drivers)。
