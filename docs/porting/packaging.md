# Device packaging script

**Mandatory for every device repository.** A device repository carries one
packaging script that produces its boot image and its payload from a clean
checkout, with no argument and no edit. Other device repositories copy this
page's structure. They fill in configuration values, never the script.

## Rules

1. **One command, one result.** `scripts/package.sh` in the device repository
   builds both artifacts. A second run on the same sources produces byte
   identical outputs.
2. **Configuration comes from TOML.** The script reads `board.toml` and the
   referenced `feeds.toml`, profile and local file. It contains no device name,
   path, size, kernel argument or version as a literal. A value the script
   needs but the TOML does not carry is added to `board.toml` first.
3. **The script is shared, not per device.** Device repositories use the same
   script text. Boards differ only in their TOML values. A change to the flow
   is made once and adopted by every device repository.
4. **The build target is a parameter.** One branch serves every OS profile.
   `--os` selects iOS or iPadOS 17, 26 or 27 for that run. There is no per
   target branch, and no second copy of a driver, patch or optimization for a
   second target.
5. **Every step is named and checked.** A step that fails stops the run with
   its name and the command's output. A step that is skipped says so.

## Structure

The script runs these steps in this order. Each one is a function with the
step's name, and each prints a header line before it runs.

| Step | Does | Reads |
| --- | --- | --- |
| `deps` | Clones or updates UniXNU, the device repository, its modules and the UEFI repository; checks each pinned revision | `feeds.toml`, `.gitmodules`, `unixnu.lock` |
| `preflight` | Runs the board's checks and resolves the profiles | `board.toml`, `--os` |
| `patches` | Lists the resolved patch series in application order, then applies it | `patch_series`, profile series |
| `build` | Builds each stage in dependency order, stopping at the first failure | `components`, `kernel`, `firmware` |
| `pack` | Writes the two artifacts and their manifest | `bootimg`, `payload` |
| `verify` | Checks the artifacts against the manifest and reports sizes | the manifest |

## Interface

```sh
scripts/package.sh [--os 17|26|27|PROFILE] [--device DIR] [--out DIR] [--jobs N] [--no-deps] [--check]
```

| Option | Meaning |
| --- | --- |
| `--os` | OS profile for this run. Defaults to `board.os_profile` |
| `--device` | Device repository. Defaults to the directory holding the script |
| `--out` | Output root. Defaults to `out/` in the UniXNU checkout |
| `--jobs` | Parallel jobs for the compile steps |
| `--no-deps` | Skips `deps`, for a machine whose sources are already fetched and pinned |
| `--check` | Runs `deps`, `preflight`, `patches` and `verify` only, and reports what would change |

Every option maps onto a `unixnu` argument. The script adds no logic of its own
to a step that `unixnu` already performs.

## Required outputs

The run writes these files, and the manifest names each one with its size and
SHA-256.

| Output | Contents |
| --- | --- |
| `out/<device>/<os_profile>/<config>/boot.img` | Android boot image: shim, firmware volume, device tree, payload ramdisk |
| `out/<device>/<os_profile>/<config>/payload.img` | The payload volume the boot image carries |
| `out/<device>/<os_profile>/<config>/kernel.macho` | The prelinked kernel the payload boots |
| `out/<device>/<os_profile>/<config>/package.manifest.json` | Build id, OS profile, resolved revisions, patch series, output sizes and hashes |

The boot image must fit the bootloader's partition and the kernel command line
must stay under 1000 bytes. The script refuses both cases before it writes an
image.

## Verification

A packaging run counts as complete when `verify` passes: both artifacts exist,
their hashes match the manifest, the kernel command line is within its limit,
and the boot image is not larger than the partition it is booted from. Booting
the artifact is a separate step with its own record.

## Adoption

For a device repository without the script:

1. Copy `scripts/package.sh` from the reference device repository.
2. Fill `board.toml` until `--check` reports no missing value.
3. Record the outputs in the device's `porting.toml` packaging area.
4. Add the run to the build documentation.

[Build and boot](/building), [Device repository](/porting/device-repository)
