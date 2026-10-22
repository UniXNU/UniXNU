# Device repository

A device repository describes one board and supplies the modules that differ from the generic tree.

## Layout

```
UniXNU-<device>/
  board.toml                  board description
  configs/<name>_defconfig    kernel configuration
  feeds.toml                  optional extra sources
  local.toml                  optional local source overrides, ignored by Git
  drivers/                    device XNU drivers
  kits/                       device kernel libraries
  patches/                    device patches
  scripts/                    build and bring-up scripts
  package/                    UniXNU kit contents
  .gitmodules                 module submodules
  .cache/firmware/            proprietary inputs, not tracked
  unixnu.lock                 written by unixnu fetch
```

The directory layout matches `UniXNU`. A module in the device repository overrides the module with the same name in the base repository. Device drivers and kits are independent repositories included as submodules.

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
| `name` | Output directory name under `out/` |
| `soc` | SoC identifier for reports and scripts |
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
windows = [
  { name = "OS", component = "OS" },
  { name = "SystemOS", component = "Cryptex1,SystemOS" },
]
```

`first_lba` and `last_lba` come from the GPT entry named `userdata`. `lba_bytes` is the logical block size. Each window names a disk image component from the IPSW.

### Kernel

```toml
[kernel]
defconfig = "<name>_defconfig"
archives = [
  "scripts/build-native-aes-bindings.py",
  "scripts/build-libpthread-kernel.py",
  "scripts/build-corecrypto-14.py",
  "scripts/build-corecrypto-14.py --namespace",
]

[kernel.prelink]
tool = "kits/NativePrelink/emit_prelink.py"
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
tool = "scripts/make-<device>-adt.py"
chip_id = "0"
owned_memory_size = "0x10000000"
root_match_volume_uuid = "00000000-0000-0000-0000-000000000000"
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

The `[payload.adt]` keys are passed to the ADT tool. The tool contract is device specific. The generic keys are documented in [Device tree](/porting/device-tree).

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

A device repository can add sources:

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

Kinds are `driver`, `kit`, `patch`, `package` and `refer`. `path` fetches only a subdirectory. `local` uses a local directory.

The base `feeds.toml` supplies `xnu`, `libplatform`, `libdispatch`, `AvailabilityVersions`, `edk2`, `libpthread` and `corecrypto-2023`.

## Proprietary files

The device repository keeps its proprietary inputs under `.cache/firmware`. The build tree links to that directory, so every tree and every rebuild uses the same files without copying them into the repository.

## Local development

The first match wins:

1. `--local-module [KIND:]NAME=PATH`
2. `--local-<kind> DIR`
3. `--local DIR`
4. a `local` key in `feeds.toml` or an entry in `local.toml`
5. the device repository
6. the base repository
7. a git source in `feeds.toml`

A local module is linked into `out/<board>/tree`. `unixnu status` marks it and reports that the lock does not pin it.

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

The `[match]` keys are all required. Within one key, any listed value matches. A kit that does not match is skipped and counted in the menu summary.

## Next steps

- [UEFI firmware](/porting/uefi-firmware)
- [Device tree](/porting/device-tree)
- [Device configuration reference](/reference/configuration)
- [Devices](/devices/)
