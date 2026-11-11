# SweetAdreno

Adreno 650 kernel GPU driver for the Xiaomi Mi 10 (umi, SM8250). It powers the GPU through the GMU and RPMh, has TrustZone authenticate the zap shader, starts the command processor, and manages buffer objects, fences and per-app GPU memory caps. `SweetAdrenoUserClient` serves Mesa turnip; a Metal-to-Vulkan bridge (metal2vulkan) puts CoreAnimation and Metal apps on it.

| Repository | Maintainer | Scope |
| --- | --- | --- |
| [ios-umi](https://github.com/qcom-toolbox/ios-umi) | [qcom-toolbox](https://github.com/qcom-toolbox) | [XNU patches 0160–0200, 0239–0251](https://github.com/qcom-toolbox/ios-umi/tree/main/xnu/patches); [turnip and metal2 userland](https://github.com/qcom-toolbox/ios-umi/tree/main/phone) |

## State

iOS 16.7.16 (20H392), 2026-11-06: the GPU draws the UI and every Metal app, Safari included. Safari's address bar and the App Library blur still glitch. Device page: [Xiaomi Mi 10 — iOS 16](/devices/umi-qcom-toolbox).

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the driver and its state; it does not take over maintenance.
