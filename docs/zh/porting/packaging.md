# 设备打包脚本

**每个设备仓库必须遵守。** 设备仓库带有 `scripts/package.sh`，用一条命令从干净检出产出该设备的启动镜像和 payload。
所有设备仓库中的脚本文本相同。板级只修改 `board.toml`，不修改脚本。

## 规则

1. **一条命令。** `scripts/package.sh` 按下列固定步骤运行，写出产物和清单。第一个失败的步骤会终止运行并指出步骤名。
2. **配置来自 TOML。** 脚本和 `unixnu release` 中不出现设备名、路径、尺寸、内核参数或版本。取值读自 `board.toml`（以及它选择的配置文件和 feeds）。缺少的值先加进 `board.toml`。
3. **脚本是固定的。** UniXNU 仓库的 `templates/package.sh` 是唯一来源，设备仓库原样复制。脚本自己读取的板级值只有 `[package] unixnu`，即 UniXNU 检出的路径。
4. **构建目标是参数。** 单一分支服务所有 OS 配置。`--os 17|26|27|PROFILE` 为本次运行选择配置。随配置不同的取值写在 `board.toml` 的 `[os_overrides."<profile>"]` 下；不按目标建分支，也不为第二个目标另存驱动、补丁或优化。
5. **源码已固定。** `deps` 只获取 `feeds.toml`、`.gitmodules` 和 `unixnu.lock` 指定的版本。

## 步骤

`unixnu release` 按顺序运行下列步骤，每步之前打印一行 `step <名称>`。

| 步骤 | 作用 | 读取 |
| --- | --- | --- |
| `deps` | 获取模块子模块和 git 源，写 `unixnu.lock`，解出板级列出的 IPSW 成员 | `feeds.toml`、`.gitmodules`、`[ipsw]` |
| `preflight` | 选择该 OS 配置的 defconfig 并写出配置 | `[package.defconfig]`、`[kernel]` |
| `patches` | 解析并按应用顺序列出补丁系列 | `[kernel] patch_series` |
| `build` | 按依赖顺序构建内核、package、payload 和固件 | `[components]`、`[kernel]`、`[firmware]`、`[payload]` |
| `pack` | 由固件卷、设备树和 payload 打包启动镜像 | `[bootimg]`、`[device_tree]` |
| `verify` | 写清单并按清单检查产物 | 产物 |

## 接口

```sh
scripts/package.sh [--os 17|26|27|PROFILE] [--no-deps] [--check] [unixnu 选项]
```

| 选项 | 含义 |
| --- | --- |
| `--os` | 本次运行的 OS 配置，默认取 `[board] os_profile` |
| `--no-deps` | 跳过 `deps`，用于源码已获取并固定的本机 |
| `--check` | 运行 `deps`、`preflight` 和 `patches`，打印补丁列表后在任何构建之前停止 |

其他 `unixnu` 选项（`--uefi`、`--kernelcache`、`--dtb`、`--out`、`-j`）原样传递。不在仓库中的本地输入来自 `unixnu.local.toml`。
平台种子（`--unique-chip-id HEX` 或 `UNIXNU_UNIQUE_CHIP_ID`）和固件检出（`--uefi DIR` 或 `UNIXNU_UEFI`）不保存在任何仓库中；固件步骤把 `UNIXNU_UEFI` 传给板级的 preflight 脚本。

## board.toml 键

```toml
[package]
unixnu = "../UniXNU"

[package.defconfig]
"ipados-27.0.1-24A446" = "<device>_ipados27_defconfig"

[os_overrides."ipados-17.7.11-21H461".kernel]
archives = [ ... ]
remove = [ ... ]
```

| 键 | 含义 |
| --- | --- |
| `[package] unixnu` | UniXNU 检出相对设备仓库的路径 |
| `[package.defconfig]` | 各 OS 配置的 defconfig，`release` 使用 |
| `[package] boot_partition_bytes` | 可选。`verify` 拒绝更大的 `boot.img` |
| `[bootimg] dtb` | 启动镜像的设备树，相对构建树。由固件 preflight 脚本生成 |
| `[os_overrides."<profile>"]` | 仅对该配置合并到板级之上的表 |
| 覆盖中的 `remove` | 板级为其他配置设置、而本配置没有的点分键 |

## 产物

路径都在 `out/<device>/<os_profile>/<config>/` 下。清单记录每个文件的尺寸和 SHA-256、每个模块解析后的版本、补丁顺序和内核命令行长度。

| 产物 | 内容 |
| --- | --- |
| `boot/boot.img` | Android 启动镜像：shim、固件卷、设备树、payload ramdisk |
| `payload/payload.img` | 启动镜像携带的 FAT payload 卷 |
| `kernel/kernel.macho` | payload 启动的预链接内核 |
| `package.manifest.json` | 清单 |

## 验证

产物缺失或与清单不符、内核命令行达到 1000 字节、`boot.img` 超过 `boot_partition_bytes`，`verify` 都会失败。启动这些产物是另一步，另行记录。

## 采用

1. 把 `templates/package.sh` 复制为设备仓库的 `scripts/package.sh`。
2. 在 `board.toml` 加 `[package]` 和 `[package.defconfig]`，为其他配置加 `[os_overrides]`。
3. 对每个配置运行 `scripts/package.sh --check --os <profile>`，修正报告的问题。
4. 把运行记录到 `porting.toml` 的 `packaging` 区域。

[构建与启动](/zh/building)、[设备仓库](/zh/porting/device-repository)
