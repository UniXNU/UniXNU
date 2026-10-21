# 小米平板 5（nabu）

nabu 是搭载 SM8150 的小米平板 5。下面的移植是独立的社区项目，UniXNU 组织不维护它。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [unixnu-nabu](https://github.com/Lux12138/unixnu-nabu) | [Lux12138](https://github.com/Lux12138) | XNU 已执行，下一步 PMGR 和用户态 |

## 状态

启动链已到 XNU：`fastboot boot` 启动 Mu UEFI，UniXNU 菜单读取 cust 负载，DarwinBoot 校验 51 MB 内核并交接，出现绿色 XNU 画面。下一步是 PMGR 电源管理框架，之后才能启动 IPSW 用户态。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
