# Lenovo TB710FU: minimal macOS 27 kernel bring-up, storage and hardware boot unqualified \(limingerf\)

[limingerf/UniXNU-tb710fu](https://github.com/limingerf/UniXNU-tb710fu)

<div v-pre>

Clean native-only macOS 27 kernel build for Lenovo TB710FU. Hardware boot, prelink and macOS userspace remain unqualified.

Source record: [porting.toml](https://github.com/limingerf/UniXNU-tb710fu/blob/cf643221155ba2cb185bf969eb5f90c8d6243d2f/porting.toml), `cf643221155ba2cb185bf969eb5f90c8d6243d2f`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `implemented` |
| [Firmware and boot](#firmware) | `host-verified` |
| [CPU and interrupts](#cpu) | `planned` |
| [Memory and DMA](#memory) | `planned` |
| [usb](#usb) | `host-verified` |
| [Storage and root](#storage) | `planned` |
| [Display](#display) | `planned` |
| [Input](#input) | `planned` |
| [GPU](#gpu) | `planned` |
| [Network](#network) | `planned` |
| [cellular](#cellular) | `planned` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `planned` |
| [Image assembly](#packaging) | `planned` |
| [Diagnostics](#diagnostics) | `planned` |

## Configuration {#configuration}

`implemented`

Components: `ArmDTPlatform`, `ArmCpu`, `XnuPrelink`.

### Hardware and dependencies

- Pinned official UniXNU and XNU revisions in upstream.lock.json; the macos-27.3-26C5035r profile; the repository-local soc feed.

### Configuration

- board.toml selects ArmDTPlatform, ArmCpu and XnuPrelink. Its explicit archive and patch arrays replace inherited arrays; preserve the recorded order.
- The patch order is arch, device pre-OS, OS, then device XNU. The kernel configuration includes arch common and OS macOS fragments.

### Procedure

- 1. Resolve the pinned official checkout and profile without editing fetched source caches.
- 2. Generate the selected defconfig and inspect the resolved status and component dependencies.
- 3. Run the bounded native-only macOS CI build and retain the source revisions, invocation and first actual failure or kernel artifact.

### Development findings

- The clean board identity matches this record. No USB or UFS controller component is selected; the local kit source currently holds a hardware-independent CDC protocol/log-ring slice.
- The previous workspace mixes initial skeletons and later experiments. It is evidence only and is not a feed for this clean build.

### Completion criteria

- Official record validation and resolved status pass with the intended identity, component closure, OS profile, archives and patch order.

### Current limits

- Run 43844823907 passed native and strict prelink; no device boot or runtime qualification is claimed by this record.

### Next action

- Capture a device checkpoint against the exact signed image hash; retain the native/PAC and hardware gates as separate work.

### Evidence

- `source`: [Defines the clean schema-2 identity, selected components and ordered kernel inputs.](https://github.com/limingerf/UniXNU-tb710fu/blob/cf643221155ba2cb185bf969eb5f90c8d6243d2f/board.toml)
- `source`: [Pins the official UniXNU, XNU, OS profile and mainline hardware reference.](https://github.com/limingerf/UniXNU-tb710fu/blob/cf643221155ba2cb185bf969eb5f90c8d6243d2f/upstream.lock.json)
- `host`: [Native arm64e compilation, strict prelink and production DarwinBoot parser passed. Prelinked kernel SHA-256 045bfc7cfad9ed2539a586043dd43211263099734f4978abd8092c213b7d7d95; 86 retained components, no missing or stubbed symbols. Hardware remains unqualified.](https://github.com/limingerf/UniXNU-tb710fu/actions/runs/43844823907)
  Command: <code>workflow_dispatch stage=prelink</code>. Revision: `e83bd00d94fc947ecdefd3fafdd471711561dff3`.

## Firmware and boot {#firmware}

`host-verified`

Components: `DarwinBoot`.

### Hardware and dependencies

- A clean pinned UEFI base and reviewed TB710FU overlay; locally held stock boot-chain backups; a qualified firmware DTB and framebuffer handoff.

### Configuration

- board.toml firmware selects the reviewed source-only TB710FU overlay on uefi-sheng 66421cb7; vendor gates remain closed.
- A separate shared SimpleFb patch validates memory lookup, range and GOP error paths. Tb710fuKeyInputDxe reads physical PMIC status through the v7 observer and publishes SimpleTextIn; source provenance and host checks are in docs/UEFI\_INPUT.md.

### Procedure

- 1. Check out pinned official UniXNU and uefi-sheng sources.
- 2. Apply the reviewed source patch and board overlay, then run the source-policy preflight.
- 3. Run the official build firmware command and inspect required GUIDs in the real nested FV/FFS volumes.

### Development findings

- Previous evidence records FD base 0xA7100000, FD size 0x300000 and Android boot header version 4. These are import candidates, not clean-build verification.
- The previous overlay disables custom display and vendor hardware DXE to preserve ABL scanout; enabling the whole vendor dependency chain was associated with loss of display.

### Completion criteria

- A pinned firmware build preserves reviewed memory reservations and enters the intended loader with a usable log channel on this board.

### Current limits

- The source-only overlay imports no proprietary firmware inputs. New hardware boot, scanout stride/format, reserved memory and EL1 PAC remain unqualified.
- A previous UniXNU menu observation does not qualify this rebuilt FD or macOS userspace.

### Next action

- The physical-key candidate passed cloud compilation and local ten-module FV verification. Next qualify physical keys on this exact FD in a separately authorized device test.

### Evidence

- `source`: [Records the fixed base, board delta, forty memory ranges and source-only limits.](https://github.com/limingerf/UniXNU-tb710fu/blob/cf643221155ba2cb185bf969eb5f90c8d6243d2f/docs/UEFI_AUDIT.md)
- `source`: [Explains the audited SimpleFb error-path fixes and their host checks.](https://github.com/limingerf/UniXNU-tb710fu/blob/cf643221155ba2cb185bf969eb5f90c8d6243d2f/firmware/patches/README.md)
- `host`: [Official AARCH64 DEBUG CLANGPDB firmware build passed; 3145728-byte FD and nine required modules verified in two actual nested FVs; SHA-256 independently verified in docs/evidence/uefi-build.json. Hardware remains unqualified.](https://github.com/limingerf/UniXNU-tb710fu/actions/runs/43618658596)
  Command: <code>python3 tools/ci_firmware.py build</code>. Revision: `4497de4724af619b9cd5ec74d9ec6a8354d459f9`.
- `host`: [Physical-key candidate compiled successfully; sanitized host model passed. The 3145728-byte FD SHA-256 4fc321fb77ebad6f63970ae617228eef6be3bf98d98af5cfd4497ea51cd85b9b independently matched; ten module GUIDs and fourteen overlay hashes verified. Physical keys remain unverified; exact provenance is in docs/evidence/uefi-input-build.json.](https://github.com/limingerf/UniXNU-tb710fu/actions/runs/43636909923)
  Command: <code>python3 tools/ci_firmware.py build</code>. Revision: `e7f3c7ca74a953e7f6fe8aaf897eaf2133514d05`.

## CPU and interrupts {#cpu}

`planned`

Components: `ArmCpu`.

### Hardware and dependencies

- Board-specific enabled MPIDRs, PSCI method, GIC redistributor affinities, timer frequency and per-core EL1 PAC evidence.

### Configuration

- ArmCpu is selected for compilation. No board DTS or SMP success is supplied by the native-only build.

### Procedure

- 1. Compare the selected stock DTB and DTBO with the pinned same-device Linux reference.
- 2. Qualify the primary core, PSCI and timer before enabling secondary cores.
- 3. In a later authorized device test, record each enabled MPIDR, GICR affinity, timer/IPI checkpoint and required PAC behavior.

### Development findings

- The same-device reference disables physical affinities 0x100 and 0x200, leaving 0x000, 0x300, 0x400, 0x500, 0x600 and 0x700. Linux logical CPU numbering must not replace physical affinity values.
- Previous Android evidence reports six logical CPUs and EL0 paca/pacg features. It does not establish per-core EL1 PAC operation or successful XNU SMP.

### Completion criteria

- Every enabled core reaches its entry checkpoint with matching affinity, working local timer and IPI, and the selected arm64e requirements pass.

### Current limits

- No core has been qualified by this clean project. The timer frequency and GICR mapping still require board evidence.

### Next action

- Parse the selected local stock DTB/DTBO and retain a redacted CPU, PSCI, timer and GIC fact table.

### Evidence

- `source`: [Same-device reference declares the six enabled affinities and the SM8650 PSCI/GIC resources; this is source evidence.](https://github.com/SpendyYT/tb710fu-linux/blob/4d04410798b538fbe4b50664e3a66d9500a2ed31/arch/arm64/boot/dts/qcom/sm8650.dtsi)

## Memory and DMA {#memory}

`planned`

Components: `ArmDTPlatform`.

### Hardware and dependencies

- Selected live firmware DT, DDR banks, stock reserved ranges, UEFI memory descriptors, loader allocations and DMA ownership.

### Configuration

- The clean build has no board DTS and does not invent a DRAM window, reservation map or DMA translation.

### Procedure

- 1. Extract actual DDR and reserved ranges from qualified stock inputs.
- 2. Compare them with the same-device reference and previous UEFI memory table.
- 3. Account for all loader, display, secure firmware and DMA allocations before configuring an owned-memory window.

### Development findings

- The previous handwritten minimal DTS has a zero-length memory declaration and an invalid ranges encoding; it is excluded from the clean project.
- The previous UEFI overlay includes display demura and high-DDR reservations. Their values require comparison with this device's selected firmware DT before reuse.

### Completion criteria

- All memory and handoff ranges are accounted for, non-overlapping and correctly attributed; each enabled DMA engine has documented addressing and cache rules.

### Current limits

- No clean-project DT or DMA engine is qualified. Mainline reserved-memory alone cannot establish the live firmware DDR layout.

### Next action

- Generate a range comparison from local stock DTB/DTBO and UEFI inputs without reusing the invalid handwritten DTS.

### Evidence

- `source`: [Separates stock inputs, mainline reference data and rejected previous DTS content.](https://github.com/limingerf/UniXNU-tb710fu/blob/cf643221155ba2cb185bf969eb5f90c8d6243d2f/docs/HARDWARE.md)

## usb {#usb}

`host-verified`

### Hardware and dependencies

- Static DWC3/PHY/clock resources, XNU 12377 DMA and log interfaces, and host-side CDC enumeration. Current role, PHY and SMMU ownership are checked by the controller during initialization.

### Configuration

- The device kit contains hardware-independent CDC-ACM descriptors/request validation, a bounded log ring, a fail-closed transport preflight function, and a statically allocated 64 KiB XNU console tap archive. The XNU character hooks only write RAM; no DWC3 transport or USB drain worker is selected.

### Procedure

- 1. Run the host protocol, ring-buffer, kernel-tap and preflight-guard tests.
- 2. Build and verify the target arm64e kernel tap archive on the supported macOS runner.
- 3. Implement the XNU 12377 DWC3 controller bring-up, DMA and device transport from the static board inputs; check role/clock/PHY/SMMU state inside driver initialization and refuse DMA on unsupported state.
- 4. Drain buffered bytes over a validated transport and verify enumeration plus byte capture on TB710FU.

### Development findings

- The TWRP DT declares DWC3 at 0x00a600000, nested stream ID 0x40, dr\_mode=otg and atomic DMA. It also describes the eUSB2 PHY and clocks; these are Linux/TWRP inputs, not proof of XNU handoff state.
- Ace 5 reports a real XNU CDC ACM log channel, but its kernel is XNU 8796; this implementation is a fresh portable protocol layer and guard, not copied controller code.
- A local XNU patch tees console and PE kprintf characters into a bounded 64 KiB RAM ring. The ring is not connected to DWC3, so it does not yet provide a host-visible CDC port.

### Completion criteria

- XNU reports through a host-enumerated CDC ACM port, the host captures the expected bytes without drops, and an intentional stop/panic path is separately verified.

### Current limits

- No XNU target build has validated the new character hooks and ring archive yet. The ring has no DWC3 endpoint transfer, SMMU/DMA adapter, XNU USB startup hook or CDC enumeration; it does not create a host-visible COM port. The host guard tests only validate caller-provided state and do not read TB710FU hardware.

### Next action

- Run the supported native kernel build to verify the character hooks, then implement and build the board-specific USB 2 device transport with early role, PHY, clock and SMMU checks.

### Evidence

- `host`: [Host descriptor, malformed-request, log-ring and fail-closed DWC3 preflight tests passed under AddressSanitizer/UndefinedBehaviorSanitizer; there is no XNU state reader, controller transport or enumeration yet.](https://github.com/limingerf/UniXNU-tb710fu/blob/cf643221155ba2cb185bf969eb5f90c8d6243d2f/tests/usb_cdc_protocol_test.c)
  Command: <code>CC=cc python scripts/check_usb_cdc_protocol.py</code>. Revision: `919b4bdbc63ace99271a9442e3af3673a0ed8075`.
- `source`: [Records the hardware-independent implementation, source provenance and outstanding device gates.](https://github.com/limingerf/UniXNU-tb710fu/blob/cf643221155ba2cb185bf969eb5f90c8d6243d2f/docs/USB_CDC_PORT.md)
- `source`: [Ace 5 reports CDC COM21 with 8,802 status bytes and no drops on Darwin 22; this is reference-device evidence.](https://github.com/tycykp/UniXNU-OnePlus-Ace5/blob/main/hardware/ios16-bringup-verified.json)
- `source`: [Pinned SoC source declares UFS host resources and SID 0x60; TWRP FDT details are summarized with hashes in docs/USB\_CDC\_PORT.md.](https://github.com/SpendyYT/tb710fu-linux/blob/4d04410798b538fbe4b50664e3a66d9500a2ed31/arch/arm64/boot/dts/qcom/sm8650.dtsi)

## Storage and root {#storage}

`planned`

### Hardware and dependencies

- UFS controller and PHY resources, clocks, resets, supplies, SMMU stream, actual LUN/block geometry and an approved root-volume layout. Runtime DMA and queue ownership are checked by the driver during initialization.

### Configuration

- No UFS component, root partition, persistent Data region or storage write path is selected for the native-only build.

### Procedure

- 1. Reconcile the same-device UFS source with the pinned SM8650 Linux DTS and TWRP block sample.
- 2. Adapt and build the NativeUfs controller path; have its initialization verify power, link, SMMU, DMA and queue ownership before issuing a read-only known-block command.
- 3. Review root and persistent Data layout independently before any storage write work.

### Development findings

- The TWRP FDT and pinned Linux DTS declare SM8650 UFS host 0x01d84000, PHY 0x01d80000 and stream ID 0x60; the FDT also declares ICE/MCQ resources and fastmap DMA. These do not prove XNU queue ownership, live SMMU mappings or DMA coherence.
- TWRP read-only sample: user LUN /dev/block/sda, 4096-byte logical blocks, GPT-header LBA 1. The 4096-byte sample CRC32 is 44b9c49a and its GPT header CRC validates; this is not an XNU read result.
- The host-only UfsReadProbe contract covers DMA mapping checks, idle-queue takeover, READ\(10\), quiescence, restoration and quarantine. It has no XNU register/DMA callbacks and is not a prerequisite probe or hardware driver.
- The optional ufs-source workflow compiles pinned ShengUfs with a device patch accepting qcom,sm8650-ufshc. Its archive is not linked into the native kernel; runtime ownership, DMA and reads are unverified.
- Owner-signed OS, SystemOS and App root policies now pass VerifiedRoot C signature and full block verification, and their raw .vroot tables are present in a rebuilt SHNGROOT v2 userdata image. This is host-only validation and is not consumed by the current TB710FU kernel configuration.
- Previous Android inventory reports 4096-byte logical and physical blocks. The previous Android userdata uses F2FS with file and metadata encryption; filesystem free space does not establish free GPT space or a safe shrink path.

### Completion criteria

- Controller, link and DMA qualify; known blocks and capacity match the device; the selected root mounts and launchd starts; persistence is tested separately if implemented.

### Current limits

- The source archive is a compile audit only and is not linked into the kernel. No XNU UFSHCI/SMMU reader, DMA ownership result, queue takeover, known-block read, media publication or root mount is qualified. The official source-storage bridge files are not present in this device repository. The userdata image has not been flashed; no partition, format or device write has been performed.

### Next action

- Add and review the board-owned SourceStorage, SourceRootPolicies and SourceRootBinding bridge against the pinned framework recipe, then link an archive only after the native compiler records and policy handoff pass. Validate firmware ownership, DMA and a read-only LBA 1 result on-device before selecting UFS at boot.

### Evidence

- `host`: [READ\(10\) command, GPT validation, disabled/refusal flow, DMA-map checks, queue restore and timeout quarantine passed under AddressSanitizer/UndefinedBehaviorSanitizer; callbacks do not access hardware.](https://github.com/limingerf/UniXNU-tb710fu/blob/cf643221155ba2cb185bf969eb5f90c8d6243d2f/package/Tb710fuUfsProbe/Test/ufs_read_probe_test.c)
  Command: <code>CC=cc python package/Tb710fuUfsProbe/Test/run_host_tests.py</code>. Revision: `919b4bdbc63ace99271a9442e3af3673a0ed8075`.
- `device`: [Read 4096 bytes at LBA 1; EFI PART signature and GPT header CRC validate; whole-block CRC32 44b9c49a. This does not test XNU UFS.](https://github.com/limingerf/UniXNU-tb710fu/blob/cf643221155ba2cb185bf969eb5f90c8d6243d2f/docs/evidence/ufs-gpt-lba1-twrp.json)
  Command: <code>TWRP ADB read of /dev/block/sda LBA 1; verify GPT header CRC and sample CRC32</code>. Revision: `35abab0ea7a50745220fe517a9dc782306e606b8`.
- `source`: [Pinned SoC DTS provides the UFS host/PHY/SID baseline; TWRP FDT hashes and limits are recorded in docs/USB\_CDC\_PORT.md.](https://github.com/SpendyYT/tb710fu-linux/blob/4d04410798b538fbe4b50664e3a66d9500a2ed31/arch/arm64/boot/dts/qcom/sm8650.dtsi)
- `source`: [Ace 5 has a run-bound 8 KiB UFS read and matching device CRC; its value is not a TB710FU block baseline.](https://github.com/tycykp/UniXNU-OnePlus-Ace5/blob/main/hardware/ios16-bringup-verified.json)

## Display {#display}

`planned`

### Hardware and dependencies

- Preserved ABL framebuffer address, size, stride, format and orientation; NT36532 dual-DSI/DSC resources and board backlight supplies.

### Configuration

- No GOP framebuffer, DSI, backlight or presentation component is selected for this native-only build.

### Procedure

- 1. Establish a stable firmware scanout and its actual framebuffer geometry.
- 2. Match the selected XNU framebuffer interface and OS ABI.
- 3. Add panel or backlight operations only after basic framebuffer output is qualified.

### Development findings

- The mainline panel reference is NT36532, 3200 by 2000, dual DSI and DSC. Source timing parameters do not establish ABL stride or XNU presentation.
- The previous vendor-DXE experiment could overwrite ABL display state, so its full driver chain is not imported.

### Completion criteria

- A known frame has correct geometry and colors; userspace presentation and brightness each pass their own checks.

### Current limits

- No clean-build framebuffer or panel result exists.

### Next action

- Document a qualified firmware framebuffer descriptor before choosing a display component.

### Evidence

- `source`: [Provides panel protocol, mode and power-sequence reference for later review.](https://github.com/SpendyYT/tb710fu-linux/blob/4d04410798b538fbe4b50664e3a66d9500a2ed31/drivers/gpu/drm/panel/panel-nt36532-wqhd-dual-dsi-dsc.c)

## Input {#input}

`planned`

### Hardware and dependencies

- Novatek SPI touch protocol, IRQ/reset wiring, firmware source, contact reporting and display coordinate mapping; button and accessory protocols.

### Configuration

- No XNU input component is enabled. UEFI-only Tb710fuKeyInputDxe is implemented in the board firmware overlay; volume keys map to Up/Down and power maps to Enter.

### Procedure

- 1. Review the same-device SPI driver and firmware-loading sequence.
- 2. Match the target OS HID interface before implementing a provider.
- 3. Qualify contact IDs, release events, coordinates and buttons separately.

### Development findings

- The same-device board declares novatek,NVT-ts-spi on SPI4. Its Linux configuration selects TOUCHSCREEN\_NT36532\_SPI rather than the different novatek-nvt-ts driver.

### Completion criteria

- Multiple contacts keep stable IDs, releases arrive, coordinates match the display and declared buttons emit correct HID reports.

### Current limits

- The UEFI physical-key provider has host-model verification only; it has not run on this device. Touch, XNU HID buttons, keyboard and stylus remain unimplemented. UEFI SimpleTextIn and Linux support do not establish XNU HID support.

### Next action

- Record the exact touch firmware and protocol dependencies before selecting or porting an input component.

### Evidence

- `source`: [Identifies the correct board touch reference and distinguishes source reports from native support.](https://github.com/limingerf/UniXNU-tb710fu/blob/cf643221155ba2cb185bf969eb5f90c8d6243d2f/docs/HARDWARE.md)

## GPU {#gpu}

`planned`

### Hardware and dependencies

- Adreno 750 GPU/GMU revision, signed firmware, power ownership, SMMU/DMA mappings, submission and fence interfaces, target Metal ABI.

### Configuration

- No GPU, GMU, Metal or GPU presentation component is selected.

### Procedure

- 1. Compare hardware and firmware requirements of existing implementations.
- 2. Qualify mapping and a bounded submission before enabling rendering.
- 3. Qualify the macOS frontend and presentation independently.

### Development findings

- Linux GPU support is a hardware reference only. A different OS's successful Adreno submission does not qualify macOS 27 Metal or class layouts.

### Completion criteria

- A known submission completes with correct mappings and fences, then a selected macOS client renders and presents a known image.

### Current limits

- GPU work is deferred until the native build and basic boot are qualified.

### Next action

- Keep GPU dependencies disabled during compiler and linker diagnosis.

### Evidence

- `source`: [The selected components exclude GPU providers.](https://github.com/limingerf/UniXNU-tb710fu/blob/cf643221155ba2cb185bf969eb5f90c8d6243d2f/board.toml)

## Network {#network}

`planned`

### Hardware and dependencies

- WCN7850 PCIe Wi-Fi and UART Bluetooth resources, firmware provenance, interrupts, DMA and target OS network interfaces.

### Configuration

- Wi-Fi, Bluetooth and their firmware loaders are not selected.

### Procedure

- 1. Verify the exact board firmware and power dependencies.
- 2. Match each controller to an existing component interface and target ABI.
- 3. Qualify firmware boot, transport and sustained traffic independently.

### Development findings

- The mainline board describes WCN7850 with Wi-Fi on PCIe and Bluetooth on UART14. Linux ath12k support is not a native network implementation.

### Completion criteria

- Wi-Fi scans and associates with sustained transmit/receive traffic; Bluetooth transport and selected profiles pass separate tests.

### Current limits

- No clean-project network implementation or device result exists.

### Next action

- Defer wireless implementation until the native-only kernel and initial boot are resolved.

### Evidence

- `source`: [Records the same-device network wiring source without importing firmware blobs.](https://github.com/limingerf/UniXNU-tb710fu/blob/cf643221155ba2cb185bf969eb5f90c8d6243d2f/docs/HARDWARE.md)

## cellular {#cellular}

`planned`

### Hardware and dependencies

- A confirmed SKU modem/SIM inventory before declaring cellular applicable or not applicable.

### Configuration

- No modem, QRTR/QMI, IPA/QMAP or cellular session provider is selected.

### Procedure

- 1. Establish the actual board's modem and SIM scope from qualified evidence.
- 2. Mark this area not-applicable only if the hardware inventory supports that conclusion; otherwise keep its firmware and interface work separate.

### Development findings

- Cellular capability is not inferred from the presence of generic modem reservations in a shared SoC description.

### Completion criteria

- The SKU scope is documented; applicable registration and data-session claims have their own evidence.

### Current limits

- Cellular hardware is not assessed in the clean native-only task.

### Next action

- Record the SKU's radio scope before any cellular implementation or not-applicable classification.

### Evidence

Collect evidence using the next action.

## Audio {#audio}

`planned`

### Hardware and dependencies

- ADSP firmware/services, WCD9395 codec, four AW88461 amplifiers, clocks, power supplies and route configuration.

### Configuration

- No audio, DSP, codec or amplifier component is selected.

### Procedure

- 1. Reconcile the board's DSP and codec source requirements.
- 2. Match the target OS audio interface and firmware services.
- 3. Qualify each playback and capture route, including start and stop.

### Development findings

- The mainline reference describes WCD9395 and four AW88461 amplifiers; its ASoC routes and UCM data are reference inputs rather than XNU drivers.

### Completion criteria

- Each declared route carries the intended format through playback or capture and handles start/stop without unsafe output.

### Current limits

- No clean-project DSP boot or audio route is qualified.

### Next action

- Keep audio dependencies out of native kernel build diagnosis.

### Evidence

- `source`: [Identifies same-device audio parts and source limits.](https://github.com/limingerf/UniXNU-tb710fu/blob/cf643221155ba2cb185bf969eb5f90c8d6243d2f/docs/HARDWARE.md)

## Power {#power}

`planned`

### Hardware and dependencies

- Board PMIC/regulator inventory, clock and firmware ownership, battery units and evidence for each proposed state transition.

### Configuration

- No board PMGR, clock, battery, suspend or secondary-CPU power provider is selected.

### Procedure

- 1. Map each requested operation to actual hardware and its current owner.
- 2. Qualify the macOS 27 interface before implementing operations.
- 3. Test each implemented state transition with its dependent devices.

### Development findings

- The previous reference's ShengPlatformPower is an OS-specific ABI qualification fixture with unsupported hardware methods. It must not be imported as a functioning power driver.

### Completion criteria

- Each advertised power operation and battery reading matches hardware observations, with explicit limits on unsupported transitions.

### Current limits

- No PMGR class sizes, vtable slots, empty success stubs or power claims are carried into this clean project.

### Next action

- Review a target-ABI implementation only when a specific boot requirement establishes the need.

### Evidence

- `source`: [Documents rejected ABI-specific power fixture reuse.](https://github.com/limingerf/UniXNU-tb710fu/blob/cf643221155ba2cb185bf969eb5f90c8d6243d2f/docs/HARDWARE.md)

## Image assembly {#packaging}

`planned`

Components: `XnuPrelink`.

### Hardware and dependencies

- Pinned macOS 27.3 profile and XNU source, supported macOS runner, selected ABI and complete native archive plan. Later prelink needs separately qualified IPSW members.

### Configuration

- The immediate artifact is the native-only kernel. XnuPrelink is selected as a build tool but a completed prelink, payload, boot image or userspace is not claimed.

### Procedure

- 1. Run one bounded native-only cloud build with the recorded official inputs.
- 2. Verify the actual kernel artifact and preserve its hash and build log.
- 3. Treat prelink, Data seed, trust caches, firmware, payload and image assembly as subsequent gates with their own inputs and evidence.

### Development findings

- The target profile is macos-27.3-26C5035r. A successful native link does not establish compatibility with a prelinked Apple image or successful device boot.
- The ordered device XNU series also carries diagnostic reporter mappings and switch markers; they remain diagnostic-only and do not establish device boot.

### Completion criteria

- The native kernel artifact is reproducible and identified by hash; every later image stage meets its own official format and ABI checks before being reported complete.

### Current limits

- No stock firmware, IPSW member, signing key, platform seed or device image is committed. Native-only CI does not authorize flashing.

### Next action

- Attach the bounded cloud run and actual kernel artifact result to this area after the run completes.

### Evidence

- `source`: [Pins the target profile, XNU source and expected Apple kernelcache hash for later image work.](https://github.com/limingerf/UniXNU-tb710fu/blob/cf643221155ba2cb185bf969eb5f90c8d6243d2f/upstream.lock.json)
- `source`: [Records the ordered device patch input for kernel packaging, including explicitly diagnostic-only patches.](https://github.com/limingerf/UniXNU-tb710fu/blob/cf643221155ba2cb185bf969eb5f90c8d6243d2f/patches/xnu/series)

## Diagnostics {#diagnostics}

`planned`

### Hardware and dependencies

- Complete source revisions, bounded CI logs and artifact hashes; later device logs identifying firmware, image and the last confirmed stage.

### Configuration

- hardware.toml is an evidence inventory, not a UniXNU runtime configuration. docs/HARDWARE.md separates historical observations from clean-project qualification.

### Procedure

- 1. Run the official porting-record checker against this repository.
- 2. Preserve the first actual CI failure and diagnose it before another build.
- 3. Add device evidence only after a separately authorized test, recording firmware/image identity and an actual checkpoint.

### Development findings

- Run 43844823907 passed native build, strict prelink and the production parser. The diagnostic models, QR render/decode and fixed OneSend receiver pass for the recorded stages.
- The device reporter changes in patches/xnu/0006 and 0009 preserve diagnostics across the fileset and switch boundary; they are observability changes, not a functional MMU fix.
- The TWRP GPT-header sample is a read-only Linux/TWRP storage baseline and is not an XNU UFS result.
- The user supplied a guard11-labelled hardware report, src-eff36305-guard11, with STAGE=56 and XNU returned: tb710fu\_ramoops\_init at physical zone 0x93ff00000. This is evidence of reaching that early-kernel checkpoint, not root-volume or userspace boot.
- No device partition hash binds the report to the exact signed guard11 pair. The ramoops header/content and cross-reset retention remain unverified; the signed pair's independent RSA and payload readback checks passed.

### Completion criteria

- Each reported milestone has a reproducible invocation, full source revision and accessible matching evidence; secrets and personal identifiers remain excluded.

### Current limits

- The guard11-labelled stage-56 report has no matching device partition hash. Valid ramoops contents/retention, root-volume mount, native UFS operation and macOS userspace remain unqualified.

### Next action

- Use the stage-56 report as the current early-kernel checkpoint; verify the exact booted image and capture ramoops contents, then continue the native storage/root-volume bring-up on main.

### Evidence

- `source`: [Defines evidence categories, excluded identifiers and qualification gates.](https://github.com/limingerf/UniXNU-tb710fu/blob/cf643221155ba2cb185bf969eb5f90c8d6243d2f/docs/HARDWARE.md)
- `source`: [Documents diagnostic patch provenance and states that it does not claim a functional MMU repair.](https://github.com/limingerf/UniXNU-tb710fu/blob/cf643221155ba2cb185bf969eb5f90c8d6243d2f/patches/xnu/README.md)
- `source`: [Records the native/prelink build and report identity, with device partition attribution limits.](https://github.com/limingerf/UniXNU-tb710fu/blob/cf643221155ba2cb185bf969eb5f90c8d6243d2f/docs/evidence/kernel-ttbr1-guard11-build.json)
- `source`: [Records a read-only GPT-header block captured through TWRP; this is not XNU UFS qualification.](https://github.com/limingerf/UniXNU-tb710fu/blob/cf643221155ba2cb185bf969eb5f90c8d6243d2f/docs/evidence/ufs-gpt-lba1-twrp.json)

</div>
