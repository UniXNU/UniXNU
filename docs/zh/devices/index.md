# 支持的设备

一个设备条目由两个仓库和一组让通用栈在该板子上运行的数值组成。下表记录有公开仓库的移植。采用类似 SoC 的板子需要自己的移植和条目。

| 设备 | SoC | 支持功能 | 设备仓库 | 固件 |
| --- | --- | --- | --- | --- |
| 小米平板 6S Pro（sheng） | SM8550 | 显示、触控、UFS、GPU | [UniXNU-sheng](https://github.com/UniXNU/UniXNU-sheng) | [uefi-sheng](https://github.com/UniXNU/uefi-sheng) |

## 社区移植

这里列出的移植独立维护。仓库归各自维护者所有，UniXNU 组织不维护它们。每个条目有自己的页面。表格按完成度排序，已到用户态或完整构建链的移植在前。

| 设备 | SoC | 状态 | 维护者 |
| --- | --- | --- | --- |
| [DroidVM 客户机（Gunyah 上的 crosvm）](/zh/devices/droidvm) | crosvm-gunyah | iPadOS 17 主屏幕，CPU 呈现，Metal widget 和图标，virtio-net 工作 | Droid-VM |
| [QEMU virt](/zh/devices/qemu) | QEMU virt | iPadOS 17 主屏幕和 Settings；使用 `--metal` 时在 Mac GPU 上运行 Metal | xVanTuring |
| [联想小新 Pad 2022（tb128fu）](/zh/devices/tb128fu) | SM6225 | 已到 iPadOS 17 主屏幕，触控可用；Metal 帧由 GPU 呈现；Adreno 610 已运行 | xVanTuring |
| [一加 10 Pro 5G（negroni）](/zh/devices/negroni) | SM8450 | 已到 iOS 16.7.16 SpringBoard，触控可用；CPU 渲染；Wi-Fi 待完成 | pawlickerr |
| [小米 17 Pro（pandora）](/zh/devices/pandora) | SM8850 | 已到 iOS 16.7.16 锁屏，触控和按键可用；自有加载器，不经 UEFI 链 | ShueiTsuki |
| [小米 13（fuxi）](/zh/devices/fuxi) | SM8550 | 内核可链接和预链接，阶段 B archive 链接近完成，未在真机运行 | matejkoo217、hanzi123-bilp |
| [一加 7 Pro（guacamole）](/zh/devices/guacamole) | SM8150 | 已到达 iOS 16.7.16 用户态，GPU 待完成 | wochgn |
| [一加 Ace 5（giulia）](/zh/devices/giulia) | SM8650 | 已到 Hello/Setup 和 GUI 进度条，触控和安装待完成 | jasper2863、tycykp |
| [小米平板 7 / POCO Pad X1（uke）](/zh/devices/uke) | SM7675 | 根已挂载，launchd 启动；显示 surface 待完成 | Allenwdk |
| [小米平板 8 Pro（piano）](/zh/devices/piano) | SM8750 | 内核在 CI 编译并预链接，未在平板上运行 | code002-2 |
| [小米 13 Pro（nuwa）](/zh/devices/nuwa) | SM8550 | 源内核可编译，平台静态库和预链接待完成 | wh1stl3 |
| [一加 13T（oneplus13t）](/zh/devices/oneplus13t) | SM8750 | 已到 XNU S1 到 S6，根设备查找 panic | IssacL04 |
| [一加平板 2 Pro（erhai）](/zh/devices/erhai) | SM8750 | XNU 入口 bring-up，根和用户态未配置 | wally001012-cyber |
| [OPPO Find X7 Ultra（PHY120）](/zh/devices/phy120) | SM8650 | 启动管理器菜单工作，内核在 CI 构建 | peiyuesheng666 |
| [Redmi K40 Pro（haydn）](/zh/devices/haydn) | SM8350 | 固件、负载和启动镜像已构建，haydn4 从 guacamole 导入 | xiaomi-haydn-dev |
| [小米平板 5（nabu）](/zh/devices/nabu) | SM8150 | XNU 已执行，下一步 PMGR 和用户态 | Lux12138 |
| [一加 6T（fajita）](/zh/devices/fajita) | SDM845 | XNU 已到根挂载，无存储驱动 | johnpanos |
| [Microsoft Surface Duo 2（zeta）](/zh/devices/zeta) | SM8350 | UEFI、菜单和负载工作，内核已构建，未启动 | none24smu |
| [一加 Ace 5 Pro（hummer）](/zh/devices/hummer) | SM8750 | UEFI 层工作，XNU 在 CI 试水 | 2426120557 |
| [小米 15（dada）](/zh/devices/dada) | SM8750 | UEFI 固件工作，UniXNU 和 XNU 未运行 | 7Night-kqx |
| [Redmi Note 14 Pro+ 5G（amethyst）](/zh/devices/amethyst) | SM7635 | 板级文件面向 iPhone10,3，未记录真机运行 | andr0d1v |
| [Redmi K70（vermeer）](/zh/devices/vermeer) | SM8550 | 源码构建基线和从 sheng 派生的设备仓库 | mansar1337、yyx2025 |
| [努比亚红魔 8 Pro / 8 Pro+（nx729j）](/zh/devices/nx729j) | SM8550 | 板级文件从 sheng 移植，运行时未记录 | 2713385115 |
| [小米平板 6（pipa）](/zh/devices/pipa) | SM8250 | 已读取板级和 userdata 数值，未在平板运行 | xVanTuring |
| [Galaxy Tab A7 10.4（gta4l）](/zh/devices/gta4l) | SM6115 | 板级、ADT 和固件可构建，第二个仓库在 CI 构建内核 | NoNameBuilder、ilovemykedi |
| [Redmi Note 10 Pro（sweet）](/zh/devices/sweet) | SM7150 | 平台和加载器 bring-up，无可启动镜像 | dipa-studio |
| [一加 5（cheeseburger）](/zh/devices/cheeseburger) | MSM8998 | 已观察到 XNU 入口色条，MMU 和根未验证 | DinnerABC |
| [Redmi K20 Pro / Mi 9T Pro（raphael）](/zh/devices/raphael) | SM8150 | 新仓库，内核构建未通过 | penYo22 |
| [Galaxy Z Fold3（q2q）](/zh/devices/q2q) | SM8350 | 仅源码内核构建工具 | agcarbajo |
| [Redmi K30 5G（picasso）](/zh/devices/picasso) | SM7250 | 早期骨架，固件未构建 | YinCQL |
| [Redmi 9A（dandelion）](/zh/devices/dandelion) | MT6765 | 早期 bring-up，UEFI 移植进行中 | licg89 |
| [小米 6（sagit）](/zh/devices/sagit) | MSM8998 | 设备仓库，状态未记录 | dmnakzkahziamnk-a11y |

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
