# 支持的设备

一个设备条目由两个仓库和一组让通用栈在该板子上运行的数值组成。下表记录有公开仓库的移植。采用类似 SoC 的板子需要自己的移植和条目。

| 设备 | SoC | 支持功能 | 设备仓库 | 固件 |
| --- | --- | --- | --- | --- |
| 小米平板 6S Pro（sheng） | SM8550 | 显示、触控、UFS、GPU | [UniXNU-sheng](https://github.com/UniXNU/UniXNU-sheng) | [uefi-sheng](https://github.com/UniXNU/uefi-sheng) |

## 社区移植

这里列出的移植独立维护。仓库归维护者所有，UniXNU 组织不维护它。

| 设备 | SoC | 状态 | 仓库 | 维护者 |
| --- | --- | --- | --- | --- |
| [小米 13（fuxi）](/zh/devices/fuxi) | SM8550 | UniXNU 设备仓库，进行中 | [UniXNU-fuxi](https://github.com/matejkoo217/UniXNU-fuxi) | [matejkoo217](https://github.com/matejkoo217) |

## 设备页面记录什么

| 项目 | 示例 |
| --- | --- |
| 板级身份 | 产品名、SoC、代号 |
| IPSW | 产品、版本、build、device class、chip 和 board ID |
| 分区几何 | `first_lba`、`last_lba`、块大小 |
| 内核预链接 | slide、roots、早期安全初始化器、kernelcache 固定 |
| 固件 | Mu-Silicium 配置、DSC、固件卷路径、defines |
| 负载 | 卷标、大小、DRAM 大小、内核参数 |
| ADT | 生成脚本、身份、CPU 寄存器、PSCI 方法 |
| 设备树追加 | 给原有 bootloader 的 reserved-memory 节点 |
| 构建命令 | 实际驱动命令 |
| 启动命令 | 实际 fastboot 命令 |
| 观察状态 | 已在设备上运行过的阶段 |

## 新增设备

1. 按[移植](/zh/porting/)操作。
2. 创建设备仓库和 UEFI 仓库。
3. 分阶段构建和 bring-up。
4. 在 `docs/zh/devices/` 下新增页面，记录数值和命令。
5. 把设备加入上表。

设备页面是板级数值的位置。通用指南使用占位符并链接到这里。

## sheng

[sheng 页面](/zh/devices/sheng)记录小米平板 6S Pro 移植。它是一个设备条目。[Novatek 触控驱动](/zh/drivers/native-novatek-touch)把 sheng 的触控驱动作为内置 XNU 驱动的完整示例。
