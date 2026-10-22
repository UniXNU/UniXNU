# OnePlus 6T (fajita)

fajita is the OnePlus 6T with the SDM845 SoC. The port below is an independent community project. The UniXNU organization does not maintain it.

| Repository | Maintainer | State |
| --- | --- | --- |
| [UniXNU-fajita](https://github.com/johnpanos/UniXNU-fajita) | [johnpanos](https://github.com/johnpanos) | XNU reaches the root mount; no storage driver |

## State

| Stage | State |
| --- | --- |
| UEFI firmware and UniXNU menu | works on hardware with `fastboot boot` and an empty ramdisk |
| Payload, ADT and kernel | XNU 23.6.0 from the iPadOS 17.7.11 kernelcache boots to the root mount on hardware; VM, scheduler, IOKit, AMFI, Sandbox and APFS start |
| Root volume | the verbose console ends on `Waiting on ... IOMedia ... Apple_HFS`; no storage driver yet |
| Userdata | the 8.74 GiB iPadOS 17.7.11 root image was built and flashed; no kernel has read it yet |

The payload volume is flashed to `boot_a` because the ABL refuses a large ramdisk. The boot image carries no ramdisk. Run `fastboot set_active b` before each `fastboot boot`; the ABL refuses the boot when the active slot's boot partition holds an image or the retry counter is exhausted.

## Build

```sh
./unixnu defconfig fajita_defconfig -D ../UniXNU-fajita
./unixnu fetch
./unixnu build package firmware --uefi ../Mu-Silicium
./unixnu bootimg --uefi ../Mu-Silicium --dtb ../Mu-Silicium/Resources/DTBs/fajita.dtb
```

The firmware is derived from the enchilada port by `scripts/make-fajita-uefi.py`.

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the port and its state; it does not take over maintenance.
