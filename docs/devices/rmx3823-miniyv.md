# realme GT5 240W (rmx3823) — miniyv port

realme GT5 240W (rmx3823) is an SM8550 (kalama) device. The port below is an
independent community fork of [Janit8r/uefi-rmx3823](https://github.com/Janit8r/uefi-rmx3823).
The UniXNU organization does not maintain it.

| Repository | Maintainer | State |
| --- | --- | --- |
| [simple-RMX3823-UniXNU](https://github.com/miniyv/simple-RMX3823-UniXNU) | [miniyv](https://github.com/miniyv) | UEFI bring-up |

## State

The full UEFI boot chain runs via `fastboot boot` (temporary boot — no
partitions are written):

ABL → BootShim → SEC → firmware-volume decompression → DXE (all drivers
dispatched) → BDS → the UniXNU menu (Apple logo, volume-key navigation) →
diagnostics halt.

Verified on hardware on 2026-11-10: framebuffer console at 1240x2772, menu
graphics, and button input. XNU has not been booted on this port yet.

Notable fixes on top of upstream:

- **Gunzip output corruption workaround.** ABL overwrites about 1.2 KB at a fixed offset
  (firmware offsets 0x349A6–0x47661) inside its own gunzip output. In the
  upstream layout that region lands in the middle of the LZMA-compressed
  firmware volume, so FV decompression fails on every prebuilt image. The
  firmware now inserts a 0x41000-byte pad section so the compressed volume
  starts past the damaged window.
- **RamManagerDxe removed.** It requires the Qualcomm RamPartition protocol
  that ABL provides in the stock chain; nothing installs it under
  `fastboot boot`, so the driver asserted.
- **BDS no longer powers off.** When no boot option is found, the platform
  now prints GOP and boot-option diagnostics and halts instead of blanking
  the screen and shutting down.

## Roadmap

- Wire up the UniXNU payload (the menu currently reports `image not found`).
- UFS storage support, so boot options can be registered.
- Boot XNU through DarwinBoot.
- GPU acceleration (Adreno 740).
- Peripherals: touch, USB, sensors, audio, smooth system experience.
  The cellular modem is out of scope for this port.

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU
documentation lists the port and its state; it does not take over maintenance.
