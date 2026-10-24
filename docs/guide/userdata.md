# Userdata image

The userdata image supplies the root file system to XNU. It holds the unchanged `OS` and `Cryptex1,SystemOS` disk images from the target IPSW behind a manifest that the kernel reads.

Prepare the selected IPSW and the device GPT values. On Linux, install the [Linux toolchain](/guide/requirements#linux), which provides `lzfse`. Growing the Data seed (step 4) needs macOS `hdiutil` and `diskutil`. Select the device and save local inputs using [Build and boot](/building) first.

## 1. Check partition geometry {#partition}

`board.toml` describes the GPT entry:

```toml
[userdata]
first_lba = 0x2f3840
last_lba = 0x3d0abfa
lba_bytes = 4096
windows = [
  { name = "OS", component = "OS" },
  { name = "SystemOS", component = "Cryptex1,SystemOS" },
]
```

`first_lba` and `last_lba` come from the GPT entry named `userdata` on the device. `lba_bytes` is the logical block size of the partition.

The image size is the sum of the windows, each aligned to 1 MiB, plus the 1 MiB header region. The step rejects an image larger than the partition.

## 2. Preview and build the image {#build}

```sh
./unixnu build userdata --ipsw /path/to/restore.ipsw --dry-run
./unixnu build userdata --ipsw /path/to/restore.ipsw
```

The step extracts the IPSW components named in `[userdata] windows`, reads each disk image with `hdiutil` on macOS or `scripts/unixnu/udif.py` on Linux, and writes a raw image to `out/<device>/<os_profile>/<config>/userdata/userdata-root.img`.

The report `userdata-root.json` records the window offsets, sizes and hashes, the partition capacity and the flash command.

Review the dry-run capacity and window layout before running the second command. Completion produces the image and its report.

## 3. Set the root UUID {#root-selection}

The kernel mounts the root volume by UUID:

```toml
[payload.adt]
root_match_volume_uuid = "REQUIRED_ROOT_VOLUME_UUID"
```

Use the APFS root volume UUID from the selected OS image. On macOS, inspect the attached image with `diskutil apfs list`; match the root volume to the image's container and copy its Volume UUID. Rebuild the payload and boot image after changing it.

The ADT generator writes a `/chosen/root-matching` dictionary with `IOProviderClass = IOMedia` and the UUID. The native block driver publishes the userdata partition, the partition scheme publishes the volumes, and XNU selects the IOMedia with the matching UUID.

## 4. Prepare the Data volume {#data-volume}

The writable Data volume comes from the Data ramdisk seed in the payload. The seed is an input to the payload step:

```sh
./unixnu build payload --data-ramdisk data.img
```

For sheng's persistent-store layout, the macOS growth tool can resize a seed:

```sh
python3 scripts/seed-data-grow.py --gib 8 /path/to/data.dbr /path/to/data-grow.dbr
```

Choose a size that fits the target Data allocation after root windows, store
metadata and log reservations. The tool attaches the raw image with `hdiutil`
and resizes APFS with `diskutil`; it writes a new packed seed. Its accepted size
range is 3 to 1024 GiB.

`--auto` additionally reads the script tree's
`build/userdata-root/userdata-root.json` (or `.img`) and queries fastboot for
userdata capacity. Supply that report from the same target before using this
mode. `--userdata-bytes BYTES` replaces the capacity query; `--reserve-mib`
selects the log reserve. The default reserve is 1024 MiB.

The volume UUID is preserved, but changing the seed size changes its persistence
identity and initializes a new Data store. Record the selected size and root
report with the image. On another board, first adapt and verify the storage
allocation described in [UFS porting](/porting/ufs).

`--skip-setup` marks Setup as done in a copy of the seed. The payload report records the seed hash and the resulting image hash. See [Skip Setup](/guide/skip-setup) for the preference changes.

## 5. Flash and boot {#flash}

Flashing `userdata` overwrites that partition. Confirm the target device, its partition geometry and the report's image path, and save any data needed from that partition before running the command.

```sh
fastboot devices
fastboot flash userdata out/<device>/<os_profile>/<config>/userdata/userdata-root.img
```

After a successful flash, [boot the matching image](/guide/boot#start-the-image) and record the root-mount result.

The driver prints the command in the report. The device repository can provide a wrapper script that checks the image and partition before flashing.

## Layout

```
0x000000  SHNGROOT manifest, 4096 bytes, zero padded to 1 MiB
0x100000  OS window, whole disk image
....      SystemOS window, whole disk image
```

The manifest is little endian:

| Offset | Field |
| --- | --- |
| 0 | `SHNGROOT` |
| 8 | version, 32-bit, value 1 |
| 12 | window count, 32-bit |
| 16 | image size, 64-bit |
| 24 | window entries, 128 bytes each |
| 4064 | SHA-256 of bytes 0 to 4063 |

Each window entry contains a 32-byte name, a 64-bit offset, a 64-bit size, a 32-bit block size, a 32-bit flags field, a 32-byte SHA-256 and 40 reserved bytes.

## Next steps

- [Userdata layout](/concepts/userdata) explains the manifest and the disk windows.
- [Boot the image](/guide/boot) covers the first boot.
- [Device configuration](/reference/configuration) lists every `[userdata]` key.
