# OPPO Reno Ace \(PCLM10 / Project 19081, Snapdragon 855+ SM8150-AC\)

[shmilylee409-a11y/UniXNU-pclm10](https://github.com/shmilylee409-a11y/UniXNU-pclm10)

<div v-pre>

Format 2 UniXNU port for OPPO Reno Ace \(PCLM10, OPPO project 19081, Snapdragon 855 Plus / SM8150-AC\) with verified SM8150 memory map, Samsung SOFEF03F-M 1080x2400@90Hz GOP framebuffer, Synaptics S3706 touch on QUPv3 SE17 I2C, UFS 3.0, and Adreno 640 v2.

Source record: [porting.toml](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/4e9214d6571c670d73e73478fbfb4cf58624d0e8/porting.toml), `4e9214d6571c670d73e73478fbfb4cf58624d0e8`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `implemented` |
| [Firmware and boot](#firmware) | `device-verified` |
| [CPU and interrupts](#cpu) | `device-verified` |
| [Memory and DMA](#memory) | `device-verified` |
| [Storage and root](#storage) | `device-verified` |
| [Display](#display) | `device-verified` |
| [Input](#input) | `device-verified` |
| [GPU](#gpu) | `planned` |
| [Network](#network) | `device-verified` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `device-verified` |
| [Image assembly](#packaging) | `device-verified` |
| [Diagnostics](#diagnostics) | `device-verified` |

## Configuration {#configuration}

`implemented`

Components: `ArmDTPlatform`.

### Hardware and dependencies

- OPPO Reno Ace retail model PCLM10 \(OP4A89, OPPO project 19081, oppo,dtsi\_no = &lt;19081&gt;\) on Qualcomm Snapdragon 855 Plus \(SM8150-AC, msm-id = &lt;0x153 0x20000&gt;, board-id = &lt;8 0&gt;\).
- UniXNU-sm8150-common shared SoC repository pinned at commit f363dcda920101a99e440ce3e8b68849122a3c0a.
- Upstream Android kernel DTS reference guh0613/android\_kernel\_oppo\_sm8150 \(arch/arm64/boot/dts/19081/\) and UEFI reference Project-Aloha/mu\_aloha\_platforms \(Platforms/SurfaceDuo1Pkg/Device/oppo-pclm10/\).

### Configuration

- board.toml selects schema\_version = 2, board.name = 'pclm10', board.soc = 'SM8150', board.soc\_source = 'sm8150', and board.os\_profile = 'ipados-17.7.11-21H461'.
- configs/pclm10\_defconfig sets CONFIG\_BOARD\_PCLM10=y and CONFIG\_SOC\_SM8150=y on top of arch:configs/common.config, soc:configs/sm8150.config, and os:configs/ipados.config.
- Patch series order is arch:patches/xnu/series, soc:patches/xnu/series, os:patches/xnu/series, device:patches/xnu/series.

### Procedure

- Run ./unixnu defconfig pclm10\_defconfig -D ../UniXNU-pclm10 from the UniXNU checkout.
- Verify resolution and status via ./unixnu status --json -D ../UniXNU-pclm10 and python3 scripts/porting-record.py check --device ../UniXNU-pclm10.

### Development findings

- Retail model PCLM10 corresponds to OPPO project 19081 \(SM8150-AC\); early community posts occasionally confused PCKM00 \(OPPO Reno2 SM7150\) with Reno Ace.
- All selected components in board.toml resolve against canonical IDs in UniXNU/components.toml \(ArmDTPlatform, ArmCpu, SoftwareAES, DarwinBoot, XnuPrelink, GopFramebuffer, RamBlock, VirtioMmioBlock, ShengUfs, VerifiedRoot, AppleKeyStoreState\).

### Completion criteria

- All source pins resolve; every selected component has a record; status shows the intended overrides and patch order.

### Current limits

- Board-specific XNU patches remain empty until first hardware boot log triage.

### Next action

- Build the prelinked kernel and UEFI boot image via GitHub Actions macOS runner or local Xcode toolchain.

### Evidence

- `source`: [Format 2 board manifest configures pclm10, SM8150 SoC source, ipados-17.7.11-21H461 profile, and 11 canonical components.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/4e9214d6571c670d73e73478fbfb4cf58624d0e8/board.toml)
- `source`: [Pins UniXNU-sm8150-common at commit f363dcda920101a99e440ce3e8b68849122a3c0a.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/4e9214d6571c670d73e73478fbfb4cf58624d0e8/feeds.toml)
- `source`: [Defines CONFIG\_BOARD\_PCLM10=y and CONFIG\_SOC\_SM8150=y.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/4e9214d6571c670d73e73478fbfb4cf58624d0e8/configs/pclm10_defconfig)

## Firmware and boot {#firmware}

`device-verified`

Components: `DarwinBoot`.

### Hardware and dependencies

- Project-Aloha / Silicium EDK2 UEFI firmware for oppo-pclm10 \(Platforms/SurfaceDuo1Pkg/Device/oppo-pclm10\) and UniXNU/uefi-sheng.
- Extracted single DTB dts/oppo-pclm10-19081.dtb \(486447 bytes, oppo,prjversion = &lt;1 19081&gt;\) containing /reserved-memory/cont\_splash\_region at 0x9d000000 \(size 0x02400000\).
- UEFI FD loaded at 0x9fc00000 \(size 0x00300000\), FV region at 0x9f800000 \(size 0x00400000\), SEC heap/page tables/stack at 0x9ff00000..0xa0000000, DXE heap at 0xa5800000 \(size 0x1a800000\).

### Configuration

- board.toml \[firmware\] selects config = 'pclm10', dsc = 'Platforms/OPPO/pclm10Pkg/pclm10.dsc', preflight = \['scripts/prepare-pclm10-uefi.py'\], and \[bootimg\] dtb = 'build/pclm10/pclm10.dtb'.
- scripts/prepare-pclm10-uefi.py injects Resources/Configs/pclm10.toml and Platforms/OPPO/pclm10Pkg/ into the UniXNU/uefi-sheng checkout and stages dts/oppo-pclm10-19081.dtb to build/pclm10/pclm10.dtb.
- patches/darwinboot-32mb.patch aligns DarwinBoot payload/XNU handoff to SIZE\_32MB on 896 MiB UEFI memory window while preserving cont\_splash at 0x9d000000.

### Procedure

- Run scripts/prepare-pclm10-uefi.py --uefi ../uefi-pclm10 --device . --tree ../UniXNU, then build UEFI firmware with DarwinBoot integrated and pack into Android boot.img via scripts/build-sweet-boot.py.

### Development findings

- dts/oppo-pclm10-19081.dtb already defines /reserved-memory/cont\_splash\_region \(0x9d000000, 0x02400000\), qseecom\_region \(0xa0000000, 0x01400000\), and cdsp\_sec\_regions \(0xa4c00000, 0x00c00000\), so placing DXE Heap at 0xa5800000 \(424 MiB\) avoids all Bank 0 carveouts.
- Device-verified SIZE\_32MB UEFI + DarwinBoot handoff on OPPO Reno Ace \(serial 34d5cb55\) into xnu-8796 \(iOS 16.7.16 20H392\) via fastboot flash boot + fastboot reboot, leaving Android OS partitions intact.

### Completion criteria

- Firmware image builds, enters UniXNU via DarwinBoot, publishes the 1080x2400 framebuffer, and preserves documented memory reservations.

### Current limits

- UEFI identity map remains capped below 4 GiB; multi-GB DRAM expansion is handled inside XNU arm\_init via pclm10-ram-mb.

### Next action

- Keep Android dual-boot layout intact while keeping uefi-32m-896m/boot-uefi-32m.img aligned with sweet-16k.yml.

### Evidence

- `source`: [Firmware build recipe, preflight script, and bootimg DTB path configured.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/4e9214d6571c670d73e73478fbfb4cf58624d0e8/board.toml)
- `source`: [Generates Resources/Configs/pclm10.toml and Platforms/OPPO/pclm10Pkg/ and stages build/pclm10/pclm10.dtb.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/4e9214d6571c670d73e73478fbfb4cf58624d0e8/scripts/prepare-pclm10-uefi.py)
- `device`: [Booted SIZE\_32MB UEFI + DarwinBoot + xnu-8796 on PCLM10 \(34d5cb55\) to SpringBoard Lock Screen and returned cleanly to fastboot.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/4e9214d6571c670d73e73478fbfb4cf58624d0e8/scripts/build-sweet-boot.py)
  Command: <code>python3 scripts/build-sweet-boot.py --uefi-bootimg sweet_work/uefi-32m-896m/boot-uefi-32m.img --kernel sweet_work/ci_xnu_43038210536/kernel.development.sweet --owned-memory-size 0x30000000 --out-dir sweet_work/out_ios_20H392_m4_shot</code>. Revision: `f437b9a8a811c9b3edf99f097e34e1ef4e76b9e6`.

## CPU and interrupts {#cpu}

`device-verified`

Components: `ArmCpu`.

### Hardware and dependencies

- 8x Kryo 485 cores \(MPIDR 0x000..0x700\): 4x Cortex-A55 Silver \(0x000..0x300 @ 1.80 GHz\), 3x Cortex-A76 Gold \(0x400..0x600 @ 2.42 GHz\), 1x Cortex-A76 Prime \(0x700 @ 2.96 GHz\).
- PSCI 1.0 over SMC; GICv3 distributor at 0x17a00000 \(size 0x10000\), redistributors at 0x17a60000 \(size 0x100000, stride 0x20000\); 19.2 MHz architected counter with virtual timer INTID 19.

### Configuration

- Inherited from UniXNU-sm8150-common dts/sm8150.dtsi via dts/pclm10.dts.
- board.toml sets cpu\_regs = '0,0x100,0x200,0x300,0x400,0x500,0x600,0x700', psci\_method = 'smc', and kernel\_args = \['-v', 'serial=3', 'cpus=8', 'armcpu-self-ipi=1'\].

### Procedure

- Boot XNU with cpus=8 and verify all 8 Kryo 485 cores come online via PSCI CPU\_ON with working GICv3 SGI1 IPIs and virtual timer interrupts \(INTID 19\).

### Development findings

- Device-verified 8/8 Kryo 485 SMP initialization \(cpu 0..7, MPIDR 0x0..0x700\) on PCLM10: PSCI CPU\_ON rc=0 on all secondary cores and SWEET CPU: 8/8 CPUs initialized, SGI1 verified.

### Completion criteria

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU.

### Current limits

- EPSS dynamic frequency scaling for the 2.96 GHz Prime core is not yet implemented.

### Next action

- Add optional EPSS OPP frequency scaling once Adreno GPU bring-up starts.

### Evidence

- `source`: [Declares 8 CPU MPIDR affinities, PSCI smc method, and armcpu-self-ipi=1 boot argument.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/4e9214d6571c670d73e73478fbfb4cf58624d0e8/board.toml)
- `device`: [Logged SWEET GIC: virtual timer INTID 19, PSCI CPU\_ON rc=0 for cpu 1..7, and SWEET CPU: 8/8 CPUs initialized, SGI1 verified on 34d5cb55.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/4e9214d6571c670d73e73478fbfb4cf58624d0e8/scripts/apply-pclm10-sweet-overlay.py)
  Command: <code>python3 sweet_work/auto_qud_shot.py --serial 34d5cb55 --qud-serial QcomXnuUsbDebug --boot-img sweet_work/out_ios_20H392_m4_shot/boot-sweet.img --capture-dir sweet_work/usb_captures/ios_20H392_m4_shot</code>. Revision: `f437b9a8a811c9b3edf99f097e34e1ef4e76b9e6`.

## Memory and DMA {#memory}

`device-verified`

### Hardware and dependencies

- 8 GB / 12 GB LPDDR4X @ 2133 MHz across Bank 0 \(0x80000000..0xbbb00000\), Carveout Hole \(0xbbb00000..0xc0000000\), Bank 1 \(0xc0000000, size 0x80000000\), and Bank 2 \(0x140000000+\).
- OPPO project 19081 reserved-memory layout: hyp\_mem \(0x85700000, 0x600000\), xbl\_aop\_mem + cmd\_db \(0x85d00000..0x85f40000\), gpu\_prr \(0x85f40000, 0x10000\), smem \(0x86000000, 0x200000\), qtee \(0x86200000, 0x1800000\), expanded tzapps\_mem \(0x87a00000, 0x5d00000\), pil\_mem \(0x8d700000, 0xf400000\), cont\_splash\_region \(0x9d000000, 0x2400000\), fv\_region \(0x9f800000, 0x400000\), uefi\_fd \(0x9fc00000, 0x300000\), pstore \(0x17fe00000, 0x200000\).
- Apps SMMU-500 at 0x15000000 \(UFS stream 0x300, USB stream 0x140\) and GPU SMMU-500 at 0x02ca0000.

### Configuration

- dts/pclm10.dts sets memory@c0000000 reg = &lt;0x0 0xc0000000 0x0 0x80000000&gt; and records all 11 no-map reserved-memory regions plus ramoops pstore.
- scripts/apply-pclm10-sweet-overlay.py adds pclm10-ram-mb=&lt;512..2816&gt; expansion in osfmk/arm/arm\_init.c \(0xC4800000..0x174800000 across DDR Bank 1+2 below PANIC\_LOG\_BASE 0x17E000000 and PStore 0x17FE00000\).

### Procedure

- Boot with --owned-memory-size 0x30000000 and pclm10-ram-mb=2816; verify vm\_page\_bootstrap page count, absence of VM swap failures, and SMMU stream 0x300/0x140 DMA.

### Development findings

- Device-verified 2816 MiB \(2.75 GiB\) DRAM via pclm10-ram-mb=2816 with 16 KiB pages: vm\_page\_bootstrap reported 176859 free pages + 3365 wired pages \(180224 total 16K pages = 2816 MiB\) and eliminated earlier VM swap file failures.
- Apps SMMU-500 stream bypass verified on hardware for UFS \(stream 0x300\) and USB DWC3 \(stream 0x140\) above 4 GiB.

### Completion criteria

- All handoff regions are accounted for and each enabled DMA engine accesses its allocated range with the documented cache policy.

### Current limits

- DRAM window is capped at 2816 MiB \(0xC4800000..0x174800000\) to avoid DDR Bank 2 PANIC\_LOG\_BASE \(0x17E000000\) and PStore \(0x17FE00000\).

### Next action

- Validate GPU SMMU \(0x02ca0000\) mappings when Adreno 640 driver work begins.

### Evidence

- `source`: [Defines memory@c0000000 and all OPPO project 19081 reserved-memory carveouts.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/4e9214d6571c670d73e73478fbfb4cf58624d0e8/dts/pclm10.dts)
- `device`: [Verified vm\_page\_bootstrap: 176859 free pages, 3365 wired pages \(2816 MiB at 16K\) and Apps SMMU stream 0x300/0x140 DMA on 34d5cb55.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/4e9214d6571c670d73e73478fbfb4cf58624d0e8/scripts/apply-pclm10-sweet-overlay.py)
  Command: <code>python3 sweet_work/auto_qud_shot.py --serial 34d5cb55 --qud-serial QcomXnuUsbDebug --boot-img sweet_work/out_ios_20H392_m4_shot/boot-sweet.img --capture-dir sweet_work/usb_captures/ios_20H392_m4_shot</code>. Revision: `f437b9a8a811c9b3edf99f097e34e1ef4e76b9e6`.

## Storage and root {#storage}

`device-verified`

Components: `SoftwareAES`.

### Hardware and dependencies

- Samsung UFS 3.0 storage \(128 GB / 256 GB\) on Qualcomm ufshc@1d84000 \(MMIO 0x01d84000, size 0x2500\), QMP v4 PHY at 0x01d87000, ICE at 0x01d90000, GCC UFS clock window at 0x00177000 \(size 0x1000\).
- Apps SMMU at 0x15000000 with stream ID 0x300 and 4096-byte logical block size; dual-boot LUN 0 GPT partition 'ios' \(20480 MiB at first block 0x359cf00\).

### Configuration

- dts/pclm10.dts enables &amp;ufs and &amp;ufs\_smmu from sm8150.dtsi.
- scripts/mkiosroot-mac.sh + scripts/sweet/sweet-root-tweaks.py stage iOS 16.7.16 \(20H392\) HFS+ rootfs into the dual-boot 'ios' LUN 0 partition.

### Procedure

- Boot with rd=ufsroot0 ufsroot=ios ufsrw=1 rootrw=1 ufscache=1 and verify LUN0 4K block reads/writes, HFS+ root mount, launchd, and tail-partition console log flushing.

### Development findings

- Device-verified sweet\_ufs read-write mount of the 20480 MiB 'ios' LUN 0 partition \(block 0x359cf00, DMA 0xcb518000\) booting iOS 16.7.16 \(20H392\) into SpringBoard while preserving all Android OS partitions.

### Completion criteria

- Host: register, clock, link and SMMU facts match the board inventory.
- Reads: SCSI capacity, GPT and known blocks are correct; OS/SystemOS windows stay within userdata.
- Root: the configured volume mounts and launchd starts. Persistence: writes survive reboot within the allocated Data region.

### Current limits

- Uses HFS+ iOS 16.7.16 rootfs partition alongside Android LUN 0 partitions rather than APFS sealed volume.

### Next action

- Preserve the dual-boot 'ios' LUN 0 GPT layout across future kernel updates.

### Evidence

- `source`: [Enables &amp;ufs \(0x01d84000\) and &amp;ufs\_smmu \(0x15000000, stream 0x300\).](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/4e9214d6571c670d73e73478fbfb4cf58624d0e8/dts/pclm10.dts)
- `device`: [Mounted 'ios' on LUN 0 \(20480 MiB, block 0x359cf00\) read-write and booted iOS 16.7.16 \(20H392\) to SpringBoard on 34d5cb55.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/4e9214d6571c670d73e73478fbfb4cf58624d0e8/scripts/mkiosroot-mac.sh)
  Command: <code>python3 sweet_work/auto_qud_shot.py --serial 34d5cb55 --qud-serial QcomXnuUsbDebug --boot-img sweet_work/out_ios_20H392_m4_shot/boot-sweet.img --capture-dir sweet_work/usb_captures/ios_20H392_m4_shot</code>. Revision: `f437b9a8a811c9b3edf99f097e34e1ef4e76b9e6`.

## Display {#display}

`device-verified`

Components: `GopFramebuffer`.

### Hardware and dependencies

- Samsung SOFEF03F-M 6.5-inch FHD+ \(1080x2400 @ 90Hz\) single-DSI command-mode AMOLED panel with DSC \(dsi\_samsung\_sofef03f\_m\_amoled\_fhd\_plus\_90fps\_cmd\).
- Panel TLMM GPIOs: TE = GPIO 8, Reset = GPIO 6, Mode/VDDD\(1.1V\) = GPIO 152, VCI\(3.0V\) = GPIO 25, ErrFlag = GPIO 49; DCS backlight range 6..2047.
- UEFI GOP continuous splash linear framebuffer at 0x9d000000 \(size 0x02400000, 1080x2400, 32bpp BGRA8888, stride 4320\).

### Configuration

- SweetFramebuffer publishes AppleCLCD 1080x2400 stride 4320 at 0x9d000000 \(presented as 1125x2436 BGRA8888\) and registers qcom\_usb\_debug\_register\_framebuffer\(&amp;qud\_fb\) for live USB PNG capture.
- AppleCLCD::present\(\) bilinearly downscales the logical 1125x2436 frame to 1080x2400 via a cached horizontal LUT and L1 rowbuf\[2048\] + memcpy Write-Combine bursts \(preventing WC bus stalls and 22/23px edge clipping, with sweetfb\_crop=1 opt-in\), composites multi-layer SrcOver alpha, clears uncovered background, and drains stores with dsb sy.
- AppleARMBacklight \(sweetbacklight=1, sweetbl\_dcs=1\) verifies DISP\_CC \(0x0af00000\) + DSI0 \(0x0ae94000\) active state, publishes CoreBrightness IODisplayParameters/calibration properties, and writes 10-bit MIPI DCS 0x51 brightness packets via DSI0 TPG FIFO.
- SweetFramebuffer RequestPowerChange \(selector 12\) handles display on/off transitions from backboardd.

### Procedure

- Boot XNU with sweetfb\_noconsole=1 sweetfb\_hz=15 sweetbacklight=1 sweetbl\_dcs=1 qcom-usb-debug=1 qcom-usb-ctl=1, capture CRC-verified PNG frames via scripts/screenshot-xnu-usb.py, and sweep Control Center brightness slider via pclm10-autoswipe=100.

### Development findings

- Replaced upstream 1125x2436-&gt;1080x2400 center-crop \(top=33, bot=12, dock\_L=8, dock\_R=7\) and direct volatile WC writes with L1-buffered bilinear scaling + memcpy bursts, eliminating edge clipping \(top=50, bot=23..29, dock\_L=28, dock\_R=28\) and sustained-animation WC disconnects.
- Device-verified 1080x2400 iOS 16.7.16 UI across Lock Screen, Home Screen, Settings \(initial and scrolled\), App Library, and Control Center via CRC32-verified live USB screenshot capture.
- iOS 16.7.16 CoreBrightness \_DisplayCreateWithID requires AppleARMBacklight class conformance plus all 9 backlight-calibration-parameters keys \(including current-for-max/mid-backlight and hardware-max-current-limit\) before starting libEDR and delivering brightness-nits updates.
- Device-verified Control Center slider ramp \(20 steps lvl=537..984, dcs\_ok=1\) and display-on brightness restoration \(lvl=984, dcs\_ok=1\) over DSI0 TPG FIFO MIPI DCS 0x51 on 34d5cb55.

### Completion criteria

- A known frame appears with correct geometry and colors, then userland presentation and display power controls work.

### Current limits

- Native DPU TE \(GPIO 8\) refresh modulation is not wired yet; display off fades AMOLED pixels to black and RequestPowerChange runs at software vsync.

### Next action

- Optional: wire native MDSS TE IRQ \(GPIO 8\) and RequestPowerChange DCS 0x28/0x29 power gating if hardware DPU composition is enabled later.

### Evidence

- `source`: [Documents framebuffer0@9d000000 \(1080x2400, stride 4320\) and cont\_splash\_region@9d000000.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/4e9214d6571c670d73e73478fbfb4cf58624d0e8/dts/pclm10.dts)
- `device`: [Captured CRC32-verified 1080x2400 PNGs across Lock Screen \(e32d2895\), Home Screen \(3fad9be9\), Settings \(c5378c71\), scrolled Settings \(8eeca332\), and App Library \(732b19ef\) with unclipped margins on 34d5cb55.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/4e9214d6571c670d73e73478fbfb4cf58624d0e8/scripts/screenshot-xnu-usb.py)
  Command: <code>python3 sweet_work/auto_qud_multishot.py --boot-img sweet_work/out_ios_20H392_rowbuf/boot-sweet.img --capture-dir sweet_work/usb_captures/ios_20H392_rowbuf --capture-seconds 280</code>. Revision: `094c73534157a8e09bd111ffbbd91250cd5ad114`.
- `device`: [Verified AppleARMBacklight CoreBrightness ramp \(lvl=537..984, 20 steps dcs\_ok=1\) across Control Center slider drag and wake restore \(lvl=984 dcs\_ok=1\) on 34d5cb55 \(ios\_20H392\_bl\_v4 &amp; ios\_20H392\_final\_v3\).](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/4e9214d6571c670d73e73478fbfb4cf58624d0e8/scripts/apply-pclm10-sweet-overlay.py)
  Command: <code>python3 sweet_work/auto_qud_multishot.py --boot-img sweet_work/out_ios_20H392_bl_v4/boot-sweet.img --capture-dir sweet_work/usb_captures/ios_20H392_bl_v4 --capture-seconds 370</code>. Revision: `1088bedc09493f4d8627a57e393b0a66f24e6372`.

## Input {#input}

`device-verified`

### Hardware and dependencies

- Primary touchscreen: Synaptics S3706A \(I2C slave 0x20\) on qupv3\_se17\_i2c \(MMIO 0x00c80000, qupv3\_2 wrapper 0x00c00000, TLMM SOUTH SDA GPIO 55, SCL GPIO 56, reset GPIO 54, IRQ GPIO 122\).
- Power &amp; pull-up: vdd\_2v8 = &lt;&amp;pm8150\_l17&gt; \(RPMh ldoa17 3.0V\), enable1v8\_gpio = &lt;&amp;pm8150l\_gpios 5&gt; \(SPMI PPID 0x4c4, APID 318\); 1080x2400 coords, up to 10 contacts.
- Physical buttons: Volume Up \(&amp;pm8150\_gpios 6\), Volume Down \(&amp;pm8150\_gpios 7\), Power key via PM8150 PON \(SPMI APIDs 247 / 260\).

### Configuration

- scripts/apply-pclm10-sweet-overlay.py configures sweet\_touch.c for SM8150 TLMM SOUTH GPIO 55/56 software I2C bitbang fallback when SE17 GENI\_IF\_DISABLE\_RO \(0x64=0x1\) indicates TZ-locked GPI mode.
- RMI4 S3706A F12\_DATA\_BASE \(d1\_off=0\) + DATA15 obj\_attention + F01 wake/IRQ init publish multi-touch events via SweetHIDTouch \(aligned 1:1 to 1080x2400 scaled display with fOffX=0, fOffY=0\); sweet\_keys.c publishes PON/GPIO buttons via SweetHIDButtons.

### Procedure

- Boot with sweettouch=1 sweettouchdelay=3 sweetkeys=1 and verify S3706A probe \(0x20\), SpringBoard swipe/tap coordinates, and physical key HID delivery.

### Development findings

- TrustZone locks QUPv3 SE17 to GPI DMA mode \(GENI\_IF\_DISABLE\_RO 0x64=0x1\) and GCC wrap2 s\_ahb\_clk \(0x1e008\) is HWCG-gated; software I2C bitbang on TLMM SOUTH GPIO 55/56 after PM8150L GPIO5 high enables reliable 10ms multi-touch polling.
- OPPO S3706A F12 stores finger slots directly at F12\_2D\_DATA\_BASE \(d1\_off=0\) and obj\_attention at f12\_d+3, verified with real finger swipes and 1:1 scaled UI unlock/Settings/App Library navigation on hardware.

### Completion criteria

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive, and buttons produce expected HID reports.

### Current limits

- Touch runs in 10ms polled bitbang mode rather than interrupt-driven TLMM IRQ 122.

### Next action

- Optional: wire TLMM GPIO 122 interrupt trigger to reduce idle I2C polling.

### Evidence

- `source`: [Documents qupv3\_se17\_i2c \(0x00c80000\) and touchscreen@20 \(synaptics,s3706\).](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/4e9214d6571c670d73e73478fbfb4cf58624d0e8/dts/pclm10.dts)
- `device`: [Verified S3706A probe \(pid=S3706A f01=0x6 f12=0x8 d1\_off=0 n=10\), 1:1 scaled UI touch navigation \(Lock-&gt;Home-&gt;Settings-&gt;Scroll-&gt;App Library\), and PM8150 keys on 34d5cb55.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/4e9214d6571c670d73e73478fbfb4cf58624d0e8/scripts/apply-pclm10-sweet-overlay.py)
  Command: <code>python3 sweet_work/auto_qud_multishot.py --boot-img sweet_work/out_ios_20H392_rowbuf/boot-sweet.img --capture-dir sweet_work/usb_captures/ios_20H392_rowbuf --capture-seconds 280</code>. Revision: `094c73534157a8e09bd111ffbbd91250cd5ad114`.

## GPU {#gpu}

`planned`

### Hardware and dependencies

- Qualcomm Adreno 640 v2 \(SM8150-AC bin, up to 675 MHz, chip-id 0x06040001, 1 MiB GMEM\).
- MMIO windows: kgsl\_3d0 0x02c00000 \(0x40000\), GMU 0x02c6a000 \(0x30000\), RSCC 0x02c8d000 \(0x2000\), PDC 0x0b290000 / 0x0b490000, GPU SMMU-500 0x02ca0000, GPUCC 0x02c90000 \(0x9000\), GCC 0x00100000 \(0x1f0000\).
- Reserved regions: AOP CMD DB 0x85f20000 \(0x20000\), GPU PRR 0x85f40000 \(0x10000\), PIL GPU ZAP shader region 0x99515000 \(0x2000\).

### Configuration

- soc:configs/sm8150.config enables CONFIG\_XNU\_NATIVE\_ADRENO=y.
- dts/pclm10.dts enables &amp;gpu, &amp;gmu, &amp;gpu\_smmu, &amp;gpucc, and &amp;gcc from sm8150.dtsi.
- proprietary-files.txt lists a640\_sqe.fw, a640\_gmu.bin, and a640\_zap.&\#123;mdt,b00,b01,b02,elf&\#125;.

### Procedure

- Stage Adreno 640 vendor firmware from PCLM10 /vendor/firmware, note the 0x99515000 ZAP PIL address on project 19081, and test GMU/CP ring initialization.

### Development findings

- Because OPPO project 19081 shifts pil\_region to 0x8d700000, the GPU ZAP PIL sub-region sits at 0x99515000 \(size 0x2000\) rather than nabu's 0x98f15000.

### Completion criteria

- GPU submissions complete, mapping/fence handling is correct, a known image renders, and the selected Metal client presents it.

### Current limits

- Adreno 640 ZAP shader physical address offset \(0x99515000\) must be passed to the GPU bring-up driver.

### Next action

- Extract a640\_\* firmware blobs from PCLM10 vendor image and test Adreno 640 initialization after CPU/storage boot.

### Evidence

- `source`: [Enables &amp;gpu, &amp;gmu, &amp;gpu\_smmu, &amp;gpucc, &amp;gcc and documents the 0x99515000 GPU ZAP PIL offset.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/4e9214d6571c670d73e73478fbfb4cf58624d0e8/dts/pclm10.dts)
- `source`: [Records Adreno 640 SQE, GMU, and ZAP firmware paths.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/4e9214d6571c670d73e73478fbfb4cf58624d0e8/proprietary-files.txt)

## Network {#network}

`device-verified`

### Hardware and dependencies

- Qualcomm WCN3990 integrated 802.11a/b/g/n/ac 2x2 MU-MIMO Wi-Fi &amp; Bluetooth 5.0 \(BT UART on qupv3\_se14\_4uart @ 0x00a98000, WLAN FW PIL at 0x9b000000 size 0x00180000\).
- Synopsys DWC3 USB 3.1 Controller at 0x0a600000 behind QSCRATCH 0x0a6f8800 and SNPS Femto HS PHY @ 0x088e2000 \(SMMU stream 0x140\).

### Configuration

- pil\_mem in dts/pclm10.dts preserves the WLAN firmware carveout at 0x9b000000 \(0x00180000\).
- scripts/apply-pclm10-sweet-overlay.py adapts sweet\_usb.c GCC clocks \(0x0f010/0x0f014/0x0f018/0x0f050/0x0f054\), QSCRATCH UTMI-PIPE routing, PHY restore across CSFTRST, and SMMU stream 0x140 bypass for USB CDC-ECM \(sweetusb=2\).

### Procedure

- Boot with sweetusb=2 usbstream=0x140 qcom-usb-debug=0; verify Sweet iOS \(USB Ethernet\) VID 0x1209 PID 0x0001 enumeration on macOS and UDP port 5141 RX into pclm10\_watchdog\_thread.

### Development findings

- Device-verified USB CDC-ECM networking on PCLM10: macOS enumerated Sweet iOS \(USB Ethernet\) on en2 \(status: active, 02:00:5e:77:ee:01\) and XNU received broadcast UDP port 5141 REBOOT triggering fastboot return in 7s.
- WCN3990 uses SNOC/QMI rather than PCIe MHI and remains deferred.

### Completion criteria

- Scanning, association, address configuration and sustained receive/transmit traffic pass with the selected firmware.

### Current limits

- USB CDC-ECM shares the single DWC3 controller with QcomXnuUsbDebug \(mutually exclusive per boot\); WCN3990 Wi-Fi is not yet enabled.

### Next action

- Assign 192.168.7.1/24 on host en2 when using sweetusb=2 for interactive TCP/UDP traffic or nc -ukl 5140 live logs.

### Evidence

- `device`: [Enumerated Sweet iOS \(USB Ethernet\) VID 0x1209/PID 0x0001 \(en2 active\) and delivered UDP 5141 REBOOT to XNU on 34d5cb55.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/4e9214d6571c670d73e73478fbfb4cf58624d0e8/scripts/apply-pclm10-sweet-overlay.py)
  Command: <code>fastboot -s 34d5cb55 flash boot sweet_work/out_ios_20H392_ecm/boot-sweet.img &amp;&amp; fastboot -s 34d5cb55 reboot</code>. Revision: `76421c000a3de564d0dbdd48dc0d25424537e86a`.

## Audio {#audio}

`planned`

### Hardware and dependencies

- Qualcomm WCD934x \(Tavil\) audio codec over SLIMbus, dual stereo speakers \(Dolby Atmos\), 3.5mm headset jack, and ADSP PIL region at 0x9b200000 \(size 0x01e00000\).

### Configuration

- dts/pclm10.dts preserves smem\_mem \(0x86000000\) and adsp\_region inside pil\_mem \(0x9b200000, 0x01e00000\).

### Procedure

- Defer audio subsystem bring-up until interactive UI and touch input are verified.

### Development findings

- ADSP firmware carveout is located at 0x9b200000 \(30 MiB\) in android-pclm10.dtb.

### Completion criteria

- Each declared route carries the selected audio format through playback or capture and handles start/stop correctly.

### Current limits

- ADSP GLINK/APR and WCD934x codec drivers are not implemented.

### Next action

- Defer until after display, storage, and touch bring-up.

### Evidence

Collect evidence using the next action.

## Power {#power}

`device-verified`

### Hardware and dependencies

- PM8150 \(SID 0\), PM8150B \(SID 2 SMB5 @ 0x1000..0x1300\), and PM8150L \(SID 4\) PMICs over SPMI \(0x0c440000 / 0x0e600000 / 0x0c40a000\); RPMh RSC at 0x18220000 and AOP CMD DB at 0x85f20000.
- Dual-cell \(2S\) 4000 mAh battery with TI BQ27541 fuel gauge \(oplus,bq27541-battery @ 0x55\) on qupv3\_se15\_i2c \(TLMM EAST 0x03500000 GPIO 27 SDA / GPIO 28 SCL, dtbo fragment@65\) and STM8S fast-charge MCU @ 0x26.
- Awinic AW8697 LRA haptic actuator \(awinic,aw8697\_haptic @ 0x5a\) on qupv3\_se7\_i2c \(TLMM SOUTH GPIO 98/99, dtbo fragment@51\).

### Configuration

- scripts/apply-pclm10-sweet-overlay.py enables SPMI SID 2 reads in bsd/dev/sweet\_spmi.c and reads BQ27541 via TLMM EAST GPIO 27/28 bitbang + PM8150B SMB5 \(0x1310, 0x110b, 0x1006, 0x1007, 0x100d\) in SweetBattery.cpp.
- sweet\_rpmh.c votes L11C \(ldoa17 3000 mV\) via RPMh TCS0 ACTIVE for touch power.

### Procedure

- Boot with sweetbattery=1 and verify BQ27541 voltage/SOC/current, PM8150B SMB5 USB/charging state, RPMh ldoa17 TCS0 completion, and SpringBoard status-bar charging icon.

### Development findings

- dtbo.img fragment@65 confirmed BQ27541 @ 0x55 is wired to qupv3\_se15\_i2c \(TLMM EAST 0x03500000 GPIO 27/28\), not qupv3\_se1\_i2c \(GPIO 114/115\).
- Device-verified dual-cell BQ27541 readout \(raw 8633 mV -&gt; 4316 mV/cell, SOC 100%, 0 mA\) and PM8150B SID 2 SMB5 telemetry \(usb=0x10, path=0x95, chg=0x47\), reflected by the live Lock Screen charging indicator.
- Device-verified BQ27541 bq\_recover\(\) 9-clock SCL recovery yielding mv\_ok=1\(8623\) soc\_ok=1\(100\) on poll 0 and AW8697 LRA haptic probe \(err=0 id=0x97\) + BY\_DRV\_TIME boot tap \(glb=0-&gt;0\) on 34d5cb55.

### Completion criteria

- Declared power controls and battery readings match observations; RPMh rail voting completes cleanly.

### Current limits

- Sleep/resume S2R and 65W SuperVOOC protocol negotiation with STM8S \(0x26\) remain unimplemented; I2C bitbang uses polled GPIO 27/28.

### Next action

- Optional: expose AW8697 IOKit haptic trigger service once CoreBrightness display backlight verification completes.

### Evidence

- `source`: [Reserves AOP Command DB at 0x85f20000 and RPMh RSC at 0x18220000.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/4e9214d6571c670d73e73478fbfb4cf58624d0e8/dts/pclm10.dts)
- `device`: [Verified BQ27541 \(8633 mV -&gt; 4316 mV, 100%, 0 mA\), PM8150B SID 2 SMB5 \(usb=0x10 path=0x95 chg=0x47\), and RPMh L11C vote on 34d5cb55.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/4e9214d6571c670d73e73478fbfb4cf58624d0e8/scripts/apply-pclm10-sweet-overlay.py)
  Command: <code>python3 sweet_work/auto_qud_shot.py --serial 34d5cb55 --qud-serial QcomXnuUsbDebug --boot-img sweet_work/out_ios_20H392_m4_shot/boot-sweet.img --capture-dir sweet_work/usb_captures/ios_20H392_m4_shot</code>. Revision: `f437b9a8a811c9b3edf99f097e34e1ef4e76b9e6`.
- `device`: [Verified BQ27541 bq\_recover\(\) mv\_ok=1\(8623\) soc\_ok=1\(100\) on poll 0 and AW8697 probe \(err=0 id=0x97\) + BY\_DRV\_TIME boot tap \(glb=0-&gt;0\) on 34d5cb55.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/4e9214d6571c670d73e73478fbfb4cf58624d0e8/scripts/apply-pclm10-sweet-overlay.py)
  Command: <code>python3 sweet_work/auto_qud_shot.py --serial 34d5cb55 --qud-serial QcomXnuUsbDebug --boot-img sweet_work/out_ios_20H392_final_v3/boot-sweet.img --capture-dir /tmp/qud_final_v3 --settle-seconds 130 --capture-seconds 160 --no-reboot</code>. Revision: `1088bedc09493f4d8627a57e393b0a66f24e6372`.

## Image assembly {#packaging}

`device-verified`

Components: `XnuPrelink`, `AppleKeyStoreState`.

### Hardware and dependencies

- Android v2 boot.img \(SIZE\_32MB UEFI FD + patched DTB\) + FAT32 payload.img carrying rebased kernel.development.sweet \(xnu-8796 ios-sweet\) and pclm10-sweet.adt.
- PANIC\_LOG\_BASE = 0x17E000000 in scripts/mkadt-sweet-pclm10.py sits in DDR Bank 2 above 2816 MiB RAM \(0x174800000\) and below PStore \(0x17FE00000\).

### Configuration

- .github/workflows/sweet-16k.yml builds kernel.development.sweet on macos-15-intel \(with Xcode 15\) from pinned ios-sweet + scripts/apply-pclm10-sweet-overlay.py + QcomXnuUsbDebug.
- scripts/build-sweet-boot.py builds pclm10-sweet.adt, rebases the Mach-O kernel, packs FAT32 payload.img, and emits boot-sweet.img.

### Procedure

- Build kernel via sweet-16k.yml, assemble boot-sweet.img with scripts/build-sweet-boot.py, and flash to Android boot partition via fastboot flash boot.

### Development findings

- Switching sweet-16k.yml xnu job to macos-15-intel resolves arm64 runner capacity stalls \(\~12-13 min kernel build\).
- Raising PANIC\_LOG\_BASE to 0x17E000000 in scripts/mkadt-sweet-pclm10.py clears DDR Bank 1+2 for 2816 MiB XNU DRAM without overlapping PStore.
- scripts/apply-pclm10-sweet-overlay.py populates all 9 mandatory iOS 16 CoreBrightness calibration keys in AppleARMBacklight and adds Control Center brightness slider autoswipe gestures \(6/7\) for automated backlight verification.

### Completion criteria

- Kernel and boot-sweet.img build cleanly, fit the 100 MiB Android boot partition, and boot on PCLM10 hardware.

### Current limits

- Local Linux/macOS python3.9 lacks stdlib tomllib required by UniXNU/scripts/porting-record.py; CI porting-record.yml runs validation on Ubuntu 26.04 Python 3.12+.

### Next action

- Keep final interactive boot-sweet.img \(CI 43144689220, sha256 06b2daf5927137b231a68293e989ed894ae008bcedcff98be1e576ed40e9e404\) synced with any future GPU/Wi-Fi/audio milestones.

### Evidence

- `source`: [Defines \[package\], \[firmware\], \[bootimg\], \[payload\], and \[payload.adt\] sections.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/4e9214d6571c670d73e73478fbfb4cf58624d0e8/board.toml)
- `device`: [Built 80257024-byte boot-sweet.img from CI run 43038210536 and booted PCLM10 34d5cb55 to SpringBoard Lock Screen.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/4e9214d6571c670d73e73478fbfb4cf58624d0e8/scripts/build-sweet-boot.py)
  Command: <code>python3 scripts/build-sweet-boot.py --uefi-bootimg sweet_work/uefi-32m-896m/boot-uefi-32m.img --kernel sweet_work/ci_xnu_43038210536/kernel.development.sweet --owned-memory-size 0x30000000 --out-dir sweet_work/out_ios_20H392_m4_shot</code>. Revision: `f437b9a8a811c9b3edf99f097e34e1ef4e76b9e6`.
- `device`: [Built final interactive 80257024-byte boot-sweet.img from CI run 43144689220 and verified live interactive Lock Screen \(crc32 b2503975\), AppleARMBacklight \(lvl=984 dcs\_ok=1\), AW8697 boot tap \(glb=0-&gt;0\), and BQ27541 poll 0 \(mv\_ok=1\) on 34d5cb55.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/4e9214d6571c670d73e73478fbfb4cf58624d0e8/scripts/build-sweet-boot.py)
  Command: <code>python3 scripts/build-sweet-boot.py --uefi-bootimg sweet_work/uefi-32m-896m/boot-uefi-32m.img --kernel sweet_work/ci_xnu_43144689220/kernel.development.sweet --owned-memory-size 0x30000000 --out-dir sweet_work/out_ios_20H392_final_v3</code>. Revision: `1088bedc09493f4d8627a57e393b0a66f24e6372`.

## Diagnostics {#diagnostics}

`device-verified`

### Hardware and dependencies

- QcomXnuUsbDebug CDC-ACM USB console \(VID 0x1209 / PID 0x316d, serial QcomXnuUsbDebug\), QcomUsbControl \(2048-byte replies, HELLO/STATUS/REBOOT/SCREENSHOT/SHOTNEXT\), and QcomUsbScreenshot \(768-byte RLE RGB chunks\).
- Pclm10BootReset.c fastboot reboot via IMEM restart\_reason \(0x146bf65c\), PM8150 PON spare, and PS\_HOLD.

### Configuration

- scripts/xnu\_usb\_control.py sets REPLY\_BYTES = 2048 and scripts/screenshot-xnu-usb.py accepts MAX\_CHUNK = 768 matching QcomUsbControl.h / QcomUsbScreenshot.h.
- scripts/apply-pclm10-sweet-overlay.py hooks bsd\_autoconf USB worker, pclm10-autoreset, pclm10-panic-reset, and UDP 5141 watchdog reset.

### Procedure

- Boot with -v -enable\_kprintf\_spam serial=3 qcom-usb-debug=1 qcom-usb-ctl=1; capture logs via collect-xnu-usb.py --control-socket, grab screenshots via scripts/screenshot-xnu-usb.py, and reboot via xnu\_usb\_control.py reboot.

### Development findings

- Upstream QUD bumped QUD\_SCREENSHOT\_CHUNK to 768 and SXNU\_CONTROL\_REPLY\_BYTES to 2048, so host scripts needed REPLY\_BYTES = 2048 and MAX\_CHUNK = 768 to transfer 1626-byte SHOTNEXT frames without timing out.
- QcomXnuUsbDebug kprintf tee relies on -enable\_kprintf\_spam to stay active before bsd\_autoconf; keeping -v -enable\_kprintf\_spam with sweetfb\_noconsole=1 preserves both live USB control and a clean GUI framebuffer.

### Completion criteria

- Each claimed milestone has a reproducible command, a matching source/image revision and an accessible result.

### Current limits

- Using QcomXnuUsbDebug disables sweetusb CDC-ECM for that boot because both share DWC3 at 0x0a600000.

### Next action

- Keep xnu\_usb\_control.py and screenshot-xnu-usb.py synced with QUD upstream chunk sizes.

### Evidence

- `device`: [Delivered 129/129 control frames \(0 timeouts\), verified CRC32 PNG screenshot, and executed CTL REBOOT back to fastboot on 34d5cb55.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/4e9214d6571c670d73e73478fbfb4cf58624d0e8/scripts/xnu_usb_control.py)
  Command: <code>python3 scripts/xnu_usb_control.py --socket sweet_work/usb_captures/ios_20H392_m4_shot/usb-control.sock reboot</code>. Revision: `f437b9a8a811c9b3edf99f097e34e1ef4e76b9e6`.

</div>
