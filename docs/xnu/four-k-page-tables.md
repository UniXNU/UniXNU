# Four-kilobyte pages

Apple ARM64 kernels use a 16 KiB page on most SoCs. Non-Apple ARM64 SoCs commonly use a 4 KiB granule. UniXNU builds XNU for the BCM2837 machine configuration, which carries the 4 KiB layout, and patches the places where XNU assumes 16 KiB.

## Granule constants

| Machine | `ARM_PGSHIFT` | `ARM_PGBYTES` | `TCR_EL1_BOOT` TG0 | TG1 |
| --- | --- | --- | --- | --- |
| `BCM2837` | 12 | 4096 | 0, 4 KiB | 2, 4 KiB |
| `VMAPPLE` | 14 | 16384 | 2, 16 KiB | 1, 16 KiB |

`scripts/check-xnu-granules.py` compiles `TCR_EL1_BOOT` for both profiles and checks the TG0 and TG1 fields.

The kernel is compiled for 4 KiB. The page size is part of the machine configuration and the build flags. A 16 KiB kernel and a 4 KiB kernel are separate builds.

## Boot page tables

`osfmk/arm64/start.s` builds the bootstrap page tables before the MMU is enabled. The table pool is sized by `BOOTSTRAP_TABLE_SIZE`.

The patch `native-4k-bootstrap-capacity` adds a non-Apple 4 KiB budget:

```c
#elif !defined(APPLE_ARM64_ARCH_FAMILY) && !__ARM_16K_PG__
/* Two roots plus up to ten L2 pages per mapping of up to 9 GiB. */
#define BOOTSTRAP_TABLE_SIZE (ARM_PGBYTES * 22)
```

The same patch adds a capacity check before a new L2 table is allocated:

```asm
add $6, x25, #(BOOTSTRAP_TABLE_BYTES >> 12), lsl #12
cmp $4, $6
b.hs Lbootstrap_tables_exhausted
```

The exhaustion label stops in a loop with the cursor and end address preserved in registers. The MMU is still off at that point, so the debugger can inspect the registers without a mapped stack.

The patch also clears the whole reserved pool instead of four 16 KiB pages:

```asm
mov x2, #(BOOTSTRAP_TABLE_BYTES / ARM_PGBYTES)
lsl x2, x2, #(ARM_PGSHIFT - TTE_SHIFT)
```

## Runtime page size

`osfmk/arm/arm_init.c` selects the page size from the RAM size on Apple boards. The patch `native-4k-user-abi` makes the native 4 KiB build use the hardware page size at every RAM size:

```c
#if !defined(APPLE_ARM64_ARCH_FAMILY) && !__ARM_16K_PG__
    PAGE_SHIFT_CONST = ARM_PGSHIFT;
    page_shift_user32 = ARM_PGSHIFT;
#else
    ...
#endif
```

`scripts/check-native-4k-policy.py` extracts this policy from the patched source and executes it at RAM boundaries:

| Profile | RAM | Kernel shift | User 32-bit shift |
| --- | --- | --- | --- |
| native 4K | any | 12 | 12 |
| Apple 4K | up to 1 GiB | 12 | 14 |
| Apple 4K | above 1 GiB | 14 | 14 |
| Apple 16K | any | 14 | 14 |

The Apple 4K profile switches to 16 KiB above 1 GiB. The native build keeps 4 KiB at every size.

## User address space

The patch updates the user map policy:

| File | Change |
| --- | --- |
| `bsd/kern/mach_loader.c` | 64-bit processes get `FOURK_PAGE_SHIFT` |
| `osfmk/arm/commpage/commpage.c` | 64-bit commpage shifts are 12 |
| `osfmk/vm/vm_shared_region.c` | The shared region submap uses 4 KiB entries |
| `osfmk/arm/arm_init.c` | `PAGE_SHIFT_CONST` and `page_shift_user32` follow `ARM_PGSHIFT` |

A 4 KiB userspace expects 4 KiB `mmap` alignment, 4 KiB commpage shifts and a 4 KiB dyld shared cache layout. A process that reads the commpage receives 12 for both the legacy and current 64-bit shift fields.

## Code signing

The original CodeDirectory in the kernelcache uses a 16 KiB hash page. A 4 KiB kernel validates 4 KiB pages. The patch `native-4k-signature-hash-cache` bridges the two:

1. Accept a CodeDirectory with `pageSize = 14` on a 12-bit kernel.
2. Read each original 16 KiB block through `vn_rdwr`.
3. Compare the block with the original CodeDirectory hash.
4. Derive one digest per 4 KiB page from the verified block.
5. Store the derived digests in read-only kernel memory.
6. Serve `cs_validate_page` from the derived table.

The derived table is attached to the `cs_blob`:

