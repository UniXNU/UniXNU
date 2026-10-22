# 小米 13（fuxi）

fuxi 是搭载 SM8550 的小米 13。下面的仓库是独立的社区移植，UniXNU 组织不维护它们。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [UniXNU-fuxi](https://github.com/matejkoo217/UniXNU-fuxi) | [matejkoo217](https://github.com/matejkoo217) | 设备仓库，进行中 |
| [unixnu-fuxi](https://github.com/hanzi123-bilp/unixnu-fuxi)、[uefi-fuxi](https://github.com/hanzi123-bilp/uefi-fuxi) | [hanzi123-bilp](https://github.com/hanzi123-bilp) | 阶段 A 和 B 构建输入，未记录真机运行 |

## UniXNU-fuxi

UniXNU-fuxi 是基于 UniXNU-sheng 的 fuxi 板级数据分支。它沿用 iPad7,1 iPadOS 17.7.11 镜像和 sheng 的内核预链接。fuxi 的 UEFI package、预链接、内核构建、触控驱动和 defconfig 仍在进行中。移植记录见 `PORTING-FUXI.md`。

## hanzi123-bilp 仓库

`hanzi123-bilp` 的仓库是另一套设备和固件移植。设备仓库有阶段 A 的最小内核，可在预链接候选存在前完成链接；阶段 B 使用 19 个 archive 的完整配置。存储审计在拿到实机元数据前只生成头文件。固件仓库映射 SM8550 寄存器窗口。未记录真机运行。

## 维护

表中的维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
