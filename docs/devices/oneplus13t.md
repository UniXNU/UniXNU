# OnePlus 13T (oneplus13t)

oneplus13t is the OnePlus 13T (PKX110, OP60F5L1) with the SM8750 SoC. The port below is an independent community project. The UniXNU organization does not maintain it.

| Repository | Maintainer | State |
| --- | --- | --- |
| [UniXNU-oneplus13t](https://github.com/IssacL04/UniXNU-oneplus13t) | [IssacL04](https://github.com/IssacL04) | UEFI Shell and menu; XNU build and payload; DarwinBoot handoff; no XNU entry |

## State

| Part | State |
| --- | --- |
| UEFI Shell and menu | works on hardware; side key interaction still to confirm |
| XNU build in GitHub Actions | builds; `kernel.macho` and FAT payload produced |
| Payload and boot image | payload produced; boot image compared after unpacking |
| DarwinBoot handoff | green handoff bar on hardware |
| XNU entry | no evidence yet |
| kernelcache prelink, userdata, iOS userland | not configured |

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the port and its state; it does not take over maintenance.
