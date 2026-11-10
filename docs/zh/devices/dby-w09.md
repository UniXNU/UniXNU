# Huawei MatePad 11

[WQSQW/UniXNU-dby_w09](https://github.com/WQSQW/UniXNU-dby_w09)

<div v-pre>

Huawei MatePad 11 \(DBY-W09, kona\) runs iPadOS 17.7.11 with the donor identity iPad7,1 / j120ap. The board owns its partition geometry, defconfig, boot package and build recipes; XNU, driver and kit implementations come from the shared tree. This record states what is implemented, what has been observed on hardware and what is still missing.

源记录: [porting.toml](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/porting.toml), `715814d07840c817317892d5a585f4a3e769e343`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `implemented` |
| [固件与启动](#firmware) | `device-verified` |
| [CPU 与中断](#cpu) | `implemented` |
| [内存与 DMA](#memory) | `device-verified` |
| [存储与根卷](#storage) | `device-verified` |
| [显示](#display) | `device-verified` |
| [输入](#input) | `device-verified` |
| [GPU](#gpu) | `planned` |
| [网络](#network) | `planned` |
| [音频](#audio) | `device-verified` |
| [电源](#power) | `device-verified` |
| [镜像组装](#packaging) | `device-verified` |
| [诊断](#diagnostics) | `device-verified` |
| [device-tree](#device-tree) | `host-verified` |

## 配置 {#configuration}

`implemented`

### 硬件与依赖

- iPadOS 17.7.11 build 21H461 for iPad7,1 \(chip\_id 0x8011, board\_id 12, device\_class j120ap\).
- Shared hardware description and drivers resolve through \[components\] plus the two feeds in feeds.toml: the sm8250 SoC feed and the ShengUfs driver replacement.
- One defconfig, configs/dby\_w09\_defconfig, named by board.toml \[kernel\] defconfig.

### 配置

- board.toml sets schema\_version = 2, so the profile layers, dts/, the SoC repository and patch\_series are read as format 2.
- \[board\] kit = dby\_w09 maps package/ to kits/dby\_w09 in the assembled tree.
- \[ipsw\] pins the restore URL, identity and two root-image member hashes; \[userdata\] records the userdata GPT entry; \[device\_tree\] selects dts/dby\_w09.dts with the SoC include directory, and scripts/unixnu/devicetree.py generates the ADT.
- feeds.toml pins two sources beyond the base repository: kind = soc sm8250 \(FFT-infra/UniXNU-sm8250-common\) and kind = driver ShengUfs \(FFT-infra/NativeUfs-alioth, the SM8250 stream of the same driver\). ./unixnu fetch clones both at their pinned commits and records them, with every Apple reference source and edk2, in unixnu.lock. Machine paths belong to the ignored local.toml or --local-module.

### 操作步骤

- Read https://unixnu.com/porting/device-repository and https://unixnu.com/porting/records.
- From the UniXNU checkout run ./unixnu defconfig dby\_w09\_defconfig -D ../UniXNU-dby\_w09, then ./unixnu status --json -D ../UniXNU-dby\_w09 and ./unixnu tree -D ../UniXNU-dby\_w09.
- Check that every printed module source is the intended one before building.

### 开发经验

- The iOS flashlight gate is a build-time ADT input: docs/guide/mobilegestalt.md:14-32 lists the /product properties as things the payload writes when the image is built, and scripts/unixnu/devicetree.py:280-287 turns any non-property key of an \[adt.\*\] table into a child node of the same form, so \[adt.product.camera.u32\] flash = 1 emits the node AVFlashlight asks about \(refer/PaganiDrivers/drivers/PaganiTorch/README.md:76: +\[AVFlashlight hasFlashlight\] is MGGetBoolAnswer of camera-flash, which is the property flash of IODeviceTree:/product/camera existing at all\). adt-walk.py over the payload that shipped as ord216 reads /product -&gt; /camera -&gt; flash = 01000000. What is NOT settled is written here rather than left hidden: the mother adds that node from the kernel only when the plug-in is visible and the driver runs, so a static ADT copy also answers camera-flash on a boot where dby-ti is off, and on 2026-11-09 the owner reported that Control Center lists a camera whose opening restarts SpringBoard. Cause is being attributed before any further flash.
- The catalog name is \`dby-w09\`, not \`dby\_w09\`: scripts/sync-devices.py parses board.toml through board\_data\(\), which returns None unless \[board\] name matches SLUG = \[a-z0-9\]\[a-z0-9-\]\*, so an underscore makes the twice-daily scan discover the repository and then skip it -- none of the registered devices has an underscore, while repository names may keep one \(IssacL04/UniXNU-Pagani\_SM8750 registers as oneplus13t\). porting-record.py:validate requires device.name to match board.toml and config.py:80 builds out/&lt;name&gt;/ from it, so the record name and the two out/ paths in the prose moved with the board name; kit = dby\_w09, configs/dby\_w09\_defconfig, dts/dby\_w09.dts, \[firmware\] config and scripts/check-dby\_w09.py are directory or file names and are unchanged.
- board.toml on 2026-11-05 pins the firmware tree as the published \`WQSQW/uefi-dby\_w09@423e222\`, and the sm8250 SoC feed checkout is at its pinned commit \`6bb9b025704764a662728dce1a30557a35e082d8\` with a clean work tree, so \`unixnu fetch\` reproduces both feeds.
- scripts/ is an overlay, not a symlink: tree.py:assemble copies core, then the SoC repository, then the device repository into out/&lt;device&gt;/tree/scripts, so scripts/build-xnu-4k-baseline.sh in this repository IS the board kernel step and core's copy is only the default it replaces. When core changes that script the board copy has to be re-diffed by hand; today the two differ only in the QcomXnuUsbDebug hunks.
- components.toml is symlinked from core and the device repository cannot extend it \(tree.py:assemble\), so a module with no catalog spec reaches the kernel as package/&lt;Name&gt; plus a \[kernel\] archives script slot; that is the official shape for QcomXnuUsbDebug, and \[components\] says so instead of pretending to select it.
- Editing configs/\*\_defconfig alone is inert: the kernel build reads the generated out/dby-w09/.config, so defconfig must run again after every defconfig change.
- The donor identity is not a free choice. Prelink, ADT, PMGR contract and Metal inputs are written against iPad7,1 / 21H461, the only combination with an official qualified reference; another donor means redoing target adaptation from scratch.
- kernel\_args are measured, never assumed: the CPU round passed armcpu-self-ipi=1 and moved sheng-cpufreq from 2 to 3, so the accepted line is 46 arguments and 984 bytes against the 1000-byte gate in core/scripts/unixnu/payload.py:35. The probe that spent the whole reserve \(sheng-banner=1, 47 arguments and 999 bytes\) was built, flashed, read and reverted at the owner's instruction on 2026-11-05: a readable log outranks painted text, and he never asked for the text back. So the line is at 984 with 16 bytes free again, and qcom-usb-ctl=1 \(15 bytes with its space\) has gone back from queued to affordable. On 2026-11-05 21:43 the line moved to 46 arguments and 993 bytes: sheng-log=1 was dropped \(-12 bytes, the owner judged the userdata log window useless after it was built and read\) and -enable\_kprintf\_spam added \(+21\). That flag is the only thing missing between the 3844-byte / 65-line console and full kprintf: the QUD port rewrites pe\_kprintf.c so qcom\_usb\_debug\_kprintf\_requested = \!disable\_kprintf\_output, which is false on a DEVELOPMENT kernel unless this argument is present, leaving only the \_cnputs printf tee. On 2026-11-06 00:08 the owner approved a trim and the line was re-measured at 42 arguments and 901 bytes with 99 free: offline-legacy-retire=1 \(-23\), boot-ui-focus=launchd \(-21\), boot-ui-focus4=SpringBoard \(-26\) and sheng-data-reset=1 \(-18\) were each dropped together with their separating space. None of the four carried behaviour, and that was checked at the reader, not assumed: offline-legacy-retire and offline-legacy-cpu-present feed one OR at NativeLegacyDisplay.cpp:522 \(if \(\!\(retire==1 \|\| cpuPresent==1 \|\| force\)\) return false;\), cpu-present stays, so the retire path is untouched; the two boot-ui-focus rows re-added processes BootProcessProbe.c:36 already lists \(launchd sits at slot 0, SpringBoard at slot 2 with trace\_slot=&\#123;0,1,1&\#125;\), so the sample table simply falls back to its default; sheng-data-reset=1 never enters a branch because BootWatchdogPolicy.c:51 acts only on reset==2, leaving the persist argument as the one that works. The reclaimed reserve goes to the backlight argument under the naming rule now written at the top of kernel\_args: a board-prefixed short key, dby-bl=1, takes 9 bytes including its separator where the sheng-backlight=1 the earlier budget assumed would have taken 18. That rule is the answer to the 1024-byte ceiling being structural \(DarwinBoot.c:542 CommandLine\[1024\] copies straight into boot\_args.CommandLine, which the kernel declares as BOOT\_LINE\_LENGTH 1024 at pexpert/arm64/boot.h:25\): a new switch either earns a short board name or moves to the device tree through PE\_get\_default and /defaults, which devicetree.py:376 already emits.
- payload\_sha256 can never repeat between two builds of one source: generate\(\) writes os.urandom\(64\) as /chosen/random-seed \(core/scripts/unixnu/devicetree.py:308\), so the ADT differs by seed bytes only. Measured on 2026-11-05 by extracting kernel.macho.adt and unixnu.toml out of the accepted 4e808ec1 image and the reverted c1303fb6 image with mcopy -i and diffing them: the two command lines are byte-identical and the ADT differs in 62 bytes inside one 64-byte range \(393..456\). Identity of a payload is that diff, not its sha.
- A fresh output tree is not self-sufficient on this board: the board slug dby-w09 \(catalog rejects the underscore\) derives the whole output directory from \[board\] name, so out/dby-w09/... starts empty while out/dby\_w09/... holds the previous round. Three build-tree inputs that no builder on Linux can make have to be carried across: the two xnu-prelink reference candidates that build-sheng-hid-input.py:20 and build-gop-legacy-display.py:109 hard-require \(the device builder build-platform-power.py:5 defines the fallback and documents it as this board-s previous prelinked kernel, but the HID and display consumers have no such branch\), the pruned QEMU observation record build/display-analysis/mobile-graphics-legacy-abi.json that audit-mobile-graphics-legacy.py:61 falls back to, and CONFIG\_XNU\_VERIFIED\_ROOT\_ARCHIVE, whose only writer build-cpu-desktop-kernel.py:9 is macOS-only. All three contain Apple kernelcache bytes, so they can never be committed.
- An untracked local copy of the shared tree accumulates board-specific edits silently. Every module that the board build depends on must be named here, otherwise this repository cannot reproduce the kernel \(see README Deviations\).
- The porting-record gate only fires for files an area claims, and three of this board-s live sources were claimed by nobody: package/DbyBattery.cpp, package/BatteryProbe.cpp, package/DbySmartPA.cpp and package/GeniI2c.c/h matched no area paths at all, so several rounds of battery, PA and bus work could be committed without the gate ever asking for a record change -- the skip is silent, it does not read as a pass. They are now claimed by power and audio. The mirror image of the same defect is package/BootLog.c, which sits under network: an area that has nothing to do with it, which is how its behaviour got asserted in three other areas without ever being checked there.
- Two output trees live on the build host and only one is current: out/dby-w09 \(the catalog name, hyphen\) and out/dby\_w09, the format-1 tree from before the 2026-11-05 rename. A wrapper pointed at the stale one does not fail, it prints a kernel hash, an archive listing and a payload that belong to no image ever flashed -- measured on 2026-11-06, where it reported the 2026-11-05 kernel a6382e52 after the real build had produced b587c637. Any proof read off a build directory has to name the directory it came from, and the hash has to be recomputed from the file that actually went to the device.
- Two boot arguments were reversed on 2026-11-08 and both reversals are measurements rather than tidying. offline-legacy-unit-scale went to 1 to test whether the panel flicker was the scale; the verdict came the same day: the interface dropped to the very small tier \(1 lays the panel out as 1600 x 2560 logical points on a 10.8-inch tablet\) and the flicker kept happening, so the value went back to 2 and the flicker was settled by the supply, not by this argument. dby-bl was switched off for the same experiment and its cost was equally immediate: without it the brightness control disappears entirely, because package/BacklightProbe.cpp:24 returns from sheng\_backlight\_probe\(\) unless the argument parses as 1, which leaves the AppleARMBacklight classes unregistered and nothing published. It is back on, and the flicker was never a candidate inside that gate: the four amplifiers are probed at :22, two lines before the dby-bl test, so dropping the argument could not have changed what the smartpa path does. Both rows now carry their measured reason in board.toml so the next hand reaches for the result instead of repeating the experiment.
- The defconfig rule above is a step and not a note, and it recurred on the torch archive: \`configs/dby\_w09\_defconfig:130\` already named three archives and \`tree/build/dby-torch/libDbyTorch.a\` \(256216 B\) already existed, yet kernel pass 1 died on \`Undefined symbols: \_dby\_torch\_start, referenced from: \_monitor in libBootProgress.a\(BootProgress.o\)\` because the generated \`out/dby-w09/ipados-17.7.11-21H461/dby\_w09/.config:148\` still carried the two-archive line. \`BOOTSTRAP=0\` in that same log is what excluded the bootstrap-link explanation, and re-running \`./unixnu defconfig dby\_w09\_defconfig -D ../UniXNU-dby\_w09\` made both passes return 0. A red link row naming an archives symbol is read as the missing step, not as a recipe that failed.
- The argument line is re-measured every round rather than carried forward, and on 2026-11-09 it paid for the torch. At this commit the joined \`kernel\_args\` are 49 arguments and 989 bytes against the 1000-byte gate, so 11 bytes are free and \` dby-torch=2\` is on the line. The payment came from \`-no\_slto\_panic\`, chosen by enumeration and not by preference: 22 candidate names were searched across this repository, core, the sm8250 SoC feed, the xnu feed and uefi-sheng, and that one has exactly one reader \(\`osfmk/kern/startup.c:473\`, which only clears the \`SECURITY\_READ\_ONLY\_LATE\` \`spinlock\_timeout\_panic\` consulted at \`locks.c:417\`, \`:506\`, \`:599\` and \`:621\`\), is absent from the CRITICAL\_ARGS dict of \`scripts/check-regression.py\`, and no accepted boot console capture has ever printed a spinlock timeout. \`-apfs\_shared\_datavolume\` looked just as spare and is not spendable: it is pinned in that same dict, in \`scripts/regression-baseline.json\`, and in the official provisioned-Data shape at \`core/scripts/check-provisioned-data.py\`. The second rule this swap teaches: \`scripts/check-regression.py\` diffs the shipped line against the recorded baseline list and fails on a vanished argument, so removing one from \`board.toml\` without moving \`scripts/regression-baseline.json\` in the same commit turns the gate against whoever reads it next; both files move together here, the baseline now lists 48 arguments, the shipped line 49, the lost set is empty and the only addition is the torch argument. The visible boot self-test is still not affordable \(\` dby-torch=1\` plus \` dby-torch-test=NNNN\` costs 31 bytes against 11 free\), so what the line arms is the read-only dry run.
- \`board.toml\` gained a \`patch\_series\` entry this round and nothing else: \`device:patches/xnu/series-torch\` is appended after \`device:patches/xnu/series-audio\`, last, with a comment naming the reason \(both hunks of the torch patch anchor on lines the audio patch inserts\). That is the whole of the ordering rule for this repository - \`scripts/unixnu/patches.py\` prepare\(\) resolves the list and applies it literally, and re-clones the XNU work tree when the series signature changes, so a reordered or renamed entry is a tree that builds differently rather than a comment that can be wrong quietly. \`kernel\_args\` is untouched at 49 arguments and 989 joined bytes, so the torch native arguments are still not on the line and nothing accepted moved.

### 完成条件

- Status resolves without error, every referenced file exists in the repository, and no personal path is required to build.

### 当前范围

- The kernel step this board builds with lives in the repository, so its diff against core is maintained by hand.
- ./unixnu status calls any local.toml module override unpinned, so the reproducibility verdict only holds for the published shape: a machine that adds a local.toml prints not reproducible for this same commit.

### 下一步

- Re-run status after any profile, source pin or defconfig change and record the effective module list.

### 证据

- `source`: [Board, IPSW identity, userdata geometry, kernel, firmware and payload inputs described in this section](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/board.toml)
- `source`: [Kernel configuration selected by \[kernel\] defconfig, including the owner data volume UUID](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/configs/dby_w09_defconfig)
- `source`: [dby\_smartpa\_probe\(\) is called on :22 and the boot argument is parsed and gated on :24, so the amplifier bring-up and the brightness service sit on opposite sides of that return: removing dby-bl can only cost the brightness control and can never change what the smartpa path does](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/package/BacklightProbe.cpp)
  Command: <code>sed -n 21,24p package/BacklightProbe.cpp</code>. Revision: `d8713c10ece45faed2d80762d8f04a014b6f6e49`.
- `host`: [generated .config:148 carries all three archives; pass 1 kernel d2ad2b4d and pass 2 kernel 05d697b0be1471b8 both RC=0; the 20 DbyTorch symbols are defined \(type S\) and none is undefined. The same sources without the defconfig re-run fail pass 1 on \_dby\_torch\_start.](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/configs/dby_w09_defconfig)
  Command: <code>./unixnu defconfig dby_w09_defconfig -D ../UniXNU-dby_w09 &amp;&amp; ./unixnu build kernel -j 2 -D ../UniXNU-dby_w09 --uefi ../uefi-sheng (twice) &amp;&amp; llvm-nm --extern-only kernel.macho</code>. Revision: `a167df4c928876b460e4543a5755f77976ce2c92`.
- `host`: [kernel\_args joined to 989 bytes, 49 arguments, 11 bytes free against the 1000-byte gate; payload.json carries dby-torch=2 and no -no\_slto\_panic; the gate prints checks=93 pass=93 fail=0 and the baseline-versus-shipped lost set is empty, so nothing accepted disappeared.](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/board.toml)
  Command: <code>./unixnu build payload -D ../UniXNU-dby_w09 with the recorded carriers, then python3.11 scripts/check-regression.py -D ../UniXNU-dby_w09</code>. Revision: `0a6d3ceb548fd5874f7e0ec95eb0b5aa9fd91f49`.

## 固件与启动 {#firmware}

`device-verified`

### 硬件与依赖

- UniXNU UEFI \(Silicium mu-derived\) tree exposing Platforms/Huawei/dby\_w09Pkg/dby\_w09.dsc and Resources/Configs/dby\_w09.toml.
- EDK II base packages and the DarwinBoot driver package, resolved from the build tree.
- Stock Huawei boot image: the panel, the three physical keys and USB device mode are already usable at the firmware level.

### 配置

- board.toml \[firmware\] records config = dby\_w09, the DSC path, Build/dby\_w09Pkg/&\#123;target&\#125;\_CLANGPDB/FV/SILICIUM\_UEFI.fd, preflight scripts/check-dby\_w09.py and the PACKAGES\_PATH list.
- \[firmware.defines\] sets DEVICE\_MODEL = dby\_w09, ENABLE\_SECUREBOOT = 1, MEMORY\_PROTECTION = TRUE and SHIP\_MODE = FALSE.

### 操作步骤

- Build the firmware in its own tree, then pass the checkout to the payload build with --uefi.
- Boot the tablet into fastboot from that firmware and flash the payload; read the screen state after each attempt.

### 开发经验

- \`unixnu build firmware\` is now the only firmware entry point used here: \`WQSQW/uefi-dby\_w09@423e222\` built \`Build/dby\_w09Pkg/DEBUG\_CLANGPDB/FV/SILICIUM\_UEFI.fd\` \(8,388,608 bytes\) with 0 \`error:\` lines, 1 upstream warning from \`SiliciumPkg.dsc.inc\(211\)\`, and preflight \`50 memory descriptors checked, 0 static errors\`. The same tree rebuilt an FD that matches the flashed one on 106 of 107 FFS entries, the outlier being the 8-byte CodeView PDB GUID in \`PcdDx\_.ffs\`.
- ./unixnu build firmware does work against this checkout, contrary to what this area recorded until 2026-11-05: run it from the core checkout with --uefi &lt;uefi tree&gt; --edk2 &lt;core mu\_basecore feed&gt; -D &lt;device repository&gt; --jobs 4 and it produces Build/dby\_w09Pkg/DEBUG\_CLANGPDB/FV/SILICIUM\_UEFI.fd in 103-119 s. edk2 must be the core feed because the Mu\_Basecore checkout has no brotli, and python3 must be 3.11 or newer for tomllib.
- Whether a blob reaches the firmware volume is decided by the PE32\| line of the module INF, not by which file the packaging script copies: a patched UsbConfigDxe.patched.efi next to the vendor binary is invisible in the FV until the INF names it, so read the FFS list before believing a note about what was shipped.
- A DEBUG firmware volume is not byte-reproducible: \_\_DATE\_\_ and \_\_TIME\_\_ change on every rebuild, so the boot packaging gate compares the FD timestamp against the sources it must include and records the hash instead of pinning it.
- The firmware handoff is what makes XNU visible: the GOP framebuffer and the entry-argument HOB are consumed by the legacy display backend, so a display failure is usually a firmware-side reservation problem, not a driver problem.
- The device enters fastboot from the UEFI port, which is the only supported way to write the payload partition.
- The panel's Error: Image at &lt;base&gt; start failed: Not Found does identify the image: EDK2 prints the load base both in the Loading driver line \(Mu\_Basecore/MdeModulePkg/Core/Dxe/Image/Image.c:869\) and in the start-failure line \(Image.c:1902\), so the address printed next to USB boot desired was MsBootPolicy.efi itself, and the status is what its entry point returned. It only ever runs because this platform registered no boot option for UniXNU: the official recipe in UniXNUPkg/Driver/UniXNUDxe/UniXNUDxe.inf is to put that registrar driver in the same firmware volume as the application, so on dispatch it writes a Boot\#\#\#\# for the app and moves it to the front of BootOrder and the platform BDS starts UniXNU like any other boot option - but dby\_w09.dsc and dby\_w09.fdf shipped only UniXNU.inf. BDS therefore fell through to Silicium's Internal Storage option, which names the MsBootPolicy FV file \(Silicon/Silicium/SiliciumPkg/Library/MsBootOptionsLib/MsBootOptionsLib.c:246\), and that application finds no BOOTAA64.EFI on any SimpleFileSystem \(Common/Mu/PcBdsPkg/MsBootPolicy/MsBootPolicy.c:345, No handles survived filtering\!\) and returns EFI\_NOT\_FOUND at :346. Wiring UniXNUDxe into the same FV is the fix; USB boot desired, but no USB devices found on first attempt is that same MsBootPolicy USB step and was never a USB regression.

### 完成条件

- The firmware image builds, enters UniXNU, publishes the framebuffer and preserves the documented memory reservations.

### 当前范围

- The firmware lives in its own repository and is not yet published, so a machine that clones only this repository cannot rebuild the FD that the recorded boot image was made from.

### 下一步

- Publish the firmware repository at the commit whose UsbConfigDxe.inf names the vendor binary, so the boot image in README is reproducible from two pinned repositories instead of one plus a workbench.

### 证据

- `device`: [Hardware boots this firmware, shows the UniXNU menu, hands the panel over to XNU and re-enters fastboot on request](https://github.com/UniXNU/UniXNU)
  Command: <code>make -C &lt;uefi&gt; (dby_w09Pkg, RELEASE), then fastboot flash preload &lt;payload.img&gt; and power on</code>. Revision: `c37c18deb67df26e7a8394b5a8309ffce339e15c`.
- `source`: [Board preflight checks named by \[firmware\] preflight](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/scripts/check-dby_w09.py)

## CPU 与中断 {#cpu}

`implemented`

组件: `ArmCpu`, `ArmDTPlatform`.

### 硬件与依赖

- Eight ARM64 cores \(SM8250 Kryo 585\): four Cortex-A55 \(cpu0-3\) and four Cortex-A77 \(cpu4-7\), MPIDR core number in Affinity1 so the phys ids are 0x000 through 0x700.
- GICv3 interrupt controller, PSCI through SMC; secondary start is PSCI CPU\_ON, taken from the ArmCpu component.
- Three EPSS frequency domains at 0x18591000/0x18592000/0x18593000 with 4/3/1 cores each, the qcom-cpufreq-hw epss register interface \(reg\_enable 0x0, reg\_domain\_state 0x20, reg\_dcvs\_ctrl 0xb0, reg\_freq\_lut 0x100 with 4-byte rows, reg\_perf\_state 0x320\). This SoC declares no EPSS L3, so the L3 window the SM8550 reference probes maps is absent here.
- native-smp-secondary.patch and native-smp-type-clusters.patch, now from the SoC feed at a6e7e36 \(the pin the official SM8250 board uses\), and package/CpuFreqProbe.cpp taken unchanged from that same board.
- ArmCpu pinned in feeds.toml to xVanTuring/ArmCpu@a9c4585, the same pin the official SM8250 board uses, for the cluster-aware registration and the completion call described in findings.
- AppleARMPlatform and ApplePMGR kept in the prelink roots of board.toml \[kernel.prelink\].

### 配置

- dts/dby\_w09.dts declares unixnu,cluster-type = "E" on cpu0-3 and "P" on cpu4-7, in the same file that enables the eight cores.
- \[payload\] kernel\_args enables sheng-smp=1, armcpu-diagnostics=1, armcpu-spi-ipi=1 and armcpu-self-ipi=1, and sheng-cpufreq=3 \(vote every domain that reads enabled its highest non-turbo level\).
- scripts/build-gop-legacy-display.py compiles CpuFreqProbe.cpp from the same IOPlatformExpert record as the display and key-store probes and puts CpuFreqProbe.o in the force-loaded late archive, which is what makes sheng\_cpufreq\_probe/sheng\_cpufreq\_poll resolve instead of hitting the weak no-op in LinkStubs.c.
- early\_security\_init points at the unmodified AppleMobileFileIntegrity \_\_TEXT\_EXEC address of the donor kernelcache.
- ArmCpu is the shared secondary-core and IPI driver, pinned in feeds.toml to xVanTuring/ArmCpu@a9c4585 rather than the directory's UniXNU/ArmCpu@9066b53; ArmDTPlatform publishes the platform description it reads from the handoff device tree. The 19 armcpu\_\* symbols this board's package/kits/scripts read were checked against the fork before the pin moved, so the panel rows are unchanged.
- board.toml \[kernel\] patch\_series still lists device: before os:, but only for sheng-platform-power now: the two SMP patches moved to their official layer when the sm8250 feed pin moved from 6bb9b02 to a6e7e36.

### 操作步骤

- Build the kernel and payload, boot the device and read the boot-progress checkpoints for the CPU stage.
- Run scripts/check-smp-topology.py from the device repository before flashing: it exits non-zero for a tree that declares cluster-type tags without the cluster patch, and that combination kills the kernel before the console comes up.
- Read panel row 39 \(BootProgress.c:342, drawn once native\_cpufreq\_stage reaches 2\): CPUFREQ d0/d1/d2 each with the enable bit, the current level in MHz, the voted LUT index and the level seen before the vote.
- Where the panel is ambiguous, reproduce the same image in the offline QEMU harness and read the diagnostic counters as text.

### 开发经验

- Secondary cores come up only when the IPI path matches what the ADT declares; armcpu-spi-ipi=1 was needed after an early bring-up that reached user space on one core.
- An SGI does not reach these cores: ArmCpu.cpp:34 records that IPIs are software-pended SPIs, and XNU only enables a core's IPI after that core has itself sent one, so each core has to signal itself in initCPU. The reader is at ArmCpu.cpp:365 and was already linked; the board simply never passed armcpu-self-ipi=1, which the official same-SoC board's cpu record lists as one of four required arguments.
- sheng-cpufreq was in this board's kernel\_args long before anything read it: the call site LegacyDisplayProbe.cpp:495 resolved to the weak no-op in LinkStubs.c:96, so no boot of this port has ever issued a frequency vote and the domains sat on whatever the reset left. The argument's bytes were paid for; the vote was not.
- unixnu,cluster-type must never ship without native-smp-type-clusters.patch. With MAX\_CPU\_CLUSTERS still 1 the topology parser takes phys\_cluster\_id = \(cluster\_type == P\), which is 1, and writes cluster\_phys\_to\_logical\[1\] past a one-element stack array; release builds do not assert, the kernel just dies before the console. The official SoC patch is also what raises MAX\_CPU\_CLUSTERS to 2 and defines \_\_ARM\_AMP\_\_, so this board needs no separate AMP patch.
- The same patch gives the Edge scheduler per-bucket cluster preferences for the case with no performance controller: fixed-priority and above-utility timeshare buckets prefer the first P cluster, utility and background the E cluster. That is the official mechanism for keeping UI work on the big cores; nothing here is a board-local scheduler.
- The directory's ArmCpu cannot use that mechanism: at 9066b53 both registration paths \(ArmCpu.cpp:402 for the boot core, :452 for a secondary\) set info.cluster\_type = ml\_get\_boot\_cluster\_type\(\), so all eight cores are declared as the boot cluster and the DTS cluster-type tags never reach the processor record. It also never calls ml\_cpu\_init\_completed\(\); the only call site in this XNU tree is AppleARMSMP.cpp:236, and this board brings secondaries up through ArmCpu, so the Edge scheduler is told nothing about inter-cluster edges -- without them no thread migrates or is stolen across clusters. That is why MAX\_CPU\_CLUSTERS 2 plus cluster tags alone could not have fixed the lag, and why the pin is the official part of this round: xVanTuring/ArmCpu@a9c4585 reads topology-&gt;cpus\[cpu\].cluster\_type per core and calls ml\_cpu\_init\_completed\(\) once every core of the topology has registered, and derives the SPI IPI INTID base from GICD\_TYPER instead of the fixed 1008, which is sheng's number.
- armcpu-self-ipi=1 is read in both copies \(ArmCpu.cpp:365 sets gSelfIpi, used at :536 and :550 in the pinned copy\), so the argument was never dead code here -- it was simply never passed.

### 完成条件

- All cores run, the timer and IPI path is stable, user space is scheduled across them, and the E/P split reaches the scheduler with each EPSS domain voted to its highest non-turbo level.

### 当前范围

- CPU idle states are still not ported: no domain is asked to park a core, and the idle path stays whatever the reset default is.
- The cluster vote and the per-domain frequency readings are wiring plus the official checker in this round; the on-device numbers arrive with the first boot that draws row 39.

### 下一步

- Read row 39 and the per-process CPU rows from the UFS log window once package/linux-log exists -- the banner is off by the owner's choice, so the panel no longer shows them. The P cluster \(c4-c7\) should carry the UI workload, which is the alioth record's own success criterion; until rows exist the evidence is his own report that the system is much smoother.
- Then idle states, which nothing on this board has touched yet.

### 证据

- `device`: [Kernel with SMP boots on hardware; boot-progress and panic text are drawn by the panel build](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/board.toml)
  Command: <code>./unixnu build payload -D ../UniXNU-dby_w09 --uefi ../uefi-sheng … &amp;&amp; fastboot flash preload &lt;payload.img&gt;</code>. Revision: `d8b80295118ef25ac3a784134bcf95cd8e88109f`.

## 内存与 DMA {#memory}

`device-verified`

### 硬件与依赖

- LPDDR5 whose size is a per-unit input rather than a board constant: this model ships with 6 or 8 GiB, and the tested unit has 6 GiB \(dram\_size 0x180000000 in \[payload\]\).
- DarwinBoot contiguous window selected by \[payload.adt\] owned\_memory\_size.
- Persistent Data overlay pages held by the RAM block device.

### 配置

- \[payload.adt\] owned\_memory\_size = 0x100000000: the value the same-SoC official board uses. Without it DarwinBoot falls back to its 256 MiB window and XNU sees only 256 MiB.
- The ADT generator writes the reserved-memory nodes that the stock bootloader expects, including the splash region.

### 操作步骤

- Build the payload, boot and read the memory checkpoints from the panic or diagnostic page.
- Compare the reported free pages against the window size before concluding a memory shortage.

### 开发经验

- The image measured on hardware on 2026-11-05 is payload \`09c3aad671332eee4b0771e3592196d06e2b32a3f167164c1f20722f0934910f\` \(218,103,808 bytes\) over prelinked kernel candidate \`a6382e526e02747b952f45fd4878d194e4796cfa2ead0b6932da87078006b707\` \(125,677,568 bytes\); those are the numbers the 4 GiB register window and the tested unit's dram reg in board.toml were sized against, so any window or seed change restates both.
- The window size was the first silent limit: the kernel booted, then user space stalled with a memory-shaped failure while 3.7 GiB of the declared RAM was simply unavailable to it.
- Free-page counts printed by a panic are the decisive measurement; an allocation failure that survives a rebuild with more free memory is a different bug, not a size problem.
- A sparse Data container is what makes an 8 GiB seed usable: the firmware reads the initrd as one whole File-&gt;Read\(\), so a dense container stalls the loader.
- DRAM is not a board constant on this model: units ship with 6 or 8 GiB, so dram\_size 0x180000000 and the device tree memory node both record the tested 6 GiB unit, and another unit re-measures that pair rather than reusing it.

### 完成条件

- The kernel reports the intended DRAM size and the payload's window reaches user space.

### 当前范围

- The 6 GiB figure is the tested unit's, taken from the product specification of that variant; a SMEM RAM table read-out has not been recorded.
- DRAM size is not fixed on this model, so a unit of the other variant needs dram\_size and the device tree memory node re-recorded together before the payload is built.

### 下一步

- Confirm DRAM against a firmware memory map dump and record the reservations actually handed to XNU.

### 证据

- `device`: [Panic page on hardware reports pages=0xf37fe free=0xed5e1, i.e. the 4 GiB window is published and mostly free](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/board.toml)
  Command: <code>./unixnu build payload -D ../UniXNU-dby_w09 --uefi ../uefi-sheng … &amp;&amp; fastboot flash preload &lt;payload.img&gt;</code>. Revision: `d8b80295118ef25ac3a784134bcf95cd8e88109f`.
- `source`: [the 2026-11-08 audio round adds the cpu cluster tags and nothing else to the tree: no reserved window, no memory node and no change to the pil\_adsp\_mem range AdspProbe maps, so no row this area owns moved](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/dts/dby_w09.dts)

## 存储与根卷 {#storage}

`device-verified`

组件: `ShengUfs`, `VirtioMmioBlock`, `RamBlock`, `SoftwareAES`, `AppleKeyStoreState`, `VerifiedRoot`.

### 硬件与依赖

- UFS on LUN 0 with 4096-byte logical blocks; this model ships with 128 or 256 GiB and the tested unit has 128 GiB, so the capacity is read from the device instead of assumed.
- Backup GPT read from a full 9008 dump: the userdata entry spans first\_lba 0x29B600 to last\_lba 0x1D455FF, i.e. 27,959,296 blocks = 114,521,276,416 bytes.
- fastboot in the same session reports the userdata partition size as 0x14651E0000 = 87,595,810,816 bytes, so the two sources disagree and neither number is used to write anything.
- OS and Cryptex1,SystemOS root images, mounted read-only as disk windows.
- A scratch Data volume seed carrying the writable /private/var.

### 配置

- \[userdata\] records the two windows and the LBA range read from the backup; nothing about the geometry is estimated.
- \[kernel.prelink\] roots keep com.apple.filesystems.apfs and com.apple.iokit.IOStorageFamily, so offline-apfs-load=1 can resolve the identifier it loads.
- \[payload.adt\] root\_match\_volume\_uuid and packed\_data\_ramdisk = true describe the delivered form; CONFIG\_XNU\_OWNER\_DATA\_VOLUME\_UUID in the defconfig must equal the seed's volume UUID.
- The selected components split by role: ShengUfs drives the UFS host on hardware, RamBlock backs the packed Data seed as a block device, VirtioMmioBlock is the root block device of the offline harness, AppleKeyStoreState publishes the key-store events userspace waits for \(package/KeyStoreProbe.cpp, sheng-aks=1\), VerifiedRoot carries the OS and SystemOS root trust and SoftwareAES is chosen because no Qualcomm crypto engine driver is ported.

### 操作步骤

- Build the kernel, then the payload with --data-ramdisk, flash the payload partition and read the Data mount checkpoint.
- For a seed produced by the official fixture workflow, verify the packed form against \[payload.adt\] packed\_data\_ramdisk before blaming the driver.

### 开发经验

- The payload partition choice is a capacity fact, not a preference: the official kernel image is 119 MiB and the cache partition is 104 MiB, so the payload lives in the preload partition. userdata is never imaged because it holds the tablet's own iPadOS root volume.
- A missing or mismatched Data seed is unambiguous: native\_ram\_block\_volume\_seed\(\) fails, kern\_exec reports the mount error and the boot stops. Growing an existing seed keeps the volume UUID and needs only a payload rebuild; a fresh fixture changes it and forces a kernel rebuild.
- Persistent Data \(sheng-data-persist=2\) writes every dirty page through the UFS store. It eventually fills its own container and the next write returns ENOSPC, which surfaces as a watchdog-policy panic; sheng-data-reset=1 starts the overlay over.
- Copying the fixture onto a dense container instead of a packed one only moves the failure: the loader stalls on the read instead of the kernel stalling on allocation.
- UFS capacity is a per-unit input the same way: 128 and 256 GiB units exist, so the userdata range in board.toml is this unit's backup table and is never a number to carry to another device.

### 完成条件

- Root and Data volumes mount on hardware, the overlay survives a reboot and no partition other than the payload partition is written.

### 当前范围

- The UFS geometry is read from a backup of the factory table rather than from the running device tree, and no vendor UFS calibration blob is used.
- The recorded userdata range belongs to the 128 GiB unit this record was measured on; a 256 GiB unit has a different table and has to be read before anything is written.

### 下一步

- Record the store capacity and wear counters of the overlay once the boot is repeatable.

### 证据

- `device`: [APFS mounts the OS, SystemOS and Data windows on hardware; the ENOSPC path \(watchdog launch policy failed: 28\) and its reset path were both observed on the panel](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/package/BootWatchdogPolicy.c)
  Command: <code>./unixnu build payload -D ../UniXNU-dby_w09 --uefi ../uefi-sheng --data-ramdisk &lt;seed.dbr&gt; &amp;&amp; fastboot flash preload &lt;payload.img&gt;</code>. Revision: `d8b80295118ef25ac3a784134bcf95cd8e88109f`.
- `source`: [Partition roles and the flash target, each with the capacity fact behind it](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/README.md)
- `source`: [sheng\_policy\_unmodified\(\) reads the on-disk disabled.plist and skips the rewrite when it already carries this boot policy, and an ENOSPC at the done label is reported instead of fatal, so a full 8 GiB Data seed cannot stop a boot that has nothing left to configure](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/package/BootWatchdogPolicy.c)

## 显示 {#display}

`device-verified`

组件: `GopFramebuffer`.

### 硬件与依赖

- Firmware GOP framebuffer handed over by the UEFI port.
- Panel mode published through /chosen display-scale.
- Unmodified IOMobileFramebufferLegacy and IOMobileGraphicsFamily from the donor kernelcache.

### 配置

- \[kernel\] archives build the legacy display backend with build-gop-legacy-display.py and force\_load it.
- \[payload\] kernel\_args keep the official offline-legacy-\* sequence with offline-legacy-unit-scale=1 and offline-legacy-phase=4.
- panic\_screen = true patches the panic screen into the payload copy of the kernel.
- GopFramebuffer is the selected shared component that publishes the firmware framebuffer to that backend.

### 操作步骤

- Rebuild the payload for an argument change, rebuild the kernel only for a driver change, flash and photograph the panel.
- Read the display checkpoints \(stage, client calls, swap validation, frame count\) as text from the diagnostic page.

### 开发经验

- scripts/build-gop-legacy-display.py binds the legacy backend to a reference kernel image: it takes build/xnu-prelink/native-owner-mobile-graphics-candidate.macho, or the newest native-owner-ufs-cpu-desktop-\*-candidate.macho when that name has been pruned, and writes its original-bindings.S with .globl/.set at the absolute addresses read from it. That directory is written by core scripts/unixnu/kernel.py:prelink, which runs after the link, so the first kernel pass of a fresh clone has no candidate to bind against and the step stops with \`No reference candidate available\` rather than building without a display. The board carries no seed for it: the bindings are only valid for a candidate this panel has already booted, and a committed copy would freeze the kernel identity it was taken from.
- The display and PMGR builders import native\_prelink from the official kit directory kits/XnuPrelink in the assembled tree. They previously prepended kits/NativePrelink, a name retired upstream, so that path never existed for a fresh clone.
- scripts/build-boot-progress.py compiles the board BootProgress.c with the panic-screen glyph table \(Font.h\) taken from the Mu-Silicium checkout passed with --uefi, so the firmware tree is a build input of the kernel step; a missing checkout is now the documented prerequisite error instead of an empty -I that surfaces as a fatal missing-header error.
- The legacy backend's own start already dispatches the hardware start; calling it a second time from board code produced a crash storm that looked like a panel failure.
- Scale is the gate that decided everything: preferredScale 0 makes the unchanged -\[FBSDisplayMode \_initWithWidth:height:preferredScale:\] trap, SpringBoard never finishes and the render server ignores the panel. Publishing /chosen display-scale with unit-scale=1 closed it.
- Once the OS owns the panel, the diagnostic page must not take it back. boot-diag-resume=10 alternated our text page with the iPadOS lock screen because an ambient screen legitimately scans out nothing for more than ten seconds.
- The lock screen with its clock and home indicator is now on the panel on hardware, which is the first presented iPadOS frame observed on this board.
- scripts/build-gop-legacy-display.py:293 asserted that the only ready reader of native\_battery\_stats\[16\] is the \[battery\] row in BootLog.c and that the row never printed for lack of a producer. The second half was an assumption and the first half is false: BootLog.c is compiled by no builder in this tree, so the row is not in the image \(ar membership, builder grep and symbol table in the diagnostics area\). The comment now states what was measured instead.

### 完成条件

- An iPadOS frame is presented and stays presented across a normal idle period.

### 当前范围

- A fresh clone needs one kernel pass that produces a prelink candidate before the legacy display archive can link; build/xnu-prelink/ is a build product, not a repository input.
- No hardware cursor, no vsync-driven swap accounting and no DPU-specific timing on this SoC: the path is a GOP-backed legacy scanout.

### 下一步

- Keep the panel with the OS across idle, then make the lock screen passable \(see the input area\).

### 证据

- `device`: [Video of the panel shows the iPadOS lock screen \(clock and home indicator\) alternating only with the diagnostic page, which boot-diag-resume then stopped](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/scripts/build-gop-legacy-display.py)
  Command: <code>./unixnu build kernel -j 2 -D ../UniXNU-dby_w09 --uefi ../uefi-sheng &amp;&amp; ./unixnu build payload … &amp;&amp; fastboot flash preload &lt;payload.img&gt;</code>. Revision: `d8b80295118ef25ac3a784134bcf95cd8e88109f`.
- `source`: [Panic and checkpoint text rendered by the panel build](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/scripts/xnu-panic-screen.c)

## 输入 {#input}

`device-verified`

组件: `ShengHidInput`, `ShengNovatekTouch`, `QcomGeniSpi`.

### 硬件与依赖

- Capacitive touch panel \(Novatek N9Z family over TDDI\) and three physical keys \(power, volume up, volume down\), polled on the SE14 GENI SPI bus.
- The keys are already usable in firmware; the DbyTouch stack reports them in XNU as an HID consumer as well.
- Touch firmware image for this panel, carried verbatim in package/DbyTouch/DbyTouchFw.h.

### 配置

- \[components\] selects ShengHidInput, ShengNovatekTouch and QcomGeniSpi from the catalog; the board producer DbyTouch reaches the kernel through \[kernel\] archives and scripts/build-dby-touch.py.
- \[kernel.prelink\] roots already include com.apple.iokit.IOHIDFamily and com.apple.iokit.IOHIDEventDriver, so the OS side of HID is inside the prelink closure.
- \[payload\] kernel\_args carry the stage ladder: dby-touch=8 dby-touch-se=1 sheng-touch-hid=1 sheng-buttons=1, with offline-hid-input=1 offline-hid-home=1 offline-key-events=1 on the consumer side.

### 操作步骤

- Read https://unixnu.com/porting/input completely before writing board code: transport and sensor, publishing reports through the qualified IOHIDDevice ABI, then physical buttons.
- Keep the vendor-verified driver sources byte-identical to the accepted implementation, then change one variable per flash and read the stage ladder.

### 开发经验

- \`DbyTouch\` is the accepted producer for this panel \(Novatek N9Z, 1600x2560, mode 0\): on hardware it reports points on the lock screen against payload \`09c3aad6…\`, so the earlier no-XNU-HID-device limit is closed. The Home and volume keys go through the board \`KeypadDeviceLib\` in the firmware tree.
- The stage ladder gates the chip side only: once the SE answers \(dby-touch-se=1\) stage2 chains to stage5, which reads frames and publishes contacts, so dby-touch=2 already reaches the UI. Reading the number as a feature switch misattributes every later failure.
- Publishing reports means subclassing the original IOHIDDevice with its exact 207-slot vtable and 0xd0 instance size; an approximate header changes the instance layout and the failure appears far from its cause.
- The N9Z command mailbox and the 0x30000 firmware array are board data, not SoC data: taking the SM8550 board's controller sources as-is for this panel is the trap on this line.
- The publish cadence question is closed by reverting, not by re-tuning. The rung ladder &\#123;8208, 2048, 1024, 512, 128&\#125; and every number measured on it \(read=11178 us on the 128 rung, loop=25994 us, about 67 us per piece\) describe a read path that exists only in our tree: the accepted driver has no ladder, it reads at a fixed DBY\_TOUCH\_FRAME\_CHUNK piece with a memset per piece. On 2026-11-06 the self-invented read path went back with \`git checkout e61237a -- package/DbyTouch/DbyTouch.cpp package/DbyTouch/DbyTouchBoard.h\`, which removed +470/-24 lines and the nine symbols stage5ReadAdaptive, gTouchChunks, gTouchChunkStep, gTouchChunkFail, gTouchTxPad, gTouchFaultTry, dbyTouchCompensateBase, gTouchBaseLift and gTouchIdleRun; kernel 916f71cd and payload e4a24792 were then rebuilt from the restored source. So the cadence figures above are measurements of reverted code and are not a criterion for anything. What stands: this unit is a three-firmware integration assembled by its owner, the stage-8 upload really does run \(dby-touch=8 dby-touch-se=1 sheng-touch-hid=1, byte-for-byte the reference kernel-args.txt values\), and the accepted read shape is part of that contract, not a detail to optimise.
- Withdrawn inference. The 2026-11-06 sentence that eliminated GENI\_ERR\_TIMEOUT \(-110\) because a silent engine would cost about 20 ms at poll\_limit 20000 was arithmetic on an unmeasured constant: it assumed one empty-poll iteration costs 1 us, and that iteration cost was never measured on this bus, so both the 20 ms figure and the -110 exclusion it produced are void. The refusals it set out to explain \(the cf=1/1/1/0 row\) came from the ladder described in the entry above, and the fault latch it defended -- snap\_irq, snap\_status, snap\_txfs, snap\_rxfs copied on every failed piece plus a 4-byte CS-release transfer inserted inside stage5ReadChunked -- was itself our addition. Putting an instrument inside the data path it measures is how this panel went from working to dead, and no raw errno was ever recorded for that boot.
- A diagnostic column that never moves is a bug, not a baseline: gTouchUsLoopMin was re-armed to 0 at every publish window while the sample test also accepts gTouchRateN == 0, so every row after the first printed loop=26088/0/26305 -- a minimum of 0 us, which reads as a free loop. It re-arms at 0xFFFFFFFF now.
- The deferred question -- touch stops working after a while -- did not reproduce at this cadence: the 2026-11-06 capture is 745 lines over a 420 s window and the loop was still publishing when it closed \(n=15936, i.e. 15936 x 26 ms = 414 s of it, rf=0 read failures, IRQ timeouts 0, no panic row\). Whatever killed the earlier streams sat on the 76 ms path, so the silent read-fail backoff stays a hypothesis about the old cadence rather than a measured cause of this one. A second, free measurement on that same boot, taken at 10:35 while the console ring replayed: 89,800 publish cycles in the captured stream \(n=28928 up to n=118750, about 39 minutes at the 26 ms cadence, i.e. roughly 51 minutes of uptime\) and every row still reports chunk=128, cf=1/1/1/0, wait=1 us, IRQ timeouts 0, rf=0, with no \[touch\] link clear row and no panic anywhere in 199807 bytes. So on this cadence the loop does not degrade with age. What the same replay cannot decide: all 360 \[touch\] p= rows in it read h=0 an=0 live=0 cc=0, i.e. no contact was confirmed during that period -- and whether a finger was on the panel is not recoverable from the console, so it stands as an open observation on this line rather than a measured defect. Both captures in this entry were taken on the reverted ladder build, not on the accepted read path, so they describe our own code and not the panel.

### 完成条件

- A touch or key event reaches SpringBoard and the lock screen can be dismissed on hardware.

### 当前范围

- This area records the accepted DbyTouch stack and the catalog consumer; the hand-built producer that preceded it is retired, so its counters no longer describe the shipped path.

### 下一步

- Use working input as the instrument for the next frontier instead of panel photographs, and re-open this area only if a touch regression appears.

### 证据

- `device`: [Accepted on the tablet on 2026-11-04: contacts follow the finger, the swipe clears the lock screen and the three keys report. This is the state committed as e61237a.](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/package/DbyTouch/DbyTouch.cpp)
  Command: <code>./unixnu build kernel &amp;&amp; ./unixnu build payload -D ../UniXNU-dby_w09 --uefi ../uefi-sheng, then fastboot flash preload &lt;payload.img&gt; and reboot</code>. Revision: `e61237a2db62a1a35b57d6cdcec8671ec1878265`.

## GPU {#gpu}

`planned`

### 硬件与依赖

- Adreno 650 \(SM8250\). The shared tree's GPU components target Adreno 740, a different generation.
- Signed ZAP firmware and GMU/HFI bring-up inputs, neither of which this board has recorded.

### 配置

- The board selects no GPU component; com.apple.iokit.IOGPUFamily is kept in the prelink roots only because the donor closure requires it.
- IOCoreSurfaceRoot has to be published for the display stack to complete, which was done without any GPU hardware.

### 操作步骤

- Before porting, confirm an SM8250 GPU path exists upstream or scope the bring-up as its own project; do not adapt an Adreno 740 source line by line.

### 开发经验

- Everything currently on the panel is CPU-rendered scanout, so GPU work is an optimization and not the next blocker.
- The display stack reaching its started state without GPU proves the surface path is separable from rendering.

### 完成条件

- A GPU-backed surface presents and the frame counters move without the CPU renderer.

### 当前范围

- No GPU code is implemented for this SoC.

### 下一步

- Decide the SM8250 GPU route after the system is usable.

### 证据

按下一步操作收集证据。

## 网络 {#network}

`planned`

### 硬件与依赖

- SM8250 Wi-Fi/BT combo plus the modem subsystem, both requiring firmware blobs this port does not carry.
- No serial or USB console is wired in XNU, so device observations come from the panel.

### 配置

- No network component is selected; com.apple.iokit.IOSlowAdaptiveClockingFamily and friends are in the prelink roots only as closure dependencies.
- launchd jobs that need the modem or Bluetooth are suppressed by sheng-disable-jobs rather than started and failed.

### 操作步骤

- Read the bring-up order first: a console or log path that survives a panic makes every later subsystem cheaper, so the USB debug console is the step before Wi-Fi.

### 开发经验

- Disabling identityservicesd, locationd, CommCenter and bluetoothd is a bring-up measure to keep noisy subsystems out of the boot, not a statement that they work.
- The absence of any host-visible log is what makes each iteration cost a physical flash and a photograph.
- The \`A\` row of \`package/BootLog.c\` - a file this area owns the paths for - is wider and carries two more mount pairs: \`char row\[120\]\` became \`char row\[200\]\`, and \`mount4=stage/status mount5=stage/status\` were appended after \`mount3=\`, with the comment naming what each pair stands for \(the audio HAL plug-in and the flashlight plug-in overlay\) and what each stage of the ladder means. Fixing the row also fixes the claim attached to it: \`mount4=\` was recorded as printed before it was, and \`checks=93 pass=93 fail=0\` after the change says the row width cost nothing else.

### 完成条件

- An interface is enumerated, associates and obtains an address on hardware.

### 当前范围

- Nothing is implemented and no vendor firmware inventory exists for this board.

### 下一步

- Port the SM8250 USB debug console to get a log path, then evaluate Wi-Fi.

### 证据

- `source`: [the \[audio\] row prints the legacy APR ladder \(st, q, ans, status, refused, to, ign, rdy, up, down, op, drop, sendfail, lvl, done, map\) over the 16 native\_audio\_stats slots in a 240-byte buffer, in place of the AudioReach probe mode field. It is a row format change, which is why this area sits on it: BootLog.c is the console and panel row composer](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/package/BootLog.c)

## 音频 {#audio}

`device-verified`

### 硬件与依赖

- SM8250 \(kona\) audio DSP \(ADSP, LPASS\) and the firmware image inside this unit's own modem partition; the playback graph this machine's vendor kernel defines for it - legacy APR over GLINK with PRI TDM at 0x9000, not MI2S and not a WCD codec - and the four TFA9874 amplifiers on the qupv3\_se3 I2C bus.
- Apple audio kexts are in the prelink closure \(IOAVFamily, IOAudio2Family, AppleIISController, AppleAudioClockLibs\) because the donor roots list requires them.

### 配置

- Three arguments are enabled on the audio path and they are a chain, not three switches: sheng-adsp=2 is power.md section 2 tier 2 \(start the subsystem and bring up GLINK\), dby-audio=2 runs the legacy APR playback ladder in package/DbyAudio.cpp, whose own gate at :709 also demands that tier, and sheng-gpu-addon=1 gates the boot-time addon mount that presents /private/var/ngpu/audio over /System/Library/Audio/Plug-Ins/HAL.
- The codec half this field used to call missing was never what stood between the ladder and sound: ord209 plays out of the four TFA9874s with no SM8550 AudioProbe.cpp compiled for this board and no clock provider selected here, because the Kona path hands PRI TDM at 0x9000 to the amplifier and the ADM brings its own backend clocks up. What was missing is the timestamp-valid bit of the ASM write, recorded in findings.
- The audio server plug-in is donor code, kept here as a copy rather than as a patch. hal/ShengAudioPlugIn.c is the donor tree's file minus its authenticated-pointer branches: the ptrauth.h include, the two-way handling of the AudioGetHostClockFrequency dlsym result and the ptrauth guard around the image-load trace, leaving the plain 47-bit mask, because the bundle is built as arm64 while the audio server that loads it is arm64e. hal/Info.plist, da8a31bf, and package/ShengAudioAbi.h, 9ef36987, are byte-identical to the donor's, and scripts/build-sheng-audio-hal.py is the donor builder with its TARGET argument removed, which pins arm64-apple-ios17.0. So the board-specific part of the OS half is only which seed carries the bundle and which trust cache names its CDHash - and the seed CI builds the donor commit it pins \(68940017\) rather than this copy, because that is the tree it can fetch today, so the trust entry is read from that build's own trust.json and bundle and CDHash cannot come apart.

### 操作步骤

- Follow the shared guide for the ADSP and audio path before writing board code; the closure presence of the audio kexts is not an implementation.
- Survey before loader, in the order power.md section 2 sets it: read what the boot stages left, write nothing, and let that decide whether a PIL-TZ load sequence is needed at all.
- Before a constant is taken from another board's kit, diff the compatible string first - pas\_loader and pil-tz are different hardware paths and their addresses are not interchangeable.

### 开发经验

- GLINK identity, not the DSP, is what kept apr\_audio\_svc down. Our own OPEN\_ACK carried our number in the field the peer uses to find the channel, and a repeated OPEN reset a live channel. The vendor rule, now written at the branch points of package/QcomGlink.c: qcom\_glink\_rx\_open\(\) finds a channel by name and only there does rcid get assigned, from the peer's OPEN \(:321-338\); qcom\_glink\_send\_open\_ack\(\) keys the ACK on channel-&gt;rcid and the peer resolves it in its own lcids, so an ACK confirms an open and never reveals a number \(:340-349, and the local-initiated ack goes out from progress\(\) at :196-201 once both halves are known\); both ends therefore have to send OPEN. Each branch counts itself now \(QcomGlink.h:53-54 lcid, rcid, open\_sent, open\_acked, remote\_open, ack\_sent, up and :75-77 unmatched, last\_unmatched\_cid, last\_unmatched\_cmd\), so a channel that stays down names the command that matched nothing instead of only a refusal count.
- package/ShengAudioService.cpp sat in the tree named by nothing: DbyAudio.cpp:39-43 externs its static initialiser, its start routine and its two ring entry points, but no builder compiled it, so the second kernel pass died on three undefined symbols. It is now compiled and archived the way the donor kit does the same file \(its scripts/build-gop-legacy-display.py compiles it, objcopies it and lists it in the archive\): \_\_DATA,\_\_mod\_init\_func is removed and \_\_GLOBAL\_\_sub\_I\_ShengAudioService.cpp is globalised, because publishService\(\) at DbyAudio.cpp:431-438 registers those two classes by name between OSMetaClass::preModLoad and postModLoad, and registering them from the initialiser section as well is the duplicate-OSMetaClass panic this board has already paid for.
- The classification knob has two measured positions and its third candidate is now closed by enumeration rather than by taste. Answering kAudioDeviceTransportTypeBuiltIn is the only built-in lever the AudioServerPlugIn API gives a plug-in: across the five headers a HAL bundle can include \(AudioServerPlugIn.h and, through it, CoreAudioTypes.h and AudioHardwareBase.h, plus AudioHardwareDeprecated.h and AudioHardwarePropertyData.h\) the only Port-spelled names are kAudioStreamTerminalTypeDisplayPort and kAudioDeviceTransportTypeDisplayPort, so the Apple port descriptions the donor record points at \(docs/devices/sheng.md:461\) belong to the DriverKit side and a plug-in cannot reach them; the AudioTransportManager that would vend end points is an AudioPlugIn subclass whose CreateDevice and DestroyDevice return kAudioHardwareUnsupportedOperationError in the donor file and in this repository's copy alike \(hal/ShengAudioPlugIn.c:129-130\), and Apple declares no TransportManager plug-in type UUID -- the bundle's CFPlugInType is kAudioServerPlugInTypeUUID -- so that branch is unimplemented, not a verified road to built-in. The device-level spelling of the volume fails the same test from the other side: volm, vold, vdb\#, v2db and db2v are declared only in AudioHardware.h:1248-1252, the client header AudioServerPlugIn.h does not include \(its CoreAudio includes are CoreAudioTypes.h and AudioHardwareBase.h, :110-111\), and AudioHardware.h:994-1022 documents each of them as implemented by an AudioVolumeControl subclass -- the object this plug-in already vends through the device control list. Answering them on the device would mean pulling the client API into a server-side bundle to duplicate an answer the server already knows how to reach, and the curve declaration that goes with them, 'lctf' and 'vctf' \(AudioHardwareDeprecated.h:115 and :505\), is not asked of this plug-in on any boot, so neither is added. What is left is the one knob that is: hal/ShengAudioPlugIn.c answers kAudioDeviceTransportTypeBuiltIn again, the value the sheng plug-in it descends from ships.
- The transport question is closed by the official source rather than by our own ranking, because it was reopened twice. The UniXNU sheng plug-in this one descends from answers kAudioDeviceTransportTypeThunderbolt at hal/ShengAudioPlugIn.c:279 \(introduced by 08cde20\), and its comment at :276-278 states the alternatives and why they are not reachable from a bundle: built-in devices are used only through Apple's port descriptions and a USB device must carry a USB location the HAL does not take from a plug-in \(i529\). That same file carries exactly one volume path -- an AudioVolumeControl object, set at :170-182 and read at :353-369, with no device-scope volume family -- so the official delivery is this transport plus this control, and this board matches it. Our own two boots rank identically: on Thunderbolt the audio server wrote the volume \(os=1000 want=0 sets=0 at boot, then os=225 want=3 sets=1, sets=1 played=3653632 late=0, 1000 to 225 milli\); on built-in it streamed and never moved the gain \(ord203: opens=1, played=1429504, late=0, holes=0, volume\_sets=0\). Two things follow, and both are now settled rather than argued: the display label of an external-looking device is what the official mechanism costs, and the device-scope volume spelling \(volm, vold, vdb\#, v2db, db2v\) stays out -- it was implemented this cycle, then reverted, because those selectors belong to the control object the server already reaches and the official file does not answer them at all. The built-in classification is not a knob this plug-in can win, so anything that trades the volume for the label is a regression, not a fix.
- The built-in experiment of ord198 was judged on half an instrument, and the other half is now printed. The unknown-property ring the plug-in writes on the shared control page records only calls that reached this plug-in and were refused; the audio server's own failing calls \(kind 4, against any object\) and VirtualAudio's C++ throws \(kind 8, with an image offset in place of the selector\) are recorded in a second ring on the same page -- package/ShengAudioAbi.h:81-86, SHENG\_AUDIO\_TRACE\_OFFSET 2560, SHENG\_AUDIO\_TRACE\_SLOTS 128, two words per entry, deduplicated by selector and info word -- and no kernel code had ever read it, so every boot discarded the one record that could say what the server did instead of setting the volume. package/DbyAudio.cpp grew traceRow\(\), called from paceFired\(\) beside serviceRow\(\) and unknownRow\(\): one \[apr\] tr= row per unread entry with the fourcc or offset spelled twice \(letters for a property, hex for a symbol address\), the object, the scope character, the kind and whether the call failed, with kind 0 skipped because a refused read already gets its unk= row and an answered read says nothing. The info word is packed by the plug-in as object in the top byte, the first byte of the scope under it, the kind in the low half and the failure in bit 1, which none of the kinds it uses occupies, so the decode masks 0xfffe rather than clearing bit 1 of the whole word. With that the next built-in boot names the layer instead of only the refusal count: kind 1 rows are writes reaching the control, kind 4 rows are the server failing to talk to something else, kind 8 rows are the routing layer throwing.
- The plug-in ships out of this repository and the ABI between the two halves is proved, not asserted: the macOS Data-seed workflow takes sheng\_repository with a pinned sheng\_commit as its plug-in source and hard-gates on shasum -a 256 kit/package/ShengAudioAbi.h = 9ef369877cfae3d2255129f7fdf332448b71300a0fc840d6522ec83e09754b52, which is byte-for-byte this repository's copy, so the kernel service and the user-space bundle cannot disagree about the control page or the two sample rings. The seed the board boots is that workflow's data-audio.dbr, grown from a recorded base, so the volume UUID F26D17C8-45E7-4C47-9AD9-A2A8C208E44A that configs/dby\_w09\_defconfig pins as CONFIG\_XNU\_OWNER\_DATA\_VOLUME\_UUID survives and a plug-in change stays payload-only \(kern\_exec.c:7993 looks the seed up by that string; a mismatch is the offline scratch Data mount failed: 2 screen\).
- The host checks call cc literally \(scripts/check-adsp-host.py:15\), and with Debian's gcc as cc every one of them fails in the compile rather than in a check; they pass when cc resolves to clang. Measured both ways on 2026-11-08.
- Carrying the donor's audio providers in the prelink roots is required for the closure to relocate correctly; it says nothing about audio working on kona.
- Audio is out of scope while the system cannot be operated: the panel and one input event come first.
- The amplifier silicon on this unit is TFA9874 in all four slots, read off hardware on 2026-11-06 rather than guessed from the three-BOM DTBO set: \[pa\] set=tfa9874 ... alive=0xf id=0x00000c74,0x00000c74,0x00000c74,0x00000c74 rc=0,0,0,0, then 42 registers pushed per slot and \[pa\] done set=tfa9874 invert=0 transfers=180 errors=8. The aw88262 branch returned rc=2 \(ADDR\_NACK\) on all four slots on both invert settings, and those 8 refusals are exactly the errors=8 that the done row counts, so the counter reconciles and the tree is a TI/NXP part, not an AW one. st= on those rows is the GeniI2c controller error\_status \(0x40000409 on every row, including the successful set\), not codec state -- reading it as device status is how a healthy bus looks broken. What still blocks audible sound is upstream of the PA, and the missing input is now located rather than declared absent: this unit's own whole-machine readback D:\\Windows\\Android\\华为\\matepad11\\QCTool\_ParReadback\_2026.03.18\_21.43.31.196\\images\\modem.img \(197132288 B, md5 704ead969fd17d23bf2b309254263fe9, raw FAT16\) carries /image/adsp.mdt plus adsp.b00..b18 - 22 files, 15061894 bytes - and /verinfo/ver\_info.txt names the build ADSP.HT.5.3-00618-SM8250-1.63882.3 \(2024-08-30 08:40:52, asic\), while dsp.img \(raw ext4, volume dsp\) holds the /adsp runtime libraries rather than the executable; a working copy is at D:\\Linux\\stock\\adsp\_unit\\. Saying earlier that the board had no adsp.mbn anywhere was an absence claim made without enumerating D:\\Windows, and fastboot fetch is refused here \(Device does not support fetch command\), so the readback is the only route to that input. What is missing is the AP side - and the way that was worded here before was an absence claim that did not enumerate the trees, so it is withdrawn: upstream does carry XNU subsystem-loader implementations. /home/wqsqw/upstream/sheng/package/ has AdspProbe.cpp \(688 lines\), AudioProbe.cpp, AdspFirmware.c, ShengGpr.c/h, ShengAdsp.h, ShengAudioReach.c/h and ShengAudioService.cpp plus QcomGlink.c, QcomMdt.c, QcomSmem.c and QcomSmp2p.c, with hal/ShengAudio.driver, the xnu patch zzyd-sheng-audio-addon-mount.patch and three host checks \(check-adsp-host.py, check-gpr-host.py, check-audioreach-host.py\); /home/wqsqw/upstream/alioth/package/ carries the same ADSP set minus the AudioReach/service half, and core/docs/porting/power.md section 2 documents the tiers - sheng-adsp=1 surveys what the boot stages left and writes nothing, =2 starts the DSP and brings up GLINK - while section 3 gives the audio layer order \(ShengGpr, ShengAudioReach, AudioProbe, the codec, the service, the HAL plug-in\). Neither of those boards is this one: both are SM8550 PAS \(kAdspBase 0x9ea00000, compatible qcom,sm8550-adsp-pas, SMEM 0x81d00000, RPMh ARC proxy rails lcx/lmx, MIAM mailbox at 0xc300000\), whereas this tablet's own kona.dtsi:4386 declares qcom,lpass@17300000 as qcom,pil-tz-generic with pas-id 1, smem-id 423, sysmon-id 1, ssctl-instance-id 0x14, firmware-name adsp, memory-region pil\_adsp\_mem = 0x8a100000 + 0x1d00000 \(no-map\), proxy rails L11A \(vdd\_cx\) and L4A \(vdd\_mx\) both at RPMH\_REGULATOR\_LEVEL\_TURBO over RPMH\_CXO\_CLK, proxy-timeout-ms 10000, mboxes &lt;&amp;qmp\_aop 0&gt; named adsp-pil, inputs &lt;&amp;pdc 6&gt; plus adsp\_smp2p\_in 0/2/1/3 and one smem-state \(force-stop\) on adsp\_smp2p\_out. Copying either kit's constants onto a PIL-TZ board would be invention, so the kit supplies the method and this machine's own Android source supplies the numbers - and the two do meet in the places that matter: the SMEM item ids coincide \(kona-smp2p.dtsi:9 gives qcom,smem = &lt;443&gt;, &lt;429&gt; for the SMP2P items and qcom,smem-id = &lt;423&gt; for the subsystem failure reason, the same three numbers sheng hard-codes\), and the decode formats are generation-independent - the partition table sits in SMEM's last 4 KiB \(smem.c:1055\) with magic $TOC, version 1 and 48-byte entries; a partition header is 32 bytes with magic $PRT; a private item is a 16-byte header carrying the 0xa5a5 canary, with next = here + 16 + padding\_hdr + size; the SMP2P item is a $SMP header plus sixteen name/value pairs \(smp2p.c:66-88\); and cmd-db is version, magic &\#123;db,30,03,0c&\#125;, then 16-byte rsc\_hdr slots \(cmd-db.c:53-98\). f2-payload-175 ships power.md's first tier - the survey, not the loader - inside package/DbySmartPA.cpp under the dby-pa argument that is already shipped, rather than as a new boot argument: the command line sits at 998 of the 1000-byte gate and no functional argument was going to be deleted to host a survey. It maps SMEM 0x80900000+0x200000, cmd-db 0x80860000+0x20000 and the 16 KiB head of pil\_adsp\_mem 0x8a100000, decodes the SMEM header, the partition table and exactly the two partitions qcom\_smem\_get\(\) would consult \(the host-0-with-host-2 peer partition and the 0xfffe/0xfffe global one\), reads items 443, 429 and 423 including the failure-reason string, and counts non-zero words in the PIL region. It writes nothing: no window is written, no rail is voted, no clock is touched. Two windows are left alone on purpose, and that is a decision rather than an oversight - LPASS CSR 0x17300000 is pil-tz's own register block and no source in this tree says a read with the ADSP unpowered cannot hang the bus, so a working boot is not a price worth paying for one more number; and IPCC 0x408000 has no register semantics in this kernel's source, so a read back would be raw data with no vendor meaning. The rows settle next round's fork by themselves: an all-zero PIL region with no SMP2P item means the boot stages left no ADSP running and the work is subsys-pil-tz.c's load sequence plus the RPMh proxy votes, while a loaded region and live SMP2P bits mean the loader can be skipped and the audio reach layer can start against a DSP that is already up.
- The volume slider cannot reach anything until an audio server plug-in exists in user space, and the official carrier for one is the Data seed, not the boot image. The donor ships its HAL the way core ships its Metal plug-in: a directory inside the writable container that the kernel union-mounts over a system path \(docs/zh/porting/gpu.md:95-99 with scripts/add-gpu-plugin-data.py\). It is one of the four mounts in kern\_exec.c's boot-time addon block, gated by the boot argument sheng-gpu-addon=1 at kern\_exec.c:7649, and the gate is entered with no addon blob at all because native\_gpu\_addon\_install\(\) returns at its first step without a blob \(:7405-7407, the NGPUADD2 check would only be at :7410\) while the four native\_gpu\_addon\_mount\(\) calls run regardless -- so the blob route \(scripts/make-gpu-addon.py, Payloads/kernel.macho.gpuaddon\) is not needed and the loader is not touched. Audio is the fourth mount: window 0xa00, source /private/var/ngpu/audio, point /System/Library/Audio/Plug-Ins/HAL, and the union is only accepted after comparing BuiltinAudioPlugin.driver against ShengAudio.driver/Info.plist; its counters are native\_gpu\_addon4\_stage and native\_gpu\_addon4\_status, and the BootProgress A row now prints them as mount4=stage/status \(the two weak symbols are defined in package/BootProgressStubs.c so the archive links before the kernel carries them\). What else the same gate buys is part of the decision, not a side note: that region of kern\_exec.c also runs native\_cryptex\_os\_view \(the /private/preboot union plus the /System and /usr binds, reported as \[cryptex os\]\), native\_gestalt\_cache\_drop and native\_ls\_store\_drop, so turning on the audio mount also rebuilds the launchservices store once. The argument took the slot left by boot-ui-focus=launchd, which BootProcessProbe.c:105 does not need because launchd already sits in slot 0 of its own default table; measured after the swap, 49 arguments and 992 of the 1000 bytes core/scripts/unixnu/payload.py:35 allows.
- Staging a plug-in into an existing seed keeps the volume UUID and so costs no kernel rebuild \(docs/guide/userdata.md\), but this board has no growable seed left: the macOS seed workflow keeps artifacts for one day, so the next seed is a fresh fixture, and scripts/prepare-owner-data-fixture.py takes no volume-uuid option -- a fresh fixture means a new UUID, which the kernel pins as CONFIG\_XNU\_OWNER\_DATA\_VOLUME\_UUID \(configs/dby\_w09\_defconfig, copied into build/xnu/owner-data-volume.h by scripts/build-xnu-4k-baseline.sh and looked up by that exact string at kern\_exec.c:7993, where a miss is the panic offline scratch Data mount failed: 2\). That coupling, not preference, fixes the order of this round: cloud seed first, then its UUID into the defconfig with ./unixnu defconfig re-run, then the kernel, then the payload -- and the plug-in CDHash into the owner trust cache in the same payload, because an ad hoc bundle the cache does not name is refused before the audio server ever loads it, which would read back as a working mount and no device.
- ord206 measured the pump and the audio server on two different clocks: at the plug-in's first client write its out\_written stood at 4426164 frames while the ladder had issued 3727360, so 14.6 s -- ten turns of a 1.37 s ring -- had been cleared unread, and the distance kept growing while a stream was stopped. package/DbyAudio.cpp now derives the read position from out\_written minus the 300 ms lead the control page itself publishes \(kRingLagFrames\), re-locks ringBase whenever the skew exceeds half a ring, and prints the phase as resync= and gap=.
- A pace timer alone cannot feed the ASM: four 1024-frame regions at 48 kHz hold 85 ms of sound and the tick is 100 ms, so 15 % of every round is missing by construction. ord207 measured exactly that ratio -- plug-in cursor 218112 frames against 184320 issued, 0.845. The refill now fires on the write-done event the way the vendor feeder does \(q6asm-dai.c:186-212\), behind a wall-clock cap the vendor does not need: issued frames may not run more than the four regions in flight past \(mach\_absolute\_time\(\) - playAt\) / \(ticks\_per\_frame\_q32 &gt;&gt; 32\), 400 host ticks per frame here.
- The silence was one bit. apr\_audio-v2.h:7214 spells the flags field of ASM\_DATA\_CMD\_WRITE\_V2 as bit 31 = 1 for a valid timestamp and 0 for an invalid one, and both drivers write a session-less PCM stream as the caller's NO\_TIMESTAMP \(0xFF00\) -- q6asm.c:9693-9699 in this SoC's own tree, mainline q6asm.c:1216-1219 in the same branch -- which the encoder emits as 0x0000FF00. Eight rounds sent 0x80000000 with the timestamp left at zero, so the ADSP believed every buffer was due at 0 us and returned each one unrung: that is ord208's 44x write-done rate, and it was never a starved pump. package/ShengApr.h now names the value APR\_ASM\_NO\_TIMESTAMP and apr\_asm\_write\(\) sets bit 31 only for a caller that really supplies a timestamp; payload-ord209.img is audible from the built-in speaker and the slider follows it.
- A rising counter is not evidence until its increment condition is quoted. derr= grew one per write-done event and read as a failing link, but asm\_data\_event\_write\_done\_v2 \(apr\_audio-v2.h:7351, opcode ASM\_DATA\_EVENT\_WRITE\_DONE\_V2 0x00010D99\) carries buffer address low word, buffer address high word, mem\_map\_handle and status -- the status at payload+12 -- while package/ShengApr.c read payload+4, which is the high word this driver always sets to 1 through kSidTag. The count measured my offset, not the DSP, and the next round moves it.

### 完成条件

- A playback path is established and audible on hardware.

### 当前范围

- The DSP loader is not the gap: package/AdspProbe.cpp is 696 lines and carries the AP side itself - the QCOM\_SCM\_SVC\_PIL calls at :275, QCOM\_SCM\_PAS\_MEM\_SETUP at :337, qcom\_mdt\_parse, qcom\_mdt\_metadata and qcom\_mdt\_place at :322, :332 and :351, the RPMh proxy votes under its own header at :233, the AOSS load\_state adsp message at :566 and the SMP2P and GLINK bring-up - and build-gop-legacy-display.py:232-233 archives the protocol cores with it \(QcomMdt, FatVolume, QcomQrtr, ShengQrtr, QcomSmem, QcomSmp2p, QcomGlink, QcomQmp, QcomRpmh, ShengGpr, ShengAudioReach, ShengCs35l43, ShengApr\). The survey-versus-loader fork this entry used to describe is therefore closed. What is genuinely missing: no hardware readout of native\_adsp\_stats is recorded in this repository, so the loader has repo evidence as compiled code but not as a measured stage; the SM8550 codec half is deliberately out of the link \(package/AudioProbe.cpp votes another machine's GCC registers and TLMM pins\), so ShengCs35l43.c is archived yet is not this unit's amplifier either; and the AFE, ADM and ASM ladder in package/DbyAudio.cpp has no accepted audible result. What is not missing is the firmware input - adsp.mdt plus adsp.b00..b18 are read off this unit's modem.img and inventoried above.
- Nothing beyond the TFA9874 INIT\_CHIP tables is written to any codec, and the survey tier writes nothing at all; LPASS CSR and IPCC are unread by decision, not by omission.

### 下一步

- Read the stage ladder the loader already publishes - native\_adsp\_stats\[0\] names the step that failed when negative - together with the DbyAudio ladder rows, then carry the sample path the rest of the way: the ASM and AFE/PRI-TDM open that no board result has confirmed yet.
- Flash the staged seed with the kernel rebuilt for its UUID and the trust cache that names the plug-in CDHash, then read mount4=stage/status on the A row and move the slider: non-zero means the union took and the audio server saw a second HAL, while silence past that point is the ASM and PRI TDM playback half, not the mount.

### 证据

- `source`: [the rx\_open branch assigns rcid only from the peer OPEN and acks a remote-initiated channel there; the OPEN\_ACK branch resolves by lcid and completes open\_acked; every unmatched message records its cid and command](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/package/QcomGlink.c)
- `source`: [kAudioDevicePropertyTransportType answers kAudioDeviceTransportTypeBuiltIn for the device object; the name strings are unchanged, so a refusal is visible as a classification problem and not as a missing device](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/hal/ShengAudioPlugIn.c)
- `host`: [both passes return RC=0; kernel.macho sha256 aa7978de545ceae146e3b6e58a4a2480a954c58068e0d847ec72e91dd9f79fb4 defines \_sheng\_audio\_service\_start, \_native\_audio\_service, \_native\_audio\_clock and \_\_GLOBAL\_\_sub\_I\_ShengAudioService.cpp, ShengAudioService.late.o is one of the 25 members of libNativeLegacyDisplay.late.a, and the image lists no undefined symbol at all](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/scripts/build-gop-legacy-display.py)
  Command: <code>./unixnu defconfig dby_w09_defconfig -D &lt;device repository&gt;, then ./unixnu build kernel -D &lt;device repository&gt; --jobs 4 twice, then llvm-nm out/dby-w09/ipados-17.7.11-21H461/dby_w09/kernel/kernel.macho</code>. Revision: `baca7ebada2ee1939fbebf2fd0b14a5acb71879a`.
- `host`: [PASS qcom adsp cores: 4184 checks](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/scripts/check-adsp-host.py)
  Command: <code>PATH with cc resolving to clang; python3 scripts/check-adsp-host.py</code>. Revision: `baca7ebada2ee1939fbebf2fd0b14a5acb71879a`.
- `host`: [PASS apr: core handshake, AFE v1/v2 parameters, TDM ladder, ADM route, ASM stream, answers, decoder](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/scripts/check-apr-host.py)
  Command: <code>PATH with cc resolving to clang; python3 scripts/check-apr-host.py</code>. Revision: `baca7ebada2ee1939fbebf2fd0b14a5acb71879a`.
- `host`: [PASS audioreach: 182 checks](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/scripts/check-audioreach-host.py)
  Command: <code>PATH with cc resolving to clang; python3 scripts/check-audioreach-host.py</code>. Revision: `baca7ebada2ee1939fbebf2fd0b14a5acb71879a`.
- `host`: [PASS qrtr and service locator: 41 checks](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/scripts/check-qrtr-host.py)
  Command: <code>PATH with cc resolving to clang; python3 scripts/check-qrtr-host.py</code>. Revision: `baca7ebada2ee1939fbebf2fd0b14a5acb71879a`.
- `device`: [FAIL the built-in classification gives the volume slider nothing to talk to: \[apr\] os=1000 want=0 sets=0 opens=1 maps=3 played=1548288 late=0 holes=0, and no \[apr\] unk= row at all, so the audio server streamed through the plug-in device without ever setting its volume or asking a property it refused. No panic: one kprintf initialized and one Firehose line in the replayed ring, DbyBattery \#1 to \#53 in the same boot](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/hal/ShengAudioPlugIn.c)
  Command: <code>boot of payload-ord198.img (preload, payload_sha256 7fa555d782a1cd761369ee4189af529b68ae1c6dfe2bb37dd3b51a402db16a20), COM4 read for 45 s at 2026-11-08 20:38 with DTR/RTS set after the boot</code>. Revision: `52682b2dce38d1cc95893dd7debc53b9fbbeba51`.
- `source`: [one spelling of that word is left in the delivered binary and it is not the device name: the output stream's kAudioObjectPropertyName, which is the label a HAL device without Apple port descriptions offers for its route. The UIDs are the other candidate -- iPadOS keys per-device settings by device UID and kDeviceUID never changed, so a cached name would survive a rename. Both change in this cycle so the panel answers which](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/hal/ShengAudioPlugIn.c)
  Command: <code>grep -n 'REPLY_STR("Speaker")' hal/ShengAudioPlugIn.c after the device and model name were renamed (ord199)</code>. Revision: `75b89611fb7068e3ec75ab87537905ff5d0a6a93`.
- `device`: [PASS the volume control path is reachable on the transport the donor record names: \[apr\] os=1000 want=0 sets=0 at boot, then \[apr\] os=225 want=3 sets=1 and \[apr\] os=225 want=0 sets=1 played=3653632 late=0 holes=10, so the audio server wrote this device's volume \(1000 to 225 milli\) instead of only streaming through it. The one refused property is cfsz \(\[apr\] unk=0 cfsz obj=2 sc=g\), which EVB10 also leaves unanswered while keeping the device. No regression in the other boot verdicts: the same 45 arguments as ord198, no panic row, DbyBattery \#1 to \#49 in one continuous boot](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/hal/ShengAudioPlugIn.c)
  Command: <code>boot of payload-ord199.img (fastboot flash preload, payload_sha256 5c16a21681adbe44df14d4f22f9fba773b1f0b0acea5f8f987e5e0f297876336, seed run #22 42483176062 with plug-in CDHash 5a42f10fbab722a83ffde517a5bd92c1e4dca0f3), COM4 read for 60 s at 2026-11-08 21:13 with DTR/RTS set after the boot</code>. Revision: `75b89611fb7068e3ec75ab87537905ff5d0a6a93`.
- `device`: [the panel flicker that starts at the Apple logo is the supply, not board code: on the computer port the fuel gauge answers soc=0 mv=2816 with the input limit at 500 mA \(icl=500 want=500 ceiling=500 aicl0=500\) and the tablet later drops off the USB bus entirely with no panic row on the console, which is a power loss and not a hang; on a wall charger the same image boots without flicker, so no display or backlight code was touched \(dby-bl=1 stays\)](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/porting.toml)
  Command: <code>the same boot on the PC's USB port, then the same image on a wall charger</code>. Revision: `52682b2dce38d1cc95893dd7debc53b9fbbeba51`.
- `host`: [PASS GPR: 37 checks](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/scripts/check-gpr-host.py)
  Command: <code>PATH with cc resolving to clang; python3 scripts/check-gpr-host.py</code>. Revision: `baca7ebada2ee1939fbebf2fd0b14a5acb71879a`.
- `host`: [AudioServerPlugIn.h pulls in CoreAudioTypes.h, AudioHardwareBase.h and CoreFoundation.h only; the Port-spelled names across those five headers are the two DisplayPort fourccs and nothing else; the device-level volume selectors are absent from both headers a plug-in can include, appearing only in AudioHardware.h:1248-1252 where AudioHardware.h:994-1022 assigns each to an AudioVolumeControl; the transfer-function selectors are AudioHardwareDeprecated.h:115 \('lctf'\) and :505 \('vctf'\). No port, route or device-volume surface is reachable from a HAL plug-in, so the only classification knob left is the transport answer itself](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/hal/ShengAudioPlugIn.c)
  Command: <code>grep '^#include' AudioServerPlugIn.h; grep -ohE 'kAudio[A-Za-z0-9]*Port[A-Za-z0-9]*' AudioServerPlugIn.h AudioHardwareBase.h AudioHardwareDeprecated.h AudioHardwarePropertyData.h CoreAudioTypes.h | sort -u; grep -cE 'volm|vold|vdb#|v2db|db2v' AudioHardwareBase.h AudioServerPlugIn.h; grep -nE 'vctf|lctf' AudioHardwareDeprecated.h</code>. Revision: `11650d08c0b6caf87d1eb294715d5d5d7b3a2334`.
- `device`: [the rename arrived and the classification did not: the panel reads MatePad Speaker where ord199 read speaker, which settles that the output stream name is the label the route list shows, and the device is still listed as external because that build answers kAudioDeviceTransportTypeThunderbolt; the \[apr\] os= rows still count the server writing this device's volume, so the control path is alive on the external transport and the built-in classification is the remaining half](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/hal/ShengAudioPlugIn.c)
  Command: <code>boot of payload-ord200.img (fastboot flash preload, payload_sha256 e65236fd13c61a629d9f141194657681fc4da92994cab6f01e726c390eb5745c), panel read by hand, COM4 read for 60 s with DTR/RTS set after the boot</code>. Revision: `11650d08c0b6caf87d1eb294715d5d5d7b3a2334`.
- `source`: [two hits, the definition and the call from paceFired\(\), so the ring the plug-in has filled on every boot of this experiment is read for the first time and its server-side kinds reach the console beside the unk= rows](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/package/DbyAudio.cpp)
  Command: <code>grep -n 'traceRow' package/DbyAudio.cpp</code>. Revision: `11650d08c0b6caf87d1eb294715d5d5d7b3a2334`.
- `device`: [PASS the built-in speakers sound and the slider follows them: the \[apr\] rows advance at real time \(26.3 s of audio across 21.5 s of wall clock\), played= and wrot= stay within 31072 frames \(0.6 s\) of each other, peak= holds 9787 and late= stays 0, and the 44x write-done spin the same ladder showed one round earlier is gone.](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/package/ShengApr.c)
  Command: <code>host platform-tools fastboot flash preload payload-ord209.img (sha256 592c632b74abcf0d6e13929257fc18976407f7c9203310031e9f65f745d10db3), then COM4 at 115200 with DtrEnable and RtsEnable held by the reader</code>. Revision: `e392957e512557a4f534167dd707719a789fd52f`.

## 电源 {#power}

`device-verified`

### 硬件与依赖

- ApplePMGR from the donor kernelcache \(original \_\_TEXT\_EXEC hash 2c433279d004…\).
- SM8250 PMGR/regulator contract as reached by the shared board scripts.
- The payload's native-ufs-root gate, which demands exactly one sheng-pmgr=2 and a linked \_sheng\_pmgr\_run.

### 配置

- \[kernel\] archives runs scripts/build-platform-power.py after the driver recipes so the audit reads the original kernelcache from the pinned cache.
- \[payload\] kernel\_args set sheng-pmgr=2.

### 操作步骤

- Build the kernel and let the payload build assert the PMGR gate; then boot and read whether AMFI's PMGR dependency holds on hardware.
- Record the contract audit output \(extent hashes\) with the build, because a mismatch is upstream refusing the input rather than a local error to bypass.

### 开发经验

- ord216 settled both of the torch rules that ord214 had wrong, on hardware. \[V\] leds-qpnp-flash-v2.c reads STATUS1 and STATUS2 only from its led-fault-irq handler \(1992-2013\), and every recorded board DT places that interrupt at INT\_RT\_STS bit 0, so a STATUS1 seen while the line is clear is a ramp-up artefact and not a fault: DbyTorchCore.c fault\_of\(\) answers nothing unless DBT\_V\_LED\_FAULT is set, lamp\_fault\(\) puts the LED away with the accepted switch\_disable ladder and leaves the write gate open, and the gate that closes until reboot is reserved for what actually loses the bus \(a refusal, a failed read-back, an spmi error\). The board row from the same day, in backticks: FAULT vph-droop rc=-5 off=0 s1=00 s2=10 rt=01 reg=0x43 status=0x1 refused=0: off, and the next request lights it again, and the request after it lit. ord214-s own reading is a host fixture now: STATUS1 0x01 with INT\_RT\_STS 0x90 returns DBT\_OK with faults == 0, Test/core.c.
- The PMGR bridge is still the accepted sheng implementation: the second \`build kernel\` pass links the real \`\_sheng\_pmgr\_run\` and \`./unixnu build payload\` for \`09c3aad6…\` accepted it on this board, which is the gate that rejects a kernel without that symbol.
- The AMFI/PMGR pairing is a hard gate with a clear failure: without ApplePMGR in the roots the contract audit cannot take its extent and the platform-power archive is never produced, so the payload refuses the image.
- Regulator votes themselves are not yet modelled for kona; the verified part is the contract and the payload gate, which is why this area is host-verified rather than device-verified.
- The battery producer is package/DbyBattery.cpp plus package/BatteryProbe.cpp: the official alioth producer ABI \(an IOPMPowerSource provider over the 16-slot native\_battery\_stats\) with the transport replaced, because this board has no ADSP stack in this tree while its stock DTBO describes the gauge as qcom,fg-gen4 and the charger as qcom,qpnp-smb5 on SPMI -- so it reads the arbiter-s observer engine at 0x0e600000 directly, the same channel DbyTouch runs on. It is read-only by construction: the chnls window is never mapped, no PMIC configuration register is written, no charger or bark/bite path is touched, and a value that cannot be read stays -1 / unknown rather than 0. What was wrong in the round before this one is the reporting, not the transport: all thirteen rows used IOLog, which this console does not mirror, and BatteryProbe returned silently from both of its early gates, so a boot that never parsed dby-battery, a boot whose module registration failed \(-10/-11\) and a boot whose PMIC never answered were three names for the same empty screen. Every branch now prints through kprintf and stage is latched into native\_battery\_stats\[0\] with the upstream sign convention. A row from this driver is on the console now: the 2026-11-06 capture carries the arbiter census, one published dictionary and 84 cycle rows, which is what turned the two complaints about the battery line into measured defects rather than guesses.
- Both complaints are inside that one capture and both are this file, not the PMIC. The percentage that differs from boot to boot is the transport latch: rows \#1-\#61 answered op=1 tx=14 clean=14 to=0 err=0, cycle \#62 issued one transaction and took one error bit, and the operation-form ladder then latched for the whole boot - rows \#63 through \#84 carry tx=0 clean=0 to=0 with every field reason 2, so for 22 more cycles no transaction was even attempted. After that the dictionary the UI shows is frozen at whatever the last good cycle published, and where a boot freezes is wherever its own first error lands: that is the 「每次开机都不一样」. The latch is gone - a silent engine now ends only that cycle, prints which cycle it ended, and the next cycle re-walks the ladder.
- The charging icon that dies on a brightness slide was a charging test this tablet's own kernel does not make. The branch that is compiled here is Huawei's smblib\_get\_prop\_batt\_status\(\) \(smb5-lib.c:2111-2162; it is Huawei's because merge\_kona\_defconfig:5912 sets CONFIG\_HUAWEI\_POWER\_EMBEDDED\_ISOLATION=y\): a disjunction of the direct-charge stage window, the wireless adapter type and \(usb\_present &amp;&amp; \!usb\_icl\_change\_irq\_enabled &amp;&amp; \!input\_suspend\), each then rewritten to NOT\_CHARGING by health COLD, OVERHEAT or OVERVOLTAGE - and the SMB5 3-bit regulation stage is not in it. What the port tested was stage in \[Trickle..Taper\], and a load step walks that stage through INHIBIT or PAUSE for a sample at a time, so the icon switched off while the cell was still taking current. IsCharging now reads the vendor's own inputs \(USBIN\_PLUGIN\_RT\_STS bit 4 for presence; POWER\_PATH\_STATUS USE\_USBIN bit 4 together with VALID\_INPUT\_POWER\_SOURCE\_STS bit 0 for usb\_online; CHARGING\_ENABLE\_CMD; STATUS\_7 TOO\_COLD and TOO\_HOT\). One wording correction recorded here because the first version of this sentence conflated two registers: the term the status rule subtracts is chg-&gt;input\_suspend, which is the driver's cache of USBIN\_CMD\_IL bit 0 - smblib\_get\_usb\_suspend\(\) reads that bit and smblib\_set\_usb\_suspend\(\) is its only writer \(smb5-lib.c:418-431, 770-790\) - not of POWER\_PATH\_STATUS bit 6, which is only the echo of the vote and is kept in the row as sus=. The stage keeps the one use the vendor gives it: saying the cell is full.
- Two of the rule's terms needed a decision rather than a transcription, and both are recorded in the source. usb\_icl\_change\_irq\_enabled is read as false, not dropped: SMB5's smblib\_set\_usb\_suspend\(\) votes icl\_irq\_disable\_votable \(smb5-lib.c:767-785\) and the only writer of the field is a HIZ\_MODE setter \(qpnp-smb5.c:2322\), so false is the vendor's own steady state and the third term is the live path for a wired charge. OVERVOLTAGE is left out, because smblib\_get\_prop\_batt\_health\(\) asserts it only after comparing the gauge VOLTAGE\_NOW with the float-voltage votable plus 40 mV \(smb5-lib.c:2413-2429\); honouring the raw BAT\_OV bit alone would claim a state the vendor itself refuses to. COLD and OVERHEAT need nothing but STATUS\_7 and both are read. Reporting moved to upstream's shape: one publish per cycle end, a per-field reason byte, and every field that did not answer named in the row, so a missing number and a zero cannot be confused by a reader.
- f2-payload-168 answered both battery defects on hardware and then did not reach the lock screen, and the two halves are recorded apart. What the rows proved: the first ten cycles each carried why=00000000000, meaning all eleven fields answered, with tx=16 clean=16 to=0 err=0, soc=59 mv=3887 on the first cycle and soc=58 mv=3846 ma=+422 by the tenth, chg=1 the whole way and full=0 - so the vendor status rule and the measured current agree, which the stage-window rule never managed. What the same flash did not survive: the panel stayed on the Apple logo - and the 163-versus-167 touch comparison built on top of that was invalid from the start, because the argument above was missing from every payload of the day, so the two images could not differ in the way I claimed and no such A/B was ever owed a device boot. What is nevertheless measured and stands: the accepted touch contract is intact, git diff --stat e61237a -- package/DbyTouch/ is empty, so the current 4988-line DbyTouch.cpp is byte-identical to the accepted commit. The friend's kit is the source of the touch \*approach\* only; this device is maintained in this repo, and its history is the baseline - the 1213-line gap against his 01-src drop is that drop being a partial earlier snapshot, not leftover edits of mine.
- The poll bound is the part of this transport that was never the vendor-s shape. spmi-pmic-arb.c decrements PMIC\_ARB\_TIMEOUT\_US once per readl\_relaxed\(\) with udelay\(1\) between the reads, which is one millisecond of polling per transaction; this file spun up to 200000 uncached reads on the same status word, on the default IOKit work loop, because it had copied the count from DbyTouch-s boot path where it is a one-shot. On a silent engine that is hundreds of milliseconds per cycle of a loop every driver shares.
- The other half of the charge complaint - the icon that stays after the cable comes out - is a defect on the presence axis, not the charging axis, and the enable bit has nothing to do with it: CHARGING\_ENABLE\_CMD is a configuration mirror the firmware leaves set, so it can say inhibited but can never say charging. Two things made the icon survive an unplug. First, publish\(\) gated setExternalConnected, setExternalChargeCapable and setIsCharging on those reads having answered, so a cycle whose transactions died republished nothing and the last true value stayed in the registry for the rest of the boot; upstream decodes an absent answer as false \(ShengBattmgr.c:152-159\) and publishes unconditionally \(ShengBattery.cpp:95-99,107\), and the three booleans now do the same, with charging ANDed behind presence and the unknown-is-not-zero rule kept for the numbers only. Second, and this is the state userland actually reads: IOPMrootDomain::acAdaptorConnected is initialised true \(IOPMrootDomain.cpp:1667\) and its only writer is the AC branch of handlePowerNotification\(\) \(:8459-8472\), which decodes presence as the message carrying kIOPMSetValue \(:8460; IOPMPrivate.h:156 and :160 for the two constants\) - and that branch is reached only through receivePowerNotification\(\) \(:8293-8315\), which queues the work onto pmPowerStateQueue \(:8311\) instead of running it on the caller thread. Nothing on this board had ever called it, and updateStatus\(\) cannot carry the state either: it writes the registry and sends kIOPMMessageBatteryStatusHasChanged \(IOPMPowerSource.cpp:177-216, the message at :211\), which has no consumer anywhere in the pinned XNU outside its own definition at IOPM.h:865. So the root domain kept believing AC was attached and the status bar repainted only when an unrelated event invalidated it - which is precisely the observed behaviour of the mark disappearing on a brightness slide. On every presence edge now, publish\(\) calls getPMRootDomain\(\)-&gt;receivePowerNotification\(kIOPMSetACAdaptorConnected \| \(attached ? kIOPMSetValue : 0\)\) once, the same push Apple uses for its own services from IOUserServer::powerSourceChanged\(\) \(IOUserServer.cpp:5496-5509, via getSystemStateNotificationService\(\), assigned during setPlatform\(\) at IOService.cpp:1600 and dereferenced unguarded by Apple at IOUserServer.cpp:7017\). post\_sys\_powersource\(\) was checked as an alternative route and rejected: it compiles to a no-op on iOS \(vm\_shared\_region.c:4009-4019\).
- The lag the user measured on the 173 boot - 「终于正常了，但是反应很迟缓，得等好一会才正确反馈」 - says the presence fix landed and the cadence did not: it is the timer, not the transport. Upstream never ran one timer for this. ShengBattery.cpp:47 keeps kRequestMs = 2000 and kRefreshMs = 60000 with kSlowEvery = 10, and sheng\_battmgr\_refresh\(&amp;bm, ++refreshes % kSlowEvery == 0\) picks which field set a cycle reads, publishing only at BmCycleDone. This file carried a single IOTimerEventSource at 60 s, so a plug or unplug edge could wait a whole cycle before the dictionary and the root-domain push moved. 175 splits it the upstream way: a 2 s status timer reads only what chargingOf\(\) and externalOf\(\) consume - Current, Plug \(USBIN\_PLUGIN\_RT\_STS\), Online/Suspend \(POWER\_PATH\_STATUS\), USBIN\_CMD\_IL, Enable, the STATUS\_7 health bits and the regulation stage - and republishes every cycle; the 60 s timer keeps the slow tier, meaning the capacity and voltage reads, the four charger-limit diagnosis bytes and the battery-presence fields, which now carry a distinct reason byte 7 \(kWhySlowOnly\) so a fast row can never be misread as thirteen timeouts. The three numeric stats slots are written only by a cycle that actually holds the field, which is what stopped native\_battery\_stats oscillating to -1 between tiers. Why this is a timer and not an interrupt is stated rather than glossed: the vendor does not poll either - qpnp-smb5.c reacts on the SMB5 usbin\_change\_pend interrupts, and the only poll-shaped numbers in that tree are deglitches \(OTG\_DEFAULT\_DEGLITCH\_TIME\_MS 50, DEFAULT\_FCC\_STEP\_UPDATE\_DELAY\_MS 1000, bc12 500/1200 ms\), so no 2 s Android interval is being copied here. This service has no PMIC interrupt path at all \(native\_battery\_stats\[9\] = 0 and the census row's irq-owner field say the same\), so the 2 s tier is the honest stand-in until an SPI is attached through armcpu\_spi\_attach\(\) \(.local-armcpu/ArmCpu.cpp:877\); the interval itself is upstream's number, not a guessed one.
- The charge-icon complaint is now closed at the panel rather than on the console, and the boot that decides it is payload-ord209.img \(sha256 592c632b74abcf0d...\), not 168, 171, 173 or 174: that image carries the presence-first publish, the vendor status rule and the 2 s/60 s cadence split in the same build whose \[apr\] rows prove the audio ladder at real time, so the four booleans the status bar reads were exercised together for the first time. The owner-s read of this boot is that the charging mark behaves. What the transport still costs is stated once and not papered over: no PMIC interrupt is attached here \(native\_battery\_stats\[9\] = 0\), so a cable edge is published up to 2 s after it happens, where the vendor would react on usbin\_change\_pend immediately.
- The flashlight producer is \`package/DbyTorch/\` and it reaches the kernel the way every other board archive does, so its first proof is a symbol table and not a boot: \`scripts/build-dby-torch.py\` builds \`build/dby-torch/libDbyTorch.a\` \(256216 B\), \`board.toml\` gives it a \`\[kernel\] archives\` slot after the driver recipes, \`configs/dby\_w09\_defconfig:130\` appends it to \`CONFIG\_XNU\_EXTRA\_LD\_ARCHIVES\`, and \`package/BootProgress.c:116\` names \`dby\_torch\_start\(\)\` as a strong reference so the plain non-force\_load path pulls it in. On kernel \`05d697b0be1471b8\`: \`llvm-nm --extern-only\` shows \`dbt\_spmi\_read/open/discover/allowed/write/reset\_interlock/emergency\_stop\`, \`dbt\_config\_make/test\_ms/current\_law/level\_ma\`, \`dbt\_core\_init/set/poll/export\` and the five \`dby\_torch\_\*\` entry points all defined.
- The transport is the one the battery already runs on, and the write side is fenced by a gate rather than by intent. \`DbyTorchSpmi.c:107 dbt\_spmi\_allowed\(\)\` is the only path by which a write reaches the PM8150L flash block, \`:145\` refuses anything the whitelist does not cover, \`:163\` drops the interlock when the LED mask reads back zero, and \`:178 dbt\_spmi\_emergency\_stop\(\)\` is the single stop the header permits \(\`DbyTorchSpmi.h:77\`: \`EN\_LED\_CTRL\` to 0 for this board-s led-mask with \`MOD\_CTRL\` off\), the rule itself stated at \`DbyTorchSpmi.h:53\` -- a channel may be switched on only once the gate has written every field it owns. \`scripts/check-dby-torch-host.py\` reports PASS on the strict compile of the two portable sources, 9045 spmi checks against a model of the v5 arbiter and the flash block \(discovery, the owned mapping, both ladders, the whitelist over all 256 bytes, read-modify-write, failures, the one stop\), 1580100 core checks \(the boot arguments- configuration, the current law with the PM8150L erratum, dry run, refusals before any write, the vendor on and off sequences, every level of 300 mA, the 5 minute limit, the thermal derate, every fault bit\) and PASS args over the four boot arguments -- then prints its own limit: no --tree, so it built no kernel archive. Host checks do not establish that the LED lights.
- The flashlight of iOS is \`package/DbyTorch/DbyTorchIos.&\#123;h,c,cpp&\#125;\` and it is a publication and not a script hook: when \`dby-ti=1\` and \`dby-torch=1\` are both parsed on the same line the kernel registers the \`AppleH6CamIn\` service, its mediaserverd-only user client and the \`flash\` property of \`IODeviceTree:/product/camera\` - the property \`MGGetBoolAnswer\("camera-flash"\)\` answers, which is the only thing that makes a Control Center toggle exist at all. It refuses when either argument is missing, when \`dby-torch\` is not 1, or when the mount below does not show the plug-in, because a button that does nothing is the failure the mother-s own gate is written against. \`scripts/check-dby-torch-host.py --tree\` compiles and links it on 2026-11-09: 5 objects, 25 entry points, 239 kernel imports each defined by that tree-s own linked kernel, the class initializer staged out of \`\_\_mod\_init\_func\` with \`llvm-objcopy --remove-section\` plus \`--globalize-symbol=...\_\_GLOBAL\_\_sub\_I\_DbyTorchIos.cpp\`, \`\_kprintf\` present, \`\_IOLog\` absent, \`LC\_BUILD\_VERSION\` iOS 17. The tree-s \*last linked\* kernel does not carry it: \`build/xnu/ios-obj/mach.development.bcm2837\` defines 23 \`\_dby\_torch\|\_dbt\_\` rows - 20 extern entry points - and no glue symbol at all, because that kernel was linked before \`DbyTorchIos.\*\` existed. Both numbers are measured; the 24 this record carried was one of my own inflations.
- The mount that verdict reads is a fifth \`native\_gpu\_addon\_mount\(\)\` in \`native\_gpu\_addon\_prepare\(\)\`, added by \`patches/xnu/zze-dby-torch-media-mount.patch\` with \`patches/xnu/series-torch\`: source \`/private/var/ngpu/mediacapture\` \(the directory the Data seed delivers, the same carrier as the audio HAL\), point \`/System/Library/MediaCapture\`, \`visible\` that point itself and \`own\` \`/System/Library/MediaCapture/H6ISP.mediacapture\`. The sealed root has no entry at that point, so there is nothing there to prove the lower layer with and the directory stands for it - verbatim the mother-s shape at \`refer/Pagani/patches/xnu/phone-torch-overlay.patch\`, kept as one argument \(\`dby\_torch\_ios\_commit\(int plugin\_visible\)\`\) rather than widened into something the mother does not have, with this tree-s counter numbering and this board-s argument names. The window is \`0xe00\`, which is arithmetic and not a guess: \`kern\_exec.c:8193\` allocates the scratch as one \`map\_page\_size\` \(16 KiB\), a mount consumes its window plus \`0x130\`, the four existing mounts take \`0x400\`, \`0x600\`, \`0x800\` and \`0xa00\`, and \`0xc00\` belongs to the \`mkdir\` and \`unlink\` paths that run after the mounts.
- \`series-torch\` is the last entry of \`board.toml\`-s \`patch\_series\` because both hunks of the patch are anchored on lines that \`zzyd-sheng-audio-addon-mount.patch\` inserts, so the order is a hard requirement - and it is measured rather than asserted. Replaying the recorded \`xnu-inputs.json\` series with the audio patch removed makes this patch fail \(\`rc=1\`, \`error: bsd/kern/kern\_exec.c: 补丁未应用\`\); the full 66-patch series plus this one applies onto a fresh shared clone of \`d8b80295118ef25ac3a784134bcf95cd8e88109f\`, leaving five distinct \`native\_gpu\_addon\_mount\` offsets with \`0xe00\` last and a clean \`git apply --reverse --check\`. \`scripts/unixnu/patches.py\` prepare\(\) applies the resolved list literally, so an edited patch series is only reviewable by replaying it.
- The two new counters reach the console the way this repository already does it, and that is a correction as much as an addition. There is no \`boot\_progress\_trace\` in this tree or in this repository - the mother has one, and inventing a Linux-side stand-in for it is not a port - so the ladder goes out on \`package/BootLog.c\`-s \`A\` row, which \`boot\_log\_tick\(now\)\` re-renders after the mounts run: the five \`native\_gpu\_addon\*\` pairs are \`weak\_import\` externs, weak definitions live in \`package/BootProgressStubs.c\` so the archive links before the kernel carries them, and the row gained \`mount4=stage/status mount5=stage/status\` with \`char row\[120\]\` widened to \`char row\[200\]\`. Reading \`mount5\`: \`1\` with a status is no \`/private/var/ngpu/mediacapture\` \(a delivery problem, not a mount problem\), \`2\` or \`3\` a refused bindfs mount, \`4\` a lookup the sealed root does not answer, \`5\` the overlay took and the commit will publish. Doing this found a record-versus-build mismatch in the same row: this file stated the \`A\` row printed \`mount4=\`, and it never did - the audio HAL stage was defined and never rendered.
- \`scripts/test-dby-torch-media-mount-patch.py --inputs &lt;out&gt;/&lt;device&gt;/&lt;os-build&gt;/&lt;board&gt;/xnu-inputs.json\` is the gate for all three of the above: 7 tests, \`Ran 7 tests in 14.511s OK\`, covering the patch shape \(only \`bsd/kern/kern\_exec.c\`, exactly two hunks\), the two argument names against what \`DbyTorch.cpp\` parses and what the README table documents, the class and bundle names against the glue and the record, the \`weak\_import\` declaration against the definition and the prototype, the counters against BootLog and the stubs, the series file against \`board.toml\`-s last entry and against every other series file, and the replay. It is now a step of \`scripts/check-dby-torch-host.py --tree\` \(\`PASS mount patch: 7 tests against .../dby\_w09/xnu-inputs.json\`\), because a README that says one command is the whole host check has to mean it after each new part; that command is RC=0 end to end and \`scripts/check-regression.py\` prints \`checks=93 pass=93 fail=0 kernel\_args\_bytes=989\` with these edits in.
- What this round cannot prove from the host is named instead of deferred. The \`CMCapture\` class-to-bundle table for 21H461 is not readable on this machine \(there is no shared cache here\), so this record said the plug-in would be delivered under every candidate \`&lt;H..&gt;ISP.mediacapture\` name with a per-name counter saying which one the vendor opened. That spray is dropped and the correction is the mother-s, not mine: \`package/DbyTorch/DbyTorchIos.h:63\` names one service \(\`AppleH6CamIn\`\) and the bundle is one file \(\`H6ISP.mediacapture\`\) because H6 is the last entry of CMCapture-s table and the only one of the five that the pinned kernelcache does not carry \(it has H9, H10 and H13\) - \`refer/PaganiDrivers/drivers/PaganiTorch/TorchIos.h\` states the same reason for the same iOS. Nothing here ever implemented the spray: one name is in the patch, the header, the builder and the staging script. And the command line: \` dby-torch=1 dby-ti=1\` costs 16 joined bytes against the 11 free at 989, so the same full enumeration of every reader in every tree that paid for \` dby-torch=2\` was run again over all 49 entries - and this time it found nothing to spend: each \`offline-legacy-\*\` row gates a branch of NativeLegacyDisplay.cpp \(gop at :383, pm and phase at :98-102, register at :128, validate at :313, transfer at :149\), \`kt\_fixed\_zones=120\` overrides XNU's own 260 \(zalloc\_internal.h:485; the 120 branch is watchOS-or-KASAN only\), \`dk=0\` overrides IOKit's default-on DriverKit debug \(IOKitDebug.h:134, IOUserServer.cpp:88\), \`panic\_on\_crash\_disabled=1\` keeps a crashed daemon off the panic path \(kern\_exit.c:1695\) and \`-enable\_kprintf\_spam\` is the only route by which kprintf reaches the console at all \(pe\_kprintf.c:50\). The 2026-11-06 loss of \`sheng-data-reset=1\` is why enumeration and not preference decides, and here the answer was the naming rule already written at the top of kernel\_args instead: the switch is \`dby-ti=1\` at 8 bytes, the armed line measures 50 entries and 998 bytes with 2 free in core's own payload.check\_args, and no argument was removed.
- The iOS halves of this round are ports, file for file, of what the mother board ships for the same iOS build. \`package/DbyTorch/ios/DbyTorchPlugin.&\#123;h,m&\#125;\` is \`refer/PaganiDrivers/drivers/PaganiTorch/ios/TorchPlugin.&\#123;h,m&\#125;\`, \`package/DbyCamera/ios/DbyCameraProvider.m\` and \`DbyCameraPattern.&\#123;c,h&\#125;\` are the three \`PaganiCamera/ios/\` files of the same name, and \`scripts/build-dby-camera-plugin.py\`, \`scripts/add-dby-camera-data.py\` and \`scripts/add-dby-camera-trust.py\` are \`build-pagani-camera-plugin.py\` and the two halves \(plug-in staging, trust merge\) of \`add-pagani-camera-data.py\`, which the mother runs through one script and this repository keeps as one step per file. Only names moved: \`dbt\_plugin\_load\`, \`dbc\_plugin\_load\`, \`DbyCameraTestPattern\`, \`org.unixnu.dby\_w09.camera\`, \`/private/var/ngpu/mediacapture\`. Every gate of the mother builder is kept and each is a refusal rather than a warning: \`-target arm64-apple-ios17.0\`, the FLAGS list \`-O2 -g0 -Wall -Wextra -Werror -fno-objc-arc -fvisibility=hidden -dynamiclib -Wl,-no\_warn\_inits\`, \`-install\_name /System/Library/MediaCapture/H6ISP.mediacapture\`, \`nm -gU\` refusing any \`CaptureDeviceCreate\` export \(exporting one makes the vendor believe there is a default device, which is the failure \`DbyTorchIos.h\` is written against\), \`nm -u\` refusing an undefined \`\_OBJC\_CLASS\_$\_CMIO...\`, \`otool -l\` demanding the install name and \`minos 17.0\`, a \`\_\_mod\_init\_func\` section or named constructor, \`otool -L\` refusing any library outside the system, then \`codesign --force --sign - --pagesize 4096 --identifier org.unixnu.dby\_w09.camera\` and a \`trust.json\` whose CDHash is read out of that signature. The three name pairs the torch plug-in and the kernel must agree on \(\`DBT\_PLUGIN\_SERVICE\`/\`DBT\_IOS\_SERVICE\`, \`\_PROCESS\`, \`\_SELECTOR\`\) are compared define by define before anything is compiled, so the plug-in cannot drift away from the service the kernel publishes.
- Why the two plug-ins are one file, and why a torch-only seed is not a smaller version of the answer but a different, non-working one: \`-\[BWFigCaptureDeviceVendor initWithDefaultDeviceCreateFunction:cmioExtensionDeviceCreateFunction:cmioDiscoverySession:\]\` \(0x1a693fcf4, the bail at 0x1a693fde0, read in 21H461 by the mother\) returns nil when the default create function is empty and \`kern.hv\_vmm\_present\` is 0 - on a phone it is 0, because that is a device-tree property the QEMU recipes name and this board does not set - so \`+sharedCaptureDeviceVendor\` is nil for the whole boot, every message sent to it lands nowhere, and the six vendor methods \`DbyTorchPlugin.m\` replaces are never called. A torch-only delivery therefore gives a kernel that publishes \`AppleH6CamIn\`, a \`flash\` property on \`/product/camera\`, a Control Center toggle - and no path from that toggle to the LED. \`DbyCameraProvider.m\` corrects that init from the same Mach-O, with its own constructor independent of the torch one: it passes a permanently failing placeholder through the nil check and writes \`\_defaultDeviceCreateFunction\` back to empty afterwards, so the vendor ends up exactly as it is today except that it exists. The test pattern is armed by the staged marker \`ngpu/mediacapture/DbyCameraTestPattern\` - \`/System/Library/MediaCapture/DbyCameraTestPattern\` once the union mount runs - and not by a boot argument, for the mother-s stated reason: it costs no command-line bytes and only means something on a seed that carries the bundle. The QR payload is the mother-s string verbatim \(\`DBC\_QR\_TEXT\` = \`https://unixnu.com/pagani-cam-test\`, \`DbyCameraPattern.h:29\`\) and the modes are 1920x1080 and 1280x720 with 720p active, because a rewrite of a test fixture proves nothing.

### 完成条件

- The audit, the archive and the payload gate pass, and the device boots with the PMGR provider registered.

### 当前范围

- No frequency, idle or charger policy is implemented. Battery reporting is ported read-only \(package/DbyBattery.cpp over the SPMI observer engine\) and its rows are device-measured, and the official-semantics rewrite has been flashed once \(f2-payload-168, which answered both defects on the console but did not leave the Apple logo\); f2-payload-171 \(cb28519bbbe250376918d8f01e549d15bb76c885c9b6076f137b8919903ea5a4, to preload at 18:34:04\) is the first image that carries the official 60 s cadence, the vendor 1000-poll bound and the restored data argument together, so the battery verdict - percentage stable across boots, charge icon surviving a brightness slide - is judged at the panel on this boot and on no earlier one. One recorded correction while doing it: the kernel command line is gated at 1000 bytes by unixnu build payload \(board.toml's older comment cited DarwinBoot.c:542 and said 1024\); the HEAD argument table is 45 arguments / 966 bytes, and 171 ships those 45 plus the three board feature gates under repair \(dby-bl, dby-pa, dby-battery\) at 998 bytes, with only my own newest diagnostic argument armcpu-self-ipi=1 deferred to stay inside the gate. There is no capacity teaching and no charger or float-voltage configuration read; battery health reaches this file as two STATUS\_7 bits feeding the status rule, not as a published health property. f2-payload-173 \(payload\_sha256 673ad03e4a91c5e844c6a484e2207d09336502eafda305ac95130da286d46eb4, kernel\_sha256 5ffc0dc39925c27eacd7d37eb12253fcf9ea8e36941b7e041359166baf5d6365\) is the first image in which the presence fix is actually linked: the payload-only step does not recompile the display-late archive, so payload 172 shipped the 17:24 DbyBattery.o - an object older than the edit and with no reference to getPMRootDomain - and was never flashed. 173 was built by the official kernel-then-payload entry, its object carries that reference, and it went to preload after the 18:59 payload, so the charge-icon verdict is judged on this boot and not on 171 or 172.
- Two cadences ship now and their limits differ: 174 put the five official reasons a cell would not take current \(the input-suspend vote, the requested ICL, the ceiling, the applied ICL and the float voltage\) into the 60 s row, and 175 put the reaction on the 2 s tier. Neither image writes a charger register, so a blocker that the rows name can still only be answered by the official host-side control path over a transport whose write side is not proven - the chnls window stays unmapped and the five prohibitions \(no PMIC configuration write, no charger configuration, no bark/bite, no invented logging, no invented capacity\) are unchanged. The reaction time is bounded by the timer, not by the PMIC: with no interrupt, a cable event is up to 2 s old when it is published.
- The 60 s tier is what the capacity complaint is judged on and a fast cycle deliberately leaves the percentage alone, so a reader who checks the icon within 2 s of an unplug is reading a different field set from the one that carries soc=.
- The torch rows are read on hardware and the console gap of the previous round is closed. payload-ord212-torch.img \(sha256 ec17ddd4fe7d8426a7514a755702e87296efc5ec9637cffd7014454ecc1911e0, kernel de7a04fa...\) booted with \` dby-torch=1 dby-ti=1\` on the line \(50 entries, 998 bytes, 2 free\) and VID\_1209/PID\_316d enumerated, so the capture holds \`\[torch\] start mode=1 max\_ma=300 hard\_ma=500 ppid=0x5d3 leds=0x1 log=1 test\_ms=0\`, \`\[torch\] spmi rc=0 v=0x50010000 apid=97 ee=0 own=0 slots=352 hits=1\`, \`\[torch\] id flash=18/04 ppid=0x5d3\`, the register dump and \`ready ... code=23 hard\_code=39 apid=97 off\_s=300 reads=20 writes=0\`. Mode 1 is what ran, and the identity reads mode 2 exists to earn came back inside it. What is still not measured is light: \`writes=0\` says no channel was switched on, because nothing asked - neither \`dby-torch-test\` nor the user client has been driven on this board - so the current formula \(code 23 for 300 mA under the hard code 39 for 500 mA\) is read-back-correct and never photometrically verified, and the 5 minute bound and the fault ladder stay host-tested. The panel half is unchanged and is the complaint: no flashlight toggle, Camera.app still will not open - which is the iOS advertisement, not the SPMI write, and the same boot says why: \`\[torch\] ios not made: the plug-in is not on the root\`.
- The iOS half is now read on the device down to one refusal and no further. \`\[torch\] ios not made: the plug-in is not on the root\` is \`pgt\_ios\_final\(\)\` answering \`plugin\_visible == 0\`, i.e. the fifth mount reporting that /private/var/ngpu/mediacapture held nothing, because the Data volume in that payload carries no \`H6ISP.mediacapture\`. The sources are in the tree, so what is missing is a Mach-O this machine cannot produce: \`xcrun --sdk iphoneos\` plus \`codesign --pagesize 4096\` exist only on Darwin, which is the same reason the audio server plug-in is built by the macOS Data-seed workflow, and an ad hoc signature means the CDHash of those exact bytes has to join the owner trust cache before mediaserverd - a platform process - maps the code. Until one seed carries the bundle and one trust bundle carries its hash, no host check can stand in for the panel verdict, and mediaserverd-s dlopen trust chain on this board is itself unproven \(audiomxd took the same shape and needed its hash in the owner cache first\).

### 下一步

- Add a device checkpoint for the regulator path once the boot is repeatable.
- Build the plug-in where it can be built and flash what it produces. The two remaining steps are the mother-s, moved to the one runner that has the toolchain: beside the audio steps in the macOS Data-seed workflow, \`python3 device/scripts/build-dby-camera-plugin.py --out &lt;temp&gt;/dby-camera-plugin\` and then \`python3 device/scripts/add-dby-camera-data.py --test-pattern &lt;temp&gt;/data-final.dbr &lt;temp&gt;/data-camera.dbr\`, staged into the pre-grow base so the volume UUID is kept and the round stays payload-only. Then \`scripts/add-dby-camera-trust.py\` puts the job-s own \`trust.json\` CDHash into the owner trust bundle, the payload is rebuilt with \`--data-ramdisk\` and \`--owner-trust-cache\`, and \`preload\` takes it - no kernel rebuild, because the UUID is the ord212 one. The console verdict is \`\[torch\] ios made\` in place of \`not made\`, beside the \`mount5=\` pair; the panel verdict is a Control Center toggle that lights the LED and a code scanner that shows the scrolling bars and the QR. The camera sensor pipeline \(stage 2, task 212\) and the windows on which VID\_1209/PID\_316d does not enumerate \(task 223\) stay separate rounds.

### 证据

- `host`: [Contract audit produces libShengPlatformPower.a and the payload accepts the native-ufs-root + sheng-pmgr=2 gate](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/scripts/build-platform-power.py)
  Command: <code>./unixnu build kernel -j 2 -D ../UniXNU-dby_w09 --uefi ../uefi-sheng &amp;&amp; ./unixnu build payload -D ../UniXNU-dby_w09 --uefi ../uefi-sheng …</code>. Revision: `d8b80295118ef25ac3a784134bcf95cd8e88109f`.
- `device`: [Census arb=50010000 slots=512 usid2=67 ee0-owned=28 with the gauge at channels 33/30/32/48, one published dictionary \(soc=65 mv=3947 ma=-98 stage=3 plug=1\) and 84 cycle rows, including the measured cliff: cycle \#62 err=1 then 22 cycles at tx=0. The image was built from this base commit plus an untracked package/DbyBattery.cpp, which is what these rows are evidence about.](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/package/DbyBattery.cpp)
  Command: <code>/home/wqsqw/f2-rebuild.sh &amp;&amp; fastboot flash preload f2-payload-167.img, then the COM4 kernel console with DtrEnable and RtsEnable set</code>. Revision: `0baa92b6a5e87e3d1f7f16171aa75d6318183225`.
- `device`: [Ten cycles at why=00000000000 with tx=16 clean=16 err=0, published soc=59 mv=3887 ma=-85 plug=1 on=1 en=1 sus=0 st=3, tenth cycle soc=58 mv=3846 ma=+422, chg=1 and full=0 throughout - the vendor status rule measured against the cell current. Same image did not reach the lock screen, which is why the two non-upstream cadences in that row are recorded as its limits rather than as a pass.](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/package/DbyBattery.cpp)
  Command: <code>/home/wqsqw/f2-rebuild.sh &amp;&amp; fastboot flash preload f2-payload-168.img, then the COM4 kernel console with DtrEnable and RtsEnable set</code>. Revision: `0baa92b6a5e87e3d1f7f16171aa75d6318183225`.
- `device`: [Official order ran kernel then payload: REBUILD\_RC=0, KERNEL\_RC=0, DbyBattery.o rebuilt at 18:58:31 from the 18:52:39 source and kernel.macho relinked at 18:59:27. The link proof is \_\_ZN9IOService15getPMRootDomainEv as an undefined reference in tree/build/native-legacy-display/DbyBattery.o; receivePowerNotification itself is virtual \(RootDomain.h:266 under the public: at :155\) so it dispatches through the vtable and cannot appear as a symbol, and a strings match on the macho proves nothing because XNU defines it in IOPMrootDomain.cpp. The shipped argument line is 998 of the 1000-byte gate and carries the five restored families - sheng-data-reset=1, sheng-log=1, offline-legacy-retire=1, boot-ui-focus=launchd, boot-ui-focus4=SpringBoard - plus sheng-data-persist=2 and dby-battery=1. No serial was armed: this console port must not be held across a boot. The pass criterion is at the panel, with no drawn diagnostics: the mark clears when the cable leaves USBIN\_PLUGIN\_RT\_STS without any brightness slide, returns on plug, and the percentage is stable across reboots.](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/package/DbyBattery.cpp)
  Command: <code>/home/wqsqw/f2-rebuild.sh &amp;&amp; fastboot flash preload f2-payload-173.img</code>. Revision: `0baa92b6a5e87e3d1f7f16171aa75d6318183225`.
- `device`: [Official order, kernel then payload: md5 of the build input 9278d9d79384497382d147d272c3091f, REBUILD\_RC=0, KERNEL\_RC=0, DbyBattery.o and DbyBattery.late.o rebuilt at 19:42:27 from a 19:40:24 source and kernel.macho relinked at 19:43:06, with both new \_\_cstring tokens \(cfg=0x%02x iclc and iclc=%d iclm\) counting 1 in the object, in the late object and in kernel.macho - which is the link proof the payload-only step cannot give. Shipped line 998 bytes; payload\_sha256 9f86659e0a597fd409b280f9d9df132aebe66d48de3a50d64634e61cd3902a92, kernel\_sha256 bd96c7f693bfd3cf775ebed6fd65b057d28880208d8f46b90a21b78476d9a8fb; flashed to preload only at 19:46:38 \(212992 KB, FLASH\_RC=0\) and no COM4 was armed across that boot, so this row proves build and link, not content: the five charger-limit fields it added stay unread until a capture works. The verdict the user gave for the PREVIOUS image \(173\) is what this round was aimed at - the charge state finally follows the cable but lags - and that lag is the single 60 s timer, which is 175's subject, not 174's.](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/package/DbyBattery.cpp)
  Command: <code>/home/wqsqw/f2-rebuild.sh &amp;&amp; fastboot flash preload f2-payload-174.img</code>. Revision: `0baa92b6a5e87e3d1f7f16171aa75d6318183225`.
- `device`: [PASS the charging icon follows the cable in both directions with no brightness slide and no repaint event behind it, and it does so on the same image whose \[apr\] rows hold 26.3 s of audio across 21.5 s of wall clock -- so this row is evidence about the shipped tree, whose package/ directory is exactly commit e392957 \(git status shows only the untracked drivers/ShengUfs debris\). The 168-174 rows above stay as the build-and-link history of the same code; the panel verdict moved to this boot because the earlier images either did not leave the Apple logo, shipped an object older than the edit, or had the 2 s tier but not the audio ladder.](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/package/DbyBattery.cpp)
  Command: <code>fastboot flash preload payload-ord209.img (sha256 592c632b74abcf0d6e13929257fc18976407f7c9203310031e9f65f745d10db3, 218103808 bytes, to preload at 03:04), then the charge mark watched at the panel while the cable went in and out</code>. Revision: `e392957e512557a4f534167dd707719a789fd52f`.
- `host`: [PASS strict compile of the two portable sources, spmi 9045 checks, core 1580100 checks, args 4; the runner itself states that it built no kernel archive, so the link proof is the other row.](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/scripts/check-dby-torch-host.py)
  Command: <code>python3.11 scripts/check-dby-torch-host.py</code>. Revision: `a167df4c928876b460e4543a5755f77976ce2c92`.
- `host`: [build/dby-torch/libDbyTorch.a is 256216 B and kernel 05d697b0be1471b8 carries the DbyTorch symbols defined, which is the gate a force\_load bypass would have faked.](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/scripts/build-dby-torch.py)
  Command: <code>./unixnu build kernel -j 2 -D ../UniXNU-dby_w09 --uefi ../uefi-sheng &amp;&amp; llvm-nm --extern-only out/dby-w09/ipados-17.7.11-21H461/dby_w09/kernel/kernel.macho | grep dbt_</code>. Revision: `a167df4c928876b460e4543a5755f77976ce2c92`.
- `device`: [No regression named at the panel after the delete-and-add argument swap: the tablet enters the system normally. The torch verdict is not measured: the USB debug console never enumerated in the 240 s capture window, so no \`\[torch\]\` row exists for this boot, and the same look shows Control Center without a flashlight toggle and Camera.app that does not open, unchanged from the previous image.](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/package/DbyTorch/DbyTorch.cpp)
  Command: <code>fastboot flash preload f2-payload (sha256 b9c756522b7d86cef3e552d5f17eca62d3dfbdbffa6d44cfc650dcaf92c8a646, payload built at this commit, kernel 05d697b0be1471b8 unchanged), then fastboot continue and the panel read by the owner</code>. Revision: `0a6d3ceb548fd5874f7e0ec95eb0b5aa9fd91f49`.
- `host`: [Ran 7 tests in 14.511s OK, RC=0: the recorded 66 patches plus zze-dby-torch-media-mount.patch apply in order onto a fresh shared clone of d8b80295118ef25ac3a784134bcf95cd8e88109f, the five native\_gpu\_addon\_mount offsets are distinct with 0xe00 last, git apply --reverse --check is clean, and dropping zzyd-sheng-audio-addon-mount.patch from the replay makes this patch fail - so the order board.toml encodes is proven by mutation and not only read.](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/scripts/test-dby-torch-media-mount-patch.py)
  Command: <code>python3.11 scripts/test-dby-torch-media-mount-patch.py --inputs /home/wqsqw/upstream/core/out/dby-w09/ipados-17.7.11-21H461/dby_w09/xnu-inputs.json</code>. Revision: `e19d6f979b079795cf02c31a4b2865f04ef2d095`.
- `host`: [RC=0 end to end: strict compile of 3 portable sources, spmi 9045, core 1580100, ios 19 checks, args 5 boot arguments, PASS 5 objects in a temporary libDbyTorch.a \(25 entry points, 239 kernel imports each defined by that tree-s linked kernel, so the iOS glue is now compiled and linked by this gate\), PASS mount patch: 7 tests. One command is still the whole host check because the replay became a step of it instead of a second instruction nobody runs.](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/scripts/check-dby-torch-host.py)
  Command: <code>PATH=/home/wqsqw/xnu-toolchain/llvm20-shims:$PATH XNU_TOOLCHAIN_BIN=/home/wqsqw/unixnu-linux/CommandLineTools/usr/bin python3.11 scripts/check-dby-torch-host.py --tree /home/wqsqw/upstream/core/out/dby-w09/ipados-17.7.11-21H461/dby_w09/tree</code>. Revision: `e19d6f979b079795cf02c31a4b2865f04ef2d095`.
- `host`: [23 rows \(20 extern entry points\) and no glue symbol: the kernel this tree last linked predates package/DbyTorch/DbyTorchIos.\*, so no iOS-facing claim can be read from that image and the README now reports 20 rather than the 24 recorded before this measurement. The next official kernel build is what puts the glue and the fifth mount into a kernel.](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/package/DbyTorch/DbyTorchIos.cpp)
  Command: <code>PATH=/home/wqsqw/xnu-toolchain/llvm20-shims:$PATH llvm-nm --extern-only /home/wqsqw/upstream/core/out/dby-w09/ipados-17.7.11-21H461/dby_w09/tree/build/xnu/ios-obj/mach.development.bcm2837 | grep -c "dby_torch\|dbt_"</code>. Revision: `e19d6f979b079795cf02c31a4b2865f04ef2d095`.

## 镜像组装 {#packaging}

`device-verified`

组件: `DarwinBoot`, `XnuPrelink`.

### 硬件与依赖

- Prelinked kernel image from the donor kernelcache plus board archives.
- Firmware volume, ADT generated by scripts/make-adt.py from the compiled hardware DTB, trust cache bundle and Data seed.
- Payload FAT volume labelled DBYW09ESP, 208 MiB.

### 配置

- \[payload\] loader = firmware places DarwinBoot inside the firmware volume; title, timeout and kernel\_args are written into the ESP unixnu.toml of the image.
- \[payload.adt\] unique\_chip\_id = required and --unique-chip-id carry the identity at build time.
- \[userdata\] describes which IPSW components become root windows inside the assembled image.
- XnuPrelink is the kit stage that assembles the prelinked kernel image the payload then carries.

### 操作步骤

- Build the payload, inspect the produced image \(menu entry, kernel arguments, ramdisk size\) and flash it to the payload partition named in README.md.
- Keep every produced image: rebuilds overwrite the output path, and a checkpoint that cannot be re-flashed cannot be repeated.

### 开发经验

- \[kernel\] patch\_series is an array override, not an append: a device layer that adds a fifth series repeats the four inherited arch:/soc:/device:/os: entries, and the order inside that array is the order patches.py:prepare applies them.
- Argument counts come from the command line embedded in the built image, never from the board.toml array: the array spans comment lines, so an unfiltered grep reported 48 arguments / 1038 bytes for an image that carries 44 / 955, and the DarwinBoot header caps the string at 1000 bytes, which is what makes the difference decisive.
- The menu entry's kernel arguments come from the payload, which is why an argument change is a three-minute payload rebuild rather than a kernel rebuild.
- The payload partition had to change because the image exceeds the official cache partition; the flash target is recorded with its reason instead of being a local habit.
- A seed larger than what the packed container can carry silently produces an unbootable image; check the packed size and the logical size together.
- A second \`patches/xnu\` series now ships: \`patches/xnu/series-torch\`, naming exactly one patch \(\`zze-dby-torch-media-mount.patch\`\), resolved after \`series-audio\` in \`board.toml\`. Two things this area records because the last round taught them: the patch is generated from the work-tree file and verified by \`git apply --check\` plus a \`diff -q\` against the intended post-state rather than typed \(tabs and context lines do not survive retyping\), and a series is only reviewable by replay, since the next \`unixnu build kernel\` re-clones and applies 67 patches where it applied 66 - the replay is \`scripts/test-dby-torch-media-mount-patch.py --inputs xnu-inputs.json\`, now a step of the torch host check.

### 完成条件

- One command produces a bootable image that is reproducible from the recorded inputs and hashes.

### 当前范围

- One image is assembled from two repositories: the firmware repository builds SILICIUM\_UEFI.fd, and a workbench script splices that volume behind the verified 144-byte boot shim into a stock Android boot header, because this tablet cannot boot an unpacked image and the flashed partition is not ./unixnu bootimg's output.
- ./unixnu bootimg packs this board's image correctly but bootimg.verify\(\) unpacks the v0/v1 header fields, so any header\_version &gt;= 3 board rejects its own output; the check is read as a layout diff, not as a pass/fail gate.

### 下一步

- Bring the boot packaging \(shim + FD into the stock boot header, with its size and shape gates\) into this repository so one recorded command produces the image that is flashed to boot.

### 证据

- `device`: [Built images boot on hardware to the iPadOS lock screen; the flashed partition and its size limit are recorded in README.md](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/package/unixnu.toml)
  Command: <code>./unixnu build payload -D ../UniXNU-dby_w09 --uefi ../uefi-sheng --trust-cache build/original-static-system-trust/original-static-system.bundle --data-ramdisk &lt;seed.dbr&gt; &amp;&amp; fastboot flash preload &lt;payload.img&gt;</code>. Revision: `d8b80295118ef25ac3a784134bcf95cd8e88109f`.
- `source`: [Apple input inventory, hashes and the rule that they stay out of Git](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/proprietary-files.txt)
- `source`: [native-smp-secondary and native-smp-type-clusters are applied by the sm8250 feed at its new pin a6e7e36, so this series keeps only sheng-platform-power plus the device-local rows; patches/xnu/series-audio adds zzyd-sheng-audio-addon-mount.patch, the 0xa00 bindfs entry that presents the staged /private/var/ngpu/audio as /System/Library/Audio/Plug-Ins/HAL behind the sheng-gpu-addon=1 boot argument](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/patches/xnu/series)

## 诊断 {#diagnostics}

`device-verified`

### 硬件与依赖

- Panel text output \(boot-progress=2 checkpoints, panic screen, UI trace page\) and, since the 2026-11-05 firmware revert, the CDC-ACM kernel console enumerating as 1209:316d.
- An offline QEMU harness reproducing the same image with counters readable as text.
- The same rows written to the UFS log by BootLog.c, which is where they live now that the panel is left alone.

### 配置

- \[payload\] panic\_screen = true and kernel\_args boot-progress=2, armcpu-diagnostics=1, boot-ui-focus=launchd, boot-ui-focus4=SpringBoard, sheng-build-tag.
- Since 2026-11-05 nothing paints after the scanout hand-off: BootProgress.c:1025 defaults sheng-banner to 0, so the live banner is off, and boot-diag-resume is gone, which leaves resume\_after=0 \(BootProgress.c:551 clamps &lt;5 to 0\) = never retake the panel. sheng-banner=1 can opt the painting back in and was tried once on 2026-11-05; the owner refused it \(the panel is not a debug surface\) and the accepted configuration leaves the banner off, so a number has to come from the log route.
- LinkStubs/BootProgressStubs provide the zero-value definitions for sheng-specific counters that libBootProgress references.

### 操作步骤

- For each attempt record the command, the image hash, the last completed checkpoint and the first failing operation.
- Use the offline harness for counter-level questions and the device only for what needs the real panel or the real storage.

### 开发经验

- The board preflight is called with cwd = the device tree and the firmware checkout in $UNIXNU\_UEFI \(core cli.py\), so it has to resolve that variable rather than a literal repository name, tolerate the whitespace the memory-map generator emits, and compare intervals only from PcdSystemMemoryBase upward because MemoryInitPei.c never registers a region below it.
- The panel is the instrument: without a console, the panic text plus checkpoint numbers are the only evidence, so a build tag per image is not decoration but the way to correlate a photograph with a build.
- Counters beat wall-clock judgement. In the offline harness the guest clock advances while TCG work rate stays roughly ten times slower than the official hypervisor, so elapsed time never proves progress or regression.
- The current limits are visible in this area: the offline harness reads counters, but the panel still needs a camera photograph, and a USB console is the change that removes that bottleneck.
- Diagnostic polish must not outrank the next root cause; the fastest useful step has repeatedly been one static query that enumerates the answer instead of another flash-and-read cycle.
- The console's blocker was firmware-side, not in XNU: the board shipped a byte-patched UsbConfigDxe \(two cbz w10 -&gt; b plus one table entry\) that forced the DWC3 HOST init path, so QcomXnuUsbDebug failed at its CORE\_NOT\_DEVICE gate and 1209:316d never appeared. Reverting to the vendor binary \(md5 6340bc7e..., named directly by the INF\) enumerated it 74 s into the boot and bound COM4.
- A binary patch of a vendor .efi can therefore remove a capability while appearing to add one; check which blob the INF names before believing any note about what reached the FV.
- Enumeration was not the last blocker -- reading was. pump\(\) in package/QcomXnuUsbDebug/usb/Dwc3.c:387 refuses to queue an IN transfer while d-&gt;dtr is 0, and dtr is set only by the host's SET\_CONTROL\_LINE\_STATE \(Dwc3.c:313\), so a reader that leaves DTR down sees a live COM port and zero bytes forever. The official collector is a pyserial script and pyserial asserts DTR on open, which is why this never showed up in the module docs; a hand-written System.IO.Ports reader needs DtrEnable and RtsEnable set explicitly. With them the same idle boot yielded 3844 bytes on the first open and 0 on the second: the 4 MiB CPU backlog replays from the module banner on the first read, so no cold-boot timing is required, and after the drain the port live-tails.
- The console stops at lockdown\_mode: ... in nvram is off because nothing after that prints -- the board's own diagnostic rows go to the UFS log \(BootLog.c:1110 native\_ufs\_log\_write\) and, until this default flip, to the panel, never to kprintf. Both of those destinations are now wrong in the interesting direction: BootLog.c is not in the image at all \(two rows below\), so the rows that reach the host are kprintf rows. What the console does carry is the kernel's own output and the panic path, where QCOM PANIC END is the only marker that the two send queues drained.
- Turning the panel off with no reader ported leaves the board with zero readouts, and that is what 769d8ef did: the comment at package/BootProgress.c:1020 promises the record reaches the host by itself, but the only host-side stream is kprintf, which ends with the early boot. Measured on the 2026-11-05 CPU-round boot: the CDC console carried 3844 bytes, last line lockdown\_mode, and no row after that. Two sources exist: the live banner, sheng-banner=1 \(BootProgress.c:1028, it draws the CPUFREQ and SCHED rows over the OS frame\) -- flashed and read on 2026-11-05, then reverted because painting over the system was refused -- and the official reader UniXNU-sheng/scripts/read-sheng-log.py, which needs this board-s own package/linux-log bring-up, not ported yet. With the banner off that reader is the only source, so porting it is the next device-visible step. Until one of them is used, no frequency vote or cluster placement claim from this board is evidenced by numbers, only by behaviour.
- COM4 mirrors kprintf and not IOLog. Measured on the 2026-11-06 capture: 745 lines carrying every \[touch\] and \[pa\] kprintf row and not one IOLog-family row anywhere -- no AMFI line, no Sandbox line, no IOKit class line. That single fact is the whole explanation of the battery line looking dead: package/DbyBattery.cpp wrote all thirteen of its rows with IOLog, so a boot with dby-battery=1 and zero battery rows said nothing about the PMIC, nothing about the SPMI observer engine and nothing about whether the driver started at all. Board code that has to be seen on this console calls kprintf.
- scripts/check-regression.py had the right ADT contract and the wrong shape: it demanded that the difference between the recorded baseline and a freshly built ADT be one contiguous 64-byte run sitting under a /chosen random-seed property name. ord208 measured the runs at \[\(392, 445\), \(446, 456\)\] -- 63 of the 64 seed bytes different and nothing outside 392..456 different at all -- because a byte the new random draw happens to repeat splits the run, so an unchanged ADT was reporting as a regression. The gate now bounds the union of the runs at 64 bytes and still requires the property name before it.
- Each field of the \[apr\] row needs a definition before it can carry a verdict: played= is completed regions x 1024 frames, which counts silence as readily as sound; wrot= is the audio server's own out\_written cursor; peak= is the largest absolute sample the pump has taken out of the ring; resync= counts ring-phase re-locks; derr= counted write-done events whose status byte was read at the wrong offset. ord209 could be called sound because played and wrot converged to within 31072 frames \(0.6 s\) while peak= held at 9787 and late= stayed at 0.
- package/BootLog.c is not compiled into this kernel, which is what supersedes the UFS-log sentence above \(BootLog.c:1110 native\_ufs\_log\_write as the destination of the board rows\) and the same assumption in the display area. Measured on kernel b587c637: llvm-ar t on build/boot-progress/libBootProgress.a lists BootProgress, BootFaultProbe, BootWatchdogPolicy, BootProcessProbe and BootUiTraceProbe and no BootLog.o; no builder in the assembled tree or in core names BootLog.c \(it is referenced only in comments\); and llvm-nm finds its own symbols absent -- boot\_log\_export\_put, diag\_flush, copy\_msgbuf. The grep the build wrapper used as a proxy was boot\_log\_tick, which package/BootProgress.c defines, so that check answered yes and proved nothing; it now greps the three BootLog-only symbols. Two consequences: the \[battery\] row at BootLog.c:837-843 can never appear, so native\_battery\_stats\[16\] has no reader in this image and the only way to see a battery reading is IOPMPowerSource or the producer-s own kprintf rows; and console silence anywhere in the battery or boot-record path has to be re-explained from the kprintf sink, not from a log window that does not exist.
- Two audio instruments were added while the transport question was being settled, and both belong to the diagnostics record rather than the audio one because they read state that has nothing to do with classification. The first is the pre-flash gate: scripts/check-regression.py compares the kernel arguments and the counters this board is accepted on against the boot that is known good, so a change that silently removes one of them fails before a flash instead of after it. Measured on the tree as it stands here: checks=91, pass=91, fail=0, kernel\_args\_bytes=992, REGRESSION\_GATE=0. The second is the kernel print of the plug-in trace ring: package/DbyAudio.cpp skipped kind 0, which is a property read of an object this plug-in answers, so a boot could stream for half a minute while every row naming what the audio server actually asked sat unread in the low slots -- ord203 printed slots 42..64 and dropped 0..41, and unk= only ever held the reads that were refused. Every kind now prints, spelled get, set, call or throw, which turns a refused-property count into the list of questions themselves.
- The gate's payload-input section also pinned adt\_sha256, and that check failed on a build which had changed nothing: devicetree.py:308 writes os.urandom\(64\) into /chosen/random-seed, so an ADT digest is a per-build draw. Measured on two payload builds from the identical three run \#25 carriers: 7d836064... and 4e32cedd..., same 14736 bytes, one differing run at 392..456, and the property holding those bytes is random-seed. The fix pins bytes instead of a digest. scripts/regression-baseline-adt.adt is the accepted boot's own ADT, extracted from payload-ord203.img with mcopy -i \(no root, no loop mount\), which reproduces the e91c7e80... digest the baseline had already recorded -- so the extraction is faithful to what the board booted -- and the gate now allows exactly one 64-byte difference, only where the preceding property name is random-seed. That is stricter than the digest it replaces: flipping one character inside root-matching, the 171-byte property carrying the Data volume UUID the kernel looks the seed up by, is refused, while replacing all 64 random bytes is accepted, and both cases are exercised in the same step that rewrites the check. The three genuine carriers were re-recorded beside it because this delivery swaps them on purpose \(trust 400d5667..., addon a267725c..., seed 423d4000... for the CI run 42504049040 plug-in\). Verdict over the built artifact: checks=93 pass=93 fail=0, kernel\_args\_bytes=992, REGRESSION\_GATE=0.
- The torch hook follows the one-shot rule the touch hook was accepted on: \`package/BootProgress.c:1134\` requires the latch clear, \`\!ml\_at\_interrupt\_context\(\)\` and \`nprocs&gt;0\`, and \`:1135\` sets \`dby\_torch\_hook\_runs\` before calling \`dby\_torch\_start\(\)\`, so a \`monitor\(\)\` that runs every tick cannot start a second thread. The entry point still needs a sleeping context of its own, which is why it returns void and reports instead: \`DbyTorch.cpp:238\` records -6 if \`kernel\_thread\_start\` fails, and the rest of the story goes out as \`\[torch\]\` kprintf rows -- the family COM4 mirrors, where IOLog rows have already once made a live driver look dead.
- The pre-flash gate caught a launcher that had fallen behind the record, and the arbiter was the accepted image itself. \`f2-payload.sh\` was still passing \`run23/data-audio.dbr\` \(997ca7ee...\), so the payload-input row failed against \`scripts/regression-baseline.json:72\`, which pins 423d4000...; measured rather than argued, \`payload-ord209.img\` \(sha256 592c632b74abcf0d..., 218103808 B\) lists \`EFI/UniXNU/Payloads/scratch-data.img\` at 1511664 B and that extracted file hashes to 423d4000d4d9de1f..., byte for byte \`audio-addon/run25/data-audio.dbr\`, while the trust bundle \(400d5667de0da464..., 61408 B\) and the plug-in \(a267725cd48bf899..., 12088 B\) are already identical between run23 and run25 -- only the seed had advanced. With the launcher naming run25 the same tree reports checks=93 pass=93 fail=0 and kernel\_args\_bytes=992, and the freshly built payload \(d1d71fed8d6e32c1...\) re-extracts to 423d4000... Nothing was written into the baseline to get there, which is the point of pinning an input hash: it indicts a stale command, where a digest of a build directory would have indicted the tree.
- The addon-mount counters the flashlight round adds follow this area-s established link shape rather than a new one: \`package/BootProgressStubs.c\` defines \`native\_gpu\_addon5\_stage\` and \`native\_gpu\_addon5\_status\` weakly, next to the four pairs already there, so \`libBootProgress.a\` links before the kernel carries them, and \`scripts/check-dby-torch-host.py --tree\` grew a \`mount\` step that replays the tree-s own recorded \`xnu-inputs.json\` series with the torch patch after it. The diagnostics that have been \*read\* are unchanged: no \`\[torch\]\`, \`mount4=\` or \`mount5=\` row exists on hardware yet, because the console component of this area has not enumerated since the argument swap.

### 完成条件

- Every claimed milestone has a reproducible command, a matching source revision and an accessible result.

### 当前范围

- The console only carries kernel text while the firmware hands DWC3 over in DEVICE role, so a firmware-side role change can silence it again without any XNU fault.
- The gadget is kernel-side, so COM4 exists only from about 74 s after power-on and ABL or UEFI text can never appear on it.
- UI-trace and process probes are board-local adaptations of shared sources.

### 下一步

- Evidence for the CPU round is behavioural only: the owner reports the system much smoother, while the accepted pair \(kernel 60f3dbac380b, payload c1303fb6cf93\) paints nothing and the console stops at lockdown\_mode. alioth's own criterion -- UI work on c4-c7 -- still needs the CPUFREQ and SCHED rows, and the only place left to read them is the UFS window.
- Port package/linux-log so UniXNU-sheng/scripts/read-sheng-log.py can fetch the same rows from the UFS window with no panel at all.
- Turn the control plane on for the backpressure and drop counters, STATUS and REBOOT: qcom-usb-ctl=1 is no longer within budget \(the line is at 999 of 1000 bytes\), so it needs an argument retired first. A screenshot still needs a qcom\_usb\_debug\_register\_framebuffer\(\) call, and the display side has none, so a shot answers unavailable today.
- Before re-enabling the CDC-ACM tee permanently, settle the 2026-11-01 hazard: qcom\_usb\_debug\_write\(\) polls DWC3 and once the cable leaves there is no owner to find.

### 证据

- `device`: [Panic text with frames, pages and free counters and the checkpoint page were both read on the panel of the tablet](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/package/BootProgress.c)
  Command: <code>./unixnu build payload -D ../UniXNU-dby_w09 --uefi ../uefi-sheng … &amp;&amp; fastboot flash preload &lt;payload.img&gt;</code>. Revision: `d8b80295118ef25ac3a784134bcf95cd8e88109f`.
- `host`: [Entry-probe and display counters are readable from the offline harness used to decide the display fixes](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/scripts/patch-xnu-entry-probe.py)
  Command: <code>./unixnu build kernel -j 2 -D ../UniXNU-dby_w09 --uefi ../uefi-sheng</code>. Revision: `d8b80295118ef25ac3a784134bcf95cd8e88109f`.
- `device`: [USB\\VID\_1209&amp;PID\_316D\\QCOMXNUUSBDEBUG enumerated 74 s after the 2026-11-05 flash and bound as COM4; the same watcher on the previous build saw zero hits over 240 s](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/board.toml)
  Command: <code>fastboot flash boot &lt;boot_dby_w09_uefi.img built from the vendor UsbConfigDxe&gt; &amp;&amp; reboot, then watch Windows for VID_1209&amp;PID_316D</code>. Revision: `e61237a2db62a1a35b57d6cdcec8671ec1878265`.
- `source`: [The SM8250 bring-up recipe this board wired: six patched XNU call sites, the two darwin23 series entries after os:/zzz-boot-progress.patch, qcom-usb-debug=1 as the only enable switch, and 1209:316d serial QcomXnuUsbDebug as the host-side proof](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/package/QcomXnuUsbDebug/docs/port-sm8250.md)
- `host`: [3844 bytes of real kernel log headed by QCOM XNU USB CDC ACM v1 and Darwin Kernel Version 23.6.0; a reboot captured 4035 bytes from the same head; a second open returned 0 bytes because the CPU backlog had drained](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/package/QcomXnuUsbDebug/usb/Dwc3.c)
  Command: <code>System.IO.Ports.SerialPort on COM4 with DtrEnable and RtsEnable set before Open(), read for 12 s</code>. Revision: `7b9579e348c30a893e0d34cde3058f64e8bc638f`.
- `host`: [the accepted boot-s own carrier hashes to the pinned 423d4000... \(1511664 B\); the rebuilt payload \(d1d71fed8d6e32c1 on kernel 05d697b0be1471b8\) extracts to the same bytes and the gate reads checks=93 pass=93 fail=0, kernel\_args\_bytes=992, REGRESSION\_GATE=0.](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/scripts/regression-baseline.json)
  Command: <code>mdir -i payload-ord209.img ::/EFI/UniXNU/Payloads &amp;&amp; mcopy -i payload-ord209.img ::/EFI/UniXNU/Payloads/scratch-data.img /tmp/ &amp;&amp; sha256sum, then ./unixnu build payload with --data-ramdisk run25/data-audio.dbr and scripts/check-regression.py</code>. Revision: `a167df4c928876b460e4543a5755f77976ce2c92`.
- `host`: [The recorded argument list moves with the board.toml line it pins, in the same commit: the baseline holds 48 arguments, the shipped payload line holds 49, the lost set is empty and the only addition is dby-torch=2, and the gate prints checks=93 pass=93 fail=0 with kernel\_args\_bytes=989. The baseline note names the reason for the addition, so the lost-argument row keeps guarding the 48 accepted arguments instead of going blind after an edit that was deliberate. This row supersedes the 992-byte readings recorded above, which were measured on their own trees.](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/scripts/regression-baseline.json)
  Command: <code>python3.11 scripts/check-regression.py -D ../UniXNU-dby_w09</code>. Revision: `0a6d3ceb548fd5874f7e0ec95eb0b5aa9fd91f49`.

## device-tree {#device-tree}

`host-verified`

### 硬件与依赖

- Board memory, enabled CPUs and enabled peripherals in the board DTS; controller registers and interrupt geometry in the SoC DTSI.
- \[device\_tree\] source = device:dts/dby\_w09.dts with include\_dirs = soc:dts, so the dtsi comes from the sm8250 feed pinned in feeds.toml and recorded in unixnu.lock, not from a sibling checkout.
- OS profile property tables and the payload handoff switches in board.toml \[payload.adt\].

### 配置

- dtc compiles the two sources into device-tree/hardware.dtb and scripts/unixnu/devicetree.py encodes kernel.macho.adt; the hand-written format 1 generator is retired.
- The memory node needs two size cells because the root declares \#size-cells = &lt;2&gt;: the tested unit's 6 GiB is reg = &lt;0 0x80000000 1 0x80000000&gt;.

### 操作步骤

- The build compiles the DTS itself with the include directory resolved from \[device\_tree\] include\_dirs = soc:dts; the manual equivalent is dtc -I dts -O dtb -i &lt;sm8250 feed checkout&gt;/dts -o /tmp/dby\_w09.dtb dts/dby\_w09.dts, and the checkout is the one ./unixnu fetch creates for the pinned commit.
- The core's scripts/make-adt.py converts that DTB with --os-profile profiles/os/ipados-17.7.11-21H461/profile.toml --board board.toml --unique-chip-id HEX --data-ramdisk --trust-cache into kernel.macho.adt; devicetree.py and make-adt.py both live in the core checkout, not in this repository.
- Decode both the generated and the hardware-proven ADT and diff them node by node; random-seed and boot-manifest-hash are excluded because the generator writes a fresh seed each run.

### 开发经验

- The hardware-proven ADT lives inside the flashed payload image, not as a loose file, so the golden copy is extracted from the FAT volume with mcopy.
- /arm-io children are exported as offsets from the window base that arm\_io\_window\(\) derives from the lowest register it can see, so a different base between two ADTs is not a different physical address.
- ephemeral-storage is published by the converter whenever --data-ramdisk is passed and persistent\_data is absent; the hardware-proven image carries it, so the board must not set persistent\_data for a reproduction run.
- The memory node makes the board device tree per-unit data too: it carries the tested unit's 6 GiB, so an 8 GiB unit compiles a different reg against a matching board.toml dram\_size.

### 完成条件

- The official converter alone produces an ADT that differs from the hardware-proven one only in the rows recorded as limits.

### 当前范围

- The common generator emits no /pram node and no /chosen/embedded-panic-log-size, so check\_for\_panic\_log\(\) maps nothing; this is the same gap the official alioth board records, and the panic evidence channel on this board is the panic\_screen text instead.
- /chosen/boot-uuid was a format 1 extra: IOKitBSDInit.cpp consumes root-matching first and only falls through to boot-uuid when it is absent, so the official output needs no substitute.
- One contiguous DRAM range is all the handoff supports, so the board declares the 6 GiB that was measured on hardware; an 8 GiB unit of this same model, or a larger reservation on this one, requires that tablet's own device tree as the source, not a hand-set number.

### 下一步

- Re-record the DRAM extent and the enabled peripheral registers from the tablet's own Android device tree once the payload flashes from the official chain.

### 证据

- `host`: [82 property rows are identical; the generator additionally emits /arm-io/ufsphy and /product/audio, the hardware-proven image additionally carries /pram and /chosen/embedded-panic-log-size, and the arm-io child is named ufshc there against ufsphy here - the same rows this area records as limits](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/dts/dby_w09.dts)
  Command: <code>dtc -I dts -O dtb -i &lt;sm8250 feed checkout&gt;/dts -o /tmp/dby_w09.dtb dts/dby_w09.dts; python3 &lt;core&gt;/scripts/make-adt.py --dtb /tmp/dby_w09.dtb --os-profile profiles/os/ipados-17.7.11-21H461/profile.toml --board board.toml --unique-chip-id HEX --data-ramdisk --trust-cache --output /tmp/generated.adt; decode the generated ADT and the one extracted from the flashed payload and diff them node by node</code>. Revision: `d8b80295118ef25ac3a784134bcf95cd8e88109f`.
- `source`: [\[device\_tree\] source and include\_dirs, and the \[payload.adt\] handoff switches the converter consumes](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/board.toml)
- `source`: [unixnu,cluster-type is E on cpu0 to cpu3 and P on cpu4 to cpu7. Those rows are only valid together with the feed patch native-smp-type-clusters.patch, which raises MAX\_CPU\_CLUSTERS to 2 and defines \_\_ARM\_AMP\_\_: parsed against MAX\_CPU\_CLUSTERS 1 the topology parser maps a P core to cluster 1 and writes past the end of cluster\_phys\_to\_logical on the stack, and the kernel dies before the console comes up. scripts/check-smp-topology.py refuses the unpaired form](https://github.com/WQSQW/UniXNU-dby_w09/blob/715814d07840c817317892d5a585f4a3e769e343/dts/dby_w09.dts)

</div>
