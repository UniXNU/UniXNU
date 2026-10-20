# 命令行

```
./unixnu <command> [options]
```

选项写在命令之后。驱动从 `-D`、`UNIXNU_DEVICE` 或 `out/state.json` 读取设备仓库。

## 命令

### defconfig

```
unixnu defconfig [NAME]
```

列出设备仓库的 `configs/*_defconfig`。指定名称时复制到 `out/<board>/.config` 并解析。

### fetch

```
unixnu fetch [NAME...] [--update]
```

更新本仓库和设备仓库的模块子模块，然后拉取 git 源码。指定名称时只拉取这些源码。`--update` 忽略 `unixnu.lock` 并移到最新 ref。commit 写入设备仓库的 `unixnu.lock`。

### tree

```
unixnu tree
```

解析模块、拉取步骤需要的参考源码，并组装 `out/<board>/tree`。

### ipsw

```
unixnu ipsw info
unixnu ipsw fetch [COMPONENT...]
```

`info` 打印产品、build、device class 和 manifest 中每个组件的大小与路径。`fetch` 提取指定组件，未指定时使用 `[ipsw] fetch` 列表。

### build

```
unixnu build [kernel] [package] [firmware] [payload] [prelink] [userdata]
```

按 kernel、prelink、package、payload、firmware 顺序执行指定步骤。未指定时执行 kernel、package、firmware 和 payload。`userdata` 单独执行，`all` 覆盖其他四个步骤。

`build prelink` 只重做预链接。

`build kernel` 在链接前运行生成编译记录的构建和 `[kernel] archives` 中的静态库脚本。

`build userdata --dry-run` 检查 IPSW 和分区大小。

### bootimg

```
unixnu bootimg [--fd FILE] [--dtb FILE] [--ramdisk FILE|none] [-o FILE]
```

打包启动镜像。固件卷默认取 `--uefi` 下的输出，ramdisk 默认取负载输出。

### status

```
unixnu status
```

打印设备、输出根、配置路径和每个模块来源。标记本地模块并报告未固定的模块。

### clean

```
unixnu clean
```

删除板级输出下的 `tree`、`logs`、`kernel`、`package`、`boot` 和 `edk2-conf`，保留已拉取源码。

## 选项

| 选项 | 含义 |
| --- | --- |
| `-D DIR`、`--device DIR` | 设备仓库 |
| `--out DIR` | 输出根 |
| `-j N`、`--jobs N` | 并行任务 |
| `--local DIR` | 与本仓库布局相同的本地树 |
| `--local-drivers DIR` | 本地 drivers 目录 |
| `--local-kits DIR` | 本地 kits 目录 |
| `--local-patches DIR` | 本地 patches 目录 |
| `--local-scripts DIR` | 本地 scripts 目录 |
| `--local-package DIR` | 本地 package 目录 |
| `--local-module [KIND:]NAME=PATH` | 单个本地模块，可重复 |
| `--uefi DIR` | Mu-Silicium 仓库 |
| `--edk2 DIR` | Mu_Basecore 仓库 |
| `--kernelcache FILE` | 原始解压 kernelcache |
| `--skip-preflight` | 跳过板级预检 |
| `--kernel FILE` | 负载使用的预链接内核 |
| `--kernel-arg NAME[=VALUE]` | 额外内核参数；与 `[payload] kernel_args` 同名时替换，可重复 |
| `--trust-cache FILE` | trust cache 包 |
| `--owner-trust-cache FILE` | owner 签名的包，包含原始缓存和额外模块。替换 `--trust-cache`，并跳过板级允许列表 |
| `--skip-setup` | 在 Data 种子副本中标记 Setup 完成 |
| `--data-ramdisk FILE` | Data ramdisk 种子 |
| `--unique-chip-id HEX` | ADT 平台种子 |
| `--ipsw PATH_OR_URL` | 目标 IPSW |
| `--dry-run` | userdata 试运行 |
| `--target DEBUG\|RELEASE` | EDK II 目标 |
| `--fd FILE` | bootimg 的固件卷 |
| `--dtb FILE` | bootimg 的编译设备树 |
| `--ramdisk FILE\|none` | bootimg 的 ramdisk |
| `-o FILE`、`--output FILE` | 启动镜像输出 |

## 环境变量

| 变量 | 等价选项 |
| --- | --- |
| `UNIXNU_DEVICE` | `-D` |
| `UNIXNU_OUT` | `--out` |
| `UNIXNU_UEFI` | `--uefi` |
| `UNIXNU_EDK2` | `--edk2` |
| `UNIXNU_KERNELCACHE` | `--kernelcache` |
| `UNIXNU_DTB` | `--dtb` |
| `UNIXNU_IPSW` | `--ipsw` |
| `UNIXNU_UNIQUE_CHIP_ID` | `--unique-chip-id` |
| `JOBS` | `-j` |

## 退出行为

| 条件 | 结果 |
| --- | --- |
| 缺少设备仓库 | 提示 `-D` |
| 内核构建缺少配置 | 提示先运行 `defconfig` |
| 固件缺少 Mu-Silicium 仓库 | 拉取前报错 |
| IPSW 身份不匹配 | 报错并给出期望和实际镜像 |
| sha256 不匹配 | 报错并给出成员名 |
| 固件卷大小不匹配 | 报错并给出大小 |
| 负载超过 `size_mib` | 报错并给出需要提高的大小 |
| 内核参数非法 | 报错并给出参数 |
| 内核命令行超过 1000 字节 | 报错并给出长度和上限 |
| 缺少平台种子 | 提示 `--unique-chip-id` |
| 示例设备仓库 | `build` 或 `bootimg` 前报错 |

## 下一步

- [设备配置](/zh/reference/configuration)
- [输出布局](/zh/reference/output-layout)
- [故障排查](/zh/reference/troubleshooting)
