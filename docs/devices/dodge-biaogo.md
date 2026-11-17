# OnePlus 13 / dodge / PJZ110: format 2 port \(Biaogo\)

[Biaogo/UniXNU-dodge](https://github.com/Biaogo/UniXNU-dodge)

<div v-pre>

OnePlus 13 PJZ110 \(dodge, SM8750\). Skip Setup and turn the on-screen HUD off for normal use. Display, touch, storage boot, and GPU scanout are device-observed. Network, audio, and long-term stability are not claimed.

Source record: [porting.toml](https://github.com/Biaogo/UniXNU-dodge/blob/e9f298d0c6b66a7aa22eca1a3c2852227dfff309/porting.toml), `e9f298d0c6b66a7aa22eca1a3c2852227dfff309`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `implemented` |
| [Firmware and boot](#firmware) | `implemented` |
| [CPU and interrupts](#cpu) | `implemented` |
| [Memory and DMA](#memory) | `implemented` |
| [Storage and root](#storage) | `implemented` |
| [Display](#display) | `implemented` |
| [Input](#input) | `implemented` |
| [GPU](#gpu) | `implemented` |
| [Network](#network) | `not-applicable` |
| [Audio](#audio) | `not-applicable` |
| [Power](#power) | `implemented` |
| [Image assembly](#packaging) | `implemented` |
| [Diagnostics](#diagnostics) | `implemented` |

## Configuration {#configuration}

`implemented`

Components: `NativeKeyStoreEvents`.

### Hardware and dependencies

- OnePlus 13 PJZ110, OPLUS codename dodge, SM8750, iPadOS 17.7.11 \(21H461\).

### Configuration

- schema\_version=2. Board name dodge. Defconfig dodge\_defconfig.

### Procedure

- From a UniXNU checkout: defconfig dodge\_defconfig -D &lt;this repository&gt;; fetch; status.

### Development findings

- The published board name is dodge. Process logs stay in the private backup.

### Completion criteria

- board.toml, feeds, and the defconfig name the same device.

### Current limits

- This record does not publish private build logs or device identifiers.

### Next action

- Keep the public tree limited to the files needed to build and boot.

### Evidence

- `source`: [Board name, SoC, and OS profile are dodge / SM8750 / ipados-17.7.11-21H461.](https://github.com/Biaogo/UniXNU-dodge/blob/e9f298d0c6b66a7aa22eca1a3c2852227dfff309/board.toml)

## Firmware and boot {#firmware}

`implemented`

Components: `PaganiDarwinBoot`.

### Hardware and dependencies

- Embedded UEFI payload. Firmware binaries are not stored in this repository.

### Configuration

- The boot image embeds the payload. Firmware hashes stay in proprietary-files.txt.

### Procedure

- Build firmware, then payload and bootimg from the selected device tree.

### Development findings

- Temporary boot is the supported trial path. Do not flash the partition that holds the installed system.

### Completion criteria

- Firmware publishes a framebuffer and the documented memory reservations.

### Current limits

- The standard initrd path is not separately claimed.

### Next action

- Keep firmware blobs out of the public tree.

### Evidence

- `source`: [Required firmware inputs are listed by hash, not embedded.](https://github.com/Biaogo/UniXNU-dodge/blob/e9f298d0c6b66a7aa22eca1a3c2852227dfff309/proprietary-files.txt)

## CPU and interrupts {#cpu}

`implemented`

Components: `PaganiArmCpu`, `PaganiArmDTPlatform`.

### Hardware and dependencies

- SM8750 CPU topology and GICv3 from the board device tree.

### Configuration

- Eight CPUs are selected by the board kernel arguments.

### Procedure

- Resolve the device tree, then build the kernel with the device patch series.

### Development findings

- The board boots far enough to reach Setup and the desktop on this device.

### Completion criteria

- All selected CPUs come online without a scheduler lock panic.

### Current limits

- Sustained multi-core stress is not claimed.

### Next action

- Leave scheduler experiments in the private tree.

### Evidence

- `source`: [The board DTS identifies OnePlus 13 PJZ110 on SM8750.](https://github.com/Biaogo/UniXNU-dodge/blob/e9f298d0c6b66a7aa22eca1a3c2852227dfff309/dts/dodge.dts)

## Memory and DMA {#memory}

`implemented`

Components: `NativeRamBlock`.

### Hardware and dependencies

- Board memory window from the device tree.

### Configuration

- RAM disk and reserved ranges follow board.toml.

### Procedure

- Build the payload with the selected RAM Data input. Do not commit that input.

### Development findings

- The desktop path uses the packed RAM disk already selected by the board.

### Completion criteria

- The kernel accepts the documented memory window.

### Current limits

- A larger allocation is not claimed.

### Next action

- Do not publish RAM Data images.

### Evidence

- `source`: [Memory and payload settings stay in the board file.](https://github.com/Biaogo/UniXNU-dodge/blob/e9f298d0c6b66a7aa22eca1a3c2852227dfff309/board.toml)

## Storage and root {#storage}

`implemented`

Components: `NativeUfs`, `NativeVirtioBlock`, `PaganiVerifiedRoot`, `NativeAES`.

### Hardware and dependencies

- UFS root and a packed APFS RAM disk. Partition images are local inputs.

### Configuration

- native-ufs-root=1 and offline-apfs-load=1.

### Procedure

- Prepare RAM Data locally, then build payload and bootimg.

### Development findings

- The device reaches userspace from the packed root. Erase can reboot. Swipe-to-power-off can power off.

### Completion criteria

- Root mount and shutdown do not hit the dead-parent vnode underflow.

### Current limits

- Write qualification of the installed userdata partition is not claimed.

### Next action

- Keep backup and shrink tools in the private tree.

### Evidence

- `source`: [The device patch series includes the dead-parent vnode fix.](https://github.com/Biaogo/UniXNU-dodge/blob/e9f298d0c6b66a7aa22eca1a3c2852227dfff309/patches/xnu/series)

## Display {#display}

`implemented`

Components: `NativeMobileDisplay`, `PaganiPanel`.

### Hardware and dependencies

- OnePlus 13 panel timing and the legacy framebuffer.

### Configuration

- Panel and legacy display arguments are in board.toml. Normal use turns the HUD off.

### Procedure

- Boot with the published arguments. Skip Setup. Disable the on-screen HUD.

### Development findings

- With the HUD off, the low frame-rate symptom is resolved for normal use on this device.

### Completion criteria

- The panel shows Setup and the desktop without the diagnostic overlay.

### Current limits

- This record does not publish frame traces or probe output.

### Next action

- Keep display probes in the private tree.

### Evidence

- `source`: [Panel and peripheral wiring is board-owned.](https://github.com/Biaogo/UniXNU-dodge/blob/e9f298d0c6b66a7aa22eca1a3c2852227dfff309/package/PaganiPeripherals.h)

## Input {#input}

`implemented`

Components: `PaganiInput`, `QcomGeniSpi`.

### Hardware and dependencies

- Buttons and the board touch controller.

### Configuration

- pagani-buttons=1 and pagani-touch=1.

### Procedure

- Boot and confirm buttons and touch after Setup is skipped.

### Development findings

- Touch and buttons are usable on the device-observed desktop path.

### Completion criteria

- Press, release, and basic navigation work.

### Current limits

- Gesture coverage and long sessions are not claimed.

### Next action

- Do not publish touch-debug captures.

### Evidence

- `source`: [Input rails and the touch bus are described with the board peripherals.](https://github.com/Biaogo/UniXNU-dodge/blob/e9f298d0c6b66a7aa22eca1a3c2852227dfff309/package/PaganiPeripherals.h)

## GPU {#gpu}

`implemented`

Components: `Adreno830`, `AdrenoNext`.

### Hardware and dependencies

- SM8750 Adreno 830. The Metal addon is a local input and is not stored here.

### Configuration

- GPU handoff and the addon switch are in board.toml. Color correction stays on the scanout path.

### Procedure

- Supply the addon locally, build payload, and boot.

### Development findings

- GPU scanout is part of the device-observed path. Later GPU probes stay private.

### Completion criteria

- Frames reach the panel through the GPU handoff without falling back to the CPU copy.

### Current limits

- Addon binaries, pipeline caches, and shader packs are not published.

### Next action

- Keep addon build history in the private repository.

### Evidence

- `source`: [The A830 kernel components are selected by this device repository.](https://github.com/Biaogo/UniXNU-dodge/blob/e9f298d0c6b66a7aa22eca1a3c2852227dfff309/components.toml)

## Network {#network}

`not-applicable`

### Hardware and dependencies

- No network controller is selected.

### Configuration

- No network component is enabled.

### Procedure

- Do not claim Wi-Fi, cellular, or USB networking from this tree.

### Development findings

- Network is outside this publication.

### Completion criteria

- No network component is required for the published boot path.

### Current limits

- Network is not implemented here.

### Next action

- Add a network area only when a controller is selected.

### Evidence

Collect evidence using the next action.

## Audio {#audio}

`not-applicable`

### Hardware and dependencies

- No audio controller is selected.

### Configuration

- No audio component is enabled.

### Procedure

- Do not claim speaker, headphone, or microphone support.

### Development findings

- Audio is outside this publication.

### Completion criteria

- No audio component is required for the published boot path.

### Current limits

- Audio is not implemented here.

### Next action

- Add an audio area only when a controller is selected.

### Evidence

Collect evidence using the next action.

## Power {#power}

`implemented`

Components: `ShengPlatformPower`, `Sm8750Platform`.

### Hardware and dependencies

- PSCI system off and reset.

### Configuration

- Shutdown uses the platform halt path.

### Procedure

- Verify erase reboot and swipe-to-power-off on a temporary boot.

### Development findings

- Erase can reboot. Swipe-to-power-off can power the device off.

### Completion criteria

- The halt timer calls the platform restart path before panic.

### Current limits

- Battery gauge and charging control are not claimed.

### Next action

- Do not publish power-management probe logs.

### Evidence

- `source`: [The device patch series includes the platform halt and reset timeout fix.](https://github.com/Biaogo/UniXNU-dodge/blob/e9f298d0c6b66a7aa22eca1a3c2852227dfff309/patches/xnu/series)

## Image assembly {#packaging}

`implemented`

Components: `NativePrelink`.

### Hardware and dependencies

- Kernel, trust cache, RAM Data, and optional GPU addon. Only the source pins are published.

### Configuration

- Output is out/dodge/ipados-17.7.11-21H461/dodge/.

### Procedure

- defconfig, fetch, kernel, payload, bootimg. Keep generated images out of git.

### Development findings

- The public tree does not contain IPSW, kernelcache, trust cache, RAM Data, or addon binaries.

### Completion criteria

- A temporary boot image can be assembled from local inputs.

### Current limits

- Image bytes are not part of this repository.

### Next action

- Ignore generated output.

### Evidence

- `source`: [Source pins are recorded without build products.](https://github.com/Biaogo/UniXNU-dodge/blob/e9f298d0c6b66a7aa22eca1a3c2852227dfff309/feeds.toml)

## Diagnostics {#diagnostics}

`implemented`

Components: `BootProgress`, `Stage7Probe`.

### Hardware and dependencies

- Boot progress can draw an overlay. Normal use does not need it.

### Configuration

- Turn the HUD off after Setup. Do not publish probe switches.

### Procedure

- Skip Setup, then disable the HUD.

### Development findings

- The usable path is skip Setup and HUD off. Probe history stays in the private backup.

### Completion criteria

- The desktop remains usable with the HUD disabled.

### Current limits

- This repository does not publish HUD captures or probe logs.

### Next action

- Remove probe code from the public tree only after the boot path no longer references it.

### Evidence

- `source`: [The public instructions name the device and keep process history out of this record.](https://github.com/Biaogo/UniXNU-dodge/blob/e9f298d0c6b66a7aa22eca1a3c2852227dfff309/README.md)

</div>
