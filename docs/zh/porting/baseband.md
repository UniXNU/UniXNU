# 基带与移动网络适配

没有蜂窝基带的 Wi-Fi 平板可以跳过本页。在 `porting.toml` 中将蜂窝网络项设为 `not-applicable`，在 `limits` 写明硬件原因。

示例使用 **HoshinoYumeka（[@chiba233](https://github.com/chiba233)）** 编写的 [QcomBaseband](/zh/drivers/qcom-baseband)。它把 iOS 的 ABM、BBUpdater 和 CommCenter 接到高通 modem。Coachz 示例使用 SC7180、IPA v4.2 和 iOS 17（21H461）。

先完成[平台内存与 DMA](/zh/porting/platform)，确认 modem 型号、控制传输、数据引擎、固件、SIM 接口和 EFS/NV 存储。

## 1. 划分实现层 {#layers}

| 层 | 职责 | 示例 |
| --- | --- | --- |
| SoC 与板级 | 电源、时钟、保留内存、固件启动、中断、DMA、EFS/NV | MBA/MPSS、SMEM/SMP2P、GLINK/QRTR、rmtfs |
| 控制桥 | QMUX 帧、QMI 客户端分配、服务发现和回复路由 | `baseband/coachz_bb_qmux.h` |
| iOS 接口 | 基带服务、通道、异步读写和启动交互 | `baseband/coachz_baseband.cpp`、`coachz_bb_channels.h`、`coachz_bb_sahara.h` |
| 数据通路 | IPA/GSI、QMAP mux、系统网卡收发 | `ipa/`、`platform/coachz/coachz_modem.c` |

源码位于 [UniXNU/QcomBaseband](https://github.com/UniXNU/QcomBaseband)。寄存器地址、DMA 布局和固件策略由设备或 SoC 仓库提供。

SC7180 通过 GLINK/QRTR 传输 QMI，桥接层在其上向 iOS 发布苹果 PCIe 基带类名。通过 PCIe/MHI 连接的 modem 使用对应的板级传输实现。

## 2. 启动 modem 并建立 QMI {#modem-startup}

1. 记录 modem 电源、复位、时钟、互连请求、中断、固件内存和 SMMU stream。按地址转换模式提供 DMA 地址与缓存维护。
2. 加载板级 MBA/MPSS 固件，提供本机的原厂 FSG/EFS/NV 数据。Coachz 从 eMMC 硬件启动分区读取 FSG，并核对设备保存的摘要。确认 modem 启动、设备身份和 SMP2P 就绪信号。
3. 建立 GLINK/QRTR，跟踪服务发布与移除，验证 QMI 请求和回复。QRTR 端口、轮询和复位恢复由板级负责。
4. IPA v4.2 示例在 modem 启动前配置 IPA，收到 `ipa-setup-ready` 后建立 GSI 与端点，再通过 QMI 完成 INIT_DRIVER、INIT_COMPLETE。Coachz 在此后启动 modem 的收发通道。

在 `proprietary-files.txt` 记录固件来源、哈希和打包路径。高通 modem 镜像、EFS/NV 内容、供 ABM 使用的苹果 `.bbfw` 是不同的输入。

**结果：** modem 持续运行，QMI 服务响应，IPA 初始化完成。

## 3. 接入 iOS 桥接层 {#ios-bridge}

阅读 `baseband/QcomBaseband.h` 和 [Coachz 接线示例](https://github.com/UniXNU/QcomBaseband/blob/main/platform/coachz/README.md)。

1. 发布 `AppleBaseband`、`AppleBasebandPCIControl`，以及每个通道的 `AppleBasebandPCIInterface`。用 `ABPInterfaceProtocol` 设置并匹配 `pbl`、`sahara`、`qmux1`、`qmux2` 等名称。按所选 OS 核对 UserClient 类名、方法号、参数大小和异步完成参数。
2. 提供 `coachz_baseband_configure(send, del_client)`，通过 `coachz_baseband_new_server`、`coachz_baseband_del_server`、`coachz_baseband_qrtr` 转发 QRTR 服务变化和消息，在传输工作线程调用 `coachz_baseband_poll`。
3. CTL 分配 QMI 客户端和本地 QRTR 端口；标准服务消息经 QMUX/QRTR 桥转发。桥接层处理 BSP 激活和 VINYL Tape 请求，其他苹果私有请求回复 `QMI_ERR_NOT_SUPPORTED`。激活指示带上服务已开通和卡槽已接受状态。BSP 0xb001 返回 BHI 阶段已报告的芯片 ID 和序列号。运营商包的 PRI/GRI 分段（BSP 0xa000、SetConfig 0xe00d）以下一段段号应答并丢弃，最后一段之后发送 FileTransferStatus 0xa001；CommCenter 随后缓存配置，不再重启基带。
4. 加入所选蜂窝 ADT 节点与产品属性，让 launchd 选择蜂窝版 CommCenter。示例使用 `/chosen/coachz-baseband`、`/baseband`、`baseband-chipset = mav16` 和根节点 `compatible = J121AP`，保持显示身份属性不变。按目标 IPSW 与基带 ABI 适配这些身份值。
5. 将苹果固件打包并挂载到 ABM、BBUpdater 读取的位置。示例的 SAHARA 端点接收这段启动交互，高通 modem 继续运行自己的固件。
6. 发布 CommCenter 需要的 PDP 管理服务，分别检查 ABM 启动、QMUX 客户端、SIM 状态、modem 身份和设置中的蜂窝网络页面。

桥接层每通道为 ABM 暂存最多 1024 帧；每通道前 32 次丢帧记录队列深度与消息头。冷启动和注册时检查丢帧计数。

观察 CommCenter 的 EF_ICCID 与 EF_IMSI 读取，将卡内数据转换为阅读顺序的 BCD，通过激活 TLV `0x42` 与 `0x43` 提供给运营商匹配流程。

**结果：** CommCenter 与实际 modem 通信，读到 SIM 和设备身份。

## 4. 接通移动数据 {#data-path}

modem 的 `kOnline` 表示无线电已上线。网络注册需要检查 NAS 注册状态、驻留网络和分组业务附着。

`coachz_bb_data.h` 在第一个 WDS 客户端绑定前通过 DPM 打开 IPA 硬件端口，配置 WDA raw IP/QMAPv4。它将 WDS/QOS 的苹果 PCIe 端点 `{3, 4}` 转换为 embedded `{4, 1}`，为只带 mux id 的请求补上端点。随后将 WDS 会话绑定到 QMAP mux，再建立数据会话。把返回的地址、路由、DNS、MTU 接到 `pdp_ip`。按 mux 将数据送到对应网卡，按 DMA 完成结果归还缓冲区。依次验证发送、接收、断开、飞行模式和 modem 复位。eSIM 还需要 UIM/APDU 与 VINYL 流程。

Coachz 使用原厂 FSG 后显示 IMEI、ICCID 和 modem 固件。有效 SIM 已完成 LTE 漫游注册与 CS/PS 附着，冷启动后状态栏直接显示运营商和信号格。DPM/WDA 配置与 WDS/QOS 绑定已成功。SIM 已匹配运营商设置包，状态栏显示 LTE，蜂窝 IPv4 网页加载通过，PDP 重建后仍可用。固定版本的 CommCenter 在缺少 Apple postponement ticket 时阻塞 Internet 上下文，[`coachz_cellular_compat.py`](https://github.com/UniXNU/QcomBaseband/blob/main/platform/coachz/README.md#commcenter-compatibility-copy) 生成经哈希核对的补丁副本、签名和 trust cache；固件归档、ADT 摘要和 trust cache 集合携带它们。IPv6 数据、APN 编辑和长时间连接待验收。EFS 写入仍保存在内存中，重启后重新加载原厂数据。

`coachz_bb_pdp.cpp` 由 `coachz_baseband.cpp` 包含，为 QMAP mux 1 至 4 注册 `pdp_ip0` 至 `pdp_ip3`，MTU 为 1492。WDS 绑定、IP family、启动、停止与状态应答分别控制各地址族。在 QRTR/IPA 所属线程实现 `QcomBaseband.h` 中的 `coachz_modem_data_send` 与 `coachz_modem_data_receiver`；Coachz 适配器已提供两者。接口需注册 `PF_INET` 与 `PF_INET6` 的 protocol plumber，使 CommCenter 卸载旧上下文后能重新挂接地址族，初始挂接复用同一回调。分别验证 IPv4、IPv6，以及停止一个地址族后另一个仍能通信。

`coachz_bb_esim.h` 发现真实 eUICC 卡槽，将 VINYL Tape 请求转为 ISD-R 逻辑通道上的 APDU。卡状态应答与指示都保留能力 TLV `0x21`；旧版 GetCsn 返回 `0x204`，完成原版驱动初始化。EID 与能力请求读取 TLV `0x01`，Tape 结果使用 11 字节头。

挑战、认证与下载准备共用所属客户端的通道。终结操作、错误、客户端断开或空闲 180 秒后关闭通道并恢复原卡槽映射。会话恢复查询返回空记录集。四项只读 ES10 缓存复用重复查询的卡片应答，命中时保持物理卡槽映射，状态变更指令清除缓存。主机模型已通过。Coachz 的设置中已出现 eSIM，页面显示仍需完善，profile 开通仍待实机验证。使用已开通数据套餐的 SIM 卡验证蜂窝数据收发。

## 5. 构建与记录 {#build}

将 `QcomBaseband` 加入设备已有的组件选择。普通归档命令为 `component:QcomBaseband`；Coachz 的 IPA 接线使用内核归档命令 `build-qcom-baseband.py --coachz`。

更新 QcomBaseband 时，将 `components.toml` 与主仓库的 `drivers/QcomBaseband` submodule 固定到同一个提交。

XNU 构建完成后，在目标构建树运行：

```sh
python3 scripts/build-qcom-baseband.py --coachz
```

输出为 `build/qcom-baseband/libQcomBaseband.a`。配方用 C 编译记录构建 `coachz_ipa_config.c`、`coachz_gsi.c`、`coachz_modem.c`，用 C++ 记录构建 `coachz_baseband.cpp`。`coachz_modem.c` 将命令、RX、modem 实现包含在同一编译单元；PDP 源码包含在基带 C++ 单元中。

按[驱动接入步骤](/zh/porting/drivers#build-integration)链接归档，连接 IOKit 类初始化与启动调用。在 `porting.toml` 中分别记录 modem 启动、QMI、SIM 身份、网络注册、数据、复位和 eSIM。

继续 [DSP、音频和电源](/zh/porting/power)，或返回[驱动清单](/zh/porting/drivers)。
