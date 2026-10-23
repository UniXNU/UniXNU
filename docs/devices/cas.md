# Xiaomi 10 Ultra (cas)

cas is the Xiaomi 10 Ultra (M2007J1SC) with the SM8250 SoC and about 12 GB of RAM. The port below is an independent community project. The UniXNU organization does not maintain it.

| Repository | Maintainer | State |
| --- | --- | --- |
| [UniXNU-cas](https://github.com/ht94911/UniXNU-cas) | [ht94911](https://github.com/ht94911) | UEFI and UniXNU menu on hardware; DarwinBoot and XNU not tested |
| [uefi-cas](https://github.com/ht94911/uefi-cas) | [ht94911](https://github.com/ht94911) | Mu-Silicium firmware port |
| [UniXNU-cas](https://github.com/pxl777806/UniXNU-cas) | [pxl777806](https://github.com/pxl777806) | Alternate cas repository; status not documented |

## State

| Area | State |
| --- | --- |
| UEFI and UniXNU menu | temporary `fastboot boot`; 1080x2340 display; physical volume and power controls work |
| Payload | read-only 16 MiB RAM FAT; CasSmoke EFI loads, runs and returns to the menu; a missing file reports `Not Found` |
| Reboot | the menu returns to Android, including the firmware information menu |
| Repeatability | three complete runs with the same image; a clean rebuild matched 34 artifacts; 126 source tests pass |
| Partition integrity | 18 protected partition hashes and the primary and backup GPT of six UFS LUNs stayed unchanged across the three runs |
| DarwinBoot, XNU, iOS | not tested |
| Touch and GPU | not tested |

The tested tablet ran Android 15 / OS3.0.4.0.VMKCNXM. The build uses UniXNU `67e8ef0`. The full boot image needs a matching stock DTB and is not distributed.

## Maintenance

The maintainer owns the repositories and their release decisions. UniXNU documentation lists the port and its state; it does not take over maintenance.
