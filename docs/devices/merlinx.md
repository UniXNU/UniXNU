# Xiaomi Redmi Note 9 \(merlinx\)

[Dracen-W/UniXNU-merlinx](https://github.com/Dracen-W/UniXNU-merlinx)

<div v-pre>

Redmi Note 9 bring-up: UEFI boot, native eMMC, SystemOS cache and launchd userland, plus a Mali-G52 kernel path that completes M2/M3/M4/M6, reads GPU\_ID and reports MALI RC 0; a GPU job/fence, NativeMali service, PanVK device and userland display remain incomplete.

Source record: [porting.toml](https://github.com/Dracen-W/UniXNU-merlinx/blob/c6443a068d0fe662fae2e991be1511b06efb7ef3/porting.toml), `c6443a068d0fe662fae2e991be1511b06efb7ef3`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `device-verified` |
| [Firmware and boot](#firmware) | `device-verified` |
| [CPU and interrupts](#cpu) | `implemented` |
| [Memory and DMA](#memory) | `implemented` |
| [Storage and root](#storage) | `device-verified` |
| [Display](#display) | `implemented` |
| [Input](#input) | `planned` |
| [GPU](#gpu) | `implemented` |
| [Network](#network) | `planned` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `implemented` |
| [Image assembly](#packaging) | `implemented` |
| [Diagnostics](#diagnostics) | `device-verified` |

## Configuration {#configuration}

`device-verified`

Components: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `DarwinBoot`, `XnuPrelink`.

### Hardware and dependencies

- MT6768 board resources, PMIC keys, p33 boot partition and the iPadOS 17.7.11 21H461 restore profile.

### Configuration

- board.toml selects merlinx\_defconfig, the iPad7,1 restore profile, the p33 boot layout and the native eMMC root path.

### Procedure

- Build the firmware, kernel, payload and boot image, then flash the image to p33 with fastboot.

### Development findings

- The bootloader rejects fastboot boot, so every test image is written to p33 with fastboot flash boot.

### Completion criteria

- Source pins resolve, the defconfig applies and the selected board tests boot from p33.

### Current limits

- Only the iPadOS 17.7.11 profile is configured. The final phone target needs a separate OS profile.

### Next action

- Keep the board keys and OS profile synchronized with the packaging manifest.

### Evidence

- `source`: [Board name, SoC, OS profile, components and package defconfig are declared.](https://github.com/Dracen-W/UniXNU-merlinx/blob/c6443a068d0fe662fae2e991be1511b06efb7ef3/board.toml)
- `device`: [The UEFI menu, kernel and payload start on the phone.](https://github.com/Dracen-W/UniXNU-merlinx)
  Command: <code>fastboot flash boot &lt;merlinx-boot.img&gt;</code>. Revision: `237c204655577c1ed1c9536a4bdc890bb2eaf1cc`.

## Firmware and boot {#firmware}

`device-verified`

Components: `DarwinBoot`, `XnuPrelink`.

### Hardware and dependencies

- merlinx.dts, the firmware volume from uefi-merlinx and the boot image parameters for p33.

### Configuration

- The boot image wraps the fixed BootShim, the 3 MiB firmware volume, the trimmed DTB and the payload ramdisk.

### Procedure

- Build the firmware volume, generate the ADT sidecar and pack the p33 boot image.

### Development findings

- The BootShim self-overwrite is fixed by relocating the copy and clean block before loading the firmware volume.

### Completion criteria

- Firmware enters UniXNU, publishes the framebuffer and boots the payload from p33.

### Current limits

- The bootloader does not support fastboot boot. Recovery uses a stock boot image.

### Next action

- Record the firmware revision and the boot image hash for each hardware run.

### Evidence

- `source`: [The device tree reserves the splash region and describes the board.](https://github.com/Dracen-W/UniXNU-merlinx/blob/c6443a068d0fe662fae2e991be1511b06efb7ef3/dts/merlinx.dts)
- `device`: [UniXNU and DarwinBoot start from p33.](https://github.com/Dracen-W/UniXNU-merlinx)
  Command: <code>fastboot flash boot &lt;merlinx-boot.img&gt;</code>. Revision: `237c204655577c1ed1c9536a4bdc890bb2eaf1cc`.

## CPU and interrupts {#cpu}

`implemented`

Components: `ArmCpu`.

### Hardware and dependencies

- MT6768 CPU affinities, GIC and the ARM generic timer.

### Configuration

- merlinx\_defconfig enables ArmCpu, the architectural timer and the native SMP secondary path.

### Procedure

- Build the kernel and inspect the CPU and interrupt initialization path on hardware.

### Development findings

- XNU reaches the scheduler and userland with the native timer entry.

### Completion criteria

- Every enabled CPU enters the scheduler and timer handling works on each CPU.

### Current limits

- GIC affinity and per-CPU interrupt coverage are not fully audited.

### Next action

- Record the per-CPU startup checkpoints and the GIC configuration.

### Evidence

- `source`: [ArmCpu and the architectural timer are selected.](https://github.com/Dracen-W/UniXNU-merlinx/blob/c6443a068d0fe662fae2e991be1511b06efb7ef3/configs/merlinx_defconfig)

## Memory and DMA {#memory}

`implemented`

Components: `ArmDTPlatform`.

### Hardware and dependencies

- 4 GiB DRAM, the owned memory window and the firmware framebuffer reservations.

### Configuration

- The ADT generator receives DRAM size, owned memory size and CPU register values from board.toml.

### Procedure

- Generate the ADT sidecar and boot the kernel with the reserved memory layout.

### Development findings

- The kernel window and owned memory handoff allow XNU entry and root mount.

### Completion criteria

- Every reserved region is described, and the kernel does not overlap firmware or framebuffer memory.

### Current limits

- DMA ownership and SMMU translation are not implemented for this board.

### Next action

- Audit the reserved-memory and DMA windows against the final device tree.

### Evidence

- `source`: [The generator encodes the DRAM and owned-memory values.](https://github.com/Dracen-W/UniXNU-merlinx/blob/c6443a068d0fe662fae2e991be1511b06efb7ef3/scripts/make-merlinx-adt.py)

## Storage and root {#storage}

`device-verified`

Components: `NativeEmmc`, `RamBlock`.

### Hardware and dependencies

- The eMMC userdata partition, the OS and SystemOS APFS volumes and the local Data seed.

### Configuration

- NativeEmmc publishes userdata and the OS and SystemOS volumes. The owner path mounts the SystemOS cache carrier and a packed Data seed.

### Procedure

- Flash the boot image, start XNU and read the ROM/status output.

### Development findings

- NativeEmmc replaces the timed-out UEFI storage path. The kernel mounts SystemOS, executes initproc and reaches launchd, xpcproxy and SpringBoard. The macOS-generated Data seed mounts read-write and disables watchdogd through the launchd disabled plist.

### Completion criteria

- Root and SystemOS mount, initproc runs, Data is writable and the launchd service graph remains alive.

### Current limits

- Data is a bring-up seed. The NativeEmmc manifest backend and UFS persistence are stubbed, so the Data store is volatile and the full user data set is not present.

### Next action

- Verify writable /private/var across reboot, then replace the bring-up stubs and keep watchdogd disabled only for diagnostics.

### Evidence

- `source`: [NativeEmmc, RamBlock and the owner Data path are selected.](https://github.com/Dracen-W/UniXNU-merlinx/blob/c6443a068d0fe662fae2e991be1511b06efb7ef3/configs/merlinx_defconfig)
- `device`: [SystemOS mounts, initproc runs and launchd exec succeeds.](https://github.com/Dracen-W/UniXNU-merlinx)
  Command: <code>fastboot flash boot &lt;merlinx-boot.img&gt;</code>. Revision: `237c204655577c1ed1c9536a4bdc890bb2eaf1cc`.

## Display {#display}

`implemented`

### Hardware and dependencies

- The UEFI GOP framebuffer at 1080x2340 and the panning offset observed on the panel.

### Configuration

- The kernel uses the retained GOP framebuffer for panic and boot-stage text. Userland display ownership is not configured.

### Procedure

- Flash a diagnostic image and read the status lines from the panel.

### Development findings

- The GOP base, row stride and 32-bit format work. The kernel draws ROOT, VOL, CACHE, EXEC, LAUNCHD and Mali diagnostics. Userland reaches SpringBoard, but IOMFB\_FDR\_loader exits with status 1 and no scanout provider is published.

### Completion criteria

- The kernel console is visible and userland presentation and backlight control work.

### Current limits

- No userland display provider or renderer is implemented. IOMFB\_FDR\_loader fails before GPU display handoff. The scanout starts mid-panel.

### Next action

- Trace IOMFB\_FDR\_loader exit 1 and add the userland display and GPU scanout path after the service graph is stable.

### Evidence

- `source`: [The GOP status lines and panic screen are linked into the kernel.](https://github.com/Dracen-W/UniXNU-merlinx/blob/c6443a068d0fe662fae2e991be1511b06efb7ef3/patches/xnu/offline-owner-systemos-mount.patch)

## Input {#input}

`planned`

### Hardware and dependencies

- PMIC keys, volume-up, volume-down and power routing.

### Configuration

- The UEFI menu uses volume-down to scroll and volume-up or power to select. No userland input path is configured.

### Procedure

- Measure key events in the UEFI menu and later in userland.

### Development findings

- The PMIC mask covers power and volume-up, so both keys select a menu entry.

### Completion criteria

- Touch or buttons produce stable HID events in userland.

### Current limits

- No userland touch or HID provider is implemented.

### Next action

- Define the input provider after the userland display path.

### Evidence

Collect evidence using the next action.

## GPU {#gpu}

`implemented`

Components: `MaliG52`, `MaliMetal`.

### Hardware and dependencies

- Mali-G52 r1p0 at 0x13040000, MT6358 VGPU/VSRAM via pwrap WACS2, and the SPM, INFRACFG, topckgen and mfgcfg clock and power windows.
- NativeMali fixed external-method ABI and the MaliMetal MM3 pan\_kmod seam.

### Configuration

- MaliG52 is selected by board.toml and components.toml. The kernel personality matches mediatek,mali. build-mali-g52.py is invoked with --m2-writes --m3-writes --m4-writes --m6-writes so power, reset, MMU and job-write stages are compiled in. The IOKit glue, archive layout and build integration follow the official Adreno740 driver as the reference implementation; the Mali register, power and clock facts remain from MediaTek and panfrost sources. MaliMetal is the userland Metal/PanVK frontend and is not yet selected by the kernel build.

### Procedure

- Build the kernel, build a payload with the Mali diagnostic image, flash it to p33 and read the MALI status lines through the GOP framebuffer.
- For the userland path, build PanVK with the MaliMetal patch series and open the NativeMali service from the MaliMetal bundle.

### Development findings

- The kernel matches the Mali provider and maps all six windows. GICD\_PIDR2 reads 0x3b, proving the physical MMIO path. PMIC PSEQ\_ID reads 0x0800, proving pwrap reads. M2 power/clock/domain setup completes, the M3 GPU reset and M4 MMU initialization run, and the M6 job-write stage is enabled.
- GPU\_ID reads 0x74021000, which masks to product 0x7002 \(Mali-G52\). MALI RC is 0, and the GPU service publishes its device state. No GPU job, completed fence, PanVK device or userland Metal device has run yet.
- MaliMetal contains the host-tested NativeMali client and the MM3 device/sync patch series; the mesa-panvk CI job compiles the seam but the NativeMali IOUserClient is not installed.

### Completion criteria

- M2 completes, GPU\_ID reads 0x70021000 with the expected feature and present masks, and a bounded GPU submission returns a completed fence.

### Current limits

- The kernel path is confirmed through reset and MMU setup, but no job/fence has completed. The NativeMali IOUserClient and service are not installed in the current boot image, so MM4 cannot create a PanVK device on hardware. PanVK's 144 MB JM indirect buffer also exceeds the current 128 MB NativeMali per-BO limit. Userland display remains at IOMFB\_FDR\_loader exit 1.

### Next action

- Build and install the NativeMali IOUserClient, lower or extend the PanVK indirect allocation, cross-build the target PanVK dylib, then run one bounded PanVK job and record its fence.

### Evidence

- `source`: [The IOKit service matches the ADT Mali node, maps the GPU and power windows and exposes the diagnostic stages.](https://github.com/Dracen-W/UniXNU-merlinx/blob/c6443a068d0fe662fae2e991be1511b06efb7ef3/drivers/MaliG52/xnu/NativeMaliGpuService.cpp)
- `source`: [The MaliG52 component pins revision be5ed4437fed98def5b9e392f9fa4da790b341e1 and the M2/M3/M4/M6 build recipe.](https://github.com/Dracen-W/UniXNU-merlinx/blob/c6443a068d0fe662fae2e991be1511b06efb7ef3/components.toml)
- `device`: [MALI RC 0; GPU\_ID 0x74021000; M3 reset, M4 MMU and M6 job-write stages enabled.](https://github.com/Dracen-W/UniXNU-merlinx)
  Command: <code>fastboot flash boot out/merlinx-uefi-emmc-mali-m4m6.img</code>. Revision: `22f479e03dcdf22006415cb22300f509faa75bbf`.
- `host`: [All five jobs passed, including the full mesa-panvk compile of the 0001-0006 patch series.](https://github.com/Dracen-W/MaliMetal/actions/runs/41444900463)
  Command: <code>tests/run.sh; meson setup build-vk ...; ninja -C build-vk src/panfrost/vulkan/libvulkan_panfrost.so</code>. Revision: `df45b652c8d321c4a98d4195c8eb47896c62072d`.

## Network {#network}

`planned`

### Hardware and dependencies

- Wi-Fi and Bluetooth controllers and their firmware.

### Configuration

- No network driver is selected.

### Procedure

- Inventory the wireless hardware and firmware before implementing a driver.

### Development findings

- No network path exists in the current image.

### Completion criteria

- Scanning, association and sustained traffic pass with the selected firmware.

### Current limits

- Network support is outside the current bring-up scope.

### Next action

- Inventory the wireless hardware when userland services are stable.

### Evidence

Collect evidence using the next action.

## Audio {#audio}

`planned`

### Hardware and dependencies

- Audio DSP, codec and speaker routing.

### Configuration

- No audio driver is selected.

### Procedure

- Inventory the audio DSP and codec before implementing a route.

### Development findings

- No audio path exists in the current image.

### Completion criteria

- A declared route carries audio through playback or capture.

### Current limits

- Audio support is outside the current bring-up scope.

### Next action

- Inventory the audio hardware after launchd services are stable.

### Evidence

Collect evidence using the next action.

## Power {#power}

`implemented`

### Hardware and dependencies

- MT6768 PMIC, power keys and the platform power handoff.

### Configuration

- The merlinx platform power archive and the sheng PMGR integration are linked into the kernel.

### Procedure

- Build the platform power archive and boot the kernel from p33.

### Development findings

- The PMIC keys drive the UEFI menu and the kernel reaches launchd with the platform power path linked.

### Completion criteria

- Declared power controls and battery readings match the board and sleep/resume restores peripherals.

### Current limits

- Battery reporting and suspend/resume are not implemented.

### Next action

- Add battery reporting and a suspend/resume path when userland is stable.

### Evidence

- `source`: [The platform power archive is built for the kernel.](https://github.com/Dracen-W/UniXNU-merlinx/blob/c6443a068d0fe662fae2e991be1511b06efb7ef3/scripts/build-merlinx-platform-power.py)

## Image assembly {#packaging}

`implemented`

Components: `DarwinBoot`, `XnuPrelink`.

### Hardware and dependencies

- Kernel, firmware volume, DTB, payload and the packed Data seed.

### Configuration

- board.toml declares the p33 boot size, package defconfig and payload inputs. scripts/package.sh is the fixed release entry point.

### Procedure

- Run scripts/package.sh with the selected OS profile and local inputs, then flash the boot image to p33.

### Development findings

- Kernel and payload builds succeed with the packed Data seed. The validation image carries the seed and boot stages.

### Completion criteria

- The release command writes boot.img, payload.img and kernel.macho with a manifest that verifies.

### Current limits

- The current Data seed uses bring-up stubs and is not a production image. The package release has not replaced the manual build loop.

### Next action

- Run scripts/package.sh --check and record its manifest in this area.

### Evidence

- `source`: [The fixed packaging entry point is present.](https://github.com/Dracen-W/UniXNU-merlinx/blob/c6443a068d0fe662fae2e991be1511b06efb7ef3/scripts/package.sh)

## Diagnostics {#diagnostics}

`device-verified`

### Hardware and dependencies

- Panel output, panic screen and the GOP status lines.

### Configuration

- The kernel draws ROOT, VOL, CACHE, EXEC and LAUNCHD through the GOP framebuffer. The panic screen renders kernel panics on the panel.

### Procedure

- Flash a diagnostic image to p33 and read the panel.

### Development findings

- The status lines identified the cache and launchd checkpoints without a UART. The Mali diagnostics add MATCH, START, RC, M2W, M2P, PMIC, GIC and staged M2 voltage markers. The launchd exit trace showed IOMFB\_FDR\_loader exit 1 while SpringBoard did not exit.

### Completion criteria

- Each claimed milestone has a panel checkpoint or a reproducible panic result.

### Current limits

- There is no UART and no userland log transport. The current Mali image omits the panic screen because the local UEFI font input was unavailable. Data I/O and userland display remain inferred from panel checkpoints.

### Next action

- Add pwrap read sub-markers for the VSRAM path and restore the panic screen in the next CI payload build.

### Evidence

- `source`: [The device page records the panel checkpoints and their limits.](https://github.com/Dracen-W/UniXNU-merlinx/blob/c6443a068d0fe662fae2e991be1511b06efb7ef3/docs/devices/merlinx.md)
- `device`: [The panel shows ROOT, VOL, CACHE, EXEC and LAUNCHD.](https://github.com/Dracen-W/UniXNU-merlinx)
  Command: <code>fastboot flash boot &lt;merlinx-boot.img&gt;</code>. Revision: `237c204655577c1ed1c9536a4bdc890bb2eaf1cc`.

</div>
