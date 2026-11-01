# Xiaomi 13 \(OddlyLabs\)

[OddlyLabs/unixnu-fuxi](https://github.com/OddlyLabs/unixnu-fuxi)

<div v-pre>

Xiaomi 13 \(fuxi\). Board files from the UniXNU device template, the FTM5 touch driver and its staged kernel probe; CI builds the kernel, the payload, the DEBUG firmware and the fastboot boot image. No device boot evidence yet.

源记录: [porting.toml](https://github.com/OddlyLabs/unixnu-fuxi/blob/77c0a035d49008df4ccafe617456c3c2e62d1dc0/porting.toml), `77c0a035d49008df4ccafe617456c3c2e62d1dc0`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `implemented` |
| [固件与启动](#firmware) | `host-verified` |
| [CPU 与中断](#cpu) | `planned` |
| [内存与 DMA](#memory) | `planned` |
| [存储与根卷](#storage) | `planned` |
| [显示](#display) | `planned` |
| [输入](#input) | `implemented` |
| [GPU](#gpu) | `planned` |
| [网络](#network) | `planned` |
| [音频](#audio) | `planned` |
| [电源](#power) | `planned` |
| [镜像组装](#packaging) | `host-verified` |
| [诊断](#diagnostics) | `implemented` |

## 配置 {#configuration}

`implemented`

组件: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`, `DarwinBoot`.

### 硬件与依赖

- UniXNU examples/device template \(SM8550, iPadOS 17.7.11 profile\).
- UniXNU-sm8550-common at 23b2049fcd9e30356161def84231334fb55ecca9.

### 配置

- board.toml: name fuxi, kit fuxi, soc\_source sm8550, os\_profile ipados-17.7.11-21H461, device\_tree.source device:dts/fuxi.dts.
- configs/fuxi\_defconfig: the template options, CONFIG\_XNU\_NATIVE\_ADRENO off \(the SoC fragment turns it on\), and CONFIG\_XNU\_EXTRA\_LD\_ARCHIVES for the touch archive. The arch fragment sets CONFIG\_XNU\_BUILD\_ARCHIVES, CONFIG\_XNU\_NATIVE\_AES, CONFIG\_XNU\_NATIVE\_ARCH\_TIMER and CONFIG\_XNU\_NATIVE\_PAN; the OS fragment sets CONFIG\_XNU\_SOURCE\_MOCKFS.
- \[kernel\] archives in build order: corecrypto \(plain and namespaced\), ArmDTPlatform, ArmCpu, SoftwareAES and its bindings, libpthread, the mockfs fixture, build-fuxi-touch.py.

### 操作步骤

- ./unixnu defconfig fuxi\_defconfig -D ../unixnu-fuxi
- ./unixnu status --json
- ./unixnu build kernel

### 开发经验

- CI \(.github/workflows/build.yml\) pins OddlyLabs/UniXNU and OddlyLabs/uefi-fuxi at full revisions; after merging upstream into either fork, update UNIXNU\_REF or UEFI\_REF and let the image job run again.
- The image job installs Homebrew's openssl@3 itself rather than relying on the runner image: the encryption step uses OpenSSL 3 \(PBKDF2 for the image, RSA-OAEP with SHA-256 for its key\).
- The host tests byte-compile scripts/\*.py and ci/\*.py and parse ci/decrypt-boot-image.sh with bash -n, so the image tools are checked on every push.
- The merged configuration is the arch, SoC and OS fragments followed by the defconfig; the archive list has to cover every archive the merged options require, not only those of the template defconfig.
- CONFIG\_XNU\_SOURCE\_MOCKFS \(OS fragment\) makes vfs\_conf.o reference mockfs, so the link needs build/mockfs-fixture/libmockfs\_fixture.a: the first CI kernel build at 450f518 applied all 62 patches and built every listed archive, then stopped at that missing archive.
- ArmCpu needs the source corecrypto provider, so corecrypto is built before the components, as in UniXNU-sheng.

### 完成条件

- All source pins resolve; every selected component has a record; status shows the intended overrides and patch order.

### 当前范围

- unixnu.lock is not committed yet.

### 下一步

- Run ./unixnu fetch and commit unixnu.lock.

### 证据

- `source`: [Board selection and archive order](https://github.com/OddlyLabs/unixnu-fuxi/blob/77c0a035d49008df4ccafe617456c3c2e62d1dc0/board.toml)
- `host`: [All sources resolved, 62 patches applied, nine archives built, kernel linked and prelinked](https://github.com/OddlyLabs/unixnu-fuxi/actions/runs/41261795785)
  Command: <code>./unixnu defconfig fuxi_defconfig; ./unixnu build kernel</code>. Revision: `8b4c03f69fc15878d7ee92c0f157215fa235d78d`.

## 固件与启动 {#firmware}

`host-verified`

组件: `DarwinBoot`.

### 硬件与依赖

- OddlyLabs/uefi-fuxi, branch fuxi: a fork of UniXNU/uefi-sheng \(the official Mu-Silicium fork for UniXNU\) with the nine fuxi bring-up commits of matejkoo217/uefi-fuxi cherry-picked \(authors kept, cherry-pick -x\); its fuxiPkg derives from Silicium's SM8550 nuwa \(Xiaomi 13 Pro\).
- fastboot boot of the image \(temporary, nothing is written to the device\).

### 配置

- board.toml \[firmware\]: config fuxi, dsc Platforms/Xiaomi/fuxiPkg/fuxi.dsc, fd Build/fuxiPkg/&\#123;target&\#125;\_CLANGPDB/FV/SILICIUM\_UEFI.fd, and the submodules, edk2 patch and package path list of UniXNU-sheng's \[firmware\].
- fuxi.dsc: FUXI\_VENDOR\_HW = 0 \(Mu drivers only; the previous stage keeps the panel scanning out\), framebuffer 1080x2400x32, DDR base 0x80000000, the UniXNU menu, UniXNUDxe, DarwinBoot, DiskIo, Partition and FAT; FuxiBootMemoryDxe publishes the payload volume the shim hands over.

### 操作步骤

- ./unixnu build firmware --uefi ../uefi-fuxi --target DEBUG \(CI: the image job of .github/workflows/build.yml\).

### 开发经验

- UniXNU provides the boot menu \(UniXNUPkg\) and the XNU loader \(DarwinBoot\) as UEFI modules; the board firmware that runs them on the phone is a Mu-Silicium platform, and upstream Mu-Silicium has no fuxi platform.
- Measured on hardware in matejkoo217/uefi-fuxi: with text offset 0 in the shim's ARM64 header the ABL loads the image and the firmware's DEBUG console prints on the panel; with the firmware address there the ABL answers Load Error.
- The firmware's FdtBlob \(sm8550-xiaomi-fuxi.dtb, model 8550 fuxi, msm-id 0x207, board-id 0x10008\) carries the root properties the ABL selects an appended DTB by; the DTB merged from OS3.0.309 keeps the base DTB's board-id 0 and is not used for the boot image.
- fuxiPkg Include/RAW.inc listed the vendor raw files SecParti.cfg, uefipil.cfg and QcomChargerCfg.cfg outside the FUXI\_VENDOR\_HW gate, so the first firmware build in CI \(run 41268231266 at 72300f2\) stopped at the missing Binaries/nuwa/RawFiles/SecParti.cfg; uefi-fuxi 87554bf9 gates them with their drivers.
- With FUXI\_VENDOR\_HW = 0 the volume holds UniXNU, UniXNUDxe, DarwinBoot, FuxiBootMemoryDxe, SimpleFbDxe, FAT, PartitionDxe and DiskIoDxe. FuxiGopLogDxe and FuxiDisplayDepexDxe are compiled but enter the volume only with USE\_CUSTOM\_DISPLAY\_DRIVER = 1.

### 完成条件

- Firmware image builds, enters UniXNU, publishes the framebuffer and preserves the documented memory reservations.

### 当前范围

- No device evidence with this exact checkout: the hardware results above are matejkoo217's and Kerfand's \(who reached XNU with the same commits through a fork\).

### 下一步

- Boot the CI image with fastboot boot and confirm the UniXNU menu and the DarwinBoot handoff.

### 证据

- `source`: [Firmware fork with the fuxi platform](https://github.com/OddlyLabs/uefi-fuxi/tree/fuxi)
- `host`: [DEBUG SILICIUM\_UEFI.fd built at 0x300000 bytes with the UniXNU menu, UniXNUDxe, DarwinBoot and FuxiBootMemoryDxe in the volume](https://github.com/OddlyLabs/uefi-fuxi/commit/87554bf90a6f5707ceeb3720b3dc507de914db94)
  Command: <code>./unixnu build firmware --uefi ../uefi-fuxi --target DEBUG (Ubuntu 26.04, clang 21.1.8, uefi-fuxi 87554bf90a6f5707ceeb3720b3dc507de914db94, UniXNU 6ae4c252937ae1920ab68eaded10fc78447e0194)</code>. Revision: `72300f2b07ccee230e07caa7b31f5af269b4f942`.
- `host`: [DEBUG firmware from uefi-fuxi 87554bf9 built on macOS 26 at 0x300000 bytes \(fd\_sha256 627fe52af360...\) and packed into the boot image](https://github.com/OddlyLabs/unixnu-fuxi/actions/runs/41273003819)
  Command: <code>./unixnu build firmware --uefi ../uefi-fuxi --target DEBUG</code>. Revision: `2bbd3993e97081db16d8ecc00c58c78f53200b8e`.

## CPU 与中断 {#cpu}

`planned`

### 硬件与依赖

- CPU layout and GIC ranges of SM8550 v2 \(soc\_id 519\) from the stock device tree.

### 配置

- The template ArmCpu and ArmDTPlatform selection.

### 操作步骤

- Boot to the XNU entry checkpoint and record the enabled CPUs.

### 开发经验

- No fuxi CPU observation yet.

### 完成条件

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU.

### 当前范围

- Hardware inputs are not recorded in dts/fuxi.dts beyond the SoC DTSI.

### 下一步

- Record the CPU and GIC nodes from the stock device tree.

### 证据

按下一步操作收集证据。

## 内存与 DMA {#memory}

`planned`

### 硬件与依赖

- DRAM and reserved-memory nodes of the stock device tree; the apps SMMU at 0x15000000.

### 配置

- dts/fuxi.dts includes sm8550.dtsi and sets model and compatible; package/SmmuBypass.h is the UniXNU-sheng pass-through stream helper the touch probe uses for stream 0xa3.

### 操作步骤

- Fill the memory map from the stock device tree and the firmware's memory map.

### 开发经验

- fuxi and sheng share the touch engine's SMMU stream \(0xa3\).

### 完成条件

- All handoff regions are accounted for and each enabled DMA engine accesses its allocated range with the documented cache policy.

### 当前范围

- The DTS memory map is the SoC default.

### 下一步

- Record the DRAM size and reservations of the device.

### 证据

按下一步操作收集证据。

## 存储与根卷 {#storage}

`planned`

### 硬件与依赖

- UFS host of SM8550; the GPT of LUN 0 \(userdata\) on the device.

### 配置

- CONFIG\_XNU\_NATIVE\_UFS is not set.

### 操作步骤

- Select a UFS component after the firmware boots.

### 开发经验

- Other fuxi ports report the UFS controller hand-off from the firmware as usable; not reproduced here.

### 完成条件

- Host: register, clock, link and SMMU facts match the board inventory.

### 当前范围

- No storage driver is selected.

### 下一步

- Choose the root path \(RAM root or UFS\) once the firmware boots.

### 证据

按下一步操作收集证据。

## 显示 {#display}

`planned`

### 硬件与依赖

- Panel xiaomi m3 38 0c 0a \(Samsung DDIC by its command set\), 1080x2400, DSI0 command mode with DSC 8 bpp, slices 540x40, 1.1 GHz.
- Splash framebuffer 0xb8000000 \(0x2b00000\), 32 bpp, stride 1080 pixels, the same region as sheng.

### 配置

- package/FuxiPanelBoard.h holds the panel and controller constants with their sources; no display component is selected.

### 操作步骤

- First stage: keep the firmware framebuffer \(GopFramebuffer route\), as sheng does.

### 开发经验

- 73 DSI command sequences of the panel are decoded in facts/panel\_cmds\_\*.txt.
- The PPS in the on-command gives pic\_height 2520 while the timing and page address give 2400; unresolved.

### 完成条件

- A known frame appears with correct geometry and colors, then userland presentation and backlight controls work.

### 当前范围

- No device evidence for display.

### 下一步

- Read the framebuffer the firmware publishes on fuxi \(address, stride, format\).

### 证据

- `source`: [Panel facts with sources \(section 3\)](https://github.com/OddlyLabs/unixnu-fuxi/blob/77c0a035d49008df4ccafe617456c3c2e62d1dc0/fuxi_touch_panel_porting.md)

## 输入 {#input}

`implemented`

组件: `QcomGeniSpi`, `FuxiFtsTouch`.

### 硬件与依赖

- Stock device tree \(OS3.0.309 vendor\_boot DTB\[2\] with dtbo\[4\], merged with fdtoverlay\): /soc/qcom,qupv3\_1\_geni\_se@ac0000/spi@a90000/fts@0, compatible st,spi, 12 MHz, SPI mode 0.
- Controller ST FingerTip FTM5, chip id 36 40, firmware 53.42 kept in its own flash \(/proc/tp\_fw\_version on Android\), tp-vendor 0x38.
- Bus QUP1 SE4 at 0xa90000, wrapper 0xac0000, SMMU stream 0xa3; pins 44-47 \(qup1\_se4\); interrupt GPIO 25 \(active low, TLMM summary SPI 208\); reset GPIO 24.
- Rails vdd ldob12 1.8 V \(RPMh 0x40900\) and avdd ldom6 3.2 V \(RPMh 0x41b00\), measured with root on Android; their only consumer is spi0.0.

### 配置

- board.toml \[components\] selects QcomGeniSpi and FuxiFtsTouch; \[kernel\] archives runs scripts/build-fuxi-touch.py.
- configs/fuxi\_defconfig links build/fuxi-touch/libFuxiTouch.a through CONFIG\_XNU\_EXTRA\_LD\_ARCHIVES; patches/xnu/fuxi-touch-probe.patch calls native\_touch\_probe\(\) from bsd\_init after IOKitInitializeTime\(\).
- Boot arguments: fuxi-touch=1..4, fuxi-touch-panic=1 or 2, fuxi-touch-hz, fuxi-touch-power, fuxi-touch-tcs, fuxi-touch-poll, fuxi-touch-map. board.toml sets fuxi-touch=3 fuxi-touch-panic=1.

### 操作步骤

- Stage 1: snapshot of the QUP clocks, the pins and the two rails in the command database.
- Stage 2: RPMh votes vdd then avdd in active TCS 2 of apps RSC DRV2 \(tcs-offset 0xd00\), wait 3 ms, vote the QUP clocks, configure the pins.
- Stage 3: GENI SPI at 12 MHz; reset low 10 ms; wait for event 03 \(2 ms polls, 100 ms, three tries, then the ICR 4-wire fallback and the chip id\); read the chip id.
- Stage 4: A0 00 00, 50 ms, A0 00 01; falling-edge interrupt; drain the FIFO; publish contacts in the ShengHidInput ABI.
- Host: run the FuxiFtsTouch tests and tests/board\_test.c \(README\).

### 开发经验

- The fts\_spi driver dispatches events on the high nibble of byte 0, whose bits 2-3 carry the top of the major axis, so 0x13 to 0x1F are all enter events.
- Coordinates are ten times the panel pixels \(fts,support-super-resolution\): 0..10800 x 0..24000; the probe maps them to the 30480 x 20320 range that ShengHidInput scales from.
- Both touch rails stay on while Android runs, also with the screen off, and carry no boot-on property, so the probe votes them before it touches the controller.

### 完成条件

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive, and buttons produce expected HID reports.

### 当前范围

- No device evidence. Unverified: whether the RPMh done bit sets without the TCS interrupt enabled, the axis directions, and the HID orientation on a portrait panel.
- GENI has no setting for the 10 us chip-select hold the vendor driver uses \(SPI\_DELAY\_CS\).

### 下一步

- Boot an image with fuxi-touch=3 fuxi-touch-panic=1 and read the FTS rows on the panic screen: reset result 0 and chip id 36 40.

### 证据

- `source`: [FTM5 protocol and contact tracking with host tests](https://github.com/OddlyLabs/FuxiFtsTouch)
- `source`: [Staged board probe](https://github.com/OddlyLabs/unixnu-fuxi/blob/77c0a035d49008df4ccafe617456c3c2e62d1dc0/package/FuxiTouchProbe.cpp)
- `source`: [Touch facts with sources and the Android measurements \(sections 2 and 6\)](https://github.com/OddlyLabs/unixnu-fuxi/blob/77c0a035d49008df4ccafe617456c3c2e62d1dc0/fuxi_touch_panel_porting.md)

## GPU {#gpu}

`planned`

### 硬件与依赖

- Adreno 740 of SM8550, the same GPU as sheng.

### 配置

- CONFIG\_XNU\_NATIVE\_ADRENO is not set.

### 操作步骤

- Reuse the sheng GPU components after display and storage work.

### 开发经验

- No fuxi GPU observation yet.

### 完成条件

- GPU submissions complete, mapping/fence handling is correct, a known image renders, and the selected Metal client presents it.

### 当前范围

- Not started.

### 下一步

- None before the first boot.

### 证据

按下一步操作收集证据。

## 网络 {#network}

`planned`

### 硬件与依赖

- The Wi-Fi chip of the board, from the stock device tree.

### 配置

- No network component is selected.

### 操作步骤

- Identify the Wi-Fi chip and its bus.

### 开发经验

- No fuxi network observation yet.

### 完成条件

- Scanning, association, address configuration and sustained receive/transmit traffic pass with the selected firmware.

### 当前范围

- Not started.

### 下一步

- None before the first boot.

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`planned`

### 硬件与依赖

- The audio DSP and codec of the board.

### 配置

- No audio component is selected.

### 操作步骤

- Identify the codec and amplifiers from the stock device tree.

### 开发经验

- No fuxi audio observation yet.

### 完成条件

- Each declared route carries the selected audio format through playback or capture and handles start/stop correctly.

### 当前范围

- Not started.

### 下一步

- None before the first boot.

### 证据

按下一步操作收集证据。

## 电源 {#power}

`planned`

### 硬件与依赖

- RPMh command database \(/sys/kernel/debug/cmd-db on Android\) and the regulator summary with the screen on and off.

### 配置

- package/QcomRpmh.c and QcomRpmh.h are the UniXNU-sheng RPMh helpers; the touch probe uses them for its two rails.

### 操作步骤

- Record each rail a driver needs from the command database and the regulator summary.

### 开发经验

- Panel rails vci 3.0 V, vddio 1.8 V and vddd 1.5 V are off while the screen is off; the touch rails stay on.

### 完成条件

- Declared power controls and battery readings match observations; each claimed sleep/resume transition restores its dependent peripherals.

### 当前范围

- Only the touch rails are used.

### 下一步

- None before the first boot.

### 证据

按下一步操作收集证据。

## 镜像组装 {#packaging}

`host-verified`

组件: `XnuPrelink`.

### 硬件与依赖

- The iPadOS 17.7.11 restore image of the OS profile \(members fetched with range requests\), a platform seed, the firmware volume, the firmware's FdtBlob.

### 配置

- patches/xnu/series applies fuxi-touch-probe.patch after the arch, SoC and OS series.
- \[payload\] kernel\_args set the touch probe stage and its panic report; panic\_screen = true; \[payload.adt\] owned\_memory\_size 0x130000000.
- \[bootimg\] payload = "image" and \[bootimg.image\]: header v0 \(fuxi-legacy.toml's container\), text\_offset 0. The options are in OddlyLabs/UniXNU branch fuxi \(scripts/unixnu/bootimg.py\).

### 操作步骤

- ./unixnu build kernel; ./unixnu build payload --uefi ../uefi-fuxi --unique-chip-id &lt;seed&gt;; ./unixnu build firmware --uefi ../uefi-fuxi --target DEBUG; ./unixnu bootimg --uefi ../uefi-fuxi --target DEBUG --dtb &lt;FdtBlob&gt;.
- CI encrypts boot.img to ci/boot-image-recipient.pem; ci/decrypt-boot-image.sh decrypts it with the owner's private key.

### 开发经验

- fuxi-touch-probe.patch keeps only original XNU lines as context, so changes to the shared series around it do not break it.
- Measured on hardware in matejkoo217/uefi-fuxi: the ABL's fastboot boot refuses a header v4 image \(Invalid Parameter\), so the fastboot image uses the v0 container; and the ABL keeps the boot image ramdisk in vendor\_boot, so the payload follows the firmware volume and the image size at header offset 0x10 covers it \(Kerfand: 0x0C300200 for a 192 MiB payload\).
- The first kernel build in CI at 8b4c03f linked and prelinked; bsd\_init calls native\_touch\_probe in the linked kernel.
- The CI image at 2bbd399 advertises image size 0x0C300200 \(shim 0x200, firmware 0x300000, payload 0xC000000\), the value Kerfand measured for a booting 192 MiB payload. gzip brings the whole image to 11.1 MiB because the payload volume is mostly free space.
- The payload's ADT has dram-size 0x80000000 and darwinboot-memory-size 0x130000000, the values of UniXNU-sheng and of both community fuxi ports.

### 完成条件

- Kernel and prelink succeed, payload contains all declared inputs, and the boot image matches the bootloader format and size limit.

### 当前范围

- The platform seed in CI is a fixed bring-up value, not the phone's own; replace it before booting to userland.
- No boot image has been started on the device.

### 下一步

- Boot the decrypted image with fastboot boot \(the owner's decision\) and photograph the panic screen.

### 证据

- `host`: [Kernel linked and prelinked; bsd\_init calls \_native\_touch\_probe](https://github.com/OddlyLabs/unixnu-fuxi/actions/runs/41261795785)
  Command: <code>./unixnu build kernel --device fuxi</code>. Revision: `8b4c03f69fc15878d7ee92c0f157215fa235d78d`.
- `host`: [boot.img v0, 11677696 bytes \(sha256 931ac9582632...\), uploaded encrypted; decrypted with ci/decrypt-boot-image.sh, ci/check-boot-image.py passes: text offset 0, firmware and 192 MiB FUXIESP payload in the kernel image, FdtBlob appended, kernel.macho with the touch probe, its ADT and the boot arguments of board.toml](https://github.com/OddlyLabs/unixnu-fuxi/actions/runs/41273003819)
  Command: <code>./unixnu build payload --uefi ../uefi-fuxi --unique-chip-id 0x0123456789abcdef; ./unixnu bootimg --uefi ../uefi-fuxi --target DEBUG --dtb &lt;FdtBlob&gt;</code>. Revision: `2bbd3993e97081db16d8ecc00c58c78f53200b8e`.

## 诊断 {#diagnostics}

`implemented`

### 硬件与依赖

- The panic screen of the payload \(panic\_screen = true\) while no display driver runs.

### 配置

- fuxi-touch-panic=1 ends the boot with a panic whose message is the probe's four diagnostic rows; the rows are also printed to the kernel log at each stage.

### 操作步骤

- Photograph the panic screen and compare the FTS rows with fuxi\_touch\_panel\_porting.md section 7.2.

### 开发经验

- The other fuxi ports read their results from panic screen photographs as well.
- The DEBUG firmware prints its log on the panel before the handoff \(matejkoo217/uefi-fuxi\), the only console before the touch report.
- The earlier ci/ scripts compiled the probe inside a UniXNU-sheng build; the fuxi kernel build replaces them.
- ci/check-boot-image.py checks a decrypted image before fastboot boot against boot.json, board.toml and the firmware checkout: container and load addresses, the shim header, the firmware volume, the payload files, the ADT root and /chosen values, and the boot arguments.

### 完成条件

- Each claimed milestone has a reproducible command, a matching source/image revision and an accessible result.

### 当前范围

- No device log has been captured.

### 下一步

- Capture the first touch report from the device.

### 证据

- `source`: [Panic report and kernel log rows](https://github.com/OddlyLabs/unixnu-fuxi/blob/77c0a035d49008df4ccafe617456c3c2e62d1dc0/package/FuxiTouchProbe.cpp)
- `host`: [The image artifact decrypts with the owner's key \(sha256 matches boot.img.sha256\) and every check passes; a tampered boot.json fails two checks](https://github.com/OddlyLabs/unixnu-fuxi/actions/runs/41273003819)
  Command: <code>bash ci/decrypt-boot-image.sh &lt;key&gt; &lt;artifact&gt;; python3 ci/check-boot-image.py boot.img boot.json ../uefi-fuxi</code>. Revision: `2bbd3993e97081db16d8ecc00c58c78f53200b8e`.

</div>
