# Bring-up order

Bring-up proceeds in stages. Each stage has a visible result and a log line. Isolate one stage at a time.

For repeated builds, save paths in [unixnu.local.toml](/reference/configuration#local-build-inputs). After changing boot arguments, rebuild the payload and boot image using the [argument workflow](/xnu/boot-arguments#apply-arguments). Follow the [green-bar diagnosis](/guide/debugging#green-bar) for a stall at loader handoff.

Before enabling a peripheral, complete its [adaptation procedure](/porting/drivers). Build the image with [Building](/building), then use these checkpoints in order. After each failure, keep the image and the last log before changing inputs.

## Stage 1: UEFI

Goal: the firmware reaches a UEFI shell, a boot menu or the UniXNU application.

Checks:

- The firmware volume size matches `[uefi_fd] size`.
- The boot image header matches the bootloader requirement.
- `fastboot boot boot.img` starts the firmware without a reset.
- The framebuffer shows output, or the serial port shows UEFI output.
- Block devices and the payload volume are visible. For a Mu-Silicium initrd payload, check `UniXNURamDiskDxe`, DiskIoDxe and FAT in the FD using the [firmware integration guide](/porting/uefi-firmware#required-integration).

Tools:

```sh
fastboot boot out/<device>/<os_profile>/<config>/boot/boot.img
```

If firmware stops responding, reset into the device's bootloader, confirm `fastboot devices`, and capture the last firmware output before retrying.

## Stage 2: UniXNU

Goal: the menu appears and the configuration is parsed.

Checks:

- Serial lines start with `UNIXNU:`.
- The log reports the entry, driver, patch, ACPI, slice and kit counts.
- The menu lists the expected entries.
- Driver failures show a count and the first failure reason.

Minimal test: an empty ramdisk. UniXNU falls back to its built-in configuration and lists removable loaders.

```sh
./unixnu bootimg --uefi /path/to/Mu-Silicium --dtb board.dtb --ramdisk none
```

Before continuing, [scan the firmware log](/porting/log-capture#qr-logs) from
**Tools → Advanced Logger**. Prepare the platform logger and plugin with the
[integration steps](/porting/log-capture#firmware-setup).

## Stage 3: Payload

Goal: UniXNU reads `unixnu.toml` and the payload files.

Checks:

- The log reports the configuration path.
- The `xnu` entry is present.
- The payload report hashes match the files in the volume.
- The ADT sidecar is next to the kernel.

A payload error is visible before DarwinBoot starts.

## Stage 4: DarwinBoot

Goal: DarwinBoot validates the kernel, the ADT and the trust cache, then exits boot services.

Checks:

- Serial lines start with `DARWINBOOT:`.
- The loader prints the virtual base, physical base, arguments address and entry address.
- The printed output shows the framebuffer base, width, height and depth.
- The exception level is EL1.
- The bootstrap page table path reaches the kernel entry.

A refusal prints `DARWINBOOT: boot refused: <status>; firmware retained`. The firmware stays in control, so the device returns to the menu.

## Stage 5: Kernel entry

Goal: XNU starts and reaches the platform expert.

Checks:

- The kernel prints its version and boot arguments.
- The bootstrap page tables map the kernel window.
- The platform expert matches the ADT root.
- `/cpus`, `/arm-io`, `/defaults`, `/options` and the NVRAM proxy are present.

With the entry probe enabled, color bars mark early kernel checkpoints. See [Color bars](/guide/debugging#color-bars).

A missing platform provider produces a panic that names the provider. Add the driver or correct the ADT.

## Stage 6: Storage and root

Goal: the block driver publishes the userdata partition, the volumes appear, and XNU mounts the root.

Checks:

- The storage driver logs the link speed and the command queue.
- The partition scheme publishes `OS` and `SystemOS`.
- The root volume UUID matches `root_match_volume_uuid`.
- The kernel mounts the root and starts `launchd`.

A root match failure leaves the kernel without a root device. Check the UUID, the window offsets and the partition capacity.

Once storage works, [adapt persistent capture](/porting/log-capture#persistent-logs)
with a kernel writer and a Linux or recovery reader. Complete one manual retrieval before
enabling timed reset and the automated cycle.

## Stage 7: Userland

Goal: `launchd` runs and the first user process reaches a visible state.

Checks:

- `launchd` starts from the root volume.
- The Data volume mounts.
- The display server or the console presents output.
- The boot progress layer records the last checkpoint.

Use `boot-progress=2` and the diagnostic boot arguments to see the last completed checkpoint.

## QEMU before hardware

Follow [QEMU testing](/reference/qemu) to stage the ESP and run the menu/payload
fixture. The XNU entry fixture needs an ARM64 kernel, its ADT sidecar and
DarwinBoot staged together. Check the fixture's selected entry and expected
checkpoint before running it.

```sh
JOBS=8 bash package/Scripts/smoke.sh
```

Run from the main checkout with the QEMU requirements installed. This command
checks the UEFI package scenarios and writes logs/screenshots under
`package/Build/Smoke/`. Use the [kernel-entry instructions](/reference/qemu#xnu-entry-fixture)
for XNU work. Hardware peripheral results are recorded on the target device.

## Failure isolation

| Symptom | First check |
| --- | --- |
| No firmware output | Boot image header, firmware base and size, bootloader log |
| Firmware output, no menu | GOP driver, UniXNU driver path, `unixnu.toml` |
| Menu, no payload entry | Payload volume label, FAT driver, entry path |
| Payload entry, no DarwinBoot log | Loader protocol, DarwinBoot in the firmware volume |
| DarwinBoot refusal | Kernel Mach-O, ADT, trust cache, placeholder |
| Kernel entry, no log | Boot arguments, serial selection, framebuffer address |
| Panic naming a provider | ADT node, driver archive, kernel flag |
| No root | Userdata image, UUID, partition capacity |

## Next steps

- [Troubleshooting](/reference/troubleshooting)
- [QEMU testing](/reference/qemu)
- [Boot arguments](/xnu/boot-arguments)
