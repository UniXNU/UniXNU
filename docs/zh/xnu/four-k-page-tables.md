# 4 KiB 页表

Apple ARM64 内核在多数 SoC 上使用 16 KiB 页。非 Apple ARM64 SoC 常用 4 KiB granule。UniXNU 为携带 4 KiB 布局的 BCM2837 机型配置构建 XNU，并修改 XNU 中假设 16 KiB 的位置。

## granule 常量

| 机型 | `ARM_PGSHIFT` | `ARM_PGBYTES` | `TCR_EL1_BOOT` TG0 | TG1 |
| --- | --- | --- | --- | --- |
| `BCM2837` | 12 | 4096 | 0，4 KiB | 2，4 KiB |
| `VMAPPLE` | 14 | 16384 | 2，16 KiB | 1，16 KiB |

`scripts/check-xnu-granules.py` 为两个 profile 编译 `TCR_EL1_BOOT` 并检查 TG0 和 TG1 字段。

内核按 4 KiB 编译。页大小属于机型配置和构建参数，16 KiB 内核和 4 KiB 内核是两次独立构建。

## 启动页表

`osfmk/arm64/start.s` 在 MMU 开启前构建 bootstrap 页表。页表池大小由 `BOOTSTRAP_TABLE_SIZE` 决定。

补丁 `native-4k-bootstrap-capacity` 加入非 Apple 4 KiB 预算：

```c
#elif !defined(APPLE_ARM64_ARCH_FAMILY) && !__ARM_16K_PG__
/* 两个根，加上每个最多 9 GiB 的映射最多十个 L2 页。 */
#define BOOTSTRAP_TABLE_SIZE (ARM_PGBYTES * 22)
```

同一补丁在分配新 L2 表前检查容量：

```asm
add $6, x25, #(BOOTSTRAP_TABLE_BYTES >> 12), lsl #12
cmp $4, $6
b.hs Lbootstrap_tables_exhausted
```

耗尽标签在循环中停住，游标和结束地址保留在寄存器中。此时 MMU 未开启，调试器可以直接查看寄存器。

补丁还把整个保留池清零，而不是只清四个 16 KiB 页：

```asm
mov x2, #(BOOTSTRAP_TABLE_BYTES / ARM_PGBYTES)
lsl x2, x2, #(ARM_PGSHIFT - TTE_SHIFT)
```

## 运行时页大小

`osfmk/arm/arm_init.c` 在 Apple 板上按 RAM 大小选择页大小。补丁 `native-4k-user-abi` 让原生 4 KiB 构建在任何 RAM 大小下使用硬件页大小：

```c
#if !defined(APPLE_ARM64_ARCH_FAMILY) && !__ARM_16K_PG__
    PAGE_SHIFT_CONST = ARM_PGSHIFT;
    page_shift_user32 = ARM_PGSHIFT;
#else
    ...
#endif
```

`scripts/check-native-4k-policy.py` 从打补丁后的源码提取策略，并在 RAM 边界执行：

| Profile | RAM | 内核 shift | 用户 32 位 shift |
| --- | --- | --- | --- |
| native 4K | 任意 | 12 | 12 |
| Apple 4K | 1 GiB 以内 | 12 | 14 |
| Apple 4K | 1 GiB 以上 | 14 | 14 |
| Apple 16K | 任意 | 14 | 14 |

Apple 4K profile 在 1 GiB 以上切换到 16 KiB，native 构建在任何大小下保持 4 KiB。

## 用户地址空间

补丁修改用户 map 策略：

| 文件 | 修改 |
| --- | --- |
| `bsd/kern/mach_loader.c` | 64 位进程使用 `FOURK_PAGE_SHIFT` |
| `osfmk/arm/commpage/commpage.c` | 64 位 commpage shift 为 12 |
| `osfmk/vm/vm_shared_region.c` | shared region 子 map 使用 4 KiB 项 |
| `osfmk/arm/arm_init.c` | `PAGE_SHIFT_CONST` 和 `page_shift_user32` 跟随 `ARM_PGSHIFT` |

4 KiB 用户态需要 4 KiB `mmap` 对齐、4 KiB commpage shift 和 4 KiB dyld shared cache 布局。读取 commpage 的进程在 legacy 和当前 64 位 shift 字段都得到 12。

## 代码签名

原始 CodeDirectory 使用 16 KiB 哈希页，4 KiB 内核校验 4 KiB 页。补丁 `native-4k-signature-hash-cache` 连接两者：

1. 在 12 位内核上接受 `pageSize = 14` 的 CodeDirectory。
2. 通过 `vn_rdwr` 读取每个原始 16 KiB 块。
3. 用原始 CodeDirectory 哈希校验该块。
4. 从已验证块派生每 4 KiB 页的摘要。
5. 把派生摘要存入只读内核内存。
6. 让 `cs_validate_page` 使用派生表。

派生表挂在 `cs_blob`：

