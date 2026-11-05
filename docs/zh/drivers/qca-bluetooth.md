# QcaBluetooth

QcaBluetooth 将高通 WCN7850 串口控制器接入苹果蓝牙栈。

[源码仓库](https://github.com/UniXNU/QcaBluetooth)。

## 状态

设备：小米平板 6S Pro（sheng），iPadOS 27.0.1（24A446）。

| 状态 | 功能 |
| --- | --- |
| 可用 | 配对、重启后回连、开关蓝牙、A2DP 播放、AirPods 降噪和电量、与 Wi-Fi 同时使用 |
| 未测试 | 通话和麦克风（HFP/SCO）、休眠唤醒 |
| 不可用 | 依赖苹果厂商命令的功能 |

## 分层

驱动复用固定版本 Linux `btqca.c` 的初始化流程，处理 H4 和 IBS。UART.SK/Skywalk
将 H4 数据交给 `bluetoothd`。扫描、配对、密钥、BLE 和音频协议由苹果系统负责。

GENI 使用四块 2048 字节接收缓冲和一块 4096 字节发送缓冲。硬中断只屏蔽中断线、
唤醒工作线程。接收侧保留未消费的缓冲，满时关闭 RFR；发送侧确认 DMA 完成且串口
排空。IBS 控制字节只插在完整 H4 包之间。关时钟要求接收侧已停止，并已启用硬件
唤醒源。

| Sysctl | 含义 |
| --- | --- |
| `kern.qbt_boot` | 控制器状态 |
| `kern.qbt_power_on` | 读取即启动控制器并返回结果 |
| `kern.qbt_firmware` | 已加载的固件名 |

三者都是只读，因为 BlueTool 的沙盒禁止写 sysctl。连接 UART.SK 也会启动已停止的
控制器。

## 板级集成

板级代码提供 WCN 电源、时钟、引脚、DMA 映射、中断和固件。`WcnPower.h` 为 Wi-Fi
和蓝牙分别记录共享电源的使用票，最后一方释放时关闭电源。

在 sheng 上，`sheng-bluetooth=1` 在 Data 插件安装后启动 UART14 工作线程，绑定
0x898000 的 GENI SE6、中断 493 和 QUP2 DMA 流 0x423。精确的 51.2 MHz 时钟生成
3.2 Mbaud。DMA 缓冲使用与触摸、音频共用的固件管理直通上下文。GPIO79 唤醒已关
时钟的串口。UART 需要启动固件提供协议号为 2 的微码。

板级代码在用户态启动前导出 `/arm-io/bluetooth` 和同名 IOService，带 H4 编码、
波特率和稳定的私有地址。

## 原生适配

iPadOS 27 适配固定匹配一个 `bluetoothd` 二进制：

- 所有产品都按控制器类型零运行，使用标准 HCI 初始化。
- 能力来自 Supported Commands 和 LE Features。广播组数来自 0x203b，上限六组。
- 扩展扫描使用 0x2041 和 0x2042。启动扫描或广播组前先发送随机地址。
- 补丁保留认证修正信息和 PACIBSP 入口。

`payload.runtime` 选择 `build-bluetooth-userspace.py`，打入已签名的 BlueTool、
`bluetoothd`、`QcaBTType0.dylib` 和固定版本固件。只读联合挂载在 `/usr/lib` 和
`/usr/sbin` 下暴露这些文件。Wi-Fi 和蓝牙共用一份签名启动缓存。

配对密钥依赖 keychain，keychain 依赖 [AppleKeyStoreState](/zh/drivers/apple-key-store-state)
的密钥封装。

## 音频

音频覆盖层会遮住系统的 HAL 插件目录。在 `payload.runtime` 的
`audio_system_plugins` 中列出 `BTAudioHALPlugin.driver`，运行时构建脚本会从系统
镜像原样复制该插件。

## 构建与检查

```sh
python3 tools/test-runtime.py
python3 tools/test-geni.py
python3 tools/build-bluetool.py
python3 tools/build-type0.py
python3 tools/check-kernel.py /path/to/tree --record <内核源码的编译记录> \
    --extra-source <板级源码> --board-export <符号>
```

以上在组件目录运行。原生适配的检查见 `native-ios27.md`。sheng 的板级检查在工作区
根目录运行：

```sh
python3 UniXNU-sheng/scripts/check-bluetooth-platform.py
python3 UniXNU-sheng/scripts/check-bluetooth-shared.py
python3 UniXNU-sheng/scripts/check-bluetooth-board.py /path/to/tree
python3 UniXNU-sheng/scripts/check-bluetooth-runtime.py
```

`log-bluetooth=1` 在启动日志的 `[bluetooth]` 行增加初始化信息，`log-bluetooth=2`
增加进程和控制器输出行。

按[运行时输入](/zh/porting/packaging#ios-27-运行输入)提供安装输入，再按
[启动载荷](/zh/concepts/payload)操作。

参考：[Linux](https://github.com/ianchb/sm8550-mainline)、
[Debian sheng](https://github.com/ianchb/debian-sheng)、
[Renoir UART.SK](https://github.com/daimile2/renoir_xnu_bluethooth)。
