# Community repository index

This page lists public UniXNU repositories that do not have a separate device page yet. A repository here is listed for completeness; its state is recorded only when the repository documents one.

## Device ports

| Device | SoC | Repository | State |
| --- | --- | --- | --- |
| Google Pixel 9 Pro XL (komodo) | Tensor G4 | [UniXNU-komodo](https://github.com/Trijal08/UniXNU-komodo) | board, defconfig and ADT; UEFI is separate; no hardware run |
| Sony Xperia 1 II (pdx203) | SM8250 | [UniXNU-pdx203](https://github.com/chardidathing/UniXNU-pdx203) | kernel builds and prelinks in CI; not booted |
| Xiaomi Mi 9 (cepheus) | SDM855 | [UniXNU-cepheus](https://github.com/sxl47/UniXNU-cepheus) | device repository and boot chain prepared; no hardware result documented |
| Xiaomi MIX 2 (chiron) | SDM835 | [ios-party](https://github.com/to-mid/ios-party) | minimal 4 KiB XNU and PID 1 heartbeat on hardware; no full iOS userland |
| Xiaomi MIX Flip (ruyi) | SM8650 | [UniXNU-ruyi-min](https://github.com/ArnoDorian123/UniXNU-ruyi-min) | board and defconfig; no README or hardware result |
| Xiaomi Civi 5 Pro (luming) | SM8735 | [UniXNU-luming](https://github.com/infinityEX-RSXQ/-UniXNU-luming) | pre-build skeleton; static checks pass; no build or boot |
| Xiaomi Pad 6 Pro (liuqin) | SM8475 | [UniXNU-liuqin](https://github.com/1696108518/UniXNU-liuqin) | board, defconfig and kernel USB debug port; UEFI next |
| Xiaomi Pad 5 Pro 5G (enuma) | SM8250-AC | [UniXNU-enuma](https://github.com/wh1stl3/UniXNU-enuma), [UniXNU-enuma](https://github.com/Tlrenhb/UniXNU-enuma) | device repositories; UEFI and a bootable image are missing |
| Redmi Turbo 3 / Poco F6 (peridot) | SM8635 | [UniXNU-peridot](https://github.com/kvfsrl/UniXNU-peridot), [UniXNU-peridot-standalone](https://github.com/hoshikv/UniXNU-peridot-standalone) | WIP device repositories; PR #52 |
| OnePlus 8 Pro (instantnoodlep) | SM8250 | [UniXNU-instantnoodlep](https://github.com/zhangp996/UniXNU-instantnoodlep) | UEFI platform and kernel baseline; status not documented |
| OnePlus 8T (kebab) | SM8250 | [UniXNU-kebab](https://github.com/GFander/UniXNU-kebab) | first milestone: kernel.macho only |
| OnePlus 6 (enchilada) | SDM845 | [UniXNU-enchilada](https://github.com/keyfan/UniXNU-enchilada) | device repository; status not documented |
| OnePlus 15T (fairlady) | SM8850 | [UniXNU-fairlady](https://github.com/Osilvfe/UniXNU-fairlady) | early port with S1 to S6 diagnostics; no hardware result documented |
| OnePlus Pad Pro (caihong) | SM8650 | [UniXNU-caihong](https://github.com/Axiang-dev/UniXNU-caihong) | board and defconfig; UEFI integration not done |
| Nothing Phone (3a) (asteroids) | SM7635 | [UniXNU-asteroids](https://github.com/rootstockos/UniXNU-asteroids) | UEFI reaches DXE and BDS; UniXNU and XNU not reached |
| Brave Ark tablet (braveark) | SM8635 | [UniXNU-braveark](https://github.com/tattwamashi/UniXNU-braveark) | UEFI, menu, payload, DarwinBoot and XNU BSD init on 8 CPUs; root in progress |
| Galaxy Tab S9 Ultra Wi-Fi (gts9uwifi) | SM-X910 | [UniXNU-gts9uwifi](https://github.com/zc47796741-pixel/UniXNU-gts9uwifi) | device repository; status not documented |
| Moto Z2 Force (nash) | MSM8998 | [UniXNU-nash](https://github.com/fcxuhaq3/UniXNU-nash) | UEFI, UniXNU and payload passed on hardware; XNU stage needs macOS |
| Moto G9 Play (guamp) | SM6115 | [UniXNU-guamp](https://github.com/itsChris122/UniXNU-guamp) | UEFI menu boots; kernel not built |
| Moto G 5G (gauguin) | SM7125 | [UniXNU-gauguin](https://github.com/lvyufeng/UniXNU-gauguin) | device repository; status not documented |
| Microsoft Lumia 950 | MSM8992 | [UniXNU-lumia950](https://github.com/ManGuy-Legend/UniXNU-lumia950) | device repository; uses the phone's own UEFI; no boot |
| OPPO R11 (r11) | SDM660 | [unixnu-r11](https://github.com/huhaitao1136-cpu/unixnu-r11) | board, defconfig and hardware notes; status not documented |
| OPPO Find X9 (x9) | MT6993 | [unixnu_x9](https://github.com/tosasitill/unixnu_x9) | UEFI not reached; about 25 to 30 percent |

## Related and alternate repositories

| Device or project | Repository | Note |
| --- | --- | --- |
| Xiaomi 13 (fuxi) | [unixnu-fuxi](https://github.com/Xyvern08371/unixnu-fuxi) | alternate fuxi repository |
| Redmi Note 10 Pro (sweet) | [UniXNU-sweet](https://github.com/CrackerCat/UniXNU-sweet) | alternate sweet repository |
| OnePlus 5 (cheeseburger) | [UniXNU-cheeseburger](https://github.com/lss717/UniXNU-cheeseburger) | alternate cheeseburger repository |
| Xiaomi 10 Ultra (cas) | [UniXNU-cas](https://github.com/pxl777806/UniXNU-cas) | alternate cas repository |
| Xiaomi Pad 5 (nabu) | [unixnu-nabu](https://github.com/zzc775/unixnu-nabu), [unixnu-nabu-build](https://github.com/3214791900-del/unixnu-nabu-build), [uefi-nabu-build](https://github.com/3214791900-del/uefi-nabu-build) | alternate and build repositories |
| QEMU virt for vermeer | [UniXNU-qemu](https://github.com/yyx2025/UniXNU-qemu) | QEMU virt repository used for vermeer bring-up |
| Redmi K70 (vermeer) | [k70-unixnu-build](https://github.com/wuan0039/k70-unixnu-build), [k70-unixnu-build-20261022](https://github.com/xyyyds0106/k70-unixnu-build-20261022) | kernel CI and pinned build repositories |
| Unisoc devices | [UniXNU-Unisoc](https://github.com/hxzbaka/UniXNU-Unisoc) | core fork for Unisoc devices; no device-specific port yet |
| Xiaomi Pad 6S Pro (sheng) | [macOS-ForSheng](https://github.com/Jelly10086/macOS-ForSheng) | macOS 27 bring-up based on UniXNU and Snapintosh; not an iOS device port |
| Unclassified build tree | [unixnu-build](https://github.com/iskssksjjsjjzjs/unixnu-build) | build tree only; device not documented |

## Maintenance

Each maintainer owns their repository and release decisions. This index records public repositories and the state their documentation reports; it does not take over maintenance.
