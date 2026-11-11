# SweetUfs

自研 UFS 主机驱动，支持 SM7150 与 SM8250，为 XNU 提供 `userdata` 分区中可读写的日志式 HFS+ 根卷，支持 4 GB 以上 DMA。

| 仓库 | 维护者 | 范围 |
| --- | --- | --- |
| [ios-umi](https://github.com/qcom-toolbox/ios-umi) | [qcom-toolbox](https://github.com/qcom-toolbox) | [XNU 补丁 0028–0034、0069](https://github.com/qcom-toolbox/ios-umi/tree/main/xnu/patches) |

## 状态

在小米 10 与红米 Note 10 Pro（sweet）上，iOS 可从 HFS+ 根卷启动并写入。 设备页面：[小米 10 — iOS 16](/zh/devices/umi-qcom-toolbox)。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录驱动及其状态，不接管维护。
