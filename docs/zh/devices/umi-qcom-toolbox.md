# 小米 10 — iOS 16（qcom-toolbox）

这是另一个小米 10（`umi`，SM8250）移植：在打过补丁的 XNU（xnu-8796）上运行
**未经修改的 iPhone X iOS 16.7.16（20H392）用户空间**。它与
[iPadOS 17 umi 移植](/zh/devices/umi)及其他 [umi 来源](/zh/devices/models/umi)
互相独立，不共用内核、启动路径或根文件系统镜像。

| 来源 | 内容 |
| --- | --- |
| [qcom-toolbox/ios-umi](https://github.com/qcom-toolbox/ios-umi) | 上游仓库：启动 shim、XNU 补丁序列、主机工具、笔记 |

项目最初在红米 Note 10 Pro（`sweet`）上开始，因此许多驱动、工具和启动参数仍沿用
`sweet` 名称。内核在运行时根据设备树选择机型。

## 状态

截至 2026-11-06，手机可进入带原生应用的 iOS 主屏幕。逐项状态见
[`Status.md`](https://github.com/qcom-toolbox/ios-umi/blob/main/Status.md)，
每次启动与决策记录在
[`NOTES.md`](https://github.com/qcom-toolbox/ios-umi/blob/main/NOTES.md)。

| 部分 | 状态 |
| --- | --- |
| 启动 | 原厂小米 ABL → `fastboot boot` 自有 shim → XNU；也可刷入 `boot` |
| CPU 与内存 | 通过 PSCI 启动全部 8 核，GICv3，EPSS 调频；8 GB 中 6 GB 供 iOS 使用 |
| 存储 | 自有 UFS 主机驱动；`userdata` 中的日志式 HFS+ 根卷，可读写 |
| 用户空间与界面 | launchd、系统守护进程、backboardd、SpringBoard、锁屏、控制中心、设置、31 个原生应用 |
| 显示与亮度 | 1080×2340 AMOLED 以 iPhone X 面板呈现；亮度滑块、自动亮度（SLPI 光线传感器）、夜览 |
| GPU | Adreno 650 通过 Mesa turnip 与 Metal→Vulkan 桥绘制界面及所有 Metal 应用（含 Safari） |
| 触摸与按键 | ST FTM5，GENI I²C + GPI DMA；电源键与音量键 |
| 电池与充电 | PM8150B 电量计；内核充电控制（4.40 V、2.0 A、QC 2.0 / 3.0）；不支持 USB-PD |
| Wi-Fi | QCA6390，PCIe + MHI；2.4 GHz 开放与 WPA2-PSK 网络 |
| 蓝牙 | QCA6390 经 UART；扫描、连接与配对 |
| 音频 | 扬声器经 ADSP 与 CS35L41 功放；无麦克风 |
| 蜂窝网络 | X55 注册 LTE，状态栏显示运营商与信号；数据会话已建立，尚未传输数据包 |
| 定位 | Wi-Fi 定位；无 GPS |
| 尚不可用 | 相机、视频解码、运动传感器、指纹、SEP / 面容 ID、NFC、振动、App Store / Apple ID |

安全机制基本关闭（宽松的 AMFI 与沙盒、AppleKeyStore 桩、无数据保护）。请勿在手机上存放个人数据。

## 驱动

本移植的驱动以[社区驱动](/zh/drivers/repositories#社区驱动)形式列出，源码保留在 ios-umi 仓库中。

| 驱动 | 硬件 |
| --- | --- |
| [SweetAdreno](/zh/drivers/community-ios-umi-adreno650) | Adreno 650 GPU |
| [QCA6390 Wi-Fi (umi)](/zh/drivers/community-ios-umi-qca6390-wifi) | Wi-Fi |
| [QCA6390 Bluetooth (umi)](/zh/drivers/community-ios-umi-qca6390-bluetooth) | 蓝牙 |
| [SweetHIDTouch](/zh/drivers/community-ios-umi-ftm5-touch) | 触控与按键 |
| [AppleCLCD / AppleARMBacklight (umi)](/zh/drivers/community-ios-umi-display) | 显示与亮度 |
| [SweetHIDALS](/zh/drivers/community-ios-umi-slpi-als) | 环境光传感器 |
| [SweetAudio](/zh/drivers/community-ios-umi-adsp-audio) | 音频 |
| [SweetBattery](/zh/drivers/community-ios-umi-pm8150b-battery) | 电池与充电 |
| [AppleBaseband (X55, umi)](/zh/drivers/community-ios-umi-x55-baseband) | 蜂窝调制解调器 |
| [SweetUfs](/zh/drivers/community-ios-umi-ufs) | UFS 存储 |
| [ios-umi boot shim](/zh/drivers/community-ios-umi-boot-shim) | 启动加载器 |

## 机型与系统输入

| 项目 | 值 |
| --- | --- |
| 机型 | `umi` |
| SoC | `SM8250` |
| 来源设备 | iPhone X `iPhone10,3` / `D22AP`，iOS `16.7.16`，版本 `20H392` |
| 源 XNU | `xnu-8796`（Darwin 22），在 GitHub macOS 运行器上构建 |
| 启动镜像 | Android boot.img v2，包含 shim、XNU、生成的 ADT 与启动参数 |
| 根文件系统 | 单个区分大小写的日志式 HFS+ 卷，刷入 `userdata` |

安装会**清除 Android 的 `userdata`**。不会改动 bootloader、recovery、基带和 persist
分区；请先备份。

## 构建

步骤见仓库 [README](https://github.com/qcom-toolbox/ios-umi#how-to-do-it-yourself)
与 [`docs/UMI.md`](https://github.com/qcom-toolbox/ios-umi/blob/main/docs/UMI.md)。概要：

1. 备份手机，并从 `boot.img` 提取原厂 DTB。
2. 使用 `xnu.yml` 工作流构建内核，按顺序应用 `xnu/patches/`。
3. 用 `tools/mkiosroot.sh` 与 `tools/sweet-root-tweaks.py` 从 iPhone X IPSW 构建 HFS+ 根卷。
4. 用 `tools/umi-boot-image.sh` 生成启动镜像。
5. `fastboot flash userdata` 刷入根卷，再 `fastboot boot` 启动镜像。

不分发 Apple 固件与根镜像、手机固件及分区备份。

## 维护

维护者负责仓库及其发布。本页记录该移植所报告的状态。
