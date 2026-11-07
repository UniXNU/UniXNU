# 小米红米 Note 5 / Note 5 AI (whyred)

whyred 是小米红米 Note 5 / Note 5 AI，搭载 SDM636 SoC（4 个 Cortex-A73 和 4 个 Cortex-A53，Kryo 260，ARMv8.0），内存为 3、4 或 6 GB。下列移植是独立的社区项目，UniXNU 组织不负责维护。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [UniXNU-whyred](https://github.com/N1709/UniXNU-whyred) | [N1709](https://github.com/N1709) | 开发板、SoC 层、DTS、defconfig、打包输入和固件 |

## 状态

| 层 | 状态 |
| --- | --- |
| 开发板描述 | 格式 2；ARM64 配置，使用本地 `sdm660` SoC 层和未修改的 iPad7,1 / iPadOS 17.7.11 / 21H461 镜像 |
| SoC 层 | CPU、PSCI、GICv3 和定时器；已通过 `dtc` 和 `make-adt.py` 验证 |
| 内存 | RAM 起始于 `0x80000000`，大小 2 GiB；开机画面保留区位于 `0x9d400000`，大小 36 MiB |
| userdata | GPT 首个 LBA 为 `0x2b8c00`，末个 LBA 为 `0x1d7d6ff`，LBA 大小 4 KiB |
| 固件 | Mu-Silicium UEFI 已在仓库中完成；尚未在硬件上启动 |
| 内核、payload 和启动镜像 | 尚未构建；首次完整构建待进行 |
| 驱动 | eMMC / SDHCI、显示、Synaptics 触摸、GPU、网络、音频和电源部分完成或尚未开始 |

## 边界

仅使用 `fastboot boot` 启动。切勿刷写 boot、modem、persist 或 recovery，也切勿格式化 `userdata`。根镜像由用户自行放入 `userdata`，本仓库不会写入。

## 维护

维护者拥有该仓库及其发布决定权。UniXNU 文档仅列出该移植及其状态，不接管维护工作。
