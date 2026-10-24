# Build and boot

`unixnu` resolves ARM64, SoC, OS, and device profiles, selects component dependencies, assembles a target tree, and runs each build step. Format 2 uses `out/<device>/<os_profile>/<config>/`. Format 1 uses `out/<board>/`.

::: warning Required firmware integration
Build the device firmware with `./unixnu build firmware --uefi ../uefi-<device>` before packing the boot image. Its DSC and FDF must include UniXNU, UniXNUDxe, DarwinBoot and the payload volume driver. For the Mu-Silicium FDT initrd path, use the shared `UniXNURamDiskDxe` with DiskIoDxe and FAT support. Follow [firmware integration](/porting/uefi-firmware#required-integration).
:::

## 1. Prepare the host and repositories {#quick-start}

Read [Requirements](/guide/requirements), then choose a port from
[Devices](/devices/). New ports follow [Port a device](/porting/) first.
Obtain the port's device and UEFI repositories, including their submodules.
For example, sheng uses:

```sh
git clone --recurse-submodules https://github.com/UniXNU/UniXNU
git clone --recurse-submodules https://github.com/UniXNU/UniXNU-sheng
git clone --recurse-submodules https://github.com/UniXNU/uefi-sheng
cd UniXNU
./unixnu defconfig sheng_defconfig -D ../UniXNU-sheng
./unixnu fetch
./unixnu status --json
```

Use your port's repository and defconfig names. `status` reports the effective
profiles, revisions, patch order and output directory. `-D` is remembered in
`out/state.json`. Run subsequent commands from the main UniXNU checkout.

**Expected result:** the intended device/configuration and resolved source paths.

## 2. Save and obtain build inputs {#saved-build-inputs}

```sh
cp unixnu.example.toml unixnu.local.toml
```

Fill the local file using [local build configuration](/reference/configuration#local-build-inputs).
Set the device and UEFI paths, firmware DTB, platform identity and required
kernelcache, trust-cache and Data seed inputs. Use the board's inventory;
[sheng build inputs](/porting/migration#build-inputs) lists its additional SDK,
firmware and ABI requirements.

```sh
./unixnu ipsw info
./unixnu ipsw fetch
./unixnu tree
```

`ipsw info` must show the OS build selected by the profile. `ipsw fetch` extracts
the configured members into `out/ipsw/<build>/`. Device firmware, Data seeds and
ABI audit inputs have their own preparation steps. Check those before building
a recipe that consumes them.

## 3. Build the kernel, package and firmware {#build-artifacts}

```sh
./unixnu build kernel
./unixnu build package
./unixnu build firmware
```

Run each command after the preceding one succeeds. [Kernel preparation](/guide/build-kernel)
explains archive/ABI requirements and prelink. [Firmware integration](/porting/uefi-firmware#required-integration)
explains the required DSC/FDF modules.

| Step | Expected output |
| --- | --- |
| Kernel | `<output>/kernel/kernel.macho` and build/prelink logs |
| Package | `<output>/package/Build/Out/AARCH64-DEBUG/UniXNU.efi` for the default target |
| Firmware | The FD path selected by `[firmware] fd` inside the UEFI checkout |

`<output>` is the directory printed by `status`. `--target RELEASE` changes the
package directory to `AARCH64-RELEASE` and selects the release firmware path.

## 4. Prepare root and payload

For a port using the userdata root layout, follow [Userdata](/guide/userdata).
The command requires macOS image tools and the target partition geometry:

```sh
./unixnu build userdata --dry-run
./unixnu build userdata
```

Inspect `<output>/userdata/userdata-root.json` for size, windows and the flash
command. Set the root UUID from the selected volume. For the writable Data volume,
prepare the seed described by the device; [Skip Setup](/guide/skip-setup) is an
optional transformation of that seed.

```sh
./unixnu build payload
```

This uses the local trust-cache, identity and Data seed inputs. Inspect
`<output>/payload/payload.json` and the printed command line. The generated FAT
volume contains `unixnu.toml`, the kernel and its ADT/selected sidecars. See
[Payload](/concepts/payload) for their layout.

**Expected result:** root and Data inputs match the device policy, and the payload
contains the intended boot entry and arguments.

## 5. Pack and boot

```sh
./unixnu bootimg
```

Inspect `<output>/boot/boot.json`: the firmware, DTB and payload must be the
intended files, and `ramdisk_bytes` must be nonzero for a configured payload boot.
Follow [Boot the image](/guide/boot) for flashing conditions and the one-time boot
command. Follow [bring-up](/porting/bring-up) on a new port.

After changing boot arguments, run `./unixnu payload` and `./unixnu bootimg`.
Follow [apply arguments](/xnu/boot-arguments#apply-arguments) to inspect the packed
configuration. After changing kernel code, also rebuild the kernel first.

## macOS runner

The kernel step calls Xcode on macOS, and the Data seed steps call `hdiutil` and `diskutil`. A fork can run them on a GitHub macOS runner without a local Mac. The workflow is a build check: it publishes redacted text logs and no images.

1. Fork the repository and enable Actions.
2. Add the repository secret `UNIXNU_UNIQUE_CHIP_ID` when the board requires a platform seed for its payload.
3. Run the `macOS build` workflow. Choose the device repository, ref, defconfig, Xcode version and steps.
4. Read the step summary or download the log artifact.

The job runs on `macos-26`. `xcode` selects `/Applications/Xcode_<version>.app` and defaults to `26.6`.

| Input | Meaning |
| --- | --- |
| `device_repository` | Device repository as `owner/name` |
| `device_ref` | Ref of the device repository |
| `defconfig` | Defconfig name from `configs/` |
| `xcode` | Xcode version on the `macos-26` image |
| `steps` | `kernel`, `kernel payload`, `kernel userdata` or `kernel userdata payload`. The default is `kernel` |
| `ipsw_url` | Optional IPSW URL. An empty value uses `board.toml` |
| `pre_build` | Optional shell commands run in the UniXNU checkout before the kernel build. The device repository is at `DEVICE_DIR` |
| `trust_cache_url` | Optional trust cache bundle URL, masked in the logs |
| `owner_trust_cache` | Treat the URL as an owner-signed bundle |
| `data_seed_url` | Optional Data seed URL, masked in the logs |
| `grow_gib` | Grow the Data seed to this size |
| `skip_setup` | Mark Setup as done in the Data seed |

Add the repository secret `UNIXNU_DEVICE_TOKEN` when the device repository is private.

The workflow uses the shared resolver to read effective profiles and output paths. It checks the inputs, the defconfig, the Xcode path and the platform seed before installing or building. It publishes only `*.log` files with secrets and signed URLs replaced, and writes a per-step summary.

A device archive chain that needs a bootstrap candidate, display ABI evidence or a staged kernelcache uses `pre_build`. Its commands run after checkout and before the kernel build. The workflow removes the fetched IPSW, the fetched feeds and the staged firmware cache at the end.

A bootstrap candidate example:

```sh
./unixnu defconfig bootstrap_defconfig -D "$DEVICE_DIR"
./unixnu build kernel -D "$DEVICE_DIR"
mkdir -p out/<device>/<os_profile>/<config>/tree/build/xnu-prelink
cp out/<device>/<os_profile>/<config>/kernel/kernel.macho \
   out/<device>/<os_profile>/<config>/tree/build/xnu-prelink/<candidate>.macho
```

The candidate names and the display or kernelcache inputs come from the device repository.

The workflow runs kernel, userdata and payload. Package, firmware and boot image commands run locally on supported macOS or Linux hosts. Check the workflow and account runner settings before using hosted builds.

## Linux host

The installer supports apt, dnf, pacman and zypper on glibc Linux. Use `--package-manager none` with prepared dependencies and `--llvm-config FILE` for a specific host LLVM. See [Linux requirements](/guide/requirements#linux).

The kernel step runs on Linux after a one-time toolchain install (see [Requirements](/guide/requirements#linux)):

```sh
scripts/linux/setup-toolchain.py --print-packages
sudo scripts/linux/setup-toolchain.py
./unixnu defconfig <name> -D ../UniXNU-<device>
./unixnu fetch
./unixnu build kernel
```

The driver selects the Linux path from the host. It sets the toolchain environment, and `build-xnu-4k-baseline.sh` runs `scripts/linux/prepare-xnu.py`:

- `source`, after the xnu patches: rewrites the few xnu sources that assume Apple's clang or BSD tools (the SHA and AES assembler macros, the syscall table generator under mawk, `kextsymboltool` writing to `/dev/null`) and installs a `TargetConditionals.h` into the fakeroot.
- `libs`, after the headers: builds `libcc_kext.a`, which a Mac takes from Apple clang, from compiler-rt.

`build-firehose.sh` compiles `libfirehose_kernel` without Xcode, `build-corecrypto-14.py` reads the corecrypto project with `scripts/pbxproj.py` instead of `plutil`, and the kernelcache is decoded with `lzfse`.

The Linux path uses the same selected profiles, archive recipes and prelink checks. Record the host toolchain with the build result; device recipes may require additional SDK or image tools.

## Commands

| Command | Action |
| --- | --- |
| `defconfig [NAME]` | Lists `configs/*_defconfig` of the device repository, or merges the selected configuration into the target `.config`. |
| `fetch [NAME...] [--update]` | Fetches git sources and writes `unixnu.lock` in the device repository. `--update` refreshes unpinned refs; explicit format 2 commits remain selected. |
| `tree` | Resolves modules, fetches the references the steps need, and assembles `out/<device>/<os_profile>/<config>/tree`. |
| `ipsw info` | Prints the product, build and every component of the target IPSW. |
| `ipsw fetch [COMPONENT...]` | Extracts the named components into `out/ipsw/<build>/`. |
| `build [kernel] [package] [firmware] [payload] [prelink]` | Runs the named steps. The default selects kernel, package, payload and firmware. `prelink` repeats the prelink alone. |
| `build userdata [--dry-run]` | Builds the raw userdata image. This step is large and runs only when named. |
| `bootimg` | Packs BootShim, the firmware volume, the device tree and the optional payload into an Android boot image. |
| `status [--json]` | Prints effective profiles, component scope, revisions, overrides, and patch order. |
| `clean` | Removes target `tree`, `logs`, `kernel`, `package`, `boot` and `edk2-conf`. |

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

`defconfig` merges the ordered configuration fragments and the selected device defconfig into the target `.config`. The selected defconfig is applied last. It rejects malformed lines before the build starts.

### fetch

`fetch` resolves every module and fetches the git sources. It uses a shallow, blobless clone with a cone sparse checkout. Format 2 caches each repository and selected revision. The resolved commits are written to `unixnu.lock`; explicit source commits take priority over recorded locks.

### tree

`tree` assembles `out/<device>/<os_profile>/<config>/tree` with the layout the scripts expect:

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

1. Resolves the declared patch series and component patches, then applies them to target-local XNU sources. Format 1 uses its directory patch order.
2. Runs `prepare-xnu-source.py` to restore omitted DriverKit headers.
3. Runs one XNU pass for the compile records when `startup.o.json` is absent. The pass may stop at the link.
4. Runs selected component recipes and auxiliary `[kernel] archives` commands. `component:<ID>` entries place component recipes at explicit positions; dependencies run first.
5. Builds XNU for `ARM64`, machine `BCM2837`, configuration `DEVELOPMENT`, iOS 17, and links the archives.
6. Prelinks the native kernel against the original kernelcache with `kits/XnuPrelink`. A rebuild replaces the earlier candidate.

The kernelcache comes from the IPSW unless `--kernelcache` supplies one. The LZFSE payload of the `KernelCache` IM4P is decoded with macOS `compression_tool` (`lzfse` on Linux), the arm64 slice is selected, and the result is checked against `[kernel.prelink] kernelcache_sha256`.

The output is `out/<device>/<os_profile>/<config>/kernel/kernel.macho`.

### package

The package step builds `package/` with EDK II. The output is `out/<device>/<os_profile>/<config>/package/Build/Out`. It contains `UniXNU.efi`, `UniXNUDxe.efi`, `UniXNURamDiskDxe.efi`, `HelloPayload.efi`, `SampleDriver.efi` and `XnuTest.efi`.

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

The kernel command line comes from `[payload] kernel_args`. An extra `--kernel-arg NAME=VALUE` replaces the board argument with the same name. The volume is written with mtools without mounting. The output is `out/<device>/<os_profile>/<config>/payload/payload.img` with `payload.json`.

`--owner-trust-cache` supplies an owner-signed bundle with the original caches and extra modules. It replaces `--trust-cache` and skips `[payload] trust_cache_sha256`.

`--skip-setup` marks Setup as done in a copy of the Data seed supplied with `--data-ramdisk`.

### userdata

The userdata step builds the raw image for the `userdata` partition. It holds the unchanged `OS` and `SystemOS` disk images of the IPSW behind the `SHNGROOT` manifest. On macOS the disk images are attached read-only with `hdiutil`; on Linux `scripts/unixnu/udif.py` decodes them, with `lzfse` for LZFSE chunks. Both give the same bytes. The output is `out/<device>/<os_profile>/<config>/userdata/userdata-root.img` with `userdata-root.json`.

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
| `out/<device>/<os_profile>/<config>/.config` | Selected defconfig |
| `out/<device>/<os_profile>/<config>/tree/` | Assembled build tree |
| `out/<device>/<os_profile>/<config>/logs/` | Step logs |
| `out/<device>/<os_profile>/<config>/kernel/kernel.macho` | Prelinked kernel |
| `out/<device>/<os_profile>/<config>/package/Build/Out/` | EFI binaries |
| `out/<device>/<os_profile>/<config>/payload/` | Payload image and report |
| `out/<device>/<os_profile>/<config>/boot/` | Boot image and report |
| `out/<device>/<os_profile>/<config>/userdata/` | Userdata image and report |

## Reproducibility

`unixnu.lock` pins every fetched source. The firmware build sets `SOURCE_DATE_EPOCH` to the Mu-Silicium commit time, so EDK II does not embed the build time. The boot image is deterministic for a given firmware volume, device tree and ramdisk. The payload contains a random seed, so two payload builds differ.

## Next steps

- [Build the kernel](/guide/build-kernel) describes the kernel flags and archives.
- [Boot the image](/guide/boot) describes the fastboot commands.
- [Reference](/reference/output-layout) lists every report field.
