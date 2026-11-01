# Device packaging script

**Mandatory for every device repository.** A device repository carries
`scripts/package.sh`, which produces the boot image and the payload of the
device from a clean checkout in one command. Every device repository holds the
same script text. A board changes `board.toml`, never the script.

## Rules

1. **One command.** `scripts/package.sh` runs the fixed steps below and writes
   the outputs and a manifest. It stops at the first failing step and names it.
2. **Configuration comes from TOML.** The script and `unixnu release` contain no
   device name, path, size, kernel argument or version. The values are read from
   `board.toml` (and the profiles and feeds it selects). A value that is missing
   is added to `board.toml` first.
3. **The script is fixed.** `templates/package.sh` in the UniXNU repository is the
   only source. A device repository copies it unchanged. The one board value it
   reads itself is `[package] unixnu`, the path of the UniXNU checkout.
4. **The build target is a parameter.** One branch serves every OS profile.
   `--os 17|26|27|PROFILE` selects the profile for the run. The values that differ
   per profile sit in `board.toml` under `[os_overrides."<profile>"]`; there is no
   branch and no second copy of a driver, patch or optimization per target.
5. **Sources are pinned.** `deps` fetches only the revisions that `feeds.toml`,
   `.gitmodules` and `unixnu.lock` name.

## Steps

`unixnu release` runs these steps in order and prints a `step <name>` line before each.

| Step | Does | Reads |
| --- | --- | --- |
| `deps` | Fetches the module submodules and git sources, writes `unixnu.lock`, extracts the IPSW members the board lists | `feeds.toml`, `.gitmodules`, `[ipsw]` |
| `preflight` | Selects the defconfig of the OS profile and writes the configuration | `[package.defconfig]`, `[kernel]` |
| `patches` | Resolves and lists the patch series in application order | `[kernel] patch_series` |
| `build` | Builds kernel, package, payload and firmware in dependency order | `[components]`, `[kernel]`, `[firmware]`, `[payload]` |
| `pack` | Packs the boot image from the firmware volume, the device tree and the payload | `[bootimg]`, `[device_tree]` |
| `verify` | Writes the manifest and checks the outputs against it | the outputs |

## Interface

```sh
scripts/package.sh [--os 17|26|27|PROFILE] [--no-deps] [--check] [unixnu options]
```

| Option | Meaning |
| --- | --- |
| `--os` | OS profile for this run. Defaults to `[board] os_profile` |
| `--no-deps` | Skips the `deps` step, for a machine whose sources are fetched and pinned |
| `--check` | Runs `deps`, `preflight` and `patches`, prints the patch list and stops before any build |

Any other `unixnu` option (`--uefi`, `--kernelcache`, `--dtb`, `--out`, `-j`) is passed on.
Local inputs that are not in a repository come from `unixnu.local.toml`.
The platform seed (`--unique-chip-id HEX` or `UNIXNU_UNIQUE_CHIP_ID`) and the firmware checkout (`--uefi DIR` or `UNIXNU_UEFI`) are not stored in any repository; the firmware step passes `UNIXNU_UEFI` to the board's preflight scripts.

## On GitHub

The device repository carries `.github/workflows/package.yml`. It runs
`scripts/package.sh` on a macOS runner, with the UniXNU and uefi-sheng
checkouts beside the device repository, and offers `boot.img`, `payload.img`,
`kernel.macho` and `package.manifest.json` as the run's artifacts.

The run installs its tools itself (Homebrew dtc, llvm, lld, cmake, mtools and
the ipsw tap for the AEA keys) and asserts them before the build. The board
names the official firmware archive in board.toml `[firmware.image]`; the run
downloads it with concurrent HTTP ranges, keeps only the named inputs, deletes
the archive and generates the binary modules the firmware volume builds from.

Run it in a fork of the device repository:

1. Fork the device repository and set its secret `UNIXNU_UNIQUE_CHIP_ID` to the
   platform seed of the device (8 hex digits). The seed is in no repository and
   the images bake it, so they serve that device alone.
2. Actions, package, Run workflow, and pick the OS profile.
3. Download the artifacts, then delete the run (`gh run delete`). The artifacts
   are boot images of one device and are not kept.

