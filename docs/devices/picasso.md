# Redmi K30 5G (picasso)

picasso is the Redmi K30 5G with the Qualcomm SM7250 SoC. The port is an independent community project initiated by YinCQL.

| Repository | Maintainer / Contributor | State & Focus |
| --- | --- | --- |
| [UniXNU-picasso](https://github.com/YinCQL/UniXNU-picasso) | [YinCQL](https://github.com/YinCQL) | Initial device port & UEFI firmware bring-up |
| [UniXNU-picasso](https://github.com/silenzio111/UniXNU-picasso) | [silenzio111](https://github.com/silenzio111) | Stage 2: UFS 2.1 physical root, Adreno 620 Metal stack, GENI UART & USB panic dump |

## State

The picasso port combines UEFI firmware bring-up with the Stage 2 kernel and driver stack. The current stack features:
- Board description, kernel defconfig (`picasso_platform_defconfig`), and full Apple Device Tree (ADT) generation.
- Qualcomm QUPv3 GENI UART early serial console with dual-output LCD framebuffer mirroring.
- Physical UFS 2.1 root partition mapping (Route B, 8.74 GiB APFS system and Cryptex1 volumes).
- Adreno 620 Metal acceleration userland stack with static AMFI trust cache integration.
- Host-side non-invasive crash and dmesg buffer extraction over USB (`dump-picasso-panic.py`).

## Maintenance

The maintainers own their respective repositories and release decisions. UniXNU documentation records the community port and its state; it does not take over maintenance.
