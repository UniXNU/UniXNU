# Build

`unixnu` is the build driver. It reads a device repository, resolves modules, assembles a build tree and runs each step.

## Quick start

```sh
git clone --recurse-submodules https://github.com/UniXNU/UniXNU
git clone --recurse-submodules https://github.com/UniXNU/UniXNU-sheng
git clone https://github.com/UniXNU/uefi-sheng
cd UniXNU

# For an existing clone:
git submodule update --init --recursive

./unixnu defconfig sheng_defconfig -D ../UniXNU-sheng
./unixnu fetch
./unixnu ipsw fetch
./unixnu build kernel
./unixnu build package
./unixnu build firmware --uefi ../uefi-sheng
./unixnu bootimg --uefi ../uefi-sheng --dtb /path/to/device.dtb
```

The device repository is remembered in `out/state.json` after the first `-D`.

The boot image is `out/<board>/boot/boot.img` with `out/<board>/boot/boot.json` next to it. Options follow the subcommand.

## macOS runner

The kernel, userdata and Data seed steps call Xcode, `hdiutil` and `diskutil`. A fork can run them on a GitHub macOS runner without a local Mac.

1. Fork the repository and enable Actions.
2. Add the repository secret `UNIXNU_UNIQUE_CHIP_ID` when the board requires a platform seed.
3. Run the `macOS build` workflow. Choose the device repository, ref, defconfig and steps.
4. Download the artifacts from the run.

| Input | Meaning |
| --- | --- |
| `device_repository` | Device repository as `owner/name` |
| `device_ref` | Ref of the device repository |
| `defconfig` | Defconfig name |
| `steps` | `kernel`, `kernel userdata` or `kernel userdata payload`. The default is `kernel userdata` |
| `ipsw_url` | Optional IPSW URL. An empty value uses `board.toml` |
| `pre_build` | Optional shell commands run in the UniXNU checkout before the kernel build. The device repository is at `DEVICE_DIR` |
| `trust_cache_url` | Optional trust cache bundle URL |
| `owner_trust_cache` | Treat the URL as an owner-signed bundle |
| `data_seed_url` | Optional Data seed URL |
| `grow_gib` | Grow the Data seed to this size |
| `skip_setup` | Mark Setup as done in the Data seed |
| `upload_userdata` | Upload the userdata image. The image is large |

Add the repository secret `UNIXNU_DEVICE_TOKEN` when the device repository is private.

A device archive chain that needs a bootstrap candidate, display ABI evidence or a staged kernelcache uses `pre_build`. Its commands run after `unixnu fetch` and before `unixnu build kernel`. The workflow removes the fetched IPSW, the fetched feeds and the staged firmware cache after the artifacts are uploaded.

A bootstrap candidate example:

```sh
./unixnu defconfig bootstrap_defconfig -D "$DEVICE_DIR"
./unixnu build kernel -D "$DEVICE_DIR"
mkdir -p out/<board>/tree/build/native-prelink
cp out/<board>/kernel/kernel.macho \
   out/<board>/tree/build/native-prelink/<candidate>.macho
```

The candidate names and the display or kernelcache inputs come from the device repository.

The workflow runs kernel, userdata and payload. Package, firmware and boot image steps run on any OS and stay outside the workflow. Public repositories use the free macOS runner quota. Private repositories consume Actions minutes.

## Commands

| Command | Action |
| --- | --- |
| `defconfig [NAME]` | Lists `configs/*_defconfig` of the device repository, or copies one to `out/<board>/.config`. |
| `fetch [NAME...] [--update]` | Fetches git sources and writes `unixnu.lock` in the device repository. `--update` ignores the lock. |
| `tree` | Resolves modules, fetches the references the steps need, and assembles `out/<board>/tree`. |
| `ipsw info` | Prints the product, build and every component of the target IPSW. |
| `ipsw fetch [COMPONENT...]` | Extracts the named components into `out/ipsw/<build>/`. |
| `build [kernel] [package] [firmware] [payload] [prelink]` | Runs the named steps. The default is all four steps. `prelink` repeats the prelink alone. |
| `build userdata [--dry-run]` | Builds the raw userdata image. This step is large and runs only when named. |
| `bootimg` | Packs BootShim, the firmware volume, the device tree and the optional payload into an Android boot image. |
| `status` | Prints the device, configuration and the origin of every module. |
| `clean` | Removes the board output and keeps fetched sources. |

