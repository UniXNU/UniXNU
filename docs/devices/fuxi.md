# Xiaomi 13 (fuxi)

fuxi is the Xiaomi 13 with the SM8550 SoC. The repositories below are independent community ports. The UniXNU organization does not maintain them.

| Repository | Maintainer | State |
| --- | --- | --- |
| [UniXNU-fuxi](https://github.com/matejkoo217/UniXNU-fuxi) | [matejkoo217](https://github.com/matejkoo217) | Device repository, work in progress |
| [unixnu-fuxi](https://github.com/hanzi123-bilp/unixnu-fuxi), [uefi-fuxi](https://github.com/hanzi123-bilp/uefi-fuxi) | [hanzi123-bilp](https://github.com/hanzi123-bilp) | Stage A and stage B build inputs; no hardware run documented |

## UniXNU-fuxi

UniXNU-fuxi is a fork of UniXNU-sheng with fuxi board data. It targets the same iPad7,1 iPadOS 17.7.11 image and keeps the sheng kernel prelink. The fuxi UEFI package, prelink, kernel build, touch driver and defconfig are still in progress. The port notes are in `PORTING-FUXI.md`.

## hanzi123-bilp repositories

The `hanzi123-bilp` repositories are a separate device and firmware port. The device repository has a stage A minimal kernel that links before any prelink exists, and a stage B full configuration with 19 archives. The storage audit runs headers-only until live metadata exists. The firmware repository maps the SM8550 register apertures. No hardware run is documented.

## Maintenance

The maintainer named in the table owns the repository and its release decisions. UniXNU documentation lists the port and its state; it does not take over maintenance.
