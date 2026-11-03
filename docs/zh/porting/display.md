# 显示与亮度

先完成[平台与内存](/zh/porting/platform)。收集固件 GOP 地址、大小、分辨率、行跨度、
像素格式和保留内存范围，确认面板、显示控制器、背光控制器及其电源控制方。

实现后按[驱动接入步骤](/zh/porting/drivers#build-integration)连接初始化调用、归档配方和 OS ABI，
再执行本页对应的硬件验证。

## 源码与接口 {#source-map}

以下链接固定到已核对的源码版本。使用所选 SoC、组件和 OS 版本核对接口；
链接的设备源码提供板级集成示例。

| 实现部分 | 源码 | 阅读与实现内容 |
| --- | --- | --- |
| OS 显示接口 | [NativeLegacyDisplay.cpp](https://github.com/UniXNU/GopFramebuffer/blob/cf3b42979a9c44219e7bb149543e6fc3388b58ed/NativeLegacyDisplay.cpp), [OriginalMobileFramebufferABI.h](https://github.com/UniXNU/GopFramebuffer/blob/cf3b42979a9c44219e7bb149543e6fc3388b58ed/OriginalMobileFramebufferABI.h) | provider 方法、请求布局及选定 MobileFramebuffer ABI |
| 帧所有权 | [NativeGOPWire.h](https://github.com/UniXNU/GopFramebuffer/blob/cf3b42979a9c44219e7bb149543e6fc3388b58ed/NativeGOPWire.h#L6), [NativeGOPPresenter.cpp](https://github.com/UniXNU/GopFramebuffer/blob/cf3b42979a9c44219e7bb149543e6fc3388b58ed/NativeGOPPresenter.cpp) | `NGPPresent`、`NGPSwap`、`NGPComplete`：缓冲边界与交换完成 |
| 亮度实现 | [AppleARMBacklight.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/AppleARMBacklight.cpp), [GeniI2c.h](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/GeniI2c.h#L80) | OS 属性与 `geni_i2c_start_write/read`、事件及超时处理 |
| 时序参考 | [DisplayTimingProbe.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/DisplayTimingProbe.cpp) | 目标控制器计数器与刷新测量 |

## 1. 确认固件扫描输出

构建[集成后的 UEFI 固件](/zh/porting/uefi-firmware)，确认菜单显示正确。
将 GOP 参数和帧缓冲范围与固件内存映射、板级 DTS 对照，在内核交接期间保留当前扫描缓冲区。

**预期结果：** 固件画面稳定，颜色和尺寸正确。完成后再启用 XNU 显示后端。

## 2. 适配 XNU 显示后端

阅读 [GopFramebuffer](/zh/drivers/gop-framebuffer)及其 `NativeLegacyDisplay.cpp`、
`NativeGOPPresenter.cpp` 和 `NativeGOPWire.h`。它从 `PE_current_console` 获取帧缓冲，
并接入选定的 MobileFramebuffer 和 IOSurface ABI。

在 [参考板级 package](https://github.com/UniXNU/UniXNU-sheng/tree/main/package) 中检查
`LegacyDisplayProbe.cpp` 与 `DisplayTimingProbe.cpp`。
设备脚本 `scripts/build-gop-legacy-display.py` 使用预链接候选内核验证 ABI 方法，再生成后期显示归档。
按[构建输入](/zh/porting/migration#build-inputs)提供匹配的候选内核和审计文件。

1. 选择 GopFramebuffer 和显示归档配方，保留所需依赖。
2. 启用配方需要的内核配置和初始化调用。参考实现使用 `CONFIG_XNU_NATIVE_LEGACY_DISPLAY=y`
   及相应的 `offline-legacy-*` 参数。
3. 在 CPU 呈现路径中确认像素布局、行跨度、分配大小和缓存处理，检查已知画面能否显示。
4. 确认交换完成通知与 IOSurface 生命周期后再启用 [GPU 呈现](/zh/porting/gpu)。
5. 按目标控制器适配时序读取。参考探针 `sheng-dpu=1` 通过 `DisplayTimingProbe.cpp`
   采样 SM8550 DPU 和双 DSI 计数器。根据实际面板模式设置刷新策略；参考实现用 `sheng-vsync=120` 请求 120 Hz。

对 `NativeGOPWire.h` 路径，先通过 mode 请求读取格式和几何参数，再检查每个呈现缓冲的大小与行跨度。
GPU 交接使用 `NGPSwap.sequence` 跟踪待处理帧，复制完成后用相同序列提交 `NGPComplete`。
交换结束前保留源帧和 IOSurface 引用，超时或失败时完成对应错误处理。

**预期结果：** XNU 发布显示服务、呈现画面并完成交换。分别记录请求刷新率和测得的帧时序。

24A446 适配通过原版 IOSurfaceRoot 工厂创建默认 surface，核对内存和尺寸后将引用交给显示框架。
框架的 `create_default_fb_surface()` 槽返回 void，返回寄存器中的残值不是对象指针。
一次 300 秒启动记录中，三次交换均完成，没有内核 panic，屏幕显示苹果标志。
桌面启动尚未通过验证；应先抓取显示服务和 SpringBoard 的等待链，再判断静止标志是否由帧传输故障造成。

### 读取显示管线 {#dpu-pipes}

修改显示控制器的取图来源前，先读取固件留下的状态。参考实现的 `DisplayTimingProbe.cpp` 提供以下阶段：

| 参数 | 读取内容 |
| --- | --- |
| `sheng-dpu=2` | VIG 0 和 1 的源地址、尺寸、格式和取图设置；CTL 0 状态；两个接口的 tear check；apps SMMU 中的显示流 |
| `sheng-dpu=3` | 另外重写每条管线的当前地址，并测量 CTL flush 的锁存时间 |

参考实现中两条 VIG 管线取同一个 32 位物理地址，右侧管线用自己的源 x 坐标；面板自行
刷新，flush 不需要 start，5.4 ms 内锁存。显示 context bank 起始时关闭地址转换。

直接扫描输出（`sheng-dpu-scanout=2`）为实验功能，默认关闭：它给显示 bank 一个
stage 1 窗口（ShengUfs），让管线直接读取合成器的 surface。任何失败都会回退到 GPU 复制。

窗口的 TCR2 把符号扩展字段（SEP，位 17:15）设为 7，与 arm-smmu 对 AArch64 上下文的
做法一致；SEP 为 0 时，第 31 位为 1 的地址会在第 0 级出错。合成器在命令缓冲被调度时就
提交换帧，而不是在 GPU 完成时，所以显示驱动要等 GPU 写完换帧到达前交给它的所有工作
才翻转（Adreno 驱动导出已发出的最新 fence 和已完成的 fence）。没有这个等待，显示管线会
扫描 GPU 仍在写的 surface，面板闪烁。启动日志行 `[direct scanout]` 给出翻转次数、映射的
surface、latch 时间和翻转等待 GPU 的时间。帧缓冲必须是 8 位 BGRA。

## 3. 确认亮度控制接口

选择目标的 I2C、DSI 命令或 PWM 传输方式及亮度编码。
`AppleARMBacklight.cpp` 提供 KTZ8866 控制器的 OS 服务示例，
`GeniI2c.h` 定义该示例使用的 GENI 传输状态机。

复用前记录目标设备的控制器数量、寄存器编码、亮度范围、I2C 引擎、从地址、引脚、时钟、中断和供电顺序。
使用 DSI 命令或 PWM 背光的设备，需要在面向 OS 的亮度服务下实现相应传输与亮度编码。

## 4. 适配并启用亮度

1. 更新板级引擎映射、时钟投票和中断路由。参考 GENI 路径采用固件加载的引擎代码与时序；
   核对该交接状态，或实现目标所需初始化。
2. 实现目标控制器的亮度编码、写入和回读，按面板连接匹配控制器数量和更新顺序。
3. 使用 GENI 示例时，先调用 `geni_i2c_prepare`，再启动读写，把中断状态交给 `geni_i2c_event`，
   到期时调用 `geni_i2c_timeout`。当前传输完成或取消后再发起下一次传输。
   服务请求在工作循环上处理，确认失败处理后再启用渐变调光。
4. 根据选定 OS ABI 配置 `IODisplayParameters` 亮度范围和 `backlight-control`。
   服务接受 brightness 与 `FadePeriod` 属性。
5. 构建服务和注册封装。参考显示配方包含两者，`sheng-backlight=1` 启用 probe。

在解析后的构建树定位集成点：

```sh
rg -n 'kSeA|kSeB|kSpi|kMaxLevel|backlight-control|FadePeriod' kits/*/AppleARMBacklight.cpp
rg -n 'backlight|GeniI2c' scripts/build-gop-legacy-display.py
```

新设备使用对应 kit 路径，按[构建指南](/zh/building)重建内核、payload 和启动镜像。

**预期结果：** 最低、中间和最高设置有对应回读与可见亮度，渐变调光完成，超时计数稳定。
参考实现的 `native_backlight_stats` 记录发布、请求、回读、中断和失败。
控制器写入与系统 UI 亮度调整分别验证。

## 下一步

分别记录显示与亮度结果，再进入[触控和按键](/zh/porting/input)。