## Common options

| Option | Meaning |
| --- | --- |
| `-D DIR` | Device repository. Remembered after the first use. |
| `--out DIR` | Output root. Default `out/` in this repository. |
| `-j N` | Parallel jobs. Default is `JOBS` or the CPU count. |
| `--target DEBUG\|RELEASE` | EDK II build target. Default `DEBUG`. |
| `--uefi DIR` | Mu-Silicium checkout for the device. |
| `--edk2 DIR` | Mu_Basecore checkout. |
| `--kernelcache FILE` | Original decompressed kernelcache. |
| `--kernel FILE` | Prelinked kernel Mach-O for the payload. |
| `--kernel-arg NAME[=VALUE]` | Extra kernel argument. A name already in `[payload] kernel_args` is replaced. Repeatable. |
| `--trust-cache FILE` | Trust cache bundle. |
| `--owner-trust-cache FILE` | Owner-signed bundle with the original caches and extra modules. Replaces `--trust-cache` and skips the board allow-list. |
| `--data-ramdisk FILE` | Data ramdisk seed. |
| `--skip-setup` | Marks Setup as done in a copy of the Data seed. Requires `--data-ramdisk`. |
| `--unique-chip-id HEX` | Platform seed for the device tree. |
| `--ipsw PATH_OR_URL` | Target IPSW, local or remote. |
| `--skip-preflight` | Skips the board preflight scripts of the firmware step. |
| `--dry-run` | Userdata only: check sizes and pins, write nothing. |

The environment variables `UNIXNU_DEVICE`, `UNIXNU_OUT`, `UNIXNU_UEFI`, `UNIXNU_EDK2`, `UNIXNU_KERNELCACHE`, `UNIXNU_DTB`, `UNIXNU_IPSW`, `UNIXNU_UNIQUE_CHIP_ID` and `JOBS` supply the same values.

## Steps

### defconfig

`defconfig` copies `configs/<name>_defconfig` from the device repository to `out/<board>/.config`. It parses the file to reject a malformed line before the build starts.

### fetch

`fetch` resolves every module and fetches the git sources. It uses a shallow, blobless clone with a cone sparse checkout. One clone exists per repository and ref. The commit of each source is written to `unixnu.lock` in the device repository. A later build uses the locked commit.

### tree

`tree` assembles `out/<board>/tree` with the layout the scripts expect:

```
tree/
  drivers/ kits/ patches/ refer/
  scripts/ package/
  build/ .cache/
```

Modules are symbolic links to their sources. Scripts are copied. The device `package/` appears as `kits/<board.kit>`. `.cache/firmware` links to the device repository's `.cache/firmware`, so every tree uses the same proprietary files.

### ipsw

The IPSW is read member by member. A remote IPSW is never downloaded as a whole. The zip directory and each needed member are read with HTTP range requests. Extracted members are cached in `out/ipsw/<build>/` and checked against the sha256 pins in `board.toml [ipsw.sha256]`.

The image must match `[ipsw]`: product, version, build, device class, chip ID and board ID.

### kernel

The kernel step:

1. Applies `patches/xnu` and `kits/NativePrelink/patches` to the pinned XNU source.
2. Runs `prepare-xnu-source.py` to restore omitted DriverKit headers.
3. Runs one XNU pass for the compile records when `startup.o.json` is absent. The pass may stop at the link.
4. Runs the archive builders in `[kernel] archives` order.
5. Builds XNU for `ARM64`, machine `BCM2837`, configuration `DEVELOPMENT`, iOS 17, and links the archives.
6. Prelinks the native kernel against the original kernelcache with `kits/NativePrelink`. A rebuild replaces the earlier candidate.

The kernelcache comes from the IPSW unless `--kernelcache` supplies one. The LZFSE payload of the `KernelCache` IM4P is decoded with macOS `compression_tool`, the arm64 slice is selected, and the result is checked against `[kernel.prelink] kernelcache_sha256`.

