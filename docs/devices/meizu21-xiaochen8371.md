# Meizu 21: UniXNU transition with retained Darwin22 kernel and protected APFS root \(XiaoChen8371\)

[XiaoChen8371/unixnu-meizu21](https://github.com/XiaoChen8371/unixnu-meizu21)

<div v-pre>

UniXNU transition: host menu/protocol verified; retained Darwin22 hardware path; r20 not device-tested.

Source record: [porting.toml](https://github.com/XiaoChen8371/unixnu-meizu21/blob/6e644239a9c937ec1ffebe17f171a72cfba7a2ec/porting.toml), `6e644239a9c937ec1ffebe17f171a72cfba7a2ec`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `host-verified` |
| [Firmware and boot](#firmware) | `host-verified` |
| [CPU and interrupts](#cpu) | `implemented` |
| [Memory and DMA](#memory) | `host-verified` |
| [Storage and root](#storage) | `implemented` |
| [Display](#display) | `host-verified` |
| [Input](#input) | `implemented` |
| [GPU](#gpu) | `planned` |
| [Network](#network) | `planned` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `implemented` |
| [Image assembly](#packaging) | `host-verified` |
| [Diagnostics](#diagnostics) | `host-verified` |

## Configuration {#configuration}

`host-verified`

### Hardware and dependencies

- SM8650, retained iOS16.5/Darwin22.5, source pins in unixnu.lock.

### Configuration

- Format 2 resolves the custom OS profile; inherited Darwin23 archives are explicitly replaced.

### Procedure

- Run scripts/package.sh --check, then scripts/package.sh; inspect the referenced evidence.

### Development findings

- Format 2 resolves the custom OS profile; inherited Darwin23 archives are explicitly replaced.

### Completion criteria

- Replace retained drivers with ABI-audited native component recipes.

### Current limits

- The selected native DarwinBoot source is for review only; stage 1 uses the board protocol adapter.

### Next action

- Replace retained drivers with ABI-audited native component recipes.

### Evidence

- `host`: [Format 2 resolves the custom OS profile; inherited Darwin23 archives are explicitly replaced.](https://github.com/XiaoChen8371/unixnu-meizu21/blob/6e644239a9c937ec1ffebe17f171a72cfba7a2ec/evidence/configure.log)
  Command: <code>bash scripts/package.sh</code>. Revision: `63f39b92ede3d30c53f8317d5607bb2ceb099342`.

## Firmware and boot {#firmware}

`host-verified`

### Hardware and dependencies

- Exact r19 DEBUG FD; real UniXNU 04573c5; retained loader SHA0be90c00; physical FB E3940000.

### Configuration

- DEBUG menu and production bridge compile; the bridge fits the existing embedded-loader slot.

### Procedure

- Run scripts/package.sh --check, then scripts/package.sh; inspect the referenced evidence.

### Development findings

- DEBUG menu and production bridge compile; the bridge fits the existing embedded-loader slot.

### Completion criteria

- Confirm menu and kernel handoff on Meizu21 after the owner returns.

### Current limits

- No r20 hardware boot. Current original firmware sources diverge from the stable binary.

### Next action

- Confirm menu and kernel handoff on Meizu21 after the owner returns.

### Evidence

- `host`: [DEBUG menu and production bridge compile; the bridge fits the existing embedded-loader slot.](https://github.com/XiaoChen8371/unixnu-meizu21/blob/6e644239a9c937ec1ffebe17f171a72cfba7a2ec/evidence/packaging-check.json)
  Command: <code>bash scripts/package.sh</code>. Revision: `63f39b92ede3d30c53f8317d5607bb2ceb099342`.

## CPU and interrupts {#cpu}

`implemented`

### Hardware and dependencies

- Retained loader uses GICD17100000/GICR17180000, core shift8, and default cpus=1.

### Configuration

- CPU/interrupt code is preserved in the independent kernel snapshot; no SMP behavior changed.

### Procedure

- Run scripts/package.sh --check, then scripts/package.sh; inspect the referenced evidence.

### Development findings

- CPU/interrupt code is preserved in the independent kernel snapshot; no SMP behavior changed.

### Completion criteria

- Preserve the working primary-core path while auditing native GIC/timer ABI.

### Current limits

- No new native ArmCpu integration or SMP verification.

### Next action

- Preserve the working primary-core path while auditing native GIC/timer ABI.

### Evidence

- `source`: [CPU/interrupt code is preserved in the independent kernel snapshot; no SMP behavior changed.](https://github.com/XiaoChen8371/unixnu-meizu21/blob/6e644239a9c937ec1ffebe17f171a72cfba7a2ec/evidence/kernel-snapshot.json)

## Memory and DMA {#memory}

`host-verified`

### Hardware and dependencies

- FD A4000000+400000, payload F0000000+3800000, retained kernel window B0000000..D8000000.

### Configuration

- All firmware file offsets and MemoryMap stay unchanged; bounded parser passes 100000 mutations.

### Procedure

- Run scripts/package.sh --check, then scripts/package.sh; inspect the referenced evidence.

### Development findings

- All firmware file offsets and MemoryMap stay unchanged; bounded parser passes 100000 mutations.

### Completion criteria

- Audit native DarwinBoot placement against 16KiB pages and actual free windows.

### Current limits

- QEMU does not establish DMA or SMMU behavior on SM8650.

### Next action

- Audit native DarwinBoot placement against 16KiB pages and actual free windows.

### Evidence

- `host`: [All firmware file offsets and MemoryMap stay unchanged; bounded parser passes 100000 mutations.](https://github.com/XiaoChen8371/unixnu-meizu21/blob/6e644239a9c937ec1ffebe17f171a72cfba7a2ec/evidence/xnup-r20-test.log)
  Command: <code>bash scripts/package.sh</code>. Revision: `63f39b92ede3d30c53f8317d5607bb2ceb099342`.

## Storage and root {#storage}

`implemented`

### Hardware and dependencies

- Existing UFS/APFS root and cryptex occupy protected super; boot\_a must remain intact.

### Configuration

- Packaging carries forward the exact small root ramdisk and meizu\_ufs/root\_apfs arguments.

### Procedure

- Run scripts/package.sh --check, then scripts/package.sh; inspect the referenced evidence.

### Development findings

- Packaging carries forward the exact small root ramdisk and meizu\_ufs/root\_apfs arguments.

### Completion criteria

- After menu validation, confirm existing root still mounts; keep super immutable.

### Current limits

- No root-image transformation, new partition geometry, userdata recipe or storage hardware test.

### Next action

- After menu validation, confirm existing root still mounts; keep super immutable.

### Evidence

- `source`: [Packaging carries forward the exact small root ramdisk and meizu\_ufs/root\_apfs arguments.](https://github.com/XiaoChen8371/unixnu-meizu21/blob/6e644239a9c937ec1ffebe17f171a72cfba7a2ec/evidence/inputs.json)

## Display {#display}

`host-verified`

### Hardware and dependencies

- Physical 1080x2340, BGRx32, stride4320, framebuffer E3940000.

### Configuration

- Real UniXNU renders a portrait menu at this geometry in QEMU; r16 Dock correction is retained.

### Procedure

- Run scripts/package.sh --check, then scripts/package.sh; inspect the referenced evidence.

### Development findings

- Real UniXNU renders a portrait menu at this geometry in QEMU; r16 Dock correction is retained.

### Completion criteria

- Check menu and Dock on the phone without changing memory reservations.

### Current limits

- QEMU validates menu layout, not phone panel presentation, backlight or acceleration.

### Next action

- Check menu and Dock on the phone without changing memory reservations.

### Evidence

- `host`: [Real UniXNU renders a portrait menu at this geometry in QEMU; r16 Dock correction is retained.](https://github.com/XiaoChen8371/unixnu-meizu21/blob/6e644239a9c937ec1ffebe17f171a72cfba7a2ec/evidence/qemu-result.log)
  Command: <code>bash scripts/package.sh</code>. Revision: `63f39b92ede3d30c53f8317d5607bb2ceb099342`.

## Input {#input}

`implemented`

### Hardware and dependencies

- Goodix GPIO48/49/50/51, reset161, IRQ162; raw coordinates10800x23400; TCS0 power path.

### Configuration

- Existing persistent quiet touch kernel and libhakios/backboardd bridge are preserved.

### Procedure

- Run scripts/package.sh --check, then scripts/package.sh; inspect the referenced evidence.

### Development findings

- Existing persistent quiet touch kernel and libhakios/backboardd bridge are preserved.

### Completion criteria

- Verify repeated iOS touches after r20 boot before replacing the HID path.

### Current limits

- r20 has not been phone-tested; touch input for the UEFI menu is not implemented.

### Next action

- Verify repeated iOS touches after r20 boot before replacing the HID path.

### Evidence

- `source`: [Existing persistent quiet touch kernel and libhakios/backboardd bridge are preserved.](https://github.com/XiaoChen8371/unixnu-meizu21/blob/6e644239a9c937ec1ffebe17f171a72cfba7a2ec/evidence/kernel-snapshot.json)

## GPU {#gpu}

`planned`

### Hardware and dependencies

- A750/SM8650; native DT profiles43051400 and43051401; stock Meizu firmware pins preserved locally.

### Configuration

- GPU probe remains off. Neither A740 rendering nor Ace5 preparation proves A750 rendering here.

### Procedure

- Run scripts/package.sh --check, then scripts/package.sh; inspect the referenced evidence.

### Development findings

- GPU probe remains off. Neither A740 rendering nor Ace5 preparation proves A750 rendering here.

### Completion criteria

- Read real SoC/GPU revision first, then port power and memory ownership before firmware execution.

### Current limits

- No Meizu GPU power/SMMU/GMU/HFI/CP submission, frontend ABI or Metal verification.

### Next action

- Read real SoC/GPU revision first, then port power and memory ownership before firmware execution.

### Evidence

- `source`: [GPU probe remains off. Neither A740 rendering nor Ace5 preparation proves A750 rendering here.](https://github.com/XiaoChen8371/unixnu-meizu21/blob/6e644239a9c937ec1ffebe17f171a72cfba7a2ec/evidence/inputs.json)

## Network {#network}

`planned`

### Hardware and dependencies

- Native WLAN adaptation and firmware transport are not migrated by the boot manager.

### Configuration

- No networking driver from another board is enabled in this transition.

### Procedure

- Run scripts/package.sh --check, then scripts/package.sh; inspect the referenced evidence.

### Development findings

- No networking driver from another board is enabled in this transition.

### Completion criteria

- Inventory Meizu WLAN transport/firmware after the boot/GPU migration stage.

### Current limits

- No working network claim or new radio operation.

### Next action

- Inventory Meizu WLAN transport/firmware after the boot/GPU migration stage.

### Evidence

Collect evidence using the next action.

## Audio {#audio}

`planned`

### Hardware and dependencies

- SM8650 DSP/codec routing requires board-specific firmware and service adaptation.

### Configuration

- Existing code is preserved; no Ace5 audio or modem initialization is imported.

### Procedure

- Run scripts/package.sh --check, then scripts/package.sh; inspect the referenced evidence.

### Development findings

- Existing code is preserved; no Ace5 audio or modem initialization is imported.

### Completion criteria

- Audit actual board audio resources and services before enabling a native driver.

### Current limits

- No audio playback/capture result.

### Next action

- Audit actual board audio resources and services before enabling a native driver.

### Evidence

Collect evidence using the next action.

## Power {#power}

`implemented`

### Hardware and dependencies

- Approved touch rails: ldob9=2960mV, ldob12=1800mV, HPM7; verified TCS0 response masks.

### Configuration

- The working touch voltage/ACK/recovery implementation remains in the retained kernel.

### Procedure

- Run scripts/package.sh --check, then scripts/package.sh; inspect the referenced evidence.

### Development findings

- The working touch voltage/ACK/recovery implementation remains in the retained kernel.

### Completion criteria

- Preserve existing touch power behavior; audit GPU resource ownership separately.

### Current limits

- No GPU rail write, new PMIC configuration, battery or suspend migration.

### Next action

- Preserve existing touch power behavior; audit GPU resource ownership separately.

### Evidence

- `source`: [The working touch voltage/ACK/recovery implementation remains in the retained kernel.](https://github.com/XiaoChen8371/unixnu-meizu21/blob/6e644239a9c937ec1ffebe17f171a72cfba7a2ec/evidence/kernel-snapshot.json)

## Image assembly {#packaging}

`host-verified`

### Hardware and dependencies

- Pinned complete r19 image, exact legacy loader, current linked kernel, stock DTB, DEBUG menu.

### Configuration

- Repacked image is unpacked and compared; kernel/root/cmdline/shim/DTB remain exact.

### Procedure

- Run scripts/package.sh --check, then scripts/package.sh; inspect the referenced evidence.

### Development findings

- Repacked image is unpacked and compared; kernel/root/cmdline/shim/DTB remain exact.

### Completion criteria

- Device-test r20 boot\_b while retaining the complete r16 rollback.

### Current limits

- r20 unflashed; native UniXNU userdata, generic payload and bootshim recipes are not used.

### Next action

- Device-test r20 boot\_b while retaining the complete r16 rollback.

### Evidence

- `host`: [Repacked image is unpacked and compared; kernel/root/cmdline/shim/DTB remain exact.](https://github.com/XiaoChen8371/unixnu-meizu21/blob/6e644239a9c937ec1ffebe17f171a72cfba7a2ec/evidence/packaging-check.json)
  Command: <code>bash scripts/package.sh</code>. Revision: `63f39b92ede3d30c53f8317d5607bb2ceb099342`.

## Diagnostics {#diagnostics}

`host-verified`

Components: `DarwinBoot`.

### Hardware and dependencies

- Logs include production DEBUG builds, bounded-parser sanitizers and QEMU menu/protocol receiver.

### Configuration

- The QEMU receiver exits before any phone kernel or hardware operation. Sources and image pins are recorded.

### Procedure

- Run scripts/package.sh --check, then scripts/package.sh; inspect the referenced evidence.

### Development findings

- The QEMU receiver exits before any phone kernel or hardware operation. Sources and image pins are recorded.

### Completion criteria

- Record the first phone menu/kernel/desktop checkpoint with image SHA after the owner returns.

### Current limits

- Host evidence must not be labelled hardware verification; native DarwinBoot ABI is still incompatible.

### Next action

- Record the first phone menu/kernel/desktop checkpoint with image SHA after the owner returns.

### Evidence

- `host`: [The QEMU receiver exits before any phone kernel or hardware operation. Sources and image pins are recorded.](https://github.com/XiaoChen8371/unixnu-meizu21/blob/6e644239a9c937ec1ffebe17f171a72cfba7a2ec/evidence/qemu-result.log)
  Command: <code>bash scripts/package.sh</code>. Revision: `63f39b92ede3d30c53f8317d5607bb2ceb099342`.

</div>
