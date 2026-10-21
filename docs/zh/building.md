# 构建

`unixnu` 是构建驱动。它读取设备仓库、解析模块、组装构建树，并按步骤执行。

## 快速开始

```sh
git clone --recurse-submodules https://github.com/UniXNU/UniXNU
git clone --recurse-submodules https://github.com/UniXNU/UniXNU-sheng
git clone https://github.com/UniXNU/uefi-sheng
cd UniXNU

# 已有克隆：
git submodule update --init --recursive

./unixnu defconfig sheng_defconfig -D ../UniXNU-sheng
./unixnu fetch
./unixnu ipsw fetch
./unixnu build kernel
./unixnu build package
./unixnu build firmware --uefi ../uefi-sheng
./unixnu bootimg --uefi ../uefi-sheng --dtb /path/to/device.dtb
```

第一次使用 `-D` 后，设备仓库会记录在 `out/state.json` 中。

启动镜像位于 `out/<board>/boot/boot.img`，旁边的 `boot.json` 是报告。选项写在子命令之后。

## macOS runner

内核、userdata 和 Data 种子步骤调用 Xcode、`hdiutil` 和 `diskutil`。fork 后可以在 GitHub 的 macOS runner 上运行这些步骤，不需要本地 Mac。

1. fork 仓库并启用 Actions。
2. 板级需要平台种子时，添加仓库 secret `UNIXNU_UNIQUE_CHIP_ID`。
3. 运行 `macOS build` workflow，选择设备仓库、ref、defconfig 和步骤。
4. 从运行结果下载 artifact。

| 输入 | 含义 |
| --- | --- |
| `device_repository` | 设备仓库，格式 `owner/name` |
| `device_ref` | 设备仓库的 ref |
| `defconfig` | defconfig 名称 |
| `steps` | `kernel`、`kernel userdata` 或 `kernel userdata payload`，默认 `kernel userdata` |
| `ipsw_url` | 可选 IPSW URL，空值使用 `board.toml` |
| `pre_build` | 可选 shell 命令，在内核构建前于 UniXNU 检出目录运行。设备仓库位于 `DEVICE_DIR` |
| `trust_cache_url` | 可选 trust cache 包 URL |
| `owner_trust_cache` | 把该 URL 当作 owner 签名的包 |
| `data_seed_url` | 可选 Data 种子 URL |
| `grow_gib` | 把 Data 种子增长到该大小 |
| `skip_setup` | 在 Data 种子中标记 Setup 完成 |
| `upload_userdata` | 上传 userdata 镜像。该镜像很大 |

设备仓库为私有仓库时，添加仓库 secret `UNIXNU_DEVICE_TOKEN`。

需要 bootstrap 候选、显示 ABI 证据或预置 kernelcache 的设备静态库链使用 `pre_build`。命令在 `unixnu fetch` 之后、`unixnu build kernel` 之前运行。workflow 在上传 artifact 后删除抓取的 IPSW、抓取的 feeds 和预置的固件缓存。

bootstrap 候选示例：

```sh
./unixnu defconfig bootstrap_defconfig -D "$DEVICE_DIR"
./unixnu build kernel -D "$DEVICE_DIR"
mkdir -p out/<board>/tree/build/native-prelink
cp out/<board>/kernel/kernel.macho \
   out/<board>/tree/build/native-prelink/<candidate>.macho
```

候选名称以及显示和 kernelcache 输入由设备仓库决定。

workflow 运行 kernel、userdata 和 payload。package、firmware 和 boot image 步骤可以在任意系统运行，不在 workflow 中。公开仓库使用免费的 macOS runner 配额，私有仓库消耗 Actions 分钟。

## 命令

| 命令 | 作用 |
| --- | --- |
| `defconfig [NAME]` | 列出设备仓库的 `configs/*_defconfig`，或把选中的文件复制到 `out/<board>/.config`。 |
| `fetch [NAME...] [--update]` | 拉取 git 源码并把 commit 写入设备仓库的 `unixnu.lock`。`--update` 忽略锁文件。 |
| `tree` | 解析模块、拉取步骤需要的参考源码，并组装 `out/<board>/tree`。 |
| `ipsw info` | 打印目标 IPSW 的产品、build 和全部组件。 |
| `ipsw fetch [COMPONENT...]` | 把指定组件解压到 `out/ipsw/<build>/`。 |
| `build [kernel] [package] [firmware] [payload] [prelink]` | 执行指定步骤。默认执行四个步骤。`prelink` 只重做预链接。 |
| `build userdata [--dry-run]` | 构建 userdata 原始镜像。该步骤较大，只在显式指定时执行。 |
| `bootimg` | 把 BootShim、固件卷、设备树和可选负载打包为 Android 启动镜像。 |
| `status` | 打印设备、配置和每个模块的来源。 |
| `clean` | 删除板级输出，保留已拉取源码。 |

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

