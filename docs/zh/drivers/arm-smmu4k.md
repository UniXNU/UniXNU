# ArmSmmu4K

先按[适配流程](/zh/porting/platform)准备板级输入、修改源码、接入构建并逐步验证。

ARM SMMUv2 原生 4 KiB 表 kit。构建并编程 stage-1/stage-2 context 表。

| 仓库 | 维护者 | 范围 |
| --- | --- | --- |
| [ArmSmmu4K](https://github.com/UniXNU/ArmSmmu4K) | [UniXNU](https://github.com/UniXNU) | ARM SMMUv2 原生 4 KiB 表 kit。构建并编程 stage-1/stage-2 context 表。 |

## 状态

Adreno740 和存储驱动使用它。

live 更新在一个事务内映射或解除一批页：每批只发布一次页表页、同步一次 TLB、复查一次。`ArmSmmu4KLiveMapContextBatchExclusive` 映射调用方独占的物理页，跳过与已有区间的别名检查，批内各页之间仍互相检查。解除不超过 512 页时逐页发 TLBIVAL，更多时按 ASID 失效。

流路由带有 SMR 掩码（`ArmSmmu4KStream.mask`）：SMMU 匹配时忽略的流 ID 位，与设备树 `iommus` 条目中的掩码相同。0 表示精确匹配。宽于 SMMU 流 ID 位数的掩码会被拒绝。两个自有路由之间，或自有路由与已生效的 SMR 之间，若 ID 只在其中一方掩码忽略的位上不同，即视为重叠。

## 构建

消费该 kit 的驱动配方编译其源码。sheng 将 `ArmSmmu4K*.c` 加入 GPU 归档。按[平台适配](/zh/porting/platform)提供 MMIO、context/stream 所有权和分配回调。
