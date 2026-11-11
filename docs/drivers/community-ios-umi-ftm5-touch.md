# SweetHIDTouch

ST FTM5 touch driver for the Xiaomi Mi 10 (umi, SM8250) over GENI I²C with GPI DMA, powered from the PM8150B GPIO 5 boost rail, delivered as HID digitizer events. `SweetHIDButtons` reports power and volume keys from the PM8150 PON block over SPMI.

| Repository | Maintainer | Scope |
| --- | --- | --- |
| [ios-umi](https://github.com/qcom-toolbox/ios-umi) | [qcom-toolbox](https://github.com/qcom-toolbox) | [XNU patches 0083–0109](https://github.com/qcom-toolbox/ios-umi/tree/main/xnu/patches) |

## State

Touch, power and volume keys work; lock and wake work. Device page: [Xiaomi Mi 10 — iOS 16](/devices/umi-qcom-toolbox).

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the driver and its state; it does not take over maintenance.
