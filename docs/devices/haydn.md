# Redmi K40 Pro (haydn)

haydn is the Redmi K40 Pro with the SM8350 SoC. The port below is an independent community project. The UniXNU organization does not maintain it. The page covers the UniXNU route. A separate SWEET route with iOS 16 userland also exists in the maintainer's workspace.

| Repository | Maintainer | State |
| --- | --- | --- |
| [UniXNU-haydn](https://github.com/xiaomi-haydn-dev/UniXNU-haydn) | [xiaomi-haydn-dev](https://github.com/xiaomi-haydn-dev) | Device repo and UEFI plan; firmware, payload and boot image built; not run on hardware |
| [UniXNU-haydn4](https://github.com/xiaomi-haydn-dev/UniXNU-haydn4) | [xiaomi-haydn-dev](https://github.com/xiaomi-haydn-dev) | Imported from guacamole; board file haydn, kit guacamole |

## State

| Layer | State |
| --- | --- |
| Board description and ADT | in place |
| UEFI plan | `haydnPkg` derived from venus; preflight reports 0 static errors; hardware unverified |
| Firmware, payload and boot image | built and byte-checked |
| Kernel and userdata | need macOS |
| Hardware boot | not run |

`PORTING.md` records the SM8350 hardware values and the iPad7,1 iPadOS 17.7.11 target. The separate SWEET route reached `launchd` with the iPhone X iOS 16.7.16 userland on hardware. It uses 16 KiB pages and HFS+, so it is not the UniXNU route.

## haydn4 repository

`UniXNU-haydn4` imports the guacamole tree and names the board haydn. The README and kit still use guacamole values. Treat its hardware state as not qualified until the board data is measured.

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the port and its state; it does not take over maintenance.
