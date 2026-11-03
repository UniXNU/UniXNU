# QcomBaseband

**HoshinoYumeka（[@chiba233](https://github.com/chiba233)）** 编写的高通基带桥与 SC7180 IPA v4.2 数据通路。

[源码仓库](https://github.com/UniXNU/QcomBaseband)。[适配流程](/zh/porting/baseband)。

组件提供 QMUX/QRTR、QMI CTL、SAHARA 端点、AppleBaseband IOKit 服务及 IPA/GSI/QMAP 代码。板级提供 modem 启动、固件、电源、DMA、GLINK/QRTR 和 rmtfs。

`baseband/QcomBaseband.h` 定义传输挂钩。`scripts/build-qcom-baseband.py` 使用所选 XNU 的编译记录构建桥接归档；`--coachz` 加入 SC7180 IPA 接线。输出为 `build/qcom-baseband/libQcomBaseband.a`。

Coachz 示例能显示 IMEI、ICCID，有效 SIM 已完成 LTE 漫游注册与 CS/PS 附着；重新插拔 SIM 后显示运营商和信号格，数据口绑定已成功。`pdp_ip` 收发和可用的蜂窝数据会话仍待完成。eSIM Tape/UIM 桥的卡状态指示和旧版 GetCsn 主机用例仍未通过，实机开通仍待验证。没有蜂窝基带的设备可跳过此组件。

[组件目录](/zh/reference/components)
