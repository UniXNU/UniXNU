# Meizu 21: UniXNU transition with retained Darwin22 kernel and protected APFS root \(XiaoChen8371\)

[XiaoChen8371/unixnu-meizu21](https://github.com/XiaoChen8371/unixnu-meizu21)

<div v-pre>

UniXNU transition: host menu/protocol verified; retained Darwin22 hardware path; r20 not device-tested.

源记录: [porting.toml](https://github.com/XiaoChen8371/unixnu-meizu21/blob/6e644239a9c937ec1ffebe17f171a72cfba7a2ec/porting.toml), `6e644239a9c937ec1ffebe17f171a72cfba7a2ec`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `host-verified` |
| [固件与启动](#firmware) | `host-verified` |
| [CPU 与中断](#cpu) | `implemented` |
| [内存与 DMA](#memory) | `host-verified` |
| [存储与根卷](#storage) | `implemented` |
| [显示](#display) | `host-verified` |
| [输入](#input) | `implemented` |
| [GPU](#gpu) | `planned` |
| [网络](#network) | `planned` |
| [音频](#audio) | `planned` |
| [电源](#power) | `implemented` |
| [镜像组装](#packaging) | `host-verified` |
| [诊断](#diagnostics) | `host-verified` |

## 配置 {#configuration}

`host-verified`

### 硬件与依赖

- SM8650, retained iOS16.5/Darwin22.5, source pins in unixnu.lock.

### 配置

- Format 2 resolves the custom OS profile; inherited Darwin23 archives are explicitly replaced.

### 操作步骤

- Run scripts/package.sh --check, then scripts/package.sh; inspect the referenced evidence.

### 开发经验

- Format 2 resolves the custom OS profile; inherited Darwin23 archives are explicitly replaced.

### 完成条件

- Replace retained drivers with ABI-audited native component recipes.

### 当前范围

- The selected native DarwinBoot source is for review only; stage 1 uses the board protocol adapter.

### 下一步

- Replace retained drivers with ABI-audited native component recipes.

### 证据

- `host`: [Format 2 resolves the custom OS profile; inherited Darwin23 archives are explicitly replaced.](https://github.com/XiaoChen8371/unixnu-meizu21/blob/6e644239a9c937ec1ffebe17f171a72cfba7a2ec/evidence/configure.log)
  Command: <code>bash scripts/package.sh</code>. Revision: `63f39b92ede3d30c53f8317d5607bb2ceb099342`.

## 固件与启动 {#firmware}

`host-verified`

### 硬件与依赖

- Exact r19 DEBUG FD; real UniXNU 04573c5; retained loader SHA0be90c00; physical FB E3940000.

### 配置

- DEBUG menu and production bridge compile; the bridge fits the existing embedded-loader slot.

### 操作步骤

- Run scripts/package.sh --check, then scripts/package.sh; inspect the referenced evidence.

### 开发经验

- DEBUG menu and production bridge compile; the bridge fits the existing embedded-loader slot.

### 完成条件

- Confirm menu and kernel handoff on Meizu21 after the owner returns.

### 当前范围

- No r20 hardware boot. Current original firmware sources diverge from the stable binary.

### 下一步

- Confirm menu and kernel handoff on Meizu21 after the owner returns.

### 证据

- `host`: [DEBUG menu and production bridge compile; the bridge fits the existing embedded-loader slot.](https://github.com/XiaoChen8371/unixnu-meizu21/blob/6e644239a9c937ec1ffebe17f171a72cfba7a2ec/evidence/packaging-check.json)
  Command: <code>bash scripts/package.sh</code>. Revision: `63f39b92ede3d30c53f8317d5607bb2ceb099342`.

## CPU 与中断 {#cpu}

`implemented`

### 硬件与依赖

- Retained loader uses GICD17100000/GICR17180000, core shift8, and default cpus=1.

### 配置

- CPU/interrupt code is preserved in the independent kernel snapshot; no SMP behavior changed.

### 操作步骤

- Run scripts/package.sh --check, then scripts/package.sh; inspect the referenced evidence.

### 开发经验

- CPU/interrupt code is preserved in the independent kernel snapshot; no SMP behavior changed.

### 完成条件

- Preserve the working primary-core path while auditing native GIC/timer ABI.

### 当前范围

- No new native ArmCpu integration or SMP verification.

### 下一步

- Preserve the working primary-core path while auditing native GIC/timer ABI.

### 证据

- `source`: [CPU/interrupt code is preserved in the independent kernel snapshot; no SMP behavior changed.](https://github.com/XiaoChen8371/unixnu-meizu21/blob/6e644239a9c937ec1ffebe17f171a72cfba7a2ec/evidence/kernel-snapshot.json)

## 内存与 DMA {#memory}

`host-verified`

### 硬件与依赖

- FD A4000000+400000, payload F0000000+3800000, retained kernel window B0000000..D8000000.

### 配置

- All firmware file offsets and MemoryMap stay unchanged; bounded parser passes 100000 mutations.

### 操作步骤

- Run scripts/package.sh --check, then scripts/package.sh; inspect the referenced evidence.

### 开发经验

- All firmware file offsets and MemoryMap stay unchanged; bounded parser passes 100000 mutations.

### 完成条件

- Audit native DarwinBoot placement against 16KiB pages and actual free windows.

### 当前范围

- QEMU does not establish DMA or SMMU behavior on SM8650.

### 下一步

- Audit native DarwinBoot placement against 16KiB pages and actual free windows.

### 证据

- `host`: [All firmware file offsets and MemoryMap stay unchanged; bounded parser passes 100000 mutations.](https://github.com/XiaoChen8371/unixnu-meizu21/blob/6e644239a9c937ec1ffebe17f171a72cfba7a2ec/evidence/xnup-r20-test.log)
  Command: <code>bash scripts/package.sh</code>. Revision: `63f39b92ede3d30c53f8317d5607bb2ceb099342`.

## 存储与根卷 {#storage}

`implemented`

### 硬件与依赖

- Existing UFS/APFS root and cryptex occupy protected super; boot\_a must remain intact.

### 配置

- Packaging carries forward the exact small root ramdisk and meizu\_ufs/root\_apfs arguments.

### 操作步骤

- Run scripts/package.sh --check, then scripts/package.sh; inspect the referenced evidence.

### 开发经验

- Packaging carries forward the exact small root ramdisk and meizu\_ufs/root\_apfs arguments.

### 完成条件

- After menu validation, confirm existing root still mounts; keep super immutable.

### 当前范围

- No root-image transformation, new partition geometry, userdata recipe or storage hardware test.

### 下一步

- After menu validation, confirm existing root still mounts; keep super immutable.

### 证据

- `source`: [Packaging carries forward the exact small root ramdisk and meizu\_ufs/root\_apfs arguments.](https://github.com/XiaoChen8371/unixnu-meizu21/blob/6e644239a9c937ec1ffebe17f171a72cfba7a2ec/evidence/inputs.json)

## 显示 {#display}

`host-verified`

### 硬件与依赖

- Physical 1080x2340, BGRx32, stride4320, framebuffer E3940000.

### 配置

- Real UniXNU renders a portrait menu at this geometry in QEMU; r16 Dock correction is retained.

### 操作步骤

- Run scripts/package.sh --check, then scripts/package.sh; inspect the referenced evidence.

### 开发经验

- Real UniXNU renders a portrait menu at this geometry in QEMU; r16 Dock correction is retained.

### 完成条件

- Check menu and Dock on the phone without changing memory reservations.

### 当前范围

- QEMU validates menu layout, not phone panel presentation, backlight or acceleration.

### 下一步

- Check menu and Dock on the phone without changing memory reservations.

### 证据

- `host`: [Real UniXNU renders a portrait menu at this geometry in QEMU; r16 Dock correction is retained.](https://github.com/XiaoChen8371/unixnu-meizu21/blob/6e644239a9c937ec1ffebe17f171a72cfba7a2ec/evidence/qemu-result.log)
  Command: <code>bash scripts/package.sh</code>. Revision: `63f39b92ede3d30c53f8317d5607bb2ceb099342`.

## 输入 {#input}

`implemented`

### 硬件与依赖

- Goodix GPIO48/49/50/51, reset161, IRQ162; raw coordinates10800x23400; TCS0 power path.

### 配置

- Existing persistent quiet touch kernel and libhakios/backboardd bridge are preserved.

### 操作步骤

- Run scripts/package.sh --check, then scripts/package.sh; inspect the referenced evidence.

### 开发经验

- Existing persistent quiet touch kernel and libhakios/backboardd bridge are preserved.

### 完成条件

- Verify repeated iOS touches after r20 boot before replacing the HID path.

### 当前范围

- r20 has not been phone-tested; touch input for the UEFI menu is not implemented.

### 下一步

- Verify repeated iOS touches after r20 boot before replacing the HID path.

### 证据

- `source`: [Existing persistent quiet touch kernel and libhakios/backboardd bridge are preserved.](https://github.com/XiaoChen8371/unixnu-meizu21/blob/6e644239a9c937ec1ffebe17f171a72cfba7a2ec/evidence/kernel-snapshot.json)

## GPU {#gpu}

`planned`

### 硬件与依赖

- A750/SM8650; native DT profiles43051400 and43051401; stock Meizu firmware pins preserved locally.

### 配置

- GPU probe remains off. Neither A740 rendering nor Ace5 preparation proves A750 rendering here.

### 操作步骤

- Run scripts/package.sh --check, then scripts/package.sh; inspect the referenced evidence.

### 开发经验

- GPU probe remains off. Neither A740 rendering nor Ace5 preparation proves A750 rendering here.

### 完成条件

- Read real SoC/GPU revision first, then port power and memory ownership before firmware execution.

### 当前范围

- No Meizu GPU power/SMMU/GMU/HFI/CP submission, frontend ABI or Metal verification.

### 下一步

- Read real SoC/GPU revision first, then port power and memory ownership before firmware execution.

### 证据

- `source`: [GPU probe remains off. Neither A740 rendering nor Ace5 preparation proves A750 rendering here.](https://github.com/XiaoChen8371/unixnu-meizu21/blob/6e644239a9c937ec1ffebe17f171a72cfba7a2ec/evidence/inputs.json)

## 网络 {#network}

`planned`

### 硬件与依赖

- Native WLAN adaptation and firmware transport are not migrated by the boot manager.

### 配置

- No networking driver from another board is enabled in this transition.

### 操作步骤

- Run scripts/package.sh --check, then scripts/package.sh; inspect the referenced evidence.

### 开发经验

- No networking driver from another board is enabled in this transition.

### 完成条件

- Inventory Meizu WLAN transport/firmware after the boot/GPU migration stage.

### 当前范围

- No working network claim or new radio operation.

### 下一步

- Inventory Meizu WLAN transport/firmware after the boot/GPU migration stage.

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`planned`

### 硬件与依赖

- SM8650 DSP/codec routing requires board-specific firmware and service adaptation.

### 配置

- Existing code is preserved; no Ace5 audio or modem initialization is imported.

### 操作步骤

- Run scripts/package.sh --check, then scripts/package.sh; inspect the referenced evidence.

### 开发经验

- Existing code is preserved; no Ace5 audio or modem initialization is imported.

### 完成条件

- Audit actual board audio resources and services before enabling a native driver.

### 当前范围

- No audio playback/capture result.

### 下一步

- Audit actual board audio resources and services before enabling a native driver.

### 证据

按下一步操作收集证据。

## 电源 {#power}

`implemented`

### 硬件与依赖

- Approved touch rails: ldob9=2960mV, ldob12=1800mV, HPM7; verified TCS0 response masks.

### 配置

- The working touch voltage/ACK/recovery implementation remains in the retained kernel.

### 操作步骤

- Run scripts/package.sh --check, then scripts/package.sh; inspect the referenced evidence.

### 开发经验

- The working touch voltage/ACK/recovery implementation remains in the retained kernel.

### 完成条件

- Preserve existing touch power behavior; audit GPU resource ownership separately.

### 当前范围

- No GPU rail write, new PMIC configuration, battery or suspend migration.

### 下一步

- Preserve existing touch power behavior; audit GPU resource ownership separately.

### 证据

- `source`: [The working touch voltage/ACK/recovery implementation remains in the retained kernel.](https://github.com/XiaoChen8371/unixnu-meizu21/blob/6e644239a9c937ec1ffebe17f171a72cfba7a2ec/evidence/kernel-snapshot.json)

## 镜像组装 {#packaging}

`host-verified`

### 硬件与依赖

- Pinned complete r19 image, exact legacy loader, current linked kernel, stock DTB, DEBUG menu.

### 配置

- Repacked image is unpacked and compared; kernel/root/cmdline/shim/DTB remain exact.

### 操作步骤

- Run scripts/package.sh --check, then scripts/package.sh; inspect the referenced evidence.

### 开发经验

- Repacked image is unpacked and compared; kernel/root/cmdline/shim/DTB remain exact.

### 完成条件

- Device-test r20 boot\_b while retaining the complete r16 rollback.

### 当前范围

- r20 unflashed; native UniXNU userdata, generic payload and bootshim recipes are not used.

### 下一步

- Device-test r20 boot\_b while retaining the complete r16 rollback.

### 证据

- `host`: [Repacked image is unpacked and compared; kernel/root/cmdline/shim/DTB remain exact.](https://github.com/XiaoChen8371/unixnu-meizu21/blob/6e644239a9c937ec1ffebe17f171a72cfba7a2ec/evidence/packaging-check.json)
  Command: <code>bash scripts/package.sh</code>. Revision: `63f39b92ede3d30c53f8317d5607bb2ceb099342`.

## 诊断 {#diagnostics}

`host-verified`

组件: `DarwinBoot`.

### 硬件与依赖

- Logs include production DEBUG builds, bounded-parser sanitizers and QEMU menu/protocol receiver.

### 配置

- The QEMU receiver exits before any phone kernel or hardware operation. Sources and image pins are recorded.

### 操作步骤

- Run scripts/package.sh --check, then scripts/package.sh; inspect the referenced evidence.

### 开发经验

- The QEMU receiver exits before any phone kernel or hardware operation. Sources and image pins are recorded.

### 完成条件

- Record the first phone menu/kernel/desktop checkpoint with image SHA after the owner returns.

### 当前范围

- Host evidence must not be labelled hardware verification; native DarwinBoot ABI is still incompatible.

### 下一步

- Record the first phone menu/kernel/desktop checkpoint with image SHA after the owner returns.

### 证据

- `host`: [The QEMU receiver exits before any phone kernel or hardware operation. Sources and image pins are recorded.](https://github.com/XiaoChen8371/unixnu-meizu21/blob/6e644239a9c937ec1ffebe17f171a72cfba7a2ec/evidence/qemu-result.log)
  Command: <code>bash scripts/package.sh</code>. Revision: `63f39b92ede3d30c53f8317d5607bb2ceb099342`.

</div>