```c
const uint8_t *csb_native4k_hashes;
vm_size_t csb_native4k_hashes_size;
vm_size_t csb_native4k_hash_count;
```

页校验检查索引、偏移对齐和表边界。未命中返回 `CS_VALIDATE_TAINTED`。原始 16 KiB 哈希失败的块不会产生表。

构建开关为 `XNU_NATIVE_CS_HASH_CACHE`。`scripts/check-code-signing-granules.py` 编译实际的 `cs_validate_codedirectory` gate，并检查内核 shift、签名 shift 和 cache 模式的八种组合。

## 分配器对齐

zone 分配器把元数据放在 secondary page。补丁 `pgz-aligned-validation` 在页掩码检查前解码 PGZ 地址：

```c
elem = pgz_decode((vm_offset_t)addr, 1);
offs = (elem & PAGE_MASK) - zone_elem_inner_offs(zone);
if (from_zone_map(elem, 1)) {
```

后续元数据查找使用解码后的元素地址。

## 4 GiB 以上的物理地址

`pmap_sync_page_attributes_phys` 原先用 32 位 shift 处理物理页号：

```c
flush_dcache((vm_offset_t)(pp << PAGE_SHIFT), PAGE_SIZE, TRUE);
```

补丁 `zzx-pmap-sync-64bit-pa` 改用 `ptoa()`：

```c
flush_dcache((vm_offset_t)ptoa(pp), PAGE_SIZE, TRUE);
```

`ptoa()` 在 shift 前扩展页号。DRAM 从 4 GiB 以上开始的设备保留高位地址。

## 非 Apple 平台保护

若干 Apple 专属路径在非 Apple 平台上需要保护：

| 补丁 | 修改 |
| --- | --- |
| `apple-only-cpu-tunables` | 仅在 `APPLE_ARM64_ARCH_FAMILY` 应用 Apple CPU tunables |
| `non-apple-cache-monitor` | 仅在 `XNU_MONITOR` 下调用 `ml_enable_monitor`，并导出 cache clean 符号 |
| `non-apple-iommu-bootstrap` | 保护 UAT 和 SART bootstrap 及 PPL 代码 |
| `non-apple-pmap-field` | 按非 PAC 布局重命名保留字段 |
| `source-machine-layer` | 加入 `CONFIG_APPLE_AMCC`，去掉 Apple 专属配置项 |
| `native-arm-pan` | 设置 `XNU_NATIVE_PAN` 时在 ARMv8.1 启用 PAN |

## SMMU 与 4 KiB 表

`ArmSmmu4K` kit 用 4 KiB granule 构建 stage 1 和 stage 2 表：

| 文件 | 功能 |
| --- | --- |
| `ArmSmmu4KProgram.c` | 表编程 |
| `ArmSmmu4KContext.c` | context descriptor |
| `ArmSmmu4KStreams.c` | stream match group |
| `ArmSmmu4KLive.c` | live stream 映射 |
| `ArmSmmu4KTableMemory.c` | 表内存 |

设备驱动用 4 KiB 表映射 DMA 缓冲。Novatek 触控驱动使用 apps SMMU bypass 路径。

## 验证

| 检查 | 工具 |
| --- | --- |
| granule 常量 | `scripts/check-xnu-granules.py` |
| 页大小策略 | `scripts/check-native-4k-policy.py` |
| 代码签名 gate | `scripts/check-code-signing-granules.py` |
| PGZ 对齐 | `scripts/check-pgz-alignment-checkpoints.py` |
| UFS VA64 证据 | `scripts/check-ufs-va64-evidence.py` |
| QEMU HVF 观察 | `scripts/qemu-entry/gdb-stop.py` 与 native 4K fixture |

QEMU 观察记录：

| 寄存器 | 期望 |
| --- | --- |
| `TCR_EL1` TG0 | 0，4 KiB |
| `TCR_EL1` TG1 | 2，4 KiB |
| `SCTLR_EL1` M | 1，MMU 开启 |
| `TTBR0_EL1`、`TTBR1_EL1` | 非零 |
| `_PAGE_SHIFT_CONST`、`_page_shift`、`_page_shift_user32`、`_page_size` | 12、12、12、4096 |

## 新代码规则

1. 使用 `PAGE_SIZE` 和 `PAGE_SHIFT`，汇编使用 `ARM_PGBYTES` 和 `ARM_PGSHIFT`。
2. 代码签名哈希 shift 与内核页 shift 分开。
3. 每个新用户 map 设置页 shift。
4. DMA 缓冲和 descriptor 按 `PAGE_SIZE` 对齐。
5. 新 IOMMU 上下文使用 4 KiB SMMU 表。
6. 应用页掩码前解码 PGZ 地址。
7. 4 GiB 以上物理地址使用 `ptoa()` 和 `phystokv()`。
8. 为每个映射的 GiB 预算 bootstrap 页表。

## 下一步

- [补丁参考](/zh/xnu/patch-reference)
- [驱动分层](/zh/drivers/overview)
- [构建内核](/zh/guide/build-kernel)
