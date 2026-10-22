# 设备仓库

设备仓库描述一块板子，并提供与通用树不同的模块。

## 布局

```
UniXNU-<device>/
  board.toml                  板级描述
  configs/<name>_defconfig    内核配置
  feeds.toml                  可选外部源码
  local.toml                  可选本地覆盖，Git 忽略
  drivers/                    设备 XNU 驱动
  kits/                       设备内核库
  patches/                    设备补丁
  scripts/                    构建和 bring-up 脚本
  package/                    UniXNU kit 内容
  .gitmodules                 模块子模块
  .cache/firmware/            专有输入，不跟踪
  unixnu.lock                 unixnu fetch 写入
```

目录布局与 `UniXNU` 相同。设备仓库中的同名模块覆盖基础仓库模块。设备驱动和 kit 是独立仓库，以子模块形式引入。

## board.toml

### 板级

```toml
[board]
name = "<device>"
soc = "<SoC>"
description = "<device description>"
kit = "<kit>"
# example = true
```

| 键 | 含义 |
| --- | --- |
| `name` | `out/` 下的输出目录名 |
| `soc` | 报告和脚本使用的 SoC 标识 |
| `description` | 可读描述 |
| `kit` | 设备 package 在 `kits/` 下的目录名 |
| `example` | 标记示例仓库，`build` 和 `bootimg` 会拒绝 |

### IPSW

```toml
[ipsw]
url = "https://example.invalid/restore.ipsw"
product = "<product>"
version = "<version>"
build = "<build>"
device_class = "<device class>"
chip_id = 0x0000
board_id = 0

fetch = ["KernelCache", "DeviceTree", "StaticTrustCache", "Cryptex1,SystemTrustCache"]

[ipsw.sha256]
"<member file>" = "<sha256>"
```

`url` 是默认来源，`--ipsw` 或 `UNIXNU_IPSW` 覆盖。镜像必须匹配产品、版本、build、device class、chip ID 和 board ID。

`fetch` 列出 `unixnu ipsw fetch` 无参数时提取的组件。`[ipsw.sha256]` 按成员文件名固定哈希。

### userdata

```toml
[userdata]
first_lba = 0x0
last_lba = 0x0
lba_bytes = 4096
windows = [
  { name = "OS", component = "OS" },
  { name = "SystemOS", component = "Cryptex1,SystemOS" },
]
```

`first_lba` 和 `last_lba` 来自名为 `userdata` 的 GPT 条目，`lba_bytes` 是逻辑块大小。每个窗口指定 IPSW 磁盘镜像组件。

### 内核

```toml
[kernel]
defconfig = "<name>_defconfig"
archives = [
  "scripts/build-native-aes-bindings.py",
  "scripts/build-libpthread-kernel.py",
  "scripts/build-corecrypto-14.py",
  "scripts/build-corecrypto-14.py --namespace",
]

[kernel.prelink]
tool = "kits/NativePrelink/emit_prelink.py"
kernel = "build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/mach.development.bcm2837.unstripped.noctf"
kernelcache_sha256 = "..."
slide = "-0x1000000"
early_security_init = "com.apple.driver.AppleMobileFileIntegrity=0xfffffff005ab4ae0"
roots = [
  "com.apple.driver.AppleARMPlatform",
  "com.apple.filesystems.apfs",
]
extra_args = []
```

| 键 | 含义 |
| --- | --- |
| `defconfig` | `configs/` 下的文件名 |
| `archives` | 静态库脚本，在链接内核前按顺序执行 |
| `tool` | 构建树中的预链接工具 |
| `kernel` | 构建树中的原生内核 |
| `kernelcache_sha256` | 固定原始 kernelcache |
| `slide` | 选中组件的地址 slide |
| `early_security_init` | 早期初始化器的组件标识和地址 |
| `roots` | 保留的原始 kernelcache bundle identifier |
| `extra_args` | 预链接工具的额外参数 |

### 固件

```toml
[firmware]
config = "<name>"
dsc = "Platforms/<Vendor>/<device>Pkg/<device>.dsc"
fd = "Build/<device>Pkg/{target}_CLANGPDB/FV/SILICIUM_UEFI.fd"
preflight = ["scripts/check-<device>.py"]
submodules = []
patches = ["Resources/MuPatches/<patch>.patch"]
packages = [
  "{uefi}",
  "{tree}/package",
  "{tree}/drivers/DarwinBoot",
  "{edk2}",
]

[firmware.defines]
DEVICE_MODEL = "<device>"
```

| 键 | 含义 |
| --- | --- |
| `config` | Mu-Silicium 中的 `Resources/Configs/<name>.toml` |
| `dsc` | 相对仓库根目录的 DSC |
| `fd` | 固件卷路径，`{target}` 替换为 `DEBUG` 或 `RELEASE` |
| `preflight` | 构建树中的预检脚本 |
| `submodules` | 板级需要的 Mu-Silicium 子模块 |
| `patches` | 构建期间应用到共享 edk2 树、之后还原的补丁 |
| `packages` | `PACKAGES_PATH` 条目，`{uefi}`、`{edk2}`、`{tree}` 会被替换 |
| `defines` | EDK II 额外 `-D` 定义 |

### 启动镜像

```toml
[bootimg.image]
base = 0x0
kernel_offset = 0x8000
tags_offset = 0x1e00000
pagesize = 4096
header_version = 0

[[bootimg.dtb_node]]
path = "/reserved-memory/<region>"
props = [
  { name = "label", type = "s", value = "<label>" },
  { name = "reg", type = "x", value = ["0x0", "0x80000000", "0x0", "0x100000"] },
]
```

