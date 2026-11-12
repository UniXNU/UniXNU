# RamBlock

Start with the [adaptation procedure](/porting/platform) for board inputs, source changes, build integration and verification order.

Sparse RAM-backed block storage with optional persistent backing callbacks.

[Source repository](https://github.com/UniXNU/RamBlock).

RamBlock publishes Data images and persistent APFS root containers as block devices.
Its persistence interface uses `native_ufs_store` callbacks; the board supplies
the storage and reset policy.

## Direct mode

With the persistent store open read-write, changed pages live only in the store
window and the seed answers for the rest. Requests run concurrently: reads take
no lock, writes to the same pages never overlap, and a flush waits for the
writes in progress, so every bitmap bit on the medium names a durable page. With
cached store writes the store runs write back (`data-fua=1` selects write
through); a synchronize with no write since the last flush sends no command.

## APFS root container

With `root-container=1`, disk publication waits for IOBSD and a matching writable
persistent store. A missing or mismatched store leaves the disk unpublished.
`data-reset` does not reset the root container.

The whole-disk IOMedia uses the iBoot System Container content hint for Hardware
and xART discovery. `native_ram_block_root_device` identifies media backed by the
active writable root store.

## Integration

The catalog records implementation scope, hardware and OS requirements, board dependencies, revision, build stage, outputs, and runtime identifiers. The selected profile orders build commands by dependency.

```sh
./unixnu build kernel -D /path/to/device
```

[Component catalog](/reference/components)
