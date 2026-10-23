# Redmi K30 5G（picasso）

picasso 是搭载高通骁龙 765G（SM7250）的 Redmi K30 5G。该机型移植是由社区发起的协作项目，最初由 YinCQL 开启移植。

| 仓库 | 维护者 / 贡献者 | 阶段与侧重点 |
| --- | --- | --- |
| [UniXNU-picasso](https://github.com/YinCQL/UniXNU-picasso) | [YinCQL](https://github.com/YinCQL) | 机型初创发起与 UEFI 固件点亮 |
| [UniXNU-picasso](https://github.com/silenzio111/UniXNU-picasso) | [silenzio111](https://github.com/silenzio111) | 阶段 2：物理 UFS 2.1 根卷、Adreno 620 Metal 图形栈、GENI 串口与 USB 崩溃转储 |

## 状态

picasso 移植融合了社区早期的 UEFI 固件探索与阶段 2 的完整内核与驱动推进。当前技术栈包含：
- 板级描述、内核 defconfig（`picasso_platform_defconfig`）及完整的 Apple Device Tree（ADT）生成器。
- Qualcomm QUPv3 GENI UART 串口与屏幕 LCD Framebuffer 双重镜像驱动。
- 物理 UFS 2.1 根分区映射（路线 B，8.74 GiB 预制 APFS 系统根镜像与 Cryptex1 挂载）。
- Adreno 620 Metal 用户态图形栈与静态 AMFI 信任证书集成。
- 免拆机 USB 崩溃日志与控制台转储提取工具（`dump-picasso-panic.py`）。

## 维护

维护者各自管理其仓库与发布决定。UniXNU 文档记录社区移植及其演进状态，不接管维护。
