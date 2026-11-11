# AppleBaseband (X55, umi)

面向小米 10（umi，SM8250）的骁龙 X55 调制解调器支持：PCIe2 探测、BHI/SBL1 与 MHI Sahara 启动至 mission mode、QMI 客户端、TFTP 与 EFS 服务、UIM/USIM 配置以及 WDA/WDS 数据会话。`sweet-telephonyd` 代替 CommCenter，根据调制解调器状态回答 CoreTelephony。

| 仓库 | 维护者 | 范围 |
| --- | --- | --- |
| [ios-umi](https://github.com/qcom-toolbox/ios-umi) | [qcom-toolbox](https://github.com/qcom-toolbox) | [XNU 补丁 0259–0275](https://github.com/qcom-toolbox/ios-umi/tree/main/xnu/patches)；[sweet-telephonyd](https://github.com/qcom-toolbox/ios-umi/tree/main/phone/sweet-telephonyd) |

## 状态

调制解调器可插卡注册 LTE；状态栏显示运营商与信号格。数据会话已建立（IPv4、DNS），尚未传输数据包。不计划支持通话和短信。 设备页面：[小米 10 — iOS 16](/zh/devices/umi-qcom-toolbox)。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录驱动及其状态，不接管维护。
