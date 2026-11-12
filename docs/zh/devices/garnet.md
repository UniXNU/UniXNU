# Preliminary garnet bring-up; not bootable

[Scarpy19/UniXNU-garnet](https://github.com/Scarpy19/UniXNU-garnet)

<div v-pre>

Preliminary research scaffold; no verified build or device boot.

源记录: [porting.toml](https://github.com/Scarpy19/UniXNU-garnet/blob/86e64537fa71951f420b0b3ef442455b936e6c71/porting.toml), `86e64537fa71951f420b0b3ef442455b936e6c71`.

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

组件: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`, `DarwinBoot`.

### 硬件与依赖

- Pinned UniXNU and preliminary SM7435 sources; target OS profile.

### 配置

- Example guard remains enabled; profile 27 is unverified.

### 操作步骤

- Resolve sources and inspect configuration after required inputs are established.

### 开发经验

- The SoC feed is pinned; ARM64e compatibility is not established.
- WSL defconfig and status resolve garnet and its SM7435 feed. Empty kernel.archives selects automatic component recipes, while auxiliary archives and several components' research-profile ABI support need review.
- The guarded board selects a provisional OS patch series without the incompatible boot-progress layer; equivalent diagnostics and profile compatibility are unverified.
- The guarded board file describes candidate UEFI package roots and submodules, not a verified build configuration.
- The user authorized system packages and administrator access for compilation; the WSL host check reports llvm-config missing. The official installer was started as WSL root; completion is pending.

### 完成条件

- Configuration and all selected component dependencies resolve with reviewed inputs.

### 当前范围

- The board is deliberately incomplete and is not ready to build.

### 下一步

- Verify PAC and complete the board resource inventory.

### 证据

按下一步操作收集证据。

## 固件与启动 {#firmware}

`planned`

### 硬件与依赖

- Garnet UEFI source, firmware files, device DTB, and redistribution terms.

### 配置

- Guarded board configuration lists candidate garnet DSC, FD, package roots and source-declared submodules; it does not apply the UEFI patch or supply the required vendor files.

### 操作步骤

- Audit the exact UEFI revision and integrate UniXNU and DarwinBoot modules.

### 开发经验

- The audited garnet firmware configuration does not establish UniXNU integration.
- The user reports that HakiOS boots garnet; its source specifies boot header version 4 and a separate loader workflow that must not be assumed compatible with UniXNU.
- The candidate firmware package roots and submodules follow its DeviceBuild.py; vendor binaries and their provenance are not verified.
- A preliminary DSC/FDF integration patch avoids redeclaring inherited DiskIo, FAT, HobLib and FdtLib; it has not been compiled or booted.
- A read-only checker rejects unknown firmware revisions and modified relevant files before checking patch applicability.
- UniXNU firmware.patches targets EDK II, not Mu-Silicium, so the device UEFI patch is not automatically applied by that setting.
- A read-only inventory extracts garnet binary INF and RAW references from the pinned UEFI source without redistributing or validating their files.
- The proposed UniXNUDxe can modify nonvolatile UEFI boot variables; the platform includes VariableRuntimeDxe but its backing store, manual-launch path and recovery remain unverified.

### 完成条件

- Firmware builds with required modules and boots on the target with logs.

### 当前范围

- Firmware sources and device-specific binary inputs are not yet integrated.
- Do not test firmware with UniXNUDxe before evaluating persistent variable writes and recovery.

### 下一步

- Identify the firmware input list and audit provenance.

### 证据

按下一步操作收集证据。

## CPU 与中断 {#cpu}

`planned`

### 硬件与依赖

- SM7435 CPU topology, PSCI, interrupt controller, timer, and PAC.

### 配置

- The preliminary boot arguments request one CPU.

### 操作步骤

- Verify boot CPU and PAC, then record timer and secondary CPU checkpoints.

### 开发经验

- The shared SMP patch does not apply to the selected XNU 27 profile after its architecture changes; the provisional board omits that series and keeps cpus=1.
- Android on the connected target reported eight processors and did not advertise paca or pacg in its CPU feature list; this does not establish EL1 behavior under UEFI.

### 完成条件

- Each enabled CPU, timer, and interprocessor interrupt works on the target.

### 当前范围

- No CPU or PAC behavior has been observed on the target.

### 下一步

- Collect target CPU feature and boot CPU evidence.

### 证据

按下一步操作收集证据。

## 内存与 DMA {#memory}

`planned`

### 硬件与依赖

- Device RAM banks, reservations, firmware memory map, and DMA requirements.

### 配置

- The board DTS intentionally has no memory node.

### 操作步骤

- Compare target memory descriptions with the exact UEFI memory map.

### 开发经验

- A shared SoC description cannot establish the board's usable RAM ranges.
- A prebuilt reference DTB reports multiple memory entries, including zero-size entries; it has not been validated against the target and dtc emits warnings.
- The JosephMontfort firmware baseline adds reservations compared with the candidate UEFI revision; the HakiOS device overlay further changes the kernel region and adds an XNU payload reservation. None is validated as a UniXNU memory map.

### 完成条件

- RAM and reservations match target observations and loader allocations.

### 当前范围

- RAM and reservation ranges have not been verified.

### 下一步

- Obtain target-specific memory and firmware map evidence.

### 证据

按下一步操作收集证据。

## 存储与根卷 {#storage}

`planned`

### 硬件与依赖

- Garnet UFS controller, firmware block I/O, partition and root inputs.

### 配置

- Native UFS is not selected.

### 操作步骤

- Identify the controller and verify read-only access before considering writes.

### 开发经验

- HakiOS reports storage support; this does not establish UniXNU support.

### 完成条件

- Storage reads, root access, and any approved persistence work on the target.

### 当前范围

- No storage path has been tested in this port.

### 下一步

- Inventory the UFS interface and compatible UniXNU components.

### 证据

按下一步操作收集证据。

## 显示 {#display}

`planned`

### 硬件与依赖

- Garnet panel, firmware framebuffer, pixel format, and backlight.

### 配置

- No display driver or board display wiring has been selected.

### 操作步骤

- Inspect the firmware framebuffer and validate a known frame on the target.

### 开发经验

- A reference project reports display output, not a result for this port.

### 完成条件

- Correct display output and backlight operation are observed on the target.

### 当前范围

- No display output has been tested in this port.

### 下一步

- Identify the target framebuffer and display interfaces.

### 证据

按下一步操作收集证据。

## 输入 {#input}

`planned`

### 硬件与依赖

- Garnet touchscreen, bus, power rails, firmware, and physical buttons.

### 配置

- No input driver or board wiring has been selected.

### 操作步骤

- Check target hardware and driver interfaces before implementing input.

### 开发经验

- Reference touchscreen claims require target and ABI verification.

### 完成条件

- Touch and physical buttons are observed working on the target.

### 当前范围

- No input implementation has been tested in this port.

### 下一步

- Verify touchscreen model and required firmware provenance.

### 证据

按下一步操作收集证据。

## GPU {#gpu}

`planned`

### 硬件与依赖

- Adreno 710 revision, GPU firmware, clocks, mappings, and driver ABI.

### 配置

- Native Adreno support is not selected.

### 操作步骤

- Audit compatible drivers and firmware before enabling GPU access.

### 开发经验

- A separate project reports OpenGL ES; it is not evidence for this port.

### 完成条件

- A verified graphics workload renders correctly on garnet.

### 当前范围

- No GPU driver has been built or tested for this port.

### 下一步

- Inventory the GPU interface and legally obtained firmware.

### 证据

按下一步操作收集证据。

## 网络 {#network}

`planned`

### 硬件与依赖

- Garnet wireless hardware, firmware, transport, and compatible drivers.

### 配置

- No network component is selected.

### 操作步骤

- Identify hardware and dependencies after core boot milestones.

### 开发经验

- Network functionality remains unverified.

### 完成条件

- Network hardware associates and transfers traffic on the target.

### 当前范围

- No network implementation has been tested.

### 下一步

- Identify wireless hardware and firmware inputs.

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`planned`

### 硬件与依赖

- Audio DSP, amplifiers, firmware, and board routing.

### 配置

- No audio component is selected.

### 操作步骤

- Audit target audio hardware and available compatible drivers.

### 开发经验

- Reference audio support is reported as partial.

### 完成条件

- Basic audio playback is observed on the target.

### 当前范围

- No audio implementation has been tested.

### 下一步

- Inventory audio hardware and firmware requirements.

### 证据

按下一步操作收集证据。

## 电源 {#power}

`planned`

### 硬件与依赖

- Garnet PMIC, battery, charging, thermal limits, and power management.

### 配置

- No board-specific power component is selected.

### 操作步骤

- Identify safe read-only measurements and compatible power interfaces.

### 开发经验

- Battery status and charging behavior are not established for this port.

### 完成条件

- Battery reporting and charging behavior are validated on the target.

### 当前范围

- No power management implementation has been tested.

### 下一步

- Inventory power controllers and identify safe measurement methods.

### 证据

按下一步操作收集证据。

## 镜像组装 {#packaging}

`planned`

### 硬件与依赖

- Verified UEFI FD, hardware DTB, XNU payload, image format, and seed.

### 配置

- No boot image or package settings are complete.

### 操作步骤

- Review the selected boot chain and build artifacts before packaging.

### 开发经验

- Reference Android and UEFI build paths use different boot header versions.

### 完成条件

- A reproducible image passes structural checks and an approved device test.

### 当前范围

- No image has been built or validated.

### 下一步

- Establish the firmware and bootloader handoff requirements.

### 证据

按下一步操作收集证据。

## 诊断 {#diagnostics}

`planned`

### 硬件与依赖

- Safe device access, recovery procedure, firmware log and kernel log transport.

### 配置

- Only host scaffold checks exist.

### 操作步骤

- Prepare log capture and obtain approval before device commands.

### 开发经验

- The example guard rejects the kernel build; syntax checks are not hardware evidence.
- Host regression checks verify the candidate firmware paths and guard, and that the UEFI patch does not redeclare inherited library or disk dependencies.
- The original XNU series failed at a board-specific boot-progress patch; a guarded research series preserves the other OS patches and omits that layer. Equivalent diagnostics remain required before a device test.

### 完成条件

- Logs identify each verified firmware and kernel handoff checkpoint.

### 当前范围

- No logs have been collected from the target.

### 下一步

- Identify a safe log transport and recovery procedure.

### 证据

按下一步操作收集证据。

</div>
