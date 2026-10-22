# OnePlus Ace 5 (giulia)

giulia is the OnePlus Ace 5 (PKG110) with the SM8650 SoC. The port below is an independent community project. The UniXNU organization does not maintain it. The kernel is a Darwin 22.6 / iOS 16 build.

| Repository | Maintainer | State |
| --- | --- | --- |
| [UniXNU-giulia](https://github.com/jasper2863/UniXNU-giulia) | [jasper2863](https://github.com/jasper2863) | GUI progress bar reached; installation service blocked |
| [UniXNU-OnePlus-Ace5](https://github.com/tycykp/UniXNU-OnePlus-Ace5) | [tycykp](https://github.com/tycykp) | Hello and Setup reached; touch in progress |

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

## tycykp repository

`UniXNU-OnePlus-Ace5` records a separate iOS 16 / Darwin 22 bring-up. Its latest device test reached the Hello and Setup interface. UEFI handoff, XNU startup, native UFS reads, USB CDC serial, HFSX root mount and `launchd` startup are recorded for the tested configuration. Touch identity and reports are observed; the GPIO fallback is unverified. Wi-Fi stays at `Detect.Quiet`, and GPU, audio, cellular and DRM have no complete device validation.

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the port and its state; it does not take over maintenance.
