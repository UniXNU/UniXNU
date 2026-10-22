# Supported devices

A device entry is a pair of repositories and the values that make the generic stack run on that board. The table records the ports with a public repository. Boards with a similar SoC need their own port and their own entry.

| Device | SoC | Support | Device repository | Firmware |
| --- | --- | --- | --- | --- |
| Xiaomi Pad 6S Pro (sheng) | SM8550 | Display, Touch, UFS, GPU | [UniXNU-sheng](https://github.com/UniXNU/UniXNU-sheng) | [uefi-sheng](https://github.com/UniXNU/uefi-sheng) |

## Community ports

The ports listed here are independent. Their maintainers own the repositories; the UniXNU organization does not maintain them. Each entry has its own page. The table is ordered by completion, with the ports that reach userland or a full build chain first.

| Device | SoC | State | Maintainer |
| --- | --- | --- | --- |
| [DroidVM guest (crosvm on Gunyah)](/devices/droidvm) | crosvm-gunyah | iPadOS 17 home screen; CPU presentation; Metal widgets and icons; virtio-net works | Droid-VM |
| [QEMU virt](/devices/qemu) | QEMU virt | iPadOS 17 home screen and Settings; Metal on the Mac GPU with `--metal` | xVanTuring |
| [Lenovo Xiaoxin Pad 2022 (tb128fu)](/devices/tb128fu) | SM6225 | iPadOS 17 home screen with touch; Metal frames presented by the GPU; Adreno 610 runs | xVanTuring |
| [OnePlus 10 Pro 5G (negroni)](/devices/negroni) | SM8450 | iOS 16.7.16 SpringBoard with touch; CPU-rendered; Wi-Fi pending | pawlickerr |
| [Xiaomi 17 Pro (pandora)](/devices/pandora) | SM8850 | iOS 16.7.16 lock screen with touch and buttons; own loader, no UEFI chain | ShueiTsuki |
| [Xiaomi 13 (fuxi)](/devices/fuxi) | SM8550 | Kernel links and prelinks; stage B archive chain near complete; no hardware run | matejkoo217, hanzi123-bilp |
| [OnePlus 7 Pro (guacamole)](/devices/guacamole) | SM8150 | iOS 16.7.16 userland reached; GPU pending | wochgn |
| [OnePlus Ace 5 (giulia)](/devices/giulia) | SM8650 | Hello/Setup and GUI progress reached; touch and installation pending | jasper2863, tycykp |
| [Xiaomi Pad 7 / POCO Pad X1 (uke)](/devices/uke) | SM7675 | Root mounted and launchd starts; display surface pending | Allenwdk |
| [Xiaomi Pad 8 Pro (piano)](/devices/piano) | SM8750 | Kernel builds and prelinks in CI; not run on the tablet | code002-2 |
| [Xiaomi 13 Pro (nuwa)](/devices/nuwa) | SM8550 | Source kernel builds; platform archives and prelink pending | wh1stl3 |
| [OnePlus 13T (oneplus13t)](/devices/oneplus13t) | SM8750 | XNU S1 to S6 reached; root device search panics | IssacL04 |
| [OnePlus Pad 2 Pro (erhai)](/devices/erhai) | SM8750 | XNU entry bring-up; root and userland not configured | wally001012-cyber |
| [OPPO Find X7 Ultra (PHY120)](/devices/phy120) | SM8650 | Boot manager menu works; kernel builds in CI | peiyuesheng666 |
| [Redmi K40 Pro (haydn)](/devices/haydn) | SM8350 | Firmware, payload and boot image built; haydn4 imported from guacamole | xiaomi-haydn-dev |
| [Xiaomi Pad 5 (nabu)](/devices/nabu) | SM8150 | XNU executes; PMGR and userspace next | Lux12138 |
| [OnePlus 6T (fajita)](/devices/fajita) | SDM845 | XNU reaches root mount; no storage driver | johnpanos |
| [Microsoft Surface Duo 2 (zeta)](/devices/zeta) | SM8350 | UEFI, menu and payload work; kernel builds, not booted | none24smu |
| [OnePlus Ace 5 Pro (hummer)](/devices/hummer) | SM8750 | UEFI layer works; XNU CI trial | 2426120557 |
| [Xiaomi 15 (dada)](/devices/dada) | SM8750 | UEFI firmware works; UniXNU and XNU not run | 7Night-kqx |
| [Redmi Note 14 Pro+ 5G (amethyst)](/devices/amethyst) | SM7635 | Board file targets iPhone10,3; no hardware run documented | andr0d1v |
| [Redmi K70 (vermeer)](/devices/vermeer) | SM8550 | Source build baseline and sheng-derived device repository | mansar1337, yyx2025 |
| [Nubia RedMagic 8 Pro / 8 Pro+ (nx729j)](/devices/nx729j) | SM8550 | Board files ported from sheng; runtime not documented | 2713385115 |
| [Xiaomi Pad 6 (pipa)](/devices/pipa) | SM8250 | Board and userdata values measured; not run on the tablet | xVanTuring |
| [Galaxy Tab A7 10.4 (gta4l)](/devices/gta4l) | SM6115 | Board, ADT and firmware build; second repository builds a kernel in CI | NoNameBuilder, ilovemykedi |
| [Redmi Note 10 Pro (sweet)](/devices/sweet) | SM7150 | Platform and loader bring-up; no bootable image | dipa-studio |
| [OnePlus 5 (cheeseburger)](/devices/cheeseburger) | MSM8998 | XNU entry bar observed; MMU and root unverified | DinnerABC |
| [Redmi K20 Pro / Mi 9T Pro (raphael)](/devices/raphael) | SM8150 | New repository; kernel build not passing | penYo22 |
| [Galaxy Z Fold3 (q2q)](/devices/q2q) | SM8350 | Source kernel build harness only | agcarbajo |
| [Redmi K30 5G (picasso)](/devices/picasso) | SM7250 | Early skeleton; firmware not built | YinCQL |
| [Redmi 9A (dandelion)](/devices/dandelion) | MT6765 | Early bring-up; UEFI port in progress | licg89 |
| [Xiaomi Mi 6 (sagit)](/devices/sagit) | MSM8998 | Device repository; status not documented | dmnakzkahziamnk-a11y |

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
