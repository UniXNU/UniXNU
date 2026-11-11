# SweetAdreno

面向小米 10（umi，SM8250）的 Adreno 650 内核 GPU 驱动。它通过 GMU 与 RPMh 为 GPU 上电，由 TrustZone 验证 zap shader，启动命令处理器，并管理缓冲对象、栅栏和按应用的 GPU 内存上限。`SweetAdrenoUserClient` 为 Mesa turnip 提供接口，Metal→Vulkan 桥（metal2vulkan）让 CoreAnimation 和 Metal 应用运行在其上。

| 仓库 | 维护者 | 范围 |
| --- | --- | --- |
| [ios-umi](https://github.com/qcom-toolbox/ios-umi) | [qcom-toolbox](https://github.com/qcom-toolbox) | [XNU 补丁 0160–0200、0239–0251](https://github.com/qcom-toolbox/ios-umi/tree/main/xnu/patches)；[turnip 与 metal2 用户空间](https://github.com/qcom-toolbox/ios-umi/tree/main/phone) |

## 状态

iOS 16.7.16（20H392），2026-11-06：GPU 绘制界面和所有 Metal 应用（含 Safari）。Safari 地址栏和 App 资源库模糊效果仍有异常。 设备页面：[小米 10 — iOS 16](/zh/devices/umi-qcom-toolbox)。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录驱动及其状态，不接管维护。
