# Redmi Pad format-2 qualification candidate; boot Mu and cust UniXNU must remain separate

[woaphone/UniXNU-yunluo](https://github.com/woaphone/UniXNU-yunluo)

<div v-pre>

Xiaomi Redmi Pad \(MT6789\) UniXNU port with UEFI display, UFS root, activation UI, touch, eight-core SMP and a tested 2 GiB XNU memory window.

源记录: [porting.toml](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/porting.toml), `c8bb04451690443c1c0a0c7404786d2d4b27d7f5`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `host-verified` |
| [固件与启动](#firmware) | `device-verified` |
| [CPU 与中断](#cpu) | `device-verified` |
| [内存与 DMA](#memory) | `device-verified` |
| [存储与根卷](#storage) | `device-verified` |
| [显示](#display) | `device-verified` |
| [输入](#input) | `device-verified` |
| [GPU](#gpu) | `planned` |
| [网络](#network) | `planned` |
| [音频](#audio) | `planned` |
| [电源](#power) | `planned` |
| [镜像组装](#packaging) | `device-verified` |
| [诊断](#diagnostics) | `device-verified` |

## 配置 {#configuration}

`host-verified`

组件: `ArmDTPlatform`, `SoftwareAES`.

### 硬件与依赖

- Current UniXNU device configuration, selected OS profile, MT6789 SoC source cad9262392dd589b75c7c9bf38f3f6c256be6c31 and XNU source woaphone/xnu-mtk branch yunluo at 53bc420e5acda41c1689f6690a85841393a347cf.

### 配置

- Profiles resolve in arch/SoC/OS/device order; arrays replace inherited arrays.

### 操作步骤

- Use the corresponding current UniXNU common guide; preserve source pins and collect the result before progressing.
- Integrate every required runtime component and publish reviewed SoC/component pins before enabling an image build.

### 开发经验

- The device record now points kernel source at woaphone/xnu-mtk branch yunluo instead of treating the hosted XNU patch tree as an unrelated artifact.
- The public configuration pins woaphone/UniXNU-mt6789-common at cad9262392dd589b75c7c9bf38f3f6c256be6c31 and supplies an ignored local override example.
- The tested runtime milestones are recorded separately from the current source-migration layout.

### 完成条件

- All source pins resolve; every selected component has a record; status shows the intended overrides and patch order.

### 当前范围

- The public repository still needs its full runtime archive set reproduced, but the tested legacy milestones are no longer hidden behind a generic qualification label.

### 下一步

- Integrate every required runtime component and publish reviewed SoC/component pins before enabling an image build.

### 证据

- `source`: [Explicit source/qualification boundary and outstanding runtime work; no new device proof.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/source-scope.md)
- `host`: [PASS: profile and defconfig generation on the explicit local SoC source; not a kernel build.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/defconfig.txt)
  Command: <code>python3 /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/UniXNU/unixnu defconfig yunluo_defconfig -D /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo --local-module soc:mt6789=/home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-mt6789-common --out /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo/out/structural-committed/configured</code>. Revision: `238f33cda2750f52c19748607cee6ca56f56e2a3`.
- `host`: [PASS: configured=true and five core components resolve; this is not the complete legacy runtime.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/configured-status.txt)
  Command: <code>python3 /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/UniXNU/unixnu status --json -D /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo --local-module soc:mt6789=/home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-mt6789-common --out /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo/out/structural-committed/configured</code>. Revision: `238f33cda2750f52c19748607cee6ca56f56e2a3`.

## 固件与启动 {#firmware}

`device-verified`

组件: `DarwinBoot`.

### 硬件与依赖

- Mu-Silicium platform firmware, BootShim and stock boot/vendor\_boot protocol inputs.

### 配置

- boot contains Mu firmware only; UniXNU and file-loaded DarwinBoot belong in cust.

### 操作步骤

- Use the corresponding current UniXNU common guide; preserve source pins and collect the result before progressing.
- Separate FV integration from cust EFI files, then prove the actual cust entry load path without the old ramdisk fallback.

### 开发经验

- The tested v4 boot image entered UniXNU, produced visible UEFI/XNU output and passed DarwinBoot handoff.
- The preserved cust-v2 loader work supplied the largest-window allocation policy later used by the tested 2 GiB profile.
- The current split-image repository layout still needs a fresh packaging pass; this does not invalidate the tested legacy boot chain.

### 完成条件

- Firmware image builds, enters UniXNU, publishes the framebuffer and preserves the documented memory reservations.

### 当前范围

- The tested image embeds loader/application modules in the firmware volume; rebuilding the current split layout remains pending.

### 下一步

- Separate FV integration from cust EFI files, then prove the actual cust entry load path without the old ramdisk fallback.

### 证据

- `source`: [Explicit source/qualification boundary and outstanding runtime work; no new device proof.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/source-scope.md)
- `source`: [Published loader reference and paired firmware provenance, with current split-layout integration still in progress.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/publication-scope.md)
- `host`: [PASS: production largest-window helper and source models under ASan/UBSan, plus normal/base record checks.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/publication-host-checks.json)
  Command: <code>gcc -O1 -g -Wall -Wextra -fsanitize=address,undefined -I loader/DarwinBoot/DarwinBootPkg/Driver tests/largest-window.c -o out/largest-window &amp;&amp; ./out/largest-window</code>. Revision: `db777162eccdde5c6854750786e24fa8e6afe52b`.
- `device`: [The fb46 and later images produced visible UEFI/XNU output and entered the tested UniXNU boot chain.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/device-progress-2026-10-29.md)
  Command: <code>fastboot boot boot-yunluo-unixnu-fb198.img and later images</code>. Revision: `2551dfe8ec21d0c6711139058ef70f08edf7a220`.

## CPU 与中断 {#cpu}

`device-verified`

组件: `ArmCpu`.

### 硬件与依赖

- Six Cortex-A55 plus two Cortex-A76; source ADT affinities 0..0x700 in 0x100 steps, GICv3 and 13 MHz timer.

### 配置

- Board DTS includes the MT6789 DTSI; selected CPU driver and Apple CPU-node ABI must be audited together.

### 操作步骤

- Use the corresponding current UniXNU common guide; preserve source pins and collect the result before progressing.
- Compare reg/cpu-id/reg-private and GIC ranges against the preserved working ABI before a new boot.

### 开发经验

- Eight-core startup and software/MMIO IPI delivery were tested on the inputfix6 SMP baseline.
- The current common-converter CPU properties still need a build through the current repository layout.

### 完成条件

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU.

### 当前范围

- The tested ABI used the preserved legacy ADT generator; a fresh build with the current common converter remains pending.

### 下一步

- Compare reg/cpu-id/reg-private and GIC ranges against the preserved working ABI before a new boot.

### 证据

- `source`: [Explicit source/qualification boundary and outstanding runtime work; no new device proof.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/source-scope.md)
- `host`: [PASS: sourced eight-CPU/GIC/timer description compiles without diagnostics.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/dtc.txt)
  Command: <code>dtc -I dts -O dtb -i /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-mt6789-common/dts -o /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo/out/structural-committed/hardware.dtb /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo/dts/yunluo.dts</code>. Revision: `238f33cda2750f52c19748607cee6ca56f56e2a3`.
- `device`: [inputfix6 started all eight CPUs and delivered MMIO IPIs.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/device-progress-2026-10-29.md)
  Command: <code>fastboot boot boot-yunluo-unixnu-inputfix6-smp8-mmioipi.img</code>. Revision: `2551dfe8ec21d0c6711139058ef70f08edf7a220`.

## 内存与 DMA {#memory}

`device-verified`

### 硬件与依赖

- Six-GiB board DRAM declaration, 2.5-GiB requested loader window, existing reservations and DMA ownership.

### 配置

- DRAM starts at 0x40000000; requested owned window 0xa0000000, not proof of a new allocation.

### 操作步骤

- Use the corresponding current UniXNU common guide; preserve source pins and collect the result before progressing.
- Account for every firmware reservation and DMA engine; compare generated ADT and actual loader allocation.

### 开发经验

- The inputfix6 2 GiB XNU owned-memory profile was tested and confirmed usable.
- The largest-window helper preserves reserved edges and allocation accounting. A 2.5 GiB current-board attempt still needs a matching build and device run.

### 完成条件

- All handoff regions are accounted for and each enabled DMA engine accesses its allocated range with the documented cache policy.

### 当前范围

- The device-tested baseline used a 2 GiB owned-memory window; the 2.5 GiB configuration in this source tree remains unverified.

### 下一步

- Account for every firmware reservation and DMA engine; compare generated ADT and actual loader allocation.

### 证据

- `source`: [Explicit source/qualification boundary and outstanding runtime work; no new device proof.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/source-scope.md)
- `host`: [PASS: common ADT conversion on synthetic host identity, declared memory and placeholders.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/make-adt.txt)
  Command: <code>python3 /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/UniXNU/scripts/make-adt.py --dtb /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo/out/structural-committed/hardware.dtb --os-profile /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/UniXNU/profiles/os/ipados-17.7.11-21H461/profile.toml --board /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo/board.toml --unique-chip-id 0x594c4e554d543637 --data-ramdisk --trust-cache --output /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo/out/structural-committed/kernel.macho.adt</code>. Revision: `238f33cda2750f52c19748607cee6ca56f56e2a3`.
- `device`: [The inputfix6 2 GiB owned-memory baseline was confirmed usable.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/device-progress-2026-10-29.md)
  Command: <code>fastboot boot boot-yunluo-unixnu-inputfix6-smp8-mmioipi-2g.img</code>. Revision: `2551dfe8ec21d0c6711139058ef70f08edf7a220`.

## 存储与根卷 {#storage}

`device-verified`

### 硬件与依赖

- MTK UFS LU2/4096-byte blocks and host 0x11270000/0x2300; actual cust GPT/LP identity and capacity are required.

### 配置

- cust owns the separate UniXNU filesystem. Persistent Data is independent and is not enabled by this layout.

### 操作步骤

- Use the corresponding current UniXNU common guide; preserve source pins and collect the result before progressing.
- Obtain saved GPT/LP metadata, qualify direct firmware visibility, and migrate the real MTK transport without Qualcomm aliases.

### 开发经验

- The tested baseline used MT6789 UFS LU2 with 4096-byte logical blocks, presented GPT/APFS, mounted the root volume and reached launchd.
- The current public source layout uses a separate cust image and still needs a fresh transport/package integration pass.

### 完成条件

- Actual cust partition type/capacity and firmware block/filesystem visibility are established without guessed geometry.
- Qualified MTK reads identify GPT/LUN/root windows correctly and launchd starts; persistent Data tests remain a separate explicit scope/authorization.

### 当前范围

- Storage is tested on the preserved UFS layout; the current split boot/cust layout still needs its own build and device run.

### 下一步

- Obtain saved GPT/LP metadata, qualify direct firmware visibility, and migrate the real MTK transport without Qualcomm aliases.

### 证据

- `source`: [Explicit source/qualification boundary and outstanding runtime work; no new device proof.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/source-scope.md)
- `host`: [The current split-policy build gate still requires fresh cust geometry and load-path evidence.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/build-readiness-rejection.txt)
  Command: <code>python3 /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo/scripts/check-partition-layout.py --require-build-ready</code>. Revision: `238f33cda2750f52c19748607cee6ca56f56e2a3`.
- `device`: [UFS LU2, APFS root, cryptex and launchd were reached on the tested baseline.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/device-progress-2026-10-29.md)
  Command: <code>fastboot boot boot-yunluo-unixnu-fb70.img and later images</code>. Revision: `2551dfe8ec21d0c6711139058ef70f08edf7a220`.

## 显示 {#display}

`device-verified`

### 硬件与依赖

- UEFI GOP handoff, 1200x2000 panel and 2048-pixel/8192-byte stride from existing source records.

### 配置

- Preserve the qualified mod\_init ordering and donor vtable/selector ABI when integrating the actual implementation.

### 操作步骤

- Use the corresponding current UniXNU common guide; preserve source pins and collect the result before progressing.
- Port the actual display component and probe lifecycle, then test a known frame and userspace presentation.

### 开发经验

- UEFI output, XNU console and the activation page were visible on the tested baseline.
- The inputfix5 display configuration applied the 180-degree presentation and AKS compatibility layer.
- The Setup-init image later ended with PID1 SIGBUS; its fault PC is not recorded.

### 完成条件

- A known frame appears with correct geometry and colors, then userland presentation and backlight controls work.

### 当前范围

- Activation-page presentation is tested; stable post-Setup behavior is blocked by the PID1 SIGBUS.

### 下一步

- Port the actual display component and probe lifecycle, then test a known frame and userspace presentation.

### 证据

- `source`: [Source record for the tested display path and remaining Setup failure.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/source-scope.md)
- `device`: [The activation page and the 180-degree display configuration were observed on the tested images.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/device-progress-2026-10-29.md)
  Command: <code>fastboot boot boot-yunluo-unixnu-fb198.img; fastboot boot boot-yunluo-unixnu-inputfix5-display-aks.img</code>. Revision: `2551dfe8ec21d0c6711139058ef70f08edf7a220`.

## 输入 {#input}

`device-verified`

### 硬件与依赖

- Yunluo PMIC state helper plus reusable Novatek protocol/core models; actual MTK bus/IRQ and yunluo sensor firmware remain separate inputs.

### 配置

- Power uses TOPSTATUS bit1, volume-up bit3; inherited Qcom clock/pin/SMMU helpers are excluded.

### 操作步骤

- Use the corresponding current UniXNU common guide; preserve source pins and collect the result before progressing.
- Run scoped host regressions and qualify the actual sensor/firmware/bus/HID ABI before claiming touch works.

### 开发经验

- Touch input was confirmed usable on the inputfix4 baseline.
- The tested path included the Novatek sensor, SPI transport and HID delivery to the userspace consumer.
- Physical-key behavior and four-corner calibration still need a dedicated final test.

### 完成条件

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive, and buttons produce expected HID reports.

### 当前范围

- Touch is tested; physical-key coverage and four-corner calibration are incomplete.

### 下一步

- Run scoped host regressions and qualify the actual sensor/firmware/bus/HID ABI before claiming touch works.

### 证据

- `source`: [Explicit source/qualification boundary and outstanding runtime work; no new device proof.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/source-scope.md)
- `host`: [PASS under ASan/UBSan: 4096 PMIC state combinations and polling cases; register model only.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/pmic-state.txt)
  Command: <code>/usr/bin/g++ -O1 -g -Wall -Wextra -fsanitize=address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer -std=c++17 tests/board-key-state.cpp -o /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo/out/host-committed/pmic-state &amp;&amp; /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo/out/host-committed/pmic-state</code>. Revision: `238f33cda2750f52c19748607cee6ca56f56e2a3`.
- `host`: [PASS under ASan/UBSan: reusable protocol model; real-firmware cases explicitly skipped.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/novatek-protocol-model.txt)
  Command: <code>/usr/bin/gcc -O1 -g -Wall -Wextra -fsanitize=address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer -std=c11 drivers/NativeNovatekTouch/Test/nvt-protocol.c drivers/NativeNovatekTouch/NvtProtocol.c -o /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo/out/host-committed/novatek-protocol-model &amp;&amp; /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo/out/host-committed/novatek-protocol-model</code>. Revision: `238f33cda2750f52c19748607cee6ca56f56e2a3`.
- `host`: [PASS under ASan/UBSan: reusable contact/core model.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/novatek-touch-core-model.txt)
  Command: <code>/usr/bin/gcc -O1 -g -Wall -Wextra -fsanitize=address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer -std=c11 drivers/NativeNovatekTouch/Test/touch-core.c drivers/NativeNovatekTouch/NvtTouchCore.c -lm -o /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo/out/host-committed/novatek-touch-core-model &amp;&amp; /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo/out/host-committed/novatek-touch-core-model</code>. Revision: `238f33cda2750f52c19748607cee6ca56f56e2a3`.
- `device`: [Touch input was confirmed usable on yunluo.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/device-progress-2026-10-29.md)
  Command: <code>fastboot boot boot-yunluo-unixnu-inputfix4-expdb1029.img</code>. Revision: `2551dfe8ec21d0c6711139058ef70f08edf7a220`.

## GPU {#gpu}

`planned`

### 硬件与依赖

- MT6789 Mali hardware identity and a compatible driver/frontend ABI, not Adreno firmware or GMU recipes.

### 配置

- No Adreno/Qcom components are selected.

### 操作步骤

- Use the corresponding current UniXNU common guide; preserve source pins and collect the result before progressing.
- Inventory the actual Mali submission, memory/fence and presentation interfaces before choosing an implementation.

### 开发经验

- GPU/Metal acceleration is planned and unsupported, not declared not-applicable to a device with a GPU.

### 完成条件

- GPU submissions complete, mapping/fence handling is correct, a known image renders, and the selected Metal client presents it.

### 当前范围

- GPU/Metal acceleration is planned and unsupported, not declared not-applicable to a device with a GPU.

### 下一步

- Inventory the actual Mali submission, memory/fence and presentation interfaces before choosing an implementation.

### 证据

- `source`: [Explicit source/qualification boundary and outstanding runtime work; no new device proof.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/source-scope.md)

## 网络 {#network}

`planned`

### 硬件与依赖

- Board wireless bus, chipset, firmware, IRQ/DMA and OS network interface.

### 配置

- No WLAN implementation is selected.

### 操作步骤

- Use the corresponding current UniXNU common guide; preserve source pins and collect the result before progressing.
- Inventory verified wireless resources and choose an implementation compatible with this board.

### 开发经验

- Association and packet transfer are unimplemented; this is not not-applicable.

### 完成条件

- Scanning, association, address configuration and sustained receive/transmit traffic pass with the selected firmware.

### 当前范围

- Association and packet transfer are unimplemented; this is not not-applicable.

### 下一步

- Inventory verified wireless resources and choose an implementation compatible with this board.

### 证据

- `source`: [Explicit source/qualification boundary and outstanding runtime work; no new device proof.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/source-scope.md)

## 音频 {#audio}

`planned`

### 硬件与依赖

- MTK DSP/codec, clocks, firmware services and physical route inventory.

### 配置

- No Qualcomm DSP/GLINK/QMP recipe is selected.

### 操作步骤

- Use the corresponding current UniXNU common guide; preserve source pins and collect the result before progressing.
- Establish the actual MTK audio resources and services before porting a route.

### 开发经验

- Playback/capture are not implemented or verified.

### 完成条件

- Each declared route carries the selected audio format through playback or capture and handles start/stop correctly.

### 当前范围

- Playback/capture are not implemented or verified.

### 下一步

- Establish the actual MTK audio resources and services before porting a route.

### 证据

- `source`: [Explicit source/qualification boundary and outstanding runtime work; no new device proof.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/source-scope.md)

## 电源 {#power}

`planned`

### 硬件与依赖

- MTK regulator/clock/battery units, firmware ownership and transition dependencies.

### 配置

- A pure PMIC key-state model is not battery or suspend/resume support.

### 操作步骤

- Use the corresponding current UniXNU common guide; preserve source pins and collect the result before progressing.
- Identify source-confirmed controls and define per-transition observable tests.

### 开发经验

- Sleep/resume, battery and peripheral power transitions remain unqualified.

### 完成条件

- Declared power controls and battery readings match observations; each claimed sleep/resume transition restores its dependent peripherals.

### 当前范围

- Sleep/resume, battery and peripheral power transitions remain unqualified.

### 下一步

- Identify source-confirmed controls and define per-transition observable tests.

### 证据

- `source`: [Explicit source/qualification boundary and outstanding runtime work; no new device proof.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/source-scope.md)

## 镜像组装 {#packaging}

`device-verified`

组件: `XnuPrelink`.

### 硬件与依赖

- XNU 10063.141.1/21H461 ABI inputs and separately built Mu boot and UniXNU cust images.

### 配置

- No UniXNU payload in boot ramdisk. Exact cust image size/filesystem awaits partition evidence.

### 操作步骤

- Use the corresponding current UniXNU common guide; preserve source pins and collect the result before progressing.
- Implement and test two-artifact manifests, boot payload exclusion and exact cust EFI/kernel/ADT contents before usability testing.

### 开发经验

- The legacy v4 boot image built, loaded through BootShim and UEFI, and reached the activation page on device.
- The current split boot/cust policy is recorded in this repository but still needs a fresh package build.

### 完成条件

- Separate boot firmware and cust UniXNU artifacts build from reviewed source pins; boot contains no UniXNU payload ramdisk; cust contains all declared EFI/runtime/kernel/ADT inputs.
- An explicitly authorized device test identifies both artifact hashes and proves Mu loads the intended cust path, not an old ramdisk or unrelated ESP.

### 当前范围

- The tested baseline used the embedded-payload layout; the current split-image layout still needs a validated build.

### 下一步

- Implement and test two-artifact manifests, boot payload exclusion and exact cust EFI/kernel/ADT contents before usability testing.

### 证据

- `source`: [Explicit source/qualification boundary and outstanding runtime work; no new device proof.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/source-scope.md)
- `host`: [PASS: split-header fixture accepted; embedded payload, empty/truncated kernel rejected. Fixture/header scope only.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/split-policy-fixtures.txt)
  Command: <code>python3 /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo/scripts/check-partition-layout.py --self-test /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo/out/structural-committed/fixtures</code>. Revision: `238f33cda2750f52c19748607cee6ca56f56e2a3`.
- `host`: [The current split-policy checker rejects the preserved embedded-payload layout.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/old-monolithic-image-rejection.txt)
  Command: <code>python3 /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo/scripts/check-partition-layout.py --boot-image /mnt/d/漏洞/UNIXNU/bringup/uefi/boot-yunluo-unixnu-inputfix6-smp8-mmioipi-2g.img</code>. Revision: `238f33cda2750f52c19748607cee6ca56f56e2a3`.
- `device`: [The tested v4 boot image reached the activation page on yunluo.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/device-progress-2026-10-29.md)
  Command: <code>fastboot boot boot-yunluo-unixnu-fb198.img</code>. Revision: `2551dfe8ec21d0c6711139058ef70f08edf7a220`.

## 诊断 {#diagnostics}

`device-verified`

### 硬件与依赖

- Exact source/firmware/image revisions, accessible logs and official record/base-diff checks.

### 配置

- Host and device evidence are distinct; publication is gated on real build and usable-boot proof.

### 操作步骤

- Use the corresponding current UniXNU common guide; preserve source pins and collect the result before progressing.
- Record real commands/results and full source revisions, then run the official normal and --base checks.

### 开发经验

- The preserved yunluo bring-up has device-confirmed UEFI, UFS, APFS, launchd, activation UI, touch, eight-core SMP and 2 GiB milestones.
- The record keeps PID1 SIGBUS, calibration and peripheral gaps visible.

### 完成条件

- Each claimed milestone has a reproducible command, a matching source/image revision and an accessible result.

### 当前范围

- The summarized device progress references the preserved 2026-10-29 image set; large logs remain outside the public repository.

### 下一步

- Record real commands/results and full source revisions, then run the official normal and --base checks.

### 证据

- `source`: [Explicit source/qualification boundary and outstanding runtime work; no new device proof.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/source-scope.md)
- `host`: [PASS: official checker validates the 13-area record schema and declared component coverage; not usability.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/record-check.txt)
  Command: <code>python3 /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/UniXNU/scripts/porting-record.py check --device /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo</code>. Revision: `238f33cda2750f52c19748607cee6ca56f56e2a3`.
- `host`: [PASS: committed code changes have record ownership against porting-import-base.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/record-base-check.txt)
  Command: <code>python3 /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/UniXNU/scripts/porting-record.py check --device /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo --base porting-import-base</code>. Revision: `238f33cda2750f52c19748607cee6ca56f56e2a3`.
- `device`: [The tested image sequence records UEFI, UFS/APFS, activation, touch, SMP and 2 GiB milestones.](https://github.com/woaphone/UniXNU-yunluo/blob/c8bb04451690443c1c0a0c7404786d2d4b27d7f5/docs/evidence/device-progress-2026-10-29.md)
  Command: <code>fastboot boot the named preserved yunluo image sequence</code>. Revision: `2551dfe8ec21d0c6711139058ef70f08edf7a220`.

</div>
