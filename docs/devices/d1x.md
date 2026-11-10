# Samsung Galaxy Note10 5G \(SM-N971N, d1x, Exynos 9825\), 12 GB / 256 GB

[KosugiYukina/UniXNU-d1x](https://github.com/KosugiYukina/UniXNU-d1x)

<div v-pre>

Samsung Galaxy Note10 5G \(SM-N971N, Exynos 9825\) boots the iPadOS 17.7.11 userland from a recovery image: UEFI, prelinked XNU, UFS and APFS root and framebuffer scanout work. SpringBoard still exits on every launch because the legacy IOMobileFramebuffer client never serves selectors 3, 4, 5 and 6, so CoreAnimation has no surface to present. Input, GPU, Wi-Fi, audio and power management are not implemented.

Source record: [porting.toml](https://github.com/KosugiYukina/UniXNU-d1x/blob/6e2aca1cafaa416704d79a2460a99c0059ce0127/porting.toml), `6e2aca1cafaa416704d79a2460a99c0059ce0127`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `implemented` |
| [Firmware and boot](#firmware) | `implemented` |
| [CPU and interrupts](#cpu) | `implemented` |
| [Memory and DMA](#memory) | `implemented` |
| [Storage and root](#storage) | `implemented` |
| [Display](#display) | `implemented` |
| [Input](#input) | `planned` |
| [GPU](#gpu) | `planned` |
| [Network](#network) | `planned` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `planned` |
| [Image assembly](#packaging) | `implemented` |
| [Diagnostics](#diagnostics) | `implemented` |

## Configuration {#configuration}

`implemented`

Components: `ArmDTPlatform`, `XnuPrelink`.

### Hardware and dependencies

- SM-N971N \(d1x\) with Exynos 9825, 12 GB RAM and 256 GB UFS; bootloader N971NKSU2HWH5, hardware revision 23.
- iPadOS 17.7.11 build 21H461 \(iPad7,1 / J120AP\), kernelcache sha256 f18b4df865405f2a287b84977d7aca745e056d656d9fc9df1662970ce2969de7, XNU revision d8b80295118ef25ac3a784134bcf95cd8e88109f.
- Live device tree, GPT and boot arguments captured on 2026-11-01 while Android was rooted. The ro.product properties are spoofed and were not used.

### Configuration

- schema\_version 2: board.name d1x, board.soc exynos9825, board.os\_profile ipados-17.7.11-21H461, board.kit d1x.
- Selected components: ArmDTPlatform, ArmCpu, SoftwareAES, DarwinBoot and XnuPrelink. The board-owned D1xDisk and D1xFramebuffer drivers are kernel archives, not catalog components.
- kernel.defconfig d1x\_defconfig with arch, SoC and OS configuration fragments and the arch, SoC, OS and device patch series.
- payload volume D1XESP of 52 MiB, boot image header v2 with a 376 KiB one-entry dt\_table, ADT chip\_id 971, dram\_size 0x80000000 and defaults vmm-present=1.

### Procedure

- Run ./unixnu defconfig d1x\_defconfig -D ../UniXNU-d1x and ./unixnu status --json -D ../UniXNU-d1x from UniXNU; inspect the resolved profile, components, source pins and patch order.
- Build the kernel and payload with the bring-up scripts, flash the recovery image, boot for 300 s and pull the kernel console log.

### Development findings

- The device identifies itself through /proc/device-tree and the GPT. ro.product.model reports SM-S9280 and b0s; those values are spoofed and contradict the Exynos 9825 device tree.
- The GPT uses 4096-byte logical blocks. boot is sda14 \(55 MiB, LBA 27264-41343\) and recovery is sda15; userdata spans LBA 3313152-62476282.
- The boot image must carry a dt\_table. A header v1 image without a device tree fails with \[DTH\] dt table header check fail; pasting the vendor dt\_table after the ramdisk then fails with DT Load Fail. Header v2 with the live 376 KiB FDT wrapped in a one-entry dt\_table boots.
- 12 GB of DRAM is not contiguous: about 2 GiB sits below 4 GiB and 10 GiB sits above 32 GiB. The ADT accepts one contiguous range, so only the low window is declared.
- The kernel declares max\_cpus 4 even though the device tree publishes cpu0 through cpu7.
- profiles.py replaces arrays instead of merging them, so the board archives list restates the arm64 profile entries and then appends the D1x storage and display archives.
- A defconfig that contains both CONFIG\_X=y and a later \# CONFIG\_X is not set keeps the later line; duplicate blocks silently disabled the native display build once.
- The prelink roots keep com.apple.iokit.IOMobileGraphicsFamily and com.apple.iokit.IOSurface. Removing either shifts the prelinked layout and panics in IOKitInitializeTime before bsd\_init completes.

### Completion criteria

- unixnu status resolves the device, SoC and OS profile with no missing input.
- The built image reaches launchd, reports Darwin 23.6.0 and runs 64 processes for the full 300 s window.

### Current limits

- The v28 working tree still lists two board archives by absolute /opt/unixnu/UniXNU-d1x path; they must become repository-relative before publication.
- The SoC repository is not pinned to a reviewed commit and feeds.toml is still a placeholder.
- Only the low 2 GiB DRAM window is described; the 10 GiB above 32 GiB is unused.

### Next action

- Pin exynos9825 to a reviewed commit and make the archive paths repository-relative before the next release.

### Evidence

- `source`: [Board identity, DRAM window, payload inputs and boot arguments used for the v28 build.](https://github.com/KosugiYukina/UniXNU-d1x/blob/6e2aca1cafaa416704d79a2460a99c0059ce0127/reports/v28-state.json)
- `source`: [Kernel console capture of the v198 boot: 300 s alive, 64 processes, Darwin 23.6.0.](https://github.com/KosugiYukina/UniXNU-d1x/blob/6e2aca1cafaa416704d79a2460a99c0059ce0127/reports/v28-boot.log)

## Firmware and boot {#firmware}

`implemented`

Components: `DarwinBoot`.

### Hardware and dependencies

- Samsung LK bootloader with Odin download mode and no fastboot; only the recovery partition is used for bring-up.
- 55 MiB boot partition, 376 KiB live FDT, GOP framebuffer at 0xCA000000 and PSCI over SMC.
- Mu-Silicium Samsung platform seed; the d1xPkg DSC is built from the unixnu-d1x branch.

### Configuration

- firmware.dsc Platforms/Samsung/d1xPkg/d1x.dsc and firmware.fd Build/d1xPkg/&\#123;target&\#125;\_CLANGPDB/FV/SILICIUM\_UEFI.fd; ENABLE\_SECUREBOOT=0 during bring-up.
- bootimg.image header\_version 2, base 0, kernel\_offset 0x10008000, tags\_offset 0x10000100, ramdisk\_offset 0, pagesize 0x800; bootimg.dtb package/d1x/dt\_table.bin.
- BootShim paints 0xCA000000 with 0x964000 bytes of red before entering the firmware volume, as a loader heartbeat.

### Procedure

- Build the firmware volume, wrap BootShim, the FD and the FAT payload into the recovery image, flash recovery over adb and reboot to Android.
- Capture the serial console for the full 300 s test window and confirm the kernel checkpoints before the next change.

### Development findings

- The Samsung bootloader refuses a recovery image without a dt\_table and also refuses the raw vendor table appended after the ramdisk. The working shape is header v2 plus a dtb section holding a one-entry dt\_table with the full live FDT.
- A red screen after flashing proves LK entered BootShim and the Decon still scans 0xCA000000. A screen that never changes means LK rejected the image or the framebuffer is no longer scanned.
- The menu is configured with timeout 0 so the firmware boots without a working UEFI timer or key input; this is required for unattended 300 s tests.
- The payload volume is limited to 52 MiB because BootShim plus the firmware volume take about 2.1 MiB of the 55 MiB boot partition.

### Completion criteria

- The flashed recovery image loads through LK, prints kernel checkpoints C0-C25 and reaches launchd without a panic.
- The boot returns to Android after the 300 s test window.

### Current limits

- The firmware is built from a local Mu-Silicium branch that is not published as uefi-d1x.
- Bring-up uses recovery only; nothing installs to the boot partition and no Odin tar is produced.
- There is no interactive menu or fastboot path.

### Next action

- Publish the uefi-d1x branch and pin it in feeds.toml, then add Odin tar packaging and verify a cold boot from the boot partition.

### Evidence

- `source`: [Boot image shape, payload size and the v198 and v200 artifact hashes.](https://github.com/KosugiYukina/UniXNU-d1x/blob/6e2aca1cafaa416704d79a2460a99c0059ce0127/reports/v28-manifest.md)
- `source`: [Console capture proving the loader handoff reached the kernel and userspace.](https://github.com/KosugiYukina/UniXNU-d1x/blob/6e2aca1cafaa416704d79a2460a99c0059ce0127/reports/v28-boot.log)

## CPU and interrupts {#cpu}

`implemented`

Components: `ArmCpu`.

### Hardware and dependencies

- Eight cores: four Cortex-A55, two Cortex-A75 and two Exynos M4; MPIDR affinities 0x0-0x3, 0x4-0x5 and 0x100-0x101.
- GIC-400 \(GICv2\): distributor 0x10101000, CPU interface 0x10102000, virtual interface 0x10106000; 26 MHz timebase.

### Configuration

- CONFIG\_XNU\_ARMCPU=y; ADT cpu\_regs 0x0,0x1,0x2,0x3,0x4,0x5,0x100,0x101; PSCI method smc.
- Device tree cpu nodes and the arm,armv8-timer block feed the ADT and the platform expert.

### Procedure

- Boot and inspect the C6 topology, C11 timer and C19 timebase checkpoints.
- Read the GIC distributor, CPU interface and timer lines, then dump the IORegistry cpu nodes.

### Development findings

- GICv2 works on this kernel: the distributor reports type 0x0000fcef and IIDR 0x0200143b, and the timer arrives as PPI 27 in group 0 at 26 MHz.
- pe\_arm\_map\_interrupt\_controller reports that it cannot find the interrupt controller before the GIC is programmed, yet the later gicd and gicc reads are valid. The message comes from the early mapping path and does not stop timer delivery.
- The kernel declares max\_cpus 4 in C23 and C24 while the device tree publishes eight cpu nodes; cores above the declared limit are not brought up by this image.
- No inter-processor interrupt or per-core entry test has been recorded yet.

### Completion criteria

- The declared CPUs reach their entry point, the timer fires and launchd runs.

### Current limits

- Only four CPUs are declared; SMP bring-up of all eight cores and IPI delivery remain unverified.
- CPU frequency and DVFS are owned by ACPM and are not implemented.

### Next action

- Raise max\_cpus after adding a per-core entry check, then add an IPI test and record each core's MPIDR.

### Evidence

- `source`: [GIC, timer, max\_cpus and IORegistry cpu lines from the v198 boot.](https://github.com/KosugiYukina/UniXNU-d1x/blob/6e2aca1cafaa416704d79a2460a99c0059ce0127/reports/v28-boot.log)

## Memory and DMA {#memory}

`implemented`

### Hardware and dependencies

- 12 GB physical DRAM in eight live device-tree nodes: three below 4 GiB and five 2 GiB nodes starting at 0x880000000.
- UEFI memory map, GOP framebuffer reservation at 0xCA000000 and the payload initrd.

### Configuration

- The ADT receives dram\_size 0x80000000, one contiguous range from 0x80000000 to 0xFFFFFFFF.
- dts/d1x.dts declares the same low window as its single /memory node.

### Procedure

- Compare the base DTB with /proc/device-tree on Android to confirm that the bootloader rewrites the memory nodes.
- Boot the kernel and read the vm\_page\_bootstrap counters and the pmap startup lines.

### Development findings

- The bootloader exposes eight memory nodes, not the three in the base DTB. Ten of the twelve GiB sit above 32 GiB and cannot be described by the single ADT range.
- vm\_page\_bootstrap reports 48062 free pages and 17474 wired pages; with 16 KiB pages that is 65536 pages, about 1 GiB accounted at bootstrap inside the declared 2 GiB window.
- The rest of the low window is absent from the bootstrap free and wired counts. Firmware, the framebuffer, the payload and reserved regions account for part of it, but no complete map audit exists yet.

### Completion criteria

- The kernel accounts its memory, maps the framebuffer and runs launchd plus 64 processes without a memory panic.

### Current limits

- The 10 GiB above 32 GiB is unused and untested. DMA address widths and SMMU ownership are not described.

### Next action

- Export the UEFI memory map, add the high range as a second owned-memory region and verify that XNU can allocate above 32 GiB.

### Evidence

- `source`: [vm\_page\_bootstrap, pmap startup and process count lines.](https://github.com/KosugiYukina/UniXNU-d1x/blob/6e2aca1cafaa416704d79a2460a99c0059ce0127/reports/v28-boot.log)
- `source`: [Declared DRAM range, memory split and payload inputs.](https://github.com/KosugiYukina/UniXNU-d1x/blob/6e2aca1cafaa416704d79a2460a99c0059ce0127/reports/v28-state.json)

## Storage and root {#storage}

`implemented`

Components: `SoftwareAES`.

### Hardware and dependencies

- Samsung Exynos UFS at 0x13D60000, HS-GEAR4 with two lanes, LUN0 of 238 GiB and 4096-byte logical blocks.
- GPT with 37 entries; the OS, SystemOS, OwnerData, VAR and LOG windows are carved from userdata.

### Configuration

- CONFIG\_XNU\_EXTRA\_LD\_ARCHIVES force-loads libD1xStorage.a; D1xDisk publishes one IOBlockStorageDevice per window over the prelinked IOStorageFamily.
- SoftwareAES provides software AES-CBC through the kernel AES helpers and the IOAESAccelerator ABI; it is linked from the arm64 profile.
- Boot arguments rd=md0, d1x-ufs-probe=1, d1x-ufs-enable=1, d1x-ufs-uic=1, d1x-ufs-utp=1, offline-apfs-load=1, d1x-var-apfs=1 and d1x-log-apfs=1.
- userdata window first\_lba 3313152, last\_lba 62476282, lba\_bytes 4096.

### Procedure

- Boot and inspect the UFS capability, HCS and UniPro lines, then the D1xDisk publish sequence and the APFS media tree.
- Confirm the OS volume mounts at /apfs/mnt9, the VAR seed mounts at /apfs/mnt9/private/var and launchd starts from the APFS root.

### Development findings

- The UFS controller reports CAP 0x01303ff1f, version 0x300, HCS 0x10f and a ready UniPro link; UIC and UTP commands complete.
- Five APFS windows publish: disk1s1 OwnerData \(184 MiB of a 512 MiB window\), disk3s1 SystemOS \(3.3 GB\), disk5s1 OS \(6.08 GB\), disk7s1 VAR \(32 MiB\) and a 224 MiB LOG window with no volume slice.
- The OS window mounts read-only at /apfs/mnt9 and becomes the root, replacing the ext2 skeleton that vfs\_mountroot initially mounts from UFS. The 32 MiB VAR seed mounts read-write at /apfs/mnt9/private/var.
- The 32 MiB VAR seed is 93.8 percent non-zero and full; launchd logs could not set create /private/var/mobile/tmp: No space left on device.
- The 224 MiB LOG container publishes an IOMedia but no APFS volume. mount /dev/disk9 returns ENOENT, so the container from apfsprogs is not recognised as a container with a volume.

### Completion criteria

- GPT and APFS containers read correctly, the OS volume mounts, launchd runs and the 300 s test completes.

### Current limits

- The OS volume is read-only and the VAR volume is only 32 MiB; persistent writes larger than the seed fail.
- The LOG container is unusable and there is no Data volume resize or fsck.

### Next action

- Repair or replace the LOG container with a container that Apple APFS accepts, then grow VAR or add a Data volume and measure read throughput.

### Evidence

- `source`: [UFS, D1xDisk, APFS mount and out-of-space lines.](https://github.com/KosugiYukina/UniXNU-d1x/blob/6e2aca1cafaa416704d79a2460a99c0059ce0127/reports/v28-boot.log)
- `source`: [Storage windows, userdata geometry and storage-related boot arguments.](https://github.com/KosugiYukina/UniXNU-d1x/blob/6e2aca1cafaa416704d79a2460a99c0059ce0127/reports/v28-state.json)

## Display {#display}

`implemented`

### Hardware and dependencies

- Samsung S6E3HA9 panel, 1080x2280 at 60 Hz, 4320-byte stride; firmware GOP framebuffer at 0xCA000000.
- Prelinked IOMobileGraphicsFamily and IOSurface kexts; iPadOS 17.7.11 IOMobileFramebuffer.framework.

### Configuration

- CONFIG\_XNU\_NATIVE\_LEGACY\_DISPLAY=y force-loads libNativeLegacyDisplay.late.a, which publishes D1xFirmwareFramebuffer and NativeLegacyDisplay under /arm-io.
- Boot arguments offline-legacy-gop=1, phase=4, unit-scale=3, sheng-vsync=60, offline-legacy-pm=1, validate=1, transfer=1, retire=1 and d1x-fb-bars=1.
- d1x-backlight impersonates AppleARMBacklight and registers a 1024-level range; it does not program the panel backlight yet.

### Procedure

- Boot and confirm the console framebuffer and the paint tick lines, then inspect D1xFirmwareFramebuffer and NativeLegacyDisplay in the IORegistry.
- Disassemble IOMobileFramebuffer.framework from the 17.7.11 dyld cache, enumerate the user-client selector calls and compare them with the legacy client trace.

### Development findings

- Scanout works: the console reports fb ca000000 1080x2280 row 4320, the paint tick redraws the bars and the panel stays quiet after 20 s.
- Seven processes open the legacy user client: backboardd \(37\), 64, 80, 105, 142, 178 and 198. They interpose the vtable but the v198 log records no selector trace, so selector logging must be restored before judging traffic.
- The last complete client trace, from v193, was 88, 57, 15, 22, 8, 29, 33, 79, 74, 12, 6, 27, 84, 50 and 28: capability and status calls only, never 3, 4, 5 or 6.
- The 17.7.11 framework calls selector 3 for the layer default surface \(one 32-bit output\), 4 for swap begin \(one 64-bit id\), 5 for swap with a 0x508-byte structure, 6 for swap wait and 8 for display size. iOS 16 used 0x46c bytes for selector 5.
- Adding canvas-width, canvas-height, canvas-depth and canvas-rowbytes to the nub in v195 made every client stop issuing selectors; v198 removed the properties, but the captured log still shows no selector traffic, so the probe state must be re-established before the next test.
- The sweet display classes cannot coexist with the prelinked kexts: IOSurfaceRootUserClient, AppleCLCD and IOMobileFramebuffer already exist, and removing the two kexts panics in IOKitInitializeTime with the class-name string in FAR 0x755365726f434f49, the ASCII bytes of IOCoreSu.
- v200 implements selectors 3, 4, 5 and 6 in the legacy client: 3 returns 0 with a log line, 4 increments a swap id, 5 accepts at least 0x508 bytes, logs the mask and layer ids and paints the panel solid, and 6 returns success. The image is built but was never flashed because adb had no device.

### Completion criteria

- Stage 1: colour bars and a stable panel, achieved.
- Stage 2: the framework issues 3, 4 and 5 and the panel leaves the bars.
- Stage 3: SpringBoard draws the first UI frame.

### Current limits

- No surface object is wired to selector 3 yet; v200 returns 0 and paints a solid colour instead of copying layers.
- The text console is not disabled on the first swap, there is no presenter thread, no screen surface reserve and no vsync source.
- The backlight service is a stub.

### Next action

- Flash v200 and look for sel5 swap mask in the console. If selector 3 is never called, restore the pre-v195 probing state and check selectors 18, 28 and 72; once swap arrives, port SweetSurface as D1xSurfaceRoot and D1xSurfaceUserClient, copy layers with CPU memcpy, disable the text console and add the presenter thread.

### Evidence

- `source`: [GOP, paint tick, user-client and IORegistry display lines.](https://github.com/KosugiYukina/UniXNU-d1x/blob/6e2aca1cafaa416704d79a2460a99c0059ce0127/reports/v28-boot.log)
- `source`: [v198 and v200 kernel and image hashes.](https://github.com/KosugiYukina/UniXNU-d1x/blob/6e2aca1cafaa416704d79a2460a99c0059ce0127/reports/v28-manifest.md)

## Input {#input}

`planned`

### Hardware and dependencies

- Samsung sec\_ts touch controller on HSI2C 0x104B0000 \(i2c-4\) at address 0x48; S Pen on i2c-9 at 0x56.
- Three input devices reported by the vendor kernel: sec\_touchscreen, sec\_touchpad and sec\_touchproximity; volume and power keys are wired to the PMIC.

### Configuration

- No kernel configuration. The device tree carries the nodes but no HSI2C controller or sec\_ts driver is selected.

### Procedure

- Extract the sec\_ts initialisation and ioctl sequences from the vendor kernel, then implement the HSI2C controller and the touch driver.
- Bind the touch and key devices to IOHIDFamily and verify coordinates in SpringBoard.

### Development findings

- HSI2C is a Samsung controller, not a Qualcomm GENI block; no existing UniXNU component matches it.
- sec\_ts uses a private protocol and the component catalog has no implementation. The sm-t733 FocalTech path is not reusable.
- No touch, key or S Pen event reaches userspace in the v28 log.

### Completion criteria

- Touch coordinates and key events reach SpringBoard and the UI responds.

### Current limits

- The touch protocol is undocumented; the HSI2C driver and the panel power sequence are missing.

### Next action

- Dump the sec\_ts firmware and init sequence from the vendor kernel and add an HSI2C node plus a minimal probe.

### Evidence

- `source`: [Hardware inventory for the touch and S Pen buses.](https://github.com/KosugiYukina/UniXNU-d1x/blob/6e2aca1cafaa416704d79a2460a99c0059ce0127/reports/v28-state.json)

## GPU {#gpu}

`planned`

### Hardware and dependencies

- ARM Mali-G76 MP12 integrated GPU; no GPU firmware, power domain or SMMU setup.
- CoreAnimation on iPadOS 17.7.11 still contains the OpenGL ES renderer and the software renderer path.

### Configuration

- No GPU configuration. Boot arguments still publish d1x-metal=1 accelerator services from the v183-v188 experiments.

### Procedure

- Review the six plugin-model boots, then choose between an EAGL and OSMesa CPU renderer and a native Mali driver.
- Build the chosen renderer, inject it into backboardd and SpringBoard and check which CoreAnimation renderer is selected.

### Development findings

- iOS 17.7 ignores IOAcceleratorES and AGXAccelerator services that carry MetalPluginName and MetalPluginClassName. Six boots from v183 to v188 falsified that model: backboardd opens AGXAccelerator and closes it immediately, Metal never matches and the plugin bundle is never loaded.
- The accelerator services still appear in the v198 IORegistry dump, but no client uses them.
- QuartzCore still carries CA::OGL::GLESImage, CAEAGLLayer, the OpenGLES framework path and CA\_ENABLE\_OGL, plus the CoreAnimation software renderer string. The EAGL to OSMesa route used by Scion on iOS 16.5 therefore has evidence on 17.7 but has not been built.
- ios-topaz proves that a CPU-only renderer can drive the full iOS 16 UI, but its display classes collide with the prelinked kexts.

### Completion criteria

- A CoreAnimation renderer exists and SpringBoard draws its first frame.

### Current limits

- No GPU power, firmware or SMMU support; no Mesa, OSMesa or EAGL library for this OS build.

### Next action

- Build Mesa softpipe and libhakios.gl for iOS 17.7, inject them at exec time and record the renderer line; keep the sweet CPU compositor as the fallback.

### Evidence

- `source`: [IORegistry dump with IOAcceleratorES and AGXAccelerator.](https://github.com/KosugiYukina/UniXNU-d1x/blob/6e2aca1cafaa416704d79a2460a99c0059ce0127/reports/v28-boot.log)
- `source`: [Falsified Metal plugin route and renderer notes.](https://github.com/KosugiYukina/UniXNU-d1x/blob/6e2aca1cafaa416704d79a2460a99c0059ce0127/reports/v28-state.json)

## Network {#network}

`planned`

### Hardware and dependencies

- Broadcom BCM4375 Wi-Fi and Bluetooth combo; the vendor kernel uses bcmdhd and the firmware file bcmdhd\_sta.bin.
- Bus, power rails and firmware load sequence are not yet documented.

### Configuration

- No configuration. The device tree has no enabled network node and no driver is selected.

### Procedure

- Identify the host bus and firmware path from the vendor device tree and bcmdhd probe log.
- Evaluate brcmfmac or a board port of bcmdhd, then bind the interface to the OS network stack.

### Development findings

- The existing UniXNU wireless component is ath12k for Qualcomm parts and does not apply.
- No Wi-Fi or Bluetooth driver loads in the v28 boot; launchd fails to bootstrap wifid and CoreWifi lookups fail, so no network stack attaches.

### Completion criteria

- The interface scans, associates and passes traffic.

### Current limits

- The bus, firmware interface and power sequence are unknown.

### Next action

- Read the vendor device tree and bcmdhd probe log to identify the bus and firmware, then pick brcmfmac or bcmdhd.

### Evidence

- `source`: [Network hardware inventory.](https://github.com/KosugiYukina/UniXNU-d1x/blob/6e2aca1cafaa416704d79a2460a99c0059ce0127/reports/v28-state.json)

## Audio {#audio}

`planned`

### Hardware and dependencies

- Exynos 9825 audio subsystem with an external codec; the codec part number and I2C address are not yet recorded.
- Speaker, earpiece, headset and microphone routing; no DSP firmware.

### Configuration

- No configuration and no audio driver.

### Procedure

- Identify the codec from the vendor device tree and schematics, then document clocks, I2S and DSI routes and power.
- Implement playback and capture and expose the routes to the OS audio server.

### Development findings

- audiomxd starts, but no codec or DSP driver exists, so no audio route is usable.
- The ADT carries the iPad product audio identity, so the userland audio server initialises as it would on the reference device.

### Completion criteria

- Playback and recording work through the speaker, headset and microphone.

### Current limits

- Codec, DSP and routing are unidentified.

### Next action

- Identify the codec and its bus from the vendor device tree and add the minimum playback route.

### Evidence

- `source`: [audiomxd spawn and CoreAudio lines.](https://github.com/KosugiYukina/UniXNU-d1x/blob/6e2aca1cafaa416704d79a2460a99c0059ce0127/reports/v28-boot.log)

## Power {#power}

`planned`

### Hardware and dependencies

- ACPM coprocessor owns DVFS and clock policy; PMIC identity is encoded as pmic\_info=43 in the boot arguments and is not decoded.
- Battery, charger, fuel gauge and thermal sensors are not described.

### Configuration

- No regulator, clock or PMIC driver. The ADT declares vmm-present=1 so AMFI does not wait for a PMGR that this board does not have.
- d1x-backlight publishes an AppleARMBacklight service with a 1024-level range as a stub.

### Procedure

- Decode pmic\_info, locate the PMIC and charger on their buses and document the regulator tree.
- Implement CPU frequency scaling through ACPM and expose battery and thermal state.

### Development findings

- The ACPM firmware interface is undocumented; mainline exynos-acpm is the closest reference.
- thermalmonitord, powerd and PerfPowerServices start but receive no real sensor or PMGR data.
- The backlight stub satisfies clients that look for AppleARMBacklight but does not drive the panel backlight.

### Completion criteria

- CPU frequency scales, battery state is reported and thermal limits are enforced.

### Current limits

- No PMIC, regulator, charger or ACPM implementation.

### Next action

- Decode pmic\_info=43 and the ACPM mailbox from the vendor kernel, then add the regulator tree to the device tree.

### Evidence

- `source`: [Power service and backlight lines.](https://github.com/KosugiYukina/UniXNU-d1x/blob/6e2aca1cafaa416704d79a2460a99c0059ce0127/reports/v28-boot.log)

## Image assembly {#packaging}

`implemented`

### Hardware and dependencies

- Odin-only bootloader; recovery partition used for bring-up; 55 MiB boot partition.
- BootShim, UEFI firmware volume and a 52 MiB FAT payload.

### Configuration

- Recovery image: 2 KiB boot header, BootShim plus firmware volume, then the FAT payload; header v2 and a 376 KiB dt\_table.
- Payload volume D1XESP, title Boot UniXNU, timeout 0 and the v28 kernel arguments.

### Procedure

- Build the kernel, firmware and payload, assemble the recovery image, flash it over adb and boot for 300 s.
- Record the kernel and image SHA-256 for every flashed build.

### Development findings

- BootShim plus the firmware volume take about 2.1 MiB, leaving 52 MiB for the FAT payload inside the 55 MiB boot partition.
- A recovery image without a dt\_table is rejected before the kernel runs; header v2 with the live FDT is the only shape that has booted.
- There is no fastboot path. Flashing happens from Android over adb, and the device is powered off after the flash so the operator presses power once.
- v198 image 3a8614b223caed6fd7adc3a8867103261c66b8531261d031e2caa2bdbcf1679d with kernel ca6282f331cd82ac3a2153a1c07f095fb2b04e7a73c2c3aaa4fad02dd36fee22 boots. v200 image 4c86450faa475972ea7eabead2ebeee0f55ff08e3084a73ada7ef00155d421c1 with kernel c3332383d31e6f381bbace5310a4f92970fdf6b46e622b41c2b29cb532695325 is built but not flashed.

### Completion criteria

- The assembled image flashes, boots to userspace and passes the 300 s test.

### Current limits

- No Odin tar, no boot partition install and no automated image verification in CI.

### Next action

- Add Odin tar packaging, a cold-boot test from the boot partition and a CI job that records the artifact hashes.

### Evidence

- `source`: [Artifact hashes and the handoff manifest.](https://github.com/KosugiYukina/UniXNU-d1x/blob/6e2aca1cafaa416704d79a2460a99c0059ce0127/reports/v28-manifest.md)

## Diagnostics {#diagnostics}

`implemented`

### Hardware and dependencies

- Kernel console over the debug UART and /dev/console; 300 s test window with an automatic reset to Android.
- Panic screen and the d1x checkpoint markers.

### Configuration

- Kernel arguments -v serial=3 debug=0x14e -enable\_kprintf\_spam and the d1x-\* bring-up flags.
- The test harness prints d1x: alive 300 s and d1x: test boot over after 300 s, then resets.

### Procedure

- Flash, boot, wait for the reset, pull the console log and count checkpoints, faults and processes.
- Compare the SpringBoard and display traces against the previous build before changing code.

### Development findings

- Checkpoints C0 to C25 cover arm\_init through bsd\_init, and the bsd\_init call markers localise a stall to a single subsystem.
- The pass marker is d1x: alive 300 s followed by d1x: test boot over after 300 s. The v28 log is 24656 lines, 1308975 bytes of console text, 64 processes and no panic.
- SpringBoard is exec'd 15 times and exits 15 times; 15 user faults carry ESR 0x92000005 with FAR 0x3adffc846. That signature is downstream of the missing renderer and is not a separate bug.
- The two early debug\_log\_init: Error\!\! gPanicBase is still not initialized lines are emitted before the panic buffer is set up and do not stop the boot.

### Completion criteria

- Every boot produces a complete log with the pass marker and no panic; regressions are visible as a checkpoint change or a new fault signature.

### Current limits

- No KDP, no persistent ramoops and no automatic summary beyond the console log.

### Next action

- Emit a machine-readable boot summary with the last checkpoint, fault counts and process count, and attach it to each image.

### Evidence

- `source`: [Complete v198 console capture.](https://github.com/KosugiYukina/UniXNU-d1x/blob/6e2aca1cafaa416704d79a2460a99c0059ce0127/reports/v28-boot.log)
- `source`: [Machine-readable summary of the same boot.](https://github.com/KosugiYukina/UniXNU-d1x/blob/6e2aca1cafaa416704d79a2460a99c0059ce0127/reports/v28-state.json)

</div>
