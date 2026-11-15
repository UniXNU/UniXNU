# Xiaomi Redmi Pad Pro \(dizi\); ruan unverified

[vildangil/UniXNU-Dizi-Ruan](https://github.com/vildangil/UniXNU-Dizi-Ruan)

<div v-pre>

Xiaomi Redmi Pad Pro \(dizi\), SM7435 \(Parrot\). Bring-up stage: CPU, interrupts, timer and GOP framebuffer through Mu-Silicium diziPkg. No hardware boot evidence yet.

Source record: [porting.toml](https://github.com/vildangil/UniXNU-Dizi-Ruan/blob/981f51b5f09d0b5ddc74e48e0b56c413c29bfd3c/porting.toml), `981f51b5f09d0b5ddc74e48e0b56c413c29bfd3c`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `implemented` |
| [Firmware and boot](#firmware) | `implemented` |
| [CPU and interrupts](#cpu) | `device-verified` |
| [Memory and DMA](#memory) | `planned` |
| [Storage and root](#storage) | `implemented` |
| [Display](#display) | `planned` |
| [Input](#input) | `implemented` |
| [GPU](#gpu) | `planned` |
| [Network](#network) | `planned` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `planned` |
| [Image assembly](#packaging) | `planned` |
| [Diagnostics](#diagnostics) | `planned` |

## Configuration {#configuration}

`implemented`

Components: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`, `DarwinBoot`.

### Hardware and dependencies

- Identify the configuration hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for configuration.

### Procedure

- Follow the configuration stage in the porting guide and record the actual commands.

### Development findings

- feeds.toml previously pinned an SM8550 commit, so status resolved the sm8550 SoC profile; it now pins sm7435-common and status reports soc sm7435.
- board.toml carries the bring-up component set, config fragments, patch series, device tree, Mu-Silicium firmware paths and a 56 MiB payload that fits the 100 MiB boot partition.
- The ADT declares vmm-present = 1: dizi firmware publishes no Apple PMGR and AMFI otherwise panics with 'AMFI: No PMGR?' at ConfigurationSettings.cpp:235.
- 2026-11-15: kernel\_args default to cpus=8 smp=1; \[kernel\] archives add ShengUfs, its KDK-free bindings \(candidate kernel without ShengUfs\), the PMGR bridge and the boot-progress page; \[userdata\] holds the GPT range 0x35a228-0x1d13ffa; ruan's 2.75 GiB window does not fit dizi's UEFI map, and the 1952 MiB window above 4 GiB stops at setconf, so the default window stays.

### Completion criteria

- All source pins resolve; every selected component has a record; status shows the intended overrides and patch order.

### Current limits

- Payload memory is the single 2 GiB DDR region0 at 0x80000000 that UniXNU's ADT generator requires; other RAM sizes are not checked.

### Next action

- Add the root filesystem inputs \(storage driver, userdata root image\).

### Evidence

- `source`: [unixnu status resolves soc sm7435, profile ipados-17.7.11-21H461 and the dizi patch order](https://github.com/vildangil/UniXNU-Dizi-Ruan/blob/981f51b5f09d0b5ddc74e48e0b56c413c29bfd3c/board.toml)

## Firmware and boot {#firmware}

`implemented`

### Hardware and dependencies

- Identify the firmware and boot hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for firmware and boot.

### Procedure

- Follow the firmware and boot stage in the porting guide and record the actual commands.

### Development findings

- Mu-Silicium diziPkg embeds UniXNU, UniXNUDxe, UniXNURamDiskDxe and DarwinBoot; Silicium SEC saves the bootloader x0 \(FDT\) in the entry-argument HOB.
- On dizi the initrd starts with the vendor\_boot LZ4 legacy ramdisk \(0x184C2102\) followed by the FAT32 payload; UniXNURamDiskDxe now skips the LZ4 frames and publishes the payload, so the menu loads \\EFI\\UniXNU\\unixnu.toml.
- The Windows KEP ExitBootServices hook is left out with DISABLE\_KEP; BootShim's image size covers the shim plus the FD.
- Volume and power keys use the PMIC/SPMI reader from the old-ChatGPT branch in diziPkg/Library/UniXNULibDizi; Volume Down timing was shortened and is not yet re-tested.

### Completion criteria

- Firmware image builds, enters UniXNU, publishes the framebuffer and preserves the documented memory reservations.

### Current limits

- The UEFI vendor binaries in Mu-Silicium Binaries/dizi are documented as Redmi Note 13 Pro 5G firmware.

### Next action

- Test Volume Down in the menu with the shortened guard.

### Evidence

- `source`: [DarwinBoot handoff with the green bar observed on dizi on 2026-11-14](https://github.com/vildangil/Mu-Silicium/tree/dizi-bringup)

## CPU and interrupts {#cpu}

`device-verified`

### Hardware and dependencies

- Identify the cpu and interrupts hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for cpu and interrupts.

### Procedure

- Follow the cpu and interrupts stage in the porting guide and record the actual commands.

### Development findings

- 2026-11-14 on dizi with cpus=1: entry probe showed the blue \(kernel entry\) and magenta \(pre-MMU\) bands, and a reset after MMU-on.
- XNU then panicked at fiq\_context\_init writing CNTP\_CTL\_EL0: the hypervisor traps EL1 physical-timer access. sm7435-virtual-timer-only.patch removes that write.
- With the patch XNU passes arm\_init, IOKit and AMFI and stops at 'Failed to mount root device' \(IOKitBSDInit.cpp:984\), which is expected without a root filesystem.

### Completion criteria

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU.

### Current limits

- Secondary CPUs \(SMP\) are not started or tested; cpus=1 stays the default.

### Next action

- Test SMP with an explicit cpus=2 run after root mount works.

### Evidence

- `device`: [XNU reaches 'Failed to mount root device' at IOKitBSDInit.cpp:984 on the panic screen](https://github.com/vildangil/UniXNU-sm7435-common/commit/1765d1bc3601d288f00fa6f7be9b7634b4e10e18)
  Command: <code>fastboot boot out/dizi/ipados-17.7.11-21H461/dizi/boot/boot.img</code>. Revision: `1765d1bc3601d288f00fa6f7be9b7634b4e10e18`.

## Memory and DMA {#memory}

`planned`

### Hardware and dependencies

- Identify the memory and dma hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for memory and dma.

### Procedure

- Follow the memory and dma stage in the porting guide and record the actual commands.

### Development findings

- Collect the first memory and dma observation, its cause when established, and the resulting implementation decision.

### Completion criteria

- All handoff regions are accounted for and each enabled DMA engine accesses its allocated range with the documented cache policy.

### Current limits

- Hardware inputs and implementation are pending for dizi.

### Next action

- Inventory the required memory and dma inputs before implementation.

### Evidence

Collect evidence using the next action.

## Storage and root {#storage}

`implemented`

Components: `ShengUfs`, `VerifiedRoot`, `VirtioMmioBlock`.

### Hardware and dependencies

- Identify the storage and root hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for storage and root.

### Procedure

- Follow the storage and root stage in the porting guide and record the actual commands.

### Development findings

- ShengUfs drives dizi's UFS host \(0x1d84000, SPI 265\) with SMMU stream 0x20 \(native-ufs-stream\). Gunyah blocks the SMMU's GR1 and context banks \(external abort\), so native-ufs-smmu-reuse=1 keeps the firmware's stream-to-bank-2 mapping.
- The GPT read gives userdata at 0x35a228-0x1d13ffa on LUN 0, matching fastboot's partition size.
- DMA straight into caller pages powered the tablet off; native-ufs-zero-copy=0 keeps all DMA in the host buffer.
- With native-ufs-allow-unverified=1 and dizi-ufs-unverified-root.patch the iPadOS 17.7.11 OS volume \(04769D26\) mounts read-only from userdata and launchd starts.
- launchd stops at dyld: libSystem.B.dylib is only in the dyld shared cache of the SystemOS cryptex, which is not mounted yet. A DarwinBoot window above 4 GiB \(0x7A000000 at 0x840000000\) stops at setconf with no interrupts.

### Completion criteria

- Host: register, clock, link and SMMU facts match the board inventory.
- Reads: SCSI capacity, GPT and known blocks are correct; OS/SystemOS windows stay within userdata.
- Root: the configured volume mounts and launchd starts. Persistence: writes survive reboot within the allocated Data region.

### Current limits

- Hardware inputs and implementation are pending for dizi.

### Next action

- Mount the SystemOS cryptex window before launchd \(UniXNU owner SystemOS union\).

### Evidence

- `source`: [dizi changes to ShengUfs: stream, SMMU reuse, zero-copy switch, unverified root](https://github.com/vildangil/UniXNU-Dizi-Ruan/blob/981f51b5f09d0b5ddc74e48e0b56c413c29bfd3c/patches/drivers/ShengUfs-dizi.patch)

## Display {#display}

`planned`

Components: `GopFramebuffer`.

### Hardware and dependencies

- Identify the display hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for display.

### Procedure

- Follow the display stage in the porting guide and record the actual commands.

### Development findings

- Collect the first display observation, its cause when established, and the resulting implementation decision.

### Completion criteria

- A known frame appears with correct geometry and colors, then userland presentation and backlight controls work.

### Current limits

- Hardware inputs and implementation are pending for dizi.

### Next action

- Inventory the required display inputs before implementation.

### Evidence

Collect evidence using the next action.

## Input {#input}

`implemented`

### Hardware and dependencies

- Identify the input hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for input.

### Procedure

- Follow the input stage in the porting guide and record the actual commands.

### Development findings

- UniXNU menu: Volume Up, Volume Down and Power work through the PMIC/SPMI key reader in Mu-Silicium diziPkg/Library/UniXNULibDizi \(from the old-ChatGPT build\). Each press must be held about one second \(2026-11-15\).
- No touch or button input in XNU yet.

### Completion criteria

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive, and buttons produce expected HID reports.

### Current limits

- Hardware inputs and implementation are pending for dizi.

### Next action

- Inventory the required input inputs before implementation.

### Evidence

- `source`: [Menu keys confirmed on dizi 2026-11-15](https://github.com/vildangil/Mu-Silicium/tree/main/Platforms/Xiaomi/diziPkg/Library/UniXNULibDizi)

## GPU {#gpu}

`planned`

### Hardware and dependencies

- Identify the gpu hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for gpu.

### Procedure

- Follow the gpu stage in the porting guide and record the actual commands.

### Development findings

- Collect the first gpu observation, its cause when established, and the resulting implementation decision.

### Completion criteria

- GPU submissions complete, mapping/fence handling is correct, a known image renders, and the selected Metal client presents it.

### Current limits

- Hardware inputs and implementation are pending for dizi.

### Next action

- Inventory the required gpu inputs before implementation.

### Evidence

Collect evidence using the next action.

## Network {#network}

`planned`

### Hardware and dependencies

- Identify the network hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for network.

### Procedure

- Follow the network stage in the porting guide and record the actual commands.

### Development findings

- Collect the first network observation, its cause when established, and the resulting implementation decision.

### Completion criteria

- Scanning, association, address configuration and sustained receive/transmit traffic pass with the selected firmware.

### Current limits

- Hardware inputs and implementation are pending for dizi.

### Next action

- Inventory the required network inputs before implementation.

### Evidence

Collect evidence using the next action.

## Audio {#audio}

`planned`

### Hardware and dependencies

- Identify the audio hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for audio.

### Procedure

- Follow the audio stage in the porting guide and record the actual commands.

### Development findings

- Collect the first audio observation, its cause when established, and the resulting implementation decision.

### Completion criteria

- Each declared route carries the selected audio format through playback or capture and handles start/stop correctly.

### Current limits

- Hardware inputs and implementation are pending for dizi.

### Next action

- Inventory the required audio inputs before implementation.

### Evidence

Collect evidence using the next action.

## Power {#power}

`planned`

### Hardware and dependencies

- Identify the power hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for power.

### Procedure

- Follow the power stage in the porting guide and record the actual commands.

### Development findings

- Collect the first power observation, its cause when established, and the resulting implementation decision.

### Completion criteria

- Declared power controls and battery readings match observations; each claimed sleep/resume transition restores its dependent peripherals.

### Current limits

- Hardware inputs and implementation are pending for dizi.

### Next action

- Inventory the required power inputs before implementation.

### Evidence

Collect evidence using the next action.

## Image assembly {#packaging}

`planned`

### Hardware and dependencies

- Identify the image assembly hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for image assembly.

### Procedure

- Follow the image assembly stage in the porting guide and record the actual commands.

### Development findings

- Collect the first image assembly observation, its cause when established, and the resulting implementation decision.

### Completion criteria

- Kernel and prelink succeed, payload contains all declared inputs, and the boot image matches the bootloader format and size limit.

### Current limits

- Hardware inputs and implementation are pending for dizi.

### Next action

- Inventory the required image assembly inputs before implementation.

### Evidence

Collect evidence using the next action.

## Diagnostics {#diagnostics}

`planned`

### Hardware and dependencies

- Identify the diagnostics hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for diagnostics.

### Procedure

- Follow the diagnostics stage in the porting guide and record the actual commands.

### Development findings

- Collect the first diagnostics observation, its cause when established, and the resulting implementation decision.

### Completion criteria

- Each claimed milestone has a reproducible command, a matching source/image revision and an accessible result.

### Current limits

- Hardware inputs and implementation are pending for dizi.

### Next action

- Inventory the required diagnostics inputs before implementation.

### Evidence

Collect evidence using the next action.

</div>
