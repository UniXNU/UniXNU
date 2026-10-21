# 三星 Galaxy Tab A7 10.4（gta4l）

gta4l 是搭载 SM6115 的三星 Galaxy Tab A7 10.4（2020），型号 SM-T500 或 SM-T505。下面的移植是独立的社区项目，UniXNU 组织不维护它。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [UniXNU-gta4l](https://github.com/NoNameBuilder/UniXNU-gta4l) | [NoNameBuilder](https://github.com/NoNameBuilder) | 板级、ADT 和固件可构建，内核未构建 |

## 状态

| 层 | 状态 |
| --- | --- |
| 板级描述 | 可解析，`defconfig`、`fetch` 和 `tree` 可运行 |
| 固件 | 在 Linux 构建：`gta4lPkg` 加 UniXNU 和 DarwinBoot，3,145,728 字节 |
| ADT | 为 8 个 Kryo 260 核生成 13,180 字节 |
| 内核 | 未构建，UniXNU 内核步骤需要 macOS 和 Xcode |
| 负载和启动镜像 | 未构建，依赖内核 |
| 真机启动 | 未在 UniXNU 下验证；单独的 ios-topaz 16 KiB 构建可到 XNU 控制台 |

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
