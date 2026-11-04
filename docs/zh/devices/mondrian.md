# Redmi K60 \(mondrian/SM8475\): UniXNU UEFI bring-up

[Emilelu/UniXNU-mondrian](https://github.com/Emilelu/UniXNU-mondrian)

<div v-pre>

Redmi K60 \(mondrian/SM8475\). Format 2 device: the kernel builds and prelinks, the payload and the boot image still need the board ADT and the hardware bring-up.

源记录: [porting.toml](https://github.com/Emilelu/UniXNU-mondrian/blob/c39ff292eee2726c0135f3ba3a98462c9c21d8de/porting.toml), `c39ff292eee2726c0135f3ba3a98462c9c21d8de`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `implemented` |
| [固件与启动](#firmware) | `device-verified` |
| [CPU 与中断](#cpu) | `implemented` |
| [内存与 DMA](#memory) | `implemented` |
| [存储与根卷](#storage) | `planned` |
| [显示](#display) | `planned` |
| [输入](#input) | `planned` |
| [GPU](#gpu) | `planned` |
| [网络](#network) | `planned` |
| [音频](#audio) | `planned` |
| [电源](#power) | `planned` |
| [镜像组装](#packaging) | `host-verified` |
| [诊断](#diagnostics) | `device-verified` |

## 配置 {#configuration}

`implemented`

组件: `ArmDTPlatform`, `ArmCpu`, `XnuPrelink`.

### 硬件与依赖

- Identify the configuration hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for configuration.

### 操作步骤

- Follow the configuration stage in the porting guide and record the actual commands.

### 开发经验

- Migrated from format 1 on 2026-10-28: board.toml is schema\_version = 2 with soc\_source sm8475 and os\_profile ipados-16.6.1-20G81, the SM8475 resources live in UniXNU-sm8475-common, and the board wiring in dts/mondrian.dts.
- Fork audit 2026-10-31: mzyxsl daed6b5d44e3c62978cc0fce4e876ded2a57afc9 imported with provenance. board.toml uses an exact trust-cache list; unixnu.lock matches the explicit SM8475 feed pin. The current payload reader also accepted an exactly equal scalar hash, so the list is schema hardening rather than a proven former build blocker.

### 完成条件

- All source pins resolve; every selected component has a record; status shows the intended overrides and patch order.

### 当前范围

- Hardware inputs and implementation are pending for this board.

### 下一步

- Inventory the required configuration inputs before implementation.

### 证据

- `source`: [schema\_version = 2 resolves through the arch, SM8475, 20G81 and device layers; status reports three components and 83 ordered patches](https://github.com/Emilelu/UniXNU-mondrian/blob/c39ff292eee2726c0135f3ba3a98462c9c21d8de/board.toml)

## 固件与启动 {#firmware}

`device-verified`

### 硬件与依赖

- Identify the firmware and boot hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for firmware and boot.

### 操作步骤

- Follow the firmware and boot stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first firmware and boot observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Firmware image builds, enters UniXNU, publishes the framebuffer and preserves the documented memory reservations.

### 当前范围

- Hardware inputs and implementation are pending for this board.

### 下一步

- Inventory the required firmware and boot inputs before implementation.

### 证据

- `device`: [Darwin 24 loader boots the board every time: green bar from Entry.S, then the upstream probe's blue and magenta bars at the kernel entry and just before the MMU comes on. Confirms the 0x480 boot\_args ABI, ADT handoff and framebuffer are live on hardware. A readable kernel panic followed at k60\_fontscale=4 until the CPU start order was fixed; that panic is gone.](https://github.com/Emilelu/UniXNU-mondrian/blob/c39ff292eee2726c0135f3ba3a98462c9c21d8de/docs/ROUTE-A-18-STATE.md)
  Command: <code>scripts/k60-device.sh boot /mnt/d/Android/k60-ios/boot-darwin24-bc8.img</code>. Revision: `d2af811a6dc9c6225de586e1615ca3824e2edce4`.

## CPU 与中断 {#cpu}

`implemented`

### 硬件与依赖

- Identify the cpu and interrupts hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for cpu and interrupts.

### 操作步骤

- Follow the cpu and interrupts stage in the porting guide and record the actual commands.

### 开发经验

- The SM8475 hardware MPIDRs are flat: 0x000..0x700, Aff1 = core index. That is what the vendor device tree and the Android tree carry, and this firmware rejects every CPU\_ON target outside that table. The 4/3/1 A510/A710/X2 grouping seen in Android's sysfs is L2/L3 cache topology, not MPIDR affinity, and the kernel's cluster-type property \(all 'P'\) is what collapses the eight cores into one topology cluster.
- A starting core is matched to its cpu data by MPIDR &amp; 0xFFFF against the ADT's per-CPU reg, and the same value is the PSCI target, so the ADT must carry the real MPIDRs. The board dts must not override the SoC dtsi's cpu nodes: the ADT generator needs their compatible string and their unixnu,cluster-type.

### 完成条件

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU.

### 当前范围

- The eight cores register and the boot CPU takes its first IPI, but no secondary has yet been seen past its own entry checkpoint on hardware.

### 下一步

- Confirm that each secondary CPU runs its own entry checkpoint and serves a timer on the unit.

### 证据

- `device`: [Android's device tree carries the eight hardware MPIDRs flat, 0x000..0x700, and boots all eight through PSCI; Android's sysfs reports a 4/3/1 A510/A710/X2 split by cache grouping, not by MPIDR. Our board dts had overridden the cpu nodes with packed 0x0-0x3/0x100-0x102/0x200 values, which broke both the firmware target table and the reset vector's match; the override is removed and the SoC dtsi's nodes are inherited again.](https://github.com/Emilelu/UniXNU-mondrian/blob/c39ff292eee2726c0135f3ba3a98462c9c21d8de/dts/mondrian.dts)
  Command: <code>adb shell 'cat /sys/devices/system/cpu/cpu*/topology/physical_package_id; cat /proc/device-tree/cpus/cpu@*/reg'</code>. Revision: `e636e445b621bed4fac0069f3604b87061350a8d`.
- `device`: [The Darwin 22 start order in ArmCpu::start\(\) called initCPU\(\) itself, whose trailing signalCPU\(this\) sent the boot CPU a self IPI before cpu\_machine\_init\(\) had set StartedState, so the first IPI tripped the assertion at cpu\_common.c:586 with cpu\_flags 0x2000 against the expected 0x3000. Switching to the Darwin 24 first-boot path \(pong\_cpu\_first\_boot, pong\_cpu\_first\_boot\_wait, ml\_cpu\_init\_completed\) makes the kernel call initCPU\(\) during processor\_boot\(\). The unit now paints all three probe bars, never reaches the assertion, and walks back to Android on its own through the probe's timed PSCI reset.](https://github.com/Emilelu/UniXNU-mondrian/blob/c39ff292eee2726c0135f3ba3a98462c9c21d8de/drivers/ArmCpu/ArmCpu.cpp)
  Command: <code>scripts/k60-device.sh boot /mnt/d/Android/k60-ios/boot-darwin24-bc8.img</code>. Revision: `d2af811a6dc9c6225de586e1615ca3824e2edce4`.
- `device`: [With the flat targets every CPU\_ON was granted and AFFINITY\_INFO answered 'on', yet no core joined: the arrival flag showed MPIDR 0x81000200 in the reset vector, and the core then hung on start.s's Lskip\_cpu\_reset\_handler because the cpu data it matched \(by its real MPIDR\) had no reset handler yet. The flat targets are the firmware's table; the pairing was the defect.](https://github.com/Emilelu/UniXNU-mondrian/blob/c39ff292eee2726c0135f3ba3a98462c9c21d8de/patches/xnu-ipados18/0247-k60-psci-flat-targets.patch)
  Command: <code>scripts/k60-device.sh boot /mnt/d/Android/k60-ios/boot-darwin24-bc11.img</code>. Revision: `e636e445b621bed4fac0069f3604b87061350a8d`.

## 内存与 DMA {#memory}

`implemented`

### 硬件与依赖

- Identify the memory and dma hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for memory and dma.

### 操作步骤

- Follow the memory and dma stage in the porting guide and record the actual commands.

### 开发经验

- Live serial-6033dbec /memory/reg and rooted /proc/iomem give six RAM banks with a 28 GiB hole at 4..32 GiB. The installed 12 GiB cannot be one XNU window: the longest contiguous unreserved run is 8.65 GiB \(0x840000000..0xa69b78000\).
- The 4 GiB window booted XNU at mem=actual=managed=4096 MiB. An 8 GiB window \(arena equal to the whole 8 GiB\) was refused: DXE occupies part of the arena, so DarwinBoot returned to the UniXNU menu.
- A 8.625 GiB arena \[0x840000000,0xa68000000\) with a 7 GiB window is accepted: loader printed window 0x1c0000000 bytes at pa 0x8400200000 and HANDOFF EXIT RETURN 0. DarwinWindowSizeValid caps a window at 8 GiB, so 12 GiB is not reachable at all.
- Screen trace of the 4 GiB boot: suggestd exits with status 163 signal 0 and ns=0 code=0x0, i.e. a normal exit status, not jetsam or a sandbox denial; disk5s APFS transactions keep completing \(xid 2512, 140/140 finished\), so the Data volume is not stuck.

### 完成条件

- All handoff regions are accounted for and each enabled DMA engine accesses its allocated range with the documented cache policy.

### 当前范围

- The 4 GiB window is the proven configuration; 7 GiB was accepted by the loader but XNU did not start, and 12 GiB is physically impossible as one window. The display/CA prerequisites from the reference project are present in our kernel; the open wall is userland contract/container handling, evidenced by ns=2 SIGABRT/SIGTRAP.

### 下一步

- Read the STR heap lines from the crash-string image to name the failing framework contract \(container path, MobileGestalt, activation\), then fix that one contract; display/CoreAnimation prerequisites are already audited as present.

### 证据

- `host`: [8.625 GiB arena and 7 GiB window; strict v4 round trip PASS; image sha256 8ea52daf4b3e926d4840e13a73fa00c9cadf9b3f1e97e1ececfdaa446e1afc34.](https://github.com/Emilelu/UniXNU-mondrian/blob/c39ff292eee2726c0135f3ba3a98462c9c21d8de/docs/MEASURED-HIGH-WINDOW-2026-11-02.md)
  Command: <code>python3 repair-high-window.py; build-uefi-8g.sh; build-kernel-summary.sh; package-textonly.py</code>. Revision: `48abe35d0a0a57f5fea9f9ba1e570800021ae6b1`.
- `device`: [Loader accepted window 0x1c0000000 bytes at pa 0x8400200000 and HANDOFF EXIT RETURN 0; console output from XNU not yet observed.](https://github.com/Emilelu/UniXNU-mondrian/blob/c39ff292eee2726c0135f3ba3a98462c9c21d8de/docs/MEASURED-HIGH-WINDOW-2026-11-02.md)
  Command: <code>fastboot boot /mnt/e/k60-work/candidates/7g/boot-ios16-7g-textonly.img</code>. Revision: `e06211de59325bbd086c312324bdbf40e21d1045`.

## 存储与根卷 {#storage}

`planned`

组件: `PongUfs`.

### 硬件与依赖

- Identify the storage and root hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for storage and root.

### 操作步骤

- Follow the storage and root stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first storage and root observation, its cause when established, and the resulting implementation decision.
- 2026-10-31 user console reports APFS Data ENOSPC: free\_blocks around 1208 below threshold\_blocks 1310, affecting launchd/usermanagerd/logd\_helper. Latest saved installation is a 256 MiB APFS container in a 258 MiB Data GPT window at unixnu offset 7420 MiB, leaving about 24.502 GiB outside windows. Historical images are checksum/CRC verified but do not establish current live occupancy; capture in root recovery is pending. Read-only inspector validates saved 256/512 MiB images and can back up current Data with second-read hash comparison and optional local directory-allocation summary. No device storage writes or resize performed.

### 完成条件

- Host: register, clock, link and SMMU facts match the board inventory.
- Reads: SCSI capacity, GPT and known blocks are correct; OS/SystemOS windows stay within userdata.
- Root: the configured volume mounts and launchd starts. Persistence: writes survive reboot within the allocated Data region.

### 当前范围

- Hardware inputs and implementation are pending for this board.

### 下一步

- Inventory the required storage and root inputs before implementation.

### 证据

按下一步操作收集证据。

## 显示 {#display}

`planned`

### 硬件与依赖

- Identify the display hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for display.

### 操作步骤

- Follow the display stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first display observation, its cause when established, and the resulting implementation decision.
- Board-level chosen display-scale=3 adapted from XTOM0706 9d1a14f83d1050a042313f30dc9d5b7e80d31f7a. Parsing generated ADTs before/after gives identical properties except random-seed with the current 20G81 profile. Its additional sweet display node is not copied because MiniIOMobileFramebuffer already publishes a disp0 display-subsystem child at runtime.

### 完成条件

- A known frame appears with correct geometry and colors, then userland presentation and backlight controls work.

### 当前范围

- Hardware inputs and implementation are pending for this board.

### 下一步

- Inventory the required display inputs before implementation.

### 证据

按下一步操作收集证据。

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

- Hardware inputs and implementation are pending for this board.

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

- Hardware inputs and implementation are pending for this board.

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

- Hardware inputs and implementation are pending for this board.

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

- Hardware inputs and implementation are pending for this board.

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

- Hardware inputs and implementation are pending for this board.

### 下一步

- Inventory the required power inputs before implementation.

### 证据

按下一步操作收集证据。

## 镜像组装 {#packaging}

`host-verified`

### 硬件与依赖

- Identify the image assembly hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for image assembly.

### 操作步骤

- Follow the image assembly stage in the porting guide and record the actual commands.

### 开发经验

- The three local trees use different userland models: ours keeps an OS+SystemOS read-only APFS union from the unixnu partition; ios-sweet-k60 rewrites a writable HFSX image at build time; UniXNU-pong prepares at run time inside its own static init that becomes PID 1 and then execs launchd. Selected approach: diagnose first and do not replace PID 1, because the launchd chain is already verified and the pong adapter targets Darwin 24 ABI. Our kernel already carries exec\_inject and bindfs, so the pong model remains available if the blocker turns out to need run-time preparation. See docs/USERLAND-ROUTES-2026-11-02.md.
- The kernel links and prelinks on macOS CI. Format 1 run 40631225483 produced 54349824 bytes; format 2 run 40650877574 produced 54419456 bytes at the same slide -0xb9c000 and the same lowest component extent 0xfffffff004426600.
- The 69632-byte difference is a real fix, not noise: the format-1 glob applied zzzzzz-pong-init-scratch-allocation.patch through fuzz and the panic string it adds is absent from that kernel, while the strict format-2 series applies it at its intended place and the string is present. The checked scratch allocation had never reached a qualified kernel before.
- mzyxsl daed6b5 fixes the local prelink helper to merge the OS-profile prelink table and board overrides. A real prelink of the 0238 native kernel succeeded with 32 roots and automatic slide -0xb9c000, 53788672 bytes, SHA-256 bb33682837f1807ef28d385cf09acf94f2749f49b3f7337d22348dcbf6c4b9df. Use --profile/--kit for non-sibling checkouts.

### 完成条件

- Kernel and prelink succeed, payload contains all declared inputs, and the boot image matches the bootloader format and size limit.

### 当前范围

- Hardware inputs and implementation are pending for this board.

### 下一步

- Inventory the required image assembly inputs before implementation.

### 证据

- `host`: [Build kernel succeeded on macOS from this revision: prelink slide -0xb9c000, 54419456 bytes, lowest component extent 0xfffffff004426600](https://github.com/Emilelu/UniXNU/actions/runs/40650877574)
  Command: <code>./unixnu build kernel -D ../UniXNU-mondrian</code>. Revision: `6a10bf5e42ecfad7eed2789cc091287d31009623`.
- `host`: [Route a-18 chain reproduces end to end: kernel 20,872,544 B \(15966fcd\) -&gt; prelink 54,808,576 B -&gt; payload 201,326,592 B -&gt; boot-darwin24-bc6.img. The verifier confirms the kernel slot is the 112-byte shim plus the rebuilt FD, the ramdisk slot is byte-identical to payload.img, and the in-volume kernel.macho matches the built kernel.](https://github.com/Emilelu/UniXNU-mondrian/blob/c39ff292eee2726c0135f3ba3a98462c9c21d8de/scripts/verify-boot-img-payload.py)
  Command: <code>python3 scripts/k60-prelink-darwin24.py &amp;&amp; python3 scripts/verify-boot-img-payload.py --img /mnt/d/Android/k60-ios/boot-darwin24-bc6.img --payload /tmp/k60build/out/mondrian/ipados-18.7.10-22H374/mondrian/payload/payload.img --kernel /tmp/k60build/out/mondrian/ipados-18.7.10-22H374/mondrian/kernel/kernel.macho</code>. Revision: `e636e445b621bed4fac0069f3604b87061350a8d`.

## 诊断 {#diagnostics}

`device-verified`

### 硬件与依赖

- Identify the diagnostics hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for diagnostics.

### 操作步骤

- Follow the diagnostics stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first diagnostics observation, its cause when established, and the resulting implementation decision.
- Imported the source-only offline path/evidence checker from mzyxsl 76552b88441757defce4080a241c2f0ea7464538, preserving current milestone statuses instead of copying its outdated runtime records. scripts/audit-forks.py enumerates public forks and all branches, pins comparison SHAs, and reports candidates without executing or merging fork code. KX SIGKILL records alone do not prove a sender or pressure; 0238 adds committed reason scalars and bounded fallback logging. See docs/FORK-REVIEW.md and docs/BOOT-STALL-2026-10-31.md.

### 完成条件

- Each claimed milestone has a reproducible command, a matching source/image revision and an accessible result.

### 当前范围

- Hardware inputs and implementation are pending for this board.

### 下一步

- Inventory the required diagnostics inputs before implementation.

### 证据

- `device`: [Breadcrumbs turned a silent reset into a located fault: column 1 showed six squares, column 2 zero, column 3 one, which put the death inside ml\_parse\_cpu\_topology\(\). The first carrier \(u64 slots at 0xA73FF000\) was useless because a hung board never returns DRAM, so the markers moved into the framebuffer; 0245 then produced a readable panic on hardware.](https://github.com/Emilelu/UniXNU-mondrian/blob/c39ff292eee2726c0135f3ba3a98462c9c21d8de/patches/xnu-ipados18/0244-k60-breadcrumbs.patch)
  Command: <code>scripts/k60-device.sh boot /mnt/d/Android/k60-ios/boot-darwin24-bc4.img; count the breadcrumb squares</code>. Revision: `e636e445b621bed4fac0069f3604b87061350a8d`.
- `device`: [The upstream entry probe installs on this kernel: stage 1 blue bar, stage 2 magenta bar, stage 3 resets the board through PSCI six seconds after the MMU comes on. The board walked back to fastboot and then to Android by itself, so a hung kernel no longer needs a manual power cycle. The probe's panic screen stays off because it installs code in the padding after panic\(\), at an address fixed for the reference kernel.](https://github.com/Emilelu/UniXNU-mondrian/blob/c39ff292eee2726c0135f3ba3a98462c9c21d8de/docs/ROUTE-A-18-UPSTREAM.md)
  Command: <code>scripts/k60-device.sh boot /mnt/d/Android/k60-ios/boot-darwin24-bc7.img</code>. Revision: `350d1c57c86d2fc562c7fa7529271fdae3af95bc`.

</div>
