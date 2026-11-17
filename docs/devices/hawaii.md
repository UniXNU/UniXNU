# Motorola Moto E32 \(XT2227-1\), Unisoc UMS9230 / Tiger T606

[lu4nn3ry/hawaii-unixnu](https://github.com/lu4nn3ry/hawaii-unixnu)

<div v-pre>

Motorola Moto E32 \(XT2227-1\), Unisoc UMS9230/T606. UEFI firmware builds and boots to SEC \(cyan/magenta stage markers confirmed on hardware\). DXE/PEI hang after SEC C code. No XNU kernel boot yet.

Source record: [porting.toml](https://github.com/lu4nn3ry/hawaii-unixnu/blob/eb2668c0b81183a5554117079eee6ea7d9aa95b2/porting.toml), `eb2668c0b81183a5554117079eee6ea7d9aa95b2`.

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
| [kernel](#kernel) | `implemented` |
| [Image assembly](#packaging) | `implemented` |
| [Diagnostics](#diagnostics) | `device-verified` |

## Configuration {#configuration}

`implemented`

Components: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`, `DarwinBoot`.

### Hardware and dependencies

- Vendor partition dumps \(boot\_b, uboot\_b\), motorola-moto-e32-root repo
- board.toml: schema\_version 2, soc=UMS9230, os\_profile=ipados-17.7.11-21H461

### Configuration

- board.soc = UMS9230
- board.os\_profile = ipados-17.7.11-21H461
- config\_fragments = arch common + soc:configs/ums9230.config

### Procedure

- 1. ./unixnu defconfig hawaii\_defconfig -D .
- 2. ./unixnu fetch
- 3. ./unixnu status --json

### Development findings

- See AGENTS.md for full technical details.

### Completion criteria

- See next\_action for the next concrete step.

### Current limits

- SoC source selected locally through local.toml until soc/UniXNU-ums9230-common is published

### Next action

- Publish soc/UniXNU-ums9230-common, pin its commit, re-run defconfig/status

### Evidence

- `host`: [defconfig resolves 5 components](https://github.com/lu4nn3ry/hawaii-unixnu/blob/eb2668c0b81183a5554117079eee6ea7d9aa95b2/board.toml)
  Command: <code>./unixnu defconfig</code>. Revision: `a214152000000000000000000000000000000000`.

## Firmware and boot {#firmware}

`implemented`

Components: `DarwinBoot`.

### Hardware and dependencies

- FD\_BASE=0x80800000, FD\_SIZE=0x400000 from vendor uboot\_b header
- BootShim ARM64 Image with ARMd magic at 0x38, .ltorg before \_Payload
- UEFI FD: SEC+PEI+DXE with PlatformSecLib \(cyan/magenta stage markers\), MemoryMapLib, SerialPortLib \(RGB565\), BringupDxe

### Configuration

- Toolchain: CLANGDWARF \(not CLANGPDB\)
- Dependencies: mu\_basecore + mu\_plus + mu\_oem\_sample
- kernel\_compression = none \(raw ARM64 Image\)
- AVB SHA256\_RSA4096 rollback index 2

### Procedure

- 1. Build: ./unixnu build firmware --uefi uefi-hawaii
- 2. Assemble: python3 scripts/assemble\_bootshim\_fd.py
- 3. Pack: python3 scripts/pack\_unixnu\_boot.py
- 4. Sign: python3 scripts/avb\_sign.py
- 5. Flash: dd to boot\_a via root, fastboot set\_active a

### Development findings

- See AGENTS.md for full technical details.

### Completion criteria

- See next\_action for the next concrete step.

### Current limits

- DXE/PEI hangs after SEC C code \(magenta\) - no EndOfDxe reached
- No UART on device - framebuffer stage markers are the only diagnostic
- Framebuffer half-painted suggests stride/resolution mismatch with DPU scanout

### Next action

- Fix PEI/DXE hang: check MemoryInitPeiLib against MemoryMapLib, check ArmGicDxe GIC base, check TimerDxe PPI numbers

### Evidence

- `device`: [cyan \(SEC asm\) then magenta \(SEC C\) confirmed on hardware; device hangs after magenta, does not reset](https://github.com/lu4nn3ry/hawaii-unixnu/blob/eb2668c0b81183a5554117079eee6ea7d9aa95b2/uefi-hawaii/Platforms/Unisoc/hawaiiPkg/Library/HawaiiPlatformSecLib/HawaiiPlatformSec.c)
  Command: <code>fastboot set_active a + reboot</code>. Revision: `a214152000000000000000000000000000000000`.

## CPU and interrupts {#cpu}

`implemented`

Components: `ArmDTPlatform`, `ArmCpu`.

### Hardware and dependencies

- Vendor DTS: 6x Cortex-A55 + 2x Cortex-A75, PSCI, GICv3 0x10000000/0x10040000, timer PPI 13/14/11/10

### Configuration

- PcdCoreCount=8
- PcdClusterCount=2
- PcdGicDistributorBase=0x10000000
- PcdGicRedistributorsBase=0x10040000
- Timer PPIs: 13/14/11/10

### Procedure

- 1. Inspect dts/hawaii.dts CPU, interrupt-controller, and timer nodes against the vendor DTS.
- 2. Resolve the hawaii defconfig and inspect the selected ArmCpu and ArmDTPlatform components.
- 3. Build the firmware and capture whether ArmGicDxe and TimerDxe reach their initialization checkpoints on hardware.

### Development findings

- See AGENTS.md for full technical details.

### Completion criteria

- See next\_action for the next concrete step.

### Current limits

- ArmGicDxe may hang if GIC base is wrong - not yet verified in DXE

### Next action

- Verify GIC base in DXE by checking if ArmGicDxe loads without fault

### Evidence

- `host`: [CPU and GIC nodes match vendor DTS](https://github.com/lu4nn3ry/hawaii-unixnu/blob/eb2668c0b81183a5554117079eee6ea7d9aa95b2/dts/hawaii.dts)
  Command: <code>./unixnu status</code>. Revision: `a214152000000000000000000000000000000000`.

## Memory and DMA {#memory}

`implemented`

### Hardware and dependencies

- System RAM: 0x80000000-0x17fffefff \(4 GiB\)
- Framebuffer: 0x9e000000 \(logobuffer\)
- Ramoops: 0xfff80000 \(0x40000\)

### Configuration

- UEFI Stack: 0x80480000 \(2 MB\)
- SEC Heap: 0x80680000 \(1 MB\)
- MMU PT: 0x80780000 \(0x40000\)
- UEFI FD: 0x80800000 \(4 MB\)
- DXE Heap: 0x80C00000 \(19.9 MB\)
- VarStore: 0x81FD0000 \(0x20000\)
- FDT: 0x82000000 \(1 MB\)

### Procedure

- 1. Compare MemoryMapLib reservations with the documented DRAM and reserved ranges.
- 2. Build the firmware and inspect the generated HOB memory map.
- 3. Compare the map with /proc/iomem and ramoops after PEI/DXE reaches the reset checkpoint.

### Development findings

- See AGENTS.md for full technical details.

### Completion criteria

- See next\_action for the next concrete step.

### Current limits

- Initrd window size may not match actual ramdisk load address
- Vendor reserved regions \(audio, DSP, modem\) may overlap DXE heap

### Next action

- Verify MemoryMapLib against /proc/iomem after fixing PEI hang
- Check if MemoryInitPeiLib rejects overlapping regions

### Evidence

- `host`: [Memory map compiles and links into SEC](https://github.com/lu4nn3ry/hawaii-unixnu/blob/eb2668c0b81183a5554117079eee6ea7d9aa95b2/uefi-hawaii/Platforms/Unisoc/hawaiiPkg/Library/MemoryMapLib/MemoryMapLib.c)
  Command: <code>./unixnu build firmware</code>. Revision: `a214152000000000000000000000000000000000`.

## Storage and root {#storage}

`planned`

Components: `SdhciBlock`.

### Hardware and dependencies

- SDHCI at 0x201a0000 \(not 0x71400000 as in UMS512\)
- UFS at 0x20200000
- Reference: woshimaniubi8/unixnu-eebbk-a2\_x2-ums512 drivers/SdhciBlock

### Configuration

- Controller base address: 0x201a0000; confirm protocol and register map from Hawaii vendor sources before enabling the component.

### Procedure

- 1. Compare the Hawaii vendor device tree controller, clocks, resets, and PHY with the candidate SDHCI implementation.
- 2. Build the storage component after confirming register compatibility.
- 3. Enumerate storage and read GPT on hardware after DXE is operational.

### Development findings

- See AGENTS.md for full technical details.

### Completion criteria

- See next\_action for the next concrete step.

### Current limits

- SDHCI register map not verified on hardware
- UFS vs eMMC path not confirmed

### Next action

- Verify SDHCI register map matches UMS512
- Test storage driver on hardware after DXE is working

### Evidence

Collect evidence using the next action.

## Display {#display}

`planned`

### Hardware and dependencies

- DPU at 0x31000000, DSI at 0x31100000
- Panel: 1600x720, RGB565, framebuffer at 0x9e000000
- Bootargs: lcd\_name=lcd\_nt36525c\_boe\_mipi\_fhd, lcd\_size=1600x720

### Configuration

- PcdFrameBufferWidth=1600
- PcdFrameBufferHeight=720
- PcdFrameBufferColorDepth=16 \(RGB565\)

### Procedure

- 1. Read the vendor panel mode and framebuffer properties from the Hawaii device tree.
- 2. Compare GOP dimensions and pixel format with the live DPU scanout.
- 3. Verify full-screen stage markers and GOP output on hardware.

### Development findings

- See AGENTS.md for full technical details.

### Completion criteria

- See next\_action for the next concrete step.

### Current limits

- SimpleFbDxe assumes cboot leaves DPU scanning out 0x9e000000
- Framebuffer half-painted suggests stride mismatch - DPU may scan at different resolution
- No DPU/DSI init driver - panel may not be initialized

### Next action

- Verify framebuffer stride by checking DPU registers at 0x31000000
- Write DPU/DSI GOP driver if SimpleFbDxe does not work

### Evidence

- `device`: [Cyan paint covered top half of screen, bottom half shows Motorola logo - DPU is scanning 0x9e000000 but stride/resolution differs from 1600x720](https://github.com/lu4nn3ry/hawaii-unixnu/blob/eb2668c0b81183a5554117079eee6ea7d9aa95b2/uefi-hawaii/Platforms/Unisoc/hawaiiPkg/Library/HawaiiPlatformSecLib/HawaiiPlatformSec.c)
  Command: <code>screen observation</code>. Revision: `a214152000000000000000000000000000000000`.

## Input {#input}

`planned`

### Hardware and dependencies

- GPIO keys: power \(gpio 73\), volumedown \(gpio 122\), volumeup \(gpio 73\)
- Touch controller not identified \(cit\_tp=0x00 in bootargs\)
- I2C3: aw9610x, ucp1301, vl53l0

### Configuration

- Touch controller and bus: unresolved; identify from the Hawaii vendor device tree before selecting a driver.

### Procedure

- 1. Identify the touch controller and bus from the vendor device tree and kernel sources.
- 2. Search UniXNU device repositories for a matching controller implementation.
- 3. Implement or adapt the matching driver and verify touch events on hardware.

### Development findings

- See AGENTS.md for full technical details.

### Completion criteria

- See next\_action for the next concrete step.

### Current limits

- No UniXNU touch driver for Goodix gt9xx or Unisoc touch
- Touch controller chip not identified

### Next action

- Identify touch controller from vendor kernel sources
- Implement touch driver

### Evidence

Collect evidence using the next action.

## GPU {#gpu}

`planned`

Components: `MaliG57`.

### Hardware and dependencies

- GPU at 0x23100000 \(sprd,mali-natt\), GIC\_SPI 60 x3 \(JOB/MMU/GPU\)
- Mali-G57 Valhall, r28p0-01eac0 DDK
- DVFS: 150-3300 MHz

### Configuration

- GPU base: 0x23100000; GPU\_ID and firmware requirements remain unverified.

### Procedure

- 1. Inspect the vendor Mali DDK and confirm the GPU\_ID and firmware requirements.
- 2. Compare the available Valhall implementation and document the required G57 adaptations.
- 3. Build the driver and verify GPU initialization and rendering on hardware.

### Development findings

- See AGENTS.md for full technical details.

### Completion criteria

- See next\_action for the next concrete step.

### Current limits

- GPU\_ID not confirmed from vendor DTB
- NativeMaliG57.cpp is skeleton, not functional

### Next action

- Extract Mali kbase DDK r28p0 from CreitinGameplays patches 0014-0017
- Confirm GPU\_ID from vendor kernel
- Complete driver implementation

### Evidence

Collect evidence using the next action.

## Network {#network}

`planned`

Components: `WcnWifi`.

### Hardware and dependencies

- WCN: sprd,ums9230-wcn, SDIO-based combo Wi-Fi/BT
- Reference: linux/drivers/net/wireless/unisoc/ \(SC23xx\)

### Configuration

- WCN transport: SDIO; exact functions, interrupts, and firmware selection remain unverified.

### Procedure

- 1. Identify the WCN SDIO function, firmware files, and interrupt/DMA requirements from Hawaii sources.
- 2. Search UniXNU repositories for a driver covering the same controller and register map.
- 3. Build the adapted driver and verify association and packet transfer on hardware.

### Development findings

- See AGENTS.md for full technical details.

### Completion criteria

- See next\_action for the next concrete step.

### Current limits

- No open-source UniXNU Wi-Fi driver for Unisoc WCN
- Firmware not extracted from vendor partitions

### Next action

- Extract wcnmodem.bin and firmware from vendor partitions
- Implement Wi-Fi driver based on Linux unisoc reference

### Evidence

Collect evidence using the next action.

## Audio {#audio}

`planned`

### Hardware and dependencies

- Codec: sprd,vbc-v4-codec-sc2730
- I2S: sprd,i2s-null-codec
- Audio DSP: audio-mem@94100000, audiodsp-mem@89000000

### Configuration

- Codec: SC2730 VBC v4; I2S and DSP firmware integration are not implemented.

### Procedure

- 1. Inventory codec, DSP, clocks, and firmware from the Hawaii vendor sources.
- 2. Locate a reusable UniXNU implementation for matching audio hardware.
- 3. Build the audio path and verify playback and capture on hardware.

### Development findings

- See AGENTS.md for full technical details.

### Completion criteria

- See next\_action for the next concrete step.

### Current limits

- No audio driver implemented
- DSP firmware not extracted

### Next action

- Inventory audio DSP firmware from vendor partitions
- Implement audio driver

### Evidence

Collect evidence using the next action.

## Power {#power}

`planned`

### Hardware and dependencies

- PMIC: SC2730 \(sprd,sc2731-regulator, sprd,sc2730-regulator\)
- 32 regulators: vddcpu, vddgpu, vddcore, vddmem, etc.
- PMIC SPI at 0x64200000

### Configuration

- PMIC bus base: 0x64200000; regulator mapping and ownership remain unverified.

### Procedure

- 1. Map SC2730 bus access, regulators, and firmware ownership from Hawaii sources.
- 2. Search UniXNU repositories for a matching PMIC implementation.
- 3. Implement or adapt the PMIC support and verify safe power transitions on hardware.

### Development findings

- See AGENTS.md for full technical details.

### Completion criteria

- See next\_action for the next concrete step.

### Current limits

- No power driver implemented
- Regulator mapping not verified on hardware

### Next action

- Implement SC2730 PMIC driver via SPI
- Register regulators with XNU power management

### Evidence

Collect evidence using the next action.

## kernel {#kernel}

`implemented`

Components: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`.

### Hardware and dependencies

- XNU xnu-10063.141.1 \(d8b80295118ef25ac3a784134bcf95cd8e88109f\)
- Toolchain: clang-24, 28 xnu patches applied
- Prelink ABI patches applied

### Configuration

- ARCH\_CONFIGS=ARM64
- MACHINE\_CONFIGS=BCM2837
- KERNEL\_CONFIGS=DEVELOPMENT

### Procedure

- 1. Inspect the selected kernel defconfig, patch series, and recorded XNU revision.
- 2. Move required machine and prelink changes into the ordered device patch series.
- 3. Build the kernel and verify the resulting Mach-O architecture and configuration.

### Development findings

- See AGENTS.md for full technical details.

### Completion criteria

- See next\_action for the next concrete step.

### Current limits

- BCM2837 machine config used \(not UMS9230-specific\)
- Prelink ABI patches applied manually, not in series

### Next action

- Create UMS9230-specific machine config
- Commit prelink ABI patches to patches/xnu/ series

### Evidence

- `host`: [Kernel configuration selects ARM64/DEVELOPMENT; machine selection remains BCM2837 and is not UMS9230-specific.](https://github.com/lu4nn3ry/hawaii-unixnu/blob/eb2668c0b81183a5554117079eee6ea7d9aa95b2/configs/hawaii_defconfig)
  Command: <code>./unixnu kernel</code>. Revision: `a214152000000000000000000000000000000000`.

## Image assembly {#packaging}

`implemented`

Components: `SoftwareAES`, `XnuPrelink`.

### Hardware and dependencies

- boot\_b header: ANDROID\! v2, pagesize 2048, kernel\_addr 0x8000
- BootShim+UEFI FD as kernel, payload FAT as ramdisk, DTB preserved

### Configuration

- header\_version=2
- kernel\_compression=none
- AVB SHA256\_RSA4096 rollback index 2

### Procedure

- 1. Build the XNU kernel and generate the board ADT sidecar.
- 2. Create the payload FAT with the kernel, ADT, and boot configuration.
- 3. Pack and inspect the Android boot image and verify payload contents before hardware boot.

### Development findings

- See AGENTS.md for full technical details.

### Completion criteria

- See next\_action for the next concrete step.

### Current limits

- Payload FAT has no kernel.macho yet \(needs XNU build\)
- startup.nsh removed from FDF \(file not found in PACKAGES\_PATH\)

### Next action

- Build XNU kernel.macho for arm64
- Create payload FAT with kernel.macho + .adt + unixnu.toml

### Evidence

- `host`: [Boot image packaging procedure is present; payload kernel and ADT are still pending.](https://github.com/lu4nn3ry/hawaii-unixnu/blob/eb2668c0b81183a5554117079eee6ea7d9aa95b2/scripts/pack_unixnu_boot.py)
  Command: <code>python3 scripts/pack_unixnu_boot.py --help</code>. Revision: `a214152000000000000000000000000000000000`.

## Diagnostics {#diagnostics}

`device-verified`

### Hardware and dependencies

- No UART on device
- Framebuffer stage markers: cyan \(SEC asm\), magenta \(SEC C\)
- BringupDxe reset is intended at EndOfDxe but has not been observed

### Configuration

- SEC stage markers: cyan for assembly and magenta for SEC C; current observed stop is after magenta.
- UART unavailable; ramoops collection awaits EndOfDxe reset.

### Procedure

- 1. Boot the signed image and record the panel stage marker reached.
- 2. After the EndOfDxe reset checkpoint, return to Android and collect ramoops.
- 3. Attach the log and exact source revision to the device validation record.

### Development findings

- See AGENTS.md for full technical details.

### Completion criteria

- See next\_action for the next concrete step.

### Current limits

- No UART access - framebuffer is the only diagnostic
- ramoops not yet readable \(device does not reach EndOfDxe to reset\)

### Next action

- Fix PEI/DXE hang so BringupDxe fires and device resets to Android
- Read ramoops from /sys/fs/pstore/ after reset

### Evidence

- `device`: [Cyan and magenta stage markers confirmed on hardware; device hangs after magenta \(PEI/DXE stage\)](https://github.com/lu4nn3ry/hawaii-unixnu/blob/eb2668c0b81183a5554117079eee6ea7d9aa95b2/uefi-hawaii/Platforms/Unisoc/hawaiiPkg/Library/HawaiiPlatformSecLib/HawaiiPlatformSec.c)
  Command: <code>screen observation</code>. Revision: `a214152000000000000000000000000000000000`.

</div>
