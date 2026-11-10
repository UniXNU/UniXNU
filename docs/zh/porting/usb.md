# USB 适配

先完成[平台中断和 DMA](/zh/porting/platform)。[QcomDwc3](https://github.com/UniXNU/QcomDwc3)
派生自苹果的 `AppleUSBXDCI` 和 `AppleUSBXHCI`。移植时提供寄存器窗口、中断、电源和 PHY。
苹果的 USB 栈、`configd` 和 `lockdownd` 不做修改。

按[驱动接入步骤](/zh/porting/drivers#build-integration)连接构建配方，再执行本页的检查。

## 源码与接口 {#source-map}

| 实现部分 | 源码 | 阅读与实现内容 |
| --- | --- | --- |
| 控制器 | [QcomDwc3.cpp](https://github.com/UniXNU/QcomDwc3/blob/e4efe95c903a737e0f5955e5b50a8fb4d2a7d718/QcomDwc3.cpp) | `bringUp`、`qcom_dwc3_publish`、类覆盖和角色切换 |
| PHY | [QcomEusb2Phy.h](https://github.com/UniXNU/QcomDwc3/blob/e4efe95c903a737e0f5955e5b50a8fb4d2a7d718/QcomEusb2Phy.h)、[QcomQmpUsb3.h](https://github.com/UniXNU/QcomDwc3/blob/e4efe95c903a737e0f5955e5b50a8fb4d2a7d718/QcomQmpUsb3.h) | eUSB2、中继器和 QMP 时序 |
| 线缆角色 | [QcomUcsi.h](https://github.com/UniXNU/QcomDwc3/blob/e4efe95c903a737e0f5955e5b50a8fb4d2a7d718/QcomUcsi.h)、[ShengBattery.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/ce0c600fa015964d4ecb6af864fa2ab66efa915f/package/ShengBattery.cpp) | 通过充电器 GLINK 通道收发 UCSI 消息 |
| 板级入口 | [UsbProbe.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/ce0c600fa015964d4ecb6af864fa2ab66efa915f/package/UsbProbe.cpp) | 加载 kext 和注册类 |
| 构建 | [build-gop-legacy-display-27.py](https://github.com/UniXNU/UniXNU-sheng/blob/ce0c600fa015964d4ecb6af864fa2ab66efa915f/scripts/build-gop-legacy-display-27.py)、[board.toml](https://github.com/UniXNU/UniXNU-sheng/blob/ce0c600fa015964d4ecb6af864fa2ab66efa915f/board.toml) | 生成的类头文件和 prelink 根 |

硬件时序遵循[主线 Linux](https://github.com/ianchb/sm8550-mainline)。

## 1. 收集硬件输入

从目标设备的 DTS 和时钟定义读取：

| 输入 | sheng 的值 |
| --- | --- |
| DWC3 基址和苹果寄存器窗口 | `0x0a600000`，窗口在基址 + `0xc000` |
| 中断 | GIC INTID 165 |
| SMMU 流 | `0x40` |
| eUSB2 参考时钟 | 38.4 MHz |
| PHY 和电源轨 | eUSB2 PHY、PMIC 中继器、QMP combo PHY、retimer、GDSC、RPMh 电源轨 |

SoC 相关的值是 `QcomDwc3.cpp` 里的常量。其他 SoC 的 QMP 表在设备仓库中从其 Linux 源码生成：

```sh
python3 scripts/gen-qmp-usb3-table.py LINUX_TREE drivers/QcomDwc3/QcomQmpUsb3.h
```

## 2. 启动控制器

`bringUp` 按以下顺序执行，并把每一步写入 `native_usb_stats[0]`。负值表示失败的步骤。

| 阶段 | 步骤 |
| --- | --- |
| 1 | 映射时钟、TCSR、PHY 和 QSCRATCH 窗口 |
| 2 | 投票电源轨 |
| 3 | 打开 GDSC |
| 4 | 打开时钟并释放复位 |
| 5 | 创建该流的 SMMU 上下文 |
| 6 | 启动中继器 |
| 7 | 启动 eUSB2 PHY，再启动 QMP PHY；QMP 未启动时改用 UTMI 时钟 |
| 8 | 通过寄存器窗口读取核心 ID |
| 9 | 硬件就绪 |

`AppleUSBXDCI` 不做缓存维护。为控制器的流配置 stage 1 恒等映射上下文，使用 write-back、
inner shareable 块。

**预期结果：** 到达阶段 9，`native_usb_stats[1]` 为 DWC3 核心 ID。

## 3. 注册类

设置 `usb` 后，板级代码启动一个工作线程，依次执行：

1. `qcom_dwc3_bring_up`。
2. 用 `OSKextLoadKextWithIdentifier` 加载 `com.apple.driver.AppleUSBXDCI` 和
   `com.apple.driver.usb.AppleUSBXHCI`。`AppleUSBXDCI` 没有 personality，其他路径不会加载它。
3. `OSMetaClass::preModLoad`、驱动的静态初始化和 `postModLoad`。
4. `qcom_dwc3_publish`，挂接 provider nub 并启动设备栈。

把 USB 栈加入 `board.toml` 中 `[kernel.prelink]` 的 prelink 根。

类布局来自所选的 kernelcache。`scripts/gen-usb27-abi.py` 和 `scripts/gen-usb27-host-abi.py`
生成 `scripts/usb-xdci-24A446.json` 和 `scripts/usb-xhci-24A446.json`。这两个脚本写明了
24A446 的 kernelcache 和类地址，其他 OS 版本需要修改。

布局变化时保留两处覆盖：

- 没有 `IOPort` 传输对象时，`AppleUSBXDCI` 的 179 号槽返回 false。
- 主机模式下，xHCI 子类对 family 的期望电源回答开启，设备栈回答 0。

**预期结果：** 到达阶段 12，`IOUSBDeviceFamily` 在 nub 上启动。

## 4. 连接线缆角色

在板级充电器驱动中调用：

| 函数 | 用途 |
| --- | --- |
| `qcom_dwc3_vbus(int)` | 充电器的 USB 在线值 |
| `qcom_ucsi_start`、`qcom_ucsi_receive`、`qcom_ucsi_tick` | 把每条返回的消息发到 GLINK 通道 |
| `qcom_ucsi_polling` | 驱动需要 20 ms 定时器时为 true |

线缆对端是主机时选择设备角色，是外设时选择主机角色。两个来源都没有回答时运行设备角色。
在 `drivers/QcomDwc3/tests` 中检查 UCSI 客户端：

```sh
clang++ -std=c++17 -I.. ucsi_host.cpp && ./a.out
```

## 5. 回答 Mac 的配对检查

| 回答 | 位置 |
| --- | --- |
| `chip-id` | `board.toml` 的 `[payload.adt]` |
| `board-id`、`security-domain` | OS 配置的 `adt.chosen.u32` |
| `/System` 和系统守护进程使用同一个文件系统编号 | [`native-union-statfs-fsid`](/zh/xnu/patch-reference) |
| 锁状态 3 | [`aks-sls=3`](/zh/drivers/apple-key-store-state) |

三个 ID 使用 `MobileDevice.framework` 内设备映射表中该机型的行。

## 6. 构建和验证

在 UniXNU 仓库中，确认板级启动参数含 `usb=1` 和 `log-sys=1`：

```sh
./unixnu build kernel payload -D ../UniXNU-<device> --os <profile>
./unixnu bootimg -D ../UniXNU-<device> --os <profile> --dtb <device>.dtb -o boot.img
fastboot boot boot.img
```

把设备连接到 Mac：

```sh
ioreg -p IOUSB -l -w0 | grep -E 'idVendor|idProduct|Device Speed'
```

**预期结果：** Mac 列出设备，USB 3 线缆下 `Device Speed` 为 4。解锁并点“信任”后，Mac 报告已配对并开始
lockdown 会话。[抓取日志](/zh/porting/log-capture)后可查看 `[usb]` 行。

| 现象 | 检查 |
| --- | --- |
| chirp 通过，高速数据失败 | eUSB2 参考时钟表 |
| `ep0OutEventOccurred: event 0` | stage 1 SMMU 上下文 |
| 创建 TRB 池时 PAC panic | 注册类之前是否加载了 `AppleUSBXDCI` |
| `bNumConfigurations` 为 0，主机复位 | 179 号槽 |
| Mac 要求更新软件 | `chip-id`、`board-id`、`security-domain` |
| `UserDeniedPairing`，屏幕上没有弹窗 | `/System` 的文件系统编号 |
| 点“信任”后要求输入密码 | 锁状态 |

测试主机模式时，`usb-host=<s>` 在延时后强制进入主机模式，`usb-back=<s>` 再回到线缆决定的角色。
设备结果按[适配记录](/zh/porting/records)记录。

## 下一步

有基带的设备继续[基带与移动网络](/zh/porting/baseband)，其余设备继续 [DSP、音频和电源](/zh/porting/power)。
