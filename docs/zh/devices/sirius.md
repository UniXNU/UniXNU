# 小米 8 SE（sirius）

[57UU/UniXNU-sirius](https://github.com/57UU/UniXNU-sirius)

<div v-pre>

Xiaomi Mi 8 SE running the UniXNU source kernel through its own U-Boot UEFI: entry, MMU, timer, PSCI, platform expert and the boot-progress console work on hardware; IOKit is blocked on AppleARMCPU claiming /cpus.

源记录: [porting.toml](https://github.com/57UU/UniXNU-sirius/blob/f269452c36eceb7f91446fccc4c3bed175aaa98e/porting.toml), `f269452c36eceb7f91446fccc4c3bed175aaa98e`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `implemented` |
| [固件与启动](#firmware) | `implemented` |
| [CPU 与中断](#cpu) | `implemented` |
| [内存与 DMA](#memory) | `implemented` |
| [存储与根卷](#storage) | `device-verified` |
| [显示](#display) | `implemented` |
| [输入](#input) | `planned` |
| [GPU](#gpu) | `planned` |
| [网络](#network) | `planned` |
| [音频](#audio) | `planned` |
| [电源](#power) | `planned` |
| [镜像组装](#packaging) | `implemented` |
| [诊断](#diagnostics) | `implemented` |
| [boot-chain](#boot-chain) | `implemented` |

## 配置 {#configuration}

`implemented`

组件: `ArmDTPlatform`, `DarwinBoot`.

### 硬件与依赖

- SoC: SDM710 \(Kryo 360, 2x Cortex-A75 + 6x Cortex-A55\), GIC-500 GICv3, 19.2 MHz Qualcomm XO counter, PSCI over SMC.
- DRAM: 6 GiB model, 2 GiB at 0x80000000 plus 0xfd6c0000 at 0x100000000, 0x17d6c0000 usable.
- Target OS: the unchanged iPad7,1 iPadOS 17.7.11 \(21H461\) restore image, the same kernelcache as fajita and sheng.
- Hardware sources: mainline sdm670.dtsi, the vendor kernel tree and measurements on the phone.

### 配置

- board.toml is format 2 \(schema\_version = 2\) and selects soc\_source = sdm710 and os\_profile = ipados-17.7.11-21H461.
- dts/sirius.dts describes memory, the eight cores and their affinities, and includes the SoC DTSI for the GIC, PSCI and counter.
- configs/sirius\_defconfig keeps the first-console kernel configuration and turns off the profile settings the image does not use yet.
- The prelink roots, slide, early security initializer and Apple device-tree identity come from the OS profile; the board adds sleep-disabled, the product model and the button set.

### 操作步骤

- From a UniXNU checkout: ./unixnu defconfig sirius\_defconfig -D ../UniXNU-sirius.
- Then ./unixnu fetch, ./unixnu status --json and ./unixnu tree; the output is out/sirius/ipados-17.7.11-21H461/sirius/.
- Compile the hardware tree through the payload step \(prototype: dtc -I dts -O dtb -i &lt;soc&gt;/dts dts/sirius.dts\).

### 开发经验

- board.toml gained build-sirius-emmc.py in the archive list next to the USB console entry.
- board.toml lists build-sirius-emmc.py alongside the other archives, because the SDCC1 probe is compiled the same way as the USB console and joins the same force-loaded archive.
- Format 2 replaced the hand-written ADT generator of the legacy port \(scripts/make-sirius-adt.py\) with a board DTS: the payload step compiles the tree and derives kernel.macho.adt from it.
- The arm-io base is derived from the exported nodes, not written by hand: the GIC at 0x17a00000 makes the window start at 0x17000000, which XNU reads as the SoC base.
- The legacy port set ipad\_identity = true; in format 2 the same identity is the OS profile's \[adt\] tables, so the board only states its deviations.

### 完成条件

- status --json resolves the ARM64, sdm710, iPadOS and device layers, prints a non-empty patch order and shows the device package as kits/sirius.
- The compiled hardware tree carries one contiguous memory range equal to payload.dram\_size, eight enabled CPUs and a PSCI method.

### 当前范围

- The SoC profile is new: only the GIC, PSCI, counter and the timer INTID are shared, everything else is still board-local.
- No device-verified configuration has been recorded against a commit of this repository yet; the evidence is the legacy port's handoff document.

### 下一步

- Run status --json and tree against this repository and commit the resulting unixnu.lock.
- Rebuild the payload from dts/sirius.dts and compare the generated ADT with the legacy one before the next hardware boot.

### 证据

- `source`: [Hardware values, the boot chain and the bring-up history of the legacy port, from which this configuration is carried over.](https://github.com/57UU/UniXNU-sirius/blob/f269452c36eceb7f91446fccc4c3bed175aaa98e/docs/HANDOFF.zh-CN.md)

## 固件与启动 {#firmware}

`implemented`

组件: `DarwinBoot`.

### 硬件与依赖

- The device runs sirius-distro \(mainline Linux\) and its boot partition carries U-Boot 2026.07 with EFI\_LOADER, the UEFI boot manager, GOP through vidconsole and EFI block volumes over FAT.
- UniXNU.efi is built on the host by ./unixnu build package; DarwinBoot.efi is built from drivers/DarwinBoot.
- The payload volume goes to the unused vendor partition mmcblk0p80 \(3 GiB\) and is selected by a marker file.

### 配置

- board.toml has no \[firmware\] table: there is no Mu-Silicium firmware and no boot image on this port.
- \[payload\] loader = "payload" makes the generated unixnu.toml load Payloads/DarwinBoot.efi as a \[\[driver\]\] instead of expecting it in the firmware volume.
- scripts/make-uboot-payload.py adds \\EFI\\BOOT\\BOOTAA64.EFI \(UniXNU.efi\) and the DarwinBoot.efi driver to the payload FAT volume.

### 操作步骤

- fastboot flash boot the U-Boot image, fastboot flash vendor the finished payload volume, then select the UniXNU menu entry in U-Boot.
- U-Boot boots UniXNU when /EFI/UniXNU/BOOTUNIXNU exists on the vendor partition and boots Linux otherwise.

### 开发经验

- The eMMC work adds no firmware component: the payload still boots through U-Boot with the same marker file.
- U-Boot's UEFI services are enough for UniXNU, DarwinBoot and XNU: no Mu-Silicium platform port is needed for this board.
- DarwinBoot's GIC-500 pre-configuration \(the iBoot role\) is what lets the kernel pass lockdown and start kexts on this SoC.
- The pre-configuration must not enable the EL1 virtual timer PPI early: on SDM710 that is INTID 19 and it fires before ArmCpu installs its handler.

### 完成条件

- U-Boot starts UniXNU from the FAT volume, the menu lists the xnu entry, and DarwinBoot hands control to the kernel with the device tree, framebuffer and command line.

### 当前范围

- The boot chain is U-Boot specific: it is not reproducible with the Mu-Silicium flow of the other ports and is not covered by ./unixnu firmware or ./unixnu bootimg.

### 下一步

- Keep the U-Boot side \(sirius-distro\) pinned by revision in the handoff document; it is the firmware for this port.

### 证据

- `source`: [Boot-chain diagram, the marker-file boot rule and the DarwinBoot GIC pre-configuration rationale.](https://github.com/57UU/UniXNU-sirius/blob/f269452c36eceb7f91446fccc4c3bed175aaa98e/docs/HANDOFF.zh-CN.md)

## CPU 与中断 {#cpu}

`implemented`

组件: `ArmCpu`.

### 硬件与依赖

- Eight Kryo 360 cores at Affinity1 0x000..0x700, boot CPU cpu0; cpu0-5 Cortex-A55, cpu6-7 Cortex-A75.
- GIC-500 distributor 0x17a00000/0x10000, redistributor 0x17a60000/0x100000, stride 0x20000.
- The EL1 virtual timer is GIC PPI 3 / INTID 19 \(Apple uses PPI 11 / INTID 27\); the SoC counter runs at 19.2 MHz.

### 配置

- dts/sirius.dts lists all eight cores in boot order with their compatible strings; the ADT carries the same order.
- The kernel command line selects the board behaviour: sheng-smp=1, cpus=8, armcpu-self-ipi=1, armcpu-timer-intid=19.
- drivers/ArmCpu/ArmCpu.cpp is the board copy of the component: it adds the non-Apple timer INTID, the /cpus probe counters and the sheng-smp claim path.

### 操作步骤

- Build the kernel, then read the boot-progress TOPO line to confirm the topology and the probe decision.

### 开发经验

- The eMMC bring-up does not touch the CPU selection or the ArmCpu driver; board.toml only gained an archive entry.
- The boot-progress TOPO row confirms the kernel topology on hardware: boot=0 max=7 nums=01234567.
- With sheng-smp=1 the native ArmCpu claims every /cpus nub; without it the kernelcache AppleARMCPU takes the nubs and panics with "CPU configuration in device tree is invalid" because it requires /cpus/max\_cpus.
- AppleARMCPU still wins the nubs at the current stage, which is the open IOKit blocker.

### 完成条件

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU with the board INTID.

### 当前范围

- IOKit attach of the native ArmCpu is not yet proven; the last trusted snapshot shows AppleARMCPU holding /cpus.

### 下一步

- Stop pre-enabling the timer PPI in DarwinBoot, re-read the probe row, and confirm ArmCpu installs its IRQ handler before the timer fires.

### 证据

- `source`: [Timer INTID measurement, the TOPO checkpoint and the AppleARMCPU panic analysis.](https://github.com/57UU/UniXNU-sirius/blob/f269452c36eceb7f91446fccc4c3bed175aaa98e/docs/HANDOFF.zh-CN.md)

## 内存与 DMA {#memory}

`implemented`

### 硬件与依赖

- Usable DRAM 0x17d6c0000 from 0x80000000 \(6 GiB model: 2 GiB then 0xfd6c0000 at 0x100000000\).
- The framebuffer handed over by U-Boot sits at 0x9c000000 \(1080x2240 splash\).

### 配置

- The DTS memory node is a single contiguous range and board.toml repeats the size as \[payload\] dram\_size; the driver refuses a mismatch.
- The ADT receives dram-base, dram-size and the CHRP NVRAM proxy from the payload step.

### 操作步骤

- Read the MEM row of the boot-progress panel and compare it with the DTS range.

### 开发经验

- The eMMC probe maps two register windows \(GCC and SDCC1\) and reads only; the payload memory map is unchanged.
- The single contiguous range is what DarwinBoot's window allocation and the ADT handoff require; the two physical banks are described as one range on purpose.

### 完成条件

- The kernel memory map accounts for every handoff region, and no DMA engine or framebuffer range overlaps the kernel window.

### 当前范围

- DMA and SMMU behaviour is untested: there is no storage or GPU driver yet.

### 下一步

- Capture the kernel's memory map row after the next IOKit break-through and reconcile it with the DTS.

### 证据

- `source`: [DRAM split, framebuffer address and the memory-map checkpoint.](https://github.com/57UU/UniXNU-sirius/blob/f269452c36eceb7f91446fccc4c3bed175aaa98e/docs/HANDOFF.zh-CN.md)

## 存储与根卷 {#storage}

`device-verified`

### 硬件与依赖

- The reference unit is eMMC, not UFS: the UFS transport and its sheng integration points do not apply to this board.
- The original kernelcache is the only source of IOStorageFamily's addresses; its kext images carry no symbol table, so they are derived from the dispatch table itself.

### 配置

- board.toml lists build-sirius-emmc.py \(the SDCC1 probe\) and build-native-emmc.py \(the IOKit block driver\) in \[kernel\] archives; CONFIG\_XNU\_NATIVE\_UFS stays off.
- \[userdata\] carries the 512-byte geometry and the OS/SystemOS windows read from the device's own GPT.

### 操作步骤

- Build the kernel with that archive list: the driver's storage imports are bound at the prelink slide and archived with it.
- Read the evidence off the boot-progress console: the probe prints the GPT rows, the driver logs the block count it publishes.

### 开发经验

- The data path works: ADMA2 reads return EFI PART from LBA 1, the GPT header parses \(entries\_lba=2, count=84, size=128\) and 81 partitions with geometry are listed; boot 1179648..1310719, vendor 11010048..17301503, userdata 17301504..122142686.
- Five conditions had to hold at once: the RCG2 encoding \(CFG=0x2017, M=1, N=0xfc, D=0xfb\), 1.8 V I/O \(the board's vqmmc\), the 32-bit interrupt/error map at 0x30/0x32/0x36, the ADMA descriptor address at 0x58/0x5c rather than 0x00, and cache maintenance \(flush\_dcache64\) because the engine reads memory and not the CPU cache.
- SMMU is not the blocker: the boot chain leaves it disabled \(scr0=0x00230406, bit0=0\) and writing S2CR hung the SoC twice, so the driver only reads SMMU state.
- IOStorageFamily is a kext of the original kernelcache, so the archive form of the driver left IOBlockStorageDevice undefined at the kernel link \(ld: 'a missing vtable usually means the first non-inline virtual member function has no definition'\).
- The prelink slides every component by a constant: extents\[\].va = original + slide for each segment and bindings\[\] carries new\_site = site + slide, so the addresses the driver needs are the kernelcache's plus the slide.
- The dispatch table is identifiable without a live snapshot: of the 190 pinned slot names 176 are kernel exports, exactly one \_\_DATA\_CONST table matches all of them, the other 14 slots point at the kext's own BRK traps, the single constructor that stores table+16 forwards to the actual IOService constructor and the base destructor resolves to IOService's.
- Eleven imports are bound \(dispatch table, metaclass, protected constructor, base destructor and seven methods\); when the prelinked kernel exists the derivation also checks it holds the same constructor at the slid address, so a wrong slide cannot pass.
- The SHNGROOT manifest at userdata LBA 17301504 describes two windows \(OS 17303552+11870275, SystemOS 29175808+6451200\); publishing them as their own IOBlockStorageDevice makes APFS mount disk0, disk1s1 and disk2s1 \(the OS volume DawnUpdate21H461.J120J121J207J208OS\) and bsd\_init completes.
- A thread\_call has a single pending slot: thread\_call\_enter1 neither queues a second call nor preserves the first parameter, so passing requests there silently dropped completions and any caller waiting on such a request hung with the kernel otherwise idle. Requests now sit on a software queue that one drain services.
- Completing a block request from another thread deadlocks this stack the same way the drop did \(reads and blocks frozen at the same point, no error, the drain asleep\), so doAsyncReadWrite completes inline by default.
- The recurring 'Taking non-sleepable RW lock with preemption enabled' panic is the trust cache runtime lock, not a pmap lock: lock 0xfffffff007b3b548 resolves to \_trust\_cache\_rt\_lock and the first caller to \_query\_trust\_cache+0x70. trust\_cache\_runtime\_init\(\) is not compiled into this build, so the lock word reads all zeros \(lck\_rw\_can\_sleep == false\) and lck\_rw\_lock\_shared panics at lock\_rw.c:1400; the driver's heartbeat now mirrors the panic text into the USB ring, which is how the addresses were read.
- With the runtime guarded to answer KERN\_NOT\_FOUND, AMFI refuses every image and the kernel kills launchd with namespace 9 \(OS\_REASON\_EXEC\) code 8 \(EXEC\_EXIT\_REASON\_SECURITY\_POLICY\); recording and clearing that answer with sirius-skip-cs=1 makes exec\_activate\_image return 0, so execve of /sbin/launchd completes.
- The card clock can be raised from the identification rate with the same table U-Boot programs: the RCG divider field holds \(div \* 2 - 1\) and DUAL\_EDGE is set when n \!= m, so the 400 kHz entry \(CXO, div 12, m 1, n 4\) is CFG 0x2017 and 25 MHz \(GPLL0\_EVEN, div 6, m 1, n 2\) is CFG 0x260B; 25 MHz stays inside default speed, 50 MHz would need the CMD6 high-speed switch.
- With the original trust-cache bundle in the payload and the runtime initialised at startup, AMFI answers the exec policy itself: the boot prints execve activate 0 without the sirius-skip-cs bypass line, so the Apple-signed launchd is trusted rather than skipped into.
- The 25 MHz switch reads the GPT signature back at the new rate on device \(the probe prints EMMC clock25=ok\), so the RCG encoding above is confirmed rather than assumed.
- Throughput at the identification clock is about 550 blocks/s \(0x3FC to 0x84A in two seconds\), the expected ceiling for 400 kHz on a four-bit bus, so the 400 kHz setting is a speed problem and not the cause of the stalls.
- The init exec returns 0 and then nothing asks the driver for another block: reads stop at 0x10D \(269 requests, 0x98F blocks\) while the heartbeat keeps counting, so the wait is past the storage stack. The caller side is now instrumented \(sirius-post-exec-trace.patch\): the exec thread-switch state, every new user thread start at thread\_bootstrap\_return, the first pid 1 syscalls with their returns, each bsd\_ast for pid 1 and the first user faults after the exec, all written to the same USB ring and summarised by the heartbeat.
- The caller-side probe closes that question: the pid 1 thread stays in load\_init\_program\_at\_path, inside copyout\(\) of the launchd path, and takes 62.6 million faults in about a minute. The stall is a fault loop in the exec path, not a storage wait.

### 完成条件

- The eMMC registers, GPT and the SHNGROOT windows are correct; APFS mounts the OS volume, bsd\_init completes, init execs /sbin/launchd and execve returns 0.

### 当前范围

- Read-only: the transfer path has no write command and reportWriteProtection\(\) says so.
- After the successful execve of launchd the driver receives no further requests: the remaining wait is past the storage stack, not in it.
- The card clock is still the identification rate \(400 kHz, about 550 blocks/s measured\); nothing raises it to high speed yet.
- The exec policy no longer needs a boot argument: the payload carries the original trust-cache bundle and the kernel initialises its runtime at startup. The sirius-skip-cs bypass is kept in the patch series, unused, in case a future image falls outside the bundle.

### 下一步

- Verify the 25 MHz switch \(sirius\_emmc\_hs=1\) reads the GPT signature back and measure the new block rate; then decide whether the CMD6 high-speed switch to 50 MHz is worth it.
- Keep the trust-cache bundle in step with the OS build when the IPSW changes \(its sha256 is pinned in board.toml \[payload\] trust\_cache\_sha256\).
- Boot the post-exec-probe kernel and read the counters: two SIRIUS user thread start lines mean the exec'd thread was scheduled, and the last init syscall enter without a matching return names the call it never comes back from.
- Raise the SDCC1 clock out of identification speed \(GCC root clock plus the card's high-speed mode\).

### 证据

- `device`: [NativeEmmc starts from bsd\_init, publishes 0x747BFDF blocks of 512 bytes, and IOStorageFamily reads block 0, block 1 and block 2 with 21 sectors \(the 84 GPT entries\) through doAsyncReadWrite; the heartbeat keeps ticking with the transfer count fixed at seven, so the boot ends at the root-device wait. Log in docs/HANDOFF.zh-CN.md.](https://github.com/57UU/UniXNU-sirius/blob/f269452c36eceb7f91446fccc4c3bed175aaa98e/docs/HANDOFF.zh-CN.md)
  Command: <code>fastboot flash vendor sirius-obs.img; fastboot reboot; capture-usb-console.py --duration 240</code>. Revision: `d867b1d6498dc4d0f4ae4e18060762dcae6c5847`.
- `host`: [The kernel links with NativeEmmc in the image \(kernel.macho sha256 372820eb1b2cd9ecee15d769d1296771d0c8141c2681626d54651a62473446b8\); the GitHub macOS runner builds the same archive \(kernel workflow run 40386710258\).](https://github.com/57UU/UniXNU-sirius/blob/f269452c36eceb7f91446fccc4c3bed175aaa98e/docs/HANDOFF.zh-CN.md)
  Command: <code>./scripts/xnu-container.sh run bash -lc './unixnu build kernel --skip-setup -D ../sirius'</code>. Revision: `a47f0d6b4615c3cdebf92102400a1bc302eb6d73`.
- `device`: [APFS mounts disk0/disk1s1/disk2s1, bsd\_init completes, execve of /sbin/launchd prints activate enter, namei 0, 'exec policy answered 1, skipped by boot arg' and finally 'execve activate 0'; the driver then has no transfer in flight and the read count stops at 0x10D, so the remaining wait is past storage.](https://github.com/57UU/UniXNU-sirius/blob/f269452c36eceb7f91446fccc4c3bed175aaa98e/docs/HANDOFF.zh-CN.md)
  Command: <code>fastboot flash vendor sirius-if.img; fastboot reboot; capture-usb-console.py --duration 220</code>. Revision: `bb812428dccd1f676455813ad198ed2bee4a8e3e`.
- `source`: [SDCC1 bring-up, the ADMA2 read path and the GPT parse.](https://github.com/57UU/UniXNU-sirius/blob/f269452c36eceb7f91446fccc4c3bed175aaa98e/package/sirius_emmc.c)

## 显示 {#display}

`implemented`

### 硬件与依赖

- U-Boot hands over a 1080x2240 splash framebuffer at 0x9c000000 through GOP \(vidconsole\).
- The panel is 1080x2244 DSI; there is no backlight or display driver in the kernel yet.

### 配置

- CONFIG\_XNU\_BOOT\_PROGRESS=y links the boot-progress layer; boot-progress=2 on the command line draws the kernel console lines.
- package/Font.h is vendored from Mu-Silicium, so the archive builds without a UEFI checkout.

### 操作步骤

- Build kernel, payload and volume, boot, and read the panel: stage lines, TOPO, PROBE, MEM and panic text.

### 开发经验

- The panel gained an EMMC row \(step, version, capabilities, state, clock, power, clock-branch halts\) next to the USB row, so the storage bring-up is visible without a serial link.
- The USB row \(drawn by this panel\) labels its six values after what they now carry - step, txev, rxev, chars, echo, poll - because they were first wired to register names and had drifted.
- The panel is the readable kernel log of this port: it renders the console, the TOPO/PROBE rows and panic\(\) output.
- Since the panic snapshot patch the panel re-renders at panic time, so the rows are not a stale frame.

### 完成条件

- A known frame appears with correct geometry, and the kernel console and panic output stay readable on the panel.

### 当前范围

- This is a firmware framebuffer text surface, not a Darwin display driver: no IOMobileFramebuffer, no backlight, no modesetting.

### 下一步

- Keep the panel as the diagnostic surface until a display provider exists, and record each new row it prints.

### 证据

- `source`: [Boot-progress panel behaviour, the panic snapshot fix and the geometry of the U-Boot framebuffer.](https://github.com/57UU/UniXNU-sirius/blob/f269452c36eceb7f91446fccc4c3bed175aaa98e/docs/HANDOFF.zh-CN.md)

## 输入 {#input}

`planned`

### 硬件与依赖

- The board has no Home button; volume keys are reported by the button node of the ADT.
- The touch controller is not identified for this unit yet.

### 配置

- board.toml writes \[adt.buttons\] with hold, voldown, volup and home-button-type = 2.

### 操作步骤

- Follow the input guide once a touch controller is known, then select an implementation.

### 开发经验

- The SDCC1 probe does not touch the ADT buttons, so the input row and its hold/voldown/volup mapping are unchanged.
- No input component is selected; the button node exists so that BSPlatform and MobileGestalt read a coherent product.

### 完成条件

- Touches map to the display with stable contacts and the volume keys produce the expected HID reports.

### 当前范围

- No touch support and no IOHIDDevice provider.

### 下一步

- Identify the touch controller from the vendor DTS and the panel firmware.

### 证据

按下一步操作收集证据。

## GPU {#gpu}

`planned`

### 硬件与依赖

- Adreno 616 with the SDM710 GPU firmware; no GPU component is selected yet.

### 配置

- Nothing is configured: the CPU renders the boot-progress panel through the firmware framebuffer.

### 操作步骤

- Follow the GPU guide to evaluate Adreno740/AdrenoMetal for this revision; the A616 is not the A740 the component targets.

### 开发经验

- The Adreno family components in the catalog target the A740 of SM8550; a different implementation would be needed here.

### 完成条件

- GPU submissions complete, fences work and a known image renders.

### 当前范围

- No GPU bring-up has been attempted on this port.

### 下一步

- Decide whether an A616 implementation is in scope after IOKit and storage; do not assume the A740 path applies.

### 证据

按下一步操作收集证据。

## 网络 {#network}

`planned`

### 硬件与依赖

- The Wi-Fi chip of this unit is not identified in the port record yet.

### 配置

- No network component is selected.

### 操作步骤

- Follow the network guide once the chip and its firmware are known.

### 开发经验

- No network work has started; the first console image does not need it.

### 完成条件

- Scanning, association and sustained traffic pass with the selected firmware.

### 当前范围

- No network support at any layer.

### 下一步

- Identify the WCN chip from the vendor DTS and the firmware partition before selecting a driver.

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`planned`

### 硬件与依赖

- No audio path is documented for this unit yet.

### 配置

- No audio component is selected.

### 操作步骤

- Follow the audio guide once the codec and DSP path are known.

### 开发经验

- No audio work has started.

### 完成条件

- Each declared route carries the selected format through playback or capture.

### 当前范围

- No audio support at any layer.

### 下一步

- Inventory the codec and the DSP layout from the vendor tree.

### 证据

按下一步操作收集证据。

## 电源 {#power}

`planned`

### 硬件与依赖

- No suspend/resume path exists; the boot-progress panel is the only power-facing behaviour so far.

### 配置

- board.toml writes \[adt.defaults\] sleep-disabled = 1 so the CPU does not park forever.
- PSCI is declared in the SoC DTSI and used for reset and secondary-core start.

### 操作步骤

- Follow the power guide to add the PMIC and battery controls once the platform expert is stable.

### 开发经验

- The eMMC probe does not vote any RPMH resource; it re-enables the GCC SDCC1 branches that the boot chain had already set.
- Reset works through PSCI \(the stage-3 reset loop proved it\).

### 完成条件

- Declared power controls and battery readings match observations and sleep/resume restores the dependent peripherals.

### 当前范围

- No battery reporting, no CPU frequency policy and no PMIC driver.

### 下一步

- Defer until IOKit and storage are stable; keep sleep-disabled until a resume path exists.

### 证据

- `source`: [PSCI reset evidence and the reason sleep is disabled.](https://github.com/57UU/UniXNU-sirius/blob/f269452c36eceb7f91446fccc4c3bed175aaa98e/docs/HANDOFF.zh-CN.md)

## 镜像组装 {#packaging}

`implemented`

组件: `XnuPrelink`.

### 硬件与依赖

- The payload FAT volume is the flashed artifact of this port; there is no boot.img.
- The prelink inputs \(kernel path, roots, slide, early security initializer\) come from the OS profile; the board does not override them.

### 配置

- \[payload\] sets volume SIRIUSESP, 256 MiB, loader = payload, dram\_size and the kernel command line.
- \[payload.adt\] keeps only chip\_id: the platform seed is supplied per build with --unique-chip-id when the userland stages need it.

### 操作步骤

- ./unixnu build kernel, ./unixnu build package, then bash scripts/build-darwinboot.sh \(or the CI workflow\), ./unixnu build payload, and finally make-uboot-payload.py --output the volume to flash.

### 开发经验

- The eMMC probe ships in the same force-loaded archive as the USB console, so the package list and payload layout are unchanged.
- Format 2 generates kernel.macho.adt from the DTS, so the legacy ADT script is retired; make-uboot-payload.py still finishes the volume because U-Boot needs the EFI binaries inside it.
- scripts/build-xnu-4k-baseline.sh is a copy of the UniXNU script with one board deviation: the boot-progress interlock only requires the source crypto provider.
- The legacy build applied patches/xnu/\*.patch by glob \(56 files\); format 2 applies only what the series list names, and the ARM64 and OS series assume the two files they omit are present. native-smp-secondary.patch sets MAX\_CPUS 8 and Affinity1 core numbering; sheng-platform-power.patch supplies the bsd\_init.c block that zzz-boot-progress.patch quotes as context \(CONFIG\_XNU\_SHENG\_PMGR is off, so its code compiles to nothing\). Both now live in the sdm710 SoC series, which applies before the OS series.
- The first format 2 kernel build on Linux failed at the last patch, zzz-boot-progress.patch, with a bsd\_init.c context mismatch: the missing piece was sheng-platform-power.patch, not the moved native-smp-secondary. With both in the SoC series the whole series applies and the kernel prelinks: kernel.macho 50 MB, \_\_TEXT 0xfffffff007004000, 30 kernelcache components, 69294 bindings.
- The kernel step also runs on Linux through UniXNU's toolchain installer, which builds a patched LLVM, cctools-port ld64, MIG, iig and lzfse. That installer writes /opt/unixnu-linux, /usr/bin shims and distribution packages, so this port runs it inside a Podman image \(containers/xnu-linux/\) and leaves the host untouched. The alternative, Allenwdk/xnu-linux-toolchain, uses the system clang with portable-kalloc-type-builtins.patch and cctools-port, but needs a path-layout adapter for the driver's checks.
- The first flashed build hung on hardware with the entry probe's blue bar and no magenta bar. The cause was a defconfig override, not the kernel sources: CONFIG\_XNU\_NATIVE\_ARCH\_TIMER=n. build-xnu-4k-baseline.sh sets NATIVE\_ARCH\_TIMER=$&\#123;XNU\_NATIVE\_ARCH\_TIMER:-$&\#123;XNU\_ARMCPU:-0&\#125;&\#125;, so the legacy build ran with 1; at 0, architectural-timer-entry.patch compiles the BCM2837 local interrupt router write \(0x40000040 + cpu\*4, Raspberry Pi local peripherals\) into start.s. SDM710 has nothing at that address, and the store aborts before the MMU is on. The defconfig now leaves the ARM64 profile value \(y\) alone and documents why.
- Diagnosis method worth repeating: the legacy kernel from payload-full.img boots with this repository's new UniXNU.efi, DarwinBoot.efi and DTS-generated ADT \(it reaches \_sleh\_irq and panics on the known early timer PPI\), so the EFI side and the ADT are sound and the regression is in the kernel build. Comparing the two kernels' start\_first\_cpu bodies then showed the extra router write as the only semantic difference.
- With the timer override removed the Linux-built kernel boots past the MMU on hardware: the boot-progress panel reports TOPO boot=0 max=7 nums=01234567, the console reaches IOKit \(PE\_init\_iokit, IONVRAM initImageFormat\) and then the CPU takes an IRQ it cannot dispatch. lr 0xfffffff00741754c is \_sleh\_irq+0x70, the same NULL per-CPU handler the legacy kernel hit.
- That IRQ is DarwinBoot's early timer PPI. GIC\_SGI\_PPI\_ENABLE included bit 19, so the EL1 virtual timer fired before ArmCpu::start installed the handler. DarwinBoot now enables SGIs 0..15 only and leaves INTID 19 to ArmCpu \(armcpu-timer-intid=19\), which is what the handoff's next step asked for.
- With the timer PPI left to ArmCpu the next stop was AppleARMPlatform's CPU class: it matches cpu0..cpu7 because IODTPlatformExpert compares IONameMatch by prefix \('cpu' matches 'cpu0'\), starts first, and panics with 'CPU configuration in device tree is invalid' \(its AppleARMCPU.cpp validates max\_cpus, cpu-id, interrupts and function-\* properties that an Apple device tree carries\). The native ArmCpu personality \(IOPlatformDevice, probe score 2000\) did not win that match even after probe\(\) added 40000, so make-uboot-payload.py rewrites the AppleARMCPU IONameMatch from cpu to xpu in the personality plist inside kernel.macho \(equal length, nothing moves\).
- A frozen panel is not proof of a hang: the panel repaints from the timer interrupt, so before ArmCpu enables the timer PPI the last painted second stays on screen while the kernel may still be running. Checkpoints \(armcpu-panic=N, panics at entry/prepareGic/registration/controller/initCPU/registerService\) are what distinguish the two.
- ArmCpu::start then failed inside initDistributor: it re-ran the quiesce sequence \(GICD\_CTLR &amp;= \~3, wait, restore with ARE\) over the state DarwinBoot had already programmed, which clears the group enables and leaves the core with no interrupts at all; the boot then sits in IOKit matching with a frozen panel. The fix keeps the firmware state when GICD\_CTLR already reports affinity routing plus group 1 and only quiesces the SPIs. After it the panel advances \(time=31s, IRQ=1076\) and the kernel reaches bsd\_init with TOPO boot=0 max=7, PROBE calls=17 acc=8 num=7 reg=700 - eight CPUs online.
- The next blocker is AMFI: 'AMFI: No PMGR?' @ConfigurationSettings.cpp:235. The unchanged target AMFI finds the PMGR through IOService::serviceMatching\("ApplePMGRNub"\) + waitForMatchingService, then reads the provider at nub+0x88 and calls its readAon/writeAon slots \(OR bit 2\). The original classes are ApplePMGR \(storage 0x4b8a8\) and ApplePMGRNub \(0x740\); UniXNU/scripts/audit-amfi-pmgr-contract.py pins the exact instructions. amfi\_get\_out\_of\_my\_way=1 does not skip the check. Two routes remain: instantiate the original classes the way UniXNU-sheng does \(OSKextLoadKextWithIdentifier + a generated OriginalPMGRABI.h + a published nub\), or patch the AMFI block in the prelinked kernel.
- AMFI is cleared without touching the target kernel: the nub helpers behind AMFI's readAon/writeAon return 0 when the provider stored at nub+0x88 is NULL, so publishing a real but provider-less ApplePMGRNub satisfies the latch \(read 0, OR 4, write no-op\). package/SiriusPmgr.cpp allocates the class through OSMetaClass::getMetaClassWithName + alloc + init, attaches it to the platform and registers it from the sheng\_pmgr\_run hook in bsd\_init \(CONFIG\_XNU\_SHENG\_PMGR=1, sheng-pmgr=2\), and its build script writes the archive to build/sheng-platform-power/libShengPlatformPower.a because build-xnu-4k-baseline.sh force-loads exactly that path.
- With AMFI satisfied the boot passes bsd\_init and stops at 'Failed to mount root device' @IOKitBSDInit.cpp:984 with 8 CPUs, IRQ=2145, 61 s of live uptime: the kernel now runs to the point where it needs a storage driver and a root filesystem, which this board does not have yet \(no UFS or VirtIO block component, no APFS container on the payload volume\).

### 完成条件

- The kernel prelinks against the pinned 21H461 kernelcache, the payload contains the kernel, the ADT and the DarwinBoot driver, and the flashed volume boots from U-Boot.

### 当前范围

- The kernel step needs macOS and Xcode, or the container image with UniXNU's Linux toolchain; the board script must be re-based on the upstream script when UniXNU changes it.

### 下一步

- Run the new payload once and diff the generated ADT against the legacy one before flashing.
- Boot the prelinked kernel on the phone and record the stage rows; the build side is now reproducible on Linux \(container image, see downloads\).

### 证据

- `source`: [Build and deploy loop, the CI kernel artifact and the payload layout on the vendor partition.](https://github.com/57UU/UniXNU-sirius/blob/f269452c36eceb7f91446fccc4c3bed175aaa98e/docs/HANDOFF.zh-CN.md)

## 诊断 {#diagnostics}

`implemented`

### 硬件与依赖

- The panel and the serial console are the two evidence channels; since the DWC3 CDC console works, the host captures the kernel log directly and photographs are only a fallback.

### 配置

- panic\_screen = true patches the entry probe and the panic screen into the payload kernel.
- boot-progress=2 draws the kernel console lines; debug=0x14e keeps the debug output on.

### 操作步骤

- Record the last checkpoint printed on the panel and in the U-Boot/XNU log for every boot, with the kernel and payload hashes of that run.

### 开发经验

- A register write-and-read-back test is the next diagnostic for the eMMC data phase, because SDHCI\_TRANSFER\_MODE reads back 0x33 after writing 0x13, which separates a write the vendor layer ignores from a command that is never sent.
- The eMMC probe reports every step \(controller registers, the clock tree, the response registers around CMD0/CMD1 and each failure\) into the USB console ring, which is how the card clock and CMD2 findings above were obtained without a photograph.
- The eMMC probe reports through sirius\_usb\_log\_char\(\) straight into the USB console ring, because kernel console output stops reaching the ring long before bsd\_init runs.
- Stage bands \(entry, pre-MMU, panic\) and the TOPO/PROBE/MEM rows replaced the LED and UART guessing of earlier bring-up.
- A panic snapshot forces a panel re-render at panic time; before it, rows could show a stale frame.
- The USB panel row names its fields after what they hold \(step, txev, rxev, chars, echo, poll\) instead of the register names they were first wired to, so a photograph can be read without the source.
- The CDC console hands the console ring to the host once per attach: the pump timing that works \(a short inline poll loop that breaks after the ring is drained\) delivered the 3813-byte boot log on every attempt, while longer loops and a DTR-gated pump delivered nothing, so that timing is treated as load-bearing until the periodic path runs during bsd\_init.
- The post-exec wait is instrumented on the kernel side rather than through the driver: sirius-post-exec-trace.patch prints the exec thread-switch flags, every user thread start \(from thread\_bootstrap\_return, so one line means the exec'd thread never ran and two mean it did\), the first pid 1 syscalls with their returns, every bsd\_ast for pid 1 and the first user faults after the exec, and the eMMC heartbeat prints the counters so one capture answers the question.
- The exec does not stall after activate: load\_init\_program prints the scratch page \(0x1000, the first free page of the init map\), then the init thread is inside copyout\(\) and takes 62,673,044 faults in about a minute while it stays TH\_RUN, so the wait is a tight fault-retry loop, not a sleep.
- PAN is not the cause: the kernel reports PAN implemented with PSTATE.PAN already 0, and CONFIG\_XNU\_NATIVE\_PAN=n compiles copyio's user\_access\_enable\(\)/disable\(\) away anyway, so nothing in this kernel ever sets it.
- The mapping is not missing either: the first fault is a level-1 translation fault, but afterwards pmap\_find\_phys finds the page, AT S1E1W resolves the same address and vm\_fault returns KERN\_SUCCESS, while the retried store faults again as a level-3 permission fault; the raw leaf PTE the pmap holds is now dumped next to ESR/FAR/PC to see which AP bits it carries.
- The pid 1 kernel stack, dumped out of band by the heartbeat and symbolized against mach.development.bcm2837.unstripped, shows \_bcopyout+0x38 under \_load\_init\_program\_at\_path+0x6c under \_bsdinit\_task+0x74, which is the copyout of the launchd path.
- The loop is not limited to the copyout: with the trust-cache bundle back in the payload the exec completes \(execve activate 0, AMFI answers nothing\) and the exec'd thread enters userland at pc 0x100924e50, where it takes 92 million instruction aborts in about a minute on three addresses \(ESR 0x82000007, level-3 translation faults\) without ever issuing a syscall or a single block read; the entry point is right, the code pages are simply not visible to the CPU.
- Both loops have the same shape: vm\_fault opens the page in thread-&gt;map's pmap and returns KERN\_SUCCESS, while the CPU keeps taking the fault. AT S1E1W and pmap\_find\_phys disagree about the physical page behind 0x1000, which points at the CPU running with a pmap that is not the thread's after the exec task switch.
- A payload built without --trust-cache leaves the ring reporting no external trust caches found and AMFI kills launchd with namespace 9 \(OS\_REASON\_EXEC\) code 8; the same kernel with the bundle present reaches execve activate 0 without an exec-policy line, so that panic is a build-argument slip, not a regression.

### 完成条件

- Each claimed milestone has a reproducible command, a matching source and image revision and an accessible result.

### 当前范围

- The CDC console delivers the console ring as it stood when the host attached; making the whole boot stream live is the remaining work.

### 下一步

- Add the boot row and hash triple to every hardware result recorded here, and attach the captured console log rather than a photograph whenever one exists.

### 证据

- `source`: [Entry probe, panic screen, panel rows and the evidence convention of the port.](https://github.com/57UU/UniXNU-sirius/blob/f269452c36eceb7f91446fccc4c3bed175aaa98e/docs/HANDOFF.zh-CN.md)
- `device`: [3813 bytes of kernel log read from /dev/ttyACM0 over the DWC3 CDC console.](https://github.com/57UU/UniXNU-sirius/blob/f269452c36eceb7f91446fccc4c3bed175aaa98e/docs/evidence/sirius-usb-console-20261026-1605.log)
  Command: <code>sudo python3 scripts/capture-usb-console.py --wait 60 --duration 190 --output /tmp/boot.log</code>. Revision: `366abe2948fdb0c1554f7e0b89b731160f4527a4`.

## boot-chain {#boot-chain}

`implemented`

### 硬件与依赖

- Boot chain: ABL -&gt; U-Boot \(boot partition\) -&gt; UEFI -&gt; UniXNU.efi on the vendor partition -&gt; DarwinBoot.efi -&gt; XNU.
- The U-Boot fork github.com/57UU/u-boot branch sirius/v2.0 carries the board support for sdm710-xiaomi-sirius and sirius-build.sh's ENV\_FILE option; the UniXNU boot chain itself is environment text, not source.
- The EDK II package that builds UniXNU.efi, the DXE drivers and DarwinBoot comes from the UniXNU framework's package/ directory.

### 配置

- uboot/src is a submodule of that fork at branch sirius/v2.0 \(shallow\), pinned to a2a847b1a84.
- uboot/unixnu-sirius.env is the board's stock default environment plus unixnu\_boot/unixnu\_check, the bootmenu entry they need and the bootcmd chain; uboot/build.sh builds boot-unixnu.img from the submodule and that file.
- efi/ is a vendored copy of the framework's package/ \(UniXNUPkg, Scripts, build.sh\) taken at f85b5a6, so the repository can build the whole chain on its own.

### 操作步骤

- U-Boot: git submodule update --init --depth 1 uboot/src, then uboot/build.sh \(needs CROSS\_COMPILE and mkbootimg\); fastboot flash boot uboot/boot-unixnu.img.
- Payload: assemble the kernel, efi/ and the EDK II build output with scripts/make-uboot-payload.py --marker, then fastboot flash vendor.
- Recovery: flash sirius-distro's build/boot.img, which ignores the marker and boots Linux.

### 开发经验

- U-Boot needs no source change for this port: with the environment file above, bootcmd runs unixnu\_check first and falls back to the Linux path when /EFI/UniXNU/BOOTUNIXNU is absent on p80.
- mmc 0:50 is a hexadecimal partition number \(0x50 = 80 = the vendor partition\); 0:80 is read as 0x80 = 128 and fails with 'Invalid partition 128'.
- bootflow scan cannot find p80: it stops after the first 30 partitions of each device, so the boot chain uses load/bootefi with the partition spelled out.
- The UniXNU boot chain used to live only in an unversioned scratch directory \(the environment file and boot-unixnu.img\), so the boot image could not be rebuilt from any repository; both the file and the recipe are in uboot/ now.
- U-Boot's fastboot gadget answers the whole getvar dialogue but flashing the vendor partition hangs; the repeated 'request ... was not queued to ep1in-bulk' line is fastboot\_tx\_write\(\) cancelling the IN request before every queue, a dequeue miss rather than a rejected transfer, and stock 2026.07 never received the modern dwc3 ENDTRANSFER/dequeue rework, so that cancel can strand a TRB the controller still owns. Removing the dequeue is the candidate fix.
- Writing the BCB command 'uboot-fastboot' before booting UniXNU does bring the next start into U-Boot's own fastboot on the phone, so entering it is solved while flashing from it is not; the PMIC spare ABL actually reads \(PON\_SOFT\_RB\_SPARE, 0x88f = 0x04 in U-Boot's PID/offset encoding\) still needs CONFIG\_CMD\_PMIC and a verified pmic device name.
- U-Boot's fastboot reports slot a, so the host appends \_a to every partition name it flashes; fastboot\_partition\_alias\_&lt;name&gt;\_a=&lt;name&gt; in the environment maps both spellings onto the real GPT names.

### 完成条件

- uboot/build.sh reproduces boot-unixnu.img from a fresh clone; with the marker in the payload U-Boot starts UniXNU.efi, and without it the phone boots Linux.
- The payload volume holds UniXNU.efi, DarwinBoot.efi, kernel.macho, kernel.macho.trustcache and the marker.

### 当前范围

- The EDK II package is a copy, not a submodule: keeping it in step with the framework is a manual diff of package/.
- The U-Boot submodule is shallow and pinned by commit; rebasing onto a newer sirius/v2.0 is a deliberate update.

### 下一步

- Test the f\_fastboot dequeue removal end to end: after a power cycle, flash boot from U-Boot's own fastboot and, if that works, arm the BCB before booting UniXNU so a hung run comes back to a usable fastboot without the chord.
- Build UniXNU.efi from efi/ once and compare it with the framework's output, so the vendored copy is known good rather than assumed.

### 证据

- `source`: [The build recipe, the four environment lines that add the UniXNU chain, and the two partition/short-scan traps.](https://github.com/57UU/UniXNU-sirius/blob/f269452c36eceb7f91446fccc4c3bed175aaa98e/uboot/README.md)
- `source`: [Provenance of the vendored EDK II package \(framework commit f85b5a6\) and what the payload takes from it.](https://github.com/57UU/UniXNU-sirius/blob/f269452c36eceb7f91446fccc4c3bed175aaa98e/efi/README.md)

</div>
