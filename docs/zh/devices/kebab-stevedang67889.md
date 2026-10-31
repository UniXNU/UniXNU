# OnePlus 8T \(stevedang67889\)

[stevedang67889/UniXNU-kebab](https://github.com/stevedang67889/UniXNU-kebab)

<div v-pre>

OnePlus 8T \(KB2000\). Firmware, menu and payload volume work, and the kernel walks the whole kernel\_bootstrap\_thread into bsd\_init: IOKit initialisation, startup step 16, the commpage, mac\_policy, vnguard, dtrace, sdt, mbuf\_tag\_init and the rest all pass. What still holds it is the interrupt controller: ArmCpu::mapGic\(\), prepareGic\(\) and enableGic\(\) live in the prelinked AppleARMCPU kext, so a bring-up kernel that skips kext loading and IOKit matching has no interrupts at all - with IRQs masked every allocation that wants to sleep hangs, and with them unmasked the first IRQ stops the boot. The ADT also handed the GIC and timer window offsets that were made absolute by mistake, which double-mapped both; that is fixed.

源记录: [porting.toml](https://github.com/stevedang67889/UniXNU-kebab/blob/8b5295d81c61cef68a5dc521cf08695aa36f5d01/porting.toml), `8b5295d81c61cef68a5dc521cf08695aa36f5d01`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `implemented` |
| [固件与启动](#firmware) | `device-verified` |
| [CPU 与中断](#cpu) | `implemented` |
| [内存与 DMA](#memory) | `implemented` |
| [存储与根卷](#storage) | `planned` |
| [显示](#display) | `device-verified` |
| [输入](#input) | `device-verified` |
| [GPU](#gpu) | `planned` |
| [网络](#network) | `planned` |
| [音频](#audio) | `planned` |
| [电源](#power) | `planned` |
| [镜像组装](#packaging) | `device-verified` |
| [诊断](#diagnostics) | `device-verified` |

## 配置 {#configuration}

`implemented`

组件: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`, `DarwinBoot`.

### 硬件与依赖

- UniXNU format 2 device repository
- UniXNU-sm8250-common SoC feed pinned in feeds.toml
- iPad7,1 17.7.11 21H461 donor IPSW

### 配置

- board.toml schema\_version = 2
- components include ArmDTPlatform, ArmCpu, SoftwareAES, XnuPrelink and DarwinBoot
- kernel.prelink slide -0x1000000 against kernelcache f18b4df865405f2a287b84977d7aca745e056d656d9fc9df1662970ce2969de7
- kernel archives add build-arm-driver.py ArmDTPlatform and ArmCpu

### 操作步骤

- Clone UniXNU, UniXNU-kebab and UniXNU-sm8250-common as siblings
- Run ./unixnu fetch and ./unixnu defconfig kebab\_defconfig
- ./unixnu status --json reports the resolved pins

### 开发经验

- The format 2 builder exports an arm-io child only for device tree nodes that carry a unixnu,adt-name property, so an untagged tree yields an empty arm-io and the kernel has no interrupt controller.
- The boot image has to use the phone own device tree; the tree shipped with Mu-Silicium lacks cont\_splash\_region@9c000000 and ABL then keeps the panel dark.
- Two inputs are not in any repository and must be captured per handset: the live device tree from /sys/firmware/fdt and the kernel built on a macOS runner. proprietary-files.txt names both with their hashes and consumers.
- Every change to a file an area owns has to update that area findings or evidence in the same commit; the catalog workflow fails otherwise and names the path.
- The device summary is what the generated page shows first, so it has to name the current stage rather than the first blocker found.
- The README status table names the current PE\_init\_iokit to bsd\_init gap and links the 32-checkpoint capture in docs/log-capture.md.
- The shared ADT generator gained platform\_node\(\) for nested \[adt.\*\] nodes and reads unixnu,cluster-type \(E or P\) from a cpu node, so kebab's 1+3+4 clusters can be described without a device-side patch.
- The ADT generator emits a plain phandle property, while IOKit registers and looks up AAPL,phandle. Until the generator maps one to the other, no device tree node is reachable by phandle inside XNU.

### 完成条件

- Every source pin resolves and the selected components have records; unixnu status reports the intended overrides.

### 当前范围

- No device-side repository record was published before this file; the entries below are the first complete record.

### 下一步

- Keep the record current as firmware and kernel patches land.

### 证据

- `source`: [Format 2 board description with the SM8250 SoC feed and the five components above.](https://github.com/stevedang67889/UniXNU-kebab/blob/8b5295d81c61cef68a5dc521cf08695aa36f5d01/board.toml)
- `source`: [Thirteen areas with measured facts; python3 scripts/porting-record.py check --device ../UniXNU-kebab passes.](https://github.com/stevedang67889/UniXNU-kebab/blob/8b5295d81c61cef68a5dc521cf08695aa36f5d01/porting.toml)

## 固件与启动 {#firmware}

`device-verified`

组件: `DarwinBoot`.

### 硬件与依赖

- Mu-Silicium Platforms/OnePlus/kebabPkg
- Phone's own live device tree as the boot image DTB
- boot\_a, 96 MiB, header v2 with 4096-byte pages

### 配置

- FD\_BASE 0x9FC00000, FD\_SIZE 0x4600000 \(3 MiB firmware volume plus a raw payload region at 0x00300000\)
- UFSDxe removed from DXE.inc; SEC disables the APSS watchdog at 0x17C10008
- ScmDxeLA and SdccDxe are included; TzDxeLA is commented out
- Framebuffer PCDs 1080x2400x32
- unixnu bootimg passes the live DTB; ABL refuses images without the splash region node

### 操作步骤

- Build firmware with ./unixnu build firmware -D ../UniXNU-kebab --uefi &lt;Mu-Silicium&gt;
- ./unixnu bootimg -D ../UniXNU-kebab --uefi &lt;Mu-Silicium&gt; --fd &lt;SILICIUM\_UEFI.fd&gt; --dtb &lt;live.dtb&gt; --ramdisk none
- fastboot flash boot\_a &lt;image&gt;; fastboot reboot

### 开发经验

- ABL hands the framebuffer over only when the boot image carries the phone's own device tree; the tree shipped with Mu-Silicium has no cont\_splash\_region@9c000000 and the panel stays black.
- A payload file inside the firmware volume is impossible: the FFS size field is 24 bits, so the 64 MiB payload is a raw FDF region instead.
- FrameBufferSerialPortLib handled newline and carriage return but ignored form feed, so DarwinBoot's clear screen did nothing and the left half of every log line was cut off.
- The payload builder injects the nodes XNU looks up by property \(gic with interrupt-controller master, a one-cell redistributor stride, virtual-timer-intid, a timer node, pram and the panic log size\); without them the kernel stops before PE\_init\_platform returns.
- KebabBootLog reads the 32 checkpoint bytes at 0xB9000010, prints the set list and clears the flags; CacheMaintenanceLib flushes the clear.
- The current firmware has SCM and SDCC but no UFS block device: UFSDxe is removed for the vendor assert, TzDxeLA is disabled and SdccDxe does not replace UFS.

### 完成条件

- Firmware boots from boot\_a, the menu is rendered on the panel, the keys navigate it and the log is readable.

### 当前范围

- USB is not brought up in the firmware; the only log transport is the panel.

### 下一步

- Publish a firmware image revision alongside each kernel change.

### 证据

- `device`: [UniXNU menu on the KB2000 panel listing the payload entry, keys working, full firmware and DarwinBoot log readable.](https://github.com/stevedang67889/UniXNU-kebab/blob/8b5295d81c61cef68a5dc521cf08695aa36f5d01/docs/bring-up.md)
  Command: <code>fastboot flash boot_a out/darwin-boot.img; fastboot reboot</code>. Revision: `97f6fea12dae49a1bbc30ccd22c098b82b97dbe4`.

## CPU 与中断 {#cpu}

`implemented`

组件: `ArmCpu`.

### 硬件与依赖

- Eight cores at MPIDR affinities 0x000 through 0x700
- PSCI method smc
- 19.2 MHz timebase

### 配置

- cpus node with one cpu per affinity and state running/waiting
- timebase-frequency 0x124f800
- arm-io/gic interrupt-controller master, virtual-timer-intid 27

### 操作步骤

- Install the kernel entry probe with entry\_probe\_reset\_delay and a symbol to bisect
- Read the stage bars: blue is kernel entry with the MMU off, magenta is just before the MMU is on
- A reboot six seconds after the bars proves the probe point was reached
- Run scripts/patch-xnu-log-probe.py on a private kernel copy, build the payload and read the 32 flags in KebabBootLog

### 开发经验

- The kernel is entered and enables the MMU once ExitBootServices is allowed to finish; the timed reset after the MMU enable proves it.
- With PE\_create\_console replaced by a ret, the kernel completes PE\_init\_printf, PE\_init\_cpu, machine\_conf, vm\_mem\_bootstrap, console\_init, sched\_init and kernel\_thread\_create, and reaches the bootstrap thread with its first context switch.
- \_machine\_startup is four instructions and tail-branches into \_kernel\_bootstrap, so a probe placed after that call can never fire; earlier readings of it measured nothing.
- \_arm\_init calls PE\_init\_platform twice and kernel\_startup\_initialize\_upto is called once per init stage, so a probe needs entry\_probe\_reset\_occurrence when the call appears more than once.
- The kernel clears the screen when it creates the console, so a black panel after the stage bars does not mean the kernel died.
- The kernel removes its identity map in arm\_vm\_init and the physical aperture starts at gPhysBase. The ring is below both window configurations' kernel base, so the stub uses ml\_phys\_write\_byte, which maps the unmanaged page through the uncached CPU copy window instead of phystokv.
- A call-site stub can save x0-x8 and LR, call ml\_phys\_write\_byte, restore and tail-call the original callee, so arguments and return address are unchanged.
- The 32 calls between PE\_init\_iokit and the first bsd\_init locks name the gap: the last set byte is the call entered, and the next unset byte is the callee that did not return.
- The 4 GiB window loads the kernel at physical 0x20007C000 \(base A, measured by a temporary DarwinBoot colour band\). A one-stub BSS write at 0x7B281B0, dc cvac and PSCI reset reboots, but the next reader still sees no prefix, so normal DRAM does not carry the flag across the reset; pram 0x17F00FE0 is the persistent page.
- The 2026-10-29 checkpoints reach IOLibInit, OSlibkernInit, IOMachPortInitialize, the OSSymbol interners, OSSet::withObjects, interruptAccountingInit and the IOPlatformExpertDevice allocation on the boot CPU.
- cpus=1, and ret patches on ml\_wait\_max\_cpus, kperf\_init\_early and platform\_stall\_panic\_or\_spin, do not move the PE\_init\_iokit stall.

### 完成条件

- Every enabled CPU reaches its entry checkpoint and timer and IPI handling works on each enabled CPU.

### 当前范围

- Only the boot CPU runs; secondary cores are not started and \_machine\_conf does not complete.

### 下一步

- Confirm the pram one-stub at 0x17F00FE0 \(out/prammap-boot.img\), then move the 32 checkpoint bytes from the ring to pram and read last/next in KebabBootLog.

### 证据

- `device`: [Reboot six seconds after the stage bars with the probe after the MMU enable; no reboot with the probe after \_machine\_conf, so the kernel reached \_machine\_startup and stopped inside it.](https://github.com/stevedang67889/UniXNU-kebab/blob/8b5295d81c61cef68a5dc521cf08695aa36f5d01/docs/bring-up.md)
  Command: <code>flash the reset-probe image and observe the panel</code>. Revision: `97f6fea12dae49a1bbc30ccd22c098b82b97dbe4`.
- `source`: [Resolves 32 call sites, verifies every original bl, places 80-byte stubs in \_\_TEXT\_EXEC padding and checks each branch.](https://github.com/stevedang67889/UniXNU-kebab/blob/8b5295d81c61cef68a5dc521cf08695aa36f5d01/scripts/patch-xnu-log-probe.py)

## 内存与 DMA {#memory}

`implemented`

组件: `ArmDTPlatform`.

### 硬件与依赖

- DRAM banks 0x80000000+0x39900000, 0xC0000000+0xC0000000 and 0x200000000+0x200000000
- DarwinBoot window request of 3 GiB

### 配置

- dram-base, dram-size and darwinboot-memory-size all 0xC0000000
- /memory node in dts/kebab.dts restricted to the 0xC0000000 window
- DarwinBoot skips conventional-memory runs below 0x40000000

### 操作步骤

- Build the payload so the generated ADT carries the window, then boot and read the DarwinBoot log line with the kernel virtual and physical base

### 开发经验

- The kernel first-fit allocated at 0x7D000 and faulted during relocation; loading above 0x40000000 moved it to DRAM.
- A 256 MiB window leaves too little room in arm\_vm\_init's early I/O page-table reservation for the 0x2300000-byte framebuffer region; only after the window became 3 GiB did the kernel reach the MMU enable and \_machine\_startup.
- The physical aperture starts at gPhysBase and maps upward, so the 0xB9000000 ring has no phystokv mapping. ml\_phys\_write\_data falls back to the uncached CPU copy window for this unmanaged page, which is how the stage-1 stub writes it.
- The 4 GiB test window put the kernel physical base at 0x20007C000, measured by a temporary DarwinBoot colour band; the 3 GiB build's 0xC007C000 is not the current local base.
- Normal DRAM does not carry the checkpoint flags across the reset: the 0xB9000010 ring, 0xC0001000/0x200001000 and a real \_\_DATA BSS page all lose the byte after a reboot. The pram page at 0x17F00FE0 is the reset-persistent page; UEFI must map it before it can read the flags.
- The ADT handed to the kernel is 13980 bytes with 21 nodes, 122 properties and maximum depth two, so a tree that small cannot make a walk loop; a stall inside IODeviceTreeAlloc would be a lock or a fault.
- SecureDTIsLockedDown\(\) is false because the ADT sits physically after the kernel, so arm\_vm\_prot\_init does not treat it as EXTRADATA; the tree stays mapped through the boot\_args window up to topOfKernelData.

### 完成条件

- All handoff regions are accounted for and each enabled DMA engine uses the documented cache policy.

### 当前范围

- Only 3 GiB of the 12 GiB is handed to the kernel; no DMA or SMMU work is done yet.

### 下一步

- Widen the window or describe all three banks once the platform expert completes.

### 证据

- `device`: [DarwinBoot reports the kernel at physical 0xC007C000 inside the 3 GiB window, and the kernel reaches the MMU enable.](https://github.com/stevedang67889/UniXNU-kebab/blob/8b5295d81c61cef68a5dc521cf08695aa36f5d01/docs/bring-up.md)
  Command: <code>flash the entry-probe image and read the DarwinBoot physical base line</code>. Revision: `97f6fea12dae49a1bbc30ccd22c098b82b97dbe4`.

## 存储与根卷 {#storage}

`planned`

### 硬件与依赖

- UFS host 0x1D84000
- userdata first\_lba 4748320, last\_lba 61748338 at 4096-byte blocks

### 配置

- UFSDxe removed from the firmware because the vendor driver asserts; ConfigurationMapLib sets EnableUfsIOC = 1, which removes the assert but still yields no block device

### 操作步骤

- Not started; the kernel has no storage driver yet

### 开发经验

- The vendor UEFI UFS driver asserts in UFS.c and must stay out of the firmware image.
- With no block device, the firmware cannot expose the root volume and the kernel cannot mount anything.
- DXE.inc includes ScmDxeLA and SdccDxe, comments out UFSDxe and TzDxeLA. The phone has no SD slot, so SDCC does not replace UFS; the missing UFS block device is still what blocks userdata/root.

### 完成条件

- The root volume mounts read-only from the OS window and Data is persistent.

### 当前范围

- No storage driver in firmware or kernel; userdata geometry is recorded but unverified against this handset.

### 下一步

- Decide between a native UFS driver and a RAM root image for the first userspace milestone.

### 证据

按下一步操作收集证据。

## 显示 {#display}

`device-verified`

组件: `ArmDTPlatform`.

### 硬件与依赖

- Samsung AMB655X panel oplus20828samsung\_amb655x\_1080\_2400\_cmd
- Framebuffer base 0x9C000000, 1080x2400, row 4320 bytes, 32 bpp

### 配置

- PcdFrameBufferWidth 1080, PcdFrameBufferHeight 2400, PcdFrameBufferColorDepth 32
- DarwinEnter paints the hand-off band from the GOP base and flushes it from the data cache

### 操作步骤

- Read the DarwinBoot video line, then confirm the panel shows text at the expected coordinates

### 开发经验

- The stride used while drawing a glyph row must remain \(FB\_WIDTH - FONT\_WIDTH \* FontScale\) \* FB\_BPP; using a full scanline there shears every glyph.
- The framebuffer is a DSC command-mode panel; the firmware console renders correctly with the inherited GOP.
- PE\_create\_console blocks in ml\_io\_map\_wcomb while it maps the framebuffer, so the bring-up kernel replaces it with a ret; vcattach and vc\_progress\_initialize block on the same mapping and are patched the same way.
- initialize\_screen is the next call after PE\_init\_iokit in kernel\_bootstrap\_thread; it reaches the same framebuffer mapping that blocks PE\_create\_console, so it is the next checkpoint.

### 完成条件

- The kernel presents the boot logo and later the SpringBoard frame through the controller or GOP.

### 当前范围

- Only the firmware text console is verified; the kernel has no display driver, so kernel output is limited to the entry probe bands.

### 下一步

- Add a kernel-side framebuffer console or the native display driver once \_machine\_conf completes.

### 证据

- `device`: [Menu, firmware log and DarwinBoot log render at 1080x2400 with correct geometry.](https://github.com/stevedang67889/UniXNU-kebab/blob/8b5295d81c61cef68a5dc521cf08695aa36f5d01/docs/bring-up.md)
  Command: <code>boot the firmware and read the panel</code>. Revision: `97f6fea12dae49a1bbc30ccd22c098b82b97dbe4`.

## 输入 {#input}

`device-verified`

### 硬件与依赖

- Synaptics S3908 touch controller on i2c 0xa94000, address 0x4B, reset GPIO 38, IRQ GPIO 39
- Power and volume keys

### 配置

- Volume and power keys drive the UniXNU menu

### 操作步骤

- Move the selection with the volume keys and confirm with the power key

### 开发经验

- The keys navigate the menu and start the payload, which is enough to drive the bring-up without touch.

### 完成条件

- Touch reports contacts under the kernel and the menu is usable without the physical keys.

### 当前范围

- Only the UEFI key path is verified; touch has no driver in firmware or kernel.

### 下一步

- Port the S3908 driver once the kernel reaches the driver-matching stage.

### 证据

- `device`: [Menu selection and confirmation work with the physical keys.](https://github.com/stevedang67889/UniXNU-kebab/blob/8b5295d81c61cef68a5dc521cf08695aa36f5d01/docs/bring-up.md)
  Command: <code>boot the firmware and press volume and power</code>. Revision: `97f6fea12dae49a1bbc30ccd22c098b82b97dbe4`.

## GPU {#gpu}

`planned`

### 硬件与依赖

- Adreno 650 with GMU firmware from the phone's own Android partitions

### 配置

- No GPU driver is built or loaded

### 操作步骤

- Not started

### 开发经验

- No GPU work has been attempted; the bring-up stops before IOKit matching.

### 完成条件

- A Metal or OpenGL ES surface is presented through the available scanout path.

### 当前范围

- No GPU firmware is collected and no driver component exists.

### 下一步

- Collect the Adreno firmware after the platform expert completes.

### 证据

按下一步操作收集证据。

## 网络 {#network}

`planned`

### 硬件与依赖

- WCN6855 Wi-Fi and Bluetooth combo

### 配置

- No network driver is built or loaded

### 操作步骤

- Not started

### 开发经验

- No network work has been attempted.

### 完成条件

- Association, DHCP and packet transfer work under the kernel.

### 当前范围

- Firmware, calibration data and driver are all missing.

### 下一步

- Defer until userspace starts.

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`planned`

### 硬件与依赖

- WCD9385 codec and the ADSP firmware

### 配置

- No audio driver is built or loaded

### 操作步骤

- Not started

### 开发经验

- No audio work has been attempted.

### 完成条件

- Playback and capture work through the DSP.

### 当前范围

- DSP firmware and driver are missing.

### 下一步

- Defer until userspace starts.

### 证据

按下一步操作收集证据。

## 电源 {#power}

`planned`

### 硬件与依赖

- PM8150 and PM8150B PMICs
- APSS watchdog at 0x17C10008

### 配置

- SEC disables the APSS watchdog so a fault leaves the panel readable

### 操作步骤

- Not started beyond the watchdog disable

### 开发经验

- Without the watchdog disable a fault reboots the phone before the log can be read.

### 完成条件

- Regulators, clocks and battery reporting match the board.

### 当前范围

- No PMIC driver; only the watchdog is handled.

### 下一步

- Defer until the kernel reaches the platform driver stage.

### 证据

按下一步操作收集证据。

## 镜像组装 {#packaging}

`device-verified`

组件: `XnuPrelink`, `DarwinBoot`.

### 硬件与依赖

- XNU built from source on a macOS runner against kernelcache f18b4df865405f2a287b84977d7aca745e056d656d9fc9df1662970ce2969de7
- iPadOS 17.7.11 21H461 userland image
- 64 MiB payload FAT image

### 配置

- header\_version 2, pagesize 4096, kernel\_offset 0x8000, tags\_offset 0x100, dtb section from the live device tree
- payload as a raw FDF region at 0x00300000, published by KebabRamDisk over BlockIo
- kernel args -v keepsyms=1 kt\_fixed\_zones=120

### 操作步骤

- ./unixnu build payload, then run scripts/pack-payload-mbr.py on the FAT image, point the FDF FILE region at the wrapped image, rebuild the firmware and run ./unixnu bootimg
- ./unixnu bootimg --uefi &lt;Mu-Silicium&gt; --dtb desktop-kebab.dtb --ramdisk none verifies the gzip payload, firmware volume and appended DTB before flashing

### 开发经验

- The payload cannot be an FFS file, and RamDiskDxe refused the buffer with EFI\_INVALID\_PARAMETER, so KebabRamDisk publishes the region as a BlockIo device with a device path for PartitionDxe.
- unixnu bootimg needs the patched mkbootimg call that passes the DTB for header version 2.
- The payload builder now injects the device tree nodes XNU looks up by property, and scripts/patch-func-ret.py replaces a single kernel function with a ret when one call has to be skipped without a kernel rebuild.
- The exported firmware patch keeps every edited firmware file, including the two kebab drivers and the BootShim, so the tree can be rebuilt from the patch alone.
- The bring-up kernel is reproducible: the CI Mach-O with a ret in \_PE\_create\_console, \_vcattach, \_vc\_progress\_initialize and \_PE\_get\_default is sha256 db666dcf2b930fac1ed5da95accf2a4ed5f9e6c780ab7445284bbcbeedcc7d96, and the entry probe refuses to apply unless that base is un-probed.
- The payload FAT volume has to be wrapped in an MBR disk before it becomes the FDF FILE region: a type 0x0c partition at LBA 2048 plus a 1 MiB pad, written by scripts/pack-payload-mbr.py.
- The working boot image DTB is desktop-kebab.dtb \(sha256 8ba6ed34b8396102eac4d95769c56317aece50cf95b69cd3d98aa8353b27f293\); the 11 MiB raw live dump carries trailing data past the FDT totalsize and fails the bootimg check.
- The bring-up kernel grew to six ret patches on 2026-10-30: PE\_create\_console, vcattach, vc\_progress\_initialize, PE\_get\_default, initialize\_screen and kperf\_init\_early \(sha256 9531eef048f30eba31d159194260e19044fec25b9cd605cbbb2c82ca997d1461\).
- The 2026-10-30 evening bring-up kernel grew to eight ret patches: the six above plus vm\_commpage\_init and vm\_commpage\_text\_init \(sha256 63ac20f91988a04f96396408f1d0b1248784d805a5c2e0eee3632082cbef49f4\), used to bisect past the commpage stall.
- The 2026-10-31 bring-up kernel is kernel-bsd9: sixteen patches on top of the source build - ret for PE\_create\_console, vcattach, vc\_progress\_initialize, PE\_get\_default, initialize\_screen, kperf\_init\_early, vm\_commpage\_init, vm\_commpage\_text\_init, OSKextLog, OSKextRemoveKextBootstrap, machine\_lockdown, kernel\_list\_tests, kernel\_do\_post and PE\_lockdown\_iokit, mov x0,\#0 over the OSKext::copyKexts call in loadSecurityExtensions, and a nop over the ml\_set\_interrupts\_enabled\(1\) call in kernel\_bootstrap\_thread.
- The 2026-10-31 evening bring-up kernel is kernel-bsd11: kernel-bsd9 plus a ret for vm\_set\_restrictions and a mov x0,\#0; ret for kernel\_do\_post, whose return value kernel\_bootstrap\_thread checks with cbnz before the Assert path at 0xfffffff007984414.

### 完成条件

- The boot image loads, the menu appears and the kernel is entered.

### 当前范围

- The payload image must be rebuilt whenever the ADT node injection changes.

### 下一步

- Fold the ADT node injection into the payload step so the wrapper step disappears.

### 证据

- `device`: [The image boots to the menu, the payload volume mounts and the kernel entry bar appears after the DarwinBoot hand-off.](https://github.com/stevedang67889/UniXNU-kebab/blob/8b5295d81c61cef68a5dc521cf08695aa36f5d01/docs/bring-up.md)
  Command: <code>fastboot flash boot_a out/probe-final-boot.img; fastboot reboot</code>. Revision: `97f6fea12dae49a1bbc30ccd22c098b82b97dbe4`.
- `source`: [MBR wrapper for the payload FAT volume: status 0, type 0x0c partition at LBA 2048, 1 MiB pad.](https://github.com/stevedang67889/UniXNU-kebab/blob/8b5295d81c61cef68a5dc521cf08695aa36f5d01/scripts/pack-payload-mbr.py)

## 诊断 {#diagnostics}

`device-verified`

组件: `DarwinBoot`.

### 硬件与依赖

- Panel as the only output
- kernel entry probe and timed reset from patch-xnu-entry-probe.py

### 配置

- DEBUG output routed to the framebuffer console
- entry\_probe\_reset\_delay with entry\_probe\_reset\_after and entry\_probe\_reset\_in selects the bisect point

### 操作步骤

- Build the payload with the probe, flash, boot and read the panel
- A reboot after the delay means the probe point was reached

### 开发经验

- Stage bars mark kernel entry and the point just before the MMU is on; a timed reset is the only signal available once the kernel runs without a console.
- A probe registered after the exit-boot-services notifications proved those notifications never returned; skipping them made the hand-off complete.
- Probes can mislead: an inline-assembly probe hardcoded to an identity mapping crashes after arm\_vm\_init closes that mapping and looks like a kernel hang.
- A checkpoint ring at 0xB9000000 and a BSS probe were tried. A one-stub BSS write + dc cvac + PSCI reset reboots, but the next reader still reads no prefix, so normal DRAM does not carry the flag across the reset; the 0xB9000010, 0xC0001000 and 0x200001000 probes behaved the same way.
- pram 0x17F00FE0 is the panic-log page that survives the reset. UEFI leaves it unmapped; a reader that adds it to the GCD and sets it uncached with gDS-&gt;AddMemorySpace and gDS-&gt;SetMemorySpaceAttributes was built, together with a one-stub ml\_phys\_write\_byte\(0x17F00FE0,1\) + reset image \(out/prammap-boot.img\).
- Do not clear the flag page from the firmware: pram may be read-only to UEFI and the kernel clears its own BSS. The prefix check must accept only the value 1, not any non-zero byte.
- debug=0x144 enables a branch that calls SecureDTLookupEntry on /chosen/iBoot and stalls before any IOKit code, so debug stays out of kernel\_args.
- The 2026-10-29 chain uses entry\_probe\_reset\_after and entry\_probe\_reset\_in on \_InitIOKit and IOPlatformExpertDevice::init: the patched bl performs the call, waits six seconds of the 19.2 MHz counter and issues PSCI SYSTEM\_RESET, so one flash answers exactly one question.
- 2026-10-30 bisection of IODeviceTreeAlloc: the checkpoint after IODeviceTreeAlloc did not fire, the one after the first child MakeReferenceTable fired, getRegistryRoot fired and IORegistryIterator::iterateOver fired, which left the interrupt-mapping loop as the stall.
- The device tree carried interrupts and interrupt-parent on the gic node. IODTFindInterruptParent resolves the phandle through gIODTPHandles, which AddPHandle fills only from AAPL,phandle; the ADT has none, so the parent was NULL and IODTGetICellCounts\(NULL\) dereferenced it. A CPU exception screen after repeated resets is the bootloader crash dump for that fault.
- Removing the gic interrupts property from dts/kebab.dts clears IODeviceTreeAlloc, InitIOKit and ConfigureIOKit; the kernel now reaches initialize\_screen in kernel\_bootstrap\_thread.
- kernel\_bootstrap\_thread calls PE\_init\_iokit, then initialize\_screen, vm\_commpage\_init, mac\_policy\_initmach, OSKextRemoveKextBootstrap, machine\_lockdown, kernel\_do\_post, PE\_lockdown\_iokit, vm\_set\_restrictions and kperf\_init\_early before bsd\_init.
- 2026-10-30, after the gic fix: the checkpoint after PE\_init\_iokit fired, and the one after ConfigureIOKit fired too, so InitIOKit and ConfigureIOKit both return.
- kernel\_bootstrap\_thread runs kernel\_startup\_initialize\_upto\(16\) \(THREAD\_CALL\) right after PE\_init\_iokit; that checkpoint fires. The next checkpoints - after initialize\_screen, mac\_policy\_initmach and vm\_commpage\_text\_init - do not, so the stall is in vm\_commpage\_init.
- vm\_commpage\_init calls commpage\_populate, whose first call is pmap\_create\_commpages; it is the current bisection target.
- vm\_commpage\_init calls commpage\_populate, whose first call is pmap\_create\_commpages. The checkpoint after pmap\_create\_commpages did not fire, and inside it the one after the second pmap\_enter\_options\_addr did not either, so the commpage pmap creation stops in its first half \(page allocation, pmap\_create\_options, ASID or the first enter\).
- Replacing vm\_commpage\_init and vm\_commpage\_text\_init with ret lets the boot continue; the next checkpoint after OSKextRemoveKextBootstrap still fails, so the stall moves into mac\_policy\_initmach, vnguard\_policy\_init, dtrace\_early\_init, sdt\_early\_init or OSKextRemoveKextBootstrap.
- The stall after the commpage is mac\_policy\_initmach: the checkpoints after vnguard\_policy\_init and dtrace\_early\_init never fire and the one after mac\_policy\_initmach does not either.
- mac\_policy\_initmach calls load\_security\_extensions\_function, which the libsa KLDBootstrap static constructor points at bootstrapLoadSecurityExtensions. That walks com.apple.\* kexts and calls OSKext::loadKextWithIdentifier for every kAppleSecurityExtension kext, so the boot is now inside prelinked kext loading \(AMFI and friends\) before PE\_lockdown\_iokit.
- Inside KLDBootstrap::loadSecurityExtensions the checkpoint after OSKext::copyKexts already fails, and the one after the first OSKext::loadKextWithIdentifier fails too, so the boot stops in OSKext::copyKexts itself.
- OSKext::copyKexts takes sKextLock with IORecursiveLockLock and then copies sKextsByID with copyCollection. Nothing else in this path runs, so either the lock is held by another thread \(deadlock\) or the kext registry is not usable at this point.
- The sKextLock acquisition inside OSKext::copyKexts returns, so the lock is fine and the stall is sKextsByID-&gt;copyCollection\(\).
- OSKext::initialize creates both sKextLock and sKextsByID and asserts them, and \_\_PRELINK\_INFO lists 38 bundle identifiers, so a valid registry of that size should copy instantly; the copy is most likely faulting on a corrupt entry recorded by readStartupExtensions rather than looping.
- Correction, 2026-10-31: OSKext::copyKexts has three callers - KLDBootstrap::loadSecurityExtensions, KLDBootstrap::loadKernelExternalComponents \(which runs inside InitIOKit\) and IOCatalogue::resetAndAddDrivers. The 2026-10-30 checkpoint inside copyKexts therefore fired during InitIOKit, not at mac\_policy\_initmach, and patching the whole function broke InitIOKit so every later checkpoint failed.
- With only the copyKexts call inside loadSecurityExtensions neutralised, the checkpoint after OSKextLog at the top of that function still does not fire, so the stop is at that log call or the jump into the bootstrap segment rather than in the kext registry copy.
- 2026-10-31 chain with kernel-bsd9: startup step 16, initialize\_screen, vm\_commpage\_init, vm\_commpage\_text\_init, mac\_policy\_initmach, vnguard\_policy\_init, dtrace\_early\_init, sdt\_early\_init, mbuf\_tag\_init all return; machine\_lockdown, kernel\_do\_post and PE\_lockdown\_iokit only return because they are patched out.
- The stop after that is vm\_set\_restrictions, whose argument is machine\_info.max\_cpus and whose body starts with assert\(num\_cpus &gt; 0\); machine\_conf derives the value from the topology max\_cpu\_id, so a zero there panics before kperf\_init\_early and bsd\_init.
- Checkpoints at or after ml\_set\_interrupts\_enabled\(1\) never fire unless that call is nop'd, which is why the earlier bisection reported contradictory results: with IRQs unmasked the checkpoint cave cannot complete its wait either.
- With kernel-bsd11 the checkpoint after kperf\_init\_early fires: the whole kernel\_bootstrap\_thread completes and bsd\_init is entered. The checkpoint after bsd\_init does not fire, so bsd\_init itself now holds the boot.
- A plain ret on kernel\_do\_post sent the boot to the Assert path at 0xfffffff007984414 because cbnz w0 tested a garbage return value; returning zero fixes it.
- Inside bsd\_init the boot stops in throttle\_init: the checkpoints after throttle\_init and after its first thread\_call\_allocate never fire, while the earlier bsd\_init calls \(platform\_stall\_panic\_or\_spin, whose stall value is disabled\) do not stall.
- throttle\_init first calls throttle\_init\_throttle\_window, which reads three kern.io\_throttle\_window\_tier\* defaults through PE\_get\_default. Restoring the real PE\_get\_default and replacing it with a clean mov x0,\#0; ret both leave the stop unchanged, so the PE\_get\_default bring-up patch is not what blocks it; the remaining suspects inside throttle\_init are its PE\_parse\_boot\_argn calls and the lck\_mtx\_init of each throttle lock.
- throttle\_init stops in thread\_call\_allocate, which does not reach zalloc but kalloc\_type\_impl\_internal, the typed allocator; setup itself is trivial, so the allocation is what blocks.
- bsd\_init's first printf also never returns: kprintf's disabled-output branch calls os\_log\_with\_args, and printf itself formats through console\_printbuf\_putc, which needs a console that PE\_create\_console and vcattach currently never create. Patching os\_log\_with\_args out is not enough; patching printf out moves the boot to kauth\_init, which then does not return either.
- The interrupt controller is not part of the kernel image: the symbols are ArmCpu::mapGic, ArmCpu::prepareGic and ArmCpu::enableGic in the prelinked AppleARMCPU kext. Without kext loading and IOKit matching there is no GIC, so the bring-up kernel has to keep IRQs masked, and every wait that needs an interrupt or a timer never returns.
- The devicetree generator added the arm-io window base to the GIC reg but pe\_arm\_map\_interrupt\_controller already maps soc\_phys + reg, so the GIC and timer landed at 0x2EA00000 instead of 0x17A00000. The injected reg now keeps the window offsets \(0xa00000, 0xa60000\) and the mapping resolves to the real addresses.
- Restoring the real PE\_lockdown\_iokit \(IOKit matching\) with the printf/os\_log/throttle stubs in place still does not return, so driver matching is the next thing to walk.
- PE\_lockdown\_iokit is zalloc\_iokit\_lockdown\(\) followed by a tail branch to StartIOKitMatching; StartIOKitMatching calls IOPlatformExpertDevice::startIOServiceMatching, which stops in IOWorkLoop::workLoop, whose first step is OSObject\_typed\_operator\_new - so the stop could never be about drivers: it is kalloc\_type\_impl\_internal.
- kalloc\_type\_impl\_internal ends in zalloc\_ext with the Z\_NOFAIL flag set, and Z\_NOFAIL retries forever; with one CPU, no interrupt controller and IRQs masked, a zone that cannot reach a page never returns. ArmCpu::start \(drivers/ArmCpu/ArmCpu.cpp\) is what would call prepareGic/mapGic/enableGic, so the GIC, the kext matching and the allocator are one dependency cycle.

### 完成条件

- A failed boot leaves enough on the panel or over a transport to identify the failed stage.

### 当前范围

- No USB or storage log transport yet; the RAM ring did not survive the reset in the 2026-10-28 test; the pram reader mapping is the current work.

### 下一步

- Break the cycle at the GIC: either build the kernel with the generic gic\_v3\_irq.c driver \(add it to osfmk/arm64/Makefile, it is not in the object list today, and it reads /arm-io/gic whose reg the ADT now encodes correctly\), or get ArmCpu::prepareGic to run before matching. Also confirm why zalloc\_ext cannot reach a page at that point.

### 证据

- `device`: [Seventeen exit-boot-services notifications, a hung notification phase and a passing hand-off after skipping them; kernel entry, MMU enable and \_machine\_startup all confirmed by bars and timed resets.](https://github.com/stevedang67889/UniXNU-kebab/blob/8b5295d81c61cef68a5dc521cf08695aa36f5d01/docs/bring-up.md)
  Command: <code>flash each bisect image and photograph the panel</code>. Revision: `97f6fea12dae49a1bbc30ccd22c098b82b97dbe4`.

</div>
