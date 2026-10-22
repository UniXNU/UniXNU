# 一加平板 2 Pro（erhai）

erhai 是搭载 SM8750 的一加平板 2 Pro（OPD2413）。下面的移植是独立的社区项目，UniXNU 组织不维护它。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [UniXNU-erhai](https://github.com/wally001012-cyber/UniXNU-erhai) | [wally001012-cyber](https://github.com/wally001012-cyber) | XNU 入口 bring-up，根和用户态未配置 |

## 状态

| 区域 | 状态 |
| --- | --- |
| 板级数值 | 已在设备上测量：FD 基址 `0xA7000000`、GIC、时钟、面板、触控和 boot 分区 |
| UEFI 和负载 | `embed_payload` 把负载放在 kernel 字段，因为一加 ABL 在 `fastboot boot` 时会替换 ramdisk 字段 |
| 内核 | source-only 内核，在 GitHub Actions 构建；bring-up 配置只在启动 CPU 上运行，预链接中移除了 AMFI |
| 屏幕检查点 | 绿色条加 S1 到 S6 |
| 根、UFS 和 GPU | 当前配置未启用 |
| 硬件结果 | 仓库记录了测量值和预期的 S1 到 S6 顺序 |

板级结构参考一加 13T 移植。当前目标是 XNU 入口，不是根文件系统或用户态。

## 构建

```sh
python unixnu --prepare
python unixnu defconfig erhai_defconfig
python unixnu bootimg --dtb <device.dtb> --ramdisk <payload.img> -o boot.img
```

内核和负载在 GitHub Actions 中构建：

```
Actions -> erhai XNU (OnePlus Pad 2 Pro) -> Run workflow
```

只用 `fastboot boot boot.img` 启动，不要刷写分区。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
