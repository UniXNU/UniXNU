# Xiaomi Pad 6S Pro \(sheng\): macOS 26.5 port with its own kernel and drivers; the full system reaches the desktop with CPU rendering \(mataht\)

[mataht/sheng-macos-link-lab](https://github.com/mataht/sheng-macos-link-lab)

<div v-pre>

Xiaomi Pad 6S Pro \(sheng, CN 16 GB / 1 TB\) running macOS 26.5 \(25F71\) from RAM-only fastboot boots. The full system reaches the CPU-rendered desktop, and with the Metal plug-in stack \(WindowServer -&gt; Metal plug-in -&gt; metal2vulkan -&gt; Turnip -&gt; Adreno 740 kernel driver\) it has for the first time displayed a GPU-composited interface on the tablet \(wallpaper, menu bar and post-login Setup Assistant pages, with working touch\) at about 6 frames per second. GPU acceleration is not yet usable: most 50 ms display waits and 1517 of 2274 kernel fence waits time out, plug-in boots are intermittently slow for undetermined reasons, and per-frame display copy takes 0.1 to 0.4 seconds over the Device-mapped framebuffer \(\~79 MiB/s write\). Wi-Fi has run through stages 4 and 5 \(stage 5 outcome unknown; no wireless stack behind it\), keyboard cover stage 3 L12B voltage vote did not receive completion, and Bluetooth, USB, audio, battery reporting, brightness control, sleep and persistent disk writes do not work.

Source record: [porting.toml](https://github.com/mataht/sheng-macos-link-lab/blob/be7c6c4b8684492870a95d316e8fac86db4cb0a1/porting.toml), `be7c6c4b8684492870a95d316e8fac86db4cb0a1`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `host-verified` |
| [Firmware and boot](#firmware) | `device-verified` |
| [CPU and interrupts](#cpu) | `device-verified` |
| [Memory and DMA](#memory) | `device-verified` |
| [Storage and root](#storage) | `device-verified` |
| [Display](#display) | `device-verified` |
| [Input](#input) | `device-verified` |
| [GPU](#gpu) | `implemented` |
| [Network](#network) | `implemented` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `implemented` |
| [Image assembly](#packaging) | `host-verified` |
| [Diagnostics](#diagnostics) | `device-verified` |
| [usb](#usb) | `implemented` |
| [userspace](#userspace) | `device-verified` |

## Configuration {#configuration}

`host-verified`

### Hardware and dependencies

- Pinned upstream sources in sources.lock.json \(UniXNU, UniXNU-sheng, uefi-sheng, Apple's open-source XNU 12377.121.6 and companion libraries\) and the paired macOS 26.5 \(25F71\) kernel debug kit, used by CI for headers and signature checks.

### Configuration

- Kernel configuration DEVELOPMENT ARM64 with the SHENG board; XNU patches in platform/sheng/macos26/patches and platform/sheng/macos26/pac, applied in numeric order; driver switches are boot arguments \(sheng-gpu-power, sheng-wifi, sheng-kbd, sheng-usb and so on\), all default off.

### Procedure

- Build in CI \(the builds run in a private repository; the workflow file hw-sheng-cn-1tb.yml in this repository shows the steps, and Actions are disabled here\): scripts/build\_macos26\_xnu.py --link-kernel with the --build-\* switches of the drivers to include.
- Assemble the kernel collection locally; assembly uses Apple kernel extensions and its output is not published.

### Development findings

- CI compiles and links with the Apple toolchain on an xcode-27 runner; -Werror failures in earlier runs were fixed on the same branch \(see docs/ci.md\).
- CI artifacts are kept for seven days; the build.json of each run records the SHA-256 of every output.
- A kernel can also be built on a Mac with Xcode 27.2 \(SDK 27.2\) by the same steps; the SDK check of the build script also accepts 27.2. Against a CI build of the same source the build records have the same keys and differ only in toolchain versions, output identities and absolute paths or parallelism, but object files and the kernel are not byte-identical. A Mac-built kernel counts as a new kernel and passes its own gates.

### Completion criteria

- Every selected driver compiles and links, the ABI audits pass \(vtable slot counts, pointer-authentication metadata, no weak imports\) and the artifact digests match the GitHub API.

### Current limits

- CI does not run the kernel. It proves compile, link and static audits only. This repository is not a UniXNU device repository and does not build with the unixnu tool.

### Next action

- Keep one CI run per integrated head and record its digests in docs/ci.md.

### Evidence

- `host`: [Run 42576253178 succeeded: kernel and the eight merged driver branches compile and link, ABI audits pass.](https://github.com/mataht/sheng-macos-link-lab/blob/milestone-desktop-20261109/docs/ci.md)
  Command: <code>GitHub Actions: CN 1 TB sheng hardware candidate build</code>. Revision: `36e11087791ca3b68505ee19c1f8602d7713039d`.

## Firmware and boot {#firmware}

`device-verified`

### Hardware and dependencies

- uefi-sheng and UniXNU-sheng at the commits pinned in sources.lock.json, plus this repository's patch series; the vendor firmware archive named by the pinned UniXNU-sheng, which is downloaded on the build machine and not stored here.

### Configuration

- Boot image: Android boot container with the UEFI firmware and a FAT payload volume holding the UniXNU configuration, the kernel, the device tree and the trust cache; the loader is DarwinBoot. Boot arguments \(cpus=8, driver stages\) come from the packager.

### Procedure

- Build the firmware with scripts/build\_firmware.py, package the kernel and device tree with scripts/package\_macos26\_ufs.py, then run \`fastboot boot\` once with the device owner's approval. Nothing is flashed; a restart returns to Android.

### Development findings

- The bootloader of the CN OS3.0.306 unit accepts the self-built container and the firmware shows the UniXNU menu \(first seen 2026-11-06\).
- The bootloader leaves the display lit and a framebuffer in memory, which the kernel display driver reuses.

### Completion criteria

- The firmware reaches the UniXNU menu, DarwinBoot loads the kernel with the 16 GB memory map, and the framebuffer and reservations are preserved.

### Current limits

- Only the CN OS3.0.306 unit has been tested. Other vendor firmware versions are untested.

### Next action

- None until a second unit with a different firmware version is available.

### Evidence

- `device`: [UEFI and DarwinBoot loaded the kernel built from this revision; the system reached the desktop about two minutes after the command \(2026-11-09\). Nothing was flashed.](https://github.com/mataht/sheng-macos-link-lab/blob/milestone-desktop-20261109/docs/status.md)
  Command: <code>fastboot boot sheng-macos26-kernel.img</code>. Revision: `36e11087791ca3b68505ee19c1f8602d7713039d`.

## CPU and interrupts {#cpu}

`device-verified`

### Hardware and dependencies

- Eight cores \(three Cortex-A510, four A715, one X3\) brought up with PSCI; inter-processor interrupts through SPIs; CPU frequency registers read from the performance domains.

### Configuration

- Boot arguments cpus=8, sheng-smp=1, armcpu-spi-ipi=1; sheng-cpufreq=1 enables the read-only frequency reader.

### Procedure

- Boot with the packager's 8-CPU configuration; with sheng-cpufreq=1 the reader prints a CPUFREQ row every 5 seconds for 120 seconds.

### Development findings

- All eight cores came online on the tablet on 2026-11-07 \(cpu\_start 0 to 7\), on an earlier build of this repository.
- The bootloader leaves the clusters near the top of their ranges: 1670 MHz \(A510\), 2707 MHz \(A715\), 2956 MHz \(X3\), including during slow Metal plug-in boots, so CPU throttling is ruled out.
- This CPU reports cache geometry in the 64-bit CCIDX format of CCSIDR; XNU's whole-cache set/way shortcut parses the old format and is effectively a no-op here, so display and GPU code clean caches by address.

### Completion criteria

- Every enabled core reaches its entry checkpoint; timers and inter-processor interrupts work on each core.

### Current limits

- Inter-processor interrupt correctness and stability under sustained load are not established.

### Next action

- Evaluate whether any L3 or DDR vote needs raising after framebuffer write-combined mapping is tested.

### Evidence

- `device`: [Rows identical from 2 s to 100 s: three clusters at 1670, 2707 and 2956 MHz \(2026-11-08\).](https://github.com/mataht/sheng-macos-link-lab/blob/96ac3a9e43a4cc80ed1c3ab7bff78a315269bb39/platform/sheng/macos26/power/native_cpufreq.cpp)
  Command: <code>fastboot boot sheng-macos26-kernel.img (sheng-cpufreq=1)</code>. Revision: `96ac3a9e43a4cc80ed1c3ab7bff78a315269bb39`.

## Memory and DMA {#memory}

`device-verified`

### Hardware and dependencies

- Two DRAM windows \(0x80000000 to 0xFFFFFFFF and 0x880000000 to 0xBFFFFFFFF\) on the 16 GB unit; macOS uses 16 KiB pages.

### Configuration

- Memory map patch for the CN 16 GB unit in the UniXNU-sheng series \(0009\); 16 KiB page size in the kernel and the Adreno code; sheng-memperf=1 enables the read-only L3/RPMh report.

### Procedure

- Boot the packaged kernel; the packager checks the memory map against the unit's layout.

### Development findings

- The full system runs with the 16 KiB-page kernel and this memory map.
- The NativeMemPerf benchmark on the tablet \(boot 39\) measured \(MiB/s\): cached write \~11236, read \~10637; Device write \~79, read \~141; write-combined write \~11275, read \~256.

### Completion criteria

- All handoff regions are accounted for and each DMA engine uses its allocated range with the documented cache policy.

### Current limits

- The framebuffer is currently mapped as Device memory \(\~79 MiB/s write\), so a full-screen write takes about 0.3 seconds; CPU-rendered surfaces are read at about 70 MB/s \(inferred to be mapped non-cacheable in the kernel\).

### Next action

- Switch the framebuffer mapping from Device to write-combined.

### Evidence

- `device`: [The full system ran on the tablet with this kernel and memory map; the NativeMemPerf stage-1 report read the command database \(2026-11-09\).](https://github.com/mataht/sheng-macos-link-lab/blob/milestone-desktop-20261109/docs/status.md)
  Command: <code>fastboot boot sheng-macos26-kernel.img</code>. Revision: `36e11087791ca3b68505ee19c1f8602d7713039d`.

## Storage and root {#storage}

`device-verified`

### Hardware and dependencies

- UFS controller with several LUNs; a new partition for macOS on LUN0; a small log partition; a system image supplied by the user \(this repository neither contains nor documents how it is made\).

### Configuration

- NativeUfs is a read-only driver that publishes only registered partition windows after checking the SHNGROOT header \(size and SHA-256\); writes are off by default. The system volume is selected by volume UUID with -nobsdmgroot; writes go to a volatile RAM overlay \(boot argument native-ufs-root-overlay-mib\).

### Procedure

- Create the partition and write the image only with the device owner's approval for each step; the packager refuses a package without matching install evidence. Boot with \`fastboot boot\`.

### Development findings

- The tablet reads its macOS partition through NativeUfs and runs the full system on it; persistent writes are implemented but disabled.
- Reading is slower than it needs to be; the read path is deliberately simple.

### Completion criteria

- The root volume mounts, the data volume mounts, and the system runs without disk writes.

### Current limits

- Persistent writes are not verified on the tablet. The UFS driver cannot be exercised in QEMU, so full-system QEMU evidence comes from a VirtIO build of the same kernel with only the storage driver replaced.

### Next action

- Enable and verify persistent writes with a separate approval; improve read throughput.

### Evidence

- `device`: [Root and data volumes mounted from UFS through NativeUfs with the RAM overlay; the system reached the desktop \(2026-11-09\).](https://github.com/mataht/sheng-macos-link-lab/blob/milestone-desktop-20261109/docs/status.md)
  Command: <code>fastboot boot sheng-macos26-kernel.img</code>. Revision: `36e11087791ca3b68505ee19c1f8602d7713039d`.

## Display {#display}

`device-verified`

### Hardware and dependencies

- Framebuffer left by the bootloader, 3048 x 2032 BGRA; panel size 262 x 175 mm; no GPU driver in use.

### Configuration

- NativeGOPDisplay presents the framebuffer as an IOMobileFramebuffer \(native-gop-display=1\). WindowServer is switched to CPU compositing and BGRA output by in-memory edits of a few pages of the shared cache, each checked by original bytes and page hash \(sheng-full-ui=1\). A software cursor is forced; sleep is disabled.

### Procedure

- Boot with native-gop-display=1 sheng-full-ui=1; optional native-gop-diag=1 draws a counter strip at the top left.

### Development findings

- The desktop shows wallpaper, widgets and windows; taps register.
- The new copy code supports copying only changed rows and cleaning caches by address \(both default-off options, enabled in the GPU packages\).
- Per-stage timing on the tablet shows 0.1 to 0.4 seconds per frame, spent mostly reading the surface, comparing with the previous frame and writing changed rows into the Device-mapped framebuffer \(\~79 MiB/s write, \~0.3 seconds for a full-screen change\). Reading CPU-rendered surfaces also runs at \~70 MB/s \(inferred non-cacheable mapping in the kernel\).

### Completion criteria

- The first frame is presented, the desktop is drawn and the pointer follows the finger.

### Current limits

- No backlight control; per-frame copy takes 0.1 to 0.4 seconds over the Device-mapped framebuffer.

### Next action

- Map the framebuffer as write-combined \(inferred to be much faster based on the \~11275 MiB/s benchmark\) and investigate the non-cacheable surface read path.

### Evidence

- `device`: [Desktop with wallpaper, widgets and system windows displayed about two minutes after the boot command; very laggy \(2026-11-09\).](https://github.com/mataht/sheng-macos-link-lab/blob/milestone-desktop-20261109/docs/status.md)
  Command: <code>fastboot boot sheng-macos26-kernel.img</code>. Revision: `36e11087791ca3b68505ee19c1f8602d7713039d`.
- `device`: [Recovery's language chooser showed one selection row after the changed-rows copy fix \(2026-11-08\).](https://github.com/mataht/sheng-macos-link-lab/blob/milestone-recovery-keys-20261108/docs/status.md)
  Command: <code>fastboot boot sheng-macos26-kernel.img</code>. Revision: `e2da63e11cc4bc039b7ea090b68a589dc16efecd`.

## Input {#input}

`device-verified`

### Hardware and dependencies

- Novatek NT36532E touch on a GENI SPI engine \(QUP1 SE4, GPIO 44 to 47, interrupt GPIO 25\), 20319 x 30479 raw range; power and volume keys on the PMIC \(SPMI\); the keyboard cover on GENI I2C with its own MCU.

### Configuration

- Touch follows UniXNU-sheng's host-computed route: the host downloads the touch firmware into the controller at each boot, reads the capacitance frames and computes a single absolute pointer \(sheng-touch=1..4\). The firmware is a vendor file read from the user's own device and injected into the device tree locally; it is not in this repository. Keys: native-button-keys=1 reports arrows, Tab and Return. Keyboard cover: sheng-kbd=1..5, default off.

### Procedure

- Boot with sheng-touch=4 for a working pointer; bring-up stages 1 to 3 are read-only or clock and pin only and were run in order with approval for each boot.

### Development findings

- The pointer follows the finger from the Apple-logo phase on; taps select rows in Recovery and work on the GPU-composited Setup Assistant pages.
- On the full system a stage-1 read of the keyboard cover shows regulators L6B, L12B and L13B off. Stage 2 \(clocks and engine identity, no rail, no bus traffic\) passed on the tablet. Stage 3 \(boot 28, first voltage vote via RPMh for L12B 1.8 V and L13B 3000 mV\) did not receive a completion signal for L12B within 50 ms and stopped by design \(L13B not voted, no I2C traffic\); 13 seconds later a kernel lock-wait timeout panic occurred \(same signature as an earlier boot without a keyboard driver, causal link not established\). Inferred cause of the missing completion: the command channel completion interrupt was not enabled before voting; a fix is written offline and not yet built or booted.

### Completion criteria

- Touch produces correct pointer coordinates and clicks; keys can drive Recovery; the cover types.

### Current limits

- Single finger only. The keyboard cover's stage 3 voltage vote did not complete, and stages 4 and 5 have never run. No interrupt line is used; the drivers poll.

### Next action

- Build and test the keyboard cover stage 3 completion-interrupt fix with approval.

### Evidence

- `device`: [Pointer followed the finger and taps selected rows in the language chooser \(2026-11-08\).](https://github.com/mataht/sheng-macos-link-lab/blob/milestone-touch-20261108/docs/status.md)
  Command: <code>fastboot boot sheng-macos26-kernel.img (sheng-touch=4)</code>. Revision: `f01a90598d66bb68d2fdb941065853c49c96d128`.
- `device`: [Volume keys moved the selection, power and Return advanced the language chooser \(2026-11-08\).](https://github.com/mataht/sheng-macos-link-lab/blob/milestone-recovery-keys-20261108/docs/status.md)
  Command: <code>fastboot boot sheng-macos26-kernel.img (native-button-keys=1)</code>. Revision: `e2da63e11cc4bc039b7ea090b68a589dc16efecd`.
- `device`: [Keyboard cover stage 2: clock vote, I2C engine identity registers read, regulators off, no bus traffic, no panic \(2026-11-10, video reading\).](https://github.com/mataht/sheng-macos-link-lab/blob/main/docs/status.md)
  Command: <code>fastboot boot sheng-macos26-kernel.img (sheng-kbd=2)</code>. Revision: `e5cd05044e6c9f2cb442da0d2c4444a270579994`.

## GPU {#gpu}

`implemented`

### Hardware and dependencies

- Adreno 740 \(a7xx\) with its GMU, SMMU and firmware \(firmware is read from a device tree node and is never stored here\); UniXNU's Adreno740 component; Mesa's Turnip driver with a Darwin backend; a Rust Metal-to-Vulkan bridge; a Metal plug-in loaded by WindowServer.

### Configuration

- Kernel: an IOAccelerator front end over UniXNU's Adreno kernel stack, 16 KiB pages, default off, sheng-gpu-power=1..9 \(1 is read-only\). User space: plug-in bundle \(Metal front end, bridge, Turnip\) delivered as a compressed device tree node in QEMU.

### Procedure

- Build with the --build-gpu switch \(kernel\) and the gpu-userland workflow \(plug-in\); boot with sheng-gpu-power=1 for the read-only stage. Higher stages power the GPU and need the device owner's approval.

### Development findings

- QEMU stage A: WindowServer loaded the plug-in, called its initialisation, opened the accelerator and the runtime answered that no device exists \(QEMU has no A740\).
- QEMU stage B \(fake A740 that executes nothing\): Turnip created a device, two submissions, the first frame \(800 x 600, no content\); WindowServer then exited with SIGABRT intermittently, cause unknown.
- Tablet, stages 1 to 9 without the Metal plug-in \(including control boot 39\): power domains, clocks, the GMU SMMU context and GMU firmware, GX power and heartbeat, TrustZone zap authentication \(three secure calls returning 0\) and the first GPU command and interrupt through the GPU's own SMMU context all succeeded \(with whole-page 16 KiB unmapping\); boot 39 reached the CPU-rendered desktop quickly.
- Tablet, GPU hang avoided \(sheng-gpu-wc=0\): an earlier hang-panic QR showed the command processor at the end of the first indirect buffer, the first buffer words reading as 0, and 16 dirty or stale write-combine cache lines \(inferred: buffer still in the CPU cache, not in DRAM\). Making client buffers cacheable with pre-submission cache maintenance eliminated the hang.
- Tablet, first GPU-composited UI with the Metal plug-in \(boot 38: WindowServer -&gt; Metal plug-in -&gt; metal2vulkan -&gt; Turnip -&gt; Adreno 740 kernel driver\): fast boot; the screen displayed the desktop wallpaper, menu bar \(Simplified Pinyin, Tue Nov 10\) and post-login Setup Assistant pages \(advancing from Auto Update to the network page with working touch\) at about 6 frames per second; all 64 sampled display points had content \(0 on earlier black-screen boots\). The 300 s diagnostic panic QR recorded 759 submissions, 758 completed, no GPU hang, 7 processes that opened the GPU \(inferred from truncated names: WindowServer, loginwindow, NotificationCenter, Setup Assistant, iconservicesagent\), and the IO-coherence probe passed.
- The plug-in contains metal2vulkan \(GPL-2.0-or-later or LGPL-3.0-or-later\); its build artifacts are not redistributed.

### Completion criteria

- WindowServer renders through the Adreno 740 with Metal; AIR shaders compile to Adreno code.

### Current limits

- GPU acceleration is still slow \(\~6 fps\) and not yet usable: most 50 ms display waits and 1517 of 2274 kernel fence waits time out; boots with the Metal plug-in are intermittently slow \(boots 21 and 33 slow, \~104 s to WindowServer takeover in boot 33 vs 22 to 33 s when fast in boots 23, 38 and 39; CPU clocks are normal and the slowdown starts after launchd before WindowServer; why boot 38 was fast and showed a picture is undetermined\).

### Next action

- Investigate the display and kernel fence wait timeouts and the intermittent slow boots with the Metal plug-in; verify the remaining QR diagnostic fields.

### Evidence

- `host`: [Turnip created a device on the fake A740 and a first frame was submitted; WindowServer exited intermittently afterwards.](https://github.com/mataht/sheng-macos-link-lab/blob/gpu-fake-a740-qemu-20261109/docs/status.md)
  Command: <code>QEMU aarch64 full-system boot of the CI kernel with sheng-gpu-fake=1</code>. Revision: `41091a32532775aed1457f9bc3f65a4864707204`.
- `device`: [Stage 1, a read-only snapshot, ran on the tablet without writes or rendering \(2026-11-09\).](https://github.com/mataht/sheng-macos-link-lab/blob/milestone-desktop-20261109/docs/status.md)
  Command: <code>fastboot boot sheng-macos26-kernel.img (sheng-gpu-power=1)</code>. Revision: `36e11087791ca3b68505ee19c1f8602d7713039d`.
- `device`: [Desktop reached without a panic; first GPU interrupt, accelerator published, 1023 of 1023 test dwords correct, read from a video of the screen \(2026-11-09 night\). The kernel has no complete full-system QEMU run.](https://github.com/mataht/sheng-macos-link-lab/blob/milestone-gpu-plugin-boot-20261109/docs/status.md)
  Command: <code>fastboot boot sheng-macos26-kernel.img (sheng-gpu-power=9, second integrated kernel)</code>. Revision: `e5cd05044e6c9f2cb442da0d2c4444a270579994`.
- `device`: [Plug-in installed, accelerator registered, WindowServer created the Turnip device, 107 client calls reached the driver, no fault, no panic; the whole screen stayed black with no pointer \(2026-11-09 night, read from a video\).](https://github.com/mataht/sheng-macos-link-lab/blob/milestone-gpu-plugin-boot-20261109/docs/status.md)
  Command: <code>fastboot boot sheng-macos26-kernel.img (sheng-gpu-power=9 sheng-gpu-metal=1 sheng-full-ui=2, second integrated kernel)</code>. Revision: `e5cd05044e6c9f2cb442da0d2c4444a270579994`.
- `device`: [First GPU-composited UI on the tablet \(boot 38\): wallpaper, menu bar and post-login Setup Assistant pages displayed with working touch at about 6 fps; all 64 sampled display points had content; 300 s diagnostic QR recorded 759 submissions, 758 completed, no GPU hang, IO-coherence probe passed; most 50 ms display waits and 1517 of 2274 kernel fence waits timed out \(2026-11-10, video, photo and diagnostic QR\).](https://github.com/mataht/sheng-macos-link-lab/blob/main/docs/status.md)
  Command: <code>fastboot boot sheng-macos26-kernel.img (sheng-gpu-power=9 sheng-gpu-metal=1 sheng-full-ui=2)</code>. Revision: `e5cd05044e6c9f2cb442da0d2c4444a270579994`.

## Network {#network}

`implemented`

### Hardware and dependencies

- Wi-Fi and Bluetooth chip \(WCN7850 family\) on PCIe0 with its power rails, the sleep-clock pin and the MHI interface; vendor firmware is never stored here.

### Configuration

- NativeWifi, default off: sheng-wifi=1 read-only snapshot, 2 power and PCIe link with endpoint identification, 3 BAR0 and MHI registers. The class is an Ethernet-style controller from IONetworkingFamily. RPMh TCS 0 is used.

### Procedure

- Boot with sheng-wifi=N for stage N; stages 2 and 3 power the chip and need approval for each boot.

### Development findings

- Stage 1 on the tablet: the PCIe0 power domain is collapsed with no clock votes; WLAN\_EN, BT\_EN and PERST\# read low; two of the chip's rails read off and three on at the pinned voltages; the sleep-clock pin is idle and owned by another execution environment.
- Stage 2 on the tablet: power, PCIe0 link and endpoint identification; the endpoint ID reads 17cb:1107 \(WCN7850\), the sleep clock goes from idle to driving and one chip rail from off to on.
- Stage 3 on the tablet: BAR0 \(2 MiB\) mapped, bus mastering on, the MHI register block and the BHI registers read without a panic; MHIVER reads 0xdeadbeef, meaning not established \(digits read from a video\).
- Stage 4 on the tablet \(boot 23\): firmware loaded into the 8 MiB DMA window \(length and digest verified by the kernel\), Wi-Fi SMMU stream routed and MHI/BHI layout read without hanging; this SMMU does not support address translation self-test \(ATOS\), so the DMA window translation is unverified.
- Stage 5 on the tablet \(boot 26\): chip power-up and boot loader doorbell executed without hanging or panicking; the result rows print only after the chip reports ready, after the GUI had already taken over the screen, so the stage 5 outcome is unknown \(needs a code change to observe\).

### Completion criteria

- The endpoint enumerates, firmware loads, a network interface is published and packets flow.

### Current limits

- The SMMU does not support ATOS, so the stage 4 DMA translation is unverified; the stage 5 outcome is unknown because the result rows printed after GUI takeover; there is no wireless protocol stack behind the driver, so networking is still far off. Firmware is read from the tablet's own Android partitions and never stored here. Bluetooth has only had its pin and clock read; the macOS-side HCI path is undecided.

### Next action

- Adjust logging timing so the stage 5 outcome is visible before GUI takeover; decide the wireless stack route.

### Evidence

- `device`: [Stage-1 rows read without a panic: PCIe0 collapsed, no clock votes, enable pins low \(2026-11-09\).](https://github.com/mataht/sheng-macos-link-lab/blob/milestone-desktop-20261109/docs/status.md)
  Command: <code>fastboot boot sheng-macos26-kernel.img (sheng-wifi=1)</code>. Revision: `36e11087791ca3b68505ee19c1f8602d7713039d`.
- `device`: [PCIe0 link up and endpoint ID 17cb:1107 read, no panic \(2026-11-10, video reading\).](https://github.com/mataht/sheng-macos-link-lab/blob/main/docs/status.md)
  Command: <code>fastboot boot sheng-macos26-kernel.img (sheng-wifi=2 sheng-rtc=2)</code>. Revision: `e5cd05044e6c9f2cb442da0d2c4444a270579994`.
- `device`: [BAR0, bus mastering, MHI and BHI registers read, no panic; MHIVER read as 0xdeadbeef \(2026-11-10, video reading, a few digits ambiguous\).](https://github.com/mataht/sheng-macos-link-lab/blob/main/docs/status.md)
  Command: <code>fastboot boot sheng-macos26-kernel.img (sheng-wifi=3 sheng-rtc=2)</code>. Revision: `e5cd05044e6c9f2cb442da0d2c4444a270579994`.

## Audio {#audio}

`planned`

### Hardware and dependencies

- ADSP-owned audio path; no work has started.

### Configuration

- None yet.

### Procedure

- None yet.

### Development findings

- None yet.

### Completion criteria

- Playback and capture through an audio driver that macOS recognises.

### Current limits

- Not started.

### Next action

- Wait for the ADSP stages and the battery service to run beyond their read-only first stage.

### Evidence

Collect evidence using the next action.

## Power {#power}

`implemented`

### Hardware and dependencies

- PMIC state \(RTC, backlight drivers KTZ8866 x 2\), ADSP-owned battery and charger services, RPMh, the performance and memory-latency state.

### Configuration

- Default-off drivers: NativeRtc \(sheng-rtc\), NativeBacklight \(sheng-backlight, always clamped to 64..2047\), NativeMemPerf \(sheng-memperf\), NativeAdsp and NativeBattery \(sheng-adsp, sheng-battery\), a PSCI reset hook \(sheng-psci-reset\). Charger writes are off and the critical battery level is never asserted.

### Procedure

- Boot with sheng-&lt;driver&gt;=1 for the read-only snapshot; later stages need approval.

### Development findings

- The first stage of each ran on the tablet without writes. XNU waits up to 30 seconds for an IORTC service at boot. With sheng-rtc=2 the platform expert publishes IORTC early and NativeRtc moves the calendar forward; on the tablet this saved about 30 seconds \(WindowServer's screen about 49 seconds after the boot command against 75 to 81 seconds before; read by hand from a video at 3 second steps\). The calendar starts at the packaging time, not the true time. The ADSP firmware owns the Type-C controller.
- System sleep panics in QEMU because the platform does not register its cores for sleep, so sleep is disabled.

### Completion criteria

- Battery state and charging reported to macOS; brightness control; time kept across boots; sleep.

### Current limits

- No battery reporting, no brightness control, no true time \(the calendar starts at the packaging time; the RTC counter probably clears on a forced reset, so an offset taken from Android is not usable\), no sleep.

### Next action

- Measure the memory-bandwidth stage; decide the first ADSP stage that starts the DSP.

### Evidence

- `device`: [The first stages ran without a panic and the command database read returned status 0 \(2026-11-09\).](https://github.com/mataht/sheng-macos-link-lab/blob/milestone-desktop-20261109/docs/status.md)
  Command: <code>fastboot boot sheng-macos26-kernel.img (read-only stage 1 of RTC, backlight, ADSP, memory performance)</code>. Revision: `36e11087791ca3b68505ee19c1f8602d7713039d`.
- `device`: [WindowServer's screen appeared about 49 seconds after the boot command against about 75 to 81 seconds before; the calendar started at the packaging time \(2026-11-09 night, hand reading of a video\).](https://github.com/mataht/sheng-macos-link-lab/blob/milestone-gpu-plugin-boot-20261109/docs/status.md)
  Command: <code>fastboot boot sheng-macos26-kernel.img (sheng-rtc=2 with a floor time)</code>. Revision: `e5cd05044e6c9f2cb442da0d2c4444a270579994`.

## Image assembly {#packaging}

`host-verified`

### Hardware and dependencies

- CI outputs, the paired Apple kernel extensions \(local only\), a device tree generated from board facts, driver switches, and the evidence from QEMU runs and device steps.

### Configuration

- The packager refuses a package unless its evidence matches: same kernel identity, QEMU observations, root install evidence and, for full-system packages, a sibling VirtIO build of the same kernel. A tiered policy decides whether earlier long-run evidence can be reused, by comparing build records.

### Procedure

- Assemble the kernel twice and compare byte for byte; run the quick QEMU gates \(root found, storage default off, memory layout, eight cores\); package; verify the package with an independent script that compares container, kernel, device tree and boot arguments.

### Development findings

- Assembly outputs and packages contain Apple code and vendor firmware and stay local; the repository holds the tools and tests.
- Reusing evidence is decided by comparing build records, not by hand.
- Every new kernel booted on 2026-11-10 evening had a complete 1200-second QEMU full-system run beforehand without a panic and with the image unchanged, as did the changed-rows display copy mode. Earlier boots 14 to 17 were made under per-package user waivers before their 1200-second runs were completed afterwards.
- The QEMU observer tool was fixed so that if the VM stops in user space at the time limit, it briefly steps the VM into kernel space before the final kernel data read.
- The packager's sibling qualification does not reject a QEMU run that ended in a panic. The fix \(refuse such a run unless an explicit waiver file bound to that run and kernel digest is given\) is on a local branch and not merged.

### Completion criteria

- Every package passes the independent review before any boot is requested.

### Current limits

- The local assembly and review outputs are not published, so a third party cannot rerun the review without their own inputs.

### Next action

- Document the packager's evidence rules in docs/ so another unit can reuse them.

### Evidence

- `host`: [The tests that cover the changed paths pass in the check job of run 42576253178.](https://github.com/mataht/sheng-macos-link-lab/blob/milestone-desktop-20261109/docs/ci.md)
  Command: <code>GitHub Actions: CN 1 TB sheng hardware candidate build</code>. Revision: `36e11087791ca3b68505ee19c1f8602d7713039d`.

## Diagnostics {#diagnostics}

`device-verified`

### Hardware and dependencies

- The framebuffer as a text console, a retained log in memory and in a small partition, and a QR code of the panic state.

### Configuration

- Boot progress lines and driver status rows are printed on the screen \(sheng-boot-progress\); on a panic the screen shows a QR code with registers, stack and a caller resolved against the kernel's UUID; optional native-gop-diag and native-touch-diag strips.

### Procedure

- Photograph or film the screen; scan the QR code and decode it with scripts/decode\_xnu\_panic.py.

### Development findings

- The first full-system boot panicked about 5 minutes 50 seconds after the command; the QR code identified watchdogd's exit as the cause.
- Unified logs of the guest can be read from the QEMU overlay.

### Completion criteria

- Every stage of the boot leaves a checkpoint on the screen and every panic leaves a decodable record.

### Current limits

- The retained log keeps only the tail \(80 KB in QEMU runs\). Guest logs are only readable in QEMU.

### Next action

- Add a persistent log of the userland stage for the full system.

### Evidence

- `device`: [Boot-progress lines were read from the screen and the panic QR code was scanned and decoded \(2026-11-09\).](https://github.com/mataht/sheng-macos-link-lab/blob/milestone-full-system-boot-20261109/docs/status.md)
  Command: <code>fastboot boot sheng-macos26-kernel.img</code>. Revision: `239b233aecf8840c763c24f1589eb5b1578ffa47`.

## usb {#usb}

`implemented`

### Hardware and dependencies

- DWC3 controller, eUSB2 repeater and PHY tables, RPMh rails; the Type-C role and VBUS are owned by the ADSP firmware.

### Configuration

- NativeUsb, default off: sheng-usb=1 read-only snapshot, 2 rails, GDSC, clocks and resets, 3 repeater, PHY and host role, xHCI reset and port polling, 4 a subclass of macOS's xHCI driver \(separate build\). The PHY table is a local file.

### Procedure

- Stage 1 needs nothing else; stages 3 and 4 need an external 5 V source because the CPU side has no VBUS path.

### Development findings

- Stage 1 ran on the tablet without writes.
- The class description used for stage 4 is a generated declaration with opaque names.

### Completion criteria

- A USB device enumerates and works through macOS's own USB stack.

### Current limits

- Stages 2 and above have never run on the tablet. Stage 4 needs its own candidate and gates.

### Next action

- Stage 2 with approval, sharing the RPMh channel with the keyboard cover without a lock.

### Evidence

- `device`: [The read-only stage-1 snapshot ran on the tablet \(2026-11-09\).](https://github.com/mataht/sheng-macos-link-lab/blob/milestone-desktop-20261109/docs/status.md)
  Command: <code>fastboot boot sheng-macos26-kernel.img (sheng-usb=1)</code>. Revision: `36e11087791ca3b68505ee19c1f8602d7713039d`.

## userspace {#userspace}

`device-verified`

### Hardware and dependencies

- The installed macOS 26.5 system supplied by the user, its original trust caches, and a few services the platform lacks \(a watchdog and a key store\).

### Configuration

- Development policy: dyld skips libignition; the original trust caches are loaded unchanged with no entries of our own \(Metal plug-in boots add the plug-in's two CDHashes and set lp-sip0 to 2\); platform UUID from the device tree; panic\_on\_crash\_disabled=1; minimal IOWatchdog \(reports disabled\) and AppleKeyStore \(no keybag, no passcode, unlocked\) enabled by sheng-watchdog=1 and sheng-aks=1.

### Procedure

- Boot the full-system package; auto-login and no screen lock are required because the tablet has no hardware keyboard.

### Development findings

- The first full-system boot ran to WindowServer and then panicked when watchdogd exited without its service; a later boot reached the login window; with the services and the lock preference off it reached the desktop.
- loginwindow and WindowServer run; apps and long-run stability are not tested.
- In QEMU, opendirectoryd's first node open often times out after 5 seconds and is retried; all 7 runs with readable guest logs show 1 to 5 such timeouts, after which the process restarts and succeeds. Occasionally the process panics instead \(Failed to open /Search\), which panic\_on\_crash\_disabled does not mask. The cause is not established. No such panic was seen on the tablet, where guest logs are not readable, so silent restarts cannot be excluded.

### Completion criteria

- The desktop appears and stays up; apps run.

### Current limits

- Development kernel without a root seal check, AMFI developer mode, no SEP. Apps, network and stability under load are untested.

### Next action

- Find the cause of the slow composition, then test apps and a long run.

### Evidence

- `device`: [The full system reached the desktop about two minutes after the boot command \(2026-11-09\).](https://github.com/mataht/sheng-macos-link-lab/blob/milestone-desktop-20261109/docs/status.md)
  Command: <code>fastboot boot sheng-macos26-kernel.img</code>. Revision: `36e11087791ca3b68505ee19c1f8602d7713039d`.

</div>
