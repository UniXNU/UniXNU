# 设备配置

格式 2 在 `board.toml` 顶层设置 `schema_version = 2`。省略该字段时使用格式 1。
配置归属和示例见[设备仓库规范](/zh/porting/device-repository)。

## 本地构建参数 {#local-build-inputs}

在 UniXNU 仓库中将 `unixnu.example.toml` 复制为 `unixnu.local.toml`，填写设备路径。Git 忽略此文件。使用 `--config /path/to/build.toml` 选择其他文件。

```toml
[build]
device = "../UniXNU-<device>"
uefi = "../uefi-<device>"
dtb = "/path/to/firmware.dtb"
kernelcache = "/path/to/kernelcache"
trust_cache = "/path/to/trustcache.bundle"
data_ramdisk = "/path/to/data-seed.dbr"
unique_chip_id = "<hex>"
jobs = 8
target = "DEBUG"
kernel_args = ["-v", "serial=3", "debug=0x14e"]
```

将占位符替换为设备所需输入。相对路径从配置文件所在目录解析。优先级为命令行、环境变量、本地文件、设备默认值。`kernel_args` 按名称覆盖板级参数，`--kernel-arg` 按名称覆盖本地参数。

路径字段包括 `device`、`out`、`uefi`、`edk2`、`kernelcache`、`kernel`、`trust_cache`、`owner_trust_cache`、`data_ramdisk`、`gpu_addon`、`dtb`、`fd`、`ramdisk` 和 `output`。其他字段为 `ipsw`（路径或 URL）、`unique_chip_id`（十六进制字符串）、`jobs`（正整数）、`target`（`DEBUG` 或 `RELEASE`）、`kernel_args`（字符串数组）。`ramdisk = "none"` 选择空启动镜像 ramdisk。

```sh
./unixnu defconfig <device>_defconfig
./unixnu kernel
./unixnu firmware
./unixnu payload
./unixnu bootimg
./unixnu status --json
```

`status` 的 `build_config` 字段显示选中的文件。`unixnu.local.toml` 保存构建输入，设备仓库的 `local.toml` 保存组件源码覆盖路径。

## 配置字段

| 表 | 键 | 含义 |
| --- | --- | --- |
| `board` | `soc_source` | 固定的 `kind = "soc"` 源码名称 |
| `board` | `os_profile` | `profiles/os/` 下的目录名 |
| `components` | `include` | 规范组件 ID，依赖按构建顺序解析 |
| `kernel` | `config_fragments` | 有序的配置片段 |
| `kernel` | `patch_series` | 有序的 series 文件 |
| `device_tree` | `source` | DTS 入口，例如 `device:dts/sheng.dts` |
| `device_tree` | `include_dirs` | DTS 包含路径，例如 `soc:dts` |

配置层按 ARM64、SoC、OS、设备顺序应用。表按键合并，数组替换。
所选 defconfig 在 `config_fragments` 之后应用。路径前缀为 `arch:`、`soc:`、`os:`
和 `device:`。series 条目还支持 `component:<ID>/path`。
`unixnu status --json` 显示最终配置。

## board.toml

### [board]

| 键 | 类型 | 含义 |
| --- | --- | --- |
| `name` | 字符串 | 输出目录名 |
| `soc` | 字符串 | SoC 标识 |
| `description` | 字符串 | 可读描述 |
| `kit` | 字符串 | 设备 package 在 `kits/` 下的目录 |
| `example` | 布尔 | 标记示例，build 和 bootimg 会拒绝 |

### [ipsw]

| 键 | 类型 | 含义 |
| --- | --- | --- |
| `url` | 字符串 | 默认远程 IPSW |
| `product` | 字符串 | 产品类型，例如 `iPad7,1` |
| `version` | 字符串 | 产品版本 |
| `build` | 字符串 | 产品 build |
| `device_class` | 字符串 | manifest 中的 device class |
| `chip_id` | 整数 | `ApChipID` |
| `board_id` | 整数 | `ApBoardID` |
| `fetch` | 数组 | `ipsw fetch` 提取的组件 |

### [ipsw.sha256]

| 键 | 类型 | 含义 |
| --- | --- | --- |
| 成员文件 | 字符串 | 解压成员的期望 SHA-256 |

### [userdata]

| 键 | 类型 | 含义 |
| --- | --- | --- |
| `first_lba` | 整数 | userdata GPT 条目起始 LBA |
| `last_lba` | 整数 | userdata GPT 条目结束 LBA |
| `lba_bytes` | 整数 | 逻辑块大小 |
| `windows` | 数组 | `{ name, component }` 条目 |

### [kernel]

| 键 | 类型 | 含义 |
| --- | --- | --- |
| `defconfig` | 字符串 | `configs/` 下的文件名 |
| `archives` | 数组 | 构建树中的静态库脚本，在链接内核前按顺序执行 |

### [kernel.prelink]

| 键 | 类型 | 含义 |
| --- | --- | --- |
| `tool` | 字符串 | 构建树中的预链接工具 |
| `kernel` | 字符串 | 构建树中的原生内核 |
| `slide` | 字符串 | 地址 slide |
| `roots` | 数组 | 保留的 kernelcache bundle identifier |
| `early_security_init` | 字符串 | `identifier=address` |
| `kernelcache` | 字符串 | 可选本地 kernelcache 路径 |
| `kernelcache_sha256` | 字符串 | 期望 kernelcache 哈希 |
| `extra_args` | 数组 | 预链接额外参数 |

### [firmware]

