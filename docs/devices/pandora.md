# Xiaomi 17 Pro (pandora)

pandora is the Xiaomi 17 Pro with the SM8850 SoC. The port below is an independent community project. The UniXNU organization does not maintain it. It runs the iPhone X iOS 16.7.16 userland on an xnu-8796 kernel built from the ios-sweet patch series. A small loader started by `fastboot boot` replaces the UEFI boot chain. The kernel uses the UniXNU native 4 KiB patches, and the original Apple kexts are prelinked with NativePrelink.

| Repository | Maintainer | State |
| --- | --- | --- |
| [ios-pandora](https://github.com/ShueiTsuki/ios-pandora) | [ShueiTsuki](https://github.com/ShueiTsuki) | iOS 16.7.16 lock screen with touch and buttons on hardware |

## State

| Stage | State |
| --- | --- |
| Boot | `fastboot boot` of a loader image that carries the kernel, the ADT and the payload; Android and every partition stay unchanged |
| CPU | 8 cores, 4 KiB pages |
| Storage | native UFS driver; the root file system is a pinned file in the Android userdata partition, read and written through its extents, without a wipe |
| Display | 1220x2656 panel through the bootloader framebuffer; brightness through DSI DCS |
| Input | Synaptics touch over GPI DMA; power and volume buttons |
| Userland | iOS 16.7.16 (20H392) lock screen; wallpaper and widgets missing |
| Original kexts | AMFI and its dependencies prelinked with NativePrelink; QEMU and hardware runs in progress |
| GPU, audio, camera | not available |

## Build

The kernel is built by the `xnu.yml` GitHub Actions workflow with `machine_config=PANDORA`. The scripts in the repository build the ADT and the payload in WSL and the loader with the Android NDK:

```sh
python3 tools/mkprelink.py <kernel> <kernelcache> <out>
KERNEL=<out> tools/boot_ios.sh --file /data/local/tmp/iosroot.img --run <N> --rd ufsroot0
```

`tools/boot_ios.sh` resolves the extents of the pinned root file, builds the payload and the loader image, and starts it with `fastboot boot`. The kernel, the kernelcache, the root image and the trust caches are external inputs and are not stored in the repository.

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the port and its state; it does not take over maintenance.