`defconfig` 把 `configs/<name>_defconfig` 复制到 `out/<board>/.config`，并在构建开始前解析文件，拒绝格式错误的行。

### fetch

`fetch` 解析模块并拉取 git 源码。它使用浅克隆、blobless 过滤和 cone sparse checkout，每个仓库与 ref 一个克隆。每个源码的 commit 写入设备仓库的 `unixnu.lock`，后续构建使用锁定的 commit。

### tree

`tree` 按脚本期望的布局组装 `out/<board>/tree`：

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

1. 把 `patches/xnu` 和 `kits/NativePrelink/patches` 应用到固定版本的 XNU 源码。
2. 运行 `prepare-xnu-source.py` 恢复缺失的 DriverKit 头文件。
3. `startup.o.json` 不存在时，先运行一次 XNU 以生成编译记录。该轮可以在链接前停止。
4. 按 `[kernel] archives` 的顺序运行静态库脚本。
5. 为 `ARM64`、机型 `BCM2837`、配置 `DEVELOPMENT`、iOS 17 构建 XNU，并链接静态库。
6. 用 `kits/NativePrelink` 把原生内核与原始 kernelcache 预链接。重建会替换上一轮的结果。

kernelcache 来自 IPSW，除非 `--kernelcache` 指定文件。`KernelCache` IM4P 的 LZFSE 负载由 macOS `compression_tool` 解码，选出 arm64 切片，并按 `[kernel.prelink] kernelcache_sha256` 校验。

输出为 `out/<board>/kernel/kernel.macho`。

### package

package 步骤用 EDK II 构建 `package/`，输出到 `out/<board>/package/Build/Out`，包含 `UniXNU.efi`、`UniXNUDxe.efi`、`HelloPayload.efi`、`SampleDriver.efi` 和 `XnuTest.efi`。

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

内核命令行来自 `[payload] kernel_args`。额外的 `--kernel-arg NAME=VALUE` 替换板级同名参数。卷用 mtools 写入，不挂载。输出为 `out/<board>/payload/payload.img` 和 `payload.json`。

`--owner-trust-cache` 传入 owner 签名的包，包含原始缓存和额外模块。它替换 `--trust-cache`，并跳过 `[payload] trust_cache_sha256`。

`--skip-setup` 在 `--data-ramdisk` 提供的 Data 种子副本中把 Setup 标记为完成。

### userdata

userdata 步骤构建 `userdata` 分区的原始镜像，保存 IPSW 中未修改的 `OS` 和 `SystemOS` 磁盘镜像，前置 `SHNGROOT` manifest。磁盘镜像用 `hdiutil` 只读挂载。输出为 `out/<board>/userdata/userdata-root.img` 和 `userdata-root.json`，报告会打印 `fastboot flash userdata` 命令。

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
| `out/<board>/.config` | 选中的 defconfig |
| `out/<board>/tree/` | 组装后的构建树 |
| `out/<board>/logs/` | 步骤日志 |
| `out/<board>/kernel/kernel.macho` | 预链接内核 |
| `out/<board>/package/Build/Out/` | EFI 程序 |
| `out/<board>/payload/` | 负载镜像与报告 |
| `out/<board>/boot/` | 启动镜像与报告 |
| `out/<board>/userdata/` | userdata 镜像与报告 |

## 可复现性

`unixnu.lock` 固定每个拉取的源码。固件构建把 `SOURCE_DATE_EPOCH` 设为 Mu-Silicium 的 commit 时间，EDK II 不会写入构建时间。给定固件卷、设备树和 ramdisk 时启动镜像确定。负载包含随机种子，两次构建不同。

## 下一步

- [构建内核](/zh/guide/build-kernel)介绍内核开关和静态库。
- [启动镜像](/zh/guide/boot)介绍 fastboot 命令。
- [参考](/zh/reference/output-layout)列出报告字段。
