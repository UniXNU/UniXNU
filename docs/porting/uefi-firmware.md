# UEFI firmware

The UEFI firmware port comes from Mu-Silicium. It supplies the services UniXNU and DarwinBoot use.

For repeated builds, save paths in [unixnu.local.toml](/reference/configuration#local-build-inputs). After changing boot arguments, rebuild the payload and boot image using the [argument workflow](/xnu/boot-arguments#apply-arguments). Follow the [green-bar diagnosis](/guide/debugging#green-bar) for a stall at loader handoff.

## Procedure {#procedure}

1. Prepare the device's Mu-Silicium checkout, [vendor inputs](#vendor-inputs) and submodules. Match `board.toml` to its [device configuration](#device-configuration), DSC and FD path.
2. Complete [required integration](#required-integration): add each module to the DSC/FDF and map its libraries. The payload needs its RAM-disk, DiskIo and FAT drivers.
3. Save the firmware path in local build configuration and run the [firmware build](#build). Confirm the output FD path and size.
4. Build the payload, then follow [boot-image integration](#boot-image-integration). Check `boot/boot.json` and the packaged payload before booting.
5. On the device, confirm the configured menu entry and DarwinBoot handoff using [verification](#verification). If the entry is absent, work through [payload discovery](#payload-discovery).

## Required integration

Build firmware from the UniXNU checkout after selecting the device:

```sh
./unixnu defconfig <device>_defconfig -D ../UniXNU-<device>
./unixnu build firmware --uefi ../uefi-<device>
```

The firmware needs all of these modules in its DSC `[Components]` and FDF firmware volume:

| Module | Purpose |
| --- | --- |
| `UniXNUPkg/Application/UniXNU/UniXNU.inf` | Boot menu and configuration reader |
| `UniXNUPkg/Driver/UniXNUDxe/UniXNUDxe.inf` | Firmware boot option registration |
| `DarwinBootPkg/Driver/DarwinBoot.inf` | XNU loader |
| `UniXNUPkg/Driver/UniXNURamDiskDxe/UniXNURamDiskDxe.inf` | Publish the Mu-Silicium FDT initrd as a read-only block device |
| `MdeModulePkg/Universal/Disk/DiskIoDxe/DiskIoDxe.inf` | Disk access for the filesystem driver |
| `FatPkg/EnhancedFatDxe/Fat.inf` | Expose the payload's FAT filesystem |

List each path directly under DSC `[Components]`; use `INF <path>` in the FDF. Map the shared driver's libraries in DSC `[LibraryClasses]`:

```ini
HobLib|MdePkg/Library/DxeHobLib/DxeHobLib.inf
FdtLib|MdePkg/Library/BaseFdtLib/BaseFdtLib.inf
```

Add `PartitionDxe` when the payload uses a partition table. The FAT driver also needs the platform's Unicode collation service. The reference firmware's `Include/DXE.inc` contains these dependencies.

`UniXNURamDiskDxe` is shared by devices using Mu-Silicium's FDT handoff. Its source is in UniXNU's `package/UniXNUPkg/Driver/UniXNURamDiskDxe/`. Board memory reservations and memory expansion remain in the firmware platform.

A supplied `.fd` must contain this integration and match the board's firmware base and size. `./unixnu bootimg --fd <file>` packages the supplied firmware. Rebuild the FD after changing its DSC, FDF or drivers.

Build the payload with the selected device's inputs, then pack the image:

```sh
./unixnu build payload --unique-chip-id <hex> --trust-cache <file> --data-ramdisk <seed>
./unixnu bootimg --uefi ../uefi-<device> --dtb /path/to/firmware.dtb
```

Use the options required by the device's payload profile. See [payload inputs](/concepts/payload).

## Firmware logs

Follow [log exporter integration](/porting/log-capture#firmware-setup) to add
Advanced Logger and `AdvancedLogDxe`, then enable the Tools menu. Use
[QR capture](/porting/log-capture#qr-logs) to save firmware output before storage
adaptation and kernel handoff.

## Payload discovery

The Android bootloader places the FAT payload in RAM and writes `/chosen/linux,initrd-start` and `linux,initrd-end` into the firmware FDT. Each property is a 32-bit or 64-bit big-endian address. The range must contain complete 512-byte sectors and remain reserved while UEFI uses it.

Mu-Silicium SEC preserves the incoming FDT address as a `UINT64` in the entry-argument HOB (`DAEE82E6-8090-4E72-BFB9-78C13CD4E359`). `UniXNURamDiskDxe` reads this handoff and publishes Block I/O. DiskIoDxe and the FAT driver expose `EFI_SIMPLE_FILE_SYSTEM_PROTOCOL`, allowing UniXNU to read `\EFI\UniXNU\unixnu.toml` and list its entries.

If the menu appears without the configured entries, check:

1. `boot/boot.json` reports a nonzero `ramdisk_bytes` value.
2. The FD contains `UniXNURamDiskDxe`, DiskIoDxe and the FAT driver.
3. The firmware FDT has valid initrd start and end properties.
4. The serial log contains `UNIXNURAMDISK: initrd block device` with a successful status.
5. The payload FAT volume contains `EFI/UniXNU/unixnu.toml` and its referenced files.

The RAM disk driver must be embedded in the firmware so the payload can be discovered before its configuration is read.

## Required services

| Service | Consumer |
| --- | --- |
| `EFI_GRAPHICS_OUTPUT_PROTOCOL` | UniXNU menu, DarwinBoot framebuffer handoff, XNU console |
| `EFI_SIMPLE_TEXT_IN_PROTOCOL` | UniXNU menu input |
| `EFI_SIMPLE_FILE_SYSTEM_PROTOCOL` | Configuration, payload and kernel files |
| `EFI_BLOCK_IO_PROTOCOL` | Userdata partition and block slices |
| `EFI_SERIAL_IO_PROTOCOL` | Logs on boards with a UART |
| `EFI_ACPI_TABLE_PROTOCOL` | Optional ACPI table injection |
| `EFI_FIRMWARE_VOLUME2_PROTOCOL` | UniXNUDxe boot option registration |

A board that lacks one of these services limits the stages it can run. Add the driver to the firmware volume or to the UniXNU payload before the dependent stage.

## Mu-Silicium layout

```
Mu-Silicium/
  BootShim/
    BootShim.S
  Resources/
    Configs/<device>.toml
    Scripts/mkbootimg.py
  Platforms/<Vendor>/<device>Pkg/
    <device>.dsc
    <device>.fdf
  Silicon/
  Common/
```

The UniXNU driver reads `Resources/Configs/<name>.toml` and `<device>.dsc`. It uses `Resources/Scripts/mkbootimg.py` for the boot image.

## Device configuration

`Resources/Configs/<device>.toml` supplies the addresses and image parameters:

```toml
[boot_shim]
requires_kernel_header = true

[uefi_fd]
base = 0x00000000
size = 0x000000

[boot_image_kernel]
kernel_compression = "gzip"
append_dtb = true

[boot_image]
header_version = 0
base = 0x00000000
kernel_offset = 0x8000
tags_offset = 0x1e00000
pagesize = 4096
```

| Key | Meaning |
| --- | --- |
| `boot_shim.requires_kernel_header` | The bootloader checks the ARM64 header at the start of the image |
| `uefi_fd.base` | Physical address where the firmware volume is loaded |
| `uefi_fd.size` | Exact firmware volume size |
| `boot_image_kernel.kernel_compression` | Compression of the shim and firmware volume |
| `boot_image_kernel.append_dtb` | Append the device tree to the kernel field |
| `boot_image.*` | Android boot image header parameters |

The firmware base and size are compiled into BootShim. They are also checked when the boot image is packed.

## DSC and FDF

The DSC lists the packages, libraries and components. The FDF places the components in the firmware volume.

UniXNU packages use `PACKAGES_PATH`:

```
{uefi}:{tree}/package:{tree}/drivers/DarwinBoot:{edk2}:...
```

`{uefi}` is the Mu-Silicium checkout, `{tree}` is the assembled build tree, and `{edk2}` is the Mu_Basecore checkout. The board file lists every package path.

UniXNU and DarwinBoot are included through their INFs:

```
UniXNUPkg/Application/UniXNU/UniXNU.inf
UniXNUPkg/Driver/UniXNUDxe/UniXNUDxe.inf
UniXNUPkg/Driver/UniXNURamDiskDxe/UniXNURamDiskDxe.inf
DarwinBootPkg/Driver/DarwinBoot.inf
```

Embed these modules in the firmware volume for an initrd payload. Place the configuration and kernel files in the payload FAT volume.

## Preflight

`[firmware] preflight` lists scripts in the build tree that run before the EDK II build. A preflight script checks vendor inputs, firmware partitions or board files. `--skip-preflight` skips them.

## Vendor inputs

A Mu-Silicium port needs the vendor binaries for the board, for example:

- UEFI DXE drivers for storage, display, input or power.
- ACPI tables.
- Firmware partition images.
- Configuration data.

The board preflight script validates the files and their hashes.

## Submodules and patches

Mu-Silicium uses submodules for shared trees. The board file lists the ones it needs:

```toml
[firmware]
submodules = ["Common/Mu", "Silicon/Silicium", "Silicon/Qualcomm"]
patches = ["Resources/MuPatches/Gic-Spurious.patch"]
```

A patch in `patches` is applied to the shared edk2 tree for the build and reverted afterwards. The driver checks each patch with `git apply --check` before applying it.

## Build

With the device repository selected:

```sh
./unixnu build firmware --uefi /path/to/Mu-Silicium
```

The driver:

1. Runs the preflight scripts.
2. Initializes the listed submodules.
3. Builds BaseTools when `GenFw` is absent.
4. Applies the board patches.
5. Runs EDK II `build` with the DSC, `AARCH64`, `CLANGPDB` and the board defines.
6. Reverts the patches.
7. Checks the firmware volume size and path.

The output path comes from `[firmware] fd`:

```toml
fd = "Build/<device>Pkg/{target}_CLANGPDB/FV/SILICIUM_UEFI.fd"
```

## External firmware builds

A firmware supplied with `./unixnu bootimg --fd <file>` needs the same DSC/FDF
modules, package paths, board defines and EDK II patches as the selected
`[firmware]` configuration. Check the [required integration](#required-integration)
and use the matching board configuration when packing the image.

## Boot image integration

`unixnu bootimg` compiles BootShim with the firmware base and size:

```sh
clang --target=aarch64-none-elf -c \
  -DFD_BASE=<base> -DFD_SIZE=<size> \
  -DREQUIRES_KERNEL_HEADER=<0 or 1> \
  BootShim/BootShim.S -o shim.o
```

It appends the firmware volume, compresses the pair with gzip, appends the device tree and packs the Android boot image.

## Verification

| Check | Method |
| --- | --- |
| Firmware volume size | The driver compares the output size with `[uefi_fd] size` |
| Shim header | The driver checks `ARM\x64` and the base and size fields |
| Boot image parts | The driver unpacks the image and compares every part |
| Menu | The serial log contains `UNIXNU:` lines |
| Payload | The menu lists the `xnu` entry and DarwinBoot logs the handoff |

## Adding a UEFI driver

A driver can live in the firmware volume or in the payload.

| Location | Build | Load |
| --- | --- | --- |
| Firmware volume | Add the INF to the DSC and FDF | Firmware dispatches it, or UniXNUDxe starts the application |
| Payload | Build a standalone `.efi` | `[[driver]]` in `unixnu.toml` or a kit |

See [UEFI drivers](/drivers/uefi-drivers) for the INF, entry point and injection details.

## Next steps

- [Device tree](/porting/device-tree)
- [Bring-up order](/porting/bring-up)
- [UEFI drivers](/drivers/uefi-drivers)
