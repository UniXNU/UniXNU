# 一加 13T（oneplus13t）

oneplus13t 是搭载 SM8750 的一加 13T（PKX110、OP60F5L1）。下面的移植是独立的社区项目，UniXNU 组织不维护它。仓库从 `UniXNU-oneplus13t` 更名为 `UniXNU-Pagani_SM8750`，提交历史保留。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [UniXNU-Pagani_SM8750](https://github.com/IssacL04/UniXNU-Pagani_SM8750) | [IssacL04](https://github.com/IssacL04) | 已到 XNU S1 到 S6，根设备查找 panic，无根和用户态 |

## 状态

| 部分 | 状态 |
| --- | --- |
| UEFI Shell 和菜单 | 真机工作，侧键交互仍待确认 |
| GitHub Actions 中的 XNU 构建 | 通过，第 9 个镜像到达 S1 到 S6 |
| 负载和启动镜像 | 内嵌负载交接，启动镜像解包后比对通过 |
| DarwinBoot 交接 | 真机出现绿色交接条 |
| XNU 入口 | 已到 S1 到 S6，控制台、`zalloc` 和 BSD 根设备查找已执行 |
| 根和用户态 | 不可用，根设备查找在 60 秒后 panic |
| kernelcache 预链接、userdata、iOS 用户态 | 未配置 |

panic 页记录 `poll=0x3c`、`timer=0x1a3` 和超时路径。单核定时器中断和观察线程已运行。长期稳定性和多核调度尚未验证。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
