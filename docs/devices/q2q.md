# Galaxy Z Fold3 (q2q)

q2q is the Samsung Galaxy Z Fold3 with the SM8350 SoC. The port below is an independent community project. The UniXNU organization does not maintain it.

| Repository | Maintainer | State |
| --- | --- | --- |
| [UniXNU-q2q](https://github.com/agcarbajo/UniXNU-q2q) | [agcarbajo](https://github.com/agcarbajo) | Source kernel build harness only |

## State

The repository is a source-only XNU build harness. It builds ARM64 XNU 10063.141.1 with the UniXNU 4 KiB patches, `ArmDTPlatform`, `ArmCpu` and the source crypto provider. It contains no OS, IPSW, device dumps, keys or partition backups, and it does not access a connected phone. The first objective is a source kernel for CPU and console bring-up; it cannot boot iPadOS userspace.

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the port and its state; it does not take over maintenance.
