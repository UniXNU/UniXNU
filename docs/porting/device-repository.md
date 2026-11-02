# Device repository

Complete [steps 1 through 4 of Port a device](/porting/steps) before using this field reference. Then continue with [hardware and driver adaptation](/porting/drivers).

A device repository selects shared SoC and OS support and describes one board.
Read the [component catalog](/reference/components) before adding a driver.

## Layout

```text
UniXNU-<device>/
  AGENTS.md
  README.md
  .gitignore
  board.toml
  porting.toml
  .github/workflows/porting-record.yml
  .github/workflows/package.yml
  feeds.toml
  configs/<device>_defconfig
  dts/<device>.dts
  patches/xnu/series
  scripts/package.sh
  proprietary-files.txt
  package/
  local.toml.example
  unixnu.lock
```

`local.toml` contains local overrides. `unixnu fetch` writes source pins to
`unixnu.lock`. Component sources come from the catalog, feeds, or local
checkouts. `package/` appears as `kits/<board.kit>` in the assembled tree.
Copy `local.toml.example` to the ignored `local.toml` for machine-specific
overrides. Commit `unixnu.lock` after fetching the selected sources.

## Complete the repository {#completion}

New ports and migrated ports follow the same requirements below. Hardware
values, component selections and verification levels describe the target board.
The [new-port workflow](/porting/steps) and [migration guide](/porting/migration)
both finish here.

### 1. Complete the tracked files

Use the layout above. For an existing repository, add missing template files
and update existing files in place. Review these groups:

| Files | Required result |
| --- | --- |
| `board.toml` | Format 2 board configuration; matching device name, SoC and OS profile; completed hardware inputs; `board.example` absent or false |
| `porting.toml` | Format 1 device record, so `schema_version` stays `1`; device name, SoC and OS profile match `board.toml` |
| `feeds.toml`, `unixnu.lock`, `.gitmodules` when used | Reviewed source URLs and commits for the SoC, components and submodules; local overrides recorded separately |
| `configs/`, `patches/xnu/series` | Existing defconfig selected by `kernel.defconfig`; complete ordered configuration and patch lists; every referenced file present |
| `dts/` | Board DTS selected by `device_tree.source`, with the chosen SoC include, board resources and reservations |
| `package/`, board code and build recipes | Selected components and board services have build recipes, startup integration and required OS ABI inputs |
| `proprietary-files.txt`, firmware configuration | Required firmware sources and hashes, DSC/FDF integration, partition geometry and image inputs |
| `porting.toml`, `.github/workflows/porting-record.yml` | Every selected component and dependency covered by an area; actual source, host and device results; record check enabled |
| `.github/workflows/package.yml` | The packaging action of [the packaging script](/porting/packaging) |
| `README.md`, `AGENTS.md` | Board scope, prerequisites, build commands and links to the common guides and device record |
| `.gitignore`, `local.toml.example` | Local override file and generated output directories ignored; example paths documented |

Use the [component catalog](/reference/components) for shared implementations
and [driver adaptation](/porting/drivers) for board interfaces. Fill the template's
`REQUIRED_` values and zero RAM range from hardware sources. Record pending
implementation and verification in the corresponding `porting.toml` areas.

### 2. Resolve and verify

Run from the main UniXNU checkout. Set the device path and its actual defconfig:

```sh
DEVICE_DIR=../UniXNU-myboard
DEFCONFIG=myboard_defconfig
./unixnu defconfig "$DEFCONFIG" -D "$DEVICE_DIR"
./unixnu fetch -D "$DEVICE_DIR"
./unixnu status --json -D "$DEVICE_DIR"
./unixnu tree -D "$DEVICE_DIR"
python3 scripts/porting-record.py check --device "$DEVICE_DIR"
```

Inspect the resolved ARM64, SoC, OS and device profiles, component revisions,
overrides and patch order. The output path is
`out/<device>/<os_profile>/<config>/`, and the device package appears under
`tree/kits/<board.kit>/`. The record checker reports the number of structured
areas checked. Resolve each reported error before publication.

