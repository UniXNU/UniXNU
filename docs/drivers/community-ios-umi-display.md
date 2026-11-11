# AppleCLCD / AppleARMBacklight (umi)

Display stack for the Xiaomi Mi 10 (umi, SM8250): IOSurface and IOMobileFramebuffer (`AppleCLCD`) with direct scanout through the display SMMU, presenting the 1080×2340 AMOLED as the iPhone X panel; `AppleARMBacklight` sets brightness with DCS 0x51 over DSI, turns the panel off on lock, and maps Night Shift to the DSPP PCC.

| Repository | Maintainer | Scope |
| --- | --- | --- |
| [ios-umi](https://github.com/qcom-toolbox/ios-umi) | [qcom-toolbox](https://github.com/qcom-toolbox) | [XNU patches 0046, 0091–0092, 0205–0207](https://github.com/qcom-toolbox/ios-umi/tree/main/xnu/patches) |

## State

CoreAnimation frames reach the panel; brightness slider, Control Center and Night Shift work. Device page: [Xiaomi Mi 10 — iOS 16](/devices/umi-qcom-toolbox).

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the driver and its state; it does not take over maintenance.
