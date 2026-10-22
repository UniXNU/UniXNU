# 一加 10 Pro 5G（negroni）

negroni 是搭载 SM8450 的一加 10 Pro 5G（NE2213）。下面的移植是独立的社区项目，UniXNU 组织不维护它。它通过 Mu-Silicium UEFI 和 UniXNU/DarwinBoot，在 ios-sweet 系列的 xnu-8796 内核上运行 iPhone X 的 iOS 16.7.16 用户态。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [UniXNU-negroni](https://github.com/pawlickerr/UniXNU-negroni) | [pawlickerr](https://github.com/pawlickerr) | 已在真机到达 iOS 16.7.16 SpringBoard，CPU 渲染 |
| [Mu-Silicum-negroni](https://github.com/pawlickerr/Mu-Silicum-negroni) | [pawlickerr](https://github.com/pawlickerr) | Mu-Silicium UEFI 固件 |

## 状态

| 阶段 | 状态 |
| --- | --- |
| 启动 | ios-sweet shim 启动 Mu-Silicium；UniXNU 菜单项为 "iOS 16 (negroni-ios XNU)"；64 MiB NEGRONIESP 负载携带内核和 ADT |
| 内核 | ios-sweet 的 xnu-8796；DarwinBoot 在 3 GiB 窗口中进入内核 |
| 根 | UFS 上的 iOS 16.7.16 根，读写挂载 |
| 用户态 | 8 核上的 SpringBoard，触控、硬件按键和持久控制台日志可用 |
| 包管理 | 已安装 Sileo 和 Procursus bootstrap |
| 显示 | CPU 渲染，无 GPU 加速 |
| Wi-Fi | PCIe0 上的 QCA6490 尚未工作 |

根镜像会替换 Android 的 userdata 分区。仓库 README 记录了构建、刷写和启动命令。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
