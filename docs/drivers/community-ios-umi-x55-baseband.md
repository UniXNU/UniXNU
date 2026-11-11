# AppleBaseband (X55, umi)

Snapdragon X55 modem support for the Xiaomi Mi 10 (umi, SM8250): PCIe2 probe, BHI/SBL1 and MHI Sahara boot to mission mode, QMI clients, TFTP and EFS servers, UIM/USIM provisioning and the WDA/WDS data session. `sweet-telephonyd` stands in for CommCenter and answers CoreTelephony from the modem's state.

| Repository | Maintainer | Scope |
| --- | --- | --- |
| [ios-umi](https://github.com/qcom-toolbox/ios-umi) | [qcom-toolbox](https://github.com/qcom-toolbox) | [XNU patches 0259–0275](https://github.com/qcom-toolbox/ios-umi/tree/main/xnu/patches); [sweet-telephonyd](https://github.com/qcom-toolbox/ios-umi/tree/main/phone/sweet-telephonyd) |

## State

The modem registers on LTE with the SIM; the status bar shows the carrier with signal bars. A data session opens (IPv4, DNS) but carries no packets yet. Calls and SMS are not planned. Device page: [Xiaomi Mi 10 — iOS 16](/devices/umi-qcom-toolbox).

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the driver and its state; it does not take over maintenance.
