# 一加 6T（fajita）

fajita 是搭载 SDM845 的一加 6T。下面的移植是独立的社区项目，UniXNU 组织不维护它。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [UniXNU-fajita](https://github.com/johnpanos/UniXNU-fajita) | [johnpanos](https://github.com/johnpanos) | XNU 已到根挂载，无存储驱动 |

## 状态

| 阶段 | 状态 |
| --- | --- |
| UEFI 固件和 UniXNU 菜单 | 用 `fastboot boot` 和空 ramdisk 在真机工作 |
| 负载、ADT 和内核 | iPadOS 17.7.11 kernelcache 的 XNU 23.6.0 在真机启动到根挂载，VM、调度器、IOKit、AMFI、Sandbox 和 APFS 启动 |
| 根卷 | 详细控制台停在 `Waiting on ... IOMedia ... Apple_HFS`，尚未有存储驱动 |
| userdata | 8.74 GiB iPadOS 17.7.11 根镜像已构建并刷入，尚无内核读取 |

ABL 拒绝大 ramdisk，因此负载卷刷到 `boot_a`，启动镜像不带 ramdisk。每次 `fastboot boot` 前运行 `fastboot set_active b`；活动槽的 boot 分区有镜像或重试计数耗尽时，ABL 会拒绝启动。

## 构建

```sh
./unixnu defconfig fajita_defconfig -D ../UniXNU-fajita
./unixnu fetch
./unixnu build package firmware --uefi ../Mu-Silicium
./unixnu bootimg --uefi ../Mu-Silicium --dtb ../Mu-Silicium/Resources/DTBs/fajita.dtb
```

固件由 `scripts/make-fajita-uefi.py` 从 enchilada 移植派生。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
