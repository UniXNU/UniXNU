# Xiaomi Pad 7 Pro (muyu)

Xiaomi Pad 7 Pro (muyu) is a SM8635 device. The port below is an independent community project. The UniXNU organization does not maintain it.

| Repository | Maintainer | State |
| --- | --- | --- |
| [UniXNU-muyu](https://github.com/yehua123-oos/UniXNU-muyu) | [yehua123-oos](https://github.com/yehua123-oos) | iPadOS 17.7.11 boots; Adreno 735 GMU running |

## State

The iPadOS 17.7.11 (21H461) root is installed on `userdata` and the system boots to the desktop with a CPU-composed framebuffer (about 1.4 fps). UEFI starts with `fastboot boot`, the payload is the `vendor_boot` ramdisk, and physical buttons plus the Novatek touch controller run as native IOServices.

GPU: the Adreno 735 (`qcom,adreno-gpu-gen7-11-0`) GMU cold-starts and completes the full HFI startup on hardware (`cold=0 ph=7 proto=0` on 2026-10-30). Command submission, the CP and the Metal frontend are not implemented yet; GX rail power-up is blocked on an RPMh voter that this port does not drive.

## GPU notes

The port records its GPU evidence in the repository: `docs/GPU-CLIFFS-MMIO.md` (cliffs register map), `docs/GPU-GMU-MAP.md` (GMU platform description) and `docs/GPU-PROBE-RUNBOOK.md` (probe modes, expected values and judgement tree). The GMU firmware chip id was recovered from the CM3 image itself (`0x070b0000`), not from the catalog fallback formula.

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the port and its state; it does not take over maintenance.

## Sources

- [Board configuration](https://github.com/yehua123-oos/UniXNU-muyu/blob/main/board.toml)
