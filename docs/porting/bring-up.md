# Bring-up order

Bring-up proceeds in stages. Each stage has a visible result and a log line. Isolate one stage at a time.

## Stage 1: UEFI

Goal: the firmware reaches a UEFI shell, a boot menu or the UniXNU application.

Checks:

- The firmware volume size matches `[uefi_fd] size`.
- The boot image header matches the bootloader requirement.
- `fastboot boot boot.img` starts the firmware without a reset.
- The framebuffer shows output, or the serial port shows UEFI output.
- Block devices and the payload volume are visible.

Tools:

```sh
fastboot boot out/<board>/boot/boot.img
```

A firmware stall leaves the device in the bootloader. Start the same image again.

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

A kernel that stops before its video console draws the color bars instead. See [Color bars](/guide/debugging#color-bars).

A missing platform provider produces a panic that names the provider. Add the driver or correct the ADT.

## Stage 6: Storage and root

Goal: the block driver publishes the userdata partition, the volumes appear, and XNU mounts the root.

Checks:

- The storage driver logs the link speed and the command queue.
- The partition scheme publishes `OS` and `SystemOS`.
- The root volume UUID matches `root_match_volume_uuid`.
- The kernel mounts the root and starts `launchd`.

A root match failure leaves the kernel without a root device. Check the UUID, the window offsets and the partition capacity.

## Stage 7: Userland

Goal: `launchd` runs and the first user process reaches a visible state.

Checks:

- `launchd` starts from the root volume.
- The Data volume mounts.
- The display server or the console presents output.
- The boot progress layer records the last checkpoint.

Use `boot-progress=2` and the diagnostic boot arguments to see the last completed checkpoint.

## QEMU before hardware

The QEMU fixture tests UniXNU, DarwinBoot and the kernel entry without a device:

```sh
python3 scripts/qemu-entry/make-dt.py --armvirt --armcpu --smp 2 \
  --owned-memory-size 0x20000000 --output build/qemu.dtb

python3 package/Scripts/stage-esp.py -o out/esp \
  package/UniXNUPkg/Test/Qemu/esp \
  --put out/<board>/package/Build/Out/UniXNU.efi=EFI/BOOT/BOOTAA64.EFI

python3 package/Scripts/qemu-run.py out/esp \
  --log out/qemu.log --screenshot out/qemu.png \
  --expect "UNIXNU: menu: shown" --expect "DARWINBOOT:"
```

The QEMU runner boots an AArch64 `virt` machine with AAVMF, captures the serial log and can send keys to the emulated keyboard.

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
