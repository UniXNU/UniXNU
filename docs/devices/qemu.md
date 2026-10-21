# QEMU virt

The QEMU target runs UniXNU on the AArch64 `virt` machine. It substitutes for a tablet during bring-up. The port below is an independent community project. The UniXNU organization does not maintain it.

| Repository | Maintainer | State |
| --- | --- | --- |
| [UniXNU-qemu](https://github.com/xVanTuring/UniXNU-qemu) | [xVanTuring](https://github.com/xVanTuring) | iPadOS 17 home screen and Settings |

## State

| Stage | State |
| --- | --- |
| UniXNU menu, configuration, DarwinBoot as a driver | works |
| DarwinBoot handoff, 4 GiB window, kernel entry, MMU and 4 KiB page tables | works |
| Platform expert and IOKit | works |
| Verified VirtIO root | works; owner-signed root mounted |
| AMFI and original launchd | start with the original trust cache |
| SystemOS union and dyld shared cache | work |
| Data ramdisk | works |
| Display | NativeLegacyDisplay on ramfb; CPU-rendered |
| Touch and Home | work; typing not yet |
| GPU | no Metal device |

The repository README records the commands that stage the ESP and boot QEMU.

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the port and its state; it does not take over maintenance.
