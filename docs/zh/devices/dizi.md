# Xiaomi Redmi Pad Pro \(dizi\); ruan unverified

[vildangil/UniXNU-Dizi-Ruan](https://github.com/vildangil/UniXNU-Dizi-Ruan)

<div v-pre>

Xiaomi Redmi Pad Pro \(dizi\), SM7435 \(Parrot\). Bring-up stage: CPU, interrupts, timer and GOP framebuffer through Mu-Silicium diziPkg. No hardware boot evidence yet.

源记录: [porting.toml](https://github.com/vildangil/UniXNU-Dizi-Ruan/blob/981f51b5f09d0b5ddc74e48e0b56c413c29bfd3c/porting.toml), `981f51b5f09d0b5ddc74e48e0b56c413c29bfd3c`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `implemented` |
| [固件与启动](#firmware) | `implemented` |
| [CPU 与中断](#cpu) | `device-verified` |
| [内存与 DMA](#memory) | `planned` |
| [存储与根卷](#storage) | `implemented` |
| [显示](#display) | `planned` |
| [输入](#input) | `implemented` |
| [GPU](#gpu) | `planned` |
| [网络](#network) | `planned` |
| [音频](#audio) | `planned` |
| [电源](#power) | `planned` |
| [镜像组装](#packaging) | `planned` |
| [诊断](#diagnostics) | `planned` |

## 配置 {#configuration}

`implemented`

组件: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`, `DarwinBoot`.

### 硬件与依赖

- Identify the configuration hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for configuration.

### 操作步骤

- Follow the configuration stage in the porting guide and record the actual commands.

### 开发经验

- feeds.toml previously pinned an SM8550 commit, so status resolved the sm8550 SoC profile; it now pins sm7435-common and status reports soc sm7435.
- board.toml carries the bring-up component set, config fragments, patch series, device tree, Mu-Silicium firmware paths and a 56 MiB payload that fits the 100 MiB boot partition.
- The ADT declares vmm-present = 1: dizi firmware publishes no Apple PMGR and AMFI otherwise panics with 'AMFI: No PMGR?' at ConfigurationSettings.cpp:235.
- 2026-11-15: kernel\_args default to cpus=8 smp=1; \[kernel\] archives add ShengUfs, its KDK-free bindings \(candidate kernel without ShengUfs\), the PMGR bridge and the boot-progress page; \[userdata\] holds the GPT range 0x35a228-0x1d13ffa; ruan's 2.75 GiB window does not fit dizi's UEFI map, and the 1952 MiB window above 4 GiB stops at setconf, so the default window stays.

### 完成条件

- All source pins resolve; every selected component has a record; status shows the intended overrides and patch order.

### 当前范围

- Payload memory is the single 2 GiB DDR region0 at 0x80000000 that UniXNU's ADT generator requires; other RAM sizes are not checked.

### 下一步

- Add the root filesystem inputs \(storage driver, userdata root image\).

### 证据

- `source`: [unixnu status resolves soc sm7435, profile ipados-17.7.11-21H461 and the dizi patch order](https://github.com/vildangil/UniXNU-Dizi-Ruan/blob/981f51b5f09d0b5ddc74e48e0b56c413c29bfd3c/board.toml)

## 固件与启动 {#firmware}

`implemented`

### 硬件与依赖

- Identify the firmware and boot hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for firmware and boot.

### 操作步骤

- Follow the firmware and boot stage in the porting guide and record the actual commands.

### 开发经验

- Mu-Silicium diziPkg embeds UniXNU, UniXNUDxe, UniXNURamDiskDxe and DarwinBoot; Silicium SEC saves the bootloader x0 \(FDT\) in the entry-argument HOB.
- On dizi the initrd starts with the vendor\_boot LZ4 legacy ramdisk \(0x184C2102\) followed by the FAT32 payload; UniXNURamDiskDxe now skips the LZ4 frames and publishes the payload, so the menu loads \\EFI\\UniXNU\\unixnu.toml.
- The Windows KEP ExitBootServices hook is left out with DISABLE\_KEP; BootShim's image size covers the shim plus the FD.
- Volume and power keys use the PMIC/SPMI reader from the old-ChatGPT branch in diziPkg/Library/UniXNULibDizi; Volume Down timing was shortened and is not yet re-tested.

### 完成条件

- Firmware image builds, enters UniXNU, publishes the framebuffer and preserves the documented memory reservations.

### 当前范围

- The UEFI vendor binaries in Mu-Silicium Binaries/dizi are documented as Redmi Note 13 Pro 5G firmware.

### 下一步

- Test Volume Down in the menu with the shortened guard.

### 证据

- `source`: [DarwinBoot handoff with the green bar observed on dizi on 2026-11-14](https://github.com/vildangil/Mu-Silicium/tree/dizi-bringup)

## CPU 与中断 {#cpu}

`device-verified`

### 硬件与依赖

- Identify the cpu and interrupts hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for cpu and interrupts.

### 操作步骤

- Follow the cpu and interrupts stage in the porting guide and record the actual commands.

### 开发经验

- 2026-11-14 on dizi with cpus=1: entry probe showed the blue \(kernel entry\) and magenta \(pre-MMU\) bands, and a reset after MMU-on.
- XNU then panicked at fiq\_context\_init writing CNTP\_CTL\_EL0: the hypervisor traps EL1 physical-timer access. sm7435-virtual-timer-only.patch removes that write.
- With the patch XNU passes arm\_init, IOKit and AMFI and stops at 'Failed to mount root device' \(IOKitBSDInit.cpp:984\), which is expected without a root filesystem.

### 完成条件

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU.

### 当前范围

- Secondary CPUs \(SMP\) are not started or tested; cpus=1 stays the default.

### 下一步

- Test SMP with an explicit cpus=2 run after root mount works.

### 证据

- `device`: [XNU reaches 'Failed to mount root device' at IOKitBSDInit.cpp:984 on the panic screen](https://github.com/vildangil/UniXNU-sm7435-common/commit/1765d1bc3601d288f00fa6f7be9b7634b4e10e18)
  Command: <code>fastboot boot out/dizi/ipados-17.7.11-21H461/dizi/boot/boot.img</code>. Revision: `1765d1bc3601d288f00fa6f7be9b7634b4e10e18`.

## 内存与 DMA {#memory}

`planned`

### 硬件与依赖

- Identify the memory and dma hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for memory and dma.

### 操作步骤

- Follow the memory and dma stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first memory and dma observation, its cause when established, and the resulting implementation decision.

### 完成条件

- All handoff regions are accounted for and each enabled DMA engine accesses its allocated range with the documented cache policy.

### 当前范围

- Hardware inputs and implementation are pending for dizi.

### 下一步

- Inventory the required memory and dma inputs before implementation.

### 证据

按下一步操作收集证据。

## 存储与根卷 {#storage}

`implemented`

组件: `ShengUfs`, `VerifiedRoot`, `VirtioMmioBlock`.

### 硬件与依赖

- Identify the storage and root hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for storage and root.

### 操作步骤

- Follow the storage and root stage in the porting guide and record the actual commands.

### 开发经验

- ShengUfs drives dizi's UFS host \(0x1d84000, SPI 265\) with SMMU stream 0x20 \(native-ufs-stream\). Gunyah blocks the SMMU's GR1 and context banks \(external abort\), so native-ufs-smmu-reuse=1 keeps the firmware's stream-to-bank-2 mapping.
- The GPT read gives userdata at 0x35a228-0x1d13ffa on LUN 0, matching fastboot's partition size.
- DMA straight into caller pages powered the tablet off; native-ufs-zero-copy=0 keeps all DMA in the host buffer.
- With native-ufs-allow-unverified=1 and dizi-ufs-unverified-root.patch the iPadOS 17.7.11 OS volume \(04769D26\) mounts read-only from userdata and launchd starts.
- launchd stops at dyld: libSystem.B.dylib is only in the dyld shared cache of the SystemOS cryptex, which is not mounted yet. A DarwinBoot window above 4 GiB \(0x7A000000 at 0x840000000\) stops at setconf with no interrupts.

### 完成条件

- Host: register, clock, link and SMMU facts match the board inventory.
- Reads: SCSI capacity, GPT and known blocks are correct; OS/SystemOS windows stay within userdata.
- Root: the configured volume mounts and launchd starts. Persistence: writes survive reboot within the allocated Data region.

### 当前范围

- Hardware inputs and implementation are pending for dizi.

### 下一步

- Mount the SystemOS cryptex window before launchd \(UniXNU owner SystemOS union\).

### 证据

- `source`: [dizi changes to ShengUfs: stream, SMMU reuse, zero-copy switch, unverified root](https://github.com/vildangil/UniXNU-Dizi-Ruan/blob/981f51b5f09d0b5ddc74e48e0b56c413c29bfd3c/patches/drivers/ShengUfs-dizi.patch)

## 显示 {#display}

`planned`

组件: `GopFramebuffer`.

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

- Hardware inputs and implementation are pending for dizi.

### 下一步

- Inventory the required display inputs before implementation.

### 证据

按下一步操作收集证据。

## 输入 {#input}

`implemented`

### 硬件与依赖

- Identify the input hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for input.

### 操作步骤

- Follow the input stage in the porting guide and record the actual commands.

### 开发经验

- UniXNU menu: Volume Up, Volume Down and Power work through the PMIC/SPMI key reader in Mu-Silicium diziPkg/Library/UniXNULibDizi \(from the old-ChatGPT build\). Each press must be held about one second \(2026-11-15\).
- No touch or button input in XNU yet.

### 完成条件

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive, and buttons produce expected HID reports.

### 当前范围

- Hardware inputs and implementation are pending for dizi.

### 下一步

- Inventory the required input inputs before implementation.

### 证据

- `source`: [Menu keys confirmed on dizi 2026-11-15](https://github.com/vildangil/Mu-Silicium/tree/main/Platforms/Xiaomi/diziPkg/Library/UniXNULibDizi)

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

- Hardware inputs and implementation are pending for dizi.

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

- Hardware inputs and implementation are pending for dizi.

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

- Hardware inputs and implementation are pending for dizi.

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

- Hardware inputs and implementation are pending for dizi.

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

- Hardware inputs and implementation are pending for dizi.

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

- Hardware inputs and implementation are pending for dizi.

### 下一步

- Inventory the required diagnostics inputs before implementation.

### 证据

按下一步操作收集证据。

</div>
