# Ath12kWifi

Ath12kWifi 在 XNU 上运行 Linux 的 ath12k、mac80211 和 cfg80211，
通过 MHI、QRTR 和 QMI 启动设备，使用用户态 wpa_supplicant 2.12
完成 SME/WPA 认证。普通网络数据包在内核中传输。

| 字段 | 值 |
| --- | --- |
| 仓库 | [UniXNU/Ath12kWifi](https://github.com/UniXNU/Ath12kWifi) |
| 源码 | 固定版本的 Linux v7.0.14、配套头文件和 supplicant 2.12 |
| 板级输入 | 电源、PCIe、BAR、MSI、DMA、固件和网络接口 |
| 原生接口 | `include/nw_abi.h`、`org.unixnu.wifi.control` |
| 已选认证类型 | 开放网络、支持 PMF 的 WPA2-PSK |

按[网络适配流程](/zh/porting/network)准备板级输入并接入构建，
依赖项见[组件目录](/zh/reference/components)。

## 运行路径与性能

生产构建在 ath12k 之前启动 cfg80211/mac80211，使用主线 station
实现。原生控制通道在无线工作线程上串行处理扫描、认证、关联、密钥、
EAPOL 和无线电命令，通过所有者编号与连接代次匹配当前请求。

supplicant 负责密码派生、握手和换钥，运行配置保存在内存中；wifid
负责选择网络并提供系统保存的凭据。无线电打开后等待网络选择，
控制服务退出时释放所属接口。

mac80211 负责聚合、重排序、FQ 和 AQL。DMA 克隆和 A-MSDU 分片
共享存储；发送从保留的 mbuf 直接复制到 DMA，接收从分片复制到对齐的
缓存 mbuf，每批提交最多 64 帧。NAPI 每轮预算为 256 包或 2 ms，
工作队列每轮为 64 项或 2 ms。MSI 和待处理期限控制线程休眠，
PHY 速率与 RSSI 直接读取已有缓存。

## sheng 的 iPadOS 27 集成

WifiProbe 提供板级硬件操作，WifiNet 提供 en0 和 Apple80211。
WCN7850 导出为 `/arm-io/wlan`，满足 24A446 系统 wifid 服务的
设备树条件。Wi-Fi DMA 窗口为 128 MiB。

签名后的 supplicant 通过 Data 支持的只读映射运行于
`/usr/libexec/unixnu-wpa_supplicant`，配置位于
`/private/var/ngpu/etc/wifi/`。打包时保留原有系统任务，合入独立
服务任务，通过 Apple `plutil binary1` 序列化 launchd 缓存，
同时打包匹配的独立签名和信任哈希。

固件在 addon 解包完成后通过 VFS 从
`/private/var/ngpu/firmware/ath12k/WCN7850/hw2.0/` 加载。
板级 `package/WifiFirmware.h` 统一定义加载与打包路径，
`firmware/wcn7850/manifest.json` 固定文件长度和 SHA-256。

WifiNet 接受 592 字节和 656 字节关联请求。24A446 的异步结果为
完整初始化的 540 字节，结果和有效标志位于 0x214/0x218。
明确的连接请求在端口授权后完成；取消只结束一次待完成请求，
无结果的连接在 30 秒后超时。断开和关闭无线电会发送 BSD 与
Apple80211 断链事件。

RSSI 来自关联 BSS，并每秒从 peer 缓存更新一次；变化至少 3 dB
时通知系统，SNR 最小为零。

| 设置 | 当前行为 |
| --- | --- |
| `sheng-wifi=5` | 启动主线 Wi-Fi 栈 |
| `sheng-wifi-aj=0` | 由设置页面和 wifid 选择网络 |
| `log-wifi=1` | 开启 Wi-Fi 诊断 |
| `log-gpu=0 log-display=0` | 跳过 GPU 和显示诊断采集 |
| 自动重启 | 当前临时启动镜像已关闭 |

## 验证状态

在 Ath12kWifi 中按改动运行相关检查：

```sh
python3 tools/fetch-sources.py --check
python3 tools/test-mainline-runtime.py
python3 tools/test-supplicant.py
python3 tools/test-cfg80211-control.py
python3 tools/check-mainline-link.py --build-report FILE --kernel FILE
```

使用模拟无线电操作的主机测试已通过 ASan/UBSan，核心生命周期
释放全部 287 次跟踪分配。生产审计覆盖 125 个对象和 13 个 XNU
导入，缺失导入和重复定义均为零。板级检查覆盖 Apple80211、事件
分配、接收批处理和 VFS 读取；内核、payload、签名、固件与启动镜像
检查均通过。

设备已验证 Wi-Fi 开关、SSID 扫描、WPA2 关联、DHCP、网络流量和
连接结果通知。当前待实测：取消和超时收尾、信号显示、Data 固件
启动，以及吞吐、抖动和发热。详见[sheng 网络记录](/zh/devices/sheng#network)。
