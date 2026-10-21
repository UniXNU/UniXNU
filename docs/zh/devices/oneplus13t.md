# 一加 13T（oneplus13t）

oneplus13t 是搭载 SM8750 的一加 13T（PKX110、OP60F5L1）。下面的移植是独立的社区项目，UniXNU 组织不维护它。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [UniXNU-oneplus13t](https://github.com/IssacL04/UniXNU-oneplus13t) | [IssacL04](https://github.com/IssacL04) | UEFI Shell 和菜单，XNU 构建和负载，DarwinBoot 交接，尚未进入 XNU |

## 状态

| 部分 | 状态 |
| --- | --- |
| UEFI Shell 和菜单 | 真机工作，侧键交互仍待确认 |
| GitHub Actions 中的 XNU 构建 | 通过，生成 `kernel.macho` 和 FAT 负载 |
| 负载和启动镜像 | 已生成负载，启动镜像解包后比对通过 |
| DarwinBoot 交接 | 真机出现绿色交接条 |
| XNU 入口 | 尚无证据 |
| kernelcache 预链接、userdata、iOS 用户态 | 未配置 |

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
