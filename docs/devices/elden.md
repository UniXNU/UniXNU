# Lenovo Legion Y700 Gen 4 \(elden\)

[jerry-2009/UNIXNU_elden](https://github.com/jerry-2009/UNIXNU_elden)

<div v-pre>

Lenovo Legion Y700 Gen 4 format 2 migration. Phase 1 UEFI is device-verified; XNU, storage, display and touch remain bring-up work.

Source record: [porting.toml](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/porting.toml), `33b55083a0b61630f71478230f648606163115eb`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `host-verified` |
| [Firmware and boot](#firmware) | `device-verified` |
| [CPU and interrupts](#cpu) | `implemented` |
| [Memory and DMA](#memory) | `implemented` |
| [Storage and root](#storage) | `planned` |
| [Display](#display) | `planned` |
| [Input](#input) | `planned` |
| [GPU](#gpu) | `planned` |
| [Network](#network) | `not-applicable` |
| [Audio](#audio) | `not-applicable` |
| [Power](#power) | `planned` |
| [Image assembly](#packaging) | `device-verified` |
| [Diagnostics](#diagnostics) | `device-verified` |

## Configuration {#configuration}

`host-verified`

Components: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`, `DarwinBoot`.

### Hardware and dependencies

- Use the ARM64 and iPadOS 17.7.11 profiles supplied by UniXNU.
- Select the shared platform, CPU and DarwinBoot components.
- Provide an SM8750 profile until an official shared SoC repository exists.

### Configuration

- board.toml declares schema\_version = 2, soc\_source = sm8750 and os\_profile = ipados-17.7.11-21H461.
- The complete component list is explicit because profile arrays replace inherited arrays.
- Configuration and patch roots are ordered as ARM64, SoC, OS and device.
- soc/sm8750 supplies the transition profile and is referenced from feeds.toml.

### Procedure

- Run defconfig from a current UniXNU checkout.
- Inspect status JSON for profile order, component dependencies, patch order and output path.
- Replace the local SoC source with a reviewed UniXNU-sm8750-common commit before release.

### Development findings

- The repository was format 1 and did not select shared SoC or OS profiles.
- A public UniXNU-sm8750-common repository was not available during migration.
- Keeping a separate local SoC profile preserves parser validation without mislabelling unqualified hardware support as shared.
- Phase 2.0 resolved ARM64, local SM8750, iPadOS and device layers; the selected component order, 56 patches, 4 KiB page setting and separate format 2 output were checked with current UniXNU.
- Phase 2.1 keeps the XNU handoff and firmware memory description separate from the phase 1 dummy firmware DTB.
- Phase 2.2 resolved 57 patches after adding compile-time-disabled PMGR context required by the shared boot-progress patch. CONFIG\_XNU\_BOOT\_PROGRESS is disabled for the minimum kernel because that diagnostic layer currently requires UFS, owner-root and Virtio.
- Phase 2.5 proved XNU entry execution from the device and located the Apple-platform dependencies without adding a panic renderer: PE\_create\_console reads the iBoot video console handoff at 0x3C0F0000, and the kernel then runs through bsd\_init, IOKit and kext loading until AMFI panics with AMFI: not booted with security-mode-change-enabled. The earlier reading that a stage-16 kernel\_startup\_initialize\_upto entry never returns is withdrawn: those freezes were panics with the kprintf gate closed.

### Completion criteria

- board.toml resolves four ordered configuration layers.
- All selected components come from the UniXNU catalog and include their dependencies.
- No array field depends accidentally on inheritance.
- The SoC source is a reviewed remote commit and unixnu.lock records it.

### Current limits

- soc/sm8750 is local and is not yet a release-quality shared source.
- The first resolution pass selects only platform, CPU, AES, prelink and DarwinBoot components.

### Next action

- Phase 2.5 is complete on the kernel side: v51 \(cc739804217c3277bb07e4ce967381d5e1dd970eb46e9bb6637ebb83c5c668be\) reaches the root-device wait with no panic. Phase 3 starts with the storage entry: select and port a UFS component for the SM8750 controller so IOMedia/Apple\_HFS can match. Replace the local SM8750 source with a reviewed shared commit before release.

### Evidence

- `source`: [Schema 2 profile, component, kernel, device-tree and payload declarations.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/board.toml)
- `source`: [SM8750 transition source with the release replacement documented.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/feeds.toml)
- `source`: [Shared-profile-shaped SM8750 transition metadata.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/soc/sm8750/soc.toml)
- `source`: [Migration result, preserved phase 1 inputs and remaining release work.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/FORMAT2-MIGRATION.md)
- `host`: [2026-10-25: fresh defconfig, tree and status runs resolved four profiles, five pinned components, 56 patches and 4 KiB pages under a format 2 output directory separate from phase 1. The local SM8750 source remains unpinned for release.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2-STATUS.md)
  Command: <code>.venv/bin/python .cache/phase2-plan/UniXNU/unixnu status --json -D .</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.
- `host`: [2026-10-25: defconfig and status resolved five canonical components and 57 applied patches. The Command Line Tools host-shim build produced and prelinked the target kernel; release rebuilding still requires a full Xcode iPhoneOS SDK.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2.2-STATUS.md)
  Command: <code>PATH=.cache/phase2-plan/toolchain/bin:.venv/bin:$PATH .venv/bin/python .cache/phase2-plan/UniXNU/unixnu build kernel -D .</code>. Revision: `c91a2191fdf591a401a03027ed8b7fbfdbcad3a7`.
- `device`: [2026-11-01: the entry probe drew the full-width blue band at mid-screen and the device reset through PSCI after about two seconds, so the patched XNU entry instruction executed and the reset channel works.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2.5-STATUS.md)
  Command: <code>fastboot boot out/phase2.4/v3/elden-phase2.4-probe-boot.img</code>. Revision: `ef0e33d97c1a9571ec097e3ae37442efb8f4bb45`.
- `device`: [2026-11-01: console and initialize\_screen skipped; reset probes at 0x985d68 and 0x985d54 both froze while 0x985d44 reset, so the kernel halts inside the stage-16 kernel\_startup\_initialize\_upto call at 0x985d50.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2.5-STATUS.md)
  Command: <code>fastboot boot out/phase2.4/v45/elden-phase2.4-probe-boot.img</code>. Revision: `ef0e33d97c1a9571ec097e3ae37442efb8f4bb45`.
- `host`: [2026-11-01: the probe builder appends no segment in this mode; it overwrites the target instruction in place with a wait-then-PSCI-reset stub and optionally writes ret over named Apple handoffs. Every probe image passed verify\_phase2\_artifact.py with a v4 boot header and the 56 MiB FAT16 payload.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2.5-STATUS.md)
  Command: <code>.venv/bin/python scripts/make_entry_probe_kernel.py --output-dir out/phase2.4/v45 --reset-va 0xfffffff007985d68 --ret-at 0xfffffff0073bde3c --ret-at 0xfffffff007941dec</code>. Revision: `ef0e33d97c1a9571ec097e3ae37442efb8f4bb45`.
- `host`: [2026-11-01: the working tree at 718f75a adds --poke ADDRESS\|SYMBOL=WORD to the probe builder \(32-bit, code or data, prints the previous word and the owning segment\) on top of new segments/locate/symbol\_address helpers. The console candidate kernel is 54,050,920 bytes sha256 8a57a771b987477135692dc6b7a0c25c2a94587b8e0200e3a5934f284483de08 with eight pokes and no injected code; payload 5ebb049ef53865994e5870929397bddad4fb19c653116e77a4bfc6d757dc3f70 and image 0e3648192f2c2f3b1d6d01f75efa99b83b5f4d91fbcd06c07bd8790865fb41f9 passed verify\_phase2\_artifact.py with a v4 header, and darwinboot\_preflight accepted 16 segments and the ADT. Host evidence only; the image has not been booted.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2.5-STATUS.md)
  Command: <code>.venv/bin/python scripts/make_entry_probe_kernel.py --output-dir out/phase2.4/v49 --poke 0xfffffff0073bdf24=0x14000005 --poke 0xfffffff007941e0c=0x1400001d --poke 0xfffffff007941e90=0x52800041 --poke 0xfffffff0071fd970=0x00000000 --poke 0xfffffff0071fd978=0x073bb01c --poke 0xfffffff0071fd97c=0xfffffff0 --poke 0xfffffff0071652a4=0x00000001 --poke 0xfffffff007053aac=0x000d2970</code>. Revision: `718f75ae7215880274fda8c423858f68456509c2`.
- `device`: [2026-11-01: the poke-only console image printed kernel text on the device for the first time. The log runs from DarwinBoot and AppleCredentialManager through bsd\_init, IOKit, APFS, Skywalk, IONVRAM and IOSurface and ends in panic\(cpu 0 caller ...\): "AMFI: not booted with security-mode-change-enabled\\n" @ConfigurationSettings.cpp, preceded by Waiting on &lt;dict ... IOProviderClass ... IOMedia ... Apple\_HFS ...&gt;. So the kernel passes the stage-16 kernel\_startup\_initialize\_upto call; the earlier stage-16 halt reading was a panic with kprintf gated off.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2.5-STATUS.md)
  Command: <code>fastboot boot out/phase2.4/v49/elden-phase2.4-probe-boot.img</code>. Revision: `718f75ae7215880274fda8c423858f68456509c2`.
- `host`: [2026-11-01: v50 keeps the six console pokes and drops the startup\_debug and format-string pokes so the normal log scrolls, and pairs them with package/phase2.5-unixnu.toml whose xnu args add security-mode-change-enable=1 and amfi\_get\_out\_of\_my\_way=1 \(DarwinBoot copies the payload args into boot\_args-&gt;CommandLine\). Kernel 54,050,920 bytes sha256 f97e5f15b91630bbbad0dee002c352f122c7ff22747c6d2830148da63596deac, payload 2493716f6b8fbadd380c60bb236cc925cd90992c5c2fa6b1722af929903faf62, image d12b56ecd6e3e53fb23982ab09fbd0a26820501b8cb8d8edf1eacfa95e0cae70 passed verify\_phase2\_artifact.py \(--xnu-title\) and darwinboot\_preflight.py. Host evidence only; not yet booted.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2.5-STATUS.md)
  Command: <code>.venv/bin/python scripts/make_entry_probe_kernel.py --output-dir out/phase2.4/v50 --poke 0xfffffff0073bdf24=0x14000005 --poke 0xfffffff007941e0c=0x1400001d --poke 0xfffffff007941e90=0x52800041 --poke 0xfffffff0071fd970=0x00000000 --poke 0xfffffff0071fd978=0x073bb01c --poke 0xfffffff0071fd97c=0xfffffff0</code>. Revision: `718f75ae7215880274fda8c423858f68456509c2`.
- `device`: [2026-11-01: the AMFI security-mode-change gate passed, so the boot-arg channel from package/phase2.5-unixnu.toml through DarwinBoot to boot\_args-&gt;CommandLine is device-proven. The panic moved to "AMFI: No PMGR?\\n" @ConfigurationSettings.cpp:235: the developer-mode latch looks up the ApplePMGRNub service \(string 0xfffffff0042dde02, lookup at 0xfffffff004aaeb00\) and panics through the thunk at 0xfffffff004ac93e4 when the lookup returns NULL, which it does because elden publishes no power-management driver. The root-device wait text and the AMFI panic appear in the same screen tail.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2.5-STATUS.md)
  Command: <code>fastboot boot out/phase2.4/v50/elden-phase2.4-probe-boot.img</code>. Revision: `1724a7a6b8f87e8ecc5875a8586e7417e747a95c`.
- `host`: [2026-11-01: v51 keeps the six console pokes and adds 0xfffffff004aaecfc: mov x0,x21 \(0xaa1503e0\) -&gt; b 0xfffffff004aaec4c \(0x17ffffd4\), the epilogue of the developer-mode latch, so a missing ApplePMGRNub skips the latch instead of panicking. Kernel 54,050,920 bytes sha256 08def1c8206c04d1c20d6df273250a5ef04d72921c96112c6f863f84b8df7106, payload b912b4dfd0f86f2c92286049338756030f1592b0b2137523b4e79aa24fccc161, image cc739804217c3277bb07e4ce967381d5e1dd970eb46e9bb6637ebb83c5c668be passed verify\_phase2\_artifact.py \(--xnu-title "ELDEN 2.5 CONSOLE"\) and darwinboot\_preflight.py. Host evidence only; not yet booted.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2.5-STATUS.md)
  Command: <code>.venv/bin/python scripts/make_entry_probe_kernel.py --output-dir out/phase2.4/v51 --poke 0xfffffff0073bdf24=0x14000005 --poke 0xfffffff007941e0c=0x1400001d --poke 0xfffffff007941e90=0x52800041 --poke 0xfffffff0071fd970=0x00000000 --poke 0xfffffff0071fd978=0x073bb01c --poke 0xfffffff0071fd97c=0xfffffff0 --poke 0xfffffff004aaecfc=0x17ffffd4</code>. Revision: `1724a7a6b8f87e8ecc5875a8586e7417e747a95c`.
- `device`: [2026-11-01: v51 reaches the root-device wait loop and stops there with no panic. The screen repeats Waiting on &lt;dict ID="0"&gt;&lt;key&gt;IOProviderClass&lt;/key&gt;&lt;string ID="1"&gt;IOMedia&lt;/string&gt;&lt;key&gt;Content&lt;/key&gt;&lt;string ID="2"&gt;Apple\_HFS&lt;/string&gt;&lt;/dict&gt;, which means the kernel completed arm\_init, kernel\_bootstrap\_thread, bsd\_init, IOKit and kext loading, skipped the AMFI developer-mode latch with the 0xfffffff004aaecfc poke, and is now waiting for a block device that elden does not publish. Kernel-side phase 2.5 goal met; storage \(UFS\) is the phase 3 entry point. Display, the ArmCpu/GIC/timer checkpoints and the firmware-level console fix remain unproven.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2.5-STATUS.md)
  Command: <code>fastboot boot out/phase2.4/v51/elden-phase2.4-probe-boot.img</code>. Revision: `1724a7a6b8f87e8ecc5875a8586e7417e747a95c`.

## Firmware and boot {#firmware}

`device-verified`

Components: `DarwinBoot`.

### Hardware and dependencies

- mu\_wide\_platforms lenovo-y700g4 UEFI source and patched PMIC binaries.
- UniXNU, UniXNUDxe, DarwinBoot and EldenRamDiskDxe firmware modules.
- A 4 MiB FAT16 payload containing package/unixnu.toml.

### Configuration

- firmware.dsc points to PakalaPkg/PakalaNoSb.dsc.
- firmware.fd points to the DEBUG CLANGPDB SM8750\_EFI.fd.
- payload volume is ELDENRAM and loader is firmware.
- panic\_screen remains false because the phase 2 panic renderer is not integrated.

### Procedure

- Build the phase 1 image with scripts/build\_phase1.py.
- Run scripts/verify\_artifact.py against the FD and Android v3 image.
- Owner performs two RAM cold boots with fastboot boot.

### Development findings

- The vendor UFSDxe crashed before the menu, so it was removed from the phase 1 APRIORI, DSC and FDF.
- The embedded FAT payload avoids persistent storage and makes the menu independent of UFS.
- The same image reached the visible menu twice and returned to stock Android after reset.
- Phase 2.5 isolated the first kernel-side blocker: PE\_create\_console reads PA 0x3C0F0000, the iBoot video console handoff, and faults because this device never initialised it; replacing its first instruction with ret lets arm\_init reach machine\_startup. The firmware and payload do not need to change for this.
- DarwinBoot already forwards the UniXNU payload entry args verbatim into boot\_args-&gt;CommandLine, so kernel boot arguments \(debug flags, security-mode-change-enable, amfi\_get\_out\_of\_my\_way\) can be changed without rebuilding firmware.

### Completion criteria

- Firmware contains UniXNU, UniXNUDxe, DarwinBoot and the RAM payload driver.
- The payload config is readable and the menu accepts volume-key input.
- Two RAM boots produce the same visible checkpoint and do not modify persistent partitions.

### Current limits

- The verified firmware is phase 1 and does not contain a bootable XNU payload.
- The new format 2 firmware command is not yet switched from the project build script.
- The kernel console now works, but only through image-level pokes: DarwinBoot still hands over the raw physical framebuffer without initialize\_screen's physical-address marker, so the console patch has to be replaced by a firmware-side fix before release.

### Next action

- Use the current phase 1 image as the accepted baseline. Phase 2.5: keep the firmware unchanged and add the kernel-side GOP console fallback; the embedded payload channel and DarwinBoot hand-off are already device-verified.

### Evidence

- `source`: [Accepted phase 1 artifact and firmware/module inventory.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE1-STATUS.md)
- `source`: [Static FD, Android image and embedded FAT verification.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/scripts/verify_artifact.py)
- `device`: [2026-10-25: owner reported that the current image completed two RAM cold boots, reached the visible and operable UniXNU menu, and returned to stock Android.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2-STATUS.md)
  Command: <code>fastboot boot out/elden-phase1.img</code>. Revision: `dffc3020a85830d0d981a85871d9ab31aac5827d`.
- `device`: [Two owner-run RAM cold boots reached the UniXNU menu and returned to Android.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE1-HANDOFF.md)
  Command: <code>fastboot boot out/elden-phase1.img</code>. Revision: `c591b1a0a471f24978aba25c56c8f6ec9bd06668`.

## CPU and interrupts {#cpu}

`implemented`

Components: `ArmCpu`.

### Hardware and dependencies

- SM8750 MPIDRs 0x0, 0x100, 0x200, 0x300, 0x400, 0x500, 0x10000 and 0x10100.
- GICv3 distributor 0x16000000, redistributor base 0x16080000 and stride 0x40000.
- 19.2 MHz architectural timer and PSCI SMC conduit.

### Configuration

- The SoC DTSI declares eight CPU nodes, timebase-frequency = 19200000 and psci method = smc.
- The GIC node exports unixnu,adt-name = intc.
- The device defconfig enables ARM DT platform, ArmCpu, native timer and PAN.

### Procedure

- Compile dts/elden.dts with the SoC include path.
- Generate an ADT from the DTB and inspect /cpus, /psci and /arm-io/intc.
- Boot the smallest XNU payload and record the first CPU, GIC or timer failure.

### Development findings

- The board evidence documents the same eight MPIDR layout used by other SM8750 ports.
- The shared ADT generator emitted cpu0 as running and all other cores as waiting; ArmCpu does not probe secondary nubs unless sheng-smp is enabled.
- ArmCpu reads the GIC through /arm-io/intc and requires a complete two-range reg property.
- The old kernel argument set enabled armcpu-spi-ipi before elden had evidence that SGIs fail or that per-core SPI routing works. Phase 2.1 removed it from the single-boot-CPU milestone.
- Secondary CPU startup and both SGI and SPI IPI delivery are not device-verified for elden.
- v49 shows the boot CPU survives arm\_init, the vm/pmap bootstrap, bsd\_init, IOKit and kext loading until AMFI panics, so the earlier claim that it halts inside a stage-16 startup entry is withdrawn; ArmCpu, GIC and timer checkpoints are still not separately recorded because no kernel trace names them yet.
- Phase 2.5 explains why no probe ever printed kernel text: pexpert/arm/pe\_kprintf.c gates the whole kprintf body on disable\_serial\_output and disable\_kprintf\_output \(both default true\), and vcputc\_options gates painting on gc\_initialized and gc\_enabled \(gc\_enable runs only from initialize\_screen with kPEAcquireScreen\). PE\_init\_iokit calls PE\_init\_printf\(TRUE\) -&gt; vcattach just before the stage-16 call, so forcing PE\_create\_console into kPETextMode and mapping the GOP framebuffer brings the console up without rebuilding XNU.
- v50 device evidence shows AMFI passes its security-mode-change gate but then panics "AMFI: No PMGR?" at ConfigurationSettings.cpp:235, because the developer-mode latch needs an ApplePMGRNub service that elden does not publish. That latch is AMFI policy rather than a hardware description gap, so phase 2.5 skips it with a probe poke and leaves a real power-management driver to phase 3.

### Completion criteria

- The boot CPU reaches the ArmCpu checkpoint.
- GIC distributor and its own redistributor frame map successfully.
- Timer handling works before secondary cores or IPI transport are qualified.

### Current limits

- No elden XNU CPU, GIC or timer log exists yet.
- The eight-core topology is described, but SMP bring-up is not claimed.

### Next action

- Phase 2.5 kernel-side is proven: v51 boots to the root-device wait, so ArmDTPlatform, the boot CPU and the platform experts work. Add explicit ArmCpu, GIC and timer checkpoint output next \(armcpu-diagnostics=1 and the debug=0x14e bits\) before claiming the CPU area completion. Defer SPI IPI, SGI delivery, secondary startup and SMP qualification to separate device checks.

### Evidence

- `source`: [SM8750 CPU, PSCI, GICv3 and timer resources.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/soc/sm8750/dts/sm8750.dtsi)
- `source`: [Board CPU/GIC/timebase inventory and planned diagnostic sequence.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2-HANDOFF.md)
- `host`: [2026-10-25: independently decoded ADT contains the eight expected MPIDRs, cpu0 running and seven CPUs waiting, 19.2 MHz timebase, SMC PSCI, and GIC distributor/redistributor bases with 0x40000 stride. No device CPU checkpoint is claimed.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2.1-STATUS.md)
  Command: <code>.venv/bin/python scripts/phase2_1_audit.py --linux-dir .cache/elden-linux</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.
- `host`: [2026-10-25: the prelinked kernel exports ArmCpu probe/start, GIC distributor and timer-related symbols and ArmDTPlatform configure/createDeviceNubs symbols. Symbol presence is source evidence, not a device checkpoint.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2.2-STATUS.md)
  Command: <code>xcrun nm -g .cache/phase2-plan/UniXNU/out/elden/ipados-17.7.11-21H461/elden/kernel/kernel.macho</code>. Revision: `c91a2191fdf591a401a03027ed8b7fbfdbcad3a7`.

## Memory and DMA {#memory}

`implemented`

Components: `ArmDTPlatform`.

### Hardware and dependencies

- The owner-captured live elden FDT, including the 12 GiB RAM map, initrd and reserved-memory nodes.
- The pinned Linux 16 GiB variant and the elden UEFI static memory map.
- A conservative 256 MiB XNU handoff window in UEFI DXE conventional memory.

### Configuration

- dts/elden.dts declares one 256 MiB XNU handoff node at 0xC2400000.
- payload.dram\_size and payload.adt.owned\_memory\_size both request 0x10000000.
- dts/elden-firmware-memory.dts records the sanitised live 12 GiB RAM map, reserved-memory ranges and expected GOP framebuffer.
- The format 2 generator creates a 64-byte seed, CHRP NVRAM proxy and optional-input memory-map placeholders.

### Procedure

- Compile the hardware and firmware memory descriptions.
- Generate an ADT with the shared generator and decode it independently.
- Cross-check the XNU window against firmware RAM, reserved-memory and the pinned UEFI memory map.

### Development findings

- The previous \[0x80000000, 0x100000000\) candidate overlapped 44 recorded no-map reservations and was removed.
- The live FDT is 885,861 bytes with SHA-256 8a653a3e790f29bf2b0f3545135f06fe771360f31da3d37c04f648c26b95e26e and describes the current 12 GiB RAM map.
- The former A8000000+10000000 UEFI Kernel carveout overlaps the live initrd B74AC000-B7FFEE30 and is unsuitable for RAM-boot phase 2.
- C2400000+10000000 is covered by live RAM, avoids all live reservations and the initrd, and lies in UEFI DXE conventional memory.
- The flashed vendor FDT uses generic qcom,sun-qrd compatible strings but retains the elden 3K panel marker, 1904x3040 display and UFS path.
- The ADT has no optional RAMDisk, TrustCache or GPU addon placeholders because phase 2.1 has no matching inputs.
- The unique chip ID remains a local input and is not stored in the repository.

### Completion criteria

- The ADT contains exactly one continuous memory range.
- The range is covered by live firmware RAM and avoids recorded reservations, initrd, GOP and UEFI FD.
- DarwinBoot and the UEFI exit map confirm that same range is conventional memory before XNU entry.

### Current limits

- The raw live FDT remains local-only because it can contain device identifiers.
- Actual DarwinBoot ADT, boot\_args and allocated-window addresses remain runtime evidence.
- The live vendor tree and pinned 16 GiB source differ in RAM size and generic compatible strings; both are tracked separately.
- SMMU and cache policy are not complete.

### Next action

- Phase 2.3: preserve .cache/device/elden-live.fdt locally and rerun the live audit if firmware or boot mode changes; never commit the raw tree. Keep the phase 2 hardware ADT separate from the firmware FDT.

### Evidence

- `source`: [One 256 MiB XNU range in UEFI DXE conventional memory and board compatible values.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/dts/elden.dts)
- `source`: [Sanitised live 12 GiB RAM, reserved-memory and expected GOP framebuffer description.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/dts/elden-firmware-memory.dts)
- `source`: [Documented DRAM base, fragmentation risk and memory handoff constraints.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/porting-analysis.md)
- `device`: [2026-10-25: owner-connected device produced an 885,861-byte live FDT with SHA-256 8a653a3e790f29bf2b0f3545135f06fe771360f31da3d37c04f648c26b95e26e. The flashed vendor tree reports generic qcom,sun-qrd compatible values but contains elden panel markers, 1904x3040 display, 1d84000 UFS and a 12 GiB RAM map. Raw bytes remain local-only.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2.1-STATUS.md)
  Command: <code>/Users/jerry/Library/Android/sdk/platform-tools/adb shell su -c 'cp /sys/firmware/fdt /data/local/tmp/elden-live.fdt'</code>. Revision: `c91a2191fdf591a401a03027ed8b7fbfdbcad3a7`.
- `host`: [2026-10-25: the live FDT audit passed with C2400000+10000000. It is in live RAM and UEFI DXE conventional memory, avoids all live reserved-memory and the B74AC000-B7FFEE30 initrd, and reproduces the eight-CPU ADT. No XNU entry is claimed.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2.1-STATUS.md)
  Command: <code>.venv/bin/python scripts/phase2_1_audit.py --firmware-dtb .cache/device/elden-live.fdt --output-dir .cache/phase2.1-live</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.

## Storage and root {#storage}

`planned`

### Hardware and dependencies

- SM8750 UFS host at 0x1d84000 \(+0x3000\) and QMP PHY at 0x1d80000 \(+0x2000\), both described by the same-device Linux tree sm8750-lenovo-elden.dts and sm8750.dtsi pinned at bf96c3d4048973298ede78487177c6f1b4f6bc0f.
- Controller resources: GIC\_SPI 265 level-high, 8 GCC/RPMh clocks, GCC\_UFS\_PHY\_BCR, GCC\_UFS\_PHY\_GDSC, apps\_smmu stream 0x60, lanes-per-direction 2, ICE crypto@1d88000.
- PHY resources: RPMH\_CXO\_CLK, GCC\_UFS\_PHY\_PHY\_AUX\_CLK, TCSR\_UFS\_CLKREF\_EN, GCC\_UFS\_MEM\_PHY\_GDSC.
- Board supplies and reset: PHY vreg\_l1j\_0p91 and vreg\_l3g\_1p2, host vreg\_l17b\_2p5 \(1.3 A\) and vreg\_l1d\_1p2 \(1.2 A\), reset GPIO tlmm 215 active-low.
- 4 KiB logical-sector partition geometry and a root-volume UUID, both owner-supplied and read-only.

### Configuration

- The phase 1 defconfig disables Native UFS; no defconfig selects a storage transport yet.
- soc/sm8750/dts/sm8750.dtsi now declares ufs\_mem\_hc and ufs\_mem\_phy and dts/elden.dts enables both; only generator-exported properties are present \(reg, compatible, interrupt-parent, interrupts, dma-coherent, unixnu,adt-name\).
- Clocks, resets, power domains, SMMU and ICE stay comments until their provider nodes exist, because the ADT generator drops reference properties whose target is absent.
- Provider nodes still missing: GCC, RPMh, TCSR, apps\_smmu, TLMM and the PMIC regulators.

### Procedure

- Stage 1 \(host\): describe the controller, PHY and supplies, and verify the ADT export without building a new kernel.
- Stage 2 \(host\): the probe defconfig, payload config, ShengUfs substrate patch and build-sheng-ufs-probe.py exist; the probe-only kernel is not built yet because this host has Command Line Tools without Xcode.
- Stage 3 \(device\): owner RAM-boots the probe image with native-ufs-probe=N and native-ufs-diagnostics=1; record the GCC, controller and LUN0 results.
- Stage 4 \(later\): add the sheng PMGR instrument, native-ufs-root=1, userdata geometry and the verify-root probe before any mount.

### Development findings

- The same-device Linux tree is the authoritative inventory: UFS works on Linux 7.2.6 with F2FS, so controller and PHY are good hardware on elden.
- The distro repository tb322fc-linux \(c1fecc6\) is packaging only and its UFS patch is Linux ufshcd code, not portable to XNU.
- ShengUfs matches Apple platform-expert personality 2 unconditionally and reads fixed SM8750 constants \(host 0x1d84000, GCC 0x100000, SMMU 0x15000000, stream 0x60\) instead of the device tree; NativeUfs::inspect only reads the GCC UFS-MEM-GDSC and the driver never writes clocks.
- Exporting ufshc/ufsphy moves the ADT arm-io window from base 0x16000000 size 0x1000000 \(13,152-byte ADT\) to base 0x1000000 size 0x16000000 \(13,624-byte ADT\) because the UFS block at 0x1d80000 lies below the GIC at 0x16000000; arm-io/ufshc exports reg 0xd84000 and arm-io/ufsphy exports reg 0xd80000.
- UFSDxe crashed in phase 1 and was removed from the menu path, but a fastboot RAM boot does not need it: ABL must read boot.img from UFS before starting this image, so the controller and PHY are already running when XNU starts.
- There is no elden XNU UFS probe result yet; the phase 1 FAT payload intentionally bypasses persistent storage.
- Stage 2 code is in place: scripts/driver-patches/sheng-ufs-sm8750.patch applies to the pinned ShengUfs revision e2b32cc4, scripts/build-sheng-ufs-probe.py compiles the probe-only archive, configs/elden-ufs\_probe\_defconfig selects CONFIG\_XNU\_NATIVE\_UFS, board.toml \[kernel\].archives names the builder, and package/phase3-ufs-probe-unixnu.toml carries native-ufs-probe=2 without native-ufs-root or sheng-pmgr.
- The probe kernel is not built: this host has Command Line Tools only, so XNU compiles through the phase 2.2 shims \(.cache/phase2-plan/toolchain\) up to the assembler rule and sysproto regeneration and then stops; a complete Xcode install removes every shim.

### Completion criteria

- Controller and PHY initialize.
- Read-only capacity, GPT and known-block checks match the device.
- The configured OS volume mounts and launchd starts.

### Current limits

- Storage is not implemented; the first deliverable is a read-only probe, not a root device.
- The new arm-io window has only been generated and decoded on the host, not booted on the device.
- No owner-authored userdata image or root UUID exists, and no read-only GPT geometry has been captured.
- The probe keeps the phase 2.5 AMFI skip poke because elden still publishes no PMGR.
- No host build evidence exists for the probe kernel and no NativeUfs symbol has been checked yet; Stage 2 is code-complete but not verified.

### Next action

- Stage 2 resume: install a complete Xcode with the iPhoneOS SDK, run ".venv/bin/python .cache/phase2-plan/UniXNU/unixnu build kernel -D . -j 8", confirm NativeUfs symbols in the produced kernel, then build the probe image and hand it to the owner for a native-ufs-probe=2 RAM boot.

### Evidence

- `source`: [Storage addresses, missing root inputs and phase 1 bypass decision; implementation remains a later phase.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/porting-analysis.md)
- `source`: [Full SM8750 UFS inventory with Linux line references, driver reality, the arm-io window change and the four-stage probe plan.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE3-STORAGE.md)
- `host`: [2026-11-01: the hardware DTS with ufs\_mem\_hc and ufs\_mem\_phy compiles; the decompiled tree keeps reg 0x0 0x1d84000 0x0 0x3000, interrupts &lt;0 0x109 4&gt;, dma-coherent and status okay.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE3-STORAGE.md)
  Command: <code>.cache/dtc-src/dtc -I dts -O dtb -i soc/sm8750/dts -o /tmp/elden.dtb dts/elden.dts</code>. Revision: `b82bb65b4b3ba7508ae8ec9b18d0f36ec183da9f`.
- `host`: [2026-11-01: a decoupled ADT generated with scripts/unixnu/devicetree.py exports arm-io base 0x1000000 size 0x16000000, arm-io/ufshc reg 0xd84000/+0x3000, arm-io/ufsphy reg 0xd80000/+0x2000 and interrupts \(0, 265, 4\); the ADT grew from 13,152 to 13,624 bytes. No XNU boot is claimed.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE3-STORAGE.md)
  Command: <code>.venv/bin/python -c 'generate(Path("/tmp/elden.dtb"), merged_board_config, unique_chip_id="0x1")'</code>. Revision: `b82bb65b4b3ba7508ae8ec9b18d0f36ec183da9f`.

## Display {#display}

`planned`

### Hardware and dependencies

- 1904x3040 bonded dual-DSI panel with DSC.
- UEFI GOP framebuffer and splash reservation.
- SM8750 DPU/DSI/PHY and backlight sequencing.

### Configuration

- The phase 1 menu renders through UEFI GOP.
- XNU display and IOMobileFramebuffer components remain disabled.

### Procedure

- Keep display handoff on GOP for the first kernel milestone.
- Record a visible checkpoint after DarwinBoot.
- Add DPU/DSI only after kernel entry is stable.

### Development findings

- GOP display is device-verified in the UniXNU menu.
- No XNU display provider has been validated.
- The panel path remains a known high-risk cold-boot area.
- DarwinBoot fills boot\_args Video\[0..5\] from GOP and the device prints base 0xFC800000, row 7616, 1904x3040, depth 32. After the MMU is on the kernel only maps VirtualBase + \(PA - PhysicalBase\) inside the 256 MiB window, so the frame buffer is outside that window and later console writes need an explicit mapping or must happen before the switch.

### Completion criteria

- XNU paints a known pattern through a declared framebuffer handoff.
- Userland presentation and backlight transitions work.

### Current limits

- No DPU, DSI, DSC or panel node is present in the hardware DTS.
- GOP success is not counted as XNU display support.
- The current kernel console is hard-wired to the iBoot video console handoff, which elden does not have.

### Next action

- Make PE\_create\_console fall back to boot\_args Video\[0..5\] when the iBoot console handoff is absent; this is the next phase 2.5 step and the first visible kernel output.

### Evidence

- `source`: [GOP menu display was observed on hardware.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE1-STATUS.md)
- `source`: [Display topology, panel risk and GOP-first strategy.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/porting-analysis.md)

## Input {#input}

`planned`

### Hardware and dependencies

- Novatek SPI touch on SPI4 and GPIO 162 interrupt.
- Volume and power keys used by the UEFI menu.

### Configuration

- The phase 1 menu accepts volume-key input through UEFI.
- No XNU HID or Novatek transport is selected.

### Procedure

- Preserve UEFI key navigation as the bring-up input path.
- Inventory the touch firmware and protocol from read-only sources.
- Add QCOM GENI SPI, touch protocol and HID input after XNU boots.

### Development findings

- Volume-key menu input is device-verified.
- Touch has not been initialized by XNU.
- The panel and touch controller share board state that must be validated together.

### Completion criteria

- Touch coordinates map to the display.
- Contact IDs, releases and multi-touch remain stable.
- Buttons produce expected HID events in XNU.

### Current limits

- No touch component is selected.
- The NT36536 firmware and ABI inputs are not yet integrated.

### Next action

- Read the touch controller model and firmware version without modifying flash, then define the board transport.

### Evidence

- `source`: [Volume-key navigation reached the accepted menu.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE1-STATUS.md)
- `source`: [Novatek SPI wiring and input bring-up requirements.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/porting-analysis.md)

## GPU {#gpu}

`planned`

### Hardware and dependencies

- Adreno 830 / gen80000.
- GPU firmware, power votes, SMMU and display integration.

### Configuration

- GPU and Metal components are not selected.
- The first XNU milestone targets CPU/console progress only.

### Procedure

- Reach the XNU platform expert without GPU dependencies.
- Collect the GPU identity and firmware hashes.
- Select and implement a GPU component only after a display provider exists.

### Development findings

- The board has no validated XNU GPU path.
- Selecting SM8550 Adreno740 would misrepresent the Adreno 830 implementation scope.

### Completion criteria

- GPU submissions, fences and mapping work.
- A known image renders and Metal presentation is visible.

### Current limits

- GPU and Metal are explicitly out of the first milestone.

### Next action

- Keep GPU unselected until an SM8750-compatible component and firmware inputs exist.

### Evidence

- `source`: [Adreno 830 scope and exclusion from the first milestone.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/porting-analysis.md)

## Network {#network}

`not-applicable`

### Hardware and dependencies

- Wi-Fi is outside the current bring-up milestone.

### Configuration

- No Wi-Fi or MHI component is selected.

### Procedure

- Revisit after the USB or PCIe transport and firmware ownership are established.

### Development findings

- There is no verified Wi-Fi source or firmware path for elden.

### Completion criteria

- Not required for this milestone.

### Current limits

- Wi-Fi, Bluetooth and cellular are not implemented or claimed.

### Next action

- Open a separate network bring-up task when the base kernel and root volume are stable.

### Evidence

Collect evidence using the next action.

## Audio {#audio}

`not-applicable`

### Hardware and dependencies

- Audio is outside the current bring-up milestone.

### Configuration

- No ADSP, GLink, codec or audio component is selected.

### Procedure

- Revisit after platform, storage and display are stable.

### Development findings

- There is no elden audio log or firmware inventory.

### Completion criteria

- Not required for this milestone.

### Current limits

- Speakers, microphone and DSP routing are not implemented or claimed.

### Next action

- Open a separate audio bring-up task with DSP and codec inputs.

### Evidence

Collect evidence using the next action.

## Power {#power}

`planned`

### Hardware and dependencies

- PM8550-class PMIC, RPMh resources and device power domains.
- Volume and power key behavior.

### Configuration

- The first DTS selects only CPU and GIC resources.
- No platform power component is selected.

### Procedure

- Keep suspend and CPU power management disabled during first XNU entry.
- Record regulator and clock ownership.
- Add platform power only after the boot CPU reaches a stable checkpoint.

### Development findings

- UEFI power and key handling are verified only at the firmware layer.
- The selected OS profile does not supply sleep-disabled, so board.toml now adds it under \[adt.defaults.u32\].
- The final Phase 2.1 ADT was decoded with sleep-disabled=1.
- The XNU power topology is not complete.

### Completion criteria

- Declared power controls match readings.
- Sleep/resume or shutdown transitions restore dependent peripherals.

### Current limits

- Battery, charging, thermal and sleep are not implemented.

### Next action

- Phase 2.5: use armcpu-diagnostics=1 to observe boot-CPU quiesce/halt behavior. Audit RPMh ownership and keep suspend/secondary CPU power management out of initial qualification.

### Evidence

- `source`: [Board hardware and payload policy values.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/board.toml)
- `host`: [2026-10-25: independent ADT decode found /defaults sleep-disabled=1. This is source/host evidence, not a device suspend test.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2.1-STATUS.md)
  Command: <code>.venv/bin/python scripts/phase2_1_audit.py --linux-dir .cache/elden-linux</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.

## Image assembly {#packaging}

`device-verified`

### Hardware and dependencies

- iPad7,1 iPadOS 17.7.11 build 21H461 restore inputs.
- Target kernelcache, XNU 10063.141.1, DriverKit and TrustCache ABI inputs.
- Android v3 RAM-boot image, a 4 MiB phase 1 embedded FAT payload and a measured 56 MiB phase 2 candidate.

### Configuration

- The phase 1 image is produced by the project build script and verified against recorded hashes.
- Format 2 output is out/elden/ipados-17.7.11-21H461/elden/.
- The 2.2 prelink output is kernel/kernel.macho and its ADT sidecar; no phase 2 boot image is generated.

### Procedure

- Run scripts/build\_phase1.py for the accepted firmware path.
- Fetch the target IPSW components and build the patched 4 KiB XNU.
- Prelink against the pinned kernelcache and audit Mach-O, ABI, symbols and ADT.
- Package an isolated near-final-size payload only in Phase 2.3.

### Development findings

- The documented Phase 1 build was device-verified and the current procedure rebuilds and passes structural checks.
- The same current recipe produced 94b6a6315b04fc9d276bc15e9519107be292244380fc3bf139f5af6c96a3bb0a instead of the historical accepted image hash; byte-for-byte rebuild identity is not claimed, but the new image completed two owner RAM cold boots.
- The verified UniXNU third-party pin is intentionally retained for the accepted build.
- Phase 2.2 produced a 21,206,040-byte native kernel and a 54,050,816-byte prelinked kernel. The 57-patch sequence selects 30 executable Apple components, 7 kernel interfaces and 30 module entrypoints.
- A 58,720,256-byte FAT volume held the 54,063,968-byte kernel/config/ADT set with 3,734,016 bytes free and a byte-identical kernel readback; that 2026-10-25 volume was actually FAT32 \(mformat -F\) and is only mountable because 56 MiB clears the EnhancedFatDxe FAT16 cluster floor.
- EnhancedFatDxe derives the FAT type from the cluster count: a FAT32 BPB with fewer than 65,525 clusters returns EFI\_VOLUME\_CORRUPTED, so the 8 MiB FAT32 probe volume never became a SimpleFileSystem and UniXNU fell back to the built-in menu. The probe and payload volumes are now written as FAT16 by scripts/make\_payload.py, and scripts/verify\_phase2\_artifact.py recomputes the cluster count and BPB label for every candidate.
- The prelink report remains runtime\_qualified=false, abi\_qualified=false and loadable=false until device execution evidence exists.
- The embed\_payload images were device-verified on 2026-11-01: EnhancedFatDxe mounted both FAT16 volumes, UniXNU read \\EFI\\UniXNU\\unixnu.toml from the embedded payload and listed its entries next to the green checkpoint, so the kernel-field payload channel replaces the ramdisk channel for phase 2.3.
- The menu used the automatic scale \(MAX \(1, Width / 270\) = 7 on the 1904-pixel short side\) and truncated the footer; the scale is now pinned to 4 in package/phase2.3-unixnu.toml, which scripts/make\_phase2\_payload.py reads by default.
- 2026-11-01: the stage 2.3 embed-payload boot image 3dc8ae9611ec899ff14d50032ecd0ce2dd1035b3af9f9d3183bbab6cd41bcd93 reached the DarwinBoot hand-off in two RAM cold boots: the screen printed the ARM64, video and inputs-validated lines and the Entry.S green band, so EL1, the 256 MiB window at 0xB927C000 and ExitBootServices are device-verified. The green band is the loader breadcrumb; it does not prove that the XNU entry instruction ran.
- The stage 2.5 entry probe appends an r-x LC\_SEGMENT\_64 after Kernel.End, rewrites the entry B to branch into it and draws a blue band from boot\_args-&gt;Video before branching back to the original target; scripts/darwinboot\_preflight.py replays ParseKernel/AdtNode on the host \(16 segments, span 0x4310000, window 0x10000000\) and the 12,738,560-byte image a4ad1fc74abef35da9f947c350ff5763f2b8dea61da5adeee72aefcd0a67abf7 passes the stage 2.3 verifier with probe kernel a8f04b455996a4656a3055254c127e42f0676187c9550aa0b5fa57bbbe94e2d9.

### Completion criteria

- All format 2 build steps run from the resolved output directory.
- The payload contains the kernel, ADT and declared optional inputs.
- The boot image matches the ABL header and size limits.

### Current limits

- The three 2026-10-31 device failures \(two v3 probe boots, one v4 boot\) share the broken FAT32 probe volume, so they do not disprove the ABL ramdisk handoff; that channel is unproven rather than closed, and reopening it needs firmware that still contains UniXNURamDiskDxe. The embed\_payload channel that replaced it is device-verified; see docs/PHASE2.3-STATUS.md.
- The current 4 MiB board payload belongs to the accepted phase 1 build; the phase 2 payload is 56 MiB and is only used by the separate out/phase2.3 candidate.
- The 2.2 host build used Command Line Tools with an iPhone platform shim because full Xcode is absent; release rebuilding still requires the official Xcode/iPhoneOS SDK.
- The entry-probe kernel is a diagnostic artifact for out/phase2.4 only; it is not the release kernel and must not replace the phase 2.3 payload in a final image.

### Next action

- Phase 2.4 is device-verified; Phase 2.5 starts with the entry probe. The owner RAM-boots out/phase2.4/elden-phase2.4-probe-boot.img \(a4ad1fc74abef35da9f947c350ff5763f2b8dea61da5adeee72aefcd0a67abf7\) twice and chooses xnu: a blue band across the screen middle, drawn before the kernel image runs, proves the entry instruction executed, while the green band alone only proves Entry.S ran. Host rebuild and judgement rules are in docs/PHASE2.4-STATUS.md.

### Evidence

- `source`: [Reproducible phase 1 build commands, hashes and verification checklist.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE1-HANDOFF.md)
- `source`: [Preserved build inputs and remaining format 2 handoff work.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/FORMAT2-MIGRATION.md)
- `source`: [Phase 2 gates mapped to the official porting steps, capacity and memory constraints, and separate loader/kernel acceptance criteria; planning only, with no new device qualification.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2-HANDOFF.md)
- `source`: [Source-derived FDT, firmware RAM and reservation audit, decoded ADT checks, boot CPU parameter policy and remaining runtime evidence.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2.1-STATUS.md)
- `source`: [Pinned kernelcache, 57-patch XNU build, prelink inventory, symbol/4 KiB audits and measured 56 MiB payload fit.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2.2-STATUS.md)
- `host`: [Phase 2.0 established a rebuilt phase 1 baseline, preserved prior candidates, verified format 2 output isolation, and did not generate a phase 2 boot image.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2-STATUS.md)
  Command: <code>test -e .cache/phase2-plan/UniXNU/out/elden/ipados-17.7.11-21H461/elden/tree</code>. Revision: `dffc3020a85830d0d981a85871d9ab31aac5827d`.
- `host`: [2026-10-25: kernelcache f18b4df865405f2a287b84977d7aca745e056d656d9fc9df1662970ce2969de7 produced native kernel 02f216348851ba9ce70616430ff7607be9d3305cbc8b2ae1186f0e7d6b20fce7 and prelinked kernel.macho 65a3e799e1eb7f631a3b146dfc890ef5a8147c8fc613ee383a1665b398fb1ef9; runtime qualification remains false.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2.2-STATUS.md)
  Command: <code>PATH=.cache/phase2-plan/toolchain/bin:.venv/bin:$PATH .venv/bin/python .cache/phase2-plan/UniXNU/unixnu build kernel -D .</code>. Revision: `c91a2191fdf591a401a03027ed8b7fbfdbcad3a7`.
- `host`: [2026-10-25: a 58,720,256-byte FAT16 volume held all 54,063,968 payload bytes, left 3,734,016 bytes free, and round-tripped kernel.macho with SHA-256 65a3e799e1eb7f631a3b146dfc890ef5a8147c8fc613ee383a1665b398fb1ef9.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2.2-STATUS.md)
  Command: <code>mformat -C -F -T 114688 -v ELDENPH2 -i .cache/phase2.2/payload-fit-56m-20261025-223638.img :: &amp;&amp; mcopy -i .cache/phase2.2/payload-fit-56m-20261025-223638.img -s .cache/phase2-plan/UniXNU/out/elden/ipados-17.7.11-21H461/elden/payload/stage/EFI ::/</code>. Revision: `c91a2191fdf591a401a03027ed8b7fbfdbcad3a7`.
- `host`: [2026-11-01: FAT16 probe \(16,223 clusters\) and FAT16 56 MiB payload \(57,103 clusters\) replace the mformat -F FAT32 volumes EnhancedFatDxe rejects below 65,525 clusters. Probe image d6bf11a7a260856a525a831689def5b12ea028dedaca7dc2c78009bc6f0c6adf and final image 863d1b02ae7c7c5b7a7de0ac6cd8590aa36332dbf25540735ed4a264de8288e9 pass FAT type, BPB label, gzip\(shim+FD+payload\) and FV module checks; firmware is unchanged at 20b4b370d599aee9b081a283bd62faffe6ee66005d0de32967284d7d53adf245. Host evidence only; no device boot was performed.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2.3-STATUS.md)
  Command: <code>python3 scripts/make_phase2_probe.py &amp;&amp; python3 scripts/make_phase2_payload.py --from-image out/phase2.3/payload.img &amp;&amp; python3 scripts/build_phase2_image.py --kind probe --embed-payload &amp;&amp; python3 scripts/build_phase2_image.py --kind boot --embed-payload &amp;&amp; python3 scripts/verify_phase2_artifact.py --kind probe --image out/phase2.3/elden-phase2-embed-probe.img --shim out/phase2.3/shim-probe-embed.bin --embed-payload --payload out/phase2.3/probe.img &amp;&amp; python3 scripts/verify_phase2_artifact.py --kind boot --image out/phase2.3/elden-phase2-embed-boot.img --shim out/phase2.3/shim-boot-embed.bin --embed-payload --payload out/phase2.3/payload.img</code>. Revision: `5582de7371ea5d880235e05854f459c7b819b41a`.
- `host`: [2026-10-31: phase-2 firmware dc8a97dcf1369066114f0d10e50f0b163876b78a37796c29d7d468a7f6d9d9bf, 56 MiB payload b2c96e08f71bbd3f8a84018024b1dc048994b72c2a81b56789686e503da82f80, probe image 9ea0174c275e7ebb42d9727c770b7a06ae09a6d44df9e36657a667c8de7e051b and final image d52dd8e37fa0ef87c44b2b15207497e93ac6285ca874cf20e5a668c4226ecf99 passed v3 header, gzip\(shim+FD\), FV module and FAT/config checks. Host evidence only; no device boot was performed.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2.3-STATUS.md)
  Command: <code>python3 scripts/verify_phase2_artifact.py --kind probe --image out/phase2.3/elden-phase2-probe.img &amp;&amp; python3 scripts/verify_phase2_artifact.py --kind boot --image out/phase2.3/elden-phase2-boot.img</code>. Revision: `57e68be133c407ef9fa7dc6b4f10f1bd4cd3aedd`.
- `device`: [2026-11-01: owner booted both FAT16 embed-payload images; the menu showed config: \\EFI\\UniXNU\\unixnu.toml and the ELDEN 2.3 INITRD 56M entry from the embedded volume, so the kernel-field payload channel is device-verified. The menu scale was pinned to 4 afterwards.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2.3-STATUS.md)
  Command: <code>fastboot boot out/phase2.3/elden-phase2-embed-probe.img &amp;&amp; fastboot boot out/phase2.3/elden-phase2-embed-boot.img</code>. Revision: `509bc088641cb6d56d2a28b5526adb72dc88d51d`.
- `device`: [2026-11-01: two RAM cold boots of the scaled image 3dc8ae9611ec899ff14d50032ecd0ce2dd1035b3af9f9d3183bbab6cd41bcd93 printed DARWINBOOT: ARM64 va=0xFFFFFFF00427C000 pa=0xB927C000 args=0xBDB58000 entry=0xBC3ED488 owned=0x10000000, video base=0xFC800000 1904x3040 row 7616 depth 32, and inputs validated; exiting boot services, then the top 1/16 green band. The EL/input check passed and the window was allocated; no kernel output followed.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2.4-STATUS.md)
  Command: <code>fastboot boot out/phase2.3/elden-phase2-embed-boot.img (select xnu) twice</code>. Revision: `da1d077cf6856e3f2621785f4a612f2c5ebae260`.
- `host`: [2026-11-01: probe kernel 54,050,912 bytes a8f04b455996a4656a3055254c127e42f0676187c9550aa0b5fa57bbbe94e2d9 with entry 0xFFFFFFF0073ED488 branching to stub 0xFFFFFFF008588000 and back to 0xFFFFFFF0073EF05C; preflight accepted 16 segments and the ADT; FAT payload 065282a2... and image a4ad1fc7... passed the v4/FAT16/FV checks and match the probe bytes. Host evidence only; the probe image has not been booted.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2.4-STATUS.md)
  Command: <code>python3 scripts/make_entry_probe_kernel.py &amp;&amp; python3 scripts/make_phase2_payload.py --output out/phase2.4/payload.img --kernel out/phase2.4/probe/kernel.macho --adt out/phase2.4/probe/kernel.macho.adt --kernel-bytes 54050912 --kernel-sha256 a8f04b455996a4656a3055254c127e42f0676187c9550aa0b5fa57bbbe94e2d9 &amp;&amp; python3 scripts/build_phase2_image.py --kind boot --fd out/phase2.3/SILICIUM_UEFI.fd --payload out/phase2.4/payload.img --output out/phase2.4/elden-phase2.4-probe-boot.img --embed-payload --work out/phase2.4 &amp;&amp; python3 scripts/darwinboot_preflight.py --kernel out/phase2.4/probe/kernel.macho --adt out/phase2.4/probe/kernel.macho.adt &amp;&amp; python3 scripts/verify_phase2_artifact.py --kind boot --image out/phase2.4/elden-phase2.4-probe-boot.img --fd out/phase2.3/SILICIUM_UEFI.fd --shim out/phase2.4/shim-boot-embed.bin --report out/phase2.4/verify.json --embed-payload --payload out/phase2.4/payload.img --expect-kernel-bytes 54050912 --expect-kernel-sha256 a8f04b455996a4656a3055254c127e42f0676187c9550aa0b5fa57bbbe94e2d9</code>. Revision: `da1d077cf6856e3f2621785f4a612f2c5ebae260`.

## Diagnostics {#diagnostics}

`device-verified`

### Hardware and dependencies

- RAM-only owner-operated boot procedure.
- Build and artifact SHA-256 values.
- UEFI screen output and recovery path.

### Configuration

- verify\_artifact.py checks the FD, Android image and embedded FAT.
- build.json records artifact sizes and hashes.
- The phase 1 acceptance requires two consecutive cold boots.

### Procedure

- Build and verify the image.
- Owner runs fastboot boot twice and records the visible result.
- Power off and confirm stock Android before further work.

### Development findings

- The original accepted image is b56ef4b7e5a71382b8c279c4ee1560764fabd126ba37ac0fd6e495c80b9ec6e1.
- Earlier UFSDxe failure images are identified and must not be reused.
- Phase 2 requires separate kernel and DarwinBoot evidence.
- On 2026-10-25 a fresh phase 1 rebuild produced image SHA-256 94b6a6315b04fc9d276bc15e9519107be292244380fc3bf139f5af6c96a3bb0a and FD SHA-256 e5420517d55f4b638c07617a252d3a65c95cfb731584dcb10dd1d98bae412580. The build and prior local candidate were read-only preserved under .cache/phase2.0, and the owner then completed two RAM cold boots of the new image.
- Phase 2.1 host auditing now checks the ADT independently and records FDT, ADT, UEFI memory and boot argument sources under .cache/phase2.1 without replacing phase 1 artifacts.
- Phase 2.2 audits passed for 1,010 target objects, 7,730 prelink XML tags, iOS 17.0 deployment, 4 KiB TCR and the expected ArmDTPlatform/ArmCpu symbols. These are host-only checks.
- 2026-11-01: the two phase 2.3 embed-payload images both reached the UniXNU menu with the green payload checkpoint and printed config: \\EFI\\UniXNU\\unixnu.toml, so a visible menu no longer depends on the ABL ramdisk.
- 2026-11-01: choosing xnu on the stage 2.3 boot image printed the DarwinBoot ARM64/video/inputs-validated lines twice and painted the Entry.S green band. This is loader evidence; the entry probe now supplies the first kernel-side checkpoint.

### Completion criteria

- Every claimed checkpoint has a reproducible command, image hash and visible result.
- Failures reach a diagnosable screen or log instead of a silent hang.

### Current limits

- The DarwinBoot hand-off and ADT acceptance are device-verified, but there is no XNU console or serial log yet; the entry probe is the first kernel-side checkpoint and still needs a device result.
- The generated hardware ADT input is a minimal host candidate. The separate firmware memory description contains the source-derived reservation map, but neither is a live device FDT.
- The historical accepted image bytes are absent from the workspace, so they cannot be booted or byte-compared locally.

### Next action

- Owner RAM-boots out/phase2.4/elden-phase2.4-probe-boot.img \(a4ad1fc74abef35da9f947c350ff5763f2b8dea61da5adeee72aefcd0a67abf7\) twice and chooses xnu; the blue band is the XNU entry checkpoint. Phase 2.5 then narrows any hang with arm\_init, ArmDTPlatform and cpu\_init probes; see docs/PHASE2.4-STATUS.md.

### Evidence

- `source`: [Recorded phase 1 artifact sizes and SHA-256 values.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/out/build.json)
- `source`: [The elden Linux reference now matches soc/sm8750/soc.toml at h0cheung/tb322fc-linux-kernel 6f97250ead155fc3b980856323e99a4623dae73d.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/unixnu.lock)
- `host`: [2026-10-25: a fresh phase 1 rebuild completed in 6:46 and passed static Android v3, shim, FD, embedded FAT and module checks. Image SHA-256 was 94b6a6315b04fc9d276bc15e9519107be292244380fc3bf139f5af6c96a3bb0a and FD SHA-256 was e5420517d55f4b638c07617a252d3a65c95cfb731584dcb10dd1d98bae412580; no device boot was performed.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2-STATUS.md)
  Command: <code>.venv/bin/python scripts/build_phase1.py --skip-submodules --crypto-path $PWD/.cache/phase1/basecrypto</code>. Revision: `dffc3020a85830d0d981a85871d9ab31aac5827d`.
- `device`: [2026-10-25: owner confirmed two RAM cold boots of image 94b6a6315b04fc9d276bc15e9519107be292244380fc3bf139f5af6c96a3bb0a; both reached the usable UniXNU menu and stock Android resumed after exit. This evidence covers phase 1 only.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2-STATUS.md)
  Command: <code>fastboot boot out/elden-phase1.img</code>. Revision: `dffc3020a85830d0d981a85871d9ab31aac5827d`.
- `host`: [2026-10-25: DTC 1.8.1-gf99e3af0 generated a 1,557-byte DTB with SHA-256 60316b6d4e753610610126d691f6d39ba54edd21e9b02875ec034e81e27a4371; round-trip inspection found the expected compatible strings, CPU MPIDRs, PSCI, GICv3, timer and DRAM data.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2-STATUS.md)
  Command: <code>.cache/dtc-src/dtc -I dts -O dtb -i soc/sm8750/dts -o /tmp/elden-phase2.0.dtb dts/elden.dts</code>. Revision: `f99e3af0ecb67a9085478a9b8ddbcc25aa64931d`.
- `host`: [2026-10-25: live-FDT audit produced a 13,152-byte ADT. Independent checks passed for C2400000+10000000 RAM/reservation/initrd coverage, UEFI DXE conventional memory, framebuffer, eight MPIDRs, one running boot CPU, GIC, timer, CHRP NVRAM, optional placeholders and sleep-disabled=1. Report: .cache/phase2.1-live/audit.json.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2.1-STATUS.md)
  Command: <code>.venv/bin/python scripts/phase2_1_audit.py --firmware-dtb .cache/device/elden-live.fdt --output-dir .cache/phase2.1-live</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.
- `host`: [2026-10-25: native kernel audited as arm64/iOS 17 with 4 KiB TG0 and TG1; 1,010 target objects passed; the pinned prelink XML lexer accepted 7,730 tags. No device checkpoint is claimed.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2.2-STATUS.md)
  Command: <code>python3 scripts/audit-xnu-kernel.py build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/mach.development.bcm2837.unstripped.noctf &amp;&amp; python3 scripts/audit-xnu-objects.py &amp;&amp; python3 scripts/check-prelink-xml.py ../kernel/kernel.macho</code>. Revision: `c91a2191fdf591a401a03027ed8b7fbfdbcad3a7`.
- `device`: [2026-11-01: owner booted both phase 2.3 embed-payload images; each reached the UniXNU menu with the green payload checkpoint, printed config: \\EFI\\UniXNU\\unixnu.toml and listed the ELDEN 2.3 INITRD 56M entry, proving the payload HOB, BlockIo, FAT16 mount and config discovery chain on device.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE2.3-STATUS.md)
  Command: <code>fastboot boot out/phase2.3/elden-phase2-embed-probe.img &amp;&amp; fastboot boot out/phase2.3/elden-phase2-embed-boot.img</code>. Revision: `509bc088641cb6d56d2a28b5526adb72dc88d51d`.
- `device`: [Screen capture of the phase 2.3 56 MiB payload menu before the scale fix: config read from the embedded volume, entries ELDEN 2.3 INITRD 56M and Restart, green checkpoint band, footer truncated at scale 7.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/assets/phase23-menu-embed-20261101.jpg)
  Command: <code>fastboot boot out/phase2.3/elden-phase2-embed-boot.img</code>. Revision: `509bc088641cb6d56d2a28b5526adb72dc88d51d`.
- `device`: [Two cold boots reached DISPLAY OK, INPUT OK, config loaded and menu shown.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/docs/PHASE1-STATUS.md)
  Command: <code>fastboot boot out/elden-phase1.img</code>. Revision: `c591b1a0a471f24978aba25c56c8f6ec9bd06668`.
- `device`: [Screen capture shows the rendered UniXNU menu on the tablet.](https://github.com/jerry-2009/UNIXNU_elden/blob/33b55083a0b61630f71478230f648606163115eb/assets/phase1-menu-20261025.jpg)
  Command: <code>fastboot boot out/elden-phase1.img</code>. Revision: `c591b1a0a471f24978aba25c56c8f6ec9bd06668`.

</div>
