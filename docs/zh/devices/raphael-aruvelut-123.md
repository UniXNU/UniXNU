# Redmi K20 Pro / Mi 9T Pro \(raphael, SM8150\) - arm64 port of iPadOS 18.7.12 \(22H390\). Kernel from the arm64 iPadOS restore, root image from the iOS 18.7.12 paylo \(Aruvelut-123\)

[Aruvelut-123/UniXNU-raphael](https://github.com/Aruvelut-123/UniXNU-raphael)

<div v-pre>

Redmi K20 Pro / Mi 9T Pro \(raphael, SM8150\) arm64 UniXNU port, targeting ipados-18.7.12-22H390 \(Darwin 24.6.0\).

源记录: [porting.toml](https://github.com/Aruvelut-123/UniXNU-raphael/blob/f16ce447b49adf258491ccc0e08212ac476ba694/porting.toml), `f16ce447b49adf258491ccc0e08212ac476ba694`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `implemented` |
| [固件与启动](#firmware) | `device-verified` |
| [CPU 与中断](#cpu) | `planned` |
| [内存与 DMA](#memory) | `planned` |
| [存储与根卷](#storage) | `planned` |
| [显示](#display) | `planned` |
| [输入](#input) | `planned` |
| [GPU](#gpu) | `planned` |
| [网络](#network) | `planned` |
| [音频](#audio) | `planned` |
| [电源](#power) | `planned` |
| [镜像组装](#packaging) | `host-verified` |
| [诊断](#diagnostics) | `planned` |
| [platform-expert](#platform-expert) | `device-verified` |

## 配置 {#configuration}

`implemented`

组件: `ArmDTPlatform`.

### 硬件与依赖

- SM8150 device identity and partition plan from the raphael board configuration
- OS profile ipados-18.7.12-22H390 \(arm64\) carried by this repository and installed into the UniXNU checkout
- iOS 18.7.12 payload IPSW and the staged iPadOS 18.7.12 arm64 kernelcache, both build 22H390
- Shared SM8150 support pinned in feeds.toml

### 配置

- format 2 board: soc\_source=sm8150, kit=raphael, os\_profile=ipados-18.7.12-22H390
- upstream UniXNU has no 18.x profile, so os-profiles/ipados-18.7.12-22H390/ is copied in by scripts/install-device-profile.py
- the arm64 kernelcache is staged by scripts/stage-arm64-kernelcache.py into the path \[kernel.prelink\] kernelcache names
- kernel fragments arch:configs/common.config and soc:configs/sm8150.config
- arm64e-only profiles are intentionally not mapped: SM8150 has no FEAT\_PAuth
- configs/raphael\_defconfig selects CONFIG\_XNU\_CRYPTO\_BOOTSTRAP=prelinked; a native-only --skip-prelink image therefore has no source crypto callbacks and no retained Apple crypto provider
- v41 hardware probe reads g\_crypto\_funcs as zero inside the generatePlatformUUID SHA-1 call, matching the native-only build path
- the 22H390 arm64 kernelcache contains com.apple.kec.corecrypto; adding the qualified 31 roots gives a 38-entry dependency closure containing corecrypto, APFS and AMFI dependencies
- using the prior CI native kernel artifact and the verified 22H390 cache, host prelink emitted a 55,156,736-byte experimental candidate retaining all 31 roots and com.apple.kec.corecrypto; that native-only candidate was not qualified for hardware
- CI run 43892011062 compiled and linked XNU, then prelink failed because kernelcache was staged under checkout out/raphael while the profile-relative lookup resolved under the isolated tree/out/raphael; pass the staged file through UNIXNU\_KERNELCACHE
- CI run 43894941089 completed the formal macOS prelink with the staged kernelcache override: the 31-root command included com.apple.kec.corecrypto and emitted kernel.macho at 55,156,736 bytes \(sha256 1526a3df9d1b563ef2cde0a2afdfa25c31448679fa93f6ff0ca6b52139394ab1\); the workflow does not publish loadable, relocation-complete, ABI or runtime qualification fields, so those remain unverified
- the formal prelinked kernel is 52.6 MiB while payload.py accepts only 95% of the FAT size for files; the old 48 MiB volume therefore rejected the 22H390 kernel at 52 MiB, and size\_mib=56 leaves the required headroom while the measured Aloha fixed overhead predicts a boot image near 59.4 MiB

### 操作步骤

- From the UniXNU checkout: python3 ../UniXNU-raphael/scripts/install-device-profile.py --unixnu .
- python3 ../UniXNU-raphael/scripts/stage-arm64-kernelcache.py --unixnu .
- ./unixnu defconfig raphael\_defconfig -D ../UniXNU-raphael, ./unixnu fetch -D ../UniXNU-raphael, then ./unixnu status --json -D ../UniXNU-raphael

### 开发经验

- arm64e-only Apple OS profiles \(iPadOS 26/27\) cannot run on this SoC \(no FEAT\_PAuth\); iPadOS 18 still ships an arm64 kernelcache because the no-PAC A10 iPad 7 runs it
- UniXNU reads exactly one IPSW per run, so the iOS payload is \[ipsw\] and the arm64 kernelcache is passed to prelink by path instead
- iPadOS and iOS share the 22H390 build ID, so the staged kernelcache needs its own output path or the two would overwrite each other in out/ipsw/22H390/
- both 22H390 dmgs are AEA encrypted, so building the root image needs macOS /usr/bin/aea
- status resolves arch=arm64, soc=sm8150, os=ipados-18.7.12-22H390 and the device board.toml
- board.toml \[firmware\] and \[bootimg.image\] describe the Mu-Silicium route only \(config raphael, Platforms/Xiaomi/raphaelPkg/raphael.dsc, SILICIUM\_UEFI.fd, header\_version 1 with base 0x10000000 and pagesize 2048\); ./unixnu build firmware and ./unixnu bootimg read those paths, and that route has never produced an image that booted on this device
- the shipping firmware route is Project Aloha instead: build\_cfg/sm8150.json uses header\_version 0 with base 0 and pagesize 4096, and PythonLibs/PostBuild.py is the packer, so the Mu-Silicium values in \[bootimg.image\] are deliberately not applied to it
- board.toml \[payload\] is what makes the Aloha image bootable: volume UNIXNU, 56 MiB, loader firmware, carrying Payloads/kernel.macho, its ADT and EFI/UniXNU/unixnu.toml; 56 MiB is required by the 55,156,736-byte formal prelinked kernel and payload.py's 95% file-content limit

### 完成条件

- Every profile root, source pin, component closure and patch order resolves without error

### 当前范围

- Resolution success is not a boot result; nothing here has run on raphael hardware

### 下一步

- Run the macOS build without --skip-prelink and inspect the candidate report for the retained crypto closure
- Obtain a loadable, relocation-complete and runtime-qualified candidate, then repeat the v41 check with a nonzero g\_crypto\_funcs expectation
- Record the resolved status output as host evidence once the CI build produces it

### 证据

- `source`: [Format 2 board definition with the arm64 ipados-18.7.12-22H390 profile \(iOS 18.7.12 payload for the root image, staged iPadOS 18.7.12 arm64 kernelcache for prelink\) and raphael\_defconfig mapping.](https://github.com/Aruvelut-123/UniXNU-raphael/blob/f16ce447b49adf258491ccc0e08212ac476ba694/board.toml)
- `source`: [Pinned shared SM8150 source used as the soc profile.](https://github.com/Aruvelut-123/UniXNU-raphael/blob/f16ce447b49adf258491ccc0e08212ac476ba694/feeds.toml)

## 固件与启动 {#firmware}

`device-verified`

组件: `DarwinBoot`.

### 硬件与依赖

- Project Aloha platforms checkout \(Project-Aloha/mu\_aloha\_platforms\), which lists xiaomi-raphael and builds the SurfaceDuo1Pkg platform
- Aloha's own packer: build\_uefi.py drives Platforms/SurfaceDuo1Pkg/PlatformBuildNoSb.py, and PythonLibs/PostBuild.py writes the Android boot image from BootShim.bin + FV/SM8150\_EFI.fd + the device DTB
- build\_cfg/sm8150.json for the boot geometry \(header\_version 0, base 0, pagesize 4096\) and Device/xiaomi-raphael/\*.inc for the module set

### 配置

- board.toml \[firmware\] still names the Mu-Silicium layout \(config raphael, Platforms/Xiaomi/raphaelPkg/raphael.dsc, FD Build/raphaelPkg/&\#123;target&\#125;\_CLANGPDB/FV/SILICIUM\_UEFI.fd\); ./unixnu build firmware and ./unixnu bootimg read exactly those paths, which is why the Aloha route does not go through them
- the Aloha route is driven by scripts/stage-aloha-unixnu.py: it writes Include/UniXNU.dsc.inc, Include/UniXNU.fdf.inc and Include/UniXNULLib.dsc.inc, sets BUILD\_UNIXNU in both SurfaceDuo1.dsc and SurfaceDuo1NoSb.dsc, packages those includes after DXE.dsc.inc / DXE.inc, and appends ALOHA\_EXTRA\_PACKAGES to the hard-coded PACKAGES\_PATH tuple in both PlatformBuild\*.py
- the disk stack is not added again: Device/xiaomi-raphael/APRIORI.inc embeds DiskIoDxe and PartitionDxe as fixed-GUID PE32 images and SurfaceDuo1.fdf already lists FatPkg, so the script only verifies them
- BUILD\_UNIXNU=1 compiles UniXNU, UniXNUDxe, UniXNURamDiskDxe and DarwinBoot into the FD; BUILD\_UNIXNU=0 leaves a byte-identical stock Aloha build

### 操作步骤

- python3 scripts/stage-aloha-unixnu.py --aloha &lt;mu\_aloha\_platforms&gt; --unixnu &lt;UniXNU&gt; --payload &lt;payload.img&gt;
- cd &lt;mu\_aloha\_platforms&gt; &amp;&amp; python3 build\_uefi.py --init, then ALOHA\_EXTRA\_PACKAGES=&lt;UniXNU&gt;/package:&lt;UniXNU&gt;/drivers/DarwinBoot python3 build\_uefi.py -d xiaomi-raphael
- fastboot flash boot &lt;aloha&gt;/Build/SurfaceDuo1Pkg/xiaomi-raphael.img

### 开发经验

- the Mu-Silicium raphael platform never booted on hardware; Project Aloha lists xiaomi-raphael as supported and is what produced the working image
- ./unixnu build firmware and ./unixnu bootimg only understand the Mu-Silicium layout \(Resources/Configs/&lt;config&gt;.toml with \[uefi\_fd\], Resources/Scripts/mkbootimg.py, BootShim.S built with -DFD\_BASE/-DFD\_SIZE\), so an Aloha checkout cannot be passed to --uefi; Aloha packs its own boot image instead
- build\_uefi.py drives EDK II through os.system and ignores the child's exit status, so a failed build still exits 0; the workflow verifies FV/SM8150\_EFI.fd and the .img exist rather than trusting the exit code
- the boot geometry that boots on this device is build\_cfg/sm8150.json as-is \(kernel\_addr 0x8000, ramdisk\_addr 0x1000000, tags 0x100, pagesize 4096, i.e. base 0\). board.toml \[bootimg.image\] pins base 0x10000000 for the Mu-Silicium route; forcing that here would move the shim to 0x10008000 for no benefit
- PostBuild.py:99-100 emits --ramdisk ./PythonLibs/emptyramdisk whenever emptyramdisk is true, and that file is a six-byte placeholder \(b'dummy\\n'\). Copying the payload over it is the one seam Aloha exposes without patching PythonLibs
- with the placeholder ramdisk the menu still renders but falls back to the built-in configuration, which has no bootable entry: Config.c reads \\EFI\\UniXNU\\unixnu.toml from any SimpleFileSystem volume and UniXNURamDiskDxe publishes the payload volume as BlockIo from the FDT /chosen initrd range
- the kernel and the firmware are built in one workflow run \(jobs build on macos-26 and firmware on ubuntu-24.04, joined by needs\), so the payload can only carry the kernel that run compiled; the firmware job re-checks kernel.macho's sha256 against the build job's output before packing it
- the firmware job runs on a plain push to main as well as on dispatch: the platform seed comes from the UNIXNU\_UNIQUE\_CHIP\_ID repository variable, and only an explicit dispatch with build\_firmware=false turns the job off
- the payload volume is sized for the boot partition, not for comfort: the formal 22H390 kernel.macho is 55,156,736 bytes \(52.6 MiB\), so payload.py's 95% content limit requires size\_mib=56; the prior 192 MiB volume produced a 195 MiB boot image that cannot be flashed, while the measured Aloha fixed overhead predicts about 59.4 MiB at 56 MiB payload size
- the payload image itself is byte-correct: the boot image header reports ramdisk\_size 50331648 at ramdisk\_addr 0x1000000, and check-bootimg-ramdisk.py confirms the ramdisk is the payload. The problem is that the ramdisk is never published as a UEFI volume
- UniXNURamDiskDxe reads the DTB address from the Mu-Silicium entry-argument HOB \(0xDAEE82E6...\), which only that platform's SEC emits. Searching the whole tree shows no producer of that HOB at all, so on Aloha the driver returns at 'no entry argument HOB' and publishes nothing
- a fallback to the FDT configuration table \(gFdtTableGuid\) alone is not enough: Aloha installs the Android board tree, whose /chosen names the MIUI boot's initrd \(0x84518000\) rather than this handoff's ramdisk, so the driver read a valid tree and still published the wrong range; the UniXNU FV entries were moved after DtPlatformDxe and its FDT freefile because a configuration table is not a protocol and cannot be expressed as a Depex
- the driving fix is a fallback that does not depend on a tree at all: UniXNURamDiskDxe scans the HOB system-memory ranges for the payload's FAT32 boot sector \(mformat OEM MTOO4043, volume label UNIXNU, 0x55AA signature, BPB geometry check\) and publishes whatever it finds, so the volume is reachable even though Aloha publishes neither the Mu-Silicium HOB nor a /chosen that points at the payload
- the driver change is shipped as a patch applied by .github/workflows/build.yml \(patches/unixnu/ramdisk-scan-fat-volume.patch, applied right after the UniXNU checkout\). Editing the local UniXNU copy had no effect at all: the workflow checks out UniXNU/UniXNU@main, so only a patch in this repository reaches the firmware; the earlier 'fallback' had never been in any built image, which is why flashing still showed the built-in configuration
- the firmware job log is the evidence that the patch is in the image: 'Applied patch .../UniXNURamDiskDxe.c cleanly.', then 'Building ... UniXNURamDiskDxe.inf \[AARCH64\]' under -Wall -Werror, with 'Build total time: 00:01:39' and a 3145728-byte FV
- the Aloha EDK II chain is Linux-only: build\_setup.sh is an apt script and CLANGPDB uses aarch64-linux-gnu-gcc, so the macOS runner cannot host it; the XNU kernel conversely needs Xcode, cctools and lzfse

### 完成条件

- A firmware volume builds, and the boot image carries the UniXNU payload volume as its ramdisk
- UniXNU draws its boot menu on raphael
- UniXNURamDiskDxe compiles into the firmware together with the system-memory scan patch, so the payload volume has a path to BlockIo that does not need the Mu-Silicium HOB or a /chosen that names it

### 当前范围

- Verified on the handset \(images built before this patch\): the menu renders with working UI, fonts and input, but the footer reads "built-in configuration", so no unixnu.toml was found. On those images the driver had no path to the volume at all, which is why the DTB swap and the FDF reorder changed nothing on screen
- The scan fallback only makes the volume reachable; whether the menu then lists the xnu entry and hands off to DarwinBoot is still an on-device question. The 56 MiB payload is sized for the formal 52.6 MiB prelinked kernel and is estimated to keep the boot image near 59.4 MiB
- DarwinBoot has not handed off to XNU on this device: CI now emits the formal prelinked Mach-O, but no loadable, relocation-complete, ABI-qualified or runtime-qualified result has yet been established

### 下一步

- Flash the image built with the scan patch \(xiaomi-raphael-v4.img\) and confirm the menu lists the xnu entry instead of "built-in configuration", then capture the DarwinBoot handoff

### 证据

- `source`: [jobs.build runs on macos-26 \(Xcode, cctools, lzfse\) and produces kernel.macho; jobs.firmware runs on ubuntu-24.04 with needs: build, packs that run's kernel into the payload volume, installs it as Aloha's ramdisk and verifies the result with scripts/check-bootimg-ramdisk.py.](https://github.com/Aruvelut-123/UniXNU-raphael/blob/f16ce447b49adf258491ccc0e08212ac476ba694/.github/workflows/build.yml)
- `source`: [Patches both Aloha DSC variants and the FDF to compile UniXNU, UniXNUDxe, UniXNURamDiskDxe and DarwinBoot into the FD, teaches PlatformBuild\*.py about ALOHA\_EXTRA\_PACKAGES, and with --payload installs the volume over PythonLibs/emptyramdisk.](https://github.com/Aruvelut-123/UniXNU-raphael/blob/f16ce447b49adf258491ccc0e08212ac476ba694/scripts/stage-aloha-unixnu.py)
- `device`: [UniXNU draws its menu on raphael: blue title, Input/Tools on the right, and the footer reads "built-in configuration", which is Config.c:1595 falling back because no \\EFI\\UniXNU\\unixnu.toml volume was present.](https://github.com/Aruvelut-123/UniXNU-raphael/blob/f16ce447b49adf258491ccc0e08212ac476ba694/docs/evidence/2026-11-14-aloha-unixnu-menu.md)
  Command: <code>fastboot flash boot aloha-unixnu.img, then photograph the UniXNU boot menu on the handset</code>. Revision: `dc881bab4a5c44206ecb6802ef2cb8a58349169c`.
- `host`: [Both jobs pass in one run: build compiles the kernel on macos-26, firmware installs device-tree-compiler and mtools, builds the 192 MiB payload volume, stages it over PythonLibs/emptyramdisk, builds Aloha, and asserts in step 17 that the boot image ramdisk is the payload. The artifact aloha-raphael-bootimg carries SM8150\_EFI.fd \(3145728 B\), payload.img \(201326592 B\) and xiaomi-raphael.img \(204840960 B\); scripts/check-bootimg-ramdisk.py reports the ramdisk is the payload volume at offset 0x35a000.](https://github.com/Aruvelut-123/UniXNU-raphael/actions/runs/43620004865)
  Command: <code>gh api -X POST repos/Aruvelut-123/UniXNU-raphael/actions/workflows/build.yml/dispatches -f ref=main -f 'inputs[build_kernel]=true' -f 'inputs[build_firmware]=true' -f 'inputs[unique_chip_id]=0123456789ABCDEF'</code>. Revision: `43803ea568627dd054c7ae5a3ade9d446f4e2d7d`.

## CPU 与中断 {#cpu}

`planned`

组件: `XnuPrelink`.

### 硬件与依赖

- CPU topology for SM8150 \(four Cortex-A76 plus four Cortex-A55\) from the vendor DTS

### 配置

- raphael\_defconfig carries the kernel options; CPU enablement is not yet wired to a device tree

### 操作步骤

- Build the kernel, boot it and capture the CPU bring-up log

### 开发经验

- SM8150 Cortex-A76 and A55 do not implement ARMv8.3 FEAT\_PAuth, which is why arm64e is excluded
- xnu-11417.140.69 \(Darwin 24\) dropped the BCM2837 machine configuration entirely: 'grep -r BCM2837' over the tree returns nothing, pexpert/pexpert/arm64/BCM2837.h and config/MASTER.arm64.bcm2837 no longer exist, and the supported list is now T6000..T8132 VMAPPLE. Apple added config/MASTER.arm64.iPhoneOS in their place
- the shared arch patch series \(profiles/arch/arm64/patches/xnu/series, 56 patches\) was written against xnu-10063.141.1 / Darwin 23 and does not survive the move: 15 of the 56 fail 'git apply --check' against xnu-11417, 41 still apply. Two of the 15 \(native-arm-pan, source-machine-layer\) fail because their target file is gone, not merely shifted; the other 13 fail on hunk context alone
- the prelink path still names DEVELOPMENT\_ARM64\_BCM2837 \(profile.toml \[kernel.prelink\] kernel\), so the machine configuration has to be settled before any kernel link can be trusted
- pong \(SM8475, /tmp/pong18\) resolved the same problem by dropping BCM2837 rather than reviving it: it adds config/MASTER.arm64.pong, registers PONG in SUPPORTED\_ARM64\_MACHINE\_CONFIGS, builds DEVELOPMENT\_ARM64\_PONG, and leaves profiles/arch/arm64's own series out of its patch\_series behind an effectively empty migration/format2/arch-darwin24.series. Its Darwin24 work rides in a single 480 KB device aggregate \(patches/xnu-ipados18/0001-pong-darwin24.patch, 97 files\) that is SoC-specific and not reusable here

### 完成条件

- All eight CPUs come up and the interrupt controller delivers timer interrupts

### 当前范围

- No device log exists yet; the CPU area is unverified on hardware
- The Darwin 23 -&gt; 24 arch adaptation is not started: nothing yet replaces the 15 failing arch patches or names the machine configuration the kernel will actually be built with

### 下一步

- Decide the machine configuration: drop BCM2837 for a raphael one \(pong's path\) or regenerate the arch series against xnu-11417
- Boot the arm64 kernel and record the per-CPU startup log

### 证据

按下一步操作收集证据。

## 内存与 DMA {#memory}

`planned`

### 硬件与依赖

- RAM size and reserved region plan for raphael

### 配置

- dts/raphael.dts declares a 4 GiB memory node; reservations are not yet described

### 操作步骤

- Extend the device tree with the reserved-memory nodes and boot the kernel

### 开发经验

- Boot page table capacity for the native 4 KiB granule is handled by the arch profile patches, not by this device

### 完成条件

- XNU maps the full RAM range and the reserved regions stay out of the kernel map

### 当前范围

- The current device tree is a skeleton and has not been used for a boot

### 下一步

- Add reserved-memory nodes for firmware, display and modem regions

### 证据

按下一步操作收集证据。

## 存储与根卷 {#storage}

`planned`

### 硬件与依赖

- GPT entry for the root partition, from the device partition table
- Shared SM8150 UFS operations from the pinned SoC repository

### 配置

- Root image is built with ./unixnu build userdata from the board partition geometry and the OS profile's IPSW
- scripts/build-root.sh prefers a unixnu partition label and falls back to userdata at flash time

### 操作步骤

- scripts/build-root.sh --ipsw restore.ipsw --dry-run, then --flash

### 开发经验

- UniXNU selects root by APFS volume UUID written into the ADT, so a boot-time partition search is not available
- Kernel and root image must be the same build \(22H390 here\); the root is the iOS 18.7.12 payload and the kernelcache the same-build iPadOS 18.7.12 arm64 one, and builds must never be mixed across Darwin versions
- the payload dmgs are AEA encrypted, so the root image can only be assembled on macOS

### 完成条件

- XNU mounts the root volume read-only and starts launchd

### 当前范围

- The matching SHNGROOT image was built and flashed; XNU root mounting and launchd remain unverified
- Image SHA-256 b8f8c41637b0d4918e91241fab771224f6985154631feaca80ffff9e755b1f75; OS and SystemOS UUIDs were extracted from checksum-valid APFS superblocks

### 下一步

- Build with the extracted OS and SystemOS volume UUIDs and verify XNU root mounting on hardware
- Download the payload IPSW once and fill the \[ipsw.sha256\] member pins

### 证据

按下一步操作收集证据。

## 显示 {#display}

`planned`

### 硬件与依赖

- Panel timing and DSI configuration for the raphael panel

### 配置

- No display nodes are described in the device tree yet

### 操作步骤

- Boot the kernel and capture the framebuffer handoff log

### 开发经验

- GopFramebuffer is not selected for this board, so there is no handoff path yet

### 完成条件

- The kernel console and SpringBoard both render on the panel

### 当前范围

- Display is unverified; no panel timing has been collected

### 下一步

- Collect panel timings and add a display node plus the framebuffer component

### 证据

按下一步操作收集证据。

## 输入 {#input}

`planned`

### 硬件与依赖

- GT9889 touch controller wiring and I2C address

### 配置

- No input driver is selected or declared

### 操作步骤

- Integrate a HID provider and verify touch events in userspace

### 开发经验

- Touch bring-up has not started; the upstream raphael port has an independent GT9889 note

### 完成条件

- Touch events reach userspace and SpringBoard responds

### 当前范围

- No input hardware work exists in this repository

### 下一步

- Select a HID input component and record its required inputs

### 证据

按下一步操作收集证据。

## GPU {#gpu}

`planned`

### 硬件与依赖

- Adreno 640 firmware and command stream interface

### 配置

- No GPU component is selected

### 操作步骤

- Add the Adreno component chain and verify a userspace Metal or Vulkan probe

### 开发经验

- The Adreno driver family exists upstream but no raphael GPU work has been done here

### 完成条件

- A GPU client allocates a buffer and completes a queue submission

### 当前范围

- GPU is unverified and unstarted

### 下一步

- Review the Adreno component catalog entries for SM8150 compatibility

### 证据

按下一步操作收集证据。

## 网络 {#network}

`planned`

### 硬件与依赖

- WCN3990 Wi-Fi and Bluetooth firmware plus calibration data

### 配置

- No network driver is selected

### 操作步骤

- Add the wireless component chain and verify an association and a Bluetooth HCI open

### 开发经验

- Network bring-up has not started

### 完成条件

- The device associates with an access point and reports an interface to userspace

### 当前范围

- No network hardware work exists in this repository

### 下一步

- Identify the WCN3990 firmware and calibration inputs for raphael

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`planned`

### 硬件与依赖

- Audio DSP firmware and codec wiring for raphael

### 配置

- No audio component is selected

### 操作步骤

- Add audio components and verify playback from userspace

### 开发经验

- Audio bring-up has not started

### 完成条件

- A userspace client plays audio through the device speaker

### 当前范围

- No audio hardware work exists in this repository

### 下一步

- Collect the DSP firmware inputs from the vendor partition

### 证据

按下一步操作收集证据。

## 电源 {#power}

`planned`

### 硬件与依赖

- PMIC and regulator topology for raphael

### 配置

- No power component is selected

### 操作步骤

- Add the power component chain and verify rail state across a suspend and resume

### 开发经验

- Power management has not started

### 完成条件

- The device suspends and resumes without losing the framebuffer

### 当前范围

- No power hardware work exists in this repository

### 下一步

- Record the PMIC topology from the vendor device tree

### 证据

按下一步操作收集证据。

## 镜像组装 {#packaging}

`host-verified`

### 硬件与依赖

- Kernel Mach-O from the macOS job, the payload volume built from it, and the Aloha firmware volume built from the staged boot chain
- IPSW disk image or a raw root image to convert into the flashable unixnu/userdata image

### 配置

- jobs.build \(macos-26\) runs defconfig, fetch, status, formal prelink, package and uploads kernel.macho; jobs.firmware \(ubuntu-24.04, needs: build\) builds the payload from that kernel and then the firmware, so the two artifacts of one run cannot disagree
- scripts/stage-aloha-unixnu.py --payload installs payload.img over PythonLibs/emptyramdisk, which PostBuild.py hands to mkbootimg as --ramdisk; scripts/check-bootimg-ramdisk.py then fails the run unless the boot image ramdisk is byte-identical to the payload volume
- scripts/report-payload.py reads payload.json rather than parsing log text, and reports the kernel, ADT and volume hashes
- scripts/ipsw\_to\_sparse.py converts a raw image to libsparse chunks and self-verifies the result

### 操作步骤

- gh workflow run build.yml -f build\_kernel=true -f build\_firmware=true -f unique\_chip\_id=&lt;HEX&gt;
- python3 scripts/ipsw\_to\_sparse.py --raw-image userdata-root.img --output unixnu.sparse
- fastboot flash boot xiaomi-raphael.img and fastboot flash unixnu unixnu.sparse

### 开发经验

- the two products of a run are the boot image and the root image; they are independent. Flashing the sparse root image does not supply the payload, because the payload is the boot image ramdisk and is read through UniXNURamDiskDxe, not from the root partition
- the boot image and the payload have to come from one run: pulling kernel.macho out of an older build.yml run silently pairs a firmware with a stale kernel, so jobs.firmware both depends on jobs.build and re-checks the artifact's sha256
- the kernel cannot be built on the Linux runner: setup-toolchain.py compiles a patched LLVM and cctools-port from source, and the kernel step dies on the first missing host tool \(unifdef, then lzfse\) long before that finishes
- Sparse output is produced only from a raw image; AEA-encrypted IPSW payloads need macOS tooling and the script reports that instead of emitting a bad image. root-image.yml handles that case on macos-26
- the boot image ramdisk is 56 MiB by board.toml \[payload\] size\_mib, so the packed .img grows by that amount; Aloha's own emptyramdisk placeholder is six bytes, which is why a stock build looks small

### 完成条件

- One run produces a boot image whose ramdisk is the payload volume, plus the UniXNU.efi and kernel.macho artifacts

### 当前范围

- The firmware and payload jobs run green in CI; the image they produce has not been flashed, so the packed-ramdisk path is host-verified only

### 下一步

- Flash the packed boot image and record the menu result as device evidence, then move this area to device-verified

### 证据

- `source`: [Parses the v0-v2 boot image header, locates the ramdisk by page-aligned kernel size and exits non-zero unless those bytes equal the payload volume. Against the baseline image it reports a 6-byte ramdisk holding b'dummy\\n', which is exactly the placeholder that produced the built-in configuration menu.](https://github.com/Aruvelut-123/UniXNU-raphael/blob/f16ce447b49adf258491ccc0e08212ac476ba694/scripts/check-bootimg-ramdisk.py)
- `host`: [The Aloha workflow on ubuntu-24.04 reached the XNU kernel step and failed there with 'unifdef not found on PATH', which is the measurement that moved the kernel build back to the macOS job.](https://github.com/Aruvelut-123/UniXNU-raphael/actions/runs/43613243577)
  Command: <code>gh api repos/Aruvelut-123/UniXNU-raphael/actions/runs/43613243577/jobs --jq '.jobs[].steps[] | &#123;name,conclusion&#125;'</code>. Revision: `8dd26ff2a7fc82e8ae3aae13645a8d3d22ea1f7c`.
- `host`: [The folded workflow completes end to end: jobs.build \(macos-26\) compiles the kernel and records its sha256, jobs.firmware \(ubuntu-24.04\) downloads that artifact, refuses to continue on a hash mismatch, and produces aloha-raphael-bootimg. Downloaded and re-checked locally, the boot image's ramdisk is byte-identical to payload.img \(201326592 bytes at offset 0x35a000\).](https://github.com/Aruvelut-123/UniXNU-raphael/actions/runs/43620004865)
  Command: <code>gh run download 43620004865 -R Aruvelut-123/UniXNU-raphael -n aloha-raphael-bootimg -D /tmp/art; python3 scripts/check-bootimg-ramdisk.py /tmp/art/xiaomi-raphael.img /tmp/art/payload.img</code>. Revision: `43803ea568627dd054c7ae5a3ade9d446f4e2d7d`.

## 诊断 {#diagnostics}

`planned`

### 硬件与依赖

- Serial or UART access path for raphael, or a framebuffer console fallback

### 配置

- No log transport is configured for this device

### 操作步骤

- Capture firmware and kernel output during a boot attempt and attach it as device evidence

### 开发经验

- User reports v14 and v15 show the boot entry then remain on a green top bar; v15 includes the extracted root UUIDs with no observed improvement
- DarwinBoot 5243c68 Entry.S paints the green bar in DarwinEnter after ExitBootServices but before cache maintenance, MMU shutdown and the branch to XNU; the green bar alone does not establish kernel entry
- Device report: v16 shows blue and magenta XNU probes; v17 resets with the post-MMU probe, v18 resets with the probe after the first PE\_init\_platform call, and v19 resets with the probe after arm\_vm\_init in arm\_init
- Device report: v20 resets with the probe after the second PE\_init\_platform call in arm\_init \(call site 0xfffffff007a2e3b4\)
- Device report: v21 resets immediately. Source inspection confirms RESET\_BEFORE has no delay and directly invokes PSCI SYSTEM\_RESET before machine\_startup \(call site 0xfffffff007a2e410\); the earlier description of a six-second delay for v21 was incorrect. This supports reaching that call site
- Device report: v22 resets with the timed stage-4 probe after machine\_conf in machine\_startup \(call site 0xfffffff007475200\), before its tail branch to kernel\_bootstrap; exact reboot latency was not specified
- Device report: v23 resets after approximately six seconds with the probe after machine\_init in kernel\_bootstrap \(call site 0xfffffff007300e54\), supporting execution through that call
- Device report: v24 does not reset with the probe after PE\_init\_iokit in kernel\_bootstrap\_thread \(call site 0xfffffff007a0d804\). This does not isolate PE\_init\_iokit: intervening initialization, thread handoff and probe execution remain possible causes
- Device report: v25 resets with the probe after kernel\_thread\_create in kernel\_bootstrap \(call site 0xfffffff0073011fc\). The probe checks return before its status is tested, so this does not establish successful thread creation; exact reboot latency was not specified
- Device report: v26 resets with the probe after sched\_startup in kernel\_bootstrap\_thread \(call site 0xfffffff007a0d684\), supporting progress into the bootstrap thread; exact reboot latency was not specified
- Device report: v27 resets with the probe after the second kernel\_startup\_initialize\_upto call in kernel\_bootstrap\_thread \(call site 0xfffffff007a0d790\); exact reboot latency was not specified
- v28 places a timed reset before PE\_init\_iokit at the same call site as v24 \(0xfffffff007a0d804\). Generated by importing patch-xnu-entry-probe.py and replacing RESET\_BEFORE in memory with SOURCES\[4\] minus bl callee, formatted with TIMEBASE\*6 ticks; the original script remains unchanged. The emitted cave contains 115200000 ticks and SMC. Device report: v28 resets; exact latency was not specified
- Device report: v29 resets with the timed-before probe before InitIOKit within PE\_init\_iokit \(call site 0xfffffff0079db3bc\); exact latency was not specified. Uses the same timed-before generator as v28. SHA-256 9b57b1960698c784fb51685223acabd0fb8986b00702941d9b71b8e4ace42ec7
- Device report: v30 resets with the six-second stage-4 probe after InitIOKit within PE\_init\_iokit \(call site 0xfffffff0079db3bc\); exact latency was not specified. SHA-256 cddc6c1a34d8eee7be32bff340dff2639bc934c11f3bda49ee803e66fcd03b78
- Device report: v31 does not reset after ConfigureIOKit within PE\_init\_iokit \(call site 0xfffffff0079db3c0\); SHA-256 09219d2b421e52d61d9a1a8ebdc1ddc88dcdde0020173400f432274a31f754b8. Disassembly shows ConfigureIOKit tail-branches to IOPlatformExpertDevice::configureDefaults when the platform object exists; the latter calls createNVRAM before property handling and generatePlatformUUID
- Device report: v32 resets with the six-second probe after IOPlatformExpertDevice::createNVRAM in configureDefaults \(call site 0xfffffff007970d64\); exact latency was not specified. SHA-256 d722ac5daec6a027da3e36d3a2e182530188f770b792f30a787243d6e204b6ac
- Device report: v33 resets with the terminal six-second probe at IOPlatformExpertDevice::generatePlatformUUID entry \(0xfffffff00796f884\); exact latency was not specified. The configureDefaults tail branch at 0xfffffff007970dd4 was verified. This probe does not execute the UUID function body. SHA-256 ecdf5ea9fc35ee7e619a5dfc648ee5932b452d46002a8eb5679bcb11d6c08d2c
- Device report: v34 does not reset at the common exit of generatePlatformUUID \(0xfffffff00796fb38, before the stack-canary check\). Entry remains original; stage-1/2 bars retained. SHA-256 cf3cc2463c9787ac9aa47a2562c5254ed8b25c301392e6dc9400334823f5bd97. Together with the resetting v33 entry probe, this focuses investigation on the function body while retaining probe-execution uncertainty
- Device report: v35 resets after the first IORegistryEntry::fromPath call in generatePlatformUUID \(call site 0xfffffff00796f8e0\); exact latency was not specified. This supports return from the call and execution through the entry prologue, stack-canary load, movi v0 and stp q0, but does not establish a non-null lookup result. SHA-256 637f3cd0fba8068f6fe84128e0afae9b53b6bfbcdf04937f05e5d08b14f61730
- Device report: v36 resets; exact latency was not specified. It covers both successors of the first fromPath result test with terminal six-second probes: 0xfffffff00796f914 after the first property virtual call and safeMetaCast, and 0xfffffff00796fa70 at the null-lookup fallback entry. The report establishes reaching at least one of these sites, not which path, property validity or UUID success. SHA-256 f6dffe0f6c57d78ec9db4a59b70e585fb673615356cf1e5c0f4a862556f37866
- Device report: v37 resets after approximately six seconds. Its primary-path probe at 0xfffffff00796f96c waits six seconds, while probes at primary validation failure \(0xfffffff00796fa58\) and fallback entry \(0xfffffff00796fa70\) wait twelve seconds. This supports both primary data properties passing type and length checks \(8 and 4 bytes\) and reaching SHA1 setup, but does not prove hashing or UUID success. SHA-256 112fdd289d5aa1e2467389f6b243c9cd652babad06191d140a745e08e7c2284d
- Device report: v38 does not reset with the probe after SHA1Final \(call site 0xfffffff00796fa18, callee 0xfffffff007903c00\) in generatePlatformUUID. Together with v37 this focuses investigation on context setup, sha1\_init, three sha1\_loop calls, intervening data access and SHA1Final; it does not isolate SHA1Final itself. Probe execution uncertainty remains. SHA-256 b3142e6eaeefe447903eac63f8e1f2c8b1787202b964a870251feefc97ae0c21
- Device report: v39 does not reset after the first sha1\_loop/SHA1Update call in generatePlatformUUID \(0xfffffff00796f9a0, target 0xfffffff007903a64, input length 16\). With v37 this focuses investigation on context setup, sha1\_init and the first update, without isolating the update itself. SHA-256 ef0be6aef0cb6df4fcf4afbb1288454fe6e5ee9ddbd423476244d38a8a4d2258
- Device report: v40 does not reset after sha1\_init/SHA1Init in generatePlatformUUID \(call site 0xfffffff00796f98c, target 0xfffffff007903958\). With v37 this focuses investigation on context setup and sha1\_init, while retaining probe execution uncertainty. SHA-256 f5a5ba4b59e455df9979ca0ce4ecca9f75b22617b0e3cadb6ff0d9d325187e4a
- v41 patches sha1\_init at 0xfffffff00790398c before ldr x20,\[x22,\#0x28\], after x22 has loaded g\_crypto\_funcs. A caller filter compares x30 with the PC-relative generatePlatformUUID return address 0xfffffff00796f990; other callers replay the displaced load and resume. For the target caller, x22==0 selects a terminal six-second reset, x22\!=0 selects twelve seconds, without dereferencing the table. No reset requires investigating progress before this checkpoint or filter/probe execution. A nonzero result does not validate the table or descriptor. Branches, delay constants, caller gate disassembly, payload readback, boot digest and sdcard copy verified; SHA-256 b278e4c9dbda2ff011a8cfed9cb2fd3564a68fbd2aa01bbc377d5b4795e45828. Device report: reset after approximately six seconds, supporting g\_crypto\_funcs==0 for this generatePlatformUUID SHA-1 call
- Disassembly shows sha1\_init reads g\_crypto\_funcs at 0xfffffff0071cc128, then dereferences its SHA1 descriptor at offset 0x28 before indirect digest initialization. The original kernel file holds zero at g\_crypto\_funcs; this is only its static initial value and does not establish whether runtime registration occurred. If v40 fails, runtime table registration and descriptor access remain hypotheses to probe alongside context setup and sha1\_init execution

### 完成条件

- A boot attempt produces a readable log that is committed as evidence

### 当前范围

- No log has been captured for this port

### 下一步

- Configure a log transport and record the first boot attempt output

### 证据

按下一步操作收集证据。

## platform-expert {#platform-expert}

`device-verified`

组件: `ArmDTPlatform`.

### 硬件与依赖

- The arm64 iPadOS 18.7.12 kernelcache staged by scripts/stage-arm64-kernelcache.py
- ArmDTPlatform from components.toml \(repository https://github.com/UniXNU/ArmDTPlatform.git, revision 417ff95d6a6e8607ddea9309ec45c3bfd4a67c60\)

### 配置

- board.toml \[kernel\] archives lists component:ArmDTPlatform between the corecrypto archives and the raphael CPU/pthread archives, so archive\_plan expands its build recipe at that ordered position
- configs/raphael\_defconfig sets CONFIG\_XNU\_ARM\_DT\_PLATFORM=y; build-xnu-4k-baseline.sh reads XNU\_ARM\_DT\_PLATFORM and appends -Wl,-force\_load,$ROOT/build/armdt-platform/libArmDTPlatform.a
- configs/raphael\_defconfig sets CONFIG\_XNU\_TRUST\_CACHE\_RUNTIME=y; build-xnu-4k-baseline.sh passes it as startup.o\_CFLAGS\_ADD=-DXNU\_NATIVE\_TRUST\_CACHE and invalidates startup.o when the mode changes

### 操作步骤

- Run ./unixnu build kernel -D ../UniXNU-raphael in CI \(macos-26-intel\); the bootstrap pass leaves the compile records build-arm-driver.py needs, then build\_archives runs before the linking pass

### 开发经验

- A panic screen compiled into the kernel's own framebuffer mapping \(scripts/xnu-panic-screen.c via patch-xnu-entry-probe.py --panic-screen\) turned an invisible hang into readable text on raphael hardware; two successive screens identified two distinct stops
- First panic screen: 'image4 interface not available @kern\_trustcache.c:584' with the frame 0xfffffff007a0d8f4, the return address of bl \_load\_static\_trust\_cache in \_kernel\_bootstrap\_thread. \_trust\_cache\_runtime\_init at 0xfffffff0077a49cc loads PE\_state+0x148 and branches to \_trust\_cache\_runtime\_init.cold.3 when it is null, which is the case on a non-Apple bootloader
- Second panic screen after the diagnostic image skipped the trust-cache calls: 'Unable to find driver for this platform: "J171AP" @IOPlatformExpert.cpp:2369' at \_IOPanicPlatform::start \(0xfffffff0079711e0\), i.e. no IODTPlatformExpert subclass probed successfully for the injected device tree
- nm on the shipped formal-kernel.macho \(55,156,736 bytes, the CI prelinked candidate\) contains no ArmDTPlatform, armdt\_platform\_configured, AppleARMPE or AppleARMIO symbol, while raphael timer symbols from the device patch series are present; the native kernel is in the image but no platform expert was linked into it
- Root cause: board.toml \[kernel\] archives listed only build-corecrypto-14.py \(twice\), build-raphael-cpu.py and build-raphael-pthread.py. kernel.py archive\_plan only appends a component archive when the board lists it as component:ID, so ArmDTPlatform was never built or force-loaded despite \[components\].include naming it
- Second root cause: the raphael machine config defines BCM2837 \(patches/xnu-darwin24/machine-config-bcm2837.patch line 57\), so startup.c's '\#ifndef BCM2837' compiled the whole trust-cache runtime block out. patches/xnu/native-trust-cache-runtime.patch widens that guard to include XNU\_NATIVE\_TRUST\_CACHE, and is applied automatically by the build script's patches/xnu/\*.patch loop, but the defconfig never set CONFIG\_XNU\_TRUST\_CACHE\_RUNTIME
- The staged OS profile carries only profile.toml; cmd\_defconfig merges \[kernel\] config\_fragments \(arch and soc\) with the board defconfig and never reads profiles/os/&lt;name&gt;/configs/, so the ipados.config of the 17.7.11 profile does not apply here
- Third and decisive root cause: the soc fragment configs/sm8150.config of guowenye/UniXNU-sm8150-common \(commit f8bc872\) turns all eight switches off under 'Compilation-only bootstrap: platform consumers are not yet qualified', and cmd\_defconfig concatenates arch then soc then this defconfig, so the soc 'n' values won. The first CI attempt set only CONFIG\_XNU\_ARM\_DT\_PLATFORM and CONFIG\_XNU\_TRUST\_CACHE\_RUNTIME in the defconfig, which was enough for the trust-cache switch but left CONFIG\_XNU\_BUILD\_ARCHIVES=n inherited from the soc fragment: build\_archives\(\) returned before the loop, no component archive was built, and the log jumps from 'prepare storage headers' straight to 'prelink' with no component-\* or archive-\* line
- Because ARM\_DT\_PLATFORM was still 1 while libArmDTPlatform.a did not exist, the guard at build-xnu-4k-baseline.sh:641 \(test -f on the archive\) also means the port would not have linked it even if it had tried; the archive has to be produced first
- The first run with archives enabled also proved that board.toml named two scripts that never existed in either tree: build\_raphael-cpu.py and build-raphael-pthread.py. archive\_plan resolved them as scripts under tree/scripts and build\_archives raised 'archive-04-build-raphael-cpu: build script missing'. They were never load-bearing because XNU\_BUILD\_ARCHIVES had always been n, so the whole step was skipped and the dead references were never exercised. UniXNU's own recipes are build-cpu-desktop-kernel.py and build-libpthread-kernel.py, and the soc fragment disables both XNU\_ARMCPU and XNU\_SOURCE\_PTHREAD anyway, so the archive list is now corecrypto twice plus component:ArmDTPlatform
- With archives enabled, component-ArmDTPlatform ran and build-arm-driver.py returned without an error before the missing-script failure, so the IOPlatformExpert.cpo.json record that recipe consumes is present after the bootstrap pass
- Fourth root cause, and the reason the 06:46 run still shipped a kernel with no ArmDTPlatform despite archives running: every -Wl,-force\_load block in build-xnu-4k-baseline.sh is indented inside 'if \[ "$&\#123;XNU\_SOURCE\_CORECRYPTO14:-0&\#125;" = 1 \] &amp;&amp; \[ "$BOOTSTRAP" = 0 \]; then' at line 606, which does not close until well past the ArmDTPlatform branch at 641-646. The soc fragment also turns XNU\_SOURCE\_CORECRYPTO14 off, so the archive was built at 06:47:31-06:48:04 and then simply never linked. Restoring the arch fragment's CONFIG\_XNU\_SOURCE\_CORECRYPTO14=y admits the whole block; the corecrypto recipe that block test -f checks is build/corecrypto-2023/libcorecrypto\_kernel\_noasm-namespaced.a, which the second --namespace archive entry already produces, and XNU\_CRYPTO\_BOOTSTRAP="prelinked" still strips the duplicate provider via prng\_random.o\_CFLAGS\_ADD=-UXNU\_SOURCE\_CORECRYPTO14
- Fifth root cause, and the one behind every Unable-to-find-driver screen since archives started linking: the archive is force-loaded, so the ArmDTPlatform class and its 36 symbols are in the kernel, but gIOKernelConfigTables had no IOClass = ArmDTPlatform entry. Dumping the built table shows only RaphaelBootCpu, IOPanicPlatform and IOExclaveProxy, and a grep for the ArmDTPlatform IOClass counts 0. A bundled class with no personality never probes, so the score-0 IOPanicPlatform fallback wins and panics. Upstream patches/xnu/armvirt-platform-personality.patch registers exactly this personality \(IOProviderClass IOPlatformExpertDevice, IONameMatch device-tree, IOProbeScore 5000\), but the raphael series never carried that hunk; patches/xnu/raphael-dt-platform-personality.patch adds it after raphael-bootcpu.patch, whose RaphaelBootCpu entry it anchors on
- Kernel size alone cannot show whether a component archive linked: the 44024269099 and 44032715635 kernels are both 55,156,736 bytes with different sha256, so the file is rebuilt every run and only the symbol/string content distinguishes a linked driver from an unlinked one. 'strings \| grep ArmDTPlatform' returning 0 is the reliable check here
- Two diagnostic images used a nop in place of bl \_trust\_cache\_runtime\_init/\_load\_static\_trust\_cache and a ret at KLDBootstrap::loadSecurityExtensions. Those are probes, not the fix; the configuration changes above are the port's real answer to both stops

### 完成条件

- The kernel links libArmDTPlatform.a and keeps the trust-cache runtime path; the 44041220171 kernel carries 36 ArmDTPlatform strings including the IODTPlatformExpert meta-class and the 'required /cpus, /arm-io, /defaults or /options node is absent' diagnostic
- PE\_init\_platform reaches AMFI on the real device: the r81 screen says 'AMFI: no amfi-only-platform-code device tree node\!' instead of 'Unable to find driver for this platform'. AMFI is checked in PE\_init\_platform, which runs before IOKit matching, so this proves the device tree was loaded and the early platform path ran; it does NOT prove any platform expert matched

### 当前范围

- The platform expert still needs the device tree ArmDTPlatform::configure requires \(/cpus, /arm-io, /defaults, /options and a /chosen CHRP NVRAM proxy\); devicetree.py synthesises chosen, nvram-proxy-data, cpus, arm-io, defaults and options from dts/raphael.dts, but that arm-io must carry the real SM8150 hardware nodes for anything downstream to attach
- A driver that probes successfully is not a booted SpringBoard; display, storage, input and the userspace handoff remain unproven on this device
- The panic screen is not part of the XNU build. scripts/xnu-panic-screen.c is freestanding code that scripts/patch-nobars.py --panic-screen copies into unused kernel padding and wires panic\(\) to, so a CI-built kernel has no on-screen panic until that post-processing step runs against the CI output

### 下一步

- Flash the next CI image with the AMFI /chosen properties and read where the kernel stops
- If the next screen still names J171AP at IOPlatformExpert.cpp:2369, the personality is registered but its IONameMatch does not match the provider name; then read provider-&gt;getName\(\) at the panic and widen the match rather than the device tree

### 证据

- `source`: [Restates CONFIG\_XNU\_BUILD\_ARCHIVES=y, CONFIG\_XNU\_SOURCE\_CORECRYPTO14=y, CONFIG\_XNU\_ARM\_DT\_PLATFORM=y and CONFIG\_XNU\_TRUST\_CACHE\_RUNTIME=y; unixnu.config.parse\_config returns all four True, overriding the soc fragment's n](https://github.com/Aruvelut-123/UniXNU-raphael/blob/f16ce447b49adf258491ccc0e08212ac476ba694/configs/raphael_defconfig)
- `source`: [\[kernel\] archives is the two corecrypto recipes plus component:ArmDTPlatform; \[adt.chosen.u32\] carries the certificate/security-mode and amfi-only-platform-code properties AMFI reads off /chosen](https://github.com/Aruvelut-123/UniXNU-raphael/blob/f16ce447b49adf258491ccc0e08212ac476ba694/board.toml)
- `source`: [Revision 417ff95d6a6e8607ddea9309ec45c3bfd4a67c60 is the IODTPlatformExpert subclass matching IOProviderClass IOPlatformExpertDevice with IONameMatch device-tree](https://github.com/UniXNU/ArmDTPlatform.git)
- `device`: [On-screen panic moves from 'Unable to find driver for this platform' to 'AMFI: no amfi-only-platform-code device tree node\! @AppleMobileFileIntegrity.cpp:5307', so the platform expert now probes and PE\_init\_platform reaches AMFI](https://github.com/Aruvelut-123/UniXNU-raphael/blob/f16ce447b49adf258491ccc0e08212ac476ba694/evidence/r81-boot-record.txt)
  Command: <code>strings -a kernel.macho | grep -c ArmDTPlatform</code>. Revision: `6db5be1bbf663c0a50e0d1617c832777e77820e6`.

</div>
