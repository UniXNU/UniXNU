# Xiaomi Redmi Note 9 \(Gytis283123\)

[Gytis283123/UniXNU-merlinx](https://github.com/Gytis283123/UniXNU-merlinx)

<div v-pre>

Redmi Note 9 bring-up: UEFI boot, native eMMC, SystemOS cache and launchd userland, plus a Mali-G52 kernel path that completes M2/M3/M4/M6, reads GPU\_ID and reports MALI RC 0; a GPU job/fence, NativeMali service, PanVK device and userland display remain incomplete.

源记录: [porting.toml](https://github.com/Gytis283123/UniXNU-merlinx/blob/21654d3062da9eccd2ac78827065d90487c55a2e/porting.toml), `21654d3062da9eccd2ac78827065d90487c55a2e`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `device-verified` |
| [固件与启动](#firmware) | `device-verified` |
| [CPU 与中断](#cpu) | `implemented` |
| [内存与 DMA](#memory) | `implemented` |
| [存储与根卷](#storage) | `device-verified` |
| [显示](#display) | `implemented` |
| [输入](#input) | `planned` |
| [GPU](#gpu) | `implemented` |
| [网络](#network) | `planned` |
| [音频](#audio) | `planned` |
| [电源](#power) | `implemented` |
| [镜像组装](#packaging) | `implemented` |
| [诊断](#diagnostics) | `device-verified` |

## 配置 {#configuration}

`device-verified`

组件: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `DarwinBoot`, `XnuPrelink`.

### 硬件与依赖

- MT6768 board resources, PMIC keys, p33 boot partition and the iPadOS 17.7.11 21H461 restore profile.

### 配置

- board.toml selects merlinx\_defconfig, the iPad7,1 restore profile, the p33 boot layout and the native eMMC root path.

### 操作步骤

- Build the firmware, kernel, payload and boot image, then flash the image to p33 with fastboot.

### 开发经验

- The bootloader rejects fastboot boot, so every test image is written to p33 with fastboot flash boot.

### 完成条件

- Source pins resolve, the defconfig applies and the selected board tests boot from p33.

### 当前范围

- Only the iPadOS 17.7.11 profile is configured. The final phone target needs a separate OS profile.

### 下一步

- Keep the board keys and OS profile synchronized with the packaging manifest.

### 证据

- `source`: [Board name, SoC, OS profile, components and package defconfig are declared.](https://github.com/Gytis283123/UniXNU-merlinx/blob/21654d3062da9eccd2ac78827065d90487c55a2e/board.toml)
- `device`: [The UEFI menu, kernel and payload start on the phone.](https://github.com/Dracen-W/UniXNU-merlinx)
  Command: <code>fastboot flash boot &lt;merlinx-boot.img&gt;</code>. Revision: `237c204655577c1ed1c9536a4bdc890bb2eaf1cc`.

## 固件与启动 {#firmware}

`device-verified`

组件: `DarwinBoot`, `XnuPrelink`.

### 硬件与依赖

- merlinx.dts, the firmware volume from uefi-merlinx and the boot image parameters for p33.

### 配置

- The boot image wraps the fixed BootShim, the 3 MiB firmware volume, the trimmed DTB and the payload ramdisk.

### 操作步骤

- Build the firmware volume, generate the ADT sidecar and pack the p33 boot image.

### 开发经验

- The BootShim self-overwrite is fixed by relocating the copy and clean block before loading the firmware volume.

### 完成条件

- Firmware enters UniXNU, publishes the framebuffer and boots the payload from p33.

### 当前范围

- The bootloader does not support fastboot boot. Recovery uses a stock boot image.

### 下一步

- Record the firmware revision and the boot image hash for each hardware run.

### 证据

- `source`: [The device tree reserves the splash region and describes the board.](https://github.com/Gytis283123/UniXNU-merlinx/blob/21654d3062da9eccd2ac78827065d90487c55a2e/dts/merlinx.dts)
- `device`: [UniXNU and DarwinBoot start from p33.](https://github.com/Dracen-W/UniXNU-merlinx)
  Command: <code>fastboot flash boot &lt;merlinx-boot.img&gt;</code>. Revision: `237c204655577c1ed1c9536a4bdc890bb2eaf1cc`.

## CPU 与中断 {#cpu}

`implemented`

组件: `ArmCpu`.

### 硬件与依赖

- MT6768 CPU affinities, GIC and the ARM generic timer.

### 配置

- merlinx\_defconfig enables ArmCpu, the architectural timer and the native SMP secondary path.

### 操作步骤

- Build the kernel and inspect the CPU and interrupt initialization path on hardware.

### 开发经验

- XNU reaches the scheduler and userland with the native timer entry.

### 完成条件

- Every enabled CPU enters the scheduler and timer handling works on each CPU.

### 当前范围

- GIC affinity and per-CPU interrupt coverage are not fully audited.

### 下一步

- Record the per-CPU startup checkpoints and the GIC configuration.

### 证据

- `source`: [ArmCpu and the architectural timer are selected.](https://github.com/Gytis283123/UniXNU-merlinx/blob/21654d3062da9eccd2ac78827065d90487c55a2e/configs/merlinx_defconfig)

## 内存与 DMA {#memory}

`implemented`

组件: `ArmDTPlatform`.

### 硬件与依赖

- 4 GiB DRAM, the owned memory window and the firmware framebuffer reservations.

### 配置

- The ADT generator receives DRAM size, owned memory size and CPU register values from board.toml.

### 操作步骤

- Generate the ADT sidecar and boot the kernel with the reserved memory layout.

### 开发经验

- The kernel window and owned memory handoff allow XNU entry and root mount.

### 完成条件

- Every reserved region is described, and the kernel does not overlap firmware or framebuffer memory.

### 当前范围

- DMA ownership and SMMU translation are not implemented for this board.

### 下一步

- Audit the reserved-memory and DMA windows against the final device tree.

### 证据

- `source`: [The generator encodes the DRAM and owned-memory values.](https://github.com/Gytis283123/UniXNU-merlinx/blob/21654d3062da9eccd2ac78827065d90487c55a2e/scripts/make-merlinx-adt.py)

## 存储与根卷 {#storage}

`device-verified`

组件: `NativeEmmc`, `RamBlock`.

### 硬件与依赖

- The eMMC userdata partition, the OS and SystemOS APFS volumes and the local Data seed.

### 配置

- NativeEmmc publishes userdata and the OS and SystemOS volumes. The owner path mounts the SystemOS cache carrier and a packed Data seed.

### 操作步骤

- Flash the boot image, start XNU and read the ROM/status output.

### 开发经验

- NativeEmmc replaces the timed-out UEFI storage path. The kernel mounts SystemOS, executes initproc and reaches launchd, xpcproxy and SpringBoard. The macOS-generated Data seed mounts read-write and disables watchdogd through the launchd disabled plist.

### 完成条件

- Root and SystemOS mount, initproc runs, Data is writable and the launchd service graph remains alive.

### 当前范围

- Data is a bring-up seed. The NativeEmmc manifest backend and UFS persistence are stubbed, so the Data store is volatile and the full user data set is not present.

### 下一步

- Verify writable /private/var across reboot, then replace the bring-up stubs and keep watchdogd disabled only for diagnostics.

### 证据

- `source`: [NativeEmmc, RamBlock and the owner Data path are selected.](https://github.com/Gytis283123/UniXNU-merlinx/blob/21654d3062da9eccd2ac78827065d90487c55a2e/configs/merlinx_defconfig)
- `device`: [SystemOS mounts, initproc runs and launchd exec succeeds.](https://github.com/Dracen-W/UniXNU-merlinx)
  Command: <code>fastboot flash boot &lt;merlinx-boot.img&gt;</code>. Revision: `237c204655577c1ed1c9536a4bdc890bb2eaf1cc`.

## 显示 {#display}

`implemented`

### 硬件与依赖

- The UEFI GOP framebuffer at 1080x2340 and the panning offset observed on the panel.

### 配置

- The kernel uses the retained GOP framebuffer for panic and boot-stage text. Userland display ownership is not configured.

### 操作步骤

- Flash a diagnostic image and read the status lines from the panel.

### 开发经验

- The GOP base, row stride and 32-bit format work. The kernel draws ROOT, VOL, CACHE, EXEC, LAUNCHD and Mali diagnostics. Userland reaches SpringBoard, but IOMFB\_FDR\_loader exits with status 1 and no scanout provider is published.

### 完成条件

- The kernel console is visible and userland presentation and backlight control work.

### 当前范围

- No userland display provider or renderer is implemented. IOMFB\_FDR\_loader fails before GPU display handoff. The scanout starts mid-panel.

### 下一步

- Trace IOMFB\_FDR\_loader exit 1 and add the userland display and GPU scanout path after the service graph is stable.

### 证据

- `source`: [The GOP status lines and panic screen are linked into the kernel.](https://github.com/Gytis283123/UniXNU-merlinx/blob/21654d3062da9eccd2ac78827065d90487c55a2e/patches/xnu/offline-owner-systemos-mount.patch)

## 输入 {#input}

`planned`

### 硬件与依赖

- PMIC keys, volume-up, volume-down and power routing.

### 配置

- The UEFI menu uses volume-down to scroll and volume-up or power to select. No userland input path is configured.

### 操作步骤

- Measure key events in the UEFI menu and later in userland.

### 开发经验

- The PMIC mask covers power and volume-up, so both keys select a menu entry.

### 完成条件

- Touch or buttons produce stable HID events in userland.

### 当前范围

- No userland touch or HID provider is implemented.

### 下一步

- Define the input provider after the userland display path.

### 证据

按下一步操作收集证据。

## GPU {#gpu}

`implemented`

组件: `MaliG52`, `MaliMetal`.

### 硬件与依赖

- Mali-G52 r1p0 at 0x13040000, MT6358 VGPU/VSRAM via pwrap WACS2, and the SPM, INFRACFG, topckgen and mfgcfg clock and power windows.
- NativeMali fixed external-method ABI and the MaliMetal MM3 pan\_kmod seam.

### 配置

- MaliG52 is selected by board.toml and components.toml. The kernel personality matches mediatek,mali. build-mali-g52.py is invoked with --m2-writes --m3-writes --m4-writes --m6-writes so power, reset, MMU and job-write stages are compiled in. The IOKit glue, archive layout and build integration follow the official Adreno740 driver as the reference implementation; the Mali register, power and clock facts remain from MediaTek and panfrost sources. MaliMetal is the userland Metal/PanVK frontend and is not yet selected by the kernel build.

### 操作步骤

- Build the kernel, build a payload with the Mali diagnostic image, flash it to p33 and read the MALI status lines through the GOP framebuffer.
- For the userland path, build PanVK with the MaliMetal patch series and open the NativeMali service from the MaliMetal bundle.

### 开发经验

- The kernel matches the Mali provider and maps all six windows. GICD\_PIDR2 reads 0x3b, proving the physical MMIO path. PMIC PSEQ\_ID reads 0x0800, proving pwrap reads. M2 power/clock/domain setup completes, the M3 GPU reset and M4 MMU initialization run, and the M6 job-write stage is enabled.
- GPU\_ID reads 0x74021000, which masks to product 0x7002 \(Mali-G52\). MALI RC is 0, and the GPU service publishes its device state. No GPU job, completed fence, PanVK device or userland Metal device has run yet.
- MaliMetal contains the host-tested NativeMali client and the MM3 device/sync patch series; the mesa-panvk CI job compiles the seam but the NativeMali IOUserClient is not installed.

### 完成条件

- M2 completes, GPU\_ID reads 0x70021000 with the expected feature and present masks, and a bounded GPU submission returns a completed fence.

### 当前范围

- The kernel path is confirmed through reset and MMU setup, but no job/fence has completed. The NativeMali IOUserClient and service are not installed in the current boot image, so MM4 cannot create a PanVK device on hardware. PanVK's 144 MB JM indirect buffer also exceeds the current 128 MB NativeMali per-BO limit. Userland display remains at IOMFB\_FDR\_loader exit 1.

### 下一步

- Build and install the NativeMali IOUserClient, lower or extend the PanVK indirect allocation, cross-build the target PanVK dylib, then run one bounded PanVK job and record its fence.

### 证据

- `source`: [The IOKit service matches the ADT Mali node, maps the GPU and power windows and exposes the diagnostic stages.](https://github.com/Gytis283123/UniXNU-merlinx/blob/21654d3062da9eccd2ac78827065d90487c55a2e/drivers/MaliG52/xnu/NativeMaliGpuService.cpp)
- `source`: [The MaliG52 component pins revision be5ed4437fed98def5b9e392f9fa4da790b341e1 and the M2/M3/M4/M6 build recipe.](https://github.com/Gytis283123/UniXNU-merlinx/blob/21654d3062da9eccd2ac78827065d90487c55a2e/components.toml)
- `device`: [MALI RC 0; GPU\_ID 0x74021000; M3 reset, M4 MMU and M6 job-write stages enabled.](https://github.com/Dracen-W/UniXNU-merlinx)
  Command: <code>fastboot flash boot out/merlinx-uefi-emmc-mali-m4m6.img</code>. Revision: `22f479e03dcdf22006415cb22300f509faa75bbf`.
- `host`: [All five jobs passed, including the full mesa-panvk compile of the 0001-0006 patch series.](https://github.com/Dracen-W/MaliMetal/actions/runs/41444900463)
  Command: <code>tests/run.sh; meson setup build-vk ...; ninja -C build-vk src/panfrost/vulkan/libvulkan_panfrost.so</code>. Revision: `df45b652c8d321c4a98d4195c8eb47896c62072d`.

## 网络 {#network}

`planned`

### 硬件与依赖

- Wi-Fi and Bluetooth controllers and their firmware.

### 配置

- No network driver is selected.

### 操作步骤

- Inventory the wireless hardware and firmware before implementing a driver.

### 开发经验

- No network path exists in the current image.

### 完成条件

- Scanning, association and sustained traffic pass with the selected firmware.

### 当前范围

- Network support is outside the current bring-up scope.

### 下一步

- Inventory the wireless hardware when userland services are stable.

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`planned`

### 硬件与依赖

- Audio DSP, codec and speaker routing.

### 配置

- No audio driver is selected.

### 操作步骤

- Inventory the audio DSP and codec before implementing a route.

### 开发经验

- No audio path exists in the current image.

### 完成条件

- A declared route carries audio through playback or capture.

### 当前范围

- Audio support is outside the current bring-up scope.

### 下一步

- Inventory the audio hardware after launchd services are stable.

### 证据

按下一步操作收集证据。

## 电源 {#power}

`implemented`

### 硬件与依赖

- MT6768 PMIC, power keys and the platform power handoff.

### 配置

- The merlinx platform power archive and the sheng PMGR integration are linked into the kernel.

### 操作步骤

- Build the platform power archive and boot the kernel from p33.

### 开发经验

- The PMIC keys drive the UEFI menu and the kernel reaches launchd with the platform power path linked.

### 完成条件

- Declared power controls and battery readings match the board and sleep/resume restores peripherals.

### 当前范围

- Battery reporting and suspend/resume are not implemented.

### 下一步

- Add battery reporting and a suspend/resume path when userland is stable.

### 证据

- `source`: [The platform power archive is built for the kernel.](https://github.com/Gytis283123/UniXNU-merlinx/blob/21654d3062da9eccd2ac78827065d90487c55a2e/scripts/build-merlinx-platform-power.py)

## 镜像组装 {#packaging}

`implemented`

组件: `DarwinBoot`, `XnuPrelink`.

### 硬件与依赖

- Kernel, firmware volume, DTB, payload and the packed Data seed.

### 配置

- board.toml declares the p33 boot size, package defconfig and payload inputs. scripts/package.sh is the fixed release entry point.

### 操作步骤

- Run scripts/package.sh with the selected OS profile and local inputs, then flash the boot image to p33.

### 开发经验

- Kernel and payload builds succeed with the packed Data seed. The validation image carries the seed and boot stages.

### 完成条件

- The release command writes boot.img, payload.img and kernel.macho with a manifest that verifies.

### 当前范围

- The current Data seed uses bring-up stubs and is not a production image. The package release has not replaced the manual build loop.

### 下一步

- Run scripts/package.sh --check and record its manifest in this area.

### 证据

- `source`: [The fixed packaging entry point is present.](https://github.com/Gytis283123/UniXNU-merlinx/blob/21654d3062da9eccd2ac78827065d90487c55a2e/scripts/package.sh)

## 诊断 {#diagnostics}

`device-verified`

### 硬件与依赖

- Panel output, panic screen and the GOP status lines.

### 配置

- The kernel draws ROOT, VOL, CACHE, EXEC and LAUNCHD through the GOP framebuffer. The panic screen renders kernel panics on the panel.

### 操作步骤

- Flash a diagnostic image to p33 and read the panel.

### 开发经验

- The status lines identified the cache and launchd checkpoints without a UART. The Mali diagnostics add MATCH, START, RC, M2W, M2P, PMIC, GIC and staged M2 voltage markers. The launchd exit trace showed IOMFB\_FDR\_loader exit 1 while SpringBoard did not exit.

### 完成条件

- Each claimed milestone has a panel checkpoint or a reproducible panic result.

### 当前范围

- There is no UART and no userland log transport. The current Mali image omits the panic screen because the local UEFI font input was unavailable. Data I/O and userland display remain inferred from panel checkpoints.

### 下一步

- Add pwrap read sub-markers for the VSRAM path and restore the panic screen in the next CI payload build.

### 证据

- `source`: [The device page records the panel checkpoints and their limits.](https://github.com/Gytis283123/UniXNU-merlinx/blob/21654d3062da9eccd2ac78827065d90487c55a2e/docs/devices/merlinx.md)
- `device`: [The panel shows ROOT, VOL, CACHE, EXEC and LAUNCHD.](https://github.com/Dracen-W/UniXNU-merlinx)
  Command: <code>fastboot flash boot &lt;merlinx-boot.img&gt;</code>. Revision: `237c204655577c1ed1c9536a4bdc890bb2eaf1cc`.

</div>
