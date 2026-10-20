# Boot the image

The boot image runs from RAM. The workflow starts the image and leaves the installed boot partition unchanged.

## Prerequisites

- An unlocked bootloader with `fastboot`.
- A device with a UEFI port that matches the board configuration.
- A built boot image with a payload, or an empty ramdisk for the boot manager smoke test.
- A serial console when the board exposes a UART.

## Start the image

```sh
fastboot devices
fastboot boot out/<board>/boot/boot.img
```

`fastboot boot` transfers the image and starts it one time. The stock boot partition and the installed OS stay unchanged.

The boot image contains:

| Part | Contents |
| --- | --- |
| Kernel | gzip of BootShim plus the UEFI firmware volume |
| Ramdisk | UniXNU payload FAT volume |
| Appended data | Device tree |

The stock Android bootloader loads the image, verifies the ARM64 header in BootShim, and jumps to the shim. BootShim starts the firmware volume.

## Boot manager

UniXNU prints its version and configuration summary to the serial port and draws the menu. The default configuration uses a timeout, a default entry and a countdown.

| Action | Key |
| --- | --- |
| Move the highlight | Up and Down |
| Boot the selected entry | Enter |
| Stop the countdown | Any key |
| Confirm an entry | Enter |
| Cancel a confirmation | Any key without choices, or Enter on Cancel |
| Choose a confirmation option | Up and Down, then Enter |

An entry with `confirm` shows a question before it boots. The countdown skips entries that require confirmation. With `confirm_titles`, Cancel is selected first and the chosen `confirm_args` entry is appended to the entry's arguments. See [Boot configuration](/reference/boot-configuration).

The menu entries come from `\EFI\UniXNU\unixnu.toml`. An entry can start an EFI image, a Linux image with an EFI stub, an action, or a Darwin kernel through the loader protocol.

If UniXNU finds no configuration, it scans every volume for `\EFI\BOOT\BOOTAA64.EFI` and adds those entries in front of the built-in actions.

## Darwin boot

For an entry of type `xnu`, DarwinBoot reads these files from the entry directory:

| File | Required | Contents |
| --- | --- | --- |
| `kernel.macho` | yes | Prelinked XNU kernel |
| `kernel.macho.adt` | yes | Apple-format device tree sidecar |
| `kernel.macho.trustcache` | no | Trust cache bundle |
| the entry `initrd` | no | Data ramdisk seed |

DarwinBoot copies the kernel segments into a contiguous physical window, builds `boot_args`, installs the ADT and the trust cache addresses in the `/chosen/memory-map` placeholders, and exits boot services.

The default window is 256 MiB. The ADT property `/chosen/darwinboot-memory-size` can request a larger window.

## First boot

The first boot needs a userdata image. The image supplies the OS and SystemOS volumes and the root volume UUID that the kernel matches.

```sh
fastboot flash userdata out/<board>/userdata/userdata-root.img
fastboot reboot bootloader
fastboot boot out/<board>/boot/boot.img
```

The userdata image is large. Build it with `unixnu build userdata` and flash it from the device repository report.

The Data seed supplies the writable Data volume. The `--skip-setup` option marks Setup as done in a copy of the seed, so the Hello pages do not run. The procedure and the preference changes are in [Skip Setup](/guide/skip-setup).

## Logs

The UEFI firmware logs to `EFI_SERIAL_IO_PROTOCOL` when the board exposes a UART. UniXNU prefixes its lines with `UNIXNU:`.

The kernel logs to the serial port when the command line selects one, for example `serial=3`. The boot progress layer writes checkpoints to the framebuffer and the serial port.

Useful logs:

| Source | Location |
| --- | --- |
| Build driver | `out/<board>/logs/*.log` |
| Boot manager | Serial console, lines with `UNIXNU:` |
| DarwinBoot | Serial console, lines with `DARWINBOOT:` |
| XNU | Serial console, kernel output |

## Recovery

The image runs from RAM. Reset the device to return to the stock bootloader and the installed OS.

```sh
fastboot reboot bootloader
```

If the firmware stalls before the menu, reset the device and start the same image again. A firmware stall leaves the device in the bootloader; a second `fastboot boot` uses the same image.

## macOS

The boot pipeline is driven by the IPSW. A macOS restore image provides `KernelCache`, `DeviceTree`, `OS`, `Cryptex1,SystemOS`, `StaticTrustCache` and `Cryptex1,SystemTrustCache` in the same member layout.

To boot macOS:

1. Point `[ipsw]` in the board file at a macOS IPSW and set the product, version, build, device class, chip ID and board ID of that image.
2. Pin the member hashes in `[ipsw.sha256]`.
3. Set `[userdata] windows` to `OS` and `Cryptex1,SystemOS`.
4. Build the kernel, payload, boot image and userdata image.
5. Flash the userdata image and start the boot image.

The device tree and the platform drivers supply the hardware description. The userland comes from the macOS disk images.

## Next steps

- [Userdata image](/guide/userdata) describes the partition image.
- [Boot arguments](/xnu/boot-arguments) lists the kernel arguments.
- [Troubleshooting](/reference/troubleshooting) lists failure conditions and checks.
- [Devices](/devices/) lists device specific commands.
