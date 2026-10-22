# 一加 5（cheeseburger）

cheeseburger 是搭载 MSM8998 的一加 5。下面的移植是独立的社区项目，UniXNU 组织不维护它。目标用户态是 iPhone iOS。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [UniXNU-cheeseburger](https://github.com/DinnerABC/UniXNU-cheeseburger) | [DinnerABC](https://github.com/DinnerABC) | UEFI 和菜单工作，已观察到 XNU 入口色条，MMU 和根未验证 |

## 状态

| 层 | 状态 |
| --- | --- |
| 原生 UEFI 和集成固件 | 可构建，原版镜像在真机进入 EFI Shell |
| UniXNU 菜单 | 图形菜单在真机运行 |
| DarwinBoot | 已记录文件哈希、Mach-O 装载、ADT、`boot_args` 和 EBS 交接 |
| XNU | 独立的 MSM8998 ARM64 构建，P5 镜像显示 XNU `__start` 入口色条 |
| MMU、C 初始化、根卷和 iOS | 未验证 |
| 板级文件 | `example = true`，通用 build 和 boot image 步骤会拒绝不完整的板级配置 |

P1 GitHub Actions 在 `actions/setup-python` 阶段失败，审计未执行，目前没有远程构建通过记录。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
