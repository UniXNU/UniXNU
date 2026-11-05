# Orange Pi 5 \(Rockchip RK3588S\)

[Ken-u/UniXNU-orangepi5](https://github.com/Ken-u/UniXNU-orangepi5)

<div v-pre>

Orange Pi 5 \(Rockchip RK3588S\) with an HDMI display and an M.2 NVMe drive, running the iPadOS 17.7.11 userland on a source-built XNU, started from edk2-rk3588 firmware \(uefi-orangepi5\). Shared SoC support is in UniXNU-rk3588-common, which the EVB10 port already proved on hardware. Observed on the board \(2026-11-03..05\): U-Boot starts the firmware from the NVMe ESP; NVMe root and persistent Data mount; SpringBoard and Mali Metal compose over HDMI0 through the shared RK3588 VOP2 direct scanout \(iommu paging, no CPU GOP copy\). Network and audio drivers are not started yet; DVFS is not hooked; physical USB input is not brought up \(a software HID digitizer stand-in is linked\).

Source record: [porting.toml](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/porting.toml), `f96d273b526254d700bd42bfeadef0359a1d3c46`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `host-verified` |
| [Firmware and boot](#firmware) | `device-verified` |
| [CPU and interrupts](#cpu) | `implemented` |
| [Memory and DMA](#memory) | `device-verified` |
| [Storage and root](#storage) | `device-verified` |
| [Display](#display) | `device-verified` |
| [Input](#input) | `implemented` |
| [GPU](#gpu) | `device-verified` |
| [Network](#network) | `planned` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `planned` |
| [Image assembly](#packaging) | `device-verified` |
| [Diagnostics](#diagnostics) | `device-verified` |

## Configuration {#configuration}

`host-verified`

### Hardware and dependencies

- ARM64 profile, rk3588 SoC source pinned in feeds.toml, iPadOS 17.7.11 build 21H461 profile, orangepi5\_defconfig.

### Configuration

- board.soc\_source = rk3588; board.os\_profile = ipados-17.7.11-21H461; schema\_version = 2.
- orangepi5\_defconfig is the console kernel with NVMe storage and the Mali driver linked \(inert without mali=N\): no display, no RAM disk, no UFS; orangepi5\_display\_defconfig, the configuration of the image, adds CONFIG\_XNU\_NATIVE\_LEGACY\_DISPLAY=y and the link stubs \(scripts/build-orangepi5-kernel.sh builds the two in that order\); the trust-cache runtime and the code-signing hash cache stay on.
- \[adt.defaults.u32\] carries sleep-disabled = 1 and vmm-present = 1, which the EVB10 port found necessary for watchdogd.

### Procedure

- From the UniXNU checkout run ./unixnu defconfig orangepi5\_defconfig -D ../UniXNU-orangepi5, then ./unixnu fetch, ./unixnu status --json and ./unixnu tree with the same -D.
- scripts/build-orangepi5-kernel.sh runs the kernel build; it needs the environment of the machine that builds \(.env\) and CMake 3.19.6 or newer.

### Development findings

- Resolution is host-verified: defconfig, fetch, status --json and tree complete against the pinned SoC repository.
- The UniXNU bootstrap pass builds AvailabilityVersions with CMake; the distribution CMake of Ubuntu 20.04 is 3.16 and fails, so the build script puts /usr/local/bin first.
- The kernel now carries the NVMe driver: board.toml archives build-orangepi5-drivers.py Rk3588Nvme and bind-nvme-storage.py, the defconfig force-loads libRk3588Nvme.a, and the build script verifies the bound addresses against the kernel \(18 addresses inside the audited IOStorageFamily\).
- board.toml \[userdata\] is the layout of the 128 GB drive: userdata at LBA 526336..134744063 behind a 256 MiB ESP at LBA 2048; the boot arguments are the EVB10 ones with the storage names of the NVMe driver \(nvme=4, nvme-root-trust=1, nvme-data-size=2048, nvme-data-persist=1\).
- board.toml payload.dram\_size and payload.adt.owned\_memory\_size are 0xF8000000 \(3.875 GiB, in the 4 GiB bank at 0x100000000\) now, the window measured on the board \(memory area, evidence/device-memory-20261103.txt\); the old 4 GiB and 2 GiB values were EVB10 placeholders.
- The kernel is built in two passes now and carries the GOP-backed legacy display \(board.toml archive build-orangepi5-display.py, component GopFramebuffer, the offline-legacy-\* and sheng-\* arguments; evidence/host-display-build-20261103.txt\) and the Mali-G610 driver \(archives build-mali-firmware.py and build-orangepi5-drivers.py Mali, libMali.a force-loaded by both defconfigs, no mali argument in the list; evidence/host-gpu-build-20261103.txt\). Both link on the host.
- board.toml now defaults mali=8 mali-metal=1 evb10-gpu-addon=1, rk3588-vop-direct=1 with esmart=2/vp=2/fence=1, opi5-hid-input and sheng-touch-hid, and thin-bezel=1; feeds.toml pins UniXNU-rk3588-common at b5f5d94 \(Rk3588VopDirect\). Observed on the board with that list \(evidence/device-vop-direct-20261105.txt\).

### Completion criteria

- Every source pin resolves, ./unixnu status lists the intended patch order, and the defconfig materialises.

### Current limits

- Network and audio still have no driver; DVFS is not started from the Orange Pi 5 probe; physical USB HID is not brought up; the default menu entry is still xnu-probe.

### Next action

- DEFAULT\_ENTRY=xnu MENU\_TIMEOUT=3 rewrite of esp.img; hook RK3588 DVFS from the display probe; Ethernet or Wi-Fi.

### Evidence

- `source`: [Board configuration of the console kernel](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/board.toml)
- `host`: [The two-pass kernel with the display and the Mali driver links \(51658752 bytes, sha256 9281cf98...\); nothing ran on the board](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/evidence/host-gpu-build-20261103.txt)
  Command: <code>source host/env.sh &amp;&amp; cd UniXNU-orangepi5 &amp;&amp; scripts/build-orangepi5-kernel.sh</code>. Revision: `ce6c6fb8d6f31b3c0a87dd4ead1f6d444c79f366`.
- `host`: [The kernel with the NVMe driver links and the bound-address check passes \(51154944 bytes, sha256 76ba878c...\); nothing ran on the board](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/evidence/host-nvme-storage-20261101.txt)
  Command: <code>source host/env.sh &amp;&amp; cd UniXNU-orangepi5 &amp;&amp; scripts/build-orangepi5-kernel.sh</code>. Revision: `5cbaf4236c5f0a850a62daa341b1195956b4a63f`.
- `host`: [defconfig, fetch, status, tree and the full console kernel build complete on the host; nothing ran on the board](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/evidence/host-kernel-build-20261101.txt)
  Command: <code>source host/env.sh &amp;&amp; cd UniXNU-orangepi5 &amp;&amp; scripts/build-orangepi5-kernel.sh</code>. Revision: `f4bb6e952e915f4f837547f11981ca26b61a5c46`.
- `device`: [The board.toml memory values boot the kernel to launchd: the 3.875 GiB window at 0x100000000 \(400 s, no panic\); 3.5 GiB and 4094 MiB boot too](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/evidence/device-memory-20261103.txt)
  Command: <code>cd uefi-orangepi5 &amp;&amp; REBUILD=1 tools/board/make-bundle.sh; capture as in the memory area</code>. Revision: `1cbc693ca1c335720f0c4ae48665320e05390b4d`.

## Firmware and boot {#firmware}

`device-verified`

### Hardware and dependencies

- edk2-rk3588 firmware built by uefi-orangepi5 \(an SPI NOR image with TF-A at EL3, OP-TEE and the UEFI volume, or the UEFI volume alone as a launcher image\), UEFI GOP frame buffer on HDMI0.
- A U-Boot in the SPI NOR supplied by the board's owner. Reported from its console \(not observed from here\): kernel\_addr\_r=0x00400000, fdt\_addr\_r=0x08300000, boot\_targets=mmc1 mmc0 nvme scsi usb pxe dhcp spi, and a working ums.

### Configuration

- board.toml has no \[firmware\] section: the unixnu firmware step builds Mu-Silicium, and this board boots edk2-rk3588 built by uefi-orangepi5.
- payload.loader = firmware: DarwinBoot is inside the firmware volume and reads the payload from the ESP of the NVMe drive, found through NvmExpressDxe.
- The board has no SD card, so the firmware is not flashed: boot.scr on the ESP makes U-Boot load uefi-launcher.img \(a stub with the volume inside\) at 0xa000000 and booti it; the stub copies the volume to 0x200000 and jumps to its reset vector target \(0x1400\) at EL2. The volume is built with RK\_NOR\_FLASH\_ENABLE=FALSE \(build.sh -L\), so edk2 does not write the SPI that holds U-Boot.

### Procedure

- Build the volume \(uefi-orangepi5 build.sh -L\), the bundle \(tools/board/make-bundle.sh puts uefi-launcher.img and boot.scr on the ESP\) and the disk files \(tools/board/make-disk-image.sh\). Put the drive on a Mac with U-Boot's ums, write head.img, tail.img, the zeroed Data header and esp.img with dd, then power-cycle: U-Boot runs boot.scr. With an SD card the firmware can go into the SPI NOR instead \(tools/board/spi-flash.sh, Maskrom when /proc/mtd does not list the flash\). All of it is in uefi-orangepi5/docs/first-boot.md.

### Development findings

- Observed on the board \(evidence/device-first-boot-20261103.txt, sections 1 to 3 and 6\): the SPI NOR U-Boot \(v5-gc507c92ef837-261013\) scans the NVMe, finds /boot.scr and runs it; the stub copies the volume to 0x200000 and jumps to 0x1400 at EL2 \(booti left it where it was loaded\); the UEFI banner follows 0.04 s after the jump; the firmware reports 4 x 2048 MB = 8192 MB of RAM, brings the PCIe link up again after U-Boot used the drive \(x1, 2.5 GT/s\), reads kernel.macho and its companions from the ESP of the NVMe drive, and DarwinBoot hands the kernel over with the GOP frame buffer 0xE7AC0000 \(640x480, row 2560\). The device tree U-Boot hands over reaches edk2 as x0 \(one harmless 'Bad transfer list signature 0xEDFE0DD0' line\).
- The board's U-Boot counts the entries of a script image up to a word of 0xffffffff, not up to 0 as mkimage writes: boot.scr as mkimage writes it printed "Unknown command '&lt;garbage&gt;'" because the text was taken from behind the end of the file. With \[length, 0xffffffff\] as the size table iminfo lists one image and source runs the text \(checked with small images in RAM, then with the real boot.scr, which now starts the launcher by itself, also after the restart that follows a kernel panic\). tools/board/make-bootscr.py writes that by default and --table-end 0 gives the mkimage layout.
- The UniXNU menu takes keys from the serial port: serial-capture.py --send 'menu: shown' text:1 picked the xnu entry \(menu: key 1, booting 0\) in the 10 s countdown.
- HDMI0 shows the kernel log: the xnu-hdmi entry \(vc\_mirror=1\) copies it to the GOP frame buffer \(video base 0xE7AC0000, 640x480, row 2560\) and the person at the board saw text scrolling on the monitor \(evidence/device-hdmi-watchdog-20261103.txt; not photographed, so colours, position and readability are not recorded\). The xnu and xnu-probe entries leave the monitor black after the menu, as designed.
- A kernel panic restarts the board at once \(the next U-Boot banner 0.97 s after the panic line\); the hardware watchdog path was run once: after the kernel's wdt-kick feeder stopped \(1800 s\), the board was reset and ran by itself again, the adapter dropping off the bus at 11:49 \(the 89 s were due 11:49:33\). The reset itself was not seen on the serial line, so that it was the watchdog is an inference from the time. The launcher arms the DW watchdog, UniXNUBootWdtDxe takes over, and the kernel's wdt-kick feeder kept the board up for the 400 s from the hand-off to the end of the xnu capture.
- The firmware builds on the host with the GPU rail set to 0.75 V and the hardware watchdog driver of uefi-orangepi5 armed \(the board has no remote power switch, so a hung kernel must end in a watchdog reset\).
- The firmware image is a bundle member \(nor.img\) built by uefi-orangepi5 tools/board/make-bundle.sh; spi-flash.sh was checked for its /proc/mtd parsing only, it has not touched a flash.
- Host-verified for the launcher: the stub's instructions are identical to the EVB10 stub that ran on a board \(only strings and the text\_offset field differ\); the entry offset read from the volume's reset vector is 0x1400 for the EVB10 and both Orange Pi 5 volumes; boot.scr written with --table-end 0 is byte for byte what mkimage -T script writes; the ESP with both files passes fsck.vfat and reads back identical; make-disk-image.sh runs nvme-install.py with read-back into a 128 GB sparse file.
- The ESP can be updated from the serial console, with no second computer: at the U-Boot prompt uboot-put.py \(UniXNU-rk3588-common tools/board\) sends a file with YMODEM, fatwrite puts it on the ESP, fatload and crc32 read it back \(all numbers hex\). uefi-launcher.img \(5251560 bytes\) takes about 40 s at 1.5 Mbaud; the launcher, kernel.macho.adt and unixnu.toml were replaced that way for the memory runs and verified by crc32 \(evidence/device-memory-20261103.txt, section 7\). The firmware logs its UEFI memory map \(UniXNUMemMapDxe, uefi-orangepi5 e35d303\) before the menu and at ExitBootServices.
- Two firmware fixes came out of the memory work \(uefi-orangepi5 dc08d7c and e1ac136; memory area, evidence/device-memory-20261103.txt, sections 5 and 6\): the ACPI tables are linked with -Wl,--sort-section=name so the table, not clang's ReferenceAcpiTable pointer, is first in Pptt.acpi \(observed on the board: all eight tables install, the 'Couldn't locate ACPI DSDT' line is gone, no more AcpiTableDxe abort in the builds that had one\) and PcdImageLargeAddressLoad is FALSE \(RtkUndiDxe loads at 0xE7CFB000 instead of its linked 0x180000000\).

### Completion criteria

- Firmware enters DarwinBoot, publishes the GOP frame buffer and finds the NVMe ESP.

### Current limits

- The HDMI picture is a text mirror only \(no display driver; the monitor was reported as scrolling text, nothing more\); the SPI NOR route \(nor.img\) has not run; the U-Boot is the owner's build, known by its console, its environment and what it did in the runs above.
- The first runs started from the U-Boot prompt by 'reset' typed on the serial console; a power-on from cold \(BootROM to U-Boot\) is the same path but was not captured.
- The USB serial adapter drops off the bus at every board reset and returns under another name; captures need its /dev/serial/by-id path \(BOARD\_SERIAL\_DEV\).

### Next action

- Capture the watchdog reset on a line that survives it \(by-id path\) to confirm the 89 s; once the runs are good, make xnu the default \(DEFAULT\_ENTRY=xnu MENU\_TIMEOUT=3 tools/board/make-bundle.sh\) and write the new esp.img.

### Evidence

- `host`: [Launcher volume builds without the SPI NOR variable store; the stub's instructions equal the EVB10 stub that ran on a board; boot.scr equals mkimage's output byte for byte; the ESP with launcher and boot.scr passes fsck.vfat; the disk files install and read back. Nothing ran on the board](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/evidence/host-launcher-20261103.txt)
  Command: <code>cd uefi-orangepi5 &amp;&amp; ./build.sh -b DEBUG -L &amp;&amp; REBUILD=1 tools/board/make-bundle.sh &amp;&amp; tools/board/make-disk-image.sh</code>. Revision: `34fb4cfa4fa32f5e1a0e8eaa341724ad72abb000`.
- `source`: [Boot flow and milestones M0 to M4](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/docs/bring-up.md)
- `device`: [Launcher, firmware and DarwinBoot on the Orange Pi 5 from U-Boot's boot.scr: 8192 MB RAM, PCIe link up again after U-Boot, payload read from the NVMe ESP, kernel hand-off with the 640x480 GOP frame buffer, menu key through the serial port \(captures auto1 and xnu1\)](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/evidence/device-first-boot-20261103.txt)
  Command: <code>cd uefi-orangepi5 &amp;&amp; tools/board/capture-remote.sh auto1 330 (reset typed at the U-Boot prompt); CAPTURE_ARGS="--send 'menu: shown' text:1" tools/board/capture-remote.sh xnu1 480</code>. Revision: `b1d3c18fc1ba985101e5d3c372d18e59d0378df4`.
- `device`: [xnu-hdmi: the kernel log scrolls on the HDMI monitor \(reported\), launchd up with vc\_mirror=1; the board resets and runs again after the kernel stops feeding the watchdog \(inferred, the adapter dropped at that moment\)](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/evidence/device-hdmi-watchdog-20261103.txt)
  Command: <code>cd uefi-orangepi5 &amp;&amp; CAPTURE_ARGS="--send 'menu: shown' text:2" tools/board/capture-remote.sh hdmi3 1500 /dev/serial/by-id/ADAPTER</code>. Revision: `b1d3c18fc1ba985101e5d3c372d18e59d0378df4`.

## CPU and interrupts {#cpu}

`implemented`

Components: `ArmCpu`, `ArmDTPlatform`.

### Hardware and dependencies

- Four Cortex-A55 and four Cortex-A76 at affinities 0x000 to 0x700, GICv3 at 0xfe600000, 24 MHz architected timer, PSCI over SMC: the same cluster layout and GIC as the EVB10, since the RK3588S is the RK3588 without some interfaces.

### Configuration

- The CPU, GIC and PSCI nodes come from the SoC dtsi \(rk3588-common dts/rk3588.dtsi\); the board DTS enables nothing extra.
- Kernel arguments sheng-smp=1, armcpu-self-ipi=1, armcpu-mmio-sgi=0 and cpumask=31 are the ones of the EVB10 port.

### Procedure

- Compile dts/orangepi5.dts through ./unixnu tree and inspect /cpus, /psci and /arm-io/intc in the generated device tree.
- Boot and read the per-core entry lines on the serial console.

### Development findings

- The CPU path is shared with the EVB10 and unchanged here; the EVB10 record documents the EL2 to EL1 drop of secondary cores and the Darwin assembler caveat.
- Whether the Orange Pi 5 firmware leaves the same state is not yet observed.

### Completion criteria

- Every enabled core reaches its entry checkpoint and receives timer and inter-processor interrupts.

### Current limits

- No CPU frequency governor yet; the DVFS rail table of the EVB10 \(RK8602 at I2C0 0x42 and 0x43, RK806 BUCK1 and BUCK2\) matches the Orange Pi 5 and will be reused with the power area.

### Next action

- Boot the console kernel and compare the per-core lines with the EVB10 log.

### Evidence

- `source`: [Board device tree on top of the shared SoC description](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/dts/orangepi5.dts)

## Memory and DMA {#memory}

`device-verified`

### Hardware and dependencies

- The board of this port has 8 GiB of LPDDR4x. The firmware \(edk2-rk3588 as built by uefi-orangepi5\) maps it as the lower bank below 0xf0000000 \(3.75 GiB, cut by OP-TEE, TF-A and the firmware's own allocations\) and the 4 GiB bank from 0x100000000; U-Boot also reports 256 MiB at 0x2f0000000 that edk2 does not map.

### Configuration

- payload.adt.owned\_memory\_size = 0xF8000000 \(3.875 GiB\): DarwinBoot takes that many contiguous bytes from one run of free memory of the UEFI map, first fit. With the firmware as built here that is the 4 GiB run at 0x100000000: the window is pa 0x10007C000 to 0x1F807C000 and 127 MiB of the run stay free behind it.
- The memory node of dts/orangepi5.dts \(memory@100000000, 3.875 GiB\) and payload.dram\_size = 0xF8000000 follow the window; the kernel does not read the node.
- Firmware side \(uefi-orangepi5\): the link order of the ACPI tables \(dc08d7c\) and PcdImageLargeAddressLoad = FALSE \(e1ac136\), which keep the 4 GiB bank in one piece; without them the longest run is 2.6 GiB.

### Procedure

- Read the memory map the firmware prints \(UniXNUMemMapDxe: before the menu and at ExitBootServices\) and take the largest run of free memory \(4096 MiB at 0x100000000 on this firmware\); set owned\_memory\_size below it with margin \(2 MiB steps\), rebuild the payload \(REBUILD=1 tools/board/make-bundle.sh\) and write kernel.macho.adt to the ESP \(through U-Boot: uboot-put.py, fatwrite, crc32\). DarwinBoot prints 'boot refused: Out of Resources' when no run is long enough, and the UniXNU menu then waits for a key \(5 restarts the board\).

### Development findings

- Observed with the firmware as first built \(evidence/device-memory-20261103.txt, section 1\): free runs 0x7F0000 + 124 MiB, 0x9400000 + 849 MiB and 0x40000000 + 2674 MiB \(the largest, up to 0xE72DA000\) in the lower bank, 0x100000000 + 2048 MiB and 0x180024000 + 2047 MiB above it.
- The upper bank was cut at 0x180000000 by RtkUndiDxe.efi \(prebuilt Realtek UNDI driver of edk2-non-osi, ImageBase 0x180000000, 0x24000 bytes\): DxeCore loads an image at its linked address when that is free because PcdImageLargeAddressLoad is TRUE \(host reading of the PE header and of Image.c; the log shows the load at 0x180000000\). So no run above 4 GiB was longer than 2 GiB, and window requests of 3.5 GiB \(0xE0000000\) and of sizes between 2.75 and 3 GiB were refused \('DARWINBOOT: boot refused: Out of Resources'\); 2.5 GiB \(0xA0000000\) booted \(memC, memH, memI: pa 0x4007C000, 626169 to 626173 free pages against 497587 with the 2 GiB window, launchd 'Early boot complete' 30 s after the hand-off, no panic in 400 s; section 4\).
- The two ways tried to get the upper bank in one piece \(-D NETWORK\_ENABLE=FALSE; PcdImageLargeAddressLoad=FALSE\) stopped the firmware before the menu with a data abort in AcpiTableDxe \(FAR 0xFFFFFFF0, 0xAFAFAFAF in the registers; memG, memJ\). Cause of the broken ACPI install, found on the host \(section 5\): Pptt.aslc compiled with clang has an 8-byte ReferenceAcpiTable pointer in .data.rel.ro in front of the table in .data, GenFw -c copies the sections in the order the linker gives, so Pptt.acpi began with 8 stray bytes; the firmware read a sixth table with a garbage signature and length 0, its install failed, SPCR and DSDT were never installed. Linking the ACPI tables with -Wl,--sort-section=name puts the table first \(reproduced by hand: the first bytes are 'PPTT' with the flag, 40 02 00 00 00 00 00 00 'PPTT' without\). Observed after dc08d7c: all eight tables install \(memK\); the memJ configuration \(PcdImageLargeAddressLoad=FALSE, window 0xE0000000\) plus the fix no longer aborts \(memL\). Which line of AcpiTableDxe reads the freed memory was not traced; the memG build was not repeated with the fix.
- With both firmware changes the 4 GiB above 0x100000000 is one run of 4096 MiB \(memL map, section 6\) and the kernel boots from a window there: 3.5 GiB \(memL: pa 0x10007C000, 884604 free pages\), 4094 MiB \(memM: 1013320 free pages\) and the committed 3.875 GiB \(memN: pa 0x10007C000, args 0x1040C4000, 981518 free pages, 3968 MiB 'loader code' run with 127 MiB free behind it\); each reaches launchd 'Early boot complete' 30 s after the hand-off with no panic, for 150 s \(memL, memM\) and 400 s \(memN\) of feeding. The kernel has run above 4 GiB on this port since memL.
- The ADT generator takes one range and DarwinBoot one window, and nothing in the kernel sources of this tree reads dram-base or dram-size from /chosen \(host reading\), so the lower bank \(3.75 GiB, 2.6 GiB free\) and the upper one cannot both be given to the kernel; the 256 MiB at 0x2f0000000 are not mapped by edk2.

### Completion criteria

- The kernel reports the memory it owns and the ADT memory ranges match the firmware map.

### Current limits

- The kernel owns 3.875 GiB of the 8 GiB: the lower bank \(3.75 GiB, 2.6 GiB of it free\) and the 256 MiB at 0x2f0000000 are unused \(one window, one ADT range\).
- The window leaves 127 MiB in the run. A firmware change that splits the upper bank again \(a prebuilt driver with a fixed load address, PcdImageLargeAddressLoad back to TRUE\) makes DarwinBoot refuse the boot and the board waits in the menu for a key; the MEMMAP lines show the runs before the menu.
- Which of the captures memA, memB, memD and memE had which size was not written down; the refusals and the sizes tried are recorded, the pairing is not.
- SpringBoard did not start in the longest run \(memN, 400 s\), so the effect of the larger window on the later boot was not measured. The committed unixnu.toml itself \(default entry xnu-probe, wdt-kick=1800\) was not booted with this window: memN used entry xnu and wdt-kick=400.

### Next action

- None for the window itself. Watch the MEMMAP lines whenever a firmware driver is added or a PCD changes, and test that the contents of Data survive a reboot \(storage area\).

### Evidence

- `source`: [Memory node memory@100000000: the window's worth of the 4 GiB bank the kernel's memory comes from](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/dts/orangepi5.dts)
- `device`: [The firmware's memory maps \(MEMMAP log\) before and after the ACPI and PCD fixes, the refused and the accepted window sizes, the 2.5 GiB boot and the 3.5 GiB, 4094 MiB and 3.875 GiB boots from the 4 GiB bank to launchd, and the PPTT cause of the two AcpiTableDxe crashes](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/evidence/device-memory-20261103.txt)
  Command: <code>cd uefi-orangepi5 &amp;&amp; CAPTURE_ARGS="--send 'menu: shown' text:1 --send 'U-Boot v' ctrl-c --stop '&lt;INTERRUPT&gt;' 1 'at the U-Boot prompt'" tools/board/capture-remote.sh memN 700 (ESP files written through U-Boot with uboot-put.py; docs/first-boot.md)</code>. Revision: `1cbc693ca1c335720f0c4ae48665320e05390b4d`.
- `device`: [The memory the firmware reports on the 8 GiB board and the kernel booting with the 2 GiB window of the first runs \(capture auto1, section 2\)](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/evidence/device-first-boot-20261103.txt)
  Command: <code>cd uefi-orangepi5 &amp;&amp; tools/board/capture-remote.sh auto1 330 (reset typed at the U-Boot prompt); CAPTURE_ARGS="--send 'menu: shown' text:1" tools/board/capture-remote.sh xnu1 480</code>. Revision: `b1d3c18fc1ba985101e5d3c372d18e59d0378df4`.

## Storage and root {#storage}

`device-verified`

Components: `AppleKeyStoreState`.

### Hardware and dependencies

- M.2 M-key slot on PCIe 2.0 x1 \(pcie2x1l2 through combphy0\_ps, reset GPIO3\_D1, 3.3 V enable GPIO0\_PC5\), a 128 GB NVMe drive for the ESP, the root image and the Data volume; the eMMC socket and the microSD slot are left unused.

### Configuration

- board.toml \[userdata\]: an ESP of 256 MiB at LBA 2048 and a 64 GiB userdata partition at LBA 526336..134744063, with the OS and SystemOS windows at its start and the Data window \(1 MiB header + 2 GiB container\) at its end.
- dts/orangepi5.dts exports /arm-io/pcie-nvme \(compatible unixnu,rk3588-pcie-nvme, no reg, no interrupts\) and keeps the pcie@fe190000 node disabled; patches/xnu/orangepi5-nvme-personality.patch matches NativeNvme to it.
- Boot arguments nvme=4, nvme-root-trust=1, nvme-data-size=2048, nvme-data-persist=1; probe-only runs use nvme=1.

### Procedure

- Write GPT, ESP \(payload\) and userdata to the drive with uefi-orangepi5 tools/board/nvme-install.py from a Linux booted on the board, then boot; the driver publishes the OS and SystemOS windows read-only and the Data window writable.

### Development findings

- package/Rk3588Nvme follows the EVB10 eMMC driver above the controller \(GPT scan, SHNGROOT root image, Data window, kernel hooks, watchdog feeder, PMGR nub\) and has its own host: PCIe bring-up from the state edk2-rk3588 leaves, a polled NVMe controller core \(reset, admin queue, identify, one I/O queue pair, PRP transfers through a contiguous bounce window, writes only inside the Data window\).
- Host-verified: the NVMe core and the GPT reader against a controller model behind a non-coherent cache \(seven mutations of the core are caught\), the root manifest reader, the BAR window classification \(four mutations caught\), the driver compiled with -Werror and bound to the original IOBlockStorageDevice \(190 slots, 11 imports\), the kernel link and its bound-address check, and the installer's GPT through the driver's own reader.
- Observed on the board \(evidence/device-first-boot-20261103.txt, sections 4 and 6\): the PCIe controller addresses derived from the sources of edk2-rk3588 are right \(APB 0xfe190000, DBI 0xa41000000, CFG0 0xa36500000: vendor 0x126f device 0x2263 class 0x10802 at 00:00.0, LTSSM L0\); the drive is a Silicon Motion NE-128 with 250069680 512-byte blocks; the controller is enabled as the firmware leaves it and the driver resets and initialises it; GPT and the SHNGROOT header are read; the probe reads 4096 blocks twice with the same CRC at 72 MiB/s, 0 retries, 0 failures; the OS \(5796 MiB\) and SystemOS \(3150 MiB\) windows are published and the root device is accepted; the Data window is formatted at the first boot \(64 MiB zeroed, 9216 KiB seed, 534 ms\) and published writable \(650 write calls, 0 failures\); launchd starts 29 s after the hand-off and the kernel runs the 400 s until the capture ends without a panic.
- Found on the board and fixed \(b1d3c18f\): BAR0 is a 64-bit non-prefetchable BAR that edk2 places in the 32-bit window \(bus 0xf0000000, CPU 0xa38000000\); the first version of the driver took every 64-bit BAR for the 64-bit window and refused it. The run that carried the fix logged "BAR0 0xf0000000 \(64-bit, not prefetchable\) is at CPU address 0xa38000000" and everything after it worked.
- The link: the firmware \(2.5 GT/s\) and the kernel \(link status Gen1 x1\) see Gen1 where U-Boot reported Gen2 x1 for its own link-up; the driver does not retrain the link.
- The kernel patches of the EVB10 call two Mali hooks \(mali\_gpu\_addon, mali\_test\_file\); the driver defines weak versions that answer none until a display archive is linked.
- Design debts: the storage code is duplicated between Rk3588Emmc and Rk3588Nvme \(a fix to the shared parts goes into both\); the headers Gpt.h, RootManifest.h and StorageCommon.h are copies with the namespace renamed; the first round keeps the 2 GiB Data container of the existing seed.
- Second and later boots \(evidence/device-memory-20261103.txt, section 8\): the Data window's header is found again \('version 1 state 2 ... formatted 1 times'\) and Data mounts writable on /dev/disk3s1, the OS window as the read-only root, with the new ADT of the memory change \(memory node memory@40000000, 2.5 GiB window\); the driver does not read the memory node.
- scripts/build-orangepi5-drivers.py also builds the display objects and the Mali driver now \(components NativeLegacyDisplay, NativeGOPPresenter, NativeKeyStoreEvents, Mali\); the Rk3588Nvme entry and its bind step are unchanged and the bound-address check still passes on the two-pass kernel \(18 addresses inside the audited IOStorageFamily, evidence/host-display-build-20261103.txt and host-gpu-build-20261103.txt\).
- When wdt-kick expires, NativeNvme also writes CRU\_GLB\_SRST\_FST \(0xFDB9\) so the board soft-resets to U-Boot if the hardware watchdog does not fire \(observed while deploying the VOP kernel\).

### Completion criteria

- The kernel mounts the root and Data volumes from the NVMe drive and launchd starts.

### Current limits

- Boots after the first \(hdmi3, memH, memI\) found the Data window's header \('formatted 1 times'\) and mounted it writable without formatting; that contents written in one boot are read in the next, long write loads and the cache handling under them were not checked.
- The probe's 72 MiB/s is below what the Gen1 x1 link can carry; whether the link or the polled bounce-window reads limit it was not measured.
- Only 512-byte logical blocks are supported.

### Next action

- Write a marker file to Data, reboot and read it back, then measure the read speed with a larger probe \(nvme-probe=N\) and decide whether the link or the driver limits it.

### Evidence

- `source`: [Driver structure, host checks and the list of unverified hardware assumptions](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/package/Rk3588Nvme/README.md)
- `host`: [Host tests, -Werror build, vtable binding, kernel link, payload and a full install of the NVMe image into a 128 GB sparse file with read-back; nothing ran on the board](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/evidence/host-nvme-storage-20261101.txt)
  Command: <code>g++ -std=c++17 -Wall -Wextra -Werror -O1 -I package/Rk3588Nvme package/Rk3588Nvme/tests/test-nvme-host.cpp -o /tmp/test-nvme-host &amp;&amp; /tmp/test-nvme-host</code>. Revision: `5cbaf4236c5f0a850a62daa341b1195956b4a63f`.
- `device`: [NVMe drive found over PCIe, GPT and SHNGROOT read, root windows published, Data window formatted and used, launchd running for 400 s without a panic \(captures auto1 with nvme=1 and xnu1 with nvme=4\)](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/evidence/device-first-boot-20261103.txt)
  Command: <code>cd uefi-orangepi5 &amp;&amp; tools/board/capture-remote.sh auto1 330 (reset typed at the U-Boot prompt); CAPTURE_ARGS="--send 'menu: shown' text:1" tools/board/capture-remote.sh xnu1 480</code>. Revision: `b1d3c18fc1ba985101e5d3c372d18e59d0378df4`.
- `device`: [Root and Data mount again on later boots with the 2.5 GiB window \(memI\) and the 3.875 GiB window \(memN\): the Data header is found \('formatted 1 times'\), no reformat](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/evidence/device-memory-20261103.txt)
  Command: <code>cd uefi-orangepi5 &amp;&amp; CAPTURE_ARGS="--send 'menu: shown' text:1" tools/board/capture-remote.sh memN 700 (unixnu.toml with wdt-kick=400)</code>. Revision: `1cbc693ca1c335720f0c4ae48665320e05390b4d`.

## Display {#display}

`device-verified`

Components: `GopFramebuffer`.

### Hardware and dependencies

- HDMI0 from VOP2 \(firmware VP2 + Esmart2, 1920x1080p60\), the UEFI GOP frame buffer as the boot surface, monitor mode from EDID.

### Configuration

- offline-legacy-\* / sheng-\* bind IOMobileFramebufferLegacy to NativeLegacyDisplay \(package/Opi5Display, force primary and IOMFBDisplayRefresh at sheng-vsync&gt;=60\).
- rk3588-vop-direct=1 uses UniXNU-rk3588-common Rk3588VopDirect: VOP IOMMU identity maps compositor surfaces and Esmart2 fetches them \(rk3588-vop-esmart=2 rk3588-vop-vp=2\); rk3588-vop-fence=1 waits for Mali before the flip. GOP CPU blit remains the fallback when iommu init fails.

### Procedure

- Build the two-pass display kernel, esp-put kernel/ADT/unixnu.toml, boot entry xnu, read opi5: display and rk3588: vop-direct lines.

### Development findings

- Firmware HDMI0 / GOP hand-off as in evidence/device-display-firmware-20261103.txt.
- GOP CPU copy path reached SpringBoard on the board \(landscape 1920x1080\) but cost about 53 ms per 8294400-byte frame.
- Shared VOP2 direct scanout \(SoC b5f5d94\) fixed page-table allocation for owned RAM above 4 GiB \(40-bit IOMMU PA\). On the board \(evidence/device-vop-direct-20261105.txt, kernel crc32 6612adcc\): vop direct iommu 1, flips 24, copy fallbacks 0, CPU copies 0; SpringBoard stayed up with Mali Metal.

### Completion criteria

- The kernel draws the boot screen on the HDMI monitor and SpringBoard appears.

### Current limits

- Person at the monitor has not re-confirmed the picture after the VOP switch \(serial only\).
- Flips stop once the lock screen is static; fence often waits on GPU work at first swaps.
- DVFS is not started from this probe.

### Next action

- Ask for a look at HDMI after VOP; measure frame rate under a gesture; start DVFS from the probe.

### Evidence

- `source`: [Display milestones](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/docs/bring-up.md)
- `host`: [The display kernel \(pass B of scripts/build-orangepi5-kernel.sh\) links: 51286016 bytes, sha256 2425c31b..., the display archive 95175c9f..., the NVMe bound-address check passes; nothing ran on the board](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/evidence/host-display-build-20261103.txt)
  Command: <code>source host/env.sh &amp;&amp; cd UniXNU-orangepi5 &amp;&amp; scripts/build-orangepi5-kernel.sh</code>. Revision: `f2831c1b913f29d664727a73847853a15450c4f3`.
- `device`: [The firmware drives HDMI0 at 1920x1080p60 \(VOP2 video port 2, Esmart 2\) and DarwinBoot hands the kernel a 1920x1080 32-bit frame buffer at 0xE73D0000, row 7680](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/evidence/device-display-firmware-20261103.txt)
  Command: <code>cd uefi-orangepi5 &amp;&amp; CAPTURE_ARGS="--send 'menu: shown' text:1 --send 'U-Boot v' ctrl-c --stop '&lt;INTERRUPT&gt;' 1 'at the U-Boot prompt'" tools/board/capture-remote.sh memN 700 (lines of the firmware and DarwinBoot)</code>. Revision: `1cbc693ca1c335720f0c4ae48665320e05390b4d`.
- `device`: [VOP2 direct scanout on HDMI0: iommu 1, flips 24, copy fallbacks 0, CPU copies 0 \(kernel crc32 6612adcc\)](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/evidence/device-vop-direct-20261105.txt)
  Command: <code>cd uefi-orangepi5 &amp;&amp; tools/board/esp-put.sh out/bundle/.../kernel.macho EFI/UniXNU/Payloads/kernel.macho; tools/board/capture-remote.sh vop2b 420</code>. Revision: `7b6f63f2b1ef4016636b3c55b00e48815bae471b`.

## Input {#input}

`implemented`

### Hardware and dependencies

- No on-board digitizer; software HID keyboard/digitizer stand-in \(EVB10 NativeHidInput\) so backboardd and SpringBoard have a digitizer node.

### Configuration

- opi5-hid=1 loads IOHIDFamily; opi5-hid-input=1 and sheng-touch-hid=1 start the owned HID input; libOpi5Hid.a is force-loaded by orangepi5\_display\_defconfig.

### Procedure

- Boot with the display kernel and read whether IOHIDEventDriver and the owned HID publish; real USB HID waits on xHCI.

### Development findings

- The Orange Pi 5 has no panel touch; the stand-in is enough for SpringBoard to run. Physical USB keyboard/mouse needs xHCI, not started.

### Completion criteria

- SpringBoard runs with a digitizer node published.

### Current limits

- No real pointer or keyboard on the board; scripted touch is not wired like EVB10's GT911 path.

### Next action

- xHCI + USB HID after the display path is stable.

### Evidence

- `source`: [Input is deferred](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/docs/bring-up.md)

## GPU {#gpu}

`device-verified`

Components: `GopFramebuffer`.

### Hardware and dependencies

- Mali-G610 at 0xfb000000, supply RK806 BUCK1 \(vdd\_gpu\_s0\), PanVK on Mesa and metal2vulkan from the EVB10 port.

### Configuration

- package/Mali linked; board.toml defaults mali=8 mali-metal=1 evb10-gpu-addon=1; uefi-orangepi5 make-bundle.sh switches to the owner trust cache and carries NativeMaliMetal.addon when those args are set.

### Procedure

- Boot the display+VOP kernel with mali=8 mali-metal=1; read mali: lines and SpringBoard composition.

### Development findings

- On the board with mali=8 mali-metal=1 \(same runs as the VOP evidence\): mali user status shows SpringBoard and poster extensions composing \(vkpipe failed=0\); VOP flips the Metal surfaces without a CPU copy.

### Completion criteria

- Mali composition runs on the Orange Pi 5.

### Current limits

- Frame rate under gesture not measured on this board; GPU rail/clock may still be the firmware default \(\~198 MHz\) unless DVFS or mali-npll is set; 5 GHz Wi-Fi and audio unrelated.

### Next action

- Gesture frame measurement; optional mali-npll / DVFS for higher clocks.

### Evidence

- `source`: [GPU milestone](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/docs/bring-up.md)
- `host`: [The kernel with package/Mali links: 51658752 bytes, sha256 9281cf98..., libMali.a 00ef7ebe..., the NVMe bound-address check passes; mali\_start\(\) returns without mali=N; nothing ran on the board](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/evidence/host-gpu-build-20261103.txt)
  Command: <code>source host/env.sh &amp;&amp; cd UniXNU-orangepi5 &amp;&amp; scripts/build-orangepi5-kernel.sh</code>. Revision: `ce6c6fb8d6f31b3c0a87dd4ead1f6d444c79f366`.
- `device`: [mali=8 mali-metal=1 with SpringBoard composing; VOP direct flips surfaces \(same capture as display\)](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/evidence/device-vop-direct-20261105.txt)
  Command: <code>cd uefi-orangepi5 &amp;&amp; tools/board/capture-remote.sh vop2b 420</code>. Revision: `7b6f63f2b1ef4016636b3c55b00e48815bae471b`.

## Network {#network}

`planned`

### Hardware and dependencies

- GMAC1 with an RGMII PHY \(gigabit Ethernet connector\), the on-board Wi-Fi and Bluetooth module \(not described in the mainline device tree, to be identified on the board\), USB Ethernet.

### Configuration

- Not configured. The firmware driver DwcEqosSnpDxe stays enabled in uefi-orangepi5 for later network boot.

### Procedure

- None in the first rounds.

### Development findings

- Not started; the EVB10 Wi-Fi and Ethernet work does not apply directly.

### Completion criteria

- Out of the first milestones.

### Current limits

- No network in the first rounds.

### Next action

- Decide between GMAC1 and a USB Ethernet adapter once storage and display work.

### Evidence

- `source`: [Network is deferred](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/docs/bring-up.md)

## Audio {#audio}

`planned`

### Hardware and dependencies

- ES8388 codec on I2C6 at 0x10 with I2S1 \(3.5 mm jack\) and HDMI audio on I2S5.

### Configuration

- Not configured.

### Procedure

- None in the first rounds.

### Development findings

- The EVB10 audio driver targets another codec; only the I2S controller part is shared.

### Completion criteria

- Out of the first milestones.

### Current limits

- No audio in the first rounds.

### Next action

- Port the I2S path after the display works.

### Evidence

- `source`: [Audio is deferred](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/docs/bring-up.md)

## Power {#power}

`planned`

### Hardware and dependencies

- RK806 PMIC on SPI \(BUCK1 GPU, BUCK2 little cores\), RK8602 and RK8603 at 0x42 and 0x43 on I2C0 for the big cores, HYM8563 RTC at I2C6 0x51, a PWM fan header, no remote power switch.

### Configuration

- The firmware initialises the rails; the GPU rail is set to 0.75 V at build time \(GPU\_RAIL\_UV in uefi-orangepi5\). The kernel keeps the hardware watchdog fed with wdt-kick=1800.

### Procedure

- Run the kernel and read the watchdog behaviour on the serial console; CPU and GPU frequency management reuse the EVB10 DVFS tables once the probe hook exists.

### Development findings

- The board has no remote reset controller; wdt-kick feeds the hardware watchdog.
- When the feed window ends, NativeNvme also writes CRU\_GLB\_SRST\_FST \(0xFD7C0A00 = 0xFDB9\) so the board returns to U-Boot without a pull-plug \(observed: soft reset then U-Boot banner\).
- DVFS tables from the SoC repository are not started from the Orange Pi 5 probe yet.

### Completion criteria

- The kernel runs for minutes without a reset and the frequencies follow the load.

### Current limits

- DVFS is still not hooked on this board; soft reset is not a substitute for a remote reset controller during firmware hangs.

### Next action

- Start Rk3588Dvfs from the display probe \(board rail table\).

### Evidence

- `source`: [wdt-kick and the firmware watchdog hand-off](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/board.toml)

## Image assembly {#packaging}

`device-verified`

Components: `XnuPrelink`, `DarwinBoot`, `SoftwareAES`.

### Hardware and dependencies

- Kernel from orangepi5\_defconfig with the NVMe driver, the original trust cache bundle, the 2 GiB Data seed and unixnu.toml of the payload, the 256 MiB OPI5ESP payload volume that goes on the NVMe ESP, the 9.4 GB root image.

### Configuration

- payload.loader = firmware: the loader is part of the firmware volume of uefi-orangepi5, so the payload carries no loader image.

### Procedure

- unixnu build kernel, then uefi-orangepi5 tools/board/make-bundle.sh \(unixnu build payload, the power-off menu entry removed, bundle with the firmware image and the root image\); nvme-install.py writes the ESP of the drive.

### Development findings

- The SoC patch rk3588-root-trust.patch makes bsd\_init.c call native\_emmc\_root\_trusted; the NVMe driver defines it, so the stub patch of the console kernel is gone.
- The five EVB10 kernel patches \(exit trace, mmap grant, thread sample, userland mounts, vc mirror\) are vendored with their source commit; the NVMe personality patch is the board's own.
- The payload assembles on the host \(payload.img 256 MiB, ADT with the pcie-nvme node\) and the board started it \(evidence/device-first-boot-20261103.txt\): the firmware read kernel.macho, its ADT and trust cache from the NVMe ESP, DarwinBoot handed the kernel over, the driver bound to the original IOBlockStorageDevice and the kernel booted to launchd. The ADT memory values were placeholders in those runs; they are the measured ones now \(memory area\).
- The package gained PcieWindows.h and its host test \(tests/test-pcie-windows.cpp\) after the first run showed the BAR in the 32-bit window; the kernel was rebuilt and the bound-address check still passes \(18 addresses inside the audited IOStorageFamily, kernel.macho sha256 178d2e1f...\).
- The SoC repository is pinned in feeds.toml; local.toml can point at a checkout during development.
- The kernel is now built in two passes \(configs/orangepi5\_defconfig, then orangepi5\_display\_defconfig\) and the payload comes from the second one: package/LegacyDisplayProbe.cpp, KeyStoreProbe.cpp and LinkStubs.c are the display pass's device code, tools/board/make-bundle.sh of uefi-orangepi5 selects the kernel by KERNEL\_CONFIG \(default the display kernel\), and board.toml carries the display archive, the GopFramebuffer component and the offline-legacy-\* / sheng-\* arguments \(553 of 1000 bytes\). Host-verified in evidence/host-display-build-20261103.txt; the ADT of a payload build differs from build to build while the kernel does not.
- package/Mali is a submodule now \(Ken-u/Mali, the EVB10's commit 9dd949a; the pointer is staged with the change that adds it, otherwise unixnu resets it to the index\). The payload of the Mali-linked display kernel is kernel.macho 51658752 bytes crc32 7bec4f41, ADT crc32 970b5293 \(the ADT differs per payload build\), trust cache e3343405 and unixnu.toml fe909e88 unchanged; the ESP of the board still holds the display kernel without Mali \(f7215c41, written, not verified\).
- Later esp-put \(tools/board/esp-put.sh\) verified kernel.macho crc32 6612adcc \(VOP+Mali+HID display kernel\), ADT and unixnu.toml on the NVMe ESP; make-bundle.sh carries the GPU addon and owner trust when evb10-gpu-addon=1.

### Completion criteria

- The payload boots from the NVMe ESP through the firmware and reaches the kernel entry.

### Current limits

- The vendored EVB10 patches keep the EVB10 names and drift when the EVB10 repository changes \(scripts/check-vendored-patches.sh shows it\).
- The payload was started from U-Boot through the launcher only; the SPI NOR route has not run.
- Default menu entry is still xnu-probe.

### Next action

- DEFAULT\_ENTRY=xnu MENU\_TIMEOUT=3 tools/board/make-bundle.sh and rewrite esp.img.

### Evidence

- `source`: [Kernel build driver](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/scripts/build-orangepi5-kernel.sh)
- `host`: [Pass B of the kernel build \(display\) links and the payload of the display kernel assembles with the display arguments; the ADT differs between payload builds, the kernel does not; nothing ran on the board](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/evidence/host-display-build-20261103.txt)
  Command: <code>source host/env.sh &amp;&amp; cd UniXNU-orangepi5 &amp;&amp; scripts/build-orangepi5-kernel.sh &amp;&amp; cd ../uefi-orangepi5 &amp;&amp; REBUILD=1 tools/board/make-bundle.sh</code>. Revision: `f2831c1b913f29d664727a73847853a15450c4f3`.
- `host`: [The payload assembles \(256 MiB FAT volume with kernel, ADT, trust cache and Data seed\) and the bundle installs into a 128 GB image with read-back; the board has not started it](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/evidence/host-nvme-storage-20261101.txt)
  Command: <code>cd UniXNU &amp;&amp; host/in-ns.sh ./unixnu build payload -D ../UniXNU-orangepi5 --unique-chip-id ID --trust-cache original-static-system.bundle --data-ramdisk owner-data-2048.trim.img</code>. Revision: `5cbaf4236c5f0a850a62daa341b1195956b4a63f`.
- `host`: [The console kernel linked to a 51019776-byte arm64 Mach-O executable with the first board patch series \(superseded by the NVMe kernel above\)](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/evidence/host-kernel-build-20261101.txt)
  Command: <code>source host/env.sh &amp;&amp; cd UniXNU-orangepi5 &amp;&amp; scripts/build-orangepi5-kernel.sh</code>. Revision: `f4bb6e952e915f4f837547f11981ca26b61a5c46`.
- `device`: [The payload on the NVMe ESP was started by the firmware, the kernel with the NVMe driver booted to launchd \(capture xnu1\)](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/evidence/device-first-boot-20261103.txt)
  Command: <code>cd uefi-orangepi5 &amp;&amp; CAPTURE_ARGS="--send 'menu: shown' text:1" tools/board/capture-remote.sh xnu1 480</code>. Revision: `b1d3c18fc1ba985101e5d3c372d18e59d0378df4`.

## Diagnostics {#diagnostics}

`device-verified`

### Hardware and dependencies

- UART2 on the 3-pin debug header at 1.5 Mbaud 8N1; the firmware prints its own log on the same port.

### Configuration

- serial=3 and debug=0x10014e keep the kernel console on UART2 and restart after a panic.

### Procedure

- Attach a 3.3 V USB serial adapter to the debug header and capture from power-on.

### Development findings

- The serial adapter is on the board host \(UART2 at 1.5 Mbaud\) and the first two captures are stored as excerpts in evidence/device-first-boot-20261103.txt \(the raw logs stay out of the repository\).
- uefi-orangepi5 tools/board/capture.sh and capture-remote.sh record the port with times \(serial-capture.py of the SoC repository, which can also type keys after a matching line: --send\); docs/first-boot.md of that repository lists the log lines that settle each step \(firmware, PCIe, NVMe, GPT, root, Data, userland\) and what each failure means.
- The driver's PCIe, controller and identify lines did show which derived assumption was wrong \(the BAR window\) in the first log, as planned.
- The USB serial adapter re-enumerates when the board resets: a long capture on /dev/ttyUSB0 went silent at the watchdog reset while the board kept running. serial-capture.py now stops with '\# device closed' \(or 'read error'\) when the line goes away, and capture-remote.sh takes the device from BOARD\_SERIAL\_DEV.
- The firmware's memory map is in the serial log \(MEMMAP lines of UniXNUMemMapDxe: before the menu, when it changes, and at ExitBootServices\); capture-remote.sh can type Ctrl-C at the U-Boot banner \(--send 'U-Boot v' ctrl-c,...\) and stop on the prompt, so a run starts and ends without anyone at the board.
- evidence/device-display-firmware-20261103.txt is cut from the same capture as the memory evidence \(memN\); the EDID dump is left out of it because it carries the monitor's serial number \(the lines about the EDID stay\).
- The host records of the display and Mali builds \(evidence/host-display-build-20261103.txt, host-gpu-build-20261103.txt\) state which checksums were written to the ESP over U-Boot and which were verified; the file written last \(the display kernel without Mali, f7215c41\) is the one whose read back aborted U-Boot and is unverified.
- evidence/device-vop-direct-20261105.txt is an excerpt of capture vop2b after esp-put verified kernel crc32 6612adcc: VOP direct iommu 1 with zero CPU copies.

### Completion criteria

- A boot log from the board is stored with the evidence.

### Current limits

- Excerpts, not the raw logs, are kept in the repository; each evidence file names the command that repeats its run.

### Next action

- Capture a cold power-on run and the second boot over the formatted Data window and add them as evidence.

### Evidence

- `source`: [Repository overview and status](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/README.md)
- `device`: [The first serial logs of the board, excerpted](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/evidence/device-first-boot-20261103.txt)
  Command: <code>cd uefi-orangepi5 &amp;&amp; tools/board/capture-remote.sh auto1 330 (reset typed at the U-Boot prompt); CAPTURE_ARGS="--send 'menu: shown' text:1" tools/board/capture-remote.sh xnu1 480</code>. Revision: `b1d3c18fc1ba985101e5d3c372d18e59d0378df4`.
- `device`: [HDMI text mirror, the watchdog reset and the adapter that drops off the bus, excerpted](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/evidence/device-hdmi-watchdog-20261103.txt)
  Command: <code>cd uefi-orangepi5 &amp;&amp; CAPTURE_ARGS="--send 'menu: shown' text:2" tools/board/capture-remote.sh hdmi3 1500 /dev/serial/by-id/ADAPTER</code>. Revision: `b1d3c18fc1ba985101e5d3c372d18e59d0378df4`.
- `host`: [Checksums of the Mali-linked display kernel and its payload \(kernel crc32 7bec4f41\), and what the ESP holds](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/evidence/host-gpu-build-20261103.txt)
  Command: <code>source host/env.sh &amp;&amp; cd UniXNU-orangepi5 &amp;&amp; scripts/build-orangepi5-kernel.sh &amp;&amp; cd ../uefi-orangepi5 &amp;&amp; REBUILD=1 tools/board/make-bundle.sh</code>. Revision: `ce6c6fb8d6f31b3c0a87dd4ead1f6d444c79f366`.
- `device`: [Serial excerpt after VOP direct kernel on the ESP \(iommu 1, zero CPU copies\)](https://github.com/Ken-u/UniXNU-orangepi5/blob/f96d273b526254d700bd42bfeadef0359a1d3c46/evidence/device-vop-direct-20261105.txt)
  Command: <code>cd uefi-orangepi5 &amp;&amp; tools/board/capture-remote.sh vop2b 420</code>. Revision: `7b6f63f2b1ef4016636b3c55b00e48815bae471b`.

</div>
