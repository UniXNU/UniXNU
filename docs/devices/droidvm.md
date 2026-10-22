# DroidVM guest (crosvm on Gunyah)

The DroidVM target runs UniXNU as a guest under crosvm on the Gunyah hypervisor of a Snapdragon phone. The port below is an independent community project. The UniXNU organization does not maintain it.

| Repository | Maintainer | State |
| --- | --- | --- |
| [UniXNU-droidvm](https://github.com/Droid-VM/UniXNU-droidvm) | [Droid-VM](https://github.com/Droid-VM) | Kernel build, verified root, lock screen and home screen |

## State

| Stage | State |
| --- | --- |
| Kernel build | done on macOS 27 with Xcode 27.1 |
| UEFI to XNU | works on SM8650 and SM8850, 4 KiB pages |
| Root | original OS and SystemOS images verified on read-only virtio-mmio disks |
| Desktop | lock screen about a minute after boot; home screen after a Home press; CPU-rendered on SM8650 |
| Data | persistent through the store disk on SM8650 |
| Input | touch screen and Home over virtio-input |
| Network | en0 over virtio-net on virtio-mmio, bridged to the phone's Wi-Fi; DHCP IPv4 and IPv6 (SM8650) |
| GPU | NativeAdreno over the host phone's KGSL through crosvm `--droidvm-gpu`; the widget renderer and icon services draw through the Metal plugin; full GPU apps not qualified |

`BigfootACA/unixnu-droidvm-ci` provides CI builds for the QEMU/KVM and DroidVM targets.

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the port and its state; it does not take over maintenance.
