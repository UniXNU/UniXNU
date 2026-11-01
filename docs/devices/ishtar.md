# Xiaomi 13 Ultra \(ishtar\)

[peter8889/UniXNU-ishtar](https://github.com/peter8889/UniXNU-ishtar)

<div v-pre>

Xiaomi 13 Ultra \(ishtar\) reuses shared SM8550 support and the sheng kit, and owns its board tree, partition geometry, firmware package and payload policy. This record states what is implemented, what is only configured, and what has not been observed on hardware.

Source record: [porting.toml](https://github.com/peter8889/UniXNU-ishtar/blob/e42ad4d6141a85ca8811868048eb43865d8bf5db/porting.toml), `e42ad4d6141a85ca8811868048eb43865d8bf5db`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `implemented` |
| [Firmware and boot](#firmware) | `implemented` |
| [CPU and interrupts](#cpu) | `implemented` |
| [Memory and DMA](#memory) | `implemented` |
| [Storage and root](#storage) | `planned` |
| [Display](#display) | `planned` |
| [Input](#input) | `planned` |
| [GPU](#gpu) | `planned` |
| [Network](#network) | `planned` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `planned` |
| [Image assembly](#packaging) | `implemented` |
| [Diagnostics](#diagnostics) | `implemented` |

## Configuration {#configuration}

`implemented`

### Hardware and dependencies

- SM8550 shared source pinned in feeds.toml at 23b2049fcd9e30356161def84231334fb55ecca9.
- iPadOS 17.7.11 build 21H461 OS profile.
- Board identity xiaomi,ishtar and the sheng kit reused unchanged.

### Configuration

- board.schema\_version = 2; board.name = ishtar; board.soc = SM8550; board.kit = sheng; board.os\_profile = ipados-17.7.11-21H461.
- kernel.defconfig = sheng\_defconfig; config\_fragments apply arch, soc then os, and the device defconfig applies last.
- kernel.patch\_series is arch, soc, os then device, so a board patch cannot be shadowed by a shared one.

### Procedure

- Run ./unixnu defconfig sheng\_defconfig -D ../UniXNU-ishtar from UniXNU.
- Run ./unixnu status --json -D ../UniXNU-ishtar and confirm profiles resolve in ARM64, SoC, OS, device order.
- Run ./unixnu tree -D ../UniXNU-ishtar and confirm kits/sheng is selected and the device package lands in tree/package.

### Development findings

- The board reuses kit sheng because the package scripts, ADT generator and archive plan are shared with the SM8550 reference board; only board.toml values and the device tree differ.
- Arrays replace inherited selections rather than extending them, so kernel.archives lists every archive the link needs even though most entries come from sheng.
- Three defconfigs exist for different purposes: sheng\_defconfig carries the board build, gpu\_defconfig enables CONFIG\_XNU\_BOOT\_PROGRESS, bringup\_defconfig disables every optional component for early entry debugging.

### Completion criteria

- All source pins resolve, status reports the intended overrides, and tree/ contains the device package plus the shared scripts.

### Current limits

- The board does not yet carry its own kit; it inherits sheng's. A divergent board package would need kits/ishtar and a board.kit change.
- gpu\_defconfig currently leaves CONFIG\_XNU\_NATIVE\_UFS, CONFIG\_XNU\_NATIVE\_LEGACY\_DISPLAY and CONFIG\_XNU\_NATIVE\_MOBILE\_DISPLAY disabled.

### Next action

- Split the board-specific package code out of kit sheng once the bring-up stabilises, so the ishtar tree stops depending on sheng's file layout.

### Evidence

- `source`: [Board identity, partition geometry, archive order, firmware package, payload policy and ADT overrides](https://github.com/peter8889/UniXNU-ishtar/blob/e42ad4d6141a85ca8811868048eb43865d8bf5db/board.toml)
- `source`: [SM8550 shared source pinned to a full commit](https://github.com/peter8889/UniXNU-ishtar/blob/e42ad4d6141a85ca8811868048eb43865d8bf5db/feeds.toml)
- `source`: [gpu profile builds without the boot-progress layer \(CONFIG\_XNU\_BOOT\_PROGRESS=n\); the kernel baseline guard requires the audited native-UFS and owner-root builds, which this profile does not carry yet.](https://github.com/peter8889/UniXNU-ishtar/blob/e42ad4d6141a85ca8811868048eb43865d8bf5db/configs/gpu_defconfig)
- `source`: [gpu archive plan keeps build-adreno-link-stubs.py; build-gop-legacy-display.py was tried and reverted because its audit-mobile-graphics-legacy step needs the owner-root reference candidates \(native-owner-\*-candidate.macho\) that only the audited UFS/owner-root chain produces. The GPU/display kit is tracked as its own workstream.](https://github.com/peter8889/UniXNU-ishtar/blob/e42ad4d6141a85ca8811868048eb43865d8bf5db/board.toml)
- `source`: [tools step now installs the lld-link toolchain \(dtc llvm lld cmake mtools ipsw\) with a fail-fast check, matching the upstream packaging template; the kernel link needs lld-link on the macOS runner.](https://github.com/peter8889/UniXNU-ishtar/blob/e42ad4d6141a85ca8811868048eb43865d8bf5db/.github/workflows/package.yml)
- `source`: [the ishtar device binaries are vendored in the uefi-sheng fork and installed into Binaries/ishtar before packaging, because the Binaries submodule upstream does not carry this device; the firmware build needs RawFiles/SecParti.cfg from there.](https://github.com/peter8889/UniXNU-ishtar/blob/e42ad4d6141a85ca8811868048eb43865d8bf5db/.github/workflows/package.yml)
- `source`: [the uefi-sheng checkout is recursive, because the firmware volume submodules are the binary modules the volume builds from \(the framework template and docs say so\); the ishtar Binaries set is then installed over the submodule path.](https://github.com/peter8889/UniXNU-ishtar/blob/e42ad4d6141a85ca8811868048eb43865d8bf5db/.github/workflows/package.yml)
- `source`: [bootimg.dtb names ../device-tree/hardware.dtb relative to the tree, which is where the dts build writes it; the release flow passes it to bootimg, which otherwise fails with device tree \(--dtb\) not found.](https://github.com/peter8889/UniXNU-ishtar/blob/e42ad4d6141a85ca8811868048eb43865d8bf5db/board.toml)
- `source`: [the images leave the runner encrypted: a random AES-256 key encrypts the tar, and RSA-OAEP to ci/boot-image-recipient.pem protects the key, because the images carry the prelinked Apple kernelcache.](https://github.com/peter8889/UniXNU-ishtar/blob/e42ad4d6141a85ca8811868048eb43865d8bf5db/.github/workflows/package.yml)

## Firmware and boot {#firmware}

`implemented`

### Hardware and dependencies

- ishtarPkg under uefi-sheng Platforms/Xiaomi, built from the sheng firmware tree.
- Stock ishtar firmware DTB for the boot-image step.
- Vendor firmware inventory in proprietary-files.txt, fetched from the recorded upstream commit.

### Configuration

- firmware.config = ishtar; firmware.dsc = Platforms/Xiaomi/ishtarPkg/ishtar.dsc; firmware.fd = Build/ishtarPkg/&\#123;target&\#125;\_CLANGPDB/FV/SILICIUM\_UEFI.fd.
- firmware.defines sets DEVICE\_MODEL = ishtar, ENABLE\_SECUREBOOT = 1, MEMORY\_PROTECTION = TRUE and SHIP\_MODE = FALSE.
- firmware.patches applies Resources/MuPatches/Gic-Spurious.patch, shared with the SM8550 reference board.

### Procedure

- Run ./unixnu firmware -D ../UniXNU-ishtar --uefi ../uefi-sheng.
- Record the firmware commit, the produced FD path and the handoff memory map before any boot attempt.
- Build the payload, then assemble the boot image with the firmware DTB and inspect boot.json for ramdisk\_bytes and dtb\_appended.

### Development findings

- The firmware package name and the device model are both ishtar, so the DSC, the FD path and the ADT product string must agree or the image builds under the wrong identity.
- The firmware DTB is an input to boot-image assembly only; XNU consumes the separately generated ADT, which is why device-tree and ADT values are maintained in different places.
- proprietary-files.txt fetches from a recorded upstream commit so the firmware inventory is reproducible without a local vendor dump.

### Completion criteria

- The firmware FD builds, enters UniXNU, publishes the framebuffer and preserves the documented memory reservations.

### Current limits

- The firmware tree is uefi-sheng, not a dedicated uefi-ishtar repository; ishtarPkg lives inside it.
- No firmware revision or handoff memory map has been recorded from a device boot yet.

### Next action

- Capture the firmware revision, the FD size and the handoff memory map on the first successful device boot.

### Evidence

- `source`: [Firmware inventory with upstream commit and per-file SHA-256 digests](https://github.com/peter8889/UniXNU-ishtar/blob/e42ad4d6141a85ca8811868048eb43865d8bf5db/proprietary-files.txt)

## CPU and interrupts {#cpu}

`implemented`

Components: `ArmCpu`, `ArmDTPlatform`.

### Hardware and dependencies

- SM8550 CPU affinities, GIC distributor and redistributor ranges and the 19.2 MHz timer, all from the shared SoC source.
- Board CPU selection and enablement in dts/ishtar.dts.

### Configuration

- CONFIG\_XNU\_ARMCPU=y and CONFIG\_XNU\_ARM\_DT\_PLATFORM=y in the board defconfig.
- kernel\_args select sheng-smp=1 and armcpu-spi-ipi=1, matching the shared platform's inter-processor interrupt path.
- dts/ishtar.dts includes sm8550.dtsi and overrides only board-level nodes.

### Procedure

- Compile the board DTS with the shared SoC include path and inspect the enabled CPUs, GIC ranges and timer properties in the generated ADT.
- Record per-CPU entry, timer interrupts and inter-processor interrupt delivery.

### Development findings

- CPU affinity values are hardware identifiers read from the firmware, not logical indices; the enabled CPU count and the MPIDR affinities have to be checked together or secondary cores enter at the wrong offset.
- cpu\_init\(\) reaches the architecture switch through cpuid\_info\(\), which returns the single global cpuid\_cpu\_info that do\_cpuid\(\) fills once on the boot CPU and stamps with CPU\_ARCH\_ARMv8, so a secondary CPU already sees a known architecture and never enters the panic arm; the board patch that called do\_cpuid\(\) per CPU was removed as redundant and as a write into a section that is read-only after the late lockdown.
- GIC register ranges must be translated physical addresses from the hardware tree; the raw SoC addresses are not valid once the firmware remaps them.

### Completion criteria

- Every enabled CPU reaches its entry checkpoint and timer and inter-processor interrupt handling works on each enabled CPU.

### Current limits

- CPU entry has not been observed on ishtar hardware; this area is implemented and host-verified only by the board DTS compiling.
- CPU frequency policy is inherited from the sheng kit and has not been retuned for ishtar thermal limits.

### Next action

- Record per-CPU entry and the secondary-core MPIDR values on the first device boot.

### Evidence

- `source`: [Board device tree including the shared SM8550 description](https://github.com/peter8889/UniXNU-ishtar/blob/e42ad4d6141a85ca8811868048eb43865d8bf5db/dts/ishtar.dts)
- `source`: [gpu profile builds without the boot-progress layer \(CONFIG\_XNU\_BOOT\_PROGRESS=n\); the kernel baseline guard requires the audited native-UFS and owner-root builds, which this profile does not carry yet.](https://github.com/peter8889/UniXNU-ishtar/blob/e42ad4d6141a85ca8811868048eb43865d8bf5db/configs/gpu_defconfig)

## Memory and DMA {#memory}

`implemented`

### Hardware and dependencies

- 8 GiB declared DRAM at 0x80000000.
- Splash framebuffer reserved region at 0xb8000000, size 0x2b00000.
- Payload DRAM size and owned memory size recorded in board.toml.

### Configuration

- dts/ishtar.dts declares memory@80000000 with reg = &lt;0 0x80000000 0x2 0x0&gt;, which needs two size cells because a single 0x200000000 literal is truncated by dtc.
- reserved-memory/splash\_region is labelled cont\_splash\_region and marked no-map so the kernel never allocates over the firmware's framebuffer.
- payload.dram\_size = 0x200000000; payload.adt.owned\_memory\_size = 0x130000000.

### Procedure

- Compile the board DTS and confirm the memory node size is 0x200000000 rather than a truncated value.
- Inspect the generated ADT for the owned memory size and the reserved region list before assembling the payload.

### Development findings

- Declaring less DRAM than the phone physically has is deliberate: the physmap and the page-table allocator will otherwise reach addresses no DRAM backs. The SM8550 reference boards declare less than the fitted DRAM for the same reason.
- The reserved splash region must stay no-map. Mapping it as normal memory lets the page-table allocator hand out the framebuffer and the firmware's splash output disappears.
- The size cell count is the single easiest value to get silently wrong; dtc truncates a 64-bit literal in a one-cell property without failing.

### Completion criteria

- The ADT reports the intended DRAM and owned memory sizes and the reserved splash region appears in the handoff list.

### Current limits

- Memory has not been validated on hardware; the declared size follows the reference board policy rather than a measurement of this unit.
- SMMU and DMA address-translation ownership is not configured for this board.

### Next action

- Compare the ADT memory description against the firmware's memory map on the first device boot.

### Evidence

- `source`: [Declared DRAM size and the reserved splash framebuffer region](https://github.com/peter8889/UniXNU-ishtar/blob/e42ad4d6141a85ca8811868048eb43865d8bf5db/dts/ishtar.dts)

## Storage and root {#storage}

`planned`

Components: `ShengUfs`, `VirtioMmioBlock`, `VerifiedRoot`.

### Hardware and dependencies

- SM8550 UFS host controller and PHY resources from the shared SoC source.
- Board UFS and UFS PHY enablement in dts/ishtar.dts, both currently status = okay.
- Userdata partition geometry in board.toml.

### Configuration

- CONFIG\_XNU\_NATIVE\_UFS=n and CONFIG\_XNU\_NATIVE\_VIRTIO\_BLOCK=n in gpu\_defconfig, so the storage path is selected as a component but not compiled into the kernel.
- board.userdata records first\_lba = 3094592, last\_lba = 64007162 and lba\_bytes = 4096, with OS and SystemOS windows.
- dts/ishtar.dts sets ufs and ufsphy status = okay so the nodes are present in the hardware tree.

### Procedure

- Read the UFS controller base address and the PHY register window from the vendor firmware DTB before writing board values.
- Build with CONFIG\_XNU\_NATIVE\_UFS=y once the controller resources are confirmed, and record the boot attempt.
- Confirm the userdata geometry against the stock GPT before mounting anything.

### Development findings

- The UFS nodes are enabled in the device tree while the driver is compiled out, which is intentional: it keeps the hardware description complete so enabling the driver is a configuration change rather than a device-tree change.
- The partition geometry was taken from the stock GPT; first\_lba and last\_lba are absolute LBAs, so they are only valid for a device that has not been repartitioned.
- ShengUfs depends on VirtioMmioBlock and VerifiedRoot, so both appear in the component closure even though neither is compiled in yet.

### Completion criteria

- The kernel probes the UFS controller, reads the GPT and mounts the root volume.

### Current limits

- No controller address has been confirmed for ishtar; the value is expected to match the SM8550 reference board but that has not been checked against this unit's firmware.
- The root volume and the persistent Data volume are both unconfigured.
- No storage evidence of any kind exists for this board yet.

### Next action

- Read the UFS controller base and PHY window out of the stock ishtar firmware DTB and record them before enabling CONFIG\_XNU\_NATIVE\_UFS.

### Evidence

- `source`: [Userdata partition geometry and the selected storage components](https://github.com/peter8889/UniXNU-ishtar/blob/e42ad4d6141a85ca8811868048eb43865d8bf5db/board.toml)
- `source`: [gpu profile builds without the boot-progress layer \(CONFIG\_XNU\_BOOT\_PROGRESS=n\); the kernel baseline guard requires the audited native-UFS and owner-root builds, which this profile does not carry yet.](https://github.com/peter8889/UniXNU-ishtar/blob/e42ad4d6141a85ca8811868048eb43865d8bf5db/configs/gpu_defconfig)

## Display {#display}

`planned`

### Hardware and dependencies

- Panel resolution 1440x3200 with a 5760-byte stride, from the firmware framebuffer.
- Splash framebuffer physical base 0xb8000000 and size 0x2b00000.

### Configuration

- payload.panic\_framebuffer = &\#123; base = 0xb8000000, width = 1440, height = 3200, stride = 5760 &\#125; lets the panic path and the boot-progress renderer write pixels without a display driver.
- CONFIG\_XNU\_NATIVE\_LEGACY\_DISPLAY=n and CONFIG\_XNU\_NATIVE\_MOBILE\_DISPLAY=n, so no display driver is compiled in.
- kernel\_args carry offline-legacy-gop=1 and offline-legacy-unit-scale=2 for the inherited legacy display path.

### Procedure

- Record the framebuffer base, stride and format from the firmware before changing any display value.
- Confirm the panic framebuffer writes appear at the expected offset, since a wrong stride shifts every row.
- Enable CONFIG\_XNU\_NATIVE\_MOBILE\_DISPLAY only after the panel controller resources are confirmed.

### Development findings

- The only display output that works without a driver is the direct framebuffer path: panic screen and boot progress both write through the physical base, which is why they survive a hang before any display driver exists.
- Stride is not width times bytes per pixel. The panel reports 5760 bytes for 1440 pixels, so the renderer must use the reported stride or every row lands at the wrong address.
- The framebuffer is a reserved no-map region, so it is reachable only through the physical aperture once arm\_vm\_init has run.

### Completion criteria

- The panel shows kernel output through a real display driver rather than a direct framebuffer write.

### Current limits

- No display driver is compiled in; only the direct framebuffer path is available.
- Panel timing, backlight and the display controller have not been configured for this board.
- The framebuffer has not been observed on ishtar hardware.

### Next action

- Confirm the firmware framebuffer base and stride on the device, then enable CONFIG\_XNU\_NATIVE\_MOBILE\_DISPLAY with the panel resources filled in.

### Evidence

- `source`: [Panic framebuffer geometry used by the direct framebuffer path](https://github.com/peter8889/UniXNU-ishtar/blob/e42ad4d6141a85ca8811868048eb43865d8bf5db/board.toml)

## Input {#input}

`planned`

### Hardware and dependencies

- Novatek NT36532 touch controller firmware, recorded in proprietary-files.txt with its SHA-256 digest.
- Touch bus, GPIO and interrupt assignment, not yet read from the vendor firmware.

### Configuration

- ShengHidInput and ShengNovatekTouch exist in the tree but are not listed in board.components.include, so neither is built.
- proprietary-files.txt carries the Novatek firmware blob so the touch driver has its firmware input available once selected.

### Procedure

- Read the touch controller's bus, reset GPIO and interrupt line from the vendor firmware DTB.
- Add ShengHidInput and ShengNovatekTouch to board.components.include and rebuild.
- Record the first touch report and the coordinate mapping.

### Development findings

- The touch firmware blob is already pinned even though the driver is not selected, so enabling input does not require a new vendor dump.
- ShengNovatekTouch depends on QcomGeniSpi for the SPI transport, so enabling touch pulls in the GENI SPI component as well.

### Completion criteria

- Touch reports reach the HID stack with correct coordinates and the home gesture is recognised.

### Current limits

- No input component is selected for this board.
- Bus, GPIO and interrupt values are unconfirmed.
- No input evidence exists for this board.

### Next action

- Read the Novatek controller's bus and interrupt assignment from the vendor firmware DTB.

### Evidence

- `source`: [Novatek touch firmware pinned with its SHA-256 digest](https://github.com/peter8889/UniXNU-ishtar/blob/e42ad4d6141a85ca8811868048eb43865d8bf5db/proprietary-files.txt)

## GPU {#gpu}

`planned`

Components: `Adreno740`, `Sm8550Platform`, `AdrenoPM4`, `AdrenoFirmware`, `ArmSmmu4K`.

### Hardware and dependencies

- Adreno 740 GPU and GMU resources from the shared SM8550 source.
- GPU firmware and PM4 microcode, audited by the probe builders in package/.
- GPU SMMU and GMU enablement in dts/ishtar.dts, all three currently status = okay.

### Configuration

- CONFIG\_XNU\_NATIVE\_ADRENO=y, but CONFIG\_XNU\_EXTRA\_LD\_ARCHIVES points at build/adreno-link-stubs/libAdrenoLinkStubs.a, so the kernel links against stubs rather than the full driver.
- kernel\_args carry sheng-gpu-power=9, sheng-gpu-metal=1 and sheng-gpu-perf=8, inherited from the shared platform.
- dts/ishtar.dts enables gpu, gmu and gpu\_smmu.

### Procedure

- Run scripts/build-adreno-link-stubs.py to produce the stub archive the kernel link expects.
- Run the Adreno probe builders and compare the reported GPU identity against the expected Adreno 740 values.
- Record the first GPU command submission once the real driver replaces the stubs.

### Development findings

- The kernel links with Adreno link stubs on purpose: the full Adreno driver needs the AdrenoMetal accelerator ABI, which is a payload-stage component and has no kernel link variable. Selecting the component while linking stubs keeps the archive plan valid.
- GPU firmware and PM4 microcode are inputs, not build products; the probe builders audit the recorded candidates rather than regenerating them.
- Adreno740 pulls in Sm8550Platform, AdrenoPM4, AdrenoFirmware and ArmSmmu4K, which is why five components belong to this area.

### Completion criteria

- The GPU reports its identity, accepts a command submission and presents a frame through the Metal frontend.

### Current limits

- Only link stubs are compiled; no GPU command has been submitted on this board.
- The GPU and GMU have not been powered on outside the firmware.
- No GPU evidence exists for this board.

### Next action

- Run the Adreno probe builders against the ishtar firmware and record the reported GPU identity.

### Evidence

- `source`: [Builds the stub archive the kernel link uses while the full driver is unavailable](https://github.com/peter8889/UniXNU-ishtar/blob/e42ad4d6141a85ca8811868048eb43865d8bf5db/scripts/build-adreno-link-stubs.py)
- `source`: [gpu profile builds without the boot-progress layer \(CONFIG\_XNU\_BOOT\_PROGRESS=n\); the kernel baseline guard requires the audited native-UFS and owner-root builds, which this profile does not carry yet.](https://github.com/peter8889/UniXNU-ishtar/blob/e42ad4d6141a85ca8811868048eb43865d8bf5db/configs/gpu_defconfig)

## Network {#network}

`planned`

### Hardware and dependencies

- Ath12k Wi-Fi hardware resources, not yet mapped for this board.
- Board Wi-Fi firmware and calibration data, not yet collected.

### Configuration

- drivers/Ath12kWifi exists in the tree but is not listed in board.components.include, so it is not built.
- No network kernel arguments are set in board.toml.

### Procedure

- Map the Wi-Fi PCIe or AHB window and the interrupt line from the vendor firmware.
- Collect the board calibration data and firmware before selecting the component.
- Add the component to board.components.include and record the first association attempt.

### Development findings

- The driver directory is present because the tree is derived from sheng, which does select it; ishtar does not, so the directory is currently unused by this board.
- Wi-Fi on this platform needs per-board calibration data that cannot be reused from a different board even on the same SoC.

### Completion criteria

- The interface associates and carries packets through the OS network stack.

### Current limits

- No network component is selected for this board.
- Calibration data has not been collected.
- No network evidence exists for this board.

### Next action

- Determine whether the Wi-Fi window is PCIe or AHB on this board before selecting the driver.

### Evidence

- `source`: [Component selection showing that no network component is included](https://github.com/peter8889/UniXNU-ishtar/blob/e42ad4d6141a85ca8811868048eb43865d8bf5db/board.toml)

## Audio {#audio}

`planned`

### Hardware and dependencies

- ADSP firmware and the codec topology, neither collected for this board.
- Board audio routing, not yet documented.

### Configuration

- No audio component is selected in board.components.include.
- The ADSP probe builders exist in package/ but are not part of the ishtar archive plan.

### Procedure

- Collect the ADSP firmware image and record its hash.
- Map the codec and the amplifier enable GPIOs from the vendor firmware.
- Select the audio components and record playback and capture separately.

### Development findings

- ADSP firmware is a per-board input; the probe builders audit a recorded candidate rather than synthesising one.
- The audio path on this platform spans ADSP, codec and amplifier, so it cannot be enabled by a single component selection.

### Completion criteria

- Playback and capture both work through the OS audio stack.

### Current limits

- No audio component is selected.
- No firmware or routing data has been collected.
- No audio evidence exists for this board.

### Next action

- Collect the ADSP firmware image and record its hash before attempting audio bring-up.

### Evidence

- `source`: [Component selection showing that no audio component is included](https://github.com/peter8889/UniXNU-ishtar/blob/e42ad4d6141a85ca8811868048eb43865d8bf5db/board.toml)

## Power {#power}

`planned`

### Hardware and dependencies

- Regulator and clock ownership from the shared SM8550 source.
- Battery fuel gauge configuration, not yet confirmed for this board.

### Configuration

- CONFIG\_XNU\_SHENG\_PMGR=y, inherited from the shared platform, but the power manager has not been exercised on this board.
- kernel\_args carry sheng-cpufreq=3 and sheng-disable-watchdogd=1.
- payload.adt.defaults.u32 sets sleep-disabled = 1 so the device does not suspend during bring-up.

### Procedure

- Record the regulator and clock state the firmware leaves behind before claiming ownership.
- Confirm the fuel gauge reports a plausible charge level before enabling battery reporting.
- Remove sleep-disabled = 1 only after suspend and resume are understood.

### Development findings

- sleep-disabled = 1 is a bring-up setting, not a shipping one; leaving it set hides suspend bugs rather than fixing them.
- The power manager is compiled in through the shared platform but has no board-specific regulator or clock table for ishtar yet.
- CPU frequency policy is inherited from the shared platform and has not been retuned for this board's thermal envelope.

### Completion criteria

- Regulators and clocks are owned by the OS, the battery reports a plausible charge, and suspend and resume work.

### Current limits

- No board-specific regulator or clock configuration exists.
- The fuel gauge has not been read on this board.
- No power evidence exists for this board.

### Next action

- Read the fuel gauge on the first device boot and compare it against the stock firmware's reported charge.

### Evidence

- `source`: [Power-related kernel arguments and the sleep-disabled bring-up default](https://github.com/peter8889/UniXNU-ishtar/blob/e42ad4d6141a85ca8811868048eb43865d8bf5db/board.toml)
- `source`: [gpu profile builds without the boot-progress layer \(CONFIG\_XNU\_BOOT\_PROGRESS=n\); the kernel baseline guard requires the audited native-UFS and owner-root builds, which this profile does not carry yet.](https://github.com/peter8889/UniXNU-ishtar/blob/e42ad4d6141a85ca8811868048eb43865d8bf5db/configs/gpu_defconfig)

## Image assembly {#packaging}

`implemented`

Components: `DarwinBoot`, `XnuPrelink`, `SoftwareAES`.

### Hardware and dependencies

- iPadOS 17.7.11 kernelcache as the prelink input.
- Firmware DTB for boot-image assembly.
- The recorded archive plan in board.kernel.archives.

### Configuration

- kernel.archives lists the ordered archive plan, mixing component: entries and script filenames.
- payload.volume = ISHTARESP, size\_mib = 54, loader = firmware, title = Boot iPadOS.
- bootimg.dtb\_node adds reserved-memory/splash\_region to the firmware DTB so the firmware hands the framebuffer over.

### Procedure

- Run ./unixnu kernel -D ../UniXNU-ishtar and confirm kernel/kernel.macho is produced.
- Run ./unixnu payload -D ../UniXNU-ishtar and confirm payload/payload.img and payload/payload.json.
- Run ./unixnu bootimg -D ../UniXNU-ishtar and confirm the assembled image reports a passing round trip.

### Development findings

- The archive plan is explicit rather than inherited, so every kernel-stage recipe appears in order; a component: entry resolves through the component catalog and a bare filename runs a shared builder.
- build-adreno740-accelerator.py is deliberately absent from the archive plan because it needs a payload-stage header that the kernel link does not provide; adding it fails the link.
- Boot-image assembly needs the firmware DTB. Without it the payload is correct but the image cannot be produced.
- The container is larger than the payload because the boot image inlines a 64 MiB window at 0xF0000000 with ramdisk\_bytes = 0 and no appended device tree.

### Completion criteria

- Kernel, payload and boot image all build, and the assembled image passes its own round-trip check.

### Current limits

- The boot image has never been loaded on ishtar hardware.
- The build has no recorded host verification entry yet because the device repository has no published commit to cite.
- Kernel build reliability is affected by an intermittent clang frontend crash on osfmk/vm/vm\_kern.c, which is resolved by re-running the single translation unit rather than by a source change.

### Next action

- Publish the device repository, then record the kernel, payload and boot-image commands with the resulting commit as host evidence.

### Evidence

- `source`: [Board kernel configuration including the extra link archive and the boot-progress switch](https://github.com/peter8889/UniXNU-ishtar/blob/e42ad4d6141a85ca8811868048eb43865d8bf5db/configs/gpu_defconfig)
- `source`: [Archive plan, payload policy and boot-image device-tree overlay](https://github.com/peter8889/UniXNU-ishtar/blob/e42ad4d6141a85ca8811868048eb43865d8bf5db/board.toml)
- `source`: [gpu profile builds without the boot-progress layer \(CONFIG\_XNU\_BOOT\_PROGRESS=n\); the kernel baseline guard requires the audited native-UFS and owner-root builds, which this profile does not carry yet.](https://github.com/peter8889/UniXNU-ishtar/blob/e42ad4d6141a85ca8811868048eb43865d8bf5db/configs/gpu_defconfig)

## Diagnostics {#diagnostics}

`implemented`

### Hardware and dependencies

- Framebuffer geometry from board.toml for direct pixel writes.
- The kernel symbol physmap\_base for reaching the framebuffer after arm\_vm\_init.
- The 5x12 glyph table in the firmware Font.h.

### Configuration

- CONFIG\_XNU\_BOOT\_PROGRESS=y selects the boot-progress observer in gpu\_defconfig.
- Two implementations provide the entry points: BootProgressMin.c is self-contained and links into any configuration, while BootProgress.c is the full monitor and requires the audited UFS, owner-root, Virtio and source-corecrypto build.
- payload.panic\_screen = true and payload.panic\_framebuffer give the panic path a place to draw.

### Procedure

- Run scripts/build-boot-progress-min.py to build libBootProgress.a and confirm the undefined-symbol gate passes.
- Boot the image and photograph the panel; the last numbered log line identifies the stage the kernel did not survive.
- Compare the last stage against the checkpoint list to pick the next area to investigate.

### Development findings

- The observer must never fault: a diagnostic that faults turns a hang into a hang with no output. Every kernel pointer is probe-translated with AT S1E1R before it is read, and every framebuffer store is bounded by the geometry the console reported.
- boot\_progress\_active\(\) stays false until a framebuffer has been validated, so a board with no usable framebuffer keeps its normal console output instead of going silent.
- Once the observer binds, the normal console output is suppressed; a rendering fault therefore leaves a half-drawn screen with no textual output. The panic screen is a separate mechanism and is unaffected.
- The self-contained implementation is chosen by default because the full monitor reads UFS and Virtio counters directly and fails the link in a reduced configuration.
- A fixed-size literal destination can be constant-folded into mov/movk immediates, so a string that is visibly in the source may not appear in \_\_cstring. Verifying that a patch reached the image needs a string that is genuinely stored as a literal.

### Completion criteria

- The screen shows the boot-progress panel and the last logged stage identifies where the kernel stopped.

### Current limits

- The observer has never rendered on ishtar hardware; its layout has only been verified on the host with a synthetic framebuffer.
- The full monitor implementation cannot be selected without the audited storage, owner-root, Virtio and corecrypto build.

### Next action

- Boot the boot-progress image on ishtar and record the last logged stage together with a photograph of the panel.

### Evidence

- `source`: [Self-contained boot-progress observer that renders stages to the raw framebuffer](https://github.com/peter8889/UniXNU-ishtar/blob/e42ad4d6141a85ca8811868048eb43865d8bf5db/package/BootProgressMin.c)
- `source`: [Build script with an undefined-symbol gate that rejects the object when the kernel image cannot satisfy it](https://github.com/peter8889/UniXNU-ishtar/blob/e42ad4d6141a85ca8811868048eb43865d8bf5db/scripts/build-boot-progress-min.py)

</div>
