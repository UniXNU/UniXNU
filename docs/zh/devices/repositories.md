# 社区仓库索引

本页列出还没有单独设备页的公开 UniXNU 仓库。列入这里是为了完整覆盖；只有仓库自己记录状态时才写入状态。

## 设备移植

| 设备 | SoC | 仓库 | 状态 |
| --- | --- | --- | --- |
| Google Pixel 9 Pro XL（komodo） | Tensor G4 | [UniXNU-komodo](https://github.com/Trijal08/UniXNU-komodo) | 板级、defconfig 和 ADT；UEFI 为独立仓库；无真机运行 |
| Sony Xperia 1 II（pdx203） | SM8250 | [UniXNU-pdx203](https://github.com/chardidathing/UniXNU-pdx203) | 内核在 CI 编译并预链接；未启动 |
| 小米 9（cepheus） | SDM855 | [UniXNU-cepheus](https://github.com/sxl47/UniXNU-cepheus) | 设备仓库和启动链已准备；未记录真机结果 |
| 小米 MIX 2（chiron） | SDM835 | [ios-party](https://github.com/to-mid/ios-party) | 真机运行最小 4 KiB XNU 和 PID 1 心跳；无完整 iOS 用户态 |
| 小米 MIX Flip（ruyi） | SM8650 | [UniXNU-ruyi-min](https://github.com/ArnoDorian123/UniXNU-ruyi-min) | 板级和 defconfig；无 README 或真机结果 |
| 小米 Civi 5 Pro（luming） | SM8735 | [UniXNU-luming](https://github.com/infinityEX-RSXQ/-UniXNU-luming) | 预构建骨架；静态检查通过；未构建或启动 |
| 小米平板 6 Pro（liuqin） | SM8475 | [UniXNU-liuqin](https://github.com/1696108518/UniXNU-liuqin) | 板级、defconfig 和内核 USB 调试口；下一步 UEFI |
| 小米平板 5 Pro 5G（enuma） | SM8250-AC | [UniXNU-enuma](https://github.com/wh1stl3/UniXNU-enuma)、[UniXNU-enuma](https://github.com/Tlrenhb/UniXNU-enuma) | 设备仓库；UEFI 和可烧写镜像缺失 |
| Redmi Turbo 3 / Poco F6（peridot） | SM8635 | [UniXNU-peridot](https://github.com/kvfsrl/UniXNU-peridot)、[UniXNU-peridot-standalone](https://github.com/hoshikv/UniXNU-peridot-standalone) | WIP 设备仓库；PR #52 |
| 一加 8 Pro（instantnoodlep） | SM8250 | [UniXNU-instantnoodlep](https://github.com/zhangp996/UniXNU-instantnoodlep) | UEFI 平台和内核基线；状态未记录 |
| 一加 8T（kebab） | SM8250 | [UniXNU-kebab](https://github.com/GFander/UniXNU-kebab) | 第一个里程碑：仅 kernel.macho |
| 一加 6（enchilada） | SDM845 | [UniXNU-enchilada](https://github.com/keyfan/UniXNU-enchilada) | 设备仓库；状态未记录 |
| 一加 15T（fairlady） | SM8850 | [UniXNU-fairlady](https://github.com/Osilvfe/UniXNU-fairlady) | 早期移植，带 S1 到 S6 诊断；未记录真机结果 |
| 一加平板 Pro（caihong） | SM8650 | [UniXNU-caihong](https://github.com/Axiang-dev/UniXNU-caihong) | 板级和 defconfig；UEFI 集成未完成 |
| Nothing Phone (3a)（asteroids） | SM7635 | [UniXNU-asteroids](https://github.com/rootstockos/UniXNU-asteroids) | UEFI 到达 DXE 和 BDS；未到 UniXNU 和 XNU |
| Brave Ark 平板（braveark） | SM8635 | [UniXNU-braveark](https://github.com/tattwamashi/UniXNU-braveark) | UEFI、菜单、负载、DarwinBoot 和 8 核 XNU BSD init；根卷进行中 |
| Galaxy Tab S9 Ultra Wi-Fi（gts9uwifi） | SM-X910 | [UniXNU-gts9uwifi](https://github.com/zc47796741-pixel/UniXNU-gts9uwifi) | 设备仓库；状态未记录 |
| Moto Z2 Force（nash） | MSM8998 | [UniXNU-nash](https://github.com/fcxuhaq3/UniXNU-nash) | UEFI、UniXNU 和负载已在真机通过；XNU 阶段需要 macOS |
| Moto G9 Play（guamp） | SM6115 | [UniXNU-guamp](https://github.com/itsChris122/UniXNU-guamp) | UEFI 菜单可启动；内核未构建 |
| Moto G 5G（gauguin） | SM7125 | [UniXNU-gauguin](https://github.com/lvyufeng/UniXNU-gauguin) | 设备仓库；状态未记录 |
| Microsoft Lumia 950 | MSM8992 | [UniXNU-lumia950](https://github.com/ManGuy-Legend/UniXNU-lumia950) | 设备仓库；使用手机自带 UEFI；未启动 |
| OPPO R11（r11） | SDM660 | [unixnu-r11](https://github.com/huhaitao1136-cpu/unixnu-r11) | 板级、defconfig 和硬件笔记；状态未记录 |
| OPPO Find X9（x9） | MT6993 | [unixnu_x9](https://github.com/tosasitill/unixnu_x9) | 未到 UEFI；约 25 到 30% |

## 相关和替代仓库

| 设备或项目 | 仓库 | 说明 |
| --- | --- | --- |
| 小米 13（fuxi） | [unixnu-fuxi](https://github.com/Xyvern08371/unixnu-fuxi) | fuxi 替代仓库 |
| Redmi Note 10 Pro（sweet） | [UniXNU-sweet](https://github.com/CrackerCat/UniXNU-sweet) | sweet 替代仓库 |
| 一加 5（cheeseburger） | [UniXNU-cheeseburger](https://github.com/lss717/UniXNU-cheeseburger) | cheeseburger 替代仓库 |
| 小米 10 Ultra（cas） | [UniXNU-cas](https://github.com/pxl777806/UniXNU-cas) | cas 替代仓库 |
| 小米平板 5（nabu） | [unixnu-nabu](https://github.com/zzc775/unixnu-nabu)、[unixnu-nabu-build](https://github.com/3214791900-del/unixnu-nabu-build)、[uefi-nabu-build](https://github.com/3214791900-del/uefi-nabu-build) | 替代和构建仓库 |
| 用于 vermeer 的 QEMU virt | [UniXNU-qemu](https://github.com/yyx2025/UniXNU-qemu) | vermeer bring-up 使用的 QEMU virt 仓库 |
| Redmi K70（vermeer） | [k70-unixnu-build](https://github.com/wuan0039/k70-unixnu-build)、[k70-unixnu-build-20261022](https://github.com/xyyyds0106/k70-unixnu-build-20261022) | 内核 CI 和固定构建仓库 |
| Unisoc 设备 | [UniXNU-Unisoc](https://github.com/hxzbaka/UniXNU-Unisoc) | Unisoc 设备核心分支；尚无具体设备移植 |
| 小米平板 6S Pro（sheng） | [macOS-ForSheng](https://github.com/Jelly10086/macOS-ForSheng) | 基于 UniXNU 和 Snapintosh 的 macOS 27 bring-up；不是 iOS 设备移植 |
| 未分类构建树 | [unixnu-build](https://github.com/iskssksjjsjjzjs/unixnu-build) | 仅构建树；设备未记录 |

## 维护

各维护者拥有自己的仓库和发布决定。本索引记录公开仓库和仓库文档声明的状态，不接管维护。
