# 启动负载

负载是一个 FAT 卷，作为 Android 启动镜像的 ramdisk。UniXNU 从中读取配置，DarwinBoot 从中读取内核、ADT 和可选 trust cache。

## 卷布局

```
/EFI/UniXNU/unixnu.toml
/EFI/UniXNU/Payloads/kernel.macho
/EFI/UniXNU/Payloads/kernel.macho.adt
/EFI/UniXNU/Payloads/kernel.macho.trustcache
/EFI/UniXNU/Payloads/scratch-data.img
```

负载步骤用 `mformat` 和 `mcopy` 写卷。时间戳固定为 1980-01-01，相同输入得到相同卷。ADT 包含随机种子，两次负载构建不同。

## 配置

负载步骤写入：

```toml
version = 1

[boot]
timeout = 3
default = "xnu"

[kits]
autoload = false

[[entry]]
id = "xnu"
title = "UniXNU"
type = "xnu"
path = "Payloads/kernel.macho"
initrd = "Payloads/scratch-data.img"
args = "-v serial=3"
```

提供 Data 种子时存在 `initrd`。`args` 是 `[payload] kernel_args` 和 `--kernel-arg` 合并后的命令行。

## ADT sidecar

ADT 使用 Apple 的扁平节点编码。`[payload.adt] tool` 指定的板级脚本生成它。负载步骤传入：

| 选项 | 来源 |
| --- | --- |
| `--output` | `Payloads/kernel.macho.adt` |
| `--dram-size` | `[payload] dram_size` |
| `--owned-memory-size` | `[payload.adt] owned_memory_size` |
| `--root-match-volume-uuid` | `[payload.adt] root_match_volume_uuid` |
| `--chip-id` | `[payload.adt] chip_id` |
| `--cpu-regs` | `[payload.adt] cpu_regs` |
| `--psci-method` | `[payload.adt] psci_method` |
| `--unique-chip-id` | `--unique-chip-id` 或 `UNIXNU_UNIQUE_CHIP_ID` |
| `--packed-data-ramdisk` | `[payload.adt] packed_data_ramdisk` |
| `--data-ramdisk` | 非 packed Data 种子 |
| `--trust-cache` | trust cache 包 |
| `--owner-trust-cache` | owner 签名的包，包含原始缓存和额外模块。它替换 `--trust-cache`，并跳过板级允许列表 |
| `--ipad-identity` | `[payload.adt] ipad_identity` |

ADT 必须为对应输入预留以下属性：

| 属性 | 用途 |
| --- | --- |
| `/chosen/memory-map/RAMDisk` | DarwinBoot 写入 ramdisk 地址和大小 |
| `/chosen/memory-map/PackedRAMDisk` | DarwinBoot 写入 packed ramdisk 地址和大小 |
| `/chosen/memory-map/TrustCache` | DarwinBoot 写入 trust cache 地址和大小 |
| `/chosen/darwinboot-memory-size` | 请求大于 256 MiB 的连续窗口 |

DarwinBoot 要求每个输入都有对应占位符。不匹配时返回 `EFI_COMPROMISED_DATA`。

## 内核参数

写卷前会检查命令行：

- 每个参数匹配 `[A-Za-z0-9_.\-]+`，可选 `=value`，值匹配 `[A-Za-z0-9_.,\-]+`。
- 额外的 `--kernel-arg NAME=VALUE` 会替换板级同名参数。
- 合并后的行不超过 1000 字节。DarwinBoot 把它复制到 1024 字节缓冲区。

命令行以 `args` 写入 `unixnu.toml`，DarwinBoot 原样复制到 `boot_args`。

## trust cache

DarwinBoot 校验 trust cache 包：

- 32 位计数为 1 到 128。
- 每个 cache 一个偏移表项。
- 每个 cache 以版本 2 开头。
- 每个条目 24 字节。
- 哈希类型为 1 到 4。
- 哈希按升序排列。

包被复制到内核窗口，地址和大小替换 `TrustCache` 占位符。

`--owner-trust-cache` 包不经过 `[payload] trust_cache_sha256` 校验。它携带原始缓存和 GPU 插件等额外模块。

## Data ramdisk

Data 种子有两种交付形式：

| 形式 | ADT 占位符 | 行为 |
| --- | --- | --- |
| Dense | `RAMDisk` | DarwinBoot 复制整个镜像 |
| Packed | `PackedRAMDisk` | DarwinBoot 校验 `DBRDISK1` extent 表并复制片段 |

Packed 形式包含 magic `DBRDISK1`、版本 1、页大小、展开大小和 `(offset, length)` extent 表。未列出的范围是零填充 RAM。

`scripts/seed-data-grow.py` 把 packed 种子增长到平板的存储大小。内核接受最大 1 TiB 的 Data 磁盘，超过 2 GiB 时 typed provider 只保存种子的非零页。

## 确定性

给定固件卷、设备树和 ramdisk 时启动镜像确定。ADT 的随机种子使每次负载构建不同。负载报告记录内核、ADT、trust cache、Data 种子和负载哈希。

## 下一步

- [启动链](/zh/concepts/boot-chain)
- [启动配置](/zh/reference/boot-configuration)
- [启动参数](/zh/xnu/boot-arguments)
