# OnePlus 13T (oneplus13t)

oneplus13t is the OnePlus 13T (PKX110, OP60F5L1) with the SM8750 SoC. The port below is an independent community project. The UniXNU organization does not maintain it. The repository was renamed from `UniXNU-oneplus13t` to `UniXNU-Pagani_SM8750` and keeps its history.

| Repository | Maintainer | State |
| --- | --- | --- |
| [UniXNU-Pagani_SM8750](https://github.com/IssacL04/UniXNU-Pagani_SM8750) | [IssacL04](https://github.com/IssacL04) | XNU S1 to S6 reached; root device search panics; no root or userland |

## State

| Part | State |
| --- | --- |
| UEFI Shell and menu | works on hardware; side key interaction still to confirm |
| XNU build in GitHub Actions | builds; the ninth image reaches S1 to S6 |
| Payload and boot image | embedded payload handoff; boot image compared after unpacking |
| DarwinBoot handoff | green handoff bar on hardware |
| XNU entry | S1 to S6 reached; console, `zalloc` and BSD root search executed |
| Root and userland | not available; the root search panics after 60 seconds |
| kernelcache prelink, userdata, iOS userland | not configured |

The panic page records `poll=0x3c`, `timer=0x1a3` and the timeout path. The single-core timer interrupt and observation thread run. Long-term stability and multi-core scheduling are not verified.

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the port and its state; it does not take over maintenance.
