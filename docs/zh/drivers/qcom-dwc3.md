# QcomDwc3

QcomDwc3 让苹果的 USB 设备栈和主机栈运行在高通 DWC3 控制器上。

[源码仓库](https://github.com/UniXNU/QcomDwc3)。

## 状态

设备：小米平板 6S Pro（sheng），iPadOS 27.0.1（24A446）。

| 状态 | 功能 |
| --- | --- |
| 可用 | USB 3 线缆 10 Gbps、USB 2 线缆 480 Mbps 枚举，重新枚举，信任弹窗，与 Mac 配对，lockdown 会话和服务启动 |
| 部分可用 | 主机模式：苹果 xHCI 栈可运行并完成命令，外设枚举尚未验证 |
| 未测试 | 持续传输、安装应用、USB 3 线缆反向插入 |

`fairplayd.A2` 和 `adid` 保持禁用。两者都启用时，SpringBoard 无法完成启动。

## 分层

`QcomDwc3Xdci` 派生自 `AppleUSBXDCI`，`QcomDwc3Xhci` 派生自 `AppleUSBXHCI`。两者提供寄存器窗口、中断、电源和 PHY。`IOUSBDeviceFamily`、`AppleUSBDeviceMux`、`IOUSBHostFamily`、`USBDeviceConfiguration` 和 `lockdownd` 不做修改。

UCSI 通过充电器的 GLINK 通道报告线缆对端：对端是主机时进入设备模式，对端是外设时进入主机模式。UCSI 应答前，用充电器的在线状态判断主机。同一时间只运行一个角色，切换角色时对核心做软复位。

## 板级集成

板级提供 eUSB2 中继器、QMP PHY、retimer、电源轨和 SMMU 上下文。在 sheng 上，`sheng-usb=1` 启动驱动。eUSB2 参考时钟为 38.4 MHz。`AppleUSBXDCI` 不做缓存维护，所以 stream 0x40 使用独立的 stage 1 上下文，并映射为 write-back inner shareable。

`AppleUSBXDCI` 没有 personality，驱动要先加载该 kext，再注册子类。prelink roots 加入设备栈和主机栈，并排除 `AppleOnboardSerial` 和 `AppleSMC`，主机栈只在 metaclass 比较中用到这两者。

## 与 Mac 配对

Mac 和 `lockdownd` 需要系统给出以下信息：

| 信息 | 来源 | 作用 |
| --- | --- | --- |
| `/chosen` 中的 `chip-id`、`board-id`、`security-domain` | 板级和 OS 配置 | MobileDevice 在设备表中找到型号，不要求更新软件 |
| `/System` 与系统守护进程使用同一个文件系统编号 | [`native-union-statfs-fsid`](/zh/xnu/patch-reference) | SpringBoard 接受守护进程的 `CFUserNotification`，显示信任弹窗 |
| 锁定状态 3，无密码 | [`sheng-aks-sls=3`](/zh/drivers/apple-key-store-state) | `lockdownd` 不要求输入密码即可完成信任 |

## 验证

1. 启动设备并连接 Mac。
2. 解锁平板并点击“信任”。
3. Mac 报告设备已配对，lockdown 会话随之启动。
