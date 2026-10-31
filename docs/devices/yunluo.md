# Redmi Pad format-2 qualification candidate; boot Mu and cust UniXNU must remain separate

[woaphone/UniXNU-yunluo](https://github.com/woaphone/UniXNU-yunluo)

<div v-pre>

Redmi Pad MT6789 format-2 qualification; Mu in boot, UniXNU in cust. Not yet build- or device-qualified.

Source record: [porting.toml](https://github.com/woaphone/UniXNU-yunluo/blob/c2b81b9f4f5ded51b114008e60baadc1f53ee89b/porting.toml), `c2b81b9f4f5ded51b114008e60baadc1f53ee89b`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `planned` |
| [Firmware and boot](#firmware) | `planned` |
| [CPU and interrupts](#cpu) | `planned` |
| [Memory and DMA](#memory) | `planned` |
| [Storage and root](#storage) | `planned` |
| [Display](#display) | `planned` |
| [Input](#input) | `planned` |
| [GPU](#gpu) | `planned` |
| [Network](#network) | `planned` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `planned` |
| [Image assembly](#packaging) | `planned` |
| [Diagnostics](#diagnostics) | `planned` |

## Configuration {#configuration}

`planned`

Components: `ArmDTPlatform`, `SoftwareAES`.

### Hardware and dependencies

- Current format-2 framework, selected OS profile, local MT6789 SoC commit d179fac7d291ae05b3546aa0abe04bf1a17475ca

### Configuration

- Profiles resolve in arch/SoC/OS/device order; arrays replace inherited arrays.

### Procedure

- Use the corresponding current UniXNU common guide; preserve source pins and collect the result before progressing.
- Integrate every required runtime component and publish reviewed SoC/component pins before enabling an image build.

### Development findings

- Only the qualification core is selected. The full legacy MTK storage/input/display archive set is not yet migrated; this is not baseline equivalence.
- The initial public WIP pins woaphone/UniXNU-mt6789-common at cad9262392dd589b75c7c9bf38f3f6c256be6c31 and supplies an ignored local override example. It is source publication, not a completed runtime migration.

### Completion criteria

- All source pins resolve; every selected component has a record; status shows the intended overrides and patch order.

### Current limits

- Only the qualification core is selected. The full legacy MTK storage/input/display archive set is not yet migrated; this is not baseline equivalence.

### Next action

- Integrate every required runtime component and publish reviewed SoC/component pins before enabling an image build.

### Evidence

- `source`: [Explicit source/qualification boundary and outstanding runtime work; no new device proof.](https://github.com/woaphone/UniXNU-yunluo/blob/c2b81b9f4f5ded51b114008e60baadc1f53ee89b/docs/evidence/source-scope.md)
- `host`: [PASS: format-2 profile/defconfig generation on the explicit local SoC source; not a kernel build.](https://github.com/woaphone/UniXNU-yunluo/blob/c2b81b9f4f5ded51b114008e60baadc1f53ee89b/docs/evidence/defconfig.txt)
  Command: <code>python3 /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/UniXNU/unixnu defconfig yunluo_defconfig -D /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo --local-module soc:mt6789=/home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-mt6789-common --out /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo/out/structural-committed/configured</code>. Revision: `238f33cda2750f52c19748607cee6ca56f56e2a3`.
- `host`: [PASS: configured=true and five core components resolve; this is not the complete legacy runtime.](https://github.com/woaphone/UniXNU-yunluo/blob/c2b81b9f4f5ded51b114008e60baadc1f53ee89b/docs/evidence/configured-status.txt)
  Command: <code>python3 /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/UniXNU/unixnu status --json -D /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo --local-module soc:mt6789=/home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-mt6789-common --out /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo/out/structural-committed/configured</code>. Revision: `238f33cda2750f52c19748607cee6ca56f56e2a3`.

## Firmware and boot {#firmware}

`planned`

Components: `DarwinBoot`.

### Hardware and dependencies

- Mu-Silicium platform firmware, BootShim and stock boot/vendor\_boot protocol inputs.

### Configuration

- boot contains Mu firmware only; UniXNU and file-loaded DarwinBoot belong in cust.

### Procedure

- Use the corresponding current UniXNU common guide; preserve source pins and collect the result before progressing.
- Separate FV integration from cust EFI files, then prove the actual cust entry load path without the old ramdisk fallback.

### Development findings

- The format-2 candidate has not built a complete cust chainload path.
- The independent v4 firmware and cust-v2 artifacts have source/offline evidence, but are not a clean build of this format-2 configuration.
- loader/ publishes the exact source-only largest-window reference and its provenance. It is not yet selected by the board build; no new device or desktop result is claimed.

### Completion criteria

- Firmware image builds, enters UniXNU, publishes the framebuffer and preserves the documented memory reservations.

### Current limits

- The old FV embeds loader/application modules; a cust chainload path has not been built or tested.

### Next action

- Separate FV integration from cust EFI files, then prove the actual cust entry load path without the old ramdisk fallback.

### Evidence

- `source`: [Explicit source/qualification boundary and outstanding runtime work; no new device proof.](https://github.com/woaphone/UniXNU-yunluo/blob/c2b81b9f4f5ded51b114008e60baadc1f53ee89b/docs/evidence/source-scope.md)
- `source`: [Published loader reference and paired firmware provenance, with unresolved format-2 integration and device scope.](https://github.com/woaphone/UniXNU-yunluo/blob/c2b81b9f4f5ded51b114008e60baadc1f53ee89b/docs/evidence/publication-scope.md)
- `host`: [PASS: production largest-window helper and source models under ASan/UBSan, plus normal/base record checks. No device allocation or complete runtime build.](https://github.com/woaphone/UniXNU-yunluo/blob/c2b81b9f4f5ded51b114008e60baadc1f53ee89b/docs/evidence/publication-host-checks.json)
  Command: <code>gcc -O1 -g -Wall -Wextra -fsanitize=address,undefined -I loader/DarwinBoot/DarwinBootPkg/Driver tests/largest-window.c -o out/largest-window &amp;&amp; ./out/largest-window</code>. Revision: `db777162eccdde5c6854750786e24fa8e6afe52b`.

## CPU and interrupts {#cpu}

`planned`

Components: `ArmCpu`.

### Hardware and dependencies

- Six Cortex-A55 plus two Cortex-A76; source ADT affinities 0..0x700 in 0x100 steps, GICv3 and 13 MHz timer.

### Configuration

- Board DTS includes the MT6789 DTSI; selected CPU driver and Apple CPU-node ABI must be audited together.

### Procedure

- Use the corresponding current UniXNU common guide; preserve source pins and collect the result before progressing.
- Compare reg/cpu-id/reg-private and GIC ranges against the preserved working ABI before a new boot.

### Development findings

- A DTS compile cannot prove CPU start or IPIs; old ADT vs current common-converter CPU properties need comparison.

### Completion criteria

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU.

### Current limits

- A DTS compile cannot prove CPU start or IPIs; old ADT vs current common-converter CPU properties need comparison.
- New common output omits cpu-id/no-aic-ipi-required present in the preserved working generator; validate the selected component/kext consumers before boot.

### Next action

- Compare reg/cpu-id/reg-private and GIC ranges against the preserved working ABI before a new boot.

### Evidence

- `source`: [Explicit source/qualification boundary and outstanding runtime work; no new device proof.](https://github.com/woaphone/UniXNU-yunluo/blob/c2b81b9f4f5ded51b114008e60baadc1f53ee89b/docs/evidence/source-scope.md)
- `host`: [PASS: sourced eight-CPU/GIC/timer description compiles without diagnostics; not CPU start/IPI proof.](https://github.com/woaphone/UniXNU-yunluo/blob/c2b81b9f4f5ded51b114008e60baadc1f53ee89b/docs/evidence/dtc.txt)
  Command: <code>dtc -I dts -O dtb -i /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-mt6789-common/dts -o /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo/out/structural-committed/hardware.dtb /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo/dts/yunluo.dts</code>. Revision: `238f33cda2750f52c19748607cee6ca56f56e2a3`.

## Memory and DMA {#memory}

`planned`

### Hardware and dependencies

- Six-GiB board DRAM declaration, 2.5-GiB requested loader window, existing reservations and DMA ownership.

### Configuration

- DRAM starts at 0x40000000; requested owned window 0xa0000000, not proof of a new allocation.

### Procedure

- Use the corresponding current UniXNU common guide; preserve source pins and collect the result before progressing.
- Account for every firmware reservation and DMA engine; compare generated ADT and actual loader allocation.

### Development findings

- No new DMA/SMMU/reservation qualification; historical 2.5-GiB log is not evidence for this proposed branch.
- The largest-window source helper and tests preserve reserved edges and real allocation accounting. This source reference is not yet enabled by the format-2 candidate and does not prove successful device allocation.

### Completion criteria

- All handoff regions are accounted for and each enabled DMA engine accesses its allocated range with the documented cache policy.

### Current limits

- No new DMA/SMMU/reservation qualification; historical 2.5-GiB log is not evidence for this proposed branch.

### Next action

- Account for every firmware reservation and DMA engine; compare generated ADT and actual loader allocation.

### Evidence

- `source`: [Explicit source/qualification boundary and outstanding runtime work; no new device proof.](https://github.com/woaphone/UniXNU-yunluo/blob/c2b81b9f4f5ded51b114008e60baadc1f53ee89b/docs/evidence/source-scope.md)
- `host`: [PASS: common ADT conversion on synthetic host identity, declared memory and placeholders; no allocation/DMA proof.](https://github.com/woaphone/UniXNU-yunluo/blob/c2b81b9f4f5ded51b114008e60baadc1f53ee89b/docs/evidence/make-adt.txt)
  Command: <code>python3 /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/UniXNU/scripts/make-adt.py --dtb /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo/out/structural-committed/hardware.dtb --os-profile /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/UniXNU/profiles/os/ipados-17.7.11-21H461/profile.toml --board /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo/board.toml --unique-chip-id 0x594c4e554d543637 --data-ramdisk --trust-cache --output /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo/out/structural-committed/kernel.macho.adt</code>. Revision: `238f33cda2750f52c19748607cee6ca56f56e2a3`.

## Storage and root {#storage}

`planned`

### Hardware and dependencies

- MTK UFS LU2/4096-byte blocks and host 0x11270000/0x2300; actual cust GPT/LP identity and capacity are required.

### Configuration

- cust owns the separate UniXNU filesystem. Persistent Data is independent and is not enabled by this layout.

### Procedure

- Use the corresponding current UniXNU common guide; preserve source pins and collect the result before progressing.
- Obtain saved GPT/LP metadata, qualify direct firmware visibility, and migrate the real MTK transport without Qualcomm aliases.

### Development findings

- No cust geometry/type/GUID/filesystem has been established. NativeMtkUfs is not ShengUfs; UFS transport is not in this core-only candidate.
- Boot-Mu/cust-UniXNU separation is enforced as a source-policy and release gate; cust geometry/discovery remain unknown, so the build-readiness gate correctly refuses progression.

### Completion criteria

- Actual cust partition type/capacity and firmware block/filesystem visibility are established without guessed geometry.
- Qualified MTK reads identify GPT/LUN/root windows correctly and launchd starts; persistent Data tests remain a separate explicit scope/authorization.

### Current limits

- No cust geometry/type/GUID/filesystem has been established. NativeMtkUfs is not ShengUfs; UFS transport is not in this core-only candidate.

### Next action

- Obtain saved GPT/LP metadata, qualify direct firmware visibility, and migrate the real MTK transport without Qualcomm aliases.

### Evidence

- `source`: [Explicit source/qualification boundary and outstanding runtime work; no new device proof.](https://github.com/woaphone/UniXNU-yunluo/blob/c2b81b9f4f5ded51b114008e60baadc1f53ee89b/docs/evidence/source-scope.md)
- `host`: [Expected refusal: actual cust geometry, filesystem and firmware load-path verification are still missing.](https://github.com/woaphone/UniXNU-yunluo/blob/c2b81b9f4f5ded51b114008e60baadc1f53ee89b/docs/evidence/build-readiness-rejection.txt)
  Command: <code>python3 /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo/scripts/check-partition-layout.py --require-build-ready</code>. Revision: `238f33cda2750f52c19748607cee6ca56f56e2a3`.

## Display {#display}

`planned`

### Hardware and dependencies

- UEFI GOP handoff, 1200x2000 panel and 2048-pixel/8192-byte stride from existing source records.

### Configuration

- Preserve the qualified mod\_init ordering and donor vtable/selector ABI when integrating the actual implementation.

### Procedure

- Use the corresponding current UniXNU common guide; preserve source pins and collect the result before progressing.
- Port the actual display component and probe lifecycle, then test a known frame and userspace presentation.

### Development findings

- No display runtime or physical presentation is qualified on this branch; unknown SIGBUS fault PC remains unresolved.

### Completion criteria

- A known frame appears with correct geometry and colors, then userland presentation and backlight controls work.

### Current limits

- No display runtime or physical presentation is qualified on this branch; unknown SIGBUS fault PC remains unresolved.

### Next action

- Port the actual display component and probe lifecycle, then test a known frame and userspace presentation.

### Evidence

- `source`: [Explicit source/qualification boundary and outstanding runtime work; no new device proof.](https://github.com/woaphone/UniXNU-yunluo/blob/c2b81b9f4f5ded51b114008e60baadc1f53ee89b/docs/evidence/source-scope.md)

## Input {#input}

`planned`

### Hardware and dependencies

- Yunluo PMIC state helper plus reusable Novatek protocol/core models; actual MTK bus/IRQ and yunluo sensor firmware remain separate inputs.

### Configuration

- Power uses TOPSTATUS bit1, volume-up bit3; inherited Qcom clock/pin/SMMU helpers are excluded.

### Procedure

- Use the corresponding current UniXNU common guide; preserve source pins and collect the result before progressing.
- Run scoped host regressions and qualify the actual sensor/firmware/bus/HID ABI before claiming touch works.

### Development findings

- Novatek tests model NT36532-family behavior, not a physical yunluo sensor. No real firmware blob, SPI rate, IRQ or HID consumer path is qualified here.
- Committed-source host models pass; their scope excludes real firmware, MTK bus timing, physical keys, IRQ and HID consumers. The area remains planned as an end-to-end input capability.
- The added largest-window host test is a loader arithmetic test, not additional physical input or HID qualification.

### Completion criteria

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive, and buttons produce expected HID reports.

### Current limits

- Novatek tests model NT36532-family behavior, not a physical yunluo sensor. No real firmware blob, SPI rate, IRQ or HID consumer path is qualified here.

### Next action

- Run scoped host regressions and qualify the actual sensor/firmware/bus/HID ABI before claiming touch works.

### Evidence

- `source`: [Explicit source/qualification boundary and outstanding runtime work; no new device proof.](https://github.com/woaphone/UniXNU-yunluo/blob/c2b81b9f4f5ded51b114008e60baadc1f53ee89b/docs/evidence/source-scope.md)
- `host`: [PASS under ASan/UBSan: 4096 PMIC state combinations and polling cases; register model only.](https://github.com/woaphone/UniXNU-yunluo/blob/c2b81b9f4f5ded51b114008e60baadc1f53ee89b/docs/evidence/pmic-state.txt)
  Command: <code>/usr/bin/g++ -O1 -g -Wall -Wextra -fsanitize=address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer -std=c++17 tests/board-key-state.cpp -o /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo/out/host-committed/pmic-state &amp;&amp; /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo/out/host-committed/pmic-state</code>. Revision: `238f33cda2750f52c19748607cee6ca56f56e2a3`.
- `host`: [PASS under ASan/UBSan: reusable protocol model; real-firmware cases explicitly skipped.](https://github.com/woaphone/UniXNU-yunluo/blob/c2b81b9f4f5ded51b114008e60baadc1f53ee89b/docs/evidence/novatek-protocol-model.txt)
  Command: <code>/usr/bin/gcc -O1 -g -Wall -Wextra -fsanitize=address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer -std=c11 drivers/NativeNovatekTouch/Test/nvt-protocol.c drivers/NativeNovatekTouch/NvtProtocol.c -o /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo/out/host-committed/novatek-protocol-model &amp;&amp; /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo/out/host-committed/novatek-protocol-model</code>. Revision: `238f33cda2750f52c19748607cee6ca56f56e2a3`.
- `host`: [PASS under ASan/UBSan: synthetic contact/core model; no physical sensor or HID client qualified.](https://github.com/woaphone/UniXNU-yunluo/blob/c2b81b9f4f5ded51b114008e60baadc1f53ee89b/docs/evidence/novatek-touch-core-model.txt)
  Command: <code>/usr/bin/gcc -O1 -g -Wall -Wextra -fsanitize=address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer -std=c11 drivers/NativeNovatekTouch/Test/touch-core.c drivers/NativeNovatekTouch/NvtTouchCore.c -lm -o /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo/out/host-committed/novatek-touch-core-model &amp;&amp; /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo/out/host-committed/novatek-touch-core-model</code>. Revision: `238f33cda2750f52c19748607cee6ca56f56e2a3`.

## GPU {#gpu}

`planned`

### Hardware and dependencies

- MT6789 Mali hardware identity and a compatible driver/frontend ABI, not Adreno firmware or GMU recipes.

### Configuration

- No Adreno/Qcom components are selected.

### Procedure

- Use the corresponding current UniXNU common guide; preserve source pins and collect the result before progressing.
- Inventory the actual Mali submission, memory/fence and presentation interfaces before choosing an implementation.

### Development findings

- GPU/Metal acceleration is planned and unsupported, not declared not-applicable to a device with a GPU.

### Completion criteria

- GPU submissions complete, mapping/fence handling is correct, a known image renders, and the selected Metal client presents it.

### Current limits

- GPU/Metal acceleration is planned and unsupported, not declared not-applicable to a device with a GPU.

### Next action

- Inventory the actual Mali submission, memory/fence and presentation interfaces before choosing an implementation.

### Evidence

- `source`: [Explicit source/qualification boundary and outstanding runtime work; no new device proof.](https://github.com/woaphone/UniXNU-yunluo/blob/c2b81b9f4f5ded51b114008e60baadc1f53ee89b/docs/evidence/source-scope.md)

## Network {#network}

`planned`

### Hardware and dependencies

- Board wireless bus, chipset, firmware, IRQ/DMA and OS network interface.

### Configuration

- No WLAN implementation is selected.

### Procedure

- Use the corresponding current UniXNU common guide; preserve source pins and collect the result before progressing.
- Inventory verified wireless resources and choose an implementation compatible with this board.

### Development findings

- Association and packet transfer are unimplemented; this is not not-applicable.

### Completion criteria

- Scanning, association, address configuration and sustained receive/transmit traffic pass with the selected firmware.

### Current limits

- Association and packet transfer are unimplemented; this is not not-applicable.

### Next action

- Inventory verified wireless resources and choose an implementation compatible with this board.

### Evidence

- `source`: [Explicit source/qualification boundary and outstanding runtime work; no new device proof.](https://github.com/woaphone/UniXNU-yunluo/blob/c2b81b9f4f5ded51b114008e60baadc1f53ee89b/docs/evidence/source-scope.md)

## Audio {#audio}

`planned`

### Hardware and dependencies

- MTK DSP/codec, clocks, firmware services and physical route inventory.

### Configuration

- No Qualcomm DSP/GLINK/QMP recipe is selected.

### Procedure

- Use the corresponding current UniXNU common guide; preserve source pins and collect the result before progressing.
- Establish the actual MTK audio resources and services before porting a route.

### Development findings

- Playback/capture are not implemented or verified.

### Completion criteria

- Each declared route carries the selected audio format through playback or capture and handles start/stop correctly.

### Current limits

- Playback/capture are not implemented or verified.

### Next action

- Establish the actual MTK audio resources and services before porting a route.

### Evidence

- `source`: [Explicit source/qualification boundary and outstanding runtime work; no new device proof.](https://github.com/woaphone/UniXNU-yunluo/blob/c2b81b9f4f5ded51b114008e60baadc1f53ee89b/docs/evidence/source-scope.md)

## Power {#power}

`planned`

### Hardware and dependencies

- MTK regulator/clock/battery units, firmware ownership and transition dependencies.

### Configuration

- A pure PMIC key-state model is not battery or suspend/resume support.

### Procedure

- Use the corresponding current UniXNU common guide; preserve source pins and collect the result before progressing.
- Identify source-confirmed controls and define per-transition observable tests.

### Development findings

- Sleep/resume, battery and peripheral power transitions remain unqualified.

### Completion criteria

- Declared power controls and battery readings match observations; each claimed sleep/resume transition restores its dependent peripherals.

### Current limits

- Sleep/resume, battery and peripheral power transitions remain unqualified.

### Next action

- Identify source-confirmed controls and define per-transition observable tests.

### Evidence

- `source`: [Explicit source/qualification boundary and outstanding runtime work; no new device proof.](https://github.com/woaphone/UniXNU-yunluo/blob/c2b81b9f4f5ded51b114008e60baadc1f53ee89b/docs/evidence/source-scope.md)

## Image assembly {#packaging}

`planned`

Components: `XnuPrelink`.

### Hardware and dependencies

- XNU 10063.141.1/21H461 ABI inputs and separately built Mu boot and UniXNU cust images.

### Configuration

- No UniXNU payload in boot ramdisk. Exact cust image size/filesystem awaits partition evidence.

### Procedure

- Use the corresponding current UniXNU common guide; preserve source pins and collect the result before progressing.
- Implement and test two-artifact manifests, boot payload exclusion and exact cust EFI/kernel/ADT contents before usability testing.

### Development findings

- No complete archive/bootstrap chain, kernel/prelink or split image build has passed; current upstream boot packer is not proven for this board v4 path.
- Boot-Mu/cust-UniXNU separation is enforced as a source-policy and release gate; cust geometry/discovery remain unknown, so the build-readiness gate correctly refuses progression.

### Completion criteria

- Separate boot firmware and cust UniXNU artifacts build from reviewed source pins; boot contains no UniXNU payload ramdisk; cust contains all declared EFI/runtime/kernel/ADT inputs.
- An explicitly authorized device test identifies both artifact hashes and proves Mu loads the intended cust path, not an old ramdisk or unrelated ESP.

### Current limits

- No complete archive/bootstrap chain, kernel/prelink or split image build has passed; current upstream boot packer is not proven for this board v4 path.

### Next action

- Implement and test two-artifact manifests, boot payload exclusion and exact cust EFI/kernel/ADT contents before usability testing.

### Evidence

- `source`: [Explicit source/qualification boundary and outstanding runtime work; no new device proof.](https://github.com/woaphone/UniXNU-yunluo/blob/c2b81b9f4f5ded51b114008e60baadc1f53ee89b/docs/evidence/source-scope.md)
- `host`: [PASS: split-header fixture accepted; embedded payload, empty/truncated kernel rejected. Fixture/header scope only.](https://github.com/woaphone/UniXNU-yunluo/blob/c2b81b9f4f5ded51b114008e60baadc1f53ee89b/docs/evidence/split-policy-fixtures.txt)
  Command: <code>python3 /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo/scripts/check-partition-layout.py --self-test /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo/out/structural-committed/fixtures</code>. Revision: `238f33cda2750f52c19748607cee6ca56f56e2a3`.
- `host`: [Expected refusal: protected historical monolithic image contains a nonempty boot ramdisk. No image changed.](https://github.com/woaphone/UniXNU-yunluo/blob/c2b81b9f4f5ded51b114008e60baadc1f53ee89b/docs/evidence/old-monolithic-image-rejection.txt)
  Command: <code>python3 /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo/scripts/check-partition-layout.py --boot-image /mnt/d/漏洞/UNIXNU/bringup/uefi/boot-yunluo-unixnu-inputfix6-smp8-mmioipi-2g.img</code>. Revision: `238f33cda2750f52c19748607cee6ca56f56e2a3`.

## Diagnostics {#diagnostics}

`planned`

### Hardware and dependencies

- Exact source/firmware/image revisions, accessible logs and official record/base-diff checks.

### Configuration

- Host and device evidence are distinct; publication is gated on real build and usable-boot proof.

### Procedure

- Use the corresponding current UniXNU common guide; preserve source pins and collect the result before progressing.
- Record real commands/results and full source revisions, then run the official normal and --base checks.

### Development findings

- No proposed-branch device log exists. Historical logs are not relabeled as fresh test evidence.

### Completion criteria

- Each claimed milestone has a reproducible command, a matching source/image revision and an accessible result.

### Current limits

- No proposed-branch device log exists. Historical logs are not relabeled as fresh test evidence.

### Next action

- Record real commands/results and full source revisions, then run the official normal and --base checks.

### Evidence

- `source`: [Explicit source/qualification boundary and outstanding runtime work; no new device proof.](https://github.com/woaphone/UniXNU-yunluo/blob/c2b81b9f4f5ded51b114008e60baadc1f53ee89b/docs/evidence/source-scope.md)
- `host`: [PASS: official checker validates the 13-area record schema and declared component coverage; not usability.](https://github.com/woaphone/UniXNU-yunluo/blob/c2b81b9f4f5ded51b114008e60baadc1f53ee89b/docs/evidence/record-check.txt)
  Command: <code>python3 /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/UniXNU/scripts/porting-record.py check --device /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo</code>. Revision: `238f33cda2750f52c19748607cee6ca56f56e2a3`.
- `host`: [PASS: proposed committed code changes have record ownership against porting-import-base.](https://github.com/woaphone/UniXNU-yunluo/blob/c2b81b9f4f5ded51b114008e60baadc1f53ee89b/docs/evidence/record-base-check.txt)
  Command: <code>python3 /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/UniXNU/scripts/porting-record.py check --device /home/ubuntu/unixnu-ext4/yunluo-upstream-20261030/release/UniXNU-yunluo --base porting-import-base</code>. Revision: `238f33cda2750f52c19748607cee6ca56f56e2a3`.

</div>
