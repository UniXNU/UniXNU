# 移植设备

UniXNU 通过 UEFI 在 ARM64 设备上运行 iOS 或 macOS。架构见[欢迎页](/zh/porting/)。按下面八个步骤准备输入、选择共享支持、适配驱动并构建镜像，每一步都写明完成结果。新建与迁移后的仓库使用相同的[完成与发布要求](/zh/porting/device-repository#completion)。

- **新增设备：** 从步骤 1 开始。
- **构建已有设备：** 在[设备列表](/zh/devices/)确认输入和当前支持范围，再按[构建指南](/zh/building)操作。
- **迁移已有仓库：** 按[迁移指南](/zh/porting/migration)更新配置，再继续需要完成的驱动适配和构建步骤。

## 1. 收集设备输入

准备[主机工具](/zh/guide/requirements)。记录 SoC、CPU 拓扑、RAM 保留区、中断控制器、
存储、面板、触控芯片、无线芯片和固件版本。以原厂 DTS、固件源码和硬件观测为依据。
阅读目标仓库根目录的 `AGENTS.md`。

收集信息时建立[移植记录](/zh/porting/records)，逐项记录输入来源、实现、当前结果和下一项测量。
[驱动适配清单](/zh/porting/drivers)链接子系统接口、源码参考和构建接入步骤，包括设备 package 内的服务。

**结果：** 硬件清单和缺失输入列表。寄存器地址与分区布局必须取自目标设备。

## 2. 选择共享支持

选择驱动前阅读[组件目录](/zh/reference/components)和候选实现，核对硬件版本、固件协议和 OS ABI。

| 位置 | 需要选择或实现的内容 |
| --- | --- |
| `UniXNU/profiles/arch/arm64` | ARM64 通用构建配置和补丁 |
| `UniXNU-<soc>-common` | SoC 资源、DTSI、平台操作和补丁 |
| `UniXNU/profiles/os/<profile>` | XNU/IPSW 版本、ABI、预链接和 OS 补丁 |
| `UniXNU-<device>` | 板级连接、组件选择、固件和分区策略 |
| 组件仓库 | 可复用驱动、库、加载器或工具 |
| `uefi-<device>` | 固件平台和外设初始化 |

按[SoC 支持步骤](/zh/porting/soc-support)选择已有实现或建立新的共享仓库，
核对资源、平台操作和组件依赖，再将源码版本固定到设备配置。
新 OS profile 需要先完成 [XNU 与补丁输入](/zh/xnu/source-and-patches)以及
[预链接 ABI 工作](/zh/concepts/prelink)，再验证硬件驱动。
iOS 或 iPadOS 27 等 arm64e 系统仅适用于受支持的设备，见 [arm64e OS 配置](/zh/porting/arm64e)。

**结果：** 已选仓库及精确版本，以及待完成的硬件或 ABI 工作记录。

## 3. 创建设备仓库

模板选择 SM8550 和 iPadOS 17.7.11 profile。把 `DEVICE` 设置为新设备代号，
在 UniXNU 仓库执行：

```sh
DEVICE=myboard
DEVICE_DIR="../UniXNU-$DEVICE"
cp -R examples/device "$DEVICE_DIR"
mv "$DEVICE_DIR/configs/example_defconfig" "$DEVICE_DIR/configs/${DEVICE}_defconfig"
mv "$DEVICE_DIR/dts/board.dts" "$DEVICE_DIR/dts/${DEVICE}.dts"
```

按[设备仓库参考](/zh/porting/device-repository)完成以下文件：

1. `board.toml`：设置设备名、kit、SoC 来源、OS profile、DTS 入口和固件路径，核对完整组件和归档选择。
2. `feeds.toml`：填写 SoC 仓库 URL 和提交。更换 SoC 时同步修改 `board.soc`、`board.soc_source` 和 DTS include。
3. 将 `kernel.defconfig` 设为 `<device>_defconfig`，`device_tree.source` 设为
   `device:dts/<device>.dts`，与重命名后的文件一致。核对所选 SoC 和 OS 的配置片段与补丁序列。
4. 在 DTS 中填写 RAM、启用的 CPU、外设和保留区。
5. 在 `proprietary-files.txt` 中列出固件文件及来源。
6. 为该设备填写 `porting.toml`、根目录 README 和 `AGENTS.md`。记录身份与 `board.toml`
   一致，覆盖所选组件及依赖，归属路径指向实际板级文件。保留复制的
   `.github/workflows/porting-record.yml`、`.gitignore` 和 `local.toml.example`，
   按[完成清单](/zh/porting/device-repository#completion)检查。
7. 填好必要占位符后移除 `board.example = true`。构建命令会拒绝标记为示例的仓库。

数组会替换继承值。覆盖组件、归档、配置片段和补丁序列时，保留完整的必需列表。

**结果：** 源码固定版本和硬件参数明确的设备仓库。

## 4. 解析并检查构建配置

```sh
./unixnu defconfig "${DEVICE}_defconfig" -D "../UniXNU-$DEVICE"
./unixnu fetch
./unixnu status --json
./unixnu tree
```

检查 `status` 中的 profile、组件来源、覆盖项和补丁顺序。
组装后的源码位于 `out/<device>/<os_profile>/<config>/tree/`，
设备 `package/` 映射为其中的 `kits/<board.kit>`。
组件说明同时使用 `scripts/`、`drivers/` 和 `kits/` 时，从该组装目录执行脚本。

**结果：** 依赖解析完成，构建树使用选定的源码版本。
字段定义见[配置参考](/zh/reference/configuration)，参数见 [CLI 参考](/zh/reference/cli)。

## 5. 准备硬件描述和固件

按[设备树转换](/zh/porting/device-tree)编译板级 DTS，检查驱动消费的 ADT 资源。
payload 命令根据硬件描述和 OS profile 生成 `kernel.macho.adt`。
boot image 另需设备固件使用的 DTB。

按 [UEFI 集成](/zh/porting/uefi-firmware#required-integration)加入 UniXNU、DarwinBoot
和 payload 文件系统支持。Mu-Silicium initrd 需要在 DSC 与 FDF 中加入
`UniXNURamDiskDxe`、DiskIoDxe 和 FAT 支持。

按[固件日志导出器步骤](/zh/porting/log-capture#firmware-setup)加入插件，
便于首次启动时从菜单扫描日志。

**结果：** 可构建的固件配置，以及用途明确的两个树输入：生成 XNU ADT 的板级 DTS、组装启动镜像的固件 DTB。

## 6. 按依赖顺序适配驱动

沿[驱动适配](/zh/porting/drivers)依次完成平台与内存、存储、显示与亮度、输入、GPU、
Wi-Fi，再处理 DSP、音频和电源。每篇指南列出源码位置、板级输入、构建集成和预期观测。
仅选择必需输入已满足的实现。

**结果：** 每项能力都有配置和验证记录。在 TOML 中选择组件后，还需要对应归档配方和板级接口。

## 7. 构建并启动

将[前置条件](/zh/guide/requirements)中的路径保存到
[本地构建配置](/zh/reference/configuration#local-build-inputs)。
按[构建指南](/zh/building)依次生成内核、package、固件、payload、所需 userdata 和启动镜像，
确认当前输出后继续。
使用独立 UniXNU 分区时，先按[分区步骤](/zh/porting/dual-system-partition)准备目标分区，再安装镜像。

按[启动验证顺序](/zh/porting/bring-up)检查固件、菜单、加载器、内核和根卷。
设备命令见[启动与恢复](/zh/guide/boot)。修改启动参数后，按
[参数应用流程](/zh/xnu/boot-arguments#apply-arguments)重建 payload 和启动镜像。

**结果：** 构建输出，以及单独记录的设备观测。失败时记录最后完成的阶段，继续
[调试](/zh/guide/debugging)和[故障排查](/zh/reference/troubleshooting)。

在固件阶段先按[日志抓取步骤](/zh/porting/log-capture#firmware-setup)集成二维码导出，
在内核交接前保存固件日志。存储验证完成后，继续该页的持久化抓取、手动循环和自动测试步骤。

## 8. 完成并发布仓库

依次完成[仓库收尾步骤](/zh/porting/device-repository#completion)：核对受版本控制的文件、
解析源码、检查记录、发布审核后的提交。迁移后的仓库也使用这套收尾步骤。

按[发布命令](/zh/porting/device-repository#publish)添加 **`unixnu` GitHub topic**，
启用记录工作流，再按[移植记录](/zh/porting/records)和
[文档贡献](/zh/contributing/documentation)发布设备固定版本与中英文页面。

**结果：** 仓库满足统一的格式 2 要求，并可通过 `unixnu` topic 查找。
记录依据源码、主机和设备证据说明已完成与待完成工作。

## 相关文档

按当前步骤查阅以下说明：

| 内容 | 文档 |
| --- | --- |
| 启动过程与镜像输入 | [启动链](/zh/concepts/boot-chain)、[预链接](/zh/concepts/prelink)、[payload](/zh/concepts/payload)、[userdata 布局](/zh/concepts/userdata)、[完整性与启动策略](/zh/concepts/security) |
| 组件实现与开发 | [驱动分层](/zh/drivers/overview)、[驱动仓库和组件页面](/zh/drivers/repositories) |
| 内核修改 | [源码与补丁](/zh/xnu/source-and-patches)、[补丁参考](/zh/xnu/patch-reference)、[4 KiB 页表](/zh/xnu/four-k-page-tables) |
| 构建与启动配置 | [命令行](/zh/reference/cli)、[设备配置](/zh/reference/configuration)、[启动配置](/zh/reference/boot-configuration)、[输出布局](/zh/reference/output-layout) |
| 主机验证 | [QEMU 流程](/zh/reference/qemu) |
| 项目维护 | [仓库布局](/zh/contributing/repository)、[文档维护](/zh/contributing/documentation)、[术语表](/zh/reference/glossary) |

字段、驱动接口、内核补丁和项目维护见[技术参考](/zh/reference/)。
