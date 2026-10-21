# Samsung Galaxy Tab A7 10.4 (gta4l)

gta4l is the Samsung Galaxy Tab A7 10.4 (2020), model SM-T500 or SM-T505, with the SM6115 SoC. The port below is an independent community project. The UniXNU organization does not maintain it.

| Repository | Maintainer | State |
| --- | --- | --- |
| [UniXNU-gta4l](https://github.com/NoNameBuilder/UniXNU-gta4l) | [NoNameBuilder](https://github.com/NoNameBuilder) | Board, ADT and firmware build; kernel not built |

## State

| Layer | State |
| --- | --- |
| Board description | parses; `defconfig`, `fetch` and `tree` run |
| Firmware | builds on Linux: `gta4lPkg` plus UniXNU and DarwinBoot, 3,145,728 bytes |
| ADT | emits 13,180 bytes for the 8 Kryo 260 cores |
| Kernel | not built; the UniXNU kernel step needs macOS and Xcode |
| Payload and boot image | not built; depends on the kernel |
| Hardware boot | not demonstrated under UniXNU; a separate ios-topaz 16 KiB build reaches the XNU console |

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the port and its state; it does not take over maintenance.
