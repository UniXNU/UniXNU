# 联想小新 Pad 2022（tb128fu）

tb128fu 是搭载骁龙 680（SM6225）的联想小新 Pad 2022（TB128FU）。下面的移植是独立的社区项目，UniXNU 组织不维护它。固件是 [uefi-tb128fu](https://github.com/xVanTuring/uefi-tb128fu)，基于 uefi-sheng 树的纯 Mu 平台。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [UniXNU-tb128fu](https://github.com/xVanTuring/UniXNU-tb128fu) | [xVanTuring](https://github.com/xVanTuring) | 已在平板上到达 iPadOS 17.7.11 主屏幕，触控可用；Metal 帧使用 GPU 交接 |
| [uefi-tb128fu](https://github.com/xVanTuring/uefi-tb128fu) | [xVanTuring](https://github.com/xVanTuring) | UEFI、UniXNU 菜单和 DarwinBoot 在平板上运行 |

## 状态

| 阶段 | 状态 |
| --- | --- |
| UEFI 固件和 UniXNU 菜单 | 工作。纯 Mu：原厂 ABL 没有可拆出的厂商 DXE 模块；显示使用 ABL 留下的启动画面缓冲区 |
| 负载卷和 DarwinBoot | 工作。镜像刷入 `boot_a`；ABL 的 `fastboot boot` 缓冲区放不下它 |
| XNU 和根文件系统 | iPadOS 17.7.11 内核运行在全部 8 个核上；UFS 上的已验证 OS/SystemOS 根和 Data 卷 |
| iOS 用户态 | 开机后 70～95 秒出现主屏幕；QuartzCore 在 CPU 上绘制，Metal 帧通过 GPU 交接呈现 |
| 触控 | SPI 上的 Himax HX83102E；内核下载其固件 |
| GPU | Adreno 610（无 GMU）在 NativeAdreno 下运行；Metal 插件通过 GPU 交接呈现帧，tb128fu-040 中 236 帧全部走 GPU，无 CPU 回退 |
| 未工作 | 音频、Wi-Fi、电池、按键、休眠 |

## 说明

以下 SM6225 的情况与 sheng 不同，可能对其他移植有帮助：

- EL1 虚拟定时器是 INTID 19（设备树列出的定时器 PPI 为 1、2、3、0）。INTID 27 是另一个一直有效的中断源。
- SGI 收不到，因此核间中断改用设备树已用 SPI 之上、由软件挂起的 SPI。
- GPU SMMU 的固件会忽略对 S2CR 的 fault 写入，并把 bypass 改成 fault；translate 写入有效。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
