# 一加 Ace 5（giulia）

giulia 是搭载 SM8650 的一加 Ace 5（PKG110）。下面的移植是独立的社区项目，UniXNU 组织不维护它。内核为 Darwin 22.6 / iOS 16 构建。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [UniXNU-giulia](https://github.com/jasper2863/UniXNU-giulia) | [jasper2863](https://github.com/jasper2863) | 已到 GUI 进度条，安装服务受阻 |

## 状态

| 区域 | 状态 |
| --- | --- |
| UEFI 交接和 XNU 内存初始化 | 工作 |
| 平台驱动、CPU0 和 SGI1 | 工作 |
| 原生 UFS 读取 | 工作 |
| USB CDC 调试串口 | 工作 |
| HFSX 根卷 | 读写挂载工作 |
| `launchd` 和系统服务 | 启动 |
| GUI 内核 | 苹果标志和进度条，记录约 77,000 次画面提交，未观察到 SpringBoard 或 backboardd 崩溃 |
| 可操作界面 | 未到达，安装服务受阻 |
| 触控 | 控制器身份和报文已验证，物理触控不可用 |
| 基带、音频、GPU 和 DRM | 未实现 |

仓库保留了完整启动日志、主机检查和镜像哈希。当前阻塞点是系统应用安装和迁移路径。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
