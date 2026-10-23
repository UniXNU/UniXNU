# Redmi K70（vermeer）

vermeer 是搭载 SM8550 的 Redmi K70。下面的仓库是独立的社区移植，UniXNU 组织不维护它们。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [UniXNU-vermeer](https://github.com/mansar1337/UniXNU-vermeer) | [mansar1337](https://github.com/mansar1337) | 源码 XNU 构建基线 |
| [UniXNU-vermeer](https://github.com/yyx2025/UniXNU-vermeer) | [yyx2025](https://github.com/yyx2025) | 从 sheng 移植的设备仓库，状态未记录 |
| [k70-unixnu-build](https://github.com/wuan0039/k70-unixnu-build) | [wuan0039](https://github.com/wuan0039) | 仅内核 CI 工作流 |
| [k70-unixnu-build-20261022](https://github.com/xyyyds0106/k70-unixnu-build-20261022) | [xyyyds0106](https://github.com/xyyyds0106) | 固定 XNU 源码和平台内核构建 |

## 状态

`mansar1337` 仓库记录了源码 XNU 构建基线。编译、最终链接和产物收集在 GitHub Actions 通过。产物经过格式检查，不是手机启动镜像。`yyx2025` 仓库是从 sheng 派生的设备仓库，没有记录运行时状态。

## 维护

维护者拥有各自仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
