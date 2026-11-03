# 选择与添加 SoC 支持

SoC 仓库提供同一芯片各板型共享的硬件描述和平台代码。
完成[设备仓库](/zh/porting/device-repository)前，先按以下步骤选择或建立共享支持。

## 1. 确认硬件与现有支持

从厂商 DTS、固件和源码记录 SoC 型号与修订版本、CPU 拓扑、中断控制器、计时器、
IOMMU 和外设控制器。阅读[组件目录](/zh/reference/components)，再检查候选
`UniXNU-<soc>-common` 仓库的 `README.md`、`AGENTS.md`、`soc.toml`、DTSI、
配置片段、补丁和平台代码。

逐项核对寄存器范围、中断号、控制器版本、固件接口和 OS ABI。
通过关联设备记录确认实机结果。[SM8550](#sm8550) 是一个现有实现。

**结果：** 确定匹配的 SoC 仓库和已审查提交，或列出新仓库需要完成的共享硬件与平台工作。

## 2. 确定配置归属

| 归属 | 内容 |
| --- | --- |
| ARM64 配置 | 通用架构配置和 XNU 补丁 |
| SoC 仓库 | CPU 拓扑、控制器资源、共享平台操作和 SoC 补丁 |
| 设备仓库 | 启用的 CPU/外设、RAM 与预留区域、连接方式、固件选择、电源策略、显示和分区 |
| OS 配置 | XNU/IPSW 版本、Apple 身份、预链接根组件、ABI 要求和版本补丁 |
| 组件仓库 | 按接口、硬件范围和依赖选择的驱动与库 |

可复用的控制器代码放入组件。SoC 配置选择兼容实现，板型提供所需输入并记录自己的验证结果。
按[驱动适配清单](/zh/porting/drivers)检查每项所选能力。

**结果：** 每项配置和源码都有明确归属。使用已有支持时继续步骤 4；新 SoC 先完成步骤 3。

## 3. 为新 SoC 建立共享支持

使用芯片的标准标识命名 `UniXNU-<soc>-common`。
在预定仓库的父目录中，将 `SOC` 设置为该标识并建立目录：

```sh
SOC=mychip
SOC_REPO="UniXNU-$SOC-common"
mkdir -p "$SOC_REPO/configs" "$SOC_REPO/dts" "$SOC_REPO/patches/xnu" "$SOC_REPO/kits"
```

完成以下结构：

```text
UniXNU-<soc>-common/
  AGENTS.md
  README.md
  soc.toml
  configs/<soc>.config
  dts/<soc>.dtsi
  patches/xnu/series
  kits/
```

1. 编写 `soc.toml`，设置 `schema_version = 2`、`[soc] name`、描述及硬件数据采用的
   源码仓库和版本。在 `[components] include` 中用规范组件 ID 列出已核对的实现。
2. 在 `dts/<soc>.dtsi` 中描述已确认的共享资源。
   按[设备树步骤](/zh/porting/device-tree#procedure)处理绑定、地址转换、中断和引用。
   板级 DTS 包含此文件并提供设备内存和外设配置。
3. 在 `configs/<soc>.config` 中加入共享内核设置，在 `patches/xnu/series` 中按顺序列出
   SoC 补丁。无需补丁时使用空的 series 文件。
4. 将共享平台操作放入 `kits/`，通过[构建配置](/zh/reference/configuration)接入源码或静态库。
   按该 SoC 的资料核对每个硬件地址和固件操作。
5. 编写简洁 README，说明范围、输入、构建命令和已验证设备。
   根目录 `AGENTS.md` 列出职责和必读文档，详细操作链接到本站。
6. 发布仓库，为设备 feed 选择已审查的提交。

**结果：** SoC 配置已有固定版本，硬件值均有明确来源。

## 4. 从设备选择 SoC 配置

在设备的 `feeds.toml` 中加入固定版本的源码。
将示例名称、URL 和提交替换为选定仓库：

```toml
[[source]]
name = "mychip"
kind = "soc"
git = "https://github.com/<owner>/UniXNU-mychip-common"
commit = "<reviewed 40-character commit>"
```

在 `board.toml` 已有的表中设置：

```toml
[board]
soc = "mychip"
soc_source = "mychip"
os_profile = "<selected OS profile>"

[device_tree]
source = "device:dts/board.dts"
include_dirs = ["soc:dts"]
```

将板级 DTS 的 include 改为选定的 `<soc>.dtsi`。
更新 `[kernel] config_fragments`，加入 `soc:configs/<soc>.config`；
更新 `patch_series`，将 `soc:patches/xnu/series` 放入预定顺序。
保留完整的 ARM64、SoC、OS 和设备列表：表按键合并，普通数组替换之前的数组。
组件选择和静态库列表遵循同一规则。

**结果：** 板型选择了固定版本的 SoC 源码，以及匹配的 DTSI 和配置片段。
选择或建立 OS 配置时，按 [OS 配置与补丁要求](/zh/xnu/source-and-patches)操作。

## 5. 解析并验证组合

从 UniXNU 主仓库运行：

```sh
./unixnu defconfig <device>_defconfig -D ../UniXNU-<device>
./unixnu fetch
./unixnu status --json
./unixnu tree
```

在 `status` 中检查 SoC 版本、所选配置、组件、覆盖项和补丁顺序。
检查组装树，再按[设备树编译](/zh/porting/device-tree#procedure)、
[驱动适配](/zh/porting/drivers)和[构建指南](/zh/building)操作。
将每块板型的[启动检查点](/zh/porting/bring-up)、[日志证据](/zh/porting/log-capture)
与构建结果分别记录。

**结果：** 源码已解析、硬件描述已编译，并有板型自己的验证记录。继续[移植设备](/zh/porting/steps)。

## SM8550 示例 {#sm8550}

[`UniXNU-sm8550-common`](https://github.com/UniXNU/UniXNU-sm8550-common)
提供 `soc.toml`、`configs/sm8550.config`、`dts/sm8550.dtsi`、平台操作和 XNU 补丁系列。
选择前阅读这些文件和根目录 `AGENTS.md`，在设备 feed 中固定仓库版本，并包含其 DTSI。

Adreno740 和 AdrenoMetal 覆盖 A740/SM8550 接口。每块板型提供自己的固件、电源、
保留内存和显示输入。[参考设备记录](/zh/devices/sheng)包含该设备的 GPU 实机结果；
其设备配置还选择了相应 UFS、触控和 HID 实现。复用时检查这些组件的板级依赖。
已有移植按[迁移指南](/zh/porting/migration)操作。
