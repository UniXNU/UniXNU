# Redmi 9A（dandelion）

dandelion 是搭载 MediaTek MT6765（Helio G25）的 Redmi 9A。下面的移植是独立的社区项目，UniXNU 组织不维护它。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [UniXNU-dandelion](https://github.com/licg89/UniXNU-dandelion) | [licg89](https://github.com/licg89) | 早期 bring-up，UEFI 移植进行中 |

## 状态

| 组件 | 状态 |
| --- | --- |
| 硬件分析 | 完成 |
| 驱动 | 8 个核心驱动已实现 |
| 启动代码 | chainloader 和测试内核 |
| 直接启动 | 失败，内核崩溃，无 UART |
| UEFI 移植 | 进行中 |
| 真机测试 | 因无 UART 受阻 |

整体进度约 55%。当前策略是为 MT6765 移植 Mu-Silicium UEFI，然后集成 UniXNU。README 记录移植预计需要 6 到 12 个月。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
