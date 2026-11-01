# Device configuration

Format 2 uses `schema_version = 2` at the top of `board.toml`. Files without
this field use format 1. See the [device repository specification](/porting/device-repository)
for profile ownership and examples.

## Local build inputs {#local-build-inputs}

Copy `unixnu.example.toml` to `unixnu.local.toml` in the UniXNU checkout and fill in your device paths. The file is ignored by Git. Use `--config /path/to/build.toml` to select another file.

```toml
[build]
device = "../UniXNU-<device>"
uefi = "../uefi-<device>"
dtb = "/path/to/firmware.dtb"
kernelcache = "/path/to/kernelcache"
trust_cache = "/path/to/trustcache.bundle"
data_ramdisk = "/path/to/data-seed.dbr"
unique_chip_id = "<hex>"
jobs = 8
target = "DEBUG"
kernel_args = ["-v", "serial=3", "debug=0x14e"]
```

Replace the placeholders with your port's inputs. Relative paths start at the configuration file's directory. Command-line flags take priority, followed by environment variables, then this file, then device defaults. `kernel_args` overrides board arguments by name; `--kernel-arg` overrides local arguments by name.

Supported path keys are `device`, `out`, `uefi`, `edk2`, `kernelcache`, `kernel`, `trust_cache`, `owner_trust_cache`, `data_ramdisk`, `gpu_addon`, `dtb`, `fd`, `ramdisk`, and `output`. Other keys are `ipsw` (path or URL), `unique_chip_id` (hex string), `jobs` (positive integer), `target` (`DEBUG` or `RELEASE`), and `kernel_args` (string array). `ramdisk = "none"` selects an empty boot-image ramdisk.

```sh
./unixnu defconfig <device>_defconfig
./unixnu kernel
./unixnu firmware
./unixnu payload
./unixnu bootimg
./unixnu status --json
```

`status` reports the selected file as `build_config`. Build inputs use `unixnu.local.toml`; module source overrides use the device repository's `local.toml`.

## Profile fields

| Table | Key | Meaning |
| --- | --- | --- |
| `board` | `soc_source` | Name of a pinned `kind = "soc"` source |
| `board` | `os_profile` | Directory under `profiles/os/` |
| `components` | `include` | Canonical component IDs; dependencies are resolved in build order |
| `kernel` | `config_fragments` | Ordered profile-relative configuration files |
| `kernel` | `patch_series` | Ordered profile-relative series files |
| `device_tree` | `source` | DTS entry point, such as `device:dts/sheng.dts` |
| `device_tree` | `include_dirs` | DTS include paths, such as `soc:dts` |

Layers apply as ARM64, SoC, OS, device. Tables merge by key; arrays replace.
The selected defconfig applies after `config_fragments`. File prefixes are
`arch:`, `soc:`, `os:`, and `device:`. Series entries also accept
`component:<ID>/path`. `unixnu status --json` reports the effective configuration.

## board.toml

### [board]

| Key | Type | Meaning |
| --- | --- | --- |
| `name` | string | Output directory name |
| `soc` | string | SoC identifier |
| `description` | string | Human readable description |
| `kit` | string | Device package folder under `kits/` |
| `example` | boolean | Marks a sample. Build and bootimg refuse it |

### [ipsw]

| Key | Type | Meaning |
| --- | --- | --- |
| `url` | string | Default remote IPSW |
| `product` | string | Product type, for example `iPad7,1` |
| `version` | string | Product version |
| `build` | string | Product build |
| `device_class` | string | Device class from the manifest |
| `chip_id` | integer | `ApChipID` |
| `board_id` | integer | `ApBoardID` |
| `fetch` | array | Components extracted by `ipsw fetch` |

### [ipsw.sha256]

| Key | Type | Meaning |
| --- | --- | --- |
| member file | string | Expected SHA-256 of the extracted member |

### [userdata]

| Key | Type | Meaning |
| --- | --- | --- |
| `first_lba` | integer | First LBA of the userdata GPT entry |
| `last_lba` | integer | Last LBA of the userdata GPT entry |
| `lba_bytes` | integer | Logical block size |
| `windows` | array | `{ name, component }` entries |

### [kernel]

| Key | Type | Meaning |
| --- | --- | --- |
| `defconfig` | string | File name under `configs/` |
| `archives` | array | Archive builder scripts of the build tree, run in order before the kernel link |

### [kernel.prelink]

| Key | Type | Meaning |
| --- | --- | --- |
| `tool` | string | Prelink tool path in the build tree |
| `kernel` | string | Native kernel path in the build tree |
| `slide` | string | Address slide |
| `roots` | array | Bundle identifiers kept from the kernelcache |
| `early_security_init` | string | `identifier=address` |
| `kernelcache` | string | Optional path to a local kernelcache |
| `kernelcache_sha256` | string | Expected kernelcache hash |
| `extra_args` | array | Extra prelink arguments |

