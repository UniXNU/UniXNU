# SweetAudio

面向小米 10（umi，SM8250）的音频：ADSP 启动、经 APR 的 AFE / ASM / ADM、经 FastRPC 的 audio PD，以及 tertiary MI2S 上的两颗 CS35L41 功放；iOS 通过 `/dev/sweet-audio` 与 `SweetAudio.driver` HAL 插件访问。

| 仓库 | 维护者 | 范围 |
| --- | --- | --- |
| [ios-umi](https://github.com/qcom-toolbox/ios-umi) | [qcom-toolbox](https://github.com/qcom-toolbox) | [XNU 补丁 0215–0232](https://github.com/qcom-toolbox/ios-umi/tree/main/xnu/patches)；[SweetAudio.driver](https://github.com/qcom-toolbox/ios-umi/tree/main/phone/sweet-audio) |

## 状态

铃声和系统声音可从扬声器播放。无麦克风，未使用听筒。 设备页面：[小米 10 — iOS 16](/zh/devices/umi-qcom-toolbox)。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录驱动及其状态，不接管维护。
