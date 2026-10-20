# Command line

```
./unixnu <command> [options]
```

Options follow the command. The driver reads a device repository from `-D`, `UNIXNU_DEVICE` or `out/state.json`.

## Commands

### defconfig

```
unixnu defconfig [NAME]
```

Lists `configs/*_defconfig` in the device repository. With a name, copies the file to `out/<board>/.config` and parses it.

### fetch

```
unixnu fetch [NAME...] [--update]
```

Updates the module submodules of this repository and the device repository, then fetches git sources. With names, fetches only those sources. `--update` ignores `unixnu.lock` and moves to the newest ref. Writes the commits to `unixnu.lock` in the device repository.

### tree

```
unixnu tree
```

Resolves modules, fetches the references the steps need, and assembles `out/<board>/tree`.

### ipsw

```
unixnu ipsw info
unixnu ipsw fetch [COMPONENT...]
```

`info` prints the product, build, device class and every manifest component with its size and path. `fetch` extracts the named components, or the `[ipsw] fetch` list when no component is named.

### build

```
unixnu build [kernel] [package] [firmware] [payload] [prelink] [userdata]
```

Runs the named steps in this order: kernel, prelink, package, payload, firmware. With no step, runs kernel, package, firmware and payload. `userdata` runs alone; `all` covers the other four.

`build prelink` repeats the prelink without rebuilding XNU.

`build kernel` runs the compile-record pass and the `[kernel] archives` builders before the link.

`build userdata --dry-run` checks the IPSW and the partition size.

### bootimg

```
unixnu bootimg [--fd FILE] [--dtb FILE] [--ramdisk FILE|none] [-o FILE]
```

Packs the boot image. The firmware volume defaults to the output under `--uefi`. The ramdisk defaults to the payload output when it exists.

### status

```
unixnu status
```

Prints the device, output root, configuration path and the origin of every module. Marks local modules and reports that they are not pinned.

### clean

```
unixnu clean
```

Removes `tree`, `logs`, `kernel`, `package`, `boot` and `edk2-conf` under the board output. Keeps fetched sources.

## Options

| Option | Meaning |
| --- | --- |
| `-D DIR`, `--device DIR` | Device repository |
| `--out DIR` | Output root |
| `-j N`, `--jobs N` | Parallel jobs |
| `--local DIR` | Local tree with this repository's layout |
| `--local-drivers DIR` | Local drivers directory |
| `--local-kits DIR` | Local kits directory |
| `--local-patches DIR` | Local patches directory |
| `--local-scripts DIR` | Local scripts directory |
| `--local-package DIR` | Local package directory |
| `--local-module [KIND:]NAME=PATH` | One local module. Repeatable |
| `--uefi DIR` | Mu-Silicium checkout |
| `--edk2 DIR` | Mu_Basecore checkout |
| `--kernelcache FILE` | Original decompressed kernelcache |
| `--skip-preflight` | Skips the board preflight scripts |
| `--kernel FILE` | Prelinked kernel for the payload |
| `--kernel-arg NAME[=VALUE]` | Extra kernel argument. A name already in `[payload] kernel_args` is replaced. Repeatable |
| `--trust-cache FILE` | Trust cache bundle |
| `--owner-trust-cache FILE` | Owner-signed bundle with the original caches and extra modules. Replaces `--trust-cache` and skips the board allow-list |
| `--skip-setup` | Marks Setup as done in a copy of the Data seed |
| `--data-ramdisk FILE` | Data ramdisk seed |
| `--unique-chip-id HEX` | Platform seed for the ADT |
| `--ipsw PATH_OR_URL` | Target IPSW |
| `--dry-run` | Userdata dry run |
| `--target DEBUG\|RELEASE` | EDK II target |
| `--fd FILE` | Firmware volume for bootimg |
| `--dtb FILE` | Compiled device tree for bootimg |
| `--ramdisk FILE\|none` | Ramdisk for bootimg |
| `-o FILE`, `--output FILE` | Boot image output |

## Environment

| Variable | Equivalent |
| --- | --- |
| `UNIXNU_DEVICE` | `-D` |
| `UNIXNU_OUT` | `--out` |
| `UNIXNU_UEFI` | `--uefi` |
| `UNIXNU_EDK2` | `--edk2` |
| `UNIXNU_KERNELCACHE` | `--kernelcache` |
| `UNIXNU_DTB` | `--dtb` |
| `UNIXNU_IPSW` | `--ipsw` |
| `UNIXNU_UNIQUE_CHIP_ID` | `--unique-chip-id` |
| `JOBS` | `-j` |

## Exit behavior

| Condition | Result |
| --- | --- |
| Missing device repository | Error with the `-D` hint |
| Missing configuration for a kernel build | Error with the `defconfig` hint |
| Missing Mu-Silicium checkout for firmware | Error before fetching |
| IPSW identity mismatch | Error naming the expected and actual image |
| sha256 pin mismatch | Error naming the member |
| Firmware volume size mismatch | Error naming the size |
| Payload larger than `size_mib` | Error with the size to raise |
| Invalid kernel argument | Error naming the argument |
| Kernel command line over 1000 bytes | Error naming the length and the limit |
| Missing platform seed | Error with the `--unique-chip-id` hint |
| Example device repository | Error before build or bootimg |

## Next steps

- [Device configuration](/reference/configuration)
- [Output layout](/reference/output-layout)
- [Troubleshooting](/reference/troubleshooting)
