# Galaxy Z Fold3（q2q）

q2q 是搭载 SM8350 的三星 Galaxy Z Fold3。下面的移植是独立的社区项目，UniXNU 组织不维护它。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [UniXNU-q2q](https://github.com/agcarbajo/UniXNU-q2q) | [agcarbajo](https://github.com/agcarbajo) | 仅源码内核构建工具 |

## 状态

仓库是只构建源码的 XNU 工具。它使用 UniXNU 的 4 KiB 补丁、`ArmDTPlatform`、`ArmCpu` 和源码 crypto provider 构建 ARM64 XNU 10063.141.1。仓库不包含 OS、IPSW、设备转储、密钥或分区备份，也不访问连接的手机。首个目标是用于 CPU 和控制台 bring-up 的源码内核，不能启动 iPadOS 用户态。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
