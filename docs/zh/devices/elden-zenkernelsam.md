# Lenovo Legion Y700 Gen 4 \(zenkernelsam\)

[zenkernelsam/UniXNU_elden](https://github.com/zenkernelsam/UniXNU_elden)

<div v-pre>

v91 reached populated Settings via software input. Physical input/performance/basic peripherals remain incomplete. Source migration and clean reproduction are in progress; device restored stock.

源记录: [porting.toml](https://github.com/zenkernelsam/UniXNU_elden/blob/901349f0d3d4df504bd386c760be2428b4506636/porting.toml), `901349f0d3d4df504bd386c760be2428b4506636`.

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

- `host`: [Frozen v91 source profile imported and verified. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/901349f0d3d4df504bd386c760be2428b4506636/docs/REPRODUCIBILITY.md)
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

- `device`: [Existing UniXNU menu, payload handoff and recovery firmware boot the v91 kernel. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/901349f0d3d4df504bd386c760be2428b4506636/docs/CURRENT-STATUS.md)
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

- `host`: [CPU8 source configuration, identity/IRQ changes and guarded startup are captured in v91. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/901349f0d3d4df504bd386c760be2428b4506636/docs/CURRENT-STATUS.md)
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

- `host`: [v91 retains the validated high-address RAM configuration. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/901349f0d3d4df504bd386c760be2428b4506636/docs/CURRENT-STATUS.md)
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

### 配置

- Frozen v91 inputs and explicit experimental v92 separation; see docs/REPRODUCIBILITY.md.

### 操作步骤

- Follow docs/PLAN.md and retain identity, fresh power, floor and full SHA admission.

### 开发经验

- UFS-backed iPadOS root, RAM Data, launchd and Settings have run.

### 完成条件

- Controller and PHY initialize.
- Read-only capacity, GPT and known-block checks match the device.
- The configured OS volume mounts and launchd starts.

### 当前范围

- Persistent Data and UFS performance are not fully qualified.

### 下一步

- Compare measured I/O with the pinned sheng success path; qualify persistence separately.

### 证据

- `host`: [UFS-backed iPadOS root, RAM Data, launchd and Settings have run. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/901349f0d3d4df504bd386c760be2428b4506636/docs/CURRENT-STATUS.md)
  Command: <code>Read frozen source/hardware manifests; no new device operation during maintenance</code>. Revision: `c7fae2baaaad4be7406de3691a4e79cc5cc48664`.

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

- `host`: [v91 renders a populated Settings page with the owned CPU graphic-variant helper. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/901349f0d3d4df504bd386c760be2428b4506636/docs/CURRENT-STATUS.md)
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

- `host`: [One software swipe and one short Settings tap reached the real Settings UI in v91. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/901349f0d3d4df504bd386c760be2428b4506636/docs/CURRENT-STATUS.md)
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

- `host`: [Reference sources and inactive experimental components are preserved. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/901349f0d3d4df504bd386c760be2428b4506636/docs/CURRENT-STATUS.md)
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

- `host`: [Board resources, firmware inspection and partial Wi-Fi/Bluetooth transport components exist. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/901349f0d3d4df504bd386c760be2428b4506636/docs/CURRENT-STATUS.md)
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

- `host`: [Reference work retained; no new speaker enablement. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/901349f0d3d4df504bd386c760be2428b4506636/docs/CURRENT-STATUS.md)
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

### 完成条件

- Declared power controls match readings.
- Sleep/resume or shutdown transitions restore dependent peripherals.

### 当前范围

- Shared 500mA, complete fast charging, bypass, charge windows and all dual-port failure cases remain open.

### 下一步

- Use decision-changing functional tests; do not repeat the rejected GLINK write path.

### 证据

- `host`: [Battery/backlight, OEM ADSP/GLINK, UCSI notifications and controlled PD procedures have hardware evidence. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/901349f0d3d4df504bd386c760be2428b4506636/docs/CURRENT-STATUS.md)
  Command: <code>Read frozen source/hardware manifests; no new device operation during maintenance</code>. Revision: `c7fae2baaaad4be7406de3691a4e79cc5cc48664`.

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

- `device`: [v91 boot image ran; rollback floor and full-image identity are recorded. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/901349f0d3d4df504bd386c760be2428b4506636/docs/CURRENT-STATUS.md)
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

### 完成条件

- Every claimed checkpoint has a reproducible command, image hash and visible result.
- Failures reach a diagnosable screen or log instead of a silent hang.

### 当前范围

- v91 whole capture dropped 24 bytes; counted raster records and Settings frame CRC were retained.

### 下一步

- Preserve the recovery path and measure rather than infer CPU/UFS stalls.

### 证据

- `device`: [USB kernel logs, frame readback, session-bound RPC and directed fastboot recovery work. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/901349f0d3d4df504bd386c760be2428b4506636/docs/CURRENT-STATUS.md)
  Command: <code>Read frozen source/hardware manifests; no new device operation during maintenance</code>. Revision: `c7fae2baaaad4be7406de3691a4e79cc5cc48664`.

</div>
