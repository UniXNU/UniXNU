# Lenovo Xiaoxin Pad Pro GT \(TB710FU\)

[bmk-keyeast/UniXNU-tb710fu](https://github.com/bmk-keyeast/UniXNU-tb710fu)

<div v-pre>

Lenovo Xiaoxin Pad Pro GT \(TB710FU\) port. Board DTS generated from mainline Linux; UEFI built from the device's own firmware; boot and vendor\_boot images built, not yet booted.

Source record: [porting.toml](https://github.com/bmk-keyeast/UniXNU-tb710fu/blob/23235249d71604f8a6f743680ef8fd1003fe7189/porting.toml), `23235249d71604f8a6f743680ef8fd1003fe7189`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `host-verified` |
| [Firmware and boot](#firmware) | `implemented` |
| [CPU and interrupts](#cpu) | `planned` |
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

`host-verified`

Components: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`, `DarwinBoot`.

### Hardware and dependencies

- SM8650 shared support from loolooc/UniXNU-sm8650-common \(pinned commit\); arm64 iPadOS 17.7.11 profile as on houji and caihong.

### Configuration

- board.toml: soc\_source sm8650, os\_profile ipados-17.7.11-21H461, defconfig tb710fu\_defconfig \(meizu21 values\), payload 64 MiB, owned\_memory\_size 0x80000000.

### Procedure

- ./unixnu defconfig tb710fu\_defconfig -D ../UniXNU-tb710fu; ./unixnu fetch; ./unixnu status --json; CI build.yml kernel job on macos-26.

### Development findings

- The configuration resolves and the XNU kernel \(xnu-10063.141.1 with the SM8650 patch series\) builds and prelinks against the iPadOS 17.7.11 kernelcache in about 10 minutes.
- The bootstrap pass ends in an expected link error \(mockfs symbols\) before the archives exist; the step result is the final build.
- payload.panic\_screen = true \(no UART on the tablet\); CI runs the AVB selftest and syntax-checks every script.
- kernel\_args add ramoops=0xac340000 and ramoops\_reset\_after=120; CI runs tests/run-ramoops-test.sh.
- logs/ \(pulled ramoops/pstore logs\) is ignored by git, like firmware-dump/ and images/.

### Completion criteria

- All source pins resolve; every selected component has a record; status shows the intended overrides and patch order.

### Current limits

- macOS needs a separate OS profile \(macOS-ForSheng approach\); no SM8650 macOS profile exists.

### Next action

- Boot the images on the unlocked device; switch the OS profile after storage and display work.

### Evidence

- `host`: [kernel job success; kernel.macho Mach-O sha256 edb98193a248...](https://github.com/bmk-mikufan/UniXNU-tb710fu/actions/runs/42738403553)
  Command: <code>./unixnu build kernel -j $(sysctl -n hw.ncpu)</code>. Revision: `a28f8b97df73988506594c8ccca3c67f461b418c`.

## Firmware and boot {#firmware}

`implemented`

### Hardware and dependencies

- Device partitions dumped read-only over adb \(uefi\_a, xbl\_a, xbl\_config\_a, abl\_a, imagefv\_a, uefisecapp\_a, vendor\_boot\_a, boot\_a, dtbo\_a\) with sizes checked against the block devices.
- uefi\_a: ELF with one FV, BOOT.MXF.2.1-02000-LANAI-1; 100 DXE INFs extracted with UEFIReader \(duplicate Ebl renamed instead of aborting\).

### Configuration

- uefi/Platforms/Lenovo/tb710fuPkg from Mu-Silicium giulia \(SM8650, LanaiPkg\); Lenovo SMBIOS; framebuffer 3200x2000 \(mainline NT36532 panel\); SOC\_TYPE only selects SMBIOS strings.
- UniXNU.inf, UniXNUDxe, UniXNURamDiskDxe, DarwinBoot in DSC and FDF; UniXNULib and FdtLib mapped; built on UniXNU/uefi-sheng for the SEC FDT handoff.

### Procedure

- UEFIReader uefi\_a.img tb710fu; copy uefi/ over uefi-sheng; ./unixnu build firmware --uefi ../uefi-tb710fu.

### Development findings

- The giulia references resolve against the TB710FU blobs except OplusProject and OnePlus panel XMLs, which were dropped.
- uefiplat.cfg matches giulia's configuration map except EnableDisplayThread/EnableDisplayImageFv \(kept 0 as in Silicium\).
- SILICIUM\_UEFI.fd builds at exactly 0x300000 with all four UniXNU modules \(WSL, clang 18\).
- scripts/dump-firmware.sh also dumps vbmeta and takes SLOT=\_b for the inactive slot \(read-only\); scripts/sign-images.sh signs from the slot-a dumps \(vbmeta\_a, boot\_a\).
- First device boot \(2026-11-11, slot b, locked ABL\): ABL accepted the testkey chain and BootShim started Mu-Silicium; the framebuffer showed DxeCore 'Loading driver at' lines, then the panel went black with the backlight on and nothing else appeared. pstore was empty afterwards. This matches sheng's PORTING.md for its vendor drivers \(panel blanks at ClockDxe\). The APRIORI list also loaded GLinkDxe, which DXE.inc marks as crashing.
- TB710FU\_VENDOR\_HW \(DSC, default 0\) gates every Binaries/tb710fu DXE and RamManagerDxe and sets PcdBuildXblHobs FALSE, as in sheng. Without RamManagerDxe, the UEFI has only the MemoryMapLib DXE\_Heap \(432 MiB\) as conventional memory.
- With TB710FU\_VENDOR\_HW = 0 the device reaches the UniXNU menu with the payload \(kits 0, drivers 0 is normal\), and the 3 s timeout starts the xnu entry. DarwinBoot then returned Out of Resources: the 2 GiB owned window had no conventional run. MemoryMapLib therefore maps RAM\_High \(0x8C0000000 + 3 GiB, DDR in the live FDT\) as Conv. Buttons do nothing without the vendor PMIC drivers.

### Completion criteria

- Firmware image builds, enters UniXNU, publishes the framebuffer and preserves the documented memory reservations.

### Current limits

- The vendor-driver build blanks the panel; the Mu-only build has no UFS, USB or clocks in UEFI. Firmware blobs are not redistributed.

### Next action

- Boot the TB710FU\_VENDOR\_HW = 0 image from slot b; check the UniXNU menu and the payload line; then re-add vendor drivers in groups to find the one that blanks the panel.

### Evidence

- `source`: [board package with UniXNU integration](https://github.com/bmk-keyeast/UniXNU-tb710fu/blob/23235249d71604f8a6f743680ef8fd1003fe7189/uefi/Platforms/Lenovo/tb710fuPkg/tb710fu.dsc)

## CPU and interrupts {#cpu}

`planned`

### Hardware and dependencies

- Identify the cpu and interrupts hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for cpu and interrupts.

### Procedure

- Follow the cpu and interrupts stage in the porting guide and record the actual commands.

### Development findings

- Collect the first cpu and interrupts observation, its cause when established, and the resulting implementation decision.

### Completion criteria

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU.

### Current limits

- Hardware inputs and implementation are pending for this example board.

### Next action

- Inventory the required cpu and interrupts inputs before implementation.

### Evidence

Collect evidence using the next action.

## Memory and DMA {#memory}

`implemented`

### Hardware and dependencies

- Reserved memory from the mainline sm8650-lenovo-tb710fu.dtb; stock UEFI memory map from the DTB embedded in xbl\_config; DDR banks from /sys/firmware/fdt.

### Configuration

- dts/tb710fu.dts generated by scripts/gen-board-dts.py: 37 mainline regions plus display-demura@a3600000 and display-reserved@d5100000; /memory = 0x8c0000000 + 5 GiB.
- MemoryMapLib: PIL\_Reserved 0x16F80000 and Display\_Demura from the stock map; DXE\_Heap ends at 0xD3000000.

### Procedure

- scripts/gen-board-dts.py LINUX\_DTB LIVE\_FDT; scripts/stock-memory-map.py xbl\_config\_a.img MemoryMapLib.c; scripts/check-memory-map.py.

### Development findings

- DDR is split: 2 GiB at 0x80000000 and 6 GiB at 0x880000000 with secure holes \(MemTotal 7.4 GiB, 8 GB SKU\). XNU manages one contiguous window, so the largest run 0x8c0000000-0xa00000000 is the /memory node.
- The mainline board DT puts rmtfs at 0xd3000000, inside the stock DXE heap \(stock Android allocates rmtfs dynamically\).
- Display\_Demura \(0xA3600000, 43 MiB\) exists only in the stock UEFI map; mainline does not reserve it.

### Completion criteria

- All handoff regions are accounted for and each enabled DMA engine accesses its allocated range with the documented cache policy.

### Current limits

- The 2 GiB owned window is the caihong value; the UEFI free map on this device is not observed yet.

### Next action

- Read the DarwinBoot window address on the first boot; try a larger owned\_memory\_size after root works.

### Evidence

- `source`: [generated board DTS; compiles against the SoC DTSI in CI](https://github.com/bmk-keyeast/UniXNU-tb710fu/blob/23235249d71604f8a6f743680ef8fd1003fe7189/dts/tb710fu.dts)

## Storage and root {#storage}

`planned`

### Hardware and dependencies

- Identify the storage and root hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for storage and root.

### Procedure

- Follow the storage and root stage in the porting guide and record the actual commands.

### Development findings

- Collect the first storage and root observation, its cause when established, and the resulting implementation decision.

### Completion criteria

- Host: register, clock, link and SMMU facts match the board inventory.
- Reads: SCSI capacity, GPT and known blocks are correct; OS/SystemOS windows stay within userdata.
- Root: the configured volume mounts and launchd starts. Persistence: writes survive reboot within the allocated Data region.

### Current limits

- Hardware inputs and implementation are pending for this example board.

### Next action

- Inventory the required storage and root inputs before implementation.

### Evidence

Collect evidence using the next action.

## Display {#display}

`planned`

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

- Hardware inputs and implementation are pending for this example board.

### Next action

- Inventory the required display inputs before implementation.

### Evidence

Collect evidence using the next action.

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

- Collect the first gpu observation, its cause when established, and the resulting implementation decision.

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

`implemented`

### Hardware and dependencies

- Stock boot\_a: header v4, ramdisk 0 \(GKI\). Stock vendor\_boot\_a: header v4, ramdisk at 0x1000000, DTB 0x317e5d bytes at 0x1f00000.
- Bootloader stays locked \(LTBox root\). Stock vbmeta is signed with the AOSP testkey \(2597c218...\); it chains boot \(rollback location 3\) to the testkey and carries a hash descriptor for vendor\_boot.

### Configuration

- Payload in vendor\_boot with --ramdisk-addr 0x2400000; boot.img with --ramdisk none and the live FDT as firmware DTB.

### Procedure

- ./unixnu build payload; ./unixnu vendor\_boot --stock vendor\_boot\_a.img --ramdisk payload.img --ramdisk-addr 0x2400000; ./unixnu bootimg --uefi ../uefi-tb710fu --dtb live-fdt.dtb --ramdisk none.
- scripts/sign-images.sh firmware-dump images -&gt; images/slot-b; scripts/flash-slot-b.sh images/slot-b \[--write\].

### Development findings

- boot.img 2228224 bytes; vendor\_boot.img 100663296 bytes \(the partition size\) with the 64 MiB payload; the payload holds kernel.macho and kernel.macho.adt, no trust cache or Data seed yet.
- A locked bootloader refuses fastboot boot and flash, so the images are signed for the testkey path and written to slot b from rooted Android \(LTBox EDL partition writes are the recovery path\).
- scripts/avb/avbsign.py rehash recomputes vbmeta hash descriptors; on the stock vbmeta the init\_boot descriptor equals sha256\(salt + init\_boot\[:size\]\), and the rehashed vendor\_boot descriptor \(70365184 bytes\) matches the built image.
- patches/xnu/tb710fu-ramoops-console.patch applies on the 61-patch arm64/SM8650/iPadOS 17 series \(git apply --check on xnu d8b80295\).
- The stock slot-b chain is mixed firmware: vbmeta\_b's vendor\_boot descriptor matches vendor\_boot\_a, its dtbo descriptor matches neither dtbo\_a nor dtbo\_b. vbmeta\_a matches dtbo\_a, init\_boot\_a and vendor\_boot\_a, and chains vbmeta\_system to the testkey, so slot b is built as slot a's chain plus the UniXNU boot/vendor\_boot and a re-signed vbmeta\_a \(shared with the tb710fu-arch-linux E2 design\).
- A simulated slot b \(images/slot-b + dtbo\_a + init\_boot\_a\) passes tb710fu-arch-linux build/avbcheck.py; boot\_b verifies against the testkey with rollback index 1736035200.
- adb exec-in can return before the device-side dd finishes; the flash path now runs on the tablet \(scripts/android/flash-slot-b.sh, from tb710fu-arch-linux\) with cmp verification.
- Real AOSP libavb avb\_slot\_verify \(tb710fu-arch-linux build/avbverify, locked, testkey only, partitions boot/dtbo/vendor\_boot/init\_boot\) returns OK on images/slot-b plus slot a's dtbo, init\_boot, vbmeta\_system and recovery, with the device rollback floors 0/1/1780617600/1736035200.
- Qualcomm ABL \(SM8650 VerifiedBoot.c GetOsVerAndSecPactchLevel, found by the tb710fu-arch-linux session\) reads com.android.build.boot.os\_version/security\_patch from the boot vbmeta and falls back to the boot header os\_version, refusing 0. The UniXNU boot.img header carries 0x200001a7 \(16, 2026-07\), so it passed either way; sign-images.sh now copies boot\_a's properties \(14, 2025-01-05\) with avbsign.py footer --props-from so the OS version handed to the TEE matches stock, and fails when the property is missing. The ABL-emulating build/avbverify harness returns OK for the new slot b.
- PVMFW\_BCC ABL builds add pvmfw to the avb\_slot\_verify request when the partition holds an image \(HasPvmFw\); its hash descriptor is in vbmeta\_system, so copying vbmeta\_system\_a without pvmfw\_a fails verification \(tb710fu-arch-linux found it; their E1 then passed ABL on the device\). The flash path copies pvmfw from slot a; the build/avbverify harness returns ERROR\_VERIFICATION for UniXNU slot b with the old pvmfw\_b and OK with pvmfw\_a.
- After AVB, ABL's UpdateDeviceTree\(\) fails BootLinux \(fastboot fallback\) when the selected DTB lacks /, /memory, /chosen, /reserved-memory or /soc/cache-controller \(LLCC, SCT DDR\); the mainline DTB names it system-cache-controller and stalled the Linux E2 boot. UniXNU keeps the stock vendor\_boot DTBs: tb710fu-arch-linux build/dtcheck.py passes on the msm-id 0x2b8 entry ABL selects.

### Completion criteria

- The signed images boot from slot b, the menu lists the xnu entry and DarwinBoot hands off.

### Current limits

- Not booted. Slot b currently holds the tb710fu-arch-linux E2 set \(written 18:31, after the UniXNU writes\); UniXNU images are written again only after the user assigns slot b.
- ABL loads a 70365184-byte vendor\_boot \(stock 11.9 MB, mostly the 64 MiB FAT payload\); whether ABL caps the vendor ramdisk size is unknown, and libavb success does not cover ABL's image loading \(a header-v2 boot passed libavb yet was rejected\).
- The GKI init\_boot ramdisk is appended after the 64 MiB FAT payload; UniXNURamDiskDxe reads the FAT from initrd-start, but this is unverified on TB710FU.

### Next action

- Agree slot-b ownership with the Linux session, then scripts/flash-slot-b.sh \(dry run\), scripts/flash-slot-b.sh images/slot-b --write; the user activates slot b.

### Evidence

- `source`: [build, signing and test commands](https://github.com/bmk-keyeast/UniXNU-tb710fu/blob/23235249d71604f8a6f743680ef8fd1003fe7189/README.md)
- `source`: [selftest covers footer, rekey and rehash](https://github.com/bmk-keyeast/UniXNU-tb710fu/blob/23235249d71604f8a6f743680ef8fd1003fe7189/scripts/avb/avbsign.py)

## Diagnostics {#diagnostics}

`implemented`

### Hardware and dependencies

- Host-side checks for the hardware description.

### Configuration

- scripts/check-memory-map.py fails when a UEFI Conv region overlaps a no-map DTS region; every script carries a --selftest run in CI.

### Procedure

- python3 scripts/check-memory-map.py; CI build.yml checks job.

### Development findings

- The check caught the giulia DXE\_Heap overlapping the TB710FU rmtfs at 0xd3000000.
- Kernel console mirrored into the stock Android ramoops console zone \(live DT ramoops\_region 0xac300000, 1 MiB, console 0x40000 at 0xac340000 after the dmesg zone, ecc-size 16\) in the fs/pstore/ram\_core.c format: DBGC header, ring, RS\(255\) parity per 128-byte block plus header parity \(poly 0x11d, fcr 0, prim 1\). Hooked at \_cnputc, so console, printf and panic text all reach it; output before arm\_vm\_init is buffered \(4 KiB\) and replayed. A panic flushes, waits ramoops\_panic\_delay and issues PSCI SYSTEM\_RESET; ramoops\_reset\_after resets a hung boot. tests/run-ramoops-test.sh builds the writer from the patch with ASan/UBSan and checks every codeword has zero syndromes, append across boots, ring wrap and no-ECC mode.
- scripts/read-ramoops.sh reads /sys/fs/pstore from rooted Android; --check prints the stock ramoops module parameters, --mark proves a reset keeps the zone. Not run on the device yet.

### Completion criteria

- Every check runs in CI and fails on a regression.

### Current limits

- No device-side diagnostics yet.

### Next action

- Add log capture once the UniXNU menu runs on the device.

### Evidence

- `source`: [overlap check with selftest](https://github.com/bmk-keyeast/UniXNU-tb710fu/blob/23235249d71604f8a6f743680ef8fd1003fe7189/scripts/check-memory-map.py)

</div>
