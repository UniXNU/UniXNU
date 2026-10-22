# Xiaomi Pad 7 / POCO Pad X1 (uke)

uke is the Xiaomi Pad 7 and POCO Pad X1 with the SM7675 SoC. The port below is an independent community project. The UniXNU organization does not maintain it.

| Repository | Maintainer | State |
| --- | --- | --- |
| [UniXNU-uke](https://github.com/Allenwdk/UniXNU-uke) | [Allenwdk](https://github.com/Allenwdk) | Device repository; root mounted and launchd starts; display pending |
| [uefi-uke](https://github.com/Allenwdk/uefi-uke) | [Allenwdk](https://github.com/Allenwdk) | Mu-Silicium UEFI port |

## State

The stock ABL reaches stages 1 to 5: UEFI firmware, UniXNU menu, payload, DarwinBoot and the XNU entry. The green bar means the kernel entry code ran. On hardware, UFS root mounts and launchd starts. The display stays on the Apple logo because IOMFB finds no default framebuffer surface.

The stage 6 full kernel compiles and prelinks with `uke-full_defconfig`. The UFS block class binds to the pinned original candidate. On hardware, the root volume mounts and launchd runs; display and GPU remain the blockers.

| Area | State |
| --- | --- |
| UEFI firmware | works |
| UniXNU menu | works |
| Payload and DarwinBoot | works |
| XNU entry | works, green bar |
| Root device | mounted; launchd starts |
| Display | Apple logo; no default framebuffer surface |
| Watchdog | partial; watchdogd still hits SIGTRAP |
| Touch | probe only, firmware object empty |
| GPU | Adreno 732 values recorded, driver pending |
| USB, audio, Wi-Fi, sensors | not part of the current pass |

## Build

Firmware and boot image on Linux:

```sh
cd /path/to/UniXNU
./unixnu defconfig uke_defconfig -D ../UniXNU-uke
./unixnu fetch -D ../UniXNU-uke
./unixnu build firmware --skip-preflight -D ../UniXNU-uke --uefi ../uefi-uke -j 8
./unixnu bootimg -D ../UniXNU-uke --uefi ../uefi-uke --dtb ../uke-port/data/vendor_boot.dtb --ramdisk none
```

Kernel in the repository's GitHub Actions:

```sh
gh workflow run build-uke-kernel
```

The userdata image needs macOS `hdiutil`. The current stage, artifacts and remaining work are in `docs/PROGRESS.md` in the device repository.

## Maintenance

The maintainer named in the table owns the repositories and their release decisions. UniXNU documentation lists the port and its state; it does not take over maintenance.
