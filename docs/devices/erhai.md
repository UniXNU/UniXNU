# OnePlus Pad 2 Pro (erhai)

erhai is the OnePlus Pad 2 Pro (OPD2413) with the SM8750 SoC. The port below is an independent community project. The UniXNU organization does not maintain it.

| Repository | Maintainer | State |
| --- | --- | --- |
| [UniXNU-erhai](https://github.com/wally001012-cyber/UniXNU-erhai) | [wally001012-cyber](https://github.com/wally001012-cyber) | XNU entry bring-up; root and userland not configured |

## State

| Area | State |
| --- | --- |
| Board values | measured on the device: FD base `0xA7000000`, GIC, timebase, panel, touch and boot partition |
| UEFI and payload | `embed_payload` puts the payload in the kernel field because the OnePlus ABL replaces the ramdisk field during `fastboot boot` |
| Kernel | source-only kernel built in GitHub Actions; the bring-up profile runs on the boot CPU with AMFI removed from the prelink |
| Screen checkpoints | green bar plus S1 to S6 |
| Root, UFS and GPU | not enabled in this profile |
| Hardware result | the repository records the measured values and the expected S1 to S6 sequence |

The board is modelled on the OnePlus 13T port. The current target is the XNU entry, not a root file system or userland.

## Build

```sh
python unixnu --prepare
python unixnu defconfig erhai_defconfig
python unixnu bootimg --dtb <device.dtb> --ramdisk <payload.img> -o boot.img
```

Kernel and payload in GitHub Actions:

```
Actions -> erhai XNU (OnePlus Pad 2 Pro) -> Run workflow
```

Boot with `fastboot boot boot.img` only. Do not flash a partition.

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the port and its state; it does not take over maintenance.
