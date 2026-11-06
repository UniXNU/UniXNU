# Patch reference

Format 2 applies `[kernel] patch_series` in declared order. Series can reference profile and component patches. `unixnu status --json` reports the resolved sequence. Format 1 applies `patches/xnu/*.patch` and `kits/XnuPrelink/patches/*.patch` in filename order.

## Build and toolchain

| Patch | Purpose |
| --- | --- |
| `apple-only-cpu-tunables` | Applies Apple CPU tunables only on `APPLE_ARM64_ARCH_FAMILY` |
| `cxx-flag-dependencies` | Passes `CFLAGS` to C++ object builds in the Makefile templates |
| `external-archive-dependencies` | Makes external archives relink dependencies of the kernel |
| `kernel-sdk-root` | Separates `KERNEL_SDKROOT` from `SDKROOT` and adds include paths |
| `local-availability` | Allows `XNU_AVAILABILITY_PL` to point at a local `availability.pl` |
| `public-entitlements-header` | Adds the web browser entitlement names and uses `CoreEntitlements` |
| `source-machine-layer` | Adds `CONFIG_APPLE_AMCC` and adjusts the BCM2837 config and file list |
| `disabled-deferred-reclaim` | Removes an unused parameter that breaks the build |
| `published-freezer-condition` | Fixes the preprocessor condition for the freezer default |

## Platform and CPU

| Patch | Purpose |
| --- | --- |
| `architectural-timer-entry` | Skips the BCM2837 timer routing when the native architectural timer is enabled |
| `armvirt-platform-personality` | Adds `ArmCpu`, `ArmVirtPlatform` and `ArmDTPlatform` personalities |
| `native-smp-secondary` | Raises `MAX_CPUS` to 8 and uses MPIDR Affinity1 for BCM2837 secondary CPUs |
| `native-arm-pan` | Enables ARMv8.1 PAN when `XNU_NATIVE_PAN` is set |
| `native-dt-panic-region` | Reads the panic log region from the device tree and validates it |

## Four-kilobyte pages

| Patch | Purpose |
| --- | --- |
| `native-4k-bootstrap-capacity` | Sizes the bootstrap page table pool for 4 KiB mappings and stops before overflow |
| `native-4k-user-abi` | Sets the 4 KiB page shift for user maps, commpage and shared region |
| `native-4k-signature-hash-cache` | Derives 4 KiB code signing hashes from verified 16 KiB blocks |
| `pgz-aligned-validation` | Decodes the PGZ address before the alignment check |
| `zzx-pmap-sync-64bit-pa` | Uses `ptoa()` to keep physical addresses above 4 GiB |
| `non-apple-pmap-field` | Matches the non-PAC pmap field layout |
| `non-apple-iommu-bootstrap` | Guards UAT and SART bootstrap and PPL code |
| `non-apple-cache-monitor` | Guards the monitor enable and exports the cache clean symbol |

## Security and owner root

| Patch | Purpose |
| --- | --- |
| `native-trust-cache-runtime` | Initializes the trust cache runtime on BCM2837 |
| `source-corecrypto14-bootstrap` | Registers the source corecrypto provider at early boot |
| `source-pthread-bootstrap` | Registers the source pthread component at early boot |
| `native-aes-personality` | Adds the AES, VirtIO block, VirtIO console, RAM block and UFS personalities |
| `offline-owner-root-crypto-probe` | Starts the verified root probe when `offline-owner-root-check` is set |
| `offline-owner-root-binding-audit` | Compares the mounted root device with the verified root device |
| `offline-owner-boot-manifest` | Publishes the owner boot manifest hash from the root and cache devices |
| `offline-owner-cache-carrier` | Selects the owner dyld cache carrier and validates its device and path |
| `offline-owner-systemos-mount` | Mounts the SystemOS cryptex and composes the root with the owner cache |
| `offline-owner-z-air-init` | Initializes the Z air path for the owner root |
| `offline-legacy-start` | Starts the legacy display probe after `IOKitBSDInit` |
| `offline-component-load-probes` | Loads APFS, IOGPU and mobile graphics components with checkpoints |
| `offline-native-gpu-broker` | Publishes the offline GPU broker after DTrace initialization |
| `sheng-platform-power` | Runs the board PMGR integration before the calendar initialization |

## Graphics and display

| Patch | Purpose |
| --- | --- |
| `offline-native-gpu-broker` | Starts the offline GPU broker |
| `zzy-native-gpu-addon-mount` | Mounts read-only union views for GPU addon content and launch jobs |
| `zzw-native-adreno-sandbox-grant` | Lets Adreno740 name the render server in `NativeSandboxGrantProcess` and open its user client past the sandbox |
| `native-aes-personality` | Registers the storage and console personalities |

## Diagnostics

| Patch | Purpose |
| --- | --- |
| `offline-pgz-alignment-probe` | Adds the PGZ allocation probe and checkpoints |
| `native-work-interval-trace` | Records the last work interval results for the boot progress page |
| `native-quiet-managed-page-report` | Stops the DEVELOPMENT managed-page report on GPU buffer and scanout mappings |
| `zzz-boot-progress` | Adds boot progress checkpoints across the kernel startup path |

## Behavior fixes

| Patch | Purpose |
| --- | --- |
| `native-priv-work-interval` | Grants `PRIV_WORK_INTERVAL` before policy evaluation |
| `native-work-interval-soft-fail` | Soft-fails a refused CA client work interval |
| `native-union-getattrlistbulk` | Continues a bulk directory read in the lower union directory |
| `native-union-statfs-fsid` | Reports the root volume's file system number through `statfs64` for a union over the root |
| `null-root-media` | Handles a null root in `IOService::setRootMedia` |
| `published-freezer-condition` | Fixes the freezer default condition |

## Mockfs

| Patch | Purpose |
| --- | --- |
| `mockfs-intermediate-lookup` | Allows lookups that are not the last component |
| `mockfs-memory-device-width` | Uses the device path when the legacy ioctl cannot express a 64-bit address |
| `mockfs-statfs` | Implements `vfs_getattr` |
| `mockfs-typed-allocation` | Uses the struct type for `kalloc_type` and `kfree_type` |
| `mockfs-test-file` | Adds `launchd` and `probe.bin` to the test file system |

## Prelink patches

`kits/XnuPrelink/patches/`:

| Patch | Purpose |
| --- | --- |
| `xnu-10063.141.1-security-init.patch` | Adds the early security initializer entry point |
| `xnu-10063.141.1-sparse-index.patch` | Adds the sparse prelink index ABI |

## Add a patch

1. Edit `.cache/xnu-work`.
2. Generate the diff with `git diff`.
3. Place it in `patches/xnu/` with a name that orders it correctly.
4. Rebuild the kernel.

A patch that depends on another patch applies after it. A patch that changes a region touched by `zzy` or `zzz` applies before them.

## Next steps

- [Source and patches](/xnu/source-and-patches)
- [Four-kilobyte pages](/xnu/four-k-page-tables)
- [Build the kernel](/guide/build-kernel)
