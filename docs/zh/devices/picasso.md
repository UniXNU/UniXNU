# Redmi K30 5G（picasso）

picasso 是搭载高通骁龙 765G（SM7250）的 Redmi K30 5G。下面的移植是独立的社区项目。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [UniXNU-picasso](https://github.com/silenzio111/UniXNU-picasso) | [silenzio111](https://github.com/silenzio111) | 阶段 2：物理 UFS 2.1 根卷、Adreno 620 Metal 图形栈、GENI 串口与 USB 崩溃转储 |
| [UniXNU-picasso（早期骨架）](https://github.com/YinCQL/UniXNU-picasso) | [YinCQL](https://github.com/YinCQL) | 早期骨架 |

## 状态

该移植包含完整的板级描述、内核 defconfig（`picasso_platform_defconfig`）、完整的 Apple Device Tree（ADT）生成器、Qualcomm QUPv3 GENI UART 串口与屏幕双重镜像驱动、物理 UFS 2.1 根分区映射（路线 B，8.74 GiB 预制 APFS 系统根镜像）、Adreno 620 Metal 用户态图形栈与 AMFI 静态信任证书，以及免拆机 USB 崩溃日志提取工具（`dump-picasso-panic.py`）。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
