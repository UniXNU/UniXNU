# OPPO Reno Ace \(PCLM10 / Project 19081, Snapdragon 855+ SM8150-AC\)

[shmilylee409-a11y/UniXNU-pclm10](https://github.com/shmilylee409-a11y/UniXNU-pclm10)

<div v-pre>

Format 2 UniXNU port for OPPO Reno Ace \(PCLM10, OPPO project 19081, Snapdragon 855 Plus / SM8150-AC\) with verified SM8150 memory map, Samsung SOFEF03F-M 1080x2400@90Hz GOP framebuffer, Synaptics S3706 touch on QUPv3 SE17 I2C, UFS 3.0, and Adreno 640 v2.

源记录: [porting.toml](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/29e9f7cc47421f0ceb6419ce0031e998642383d3/porting.toml), `29e9f7cc47421f0ceb6419ce0031e998642383d3`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `implemented` |
| [固件与启动](#firmware) | `implemented` |
| [CPU 与中断](#cpu) | `planned` |
| [内存与 DMA](#memory) | `implemented` |
| [存储与根卷](#storage) | `planned` |
| [显示](#display) | `planned` |
| [输入](#input) | `planned` |
| [GPU](#gpu) | `planned` |
| [网络](#network) | `planned` |
| [音频](#audio) | `planned` |
| [电源](#power) | `planned` |
| [镜像组装](#packaging) | `implemented` |
| [诊断](#diagnostics) | `planned` |

## 配置 {#configuration}

`implemented`

组件: `ArmDTPlatform`.

### 硬件与依赖

- OPPO Reno Ace retail model PCLM10 \(OP4A89, OPPO project 19081, oppo,dtsi\_no = &lt;19081&gt;\) on Qualcomm Snapdragon 855 Plus \(SM8150-AC, msm-id = &lt;0x153 0x20000&gt;, board-id = &lt;8 0&gt;\).
- UniXNU-sm8150-common shared SoC repository pinned at commit f363dcda920101a99e440ce3e8b68849122a3c0a.
- Upstream Android kernel DTS reference guh0613/android\_kernel\_oppo\_sm8150 \(arch/arm64/boot/dts/19081/\) and UEFI reference Project-Aloha/mu\_aloha\_platforms \(Platforms/SurfaceDuo1Pkg/Device/oppo-pclm10/\).

### 配置

- board.toml selects schema\_version = 2, board.name = 'pclm10', board.soc = 'SM8150', board.soc\_source = 'sm8150', and board.os\_profile = 'ipados-17.7.11-21H461'.
- configs/pclm10\_defconfig sets CONFIG\_BOARD\_PCLM10=y and CONFIG\_SOC\_SM8150=y on top of arch:configs/common.config, soc:configs/sm8150.config, and os:configs/ipados.config.
- Patch series order is arch:patches/xnu/series, soc:patches/xnu/series, os:patches/xnu/series, device:patches/xnu/series.

### 操作步骤

- Run ./unixnu defconfig pclm10\_defconfig -D ../UniXNU-pclm10 from the UniXNU checkout.
- Verify resolution and status via ./unixnu status --json -D ../UniXNU-pclm10 and python3 scripts/porting-record.py check --device ../UniXNU-pclm10.

### 开发经验

- Retail model PCLM10 corresponds to OPPO project 19081 \(SM8150-AC\); early community posts occasionally confused PCKM00 \(OPPO Reno2 SM7150\) with Reno Ace.
- All selected components in board.toml resolve against canonical IDs in UniXNU/components.toml \(ArmDTPlatform, ArmCpu, SoftwareAES, DarwinBoot, XnuPrelink, GopFramebuffer, RamBlock, VirtioMmioBlock, ShengUfs, VerifiedRoot, AppleKeyStoreState\).

### 完成条件

- All source pins resolve; every selected component has a record; status shows the intended overrides and patch order.

### 当前范围

- Board-specific XNU patches remain empty until first hardware boot log triage.

### 下一步

- Build the prelinked kernel and UEFI boot image via GitHub Actions macOS runner or local Xcode toolchain.

### 证据

- `source`: [Format 2 board manifest configures pclm10, SM8150 SoC source, ipados-17.7.11-21H461 profile, and 11 canonical components.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/29e9f7cc47421f0ceb6419ce0031e998642383d3/board.toml)
- `source`: [Pins UniXNU-sm8150-common at commit f363dcda920101a99e440ce3e8b68849122a3c0a.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/29e9f7cc47421f0ceb6419ce0031e998642383d3/feeds.toml)
- `source`: [Defines CONFIG\_BOARD\_PCLM10=y and CONFIG\_SOC\_SM8150=y.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/29e9f7cc47421f0ceb6419ce0031e998642383d3/configs/pclm10_defconfig)

## 固件与启动 {#firmware}

`implemented`

组件: `DarwinBoot`.

### 硬件与依赖

- Project-Aloha / Silicium EDK2 UEFI firmware for oppo-pclm10 \(Platforms/SurfaceDuo1Pkg/Device/oppo-pclm10\) and UniXNU/uefi-sheng.
- Extracted single DTB dts/oppo-pclm10-19081.dtb \(486447 bytes, oppo,prjversion = &lt;1 19081&gt;\) containing /reserved-memory/cont\_splash\_region at 0x9d000000 \(size 0x02400000\).
- UEFI FD loaded at 0x9fc00000 \(size 0x00300000\), FV region at 0x9f800000 \(size 0x00400000\), SEC heap/page tables/stack at 0x9ff00000..0xa0000000, DXE heap at 0xa5800000 \(size 0x1a800000\).

### 配置

- board.toml \[firmware\] selects config = 'pclm10', dsc = 'Platforms/OPPO/pclm10Pkg/pclm10.dsc', preflight = \['scripts/prepare-pclm10-uefi.py'\], and \[bootimg\] dtb = 'build/pclm10/pclm10.dtb'.
- scripts/prepare-pclm10-uefi.py injects Resources/Configs/pclm10.toml and Platforms/OPPO/pclm10Pkg/ into the UniXNU/uefi-sheng checkout and stages dts/oppo-pclm10-19081.dtb to build/pclm10/pclm10.dtb.

### 操作步骤

- Run scripts/prepare-pclm10-uefi.py --uefi ../uefi-pclm10 --device . --tree ../UniXNU, then build UEFI firmware with DarwinBoot integrated and pack into Android boot.img.

### 开发经验

- dts/oppo-pclm10-19081.dtb already defines /reserved-memory/cont\_splash\_region \(0x9d000000, 0x02400000\), qseecom\_region \(0xa0000000, 0x01400000\), and cdsp\_sec\_regions \(0xa4c00000, 0x00c00000\), so placing DXE Heap at 0xa5800000 \(424 MiB\) avoids all Bank 0 carveouts.

### 完成条件

- Firmware image builds, enters UniXNU via DarwinBoot, publishes the 1080x2400 framebuffer, and preserves documented memory reservations.

### 当前范围

- On-device fastboot boot verification of the DarwinBoot handoff is pending.

### 下一步

- Trigger the GitHub Actions package workflow to build boot.img and payload.img and test fastboot boot on PCLM10 hardware.

### 证据

- `source`: [Firmware build recipe, preflight script, and bootimg DTB path configured.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/29e9f7cc47421f0ceb6419ce0031e998642383d3/board.toml)
- `source`: [Generates Resources/Configs/pclm10.toml and Platforms/OPPO/pclm10Pkg/ and stages build/pclm10/pclm10.dtb.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/29e9f7cc47421f0ceb6419ce0031e998642383d3/scripts/prepare-pclm10-uefi.py)
- `source`: [Extracted single-board DTB \(486447 bytes\) for OPPO project 19081 with cont\_splash\_region@9d000000.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/29e9f7cc47421f0ceb6419ce0031e998642383d3/dts/oppo-pclm10-19081.dtb)

## CPU 与中断 {#cpu}

`planned`

组件: `ArmCpu`.

### 硬件与依赖

- 8x Kryo 485 cores \(MPIDR 0x000..0x700\): 4x Cortex-A55 Silver \(0x000..0x300 @ 1.80 GHz\), 3x Cortex-A76 Gold \(0x400..0x600 @ 2.42 GHz\), 1x Cortex-A76 Prime \(0x700 @ 2.96 GHz\).
- PSCI 1.0 over SMC; GICv3 distributor at 0x17a00000 \(size 0x10000\), redistributors at 0x17a60000 \(size 0x100000, stride 0x20000\); 19.2 MHz architected counter with virtual timer INTID 19.

### 配置

- Inherited from UniXNU-sm8150-common dts/sm8150.dtsi via dts/pclm10.dts.
- board.toml sets cpu\_regs = '0,0x100,0x200,0x300,0x400,0x500,0x600,0x700', psci\_method = 'smc', and kernel\_args = \['-v', 'serial=3', 'cpus=8', 'armcpu-self-ipi=1'\].

### 操作步骤

- Boot XNU with cpus=8 and armcpu-self-ipi=1 and verify all 8 Kryo 485 cores come online with working GICv3 SGI IPIs and virtual timer interrupts.

### 开发经验

- SM8150-AC shares identical MPIDR affinities \(0x000..0x700\), GICv3 MMIO windows \(0x17a00000 / 0x17a60000\), and timer INTID \(19\) with verified SM8150 boards \(nabu, raphael\).

### 完成条件

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU.

### 当前范围

- EPSS dynamic frequency scaling for the 2.96 GHz Prime core is not yet implemented.

### 下一步

- Verify 8-core SMP bring-up on device and confirm SGI counters.

### 证据

- `source`: [Declares 8 CPU MPIDR affinities, PSCI smc method, and armcpu-self-ipi=1 boot argument.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/29e9f7cc47421f0ceb6419ce0031e998642383d3/board.toml)

## 内存与 DMA {#memory}

`implemented`

### 硬件与依赖

- 8 GB / 12 GB LPDDR4X @ 2133 MHz across Bank 0 \(0x80000000..0xbbb00000\), Carveout Hole \(0xbbb00000..0xc0000000\), Bank 1 \(0xc0000000, size 0x80000000\), and Bank 2 \(0x140000000+\).
- OPPO project 19081 reserved-memory layout: hyp\_mem \(0x85700000, 0x600000\), xbl\_aop\_mem + cmd\_db \(0x85d00000..0x85f40000\), gpu\_prr \(0x85f40000, 0x10000\), smem \(0x86000000, 0x200000\), qtee \(0x86200000, 0x1800000\), expanded tzapps\_mem \(0x87a00000, 0x5d00000\), pil\_mem \(0x8d700000, 0xf400000\), cont\_splash\_region \(0x9d000000, 0x2400000\), fv\_region \(0x9f800000, 0x400000\), uefi\_fd \(0x9fc00000, 0x300000\), pstore \(0x17fe00000, 0x200000\).
- Apps SMMU-500 at 0x15000000 \(UFS stream 0x300\) and GPU SMMU-500 at 0x02ca0000.

### 配置

- dts/pclm10.dts sets memory@c0000000 reg = &lt;0x0 0xc0000000 0x0 0x80000000&gt; \(2 GiB contiguous baseline in Bank 1\) and records all 11 no-map reserved-memory regions plus ramoops pstore.
- board.toml sets payload.dram\_size = '0x80000000' and payload.adt.owned\_memory\_size = '0x40000000'.

### 操作步骤

- Extracted and cross-checked android-pclm10.dtb, 19081/sm8150-mtp.dtsi, and Project-Aloha oppo-pclm10 PlatformMemoryMapLib.c.

### 开发经验

- OPPO project 19081 expands tzapps\_region at 0x87a00000 from 0x3900000 \(57 MiB\) to 0x5d00000 \(94 MiB\) for OPLUS\_FEATURE\_FINGERPRINT\_SECURE, which shifts pil\_region start to 0x8d700000 \(size 0x0f400000\).
- Placing XNU's contiguous DRAM window at 0xc0000000 cleanly bypasses all Bank 0 firmware carveouts and the 0xbbb00000..0xc0000000 hole.

### 完成条件

- All handoff regions are accounted for and each enabled DMA engine accesses its allocated range with the documented cache policy.

### 当前范围

- DRAM window is conservatively capped at 2 GiB \(Bank 1\) for initial bring-up before expanding across Bank 2 \(5 GiB total\).

### 下一步

- Verify SMMU translation for UFS \(0x15000000 stream 0x300\) and Adreno 640 \(0x02ca0000\) during device boot.

### 证据

- `source`: [Defines memory@c0000000 and all OPPO project 19081 reserved-memory carveouts.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/29e9f7cc47421f0ceb6419ce0031e998642383d3/dts/pclm10.dts)
- `source`: [Sets dram\_size = 0x80000000, owned\_memory\_size = 0x40000000, and cont\_splash\_region DTB node.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/29e9f7cc47421f0ceb6419ce0031e998642383d3/board.toml)

## 存储与根卷 {#storage}

`planned`

组件: `SoftwareAES`.

### 硬件与依赖

- Samsung UFS 3.0 storage \(128 GB / 256 GB\) on Qualcomm ufshc@1d84000 \(MMIO 0x01d84000, size 0x2500\), QMP v4 PHY at 0x01d87000, ICE at 0x01d90000, GCC UFS clock window at 0x00177000 \(size 0x1000\).
- Apps SMMU at 0x15000000 with stream ID 0x300 and 4096-byte logical block size.

### 配置

- dts/pclm10.dts enables &amp;ufs and &amp;ufs\_smmu from sm8150.dtsi.
- board.toml selects ShengUfs, RamBlock, VirtioMmioBlock, SoftwareAES, and VerifiedRoot with packed\_data\_ramdisk = true and root\_match\_volume\_uuid = '04769D26-2CA0-4825-B443-E2E5F88300F2'.

### 操作步骤

- Boot with ShengUfs and RamBlock enabled, stage the root image in userdata or ramdisk, and verify LUN0 4K block reads and APFS root mount.

### 开发经验

- UFS controller base \(0x01d84000\), GCC window \(0x00177000\), SMMU base \(0x15000000\), and stream ID \(0x300\) match the SM8150 ShengUfs contract in UniXNU-sm8150-common.

### 完成条件

- Host: register, clock, link and SMMU facts match the board inventory.
- Reads: SCSI capacity, GPT and known blocks are correct; OS/SystemOS windows stay within userdata.
- Root: the configured volume mounts and launchd starts. Persistence: writes survive reboot within the allocated Data region.

### 当前范围

- Initial bring-up uses volatile packed\_data\_ramdisk = true before provisioning a persistent UFS Data slice.

### 下一步

- Verify ShengUfs LUN0 probe and root volume mount on PCLM10 hardware.

### 证据

- `source`: [Enables &amp;ufs \(0x01d84000\) and &amp;ufs\_smmu \(0x15000000, stream 0x300\).](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/29e9f7cc47421f0ceb6419ce0031e998642383d3/dts/pclm10.dts)

## 显示 {#display}

`planned`

组件: `GopFramebuffer`.

### 硬件与依赖

- Samsung SOFEF03F-M 6.5-inch FHD+ \(1080x2400 @ 90Hz\) single-DSI command-mode AMOLED panel with DSC \(dsi\_samsung\_sofef03f\_m\_amoled\_fhd\_plus\_90fps\_cmd\).
- Panel TLMM GPIOs: TE = GPIO 8, Reset = GPIO 6, Mode/VDDD\(1.1V\) = GPIO 152, VCI\(3.0V\) = GPIO 25, ErrFlag = GPIO 49; DCS backlight range 6..2047.
- UEFI GOP continuous splash linear framebuffer at 0x9d000000 \(size 0x02400000, 1080x2400, 32bpp xRGB8888, stride 4320\).

### 配置

- board.toml includes GopFramebuffer, sets panic\_screen = true, and reserves /reserved-memory/cont\_splash\_region at 0x9d000000 \(0x02400000\).
- dts/pclm10.dts defines cont\_splash\_region@9d000000 and framebuffer0@9d000000 \(width 1080, height 2400, stride 4320, format a8r8g8b8\).

### 操作步骤

- Boot into DarwinBoot and XNU with -v serial=3 and verify early console text and panic screen render cleanly on the 1080x2400 AMOLED panel.

### 开发经验

- Both 19081/sm8150-sde-display.dtsi and Project-Aloha DSDT.aml confirm the single-DSI Samsung SOFEF03F-M 1080x2400@90Hz panel and 0x9d000000 framebuffer base.

### 完成条件

- A known frame appears with correct geometry and colors, then userland presentation and backlight controls work.

### 当前范围

- DCS backlight brightness control and native DPU tear-effect \(TE GPIO 8\) refresh modulation are not yet wired.

### 下一步

- Confirm GOP early console output at 0x9d000000 on physical device.

### 证据

- `source`: [Documents framebuffer0@9d000000 \(1080x2400, stride 4320\) and cont\_splash\_region@9d000000.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/29e9f7cc47421f0ceb6419ce0031e998642383d3/dts/pclm10.dts)

## 输入 {#input}

`planned`

### 硬件与依赖

- Primary touchscreen: Synaptics S3706 \(compatible = 'synaptics-s3706', I2C slave 0x20\) on qupv3\_se17\_i2c \(MMIO 0x00c80000, size 0x4000, qupv3\_2 wrapper 0x00c00000, GIC SPI 373\).
- Touch TLMM GPIOs &amp; power: irq-gpio = &lt;&amp;tlmm 122 0x2008&gt;, reset-gpio = &lt;&amp;tlmm 54 0x1&gt;, vdd\_2v8 = &lt;&amp;pm8150\_l17&gt; \(3.0V\), enable1v8\_gpio = &lt;&amp;pm8150l\_gpios 5 0x1&gt;; 1080x2400 coords, 15x34 TX/RX, 10 contacts @ 120Hz.
- Physical buttons: Volume Up \(&amp;pm8150\_gpios 6\), Volume Down \(&amp;pm8150\_gpios 7\), Power key via PM8150 PON.

### 配置

- dts/pclm10.dts declares qupv3\_se17\_i2c \(i2c@c80000\) and child node touchscreen@20 \(synaptics,s3706\) with panel/display geometry 1080x2400.
- proprietary-files.txt tracks firmware/tp/19081/19081\_FW\_S3706\_SYNAPTICS.img.

### 操作步骤

- Implement GeniI2c + Synaptics S3706 RMI4/TouchComm kext polling or interrupt-driven on QUPv3 SE17 \(0x00c80000\) and publish digitizer events via IOHIDEventDriverSafeBoot.

### 开发经验

- Inspection of guh0613/android\_kernel\_oppo\_sm8150 arch/arm64/boot/dts/19081/sm8150-mtp.dtsi confirmed Synaptics S3706 at 0x20 on qupv3\_se17\_i2c \(0x00c80000\), distinct from Xiaomi Pad 5's SPI Novatek NT36523.

### 完成条件

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive, and buttons produce expected HID reports.

### 当前范围

- Synaptics S3706 XNU IOHID driver is planned and not yet compiled into the kernel.

### 下一步

- Write a minimal QUPv3 SE17 GeniI2c + Synaptics S3706 RMI4 touch driver for pclm10.

### 证据

- `source`: [Documents qupv3\_se17\_i2c \(0x00c80000\) and touchscreen@20 \(synaptics,s3706\).](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/29e9f7cc47421f0ceb6419ce0031e998642383d3/dts/pclm10.dts)
- `source`: [Lists firmware/tp/19081/19081\_FW\_S3706\_SYNAPTICS.img.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/29e9f7cc47421f0ceb6419ce0031e998642383d3/proprietary-files.txt)

## GPU {#gpu}

`planned`

### 硬件与依赖

- Qualcomm Adreno 640 v2 \(SM8150-AC bin, up to 675 MHz, chip-id 0x06040001, 1 MiB GMEM\).
- MMIO windows: kgsl\_3d0 0x02c00000 \(0x40000\), GMU 0x02c6a000 \(0x30000\), RSCC 0x02c8d000 \(0x2000\), PDC 0x0b290000 / 0x0b490000, GPU SMMU-500 0x02ca0000, GPUCC 0x02c90000 \(0x9000\), GCC 0x00100000 \(0x1f0000\).
- Reserved regions: AOP CMD DB 0x85f20000 \(0x20000\), GPU PRR 0x85f40000 \(0x10000\), PIL GPU ZAP shader region 0x99515000 \(0x2000\).

### 配置

- soc:configs/sm8150.config enables CONFIG\_XNU\_NATIVE\_ADRENO=y.
- dts/pclm10.dts enables &amp;gpu, &amp;gmu, &amp;gpu\_smmu, &amp;gpucc, and &amp;gcc from sm8150.dtsi.
- proprietary-files.txt lists a640\_sqe.fw, a640\_gmu.bin, and a640\_zap.&\#123;mdt,b00,b01,b02,elf&\#125;.

### 操作步骤

- Stage Adreno 640 vendor firmware from PCLM10 /vendor/firmware, note the 0x99515000 ZAP PIL address on project 19081, and test GMU/CP ring initialization.

### 开发经验

- Because OPPO project 19081 shifts pil\_region to 0x8d700000, the GPU ZAP PIL sub-region sits at 0x99515000 \(size 0x2000\) rather than nabu's 0x98f15000.

### 完成条件

- GPU submissions complete, mapping/fence handling is correct, a known image renders, and the selected Metal client presents it.

### 当前范围

- Adreno 640 ZAP shader physical address offset \(0x99515000\) must be passed to the GPU bring-up driver.

### 下一步

- Extract a640\_\* firmware blobs from PCLM10 vendor image and test Adreno 640 initialization after CPU/storage boot.

### 证据

- `source`: [Enables &amp;gpu, &amp;gmu, &amp;gpu\_smmu, &amp;gpucc, &amp;gcc and documents the 0x99515000 GPU ZAP PIL offset.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/29e9f7cc47421f0ceb6419ce0031e998642383d3/dts/pclm10.dts)
- `source`: [Records Adreno 640 SQE, GMU, and ZAP firmware paths.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/29e9f7cc47421f0ceb6419ce0031e998642383d3/proprietary-files.txt)

## 网络 {#network}

`planned`

### 硬件与依赖

- Qualcomm WCN3990 integrated 802.11a/b/g/n/ac 2x2 MU-MIMO Wi-Fi &amp; Bluetooth 5.0 \(BT UART on qupv3\_se14\_4uart @ 0x00a98000, WLAN FW PIL at 0x9b000000 size 0x00180000\).
- Synopsys DWC3 USB 3.1 Dual-Role Controller at 0x0a600000.

### 配置

- pil\_mem in dts/pclm10.dts preserves the WLAN firmware carveout at 0x9b000000 \(0x00180000\).

### 操作步骤

- Bring up USB gadget networking \(CDC-NCM/ECM\) over DWC3 \(0x0a600000\) first for host tether, then evaluate WCN3990 SNOC/QMI driver requirements.

### 开发经验

- PCLM10 uses the on-SoC WCN3990 \(SNOC/QMI architecture\) rather than PCIe MHI QCA6390/Ath12k.

### 完成条件

- Scanning, association, address configuration and sustained receive/transmit traffic pass with the selected firmware.

### 当前范围

- Neither USB networking nor WCN3990 Wi-Fi is active in the initial configuration.

### 下一步

- Evaluate DWC3 USB peripheral mode at 0x0a600000 for early tethered debugging and networking.

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`planned`

### 硬件与依赖

- Qualcomm WCD934x \(Tavil\) audio codec over SLIMbus, dual stereo speakers \(Dolby Atmos\), 3.5mm headset jack, and ADSP PIL region at 0x9b200000 \(size 0x01e00000\).

### 配置

- dts/pclm10.dts preserves smem\_mem \(0x86000000\) and adsp\_region inside pil\_mem \(0x9b200000, 0x01e00000\).

### 操作步骤

- Defer audio subsystem bring-up until interactive UI and touch input are verified.

### 开发经验

- ADSP firmware carveout is located at 0x9b200000 \(30 MiB\) in android-pclm10.dtb.

### 完成条件

- Each declared route carries the selected audio format through playback or capture and handles start/stop correctly.

### 当前范围

- ADSP GLINK/APR and WCD934x codec drivers are not implemented.

### 下一步

- Defer until after display, storage, and touch bring-up.

### 证据

按下一步操作收集证据。

## 电源 {#power}

`planned`

### 硬件与依赖

- PM8150, PM8150B, and PM8150L PMICs over SPMI; RPMh RSC at 0x18220000 and AOP CMD DB at 0x85f20000.
- 65W SuperVOOC 2.0 4000 mAh dual-cell battery with BQ27541 fuel gauge \(oppo,bq27541-battery @ 0x55\) and STM8S fast-charge MCU \(oppo,stm8s-fastcg @ 0x26\) on qupv3\_se1\_i2c \(0x00a80000\).
- Awinic AW8697 LRA haptic actuator \(awinic,aw8697\_haptic @ 0x5a\) on qupv3\_se7\_i2c \(0x0089c000, TLMM reset GPIO 116, IRQ GPIO 24\).

### 配置

- dts/pclm10.dts documents qupv3\_se1\_i2c \(0x00a80000\) with battery@55 and fastcg@26, and qupv3\_se7\_i2c \(0x0089c000\) with haptic@5a.
- xbl\_aop\_mem in dts/pclm10.dts preserves the AOP Command DB at 0x85f20000 \(size 0x20000\).

### 操作步骤

- Rely on XBL/ABL/UEFI regulator handoff for initial boot; later add BQ27541 I2C battery telemetry on qupv3\_se1\_i2c \(0x00a80000\).

### 开发经验

- OPPO Reno Ace uses an external TI BQ27541 fuel gauge at I2C 0x55 and STM8S SuperVOOC MCU at 0x26 on QUPv3 SE1 I2C \(0x00a80000\) alongside PM8150B.

### 完成条件

- Declared power controls and battery readings match observations; each claimed sleep/resume transition restores its dependent peripherals.

### 当前范围

- Dynamic PMIC rail voting, sleep/resume, and SuperVOOC telemetry are not yet implemented.

### 下一步

- Verify continuous regulator state across ExitBootServices during initial XNU boot.

### 证据

- `source`: [Documents qupv3\_se1\_i2c \(0x00a80000\) battery/fastcg nodes and qupv3\_se7\_i2c \(0x0089c000\) AW8697 haptics.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/29e9f7cc47421f0ceb6419ce0031e998642383d3/dts/pclm10.dts)

## 镜像组装 {#packaging}

`implemented`

组件: `XnuPrelink`, `AppleKeyStoreState`.

### 硬件与依赖

- Android boot.img \(UEFI FD + patched DTB\) and 192 MiB FAT32 payload.img \(volume PCLM10\) carrying prelinked kernel.macho, pclm10.dtb, and ramdisk.
- Target OS profile ipados-17.7.11-21H461 with chip\_id = 32785, ipad\_identity = true, packed\_data\_ramdisk = true, and unique\_chip\_id = 'required'.

### 配置

- board.toml configures \[package\], \[firmware\], \[bootimg\], \[payload\], and \[payload.adt\].
- scripts/package.sh and .github/workflows/package.yml invoke \`unixnu release -D .\` to build kernel, prelink, firmware, payload.img, and boot.img.

### 操作步骤

- Run scripts/package.sh --os 17 --check \(or dispatch .github/workflows/package.yml on a macOS runner with UNIXNU\_UNIQUE\_CHIP\_ID set\).

### 开发经验

- Packaging pipeline uses the standard Format 2 declarative sections in board.toml with zero custom packaging scripts required.

### 完成条件

- Kernel and prelink succeed, payload contains all declared inputs, and the boot image matches the bootloader format and size limit.

### 当前范围

- Full Mach-O kernel build and prelink require macOS with full Xcode \(iphoneos SDK\) or the GitHub Actions macos-26 runner.

### 下一步

- Execute the full packaging workflow on a macOS runner or local Xcode install to produce boot.img and payload.img.

### 证据

- `source`: [Defines \[package\], \[firmware\], \[bootimg\], \[payload\], and \[payload.adt\] sections.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/29e9f7cc47421f0ceb6419ce0031e998642383d3/board.toml)
- `source`: [Standard Format 2 release entry point invoking unixnu release.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/29e9f7cc47421f0ceb6419ce0031e998642383d3/scripts/package.sh)

## 诊断 {#diagnostics}

`planned`

### 硬件与依赖

- UEFI GOP panic screen at 0x9d000000 \(1080x2400 @ 32bpp\) and PStore ramoops region at 0x17fe00000 \(size 0x00200000\).

### 配置

- board.toml sets panic\_screen = true and kernel\_args = \['-v', 'serial=3', 'cpus=8', 'armcpu-self-ipi=1'\].
- dts/pclm10.dts reserves pstore\_region: ramoops@17fe00000 \(0x00200000, record/console/ftrace/pmsg 0x40000 each\).

### 操作步骤

- Boot XNU with -v serial=3 and panic\_screen = true; inspect on-screen panic backtraces or read 0x17fe00000 ramoops across warm reboot.

### 开发经验

- Project-Aloha oppo-pclm10 PlatformMemoryMapLib.c defines PStore at 0x17fe00000 \(size 0x00200000\), providing a persistent RAM buffer above Bank 1 for crash logs.

### 完成条件

- Each claimed milestone has a reproducible command, a matching source/image revision and an accessible result.

### 当前范围

- Persistent ESP/ramoops log writer kext is not yet enabled on pclm10.

### 下一步

- Capture the first early-boot framebuffer log on OPPO Reno Ace hardware.

### 证据

- `source`: [Enables panic\_screen = true and verbose kernel boot arguments \(-v serial=3\).](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/29e9f7cc47421f0ceb6419ce0031e998642383d3/board.toml)
- `source`: [Reserves ramoops@17fe00000 \(0x00200000\) matching the UEFI PStore region.](https://github.com/shmilylee409-a11y/UniXNU-pclm10/blob/29e9f7cc47421f0ceb6419ce0031e998642383d3/dts/pclm10.dts)

</div>
