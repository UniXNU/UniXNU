# Xiaomi Pad 8 Pro: first XNU boot from RAM \(OnePlus 13T base\) \(donyanchen\)

[donyanchen/UniXNU-piano](https://github.com/donyanchen/UniXNU-piano)

<div v-pre>

Xiaomi Pad 8 Pro \(piano, SM8750\) boots iPadOS 17.7.11 from RAM through a Mu-Silicium based UEFI, using the SM8750 support and the board-owned storage, PMGR and firmware integration. Not booted on the device yet.

Source record: [porting.toml](https://github.com/donyanchen/UniXNU-piano/blob/167776dc0cbee63c190abbbf0a556981ac8aaba1/porting.toml), `167776dc0cbee63c190abbbf0a556981ac8aaba1`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `implemented` |
| [Firmware and boot](#firmware) | `implemented` |
| [CPU and interrupts](#cpu) | `implemented` |
| [Memory and DMA](#memory) | `planned` |
| [Storage and root](#storage) | `implemented` |
| [Display](#display) | `planned` |
| [Input](#input) | `planned` |
| [GPU](#gpu) | `not-applicable` |
| [Network](#network) | `not-applicable` |
| [Audio](#audio) | `not-applicable` |
| [Power](#power) | `implemented` |
| [Image assembly](#packaging) | `planned` |
| [Diagnostics](#diagnostics) | `planned` |

## Configuration {#configuration}

`implemented`

### Hardware and dependencies

- SM8750 SoC support from the OnePlus 13T port \(UniXNU-sm8750-common\), an iPadOS 17.7.11 \(21H461\) IPSW, and a UniXNU checkout pinned by the packaging workflow.

### Configuration

- board.soc\_source = sm8750; board.os\_profile = ipados-17.7.11-21H461; board.kit = piano; schema\_version = 2.
- configs/piano\_defconfig selects the native UFS, AES, virtio block and ram block archives plus CONFIG\_XNU\_SHENG\_PMGR; configs/piano\_bootstrap\_defconfig is the same selection with CONFIG\_XNU\_SHENG\_PMGR off.
- \[kernel\].archives is read from board.toml, not from the defconfig, so a selection change has to touch both files.

### Procedure

- Run ./unixnu defconfig piano\_defconfig -D ../device from the UniXNU checkout.
- Run ./unixnu fetch, ./unixnu ipsw fetch -D ../device and ./unixnu tree -D ../device.
- Trigger .github/workflows/package-bare-metal.yml with os=17 and jobs=4.

### Development findings

- The kernel step runs as two passes. configs/piano\_bootstrap\_defconfig builds a kernel without the sheng PMGR binder and stages it as build/xnu-prelink/native-owner-ufs-rootauth3-candidate.macho, because build-sheng-platform-power.py refuses to start without a reference candidate \('No reference candidate available'\).
- The PMGR binder is listed in \[kernel\].archives, which the bootstrap pass also reads, so the candidate step removes that line from board.toml with python \(macOS sed -i treats the next argument as the suffix\), builds, and restores the file.
- build-sheng-platform-power.py compiles $TREE/kits/sheng/ShengPlatformPower.cpp, while the board ships the source at package/ShengPlatformPower.cpp; the defconfig step now copies it into both out/.../piano/tree/kits/sheng and out/.../piano\_bootstrap/tree/kits/sheng.
- audit-amfi-pmgr-contract.py reads tree/.cache/firmware/kernelcache.macho/kernelcache.release.ipad7.decompressed, so the candidate step copies out/ipsw/21H461/kernelcache.decompressed there.
- The UEFI checkout is read-only, and its piano.dsc lacks the UniXNULib mapping \(error 4000\), so patches/uefi/piano-dsc-unixnulib.patch is applied in the prep step with the two-level uefi/uefi/pianoPkg/piano.dsc path.
- patches/xnu/series on the SoC side already carries sheng-platform-power.patch; adding it to the device series applies it twice and fails at bsd\_init.c:688.
- The device release is driven by scripts/package.sh, which only resolves \[package\] unixnu from board.toml and hands everything else to the pinned UniXNU checkout.

### Completion criteria

- All source pins resolve, every selected component is covered by an area, and the two-pass kernel build links with the sheng PMGR archive force-loaded.

### Current limits

- The UniXNU revision is pinned in the workflow; the effective component set is only visible through ./unixnu status.

### Next action

- Compare ./unixnu status --json output whenever a defconfig, fragment or source pin changes.

### Evidence

- `source`: [candidate pass, ShengPlatformPower.cpp staging and the fixed kernelcache path for the PMGR audit; the prep step also applies patches/uefi/piano-dsc-unixnulib.patch and patches/uefi/piano-start-unixnu.patch, patches/uefi/bootshim-image-size.patch and patches/uefi/mu-sec-entry-arg.patch \(the last two against uefi/deps/Mu-Silicium, because that checkout and its BootShim and SEC sources only exist after tools/setup-deps.sh\), and patches/unixnu-bootimg-text-offset.patch against the pinned UniXNU checkout, applies patches/uefi/piano-usb-diagnostics.patch for the USB bring-up trace, and runs scripts/prepare-unixnu-diagnostics.py on its UniXNULib/Config.c](https://github.com/donyanchen/UniXNU-piano/blob/167776dc0cbee63c190abbbf0a556981ac8aaba1/.github/workflows/package-bare-metal.yml)
- `source`: [bootstrap selection: identical to piano\_defconfig except CONFIG\_XNU\_SHENG\_PMGR](https://github.com/donyanchen/UniXNU-piano/blob/167776dc0cbee63c190abbbf0a556981ac8aaba1/configs/piano_bootstrap_defconfig)
- `source`: [board identity, component selection, \[kernel\].archives and \[package\].unixnu the packaging workflow consumes](https://github.com/donyanchen/UniXNU-piano/blob/167776dc0cbee63c190abbbf0a556981ac8aaba1/board.toml)

## Firmware and boot {#firmware}

`implemented`

### Hardware and dependencies

- Mu-Silicium based UEFI for SM8750, spliced through tools/setup-deps.sh, plus the board UEFI repository pinned by the workflow.

### Configuration

- \[firmware\] config = piano, dsc = Platforms/Xiaomi/pianoPkg/piano.dsc, fd = Build/pianoPkg/&\#123;target&\#125;\_CLANGPDB/FV/SILICIUM\_UEFI.fd.
- \[firmware\].packages lists the UEFI root, &\#123;tree&\#125;/package, &\#123;tree&\#125;/kits, &\#123;tree&\#125;/drivers/DarwinBoot and the EDK II/Mu trees.
- \[firmware.defines\] UNIXNU = 1 and DEVICE\_MODEL = piano.

### Procedure

- Run uefi/tools/setup-deps.sh in the UEFI checkout.
- Apply patches/uefi/piano-dsc-unixnulib.patch at the repository root.
- Run ./unixnu build firmware -D ../device --uefi ../uefi/deps/Mu-Silicium.

### Development findings

- The firmware volume failed with error 4000 \('Instance of library class \[UniXNULib\] is not found for module ... UniXNU.inf'\) because pianoPkg/piano.dsc had no LibraryClasses mapping for UniXNULib; the patch adds it.
- ENABLE\_SECUREBOOT defined empty made '\#if ENABLE\_SECUREBOOT == 1' an invalid token; the DSC now defines it as 0.
- The firmware packages list needs drivers/DarwinBoot rather than the older PaganiDarwinBoot path.
- PianoFastbootStart prints only one line per outcome and the boot manager clears the screen when it draws, so the 'piano-uefi' fastboot interface was never observable: OTG showed nothing but the two root hubs. The patch prints the UsbDevice protocol and StartEx results and holds each line for two seconds, and it retries both the protocol lookup \(10 x 200 ms\) and StartEx \(5 x 300 ms\) instead of losing the race against the asynchronous controller bring-up. PmicDxe stays disabled: its SPMI channel 690 access faults because ABL no longer grants that channel to the apps execution environment, and the fault is what the vendor comment records. UFS still enumerates, so the protocols the storage path needs are provided by the unconditionally loaded charger and platform drivers; a StartEx failure would point at the rails rather than at a missing protocol.
- The stock boot manager never started UniXNU.efi: DeviceBootManagerAfterConsole ran PianoDtbInstall, PianoFastbootStart, StartEspLoader and StartFvApp\(AndroidBoot\), so the menu built into the firmware volume was unreachable. The first patch added a StartFvApp call with UniXNU's FILE\_GUID; the board then booted UEFI all the way to the console and dropped into the UEFI Shell instead of the menu, because StartFvApp built its device path from DevicePathFromHandle\(LoadedImage-&gt;DeviceHandle\), which inside BDS does not carry a usable firmware volume path, so EfiBootManagerBoot failed silently. StartFvApp now reads the PE32 section with GetSectionFromAnyFv and calls LoadImage/StartImage itself, and prints each outcome on the console so the next boot states whether the image is in a volume, failed to load, or returned.

### Completion criteria

- The firmware step emits SILICIUM\_UEFI.fd for pianoPkg with the UniXNU application linked in.

### Current limits

- No firmware image has been booted on the device yet; the GOP handover is unverified.

### Next action

- Boot the firmware and capture its serial output before claiming the UEFI stage.

### Evidence

- `source`: [reports the USB device protocol lookup and StartEx result on the console, each held for two seconds, so the piano-uefi fastboot bring-up can be diagnosed without a serial port](https://github.com/donyanchen/UniXNU-piano/blob/167776dc0cbee63c190abbbf0a556981ac8aaba1/patches/uefi/piano-usb-diagnostics.patch)
- `source`: [starts UniXNU.efi from the firmware volume before the ESP loader and AndroidBoot fallbacks, and loads it with GetSectionFromAnyFv plus LoadImage/StartImage instead of a device path built from the BDS loaded image, printing each outcome on the console; the patch names uefi/uefi/pianoPkg/Library/DeviceBootManagerLib/DeviceBootManager.c because the UEFI repository carries its own uefi/ directory and prep applies it from the workspace root](https://github.com/donyanchen/UniXNU-piano/blob/167776dc0cbee63c190abbbf0a556981ac8aaba1/patches/uefi/piano-start-unixnu.patch)
- `source`: [adds the UniXNULib LibraryClasses mapping that fixes the error 4000 firmware build failure](https://github.com/donyanchen/UniXNU-piano/blob/167776dc0cbee63c190abbbf0a556981ac8aaba1/patches/uefi/piano-dsc-unixnulib.patch)

## CPU and interrupts {#cpu}

`implemented`

Components: `ArmCpu`, `ArmDTPlatform`.

### Hardware and dependencies

- SM8750 CPU nodes in the device tree, the ARM generic timer, and the GICv3 ranges of the SoC.

### Configuration

- CONFIG\_XNU\_ARMCPU, CONFIG\_XNU\_ARM\_DT\_PLATFORM and CONFIG\_XNU\_NATIVE\_ARCH\_TIMER in piano\_defconfig.
- board.toml \[components\].include selects ArmCpu and ArmDTPlatform; \[kernel\].archives builds both as components.

### Procedure

- Run ./unixnu build kernel -D ../device and inspect logs/component-ArmCpu.log.
- Boot with cpus=1 in the kernel arguments \(board.toml \[payload\].kernel\_args\).

### Development findings

- The first RAM boot is limited to one CPU through the cpus=1 kernel argument, so smp bring-up is not exercised yet.
- The BCM2837 panic buffer address in the shared code is not mapped on this device, so CONFIG\_XNU\_DT\_PANIC\_REGION is enabled to take the panic region from the device tree.

### Completion criteria

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works.

### Current limits

- Only one CPU is expected to be online on the first boot.

### Next action

- Raise cpus once one CPU boots to user space.

### Evidence

- `source`: [ArmCpu, ArmDTPlatform, native arch timer and DT panic region selections](https://github.com/donyanchen/UniXNU-piano/blob/167776dc0cbee63c190abbbf0a556981ac8aaba1/configs/piano_defconfig)

## Memory and DMA {#memory}

`planned`

### Hardware and dependencies

- DRAM layout, the reserved regions of the SM8750 firmware, and the owned memory size handed over by UEFI.

### Configuration

- \[payload\] dram\_size = 0x180000000; \[payload.adt\] owned\_memory\_size = 0x100000000.
- \[adt.defaults.u32\] sleep-disabled = 1.

### Procedure

- Read the UEFI memory map from the firmware serial output and compare it with dts/piano.dts reservations.

### Development findings

- The owned memory size is 4 GiB while the payload DRAM size is 6 GiB; no device boot has validated the split yet.

### Completion criteria

- The kernel boots with the retained reservations intact and DMA of the storage and display controllers stays inside the owned range.

### Current limits

- A device memory map has not been captured yet.

### Next action

- Capture the UEFI memory map on the first boot and reconcile it with the device tree.

### Evidence

Collect evidence using the next action.

## Storage and root {#storage}

`implemented`

Components: `ShengUfs`, `VirtioMmioBlock`, `RamBlock`, `VerifiedRoot`.

### Hardware and dependencies

- iPadOS 17.7.11 \(21H461\) IPSW, the signed verified-root policies from 044-76040-038.dmg and 044-76034-038.dmg, and the original kernelcache as the ABI reference.

### Configuration

- CONFIG\_XNU\_NATIVE\_UFS, CONFIG\_XNU\_NATIVE\_VIRTIO\_BLOCK, CONFIG\_XNU\_NATIVE\_RAM\_BLOCK and CONFIG\_XNU\_VERIFIED\_ROOT\_PROBE.
- CONFIG\_XNU\_NATIVE\_UFS\_ARCHIVE, CONFIG\_XNU\_NATIVE\_VIRTIO\_BLOCK\_ARCHIVE, CONFIG\_XNU\_NATIVE\_RAM\_BLOCK\_ARCHIVE and CONFIG\_XNU\_VERIFIED\_ROOT\_ARCHIVE point at the archives the kernel step builds.
- \[payload\].kernel\_args carries native-ufs-root=1; \[payload.adt\].root\_match\_volume\_uuid names the APFS volume 04769D26-2CA0-4825-B443-E2E5F88300F2 of 044-76040-038.dmg.

### Procedure

- Run ./unixnu ipsw fetch -D ../device to place the IPSW under out/ipsw/21H461.
- Run python3 scripts/prepare-ufs-policies.py --tree &lt;tree&gt; --inputs &lt;ipsw&gt; --openssl-prefix $\(brew --prefix openssl@3\).
- Run ./unixnu build kernel -D ../device, which builds ShengUfs, VirtioMmioBlock and RamBlock and their bindings against kernelcache.decompressed.

### Development findings

- The three storage components share one set of binding objects: 468d1fd put the raw bindings only in libShengUfs.a and let VirtioMmioBlock and RamBlock reuse them, which removed twelve duplicate symbols at link time.
- 67ad370 dropped a native\_ufs\_store\_write stub already provided by NativeUfs.o, and 2b1e6ec kept only the weak native\_ufs\_store\_write\_cached stub.
- The policies step has to read the DMG files from out/ipsw/21H461, not from the device output directory \(e04d7c2\).
- The verified-root probe needs -Wno-missing-include-dirs because the probe compiles outside the SDK include set \(70c6fc7\).
- The binding scripts take the kernelcache as the ABI reference and the PMGR audit reads it from tree/.cache/firmware/kernelcache.macho/, so the candidate step copies it there.

### Completion criteria

- The kernel links with the storage archives, the prelink succeeds, and the payload declares the native UFS root.

### Current limits

- No UFS controller has been probed on the device; the APFS root has never been mounted.

### Next action

- Boot with native-ufs-root=1 and capture the first UFS probe output.

### Evidence

- `source`: [extracts and signs the verified-root policies from the two iPadOS DMG inputs](https://github.com/donyanchen/UniXNU-piano/blob/167776dc0cbee63c190abbbf0a556981ac8aaba1/scripts/prepare-ufs-policies.py)
- `source`: [storage selections and archive paths the kernel links](https://github.com/donyanchen/UniXNU-piano/blob/167776dc0cbee63c190abbbf0a556981ac8aaba1/configs/piano_defconfig)

## Display {#display}

`planned`

Components: `GopFramebuffer`.

### Hardware and dependencies

- UEFI GOP framebuffer handed over by the firmware, panel timing of the Pad 8 Pro and the ktz8866 backlight.

### Configuration

- \[components\].include selects GopFramebuffer.
- \[payload\].kernel\_args carries offline-legacy-gop=1.
- \[adt.chosen.u32\] display-scale = 2 and display-rotation = 0.

### Procedure

- Read the framebuffer base and size from the UEFI output, then boot with offline-legacy-gop=1.

### Development findings

- The splash region of the device is 0xfc800000 with a size of 0x2b00000, the same base the Pagani 13T port uses for FB\_BASE.
- The native Adreno path is disabled \(CONFIG\_XNU\_NATIVE\_ADRENO is not set\) and the legacy display path is disabled too, so the first boot is expected to use the GOP framebuffer.

### Completion criteria

- The verbose XNU boot log is visible on the panel from a RAM boot.

### Current limits

- No framebuffer handover has been observed on the device.

### Next action

- Confirm the GOP base and stride against the firmware output on the first boot.

### Evidence

- `source`: [GOP selection, display scale and rotation, and the offline-legacy-gop=1 argument](https://github.com/donyanchen/UniXNU-piano/blob/167776dc0cbee63c190abbbf0a556981ac8aaba1/board.toml)

## Input {#input}

`planned`

### Hardware and dependencies

- Novatek touch controller, the pogo keyboard cover and the volume/power keys of the Pad 8 Pro.

### Configuration

- \[adt.buttons.string\] compatible = buttons; \[adt.buttons.strings\] button-names = \[hold, voldown, volup\]; \[adt.buttons.u32\] home-button-type = 2.

### Procedure

- Boot with the buttons node present and read the HID devices from the boot log.

### Development findings

- The device tree only describes the physical buttons; no touch or keyboard driver is selected yet.

### Completion criteria

- Buttons and touch report events under XNU.

### Current limits

- The touch controller is not part of the first RAM boot scope.

### Next action

- Inventory the Novatek touch node and its interrupts for a later pass.

### Evidence

Collect evidence using the next action.

## GPU {#gpu}

`not-applicable`

### Hardware and dependencies

- Adreno 830 GMU and SMMU, which are out of scope for the first RAM boot.

### Configuration

- CONFIG\_XNU\_NATIVE\_ADRENO is not set in piano\_defconfig.

### Procedure

- Not applicable until the first boot reaches user space.

### Development findings

- The first RAM boot only needs a framebuffer console, so no GPU component is selected.

### Completion criteria

- Not applicable while the GPU component set is empty.

### Current limits

- SM8750 GPU support would need the Adreno 830 GMU, SMMU and firmware integration that the shared SM8750 support does not carry yet.

### Next action

- Revisit after the first boot reaches a user session.

### Evidence

Collect evidence using the next action.

## Network {#network}

`not-applicable`

### Hardware and dependencies

- The Pad 8 Pro Wi-Fi module, which is not identified in the device tree yet.

### Configuration

- No network component is selected in board.toml.

### Procedure

- Not applicable for the first RAM boot.

### Development findings

- The community SM8750 support has no working Wi-Fi component for this platform, so the first boot is offline.

### Completion criteria

- Not applicable while the network component set is empty.

### Current limits

- The Wi-Fi module and its firmware are unidentified.

### Next action

- Identify the Wi-Fi module from the hardware once boot is stable.

### Evidence

Collect evidence using the next action.

## Audio {#audio}

`not-applicable`

### Hardware and dependencies

- Pad 8 Pro speaker amplifiers, which are out of scope for the first RAM boot.

### Configuration

- No audio component is selected in board.toml.

### Procedure

- Not applicable for the first RAM boot.

### Development findings

- Audio is not needed to observe the verbose boot log.

### Completion criteria

- Not applicable while the audio component set is empty.

### Current limits

- The amplifier and codec parts of the Pad 8 Pro are not integrated.

### Next action

- Revisit with the measured codec I2C addresses after boot.

### Evidence

Collect evidence using the next action.

## Power {#power}

`implemented`

Components: `AppleKeyStoreState`.

### Hardware and dependencies

- The original ApplePMGR implementation of the reference kernelcache, and the 340-entry provider table of IOPMGR.

### Configuration

- CONFIG\_XNU\_SHENG\_PMGR in piano\_defconfig; the bootstrap defconfig leaves it off.
- \[payload\].kernel\_args carries sheng-pmgr=2.

### Procedure

- Build the bootstrap kernel without the PMGR binder and stage it as the reference candidate.
- Run ./unixnu build kernel -D ../device, which runs build-sheng-platform-power.py against that candidate.
- Read logs/archive-15-build-sheng-platform-power.log.

### Development findings

- build-sheng-platform-power.py audits the AMFI read/OR/write sequence and the AppleT8011PMGR provider slots of the reference candidate before it emits the archive, and refuses to build when either check fails.
- The instrument inherits only the two original AON slots \(320, 321\) from ApplePMGR and refuses every unimplemented slot through unavailable\(\), so a missing power backend stops instead of writing.
- The bootstrap pass cannot run the same binder because the binder is the thing that needs the candidate it produces; the candidate step therefore strips it from \[kernel\].archives for that pass only.
- The archive is registered late \(llvm-objcopy removes \_\_DATA,\_\_mod\_init\_func\) and the script asserts the late registration cannot change the instructions of the object.

### Completion criteria

- The kernel links with libShengPlatformPower.a force-loaded and keeps the original AMFI and PMGR dispatch unchanged.

### Current limits

- The instrument is a refusal-first integration, not a functional power backend, and is not runtime qualified \(runtime\_qualified = false in its build report\).

### Next action

- Read the sheng-pmgr=2 output on the first boot and record which slots refuse.

### Evidence

- `source`: [guarded PMGR provider that inherits only the original AON slots](https://github.com/donyanchen/UniXNU-piano/blob/167776dc0cbee63c190abbbf0a556981ac8aaba1/package/ShengPlatformPower.cpp)
- `source`: [candidate-backed audit, original bindings and late registration of the PMGR archive](https://github.com/donyanchen/UniXNU-piano/blob/167776dc0cbee63c190abbbf0a556981ac8aaba1/scripts/build-sheng-platform-power.py)

## Image assembly {#packaging}

`planned`

Components: `DarwinBoot`, `XnuPrelink`, `SoftwareAES`.

### Hardware and dependencies

- The linked XNU kernel, the prelink tool at kits/XnuPrelink, the iPadOS 17.7.11 kernelcache as the prelink hash reference, and the DarwinBoot booter.

### Configuration

- \[kernel.prelink\] tool = kits/XnuPrelink/emit\_prelink.py, kernel = build/xnu/ios-obj/DEVELOPMENT\_ARM64\_BCM2837/mach.development.bcm2837.unstripped.noctf, slide = -0x1000000.
- \[kernel.prelink\].kernelcache\_sha256 pins the 21H461 kernelcache; \[kernel.prelink\].roots lists the eleven IOKit and kext roots the prelink closure keeps.
- \[bootimg\] embed\_payload = true, partition = unixnu, lba 44928768..61705983 at 4096 bytes per LBA, with OS and SystemOS windows.

### Procedure

- Run ./unixnu build kernel -D ../device, then ./unixnu build package -D ../device.
- Run ./unixnu build firmware --uefi ../uefi/deps/Mu-Silicium, ./unixnu build payload -D ../device and ./unixnu bootimg -D ../device.

### Development findings

- The kernel links and prelinks successfully on the macOS runner: kernel.macho sha256 4c9dcef0... was produced in run 42755922774.
- The DarwinBoot firmware package registers the board store hooks and the VerifiedRoot policy archive \(5e6b930\).
- The payload requires the linked kernel to carry the sheng PMGR integration; dropping CONFIG\_XNU\_SHENG\_PMGR or the archive makes it fail with 'native UFS root kernel lacks the linked sheng PMGR integration'.
- The boot image targets a unixnu partition, but the device currently has only userdata, super and metadata. The Partition Manager layout and the DSU-style approach of the Pagani port are both still open.

### Completion criteria

- Kernel and prelink succeed, the payload contains every declared input, and boot.img matches the bootloader format and size limit.

### Current limits

- payload and bootimg have not completed yet, and no boot img has been flashed or RAM-booted.

### Next action

- Complete the payload and bootimg steps, then decide between a unixnu partition and a DSU-style RAM boot before touching the device.

### Evidence

- `source`: [prelink tool, kernel path, slide, roots and the boot image partition geometry](https://github.com/donyanchen/UniXNU-piano/blob/167776dc0cbee63c190abbbf0a556981ac8aaba1/board.toml)
- `source`: [kernel, package, firmware and payload steps pass on run 42812944686 \(head 0c76f70\); the payload step emits payload/payload.img at 160 MiB and the hardware device tree at device-tree/hardware.dtb, and the boot image step takes both --uefi and --dtb because it compiles BootShim, runs the Mu-Silicium mkbootimg.py and embeds the device tree in the image header](https://github.com/donyanchen/UniXNU-piano/blob/167776dc0cbee63c190abbbf0a556981ac8aaba1/.github/workflows/package-bare-metal.yml)
- `source`: [bootimg rejected run 42816650617 with 'the ARM64 image header does not describe the shim plus the firmware volume': the pinned Mu-Silicium writes FD\_SIZE alone into the image\_size field \(0x300000\), while bootimg requires len\(shim\) + FD\_SIZE \(0x300070\). The patch sets the field to 'FD\_SIZE + \_Payload - \_Head'. It also writes 0 into the text\_offset field instead of FD\_BASE, because piano's ABL reads text\_offset as a displacement from the load address: the absolute 0xA7100000 made it place the image outside its reservation and the tablet returned to fastboot with a black screen after 'Booting OKAY'. The stock piano kernel reports text\_offset 0x0; an aarch64-none-elf build of the patched shim gives 112 shim bytes with \_Payload at 0x70, text\_offset 0x0 and image\_size 0x300070](https://github.com/donyanchen/UniXNU-piano/blob/167776dc0cbee63c190abbbf0a556981ac8aaba1/patches/uefi/bootshim-image-size.patch)
- `source`: [piano's DeviceBootManagerAfterConsole starts the ESP loader and AndroidBoot and never starts UniXNU.efi, so the menu the board builds into its own firmware volume is unreachable even when UEFI runs. The patch calls StartFvApp with UniXNU.efi's FILE\_GUID \(9B665204-A133-47A2-9396-9E2B370A4E25\) before the ESP and Android fallbacks](https://github.com/donyanchen/UniXNU-piano/blob/167776dc0cbee63c190abbbf0a556981ac8aaba1/patches/uefi/piano-start-unixnu.patch)
- `source`: [Mu-Silicium SEC overwrites x0 before it reads it, so the device tree pointer the Android bootloader passes is lost; UniXNURamDiskDxe then reports 'no entry argument HOB' and never publishes the payload volume, which leaves the boot menu without an entry. The patch keeps x0 in x19 across the platform initialisation, passes it to SecEntry and builds the DAEE82E6-8090-4E72-BFB9-78C13CD4E359 HOB once the HOB list exists \(the same fix the marble port needed\)](https://github.com/donyanchen/UniXNU-piano/blob/167776dc0cbee63c190abbbf0a556981ac8aaba1/patches/uefi/mu-sec-entry-arg.patch)
- `source`: [bootimg.py required text\_offset to equal FD\_BASE, which is the Mu-Silicium convention, while the ARM64 specification defines the field as a displacement from the load address and piano's ABL reads it that way \(its stock kernel reports 0\). The shim now writes 0, so the patch accepts 0 or the firmware base and keeps the image-size check strict](https://github.com/donyanchen/UniXNU-piano/blob/167776dc0cbee63c190abbbf0a556981ac8aaba1/patches/unixnu-bootimg-text-offset.patch)
- `source`: [\[bootimg.image\] kernel\_compression = none follows uefi/piano.toml \[boot\_image\_kernel\] kernel\_compression = none; without it bootimg falls back to its gzip default for a board that asks for an uncompressed kernel field](https://github.com/donyanchen/UniXNU-piano/blob/167776dc0cbee63c190abbbf0a556981ac8aaba1/board.toml)

## Diagnostics {#diagnostics}

`planned`

Components: `VerifiedRoot`, `AppleKeyStoreState`.

### Hardware and dependencies

- UEFI serial output, the XNU verbose boot log, and the boot\_progress\_poll weak stub added in d185787.

### Configuration

- CONFIG\_XNU\_EARLY\_BOOT\_PROGRESS is enabled; CONFIG\_XNU\_BOOT\_PROGRESS is not set.
- \[payload\].kernel\_args carries -v, debug=0x14e, startup\_debug=0 and pagani-platform-status=1.

### Procedure

- Capture the UEFI serial console during fastboot boot.
- Read the panic and progress lines from the captured output.

### Development findings

- The early boot progress path needs boot\_progress\_poll, which a weak stub provides until a board implementation exists \(d185787\).
- Several patch series add panic output for early boot \(zzzz-early-boot-progress, zzzzz-root-panic-progress, zzzz-boot-progress-panic-output\), so a failure before serial init still reaches the screen.
- piano has no serial console, so the first UEFI boots gave no evidence about the payload: UniXNURamDiskDxe publishes nothing and the menu only said 'no boot entry found'. scripts/prepare-unixnu-diagnostics.py rewrites that line during packaging so it reads 'payload volume missing' or 'config unreadable', which separates a missing initrd handoff from an unreadable FAT volume without any cabling.

### Completion criteria

- Each claimed milestone has a reproducible command, a matching image revision and an accessible result.

### Current limits

- No serial capture of a device boot exists yet.

### Next action

- Set up a serial or pstore capture before the first RAM boot.

### Evidence

- `source`: [makes the built-in fallback message report whether the payload volume is reachable, so a board without a serial console can be diagnosed from the menu alone](https://github.com/donyanchen/UniXNU-piano/blob/167776dc0cbee63c190abbbf0a556981ac8aaba1/scripts/prepare-unixnu-diagnostics.py)
- `source`: [early boot progress and panic output patches applied to the XNU tree](https://github.com/donyanchen/UniXNU-piano/blob/167776dc0cbee63c190abbbf0a556981ac8aaba1/patches/xnu/series)

</div>
