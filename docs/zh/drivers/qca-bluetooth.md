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

`sheng-bluetooth=1` 在插件安装后启动 UART14 工作线程。板级代码绑定 0x898000 的
GENI SE6、中断 493 和 QUP2 DMA 流 0x423。SM8550 代码使用精确的 51.2 MHz 时钟
生成 3.2 Mbaud，并以原生 4 KiB 页映射 32 KiB DMA 区域。配置锁协调触摸、音频
与蓝牙的时钟票和 SMMU 分配。GPIO79 通过共享 TLMM 中断唤醒已关时钟的串口。
UART 需要启动固件提供协议号为 2 的微码。

板级代码在用户态启动前导出蓝牙设备树节点和同名 IOService。H4 UART.SK 编码及
3.2 Mbaud 使用四字节小端属性，两者携带从平台标识派生的稳定私有地址。
Linux 接口把网络顺序的地址转换为 bdaddr_t 顺序。

内核与用户态构建使用同一份已解析的 QcaBluetooth 源码。串口时钟恢复失败时，
驱动结束当前传输并保留硬件错误，停止转发和重试。

控制器关闭或故障时会唤醒 UART.SK 的收发队列，同步回调在搬运数据前返回控制器
错误。通知期间保留队列引用，断开流程等待通知完成后再释放。

工作线程保留 DMA 内存，每次处理有界批量，等待中断、队列空间或期限事件。
硬件错误立即结束命令等待。启动日志的 `[bluetooth]` 行记录阶段、收发、休眠、
供电归属和 SMMU 状态；`log-bluetooth=1` 增加初始化信息。

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

在工作区根目录运行板级检查：

```sh
python3 UniXNU-sheng/scripts/check-bluetooth-platform.py
python3 UniXNU-sheng/scripts/check-bluetooth-shared.py
python3 UniXNU-sheng/scripts/check-bluetooth-board.py /path/to/assembled/tree
```

平台模型检查频率比例、DFS 切换、独立 DMA 页表、ASID 冲突和超时边界；共享资源
模型检查中断分发、并发注册和串口与音频的时钟归属。UART14、ArmCpu、触摸、音频
与启动日志代码通过目标编译，构建脚本为板级归档编译八个协议和 SoC 对象。

iPadOS 27 原生适配固定匹配目标二进制，选择控制器类型零并保留标准 HCI 初始化。
扫描、连接、广播及 coded、2M PHY 能力来自 Supported Commands 和 LE Features。
异步 0x203b 查询取得广播组数，上限为原生数组的六组。模型查询、配置缓存、
底层开关及广播模式使用同一份能力。正常数据收发留在 UART.SK 和原生栈。

离线补丁保留指针修正链的认证信息与 PACIBSP 入口。144 项原生指令模拟覆盖两种
ASLR 偏移，PAC 操作按无设备密钥模型处理；生产能力发布代码通过 58 项 ASan/UBSan
HCI 与策略测试。`tools/build-type0.py` 构建并签名 arm64e 能力发布库。
板级 `payload.runtime` 为 ios27 选择 `build-bluetooth-userspace.py`，打入已签名的
BlueTool、bluetoothd、QcaBTType0.dylib 和固定版本固件。原生守护进程保留原有
标识与权限。只读联合挂载暴露 /usr/lib 和 /usr/sbin 文件，先挂载库再挂载程序。
BlueTool 保留原有 Mach 服务，以 root 身份运行并启用事务。Wi-Fi 和蓝牙共用一份
签名启动缓存，其他原生任务保持原样；缺少的代码哈希追加到原有信任包。

`check-bluetooth-runtime.py` 检查实际打包内容、签名、固件、启动任务、信任模块
和原有 Data 种子。联合插件通过 45 个文件、3 个签名蓝牙程序及 716 个启动任务
验证，宿主 libxpc 接受缓存。显式选择本地组件后，完整内核、fileset、FAT 载荷和
临时启动镜像均构建成功。实际载荷包含蓝牙入口、H4/波特率属性、签名运行时和
原有 Data 种子，并关闭自动重启。扫描、配对、音频、功耗和共存的上机验证待完成。

当前设备启动已完成覆盖挂载，随后 launchd 报 `No service cache`。蓝牙 DMA
分配在 UART 启动前报 ENOSPC，需先修复启动，再测功能和性能。

在 UniXNU 仓库显式选择本地源码：

```sh
./unixnu build kernel payload -D /path/to/UniXNU-sheng --os 27 \
  --local-module driver:QcaBluetooth=/path/to/QcaBluetooth
```

按[运行时输入](/zh/porting/packaging#ios-27-运行输入)提供原有安装输入，再按
[启动载荷](/zh/concepts/payload)封装临时启动镜像。

参考：[Linux](https://github.com/ianchb/sm8550-mainline)、
[Debian sheng](https://github.com/ianchb/debian-sheng)、
[Renoir UART.SK](https://github.com/daimile2/renoir_xnu_bluethooth)。
