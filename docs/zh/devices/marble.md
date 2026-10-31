# Redmi Note 12 Turbo / POCO F5（marble）

[sing0626/UniXNU-marble](https://github.com/sing0626/UniXNU-marble)

<div v-pre>

Community legacy XNU 8796 source port for Marble. A historical temporary boot reached iOS Hello, but touch/setup remain incomplete; no matching upstream Format-2 profile/feed or Format-2 device build is claimed.

源记录: [porting.toml](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/porting.toml), `a63260314d130ebf02a987f0785f5ae3258c219c`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `planned` |
| [固件与启动](#firmware) | `planned` |
| [CPU 与中断](#cpu) | `planned` |
| [内存与 DMA](#memory) | `planned` |
| [存储与根卷](#storage) | `planned` |
| [显示](#display) | `planned` |
| [输入](#input) | `planned` |
| [GPU](#gpu) | `planned` |
| [网络](#network) | `planned` |
| [音频](#audio) | `planned` |
| [电源](#power) | `planned` |
| [镜像组装](#packaging) | `planned` |
| [诊断](#diagnostics) | `planned` |

## 配置 {#configuration}

`planned`

### 硬件与依赖

- iOS 16.7.16 inputs, reviewed SM7475 feed and board-specific ADT/configuration.

### 配置

- Record actual board keys, device-tree properties, build flags and source revisions as resolved; no placeholder profile or feed value is treated as established.

### 操作步骤

- Use the documented offline workflow with explicit user-supplied inputs; preserve the command, source revision and observable result for each milestone.

### 开发经验

- Resolve board pins, OS profile, SoC feed, source selection, array replacements and patch order. No matching iOS 16.7.16 profile or reviewed SM7475 feed was present at upstream 0fc0fc1f9ddd0fbd4787738afef38667df5e0a95.
- Added the schema-2 identity, a real reference-only Git lock, matching iPhone restore identity/member hashes, input inventories and the official record workflow. The matching OS/SoC implementations are still absent, so example=true remains a build guard; a 13-area record pass is not a resolved build.

### 完成条件

- Reviewed profile/feed exists; all source pins and config resolve; selected components and overrides are recorded.

### 当前范围

- The published v4 tree is based on XNU 1b191cb58250d0705d8a51287127505aa4bc0789 and is an older dirty snapshot, not the exact tested kernel source. This area is not claimed Format-2 implemented or verified.

### 下一步

- Obtain reviewed matching upstream profile/feed, then resolve board pins and a clean source migration.

### 证据

- `source`: [Upstream profile/feed review at pinned revision.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/docs/evidence/upstream-format2-review.md)
- `source`: [Public source snapshot facts and scope.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/legacy-xnu/README.md)
- `source`: [Recorded migration checks and unresolved resolver gates, not hardware/build completion.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/docs/evidence/format2-validation.json)
- `source`: [Matching restore identity and recomputed member hashes; no Apple binary content.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/docs/evidence/ios16-inputs.json)

## 固件与启动 {#firmware}

`planned`

### 硬件与依赖

- Matching user-supplied firmware, boot payload and qualified device tree.

### 配置

- Record actual board keys, device-tree properties, build flags and source revisions as resolved; no placeholder profile or feed value is treated as established.

### 操作步骤

- Use the documented offline workflow with explicit user-supplied inputs; preserve the command, source revision and observable result for each milestone.

### 开发经验

- Matching restore-derived firmware, boot payload, device-qualified FDT and handoff inputs. Private firmware/system images are not included.
- Measured legacy layout is Platforms/Xiaomi/marblePkg/marble.dsc and Build/marblePkg/&\#123;target&\#125;\_CLANGPDB/FV/SILICIUM\_UEFI.fd, Android header v4. Board package integration is explicitly unfinished; no fabricated Kit.toml or vendor hash is used.

### 完成条件

- Clean payload boots and documents firmware, framebuffer and memory handoff.

### 当前范围

- Historical experimental kernel reached Hello through temporary fastboot boot; the published v4 source does not exactly reproduce that image. This area is not claimed Format-2 implemented or verified.

### 下一步

- Build the boot payload from public sources plus user-supplied firmware, then validate handoff on target.

### 证据

- `source`: [Sanitized historical device observation; legacy only.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/docs/evidence/legacy-hello.md)
- `source`: [Public source snapshot facts and scope.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/BUILDING.md)
- `source`: [Recorded migration checks and unresolved resolver gates, not hardware/build completion.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/docs/evidence/format2-validation.json)

## CPU 与中断 {#cpu}

`planned`

### 硬件与依赖

- Device CPU topology, GIC, timer and interrupt map.

### 配置

- Record actual board keys, device-tree properties, build flags and source revisions as resolved; no placeholder profile or feed value is treated as established.

### 操作步骤

- Use the documented offline workflow with explicit user-supplied inputs; preserve the command, source revision and observable result for each milestone.

### 开发经验

- SM7475-family CPU topology, GIC ranges, timer rate, interrupts and IPIs.
- Observed boot affinity0, PSCI smc, GIC distributor0x17100000/0x10000 and redistributor0x17180000/0x200000, stride0x40000, virtual timer19200000Hz/PPI11. Only one boot CPU is described; no format-2 SMP or IPI result is claimed.

### 完成条件

- Every enabled CPU reaches checkpoint and timer/IPI works on each.

### 当前范围

- Hello establishes a historical kernel-to-userspace path, not full per-core or interrupt coverage. This area is not claimed Format-2 implemented or verified.

### 下一步

- Record per-core entry, timer and interrupt checkpoints from a clean build.

### 证据

- `source`: [Public source snapshot facts and scope.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/legacy-xnu/README.md)
- `source`: [Recorded migration checks and unresolved resolver gates, not hardware/build completion.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/docs/evidence/format2-validation.json)
- `source`: [Sanitized source-backed resource inventory with explicit omissions and disabled integration.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/docs/HARDWARE.md)

## 内存与 DMA {#memory}

`planned`

### 硬件与依赖

- Validated ADT, physical map, reservations, DMA widths/cache policy and stream ownership.

### 配置

- Record actual board keys, device-tree properties, build flags and source revisions as resolved; no placeholder profile or feed value is treated as established.

### 操作步骤

- Use the documented offline workflow with explicit user-supplied inputs; preserve the command, source revision and observable result for each milestone.

### 开发经验

- Memory handoff/reservations, DMA widths/cache policy and SMMU ownership. Touch GPI and QUP wrapper have distinct DMA contexts.
- The sanitized DTS omits guessed RAM/reservation ranges. Legacy firmware allocated a real512MiB window; a DRAM envelope is not RAM capacity. GPI ring SID0x5b6 and QUP payload SID0x5a3 are separate mapping roles, not a DMA-safety proof.

### 完成条件

- Memory reservations reconcile and each enabled DMA engine stays within a verified mapped range.

### 当前范围

- SMMU decoder handles already-read words only; it does not program MMIO, DMA or SMMU. This area is not claimed Format-2 implemented or verified.

### 下一步

- Audit reservations and implement/verify each needed DMA context before enabling peripheral DMA.

### 证据

- `source`: [Public source snapshot facts and scope.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/touch/MARBLE-GPI-DMA-PATH.md)
- `source`: [Recorded migration checks and unresolved resolver gates, not hardware/build completion.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/docs/evidence/format2-validation.json)
- `source`: [Sanitized source-backed resource inventory with explicit omissions and disabled integration.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/docs/HARDWARE.md)
- `host`: [Host checks passed on the published source revision; no format-2 device, touch or DMA result.](https://github.com/sing0626/UniXNU-marble/actions/runs/40470393424)
  Command: <code>GitHub Actions Source checks: synthetic C fixtures, source integrity and fake-fastboot installer tests</code>. Revision: `28105e5831e680cfe50fa573b5b6ea85cb0f7b56`.

## 存储与根卷 {#storage}

`planned`

### 硬件与依赖

- Device-qualified UFS path, root layout and user-provided restore input.

### 配置

- Record actual board keys, device-tree properties, build flags and source revisions as resolved; no placeholder profile or feed value is treated as established.

### 操作步骤

- Use the documented offline workflow with explicit user-supplied inputs; preserve the command, source revision and observable result for each milestone.

### 开发经验

- UFS controller/PHY/clocks/power, SMMU stream, GPT/root layout and restore inputs.
- The described UFS register regions are 0x1d84000/0x3000,0x1d88000/0x8000,0x1d90000/0x9000. Legacy native UFS/HFSX work reached launchd/Hello on the maintainer root; a fresh format-2 root and driver/PHY/power integration remain unverified.

### 完成条件

- UFS reads and root mount work; Data behavior is explicitly validated.

### 当前范围

- Project status reports legacy UFS/HFS root progressed to launchd/Hello; persistence and broad storage qualification are not established. This area is not claimed Format-2 implemented or verified.

### 下一步

- Reproduce UFS reads, HFS root mount and controlled Data persistence from a clean public build.

### 证据

- `source`: [Public source snapshot facts and scope.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/README.md)
- `source`: [Public source snapshot facts and scope.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/BUILDING.md)
- `source`: [Sanitized historical device observation; legacy only.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/docs/evidence/legacy-hello.md)
- `source`: [Recorded migration checks and unresolved resolver gates, not hardware/build completion.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/docs/evidence/format2-validation.json)
- `source`: [Sanitized source-backed resource inventory with explicit omissions and disabled integration.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/docs/HARDWARE.md)

## 显示 {#display}

`planned`

### 硬件与依赖

- Panel, framebuffer and backlight metadata for this SKU.

### 配置

- Record actual board keys, device-tree properties, build flags and source revisions as resolved; no placeholder profile or feed value is treated as established.

### 操作步骤

- Use the documented offline workflow with explicit user-supplied inputs; preserve the command, source revision and observable result for each milestone.

### 开发经验

- Framebuffer/GOP handoff, panel timing, format, stride and backlight.
- Legacy GOP-backed display showed Apple Logo and multilingual Hello with a clean background. No fixed framebuffer address is put in DTS. The GUI quiet latch hides normal logs after first swap, so a persistent Logo alone does not identify the blocked service.

### 完成条件

- Known geometry/colors are correct through userland transition and backlight control.

### 当前范围

- Historical legacy kernel showed a clean multilingual Hello screen and home indicator; broader rendering/backlight validation is absent. This area is not claimed Format-2 implemented or verified.

### 下一步

- Capture geometry/format/timing from a reproducible build and validate UI transition/backlight.

### 证据

- `source`: [Public source snapshot facts and scope.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/README.md)
- `source`: [Sanitized historical device observation; legacy only.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/docs/evidence/legacy-hello.md)
- `source`: [Recorded migration checks and unresolved resolver gates, not hardware/build completion.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/docs/evidence/format2-validation.json)
- `source`: [Sanitized source-backed resource inventory with explicit omissions and disabled integration.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/docs/HARDWARE.md)

## 输入 {#input}

`planned`

### 硬件与依赖

- Goodix protocol, pin/power state, GPI ownership and verified mappings.

### 配置

- Record actual board keys, device-tree properties, build flags and source revisions as resolved; no placeholder profile or feed value is treated as established.

### 操作步骤

- Use the documented offline workflow with explicit user-supplied inputs; preserve the command, source revision and observable result for each milestone.

### 开发经验

- Goodix SPI SE4/static GPII0, TLMM, power/interrupt state and separate GPI/wrapper SMMU contexts.
- Goodix9916R uses SPI0x990000,CS0,15MHz child limit, GPIO20reset/GPIO21IRQ. GCC IDs94/134/135 and GPI TX0/RX1/SEID4/protocol1/64TREs are inventoried. Clock enable/read/restore and snapshot return are observed; no Goodix SPI transaction or physical iOS touch exists.

### 完成条件

- Goodix transaction completes with bounded DMA/events and iOS HID contacts operate through setup.

### 当前范围

- Physical iOS touch is not implemented. Clock/prerequisite probes and host decoders do not implement a GPI DMA provider or HID event path. This area is not claimed Format-2 implemented or verified.

### 下一步

- Establish DMA ownership/mappings, implement GPI completion and Goodix protocol, then verify HID delivery.

### 证据

- `source`: [Public source snapshot facts and scope.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/touch/MARBLE-GPI-DMA-PATH.md)
- `source`: [Sanitized historical device observation; legacy only.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/docs/evidence/legacy-hello.md)
- `source`: [Recorded migration checks and unresolved resolver gates, not hardware/build completion.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/docs/evidence/format2-validation.json)
- `source`: [Sanitized source-backed resource inventory with explicit omissions and disabled integration.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/docs/HARDWARE.md)
- `host`: [Host checks passed on the published source revision; no format-2 device, touch or DMA result.](https://github.com/sing0626/UniXNU-marble/actions/runs/40470393424)
  Command: <code>GitHub Actions Source checks: synthetic C fixtures, source integrity and fake-fastboot installer tests</code>. Revision: `28105e5831e680cfe50fa573b5b6ea85cb0f7b56`.

## GPU {#gpu}

`planned`

### 硬件与依赖

- GPU firmware, SMMU context and OS submission ABI.

### 配置

- Record actual board keys, device-tree properties, build flags and source revisions as resolved; no placeholder profile or feed value is treated as established.

### 操作步骤

- Use the documented offline workflow with explicit user-supplied inputs; preserve the command, source revision and observable result for each milestone.

### 开发经验

- GPU/GMU generation, firmware, clocks/votes, SMMU and submission ABI.
- No GPU/Metal support is claimed. The current Adreno740 catalog entry is SM8550-specific and is not selected for this SM7475 board.

### 完成条件

- Verified GPU/GMU init and submission/fence path; acceleration scope documented.

### 当前范围

- No GPU acceleration result is claimed; Hello display does not prove GPU operation. This area is not claimed Format-2 implemented or verified.

### 下一步

- Inventory the stack and define a bounded submit/fence checkpoint before component selection.

### 证据

- `source`: [Public source snapshot facts and scope.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/README.md)
- `source`: [Recorded migration checks and unresolved resolver gates, not hardware/build completion.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/docs/evidence/format2-validation.json)

## 网络 {#network}

`planned`

### 硬件与依赖

- Device network firmware, transport and DMA mapping.

### 配置

- Record actual board keys, device-tree properties, build flags and source revisions as resolved; no placeholder profile or feed value is treated as established.

### 操作步骤

- Use the documented offline workflow with explicit user-supplied inputs; preserve the command, source revision and observable result for each milestone.

### 开发经验

- Wi-Fi/cellular hardware, firmware, interrupts, DMA and OS interfaces.
- No iOS Wi-Fi/cellular association or packet transfer is verified; firmware, DMA and OS-interface wiring remain pending rather than filled with assumed values.

### 完成条件

- Device associates and transfers packets through the OS interface.

### 当前范围

- No network association or packet transfer is claimed. This area is not claimed Format-2 implemented or verified.

### 下一步

- Inventory one network transport and firmware dependency before implementation.

### 证据

- `source`: [Public source snapshot facts and scope.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/README.md)
- `source`: [Recorded migration checks and unresolved resolver gates, not hardware/build completion.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/docs/evidence/format2-validation.json)

## 音频 {#audio}

`planned`

### 硬件与依赖

- DSP/codec firmware, clocking and routes.

### 配置

- Record actual board keys, device-tree properties, build flags and source revisions as resolved; no placeholder profile or feed value is treated as established.

### 操作步骤

- Use the documented offline workflow with explicit user-supplied inputs; preserve the command, source revision and observable result for each milestone.

### 开发经验

- DSP, codec, clocks, firmware services and routes.
- No DSP/codec route or iOS playback/capture is verified. The record does not infer working audio from kernel or Hello progress.

### 完成条件

- At least one documented playback/capture route works.

### 当前范围

- No audio playback or capture is claimed. This area is not claimed Format-2 implemented or verified.

### 下一步

- Trace the DSP/codec dependencies and define a playback or loopback checkpoint.

### 证据

- `source`: [Public source snapshot facts and scope.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/README.md)
- `source`: [Recorded migration checks and unresolved resolver gates, not hardware/build completion.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/docs/evidence/format2-validation.json)

## 电源 {#power}

`planned`

### 硬件与依赖

- Rail/clock ownership, battery units and transition policy.

### 配置

- Record actual board keys, device-tree properties, build flags and source revisions as resolved; no placeholder profile or feed value is treated as established.

### 操作步骤

- Use the documented offline workflow with explicit user-supplied inputs; preserve the command, source revision and observable result for each milestone.

### 开发经验

- Regulators, clocks, battery units, firmware ownership and supported transitions.
- The bounded legacy S4 probe temporarily set its owned GCC vote and restored it; this is not complete touch rail/reset sequencing or battery/power-management support.

### 完成条件

- Rails/clocks are owned and a supported power transition recovers correctly.

### 当前范围

- Touch clock probe has narrow read/restore scope; it is not system power management. This area is not claimed Format-2 implemented or verified.

### 下一步

- Document ownership and validate a controlled suspend/resume transition.

### 证据

- `source`: [Public source snapshot facts and scope.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/touch/MARBLE-GPI-DMA-PATH.md)
- `source`: [Recorded migration checks and unresolved resolver gates, not hardware/build completion.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/docs/evidence/format2-validation.json)
- `source`: [Sanitized source-backed resource inventory with explicit omissions and disabled integration.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/docs/HARDWARE.md)
- `host`: [Host checks passed on the published source revision; no format-2 device, touch or DMA result.](https://github.com/sing0626/UniXNU-marble/actions/runs/40470393424)
  Command: <code>GitHub Actions Source checks: synthetic C fixtures, source integrity and fake-fastboot installer tests</code>. Revision: `28105e5831e680cfe50fa573b5b6ea85cb0f7b56`.

## 镜像组装 {#packaging}

`planned`

### 硬件与依赖

- Pinned public source inputs and user-provided proprietary restore data.

### 配置

- Record actual board keys, device-tree properties, build flags and source revisions as resolved; no placeholder profile or feed value is treated as established.

### 操作步骤

- Use the documented offline workflow with explicit user-supplied inputs; preserve the command, source revision and observable result for each milestone.

### 开发经验

- Matching iOS restore input, XNU, ADT, generated trust-cache data, payload and boot-image format.
- The restore input is iPhone10,6/d221ap iOS16.7.16/20H392, chip0x8015 board0x0e; six exact member SHA256 pins were recomputed without publishing binaries. The 64MiB payload/header-v4 legacy recipe and monolithic patch are inventoried, not validated as a modern format-2 stack.

### 完成条件

- Clean build/package from pinned source plus user inputs reproduces checksummed output.

### 当前范围

- No IPSW/root filesystem/firmware/boot image is published; current snapshot is not a full reproduction package. This area is not claimed Format-2 implemented or verified.

### 下一步

- Reconstruct from pinned public inputs and user-provided data; produce clean auditable package before migration claims.

### 证据

- `source`: [Public source snapshot facts and scope.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/BUILDING.md)
- `source`: [Public source snapshot facts and scope.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/legacy-xnu/README.md)
- `source`: [Sanitized historical device observation; legacy only.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/docs/evidence/legacy-hello.md)
- `source`: [Recorded migration checks and unresolved resolver gates, not hardware/build completion.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/docs/evidence/format2-validation.json)
- `source`: [Matching restore identity and recomputed member hashes; no Apple binary content.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/docs/evidence/ios16-inputs.json)

## 诊断 {#diagnostics}

`planned`

### 硬件与依赖

- Recoverable boot/log path and identified source/image artifacts.

### 配置

- Record actual board keys, device-tree properties, build flags and source revisions as resolved; no placeholder profile or feed value is treated as established.

### 操作步骤

- Use the documented offline workflow with explicit user-supplied inputs; preserve the command, source revision and observable result for each milestone.

### 开发经验

- Log transport, checkpoints, recovery and source/image identities.
- Official pinned checker reports13 structured areas, and the sanitized DTS compiles without diagnostics. Actual defconfig/status/tree attempts stop at the absent reviewed sm7475 SoC source; even an implemented local SoC would still need the missing iOS16 OS profile. Reference lock verification ran on Linux/WSL, not a whole-target build.

### 完成条件

- Recovery and logs correlate checkpoints with exact source and artifact revisions.

### 当前范围

- Private recordings/logs are excluded; only sanitized observation summary is public. Logo-only probes do not establish a specific failure cause. This area is not claimed Format-2 implemented or verified.

### 下一步

- Publish reproducible source/image identifiers and bounded log checkpoints.

### 证据

- `source`: [Sanitized historical device observation; legacy only.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/docs/evidence/legacy-hello.md)
- `source`: [Public source snapshot facts and scope.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/STATUS.md)
- `source`: [Recorded migration checks and unresolved resolver gates, not hardware/build completion.](https://github.com/sing0626/UniXNU-marble/blob/a63260314d130ebf02a987f0785f5ae3258c219c/docs/evidence/format2-validation.json)
- `host`: [Host checks passed on the published source revision; no format-2 device, touch or DMA result.](https://github.com/sing0626/UniXNU-marble/actions/runs/40470393424)
  Command: <code>GitHub Actions Source checks: synthetic C fixtures, source integrity and fake-fastboot installer tests</code>. Revision: `28105e5831e680cfe50fa573b5b6ea85cb0f7b56`.

</div>
