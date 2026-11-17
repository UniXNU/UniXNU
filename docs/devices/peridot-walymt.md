# Redmi Turbo 3 / POCO F6 \(WaLymT\)

[WaLymT/UniXNU-peridot](https://github.com/WaLymT/UniXNU-peridot)

<div v-pre>

Redmi Turbo 3 / POCO F6 on Qualcomm SM8635 \(cliffs\). The board selects the iPadOS 17.7.11 profile and the SM8635 shared support. As of 2026-11-15 the kernel mounts the real APFS RestoreRamDisk container from UFS userdata as a memory-device root, runs Apple signed launchd/restored\_external under AMFI with the ramdisk trust cache, and publishes the same window as a writable block device; the install-to-disk path \(restore/asr\) and the plain block-device root are still open.

Source record: [porting.toml](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/porting.toml), `2158177f8670f7f7fc2d35db51ab10086b89ca1d`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `implemented` |
| [Firmware and boot](#firmware) | `device-verified` |
| [CPU and interrupts](#cpu) | `device-verified` |
| [Memory and DMA](#memory) | `device-verified` |
| [Storage and root](#storage) | `device-verified` |
| [Display](#display) | `device-verified` |
| [Input](#input) | `planned` |
| [GPU](#gpu) | `implemented` |
| [Network](#network) | `planned` |
| [usb](#usb) | `planned` |
| [cellular](#cellular) | `planned` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `planned` |
| [Image assembly](#packaging) | `host-verified` |
| [Diagnostics](#diagnostics) | `device-verified` |
| [userspace](#userspace) | `device-verified` |

## Configuration {#configuration}

`implemented`

### Hardware and dependencies

- SM8635 shared support, the iPadOS 17.7.11 profile, this board's defconfig and the pinned component sources.

### Configuration

- board.soc = SM8635; board.soc\_source = sm8635; board.os\_profile = ipados-17.7.11-21H461.
- The board selects only ArmDTPlatform, ArmCpu, SoftwareAES, XnuPrelink and DarwinBoot; storage, display and input components are added when their board recipes exist.

### Procedure

- Read https://unixnu.com/porting/device-repository and https://unixnu.com/porting/records.
- Run ./unixnu defconfig peridot\_defconfig -D ../UniXNU-peridot from the UniXNU checkout.
- Run ./unixnu status --json -D ../UniXNU-peridot and review profiles, components, source pins and patch order.

### Development findings

- Tables merge in ARM64, SoC, OS and device order. Arrays replace inherited selections, so every required component and fragment is listed explicitly.
- The board inherits \[ipsw\] and \[kernel.prelink\] from the OS profile. Overriding either in board.toml would desynchronise the kernelcache pin from the components it was qualified against.
- Public snapshot 2026-11-17: the Adreno735 component is no longer selected in board.toml because its GPU firmware is vendor data and is not redistributed; the driver and kit sources remain for later work \(docs/proprietary.md\).

### Completion criteria

- All source pins resolve, status shows the intended component set and patch order, and the porting record check passes.

### Current limits

- The SM8635 shared repository is new and unverified; its addresses are copied from the board's stock DTS.

### Next action

- Resolve the SM8635 source pin and run status once the shared repository is published.

### Evidence

- `source`: [Board identity, profile selection, component list, firmware and payload inputs.](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/board.toml)

## Firmware and boot {#firmware}

`device-verified`

Components: `DarwinBoot`.

### Hardware and dependencies

- Mu-Silicium Platforms/Xiaomi/peridotPkg, its Resources/Configs/peridot.toml, the stock firmware DTB and the PSCI SMC interface.

### Configuration

- firmware.dsc = Platforms/Xiaomi/peridotPkg/peridot.dsc; firmware.config = peridot; firmware.fd = Build/peridotPkg/&\#123;target&\#125;\_CLANGPDB/FV/SILICIUM\_UEFI.fd.
- The firmware DSC and FDF must embed UniXNU, UniXNUDxe, DarwinBoot, UniXNURamDiskDxe, DiskIoDxe and FAT support.
- bootimg.image pins header\_version = 0 and pagesize = 4096; the device rejects every signed-header variant.

### Procedure

- Build the stock peridotPkg firmware first and boot it with fastboot boot to verify display, side buttons and block devices.
- Then run ./unixnu build firmware -D ../UniXNU-peridot --uefi ../Mu-Silicium and boot the resulting image.

### Development findings

- peridotPkg already loads at 0xA7100000 with size 0x300000 and reports display, internal storage, side buttons, USB device mode and mass storage as working in the Mu-Silicium status page.
- Mu-Silicium labels peridot Inactive: the platform has no active maintainer, so any firmware fault has to be fixed here.
- Measured on the device: the RELEASE build produces a 3 MiB SILICIUM\_UEFI.fd and the Silicium UEFI menu appears on the panel.
- Header v4, v4 with os\_version and v1 are all rejected with Failed to load/authenticate boot image: Invalid Parameter; only header v0 with pagesize 4096 boots.
- With no bootable entry the menu returns to the bootloader after a while, and repeated failed fastboot boot attempts make the bootloader mark the active slot unbootable until fastboot --set-active clears it.
- Public snapshot: the Adreno735 archive entry is removed from board.toml together with the component, so the firmware and payload builds no longer pull the vendor GPU firmware placeholder.

### Completion criteria

- The firmware boots, shows the UniXNU menu, publishes the payload RAM disk and hands the framebuffer to DarwinBoot.

### Current limits

- The peridot firmware configuration is unmaintained upstream; SM8635 and SM7675 share the Palawan platform package.
- The firmware volume has no bootable entry yet, so the menu is the end of the current chain.

### Next action

- Add UniXNU, DarwinBoot and UniXNURamDiskDxe to the firmware volume so the menu has a boot option.

### Evidence

- `source`: [FD base and size, framebuffer geometry, SM8635 platform selection.](https://github.com/Project-Silicium/Mu-Silicium/blob/main/Platforms/Xiaomi/peridotPkg/peridot.dsc)
- `device`: [Silicium UEFI menu appears on the panel when booted with header v0 and pagesize 4096.](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/docs/uefi-bringup.md)
  Command: <code>fastboot boot Mu-peridot.img</code>. Revision: `8b9acafab284a2f0d2ad91cf4c4dac204236e75b`.

## CPU and interrupts {#cpu}

`device-verified`

Components: `ArmCpu`, `ArmDTPlatform`.

### Hardware and dependencies

- Eight cores with MPIDR 0x000 through 0x700, GIC distributor at 0x17100000, redistributors at 0x17180000 with 0x40000 stride, 19.2 MHz timer and PSCI over SMC.

### Configuration

- dts/peridot.dts includes sm8635.dtsi from the SoC source.
- cpu\_regs lists every MPIDR in the ADT; clusters are A520 \(E\), A720 \(P\) and X4 \(P\).

### Procedure

- Compile the board DTS and inspect enabled CPUs, GIC ranges and timer properties in the ADT.
- Record per-CPU entry, timer interrupts and IPI delivery for each core.

### Development findings

- The stock DTS describes every core as qcom,kryo; the dtsi uses the ARM generic compatible strings so the platform expert builds CPU nubs.
- GIC and redistributor ranges match SM8550 exactly, so the SoC dtsi can keep that layout.

### Completion criteria

- Every enabled CPU reaches its entry checkpoint and timer and IPI handling work on each core.

### Current limits

- CPU frequency policy is a board input and is not implemented.

### Next action

- Verify the redistributor count against GICR\_TYPER on the device.
- Add CPU idle/power-off once the install path exists.

### Evidence

- `source`: [CPU MPIDR values, GIC ranges and redistributor stride.](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/dts/vendor/peridot-stock.dts)
- `device`: [SMP boot on all 8 cores \(MAX\_CPUS 8 / MAX\_CPU\_CLUSTERS 2 fixed the topology-parser stall\); Apple launchd reaches userspace \(HANDOFF-2026-11-15.md section 7\).](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/configs/peridot_defconfig)
  Command: <code>fastboot boot out/Mu-peridot-p354.img and out/Mu-peridot-p359.img with kernel_args -v native-ufs-probe=18 sheng-pmgr=2 amfi_get_out_of_my_way=1 peridot-allow-unsigned-root=1 offline-apfs-load=1 rd=md1 amfi-allows-trust-cache-load=1 amfi_allow_any_signature=1 -restore</code>. Revision: `5aba75132ed14960f3205fa810aaf64cca67c982`.

## Memory and DMA {#memory}

`device-verified`

### Hardware and dependencies

- DRAM at 0x80000000, 12 GiB on this unit \(ddr\_size = 0x0c\). UEFI runs inside 0xA7100000 to 0xA7400000; the display reservation is 0xE3940000 with size 0x2B00000.

### Configuration

- device\_tree.source = device:dts/peridot.dts with include\_dirs = \[soc:dts\].
- payload.dram\_size = 0x80000000 and payload.adt.owned\_memory\_size = 0x100000000 are the values the working images boot with; they are smaller than the 12 GiB physical DRAM because the bring-up only needs a contiguous owned window.

### Procedure

- Compare the firmware memory map, the DTS memory and reserved-memory nodes and the ADT memory-map entries before the first boot.
- Check every DMA range against the controller address width and SMMU mapping before enabling a driver.

### Development findings

- DRAM is 12 GiB on this unit but the ADT publishes a smaller owned window; the apps SMMU sits at 0x15000000 and the UFS DMA stream 0x60 is bypassed through it.
- 2026-11-15: a 176 MiB wired buffer for the APFS container is allocated and addressed by the UFS DMA engine, and the same path writes back to UFS \(p356\).
- Public snapshot: board.toml only drops the Adreno735 selection; the memory map and ADT values are unchanged.

### Completion criteria

- Every handoff region is accounted for and each DMA engine reaches its range with the documented cache policy.

### Current limits

- The RAM size varies by SKU and the ADT owned window is smaller than physical DRAM; the 184 MiB APFS container is allocated as wired memory at boot.

### Next action

- Read the firmware memory map and record it here.
- Size the ADT owned window from the real memory map before any large install target is mapped.

### Evidence

- `device`: [The 184,549,376-byte APFS container is read into a 176 MiB wired buffer and registered with mdevadd; the same SMMU/DMA path writes back \(p356 match=1 restore=0/0 ok=1\).](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/drivers/ShengUfs/NativeUfs.cpp)
  Command: <code>fastboot boot out/Mu-peridot-p354.img and out/Mu-peridot-p359.img with kernel_args -v native-ufs-probe=18 sheng-pmgr=2 amfi_get_out_of_my_way=1 peridot-allow-unsigned-root=1 offline-apfs-load=1 rd=md1 amfi-allows-trust-cache-load=1 amfi_allow_any_signature=1 -restore (probe 33 write test)</code>. Revision: `5aba75132ed14960f3205fa810aaf64cca67c982`.

## Storage and root {#storage}

`device-verified`

Components: `ShengUfs`, `VirtioMmioBlock`, `VerifiedRoot`.

### Hardware and dependencies

- UFS host at 0x1d84000 with size 0x3000, ICE at 0x1d88000, ICE hardware key manager at 0x1d90000, MCQ registers, PHY at 0x1d80000 and the apps SMMU stream 0x60.

### Configuration

- ShengUfs is vendored under drivers/ShengUfs and declared as a local source in feeds.toml, so it can be adapted for cliffs and the build survives an unreachable github.com.
- Root path \(2026-11-15\): native-ufs-probe=18 reads the 184,549,376-byte RestoreRamDisk APFS container from the start of userdata into wired memory, registers it as md1 and leaves it as rootdev; rd=md1 plus patches/xnu/peridot-rd-wait.patch mount it through the APFS restore/ramdisk branch, and the same window is published as a writable IOBlockStorageDevice \(disk0/disk1/disk1s1\).
- peridot-apfs-register.patch re-registers the prelinked apfs vfs in front of mockfs; peridot-rootauth.patch lets peridot-allow-unsigned-root=1 replace the missing volume seal.

### Procedure

- Read the GPT and confirm the userdata entry before writing any board value.
- After WSL access is available, run the peridot UFS binding wrapper on the active tree and verify its archive and current kernel.json; then boot with native-ufs-probe=2 and =10 for read-only transport/GPT checks before any write.

### Development findings

- The host and PHY addresses match SM8550, but the PHY compatible is qcom,ufs-phy-qmp-v4-cliffs and the controller adds ICE and MCQ regions the SM8550 implementation does not use.
- Fix A from audit/2026-11-15-enotblk.md works: the UFS window is published as a bdevsw disk, claimed and adopted inside the rd= wait loop, and APFS mounts the container through its ramdisk restore branch from the real UFS disk.
- The bdevsw path needs the page-cache buf\_map strategy, a real write path \(WRITE\(10\)+FUA through ufsWriteWindow with counts in 512-byte blocks\) and the disk ioctl contract \(DKIOCGETFEATURES/ISSOLIDSTATE/SYNCHRONIZE plus max-transfer/segment\); Apple newfs\_apfs then formats the 8 GiB install target \(p381\).
- The iPadOS System container extracted from the IPSW OS image \(6,077,546,496 bytes, NXSB, block\_count 1483776\) can be staged into userdata through a fastboot sparse image and mounted as root: its /sbin/launchd is exec-ed from UFS \(p383\). dyld then needs the shared cache, which iOS 16+ keeps in a cryptex \(Cryptex1,SystemOS\).
- Public snapshot: board.toml only drops the Adreno735 selection; the UFS/APFS root path is unchanged.

### Completion criteria

- SCSI capacity, GPT and known blocks are correct, then the configured root volume mounts and launchd starts.

### Current limits

- The root is mounted through APFS's restore/ramdisk branch and is read-only; a writable system volume needs the mount flags opened or a native block-device root.
- The staged iPadOS System container is bootable far enough to exec launchd but cannot run it without the dyld shared cache / cryptex content; the restore container remains at userdata offset 0 and the OS container at offset 1 GiB.
- The bdevsw strategy is serialised by one lock; the screen remains the only diagnostic channel.

### Next action

- The official SHNGROOT userdata install flow is verified on hardware: userdata-root.img \(9,382,658,048 bytes\) was flashed \(12 chunks, 226 s\) and Mu-peridot-p418.img \(PROBE=55\) parsed the SHNGROOT manifest, skipped the OS window GPT, claimed the Apple\_APFS partition as root and started launchd from /sbin/launchd; only the dyld shared cache \(SystemOS cryptex\) is still missing. Next: probe 56 = SHNGROOT OS root + SystemOS \(/dev/nu1\) + the 12 GiB staging volume \(/dev/nu2\), then the probe=5 file-vnode graft flow \(mount staging, copy cryptex.img, graft\) to provide the cache.
- Keep the ad-hoc probes \(native-ufs-probe 18/40/45\) available for bisection; the 8 GiB staging container at 12 GiB survived the 9.4 GB userdata flash.

### Evidence

- `host`: [NativeUfs.cpp builds to a 473 KB object with 634 symbols, libShengUfs.a is produced, and -force\_load reaches the kernel link line.](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/drivers/ShengUfs/NativeUfs.cpp)
  Command: <code>cd &lt;unixnu-checkout&gt; &amp;&amp; ./unixnu defconfig peridot_defconfig -D ../UniXNU-peridot &amp;&amp; ./unixnu kernel -D ../UniXNU-peridot</code>. Revision: `2e767bc7aa14e0dfaec774cfe73d3180fcb74dfd`.
- `host`: [With CONFIG\_XNU\_NATIVE\_UFS=y the link stops on IOBlockStorageDevice \(external IOStorageFamily kext\), verified\_root\_key/policies \(VerifiedRoot\) and boot\_progress\_poll; the option is back to unset so the tree still builds.](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/configs/peridot_defconfig)
  Command: <code>cd &lt;unixnu-checkout&gt; &amp;&amp; UNIXNU_KERNELCACHE=$PWD/out/ipsw/21H461/kernelcache.decompressed ./unixnu kernel -D ../UniXNU-peridot</code>. Revision: `2e767bc7aa14e0dfaec774cfe73d3180fcb74dfd`.
- `source`: [ufshc@1d84000 with reg size 0x3000, iommus &lt;&amp;apps\_smmu 0x60 0&gt; and GCC clock-controller@100000: the three constants the SM8550 transport assumes all match.](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/dts/vendor/peridot-stock.dts)
- `device`: [The vendored SM8550 transport matched peridot ufshc and ran its read-only inspection on device: the six GCC UFS PHY clock branches \(axi, ahb, uniphy, txs, rxs, aux\) all read 0x11, so fastboot leaves the link clocked. The gdsc values printed as 0xff22227ff890000, which does not look like a power-domain status register, so the SM8550 GCC offsets are probably wrong for cliffs and must be re-derived before anything is written.](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/drivers/ShengUfs/NativeUfs.cpp)
  Command: <code>fastboot boot out/Mu-peridot-ufsprobe.img with kernel_args -v native-ufs-probe=2</code>. Revision: `2e767bc7aa14e0dfaec774cfe73d3180fcb74dfd`.
- `host`: [Generated a 9,382,658,048-byte SHNGROOT v1 image with OS and SystemOS windows. Both IPSW members matched the OS profile SHA-256 pins; independent header, bounds, per-window and full-image SHA-256 checks passed. Capacity used the measured 0x78587FB000-byte partition size only; physical first/last GPT LBA remain unset, the image was not flashed, and hardware boot was not tested.](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/docs/boot-bisection.md)
  Command: <code>python .tmp/build_userdata_image.py --ipsw &lt;local iPad_Pro_HFR_17.7.11_21H461_Restore.ipsw&gt;; python .tmp/verify_userdata_image.py &lt;generated userdata-root.img&gt;</code>. Revision: `02a562d39c4cbd160633d3ab611010a994d54848`.
- `device`: [Cross-container reads at offsets 0, 4 MiB, 64 MiB and 1 GiB all returned status 0, so the transport serves the whole window. Both APFS entry points fail: apfs\_vfsop\_mountroot and a direct VFS\_MOUNT gated by peridot-apfs-vfsmount=1 both return ENOENT at apfs\_vfsop\_mount:2479. Cause: the flashed userdata image is the update payload, not an installed system. Container 4096 x 1483776 \(6,077,546,496 bytes\) with UUID 50f8a67f-afc1-4aaf-...; volume 04769d26-... named DawnUpdate21H461.J120J121J207J208OS carries no root snapshot \(com.apple.os.update absent\) and no role, so it cannot serve as a root volume.](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/drivers/ShengUfs/NativeUfs.cpp)
  Command: <code>fastboot boot out/Mu-peridot-p115.img with kernel_args -v native-ufs-probe=17 native-ufs-mountroot=1 peridot-apfs-vfsmount=1</code>. Revision: `283feb0deb1ed0c4909ff4e664f0113e3d9acbff`.
- `device`: [p368 \(and the p362-p367 series\): APFS container mounted from the real UFS bdevsw disk, /sbin/launchd loaded through decmpfs from that root, real launchd+restored\_external running \(out/screen-p368-ufs-root-real-launchd.jpg\).](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/patches/xnu/peridot-rd-wait.patch)
  Command: <code>fastboot boot out/Mu-peridot-p368.img with kernel_args -v native-ufs-probe=36 sheng-pmgr=2 amfi_get_out_of_my_way=1 peridot-allow-unsigned-root=1 offline-apfs-load=1 rd=md1 amfi-allows-trust-cache-load=1 amfi_allow_any_signature=1 -restore</code>. Revision: `23770733a454667dd844787f8fe40fb8b13219cf`.
- `device`: [p361 probe 34: IOBlockStorageDevice write path self test ok=1 \(devio block=64 read=0 write=0 reread=0 match=1 restore=0 verify=0 ok=1, out/screen-p361-probe34-devio-ok.jpg\).](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/drivers/ShengUfs/NativeUfs.cpp)
  Command: <code>fastboot boot out/Mu-peridot-p368.img with kernel_args -v native-ufs-probe=36 sheng-pmgr=2 amfi_get_out_of_my_way=1 peridot-allow-unsigned-root=1 offline-apfs-load=1 rd=md1 amfi-allows-trust-cache-load=1 amfi_allow_any_signature=1 -restore</code>. Revision: `23770733a454667dd844787f8fe40fb8b13219cf`.
- `device`: [p369: InstallTarget \(8 GiB at userdata+1 GiB\) published and writable through IOBlockStorageDevice \(page=0/0/0/0, 4 MiB write+verify+restore in 8 ms\); rootflags=0x1480d001 \(read-only root\). out/screen-p369-install-target-ok.jpg](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/drivers/ShengUfs/NativeUfs.cpp)
  Command: <code>fastboot boot out/Mu-peridot-p369.img with kernel_args -v native-ufs-probe=37 ... rd=md1 -restore</code>. Revision: `3d189e6c9cc382663f59b8b7c583fdaef3ff556e`.
- `device`: [p370: container copied to the install target and verified \(176 MiB, 1408 chunks, 570 ms\). p371: booted from the installed target, real launchd/restored\_external running. out/screen-p370-install-copy-ok.jpg, out/screen-p371-installed-target-real-launchd.jpg](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/patches/xnu/peridot-bdevsw-root.patch)
  Command: <code>fastboot boot out/Mu-peridot-p370.img / out/Mu-peridot-p371.img with native-ufs-probe=38 / 39</code>. Revision: `3d189e6c9cc382663f59b8b7c583fdaef3ff556e`.
- `device`: [The iPadOS System APFS container \(6,077,546,496 B, NXSB, block\_count 1483776\) mounts from UFS and /sbin/launchd is exec-ed; dyld stops at /usr/lib/libSystem.B.dylib \(no dyld cache\). out/screen-p383-os-root-launchd-dyld.jpg](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/tools/udif-extract.py)
  Command: <code>fastboot flash userdata userdata-os.sparse.img (5.9 GiB sparse, 124.8 s); fastboot boot out/Mu-peridot-p383.img (native-ufs-probe=43)</code>. Revision: `d940feca1017ef8497f168d7e1b0937e85e27947`.
- `host`: [OS image extracts to a 6,077,546,496-byte APFS container \(NXSB, 1483776 blocks\) whose launchd is exec-ed when staged as root \(p383\); Cryptex1,SystemOS is a raw 3,303,014,400-byte APFS container \(volume DawnUpdate21H461...SystemCryptex\) containing dyld\_v1 arm64 shared cache. The kernel graft path is syscall 549 graftdmg + VNOP\_IOCTL\(FSIOC\_GRAFT\_FS\).](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/tools/udif-extract.py)
  Command: <code>udif-extract.py 044-76040-038.dmg -&gt; &lt;work&gt;/os-container.img; inspect 044-76034-038.dmg (raw APFS)</code>. Revision: `d940feca1017ef8497f168d7e1b0937e85e27947`.
- `device`: [p384: path probe shows /sbin/launchd and /usr/lib on the mounted System volume but /System/Library/Caches/com.apple.dyld and /System/Cryptexes/OS are ENOENT. p385/p386: kernel cryptex graft called before load\_init\_program; APFS FSIOC\_GRAFT\_FS returns EINVAL \(graft failed: 22\). Screens: out/screen-p384-cryptex-paths.jpg, out/screen-p385-launchd-shared-region-fail.jpg, out/screen-p386-graft-einval.jpg](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/patches/xnu/peridot-cryptex-graft.patch)
  Command: <code>fastboot flash userdata userdata-os.sparse.img (restore@0, OS@1GiB, cryptex@8GiB, 9.1 GiB sparse); fastboot boot out/Mu-peridot-p38&#123;4,5,6&#125;.img</code>. Revision: `9e6b9464d6b03a451827631b9484954ff958d99e`.
- `device`: [kernel\_mount\("apfs"\) attempts from bsd\_init fail before launchd: noargs=22 EINVAL, kernel char\*\* device path=14 EFAULT \(APFS wants user-space mount args\), graft=22 EINVAL. out/screen-p387-apfs-mount-errno.jpg](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/patches/xnu/peridot-cryptex-graft.patch)
  Command: <code>fastboot boot out/Mu-peridot-p387.img (native-ufs-probe=45, SystemOS cryptex at userdata+8GiB)</code>. Revision: `542e3f06028389798f9ef2f2dd058038823e59ca`.
- `device`: [p388 direct mount\(\) = EPERM \(MACF\); p389 kernel\_mount with user-space args = EINVAL; p390/p391 field variants all EINVAL; p392 restore-root init override /apfs.fs/mount\_apfs = ENOENT; p395 root probe ld=0 dyld=0 fs=2 mp=2 smp=2 ump=2 \(184 MiB restore container has launchd/dyld but no apfs.fs tools\). Screens: out/screen-p388-userspace-mount-eperm.jpg … out/screen-p395-root-launchd-dyld-only.jpg](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/patches/xnu/peridot-cryptex-graft.patch)
  Command: <code>kernel builds p388-p395; fastboot boot out/Mu-peridot-p39&#123;1,2,5&#125;.img with PROBE=45/46</code>. Revision: `8d5ad00b916e99efd22d753e13296bda02acd259`.
- `device`: [p396 mount\_apfs runs as pid 1 and calls mount\(2\); APFS cannot read /dev/nu1 superblock because nu1 lacked a bounce buffer. p397 after the fix APFS scans the container \(spaceman\_scan\_free\_blocks\) but apfs\_vfsop\_mount:2550 refuses to mount the sealed cryptex volume; mount\_apfs exits 65. p400 graft retry with the block-device vnode instead panics \(nested panic at pe\_init.c:778, far=0x598\). Screens: out/screen-p396-userland-mount-apfs-einval-read.jpg, out/screen-p397-apfs-spaceman-scan-then-unable.jpg, out/screen-p400-nested-panic-graft-only.jpg](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/drivers/ShengUfs/NativeUfs.cpp)
  Command: <code>kernel builds p396-p400; fastboot boot out/Mu-peridot-p39&#123;6,7&#125;.img (PROBE=46 + peridot-init-path=/System/Library/Filesystems/apfs.fs/mount_apfs) and p400 (PROBE=45 + peridot-cryptex-probe=3)</code>. Revision: `2ca8baed6bcd67e4218842ee24135af888a644e4`.
- `device`: [p401: newfs\_apfs formatted the 8 GiB container at userdata+12 GiB \(verify thread: found=1 off=32\). p402/p403: the file-graft test builds /cryptex.img and calls the graft on a file vnode, but vnode\_open returns ENOENT because mountroot did not root from the empty staging volume - it fell back to the restore ramdisk root \(e2/e3 probes show /usr/lib exists, so root is not the new volume\). Infrastructure for absolute reads, file creation and vn\_rdwr copies is in place. out/screen-p401-staging-volume-formatted.jpg, out/screen-p402-file-graft-open-enoent.jpg, out/screen-p403-file-graft-open-enoent-again.jpg](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/drivers/ShengUfs/NativeUfs.cpp)
  Command: <code>fastboot boot out/Mu-peridot-p401.img (PROBE=49 + newfs_apfs /dev/nu0), Mu-peridot-p402/p403.img (PROBE=51 + peridot-cryptex-probe=4)</code>. Revision: `bbb5ee8efe94b62066eb63ac32cb8a7b05b368b3`.
- `device`: [p407 captured the real mount\_apfs APFS argument blob: after the fspec pointer, u64 mount flags=0, u16=1 and zeros. p406/p408 mounting the writable staging container at /System/Library/Caches from kernel\_mount still returns EINVAL, so the regular mount path difference \(kernel\_mount vs mount\(2\)\) or the mount context must be investigated; whether mount\_apfs itself can mount /dev/nu2 has not been verified yet. out/screen-p406-secondary-mount-einval.jpg, out/screen-p407-mountargs-dump.jpg, out/screen-p408-file-graft2-einval.jpg](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/drivers/ShengUfs/NativeUfs.cpp)
  Command: <code>fastboot boot out/Mu-peridot-p406.img (PROBE=52 + probe=5), Mu-peridot-p407.img (PROBE=53 + mount_apfs /dev/nu2 /usr), Mu-peridot-p408.img</code>. Revision: `103c60c0fbb943a4f2700a69d2d0c982298f048e`.
- `device`: [p411: mount\_apfs /dev/nu2 returns err=2 \(ENOENT\) - the container formatted by newfs\_apfs has no volume to mount. p412: newfs\_apfs -v stage /dev/nu0 did not format \(verify thread found=0\), so the volume creation options still need work \(init-args limited to 3 arguments\). out/screen-p411-mount-result-enoent.jpg, out/screen-p412-newfs-with-volume-found0.jpg](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/drivers/ShengUfs/NativeUfs.cpp)
  Command: <code>fastboot boot out/Mu-peridot-p41&#123;0,1,2&#125;.img (PROBE=53 restore root + mount_apfs /dev/nu2 /usr; PROBE=49 + newfs_apfs -v stage /dev/nu0)</code>. Revision: `e937fc26cd81e56ded905c854f88bc41ddd63cbf`.
- `device`: [p415: newfs\_apfs -v stage -s 6g exits 64 \(EX\_USAGE\) and leaves found=0. p416: newfs\_apfs -v stage /dev/nu0 succeeds - NATIVE\_UFS init verify thread reports found=1 off=32, so the staging container now has volume stage and should be mountable. out/screen-p415-newfs-usage-exit64.jpg, out/screen-p416-newfs-volume-ok.jpg](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/patches/xnu/peridot-init-args.patch)
  Command: <code>fastboot boot out/Mu-peridot-p415.img (PROBE=49 + newfs_apfs -v stage -s 6g /dev/nu0), Mu-peridot-p416.img (PROBE=49 + newfs_apfs -v stage /dev/nu0)</code>. Revision: `fe15faa4aac8bbd85c4041602d9cc6708422be5f`.
- `host`: [Built userdata-root.img 9,382,658,048 bytes: SHNGROOT v1 manifest with two windows, manifest SHA verified, OS window 6,077,580,800 B at 0x100000 \(GPT, APFS partition 6,077,546,496 B at 0x104400, NXSB at +0x20\), SystemOS window 3,303,014,400 B at 0x16a600000 \(raw APFS, NXSB at +0x20\); root volume UUID 04769D26-2CA0-4825-B443-E2E5F88300F2 found in the OS window.](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/drivers/ShengUfs/NativeUfs.cpp)
  Command: <code>./unixnu build userdata -D peridot/UniXNU-peridot --ipsw &lt;work&gt;/ipsw.ipsw</code>. Revision: `f2cddd73ffdd5fc05811f5d7e79171bf3d2aea6f`.
- `device`: [Hardware verified: the SHNGROOT image flashed and Mu-peridot-p418.img mounted the OS window as root - launchd was executed from &lt;4B525992-8C69-315E-A51A-CC9433E45B51&gt; /sbin/launchd - failing only on the known missing dyld shared cache \(SystemOS cryptex not grafted yet\). Evidence: out/screen-p418-shngroot-os-root-launchd.jpg.](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/drivers/ShengUfs/NativeUfs.cpp)
  Command: <code>fastboot flash userdata userdata-root.img (9,382,658,048 bytes, 226 s) + fastboot boot out/Mu-peridot-p418.img (PROBE=55)</code>. Revision: `f2cddd73ffdd5fc05811f5d7e79171bf3d2aea6f`.
- `device`: [SHNGROOT userdata install flow verified on hardware: launchd runs from the OS window of the official install image; the remaining failure is the dyld shared cache from the SystemOS cryptex. Screen: out/screen-p418-shngroot-os-root-launchd.jpg](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/drivers/ShengUfs/NativeUfs.cpp)
  Command: <code>fastboot flash userdata out/peridot/ipados-17.7.11-21H461/peridot/userdata/userdata-root.img; fastboot boot out/Mu-peridot-p418.img (PROBE=55)</code>. Revision: `f2cddd73ffdd5fc05811f5d7e79171bf3d2aea6f`.

## Display {#display}

`device-verified`

### Hardware and dependencies

- Framebuffer 1220 by 2712 at 32 bits per pixel, published by UEFI GOP and reserved at 0xE3940000 with size 0x2B00000.

### Configuration

- bootimg.dtb\_node adds /reserved-memory/splash\_region with label cont\_splash\_region for the boot image.
- adt.product.string overrides artwork-display-gamut to sRGB for the 8-bit GOP path.

### Procedure

- Confirm the panel is initialised by the bootloader and that GOP reports the expected geometry.
- Select GopFramebuffer once the kernel reaches the display checkpoint.

### Development findings

- The stock DTS contains three panel variants \(n16t\_42\_02\_0a, n16t\_36\_0f\_0b and n16t\_42\_0a\_0c\), but the UniXNU path drives the UEFI framebuffer and does not program the panel.
- The UEFI framebuffer geometry matches the panel resolution, so no scaling step is needed.
- Public snapshot: board.toml only drops the Adreno735 selection; the framebuffer path is unchanged.

### Completion criteria

- A known frame appears with correct geometry and colours, then userland presentation works.

### Current limits

- Display depends on the bootloader having trained the panel; XNU does not program the panel and there is no userland compositor.

### Next action

- Record the reported GOP geometry on the device.
- Keep the framebuffer console as the only evidence channel until a compositor exists.

### Evidence

- `device`: [The UEFI GOP framebuffer console shows kernel and launchd output on the panel \(out/screen-p354-real-launchd.jpg, out/screen-p359-writable-media-stable.jpg\).](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/board.toml)
  Command: <code>fastboot boot out/Mu-peridot-p354.img and out/Mu-peridot-p359.img with kernel_args -v native-ufs-probe=18 sheng-pmgr=2 amfi_get_out_of_my_way=1 peridot-allow-unsigned-root=1 offline-apfs-load=1 rd=md1 amfi-allows-trust-cache-load=1 amfi_allow_any_signature=1 -restore</code>. Revision: `5aba75132ed14960f3205fa810aaf64cca67c982`.

## Input {#input}

`planned`

### Hardware and dependencies

- Focaltech N16T-3683G touch controller on SPI, reported by the stock DTS as xiaomi,peridot-spi and focaltech,n16t-3683g-spi. Side buttons are separate GPIO keys.

### Configuration

- adt.buttons declares hold, voldown and volup without a menu button and sets home-button-type = 2 for gesture navigation.

### Procedure

- Read the touch controller identification from the stock firmware to confirm the panel and touch pairing on this unit.
- Implement a SPI transport and a focaltech report decoder, then publish them through the HID input path.

### Development findings

- HakiOS does drive FocalTech: its hakios.goodix.c handles both Goodix GT9916 and FocalTech FT3680 with a 116448-byte firmware blob in hakios.focaltech\_fw.h, and multitouch works on the POCO X5 Pro \(redwood\).
- The stock DTS also carries a goodix node, so units may differ in touch supplier.
- The low-risk path stays inside UniXNU: ShengHidInput and QcomGeniSpi are proven on sheng, so only the focaltech report decoder has to be written.
- Public snapshot: board.toml only drops the Adreno735 selection; no input wiring changed.

### Completion criteria

- Touch reports reach the HID stack and drive the lock screen and SpringBoard.

### Current limits

- No input driver is selected beyond the ADT button declaration.

### Next action

- Confirm the controller on this unit \(focaltech,n16t-3683g-spi\), then write the focaltech decoder on top of ShengHidInput and QcomGeniSpi.

### Evidence

Collect evidence using the next action.

## GPU {#gpu}

`implemented`

Components: `Sm8635Platform`, `Adreno735`, `AdrenoPM4`, `AdrenoFirmware`, `ArmSmmu4K`.

### Hardware and dependencies

- Adreno 735, chip id 0x43030b00, gen7-11-0, at 0x3d00000 with GMU at 0x3d68000 and GPU SMMU at 0x3da0000.

### Configuration

- peridot.dts enables the gpu, gmu and gpu\_smmu nodes; sm8635.dtsi keeps them disabled for every other board.
- Adreno735 is selected with Sm8635Platform: component:Adreno735 builds build/adreno735/libAdreno735.a, and build-adreno735-kits.py appends the kit and dependency-kit objects to it.
- build-xnu-4k-baseline.sh force-loads the archive, and the Mach-O constructor in NativeAdreno735.cpp runs stage 1-2 before bsd\_init because this kernel installs no personality for built-in drivers.

### Procedure

- Confirm the GPU chip id from the stock DT and the palawan catalog before selecting an implementation.
- Verify one stage per boot with a panic marker: the board has no UART, so the screen is the only evidence.

### Development findings

- The GPU is a different part from sheng's: chip id 0x43030b00 against 0x43050a01, and the GMU compatible is qcom,gen7-gmu rather than qcom,adreno-gmu-740.1.
- The GPU SMMU and its register window keep the SM8550 addresses.
- The RSCC window is the second range of the kgsl node at 0x3d50000 and the misc block is named cx\_misc; SM8550 calls the same block cx\_mem.
- scripts/prepare-sm8635-gmu.py derives the five windows, the chip id and the 0x68000 core-to-gpu delta from the compiled DTB, then verifies the pinned v6.16 sources and extracts the 19-write RSC/PDC sequence along the non-A740 branch.
- The non-A740 sequence is distinguishable from sheng's: the sequencer lands at word 0x180 instead of the A740 word 0x154, the TCS value is 0x80000000 instead of 0x80000021, and pdc\_in\_aop skips the PDC microcode block, leaving only the two setup\_pdc writes.
- Upstream v6.16 has no 0x43030b00 entry in a6xx\_catalog.c, and msm\_kgsl.ko carries neither the chip id nor an Adreno735 string \(the model and chip id come from the device tree\), so the GMU chip id is derived from the GEN7\_x\_y encoding used by commit 2c4c53f: 0x070b0000, patch level 0 because qcom,patchid is absent.
- ShengGmuSource.h is now generated: 36 register constants, both fatal masks, the 80680-byte firmware hash and the 19-write non-A740 RSC table.
- The generator now also emits ShengGpuSmmuSource.h \(0x3da0000, streams &\#123;0,2&\#125;, GMU SID 5\) and ShengGmuCommandDbSource.h \(0x81c60000, 131072 bytes\) from the compiled DTB.
- The three kit sources and the Adreno735 skeleton compile against the kernel's own .o.json recipes: objects 47528, 9072, 21712 and 170976 bytes.
- Catalog entries Sm8635Platform and Adreno735 exist and unixnu status resolves with them; feeds.toml vendors drivers/Adreno735 locally like ShengUfs.
- The palawan-mainline kernel carries the A735 catalog entry and confirms the derived gmu\_chipid 0x070b0000, the three gen71100 firmware names, gmem of 1.5 MiB, gmu\_cgc\_mode 0x00020202, family ADRENO\_7XX\_GEN2 and the SH0/MC0/ACV BCM table; none of these are in the XNU tree yet.
- palawan.dtsi carries the complete GPU wiring: an 11-level OPP table matching the frequencies the device reports, seven GMU clocks, GPU\_CC\_CX/GX power domains, the GPUCC node at 0x3d90000 and the 26-interrupt ADRENO SMMU. The nodes are saved verbatim in reference/palawan-gpu-nodes.dtsi.
- palawan puts the GMU at 0x3d6a000 with size 0x35000 while peridot's stock node says 0x3d68000 size 0x37000; both end at 0x3d9f000. peridot must keep its own base or every GMU register offset shifts by 0x2000.
- Turnip already describes this part: freedreno\_devices.py carries FD735 for chip id 0x43030B00 as a7xx\_gen2 with num\_ccu 3 and tile\_max 2016x2032, matching palawan's ADRENO\_7XX\_GEN2 family. The userspace Vulkan description therefore exists and the kernel driver is the only blocker.
- A clean boot loads gen71100\_zap.mbn from /odm/firmware at 6.87 s and the driver lists gen71100\_gmu.bin with gen71100\_sqe.fw, so the GMU image is gen71100\_gmu.bin \(80680 bytes, sha256 435c7bac\); gmu\_gen70900.bin belongs to the other GPU bin, which /odm/firmware also covers with gen70900\_zap.mbn.
- The generator now also emits ShengGpuSmmuSource.h \(0x3da0000, streams &\#123;0,2&\#125;, GMU SID 5\) and ShengGmuCommandDbSource.h \(0x81c60000, 131072 bytes\) from the compiled DTB.
- The three kit sources and the Adreno735 skeleton compile against the kernel's own .o.json recipes: objects 47528, 9072, 21712 and 170976 bytes.
- Catalog entries Sm8635Platform and Adreno735 exist and unixnu status resolves with them; feeds.toml vendors drivers/Adreno735 locally like ShengUfs.
- Adreno735 is now linked: component:Adreno735 builds build/adreno735/libAdreno735.a, build-adreno735-kits.py appends 16 kit and dependency-kit objects, and build-xnu-4k-baseline.sh force-loads the archive, so kernel.macho carries NativeAdreno735 and ShengGmu symbols.
- The board build-arm-driver.py keeps hardcoded component, source, output and include tables, so adding a driver means patching four places there rather than the catalog alone.
- The kit now carries the palawan-derived votes data: eleven GPU OPPs with their RPMH levels and bandwidths, two GMU OPPs, the SH0/MC0/ACV BCM policy, gmem of 1.5 MiB and gmu\_cgc\_mode 0x00020202, all generated from scripts/data/sm8635-gmu-votes.json.
- Stage 1-2 is device-verified: p66 maps all five GPU windows with ml\_io\_map and ShengGmuBindMmio returns ShengGmuSuccess, reported as NU735 ctor gpu=1 mapped=5 bind=0 at NativeAdreno735.cpp:92.
- Built-in drivers get no IOKit personality in this kernel, so IOService matching never instantiates them; the working entry point is the Mach-O constructor, which p65 proves runs and can read boot arguments.
- Stage 3 reached the hardware: p68 reports hash=1 with a local SHA-256 because the kernel ccdigest glue is unusable at constructor time, and p69 lands the corrected core offsets at the GMU window plus 0x14000 where the bus returns an external abort.
- GPUCC is readable \(p70 reads cx=0x80000000 and gx=0x0\) but the sm8650 clock-branch offsets do not respond to writes \(p71 reads all five back as 0\), so the cliffs register map must come from the vendor source rather than the sibling platform driver.
- The vendor peridot-u-oss gpucc-cliffs.c offsets are correct where the sm8650 ones were not: p72 enables cxo, hub\_cx\_int, hub\_aon and cx\_gmu with bit 0 and bit 31 set.
- gpu\_cc\_ahb\_clk only enables after its parent gpu\_cc\_hub\_clk\_src RCG at 0x919c is configured, and the vendor GPUCC driver defines no GDSCs at all, so the CX and GX domains are hardware or RPMh controlled; p73 still aborts at GMU window plus 0x14000.
- p74 shows the GPUCC split: the CX branches \(cx\_gmu 0x90e4, hub\_cx\_int 0x90f4\) read as already enabled while gpu\_cc\_ahb\_clk \(0x90c8\) and the hub RCG \(0x919c, 0x91a0\) read zero and ignore writes.
- p75 enables the GCC GPU clocks \(qmip 0x80000003, memnoc 0x80000003, snoc 0x20000001\) yet gpu\_cc\_ahb\_clk stays zero, so the branch also needs its parent gpu\_cc\_hub\_clk\_src configured.
- Diagnostics now print through printf to the framebuffer console: a panic reboots the phone about a minute later and the screen is lost.
- p78 shows the hub RCG programming works: writing 3 to 0x919c leaves bit 1 \(ROOT\_EN\) set while the hardware clears bit 0, so the TCXO-sourced clock source runs.
- p79 then takes an external abort on the GPUCC 0x90c8 access itself, so that sub-block is unpowered; with the vendor GPUCC driver defining no GDSCs, the CX domain has to be powered through RPMh.
- p80 reads the AP RSC at 0x17a00000 and takes an external abort on the DRV\_ID register itself, so the RSC block is not powered in this boot path.
- Linux only reaches that block because the XBL and AOP handshake leaves it available; a UEFI to fastboot-boot to XNU start never performs it, so an RPMh voter cannot even open its mailbox yet.
- The Mu-Silicium tree carries no RPMh, AOP or GDSC code under Silicon/Qualcomm, so a firmware-side CX vote would be new firmware work rather than a configuration change.

### Completion criteria

- A GPU provider matches the ADT node and renders a frame.

### Current limits

- Only the window map and the kit bind are verified; no GMU register has been read or written, and the firmware stage still needs memory allocated before bsd\_init.

### Next action

- Establish a boot path in which the AP RSC answers before writing any voter: either a firmware-side vote or a vendor power framework port.
- Park stage 3 until CX can be voted; the GMU code is ready behind the power gate.
- Keep the GPU record evidence current so the next session starts from the RSC finding rather than the GPUCC one.

### Evidence

- `device`: [panic NU735 ctor gpu=1 mapped=5 bind=0 at NativeAdreno735.cpp:92: five windows mapped and ShengGmuBindMmio returned ShengGmuSuccess.](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/docs/gpu-bring-up.md)
  Command: <code>fastboot boot out/Mu-peridot-p66.img with kernel_args -v native-ufs-probe=15 ... peridot-gpu=1 peridot-gpu-panic=1</code>. Revision: `c2cd2c7fa2c58cc882d7052aebf8ab84dd2b8042`.

## Network {#network}

`planned`

### Hardware and dependencies

- Qualcomm WCN6750 wireless chip on PCIe, plus the vendor firmware from /vendor/firmware\_mnt.

### Configuration

- No network component is selected; the catalog's Ath12kWifi targets a different generation.

### Procedure

- Collect the WCN6750 firmware and board data files from the vendor partition.
- Select or write an implementation once the boot path is stable.

### Development findings

- The part is WCN6750: the stock cmdline points at /vendor/firmware/wlan/qca\_cld/kiwi\_v2, the WCN6750 firmware directory.
- HakiOS drives exactly this chip with Linux's ath11k and reports Wi-Fi working on the POCO X5 Pro: five kernel files plus an Apple80211 surface, built against a QMI core.
- UniXNU's Ath12kWifi targets the next generation, so it does not apply; the HakiOS stack is the only known working reference.

### Completion criteria

- The interface appears and associates with an access point.

### Current limits

- No network work is planned before the system boots to launchd.

### Next action

- Inventory the kiwi\_v2 firmware files from the vendor partition.
- Decide the licence boundary before pulling GPL ath11k code into the BSD-2 UniXNU tree.

### Evidence

Collect evidence using the next action.

## usb {#usb}

`planned`

### Hardware and dependencies

- DWC3 at 0xa600000 with its child window 0xd93c, apps\_smmu stream 0x40, GIC SPI 133 for the core interrupt and 130 for the power event, eUSB2 PHY and PMIC repeater, QMP combo PHY at 88e8000, UCSI over the PMIC GLINK channel and usb-role-switch.

### Configuration

- No USB node exists in this port's dtsi and no USB component is selected.

### Procedure

- Select QcomDwc3, then generate the QMP USB3 table from the palawan Linux tree.
- Regenerate the XDCI and XHCI class layouts against the 21H461 kernelcache and add the USB stacks to the kernel prelink roots.
- Confirm the core interrupt and the UCSI/vbus hooks for this board before any transfer test.

### Development findings

- UniXNU already ships the whole solution as QcomDwc3, derived from AppleUSBXDCI and AppleUSBXHCI; on sheng it enumerates at 10 Gbps and 480 Mbps, pairs with a Mac and starts lockdown sessions, while host mode is only partially verified.
- peridot's stock DTS already describes every board input the recipe asks for: DWC3 at 0xa600000, the same 0x40 SMMU stream as sheng, an eUSB2 PHY with its PMIC repeater, a QMP combo PHY and qcom,ucsi-glink.
- The interrupt differs from sheng: sheng uses INTID 165, peridot's dwc3 node carries GIC SPI 133 with the power event on 130, so the mapping has to be confirmed before registration.
- The local UniXNU checkout predates QcomDwc3; the catalog lists only QcomGeniSpi, so the component pin and the prelink roots have to be added first.
- The ABI scripts in the QcomDwc3 repository name the 24A446 kernelcache, while this port selects ipados-17.7.11-21H461, so both layout files must be regenerated.
- sheng keeps fairplayd.A2 and adid disabled with the USB stack enabled; both enabled stop SpringBoard from finishing boot.

### Completion criteria

- The device enumerates over USB, pairs with a Mac and a lockdown session starts.

### Current limits

- No USB driver is selected and nothing is modelled in the dtsi.

### Next action

- Raise the UniXNU pin to a revision that carries QcomDwc3 and add it to the component list.
- Generate drivers/QcomDwc3/QcomQmpUsb3.h from the palawan tree and regenerate both ABI layouts for 21H461.

### Evidence

- `source`: [The component page records the sheng status \(USB3 10 Gbps and USB2 480 Mbps enumeration, re-enumeration, Mac pairing and lockdown sessions; host mode partial; sustained transfer untested\), the board inputs the port must supply and the two class-layout overrides.](https://github.com/UniXNU/UniXNU/blob/b56f17c/docs/zh/drivers/qcom-dwc3.md)
- `source`: [ssusb@a600000 \(around line 15861\) carries dwc3@a600000 with iommus &lt;&amp;apps\_smmu 0x40&gt;, interrupts GIC SPI 133, an eUSB2 PHY, the PMIC repeater, qcom,ucsi and usb-role-switch, so every input the recipe asks for is already described.](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/dts/vendor/peridot-stock.dts)

## cellular {#cellular}

`planned`

### Hardware and dependencies

- Qualcomm MPSS firmware, the IPA data path and the QMI service table, all versioned with SM8635; the modem serves its file systems from UFS.

### Configuration

- No modem, IPA or QMI code exists in this port.

### Procedure

- Inventory the MPSS and IPA firmware from the vendor partition.
- Port the HakiOS modem stack \(mpss, ipa, qmi, cell, nas\) or decide it is out of scope, knowing that HakiOS itself only reaches SIM binding.

### Development findings

- HakiOS carries a research-grade modem stack: hakios.mpss.c \(250 KB\), hakios.ipa.c, hakios.qmi.c, hakios.cell.c and hakios.nas.c, with en1 as the data interface.
- On the POCO X5 Pro that stack reaches 'modem boots, sees the network, the SIM is bound, IPA and en1 in place; no registration yet', so a working data path is unproven even there.
- UniXNU has no baseband component, and this port has no UFS-backed file serving for the modem yet.

### Completion criteria

- The modem registers on the network and data flows over en1.

### Current limits

- Research only; no registration has been demonstrated in any XNU port reviewed here.

### Next action

- Inventory the MPSS and IPA firmware, then decide whether to port the HakiOS stack.

### Evidence

Collect evidence using the next action.

## Audio {#audio}

`planned`

### Hardware and dependencies

- Qualcomm audio DSP firmware and the vendor calibration data on the vendor partition.

### Configuration

- No audio component is selected.

### Procedure

- Collect the DSP firmware and the board calibration files.
- Bring up the DSP transport and then the codec path.

### Development findings

- Audio needs the ADSP firmware, GLINK and the codec configuration, none of which is present for this board.

### Completion criteria

- Playback and capture work through the DSP.

### Current limits

- Out of scope until the system boots to launchd.

### Next action

- Inventory the audio firmware files.

### Evidence

Collect evidence using the next action.

## Power {#power}

`planned`

### Hardware and dependencies

- PMIC and regulator topology from the stock DTS, plus the RPMh resource set at 0x17a00000.

### Configuration

- No power policy is configured. payload.adt.defaults sets only sleep-disabled when needed.

### Procedure

- Record the regulator topology and the CPU frequency domains before adding any power policy.
- Drive the regulators from the board package rather than the kernel.

### Development findings

- The stock DTS declares the RPMh controller and the regulator tree; none of it is modelled in the current dtsi.
- The SM8550 board package keeps its power policy in the board, and this port follows that split.
- Public snapshot: board.toml only drops the Adreno735 selection; the PMGR and power inputs are unchanged.

### Completion criteria

- Rails come up in the documented order and the device survives a suspend and resume cycle.

### Current limits

- No power management is implemented.

### Next action

- Extract the regulator tree from the stock DTS.

### Evidence

Collect evidence using the next action.

## Image assembly {#packaging}

`host-verified`

Components: `SoftwareAES`, `XnuPrelink`.

### Hardware and dependencies

- The iPadOS 17.7.11 kernelcache, trust cache bundle, Data seed, platform seed and the firmware DTB.

### Configuration

- config\_fragments and patch\_series list arch, soc, os and device roots in that order.
- payload.size\_mib = 64 and payload.trust\_cache\_sha256 pins the bundle \(StaticTrustCache v2 2478 + converted RestoreTrustCache v2 267, sha256 32462f52...860d\); payload.volume = PERIDOT. panic\_screen is off because the panic blob and the entry probe share the kernel padding.
- payload.kernel\_args = \[-v, native-ufs-probe=18, sheng-pmgr=2, amfi\_get\_out\_of\_my\_way=1, peridot-allow-unsigned-root=1, offline-apfs-load=1, rd=md1, amfi-allows-trust-cache-load=1, amfi\_allow\_any\_signature=1, -restore\].

### Procedure

- Run ./unixnu ipsw fetch, then ./unixnu kernel, package, firmware, payload and bootimg in that order.
- Keep the kernelcache, trust cache and Data seed outside the repository.

### Development findings

- Prelink inputs come from the OS profile; this board must not restate them.
- 2026-11-15: the kernel build is reproducible \(same kernel.macho sha256 4d078ac1... across runs\), the kernel blob is gzip mtime=0 \(1,830,003 bytes\), every payload build re-extracts kernel.macho/trust cache/Data seed and compares them with the inputs, and out/manifests/&lt;name&gt;.json records the hashes \(current kernel sha256 2cb5e7ad..., image p360 68,943,872 bytes\).
- The macOS-only skip-setup and seed-data-grow steps are not needed for the RAM-disk root path.
- Public snapshot: the Adreno735 archive step is removed from board.toml because its firmware is local-only; the rest of the packaging is unchanged.

### Completion criteria

- Every step produces its artifact and the boot image contains the expected firmware, device tree and payload.

### Current limits

- There is no clean-checkout CI: the WSL build tree &lt;unixnu-checkout&gt; and the EDK2 tree behind &lt;Mu-Silicium&gt; are prepared by hand and only their heads/hashes are recorded.
- The boot-image ramdisk limit is 96 MiB; the payload budget is checked in build-apfs-md.sh and there is \~30 MiB headroom.

### Next action

- Freeze the &lt;Mu-Silicium&gt; firmware diff and the &lt;unixnu-checkout&gt; revision into the record before the next prelink change.
- Add the same gates to a clean CI build once the last hand-built dependency is scripted.

### Evidence

- `host`: [Kernel rebuilt \(4d078ac1810de8c3... reproduced, then 2cb5e7ad57102cbf... with the storage fixes\), payload and boot image produced \(68,943,872 bytes\), manifest out/manifests/p360.json written, check-consistency passes 11/11.](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/board.toml)
  Command: <code>bash peridot/tools/wsl-build-xnu.sh; bash peridot/tools/build-apfs-md.sh p360; bash peridot/tools/check-consistency.sh</code>. Revision: `5aba75132ed14960f3205fa810aaf64cca67c982`.

## Diagnostics {#diagnostics}

`device-verified`

### Hardware and dependencies

- UEFI log buffer at 0x81CE4000, the panic screen patch and the boot progress checkpoints.

### Configuration

- payload.panic\_screen is enabled; kernel\_args include -v, serial=3 and boot-progress=2.
- No board diagnostics package exists yet.

### Procedure

- Capture the firmware log before the kernel handoff and keep each checkpoint separately.
- Use the bring-up guide to record the first failing checkpoint.

### Development findings

- The peridot memory map provides a UEFI log region, so firmware faults can be captured without a UART.
- The phone exposes USB device mode, so logs can be retrieved without serial hardware.
- Public snapshot: the Adreno735 archive step is removed; the diagnostics hooks are unchanged.

### Completion criteria

- A failing boot identifies its last completed checkpoint from captured logs.

### Current limits

- Panic format strings must stay 32-bit: %llu/%o abort inside \_\_doprnt on this build \(HANDOFF-2026-11-15.md section 7\); two diagnostics still use 64-bit specifiers and are known debt.

### Next action

- Capture the firmware log from the first boot attempt.
- Replace the remaining 64-bit panic specifiers and add a build-time lint for them.

### Evidence

- `device`: [hostBringUp completed: planUfsSmmu adopted the firmware stream mapping \(single unmasked match, target bank SCTLR.M clear\) instead of rewriting it, the request queue started, NOP OUT passed and findRootLayout read the GPT. The userdata entry starts at LBA 0x253000; block 0 of that window read as zeros, which is expected for an unformatted or encrypted volume.](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/drivers/ShengUfs/SmmuTakeover.h)
  Command: <code>fastboot boot out/Mu-peridot-adopt.img with kernel_args -v native-ufs-probe=10</code>. Revision: `02a562d39c4cbd160633d3ab611010a994d54848`.
- `device`: [The 8.74 GiB SHNGROOT image was written in 12 sparse chunks; on the next boot root windows reported userdata first=0x253000 last=0x7aab7fa, manifest status=0 and windows=2, so the kernel now parses the root volume structure on this device.](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/drivers/ShengUfs/NativeUfs.cpp)
  Command: <code>fastboot flash userdata userdata-root.img (8.74 GiB via Linux fastboot in WSL), then fastboot boot with kernel_args -v native-ufs-probe=11</code>. Revision: `02a562d39c4cbd160633d3ab611010a994d54848`.

## userspace {#userspace}

`device-verified`

Components: `ShengUfs`, `DarwinBoot`.

### Hardware and dependencies

- mockfs \(XNU's minimal executable-root filesystem\), a Data ramdisk carrying a static arm64 Mach-O, and rd=md0.

### Configuration

- CONFIG\_XNU\_SOURCE\_MOCKFS=y is the last mockfs line in configs/peridot\_defconfig. xnu\_env\(\) takes the last value, and an earlier '\# CONFIG\_XNU\_SOURCE\_MOCKFS is not set' silently disabled the build \(the vfs\_conf.o marker stayed 0 and no mockfs symbol reached the kernel\).
- board.toml sets kernel\_args = -v rd=md0 sheng-pmgr=2 amfi\_get\_out\_of\_my\_way=1 peridot-allow-unsigned-root=1, payload packed\_data\_ramdisk = false so the ADT publishes a plain RAMDisk, and no native-ufs-probe value so the UFS driver does not touch rootdev.
- The root device content is a static Mach-O built by tools/build-launchd.sh. tools/add-unixthread.py replaces LC\_MAIN with LC\_UNIXTHREAD because load\_lcmain\(\) marks LC\_MAIN images as needing dyld, and clears MH\_DYLDLINK/MH\_PIE; tools/strip-dylinker.py rewrites the LC\_LOAD\_DYLINKER command as two LC\_SOURCE\_VERSION commands so no file offset moves.
- peridot-allow-unsigned-root=1 makes process\_signature\(\) treat the unsigned ramdisk executable as CS\_SIGNED\|CS\_VALID; without it the MAC exec hook kills pid 1 with OS\_REASON\_EXEC/SECURITY\_POLICY before any user code runs.

### Procedure

- bash peridot/tools/build-launchd.sh
- bash peridot/tools/build-ramdisk-root.sh pNNN \(payload with --data-ramdisk, 64 MiB crop, mkbootimg\)
- fastboot boot out/Mu-peridot-pNNN.img

### Development findings

- launchd and dyld run from the UFS-backed APFS restore root \(p368/p371\), which proves the signed userspace contract on this board.
- p372-p381: the kernel execs an Apple tool as pid 1 from peridot-init-path/arg1..3 boot arguments and the tool really drives the platform storage. After fixing the bdevsw write count units \(buf\_count bytes vs 512-byte blocks\) and the disk ioctls newfs\_apfs requires \(DKIOCGETFEATURES / DKIOCISSOLIDSTATE / DKIOCSYNCHRONIZE\), newfs\_apfs formatted the 8 GiB install target and the kernel found the APFS NXSB superblock at offset 32 \(p381\).
- p376-p379: newfs\_apfs pushed 1088+ strategy writes \(including a full-device initialization pass\) with no I/O errors and the writes are on disk \(p378 scan: nz=3 firstnz=1\), so the bdevsw RMW/FUA path works under real tool traffic.
- Public snapshot: board.toml only drops the Adreno735 selection; the launchd path is unchanged.

### Completion criteria

- init executes a static arm64 image, its syscalls return correct results, and the output reaches the panel.

### Current limits

- pid 1 can be any existing ramdisk executable via the boot arguments, but there is no shell in the restore ramdisk and the APFS root is read-only, so multi-step tool runs need one binary per boot or a custom static init; tool output is invisible because the exec path has no console file descriptors.
- newfs\_apfs can format the install target, but running asr/restored against it still needs the IPSW OS image on the device \(or a userspace disk-image channel\) and the tools have to be driven one boot invocation at a time.

### Next action

- Mount the freshly formatted target as root \(probe 39 path\) to confirm the newfs\_apfs container is mountable, then add console file descriptors \(or a result channel\) to the init override for multi-step tool runs.
- Put the decompressed IPSW OS image on userdata through a fastboot userdata image, expose it as a disk the kernel/adapter can read, and drive asr to restore it into the new APFS container.

### Evidence

- `device`: [The panel shows 'PERIDOT-USERSPACE pid=0x0000000000000001 fd=0x0000000000000000': init started from the mockfs root, getpid\(\) returned 1, open\(/dev/console\) returned fd 0, write\(\) reached the console, and the system stays up with no panic.](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/scripts/mockfs-launchd.S)
  Command: <code>fastboot boot out/Mu-peridot-p131.img with kernel_args -v rd=md0 sheng-pmgr=2 amfi_get_out_of_my_way=1 peridot-allow-unsigned-root=1</code>. Revision: `283feb0deb1ed0c4909ff4e664f0113e3d9acbff`.
- `device`: [p368: com.apple.xpc.launchd\[1\] and restored\_external\[3\] run from the UFS-backed APFS root; image out/Mu-peridot-p368.img \(kernel sha in out/manifests/p368.json\).](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/patches/xnu/peridot-bdevsw-root.patch)
  Command: <code>fastboot boot out/Mu-peridot-p368.img with kernel_args -v native-ufs-probe=36 sheng-pmgr=2 amfi_get_out_of_my_way=1 peridot-allow-unsigned-root=1 offline-apfs-load=1 rd=md1 amfi-allows-trust-cache-load=1 amfi_allow_any_signature=1 -restore</code>. Revision: `23770733a454667dd844787f8fe40fb8b13219cf`.
- `device`: [Kernel execs newfs\_apfs as pid 1; the tool starts device I/O and the kernel data-aborts in planUfsSmmuBank \(pc 0xfffffff0079d9134\). p374 \(probe 41\) reports target block 0 still zero: found=0 head=00000000. out/screen-p372-init-override-exec-failed.jpg, out/screen-p373-newfs-data-abort.jpg, out/screen-p374-target-check-after-newfs.jpg](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/patches/xnu/peridot-init-args.patch)
  Command: <code>fastboot boot out/Mu-peridot-p373.img (native-ufs-probe=40, peridot-init-path=/System/Library/Filesystems/apfs.fs/newfs_apfs, peridot-init-arg1=/dev/nu0)</code>. Revision: `afbb8b92da434da9606da77aa93c8e94de697aea`.
- `device`: [newfs\_apfs runs as pid 1 and formats the 8 GiB install target: kernel verification reports NATIVE\_UFS init: found=1 off=32 head=78505f5c ok=1 \(APFS NXSB on the target\). out/screen-p381-newfs-apfs-container-ok.jpg; the earlier ioctl/exit-73 diagnosis is in out/screen-p380-newfs-ioctls.jpg.](https://github.com/WaLymT/UniXNU-peridot/blob/2158177f8670f7f7fc2d35db51ab10086b89ca1d/drivers/ShengUfs/NativeUfs.cpp)
  Command: <code>fastboot boot out/Mu-peridot-p381.img (native-ufs-probe=40, peridot-init-path=/System/Library/Filesystems/apfs.fs/newfs_apfs, peridot-init-arg1=/dev/nu0)</code>. Revision: `9f31ce00dc7b5300c03da6c9792039cac7296bfb`.

</div>
