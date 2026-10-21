# 支持的设备

一个设备条目由两个仓库和一组让通用栈在该板子上运行的数值组成。下表记录有公开仓库的移植。采用类似 SoC 的板子需要自己的移植和条目。

| 设备 | SoC | 支持功能 | 设备仓库 | 固件 |
| --- | --- | --- | --- | --- |
| 小米平板 6S Pro（sheng） | SM8550 | 显示、触控、UFS、GPU | [UniXNU-sheng](https://github.com/UniXNU/UniXNU-sheng) | [uefi-sheng](https://github.com/UniXNU/uefi-sheng) |

## 社区移植

这里列出的移植独立维护。仓库归各自维护者所有，UniXNU 组织不维护它们。每个条目有自己的页面。

| 设备 | SoC | 状态 | 维护者 |
| --- | --- | --- | --- |
| [小米 13（fuxi）](/zh/devices/fuxi) | SM8550 | 设备仓库，进行中 | matejkoo217、hanzi123-bilp |
| [小米平板 7 / POCO Pad X1（uke）](/zh/devices/uke) | SM7675 | 已到 XNU 入口，等待根设备 | Allenwdk |
| [Redmi Note 10 Pro（sweet）](/zh/devices/sweet) | SM7150 | 平台和加载器 bring-up，无可启动镜像 | dipa-studio |
| [一加 Ace 5 Pro（hummer）](/zh/devices/hummer) | SM8750 | UEFI 层工作，XNU 在 CI 试水 | 2426120557 |
| [小米 6（sagit）](/zh/devices/sagit) | MSM8998 | 设备仓库，状态未记录 | dmnakzkahziamnk-a11y |
| [小米平板 8 Pro（piano）](/zh/devices/piano) | SM8750 | 内核在 CI 编译并预链接，未在平板上运行 | code002-2 |
| [Redmi Note 14 Pro+ 5G（amethyst）](/zh/devices/amethyst) | SM7635 | 进行中，状态未记录 | andr0d1v |
| [Redmi K70（vermeer）](/zh/devices/vermeer) | SM8550 | 源码构建基线和从 sheng 派生的设备仓库 | mansar1337、yyx2025 |
| [DroidVM 客户机（Gunyah 上的 crosvm）](/zh/devices/droidvm) | crosvm-gunyah | iPadOS 17 锁屏和主屏幕，CPU 渲染 | Droid-VM |
| [QEMU virt](/zh/devices/qemu) | QEMU virt | iPadOS 17 主屏幕和 Settings，CPU 渲染 | xVanTuring |
| [Redmi 9A（dandelion）](/zh/devices/dandelion) | MT6765 | 早期 bring-up，UEFI 移植进行中 | licg89 |
| [Galaxy Z Fold3（q2q）](/zh/devices/q2q) | SM8350 | 仅源码内核构建工具 | agcarbajo |
| [小米 15（dada）](/zh/devices/dada) | SM8750 | UEFI 固件工作，UniXNU 和 XNU 未运行 | 7Night-kqx |
| [小米平板 6（pipa）](/zh/devices/pipa) | SM8250 | 无平板时准备 | xVanTuring |
| [Redmi K40 Pro（haydn）](/zh/devices/haydn) | SM8350 | 固件、负载和启动镜像已构建，未在真机运行 | xiaomi-haydn-dev |
| [小米平板 5（nabu）](/zh/devices/nabu) | SM8150 | XNU 已执行，下一步 PMGR 和用户态 | Lux12138 |
| [Galaxy Tab A7 10.4（gta4l）](/zh/devices/gta4l) | SM6115 | 板级、ADT 和固件可构建，内核未构建 | NoNameBuilder |
| [一加 13T（oneplus13t）](/zh/devices/oneplus13t) | SM8750 | UEFI 菜单和 DarwinBoot 交接，尚未进入 XNU | IssacL04 |

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
