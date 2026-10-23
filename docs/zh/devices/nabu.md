# 小米平板 5（nabu）

nabu 是搭载 SM8150 的小米平板 5。下面的移植是独立的社区项目，UniXNU 组织不维护它。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [unixnu-nabu](https://github.com/Lux12138/unixnu-nabu) | [Lux12138](https://github.com/Lux12138) | XNU 已到 vfs_mountroot，下一步根设备 |
| [unixnu-nabu](https://github.com/zzc775/unixnu-nabu) | [zzc775](https://github.com/zzc775) | 面向零售 6 GB 机器的 nabu 替代仓库 |
| [unixnu-nabu-build](https://github.com/3214791900-del/unixnu-nabu-build)、[uefi-nabu-build](https://github.com/3214791900-del/uefi-nabu-build) | [3214791900-del](https://github.com/3214791900-del) | 内核和 UEFI 构建树 |

## 状态

启动链已到 XNU：`fastboot boot` 启动 Mu UEFI，UniXNU 菜单读取 cust 负载，DarwinBoot 校验 51 MB 内核并交接，出现绿色 XNU 画面。内核已到 `vfs_mountroot`。之前看到的 IOsurface 停点是最后一条到达 framebuffer 的日志，不是阻塞点。下一步是根设备。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