| 键 | 类型 | 含义 |
| --- | --- | --- |
| `config` | 字符串 | Mu-Silicium `Resources/Configs/<name>.toml` |
| `dsc` | 字符串 | 仓库中的 DSC 路径 |
| `fd` | 字符串 | 固件卷路径，`{target}` 替换 |
| `packages` | 数组 | `PACKAGES_PATH` 条目 |
| `preflight` | 数组 | 构建树预检脚本 |
| `patches` | 数组 | 构建期间应用到 edk2 的补丁 |
| `submodules` | 数组 | 需要初始化的 Mu-Silicium 子模块 |

### [firmware.defines]

| 键 | 类型 | 含义 |
| --- | --- | --- |
| 任意 | 字符串 | EDK II 构建的 `-D NAME=VALUE` |

### [bootimg.image]

| 键 | 类型 | 含义 |
| --- | --- | --- |
| `base` | 整数 | 镜像基址 |
| `kernel_offset` | 整数 | 内核偏移 |
| `tags_offset` | 整数 | tags 偏移 |
| `pagesize` | 整数 | 镜像页大小 |
| `header_version` | 整数 | Android 启动镜像 header 版本 |
| `kernel_compression` | 字符串 | `gzip`（默认）或 `none`，决定内核在启动镜像中的存储方式 |

### [[bootimg.dtb_node]]

| 键 | 类型 | 含义 |
| --- | --- | --- |
| `path` | 字符串 | 设备树节点路径 |
| `props` | 数组 | `{ name, type, value }` |

类型为 `s` 字符串、`x` 十六进制 cell、`i` 十进制 cell、`u` 无符号 cell、`empty`。

### [payload]

| 键 | 类型 | 含义 |
| --- | --- | --- |
| `volume` | 字符串 | FAT 卷标，最多 11 字符 |
| `size_mib` | 整数 | 卷大小 |
| `loader` | 字符串 | `firmware` 或驱动加载模式 |
| `title` | 字符串 | 菜单标题 |
| `dram_size` | 字符串 | ADT 使用的 DRAM 大小 |
| `panic_screen` | 布尔 | 把 panic 屏幕打进负载内核 |
| `trust_cache_sha256` | 数组 | 接受的 trust cache 哈希。用 `--owner-trust-cache` 传入的 owner 包跳过此列表 |
| `kernel_args` | 数组 | 默认内核参数 |
| `tools` | 布尔 | 在生成的菜单中加入 Tools；按[日志抓取步骤](/zh/porting/log-capture#firmware-setup)配置插件 |
| `timeout` | 整数 | 菜单超时 |
| `skip_setup_tool` | 字符串 | `--skip-setup` 使用的脚本 |

### [payload.adt]

| 键 | 类型 | 含义 |
| --- | --- | --- |
| `tool` | 字符串 | ADT 生成器路径 |
| `chip_id` | 字符串 | ADT 芯片 ID |
| `owned_memory_size` | 字符串 | 连续窗口请求 |
| `root_match_volume_uuid` | 字符串 | 根卷 UUID |
| `cpu_regs` | 字符串 | CPU MPIDR 值，逗号分隔 |
| `psci_method` | 字符串 | `smc` 或 `hvc` |
| `packed_data_ramdisk` | 布尔 | 使用 packed Data 格式 |
| `ipad_identity` | 布尔 | 写入 Apple 设备身份属性 |
| `unique_chip_id` | 字符串 | 种子必需时写 `required` |

## defconfig

```
CONFIG_NAME=y
CONFIG_NAME=n
CONFIG_NAME="text"
CONFIG_NAME=123
# CONFIG_NAME is not set
```

每个 `CONFIG_XNU_<NAME>` 变成 `XNU_<NAME>`，字符串中的 `{tree}` 替换为构建树路径。

## feeds.toml

```toml
[[source]]
name = "Name"
kind = "driver"          # driver、kit、patch、package、refer
git = "https://github.com/ORG/REPO"
ref = "main"
path = "drivers/Name"
commit = "..."
local = "/path/to/local"
submodules = []
```

| 键 | 含义 |
| --- | --- |
| `name` | 模块名 |
| `kind` | 模块类型 |
| `git` | 源码仓库 |
| `ref` | 拉取的分支、tag 或 commit |
| `path` | 可选子目录，sparse 拉取 |
| `commit` | 可选固定 commit |
| `local` | 使用本地目录 |
| `submodules` | 初始化的上游子模块 |

## local.toml

设备仓库中被 Git 忽略的文件：

```toml
[local]
drivers = "/path/to/drivers"
kits = "/path/to/kits"
patches = "/path/to/patches"
scripts = "/path/to/scripts"
package = "/path/to/package"
```

## unixnu.lock

```toml
[source."Name"]
commit = "0123456789abcdef"
```

由 `unixnu fetch` 写入，记录 Git 源码版本。格式 2 中显式源码 commit 优先于 lock，包括所选 OS 的 XNU 版本。格式 1 使用 lock 优先顺序。官方别名可复用兼容名称对应的 lock 条目。

## 模块解析

1. `--local-module [KIND:]NAME=PATH`
2. `--local-<kind> DIR`
3. `--local DIR`
4. `feeds.toml` 的 `local` 键或 `local.toml`
5. 设备仓库
6. 基础仓库
7. `feeds.toml` 的 git 源码

第一个匹配生效。

## 下一步

- [启动配置](/zh/reference/boot-configuration)
- [设备仓库](/zh/porting/device-repository)
- [命令行](/zh/reference/cli)
