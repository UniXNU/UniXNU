# ios-umi boot shim

Bare-metal boot shim packed as an Android boot.img v2. Started by the stock Xiaomi ABL, it sets up its own MMU, reads the live FDT and loads XNU with a generated Apple Device Tree and boot-args, without UEFI.

| Repository | Maintainer | Scope |
| --- | --- | --- |
| [ios-umi](https://github.com/qcom-toolbox/ios-umi) | [qcom-toolbox](https://github.com/qcom-toolbox) | [shim](https://github.com/qcom-toolbox/ios-umi/tree/main/shim); [ADT generator](https://github.com/qcom-toolbox/ios-umi/tree/main/tools/mkadt.py) |

## State

Boots XNU on the Mi 10 through `fastboot boot` or flashed to `boot`; the same image picks the board from the device tree. Device page: [Xiaomi Mi 10 — iOS 16](/devices/umi-qcom-toolbox).

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the driver and its state; it does not take over maintenance.
