# Xiaomi 13 \(kkkpc\)

[kkkpc/UniXNU-fuxi](https://github.com/kkkpc/UniXNU-fuxi)

<div v-pre>

Xiaomi 13 \(fuxi, SM8550\). Clean Format 2 port targeting iPadOS 17.7.11 \(iPad7,1, 21H461\), reusing device-verified board data from mouse233/unixnu-fuxi @ 45456925. M1 is host-side resolution only; this project has no result on its own device yet \(owner has an unlocked fuxi unit, capacity/GPT not yet read\).

源记录: [porting.toml](https://github.com/kkkpc/UniXNU-fuxi/blob/4def7458e908ae0c2d452beda445777bbff22cde/porting.toml), `4def7458e908ae0c2d452beda445777bbff22cde`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `host-verified` |
| [固件与启动](#firmware) | `host-verified` |
| [CPU 与中断](#cpu) | `planned` |
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

- Xiaomi 13 \(fuxi\), SM8550, owner's unlocked unit, 12 GB RAM + 256 GB storage \(same specification as mouse233's device-verified unit\).
- iPad\_Pro\_HFR\_17.7.11\_21H461\_Restore.ipsw \(iPad7,1\) as the OS payload, from the upstream OS profile.
- UniXNU main @ 5e839fb, UniXNU-sm8550-common pinned at a9f45dc in feeds.toml.

### 配置

- board.toml: name fuxi, soc SM8550, soc\_source sm8550, os\_profile ipados-17.7.11-21H461, kit fuxi; components ArmDTPlatform, ArmCpu, SoftwareAES, XnuPrelink, DarwinBoot \(M1 minimal set\).
- board.toml \[userdata\]: first\_lba 0x2F7840, last\_lba 0x3AFC3FA, lba\_bytes 4096, adopted from mouse233 for the same 12+256 specification; verify against this unit's own GPT before any write.
- .github/workflows/package.yml and .github/workflows/porting-record.yml are the template copies, added 2026-11-01 \(commits 2c13613, a408c63\) through the GitHub web UI because the Muse GitHub App has no workflows permission.

### 操作步骤

- ./unixnu defconfig fuxi\_defconfig -D ../UniXNU-fuxi
- ./unixnu fetch
- ./unixnu status --json
- ./unixnu tree
- python3 scripts/porting-record.py check --device ../UniXNU-fuxi
- GitHub macOS build workflow \(kkkpc/UniXNU fork\), steps=kernel, run 41287825448.

### 开发经验

- Host resolution passes end to end: profiles, component sources, overrides and patch order \(arch, soc, os, device\) resolve as intended; the assembled tree contains kits/fuxi; unixnu.lock pins xnu d8b8029 and sm8550 a9f45dc.
- CI kernel build succeeds: the macOS build run's Build kernel step completed in 8m 8s and its summary records kernel=success. The run's overall Failure conclusion comes only from the workflow's own Summary step crashing on \`xcodebuild -version \| head -n 1\` \(broken pipe, exit 134\) — an upstream workflow defect, not a board defect.
- The first Device documentation run \(41287869618\) failed its base check because the workflow-file commits did not update this record; this configuration update is that fix.
- Firmware source pinned 2026-11-01: mouse233/uefi-fuxi branch feat/ramdisk-test @ 32b3b57e4bb542136e1a932062e5b10c81b5f287, recorded in the board.toml \[firmware\] provenance comment.

### 完成条件

- All source pins resolve; every selected component has a record; status shows the intended overrides and patch order.

### 当前范围

- M1 minimal component set only; storage, display, input and GPU components are added per subsystem in porting order.
- The package workflow is still the template copy \(firmware repository placeholder\) and is not yet runnable.

### 下一步

- Add the storage components \(RamBlock, ShengUfs\) and their archive recipes for the M2/M3 RAM-root stage.

### 证据

- `host`: [Build kernel succeeded in 8m 8s; run summary records kernel=success. Run conclusion Failure is only the Summary step's xcodebuild broken-pipe crash \(exit 134\).](https://github.com/kkkpc/UniXNU/actions/runs/41287825448)
  Command: <code>macOS build workflow, steps=kernel, device kkkpc/UniXNU-fuxi, defconfig fuxi_defconfig</code>. Revision: `a408c635b87327c659fd73848ad74837279a13ce`.
- `host`: [All commands exit 0; status resolves fuxi / ipados-17.7.11-21H461 / sm8550 pin a9f45dc; assembled tree contains kits/fuxi.](https://github.com/kkkpc/UniXNU-fuxi/blob/4def7458e908ae0c2d452beda445777bbff22cde/board.toml)
  Command: <code>./unixnu defconfig fuxi_defconfig -D ../UniXNU-fuxi &amp;&amp; ./unixnu fetch &amp;&amp; ./unixnu status --json &amp;&amp; ./unixnu tree</code>. Revision: `aee06a785017892f5c0605efc8d98e458ef5ff3c`.
- `host`: [13 structured areas checked \(pass\) locally; the CI base check failed on the workflow-file commits until this record update.](https://github.com/kkkpc/UniXNU-fuxi/blob/4def7458e908ae0c2d452beda445777bbff22cde/.github/workflows/porting-record.yml)
  Command: <code>python3 scripts/porting-record.py check --device ../UniXNU-fuxi</code>. Revision: `aee06a785017892f5c0605efc8d98e458ef5ff3c`.

## 固件与启动 {#firmware}

`host-verified`

### 硬件与依赖

- mouse233/uefi-fuxi, branch feat/ramdisk-test @ 32b3b57e4bb542136e1a932062e5b10c81b5f287: fuxiPkg \(Mu-Silicium\), Resources/Configs/fuxi.toml, Resources/DTBs/fuxi.dtb \(stock Qualcomm DTB for this board\), Resources/Scripts/mkbootimg.py.
- FD layout from the device's own xbl\_config per the uefi config audit: FD\_BASE 0xA7100000, FD\_SIZE 0x300000.

### 配置

- board.toml \[firmware\]: config fuxi, dsc Platforms/Xiaomi/fuxiPkg/fuxi.dsc, fd Build/fuxiPkg/&\#123;target&\#125;\_CLANGPDB/FV/SILICIUM\_UEFI.fd, defines ENABLE\_SECUREBOOT=1, DEVICE\_MODEL=fuxi, MEMORY\_PROTECTION=TRUE.
- Boot image profile \(uefi Resources/Configs/fuxi.toml\): Android boot header v3, os\_version 17.0.0, os\_patch\_level 2026-07, measured from this phone model's stock boot\_b header; the DTB appended to the image is the stock fuxi DTB, not the XNU-side dts/fuxi.dts.

### 操作步骤

- ./unixnu build firmware -D ../UniXNU-fuxi --uefi ../uefi-fuxi \(EDK2 DEBUG CLANGPDB\)
- ./unixnu bootimg -D ../UniXNU-fuxi --uefi ../uefi-fuxi --dtb ../uefi-fuxi/Resources/DTBs/fuxi.dtb
- mkbootimg re-pack with --header\_version 3 --os\_version 17.0.0 --os\_patch\_level 2026-07 to match the stock container metadata, then a manual v3 unpack verification.

### 开发经验

- Firmware builds clean on the Linux host: SILICIUM\_UEFI.fd is exactly 0x300000 bytes as the config requires.
- fuxi's ABL profile is Android boot header v3 \(Xiaomi v3/v4 ABL path, per the uefi config audit\). UniXNU's layered bootimg verifier parses only v0 headers and rejects the image with 'boot image header does not match the requested parameters' even though mkbootimg produced it correctly; a manual v3 unpack verifies byte-exact round-trips of gzip\(BootShim + FD\) and the appended stock DTB. Forcing the profile to v0 is explicitly warned against in the uefi config without bootloader evidence, so v3 stands.
- The boot image carries an empty ramdisk: no payload yet, so this image is a firmware smoke test only \(UEFI on screen\); DarwinBoot entries arrive with the payload stage.

### 完成条件

- Firmware image builds, enters UniXNU, publishes the framebuffer and preserves the documented memory reservations.

### 当前范围

- Not yet run on this project's own unit: the first fastboot boot test is pending \(bench Mac, RAM only\). ABL acceptance of the v3 image and the receiver window behavior of this build are unproven on this hardware until that test.
- The layered driver's bootimg verification cannot validate v3 images \(v0-only parser\); images are verified by manual v3 unpack until upstream grows v3 support.

### 下一步

- fastboot boot fuxi-uefi-boot-v3.img on the owner's unit from the bench Mac; photograph the screen and record the reached stage here.

### 证据

- `host`: [Exit 0. SILICIUM\_UEFI.fd built \(3,145,728 bytes = FD\_SIZE 0x300000 at FD\_BASE 0xA7100000\), EDK2 DEBUG CLANGPDB, submodules at the checkout's pins.](https://github.com/mouse233/uefi-fuxi)
  Command: <code>./unixnu build firmware -D ../UniXNU-fuxi --uefi ../uefi-fuxi</code>. Revision: `32b3b57e4bb542136e1a932062e5b10c81b5f287`.
- `host`: [fuxi-uefi-boot-v3.img: 1,843,200 bytes, sha256 eb9f8855758febfdeebbc930ee7bde0bae7064713d3902377521eecf8cb24564. Header v3, header\_size 1580, kernel\_size 1,836,462; gzip stream ends exactly at the appended DTB, decompresses to BootShim \(192 bytes\) + the built FD byte-identical, appended DTB byte-identical to stock fuxi.dtb.](https://github.com/mouse233/uefi-fuxi/blob/feat/ramdisk-test/Resources/Configs/fuxi.toml)
  Command: <code>./unixnu bootimg --dtb ../uefi-fuxi/Resources/DTBs/fuxi.dtb, re-packed with mkbootimg --header_version 3 --os_version 17.0.0 --os_patch_level 2026-07; manual v3 unpack in Python (struct + zlib)</code>. Revision: `32b3b57e4bb542136e1a932062e5b10c81b5f287`.

## CPU 与中断 {#cpu}

`planned`

### 硬件与依赖

- Identify the cpu and interrupts hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for cpu and interrupts.

### 操作步骤

- Follow the cpu and interrupts stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first cpu and interrupts observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required cpu and interrupts inputs before implementation.

### 证据

按下一步操作收集证据。

## 内存与 DMA {#memory}

`planned`

### 硬件与依赖

- Identify the memory and dma hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for memory and dma.

### 操作步骤

- Follow the memory and dma stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first memory and dma observation, its cause when established, and the resulting implementation decision.

### 完成条件

- All handoff regions are accounted for and each enabled DMA engine accesses its allocated range with the documented cache policy.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required memory and dma inputs before implementation.

### 证据

按下一步操作收集证据。

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

- Identify the display hardware, resources and existing component interfaces for this board.

### 配置

- Record the board.toml fields, DTS properties and defconfig values used for display.

### 操作步骤

- Follow the display stage in the porting guide and record the actual commands.

### 开发经验

- Collect the first display observation, its cause when established, and the resulting implementation decision.

### 完成条件

- A known frame appears with correct geometry and colors, then userland presentation and backlight controls work.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

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

- Collect the first diagnostics observation, its cause when established, and the resulting implementation decision.

### 完成条件

- Each claimed milestone has a reproducible command, a matching source/image revision and an accessible result.

### 当前范围

- Hardware inputs and implementation are pending for this example board.

### 下一步

- Inventory the required diagnostics inputs before implementation.

### 证据

按下一步操作收集证据。

</div>
