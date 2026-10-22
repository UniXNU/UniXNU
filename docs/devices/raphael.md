# Redmi K20 Pro / Mi 9T Pro (raphael)

raphael is the Redmi K20 Pro and Mi 9T Pro with the SM8150 SoC. The port below is an independent community project. The UniXNU organization does not maintain it.

| Repository | Maintainer | State |
| --- | --- | --- |
| [UniXNU-raphael](https://github.com/penYo22/UniXNU-raphael) | [penYo22](https://github.com/penYo22) | New repository; kernel build not passing |

## State

The hardware values are measured on a device: DRAM base `0x80000000`, userdata LBAs, GIC, UFS, USB, panel and CPU layout. The repository references the nabu port for the SM8150 bring-up issues.

The kernel build has not passed. The CI workflow builds the kernel on macOS and the payload on Linux. There is no device boot evidence yet.

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the port and its state; it does not take over maintenance.
