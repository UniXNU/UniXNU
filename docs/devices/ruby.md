# Xiaomi Redmi Note 12 Pro 5G \(ruby, MediaTek Dimensity 1080 / MT6877\)

[lky005/UniXNU-ruby](https://github.com/lky005/UniXNU-ruby)

<div v-pre>

Catalog identity for the ruby \(Redmi Note 12 Pro 5G, MT6877\) XNU 8796 + iPhone X iOS 16.7.16 \(20H392\) userland bring-up. Public main documents the verified 0179 line \(v0.5.0 at 22cdb29; current main b3c704f\); the native EINT14 touch path is verified, G7/G8 and a full 10 min repeat were not run. The implementation, build recipe and device evidence live in lky005/ruby-ios-bringup. This repository selects no UniXNU components and does not claim a UniXNU UEFI or format-2 build.

Source record: [porting.toml](https://github.com/lky005/UniXNU-ruby/blob/9f6dc15b3d52b26fb4436b060ff238e6a8c78da8/porting.toml), `9f6dc15b3d52b26fb4436b060ff238e6a8c78da8`.

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

- MT6877 board identity, iPhone X iOS 16.7.16 \(20H392\) userland, XNU 8796 recipe and the 0179 patchset from lky005/ruby-ios-bringup.

### Configuration

- board.name = ruby; board.soc = MT6877; board.os\_profile = ios-16.7.16-20H392; \[components\].include = \[\].
- No SoC source, kit, defconfig, firmware or package section is selected in this catalog repository.

### Procedure

- Read README.md and follow the pinned links to the main repository.
- Use the main repository xnu-0179 workflow as the build gate; this repository has no CI.

### Development findings

- Public main is the 0179 line: patchset 10b1e2e8 \(175 files\), exec-data a4fb021e and image d438ba47; v0.5.0 is anchored at 22cdb29 and the current main is b3c704f.
- The 0179 device gates passed G1-G6; the 8-failure soft reset logged no-ack and G7/G8 plus a full 10 min repeat were cancelled by decision.

### Completion criteria

- The catalog identity matches the main repository and the generated device page links to the pinned record.

### Current limits

- This repository is not a UniXNU build tree; it has no configs, patches, firmware, package or component sources.

### Next action

- None for this line; future P2c/P3 changes get their own record.

### Evidence

- `source`: [Public device identity, current pins and the documented 0179 line.](https://github.com/lky005/ruby-ios-bringup/blob/main/README.md)
- `host`: [xnu-0179 workflow success on main; the kernel patchset 10b1e2e8 and exec-data a4fb021e gates passed.](https://github.com/lky005/ruby-ios-bringup/actions/runs/42232048852)
  Command: <code>gh run view 42232048852 --repo lky005/ruby-ios-bringup</code>. Revision: `b3c704ff5c16ced6fe252bd6fbdada7236f1a56a`.
- `host`: [host-checks workflow success on main.](https://github.com/lky005/ruby-ios-bringup/actions/runs/42232048946)
  Command: <code>gh run view 42232048946 --repo lky005/ruby-ios-bringup</code>. Revision: `b3c704ff5c16ced6fe252bd6fbdada7236f1a56a`.

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

- The XNU kernel is built for the MT6877 CPU/GIC/timer topology; the pinned 0179 image boots on the author's unit.

### Procedure

- Boot the 0179 image and inspect the boot log and GIC/timer initialization.

### Development findings

- Public STATUS records six Cortex-A55 cores, 16K pages, GICv3 and timers.
- 0179 ships the native EINT14 consumer: SPI288 -&gt; RubyGIC INTID 288 -&gt; child controller -&gt; oneshot WorkLoop; G1-G6 passed.

### Completion criteria

- All enabled CPUs boot and the GIC/timer path reaches userland.

### Current limits

- CPU frequency policy, secondary-core power and thermal behavior are not verified by this record.

### Next action

- Record per-core entry and timer/IPI checks in a future clean run; not part of the P2b gates.

### Evidence

- `source`: [6x Cortex-A55, 16K pages, GICv3, timers and the 0179 native EINT line are part of the verified boot.](https://github.com/lky005/ruby-ios-bringup/blob/main/docs/records/STATUS.md)

## Memory and DMA {#memory}

`implemented`

### Hardware and dependencies

- 128 MiB boot image, MT6877 memory map and the HFS+ root/rescue layout.

### Configuration

- The boot image and root layout are pinned in the main repository; no SMMU or DMA ownership is claimed here.

### Procedure

- Boot the 0179 image and inspect the handoff and root layout.

### Development findings

- Public STATUS documents the 128 MiB boot image, UFS root and a 4 MB HFS rescue root.

### Completion criteria

- The handoff reaches a working HFS+ root and the rescue root path.

### Current limits

- DMA widths, SMMU ownership and memory reservations are not independently audited by this record.

### Next action

- No additional memory-map claim; the P2b gates did not audit DMA/SMMU.

### Evidence

- `source`: [Public architecture documentation of the boot image and root layout.](https://github.com/lky005/ruby-ios-bringup/blob/main/docs/en/01-architecture.md)

## Storage and root {#storage}

`implemented`

### Hardware and dependencies

- MT6877 UFS LUN 2, HFS+ iosroot and the LK ramdisk slot for the md0 rescue root.

### Configuration

- The root is HFS+ on UFS LUN 2; the rescue root is a 4 MB HFS image in the LK ramdisk slot.

### Procedure

- Boot the 0179 image; mount iosroot read/write; boot the rescue image and run the /etc/rc checks.

### Development findings

- Public STATUS records read/write HFS+ on iosroot and 8/8 rescue /etc/rc checks from md0.

### Completion criteria

- The UFS root mounts read/write and the rescue root completes its checks.

### Current limits

- No UniXNU storage component, UFS driver kit or format-2 userdata window is selected in this repository.

### Next action

- Keep the root recipe in the main repository; do not duplicate storage code here.

### Evidence

- `source`: [UFS LUN 2 HFS+ root read/write and the md0 rescue-root 8/8 checks.](https://github.com/lky005/ruby-ios-bringup/blob/main/docs/records/STATUS.md)

## Display {#display}

`implemented`

### Hardware and dependencies

- MT6877 display path, LK framebuffer and the IOSurface/IOMFB bridge.

### Configuration

- The kernel presents IOSurface/IOMFB frames to the LK framebuffer at 1080x2400.

### Procedure

- Boot the 0179 image and observe SpringBoard on the panel; the public demo shows the home screen.

### Development findings

- Public README/STATUS record IOSurface/IOMFB -&gt; LK framebuffer at 1080x2400 and a live SpringBoard.
- The demo clip was captured on the 0084 build; it is not a 0179 display claim.

### Completion criteria

- The panel shows the iOS userland and the home screen.

### Current limits

- No GPU acceleration, external display or backlight control is claimed.

### Next action

- Re-capture the demo on 0179 or a later line.

### Evidence

- `source`: [Public 12 s demo of the SpringBoard home screen on the 0084 build.](https://github.com/lky005/ruby-ios-bringup/blob/main/media/autoswipe.mp4)

## Input {#input}

`device-verified`

### Hardware and dependencies

- Goodix GT9916R touch panel on EINT14 \(edge falling\) with the SPI288 parent, and the volume/power keys.

### Configuration

- The 0179 line boots with the native EINT14 oneshot service \(rubyeint=1, rubyeintb1=1, rubykpdirq=1\); gt\_thread is removed and commands run on the IOCommandGate. The 0085 bit-bang poll is historical.

### Procedure

- Boot the 0179 image; touch the panel; observe EINT14 oneshot active/enabled and HID down/up; press the volume down key; run eint status and gt diag.

### Development findings

- Public STATUS records G1-G6; first 10 min isr 2381-&gt;6004, ok 5997, fail 7; \~5 min stress isr 8672-&gt;13282, ok 12866, fail +9; 1-5-finger frames; no panic/stuck/re-activation.
- G7/G8 and a full 10 min repeat were cancelled by decision; the 8-failure soft reset logged no-ack and the ok path is not proven; no ESD timer.

### Completion criteria

- Native EINT14 touch and the hardware keys reach userland on the 0179 image.

### Current limits

- G7/G8, a full 10 min repeat, the soft-reset ok path and ESD/silent-stuck recovery are not claimed.

### Next action

- No additional gate for this line; future P2c/P3 changes get their own record.

### Evidence

- `device`: [0179 device run: G1-G6, first 10 min + \~5 min stress; native EINT14 HID and volume-down key; no panic/stuck/re-activation.](https://github.com/lky005/ruby-ios-bringup/blob/main/docs/records/STATUS.md)
  Command: <code>boot the 0179 image; touch the panel; eint status; gt diag; press volume down</code>. Revision: `b3c704ff5c16ced6fe252bd6fbdada7236f1a56a`.

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

- `source`: [GPU is listed among the not-yet-implemented peripherals.](https://github.com/lky005/ruby-ios-bringup/blob/main/docs/records/STATUS.md)

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

- `source`: [Wi-Fi, Bluetooth and cellular are listed among the not-yet-implemented peripherals.](https://github.com/lky005/ruby-ios-bringup/blob/main/docs/records/STATUS.md)

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

- `source`: [Audio is listed among the not-yet-implemented peripherals.](https://github.com/lky005/ruby-ios-bringup/blob/main/docs/records/STATUS.md)

## Power {#power}

`device-verified`

### Hardware and dependencies

- MT6360 PMIC battery/charger read-only path over I2C5; KPD/TOPSTATUS keys.

### Configuration

- The 0179 line keeps the read-only MT6360 path verified in the 0155 run; it does not write PMIC, charger or rail registers.

### Procedure

- Battery status was verified in the 0155 run and is carried in the 0179 line; the P2b G1-G6 gates focused on touch/IRQ.

### Development findings

- Public STATUS records 0155 battery OCV 4311 mV, CHG 0xa2 FULL, FOD 0x94 external, external=1/full=1, 8/8 I2C5 arbiter and no PMIC/charger/rail writes.
- Battery UI latency \(P2.4, 30 s poll, 100-&gt;98 on unplug\) remains open; Type-C is read-only.

### Completion criteria

- Battery/charger state is read correctly without writing PMIC or charger registers.

### Current limits

- No charger control, OTG, Type-C role or battery UI latency fix is claimed.

### Next action

- Keep the read-only boundary until a separately approved charger-control change.

### Evidence

- `device`: [0155 device run: 4311 mV, external=1/full=1, 8/8 I2C5 arbiter, no PMIC/charger/rail writes.](https://github.com/lky005/ruby-ios-bringup/blob/main/docs/records/STATUS.md)
  Command: <code>battery status (0155 run; carried into the 0179 line)</code>. Revision: `e81510fd7cf75ba1c8a3ee81749c53a2e16df41d`.

## Image assembly {#packaging}

`implemented`

### Hardware and dependencies

- 128 MiB Android boot image layout, pinned kernel/ADT/shim inputs and deterministic host pipeline.

### Configuration

- The main repository assembles the boot image and records the kernel, exec-data, payload and image hashes.

### Procedure

- Follow the main repository reproduction steps with config/0179.env.

### Development findings

- Public README records patchset 10b1e2e8, kernel full 2b008e52, exec-data a4fb021e, image d438ba47 and payload 72fc737c.
- The boot image itself is not published in the repository.

### Completion criteria

- The host pipeline reproduces the pinned image layout and hashes.

### Current limits

- This catalog repository does not package or publish a boot image.

### Next action

- None; the 0179 image is pinned.

### Evidence

- `source`: [Public reproduction steps for the pinned 0179 boot image.](https://github.com/lky005/ruby-ios-bringup/blob/main/docs/en/09-reproduce.md)

## Diagnostics {#diagnostics}

`device-verified`

### Hardware and dependencies

- USB CDC console, SWEETLOG ring decoder and the read-only eint/gt diagnostic commands.

### Configuration

- The diagnostic path is read-only; it does not write PMIC, rail, clock or WDT registers.

### Procedure

- Boot the 0179 image; use eint status and gt diag over the USB 0x2E channel; decode the SWEETLOG ring with tools/sweetlog/decode.py.

### Development findings

- 0179 runs used eint status/gt diag and recorded G1-G6; the 19/19 read-only probe, eight I2C5 arbiter steps and six snapshots were verified in the 0155 run and remain historical.
- Occasional EP0 0x2E EPIPE is recovered by checking the done counter, re-sending once, or re-enumerating the USB device.

### Completion criteria

- The read-only diagnostic path and console ring decode work on the 0179 image.

### Current limits

- The 19-command probe was not re-run on 0179; no charger control, PMIC writes or complete peripheral inventory is provided.

### Next action

- Keep the diagnostic path read-only; no additional diagnostic gate for this line.

### Evidence

- `device`: [0179: G1-G6 and eint/gt diagnostics; 0155: 19/19 probe, 8/8 I2C5 arbiter, no panic.](https://github.com/lky005/ruby-ios-bringup/blob/main/docs/records/STATUS.md)
  Command: <code>eint status; gt diag (0179 device run)</code>. Revision: `b3c704ff5c16ced6fe252bd6fbdada7236f1a56a`.

</div>
