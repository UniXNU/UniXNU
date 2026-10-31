# 设备打包脚本

**每个设备仓库必须遵守。** 设备仓库只带一个打包脚本，从干净检出、不带参数、不需要修改即可产出启动镜像和 payload。
其他设备仓库照搬本页的结构，只填写配置值，不修改脚本本身。

## 规则

1. **一条命令，两项产物。** 设备仓库的 `scripts/package.sh` 同时构建两项产物。同一份源码第二次运行产出的字节完全相同。
2. **配置来自 TOML。** 脚本读取 `board.toml` 及其引用的 `feeds.toml`、配置文件和本地文件。脚本里不出现设备名、路径、尺寸、内核参数或版本的字面值。脚本需要而 TOML 没有的值，先加进 `board.toml`。
3. **脚本是共享的，不按设备各写一份。** 各设备仓库使用同一份脚本文本，差异只在 TOML 取值。流程改动只改一次，由所有设备仓库采用。
4. **构建目标是参数。** 单一分支服务所有 OS 配置。`--os` 为本次运行选择 iOS 或 iPadOS 17、26、27。不存在按目标拆分的分支，也不存在为第二个目标另存一份的驱动、补丁或优化。
5. **每一步都有名字和检查。** 失败的一步以其名称和命令输出终止本次运行；被跳过的一步要说明原因。

## 结构

脚本按下列顺序执行。每一步是一个同名函数，运行前打印一行标题。

| 步骤 | 作用 | 读取 |
| --- | --- | --- |
| `deps` | 克隆或更新 UniXNU、设备仓库、其模块和 UEFI 仓库，并校验每个固定版本 | `feeds.toml`、`.gitmodules`、`unixnu.lock` |
| `preflight` | 运行板级检查并解析配置 | `board.toml`、`--os` |
| `patches` | 按应用顺序列出解析后的补丁系列，然后应用 | `patch_series`、各配置的系列 |
| `build` | 按依赖顺序构建各阶段，遇到第一个失败即停止 | `components`、`kernel`、`firmware` |
| `pack` | 写出两项产物及其清单 | `bootimg`、`payload` |
| `verify` | 按清单校验产物并报告尺寸 | 清单 |

## 接口

```sh
scripts/package.sh [--os 17|26|27|PROFILE] [--device DIR] [--out DIR] [--jobs N] [--no-deps] [--check]
```

| 选项 | 含义 |
| --- | --- |
| `--os` | 本次运行的 OS 配置，默认取 `board.os_profile` |
| `--device` | 设备仓库，默认为脚本所在目录 |
| `--out` | 输出根目录，默认为 UniXNU 检出中的 `out/` |
| `--jobs` | 编译阶段的并行任务数 |
| `--no-deps` | 跳过 `deps`，用于源码已获取并固定版本的本机 |
| `--check` | 只运行 `deps`、`preflight`、`patches` 和 `verify`，报告将会发生的变化 |

每个选项都对应一个 `unixnu` 参数。`unixnu` 已经完成的步骤，脚本不再添加自己的逻辑。

## 必需产物

本次运行写出下列文件，清单为每个文件记录尺寸和 SHA-256。

| 产物 | 内容 |
| --- | --- |
| `out/<device>/<os_profile>/<config>/boot.img` | Android 启动镜像：shim、固件卷、设备树、payload ramdisk |
| `out/<device>/<os_profile>/<config>/payload.img` | 启动镜像携带的 payload 卷 |
| `out/<device>/<os_profile>/<config>/kernel.macho` | payload 启动的预链接内核 |
| `out/<device>/<os_profile>/<config>/package.manifest.json` | 构建标识、OS 配置、解析后的版本、补丁系列、产物尺寸与哈希 |

启动镜像必须放得进引导加载程序的分区，内核命令行必须保持在 1000 字节以内。两种情况脚本在写镜像之前就拒绝。

## 验证

一次打包运行以 `verify` 通过为完成：两项产物存在，哈希与清单一致，内核命令行在限制之内，启动镜像不大于它所来自的分区。
启动该产物是另一步，另行记录。

## 采用

给尚无该脚本的设备仓库：

1. 从参考设备仓库复制 `scripts/package.sh`。
2. 填写 `board.toml`，直到 `--check` 不再报告缺失值。
3. 把产物记录到设备 `porting.toml` 的 packaging 区域。
4. 把运行方式加入构建文档。

[构建与启动](/zh/building)、[设备仓库](/zh/porting/device-repository)
