# 一加 Ace 5 Pro（hummer）

hummer 是搭载 SM8750 的一加 Ace 5 Pro（PKR110）。下面的移植是独立的社区项目，UniXNU 组织不维护它。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [UniXNU-hummer](https://github.com/2426120557/UniXNU-hummer) | [2426120557](https://github.com/2426120557) | UEFI 固件工作，XNU 在 CI 试水 |

## 状态

| 区域 | 状态 |
| --- | --- |
| UEFI 固件和菜单 | 真机工作，GOP 显示和按键输入可用 |
| XNU 内核 | CI 试水，ADT 生成器就绪 |
| GPU（Adreno 830） | 未开始 |
| 持久 Data | 未开始 |

板级文件把 `[kernel]`、`[ipsw]` 和 `[payload]` 标为脚手架。README 把 GPU 列为主要障碍。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
