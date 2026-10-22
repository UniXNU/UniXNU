# Microsoft Surface Duo 2 (zeta)

zeta is the Microsoft Surface Duo 2 with the SM8350 SoC. The port below is an independent community project. The UniXNU organization does not maintain it. The target identity is iPhone18,2 on iOS 26.5.2.

| Repository | Maintainer | State |
| --- | --- | --- |
| [UniXNU-zeta](https://github.com/none24smu/UniXNU-zeta) | [none24smu](https://github.com/none24smu) | UEFI, menu and payload volume work; kernel builds, not booted |

## State

| Step | State |
| --- | --- |
| UEFI firmware | boots on the phone with `fastboot boot`; UniXNU menu on the panel, volume and power keys work, the boot image ramdisk mounts as the payload volume |
| Device repository | this repository |
| IPSW identity | iPhone18,2 26.5.2 23F84 |
| ADT | zeta hardware values with the iPhone18,2 identity from the IPSW device tree |
| Payload and boot image | kernel builds: xnu-12377.121.6 (iOS 26.5) from the UniXNU `ios26` branch; not prelinked with the 23F84 kexts (arm64e) and not booted |
| Root and userland | not started |

The firmware half is [uefi-zeta](https://github.com/none24smu/uefi-zeta), a Mu-Silicium tree with `Platforms/Microsoft/zetaPkg`.

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the port and its state; it does not take over maintenance.
