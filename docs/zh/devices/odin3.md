# AYN Odin 3 \(Dragonwing Q8, SM8750\), 16 GiB

[darkplace/UniXNU-Odin3](https://github.com/darkplace/UniXNU-Odin3)

<div v-pre>

AYN Odin 3 on the Pagani SM8750 base: iPadOS 17.7.11 \(21H461\) boots from a microSD ESP to the SpringBoard lock screen with eight CPUs online. Root runs on verified read-only SD windows; Data persists on a dedicated partition. Display is a GOP handover with software rotation; touch identity is implemented but input is not demonstrated; GPU, Wi-Fi, audio and brightness are out of scope.

源记录: [porting.toml](https://github.com/darkplace/UniXNU-Odin3/blob/6d58c09d1529fb22dba8e3d6f74d8d4c7f9f8306/porting.toml), `6d58c09d1529fb22dba8e3d6f74d8d4c7f9f8306`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `implemented` |
| [固件与启动](#firmware) | `implemented` |
| [CPU 与中断](#cpu) | `implemented` |
| [内存与 DMA](#memory) | `implemented` |
| [存储与根卷](#storage) | `implemented` |
| [显示](#display) | `implemented` |
| [输入](#input) | `implemented` |
| [GPU](#gpu) | `planned` |
| [网络](#network) | `planned` |
| [音频](#audio) | `planned` |
| [电源](#power) | `implemented` |
| [镜像组装](#packaging) | `implemented` |
| [诊断](#diagnostics) | `implemented` |

## 配置 {#configuration}

`implemented`

组件: `NativePrelink`, `Sm8750Platform`.

### 硬件与依赖

- unixnu.lock pins xnu d8b80295118ef25ac3a784134bcf95cd8e88109f, Pagani drivers 14f50fce9778a8bb19ec6b0b7dc199863526c996 and sm8750 b79d675e522383c29131ccda8529fda45e1f2852. The 21H461 kernelcache pin stays in board.toml. The apps SMMU is ARM MMU-500 and is not enabled.

### 配置

- Odin identity, eight CPUs with the Pagani SMP path \(sheng-smp, sheng-smp-gic, armcpu-self-ipi\), 4 GiB owned RAM; no inherited PKX110 peripheral arguments.

### 操作步骤

- Resolve status; defconfig odin3\_defconfig; build kernel, payload and local medium; no device commands.

### 开发经验

- The old OnePlus README and porting record have been retained as explicitly named reference files, rather than reusing their hardware verification levels.

### 完成条件

- Resolved profile and final reports agree with the built inputs.

### 当前范围

- Local module overrides are intentional and are not upstream pin qualification.

### 下一步

- Keep each candidate in its own report and SHA. Do not fold the fan, row-layout, cluster or resume-0 branches into this area's status.

### 证据

- `source`: [Complete selection and kernelcache pin.](https://github.com/darkplace/UniXNU-Odin3/blob/6d58c09d1529fb22dba8e3d6f74d8d4c7f9f8306/board.toml)

## 固件与启动 {#firmware}

`implemented`

组件: `PaganiDarwinBoot`.

### 硬件与依赖

- Existing OpenABL v1.2; BLS entry with ODIN3.DTB splash reservation.

### 配置

- payload.loader=driver; no firmware build or ABL update.

### 操作步骤

- Preserve the existing GOP and BLS handoff; inspect local images before a separately authorized boot.

### 开发经验

- The user's diagnostic page remains visible with changing timer/poll counters; firmware scanout is already working.

### 完成条件

- Same loader handoff and stable framebuffer in the new boot.

### 当前范围

- Firmware is the existing OpenABL. There is no Mu FD, no fastboot boot and no Advanced Logger QR exporter, because the ABL is not replaced.

### 下一步

- Keep the OpenABL GOP and the BLS splash DTB. Do not add a firmware log exporter. The kernel card log is XNSDLOG1, read by scripts/h1/sd-inspect.sh.

### 证据

- `source`: [Odin boot route and evidence boundary; project reports carry the original user transcript.](https://github.com/darkplace/UniXNU-Odin3/blob/6d58c09d1529fb22dba8e3d6f74d8d4c7f9f8306/README.md)

## CPU 与中断 {#cpu}

`implemented`

组件: `PaganiArmCpu`, `PaganiArmDTPlatform`.

### 硬件与依赖

- SM8750 GIC and 19.2 MHz architectural timer; eight-CPU DTS with PSCI SMC.

### 配置

- Native architectural timer and PAN enabled; secondary CPUs started through the Pagani SMP path. Main uses 6E/2P tags and \_\_ARM\_AMP\_\_/Edge; identity-only touch profile retains the prior no-Edge configuration.

### 操作步骤

- Retain the previously booted platform settings.

### 开发经验

- Timer/poll progress is observed; it is not proof of userland progress.

### 完成条件

- Kernel continues through root and exec without a new exception.

### 当前范围

- SMP was previously observed; Edge scheduling, per-domain load and UI affinity are not hardware-qualified. Recount is accounting, not DVFS.

### 下一步

- On the host, record that the touch3 ADT has no cluster-type and that the 6E/2P candidate is unmerged. Do not change preferred-cluster policy.

### 证据

- `source`: [Unchanged CPU/PAN policy.](https://github.com/darkplace/UniXNU-Odin3/blob/6d58c09d1529fb22dba8e3d6f74d8d4c7f9f8306/configs/odin3_defconfig)

## 内存与 DMA {#memory}

`implemented`

### 硬件与依赖

- Measured Odin RAM range and 4 GiB contiguous owned window \(8 GiB: logo without page on hardware, cause not determined; see docs/builds/odin3-swap-geometry-20261029.md\).

### 配置

- payload.adt.owned\_memory\_size=0x100000000.

### 操作步骤

- Keep GOP allocation outside ordinary RAM ownership and validate actual console geometry.

### 开发经验

- No DMA presentation path is enabled; CPU copy validates source/destination bounds.
- The card ADT 624d0938 \(14188 B, image d3-fan3-uhs, same hash as p1 on 2026-10-29\) carries dram-base 0x80000000, dram-size 0x3E9A5D000 and darwinboot-memory-size 0x100000000. Its /arm-io children are intc and sdhci only. The apps SMMU is ARM MMU-500 at 0x15000000 in the AYN DTSI and is left disabled; ArmSmmu4K is not selected.

### 完成条件

- No framebuffer overrun and accepted geometry in runtime display diagnostics.

### 当前范围

- The owned window stays 4 GiB. The 15.65 GiB DDR node is not the window XNU owns. No UEFI ConventionalMemory map was read, so carveouts stay unresolved. The apps SMMU is not enabled and is not programmed.

### 下一步

- Do not enable iommu@15000000 and do not change owned\_memory\_size. Read a UEFI ConventionalMemory map from a log already captured before resizing the window.

### 证据

- `source`: [PE\_current\_console and memory-bound checks.](https://github.com/darkplace/UniXNU-Odin3/blob/6d58c09d1529fb22dba8e3d6f74d8d4c7f9f8306/modules/Pagani/drivers/NativeMobileDisplay/NativeLegacyDisplay.cpp)

## 存储与根卷 {#storage}

`implemented`

组件: `SoftwareAES`, `PaganiVerifiedRoot`, `NativeVirtioBlock`, `NativeRamBlock`.

### 硬件与依赖

- Existing signed OS/SystemOS policy windows on microSD; FD326389 Data seed.

### 配置

- OdinSd occupies the NativeUfs link slot, SDCC2 only. PackedRAMDisk Data is volatile by default. Experimental sheng-data-persist=1/2 requires a unique GUID-pinned UniXNUData partition and both GPT copies; no Data candidate is enabled here.

### 操作步骤

- Retain the previously booted SDHCI fixes and policies; perform only host readback of local image files.

### 开发经验

- The user observed SystemOS authorization and Data mount. The SD store adapter now passes actual-code and overlay host tests; writes wait for card programming and readback, without claiming UFS FUA or power-loss atomicity. Root snapshot serialization and software completion deadlines are guarded. CMD6 high-speed selection uses byte16, not the byte13 support bitmap.

### 完成条件

- Same root/Data milestones without integrity or command errors.

### 当前范围

- No UFS; persistent Data not activated or hardware-tested. Partition provisioning, durability, speed and boot-time savings remain unmeasured. Shared-cache authorization hashes remain per boot.

### 下一步

- Boot the same p1 again. A generation-1 header with the 84027 present bits still set means Data resumed. Do not rewrite p1 and do not set sheng-data-reset.

### 证据

- `source`: [PIO SD provider and bounded verified-root windows, not a UFS driver.](https://github.com/darkplace/UniXNU-Odin3/blob/6d58c09d1529fb22dba8e3d6f74d8d4c7f9f8306/drivers/OdinSd/OdinSd.cpp)

## 显示 {#display}

`implemented`

组件: `NativeMobileDisplay`, `NativeKeyStoreEvents`, `Stage7Probe`, `PaganiPanel`.

### 硬件与依赖

- Odin ICNA3520 already scanning the firmware GOP; original 21H461 Legacy ABI.

### 配置

- NativeLegacyDisplay CPU backend and software 60 Hz notification; odin-gop-only=1 blocks all PKX110 peripheral startup. AppleKeyStore stand-in enabled \(offline-key-events=1, sheng-aks=1\) as in the Pagani reference. Panel is portrait 1080x1920; sheng-fb-rotate=1 shows the system a 1920x1080 display and turns each frame 90 degrees to the left into the GOP \(display-rotation stays 0\).

### 操作步骤

- Run console and display timer tests; qualify compiled 358-slot ABI and original bindings; build kernel/payload/medium; observe one boot later.

### 开发经验

- DISPLAY 0 was an empty diagnostic stage string, not a hardware enumeration result. The previous profile omitted the system display archive and its init caller. IOSurface matching now uses service class with a fallback, not one IOName.
- Hardware \(medium 5d5ffd71, display-rotation=90\): every swap rejected with reason 3 \(layer-0 rectangles or size words differ from the GOP size\); what the compositor sent was not recorded. The 21H461 kernelcache never reads display-rotation; only libMobileGestalt does. See docs/builds/odin3-swap-geometry-20261029.md.

### 完成条件

- Display publication, valid user client/swap, a real system frame and correct handoff.

### 当前范围

- First lock-screen frame observed; distortion and stability unresolved. No physical DSI/panel/reset/brightness programming; no GPU or measured vblank. Embedded Pagani peripheral objects are compile-only.

### 下一步

- Keep odin-gop-only=1. Brightness transport is undetermined, so do not add a backlight driver or a calibration boot. Image 101bb1d1 is the reserved display checkpoint and is not part of this action.

### 证据

- `source`: [Hard GOP-only startup guard and class-based IOSurface wait.](https://github.com/darkplace/UniXNU-Odin3/blob/6d58c09d1529fb22dba8e3d6f74d8d4c7f9f8306/modules/Pagani/drivers/Stage7Probe/Stage7Probe.cpp)
- `host`: [Rotation of a BGRA frame in both directions, tile edges and refusals under ASan/UBSan.](https://github.com/darkplace/UniXNU-Odin3/blob/6d58c09d1529fb22dba8e3d6f74d8d4c7f9f8306/modules/Pagani/drivers/NativeMobileDisplay/Test/request-state.c)
  Command: <code>ASan/UBSan host test of Test/request-state.c, recorded in docs/builds/odin3-swap-geometry-20261029.md</code>. Revision: `8596d94a9bd296c0ca68f5150e2f539d531fb196`.

## 输入 {#input}

`implemented`

组件: `PaganiInput`, `QcomGeniSpi`.

### 硬件与依赖

- AYN d0bd123 Odin DTS: generic ft5426/I2C4 0x38, GPIO161 reset/162 IRQ. ROCKNIX/distribution 2a01f59e3329fd14923ccbe6f703cd84f0367196 confirms the same bus/pins/rails/extent. OTA overlay: FT3519 type 0x35190489, 10 contacts, 1080x1920; all 11 DTB variants confirm GENI 0xa90000, SPI357, QUP1 stream 0xa3.

### 配置

- Independent odin-touch=0..4 \(absent/off by default\); odin-gop-only continues to block every PKX110 provider. Stage3 reads ID/FW/mode before contact reads. Stage4 requires odin-touch-id equal to the measured register pair; no guessed default ID. Retained FIFO I2C only; no flash updater, power/reset writes or SMMU changes.

### 操作步骤

- Run host touch/FIFO ASan/UBSan tests and exact 207-slot IOHIDDevice object comparison, compile/link/prelink; later authorize stage3 separately, measure the ID, and only then qualify scanning/HID/UI.

### 开发经验

- OnePlus S3910/GPIO/RPMh constants are not Odin inputs.
- OdinTouch candidate compiles/links/prelinks; 10-contact coherent decoder, inverse display rotation, normalized HID ranges and explicit releases pass host tests. Logical /arm-io/touch node avoids inventing a &gt;16MiB GENI address; GPIO162 is not encoded as a GIC IRQ. See project docs/builds/odin3-touch-20261029.md.

### 完成条件

- Future genuine Odin input reports and UI response.

### 当前范围

- Hardware input unqualified; no known measured A3/9F identity, cold power/reset or GPI/DMA adoption. No board firmware upgrade. Physical buttons not implemented. The candidate refuses incompatible retained state rather than guessing.

### 下一步

- The missing input is the measured FT3519 ID/FW pair. No host source has it. Leave odin-touch off and do not guess A3/9F.

### 证据

- `host`: [Real decoder/transport core under ASan/UBSan: rotations, 10 IDs, release, bounds, repeated START, tails, refusal and timeout/poison PASS.](https://github.com/darkplace/UniXNU-Odin3/blob/6d58c09d1529fb22dba8e3d6f74d8d4c7f9f8306/modules/Pagani/drivers/Stage7Probe/Test/touch.c)
  Command: <code>python3 modules/Pagani/drivers/Stage7Probe/Test/test-touch.py</code>. Revision: `93757bb5027fe4888b382c42ed5318b33acce603`.

## GPU {#gpu}

`planned`

### 硬件与依赖

- SM8750 GPU is an Adreno 830 \(Gen8 generation 1, chip id 0x44050000/0x44050001 per vendor DT\), not the documented SM8550/A740 backend. Pinned firmware gen80000\_&\#123;gmu,sqe,aqe&\#125; and sm8750/gen80000\_zap.mbn, Odin vendor DT evidence and derived A830 init tables: docs/builds/odin3-adreno830-20261029.md.

### 配置

- XNU\_NATIVE\_ADRENO disabled; CPU display path only. odin-gpu-survey=0 by default; value 1 runs G1 read-only SCM availability/GCC/gated GPUCC before display handoff.

### 操作步骤

- Do not enable GPU presentation before CPU swaps are validated.

### 开发经验

- A software refresh request is not hardware acceleration or measured refresh.
- G1 has no MMIO writes or CX\_MISC/GX/GMU/CP/SMMU accesses. A synchronous framebuffer checkpoint must succeed before each attempt; otherwise the survey cancels. Host ASan/UBSan ladder and renderer tests pass; hardware not determined. See docs/builds/odin3-adreno830-g1-20261029.md in the project.

### 完成条件

- Future independently qualified GPU execution and presentation.

### 当前范围

- GPU acceleration not determined. Host-side inputs only: no GPU register has been read on the Odin; EL1 access to SCM/TZ, GDSC/clocks and the GPU SMMU is not demonstrated.

### 下一步

- Keep the CPU backend. Do not open the GPU until display has a recorded result and touch has a measured ID.

### 证据

- `source`: [GPU disabled.](https://github.com/darkplace/UniXNU-Odin3/blob/6d58c09d1529fb22dba8e3d6f74d8d4c7f9f8306/configs/odin3_defconfig)

## 网络 {#network}

`planned`

### 硬件与依赖

- Odin network hardware/firmware/OS provider not qualified.

### 配置

- No provider selected.

### 操作步骤

- Separate subsystem bring-up after storage/display/input.

### 开发经验

- No result in this task.

### 完成条件

- Future association and packet transfer.

### 当前范围

- Not implemented.

### 下一步

- Keep disabled. drivers.md places the network after display and input.

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`planned`

### 硬件与依赖

- DSP/codec/clock/firmware ownership not qualified.

### 配置

- No provider selected.

### 操作步骤

- Separate subsystem bring-up.

### 开发经验

- No result in this task.

### 完成条件

- Future playback and capture.

### 当前范围

- Not implemented.

### 下一步

- Keep disabled. drivers.md places audio after display and input.

### 证据

按下一步操作收集证据。

## 电源 {#power}

`implemented`

组件: `ShengPlatformPower`.

### 硬件与依赖

- Original PMGR nub required by AMFI; firmware owns physical display state.

### 配置

- sheng-pmgr=2; sleep-disabled=1; no physical display PM provider.

### 操作步骤

- Keep the previously booted PMGR integration unchanged.

### 开发经验

- Logical framebuffer PM controls scheduling only, not rails or physical blanking.

### 完成条件

- Same AMFI progress, no new physical power transition.

### 当前范围

- No battery, DVFS, suspend or brightness qualification.

### 下一步

- Keep physical controls disabled. Battery, DVFS and brightness stay unqualified.

### 证据

- `source`: [Existing bare-metal PMGR settings retained.](https://github.com/darkplace/UniXNU-Odin3/blob/6d58c09d1529fb22dba8e3d6f74d8d4c7f9f8306/board.toml)

## 镜像组装 {#packaging}

`implemented`

### 硬件与依赖

- Unchanged Apple IPSW/kernelcache/trust caches/Data seed; source-only changes tracked.

### 配置

- Driver loader, PackedRAMDisk, unchanged root policies.

### 操作步骤

- Build kernel; payload; local ESP/disk; read back hashes. Project report records actual outputs.

### 开发经验

- Worktree builds use explicit IDRAGON\_PROJECT policy inputs and local LLVM bridge; no package installation is needed.
- The project's host disk-image builder previously let FAT exceed the 400 MiB GPT partition. A negative readback test reproduces it; explicit KiB filesystem size now keeps the FAT within the GPT extent. No physical card was accessed.

### 完成条件

- Successful compile/link/prelink and matching local-image manifests.

### 当前范围

- A built image is not a boot qualification.

### 下一步

- Record image hashes in the build report. Do not commit Apple binaries.

### 证据

- `source`: [Actual XNU ABI preserved; only the local compiler's final-class warning disabled.](https://github.com/darkplace/UniXNU-Odin3/blob/6d58c09d1529fb22dba8e3d6f74d8d4c7f9f8306/scripts/build-stage7-driver.py)

## 诊断 {#diagnostics}

`implemented`

组件: `BootProgress`.

### 硬件与依赖

- Framebuffer observation only; no UART/USB debug transport assumed.

### 配置

- Continuous observer, boot-diag-resume=10, eight pid-1 SVC rows and bounded tails.

### 操作步骤

- Run real renderer under ASan/UBSan and kernel source contracts; build; photograph at 30/60/120 seconds in one later boot.

### 开发经验

- Exec shadow retirement is separated from live exit; kern.initproc\_spawned is a distinct main acknowledgment. Unhandled EL0 aborts and current process-name mask are retained; pid-1 stdout/stderr requests are bounded and do not alter writes.

### 完成条件

- The next observation distinguishes before-EL0, dyld/userland, main, service startup and frame handoff.

### 当前范围

- Snapshots/log tails are lossy and advisory. Pending Mach receive is not by itself a deadlock; IRQ PC is not process-attributed. No persistent log format change or new storage writer.

### 下一步

- Decode signed SVC numbers against the pinned XNU tables on the host. The XNSDLOG1 header already exists; do not add another storage writer.

### 证据

- `source`: [Read-only observation hooks preserve original critical-exit and syscall control flow.](https://github.com/darkplace/UniXNU-Odin3/blob/6d58c09d1529fb22dba8e3d6f74d8d4c7f9f8306/patches/xnu/odin3-userland-observer.patch)

</div>
