# Supported devices

A device entry is a pair of repositories and the values that make the generic stack run on that board. The table records the ports with a public repository. Boards with a similar SoC need their own port and their own entry.

| Device | SoC | Support | Device repository | Firmware |
| --- | --- | --- | --- | --- |
| Xiaomi Pad 6S Pro (sheng) | SM8550 | Display, Touch, UFS, GPU | [UniXNU-sheng](https://github.com/UniXNU/UniXNU-sheng) | [uefi-sheng](https://github.com/UniXNU/uefi-sheng) |

## Community ports

The ports listed here are independent. Their maintainers own the repositories; the UniXNU organization does not maintain them.

| Device | SoC | State | Repository | Maintainer |
| --- | --- | --- | --- | --- |
| [Xiaomi 13 (fuxi)](/devices/fuxi) | SM8550 | UniXNU device repository, work in progress | [UniXNU-fuxi](https://github.com/matejkoo217/UniXNU-fuxi) | [matejkoo217](https://github.com/matejkoo217) |
| [Xiaomi Pad 7 / POCO Pad X1 (uke)](/devices/uke) | SM7675 | XNU entry reached, root device pending | [UniXNU-uke](https://github.com/Allenwdk/UniXNU-uke), [uefi-uke](https://github.com/Allenwdk/uefi-uke) | [Allenwdk](https://github.com/Allenwdk) |

See [Community ports](/devices/community) for the full list of ports found on GitHub.

## What a device page records

| Item | Example |
| --- | --- |
| Board identity | Product name, SoC, codename |
| IPSW | Product, version, build, device class, chip and board ID |
| Partition geometry | `first_lba`, `last_lba`, block size |
| Kernel prelink | Slide, roots, early security initializer, kernelcache pin |
| Firmware | Mu-Silicium config, DSC, firmware volume path, defines |
| Payload | Volume label, size, DRAM size, kernel arguments |
| ADT | Generator script, identity, CPU registers, PSCI method |
| Device tree additions | Reserved memory nodes for the stock bootloader |
| Build commands | The exact driver commands |
| Boot commands | The exact fastboot commands |
| Observed state | Which stages have run on the device |

## Adding a device

1. Follow [Porting](/porting/).
2. Create the device repository and the UEFI repository.
3. Build and bring up in stages.
4. Add a page under `docs/devices/` with the values and commands.
5. Add the device to the table above.

Device pages are the place for board specific values. The general guide uses placeholders and links here.

## sheng

The [sheng page](/devices/sheng) records the Xiaomi Pad 6S Pro port. It is one device entry. The [Novatek touch driver](/drivers/native-novatek-touch) uses the sheng touch driver as a worked example of a built-in XNU driver.
