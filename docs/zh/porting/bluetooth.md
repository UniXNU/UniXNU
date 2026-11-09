# 蓝牙适配

先完成[平台中断和 DMA](/zh/porting/platform)，并准备[运行输入](/zh/porting/packaging#ios-27-运行输入)。
[QcaBluetooth](https://github.com/UniXNU/QcaBluetooth) 通过 GENI UART 运行 Linux `btqca.c` 初始化，
再经 UART.SK 把 H4 字节传给苹果的 `bluetoothd`。扫描、配对、密钥、BLE 和音频配置文件都由苹果的协议栈负责。

按[驱动接入步骤](/zh/porting/drivers#build-integration)连接构建配方，再执行本页的检查。

## 源码与接口 {#source-map}

| 实现部分 | 源码 | 阅读与实现内容 |
| --- | --- | --- |
| 协议核心 | [qbt.h](https://github.com/UniXNU/QcaBluetooth/blob/22ff97f93416452335bb61badb14c762da653487/include/qbt.h) | `qbt_platform` 回调、`qbt_create`、`qbt_boot`、`qbt_step`、`qbt_deadline` |
| UART | [qbt_geni.h](https://github.com/UniXNU/QcaBluetooth/blob/22ff97f93416452335bb61badb14c762da653487/include/qbt_geni.h) | GENI DMA、中断服务、排空和静默 |
| 内核管道 | [qbt_transport.h](https://github.com/UniXNU/QcaBluetooth/blob/22ff97f93416452335bb61badb14c762da653487/include/qbt_transport.h) | UART.SK 操作和电源请求 |
| 板级集成 | [BluetoothProbe.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/ce0c600fa015964d4ecb6af864fa2ab66efa915f/package/BluetoothProbe.cpp)、[WcnPower.h](https://github.com/UniXNU/UniXNU-sheng/blob/ce0c600fa015964d4ecb6af864fa2ab66efa915f/package/WcnPower.h) | 资源、上电顺序、工作线程和共享电源 |
| 原生协议栈 | [native-ios27.md](https://github.com/UniXNU/QcaBluetooth/blob/22ff97f93416452335bb61badb14c762da653487/native-ios27.md) | `bluetoothd` 路由、扫描和能力 |

## 1. 收集硬件输入

从目标设备的 DTS 读取：

| 输入 | sheng 的值 |
| --- | --- |
| UART | QUP2 SE6，地址 `0x898000`，GIC INTID 493 |
| DMA 流 | Apps SMMU `0x423` |
| CTS、RTS、TX、RX | GPIO 76、77、78、79 |
| `BT_EN` | GPIO 81 |
| 唤醒源 | GPIO 79 |
| 串口时钟和速率 | 51.2 MHz，16 倍过采样，3.2 Mbaud |
| 固件 | `hmtbtfw20.tlv`、`hmtnv20.bin` |

在 `firmware/bluetooth/manifest.json` 中固定固件版本，并在设备仓库中放置固件：

```sh
python3 scripts/stage-bluetooth-firmware.py OUTPUT --source FIRMWARE_QCA_DIRECTORY
```

UART 需要启动固件加载的协议 2 微码。引擎报告其他协议时，`powerOn` 返回 `ENXIO`。

## 2. 实现电源路径

通过 `sheng_wcn_power_get` 和 `sheng_wcn_power_put` 与 Wi-Fi 共用 WCN 电源。
每个射频持有一票，最后一方释放电源。

`powerOn` 按以下顺序执行：

1. 映射资源，在持有 `AppsSmmuLock` 时通过 `smmu_plan_bypass` 和 `smmu_configure_bypass`
   配置 32 KiB DMA 缓冲区。
2. 取得蓝牙电源票。
3. 拉低 `BT_EN` 100 ms，再打开串口时钟。
4. 检查 QUP 版本和协议，再准备引擎。
5. 挂接 UART 中断和唤醒中断。
6. 拉高 `BT_EN`，等待 60 ms，再打开引脚上下拉。
7. 调用 `qbt_geni_start`，再用速率和地址调用 `qbt_boot`。

`powerOff` 关闭控制器、静默引擎、拉低 `BT_EN` 并释放电源票。
返回第一个错误，让失败的步骤传到 `qbt_transport_power_result`。

## 3. 启动工作线程

在后期平台探测中调用 `sheng_bluetooth_probe`。工作线程：

1. 填写 `qbt_platform`，调用 `qbt_create`，再调用 `qbt_transport_init`。
2. 等待 Data 插件，固件读取依赖它。
3. 在 `qbt_transport` 和 `qbt_transmit` 之间传输字节，并休眠到 `qbt_deadline` 和
   `qbt_geni_deadline` 中较早的时刻。

## 4. 发布控制器

在设备树中添加节点：

```text
bluetooth {
    device_type = "bluetooth";
    compatible = "qcom,wcn7850-bt";
    unixnu,adt-name = "bluetooth";
    transport-encoding = <1>;
    transport-speed = <3200000>;
    status = "okay";
};
```

用户态启动前，板级代码设置 `local-mac-address` 和 `/chosen/mac-address-bluetooth0`，
并注册带相同属性、名为 `bluetooth` 的 `IOService`。

## 5. 连接原生协议栈

在 `board.toml` 的 `payload.runtime` 下设置：

```toml
audio_system_plugins = ["BTAudioHALPlugin.driver"]
bluetooth_tool = "scripts/build-bluetooth-userspace.py"
bluetooth_target = "ios27"
```

该工具放置已签名的 BlueTool、`bluetoothd`、`QcaBTType0.dylib` 和固件。
`patches/xnu-12377/sheng-bluetooth-runtime.patch` 把它们挂载到 `/usr/lib` 和 `/usr/sbin`。
`audio_system_plugins` 让蓝牙 HAL 插件穿过音频覆盖层后仍然可见。

适配器锁定到一个 `bluetoothd` 哈希。其他 OS 版本按
[native-ios27.md](https://github.com/UniXNU/QcaBluetooth/blob/22ff97f93416452335bb61badb14c762da653487/native-ios27.md)
重新定位补丁位置。

配对密钥依赖钥匙串，钥匙串依赖 [AppleKeyStoreState](/zh/drivers/apple-key-store-state)。
板级代码通过 `native_aks_device_id` 返回 `/chosen/unique-chip-id`。

## 6. 构建和验证

在工作区根目录：

```sh
python3 UniXNU-<device>/scripts/check-bluetooth-platform.py
python3 UniXNU-<device>/scripts/check-bluetooth-shared.py
python3 UniXNU-<device>/scripts/check-wcn-power.py
```

在 UniXNU 仓库中，确认板级启动参数含 `sheng-bluetooth=1` 和 `log-bluetooth=2`：

```sh
./unixnu build kernel payload -D ../UniXNU-<device> --os <profile>
./unixnu bootimg -D ../UniXNU-<device> --os <profile> --dtb <device>.dtb -o boot.img
fastboot boot boot.img
```

**预期结果：** [抓取日志](/zh/porting/log-capture)后，`[bluetooth]` 显示 `state=2 error=0`，
`[bluetooth proc]` 显示 `bluetoothd` 只启动一次。在“设置”中打开蓝牙，配对配件并播放音频。
重启后确认无需重新配对即可回连。

| 现象 | 检查 |
| --- | --- |
| 设置项保持灰色 | `bluetoothd` 的 launchd 任务和 `[bluetooth proc]` 的重启次数 |
| `[bluetooth uart]` 显示故障或错误 | 串口时钟速率、DMA 映射和引脚 |
| 配对密钥丢失，或 `bluetoothd` 报告钥匙串问题 | AppleKeyStoreState 密钥封装 |
| 音频仍从扬声器输出 | `audio_system_plugins` |

设备结果按[适配记录](/zh/porting/records)记录。

## 下一步

继续 [USB](/zh/porting/usb)。
