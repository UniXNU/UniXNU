# Redmi K20 Pro / Mi 9T Pro \(raphael, SM8150\) - arm64 port of iPadOS 18.7.12 \(22H390\). Kernel from the arm64 iPadOS restore, root image from the iOS 18.7.12 paylo \(Aruvelut-123\)

[Aruvelut-123/UniXNU-raphael](https://github.com/Aruvelut-123/UniXNU-raphael)

<div v-pre>

Redmi K20 Pro / Mi 9T Pro \(raphael, SM8150\) arm64 UniXNU port. Target build is ipados-18.7.12-22H390 \(Darwin 24.6.0\): the root image comes from the iOS 18.7.12 restore of iPhone11,2, the arm64 kernelcache from the iPadOS 18.7.12 restore of iPad7,11. Configuration and image-assembly tooling are in place; kernel, firmware and every hardware area still need device verification.

Source record: [porting.toml](https://github.com/Aruvelut-123/UniXNU-raphael/blob/577e2ceda172e41aad295deeda99f4eb3fb823e3/porting.toml), `577e2ceda172e41aad295deeda99f4eb3fb823e3`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `implemented` |
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

`implemented`

Components: `ArmDTPlatform`.

### Hardware and dependencies

- SM8150 device identity and partition plan from the raphael board configuration
- OS profile ipados-18.7.12-22H390 \(arm64\) carried by this repository and installed into the UniXNU checkout
- iOS 18.7.12 payload IPSW and the staged iPadOS 18.7.12 arm64 kernelcache, both build 22H390
- Shared SM8150 support pinned in feeds.toml

### Configuration

- format 2 board: soc\_source=sm8150, kit=raphael, os\_profile=ipados-18.7.12-22H390
- upstream UniXNU has no 18.x profile, so os-profiles/ipados-18.7.12-22H390/ is copied in by scripts/install-device-profile.py
- the arm64 kernelcache is staged by scripts/stage-arm64-kernelcache.py into the path \[kernel.prelink\] kernelcache names
- kernel fragments arch:configs/common.config and soc:configs/sm8150.config
- arm64e-only profiles are intentionally not mapped: SM8150 has no FEAT\_PAuth

### Procedure

- From the UniXNU checkout: python3 ../UniXNU-raphael/scripts/install-device-profile.py --unixnu .
- python3 ../UniXNU-raphael/scripts/stage-arm64-kernelcache.py --unixnu .
- ./unixnu defconfig raphael\_defconfig -D ../UniXNU-raphael, ./unixnu fetch -D ../UniXNU-raphael, then ./unixnu status --json -D ../UniXNU-raphael

### Development findings

- arm64e-only Apple OS profiles \(iPadOS 26/27\) cannot run on this SoC \(no FEAT\_PAuth\); iPadOS 18 still ships an arm64 kernelcache because the no-PAC A10 iPad 7 runs it
- UniXNU reads exactly one IPSW per run, so the iOS payload is \[ipsw\] and the arm64 kernelcache is passed to prelink by path instead
- iPadOS and iOS share the 22H390 build ID, so the staged kernelcache needs its own output path or the two would overwrite each other in out/ipsw/22H390/
- both 22H390 dmgs are AEA encrypted, so building the root image needs macOS /usr/bin/aea
- status resolves arch=arm64, soc=sm8150, os=ipados-18.7.12-22H390 and the device board.toml

### Completion criteria

- Every profile root, source pin, component closure and patch order resolves without error

### Current limits

- Resolution success is not a boot result; nothing here has run on raphael hardware

### Next action

- Record the resolved status output as host evidence once the CI build produces it

### Evidence

- `source`: [Format 2 board definition with the arm64 ipados-18.7.12-22H390 profile \(iOS 18.7.12 payload for the root image, staged iPadOS 18.7.12 arm64 kernelcache for prelink\) and raphael\_defconfig mapping.](https://github.com/Aruvelut-123/UniXNU-raphael/blob/577e2ceda172e41aad295deeda99f4eb3fb823e3/board.toml)
- `source`: [Pinned shared SM8150 source used as the soc profile.](https://github.com/Aruvelut-123/UniXNU-raphael/blob/577e2ceda172e41aad295deeda99f4eb3fb823e3/feeds.toml)

## Firmware and boot {#firmware}

`planned`

Components: `DarwinBoot`.

### Hardware and dependencies

- Mu-Silicium platform support for SM8150
- Device memory map and reserved regions for the firmware volume

### Configuration

- package/firmware is a placeholder: no DSC, FDF or platform code exists yet

### Procedure

- Add UniXNU, UniXNUDxe, DarwinBoot, UniXNURamDiskDxe, DiskIoDxe and FatPkg to the DSC and FDF, then run ./unixnu build firmware --uefi ../uefi-raphael

### Development findings

- Firmware integration is documented upstream but no raphael platform port exists in this repository

### Completion criteria

- A firmware volume builds and UniXNU draws its boot menu on raphael

### Current limits

- Without a firmware volume only kernel, EFI package and boot image can be produced

### Next action

- Create the uefi-raphael Mu-Silicium platform with the required DSC and FDF modules

### Evidence

Collect evidence using the next action.

## CPU and interrupts {#cpu}

`planned`

Components: `XnuPrelink`.

### Hardware and dependencies

- CPU topology for SM8150 \(four Cortex-A76 plus four Cortex-A55\) from the vendor DTS

### Configuration

- raphael\_defconfig carries the kernel options; CPU enablement is not yet wired to a device tree

### Procedure

- Build the kernel, boot it and capture the CPU bring-up log

### Development findings

- SM8150 Cortex-A76 and A55 do not implement ARMv8.3 FEAT\_PAuth, which is why arm64e is excluded

### Completion criteria

- All eight CPUs come up and the interrupt controller delivers timer interrupts

### Current limits

- No device log exists yet; the CPU area is unverified on hardware

### Next action

- Boot the arm64 kernel and record the per-CPU startup log

### Evidence

Collect evidence using the next action.

## Memory and DMA {#memory}

`planned`

### Hardware and dependencies

- RAM size and reserved region plan for raphael

### Configuration

- dts/raphael.dts declares a 4 GiB memory node; reservations are not yet described

### Procedure

- Extend the device tree with the reserved-memory nodes and boot the kernel

### Development findings

- Boot page table capacity for the native 4 KiB granule is handled by the arch profile patches, not by this device

### Completion criteria

- XNU maps the full RAM range and the reserved regions stay out of the kernel map

### Current limits

- The current device tree is a skeleton and has not been used for a boot

### Next action

- Add reserved-memory nodes for firmware, display and modem regions

### Evidence

Collect evidence using the next action.

## Storage and root {#storage}

`planned`

### Hardware and dependencies

- GPT entry for the root partition, from the device partition table
- Shared SM8150 UFS operations from the pinned SoC repository

### Configuration

- Root image is built with ./unixnu build userdata from the board partition geometry and the OS profile's IPSW
- scripts/build-root.sh prefers a unixnu partition label and falls back to userdata at flash time

### Procedure

- scripts/build-root.sh --ipsw restore.ipsw --dry-run, then --flash

### Development findings

- UniXNU selects root by APFS volume UUID written into the ADT, so a boot-time partition search is not available
- Kernel and root image must be the same build \(22H390 here\); the root is the iOS 18.7.12 payload and the kernelcache the same-build iPadOS 18.7.12 arm64 one, and builds must never be mixed across Darwin versions
- the payload dmgs are AEA encrypted, so the root image can only be assembled on macOS

### Completion criteria

- XNU mounts the root volume read-only and starts launchd

### Current limits

- No root image has been built or flashed for this device yet

### Next action

- Decrypt the iOS 18.7.12 OS dmg on macOS and fill \[root\] os\_volume\_uuid and systemos\_volume\_uuid in the board's OS profile
- Download the payload IPSW once and fill the \[ipsw.sha256\] member pins

### Evidence

Collect evidence using the next action.

## Display {#display}

`planned`

### Hardware and dependencies

- Panel timing and DSI configuration for the raphael panel

### Configuration

- No display nodes are described in the device tree yet

### Procedure

- Boot the kernel and capture the framebuffer handoff log

### Development findings

- GopFramebuffer is not selected for this board, so there is no handoff path yet

### Completion criteria

- The kernel console and SpringBoard both render on the panel

### Current limits

- Display is unverified; no panel timing has been collected

### Next action

- Collect panel timings and add a display node plus the framebuffer component

### Evidence

Collect evidence using the next action.

## Input {#input}

`planned`

### Hardware and dependencies

- GT9889 touch controller wiring and I2C address

### Configuration

- No input driver is selected or declared

### Procedure

- Integrate a HID provider and verify touch events in userspace

### Development findings

- Touch bring-up has not started; the upstream raphael port has an independent GT9889 note

### Completion criteria

- Touch events reach userspace and SpringBoard responds

### Current limits

- No input hardware work exists in this repository

### Next action

- Select a HID input component and record its required inputs

### Evidence

Collect evidence using the next action.

## GPU {#gpu}

`planned`

### Hardware and dependencies

- Adreno 640 firmware and command stream interface

### Configuration

- No GPU component is selected

### Procedure

- Add the Adreno component chain and verify a userspace Metal or Vulkan probe

### Development findings

- The Adreno driver family exists upstream but no raphael GPU work has been done here

### Completion criteria

- A GPU client allocates a buffer and completes a queue submission

### Current limits

- GPU is unverified and unstarted

### Next action

- Review the Adreno component catalog entries for SM8150 compatibility

### Evidence

Collect evidence using the next action.

## Network {#network}

`planned`

### Hardware and dependencies

- WCN3990 Wi-Fi and Bluetooth firmware plus calibration data

### Configuration

- No network driver is selected

### Procedure

- Add the wireless component chain and verify an association and a Bluetooth HCI open

### Development findings

- Network bring-up has not started

### Completion criteria

- The device associates with an access point and reports an interface to userspace

### Current limits

- No network hardware work exists in this repository

### Next action

- Identify the WCN3990 firmware and calibration inputs for raphael

### Evidence

Collect evidence using the next action.

## Audio {#audio}

`planned`

### Hardware and dependencies

- Audio DSP firmware and codec wiring for raphael

### Configuration

- No audio component is selected

### Procedure

- Add audio components and verify playback from userspace

### Development findings

- Audio bring-up has not started

### Completion criteria

- A userspace client plays audio through the device speaker

### Current limits

- No audio hardware work exists in this repository

### Next action

- Collect the DSP firmware inputs from the vendor partition

### Evidence

Collect evidence using the next action.

## Power {#power}

`planned`

### Hardware and dependencies

- PMIC and regulator topology for raphael

### Configuration

- No power component is selected

### Procedure

- Add the power component chain and verify rail state across a suspend and resume

### Development findings

- Power management has not started

### Completion criteria

- The device suspends and resumes without losing the framebuffer

### Current limits

- No power hardware work exists in this repository

### Next action

- Record the PMIC topology from the vendor device tree

### Evidence

Collect evidence using the next action.

## Image assembly {#packaging}

`planned`

### Hardware and dependencies

- Kernel, payload and device tree produced by the build steps
- IPSW disk image or a raw root image to convert

### Configuration

- scripts/build.sh runs defconfig, fetch, status, kernel, package, firmware and bootimg in order
- scripts/ipsw\_to\_sparse.py converts a raw image to libsparse chunks and self-verifies the result

### Procedure

- python3 scripts/ipsw\_to\_sparse.py --raw-image userdata-root.img --output unixnu.sparse
- scripts/build.sh for the full artifact chain

### Development findings

- Sparse output is produced only from a raw image; AEA-encrypted IPSW payloads need macOS tooling and the script reports that instead of emitting a bad image

### Completion criteria

- boot.img and UniXNU.efi are produced and published as separate artifacts

### Current limits

- No boot.img or UniXNU.efi has been built from this device configuration on hardware

### Next action

- Produce both artifacts in CI and attach the resulting log as host evidence

### Evidence

Collect evidence using the next action.

## Diagnostics {#diagnostics}

`planned`

### Hardware and dependencies

- Serial or UART access path for raphael, or a framebuffer console fallback

### Configuration

- No log transport is configured for this device

### Procedure

- Capture firmware and kernel output during a boot attempt and attach it as device evidence

### Development findings

- Log capture is required before any hardware area can move past planned

### Completion criteria

- A boot attempt produces a readable log that is committed as evidence

### Current limits

- No log has been captured for this port

### Next action

- Configure a log transport and record the first boot attempt output

### Evidence

Collect evidence using the next action.

</div>
