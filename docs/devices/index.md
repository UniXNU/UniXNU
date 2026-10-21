# Supported devices

A device entry is a pair of repositories and the values that make the generic stack run on that board. The table records the ports with a public repository. Boards with a similar SoC need their own port and their own entry.

| Device | SoC | Support | Device repository | Firmware |
| --- | --- | --- | --- | --- |
| Xiaomi Pad 6S Pro (sheng) | SM8550 | Display, Touch, UFS, GPU | [UniXNU-sheng](https://github.com/UniXNU/UniXNU-sheng) | [uefi-sheng](https://github.com/UniXNU/uefi-sheng) |

## Community ports

The ports listed here are independent. Their maintainers own the repositories; the UniXNU organization does not maintain them. Each entry has its own page.

| Device | SoC | State | Maintainer |
| --- | --- | --- | --- |
| [Xiaomi 13 (fuxi)](/devices/fuxi) | SM8550 | Device repositories, work in progress | matejkoo217, hanzi123-bilp |
| [Xiaomi Pad 7 / POCO Pad X1 (uke)](/devices/uke) | SM7675 | XNU entry reached; root device pending | Allenwdk |
| [Redmi Note 10 Pro (sweet)](/devices/sweet) | SM7150 | Platform and loader bring-up; no bootable image | dipa-studio |
| [OnePlus Ace 5 Pro (hummer)](/devices/hummer) | SM8750 | UEFI layer works; XNU CI trial | 2426120557 |
| [Xiaomi Mi 6 (sagit)](/devices/sagit) | MSM8998 | Device repository; status not documented | dmnakzkahziamnk-a11y |
| [Xiaomi Pad 8 Pro (piano)](/devices/piano) | SM8750 | Kernel builds and prelinks in CI; not run on the tablet | code002-2 |
| [Redmi Note 14 Pro+ 5G (amethyst)](/devices/amethyst) | SM7635 | Work in progress; status not documented | andr0d1v |
| [Redmi K70 (vermeer)](/devices/vermeer) | SM8550 | Source build baseline and sheng-derived device repository | mansar1337, yyx2025 |
| [DroidVM guest (crosvm on Gunyah)](/devices/droidvm) | crosvm-gunyah | iPadOS 17 lock screen and home screen; CPU-rendered | Droid-VM |
| [QEMU virt](/devices/qemu) | QEMU virt | iPadOS 17 home screen and Settings; CPU-rendered | xVanTuring |
| [Redmi 9A (dandelion)](/devices/dandelion) | MT6765 | Early bring-up; UEFI port in progress | licg89 |
| [Galaxy Z Fold3 (q2q)](/devices/q2q) | SM8350 | Source kernel build harness only | agcarbajo |
| [Xiaomi 15 (dada)](/devices/dada) | SM8750 | UEFI firmware works; UniXNU and XNU not run | 7Night-kqx |
| [Xiaomi Pad 6 (pipa)](/devices/pipa) | SM8250 | Prepared without the tablet | xVanTuring |
| [Redmi K40 Pro (haydn)](/devices/haydn) | SM8350 | Firmware, payload and boot image built; not run on hardware | xiaomi-haydn-dev |
| [Xiaomi Pad 5 (nabu)](/devices/nabu) | SM8150 | XNU executes; PMGR and userspace next | Lux12138 |
| [Galaxy Tab A7 10.4 (gta4l)](/devices/gta4l) | SM6115 | Board, ADT and firmware build; kernel not built | NoNameBuilder |
| [OnePlus 13T (oneplus13t)](/devices/oneplus13t) | SM8750 | UEFI menu and DarwinBoot handoff; no XNU entry | IssacL04 |

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