镜像参数默认来自 Mu-Silicium 设备配置，`[bootimg.image]` 覆盖。每个 `[[bootimg.dtb_node]]` 在设备树追加到启动镜像前加入节点或属性。原有 bootloader 有时需要 splash 或 reserved-memory 节点。

### 负载

```toml
[payload]
volume = "<label>"
size_mib = 192
loader = "firmware"
title = "UniXNU"
dram_size = "0x80000000"
panic_screen = true
skip_setup_tool = "scripts/seed-data-skip-setup.py"
trust_cache_sha256 = ["<sha256>"]
timeout = 3

kernel_args = ["-v", "serial=3"]

[payload.adt]
tool = "scripts/make-<device>-adt.py"
chip_id = "0"
owned_memory_size = "0x10000000"
root_match_volume_uuid = "00000000-0000-0000-0000-000000000000"
cpu_regs = "0,0x100"
psci_method = "smc"
packed_data_ramdisk = true
ipad_identity = true
unique_chip_id = "required"
```

| 键 | 含义 |
| --- | --- |
| `volume` | FAT 卷标，最多 11 字符 |
| `size_mib` | 卷大小 |
| `loader` | DarwinBoot 在固件卷中时用 `firmware` |
| `title` | 菜单标题 |
| `dram_size` | 传给 ADT 工具的 DRAM 大小 |
| `panic_screen` | 把 panic 屏幕打进负载内核副本 |
| `entry_probe_reset_*` | 保留入口探针的定时复位，可改到某个调用之后（见[调试](/zh/guide/debugging)） |
| `skip_setup_tool` | `--skip-setup` 使用的脚本 |
| `skip_setup_args` | 传给该脚本的额外参数，例如 `["--no-auto-dim"]` |
| `trust_cache_sha256` | 接受的 trust cache 哈希 |
| `timeout` | 菜单超时 |
| `kernel_args` | 默认内核命令行 |

`--owner-trust-cache` 传入 owner 签名的包，包含原始缓存和额外模块。它替换 `--trust-cache`，并跳过 `trust_cache_sha256`。

`[payload.adt]` 的键传给 ADT 工具。工具契约由设备决定，通用键见[设备树](/zh/porting/device-tree)。

## defconfig

`configs/<name>_defconfig` 使用 Linux defconfig 语法：

```
CONFIG_XNU_ARM_DT_PLATFORM=y
CONFIG_XNU_ARMCPU=y
CONFIG_XNU_NATIVE_UFS=y
CONFIG_XNU_NATIVE_CS_HASH_CACHE=y
# CONFIG_XNU_ARMVIRT_PLATFORM is not set
CONFIG_XNU_CRYPTO_BOOTSTRAP="prelinked"
CONFIG_XNU_OWNER_DATA_VOLUME_UUID="00000000-0000-0000-0000-000000000000"
CONFIG_XNU_OWNER_CACHE_VOLUME_UUID="00000000-0000-0000-0000-000000000000"
```

取值可以是 `y`、`n`、数字或带引号字符串。每个 `CONFIG_XNU_<NAME>` 变成内核构建的 `XNU_<NAME>`，字符串中的 `{tree}` 替换为构建树路径。

`CONFIG_XNU_OWNER_CACHE_VOLUME_UUID` 指定 owner 链作为缓存载体挂载的 SystemOS cryptex 卷，即签名 SystemOS 策略所覆盖镜像中的 APFS 卷 UUID。不设置时，内核使用 sheng 镜像的卷。

## feeds.toml

设备仓库可以追加源码：

```toml
[[source]]
name = "DeviceKit"
kind = "kit"
git = "https://github.com/ORG/REPO"
ref = "main"
path = "kits/DeviceKit"
commit = "..."
local = "~/Code/device-kit"
```

kind 为 `driver`、`kit`、`patch`、`package` 或 `refer`。`path` 只拉取子目录，`local` 使用本地目录。

基础 `feeds.toml` 提供 `xnu`、`libplatform`、`libdispatch`、`AvailabilityVersions`、`edk2`、`libpthread` 和 `corecrypto-2023`。

## 专有文件

设备仓库把专有输入放在 `.cache/firmware`。构建树链接到该目录，每个构建树和每次重建都使用同一份文件，不把它们复制进仓库。

## 本地开发

第一个匹配生效：

1. `--local-module [KIND:]NAME=PATH`
2. `--local-<kind> DIR`
3. `--local DIR`
4. `feeds.toml` 的 `local` 键或 `local.toml` 条目
5. 设备仓库
6. 基础仓库
7. `feeds.toml` 的 git 源码

本地模块以符号链接进入 `out/<board>/tree`。`unixnu status` 会标记它们并报告锁文件未固定。

## package 与 kit

设备 `package/` 在构建树中成为 `kits/<board.kit>`。package 可以包含 `unixnu.toml`、kit 目录、驱动、设备树 overlay 和 kext 包。

kit 目录包含 `Kit.toml`：

```toml
schema = 1

[kit]
name = "<kit>"
version = "1.0.0"
description = "<description>"

[match]
arch = "AARCH64"
fdt_compatible = ["<compatible>"]
firmware_vendor = ["<vendor>"]
requires_protocol = ["<guid>"]

[[driver]]
file = "<driver>.efi"
args = "<load options>"

[[overlay]]
file = "<overlay>.dtbo"

[[kext]]
bundle = "<name>.kext"
entry = "<entry id>"
```

`[match]` 的键全部需要满足。同一个键内任意值匹配。不匹配的 kit 会被跳过并计入菜单摘要。

## 下一步

- [UEFI 固件](/zh/porting/uefi-firmware)
- [设备树](/zh/porting/device-tree)
- [设备配置参考](/zh/reference/configuration)
- [设备](/zh/devices/)
