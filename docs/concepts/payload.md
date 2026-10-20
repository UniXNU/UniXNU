# Boot payload

The payload is a FAT volume that becomes the ramdisk of the Android boot image. UniXNU reads the configuration from it, and DarwinBoot reads the kernel, the ADT and the optional trust cache from it.

## Volume layout

```
/EFI/UniXNU/unixnu.toml
/EFI/UniXNU/Payloads/kernel.macho
/EFI/UniXNU/Payloads/kernel.macho.adt
/EFI/UniXNU/Payloads/kernel.macho.trustcache
/EFI/UniXNU/Payloads/scratch-data.img
```

The payload step writes the volume with `mformat` and `mcopy`. Timestamps are fixed at 1980-01-01, so the volume is reproducible for the same inputs. The ADT contains a random seed, so two payload builds differ.

## Configuration

The payload step writes this configuration:

```toml
version = 1

[boot]
timeout = 3
default = "xnu"

[kits]
autoload = false

[[entry]]
id = "xnu"
title = "UniXNU"
type = "xnu"
path = "Payloads/kernel.macho"
initrd = "Payloads/scratch-data.img"
args = "-v serial=3"
```

`initrd` is present when a Data seed is supplied. `args` is the joined `[payload] kernel_args` and `--kernel-arg` values.

## ADT sidecar

The ADT uses Apple's flattened node encoding. The board script named in `[payload.adt] tool` generates it. The payload step calls the tool with:

| Option | Source |
| --- | --- |
| `--output` | `Payloads/kernel.macho.adt` |
| `--dram-size` | `[payload] dram_size` |
| `--owned-memory-size` | `[payload.adt] owned_memory_size` |
| `--root-match-volume-uuid` | `[payload.adt] root_match_volume_uuid` |
| `--chip-id` | `[payload.adt] chip_id` |
| `--cpu-regs` | `[payload.adt] cpu_regs` |
| `--psci-method` | `[payload.adt] psci_method` |
| `--unique-chip-id` | `--unique-chip-id` or `UNIXNU_UNIQUE_CHIP_ID` |
| `--packed-data-ramdisk` | `[payload.adt] packed_data_ramdisk` |
| `--data-ramdisk` | a Data seed without packed delivery |
| `--trust-cache` | a trust cache bundle |
| `--owner-trust-cache` | an owner-signed bundle with the original caches and extra modules. It replaces `--trust-cache` and skips the board allow-list |
| `--ipad-identity` | `[payload.adt] ipad_identity` |

The ADT must reserve the following properties when the matching input exists:

| Property | Purpose |
| --- | --- |
| `/chosen/memory-map/RAMDisk` | DarwinBoot writes the ramdisk address and size |
| `/chosen/memory-map/PackedRAMDisk` | DarwinBoot writes the packed ramdisk address and size |
| `/chosen/memory-map/TrustCache` | DarwinBoot writes the trust cache address and size |
| `/chosen/darwinboot-memory-size` | Requests a contiguous window larger than 256 MiB |

DarwinBoot requires the placeholder to exist for every input it receives. A mismatch is `EFI_COMPROMISED_DATA`.

## Kernel arguments

The payload checks the command line before writing the volume:

- Every argument matches `[A-Za-z0-9_.\-]+` with an optional `=value` of `[A-Za-z0-9_.,\-]+`.
- An extra `--kernel-arg NAME=VALUE` replaces the board argument with the same name.
- The joined line is at most 1000 bytes. DarwinBoot copies it into a 1024-byte buffer.

The command line is stored in `unixnu.toml` as `args`. DarwinBoot copies it into `boot_args` without modification.

## Trust cache

The trust cache bundle is validated by DarwinBoot:

- A 32-bit count from 1 to 128.
- One offset table entry per cache.
- Every cache starts with version 2.
- Every entry is 24 bytes.
- Every hash type is 1 to 4.
- Hashes are sorted in ascending order.

The bundle is copied into the kernel window and its address and size replace the `TrustCache` placeholder.

An `--owner-trust-cache` bundle is copied without the `[payload] trust_cache_sha256` check. It carries the original caches and extra modules such as the GPU plugin.

## Data ramdisk

A Data seed can be delivered in two forms:

| Form | ADT placeholder | Behavior |
| --- | --- | --- |
| Dense | `RAMDisk` | DarwinBoot copies the whole image |
| Packed | `PackedRAMDisk` | DarwinBoot validates the `DBRDISK1` extent table and copies the extents |

The packed form carries a header with the magic `DBRDISK1`, version 1, the page size, the expanded size and an extent table of `(offset, length)` pairs. Omitted ranges are zeroed RAM.

`scripts/seed-data-grow.py` grows a packed seed to the tablet's storage. The kernel accepts a Data disk of up to 1 TiB, and above 2 GiB the typed provider keeps only the nonzero pages of the seed.

## Determinism

The boot image is deterministic for a given firmware volume, device tree and ramdisk. The ADT random seed makes each payload build differ. The payload report records the kernel, ADT, trust cache, Data seed and payload hashes.

## Next steps

- [Boot chain](/concepts/boot-chain) describes how the payload is consumed.
- [Boot configuration](/reference/boot-configuration) lists every `unixnu.toml` key.
- [Boot arguments](/xnu/boot-arguments) lists the kernel arguments.
