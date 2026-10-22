# Xiaomi Pad 6 (pipa)

pipa is the Xiaomi Pad 6 with the SM8250 SoC. The port below is an independent community project. The UniXNU organization does not maintain it. The firmware is [uefi-pipa](https://github.com/xVanTuring/uefi-pipa), a fork of uefi-sheng.

| Repository | Maintainer | State |
| --- | --- | --- |
| [UniXNU-pipa](https://github.com/xVanTuring/UniXNU-pipa) | [xVanTuring](https://github.com/xVanTuring) | Board and userdata values measured; not run on the tablet |
| [uefi-pipa](https://github.com/xVanTuring/uefi-pipa) | [xVanTuring](https://github.com/xVanTuring) | UEFI port, not run on hardware |

## State

The device repository is laid out like sheng. Static checks pass and every hardware value cites a public source. The memory banks, userdata geometry and hardware values were read from the tablet. Nothing has run on a pipa. The README documents stage 1 to 3 (firmware, menu, payload volume) and stage 4 to 5 (kernel entry). A storage driver is not present, so the kernel stops at the root device.

## Maintenance

The maintainer owns the repositories and their release decisions. UniXNU documentation lists the port and its state; it does not take over maintenance.
