# OnePlus 5 (cheeseburger)

cheeseburger is the OnePlus 5 with the MSM8998 SoC. The port below is an independent community project. The UniXNU organization does not maintain it. The target is the iPhone iOS userland.

| Repository | Maintainer | State |
| --- | --- | --- |
| [UniXNU-cheeseburger](https://github.com/DinnerABC/UniXNU-cheeseburger) | [DinnerABC](https://github.com/DinnerABC) | UEFI and menu work; XNU entry bar observed; MMU and root unverified |

## State

| Layer | State |
| --- | --- |
| Native UEFI and integrated firmware | builds; the stock image reaches the EFI Shell on hardware |
| UniXNU menu | the graphical menu runs on hardware |
| DarwinBoot | file hashes, Mach-O load, ADT, `boot_args` and the EBS handoff are recorded |
| XNU | independent MSM8998 ARM64 build; the P5 image shows the XNU `__start` entry color bar |
| MMU, C initialization, root volume and iOS | not verified |
| Board file | `example = true`; the incomplete board is refused by the general build and boot image steps |

The P1 GitHub Actions run failed in `actions/setup-python` before the audit, so there is no remote build pass yet.

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the port and its state; it does not take over maintenance.
