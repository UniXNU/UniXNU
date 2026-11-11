# AppleCLCD / AppleARMBacklight (umi)

面向小米 10（umi，SM8250）的显示栈：IOSurface 与 IOMobileFramebuffer（`AppleCLCD`），经显示 SMMU 直接扫描输出，将 1080×2340 AMOLED 呈现为 iPhone X 面板；`AppleARMBacklight` 通过 DSI 发送 DCS 0x51 调节亮度，锁屏时关闭面板，并把夜览映射到 DSPP PCC。

| 仓库 | 维护者 | 范围 |
| --- | --- | --- |
| [ios-umi](https://github.com/qcom-toolbox/ios-umi) | [qcom-toolbox](https://github.com/qcom-toolbox) | [XNU 补丁 0046、0091–0092、0205–0207](https://github.com/qcom-toolbox/ios-umi/tree/main/xnu/patches) |

## 状态

CoreAnimation 帧可显示到面板；亮度滑块、控制中心和夜览可用。 设备页面：[小米 10 — iOS 16](/zh/devices/umi-qcom-toolbox)。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录驱动及其状态，不接管维护。
