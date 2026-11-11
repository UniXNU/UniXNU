# OnePlus 13 CPH2653: iPhone iOS 16 source preparation

[lihenggui/UniXNU_dodge_SM8750](https://github.com/lihenggui/UniXNU_dodge_SM8750)

<div v-pre>

OnePlus 13 CPH2653: iPhone iOS source preparation; host evidence only, no phone operations.

源记录: [porting.toml](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/814bd4943b279d91ae61ada33d4968cf749a48e7/porting.toml), `814bd4943b279d91ae61ada33d4968cf749a48e7`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `host-verified` |
| [固件与启动](#firmware) | `host-verified` |
| [CPU 与中断](#cpu) | `implemented` |
| [内存与 DMA](#memory) | `host-verified` |
| [存储与根卷](#storage) | `implemented` |
| [显示](#display) | `planned` |
| [输入](#input) | `implemented` |
| [GPU](#gpu) | `implemented` |
| [网络](#network) | `planned` |
| [音频](#audio) | `planned` |
| [电源](#power) | `planned` |
| [security](#security) | `implemented` |
| [镜像组装](#packaging) | `host-verified` |
| [诊断](#diagnostics) | `host-verified` |
| [cellular](#cellular) | `planned` |

## 配置 {#configuration}

`host-verified`

组件: `XnuPrelink`.

### 硬件与依赖

- CPH2653 / dodge / SM8750 and iPhone10,3 iOS 16.7.16 build 20H392.

### 配置

- Format 2 board; local iPhone profile; public XNU 8796.141.3 with strictly rebased Darwin 22 patch series.

### 操作步骤

- Run ./unixnu status --json, scripts/test\_ios\_profile.py and scripts/check\_ios16\_patches.py with the local Python 3.12 environment.

### 开发经验

- 61 patches apply strictly on clean pinned Apple source. The original KC is 8796.142.1.703.8, a different minor revision.
- Public reports use separate original and publication hashes. Builds inherit host memory settings and use four jobs.
- Reviewed the current porting workflow at UniXNU 75f35420137371d10b5c66399a39619991cde077 and both 13T records. Architecture/SoC/OS/board layers and existing source revisions remain selected. The unchanged standard package.sh template resolves the iPhone profile and 61 patches.

### 完成条件

- All selected sources and patch series resolve and the iPhone profile stays distinct from iPadOS.

### 当前范围

- Patch application and configuration checks do not qualify compilation or binary ABI.

### 下一步

- Audit original component layouts, crypto lifecycle and runtime initialization; strict static prelink and both reviewed security entries now pass.

### 证据

- `host`: [61 patches apply strictly on clean pinned Apple source. The original KC is 8796.142.1.703.8, a different minor revision.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/814bd4943b279d91ae61ada33d4968cf749a48e7/reports/public/ios16-rebased-patches.json)
  Command: <code>python3 scripts/check_ios16_patches.py</code>. Revision: `3fa5ff5f409398c0555a9561d6437ce5d4c3b3b7`.

## 固件与启动 {#firmware}

`host-verified`

组件: `DarwinBoot`.

### 硬件与依赖

- Pinned Mu-Silicium dodge platform and its Binaries submodule.

### 配置

- Memory patch, UniXNU app/registrar, FDT initrd driver and DarwinBoot embedded in DEBUG FD.
- The board adds AdvancedLogDxe, a DXE Core Advanced Logger producer with 512 pages, and payload.tools=true.

### 操作步骤

- Run python3 scripts/build\_uefi.py --with-unixnu-menu and scripts/validate\_uefi\_artifacts.py with four jobs and the host's inherited resource settings.
- Run .venv-uefi/bin/python scripts/build\_boot\_entropy.py, .venv-gpu/bin/python scripts/check\_boot\_entropy\_kernel.py and .venv-gpu/bin/python scripts/build\_entropy\_payload.py; each supports --check-only. All outputs use isolated source/build paths.

### 开发经验

- 53 EFI images pass build validation; Android v4 container readback matches. Production SimpleFb passes 32 sanitized failure/bounds cases. Of 54 selected donor binaries, 5 match stock, 41 differ and 8 are patched variants.
- The isolated loader refreshes the final ADT seed from a 256-byte RAW EFI RNG request per attempt and refuses errors without an old-seed fallback. Fourteen provider/order, 408 malformed/truncation and three parameter sanitizer cases pass. The full FD structurally reads back 53 generated EFI and 100 embedded images, including the exact changed loader and unchanged donor RNG; that embedded loader passes actual Boot C/native seed-to-original-POST model checks.
- The logger variant builds a 3 MiB FD with 54 validated EFI images. Firmware-volume readback finds the QR exporter; generated DXE Core inputs contain the producer constructor and 2 MiB buffer setting. SEC retains its existing debug output.

### 完成条件

- Firmware builds with the loader and all required payload filesystem interfaces.

### 当前范围

- No hardware boot. Donor firmware 16.0.7.201 differs from captured 16.0.1.304; the five-byte original ramdisk is not an iOS payload.

### 下一步

- Review differing DXE interfaces and upstream patches before selecting any stock replacement; qualify GOP scanout separately from static Mu declarations.

### 证据

- `host`: [53 EFI images pass build validation; Android v4 container, shim, FD, DTB and ramdisk readback match.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/814bd4943b279d91ae61ada33d4968cf749a48e7/reports/public/uefi-build.json)
  Command: <code>python3 scripts/validate_uefi_artifacts.py</code>. Revision: `6b3d90b79e191e08171bfedd3980234a7e49d340`.
- `host`: [Isolated full firmware and Android v4 readback; exact embedded EFI Boot C paths 2 success/6 failure plus controls and native seed-to-original-POST chain; firmware/RNG/exit peers explicit](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/814bd4943b279d91ae61ada33d4968cf749a48e7/reports/public/ios16-entropy-payload.json)
  Command: <code>.venv-gpu/bin/python scripts/build_entropy_payload.py --check-only</code>. Revision: `6b3d90b79e191e08171bfedd3980234a7e49d340`.
- `host`: [Logger firmware variant: 3 MiB FD, 54 EFI validation results, exporter GUID and AArch64 image readback, DXE producer constructor and 2 MiB setting.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/814bd4943b279d91ae61ada33d4968cf749a48e7/reports/public/uefi-logs.json)
  Command: <code>.venv-uefi/bin/python scripts/validate_uefi_artifacts.py --output build/cph2653-uefi-logs --report reports/uefi-logs.json</code>. Revision: `6b3d90b79e191e08171bfedd3980234a7e49d340`.

## CPU 与中断 {#cpu}

`implemented`

组件: `ArmCpu`.

### 硬件与依赖

- Captured GICv3 0x16000000, redistributors 0x16080000/0x40000 stride and 19.2 MHz timer; eight recorded MPIDRs.

### 配置

- Generic ArmCpu with one enabled boot CPU and cpus=1; topology admits Aff1 cores and Aff2 clusters.

### 操作步骤

- Compile the source CPU driver against Darwin 22 and inspect the generated ADT.

### 开发经验

- ArmCpu and ArmDTPlatform compile/link against Darwin 22; native timer and PAN definitions are present in actual compiler records. SM8750 topology excludes Apple CPU\_OVRD.

### 完成条件

- Each enabled CPU reaches its entry and timer/IPI checkpoints.

### 当前范围

- Hardware timer, interrupt, PSCI and SMP observations are absent.

### 下一步

- Retain single-core source bring-up; qualify original component interfaces before enabling peripherals.

### 证据

- `host`: [ArmCpu and ArmDTPlatform compile/link against Darwin 22; native timer and PAN definitions are present in actual compiler records. SM8750 topology excludes Apple CPU\_OVRD.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/814bd4943b279d91ae61ada33d4968cf749a48e7/reports/public/native-kernel.json)
  Command: <code>.venv-uefi/bin/python scripts/validate_kernel_artifacts.py</code>. Revision: `3fa5ff5f409398c0555a9561d6437ce5d4c3b3b7`.

## 内存与 DMA {#memory}

`host-verified`

### 硬件与依赖

- Captured runtime DTB SHA256 f961f2596c31c51b8db5be7b9e680aa35c86b71694820a7b5844f9829a3e7d11 and its reserved regions.

### 配置

- Firmware heap holes reserved; ADT describes a four-GiB high bank and owned-memory request.

### 操作步骤

- Compare the firmware memory descriptors to the pinned runtime DTB and read back the generated ADT.

### 开发经验

- Static descriptor checks pass; the host-executed source page policy retains native 4 KiB at RAM boundaries.

### 完成条件

- All loader handoff allocations lie in current UEFI usable memory and all DMA mappings are accounted for.

### 当前范围

- Static DTS memory is not a substitute for the runtime UEFI map; DMA hardware is untested.

### 下一步

- Retain runtime-allocation proof as a separate requirement; local native kernel and payload checks now pass.

### 证据

- `host`: [Static descriptor checks pass; the host-executed source page policy retains native 4 KiB at RAM boundaries.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/814bd4943b279d91ae61ada33d4968cf749a48e7/reports/public/memory-after.json)
  Command: <code>python3 scripts/check_uefi_memory.py --map uefi/Mu-Silicium/Platforms/OnePlus/dodgePkg/Library/MemoryMapLib/MemoryMapLib.c --dtb &lt;captured-dtb&gt; --expected-sha256 f961f2596c31c51b8db5be7b9e680aa35c86b71694820a7b5844f9829a3e7d11</code>. Revision: `6b3d90b79e191e08171bfedd3980234a7e49d340`.

## 存储与根卷 {#storage}

`implemented`

### 硬件与依赖

- Captured UFS 0x1d84000, interrupt 265, SMMU stream 0x60; pinned iPhone OS/SystemOS and NativeUfs reference.

### 配置

- Default physical UFS remains disabled. Probe-only archive is preserved; a complete read-only root publisher and explicit IOBSD storage-before-graphics coordinator are separately linked against the exact 144-byte/190-slot iPhone original class. No physical partition is created.

### 操作步骤

- Run scripts/build\_storage\_stack.py with the local .venv-uefi Python; it selects .venv-gpu for linked CPU checks. Use --check-only to verify all five current stages without rebuilding.
- Run scripts/build\_data\_stack.py for both APFS seeds, real source lifecycle/helpers, the 83-object strict original prelink and CPU paths; --check-only verifies current reports/artifacts.
- Run .venv-gpu/bin/python scripts/check\_ramblock\_start\_kernel.py for the actual startup/live chain; --check-only validates its current evidence.

### 开发经验

- Original iPhone storage ABI, 12 storage aliases and the concrete 190-slot class are checked. Complete read-only UFS/ordered root-window publication and deferred original-module/native-class startup compile into a combined 68-object kernel. 32 lifecycle, 25 combined scheduling, eleven source probe matching and production root-publication host checks pass with explicit peers. Combined strict prelink reads 58962 original pointers, 208 aliases and both concrete/parent vtables. Eleven linked CPU paths execute native/source/original constructors and combined IOBSD plus three full display lifetime paths. The exact 8380219392-byte OS/SystemOS regular-file payload passes full hash readback and 32 production consumer cases. All 198 stock initial Data entries are archived with numeric ownership, permissions, links and xattr metadata, with eight corruption controls. Separate 2/3 GiB APFS v2 seeds now preserve all content/metadata and compression, pass independent read-back, strict compatible apfsck and 17 rejection controls each. The 352-byte/190-slot RamBlock and deferred registration/one-shot start link into a separate 83-object candidate retaining 332 aliases. 77 sanitizer and 30 ARM64 paths pass, including original protected constructors/destructors; 43 rejection controls pass across Data stages.
- A separate 84-object/85-entry startup candidate now queues system/Data/input in actual IOBSD. Thirty scheduler sanitizer and 43 CPU paths plus 24 rejection controls pass; the exact 721024-byte packed 2 GiB seed and preserved iPhone ADT pass actual DarwinBoot C handoff parsers and FAT/Android v4 container readback. Data remains default-off; the original mount is unqualified.
- Seven additional init/Data stages pass: exact 336-byte user/324-byte APFS request ABI, 19 original-program and 80 native/original-prefix CPU paths, 16 new request sanitizer cases and 32 rejection controls. An 87-object/91-entry candidate wires actual PID 1 scratch/Data/init ordering, uses exact seed identity and post-mount checks, and passes independent container readback. Apple option/VFS/mount/VM/IOKit/init peers remain explicit; original mount and root authentication are unqualified.
- The unchanged RamBlock start now executes against exact 2/3 GiB seeds in the 87-object candidate: 28 start paths, full 524288-page 2 GiB hashing, then 26 live I/O and 68 selector paths on the actual started objects, plus four rejection controls. Native metadata getters execute; platform/registry/type/hash/descriptor peers remain explicit. Original media publication, full APFS and persistence remain unqualified.

### 完成条件

- Qualified storage ABI, read transport, authenticated root policy and original launchd execution.

### 当前范围

- No physical UFS access, partition creation or authenticated-root readiness. Original system windows and initial Data content are prepared as local files; boot.img does not contain those windows, and APFS Data formatting/readback is prepared separately; writable runtime remains unqualified. Controller/SMMU/DMA ownership, class/IOStorageCompletion runtime ABI, actual service matching and APFS/Data/power remain unqualified. Failed hardware start retains resources until reset; rollback is unqualified.

### 下一步

- Qualify the implemented full read-only transport, original storage matching/completion and root publication; qualify authenticated-root, the implemented PID 1 Data mount route, original media matching, full parent/registry and crypto/power lifecycle. The default-off init route is wired and modeled; physical qualification remains outstanding.

### 证据

- `host`: [The iOS 16 source probe compiles, 212 public native imports match by name, and the real local UBSAN runtime dependency is recorded for static linking. Eight existing read-only host suites pass ASan/UBSan.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/814bd4943b279d91ae61ada33d4968cf749a48e7/reports/public/ufs-source-probe.json)
  Command: <code>.venv-uefi/bin/python scripts/build_ufs_probe.py --partition unixnu</code>. Revision: `f5017376415268fd39dcf0b3fd68a94661cee078`.
- `host`: [Complete read-only root publisher, original iPhone ABI, 32 lifecycle and 25 combined startup host cases; strict 68-object/208-alias source and original-component prelink, no runtime activation](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/814bd4943b279d91ae61ada33d4968cf749a48e7/reports/public/ios16-ufs-root.json)
  Command: <code>.venv-uefi/bin/python scripts/build_ufs_root.py</code>. Revision: `f5017376415268fd39dcf0b3fd68a94661cee078`.
- `host`: [Six Data stages pass: two exact original-content APFS seeds, 77 sanitizer cases, 30 ARM64 paths, 43 rejection controls and an 83-object/28-component strict prelink. Original Data matching/mount and writable runtime remain unqualified.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/814bd4943b279d91ae61ada33d4968cf749a48e7/reports/public/data-stack.json)
  Command: <code>.venv-uefi/bin/python scripts/build_data_stack.py --check-only</code>. Revision: `4be2d7eb05ef5a98126c91e0302c149140c0e3e1`.
- `host`: [Four startup stages, 84 objects, 30 scheduler sanitizer cases, 43 CPU paths and 24 rejection controls pass. Packed Data/ADT/FAT/Android readback passes; no phone or original Data mount qualification.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/814bd4943b279d91ae61ada33d4968cf749a48e7/reports/public/data-startup-stack.json)
  Command: <code>.venv-uefi/bin/python scripts/build_data_startup_stack.py --check-only</code>. Revision: `4be2d7eb05ef5a98126c91e0302c149140c0e3e1`.
- `host`: [Exact iPhone ordinary Data requests, 87-object/91-entry init hook, 19 original-program and 80 source/original-prefix CPU paths, 32 rejection controls and container readback pass; no real APFS mount/root authentication.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/814bd4943b279d91ae61ada33d4968cf749a48e7/reports/public/data-mount-stack.json)
  Command: <code>.venv-uefi/bin/python scripts/build_data_mount_stack.py --check-only</code>. Revision: `244c76b2610adc6bbfceceea7028665be6df560e`.
- `host`: [28 actual start, 26 subsequent I/O and 68 selector ARM64 paths; four rejection controls, no state reconstruction or original APFS/runtime qualification](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/814bd4943b279d91ae61ada33d4968cf749a48e7/reports/public/ios16-ramblock-start-kernel.json)
  Command: <code>.venv-gpu/bin/python scripts/check_ramblock_start_kernel.py --check-only</code>. Revision: `4be2d7eb05ef5a98126c91e0302c149140c0e3e1`.

## 显示 {#display}

`planned`

### 硬件与依赖

- Captured AA569 panel references, 1440 by 3168 Android mode; upstream GOP and display source candidates.

### 配置

- The iPhone artwork scale is three. DarwinBoot consumes GOP; Mu SimpleFb currently uses static 1440x3168x32 and 0xfc800000 platform declarations, with bounds/error checks; physical scanout geometry remains unqualified.

### 操作步骤

- Audit GOP handoff and derive display-family bindings from the pinned iPhone kernelcache.

### 开发经验

- Exact original iPhone class hierarchy and table extents pass static audit. Legacy is 5728 bytes/338 entries; fourteen typed virtual dispatch probes pass across 45 CPU cases; eight raw backend call shapes are qualified while slot 243 arguments and all operation/status semantics remain open. The partial base retains nine abstract slots; a separate concrete GOP subclass now supplies bounded error/no-op entries, a raw stock-equivalent slot 243 leaf, and service coordination. This archive passes 60 coordinator, ten actual frontend/bridge/refresh integration and 69 native CPU cases. A separate 64-object kernel includes the class and explicit original-module prepare/attach entry points; 33 sanitized orchestration peer cases pass, including original software-root presence/class and provider checks. Another 32 CPU cases execute full original Legacy init/start/post-hardware/stop/free together with the concrete source class from the real prelink; IOKit/coordinator/matching/scheduler are explicit peers. Three original dispatcher cases cover late provider use, and the source now retains provider until free. Real original parent lifecycle and physical power remain unqualified. The bounded frontend waits original producers plus a captured Adreno timeline, defaults to CPU scanout copy, and connects optional disabled software refresh. Its startup factory retains inputs while entering the original work-loop gate and rechecks identity/mode/queue state before creating the frontend. 121 sanitized frontend cases cover queue reconciliation, reentrant release, waits, cancellation, mode matching, empty startup queues and stop. Another 29 CPU cases check original init/queue blocks; registration occurs before original start returns. The 23 original-userland cases connect three unchanged kernel size functions to CGSize conversion. Sixteen additional completion body/guard CPU cases execute thirteen unchanged full-body paths and twelve release/current-clear/wakeup tails with explicit lifetime peers. A separate native derived fixture verifies all 338 vtable slots, 170 original inherited-method/C2/D2 aliases plus one parent-metaclass alias and seven bounded lifetime cases comparing actual original/source-kernel parent C2/D2 without parent peers; no real provider or metaclass is registered. The real-class GOP factory now allocates the exact 216-byte original AppleARMIODevice, uses inherited public init, reads back actual PE memory resources, and pins the published nub/metaclass. Sixty sanitizer cases and eighteen linked CPU paths cover ownership, original allocation/native constructors, early unwind and the actual IOBSD hook. An isolated native object schedules a bounded worker only with dodge-graphics=1; twenty-four scheduling sanitizer cases pass. Real registry, loader, generic init, allocation and scheduling remain explicit peers; kernel runtime and Apple bus/clock methods remain unqualified.

### 完成条件

- A verified framebuffer can display diagnostics and the original mobile display client can present.

### 当前范围

- GOP geometry and actual display-family ABI are unqualified.

### 下一步

- Qualify real original loader and full parent/user-client/IOSurfaceRoot lifetime, physical mapping and power. The real-class GOP factory and IOBSD opt-in worker are implemented and linked; actual publication, producer fences/cache visibility and GPU failure quiescence remain unqualified.

### 证据

- `host`: [Concrete exact Legacy/GOP source class and coordinator compile for Darwin 22. Strict link reads all 338 slots, 172 original aliases and 191 native/GPU imports. 60 coordinator sanitizer cases, ten actual frontend/bridge/refresh integration cases and 69 native CPU cases pass with explicit peers. Publication waits until parent start returns; gated client admission and deferred detach preserve resources through drain and parent stop. Failed Legacy start retains partial resources; source cleanup now runs once after start returns and frontend drain. Eleven bounded no-surface paths execute unchanged full original stop with explicit IOKit peers. Explicit OSKext preparation, Kernel pre/postModLoad and attachment compile into a separate strict 64-object kernel and original-graphics prelink. An additional 32 full linked lifecycle CPU cases execute actual original init/start/post-hardware/stop/free and source class instructions with primitive IOKit/core peers; two corruption/boundary controls are rejected. A provider lifetime pin protects the late original dispatcher after detach. A unified explicit boot coordinator holds provider/root and orders modules, atomic one-shot A830 startup and display attach; 24 sanitizer cases plus six direct board entry cases with 16-way calls pass with API peers. A separate FAT/Android v4 development container passes complete readback; original userspace/root remain absent and opt-in startup is disabled by default.  The real-class GOP factory now allocates the exact 216-byte original AppleARMIODevice, uses inherited public init, reads back actual PE memory resources, and pins the published nub/metaclass. Sixty sanitizer cases and eighteen linked CPU paths cover ownership, original allocation/native constructors, early unwind and the actual IOBSD hook. An isolated native object schedules a bounded worker only with dodge-graphics=1; twenty-four scheduling sanitizer cases pass. Real registry, loader, generic init, allocation and scheduling remain explicit peers; kernel runtime and Apple bus/clock methods remain unqualified. Real original loader/start/stop, service matching, power and runtime remain unqualified; defaults are unchanged.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/814bd4943b279d91ae61ada33d4968cf749a48e7/reports/public/ios16-display-service.json)
  Command: <code>.venv-gpu/bin/python scripts/build_display_service.py</code>. Revision: `3fa5ff5f409398c0555a9561d6437ce5d4c3b3b7`.

## 输入 {#input}

`implemented`

### 硬件与依赖

- Captured S3910 HBP/SPI 0xa90000/QUP SID 0xa3/reset 161/ATTN 162/19 MHz; target power/reset delays and matching original HBP raw-GPIO semantics; exact iPhone 20H392 original IOHIDFamily; exact CPH2653 16.0.1.304 UEFI SPI SEFW and independent identical I2C-module copy.

### 配置

- Separate 81-object input/storage/display candidate and local container; dodge-input=1 disabled by default. Original 208-byte/207-slot base, 1560-byte concrete class, 53 HID aliases and 35 opaque data-only slots. Only four extra HID operations callable. AVDD SID9 GPIO3 validates retained electrical fields, preloads physical high, then initializes direction and enable; VDD ldob4 1.8 V. QUP4 SPI loader accepts only an idle empty engine without DMA/GPI ownership, programs 442 words/69 configuration entries from the pinned 2141-byte stock SEFW and verifies every write. The stopped/unvoted/non-DFS SE4 root now initializes to the derived 19.2 MHz XO after ownership checks; existing roots/DFS use live locked GPLL0 and M/N readback, without rewriting shared PLLs/voltage. Warm SPI adoption also refuses leftover DMA/GPI/FIFO ownership. No donor LDO16 or private EventDriver mutation. Bounded event80/37 and driver264/219 declarations with 71 data-only bindings are included with a 552-byte/219-slot source edge subclass. Its Kernel personality is read back as \_\_kernel\_\_; original tables and event fields are accessed only through qualified APIs. Full transfer requires DMA data, command completion and engine idle before RX delivery; bounded cancel/abort/reset ACK and sticky errors prevent reuse. Source start/stop run on the workloop gate; reentrant stop retains the provider and defers parent cleanup until callbacks exit.

### 操作步骤

- Run scripts/build\_input\_stack.py, or --check-only to verify all twenty-two current stages, dependency hashes and artifacts. Public CI runs scripts/check\_input\_cold\_host.py --synthetic without proprietary input.

### 开发经验

- 3556 source sanitizer cases pass: 84 existing power/lifecycle/worker plus 73 cold GPIO, 2740 GENI parser/loader, 135 target-clock, 224 full transfer/terminal and 300 edge-origin cases. 201 CPU paths pass: 16 original HID callers, seven original init/free audits, 11 current prelinked constructor/BSD, 18 cold parser/loader, 18 clock, 20 full transfers, 12 original C HID parser/cleanup and 27 actual source gated start/stop/tick/drain and 32 actual original event accessor/default-dispatch and 40 source edge/registration/lifetime paths. Another 52 checks compare actual native S3910 reports against original parsed usage/bit/logical metadata. The unchanged original early-DMA-completion control and missing source stop are rejected. Exact 207 input and 219 source-event concrete pointers, 209-word HID and 221-word event parent tables, native chains, 332 combined aliases, 77 source entries, 28 original components/seven interfaces, all 63889 pointer sites and embedded SPI firmware read back; actual loader and FAT/Android v4 parsers accept the isolated container.
- The c888efd3ce1b817d13f28783a77cf689cb2255c9 mapping helper is reused unchanged. CPH2653 maps its RPMh command database with kIOMapReadOnly. All 22 input stages pass again, including the 81-object native candidate, iPhone prelink and local container.

### 完成条件

- Touch contacts, edge gestures and each physical button produce correct original HID events, with qualified power and cleanup.

### 当前范围

- Host MMIO/clock/loader/IOKit and CPU allocation/memory/gate/mapping/timer/thread/refcount peers remain explicit; original parent start/stop and HID submission in source drain checks are peers. Serial-engine firmware is not executed. The actual original C HID parser/cleanup executes, but complete original device start, element dispatch, EventDriver matching/UI and remaining private event semantics remain unqualified or incomplete. The used event accessors and default dispatch pass 32 CPU cases; other private prototypes stay unavailable. Target orientation, shared clock/power-domain/electrical recovery and full SMMU/DMA/reset hardware takeover remain incomplete or unqualified. Objects/provider are pinned before original init, failures are latched without release, and maps stay pinned after hardware attempts; shared votes remain enabled. No phone operation or working iOS claim.

### 下一步

- Complete shared clock/power-domain/electrical policy and qualify SMMU/DMA/reset ownership beyond bounded terminal recovery. Qualify full original EventDriver lifecycle, source edge/client ordering and original device start/element/matching; keep default candidates disabled.

### 证据

- `host`: [Twenty-two current offline stages, 3556 sanitized source cases, 201 CPU paths plus 52 report checks and independent 81-object/332-alias/77-entry/28-original-component local container; exact stock SPI SEFW embedded, no runtime/hardware/full-iOS qualification](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/814bd4943b279d91ae61ada33d4968cf749a48e7/reports/public/input-stack.json)
  Command: <code>.venv-uefi/bin/python scripts/build_input_stack.py --check-only</code>. Revision: `f5017376415268fd39dcf0b3fd68a94661cee078`.
- `host`: [Original 208-byte/207-slot IOHIDDevice vs public 205-slot reference; original/public facts stay distinct from bounded callable source interface](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/814bd4943b279d91ae61ada33d4968cf749a48e7/reports/public/ios16-hid-abi.json)
  Command: <code>.venv-uefi/bin/python scripts/prepare_hid_abi.py</code>. Revision: `f9edab5e6cc6b2cf01ec8dfc6f2a41fd60e3a0bc`.

## GPU {#gpu}

`implemented`

组件: `Adreno740`, `AdrenoMetal`.

### 硬件与依赖

- Captured Adreno830v2 0x44050001, six target power policies, exact CPH2653 16.0.1.304 stock microcodes, pinned A830/Metal/HFI/Mesa/translator sources and exact iPhone KC.

### 配置

- Independent 54-object GPU and 64-object concrete-display/module-lifecycle kernels, strict original-graphics prelinks, and ordinary ARM64/iOS 16 Rust/Turnip/Metal userspace. Original-parent accelerator initialization is deferred. Default kernel and prelink closure leave GPU disabled.

### 操作步骤

- Run scripts/build\_gpu\_stack.py for the offline build chain, or --check-only to verify current artifacts and matching stage identities.
- Run .venv-gpu/bin/python scripts/build\_fresh\_gpu\_stack.py for the separate original-IOSurface/fresh-health route; --check-only verifies completed stages and --record-existing validates and records existing outputs.
- Run .venv-gpu/bin/python scripts/build\_mapped\_lease\_stack.py for isolated all-mapping leases and bounded lock-free map waiting; --check-only verifies completed stages.
- Run .venv-gpu/bin/python scripts/build\_surface\_identity\_stack.py for isolated current-task identity resolution, native binding, strict full prelink and source-to-original permission/reference checks; --check-only preserves completed outputs.
- Run .venv-gpu/bin/python scripts/build\_surface\_pages\_stack.py for the kernel-only owned-descriptor/import page association; --check-only preserves all completed outputs. The caller must already own the exact original descriptor through original-component serialization.
- Run .venv-uefi/bin/python scripts/build\_native\_a830.py after source preparation for the standalone Shad0w23333 native Gen8 archive.
- Run python3 scripts/check\_native\_a830\_host.py for fifteen native A830 software-controller suites on Linux.

### 开发经验

- Actual full backend, target microcode/policy/board/presenter, Rust bridge, Turnip and Metal bundle builds pass. Board metal registration releases failed init/attach instances and refuses failed property writes; 15 sanitizer cases compile its actual staged function with loader/IOKit peers. Existing ASan/UBSan tests and target/4 KiB code-page readback pass. Target vendor\_boot matches the captured A-slot manifest. Exact iPhone Legacy is 5728 bytes/338 slots, rejecting the iPadOS17 reference layout.
- A separate 90-object/97-entry/341-alias kernel rechecks native GPU health after a historical fence pass, after backing and before copy/retirement. Original IOSurface writer errors do not automatically reach waiting readers. Exact notification bindings, 17 original notification-chain cases, 132 frontend sanitizer cases, 84 actual-kernel paths and strict 63889 pointer readbacks pass; two unsafe source variants fail.
- Each submit conservatively holds all current VM mappings; late mapping waits outside the publisher lock, bounded by one second and 16384 attempts. Cache failure/uncertain zero-fence publication retains the whole lease. 28 new sanitizer cases, three existing suites, five source controls, 112 actual-kernel paths and strict prelink/container readback pass.
- A kernel-callable current-task resolver uses the exact original IOSurfaceRoot entry. Actual original task/client cache, membership and policy plus the custom CAS reference counter at +1000 execute; +12 is the surface ID. Thirteen sanitizer cases, three source controls, 20 original identity and 17 source-to-original paths pass. The separate 92-object/99-entry/342-alias candidate repeats 112 existing ARM64 regressions and strict prelink.
- Kernel-only association checks original descriptor identity, allocation rounding, direction, length and every imported physical page. It independently prepares/holds descriptor, surface and real native memory. Complete failure quarantines ownership; VM/job holds defer release. Thirty-five ASan/UBSan cases, four source controls, 25 new actual-linked ownership/VM paths and five instruction controls pass. A 94-object/102-entry/343-alias candidate reruns 149 earlier ARM64 regressions and strict prelink.
- The standalone Shad0w23333 Adreno830 snapshot 1a1321056ffc5428ae925f4680093718b46ca7c2 builds 51 iOS 16 objects with its matching SMMU library and exact iPhone accelerator binding. Its Darwin 22 adapter spells out data-free operations around a dependent-template compiler failure. Linux host tests account for Clang 18 aggregate-zero initialization warnings. The existing Metal frontend adds selectors 17/18 to the shared v2 base and needs a deliberate protocol merge.

### 完成条件

- GPU power, SMMU, firmware, queues and known shader outputs operate through the original iPhone graphics clients.

### 当前范围

- Source display imports resolve to real console/completion/software timer implementations. 93 bridge, 121 bounded frontend and 46 timer sanitized cases use software peers. CPU scanout is the default; experimental presenter mode requires failed/abandoned GPU work to be quiescent before callback. Isolated static linking treats nine unselected optional diagnostics as absent weak addresses; no dummy providers are present. Concrete provider/registration/power hooks, request retirement, actual producer fences/cache visibility, GPU failure quiescence, original graphics initialization and physical rendering remain unqualified. No owner trust or hardware access.
- Fresh health snapshots do not qualify GPU/presenter quiescence or cache/DMA visibility. Two new IOSurface aliases are compiled into the isolated candidate; producer registration is not wired into the Adreno client by those aliases. Actual original surface allocation and the display +5056 surface lifecycle remain unexecuted.
- Resource leases provide lifetime accounting. A kernel-only owned-descriptor/import page association exists, but source descriptor acquisition and original backing-mutation/check-to-submit serialization remain unqualified. GPU user-client import does not yet use the association. Producer registration, pending callback/cancel/exit ordering, physical GPU/cache/reset and final descriptor/surface destruction remain incomplete or unqualified.
- The standalone Gen8 archive has no CPH2653 startup or embedded firmware. It is a separate source candidate; full prelink, frontend protocol and runtime lifecycle integration are pending.

### 下一步

- Qualify the linked original-module prepare/attach and complete parent start/stop/user-client lifecycle; qualify the linked unified module/GPU/display boot coordinator through the implemented real-class GOP factory, opt-in IOBSD worker and original-service matching in the isolated candidate.
- Acquire an owned exact original surface descriptor through qualified original-component serialization, wire the checked association into GPU user-client imports, and connect per-job producer registration, asynchronous grants, completion signalling, cancellation and client exit.
- Build the standalone Adreno830Board inputs from the captured CPH2653 GPU/GMU/thermal resources and pinned firmware. Merge the iPhone Metal selector extensions and existing surface/lease ownership before selecting this backend.

### 证据

- `host`: [Forty-six source/build/test stages pass: independent 54-object GPU and 64-object concrete-display/module kernels, 93 bridge, 121 frontend and 46 timer sanitized cases, 60 coordinator, ten actual frontend integration and 33 original-module orchestration sanitizer cases, plus 69 concrete-class ARM64 checks and 32 full linked original/source lifecycle CPU paths. Three original dispatcher cases check provider survival through detach; two negative controls reject a lost pin and an unreviewed native call. Fifteen board Metal registration sanitizer cases cover publication and allocation/init/property/attach cleanup with explicit loader/IOKit peers. Five full original newUserClient method paths and three admission refusals use explicit client lifetime peers. Unified boot ordering passes 24 peer cases and the actual atomic board entry passes six, including 16 concurrent callers. A separate local FAT/Android v4 development container is verified; it excludes original userspace/root and does not auto-invoke graphics. The real-class GOP publisher passes sixty host and eighteen linked CPU cases, including actual original allocation/native constructors and four real IOBSD scheduling paths. An isolated opt-in IOBSD worker passes twenty-four sanitizer cases. Existing original dispatch/lifecycle/userland/refresh CPU checks pass. The full-display strict prelink contains 27 original executable components/7 interfaces with 58962 pointer, 196 alias, 338 owned/340 base and 178 provider/14 metadata vtable, 53 constructor/53 finalizer, POST and loader readbacks plus ten corruption controls. Linked iOS16 userspace, six SPIR-V modules and four A830 code/reassembly cases pass. Default artifacts remain unchanged; original graphics initialization and runtime qualification remain incomplete.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/814bd4943b279d91ae61ada33d4968cf749a48e7/reports/public/gpu-stack.json)
  Command: <code>.venv-uefi/bin/python scripts/build_gpu_stack.py --check-only</code>. Revision: `1baf6d3a1d0f133d284f8b8844cc98bf5aff1bbe`.
- `host`: [Five isolated stages: exact original IOSurface notification chain, fresh-health frontend, strict full prelink, 84 ARM64 paths and separate FAT/Android v4 with unchanged fresh-entropy firmware. Explicit primitive/fence/IOKit peers; no hardware or complete-port qualification.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/814bd4943b279d91ae61ada33d4968cf749a48e7/reports/public/fresh-gpu-stack.json)
  Command: <code>.venv-gpu/bin/python scripts/build_fresh_gpu_stack.py --check-only</code>. Revision: `1baf6d3a1d0f133d284f8b8844cc98bf5aff1bbe`.
- `host`: [Mapped resource lifetime and bounded map-wait route: 28 new sanitizer cases, three existing suites, 112 ARM64 paths, strict 90-object prelink and separate entropy-EFI/FAT/Android v4 container. Explicit peers; IOSurface producer and physical cache/reset remain unqualified.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/814bd4943b279d91ae61ada33d4968cf749a48e7/reports/public/mapped-lease-stack.json)
  Command: <code>.venv-gpu/bin/python scripts/build_mapped_lease_stack.py --check-only</code>. Revision: `1baf6d3a1d0f133d284f8b8844cc98bf5aff1bbe`.
- `host`: [Kernel-callable current-task identity resolution: 13 sanitizer cases, three source controls, 20 original and 17 source-to-original identity ARM64 paths, seven instruction and five original invariant controls. Complete 92-object strict prelink and 112 preserved GPU/surface/display regressions. Explicit primitive peers; GPU backing association and producer remain incomplete.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/814bd4943b279d91ae61ada33d4968cf749a48e7/reports/public/surface-identity-stack.json)
  Command: <code>.venv-gpu/bin/python scripts/build_surface_identity_stack.py --check-only</code>. Revision: `1baf6d3a1d0f133d284f8b8844cc98bf5aff1bbe`.
- `host`: [Kernel-only already-owned surface descriptor/import page association: 35 sanitizer cases, four source controls, 25 actual-linked native/original ownership and VM-job cases, five instruction controls; 149 retained regressions and complete 94-object strict prelink. Descriptor acquisition, user-client and producer wiring remain incomplete; primitive prepare/physical/cache peers explicit.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/814bd4943b279d91ae61ada33d4968cf749a48e7/reports/public/surface-pages-stack.json)
  Command: <code>.venv-gpu/bin/python scripts/build_surface_pages_stack.py --check-only</code>. Revision: `1baf6d3a1d0f133d284f8b8844cc98bf5aff1bbe`.
- `host`: [Standalone native A830 archive: 51 arm64 iOS 16 objects and original iPhone accelerator binding. Board startup and frontend integration remain separate.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/814bd4943b279d91ae61ada33d4968cf749a48e7/reports/public/native-a830.json)
  Command: <code>.venv-uefi/bin/python scripts/build_native_a830.py</code>. Revision: `1a1321056ffc5428ae925f4680093718b46ca7c2`.
- `host`: [Fifteen ASan/UBSan suites over software controllers: startup, SMMU, GMU/HFI, CP, fences, interrupts, power/recovery, DCVS, VM and user clients. ARM barriers and allocator calls have explicit host peers.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/814bd4943b279d91ae61ada33d4968cf749a48e7/reports/public/native-a830-host.json)
  Command: <code>python3 scripts/check_native_a830_host.py</code>. Revision: `1a1321056ffc5428ae925f4680093718b46ca7c2`.

## 网络 {#network}

`planned`

### 硬件与依赖

- OnePlus 13 wireless and USB hardware; no network driver selected.

### 配置

- No synthetic network service is registered.

### 操作步骤

- Inventory firmware, buses and OS interfaces from existing captures and source.

### 开发经验

- There is no host build or hardware network evidence for this port.

### 完成条件

- A supported transport transfers data with bounded timeouts and correct addressing.

### 当前范围

- Wi-Fi, Bluetooth, cellular and USB networking are unimplemented here.

### 下一步

- Select a concrete transport and define its board and iOS ABI contract.

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`planned`

### 硬件与依赖

- OnePlus 13 audio hardware; original iPhone audio product metadata is preserved.

### 配置

- No audio driver is selected.

### 操作步骤

- Inventory codec/DSP topology and required firmware before implementing a transport.

### 开发经验

- Product identity is independent of functional audio support.

### 完成条件

- Playback/capture and routing work through the original audio clients.

### 当前范围

- No codec, DSP, speaker or microphone operation is qualified.

### 下一步

- Prepare a board-specific audio transport after the initial kernel path.

### 证据

按下一步操作收集证据。

## 电源 {#power}

`planned`

### 硬件与依赖

- SM8750 PSCI SMC and pinned SoC operations; original iPhone AMFI declares a PMGR dependency.

### 配置

- sleep-disabled=1 for bring-up; no battery or thermal values are fabricated.

### 操作步骤

- Audit original AMFI/PMGR entry points and the captured PMIC/RPMh board resources.

### 开发经验

- PMGR compatibility is a specific ABI dependency and does not imply a complete power manager.
- Exact iPhone PMGR classes and AMFI slots 312/313 are derived. The T8015 target performs real 32-bit read/OR-4/write at region 1/bank 0/offset 0xd0030; its base/null fallback and the iPad slots are not a replacement. Twelve original CPU paths reach actual loads/stores on synthetic resources or original failure boundaries, with seven input/code rejection controls. Qualcomm security-state semantics remain unresolved.

### 完成条件

- Dependency lifecycle, safe shutdown and each enabled power transition are independently qualified.

### 当前范围

- Power, charging, sleep, thermal and battery services are not implemented for this board.

### 下一步

- Derive the SM8750 security-state and power-provider contract before implementing PMGR; preserve the exact iPhone register semantics and do not install a constant-success or null-provider substitute.

### 证据

- `host`: [Exact iPhone classes, slots and real T8015 register path; three altered-input controls](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/814bd4943b279d91ae61ada33d4968cf749a48e7/reports/public/ios16-pmgr-contract.json)
  Command: <code>.venv-uefi/bin/python scripts/prepare_ios16_pmgr.py</code>. Revision: `1b191cb58250d0705d8a51287127505aa4bc0789`.
- `host`: [12 original ARM64 subpaths and four instruction-corruption controls; synthetic resources and explicit IOKit peers, no Qualcomm provider or hardware qualification](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/814bd4943b279d91ae61ada33d4968cf749a48e7/reports/public/ios16-pmgr-kernel.json)
  Command: <code>.venv-gpu/bin/python scripts/check_ios16_pmgr_kernel.py --check-only</code>. Revision: `1b191cb58250d0705d8a51287127505aa4bc0789`.

## security {#security}

`implemented`

### 硬件与依赖

- Exact iPhone10,3/20H392 original corecrypto 12.0, packed kmod record 1.0.0d1, actual Darwin 22 source and existing 87-object candidate.

### 配置

- An isolated 89-object candidate uses a single original crypto/PRNG owner at SYSCTL LAST and actual OSKext loading; default source provider/candidates remain preserved.

### 操作步骤

- Run .venv-uefi/bin/python scripts/build\_crypto\_stack.py; --check-only validates current source/dependencies/artifacts. The portable check\_crypto\_once\_host.py is included in CI.
- Run .venv-gpu/bin/python scripts/check\_original\_crypto\_kernel.py for actual original initialization/full default POST and native consumers; --check-only validates the preserved evidence and pins.
- Run the boot entropy source/EFI, linked EFI/native seed and separate full-firmware/container checks; physical entropy quality remains a distinct qualification.

### 开发经验

- Seven original inputs and 196-byte packing/48-byte PRNG callbacks are measured. Actual early/OSKext calls share one initialization result and reject conflicting or incomplete ownership. Eighteen sanitizer and 33 ARM64 ownership/startup paths pass with explicit original-initializer/POST/private-PRNG peers. Strict prelink preserves 339 aliases, 28 original components and 63889 pointer sites; independent source provider entry/POST field is absent. Loader/packed seed/FAT/Android v4 readback and 25 rejection controls pass.
- A separate ARM64 model executes the actual original initializer, all 18 full default POST tests, native PRNG/table registration, all six original callbacks and real readiness/context checks. Eighteen native SHA vectors, four fully written native PRNG transfers and one cached loader span pass; four damaged-code/answer/skipped-POST/missing-ready controls are rejected. Platform services and entropy collection remain explicit peers; no positive entropy estimate is supplied.
- Sixteen native memory-random cases and the actual 14-class EARLY\_BOOT kmem callback also pass with explicit CPU0/per-CPU allocation and post-VM page constants. Actual firmware Boot C emits an ADT that native SecureDT/PE/early PRNG consume: the first 64 bytes are cleared and hashed to the bootseed, original 18-test POST and PRNG registration then pass, and registration clears that bootseed. Two zero/short native seed inputs panic before registration. The actual embedded full-firmware EFI repeats this chain.

### 完成条件

- Original initialization and full POST execute once with correct entropy/PRNG and used KPI ABIs, before policy registration and root authentication.

### 当前范围

- The frozen five-stage CPU evidence retains initializer/POST/private-PRNG peers. The separate real-original execution report removes those peers within a CPU0 ARM64 model with private host boot seed and explicit platform services. Full provider/448-byte table/appended APIs, full OSKext/C++ loading, target entropy quality, policy registration, PMGR, root/Data and hardware remain unqualified. No cryptographic result or source fallback is installed in production.

### 下一步

- Qualify the actual target entropy/PRNG lifecycle and remaining used KPI consumers; finish PMGR/security-state, policy and authenticated-root integration.

### 证据

- `host`: [Five isolated original-owner stages, 89 objects, 97 entries, 18 sanitizer paths, 33 ARM64 paths and 25 rejection controls; initializer/POST peers explicit](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/814bd4943b279d91ae61ada33d4968cf749a48e7/reports/public/crypto-stack.json)
  Command: <code>.venv-uefi/bin/python scripts/build_crypto_stack.py --check-only</code>. Revision: `1b191cb58250d0705d8a51287127505aa4bc0789`.
- `host`: [Actual original initializer/full 18-test POST/native PRNG/table registration in ARM64 model; 18 SHA vectors, four native PRNG transfers, one cached loader span and four rejection controls; explicit platform/entropy peers, no hardware qualification](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/814bd4943b279d91ae61ada33d4968cf749a48e7/reports/public/ios16-original-crypto-kernel.json)
  Command: <code>.venv-gpu/bin/python scripts/check_original_crypto_kernel.py --check-only</code>. Revision: `1b191cb58250d0705d8a51287127505aa4bc0789`.
- `host`: [Actual EFI Boot C/parser/entropy/cleanup instructions, two successful and six refused paths, two instruction controls; actual native DT/PE/early DRBG consumption followed by original 18-test POST and native registration; two missing/short seed refusals](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/814bd4943b279d91ae61ada33d4968cf749a48e7/reports/public/ios16-boot-entropy-kernel.json)
  Command: <code>.venv-gpu/bin/python scripts/check_boot_entropy_kernel.py --check-only</code>. Revision: `1b191cb58250d0705d8a51287127505aa4bc0789`.

## 镜像组装 {#packaging}

`host-verified`

### 硬件与依赖

- Locally built firmware, compiled hardware DTS and generated iPhone ADT.

### 配置

- Payload selects the firmware DarwinBoot loader and separate kernel; four GiB owned-memory request.

### 操作步骤

- Validate container fields and embedded module GUIDs; generate and read back the ADT.
- PATH="$PWD/.venv-uefi/bin:$PATH" scripts/package.sh --check --no-deps --os 16 --out build/unixnu -j 4

### 开发经验

- The native ARM64 kernel, iPhone ADT, 160 MiB FAT and Android v4 container build and pass binary readback. DarwinBoot accepts the actual native kernel.
- A separate full entropy firmware and Android v4 development container now embed the exact tested new loader and byte-identical preserved 160 MiB crypto FAT/packed Data. Full shim/gzip/FD/DTB/FAT/header readback passes; old images are unchanged.
- The isolated fresh-GPU container replaces only the new FAT kernel and menu title, preserving all other file bytes and boot arguments. The exact prior entropy FD/EFI runs its model paths against the new kernel and feeds actual native seed consumption, original 18-test POST and native consumers.
- The standard package script matches the official template. Its check resolves 61 iPhone patches. The isolated logger payload contains the Tools action, and BootShim/FD/DTB/FAT pass Android v4 readback.

### 完成条件

- Local firmware/payload pairing carries exact component identities and correct sizes and hashes.

### 当前范围

- No release or bootable iOS image is claimed. No phone operation is authorized in this phase.

### 下一步

- Retain the source-only development payload; complete original-component, authenticated-root and peripheral code before an iOS payload.

### 证据

- `host`: [The native ARM64 kernel, iPhone ADT, 160 MiB FAT and Android v4 container build and pass binary readback. DarwinBoot accepts the actual native kernel.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/814bd4943b279d91ae61ada33d4968cf749a48e7/reports/public/native-payload.json)
  Command: <code>.venv-uefi/bin/python scripts/build_local_payload.py</code>. Revision: `6b3d90b79e191e08171bfedd3980234a7e49d340`.
- `host`: [Exact fresh-entropy EFI read back from the new FD, model-tested and packaged into a separate Android v4 container with the preserved FAT; no phone or full userspace/root boot](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/814bd4943b279d91ae61ada33d4968cf749a48e7/reports/public/ios16-entropy-payload.json)
  Command: <code>.venv-gpu/bin/python scripts/build_entropy_payload.py --check-only</code>. Revision: `6b3d90b79e191e08171bfedd3980234a7e49d340`.
- `host`: [Separate 170557440-byte Android v4 container, 90-object kernel, unchanged entropy FD/EFI and full FAT/container readback; actual EFI/native seed/original 18-test POST chain. No full kernel/userspace or phone boot.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/814bd4943b279d91ae61ada33d4968cf749a48e7/reports/public/ios16-fresh-gpu-payload.json)
  Command: <code>.venv-gpu/bin/python scripts/build_fresh_gpu_payload.py --check-only</code>. Revision: `6b3d90b79e191e08171bfedd3980234a7e49d340`.
- `host`: [Separate mapped-resource/wait kernel and container, preserved entropy FD/EFI, actual EFI/native-seed/original 18-test POST chain and full FAT/Android v4 readback. No full kernel/userspace or phone boot.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/814bd4943b279d91ae61ada33d4968cf749a48e7/reports/public/ios16-mapped-lease-payload.json)
  Command: <code>.venv-gpu/bin/python scripts/build_mapped_lease_payload.py --check-only</code>. Revision: `6b3d90b79e191e08171bfedd3980234a7e49d340`.

## 诊断 {#diagnostics}

`host-verified`

组件: `ArmDTPlatform`.

### 硬件与依赖

- Pinned source platform expert, source kernel crypto provider and local build logs.

### 配置

- Verbose kernel arguments and source-only first stage; complete source POST retained; original component crypto lifecycle remains unqualified.
- Tools &gt; Advanced Logger exports the DXE log as OneSend QR frames before kernel handoff.

### 操作步骤

- Run profile/native staging regressions and the source 4 KiB policy test; inspect failures before broadening scope.

### 开发经验

- The source kernel and selected archives compile/link, actual DarwinBoot parsing and POST field checks pass; IIG default outputs pass 213 regressions. Strict static prelink, all 28,197 pointer readbacks and two exact AMFI/sandbox entry/code readbacks pass; ABI/loadability/runtime flags remain false.
- The exporter and log producer compile and are present in firmware; the Tools action is read back from a separate FAT payload. A device capture remains the next firmware checkpoint.

### 完成条件

- Build and runtime failures have reproducible inputs and bounded diagnostic records.

### 当前范围

- No device logs or runtime observations have been collected in this task.

### 下一步

- Complete original-component ABI, register-dataflow, crypto lifecycle and runtime security-initialization audits.

### 证据

- `host`: [The source kernel and selected archives compile/link, actual DarwinBoot parsing and POST field checks pass; IIG default outputs pass 213 regressions. Strict static prelink, all 28,197 pointer readbacks and two exact AMFI/sandbox entry/code readbacks pass; ABI/loadability/runtime flags remain false.](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/814bd4943b279d91ae61ada33d4968cf749a48e7/reports/public/native-kernel.json)
  Command: <code>.venv-uefi/bin/python scripts/validate_kernel_artifacts.py</code>. Revision: `3fa5ff5f409398c0555a9561d6437ce5d4c3b3b7`.

## cellular {#cellular}

`planned`

### 硬件与依赖

- CPH2653 modem firmware, SMEM/GLINK resources and factory NV/EFS inputs.

### 配置

- No cellular driver is selected.

### 操作步骤

- Identify target modem transport and firmware memory before adapting QcomBaseband interfaces to iOS 16.

### 开发经验

- The current official porting guide tracks cellular separately on boards with a modem.

### 完成条件

- Modem boot, QMI, SIM, registration and data each pass their own checks.

### 当前范围

- Modem startup and iPhone CommCenter integration are pending.

### 下一步

- Inventory the modem resources from existing CPH2653 captures and firmware sources.

### 证据

按下一步操作收集证据。

</div>
