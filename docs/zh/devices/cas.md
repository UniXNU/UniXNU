# 小米 10 Ultra（cas）

cas 是搭载 SM8250、约 12 GB 内存的小米 10 Ultra（M2007J1SC）。下面的移植是独立的社区项目，UniXNU 组织不维护它。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [UniXNU-cas](https://github.com/ht94911/UniXNU-cas) | [ht94911](https://github.com/ht94911) | UEFI 和 UniXNU 菜单已在真机运行；DarwinBoot 和 XNU 未测试 |
| [uefi-cas](https://github.com/ht94911/uefi-cas) | [ht94911](https://github.com/ht94911) | Mu-Silicium 固件移植 |
| [UniXNU-cas](https://github.com/pxl777806/UniXNU-cas) | [pxl777806](https://github.com/pxl777806) | cas 替代仓库，状态未记录 |

## 状态

| 区域 | 状态 |
| --- | --- |
| UEFI 和 UniXNU 菜单 | 临时 `fastboot boot`；1080x2340 显示；实体音量和电源键可用 |
| 负载 | 只读 16 MiB RAM FAT；CasSmoke EFI 可加载、执行并返回菜单；缺文件时报 `Not Found` |
| 重启 | 菜单可回到 Android，包括固件信息菜单 |
| 可复现性 | 同一镜像完成三轮完整运行；独立重建的 34 项产物逐字节一致；126 项源码测试通过 |
| 分区完整性 | 18 个受保护分区哈希和六个 UFS LUN 的主、备 GPT 在三轮运行中保持不变 |
| DarwinBoot、XNU、iOS | 未测试 |
| 触控和 GPU | 未测试 |

测试设备运行 Android 15 / OS3.0.4.0.VMKCNXM。构建使用 UniXNU `67e8ef0`。完整启动镜像需要匹配的原厂 DTB，未公开分发。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
