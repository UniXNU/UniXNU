# 构建与启动

`unixnu` 解析 ARM64、SoC、OS 和设备配置，选择组件依赖并组装目标树。格式 2 输出位于 `out/<device>/<os_profile>/<config>/`，格式 1 使用 `out/<board>/`。

::: warning 必需的固件集成
打包启动镜像前，运行 `./unixnu build firmware --uefi ../uefi-<device>` 构建设备固件。DSC 和 FDF 必须包含 UniXNU、UniXNUDxe、DarwinBoot 和负载卷驱动。Mu-Silicium 的 FDT initrd 路径使用共享的 `UniXNURamDiskDxe`，并需要 DiskIoDxe 和 FAT 支持。步骤见[固件集成](/zh/porting/uefi-firmware#required-integration)。
:::

## 1. 准备主机和仓库 {#quick-start}

阅读[前置条件](/zh/guide/requirements)，从[设备列表](/zh/devices/)选择移植。
新设备先按[移植流程](/zh/porting/)操作。获取设备和 UEFI 仓库及其 submodule。
例如 sheng 使用：

```sh
git clone --recurse-submodules https://github.com/UniXNU/UniXNU
git clone --recurse-submodules https://github.com/UniXNU/UniXNU-sheng
git clone --recurse-submodules https://github.com/UniXNU/uefi-sheng
cd UniXNU
./unixnu defconfig sheng_defconfig -D ../UniXNU-sheng
./unixnu fetch
./unixnu status --json
```

替换为目标仓库和 defconfig 名称。`status` 显示最终 profile、版本、补丁顺序和输出目录。
`-D` 记录在 `out/state.json`，后续命令均在 UniXNU 主仓库执行。

**预期结果：** 设备/配置选择正确，源码路径已解析。

## 2. 保存并获取构建输入 {#saved-build-inputs}

```sh
cp unixnu.example.toml unixnu.local.toml
```

按[本地构建配置](/zh/reference/configuration#local-build-inputs)填写设备和 UEFI 路径、
固件 DTB、平台身份及所需 kernelcache、trust-cache 和 Data seed。
遵循设备输入清单；[sheng 构建输入](/zh/porting/migration#build-inputs)列出其 SDK、固件和 ABI 要求。

```sh
./unixnu ipsw info
./unixnu ipsw fetch
./unixnu tree
```

`ipsw info` 应显示 profile 选定的 OS 构建，`ipsw fetch` 将配置的成员提取到 `out/ipsw/<build>/`。
设备固件、Data seed 和 ABI 审计输入各有准备步骤，在执行消费它们的配方前逐项确认。

## 3. 构建内核、package 和固件 {#build-artifacts}

```sh
./unixnu build kernel
./unixnu build package
./unixnu build firmware
```

前一条成功后再执行下一条。[内核准备](/zh/guide/build-kernel)说明归档、ABI 和预链接要求，
[固件集成](/zh/porting/uefi-firmware#required-integration)说明必需的 DSC/FDF 模块。

| 步骤 | 预期输出 |
| --- | --- |
| 内核 | `<output>/kernel/kernel.macho` 和构建/预链接日志 |
| Package | 默认目标为 `<output>/package/Build/Out/AARCH64-DEBUG/UniXNU.efi` |
| 固件 | UEFI 仓库内由 `[firmware] fd` 选择的 FD 路径 |

`<output>` 是 `status` 显示的目录。`--target RELEASE` 使用 `AARCH64-RELEASE` package
目录并选择 release 固件路径。

## 4. 准备根卷和 payload

采用 userdata 根卷布局的设备按 [Userdata](/zh/guide/userdata)操作。
命令需要 macOS 镜像工具和目标分区布局：

```sh
./unixnu build userdata --dry-run
./unixnu build userdata
```

检查 `<output>/userdata/userdata-root.json` 中的大小、窗口和刷写命令，从选定卷取得根卷 UUID。
可写 Data 卷使用设备说明中的 seed；[跳过 Setup](/zh/guide/skip-setup)是可选的 seed 转换。

```sh
./unixnu build payload
```

命令使用本地配置中的 trust-cache、身份和 Data seed。
检查 `<output>/payload/payload.json` 及打印的命令行。生成的 FAT 卷包含 `unixnu.toml`、
内核、ADT 和所选 sidecar，布局见 [Payload](/zh/concepts/payload)。

**预期结果：** 根卷和 Data 输入匹配设备策略，payload 包含预期启动项与参数。

## 5. 打包并启动

```sh
./unixnu bootimg
```

检查 `<output>/boot/boot.json`，确认固件、DTB 和 payload 来源正确。
通过配置的 payload 启动时，`ramdisk_bytes` 应大于零。
按[启动镜像](/zh/guide/boot)确认刷写条件并单次启动；新设备按[启动验证](/zh/porting/bring-up)检查。

修改启动参数后执行 `./unixnu payload` 和 `./unixnu bootimg`，按
[参数应用](/zh/xnu/boot-arguments#apply-arguments)检查打包后的配置。修改内核代码时先重建内核。

## macOS runner

CI 使用共享解析器读取最终配置和输出路径。

内核步骤在 macOS 上调用 Xcode，Data 种子步骤调用 `hdiutil` 和 `diskutil`。fork 后可以在 GitHub 的 macOS runner 上运行这些步骤，不需要本地 Mac。workflow 是构建检查：只发布脱敏文本日志，不上传镜像。

1. fork 仓库并启用 Actions。
2. 板级需要为负载提供平台种子时，添加仓库 secret `UNIXNU_UNIQUE_CHIP_ID`。
3. 运行 `macOS build` workflow，选择设备仓库、ref、defconfig、Xcode 版本和步骤。
4. 查看 step summary，或下载日志 artifact。

job 运行在 `macos-26`。`xcode` 选择 `/Applications/Xcode_<version>.app`，默认 `26.6`。

| 输入 | 含义 |
| --- | --- |
| `device_repository` | 设备仓库，格式 `owner/name` |
| `device_ref` | 设备仓库的 ref |
| `defconfig` | `configs/` 中的 defconfig 名称 |
| `xcode` | `macos-26` 镜像上的 Xcode 版本 |
| `steps` | `kernel`、`kernel payload`、`kernel userdata` 或 `kernel userdata payload`，默认 `kernel` |
| `ipsw_url` | 可选 IPSW URL，空值使用 `board.toml` |
| `pre_build` | 可选 shell 命令，在内核构建前于 UniXNU 检出目录运行。设备仓库位于 `DEVICE_DIR` |
| `trust_cache_url` | 可选 trust cache 包 URL，日志中会被掩码 |
| `owner_trust_cache` | 把该 URL 当作 owner 签名的包 |
| `data_seed_url` | 可选 Data 种子 URL，日志中会被掩码 |
| `grow_gib` | 把 Data 种子增长到该大小 |
| `skip_setup` | 在 Data 种子中标记 Setup 完成 |

设备仓库为私有仓库时，添加仓库 secret `UNIXNU_DEVICE_TOKEN`。

workflow 在安装和构建前检查输入、defconfig、Xcode 路径和平台种子。它只发布 `*.log` 文件，替换其中的密钥和签名 URL，并写入每一步的结果摘要。

需要 bootstrap 候选、显示 ABI 证据或预置 kernelcache 的设备静态库链使用 `pre_build`。命令在检出之后、内核构建之前运行。workflow 在结束时删除抓取的 IPSW、feeds 和固件缓存。

bootstrap 候选示例：

```sh
./unixnu defconfig bootstrap_defconfig -D "$DEVICE_DIR"
./unixnu build kernel -D "$DEVICE_DIR"
mkdir -p out/<device>/<os_profile>/<config>/tree/build/xnu-prelink
cp out/<device>/<os_profile>/<config>/kernel/kernel.macho \
   out/<device>/<os_profile>/<config>/tree/build/xnu-prelink/<candidate>.macho
```

候选名称以及显示和 kernelcache 输入由设备仓库决定。

workflow 运行 kernel、userdata 和 payload。package、firmware 和 boot image 命令在受支持的 macOS 或 Linux 主机上执行。使用托管构建前检查 workflow 和账户 runner 配置。

## Linux 主机

安装脚本在 glibc Linux 上支持 apt、dnf、pacman 和 zypper。依赖已准备好时使用 `--package-manager none`，指定主机 LLVM 时使用 `--llvm-config FILE`。详见 [Linux 要求](/zh/guide/requirements#linux)。

一次性安装工具链后，内核步骤可以在 Linux 上运行（见[构建环境](/zh/guide/requirements#linux)）：

```sh
scripts/linux/setup-toolchain.py --print-packages
sudo scripts/linux/setup-toolchain.py
./unixnu defconfig <name> -D ../UniXNU-<device>
./unixnu fetch
./unixnu build kernel
```

驱动按主机选择 Linux 路径。它设置工具链环境，`build-xnu-4k-baseline.sh` 运行 `scripts/linux/prepare-xnu.py`：

- `source`，在 xnu 补丁之后：改写少数依赖 Apple clang 或 BSD 工具的 xnu 源码（SHA 与 AES 汇编宏、mawk 下的系统调用表生成脚本、`kextsymboltool` 写入 `/dev/null`），并把 `TargetConditionals.h` 装入 fakeroot。
- `libs`，在头文件之后：用 compiler-rt 构建 `libcc_kext.a`。Mac 上这个库来自 Apple clang。

`build-firehose.sh` 不经 Xcode 编译 `libfirehose_kernel`，`build-corecrypto-14.py` 用 `scripts/pbxproj.py` 代替 `plutil` 读取 corecrypto 工程，kernelcache 用 `lzfse` 解码。

Linux 路径使用相同的选定 profile、归档配方和预链接检查。随构建结果记录主机工具链；设备配方可能还需要 SDK 或镜像工具。

## 命令

| 命令 | 作用 |
| --- | --- |
| `defconfig [NAME]` | 列出设备仓库的 `configs/*_defconfig`，或将选中配置合并到目标 `.config`。 |
| `fetch [NAME...] [--update]` | 拉取 git 源码并把 commit 写入设备仓库的 `unixnu.lock`。`--update` 更新未显式固定的 ref，格式 2 中明确指定的 commit 保持优先。 |
| `tree` | 解析模块、拉取步骤需要的参考源码，并组装 `out/<device>/<os_profile>/<config>/tree`。 |
| `ipsw info` | 打印目标 IPSW 的产品、build 和全部组件。 |
| `ipsw fetch [COMPONENT...]` | 把指定组件解压到 `out/ipsw/<build>/`。 |
| `build [kernel] [package] [firmware] [payload] [prelink]` | 执行指定步骤。默认执行四个步骤。`prelink` 只重做预链接。 |
| `build userdata [--dry-run]` | 构建 userdata 原始镜像。该步骤较大，只在显式指定时执行。 |
| `bootimg` | 把 BootShim、固件卷、设备树和可选负载打包为 Android 启动镜像。 |
| `status` | 打印设备、配置和每个模块的来源。 |
| `clean` | 删除目标目录中的 `tree`、`logs`、`kernel`、`package`、`boot` 和 `edk2-conf`。 |

## 常用选项

| 选项 | 含义 |
| --- | --- |
| `-D DIR` | 设备仓库，首次使用后会记住。 |
| `--out DIR` | 输出根目录，默认是本仓库的 `out/`。 |
| `-j N` | 并行任务数，默认取 `JOBS` 或 CPU 数量。 |
| `--target DEBUG\|RELEASE` | EDK II 构建目标，默认 `DEBUG`。 |
| `--uefi DIR` | 设备的 Mu-Silicium 仓库。 |
| `--edk2 DIR` | Mu_Basecore 仓库。 |
| `--kernelcache FILE` | 原始解压 kernelcache。 |
| `--kernel FILE` | 负载使用的预链接内核。 |
| `--kernel-arg NAME[=VALUE]` | 额外内核参数；与 `[payload] kernel_args` 同名时替换，可重复。 |
| `--trust-cache FILE` | trust cache 包。 |
| `--owner-trust-cache FILE` | owner 签名的包，包含原始缓存和额外模块。替换 `--trust-cache`，并跳过板级允许列表。 |
| `--data-ramdisk FILE` | Data ramdisk 种子。 |
| `--skip-setup` | 在 Data 种子副本中把 Setup 标记为完成，需要 `--data-ramdisk`。 |
| `--unique-chip-id HEX` | 设备树平台种子。 |
| `--ipsw PATH_OR_URL` | 目标 IPSW，本地或远程。 |
| `--skip-preflight` | 跳过固件步骤的板级预检脚本。 |
| `--dry-run` | 仅 userdata：检查大小和哈希，不写文件。 |

环境变量 `UNIXNU_DEVICE`、`UNIXNU_OUT`、`UNIXNU_UEFI`、`UNIXNU_EDK2`、`UNIXNU_KERNELCACHE`、`UNIXNU_DTB`、`UNIXNU_IPSW`、`UNIXNU_UNIQUE_CHIP_ID` 和 `JOBS` 提供相同取值。

## 步骤

### defconfig

`defconfig` 按顺序合并配置片段，再应用所选设备 defconfig，将结果写入目标 `.config`。构建前拒绝格式错误的行。

### fetch

`fetch` 解析模块并拉取 git 源码。它使用浅克隆、blobless 过滤和 cone sparse checkout，格式 2 按仓库和选定版本缓存。解析后的 commit 写入设备仓库的 `unixnu.lock`，显式 source commit 优先于已有锁记录。

### tree

`tree` 按脚本期望的布局组装 `out/<device>/<os_profile>/<config>/tree`：

```
tree/
  drivers/ kits/ patches/ refer/
  scripts/ package/
  build/ .cache/
```

模块是指向源码的符号链接，脚本会复制。设备 `package/` 出现在 `kits/<board.kit>`。`.cache/firmware` 指向设备仓库的 `.cache/firmware`，每个构建树使用同一份专有文件。

### ipsw

IPSW 按成员读取，远程 IPSW 不会整体下载。zip 目录和需要的成员通过 HTTP range 请求读取。解压的成员缓存在 `out/ipsw/<build>/`，并按 `board.toml [ipsw.sha256]` 的哈希校验。

镜像必须匹配 `[ipsw]` 的产品、版本、build、device class、chip ID 和 board ID。

### kernel

内核步骤：

1. 解析声明的补丁系列与组件补丁，应用到目标独立的 XNU 源码。格式 1 使用其目录补丁顺序。
2. 运行 `prepare-xnu-source.py` 恢复缺失的 DriverKit 头文件。
3. `startup.o.json` 不存在时，先运行一次 XNU 以生成编译记录。该轮可以在链接前停止。
4. 按顺序运行所选组件构建命令和 `[kernel] archives` 辅助命令，`component:<ID>` 指定组件位置，依赖先运行。
5. 为 `ARM64`、机型 `BCM2837`、配置 `DEVELOPMENT`、iOS 17 构建 XNU，并链接静态库。
6. 用 `kits/XnuPrelink` 把原生内核与原始 kernelcache 预链接。重建会替换上一轮的结果。

kernelcache 来自 IPSW，除非 `--kernelcache` 指定文件。`KernelCache` IM4P 的 LZFSE 负载由 macOS `compression_tool`（Linux 上为 `lzfse`）解码，选出 arm64 切片，并按 `[kernel.prelink] kernelcache_sha256` 校验。

输出为 `out/<device>/<os_profile>/<config>/kernel/kernel.macho`。

### package

package 步骤用 EDK II 构建 `package/`，输出到 `out/<device>/<os_profile>/<config>/package/Build/Out`，包含 `UniXNU.efi`、`UniXNUDxe.efi`、`UniXNURamDiskDxe.efi`、`HelloPayload.efi`、`SampleDriver.efi` 和 `XnuTest.efi`。

### firmware

固件步骤从 Mu-Silicium 仓库构建设备固件：

1. 运行板级预检脚本。
2. 把板级补丁应用到共享 edk2 树，构建后还原。
3. 用板级 DSC 和 defines 运行 EDK II `build`。

`FD_BASE`、`FD_SIZE`、`FD_BLOCKS` 来自 Mu-Silicium 设备配置。固件卷大小必须匹配 `[uefi_fd] size`。

### payload

负载步骤写一个 FAT 卷，包含：

- `EFI/UniXNU/unixnu.toml`
- `EFI/UniXNU/Payloads/kernel.macho`
- `EFI/UniXNU/Payloads/kernel.macho.adt`
- 可选的 `kernel.macho.trustcache`
- 可选的 `scratch-data.img`

内核命令行来自 `[payload] kernel_args`。额外的 `--kernel-arg NAME=VALUE` 替换板级同名参数。卷用 mtools 写入，不挂载。输出为 `out/<device>/<os_profile>/<config>/payload/payload.img` 和 `payload.json`。

`--owner-trust-cache` 传入 owner 签名的包，包含原始缓存和额外模块。它替换 `--trust-cache`，并跳过 `[payload] trust_cache_sha256`。

`--skip-setup` 在 `--data-ramdisk` 提供的 Data 种子副本中把 Setup 标记为完成。

### userdata

userdata 步骤构建 `userdata` 分区的原始镜像，保存 IPSW 中未修改的 `OS` 和 `SystemOS` 磁盘镜像，前置 `SHNGROOT` manifest。macOS 上磁盘镜像用 `hdiutil` 只读挂载；Linux 上由 `scripts/unixnu/udif.py` 解码，LZFSE 块用 `lzfse` 解压。两者得到相同的字节。输出为 `out/<device>/<os_profile>/<config>/userdata/userdata-root.img` 和 `userdata-root.json`，报告会打印 `fastboot flash userdata` 命令。

### bootimg

启动镜像步骤：

1. 按固件基址和大小编译 BootShim。
2. 追加固件卷。
3. 用 gzip 压缩。
4. 应用 `[[bootimg.dtb_node]]` 后追加设备树。
5. 用 Mu-Silicium 设备配置中的参数调用 `mkbootimg.py`。
6. 解包镜像并逐部分与输入比较。

ramdisk 优先使用负载输出，也可以用 `--ramdisk FILE`，或用 `--ramdisk none` 使用空 ramdisk。

## 本地模块

模块可以来自本地目录，第一个匹配生效：

1. `--local-module [KIND:]NAME=PATH`
2. `--local-drivers|kits|patches|scripts|package DIR`
3. `--local DIR`，目录布局与本仓库相同
4. `feeds.toml` 中的 `local = "DIR"`，或设备仓库的 `local.toml`
5. 设备仓库
6. 本仓库
7. `feeds.toml` 中的 git 源码

本地模块以符号链接进入构建树。`unixnu status` 会标记它们，并报告它们没有锁文件固定。

## 输出

全部输出位于 `out/`：

| 路径 | 内容 |
| --- | --- |
| `out/state.json` | 记住的设备仓库 |
| `out/feeds/` | 拉取的源码 |
| `out/ipsw/<build>/` | 解压的 IPSW 成员 |
| `out/<device>/<os_profile>/<config>/.config` | 选中的 defconfig |
| `out/<device>/<os_profile>/<config>/tree/` | 组装后的构建树 |
| `out/<device>/<os_profile>/<config>/logs/` | 步骤日志 |
| `out/<device>/<os_profile>/<config>/kernel/kernel.macho` | 预链接内核 |
| `out/<device>/<os_profile>/<config>/package/Build/Out/` | EFI 程序 |
| `out/<device>/<os_profile>/<config>/payload/` | 负载镜像与报告 |
| `out/<device>/<os_profile>/<config>/boot/` | 启动镜像与报告 |
| `out/<device>/<os_profile>/<config>/userdata/` | userdata 镜像与报告 |

## 可复现性

`unixnu.lock` 固定每个拉取的源码。固件构建把 `SOURCE_DATE_EPOCH` 设为 Mu-Silicium 的 commit 时间，EDK II 不会写入构建时间。给定固件卷、设备树和 ramdisk 时启动镜像确定。负载包含随机种子，两次构建不同。

## 下一步

- [构建内核](/zh/guide/build-kernel)介绍内核开关和静态库。
- [启动镜像](/zh/guide/boot)介绍 fastboot 命令。
- [参考](/zh/reference/output-layout)列出报告字段。
