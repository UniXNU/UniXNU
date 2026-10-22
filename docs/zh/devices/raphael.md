# Redmi K20 Pro / Mi 9T Pro（raphael）

raphael 是搭载 SM8150 的 Redmi K20 Pro 和 Mi 9T Pro。下面的移植是独立的社区项目，UniXNU 组织不维护它。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [UniXNU-raphael](https://github.com/penYo22/UniXNU-raphael) | [penYo22](https://github.com/penYo22) | 新仓库，内核构建未通过 |

## 状态

硬件数值已在设备上测量：DRAM 基址 `0x80000000`、userdata LBA、GIC、UFS、USB、面板和 CPU 布局。仓库参考 nabu 移植记录 SM8150 的 bring-up 问题。

内核构建尚未通过。CI 工作流在 macOS 构建内核，在 Linux 构建负载。目前没有真机启动证据。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
