# Source and patches

The selected OS profile pins XNU and its ABI inputs. The arm64 iPadOS 17.7.11 profile
uses `xnu-10063.141.1`, Darwin 23.6.0, DriverKit headers from `xnu-10063.121.3`,
and TrustCache headers from `xnu-8796.101.5`. The iOS 16 and iPadOS 17 targets are
both arm64 and share the arm64 patch series in `profiles/arch/arm64`; the iOS and
iPadOS 27 targets use the arm64e series in `profiles/arch/arm64e`.

`feeds.toml` supplies libplatform, libdispatch, AvailabilityVersions, libpthread,
corecrypto, IOStorageFamily, and edk2. The format 2 OS profile's explicit XNU
revision takes priority over a recorded source lock.

## Procedure {#procedure}

1. Select the device and save `./unixnu status --json`. Record the OS profile, XNU source revision, configuration and ordered patches.
2. Identify the change's [owner](#ownership). Read the relevant [patch reference](/xnu/patch-reference), source and ABI inputs before editing.
3. Prepare the kernel once with `./unixnu kernel`. Use [Add a patch](#add-a-patch) to export the change against that prepared baseline and place it in the owning series.
4. Run `./unixnu status --json` again, check the patch position, and rebuild `./unixnu kernel`. Confirm patch application, archive builds, link and prelink succeed.
5. Rebuild `./unixnu payload` and `./unixnu bootimg` for boot validation. Record the affected checkpoint using [bring-up](/porting/bring-up). Use [Updating the source](#updating-the-source) when changing the pinned XNU version.

## Patch application

Format 2 resolves `[kernel] patch_series` in declared order. A series lists one
patch path per line, relative to the series file or prefixed with `arch:`, `soc:`,
`os:`, `device:`, or `component:<ID>/`. Component patches participate in the
same resolved order. `unixnu status --json` prints that order.

Kernel preparation creates `tree/.cache/xnu-work` under the selected target,
checks each patch, applies it, and prepares missing source headers. The target
also owns generated headers and `tree/build` outputs.

Format 1 selects `patches/xnu/*.patch` and `kits/XnuPrelink/patches/*.patch` in
filename order. Its shell preparation handles the late `zzw`, `zzy`, and `zzz`
patches and checks already-applied patches.

## Ownership

| Location | Contents |
| --- | --- |
| ARM64 profile | Common architecture configuration and patch series |
| SoC repository | Hardware operations and SoC patch series |
| OS profile | Version-specific fixes and prelink patch selection |
| Device repository | Board-specific patch series |
| Component repository | Patches required by that component |
| `patches/libpthread/`, `patches/mesa/` | Library and compiler source patches |

## Add a patch

1. Build the selected kernel once to prepare the target's `tree/.cache/xnu-work`.
   Set `XNU_WORK` to that directory and `DEVICE_DIR` to the device repository.
2. Copy the files you will edit into a temporary Git directory, preserving their
   XNU-relative paths. Stage this baseline before editing. For `start.s`:

```sh
PATCH_WORK=$(mktemp -d)
git -C "$PATCH_WORK" init
mkdir -p "$PATCH_WORK/osfmk/arm64"
cp "$XNU_WORK/osfmk/arm64/start.s" "$PATCH_WORK/osfmk/arm64/start.s"
git -C "$PATCH_WORK" add osfmk/arm64/start.s
```

3. Edit the temporary copy, then export its changes:

```sh
git -C "$PATCH_WORK" diff -- osfmk/arm64/start.s > "$DEVICE_DIR/patches/xnu/my-change.patch"
```

4. Review the patch, add `my-change.patch` to the device series and run
   `./unixnu build kernel` from UniXNU. Put shared changes in the owning SoC,
   architecture, OS or component series instead, at the position matching the baseline.
5. Inspect the resolved patch order with `./unixnu status --json` and record the
   build result. Kernel preparation reconstructs its working source when patch inputs change.

A patch that adds a build option follows this personality pattern:

```c
#if defined(XNU_MY_OPTION) && XNU_MY_OPTION
    "   ,{"
    "     'IOClass'         = MyDriver;"
    "     'IOProviderClass' = IOPlatformDevice;"
    "   }"
#endif
```

The matching `-DXNU_MY_OPTION=1` comes from `EXTRA_MAKE_ARGS` in the kernel script.

## Build flags

The kernel build uses these switches:

| Switch | Value |
| --- | --- |
| `SDKROOT` | `iphoneos` |
| `ARCH_CONFIGS` | `ARM64` |
| `MACHINE_CONFIGS` | `BCM2837` |
| `KERNEL_CONFIGS` | `DEVELOPMENT` |
| `ARM64_LINK_ADDR` | `0xfffffff007004000` |
| `ARM64_PLKSEG_ADDR` | `0xfffffff004004000` |
| `DEPLOYMENT_TARGET_FLAGS` | `-miphoneos-version-min=17.0 -DXNU_TARGET_OS_IOS` |
| `BUILD_LTO` | `0` |
| `BOUND_CHECKS` | `0` |

`BCM2837` carries the 4 KiB page layout. `BUILD_LTO=0` keeps the object files and the compile records readable and link-compatible with the external archives.

## Defconfig mapping

Each `CONFIG_XNU_<NAME>` becomes `XNU_<NAME>`:

| Defconfig value | Build value |
| --- | --- |
| `y` | `1` |
| `n` | `0` |
| `"text"` | `text` |
| `123` | `123` |
| `{tree}` in a string | Build tree path |

The kernel script reads the variables and adds object flags, archives and link inputs.

## Source tree

```
out/<device>/<os_profile>/<config>/tree/
  refer/xnu/                 pinned source
  .cache/xnu-work/           working clone
  .cache/fakeroot/           kernel SDK root
  .cache/sources/            restored header manifests
  build/xnu/ios-obj/         objects and compile records
  build/xnu/ios-sym/         symbols
  build/xnu/ios-dst/         install headers
  patches/xnu/               linked patches
  kits/XnuPrelink/        prelink tool and patches
```

## Updating the source

1. Update `xnu_version` and the full `xnu_revision` under `[os]` in the selected OS `profile.toml`. Format 1 updates `ref` and `commit` in its XNU feed.
2. Review `darwin`, `driverkit_tag`, `trustcache_tag`, IPSW identity and the prelink kernelcache pin in the same profile.
3. Rebase the ordered patches onto the selected source and update component and auxiliary archive builders for its compile records.
4. Run `./unixnu fetch` and `./unixnu status --json`. Confirm the resolved XNU revision matches the selected profile.
5. Run `./unixnu kernel`, inspect link, prelink and component ABI results, then rebuild payload and boot image and record verification.

Prelink depends on the original kernelcache ABI. Qualify the matching kernelcache,
root components and ABI inputs when changing the source version.

## Next steps

- [Four-kilobyte pages](/xnu/four-k-page-tables)
- [Patch reference](/xnu/patch-reference)
- [Build the kernel](/guide/build-kernel)
