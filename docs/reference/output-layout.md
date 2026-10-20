# Output layout

All build output goes under `out/`. The driver writes nothing into the repositories except `unixnu.lock` in the device repository.

## Tree

```
out/
  state.json
  feeds/
  ipsw/<build>/
  <board>/
    .config
    tree/
    logs/
    kernel/
      kernel.macho
    package/
      Build/Out/
    payload/
      payload.img
      payload.json
    boot/
      boot.img
      boot.json
    userdata/
      userdata-root.img
      userdata-root.json
```

## state.json

```json
{
  "device": "/path/to/device/repository"
}
```

The driver reads the device repository from this file when `-D` and `UNIXNU_DEVICE` are absent.

## feeds

A clone per git repository and ref:

```
out/feeds/<repo>-<hash>/
```

The hash covers the URL and the ref. The clone is shallow, blobless and sparse when the source declares a path.

## ipsw

```
out/ipsw/<build>/
  <member file>
  <member file>.json
```

The sidecar records the component, member path, size, SHA-256 and source. A cached member is reused when its size and hash match the pin.

## tree

The assembled build tree:

```
tree/
  drivers/
  kits/
  patches/
  refer/
  scripts/
  package/
  build/
  .cache/
```

Module directories are symbolic links. `scripts/` is copied. The device package appears as `kits/<board.kit>`. `.cache/firmware` is a symbolic link to the device repository's `.cache/firmware`.

## logs

One log per step:

| File | Step |
| --- | --- |
| `kernel.log` | XNU build |
| `kernel-bootstrap.log` | First XNU pass for the compile records |
| `archive-NN-<name>.log` | Archive builder `NN` from `[kernel] archives` |
| `prelink.log` | Prelink |
| `package.log` | EDK II package build |
| `firmware-preflight.log` | Board preflight |
| `firmware.log` | EDK II firmware build |
| `basetools.log` | EDK II BaseTools build |
| `payload.log` | Payload volume |
| `payload-adt.log` | ADT generator |
| `payload-patch.log` | Panic screen patch |
| `payload-skip-setup.log` | Setup skip |
| `userdata.log` | Userdata image |

## boot.json

| Field | Meaning |
| --- | --- |
| `kernel_sha256` | Kernel field hash |
| `ramdisk_bytes` | Ramdisk size |
| `header_version` | Android boot image header version |
| `kernel_address` | Kernel load address |
| `tags_address` | Tags load address |
| `image_sha256` | Boot image hash |
| `image_bytes` | Boot image size |
| `fd_sha256` | Firmware volume hash |
| `dtb_sha256` | Device tree hash |
| `shim_bytes` | BootShim size |
| `hardware_tested` | Qualification state |

## payload.json

| Field | Meaning |
| --- | --- |
| `kernel_sha256` | Input kernel |
| `payload_kernel_sha256` | Kernel in the payload |
| `adt_sha256` | ADT sidecar |
| `kernel_args` | Command line |
| `trust_cache_sha256` | Trust cache bundle |
| `data_ramdisk_sha256` | Data seed |
| `skip_setup` | Setup skip applied |
| `panic_screen` | Panic screen patch applied |
| `payload_sha256` | Payload image hash |
| `payload_bytes` | Payload image size |
| `hardware_tested` | Qualification state |

## userdata-root.json

| Field | Meaning |
| --- | --- |
| `image_bytes` | Image size |
| `image_sha256` | Image hash |
| `manifest_sha256` | Manifest hash |
| `windows` | Name, offset, size and hash per window |
| `userdata_bytes` | Partition capacity |
| `flash_command` | Fastboot command |
| `source` | Local or remote IPSW |
| `hardware_tested` | Qualification state |

## Clean

`unixnu clean` removes `tree`, `logs`, `kernel`, `package`, `boot` and `edk2-conf` under the board output. Fetched sources and extracted IPSW members stay.

## Next steps

- [Build](/building)
- [Command line](/reference/cli)
- [Troubleshooting](/reference/troubleshooting)
