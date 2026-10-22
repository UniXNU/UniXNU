# 小米 13 Pro（nuwa）

nuwa 是搭载 SM8550、12 GB 内存的小米 13 Pro。下面的移植是独立的社区项目，UniXNU 组织不维护它。目标是使用 iPhone10,3 / d22ap 身份的 iOS 16。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [UniXNU-nuwa](https://github.com/wh1stl3/UniXNU-nuwa) | [wh1stl3](https://github.com/wh1stl3) | 源内核可编译链接，平台静态库、预链接和真机未完成 |
| [UniXNU-nuwa](https://github.com/pubglite55/UniXNU-nuwa) | [pubglite55](https://github.com/pubglite55) | 固件、负载和启动镜像已打包，真机到 UniXNU 启动管理器；负载卷挂载在查 |

## 状态

以下是 wh1stl3 移植的状态。

| 层 | 状态 |
| --- | --- |
| 源内核 | xnu 8796.141.3 在 CI 编译并链接；ARM64 `MH_EXECUTE`、Darwin 22.6.0、无未解析符号 |
| 平台静态库 | 未通过；`ArmCpu` 头文件和 Darwin 22 archive 构建仍在进行 |
| donor 接口 | 已清点 65,348 个指针绑定；源内核缺少 APFS `_vfs_getvfs_with_vfsops` 绑定 |
| VFS 桥接 | 静态检查通过，实际编译待完成 |
| 预链接、QEMU 和真机 | 未运行 |
| 板级文件 | `example = true`；`uefi-nuwa` 和 nuwa 平台数值尚未建立 |

仓库的 `docs/STATUS.md` 是当前状态的唯一来源。

## pubglite55 移植的状态

这个移植以 sheng 的受限配置为基座，走「固件 + 负载」路线。

| 层 | 状态 |
| --- | --- |
| 源内核 | xnu 8796.141.3 在 CI 编译、链接并预链接；`kernel.macho` 54.3 MB |
| 平台静态库 | 13 个 archive 全部构建，以 sheng kit 为基座 |
| 固件 | Mu-Silicium `nuwaPkg` 集成 DarwinBoot、UniXNUDxe、UniXNU 应用和启动内存驱动；真机显示 UniXNU 启动管理器 |
| 负载与启动镜像 | payload FAT 卷 188 MiB；Android boot image 打包完成并刷入真机 |
| 真机 | BootShim → UEFI → BDS → 启动管理器已跑通；负载卷尚未被 Fat 挂载，内核入口未到 |
| 板级文件 | 部分数值仍是 sheng 占位（如 userdata LBA）；`uefi-nuwa` 已建立 |

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。

