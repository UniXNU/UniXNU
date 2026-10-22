# Xiaomi 13 Pro (nuwa)

nuwa is the Xiaomi 13 Pro with the SM8550 SoC and 12 GB of RAM. The port below is an independent community project. The UniXNU organization does not maintain it. The target is iOS 16 with the iPhone10,3 / d22ap identity.

| Repository | Maintainer | State |
| --- | --- | --- |
| [UniXNU-nuwa](https://github.com/wh1stl3/UniXNU-nuwa) | [wh1stl3](https://github.com/wh1stl3) | Source kernel builds and links; platform archives, prelink and hardware not done |
| [UniXNU-nuwa](https://github.com/pubglite55/UniXNU-nuwa) | [pubglite55](https://github.com/pubglite55) | Firmware, payload and boot image built; hardware reaches the UniXNU boot manager; payload volume mounting is being investigated |

## State

The table below is wh1stl3's port.

| Layer | State |
| --- | --- |
| Source kernel | xnu 8796.141.3 builds and links in CI; ARM64 `MH_EXECUTE`, Darwin 22.6.0, no unresolved symbols |
| Platform archives | not passing; `ArmCpu` includes and the Darwin 22 archive build are still in progress |
| Donor interface | 65,348 pointer bindings checked; the source kernel misses the APFS `_vfs_getvfs_with_vfsops` binding |
| VFS bridge | static checks pass; the actual compile is pending |
| Prelink, QEMU and hardware | not run |
| Board file | `example = true`; firmware `uefi-nuwa` and the nuwa platform values are not established |

`docs/STATUS.md` in the repository is the current source of truth.

## pubglite55's port

This port uses the restricted sheng configuration and follows the firmware-plus-payload route.

| Layer | State |
| --- | --- |
| Source kernel | xnu 8796.141.3 builds, links and prelinks in CI; `kernel.macho` is 54.3 MB |
| Platform archives | all 13 archives build, based on the sheng kit |
| Firmware | Mu-Silicium `nuwaPkg` integrates DarwinBoot, UniXNUDxe, the UniXNU application and a boot-memory driver; hardware shows the UniXNU boot manager |
| Payload and boot image | payload FAT volume of 188 MiB; the Android boot image builds and boots on hardware |
| Hardware | BootShim → UEFI → BDS → boot manager works; the payload volume is not attached by Fat yet, so the kernel entry is not reached |
| Board file | some values are still sheng placeholders (for example the userdata LBA); `uefi-nuwa` exists |

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the port and its state; it does not take over maintenance.

