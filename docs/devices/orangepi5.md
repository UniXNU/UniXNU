# Orange Pi 5 \(Rockchip RK3588S\)

[Ken-u/UniXNU-orangepi5](https://github.com/Ken-u/UniXNU-orangepi5)

<div v-pre>

Orange Pi 5 \(Rockchip RK3588S\) with an HDMI display and an M.2 NVMe drive, planned to run the iPadOS 17.7.11 userland on a source-built XNU, started from edk2-rk3588 firmware \(uefi-orangepi5\). Shared SoC support is in UniXNU-rk3588-common, which the EVB10 port already proved on hardware. Nothing in this repository has run on an Orange Pi 5 yet: the configuration resolves, the kernel with the NVMe driver builds and links, and the payload and the NVMe image are assembled and checked on the host; every area below records what is still to be measured.

Source record: [porting.toml](https://github.com/Ken-u/UniXNU-orangepi5/blob/d3968fa094623272ea46ebd2e142c6d6eb69da1f/porting.toml), `d3968fa094623272ea46ebd2e142c6d6eb69da1f`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `host-verified` |
| [Firmware and boot](#firmware) | `planned` |
| [CPU and interrupts](#cpu) | `implemented` |
| [Memory and DMA](#memory) | `planned` |
| [Storage and root](#storage) | `host-verified` |
| [Display](#display) | `planned` |
| [Input](#input) | `not-applicable` |
| [GPU](#gpu) | `planned` |
| [Network](#network) | `planned` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `planned` |
| [Image assembly](#packaging) | `host-verified` |
| [Diagnostics](#diagnostics) | `planned` |

## Configuration {#configuration}

`host-verified`

### Hardware and dependencies

- ARM64 profile, rk3588 SoC source pinned in feeds.toml, iPadOS 17.7.11 build 21H461 profile, orangepi5\_defconfig.

### Configuration

- board.soc\_source = rk3588; board.os\_profile = ipados-17.7.11-21H461; schema\_version = 2.
- orangepi5\_defconfig keeps the console kernel with NVMe storage: no display, no GPU, no RAM disk, no UFS; the trust-cache runtime and the code-signing hash cache stay on.
- \[adt.defaults.u32\] carries sleep-disabled = 1 and vmm-present = 1, which the EVB10 port found necessary for watchdogd.

### Procedure

- From the UniXNU checkout run ./unixnu defconfig orangepi5\_defconfig -D ../UniXNU-orangepi5, then ./unixnu fetch, ./unixnu status --json and ./unixnu tree with the same -D.
- scripts/build-orangepi5-kernel.sh runs the kernel build; it needs the environment of the machine that builds \(.env\) and CMake 3.19.6 or newer.

### Development findings

- Resolution is host-verified: defconfig, fetch, status --json and tree complete against the pinned SoC repository.
- The UniXNU bootstrap pass builds AvailabilityVersions with CMake; the distribution CMake of Ubuntu 20.04 is 3.16 and fails, so the build script puts /usr/local/bin first.
- The kernel now carries the NVMe driver: board.toml archives build-orangepi5-drivers.py Rk3588Nvme and bind-nvme-storage.py, the defconfig force-loads libRk3588Nvme.a, and the build script verifies the bound addresses against the kernel \(18 addresses inside the audited IOStorageFamily\).
- board.toml \[userdata\] is the layout of the 128 GB drive: userdata at LBA 526336..134744063 behind a 256 MiB ESP at LBA 2048; the boot arguments are the EVB10 ones with the storage names of the NVMe driver \(nvme=4, nvme-root-trust=1, nvme-data-size=2048, nvme-data-persist=1\).

### Completion criteria

- Every source pin resolves, ./unixnu status lists the intended patch order, and the defconfig materialises.

### Current limits

- The kernel configuration is the console minimum; storage, display, GPU and input join it as those drivers exist \(docs/bring-up.md\).

### Next action

- Add the display archive to board.toml when the display driver exists.

### Evidence

- `source`: [Board configuration of the console kernel](https://github.com/Ken-u/UniXNU-orangepi5/blob/d3968fa094623272ea46ebd2e142c6d6eb69da1f/board.toml)
- `host`: [The kernel with the NVMe driver links and the bound-address check passes \(51154944 bytes, sha256 76ba878c...\); nothing ran on the board](https://github.com/Ken-u/UniXNU-orangepi5/blob/d3968fa094623272ea46ebd2e142c6d6eb69da1f/evidence/host-nvme-storage-20261101.txt)
  Command: <code>source host/env.sh &amp;&amp; cd UniXNU-orangepi5 &amp;&amp; scripts/build-orangepi5-kernel.sh</code>. Revision: `5cbaf4236c5f0a850a62daa341b1195956b4a63f`.
- `host`: [defconfig, fetch, status, tree and the full console kernel build complete on the host; nothing ran on the board](https://github.com/Ken-u/UniXNU-orangepi5/blob/d3968fa094623272ea46ebd2e142c6d6eb69da1f/evidence/host-kernel-build-20261101.txt)
  Command: <code>source host/env.sh &amp;&amp; cd UniXNU-orangepi5 &amp;&amp; scripts/build-orangepi5-kernel.sh</code>. Revision: `f4bb6e952e915f4f837547f11981ca26b61a5c46`.

## Firmware and boot {#firmware}

`planned`

### Hardware and dependencies

- edk2-rk3588 firmware built by uefi-orangepi5 \(an SPI NOR image with TF-A at EL3, OP-TEE and the UEFI volume\), UEFI GOP frame buffer on HDMI0.

### Configuration

- board.toml has no \[firmware\] section: the unixnu firmware step builds Mu-Silicium, and this board boots edk2-rk3588 built by uefi-orangepi5.
- payload.loader = firmware: DarwinBoot is inside the firmware volume and reads the payload from the ESP of the NVMe drive, found through NvmExpressDxe.

### Procedure

- Build the firmware in uefi-orangepi5 \(build.sh\); tools/board/spi-flash.sh of that repository writes the SPI NOR image from a Linux booted on the board \(backup first, flashcp, compare\), or Maskrom mode when /proc/mtd does not list the flash. Both are described in uefi-orangepi5/docs/first-boot.md.

### Development findings

- The firmware builds on the host with the GPU rail set to 0.75 V and the hardware watchdog driver of uefi-orangepi5 armed \(the board has no remote power switch, so a hung kernel must end in a watchdog reset\).
- Not yet observed on the board: the UEFI banner, the DRAM size, the PCIe link of the NVMe drive and the GOP resolution.
- The firmware image is a bundle member \(nor.img\) built by uefi-orangepi5 tools/board/make-bundle.sh; spi-flash.sh was checked for its /proc/mtd parsing only, it has not touched a flash.

### Completion criteria

- Firmware enters DarwinBoot, publishes the GOP frame buffer and finds the NVMe ESP.

### Current limits

- No hardware access so far: serial console, flashing method and the board's RAM size are open inputs.

### Next action

- Connect the board \(UART2 at 1.5 Mbaud, HDMI, NVMe\), write the NOR image and record the first firmware log.

### Evidence

- `source`: [Boot flow and milestones M0 to M4](https://github.com/Ken-u/UniXNU-orangepi5/blob/d3968fa094623272ea46ebd2e142c6d6eb69da1f/docs/bring-up.md)

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

- `source`: [Board device tree on top of the shared SoC description](https://github.com/Ken-u/UniXNU-orangepi5/blob/d3968fa094623272ea46ebd2e142c6d6eb69da1f/dts/orangepi5.dts)

## Memory and DMA {#memory}

`planned`

### Hardware and dependencies

- The board of this port has 8 GiB of LPDDR4x; the RK3588 maps DRAM in two banks \(below 0xf0000000, 3.75 GiB, and from 0x100000000, 4.25 GiB\) around the peripheral window and the reserved regions of the firmware.

### Configuration

- The memory node and payload.dram\_size are placeholders for 4 GiB at 0x100000000; payload.adt.owned\_memory\_size = 0x80000000 takes 2 GiB from the UEFI memory map.

### Procedure

- Read the memory map from the firmware log of the first run and replace both placeholders; keep the kernel's 2 GiB inside the bank the firmware reports as conventional memory.

### Development findings

- The 4 GiB node at 0x100000000 lies inside the upper bank of an 8 GiB board; it is the value of the EVB10 port, not yet compared with this board's memory map. The NVMe driver does not depend on where DarwinBoot puts the kernel's pages: its DMA window accepts any address below 1 TiB.
- Not yet measured. The EVB10 port found that DarwinBoot takes contiguous memory from the UEFI memory map and that the shared-region and DRAM-carve-out sizes must agree with the ADT.

### Completion criteria

- The kernel reports the memory it owns and the ADT memory ranges match the firmware map.

### Current limits

- Where DarwinBoot places the 2 GiB of kernel pages is known only from the first firmware log.

### Next action

- Capture the UEFI memory map on the board.

### Evidence

- `source`: [Placeholder memory node](https://github.com/Ken-u/UniXNU-orangepi5/blob/d3968fa094623272ea46ebd2e142c6d6eb69da1f/dts/orangepi5.dts)

## Storage and root {#storage}

`host-verified`

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
- Host-verified: the NVMe core and the GPT reader against a controller model behind a non-coherent cache \(seven mutations of the core are caught\), the root manifest reader, the driver compiled with -Werror and bound to the original IOBlockStorageDevice \(190 slots, 11 imports\), the kernel link and its bound-address check, and the installer's GPT through the driver's own reader.
- Not observed on the board: the PCIe controller addresses \(APB 0xfe190000, DBI 0xa41000000, CFG0 0xa36500000, the BAR windows\) are derived from the sources of edk2-rk3588, the controller state the firmware leaves, the drive's BAR placement, its model and LBA format, and DMA coherence of the bounce window.
- The kernel patches of the EVB10 call two Mali hooks \(mali\_gpu\_addon, mali\_test\_file\); the driver defines weak versions that answer none until a display archive is linked.
- Design debts: the storage code is duplicated between Rk3588Emmc and Rk3588Nvme \(a fix to the shared parts goes into both\); the headers Gpt.h, RootManifest.h and StorageCommon.h are copies with the namespace renamed; the first round keeps the 2 GiB Data container of the existing seed.

### Completion criteria

- The kernel mounts the root and Data volumes from the NVMe drive and launchd starts.

### Current limits

- Nothing in this area has run on the board; the first log decides whether the derived addresses and the cache handling hold.
- Only 512-byte logical blocks are supported.

### Next action

- Boot with nvme=1 first and read the pcie:, NVMe and probe lines, then nvme=4 for the root volume \(uefi-orangepi5/docs/first-boot.md\).

### Evidence

- `source`: [Driver structure, host checks and the list of unverified hardware assumptions](https://github.com/Ken-u/UniXNU-orangepi5/blob/d3968fa094623272ea46ebd2e142c6d6eb69da1f/package/Rk3588Nvme/README.md)
- `host`: [Host tests, -Werror build, vtable binding, kernel link, payload and a full install of the NVMe image into a 128 GB sparse file with read-back; nothing ran on the board](https://github.com/Ken-u/UniXNU-orangepi5/blob/d3968fa094623272ea46ebd2e142c6d6eb69da1f/evidence/host-nvme-storage-20261101.txt)
  Command: <code>g++ -std=c++17 -Wall -Wextra -Werror -O1 -I package/Rk3588Nvme package/Rk3588Nvme/tests/test-nvme-host.cpp -o /tmp/test-nvme-host &amp;&amp; /tmp/test-nvme-host</code>. Revision: `5cbaf4236c5f0a850a62daa341b1195956b4a63f`.

## Display {#display}

`planned`

### Hardware and dependencies

- HDMI0 from VOP2 video port 0 \(the EVB10 drives a panel through video port 2\), UEFI GOP frame buffer, monitor mode chosen by EDID.

### Configuration

- The first milestone uses the GOP frame buffer DarwinBoot publishes \(component GopFramebuffer, offline-legacy-gop=1\); a VOP2 scanout driver on the Esmart window of video port 0 follows for frame rate.

### Procedure

- Boot the kernel with the GOP frame buffer and look at the monitor; then adapt the EVB10 VOP2 code to video port 0 and the monitor timing.

### Development findings

- The EVB10 VOP2 constants \(evb10-vop, evb10-fb-w, evb10-fb-h, video port, window\) are board specific; the Orange Pi 5 needs its own values.

### Completion criteria

- The kernel draws the boot screen on the HDMI monitor and SpringBoard appears.

### Current limits

- Not started; needs the board and a monitor.

### Next action

- Record the GOP mode and the VOP2 state left by the firmware.

### Evidence

- `source`: [Display milestones](https://github.com/Ken-u/UniXNU-orangepi5/blob/d3968fa094623272ea46ebd2e142c6d6eb69da1f/docs/bring-up.md)

## Input {#input}

`not-applicable`

### Hardware and dependencies

- The first round is display only: no keyboard, mouse or touch device is attached.

### Configuration

- No input driver is configured; xHCI on USB host 0 and 2 \(and a HID class driver\) join later.

### Procedure

- None in this round.

### Development findings

- The Orange Pi 5 has no on-board input device; input means a USB keyboard or mouse through xHCI, which the EVB10 port does not cover \(its touch controller sits on I2C\).

### Completion criteria

- Not applicable until USB input is requested.

### Current limits

- Out of scope of the current milestones.

### Next action

- Plan an xHCI and HID driver after the display works.

### Evidence

- `source`: [Input is deferred](https://github.com/Ken-u/UniXNU-orangepi5/blob/d3968fa094623272ea46ebd2e142c6d6eb69da1f/docs/bring-up.md)

## GPU {#gpu}

`planned`

### Hardware and dependencies

- Mali-G610 at 0xfb000000, supply RK806 BUCK1 \(vdd\_gpu\_s0\), PanVK on Mesa and metal2vulkan from the EVB10 port.

### Configuration

- Not in the kernel yet; the Mali driver submodule and the Metal stack of the EVB10 port are board independent apart from the rail table.

### Procedure

- After the display scans out, enable the Mali archive and the composition path of the EVB10 and measure a frame.

### Development findings

- The EVB10 port reached about 15 ms per heavy command buffer with the GPU at 750 MHz; the Orange Pi 5 uses the same SoC and rail, so the same driver is expected to work.

### Completion criteria

- Mali composition runs on the Orange Pi 5.

### Current limits

- Not started.

### Next action

- Reuse package/Mali after the display milestone.

### Evidence

- `source`: [GPU milestone](https://github.com/Ken-u/UniXNU-orangepi5/blob/d3968fa094623272ea46ebd2e142c6d6eb69da1f/docs/bring-up.md)

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

- `source`: [Network is deferred](https://github.com/Ken-u/UniXNU-orangepi5/blob/d3968fa094623272ea46ebd2e142c6d6eb69da1f/docs/bring-up.md)

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

- `source`: [Audio is deferred](https://github.com/Ken-u/UniXNU-orangepi5/blob/d3968fa094623272ea46ebd2e142c6d6eb69da1f/docs/bring-up.md)

## Power {#power}

`planned`

### Hardware and dependencies

- RK806 PMIC on SPI \(BUCK1 GPU, BUCK2 little cores\), RK8602 and RK8603 at 0x42 and 0x43 on I2C0 for the big cores, HYM8563 RTC at I2C6 0x51, a PWM fan header, no remote power switch.

### Configuration

- The firmware initialises the rails; the GPU rail is set to 0.75 V at build time \(GPU\_RAIL\_UV in uefi-orangepi5\). The kernel keeps the hardware watchdog fed with wdt-kick=1800.

### Procedure

- Run the kernel and read the watchdog behaviour on the serial console; CPU and GPU frequency management reuse the EVB10 DVFS tables once the probe hook exists.

### Development findings

- The board has no reset controller: a hung kernel ends in the watchdog reset \(about 89 seconds without wdt-kick\), a hung firmware needs a manual power cycle.
- Not yet observed on the board.

### Completion criteria

- The kernel runs for minutes without a reset and the frequencies follow the load.

### Current limits

- The DVFS probe of the EVB10 is started from its display probe; the Orange Pi 5 needs its own start hook.

### Next action

- Observe the first boot, then enable DVFS.

### Evidence

- `source`: [wdt-kick and the firmware watchdog hand-off](https://github.com/Ken-u/UniXNU-orangepi5/blob/d3968fa094623272ea46ebd2e142c6d6eb69da1f/board.toml)

## Image assembly {#packaging}

`host-verified`

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
- The payload assembles on the host \(payload.img 256 MiB, ADT with the pcie-nvme node\); the ADT memory values are still the placeholders.
- The SoC repository is pinned in feeds.toml; local.toml can point at a checkout during development.

### Completion criteria

- The payload boots from the NVMe ESP through the firmware and reaches the kernel entry.

### Current limits

- The vendored EVB10 patches keep the EVB10 names and drift when the EVB10 repository changes \(scripts/check-vendored-patches.sh shows it\).
- The payload has not been started by the firmware.

### Next action

- Start the payload on the board and replace the memory placeholders with the first log.

### Evidence

- `source`: [Kernel build driver](https://github.com/Ken-u/UniXNU-orangepi5/blob/d3968fa094623272ea46ebd2e142c6d6eb69da1f/scripts/build-orangepi5-kernel.sh)
- `host`: [The payload assembles \(256 MiB FAT volume with kernel, ADT, trust cache and Data seed\) and the bundle installs into a 128 GB image with read-back; the board has not started it](https://github.com/Ken-u/UniXNU-orangepi5/blob/d3968fa094623272ea46ebd2e142c6d6eb69da1f/evidence/host-nvme-storage-20261101.txt)
  Command: <code>cd UniXNU &amp;&amp; host/in-ns.sh ./unixnu build payload -D ../UniXNU-orangepi5 --unique-chip-id ID --trust-cache original-static-system.bundle --data-ramdisk owner-data-2048.trim.img</code>. Revision: `5cbaf4236c5f0a850a62daa341b1195956b4a63f`.
- `host`: [The console kernel linked to a 51019776-byte arm64 Mach-O executable with the first board patch series \(superseded by the NVMe kernel above\)](https://github.com/Ken-u/UniXNU-orangepi5/blob/d3968fa094623272ea46ebd2e142c6d6eb69da1f/evidence/host-kernel-build-20261101.txt)
  Command: <code>source host/env.sh &amp;&amp; cd UniXNU-orangepi5 &amp;&amp; scripts/build-orangepi5-kernel.sh</code>. Revision: `f4bb6e952e915f4f837547f11981ca26b61a5c46`.

## Diagnostics {#diagnostics}

`planned`

### Hardware and dependencies

- UART2 on the 3-pin debug header at 1.5 Mbaud 8N1; the firmware prints its own log on the same port.

### Configuration

- serial=3 and debug=0x10014e keep the kernel console on UART2 and restart after a panic.

### Procedure

- Attach a 3.3 V USB serial adapter to the debug header and capture from power-on.

### Development findings

- The serial adapter is not attached to any machine yet; the first observation of this port is still to come.
- uefi-orangepi5 tools/board/capture.sh records the port with times \(serial-capture.py of the SoC repository\); docs/first-boot.md of that repository lists the log lines that settle each step \(firmware, PCIe, NVMe, GPT, root, Data, userland\) and what each failure means.
- The driver prints the PCIe link state, the capability list, the controller registers as the firmware left them and the NVMe identify data, so the first log should show which of the derived hardware assumptions is wrong.

### Completion criteria

- A boot log from the board is stored with the evidence.

### Current limits

- No board access so far.

### Next action

- Capture the first UEFI and kernel log \(runs/m0.ts\) and compare it with the table of first-boot.md.

### Evidence

- `source`: [Repository overview and status](https://github.com/Ken-u/UniXNU-orangepi5/blob/d3968fa094623272ea46ebd2e142c6d6eb69da1f/README.md)

</div>
