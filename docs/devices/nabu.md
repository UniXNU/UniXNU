# Xiaomi Pad 5 (nabu)

nabu is the Xiaomi Pad 5 with the SM8150 SoC. The port below is an independent community project. The UniXNU organization does not maintain it.

| Repository | Maintainer | State |
| --- | --- | --- |
| [unixnu-nabu](https://github.com/Lux12138/unixnu-nabu) | [Lux12138](https://github.com/Lux12138) | XNU executes; PMGR and userspace next |

## State

The boot chain reaches XNU: `fastboot boot` starts Mu UEFI, the UniXNU menu reads the cust payload, DarwinBoot validates the 51 MB kernel and hands off, and the green XNU screen appears. The next step is the PMGR power management framework before the IPSW userland can start.

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the port and its state; it does not take over maintenance.