The output is `out/<board>/kernel/kernel.macho`.

### package

The package step builds `package/` with EDK II. The output is `out/<board>/package/Build/Out`. It contains `UniXNU.efi`, `UniXNUDxe.efi`, `HelloPayload.efi`, `SampleDriver.efi` and `XnuTest.efi`.

### firmware

The firmware step builds the device firmware from the Mu-Silicium checkout:

1. Runs the board preflight scripts.
2. Applies the board patches to the shared edk2 tree for the build, then reverts them.
3. Runs EDK II `build` with the board DSC and defines.

`FD_BASE`, `FD_SIZE` and `FD_BLOCKS` come from the Mu-Silicium device configuration. The firmware volume must match `[uefi_fd] size` from that configuration.

### payload

The payload step writes a FAT volume with:

- `EFI/UniXNU/unixnu.toml`
- `EFI/UniXNU/Payloads/kernel.macho`
- `EFI/UniXNU/Payloads/kernel.macho.adt`
- the optional `kernel.macho.trustcache`
- the optional `scratch-data.img`

The kernel command line comes from `[payload] kernel_args`. An extra `--kernel-arg NAME=VALUE` replaces the board argument with the same name. The volume is written with mtools without mounting. The output is `out/<board>/payload/payload.img` with `payload.json`.

`--owner-trust-cache` supplies an owner-signed bundle with the original caches and extra modules. It replaces `--trust-cache` and skips `[payload] trust_cache_sha256`.

`--skip-setup` marks Setup as done in a copy of the Data seed supplied with `--data-ramdisk`.

### userdata

The userdata step builds the raw image for the `userdata` partition. It holds the unchanged `OS` and `SystemOS` disk images of the IPSW behind the `SHNGROOT` manifest. The disk images are attached read-only with `hdiutil`. The output is `out/<board>/userdata/userdata-root.img` with `userdata-root.json`.

The report prints the `fastboot flash userdata` command.

### bootimg

The boot image step:

1. Compiles BootShim for the firmware base and size.
2. Appends the firmware volume.
3. Compresses the pair with gzip.
4. Appends the device tree after applying `[[bootimg.dtb_node]]`.
5. Packs the result with `mkbootimg.py` and the image parameters of the Mu-Silicium device configuration.
6. Unpacks the image and compares every part with its input.

The ramdisk is the payload output when it exists, `--ramdisk FILE`, or an empty ramdisk with `--ramdisk none`.

## Local modules

A module can come from a local directory. The first match wins:

1. `--local-module [KIND:]NAME=PATH`
2. `--local-drivers|kits|patches|scripts|package DIR`
3. `--local DIR`, a directory with this repository's layout
4. a `local = "DIR"` entry in `feeds.toml`, or `local.toml` in the device repository
5. the device repository
6. this repository
7. a git source in `feeds.toml`

Local modules are linked into the build tree. `unixnu status` marks them and reports that they are not pinned by the lock.

## Output

All output goes to `out/`:

| Path | Contents |
| --- | --- |
| `out/state.json` | Remembered device repository |
| `out/feeds/` | Fetched sources |
| `out/ipsw/<build>/` | Extracted IPSW members |
| `out/<board>/.config` | Selected defconfig |
| `out/<board>/tree/` | Assembled build tree |
| `out/<board>/logs/` | Step logs |
| `out/<board>/kernel/kernel.macho` | Prelinked kernel |
| `out/<board>/package/Build/Out/` | EFI binaries |
| `out/<board>/payload/` | Payload image and report |
| `out/<board>/boot/` | Boot image and report |
| `out/<board>/userdata/` | Userdata image and report |

## Reproducibility

`unixnu.lock` pins every fetched source. The firmware build sets `SOURCE_DATE_EPOCH` to the Mu-Silicium commit time, so EDK II does not embed the build time. The boot image is deterministic for a given firmware volume, device tree and ramdisk. The payload contains a random seed, so two payload builds differ.

## Next steps

- [Build the kernel](/guide/build-kernel) describes the kernel flags and archives.
- [Boot the image](/guide/boot) describes the fastboot commands.
- [Reference](/reference/output-layout) lists every report field.
