# Samsung Galaxy Tab S7+ Wi-Fi \(SM-T970, gts7xlwifi\): iPadOS desktop, 8 cores, GPU, touch, USB console, battery

[rui12366B/UniXNU-gts7xlwifi](https://github.com/rui12366B/UniXNU-gts7xlwifi)

<div v-pre>

Samsung Galaxy Tab S7+ Wi-Fi \(SM-T970\). iPadOS 17.7.11 desktop with 8 cores in 4+3+1 clusters and DVFS, native UFS root and Data, GPU-composited UI \(Adreno 650\), touch, brightness, USB debug console and battery; Wi-Fi at PCIe stage 4.

源记录: [porting.toml](https://github.com/rui12366B/UniXNU-gts7xlwifi/blob/88b34f97100a01aab4ea6b86dc9c748b2114c382/porting.toml), `88b34f97100a01aab4ea6b86dc9c748b2114c382`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `implemented` |
| [固件与启动](#firmware) | `implemented` |
| [CPU 与中断](#cpu) | `device-verified` |
| [内存与 DMA](#memory) | `device-verified` |
| [存储与根卷](#storage) | `device-verified` |
| [显示](#display) | `device-verified` |
| [输入](#input) | `device-verified` |
| [GPU](#gpu) | `device-verified` |
| [网络](#network) | `implemented` |
| [音频](#audio) | `device-verified` |
| [bluetooth](#bluetooth) | `device-verified` |
| [sensors](#sensors) | `implemented` |
| [电源](#power) | `implemented` |
| [haptics](#haptics) | `implemented` |
| [camera](#camera) | `implemented` |
| [镜像组装](#packaging) | `implemented` |
| [诊断](#diagnostics) | `device-verified` |

## 配置 {#configuration}

`implemented`

组件: `ArmDTPlatform`, `SoftwareAES`, `XnuPrelink`, `DarwinBoot`.

### 硬件与依赖

- SM8250 layer FFT-infra/UniXNU-sm8250-common 166235ec; iPadOS 17.7.11 21H461 kernelcache as prelink donor.

### 配置

- board.toml \[components\] include, \[kernel\] patch\_series \(arch, soc, device before-os, os, device\), \[payload\] text\_fixups and ADT product strings.

### 操作步骤

- ./unixnu build kernel; ./unixnu build payload --trust-cache &lt;owner trust cache&gt;.

### 开发经验

- A payload built without --trust-cache lacks the ADT trust-cache slot and the boot menu reports Compromised Data.
- board.description is the catalog title; it names the working functions so this record is told apart from the single-core sm-t970 bootstrap.
- The Wi-Fi stack archive libT970Wifi.a is force-loaded through CONFIG\_XNU\_EXTRA\_LD\_ARCHIVES, and board.toml lists build-t970-wifi.py and the audio plug-in trust cache hash; nothing in either runs without its boot argument.
- README.md describes the state as of the combo7 test build \(audio, haptics and shutdown working; Wi-Fi, Bluetooth, sensors and camera in progress\).
- board.toml lists the trust-cache hashes of the addon variants that carry the Wi-Fi supplicant, the Bluetooth BlueTool service and the Turnip buffer fix.
- board.toml lists the trust-cache hashes of the later addon variants \(audio ABI v3 with the microphone, and the bluetoothd patch sets\); README.md describes the state as of the combo26 test build \(Wi-Fi with Safari, microphone, keychain working; Bluetooth power-on and the S Pen in progress\).
- The port now builds on upstream UniXNU main \(62be7bc\) with the core carries in docs/host-patches/unixnu-main, adreno-metal-main and gop-framebuffer-main; boot arguments use upstream's names without the sheng- prefix, and board.description lists the working functions \(6.7 GB RAM, S Pen, Wi-Fi, Bluetooth, audio, USB\).

### 完成条件

- All source pins resolve and the kernel, prelink and payload build.

### 当前范围

- Built against a UniXNU-next checkout with docs/host-patches applied.

### 下一步

- Drop the host patches once equivalent changes land upstream.

### 证据

- `source`: [Board configuration with component selection, patch order and payload ADT strings.](https://github.com/rui12366B/UniXNU-gts7xlwifi/blob/88b34f97100a01aab4ea6b86dc9c748b2114c382/board.toml)

## 固件与启动 {#firmware}

`implemented`

### 硬件与依赖

- Samsung bootloader T970 with a UEFI boot selector on the boot partition \(separate firmware tree\), ESP with EFI/UniXNU.

### 配置

- docs/menu/unixnu.toml: kernel command line &lt;= 1000 bytes; payload at Payloads/gts7xlwifi.

### 操作步骤

- Copy kernel.macho, kernel.macho.adt and the trust cache to the ESP; choose the UniXNU entry in the menu \(the selector defaults to TWRP after adb reboot\).

### 开发经验

- The A650 GMU/SQE/ZAP images are compiled in; scripts/gen-gpu-firmware-a650.py rebuilds the source from the tablet files, reassembling the ZAP ELF from its .b0N segments.
- proprietary-files.txt lists the Wi-Fi board files and regdb and the ADSP image \(squashed from the split mdt by scripts/squash-mdt.py\); all stay in the ignored .cache directory.
- docs/menu/unixnu.toml is the main-base menu: renamed boot arguments, a 1023-byte command line, and the memory-outside entry. The boot partition \(candidates/menu-twrp-v1\) boots UniXNU main payloads unchanged; Skyward recovery \(separate project\) replaces TWRP for staging.

### 完成条件

- The menu starts XNU with the payload and its ADT.

### 当前范围

- The UEFI firmware itself is not in this repository.

### 下一步

- Publish the UEFI firmware tree or pin it.

### 证据

- `source`: [Firmware inputs with sources and SHA-256.](https://github.com/rui12366B/UniXNU-gts7xlwifi/blob/88b34f97100a01aab4ea6b86dc9c748b2114c382/proprietary-files.txt)

## CPU 与中断 {#cpu}

`device-verified`

组件: `ArmCpu`.

### 硬件与依赖

- Kryo 585: 4x A55 \(EPSS domain 0x18591000\), 3x A77 \(0x18592000\), 1x A77 prime \(0x18593000\); GICv3; TSENS 0xc263000/0xc265000.

### 配置

- armcpu-spi-ipi=1 armcpu-spi-ipi-base=544; DTS unixnu,cluster-type and unixnu,die-cluster-id 0/1/2; cpufreq=4 cpufreq-cap=2000.

### 操作步骤

- Boot with all 8 cores; read SMP and CPUFREQ rows of the boot log.

### 开发经验

- SGI/SPI 1008..1015 are group-0 secure on this firmware, so IPIs use software-pended SPIs from 544. MPIDR AFF1 numbers single cores in one DynamIQ cluster, so the scheduling cluster comes from die-cluster-id \(t970-three-clusters.patch, with the SM-T733 boot-cluster fallback\). DVFS: perfcontrol class and 200 ms load per EPSS domain, 10 ms worker \(after SM-T733 T733CpuPower\).
- The device tree gained a wlan node \(compatible qcom,qca6390\) for wifid's launchd condition; CPU nodes are unchanged.
- The device tree gained a bluetooth node \(/arm-io/bluetooth\) so MobileGestalt reports Bluetooth; CPU nodes are unchanged.
- ArmCpu follows the boot-argument rename \(smp=1\).

### 完成条件

- Seven secondary cores reach step 7; each EPSS domain changes level with load.

### 当前范围

- TSENS uses the hottest sensor only; no per-cluster thermal zones.

### 下一步

- Group TSENS sensors per cluster as SM-T733 T733Thermal.

### 证据

- `device`: [SMP c1..c7=step7; CPUFREQ d0 1804 MHz, d1 1958 MHz, d2 844 MHz idle with 601 level changes.](https://github.com/rui12366B/UniXNU-gts7xlwifi/blob/88b34f97100a01aab4ea6b86dc9c748b2114c382/docs/evidence/periph15-bootlog.txt)
  Command: <code>TWRP: python3 tools/read-boot-log.py --port &lt;adb serial&gt; --out logs (after booting the periph15 payload, docs/menu/unixnu.toml)</code>. Revision: `781e3528e2d5e0dc0c9c6fa1e409f5a4bc1cf0e2`.

## 内存与 DMA {#memory}

`device-verified`

### 硬件与依赖

- DRAM above the 2 GiB owned window up to t970-dram-end, with firmware holes.

### 配置

- t970-dram-end=0x280000000; /chosen/t970-dram-holes.

### 操作步骤

- Boot and read the MEM row.

### 开发经验

- XNU manages DRAM beyond the first window once the holes are skipped.
- The device tree gained a wlan node only; the memory map is unchanged.
- The device tree gained a bluetooth node only; the memory map is unchanged.
- Upstream's outside-window adoption is ported to xnu-10063 \(t970-memory-outside.patch\): six Android-RAM runs below the window are adopted page by page after the VM starts \(memory-outside=1\); with the 0xd0000000 run MEM totalMiB is 6733 with 0 refused pages.

### 完成条件

- totalMiB reflects the extended range.

### 当前范围

- DMA engines use their own SMMU contexts per driver.

### 下一步

- Raise t970-dram-end further per the RAM plan.

### 证据

- `device`: [MEM totalMiB=5969.](https://github.com/rui12366B/UniXNU-gts7xlwifi/blob/88b34f97100a01aab4ea6b86dc9c748b2114c382/docs/evidence/periph15-bootlog.txt)
  Command: <code>TWRP: python3 tools/read-boot-log.py --port &lt;adb serial&gt; --out logs (after booting the periph15 payload, docs/menu/unixnu.toml)</code>. Revision: `781e3528e2d5e0dc0c9c6fa1e409f5a4bc1cf0e2`.

## 存储与根卷 {#storage}

`device-verified`

组件: `ShengUfs`, `VirtioMmioBlock`, `VerifiedRoot`, `AppleKeyStoreState`.

### 硬件与依赖

- UFS host \(NativeUfs-alioth ab54059\); signed OS image and Data container on a spare partition.

### 配置

- native-ufs-root=1 native-ufs-stream=0xe0 t970-ufs-data=1 ufsrw=1.

### 操作步骤

- Boot and read the UFS row.

### 开发经验

- Root reads are verified per 4 KiB block; Data persists across boots.
- Boot hangs after the addon install were the polled UFS wait: IODelay\(2\) is a timer sleep on this board \(cpu\_idle\_latency 0\) taken under gHost.lock; the poll now spins on the counter for 20 ms before sleeping, with a \[ufs poll\] diagnostic row. The addon install now ends with F\_FULLFSYNC so a hard reset no longer loses its writes.
- ShengUfs follows the boot-argument rename.

### 完成条件

- No UFS failures or integrity errors over a full desktop session.

### 当前范围

- Shutdown hangs unmounting the OS volume after IOServicePH::systemHalt; the UFS driver stops serving I/O there.

### 下一步

- Serve I/O until the halt callback and flush, as SM-T733 native\_ufs\_shutdown\_complete.

### 证据

- `device`: [UFS requests=321101 verified4K=1136628 failures=0 integrity=0.](https://github.com/rui12366B/UniXNU-gts7xlwifi/blob/88b34f97100a01aab4ea6b86dc9c748b2114c382/docs/evidence/periph15-bootlog.txt)
  Command: <code>TWRP: python3 tools/read-boot-log.py --port &lt;adb serial&gt; --out logs (after booting the periph15 payload, docs/menu/unixnu.toml)</code>. Revision: `781e3528e2d5e0dc0c9c6fa1e409f5a4bc1cf0e2`.

## 显示 {#display}

`device-verified`

组件: `GopFramebuffer`.

### 硬件与依赖

- S6TUUM3 dual-DSI 2800x1752 panel, UEFI GOP framebuffer at 0x9c000000, DPU direct scanout.

### 配置

- dpu-scanout=2; ADT artwork-display-gamut = sRGB; 12 text\_fixups \(SM-T733 21H461 sRGB/BGRA8 policy\).

### 操作步骤

- Boot to the desktop; read DISPLAY and SWAP rows.

### 开发经验

- CoreAnimation XR10/b3a8 composition striped on A650 although every single format-550 operation probed exact; forcing sRGB BGRA8 \(text\_fixups + gamut\) removed the stripes. text repage keeps the fixups after a code page is evicted.
- LegacyDisplayProbe starts the haptics, camera, ADSP, audio, sensors and Bluetooth threads after the display is up; the display path itself is unchanged.
- LegacyDisplayProbe also starts the S Pen thread \(weak t970\_pen\_start\) after the display is up; the display path is unchanged.
- LegacyDisplayProbe and GopFramebuffer changes follow the boot-argument rename.

### 完成条件

- Desktop without stripes; swaps retire by direct scanout.

### 当前范围

- 120 Hz and brightness curve are not tuned.

### 下一步

- Measure frame pacing with the GPU frame trace.

### 证据

- `device`: [DISPLAY stage=10; SWAP retired=1438 with 2 copies; \[text fixup\] applied=12.](https://github.com/rui12366B/UniXNU-gts7xlwifi/blob/88b34f97100a01aab4ea6b86dc9c748b2114c382/docs/evidence/periph15-bootlog.txt)
  Command: <code>TWRP: python3 tools/read-boot-log.py --port &lt;adb serial&gt; --out logs (after booting the periph15 payload, docs/menu/unixnu.toml)</code>. Revision: `781e3528e2d5e0dc0c9c6fa1e409f5a4bc1cf0e2`.

## 输入 {#input}

`device-verified`

组件: `ShengHidInput`, `ShengNovatekTouch`, `QcomGeniSpi`.

### 硬件与依赖

- STM fts1ba90a at I2C 0x49 on QUP SE5 pins 12/13, attention GPIO 15; PMIC keys.

### 配置

- native-touch=1 touch-hid=1 t970-touch-xform=5 offline-hid-input=1.

### 操作步骤

- Touch the desktop; read TOUCHSTAT on the USB console.

### 开发经验

- The panel bus is driven as a GPIO I2C master; ShengNovatekTouch and QcomGeniSpi come in as catalog dependencies of ShengHidInput and are not used by this board.
- NativeHidInput also publishes accelerometer, gyro and orientation HID devices for the sensor service, with the 0xff00 usages backboardd and locationd look for.
- Motion HID devices set Built-In before IOHIDDevice::start so locationd's matching sees it at registration.
- The S Pen is a Wacom W9020-class digitizer on I2C \(package/T970Pen.cpp\): position 26712x16714, 4096 pressure levels, tilt, side button and the garage switch all decode on device. iPadOS ignores it so far: backboardd drops any touch path index of 31 or more \(the first contact id 0xfe was thrown away\), takes a Pencil only from its own 0x0D/0x20 digitizer service, and the separate pen service is not yet opened by the HID event system. Notes in docs/spen-notes.md.
- The S Pen works as an Apple Pencil: backboardd only opens a digitizer service shaped like the touch device \(keyboard collection first\), files it as the pencil from usage 0x0D/0x20, drops touch path indices of 31 or more, and needs AccurateMaxDigitizerPressureValue for UIKit to report force; pressure is scaled to UIKit's 0..1000 range by a dispatch wrapper.

### 完成条件

- Touches reach SpringBoard as HID events.

### 当前范围

- No palm rejection or S Pen.

### 下一步

- Add the S Pen digitizer.

### 证据

- `device`: [TOUCHSTAT frames and HID submissions on the live console.](https://github.com/rui12366B/UniXNU-gts7xlwifi/blob/88b34f97100a01aab4ea6b86dc9c748b2114c382/docs/evidence/usb-console.txt)
  Command: <code>macOS: read /dev/cu.usbmodem* while the periph15 payload runs</code>. Revision: `781e3528e2d5e0dc0c9c6fa1e409f5a4bc1cf0e2`.

## GPU {#gpu}

`device-verified`

### 硬件与依赖

- Adreno 650 \(A650 GMU/SQE/ZAP\), apps SMMU GPU context; AdrenoMetal userspace \(metal2vulkan + Turnip\) in an embedded addon.

### 配置

- pipa-gpu=12 gpu-addon=1 fb-gpu=1; NativeSandboxGrantEntitlement = opengl-or-metal, posterkit.provider.

### 操作步骤

- Boot to the desktop; read the gpu clients and methods rows.

### 开发经验

- Wallpaper posters crash-looped on a nil MTLBuffer because MACF denied AGXDeviceUserClient; granting by entitlement \(SM-T733\) fixed them. A GPU read at 0x1\_086de2c0 past the 32-bit window poisoned a VM once \(diagnostics \[gpu far\]/\[gpu vmfail\] armed\).
- GPU page faults no longer freeze the system: hangcheck ends a latched SMMU fault and restarts the CP \(gpufault1-4\), replays avoid draining queued jobs, and a Turnip patch \(t970-bo-safe\) stops command buffers being recycled while a submission still uses them.
- Adopted DRAM below gPhysBase must get CPU cache maintenance like kernel DRAM \(NativeAdrenoCpu\); otherwise the CP read zeroed command buffers and the UI stuttered. The stall handler no longer halts GBIF on a busy GPU; a UI rotation re-layout still resets the SoC and is being bisected. MobileNotes is granted the GPU so PencilKit gets a Metal device.

### 完成条件

- backboardd, SpringBoard, widget renderers, posters and Settings composite on the GPU with no map failures.

### 当前范围

- mediaserverd gets VK\_ERROR\_INITIALIZATION\_FAILED; a latched cb0 FSR 0x400 is not cleared.

### 下一步

- Add an SMMU context fault handler that records and clears FSR.

### 证据

- `device`: [gpu clients backboardd 1353M, SpringBoard 609M, CollectionsPoster 512M; BoAlloc/BoMap/Submit 0 failures.](https://github.com/rui12366B/UniXNU-gts7xlwifi/blob/88b34f97100a01aab4ea6b86dc9c748b2114c382/docs/evidence/periph15-bootlog.txt)
  Command: <code>TWRP: python3 tools/read-boot-log.py --port &lt;adb serial&gt; --out logs (after booting the periph15 payload, docs/menu/unixnu.toml)</code>. Revision: `781e3528e2d5e0dc0c9c6fa1e409f5a4bc1cf0e2`.

## 网络 {#network}

`implemented`

### 硬件与依赖

- QCA6390 \(17cb:1101\) on PCIe0: PERST GPIO 79, CLKREQ 80, WLAN\_EN 90; rails smpa4/5/6, smpc8, ldoc5; stream 0x1c01.

### 配置

- t970-wifi=&lt;stage&gt; \(4 = link and endpoint, 5 = BHI firmware, 6 = the full ath11k stack: build/t970-wifi/libT970Wifi.a, force-loaded; the DTS wlan node must be set to okay for wifid\).

### 操作步骤

- Boot with t970-wifi=4 and read the \[t970 wifi\] rows.

### 开发经验

- cmd-db lists several VRM names twice; the first match is used \(Linux behaviour\). Stage 5 with an SMMU bypass and a 36-bit buffer reset the tablet within 20 s.
- A private apps-SMMU stage-1 bank for stream 0x1c01 \(IOVA 0xa0000000, 4 MiB page-mapped arena\) contains the endpoint DMA: BHI fetched the SBL with FSR staying at FORMAT 0x400 and no reset. Choosing the bank top-down and writing FSR hung a CPU at the first access; bottom-up like QcomUsbDmaDomain with 32-bit accesses works. FSR 0x400 is the AArch64 FORMAT bit, not a fault.
- Stage 6 runs Linux ath11k for QCA6390 hw2.0 with MHI, QRTR and QMI \(package/T970WifiStack.cpp, scripts/build-t970-wifi.py\): the firmware reaches mission mode, cache maintenance fixed the ef128100 PBL error, the QRTR name service now answers the firmware's HELLO, and WLFW is announced. The board-file download then stops with an MHI BAD\_TRE completion on the IPCR uplink channel.
- The Wi-Fi supplicant \(unixnu-wpa\_supplicant, built by scripts/build-t970-wifi-service.py\) runs from the addon on Data with a launchd cache union-mounted over /System/Library/xpc \(t970-wifi-svc=1\). Scanning \(41 networks\), the 856-byte 21H461 join request, WPA2 join, DHCP, DNS and TCP all work; wifid does not yet mark the link usable, so there is no status-bar icon and no Safari traffic.
- The Wi-Fi link is usable end to end: IPConfiguration's router check reads replies through BPF, so the driver now taps every frame from a separate thread \(tapping in the receive thread hung the tablet, t970-wifi-bpf=0 turns it off\), and the repeated link-changed events after a join are suppressed so wifid stops treating each one as a roam. The status-bar icon appears and Apple News loads; Safari also needs no-lc=1 because launch constraints killed its web content process. The icon still shows no signal bars.
- The coordinator config adds the signal-bar RSSI event and BPF tap thread verified on combo25/26; status stays implemented until a sanitized device row is recorded.

### 完成条件

- Link L0, endpoint identity, BAR and MHI registers readable.

### 当前范围

- DMA domain works; SBL does not reach READY yet; no MHI contexts, QMI or ath11k.

### 下一步

- After BHI the device stays in PBL and never reports READY within 3 s: extend the wait to 10 s, trace EE/state/BHI status every 100 ms, compare with Linux mhi\_fw\_load\_bhi; then MHI contexts, BHIe for the full image and the ath11k port \(Chengdong-Yu/pong-wifi\).

### 证据

- `device`: [\[t970 wifi dom\] rc 1 bank 6 SMR 7 ASID 0xfc00, FSR 0x400; \[t970 wifi mhi\] BHI from IOVA 0xa0000000, failed in WaitReady after 3000 ms.](https://github.com/rui12366B/UniXNU-gts7xlwifi/blob/88b34f97100a01aab4ea6b86dc9c748b2114c382/docs/evidence/periph17-wifi.txt)
  Command: <code>TWRP: python3 tools/read-boot-log.py --port &lt;adb serial&gt; (periph17 payload, t970-wifi=5)</code>. Revision: `cf6ed1702d3ddc2ace4cc988b982117e77f32c0b`.
- `device`: [\[t970 wifi\] link in 13 ms, endpoint 17cb:1101 class 0x0280, BAR0 at 0x60300000.](https://github.com/rui12366B/UniXNU-gts7xlwifi/blob/88b34f97100a01aab4ea6b86dc9c748b2114c382/docs/evidence/periph15-bootlog.txt)
  Command: <code>TWRP: python3 tools/read-boot-log.py --port &lt;adb serial&gt; --out logs (after booting the periph15 payload, docs/menu/unixnu.toml)</code>. Revision: `781e3528e2d5e0dc0c9c6fa1e409f5a4bc1cf0e2`.

## 音频 {#audio}

`device-verified`

### 硬件与依赖

- ADSP \(adsp.mdt squashed to adsp.mbn, loaded through PAS/SCM\), GLINK/SMEM/SMP2P/QMP to the ADSP, APR to AFE/ADM/ASM; speaker port PRI TDM RX \(4 slots x 32 bit, DSP\_A, short sync, delay 1\); four CS35L41 amplifiers on QUP SE11 I2C 0x40-0x43.

### 配置

- t970-adsp=2 t970-audio=32 \(iOS output device through hal/T970AudioPlugIn.c and the T970AudioService ring\). t970-audio-gain=&lt;0-20&gt; sets the amp PCM gain \(default 12\).

### 操作步骤

- Boot with t970-adsp=2 t970-audio=32, play a system sound or music, read the \[audio\] and \[audio svc\] rows.

### 开发经验

- The iOS output was distorted for two reasons: startOutput cleared the whole shared ring after the path came up, erasing the samples the plug-in had already written \(found with a plug-in/kernel waveform capture\); and the amps sampled on the wrong bit-clock edge. Samsung's machine driver uses DSP\_A with IB\_NF, so SP\_FORMAT SCLK\_INV must be 1. The fsync errata write ASP\_CONTROL4 and Android's noise gate NG\_CFG were also added.
- Android runs Cirrus speaker protection firmware on the amplifier DSPs with a higher PCM gain behind it; without it the gain is kept lower.
- The built-in microphone works as an iOS input device: DMIC3 through the LPASS TX macro, decimator 0 at 48 kHz, AFE TX\_CODEC\_DMA\_TX\_3 \(0xB037\), ADM and an ASM read session, with the PM8150A L5 mic supply voted while capturing \(defaults copied from Android with scripts/t970-android-mic-dump.sh\). The shared page ABI is version 3; the microphone is on by default and t970-audio bit 8388608 turns it off.
- The microphone is on by default \(t970-audio bit 8388608 turns it off\).

### 完成条件

- iOS system sounds and media play cleanly on the four speakers.

### 当前范围

- No speaker protection firmware \(CSPL\), so the volume stays below Android's; no microphone yet.

### 下一步

- Confirm loudness with audio14 \(gain 12, VPBR\); later a CSPL loader for the amplifier DSPs and the microphone path.

### 证据

- `device`: [\[audio mic\] st=11/0 reads=1847/1847/0 frames=878880 peak=6941 ldo=0: microphone capture through the TX macro, recorded and played back in Voice Memos.](https://github.com/rui12366B/UniXNU-gts7xlwifi/blob/88b34f97100a01aab4ea6b86dc9c748b2114c382/docs/evidence/main7-bootlog.txt)
  Command: <code>recovery root shell: python3 tools/read-boot-log.py --port &lt;adb serial&gt; --out logs (main7b payload, docs/menu/unixnu.toml)</code>. Revision: `b2cdb153b4f46a3bdaeb2326f326ce5c78adc58d`.
- `source`: [AFE/ADM/ASM bring-up, CS35L41 setup \(SCLK\_INV, fsync errata, noise gate, VPBR\) and the shared output ring.](https://github.com/rui12366B/UniXNU-gts7xlwifi/blob/88b34f97100a01aab4ea6b86dc9c748b2114c382/package/T970Audio.cpp)

## bluetooth {#bluetooth}

`device-verified`

### 硬件与依赖

- QCA6390 Bluetooth on QUP0 SE6 UART \(GPIO 16-19\), BT\_EN GPIO 76; firmware htbtfw20.tlv and htnv20.bin from the device.

### 配置

- t970-bt=&lt;bits&gt; \(1 run, 2 ROM readback only, 64 step mode, 128 USB mirror\).

### 操作步骤

- Boot with t970-bt=131 and read the \[t970 bt\] and \[t970 bt log\] rows.

### 开发经验

- GPIO 20-23, 28-31 and 40-43 are TrustZone-protected; touching them resets the SoC, so the driver refuses them.
- The wrap-0 AHB branches run under hardware clock gating and read off while idle.
- The controller answers HCI, takes htbtfw20.tlv/htnv20.bin at 3 Mbaud \(QUP 2.5 needs 16x UART oversampling\) and serves com.apple.uart.sk.bluetooth; a replacement BlueTool runs as its own launchd job. bluetoothd still exits at start because the keychain cannot store its root keys.
- With software key wrapping in AppleKeyStoreState the keychain stores bluetoothd's root keys. The stock bluetoothd then stopped at HCI commands this QCA6390 does not support; build-t970-bluetool.py patches it to skip 0x0c5b, to treat refused unsupported commands \(status 628\) as skipped, and to stay on legacy LE \(no 0x204a, which locks the chip out of legacy scan\). The driver keeps the last HCI commands and replies per session \(\[t970 bt hci\]\). bluetoothd now stays up but Settings cannot turn Bluetooth on yet.
- bluetoothd patches \(skip 0x0c5b, unsupported commands as skipped, legacy LE only\) plus the scan random-address and power-off race fixes let Settings turn Bluetooth on.

### 完成条件

- The controller answers HCI\_Reset and reports its version, then loads the rampatch and NVM.

### 当前范围

- No HCI transport into iPadOS yet.

### 下一步

- ROM readback, firmware download, then the bluetoothd transport.

### 证据

- `device`: [\[t970 bt sk\] st 2 res 0 act 2/1/1/1: bluetoothd connected once and stayed up; Settings turned Bluetooth on.](https://github.com/rui12366B/UniXNU-gts7xlwifi/blob/88b34f97100a01aab4ea6b86dc9c748b2114c382/docs/evidence/main7-bootlog.txt)
  Command: <code>recovery root shell: python3 tools/read-boot-log.py --port &lt;adb serial&gt; --out logs (main7b payload, docs/menu/unixnu.toml)</code>. Revision: `b2cdb153b4f46a3bdaeb2326f326ce5c78adc58d`.
- `source`: [Power, clock, SMMU and GENI UART bring-up with a secure-pin guard.](https://github.com/rui12366B/UniXNU-gts7xlwifi/blob/88b34f97100a01aab4ea6b86dc9c748b2114c382/package/T970Bluetooth.cpp)

## sensors {#sensors}

`implemented`

### 硬件与依赖

- LSM6DSO accelerometer and gyroscope, AK09918 magnetometer, VEML3328 light sensor, all behind the SLPI sensor core \(Android reaches them through FastRPC\).

### 配置

- t970-sensors=112 \(HID accelerometer, gyro and orientation devices fed with a fake gravity vector, locationd kept enabled\).

### 操作步骤

- Boot with t970-sensors=112, read the \[sensors hid\] rows, check that the screen rotates.

### 开发经验

- backboardd follows CoreMotion, which locationd computes from accelerometer &\#123;0xff00,3&\#125; and gyro &\#123;0xff00,9&\#125; services; the HID devices are stamped with those usages.
- locationd uses the Device Orientation service &\#123;0x20,0x8a&\#125; on this model; with Built-In stamped and debug logging \(t970-sensors bit 128\) the service is still reported not ready, so rotation is not working yet.
- The pen changes in NativeHidInput and HidInputProbe add a separate digitizer device only with t970-pen; the motion HID devices are unchanged.
- Motion HID devices need the keyboard-first descriptor to be opened and a mach\_absolute\_time child event \(0xff15/2\) or locationd drops orientation as stale; with both, a fake gravity source rotates the UI. The SLPI boots over PAS 12 and announces sensor service 400 without FastRPC \(st 14\); real accelerometer streaming is next.

### 完成条件

- The screen follows the device orientation.

### 当前范围

- Fake sensor data only; the real sensors need the SLPI FastRPC stage.

### 下一步

- Find where locationd's orientation detection stops \(exported system log\), then the SLPI path.

### 证据

- `source`: [Fake accelerometer, gyro and orientation reports through NativeHidInput.](https://github.com/rui12366B/UniXNU-gts7xlwifi/blob/88b34f97100a01aab4ea6b86dc9c748b2114c382/package/T970Sensors.cpp)

## 电源 {#power}

`implemented`

### 硬件与依赖

- MAX77705 fuel gauge \(I2C 0x36\) and charger \(0x69\) on QUP SE0 pins 28/29; PSCI.

### 配置

- t970-battery=1 pmgr=2.

### 操作步骤

- Boot and read the \[t970 battery\] row; shut down from Settings.

### 开发经验

- Samsung arms the MAX77705 charger watchdog; unkicked it turns charging off \(CHG\_DTLS 0xb\). The service kicks CHG\_CNFG\_06 every 10 s.
- Shutdown works: after the writable volumes are unmounted the kernel waited forever on the sealed OS volume, so a 10 s failsafe \(patches/xnu/t970-shutdown-failsafe.patch\) makes the PSCI call; the speaker amplifiers are muted first so there is no pop.
- Charging: input limit and charge current are set from the Type-C Rp/BC1.2 source with the AICL threshold at 4.5 V; PD source capabilities are read and 9 V PD/AFC is available behind t970-hv. The Apple USB stack port \(QcomDwc3\) is planned in docs/usb-plan.md with 21H461 class layouts.
- docs/usb-plan.md gains the SuperSpeed console plan and the combo24c/25 diagnosis \(missing clock resume\).
- docs/usb-plan.md records the QcomDwc3 device-mode result and the cable/port finding for SuperSpeed.

### 完成条件

- iPadOS shows the battery level and charge state; halt powers off.

### 当前范围

- Input current stays at the default USB limit; shutdown does not reach PSCI yet \(storage\).

### 下一步

- Set CHGIN\_ILIM from the Type-C current; finish the UFS shutdown path.

### 证据

- `device`: [\[t970 battery\] 100.0 %, 4306 mV, +66 mA, charging, 48 watchdog kicks.](https://github.com/rui12366B/UniXNU-gts7xlwifi/blob/88b34f97100a01aab4ea6b86dc9c748b2114c382/docs/evidence/periph15-bootlog.txt)
  Command: <code>TWRP: python3 tools/read-boot-log.py --port &lt;adb serial&gt; --out logs (after booting the periph15 payload, docs/menu/unixnu.toml)</code>. Revision: `781e3528e2d5e0dc0c9c6fa1e409f5a4bc1cf0e2`.

## haptics {#haptics}

`implemented`

### 硬件与依赖

- Samsung COINDC coin motor on its own rail, PM8150L LDO7 \(ldoc7, 2856 mV\), switched by RPMh VRM votes \(live FDT msm\_vibrator\).

### 配置

- t970-haptics=2 \(boot test pulse\) or 3 \(test pulse and the T970Haptics service\).

### 操作步骤

- Boot with t970-haptics=3, feel one 150 ms buzz, read the \[t970 haptics\] row.

### 开发经验

- The PMIC LRA block qcom,haptics@c000 is disabled in the FDT; the motor is the regulator-driven ERM of Samsung's msm\_vibrator.

### 完成条件

- The motor pulses at boot; userspace pulses it through the Pulse property.

### 当前范围

- iPadOS has no vibration path of its own; nothing in the stock system calls the service.

### 下一步

- Route system haptics to the service \(docs/haptics.md\).

### 证据

- `source`: [LDO7C vote sequence and the T970Haptics service.](https://github.com/rui12366B/UniXNU-gts7xlwifi/blob/88b34f97100a01aab4ea6b86dc9c748b2114c382/package/T970Haptics.cpp)

## camera {#camera}

`implemented`

### 硬件与依赖

- Three Samsung cam\_sensor modules on the Titan 480 CCI \(live FDT\): front CCI0 m1 0x2d, rear CCI0 m0 0x2d, ultra-wide CCI1 m0 0x10; GPIO-switched rails, titan\_top\_gdsc.

### 配置

- t970-camera=1 \(front chip-ID read\), 7 \(all three\), +8 to leave the last sensor powered, +16 sensor-side stream test \(C2a\), +32 CSIPHY 3/CSID-lite0 receive test on the front sensor \(C3a; t970-camera=33\), +64 one RAW10 frame through IFE-lite0 into pil\_cdsp\_region with a 64x48 thumbnail in the log \(C4; t970-camera=65\).

### 操作步骤

- Boot with t970-camera=7, read the \[t970 camera\] row: st 8 and an ID word per sensor.

### 开发经验

- No camera code upstream; iPadOS expects Apple's H9 ISP \(AppleH9CameraInterface\), so frames need a raw CAMSS path \(docs/camera-notes.md\).
- C1 on device: front S5K4HA \(0x48ab\), rear S5K3M5 \(0x30d5, rev a001\), ultra-wide S5K5E9 \(0x559b\); CCI v1.7 on XO 19.2 MHz, 56 ms.
- C2a on device: all three stream on their power-on defaults \(frame\_count +8/+7/+8 in 300 ms, \~23-27 fps\) without an init list.
- C3a on device: front S5K4HA defaults = 3280x2464 RAW10, 4 lanes at 700 Mbit/s; CSIPHY 3 + CSID-lite0 received 17852 packets in 300 ms with 0 ECC and 0 CRC errors, long packet DT 0x2b WC 4100.
- C4 on device \(combo9, t970-camera=65\): one full 3280x2464 RAW10 frame through CSID-lite0 RDI0 and IFE-lite0 WM0 into pil\_cdsp 0x8e300000 in 65 ms, SMMU SMRs 0x800/0x840 mask 0x400 on the shared bypass bank \(0x801/0x841 refused\); thumbnail shows the scene, mean MSB 18 \(underexposed on defaults\).
- C4b on device \(combo10, t970-camera=193\): auto exposure converged in one step, coarse 1264 -&gt; 2526 lines, gain 1x -&gt; 3.5x, mean 24 -&gt; 77; recognisable room thumbnail.
- A CoreMediaIO camera extension \(tools/t970camerad\) is discovered by mediaserverd as an external camera; built-in cameras come only from the H9 ISP path, so apps do not use it yet.

### 完成条件

- Each sensor answers its model ID over the CCI.

### 当前范围

- No streaming, no CSIPHY/CSID/IFE yet; nothing in iPadOS consumes frames.

### 下一步

- C6: boot main with t970-camera=513 and the t970camerad addon \(scripts/build-t970camerad.py after the BlueTool script\); \[t970 camera c5\] d0/d1 show whether mediaserverd discovered the CMIO extension; then open FaceTime and pick T970 Front Camera \(docs/camera-notes.md section 5\).

### 证据

- `source`: [camcc GDSC/XO roots, CCI polled transfer, sensor power and chip-ID read.](https://github.com/rui12366B/UniXNU-gts7xlwifi/blob/88b34f97100a01aab4ea6b86dc9c748b2114c382/package/T970Camera.cpp)

## 镜像组装 {#packaging}

`implemented`

### 硬件与依赖

- iPadOS 17.7.11 21H461 kernelcache for prelink.

### 配置

- patches/xnu/series order.

### 操作步骤

- ./unixnu build kernel &amp;&amp; ./unixnu build payload --trust-cache &lt;file&gt;

### 开发经验

- The AdrenoMetal submodule is reset to the superproject pin on every kernel build, so local changes must be committed and pinned.
- New patches mount the audio HAL plug-in addon and add the shutdown failsafe; build scripts produce the audio plug-in and the Wi-Fi archive.
- New scripts build the Wi-Fi supplicant service, BlueTool, the camera viewer and Turnip addon variants; patches/xnu/t970-wifi-service-mount.patch mounts the service cache, exempts the two service executables by exact path from the Sandbox exec hook and launch constraints, defers the mount on a boot that rewrote it, and full-syncs the addon install.
- KeyStoreProbe provides native\_aks\_device\_id from /chosen/unique-chip-id for AppleKeyStoreState software key wrapping. t970-union-ro-create.patch lets a create on the read-only SystemOS union layer fall through to the layer below, so mkdir -p walks from / \(dhcpclient leases, SCPreferences\) no longer fail with EROFS. The Wi-Fi service mount patch also exempts bt-bin/bluetoothd, and the display build script lists the T970Pen service.
- Core carries are exported as git am patches; build-qcom-dwc3.py and build-t970camerad.py extend the addon chain; t970-union-statfs-fsid.patch accompanies the union patches.

### 完成条件

- Kernel, prelink and payload build.

### 当前范围

- Host patches in docs/host-patches are required.

### 下一步

- Upstream the host patches.

### 证据

- `source`: [Board patch order.](https://github.com/rui12366B/UniXNU-gts7xlwifi/blob/88b34f97100a01aab4ea6b86dc9c748b2114c382/patches/xnu/series)

## 诊断 {#diagnostics}

`device-verified`

### 硬件与依赖

- Boot log ring in a spare partition; DWC3 CDC-ACM debug console behind the MAX77705 MUIC switch.

### 配置

- qcom-usb-debug=1 qcom-usb-ctl=1 t970-qud-resume=1 t970-qud-retry=1; boot-progress=3.

### 操作步骤

- tools/read-boot-log.py from TWRP; on macOS read /dev/cu.usbmodem\*.

### 开发经验

- The USB-C D+/D- reach the SoC only through the MAX77705 analog switch, which iPadOS found open \(CONTROL1 0x3f\); writing COM\_USB \(0x09\) over the opcode mailbox brought up the console. The HS PHY needs QSCRATCH utmi-as-pipe and VBUS override.
- The boot log gained rows for audio \(\[audio ...\]\), Wi-Fi \(\[wifi-msg\]/\[wifi-log\]\), Bluetooth \(\[t970 bt\]\), sensors \(\[sensors hid\]\), camera \(\[t970 camera\], thumbnails via tools/camera-thumb.py\) and haptics; diag-export exports the persisted system log for offline reading.
- diag-export exports the persisted unified log plus bluetoothd/BlueTool log files; rows were added for UFS polling, Wi-Fi service mounts, Bluetooth serve counters and camera C5 streaming.
- The QcomXnuUsbDebug CDC console enumerates on the Mac \(qcom-usb-debug=1 t970-qud-retry=1\); the late retry now resumes the gated branch clocks itself. t970-ss=1 brings up the QMP USB3 PHY \(table from scripts/gen-qmp-sm8250-usb3.py, orientation from the MAX77705\) to step 104, but the link has trained at high speed so far; \[qud ss\] records the link state.
- QcomDwc3 device mode with Apple's USB device stack enumerates as an iPad: the Mac's usbmuxd and lockdownd answer and Finder lists it \(t970-usb=5\); the CDC console stays the fallback.

### 完成条件

- The Mac enumerates Qualcomm XNU Debug and streams the log from boot.

### 当前范围

- No Apple USB device stack \(Finder/usbmux\).

### 下一步

- Port an IOUSBDeviceFamily DWC3 controller \(UniXNU-alioth AliothUSBDevice\).

### 证据

- `device`: [Wi-Fi checkpoint row \[t970 wifi dom\] is composed live by the boot-log slot writer, so it survives a stalled monitor.](https://github.com/rui12366B/UniXNU-gts7xlwifi/blob/88b34f97100a01aab4ea6b86dc9c748b2114c382/docs/evidence/periph17-wifi.txt)
  Command: <code>TWRP: python3 tools/read-boot-log.py --port &lt;adb serial&gt; (periph17 payload)</code>. Revision: `cf6ed1702d3ddc2ace4cc988b982117e77f32c0b`.
- `device`: [QCOM XNU USB CDC ACM v1 and live rows on /dev/cu.usbmodem1101.](https://github.com/rui12366B/UniXNU-gts7xlwifi/blob/88b34f97100a01aab4ea6b86dc9c748b2114c382/docs/evidence/usb-console.txt)
  Command: <code>macOS: read /dev/cu.usbmodem* while the periph15 payload runs</code>. Revision: `781e3528e2d5e0dc0c9c6fa1e409f5a4bc1cf0e2`.
- `device`: [\[t970 muic\] CONTROL1 0x3f -&gt; 0x09; QCOM USB ACTIVE \(CDC-ACM up\).](https://github.com/rui12366B/UniXNU-gts7xlwifi/blob/88b34f97100a01aab4ea6b86dc9c748b2114c382/docs/evidence/periph15-bootlog.txt)
  Command: <code>TWRP: python3 tools/read-boot-log.py --port &lt;adb serial&gt; --out logs (after booting the periph15 payload, docs/menu/unixnu.toml)</code>. Revision: `781e3528e2d5e0dc0c9c6fa1e409f5a4bc1cf0e2`.

</div>
