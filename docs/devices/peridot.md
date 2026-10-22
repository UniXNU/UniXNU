# Xiaomi Poco F6 / Redmi Turbo 3 (peridot)

peridot is the Xiaomi Poco F6 and Redmi Turbo 3 with the SM8635 SoC. The port below is an independent community project. The UniXNU organization does not maintain it. The kernel and root file system come from the DarwinXNU peridot work; the boot chain is a Mu-Silicium UEFI firmware plus an embedded XNU loader.

| Repository | Maintainer | State |
| --- | --- | --- |
| [DarwinXNU](https://github.com/hoshikv/xnu-darwin-peridot) | [hoshikv](https://github.com/hoshikv) | iOS 16.7.16 userland reached on hardware |

## State

| Stage | State |
| --- | --- |
| UEFI firmware and boot shim | works; `fastboot boot` loads the image and the loader hands off |
| Payload blocks | the `XNUKERN1`, `XNUFDT01` and `XNUROOT1` tail blocks are validated and read |
| XNU and iOS userland | the kernel boots, mounts the UFS root and reaches the iOS 16.7.16 lock screen and home menu on the panel |
| Display | AppleCLCD console on the 1220x2712 panel, presented as 1125x2436 |
| UFS and root | the userdata `ufsroot0` device mounts read-write and launchd runs |
| Touch and keys | ported from ios-sweet; not enabled in the current image |
| GPU | no accelerator; the framebuffer is presented through an empty `IOAcceleratorES` |

The image is booted with `fastboot boot` only. It is temporary and leaves Android and every partition unchanged.

## Values

| Item | Value |
| --- | --- |
| Board | Poco F6 / Redmi Turbo 3, SM8635, codename peridot |
| SoC | Qualcomm Snapdragon 8s Gen 3 (SM8635) |
| IPSW | iPhone X (D22AP / iPhone10,3), iOS 16.7.16 (`20H392`) |
| Kernel source | xnu-8796.141.3, macOS 13.5, `MACHINE_CONFIG=PERIDOT` |
| Firmware | Mu-Silicium peridot, `FD_BASE=0xA7100000`, `FD_SIZE=0x300000` |
| Payload | `XNUKERN1` (kernel Mach-O), `XNUFDT01` (ADT), `XNUROOT1` (root image) |
| ADT | `tools/mkadt.py`; synthetic ECID `PERIDOT`; chip-id `0x8015` |
| Root | iPhone X 16.7.16 root image (`ufsroot0`, read-write) |
| Boot arguments | `serial=3 cpus=8 rd=ufsroot0 ufsrw=1 rootrw=1 peridotfb_hz=30 peridotfb_default=1080` and the peridot driver flags |

## Build

The build needs the DarwinXNU patches applied to xnu-8796.141.3, a Mu-Silicium peridot tree, and an iOS 16.7.16 iPhone X root image. The kernel is built on macOS CI (`MACHINE_CONFIG=PERIDOT`). The image is reproduced end to end with:

```sh
tools/build-image.sh \
  --mu /path/to/mu \
  --kernel kernel.development.peridot \
  --root /path/to/ios16-root-peridot.img
```

Boot:

```sh
fastboot boot Mu-peridot.img
```

The kernel, ADT and root image are external inputs and are not stored in the repository.

## Boot chain

```
ABL -> fastboot boot Mu-peridot.img
        img = [BootShim.bin][SILICIUM_UEFI.fd][pad]XNUKERN1|size|kernel Mach-O[pad]XNUFDT01|size|ADT[pad]XNUROOT1|size|root
    -> BootShim copies the FD to FD_BASE and stores the tail address.
    -> Mu UEFI starts the embedded XnuLoader, which validates the tail blocks
       and fills boot_args.
    -> XnuLoader ExitBootServices and jumps to the kernel entry.
```

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the port and its state; it does not take over maintenance.
