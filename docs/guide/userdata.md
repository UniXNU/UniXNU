# Userdata image

The userdata image supplies the root file system to XNU. It holds the unchanged `OS` and `Cryptex1,SystemOS` disk images from the target IPSW behind a manifest that the kernel reads.

## Build

```sh
./unixnu build userdata --ipsw /path/to/restore.ipsw
```

The step extracts the IPSW components named in `[userdata] windows`, reads each disk image with `hdiutil`, and writes a raw image to `out/<board>/userdata/userdata-root.img`.

The report `userdata-root.json` records the window offsets, sizes and hashes, the partition capacity and the flash command.

A dry run checks the IPSW and the partition size without writing the image:

```sh
./unixnu build userdata --dry-run
```

## Partition

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

## Flash

```sh
fastboot flash userdata out/<board>/userdata/userdata-root.img
```

The driver prints the command in the report. The device repository can provide a wrapper script that checks the image and partition before flashing.

## Root selection

The kernel mounts the root volume by UUID:

```toml
[payload.adt]
root_match_volume_uuid = "00000000-0000-0000-0000-000000000000"
```

The ADT generator writes a `/chosen/root-matching` dictionary with `IOProviderClass = IOMedia` and the UUID. The native block driver publishes the userdata partition, the partition scheme publishes the volumes, and XNU selects the IOMedia with the matching UUID.

## Data volume

The writable Data volume comes from the Data ramdisk seed in the payload. The seed is an input to the payload step:

```sh
./unixnu build payload --data-ramdisk data.img
```

A seed can grow to the tablet's storage without mounting a volume:

```sh
python3 scripts/seed-data-grow.py --auto data.dbr data-grow.dbr
```

`--auto` reads `fastboot getvar partition-size:userdata`, subtracts the root image, a 4 MiB guard, the log reserve and the store header and bitmap, rounds down to a whole GiB and keeps 1 GiB free. It needs `build/userdata-root/userdata-root.json` from the userdata build and a tablet in fastboot, unless `--userdata-bytes` is given. `--gib N` sets the size directly, `--userdata-bytes BYTES` skips the fastboot query, and `--reserve-mib` overrides the 1024 MiB log reserve. The accepted range is 3 to 1024 GiB.

The grown output keeps only the nonzero pages, so it is about as large as the input. The volume UUID is unchanged. The seed identity covers the size, so a different size starts the Data volume over. The kernel refuses a seed whose store window does not fit the real userdata partition.

The kernel accepts a Data disk of up to 1 TiB. The typed block provider holds only the nonzero pages of the seed, and the persistent store writes changed pages through to the end of the userdata partition with forced unit access.

`--skip-setup` marks Setup as done in a copy of the seed. The payload report records the seed hash and the resulting image hash. See [Skip Setup](/guide/skip-setup) for the preference changes.

## Next steps

- [Userdata layout](/concepts/userdata) explains the manifest and the disk windows.
- [Boot the image](/guide/boot) covers the first boot.
- [Device configuration](/reference/configuration) lists every `[userdata]` key.
