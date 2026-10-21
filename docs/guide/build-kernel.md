# Build the kernel

The kernel step builds Apple's XNU source with UniXNU patches, then prelinks the result against the original kernelcache.

## Source and tree

| Path | Contents |
| --- | --- |
| `out/<board>/tree/refer/xnu` | Pinned XNU source |
| `out/<board>/tree/.cache/xnu-work` | Working clone with patches applied |
| `out/<board>/tree/build/xnu/ios-obj` | Object files and compile command records |
| `out/<board>/tree/build/xnu/ios-sym` | Symbols |
| `out/<board>/tree/build/xnu/ios-dst` | Install headers |
| `out/<board>/tree/.cache/fakeroot` | Kernel SDK root with restored headers |
| `out/<board>/tree/.cache/firmware` | Device proprietary inputs, linked from the device repository |
| `out/<board>/kernel/kernel.macho` | Prelinked kernel |

The source version comes from `feeds.toml`:

```toml
[[source]]
name = "xnu"
kind = "refer"
git = "https://github.com/apple-oss-distributions/xnu.git"
ref = "xnu-10063.141.1"
commit = "d8b80295118ef25ac3a784134bcf95cd8e88109f"
darwin = "23.6.0"
version = "10063.141.1"
driverkit_tag = "xnu-10063.121.3"
trustcache_tag = "xnu-8796.101.5"
```

`unixnu build kernel` passes these values to `scripts/build-xnu-4k-baseline.sh` as `UNIXNU_XNU_TAG`, `UNIXNU_XNU_COMMIT`, `UNIXNU_XNU_DARWIN`, `UNIXNU_XNU_VERSION`, `UNIXNU_DRIVERKIT_TAG` and `UNIXNU_TRUSTCACHE_TAG`.

The kernel reference set also pins `libpthread` at `libpthread-519.120.4` and `corecrypto-2023` at commit `11fba65`. The source providers compile against the XNU compile records.

The build target is:

```
SDKROOT=iphoneos
ARCH_CONFIGS=ARM64
MACHINE_CONFIGS=BCM2837
KERNEL_CONFIGS=DEVELOPMENT
ARM64_LINK_ADDR=0xfffffff007004000
ARM64_PLKSEG_ADDR=0xfffffff004004000
DEPLOYMENT_TARGET_FLAGS="-miphoneos-version-min=17.0 -DXNU_TARGET_OS_IOS"
```

`BCM2837` is the XNU machine configuration that carries the 4 KiB page layout. The kernel still targets iOS 17 so the prelink ABI matches the iPadOS kernelcache.

## Defconfig flags

Each `CONFIG_XNU_<NAME>` line becomes `XNU_<NAME>` in the kernel build environment. `y` becomes `1`, `n` becomes `0`, quoted strings are passed as text, and `{tree}` in a string is replaced by the build tree path.

| Flag | Effect | Archive |
| --- | --- | --- |
| `XNU_SOURCE_CORECRYPTO14` | Builds and links the source corecrypto provider | `build/corecrypto-2023/libcorecrypto_kernel_noasm-namespaced.a` |
| `XNU_SOURCE_PTHREAD` | Builds and registers the source pthread component | `build/libpthread-kernel/libpthread_kernel.a` |
| `XNU_ARM_DT_PLATFORM` | Links the Apple-format device tree platform expert | `build/armdt-platform/libArmDTPlatform.a` |
| `XNU_ARMVIRT_PLATFORM` | Links the QEMU virt platform expert | `build/armvirt-platform/libArmVirtPlatform.a` |
| `XNU_ARMCPU` | Links the architectural CPU and interrupt provider | `build/armcpu/libArmCpu.a` |
| `XNU_NATIVE_UFS` | Links the UFS storage driver | `build/native-ufs/libNativeUfs.a` |
| `XNU_NATIVE_AES` | Links the AES accelerator driver | `build/native-aes/libNativeAES.a` |
| `XNU_NATIVE_VIRTIO_BLOCK` | Links the VirtIO block driver | `XNU_NATIVE_VIRTIO_BLOCK_ARCHIVE` or `build/native-virtio-block/libNativeVirtioBlock.a` |
| `XNU_NATIVE_RAM_BLOCK` | Links the RAM block driver | `build/native-ram-block/libNativeRamBlock.a` |
| `XNU_NATIVE_VIRTIO_CONSOLE` | Links the VirtIO console byte transport | `build/native-virtio-console/libNativeVirtioConsole.a` |
| `XNU_NATIVE_MOBILE_DISPLAY` | Links the mobile display provider | `build/native-mobile-display/libNativeMobileDisplay.late.a` |
| `XNU_NATIVE_LEGACY_DISPLAY` | Links the legacy display provider | `build/native-legacy-display/libNativeLegacyDisplay.late.a` |
| `XNU_NATIVE_ADRENO` | Links the Adreno GPU driver and kits | `build/native-adreno/libNativeAdreno.a` |
| `XNU_NATIVE_OFFLINE_GPU` | Links the offline GPU broker | `build/native-offline-gpu/libNativeOfflineGPU.late.a` |
| `XNU_VERIFIED_ROOT_PROBE` | Links the verified root provider | `XNU_VERIFIED_ROOT_ARCHIVE` or `build/verified-root-xnu/libVerifiedRootProbe.a` |
| `XNU_NATIVE_CS_HASH_CACHE` | Derives 4 KiB code signature hashes from verified 16 KiB blocks | none |
| `XNU_NATIVE_ARCH_TIMER` | Uses the architectural timer entry | none |
| `XNU_NATIVE_PAN` | Enables ARMv8.1 PAN support | none |
| `XNU_DT_PANIC_REGION` | Reads the panic region from the device tree | none |
| `XNU_TRUST_CACHE_RUNTIME` | Initializes the trust cache runtime | none |
| `XNU_BOOT_PROGRESS` | Adds the boot progress layer | `build/boot-progress/libBootProgress.a` |
| `XNU_SOURCE_MOCKFS` | Adds the mockfs test file | `build/mockfs-fixture/libmockfs_fixture.a` |

