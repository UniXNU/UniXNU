# Device configuration

A device repository has four configuration files: `board.toml`, `configs/<name>_defconfig`, `feeds.toml` and `local.toml`.

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
kind = "driver"          # driver, kit, patch, package, refer
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

Written by `unixnu fetch`. A build uses the locked commit. The lock records git sources only.

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
