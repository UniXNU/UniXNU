# OnePlus 7 Pro (guacamole)

guacamole is the OnePlus 7 Pro (GM1910) with the SM8150 SoC. The port below is an independent community project. The UniXNU organization does not maintain it. The kernel and root file system come from the ios-sweet guacamole work; UniXNU and DarwinBoot provide the boot chain.

| Repository | Maintainer | State |
| --- | --- | --- |
| [UniXNU-guacamole](https://github.com/wochgn/UniXNU-guacamole) | [wochgn](https://github.com/wochgn) | iOS 16.7.16 userland reached on hardware |

## State

| Stage | State |
| --- | --- |
| UEFI firmware and UniXNU menu | works; the menu lists `OnePlus 7 Pro - XNU` |
| Payload volume | the 64 MiB `GUACESP` FAT32 volume is mounted and read |
| DarwinBoot | validates `kernel.macho` and `.adt` and hands off |
| XNU and iOS userland | r15 reaches the iOS userland on the panel |
| GPU and GMU | blocked in the ios-sweet tree |

The r15 image requests a 3 GiB Darwin window and reaches the iOS userland. `fastboot boot` is temporary and leaves Android and every partition unchanged.

## Build

The build needs the ios-sweet kernel and ADT, a UniXNU checkout at `b6ae99c`, and a Project Aloha checkout at `0b798128`. Apply the three patches listed in the repository. Then:

```sh
python3 scripts/build-firmware.py
python3 scripts/build-payload.py
python3 scripts/build-bootimg.py \
  --fd uefi/Build/SurfaceDuo1Pkg/DEBUG_CLANGPDB/FV/SM8150_EFI.fd \
  --dtb inputs/uefi-prebuilt/guacamole.dtb \
  -o out/guacamole/boot/boot-32-r15.img
```

Boot:

```sh
fastboot boot out/guacamole/boot/boot-32-r15.img
```

The kernel, ADT, DTB and firmware volume are external inputs and are not stored in the repository.

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the port and its state; it does not take over maintenance.
