# QCA6390 Wi-Fi (umi)

In-kernel QCA6390 Wi-Fi driver for the Xiaomi Mi 10 (umi, SM8250): PCIe0 and MHI firmware boot, QMI/WLFW, copy engines, HTC/WMI, scan, join and the data path, with an `IO80211Controller` station so iOS's wifid can use it, and WPA2-PSK.

| Repository | Maintainer | Scope |
| --- | --- | --- |
| [ios-umi](https://github.com/qcom-toolbox/ios-umi) | [qcom-toolbox](https://github.com/qcom-toolbox) | [XNU patches 0113–0154, 0201–0203](https://github.com/qcom-toolbox/ios-umi/tree/main/xnu/patches) |

## State

wifid and Settings scan and join open and WPA2-PSK networks on 2.4 GHz at legacy rates. No 5 GHz, no WPA3. Device page: [Xiaomi Mi 10 — iOS 16](/devices/umi-qcom-toolbox).

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the driver and its state; it does not take over maintenance.
