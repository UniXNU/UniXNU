# Xiaomi Pad 5 Pro 12.4 \(dagu\), China-region Wi-Fi model 22081281AC, SM8250-AC, iPadOS 17.7.11 / arm64 target

[wayyoungboy/UniXNU-dagu](https://github.com/wayyoungboy/UniXNU-dagu)

<div v-pre>

Source and porting skeleton for the Xiaomi Pad 5 Pro 12.4 \(dagu, China-region Wi-Fi, 22081281AC\). Inputs collected from public DTS and device trees; not booted. Cannot be flashed until the bootloader is unlocked.

Source record: [porting.toml](https://github.com/wayyoungboy/UniXNU-dagu/blob/f8d638e3dd419c1e160d191d55e751808f3d5884/porting.toml), `f8d638e3dd419c1e160d191d55e751808f3d5884`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `planned` |
| [Firmware and boot](#firmware) | `planned` |
| [CPU and interrupts](#cpu) | `planned` |
| [Memory and DMA](#memory) | `planned` |
| [Storage and root](#storage) | `planned` |
| [Display](#display) | `planned` |
| [Input](#input) | `planned` |
| [GPU](#gpu) | `planned` |
| [Network](#network) | `planned` |
| [cellular](#cellular) | `not-applicable` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `planned` |
| [Image assembly](#packaging) | `planned` |
| [Diagnostics](#diagnostics) | `planned` |

## Configuration {#configuration}

`planned`

Components: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`, `DarwinBoot`.

### Hardware and dependencies

- Board identity: Xiaomi Pad 5 Pro 12.4, China-region Wi-Fi, codename dagu, model 22081281AC.
- SoC: Qualcomm SM8250-AC \(Snapdragon 870\), Adreno 650, octa-core Kryo 585.
- Intended OS profile: ipados-17.7.11-21H461 \(iPadOS 17 / arm64\). iPadOS 27 and macOS 27 / arm64e are not selected.
- SoC feed: FFT-infra/UniXNU-sm8250-common commit 166235ec2480ff0992627b7aafa15c65ce6b4efa \(community SM8250 common; no UniXNU-org SM8250 repository\).
- Closest software cousins: elish \(Pad 5 Pro 11-inch Wi-Fi\) and enuma \(Pad 5 Pro 5G\). umi is a farther SM8250 phone reference; SoC-level items only.

### Configuration

- board.toml schema\_version = 2, board.name = dagu, board.soc = SM8250-AC, board.soc\_source = sm8250, board.os\_profile = ipados-17.7.11-21H461, board.kit = dagu.
- feeds.toml pins source sm8250 to https://github.com/FFT-infra/UniXNU-sm8250-common at 166235ec2480ff0992627b7aafa15c65ce6b4efa.
- kernel.defconfig = dagu\_defconfig; device\_tree.source = device:dts/dagu.dts; include\_dirs = \[soc:dts\].
- config\_fragments = \[arch:configs/common.config, soc:configs/sm8250.config, os:configs/ipados.config\].
- patch\_series = \[arch:patches/xnu/series, soc:patches/xnu/series, os:patches/xnu/series, device:patches/xnu/series\].
- components.include = \[ArmDTPlatform, ArmCpu, SoftwareAES, XnuPrelink, DarwinBoot\]. Storage, display, input and GPU components are not selected.

### Procedure

- Copy UniXNU/examples/device, rename the defconfig and DTS to dagu, then retarget board.toml and feeds.toml from SM8550 to SM8250-AC and the iPadOS 17.7.11 profile.
- Fill hardware comments from opened public DTS and device trees. Leave DRAM size and userdata LBA as TODO.
- From the UniXNU checkout: ./unixnu defconfig dagu\_defconfig -D ../UniXNU-dagu, then ./unixnu fetch -D ../UniXNU-dagu and python3 scripts/porting-record.py check --device ../UniXNU-dagu when the Linux host can run them.

### Development findings

- On this Linux host, ./unixnu defconfig dagu\_defconfig -D ../UniXNU-dagu and ./unixnu fetch -D ../UniXNU-dagu resolved arch/arm64, FFT-infra/UniXNU-sm8250-common at 166235ec2480ff0992627b7aafa15c65ce6b4efa, ipados-17.7.11-21H461 and the dagu board, then wrote unixnu.lock. status showed the intended component set and the SoC SMP patches in the series.
- Official UniXNU does not ship a SM8250 common repository. Nearby format 2 ports pin FFT-infra/UniXNU-sm8250-common at 166235ec, which provides dts/sm8250.dtsi, soc/configs/sm8250.config and the two SMP patch series.
- The official template defaults to SM8550 and iPadOS 17.7.11. This board keeps the same OS profile and arm64 path and only changes the SoC layer.
- board.example is omitted because identity, the SoC pin and sourced DTS facts are filled. Unknown measured values are explicit TODOs rather than invented numbers.

### Completion criteria

- unixnu defconfig and fetch resolve the intended ARM64, SM8250, iPadOS 17.7.11 and dagu profiles with the pinned SoC commit.
- status --json shows the complete fragment and patch order, and every selected component has a record area.

### Current limits

- This is a source skeleton produced on a Linux build box. It has not been host-verified with a full image build and has not been booted.
- A uefi-dagu firmware repository does not exist yet.

### Next action

- After publication, confirm the Porting record workflow on the default branch. A full image build remains macOS/firmware-blocked.

### Evidence

- `source`: [Official format 2 layout, publication topic and array-replacement rules used for this skeleton.](https://unixnu.com/porting/device-repository)
- `source`: [Pinned SM8250 common commit used by nearby SM8250-AC community ports.](https://github.com/FFT-infra/UniXNU-sm8250-common/commit/166235ec2480ff0992627b7aafa15c65ce6b4efa)
- `source`: [Closest Wi-Fi family cousin \(elish\). Used for SoC/OS profile comparison only; board wiring was not copied.](https://github.com/hpadmx/UniXNU-elish)
- `source`: [Closest format 2 SM8250-AC iPadOS 17 port structure. Used as a layout reference; unique enuma values were not copied.](https://github.com/wh1stl3/UniXNU-enuma)

## Firmware and boot {#firmware}

`planned`

### Hardware and dependencies

- Target firmware checkout would be a future uefi-dagu Mu-Silicium package \(Platforms/Xiaomi/daguPkg/dagu.dsc\). It is not published.
- Stock software on the user's unit was last recorded as official HyperOS 2 OS2.0.10.0.ULZCNXM. Official bind/unlock is currently closed.
- PSCI method smc is provided by soc:dts/sm8250.dtsi.

### Configuration

- firmware.config = dagu, firmware.dsc = Platforms/Xiaomi/daguPkg/dagu.dsc, firmware.fd = Build/daguPkg/&\#123;target&\#125;\_CLANGPDB/FV/SILICIUM\_UEFI.fd.
- firmware.defines.DEVICE\_MODEL = dagu.
- payload.loader = firmware, payload.volume = DAGU, payload.size\_mib = 192, payload.kernel\_args = \[-v, serial=3\].
- No \[bootimg.image\] or splash \[\[bootimg.dtb\_node\]\] is set; those need a dagu bootloader and firmware DTB contract.

### Procedure

- Keep proprietary inputs out of git. List each extracted file in proprietary-files.txt only after a measured SHA-256 exists.
- Do not assemble or flash a boot image until an official unlock is available and userdata/DRAM inputs are measured.

### Development findings

- Rinko-Studio BoardConfig.mk uses Android boot header version 3 and pagesize 4096 for the stock Linux kernel. That is not evidence for UniXNU's mkbootimg layout on this board.
- A splash reserved region was not present in the opened dagu overlay or dagu-sm8250.dtsi. elish numbers were not copied.

### Completion criteria

- A board firmware package exists, builds, and documents framebuffer and memory handoff for dagu.
- Every required firmware member is listed with a measured hash in proprietary-files.txt.

### Current limits

- No uefi-dagu tree, no hashed firmware members, and no device firmware log exist yet.
- The bootloader is locked; this repository must not be treated as a flashable image source.

### Next action

- Create a dagu UEFI package only after the required firmware archive can be imported into .cache/firmware and hashed.

### Evidence

- `source`: [Stock Linux boot header version 3 is recorded; UniXNU boot image parameters remain TODO.](https://github.com/Rinko-Studio/android_device_xiaomi_dagu/blob/66695faea165da63e7a8eac781ea2241df06a6dd/BoardConfig.mk)

## CPU and interrupts {#cpu}

`planned`

### Hardware and dependencies

- SoC include dts/sm8250.dtsi: eight Kryo 585 cores, cpu@0..@300 Cortex-A55, cpu@400..@700 Cortex-A77, timebase-frequency 19200000, psci method smc.
- GICv3 at 0x17a00000 \(distributor 64 KiB\) and 0x17a60000 \(redistributors\), compatible arm,gic-v3, from the same SoC include.
- qcom,msm-id family 356 from kona.dtsi / kona-v2.dtsi / kona-v2.1.dtsi; board-id 51 0 from the dagu overlay.

### Configuration

- dagu.dts includes sm8250.dtsi and does not override CPU status; all eight SoC CPU nodes remain enabled.
- payload.adt.chip\_id = 356, derived from the kona qcom,msm-id, with unique\_chip\_id required.

### Procedure

- Keep CPU affinities and GIC ranges in the SoC repository. Record any dagu-specific enable or disable decisions in dts/dagu.dts.
- Confirm the live msm-id revision \(0x10000 / 0x20000 / 0x20001\) from a dagu firmware DTB or sysfs once the device can be read.

### Development findings

- The dagu overlay is built against kona.dtb, kona-v2.dtb and kona-v2.1.dtb, so the running msm-id revision depends on silicon and the selected base DTB. SM8250-AC corresponds to kona v2.1 \(356 0x20001\).
- payload.adt.chip\_id is a software identity, not an ECID.

### Completion criteria

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU.

### Current limits

- No dagu host or device CPU bring-up has been run. cpu\_regs is not pinned in board.toml.

### Next action

- After a firmware package exists, confirm MPIDR / enabled cores from a dagu DTB or live FDT.

### Evidence

- `source`: [Eight-core map, PSCI smc, GICv3 0x17a00000/0x17a60000 and 19.2 MHz timebase.](https://github.com/FFT-infra/UniXNU-sm8250-common/blob/166235ec2480ff0992627b7aafa15c65ce6b4efa/dts/sm8250.dtsi)
- `source`: [dagu qcom,board-id = &lt;51 0&gt;.](https://github.com/LineageOS/android_kernel_xiaomi_sm8250/blob/6b34d24765327d746074c8e53b5ad0d24a51acc7/arch/arm64/boot/dts/vendor/qcom/dagu-sm8250-overlay.dts)
- `source`: [kona v2.1 qcom,msm-id = &lt;356 0x20001&gt;.](https://github.com/LineageOS/android_kernel_xiaomi_sm8250/blob/6b34d24765327d746074c8e53b5ad0d24a51acc7/arch/arm64/boot/dts/vendor/qcom/kona-v2.1.dtsi)

## Memory and DMA {#memory}

`planned`

### Hardware and dependencies

- Public device documentation lists RAM SKUs of 6 GB, 8 GB and 12 GB paired with 128 GB, 256 GB and 512 GB UFS.
- The opened dagu overlay and dagu-sm8250.dtsi do not publish a /memory reg. Stock kona.dtsi uses a zero placeholder.
- Family-common reserved nodes inherited through xiaomi-sm8250-common.dtsi: xbl\_aop\_mem at 0x80600000 size 0x260000, disp\_rdump\_memory at 0xb0400000 size 0x01000000. These are not a complete dagu memory map.

### Configuration

- dts/dagu.dts memory@0 currently has reg = &lt;0 0 0 0&gt; as an explicit placeholder.
- payload.dram\_size is intentionally unset so a single SKU is not pinned.

### Procedure

- On the target SKU, record the live /memory ranges and reserved holes, then set a single memory node and payload.dram\_size for that SKU only.

### Development findings

- Inventing a dram\_size would silently exclude the other shipping SKUs. The skeleton records the variants and leaves a TODO.
- A conventional SM8250 DRAM base of 0x80000000 appears in other ports and in Linux board practice, but it is not written into this DTS as a measured dagu range.

### Completion criteria

- The ADT DRAM range matches the measured SKU, and reserved regions used at handoff are accounted for.

### Current limits

- No on-device memory map or firmware DTB memory node for dagu has been read in this work.

### Next action

- Measure the target unit's DRAM banks and reserved holes; do not copy elish or enuma sizes.

### Evidence

- `source`: [Documents Memory SKUs 128GB/6GB, 256GB/8GB and 512GB/12GB RAM.](https://github.com/Rinko-Studio/android_device_xiaomi_dagu/blob/66695faea165da63e7a8eac781ea2241df06a6dd/README.md)

## Storage and root {#storage}

`planned`

### Hardware and dependencies

- SoC UFS host ufshc@1d84000 and phy@1d87000 from UniXNU-sm8250-common dts/sm8250.dtsi, currently disabled until a storage component is selected.
- xiaomi-sm8250-common.dtsi enables &amp;ufsphy\_mem as qcom,ufs-phy-qmp-v4 and &amp;ufshc\_mem with regulator supplies. dagu-sm8250.dtsi adds only an hsg4\_synclength override.
- Userdata first\_lba, last\_lba and lba\_bytes are not filled. A published ArrowOS BOARD\_USERDATAIMAGE\_PARTITION\_SIZE of 114755874816 is a size, not GPT geometry, and storage SKUs differ.

### Configuration

- No ShengUfs or other storage component is selected.
- board.toml omits \[userdata\] rather than inventing LBA numbers. configs/dagu\_defconfig leaves CONFIG\_XNU\_NATIVE\_UFS unset.

### Procedure

- After an official unlock, read the userdata GPT entry and logical block size on the target unit and only then fill \[userdata\].
- Select a UFS component only after clocks, PHY, ICE, SMMU and LUNs for this board are inventoried.

### Development findings

- elish and enuma userdata LBA values must not be reused. Official porting rules require partition geometry from the target board.

### Completion criteria

- Host register, clock, link and SMMU facts match the dagu inventory, and OS/SystemOS windows stay within the measured userdata partition.

### Current limits

- No dagu GPT dump or on-device partition table is available in this skeleton.

### Next action

- Measure userdata first\_lba, last\_lba and lba\_bytes on the target SKU; do not copy another board.

### Evidence

- `source`: [UFS host 0x1d84000 and PHY 0x1d87000 documented at SoC scope.](https://github.com/FFT-infra/UniXNU-sm8250-common/blob/166235ec2480ff0992627b7aafa15c65ce6b4efa/dts/sm8250.dtsi)
- `source`: [dagu enables the common UFS nodes and only overrides hsg4\_synclength.](https://github.com/LineageOS/android_kernel_xiaomi_sm8250/blob/6b34d24765327d746074c8e53b5ad0d24a51acc7/arch/arm64/boot/dts/vendor/qcom/dagu-sm8250.dtsi)

## Display {#display}

`planned`

### Hardware and dependencies

- Panel dtsi dsi-panel-l81a-42-04-0a-video.dtsi: dual DSI DPHY video panel, 800 x 2560 per DSI \(1600 x 2560 total\), 120 Hz, 4 lanes, bpp 24, DSC 8 bpc / 8 bpp, HDR enabled.
- Backlight: two KTZ8866 I2C devices at address 0x11 on qupv3\_se11\_i2c and qupv3\_se9\_i2c, hwen GPIO tlmm 139.
- dagu-sm8250.dtsi sets &amp;sde\_dp &\#123; status = ok &\#125; and panel supplies enp/enn plus vddio L7A at 1.832 V.
- Rinko-Studio README describes an IPS LCD, 120 Hz, HDR10, Dolby Vision, 500 nits. Dolby Vision is not separately named in the opened panel timing node.

### Configuration

- No display or GOP component is selected. CONFIG\_XNU\_NATIVE\_MOBILE\_DISPLAY and CONFIG\_XNU\_NATIVE\_LEGACY\_DISPLAY are unset.
- Panel geometry and the L81A identifier are recorded in dts/dagu.dts comments for later wiring.

### Procedure

- Choose a handoff path \(inherit ABL framebuffer versus re-initialize DPU/DSI\) only after a firmware package can preserve or program the L81A panel.

### Development findings

- The 1600 x 2560 geometry is confirmed by both the panel timing \(800+800\) and Himax display-coords in dagu-sm8250.dtsi.
- DSC bit-per-component 8 matches an 8-bit panel pipeline in the opened timing node.

### Completion criteria

- A known frame appears with the documented 1600 x 2560 geometry and color format, and backlight control works.

### Current limits

- No framebuffer handoff, stride or pixel format has been measured on device. No display component is selected.

### Next action

- Confirm the live panel variant and stride from a firmware DTB or a future UEFI GOP log.

### Evidence

- `source`: [L81A dual DSI 800x2560@120Hz, bpp 24, DSC 8 bpc, HDR enabled.](https://github.com/LineageOS/android_kernel_xiaomi_sm8250/blob/6b34d24765327d746074c8e53b5ad0d24a51acc7/arch/arm64/boot/dts/vendor/qcom/dsi-panel-l81a-42-04-0a-video.dtsi)
- `source`: [KTZ8866 backlight at I2C 0x11, sde\_dp enabled, panel supplies and Himax 1600x2560 coords.](https://github.com/LineageOS/android_kernel_xiaomi_sm8250/blob/6b34d24765327d746074c8e53b5ad0d24a51acc7/arch/arm64/boot/dts/vendor/qcom/dagu-sm8250.dtsi)

## Input {#input}

`planned`

### Hardware and dependencies

- Primary touch node himax\_ts@0 on &amp;qupv3\_se4\_spi, compatible himax,hxcommon, 4 MHz, spi-cpha, IRQ tlmm 39, reset tlmm 100, coords 0 1600 0 2560.
- vendor/xiaomi/dagu.config enables CONFIG\_TOUCHSCREEN\_HIMAX\_IC\_HX83121 and also CONFIG\_TOUCHSCREEN\_NT36523\_HOSTDL\_SPI. No NT36523 node was found in the opened dagu dtsi.
- Keyboard dock: nanosic,803 at &amp;qupv3\_se2\_i2c address 0x4c, IRQ tlmm 83, reset tlmm 141.
- Volume up comes from the shared xiaomi-sm8250-common gpio\_keys \(pm8150 GPIO 6\). Hall sensors are on tlmm 110 and 121. Volume down and power key nodes were not found in the opened dagu dtsi.

### Configuration

- No touch or HID component is selected. Wiring is documented in dts/dagu.dts comments only.

### Procedure

- Confirm the touch IC actually present on the target unit before selecting a driver. Do not assume elish's NT36523 wiring.

### Development findings

- dagu's opened board DTS wires Himax on SE4 SPI, which is a different controller and bus setup from elish's Novatek NT36523 description. The extra NT36523 Kconfig flag is recorded as an unresolved SKU question, not as a second wired device.

### Completion criteria

- Touches map to the 1600 x 2560 panel, contacts keep stable IDs, and buttons produce expected HID reports.

### Current limits

- No touch firmware file name or hash is present in the opened DTS. Volume-down and power key locations remain TODO.

### Next action

- On the target unit, confirm the touch compatible string and firmware name; then decide whether a Himax or NT36523 driver applies.

### Evidence

- `source`: [Himax SPI touch and nanosic,803 keyboard nodes as cited in inputs.](https://github.com/LineageOS/android_kernel_xiaomi_sm8250/blob/6b34d24765327d746074c8e53b5ad0d24a51acc7/arch/arm64/boot/dts/vendor/qcom/dagu-sm8250.dtsi)
- `source`: [Enables Himax HX83121 and also NT36523\_HOSTDL\_SPI.](https://github.com/LineageOS/android_kernel_xiaomi_sm8250/blob/6b34d24765327d746074c8e53b5ad0d24a51acc7/arch/arm64/configs/vendor/xiaomi/dagu.config)

## GPU {#gpu}

`planned`

### Hardware and dependencies

- SoC include describes Adreno 650: gpu@3d00000 compatible qcom,adreno-650.2, gmu@3d6a000, gpu\_smmu@3da0000, all disabled until a GPU component with A650 scope is selected.
- soc/configs/sm8250.config leaves CONFIG\_XNU\_NATIVE\_ADRENO unset, noting that the A650 path is not provided by a catalog component yet.

### Configuration

- No Adreno or Metal component is selected in board.toml. dagu\_defconfig leaves CONFIG\_XNU\_NATIVE\_ADRENO unset.

### Procedure

- Reuse SoC-level A650 addresses from UniXNU-sm8250-common when a catalog component exists. Do not copy phone-board GPU policy from umi.

### Development findings

- Nearby SM8250 ports also leave native Adreno off at the skeleton stage. Firmware names and hashes are not yet listed.

### Completion criteria

- A selected A650 component completes submissions and presents a known image on this board.

### Current limits

- No dagu GPU firmware hash, vote or SMMU stream inventory beyond the SoC include is recorded.

### Next action

- Wait for an A650-capable catalog component, then list firmware members from a verified official package.

### Evidence

- `source`: [Adreno 650, GMU and SMMU register windows at SoC scope, disabled by default.](https://github.com/FFT-infra/UniXNU-sm8250-common/blob/166235ec2480ff0992627b7aafa15c65ce6b4efa/dts/sm8250.dtsi)

## Network {#network}

`planned`

### Hardware and dependencies

- Wi-Fi device in kona.dtsi: wlan: qcom,cnss-qca6390@b0000000, compatible qcom,cnss-qca6390, wlan-en GPIO tlmm 20.
- Bluetooth in xiaomi-sm8250-common.dtsi: bt\_qca6390, compatible qca,qca6390, reset GPIO tlmm 21, sw-ctrl GPIO tlmm 124.
- dagu-sm8250.dtsi overrides &amp;wlan and &amp;bluetooth regulator supplies \(pm8150\_s6 digital, pm8150\_s5 rfa1 at 2.0 V\).

### Configuration

- No Wi-Fi component is selected. Chip identity and board regulator overrides are recorded in dts/dagu.dts comments.

### Procedure

- List QCA6390 firmware members and hashes from a verified official package before selecting a network component.

### Development findings

- The wireless combo is QCA6390 \(CNSS + BT\) at SoC/family scope, with dagu-specific regulator overrides. This is a Wi-Fi-only board; see the cellular area.

### Completion criteria

- Scanning, association and sustained traffic pass with the selected QCA6390 firmware.

### Current limits

- No firmware file names or SHA-256 values are pinned. No association test has been run.

### Next action

- Import official QCA6390 firmware into .cache/firmware and record measured hashes.

### Evidence

- `source`: [dagu overrides &amp;wlan and &amp;bluetooth supplies for the QCA6390 combo.](https://github.com/LineageOS/android_kernel_xiaomi_sm8250/blob/6b34d24765327d746074c8e53b5ad0d24a51acc7/arch/arm64/boot/dts/vendor/qcom/dagu-sm8250.dtsi)

## cellular {#cellular}

`not-applicable`

### Hardware and dependencies

- This repository targets the China-region Wi-Fi model \(22081281AC\). There is no onboard cellular modem in scope.

### Configuration

- No modem, QRTR/QMI, SIM or IPA/QMAP component is selected, and none will be selected for this Wi-Fi model.

### Procedure

- Leave this area as not-applicable unless a different dagu SKU with a modem is explicitly targeted later.

### Development findings

- enuma is the 5G cousin in the same tablet family and is not this board. Cellular work belongs on enuma, not on this Wi-Fi dagu skeleton.

### Completion criteria

- The record continues to mark cellular as outside the scope of the Wi-Fi model.

### Current limits

- not-applicable: Wi-Fi-only China-region dagu \(22081281AC\) has no modem to bring up in this repository.

### Next action

- No cellular measurement is planned for this model.

### Evidence

- `source`: [Boards without a modem use not-applicable for the cellular area.](https://unixnu.com/porting/records)

## Audio {#audio}

`planned`

### Hardware and dependencies

- dagu-sm8250.dtsi describes four Cirrus CS35L41 amplifiers on I2C \(addresses 0x40, 0x41, 0x43 appear in the opened file\) and includes dagu-audio-overlay.dtsi.

### Configuration

- No DSP or audio component is selected. Amplifier compatible strings are recorded only as inventory.

### Procedure

- Inventory ADSP firmware and routes after the platform and display stages have a recorded baseline.

### Development findings

- Audio hardware is present in the stock DTS but has no UniXNU implementation in this skeleton.

### Completion criteria

- Each declared route carries the selected format through playback or capture.

### Current limits

- No codec clock, firmware or route map has been turned into board configuration yet.

### Next action

- Leave audio unselected until a driver with satisfied inputs is chosen from the catalog.

### Evidence

- `source`: [CS35L41 amplifier nodes and dagu-audio-overlay include are present in the stock board DTSI.](https://github.com/LineageOS/android_kernel_xiaomi_sm8250/blob/6b34d24765327d746074c8e53b5ad0d24a51acc7/arch/arm64/boot/dts/vendor/qcom/dagu-sm8250.dtsi)

## Power {#power}

`planned`

### Hardware and dependencies

- Rinko-Studio README: Li-Po 10000 mAh, non-removable battery.
- dagu.config enables QPNP SMB5 dagu, dual BQ27Z561 fuel gauge and BQ2597X charge-pump support.
- dagu-sm8250.dtsi sets mi,pd-power-max = &lt;67&gt; \(67 W\) on &amp;pm8150b\_pdphy.

### Configuration

- No battery or platform-power component is selected in this skeleton.

### Procedure

- Record regulator ownership and supported transitions after firmware handoff exists.

### Development findings

- The 10000 mAh figure comes from public device documentation, not from a fuel-gauge dump on the target unit.

### Completion criteria

- Declared power controls and battery readings match observations on this board.

### Current limits

- No on-device charge or capacity log is recorded here.

### Next action

- Leave power components unselected until a firmware package can report regulators and the fuel gauge.

### Evidence

- `source`: [Documents a non-removable Li-Po 10000 mAh battery.](https://github.com/Rinko-Studio/android_device_xiaomi_dagu/blob/66695faea165da63e7a8eac781ea2241df06a6dd/README.md)
- `source`: [Enables dagu SMB5, dual BQ27Z561 and BQ2597X charge-pump Kconfig.](https://github.com/LineageOS/android_kernel_xiaomi_sm8250/blob/6b34d24765327d746074c8e53b5ad0d24a51acc7/arch/arm64/configs/vendor/xiaomi/dagu.config)

## Image assembly {#packaging}

`planned`

### Hardware and dependencies

- OS profile ipados-17.7.11-21H461 supplies the IPSW URL, product iPad7,1, build 21H461 and prelink roots.
- scripts/package.sh is the official unmodified packaging script and reads \[package\] unixnu = ../UniXNU.
- This skeleton was produced on a Linux build box. Kernel and skip-setup steps that need Xcode or hdiutil require macOS or the official macOS GitHub runner.

### Configuration

- package.defconfig maps ipados-17.7.11-21H461 to dagu\_defconfig.
- payload.adt sets ipad\_identity and requires --unique-chip-id. root\_match\_volume\_uuid is unset until a userdata image exists.

### Procedure

- From UniXNU: ./unixnu defconfig dagu\_defconfig -D ../UniXNU-dagu &amp;&amp; ./unixnu fetch -D ../UniXNU-dagu.
- Do not run bootimg as a flashable release until DRAM, userdata, firmware and an official unlock are available.

### Development findings

- The official OS profile already pins the iPadOS 17.7.11 IPSW member hashes. This board does not duplicate them, and it does not select a 27-series profile.

### Completion criteria

- Kernel and prelink succeed for the iPadOS 17.7.11 profile, the payload contains the declared inputs, and the boot image matches a verified dagu bootloader contract.

### Current limits

- Linux hosts cannot run hdiutil or the iphoneos SDK path. A failed full image build on this box is not a repository-format failure.
- The official package.yml firmware checkout is blocked until uefi-dagu exists.

### Next action

- Resolve sources with unixnu fetch when network and the driver allow it; record host evidence only for commands that actually succeed.

### Evidence

- `source`: [Documents Linux versus macOS host limits and the official defconfig/fetch/status sequence.](https://unixnu.com/building)

## Diagnostics {#diagnostics}

`planned`

### Hardware and dependencies

- The official device-documentation workflow is retained and calls UniXNU/UniXNU/.github/workflows/porting-record.yml@main.
- Log transport, recovery commands and image revisions will be needed during bring-up; none have been captured from a dagu unit.

### Configuration

- No board-specific probe scripts are shipped in this skeleton beyond the official package.sh.

### Procedure

- Run python3 scripts/porting-record.py check --device ../UniXNU-dagu from the UniXNU checkout after record edits.
- Record the last confirmed checkpoint only from actual host or device logs.

### Development findings

- The bootloader is locked and official unlock is closed, so device evidence cannot be collected until that changes. This repository must stay a source skeleton until then.

### Completion criteria

- Each claimed milestone has a reproducible command, a full source revision and an accessible result.

### Current limits

- unixnu.lock was written by a successful fetch on this Linux host and is committed with the skeleton. There is still no device log and no bring-up checkpoint.

### Next action

- Enable and watch the Porting record workflow on the published default branch after the initial push.

### Evidence

- `source`: [Record schema, completion levels and the official checker command used to validate this file.](https://unixnu.com/porting/records)

</div>
