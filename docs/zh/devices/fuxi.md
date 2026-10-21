# 小米 13（fuxi）

fuxi 是搭载 SM8550 的小米 13。下面的项目是独立的社区移植，UniXNU 组织不维护它们。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [ios-fuxi](https://github.com/bangprovn/ios-fuxi) | [bangprovn](https://github.com/bangprovn) | fuxi 上的 iOS 16.7 用户态，CPU 渲染，正在迁移到 UniXNU |
| [UniXNU-fuxi](https://github.com/matejkoo217/UniXNU-fuxi) | [matejkoo217](https://github.com/matejkoo217) | UniXNU 设备仓库分支，进行中 |

## ios-fuxi

ios-fuxi 在 fuxi 上运行 Apple 的 iOS 16 用户态。内核为 xnu-8796。根文件系统是存放在 Android userdata 固定文件中的日志式 HFS+ 镜像，加载器通过 extent 表读取它。

| 区域 | 状态 |
| --- | --- |
| 启动 | 原厂 bootloader，临时 `fastboot boot` 镜像 |
| CPU | 8 核中的 7 核，EPSS 时钟限制 |
| 存储 | 自己的 UFS 主控驱动，从 userdata extent 读取 HFS+ 根 |
| 显示 | 1080x2400 面板，CPU CoreAnimation，60 Hz 帧缓冲复制 |
| 触控 | SPI 上的 FTS 控制器 |
| 按键 | PMK8550 上的电源和音量键 |
| GPU | 仅加载器 bring-up，XNU 内无 GPU 驱动 |
| 未工作 | Wi-Fi、蓝牙、蜂窝、音频、相机、传感器、Face ID、GPU 加速 |

启动镜像：

```sh
fastboot boot fuxi-xnu-boot.img
```

主机端监控工具是 `tools/fuxi-xnu-monitor.py`。项目只做临时启动，请备份关键分区。构建步骤见仓库。

## UniXNU-fuxi

UniXNU-fuxi 是基于 UniXNU-sheng 的 fuxi 板级数据分支。它沿用 iPad7,1 iPadOS 17.7.11 镜像和 sheng 的内核预链接。fuxi 的 UEFI package、预链接、内核构建、触控驱动和 defconfig 仍在进行中。移植记录见 `PORTING-FUXI.md`。

## 维护

表中的维护者拥有各自仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
