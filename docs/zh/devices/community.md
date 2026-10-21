# 社区移植

这些移植独立维护。仓库归各自维护者所有，UniXNU 组织不维护它们。状态来自各仓库在 2026-10-22 的 README。没有记录状态的仓库会注明。

| 设备 | SoC | 状态 | 仓库 | 维护者 |
| --- | --- | --- | --- | --- |
| [小米 13（fuxi）](/zh/devices/fuxi) | SM8550 | 设备仓库，进行中 | [UniXNU-fuxi](https://github.com/matejkoo217/UniXNU-fuxi) | [matejkoo217](https://github.com/matejkoo217) |
| [小米 13（fuxi）](/zh/devices/fuxi) | SM8550 | 设备和固件仓库，状态未记录 | [unixnu-fuxi](https://github.com/hanzi123-bilp/unixnu-fuxi)、[uefi-fuxi](https://github.com/hanzi123-bilp/uefi-fuxi) | [hanzi123-bilp](https://github.com/hanzi123-bilp) |
| Redmi Note 10 Pro（sweet） | SM7150 | 平台和加载器 bring-up，无可启动镜像 | [UniXNU-sweet](https://github.com/dipa-studio/UniXNU-sweet) | [dipa-studio](https://github.com/dipa-studio) |
| 一加 Ace 5 Pro（hummer） | SM8750 | UEFI 层工作，XNU 在 CI 试水，GPU 和持久 Data 未开始 | [UniXNU-hummer](https://github.com/2426120557/UniXNU-hummer) | [2426120557](https://github.com/2426120557) |
| 小米 6（sagit） | MSM8998 | 设备仓库，状态未记录 | [UniXNU-sagit](https://github.com/dmnakzkahziamnk-a11y/UniXNU-sagit) | [dmnakzkahziamnk-a11y](https://github.com/dmnakzkahziamnk-a11y) |
| 小米平板 8 Pro（piano） | SM8750 | 内核在 CI 编译并预链接，未在平板上运行 | [UniXNU-piano](https://github.com/code002-2/UniXNU-piano) | [code002-2](https://github.com/code002-2) |
| Redmi Note 14 Pro+ 5G（amethyst） | SM7635 | 进行中，状态未记录 | [UniXNU-amethyst](https://github.com/andr0d1v/UniXNU-amethyst) | [andr0d1v](https://github.com/andr0d1v) |
| Redmi K70（vermeer） | SM8550 | 源码 XNU 构建基线，不是启动镜像 | [UniXNU-vermeer](https://github.com/mansar1337/UniXNU-vermeer) | [mansar1337](https://github.com/mansar1337) |
| Redmi K70（vermeer） | SM8550 | 从 sheng 移植的设备仓库，状态未记录 | [UniXNU-vermeer](https://github.com/yyx2025/UniXNU-vermeer) | [yyx2025](https://github.com/yyx2025) |
| DroidVM 客户机（Gunyah 上的 crosvm） | crosvm-gunyah | iPadOS 17 锁屏和主屏幕，CPU 渲染，SM8650 上 Data 可持久化 | [UniXNU-droidvm](https://github.com/Droid-VM/UniXNU-droidvm) | [Droid-VM](https://github.com/Droid-VM) |
| QEMU virt | QEMU virt | iPadOS 17 主屏幕和 Settings，CPU 渲染，无 GPU | [UniXNU-qemu](https://github.com/xVanTuring/UniXNU-qemu) | [xVanTuring](https://github.com/xVanTuring) |
| Redmi 9A（dandelion） | MT6765 | 早期 bring-up，直接启动失败，UEFI 移植进行中，无 UART | [UniXNU-dandelion](https://github.com/licg89/UniXNU-dandelion) | [licg89](https://github.com/licg89) |
| Galaxy Z Fold3（q2q） | SM8350 | 仅源码内核构建工具，不能启动用户态 | [UniXNU-q2q](https://github.com/agcarbajo/UniXNU-q2q) | [agcarbajo](https://github.com/agcarbajo) |
| 小米 15（dada） | SM8750 | UEFI 固件工作，UniXNU 菜单和 DarwinBoot 未在真机运行 | [UniXNU-dada](https://github.com/7Night-kqx/UniXNU-dada) | [7Night-kqx](https://github.com/7Night-kqx) |
| 小米平板 6（pipa） | SM8250 | 无平板时准备，未在真机运行 | [UniXNU-pipa](https://github.com/xVanTuring/UniXNU-pipa)、[uefi-pipa](https://github.com/xVanTuring/uefi-pipa) | [xVanTuring](https://github.com/xVanTuring) |
| Redmi K40 Pro（haydn） | SM8350 | 设备仓库和 UEFI 方案，固件、负载和启动镜像已构建，未在真机运行 | [UniXNU-haydn](https://github.com/xiaomi-haydn-dev/UniXNU-haydn) | [xiaomi-haydn-dev](https://github.com/xiaomi-haydn-dev) |
| [小米平板 7 / POCO Pad X1（uke）](/zh/devices/uke) | SM7675 | 已到 XNU 入口，等待根设备 | [UniXNU-uke](https://github.com/Allenwdk/UniXNU-uke)、[uefi-uke](https://github.com/Allenwdk/uefi-uke) | [Allenwdk](https://github.com/Allenwdk) |
| 小米平板 5（nabu） | SM8150 | XNU 已执行，下一步 PMGR 和用户态 | [unixnu-nabu](https://github.com/Lux12138/unixnu-nabu) | [Lux12138](https://github.com/Lux12138) |
| Galaxy Tab A7 10.4（gta4l） | SM6115 | 板级、ADT 和固件可构建，内核未构建，未在真机启动 | [UniXNU-gta4l](https://github.com/NoNameBuilder/UniXNU-gta4l) | [NoNameBuilder](https://github.com/NoNameBuilder) |
| 一加 13T（oneplus13t） | SM8750 | UEFI Shell 和菜单，XNU 构建和负载，DarwinBoot 交接，尚未进入 XNU | [UniXNU-oneplus13t](https://github.com/IssacL04/UniXNU-oneplus13t) | [IssacL04](https://github.com/IssacL04) |

`BigfootACA/unixnu-droidvm-ci` 为 QEMU/KVM 和 DroidVM 目标提供 CI 构建。