```c
const uint8_t *csb_native4k_hashes;
vm_size_t csb_native4k_hashes_size;
vm_size_t csb_native4k_hash_count;
```

A page validation checks the index, the offset alignment and the table bounds. A miss returns `CS_VALIDATE_TAINTED`. A block that fails the original 16 KiB hash leaves the blob without a table.

The build flag is `XNU_NATIVE_CS_HASH_CACHE`. `scripts/check-code-signing-granules.py` compiles the actual `cs_validate_codedirectory` gate and checks eight combinations of kernel shift, signature shift and cache mode.

## Allocator alignment

The zone allocator stores metadata on a secondary page. The patch `pgz-aligned-validation` decodes the PGZ address before checking the page mask:

```c
elem = pgz_decode((vm_offset_t)addr, 1);
offs = (elem & PAGE_MASK) - zone_elem_inner_offs(zone);
if (from_zone_map(elem, 1)) {
```

The check then uses the decoded element address for the metadata lookup.

## Physical addresses above 4 GiB

`pmap_sync_page_attributes_phys` originally shifted the physical page number with a 32-bit shift:

```c
flush_dcache((vm_offset_t)(pp << PAGE_SHIFT), PAGE_SIZE, TRUE);
```

The patch `zzx-pmap-sync-64bit-pa` uses `ptoa()`:

```c
flush_dcache((vm_offset_t)ptoa(pp), PAGE_SIZE, TRUE);
```

`ptoa()` widens the page number before the shift. A device whose DRAM starts above 4 GiB keeps the high address bits.

## Non-Apple platform guards

Several Apple-only paths need guards on a non-Apple platform:

| Patch | Change |
| --- | --- |
| `apple-only-cpu-tunables` | Apply Apple CPU tunables only on `APPLE_ARM64_ARCH_FAMILY` |
| `non-apple-cache-monitor` | Call `ml_enable_monitor` only under `XNU_MONITOR`; export a cache clean symbol |
| `non-apple-iommu-bootstrap` | Guard UAT and SART bootstrap and PPL code |
| `non-apple-pmap-field` | Rename the reserved field to match the non-PAC layout |
| `source-machine-layer` | Add `CONFIG_APPLE_AMCC` and drop Apple-only config entries |
| `native-arm-pan` | Enable PAN on ARMv8.1 when `XNU_NATIVE_PAN` is set |

## SMMU and 4 KiB tables

The `ArmSmmu4K` kit builds stage 1 and stage 2 tables with 4 KiB granules. The kit provides:

| File | Function |
| --- | --- |
| `ArmSmmu4KProgram.c` | Table programming |
| `ArmSmmu4KContext.c` | Context descriptors |
| `ArmSmmu4KStreams.c` | Stream match groups |
| `ArmSmmu4KLive.c` | Live stream mapping |
| `ArmSmmu4KTableMemory.c` | Table memory |

A device driver maps DMA buffers through the SMMU with 4 KiB tables. The touch driver example uses the apps SMMU bypass path.

## Verification

| Check | Tool |
| --- | --- |
| Granule constants | `scripts/check-xnu-granules.py` |
| Page size policy | `scripts/check-native-4k-policy.py` |
| Code signing gate | `scripts/check-code-signing-granules.py` |
| PGZ alignment | `scripts/check-pgz-alignment-checkpoints.py` |
| UFS VA64 evidence | `scripts/check-ufs-va64-evidence.py` |
| QEMU HVF observation | `scripts/qemu-entry/gdb-stop.py` with the native 4K fixture |

The QEMU observation records:

| Register | Expected |
| --- | --- |
| `TCR_EL1` TG0 | 0, 4 KiB |
| `TCR_EL1` TG1 | 2, 4 KiB |
| `SCTLR_EL1` M | 1, MMU enabled |
| `TTBR0_EL1`, `TTBR1_EL1` | Nonzero |
| `_PAGE_SHIFT_CONST`, `_page_shift`, `_page_shift_user32`, `_page_size` | 12, 12, 12, 4096 |

## Rules for new code

1. Use `PAGE_SIZE` and `PAGE_SHIFT`. Use `ARM_PGBYTES` and `ARM_PGSHIFT` in assembly.
2. Keep the code signing hash shift separate from the kernel page shift.
3. Set the user map page shift for every new user map.
4. Align DMA buffers and descriptors to `PAGE_SIZE`.
5. Use 4 KiB SMMU tables for new IOMMU contexts.
6. Decode PGZ addresses before applying page masks.
7. Use `ptoa()` and `phystokv()` for physical addresses above 4 GiB.
8. Budget bootstrap page tables for every mapped GiB.

## Next steps

- [Patch reference](/xnu/patch-reference)
- [SMMU kit](/drivers/overview)
- [Build the kernel](/guide/build-kernel)
