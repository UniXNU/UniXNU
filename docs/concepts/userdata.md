# Userdata layout

The userdata partition carries the Darwin root file system. UniXNU keeps the original disk images unchanged and adds a manifest that maps each image to a window in the partition.

## Manifest

```
struct shngroot_header {
  char     magic[8];        /* "SHNGROOT" */
  uint32_t version;         /* 1 */
  uint32_t count;           /* window count */
  uint64_t image_bytes;     /* total image size */
  struct {
    char     name[32];
    uint64_t offset;
    uint64_t size;
    uint32_t block_size;    /* 512 */
    uint32_t flags;         /* bit 0: read-only */
    uint8_t  sha256[32];
    uint8_t  reserved[40];
  } window[count];
  uint8_t  reserved[32];
  uint8_t  manifest_sha256[32];
};
```

The header occupies 4096 bytes and is zero padded to 1 MiB. The first window starts at 0x100000. Every window is aligned to 1 MiB.

## Windows

| Window | IPSW component | Contents |
| --- | --- | --- |
| `OS` | `OS` | The system volume |
| `SystemOS` | `Cryptex1,SystemOS` | The cryptex system volume |

The images are copied byte for byte from the disk images in the IPSW. The userdata step reads the raw disk of each disk image: on macOS it attaches the image read-only with `hdiutil` and reads the raw device, on Linux `scripts/unixnu/udif.py` decodes the UDIF chunks. The OS image is a UDIF image with LZFSE chunks; the SystemOS cryptex is a raw image and is copied as it is.

## Capacity

The partition capacity is:

```
(last_lba - first_lba + 1) * lba_bytes
```

The step refuses an image larger than the capacity. The report records the capacity and the image size.

## Root matching

XNU selects the root volume through `/chosen/root-matching`:

```xml
<dict>
  <key>IOProviderClass</key><string>IOMedia</string>
  <key>IOPropertyMatch</key>
  <dict>
    <key>UUID</key><string>00000000-0000-0000-0000-000000000000</string>
  </dict>
</dict>
```

The UUID is the volume UUID of the OS window. The native block driver publishes the userdata partition, the partition scheme publishes the volumes, and XNU matches the UUID.

## Data volume

The writable Data volume is separate from the userdata image. It comes from the Data ramdisk seed in the payload. The seed is an input to the payload step, and the payload report records its hash.

The kernel accepts a Data disk of up to 1 TiB. Above 2 GiB the typed block provider keeps only the seed's nonzero pages, so memory use follows the content rather than the disk size. The seed identity hashes the size and the nonzero pages with their index.

The persistent store serves the disk from a window at the end of the userdata partition. Writes use forced unit access, so a page is on the medium when its command completes. The store stays clear of the root image and the log reserve. `sheng-log-reserve=<MiB>` sets that reserve, 1024 MiB by default. `sheng-data-persist=1` proves the window read-only, and `sheng-data-persist=2` opens it for writes.

`scripts/seed-data-grow.py` grows the APFS container of a packed seed to a chosen size or to the tablet's userdata partition. The output keeps only the nonzero pages and the volume UUID. A different size starts the Data volume over. The kernel refuses a seed whose store window does not fit the real partition.

`--skip-setup` writes a copy of the seed with the Setup preferences marked as done. The copy is cached by the seed hash.

## Report

`userdata-root.json` records:

| Field | Meaning |
| --- | --- |
| `image_bytes` | Total image size |
| `image_sha256` | Image hash |
| `manifest_sha256` | Manifest hash |
| `windows` | Name, offset, size and hash of each window |
| `userdata_bytes` | Partition capacity |
| `flash_command` | `fastboot flash userdata <image>` |
| `source` | Local or remote IPSW |
| `hardware_tested` | Qualification state |

## Next steps

- [Userdata image](/guide/userdata) describes the build and flash commands.
- [Device configuration](/reference/configuration) lists the `[userdata]` keys.
- [Boot chain](/concepts/boot-chain) describes how the volume is mounted.
