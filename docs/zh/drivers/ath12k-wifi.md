# Ath12kWifi

先按[适配流程](/zh/porting/network)准备板级输入、修改源码、接入构建并逐步验证。

Ath12kWifi 实现基于 ath12k 的 Wi-Fi 栈，包含 PCI、MHI、QRTR 和板级接口。
源码包含 QCC2072、QCN9274 和 WCN7850 硬件定义。

| 字段 | 值 |
| --- | --- |
| 仓库 | [UniXNU/Ath12kWifi](https://github.com/UniXNU/Ath12kWifi) |
| 功能 | ath12k Wi-Fi 传输与驱动集成 |
| 板级输入 | PCI 访问、中断、固件和板级回调 |
| 硬件验证 | 在设备页记录具体设备结果 |

选择前阅读组件 README 和 `nw_board` 接口。组件目录记录源码版本、OS 要求、构建
命令和输出。运行组件的主机检查和板级网络验证流程。

## sheng（WCN7850）上的状态

Ath12kWifi 在自己的兼容层（`shim/`）上编译 Linux 的 ath12k、MHI 和 QMI 源码，并加上自己的 station 层（`src/nw_sta.c`：扫描、加入、WPA2-Personal、数据路径）。板级接口是 `include/nw_abi.h`，`tools/prepare.sh` 获取并打补丁驱动源码。UniXNU-sheng 给芯片上电、训练 PCIe0，并把模块作为 `en0` 接到 iPadOS（`package/WifiProbe.cpp`：电源、PCIe0、固件、DMA、MSI、模块线程；`package/WifiNet.cpp`：`en0` 与系统的 Wi-Fi 请求）。

状态：能加入 WPA2-Personal、获得 DHCP、Safari 能打开页面。吞吐量低。

| 启动参数 | 含义 |
| --- | --- |
| `sheng-wifi=5` | 启动 Wi-Fi。没有它模块不会运行。 |
| `sheng-wifi-aj=0` | 启动时不加入网络，由设置加入。 |

### iPadOS 27 服务启动

sheng 的板级 DTS 通过 `unixnu,adt-name = "wlan"` 将 WCN7850 导出为
`/arm-io/wlan`。24A446 原生 `com.apple.wifid` 任务带有
`_LimitLoadToDeviceTree` 条件，launchd 加载前会检查。缺少匹配节点时，
内核的 `join.txt` 路径仍能连接并收发数据，但设置中的 Wi-Fi 页面为空，
开关无法打开。`/chosen/mac-address-wifi0` 和 IOService 网络对象不能满足
这个设备树条件。

27 的默认 payload 参数包含 `sheng-wifi=5`。修改 DTS 后需要重新生成
payload 和 boot 镜像，并检查镜像内的 ADT。sheng 的设置页面可以切换
Wi-Fi 开关并显示 SSID 列表。手动测试镜像应移除 `sheng-autoreset`。

WifiNet 支持 592 字节的旧版关联请求和 656 字节的 24A446 请求，
并在认证前校验凭据。手动 WPA2 关联和 DHCP 已获上机确认。

关闭 Wi-Fi 或断开连接会发布链路断开通知，并隐藏旧连接状态。
重复加入当前网络会回报完成；切换网络会等待旧连接断开后再提交新请求。
认证查询将 WPA2 个人网络报告为 0x10。AddressSanitizer 和
UndefinedBehaviorSanitizer 主机回归测试、内核与 payload 编译、镜像校验
均已通过。当前镜像的加入网络、网络切换、Wi-Fi 图标和密码弹窗行为待上机验证。

吞吐量偏低，仍待排查。使用 `log-wifi=1` 记录加入日志，
使用 `sheng-wifi-aj=0` 关闭驱动自动连接。

### 事实

- 六条 PMU 电源轨各需要 RPMh 的模式、电压和使能请求。缺少模式请求时有两条保持关闭，链路无法训练。
- PCIe0 以 Gen2 x1 到达 L0，端点读到 `17cb:1107`。
- 固件 c2-00259 在按需换页处挂起，固件 c7-00108 可用并被采用。
- 固件报告全零 MAC，由板级按芯片 ID 生成一个。
- 开发时固件从备用的 `oops` 分区读取。
- 扫描不含 6 GHz：它的 59 个被动信道占了 11 秒扫描的大部分时间。
- 固件的 beacon 丢失在 5 秒内仍有帧到达时被忽略。
- 加入和四次握手约 100 ms 完成。
- 关联里没有 HT 和 VHT 时链路为 phymode 11g，约 20 Mbit/s。带上接入点的带宽（80 MHz）但对端条目用本射频的能力时，863 个发送帧中 596 个从未被确认。改用接入点自己的能力后几乎所有帧都被确认。
- 接入点会以 VHT MCS 10/11 发送一些帧，驱动丢弃它们（每次运行约 70 个）。
- 芯片的 MSI 指向无人监视的页时，线程每 1 ms 轮询模块；改为经 PCIe0 自带的 MSI 接收器送到 SPI 141 后，线程在中断之间休眠：16 个向量，空闲时每秒几十次中断。
- 速度测试（5 GHz、80 MHz、-73 dBm）：下行约 12 Mbit/s，上行约 24 Mbit/s，发送丢包低于 1 %。DHCP 在开机后 31 秒内给出地址。
- 系统 Wi-Fi 守护进程接管启动时的加入并一直扫描，直到手动加入。系统无法保存网络密码（钥匙串错误 -25291）。
- 发热的进程是 `coreduetd` 和另一个系统进程，不是 Wi-Fi 线程。

### 猜测

- 吞吐限制在到 `ifnet_input` 的接收路径（每次调用复制一帧）或 TCP 窗口。
- 守护进程离开启动时的加入，是因为该网络没有作为已知网络保存。
- 发热来自系统守护进程和 GPU 路径。

### 计划

1. 在速度测试期间统计每个接收阶段的每秒帧数。
2. 成链地把接收帧交给协议栈，去掉多余的复制。
3. 从文件而不是 `oops` 加载固件，然后恢复 `oops`。
4. 之后：6 GHz、Wi-Fi 6/7 能力、省电。

### 构建

`unixnu build kernel` 用 UniXNU-sheng 的 `scripts/build-ath12k-wifi.py` 编译该模块，源码来自 UniXNU-sheng 的 `drivers/Ath12kWifi` 或 `ATH12K_WIFI_DIR`。
