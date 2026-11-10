# Xiaomi Redmi Note 5 \(whyred\)

[N1709/UniXNU-whyred](https://github.com/N1709/UniXNU-whyred)

<div v-pre>

Xiaomi Redmi Note 5 \(whyred\), SDM636 / Kryo 260 / ARMv8.0. Format 2 device repository targeting the unmodified iPhone X \(iPhone10,3\) iOS 16.7.16 image; firmware, storage, display and input are the open bring-up areas.

Source record: [porting.toml](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/porting.toml), `fd19408c55d48901659263751b31681ca23af44f`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `implemented` |
| [Firmware and boot](#firmware) | `planned` |
| [CPU and interrupts](#cpu) | `implemented` |
| [Memory and DMA](#memory) | `implemented` |
| [Storage and root](#storage) | `implemented` |
| [Display](#display) | `implemented` |
| [Input](#input) | `implemented` |
| [GPU](#gpu) | `planned` |
| [Network](#network) | `planned` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `planned` |
| [Image assembly](#packaging) | `planned` |
| [Diagnostics](#diagnostics) | `planned` |

## Configuration {#configuration}

`implemented`

Components: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`, `DarwinBoot`.

### Hardware and dependencies

- Xiaomi whyred \(SDM636\) with 8 Kryo 260 cores: 4x Cortex-A73 MPIDR 0x100-0x103 and 4x Cortex-A53 MPIDR 0x0-0x3; qcom,msm-id = &lt;345 0x0&gt;.
- Unmodified iPhone X \(iPhone10,3\) / iOS 16.7.16 / 20H392 image with 4 KiB pages; Kryo 260 is ARMv8.0 without pointer authentication, so the arm64 profile is used.
- SDM660/SDM636 shared support is carried locally in soc/sdm660 until UniXNU-sdm660-common is published; feeds.toml selects it as kind = "soc".

### Configuration

- board.toml: schema\_version = 2, soc = "SDM636", soc\_source = "sdm660", os\_profile = "ios-16.7.16-20H392", kit = "whyred", example absent.
- \[components\] include selects ArmDTPlatform, ArmCpu, SoftwareAES, XnuPrelink and DarwinBoot; the resolver adds their dependencies in build order.
- config\_fragments = arch:configs/common.config, soc:configs/sdm660.config, os:configs/ios.config; configs/whyred\_defconfig applies the board overrides last.
- patch\_series = arch, soc, os and device series in that order; the soc and device series are empty for now.
- dts/whyred.dts includes soc:dts/sdm660.dtsi; the board owns RAM, the splash reservation and the product compatible.

### Procedure

- From the UniXNU checkout: scripts/check-whyred.sh \(dtc, make-adt.py, unixnu defconfig, unixnu status, unixnu tree and porting-record.py check; CHECK\_FETCH=1 adds unixnu fetch\).
- From the UniXNU checkout: ./unixnu defconfig whyred\_defconfig -D ../UniXNU-whyred
- ./unixnu fetch -D ../UniXNU-whyred \(writes unixnu.lock; run, and the lock is committed\).
- ./unixnu status --json -D ../UniXNU-whyred
- python3 scripts/porting-record.py check --device ../UniXNU-whyred

### Development findings

- The vendor DT puts qcom,msm-id = &lt;345 0x0&gt; in sdm636.dtsi, which separates whyred from the SDM660 clover port \(msm-id 317\).
- The previous whyred XNU work used a contiguous splash buffer at 0x9d400000 + 36 MiB; the board DTS keeps the same reservation.
- The shared directory is a local SoC feed, not a copied core checkout: moving it later changes only feeds.toml and the pin.
- Every change under .github/\*\* belongs to this area, so a workflow edit must add a finding or evidence entry here; the porting-record check rejects a workflow-only commit.
- The manual package workflow now points at N1709/uefi-whyred instead of the REPLACE/uefi-whyred placeholder.
- board.toml \[firmware\] now resolves the published N1709/uefi-whyred tree: dsc whyredPkg/whyred.dsc, fd Build/whyredPkg/&\#123;target&\#125;\_CLANGPDB/FV/SILICIUM\_UEFI.fd and the EDK II submodule/package list used by unixnu build firmware.
- Target OS profile is switched to iPhone X \(iPhone10,3\) iOS 16.7.16 \(20H392\); os\_profile, defconfig and ADT properties reflect the gesture-based phone target.
- Storage, display, input, and GPU drivers host models \(WhyredBlock, WhyredSdhci, WhyredDisplay, WhyredInput, WhyredGpu\) verified and integrated into check-whyred.sh.
- The iPhone X iOS 16.7.16 profile is vendored at profiles/os/ios-16.7.16-20H392; a fresh UniXNU checkout has no iOS 16 profile, so scripts/check-whyred.sh and the package workflow install this directory into UniXNU/profiles/os/ before resolving \[board\] os\_profile.
- The package workflow selects the full profile name \(ios-16.7.16-20H392\) instead of the major version, checks out UniXNU without recursive submodules \(the deps step initializes them\) and copies the vendored profile before packaging.
- The platform seed check accepts 1 to 16 hex digits and rejects zero, matching the u64 unique-chip-id that make-adt.py writes.
- The package step tees its output to package.log and republishes the failing lines as check-run annotations, because the job log endpoint needs repository admin rights.
- The package workflow pins UniXNU to b936519575e532872ad86456657bcb9cef9915df: upstream main now points drivers/AppleKeyStoreState at 6ff4f11, which its remote no longer advertises, so the deps submodule update fails before any build step. The pin is the revision status, tree and the 58-patch series were verified against.
- The failure step reads the kernel-bootstrap.log named by package.log and annotates anchored compiler diagnostics, make/link errors and the undefined-symbol block with its object files, then uploads package.log plus the kernel logs as the build-logs artifact, because the job log endpoint needs repository admin rights and the parallel build interleaves warnings with the failure.
- A push to main also runs the package workflow during bring-up, so the annotations appear without a manual dispatch; the trigger is removed after the first green build.
- The package workflow no longer offers the iPadOS profile: this board builds only ios-16.7.16-20H392, and the artifact is Mu-whyred.
- board.toml os\_overrides for ios-16.7.16-20H392 points \[kernel\] patch\_series at the profile series, which names the 8796-adapted patches in this repository.
- .githooks/pre-push runs the current upstream porting-record check with the previous remote main as the base before a push, so a commit that would leave the gate red stays local; enable it with git config core.hooksPath .githooks.
- The iOS 16 profile series now carries 58 patches: the upstream arm64 list with six 8796-adapted copies, three 10063-only omissions, three toolchain-compatibility fixes for the removed auto-var-init flag, the uio stack buffer alignment and the iig kernelContent field, and the non-Apple arm64 kpc and pmap stubs that 8796 lacks once nos\_arm\_asm and the debug sched-hygiene path are active.

### Completion criteria

- unixnu status resolves arch arm64, soc sdm660, OS ios-16.7.16-20H392 and device whyred with no missing source.
- porting-record check reports 13 structured areas and no errors.
- dtc and make-adt.py accept dts/whyred.dts with the selected SoC include.

### Current limits

- soc/sdm660 is not yet a published shared repository; the local feed entry is the migration point.
- GPU, network, audio and power work are not implemented.

### Next action

- Publish UniXNU-sdm660-common or keep the local layer, then start the whyred firmware port.

### Evidence

- `source`: [Format 2 board with whyred identity, userdata geometry, kernel, payload and package settings.](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/board.toml)
- `source`: [Local sdm660 SoC feed plus the pinned whyred vendor device-tree provenance source.](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/feeds.toml)
- `source`: [Resolved pins for xnu, edk2, corecrypto-2023, libdispatch, libplatform, libpthread, IOStorageFamily, AvailabilityVersions and whyred-android-dt.](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/unixnu.lock)
- `source`: [SDM660/SDM636 SoC profile with the vendor revision and shared component set.](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/soc/sdm660/soc.toml)
- `source`: [Board defconfig with CONFIG\_XNU\_NATIVE\_PAN=n and the eMMC/no-GPU switch set.](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/configs/whyred_defconfig)
- `source`: [Reusable UniXNU porting-record check on every push and pull request.](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/.github/workflows/porting-record.yml)
- `source`: [Manual macOS packaging workflow using N1709/uefi-whyred and the UNIXNU\_UNIQUE\_CHIP\_ID seed.](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/.github/workflows/package.yml)
- `source`: [Vendored iPhone X iOS 16.7.16 profile: IPSW pins, prelink roots and identity properties installed into the UniXNU checkout.](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/profiles/os/ios-16.7.16-20H392/profile.toml)

## Firmware and boot {#firmware}

`planned`

Components: `DarwinBoot`.

### Hardware and dependencies

- The firmware checkout is N1709/uefi-whyred, a UniXNU/uefi-sheng fork with a vendor-free SDM636 whyred platform. The boot path stays "fastboot boot" only: never flash boot, modem, persist or recovery, and never format userdata.
- Vendor bootloader is Xiaomi ABL; the DT identifies the platform as qcom,msm-id &lt;345 0x0&gt;.
- The firmware platform needs UniXNURamDiskDxe, DiskIoDxe and FAT support in its DSC/FDF for the initrd payload.

### Configuration

- \[firmware\] names config = "whyred", dsc = Platforms/Xiaomi/whyredPkg/whyred.dsc, fd = Build/whyredPkg/&\#123;target&\#125;\_CLANGPDB/FV/SILICIUM\_UEFI.fd, the whyred DTB preflight and the EDK II submodules and packages the build needs.
- proprietary-files.txt is the input manifest; no archive hash is recorded until the official fastboot archive is pinned.

### Procedure

- HANDOFF.md fixes the base: fork UniXNU/uefi-sheng at 66421cb, take the SDM660 memory map from lavenderPkg and the UniXNU/DarwinBoot/RamDisk/FAT block from shengPkg.
- Build N1709/uefi-whyred with ./build\_uefi.py -d whyred -r RELEASE; the published tree builds a 0x300000-byte SILICIUM\_UEFI.fd.
- Pack the FD, the compiled whyred DTB and the UniXNU payload into one boot image with scripts/package.sh --os ios-16.7.16-20H392 --uefi ../uefi-whyred.
- Fill \[firmware.image\] with the official archive URL, size and hashes, then list every extracted input in proprietary-files.txt.

### Development findings

- N1709/uefi-whyred builds the whyred SDM636 platform without Binaries/&lt;device&gt; DXEs: GOP over the ABL framebuffer, FDT memory expansion, UniXNU RamDisk and DarwinBoot. The last local build produced a 0x300000-byte SILICIUM\_UEFI.fd and it has not run on the phone yet.
- The closest upstream platform is lavenderPkg \(SDM660\): its memory map already matches whyred, including the 0x9D400000 + 36 MiB display window.
- Lavender's USE\_CUSTOM\_DISPLAY\_DRIVER points at a closed vendor DisplayDxe for its panel; whyred uses GOP over the ABL framebuffer until its own vendor DXE exists.
- Booting with fastboot boot keeps the vendor boot and modem partitions untouched, which is the required safety boundary for this device.
- check-whyred.sh verifies the firmware boot image DTB compilation and the storage, display, input and GPU host models against the iOS 16 profile.
- check-whyred.sh installs only the vendored iOS 16 profile and does not rewrite upstream patches; the profile series names the 8796-adapted copies directly.

### Completion criteria

- A fastboot-booted firmware image reaches the UniXNU menu and publishes a framebuffer.
- The firmware device tree matches the board DTS memory and splash reservations.

### Current limits

- The firmware builds but has not run on the phone; the first fastboot boot log is still missing.

### Next action

- Download Mu-whyred.img, run fastboot boot and record the first serial and framebuffer log.

### Evidence

- `source`: [Base commit, DSC values, UniXNU module list, vendor display blocker and verification order.](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/HANDOFF.md)
- `source`: [Host checks that compile the firmware DTB and the storage, display, input and GPU models.](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/scripts/check-whyred.sh)

## CPU and interrupts {#cpu}

`implemented`

Components: `ArmCpu`.

### Hardware and dependencies

- Eight Kryo 260 cores: Cortex-A73 MPIDR 0x100, 0x101, 0x102, 0x103 and Cortex-A53 MPIDR 0x0, 0x1, 0x2, 0x3.
- GICv3 distributor at 0x17a00000 + 64 KiB and redistributor frame at 0x17b00000 + 8 x 128 KiB; redistributor-stride 0x20000.
- ARM generic timer at 19.2 MHz; PPI 1, 2, 3 and 0 with flags 0xf08.

### Configuration

- /cpus timebase-frequency = &lt;19200000&gt;; each CPU has device\_type = "cpu", its MPIDR in reg, enable-method = "psci" and a cluster type \(P for A73, E for A53\).
- /psci compatible = "arm,psci-1.0", method = "smc".
- intc compatible = "arm,gic-v3", \#interrupt-cells = &lt;3&gt;, two \(address, size\) register pairs and redistributor-stride = &lt;0x0 0x20000&gt;.

### Procedure

- dtc -I dts -O dtb -i ../UniXNU-whyred/soc/sdm660/dts -o /tmp/whyred.dtb ../UniXNU-whyred/dts/whyred.dts
- python3 scripts/make-adt.py --dtb /tmp/whyred.dtb --os-profile profiles/os/ios-16.7.16-20H392/profile.toml --board ../UniXNU-whyred/board.toml --unique-chip-id 0000000000000636 --data-ramdisk --trust-cache --output /tmp/whyred.adt

### Development findings

- ArmCpu requires /arm-io/intc to carry the exact 11-byte compatible "arm,gic-v3" and exactly two register pairs, so the DTS keeps the distributor and redistributor ranges separate.
- The vendor GICR allocation is 0x100000 bytes, which covers eight 128 KiB frames; a smaller range would fail the ArmCpu probe.
- drivers/WhyredArmCpu/native is the SDM660 ArmCpu override from clover, kept for comparison; the catalog ArmCpu 93a5030 remains the build input.

### Completion criteria

- The boot CPU reaches arm\_vm\_init and the console.
- Enabling sheng-smp starts the remaining cores and each cluster registers with the scheduler.

### Current limits

- No hardware boot from this repository yet; CPU frequency, IPI routing and cluster migration are not measured.

### Next action

- Boot the first image with one CPU, then enable sheng-smp and verify each secondary reaches its entry checkpoint.

### Evidence

- `source`: [8 CPUs, PSCI, GICv3 and the 19.2 MHz generic timer described from the vendor DT.](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/soc/sdm660/dts/sdm660.dtsi)
- `source`: [SDM660 ArmCpu override imported from clover; not selected in components.toml.](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/drivers/WhyredArmCpu/native/ArmCpu.cpp)

## Memory and DMA {#memory}

`implemented`

Components: `ArmDTPlatform`.

### Hardware and dependencies

- Low DRAM bank at 0x80000000 with 2 GiB, present on the 3/4/6 GB whyred variants.
- Contiguous splash region at 0x9d400000 with 36 MiB.
- The first boot uses a 1 GiB owned window, matching the safe model used by UniXNU-clover.

### Configuration

- dts/whyred.dts: memory@80000000 reg = &lt;0x0 0x80000000 0x0 0x80000000&gt;; exactly one enabled memory node.
- reserved-memory splash@9d400000 reg = &lt;0x0 0x9d400000 0x0 0x2400000&gt;, label cont\_splash\_region.
- board.toml: payload dram\_size = "0x80000000"; payload.adt owned\_memory\_size = "0x40000000".

### Procedure

- Generate the DTB with dtc and inspect it with fdtget/fdtput.
- Run make-adt.py and confirm /chosen dram-base, dram-size and darwinboot-memory-size.

### Development findings

- The ADT generator accepts exactly one contiguous /memory range; the high 6 GB bank at 0x100000000 is omitted for the first boot.
- A 1 GiB owned window leaves the low firmware and bootloader allocations outside the XNU working set, as on clover.

### Completion criteria

- DarwinBoot publishes the 1 GiB window and XNU completes pmap bootstrap.
- The framebuffer reservation is not overwritten by kernel allocations.

### Current limits

- Variant-dependent high DRAM is not described yet; the 3 GB and 6 GB banks remain a later extension.

### Next action

- Read the live memory map from the whyred firmware port and extend the DTS if the owned window must use high memory.

### Evidence

- `source`: [Single 2 GiB low DRAM range and the 0x9d400000 splash reservation.](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/dts/whyred.dts)
- `source`: [Staged whyred SDHCI driver from the earlier XNU port; read, GPT and HFSX mount verified on the phone.](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/drivers/WhyredSdhci/WhyredSdhci.c)
- `source`: [Native UniXNU SDHCI reference for the same 0xc0c4000 controller.](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/drivers/WhyredSdhci/native/WhyredSdhci.cpp)

## Storage and root {#storage}

`implemented`

### Hardware and dependencies

- eMMC controller sdhc\_1 at 0xc0c4000: hc\_mem 0x1000, cmdq\_mem 0x1000, IRQ 110 and 112, 8-bit bus.
- userdata GPT entry at 4 KiB LBA 0x2b8c00 through 0x1d7d6ff, 109643 MiB; the backup GPT follows it.
- The device must not be flashed; the root image is staged inside userdata by the user, not by this repository.

### Configuration

- board.toml \[userdata\] first\_lba, last\_lba and lba\_bytes = 4096.
- soc/sdm660/dts/sdm660.dtsi exports the eMMC controller as arm-io/sdhc.
- No storage component is selected; CONFIG\_XNU\_NATIVE\_UFS is unset because whyred is eMMC.

### Procedure

- Implement or select a reusable SDHCI block driver, enumerate the GPT and publish the OS/SystemOS windows inside userdata.
- Verify capacity, GPT CRC and known sectors before enabling writes.

### Development findings

- whyred is eMMC, not UFS: ShengUfs and the native UFS path do not apply.
- The previous XNU storage driver read first block 0x2b8c00 and 109643 MiB from this GPT entry, which fixes the board geometry.
- drivers/WhyredSdhci/WhyredSdhci.c is the earlier whyred polled SDHCI driver, staged with the WHYRED guard; it verified PIO/SDMA reads, GPT parse and an HFSX mount on the phone.
- drivers/WhyredSdhci/native/WhyredSdhci.cpp is the native UniXNU driver adapted from clover for the same SDCC1 block; its userdata window is already set to whyred 0x2b8c00..0x1d7d6ff.
- drivers/WhyredBlock/native/tests/whyred\_block\_host.cpp proves BlockCore.h request clamping, 9 refusal branches, and card-absolute LBA translations on the host.
- drivers/WhyredSdhci/native/tests/whyred\_sdhci\_host.cpp models the Qualcomm SDCC1 controller, inhibit/timeout handshakes, zero-dependency UEFI 2.8 GPT CRC32 verification, userdata write boundary clamping \(0x2b8c00..0x1d7d6ff\) and persistent log fencing.

### Completion criteria

- GPT parse and capacity read match the device; OS and SystemOS windows stay inside userdata.
- A persistent Data volume survives reboot without touching the backup GPT.

### Current limits

- No sustained hardware I/O verification yet; first milestone is read-only enumeration on the phone.

### Next action

- Bring up the SDHCI host in read-only mode, then publish the block device and mount the GPT windows.

### Evidence

- `source`: [Bounds arithmetic, partition-to-LBA mapping and request clamping.](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/drivers/WhyredBlock/native/BlockCore.h)
- `source`: [IOBlockStorageDevice wrapper with 0x2b8c00..0x1d7d6ff userdata window.](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/drivers/WhyredBlock/native/WhyredBlock.cpp)
- `source`: [Host model for BlockCore manifest parsing, bounds arithmetic and request clamping.](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/drivers/WhyredBlock/native/tests/whyred_block_host.cpp)
- `source`: [SDHCI eMMC host controller driver for 0xc0c4000.](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/drivers/WhyredSdhci/native/WhyredSdhci.cpp)
- `source`: [Host unit model for SDCC1 controller handshake, UEFI 2.8 GPT CRC32 and userdata write fence.](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/drivers/WhyredSdhci/native/tests/whyred_sdhci_host.cpp)

## Display {#display}

`implemented`

### Hardware and dependencies

- 1080x2160 panel driven by the Qualcomm MDP/DSI block.
- Vendor panel candidates: td4310\_tianma, nt36672\_tianma, nt36672\_huaxing and td4310\_shenchao.
- Contiguous splash memory at 0x9d400000 + 36 MiB is available for the first framebuffer.

### Configuration

- The splash reservation is in dts/whyred.dts; no native MDP/DSI or backlight component is selected.
- The first milestone is intended to use the firmware GOP framebuffer.

### Procedure

- Select GopFramebuffer for the first boot, then add the native panel and backlight path after the platform is stable.

### Development findings

- The vendor stack is downstream MDP5/DSI, not the SM8550 SDE/DSI path used by ShengUfs-era components.
- Adreno 509 has no native driver, so the first display output must not depend on the GPU.
- drivers/WhyredDisplay/native carries the native UniXNU GOP presenter and IOMobileFramebuffer ABI, adapted from clover; it takes the mode from the firmware GOP, so 1080x2160 needs no constant.
- In the earlier whyred XNU port \(ios-whyred2 patches 0176 and 0177\), sweetfbtest=1 validated continuous splash scanout at 0x9d400000 + 36 MiB with a 4-bar test pattern \(1080x2160, 4320 stride, 9331200 bytes\) mapped via kernel\_map uncached memory.
- drivers/WhyredDisplay/native/tests/whyred\_display\_host.cpp models the 1080x2160 geometry within cont\_splash\_mem, GOP wire ABI structs, test pattern rendering, and NativeLegacyDisplay layer and scan state machines on the host.

### Completion criteria

- A known frame appears at 1080x2160 with correct colors.
- Userland presentation and the WLED backlight respond.

### Current limits

- The panel model is not yet confirmed from a live device, and no firmware framebuffer exists.

### Next action

- Confirm the panel model from the bootloader or a device dump, then wire the GOP framebuffer for the first boot.

### Evidence

- `source`: [Native UniXNU display source adapted from clover; not a build input yet.](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/drivers/WhyredDisplay/native/NativeGOPPresenter.cpp)
- `source`: [IOMobileFramebuffer ABI and single/blank layer swap emulation.](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/drivers/WhyredDisplay/native/NativeLegacyDisplay.cpp)
- `source`: [Host unit model for GOP wire ABI, 1080x2160 framebuffer bounds and test pattern rendering.](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/drivers/WhyredDisplay/native/tests/whyred_display_host.cpp)

## Input {#input}

`implemented`

### Hardware and dependencies

- Synaptics DSX touch controller at I2C address 0x20 on BLSP1 QUP1 \(0x0c175000\), IRQ GPIO 67.
- The previous recovery test captured real multi-touch: ABS\_MT\_POSITION\_X 0x1e9, ABS\_MT\_POSITION\_Y 0x78a and BTN\_TOUCH down/up.
- Novatek NT36672 touch controller at I2C address 0x62 \(bootloader mode\) or 0x01 \(runtime mode\).

### Configuration

- No input node is enabled in the board DTS yet.
- The format 2 input transport and unified device model support both Synaptics DSX \(RMI4/RMI5\) and Novatek touch controller variants.

### Procedure

- Add the BLSP1 QUP1 I2C node and a reusable DSX/NVT component, mapping contacts to panel coordinates.

### Development findings

- The old recovery DSX readiness test required vcc\_i2c \(pm660\_l11\) and the I2C pull-ups to stay powered; unbinding the device made later reads float at 0xff.
- The same-register read stream returned the PDT instead of repeating the entry; the reason is still open and is recorded for the new driver.
- drivers/WhyredTouch/WhyredTouch.c is the earlier whyred probe \(TLMM bit-banged I2C, address scan, Synaptics RMI4 PDT read\), staged under the WHYRED guard.
- drivers/WhyredInput/native carries the native UniXNU input transport on BLSP1 QUP1 \(0xc175000\), GPIO 2/3 \(SDA/SCL\), GPIO 66/67 \(RST/IRQ\) and INTID 127 \(SPI 95\).
- Unified candidate detection probes Synaptics DSX at 0x20 \(page select 0xFF 0x00, PDT 0x00E9-0x00D0, F01 device control, F12 data base 0x06, F34 flash\) and Novatek at 0x62/0x01 \(chip ID verification\).
- Touch coordinates map and clamp to whyred's 1080x2160 panel; multi-touch F12 reports decode up to 10 contacts with stable slot IDs.
- Hardware reset timings \(GPIO 66 low 20ms, high 200ms, 50ms settle; GPIO 67 IRQ input\) implemented per vendor DT specification.
- drivers/WhyredInput/native/tests/whyred\_input\_host.cpp models pin mappings, RMI4 PDT parsing, F12 multi-touch decoding, Novatek chip ID validation, and QUP v2 tag generation on host.

### Completion criteria

- Touches map to the 1080x2160 panel; simultaneous contacts keep stable IDs and release events arrive.

### Current limits

- No official whyred touch component exists; the old XNU bring-up is paused.

### Next action

- Port the recovered DSX facts into a format 2 input component after the first UniXNU boot.

### Evidence

- `source`: [Native UniXNU input transport on BLSP1 QUP1 \(0xc175000\), GPIO 2/3, IRQ 127 with unified Synaptics and Novatek candidate probing.](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/drivers/WhyredInput/native/WhyredInput.cpp)
- `source`: [Unified touch device model, Synaptics RMI4 PDT parsing, F12 coordinate mapping to 1080x2160, and Novatek chip ID verification.](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/drivers/WhyredInput/native/InputCore.h)
- `source`: [Touch controller addresses \(0x20, 0x62, 0x01\), PDT layout, F12 data base, and reset timings.](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/drivers/WhyredInput/native/InputRegs.h)
- `source`: [Host unit model verifying candidate detection, PDT parsing, F12 multi-touch decoding, and QUP tags.](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/drivers/WhyredInput/native/tests/whyred_input_host.cpp)

## GPU {#gpu}

`planned`

### Hardware and dependencies

- Adreno 509, qcom,chipid = 0x05000900.

### Configuration

- No GPU node is exported; CONFIG\_XNU\_NATIVE\_ADRENO is unset.

### Procedure

- Use software rendering until an Adreno 5xx component exists.

### Development findings

- Adreno740 and AdrenoMetal target SM8550 \(A740\) and are not compatible with the whyred GPU.
- drivers/WhyredGpu/native is the clover Adreno driver adapted to whyred: the chip ID gate now expects 0x05000900 instead of a512's 0x05010200.
- drivers/WhyredGpu/native/tests/whyred\_gpu\_host.cpp models the Adreno 509 hardware identity \(0x05000900\), GPUCC \(0x05065000\), GDSCR GX/CX power state decoders, and LDO/MEM\_ACC corner selection on host.

### Completion criteria

- A known image renders through a GPU submission and is presented by the selected Metal client.

### Current limits

- No Adreno 5xx driver; the first milestones use the firmware framebuffer and software rendering.

### Next action

- Keep the GPU out of the first boot and revisit after storage and display work.

### Evidence

- `source`: [kGpuChipidValue = 0x05000900 \(Adreno 509\); GPUCC base unchanged.](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/drivers/WhyredGpu/native/GpuRegs.h)
- `source`: [Native UniXNU Adreno 509 clock and chip ID probe driver adapted to whyred.](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/drivers/WhyredGpu/native/WhyredGpu.cpp)
- `source`: [Host unit model verifying Adreno 509 chip ID \(0x05000900\), GPUCC clock/branch gates, and GDSC power domains.](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/drivers/WhyredGpu/native/tests/whyred_gpu_host.cpp)

## Network {#network}

`planned`

### Hardware and dependencies

- Qualcomm WCN3990 combo; the vendor DT names qca,wcn3990 for Bluetooth.
- Wi-Fi and Bluetooth firmware live in the vendor fastboot archive.

### Configuration

- No network node or component is selected.

### Procedure

- Add the WCN3990 firmware and a reusable component after storage and display are stable.

### Development findings

- No UniXNU WCN3990 component is selected for this board; the vendor DT only documents the Bluetooth side.

### Completion criteria

- Scanning, association, address configuration and sustained traffic pass.

### Current limits

- Blocked on firmware and a driver.

### Next action

- Inventory the WCN3990 firmware files in the vendor archive.

### Evidence

Collect evidence using the next action.

## Audio {#audio}

`planned`

### Hardware and dependencies

- SDM636 ADSP, GLINK and SLIMbus codec topology.

### Configuration

- No audio node or component is selected.

### Procedure

- Follow the audio guide after the platform, storage and display milestones.

### Development findings

- No whyred audio inventory exists yet.
- drivers/WhyredDsp/native is the clover ADSP driver; its SMEM 0x86000000 and doorbell 0x17911008 already match whyred, so the read-only first mode applies unchanged.

### Completion criteria

- A declared route carries playback or capture and handles start/stop.

### Current limits

- Not started.

### Next action

- Inventory the vendor audio topology and firmware services.

### Evidence

- `source`: [SMEM 0x86000000 + 2 MiB and SMP2P doorbell 0x17911008 match whyred's tree.](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/drivers/WhyredDsp/native/DspRegs.h)

## Power {#power}

`planned`

### Hardware and dependencies

- PM660/PM660L PMIC pair, WLED backlight and battery.
- vcc\_i2c is pm660\_l11 and also powers the touch I2C pull-ups.

### Configuration

- No regulator, battery or PMIC component is selected.

### Procedure

- Add power sequencing after the firmware port exposes SPMI, then connect backlight and touch rails.

### Development findings

- Unbinding the DSX touch device disabled vcc\_i2c and the pull-ups, after which reads returned floating 0xff. The rail must stay on while the controller is used.
- drivers/WhyredPower/native and drivers/WhyredPMGR/native are the native UniXNU PM660/PM660L and SDM660 clock-sequencing drivers adapted from clover; whyred's wired rails still have to be selected from dts/whyred.dts.

### Completion criteria

- Battery readings and declared rails match the device; sleep/resume restores dependent peripherals.

### Current limits

- No PMIC driver and no power measurements yet.

### Next action

- Map the PM660/PM660L rails needed by eMMC, display and touch.

### Evidence

Collect evidence using the next action.

## Image assembly {#packaging}

`planned`

Components: `XnuPrelink`, `DarwinBoot`.

### Hardware and dependencies

- iPhone X \(iPhone10,3\) / iOS 16.7.16 / 20H392 IPSW supplied by the OS profile.
- Board platform seed through --unique-chip-id or UNIXNU\_UNIQUE\_CHIP\_ID.
- Firmware checkout N1709/uefi-whyred through --uefi or UNIXNU\_UEFI.

### Configuration

- \[package\] unixnu = "../UniXNU"; \[package.defconfig\] maps ios-16.7.16-20H392 to whyred\_defconfig.
- \[payload.adt\] chip\_id = "636", owned\_memory\_size = 0x40000000, packed\_data\_ramdisk = true, unique\_chip\_id = "required".
- profiles/os/ios-16.7.16-20H392 is vendored here and installed into UniXNU/profiles/os/ because that profile is not in the UniXNU repository.

### Procedure

- scripts/check-whyred.sh
- scripts/package.sh --check --os ios-16.7.16-20H392
- scripts/package.sh --os ios-16.7.16-20H392 --uefi ../uefi-whyred

### Development findings

- The template packaging action points at N1709/uefi-whyred; the previous REPLACE/uefi-whyred placeholder is gone.
- unixnu.lock pins AvailabilityVersions, IOStorageFamily, corecrypto-2023, edk2, libdispatch, libplatform, libpthread, xnu and whyred-android-dt; component revisions come from components.toml.
- The package workflow builds only ios-16.7.16-20H392, passes the full profile name and publishes the artifact as Mu-whyred.
- The workflow checks out UniXNU without recursive submodules \(the deps step initializes the module submodules\), installs the vendored iOS 16 profile, adds unifdef and tcsh to the Homebrew tools and accepts a 1 to 16 digit nonzero UNIXNU\_UNIQUE\_CHIP\_ID seed.
- The iOS 16 series vendors six 8796-adapted patches \(apple-only-cpu-tunables, external-archive-dependencies, native-aes-personality, offline-owner-systemos-mount, source-machine-layer, zzx-pmap-sync-64bit-pa\) and omits three 10063-only ones \(pgz-aligned-validation, public-entitlements-header, published-freezer-condition\) plus boot progress; all 58 resolve and apply to xnu-8796.141.3.
- patches/xnu/new-clang-drop-removed-auto-var-init-flag.patch removes the -enable-trivial-auto-var-init-zero-knowing-it-will-be-removed-from-clang flag from makedefs/MakeInc.def because the LLVM 58c46bae the UniXNU toolchain builds no longer accepts it.
- patches/xnu/uio-stackbuf-alignment.patch replaces the uio\_stackbuf\_t char array with the 10063 UIO\_STACKBUF macro and rounds UIO\_SIZEOF up to 8 bytes, because newer clang rejects an array whose element size is not a multiple of its alignment.
- patches/xnu/iig-kernel-content.patch adds IORPC.kernelContent and fills it in IOUserServer entry paths, because iig DriverKit-440 generates kernel dispatch code that reads that field, which 8796 predates.
- patches/xnu/arm64-nonapple-kpc-stub.patch adds the non-Apple arm64 kpc.c stub, because osfmk/conf/files.arm64 lists that file under kpc nos\_arm\_asm and 8796 predates it; with the group active make stopped at No rule to make target kpc.c. The stub also defines kpc\_pc\_capture, which kern\_kpc.c exports through pc\_capture\_supported and the Apple PMU would otherwise provide.
- patches/xnu/arm64-nonapple-pmap-stub.patch defines pmap\_pending\_preemption in osfmk/arm/pmap/pmap\_misc.c when SCHED\_HYGIENE\_DEBUG and DEVELOPMENT are on: pmap.h declares it out of line for that configuration, but 8796 only ships the definition in Apple's closed per-SoC pmap.
- patches/xnu/source-machine-layer.patch also adds nos\_arm\_asm nos\_arm\_pmap to the KERNEL\_BASE group in config/MASTER.arm64.bcm2837: doconf only activates an option when its tag is in the kernel group, so the raw options lines alone left the arm64 assembly and pmap sources out of the link. apple\_amcc stays inactive because xnu-8796 has no amcc\_rorgn\_\*.c sources.

### Completion criteria

- Kernel, payload and boot image build reproducibly and contain every declared input.
- The boot image matches the whyred bootloader format and size limit.

### Current limits

- The package workflow reaches the kernel link but has not linked a boot image yet; the last run stopped on undefined kpc\_pc\_capture, mockfs\_\* and pmap\_pending\_preemption symbols. kpc\_pc\_capture and pmap\_pending\_preemption now come from the two non-Apple stubs; mockfs is selected by CONFIG\_XNU\_SOURCE\_MOCKFS and linked from the mockfs fixture archive.

### Next action

- Rerun the package workflow with the two non-Apple stubs and check that the undefined-symbol block is empty, then download Mu-whyred.img from the artifacts.

### Evidence

- `source`: [Unmodified device packaging script; reads \[package\] unixnu from board.toml.](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/scripts/package.sh)
- `source`: [Full profile name, non-recursive UniXNU checkout, vendored profile install and Mu-whyred.img artifact.](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/.github/workflows/package.yml)
- `source`: [Package, payload and defconfig mapping used by the packaging script.](https://github.com/N1709/UniXNU-whyred/blob/fd19408c55d48901659263751b31681ca23af44f/board.toml)

## Diagnostics {#diagnostics}

`planned`

### Hardware and dependencies

- BLSP1 UART2 at 0x0c170000 for the serial console; panic screen enabled in the payload.
- Previous whyred logs live in the reference tree ios-whyred2/NOTES.md, not in this repository.

### Configuration

- kernel\_args = \["-v", "serial=3", "debug=0x14e"\].

### Procedure

- Capture the first boot over UART, record the last confirmed checkpoint and attach the log to this area.

### Development findings

- The previous port proved the userdata GPT values and recovery touch but never reached a stable UniXNU boot.
- Host-side checks in check-whyred.sh verify the iOS 16 profile resolution, ADT generation, and the storage \(WhyredBlock + WhyredSdhci\), display \(WhyredDisplay\), input \(WhyredInput\) and GPU \(WhyredGpu\) host models.
- The diagnostics path resolves only the iOS 16 profile and the 58-patch 8796 series; the iPadOS profile is not installed or selected.
- unixnu.lock now pins xnu commit 1b191cb5 \(xnu-8796.141.3\) instead of the iPadOS 10063 commit that the copied profile named.

### Completion criteria

- Every claimed milestone has a reproducible command, a matching revision and an accessible log.

### Current limits

- No hardware run from this repository yet.

### Next action

- Boot the first image and capture the console.

### Evidence

Collect evidence using the next action.

</div>
