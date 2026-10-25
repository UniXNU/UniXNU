# Devices

A device entry is a pair of repositories and the values that make the generic stack run on that board. The table records the ports with a public repository. Boards with a similar SoC need their own port and their own entry.

## Select and use a device

1. Open the target device below and confirm its product, SoC and maintained repositories.
2. Read its inputs, current results and unfinished areas. Use the firmware, OS profile and partition values specified by that port.
3. Follow [Build and boot](/building) to build it, [Port a device](/porting/steps) to adapt new hardware, or [Migration](/porting/migration) to update the repository format.
4. Verify the checkpoints in its record and save the source, firmware and image revisions actually used.

## Organization-maintained devices

| Device | SoC | Support | Device repository | Firmware |
| --- | --- | --- | --- | --- |
| [Xiaomi Pad 6S Pro (sheng)](/devices/sheng) | SM8550 | [Implementation and evidence by area](/devices/sheng) | [UniXNU-sheng](https://github.com/UniXNU/UniXNU-sheng) | [uefi-sheng](https://github.com/UniXNU/uefi-sheng) |

## Community ports

Community ports are maintained by the people listed below. Each page distinguishes source, host-build and device results and links their records. Discovery covers the UniXNU organization, the `unixnu` topic, public repositories matching UniXNU in name or description, and existing source links. Entries require target-specific board configuration or implementation.

| Device | SoC | State | Maintainer |
| --- | --- | --- | --- |
| [DroidVM guest (crosvm on Gunyah)](/devices/droidvm) | crosvm-gunyah | iPadOS 17 home screen; Metal widgets and icons; keychain and Bluetooth; virtio-net works | Droid-VM |
| [QEMU virt](/devices/qemu) | QEMU virt | iPadOS 17 home screen and Settings; Metal on the Mac GPU with `--metal` | xVanTuring |
| [Lenovo Xiaoxin Pad 2022 (tb128fu)](/devices/tb128fu) | SM6225 | iPadOS 17 home screen with touch; Metal frames presented by the GPU; Adreno 610 runs | xVanTuring |
| [Galaxy Tab S7 FE Wi-Fi (SM-T733)](/devices/sm-t733) | SM7325 | Desktop, touch, UFS, persistent Data and battery reporting | RigoLigoRLC |
| [OnePlus 10 Pro 5G (negroni)](/devices/negroni) | SM8450 | iOS 16.7.16 SpringBoard with touch; CPU-rendered; Wi-Fi pending | pawlickerr |
| [Nothing Phone (2) (pong)](/devices/pong) | SM8475 | iOS 16.6.1 home screen with display and touch; UFS and GPU partial | Chengdong-Yu |
| [Xiaomi 17 Pro (pandora)](/devices/pandora) | SM8850 | Home screen and touch; first GPU frame, interaction hangs | ShueiTsuki |
| [Xiaomi Mi 8 SE (sirius)](/devices/sirius) | SDM710 | XNU entry and platform expert via U-Boot UEFI; IOKit in progress | 57UU |
| [Xiaomi 13 (fuxi)](/devices/fuxi) | SM8550 | Kernel links and prelinks; stage B archive chain near complete; no hardware run | matejkoo217, hanzi123-bilp |
| [Xiaomi 13 Ultra (ishtar)](/devices/ishtar) | SM8550 | Kernel, payload and boot image all build on the host; stage diagnostics ready; no hardware run yet | peter8889 |
| [OnePlus 7 Pro (guacamole)](/devices/guacamole) | SM8150 | iOS 16.7.16 userland reached; GPU pending | wochgn |
| [OnePlus Ace 5 (giulia)](/devices/giulia) | SM8650 | Hello/Setup, display, touch and keys; GPU, Wi-Fi and audio pending | tycykp |
| [Xiaomi Mi 10 (umi)](/devices/umi) | SM8250 | iPadOS 17.7.11 Hello/Setup with touch; CPU display, UFS and persistent Data | reAAAq |
| [Xiaomi MIX 2 (chiron)](/devices/chiron) | SDM835 | Minimal 4 KiB XNU and PID 1 heartbeat on hardware | to-mid |
| [Xiaomi Pad 7 / POCO Pad X1 (uke)](/devices/uke) | SM7675 | Apple logo and early userland; reboot under investigation | Allenwdk |
| [POCO X7 / Redmi Note 14 Pro 5G (malachite)](/devices/malachite) | MT6878 | UEFI works, UFS works, XNU rootfs loaded; USB, touch and the rest not implemented | ghidgdsr |
| [Brave Ark tablet (braveark)](/devices/braveark) | SM8635 | XNU BSD init on 8 CPUs; iPadOS root in progress | tattwamashi |
| [Xiaomi Pad 8 Pro (piano)](/devices/piano) | SM8750 | Kernel builds and prelinks in CI; not run on the tablet | code002-2 |
| [Xiaomi 13 Pro (nuwa)](/devices/nuwa) | SM8550 | Hardware XNU output through IODTNVRAM; reboot under investigation | wh1stl3 |
| [OnePlus 13T (oneplus13t)](/devices/oneplus13t) | SM8750 | Root and system UI on hardware; touch pending | IssacL04 |
| [OnePlus Pad 2 Pro (erhai)](/devices/erhai) | SM8750 | XNU entry bring-up; root and userland not configured | wally001012-cyber |
| [OPPO Find X7 Ultra (PHY120)](/devices/phy120) | SM8650 | Boot manager menu works; kernel builds in CI | peiyuesheng666 |
| [Sony Xperia 1 II (pdx203)](/devices/pdx203) | SM8250 | Kernel builds and prelinks in CI; not booted | chardidathing |
| [Moto Z2 Force (nash)](/devices/nash) | MSM8998 | Board configuration and early ARM patches; target hardware evidence pending | fcxuhaq3 |
| [Redmi K40 Pro (haydn)](/devices/haydn) | SM8350 | Firmware, payload and boot image built; haydn4 imported from guacamole | xiaomi-haydn-dev |
| [Xiaomi Pad 5 (nabu)](/devices/nabu) | SM8150 | launchd exec returns ENOENT; Linux kernel builds | Lux12138 |
| [OnePlus 6T (fajita)](/devices/fajita) | SDM845 | XNU reaches root mount; no storage driver | johnpanos |
| [Xiaomi Mi 8 (dipper)](/devices/dipper) | SDM845 | UEFI, menu and payload; XNU reaches BSD init, no root | hanyaa380 |
| [Microsoft Surface Duo 2 (zeta)](/devices/zeta) | SM8350 | APFS root and rewritten PID 1; shared-cache pointer fault | none24smu |
| [OnePlus Ace 5 Pro (hummer)](/devices/hummer) | SM8750 | Six CPUs and panel checkpoints; root-device wait | 2426120557 |
| [Xiaomi 10 Ultra (cas)](/devices/cas) | SM8250 | UEFI and UniXNU menu verified; DarwinBoot and XNU not tested | ht94911 |
| [Xiaomi 15 (dada)](/devices/dada) | SM8750 | UEFI works; UFS UIC and MCQ probes; UniXNU and XNU not run | 7Night-kqx |
| [Redmi Note 14 Pro+ 5G (amethyst)](/devices/amethyst) | SM7635 | Board and kernel config with legacy display; no hardware run documented | andr0d1v |
| [Redmi K90 Pro Max / Poco F8 Ultra (myron)](/devices/myron) | SM8850 | Core and driver forks; device repository and hardware result pending | zg7681 |
| [Redmi K70 (vermeer)](/devices/vermeer) | SM8550 | Platform kernel CI passes; hardware UEFI menu verified | mansar1337, yyx2025, wuan0039, xyyyds0106 |
| [Nubia RedMagic 8 Pro / 8 Pro+ (nx729j)](/devices/nx729j) | SM8550 | NativeUfs and SMMU group in the device repository; runtime not documented | 2713385115 |
| [Xiaomi Pad 6 (pipa)](/devices/pipa) | SM8250 | Hardware XNU boot; root mount fails, storage integration pending | xVanTuring |
| [Galaxy Tab A7 10.4 (gta4l)](/devices/gta4l) | SM6115 | Board, ADT and firmware build; second repository builds a kernel in CI | NoNameBuilder, ilovemykedi |
| [Redmi Note 10 Pro (sweet)](/devices/sweet) | SM7150 | Kernel and platform builds; QEMU CPU/timer checks; device integration pending | CrackerCat |
| [Xiaomi Mi MIX 2S (polaris)](/devices/polaris) | SDM845 | Platform stage verified on hardware: firmware, UniXNU, DarwinBoot and the source kernel through BSD/IOKit; no root yet | luuu20309 |
| [OnePlus 5 (cheeseburger)](/devices/cheeseburger) | MSM8998 | Root, PID 1 and RAM Data; watchdogd SIGTRAP under investigation | DinnerABC, lss717 |
| [Redmi K20 Pro / Mi 9T Pro (raphael)](/devices/raphael) | SM8150 | Public source access pending; current build and device state unconfirmed | penYo22 |
| [Galaxy Z Fold3 (q2q)](/devices/q2q) | SM8350 | Source kernel build harness only | agcarbajo |
| [Redmi K30 5G (picasso)](/devices/picasso) | SM7250 | UEFI and XNU boot; root and GPU pending | YinCQL |
| [Redmi Note 9 (merlinx)](/devices/merlinx) | MT6768 | UEFI boots and custom menu works; storage init blocks UniXNU and XNU | Dracen-W |
| [Xiaomi Mi Pad 4 LTE (clover)](/devices/clover) | SDM660 | mockfs RAM root and EL0 test init; process diagnostics in progress | qine233 |
| [Benesse TAB-A04-BR3 (a04br3)](/devices/a04br3) | MT8167 | Board, firmware, eMMC and GPT prepared; no hardware run | mouseos |
| [Redmi 9A (dandelion)](/devices/dandelion) | MT6765 | Early bring-up; UEFI port in progress | licg89 |
| [Xiaomi Mi 6 (sagit)](/devices/sagit) | MSM8998 | Public source access pending; current build and device state unconfirmed | dmnakzkahziamnk-a11y |
| [Redmi Note 12 Turbo / POCO F5 (marble)](/devices/marble) | SM7475 | Public source access pending; current build and device state unconfirmed | Enmmmmn |
| [Xiaomi Mi 10S (thyme)](/devices/thyme) | SM8250-AC | Measured board inputs and early traces; hardware boot evidence pending | tobyfox1640, Coryyi |
| [Redmi K80 Ultra (dali)](/devices/dali) | MT6991 | Single-core XNU early boot; root and userland out of scope | localhosts-A |
| [ZTE Nubia Z60 Ultra (nx721j)](/devices/nx721j) | Pineapple | Pineapple kernel and passive UFS probe; device boot pending | SangLuoCN |
| [Unisoc UMS512 / T610YP](/devices/t610yp) | UMS512 | Board, kernel config and ADT; no hardware result | hxzbaka |
| [Google Pixel 9 Pro XL (komodo)](/devices/komodo) | Tensor G4 | Menu and borrowed-kernel entry probes on hardware; native platform pending | Trijal08 |
| [Xiaomi Mi 9 (cepheus)](/devices/cepheus) | SDM855 | Device repository and boot chain prepared; no hardware result | sxl47 |
| [Xiaomi MIX Flip (ruyi)](/devices/ruyi) | SM8650 | Board, kernel configuration and firmware repository; hardware results pending | ArnoDorian123 |
| [Xiaomi Civi 5 Pro (luming)](/devices/luming) | SM8735 | Measured inputs and host ADT checks; kernel and firmware builds pending | infinityEX-RSXQ |
| [Xiaomi Pad 6 Pro (liuqin)](/devices/liuqin) | SM8475 | Board, defconfig and kernel USB debug port; UEFI next | 1696108518 |
| [Xiaomi Pad 5 Pro 5G (enuma)](/devices/enuma) | SM8250-AC | Prelink, ADT and FAT payload pass host checks; device boot pending | wh1stl3, Tlrenhb |
| [Redmi Turbo 3 / Poco F6 (peridot)](/devices/peridot) | SM8635 | WIP device repositories; no hardware result | kvfsrl, hoshikv |
| [OnePlus 8 Pro (instantnoodlep)](/devices/instantnoodlep) | SM8250 | UEFI platform and kernel baseline; status not documented | zhangp996 |
| [OnePlus 8T (kebab)](/devices/kebab) | SM8250 | XNU platform and early console; mapping and timer issues | GFander |
| [OnePlus 6 (enchilada)](/devices/enchilada) | SDM845 | Device repository; status not documented | keyfan |
| [OnePlus 15T (fairlady)](/devices/fairlady) | SM8850 | Early port with S1 to S6 diagnostics; no hardware result | Osilvfe |
| [OnePlus Pad Pro (caihong)](/devices/caihong) | SM8650 | APFS restore RAM root and launchd; display and full system root pending | Axiang-dev |
| [Nothing Phone (3a) (asteroids)](/devices/asteroids) | SM7635 | Eight CPUs, UFS root and userland; display presentation pending | rootstockos |
| [Galaxy Tab S9 Ultra Wi-Fi (gts9uwifi)](/devices/gts9uwifi) | SM-X910 | Device repository; status not documented | zc47796741-pixel |
| [Moto G9 Play (guamp)](/devices/guamp) | SM6115 | UEFI menu boots; kernel not built | itsChris122 |
| [Moto G 5G (gauguin)](/devices/gauguin) | SM7125 | Device repository; status not documented | lvyufeng |
| [Microsoft Lumia 950](/devices/lumia950) | MSM8992 | Device repository; uses the phone's own UEFI; no boot | ManGuy-Legend |
| [OPPO R11 (r11)](/devices/r11) | SDM660 | Board, defconfig and hardware notes; status not documented | huhaitao1136-cpu |
| [OPPO Find X9 (x9)](/devices/x9) | MT6993 | UEFI not reached; about 25 to 30 percent | tosasitill |
| [Unisoc devices](/devices/unisoc) | Unisoc | Core fork; no device-specific port yet | hxzbaka |
| [unixnu-build](/devices/unixnu-build) | build tree | Build tree only; device not documented | iskssksjjsjjzjs |
| [macOS on sheng](/devices/sheng-macos) | SM8550 | macOS 26.5 userland in QEMU; sheng UEFI EL1 probe | Jelly10086 |
| [Redmi K40 (alioth)](/devices/alioth) | SM8250-AC | Format 2 board, DTS and SM8250 shared support; kernel and image integration pending | FFT-infra |
| [Lenovo Xiaoxin Pad Pro 2021 (j716f)](/devices/j716f) | SM8250 | Hardware menu, keys, RAM FAT and DarwinBoot protocol checks; XNU entry pending | Denis0x00 |
| [Lenovo Legion Y700 Gen 4 (elden)](/devices/elden) | SM8750P | Two RAM boots verify menu, GOP, keys and FAT; XNU image pending | jerry-2009 |
| [Xiaomi Pad 5 Pro Wi-Fi (elish)](/devices/elish) | SM8250-AC | Board scaffold passes static checks; measured inputs and firmware pending | hpadmx |
| [Redmi K80 (zorn)](/devices/zorn) | SM8650-AB | XNU and APFS restore RAM root; launchd loading stops at PARSE | kerrinz |
| [OnePlus 9R (lemonades)](/devices/lemonades) | SM8250-AC | Firmware builds on Linux; board and payload preparation; hardware checks pending | soooink |
| [Meizu 20 Classic (m2381)](/devices/m2381) | SM8550 | Device configuration and firmware overlay; kernel/prelink bring-up | RiverKawa271828 |

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

1. Follow [Porting](/porting/steps).
2. Create the device repository and the UEFI repository.
3. Build and bring up in stages.
4. Add a page under `docs/devices/` with the values and commands.
5. Add the device to the table above.

Device pages are the place for board specific values. The general guide uses placeholders and links here.

## sheng

The [sheng page](/devices/sheng) records the Xiaomi Pad 6S Pro port. It is one device entry. The [Novatek touch driver](/drivers/sheng-novatek-touch) uses the sheng touch driver as a worked example of a built-in XNU driver.

Official device pages render each repository's `porting.toml`. See the [record workflow](/porting/records).
