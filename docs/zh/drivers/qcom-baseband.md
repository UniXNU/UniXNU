# QcomBaseband

**HoshinoYumeka（[@chiba233](https://github.com/chiba233)）** 编写的高通基带桥与 SC7180 IPA v4.2 数据通路。

[源码仓库](https://github.com/UniXNU/QcomBaseband)。[适配流程](/zh/porting/baseband)。

组件提供 QMUX/QRTR、QMI CTL、SAHARA 端点、AppleBaseband IOKit 服务及 IPA/GSI/QMAP 代码。板级提供 modem 启动、固件、电源、DMA、GLINK/QRTR 和 rmtfs。

`baseband/QcomBaseband.h` 定义传输挂钩。`scripts/build-qcom-baseband.py` 使用所选 XNU 的编译记录构建桥接归档；`--coachz` 加入 SC7180 IPA 接线。输出为 `build/qcom-baseband/libQcomBaseband.a`。

Coachz 示例能显示 IMEI、ICCID，有效 SIM 已完成 LTE 漫游注册与 CS/PS 附着；冷启动后直接显示运营商和信号格，数据口绑定已成功。ABM 接收队列每通道最多暂存 1024 帧。桥接层提供卡内 ICCID/IMSI，SIM 已匹配运营商设置包，显示 LTE；运营商包的 PRI/GRI 配置文件被收下并回报完成，CommCenter 缓存配置后不再重启基带，BSP 芯片 ID/序列号查询有应答。蜂窝 IPv4 网页加载通过 raw-IP `pdp_ip0` 至 `pdp_ip3` 与 IPA 适配器完成，PDP 重建后仍可收发；IPv6 数据、APN 编辑和长时间连接待验收。IPv4/IPv6 状态独立跟踪，只读 eSIM 查询使用四项缓存。eSIM Tape/UIM 桥在卡状态变化后保留能力字段，回应旧版初始化，并在下载准备期间保持逻辑通道。主机模型已通过。Coachz 设置中已出现 eSIM，页面显示仍需完善，profile 开通仍待实机验证。没有蜂窝基带的设备可跳过此组件。

[组件目录](/zh/reference/components)
