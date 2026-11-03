# ArmSmmu4K

Start with the [adaptation procedure](/porting/platform) for board inputs, source changes, build integration and verification order.

ARM SMMUv2 native 4 KiB table kit. Builds and programs stage-1/stage-2 context tables.

| Repository | Maintainer | Scope |
| --- | --- | --- |
| [ArmSmmu4K](https://github.com/UniXNU/ArmSmmu4K) | [UniXNU](https://github.com/UniXNU) | ARM SMMUv2 native 4 KiB table kit. Builds and programs stage-1/stage-2 context tables. |

## State

Used by Adreno740 and the storage drivers.

Live updates map or unmap a batch of pages in one transaction: one page publication, one TLB synchronization and one recheck per batch. `ArmSmmu4KLiveMapContextBatchExclusive` maps pages the caller owns exclusively and skips the alias check against the existing ranges; the changes are still checked against each other. An unmap of up to 512 pages invalidates each removed page with TLBIVAL; a larger unmap invalidates the ASID.

## Build

The consuming driver's recipe compiles the kit sources. The GPU archive recipe includes `ArmSmmu4K*.c`. Supply MMIO, context/stream ownership and allocation callbacks as described in [platform adaptation](/porting/platform).