## board.toml keys

```toml
[package]
unixnu = "../UniXNU"

[package.defconfig]
"ipados-27.0.1-24A446" = "<device>_ipados27_defconfig"

[os_overrides."ipados-17.7.11-21H461".kernel]
archives = [ ... ]
remove = [ ... ]
```

| Key | Meaning |
| --- | --- |
| `[package] unixnu` | Path of the UniXNU checkout, relative to the device repository |
| `[package.defconfig]` | Defconfig for each OS profile; `release` uses it |
| `[package] boot_partition_bytes` | Optional. `verify` refuses a larger `boot.img` |
| `[bootimg] dtb` | Device tree of the boot image, relative to the build tree. A firmware preflight script builds it |
| `[os_overrides."<profile>"]` | Tables merged over the board for that profile only |
| `remove` in an override | Dotted keys the board sets for other profiles and this one does not |

## Outputs

All paths are under `out/<device>/<os_profile>/<config>/`. The manifest records the size and
SHA-256 of each file, the resolved revision of every module, the patch order and the length
of the kernel command line.

| Output | Contents |
| --- | --- |
| `boot/boot.img` | Android boot image: shim, firmware volume, device tree, payload ramdisk |
| `payload/payload.img` | The FAT payload volume the boot image carries |
| `kernel/kernel.macho` | The prelinked kernel the payload boots |
| `package.manifest.json` | The manifest |

## Verification

`verify` fails when an output is missing or differs from the manifest, when the kernel
command line reaches 1000 bytes, or when `boot.img` exceeds `boot_partition_bytes`.
Booting the artifacts is a separate step with its own record.

## Adoption

1. Copy `templates/package.sh` to `scripts/package.sh` in the device repository.
2. Add `[package]` and `[package.defconfig]` to `board.toml`, and `[os_overrides]` for each other profile.
3. Run `scripts/package.sh --check --os <profile>` for every profile and fix what it reports.
4. Record the run in the `packaging` area of `porting.toml`.

[Build and boot](/building), [Device repository](/porting/device-repository)

## Runtime inputs for sheng iPadOS 27

The payload's `runtime` table enables preparation before kernel compilation.
Apple static/System/App trust modules come from the selected IPSW unchanged. Turnip,
AdrenoMetal and the board audio HAL are built from source; their CDHashes are
appended as a separate owner trust module. Wallpaper overlays come from the
read-only OS image. The official Xiaomi fastboot archive still supplies the
firmware inputs through the board preflight scripts.

An existing installation must reuse its original `data.dbr` with
`--data-ramdisk FILE`. GPU and audio updates travel in the addon and do not edit
that seed. The runtime step checks its APFS volume UUID against the generated
kernel configuration and records the input SHA-256 values in the package manifest.
A payload-only build refuses a different Data UUID and asks for a kernel rebuild.

For a **first installation**, `scripts/package.sh --os 27 --init-data` creates an
APFS seed from the IPSW's initial `private/var`, uses the board's `data_gib` and
Setup preferences, and binds the new UUID into the kernel configuration. This
writes host build files only; it does not erase or flash a device. Keep the seed
at `out/sheng/ipados-27.0.1-24A446/sheng_ipados27/runtime/data.dbr` for every later
build of that installation. Its content identity, not just its UUID, identifies
the persistent Data store. Regenerating it cannot preserve an older installation.

The package workflow restores this seed from an installation cache, or accepts
an original seed URL with a required SHA-256. A missing cache stops the build
unless `init_data` is explicitly selected. The workflow uploads a separate seed
backup with one-day retention. Download and retain it: Actions caches are not a
permanent backup. The current device's seed is not supplied by either firmware
archive. Automatic runtime generation currently targets the iPadOS 27 profile.

`--gpu-addon FILE` and its matching `--owner-trust-cache FILE` remain available
for reproducing an existing image. Omit both to compile the addon and generate
its trust bundle. These generated binaries and installation seeds are not Git
inputs.

For the 24A446 fileset, `regression_policy` bounds the unresolved references by
original kernel address and importing component. New gaps fail packaging even
with `--allow-missing`; this check does not qualify the remaining experimental
paths or replace a device boot test.
