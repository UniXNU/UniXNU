# Boot the image

Follow [Building](/building) through boot-image assembly first. The procedure below starts the image from RAM and checks the menu, loader and kernel in order.

Build the firmware with `./unixnu build firmware --uefi ../uefi-<device>` and include `UniXNURamDiskDxe` plus DiskIoDxe and FAT support for a Mu-Silicium initrd payload. Build the payload before `./unixnu bootimg`. The [firmware integration guide](/porting/uefi-firmware#required-integration) lists the required DSC/FDF entries and menu checks.

For repeated builds, save paths in [unixnu.local.toml](/reference/configuration#local-build-inputs). After changing boot arguments, rebuild the payload and boot image using the [argument workflow](/xnu/boot-arguments#apply-arguments). Follow the [green-bar diagnosis](/guide/debugging#green-bar) for a stall at loader handoff.

## 1. Check inputs {#prerequisites}

- An unlocked bootloader with `fastboot`.
- A device with a UEFI port that matches the board configuration.
- A built boot image with a payload, or an empty ramdisk for the boot manager smoke test.
- A serial console when the board exposes a UART.

## 2. Prepare root storage {#first-boot}

Ports using the userdata root layout need that image installed before their first root boot. The image supplies the OS and SystemOS volumes and the root volume UUID that the kernel matches.

Run the flash command when installing or replacing the root image. With the matching root image already installed, continue at step 3.

Flashing `userdata` overwrites that partition. Confirm the target device, its partition geometry and the report's image path, and save any data needed from that partition before running the command.

```sh
fastboot devices
fastboot flash userdata out/<device>/<os_profile>/<config>/userdata/userdata-root.img
fastboot reboot bootloader
```

The userdata image is large. Build it with `unixnu build userdata` and flash it from the device repository report.

The Data seed supplies the writable Data volume. The `--skip-setup` option marks Setup as done in a copy of the seed, so the Hello pages do not run. The procedure and the preference changes are in [Skip Setup](/guide/skip-setup).

## 3. Start the image {#start-the-image}

```sh
fastboot devices
fastboot boot out/<device>/<os_profile>/<config>/boot/boot.img
```

`fastboot boot` transfers the image and starts it once. The running payload follows its configured storage and installation policy.

The boot image contains:

| Part | Contents |
| --- | --- |
| Kernel | gzip of BootShim plus the UEFI firmware volume |
| Ramdisk | UniXNU payload FAT volume |
| Appended data | Device tree |

The stock Android bootloader loads the image, verifies the ARM64 header in BootShim, and jumps to the shim. BootShim starts the firmware volume.

## 4. Check the boot menu {#boot-manager}

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

## 5. Check loader handoff {#darwin-boot}

For an entry of type `xnu`, DarwinBoot reads these files from the entry directory:

| File | Required | Contents |
| --- | --- | --- |
| `kernel.macho` | yes | Prelinked XNU kernel |
| `kernel.macho.adt` | yes | Apple-format device tree sidecar |
| `kernel.macho.trustcache` | no | Trust cache bundle |
| the entry `initrd` | no | Data ramdisk seed |

DarwinBoot copies the kernel segments into a contiguous physical window, builds `boot_args`, installs the ADT and the trust cache addresses in the `/chosen/memory-map` placeholders, and exits boot services.

The default window is 256 MiB. The ADT property `/chosen/darwinboot-memory-size` can request a larger window.

## 6. Save logs {#logs}

The UEFI firmware logs to `EFI_SERIAL_IO_PROTOCOL` when the board exposes a UART. UniXNU prefixes its lines with `UNIXNU:`.

The kernel logs to the serial port when the command line selects one, for example `serial=3`. The boot progress layer writes checkpoints to the framebuffer and the serial port.

Useful logs:

| Source | Location |
| --- | --- |
| Build driver | `out/<device>/<os_profile>/<config>/logs/*.log` |
| Boot manager | Serial console, lines with `UNIXNU:` |
| DarwinBoot | Serial console, lines with `DARWINBOOT:` |
| XNU | Serial console, kernel output |

## Payload in vendor_boot {#vendor-boot-payload}

A payload larger than a few megabytes does not fit in `boot`. On a GKI device
`boot` carries no ramdisk at all (`ramdisk_size` is 0) and a vendor ABL rejects
one, so the payload belongs in the `vendor_ramdisk` field of `vendor_boot` and
`./unixnu bootimg` is run with `--ramdisk none`.

Three limits decide whether the image is accepted:

- **Window.** A stock `vendor_boot` header places the ramdisk at `0x01000000`
  and the device tree at `0x01f00000`, which leaves 15 MiB. Relocate the ramdisk
  with `--ramdisk-addr` before the payload passes that size, or it overwrites the
  device tree.
- **Partition.** The rebuilt image has to stay inside the partition. The AVB
  footer in the last 64 bytes is retargeted at the vbmeta blob, so no footer has
  to be removed.
- **Filesystem.** The firmware mounts the ramdisk as FAT. `mformat -F` can
  produce a volume it cannot read; `mformat -T 8192 -h 64 -s 32` produces a FAT16
  volume that mounts.

The menu reports what it found as `payload: initrd <start>-<end> [<id>] fs <n>`.
`fs 0` means the block device exists but carries no readable filesystem, and a
missing payload line means the ramdisk never reached the loader.

## When the panel is the only output {#panel-diagnostics}

A board without a serial console reports progress on the framebuffer, and the
loader and the kernel each have their own signal:

- DarwinBoot paints the top sixteenth of the framebuffer green immediately
  before the branch to the kernel. A green band means every stage before the
  kernel succeeded.
- The optional entry probe paints one band per stage below the green one: blue at
  the kernel entry with the MMU off, magenta just before the MMU is enabled, and
  with `entry_probe_reset_delay` a reset through PSCI some seconds after the MMU
  is on, which turns "the CPU got that far" into a reboot.
- `payload.panic_screen = true` patches the panic path so the format string is
  drawn on the kernel's own framebuffer mapping. It shares the zero padding after
  `_start` with a stage-four probe, so the two cannot be enabled together.
- `entry_probe_reset_after` bisects `_arm_init`: a reset after the named call
  means the kernel returned from it.

A loader that fails after drawing its own diagnostics has them overwritten as
soon as the menu redraws. Hold the screen for a few seconds on the failure path
when a photograph is the only record.

## Recovery

Use the device's hardware reset sequence to return to its bootloader. Once fastboot responds, the following command restarts that bootloader:

```sh
fastboot reboot bootloader
```

If firmware stalls before the menu, capture the last output, reset into the bootloader and confirm `fastboot devices`. Check the firmware inputs using [bring-up](/porting/bring-up) before another attempt.

## macOS

A macOS port needs an OS profile matching its XNU version, kernelcache, prelink
roots, private driver ABIs, trust caches and root layout. Qualify those inputs
with [kernel preparation](/guide/build-kernel) and [prelink](/concepts/prelink).
The supplied `ipados-17.7.11-21H461` profile describes its named iPadOS build.

Select the completed OS profile in `board.os_profile`, inspect `status --json`,
then repeat the build and bring-up sequence. Record macOS results against that
profile and the target device.

## Next steps

- [Userdata image](/guide/userdata) describes the partition image.
- [Boot arguments](/xnu/boot-arguments) lists the kernel arguments.
- [Troubleshooting](/reference/troubleshooting) lists failure conditions and checks.
- [Devices](/devices/) lists device specific commands.
