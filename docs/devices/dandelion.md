# Redmi 9A (dandelion)

dandelion is the Redmi 9A with the MediaTek MT6765 SoC (Helio G25). The port below is an independent community project. The UniXNU organization does not maintain it.

| Repository | Maintainer | State |
| --- | --- | --- |
| [UniXNU-dandelion](https://github.com/licg89/UniXNU-dandelion) | [licg89](https://github.com/licg89) | Early bring-up; UEFI port in progress |

## State

| Component | State |
| --- | --- |
| Hardware analysis | complete |
| Drivers | 8 core drivers implemented |
| Boot code | chainloader and test kernel |
| Direct boot | failed; kernel crashes, no UART |
| UEFI port | in progress |
| Real device test | blocked by no UART |

Overall progress is about 55%. The current strategy is to port Mu-Silicium UEFI for MT6765, then integrate UniXNU. The README records a 6 to 12 month estimate for the port.

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the port and its state; it does not take over maintenance.
