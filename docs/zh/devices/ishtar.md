# 小米 13 Ultra（ishtar）

ishtar 是搭载 SM8550 的小米 13 Ultra。下面的仓库是独立的社区移植，UniXNU 组织不维护它。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [UniXNU-ishtar](https://github.com/peter8889/UniXNU-ishtar) | [peter8889](https://github.com/peter8889) | 设备仓库；内核、载荷与启动镜像在宿主机全链路构建通过，阶段诊断已就位，未在真机运行 |

## UniXNU-ishtar

UniXNU-ishtar 基于 UniXNU-sheng，复用它的 kit、archive 计划和 iPadOS 17.7.11（21H461）OS profile，只替换板级数据。`board.toml` 是格式 2，`feeds.toml` 固定 SM8550 共享源码，`dts/ishtar.dts` 只描述板级差异并包含共享 SoC 描述。

宿主机侧构建链路已经完整打通：`./unixnu kernel`、`./unixnu payload`、`./unixnu bootimg` 依次产出内核、载荷与启动镜像，组装后的镜像通过自身的往返检查，容器头、载荷窗口和分区几何一致。配置、固件、CPU、内存、镜像组装和诊断六部分因此进入实现状态，设备树、内核配置和固件包也已对齐到同一套板级身份。

诊断是这一阶段的主要成果。`CONFIG_XNU_BOOT_PROGRESS` 把内核阶段直接画到固件帧缓冲上，在任何显示驱动存在之前就能看到内核停在哪一步。该实现自包含，不读存储或 Virtio 计数器，因此任何配置都能链接；完整版监控器需要存储、owner-root、Virtio 和源码 corecrypto 的审计构建，留待存储就位后再切换。

存储、显示、输入、GPU、网络、音频和电源是下一阶段。GPU 已进入组件选择并链接桩（`scripts/build-adreno-link-stubs.py`），因为完整驱动需要 payload 阶段的 accelerator ABI，内核链接没有对应的变量。UFS 和显示驱动在 `gpu_defconfig` 里保持关闭，但设备树已经把 `ufs`、`ufsphy`、`gpu`、`gmu`、`gpu_smmu` 全部打开，打开驱动因此是改配置而不是改设备树。触摸固件已在 `proprietary-files.txt` 里按上游提交固定，只差把驱动加入组件选择。

设备树声明 8 GiB DRAM，低于实装容量是刻意的：物理光圈和页表分配器否则会触到没有 DRAM 支撑的地址。splash 保留区在 `0xb8000000`，面板 1440×3200，stride 5760 字节，标记 `no-map`，因为把它当作普通内存会让分配器把帧缓冲分出去。分区几何取自已出厂的 GPT，只对没有重新分区的机器有效。

移植记录见 `porting.toml`。

## 维护

表中的维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
