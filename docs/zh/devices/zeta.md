# Microsoft Surface Duo 2（zeta）

zeta 是搭载 SM8350 的 Microsoft Surface Duo 2。下面的移植是独立的社区项目，UniXNU 组织不维护它。目标身份是 iOS 26.5.2 上的 iPhone18,2。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [UniXNU-zeta](https://github.com/none24smu/UniXNU-zeta) | [none24smu](https://github.com/none24smu) | UEFI、菜单和负载卷工作，内核已构建，未启动 |

## 状态

| 步骤 | 状态 |
| --- | --- |
| UEFI 固件 | 通过 `fastboot boot` 在手机启动，面板显示 UniXNU 菜单，音量键和电源键工作，启动镜像的 ramdisk 作为负载卷挂载 |
| 设备仓库 | 本仓库 |
| IPSW 身份 | iPhone18,2 26.5.2 23F84 |
| ADT | zeta 硬件数值加 IPSW 设备树中的 iPhone18,2 身份 |
| 负载和启动镜像 | 内核已构建：来自 UniXNU `ios26` 分支的 xnu-12377.121.6（iOS 26.5）；尚未与 23F84 的 arm64e kext 预链接，也未启动 |
| 根和用户态 | 未开始 |

固件部分见 [uefi-zeta](https://github.com/none24smu/uefi-zeta)，带 `Platforms/Microsoft/zetaPkg` 的 Mu-Silicium 树。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
