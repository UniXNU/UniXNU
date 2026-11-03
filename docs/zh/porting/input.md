# 触控与按键适配

先完成[显示几何参数](/zh/porting/display)和[中断/DMA 配置](/zh/porting/platform)。
记录触控芯片、固件、矩阵尺寸、物理方向、总线连接、复位/中断引脚及 OS HID ABI。

实现后按[驱动接入步骤](/zh/porting/drivers#build-integration)连接初始化调用、归档配方和 OS ABI，
再执行本页对应的硬件验证。

## 源码与接口 {#source-map}

以下链接固定到已核对的源码版本。使用所选 SoC、组件和 OS 版本核对接口；
链接的设备源码提供板级集成示例。

| 实现部分 | 源码 | 阅读与实现内容 |
| --- | --- | --- |
| 总线与传感器 | [GeniSpi.h](https://github.com/UniXNU/QcomGeniSpi/blob/eac47baefe6a5d2368a70351e6ad1b6361bedbe2/GeniSpi.h), [NvtProtocol.h](https://github.com/UniXNU/ShengNovatekTouch/blob/a1a6f2b1912b3cde2dcbe96439e5833b9ab250f4/NvtProtocol.h#L24) | `nvt_bus`、芯片识别、固件下载和帧读取 |
| 触点处理 | [NvtTouchCore.c](https://github.com/UniXNU/ShengNovatekTouch/blob/a1a6f2b1912b3cde2dcbe96439e5833b9ab250f4/NvtTouchCore.c) | 所支持传感器的矩阵处理与触点跟踪 |
| 板级集成 | [TouchBoard.h](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/TouchBoard.h), [TouchProbe.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/TouchProbe.cpp) | 电源/复位、传输回调、中断处理与坐标 |
| OS 报告 | [NativeHidInput.cpp](https://github.com/UniXNU/ShengHidInput/blob/5f3a37cec0c3fc4234b10726b25489a55f0d77ef/NativeHidInput.cpp#L125), [ButtonProbe.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/ButtonProbe.cpp) | `IOHIDDevice`、报告描述符、一致的触点快照和按键事件 |

## 1. 选择传输与传感器协议

阅读 [QcomGeniSpi](/zh/drivers/qcom-geni-spi)、
[ShengNovatekTouch](/zh/drivers/sheng-novatek-touch)和 [ShengHidInput](/zh/drivers/sheng-hid-input)。


不同传感器需要实现其识别、固件和报告协议。复用 Novatek 协议但更换总线控制器时，
实现 `nvt_bus` 所需的传输与延时回调。

实现 `nvt_bus.xfer` 时保持整次全双工传输期间片选有效，按 `NvtProtocol.h` 提供调用方拥有的缓冲区和延时回调。
按顺序调用 `nvt_identify`、`nvt_fw_parse`、`nvt_download_firmware`、`nvt_read_frame`。
每步检查返回码；固件下载失败时保存阶段、CRC 和 SRAM 回读诊断，再处理下一次重试。
将解码后的触点快照交给 HID 层，发布时保持坐标、ID 和触点数量来自同一帧。

## 2. 适配板级路径

1. 根据目标 DTS 和时钟/引脚定义设置控制器窗口、总线模式/速率、GPIO、中断和 SMMU stream。
   `TouchBoard.h` 提供板级数据布局参考。
2. 实现电源/复位控制，确认引擎固件、引脚和时钟。
3. 按目标 SMMU context 设置 DMA 寻址和缓存维护。
4. 读取芯片 ID，再加载固件并确认返回的几何参数。
5. 解码完整帧，将坐标变换到显示方向。
6. 检查稳定接触 ID、多点、边缘行为和抬起事件。

Novatek 处理核心使用 40 × 60 矩阵。修改固件或处理核心时核对几何尺寸和边界。
固件提取由设备的 `scripts/gen-touch-firmware.py` 与私有文件清单管理。

参考探针参数 `sheng-touch=1`、`2`、`3`、`4` 分别选择资源检查、时钟/引脚、控制器识别和固件/扫描。
先适配该阶段使用的硬件参数，再启用相应阶段。

**预期结果：** 得到显示坐标系中的一致接触帧，包含抬起事件。
HID 层通过序列计数器读取 `native_touch_*`；替换生产方时保留快照一致性。

## 3. 发布 HID 报告

使用选定 kernelcache 确认 IOHIDFamily 方法和对象布局。
参考归档配方使用预链接候选内核与 ABI 记录，见[构建输入](/zh/porting/migration#build-inputs)。
按传感器适配报告描述符、逻辑坐标范围和接触数量上限。

在完整组件列表选择传感器、传输和 HID 组件。参考显示配方链接传感器与总线对象，
HID 配方绑定 OS 接口；`sheng-touch-hid=1` 启用触控发布路径。在目标构建树检查：

```sh
rg -n 'TouchProbe|GeniSpi|NvtProtocol|NvtTouchCore|NvtFirmware' scripts/build-gop-legacy-display.py
rg -n 'native_touch_|ReportDescriptor' drivers/ShengHidInput/NativeHidInput.cpp
```

**预期结果：** OS 收到各接触点正确的按下、移动和抬起报告，UI 手势与面板方向一致。

## 4. 适配实体按键

参考[源码索引](#source-map)中的 `ButtonProbe.cpp` 实现中断采样和 HID 按键事件。

映射目标 GPIO 或 PMIC 输入、极性、所有权、中断路由和应答操作。
仅访问当前执行环境拥有的 PMIC 外设。SPMI 控制器变化时适配 `BootResetCore.h` 辅助接口。
将按下/释放状态接入 HID consumer 报告。参考实现使用 report 2 的 Power、Volume Increment
和 Volume Decrement 位，参数 `sheng-buttons=1` 启用该路径。

**预期结果：** 每次按下和释放产生正确报告，包括长按和同时按键，中断活动保持有界。

## 下一步

按[构建指南](/zh/building)重建，分别记录触控与按键结果，再进入 [GPU 适配](/zh/porting/gpu)。

arm64e 的公开源码构建方法及当前链接、运行时限制见[公开源码驱动构建](/zh/porting/migration#source-drivers)。历史 iOS 17 真机结果不代表该路径已通过验证。
