# Xiaomi Mi 10 — iOS 16 (qcom-toolbox)

A separate Mi 10 (`umi`, SM8250) port that boots the **unmodified iOS 16.7.16
(20H392) userland of the iPhone X** on a patched XNU (xnu-8796). It is a
different line of work from the [iPadOS 17 umi port](/devices/umi) and the
other [umi sources](/devices/models/umi); the two do not share kernels, boot
paths or root images.

| Source | Contents |
| --- | --- |
| [qcom-toolbox/ios-umi](https://github.com/qcom-toolbox/ios-umi) | Upstream repository: boot shim, XNU patch series, host tools, notes |
| [`ios-umi/`](https://github.com/qcom-toolbox/UniXNU/tree/main/ios-umi) in this repository | Imported copy with its full history |

The project began on the Redmi Note 10 Pro (`sweet`), so many drivers, tools and
boot-args still carry the `sweet` name. The kernel picks the board from the
device tree at runtime.

## State

As of 2026-11-06 the phone boots to the iOS home screen with the stock apps.
The feature-by-feature table is in
[`Status.md`](https://github.com/qcom-toolbox/ios-umi/blob/main/Status.md) and
every boot and decision is logged in
[`NOTES.md`](https://github.com/qcom-toolbox/ios-umi/blob/main/NOTES.md).

| Area | State |
| --- | --- |
| Boot | Stock Xiaomi ABL → `fastboot boot` of an own shim → XNU; the image can also be flashed to `boot` |
| CPU and RAM | All 8 cores via PSCI, GICv3, EPSS frequency governor; 6 GB of the 8 GB for iOS |
| Storage | Own UFS host driver; journaled HFS+ root in `userdata`, read/write |
| Userland and GUI | launchd, system daemons, backboardd, SpringBoard, lock screen, Control Center, Settings, 31 stock apps |
| Display and brightness | 1080×2340 AMOLED presented as the iPhone X panel; slider, auto-brightness (SLPI light sensor), Night Shift |
| GPU | Adreno 650 draws the UI and every Metal app (Safari included) through Mesa turnip and a Metal-to-Vulkan bridge |
| Touch and buttons | ST FTM5 over GENI I²C with GPI DMA; power and volume keys |
| Battery and charging | PM8150B fuel gauge; kernel charger control (4.40 V, 2.0 A, QC 2.0 / 3.0); no USB-PD |
| Wi-Fi | QCA6390 over PCIe + MHI; open and WPA2-PSK on 2.4 GHz |
| Bluetooth | QCA6390 over UART; scan, connect and pair |
| Audio | Speaker through the ADSP and CS35L41 amps; no microphones |
| Cellular | X55 registers on LTE, carrier and bars in the status bar; data session opens but carries no packets yet |
| Location | Wi-Fi positioning; no GPS |
| Not working | Camera, video decode, motion sensors, fingerprint, SEP / Face ID, NFC, vibration, App Store / Apple ID |

Security is mostly off (permissive AMFI and sandbox, stub AppleKeyStore, no data
protection). Do not put personal data on the phone.

## Board and system inputs

| Item | Value |
| --- | --- |
| Board | `umi` |
| SoC | `SM8250` |
| Donor | iPhone X `iPhone10,3` / `D22AP`, iOS `16.7.16`, build `20H392` |
| Source XNU | `xnu-8796` (Darwin 22), built on GitHub macOS runners |
| Boot image | Android boot.img v2 carrying the shim, XNU, generated ADT and boot-args |
| Root | Single case-sensitive journaled HFS+ volume flashed to `userdata` |

Installation **erases Android's `userdata`**. Bootloader, recovery, modem and
persist partitions are not touched; back them up first.

## Build

The steps are in the repository
[README](https://github.com/qcom-toolbox/ios-umi#how-to-do-it-yourself) and
[`docs/UMI.md`](https://github.com/qcom-toolbox/ios-umi/blob/main/docs/UMI.md).
In outline:

1. Back up the phone and extract the stock DTB from `boot.img`.
2. Build the kernel with the `xnu.yml` workflow, which applies `xnu/patches/` in order.
3. Build the HFS+ root from the iPhone X IPSW with `tools/mkiosroot.sh` and `tools/sweet-root-tweaks.py`.
4. Make the boot image with `tools/umi-boot-image.sh`.
5. `fastboot flash userdata` the root, then `fastboot boot` the image.

Apple firmware and root images, phone firmware and partition backups are not
distributed.

## Maintenance

The maintainer owns the repository and its releases. This page records the
reported state of the port.
