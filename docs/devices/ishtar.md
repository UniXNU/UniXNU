# Xiaomi 13 Ultra (ishtar)

ishtar is the Xiaomi 13 Ultra with the SM8550 SoC. The repository below is an independent community port. The UniXNU organization does not maintain it.

| Repository | Maintainer | State |
| --- | --- | --- |
| [UniXNU-ishtar](https://github.com/peter8889/UniXNU-ishtar) | [peter8889](https://github.com/peter8889) | Device repository; kernel, payload and boot image all build on the host; stage diagnostics ready; no hardware run yet |

## UniXNU-ishtar

UniXNU-ishtar is based on UniXNU-sheng and reuses its kit, archive plan and the iPadOS 17.7.11 (21H461) OS profile, replacing only the board data. `board.toml` is schema 2, `feeds.toml` pins the shared SM8550 source, and `dts/ishtar.dts` describes only the board differences while including the shared SoC description.

The build chain is complete on the host: `./unixnu kernel`, `./unixnu payload` and `./unixnu bootimg` produce the kernel, the payload and the boot image in order, and the assembled image passes its own round-trip check with a consistent container header, payload window and partition geometry. Configuration, firmware, CPU, memory, image assembly and diagnostics are therefore implemented, and the device tree, kernel configuration and firmware package already agree on one board identity.

Diagnostics are the main result of this stage. `CONFIG_XNU_BOOT_PROGRESS` draws kernel stages onto the firmware framebuffer, so the stage a hang occurs in is visible before any display driver exists. That implementation is self-contained and reads no storage or Virtio counters, so it links into any configuration; the full monitor needs the audited storage, owner-root, Virtio and source-corecrypto build and is held until storage is up.

The next stage is storage, display, input, GPU, network, audio and power. The GPU is already in the component selection and links against stubs (`scripts/build-adreno-link-stubs.py`), because the full driver needs the payload-stage accelerator ABI and the kernel link has no variable for it. The UFS and display drivers stay off in `gpu_defconfig`, but the device tree already enables `ufs`, `ufsphy`, `gpu`, `gmu` and `gpu_smmu`, so turning a driver on is a configuration change rather than a device-tree change. The touch firmware is already pinned in `proprietary-files.txt` against an upstream commit and only needs the driver added to the component selection.

The device tree declares 8 GiB of DRAM. Declaring less than the fitted capacity is deliberate: the physical aperture and the page-table allocator would otherwise reach addresses no DRAM backs. The splash reservation sits at `0xb8000000` for a 1440x3200 panel with a 5760-byte stride and is marked `no-map`, because treating it as normal memory lets the allocator hand the framebuffer out. The partition geometry comes from the shipped GPT and is therefore only valid on a device that has not been repartitioned.

The port record is in `porting.toml`.

## Maintenance

The maintainer named in the table owns the repository and its release decisions. UniXNU documentation lists the port and its state; it does not take over maintenance.
