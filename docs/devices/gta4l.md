# Samsung Galaxy Tab A7 10.4 (gta4l)

gta4l is the Samsung Galaxy Tab A7 10.4 (2020), model SM-T500 or SM-T505, with the SM6115 SoC. The ports below are independent community projects. The UniXNU organization does not maintain them.

| Repository | Maintainer | State |
| --- | --- | --- |
| [UniXNU-gta4l](https://github.com/NoNameBuilder/UniXNU-gta4l) | [NoNameBuilder](https://github.com/NoNameBuilder) | Board, ADT and firmware build; kernel not built |
| [UniXNU-gta4l](https://github.com/ilovemykedi/UniXNU-gta4l) | [ilovemykedi](https://github.com/ilovemykedi) | Board and defconfig; kernel builds in CI; no hardware result |

## State

| Layer | State |
| --- | --- |
| Board description | parses; `defconfig`, `fetch` and `tree` run |
| Firmware | builds on Linux: `gta4lPkg` plus UniXNU and DarwinBoot, 3,145,728 bytes |
| ADT | emits 13,180 bytes for the 8 Kryo 260 cores |
| Kernel | not built; the UniXNU kernel step needs macOS and Xcode |
| Payload and boot image | not built; depends on the kernel |
| Hardware boot | not demonstrated under UniXNU; a separate ios-topaz 16 KiB build reaches the XNU console |

## ilovemykedi repository

`ilovemykedi/UniXNU-gta4l` is a second repository for the same tablet. It carries the board file, `gta4l_defconfig` and GitHub Actions kernel workflows. The kernel workflow passes; the repository does not record a hardware boot.

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the port and its state; it does not take over maintenance.
