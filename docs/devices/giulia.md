# OnePlus Ace 5 (giulia)

giulia is the OnePlus Ace 5 (PKG110) with the SM8650 SoC. The port below is an independent community project. The UniXNU organization does not maintain it. The kernel is a Darwin 22.6 / iOS 16 build.

| Repository | Maintainer | State |
| --- | --- | --- |
| [UniXNU-giulia](https://github.com/jasper2863/UniXNU-giulia) | [jasper2863](https://github.com/jasper2863) | GUI progress bar reached; installation service blocked |

## State

| Area | State |
| --- | --- |
| UEFI handoff and XNU memory initialization | works |
| Platform drivers, CPU0 and SGI1 | works |
| Native UFS read | works |
| USB CDC debug serial | works |
| HFSX root volume | read and write mount works |
| `launchd` and system services | start |
| GUI kernel | Apple logo and progress bar; about 77,000 frame submissions logged; no SpringBoard or backboardd crash observed |
| Usable UI | not reached; the installation service is blocked |
| Touch | controller identity and packets verified; physical touch not usable |
| Baseband, audio, GPU and DRM | not implemented |

The repository keeps the full boot logs, host checks and image hashes. The current blocker is the system app installation and migration path.

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the port and its state; it does not take over maintenance.
