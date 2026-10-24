# 构建环境

## 操作步骤 {#procedure}

1. 按要执行的构建步骤选择[主机工具链](#主机)，完成 macOS 或 Linux 安装说明，确认所需工具可用。
2. 为所选 OS profile 收集[外部输入](#外部输入)：IPSW/kernelcache、trust cache、Data seed 和需要的驱动 ABI 输入，记录路径与版本。
3. 核对[设备输入](#设备)：设备仓库、固件仓库和目标 DTB，将路径保存到[本地配置](/zh/reference/configuration#local-build-inputs)。
4. 继续[构建与启动](/zh/building)。选定 defconfig 后运行 `./unixnu status --json`，确认设备、OS profile 和源码路径与上述输入一致。

## 主机

构建驱动支持 macOS 和 Linux。macOS 内核步骤使用 Xcode 和 `iphoneos` SDK，Linux 使用 [Linux 工具链](#linux)。`--skip-setup` 和 Data seed 调整使用 macOS 镜像工具。

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

没有 Mac 时，`macOS build` workflow 在 GitHub 的 macOS runner 上运行 Mac 专属步骤。见[构建](/zh/building#macos-runner)。

### Linux

在 Linux 上，内核步骤用上游 clang 和开源的 Mach-O 工具链代替 Xcode。`scripts/linux/setup-toolchain.py` 以 root 运行一次，把工具链安装到 `/opt/unixnu-linux`（或参数、`UNIXNU_TOOLCHAIN` 指定的前缀）：

| 工具 | 来源 |
| --- | --- |
| 带 xnu `kalloc.h` 所需 `__builtin_xnu_type_*` 内建函数的 clang | llvm-project 加 `scripts/linux/llvm-xnu-builtin-type.patch` |
| ld64、libtool、nm、lipo | cctools-port `1030.6.3-ld64-956.6` |
| mig、iig | bootstrap_cmds-138、iig-port |
| `xcrun`、`plutil`、`codesign` 与 Command Line Tools 目录结构 | `scripts/linux` 中的替身 |
| lzfse | lzfse，用于 kernelcache |

安装脚本运行于使用 glibc 的 Linux 主机。它通过 `/etc/os-release` 识别发行版，并调用对应包管理器安装依赖：

| 包管理器 | 发行版系列 |
| --- | --- |
| apt | Debian、Ubuntu 及其衍生发行版 |
| dnf | Fedora 及 RHEL 衍生发行版 |
| pacman | Arch Linux 及其衍生发行版 |
| zypper | openSUSE、SUSE |

已启用的软件源需要提供 Clang、LLVM 开发文件、libclang、libbsd、UUID、OpenSSL 和 zlib 开发包。安装脚本也会安装负载及设备树命令所需的 mtools 和 dtc。可用软件包取决于软件源配置。按发行版的正常更新流程保持系统和软件包数据库同步。

```sh
# 预览依赖安装命令。
scripts/linux/setup-toolchain.py --print-packages
# 安装依赖并构建工具链。
sudo scripts/linux/setup-toolchain.py
# 检查已安装的工具、头文件和库链接。
scripts/linux/setup-toolchain.py --check
```

`--package-manager apt|dnf|pacman|zypper` 显式选择包管理器。其他发行版或已经准备好依赖的环境可使用：

```sh
scripts/linux/setup-toolchain.py --package-manager pacman --print-packages
sudo scripts/linux/setup-toolchain.py --package-manager none --llvm-config /path/to/llvm-config
```

`--llvm-config FILE` 或 `LLVM_CONFIG` 选择主机 LLVM 安装，其 `clang`、`clang++`、libclang 和资源头文件一起解析。XNU 专用 Clang 从固定的 LLVM 源码构建。`-j N` 设置构建并行度。位置参数指定安装前缀，默认值为 `/opt/unixnu-linux` 或 `UNIXNU_TOOLCHAIN`。

脚本把 `xcrun`、`plutil` 和 `codesign` 包装脚本写入 `/usr/bin`，XNU makefile 从这里调用它们。Mach-O 静态库、libdispatch 和 BlocksRuntime 保存在工具链前缀下。编译 Clang 占用主要安装时间。userdata 步骤可在 Linux 上运行；`--skip-setup` 和 `seed-data-grow` 需要 macOS。

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

### 目标 IPSW

sheng 板级文件仍以 iPadOS 17.7.11 为默认目标。iPhone X iOS 16.7.16 镜像是第二个目标，不替换默认。

| 目标 | 版本 | Build | 恢复镜像 |
| --- | --- | --- | --- |
| iPadOS，sheng 默认 | 17.7.11 | 21H461 | [iPad_Pro_HFR_17.7.11_21H461_Restore.ipsw](https://updates.cdn-apple.com/2025SpringFCS/fullrestores/122-77166/DCA6CFE8-90E9-4B92-880D-3DE171798E40/iPad_Pro_HFR_17.7.11_21H461_Restore.ipsw) |
| iOS，iPhone X | 16.7.16 | 20H392 | [iPhone10,3,iPhone10,6_16.7.16_20H392_Restore.ipsw](https://updates.cdn-apple.com/2025FallFCS/fullrestores/122-77006/1158E502-D76D-4226-AA06-ED5E30CD1111/iPhone10,3,iPhone10,6_16.7.16_20H392_Restore.ipsw) |

设备仓库的 `[ipsw] url` 是默认来源，`--ipsw` 或 `UNIXNU_IPSW` 覆盖它。镜像下载到仓库外。

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

开始 sheng 完整构建前，核对 [ABI、SDK、固件和镜像输入清单](/zh/porting/migration#build-inputs)。
