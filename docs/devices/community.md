# Community ports

These ports are independent. Their maintainers own the repositories; the UniXNU organization does not maintain them. The state comes from each repository's README on 2026-10-22. A repository without a documented state is marked as such.

| Device | SoC | State | Repository | Maintainer |
| --- | --- | --- | --- | --- |
| [Xiaomi 13 (fuxi)](/devices/fuxi) | SM8550 | Device repository, work in progress | [UniXNU-fuxi](https://github.com/matejkoo217/UniXNU-fuxi) | [matejkoo217](https://github.com/matejkoo217) |
| [Xiaomi 13 (fuxi)](/devices/fuxi) | SM8550 | Device and firmware repositories, status not documented | [unixnu-fuxi](https://github.com/hanzi123-bilp/unixnu-fuxi), [uefi-fuxi](https://github.com/hanzi123-bilp/uefi-fuxi) | [hanzi123-bilp](https://github.com/hanzi123-bilp) |
| Redmi Note 10 Pro (sweet) | SM7150 | Platform and loader bring-up; no bootable image | [UniXNU-sweet](https://github.com/dipa-studio/UniXNU-sweet) | [dipa-studio](https://github.com/dipa-studio) |
| OnePlus Ace 5 Pro (hummer) | SM8750 | UEFI layer works; XNU CI trial; GPU and persistent Data not started | [UniXNU-hummer](https://github.com/2426120557/UniXNU-hummer) | [2426120557](https://github.com/2426120557) |
| Xiaomi Mi 6 (sagit) | MSM8998 | Device repository, status not documented | [UniXNU-sagit](https://github.com/dmnakzkahziamnk-a11y/UniXNU-sagit) | [dmnakzkahziamnk-a11y](https://github.com/dmnakzkahziamnk-a11y) |
| Xiaomi Pad 8 Pro (piano) | SM8750 | Kernel builds and prelinks in CI; not run on the tablet | [UniXNU-piano](https://github.com/code002-2/UniXNU-piano) | [code002-2](https://github.com/code002-2) |
| Redmi Note 14 Pro+ 5G (amethyst) | SM7635 | Work in progress; status not documented | [UniXNU-amethyst](https://github.com/andr0d1v/UniXNU-amethyst) | [andr0d1v](https://github.com/andr0d1v) |
| Redmi K70 (vermeer) | SM8550 | Source XNU build baseline, not a boot image | [UniXNU-vermeer](https://github.com/mansar1337/UniXNU-vermeer) | [mansar1337](https://github.com/mansar1337) |
| Redmi K70 (vermeer) | SM8550 | Device repository ported from sheng; status not documented | [UniXNU-vermeer](https://github.com/yyx2025/UniXNU-vermeer) | [yyx2025](https://github.com/yyx2025) |
| DroidVM guest (crosvm on Gunyah) | crosvm-gunyah | iPadOS 17 lock screen and home screen; CPU-rendered; persistent Data on SM8650 | [UniXNU-droidvm](https://github.com/Droid-VM/UniXNU-droidvm) | [Droid-VM](https://github.com/Droid-VM) |
| QEMU virt | QEMU virt | iPadOS 17 home screen and Settings; CPU-rendered; no GPU | [UniXNU-qemu](https://github.com/xVanTuring/UniXNU-qemu) | [xVanTuring](https://github.com/xVanTuring) |
| Redmi 9A (dandelion) | MT6765 | Early bring-up; direct boot fails; UEFI port in progress; no UART | [UniXNU-dandelion](https://github.com/licg89/UniXNU-dandelion) | [licg89](https://github.com/licg89) |
| Galaxy Z Fold3 (q2q) | SM8350 | Source kernel build harness only; cannot boot userspace | [UniXNU-q2q](https://github.com/agcarbajo/UniXNU-q2q) | [agcarbajo](https://github.com/agcarbajo) |
| Xiaomi 15 (dada) | SM8750 | UEFI firmware works; UniXNU menu and DarwinBoot not run on hardware | [UniXNU-dada](https://github.com/7Night-kqx/UniXNU-dada) | [7Night-kqx](https://github.com/7Night-kqx) |
| Xiaomi Pad 6 (pipa) | SM8250 | Prepared without the tablet; not run on hardware | [UniXNU-pipa](https://github.com/xVanTuring/UniXNU-pipa), [uefi-pipa](https://github.com/xVanTuring/uefi-pipa) | [xVanTuring](https://github.com/xVanTuring) |
| Redmi K40 Pro (haydn) | SM8350 | Device repo and UEFI plan; firmware, payload and boot image built; not run on hardware | [UniXNU-haydn](https://github.com/xiaomi-haydn-dev/UniXNU-haydn) | [xiaomi-haydn-dev](https://github.com/xiaomi-haydn-dev) |
| [Xiaomi Pad 7 / POCO Pad X1 (uke)](/devices/uke) | SM7675 | XNU entry reached; root device pending | [UniXNU-uke](https://github.com/Allenwdk/UniXNU-uke), [uefi-uke](https://github.com/Allenwdk/uefi-uke) | [Allenwdk](https://github.com/Allenwdk) |
| Xiaomi Pad 5 (nabu) | SM8150 | XNU executes; PMGR and userspace next | [unixnu-nabu](https://github.com/Lux12138/unixnu-nabu) | [Lux12138](https://github.com/Lux12138) |
| Galaxy Tab A7 10.4 (gta4l) | SM6115 | Board, ADT and firmware build; kernel not built; hardware boot not demonstrated | [UniXNU-gta4l](https://github.com/NoNameBuilder/UniXNU-gta4l) | [NoNameBuilder](https://github.com/NoNameBuilder) |
| OnePlus 13T (oneplus13t) | SM8750 | UEFI Shell and menu; XNU build and payload; DarwinBoot handoff; XNU entry not yet | [UniXNU-oneplus13t](https://github.com/IssacL04/UniXNU-oneplus13t) | [IssacL04](https://github.com/IssacL04) |

`BigfootACA/unixnu-droidvm-ci` provides CI builds for the QEMU/KVM and DroidVM targets.