### [firmware]

| Key | Type | Meaning |
| --- | --- | --- |
| `config` | string | Mu-Silicium `Resources/Configs/<name>.toml` |
| `dsc` | string | DSC path in the checkout |
| `fd` | string | Firmware volume path, `{target}` replaced |
| `packages` | array | `PACKAGES_PATH` entries |
| `preflight` | array | Preflight scripts in the build tree |
| `patches` | array | Patches applied to edk2 for the build |
| `submodules` | array | Mu-Silicium submodules to initialize |

### [firmware.defines]

| Key | Type | Meaning |
| --- | --- | --- |
| any | string | `-D NAME=VALUE` for the EDK II build |

### [bootimg.image]

| Key | Type | Meaning |
| --- | --- | --- |
| `base` | integer | Image base address |
| `kernel_offset` | integer | Kernel offset |
| `tags_offset` | integer | Tags offset |
| `pagesize` | integer | Image page size |
| `header_version` | integer | Android boot image header version |
| `kernel_compression` | string | `gzip` (default) or `none`; selects how the kernel is stored in the boot image |

### [[bootimg.dtb_node]]

| Key | Type | Meaning |
| --- | --- | --- |
| `path` | string | Device tree node path |
| `props` | array | `{ name, type, value }` |

Types are `s` for string, `x` for hex cells, `i` for decimal cells, `u` for unsigned cells and `empty`.

### [payload]

| Key | Type | Meaning |
| --- | --- | --- |
| `volume` | string | FAT label, at most 11 characters |
| `size_mib` | integer | Volume size |
| `loader` | string | `firmware` or a driver path mode |
| `title` | string | Menu title |
| `dram_size` | string | DRAM size for the ADT |
| `panic_screen` | boolean | Patch the panic screen into the payload kernel |
| `trust_cache_sha256` | array | Accepted trust cache hashes. An owner bundle passed with `--owner-trust-cache` skips this list |
| `kernel_args` | array | Default kernel arguments |
| `tools` | boolean | Add Tools to the generated menu; configure plugins with [log capture](/porting/log-capture#firmware-setup) |
| `timeout` | integer | Menu timeout |
| `skip_setup_tool` | string | Script used by `--skip-setup` |

### [payload.adt]

| Key | Type | Meaning |
| --- | --- | --- |
| `tool` | string | ADT generator path |
| `chip_id` | string | Chip ID for the ADT |
| `owned_memory_size` | string | Contiguous window request |
| `root_match_volume_uuid` | string | Root volume UUID |
| `cpu_regs` | string | CPU MPIDR values, comma separated |
| `psci_method` | string | `smc` or `hvc` |
| `packed_data_ramdisk` | boolean | Use the packed Data format |
| `ipad_identity` | boolean | Write the Apple device identity properties |
| `unique_chip_id` | string | `required` when the seed is mandatory |

## defconfig

```
CONFIG_NAME=y
CONFIG_NAME=n
CONFIG_NAME="text"
CONFIG_NAME=123
# CONFIG_NAME is not set
```

Each `CONFIG_XNU_<NAME>` becomes `XNU_<NAME>`. `{tree}` in a string becomes the build tree path.

## feeds.toml

```toml
[[source]]
name = "Name"
kind = "driver"          # driver, kit, patch, script, package, refer, soc
git = "https://github.com/ORG/REPO"
ref = "main"
path = "drivers/Name"
commit = "..."
local = "/path/to/local"
submodules = []
```

| Key | Meaning |
| --- | --- |
| `name` | Module name |
| `kind` | Module kind |
| `git` | Source repository |
| `ref` | Branch, tag or commit to fetch |
| `path` | Optional subdirectory, fetched sparse |
| `commit` | Optional pin |
| `local` | Local directory instead of git |
| `submodules` | Upstream submodules to initialize |

## local.toml

An ignored file in the device repository:

```toml
[local]
drivers = "/path/to/drivers"
kits = "/path/to/kits"
patches = "/path/to/patches"
scripts = "/path/to/scripts"
package = "/path/to/package"
```

## unixnu.lock

```toml
[source."Name"]
commit = "0123456789abcdef"
```

Written by `unixnu fetch` for Git sources. Format 2 gives an explicit source commit priority over the lock, including the selected OS XNU revision. Format 1 uses lock-first precedence. Official aliases can reuse lock entries recorded under their accepted source names.

## Module resolution

1. `--local-module [KIND:]NAME=PATH`
2. `--local-<kind> DIR`
3. `--local DIR`
4. a `local` key in `feeds.toml` or `local.toml`
5. the device repository
6. the base repository
7. a git source in `feeds.toml`

The first match wins.

## Next steps

- [Boot configuration](/reference/boot-configuration)
- [Device repository](/porting/device-repository)
- [Command line](/reference/cli)
