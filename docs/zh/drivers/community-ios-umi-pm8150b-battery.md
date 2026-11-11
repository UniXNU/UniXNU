# SweetBattery

面向小米 10（umi，SM8250）的 PM8150B 电量计与充电控制：`IOPMPowerSource` 提供真实电量、电压、电流和充电状态；4.40 V、2.0 A 充电电流，按充电器类型限制输入电流，并检测 QC 2.0 / 3.0。

| 仓库 | 维护者 | 范围 |
| --- | --- | --- |
| [ios-umi](https://github.com/qcom-toolbox/ios-umi) | [qcom-toolbox](https://github.com/qcom-toolbox) | [XNU 补丁 0157、0252](https://github.com/qcom-toolbox/ios-umi/tree/main/xnu/patches) |

## 状态

电池读数可用；墙充可充电。不支持 USB-PD 和 30 W 快充。 设备页面：[小米 10 — iOS 16](/zh/devices/umi-qcom-toolbox)。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录驱动及其状态，不接管维护。
