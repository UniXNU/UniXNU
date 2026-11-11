# SweetUfs

Own UFS host driver for SM7150 and SM8250, giving XNU a read/write journaled HFS+ root in the `userdata` partition, with DMA above 4 GB.

| Repository | Maintainer | Scope |
| --- | --- | --- |
| [ios-umi](https://github.com/qcom-toolbox/ios-umi) | [qcom-toolbox](https://github.com/qcom-toolbox) | [XNU patches 0028–0034, 0069](https://github.com/qcom-toolbox/ios-umi/tree/main/xnu/patches) |

## State

iOS boots from and writes to the HFS+ root on the Mi 10 and on the Redmi Note 10 Pro (sweet). Device page: [Xiaomi Mi 10 — iOS 16](/devices/umi-qcom-toolbox).

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the driver and its state; it does not take over maintenance.
