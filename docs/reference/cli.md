# Command line

```
./unixnu <command> [options]
```

Options follow the command. The driver reads a device repository from `-D`, `UNIXNU_DEVICE`, the local build file, or `out/state.json`.

`kernel`, `package`, `firmware`, `payload`, `prelink`, and `userdata` are shortcuts for `build <step>`. Save paths and boot arguments in [unixnu.local.toml](/reference/configuration#local-build-inputs), then run `./unixnu kernel`, `./unixnu firmware`, `./unixnu payload`, and `./unixnu bootimg`. `--config FILE` selects another local build file. `status --json` includes its path in `build_config`.

## Commands

### defconfig

```
unixnu defconfig [NAME]
```

Lists `configs/*_defconfig` in the device repository. With a name, merges the ordered profile fragments and the selected file into `out/<device>/<os_profile>/<config>/.config` and parses it.

### fetch

```
unixnu fetch [NAME...] [--update]
```

Updates the module submodules of this repository and the device repository, then fetches git sources. With names, fetches only those sources. `--update` ignores the recorded lock when resolving refs. Explicit format 2 source commits retain priority. Writes the commits to `unixnu.lock` in the device repository.

### tree

```
unixnu tree
```

Resolves modules, fetches the references the steps need, and assembles `out/<device>/<os_profile>/<config>/tree`.

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

Runs userdata first when selected, then kernel (including prelink), package, payload and firmware. A standalone `prelink` runs when kernel is not selected. The default and `all` select kernel, package, payload and firmware. Use separate commands in [Building](/building) to inspect each artifact.

`build prelink` repeats the prelink without rebuilding XNU.

`build kernel` prepares the ordered patches, runs the compile-record pass, and builds selected component recipes plus `[kernel] archives` commands before linking. `component:<ID>` marks a component recipe position.

`build userdata --dry-run` checks the IPSW and the partition size.

### bootimg

```
unixnu bootimg [--fd FILE] [--dtb FILE] [--ramdisk FILE|none] [-o FILE]
```

Packs the boot image. The firmware volume defaults to the output under `--uefi`. The ramdisk defaults to the payload output when it exists.

### vendor_boot

```
unixnu vendor_boot --stock FILE [--ramdisk FILE|none] [--ramdisk-addr ADDR] [--verify-against] [-o FILE]
```

Rewrites the vendor ramdisk of a stock `vendor_boot` v4 image. The device tree, the ramdisk table, the bootconfig and the vbmeta blob are copied verbatim and the AVB footer is retargeted, so only the ramdisk and the sizes that depend on it change. `--ramdisk-addr` relocates the ramdisk when the stock window is too small for the payload. `--verify-against` repacks the stock ramdisk first and refuses a device whose layout does not reproduce its own image byte for byte. The output defaults to `vendor_boot.img` next to `--stock`.

### status

```
unixnu status [--json]
```

Prints the device, output path, profile roots, component scope, source revisions, local overrides, and patch order. `--json` emits `schema_version`, `device`, `name`, `output`, `configuration`, `config_path`, `configured`, `profiles`, `configuration_sources`, `board`, `components`, `modules`, and `patch_order`. Status reads cached or local SoC sources; run `fetch` to obtain a missing source.

### clean

```
unixnu clean
```

Removes `tree`, `logs`, `kernel`, `package`, `boot` and `edk2-conf` under the board output. Keeps fetched sources.

### release

```
unixnu release [--os VERSION] [--no-deps] [--check]
```

Runs the fixed steps `deps`, `preflight`, `patches`, `build`, `pack` and `verify` for the device, then writes `package.manifest.json`. The device repository's `scripts/package.sh` calls it. See [Device packaging script](/porting/packaging).

## Options

| Option | Meaning |
| --- | --- |
| `-D DIR`, `--device DIR` | Device repository |
| `--os VERSION` | OS profile for this run: `17`, `26`, `27` or a `profiles/os` directory name. The output directory follows it |
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
| `--stock FILE` | Stock vendor_boot image for vendor_boot |
| `--ramdisk-addr ADDR` | Ramdisk load address for vendor_boot |
| `--verify-against` | Repack the stock ramdisk and require a byte-identical result |

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
