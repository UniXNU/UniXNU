# SweetHIDTouch

面向小米 10（umi，SM8250）的 ST FTM5 触控驱动，经 GENI I²C 与 GPI DMA 通信，由 PM8150B GPIO 5 升压供电，以 HID 数字化仪事件上报。`SweetHIDButtons` 通过 SPMI 从 PM8150 PON 模块上报电源键和音量键。

| 仓库 | 维护者 | 范围 |
| --- | --- | --- |
| [ios-umi](https://github.com/qcom-toolbox/ios-umi) | [qcom-toolbox](https://github.com/qcom-toolbox) | [XNU 补丁 0083–0109](https://github.com/qcom-toolbox/ios-umi/tree/main/xnu/patches) |

## 状态

触控、电源键和音量键可用；锁屏与唤醒可用。 设备页面：[小米 10 — iOS 16](/zh/devices/umi-qcom-toolbox)。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录驱动及其状态，不接管维护。