`[kernel] archives` in `board.toml` lists the archive builders in order. Each entry is a script of the build tree and its arguments. For example:

```toml
[kernel]
defconfig = "sheng_defconfig"
archives = [
  "scripts/build-native-aes-bindings.py",
  "scripts/build-libpthread-kernel.py",
  "scripts/build-corecrypto-14.py",
  "scripts/build-corecrypto-14.py --namespace",
]
```

`unixnu build kernel` runs the builders after the compile records exist, then links. Entries run in order, so a builder that consumes another builder's output follows it. An archive that no builder makes must be supplied in the build tree. A configuration opts in with `CONFIG_XNU_BUILD_ARCHIVES=y`; the bootstrap pass and first-console configurations leave it unset.

The builders read symbol names through `scripts/xnu_symbols.py`. It uses the recorded checkpoint kernel, or the objects in `build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/link.filelist` plus the aliases in `all-alias.exp`. A fresh tree therefore needs one kernel pass for the records, and the archive output cannot collide with a previously linked kernel.

The kernel step prepares the public `IOStorageFamily` headers under `build/storage-abi/include` before the archive builders.

`build-native-aes-bindings.py` and `build-native-adreno-accelerator.py` use the recorded audit results in `scripts/data/` when the original hardware evidence is absent. The recorded addresses belong to the kernelcache pinned in `board.toml`.

## Build sequence

1. `unixnu fetch` clones XNU, libpthread, corecrypto-2023 and the Apple references.
2. `unixnu build kernel` applies the patches and restores the omitted headers.
3. When the compile records are absent, it runs one XNU pass for them. The pass may stop at the link.
4. It runs the `[kernel] archives` builders in order.
5. It builds and links the kernel with the archives, then prelinks it against the original kernelcache.
6. `unixnu build prelink` repeats only the prelink. It replaces the earlier candidate and its report.

The prelinked kernel is `out/<board>/kernel/kernel.macho`.

The prelink reads `[kernel.prelink]` from `board.toml`:

```toml
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
```

`roots` lists the original kernelcache components the native kernel uses. `early_security_init` maps a component identifier to an address that runs during prelink security initialization.

## Adding a kernel flag

1. Add `CONFIG_XNU_<NAME>=y` to the device defconfig.
2. Read `XNU_<NAME>` in `scripts/build-xnu-4k-baseline.sh`.
3. Add the object flags with `EXTRA_MAKE_ARGS+=("<file>.o_CFLAGS_ADD=-DXNU_<NAME>=$VALUE")`.
4. Add the builder script to `[kernel] archives`, then add the archive to `KERNEL_EXTRA_ARCHIVES` and `KERNEL_ARCHIVE_DEPENDENCIES`.
5. Add the personality to `iokit/KernelConfigTables.cpp` through a patch.

## Prebuilt kernel

`unixnu build payload --kernel FILE` packs an existing prelinked kernel. This path builds the boot image without rebuilding XNU.

## Next steps

- [Four-kilobyte pages](/xnu/four-k-page-tables) explains the page size work.
- [Patch reference](/xnu/patch-reference) lists every patch.
- [Prelink](/concepts/prelink) explains the kernelcache binding.
