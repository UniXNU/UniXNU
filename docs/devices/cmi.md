# Xiaomi Mi 10 Pro \(cmi\) / SM8250

[wangjiaxue001/UniXNU-cmi](https://github.com/wangjiaxue001/UniXNU-cmi)

<div v-pre>

Xiaomi Mi 10 Pro \(cmi\), SM8250, 8 GB SKU. Host-side static checks only; no build and no device boot yet.

Source record: [porting.toml](https://github.com/wangjiaxue001/UniXNU-cmi/blob/4c200b18498ac6ab31500a8e0588ebfbb70aef43/porting.toml), `4c200b18498ac6ab31500a8e0588ebfbb70aef43`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `planned` |
| [Firmware and boot](#firmware) | `host-verified` |
| [CPU and interrupts](#cpu) | `planned` |
| [Memory and DMA](#memory) | `planned` |
| [Storage and root](#storage) | `planned` |
| [Display](#display) | `planned` |
| [Input](#input) | `planned` |
| [GPU](#gpu) | `not-applicable` |
| [Network](#network) | `planned` |
| [cellular](#cellular) | `planned` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `planned` |
| [Image assembly](#packaging) | `planned` |
| [Diagnostics](#diagnostics) | `planned` |

## Configuration {#configuration}

`planned`

### Hardware and dependencies

- Format 2 device config derived from examples/device/board.toml, not from umi \(format 1, standalone repository\).
- SoC source is UniXNU-sm8250-common, pinned in feeds.toml at 3f6034d21b4e5f6830c76ca4da4fe3b6fc0125fa.
- OS profile ipados-17.7.11-21H461 exists in the UniXNU tree and is shared with umi.

### Configuration

- board.toml: schema\_version = 2, board.name=cmi, board.soc=SM8250, board.soc\_source=sm8250, board.kit=cmi.
- kernel.defconfig=cmi\_defconfig; config\_fragments and patch\_series follow the template layer order arch, soc, os, device.
- Arrays replace inherited values, so every fragment and series entry is listed explicitly.

### Procedure

- Validated board.toml parses with tomllib: schema\_version 2, dram\_size 0x1fbb00000, payload.adt.chip\_id 164 \(hex\).

### Development findings

- payload.adt.chip\_id is parsed as hexadecimal by scripts/unixnu/devicetree.py \(int\(str\(chip\_id\), 16\)\); the template value 207 means 0x207, so cmi uses 164 = 0x164.
- board.example must stay unset: build and bootimg reject example repositories.
- scripts/unixnu/feeds.py resolve\_soc\(\) looks up the feed by \(kind = "soc", name = board.soc\_source\) and raises "soc source sm8250 needs a pinned commit" when neither feeds.toml nor unixnu.lock carries one, so the pin is a build input, not documentation.
- The paths of this area also cover .github/\*\*: scripts/porting-record.py check --base compares every non-Markdown path with the area patterns, and an unowned path fails with "add its owner area and paths".
- .github/workflows/porting-record.yml only calls UniXNU/UniXNU/.github/workflows/porting-record.yml@main, so the checks that run here are the upstream ones: python3 tools/scripts/porting-record.py check --device device --base &lt;before&gt;.
- board.toml \[firmware\] packages must list every PACKAGES\_PATH root that the DSC chain includes, and \[firmware.defines\] carries the same research-build switch set the reference device umi passes \(ENABLE\_SECUREBOOT, MEMORY\_PROTECTION, SHIP\_MODE, DEVICE\_MODEL, BUILDID\_STRING\); neither list is verified by a build yet.
- scripts/unixnu/util.py clang\_bin\(\) symlinks clang, lld-link, llvm-lib and llvm-rc into CLANG\_BIN and raises "not found on PATH" for the first one missing, so the firmware job must provide unversioned names for all four; the workflow creates them from /usr/lib/llvm-\*/bin when the distribution only ships versioned binaries.
- The firmware job runs fetch, tree and firmware as separate steps so a failure is attributable to source fetching, tree assembly or the EDK2 build without reading step logs.
- Actions logs cannot be downloaded without authentication even on a public repository \(403\), but check-run annotations can be read anonymously; the firmware job therefore emits the tail of its build logs with ::error:: so tools/gh\_annotations.py can read the real failure without a token.
- Annotations carry only about ten lines, so the firmware job also force-pushes a complete log to the ci-logs branch on failure; raw.githubusercontent.com/&lt;owner&gt;/&lt;repo&gt;/ci-logs/firmware.log then serves the full build transcript without credentials, which is why the workflow needs contents: write.
- The same trick publishes a successful build: the FD and its sha256 are force-pushed to the fd branch, because the artifact download endpoint needs authentication even for a public repository.
- The first successful package produced kernel.macho, payload.img and boot.img, but with \[payload\] size\_mib = 192 the boot image came out at 201,752,576 bytes while cmi's boot partition is a 128 MiB image \(the stock boot.img is exactly that\). kernel.macho measures 51,892,224 bytes, so size\_mib = 64 keeps the payload and the trust cache inside the partition.
- reAAAq/UniXNU-umi runs the same SM8250 SoC: its \[payload\] also uses size\_mib = 64, keepsyms=1 and kt\_fixed\_zones=120, its \[payload.adt\] chip\_id 0x164 matches this device's qcom,msm-id, and its userdata geometry \(first\_lba 0x2c0000, lba\_bytes 4096\) differs from cmi only in last\_lba \(0x3b51ffa vs 0x3b4b7fa\).
- Format 2 documents \[payload\] panic\_screen as the switch that paints a kernel panic on the display; with no panel driver in cmiPkg that is the only way to read a kernel failure on the handset, so it is enabled together with the board's own boot-progress archive.
- The package payload is published by UniXNUPkg/Driver/UniXNURamDiskDxe, which docs/zh/porting/uefi-firmware.md names as the required module: umi's bring-up driver UmiRamPayloadDxe rejected the 64 MiB package volume \(its check demanded Sectors\*512 == span exactly\) and the menu fell back to its built-in configuration with \`no boot entry found\`. Replacing it in cmi.dsc, DXE.inc and APRIORI.inc made the menu list the Mi 10 Pro entry again.
- A 64 MiB ramdisk is accepted end to end: with the official driver, choosing the entry prints DarwinBoot's ARM64 kernel mapping \(va=0xFFFFFFF00427C000 pa=0xC007C000 args=0xC417C000, display 0x9C000000 row 4320 1080x2340 depth 32, \`-v serial=3\`\) and ends with \`inputs validated; exiting boot services\`, which also proves the ADT carries every placeholder DarwinBoot requires.
- Kernel output is the next gap: cmi has no exposed UART and no kernel video console, so after ExitBootServices the screen keeps one green bar and nothing else. The board therefore must not grow a hand-written progress implementation; reAAAq/UniXNU-umi already ships package/boot-progress for this SoC, and upstream patches/xnu/zzz-boot-progress.patch pairs with it \(its bsd\_init.c hunk needs sheng's XNU\_SHENG\_PMGR block, so cmi skips that hunk\).
- The local patches/xnu/cmi-boot-progress.patch is gone with the klog experiment: the series keeps only the two XnuPrelink patches plus the arch series, so the kernel build no longer applies any board-owned XNU diff.
- The OS patch series cannot be reused whole: profiles/os/ipados-17.7.11-21H461/patches/xnu/series starts with zzz-boot-progress.patch, whose bsd/kern/bsd\_init.c hunk needs sheng's XNU\_SHENG\_PMGR block. cmi keeps a local copy without that hunk and lists the two XnuPrelink patches directly in patches/xnu/series.
- fastboot boot needs an Android boot image, not the raw firmware volume: scripts/unixnu/bootimg.py compiles BootShim/BootShim.S, appends the FD, gzips the pair, appends the patched device tree and calls Resources/Scripts/mkbootimg.py with the parameters of Resources/Configs/cmi.toml \[boot\_image\]. Handing a bare FD to fastboot leaves the phone on a black screen in fastboot mode without writing anything.
- ShengUfs was selected on 2026-11-06 and reverted the same day: the kernel link failed on verified-root, boot-progress and IOBlockStorageDevice symbols, so board.toml is back to the five-component baseline with no \[kernel\] archives \(letting the build derive it\) and no native-ufs-root=1. What survives the revert is selection-independent: the \[userdata\] geometry and umi's cpu\_regs stay, and dts/cmi.dts keeps the extra compatible. Four rules of the tooling were learned the hard way and are worth keeping: an explicit \[kernel\] archives list replaces the derived one and must reproduce it in full \("unixnu: \[kernel\] archives needs component entries for: ArmCpu, ArmDTPlatform, SoftwareAES", then test -f "$CRYPTO\_ARCHIVE" failed, because build-corecrypto-14.py, its --namespace pass and build-libpthread-kernel.py are derived entries too\); porting-record expands the dependency closure of \[components\] include \("components without an area: \['VerifiedRoot', 'VirtioMmioBlock'\]"\); and the area that owns a changed file must update its findings or evidence in the same commit \("board.toml: update configuration findings or evidence with this change"\).

### Completion criteria

- All source pins resolve; every selected component belongs to an area; status shows intended overrides and patch order.

### Current limits

- The SoC repository is private, so the pinned commit cannot be fetched or reviewed from a host without credentials; the pin is only as good as that push.
- The record was checked by replaying the rules of scripts/porting-record.py locally \(tools/check\_record.py\); the official Porting record workflow has not yet run on this revision.
- No UniXNU checkout exists on this host, so ./unixnu defconfig, fetch and status have never run against board.toml.

### Next action

- Push this revision and confirm the Porting record check on the published commit, then run ./unixnu defconfig cmi\_defconfig -D ../UniXNU-cmi in a real checkout.

### Evidence

Collect evidence using the next action.

## Firmware and boot {#firmware}

`host-verified`

Components: `DarwinBoot`.

### Hardware and dependencies

- Android boot image: header version 1, 4096-byte pages \(Xiaomi SM8250 convention, confirmed in the stock header\).
- Identity: qcom,msm-id 0x164 with SoC revision 0x00020001, qcom,board-id 0x24.
- Splash handoff region: cont\_splash\_region 0x9c000000 size 0x2300000, taken from the device device tree.
- Reference firmware package uefi-umi/Platforms/Xiaomi/umiPkg: Application/, Drivers/, Include/, Library/, umi.dec, umi.dsc, umi.fdf. Its DSC includes KonaPkg/KonaPkg.dsc.inc, so the SM8250 SoC layer is shared and only board PCDs and board drivers need changing.

### Configuration

- \[\[bootimg.dtb\_node\]\] adds /reserved-memory/splash\_region with label cont\_splash\_region for the stock bootloader.
- firmware.config=cmi, dsc=Platforms/Xiaomi/cmiPkg/cmi.dsc, fd=Build/cmiPkg/&\#123;target&\#125;\_CLANGPDB/FV/SILICIUM\_UEFI.fd.

### Procedure

- Compile the board DTS with dtc -I dts -O dtb -i &lt;soc dts dir&gt;; apply bootimg.dtb\_node with fdtput via ./unixnu bootimg.

### Development findings

- cmiPkg is a line-for-line derivative of Platforms/Xiaomi/umiPkg: same \!include KonaPkg/KonaPkg.dsc.inc, same library and driver list; only the SMBIOS PCDs, the stack base and the CCD flags differ.
- scripts/unixnu/firmware.py runs "build -p &lt;firmware.dsc&gt; -a AARCH64 -b &lt;target&gt; -t CLANGPDB", then requires the file named by firmware.fd to exist and to be exactly uefi\_fd.size bytes from Resources/Configs/cmi.toml \(0x00300000 here\); a base value in the config is only passed to the build as -D FD\_BASE.
- package.edk2\_dir\(\) raises "no edk2 tree: pass --edk2 DIR \(a Mu\_Basecore checkout\)" when neither --edk2/UNIXNU\_EDK2 nor a fetched refer edk2 module is present, and it then requires MdePkg/MdePkg.dec; Mu\_Basecore is a submodule of uefi-umi, so a recursive checkout provides it.
- The DSC chain needs PACKAGES\_PATH entries that resolve KonaPkg and QcomPkg \(Silicon/Qualcomm\), umiPkg INFs and the FLASH\_DEFINITION cmiPkg/cmi.fdf \(Platforms/Xiaomi\) and Silicium packages \(Silicon/Silicium\); board.toml \[firmware\] packages lists those roots.
- The FD is written to &lt;uefi&gt;/Build/cmiPkg/&lt;target&gt;\_CLANGPDB/FV/, not to the UniXNU output tree, because the DSC sets OUTPUT\_DIRECTORY = Build/cmiPkg; a workflow that searches only out/ cannot find it.
- The first successful firmware build needed three fixes together: the PACKAGES\_PATH roots, --edk2 pointing at the Mu\_Basecore submodule, and a cmiPkg Include tree \(APRIORI.inc, DXE.inc, RAW.inc plus the UmiSpmiLib and UmiRpmhLib headers\) that cmi.fdf and cmi.dec reference but the package did not have.
- The board briefly carried its own kernel progress implementation \(kits/cmi/CmiKlog.c, scripts/build-cmi-klog.py and a hand-edited copy of zzz-boot-progress.patch\). It is removed: format 2 already exposes \[payload\] panic\_screen, and reAAAq/UniXNU-umi ships a complete SM8250 boot-progress package, so a second implementation only adds surface area to maintain.
- This handset refuses fastboot boot for an unsigned image: ABL answers "Failed to load/authenticate boot image: Load Error" and stays in fastboot with the backlight on. Header version 0 and 1, with and without an appended device tree, fail identically, so the rejection is authentication rather than image layout; fastboot flash boot is the path that holds an unsigned image here.
- GOP and ConIn must exist before BdsDxe runs: BDS registers the console variables and connects the consoles in its BeforeConsole phase, so InheritedFbDxe and UmiButtonsDxe listed after BdsDxe in the APRIORI table are never bound by GraphicsConsoleDxe and UniXNU.efi starts headless. Reordering the APRIORI and DXE lists so they precede BdsDxe is what made UniXNU.efi start and draw its own menu.
- UniXNU reads its configuration from \\EFI\\UniXNU\\unixnu.toml \(PcdUniXNUConfigPath\), so a FAT payload volume needs a VFAT long-name entry: an 8.3 name such as UNIXNU.TOM cannot match a four-character extension, and the firmware then falls back to its built-in action-only menu with "no boot entry found".
- cmi.fdf includes Include/DXE.inc, so an INF listed in both places is emitted twice and GenFv aborts with "the Nth file and Mth file have the same file GUID"; APRIORI.inc is a priority list and may repeat an INF that DXE.inc or the FDF already lists.
- The arm\_init panic probe was withdrawn the same evening it was written, and it answered nothing. The first revision died in git apply \("corrupt patch ...:16": blank context lines need a leading space and the hunk counts did not match\); the corrected diff applied, arm\_init.c compiled without a single warning, and the build then failed at a make target the baseline never reaches \("LDFILELIST bsd", then Error 2\) with no compiler diagnostic anywhere in the step log. The design was wrong anyway: \[payload\] panic\_screen needs a framebuffer too, and the kernel has none, so a panic would have painted nothing either. Kernel-side visibility therefore has to start with the framebuffer handoff, not with a probe.

### Completion criteria

- Firmware image builds, enters UniXNU, publishes the framebuffer and preserves the documented memory reservations.

### Current limits

- The menu, its configuration and volume keys are confirmed on the handset, but memory-reservation preservation and the kernel handoff are not: there is no Payloads/kernel.macho yet, so choosing the entry cannot succeed.
- cmiPkg has no panel init and no backlight control yet; it reuses umiPkg panel-less GOP handoff, so the panel stays whatever the stock bootloader initialized.
- The build needs uefi-umi at 030effd or newer: earlier revisions have no cmiPkg/Include tree, so the \!include lines of cmi.fdf fail.

### Next action

- Package Payloads/kernel.macho with the package workflow on a macOS runner, repack the payload volume with it, and flash the result.

### Evidence

- `host`: [The firmware step completed in 58 s and wrote uefi-cmi/Build/cmiPkg/DEBUG\_CLANGPDB/FV/SILICIUM\_UEFI.fd; the follow-up size check passed against uefi\_fd.size 0x00300000, and the uploaded cmi-uefi-fd artifact is 412840 bytes compressed. Nothing was booted.](https://github.com/wangjiaxue001/UniXNU-cmi/actions/runs/42015025767)
  Command: <code>./unixnu firmware -D ../UniXNU-cmi --uefi ../uefi-cmi --edk2 ../uefi-cmi/Mu_Basecore</code>. Revision: `c245f21cbf3e135e0d6d629b09159116101e5232`.

## CPU and interrupts {#cpu}

`planned`

Components: `ArmCpu`, `ArmDTPlatform`.

### Hardware and dependencies

- 8 CPUs, compatible qcom,kryo, MPIDR affinity 0x0, 0x100, 0x200, 0x300, 0x400, 0x500, 0x600, 0x700 \(device DT /cpus/cpu@N\).
- GICD 0x17a00000 size 0x10000; GICR 0x17a60000 size 0x100000; redistributor-stride 0x20000 \(device DT\).
- PSCI method smc \(device DT /psci\).

### Configuration

- dts/sm8250.dtsi declares /cpus with timebase-frequency, /psci, and the GIC node with unixnu,adt-name = "intc" and phandle 1.
- Each CPU carries unixnu,cluster-type: cpu@0-300 are "E" and cpu@400-700 are "P", derived from the measured capacity-dmips-mhz values 0x1c0 versus 0x3fe-0x400.
- The interrupt-controller at 0x0b220000 is qcom,kona-pdc, not GICR, and is deliberately not exported yet.

### Procedure

- dtc compiles the tree; check\_adt.py confirms 8 CPUs, timebase-frequency present, psci method valid, phandle unique.

### Development findings

- timebase-frequency is absent from the vendor device tree; 19200000 is the SM8250 architectural timer constant and is unverified on hardware.
- \#address-cells is not in the ADT property whitelist and was dropped from the GIC node.

### Completion criteria

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU.

### Current limits

- No kernel build; timer frequency not measured on device.

### Next action

- Read the arch timer frequency from a booted kernel log or a hardware measurement, then confirm or correct timebase-frequency.

### Evidence

Collect evidence using the next action.

## Memory and DMA {#memory}

`planned`

Components: `SoftwareAES`.

### Hardware and dependencies

- Three DRAM banks: 0x80000000+0x3bb00000, 0xc0000000+0xc0000000, 0x180000000+0x100000000.
- Bank sum 0x1fbb00000 \(7.93 GiB\); a 0x4500000 \(69 MiB\) hole sits at 0xbbb00000..0xc0000000.
- 22 reserved-memory regions with base and size read from the device tree, including cont\_splash\_region, dfps\_data\_region and disp\_rdump\_region.

### Configuration

- cmi.dts declares exactly one enabled memory node with one reg range: base 0x80000000, size 0x1fbb00000.
- payload.dram\_size in board.toml equals that size; the ADT generator rejects any difference.

### Procedure

- dtc compiles the tree; check\_adt.py verifies one memory node, single range and exact dram\_size equality.

### Development findings

- The ADT generator requires one contiguous DRAM range, so the three banks are expressed as their sum rather than the 0x200000000 span; the hole is not declared as DRAM.
- reserved-memory no-map and reusable attributes are not set: they were not measured and affect whether the kernel may allocate those ranges.

### Completion criteria

- All handoff regions are accounted for and each enabled DMA engine accesses its allocated range with the documented cache policy.

### Current limits

- no-map/reusable per region unknown; SMMU ownership and DMA bit width not inventoried.

### Next action

- Read the no-map/reusable flags from the vendor device tree and set them per region before any XNU boot.

### Evidence

Collect evidence using the next action.

## Storage and root {#storage}

`planned`

### Hardware and dependencies

- UFS host: compatible qcom,ufshc, reg 0x1d84000+0x3000 and 0x1d90000+0x8000 \(ICE\), interrupt SPI 0x109 level-high, lanes-per-direction 2.
- userdata GPT entry: first\_lba 0x2C0000, last\_lba 0x3B4B7FA, lba\_bytes 4096 \(measured on this handset, 226.18 GiB\).
- Device storage: sda 254.7 GB with super 8.5 GiB of dynamic partitions.

### Configuration

- dts/sm8250.dtsi defines ufs \(label ufs, unixnu,adt-name ufshc, interrupt-parent &lt;&amp;intc&gt;\) and ufsphy \(0x1d87000, qcom,ufs-phy-qmp-v4\); both default to disabled.
- dts/cmi.dts enables them with status = "okay" and adds "qcom,sm8250-ufshc" to the &amp;ufs compatible list after the stock "qcom,ufshc"; the extra value exists only so the ShengUfs personality \(rewritten by scripts/build-cmi-ufs.py\) can bind.
- board.toml does not select ShengUfs yet. The selection, \[kernel\] archives and native-ufs-root=1 were tried on 2026-11-06 and reverted the same day after the kernel link failed; what stays in board.toml is only what is independent of the selection \(\[userdata\] geometry and the umi cpu\_regs\), and dts/cmi.dts keeps the extra compatible for the day it returns.

### Procedure

- GPT was read by dumping 8 sectors of /dev/block/sda and parsing the header on the host, because TWRP ships no sgdisk, parted or fdisk.

### Development findings

- scripts/build-cmi-ufs.py rewrites the fetched ShengUfs copy for SM8250: GCC\_UFS\_PHY\_AXI\_ENABLE 0x77018 -&gt; 0x77010, GCC\_UFS\_PHY\_AHB\_ENABLE 0x77024 -&gt; 0x77018, compatible qcom,sm8550-ufshc -&gt; qcom,sm8250-ufshc, GDSCR 0x77004 unchanged. Verified on the host against the real GccUfs.h and NativeUfs.cpp, and the CI log shows the recipe executing from &lt;tree&gt;/scripts/ during the kernel build.
- ShengUfs still ships IONameMatch qcom,sm8550-ufshc; the component-side change is the qcom,sm8250-ufshc rewrite above, not a local fork.
- SM8250 constants come from reAAAq/UniXNU-umi \(same GCC block base and GDSCR; AXI 0x77010, AHB 0x77018\). The controller base 0x1d84000/0x3000 is identical, but SM8250 UFS 3.x versus SM8550 UFS 4.x behaviour is unverified on hardware.
- Selecting ShengUfs does not link on this revision. scripts/build-arm-driver.py compiles NativeUfs with -DNATIVE\_VERIFIED\_BLOCK=1 -DNATIVE\_VERIFIED\_BLOCK\_MULTI\_POLICY=1 unconditionally, so libShengUfs.a references verified\_root\_key, verified\_root\_policies, verified\_root\_policy\_count, vr\_open, vr\_verify\_block and vr\_xnu\_crypto; NativeUfsBlock also derives from IOBlockStorageDevice and calls boot\_progress\_poll. The 2026-11-06 link failed on exactly those symbols. Satisfying them needs the VerifiedRoot kit plus a generated root policy bundle, libBootProgress \(build-boot-progress.py is absent from the UniXNU tree at 18155b4e, so umi's package/boot-progress has to be ported\), and IOStorageFamily linked into the kernel.
- The bookkeeping is settled for when that stack exists: an explicit \[kernel\] archives list replaces the derived one, so it must carry build-corecrypto-14.py, build-corecrypto-14.py --namespace, component:ArmDTPlatform, component:ArmCpu, component:SoftwareAES, build-cmi-ufs.py immediately before component:ShengUfs, and build-libpthread-kernel.py. Both failure modes were observed in CI \("needs component entries for: ...", then test -f "$CRYPTO\_ARCHIVE" failed\).
- porting-record expands the dependency closure of \[components\] include, so a selected ShengUfs also requires VirtioMmioBlock and VerifiedRoot to be claimed by an area.

### Completion criteria

- Host: register, clock, link and SMMU facts match the board inventory. Reads: capacity, GPT and known blocks correct. Root: volume mounts and launchd starts.

### Current limits

- No PHY, clock, reset, regulator or SMMU inventory; no component build.
- ShengUfs is not selected: this revision compiles it with verified-root forced on, so it cannot link without the VerifiedRoot kit, a root policy bundle, boot-progress and IOStorageFamily.
- Root mount is untested because \[payload.adt\] root\_match\_volume\_uuid and \[userdata\] windows are still unset.
- The SM8250 branch-enable offsets come from umi, not from this board, and have never run on cmi.

### Next action

- Port umi's package/boot-progress \(the kernel-output prerequisite the handover ranks first\) together with the VerifiedRoot kit and a root policy bundle, then re-select ShengUfs using the full archives list recorded here.

### Evidence

Collect evidence using the next action.

## Display {#display}

`planned`

### Hardware and dependencies

- Panel selected by the bootloader: msm\_drm.dsi\_display0=qcom,mdss\_dsi\_j2\_p2\_1\_38\_0c\_0a\_dsc\_cmd.
- Timings: 1080x2340, 24 bpp, 60 Hz \(clock 681489024 Hz\) and 90 Hz, DSC command mode, mi,panel-id 0x4a32.
- Panel GPIOs: reset GPIO 12, TE GPIO 66; rails vci, vddio, dvdd, lab, ibb.
- DCS init, off and timing-switch sequences copied byte-exact from the device tree into dts/panel-j2-p2-1-38-0c-0a.dtsi.

### Configuration

- GopFramebuffer reads the firmware GOP framebuffer through PE\_current\_console, so it consumes no device-tree node; no mdss or dsi node is declared.
- Panel initialization therefore belongs to the firmware package \(cmiPkg\), not to the ADT.

### Procedure

- Panel node was extracted with tools/fdt2dts.py from /sys/firmware/fdt pulled in TWRP.

### Development findings

- Adding an mdss node to the SoC DTSI would be dead weight for the GOP path; the display work is firmware-side.
- Android cross-check: dumpsys display reports 1080x2340, 60/90 Hz, density 440, HDR types 1-4, 420 nits peak.

### Completion criteria

- A known frame appears with correct geometry and colors, then userland presentation and backlight controls work.

### Current limits

- cmiPkg does not exist, so no panel init runs under UEFI; the panel dtsi fragment is not included by any compiled tree.
- Candidate GopFramebuffer is not selected until a firmware package exists to hand over GOP.

### Next action

- Port the panel init sequence into cmiPkg and verify framebuffer handoff after UEFI display initialization.

### Evidence

Collect evidence using the next action.

## Input {#input}

`planned`

### Hardware and dependencies

- Touch controller st,fts at i2c@a94000, address 0x49, interrupt hwirq 39 with flags 0x2008.
- reset GPIO 38, irq GPIO 39, rails named vdd \(bus\) and avdd \(power\), firmware st\_fts\_j1.ftb, x-max 1080 / y-max 2340.
- Key GPIOs are not inventoried yet.

### Configuration

- dts/touch-fts49.dtsi is a reference transcription only: the reference device repository \(UniXNU-sheng\) exports no touch node, so touch binds through board package state, not through the ADT.

### Procedure

- Node extracted with tools/fdt2dts.py; properties read from /proc/device-tree in TWRP.

### Development findings

- cmi uses the same ST FTS family as umi, so umi's FTS transport work is a candidate for reuse; its always-on PM8150B GPIO5 power trick is cmi-unverified.
- ShengHidInput binds on board-level touch state and the IOHIDFamily 2031.120.4 ABI; the ABI record is required for the archive build.

### Completion criteria

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive, and buttons produce expected HID reports.

### Current limits

- No i2c or tlmm node in the SoC DTSI; regulator wiring and firmware loading path unverified.
- Candidate ShengHidInput is not selected until the bus nodes exist and the IOHIDFamily ABI record is provided.

### Next action

- Add the i2c bus and tlmm nodes to the SoC DTSI from measured values, then wire the touch node.

### Evidence

Collect evidence using the next action.

## GPU {#gpu}

`not-applicable`

### Hardware and dependencies

- SM8250 pairs with Adreno 650; no UniXNU GPU implementation targets this part.

### Configuration

- No GPU component selected; Adreno740 and AdrenoMetal cover A740/SM8550 only.

### Procedure

- None yet.

### Development findings

- Selecting Adreno740 here would misreport the hardware range.

### Completion criteria

- No GPU milestone is claimed for cmi: framebuffer output through the firmware GOP does not need a GPU component, and nothing in the catalog targets Adreno 650.

### Current limits

- Out of scope until a GPU component declares SM8250 support; framebuffer output does not need one.

### Next action

- None.

### Evidence

Collect evidence using the next action.

## Network {#network}

`planned`

### Hardware and dependencies

- WLAN chip and firmware are not inventoried; cnss\_wlan\_region and pil\_wlan\_fw\_region exist in the device tree.

### Configuration

- No component selected.

### Procedure

- None yet.

### Development findings

- Ath12kWifi is the only Wi-Fi implementation in the catalog and targets a different part.

### Completion criteria

- Scanning, association, address configuration and sustained traffic pass with the selected firmware.

### Current limits

- Hardware identification pending.

### Next action

- Identify the WLAN chip from the vendor device tree or a booted Android log.

### Evidence

Collect evidence using the next action.

## cellular {#cellular}

`planned`

### Hardware and dependencies

- The handset has a modem partition and mdm1m9kefs1-4; modem firmware and EFS are not inventoried.

### Configuration

- No component selected.

### Procedure

- None yet.

### Development findings

- QcomBaseband documents an SC7180 IPA path; SM8250 applicability is unproven.

### Completion criteria

- Modem firmware loads, QRTR/QMI services answer, SIM identity is read and a data session completes.

### Current limits

- Hardware identification and firmware extraction pending; last in the adaptation order.
- Candidate QcomBaseband is not selected: its documented IPA data path is SC7180, SM8250 applicability unproven.

### Next action

- None until storage and root are verified.

### Evidence

Collect evidence using the next action.

## Audio {#audio}

`planned`

### Hardware and dependencies

- Device tree shows bolero codec, wsa/rx/tx macros and cs35l41 amplifiers; ADSP firmware not inventoried.

### Configuration

- No component selected.

### Procedure

- None yet.

### Development findings

- Audio depends on ADSP bring-up, which is not implemented for SM8250.

### Completion criteria

- Each declared route carries the selected format through playback or capture and handles start/stop correctly.

### Current limits

- Last in the adaptation order.

### Next action

- None until platform, storage and display are verified.

### Evidence

Collect evidence using the next action.

## Power {#power}

`planned`

### Hardware and dependencies

- PMIC topology not inventoried; device tree shows pm8150-class regulators used by display and touch.

### Configuration

- No component selected.

### Procedure

- None yet.

### Development findings

- umi qualified a 512 MiB conventional window and a 256 MiB DarwinBoot allocation on the same SoC; cmi payload windows are still unvalidated.

### Completion criteria

- Declared power controls and battery readings match observations; each claimed sleep/resume transition restores its dependent peripherals.

### Current limits

- Sleep/resume and battery are unverified; owned\_memory\_size is still the template value.

### Next action

- Validate the payload memory window on hardware before claiming any power feature.

### Evidence

Collect evidence using the next action.

## Image assembly {#packaging}

`planned`

Components: `XnuPrelink`.

### Hardware and dependencies

- OS donor: iPad7,1 / iPadOS 17.7.11 / 21H461 / j120ap, ApChipID 0x8011, ApBoardID 12.
- kernel.prelink pins kernelcache sha256 f18b4df8... and early\_security\_init com.apple.driver.AppleMobileFileIntegrity=0xfffffff005ab4ae0.

### Configuration

- \[payload\] volume CMIXNU, size 64 MiB, loader firmware, kernel\_args -v serial=3.
- \[kernel\] archives is unset, so the build derives the recipe list; whenever it is written explicitly it must reproduce that list in full.

### Procedure

- dtc compiles the board DTS; check\_adt.py validates the generator preconditions.

### Development findings

- patches/xnu/ is claimed by both this area and firmware, and porting-record demands a findings update from every owner in the same commit: two consecutive rejections named firmware first, then packaging, for the same patch change. Touch both areas whenever a patch is added or edited.
- The board carries no XNU patch of its own: the klog variant of zzz-boot-progress.patch was deleted together with the implementation it needed, and patches/xnu/series lists only the two XnuPrelink patches.
- cmi-arm-init-marker.patch panics right after PE\_init\_platform\(\) in arm\_init.c, the earliest usable C point. It answers two questions the green bar cannot: did the kernel execute C code at all, and does \[payload\] panic\_screen actually paint. It is temporary and must be removed once both are known.
- The probe exists because there is no cheaper channel: cmi has no exposed UART, and the kernel has no framebuffer at all, so boot\_progress\_bind\(\) from video\_console never fires. Both official display paths need a device-side build script that is absent from the UniXNU tree at 18155b4e: CONFIG\_XNU\_NATIVE\_LEGACY\_DISPLAY requires build/native-legacy-display/libNativeLegacyDisplay.late.a from build-gop-legacy-display.py, and build-boot-progress.py is missing too; only sheng's device repository carries them.
- Hardware DTS compiles clean with dtc 1.8.1 and passes the seven precondition checks.
- The ADT itself has never been generated: that needs a UniXNU checkout and make-adt.py.

### Completion criteria

- Kernel and prelink succeed, payload contains all declared inputs, and the boot image matches the bootloader format and size limit.

### Current limits

- No kernel build, no archive list, no payload or boot image.

### Next action

- Run ./unixnu defconfig, fetch, status --json and tree against a real UniXNU checkout.

### Evidence

Collect evidence using the next action.

## Diagnostics {#diagnostics}

`planned`

### Hardware and dependencies

- TWRP recovery shell over adb \(serial b7c8640e\) provides root for GPT, device tree and bootargs reads.
- Android 14 on this handset is a user build: no su, no Magisk/KernelSU, adb root refused, dmesg and /proc/cmdline denied to shell.

### Configuration

- tools/fdt2dts.py converts an FDT blob to dts; tools/check\_adt.py replays the generator preconditions.

### Procedure

- dd if=/dev/block/sda bs=4096 count=8, then pull and parse the GPT header on the host.
- adb pull /sys/firmware/fdt, then python tools/fdt2dts.py to produce a 37,086-line dts.
- cat /proc/device-tree/chosen/bootargs to read the bootloader panel selector.

### Development findings

- fdtdump rejects fdt.cmi.dtb with 'header is not valid' although the header is valid; the self-written parser is used instead.
- dtc from the MSYS2 package needs libyaml-0-2.dll at load time even for -O dts; the DLL was added next to dtc.exe.

### Completion criteria

- Each claimed milestone has a reproducible command, a matching source/image revision and an accessible result.

### Current limits

- No logs are committed and no 40-character revision exists, so no area can be host-verified yet.

### Next action

- Commit tools and probe records, then attach the exact commands and revision to each area's evidence.

### Evidence

Collect evidence using the next action.

</div>
