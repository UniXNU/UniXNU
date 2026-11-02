# 基带与移动网络适配

没有蜂窝基带的 Wi-Fi 平板可以跳过本页。在 `porting.toml` 中将蜂窝网络项设为 `not-applicable`，在 `limits` 写明硬件原因。

示例使用 **HoshinoYumeka（[@chiba233](https://github.com/chiba233)）** 编写的 [QcomBaseband](/zh/drivers/qcom-baseband)。它把 iPadOS 的 ABM、BBUpdater 和 CommCenter 接到高通 modem。Coachz 示例使用 SC7180、IPA v4.2 和 iPadOS 17（21H461）。

先完成[平台内存与 DMA](/zh/porting/platform)，确认 modem 型号、控制传输、数据引擎、固件、SIM 接口和 EFS/NV 存储。

## 1. 划分实现层 {#layers}

| 层 | 职责 | 示例 |
| --- | --- | --- |
| SoC 与板级 | 电源、时钟、保留内存、固件启动、中断、DMA、EFS/NV | MBA/MPSS、SMEM/SMP2P、GLINK/QRTR、rmtfs |
| 控制桥 | QMUX 帧、QMI 客户端分配、服务发现和回复路由 | `baseband/coachz_bb_qmux.h` |
| iPadOS 接口 | 基带服务、通道、异步读写和启动交互 | `baseband/coachz_baseband.cpp`、`coachz_bb_channels.h`、`coachz_bb_sahara.h` |
| 数据通路 | IPA/GSI、QMAP mux、系统网卡收发 | `ipa/`、`platform/coachz/coachz_modem.c` |

源码位于 [UniXNU/QcomBaseband](https://github.com/UniXNU/QcomBaseband)。寄存器地址、DMA 布局和固件策略由设备或 SoC 仓库提供。

SC7180 通过 GLINK/QRTR 传输 QMI，桥接层在其上向 iPadOS 发布苹果 PCIe 基带类名。通过 PCIe/MHI 连接的 modem 使用对应的板级传输实现。

## 2. 启动 modem 并建立 QMI {#modem-startup}

1. 记录 modem 电源、复位、时钟、互连请求、中断、固件内存和 SMMU stream。按地址转换模式提供 DMA 地址与缓存维护。
2. 加载板级 MBA/MPSS 固件，提供 EFS/NV 存储，确认 modem 启动和 SMP2P 就绪信号。
3. 建立 GLINK/QRTR，跟踪服务发布与移除，验证 QMI 请求和回复。QRTR 端口、轮询和复位恢复由板级负责。
4. IPA v4.2 示例在 modem 启动前配置 IPA，收到 `ipa-setup-ready` 后建立 GSI 与端点，再通过 QMI 完成 INIT_DRIVER、INIT_COMPLETE。Coachz 在此后启动 modem 的收发通道。

在 `proprietary-files.txt` 记录固件来源、哈希和打包路径。高通 modem 镜像、EFS/NV 内容、供 ABM 使用的苹果 `.bbfw` 是不同的输入。

**结果：** modem 持续运行，QMI 服务响应，IPA 初始化完成。

## 3. 接入 iPadOS 桥接层 {#ios-bridge}

阅读 `baseband/QcomBaseband.h` 和 [Coachz 接线示例](https://github.com/UniXNU/QcomBaseband/blob/main/platform/coachz/README.md)。

1. 发布 `AppleBaseband`、`AppleBasebandPCIControl`，以及每个通道的 `AppleBasebandPCIInterface`。用 `ABPInterfaceProtocol` 设置并匹配 `pbl`、`sahara`、`qmux1`、`qmux2` 等名称。按所选 OS 核对 UserClient 类名、方法号、参数大小和异步完成参数。
2. 提供 `coachz_baseband_configure(send, del_client)`，通过 `coachz_baseband_new_server`、`coachz_baseband_del_server`、`coachz_baseband_qrtr` 转发 QRTR 服务变化和消息，在传输工作线程调用 `coachz_baseband_poll`。
3. CTL 分配 QMI 客户端和本地 QRTR 端口；标准服务消息经 QMUX/QRTR 桥转发，苹果私有服务当前回复 `QMI_ERR_NOT_SUPPORTED`。
4. 加入所选蜂窝 ADT 节点与产品属性，让 launchd 选择蜂窝版 CommCenter。示例使用 `/chosen/coachz-baseband`、`/baseband`、`baseband-chipset = mav16` 和根节点 `compatible = J121AP`，保持显示身份属性不变。按目标 IPSW 与基带 ABI 适配这些身份值。
5. 将苹果固件打包并挂载到 ABM、BBUpdater 读取的位置。示例的 SAHARA 端点接收这段启动交互，高通 modem 继续运行自己的固件。
6. 发布 CommCenter 需要的 PDP 管理服务，分别检查 ABM 启动、QMUX 客户端、SIM 状态、modem 身份和设置中的蜂窝网络页面。

**结果：** CommCenter 与实际 modem 通信，读到 SIM 和设备身份。

## 4. 接通移动数据 {#data-path}

modem 的 `kOnline` 表示无线电已上线。网络注册需要检查 NAS 注册状态、驻留网络和分组业务附着。

配置 WDA 数据格式，将 WDS 会话绑定到 QMAP mux，再建立数据会话。把返回的地址、路由、DNS、MTU 接到 `pdp_ip`。按 mux 将数据送到对应网卡，按 DMA 完成结果归还缓冲区。依次验证发送、接收、断开、飞行模式和 modem 复位。eSIM 还需要 UIM/APDU 与 VINYL 流程。

当前 Coachz 示例能识别 SIM 并显示 modem 固件。现有 EFS 镜像为空，modem 报不出 IMEI，CommCenter 因此保持 SIM 禁用。ICCID、网络注册、`pdp_ip` 数据收发和 eSIM 尚未完成。

## 5. 构建与记录 {#build}

将 `QcomBaseband` 加入设备已有的组件选择。普通归档命令为 `component:QcomBaseband`；Coachz 的 IPA 接线使用内核归档命令 `build-qcom-baseband.py --coachz`。

XNU 构建完成后，在目标构建树运行：

```sh
python3 scripts/build-qcom-baseband.py --coachz
```

输出为 `build/qcom-baseband/libQcomBaseband.a`。配方用 C 编译记录构建 `coachz_ipa_config.c`、`coachz_gsi.c`、`coachz_modem.c`，用 C++ 记录构建 `coachz_baseband.cpp`。`coachz_modem.c` 将命令、RX、modem 实现包含在同一编译单元。

按[驱动接入步骤](/zh/porting/drivers#build-integration)链接归档，连接 IOKit 类初始化与启动调用。在 `porting.toml` 中分别记录 modem 启动、QMI、SIM 身份、网络注册、数据、复位和 eSIM。

继续 [DSP、音频和电源](/zh/porting/power)，或返回[驱动清单](/zh/porting/drivers)。
