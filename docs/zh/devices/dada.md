# 小米 15（dada）

dada 是搭载 SM8750 的小米 15。下面的移植是独立的社区项目，UniXNU 组织不维护它。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [UniXNU-dada](https://github.com/7Night-kqx/UniXNU-dada) | [7Night-kqx](https://github.com/7Night-kqx) | UEFI 固件工作，UniXNU 和 XNU 未在真机运行 |

## 状态

| 阶段 | 状态 |
| --- | --- |
| UEFI 固件、framebuffer、菜单、UFS、侧键、UART7 | 在 Mu-Silicium 中工作 |
| UniXNU 菜单和配置 | 未运行 |
| 负载卷 | 板级数值已写入，设备输入缺失 |
| DarwinBoot 交接 | 未运行 |
| XNU 内核入口和平台专家 | 首个目标，SM8750 平台专家尚不存在 |
| UFS 根和用户态 | 后续 |

尚未在真机启动。`board.toml` 用 `TODO(device)` 标出仍需测量的设备值。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
