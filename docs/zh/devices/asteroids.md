# Nothing Phone \(3a\)（asteroids）

[rootstockos/UniXNU-asteroids](https://github.com/rootstockos/UniXNU-asteroids)

<div v-pre>

Nothing Phone \(3a\) runs the unchanged iPad7,1 iPadOS 17.7.11 image from its UFS userdata partition, with shared SM7635 support and board-owned storage, GPU, input and power integration. Bring-up runs as numbered staged tests; their results are in docs/asteroids-gpu-gen8.md and docs/asteroids-touch.md of rootstockos/iosonandng.

源记录: [porting.toml](https://github.com/rootstockos/UniXNU-asteroids/blob/6370e66cc460202756058ae53f73afdb69abd364/porting.toml), `6370e66cc460202756058ae53f73afdb69abd364`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `implemented` |
| [固件与启动](#firmware) | `implemented` |
| [CPU 与中断](#cpu) | `implemented` |
| [内存与 DMA](#memory) | `implemented` |
| [存储与根卷](#storage) | `implemented` |
| [显示](#display) | `implemented` |
| [输入](#input) | `implemented` |
| [GPU](#gpu) | `implemented` |
| [clock](#clock) | `device-verified` |
| [网络](#network) | `planned` |
| [音频](#audio) | `implemented` |
| [电源](#power) | `implemented` |
| [镜像组装](#packaging) | `implemented` |
| [诊断](#diagnostics) | `implemented` |

## 配置 {#configuration}

`implemented`

组件: `ArmDTPlatform`, `XnuPrelink`.

### 硬件与依赖

- SM7635 SoC profile \(rootstockos/UniXNU-sm7635-common\), iPadOS 17.7.11 build 21H461, asteroids\_defconfig, the board's own driver forks as submodules.

### 配置

- board.soc\_source = sm7635; board.os\_profile = ipados-17.7.11-21H461; schema\_version = 2.
- drivers/Adreno740, drivers/ShengUfs, drivers/ShengHidInput, drivers/ArmDTPlatform and kits/AdrenoFirmware are this repository's submodules at their catalog paths and take precedence over UniXNU's.

### 操作步骤

- Run ./unixnu status --json -D ../UniXNU-asteroids from rootstockos/UniXNU and review profiles, components and patch order.

### 开发经验

- The Data seed workflow \(.github/workflows/data-seed.yml\) takes an os\_profile input \(2026-11-04\): ipados-17.7.11-21H461 as before, or ios-27.0.1-24A446 with the iPhone17,4 OS volume \(details in the storage area\).
- Format 2 builds every selected component's kernel recipe, so \[kernel\] archives lists them as component: entries in the format 1 order; build-arm-driver.py skips Adreno740 and VirtioMmioBlock while their configuration switches are off, as format 1 never built them \(T36 run 40297420036\).
- Format 2 applies the arch, SoC and OS configuration fragments before the defconfig; bootstrap\_defconfig turns off the five options common.config adds, so both passes have their format 1 configuration \(checked with parse\_config: no differences\).
- Format 2 keeps only catalog components, so the forks of NativeAdreno and NativeUfs moved from their legacy names to drivers/Adreno740 and drivers/ShengUfs; legacy aliases are made only for UniXNU's own sources.
- T36 is the first format 2 image \(build tag T36\). Every board.toml value matches the format 1 board \(4f05a36\) except what moved to the SoC and OS profiles, the ADT tool options and the firmware pins \(proprietary-files.txt\); a dry-run pack caught kernel\_args lost in the first rewrite.
- The ADT from the shared generator matches the former make-asteroids-adt.py output except for the OS profile's additions \(J120AP first in the root compatible, product-id, /product/audio\) and the arm-io window, which now covers UFS.
- T40a \(2026-10-27\): every fork has one working branch, asteroids \(former branches are archive/\* tags\); drivers/ArmDTPlatform became the submodule fork rootstockos/ArmDTPlatform; the record check runs rootstockos/UniXNU's workflow and catalog, since UniXNU main's catalog does not know Sm7635Platform or QcomPmicRtc.
- T40c \(2026-10-27\): build tag T40; the GPU governor and fence spin are board defaults \(see gpu\).
- T40d \(2026-10-27\): sheng-lite=1 as on sheng; sheng-disable-jobs keeps only bluetoothd and coreduetd \(the lite list holds the XPC wait cycle\). The kernel from fork asteroids-dev 0d215db carries native-union-root-checkdirs.patch: the SystemOS union over / no longer leaves the OS root one usecount short \(T40c's shutdown panic in vnode\_rele\_ext\).
- T50: board.toml kernel\_args gain sheng-dpu-scanout=2, sheng-dpu-linux=1 and sheng-audio=1.
- T64 \(2026-10-29\): \[payload\] dram\_size 0x23FE00000 and \[payload.adt\] owned\_memory\_size 0x1F0000000 \(7.75 GiB\) over the whole high bank, which the uefi-asteroids map now declares as one run without GPU\_Pool; \[gpu\] gpu\_pool\_base and gpu\_pool\_bytes are gone with the BO pool \(memory area\).
- T64: owned\_memory\_size is 0x180000000 \(6 GiB\) instead of 7.75 GiB until the kernel carries UniXNU 2867796's larger bootstrap table pool \(memory area\).
- T76 \(2026-10-30\): gpu-addon.yml's encrypted artifact also carries NativeAdrenoMetal.unstripped and libvulkan\_freedreno.unstripped \(build-asteroids-metal-plugin.py keeps Turnip unstripped\), for symbolizing the encode thread's CPU profile; the phone gets neither.
- arm64e requirements \(2026-11-03, https://unixnu.com/porting/arm64e, checked in recovery's Linux 6.6.114 on the 3a\): all 8 CPUs \(4 Cortex-A520 MIDR 0x410fd801, 4 Cortex-A720 0x410fd811\) report paca and pacg \(address and generic authentication\); the kernel runs with CONFIG\_ARM64\_PTR\_AUTH=y and CONFIG\_ARM64\_PTR\_AUTH\_KERNEL=y at EL1 under the same Qualcomm hypervisor, so EL1 writes the key registers and PAC instructions run without traps \(HCR\_EL2.API and APK set\). The user wants iPhone iOS 27, not iPadOS: upstream has only ipados profiles \(17.7.11, 26.5.2, 27.0.1-24A446\), so the port will carry its own iPhone iOS 27 profile after the upstream sync.
- iPhone iOS 27 target \(owner, 2026-11-04\): iPhone 16 Plus, iPhone17,4 d48ap \(chip 0x8140, board 0x0a\), iOS 27.0.1 24A446, the build of the iPadOS 27 profile. Its kernelcache \(kernelcache.release.iphone17, decompressed 77987840 bytes, sha256 fa07057bf34f33af1ec26681ad0c87c13e5aaa548a300740eddb0e92876e5f95\) is a fileset of 305 entries at the classic iOS base \(AMFI at 0xfffffff00764ece0, the iPad's at 0xfffffe00...\). The UI scale is one whole number \(LegacyDisplayProbe.cpp publishes /chosen display-scale, 2 today = 540 points\): bring-up runs at 3 \(360 points, pixel exact\); the iPhone 16 Plus size \(430 points, 2.51\) needs a 1290x2796 frame scaled to the panel afterwards. hoshikv/UniXNU-peridot \(SM8635\) carries an unfinished ios-27.0.1-24A446 profile for iPhone14,5 \(no AMFI address, iPad root UUIDs as placeholders, no hardware result\).
- iPhone17,4 pins \(2026-11-04, against the iPad17,3 24A446 kernelcache, sha256 38e6d9fa..., the iPadOS profile's pin\): all 32 compared kexts \(the 31 prelink roots, AMFI, IOMobileGraphicsFamily, IOSurface, IOHIDFamily, the kernel\) carry the same bundle versions. com.apple.iokit.IOHIDEventDriver is a codeless kext \(personalities only, load address INT64\_MAX\) on both, with no fileset entry on either, so all 31 roots apply and HidInputProbe needs no change \(the earlier note that it did was wrong\). AMFI early security init: the iPad wrapper \(0xfffffe00092551ac\) calls initializeAppleMobileFileIntegrity at 0xfffffe00092549f4; that function matches uniquely in the iPhone \_\_TEXT\_EXEC at 0xfffffff00920f854 \(12 to 48 masked instructions\), called from two sites as on the iPad, and its wrapper is 0xfffffff00921000c, byte for byte the iPad's. The fileset prelink links at the native address and ignores the profile slide. User space is not cache independent: on arm64e upstream's NativeAdrenoMetalPlugin.mm writes four QuartzCore globals and patches one instruction \(0x184461928\) at iPad 24A446 shared cache addresses, and package/AsteroidsMetalPlugin.mm writes the EDR headroom global the same way; on the iPhone's own dyld cache those addresses are other memory, so they need a per cache table before the first iPhone boot.
- Per cache QuartzCore sites \(2026-11-04\): package/AsteroidsMetalPlugin.mm writes the EDR headroom override \(QuartzCore debug\_values index 21\) only where kQuartzCoreSites holds the running dyld shared cache's UUID, and marks 0x6EF0 elsewhere; CA\_DISPLAY\_EDR\_HEADROOM is set either way. Addresses by name from each cache's symbols \(ipsw dyld symaddr, local/tools/ipsw-bin\): iPad17,x CE33B2BA-2EBB-3B58-A04E-1953E12112AE debug\_values 0x1e7020fc0; iPhone17,4 A54D617A-342B-3A29-8F63-B9F93CE76141 0x1e7024fc0. In the iPhone cache QuartzCore's code sits at the iPad's addresses \(CARenderServerStart 0x1846dce88, framebuffer\_pixel\_format 0x184461838\) and its data 0x4000 higher \(\_ca\_debug\_options 0x1e702516c, is\_virtualized 0x1e701fdd9\), so the iPad address would have written another global silently. Upstream's NativeAdrenoMetalPlugin.mm, which writes more of them, is not built for this board. UniXNU 63b3d7e adds the ios-27.0.1-24A446 profile \(root volumes 634783FE OS, FA95C6F7 SystemOS\) and decrypts AEA images with ipsw on Linux; the iPhone userdata image \(15.02 GiB, OS 10104078336 bytes at 0x100000, SystemOS 6020923392 at 0x25a500000\) is in local/userdata-ios27, not written.
- xnu-12377 patch stack for the iOS 27 profile \(2026-11-04, checked with git apply on xnu ac9718fb, as UniXNU patches.py applies it\): arch \(arm64e\) 64, SoC 2, OS 4 and device 12 patches apply in board order \(arch, SoC, OS, device\). UniXNU-sm7635-common 47dc6aa adds patches/xnu-12377 \(sm8550's versions; our two xnu-10063 SoC patches are identical to sm8550's\). patches/xnu-12377/series is sheng's xnu-12377 board series without its Wi-Fi and latency traces \(CPU idle, E/P Edge, audio add-on mount, source storage hook, iPadOS 27 bring-up\), our class registration, rootstockos/UniXNU's five xnu-10063 bring-up patches unchanged, and the watchdog policy ported to sheng's xnu-12377 call site. Not yet set for the profile: the board build scripts are iOS 17 arm64 only \(build-asteroids-platform-power.py requires the iOS 17 target; build-native-legacy-display.py and build-ufs-original-bindings.py match the 21H461 kernelcache\), and sheng builds its 27 display with its own build-gop-legacy-display-27.py.
- iPhone17,4 class ABI fixtures \(2026-11-04\): sheng builds the iPadOS 27 display and input against reviewed iPad17,3 fixtures \(scripts/legacy-display-24A446.json, IOMobileFramebufferLegacy, 379 slots; hid-device-24A446.json, IOHIDDevice, 207\). scripts/remap-24A446-display-fixture.py \(with kcremap\_24A446.py\) rewrites them for the iPhone kernelcache: each address is moved by fileset entry, segment and offset and verified, vtable slots are the iPhone's own chained-fixup pointers with PAC key, diversity and address diversity equal to the iPad's and targets equal by offset or by masked code \(display 215 offset, 161 code, 3 kernel; HID 57, 146, 4; the kernel is built per SoC, so a kernel target is the iPhone vtable's own\), and the display fixture's 10 byte checks match exactly. collection\_slide is 0: the iPhone cache is already at the link base 0xfffffff007004000, where the iPad's 0x1f000000000 moves the iPad cache. Results: scripts/legacy-display-24A446-d48.json \(vtable 0xfffffff0082d2000\), scripts/hid-device-24A446-d48.json \(vtable 0xfffffff0082b26b0\).

### 完成条件

- All source pins resolve; every selected component has a record; status shows the intended overrides and patch order.

### 当前范围

- The SoC profile is pinned to a local checkout \(local.toml\) until rootstockos/UniXNU-sm7635-common is published.

### 下一步

- Publish the SoC repository and pin its commit in feeds.toml.

### 证据

- `source`: [Format 2 board configuration with the SM7635 SoC and 21H461 OS profiles.](https://github.com/rootstockos/UniXNU-asteroids/blob/6370e66cc460202756058ae53f73afdb69abd364/board.toml)

## 固件与启动 {#firmware}

`implemented`

组件: `DarwinBoot`.

### 硬件与依赖

- rootstockos/uefi-asteroids \(Mu-Silicium VolcanoPkg and asteroidsPkg\) with UniXNU, UniXNUDxe and DarwinBoot.
- The 3a's ABL loads the boot image with fastboot boot; it ignores the boot image's ramdisk.

### 配置

- \[bootimg\] payload\_in\_kernel = true: the payload rides in the kernel image and ShengBootMemoryDxe finds it in the Kernel memory region.

### 操作步骤

- Build the payload and boot image with ./unixnu build payload and ./unixnu bootimg --dtb \(the phone's live DTB\), then fastboot boot the image.

### 开发经验

- The ABL passes the vendor\_boot and init\_boot ramdisks plus bootconfig as the initrd, never the boot image's own ramdisk.
- Proprietary files follow sheng's method: proprietary-files.txt with an @fetch source and SHA-256 per file, put in .cache/firmware by scripts/extract-files.py \(which falls back to curl when Python has no CA store\).

### 完成条件

- Firmware image builds, enters UniXNU, publishes the framebuffer and preserves the documented memory reservations.

### 当前范围

- Images are booted from RAM only \(fastboot boot\); nothing is flashed.

### 下一步

- Record the firmware revision with each boot image.

### 证据

- `source`: [\[bootimg\] and \[firmware\] select uefi-asteroids and the payload in the kernel image.](https://github.com/rootstockos/UniXNU-asteroids/blob/6370e66cc460202756058ae53f73afdb69abd364/board.toml)

## CPU 与中断 {#cpu}

`implemented`

组件: `ArmCpu`.

### 硬件与依赖

- Four Cortex-A520 \(cpus 0-3, EPSS domain 0\) and four Cortex-A720 \(4-6 domain 1, 7 domain 2\); EPSS domains at 17d91000/17d92000/17d93000.
- Gunyah hypervisor: SGIs are not delivered, so IPIs use armcpu-spi-ipi=1.

### 配置

- sheng-smp=1 and armcpu-spi-ipi=1 in board.toml; unixnu,cluster-type E/P in dts/asteroids.dts; sheng-cpufreq=&lt;mode&gt; selects the CPU governor.

### 操作步骤

- Boot with sheng-cpufreq=1 and the banner on, read the CPU row \(domain state and LUT\), then sheng-cpufreq=4.

### 开发经验

- The CPU governor is sheng's CpuFreqProbe with 4/3/1 CPUs per domain and no L3 vote \(the 3a has no EPSS L3\).
- patches/xnu-12377 \(iOS 27 profile, 2026-11-04\) takes sheng's xnu-12377 CPU idle helper and E/P Edge scheduler \(zzye, zzyf\) in place of our xnu-10063 copies; the xnu-10063 zzyf also set \_\_ARM\_AMP\_\_ and two clusters in BCM2837.h, which sheng's xnu-12377 zzyf leaves to its iPadOS 27 bring-up patch \(not yet checked on the 3a\).
- The E/P Edge scheduler and the idle-time helper are sheng's zzyf and zzye patches \(patches/xnu\).
- T40c \(2026-10-27\): the cpu0 park thread is off by default \(sheng-cpu0-park=0, as UniXNU-sheng d361b53\): the E/P Edge scheduler places work by cluster, and T39b found the park thread holding cpu0 at 100 %. The governor and the AMP and idle patches already match sheng's latest.
- T64 \(2026-10-29\): dts/asteroids.dts's memory node covers the whole high bank \(0x8C0000000 + 0x23FE00000\), equal to board.toml dram\_size, since the GPU pool at its top is gone \(memory area\).
- T76 \(2026-10-30\): the board classes here register through OSKextRegisterBoardClasses \(zzyg-board-class-registration.patch\), under the kext lock, in place of preModLoad/postModLoad alone, which deadlocked T75f's boot \(storage area\).
- T76's first kernel build \(run 41109301209\) failed: XNU has no kOSReturnNoMemory; OSKextRegisterBoardClasses and its callers use kOSKextReturnNoMemory \(libkern/OSKextLib.h\), and the helper has a prototype before its definition.

### 完成条件

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU.

### 当前范围

- The governor and the E/P scheduler are not yet verified on the phone \(T35\).

### 下一步

- Boot T35a \(read-only\) and T35b \(governor\) and record the clocks and frame rate.

### 证据

- `source`: [EPSS CPU governor with touch boost and frame floor.](https://github.com/rootstockos/UniXNU-asteroids/blob/6370e66cc460202756058ae53f73afdb69abd364/package/CpuFreqProbe.cpp)

## 内存与 DMA {#memory}

`implemented`

### 硬件与依赖

- DRAM high bank 0x8C0000000-0xAFFE00000 \(9 GiB less 2 MiB, one conventional run since T64\) for the XNU window; GMU pool at 0xE6440000 \(32 MiB\), reserved in the uefi-asteroids memory map. Until T63 a GPU pool sat at 0xABFE00000 \(1 GiB\).

### 配置

- owned\_memory\_size 0x180000000 \(6 GiB, T64; 4.75 GiB before\) and dram\_size 0x23FE00000; the DTS memory node equals dram\_size.

### 操作步骤

- Check that payload.dram\_size equals the DTS memory node and that DarwinBoot places the window.

### 开发经验

- 384 MiB of owned memory left iPadOS short; 4.75 GiB in the high bank \(uke's layout\) is enough.
- Metal's 64 MiB blocks need a 1 GiB GPU pool outside the XNU window.
- T62b-light \(2026-10-29\): with every app on the GPU the 1 GiB pool filled and the GPU stopped once BOs fell back to scattered pages, while XNU had 849 pages free. T64: no pool; user BOs are XNU's pageable memory \(sheng's Adreno740 882f4bf\) and the window grows from 4.75 to 7.75 GiB over the whole high bank, leaving 1.25 GiB of the run to UEFI's own allocations.
- T64 first boot \(2026-10-29\): 7.75 GiB stopped at the kernel's entry, the green and blue bars without the magenta one: before the MMU is on, start.s maps the window twice with 1 GiB per L2 table page, and UniXNU's native-4k-bootstrap-capacity patch held 16 pages, enough for 6 GiB; the patch's own guard loops when the pool runs out. The window is 6 GiB until a kernel with UniXNU 2867796 \(22 pages, windows up to 9 GiB; staged, not built\) is built, then 7.75 GiB.

### 完成条件

- All handoff regions are accounted for and each enabled DMA engine accesses its allocated range with the documented cache policy.

### 当前范围

- The GMU pool is a fixed reservation in the firmware memory map. DarwinBoot gives XNU at most 8 GiB.

### 下一步

- Record the firmware memory map with each firmware change.

### 证据

- `source`: [Memory node for the XNU window's DRAM bank.](https://github.com/rootstockos/UniXNU-asteroids/blob/6370e66cc460202756058ae53f73afdb69abd364/dts/asteroids.dts)

## 存储与根卷 {#storage}

`implemented`

组件: `ShengUfs`, `RamBlock`, `SoftwareAES`, `VirtioMmioBlock`, `VerifiedRoot`.

### 硬件与依赖

- UFS host 0x1d84000 and PHY 0x1d80000 \(SM8550's windows\), apps SMMU stream 0x60; userdata LUN 0 blocks 0x256248-0x3a8bffa.

### 配置

- native-ufs-root=1 and native-ufs-allow-unverified=1; sheng-data-persist=2 keeps Data at the end of userdata.

### 操作步骤

- Build the userdata image, write it to userdata from recovery, boot, and pull the Data volume with scripts/pull-asteroids-data.py.

### 开发经验

- iOS 27 storage \(2026-11-04\): drivers/ShengUfs \(rootstockos/NativeUfs asteroids 9e1cc29\) merges UniXNU/ShengUfs main: the source API, the header-only policy handoff and readPolicyTable, which reads "&lt;window&gt;.vroot" and requires its size to be the bare hash table \(block count x 32\), so the userdata objects are the tables \(OS 78938112, SystemOS 47038464 bytes\) and the image was rebuilt. Kept ours where they met: TCR2 from IDR2 and the Linux-style display bank, the counters outside the verified block guard. package/SourceStorage.cpp, SourceRootPolicies.cpp, SourceRootBinding.cpp, BootReset.c and BootProcessWorker.c are sheng's \(965460a\), unchanged, for build-sheng-source-storage.py, which now looks in kits/&lt;board kit&gt; \(UniXNU bd4766a\). The Data seed workflow takes os\_profile: for ios-27.0.1-24A446 it fetches and decrypts the iPhone17,4 OS volume \(scripts/fetch-os-volume.py; ipsw and aea on macOS\) and seeds from its var tree \(launchd c640246d..., LastSystemVersion 24A446\).
- iOS 27 root policies \(2026-11-04\): on arm64e component:ShengUfs builds the source storage runtime \(build-sheng-source-storage.py\), which mounts only a root authenticated by a signed policy. scripts/policies/ios-27.0.1-24A446/&\#123;OS,SystemOS&\#125; hold our own policies, signed with a local owner RSA-3072 key \(local/owner-keys, never in a repository; trusted key sha256 c97a039baef14b94...\) by scripts/sign-root-policies.py over the userdata image's windows: OS 10104078336 bytes, 2466816 blocks, sha256 b73d3753...; SystemOS 6020923392 bytes, 1469952 blocks, 17ca9d50.... scripts/verify-root-policies.py authenticated each with UniXNU's VerifiedRoot C code \(built as a Linux host library with its OpenSSL provider\): the full envelope, the 544-byte header alone, every block and the whole digest. Only the headers, trusted keys and records are here: the full manifests \(79 and 47 MB\) are the userdata image's objects OS.vroot and SystemOS.vroot \(XNU\_SOURCE\_STORAGE\_TABLES=userdata\), in local/userdata-ios27 \(not written\).
- Format 2 builds VirtioMmioBlock as ShengUfs's dependency; build-arm-driver.py skips it while XNU\_NATIVE\_VIRTIO\_BLOCK is off.
- NativeUfs \(the ShengUfs fork\) is built without the verified-root check until signed volume policies exist.
- Its IOBlockStorageDevice imports bind against the original class in a bootstrap kernel candidate built first in CI.
- T67, T72 and T72 again \(2026-10-29/30\) hung before the root mount: NativeUfs published SystemOS and never saw IOMedia under it \(no block request, "SystemOS volume  not ready" after 30 s\), while the UFS transport kept writing the log and every processor sat idle. bsd\_init's stage markers stopped at bsd\_autoconf, whose late probes had not reached the CPU clock row \(\[clocks\] absent, \[gpu uc\] stage 0, B st=0\); T71 on the same kernel booted. Both stalled together, so a race between the probes and IOKit matching; T73 logs where each thread waits.
- T75f \(2026-10-30\) hung before the root mount and T73's \[kernel threads\] rows caught it: a lock-order deadlock. The boot thread, in native\_keystore\_probe \(late probe step 1, key events stage 1\), held OSMetaClass's class lock from preModLoad and waited in postModLoad for sKextLock \(OSKext::lookupKextWithIdentifier\); IOConfigThread\_'IOResources' held sKextLock loading a kext \(OSKext::load, OSRuntimeInitializeCPP\) and waited for the class lock in preModLoad; IOConfigThread\_'NativeUfsBlock' waited for sKextLock in IOCatalogue::personalityIsBoot, so the SystemOS disk never got a driver. XNU takes sKextLock first; the board's probes took only the class lock. Intermittent because it needs a kext load during the probe's registration, right after bsd\_autoconf publishes IOBSD. T76: OSKextRegisterBoardClasses \(patches/xnu/zzyg-board-class-registration.patch\) registers board classes under sKextLock, and all eight probes that called preModLoad/postModLoad use it.

### 完成条件

- The root volume mounts read-only from UFS and Data persists across boots.

### 当前范围

- Root reads are not authenticated.

### 下一步

- Build the owner verified-root bundle.

### 证据

- `device`: [T29 booted iPadOS 17.7.11 from the UFS root with persistent Data to the first picture.](https://github.com/rootstockos/UniXNU-asteroids/blob/6370e66cc460202756058ae53f73afdb69abd364/board.toml)
  Command: <code>fastboot boot local/unixnu-asteroids-t29-boot.img</code>. Revision: `adf900cf453a6b318864913757f588c9f661596f`.

## 显示 {#display}

`implemented`

组件: `GopFramebuffer`.

### 硬件与依赖

- The firmware's GOP framebuffer, 1080x2392 x8r8g8b8 at stride 4320, on a 120 Hz video-mode panel.

### 配置

- offline-legacy-\* arguments, sheng-vsync=120, sheng-fb-gpu=1 \(the GPU copies each frame to the panel\).

### 操作步骤

- Boot and watch the banner rows \(sheng-banner=1\) for swaps per second and copy times.

### 开发经验

- iOS 27 builder \(2026-11-04, not built yet\): scripts/build-native-legacy-display-27.py is sheng's build-gop-legacy-display-27.py \(UniXNU-sheng 965460a\) with the IPSW device's fixtures \(d48ap: legacy-display-24A446-d48.json, hid-device-24A446-d48.json\), IOMobileGraphicsFamily's text range from the fixture \(family\_text, the iPad range moved by its kext offset\) in place of the iPad constant, kits/asteroids, and this board's drivers from the iOS 17 builder \(CPU frequency, panel and brightness, TFA9873 speaker and audio DSP, battery, buttons, FocalTech touch over GENI SPI, GPU power with NativeAdreno's staged classes and the gen8 kits\) compiled with the 27 kernel flags. The HID event driver is compiled against the profile's pinned public IOHIDFamily \(NATIVE\_HID\_SOURCE\_API\) and bound to the original IOHIDDevice by sheng's slot and discriminator rules. Sheng's generated support file stubs boot progress \(none on 27\); our LegacyDisplayStubs.c is weak. The Metal accelerator comes from UniXNU's build-adreno740-accelerator.py \(d48ap plan\). Sheng's two-pass kernel build \(native-slide in cycle27.sh\) is not needed: the builder binds fixed collection addresses and XnuPrelink recomputes the adapter branches.
- The display area owns only the 24A446 display and HID fixtures and their remap tools by name; scripts/policies \(iOS 27 root policies\) belongs to storage.
- iOS 27 \(2026-11-04\): scripts/legacy-display-24A446-d48.json and hid-device-24A446-d48.json are sheng's iPad17,3 class fixtures remapped and verified for the iPhone17,4 kernelcache \(details in the configuration area\); the iOS 27 display builder that uses them is not written yet.
- T37 \(2026-10-26\): DSI0 is reachable under Gunyah \(T37a st=1\), the brightness test ran \(T37b\), and with asteroids-panel=3 iOS sets the brightness and sleep turns the panel off and on again \(T37d\). It is a board default since then.
- T37: the panel \(Visionox RM69220 AMOLED, video mode, DSI0 at 0x0ae94000, dsi-ctrl v2.8\) takes DCS commands through the controller's TPG command FIFO, scheduled for the first front-porch line \(package/PanelProbe.cpp, asteroids-panel=1..4\): brightness 51 hi lo \(10..4095\), off 28 + 10, on 11 + 29. The iOS brightness service is sheng's AppleARMBacklight.cpp with the DCS write instead of I2C \(package/AsteroidsBacklight.cpp\); level 0 turns the panel off.
- The CPU copy \(143-285 ms a frame\) mapped the surfaces cacheable without invalidation and showed stale patches; the GPU copy removes both.
- GopFramebuffer 33e941a's direct scanout needs ShengUfs's display SMMU window \(native\_ufs\_dpu\_map\); our NativeUfs fork has none, so package/LegacyDisplayStubs.c supplies weak zero stand-ins that keep it off.
- T40c \(2026-10-27\): BootProgress.c's cpu0\_park defaults off \(see cpu\).
- T40k-T42 \(2026-10-27\): zero copy on the 3a. NativeUfs sheng-dpu-linux=1 sets the display bank up as Linux does: CBA2R and CBAR written \(the apps SMMU is qcom,virt-smmu and the hypervisor attaches the bank on that write\), TCR2 with the ASID size and SEP, cached inner-shareable walks with T0SZ 28, TTBR0 with an ASID. The bank then took stage 1 without a fault \(T40k\), where every earlier setup faulted at level 0, even with blocks lacking the access flag \(T40i-af\). T41: 1018 direct flips, 4.4 ms mean latch, once startDirect waited for the bank \(40 ms\); frames showed half drawn \(the wallpaper without the app\), so T42 flips only once the GPU's completed fence reaches the newest fence submitted at the swap.
- T42 \(2026-10-28\): the GPU wait never ran \(0 of 1272 flips\), yet opening apps still alternated the new frame with the wallpaper alone. The original completion \(IOMobileFramebufferLegacy slot 295, its body at 0xfffffff00578a96c in 21H461\) clears the current swap and releases its surfaces, and it ran as soon as a swap latched: the compositor got back the surface still on screen and drew its next frame over it. T43: sheng-dpu-hold=&lt;ms&gt; keeps the shown swap current until the next latch \(or &lt;ms&gt; without a new swap\) and only then completes it; \[direct scanout\] held / timed out count the two.
- T44: \[direct scanout\] adds frame gaps \(flip to flip: up to 17, 25, 34, 50, 100 ms, longer, the longest under a second\), to measure the frame rate opening an app reaches under blur.
- T43-copy \(2026-10-28\): copy mode felt slower and choppier than older builds. Its log \(25 minutes\) shows the copy path as before: 5310 GPU copies, none failed, no CPU throttling. The session was heavier, though: two wallpaper renderers \(PosterBoard, CollectionsPoster\) on the GPU, 691 MB of GPU memory against 345-582 MB, and seven times the time freeing it. Every counter covers the whole boot. T46: the \[frames\] row counts frames shown by copy and by flip and the gaps between them \(T44's flip-only histogram moved there\).
- T46 \(2026-10-28\): zero copy with the end-of-submission GPU cache flush still alternated the new frame with the wallpaper alone. 1102 flips in 78 s: 68 % of the gaps 17 ms or less, 17 % up to 25 ms, 3 % over 50 ms. T47 reverts the guesses that did not fix it: the GPU wait \(904bccf\) and the frame hold \(8393a37\) in GopFramebuffer \(d4f7b59, the direct path is a5fc6bf's again\), keeping the frame counting.
- T47 review \(2026-10-28\): T42's flip wait never waited. It found the GPU's fence page through NativeAdreno's native\_adreno\_fence\_phys, which only NativeAdreno's service sets; this board attaches the ring in GpuPowerProbe, so it stayed 0 \(no \[fence page\] row in any log\) and gpuCaughtUp\(\) always answered done. 'No flip waited for the GPU' therefore says nothing. T48: sheng-dpu-probe=1 samples what the display fetches \(4 x 4 luminance grid through an uncached mapping\) at the flip, the latch, each refresh tick and when the surface leaves, with the real fences \(GpuPowerProbe native\_gpu\_fences\); sheng-dpu-flipdelay=&lt;us&gt; and sheng-dpu-gpuwait=1 test late GPU work. T47-copy: copy mode is GPU-bound \(23 % of frames within 17 ms against 68 % with zero copy; 435 of 1507 busy windows at the ceiling\).
- T49: \[mic peaks\] \(the capture's peak per second and its start time\) and BTN taps=.
- T49-probe/T49-gpuwait \(2026-10-28\): the flicker's cause is flipping to frames the GPU has not finished. With the probe, 663 of 703 flips found GPU work outstanding and 277 surfaces changed between flip and latch \(222 more before leaving the screen, none on a refresh tick while shown\). Waiting for every submission made before the flip \(the real fences from GpuPowerProbe\) gave 0, 0 and 0 over 821 flips, 691 waits over 1 ms, longest 23.6 ms, and no visible flicker; smoothness felt like copy mode. T50 makes it the default: board.toml sets sheng-dpu-scanout=2 and sheng-dpu-linux=1, GopFramebuffer waits unless sheng-dpu-gpuwait=0.
- T51: \[frame time\] splits each frame into compositor time, swap to screen and flip to latch; \[frames\] gains a 9 ms \(120 Hz\) bucket. The panel is advertised as 24-120 Hz \(sheng-vsync=120\).
- T51: per frame, compositor time had a wide spread, swap to screen 8-12 ms \(the GPU\), flip to latch 4.5 ms mean; they run in series because the compositor starts the next frame only when the swap completes. T52: sheng-dpu-early-done=1 completes a direct swap when its flip is programmed.
- T53: the boot log gains \[gpu work\] \(BootLog.c\), the GPU work per submission by render passes against its GPU time.
- T54: the boot log gains \[gpu sysmem why\]; \[gpu work\] drops the draw count.
- T55: the boot log gains \[gpu ops\] \(GPU time per kind of work\).
- T61: BootProgress.c also anchors boot\_diag\_scan\_gpu \(BootDiagExport.c\), which the periodic GPU trace export \(sheng-gpu-trace-export, see diagnostics\) calls; its rounds include the half-resolution screen, so a trace comes with what was shown.
- T62: BootLog.c gains the \[gpu tables\] and \[gpu recovery\] rows \(see diagnostics\).
- T64 \(2026-10-29\): build-native-legacy-display.py no longer checks board.toml gpu\_pool\_\* against GpuPowerBoard.h \(both gone with the BO pool\); BootLog's \[bo pool\] row is \[bo memory\] \(diagnostics area\).
- T64: BootLog.c adds the \[gpu uc\] rows \(diagnostics area\).
- T65: the boot log adds a \[bo pool\] row \(native\_adreno\_pool\_stats\): pool MiB and chunks, the reservation's and write-combine's IOReturn, BOs from the pool, BOs sent to the system, MiB in use and peak.
- T73 \(2026-10-30\): native\_legacy\_display\_late\_probe records which probe bsd\_autoconf's thread is in \(native\_late\_probe\_step\) and the thread itself, for the boot log's \[late probe\] and \[kernel threads\] rows \(T67 and T72 hung inside it\).
- T76 \(2026-10-30\): the board classes here register through OSKextRegisterBoardClasses \(zzyg-board-class-registration.patch\), under the kext lock, in place of preModLoad/postModLoad alone, which deadlocked T75f's boot \(storage area\).
- T76's first kernel build \(run 41109301209\) failed: XNU has no kOSReturnNoMemory; OSKextRegisterBoardClasses and its callers use kOSKextReturnNoMemory \(libkern/OSKextLib.h\), and the helper has a prototype before its definition.
- T76's second kernel build \(run 41111730079\) failed in ShengPlatformPower.cpp: BoardClasses.h had been included after the file's last \#include, which there sits inside the ShengPlatformPower class; every probe now includes it after its first \#include.
- T89 \(2026-11-02\): BootLog.c prints the microphone's \[mic port\] row \(native\_mic\_port, audio area\) after \[mic regs\]; BootLogStandins.c gives it a weak stand-in.
- T93 \(2026-11-02\): BootLog.c prints \[mic codec\] \(native\_mic\_codec, audio area\) after \[mic port\]; BootLogStandins.c gives it a weak stand-in.
- T94 \(2026-11-02\): \[mic codec\] prints whenever \[mic port\] does.
- T95 \(2026-11-02\): BootLog.c prints \[mic page\] \(native\_mic\_page, audio area\) after \[mic codec\]; BootLogStandins.c gives it a weak stand-in.

### 完成条件

- The desktop presents through the legacy display with measured frame times.

### 当前范围

- Under 60 frames per second.

### 下一步

- Measure the frame rate with the CPU governor \(T35\).

### 证据

- `device`: [T34b: GPU copy to the panel, no tearing or stale patches, stable.](https://github.com/rootstockos/UniXNU-asteroids/blob/6370e66cc460202756058ae53f73afdb69abd364/board.toml)
  Command: <code>fastboot boot local/unixnu-asteroids-t34b-boot.img</code>. Revision: `e022e84a9721ea6408ea12665b5a23e9b89fc5f6`.

## 输入 {#input}

`implemented`

组件: `ShengHidInput`, `ShengNovatekTouch`, `QcomGeniSpi`.

### 硬件与依赖

- FocalTech FT3683G on GENI SE0 SPI; PMK8550 PON power and RESIN, PMXR2230 GPIO 6 volume up, through the SPMI arbiter and PDC pin 1 \(SPI 481\).

### 配置

- asteroids-touch=6 \(package default\) and sheng-touch-hid=1; sheng-buttons=1 for the buttons.

### 操作步骤

- Boot, touch the desktop and press each button; read the BTN banner row.

### 开发经验

- iOS 27 input \(2026-11-04\): drivers/ShengHidInput moves to UniXNU/ShengHidInput 71a40e7 \(three commits: the arm64e event driver vtable copy re-signed with Apple's slot discriminators, which are name-derived and the same in every 24A446 IOHIDFamily-2238.120.5\) and is compiled with NATIVE\_HID\_SOURCE\_API by build-native-legacy-display-27.py.
- Touch is polled; stage 2's RPMh votes need a completion check.
- Every button constant equals sheng's \(SPMI arbiter v7 at the same addresses, same PPIDs\).
- TouchState.cpp's placeholder button sink is gone: ButtonProbe.cpp owns native\_buttons\_set\_sink.
- T47 \(2026-10-28\): quick button clicks did not register, a slightly longer hold did: the thread reads the levels when it wakes, and a short press is up again by then. T49: with sheng-buttons-taps=1 the interrupt handler records which buttons fired, and one that is up again without a reported press is reported as a 30 ms tap; BTN taps= counts them.
- T49-gpuwait: quick taps still did not register although every edge raised an interrupt and a report \(45 of 45, taps=0\): the driver saw them and iOS ignored them. T50: sheng-buttons-hold-ms=&lt;ms&gt; delays a release until the press has lasted that long.
- T51: 4 button interrupts, 4 reports, with sheng-buttons-hold-ms=80; whether quick taps were tried is unknown.
- T76 \(2026-10-30\): the board classes here register through OSKextRegisterBoardClasses \(zzyg-board-class-registration.patch\), under the kext lock, in place of preModLoad/postModLoad alone, which deadlocked T75f's boot \(storage area\).
- T76's first kernel build \(run 41109301209\) failed: XNU has no kOSReturnNoMemory; OSKextRegisterBoardClasses and its callers use kOSKextReturnNoMemory \(libkern/OSKextLib.h\), and the helper has a prototype before its definition.
- T76's second kernel build \(run 41111730079\) failed in ShengPlatformPower.cpp: BoardClasses.h had been included after the file's last \#include, which there sits inside the ShengPlatformPower class; every probe now includes it after its first \#include.

### 完成条件

- Contacts and buttons reach backboardd as HID events.

### 当前范围

- The buttons are not yet verified on the phone \(T35\); ShengNovatekTouch is linked as ShengHidInput's dependency and not used.

### 下一步

- Boot T35a with sheng-buttons=1.

### 证据

- `device`: [Touch input works on the desktop \(stage 6\).](https://github.com/rootstockos/UniXNU-asteroids/blob/6370e66cc460202756058ae53f73afdb69abd364/package/AsteroidsTouchProbe.cpp)
  Command: <code>fastboot boot local/unixnu-asteroids-t34b-boot.img</code>. Revision: `e022e84a9721ea6408ea12665b5a23e9b89fc5f6`.

## GPU {#gpu}

`implemented`

组件: `Adreno740`, `AdrenoFirmware`, `AdrenoPM4`, `ArmSmmu4K`, `Sm7635Platform`, `Sm8550Platform`.

### 硬件与依赖

- Adreno 810 \(gen8, chip 0x44010000\) at 0x3d00000 with GMU, RSCC and SMMU; firmware gen80300 from proprietary-files.txt \(scripts/extract-files.py, the pinned NullDebris vendor repository\).

### 配置

- sheng-gpu-power=19, sheng-gpu-addon=1, sheng-gpu-level=6 \(763 MHz\); the Metal plugin and Turnip are built on the Mac into the payload addon.

### 操作步骤

- Build the kernel in CI, the addon with scripts/build-asteroids-metal-plugin.py --published, pack and boot.

### 开发经验

- NativeAdreno's GMU headers \(NativeAdrenoGmuConfig.h, NativeAdrenoGmuPlatform.h\) include ShengGmu.h, so the driver compiles also take kits/Sm7635Platform \(T36 run 40296339052\).
- The gen8 GMU cold start and command-database parser are the SoC kit Sm7635Platform \(UniXNU-sm7635-common\), as sheng's are Sm8550Platform; the board keeps ShengGmuVotes.c. scripts/check-asteroids-gmu.py passes against the kit.
- The render server composites on the A810 \(window server ready in 1.9 s instead of 30.8 s\).
- The GPU clock does not limit the frame rate: 1050 MHz was barely faster than 763 MHz.
- T40b \(2026-10-27\): drivers/Adreno740 is UniXNU Adreno740 main \(5c8c145\) merged into our gen8 fork \(rootstockos/NativeAdreno asteroids 60f16a6\): ABI v2 \(128 buffers per submission\), no full GPU TLB flush per submission, owned and exclusive imports mapped without alias scans. The board's GPU probe keeps its ABI structures and native\_adreno\_publish signature; it passes no GMU AHB fence status to the ring \(the new optional fence\_cookie/fence\_status\), so WPTR writes stay unchecked as before.
- T40c \(2026-10-27\): sheng's GPU governor is on by default in board.toml \(sheng-gpu-dcvs=1\) with the 3a's range: floor level 6 \(763 MHz, the former fixed level; sheng's floor 3 is 510 MHz here and held every frame in T39b\), ceiling level 7 \(895 MHz; no GPU thermal throttle yet\). Fence waits spin \(sheng-gpu-irq=0\) as a board default.
- T40d \(2026-10-27\): IO coherence. Nothing here set native\_adreno\_io\_coherent, so the merged driver cleaned and invalidated every imported page around every submission \(T40c log: 18 s and 361 GiB of maintenance for about 3000 submissions\). GpuPowerProbe now runs UniXNU-sheng's coherenceProbe \(08cde20\) before publishing: a kernel page mapped write-back inner-shareable, GPU reads of CPU-dirty lines and CPU reads of GPU writes both proved against DRAM; only then is it on \(sheng-gpu-coherent=0 skips it\). The driver keeps GPU-written imports non-coherent \(myron 5bbeb3b\). Turnip's 1 ms waits \(pandora 6265e2d\) were already fixed upstream \(100 ms slices in turnip-darwin-kmd.patch\); kern.maxvnodes is 66560 from upstream's iPadOS profile.
- T44: \[gpu load\] counts the dcvs thread's 16 ms windows with work by busy share \(under 25, 50, 85 %, 85 % or more, and those at the ceiling, where the GPU was the limit at the highest level allowed\) and the longest fully busy run, to tell a GPU-bound frame from one held up elsewhere.
- T43 \(2026-10-28\): zero copy still alternated the new frame with the wallpaper alone with the shown swap held \(586 held to the next latch, 44 by timeout; held swaps also slowed animations, so the compositor waits on the completion\), and no flip ever waited for the GPU. The ring flushes the GPU caches \(CACHE\_FLUSH7, CACHE\_INVALIDATE7\) only in the prologue of the next submission, so a finished frame's last passes reach memory late: the GPU copy read them through those caches, the display fetches memory. T45: sheng-gpu-endflush=1 \(NativeAdreno\) adds CACHE\_FLUSH7 and CP\_WAIT\_FOR\_IDLE before each framed fence.
- T45 \(first build, 2026-10-28\): sheng-gpu-endflush never took effect: this board attaches the ring in package/GpuPowerProbe.cpp \(gRing\), not in NativeAdreno's service, where the boot argument was read. T45b sets it on gRing.
- T46: the GPU was the limit at times while opening apps: of 1098 windows with work, 117 were 85 % busy or more, 111 of them at the ceiling \(level 7\), the longest fully busy run 149 ms. T47 reverts the end flush and the published fence in NativeAdreno \(cd2bbe5, the ring is 1139088's again\) and its setting in GpuPowerProbe.
- T48: GpuPowerProbe exports native\_gpu\_fences \(the ring's submissions and the fence page's completed timestamp\) for the display probe.
- T49-gpuwait \(2026-10-28\): scrolling and app opening keep the GPU at its ceiling. 511 of 1075 waited-on fences stayed pending 8 ms or more \(121 for 16-32 ms\); per-submission cache maintenance cleaned 65 GiB in 114 s \(3.6 s of CPU\); clients made 198049 fence waits, 99 % timing out at once. T51 measures it: GPU time per submission from the submit hook \(NativeAdreno native\_adreno\_ring\_hook\) and the fence interrupt, with GPU idle and queued time; maintenance bytes by kind of buffer; the timeouts clients ask for.
- T51 \(first build\): the board's declaration of NativeAdreno's ring hook carried weak\_import inside an extern "C" block, which makes it a definition; it is now a plain declaration, set unconditionally \(the driver always provides it\).
- T51 \(2026-10-28\): 1979 frames in 118 s, 48 % 17-25 ms apart, 7 % within 9 ms. Swap to GPU done was 8-12 ms for 1180 frames. Per-submission maintenance cleaned 126 GiB \(7.0 s of CPU\), nearly all read-only imports \(127722 MiB counted\): every submission cleaned every client's imports, since the VM is shared. Clients made 573185 zero-timeout fence polls \(about 4900 per second\); the big cores ran 67 % busy. \[gpu time\] stayed empty: its fences were only taken from the GPU interrupt, and the board runs sheng-gpu-irq=0. T52: sheng-gpu-own-maint=1 \(NativeAdreno per-client maintenance\), GPU timing also from the display's flip wait and the governor tick.
- T52 \(2026-10-28\): GPU time per submission, now measured: mean 13.6 ms at level 7 \(n=1035; 371 between 17 and 25 ms\), 9.0 ms with the GPU held at level 9 \(n=1095\), so the time scales with the clock and its bandwidth vote: the GPU does too much work per frame rather than stalling. Per-client maintenance changed nothing \(55 MiB per submission\): the compositor submits nearly everything and owns the imports it cleans. sheng-gpu-irq=1 cut clients' fence polls from 573185 to 13707. T53: the asteroids Turnip patch \(UniXNU patches/mesa/turnip-asteroids-stats.patch\) counts each submission's passes, system-memory passes, blits, draws and render area; \[gpu work\] ties them to GPU time.
- T53 \(2026-10-28\): with Turnip's counts, 5535 of 7713 render passes \(72 %\) ran in system memory rather than GMEM, and submissions with such a pass took 7.4 of the 12.3 s of GPU time \(60 %\); 26153 blits, copies and clears \(about 20 per submission\); 585 single-pass submissions averaged 8.9 ms of GPU time. The draw count read 0 throughout. T54: the reason for each system-memory pass \(tile memory too small, feedback loop, too many tiles without HW binning, autotune and so on\) per submission, tied to GPU time; asteroids-tu-debug=&lt;flags&gt; in the boot arguments adds Turnip debug flags \(gmem, sysmem\) for one boot.
- T54 \(first add-on build\): Turnip with the reason counts compiled; the plugin failed because setTurnipDebug sat inside the publish-only namespace while one caller is outside it. It now sits before that block.
- T54 \(2026-10-28\): every system-memory pass was Turnip's autotune choice \(586 submissions, 6.6 of 10.8 s of GPU time\); nothing forced it. Forcing GMEM \(asteroids-tu-debug=gmem\) put every pass in GMEM and rendered correctly, but GPU time per submission only went from 11.0 to 10.5 ms \(single-pass submissions 11.4 to 9.8 ms\): where the passes render is not what costs. The Reduce Transparency test could not run \(Settings crashes opening Accessibility: Preferences sig 11 at PC 0\). T55: GPU timestamps around each pass, blit, copy, resolve and clear give GPU time per kind \(turnip-asteroids-timing.patch, \[gpu ops\]\).
- T55 \(2026-10-28\): stuck at the Apple logo. Not a GPU hang \(47 submissions in 100 s, the GPU idle\): the wallpaper poster extensions \(AegirPoster, KaleidoscopePoster\) asked for Metal 12 times each and AegirPoster aborted \(signal 6\) on every launch, which no earlier boot showed; \[gpu ops\] collected 14 command buffers and 41 timing brackets that never ran. T56: the brackets are inert unless TU\_DW\_TIME is set, which the plugin does only in the render server with asteroids-tu-time=1.
- Correction to T55: AegirPoster aborted 5 times in T49-gpuwait too, which booted normally, so the poster crashes are an older bug and not why T55 stayed at the Apple logo. What T55 changed is the timing brackets in every process, the render server included, which made only 47 submissions in 100 s with 41 brackets never written. T56 \(timing off\) and T56-time \(timing in the render server only\) separate the two.
- T55-T56 \(2026-10-28\): the cause of T55's hang was the timing stamps, not the posters: fence 52, the render server's first frame, never completed \(51 written\), so every later frame waited and PosterBoard's open was refused once the driver stopped taking clients. T56 \(brackets inert\) booted normally with 913 submissions. T57: the stamps copy the always-on counter with CP\_REG\_TO\_MEM \(as Turnip's autotune does, which runs on every boot here\), the end stamp after a wait for idle; asteroids-tu-time=passes times render passes only.
- T57 \(2026-10-28\): t57-passes hung the same way: fence 55 never completed \(54 written\), and \[gpu ops\] showed 10 command buffers whose 10 brackets were never written. Both stamp methods wrote into the command buffer's sub-stream memory, which Turnip allocates GPU read-only unless marked writeable, and the Darwin backend maps it with read-only permission. T58: the slots come from the sub stream's GPU-writable memory \(tu\_cs\_set\_writeable around the allocation, as Turnip does for GPU-written clear data\).
- T58 \(2026-10-28\): t58-passes booted \(1033 submissions\): the stamps work once their slots are GPU-writable, confirming T55 and T57 hung on writes to read-only command memory. GPU time per submission 10.2 ms mean; timed render passes took 8.0 of its 10.6 s: 1692 GMEM passes 7.2 s \(4.3 ms each\), 4031 system-memory passes 0.8 s \(0.2 ms each, the autotune's small ones\). Untimed in this mode: 19239 blits and the rest \(2.5 s\); a pass's start stamp does not wait for idle, so blits still running when the next pass starts count toward that pass. t58-all brackets the blits too.
- T58-all \(2026-10-28\): with everything bracketed \(998 submissions, 10.5 s of GPU time, 9.8 s inside brackets\): 1636 GMEM passes 7.2 s \(4.4 ms each, unchanged from t58-passes, so no blit time had leaked into them\), 4897 system-memory passes 0.9 s \(0.19 ms\), 20876 copies 1.7 s \(0.08 ms\), 509 clears and 8 blits negligible, no resolves. GMEM passes are 68 % of GPU time.
- T59: asteroids-tu-time=tiles splits each GMEM pass into stages: begin with binning \(to after tu6\_tile\_render\_begin\), the first subpass's loads and clears \(a stamp in draw\_cs under the GMEM render-mode condition\), draws and stores per tile, summed on the GPU with CP\_MEM\_TO\_MEM as the occlusion queries accumulate, and the pass's end; with tile counts, tile size, render area, HW binning and attachments loaded and stored. The totals reach NativeAdreno as SetMetadata tagged TILE \(native\_adreno\_tiletime\) and the log as \[gpu tiles\].
- T59 \(2026-10-28\): t59-tiles booted. 1849 GMEM passes, 8.2 s \(the per-tile stamps add about 1 s over T58\): begin with binning 0.35 s, loads and clears 1.14 s, draws 4.99 s, stores 1.24 s, between tiles 0.50 s, end 0.01 s. 64 tiles per pass \(max 85\) of about 33K pixels for about 2.0 MP of render area: the A810's GMEM is 576 KiB \(NativeAdreno profile 0x90000\), so a full-screen pass is cut into many small bins; HW binning ran in 1499 passes; about one attachment loaded and one stored per pass. Per pixel, these passes ran at about 0.46 MP/ms against about 1 MP/ms for the autotune's system-memory passes \(0.22 MP each\).
- T59-sysmem \(2026-10-28\): every pass forced to system memory \(asteroids-tu-debug=sysmem\): 5900 passes, 7.3 s; 746 submissions, 13.0 ms of GPU time each. GPU time per megapixel of render area was the same as with the autotune's mix \(9677 ms / 4593 MP = 2.1 ms/MP; t58-all 10546 / 5017 = 2.1\): the large passes cost about 2.1 ms/MP in either mode, so tiling is not what makes them slow; their per-pixel work is.
- T60: \[gpu frags\] splits timed passes into large \(1 MP of render area or more\) and small, and takes each pass's draw count and samples passed from the autotune's finished entries \(its BANDWIDTH metric\), so samples per pixel of render area gives overdraw. The turnip-asteroids-stats draw counter had never been sent \(the submit word has no bits left\), which is why the draw count read 0. The totals reach NativeAdreno as SetMetadata tagged FRAG \(native\_adreno\_fragstats\).
- T60 \(2026-10-28\): 634 submissions, 13.4 ms of GPU time each. 1319 large passes took 6.2 s \(4.7 ms each\) for 2.52 MP of render area, the full screen; 2719 small passes took 0.2 s \(70 us, 59K px\). Measured large passes averaged 99 draws \(most 262\) and 9.2M samples, an overdraw of 3.6; small ones 5 draws and an overdraw of 2.3. Large-pass time per sample is about 0.5 ns, about 3.5 samples per clock at the 895 MHz ceiling \(the draws stage, 61 % of a GMEM pass in T59, makes it about 3.2 Gsamples/s\). The large passes are slow because CoreAnimation stacks about 3.6 full-screen layers in roughly 100 draws, each shaded and blended in full; on Apple GPUs hidden-surface removal skips the occluded opaque fragments, on the A810 without a depth buffer nothing does. \[gpu dcvs\] still prints sheng's MHz labels \(220-680\) for the 3a's levels.
- T61: a GPU trace so that new measurements need no new build. asteroids-tu-trace=&lt;letters&gt; \(AsteroidsMetalPlugin.mm, render server only\) sets Turnip's TU\_DW\_TRACE \(UniXNU patches/mesa/turnip-asteroids-timing.patch\): binary records in m2v/gpu/trace.bin of every timed pass \(GPU start and end, render area, GMEM or system memory, tiles and tile size, HW binning, the attachments' formats, load, store, clear, UBWC and tiling, the draws recorded\), every draw \(vertex and fragment shader ids from the stages' BLAKE3, blend enable and factors, write mask, depth and stencil state, scissor, count\), every shader once \(ir3's statistics: instructions, nops, texture and SFU counts, registers, waves, sync stalls\) and the autotune's samples passed per pass. Letters: p passes, d draws, b shader binaries \(1 = pdb\), s each draw's samples passed \(an occlusion-query pair around every draw, accumulated over tiles by the GPU, with a wait for idle after each draw, so GPU time in that mode is not representative\), t GMEM stages, a blits and copies. The file stops at 56 MiB. scripts/gpu-trace.py reports on it \(passes by size with overdraw, large-pass draws by blend state with their samples, the fragment shaders behind them with their statistics, render targets\) and dumps CSV tables and shader binaries; its record layouts were checked against the C structs by compiling them \(118, 60, 76 and 24 bytes\). The Turnip changes compile on Linux against the pinned Mesa with every recorded patch applied \(local/mesa-full, kgsl build in local/mesa-check\).
- T61 \(2026-10-28\): the trace works end to end: t61 booted, 7 export rounds, pull-asteroids-log fetched and decoded it \(5726 passes, 127601 draws, 71 shaders over 35 s, nothing lost\). The Metal bridge records each pass's draws in a secondary command buffer, so draws carry the secondary's serial; gpu-trace.py joins each secondary to the next primary serial, which matches the autotune's draw count for 1567 of 1570 passes. The blend fields are not valid: every draw reads factors 0, 0, 0, because Turnip keeps static blend state in the pipeline and not in the command buffer's dynamic state, where the recorder reads it. Findings, large \(full-screen\) passes, 7.8 s in all: \(1\) 252 passes with 200-400 solid fills take 12.9 ms each \(11.3 ms in system memory, so not tiling\) at an overdraw of 11.8, about 41 % of the time; each fill is a 768-vertex mesh drawn by one of two fragment shaders, vertex color times alpha \(9 instructions\) or the same plus metal2vulkan's exact 8-bit output rounding \(85 instructions: per-channel flags from a constant, scale, rndne, compare, select\), about 151 and 65 per pass. 232 passes with 100-200 fills take 4.0 ms at an overdraw of 2.2. \(2\) 1325 passes with few draws \(about 8, overdraw 0.19\), mostly with the attachment loaded and stored, take 2.3 ms each in GMEM and 1.7 ms in system memory, about 38 %; 155 with no draws at all take 0.8 ms. The exported screen is the console layer \(black under zero-copy scanout\), so it does not show the scene. ir3-disasm from the local Mesa build \(local/mesa-check, chip ffff44010000\) disassembles the trace's shader binaries.
- T61-samples \(2026-10-28, asteroids-tu-trace=pdbs\): the per-draw sample counters ran without a hang \(101786 draws, 37 s; GPU times not representative: a wait for idle after each draw\). Large passes drew 9.98 G samples. The 768-vertex solid fills that dominate the draw count are tiny \(about 325 pixels each for the 9-instruction one\); the pixels go to shaders that end in metal2vulkan's exact 8-bit output rounding \(saturate, NaN test, x255, rndne, compare with +-0.5, correct, x1/255, select by per-channel flags from c4\), about 50 instructions on top of 5-15 of real work: 31 of 66 fragment shaders, 71 % of the samples and 95 % of the instruction-weighted work. The largest single consumer, 6238666134616236 \(interpolated color then the rounding, 82 instructions\), drew 4.9 G samples at 1.67 M per draw. Upstream development removed this rounding \(70068f7c, 'Leave color writes to the device's own conversion', 2026-10-28\); the pinned translator only skips it for drivers it has measured \(VkProperty::MetalColorWrites, MoltenVK\), with no option to set it. Light passes \(fewer than 20 fills\): 1199, median coverage 0.19 of the screen, 58 % under a quarter, mostly loading and storing the whole attachment \(GMEM 621, system memory 517\).
- T61-stages \(2026-10-28, asteroids-tu-trace=pdbt; gpu-trace.py now splits large passes by coverage, the autotune's samples over the render area\): large GMEM passes drawing under a quarter of the screen \(459, about 85 tiles, 20 draws\) took 2.7 ms each: loads 0.90, draws 0.45, stores 0.94, between tiles 0.38 ms, so about 80 % is loading and storing the whole attachment around a small change; large system-memory passes at the same coverage \(66\) took 0.17 ms. At coverage 1-3 GMEM took 4.5 ms \(draws 2.9\) against 2.3 ms in system memory \(8 passes\); at 8 or more, 13.7 ms with 12.0 ms of draws. The autotune still chose GMEM for most light passes. Load and store run at about 11.5 GB/s each way \(10.3 MB of BGRA8 in 0.9 ms\). T62 plan: metal2vulkan updated to development \(exact output rounding removed\) plus a toggleable Turnip choice of system memory for passes whose history draws little of their area.
- T62 \(2026-10-29, built, not booted\): metal2vulkan moves to development eeb79340 \(UniXNU a49a8dd\), where color writes are the device's own conversion \(70068f7c\) and float maths the device's \(4817f3bdf, cdc09276f\), removing the exact 8-bit output rounding that T61-samples found in 95 % of the large passes' fragment work. The bridge is rootstockos/AdrenoMetal asteroids \(137eeb1, forked from UniXNU/AdrenoMetal\): the 16 shared patches and sheng's 21 from feat/ipados27-gpu-parity \(which stays on the old pin\) were triaged against development; 17 remain \(skip draws without a pipeline, two-plane shadow as memory lies, padded framebuffers through a new PaddedRowsPolicy::AliasWrites since development removed padded-row aliasing, priming cache, refuse\_rebinds now actually set by the bridge, optional shader cache, sRGB extended-range blend, bitreverse, growing memory blocks, patches without control points, heap texture size, Core Image libraries and two small speedups\); the rest \(keep final pass, fewer allocations per draw, keep draw commands and lists, map tracker keys, and most of sheng's draw-path patches\) are done in development by LiveBind, SpareLiveBinds, ViewportList and KeptRenderPasses. Turnip: asteroids-tu-light=&lt;percent&gt; \(TU\_DW\_LIGHT, render server only\) renders a pass in system memory when its history draws less than that share of its area \(T61-stages: 2.7 ms in GMEM against 0.17 ms in system memory for passes under a quarter of the screen\); trace pass records flag such passes \(4\), and draws read the pipeline's static blend state. Not covered: the translator's own tests beyond the touched areas, and any device run.
- T62 \(2026-10-29\), every Metal process on the GPU, as sheng's iPadOS 27 branches do \(UniXNU-sheng 9800f8cd\): drivers/Adreno740 merges UniXNU/Adreno740 feat/ipados27-gpu-parity \(rootstockos/NativeAdreno asteroids ad01b92\): no connection cap, growing object, queue and job tables, a BO pool of contiguous chunks, msm hangcheck and restart, and per-process GPU address spaces \(own page table and ASID, 4 GiB to 2^ias\) switched into the GPU's bank: mode 2 by CP\_SMMU\_TABLE\_UPDATE in the ring, only where the board opened the CP's SMMU aperture and one switch is proved at publication, else mode 1, the CPU writing TTBR0 with the GPU idle. This board keeps mode 1: asteroids-gpu-cp-aperture=1 makes sheng's qcom\_scm\_set\_gpu\_smmu\_aperture call \(off: the CP switch has not run on an A810\). Kept from this fork in the merge: the gen8 slice SRAM init before the table switch, the reserved GMU pool \(its table pages now on demand\), single-stream contexts, per-client maintenance, and the loader-kept BO pool \(adoptPool\) as an adopted chunk of the chunked pool \(write-combined, zeroed with stores, never given back\). The merge had refused a nonzero submit reserved word, which carries the asteroids Turnip's counts; that check is gone. The board publishes the context's ias with va\_start GpuClientVaStart and grants the accelerator to every process \(NativeSandboxGrantProcess "\*"\); the plugin's client list is "\*". UniXNU 2b79721 takes sheng's Turnip backend for the new ABI \(address allocator, BO cache returned under pressure\) and ArmSmmu4K 30ec63b. Host tests on Linux \(GMU and GPU contexts, the board GMU pool, VM, SMMU memory, GMU memory and map\) pass; the kernel, board and Turnip backend only build on CI.
- T62 first kernel build \(run 40785590664\) failed to link: \_native\_pmap\_user\_mappings, which the merged NativeAdrenoMemory::release weak-imports from sheng's XNU patch for a diagnostic count; GpuPowerProbe.cpp now defines a weak stand-in that finds no mapping, as it does for boot\_log\_export\_put. The add-on \(run 40785594609\) built: metal2vulkan development, the bridge, sheng's Turnip backend and the plugin compile for iOS.
- T62 \(2026-10-29, booted\): slower, with more glitches: the kernel's grant patch \(UniXNU zzw-native-adreno-sandbox-grant\) compared NativeSandboxGrantProcess "\*" as a process name, so no process had the grant: the sandbox refused AGXDeviceUserClient to backboardd and the apps, Turnip reported no device \(VK\_ERROR\_INITIALIZATION\_FAILED\), the render server composited on the CPU \(71 ms a frame\) and crashed twice \(an alignment fault on a store\), and only SpringBoard and Preferences, whose profiles allow the class, opened the GPU. The gpu-trace in that log was T61t's file left on the persistent Data. UniXNU feb5612: "\*" names every process.
- T62b \(2026-10-29\): backboardd and seven apps each on their own GPU address space \(mode 1 table switches\), no crash, but no faster than T61: 12.2 ms of GPU time per submission against 12.0, 2.7 ms per megapixel of render area against 2.2 \(the apps' own rendering now counts too\), compositor 52 ms a frame against 47; mapping into the per-process tables took 492 ms in all against 25. No trace file: m2v/gpu was missing on the phone \(Turnip makes only its last directory\).
- T62b-light \(2026-10-29, asteroids-tu-light=100\): no felt difference; it froze after many app opens. At 352-358 s the 1 GiB BO pool filled \(1023 MiB in use, backboardd 873 MiB, seven GPU clients\), 61 BOs fell back to scattered pages, and the render server's submission 1490 never completed: no SMMU fault, no recovery, every later wait timed out. Photos and ScreenshotServicesService aborted on an uncaught exception \(\!PXPixelSizeAreaIsZero\(roundedSize\)\). Sheng's answer, user BOs from system memory with no pool \(Adreno740 882f4bf\), would move them into XNU's 4.75 GiB window, where 849 pages were free; the loader-kept GiB would then go unused unless the window takes it back. Not merged.
- T63 \(2026-10-29, built from UniXNU 2ee276c\): the Metal stack is sheng's: drivers/AdrenoMetal is UniXNU/AdrenoMetal feat/ipados27-gpu-parity ca7faaf \(rootstockos/AdrenoMetal asteroids b4fb935\), metal2vulkan development 624bab39 under sheng's 18 bridge patches \(all apply; in-place written textures replace T62's padded-rows policy\), with the encoding thread, the telemetry table \(the boot log's rows from native\_adreno\_metal\_rows, empty until now\), priming from the OS image's 159 metallib paths \(scripts/data/prime-list.txt, embedded in \_\_DATA,\_\_primelist\), cache import \(off here: the driver has no method 0x7101\) and the half-float scanout conversion; GopFramebuffer 90b64ef for its header only \(the kernel builds this repository's fork\). package/AsteroidsMetalPlugin.mm is sheng's plugin with this board's diagnostics: the asteroids-tu-\* boot arguments \(and the trace's directory made whole\), the render server's stacks as BT pieces, the stack-only mode, supportsConditionalLoadStore answered NO, the deep framebuffer off by preference with sheng's render-server memory writes removed, and the clients list. The kernel and Turnip are T62b's.
- T64 \(2026-10-29\): the GPU's BOs move into XNU's memory. drivers/Adreno740 merges sheng's feat/ipados27-gpu-parity again \(rootstockos/NativeAdreno asteroids c24a81c\): user BOs are pageable system memory the driver wires \(882f4bf\), no fixed pool, the import region method 0x7101 \(aa015f7\); this fork keeps adopt\(\) for the GMU pool. GpuPowerProbe no longer tests and adopts the loader-kept pool \(mode 17 step 1\), GPB\_GPU\_POOL\_\* and board.toml gpu\_pool\_\* are gone, and the boot log's \[bo pool\] row is \[bo memory\] \(system BOs, spans, MiB in use and peak, refusals\). The loader's map \(uefi-asteroids\) drops GPU\_Pool and the window grows to 7.75 GiB \(memory area\). Host tests on Linux pass \(GMU and GPU contexts, VM, system memory, SMMU memory, GMU memory and map\) except test\_memory's stale 256 MiB budget check, as before the merge.
- T64 first kernel build \(run 40832768114\) failed to link: \_native\_ufs\_import\_blocks and \_native\_ufs\_import\_read, which the merged driver's import method 0x7101 \(aa015f7\) weak-imports from sheng's ShengUfs; GpuPowerProbe.cpp now defines weak stand-ins that report no region, as for native\_pmap\_user\_mappings, so the method answers not ready and the plugin's cache import stays off.
- T64 at 6 GiB \(2026-10-29\): booted, but every process rendered on the CPU: no Metal askers, no GPU clients, no ASTEROIDS GPU report lines. The kernel client's test \(mode 17\) ran its steps \(6 system BOs allocated and mapped, 34 submissions completed\) yet missed, so the accelerator was never published \(dcvs off, no userWatch\); its result lines had left the kernel buffer, the board kept no row of them, and this boot's unified log never reached Data. GpuPowerProbe now keeps the round, burst and summary lines \(native\_gpu\_uc\_text\) for BootLog's \[gpu uc\] rows, and asteroids-gpu-publish-unverified=1 \(off by default\) publishes despite a miss, to see whether user space renders while the test fails.
- T64b and T64b-nomedia \(2026-10-29\): the kernel's own test passed \(rounds 4/4, burst 32/32\), but the first user job \(fence 41\) never completed, from mediaserverd and, with mediaserverd off the client list, from backboardd: GPU 99% busy, no SMMU fault, the ring read pointer past the IB packet. T63 \(T62b's kernel, the loader-kept pool, the same add-on\) ran well: 1703 submissions at 7.3 ms of GPU time, compositor 33 ms a frame. A host walk of scattered BOs in a 48-bit per-process table found every page right \(833 pages\), so the tables are not it. xnu-10063 zero-fills a system BO's pages through the cacheable kernel alias and then sets the write-combined attribute without cleaning a line \(pmap\_batch\_set\_cache\_attributes cleans for VM\_WIMG\_RT only\); sheng's allocateSystem cleans only default-attribute BOs. NativeAdreno 4063b92 cleans and invalidates every write-combined system BO by physical address after the VM hands it over. GpuPowerProbe now gives the driver a DRAM reader \(ml\_phys\_read\_word\), so a stall's \[gpu stall\] rows can show a system BO's words instead of deadbeef.
- T65: drivers/Adreno740 takes NativeAdreno 5e2b23e: user BOs come from a pool reserved at GPU bring-up again \(sheng's ad01b92 chunks, sheng-gpu-pool MiB, default 1536, without the adopted range\), one span each, system memory when it is full. T64c's system BOs left 228876 owned spans live, VM insert/erase 641/841 ms against T63's pooled 61/74 ms, BoAlloc/Map/Free 196/457/940 us against 59/146/222, compositor mean 139 ms against 33 ms.
- T65: GpuPowerProbe makes sheng-gpu-import-skip default to 1: T63 spent 89 GiB \(about 3 ms of each 4.4 ms submission\) cleaning read-only imports every submission; T40f measured skipping it at 7x cheaper submissions with no stale content.
- T65 \(2026-10-29\): the pool served all 2029 BOs \(peak 789 MiB, none to system\), VM map/unmap 148/130 ms, import cleaning 0; compositor frames under 8 ms 82 % \(T63 63 %, T64c 28 %\), flip gaps under 9 ms 44 %, GPU 7.1 ms a submission. Felt better but not 120 fps.
- T65-sysmem \(asteroids-tu-debug=sysmem\) and T65-1050 \(level 9, 18.6 GB/s DDR vote against 8.17\) repeat T59 and T52/\[gpu 3\] with today's stack and change nothing felt: large passes 2.2 ms \(sysmem\) and 2.57 ms at overdraw 2.8 \(1050; 0.36 against 0.39 ns a sample\), near-empty linear load/store passes about 2.4 ms in GMEM either way. Neither tiling, GPU clock nor the DDR vote limits the frame. Not yet tested in any log: sheng-dpu-early-done=1 \(T52, NativeLegacyDisplay\), which ends T51's serial compositor -&gt; GPU -&gt; latch chain.
- T65-early \(2026-10-29, sheng-dpu-early-done=1, its first run\): worse. Flip gaps under 9 ms 21 % against T65's 44 %, swap to screen 11.6 ms against 6.7, GPU queued 8.0 s in 1508 submissions against 16.4 s in 5464, GPU time 9.3 ms a submission against 7.1, 632 of 1047 work windows at the ceiling. Freed from the latch, the compositor only queues more GPU work, so the serial chain is not the limit: the GPU's work per frame is. Stays off.
- T65-samples \(2026-10-29, asteroids-tu-trace=pdbsa, first measurement of occlusion; local/triage/occlusion-from-trace.py\): 1317 large passes, 8.44 G samples, 69 % from opaque draws \(blend off\). At least 3.70 G \(43.8 %\) were shaded under a later opaque draw covering 95 % or more of the pass \(575 passes have one\); counting partly covering opaque draws as independently placed, about 56 %. Turnip saw no feedback loops \(sysmem reason 0\), so these draws do not read the destination. On Apple GPUs hidden-surface removal skips them; here a translator-side depth order \(opaque draws front to back with depth writes, then blended draws in order with the depth test, LRZ rejecting\) would.
- Metal against Vulkan passes \(the plugin's S row against the trace\): T65 26407 Vulkan passes and 11291 full-screen against Metal's 24253 and 9590 with draws equal to 0.4 % \(+18 % full-screen\); T65-samples, scaled by draws \(trace 91 % of Metal's\), about +5 %. metal2vulkan adds some full-screen passes, between 5 and 18 % in these two runs; which ones is not yet known.
- T73 \(2026-10-30, T72's Turnip rule of passes under 100 draws in system memory unprofiled, UniXNU 7dd0abb; reverted in b239c19\): no such pass ran in GMEM \(T71: 1106\), and it felt worse than T71. Per full-screen pass, 25-99 draws cost 0.94 ms mean against 1.86 ms, under 25 draws 1.66 against 1.67 ms: T71's 89 us system-memory median came from the autotuner sending only cheap passes there. The run drew 4.9 full-screen passes a frame against 3.2 \(GPU 18.3 ms a frame, flip gaps under 9 ms 17 %\), so whole-run numbers do not compare.
- The extra Vulkan passes \(2026-10-30, metal2vulkan 624bab39 with the bridge patches, render/inline\_first.rs\): a compositor pass opens inline with its memoryless color in a transient image; a later draw that writes that color splits the pass \(WorkCounts::inline\_memoryless\_write\_splits\), and the new instance loads and stores both attachments. The traces show it as back-to-back full-screen pairs in one command buffer, the first clearing the second attachment and the second loading and storing it: 2002 in T65 \(against about 1700 full-screen passes more than Metal\) and 343 in T71. The split itself costs little: the gap between the halves is a median 13-48 us \(T73: 221 splits, 11 ms in 55 s\), and most second halves render in system memory, where their loads and stores cost almost nothing; their own time \(T71 516 ms, median 1.6 ms\) is draws that run either way. Not worth changing for frame time. metal2vulkan also stores Metal's DontCare attachments on Turnip \(no measured DriverFact\) and always renders over the whole attachment.
- T74s \(2026-10-30, T71's Turnip with asteroids-tu-debug=sysmem, every pass in system memory\): no red/blue colour flips, which T70 to T74 showed from time to time. So the flips come from GMEM rendering of the screen surface, a linear 1080x2392 IOSurface whose height is not whole GMEM blocks, which sheng's turnip-render-mode-for-attachment-memory.patch \(UniXNU ca59120\) loads with a 3D blit and stores with the unaligned CP blit \(store\_cp\_blit, its swap chosen as if GMEM ignored the attachment's swap\). Not yet narrowed to the load or the store.
- T75 \(2026-10-30, UniXNU e0f3223, add-on only\): three changes from the open/close analysis. \(1\) The compositor's surface renders in SYSMEM \(Turnip: a linear attachment over unpadded owner memory never takes GMEM\), the fix for T70-T74's colour flips. \(2\) Priming in list order with scripts/data/prime-list.txt led by QuartzCore and CoreImage, the other system frameworks next, applications last, MTLReplayer dropped: T74's priming read the list as a sorted set, spent 88 s on MTLReplayer's ray-tracing kernels \(201 of 264 refused\) and never reached QuartzCore. \(3\) Frame traces per process in m2v/gpu \(frames-&lt;pid&gt;.trace\), exported with the GPU trace: the shared frames.trace was truncated by every process's writer. From T74b's telemetry: commit to scheduled about 3 ms per command buffer \(2578 waits for it, 7.3 s\), commit to completion callback 23 ms mean against about 5 ms of GPU work, and the render server starts each frame from the previous one's completion \(the bridge's earlyOn, reverted by sheng for blur reading unfinished frames\). Ruled out by counters: write-combined reassertion \(0 ms\), surface cache flushes \(1.7 ms in all\).
- T76 \(2026-10-30\): the board classes here register through OSKextRegisterBoardClasses \(zzyg-board-class-registration.patch\), under the kext lock, in place of preModLoad/postModLoad alone, which deadlocked T75f's boot \(storage area\).
- T75 \(2026-10-30, add-on 23 on the T73 kernel\): no colour flips; open and close felt no faster, so priming \(which reached QuartzCore first\) was not the stutter. Its per-process frame trace \(frames-56.trace, backboardd, 1960 command buffers in 76 s\): heavy command buffers \(120 draws or more, n=1126\) took 2.8 ms from creation to commit on the render thread, then 8.1 ms median from commit to scheduled and 20 ms to completion \(p90 38 ms\); light ones \(under 60 draws\) waited 11.2 ms to be scheduled, queued behind heavy ones on the bridge's serial encode thread. The render server waited for scheduled 867 times \(2.2 s\). Big cores averaged 2.1-2.3 GHz during the animations \(\[cpu gov\]\), so the encode thread's Vulkan recording and submission, about 40 us a draw, is the gap before each heavy frame's GPU work.
- T75f \(2026-10-30, T75 with sheng-cpufreq-min=3000, every CPU at its highest level\): heavy command buffers took 2.9 ms to commit and 8.5 ms from commit to scheduled, as in T75 \(2.8 and 8.1 ms\): the governor already held the big cores at 2.4-2.5 GHz, 88-96 % busy, during the animations. Light ones fell from 11.2 to 1.6 ms \(the floor only helps between animations\). The 8 ms is CPU work on the bridge's encode thread at full clock. T76: the bridge samples that thread with asteroids-sample=1 \(AdrenoMetal 9db50e8, m2v/gpu/cpu-&lt;pid&gt;.profile\), and the add-on artifact carries NativeAdrenoMetal.unstripped and libvulkan\_freedreno.unstripped to symbolize it.
- T76's first kernel build \(run 41109301209\) failed: XNU has no kOSReturnNoMemory; OSKextRegisterBoardClasses and its callers use kOSKextReturnNoMemory \(libkern/OSKextLib.h\), and the helper has a prototype before its definition.
- T76's second kernel build \(run 41111730079\) failed in ShengPlatformPower.cpp: BoardClasses.h had been included after the file's last \#include, which there sits inside the ShengPlatformPower class; every probe now includes it after its first \#include.
- T76's third kernel build \(run 41114667427\) hung for 25 minutes in the CI bootstrap's GitHub fetch of the pinned Linux sources for the GMU header, which had no time limit, so kernel.org's fallback never ran \(cancelled\). prepare-asteroids-gmu.py now gives a source up when it sends under 1 KiB/s for a minute or takes 15 minutes, and falls back as on a refusal.
- T76 \(2026-10-30, kernel with the class registration fix, which booted; add-on 24 with asteroids-sample=1\): the encode thread's profile \(cpu-56.profile, 34064 samples\) found it idle in condition\_variable::wait for 88 % of samples and in kernel calls for 6.5 %, so the 8 ms from commit to scheduled \(T75\) is not its work: metal2vulkan holds a submission while two of its queue's run \(command\_buffer/group.rs\), and the GPU is the busy one. \[gpu work\]: single-pass submissions averaged 8.8 ms of GPU time \(1142, 10062 ms\) against about 2 ms for a traced full-screen pass; 38967 blits in 2237 submissions; \[gpu load\] 492 windows at 85 % or more at the ceiling level. The pass trace times render passes only, so the earlier finding that late frames left the GPU idle was wrong. Most blits are copies into shadowed textures \(L row: 568 shadowed, 32701 copies in\): metal2vulkan copies every byte of a host-page texture each time it is used unless the platform gives it a dirty-page log \(dirty\_pages.rs, HostMemory::with\_dirty\_pages\), and the bridge gives none.
- T77 \(2026-10-30, T76 kernel, add-on 25 with the SR/SC rows from AdrenoMetal 517b87c, asteroids-tu-trace=pdba, which times every copy, blit and clear\): the class registration fix booted again. 112 host-page textures were shadowed, 53 for their pitch and 59 for their placement \(no other reason, no in-place check ran\), and their copies in moved 3518 Mi texels, nearly all from host pages \(about 14.7 GB\). In the trace \(76 s\), copies took 1223 ms of 3938 ms of timed GPU work \(31 %, 7905 copies, median 144 us\), system-memory passes 2344 ms, GMEM passes 365 ms. \[gpu time\] \(7642 ms, n=933\) is not GPU execution: GpuPowerProbe measures from submission until the CPU notices the fence \(GPU interrupt with sheng-gpu-irq=1, flip wait or governor tick\), so it includes late wakes \(T39b: 72 % late\); T76's reading of the GPU as busy was overstated. backboardd's heavy command buffers took 24.7 ms median from commit to completion \(13.4 ms to scheduled\) against about 6 ms of traced GPU work; light ones 3.7 ms. Next, T77i \(packed, not booted\): the same image with the board default sheng-gpu-irq=0 \(spinning fence waits\), to see whether completions noticed late hold back metal2vulkan, which submits only once fewer than two of its queue's submissions are outstanding.
- T77i \(2026-10-30, T77 with the board default sheng-gpu-irq=0\): completion detection is not the open/close bottleneck. With the GPU line detached, a caller's fence wait \(NativeAdrenoPublish.cpp runCore\) polls with 20 us IODelay pauses \(314600 pauses for 10898 waits\), so completions are seen within tens of microseconds; the mean wait barely changed \(1.86 ms in T77, 1.94 ms\). backboardd's heavy command buffers \(2073, about 7x T77's 294: 42 open/close bursts against 6\) still took 24.15 ms median from commit to completion \(T77 24.73\) and 10.88 ms to scheduled \(13.38\); light ones 5.32 ms \(3.73\). Per burst, heavy command buffers ran at a median 66.5/s \(T77 56.2, from 6 bursts only\), with 15 % of their commit intervals over 33 ms \(21 %\). \[gpu time\] does not get more accurate with the line off: gpuTimeFences runs only from the interrupt, flip wait, governor tick and native\_gpu\_fences, not from the ring's polls \(191 batched detections against 1\). The 24 ms is not a late wake.
- Review of T77/T77i \(2026-10-31, local/tools/gpubusy.py and passes.py on trace.bin\): T77's 'about 6 ms of traced GPU work' per heavy command buffer and its reading of T76's busy GPU as overstated were wrong. Merging the trace's GPU start and end stamps of every pass, copy, blit and clear, backboardd's own work kept the GPU busy 65 % of the animation bursts' wall time in T77 \(3757 of 5814 ms\) and 75 % in T77i \(24544 of 32761 ms\), about 12 ms per heavy command buffer: render passes in system memory 62 %, copies into shadows 32 % \(T77i: 52261 copies, SR pitch 263 and placement 419, 22697 Mi texels in\). The commit-to-scheduled wait is metal2vulkan's CompletionPolicy::Grouped \(the bridge keeps the UNTRUSTED default\) holding a group while two submissions of its VkQueue are outstanding, so it is queueing on the GPU too; nothing between the commit and the ring makes the CPU wait for the GPU \(Turnip's Darwin backend emulates timelines in DEFERRED submit mode and resolves waits to ring fences\), and the completion waiter reaches the kernel's fence wait. The GPU's work per frame stays the limit, as T52 and T65-early found: the levers are the copies \(T76's dirty-page log\) and the occluded samples \(T65-samples\). Untested: turnip-a810-sysmem-ccu.patch halves the system-memory colour cache for every pass, those without depth included. The trace's binning flag is set only in staged mode \(TU\_DW\_TIME=tiles\), so pdba runs read 0 for every pass.
- T78 \(2026-10-31, add-on only, measurements behind letters of asteroids-tu-trace since the command line is at 976 of 1000 bytes\): q \(UniXNU patches/mesa/turnip-asteroids-submit-trace.patch\) records each kernel submission in trace.bin, CLOCK\_UPTIME\_RAW ns before and after it \(the frames trace's clock\) and its command buffers' serials, so local/tools/gaps.py can fit the always-on counter to the CPU clock and file every GPU idle gap of 1 ms or more in the bursts as kernel \(submitted before the gap\), held \(a commit before the gap not yet scheduled\) or late \(nothing committed\); h \(AdrenoMetal NativeMetalObjects.rs DirtyMeasure\) gives every no-copy memory a dirty-page source that never answers, so the runtime still copies every byte but counts the copies a log would decide, while a utility thread hashes the watched pages at most four times a second and counts the unchanged ones weighted by stamps, and each watch notes whether its pages are private or shared \(boot log rows DP, DW, DH\); c \(patches/mesa/turnip-a810-sysmem-ccu-color.patch\) gives system-memory passes the whole 128 KiB colour cache and half the depth cache in place of half colour and whole depth \(480 of 576 KiB with the VPC buffers\), an A/B against the halved colour cache. Planned boots: pdbaq \(the gaps, and the cache A/B's base\), pdbaqc \(its other side, compared per pass of each kind\), pdbaqh \(the copies; h moves the gated copies' recording to submission and adds a hashing thread, so its timing is not compared\), pdbsa \(occluded samples on today's stack\).
- T78q \(2026-10-31, asteroids-tu-trace=pdbaq, 104 s\): the GPU waits for work, not only the reverse. local/tools/gaps.py fits the always-on counter to the CPU clock by the GPU's idle periods \(offset 1.40 ms, drift -2.1 ppm; 424 of 446 idle periods of 5 ms or more ended 0-1 ms after a submission returned; the traced serials can't be used, since each submission starts with untraced shadow copies, serial 0\). In 18 bursts \(24380 ms\) backboardd's work kept the GPU busy 76 % \(system-memory passes 12220 ms, copies 5713, GMEM 523\); gaps of 1 ms or more took 5704 ms \(23 %\): the GPU idle with work already in the kernel 173 ms \(29\), held 3126 ms \(723, median 3.0 ms: a command buffer committed before the gap not yet scheduled\), late 2405 ms \(352, median 6.1 ms: nothing committed\). Completion is seen on time \(completion callbacks a median 0.3 ms from the GPU end of their traced work\), and the Grouped hold is not what holds: only 81 of 1223 command buffers queued behind another were scheduled within 0.5 ms of a completion, and at their scheduling 0 \(423\) or 1 \(687\) of the queue's submissions were outstanding. Commit to scheduled grows with the command buffers committed earlier and not yet scheduled, whether the GPU is busy or idle: none 2.8 ms median with the GPU idle, one 12.7 ms, two 21.9 ms; a queued command buffer is scheduled a median 9 ms after the one before it, in two modes \(under 0.5 ms or about 10-13 ms\), with no relation to its copies or draws. So a serial stage on the CPU between commit and the kernel submission holds the work: the encode thread \(it runs every encoder call's runtime half and then the commit, NativeBridgeMetalFrontend.mm submit\) or metal2vulkan's scheduler thread; the trace has no stamp between them. The review's 'the GPU's work per frame stays the limit' holds for 76 % of the bursts, not for the idle 23 %. CoreAnimation waited for scheduling 933 times \(2631 ms\) and for completion 41 times \(508 ms\), counted only after encodeDrain, so its time waiting for the encode thread to catch up is not in either.
- T78c \(2026-10-31, asteroids-tu-trace=pdbaqc, 86 s\): the whole colour cache for system-memory passes \(turnip-a810-sysmem-ccu-color.patch: colour full, depth half\) does not help. Matched against T78q by mode, the colour attachment's load and store, area and draws \(local/tools/t78/ab.py\), the cells with the same work ran 1-5 % slower \(full-screen SCut with 64 or more draws 4354 to 4528 us, LSut 5021 to 5189, LS 9998 to 10253\); the cells that moved more \(+352 %, -54 %\) differ in their work between the runs, since draws are capped at 64 in the match and the apps opened were not the same. The bursts were the same as T78q: GPU busy 76 % of 19847 ms, gaps of 1 ms or more 23 % \(kernel 181 ms, held 2492, late 1814\). The patch only acts behind letter c and goes with the next build.
- T78h \(2026-10-31, asteroids-tu-trace=pdbaqh, booted twice\): the measurement crashes the render server. The first boot was left untouched \(its static stacks and idle CPU were an idle phone, not a freeze\); in the second \(112 s, used from the start\) backboardd died with SIGSEGV four times \(pids 56, 262, 270, 279, each after 10-20 s of use\), every time at the same instruction with ESR 0x92000007 \(a read, translation fault at level 3\) at a page-aligned address, on a Rust-spawned thread: the bridge's hashing thread read the first word of a watched page that was no longer mapped. A watch lives until metal2vulkan drops its shadow log, and the watched memory \(all of it shared with other tasks: 74 sources, 37 watches, 52 MB, no private pages\) can be unmapped before that, so the thread's alive flag does not keep the pages. What the counters had in one render server's life: 72 shadow copies in \(L row cp 73\) of which 72 gated and copied whole as designed \(94 MB\), so the gate does cover the shadow copies in; the hashing gave no share of unchanged pages \(2 rounds, nearly every page first seen\). The fix is in the measurement: read the pages with mach\_vm\_read\_overwrite, which fails on an unmapped page, instead of loading them.
- T78s \(2026-10-31, asteroids-tu-trace=pdbsa, 90 s, no render server crash\): the occlusion T65-samples measured is unchanged on today's stack \(local/triage/occlusion-from-trace.py, the same script\): 2751 large passes with per-draw samples \(46 without\), 18.05 G samples, 70 % from opaque draws; at least 7.87 G \(43.6 %\) were shaded under a later opaque draw covering 95 % or more of the pass \(1290 passes have one; T65-samples 43.8 %\), and about 56.1 % counting partly covering opaque draws as independently placed \(T65 about 56 %\). Opaque draws are nearly all either tiny \(43711 under a tenth of the pass\) or full-screen \(4332 at nine tenths or more\), so the lower bound is the part a whole-draw rule could take: drawing nothing before a later full-screen opaque draw in the same pass.
- T78s, what the hidden pixels cost \(local/tools/t78/pxcost\_s.py, hidcost\_strict.py\): large system-memory passes that load and store the screen \(LS, 2412\) follow their pixels, time = 342 us + 340 us per million opaque samples + 473 per million blended \(R2 0.90; the s letter's wait after each draw goes into the per-draw term\), opaque pixels about 61 % of their time: 0.34 ns a pixel is about 11.7 GB/s of 4-byte writes, T61's DRAM rate, so in system memory every shaded pixel is a DRAM write. That is why T69's depth prepass lost \(it added a full-screen depth buffer's traffic to every pass\). But what a draw-skipping rule could drop safely is small: of the opaque draws over 95 % of a pass, 1694 cover all of it and 2572 cover 97-98 % \(the rest of the screen still shows earlier draws\), and before a cover of the whole pass with all four channels written there are 2.62 G opaque samples in LS passes \(30 % of theirs, about 0.9 s at that rate\) and almost none in SC passes. On T78q's bursts that is about 1.1 of 18.5 s of GPU work, near 5 %, and the translator cannot know a draw covers the pass when it records it \(its positions come from the vertex shader\). The 43.6 % share counted the 97-98 % covers as hiding everything before them; hidden pixels are not a large lever by any rule known to be safe.
- T79 \(2026-10-31, add-on 27, UniXNU 03a1d0c, AdrenoMetal 4ea92e4\): the shadows' cause, not their cost. metal2vulkan answers Metal's 16 bytes for a linear texture's offset and rows in a buffer \(deviceLinearTextureAlignmentBytes, minimumLinearTextureAlignmentForPixelFormat:\), while Turnip's linear images on the A810 start and step their rows at 64; QuartzCore lays out its textures over buffers by the device's answer, so the runtime bound none in place and shadowed each, copying every byte in before every use \(every shadow in T76-T78 was for pitch or placement\). The bridge now answers 64 for those queries and the linear private counts \(NativeMetalObjects.rs LINEAR\_IN\_PLACE\); the runtime still takes 16, so a texture placed by the old rule is shadowed as before; the IOSurface answers stay 16 \(no IOSurface texture was shadowed\) and the frontend's iosurfaceReadOnlyTextureAlignmentBytes asks for that answer instead of the linear one. Whether QuartzCore asks the device for each of these textures is what the boot shows: the SR row's pitch and placement counts and the trace's copy time against T78q. The same add-on carries the dirty-page measurement's fix \(pages read with mach\_vm\_read\_overwrite, DH gone counts the unmapped ones\), frame trace types 6 \(a commit's runtime half on the encoding thread, with the thread's CPU time\) and 7 \(encodeDrain waits\), to split T78q's commit-to-scheduled delay, and drops the colour-cache A/B. Planned boots: pdbaq, then pdbaqh if shadows remain.
- T79q \(2026-10-31, two boots of pdbaq\): the copies went and the picture broke. Copy time over the run fell from 5839 ms \(T78q, 65 s\) to 136 ms \(115 s\); the L row's textures in place rose from 220 to 415, of them at Metal's pitch 31 to 18; shadows for pitch fell from 236 to 3, for placement stayed \(202 to 281\). The open/close animations felt smooth. But small textures were scrambled in blocks: text \(Settings' title and rows, the App Library's labels, with a garbled copy below\), the Dock's and Settings' icons and the wallpaper's blurred shadow, while full-screen layers, the clock's digits and the App Library's large icons were clean \(photos, no screen capture: the diag frame is the teardown's text\). Every texture over host pages is bound in place unchecked \(HostPageTexturePolicy::InPlaceWrites\), so the scrambled ones are read through a linear image. Turnip steps a linear image's rows at 64 bytes a texel byte \(256 for BGRA8, 64 for R8; fd6\_layout.c\) and takes an explicit layout at 64 bytes; the textures newly in place are mostly at Turnip's own step, so 1- and 2-byte mask textures \(glyphs, blurred shadows\) are the likeliest; the explicit-pitch ones were already in place in T78q without visible damage, which argues against them. Not settled: no log said which formats went in place. requiredLinearTextureBytesPerRowForDescriptor: still padded rows to 16 while the queries answered 64. The first boot also ended backboardd with SIGKILL at about 70 s \(cause not found\); the second had a Photos abort \(MobileSlideShow sig 6\), not looked into.
- T80 \(2026-11-01, UniXNU f2ce6cc, AdrenoMetal 13b40af\): one add-on, the answer picked by TU\_DW\_TRACE letters: o the runtime's 16 \(T78's layout, to show the build itself is clean\), w 64 texels \(Turnip's own step: 64 bytes a texel byte, 256 where no format is named\), r 16 for 1- and 2-byte texels and 64 for the rest, none 64 \(T79\); requiredLinearTextureBytesPerRowForDescriptor: pads by the same answer. l logs each texture over a buffer \(m2v/gpu/textures-&lt;pid&gt;.txt: format, texel bytes, size, rows, Turnip's own row, the rows' class, in place and at Metal's pitch\). Planned boots: pdbaql, pdbaqwl, pdbaqrl \(pdbaqol if all three scramble\); the clean letter with the copy time nearest T79q's becomes the default.
- T80l \(2026-11-01, pdbaql\): icons still in shuffled blocks; backboardd restarted once and ran at 120 FPS after. The texture log shows backboardd's icons \(RGBA8 58x58 and 128x128 over buffers, rows 256 and 512\) in place over Turnip's own linear image \(driver pitch, not DRM\_FORMAT\_MOD\_LINEAR\); T78 refused that class for pitch and copied it, and its 31 explicit-pitch textures drew clean. Most glyphs \(A8\) lie 64 bytes into their buffer and stay copied \(placement\). L inp 82/5, refused 1 for pitch and 51 for placement.
- T80r \(2026-11-01, pdbaqrl\): same blocks. The 16-byte answer for 1- and 2-byte texels left Core Animation's rows unchanged \(an A8 43 wide still 64\), so r and w lay icons out as none does; w and o were not booted. L inp 190/13. textures-&lt;pid&gt;.txt persists in the cache across boots: T80r's textures-253.txt is T80l's.
- T81 \(2026-11-01\): AdrenoMetal bridge patch 0022 adds metal2vulkan boot letters: k takes the DRM\_FORMAT\_MOD\_LINEAR image at Metal's pitch for every texture in place, never the driver's own linear image; n keeps a texture only read a shadow \(its copies are what T79 removed\). Planned boots: pdbaqkl \(clean icons and smooth would make k the default\), then pdbaqnl if k still scrambles.
- T81k \(2026-11-01, pdbaqkl\): still blocks in icons, text and the live wallpaper's shadow. All 1107 textures in place were the DRM\_FORMAT\_MOD\_LINEAR image \(L inp 1107/1107\), so the image kind is not the cause. Text glyphs are mostly shadows and the wallpaper is another process, so in-place textures over buffers are not the whole story either. The RM row moves with the answer: tile memory rendered 310M pixels in T78q \(16\) and 1127-1227M in T79q, T79q2 and T80r \(64\). textures-&lt;pid&gt;.txt appends across boots when a pid repeats.
- T81 revert \(2026-11-01, AdrenoMetal a903895, UniXNU a0db373\): the bridge letters o, w, r and metal2vulkan patch 0022 \(k, n\) are gone, as none changed the scrambling; the 64-byte answer, its use in requiredLinearTextureBytesPerRowForDescriptor and the l texture log stay. Next: T82s, add-on 29 with asteroids-tu-debug=sysmem \(every pass in system memory, trace letters pl for the 1000-byte command line\).
- T82s \(2026-11-01, pl + asteroids-tu-debug=sysmem\): no pass in tile memory \(RM gmem 0, 7701 passes in system memory\) and the same blocks: tile memory is not the cause.
- T82c \(2026-11-01, pql + sheng-gpu-import-skip=0, imports cleaned around every submission\): worse, with blocks also on elements that were clean, 103 GPU hangs at 99 % busy and a backboardd SIGSEGV, after which the system drew on the CPU. The cleaning itself took 32 ms \(9234 passes, 1631 MiB\), so turning the whole switch back on is no fix and no answer.
- T83 \(2026-11-01, AdrenoMetal 3814805, UniXNU 7140588\): two letters to split what is left. v sets HostPageTexturePolicy::Shadow, so every texture over host pages is copied in as in T78 while the answers stay 64: blocks with v are in the layout, none are in reading in place. x watches each sampled source over a buffer or surface \(hash at commit and at completion: RC row\) and copies an unchanged one back through the GPU on a queue of its own, comparing it with the CPU's bytes \(RB: checks, equal, different, moved, skipped, differing 64-byte lines and 4 KiB pages of those compared, all-zero; RF: the first four\). Planned boots pdbaqx, then pdbaqv.
- T83x \(2026-11-01, pdbaqx\): RC watched 247/3 raced 0/0, RB n229 eq229 ne0: every source unchanged during GPU use, and the GPU's copy of each equal to the CPU's bytes. Its readback read client memory Core Animation had unmapped and crashed backboardd \(SIGSEGV\). T83v \(pdbaqv, HostPageTexturePolicy::Shadow\): still blocks, as the user saw before backboardd faulted on a null pointer. So neither reading in place nor any cache \(CPU or GPU\) is the cause: the GPU draws the bytes it is given, copied or not.
- T85 \(2026-11-01, AdrenoMetal 6e83314, UniXNU 8446ded\): v and the readback are gone; letter y writes the CPU's bytes of the first 48 distinct small sources a frame samples \(then every 25th up to 96\) at their commit to m2v/gpu/dump-&lt;pid&gt;-&lt;n&gt;-f&lt;format&gt;-&lt;w&gt;x&lt;h&gt;-r&lt;rows&gt;-&lt;s\|b&gt;.bin; local/tools/dumps.py turns them into PNGs. Blocks in the dumps put the cause in whatever writes those bytes under the 64-byte answer.
- T85y \(2026-11-01, pdbaqy\): 106 dumps of the render server's sampled sources \(icons 58x58 and 128x128 RGBA8, A8 text such as the date, RG8 64x64 masks\) are clean in memory. With T83x \(the GPU reads them as written\) the render server's sources are not where the blocks come from. The T79 photos put the blocks in the wallpaper's blurred flower shadows, drawn by the poster in its own process, which the boot letters \(render server only\) never reached. The watch's hashing at completion still read unmapped client memory: backboardd SIGSEGV with x or y on.
- T86 \(2026-11-01, AdrenoMetal 39bb4ec, UniXNU 405641e\): the bridge answers 64 for linear alignment in backboardd only, the runtime's 16 in every other process. package/AsteroidsMetalPlugin.mm: boot letter z skips shader priming. Every new runtime or Turnip build primes all libraries again \(T81k: 34 of 155, 927 pipelines\) from 90 s after the device opens, during animations; a backboardd restarted after a crash ran at 120 Hz \(user, T80l and T85y\). Planned boots pdbaq \(blocks?\) and pdbaqz \(smooth from the start?\).
- T86d \(2026-11-01, pdbaq\): blocks still in the wallpaper's flower shadows, no backboardd crash, L inp 62/5. The first boot was refused \(Load Error\) for every image: slot a was unbootable with its retry count spent, as nothing marks our boots successful; fastboot set\_active a reset it \(retry count 7\).
- T80o \(2026-11-01, pdbaqol, add-on 28: the runtime's 16 in every process\): no blocks. So the blocks are drawn live by the render server's 64-byte answer, not saved in a wallpaper render, and not drawn by another process. MobileSlideShow's sig 6 abort happens here too, so it is not the answer's.
- T87 \(2026-11-01, AdrenoMetal 541a19a, UniXNU 3fc28a6\): letters put one answer back to the runtime's in the render server: A the format-free alignments, B minimumLinearTextureAlignmentForPixelFormat:, C requiredLinearTextureBytesPerRowForDescriptor:; with l each distinct question and answer goes to m2v/gpu/answers-&lt;pid&gt;.txt. Planned boots pdbaqlA, pdbaqlB, pdbaqlC.
- T87a \(2026-11-02, pdbaqlA\): no blocks, not 120 Hz and far better than 15 fps \(user\). answers-&lt;pid&gt;.txt: the render server asks only deviceLinearTextureAlignmentBytes, linearTextureAlignmentBytes and deviceLinearReadOnlyTextureAlignmentBytes, once each; never minimumLinearTextureAlignmentForPixelFormat: or requiredLinearTextureBytesPerRowForDescriptor:. So A is T80o again: L inp 538/19, refused for pitch 246, 29509 copies. The blocks and the copies T79 removed come from the same answer. T87az \(A plus z, no shader priming\) booted for the post-crash 120 Hz question.
- T88 \(2026-11-02, AdrenoMetal eedebfa, UniXNU d0443d7\): the bridge answers the runtime's 16 again. UniXNU patches/mesa/turnip-narrow-linear-rows.patch: the A8xx texture descriptor states a linear row pitch in bits \(TEX\_LINE\_OFFSET\), and only render targets and the 2D engine \(A2D pitch shr 6\) step rows at 64 bytes, so an explicit DRM\_FORMAT\_MOD\_LINEAR image that is never an attachment or storage image takes rows at any multiple of 16 bytes and of its texel \(descriptor alignment field clamped to 0\); transfers touching one are skipped. Core Animation's sampled textures then bind in place at 16-byte rows without the copies. Planned boot pdbaql: no blocks, smooth, and pitch refusals near 0.
- T87az \(2026-11-02, pdbaqlAz\): priming off \(PR libs 0/0\), maybe slightly smoother than T87a \(user: possibly placebo\), L inp 224/8, 127 pitch refusals, 20738 copies: priming is not the main cost.
- GPU work shelved \(2026-11-02, AdrenoMetal 7e19eb9, UniXNU eb5bf59\): the user calls T87a's state good enough. Default: the runtime's 16-byte linear answer \(no blocks, faster than T78 but not T79's 120 Hz\). Not built or booted: T88 \(turnip-narrow-linear-rows.patch, UniXNU d0443d7\) and its CI run were dropped untested. Removed: letters A, B, C, the y source dump \(its watch read unmapped client memory and crashed backboardd\) and z \(no priming, no clear gain\). Open: what in the render server the 64-byte answer draws as blocks \(its sampled sources are clean in memory and on the GPU\); why a backboardd restarted after a crash runs at 120 Hz; MobileSlideShow sig 6 in every run since T79, T80o included.
- Upstream sync \(2026-11-03, branches sync/upstream-2026-11-03; UniXNU main f61fd6c merged as dc88d19 + 969df26\): AdrenoMetal is upstream's \(UniXNU/AdrenoMetal 243d63c\) instead of the rootstock fork, whose T78-T88 experiments stay on its asteroids branch; upstream answers the runtime's 16-byte linear alignment as the shelved default did. The Mesa list is upstream's \(GMEM mutable and memory-side swap, transient attachments in GMEM, frame diagnostics, queue priorities, thread render mode\) plus turnip-a810-sysmem-ccu; turnip-render-mode-measured \(GMEM red/blue swap on the A810, T70-T74, now fixed upstream\) and the asteroids measurement patches \(stats, timing, submit trace: TU\_DW\_TRACE, gpu-trace.py\) are dropped. All patches apply in order at the Mesa pin. The kernel GPU driver stays the NativeAdreno gen8 fork \(upstream Adreno740 has no A8xx\). package/AsteroidsMetalPlugin.mm drops CacheImport.h and the shader-cache fallback \(pipelines are compiled on the device only upstream\) and keeps the pipeline-pack import.
- Upstream's Turnip patches \(2026-11-03 sync\) call NativeAdrenoMethodSetPriority \(17\) and NativeAdrenoMethodNote \(18\); NativeAdreno 38227e7 declares them and their records in NativeAdrenoABI.h so Turnip compiles. The asteroids kernel implements neither and answers kIOReturnUnsupported, which Turnip takes as not accepted \(queue priorities stay normal, frame notes are dropped\). UniXNU acf69e3 gives turnip-frame-diagnostics.patch its missing new-file header, so git apply takes the whole recorded list \(gpu-addon run 41598242089 failed on both\).
- sync1 \(2026-11-03; kernel run 41596757530, add-on run 41600013844\) broke the screen. backboardd crashed at 56 s with SIGSEGV at 0; its crash report from the Data volume, symbolized with the add-on's unstripped binaries: Turnip's tu\_emit\_subpass\_begin&lt;chip 8&gt; wrote through a null command stream after tu\_cs\_reserve\_space could not add a BO, under the bridge's RenderLowering::draw\_indexed. The kernel refused no BO \(\[bo memory\] refused 0\). The GPU then never finished fence 88 \(hangs 1, 5, 10 from 58 s, no restart\) and the kernel refused backboardd's reopen \(PUB no device: VkResultCode\(-3\)\), so the hangs followed the crash. 4 s before it the bridge rendered a memoryless BGRA8 1080x2392 texture through a 10 MB scratch image \(its pass splits into 2 instances\). The unified log stops 35 s before the crash. mixA \(the sync kernel with the pre-sync add-on: device 9be0e5b, AdrenoMetal 7e19eb9\) booted clean: no crash, 197 GMEM passes, fences to 1172, mic peaks 817 and 476. The fault is in the sync add-on \(upstream AdrenoMetal and the new Turnip list\).
- T98: UniXNU 89438f4 adds turnip-darwin-first-alloc-failure.patch: the first failed Turnip BO allocation or map of a process goes to the kernel's report line as AF &lt;step&gt; s&lt;KiB&gt; f&lt;flags&gt; k&lt;status&gt; u&lt;MiB in use&gt; h&lt;largest hole MiB&gt; c&lt;cached MiB&gt; &lt;process&gt; \(steps r retired BOs, v GPU range, a BoAlloc, m BoMap, p BoCpuMap, i CPU mapping, H host import range\).
- T98 \(2026-11-04; the sync kernel with add-on run 41624545358, UniXNU 89438f4\): 76 s with no crash, no GPU hang and fences to 1422, but also no AF line and no memoryless full-screen pass, so the allocation failure did not recur and was not measured. The RM gmem row reads 0 in every boot of the synced add-on \(T98 too\): its counters came from turnip-asteroids-stats.patch, which the sync dropped, so sync1's 0 GMEM passes was a missing counter, not a measurement.
- T98 unlocked and looked right \(owner, 2026-11-04\); sync1 broke on its first unlock. sync1 ran with a cold shader cache \(V cache hit 0, miss 64; the first boot of upstream's shared shader cache\) and T98 with a warm one \(hit 60, miss 92\), so the failure may need a cold cache; not measured. T98 is the synced image kept; its first allocation failure line stays in as the check for a recurrence.
- package/AsteroidsMetalPlugin.mm \(2026-11-04\): the arm64e EDR headroom write takes its QuartzCore address from kQuartzCoreSites, keyed by the running dyld shared cache's UUID \(iPad17,x 24A446 and iPhone17,4 24A446, read by name from each cache\), and writes nothing by address on another cache \(marker 0x6EF0\). The iPhone cache's QuartzCore data is 0x4000 above the iPad's; details in the configuration area.

### 完成条件

- Core Animation renders through Metal on the GPU with measured frame times.

### 当前范围

- T40e: Turnip picks GMEM or system memory per pass \(TU\_DEBUG=nocb, as AdrenoMetal 461a842\); not yet booted on the 3a. Sm8550Platform is linked as Adreno740's dependency and not used.

### 下一步

- If the synced add-on breaks again, read the AF report line in the kernel log \(T98's allocation failure check\).

### 证据

- `device`: [GPU compositing and the GPU panel copy run stable.](https://github.com/rootstockos/UniXNU-asteroids/blob/6370e66cc460202756058ae53f73afdb69abd364/package/GpuPowerProbe.cpp)
  Command: <code>fastboot boot local/unixnu-asteroids-t34b-boot.img</code>. Revision: `e022e84a9721ea6408ea12665b5a23e9b89fc5f6`.

## clock {#clock}

`device-verified`

组件: `QcomPmicRtc`.

### 硬件与依赖

- The PMK8550's RTC: a read-only seconds counter behind the SPMI arbiter \(v7.1, APID 94\), described in the SoC's sm7635.dtsi.
- The Data volume for the offset file, as Android's time\_daemon keeps it under /data/vendor/time.

### 配置

- QcomPmicRtc \(UniXNU fork\) publishes IORTC with IORTCReadOnly; drivers/ArmDTPlatform \(rootstockos/ArmDTPlatform asteroids\) forwards the calendar to it as counter + offset; the kernel restores /private/var/db/unixnu-rtc-offset before launchd and stores it on every calendar set.

### 操作步骤

- Boot, set the time in Settings &gt; Date &amp; Time, restart, and compare the clock; the banner's RTC row shows the counter, restores and stores.

### 开发经验

- T39: the counter reads \(plat 3, pmic 5\); no set reached the kernel while timed hung.
- T39d/T39e: timed hung in gethostuuid\(\) without a platform UUID; with the platform seed in the ADT it answers, and a time set in Settings survives a restart.

### 完成条件

- The wall clock is right after every boot without a network.

### 当前范围

- No automatic time \(no network or GNSS time source yet\).

### 下一步

- Propose the IORTC forwarding and the RTC drivers upstream once stable.

### 证据

- `device`: [T39e: the time set in Settings survived a restart; Settings &gt; Date &amp; Time opens.](https://github.com/rootstockos/UniXNU-asteroids/blob/6370e66cc460202756058ae53f73afdb69abd364/board.toml)
  Command: <code>fastboot boot local/unixnu-asteroids-t39e-boot.img</code>. Revision: `e4d1092cc3d051617ee88858b153ed2ba0d456fd`.

## 网络 {#network}

`planned`

### 硬件与依赖

- The 3a's Wi-Fi and Bluetooth module; not yet identified for a driver.

### 配置

- None yet.

### 操作步骤

- Identify the module and its bus from the live device tree.

### 开发经验

- No network driver runs; bluetoothd is disabled.

### 完成条件

- The device joins a network and passes traffic.

### 当前范围

- No network.

### 下一步

- Identify the Wi-Fi module.

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`implemented`

### 硬件与依赖

- The audio DSP and its firmware; sheng's ADSP, GLINK, QRTR, GPR and AudioReach stack is the reference.
- The 3a's amplifier settings container \(vendor/firmware/tfa98xx.cnt, proprietary-files.txt\), turned into build/asteroids-tfa/AsteroidsTfaConfig.h by scripts/prepare-asteroids-tfa.py.

### 配置

- sheng-audio takes bits \(sheng-adsp=2 is required, the default\): any nonzero value serves the audio service, 2 plays a 1.5 s 750 Hz test tone at boot, 8 runs the lock sound test.
- sheng-audio-pa moves the DSP period buffer \(default 0xe6200000, the splash region's tail\); sheng-audio-tone-ms and sheng-audio-atten set the tone.
- asteroids-audio-i2s = interface \| data lines &lt;&lt; 8 \| bits &lt;&lt; 16 \(default primary MI2S, SD1, 32-bit: the amplifiers take their data on gpio17\); asteroids-audio-prm bits \(default 3\): 1 LPASS core vote, 2 MI2S bit clock request.
- asteroids-mic=&lt;stage&gt; \(default 8 since T96n, with sheng-audio; 0 leaves the microphone off\) brings up the WCD9378 microphone path in stages: 1 rails \(ldob7, ldob8\) and codec reset \(gpio162\), 2 PRM votes and VA/TX core clocks, 3 LPI SoundWire pins and VA/TX macro clocks, 4 VA SoundWire master \(0x33b0000, v1.7\) and enumeration, 5 codec init \(SCP setup, io\_init, SDCA class load\), 6 capture path \(ports, micbias 1, SmartMIC0 sequencer, TX decimator 1 by asteroids-mic-dec\), 7 DSP capture graphs and a 2 s capture test, 8 capture for the plug-in. asteroids-mic-port = sample interval \| offset1 &lt;&lt; 8 \| lane &lt;&lt; 16 \(default 1 \| 1 &lt;&lt; 8\). asteroids-mic-mux=1 switches the VA macro to its own core clock \(0x3420000 = 1\) as the vendor clock manager does \(default off\). asteroids-mic-usage sets the SmartMIC0 ADC usage \(default 3 NORMAL; 5 ADC\_LP wants interval 3\), asteroids-mic-pageswap=0 the MIPI page order, asteroids-mic-frame=0 skips the bank switch.
- The GPU addon carries sheng's audio server plug-in as audio/ShengAudio.driver \(scripts/build-asteroids-metal-plugin.py builds it with scripts/build-sheng-audio-hal.py unless --no-audio, and adds its CDHash to the owner trust module\); patches/xnu/zzyd-board-audio-addon-mount.patch mounts audio/ over /System/Library/Audio/Plug-Ins/HAL.

### 操作步骤

- Read the \[audio\] and \[amps\] rows: stage, DSP status, amplifiers found \(amps=3: both\), clocks stable \(lock=\), errors, SMMU result, I2C engine, PRM results \(bus= second word\), I2C failures.
- Run scripts/check-audioreach-host.py after changing the graph commands.

### 开发经验

- T38 ports sheng's audio DSP bring-up \(AdspProbe.cpp, sheng-adsp=1 survey, 2 start\) with the 3a's IPCC \(0x405000\), carveouts \(0x99300000, 0x99280000\) and crash-reason partition; the firmware comes from modem\_a \(LUN 4\) through NativeUfs's native\_ufs\_part\_find/read \(rootstockos/NativeUfs efa8271, from UniXNU's ShengUfs\).
- T41: speakers are two NXP TFA9873 \(P 0x34 slot 0, S 0x35 slot 1\) on QUPv3 wrapper 1 SE6 \(SE13, 0x898000, gpio59/60\), reset gpio141/142 \(active high\), fed by primary MI2S \(gpio15-18, function 2\) as two 32-bit slots at 48 kHz. The container carries no amplifier firmware \(a dummy patch\), only bitfield settings.
- T41: the microphone is AMIC1 of a WCD9378 \(mixer\_paths handset-mic: ADC1, MIC BIAS1 by the card routing, ADC\_LP, volume 6\) on the VA macro's SoundWire master; the handset mic back end is CODEC\_DMA-LPAIF\_RXTX-TX-3 as on sheng. The codec register recipe is the July 2026 LKML WCD9378 TX driver \(v2, paged SDCA registers, built-in power sequencers\); the master is v1.7 \(apps command FIFO at 0x31c\).
- T41: package/AsteroidsAudioProbe.cpp is sheng's AudioProbe.cpp with the 3a's board steps and the TFA9873 programs \(AsteroidsTfa9873.c\) in place of the CS35L43's; the speaker device runs 32-bit while the stream stays 16-bit \(the playback converter widens it\). The amplifiers power up after the graphs start, since they wait for the bit clock. No microphone path.
- T40k \(2026-10-27\): the speaker path ran end to end \(DSP graphs, the service, the plug-in, a 48 kHz stream without gaps; both TFA9873 rev B found, clocks and PLL locked\) but was silent: on I2S0 SD0 the amplifiers got the clocks and no data. T40k-spk-sd1 \(asteroids-audio-i2s=0x200200\) played the boot tone and iOS sound through both speakers: the amplifiers take their data on SD1 \(gpio17\), the default since T41.
- T41: TFA9873 STATUS0 bits 1, 2 and 4 \(DCOCPOK, OTDS, UVDS\) are ok flags in NXP's field list, not alarms; \[audio\] err= counts real alarms only \(OCDS, MANALARM, NOCLK, TDMERR or a missing ok flag\).
- T41, T41-mux: mic stage 4 fails. The rails are voted, the PRM grants the macro and codec votes and the VA/TX core clocks, the LPI pins and macro clocks are set \(VA SWR\_CONTROL 1\) and the master \(v1.7\) keeps its settings, but COMP\_STATUS never shows the link up, no interrupt fires and no device attaches. With asteroids-mic-mux=1 \(the VA clock source switch\) the master's registers read back 0, so the switch stays off. T42 adds \[mic extra\]: the codec reset pin read back, COMP\_STATUS over time and, with asteroids-mic-pmic=1, the codec's LDOs from the PMIC.
- T42 \(2026-10-28\): the codec reset pin read back GPIO\_IN\_OUT 2 \(output high, pad low\): gpio162 is a TLMM eGPIO \(132-166, recovery's pinmux egpio group\) and the probe left EGPIO\_ENABLE \(bit 12\) clear, so the pad was not the TLMM's and the WCD9378 stayed in reset \(link 0x40002 throughout, no slave\). T43 sets the bit. The amplifier resets \(gpio141/142\) have the same flaw but are active high, so a pad left low releases them. Recovery's device tree: the codec rails are RPMh ldob7 \(rxtx, io; already on for the eUSB2 repeater\) and ldob8 \(buck, on demand\), micbias bobb1; SID 1 0x146 has no APID and 0x147 is not an LDO, so the T42 PMIC read can show nothing.
- T43: with EGPIO\_ENABLE the codec reset reads back 3 \(pad high\), yet the VA master's link stays 0x40002 from 1 ms to the end and no slave attaches: the master itself does not run the bus. Next: its clock \(the VA macro's SoundWire clock and the 19.2 MHz VA core clock through the PRM\).
- T46 \(2026-10-28\): the mic rows are the same in T42, T43, T46 and T46-copy: rails voted, PRM grants all four requests, LPI pins function 1, VA SWR\_CONTROL 1, reset now high, yet COMP\_STATUS 0x40002 from 1 ms to the end \(bit 0, the frame generator, never set\), interrupt status 0, no slave. Against mainline's qcom\_swrm\_init \(drivers/soundwire/qcom.c\) the probe missed the v1.7 step: SWRM\_LINK\_MANAGER\_EE \(0x018\) = 1 for the CPU, then MCP\_BUS\_CTRL = CLK\_START &lt;&lt; EE\_CPU \(4\); it wrote 2, EE 0's clock start. T47 follows mainline's order and values. Recovery's DT has no swrm-hctl or EE property for this master.
- T47-mic7 \(2026-10-28\): every mic stage ran \(st=70\): bus up \(COMP\_STATUS 0x100001\), the WCD9378 TX device enumerated as device 1 \(id 0x01170223, the DT's wcd9378-tx-slave\), the codec set up, the SmartMIC0 sequencer at PS0, TX decimator 0, the DSP's capture graphs; 200 of 200 periods came back. The level was near silence: peak 34 of 32767, mean under 1, 18559 non-zero samples. The vendor's handset-mic path records AMIC1 \(ADC1, SWR\_MIC0\) and AMIC3 \(ADC2, SWR\_MIC4\) at ADC volume 6; the probe takes AMIC1 only. T49: asteroids-mic-capture-s=&lt;s&gt; \(up to 30\) and a \[mic peaks\] row with the peak of each second.
- T50: sheng-audio=1 \(speakers for iOS, no boot test tone\) is a board default.
- T51: the 20-second capture came back complete \(2000 of 2000 periods\) but silent: peak 33 in the first second, exactly 0 in the next 19. The mic path delivers no codec data.
- T76 \(2026-10-30\): the board classes here register through OSKextRegisterBoardClasses \(zzyg-board-class-registration.patch\), under the kext lock, in place of preModLoad/postModLoad alone, which deadlocked T75f's boot \(storage area\).
- T76's second kernel build \(run 41111730079\) failed in ShengPlatformPower.cpp: BoardClasses.h had been included after the file's last \#include, which there sits inside the ShengPlatformPower class; every probe now includes it after its first \#include.
- T89 \(2026-11-02\): T51's capture was digital zero after its first second, the decimator fed nothing. The probe took AMIC1 through TX SMIC MUX0 into DEC0 \(DMA channel mask 1\); the vendor's handset-mic path \(mixer\_paths\_volcano\_qrd.xml amic\_1\_3\) takes AMIC1 through TX SMIC MUX1 = SWR\_MIC0 into DEC1 and AMIC3 through SMIC MUX2 = SWR\_MIC4 into DEC2, both on TX\_AIF1\_CAP, and its default sets TX SMIC MUX0 to ZERO; the vendor TX macro passes the decimator mask as the codec DMA channel mask \(tx\_macro\_get\_channel\_map\). The VA macro's SoundWire mic clock setup for a VA-hosted master \(bolero 2.1: VA\_TOP\_CSR\_SWR\_MIC\_CTL0-2 = 0xCC\) is already in the probe. asteroids-mic-dec=&lt;n&gt; \(default 1\) picks the decimator \(mux 0x100 + 8n, path 0x400 + 0x80n\) and the capture asks for mask 1 &lt;&lt; n; \[mic port\] reads back the decimator's muxes and path, the codec's data port 1 \(PortCtrl, ChannelEn in both banks, IntStat, PrepareStatus\) and SCP\_FrameCtrl in both banks, and the master's port 1 control, 300 ms into the capture. Boot: asteroids-mic=7 asteroids-mic-capture-s=20.
- T89mic \(2026-11-02, asteroids-mic=7 asteroids-mic-capture-s=20, kernel run 41445466871\): still digital zero after the first second \(peaks 32 then 0 for 19 s, from 22.7 s; the user made noise and silence in turns\). \[mic port\]: dec 1 with mask 0x2, TX muxes SWR\_MIC0 / SWR\_MIC and the path enabled and unmuted \(0x24\), the codec's port 1 channel 1 enabled in both banks, the master's port 1 likewise \(0x1000101\), but the codec's SCP\_FrameCtrl 0 in both banks: it frames at the default 48 rows by 2 columns while the master frames at 50 by 16 \(0x101c 0xf\). Commands ride in column 0 and work; the data port does not line up.
- T90 \(2026-11-02\): after the port setup the probe writes the master's bank 1 frame \(0x105c\) like bank 0 and broadcasts SCP\_FrameCtrl\_B1 = the same shape \(device 15\), mainline's sdw\_bank\_switch with qcom\_swrm\_pre\_bank\_switch, so the codec and the master switch to bank 1 at 50 rows by 16 columns together. asteroids-mic-frame=0 skips it. \[mic port\] then reads SCP\_FrameCtrl bank 1 as 0xf.
- T90mic \(2026-11-02, capture 30 s from 43.1 s\): unchanged: peaks 33 then 0, the codec's SCP\_FrameCtrl still 0 in both banks and the master's MCP\_STATUS \(0x104c\) 0, bank 0. The broadcast never landed: mainline \(qcom\_swrm\_cmd\_fifo\_wr\_cmd\) sends a broadcast with command id 0xf \(SWR\_BROADCAST\_CMD\_ID\), and the probe's swrWrite gave it an ordinary id. The first T90mic boot ended in fastboot, not recovery, and was not pulled.
- T91 \(2026-11-02\): swrWrite uses id 0xf for device 15 and waits 10 ms after the bank switch; \[mic port\] \[6\] is the master's MCP\_STATUS \(bit 0 the bank in use\) in place of its port control 2.
- T92 \(2026-11-02, static review against the vendor master refs/nulldebris-modules swr-mstr-ctrl.c, the Volcano audio DT and sheng's working WCD938x capture\): the probe never prepared the codec's port: sheng writes DP1\_PrepareCtrl \(0x105\) before ChannelEn, and T90's DP1\_PrepareStatus read 0. T92 writes 0x105 = 1 and polls PrepareStatus for up to 10 ms before enabling the channel. Same as sheng and kept: codec HCtrl 0xff, master HCTRL 0xf0, sample interval 1. Sheng frames at 50 by 16 without a bank switch and records, so the T90/T91 bank switch is kept but may not be needed \(asteroids-mic-frame=0\). The vendor master computes a TX port's interval as 2 x bus clock / channel rate - 1 with offset1 and lane from the codec driver's table \(not in the local trees\); the Volcano VA master maps ADC1 to port 1 channel 1 \(SWRM\_TX1\_CH1\) and sets mipi-sdw-block-packing-mode 1. T91's kernel build was cancelled for T92.
- T92mic \(2026-11-02\): still digital zero \(peaks 32 then 0, from 34.1 s\). The master is now on bank 1 \(MCP\_STATUS 1\), so the 0xf broadcast lands at the master; the codec's SCP\_FrameCtrl and DP1\_PrepareStatus still read 0.
- Static review \(2026-11-02\), LKML WCD9378 v2 \(lkml.iu.edu/2607.3/09185.html, tested on the Fairphone 6, SM7635\): ADC1 leaves on codec port 1 channel BIT\(0\) to master port 1 channel BIT\(0\) \(no ChMap register, software only\); the TX ports are SDW\_DPN\_SIMPLE with simple\_ch\_prep\_sm, so no prepare is needed and PrepareStatus 0 is expected \(T92's 0x105 write is harmless\); bps 1; lane\_control\_support; clock\_reg\_supported \(the core programs SCP bus-clock base/scale; without it capture is dead, per the cover letter\): the probe already writes 0x4d = 1 \(19.2 MHz\) and 0x62/0x72 = 2 \(/2\), matching a 9.6 MHz bus \(master clock divider 0 on the 9.6 MHz macro clock\). The driver writes no raw 0xe0/0xf0; the probe's 0x01 there came with the first bring-up \(b0a33bf\) without a source. Mainline sm8550 TX SoundWire \(sm8550.dtsi swr2\): the ADC ports run sample interval 1, offset1 0, on lanes 1 and 2; only the DMIC ports \(interval 3, offset1 1\) use lane 0, which also carries the command column; sheng records on lane 2. The probe ran ADC1 at interval 1 on lane 0 with offset1 1. T92l1 / T92l2: the T92 kernel with asteroids-mic-port=0x10001 / 0x20001 \(interval 1, offset 0, lane 1 / 2\).
- T92l1 \(2026-11-02, asteroids-mic-port=0x10001\): still digital zero \(peaks 32 then 0 from 33.2 s; the run lasted 605 s and ended in fastboot\). The master's port 1 took interval 1 at offset 0 \(0x1000001\). A 150 Hz high-pass decimator turns a constant bit stream into exactly 0 after a short transient \(the first second's peak of 32 in every run\), so the decimator runs and its SWR\_MIC input is constant.
- Static review, second pass \(2026-11-02\): the lpass-cdc TX and VA macros \(refs/nulldebris-modules lpass-cdc-tx-macro.c, -va-macro.c\) need nothing the probe lacks for a SWR\_MIC decimator on a VA-hosted master: the VA SWR\_MIC\_CTL0-2 = 0xcc \(done\), TX\_TOP\_CSR\_SWR\_CTRL only cleared at power-down, the amic TX hold clear is the codec's ANA\_TX\_CH2 HPF init bit \(done\). The LKML driver's codec writes match: io\_init \(TXFE\_DIV bypass, TX support clock, PDM watchdog, SM0-2 micbias selects\), SmartMIC0 usage 0x05 \(ADC\_LP\), IT11\_MICB 0x05 \(WCD9378\_MICB\_USAGE\_2P75V for the board's 2750 mV micbias 1\), PS0 request. Left: the lane \(T92l2 next\), offset, the probe's unsourced 0xe0/0xf0 write, and the T90 bank switch.
- T92l2 \(2026-11-02, asteroids-mic-port=0x20001, lane 2 as sheng\): still digital zero \(peaks 32 then 0 from 33.2 s; again via fastboot, then recovery on its own\). Third review pass, lpass-cdc TX decimator power-up: CFG0 bit 7 clear for an analog SWR mic \(0x50 here\), DEC mode ADC\_DEFAULT \(no mixer path sets TX DEC MODE\), 150 Hz high-pass so no gate sequence, clock enable 0x20 and rate 4 \(48 kHz\) in PATH\_CTL, TX SWR\_INPUT is a plain input pin, and the TX macro never touches its SWR\_CONTROL \(only the VA macro does\). The macro side matches the vendor driver throughout; the constant input is on the codec or bus side.
- Stock modules \(2026-11-02\): recovery's kernel loads only gpr and spf\_core \(no sound card\), so vendor\_dlkm\_a was read out of super read-only \(dd of sectors 18504096 + 162696 from the LP metadata; local/stock/vendor\_dlkm\_a.img, ext4\) for the stock wcd9378\_dlkm.ko, swr\_ctrl\_dlkm.ko, lpass\_cdc\_\*\_dlkm.ko and machine\_dlkm.ko \(no source\). The Volcano codec node \(volcano-audio-overlay.dtsi wcd9378-codec\) maps ADC1 to codec port index 0, mask 0x1, SWRM\_TX1\_CH1, and qcom,swr-tx-port-params gives &lt;offset1 lane&gt; for four use cases of four ports: use case 0 \(9.6 MHz bus\) port 1 = OFFSET1\_VAL1 LANE0, the probe's original values; use case 1 \(4.8 MHz\) port 1 = VAL0 LANE1.
- Sample interval: the vendor master takes 2 x bus clock / channel rate - 1, and Qualcomm's WCD937x-family drivers give an ADC port 4.8 MHz in ADC\_LP and 9.6 MHz in NORMAL/HIFI; the LKML WCD9378 driver uses NORMAL on a 9.6 MHz bus with mainline's interval 1. The probe ran ADC\_LP \(SmartMIC usage 0x05, as the vendor's TX0 MODE ADC\_LP\) with interval 1, the NORMAL timing. T92s3: the T92 kernel with asteroids-mic-port=0x103 \(interval 3, offset 1, lane 0\): LP with LP timing on use case 0.
- T92s3 \(2026-11-02, asteroids-mic-port=0x103\): still digital zero \(peaks 32 then 0 from 33.9 s\); the master took interval 3 \(0x1000103\). Every port timing tried \(interval 1 and 3, offsets 0 and 1, lanes 0-2\) gives the same constant input, so the codec most likely sends nothing.
- T93 \(2026-11-02\): \[mic codec\] reads the codec's state 300 ms into the capture: TX sequencer 0 status \(SEQ\_TX0\_STAT\), SmartMIC0 FUNC\_STAT, PDE11 actual and requested power state, IT11 usage and micbias, SYS\_USAGE\_CTRL, TX\_NEW\_CH12\_MUX, ANA\_TX\_CH1/CH2, CDC\_ANA\_TX\_CLK\_CTL, CDC\_AMIC\_CTL, TXFE\_DIV\_CTL, PDM\_WD\_CTL0, SM0\_MB\_SEL and MB\_PULLUP\_EN. asteroids-mic-usage=&lt;n&gt; \(default 0x05 ADC\_LP\) sets the SmartMIC0 usage, so NORMAL \(0x03\) can run with interval 1. The probe's 0xe0/0xf0 write stays: per the user it came from the Nothing kernel or measurements in recovery. Boots: T93lp \(usage 5, port 0x103\) and T93n \(usage 3, port 0x101\).
- T93n \(2026-11-02, NORMAL usage 3, interval 1, offset 1, lane 0\): still digital zero \(peaks 31 then 0 from 32.6 s\), and no \[mic codec\] row: it printed only when its first two words were nonzero, and a failed read gives 0xff, so every paged codec read returned 0, the usage register written 3 a moment before among them. The probe's PS0 check \(ACT\_PS 0\) since T47 therefore proves nothing.
- T94 \(2026-11-02\): wcdPage writes SCP\_AddrPage1/2 before every paged access instead of caching them \(asteroids-mic-pagecache=1 restores the cache\): if the codec drops its page registers, every later paged access, writes included \(micbias, usage, PS0 request\), lands on page 0, which would leave the ADC off. \[mic codec\] now prints whenever \[mic port\] does.
- T94n \(2026-11-02\): still digital zero \(peaks 30 then 0 from 33.3 s\), and \[mic codec\] read 0 in every byte with the page registers written before each access. The \[mic\] row's /10 is the device id's high word \(DT reg &lt;0x10 0x01170223&gt;\), not a paged read, and efuse=0 is a paged read: no paged codec read has returned data since T47, so the codec's paged writes \(io\_init, class load, micbias, usage, PS0 request\) may never have landed either, which would leave its ADC off. The Qualcomm paging patch the LKML WCD9378 series depends on \(soundwire: qcom: add SCP address paging support, 999f80904763, lkml.iu.edu/2607.1/13485.html\) programs SCP\_AddrPage1/2 and sets bit 15 of the wire address, as the probe does.
- T95 \(2026-11-02\): \[mic page\]: SCP\_AddrPage1/2 read back after setting them for ANA\_TX\_CH1 \(beside the values written\), the raw read FIFO word of that paged read, the master's interrupt status \(0x200\) before and after it, DEV\_VER \(0x40100070\) through paging, ANA\_TX\_CH1, the unpaged SCP\_DevId\_0 and the failed reads.
- T95's first kernel build \(run 41485458782\) failed: the \[mic page\] block declared failed a second time in micPortSnapshot; it counts in pageFailed now.
- T95n \(2026-11-03\): \[mic page\] back/wrote 80308030: SCP 0x48/0x49 read back 0x30/0x80, exactly as written for ANA\_TX\_CH1 \(0x4018000e\); the paged read's FIFO word 0xa00 \(data 0, its own id\), interrupt status 0x6 before and after \(no command error\), DEV\_VER and the ADC gain 0 through paging while the unpaged SCP\_DevId reads 0x23. The paged space answers but holds nothing: the address is wrong, not the bus.
- T96 \(2026-11-03\): the page register order. Qualcomm's regmap-swr \(refs/nulldebris-modules soc/regmap-swr.c, the stock driver's path\) writes address bits 30:23 \(mask 0x7f800000\) to SCP 0x48 and bits 22:15 \(0x007f8000\) to 0x49, with the low 16 bits \| 0x8000 on the wire; the probe used the MIPI header's order \(0x48 bits 22:15, 0x49 bits 30:23\) since T47, so every paged access went to an empty address \(0x0018000e for 0x4018000e\): no codec read returned data and none of its writes \(io\_init, class load, micbias, usage, PS0 request\) landed, so the ADC never ran, whatever the port timing. The stock wcd9378\_dlkm.ko uses the same 0x4018xxxx/0x41xxxxxx space \(1461 words of 0x4018xxxx\). wcdPage now uses Qualcomm's order; asteroids-mic-pageswap=0 restores the old one. Boots: T96n \(NORMAL usage 3, interval 1\) and T96lp \(LP, interval 3\).
- T96n \(2026-11-03, NORMAL usage 3, interval 1, offset 1, lane 0, decimator 1\): the microphone records. 3000 of 3000 periods, peak 991 of 32767 \(about -30 dBFS\), mean 29, 1398442 non-zero samples; per-second peaks from 33.2 s: 448 294 35 28 36 97 319 279 140 348 321 178 113 779 560 296 573 708 128 991 744 772 325 362 329 394 315 317 381 595, rising and falling with the user's noise and silence. The codec now answers: \[mic codec\] usage 3, micbias 0x05, ANA\_TX\_CH1 0x26 \(gain 6\), TX sequencer status 2; \[mic\] efuse 0x110 \(0 before\); \[mic page\] wrote 0x80/0x30 and reads back the gain 0x26 through paging. The page register order was the fault from T47 on.
- T97 \(2026-11-03\): the microphone is on by default: asteroids-mic defaults to 8 \(capture serves the plug-in's input stream, after the 2 s boot capture test\) and the SmartMIC0 usage to 3 \(NORMAL, with the port's default interval 1, offset 1, lane 0 and decimator 1\), the T96n combination.

### 完成条件

- Playback and capture through the audio server.

### 当前范围

- The microphone records at about -30 dBFS peak with the vendor's ADC gain 6; iOS input through the plug-in \(stage 8\) is untested since T96n \(no app on the phone to record with\).

### 下一步

- Check recording in iOS once an app can record, then raise the ADC gain.

### 证据

- `host`: [PASS: 207 AudioReach packet checks, including the 3a's primary MI2S port and the 32-bit speaker device format.](https://github.com/rootstockos/UniXNU-asteroids/blob/6370e66cc460202756058ae53f73afdb69abd364/scripts/check-audioreach-host.py)
  Command: <code>python3 scripts/check-audioreach-host.py</code>. Revision: `b1621b32a2513ba8e2c4c599d4f4baf602a7369a`.
- `device`: [T40k-spk-sd1: the boot tone and iOS sounds played through both speakers; \[amps\] showed the boost converters active and \[audio-io\] 8.3 M frames without gaps in 494 s.](https://github.com/rootstockos/UniXNU-asteroids/commit/b1621b32a2513ba8e2c4c599d4f4baf602a7369a)
  Command: <code>fastboot boot with boot args sheng-audio=3 asteroids-audio-i2s=0x200200 sheng-audio-tone-ms=4000</code>. Revision: `49ec1ccb18fd6b7ddd23b25b2c4ae96cd084ad1a`.

## 电源 {#power}

`implemented`

组件: `AppleKeyStoreState`.

### 硬件与依赖

- sheng's placeholder ApplePMGR provider; the AppleKeyStore stand-in.

### 配置

- sheng-pmgr=2 \(required in board.toml by the payload check\); sheng-aks=1 publishes the AppleKeyStore stand-in with persistent Data.

### 操作步骤

- Boot and check that SpringBoard finishes booting \(AppleKeyStore opens\).

### 开发经验

- Without the AppleKeyStore stand-in on persistent Data, SpringBoard never finished booting \(T20-T28\).
- T38: sheng's battery manager client and iOS power source \(ShengBattmgr.c, ShengBattery.cpp, sheng-battery\) with the 3a's standard property numbering \(temperature 12, charge counter 14, cycles 15, design 16, full 17\); sheng's board fields \(opcode 0x50, OEM\_GET\_LOG\_BUFFER on the 3a\) and charge current are skipped.
- T76 \(2026-10-30\): the board classes here register through OSKextRegisterBoardClasses \(zzyg-board-class-registration.patch\), under the kext lock, in place of preModLoad/postModLoad alone, which deadlocked T75f's boot \(storage area\).
- T76's first kernel build \(run 41109301209\) failed: XNU has no kOSReturnNoMemory; OSKextRegisterBoardClasses and its callers use kOSKextReturnNoMemory \(libkern/OSKextLib.h\), and the helper has a prototype before its definition.
- T76's second kernel build \(run 41111730079\) failed in ShengPlatformPower.cpp: BoardClasses.h had been included after the file's last \#include, which there sits inside the ShengPlatformPower class; every probe now includes it after its first \#include.

### 完成条件

- The OS boots to the desktop with the platform power and keystore services it needs.

### 当前范围

- No battery or charging status.

### 下一步

- Port sheng's battery manager after the ADSP start.

### 证据

- `device`: [T29: with the stand-in, SpringBoard boots to the first picture.](https://github.com/rootstockos/UniXNU-asteroids/blob/6370e66cc460202756058ae53f73afdb69abd364/package/KeyStoreProbe.cpp)
  Command: <code>fastboot boot local/unixnu-asteroids-t29-boot.img</code>. Revision: `adf900cf453a6b318864913757f588c9f661596f`.

## 镜像组装 {#packaging}

`implemented`

### 硬件与依赖

- The payload carries the kernel, the ADT from the shared generator, the trust caches and the GPU addon; the boot image carries the phone's live DTB.

### 配置

- \[payload\] size\_mib = 80, panic\_screen = true; the device patch series lists the fork's bring-up patches and the board CPU patches.

### 操作步骤

- ./unixnu build payload, then ./unixnu bootimg --dtb with the live DTB.

### 开发经验

- Format 2 applies only the patches its series list; the fork's bring-up patches are listed in the device series with the arch: prefix.
- T64 \(2026-10-29\): the DTS memory node grows to the whole high bank \(0x8C0000000 + 0x23FE00000\) with board.toml dram\_size; the uefi-asteroids map declares it as one run without GPU\_Pool \(memory area\).
- T76 \(2026-10-30\): the board classes here register through OSKextRegisterBoardClasses \(zzyg-board-class-registration.patch\), under the kext lock, in place of preModLoad/postModLoad alone, which deadlocked T75f's boot \(storage area\).
- T76's first kernel build \(run 41109301209\) failed: XNU has no kOSReturnNoMemory; OSKextRegisterBoardClasses and its callers use kOSKextReturnNoMemory \(libkern/OSKextLib.h\), and the helper has a prototype before its definition.

### 完成条件

- The boot image boots on the phone with the expected kernel arguments.

### 当前范围

- The payload is built locally in the rootstock Podman machine.

### 下一步

- Build the first format 2 kernel in CI and pack it.

### 证据

- `source`: [Board patch series after the arch, SoC and OS series.](https://github.com/rootstockos/UniXNU-asteroids/blob/6370e66cc460202756058ae53f73afdb69abd364/patches/xnu/series)

## 诊断 {#diagnostics}

`implemented`

### 硬件与依赖

- sheng's boot progress kit: the live page, fault evidence, the UI trace and the banner rows.

### 配置

- sheng-log=1 keeps a persistent kernel log; sheng-banner=1 draws the rows on the desktop.

### 操作步骤

- Boot with the banner on and photograph it; pull Data for the unified log.

### 开发经验

- iOS 27 \(2026-11-04\): package/BootProcessWorker.c and BootReset.c are sheng's, for the source storage runtime, which on 27 also runs the process capture and the watchdog launch policy \(no BootProgress on 27\); details in the storage area.
- Never boot a test without on-screen diagnostics: T24b had none and taught nothing.
- T37 adds sheng's UFS diagnostic log \(BootLog.c, sheng-log=1\) through NativeUfs's log window \(the last 32 MiB of userdata\), with weak stand-ins \(BootLogStandins.c\) for the 104 references to probes this board does not build; scripts/pull-asteroids-log.py copies the window from recovery over adb and decodes it with sheng's read-sheng-log.py --decode. The unified log on Data cannot tell boots apart \(one boot UUID and clock base for every boot\).
- T43: \[direct scanout\] adds held / timed out \(sheng-dpu-hold\).
- T44: \[direct scanout\] frame gaps and the \[gpu load\] row \(BootLog.c, native\_gpu\_windows with a BootLogStandins.c stand-in\).
- T46: \[frames\] \(native\_legacy\_frames\) replaces T44's frame gaps in \[direct scanout\].
- T47: \[direct scanout\] loses the GPU wait and hold counters with the code they counted.
- T48: \[dpu probe\] counters and up to 24 \[dpu probe n\] rows \(slot, flags, fences, flip/latch/leave signatures\).
- T49: \[mic peaks\] \(the capture's peak per second and its start time\) and BTN taps=.
- T51: \[frame time\], \[gpu time\], \[gpu maint\] and \[fence asked\] rows; \[frames\] buckets 9/17/25/34/50 ms.
- T53: \[gpu work\] \(passes, system-memory passes, blits, draws, render area per submission against GPU time\).
- T54: \[gpu sysmem why\] \(system-memory pass reasons against GPU time\).
- T55: \[gpu ops\] \(GPU time per pass kind, blit, copy, resolve and clear, from Turnip's timestamp brackets\).
- T61: sheng-gpu-trace-export=&lt;seconds&gt; exports the render server's GPU trace directory \(m2v/gpu, boot\_diag\_scan\_gpu\) with the screen every so many seconds, each round into the 64 MiB quarter of the diagnostic half that the header does not name, so the header always names a complete copy whenever the phone is taken to recovery; a full export \(sheng-diag-export\) still runs once and ends the rounds. While it runs, the Metal plugin's pipeline-cache exports are refused, as with any diagnostic export. \[diag\] counts the rounds. scripts/pull-asteroids-log.py now also reads a named diagnostic export from the export region, unpacks it into diag/ and runs scripts/gpu-trace.py into gpu-trace.txt.
- T62: \[gpu tables\] \(sheng's row: table mode, CP aperture and switch check, switches by CP and CPU, address spaces, table pages on demand, ias, BO pool chunks\) and \[gpu recovery\] \(hangs and restarts, shown once one happened\); eight \[gpu client text\] rows.
- T64 \(2026-10-29\): \[bo pool\] is replaced by \[bo memory\]: system BOs made and their spans, MiB in use and peak, refusals with the last status, kernel-owned allocations and import spans, from the driver's native\_adreno\_bo\_memory; \[gpu tables\] drops the pool chunk counts.
- T64: \[gpu uc\] rows: the GPU probe's stage \(0x108 passed, 0x10e missed\), its kernel-client test counters \(rounds, steps, first error and its step, burst, system BOs, opens\) and the test's result lines.
- T65: \[bo pool\] in the boot log shows the GPU BO pool next to \[bo memory\]: MiB and chunks reserved, the reservation's and write-combine's IOReturn, BOs it served, BOs sent to system memory for lack of room, MiB in use and peak.
- T73 \(2026-10-30\): until the root is mounted, the UFS log shows \[late probe\] \(bsd\_autoconf's probe step, key events and CPU clock stages\) and \[kernel threads\]: every kernel thread that keeps its stack while it waits, with name, state, wait event and unslid return addresses \(boot\_kthread\_blocked\_rows\), '\*' for bsd\_autoconf's thread.
- T89 \(2026-11-02\): the boot log adds \[mic port\] \(native\_mic\_port: the microphone decimator, the codec's and the master's data port 1 while the capture runs; audio area\).
- T93 \(2026-11-02\): the boot log adds \[mic codec\] \(native\_mic\_codec: the WCD9378's TX sequencer, SmartMIC0 status and power state, usage, gains, clocks and micbias while the capture runs; audio area\).
- T94 \(2026-11-02\): \[mic codec\] prints whenever \[mic port\] does, zeros included.
- T95 \(2026-11-02\): the boot log adds \[mic page\] \(native\_mic\_page: whether the WCD9378's paged registers answer; audio area\).

### 完成条件

- Each test boot shows its stage and counters on screen.

### 当前范围

- The unified log needs a Data pull through recovery.

### 下一步

- Keep the banner rows for each new driver.

### 证据

- `source`: [Live page and banner rows.](https://github.com/rootstockos/UniXNU-asteroids/blob/6370e66cc460202756058ae53f73afdb69abd364/package/BootProgress.c)

</div>
