# Xiaomi Redmi Note 3 \(Kenzo\) Snapdragon 650

[CodeDevB7/UniXNU-kenzo](https://github.com/CodeDevB7/UniXNU-kenzo)

<div v-pre>

Xiaomi Redmi Note 3 \(kenzo\) Snapdragon 650 porting record.

源记录: [porting.toml](https://github.com/CodeDevB7/UniXNU-kenzo/blob/c472ccc1102a772f9e84261d8240be4eec6d7dca/porting.toml), `c472ccc1102a772f9e84261d8240be4eec6d7dca`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `host-verified` |
| [固件与启动](#firmware) | `planned` |
| [CPU 与中断](#cpu) | `implemented` |
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

`host-verified`

组件: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`, `DarwinBoot`.

### 硬件与依赖

- Xiaomi Redmi Note 3, codename kenzo; Qualcomm MSM8956; selected profile ipados-17.7.11-21H461.
- Shared SoC feed points to CodeDevB7/UniXNU-msm8956-common at c9652aca1fe3c530ef79f5dae584dd85e61b1f8c.

### 配置

- board.toml selects ArmDTPlatform, ArmCpu, SoftwareAES, XnuPrelink and DarwinBoot; kenzo\_defconfig; SoC and OS config fragments; ordered arch, SoC, OS and device patch series.
- \[package\] unixnu is ../UniXNU and \[package.defconfig\] maps ipados-17.7.11-21H461 to kenzo\_defconfig.

### 操作步骤

- Resolve board configuration from the UniXNU checkout with unixnu status -D UniXNU-kenzo.
- Run scripts/package.sh --check --os ipados-17.7.11-21H461 from the device repository after required local sources are available.
- Dispatch .github/workflows/kernel.yml to compile only the kernel on a macOS runner and inspect its redacted logs.

### 开发经验

- The current repository uses format 2 and the shared SoC feed; the older handoff's build workflow description predates the current package interface.
- The package script previously stopped immediately because \[package\].unixnu was absent; after recording the path and profile-to-defconfig mapping, host preflight resolved kenzo\_defconfig and all 59 patches.
- The local set of 86 extracted DTBs contains Qualcomm MSM8956 reference platforms, but no root model/compatible identifying Kenzo; these files do not validate board wiring.
- The kernel-only macOS workflow calls UniXNU's reusable build and uploads text logs only. Its pre-build helper removes only the optional Sheng PMGR probe hunk from the generic boot-progress patch; it fails closed if the upstream hunk layout changes.
- Local compilation was stopped at the user's request after filesystem and bootstrap issues; no kernel artifact is claimed. The workflow run is the next build attempt.

### 完成条件

- The pinned SoC source resolves; package preflight writes the selected configuration and patch resolution completes for the selected OS profile.

### 当前范围

- Package preflight, patch resolution and standalone DTS-to-ADT generation are host-verified. Kernel, UEFI firmware, payload, image assembly and device boot are unverified. The macOS Actions kernel run is pending. Firmware repository, image inputs and device seed are not configured.

### 下一步

- Run the macOS kernel workflow and record its result; identify the Kenzo UEFI source and verify board firmware paths and hardware inputs before attempting a complete package build.

### 证据

- `source`: [Format 2 board selection and package path/defconfig mapping.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/c472ccc1102a772f9e84261d8240be4eec6d7dca/board.toml)
- `source`: [Pinned MSM8956 shared SoC feed.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/c472ccc1102a772f9e84261d8240be4eec6d7dca/feeds.toml)
- `source`: [No Kenzo-compatible root was found among 86 extracted DTBs; only Qualcomm MSM8956 reference platform trees matched.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/c472ccc1102a772f9e84261d8240be4eec6d7dca/evidence/2026-11-12-dtb-inventory.md)
- `source`: [Local XNU patching needed a Sheng-only hunk workaround; builds on /mnt/c failed during atomic header replacement, and the ext4 retry was interrupted before completion.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/c472ccc1102a772f9e84261d8240be4eec6d7dca/evidence/2026-11-12-local-kernel-attempt.md)
- `source`: [Pre-build helper removes only the optional Sheng PMGR progress hunk and fails if its recognized layout changes.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/c472ccc1102a772f9e84261d8240be4eec6d7dca/scripts/prepare-kernel-patches.py)
- `source`: [Reusable macOS workflow provides a kernel-only build with redacted text logs and no image artifacts.](https://github.com/UniXNU/UniXNU/blob/c34f018aafd6befd5dc93c05a8dccd5bdce6724b/.github/workflows/macos.yml)
- `host`: [Passed on WSL/Linux against SoC pin 894aea231e7ac7133b2947777b2dbc89bdd4c6aa: wrote config for kenzo\_defconfig, extracted profile IPSW inputs, resolved 59 patches. UniXNU source revision 5a00e20157f3975d155f13ced7593347f9f5bf73.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/c472ccc1102a772f9e84261d8240be4eec6d7dca/evidence/2026-11-12-package-check.md)
  Command: <code>bash scripts/package.sh --check --os ipados-17.7.11-21H461</code>. Revision: `b9280aaa8c6f7fd2622bdc0b28aea8b9c35438a7`.
- `host`: [DTS compiled and generated a 12,888-byte ADT on WSL/Linux. The standalone generator completed; this does not verify UEFI or device boot. SoC revision 894aea231e7ac7133b2947777b2dbc89bdd4c6aa; UniXNU revision 5a00e20157f3975d155f13ced7593347f9f5bf73.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/c472ccc1102a772f9e84261d8240be4eec6d7dca/evidence/2026-11-12-adt-preflight.md)
  Command: <code>dtc -I dts -O dtb -i &lt;msm8956 DTSI&gt; -o /tmp/kenzo-hardware.dtb dts/kenzo.dts; python3 scripts/make-adt.py --dtb /tmp/kenzo-hardware.dtb --os-profile profiles/os/ipados-17.7.11-21H461/profile.toml --board ../UniXNU-kenzo/board.toml --output /tmp/kenzo.adt</code>. Revision: `b9280aaa8c6f7fd2622bdc0b28aea8b9c35438a7`.

## 固件与启动 {#firmware}

`planned`

### 硬件与依赖

- Kenzo stock Android boot image and extracted device-tree data are present in the sibling kenzo-dump directory; no Kenzo Mu-Silicium/EDK2 checkout is present in this workspace.

### 配置

- board.toml currently names a provisional Kenzo DSC/FD path; there is no firmware image pin, preflight script or confirmed firmware output.

### 操作步骤

- Follow the UniXNU UEFI integration guide, then build and inspect the device FD and boot image on a supported host.

### 开发经验

- No UEFI build or physical boot evidence is recorded. The current firmware fields were adapted from a template and must be replaced with paths verified against a Kenzo firmware checkout.

### 完成条件

- Firmware image builds, enters UniXNU, publishes the framebuffer and preserves the documented memory reservations.

### 当前范围

- UEFI source, its revision, required Mu-Silicium modules, memory reservations, framebuffer handoff and firmware build output are unknown.

### 下一步

- Identify a maintained MSM8956/Kenzo Mu-Silicium port, inspect its DSC/FDF and board configuration, then replace provisional firmware paths and record the firmware revision.

### 证据

按下一步操作收集证据。

## CPU 与中断 {#cpu}

`implemented`

组件: `ArmCpu`.

### 硬件与依赖

- The local cpuinfo reports six processors; the shared SoC definition declares four Cortex-A53 and two Cortex-A72 cores. Earlier hardware notes list GICv2 and a 19.2 MHz architectural timer.
- The local extracted DTB set contains MSM8956 MTP/CDP/QRD/simulator reference trees but no root compatible identifying Kenzo.

### 配置

- The shared SoC DTSI sets /cpus/timebase-frequency to 19200000, CPU affinity values 0-3 and 0x100-0x101, PSCI method smc, GICv2 ranges 0x0b000000/0x1000 and 0x0b002000/0x1000, and exports the controller as intc.
- The board configuration selects ArmCpu; the SoC fragment enables the GIC and architectural timer.

### 操作步骤

- Compile dts/kenzo.dts with the pinned SoC include using dtc -I dts -O dtb.
- Generate the selected OS/device ADT with scripts/make-adt.py and inspect the output against required XNU nodes.
- Before claiming hardware bring-up, compare the MPIDRs, PSCI and interrupt resources with a Kenzo-specific DTB and capture per-core XNU logs.

### 开发经验

- The MSM8956 SoC DTSI now supplies /cpus/timebase-frequency, routes interrupts to the GIC, and exports the GIC as ADT node intc. DTC and standalone ADT generation pass. CPU MPIDR values and GIC ranges are based on MSM8956 reference data, not a Kenzo-compatible DTB; no XNU secondary-core or IPI bring-up has been measured.

### 完成条件

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU.

### 当前范围

- Per-core MPIDR values, GIC interrupt specifiers, PSCI availability and IPI behavior have not been verified from the selected board DTB or on-device logs.

### 下一步

- Obtain the matching Kenzo DTB from stock firmware, then verify CPU reg/MPIDRs, GIC distributor and CPU-interface ranges, timer and PSCI nodes; validate on hardware after a UEFI boot path exists.

### 证据

- `source`: [SoC DTSI provides the timebase, interrupt-parent and exported GIC node required by the ADT generator.](https://github.com/CodeDevB7/UniXNU-msm8956-common/commit/894aea231e7ac7133b2947777b2dbc89bdd4c6aa)
- `source`: [The extracted MSM8956 trees identify only reference platforms; they are insufficient evidence for Kenzo-specific CPU/GIC values.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/c472ccc1102a772f9e84261d8240be4eec6d7dca/evidence/2026-11-12-dtb-inventory.md)
- `source`: [The board DTS compiled and standalone ADT generation completed on the host; physical CPU/GIC behavior is unverified.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/c472ccc1102a772f9e84261d8240be4eec6d7dca/evidence/2026-11-12-adt-preflight.md)

## 内存与 DMA {#memory}

`planned`

### 硬件与依赖

- The local dump reports MemTotal 1889528 kB and the current Kenzo DTS declares RAM at 0x80000000 with a 0x80000000 size.
- Extracted MSM8956 reference DTBs do not identify Kenzo and cannot establish this board's DRAM banks or reservations.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for memory and dma.

### 操作步骤

- Follow the memory and dma stage in the porting guide and record the actual commands.

### 开发经验

- MemTotal supports the 2 GiB board variant, but does not establish the complete physical bank or reserved regions. The earlier DTS comment mentioned a 3 GB variant while its reg entry described only 2 GiB; it now identifies the captured unit's 2 GiB range without making a claim about other variants.

### 完成条件

- All handoff regions are accounted for and each enabled DMA engine accesses its allocated range with the documented cache policy.

### 当前范围

- Complete DRAM banks, firmware carveouts, DMA addressability, cache policy and SMMU ownership remain unverified.

### 下一步

- Extract /memory and /reserved-memory from the matching Kenzo DTB, then reconcile with the UEFI handoff map before setting payload memory values.

### 证据

- `source`: [The local extracted set has no Kenzo-compatible root, so its Qualcomm memory nodes cannot validate this board's map.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/c472ccc1102a772f9e84261d8240be4eec6d7dca/evidence/2026-11-12-dtb-inventory.md)

## 存储与根卷 {#storage}

`planned`

### 硬件与依赖

- Identify the storage and root hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for storage and root.

### 操作步骤

- Follow the storage and root stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first storage and root observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Host: register, clock, link and SMMU facts match the board inventory.
- Reads: SCSI capacity, GPT and known blocks are correct; OS/SystemOS windows stay within userdata.
- Root: the configured volume mounts and launchd starts. Persistence: writes survive reboot within the allocated Data region.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required storage and root inputs before implementation.

### 证据

按下一步操作收集证据。

## 显示 {#display}

`planned`

### 硬件与依赖

- Identify the display hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for display.

### 操作步骤

- Follow the display stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first display observation, its cause when established, and the resulting implementation decision.

### 完成条件

- A known frame appears with correct geometry and colors, then userland presentation and backlight controls work.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required display inputs before implementation.

### 证据

按下一步操作收集证据。

## 输入 {#input}

`planned`

### 硬件与依赖

- Identify the input hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for input.

### 操作步骤

- Follow the input stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first input observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive, and buttons produce expected HID reports.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required input inputs before implementation.

### 证据

按下一步操作收集证据。

## GPU {#gpu}

`planned`

### 硬件与依赖

- Identify the gpu hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for gpu.

### 操作步骤

- Follow the gpu stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first gpu observation, its cause when established, and the resulting implementation decision.

### 完成条件

- GPU submissions complete, mapping/fence handling is correct, a known image renders, and the selected Metal client presents it.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required gpu inputs before implementation.

### 证据

按下一步操作收集证据。

## 网络 {#network}

`planned`

### 硬件与依赖

- Identify the network hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for network.

### 操作步骤

- Follow the network stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first network observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Scanning, association, address configuration and sustained receive/transmit traffic pass with the selected firmware.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required network inputs before implementation.

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`planned`

### 硬件与依赖

- Identify the audio hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for audio.

### 操作步骤

- Follow the audio stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first audio observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Each declared route carries the selected audio format through playback or capture and handles start/stop correctly.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required audio inputs before implementation.

### 证据

按下一步操作收集证据。

## 电源 {#power}

`planned`

### 硬件与依赖

- Identify the power hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for power.

### 操作步骤

- Follow the power stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first power observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Declared power controls and battery readings match observations; each claimed sleep/resume transition restores its dependent peripherals.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required power inputs before implementation.

### 证据

按下一步操作收集证据。

## 镜像组装 {#packaging}

`planned`

### 硬件与依赖

- Identify the image assembly hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for image assembly.

### 操作步骤

- Follow the image assembly stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first image assembly observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Kernel and prelink succeed, payload contains all declared inputs, and the boot image matches the bootloader format and size limit.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required image assembly inputs before implementation.

### 证据

按下一步操作收集证据。

## 诊断 {#diagnostics}

`planned`

### 硬件与依赖

- Identify the diagnostics hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for diagnostics.

### 操作步骤

- Follow the diagnostics stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first diagnostics observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Each claimed milestone has a reproducible command, a matching source/image revision and an accessible result.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required diagnostics inputs before implementation.

### 证据

按下一步操作收集证据。

</div>
