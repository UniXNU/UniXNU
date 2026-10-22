# Lenovo Xiaoxin Pad 2022 (tb128fu)

tb128fu is the Lenovo Xiaoxin Pad 2022 (TB128FU) with the Snapdragon 680 (SM6225) SoC. The port below is an independent community project. The UniXNU organization does not maintain it. The firmware is [uefi-tb128fu](https://github.com/xVanTuring/uefi-tb128fu), a Mu-only platform on the uefi-sheng tree.

| Repository | Maintainer | State |
| --- | --- | --- |
| [UniXNU-tb128fu](https://github.com/xVanTuring/UniXNU-tb128fu) | [xVanTuring](https://github.com/xVanTuring) | iPadOS 17.7.11 home screen with touch; Metal frames use the GPU hand-off |
| [uefi-tb128fu](https://github.com/xVanTuring/uefi-tb128fu) | [xVanTuring](https://github.com/xVanTuring) | UEFI, UniXNU menu and DarwinBoot run on the tablet |

## State

| Stage | State |
| --- | --- |
| UEFI firmware and UniXNU menu | Works. Mu-only: the stock ABL carries no separable vendor DXE modules; the display is the splash buffer ABL leaves scanning out |
| Payload volume and DarwinBoot | Works. The image is flashed to `boot_a`; the ABL `fastboot boot` buffer is too small for it |
| XNU and the root | iPadOS 17.7.11 kernel on all 8 cores; verified OS/SystemOS root and Data volume on UFS |
| iOS userland | Home screen 70–95 s after boot; QuartzCore draws on the CPU, and Metal frames are presented through the GPU hand-off |
| Touch | Himax HX83102E over SPI; the kernel downloads its firmware |
| GPU | Adreno 610 (no GMU) runs under NativeAdreno; the Metal plugin presents frames through the GPU hand-off, 236 frames with no CPU fallback in tb128fu-040 |
| Not working | Audio, Wi-Fi, battery, buttons, sleep |

## Notes

SM6225 facts that differ from sheng and may help other ports:

- The EL1 virtual timer is INTID 19 (the DT lists timer PPIs 1, 2, 3, 0). INTID 27 is another source that stays asserted.
- SGIs do not arrive, so the IPIs are software-pended SPIs above the last SPI the device tree uses.
- The GPU SMMU firmware ignores fault writes to S2CR and turns bypass into fault; translate writes work.

## Maintenance

The maintainer owns the repositories and their release decisions. UniXNU documentation lists the port and its state; it does not take over maintenance.
