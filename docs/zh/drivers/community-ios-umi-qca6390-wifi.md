# QCA6390 Wi-Fi (umi)

面向小米 10（umi，SM8250）的内核 QCA6390 Wi-Fi 驱动：PCIe0 与 MHI 固件启动、QMI/WLFW、copy engine、HTC/WMI、扫描、加入网络和数据通路，并提供 `IO80211Controller` station 供 iOS wifid 使用，支持 WPA2-PSK。

| 仓库 | 维护者 | 范围 |
| --- | --- | --- |
| [ios-umi](https://github.com/qcom-toolbox/ios-umi) | [qcom-toolbox](https://github.com/qcom-toolbox) | [XNU 补丁 0113–0154、0201–0203](https://github.com/qcom-toolbox/ios-umi/tree/main/xnu/patches) |

## 状态

wifid 与设置可扫描并加入 2.4 GHz 开放和 WPA2-PSK 网络（传统速率）。不支持 5 GHz 和 WPA3。 设备页面：[小米 10 — iOS 16](/zh/devices/umi-qcom-toolbox)。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录驱动及其状态，不接管维护。
