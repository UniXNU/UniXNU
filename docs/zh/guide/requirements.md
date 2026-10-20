# 构建环境

## 主机

构建驱动在 macOS 上运行。内核步骤调用带 `iphoneos` SDK 的 `xcodebuild`，`--skip-setup` 调用 `hdiutil`。

| 工具 | 用途 | 安装方式 |
| --- | --- | --- |
| macOS 与 Xcode | 内核、skip-setup、seed-data-grow | App Store 或 developer.apple.com |
| Python 3.11 或更新 | 所有步骤 | python.org 或 Homebrew |
| git、make | 拉取、固件 | Xcode command line tools 或 Homebrew |
| cmake、ninja | 内核参考源码 | `brew install cmake ninja` |
| unifdef | libdispatch 头文件 | `brew install unifdef` |
| LLVM 与 lld | 内核、固件、启动镜像 | `brew install llvm` |
| mtools | 负载卷 | `brew install mtools` |
| dtc | 设备树属性 | `brew install dtc` |
| fastboot | seed-data-grow `--auto`、userdata 刷写 | Android platform tools |
| QEMU 与 AAVMF | 可选冒烟测试 | `brew install qemu` |

驱动会直接找到 Homebrew 的 `/opt/homebrew/opt/llvm/bin`，无需修改 `PATH`。其他工具需要在 `PATH` 中。

`unixnu fetch` 需要网络，用于更新模块子模块并拉取 Apple 源码参考和 Mu_Basecore 树。

## 外部输入

以下输入位于 UniXNU 仓库之外。

| 输入 | 使用步骤 | 选项 | 环境变量 |
| --- | --- | --- | --- |
| 设备的 Mu-Silicium 仓库 | 固件、启动镜像 | `--uefi DIR` | `UNIXNU_UEFI` |
| 目标 IPSW，本地文件或 HTTPS URL | 内核预链接、userdata | `--ipsw PATH_OR_URL` | `UNIXNU_IPSW` |
| 解压后的 kernelcache | 内核预链接 | `--kernelcache FILE` | `UNIXNU_KERNELCACHE` |
| 编译后的设备树 | 启动镜像 | `--dtb FILE` | `UNIXNU_DTB` |
| trust cache 包 | 负载 | `--trust-cache FILE` | |
| owner trust cache 包 | 负载 | `--owner-trust-cache FILE` | |
| Data ramdisk 种子 | 负载 | `--data-ramdisk FILE` | |
| 平台种子 | 负载 | `--unique-chip-id HEX` | `UNIXNU_UNIQUE_CHIP_ID` |
| 预编译静态库 | 内核 | 负载可用 `--kernel FILE` | |
| edk2 或 Mu_Basecore 树 | package、固件 | `--edk2 DIR` | `UNIXNU_EDK2` |

设备仓库提供板级描述、内核 defconfig 和 `[kernel] archives` 中列出的静态库脚本。

## 设备

设备需要满足：

- bootloader 可解锁并接受 `fastboot boot`。
- UEFI 移植提供 framebuffer、输入、块 I/O 和文件系统。
- bring-up 期间有 UART 或 USB 日志通道。
- 内存足以容纳内核窗口、负载和 userdata 镜像。
- 目标系统恢复镜像和匹配的设备身份。

## 下一步

- [构建](/zh/building)介绍使用这些输入的命令。
- [设备仓库](/zh/porting/device-repository)介绍板级文件。
- [设备](/zh/devices/)列出设备仓库和各自的输入。
