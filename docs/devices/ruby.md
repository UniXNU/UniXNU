# Xiaomi Redmi Note 12 Pro 5G \(ruby, MediaTek Dimensity 1080 / MT6877\)

[lky005/UniXNU-ruby](https://github.com/lky005/UniXNU-ruby)

<div v-pre>

Catalog identity for the ruby \(Redmi Note 12 Pro 5G, MT6877\) XNU 8796 + iPhone X iOS 16.7.16 \(20H392\) userland bring-up. Public main documents the verified 0155 line; p3-eint-hal \(0160, ruby\_eint/EINT14\) is in development. The implementation, build recipe and device evidence live in lky005/ruby-ios-bringup. This repository selects no UniXNU components and does not claim a UniXNU UEFI or format-2 build.

Source record: [porting.toml](https://github.com/lky005/UniXNU-ruby/blob/d321b43deae0fba70f3fd566fa25d41648b7bf82/porting.toml), `d321b43deae0fba70f3fd566fa25d41648b7bf82`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `host-verified` |
| [Firmware and boot](#firmware) | `not-applicable` |
| [CPU and interrupts](#cpu) | `implemented` |
| [Memory and DMA](#memory) | `implemented` |
| [Storage and root](#storage) | `implemented` |
| [Display](#display) | `implemented` |
| [Input](#input) | `device-verified` |
| [GPU](#gpu) | `planned` |
| [Network](#network) | `planned` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `device-verified` |
| [Image assembly](#packaging) | `implemented` |
| [Diagnostics](#diagnostics) | `device-verified` |

## Configuration {#configuration}

`host-verified`

### Hardware and dependencies

- MT6877 board identity, iPhone X iOS 16.7.16 \(20H392\) userland, XNU 8796 recipe and the 0155 patchset from lky005/ruby-ios-bringup.

### Configuration

- board.name = ruby; board.soc = MT6877; board.os\_profile = ios-16.7.16-20H392; \[components\].include = \[\].
- No SoC source, kit, defconfig, firmware or package section is selected in this catalog repository.

### Procedure

- Read README.md and follow the pinned links to the main repository.
- Use the main repository xnu-0155 workflow as the build gate; this repository has no CI.

### Development findings

- Public main is the 0155 line: patchset da13b6df \(151 files\), exec-data 2e98fd85 and image 3b44c0e2.
- The development branch p3-eint-hal \(0160\) adds ruby\_eint and wires EINT14 into the touch thread; its CI builds are green, but this record does not claim a 0160 device gate.

### Completion criteria

- The catalog identity matches the main repository and the generated device page links to the pinned record.

### Current limits

- This repository is not a UniXNU build tree; it has no configs, patches, firmware, package or component sources.

### Next action

- Merge the 0160 line to main and refresh the public status links after its device gate is published.

### Evidence

- `source`: [Public device identity, current pins and the documented 0155 line.](https://github.com/lky005/ruby-ios-bringup/blob/main/README.md)
- `host`: [xnu-0155 workflow success on main; the kernel patchset and exec-data gate passed.](https://github.com/lky005/ruby-ios-bringup/actions/runs/41362698995)
  Command: <code>gh run view 41362698995 --repo lky005/ruby-ios-bringup</code>. Revision: `e81510fd7cf75ba1c8a3ee81749c53a2e16df41d`.
- `host`: [host-checks workflow success on main.](https://github.com/lky005/ruby-ios-bringup/actions/runs/41362698921)
  Command: <code>gh run view 41362698921 --repo lky005/ruby-ios-bringup</code>. Revision: `e81510fd7cf75ba1c8a3ee81749c53a2e16df41d`.

## Firmware and boot {#firmware}

`not-applicable`

### Hardware and dependencies

- Stock LK bootloader and a 128 MiB Android boot image; no UniXNU UEFI firmware.

### Configuration

- UEFI firmware is not used; the boot chain is stock LK -&gt; boot image -&gt; XNU.

### Procedure

- Follow the main repository reproduction steps for the LK boot image.

### Development findings

- The port does not use the UniXNU UEFI framework or DarwinBoot; the 128 MiB boot image layout is the boot contract.

### Completion criteria

- Not applicable: the board is outside the UniXNU UEFI boot model.

### Current limits

- No UEFI firmware volume, DSC/FDF, firmware defines or PSCI handoff is produced by this repository.

### Next action

- Keep UEFI out of scope unless the project changes boot model.

### Evidence

- `source`: [The public architecture chapter documents stock LK -&gt; XNU -&gt; iOS userland, not a UEFI boot.](https://github.com/lky005/ruby-ios-bringup/blob/main/docs/en/01-architecture.md)

## CPU and interrupts {#cpu}

`implemented`

### Hardware and dependencies

- Six Cortex-A55 cores, GICv3, ARM generic timers and 16K pages.

### Configuration

- The XNU kernel is built for the MT6877 CPU/GIC/timer topology; the pinned 0155 image boots on the author's unit.

### Procedure

- Boot the 0155 image and inspect the boot log and GIC/timer initialization.

### Development findings

- Public STATUS records six Cortex-A55 cores, 16K pages, GICv3 and timers.
- EINT work checks GIC SPI256 -&gt; INTID288 read-only before arming; the public 0155 line does not yet ship the EINT14 consumer.

### Completion criteria

- All enabled CPUs boot and the GIC/timer path reaches userland.

### Current limits

- CPU frequency policy, secondary-core power and thermal behavior are not verified by this record.

### Next action

- Record per-core entry and timer/IPI checks from a clean 0160 build after it lands on main.

### Evidence

- `source`: [6x Cortex-A55, 16K pages, GICv3 and timers are part of the verified boot.](https://github.com/lky005/ruby-ios-bringup/blob/main/STATUS.md)

## Memory and DMA {#memory}

`implemented`

### Hardware and dependencies

- 128 MiB boot image, MT6877 memory map and the HFS+ root/rescue layout.

### Configuration

- The boot image and root layout are pinned in the main repository; no SMMU or DMA ownership is claimed here.

### Procedure

- Boot the 0155 image and inspect the handoff and root layout.

### Development findings

- Public STATUS documents the 128 MiB boot image, UFS root and a 4 MB HFS rescue root.

### Completion criteria

- The handoff reaches a working HFS+ root and the rescue root path.

### Current limits

- DMA widths, SMMU ownership and memory reservations are not independently audited by this record.

### Next action

- Add the memory map and reservation evidence when the 0160 line is published.

### Evidence

- `source`: [Public architecture documentation of the boot image and root layout.](https://github.com/lky005/ruby-ios-bringup/blob/main/docs/en/01-architecture.md)

## Storage and root {#storage}

`implemented`

### Hardware and dependencies

- MT6877 UFS LUN 2, HFS+ iosroot and the LK ramdisk slot for the md0 rescue root.

### Configuration

- The root is HFS+ on UFS LUN 2; the rescue root is a 4 MB HFS image in the LK ramdisk slot.

### Procedure

- Boot the 0155 image; mount iosroot read/write; boot the rescue image and run the /etc/rc checks.

### Development findings

- Public STATUS records read/write HFS+ on iosroot and 8/8 rescue /etc/rc checks from md0.

### Completion criteria

- The UFS root mounts read/write and the rescue root completes its checks.

### Current limits

- No UniXNU storage component, UFS driver kit or format-2 userdata window is selected in this repository.

### Next action

- Keep the root recipe in the main repository; do not duplicate storage code here.

### Evidence

- `source`: [UFS LUN 2 HFS+ root read/write and the md0 rescue-root 8/8 checks.](https://github.com/lky005/ruby-ios-bringup/blob/main/STATUS.md)

## Display {#display}

`implemented`

### Hardware and dependencies

- MT6877 display path, LK framebuffer and the IOSurface/IOMFB bridge.

### Configuration

- The kernel presents IOSurface/IOMFB frames to the LK framebuffer at 1080x2400.

### Procedure

- Boot the 0155 image and observe SpringBoard on the panel; the public demo shows the home screen.

### Development findings

- Public README/STATUS record IOSurface/IOMFB -&gt; LK framebuffer at 1080x2400 and a live SpringBoard.
- The demo clip was captured on the 0084 build; it is not a 0160 display claim.

### Completion criteria

- The panel shows the iOS userland and the home screen.

### Current limits

- No GPU acceleration, external display or backlight control is claimed.

### Next action

- Re-capture the demo on the 0160 line after it is published.

### Evidence

- `source`: [Public 12 s demo of the SpringBoard home screen on the 0084 build.](https://github.com/lky005/ruby-ios-bringup/blob/main/media/autoswipe.mp4)

## Input {#input}

`device-verified`

### Hardware and dependencies

- Goodix GT9916R touch panel on bit-bang SPI3 and the volume/power keys.

### Configuration

- The 0155 line boots with the real touch driver \(sweetgt=1\); volume/power keys arrive through HID.

### Procedure

- Boot the 0155 image; touch the panel; observe SWEET GT initialization and HID down/up; press the volume and power keys.

### Development findings

- Public STATUS records real GT9916R HID down/up, 11+ HID lines, volume-down KPD, power/volume-up TOPSTATUS 0x2a and zero PMIC writes.
- EINT14 touch events are a 0159/0160 development feature, not a public 0155 claim.

### Completion criteria

- Real touch and the hardware keys reach userland on the 0155 image.

### Current limits

- Multi-touch gestures beyond the documented two-contact dispatch and the EINT14 event path are not claimed for public main.

### Next action

- Publish the 0160 EINT14 device gate before adding it to this record.

### Evidence

- `device`: [0155 device run: real GT9916R touch HID, 11+ HID lines, volume/power keys, 19/19 probe and no panic.](https://github.com/lky005/ruby-ios-bringup/blob/main/STATUS.md)
  Command: <code>boot the 0155 image; touch the panel; observe SWEET GT and HID down/up; press the volume and power keys</code>. Revision: `e81510fd7cf75ba1c8a3ee81749c53a2e16df41d`.

## GPU {#gpu}

`planned`

### Hardware and dependencies

- MT6877 Mali-G68 MC4 GPU; no driver is selected.

### Configuration

- No GPU driver, firmware or userland acceleration is configured.

### Procedure

- Not started.

### Development findings

- Public STATUS lists GPU as not yet implemented.

### Completion criteria

- A GPU driver and on-device composition are verified.

### Current limits

- No GPU acceleration, Metal or external display support exists in the current line.

### Next action

- Keep GPU in the P3 target; do not add a placeholder component to this catalog repository.

### Evidence

- `source`: [GPU is listed among the not-yet-implemented peripherals.](https://github.com/lky005/ruby-ios-bringup/blob/main/STATUS.md)

## Network {#network}

`planned`

### Hardware and dependencies

- MT6877 Wi-Fi/Bluetooth/cellular hardware; no driver is selected.

### Configuration

- No Wi-Fi, Bluetooth or cellular driver is configured.

### Procedure

- Not started.

### Development findings

- Public STATUS lists Wi-Fi, Bluetooth and cellular as not yet implemented.

### Completion criteria

- A network driver and on-device connectivity are verified.

### Current limits

- No wireless or cellular support exists in the current line.

### Next action

- Keep network work in the P3 target; do not add a placeholder component here.

### Evidence

- `source`: [Wi-Fi, Bluetooth and cellular are listed among the not-yet-implemented peripherals.](https://github.com/lky005/ruby-ios-bringup/blob/main/STATUS.md)

## Audio {#audio}

`planned`

### Hardware and dependencies

- MT6877 audio codec and DSP paths; no driver is selected.

### Configuration

- No audio codec, DSP or routing is configured.

### Procedure

- Not started.

### Development findings

- Public STATUS lists audio as not yet implemented.

### Completion criteria

- Playback and recording work on the device.

### Current limits

- No audio support exists in the current line.

### Next action

- Keep audio work in the P3 target; do not add a placeholder component here.

### Evidence

- `source`: [Audio is listed among the not-yet-implemented peripherals.](https://github.com/lky005/ruby-ios-bringup/blob/main/STATUS.md)

## Power {#power}

`device-verified`

### Hardware and dependencies

- MT6360 PMIC battery/charger read-only path over I2C5; KPD/TOPSTATUS keys.

### Configuration

- The 0155 line reads battery/charger state read-only; it does not write PMIC, charger or rail registers.

### Procedure

- Boot the 0155 image; run 'battery status'; read the SWEET BATTERY line and the I2C5 arbiter counters.

### Development findings

- Public STATUS records OCV 4311 mV, CHG 0xa2 FULL, FOD 0x94 external, external=1/full=1, 8/8 I2C5 arbiter and no PMIC/charger/rail writes.
- Battery UI latency \(P2.4, 30 s poll, 100-&gt;98 on unplug\) remains open; Type-C is read-only.

### Completion criteria

- Battery/charger state is read correctly without writing PMIC or charger registers.

### Current limits

- No charger control, OTG, Type-C role or battery UI latency fix is claimed.

### Next action

- Keep the read-only boundary until a separately approved charger-control change.

### Evidence

- `device`: [0155 device run: 4311 mV, external=1/full=1, 8/8 I2C5 arbiter, no PMIC/charger/rail writes.](https://github.com/lky005/ruby-ios-bringup/blob/main/STATUS.md)
  Command: <code>battery status</code>. Revision: `e81510fd7cf75ba1c8a3ee81749c53a2e16df41d`.

## Image assembly {#packaging}

`implemented`

### Hardware and dependencies

- 128 MiB Android boot image layout, pinned kernel/ADT/shim inputs and deterministic host pipeline.

### Configuration

- The main repository assembles the boot image and records the kernel, exec-data, payload and image hashes.

### Procedure

- Follow the main repository reproduction steps with config/0155.env.

### Development findings

- Public README records patchset da13b6df, kernel full 491f2373, exec-data 2e98fd85, image 3b44c0e2 and payload a00dd751.
- The boot image itself is not published in the repository.

### Completion criteria

- The host pipeline reproduces the pinned image layout and hashes.

### Current limits

- This catalog repository does not package or publish a boot image.

### Next action

- Record the 0160 image hashes when that line lands on main.

### Evidence

- `source`: [Public reproduction steps for the pinned 0155 boot image.](https://github.com/lky005/ruby-ios-bringup/blob/main/docs/en/09-reproduce.md)

## Diagnostics {#diagnostics}

`device-verified`

### Hardware and dependencies

- USB CDC console, SWEETLOG ring decoder and the 19-command read-only board probe.

### Configuration

- The diagnostic path is read-only; it does not write PMIC, rail, clock or WDT registers.

### Procedure

- Boot the 0155 image; run the 19-command read-only probe over the USB console; decode the SWEETLOG ring with tools/sweetlog/decode.py.

### Development findings

- Public STATUS records 19/19 probe commands, 8/8 I2C5 arbiter, six snapshots and no panic.

### Completion criteria

- The probe completes read-only and the log decoder recovers the console ring.

### Current limits

- The probe is read-only; it does not provide charger control, PMIC writes or a complete peripheral inventory.

### Next action

- Keep the diagnostic path read-only; add EINT status only after the 0160 gate is public.

### Evidence

- `device`: [0155 device run: 19/19 probe, 8/8 I2C5 arbiter, six snapshots, no panic.](https://github.com/lky005/ruby-ios-bringup/blob/main/STATUS.md)
  Command: <code>run the 19-command read-only probe over the USB console</code>. Revision: `e81510fd7cf75ba1c8a3ee81749c53a2e16df41d`.

</div>
