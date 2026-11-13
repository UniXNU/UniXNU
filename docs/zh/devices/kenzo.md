# Xiaomi Redmi Note 3 \(Kenzo\) Snapdragon 650

[CodeDevB7/UniXNU-kenzo](https://github.com/CodeDevB7/UniXNU-kenzo)

<div v-pre>

Xiaomi Redmi Note 3 \(kenzo\) Snapdragon 650 porting record.

源记录: [porting.toml](https://github.com/CodeDevB7/UniXNU-kenzo/blob/e48ccd6a69acb27a74a6067ef53284aa774d7948/porting.toml), `e48ccd6a69acb27a74a6067ef53284aa774d7948`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `host-verified` |
| [固件与启动](#firmware) | `planned` |
| [CPU 与中断](#cpu) | `implemented` |
| [内存与 DMA](#memory) | `planned` |
| [存储与根卷](#storage) | `planned` |
| [显示](#display) | `planned` |
| [输入](#input) | `planned` |
| [GPU](#gpu) | `planned` |
| [网络](#network) | `planned` |
| [音频](#audio) | `planned` |
| [电源](#power) | `planned` |
| [镜像组装](#packaging) | `planned` |
| [诊断](#diagnostics) | `planned` |

## 配置 {#configuration}

`host-verified`

组件: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`, `DarwinBoot`.

### 硬件与依赖

- Xiaomi Redmi Note 3, codename kenzo; Qualcomm MSM8956; selected profile ipados-17.7.11-21H461.
- Shared SoC feed points to CodeDevB7/UniXNU-msm8956-common at d6845aea8fc3e5c14993b269fcca92927e85fb45, corrected from the connected device's active FDT.

### 配置

- board.toml selects ArmDTPlatform, ArmCpu, SoftwareAES, XnuPrelink and DarwinBoot; kenzo\_defconfig; SoC and OS config fragments; ordered arch, SoC, OS and device patch series.
- \[package\] unixnu is ../UniXNU and \[package.defconfig\] maps ipados-17.7.11-21H461 to kenzo\_defconfig.
- \[bootimg.image\] defines base=0x80000000, pagesize=2048, offsets, and \[\[bootimg.dtb\_node\]\] adds continuous splash buffer.

### 操作步骤

- Resolve board configuration from the UniXNU checkout with unixnu status -D UniXNU-kenzo.
- Run scripts/package.sh --check --os ipados-17.7.11-21H461 from the device repository after required local sources are available.
- Use .github/workflows/dts-adt.yml to compile the board DTS and generate the ADT on a macOS runner; use kernel.yml for the kernel build.

### 开发经验

- The current repository uses format 2 and the shared SoC feed; the older handoff's build workflow description predates the current package interface.
- The package script previously stopped immediately because \[package\].unixnu was absent; after recording the path and profile-to-defconfig mapping, host preflight resolved kenzo\_defconfig and all 59 patches.
- The extracted 86-DTB QCDT set contains reference roots only, but a live device-tree capture now identifies the bootloader-populated MSM8956 MTP tree and matching reference selector DTB 0.
- The kernel-only macOS workflow checks out UniXNU at c34f018aafd6befd5dc93c05a8dccd5bdce6724b and uploads the kernel binary and redacted text logs. Its pre-build helper removes only the optional Sheng PMGR probe hunk from the generic boot-progress patch; it fails closed if the upstream hunk layout changes.
- Run 43170315275 completed successfully on macOS. The final build and prelink produced kernel.macho with SHA-256 43bad77f58e9a3582f330ebb3c70ad4b48d0c350188d17c2bd38ed8454b7650f. The bootstrap pass first reported unresolved mockfs symbols before the configured archive build; the later main kernel link succeeded. The first successful run retained redacted logs but did not yet publish the kernel as an artifact.
- Updated board.toml with verified bootimg parameters \(base 0x80000000, pagesize 2048, offsets\) and continuous splash DTB node; package check passed with 59 patches and kenzo\_defconfig.

### 完成条件

- The pinned SoC source resolves; package preflight writes the selected configuration and patch resolution completes for the selected OS profile.

### 当前范围

- Package preflight, patch resolution, standalone DTS-to-ADT generation and kernel compilation/prelink are host-verified. UEFI firmware, payload, image assembly and device boot are unverified. Firmware repository, image inputs and device seed are not configured.

### 下一步

- Integrate and validate the live-FDT-grounded SoC map in the ADT, then identify a Kenzo UEFI source and verify board firmware paths before attempting a complete package build.

### 证据

- `source`: [Format 2 board selection and package path/defconfig mapping.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/e48ccd6a69acb27a74a6067ef53284aa774d7948/board.toml)
- `source`: [Pinned MSM8956 shared SoC feed at d6845aea8fc3e5c14993b269fcca92927e85fb45.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/e48ccd6a69acb27a74a6067ef53284aa774d7948/feeds.toml)
- `source`: [Local extracted roots identify Qualcomm reference platforms only; the live device FDT selector matches extracted DTB 0.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/e48ccd6a69acb27a74a6067ef53284aa774d7948/evidence/2026-11-12-dtb-inventory.md)
- `source`: [Local XNU patching needed a Sheng-only hunk workaround; builds on /mnt/c failed during atomic header replacement, and the ext4 retry was interrupted before completion.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/e48ccd6a69acb27a74a6067ef53284aa774d7948/evidence/2026-11-12-local-kernel-attempt.md)
- `source`: [Pre-build helper removes only the optional Sheng PMGR progress hunk and fails if its recognized layout changes.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/e48ccd6a69acb27a74a6067ef53284aa774d7948/scripts/prepare-kernel-patches.py)
- `source`: [Compiles Kenzo DTS and generates the OS-specific ADT on macOS Actions using the pinned SoC feed.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/e48ccd6a69acb27a74a6067ef53284aa774d7948/.github/workflows/dts-adt.yml)
- `source`: [Reusable macOS workflow provides a kernel-only build with redacted text logs and no image artifacts.](https://github.com/UniXNU/UniXNU/blob/c34f018aafd6befd5dc93c05a8dccd5bdce6724b/.github/workflows/macos.yml)
- `host`: [Historical pass on WSL/Linux against SoC pin 894aea231e7ac7133b2947777b2dbc89bdd4c6aa \(not the corrected current pin\): wrote config for kenzo\_defconfig, extracted profile IPSW inputs, resolved 59 patches. UniXNU source revision 5a00e20157f3975d155f13ced7593347f9f5bf73.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/e48ccd6a69acb27a74a6067ef53284aa774d7948/evidence/2026-11-12-package-check.md)
  Command: <code>bash scripts/package.sh --check --os ipados-17.7.11-21H461</code>. Revision: `b9280aaa8c6f7fd2622bdc0b28aea8b9c35438a7`.
- `host`: [DTS compiled and generated a 12,888-byte ADT on WSL/Linux against the earlier SoC revision 894aea231e7ac7133b2947777b2dbc89bdd4c6aa; this does not validate the corrected current pin or verify UEFI/device boot. SoC revision 894aea231e7ac7133b2947777b2dbc89bdd4c6aa; UniXNU revision 5a00e20157f3975d155f13ced7593347f9f5bf73.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/e48ccd6a69acb27a74a6067ef53284aa774d7948/evidence/2026-11-12-adt-preflight.md)
  Command: <code>dtc -I dts -O dtb -i &lt;msm8956 DTSI&gt; -o /tmp/kenzo-hardware.dtb dts/kenzo.dts; python3 scripts/make-adt.py --dtb /tmp/kenzo-hardware.dtb --os-profile profiles/os/ipados-17.7.11-21H461/profile.toml --board ../UniXNU-kenzo/board.toml --output /tmp/kenzo.adt</code>. Revision: `b9280aaa8c6f7fd2622bdc0b28aea8b9c35438a7`.
- `host`: [Package check passed with bootimg image parameters and splash DTB node: 59 patches, configuration kenzo\_defconfig, OS profile 21H461.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/e48ccd6a69acb27a74a6067ef53284aa774d7948/evidence/2026-11-13-bootimg-package-check.md)
  Command: <code>bash scripts/package.sh --check --os ipados-17.7.11-21H461</code>. Revision: `dbdc31a1fcbf10ebb7db504806a4cedd9a6a12e3`.

## 固件与启动 {#firmware}

`planned`

### 硬件与依赖

- Kenzo stock Android boot image and extracted device-tree data are present in the sibling kenzo-dump directory.
- Created dedicated CodeDevB7/uefi-kenzo repository providing Platforms/Xiaomi/kenzoPkg, MemoryMapLib, BootShim.S, Resources/Configs/kenzo.toml, and verified kenzo.dtb.

### 配置

- board.toml configures \[firmware\] with dsc = 'Platforms/Xiaomi/kenzoPkg/kenzo.dsc', fd = 'Build/kenzoPkg/&\#123;target&\#125;\_CLANGPDB/FV/SILICIUM\_UEFI.fd', base = 0x9FC00000, size = 0x300000.

### 操作步骤

- Follow the UniXNU UEFI integration guide, then build and inspect the device FD and boot image on a supported host.

### 开发经验

- Established the kenzoPkg platform package in CodeDevB7/uefi-kenzo commit 4f1ceae. Configures BootShim.S with ARM64 header, MemoryMapLib with all 6 Kenzo hardware carveouts, GICv2 at 0x0B000000/0x0B002000, Arch Timer at 19.2 MHz, and SimpleFBDxe on splash framebuffer 0x83000000 \(1080x1920\).
- The user confirms fastboot boot works for temporary boots; boot image header parameters in board.toml and kenzo.toml are unified.

### 完成条件

- Firmware image builds, enters UniXNU, publishes the framebuffer and preserves the documented memory reservations.

### 当前范围

- Firmware volume build and device boot execution remain unverified; full EDK2 submodule integration and cloud build workflow pending.

### 下一步

- Set up GitHub Actions firmware compilation workflow in CodeDevB7/uefi-kenzo to build SILICIUM\_UEFI.fd.

### 证据

- `source`: [Created CodeDevB7/uefi-kenzo containing kenzoPkg DSC/FDF/DEC, MemoryMapLib, BootShim, and kenzo.dtb.](https://github.com/CodeDevB7/uefi-kenzo/commit/4f1ceae74e2d274533da8b7890ecb5c49b6b7a26)
- `source`: [No public Kenzo/MSM8956 EDK2/Mu-Silicium board config was found; near-match SDM660 configs and the lk2nd/MSM8956 references do not provide a verified UEFI path.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/e48ccd6a69acb27a74a6067ef53284aa774d7948/evidence/2026-11-12-uefi-research.md)
- `device`: [Read-only aboot hash recorded. Its binary has a fastboot-boot-unavailable string, but the user reports repeatedly booting boot.img and recovery.img successfully; no such command was run during this task.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/e48ccd6a69acb27a74a6067ef53284aa774d7948/evidence/2026-11-12-aboot-readonly.md)
  Command: <code>adb exec-out su -c 'dd if=/dev/block/mmcblk0p19 bs=1M status=none'</code>. Revision: `0ea480d8cd8f025754767d74cae3a83e84acf960`.
- `device`: [User confirms fastboot boot works for Android boot and recovery images on this device; this is not yet a UEFI payload test.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/e48ccd6a69acb27a74a6067ef53284aa774d7948/evidence/2026-11-12-aboot-readonly.md)
  Command: <code>User report: repeated successful fastboot boot boot.img and fastboot boot recovery.img; exact image hashes/output not captured</code>. Revision: `01be3c57b1e45149acf85aac68860f62dbf22af0`.
- `device`: [Recorded SBL1, TZ and HYP partition hashes; TZ exposes version TZ.BF.3.0.3-00047. No partition was written.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/e48ccd6a69acb27a74a6067ef53284aa774d7948/evidence/2026-11-12-boot-chain-readonly.md)
  Command: <code>adb exec-out su -c 'dd if=/dev/block/mmcblk0p4 bs=1M status=none'; adb exec-out su -c 'dd if=/dev/block/mmcblk0p8 bs=1M status=none'; adb exec-out su -c 'dd if=/dev/block/mmcblk0p10 bs=1M status=none'</code>. Revision: `0ea480d8cd8f025754767d74cae3a83e84acf960`.

## CPU 与中断 {#cpu}

`implemented`

组件: `ArmCpu`.

### 硬件与依赖

- The connected Kenzo reports six online Linux CPUs and soc\_id 266 \(MSM8956\). Its active FDT identifies MSM8956 MTP, qcom,msm-id &lt;0x10a 0&gt;, qcom,board-id &lt;8 0&gt;; these selectors match extracted DTB 0. A draft postmarketOS Kenzo DTS requests revision 1.1 instead and does not match the live tree.
- The captured active FDT reports CPU MPIDRs 0-3, 0x100 and 0x103 as CPUs; 0x101 and 0x102 are NAK placeholders.

### 配置

- The shared SoC DTSI sets /cpus/timebase-frequency to 19200000, observed CPU affinity values 0-3 and 0x100/0x103, PSCI method smc, GICv2 ranges 0x0b000000/0x1000 and 0x0b002000/0x1000, and exports the controller as intc. The debug UART uses captured range 0x078b0000/0x200 and interrupt &lt;0 0x6c 0&gt;.
- The board configuration selects ArmCpu; the SoC fragment enables the GIC and architectural timer.

### 操作步骤

- Compile dts/kenzo.dts with the pinned SoC include using dtc -I dts -O dtb.
- Generate the selected OS/device ADT with scripts/make-adt.py and inspect the output against required XNU nodes.
- After the UEFI path exists, boot XNU and capture per-core entry, timer and IPI logs against the captured Android FDT CPU/GIC data.

### 开发经验

- The active device FDT confirms MSM8956 MTP selector cells, six CPU MPIDRs \(0-3, 0x100, 0x103\), PSCI SMC, the configured GIC ranges, timer tuples and debug UART range/interrupt. The shared SoC DTSI was corrected for MPIDR 0x103 and the UART resources. No XNU secondary-core or IPI bring-up has been measured.

### 完成条件

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU.

### 当前范围

- The capture is the running Android kernel FDT; CPU entry, XNU timer/IPI behavior, and whether a future UEFI payload receives the same nodes are unverified.

### 下一步

- Build and inspect the ADT with the corrected pinned SoC tree, then validate XNU CPU entry, timer and IPI after a UEFI boot path exists.

### 证据

- `source`: [SoC DTSI provides the timebase, interrupt-parent and exported GIC node required by the ADT generator.](https://github.com/CodeDevB7/UniXNU-msm8956-common/commit/d6845aea8fc3e5c14993b269fcca92927e85fb45)
- `source`: [The live device selector matches reference DTB 0; its source memory values are zeroed and bootloader-populated at runtime.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/e48ccd6a69acb27a74a6067ef53284aa774d7948/evidence/2026-11-12-dtb-inventory.md)
- `source`: [The draft Linux DTS requests MSM8956 v1.1, which differs from the live device tree revision.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/e48ccd6a69acb27a74a6067ef53284aa774d7948/evidence/2026-11-12-kenzo-mainline-dts.md)
- `source`: [The board DTS compiled and standalone ADT generation completed on the host; physical XNU CPU/GIC behavior remains unverified.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/e48ccd6a69acb27a74a6067ef53284aa774d7948/evidence/2026-11-12-adt-preflight.md)
- `device`: [Captured the running Kenzo Android FDT; root selectors match DTB 0, and CPU/GIC/PSCI/UART values ground the SoC DTS correction. This does not verify XNU boot.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/e48ccd6a69acb27a74a6067ef53284aa774d7948/evidence/2026-11-12-live-device-tree.md)
  Command: <code>adb exec-out su -c 'toybox tar -C /proc/device-tree -cf - .' (SELinux temporarily Permissive with user authorization, restored to Enforcing)</code>. Revision: `1ebf05c7198156efb47a25aa8b6879b9e338b374`.

## 内存与 DMA {#memory}

`planned`

### 硬件与依赖

- The live active FDT reports /memory/reg &lt;0 0x80000000 0 0x80000000&gt;, matching the current DTS 2 GiB window; Linux reports CPUs 0-5 online.
- Analysis of kenzo-dump/iomem.txt and extracted\_dtb\_0.dtb identifies exact physical firmware carveout nodes and sizes.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for memory and dma.

### 操作步骤

- Follow the memory and dma stage in the porting guide and record the actual commands.

### 开发经验

- The active Android FDT confirms the 2 GiB DRAM range at 0x80000000. All memory gaps in iomem.txt are reconciled to device-tree nodes: other\_ext\_region \(5M at 0x86300000\), modem\_region \(86M at 0x86c00000\), reloc\_region \(23M at 0x8c200000\), and tzapp\_region \(25M at 0x8dd00000\). Upper System RAM from 0x8f600000 to 0xffffffff \(1802 MiB\) is continuous and free.
- Recommended placement for UEFI FD \(FD\_BASE\) is in upper RAM \(e.g. 0x90000000 or 0x9fc00000\), safely above all carveouts.

### 完成条件

- All handoff regions are accounted for and each enabled DMA engine accesses its allocated range with the documented cache policy.

### 当前范围

- Complete DRAM banks, firmware carveouts, DMA addressability, cache policy and SMMU ownership remain unverified on UEFI.

### 下一步

- Verify UEFI FD base placement and reconcile future UEFI memory map against the identified carveouts.

### 证据

- `source`: [The live device selector matches generic DTB 0; the source memory reg is zeroed and bootloader-populated at runtime.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/e48ccd6a69acb27a74a6067ef53284aa774d7948/evidence/2026-11-12-dtb-inventory.md)
- `device`: [Live /memory confirms the 2 GiB physical window. No reserved-memory node is exposed; UEFI carveouts remain unknown.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/e48ccd6a69acb27a74a6067ef53284aa774d7948/evidence/2026-11-12-live-device-tree.md)
  Command: <code>adb exec-out su -c 'toybox tar -C /proc/device-tree -cf - .' (SELinux temporarily Permissive with user authorization, restored to Enforcing)</code>. Revision: `1ebf05c7198156efb47a25aa8b6879b9e338b374`.
- `source`: [Reconciled iomem.txt and extracted\_dtb\_0.dtb carveouts: modem \(86M\), reloc \(23M\), tzapp \(25M\), other \(5M\), and free upper bank 0x8f600000-0xffffffff \(1802 MiB\).](https://github.com/CodeDevB7/UniXNU-kenzo/blob/e48ccd6a69acb27a74a6067ef53284aa774d7948/evidence/2026-11-13-memory-map-analysis.md)

## 存储与根卷 {#storage}

`planned`

### 硬件与依赖

- Identify the storage and root hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for storage and root.

### 操作步骤

- Follow the storage and root stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first storage and root observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Host: register, clock, link and SMMU facts match the board inventory.
- Reads: SCSI capacity, GPT and known blocks are correct; OS/SystemOS windows stay within userdata.
- Root: the configured volume mounts and launchd starts. Persistence: writes survive reboot within the allocated Data region.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required storage and root inputs before implementation.

### 证据

按下一步操作收集证据。

## 显示 {#display}

`planned`

### 硬件与依赖

- BOE NT35532 1080p video mode DSI panel \(1080x1920, 24/32bpp\) with continuous splash framebuffer at 0x83000000 \(40 MiB\).
- Hardware DT node /soc/qcom,mdss\_mdp@1a00000/qcom,mdss\_fb\_primary binds to cont\_splash\_mem at 0x83000000.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for display.

### 操作步骤

- Follow the display stage in the porting guide and record the actual commands.

### 开发经验

- Primary FB and continuous splash memory are verified at 0x83000000 with 40 MiB size. UEFI SimpleFBDxe can bind directly to this pre-initialized buffer \(1080x1920\) without requiring full DSI/MDP5 clock init.

### 完成条件

- A known frame appears with correct geometry and colors, then userland presentation and backlight controls work.

### 当前范围

- Hardware inputs are identified; SimpleFBDxe integration into UEFI FD is pending.

### 下一步

- Configure SimpleFBDxe in the Kenzo UEFI package using framebuffer base 0x83000000, 1080x1920.

### 证据

- `source`: [Identified 1080x1920 BOE NT35532 panel and verified cont\_splash framebuffer base at 0x83000000 \(40 MiB\) for SimpleFBDxe.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/e48ccd6a69acb27a74a6067ef53284aa774d7948/evidence/2026-11-13-memory-map-analysis.md)

## 输入 {#input}

`planned`

### 硬件与依赖

- Identify the input hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for input.

### 操作步骤

- Follow the input stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first input observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive, and buttons produce expected HID reports.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required input inputs before implementation.

### 证据

按下一步操作收集证据。

## GPU {#gpu}

`planned`

### 硬件与依赖

- Identify the gpu hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for gpu.

### 操作步骤

- Follow the gpu stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first gpu observation, its cause when established, and the resulting implementation decision.

### 完成条件

- GPU submissions complete, mapping/fence handling is correct, a known image renders, and the selected Metal client presents it.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required gpu inputs before implementation.

### 证据

按下一步操作收集证据。

## 网络 {#network}

`planned`

### 硬件与依赖

- Identify the network hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for network.

### 操作步骤

- Follow the network stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first network observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Scanning, association, address configuration and sustained receive/transmit traffic pass with the selected firmware.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required network inputs before implementation.

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`planned`

### 硬件与依赖

- Identify the audio hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for audio.

### 操作步骤

- Follow the audio stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first audio observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Each declared route carries the selected audio format through playback or capture and handles start/stop correctly.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required audio inputs before implementation.

### 证据

按下一步操作收集证据。

## 电源 {#power}

`planned`

### 硬件与依赖

- Identify the power hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for power.

### 操作步骤

- Follow the power stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first power observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Declared power controls and battery readings match observations; each claimed sleep/resume transition restores its dependent peripherals.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required power inputs before implementation.

### 证据

按下一步操作收集证据。

## 镜像组装 {#packaging}

`planned`

### 硬件与依赖

- Identify the image assembly hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for image assembly.

### 操作步骤

- Follow the image assembly stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first image assembly observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Kernel and prelink succeed, payload contains all declared inputs, and the boot image matches the bootloader format and size limit.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required image assembly inputs before implementation.

### 证据

按下一步操作收集证据。

## 诊断 {#diagnostics}

`planned`

### 硬件与依赖

- Identify the diagnostics hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for diagnostics.

### 操作步骤

- Follow the diagnostics stage in the porting guide and record the actual commands.

### 开发经验

- The MSM8956 feed lock now pins the live-FDT-grounded SoC correction d6845aea8fc3e5c14993b269fcca92927e85fb45; it corrects CPU MPIDR 0x103 and UART resources. This updates source resolution only and does not add an on-device XNU diagnostic probe.

### 完成条件

- Each claimed milestone has a reproducible command, a matching source/image revision and an accessible result.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required diagnostics inputs before implementation.

### 证据

- `source`: [MSM8956 feed is pinned to the corrected shared SoC revision.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/e48ccd6a69acb27a74a6067ef53284aa774d7948/feeds.toml)
- `source`: [Resolved MSM8956 lock matches feeds.toml at d6845aea8fc3e5c14993b269fcca92927e85fb45.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/e48ccd6a69acb27a74a6067ef53284aa774d7948/unixnu.lock)
- `device`: [Live FDT capture supplied the board evidence used for the SoC feed correction; XNU diagnostics remain unimplemented.](https://github.com/CodeDevB7/UniXNU-kenzo/blob/e48ccd6a69acb27a74a6067ef53284aa774d7948/evidence/2026-11-12-live-device-tree.md)
  Command: <code>adb exec-out su -c 'toybox tar -C /proc/device-tree -cf - .' (SELinux temporarily Permissive with user authorization, restored to Enforcing)</code>. Revision: `1ebf05c7198156efb47a25aa8b6879b9e338b374`.

</div>
