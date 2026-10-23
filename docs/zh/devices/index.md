# 支持的设备

一个设备条目由两个仓库和一组让通用栈在该板子上运行的数值组成。下表记录有公开仓库的移植。采用类似 SoC 的板子需要自己的移植和条目。

| 设备 | SoC | 支持功能 | 设备仓库 | 固件 |
| --- | --- | --- | --- | --- |
| 小米平板 6S Pro（sheng） | SM8550 | 显示、触控、UFS、GPU | [UniXNU-sheng](https://github.com/UniXNU/UniXNU-sheng) | [uefi-sheng](https://github.com/UniXNU/uefi-sheng) |

## 社区移植

这里列出的移植独立维护。仓库归各自维护者所有，UniXNU 组织不维护它们。每个条目有自己的页面。表格按完成度排序，已到用户态或完整构建链的移植在前。

| 设备 | SoC | 状态 | 维护者 |
| --- | --- | --- | --- |
| [DroidVM 客户机（Gunyah 上的 crosvm）](/zh/devices/droidvm) | crosvm-gunyah | iPadOS 17 主屏幕，Metal widget 和图标，Keychain 和蓝牙，virtio-net 工作 | Droid-VM |
| [QEMU virt](/zh/devices/qemu) | QEMU virt | iPadOS 17 主屏幕和 Settings；使用 `--metal` 时在 Mac GPU 上运行 Metal | xVanTuring |
| [联想小新 Pad 2022（tb128fu）](/zh/devices/tb128fu) | SM6225 | 已到 iPadOS 17 主屏幕，触控可用；Metal 帧由 GPU 呈现；Adreno 610 已运行 | xVanTuring |
| [一加 10 Pro 5G（negroni）](/zh/devices/negroni) | SM8450 | 已到 iOS 16.7.16 SpringBoard，触控可用；CPU 渲染；Wi-Fi 待完成 | pawlickerr |
| [Nothing Phone (2)（pong）](/zh/devices/pong) | SM8475 | 已到 iOS 16.6.1 主屏幕，显示和触控可用；UFS 和 GPU 部分可用 | Chengdong-Yu |
| [小米 17 Pro（pandora）](/zh/devices/pandora) | SM8850 | 已到 iOS 16.7.16 锁屏，触控和按键可用；自有加载器，不经 UEFI 链 | ShueiTsuki |
| [小米 13（fuxi）](/zh/devices/fuxi) | SM8550 | 内核可链接和预链接，阶段 B archive 链接近完成，未在真机运行 | matejkoo217、hanzi123-bilp |
| [一加 7 Pro（guacamole）](/zh/devices/guacamole) | SM8150 | 已到达 iOS 16.7.16 用户态，GPU 待完成 | wochgn |
| [一加 Ace 5（giulia）](/zh/devices/giulia) | SM8650 | 已到 Hello/Setup，显示完整、触控可用；安装、GPU 和 Wi-Fi 待完成 | jasper2863、tycykp |
| [小米 10（umi）](/zh/devices/umi) | SM8250 | iPadOS 17.7.11 Hello／设置，触摸可用；CPU 显示、UFS 和持久化 Data | reAAAq |
| [小米 MIX 2（chiron）](/zh/devices/chiron) | SDM835 | 真机运行最小 4 KiB XNU 和 PID 1 心跳 | to-mid |
| [小米平板 7 / POCO Pad X1（uke）](/zh/devices/uke) | SM7675 | 根已挂载，launchd 启动；显示 surface 待完成 | Allenwdk |
| [Brave Ark 平板（braveark）](/zh/devices/braveark) | SM8635 | 8 核 XNU BSD init；iPadOS 根卷进行中 | tattwamashi |
| [小米平板 8 Pro（piano）](/zh/devices/piano) | SM8750 | 内核在 CI 编译并预链接，未在平板上运行 | code002-2 |
| [小米 13 Pro（nuwa）](/zh/devices/nuwa) | SM8550 | 源内核可编译，平台静态库和预链接待完成 | wh1stl3 |
| [一加 13T（oneplus13t）](/zh/devices/oneplus13t) | SM8750 | 已到 XNU S1 到 S6，根设备查找 panic | IssacL04 |
| [一加平板 2 Pro（erhai）](/zh/devices/erhai) | SM8750 | XNU 入口 bring-up，根和用户态未配置 | wally001012-cyber |
| [OPPO Find X7 Ultra（PHY120）](/zh/devices/phy120) | SM8650 | 启动管理器菜单工作，内核在 CI 构建 | peiyuesheng666 |
| [Sony Xperia 1 II（pdx203）](/zh/devices/pdx203) | SM8250 | 内核在 CI 编译并预链接；未启动 | chardidathing |
| [Moto Z2 Force（nash）](/zh/devices/nash) | MSM8998 | UEFI、UniXNU 和负载已在真机通过；XNU 阶段需要 macOS | fcxuhaq3 |
| [Redmi K40 Pro（haydn）](/zh/devices/haydn) | SM8350 | 固件、负载和启动镜像已构建，haydn4 从 guacamole 导入 | xiaomi-haydn-dev |
| [小米平板 5（nabu）](/zh/devices/nabu) | SM8150 | XNU 已到 vfs_mountroot，下一步根设备 | Lux12138 |
| [一加 6T（fajita）](/zh/devices/fajita) | SDM845 | XNU 已到根挂载，无存储驱动 | johnpanos |
| [Microsoft Surface Duo 2（zeta）](/zh/devices/zeta) | SM8350 | 内核和根卷 bring-up 到 launchd exec；arm64e launchd 停止 | none24smu |
| [一加 Ace 5 Pro（hummer）](/zh/devices/hummer) | SM8750 | UEFI 工作，XNU SMP 和启动检查点已显示在面板 | 2426120557 |
| [小米 10 Ultra（cas）](/zh/devices/cas) | SM8250 | UEFI 和 UniXNU 菜单已验证，DarwinBoot 和 XNU 未测试 | ht94911 |
| [小米 15（dada）](/zh/devices/dada) | SM8750 | UEFI 工作；UFS UIC 和 MCQ 探针；UniXNU 和 XNU 未运行 | 7Night-kqx |
| [Redmi Note 14 Pro+ 5G（amethyst）](/zh/devices/amethyst) | SM7635 | 板级和启用 legacy display 的内核配置，未记录真机运行 | andr0d1v |
| [Redmi K90 Pro Max / Poco F8 Ultra（myron）](/zh/devices/myron) | SM8850 | 核心和驱动分支，设备仓库与真机结果待完成 | zg7681 |
| [Redmi K70（vermeer）](/zh/devices/vermeer) | SM8550 | 源码构建基线和从 sheng 派生的设备仓库 | mansar1337、yyx2025 |
| [努比亚红魔 8 Pro / 8 Pro+（nx729j）](/zh/devices/nx729j) | SM8550 | 设备仓库包含 NativeUfs 和 SMMU group，运行时未记录 | 2713385115 |
| [小米平板 6（pipa）](/zh/devices/pipa) | SM8250 | 已读取板级和 userdata 数值，未在平板运行 | xVanTuring |
| [Galaxy Tab A7 10.4（gta4l）](/zh/devices/gta4l) | SM6115 | 板级、ADT 和固件可构建，第二个仓库在 CI 构建内核 | NoNameBuilder、ilovemykedi |
| [Redmi Note 10 Pro（sweet）](/zh/devices/sweet) | SM7150 | 平台和加载器 bring-up，无可启动镜像 | dipa-studio |
| [一加 5（cheeseburger）](/zh/devices/cheeseburger) | MSM8998 | 已观察到 XNU 入口色条，MMU 和根未验证 | DinnerABC |
| [Redmi K20 Pro / Mi 9T Pro（raphael）](/zh/devices/raphael) | SM8150 | 新仓库，内核构建未通过 | penYo22 |
| [Galaxy Z Fold3（q2q）](/zh/devices/q2q) | SM8350 | 仅源码内核构建工具 | agcarbajo |
| [Redmi K30 5G（picasso）](/zh/devices/picasso) | SM7250 | 早期骨架，固件未构建 | YinCQL |
| [Redmi Note 9（merlinx）](/zh/devices/merlinx) | MT6768 | UEFI 可启动，自定义菜单工作；存储初始化阻塞 UniXNU 和 XNU | Dracen-W |
| [Benesse TAB-A04-BR3（a04br3）](/zh/devices/a04br3) | MT8167 | 板级、固件、eMMC 和 GPT 已准备；无真机运行 | mouseos |
| [Redmi 9A（dandelion）](/zh/devices/dandelion) | MT6765 | 早期 bring-up，UEFI 移植进行中 | licg89 |
| [小米 6（sagit）](/zh/devices/sagit) | MSM8998 | 设备仓库，状态未记录 | dmnakzkahziamnk-a11y |
| [Google Pixel 9 Pro XL（komodo）](/zh/devices/komodo) | Tensor G4 | 板级、defconfig 和 ADT；UEFI 独立；无真机运行 | Trijal08 |
| [小米 9（cepheus）](/zh/devices/cepheus) | SDM855 | 设备仓库和启动链已准备；无真机结果 | sxl47 |
| [小米 MIX Flip（ruyi）](/zh/devices/ruyi) | SM8650 | 板级和 defconfig；无 README 或真机结果 | ArnoDorian123 |
| [小米 Civi 5 Pro（luming）](/zh/devices/luming) | SM8735 | 预构建骨架；未构建或启动 | infinityEX-RSXQ |
| [小米平板 6 Pro（liuqin）](/zh/devices/liuqin) | SM8475 | 板级、defconfig 和内核 USB 调试口；下一步 UEFI | 1696108518 |
| [小米平板 5 Pro 5G（enuma）](/zh/devices/enuma) | SM8250-AC | 设备仓库；UEFI 和可烧写镜像缺失 | wh1stl3、Tlrenhb |
| [Redmi Turbo 3 / Poco F6（peridot）](/zh/devices/peridot) | SM8635 | WIP 设备仓库；无真机结果 | kvfsrl、hoshikv |
| [一加 8 Pro（instantnoodlep）](/zh/devices/instantnoodlep) | SM8250 | UEFI 平台和内核基线；状态未记录 | zhangp996 |
| [一加 8T（kebab）](/zh/devices/kebab) | SM8250 | 第一个里程碑：仅 kernel.macho | GFander |
| [一加 6（enchilada）](/zh/devices/enchilada) | SDM845 | 设备仓库；状态未记录 | keyfan |
| [一加 15T（fairlady）](/zh/devices/fairlady) | SM8850 | 早期移植，带 S1 到 S6 诊断；无真机结果 | Osilvfe |
| [一加平板 Pro（caihong）](/zh/devices/caihong) | SM8650 | 板级和 defconfig；UEFI 集成未完成 | Axiang-dev |
| [Nothing Phone (3a)（asteroids）](/zh/devices/asteroids) | SM7635 | UEFI 到达 DXE 和 BDS；未到 UniXNU 和 XNU | rootstockos |
| [Galaxy Tab S9 Ultra Wi-Fi（gts9uwifi）](/zh/devices/gts9uwifi) | SM-X910 | 设备仓库；状态未记录 | zc47796741-pixel |
| [Moto G9 Play（guamp）](/zh/devices/guamp) | SM6115 | UEFI 菜单可启动；内核未构建 | itsChris122 |
| [Moto G 5G（gauguin）](/zh/devices/gauguin) | SM7125 | 设备仓库；状态未记录 | lvyufeng |
| [Microsoft Lumia 950](/zh/devices/lumia950) | MSM8992 | 设备仓库；使用手机自带 UEFI；未启动 | ManGuy-Legend |
| [OPPO R11（r11）](/zh/devices/r11) | SDM660 | 板级、defconfig 和硬件笔记；状态未记录 | huhaitao1136-cpu |
| [OPPO Find X9（x9）](/zh/devices/x9) | MT6993 | 未到 UEFI；约 25 到 30% | tosasitill |
| [Unisoc 设备](/zh/devices/unisoc) | Unisoc | 核心分支；尚无具体设备移植 | hxzbaka |
| [unixnu-build](/zh/devices/unixnu-build) | 构建树 | 仅构建树；设备未记录 | iskssksjjsjjzjs |
| [sheng 上的 macOS](/zh/devices/sheng-macos) | SM8550 | macOS 27 bring-up；不是 iOS 设备移植 | Jelly10086 |

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
