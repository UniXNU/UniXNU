# Xiaomi Redmi Note 5 / Note 5 AI (whyred)

whyred is the Xiaomi Redmi Note 5 / Note 5 AI, with the SDM636 SoC (4x Cortex-A73 and 4x Cortex-A53, Kryo 260, ARMv8.0) and 3, 4 or 6 GB of RAM. The port below is an independent community project. The UniXNU organization does not maintain it.

| Repository | Maintainer | State |
| --- | --- | --- |
| [UniXNU-whyred](https://github.com/N1709/UniXNU-whyred) | [N1709](https://github.com/N1709) | Board, SoC layer, DTS, defconfig, packaging inputs and firmware |

## State

| Layer | State |
| --- | --- |
| Board description | format 2; ARM64 profile with the local `sdm660` SoC layer and the unmodified iPad7,1 / iPadOS 17.7.11 / 21H461 image |
| SoC layer | CPU, PSCI, GICv3 and timer; validated with `dtc` and `make-adt.py` |
| Memory | RAM at `0x80000000` for 2 GiB, splash reservation at `0x9d400000` for 36 MiB |
| userdata | GPT first LBA `0x2b8c00`, last LBA `0x1d7d6ff`, 4 KiB LBAs |
| Firmware | Mu-Silicium UEFI complete in the repository; not booted on hardware |
| Kernel, payload and boot image | not built; the first full build is pending |
| Drivers | eMMC / SDHCI, display, Synaptics touch, GPU, network, audio and power are partial or not started |

## Boundary

Boot with `fastboot boot` only. Never flash boot, modem, persist or recovery, and never format `userdata`. The user stages the root image inside `userdata`; the repository does not write it.

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the port and its state; it does not take over maintenance.
