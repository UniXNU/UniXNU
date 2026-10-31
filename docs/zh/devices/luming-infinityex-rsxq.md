# Xiaomi Civi 5 Pro \(SM8735; format-2 bring-up, iPadOS 17.7.11 profile\) \(infinityEX-RSXQ\)

[infinityEX-RSXQ/UniXNU-luming-f2-ci](https://github.com/infinityEX-RSXQ/UniXNU-luming-f2-ci)

<div v-pre>

Xiaomi Civi 5 Pro format-2 bring-up skeleton: native 4K XNU + XnuPrelink with the proven iPadOS 17.7.11 profile, a dada-shaped AMFI+PMGR kernel configuration, SM8735 measured hardware facts, SHNGROOT/VerifiedRoot userdata recipe and Mu-Silicium UEFI + DarwinBoot. Every area is planned; no build or boot evidence exists yet.

源记录: [porting.toml](https://github.com/infinityEX-RSXQ/UniXNU-luming-f2-ci/blob/4bff1b93f409ca1fc8c1ba4403abf8fa37e51888/porting.toml), `4bff1b93f409ca1fc8c1ba4403abf8fa37e51888`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `planned` |
| [固件与启动](#firmware) | `planned` |
| [CPU 与中断](#cpu) | `planned` |
| [内存与 DMA](#memory) | `planned` |
| [存储与根卷](#storage) | `planned` |
| [显示](#display) | `planned` |
| [输入](#input) | `planned` |
| [GPU](#gpu) | `not-applicable` |
| [网络](#network) | `not-applicable` |
| [音频](#audio) | `not-applicable` |
| [电源](#power) | `planned` |
| [镜像组装](#packaging) | `planned` |
| [诊断](#diagnostics) | `planned` |

## 配置 {#configuration}

`planned`

组件: `XnuPrelink`, `SoftwareAES`.

### 硬件与依赖

- Official UniXNU format-2 tool + profiles, local UniXNU-sm8735-common scaffold, luming measured lab facts, dada/sheng board references.

### 配置

- schema\_version = 2; board luming/SM8735; soc\_source = sm8735 local feed; os\_profile = ipados-17.7.11-21H461; kit = luming.
- The board vendors a soc/ feed scaffold because UniXNU-sm8735-common is not published or validated.

### 操作步骤

- Run ./unixnu defconfig luming\_defconfig -D ../../agents/f2-luming.
- Run ./unixnu fetch, status --json and tree from the UniXNU checkout.
- Compare the resolved profile/components/patch order with board.toml and the official device-repository spec.

### 开发经验

- The chosen OS profile is the proven official one \(sheng full UI, dada userland\); no official Darwin22/iOS16 profile exists, so iOS16 is an alternative only \(proposals/\).
- dada's board shape is the primary template because it is the closest proven source-XNU format-2 device \(AMFI+PMGR restored\).

### 完成条件

- The resolver reports device luming, SoC sm8735, profile ipados-17.7.11-21H461, output out/luming/ipados-17.7.11-21H461/luming/ and the expected patch order.

### 当前范围

- SM8735 SoC feed is a local scaffold that its own migration note flags as unvalidated.
- Porting record identity and every selected component must stay covered by these areas.

### 下一步

- Run defconfig/status/tree once the UniXNU base feeds are fetched and record the JSON output under docs/evidence/.

### 证据

- `source`: [Format-2 board configuration with pinned measured/placeholder values and sources](https://github.com/infinityEX-RSXQ/UniXNU-luming-f2-ci/blob/4bff1b93f409ca1fc8c1ba4403abf8fa37e51888/board.toml)

## 固件与启动 {#firmware}

`planned`

组件: `DarwinBoot`.

### 硬件与依赖

- uefi-luming Mut-Silicium checkout for the luming package, stock luming vendor DXE set, Mu-Silicium patches listed in firmware/patches/, UniXNU/UniXNUDxe/UniXNURamDiskDxe modules.

### 配置

- firmware.dsc = Platforms/Xiaomi/lumingPkg/luming.dsc; firmware.fd = Build/lumingPkg/&\#123;target&\#125;\_CLANGPDB/FV/SILICIUM\_UEFI.fd; ENABLE\_SECUREBOOT=0 for the first boot.
- The firmware must embed UniXNU, UniXNUDxe, UniXNURamDiskDxe, DarwinBoot and DiskIo/FAT; the payload volume is LUMINGESP.

### 操作步骤

- uefi-builder builds the FD from the local uefi-luming tree \(see firmware/README.md\).
- ./unixnu build firmware --uefi &lt;uefi-luming&gt;; record the FD size and module list.
- ./unixnu bootimg passes the firmware DTB as --dtb; check boot.json fd\_sha256/dtb\_sha256/ramdisk\_bytes.

### 开发经验

- The local uefi-luming tree boots the known-good UniXNU menu baseline but does not yet embed the format-2 modules.
- luming needs the luming-specific platform FDT/DTB handling already fixed in the UFS/AI8 campaign.

### 完成条件

- FD size matches the Mu-Silicium config, contains the required modules, and the v4 boot image starts UniXNU/DarwinBoot with the payload volume visible.

### 当前范围

- FD base/size for the format-2 path is not measured; uefi-luming is not published as a uefi-luming repository.
- Firmware ownership is uefi-builder; this record tracks the interface only.

### 下一步

- Hand firmware/README.md to uefi-builder and record the first FD hash + module list.

### 证据

- `source`: [Firmware interface, required modules and Mu-Silicium patch set for the format-2 route](https://github.com/infinityEX-RSXQ/UniXNU-luming-f2-ci/blob/4bff1b93f409ca1fc8c1ba4403abf8fa37e51888/firmware/README.md)

## CPU 与中断 {#cpu}

`planned`

组件: `ArmCpu`, `ArmDTPlatform`.

### 硬件与依赖

- Live DT /cpus \(8 Kryo cores, MPIDR Aff1 0..0x700\), arm,armv8-timer PPI 13/14/11/12 at 19.2 MHz, PSCI SMC, GICD 0x17100000/0x10000 and GICR 0x17180000/0x200000 stride 0x40000.

### 配置

- dts/luming.dts + soc/dts/sm8735.dtsi carry the 8 CPUs, PSCI and GIC nodes; virtual-timer-intid = &lt;27&gt; is recorded but the converter has no typed binding for it.
- soc/patches/xnu/native-smp-secondary.patch raises MAX\_CPUS to 8 and handles the MPIDR Aff1 numbering.

### 操作步骤

- Compile the board DTS with dtc and inspect the ADT /cpus and /arm-io/intc nodes.
- Record per-CPU entry, timer interrupts, IPI delivery and the VTIMER=27 value on hardware.

### 开发经验

- VTIMER INTID is 27 \(PPI 11 + 16\), not sheng's 19 and the same as the SM8350 star port.
- The timer property needs an upstream converter binding before it reaches the ADT; the arch profile timer patch currently owns the generic timer path.

### 完成条件

- All enabled CPUs reach their entry checkpoint, timer/IPI handling works on every enabled CPU, and the GIC/timer values match the measured A-line facts.

### 当前范围

- CPU selection and frequency policy are board inputs; the SoC DTSI describes all eight cores but the first boot should use cpus=1.

### 下一步

- Run the DTS compile and record the ADT CPU/GIC byte dump; then verify the timer binding question with the format-2 owners.

### 证据

- `source`: [Measured CPU/timer/GIC facts with their source paths](https://github.com/infinityEX-RSXQ/UniXNU-luming-f2-ci/blob/4bff1b93f409ca1fc8c1ba4403abf8fa37e51888/docs/KNOWN-VALUES.md)

## 内存与 DMA {#memory}

`planned`

组件: `RamBlock`.

### 硬件与依赖

- Live /proc/iomem: low bank 0x80000000..0xffffffff with XPU carve-outs; upper System RAM 0x880000000..0xaffffefff with holes; largest contiguous window 0x8c0000000..0xaffffefff = 0x23ffff000.
- A-line prelinked kernel physBase/markers around 0x8c01e06a0/0x8c4000000.

### 配置

- dts/luming.dts memory@8c0000000 reg = &lt;0 0x8c0000000 0 0x23ffff000&gt;; board.toml payload.dram\_size = 0x23ffff000.
- payload.adt owned\_memory\_size = 0x10000000 \(dada measured value; luming not measured\).

### 操作步骤

- Compare the firmware memory map, DTS memory node, ADT chosen dram-base/size and DarwinBoot owned window.
- Check every DMA buffer \(UFS, display later\) against controller address width and SMMU mapping.

### 开发经验

- Format 2 requires exactly one contiguous DRAM range; the measured luming tree has several XPU-split regions, so the high-bank contiguous window was chosen and the alternative low 2 GiB shape is documented.
- 0x23ffff000 is not 2 MiB aligned; if XNU/DarwinBoot rejects it, use 0x23ff00000 in both the DTS and payload.dram\_size.

### 完成条件

- All handoff regions are accounted for, the ADT dram window matches the DTS, and each enabled DMA engine reaches its buffers with the documented cache policy.

### 当前范围

- The DarwinBoot owned window for luming is not measured; the value is inherited from dada as a placeholder.
- RamBlock/Data-seed staging still needs the DBRDISK1 seed input.

### 下一步

- Measure the luming DarwinBoot window during S1/S3, then update owned\_memory\_size and the ADT memory window together.

### 证据

- `source`: [DRAM window measurements and alignment risk \(sections 2-3\)](https://github.com/infinityEX-RSXQ/UniXNU-luming-f2-ci/blob/4bff1b93f409ca1fc8c1ba4403abf8fa37e51888/docs/KNOWN-VALUES.md)

## 存储与根卷 {#storage}

`planned`

组件: `LumingUfs`, `VirtioMmioBlock`, `VerifiedRoot`.

### 硬件与依赖

- UFS host 0x1d84000/0x3000 + ICE/MCQ windows, PHY 0x1d80000 qcom,ufs-phy-qmp-v4-niobe, apps SMMU stream 0x60, GCC tuna offsets, userdata GPT LBAs 3124736..128619514 at 4096 B.
- SHNGROOT image windows OS/SystemOS built from the active profile; root UUID 04769D26-2CA0-4825-B443-E2E5F88300F2; DBRDISK1 Data seed.

### 配置

- Select LumingUfs \(board module; catalog lineage ShengUfs/NativeUfs\) and point CONFIG\_XNU\_NATIVE\_UFS\_ARCHIVE at build/luming-ufs/libLumingUfs.a; native-ufs-root=1/native-ufs-diagnostics=1 in kernel\_args.
- board.toml userdata windows OS/SystemOS; payload.adt packed\_data\_ramdisk/persistent\_data + root UUID; VerifiedRoot selected for the SHNGROOT recipe.

### 操作步骤

- Read docs/UFS.md and the A-line UFS reports.
- Use the luming fork of DadaUfs/ShengUfs \(NativeUfs\) with the storage-class/kext-binding archives; add the catalog entry and publish the source.
- Validate stage-0 snapshot, GPT read, SHNGROOT windows, root UUID mount and Data seed.

### 开发经验

- The UFS SM8735 driver exists only as a prelinked/device-repo build path; it is not a format-2 component.
- The A-line proved the controller can be adopted and the GPT read; the UFSDxe init works after the platform-FDT fix.
- The transport must not compile IOBlockStorageDevice itself; the base class comes from the prelinked IOStorageFamily kext \(dada\).

### 完成条件

- Host: controller/PHY/clock/SMMU facts match the board inventory and the component builds from source.
- Reads: capacity/GPT/known blocks correct; SHNGROOT windows within userdata.
- Root: the APFS volume mounts by UUID and launchd starts; Data seed mounts at /private/var.

### 当前范围

- LumingUfs is a board module; it needs an upstream catalog entry \(patch prepared\) and a published source.
- The no-AMFI first boot may need dada's AMFI-less entitlement guards before userland exec.

### 下一步

- Create the LumingUfs component and its archive builders, then run the stage-0 UFS validation from docs/UFS.md.

### 证据

- `source`: [Storage facts, component work order and acceptance criteria](https://github.com/infinityEX-RSXQ/UniXNU-luming-f2-ci/blob/4bff1b93f409ca1fc8c1ba4403abf8fa37e51888/docs/UFS.md)

## 显示 {#display}

`planned`

### 硬件与依赖

- ABL splash FB 0xFC800000/0x2b00000, stride 4944, 1236x2750; panel command qcom,mdss\_dsi\_o9\_42\_02\_0a\_dsc\_cmd; UEFI GOP hand-off via DarwinBoot boot\_args.Video.

### 配置

- No display component selected for the first boot: XNU's pexpert video console draws through DarwinBoot's GOP boot\_args.
- board.toml \[\[bootimg.dtb\_node\]\] keeps the splash reservation so ABL does not power the panel off.

### 操作步骤

- First boot validates the text console and panic screen.
- Then port/select a display component publishing IOMobileFramebuffer for luming \(panel/backlight/rail work\), recording frame timing and pixel format.

### 开发经验

- dada also reaches userland without a display service; sheng has GopFramebuffer but its stack is SM8550/Adreno-oriented.
- The A-line/format-1 facts give the FB geometry for the console and the future display component.

### 完成条件

- Text console/panic screen visible on first boot; later a known frame is presented with correct geometry/colors and userland presentation works.

### 当前范围

- No luming display component exists; the GPU family \(gen8-6-0\) has no matching catalog component.

### 下一步

- Record the first-boot console screenshot, then scope the display component with the panel/backlight/regulator inputs.

### 证据

- `source`: [Display/input scope, inputs and missing-component note](https://github.com/infinityEX-RSXQ/UniXNU-luming-f2-ci/blob/4bff1b93f409ca1fc8c1ba4403abf8fa37e51888/drivers/LumingDisplayTouch/README.md)

## 输入 {#input}

`planned`

### 硬件与依赖

- Stock DT touch node, PMIC/SPMI key nodes, luming panel/touch power rails \(to be identified from the live DT and vendor kernels\).

### 配置

- No input component selected yet; sheng's ShengHidInput + touch component are shape references, not luming hardware.
- The first boot does not need input; the menu can auto-boot \(timeout 0\) and the console needs no keys.

### 操作步骤

- Identify the touch controller and key wiring from the stock DT and vendor sources.
- Port an input component delivering Apple HID events \(IOHIDEventService\) and validate touch/keys on hardware.

### 开发经验

- sheng's Novatek touch is SM8550 hardware; luming's touch controller must be measured.
- Input is required for Setup/SpringBoard interaction, not for S1-S6.

### 完成条件

- Touch and hardware keys reach iOS/backboardd as HID events and the UI can be navigated.

### 当前范围

- No luming input driver exists; no hardware touch facts are recorded yet.

### 下一步

- Extract the touch/keys nodes from backup/analysis/device-live/luming-live/dtb-dump.json and pick the driver family.

### 证据

按下一步操作收集证据。

## GPU {#gpu}

`not-applicable`

### 硬件与依赖

- SM8735 GPU is qcom,adreno-gpu-gen8-6-0 at 0x3d00000 with GMU/SMMU; the catalog only has Adreno740/AdrenoMetal for SM8550.

### 配置

- No GPU component is selected and the GPU/GMU nodes stay disabled; the first boot is console-only and userland CPU-rendered at best.

### 操作步骤

- Defer until boot/storage/userland are proven; then evaluate a gen8-6-0 component or a community implementation.

### 开发经验

- The SM8550 Adreno740 component does not match this GPU family; dada also runs without a GPU driver.

### 完成条件

- Not applicable for the CPU-console / CPU-rendered bring-up milestones recorded here.

### 当前范围

- GPU/Metal/display acceleration is out of scope for this skeleton.

### 下一步

- Revisit only after S7 userland with CPU rendering.

### 证据

按下一步操作收集证据。

## 网络 {#network}

`not-applicable`

### 硬件与依赖

- No Wi-Fi/BT/cellular driver or firmware is ported; luming bring-up does not depend on network.

### 配置

- No network component is selected; the payload/menu and first boot work offline.

### 操作步骤

- Record network as out of scope until userland is stable.

### 开发经验

- sheng's Ath12kWifi and dada's cellular work are unrelated hardware; no luming network facts are measured.

### 完成条件

- Not applicable to the recorded bring-up milestones.

### 当前范围

- No wireless/cellular support in this skeleton.

### 下一步

- Revisit after userland with a chosen luming wireless device.

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`not-applicable`

### 硬件与依赖

- No audio DSP/codec driver or firmware is ported; bring-up does not depend on audio.

### 配置

- No audio component is selected.

### 操作步骤

- Record audio as out of scope for the bring-up milestones.

### 开发经验

- sheng/dada audio work is SM8550/SM8750 hardware and not reusable directly.

### 完成条件

- Not applicable to the recorded bring-up milestones.

### 当前范围

- No audio support in this skeleton.

### 下一步

- Revisit after userland.

### 证据

按下一步操作收集证据。

## 电源 {#power}

`planned`

### 硬件与依赖

- SM8735 GCC/RPMh/regulator facts are partially measured \(GCC tuna offsets, UFS GDSC/reset\); PMIC/regulator rails are not enumerated for the iOS load.

### 配置

- SHENG\_PMGR is on; the copied build-luming-platform-power.py \(DadaPlatformPower, same kernelcache/slide addresses\) publishes the ApplePMGRNub; untested on SM8735.
- The no-AMFI first boot relies on firmware-left power and the UFS/display components for their own rails.

### 操作步骤

- Record GCC/UFS GDSC/branch state in the stage-0 snapshot \(A-line technique\).
- If the AMFI/PMGR route is wanted later, port sheng's build-sheng-platform-power.py candidate-based instrument for luming.

### 开发经验

- The copied PMGR instrument must satisfy AMFI on SM8735; the copied AMFI-less entitlement guards are the fallback only.
- The UFS transport's clock/power assumptions are inherited from the firmware handoff.

### 完成条件

- All components that consume power own their rails explicitly; no rail is left to an implicit firmware state.

### 当前范围

- No luming power component or regulator inventory yet; the AMFI+PMGR route is unbuilt.

### 下一步

- Capture GCC/UFS GDSC/branch values in the first hardware snapshot, then decide whether the PMGR instrument is needed.

### 证据

按下一步操作收集证据。

## 镜像组装 {#packaging}

`planned`

组件: `XnuPrelink`, `SoftwareAES`.

### 硬件与依赖

- XnuPrelink kit + profile prelink values, source corecrypto/SoftwareAES archives, payload volume/dram inputs, boot image v4 parameters, Dada/Sheng packaging references.

### 配置

- board.toml \[kernel\].archives selects corecrypto/pthread/Arm\*/SoftwareAES/RamBlock/LumingUfs builders; storage-class and luming builders are missing placeholders.
- Payload = LUMINGESP 192 MiB; bootimg image = header v4, base 0, kernel\_offset 0x8000, ramdisk\_offset 0x01000000, tags 0x100.

### 操作步骤

- Build kernel then package, firmware, payload, userdata and bootimg in that order.
- Validate boot.json \(header v4, ramdisk\_bytes, fd/dtb hashes\) and the payload FAT contents before any device step.

### 开发经验

- Format 2 owns prelink through the OS profile + kit; the A-line prelinked-kernel binary bypasses must not be reused.
- The format-1 LumingKit stub is kept only as a reference.

### 完成条件

- All artifacts build from a clean checkout, their hashes are recorded, and the image passes the host validation gates G2-G5.

### 当前范围

- The package/kit is a format-1 stub; storage-class/luming builders are not ported; CI is not runnable until the repo is published.

### 下一步

- Port the missing archive builders and re-derive the package/kit for format 2, then dispatch the macOS workflow.

### 证据

- `source`: [Ordered build commands, artifacts and validation gates G0-G5](https://github.com/infinityEX-RSXQ/UniXNU-luming-f2-ci/blob/4bff1b93f409ca1fc8c1ba4403abf8fa37e51888/docs/FIRST-BUILD-PLAN.md)

## 诊断 {#diagnostics}

`planned`

### 硬件与依赖

- A-line marker/reader technique \(32-byte record at PA 0x8C4000000, high-water channel, boot nonce\), panic-screen and boot-log tooling, UEFI Advanced Logger QR, persistent log region.

### 配置

- First-boot diagnostics use the official bring-up stages S1-S7 plus the framebuffer console and a persistent kernel log; no binary marker patching on the format-2 kernel.
- CONFIG\_XNU\_DT\_PANIC\_REGION is on; embedded-panic-log-size is emitted in the ADT, but the /pram node has no converter binding yet.

### 操作步骤

- Record every gate result with command + revision + artifact hash under docs/evidence/.
- If the kernel dies before its console, fall back to the A-line direct-FB marker technique at a single, reviewed site.

### 开发经验

- The A-line diagnostics are a valuable technique but their binary patches are not compatible with a source-built format-2 kernel.
- The format-2 log capture is firmware-menu Advanced Logger QR plus the kernel console/persistent log.

### 完成条件

- Every milestone has reproducible evidence \(source revision, command, artifact hashes, device screen/log for device stages\).

### 当前范围

- Host-only evidence so far; no device log exists for a format-2 luming build.

### 下一步

- Create docs/evidence/ and seed it with the G0 host validation log; extend with G1-G5 and S1-S7 runs.

### 证据

- `source`: [A-line fixes/findings classified for format 2 with landing points](https://github.com/infinityEX-RSXQ/UniXNU-luming-f2-ci/blob/4bff1b93f409ca1fc8c1ba4403abf8fa37e51888/docs/A-FIX-CROSSWALK.md)

</div>
