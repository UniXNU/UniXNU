# Lenovo Legion Y700 Gen 4 \(zenkernelsam\)

[zenkernelsam/UniXNU_elden](https://github.com/zenkernelsam/UniXNU_elden)

<div v-pre>

v91 reached populated Settings via software input. Physical input/performance/basic peripherals remain incomplete. Source migration and clean reproduction are in progress; device restored stock.

Source record: [porting.toml](https://github.com/zenkernelsam/UniXNU_elden/blob/901349f0d3d4df504bd386c760be2428b4506636/porting.toml), `901349f0d3d4df504bd386c760be2428b4506636`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `host-verified` |
| [Firmware and boot](#firmware) | `device-verified` |
| [CPU and interrupts](#cpu) | `implemented` |
| [Memory and DMA](#memory) | `implemented` |
| [Storage and root](#storage) | `implemented` |
| [Display](#display) | `implemented` |
| [Input](#input) | `implemented` |
| [GPU](#gpu) | `planned` |
| [Network](#network) | `implemented` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `implemented` |
| [Image assembly](#packaging) | `device-verified` |
| [Diagnostics](#diagnostics) | `device-verified` |

## Configuration {#configuration}

`host-verified`

Components: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`, `DarwinBoot`.

### Hardware and dependencies

- Use the ARM64 and iPadOS 17.7.11 profiles supplied by UniXNU.
- Select the shared platform, CPU and DarwinBoot components.
- Provide an SM8750 profile until an official shared SoC repository exists.

### Configuration

- Frozen v91 inputs and explicit experimental v92 separation; see docs/REPRODUCIBILITY.md.

### Procedure

- Follow docs/PLAN.md and retain identity, fresh power, floor and full SHA admission.

### Development findings

- Frozen v91 source profile imported and verified.

### Completion criteria

- board.toml resolves four ordered configuration layers.
- All selected components come from the UniXNU catalog and include their dependencies.
- No array field depends accidentally on inheritance.
- The SoC source is a reviewed remote commit and unixnu.lock records it.

### Current limits

- Default board/lock remains the historical early profile; no clean final boot reproduction yet.

### Next action

- Finish clean full-kernel and packaging dependency closure.

### Evidence

- `host`: [Frozen v91 source profile imported and verified. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/901349f0d3d4df504bd386c760be2428b4506636/docs/REPRODUCIBILITY.md)
  Command: <code>Read frozen source/hardware manifests; no new device operation during maintenance</code>. Revision: `c7fae2baaaad4be7406de3691a4e79cc5cc48664`.

## Firmware and boot {#firmware}

`device-verified`

Components: `DarwinBoot`.

### Hardware and dependencies

- mu\_wide\_platforms lenovo-y700g4 UEFI source and patched PMIC binaries.
- UniXNU, UniXNUDxe, DarwinBoot and EldenRamDiskDxe firmware modules.
- A 4 MiB FAT16 payload containing package/unixnu.toml.

### Configuration

- Frozen v91 inputs and explicit experimental v92 separation; see docs/REPRODUCIBILITY.md.

### Procedure

- Follow docs/PLAN.md and retain identity, fresh power, floor and full SHA admission.

### Development findings

- Existing UniXNU menu, payload handoff and recovery firmware boot the v91 kernel.

### Completion criteria

- Firmware contains UniXNU, UniXNUDxe, DarwinBoot and the RAM payload driver.
- The payload config is readable and the menu accepts volume-key input.
- Two RAM boots produce the same visible checkpoint and do not modify persistent partitions.

### Current limits

- Not a claim that every firmware configuration or KShimC route is qualified.

### Next action

- Retain frozen firmware inputs and finish portable build mapping.

### Evidence

- `device`: [Existing UniXNU menu, payload handoff and recovery firmware boot the v91 kernel. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/901349f0d3d4df504bd386c760be2428b4506636/docs/CURRENT-STATUS.md)
  Command: <code>Read frozen source/hardware manifests; no new device operation during maintenance</code>. Revision: `c7fae2baaaad4be7406de3691a4e79cc5cc48664`.

## CPU and interrupts {#cpu}

`implemented`

Components: `ArmCpu`.

### Hardware and dependencies

- SM8750 MPIDRs 0x0, 0x100, 0x200, 0x300, 0x400, 0x500, 0x10000 and 0x10100.
- GICv3 distributor 0x16000000, redistributor base 0x16080000 and stride 0x40000.
- 19.2 MHz architectural timer and PSCI SMC conduit.

### Configuration

- Frozen v91 inputs and explicit experimental v92 separation; see docs/REPRODUCIBILITY.md.

### Procedure

- Follow docs/PLAN.md and retain identity, fresh power, floor and full SHA admission.

### Development findings

- CPU8 source configuration, identity/IRQ changes and guarded startup are captured in v91.

### Completion criteria

- The boot CPU reaches the ArmCpu checkpoint.
- GIC distributor and its own redistributor frame map successfully.
- Timer handling works before secondary cores or IPI transport are qualified.

### Current limits

- Configured CPUs do not prove sustained online load or explain UI stalls.

### Next action

- Measure online CPUs, scheduler/IRQ progress and actual latency with the UI workload.

### Evidence

- `host`: [CPU8 source configuration, identity/IRQ changes and guarded startup are captured in v91. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/901349f0d3d4df504bd386c760be2428b4506636/docs/CURRENT-STATUS.md)
  Command: <code>Read frozen source/hardware manifests; no new device operation during maintenance</code>. Revision: `c7fae2baaaad4be7406de3691a4e79cc5cc48664`.

## Memory and DMA {#memory}

`implemented`

Components: `ArmDTPlatform`.

### Hardware and dependencies

- The owner-captured live elden FDT, including the 12 GiB RAM map, initrd and reserved-memory nodes.
- The pinned Linux 16 GiB variant and the elden UEFI static memory map.
- A conservative 256 MiB XNU handoff window in UEFI DXE conventional memory.

### Configuration

- Frozen v91 inputs and explicit experimental v92 separation; see docs/REPRODUCIBILITY.md.

### Procedure

- Follow docs/PLAN.md and retain identity, fresh power, floor and full SHA admission.

### Development findings

- v91 retains the validated high-address RAM configuration.

### Completion criteria

- The ADT contains exactly one continuous memory range.
- The range is covered by live firmware RAM and avoids recorded reservations, initrd, GOP and UEFI FD.
- DarwinBoot and the UEFI exit map confirm that same range is conventional memory before XNU entry.

### Current limits

- Full 16GB adoption and memory stress are incomplete.

### Next action

- Keep frozen memory inputs during UI work; expand after map qualification.

### Evidence

- `host`: [v91 retains the validated high-address RAM configuration. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/901349f0d3d4df504bd386c760be2428b4506636/docs/CURRENT-STATUS.md)
  Command: <code>Read frozen source/hardware manifests; no new device operation during maintenance</code>. Revision: `c7fae2baaaad4be7406de3691a4e79cc5cc48664`.

## Storage and root {#storage}

`implemented`

Components: `ShengUfs`.

### Hardware and dependencies

- SM8750 UFS host at 0x1d84000 \(+0x3000\) and QMP PHY at 0x1d80000 \(+0x2000\), both described by the same-device Linux tree sm8750-lenovo-elden.dts and sm8750.dtsi pinned at bf96c3d4048973298ede78487177c6f1b4f6bc0f.
- Controller resources: GIC\_SPI 265 level-high, 8 GCC/RPMh clocks, GCC\_UFS\_PHY\_BCR, GCC\_UFS\_PHY\_GDSC, apps\_smmu stream 0x60, lanes-per-direction 2, ICE crypto@1d88000.
- PHY resources: RPMH\_CXO\_CLK, GCC\_UFS\_PHY\_PHY\_AUX\_CLK, TCSR\_UFS\_CLKREF\_EN, GCC\_UFS\_MEM\_PHY\_GDSC.
- Board supplies and reset: PHY vreg\_l1j\_0p91 and vreg\_l3g\_1p2, host vreg\_l17b\_2p5 \(1.3 A\) and vreg\_l1d\_1p2 \(1.2 A\), reset GPIO tlmm 215 active-low.
- 4 KiB logical-sector partition geometry and a root-volume UUID, both owner-supplied and read-only.

### Configuration

- Frozen v91 inputs and explicit experimental v92 separation; see docs/REPRODUCIBILITY.md.

### Procedure

- Follow docs/PLAN.md and retain identity, fresh power, floor and full SHA admission.

### Development findings

- UFS-backed iPadOS root, RAM Data, launchd and Settings have run.

### Completion criteria

- Controller and PHY initialize.
- Read-only capacity, GPT and known-block checks match the device.
- The configured OS volume mounts and launchd starts.

### Current limits

- Persistent Data and UFS performance are not fully qualified.

### Next action

- Compare measured I/O with the pinned sheng success path; qualify persistence separately.

### Evidence

- `host`: [UFS-backed iPadOS root, RAM Data, launchd and Settings have run. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/901349f0d3d4df504bd386c760be2428b4506636/docs/CURRENT-STATUS.md)
  Command: <code>Read frozen source/hardware manifests; no new device operation during maintenance</code>. Revision: `c7fae2baaaad4be7406de3691a4e79cc5cc48664`.

## Display {#display}

`implemented`

Components: `GopFramebuffer`, `AppleKeyStoreState`.

### Hardware and dependencies

- 1904x3040 bonded dual-DSI panel with DSC.
- UEFI GOP framebuffer and splash reservation.
- SM8750 DPU/DSI/PHY and backlight sequencing.

### Configuration

- Frozen v91 inputs and explicit experimental v92 separation; see docs/REPRODUCIBILITY.md.

### Procedure

- Follow docs/PLAN.md and retain identity, fresh power, floor and full SHA admission.

### Development findings

- v91 renders a populated Settings page with the owned CPU graphic-variant helper.

### Completion criteria

- XNU paints a known pattern through a declared framebuffer handoff.
- Userland presentation and backlight transitions work.

### Current limits

- Display fluidity and v92 framebuffer mapping remain unqualified.

### Next action

- Qualify v92 offline, then use one meaningful display/input function test.

### Evidence

- `host`: [v91 renders a populated Settings page with the owned CPU graphic-variant helper. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/901349f0d3d4df504bd386c760be2428b4506636/docs/CURRENT-STATUS.md)
  Command: <code>Read frozen source/hardware manifests; no new device operation during maintenance</code>. Revision: `c7fae2baaaad4be7406de3691a4e79cc5cc48664`.

## Input {#input}

`implemented`

Components: `ShengHidInput`.

### Hardware and dependencies

- Novatek SPI touch on SPI4 and GPIO 162 interrupt.
- Volume and power keys used by the UEFI menu.

### Configuration

- Frozen v91 inputs and explicit experimental v92 separation; see docs/REPRODUCIBILITY.md.

### Procedure

- Follow docs/PLAN.md and retain identity, fresh power, floor and full SHA admission.

### Development findings

- One software swipe and one short Settings tap reached the real Settings UI in v91.

### Completion criteria

- Touch coordinates map to the display.
- Contact IDs, releases and multi-touch remain stable.
- Buttons produce expected HID events in XNU.

### Current limits

- Physical finger accuracy, ghost-touch rejection and consistent gestures remain incomplete.

### Next action

- Correlate a real touch with raw contact, HID event and UI response in one bounded session.

### Evidence

- `host`: [One software swipe and one short Settings tap reached the real Settings UI in v91. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/901349f0d3d4df504bd386c760be2428b4506636/docs/CURRENT-STATUS.md)
  Command: <code>Read frozen source/hardware manifests; no new device operation during maintenance</code>. Revision: `c7fae2baaaad4be7406de3691a4e79cc5cc48664`.

## GPU {#gpu}

`planned`

### Hardware and dependencies

- Adreno 830 / gen80000.
- GPU firmware, power votes, SMMU and display integration.

### Configuration

- Frozen v91 inputs and explicit experimental v92 separation; see docs/REPRODUCIBILITY.md.

### Procedure

- Follow docs/PLAN.md and retain identity, fresh power, floor and full SHA admission.

### Development findings

- Reference sources and inactive experimental components are preserved.

### Completion criteria

- GPU submissions, fences and mapping work.
- A known image renders and Metal presentation is visible.

### Current limits

- No GPU daily-use qualification.

### Next action

- GPU last, after basic peripherals and CPU display are usable.

### Evidence

- `host`: [Reference sources and inactive experimental components are preserved. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/901349f0d3d4df504bd386c760be2428b4506636/docs/CURRENT-STATUS.md)
  Command: <code>Read frozen source/hardware manifests; no new device operation during maintenance</code>. Revision: `c7fae2baaaad4be7406de3691a4e79cc5cc48664`.

## Network {#network}

`implemented`

### Hardware and dependencies

- WCN7861 Wi-Fi/Bluetooth shared power, transport and firmware.

### Configuration

- Frozen v91 inputs and explicit experimental v92 separation; see docs/REPRODUCIBILITY.md.

### Procedure

- Follow docs/PLAN.md and retain identity, fresh power, floor and full SHA admission.

### Development findings

- Board resources, firmware inspection and partial Wi-Fi/Bluetooth transport components exist.

### Completion criteria

- Wi-Fi authentication/IP/traffic; Bluetooth pairing/audio/HID and persistent credentials.

### Current limits

- Wi-Fi connectivity and Bluetooth pairing/continuous operation are not accepted.

### Next action

- Follow sheng-proven driver interfaces with TB322FC-specific ArmadaOS register evidence.

### Evidence

- `host`: [Board resources, firmware inspection and partial Wi-Fi/Bluetooth transport components exist. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/901349f0d3d4df504bd386c760be2428b4506636/docs/CURRENT-STATUS.md)
  Command: <code>Read frozen source/hardware manifests; no new device operation during maintenance</code>. Revision: `c7fae2baaaad4be7406de3691a4e79cc5cc48664`.

## Audio {#audio}

`planned`

### Hardware and dependencies

- Original ADSP/DTB, WCD9395 and AW88461 board resources.

### Configuration

- Frozen v91 inputs and explicit experimental v92 separation; see docs/REPRODUCIBILITY.md.

### Procedure

- Follow docs/PLAN.md and retain identity, fresh power, floor and full SHA admission.

### Development findings

- Reference work retained; no new speaker enablement.

### Completion criteria

- Protected playback, microphone capture, system routing and sustained audio.

### Current limits

- Speaker gain and electrical protection are not qualified.

### Next action

- Discuss attenuation and protection before enabling speaker output.

### Evidence

- `host`: [Reference work retained; no new speaker enablement. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/901349f0d3d4df504bd386c760be2428b4506636/docs/CURRENT-STATUS.md)
  Command: <code>Read frozen source/hardware manifests; no new device operation during maintenance</code>. Revision: `c7fae2baaaad4be7406de3691a4e79cc5cc48664`.

## Power {#power}

`implemented`

### Hardware and dependencies

- PM8550-class PMIC, RPMh resources and device power domains.
- Volume and power key behavior.

### Configuration

- Frozen v91 inputs and explicit experimental v92 separation; see docs/REPRODUCIBILITY.md.

### Procedure

- Follow docs/PLAN.md and retain identity, fresh power, floor and full SHA admission.

### Development findings

- Battery/backlight, OEM ADSP/GLINK, UCSI notifications and controlled PD procedures have hardware evidence.

### Completion criteria

- Declared power controls match readings.
- Sleep/resume or shutdown transitions restore dependent peripherals.

### Current limits

- Shared 500mA, complete fast charging, bypass, charge windows and all dual-port failure cases remain open.

### Next action

- Use decision-changing functional tests; do not repeat the rejected GLINK write path.

### Evidence

- `host`: [Battery/backlight, OEM ADSP/GLINK, UCSI notifications and controlled PD procedures have hardware evidence. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/901349f0d3d4df504bd386c760be2428b4506636/docs/CURRENT-STATUS.md)
  Command: <code>Read frozen source/hardware manifests; no new device operation during maintenance</code>. Revision: `c7fae2baaaad4be7406de3691a4e79cc5cc48664`.

## Image assembly {#packaging}

`device-verified`

### Hardware and dependencies

- iPad7,1 iPadOS 17.7.11 build 21H461 restore inputs.
- Target kernelcache, XNU 10063.141.1, DriverKit and TrustCache ABI inputs.
- Android v3 RAM-boot image, a 4 MiB phase 1 embedded FAT payload and a measured 56 MiB phase 2 candidate.

### Configuration

- Frozen v91 inputs and explicit experimental v92 separation; see docs/REPRODUCIBILITY.md.

### Procedure

- Follow docs/PLAN.md and retain identity, fresh power, floor and full SHA admission.

### Development findings

- v91 boot image ran; rollback floor and full-image identity are recorded.

### Completion criteria

- All format 2 build steps run from the resolved output directory.
- The payload contains the kernel, ADT and declared optional inputs.
- The boot image matches the ABL header and size limits.

### Current limits

- A clean source-to-final-boot rebuild is not yet validated.

### Next action

- Close source/external-input dependency graph before presenting a one-command build.

### Evidence

- `device`: [v91 boot image ran; rollback floor and full-image identity are recorded. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/901349f0d3d4df504bd386c760be2428b4506636/docs/CURRENT-STATUS.md)
  Command: <code>Read frozen source/hardware manifests; no new device operation during maintenance</code>. Revision: `c7fae2baaaad4be7406de3691a4e79cc5cc48664`.

## Diagnostics {#diagnostics}

`device-verified`

### Hardware and dependencies

- RAM-only owner-operated boot procedure.
- Build and artifact SHA-256 values.
- UEFI screen output and recovery path.

### Configuration

- Frozen v91 inputs and explicit experimental v92 separation; see docs/REPRODUCIBILITY.md.

### Procedure

- Follow docs/PLAN.md and retain identity, fresh power, floor and full SHA admission.

### Development findings

- USB kernel logs, frame readback, session-bound RPC and directed fastboot recovery work.

### Completion criteria

- Every claimed checkpoint has a reproducible command, image hash and visible result.
- Failures reach a diagnosable screen or log instead of a silent hang.

### Current limits

- v91 whole capture dropped 24 bytes; counted raster records and Settings frame CRC were retained.

### Next action

- Preserve the recovery path and measure rather than infer CPU/UFS stalls.

### Evidence

- `device`: [USB kernel logs, frame readback, session-bound RPC and directed fastboot recovery work. Imported source is a local snapshot based on this revision; see profiles/v91/manifest.json for exact hashes.](https://github.com/zenkernelsam/UniXNU_elden/blob/901349f0d3d4df504bd386c760be2428b4506636/docs/CURRENT-STATUS.md)
  Command: <code>Read frozen source/hardware manifests; no new device operation during maintenance</code>. Revision: `c7fae2baaaad4be7406de3691a4e79cc5cc48664`.

</div>
