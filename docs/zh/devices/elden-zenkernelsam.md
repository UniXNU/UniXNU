# Lenovo Legion Y700 Gen 4 \(zenkernelsam\)

[zenkernelsam/UniXNU_elden](https://github.com/zenkernelsam/UniXNU_elden)

<div v-pre>

v156 adds verified UFS automatic idle/wake and restoration to the v15532-slot direct-DMA path. Charging cycles/net power, wireless, persistence, memory and remaining peripherals are incomplete; GPU is separate offline work.

源记录: [porting.toml](https://github.com/zenkernelsam/UniXNU_elden/blob/c4ebf12968e342bf7941781bc3ed0467060eb364/porting.toml), `c4ebf12968e342bf7941781bc3ed0467060eb364`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `host-verified` |
| [固件与启动](#firmware) | `device-verified` |
| [CPU 与中断](#cpu) | `implemented` |
| [内存与 DMA](#memory) | `implemented` |
| [存储与根卷](#storage) | `implemented` |
| [显示](#display) | `implemented` |
| [输入](#input) | `implemented` |
| [GPU](#gpu) | `planned` |
| [网络](#network) | `implemented` |
| [音频](#audio) | `planned` |
| [电源](#power) | `implemented` |
| [镜像组装](#packaging) | `device-verified` |
| [诊断](#diagnostics) | `device-verified` |
| [network-initialization](#network-initialization) | `device-verified` |
| [memory-window8](#memory-window8) | `device-verified` |
| [spmi-adc-bt-serialization](#spmi-adc-bt-serialization) | `host-verified` |
| [spmi-hci-v114](#spmi-hci-v114) | `implemented` |

## 配置 {#configuration}

`host-verified`

组件: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`, `DarwinBoot`.

### 硬件与依赖

- Use the ARM64 and iPadOS 17.7.11 profiles supplied by UniXNU.
- Select the shared platform, CPU and DarwinBoot components.
- Provide an SM8750 profile until an official shared SoC repository exists.

### 配置

- Frozen v91 inputs and explicit experimental v92 separation; see docs/REPRODUCIBILITY.md.

### 操作步骤

- Follow docs/PLAN.md and retain identity, fresh power, floor and full SHA admission.

### 开发经验

- Frozen v91 source profile imported and verified.

### 完成条件

- board.toml resolves four ordered configuration layers.
- All selected components come from the UniXNU catalog and include their dependencies.
- No array field depends accidentally on inheritance.
- The SoC source is a reviewed remote commit and unixnu.lock records it.

### 当前范围

- Default board/lock remains the historical early profile; no clean final boot reproduction yet.

### 下一步

- Finish clean full-kernel and packaging dependency closure.

### 证据

- `host`: [Frozen v91 source profile imported and verified. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/c4ebf12968e342bf7941781bc3ed0467060eb364/docs/REPRODUCIBILITY.md)
  Command: <code>Read frozen source/hardware manifests; no new device operation during maintenance</code>. Revision: `c7fae2baaaad4be7406de3691a4e79cc5cc48664`.

## 固件与启动 {#firmware}

`device-verified`

组件: `DarwinBoot`.

### 硬件与依赖

- mu\_wide\_platforms lenovo-y700g4 UEFI source and patched PMIC binaries.
- UniXNU, UniXNUDxe, DarwinBoot and EldenRamDiskDxe firmware modules.
- A 4 MiB FAT16 payload containing package/unixnu.toml.

### 配置

- Frozen v91 inputs and explicit experimental v92 separation; see docs/REPRODUCIBILITY.md.

### 操作步骤

- Follow docs/PLAN.md and retain identity, fresh power, floor and full SHA admission.

### 开发经验

- Existing UniXNU menu, payload handoff and recovery firmware boot the v91 kernel.

### 完成条件

- Firmware contains UniXNU, UniXNUDxe, DarwinBoot and the RAM payload driver.
- The payload config is readable and the menu accepts volume-key input.
- Two RAM boots produce the same visible checkpoint and do not modify persistent partitions.

### 当前范围

- Not a claim that every firmware configuration or KShimC route is qualified.

### 下一步

- Retain frozen firmware inputs and finish portable build mapping.

### 证据

- `device`: [Existing UniXNU menu, payload handoff and recovery firmware boot the v91 kernel. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/c4ebf12968e342bf7941781bc3ed0467060eb364/docs/CURRENT-STATUS.md)
  Command: <code>Read frozen source/hardware manifests; no new device operation during maintenance</code>. Revision: `c7fae2baaaad4be7406de3691a4e79cc5cc48664`.

## CPU 与中断 {#cpu}

`implemented`

组件: `ArmCpu`.

### 硬件与依赖

- SM8750 MPIDRs 0x0, 0x100, 0x200, 0x300, 0x400, 0x500, 0x10000 and 0x10100.
- GICv3 distributor 0x16000000, redistributor base 0x16080000 and stride 0x40000.
- 19.2 MHz architectural timer and PSCI SMC conduit.

### 配置

- Frozen v91 inputs and explicit experimental v92 separation; see docs/REPRODUCIBILITY.md.

### 操作步骤

- Follow docs/PLAN.md and retain identity, fresh power, floor and full SHA admission.

### 开发经验

- CPU8 source configuration, identity/IRQ changes and guarded startup are captured in v91.

### 完成条件

- The boot CPU reaches the ArmCpu checkpoint.
- GIC distributor and its own redistributor frame map successfully.
- Timer handling works before secondary cores or IPI transport are qualified.

### 当前范围

- Configured CPUs do not prove sustained online load or explain UI stalls.

### 下一步

- Measure online CPUs, scheduler/IRQ progress and actual latency with the UI workload.

### 证据

- `host`: [CPU8 source configuration, identity/IRQ changes and guarded startup are captured in v91. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/c4ebf12968e342bf7941781bc3ed0467060eb364/docs/CURRENT-STATUS.md)
  Command: <code>Read frozen source/hardware manifests; no new device operation during maintenance</code>. Revision: `c7fae2baaaad4be7406de3691a4e79cc5cc48664`.

## 内存与 DMA {#memory}

`implemented`

组件: `ArmDTPlatform`.

### 硬件与依赖

- The owner-captured live elden FDT, including the 12 GiB RAM map, initrd and reserved-memory nodes.
- The pinned Linux 16 GiB variant and the elden UEFI static memory map.
- A conservative 256 MiB XNU handoff window in UEFI DXE conventional memory.

### 配置

- Frozen v91 inputs and explicit experimental v92 separation; see docs/REPRODUCIBILITY.md.

### 操作步骤

- Follow docs/PLAN.md and retain identity, fresh power, floor and full SHA admission.

### 开发经验

- v91 retains the validated high-address RAM configuration.

### 完成条件

- The ADT contains exactly one continuous memory range.
- The range is covered by live firmware RAM and avoids recorded reservations, initrd, GOP and UEFI FD.
- DarwinBoot and the UEFI exit map confirm that same range is conventional memory before XNU entry.

### 当前范围

- Full 16GB adoption and memory stress are incomplete.

### 下一步

- Keep frozen memory inputs during UI work; expand after map qualification.

### 证据

- `host`: [v91 retains the validated high-address RAM configuration. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/c4ebf12968e342bf7941781bc3ed0467060eb364/docs/CURRENT-STATUS.md)
  Command: <code>Read frozen source/hardware manifests; no new device operation during maintenance</code>. Revision: `c7fae2baaaad4be7406de3691a4e79cc5cc48664`.

## 存储与根卷 {#storage}

`implemented`

组件: `ShengUfs`.

### 硬件与依赖

- SM8750 UFS host at 0x1d84000 \(+0x3000\) and QMP PHY at 0x1d80000 \(+0x2000\), both described by the same-device Linux tree sm8750-lenovo-elden.dts and sm8750.dtsi pinned at bf96c3d4048973298ede78487177c6f1b4f6bc0f.
- Controller resources: GIC\_SPI 265 level-high, 8 GCC/RPMh clocks, GCC\_UFS\_PHY\_BCR, GCC\_UFS\_PHY\_GDSC, apps\_smmu stream 0x60, lanes-per-direction 2, ICE crypto@1d88000.
- PHY resources: RPMH\_CXO\_CLK, GCC\_UFS\_PHY\_PHY\_AUX\_CLK, TCSR\_UFS\_CLKREF\_EN, GCC\_UFS\_MEM\_PHY\_GDSC.
- Board supplies and reset: PHY vreg\_l1j\_0p91 and vreg\_l3g\_1p2, host vreg\_l17b\_2p5 \(1.3 A\) and vreg\_l1d\_1p2 \(1.2 A\), reset GPIO tlmm 215 active-low.
- 4 KiB logical-sector partition geometry and a root-volume UUID, both owner-supplied and read-only.
- v152 IRQ binding uses ArmadaOS TB322FC -&gt; h0cheung6f97250ead155fc3b980856323e99a4623dae73d sm8750.dtsi SPI265/INTID297; inherited transport/DMA ownership is unchanged.

### 配置

- Frozen v91 inputs and explicit experimental v92 separation; see docs/REPRODUCIBILITY.md.

### 操作步骤

- Follow docs/PLAN.md and retain identity, fresh power, floor and full SHA admission.

### 开发经验

- UFS-backed iPadOS root, RAM Data, launchd and Settings have run.
- v149 declares the existing UFS windows and RAM Data nonrotating. The actual iPadOS17 ioctl path reports isssd=1 for all three BSD units; transport remains single-slot polling and RAM remains volatile.
- v152 keeps the single slot but enables completion IRQ and bounded scheduler-aware waiting. Both whole-image pins and64 paired hashes/128 samples passed, with128 sample IRQs/5 IRQ wakes. Entire session2114 sleeps/wakes and no wait timeouts; root and stock Android restored. Warm QD1 latency did not show a consistent speedup. The current block-hash tables already reside entirely in protected RAM.
- v155 enables32 slots, a qualified independent NC request list and prepared driver-owned direct DMA. Both whole-image pins and48 batches/1536 commands/16 matched datasets passed; actual outstanding doorbells peaked27. Fixed-order QD32 128KiB reads recorded2430-2837MiB/s; cache/order bias prevents a causal speedup or GUI claim. Stock restoration passed.

### 完成条件

- Controller and PHY initialize.
- Read-only capacity, GPT and known-block checks match the device.
- The configured OS volume mounts and launchd starts.

### 当前范围

- Persistent Data and UFS performance are not fully qualified.
- v155 has not qualified sustained pressure, BUSY/TASK\_SET\_FULL retry policy, CPU utilization or UI latency. Diagnostic batch reads should not recur in unrelated candidates.

### 下一步

- Retain the verified queue/DMA path and remove diagnostic batch calls in the next feature build; continue Wi-Fi hardware integration. Qualify stress, CPU/UI latency and persistence separately rather than repeating the completed QD trial.

### 证据

- `host`: [UFS-backed iPadOS root, RAM Data, launchd and Settings have run. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/c4ebf12968e342bf7941781bc3ed0467060eb364/docs/CURRENT-STATUS.md)
  Command: <code>Read frozen source/hardware manifests; no new device operation during maintenance</code>. Revision: `c7fae2baaaad4be7406de3691a4e79cc5cc48664`.
- `device`: [Three property readbacks and six ioctl outcomes passed; root and Android restoration passed. No throughput or energy-saving benchmark; drop132 and unconfirmed human touch source retained.](https://github.com/zenkernelsam/UniXNU_elden/blob/c4ebf12968e342bf7941781bc3ed0467060eb364/profiles/storage-medium/hardware.json)
  Command: <code>Run the v149 signed storage-medium candidate, retain existing spec_open SSD outcomes and property readbacks, then perform session-bound sync/reset and full-SHA stock Android restore.</code>. Revision: `8af7569707e0401fc24b2999e5edbbe37ab26609`.
- `device`: [128 rows/64 paired hashes; actual IRQ wakes and recovery passed.3129911B/drop26/no reconnect; no sustained throughput, CPU utilization or user-visible speedup claim.](https://github.com/zenkernelsam/UniXNU_elden/blob/c4ebf12968e342bf7941781bc3ed0467060eb364/profiles/ufs-wait-trial/hardware.json)
  Command: <code>Run v152 paired pinned-block trial, retain complete rows and IRQ/stop counters, then session-bound sync/reset and full-SHA stock Android restoration.</code>. Revision: `1629b24a472f7b19d74cf5d5fb5aa8059c5ff0cf`.
- `device`: [32-slot NC mapping/1536 direct reads and root/SMP/return passed.3185070B/drop155/no reconnect; fixed order/cache and high-SOC current limitations retained. v154 refusal and recovery archived separately.](https://github.com/zenkernelsam/UniXNU_elden/blob/c4ebf12968e342bf7941781bc3ed0467060eb364/profiles/ufs-queue-trial/hardware.json)
  Command: <code>Run the complete v155 QD1/8/32 candidate with retained snapshot DMA, full image pins and read-hash matching; then verify sync/reset and full-SHA stock Android restoration.</code>. Revision: `7c6553abb4e8f3de21b63a00c17004e9a8d9ebb0`.

## 显示 {#display}

`implemented`

组件: `GopFramebuffer`, `AppleKeyStoreState`.

### 硬件与依赖

- 1904x3040 bonded dual-DSI panel with DSC.
- UEFI GOP framebuffer and splash reservation.
- SM8750 DPU/DSI/PHY and backlight sequencing.

### 配置

- Frozen v91 inputs and explicit experimental v92 separation; see docs/REPRODUCIBILITY.md.

### 操作步骤

- Follow docs/PLAN.md and retain identity, fresh power, floor and full SHA admission.

### 开发经验

- v91 renders a populated Settings page with the owned CPU graphic-variant helper.

### 完成条件

- XNU paints a known pattern through a declared framebuffer handoff.
- Userland presentation and backlight transitions work.

### 当前范围

- Display fluidity and v92 framebuffer mapping remain unqualified.

### 下一步

- Qualify v92 offline, then use one meaningful display/input function test.

### 证据

- `host`: [v91 renders a populated Settings page with the owned CPU graphic-variant helper. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/c4ebf12968e342bf7941781bc3ed0467060eb364/docs/CURRENT-STATUS.md)
  Command: <code>Read frozen source/hardware manifests; no new device operation during maintenance</code>. Revision: `c7fae2baaaad4be7406de3691a4e79cc5cc48664`.

## 输入 {#input}

`implemented`

组件: `ShengHidInput`.

### 硬件与依赖

- Novatek SPI touch on SPI4 and GPIO 162 interrupt.
- Volume and power keys used by the UEFI menu.

### 配置

- Frozen v91 inputs and explicit experimental v92 separation; see docs/REPRODUCIBILITY.md.

### 操作步骤

- Follow docs/PLAN.md and retain identity, fresh power, floor and full SHA admission.

### 开发经验

- One software swipe and one short Settings tap reached the real Settings UI in v91.

### 完成条件

- Touch coordinates map to the display.
- Contact IDs, releases and multi-touch remain stable.
- Buttons produce expected HID events in XNU.

### 当前范围

- Physical finger accuracy, ghost-touch rejection and consistent gestures remain incomplete.

### 下一步

- Correlate a real touch with raw contact, HID event and UI response in one bounded session.

### 证据

- `host`: [One software swipe and one short Settings tap reached the real Settings UI in v91. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/c4ebf12968e342bf7941781bc3ed0467060eb364/docs/CURRENT-STATUS.md)
  Command: <code>Read frozen source/hardware manifests; no new device operation during maintenance</code>. Revision: `c7fae2baaaad4be7406de3691a4e79cc5cc48664`.

## GPU {#gpu}

`planned`

### 硬件与依赖

- Adreno 830 / gen80000.
- GPU firmware, power votes, SMMU and display integration.

### 配置

- Frozen v91 inputs and explicit experimental v92 separation; see docs/REPRODUCIBILITY.md.

### 操作步骤

- Follow docs/PLAN.md and retain identity, fresh power, floor and full SHA admission.

### 开发经验

- Reference sources and inactive experimental components are preserved.

### 完成条件

- GPU submissions, fences and mapping work.
- A known image renders and Metal presentation is visible.

### 当前范围

- No GPU daily-use qualification.

### 下一步

- GPU last, after basic peripherals and CPU display are usable.

### 证据

- `host`: [Reference sources and inactive experimental components are preserved. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/c4ebf12968e342bf7941781bc3ed0467060eb364/docs/CURRENT-STATUS.md)
  Command: <code>Read frozen source/hardware manifests; no new device operation during maintenance</code>. Revision: `c7fae2baaaad4be7406de3691a4e79cc5cc48664`.

## 网络 {#network}

`implemented`

### 硬件与依赖

- WCN7861 Wi-Fi/Bluetooth shared power, transport and firmware.

### 配置

- Frozen v91 inputs and explicit experimental v92 separation; see docs/REPRODUCIBILITY.md.

### 操作步骤

- Follow docs/PLAN.md and retain identity, fresh power, floor and full SHA admission.

### 开发经验

- Board resources, firmware inspection and partial Wi-Fi/Bluetooth transport components exist.

### 完成条件

- Wi-Fi authentication/IP/traffic; Bluetooth pairing/audio/HID and persistent credentials.

### 当前范围

- Wi-Fi connectivity and Bluetooth pairing/continuous operation are not accepted.

### 下一步

- Follow sheng-proven driver interfaces with TB322FC-specific ArmadaOS register evidence.

### 证据

- `host`: [Board resources, firmware inspection and partial Wi-Fi/Bluetooth transport components exist. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/c4ebf12968e342bf7941781bc3ed0467060eb364/docs/CURRENT-STATUS.md)
  Command: <code>Read frozen source/hardware manifests; no new device operation during maintenance</code>. Revision: `c7fae2baaaad4be7406de3691a4e79cc5cc48664`.

## 音频 {#audio}

`planned`

### 硬件与依赖

- Original ADSP/DTB, WCD9395 and AW88461 board resources.

### 配置

- Frozen v91 inputs and explicit experimental v92 separation; see docs/REPRODUCIBILITY.md.

### 操作步骤

- Follow docs/PLAN.md and retain identity, fresh power, floor and full SHA admission.

### 开发经验

- Reference work retained; no new speaker enablement.

### 完成条件

- Protected playback, microphone capture, system routing and sustained audio.

### 当前范围

- Speaker gain and electrical protection are not qualified.

### 下一步

- Discuss attenuation and protection before enabling speaker output.

### 证据

- `host`: [Reference work retained; no new speaker enablement. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/c4ebf12968e342bf7941781bc3ed0467060eb364/docs/CURRENT-STATUS.md)
  Command: <code>Read frozen source/hardware manifests; no new device operation during maintenance</code>. Revision: `c7fae2baaaad4be7406de3691a4e79cc5cc48664`.

## 电源 {#power}

`implemented`

### 硬件与依赖

- PM8550-class PMIC, RPMh resources and device power domains.
- Volume and power key behavior.

### 配置

- Frozen v91 inputs and explicit experimental v92 separation; see docs/REPRODUCIBILITY.md.

### 操作步骤

- Follow docs/PLAN.md and retain identity, fresh power, floor and full SHA admission.

### 开发经验

- Battery/backlight, OEM ADSP/GLINK, UCSI notifications and controlled PD procedures have hardware evidence.
- v156 enables the stock-observed5000us UFS auto-Hibern8 timer with owned clock-request bits and error handling.32 hardware enter/exit cycles and authenticated reads passed; controller restoration, sync/reset and stock Android recovery passed.

### 完成条件

- Declared power controls match readings.
- Sleep/resume or shutdown transitions restore dependent peripherals.

### 当前范围

- Shared 500mA, complete fast charging, bypass, charge windows and all dual-port failure cases remain open.
- UFS low-power entry is not whole-system sleep or measured tablet energy savings. Read-after-idle latency was0.8-1.0ms; high-SOC current and log loss do not establish net charging.

### 下一步

- Use decision-changing functional tests; do not repeat the rejected GLINK write path.

### 证据

- `host`: [Battery/backlight, OEM ADSP/GLINK, UCSI notifications and controlled PD procedures have hardware evidence. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/c4ebf12968e342bf7941781bc3ed0467060eb364/docs/CURRENT-STATUS.md)
  Command: <code>Read frozen source/hardware manifests; no new device operation during maintenance</code>. Revision: `c7fae2baaaad4be7406de3691a4e79cc5cc48664`.
- `device`: [AHIT5f4/CFG183c/IE61 admitted;32 wake reads verified; stop0 phaseRestored and original Android UFS/charging settings restored. Drop1172; critical records complete, no net-energy claim.](https://github.com/zenkernelsam/UniXNU_elden/blob/c4ebf12968e342bf7941781bc3ed0467060eb364/profiles/ufs-idle-trial/hardware.json)
  Command: <code>Run v156 auto-Hibern8 idle/read proof, verify32 hardware enter/exit counters and block hashes, then controller restore, sync/reset and full stock recovery.</code>. Revision: `9c9a739148b175c4df362d91467ae39a7fadb9c2`.

## 镜像组装 {#packaging}

`device-verified`

### 硬件与依赖

- iPad7,1 iPadOS 17.7.11 build 21H461 restore inputs.
- Target kernelcache, XNU 10063.141.1, DriverKit and TrustCache ABI inputs.
- Android v3 RAM-boot image, a 4 MiB phase 1 embedded FAT payload and a measured 56 MiB phase 2 candidate.

### 配置

- Frozen v91 inputs and explicit experimental v92 separation; see docs/REPRODUCIBILITY.md.

### 操作步骤

- Follow docs/PLAN.md and retain identity, fresh power, floor and full SHA admission.

### 开发经验

- v91 boot image ran; rollback floor and full-image identity are recorded.

### 完成条件

- All format 2 build steps run from the resolved output directory.
- The payload contains the kernel, ADT and declared optional inputs.
- The boot image matches the ABL header and size limits.

### 当前范围

- A clean source-to-final-boot rebuild is not yet validated.

### 下一步

- Close source/external-input dependency graph before presenting a one-command build.

### 证据

- `device`: [v91 boot image ran; rollback floor and full-image identity are recorded. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/c4ebf12968e342bf7941781bc3ed0467060eb364/docs/CURRENT-STATUS.md)
  Command: <code>Read frozen source/hardware manifests; no new device operation during maintenance</code>. Revision: `c7fae2baaaad4be7406de3691a4e79cc5cc48664`.

## 诊断 {#diagnostics}

`device-verified`

### 硬件与依赖

- RAM-only owner-operated boot procedure.
- Build and artifact SHA-256 values.
- UEFI screen output and recovery path.

### 配置

- Frozen v91 inputs and explicit experimental v92 separation; see docs/REPRODUCIBILITY.md.

### 操作步骤

- Follow docs/PLAN.md and retain identity, fresh power, floor and full SHA admission.

### 开发经验

- USB kernel logs, frame readback, session-bound RPC and directed fastboot recovery work.
- v150 moves the existing Gunyah arming before kernel UFS work and adopts it at unchanged SMP readiness. Normal startup and an interrupt-masked pre-UFS stall both returned to fastboot and restored Android; firmware/earlier-kernel coverage is not claimed.

### 完成条件

- Every claimed checkpoint has a reproducible command, image hash and visible result.
- Failures reach a diagnosable screen or log instead of a silent hang.

### 当前范围

- v91 whole capture dropped 24 bytes; counted raster records and Settings frame CRC were retained.

### 下一步

- Preserve the recovery path and measure rather than infer CPU/UFS stalls.

### 证据

- `device`: [USB kernel logs, frame readback, session-bound RPC and directed fastboot recovery work. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/c4ebf12968e342bf7941781bc3ed0467060eb364/docs/CURRENT-STATUS.md)
  Command: <code>Read frozen source/hardware manifests; no new device operation during maintenance</code>. Revision: `c7fae2baaaad4be7406de3691a4e79cc5cc48664`.
- `device`: [EARLY\_ARM/SMP\_ADOPT and eight-core admission passed. Masked-stall marker to responsive fastboot46.583s includes bootloader/USB time; no software fallback or PC reset observed. Normal drop59; stall drop0 with final transport-timeout boundary.](https://github.com/zenkernelsam/UniXNU_elden/blob/c4ebf12968e342bf7941781bc3ed0467060eb364/profiles/early-storage-guard/hardware.json)
  Command: <code>Run v150 normal mode and the same-kernel --early-stall candidate with passive PC capture; verify the exact stall marker, response before the120s fallback and full stock Android restoration.</code>. Revision: `e7bfb105e0af80eafe6c372da2d99857a89e372d`.

## network-initialization {#network-initialization}

`device-verified`

组件: `XnuPrelink`, `IONetworkingFamily`.

### 硬件与依赖

- Original iPadOS17 21H461 kernelcache and its IONetworkingFamily3.4; the frozen v107/v108 profiles.

### 配置

- v108 adds the original network family to prelink roots and retains its IOResources/IOBSD personality; it does not create a network interface.

### 操作步骤

- Follow profiles/v108-network-family/README.md, audit the original family extent, then inspect the six IOKit snapshots and full stock-restoration record.

### 开发经验

- v107: six complete busy0/AES-only snapshots. v108: exact original21H461 family added; six snapshots show real IONetworkStack and AES, busy0.

### 完成条件

- The real IONetworkStack registers without a dummy MAC/interface; Wi-Fi scan, association and traffic are separate unfinished requirements.

### 当前范围

- No WLAN/Ethernet interface; About latency not measured in v108. Capture dropped36 bytes.

### 下一步

- Measure userland initialization when useful and continue qualified RAM expansion; no fake network readiness.

### 证据

- `device`: [Signed candidate, sync return and complete stock restoration verified.](https://github.com/zenkernelsam/UniXNU_elden/blob/c4ebf12968e342bf7941781bc3ed0467060eb364/profiles/v108-network-family/hardware-result.json)
  Command: <code>Run the recorded v108 candidate, inspect six busy/provider snapshots, request session-bound reset-after-sync and verify the full stock boot hash and Android recovery.</code>. Revision: `1bb142e0375ed47a38b7b7166cc4cc442d3e792a`.

## memory-window8 {#memory-window8}

`device-verified`

组件: `DarwinBoot`, `ArmDTPlatform`.

### 硬件与依赖

- TB322FC EFI memory map, the v108 parent and three coherent bootstrap objects recorded in profiles/v109-memory8.

### 配置

- The separate v109 GUI profile manages8GiB with24 page-table-pool pages; current Bluetooth/PD profiles still use6GiB.

### 操作步骤

- Follow profiles/v109-memory8/README.md and inspect its window, entry, original-Apple-region and captured GUI/stock-restoration checks.

### 开发经验

- Real EFI allocation and XNU8GiB window; three coherent bootstrap objects,24page pool and31 original Apple text extents audited. Software Settings/General frame CRCb92cfd0a validated.

### 完成条件

- The requested EFI allocation and kernel window agree, root/GUI and recovery work; this does not qualify16GiB or every page under stress.

### 当前范围

- Not16GiB, full-page stress, About-latency or physical-finger acceptance. Home transition artifacts remain. Final capture drop10; damaged frame12 rejected.

### 下一步

- Keep8GiB baseline and evaluate KVA/EFI reservations before larger windows or outside-page adoption.

### 证据

- `device`: [Three trials completed sync return and full stock restoration; Android/root/green restored.](https://github.com/zenkernelsam/UniXNU_elden/blob/c4ebf12968e342bf7941781bc3ed0467060eb364/profiles/v109-memory8/ui-hardware-result.json)
  Command: <code>Run the v109 GUI window trial, verify captured Settings/General frames and the recorded full-SHA stock Android restoration.</code>. Revision: `63c7f9994776f9e1d9b990fdf5c59c06c8356a66`.

## spmi-adc-bt-serialization {#spmi-adc-bt-serialization}

`host-verified`

组件: `EldenPmicGlink`, `EldenBluetooth`.

### 硬件与依赖

- Frozen v110 ADC and Bluetooth readers, the same-board Linux transaction-serialization contract and the EldenSpmi transaction gate.

### 配置

- One shared provider serializes complete ADC and Bluetooth SPMI transactions; this area records the historical component stage.

### 操作步骤

- Run tools/test\_spmi\_transaction\_gate.py and build the ADC/WCN consumer components as documented in drivers/EldenSpmi; inspect host-result.json.

### 开发经验

- Both v110 runs stop before UART with completed SPMI status9 and ADC errors. Same-board Linux serializes entire bus transactions; Elden lacked a common gate. Actual-reader host collision/error tests and four ARM64 gate components pass.

### 完成条件

- The real readers use one gate, collisions and errors release it correctly; full-kernel and device qualification are recorded separately by v111.

### 当前范围

- No full gate kernel or hardware test. FIFO hardware not reached. Status9 causality is not proved. Charging/net-current/cycles and Bluetooth remain incomplete.

### 下一步

- Integrate one gate provider plus actual ADC and BT consumers, audit and then test thermal/WCN together.

### 证据

- `host`: [Injected concurrency/error model; not hardware proof.](https://github.com/zenkernelsam/UniXNU_elden/blob/c4ebf12968e342bf7941781bc3ed0467060eb364/drivers/EldenSpmi/host-result.json)
  Command: <code>Run the actual-reader transaction-gate fault/concurrency host tests recorded in drivers/EldenSpmi/host-result.json.</code>. Revision: `b86a5f368ca97ebdd2c2a31f58437b1cd61ed917`.

## spmi-hci-v114 {#spmi-hci-v114}

`implemented`

组件: `EldenPmicGlink`, `EldenBluetooth`.

### 硬件与依赖

- Qualified v111 shared SPMI consumers, v113 UART/peripheral evidence and the12-byte HCI identity response format in v114.

### 配置

- v114 keeps the v113 board/firmware path and adjusts the validated response-length gate; v112 remains withdrawn.

### 操作步骤

- Follow the v111, v113 and v114 profile READMEs; inspect the frozen hardware records and preserve errors/stock recovery.

### 开发经验

- v111 shared-bus consumers verified,54 ADC readings/thermal/WCN pass. v113 peripheral complete and real EDL response captured. v114 length12 validation fixes proven old-source rejection.

### 完成条件

- The expected response is reached and accepted on hardware with clean recovery; a source fix alone is insufficient for native HCI readiness or pairing.

### 当前范围

- v112 withdrawn for GIC address typo. Initial IBS wake remains variable. v114 did not reach its new check on hardware. No native HCI-ready/pairing or charge-policy completion.

### 下一步

- Inspect cold-start UART synchronization and same-board Linux port-reopen sequence before further device runs.

### 证据

- `device`: [Typed sync/reset and stock restore; stage2 timeout retained.](https://github.com/zenkernelsam/UniXNU_elden/blob/c4ebf12968e342bf7941781bc3ed0467060eb364/profiles/v114-hci-length/hardware-result.json)
  Command: <code>Run the recorded v114 candidate and preserve its failed preparation-stage trace plus the verified stock restoration; the new length gate was not reached.</code>. Revision: `79ecf38be39bcade9bb6f90ec95af60a9f57c36a`.

</div>
