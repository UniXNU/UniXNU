# Samsung Galaxy Tab A 10.1 \(2016\) LTE \(SM-T585\)

[ahmedraafat-official/UniXNU-gtaxllte](https://github.com/ahmedraafat-official/UniXNU-gtaxllte)

<div v-pre>

Samsung Galaxy Tab A 10.1 \(2016\) LTE \(SM-T585\). S-Boot loads the UniXNU UEFI, DarwinBoot hands off to the prelinked XNU, NativeDwMmc reads the eMMC and publishes the USERDATA SHNGROOT windows, and the kernel mounts the APFS OS volume and reaches /sbin/launchd. DECON/DSI display, touch and the T830 GPU are the remaining work.

Source record: [porting.toml](https://github.com/ahmedraafat-official/UniXNU-gtaxllte/blob/3100b6a717d4606fafd4a6bd0ccd9d7f5e2f1e73/porting.toml), `3100b6a717d4606fafd4a6bd0ccd9d7f5e2f1e73`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `planned` |
| [Firmware and boot](#firmware) | `device-verified` |
| [CPU and interrupts](#cpu) | `planned` |
| [Memory and DMA](#memory) | `planned` |
| [Storage and root](#storage) | `device-verified` |
| [Display](#display) | `implemented` |
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

- Identify the configuration hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for configuration.

### Procedure

- Follow the configuration stage in the porting guide and record the actual commands.

### Development findings

- The prelinked payload is the working architecture: it is written to HIDDEN \(mmcblk0p21, 60 MiB FAT16, label UNIXNU\) and loaded from EFI/UniXNU/Payloads/kernel.macho because the 49 MiB image cannot fit the 14 MiB ramdisk.
- The prelinked AppleARMPlatform ships an AppleARMCPU personality with IONameMatch cpu; IODTPlatformExpert matches by prefix and would claim the Exynos /cpus. The kernel artifact is rewritten byte-for-byte to xpu before it is written to HIDDEN.
- The prelink roots are trimmed to the software, security and storage closure plus AppleARMPlatform and ApplePMGR; the display, GPU and media kexts wait for Apple hardware and are excluded until the Exynos drivers exist.
- The display bring-up starts by restoring IOMobileGraphicsFamily and IOSurface to the prelink closure and uploading the prelink plan JSON, so the legacy display ABI audit can derive its extents from this board's own candidate.
- The board now carries the measured USERDATA geometry \(first 8013824, last 61057023, 512-byte sectors\) with the OS/SystemOS SHNGROOT windows, the OS volume UUID 04769D26-2CA0-4825-B443-E2E5F88300F2, and the same UUID as the ADT root match. The userdata image build and flash are separate from the kernel build.
- The package workflow takes a userdata boolean: when set it builds the OS/SystemOS root image before the kernel package step and uploads userdata-root.img separately, so the kernel artifact is unaffected by the optional image build.
- The ADT generator dropped \#address-cells/\#size-cells from hardware nodes. That was invisible until the first node with an interrupts property \(dwmmc0\) made IODTMapInterruptsSharing call IODTGetICellCounts on the GIC; the missing cell count faulted in IODeviceTreeAlloc. Patch 0006 adds both properties to the generated ADT.
- The GIC phandle was emitted as phandle, but XNU's IODT support indexes interrupt parents by AAPL,phandle. IODTFindInterruptParent returned NULL and IODTGetICellCounts\(NULL\) faulted. Patch 0007 renames the generated hardware phandle to AAPL,phandle; the value is packed from the FDT's phandle before the output key changes, since the FDT has no AAPL,phandle property to read.
- With the phandle fixed the kernel reached bsd\_init and stayed in its root-mount retry loop with no panic: vfs\_mountroot returned an error that the console cannot show. The diagnostic now paints attempts 283-286 and panics on the third failure with the errno and rootdevice, while the MC window reader marks the first APFS read and any failed window read.
- The first root-probe build failed the bootstrap kernel pass on an implicit gtaxllte\_fb\_mark declaration, which then stopped the corecrypto archive with 'No XNU symbol names'. The probe declares the helper before use; device patches that call a kernel helper must carry their own extern.
- The root-mount probe shows no third-attempt panic after several minutes, so vfs\_mountroot is either succeeding or blocking. The boot now paints 290 after a successful mount, 291 after set\_rootvnode and 292 before load\_init\_program, so the next photo distinguishes a mounted root from a wait.

### Completion criteria

- All source pins resolve; every selected component has a record; status shows the intended overrides and patch order.

### Current limits

- Hardware inputs and implementation are pending for this example board.

### Next action

- Inventory the required configuration inputs before implementation.

### Evidence

Collect evidence using the next action.

## Firmware and boot {#firmware}

`device-verified`

### Hardware and dependencies

- Identify the firmware and boot hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for firmware and boot.

### Procedure

- Follow the firmware and boot stage in the porting guide and record the actual commands.

### Development findings

- S-Boot loads the UniXNU UEFI, the menu entries run, and DarwinBoot reports the prelinked kernel virtual address, entry point and boot args before branching to XNU.
- Early kernel progress is visible through direct framebuffer bars at y=400/500/600/700: green after arm\_vm\_init, red after the console init, blue at PE\_init\_iokit, yellow at bsd\_init. Green, red and blue appear; yellow does not yet.

### Completion criteria

- Firmware image builds, enters UniXNU, publishes the framebuffer and preserves the documented memory reservations.

### Current limits

- The prelinked kernel stops inside IOKit before bsd\_init; storage and display drivers are not built yet.

### Next action

- Name the IOKit sub-phase that stops the prelinked kernel with the traced framebuffer squares.

### Evidence

- `device`: [S-Boot loads the UniXNU UEFI, the menu boots, DarwinBoot hands off to the prelinked kernel, and the early framebuffer bars appear on the panel.](https://github.com/ahmedraafat-official/UniXNU-gtaxllte/blob/3100b6a717d4606fafd4a6bd0ccd9d7f5e2f1e73/PHASE0.md)
  Command: <code>manual boot of the SM-T585; the photos are recorded in the workspace</code>. Revision: `f45b68897f5f48da0026881847d9204680c9dd24`.

## CPU and interrupts {#cpu}

`planned`

### Hardware and dependencies

- Identify the cpu and interrupts hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for cpu and interrupts.

### Procedure

- Follow the cpu and interrupts stage in the porting guide and record the actual commands.

### Development findings

- ArmCpu owns /cpus and the architectural timer; the prelinked AppleARMCPU IONameMatch is rewritten to xpu so it cannot claim the Exynos cores.
- The ADT must describe the GIC cell counts the kernel expects; the missing counts were fixed before the prelinked path became primary.

### Completion criteria

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU.

### Current limits

- Hardware inputs and implementation are pending for this example board.

### Next action

- Inventory the required cpu and interrupts inputs before implementation.

### Evidence

Collect evidence using the next action.

## Memory and DMA {#memory}

`planned`

### Hardware and dependencies

- Identify the memory and dma hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for memory and dma.

### Procedure

- Follow the memory and dma stage in the porting guide and record the actual commands.

### Development findings

- The kernel direct-maps the UEFI framebuffer at 0x67000000 \(1200x1920, 32 bpp, 4800-byte rows\) with ml\_io\_map\_wcomb; the green/red/blue stage bars are direct writes there.
- The prelinked kernel cannot use the corecrypto kernel RNG before the kext providers start, so the kmem size-class randomization and the platform UUID are guarded and crypto-free in the prelinked series.

### Completion criteria

- All handoff regions are accounted for and each enabled DMA engine accesses its allocated range with the documented cache policy.

### Current limits

- Hardware inputs and implementation are pending for this example board.

### Next action

- Inventory the required memory and dma inputs before implementation.

### Evidence

Collect evidence using the next action.

## Storage and root {#storage}

`device-verified`

### Hardware and dependencies

- Identify the storage and root hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for storage and root.

### Procedure

- Follow the storage and root stage in the porting guide and record the actual commands.

### Development findings

- The eMMC is a Samsung MSHC at 0x13540000: VERID 0x6c, RINTSTS 0x44, STATUS 0x48, FIFO 0x100 or 0x200, 32-bit FIFO items, 8-bit bus; Mu-Silicium MshcDxe initializes it and leaves the card selected with 512-byte blocks.
- USERDATA is mmcblk0p23 at LBA 8,013,824 with 53,043,200 sectors; HIDDEN is mmcblk0p21 at LBA 7,880,704 with 122,880 sectors. The read-only bsd\_init probe prints the controller state and reads LBA 0/1 through the PIO FIFO.
- No block driver or root mount exists yet; the first goal is the GPT signature \(EFI PART\) from the probe, then IOBlockStorageDevice publication.
- The same probe is also reachable from arm\_init behind an emmc-probe=1 boot argument, so the eMMC state can be read even while the prelinked kernel still hangs inside IOKit.
- E2 passed on the tablet: with the 64-bit FIFO item width and a DTO check, LBA0 returns mbr=aa55 and LBA1 starts with EFI PART \(20494645 54524150\). The probe is now gated behind bsd-emmc-probe=1 so bsd\_init can continue by default.
- NativeDwMmc is a read-only PIO IOBlockStorageDevice over the USERDATA window. It takes the FIFO item width from HCON, requires DTO, and links through a device build script, a kernel personality in KernelConfigTables.cpp and a build-script archive block. The dwmmc0 node is exported by the SoC DTS.
- The first driver build stopped at -Werror because seven register constants were unused; only the constants the transport actually touches remain. The bootstrap kernel link warning about the mockfs vnodeop descriptor is the expected first-pass link without archives and does not fail the release.
- A source IOBlockStorageDevice cannot link against the native kernel: the class lives in the prelinked IOStorageFamily kext. The device vendors the recorded absolute symbols for the pinned iPadOS 17.7.11 21H461 kernelcache \(f18b4df8..., already -0x1000000 slid\) and re-archives the driver object with them, the same pattern the alioth/marble repositories use.
- NativeDwMmcWindow publishes each SHNGROOT manifest window \(OS, SystemOS\) as its own 512-byte IOBlockStorageDevice, after the parent start returns, so IOStorageFamily can create the IOMedia that APFS probes. The driver checks the manifest SHA-256 and exposes only 512-byte flag-1 windows; framebuffer markers 40-43 report start, first sector, manifest and window service.

### Completion criteria

- Host: register, clock, link and SMMU facts match the board inventory.
- Reads: SCSI capacity, GPT and known blocks are correct; OS/SystemOS windows stay within userdata.
- Root: the configured volume mounts and launchd starts. Persistence: writes survive reboot within the allocated Data region.

### Current limits

- Hardware inputs and implementation are pending for this example board.

### Next action

- Inventory the required storage and root inputs before implementation.

### Evidence

- `device`: [NativeDwMmc publishes the USERDATA SHNGROOT OS/SystemOS windows and XNU mounts the OS volume at the root-matching UUID, reaching load\_init\_program \(markers 290-292\).](https://github.com/ahmedraafat-official/UniXNU-gtaxllte/blob/3100b6a717d4606fafd4a6bd0ccd9d7f5e2f1e73/PHASE0.md)
  Command: <code>manual boot of the SM-T585; photos IMG_7754-IMG_7762 record the MSHC panic and the root-mount markers</code>. Revision: `c2452fb48cf8b4d78b9a810a32f0dd464580de96`.

## Display {#display}

`implemented`

Components: `GopFramebuffer`.

### Hardware and dependencies

- The UEFI GOP hands off 1200x1920, 32 bpp, 4800-byte rows at the physical base; DarwinBoot records v\_display=1.
- The original IOMobileGraphicsFamily and IOSurface are in the prelink closure; the display ABI audit identifies the 358-slot IOMobileFramebufferLegacy class and its nine abstract leaves.

### Configuration

- board.toml \[kernel.prelink\] roots include com.apple.iokit.IOMobileGraphicsFamily and com.apple.iokit.IOSurface; \[components\] includes GopFramebuffer; \[payload\] kernel\_args enable offline-legacy-phase=4, GOP, validation, CPU transfer, retirement, registration and a 60 Hz vsync tick.
- configs/gtaxllte\_defconfig sets CONFIG\_XNU\_NATIVE\_LEGACY\_DISPLAY=y.
- The workflow builds one reference kernel with a bootstrap probe archive, then rebuilds scripts/build-gop-legacy-display.py against that prelink plan and relinks the final kernel.

### Procedure

- Build the display kernel with scripts/package.sh --os 17 --prelink=true; download the prelinked-kernel artifact.
- Flash the kernel and ADT to HIDDEN and replace EFI/UniXNU/unixnu.toml with host/write-unixnu-config.py so the display boot arguments are active.
- Boot and read the bottom-row markers 295-305, then the first frame in the GOP.

### Development findings

- The original IOMobileGraphicsFamily \_\_TEXT\_EXEC base is 0xfffffff00576c000 \(slide -0x1000000\) and its text SHA-256 is 2e044ee68c1650397e1435234ca6459206262e4c7ed709cb7131c6f664f9bd9b, matching the sheng/pipa legacy ABI reference without rebasing.
- The audit passes on this profile's prelinked candidate: 358 vtable slots, nine abstract leaves and the exact original surface, vsync and refresh-setter bytes.
- The backend uses the firmware GOP with QuartzCore's CPU renderer: NativeLegacyDisplay copies each validated full-frame BGRA/RGBA16F surface into the scanout mapping and retires it through the original completion body.
- The pinned GopFramebuffer e47c1b8 source is vendored because the workflow's UniXNU submodule is b0d812d, whose ioav/hotplug calls this board does not implement.
- The GPU trace, UFS DPU and Adreno fence symbols are stubbed because the T830 has no driver; the probe markers 295-305 report the display lifecycle on the framebuffer.

### Completion criteria

- A known frame appears with correct geometry and colors, then userland presentation and backlight controls work.

### Current limits

- Only the UEFI GOP is used: DECON/DSI, panel power, backlight and touch are not programmed by XNU. The render server draws with the CPU; the T830 GPU is a separate port.
- The static trust cache, SystemOS union and Data volume are not configured yet.

### Next action

- Boot the display kernel and confirm markers 295-305 and the first GOP frame; then add touch and the T830 GPU.

### Evidence

- `host`: [The legacy display ABI audit and every hardcoded family, surface, vsync and refresh byte check pass on this profile's prelinked candidate.](https://github.com/ahmedraafat-official/UniXNU-gtaxllte/blob/3100b6a717d4606fafd4a6bd0ccd9d7f5e2f1e73/docs/display-plan.md)
  Command: <code>python3.12 scripts/audit-mobile-graphics-legacy.py in the audit tree; the same checks are run by scripts/build-gop-legacy-display.py</code>. Revision: `006b531f56f2a6abd1691289a5ee0c22595836aa`.

## Input {#input}

`planned`

### Hardware and dependencies

- Identify the input hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for input.

### Procedure

- Follow the input stage in the porting guide and record the actual commands.

### Development findings

- Collect the first input observation, its cause when established, and the resulting implementation decision.

### Completion criteria

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive, and buttons produce expected HID reports.

### Current limits

- Hardware inputs and implementation are pending for this example board.

### Next action

- Inventory the required input inputs before implementation.

### Evidence

Collect evidence using the next action.

## GPU {#gpu}

`planned`

### Hardware and dependencies

- Identify the gpu hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for gpu.

### Procedure

- Follow the gpu stage in the porting guide and record the actual commands.

### Development findings

- The Mali-T830 is Midgard v5 with a Job Manager; Mesa PanVK has no arch 5 backend, so the GPU needs a new PanVK backend and a NativeMali JM driver.
- The GPU plan lives in a separate repository; no GPU code or hardware access runs in this image yet.

### Completion criteria

- GPU submissions complete, mapping/fence handling is correct, a known image renders, and the selected Metal client presents it.

### Current limits

- Hardware inputs and implementation are pending for this example board.

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

- Hardware inputs and implementation are pending for this example board.

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

- Hardware inputs and implementation are pending for this example board.

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

- Hardware inputs and implementation are pending for this example board.

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

- The prelink build overrides the device patch series: native-only workarounds are excluded, while the early framebuffer bars, the NULL-safe kmem wrapper, the crypto-free platform UUID, the read-only eMMC probe and the IOKit trace squares stay in.
- The package step always fails at strip on the 49 MiB prelinked Mach-O; the prelinked-kernel artifact is uploaded with if: always\(\) and is the image written to HIDDEN.
- The payload step patches a copy of the prelinked kernel with the entry bars and the framebuffer panic screen before strip fails; that stage copy is uploaded with the raw kernel and is preferred when staging, because it renders panic arguments on the panel without a serial console.
- The prelink series now also carries the boot-phase trace squares \(startup/bootstrap\) and the boot-argument-gated early eMMC probe, so one image answers both the IOKit hang and the storage question.
- The prelink artifact upload now includes the stage kernel \(panic screen\), the stage ADT, and the driver archive path; the device build script compiles NativeDwMmc against the kernel compile record and the 0004 patch links it with the NativeDwMmc personality.
- The payload builder now generates the ADT sidecar before the strip step, so a failed prelinked package still yields a fresh kernel.macho.adt next to the patched kernel; staging the ADT is opt-in until it is compared with the working one.
- Device XNU patches are generated against the post-arch-series source, not the pristine XNU tree: offline-component-load-probes.patch inserts its probes between the bsd\_init comment and the function, so a context built from the pristine file no longer applies.
- The boot-phase squares showed the prelinked kernel completing PE\_lockdown\_iokit and then stopping before bsd\_init. The only blocking call between them is kperf\_init\_early\(\)-&gt;ml\_wait\_max\_cpus\(\); the native ArmCpu path does not call ml\_set\_max\_cpus\(\) on this board, so the boot now marks the maximum CPU count set explicitly before the VM restrictions and kperf.
- The first eMMC read completed with zero data: HCON\[9:7\]=2 means a 64-bit FIFO, and the probe consumed one 32-bit word per FIFO item. The probes now take the item width from HCON, read both words per item, and require RINTSTS DTO before reporting success.

### Completion criteria

- Kernel and prelink succeed, payload contains all declared inputs, and the boot image matches the bootloader format and size limit.

### Current limits

- Hardware inputs and implementation are pending for this example board.

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

- The direct framebuffer bars are the primary early-boot diagnostic because the Apple console/panic path waits for hardware and can stay dark.
- The prelinked kernel reaches PE\_init\_iokit \(blue\); the IOKit trace squares now mark IOLibInit, OSlibkernInit, IOMachPortInitialize, the root nub and ConfigureIOKit to name the next stop.

### Completion criteria

- Each claimed milestone has a reproducible command, a matching source/image revision and an accessible result.

### Current limits

- Hardware inputs and implementation are pending for this example board.

### Next action

- Inventory the required diagnostics inputs before implementation.

### Evidence

Collect evidence using the next action.

</div>
