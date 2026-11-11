# ios-umi boot shim

打包为 Android boot.img v2 的裸机启动 shim。由原厂小米 ABL 启动，自行建立 MMU、读取实时 FDT，并以生成的 Apple 设备树和启动参数加载 XNU，无需 UEFI。

| 仓库 | 维护者 | 范围 |
| --- | --- | --- |
| [ios-umi](https://github.com/qcom-toolbox/ios-umi) | [qcom-toolbox](https://github.com/qcom-toolbox) | [shim](https://github.com/qcom-toolbox/ios-umi/tree/main/shim)；[ADT 生成器](https://github.com/qcom-toolbox/ios-umi/tree/main/tools/mkadt.py) |

## 状态

可在小米 10 上通过 `fastboot boot` 或刷入 `boot` 启动 XNU；同一镜像根据设备树选择机型。 设备页面：[小米 10 — iOS 16](/zh/devices/umi-qcom-toolbox)。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录驱动及其状态，不接管维护。
