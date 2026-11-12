# OnePlus 13 CPH2653: iPhone iOS 16 source preparation

[lihenggui/UniXNU_dodge_SM8750](https://github.com/lihenggui/UniXNU_dodge_SM8750)

<div v-pre>

OnePlus 13 CPH2653: native A830 iPhone development payload, local builds and a separate QEMU fixture reaching original launchd main through the SystemOS union and shared cache.

Source record: [porting.toml](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/porting.toml), `c789270726a971264b2095fdc5c9190290b19611`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `host-verified` |
| [Firmware and boot](#firmware) | `host-verified` |
| [CPU and interrupts](#cpu) | `implemented` |
| [Memory and DMA](#memory) | `host-verified` |
| [Storage and root](#storage) | `implemented` |
| [Display](#display) | `planned` |
| [Input](#input) | `implemented` |
| [GPU](#gpu) | `implemented` |
| [Network](#network) | `planned` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `planned` |
| [security](#security) | `implemented` |
| [Image assembly](#packaging) | `host-verified` |
| [Diagnostics](#diagnostics) | `host-verified` |
| [cellular](#cellular) | `planned` |

## Configuration {#configuration}

`host-verified`

Components: `XnuPrelink`.

### Hardware and dependencies

- CPH2653 / dodge / SM8750 and iPhone10,3 iOS 16.7.16 build 20H392.

### Configuration

- Format 2 board; local iPhone profile; public XNU 8796.141.3 with strictly rebased Darwin 22 patch series.

### Procedure

- Run ./unixnu status --json, scripts/test\_ios\_profile.py and scripts/check\_ios16\_patches.py with the local Python 3.12 environment.

### Development findings

- 61 patches apply strictly on clean pinned Apple source. The original KC is 8796.142.1.703.8, a different minor revision.
- Public reports use separate original and publication hashes. Builds inherit host memory settings and use four jobs.
- Reviewed the porting guide and both 13T ports through UniXNU 13d0779e2ccd30d3caa1f8c9a15202730feace67 on 2026-11-11. The native route backports calling-thread compilation and Vulkan device retention after recovery. The latest core change updates Adreno740 address-space fault isolation. Source revisions and the iPhone profile remain pinned; the standard package check resolves 61 patches.
- The native prelink derives normal and explicit security startup from the original iPhone module records. Sandbox uses its existing module start; AMFI keeps its explicit early initializer. The shared source profile and original component code remain pinned.

### Completion criteria

- All selected sources and patch series resolve and the iPhone profile stays distinct from iPadOS.

### Current limits

- Patch application and configuration checks do not qualify compilation or binary ABI.

### Next action

- Audit original component layouts, crypto lifecycle and runtime initialization; strict static prelink and both reviewed security entries now pass.

### Evidence

- `host`: [61 patches apply strictly on clean pinned Apple source. The original KC is 8796.142.1.703.8, a different minor revision.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/reports/public/ios16-rebased-patches.json)
  Command: <code>python3 scripts/check_ios16_patches.py</code>. Revision: `3fa5ff5f409398c0555a9561d6437ce5d4c3b3b7`.

## Firmware and boot {#firmware}

`host-verified`

Components: `DarwinBoot`.

### Hardware and dependencies

- Pinned Mu-Silicium dodge platform and its Binaries submodule.

### Configuration

- Memory patch, UniXNU app/registrar, FDT initrd driver and DarwinBoot embedded in DEBUG FD.
- The board adds AdvancedLogDxe, a DXE Core Advanced Logger producer with 512 pages, and payload.tools=true.

### Procedure

- Run .venv-uefi/bin/python scripts/build\_native\_a830\_firmware.py after preparing the pinned sources and entropy loader; --check-only validates completed files.
- The native payload builder model-tests this exact EFI before assembling the Android container.

### Development findings

- The current native firmware builds 54 EFI images into a 3 MiB FD with the original memory patch. Readback finds the exact fresh-entropy DarwinBoot, unchanged donor RNG and QR log exporter.
- The DXE producer has a 2 MiB buffer. Tools &gt; Advanced Logger exports it through OneSend; SEC retains the existing debug output.
- The loader obtains a fresh 256-byte RAW EFI RNG seed per attempt. Its actual Boot C code passes two success and six failure model paths, then the native kernel consumes the seed and runs the original 18-test crypto POST.

### Completion criteria

- Firmware builds with the loader and all required payload filesystem interfaces.

### Current limits

- No hardware boot. Donor firmware 16.0.7.201 differs from captured 16.0.1.304; the five-byte original ramdisk is not an iOS payload.

### Next action

- Review differing DXE interfaces and upstream patches before selecting any stock replacement; qualify GOP scanout separately from static Mu declarations.

### Evidence

- `host`: [54 EFI images with the exact entropy loader and DXE exporter read back from the 3 MiB firmware.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/reports/public/native-a830-firmware.json)
  Command: <code>.venv-uefi/bin/python scripts/build_native_a830_firmware.py --check-only</code>. Revision: `6b3d90b79e191e08171bfedd3980234a7e49d340`.
- `host`: [Actual EFI success/failure paths, addon/trust memory handoff, native seed consumption and original 18-test crypto POST pass with explicit firmware peers.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/reports/public/native-a830-payload.json)
  Command: <code>.venv-gpu/bin/python scripts/build_native_a830_payload.py --check-only</code>. Revision: `6b3d90b79e191e08171bfedd3980234a7e49d340`.

## CPU and interrupts {#cpu}

`implemented`

Components: `ArmCpu`.

### Hardware and dependencies

- Captured GICv3 0x16000000, redistributors 0x16080000/0x40000 stride and 19.2 MHz timer; eight recorded MPIDRs.

### Configuration

- Generic ArmCpu with one enabled boot CPU and cpus=1; topology admits Aff1 cores and Aff2 clusters.

### Procedure

- Compile the source CPU driver against Darwin 22 and inspect the generated ADT.

### Development findings

- ArmCpu and ArmDTPlatform compile/link against Darwin 22; native timer and PAN definitions are present in actual compiler records. SM8750 topology excludes Apple CPU\_OVRD.

### Completion criteria

- Each enabled CPU reaches its entry and timer/IPI checkpoints.

### Current limits

- Hardware timer, interrupt, PSCI and SMP observations are absent.

### Next action

- Retain single-core source bring-up; qualify original component interfaces before enabling peripherals.

### Evidence

- `host`: [ArmCpu and ArmDTPlatform compile/link against Darwin 22; native timer and PAN definitions are present in actual compiler records. SM8750 topology excludes Apple CPU\_OVRD.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/reports/public/native-kernel.json)
  Command: <code>.venv-uefi/bin/python scripts/validate_kernel_artifacts.py</code>. Revision: `3fa5ff5f409398c0555a9561d6437ce5d4c3b3b7`.

## Memory and DMA {#memory}

`host-verified`

### Hardware and dependencies

- Captured runtime DTB SHA256 f961f2596c31c51b8db5be7b9e680aa35c86b71694820a7b5844f9829a3e7d11 and its reserved regions.

### Configuration

- Firmware heap holes reserved; ADT describes a four-GiB high bank and owned-memory request.

### Procedure

- Compare the firmware memory descriptors to the pinned runtime DTB and read back the generated ADT.

### Development findings

- Static descriptor checks pass; the host-executed source page policy retains native 4 KiB at RAM boundaries.

### Completion criteria

- All loader handoff allocations lie in current UEFI usable memory and all DMA mappings are accounted for.

### Current limits

- Static DTS memory is not a substitute for the runtime UEFI map; DMA hardware is untested.

### Next action

- Retain runtime-allocation proof as a separate requirement; local native kernel and payload checks now pass.

### Evidence

- `host`: [Static descriptor checks pass; the host-executed source page policy retains native 4 KiB at RAM boundaries.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/reports/public/memory-after.json)
  Command: <code>python3 scripts/check_uefi_memory.py --map uefi/Mu-Silicium/Platforms/OnePlus/dodgePkg/Library/MemoryMapLib/MemoryMapLib.c --dtb &lt;captured-dtb&gt; --expected-sha256 f961f2596c31c51b8db5be7b9e680aa35c86b71694820a7b5844f9829a3e7d11</code>. Revision: `6b3d90b79e191e08171bfedd3980234a7e49d340`.

## Storage and root {#storage}

`implemented`

Components: `VirtioMmioBlock`.

### Hardware and dependencies

- Captured UFS 0x1d84000, interrupt 265, SMMU stream 0x60; pinned iPhone OS/SystemOS and NativeUfs reference.

### Configuration

- Default physical UFS remains disabled. Probe-only archive is preserved; a complete read-only root publisher and explicit IOBSD storage-before-graphics coordinator are separately linked against the exact 144-byte/190-slot iPhone original class. No physical partition is created.

### Procedure

- Run scripts/build\_storage\_stack.py with the local .venv-uefi Python; it selects .venv-gpu for linked CPU checks. Use --check-only to verify all five current stages without rebuilding.
- Run scripts/build\_data\_stack.py for both APFS seeds, real source lifecycle/helpers, the 83-object strict original prelink and CPU paths; --check-only verifies current reports/artifacts.
- Run .venv-gpu/bin/python scripts/check\_ramblock\_start\_kernel.py for the actual startup/live chain; --check-only validates its current evidence.
- Build the separate QEMU candidate with scripts/build\_qemu\_storage.py, then run scripts/check\_qemu\_storage.py with the GPU Python environment and local OS/SystemOS files. --check-only validates the recorded run.

### Development findings

- Original iPhone storage ABI, 12 storage aliases and the concrete 190-slot class are checked. Complete read-only UFS/ordered root-window publication and deferred original-module/native-class startup compile into a combined 68-object kernel. 32 lifecycle, 25 combined scheduling, eleven source probe matching and production root-publication host checks pass with explicit peers. Combined strict prelink reads 58962 original pointers, 208 aliases and both concrete/parent vtables. Eleven linked CPU paths execute native/source/original constructors and combined IOBSD plus three full display lifetime paths. The exact 8380219392-byte OS/SystemOS regular-file payload passes full hash readback and 32 production consumer cases. All 198 stock initial Data entries are archived with numeric ownership, permissions, links and xattr metadata, with eight corruption controls. Separate 2/3 GiB APFS v2 seeds now preserve all content/metadata and compression, pass independent read-back, strict compatible apfsck and 17 rejection controls each. The 352-byte/190-slot RamBlock and deferred registration/one-shot start link into a separate 83-object candidate retaining 332 aliases. 77 sanitizer and 30 ARM64 paths pass, including original protected constructors/destructors; 43 rejection controls pass across Data stages.
- A separate 84-object/85-entry startup candidate now queues system/Data/input in actual IOBSD. Thirty scheduler sanitizer and 43 CPU paths plus 24 rejection controls pass; the exact 721024-byte packed 2 GiB seed and preserved iPhone ADT pass actual DarwinBoot C handoff parsers and FAT/Android v4 container readback. Data remains default-off; the original mount is unqualified.
- Seven additional init/Data stages pass: exact 336-byte user/324-byte APFS request ABI, 19 original-program and 80 native/original-prefix CPU paths, 16 new request sanitizer cases and 32 rejection controls. An 87-object/91-entry candidate wires actual PID 1 scratch/Data/init ordering, uses exact seed identity and post-mount checks, and passes independent container readback. Apple option/VFS/mount/VM/IOKit/init peers remain explicit; original mount and root authentication are unqualified.
- The unchanged RamBlock start now executes against exact 2/3 GiB seeds in the 87-object candidate: 28 start paths, full 524288-page 2 GiB hashing, then 26 live I/O and 68 selector paths on the actual started objects, plus four rejection controls. Native metadata getters execute; platform/registry/type/hash/descriptor peers remain explicit. Original media publication, full APFS and persistence remain unqualified.
- The native A830 integration preserves the existing storage/input/startup objects and their original bindings. Its 111-object strict link and prelink repeat the UFS, RamBlock and iPhone storage-table readbacks.
- QEMU now reaches bsd\_init and then the genuine Failed to mount root device panic. This fixture has no root block transport; the prepared iPhone OS/SystemOS files remain local.
- A separate 113-object candidate connects the pinned read-only VirtioMmioBlock to the measured iPhone storage ABI. It waits for completed platform registration, snapshots all 32 actual VirtIO nubs and starts the two block devices after original IOStorageFamily loads. Actual DMA first-sector hashes and capacities match OS/SystemOS. Original APFS mounts the UUID-selected root, then XNU refuses its failed root-authentication ioctl. Disabled startup and writable-backend controls perform no disk reads.
- The owner-root fixture verifies all 2,045,449 original input blocks with C/OpenSSL and calls the exact original iPhone RSA make/verify callbacks twice each in QEMU. Every completed guest read is checked against immutable owner-signed policy. The mounted root is read-only, its signed UUID and actual BSD device match, and load\_init\_program is reached. The Apple ioctl still returns EAUTH. Damaged signatures, changed DMA and a genuinely signed wrong UUID are refused.
- Adding the original iPhone AppleFSCompressionTypeZlib extends the separate VM candidate to 29 components and 64,635 checked pointer sites. PID 1 is launchd with the original executable UUID. Its first EL0 instruction and 64 entry bytes match the original dyld extracted from OS. The missing-decompressor control fails exec with ENOTSUP before EL0.
- SoftwareAES binds to the original 288-byte iPhone AES class and 181 dispatch slots. Its actual CBC/interface self-tests pass, and original Image4 completes nonce requests using the separate public VM development identity. Original dyld returns from its ignition query, enters prepare and reaches the missing shared-cache/libSystem error. Wrong-answer and absent-identity controls are refused.
- The SystemOS fixture enables the existing Darwin 22 native union with the observed iPhone UUID. Its mounted device and signed read-only policy match, and the original OS root passes a second check. Original dyld maps the original shared cache and its live header matches all 512 bytes. Execution reaches launchd main with 16 matching original instruction bytes after the initial demand-page fault. A different SystemOS UUID is refused before mounting. Ignition remains enabled.

### Completion criteria

- Qualified storage ABI, read transport, authenticated root policy and original launchd execution.

### Current limits

- No physical UFS access, partition creation or authenticated-root readiness. Original system windows and initial Data content are prepared as local files; boot.img does not contain those windows, and APFS Data formatting/readback is prepared separately; writable runtime remains unqualified. Controller/SMMU/DMA ownership, class/IOStorageCompletion runtime ABI, actual service matching and APFS/Data/power remain unqualified. Failed hardware start retains resources until reset; rollback is unqualified.

### Next action

- Qualify the implemented full read-only transport, original storage matching/completion and root publication; qualify authenticated-root, the implemented PID 1 Data mount route, original media matching, full parent/registry and crypto/power lifecycle. The default-off init route is wired and modeled; physical qualification remains outstanding.
- Continue beyond launchd main into Data and system-service startup; retain the separate Apple authentication result and physical-storage work.

### Evidence

- `host`: [The iOS 16 source probe compiles, 212 public native imports match by name, and the real local UBSAN runtime dependency is recorded for static linking. Eight existing read-only host suites pass ASan/UBSan.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/reports/public/ufs-source-probe.json)
  Command: <code>.venv-uefi/bin/python scripts/build_ufs_probe.py --partition unixnu</code>. Revision: `f5017376415268fd39dcf0b3fd68a94661cee078`.
- `host`: [Original storage, two read-only DMA disk reads and the UUID-selected APFS root mount execute in QEMU. XNU preserves its root-authentication refusal. Two transport refusal controls and 27 coordinator sanitizer cases pass.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/reports/public/ios16-qemu-storage-entry.json)
  Command: <code>.venv-gpu/bin/python scripts/check_qemu_storage.py --check-only</code>. Revision: `4e1013eb8c45077b57f8d38d61b389fe899ea1c3`.
- `host`: [Original iPhone launchd PID 1 executes the first dyld instruction in EL0; process UUID, 64 entry bytes and original decompressor callback instructions match. The missing-component control fails before EL0.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/reports/public/ios16-qemu-exec-entry.json)
  Command: <code>.venv-gpu/bin/python scripts/check_qemu_exec.py --check-only</code>. Revision: `1b191cb58250d0705d8a51287127505aa4bc0789`.
- `host`: [SoftwareAES passes actual CBC/interface tests, original Image4 serves its ignition query, and original iPhone dyld enters prepare and its cache loader. Two refusal controls pass. SystemOS cache attachment is next.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/reports/public/ios16-qemu-aes-entry.json)
  Command: <code>.venv-gpu/bin/python scripts/check_qemu_aes.py --check-only</code>. Revision: `da07dd5c7d62bbe960f5bd4fe7789574d3a49d8c`.
- `host`: [Read-only owner-verified SystemOS union, original shared-cache mapping and launchd main entry execute in QEMU. The cache header and init entry bytes match the originals; a wrong volume UUID is refused before mounting.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/reports/public/ios16-qemu-systemos-entry.json)
  Command: <code>.venv-gpu/bin/python scripts/check_qemu_systemos.py --check-only</code>. Revision: `1b191cb58250d0705d8a51287127505aa4bc0789`.
- `host`: [Complete read-only root publisher, original iPhone ABI, 32 lifecycle and 25 combined startup host cases; strict 68-object/208-alias source and original-component prelink, no runtime activation](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/reports/public/ios16-ufs-root.json)
  Command: <code>.venv-uefi/bin/python scripts/build_ufs_root.py</code>. Revision: `f5017376415268fd39dcf0b3fd68a94661cee078`.
- `host`: [Six Data stages pass: two exact original-content APFS seeds, 77 sanitizer cases, 30 ARM64 paths, 43 rejection controls and an 83-object/28-component strict prelink. Original Data matching/mount and writable runtime remain unqualified.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/reports/public/data-stack.json)
  Command: <code>.venv-uefi/bin/python scripts/build_data_stack.py --check-only</code>. Revision: `4be2d7eb05ef5a98126c91e0302c149140c0e3e1`.
- `host`: [Four startup stages, 84 objects, 30 scheduler sanitizer cases, 43 CPU paths and 24 rejection controls pass. Packed Data/ADT/FAT/Android readback passes; no phone or original Data mount qualification.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/reports/public/data-startup-stack.json)
  Command: <code>.venv-uefi/bin/python scripts/build_data_startup_stack.py --check-only</code>. Revision: `4be2d7eb05ef5a98126c91e0302c149140c0e3e1`.
- `host`: [Exact iPhone ordinary Data requests, 87-object/91-entry init hook, 19 original-program and 80 source/original-prefix CPU paths, 32 rejection controls and container readback pass; no real APFS mount/root authentication.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/reports/public/data-mount-stack.json)
  Command: <code>.venv-uefi/bin/python scripts/build_data_mount_stack.py --check-only</code>. Revision: `244c76b2610adc6bbfceceea7028665be6df560e`.
- `host`: [28 actual start, 26 subsequent I/O and 68 selector ARM64 paths; four rejection controls, no state reconstruction or original APFS/runtime qualification](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/reports/public/ios16-ramblock-start-kernel.json)
  Command: <code>.venv-gpu/bin/python scripts/check_ramblock_start_kernel.py --check-only</code>. Revision: `4be2d7eb05ef5a98126c91e0302c149140c0e3e1`.

## Display {#display}

`planned`

### Hardware and dependencies

- Captured AA569 panel references, 1440 by 3168 Android mode; upstream GOP and display source candidates.

### Configuration

- The iPhone artwork scale is three. DarwinBoot consumes GOP; Mu SimpleFb currently uses static 1440x3168x32 and 0xfc800000 platform declarations, with bounds/error checks; physical scanout geometry remains unqualified.

### Procedure

- Audit GOP handoff and derive display-family bindings from the pinned iPhone kernelcache.

### Development findings

- Exact original iPhone class hierarchy and table extents pass static audit. Legacy is 5728 bytes/338 entries; fourteen typed virtual dispatch probes pass across 45 CPU cases; eight raw backend call shapes are qualified while slot 243 arguments and all operation/status semantics remain open. The partial base retains nine abstract slots; a separate concrete GOP subclass now supplies bounded error/no-op entries, a raw stock-equivalent slot 243 leaf, and service coordination. This archive passes 60 coordinator, ten actual frontend/bridge/refresh integration and 69 native CPU cases. A separate 64-object kernel includes the class and explicit original-module prepare/attach entry points; 33 sanitized orchestration peer cases pass, including original software-root presence/class and provider checks. Another 32 CPU cases execute full original Legacy init/start/post-hardware/stop/free together with the concrete source class from the real prelink; IOKit/coordinator/matching/scheduler are explicit peers. Three original dispatcher cases cover late provider use, and the source now retains provider until free. Real original parent lifecycle and physical power remain unqualified. The bounded frontend waits original producers plus a captured Adreno timeline, defaults to CPU scanout copy, and connects optional disabled software refresh. Its startup factory retains inputs while entering the original work-loop gate and rechecks identity/mode/queue state before creating the frontend. 121 sanitized frontend cases cover queue reconciliation, reentrant release, waits, cancellation, mode matching, empty startup queues and stop. Another 29 CPU cases check original init/queue blocks; registration occurs before original start returns. The 23 original-userland cases connect three unchanged kernel size functions to CGSize conversion. Sixteen additional completion body/guard CPU cases execute thirteen unchanged full-body paths and twelve release/current-clear/wakeup tails with explicit lifetime peers. A separate native derived fixture verifies all 338 vtable slots, 170 original inherited-method/C2/D2 aliases plus one parent-metaclass alias and seven bounded lifetime cases comparing actual original/source-kernel parent C2/D2 without parent peers; no real provider or metaclass is registered. The real-class GOP factory now allocates the exact 216-byte original AppleARMIODevice, uses inherited public init, reads back actual PE memory resources, and pins the published nub/metaclass. Sixty sanitizer cases and eighteen linked CPU paths cover ownership, original allocation/native constructors, early unwind and the actual IOBSD hook. An isolated native object schedules a bounded worker only with dodge-graphics=1; twenty-four scheduling sanitizer cases pass. Real registry, loader, generic init, allocation and scheduling remain explicit peers; kernel runtime and Apple bus/clock methods remain unqualified.
- The native A830 candidate retains eleven display support objects and original-family startup order, recompiling the frontend with per-surface recovery checks. An abandoned writer blocks its surface until a later successful writer retires; captured old epochs stay invalid. The 111-object kernel and 136 frontend cases cover this path alongside deferred producer completion and backing changes.

### Completion criteria

- A verified framebuffer can display diagnostics and the original mobile display client can present.

### Current limits

- GOP geometry and actual display-family ABI are unqualified.

### Next action

- Qualify real original loader and full parent/user-client/IOSurfaceRoot lifetime, physical mapping and power. The real-class GOP factory and IOBSD opt-in worker are implemented and linked; actual publication, producer fences/cache visibility and GPU failure quiescence remain unqualified.

### Evidence

- `host`: [Concrete exact Legacy/GOP source class and coordinator compile for Darwin 22. Strict link reads all 338 slots, 172 original aliases and 191 native/GPU imports. 60 coordinator sanitizer cases, ten actual frontend/bridge/refresh integration cases and 69 native CPU cases pass with explicit peers. Publication waits until parent start returns; gated client admission and deferred detach preserve resources through drain and parent stop. Failed Legacy start retains partial resources; source cleanup now runs once after start returns and frontend drain. Eleven bounded no-surface paths execute unchanged full original stop with explicit IOKit peers. Explicit OSKext preparation, Kernel pre/postModLoad and attachment compile into a separate strict 64-object kernel and original-graphics prelink. An additional 32 full linked lifecycle CPU cases execute actual original init/start/post-hardware/stop/free and source class instructions with primitive IOKit/core peers; two corruption/boundary controls are rejected. A provider lifetime pin protects the late original dispatcher after detach. A unified explicit boot coordinator holds provider/root and orders modules, atomic one-shot A830 startup and display attach; 24 sanitizer cases plus six direct board entry cases with 16-way calls pass with API peers. A separate FAT/Android v4 development container passes complete readback; original userspace/root remain absent and opt-in startup is disabled by default.  The real-class GOP factory now allocates the exact 216-byte original AppleARMIODevice, uses inherited public init, reads back actual PE memory resources, and pins the published nub/metaclass. Sixty sanitizer cases and eighteen linked CPU paths cover ownership, original allocation/native constructors, early unwind and the actual IOBSD hook. An isolated native object schedules a bounded worker only with dodge-graphics=1; twenty-four scheduling sanitizer cases pass. Real registry, loader, generic init, allocation and scheduling remain explicit peers; kernel runtime and Apple bus/clock methods remain unqualified. Real original loader/start/stop, service matching, power and runtime remain unqualified; defaults are unchanged.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/reports/public/ios16-display-service.json)
  Command: <code>.venv-gpu/bin/python scripts/build_display_service.py</code>. Revision: `3fa5ff5f409398c0555a9561d6437ce5d4c3b3b7`.
- `host`: [136 native frontend cases and 1,124 packet mutations pass with explicit timeline, transport and IOKit peers.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/reports/public/native-a830-recovery-host.json)
  Command: <code>.venv-gpu/bin/python scripts/check_native_a830_recovery.py --check-only</code>. Revision: `1a1321056ffc5428ae925f4680093718b46ca7c2`.

## Input {#input}

`implemented`

### Hardware and dependencies

- Captured S3910 HBP/SPI 0xa90000/QUP SID 0xa3/reset 161/ATTN 162/19 MHz; target power/reset delays and matching original HBP raw-GPIO semantics; exact iPhone 20H392 original IOHIDFamily; exact CPH2653 16.0.1.304 UEFI SPI SEFW and independent identical I2C-module copy.

### Configuration

- Separate 81-object input/storage/display candidate and local container; dodge-input=1 disabled by default. Original 208-byte/207-slot base, 1560-byte concrete class, 53 HID aliases and 35 opaque data-only slots. Only four extra HID operations callable. AVDD SID9 GPIO3 validates retained electrical fields, preloads physical high, then initializes direction and enable; VDD ldob4 1.8 V. QUP4 SPI loader accepts only an idle empty engine without DMA/GPI ownership, programs 442 words/69 configuration entries from the pinned 2141-byte stock SEFW and verifies every write. The stopped/unvoted/non-DFS SE4 root now initializes to the derived 19.2 MHz XO after ownership checks; existing roots/DFS use live locked GPLL0 and M/N readback, without rewriting shared PLLs/voltage. Warm SPI adoption also refuses leftover DMA/GPI/FIFO ownership. No donor LDO16 or private EventDriver mutation. Bounded event80/37 and driver264/219 declarations with 71 data-only bindings are included with a 552-byte/219-slot source edge subclass. Its Kernel personality is read back as \_\_kernel\_\_; original tables and event fields are accessed only through qualified APIs. Full transfer requires DMA data, command completion and engine idle before RX delivery; bounded cancel/abort/reset ACK and sticky errors prevent reuse. Source start/stop run on the workloop gate; reentrant stop retains the provider and defers parent cleanup until callbacks exit.

### Procedure

- Run scripts/build\_input\_stack.py, or --check-only to verify all twenty-two current stages, dependency hashes and artifacts. Public CI runs scripts/check\_input\_cold\_host.py --synthetic without proprietary input.

### Development findings

- 3556 source sanitizer cases pass: 84 existing power/lifecycle/worker plus 73 cold GPIO, 2740 GENI parser/loader, 135 target-clock, 224 full transfer/terminal and 300 edge-origin cases. 201 CPU paths pass: 16 original HID callers, seven original init/free audits, 11 current prelinked constructor/BSD, 18 cold parser/loader, 18 clock, 20 full transfers, 12 original C HID parser/cleanup and 27 actual source gated start/stop/tick/drain and 32 actual original event accessor/default-dispatch and 40 source edge/registration/lifetime paths. Another 52 checks compare actual native S3910 reports against original parsed usage/bit/logical metadata. The unchanged original early-DMA-completion control and missing source stop are rejected. Exact 207 input and 219 source-event concrete pointers, 209-word HID and 221-word event parent tables, native chains, 332 combined aliases, 77 source entries, 28 original components/seven interfaces, all 63889 pointer sites and embedded SPI firmware read back; actual loader and FAT/Android v4 parsers accept the isolated container.
- The c888efd3ce1b817d13f28783a77cf689cb2255c9 mapping helper is reused unchanged. CPH2653 maps its RPMh command database with kIOMapReadOnly. All 22 input stages pass again, including the 81-object native candidate, iPhone prelink and local container.

### Completion criteria

- Touch contacts, edge gestures and each physical button produce correct original HID events, with qualified power and cleanup.

### Current limits

- Host MMIO/clock/loader/IOKit and CPU allocation/memory/gate/mapping/timer/thread/refcount peers remain explicit; original parent start/stop and HID submission in source drain checks are peers. Serial-engine firmware is not executed. The actual original C HID parser/cleanup executes, but complete original device start, element dispatch, EventDriver matching/UI and remaining private event semantics remain unqualified or incomplete. The used event accessors and default dispatch pass 32 CPU cases; other private prototypes stay unavailable. Target orientation, shared clock/power-domain/electrical recovery and full SMMU/DMA/reset hardware takeover remain incomplete or unqualified. Objects/provider are pinned before original init, failures are latched without release, and maps stay pinned after hardware attempts; shared votes remain enabled. No phone operation or working iOS claim.

### Next action

- Complete shared clock/power-domain/electrical policy and qualify SMMU/DMA/reset ownership beyond bounded terminal recovery. Qualify full original EventDriver lifecycle, source edge/client ordering and original device start/element/matching; keep default candidates disabled.

### Evidence

- `host`: [Twenty-two current offline stages, 3556 sanitized source cases, 201 CPU paths plus 52 report checks and independent 81-object/332-alias/77-entry/28-original-component local container; exact stock SPI SEFW embedded, no runtime/hardware/full-iOS qualification](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/reports/public/input-stack.json)
  Command: <code>.venv-uefi/bin/python scripts/build_input_stack.py --check-only</code>. Revision: `f5017376415268fd39dcf0b3fd68a94661cee078`.
- `host`: [Original 208-byte/207-slot IOHIDDevice vs public 205-slot reference; original/public facts stay distinct from bounded callable source interface](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/reports/public/ios16-hid-abi.json)
  Command: <code>.venv-uefi/bin/python scripts/prepare_hid_abi.py</code>. Revision: `f9edab5e6cc6b2cf01ec8dfc6f2a41fd60e3a0bc`.

## GPU {#gpu}

`implemented`

Components: `Adreno740`, `AdrenoMetal`.

### Hardware and dependencies

- Native Adreno830 1a132105 and matching SMMU 3ba92451; CPH2653 Adreno830v2 0x44050001, six power/ACD bins, eight temperature sensors and four stock microcodes.
- iPhone10,3 / 20H392 original components and Darwin 22 source; pinned Mesa, AdrenoMetal and metal2vulkan inputs.

### Configuration

- Separate native A830 kernel and userspace build directories. The 57-object GPU archive joins the shared storage/input/display source to form a 111-object kernel.
- Surface-ID import uses selector 19. Optional selectors 17/18 validate their record sizes and return Unsupported; submission retains the native FIFO policy.

### Procedure

- Prepare GPU tools, stock firmware and the shared 97-object iPhone source baseline as described in docs/bring-up.md.
- Run .venv-gpu/bin/python scripts/build\_native\_a830\_stack.py to build the native route; --check-only validates completed stages and --record-existing records them without rebuilding.

### Development findings

- Native startup reads the SoC from SMEM before power writes, accepts 618/639 and checks any explicit dodge-gpu-soc request. The captured ACTLR value remains 0x32b. The 181 board checks include the actual stock firmware parsers and concurrent startup ownership.
- Surface imports resolve the calling task and retain exact original backing pages. A single active batch obtains original writer grants outside GPU locks. Whole-VM leases retain indirect resources; the deferred worker signals original completion after fence/cache retirement. Pending cancellation retains callback owners until a grant arrives. Backing changes invalidate active work and display health.
- Fifteen backend sanitizer suites, 24 native runtime cases, 12 map-wait cases and the VM concurrency suite pass. The strict prelink contains 28 original executables and seven interfaces; 63,889 pointer readbacks, four surface hooks and 17 original sync ARM64 cases pass. Prelink rebuilds validate a temporary candidate before replacing the current output.
- Turnip, Rust and Metal compile for ordinary arm64 iOS 16. Surface-ID hints reach the native import selector, with unconsumed or mismatched imports refused. The latest official calling-thread compilation policy is backported with its 2 MiB stack guard.
- GetStatus returns Busy during recovery and NotResponding after permanent loss. Turnip retains its Vulkan device after counter changes and exposes the restart count. Failed writers block only their surfaces after recovery drains; successful later writers restore visibility. Unconfirmed original completion retains tickets and callback context. Eleven actual Turnip status calls and two rejected old behaviors pass host tests.
- The official-format addon contains five files. Its trust bundle holds three local executable hashes and both unchanged iPhone 20H392 trust modules. Actual EFI addon/trust handoff, fresh seed consumption, original 18-test crypto POST and FAT/Android v4 readback pass in local models.

### Completion criteria

- The original iPhone graphics clients render known outputs through the target GPU with correct producer fences, reset and cache visibility.

### Current limits

- Local builds and software controllers leave GPU power, physical DMA/cache visibility, reset quiescence, Metal discovery and rendering for hardware bring-up. Actual QEMU startup reaches bsd\_init with AppleImage4, AMFI and Sandbox registered once, then stops at the absent root device. iOS userspace is not started.
- The native candidate is separate from the default kernel. Its development container has no original userspace/root image and retains opt-in graphics/Data startup.

### Next action

- After the source-only preparation phase, validate original-family startup, the first native fence, surface ownership across reset and known shader outputs using device logs.

### Evidence

- `host`: [Fifteen native build/test stages form one development payload with matching kernel, firmware and userspace identities, including actual QEMU entry.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/reports/public/native-a830-stack.json)
  Command: <code>.venv-gpu/bin/python scripts/build_native_a830_stack.py --check-only</code>. Revision: `1a1321056ffc5428ae925f4680093718b46ca7c2`.
- `host`: [Three ASan/UBSan suites: 24 runtime cases, 12 map-wait cases and production VM tests including 600 concurrent transactions.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/reports/public/native-a830-runtime-host.json)
  Command: <code>python3 scripts/check_native_a830_host.py --runtime</code>. Revision: `1a1321056ffc5428ae925f4680093718b46ca7c2`.
- `host`: [11 actual Turnip status calls, two rejected old recovery behaviors and 136 native display cases pass under sanitizers.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/reports/public/native-a830-recovery-host.json)
  Command: <code>.venv-gpu/bin/python scripts/check_native_a830_recovery.py --check-only</code>. Revision: `1a1321056ffc5428ae925f4680093718b46ca7c2`.
- `host`: [181 stock-firmware board checks, six real level selections and a 16-way startup-entry test.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/reports/public/native-a830-board-host.json)
  Command: <code>.venv-uefi/bin/python scripts/check_native_a830_board.py --firmware-dir build/cph2653-gpu-firmware</code>. Revision: `1a1321056ffc5428ae925f4680093718b46ca7c2`.
- `host`: [111 source/binding objects, 28 original executable components, seven interfaces, 63,889 pointer readbacks, four lifecycle hooks and 17 original sync model cases.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/reports/public/native-a830-prelink.json)
  Command: <code>.venv-gpu/bin/python scripts/build_native_a830_prelink.py --check-only</code>. Revision: `1a1321056ffc5428ae925f4680093718b46ca7c2`.

## Network {#network}

`planned`

### Hardware and dependencies

- OnePlus 13 wireless and USB hardware; no network driver selected.

### Configuration

- No synthetic network service is registered.

### Procedure

- Inventory firmware, buses and OS interfaces from existing captures and source.

### Development findings

- There is no host build or hardware network evidence for this port.

### Completion criteria

- A supported transport transfers data with bounded timeouts and correct addressing.

### Current limits

- Wi-Fi, Bluetooth, cellular and USB networking are unimplemented here.

### Next action

- Select a concrete transport and define its board and iOS ABI contract.

### Evidence

Collect evidence using the next action.

## Audio {#audio}

`planned`

### Hardware and dependencies

- OnePlus 13 audio hardware; original iPhone audio product metadata is preserved.

### Configuration

- No audio driver is selected.

### Procedure

- Inventory codec/DSP topology and required firmware before implementing a transport.

### Development findings

- Product identity is independent of functional audio support.

### Completion criteria

- Playback/capture and routing work through the original audio clients.

### Current limits

- No codec, DSP, speaker or microphone operation is qualified.

### Next action

- Prepare a board-specific audio transport after the initial kernel path.

### Evidence

Collect evidence using the next action.

## Power {#power}

`planned`

### Hardware and dependencies

- SM8750 PSCI SMC and pinned SoC operations; original iPhone AMFI declares a PMGR dependency.

### Configuration

- sleep-disabled=1 for bring-up; no battery or thermal values are fabricated.

### Procedure

- Audit original AMFI/PMGR entry points and the captured PMIC/RPMh board resources.

### Development findings

- PMGR compatibility is a specific ABI dependency and does not imply a complete power manager.
- Exact iPhone PMGR classes and AMFI slots 312/313 are derived. The T8015 target performs real 32-bit read/OR-4/write at region 1/bank 0/offset 0xd0030; its base/null fallback and the iPad slots are not a replacement. Twelve original CPU paths reach actual loads/stores on synthetic resources or original failure boundaries, with seven input/code rejection controls. Qualcomm security-state semantics remain unresolved.

### Completion criteria

- Dependency lifecycle, safe shutdown and each enabled power transition are independently qualified.

### Current limits

- Power, charging, sleep, thermal and battery services are not implemented for this board.

### Next action

- Derive the SM8750 security-state and power-provider contract before implementing PMGR; preserve the exact iPhone register semantics and do not install a constant-success or null-provider substitute.

### Evidence

- `host`: [Exact iPhone classes, slots and real T8015 register path; three altered-input controls](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/reports/public/ios16-pmgr-contract.json)
  Command: <code>.venv-uefi/bin/python scripts/prepare_ios16_pmgr.py</code>. Revision: `1b191cb58250d0705d8a51287127505aa4bc0789`.
- `host`: [12 original ARM64 subpaths and four instruction-corruption controls; synthetic resources and explicit IOKit peers, no Qualcomm provider or hardware qualification](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/reports/public/ios16-pmgr-kernel.json)
  Command: <code>.venv-gpu/bin/python scripts/check_ios16_pmgr_kernel.py --check-only</code>. Revision: `1b191cb58250d0705d8a51287127505aa4bc0789`.

## security {#security}

`implemented`

### Hardware and dependencies

- Exact iPhone10,3/20H392 original corecrypto 12.0, packed kmod record 1.0.0d1, actual Darwin 22 source and existing 87-object candidate.

### Configuration

- An isolated 89-object candidate uses a single original crypto/PRNG owner at SYSCTL LAST and actual OSKext loading; default source provider/candidates remain preserved.

### Procedure

- Run .venv-uefi/bin/python scripts/build\_crypto\_stack.py; --check-only validates current source/dependencies/artifacts. The portable check\_crypto\_once\_host.py is included in CI.
- Run .venv-gpu/bin/python scripts/check\_original\_crypto\_kernel.py for actual original initialization/full default POST and native consumers; --check-only validates the preserved evidence and pins.
- Run the boot entropy source/EFI, linked EFI/native seed and separate full-firmware/container checks; physical entropy quality remains a distinct qualification.

### Development findings

- Seven original inputs and 196-byte packing/48-byte PRNG callbacks are measured. Actual early/OSKext calls share one initialization result and reject conflicting or incomplete ownership. Eighteen sanitizer and 33 ARM64 ownership/startup paths pass with explicit original-initializer/POST/private-PRNG peers. Strict prelink preserves 339 aliases, 28 original components and 63889 pointer sites; independent source provider entry/POST field is absent. Loader/packed seed/FAT/Android v4 readback and 25 rejection controls pass.
- A separate ARM64 model executes the actual original initializer, all 18 full default POST tests, native PRNG/table registration, all six original callbacks and real readiness/context checks. Eighteen native SHA vectors, four fully written native PRNG transfers and one cached loader span pass; four damaged-code/answer/skipped-POST/missing-ready controls are rejected. Platform services and entropy collection remain explicit peers; no positive entropy estimate is supplied.
- Sixteen native memory-random cases and the actual 14-class EARLY\_BOOT kmem callback also pass with explicit CPU0/per-CPU allocation and post-VM page constants. Actual firmware Boot C emits an ADT that native SecureDT/PE/early PRNG consume: the first 64 bytes are cleared and hashed to the bootseed, original 18-test POST and PRNG registration then pass, and registration clears that bootseed. Two zero/short native seed inputs panic before registration. The actual embedded full-firmware EFI repeats this chain.
- The native A830 payload runs fresh EFI seed consumption and all 18 original iPhone crypto POST tests in the ARM64 model. Its addon trust bundle preserves both pinned 20H392 modules and adds only the three locally built executable hashes; runtime trust remains untested.
- The original Image4 getter and security start wrappers are measured from the pinned iPhone kernelcache. The owner development boot set provides strict no-mixing policy, BNCH and a SHA-384 manifest bound to the selected kernel, trust cache, addon, Data seed and normalized ADT. Its nonce is generated per payload build; hardware fuse state, Apple personalization and the persistent nonce lifecycle remain separate work.
- Sandbox's original module start already forwards to its policy initializer. Omitting the duplicate early hook fixes its EEXIST panic while preserving the original wrapper, slot and initializer bytes. Actual QEMU execution reaches bsd\_init with AppleImage4, AMFI and Sandbox each registered once. Missing policy, nonce and manifest inputs still fail in original Image4; missing entropy is refused by the EFI loader. Twelve owner boot-policy host cases pass.
- The separate owner-root VM kernel retains the original Apple EAUTH result and authorizes the matching read-only mounted root through signed block policy. Native Darwin 22 RSA layout is compiled, the two original callback registrations are derived from the pinned kernelcache, and actual QEMU execution reaches the init loader. Three runtime refusal controls preserve signature, DMA and UUID boundaries; the original component instructions remain unchanged.

### Completion criteria

- Original initialization and full POST execute once with correct entropy/PRNG and used KPI ABIs, before policy registration and root authentication.

### Current limits

- The frozen five-stage CPU evidence retains initializer/POST/private-PRNG peers. The separate real-original execution report removes those peers within a CPU0 ARM64 model with private host boot seed and explicit platform services. Full provider/448-byte table/appended APIs, full OSKext/C++ loading, target entropy quality, hardware policy behavior, PMGR, root/Data and hardware remain unqualified. No cryptographic result or source fallback is installed in production.

### Next action

- Qualify the actual target entropy/PRNG lifecycle and remaining used KPI consumers; finish PMGR/security-state, policy and authenticated-root integration.

### Evidence

- `host`: [Five isolated original-owner stages, 89 objects, 97 entries, 18 sanitizer paths, 33 ARM64 paths and 25 rejection controls; initializer/POST peers explicit](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/reports/public/crypto-stack.json)
  Command: <code>.venv-uefi/bin/python scripts/build_crypto_stack.py --check-only</code>. Revision: `1b191cb58250d0705d8a51287127505aa4bc0789`.
- `host`: [Actual original initializer/full 18-test POST/native PRNG/table registration in ARM64 model; 18 SHA vectors, four native PRNG transfers, one cached loader span and four rejection controls; explicit platform/entropy peers, no hardware qualification](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/reports/public/ios16-original-crypto-kernel.json)
  Command: <code>.venv-gpu/bin/python scripts/check_original_crypto_kernel.py --check-only</code>. Revision: `1b191cb58250d0705d8a51287127505aa4bc0789`.
- `host`: [Actual EFI Boot C/parser/entropy/cleanup instructions, two successful and six refused paths, two instruction controls; actual native DT/PE/early DRBG consumption followed by original 18-test POST and native registration; two missing/short seed refusals](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/reports/public/ios16-boot-entropy-kernel.json)
  Command: <code>.venv-gpu/bin/python scripts/check_boot_entropy_kernel.py --check-only</code>. Revision: `1b191cb58250d0705d8a51287127505aa4bc0789`.
- `host`: [Original AppleImage4, AMFI and Sandbox register once before bsd\_init in QEMU. Three Image4 missing-input controls and one EFI entropy refusal pass.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/reports/public/native-a830-entry.json)
  Command: <code>.venv-gpu/bin/python scripts/check_native_a830_entry.py --check-only</code>. Revision: `1b191cb58250d0705d8a51287127505aa4bc0789`.

## Image assembly {#packaging}

`host-verified`

### Hardware and dependencies

- The native A830 iPhone prelink, entropy/logger firmware, Metal addon, original iPhone trust inputs and preserved packed Data seed.

### Configuration

- A separate 160 MiB FAT carries the iPhone ADT with a four GiB initial memory request. TrustCache and GpuAddon have explicit EFI memory-map handoff records.

### Procedure

- Run .venv-gpu/bin/python scripts/build\_native\_a830\_payload.py after the prelink, firmware and addon stages; --check-only validates completed files.
- PATH="$PWD/.venv-uefi/bin:$PATH" scripts/package.sh --check --no-deps --os 16 --out build/unixnu -j 4

### Development findings

- The native 170569728-byte Android v4 container passes shim, FD, DTB and FAT readback. All files are extracted and hashed; the original iPhone identity, packed 2 GiB Data seed and boot arguments are retained.
- The actual EFI loader installs the addon and trust bundle at the final ADT memory-map addresses in an ARM64 model. The standard packaging template still resolves the 61-patch iPhone profile.
- The native FAT includes the owner development Image4 boot-set inputs. Twelve host cases and the actual EFI handoff check the selected component hashes, normalized ADT, nonce binding and unchanged static properties. The boot-set nonce changes on rebuild; kernel entropy is still refreshed on every handoff.

### Completion criteria

- Firmware, kernel and payload identities agree and every handoff extent and container component reads back correctly.

### Current limits

- The development payload excludes original userspace and root images. Complete kernel startup, root authentication and iOS boot remain untested.

### Next action

- Keep original system inputs local and qualify whole-kernel startup and root/Data integration before assembling a system payload.

### Evidence

- `host`: [Native kernel, entropy/logger firmware, addon/trust handoff and every FAT/container component pass local readback and ARM64 loader models.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/reports/public/native-a830-payload.json)
  Command: <code>.venv-gpu/bin/python scripts/build_native_a830_payload.py --check-only</code>. Revision: `6b3d90b79e191e08171bfedd3980234a7e49d340`.
- `host`: [Five addon files decompress to the built binaries; three owner hashes and both pinned iPhone trust modules read back unchanged.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/reports/public/native-a830-addon.json)
  Command: <code>.venv-uefi/bin/python scripts/build_native_a830_addon.py --check-only</code>. Revision: `1a1321056ffc5428ae925f4680093718b46ca7c2`.

## Diagnostics {#diagnostics}

`host-verified`

Components: `ArmDTPlatform`.

### Hardware and dependencies

- Pinned source platform expert, source kernel crypto provider and local build logs.

### Configuration

- Verbose kernel arguments and source-only first stage; complete source POST retained; original component crypto lifecycle remains unqualified.
- Tools &gt; Advanced Logger exports the DXE log as OneSend QR frames before kernel handoff.

### Procedure

- Run profile/native staging regressions and the source 4 KiB policy test; inspect failures before broadening scope.

### Development findings

- The native full kernel and strict iPhone prelink pass local link and pointer checks. Its boot model executes the actual EFI loader, native seed consumption and original 18-test crypto POST. QEMU TCG separately executes the packaged kernel through arm\_init, kernel\_bootstrap, InitIOKit and bsd\_init with EL1, MMU and 4 KiB tables. Its compiler-bound live MAC list contains AppleImage4, AMFI and Sandbox registered once. Missing policy, nonce, manifest and entropy controls preserve the original refusals. The next genuine panic is the absent root device.
- The QR exporter and 2 MiB DXE producer are present in the same firmware used by the native payload. Native GPU status rows feed the existing bounded boot console.
- The separate QEMU storage fixture performs real DMA from both local original disks, publishes the original storage stack and mounts the APFS root. It retains the post-mount authentication panic and rejects disabled/writable transport inputs before any disk read.

### Completion criteria

- Build and runtime failures have reproducible inputs and bounded diagnostic records.

### Current limits

- No OnePlus hardware logs or runtime observations have been collected in this task.

### Next action

- Continue from load\_init\_program into the original iPhone user process and Data paths. Keep hardware security-state and persistent nonce policy as separate target work.

### Evidence

- `host`: [The native route records each build/test stage and verifies the exact combined kernel, Metal userspace and firmware inputs.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/reports/public/native-a830-stack.json)
  Command: <code>.venv-gpu/bin/python scripts/build_native_a830_stack.py --check-only</code>. Revision: `1a1321056ffc5428ae925f4680093718b46ca7c2`.
- `host`: [Actual TCG execution reaches bsd\_init at EL1 with 4 KiB tables and three original MAC policies registered once; root mounting is the next stop. Three Image4 input refusals and one pre-entry EFI entropy refusal pass.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/c789270726a971264b2095fdc5c9190290b19611/reports/public/native-a830-entry.json)
  Command: <code>.venv-gpu/bin/python scripts/check_native_a830_entry.py --check-only</code>. Revision: `1b191cb58250d0705d8a51287127505aa4bc0789`.

## cellular {#cellular}

`planned`

### Hardware and dependencies

- CPH2653 modem firmware, SMEM/GLINK resources and factory NV/EFS inputs.

### Configuration

- No cellular driver is selected.

### Procedure

- Identify target modem transport and firmware memory before adapting QcomBaseband interfaces to iOS 16.

### Development findings

- The current official porting guide tracks cellular separately on boards with a modem.

### Completion criteria

- Modem boot, QMI, SIM, registration and data each pass their own checks.

### Current limits

- Modem startup and iPhone CommCenter integration are pending.

### Next action

- Inventory the modem resources from existing CPH2653 captures and firmware sources.

### Evidence

Collect evidence using the next action.

</div>