Compile the [board DTS](/porting/device-tree), then follow
[Building](/building) for kernel, package, firmware, payload and boot image.
The repository also carries the [device packaging script](/porting/packaging)
that produces the same two artifacts from a clean checkout with no edit.
Record each command, revision, output and result. Record hardware checkpoints
separately using [bring-up](/porting/bring-up) and [log capture](/porting/log-capture).
Assign each area its supported [completion level](/porting/records#completion-levels).

### 3. Publish and label the repository {#publish}

1. Review the device diff and commit the completed files and source pins. For
   a new repository, initialize Git with `git -C "$DEVICE_DIR" init -b main`
   before committing. Keep local paths in the ignored `local.toml`.
2. Publish the commit to your GitHub repository. With authenticated GitHub CLI,
   create a new public repository from the committed directory:

   ```sh
   REPOSITORY=YOUR_OWNER/UniXNU-myboard
   gh repo create "$REPOSITORY" --public --source "$DEVICE_DIR" --remote origin --push
   ```

   For an existing repository, push the reviewed branch to its configured remote.
   Set `REPOSITORY` to that repository's `OWNER/NAME` for the following commands.
3. Add the **`unixnu` GitHub topic** and verify it:

   ```sh
   gh repo edit "$REPOSITORY" --add-topic unixnu
   gh repo view "$REPOSITORY" --json repositoryTopics --jq '.repositoryTopics[].name'
   ```

   The output must include `unixnu`. In GitHub's web interface, use the repository's
   **About** settings to edit **Topics**. The topic makes ports discoverable at
   [github.com/topics/unixnu](https://github.com/topics/unixnu).
4. Confirm the porting-record workflow passes on the published commit. Official
   device branches require its `Porting record` check.
5. Publish `board.toml` and a valid `porting.toml`. The twice-daily catalog
   workflow pins the source and generates the format 2 page and navigation.
   Follow [record publication](/porting/records#publishing-and-reuse) to request
   a scan or preview locally. Confirm the [device page](/devices/) links to the
   published revision.

**Result:** a published device repository with pinned sources, reproducible
commands, a checked porting record, CI, common-guide links and the `unixnu` topic.

## Profiles

```toml
schema_version = 2

[board]
name = "sheng"
soc = "SM8550"
soc_source = "sm8550"
os_profile = "ipados-17.7.11-21H461"
kit = "sheng"

[components]
include = ["ArmDTPlatform", "ArmCpu", "Adreno740", "AdrenoMetal", "ShengUfs", "ShengHidInput", "ShengNovatekTouch", "GopFramebuffer"]

[device_tree]
source = "device:dts/sheng.dts"
include_dirs = ["soc:dts"]
```

The resolver reads these layers in order:

1. `UniXNU/profiles/arch/arm64/profile.toml`
2. The selected SoC repository's `soc.toml`
3. `UniXNU/profiles/os/<os_profile>/profile.toml`
4. Device `board.toml`

Tables merge by key. Ordinary arrays replace the inherited array. Component
dependencies are added in build order. Use `unixnu status --json` to inspect
the resolved settings, sources, overrides, and patch order.

Files without `schema_version` use format 1 and its module paths. Format 2
outputs use `out/<device>/<os_profile>/<config>/`, where `<config>` is the
defconfig name with `_defconfig` removed.

## board.toml

### Board

```toml
[board]
name = "<device>"
soc = "<SoC>"
description = "<device description>"
kit = "<kit>"
# example = true
```

| Key | Meaning |
| --- | --- |
| `name` | Device name in the output path |
| `soc` | SoC identifier for reports and scripts |
| `soc_source` | Pinned source of kind `soc` in `feeds.toml` |
| `os_profile` | Directory name under `UniXNU/profiles/os/` |
| `description` | Human readable description |
| `kit` | Folder name of the device package under `kits/` |
| `example` | Marks a sample repository. `build` and `bootimg` refuse it |

### IPSW

```toml
[ipsw]
url = "https://example.invalid/restore.ipsw"
product = "<product>"
version = "<version>"
build = "<build>"
device_class = "<device class>"
chip_id = 0x0000
board_id = 0

fetch = ["KernelCache", "DeviceTree", "StaticTrustCache", "Cryptex1,SystemTrustCache"]

[ipsw.sha256]
"<member file>" = "<sha256>"
```

`url` is the default source. `--ipsw` or `UNIXNU_IPSW` overrides it. The image must match the product, version, build, device class, chip ID and board ID.

`fetch` lists the components that `unixnu ipsw fetch` extracts with no arguments.

`[ipsw.sha256]` pins member hashes by member file name. The IPSW reader checks every extracted member against its pin.

### Userdata

```toml
[userdata]
first_lba = 0x0
last_lba = 0x0
lba_bytes = 4096
```

`first_lba` and `last_lba` come from the GPT entry named `userdata`. `lba_bytes` is the logical block size.

The OS profile lists the IPSW disk images in `[userdata] windows`. A window with `optional = true` is skipped when the IPSW does not have it.

### Kernel

```toml
[kernel]
defconfig = "<name>_defconfig"
archives = [
  "build-software-aes-bindings.py",
  "build-libpthread-kernel.py",
  "build-corecrypto-14.py",
  "build-corecrypto-14.py --namespace",
]

[kernel.prelink]
tool = "kits/XnuPrelink/emit_prelink.py"
kernel = "build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/mach.development.bcm2837.unstripped.noctf"
kernelcache_sha256 = "..."
slide = "-0x1000000"
early_security_init = "com.apple.driver.AppleMobileFileIntegrity=0xfffffff005ab4ae0"
roots = [
  "com.apple.driver.AppleARMPlatform",
  "com.apple.filesystems.apfs",
]
extra_args = []
```

| Key | Meaning |
| --- | --- |
| `defconfig` | File name under `configs/` |
| `archives` | Archive builder scripts, run in order before the kernel link |
| `tool` | Prelink tool path in the build tree |
| `kernel` | Native kernel path in the build tree |
| `kernelcache_sha256` | Pins the original kernelcache |
| `slide` | Address slide applied to the selected components |
| `early_security_init` | Component identifier and address for the early initializer |
| `roots` | Bundle identifiers kept from the original kernelcache |
| `extra_args` | Additional arguments for the prelink tool |

### Ordered configuration and patches

```toml
[kernel]
defconfig = "sheng_defconfig"
config_fragments = ["arch:configs/common.config", "soc:configs/sm8550.config"]
patch_series = ["arch:patches/xnu/series", "soc:patches/xnu/series", "os:patches/xnu/series", "device:patches/xnu/series"]
```

Configuration fragments apply in list order, followed by the selected device
defconfig. A later value replaces the earlier value for that key. Each series
lists patches in application order, one per line; `#` starts a comment. Relative
paths resolve from the series directory. Prefixes `arch:`, `soc:`, `os:`, and
`device:` select their profile roots. `component:<ID>/path` selects a component
file. The kernel build applies the resolved sequence to target-local XNU sources.

### Firmware

```toml
[firmware]
config = "<name>"
dsc = "Platforms/<Vendor>/<device>Pkg/<device>.dsc"
fd = "Build/<device>Pkg/{target}_CLANGPDB/FV/SILICIUM_UEFI.fd"
preflight = ["scripts/check-<device>.py"]
submodules = []
patches = ["Resources/MuPatches/<patch>.patch"]
packages = [
  "{uefi}",
  "{tree}/package",
  "{tree}/drivers/DarwinBoot",
  "{edk2}",
]

[firmware.defines]
DEVICE_MODEL = "<device>"
```

| Key | Meaning |
| --- | --- |
| `config` | `Resources/Configs/<name>.toml` in the Mu-Silicium checkout |
| `dsc` | DSC path, relative to the checkout |
| `fd` | Firmware volume path. `{target}` becomes `DEBUG` or `RELEASE` |
| `preflight` | Scripts in the build tree, run before the firmware build |
| `submodules` | Mu-Silicium submodules the board needs |
| `patches` | Patches applied to the shared edk2 tree for the build, then reverted |
| `packages` | `PACKAGES_PATH` entries. `{uefi}`, `{edk2}` and `{tree}` are replaced |
| `defines` | Extra `-D` definitions for the EDK II build |

### Boot image

```toml
[bootimg.image]
base = 0x0
kernel_offset = 0x8000
tags_offset = 0x1e00000
pagesize = 4096
header_version = 0

[[bootimg.dtb_node]]
path = "/reserved-memory/<region>"
props = [
  { name = "label", type = "s", value = "<label>" },
  { name = "reg", type = "x", value = ["0x0", "0x80000000", "0x0", "0x100000"] },
]
```

The image parameters default to the Mu-Silicium device configuration. `[bootimg.image]` overrides them. Each `[[bootimg.dtb_node]]` adds a node or property to the UEFI device tree before it is appended to the boot image. The stock bootloader sometimes requires a splash region or another reserved-memory node.

### Payload

```toml
[payload]
volume = "<label>"
size_mib = 192
loader = "firmware"
title = "UniXNU"
dram_size = "0x80000000"
panic_screen = true
skip_setup_tool = "scripts/seed-data-skip-setup.py"
trust_cache_sha256 = ["<sha256>"]
timeout = 3

kernel_args = ["-v", "serial=3"]

[payload.adt]
chip_id = "0"
owned_memory_size = "0x10000000"
root_match_volume_uuid = "REQUIRED_ROOT_VOLUME_UUID"
cpu_regs = "0,0x100"
psci_method = "smc"
packed_data_ramdisk = true
ipad_identity = true
unique_chip_id = "required"
```

| Key | Meaning |
| --- | --- |
| `volume` | FAT volume label, at most 11 characters |
| `size_mib` | Volume size |
| `loader` | `firmware` when DarwinBoot is in the firmware volume |
| `title` | Menu entry title |
| `dram_size` | DRAM size passed to the ADT tool |
| `panic_screen` | Patches the panic screen into the payload copy of the kernel |
| `entry_probe_reset_*` | Keeps the entry probe's timed reset, optionally after a given call (see [Debugging](/guide/debugging)) |
| `skip_setup_tool` | Script used by `--skip-setup` |
| `skip_setup_args` | Extra arguments for that script, such as `["--no-auto-dim"]` |
| `trust_cache_sha256` | Accepted trust cache bundle hashes |
| `timeout` | Menu timeout in seconds |
| `kernel_args` | Default kernel command line |

`--owner-trust-cache` supplies an owner-signed bundle with the original caches and extra modules. It replaces `--trust-cache` and skips `trust_cache_sha256`.

Format 2 uses `[device_tree]` and the common ADT generator. `[payload.adt]` supplies payload inputs. The selected OS profile supplies Apple identity. Format 1 uses its declared `tool`. See [Device tree](/porting/device-tree).

## Defconfig

`configs/<name>_defconfig` uses the same syntax as a Linux defconfig:

```
CONFIG_XNU_ARM_DT_PLATFORM=y
CONFIG_XNU_ARMCPU=y
CONFIG_XNU_NATIVE_UFS=y
CONFIG_XNU_NATIVE_CS_HASH_CACHE=y
# CONFIG_XNU_ARMVIRT_PLATFORM is not set
CONFIG_XNU_CRYPTO_BOOTSTRAP="prelinked"
CONFIG_XNU_OWNER_DATA_VOLUME_UUID="00000000-0000-0000-0000-000000000000"
CONFIG_XNU_OWNER_CACHE_VOLUME_UUID="00000000-0000-0000-0000-000000000000"
```

Values can be `y`, `n`, a number or a quoted string. Each `CONFIG_XNU_<NAME>` becomes `XNU_<NAME>` in the kernel build. `{tree}` in a string becomes the build tree path.

`CONFIG_XNU_OWNER_CACHE_VOLUME_UUID` names the SystemOS cryptex volume that the owner chain mounts as the cache carrier: the APFS volume UUID inside the image the signed SystemOS policy covers. Without it the kernel uses the sheng image's volume.

The file name is selected by `[kernel] defconfig`.

## feeds.toml

A device repository pins its SoC source and can add component sources:

```toml
[[source]]
name = "sm8550"
kind = "soc"
git = "https://github.com/UniXNU/UniXNU-sm8550-common"
commit = "<40-character SoC commit>"
```

```toml
[[source]]
name = "DeviceKit"
kind = "kit"
git = "https://github.com/ORG/REPO"
ref = "main"
path = "kits/DeviceKit"
commit = "..."
local = "~/Code/device-kit"
```

Kinds are `driver`, `kit`, `patch`, `script`, `package`, `refer` and `soc`. `path` fetches only a subdirectory. `local` uses a local directory.

The base `feeds.toml` supplies `xnu`, `libplatform`, `libdispatch`, `AvailabilityVersions`, `edk2`, `libpthread` and `corecrypto-2023`.

## Proprietary files

`proprietary-files.txt` records each required firmware file, source, and hash. The device repository keeps its proprietary inputs under `.cache/firmware`. The build tree links to that directory, so every tree and every rebuild uses the same files without copying them into the repository.

## Local development

The first match wins:

1. `--local-module [KIND:]NAME=PATH`
2. `--local-<kind> DIR`
3. `--local DIR`
4. a `local` key in `feeds.toml` or an entry in `local.toml`
5. the device repository
6. the selected SoC repository
7. the base repository
8. a git source in `feeds.toml`

Format 2 accepts source overrides in the device's `local.toml`:

```toml
[[source]]
kind = "soc"
name = "sm8550"
local = "../UniXNU-sm8550-common"
```

Relative local paths resolve from the containing configuration file. `~`
and environment variables expand before path resolution.

A local module is linked into `out/<device>/<os_profile>/<config>/tree`. `unixnu status` identifies its local source path.

## Package and kits

The device `package/` becomes `kits/<board.kit>` in the build tree. The package can contain a `unixnu.toml`, kit directories, drivers, device tree overlays and kext bundles.

A kit directory has a `Kit.toml`:

```toml
schema = 1

[kit]
name = "<kit>"
version = "1.0.0"
description = "<description>"

[match]
arch = "AARCH64"
fdt_compatible = ["<compatible>"]
firmware_vendor = ["<vendor>"]
requires_protocol = ["<guid>"]

[[driver]]
file = "<driver>.efi"
args = "<load options>"

[[overlay]]
file = "<overlay>.dtbo"

[[kext]]
bundle = "<name>.kext"
entry = "<entry id>"
```

Every supplied `[match]` key must match. Within one key, any listed value matches. A kit that does not match is skipped and counted in the menu summary.

## Next steps

- [UEFI firmware](/porting/uefi-firmware)
- [Device tree](/porting/device-tree)
- [Device configuration reference](/reference/configuration)
- [Devices](/devices/)

## Porting record

`porting.toml` sits beside `board.toml`. Every area contains development findings,
evidence and completion criteria. Its identity and component coverage match the
board configuration and catalog dependencies. Device CI checks findings or
evidence updates for changed code paths. See the [record guide](/porting/records)
for fields, status levels and publication.

Board driver submodules belong to the device repository. sheng pins ShengUfs,
ShengHidInput, ShengNovatekTouch and ShengPreflight there.
