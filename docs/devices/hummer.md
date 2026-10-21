# OnePlus Ace 5 Pro (hummer)

hummer is the OnePlus Ace 5 Pro (PKR110) with the SM8750 SoC. The port below is an independent community project. The UniXNU organization does not maintain it.

| Repository | Maintainer | State |
| --- | --- | --- |
| [UniXNU-hummer](https://github.com/2426120557/UniXNU-hummer) | [2426120557](https://github.com/2426120557) | UEFI firmware works; XNU CI trial |

## State

| Area | State |
| --- | --- |
| UEFI firmware and menu | works on hardware; GOP display and key input |
| XNU kernel | CI trial; ADT generator ready |
| GPU (Adreno 830) | not started |
| Persistent Data | not started |

The board file marks `[kernel]`, `[ipsw]` and `[payload]` as scaffolding. The README names the GPU as the main blocker.

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the port and its state; it does not take over maintenance.
