# Xiaomi 10 Ultra \(cas\)

[ht94911/UniXNU-cas](https://github.com/ht94911/UniXNU-cas)

<div v-pre>

Xiaomi 10 Ultra: UEFI menu and CPU0 platform start verified; moving to the standard UniXNU build with a UFS root, eight CPUs and touch.

Source record: [porting.toml](https://github.com/ht94911/UniXNU-cas/blob/5cba1411b76170abf027e312afee15669b9541d9/porting.toml), `5cba1411b76170abf027e312afee15669b9541d9`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `implemented` |
| [Firmware and boot](#firmware) | `device-verified` |
| [CPU and interrupts](#cpu) | `device-verified` |
| [Memory and DMA](#memory) | `implemented` |
| [Storage and root](#storage) | `planned` |
| [Display](#display) | `planned` |
| [Input](#input) | `planned` |
| [GPU](#gpu) | `planned` |
| [Network](#network) | `planned` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `planned` |
| [Image assembly](#packaging) | `implemented` |
| [Diagnostics](#diagnostics) | `planned` |

## Configuration {#configuration}

`implemented`

Components: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`, `DarwinBoot`.

### Hardware and dependencies

- UniXNU format 2 layers: arm64, sm8250 SoC source, ipados-17.7.11-21H461 OS profile and the cas board.

### Configuration

- board.toml schema 2 with soc\_source sm8250 and defconfig cas\_defconfig.

### Procedure

- Run ./unixnu defconfig cas\_defconfig, fetch, status and tree from the UniXNU checkout.

### Development findings

- The layered configuration resolves with the pinned SoC source and component revisions.

### Completion criteria

- The configuration builds a kernel, firmware, payload and boot image with the standard commands.

### Current limits

- Only CPU0 and the minimal component set are selected; storage, display and input are pending.

### Next action

- Add boot-progress, a 4.75 GiB owned window and the standard payload settings.

### Evidence

- `source`: [Format 2 board configuration with the SM8250 and iPadOS 17.7.11 layers.](https://github.com/ht94911/UniXNU-cas/blob/5cba1411b76170abf027e312afee15669b9541d9/board.toml)

## Firmware and boot {#firmware}

`device-verified`

Components: `DarwinBoot`.

### Hardware and dependencies

- uefi-cas Mu-Silicium firmware with the bounded CasBootShim, inherited framebuffer and SPMI buttons.

### Configuration

- FD 0x9f000000 / 8 MiB; Android boot image header v2, page 4096; stock SoC DTB index 2.

### Procedure

- Boot the image with fastboot boot; ABL applies the existing DTBO.

### Development findings

- The UniXNU menu, buttons, RAM FAT, EFI run and return and the return to Android passed three complete runs.

### Completion criteria

- The firmware enters UniXNU, exposes the framebuffer and the payload volume, and starts DarwinBoot.

### Current limits

- The standard firmware profile cas-upstream.dsc has not been booted on the phone yet.

### Next action

- Add the static high-RAM descriptor and boot the standard firmware profile.

### Evidence

- `device`: [Three complete runs of the UniXNU menu, buttons, RAM FAT, EFI return and Android return.](https://github.com/ht94911/UniXNU-cas/blob/15bc58bb060a1e3c3cd15d4220997e4e54953d0a/docs/validation.md)
  Command: <code>fastboot boot boot.img (cas-complete-001)</code>. Revision: `346a404f6cee464e3e95f6ded464caf804a1f89e`.

## CPU and interrupts {#cpu}

`device-verified`

Components: `ArmCpu`.

### Hardware and dependencies

- Eight CPUs with MPIDR 0x000 to 0x700, PSCI smc, GICv3 0x17a00000/0x17a60000 and a 19.2 MHz timer.

### Configuration

- CPU0 enabled; ArmCpu with the Darwin assembler separator fix.

### Procedure

- Boot the kernel and read the CPU0 platform checkpoints.

### Development findings

- CPU0 returned from arm\_vm\_init, early platform expert setup, cpu\_timebase\_init and PE\_init\_cpu with CNTFRQ 19.2 MHz.

### Completion criteria

- All eight CPUs run with working timer and IPI handling.

### Current limits

- Timer interrupts after machine\_startup and the secondary CPUs are not verified yet.

### Next action

- Enable the remaining seven CPUs after the kernel reaches the root mount.

### Evidence

- `device`: [CPU0 completed VM setup and early platform and timebase initialization.](https://github.com/ht94911/UniXNU-cas/blob/15bc58bb060a1e3c3cd15d4220997e4e54953d0a/docs/cpu0-platform-clock.md)
  Command: <code>fastboot boot boot.img (candidate 005)</code>. Revision: `bae4311fe0a8c9b8d4258fe66a19b2615c3d4adb`.

## Memory and DMA {#memory}

`implemented`

Components: `ArmDTPlatform`.

### Hardware and dependencies

- DRAM banks 0x80000000+0x39900000, 0xc0000000+5 GiB and 0x200000000+6 GiB with 31 reserved regions.

### Configuration

- dts/cas.dts describes the banks and reservations; DarwinBoot owns the kernel window.

### Procedure

- Compile the board DTS through the format 2 payload step.

### Development findings

- A 512 MiB window at 0x100000000 maps on the phone and 256 MiB of it allocates with full read-back.

### Completion criteria

- A 4.75 GiB owned window at 0x100000000 is published by UEFI and used by XNU.

### Current limits

- The large owned window for userland has not been run yet.

### Next action

- Publish 0x100000000 to 0x240000000 as conventional memory in UEFI.

### Evidence

- `source`: [Board DRAM banks and reserved regions.](https://github.com/ht94911/UniXNU-cas/blob/5cba1411b76170abf027e312afee15669b9541d9/dts/cas.dts)

## Storage and root {#storage}

`planned`

### Hardware and dependencies

- UFS host 0x1d84000; userdata is LUN0 LBA 0x2c0000 to 0x3b4b7fa with 4 KiB blocks.

### Configuration

- The OS and SystemOS images go to userdata; the root is read-only and Data stays in RAM.

### Procedure

- Port the UniXNU-umi SM8250 UFS adaptation onto the ShengUfs component.

### Development findings

- UniXNU-umi mounts OS and SystemOS from UFS on the same SoC.

### Completion criteria

- The root volume mounts from userdata and launchd starts.

### Current limits

- No UFS driver is selected yet.

### Next action

- Build the userdata root image and port the read-only UFS driver.

### Evidence

Collect evidence using the next action.

## Display {#display}

`planned`

### Hardware and dependencies

- DSC command-mode panel, 1080x2340, inherited framebuffer at 0x9c000000.

### Configuration

- CPU presentation into the inherited framebuffer; no display controller programming.

### Procedure

- Port the UniXNU-umi legacy display path with GopFramebuffer.

### Development findings

- The UEFI menu draws through the inherited framebuffer on the phone.

### Completion criteria

- The Apple logo and the Hello screen appear under XNU.

### Current limits

- No XNU display service is selected yet.

### Next action

- Add GopFramebuffer and the legacy display package.

### Evidence

Collect evidence using the next action.

## Input {#input}

`planned`

### Hardware and dependencies

- ST FTS at 0x49 on the QUP I2C at 0xa94000, GPIO38 reset, GPIO39 interrupt; same wiring as the Xiaomi Mi 10.

### Configuration

- Native GPI DMA I2C with the PM8150B GPIO5 supply, as in UniXNU-umi.

### Procedure

- Port the UniXNU-umi ST FTS and HID implementation.

### Development findings

- Volume and power buttons work in the UEFI menu.

### Completion criteria

- Physical touches operate the Hello screen.

### Current limits

- No touch driver is selected yet.

### Next action

- Port the UniXNU-umi touch package after the Hello screen appears.

### Evidence

Collect evidence using the next action.

## GPU {#gpu}

`planned`

### Hardware and dependencies

- Adreno 650 on SM8250.

### Configuration

- No GPU component is selected.

### Procedure

- Evaluate the HackiOS A650 driver and the UniXNU Adreno components.

### Development findings

- The first userland uses CPU presentation.

### Completion criteria

- GPU submissions render the system interface.

### Current limits

- GPU work starts after touch works.

### Next action

- Inventory A650 firmware and registers after the Hello screen.

### Evidence

Collect evidence using the next action.

## Network {#network}

`planned`

### Hardware and dependencies

- QCA6390 on PCIe0.

### Configuration

- No network component is selected.

### Procedure

- Use the HackiOS QCA6390 driver as the reference.

### Development findings

- The cas cmd-db has no smpf2 rail, unlike the Xiaomi Mi 10.

### Completion criteria

- The device scans, joins and passes traffic.

### Current limits

- Network work starts after touch works.

### Next action

- Map the cas power rails for QCA6390.

### Evidence

Collect evidence using the next action.

## Audio {#audio}

`planned`

### Hardware and dependencies

- ADSP audio and the AW8697 haptics.

### Configuration

- No audio component is selected.

### Procedure

- Use the HackiOS audio references.

### Development findings

- Audio is outside the first interactive milestone.

### Completion criteria

- Playback and capture work on the selected routes.

### Current limits

- Audio work starts after touch works.

### Next action

- Inventory the cas audio graph after the Hello screen.

### Evidence

Collect evidence using the next action.

## Power {#power}

`planned`

### Hardware and dependencies

- PM8150 PMICs and the ApplePMGR service contract.

### Configuration

- The UniXNU-umi platform power service provides the ApplePMGR interface.

### Procedure

- Port UmiPlatformPower for the root and userland stage.

### Development findings

- Battery and sleep are outside the first interactive milestone.

### Completion criteria

- The PMGR service matches and userland starts.

### Current limits

- No power service is selected yet.

### Next action

- Port the platform power service with the UFS root.

### Evidence

Collect evidence using the next action.

## Image assembly {#packaging}

`implemented`

Components: `XnuPrelink`.

### Hardware and dependencies

- Prelinked kernel, ADT, payload FAT, UEFI FD and the stock SoC DTB.

### Configuration

- The payload FAT holds unixnu.toml, the kernel and its ADT.

### Procedure

- Run ./unixnu payload and ./unixnu bootimg.

### Development findings

- The prelinked iPadOS 17.7.11 kernel links with the selected components.

### Completion criteria

- The standard bootimg step produces the image booted on the phone.

### Current limits

- The framework bootimg step does not support the cas header v2 DTB area and CasBootShim, so scripts/cas\_bootimg.py packs the image.

### Next action

- Add the Data seed and trust cache to the payload for the root and userland stage.

### Evidence

- `source`: [Payload and kernel settings for the standard payload step.](https://github.com/ht94911/UniXNU-cas/blob/5cba1411b76170abf027e312afee15669b9541d9/board.toml)

## Diagnostics {#diagnostics}

`planned`

### Hardware and dependencies

- Framebuffer at 0x9c000000 and the XNU console mapping.

### Configuration

- boot-progress=2 and the panic screen.

### Procedure

- Port the UniXNU-umi boot-progress package.

### Development findings

- Earlier retained-RAM trace readers are replaced by the on-screen diagnostic page.

### Completion criteria

- Each boot shows its last stage, interrupt count or panic on the screen.

### Current limits

- The boot-progress package is not ported yet.

### Next action

- Port boot-progress and enable panic\_screen.

### Evidence

Collect evidence using the next action.

</div>
