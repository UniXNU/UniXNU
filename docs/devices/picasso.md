# Redmi K30 5G (picasso)

picasso is the Redmi K30 5G with the Qualcomm SM7250 SoC. The port below is an independent community project.

| Repository | Maintainer | State |
| --- | --- | --- |
| [UniXNU-picasso](https://github.com/silenzio111/UniXNU-picasso) | [silenzio111](https://github.com/silenzio111) | Stage 2: UFS 2.1 physical root, Adreno 620 Metal stack, GENI UART & USB panic dump |
| [UniXNU-picasso (upstream skeleton)](https://github.com/YinCQL/UniXNU-picasso) | [YinCQL](https://github.com/YinCQL) | Early skeleton |

## State

The port includes the board description, kernel defconfig (`picasso_platform_defconfig`), complete Apple Device Tree (ADT) generator, Qualcomm QUPv3 GENI UART driver with framebuffer mirroring, physical UFS 2.1 root partition mapping (Route B, 8.74 GiB APFS system image), Adreno 620 Metal acceleration stack with AMFI static trust cache, and USB panic buffer extraction tool (`dump-picasso-panic.py`).

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the port and its state; it does not take over maintenance.
