# Xiaomi 13 (fuxi)

fuxi is the Xiaomi 13 with the SM8550 SoC. The projects below are independent community ports. The UniXNU organization does not maintain them.

| Repository | Maintainer | State |
| --- | --- | --- |
| [ios-fuxi](https://github.com/bangprovn/ios-fuxi) | [bangprovn](https://github.com/bangprovn) | iOS 16.7 userland on fuxi, CPU rendering, migrating to UniXNU |
| [UniXNU-fuxi](https://github.com/matejkoo217/UniXNU-fuxi) | [matejkoo217](https://github.com/matejkoo217) | UniXNU device repository fork, work in progress |

## ios-fuxi

ios-fuxi runs Apple's iOS 16 userland on fuxi. The kernel is xnu-8796. The root is a journaled HFS+ image stored as a pinned file inside Android userdata, and the loader reads it through an extent table.

| Area | State |
| --- | --- |
| Boot | Stock bootloader, temporary `fastboot boot` image |
| CPU | 7 of 8 cores, EPSS clock caps |
| Storage | Own UFS host driver, HFS+ root from userdata extents |
| Display | 1080x2400 panel, CPU CoreAnimation, framebuffer copy at 60 Hz |
| Touch | FTS controller over SPI |
| Buttons | Power and volume over PMK8550 |
| GPU | Loader bring-up only, no XNU GPU driver |
| Missing | Wi-Fi, Bluetooth, cellular, audio, camera, sensors, Face ID, GPU acceleration |

Boot the image with:

```sh
fastboot boot fuxi-xnu-boot.img
```

The host monitor is `tools/fuxi-xnu-monitor.py`. The project is temporary-boot only; keep backups of the critical partitions. The repository has the build steps.

## UniXNU-fuxi

UniXNU-fuxi is a fork of UniXNU-sheng with fuxi board data. It targets the same iPad7,1 iPadOS 17.7.11 image and keeps the sheng kernel prelink. The fuxi UEFI package, prelink, kernel build, touch driver and defconfig are still in progress. The port notes are in `PORTING-FUXI.md`.

## Maintenance

The maintainers named in the table own their repositories and their release decisions. UniXNU documentation lists the ports and their state; it does not take over maintenance.
