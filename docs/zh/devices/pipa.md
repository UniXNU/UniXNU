# 小米平板 6（pipa）

pipa 是搭载 SM8250 的小米平板 6。下面的移植是独立的社区项目，UniXNU 组织不维护它。固件是 [uefi-pipa](https://github.com/xVanTuring/uefi-pipa)，uefi-sheng 的分支。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [UniXNU-pipa](https://github.com/xVanTuring/UniXNU-pipa) | [xVanTuring](https://github.com/xVanTuring) | 已读取板级和 userdata 数值，未在平板运行 |
| [uefi-pipa](https://github.com/xVanTuring/uefi-pipa) | [xVanTuring](https://github.com/xVanTuring) | UEFI 移植，未在真机运行 |

## 状态

设备仓库采用 sheng 布局。静态检查通过，每个硬件数值都标注公开来源。内存分区、userdata 几何和硬件数值已从平板读取。尚未在 pipa 上运行。README 记录了阶段 1 到 3（固件、菜单、负载卷）和阶段 4 到 5（内核入口）。当前没有存储驱动，内核停在根设备。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
