# 小米 13 Pro（nuwa）

nuwa 是搭载 SM8550、12 GB 内存的小米 13 Pro。下面的移植是独立的社区项目，UniXNU 组织不维护它。目标是使用 iPhone10,3 / d22ap 身份的 iOS 16。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [UniXNU-nuwa](https://github.com/wh1stl3/UniXNU-nuwa) | [wh1stl3](https://github.com/wh1stl3) | 源内核可编译链接，平台静态库、预链接和真机未完成 |
| [uefi-nuwa](https://github.com/wh1stl3/uefi-nuwa) | [wh1stl3](https://github.com/wh1stl3) | 固件源码，真机 bring-up 未验证 |

## 状态

| 层 | 状态 |
| --- | --- |
| 源内核 | xnu 8796.141.3 在 CI 编译并链接；ARM64 `MH_EXECUTE`、Darwin 22.6.0、无未解析符号 |
| 平台静态库 | 未通过；`ArmCpu` 头文件和 Darwin 22 archive 构建仍在进行 |
| donor 接口 | 已清点 65,348 个指针绑定；源内核缺少 APFS `_vfs_getvfs_with_vfsops` 绑定 |
| VFS 桥接 | 静态检查通过，实际编译待完成 |
| 预链接、QEMU 和真机 | 未运行 |
| 板级文件 | `example = true`；`uefi-nuwa` 和 nuwa 平台数值尚未建立 |

仓库的 `docs/STATUS.md` 是当前状态的唯一来源。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
