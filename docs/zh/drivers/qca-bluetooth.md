# QcaBluetooth

QcaBluetooth 将高通 WCN7850 串口控制器接入苹果蓝牙栈。板级集成位于
`UniXNU-sheng`，开发中的组件位于 `drivers/QcaBluetooth`。

## 分层

板级代码提供 WCN 电源共享、时钟、引脚、DMA 映射与中断。驱动复用固定版本
Linux `btqca.c` 初始化流程，处理 H4 和 IBS。UART.SK/Skywalk 将 H4 数据交给
`bluetoothd`，BlueTool 通过 `kern.sheng_bt_control` 请求启动控制器。
扫描、配对、密钥、BLE 和音频协议由苹果系统负责。

`WcnPower.h` 为 Wi-Fi 和蓝牙分别记录共享六路电源的使用票，最后一方释放时关闭
电源。单独启动蓝牙跳过 PCIe 总线票；Wi-Fi 的启动路径已使用这个共享接口。

GENI 使用四块 2048 字节接收缓冲和一块 4096 字节发送缓冲。硬中断只屏蔽中断线、
唤醒工作线程。接收侧保留未消费的缓冲，满时关闭 RFR；发送侧确认 DMA 完成且
串口排空。IBS 控制字节只插在完整 H4 包之间。物理关时钟要求接收侧停止完成，
并已启用硬件唤醒源。

固件按哈希校验后打入 Data 插件的 `firmware/qca`。读取端与打包脚本共用
`package/BluetoothFirmware.h` 定义的路径，VFS 读取等待插件安装完成。

## 构建与检查

在组件目录运行：

```sh
python3 tools/test-runtime.py
python3 tools/test-geni.py
python3 tools/check-kernel.py /path/to/assembled/tree
python3 tools/build-bluetool.py
```

协议与 DMA 模拟通过 ASan/UBSan。协议核心、Linux 适配、原始 `btqca.c`、DMA 引擎、
Skywalk 桥接和板级固件读取代码通过 iPadOS 27 arm64e 内核参数编译，引用符号可在
目标内核中找到。BlueTool 已编译并通过签名检查。
电源模拟检查覆盖两种启动顺序、独立释放、重复申请和失败处理；Wi-Fi 消费端通过
arm64e 编译。

板级资源绑定、运行时打包和 iPadOS 27 控制器适配仍在开发。扫描、配对、音频、
功耗及 Wi-Fi 共存等待上机验证。

参考：[Linux](https://github.com/ianchb/sm8550-mainline)、
[Debian sheng](https://github.com/ianchb/debian-sheng)、
[Renoir UART.SK](https://github.com/daimile2/renoir_xnu_bluethooth)。
