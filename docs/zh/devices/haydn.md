# Redmi K40 Pro（haydn）

haydn 是搭载 SM8350 的 Redmi K40 Pro。下面的移植是独立的社区项目，UniXNU 组织不维护它。本页记录 UniXNU 路线。维护者的工作区里还有一条使用 iOS 16 用户态的 SWEET 路线。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [UniXNU-haydn](https://github.com/xiaomi-haydn-dev/UniXNU-haydn) | [xiaomi-haydn-dev](https://github.com/xiaomi-haydn-dev) | 设备仓库和 UEFI 方案，固件、负载和启动镜像已构建，未在真机运行 |
| [UniXNU-haydn4](https://github.com/xiaomi-haydn-dev/UniXNU-haydn4) | [xiaomi-haydn-dev](https://github.com/xiaomi-haydn-dev) | 从 guacamole 导入，板级名 haydn，kit 仍为 guacamole |

## 状态

| 层 | 状态 |
| --- | --- |
| 板级描述和 ADT | 就绪 |
| UEFI 方案 | 从 venus 派生的 `haydnPkg`；预检 0 个静态错误；硬件未验证 |
| 固件、负载和启动镜像 | 已构建并通过字节校验 |
| 内核和 userdata | 需要 macOS |
| 真机启动 | 未运行 |

`PORTING.md` 记录了 SM8350 硬件数值和 iPad7,1 iPadOS 17.7.11 目标。单独的 SWEET 路线已在真机上用 iPhone X iOS 16.7.16 用户态到达 `launchd`。该路线使用 16 KiB 页和 HFS+，不属于 UniXNU 路线。

## haydn4 仓库

`UniXNU-haydn4` 从 guacamole 树导入，并把板级名改为 haydn。README 和 kit 仍使用 guacamole 数值。在板级数据测量完成前，不把它视为已验证的 haydn 移植。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
