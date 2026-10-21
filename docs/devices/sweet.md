# Redmi Note 10 Pro (sweet)

sweet is the Redmi Note 10 Pro with the SM7150 SoC, Snapdragon 732G and Adreno 618. The port below is an independent community project. The UniXNU organization does not maintain it.

| Repository | Maintainer | State |
| --- | --- | --- |
| [UniXNU-sweet](https://github.com/dipa-studio/UniXNU-sweet) | [dipa-studio](https://github.com/dipa-studio) | Platform and loader bring-up |

## State

The port has a Sweet ADT, an ArmCpu override, a DarwinBoot override and an A618 legacy HFI transport. Host checks and EFI loader checks pass. There is no bootable sweet image and no accelerated desktop yet. Existing phone partitions are unchanged.

## Build

Host checks:

```sh
python3 scripts/check-host.py
python3 scripts/make-sweet-adt.py --output out/sweet.adt
```

Device repository integration:

```sh
python3 ../UniXNU/unixnu defconfig sweet_defconfig -D . --out out/driver
python3 ../UniXNU/unixnu status -D . --out out/driver
```

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the port and its state; it does not take over maintenance.
