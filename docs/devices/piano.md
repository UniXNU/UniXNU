# Xiaomi Pad 8 Pro (piano)

piano is the Xiaomi Pad 8 Pro with the SM8750 SoC. The port below is an independent community project. The UniXNU organization does not maintain it. The firmware half comes from [Project-SunUEFI](https://github.com/slwyts/Project-SunUEFI).

| Repository | Maintainer | State |
| --- | --- | --- |
| [UniXNU-piano](https://github.com/code002-2/UniXNU-piano) | [code002-2](https://github.com/code002-2) | Kernel builds and prelinks in CI |

## State

The device tree generator and board description are accepted by the `unixnu` driver. The XNU kernel builds and prelinks in CI: 51,806,208 bytes, ARM64 `MH_EXECUTE`, namespaced source corecrypto, `ArmDTPlatform` and `ArmCpu`. Nothing has run on the tablet. The payload, boot image and the UniXNU and DarwinBoot integration in the SunUEFI `pianoPkg` firmware are next.

## Build

```sh
gh workflow run build-piano-kernel
```

Download `piano-kernel` from the run and read `kernel.macho` plus its SHA-256.

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the port and its state; it does not take over maintenance.
