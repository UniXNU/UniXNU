# Preliminary garnet bring-up; not bootable

[Scarpy19/UniXNU-garnet](https://github.com/Scarpy19/UniXNU-garnet)

<div v-pre>

Preliminary research scaffold; no verified build or device boot.

Source record: [porting.toml](https://github.com/Scarpy19/UniXNU-garnet/blob/86e64537fa71951f420b0b3ef442455b936e6c71/porting.toml), `86e64537fa71951f420b0b3ef442455b936e6c71`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `planned` |
| [Firmware and boot](#firmware) | `planned` |
| [CPU and interrupts](#cpu) | `planned` |
| [Memory and DMA](#memory) | `planned` |
| [Storage and root](#storage) | `planned` |
| [Display](#display) | `planned` |
| [Input](#input) | `planned` |
| [GPU](#gpu) | `planned` |
| [Network](#network) | `planned` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `planned` |
| [Image assembly](#packaging) | `planned` |
| [Diagnostics](#diagnostics) | `planned` |

## Configuration {#configuration}

`planned`

Components: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`, `DarwinBoot`.

### Hardware and dependencies

- Pinned UniXNU and preliminary SM7435 sources; target OS profile.

### Configuration

- Example guard remains enabled; profile 27 is unverified.

### Procedure

- Resolve sources and inspect configuration after required inputs are established.

### Development findings

- The SoC feed is pinned; ARM64e compatibility is not established.
- WSL defconfig and status resolve garnet and its SM7435 feed. Empty kernel.archives selects automatic component recipes, while auxiliary archives and several components' research-profile ABI support need review.
- The guarded board selects a provisional OS patch series without the incompatible boot-progress layer; equivalent diagnostics and profile compatibility are unverified.
- The guarded board file describes candidate UEFI package roots and submodules, not a verified build configuration.
- The user authorized system packages and administrator access for compilation; the WSL host check reports llvm-config missing. The official installer was started as WSL root; completion is pending.

### Completion criteria

- Configuration and all selected component dependencies resolve with reviewed inputs.

### Current limits

- The board is deliberately incomplete and is not ready to build.

### Next action

- Verify PAC and complete the board resource inventory.

### Evidence

Collect evidence using the next action.

## Firmware and boot {#firmware}

`planned`

### Hardware and dependencies

- Garnet UEFI source, firmware files, device DTB, and redistribution terms.

### Configuration

- Guarded board configuration lists candidate garnet DSC, FD, package roots and source-declared submodules; it does not apply the UEFI patch or supply the required vendor files.

### Procedure

- Audit the exact UEFI revision and integrate UniXNU and DarwinBoot modules.

### Development findings

- The audited garnet firmware configuration does not establish UniXNU integration.
- The user reports that HakiOS boots garnet; its source specifies boot header version 4 and a separate loader workflow that must not be assumed compatible with UniXNU.
- The candidate firmware package roots and submodules follow its DeviceBuild.py; vendor binaries and their provenance are not verified.
- A preliminary DSC/FDF integration patch avoids redeclaring inherited DiskIo, FAT, HobLib and FdtLib; it has not been compiled or booted.
- A read-only checker rejects unknown firmware revisions and modified relevant files before checking patch applicability.
- UniXNU firmware.patches targets EDK II, not Mu-Silicium, so the device UEFI patch is not automatically applied by that setting.
- A read-only inventory extracts garnet binary INF and RAW references from the pinned UEFI source without redistributing or validating their files.
- The proposed UniXNUDxe can modify nonvolatile UEFI boot variables; the platform includes VariableRuntimeDxe but its backing store, manual-launch path and recovery remain unverified.

### Completion criteria

- Firmware builds with required modules and boots on the target with logs.

### Current limits

- Firmware sources and device-specific binary inputs are not yet integrated.
- Do not test firmware with UniXNUDxe before evaluating persistent variable writes and recovery.

### Next action

- Identify the firmware input list and audit provenance.

### Evidence

Collect evidence using the next action.

## CPU and interrupts {#cpu}

`planned`

### Hardware and dependencies

- SM7435 CPU topology, PSCI, interrupt controller, timer, and PAC.

### Configuration

- The preliminary boot arguments request one CPU.

### Procedure

- Verify boot CPU and PAC, then record timer and secondary CPU checkpoints.

### Development findings

- The shared SMP patch does not apply to the selected XNU 27 profile after its architecture changes; the provisional board omits that series and keeps cpus=1.
- Android on the connected target reported eight processors and did not advertise paca or pacg in its CPU feature list; this does not establish EL1 behavior under UEFI.

### Completion criteria

- Each enabled CPU, timer, and interprocessor interrupt works on the target.

### Current limits

- No CPU or PAC behavior has been observed on the target.

### Next action

- Collect target CPU feature and boot CPU evidence.

### Evidence

Collect evidence using the next action.

## Memory and DMA {#memory}

`planned`

### Hardware and dependencies

- Device RAM banks, reservations, firmware memory map, and DMA requirements.

### Configuration

- The board DTS intentionally has no memory node.

### Procedure

- Compare target memory descriptions with the exact UEFI memory map.

### Development findings

- A shared SoC description cannot establish the board's usable RAM ranges.
- A prebuilt reference DTB reports multiple memory entries, including zero-size entries; it has not been validated against the target and dtc emits warnings.
- The JosephMontfort firmware baseline adds reservations compared with the candidate UEFI revision; the HakiOS device overlay further changes the kernel region and adds an XNU payload reservation. None is validated as a UniXNU memory map.

### Completion criteria

- RAM and reservations match target observations and loader allocations.

### Current limits

- RAM and reservation ranges have not been verified.

### Next action

- Obtain target-specific memory and firmware map evidence.

### Evidence

Collect evidence using the next action.

## Storage and root {#storage}

`planned`

### Hardware and dependencies

- Garnet UFS controller, firmware block I/O, partition and root inputs.

### Configuration

- Native UFS is not selected.

### Procedure

- Identify the controller and verify read-only access before considering writes.

### Development findings

- HakiOS reports storage support; this does not establish UniXNU support.

### Completion criteria

- Storage reads, root access, and any approved persistence work on the target.

### Current limits

- No storage path has been tested in this port.

### Next action

- Inventory the UFS interface and compatible UniXNU components.

### Evidence

Collect evidence using the next action.

## Display {#display}

`planned`

### Hardware and dependencies

- Garnet panel, firmware framebuffer, pixel format, and backlight.

### Configuration

- No display driver or board display wiring has been selected.

### Procedure

- Inspect the firmware framebuffer and validate a known frame on the target.

### Development findings

- A reference project reports display output, not a result for this port.

### Completion criteria

- Correct display output and backlight operation are observed on the target.

### Current limits

- No display output has been tested in this port.

### Next action

- Identify the target framebuffer and display interfaces.

### Evidence

Collect evidence using the next action.

## Input {#input}

`planned`

### Hardware and dependencies

- Garnet touchscreen, bus, power rails, firmware, and physical buttons.

### Configuration

- No input driver or board wiring has been selected.

### Procedure

- Check target hardware and driver interfaces before implementing input.

### Development findings

- Reference touchscreen claims require target and ABI verification.

### Completion criteria

- Touch and physical buttons are observed working on the target.

### Current limits

- No input implementation has been tested in this port.

### Next action

- Verify touchscreen model and required firmware provenance.

### Evidence

Collect evidence using the next action.

## GPU {#gpu}

`planned`

### Hardware and dependencies

- Adreno 710 revision, GPU firmware, clocks, mappings, and driver ABI.

### Configuration

- Native Adreno support is not selected.

### Procedure

- Audit compatible drivers and firmware before enabling GPU access.

### Development findings

- A separate project reports OpenGL ES; it is not evidence for this port.

### Completion criteria

- A verified graphics workload renders correctly on garnet.

### Current limits

- No GPU driver has been built or tested for this port.

### Next action

- Inventory the GPU interface and legally obtained firmware.

### Evidence

Collect evidence using the next action.

## Network {#network}

`planned`

### Hardware and dependencies

- Garnet wireless hardware, firmware, transport, and compatible drivers.

### Configuration

- No network component is selected.

### Procedure

- Identify hardware and dependencies after core boot milestones.

### Development findings

- Network functionality remains unverified.

### Completion criteria

- Network hardware associates and transfers traffic on the target.

### Current limits

- No network implementation has been tested.

### Next action

- Identify wireless hardware and firmware inputs.

### Evidence

Collect evidence using the next action.

## Audio {#audio}

`planned`

### Hardware and dependencies

- Audio DSP, amplifiers, firmware, and board routing.

### Configuration

- No audio component is selected.

### Procedure

- Audit target audio hardware and available compatible drivers.

### Development findings

- Reference audio support is reported as partial.

### Completion criteria

- Basic audio playback is observed on the target.

### Current limits

- No audio implementation has been tested.

### Next action

- Inventory audio hardware and firmware requirements.

### Evidence

Collect evidence using the next action.

## Power {#power}

`planned`

### Hardware and dependencies

- Garnet PMIC, battery, charging, thermal limits, and power management.

### Configuration

- No board-specific power component is selected.

### Procedure

- Identify safe read-only measurements and compatible power interfaces.

### Development findings

- Battery status and charging behavior are not established for this port.

### Completion criteria

- Battery reporting and charging behavior are validated on the target.

### Current limits

- No power management implementation has been tested.

### Next action

- Inventory power controllers and identify safe measurement methods.

### Evidence

Collect evidence using the next action.

## Image assembly {#packaging}

`planned`

### Hardware and dependencies

- Verified UEFI FD, hardware DTB, XNU payload, image format, and seed.

### Configuration

- No boot image or package settings are complete.

### Procedure

- Review the selected boot chain and build artifacts before packaging.

### Development findings

- Reference Android and UEFI build paths use different boot header versions.

### Completion criteria

- A reproducible image passes structural checks and an approved device test.

### Current limits

- No image has been built or validated.

### Next action

- Establish the firmware and bootloader handoff requirements.

### Evidence

Collect evidence using the next action.

## Diagnostics {#diagnostics}

`planned`

### Hardware and dependencies

- Safe device access, recovery procedure, firmware log and kernel log transport.

### Configuration

- Only host scaffold checks exist.

### Procedure

- Prepare log capture and obtain approval before device commands.

### Development findings

- The example guard rejects the kernel build; syntax checks are not hardware evidence.
- Host regression checks verify the candidate firmware paths and guard, and that the UEFI patch does not redeclare inherited library or disk dependencies.
- The original XNU series failed at a board-specific boot-progress patch; a guarded research series preserves the other OS patches and omits that layer. Equivalent diagnostics remain required before a device test.

### Completion criteria

- Logs identify each verified firmware and kernel handoff checkpoint.

### Current limits

- No logs have been collected from the target.

### Next action

- Identify a safe log transport and recovery procedure.

### Evidence

Collect evidence using the next action.

</div>
