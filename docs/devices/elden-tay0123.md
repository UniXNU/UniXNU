# Lenovo Legion Y700 Gen 4 \(TAY0123\)

[TAY0123/UNIXNU_elden](https://github.com/TAY0123/UNIXNU_elden)

<div v-pre>

Lenovo Legion Y700 Gen 4 format 2 migration. Phase 1 UEFI is device-verified; XNU, storage, display and touch remain bring-up work.

Source record: [porting.toml](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/porting.toml), `d2759a06f3713ed97c347824a4f100ce83269949`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `host-verified` |
| [Firmware and boot](#firmware) | `device-verified` |
| [CPU and interrupts](#cpu) | `implemented` |
| [Memory and DMA](#memory) | `implemented` |
| [Storage and root](#storage) | `host-verified` |
| [Display](#display) | `implemented` |
| [Input](#input) | `planned` |
| [GPU](#gpu) | `host-verified` |
| [Network](#network) | `planned` |
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

- 2026-11-06 host: source GOP console kernel/archives/prelink completed; separate read-only UFS root-check archive compiled with inherited identity DMA and LUN selection. TWRP/Linux EFI prototype and userdata/ESP design remain hardware-unverified. Details and bounded evidence in docs/NIGHT-BRINGUP-20261106.md; no stock index change or device write.
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

- `host`: [2026-11-06 host: source GOP console kernel/archives/prelink completed; separate read-only UFS root-check archive compiled with inherited identity DMA and LUN selection. TWRP/Linux EFI prototype and userdata/ESP design remain hardware-unverified. Details and bounded evidence in docs/NIGHT-BRINGUP-20261106.md; no stock index change or device write. Revision plus local working-tree patches.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/NIGHT-BRINGUP-20261106.md)
  Command: <code>.venv/bin/python third_party/UniXNU/unixnu build kernel -D . -j4</code>. Revision: `33b55083a0b61630f71478230f648606163115eb`.
- `source`: [Schema 2 profile, component, kernel, device-tree and payload declarations.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/board.toml)
- `source`: [SM8750 transition source with the release replacement documented.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/feeds.toml)
- `source`: [Shared-profile-shaped SM8750 transition metadata.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/soc/sm8750/soc.toml)
- `source`: [Migration result, preserved phase 1 inputs and remaining release work.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/FORMAT2-MIGRATION.md)
- `host`: [2026-10-25: fresh defconfig, tree and status runs resolved four profiles, five pinned components, 56 patches and 4 KiB pages under a format 2 output directory separate from phase 1. The local SM8750 source remains unpinned for release.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2-STATUS.md)
  Command: <code>.venv/bin/python .cache/phase2-plan/UniXNU/unixnu status --json -D .</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.
- `host`: [2026-10-25: defconfig and status resolved five canonical components and 57 applied patches. The Command Line Tools host-shim build produced and prelinked the target kernel; release rebuilding still requires a full Xcode iPhoneOS SDK.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2.2-STATUS.md)
  Command: <code>PATH=.cache/phase2-plan/toolchain/bin:.venv/bin:$PATH .venv/bin/python .cache/phase2-plan/UniXNU/unixnu build kernel -D .</code>. Revision: `c91a2191fdf591a401a03027ed8b7fbfdbcad3a7`.
- `device`: [2026-11-01: the entry probe drew the full-width blue band at mid-screen and the device reset through PSCI after about two seconds, so the patched XNU entry instruction executed and the reset channel works.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2.5-STATUS.md)
  Command: <code>fastboot boot out/phase2.4/v3/elden-phase2.4-probe-boot.img</code>. Revision: `ef0e33d97c1a9571ec097e3ae37442efb8f4bb45`.
- `device`: [2026-11-01: console and initialize\_screen skipped; reset probes at 0x985d68 and 0x985d54 both froze while 0x985d44 reset, so the kernel halts inside the stage-16 kernel\_startup\_initialize\_upto call at 0x985d50.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2.5-STATUS.md)
  Command: <code>fastboot boot out/phase2.4/v45/elden-phase2.4-probe-boot.img</code>. Revision: `ef0e33d97c1a9571ec097e3ae37442efb8f4bb45`.
- `host`: [2026-11-01: the probe builder appends no segment in this mode; it overwrites the target instruction in place with a wait-then-PSCI-reset stub and optionally writes ret over named Apple handoffs. Every probe image passed verify\_phase2\_artifact.py with a v4 boot header and the 56 MiB FAT16 payload.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2.5-STATUS.md)
  Command: <code>.venv/bin/python scripts/make_entry_probe_kernel.py --output-dir out/phase2.4/v45 --reset-va 0xfffffff007985d68 --ret-at 0xfffffff0073bde3c --ret-at 0xfffffff007941dec</code>. Revision: `ef0e33d97c1a9571ec097e3ae37442efb8f4bb45`.
- `host`: [2026-11-01: the working tree at 718f75a adds --poke ADDRESS\|SYMBOL=WORD to the probe builder \(32-bit, code or data, prints the previous word and the owning segment\) on top of new segments/locate/symbol\_address helpers. The console candidate kernel is 54,050,920 bytes sha256 8a57a771b987477135692dc6b7a0c25c2a94587b8e0200e3a5934f284483de08 with eight pokes and no injected code; payload 5ebb049ef53865994e5870929397bddad4fb19c653116e77a4bfc6d757dc3f70 and image 0e3648192f2c2f3b1d6d01f75efa99b83b5f4d91fbcd06c07bd8790865fb41f9 passed verify\_phase2\_artifact.py with a v4 header, and darwinboot\_preflight accepted 16 segments and the ADT. Host evidence only; the image has not been booted.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2.5-STATUS.md)
  Command: <code>.venv/bin/python scripts/make_entry_probe_kernel.py --output-dir out/phase2.4/v49 --poke 0xfffffff0073bdf24=0x14000005 --poke 0xfffffff007941e0c=0x1400001d --poke 0xfffffff007941e90=0x52800041 --poke 0xfffffff0071fd970=0x00000000 --poke 0xfffffff0071fd978=0x073bb01c --poke 0xfffffff0071fd97c=0xfffffff0 --poke 0xfffffff0071652a4=0x00000001 --poke 0xfffffff007053aac=0x000d2970</code>. Revision: `718f75ae7215880274fda8c423858f68456509c2`.
- `device`: [2026-11-01: the poke-only console image printed kernel text on the device for the first time. The log runs from DarwinBoot and AppleCredentialManager through bsd\_init, IOKit, APFS, Skywalk, IONVRAM and IOSurface and ends in panic\(cpu 0 caller ...\): "AMFI: not booted with security-mode-change-enabled\\n" @ConfigurationSettings.cpp, preceded by Waiting on &lt;dict ... IOProviderClass ... IOMedia ... Apple\_HFS ...&gt;. So the kernel passes the stage-16 kernel\_startup\_initialize\_upto call; the earlier stage-16 halt reading was a panic with kprintf gated off.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2.5-STATUS.md)
  Command: <code>fastboot boot out/phase2.4/v49/elden-phase2.4-probe-boot.img</code>. Revision: `718f75ae7215880274fda8c423858f68456509c2`.
- `host`: [2026-11-01: v50 keeps the six console pokes and drops the startup\_debug and format-string pokes so the normal log scrolls, and pairs them with package/phase2.5-unixnu.toml whose xnu args add security-mode-change-enable=1 and amfi\_get\_out\_of\_my\_way=1 \(DarwinBoot copies the payload args into boot\_args-&gt;CommandLine\). Kernel 54,050,920 bytes sha256 f97e5f15b91630bbbad0dee002c352f122c7ff22747c6d2830148da63596deac, payload 2493716f6b8fbadd380c60bb236cc925cd90992c5c2fa6b1722af929903faf62, image d12b56ecd6e3e53fb23982ab09fbd0a26820501b8cb8d8edf1eacfa95e0cae70 passed verify\_phase2\_artifact.py \(--xnu-title\) and darwinboot\_preflight.py. Host evidence only; not yet booted.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2.5-STATUS.md)
  Command: <code>.venv/bin/python scripts/make_entry_probe_kernel.py --output-dir out/phase2.4/v50 --poke 0xfffffff0073bdf24=0x14000005 --poke 0xfffffff007941e0c=0x1400001d --poke 0xfffffff007941e90=0x52800041 --poke 0xfffffff0071fd970=0x00000000 --poke 0xfffffff0071fd978=0x073bb01c --poke 0xfffffff0071fd97c=0xfffffff0</code>. Revision: `718f75ae7215880274fda8c423858f68456509c2`.
- `device`: [2026-11-01: the AMFI security-mode-change gate passed, so the boot-arg channel from package/phase2.5-unixnu.toml through DarwinBoot to boot\_args-&gt;CommandLine is device-proven. The panic moved to "AMFI: No PMGR?\\n" @ConfigurationSettings.cpp:235: the developer-mode latch looks up the ApplePMGRNub service \(string 0xfffffff0042dde02, lookup at 0xfffffff004aaeb00\) and panics through the thunk at 0xfffffff004ac93e4 when the lookup returns NULL, which it does because elden publishes no power-management driver. The root-device wait text and the AMFI panic appear in the same screen tail.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2.5-STATUS.md)
  Command: <code>fastboot boot out/phase2.4/v50/elden-phase2.4-probe-boot.img</code>. Revision: `1724a7a6b8f87e8ecc5875a8586e7417e747a95c`.
- `host`: [2026-11-01: v51 keeps the six console pokes and adds 0xfffffff004aaecfc: mov x0,x21 \(0xaa1503e0\) -&gt; b 0xfffffff004aaec4c \(0x17ffffd4\), the epilogue of the developer-mode latch, so a missing ApplePMGRNub skips the latch instead of panicking. Kernel 54,050,920 bytes sha256 08def1c8206c04d1c20d6df273250a5ef04d72921c96112c6f863f84b8df7106, payload b912b4dfd0f86f2c92286049338756030f1592b0b2137523b4e79aa24fccc161, image cc739804217c3277bb07e4ce967381d5e1dd970eb46e9bb6637ebb83c5c668be passed verify\_phase2\_artifact.py \(--xnu-title "ELDEN 2.5 CONSOLE"\) and darwinboot\_preflight.py. Host evidence only; not yet booted.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2.5-STATUS.md)
  Command: <code>.venv/bin/python scripts/make_entry_probe_kernel.py --output-dir out/phase2.4/v51 --poke 0xfffffff0073bdf24=0x14000005 --poke 0xfffffff007941e0c=0x1400001d --poke 0xfffffff007941e90=0x52800041 --poke 0xfffffff0071fd970=0x00000000 --poke 0xfffffff0071fd978=0x073bb01c --poke 0xfffffff0071fd97c=0xfffffff0 --poke 0xfffffff004aaecfc=0x17ffffd4</code>. Revision: `1724a7a6b8f87e8ecc5875a8586e7417e747a95c`.
- `device`: [2026-11-01: v51 reaches the root-device wait loop and stops there with no panic. The screen repeats Waiting on &lt;dict ID="0"&gt;&lt;key&gt;IOProviderClass&lt;/key&gt;&lt;string ID="1"&gt;IOMedia&lt;/string&gt;&lt;key&gt;Content&lt;/key&gt;&lt;string ID="2"&gt;Apple\_HFS&lt;/string&gt;&lt;/dict&gt;, which means the kernel completed arm\_init, kernel\_bootstrap\_thread, bsd\_init, IOKit and kext loading, skipped the AMFI developer-mode latch with the 0xfffffff004aaecfc poke, and is now waiting for a block device that elden does not publish. Kernel-side phase 2.5 goal met; storage \(UFS\) is the phase 3 entry point. Display, the ArmCpu/GIC/timer checkpoints and the firmware-level console fix remain unproven.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2.5-STATUS.md)
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

- 2026-11-06 prerequisites: bounded current-boot FDT/original-initrd bootconfig inheritance and a conventional-memory report mode are compiled in the31744-byte EFI application. Synthetic metadata bounds/CRC, priority and full-initrd cleanup/retry pass in AAVMF; the accepted FD is unchanged. See docs/PREREQUISITES-20261106.md.
- 2026-11-06 host: source GOP console kernel/archives/prelink completed; separate read-only UFS root-check archive compiled with inherited identity DMA and LUN selection. TWRP/Linux EFI prototype and userdata/ESP design remain hardware-unverified. Details and bounded evidence in docs/NIGHT-BRINGUP-20261106.md; no stock index change or device write.
- 2026-11-05 offline inventory of the accepted FD confirms EldenPayloadDxe present and UniXNURamDiskDxe absent. Actual old/new BootShim bytes were emulated through both copy and in-place branches: x3=8 MiB versus 56 MiB, x0 preserved, FD copy identical. The newer FD regression is not hardware-isolated. See docs/OFFLINE-PAYLOAD-20261105.md.
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

- `device`: [The MacBook captured arm\_init, the macOS Base System mount, PID 1 exec, and the full libSystem.B.dylib panic with the no-dyld-cache reason. Bootloader fastboot enumerated after the panic without a host reset command. The no-host timeout remains unverified.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Boot installed r37 Recovery on slot A and monitor USB through the panic</code>. Revision: `88289ea663c239d9aa77894c090df18fd24283da`.
- `device`: [Base revision plus the Recovery panic poll and timeout changes. The r37 RAM image streamed the retained log from arm\_init over XNU USB. XNU acknowledged reboot-fastboot and bootloader fastboot enumerated on slot A. Fastboot accepted the signed boot\_a image and its installed menu listed nine entries.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Capture Recovery over XNU CDC, request reboot-fastboot, and install the signed r37 image to boot_a</code>. Revision: `b5ec68e1ee8823cdf191f2ff3cada262225f6b86`.
- `device`: [Base revision plus the live FDT handoff and macOS serial name fix. Bootloader fastboot accepted the write to active slot A. The installed UEFI CDC console listed all nine entries and completed a USB-triggered round trip to fastboot. The slot check returned open=Unsupported after the FDT transport was restored.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Flash signed r36 to boot_a and run list, slot-status and fastboot over USB</code>. Revision: `50e90091fcce705c918115e013e62865bcc9a54b`.
- `device`: [macOS enumerated /dev/cu.usbmodemELDEN\_UEFI1. With underscore handling in the host script, all nine entries listed. Read-only slot status returned open=Not Found, and Recovery handed off without an XNU CDC device appearing during capture. No flash write was performed.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Use the MacBook controller to list entries, run slot-status and start recovery-usb on the r35 RAM image</code>. Revision: `50e90091fcce705c918115e013e62865bcc9a54b`.
- `host`: [Base revision plus the USB management changes. UEFI, XNU, packed payload and MacBook controller checks passed. The tablet was visible over Linux USB ADB, then did not enumerate on the MacBook in bootloader fastboot. RAM transfer and on-device USB management remain pending.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Build the Elden USB menu driver, UniXNU firmware, Recovery USB management kernel, and combined RAM image</code>. Revision: `b622c0d7339e0ed1f4094699f786b94ed5a4e3ba`.
- `host`: [Base revision plus the direct firmware action. Mock UFS, both slot directions on copies of real GPTs, write bounds, rollback and embedded image readback passed. Native tablet qualification remains pending.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Build and test EldenBootSlot.efi and verify the combined native slot RAM image</code>. Revision: `bd467b20d19a3d62ab962a6ef79b308a842aba14`.
- `device`: [The desktop launcher delegates slot writes to Linux qbootctl. The installed protected helper reported slot B with UFS boot LUN 2. The Qualcomm reference firmware uses both GPT slot state and the UFS boot LUN. A standalone Elden UEFI writer remains unqualified.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Inspect the tablet desktop launcher and read protected slot status over SSH</code>. Revision: `3c414c39606b4889d97a64ac0c241e7e3c1e719e`.
- `device`: [Full readback matched the signed USB console image built from this base and the Recovery USB patch. Original boot\_b matched before and after. Both partitions returned to read-only and slot B remained active with UFS boot LUN 2. The new Recovery USB entry has yet to boot.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Flash the Recovery USB Console image to inactive boot_a over SSH</code>. Revision: `06cc83d15dc86b40c492fea2267eb0a0d02fbe64`.
- `device`: [The full boot\_a readback matched the signed SHA-256. Original boot\_b matched before and after the write. Both boot partitions returned to read-only and slot B remained active with UFS boot LUN 2. Boot testing of the new image is pending.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Flash the Recovery without Ignition and Linux console retention image to inactive boot_a over SSH</code>. Revision: `35e753350164a82cfe2f67b4c7f589c1bb1f20d7`.
- `device`: [Full boot\_a readback matched the signed combined image. Original boot\_b SHA-256 and active B/UFS boot LUN 2 were confirmed, and both partitions were read-only after the write. Boot of the combined image remains pending.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Flash combined diagnostics to inactive boot_a and verify both boot partitions over SSH</code>. Revision: `3847c50b48becb05d08f7cb8438ee039eb9b8200`.
- `host`: [Raw-v4 image passed DarwinBoot preflight, full FAT comparison, Linux/DTB/menu readback and slot A AVB verification. Both diagnostic payloads are present in the combined image.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Package and verify the combined Recovery PID 1 and Linux EFI diagnostic image</code>. Revision: `3847c50b48becb05d08f7cb8438ee039eb9b8200`.
- `device`: [After the reported menu failures, the tablet was reachable on the original slot B Linux path. Active B and UFS boot LUN 2 matched. The journal recorded no executed slot-switch request, pstore was empty, and both boot partition digests matched.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Inspect active slot, systemd slot-service journal, pstore and boot partition hashes over SSH</code>. Revision: `8c7e7d1667575429f3b0ca41ac678cef867ee4fd`.
- `host`: [Base revision plus the diagnostic option. After the owner reported both Linux menu entries returning, a raw-v4 RAM image with EFI debug logging, framebuffer early console, and panic hold passed host verification. No hardware diagnostic result yet.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>prepare-elden-linux-efi.py --diagnostics and verify_phase2_artifact.py --raw-packed-payload</code>. Revision: `8dad62f706e8fbcce1cf2f49683467a12fe3980d`.
- `device`: [2026-11-11: raw-v4 signed boot\_a matches the full partition readback. Original boot\_b digest, active slot B and UFS boot LUN 2 were verified. The first boot of the replacement is pending.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Write inactive boot_a from slot B Linux and verify full readbacks over SSH</code>. Revision: `f2aa1a017da59b08d99bbd8c398285349a6edd2b`.
- `host`: [Base revision plus raw ARM64 boot packaging and packed FAT driver. After the owner reported a return to fastboot on slot A, the host built an Android v4 image with stock A header metadata, a raw ARM64 payload smaller than working Linux B and LZ4 chunks decoded by DXE. Host FAT, decoder and AVB checks passed. Tablet boot of the new candidate is pending.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>build_phase2_image.py --embed-payload --raw-boot-reference and verify_phase2_artifact.py --raw-packed-payload</code>. Revision: `134edd73729109491cd3e7ace5bcbd013d40adfc`.
- `device`: [2026-11-11: full inactive boot\_a readback matches the signed dual-boot image. Original boot\_b SHA-256 and active B/UFS boot LUN 2 were confirmed. Boot of the installed slot A image remains unverified.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Read back boot_a and boot_b from the running Linux system</code>. Revision: `d6a8f4280f791fffc27957d475707e48c5b5321a`.
- `host`: [Base revision plus Linux EFI and menu changes. The Linux EFI payload uses the FDT passed in x0. The signed slot A candidate passes a one-time slot request to the installed Linux rootfs. Host artifact and service command checks passed.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>prepare-elden-linux-efi.py and verify_phase2_artifact.py</code>. Revision: `96bb7e12ea6effc4a41d55a36c65167cec671fc7`.
- `device`: [The original Linux boot in slot B reported active B and UFS boot LUN 2. Slot A selection dry-run passed. The installed UniXNU slot service skipped the normal Linux boot without a request property. Menu-driven slot selection remains unverified.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>tb322fc-select-boot-slot status and select a --dry-run</code>. Revision: `96bb7e12ea6effc4a41d55a36c65167cec671fc7`.
- `host`: [The Adreno 830 GMU probe RAM image passed embedded verification with the existing firmware and BootShim.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>build and verify the Elden Adreno 830 GMU probe</code>. Revision: `a6190077af83a6e02645a6b02a70f86c43696e3e`.
- `host`: [The v4 image embeds the existing firmware and a 224 MiB FAT payload. The Linux entry uses UniXNU's ARM64 EFI-stub handoff and installs the matching Elden DTB.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>verify the combined Recovery and Linux RAM image</code>. Revision: `cf9b0ba7c8a000b3ed4f4199707095ffd9b5fa0c`.
- `host`: [The candidate keeps the accepted firmware. The BootShim and embedded FAT carry the new 128 MiB payload.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>verify the Recovery Framebuffer Test RAM image</code>. Revision: `1241b6e42385bf4ad7afc9c48f3f39df0a5ab322`.
- `host`: [The PID 1 Trace RAM image uses the accepted firmware and a byte-identical BootShim.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>compare the PID 1 Trace BootShim and verify the embedded image</code>. Revision: `0a0254a5efb72452bdb4622b567b5727bb2a69fb`.
- `device`: [The Elden bootloader accepted the new SMP RAM image with the previously verified firmware and byte-identical BootShim.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>fastboot boot elden-macos26-4k-recovery-smp-aff2-ram.img</code>. Revision: `ed8f382d36ea0d3ebaa3a1582aa8e03410c9645d`.
- `host`: [The result-display candidate embeds the same verified Elden firmware and a byte-identical BootShim with the manual probe menu.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>verify_phase2_artifact.py on elden-macos26-4k-ufs-result-ram.img</code>. Revision: `95e9740ea6da4727a0119d878a51f93b563305bf`.
- `device`: [Elden bootloader fastboot accepted the transfer and RAM boot of the UIC retest image. The packaged firmware and BootShim are byte-identical to the first UFS probe.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>fastboot boot elden-macos26-4k-ufs-uic-ram.img</code>. Revision: `623c1f937c423c039c11991ff5e2a9150bb0542c`.
- `host`: [Elden's opt-in firmware menu action uses PSCI SYSTEM\_RESET2 with reset type 0x80010001 and cookie 0x2. The host checked the SMC arguments and returned errors, firmware linked, FAT payload verified, and the MacBook image checksum matched.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Build and verify out/elden-fastboot/elden-fastboot-ram.img</code>. Revision: `c62bf12595f9a86c1b7282cf12d5af40b441fdac`.
- `device`: [2026-11-10: the tablet accepted the temporary image and left fastboot. The owner selected the new menu action. USB re-enumerated as elden\_prc\_wifi with is-userspace: no. EFI serial invocation was not exercised.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>fastboot boot elden-fastboot-ram.img, select Reboot to Fastboot, verify fastboot getvar product and is-userspace</code>. Revision: `c62bf12595f9a86c1b7282cf12d5af40b441fdac`.
- `host`: [2026-11-06 prerequisites: bounded current-boot FDT/original-initrd bootconfig inheritance and a conventional-memory report mode are compiled in the31744-byte EFI application. Synthetic metadata bounds/CRC, priority and full-initrd cleanup/retry pass in AAVMF; the accepted FD is unchanged. See docs/PREREQUISITES-20261106.md. Source revision plus local working-tree changes.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PREREQUISITES-20261106.md)
  Command: <code>.venv/bin/python scripts/build-payload-loader.py</code>. Revision: `33b55083a0b61630f71478230f648606163115eb`.
- `host`: [2026-11-06 host: source GOP console kernel/archives/prelink completed; separate read-only UFS root-check archive compiled with inherited identity DMA and LUN selection. TWRP/Linux EFI prototype and userdata/ESP design remain hardware-unverified. Details and bounded evidence in docs/NIGHT-BRINGUP-20261106.md; no stock index change or device write. Revision plus local working-tree patches.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/NIGHT-BRINGUP-20261106.md)
  Command: <code>.venv/bin/python third_party/UniXNU/unixnu build kernel -D . -j4</code>. Revision: `33b55083a0b61630f71478230f648606163115eb`.
- `host`: [2026-11-05 offline inventory of the accepted FD confirms EldenPayloadDxe present and UniXNURamDiskDxe absent. Actual old/new BootShim bytes were emulated through both copy and in-place branches: x3=8 MiB versus 56 MiB, x0 preserved, FD copy identical. The newer FD regression is not hardware-isolated. See docs/OFFLINE-PAYLOAD-20261105.md. Source revision plus uncommitted local packaging changes.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/OFFLINE-PAYLOAD-20261105.md)
  Command: <code>.venv/bin/python scripts/build_offline_ufs_packet.py --fd out/phase3/old-fd-verified.bin --source-payload out/phase3/payload-fat16.img --kernel third_party/UniXNU/out/elden/ipados-17.7.11-21H461/elden-ufs_probe/kernel/kernel.macho</code>. Revision: `33b55083a0b61630f71478230f648606163115eb`.
- `source`: [Accepted phase 1 artifact and firmware/module inventory.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE1-STATUS.md)
- `source`: [Static FD, Android image and embedded FAT verification.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/scripts/verify_artifact.py)
- `device`: [2026-10-25: owner reported that the current image completed two RAM cold boots, reached the visible and operable UniXNU menu, and returned to stock Android.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2-STATUS.md)
  Command: <code>fastboot boot out/elden-phase1.img</code>. Revision: `dffc3020a85830d0d981a85871d9ab31aac5827d`.
- `device`: [Two owner-run RAM cold boots reached the UniXNU menu and returned to Android.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE1-HANDOFF.md)
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

- Two-core cross-affinity startup and interrupt delivery are device-verified. The Eight-core Test shows timer and IPI delivery on CPU 7. The aggregate and other secondary rows remain uncaptured in the eight-core run, and suspend/resume remains unqualified.

### Next action

- Capture the full Eight-core Test summary with seven running secondaries. Verify step 7, successful PSCI CPU\_ON, and timer and IPI delivery for each secondary.

### Evidence

- `host`: [The Adreno 830 GMU probe uses the single-core Recovery trace entry with the GPU firmware check enabled.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>build and verify the Elden Adreno 830 GMU probe</code>. Revision: `a6190077af83a6e02645a6b02a70f86c43696e3e`.
- `host`: [The framebuffer test requests one CPU, retains the PID 1 trace, and preserves the kernel affinity overlays.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>build the Recovery Framebuffer Test with the Elden bootstrap wrapper</code>. Revision: `1241b6e42385bf4ad7afc9c48f3f39df0a5ab322`.
- `host`: [The separate PID 1 trace entry requests one CPU and retains the Aff2 fixes in the kernel.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>build the PID 1 Trace image with the Elden bootstrap wrapper</code>. Revision: `0a0254a5efb72452bdb4622b567b5727bb2a69fb`.
- `device`: [Logical CPU 7 received two timer interrupts and one IPI. The photo does not capture the aggregate or the other secondary rows. After 218 seconds at launchd exec it shows one exec, zero exits, and no starts for the watched Recovery services.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Select Eight-core Test on elden-macos26-4k-recovery-smp-aff2-ram.img</code>. Revision: `1540fdbd208c22f6bc7d6d3929316889640d0954`.
- `device`: [The photos show one running secondary, CPU 1 step 7, fail=0, PSCI result 0, and rising timer and IPI counters. Observed MPIDR 0x80010000 matches requested affinity 0x10000. The paired BaseSystem mounted and XNU recorded one launchd exec and zero exits with no later service at the 31-second sample.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Select CPU Aff2 Test on elden-macos26-4k-recovery-smp-aff2-ram.img</code>. Revision: `1540fdbd208c22f6bc7d6d3929316889640d0954`.
- `host`: [The rebuilt reset vector preserves 24-bit MPIDR affinity and ArmCpu checks the hardware affinity. All 64 expected/observed Elden affinity pairs matched or rejected correctly. Secondary execution remains pending.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>build-elden-macos26-bootstrap.py --output-name for the Aff2 candidate and llvm-objdump reset audit</code>. Revision: `ed8f382d36ea0d3ebaa3a1582aa8e03410c9645d`.
- `host`: [2026-11-11: the two-core image selects MPIDRs 0x0 and 0x100 under the current reset mask. The kernel includes SMP stage, timer and IPI counters. The embedded image and MacBook copy were verified. Secondary CPU execution remains pending.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>decode Recovery ADT and verify elden-macos26-4k-recovery-smp2-ram.img</code>. Revision: `9053888e29bac20c0160efcaa7b2d75a6d969778`.
- `source`: [SM8750 CPU, PSCI, GICv3 and timer resources.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/soc/sm8750/dts/sm8750.dtsi)
- `source`: [Board CPU/GIC/timebase inventory and planned diagnostic sequence.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2-HANDOFF.md)
- `host`: [2026-10-25: independently decoded ADT contains the eight expected MPIDRs, cpu0 running and seven CPUs waiting, 19.2 MHz timebase, SMC PSCI, and GIC distributor/redistributor bases with 0x40000 stride. No device CPU checkpoint is claimed.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2.1-STATUS.md)
  Command: <code>.venv/bin/python scripts/phase2_1_audit.py --linux-dir .cache/elden-linux</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.
- `host`: [2026-10-25: the prelinked kernel exports ArmCpu probe/start, GIC distributor and timer-related symbols and ArmDTPlatform configure/createDeviceNubs symbols. Symbol presence is source evidence, not a device checkpoint.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2.2-STATUS.md)
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
- The current format 2 generator creates a 256-byte seed, CHRP NVRAM proxy and optional-input memory-map placeholders. The audit also accepts the older 64-byte seed.

### Procedure

- Compile the hardware and firmware memory descriptions.
- Generate an ADT with the shared generator and decode it independently.
- Cross-check the XNU window against firmware RAM, reserved-memory and the pinned UEFI memory map.

### Development findings

- 2026-11-07: device read-check succeeds with a 6GiB high-address window. EFI reports a 13GiB free run at0x8c0000000. Installed loader accepts at most8GiB; current bootstrap-table reserve is sized for6GiB. Fresh512MiB test Data expands exactly under the actual C decoder.
- 2026-11-06 prerequisites: offline FDT/EFI intersection planning and readonly EFI extent reporting are prepared. A historical FDT suggests a high-address4GiB candidate but dynamic reservations and a same-boot EFI map remain unqualified; the256MiB XNU probe configuration was not enlarged.
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

- Keep6GiB for the next hardware test; separately qualify any larger window and do not advertise a flat16GiB.

### Evidence

- `host`: [2026-11-10: Elden ADT audit accepts the current nonzero 256-byte seed and the prior 64-byte format. The exact macOS UFS candidate reached arm\_init in QEMU with 256 MiB owned. Five matching windows are available in the static Elden descriptions. Runtime tablet memory allocation remains unverified.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>scripts/phase2_1_audit.py --unixnu-dir ../UniXNU and observe_macos26_kernel.py arm_init with a 256 MiB QEMU window</code>. Revision: `abdae5c70bc1d7eb8eea28a045ae3544881274e2`.
- `host`: [Base revision plus local working-tree patches. 2026-11-07: device read-check succeeds with a 6GiB high-address window. EFI reports a 13GiB free run at0x8c0000000. Installed loader accepts at most8GiB; current bootstrap-table reserve is sized for6GiB. Fresh512MiB test Data expands exactly under the actual C decoder.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/STARTUP-USB-CANDIDATE-20261107.md)
  Command: <code>python edl_work/audit_startup_candidates.py (Y700 work repository)</code>. Revision: `33b55083a0b61630f71478230f648606163115eb`.
- `host`: [2026-11-06 prerequisites: offline FDT/EFI intersection planning and readonly EFI extent reporting are prepared. A historical FDT suggests a high-address4GiB candidate but dynamic reservations and a same-boot EFI map remain unqualified; the256MiB XNU probe configuration was not enlarged. Source revision plus local working-tree changes.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PREREQUISITES-20261106.md)
  Command: <code>.venv/bin/python scripts/build-payload-loader.py</code>. Revision: `33b55083a0b61630f71478230f648606163115eb`.
- `source`: [One 256 MiB XNU range in UEFI DXE conventional memory and board compatible values.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/dts/elden.dts)
- `source`: [Sanitised live 12 GiB RAM, reserved-memory and expected GOP framebuffer description.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/dts/elden-firmware-memory.dts)
- `source`: [Documented DRAM base, fragmentation risk and memory handoff constraints.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/porting-analysis.md)
- `device`: [2026-10-25: owner-connected device produced an 885,861-byte live FDT with SHA-256 8a653a3e790f29bf2b0f3545135f06fe771360f31da3d37c04f648c26b95e26e. The flashed vendor tree reports generic qcom,sun-qrd compatible values but contains elden panel markers, 1904x3040 display, 1d84000 UFS and a 12 GiB RAM map. Raw bytes remain local-only.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2.1-STATUS.md)
  Command: <code>/Users/jerry/Library/Android/sdk/platform-tools/adb shell su -c 'cp /sys/firmware/fdt /data/local/tmp/elden-live.fdt'</code>. Revision: `c91a2191fdf591a401a03027ed8b7fbfdbcad3a7`.
- `host`: [2026-10-25: the live FDT audit passed with C2400000+10000000. It is in live RAM and UEFI DXE conventional memory, avoids all live reserved-memory and the B74AC000-B7FFEE30 initrd, and reproduces the eight-CPU ADT. No XNU entry is claimed.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2.1-STATUS.md)
  Command: <code>.venv/bin/python scripts/phase2_1_audit.py --firmware-dtb .cache/device/elden-live.fdt --output-dir .cache/phase2.1-live</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.

## Storage and root {#storage}

`host-verified`

Components: `ShengUfs`.

### Hardware and dependencies

- SM8750 UFS host at 0x1d84000 \(+0x3000\) and QMP PHY at 0x1d80000 \(+0x2000\), both described by the same-device Linux tree sm8750-lenovo-elden.dts and sm8750.dtsi pinned at bf96c3d4048973298ede78487177c6f1b4f6bc0f.
- Controller resources: GIC\_SPI 265 level-high, 8 GCC/RPMh clocks, GCC\_UFS\_PHY\_BCR, GCC\_UFS\_PHY\_GDSC, apps\_smmu stream 0x60, lanes-per-direction 2, ICE crypto@1d88000.
- PHY resources: RPMH\_CXO\_CLK, GCC\_UFS\_PHY\_PHY\_AUX\_CLK, TCSR\_UFS\_CLKREF\_EN, GCC\_UFS\_MEM\_PHY\_GDSC.
- Board supplies and reset: PHY vreg\_l1j\_0p91 and vreg\_l3g\_1p2, host vreg\_l17b\_2p5 \(1.3 A\) and vreg\_l1d\_1p2 \(1.2 A\), reset GPIO tlmm 215 active-low.
- 4 KiB logical-sector partition geometry and a root-volume UUID, both owner-supplied and read-only.

### Configuration

- elden-ufs\_probe\_defconfig selects the read-only observation build; elden-ufs\_rootcheck\_defconfig builds the complete read-only IOBlockStorageDevice interface.
- The SM8750 board patch keeps explicit LUN0/4 selection and validates inherited SMMUv2 identity DMA without changing the admitted route.
- Root-check uses ARMADA\_BACKUP for the existing LUN4 test window; production root partition and manifest remain separate configuration work.
- The macOS 26.5 Elden build opts into read-only legacy queue takeover on LUN 0 after verifying the firmware clock and identity DMA state.

### Procedure

- Build on the configured Mac using the selected source-kernel headers and pinned storage reference.
- Qualify the original and concrete 190-slot ABI, link the complete kernel, then audit the final candidate and real class-registration path.
- Package the accepted FD with a 56 MiB payload, preserve exact stock rollback values, and perform independent signature/content/entry checks.
- Verify the macOS read-only UFS diagnostics on hardware before publishing or mounting Recovery media.

### Development findings

- 2026-11-07: LUN0/ipados root header read is device-verified. New AVB-kernel-pinned complete-image and per-block verification, live readonly media ancestry bridge, SystemOS union and RAM Data startup candidate compile/link and host checks pass; new mount/startup remains untested on hardware.
- 2026-11-06 prerequisites: official21H461 OS/SystemOS and original trust inputs are verified. Native readonly APFS inspection supplies actual filesystem UUIDs. A9381609472-byte raw root layout passes file readback and the actual RootLayout parser with file callbacks; Data, runtime policies and real root-target kernel remain pending. No hardware disk access.
- 2026-11-06: standalone GPL UEFI UFS backend and current/previous stage2 applications compile; original/session suites and independent SHA/header/torn-update tests pass. Actual AAVMF probe platform rejection and RAM FAT child failure/cleanup/retry pass; no tablet UFS operation is claimed. See docs/UFS-STAGE2-20261106.md.
- The full root-check kernel 07d4df1d… compiled/prelinked successfully; the diagnostic derivative is 3fd40e9f….
- 190 original/concrete slots, 23 concrete overrides, 11 original imports and actual C2/D2 were qualified without replacing the storage class with stubs.
- The final derivative executes to the real registered original storage class in QEMU using the actual menu arguments; class sizes are 0xd8/0x90/0x88.
- The compressed EFI loader decoded all complete assets in AAVMF, and a neutral-debug DarwinBoot test build passed EBS to the same XNU console and UFS registration gate. This is not a test of the entire vendor firmware.
- The exact accepted DarwinBoot binary needs its platform graphics debug sink in AAVMF; its observed fault is before EBS, unlike a proved hardware handoff failure.
- 2026-11-06 hardware: corrected arm-io/AAPL,phandle ADT and fixed-address SMMU loads reach read-only LUN4 GPT/block checks. LUN0/ipados source configuration is added; block publication and root mounting remain pending.

### Completion criteria

- Controller and PHY initialize.
- Read-only capacity, GPT and known-block checks match the device.
- The configured OS volume mounts and launchd starts.
- A verified APFS install on the former Android data extent boots with writes bounded to the selected partition.

### Current limits

- LUN4 read-only capacity/GPT/block checks passed on hardware; LUN0/ipados publication and root mount remain unverified.
- The existing 2 GiB ARMADA\_BACKUP is an empty test window, not an installed iPadOS root.
- The standalone compressed recovery branch still needs TWRP hardware boot, USB, touch and FBE checks.
- The new standalone EFI UFS backend needs tablet qualification. ADB slot transport has only root/su model tests. The actual external bundle and 3ffa745d signed bootstrap are packaged, with menu/reset and QEMU-ADT XNU-path evidence. Tablet UFS and physical power-loss behavior remain unqualified.

### Next action

- Test the new signed manual startup candidate, retain the 6GiB read-check as the device-qualified fallback, and inspect verified-image/media/mount stages before changing policy.
- Use the Recovery PID 1 Trace image to distinguish post-mount startup from storage discovery. Service startup and the Recovery GUI remain pending.

### Evidence

- `host`: [The Adreno 830 probe prelink passed the 326-slot UFS ABI and retained the 15 paired Recovery modules.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>build and verify the Elden Adreno 830 GMU probe</code>. Revision: `a6190077af83a6e02645a6b02a70f86c43696e3e`.
- `host`: [The Linux entry uses root=PARTLABEL=rootfs. The paired macOS Recovery entry and its ADT match the framebuffer test.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>inspect the installed-rootfs Linux entry</code>. Revision: `cf9b0ba7c8a000b3ed4f4199707095ffd9b5fa0c`.
- `host`: [The read-only UFS policy, root contract, Recovery module set, and 326-slot storage ABI match.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>compare the combined framebuffer and UFS prelink with the PID 1 trace</code>. Revision: `1241b6e42385bf4ad7afc9c48f3f39df0a5ab322`.
- `host`: [The read-only UFS policy and Recovery module set match. The 326-slot storage ABI and PAC metadata passed.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>compare the Recovery trace prelink against the Aff2 candidate</code>. Revision: `0a0254a5efb72452bdb4622b567b5727bb2a69fb`.
- `host`: [The rebuilt read-only UFS companion matches the deployed BaseSystem contract. The 326-slot storage ABI and pointer authentication metadata passed.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>prelink the rebuilt UFS driver into the Aff2 test image</code>. Revision: `ed8f382d36ea0d3ebaa3a1582aa8e03410c9645d`.
- `source`: [The opt-in ISC tail manifest uses the existing read-only root parser and excludes the manifest block from all data windows. The UFS build binds the local seed while retaining the paired BaseSystem contract and a bounded volatile overlay.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
- `device`: [The device write was bounded to the unused ISC extent and last block of macosroot. The seed, alternate manifest, original BaseSystem image and both GPT copies passed readback.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Elden maintenance RAM boot with verified ISC seed and alternate manifest</code>. Revision: `176e49e93c140fa829e14c7635b18979ebfee684`.
- `device`: [2026-11-11: the physical Elden photo records Root mounted and launchd exec with PID 1, one start and zero recorded exits. At 93 seconds there were no later recorded Recovery service starts.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>select Elden macOS 26.5 - Recovery Root in image 15fe0bd0…</code>. Revision: `030cc6450b0bbaa6979b1370a3accf303dcf1563`.
- `device`: [2026-11-11: installed the paired 1.471 GiB BaseSystem only on the 4 GiB macosroot partition. Verified the data before committing the manifest, the complete image after cache flush, and both unchanged GPT copies. Native APFS mount remains pending.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>offline maintenance RAM boot and full macosroot SHA-256 readback after blockdev --flushbufs</code>. Revision: `767f7bd7f60897742f596fd6ae96d5d0add654b3`.
- `device`: [Physical Elden reported ELDEN UFS PROBE PASS after a successful native read of LUN 0 LBA 1. The GPT header CRC matched the saved Linux readback from after repartitioning. Recovery media publication and mount are pending.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>select Elden macOS 26.5 - UFS Read-only Probe in image 0adacbc5…</code>. Revision: `117ed6a1fc62f473f5c43a6d271dff22e3ced75a`.
- `host`: [The 1.471 GiB BaseSystem image and manifest fit macosroot and match the compiled UFS driver. The available ISC seed differs from its compiled contract, so the host image is BaseSystem-only.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>prepare_macos26_ufs_root.py and full OS window readback</code>. Revision: `117ed6a1fc62f473f5c43a6d271dff22e3ced75a`.
- `device`: [The owner photo shows XNU at the Apple\_HFS root-device wait after APFS registration, with no visible panic. The photo does not show the LUN 0 GPT result.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>select Elden macOS 26.5 - UFS Read-only Probe in image b07b974f…</code>. Revision: `95e9740ea6da4727a0119d878a51f93b563305bf`.
- `host`: [Base revision plus the result-display overlay passed six host cases covering success, bad CRC, invalid length, transfer failure and bring-up failure. The ARM64e prelink and DarwinBoot checks passed.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>host probe-result checks and ARM64e storage prelink</code>. Revision: `95e9740ea6da4727a0119d878a51f93b563305bf`.
- `host`: [Base revision plus the unified UIC completion overlay passed eight host cases, ARM64e driver build and storage prelink, DarwinBoot preflight and RAM image validation. The controller result remains pending.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>compile and prelink the 4 KiB Elden UIC companion and verify elden-macos26-4k-ufs-uic-ram.img</code>. Revision: `623c1f937c423c039c11991ff5e2a9150bb0542c`.
- `device`: [Physical Elden observed TX lane in Hibern8. Exit reported e00002d6 with UIC result 0, IS 0x420 and DB 0 in the later snapshot, before NOP OUT or the GPT read.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>select Elden macOS 26.5 - UFS Read-only Probe in image bdebbc40…</code>. Revision: `623c1f937c423c039c11991ff5e2a9150bb0542c`.
- `host`: [Base revision plus the SM8750 link-wake overlay passed six host link-state tests, MacBook ARM64e compilation and link, the storage prelink, DarwinBoot preflight and RAM image validation. Fastboot accepted the RAM boot. Probe result remains pending.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>compile and prelink the 4 KiB Elden storage companion and verify elden-macos26-4k-ufs-wake-ram.img</code>. Revision: `e556675d1dd933f425ace1ba7b47d2feef4293d6`.
- `device`: [The physical tablet reached NativeUfs. NOP OUT timed out with result e00002d6, doorbell 1 and interrupt status 0. The probe did not read the GPT or publish media.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>select Elden macOS 26.5 - UFS Read-only Probe in image 8d884a50…</code>. Revision: `e556675d1dd933f425ace1ba7b47d2feef4293d6`.
- `device`: [2026-11-10: physical Elden bootloader fastboot reported macosroot as 4 GiB and accepted the staged UFS probe RAM image. The macOS controller read result remains pending.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>fastboot getvar partition-size:macosroot; fastboot boot elden-macos26-4k-ufs-ram.img</code>. Revision: `47cf0544d6ff4cddc88312dc43e2a48dfd98340e`.
- `device`: [2026-11-10: offline ext4 shrink reserved 4 GiB for macosroot on LUN 0. Both GPT copies matched the verified layout, Linux enumerated sda18 as macosroot, and e2fsck passed against the smaller rootfs partition. macosroot awaits Recovery media.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>e2fsck -f -n and blockdev --rereadpt from the Linux maintenance RAM boot</code>. Revision: `47cf0544d6ff4cddc88312dc43e2a48dfd98340e`.
- `host`: [The 4 KiB Elden UFS companion compiled and its 326-slot ABI passed the 25F71 prelink audit. The read-only LUN 0 GPT probe image 8d884a50… passed the embedded payload, loader preflight, and MacBook checksum checks. Tablet UFS and Recovery media remain separate tests.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>build-elden-macos26-bootstrap.py --elden-ufs-device; emit_macos26_security.py --elden-bootstrap --storage-driver</code>. Revision: `ca57db73c066162323e77156a9f0f1d72b1de4ff`.
- `device`: [2026-11-10, porting checkout at capture: Linux 7.2.8-y700-r2-androidcrypt1 used the legacy queue on the SM8750 controller with MCQ disabled and six LUNs with 4 KiB sectors. LUN 0 has no macosroot partition.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>uname -r, Linux sysfs and lsblk (read-only UFS inventory)</code>. Revision: `6a3fd8723b78acc1207279cb97655fc24353eb01`.
- `device`: [2026-11-10, porting checkout at capture: the running Linux kernel returned one live LUN 0 block at LBA 1. Its GPT CRC32 was 4b1100b9. The macOS GPT predicate accepted those bytes in a host harness and rejected the altered checksum. Native macOS controller access remains unverified.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>USB ADB on the MacBook, tablet-side sudo -n dd if=/dev/sda bs=4096 skip=1 count=1 status=none</code>. Revision: `64455d07b9f3c3d62e9ad0c0e837ae20c0150922`.
- `host`: [2026-11-10, reference revision plus Elden overlays: the Mac compiled and prelinked candidate 7e4d2664… with a passing 326-slot storage ABI and pointer authentication audit. Host fault tests passed for reads, range and write rejection, and failure quarantine.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>python scripts/build_macos26_xnu.py --build-ufs-driver --elden-ufs-device (with paired ARM64e build inputs)</code>. Revision: `ca57db73c066162323e77156a9f0f1d72b1de4ff`.
- `host`: [2026-11-10: candidate 7e4d2664… reached IOFindBSDRoot in QEMU and rejected the mismatched board before mapping controller MMIO or publishing media. Native Elden transport is unverified.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>python scripts/observe_macos26_kernel.py (Elden UFS probe selected on the QEMU board)</code>. Revision: `ca57db73c066162323e77156a9f0f1d72b1de4ff`.
- `host`: [Base revision plus local working-tree patches. 2026-11-07: LUN0/ipados root header read is device-verified. New AVB-kernel-pinned complete-image and per-block verification, live readonly media ancestry bridge, SystemOS union and RAM Data startup candidate compile/link and host checks pass; new mount/startup remains untested on hardware.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/STARTUP-USB-CANDIDATE-20261107.md)
  Command: <code>python edl_work/audit_startup_candidates.py (Y700 work repository)</code>. Revision: `33b55083a0b61630f71478230f648606163115eb`.
- `device`: [2026-11-07 owner photograph: new source kernel reads LUN0/ipados GPT bounds and SHNGROOT magic; manifest status0/windows2, SID60 slot0 CB0 inherited identity and no SMMU writes. This is the intended probe10 diagnostic panic, not an APFS root mount. Root image was independently fully hashed after Android reboot; Android setup/root also persisted.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/IPADOS-ROOT-TARGET-20261107.md)
  Command: <code>Owner selected ELDEN IPADOS ROOT CHECK - LUN0; photograph and image identity in Y700 device-result.json</code>. Revision: `33b55083a0b61630f71478230f648606163115eb`.
- `device`: [2026-11-07 device: /chosen/system-volume-auth-blob \(208-byte IM4P payload from the IPSW \*.dmg.root\_hash, sha384 vs BuildManifest\) is found and consumed — 'importing root hash' prints with no ENOENT; OS/SystemOS volumes publish; panic moves to IOKitBSDInit.cpp:984 waitForService timeout because no service claims boot-uuid-media. Manifest \(msys mtree\) transport remains open. Stock rollback 1738713600@0 unchanged.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/ROOT-MOUNT-AUTHBLOB-20261107.md)
  Command: <code>startup-authblob-signed.img sha c264290c… flashed to boot_a via owner-operated delta write</code>. Revision: `33b55083a0b61630f71478230f648606163115eb`.
- `source`: [Independent read-only ipados target configuration and fixed-address MMIO load source patch added. This source candidate requires build and device checks. Stock rollback values unchanged.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/IPADOS-ROOT-TARGET-20261107.md)
- `host`: [2026-11-06 prerequisites: official21H461 OS/SystemOS and original trust inputs are verified. Native readonly APFS inspection supplies actual filesystem UUIDs. A9381609472-byte raw root layout passes file readback and the actual RootLayout parser with file callbacks; Data, runtime policies and real root-target kernel remain pending. No hardware disk access. Source revision plus local working-tree changes.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PREREQUISITES-20261106.md)
  Command: <code>.venv/bin/python scripts/build-payload-loader.py</code>. Revision: `33b55083a0b61630f71478230f648606163115eb`.
- `host`: [Local working-tree GPL UFS adapter built as separate EFI applications; five core/session host suites, 114 SHA vectors, 512 C/Python header checks, six interrupted-update points, and real AAVMF RAM-volume retry/cleanup passed. Stage2 packaging, 15 full C selection fault cases, actual external menu/reset and QEMU-ADT menu-to-XNU registration return=1 now pass. Tablet UFS remains unverified; ADB has root/su model tests only. No device access or accepted FD replacement.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/UFS-STAGE2-20261106.md)
  Command: <code>.venv/bin/python scripts/build-ufs-stage2.py</code>. Revision: `33b55083a0b61630f71478230f648606163115eb`.
- `host`: [2026-11-06 host: source GOP console kernel/archives/prelink completed; separate read-only UFS root-check archive compiled with inherited identity DMA and LUN selection. TWRP/Linux EFI prototype and userdata/ESP design remain hardware-unverified. Details and bounded evidence in docs/NIGHT-BRINGUP-20261106.md; no stock index change or device write. Revision plus local working-tree patches.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/NIGHT-BRINGUP-20261106.md)
  Command: <code>.venv/bin/python third_party/UniXNU/unixnu build kernel -D . -j4</code>. Revision: `33b55083a0b61630f71478230f648606163115eb`.
- `host`: [2026-11-05 offline: existing Mac probe kernel \(51,986,432 bytes\) was matched against the payload and checked for NativeUfs symbols and PROBE\_ONLY/READ\_ONLY/SM8750 compile flags. No new kernel build or device storage evidence. Root publication is absent; probe 7/8 are SMMU/CB diagnostics and probe 3 is rejected. See docs/OFFLINE-PAYLOAD-20261105.md. Source revision plus uncommitted local packaging changes.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/OFFLINE-PAYLOAD-20261105.md)
  Command: <code>.venv/bin/python scripts/build_offline_ufs_packet.py --fd out/phase3/old-fd-verified.bin --source-payload out/phase3/payload-fat16.img --kernel third_party/UniXNU/out/elden/ipados-17.7.11-21H461/elden-ufs_probe/kernel/kernel.macho</code>. Revision: `33b55083a0b61630f71478230f648606163115eb`.
- `source`: [Storage addresses, missing root inputs and phase 1 bypass decision; implementation remains a later phase.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/porting-analysis.md)
- `host`: [Owned candidate: 190 original storage slots, actual C2/D2, live class sizes 0x90/0x88 and native 4K qualified. SCTLR alias was independently checked against the unchanged kernel's real MSR input. Raw-entry VM evidence only; no UEFI/EBS/UFS hardware evidence.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/STORAGE-ABI-20261106.md)
  Command: <code>python out/elden-storage-abi/scripts/audit-elden-storage.py --candidate out/bringup-20261105/kernel-gop.macho --plan elden-ufs_probe/kernel/kernel.json --snapshot storage-snapshot.json</code>. Revision: `33b55083a0b61630f71478230f648606163115eb`.
- `source`: [Concrete NativeUfsBlock slot/signature verification and genuine original-class bindings require a qualified audit, candidate and prelink plan. New lifecycle patch refuses root work before actual class registration. Complete root-check link and final candidate audit remain separate checks.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/scripts/build-elden-ufs-bindings.py)
- `host`: [Full root-check kernel compiled/prelinked \(07d4df1d…\) and its signed diagnostic derivative \(3fd40e9f…\) passed their own 190-slot static/live ABI audits. The actual menu arguments reach the genuine registration gate with result 1 before UFS MMIO. Hardware transport and root remain unverified.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/STORAGE-ABI-20261106.md)
  Command: <code>python out/build-rootcheck-kernel.py</code>. Revision: `33b55083a0b61630f71478230f648606163115eb`.
- `source`: [Complete XNU/Linux/vendor/TWRP compressed assets round-trip in 48.3 MiB. Standalone EFI decompression and recovery application added; compilation, firmware execution and hardware acceptance are separate gates. No firmware rebuild, device operation or KShimC removal.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/COMPRESSED-RESCUE-20261106.md)
- `source`: [Optional 128-byte BootShim writes the live ABL FDT pointer only into a reserved RAM FAT slot; the default build remains identical. Recovery validates/copies the current FDT and restores table ownership after failure. Hardware recovery remains unverified.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/ENTRY-FDT-HANDOFF-20261106.md)
- `source`: [Full SM8750 UFS inventory with Linux line references, driver reality, the arm-io window change and the four-stage probe plan.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE3-STORAGE.md)
- `host`: [2026-11-01: the hardware DTS with ufs\_mem\_hc and ufs\_mem\_phy compiles; the decompiled tree keeps reg 0x0 0x1d84000 0x0 0x3000, interrupts &lt;0 0x109 4&gt;, dma-coherent and status okay.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE3-STORAGE.md)
  Command: <code>.cache/dtc-src/dtc -I dts -O dtb -i soc/sm8750/dts -o /tmp/elden.dtb dts/elden.dts</code>. Revision: `b82bb65b4b3ba7508ae8ec9b18d0f36ec183da9f`.
- `host`: [2026-11-01: a decoupled ADT generated with scripts/unixnu/devicetree.py exports arm-io base 0x1000000 size 0x16000000, arm-io/ufshc reg 0xd84000/+0x3000, arm-io/ufsphy reg 0xd80000/+0x2000 and interrupts \(0, 265, 4\); the ADT grew from 13,152 to 13,624 bytes. No XNU boot is claimed.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE3-STORAGE.md)
  Command: <code>.venv/bin/python -c 'generate(Path("/tmp/elden.dtb"), merged_board_config, unique_chip_id="0x1")'</code>. Revision: `b82bb65b4b3ba7508ae8ec9b18d0f36ec183da9f`.

## Display {#display}

`implemented`

### Hardware and dependencies

- 1904x3040 bonded dual-DSI panel with DSC.
- UEFI GOP framebuffer and splash reservation.
- SM8750 DPU/DSI/PHY and backlight sequencing.

### Configuration

- The phase 1 menu renders through UEFI GOP.
- The separate macOS 26.5 build includes an opt-in Elden GOP profile and preserves the firmware scanout.

### Procedure

- Keep display handoff on GOP for the first kernel milestone.
- Record a visible checkpoint after DarwinBoot.
- Add DPU/DSI only after kernel entry is stable.

### Development findings

- GOP display is device-verified in the UniXNU menu.
- The running Elden Linux MSM DRM driver reports a 1904x3040 internal panel, 118x190 mm active area and a 7680-byte framebuffer stride.
- The recorded UEFI handoff reports base 0xFC800000, row 7616, 1904x3040 and depth 32. The macOS profile checks that the boot-time scanout fits the board's reserved aperture before mapping it.

### Completion criteria

- XNU paints a known pattern through a declared framebuffer handoff.
- Userland presentation and backlight transitions work.

### Current limits

- The Elden macOS profile uses inherited GOP scanout with CPU copies.
- XNU display provider execution on Elden, native DPU/DSI modesetting, and backlight control require separate validation.

### Next action

- Qualify the macOS EL1 handoff using a supported translation granule, then test a RAM boot for the first CPU-presented frame.

### Evidence

- `host`: [The 4 KiB prelink includes the Elden software framebuffer, matched the 473-slot display ABI and PAC metadata, and passed eleven host tests. Display on and First frame remain pending on the tablet.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>build --build-gop-display and verify the Recovery Framebuffer Test</code>. Revision: `1241b6e42385bf4ad7afc9c48f3f39df0a5ab322`.
- `device`: [2026-11-10, porting checkout at capture: Linux 7.2.8-y700-r2-androidcrypt1 drove the internal DSI panel at 1904x3040 and 165 Hz. The DRM connector reports 118x190 mm, and sysfs reports a 32-bit Linux framebuffer with a 7680-byte stride.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>modetest -M msm -c -p (read-only Linux DRM query)</code>. Revision: `cc333727e6badf997e6b2b9174934fe7ec144023`.
- `host`: [2026-11-10: the Mac compiled the opt-in Elden profile in both VirtIO and UFS companions. The QEMU VirtIO candidate passed the 473-slot framebuffer vtable and PAC audit.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>python scripts/build_macos26_xnu.py --build-qemu-gop-display --build-gop-display --elden-gop-board (with paired ARM64e build inputs)</code>. Revision: `ca57db73c066162323e77156a9f0f1d72b1de4ff`.
- `host`: [2026-11-10: the generic GOP path mapped the QEMU framebuffer and powered on the display service. The original launchd ran, and WindowServer recorded one start and zero exits in 180 seconds. An explicit Elden-profile control rejected the QEMU framebuffer before mapping. A composited frame and language chooser remain unverified.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>python scripts/observe_macos26_kernel.py --native-gop-display --follow-launchd-main --let-vector-log (with paired QEMU Recovery inputs)</code>. Revision: `ca57db73c066162323e77156a9f0f1d72b1de4ff`.
- `source`: [GOP menu display was observed on hardware.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE1-STATUS.md)
- `source`: [Display topology, panel risk and GOP-first strategy.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/porting-analysis.md)

## Input {#input}

`planned`

### Hardware and dependencies

- Novatek SPI touch on SPI4 and GPIO 162 interrupt.
- Volume and power keys used by the UEFI menu.
- The installed Linux image names novatek\_ts\_csot\_3k\_fw.bin and specifies a 10 MHz GENI SPI4 bus with GPIO 162 falling-edge interrupts.

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

- Verify live Linux touch reports and orientation, then qualify the GENI SPI transport and Novatek HID bridge under XNU.

### Evidence

- `source`: [Volume-key navigation reached the accepted menu.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE1-STATUS.md)
- `source`: [Novatek SPI wiring and input bring-up requirements.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/porting-analysis.md)

## GPU {#gpu}

`host-verified`

### Hardware and dependencies

- SM8750 Adreno 830 chip ID 0x44050000.
- GPU, GMU and GPU SMMU resources measured from the tablet's Linux device tree.
- Matched gen80000 GMU, SQE, AQE and ZAP firmware identities.

### Configuration

- The GMU loader reuses AdrenoFirmware and constrains destinations to SM8750 GMU address ranges.
- An optional ARM64e build embeds the pinned GMU image and enables validation via elden-adreno830-probe=1.

### Procedure

- Validate the full firmware image before invoking the load transport.
- Use the RAM probe to confirm the same checks under XNU.
- Establish GMU power, clocks, SMMU ownership and HFI before enabling submission.

### Development findings

- The tablet's Linux DRM and Turnip stack identifies Adreno 830.
- The shared loader validated the four expected firmware blocks on the build host and on the tablet under Linux.

### Completion criteria

- GMU firmware starts and responds on HFI under XNU.
- GPU submissions, fences and mapping work.
- A known image renders and Metal presentation is visible.

### Current limits

- The XNU probe only validates firmware and counts blocks.
- Native GMU power, firmware transfer, HFI, submission and Metal are pending.

### Next action

- Run the GMU probe on the tablet, then bring up the SM8750 GMU power and SMMU paths.

### Evidence

- `device`: [The physical tablet reports Adreno 830 via Turnip. The loader test passed against the installed 88896-byte GMU image. These results are from Linux.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>vulkaninfo --summary and run test-gmu against the installed firmware over Linux SSH</code>. Revision: `a6190077af83a6e02645a6b02a70f86c43696e3e`.
- `host`: [Firmware validation and refusal cases passed. The linked kernel, prelink, RAM image and MacBook copy passed host checks. XNU runtime remains unverified.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>compile the GMU loader with sanitizers and build the opt-in 4 KiB ARM64e probe</code>. Revision: `a6190077af83a6e02645a6b02a70f86c43696e3e`.

## Network {#network}

`planned`

### Hardware and dependencies

- Wi-Fi PCIe function 17cb:110e on the SM8750 root complex.
- WCN7861 Bluetooth over UART with brhbtnv20.bin and brhbtfw20.tlv.
- Shared WCN7861 PMU.

### Configuration

- No Elden XNU radio transport is selected.

### Procedure

- Inspect the live Linux radio bindings and firmware names.
- Verify PMU and PCIe state before Wi-Fi bring-up.
- Bring up Bluetooth over UART and check HCI initialization.

### Development findings

- The installed Linux device tree identifies both radio functions and the shared PMU.

### Completion criteria

- Wi-Fi associates and transfers traffic on the tablet.
- Bluetooth pairs and exchanges data with a peripheral.

### Current limits

- Radio operation under XNU remains unverified.

### Next action

- Record the tablet Linux drivers and firmware identities, then map the PMU, PCIe and UART dependencies to XNU.

### Evidence

- `host`: [Read-only inspection of the installed Linux image DTB identified the PCIe ID, Bluetooth UART firmware names and shared radio PMU.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>dtc -I dtb -O dts and inspect the peripheral nodes</code>. Revision: `9ba3a222426de0702e669d7d69c879c81700e1a0`.

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

- 2026-11-05 marker menu retains existing reset/shutdown actions and uses a 600-second no-input fallback to reset. No new PMIC write path or device power qualification; see docs/OFFLINE-PAYLOAD-20261105.md.
- UEFI power and key handling are verified only at the firmware layer.
- The selected OS profile does not supply sleep-disabled, so board.toml now adds it under \[adt.defaults.u32\].
- The final Phase 2.1 ADT was decoded with sleep-disabled=1.
- The XNU power topology is not complete.

### Completion criteria

- Declared power controls match readings.
- Sleep/resume or shutdown transitions restore dependent peripherals.
- An installed macOS system resumes from a hybrid hibernation image and restores storage, display, input and radios.

### Current limits

- Battery, charging, thermal and sleep are not implemented.

### Next action

- Audit RPMh resource ownership and PSCI suspend states. Qualify peripheral suspend and resume before testing hybrid hibernation on a writable install.

### Evidence

- `host`: [The diagnostic validates the GMU image before any future transport work. Its boot hook only counts validated firmware blocks.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>build and verify the Elden Adreno 830 GMU probe</code>. Revision: `a6190077af83a6e02645a6b02a70f86c43696e3e`.
- `host`: [The menu retains the Reboot to Fastboot action.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>inspect the combined Recovery and Linux menu</code>. Revision: `cf9b0ba7c8a000b3ed4f4199707095ffd9b5fa0c`.
- `host`: [The framebuffer menu retains the Reboot to Fastboot action.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>inspect the Recovery Framebuffer Test menu</code>. Revision: `1241b6e42385bf4ad7afc9c48f3f39df0a5ab322`.
- `host`: [The diagnostic retains the opt-in Reboot to Fastboot action.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>inspect the Recovery PID 1 Trace menu</code>. Revision: `0a0254a5efb72452bdb4622b567b5727bb2a69fb`.
- `host`: [The two opt-in entries use the existing PSCI CPU\_ON path and ArmCpu self-IPI diagnostics. Device CPU\_ON results remain pending.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>inspect the Aff2 and Eight-core menu boot arguments</code>. Revision: `ed8f382d36ea0d3ebaa3a1582aa8e03410c9645d`.
- `source`: [Board hardware and payload policy values.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/board.toml)
- `host`: [2026-10-25: independent ADT decode found /defaults sleep-disabled=1. This is source/host evidence, not a device suspend test.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2.1-STATUS.md)
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

- 2026-11-07: manual120-second poweroff and8-second autostart candidates include unchanged FD/56MiB FAT,6GiB ADT, original TrustCache, RAM Data and session IDs. Independent RSA/data/stock properties and embedded-file audits pass; every boot index stays1738713600@0.
- 2026-11-06 prerequisites: direct9ebc7b6a and KShimC6af63b3e experiments are signed at exact stock index. A frozen dual11 control rebuild is byte-identical; the48MiB recovery FAT preserves the full stock kernel/initrd and raises the explicit FreeExec copy bound to64MiB. Source runtime and old signed artifacts are preserved.
- 2026-11-06 host: source GOP console kernel/archives/prelink completed; separate read-only UFS root-check archive compiled with inherited identity DMA and LUN selection. TWRP/Linux EFI prototype and userdata/ESP design remain hardware-unverified. Details and bounded evidence in docs/NIGHT-BRINGUP-20261106.md; no stock index change or device write.
- 2026-11-05 offline: ramdisk argv placement fixed; gzip made deterministic; embedded validation checks both header and actual x3 constant and rejects a FAT BPB extending past published bytes. The isolated marker candidate uses the accepted FD and a rebuilt 56 MiB shim, and passes kernel/ADT/FAT/FD checks. See docs/OFFLINE-PAYLOAD-20261105.md. No device run is claimed.
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

- Use the manual startup image first; autostart is not a qualified unattended fastboot recovery loop.

### Evidence

- `host`: [The main cache and four subcaches matched all 69,356 original 16 KiB SHA-256 blocks. Twelve host cases passed for the exact patched gate. The linked feature symbol, Recovery ABI, DarwinBoot and packed payload checks passed. The installed r37 log showed this granule was rejected at signature registration.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Audit the original 25F71 ARM64e shared-cache signing blocks, compile the CodeDirectory gate, and build the r38 RAM image</code>. Revision: `800d7b888e4c116c3c5e38a33e2b30a9508c6bf1`.
- `device`: [The r38 tablet boot mounted the BaseSystem and executed PID 1. AMFI reached subcache .01 with the 16 KiB compatibility path active. PID 1 stayed in fcntl for more than nine minutes without starting Recovery services.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>fastboot boot elden-recovery-cache-signature-ram.img and capture the recovery-usb entry</code>. Revision: `2d06dd3afbc4a89681657cc63b3367db83850cc1`.
- `host`: [The r39 progress overlay marks file reads, verification offsets and the registration result. The linked messages, Recovery module and ABI comparisons, DarwinBoot preflight, packed payload and MacBook checksum passed with the local overlay.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Build and verify elden-recovery-cache-progress-ram.img</code>. Revision: `2d06dd3afbc4a89681657cc63b3367db83850cc1`.
- `device`: [The tablet verified the first MiB of the 720,125,952-byte signed range. It did not reach the 64 MiB checkpoint after more than seven minutes, and the PID 1 fcntl was still pending.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>fastboot boot elden-recovery-cache-progress-ram.img and capture the recovery-usb entry</code>. Revision: `b787f6d0c93272428f9d6d6a0ef5f5598bcb4198`.
- `host`: [The r40 buffered-read overlay keeps CodeDirectory verification and reports separate read and hash times. The linked progress strings, prelink ABI comparisons, DarwinBoot preflight, packed payload and MacBook checksum passed with the local overlay.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Build and verify elden-recovery-cache-buffered-ram.img</code>. Revision: `b787f6d0c93272428f9d6d6a0ef5f5598bcb4198`.
- `device`: [With buffered reads, the tablet verified 32 MiB within two seconds, then reported a swap-file open failure before the 64 MiB checkpoint. VM bootstrap accounted for 65,536 native pages in the 256 MiB allocation.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>fastboot boot elden-recovery-cache-buffered-ram.img and capture the recovery-usb entry</code>. Revision: `e8680d43aca454e2a65ea39591d6a221deb29aba`.
- `host`: [The r41 image requests a 4 GiB conventional-memory allocation and uses the same r40 kernel. FAT readback, DarwinBoot preflight, packed image verification and the MacBook checksum passed with the local packaging changes.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>make_phase2_payload.py --owned-memory-size 0x100000000 and verify_phase2_artifact.py</code>. Revision: `e8680d43aca454e2a65ea39591d6a221deb29aba`.
- `device`: [The tablet entered XNU with the 4 GiB window. kmem\_range\_init reported 90.77 GiB of fixed claims and a 42.84 GiB hole. The panic occurred before the USB worker was available.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>fastboot boot elden-recovery-4g-memory-ram.img and read the panel panic record</code>. Revision: `93c9bda3829895d179624818ff20ba4b50321e6a`.
- `host`: [The local Elden overlays cap the default compressor claim and arm the PSCI panic reset during early device-tree setup. Linked code, prelink ABIs, DarwinBoot preflight, packed payload readback and MacBook checksums passed for the RAM images.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Build and verify elden-recovery-memory-reset-ram.img and the separate early-panic test image</code>. Revision: `93c9bda3829895d179624818ff20ba4b50321e6a`.
- `device`: [The tablet returned to fastboot 66 seconds after the MacBook selected the deliberate early-panic entry. No XNU USB interface or host reset command appeared. The MacBook immediately RAM-booted the corrected image.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>fastboot boot elden-recovery-early-panic-check-ram.img and monitor for bootloader fastboot over USB</code>. Revision: `8f5f355b09ff3e1d91bd97219da4588271e43cc7`.
- `device`: [Both boots reset after about 149 seconds before XNU USB enumeration. The partly corrupted retained log showed an 8 GiB compressor range, completed VM bootstrap, and a later write\_pte\_fast alignment panic. The 4 KiB XNU source had selected 16 KiB VM pages because RAM exceeded 1 GiB.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Boot the r42 4 GiB image with two USB timeout values, then read the previous retained log over UniXNU USB</code>. Revision: `8f5f355b09ff3e1d91bd97219da4588271e43cc7`.
- `host`: [The local arm\_init overlay keeps the hardware and VM granules equal for the native 4 KiB SHENG target. The linked signature and panic hooks, Recovery ABI checks, 4 GiB ADT preflight, packed payload and MacBook checksum passed.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Build and verify elden-recovery-4k-vm-ram.img</code>. Revision: `ef4ded874aca91dc9b1e15bf6217384e3d80b3f5`.
- `device`: [The tablet booted with 4 GiB and 4 KiB VM pages, mounted the BaseSystem, and registered every dyld subcache signature. PID 1 then hit EXC\_ARM\_PAC\_FAIL on AUTIA x16, x17. The MacBook captured the complete panic and the tablet reset to fastboot automatically.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>fastboot boot elden-recovery-4k-vm-ram.img and capture the recovery-usb entry</code>. Revision: `ae78b9a7fe63a685b38d86323d6c5a556acbdfc8`.
- `host`: [All 4,854 nonempty 16 KiB chains were reproduced as 4 KiB parts. The audit found 13,952 crossings. The local integration links the UniXNU slide function and PID 1 PAC diagnostics, and passed prelink ABI, DarwinBoot, packed image and MacBook checksum checks.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Audit original v5 fixup chains and build elden-recovery-shared-region-ram.img</code>. Revision: `ae78b9a7fe63a685b38d86323d6c5a556acbdfc8`.
- `device`: [The tablet mapped the shared cache and advanced past the prior AUTIA failure. PID 1 exited with SIGSEGV before any tracked Recovery service started. The MacBook captured the panic and the tablet reset to fastboot automatically.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>fastboot boot elden-recovery-shared-region-ram.img and capture the recovery-usb entry</code>. Revision: `40ad9317d88a944e8c879b407c0e9d509ef117cc`.
- `host`: [The local PID 1 trace logs unresolved EL0 aborts before exception delivery. The linked diagnostics, paired prelink ABIs, DarwinBoot preflight, packed payload and MacBook checksum passed.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Build and verify elden-recovery-pid1-abort-ram.img</code>. Revision: `40ad9317d88a944e8c879b407c0e9d509ef117cc`.
- `device`: [PID 1 faulted at original libobjc cache offset 0x25524 while loading an isa-derived class pointer. USB captured the complete panic and the tablet returned to fastboot without intervention.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>fastboot boot elden-recovery-pid1-abort-ram.img and capture the recovery-usb entry</code>. Revision: `9ba3a222426de0702e669d7d69c879c81700e1a0`.
- `host`: [The local 47-bit TTBR0 and 38-bit TTBR1 candidate links both table geometries and passed the 30-module prelink, DarwinBoot preflight, packed image checks and MacBook checksum.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Build and verify elden-recovery-user-va47-ram.img with the local 47-bit overlay</code>. Revision: `2b42e94c36129a66771e746716246268e7ae4e90`.
- `device`: [Live TCR reports 47-bit TTBR0 and 38-bit TTBR1 at 4 KiB. The original launchd reaches main and runs mount-phase-1. Missing iSC role 256 causes SIGABRT before any Recovery UI service starts. The complete panic was captured over USB.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>fastboot boot elden-recovery-user-va47-ram.img and capture the recovery-usb entry</code>. Revision: `2492e40a1db94ec1aa2e1b0aec251284c09e6c55`.
- `host`: [The ARM64e kernel links the EldenAdreno830LoadGmu routine. The embedded image and MacBook checksum passed.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>build and verify the Elden Adreno 830 GMU probe</code>. Revision: `a6190077af83a6e02645a6b02a70f86c43696e3e`.
- `host`: [Verified the original boot\_b kernel's EFI header, its embedded DTB and the read-back FAT files. The MacBook copy matched the combined image's SHA-256. Tablet execution is pending.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>make_phase2_payload.py with the Linux kernel and DTB and verify_phase2_artifact.py</code>. Revision: `cf9b0ba7c8a000b3ed4f4199707095ffd9b5fa0c`.
- `host`: [The 30-module kernel fits the 128 MiB embedded payload. DarwinBoot, v4 RAM image validation and the MacBook checksum passed.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>verify_phase2_artifact.py on elden-macos26-4k-recovery-framebuffer-ram.img</code>. Revision: `1241b6e42385bf4ad7afc9c48f3f39df0a5ab322`.
- `host`: [The v4 embedded RAM artifact passed DarwinBoot and payload checks. The MacBook copy matched its SHA-256.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>verify_phase2_artifact.py on elden-macos26-4k-recovery-pid1-trace-ram.img</code>. Revision: `0a0254a5efb72452bdb4622b567b5727bb2a69fb`.
- `host`: [Verified the Aff2 and eight-core menu, the reordered Recovery ADT and the embedded kernel. The MacBook copy matched the verified image.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>verify_phase2_artifact.py on elden-macos26-4k-recovery-smp-aff2-ram.img</code>. Revision: `ed8f382d36ea0d3ebaa3a1582aa8e03410c9645d`.
- `host`: [Verified the PID 1 stdout/stderr observation image with the same paired kernel and Recovery ADT. DarwinBoot, embedded payload checks and the MacBook copy checksum passed.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>verify_phase2_artifact.py on elden-macos26-4k-recovery-pid1-ram.img</code>. Revision: `030cc6450b0bbaa6979b1370a3accf303dcf1563`.
- `device`: [2026-11-11: the Recovery Root RAM image pairs the APFS volume UUID and root hash with the installed BaseSystem. DarwinBoot and embedded image validation passed, and Elden bootloader fastboot accepted the RAM boot.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>fastboot boot elden-macos26-4k-recovery-root-ram.img</code>. Revision: `767f7bd7f60897742f596fd6ae96d5d0add654b3`.
- `host`: [Verified the result-display candidate Android v4 header, embedded FAT and kernel identity. The MacBook copy matches the verified image.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>verify_phase2_artifact.py and MacBook SHA-256 for image 0adacbc5…</code>. Revision: `95e9740ea6da4727a0119d878a51f93b563305bf`.
- `host`: [The v4 RAM image b07b974f… contains the rebuilt 4 KiB UFS kernel with the same firmware, BootShim, ADT and manual probe menu. Verified the embedded FAT and kernel and matched the MacBook copy.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>scripts/verify_phase2_artifact.py --kind boot --embed-payload --expect-default native26</code>. Revision: `623c1f937c423c039c11991ff5e2a9150bb0542c`.
- `device`: [2026-11-10: bootloader fastboot on elden\_prc\_wifi reported is-userspace=no and returned OKAY for the transfer and boot command for image 5ef0a3fe…. On-screen EL1 execution remains unverified.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>fastboot boot ~/Downloads/elden-el1-native47-ram.img (MacBook USB)</code>. Revision: `abdae5c70bc1d7eb8eea28a045ae3544881274e2`.
- `host`: [2026-11-10: the standalone 47-bit EL1 v4 RAM image 5ef0a3fe… passed structural and embedded-file checks, and the MacBook copy matched the verified SHA-256. Tablet execution is pending.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>scripts/build_phase2_image.py --kind probe --embed-payload and scripts/verify_phase2_artifact.py --kind probe --embed-payload --expect-default native47</code>. Revision: `5fa1cade0ac901d42a839b002aae3f45cf3cc9fa`.
- `host`: [2026-11-10: Clang/LLD 23.1.1 built the ARM64 EFI boot-service driver. COFF symbols confirm the handoff start and end share the same section. Loader runtime qualification is pending.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>bash scripts/build_native_loader.sh (macOS-ForSheng reference, with the Elden COFF end-label patch)</code>. Revision: `ca57db73c066162323e77156a9f0f1d72b1de4ff`.
- `host`: [Base revision plus local working-tree patches. 2026-11-07: manual120-second poweroff and8-second autostart candidates include unchanged FD/56MiB FAT,6GiB ADT, original TrustCache, RAM Data and session IDs. Independent RSA/data/stock properties and embedded-file audits pass; every boot index stays1738713600@0.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/STARTUP-USB-CANDIDATE-20261107.md)
  Command: <code>python edl_work/audit_startup_candidates.py (Y700 work repository)</code>. Revision: `33b55083a0b61630f71478230f648606163115eb`.
- `host`: [2026-11-06 prerequisites: direct9ebc7b6a and KShimC6af63b3e experiments are signed at exact stock index. A frozen dual11 control rebuild is byte-identical; the48MiB recovery FAT preserves the full stock kernel/initrd and raises the explicit FreeExec copy bound to64MiB. Source runtime and old signed artifacts are preserved. Source revision plus local working-tree changes.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PREREQUISITES-20261106.md)
  Command: <code>.venv/bin/python scripts/build-payload-loader.py</code>. Revision: `33b55083a0b61630f71478230f648606163115eb`.
- `host`: [2026-11-06 host: source GOP console kernel/archives/prelink completed; separate read-only UFS root-check archive compiled with inherited identity DMA and LUN selection. TWRP/Linux EFI prototype and userdata/ESP design remain hardware-unverified. Details and bounded evidence in docs/NIGHT-BRINGUP-20261106.md; no stock index change or device write. Revision plus local working-tree patches.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/NIGHT-BRINGUP-20261106.md)
  Command: <code>.venv/bin/python third_party/UniXNU/unixnu build kernel -D . -j4</code>. Revision: `33b55083a0b61630f71478230f648606163115eb`.
- `host`: [2026-11-05 offline: ramdisk argv placement fixed; gzip made deterministic; embedded validation checks both header and actual x3 constant and rejects a FAT BPB extending past published bytes. The isolated marker candidate uses the accepted FD and a rebuilt 56 MiB shim, and passes kernel/ADT/FAT/FD checks. See docs/OFFLINE-PAYLOAD-20261105.md. No device run is claimed. Source revision plus uncommitted local packaging changes.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/OFFLINE-PAYLOAD-20261105.md)
  Command: <code>.venv/bin/python scripts/build_offline_ufs_packet.py --fd out/phase3/old-fd-verified.bin --source-payload out/phase3/payload-fat16.img --kernel third_party/UniXNU/out/elden/ipados-17.7.11-21H461/elden-ufs_probe/kernel/kernel.macho</code>. Revision: `33b55083a0b61630f71478230f648606163115eb`.
- `source`: [Reproducible phase 1 build commands, hashes and verification checklist.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE1-HANDOFF.md)
- `source`: [Preserved build inputs and remaining format 2 handoff work.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/FORMAT2-MIGRATION.md)
- `source`: [Phase 2 gates mapped to the official porting steps, capacity and memory constraints, and separate loader/kernel acceptance criteria; planning only, with no new device qualification.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2-HANDOFF.md)
- `source`: [Source-derived FDT, firmware RAM and reservation audit, decoded ADT checks, boot CPU parameter policy and remaining runtime evidence.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2.1-STATUS.md)
- `source`: [Pinned kernelcache, 57-patch XNU build, prelink inventory, symbol/4 KiB audits and measured 56 MiB payload fit.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2.2-STATUS.md)
- `host`: [Phase 2.0 established a rebuilt phase 1 baseline, preserved prior candidates, verified format 2 output isolation, and did not generate a phase 2 boot image.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2-STATUS.md)
  Command: <code>test -e .cache/phase2-plan/UniXNU/out/elden/ipados-17.7.11-21H461/elden/tree</code>. Revision: `dffc3020a85830d0d981a85871d9ab31aac5827d`.
- `host`: [2026-10-25: kernelcache f18b4df865405f2a287b84977d7aca745e056d656d9fc9df1662970ce2969de7 produced native kernel 02f216348851ba9ce70616430ff7607be9d3305cbc8b2ae1186f0e7d6b20fce7 and prelinked kernel.macho 65a3e799e1eb7f631a3b146dfc890ef5a8147c8fc613ee383a1665b398fb1ef9; runtime qualification remains false.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2.2-STATUS.md)
  Command: <code>PATH=.cache/phase2-plan/toolchain/bin:.venv/bin:$PATH .venv/bin/python .cache/phase2-plan/UniXNU/unixnu build kernel -D .</code>. Revision: `c91a2191fdf591a401a03027ed8b7fbfdbcad3a7`.
- `host`: [2026-10-25: a 58,720,256-byte FAT16 volume held all 54,063,968 payload bytes, left 3,734,016 bytes free, and round-tripped kernel.macho with SHA-256 65a3e799e1eb7f631a3b146dfc890ef5a8147c8fc613ee383a1665b398fb1ef9.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2.2-STATUS.md)
  Command: <code>mformat -C -F -T 114688 -v ELDENPH2 -i .cache/phase2.2/payload-fit-56m-20261025-223638.img :: &amp;&amp; mcopy -i .cache/phase2.2/payload-fit-56m-20261025-223638.img -s .cache/phase2-plan/UniXNU/out/elden/ipados-17.7.11-21H461/elden/payload/stage/EFI ::/</code>. Revision: `c91a2191fdf591a401a03027ed8b7fbfdbcad3a7`.
- `host`: [2026-11-01: FAT16 probe \(16,223 clusters\) and FAT16 56 MiB payload \(57,103 clusters\) replace the mformat -F FAT32 volumes EnhancedFatDxe rejects below 65,525 clusters. Probe image d6bf11a7a260856a525a831689def5b12ea028dedaca7dc2c78009bc6f0c6adf and final image 863d1b02ae7c7c5b7a7de0ac6cd8590aa36332dbf25540735ed4a264de8288e9 pass FAT type, BPB label, gzip\(shim+FD+payload\) and FV module checks; firmware is unchanged at 20b4b370d599aee9b081a283bd62faffe6ee66005d0de32967284d7d53adf245. Host evidence only; no device boot was performed.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2.3-STATUS.md)
  Command: <code>python3 scripts/make_phase2_probe.py &amp;&amp; python3 scripts/make_phase2_payload.py --from-image out/phase2.3/payload.img &amp;&amp; python3 scripts/build_phase2_image.py --kind probe --embed-payload &amp;&amp; python3 scripts/build_phase2_image.py --kind boot --embed-payload &amp;&amp; python3 scripts/verify_phase2_artifact.py --kind probe --image out/phase2.3/elden-phase2-embed-probe.img --shim out/phase2.3/shim-probe-embed.bin --embed-payload --payload out/phase2.3/probe.img &amp;&amp; python3 scripts/verify_phase2_artifact.py --kind boot --image out/phase2.3/elden-phase2-embed-boot.img --shim out/phase2.3/shim-boot-embed.bin --embed-payload --payload out/phase2.3/payload.img</code>. Revision: `5582de7371ea5d880235e05854f459c7b819b41a`.
- `host`: [2026-10-31: phase-2 firmware dc8a97dcf1369066114f0d10e50f0b163876b78a37796c29d7d468a7f6d9d9bf, 56 MiB payload b2c96e08f71bbd3f8a84018024b1dc048994b72c2a81b56789686e503da82f80, probe image 9ea0174c275e7ebb42d9727c770b7a06ae09a6d44df9e36657a667c8de7e051b and final image d52dd8e37fa0ef87c44b2b15207497e93ac6285ca874cf20e5a668c4226ecf99 passed v3 header, gzip\(shim+FD\), FV module and FAT/config checks. Host evidence only; no device boot was performed.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2.3-STATUS.md)
  Command: <code>python3 scripts/verify_phase2_artifact.py --kind probe --image out/phase2.3/elden-phase2-probe.img &amp;&amp; python3 scripts/verify_phase2_artifact.py --kind boot --image out/phase2.3/elden-phase2-boot.img</code>. Revision: `57e68be133c407ef9fa7dc6b4f10f1bd4cd3aedd`.
- `device`: [2026-11-01: owner booted both FAT16 embed-payload images; the menu showed config: \\EFI\\UniXNU\\unixnu.toml and the ELDEN 2.3 INITRD 56M entry from the embedded volume, so the kernel-field payload channel is device-verified. The menu scale was pinned to 4 afterwards.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2.3-STATUS.md)
  Command: <code>fastboot boot out/phase2.3/elden-phase2-embed-probe.img &amp;&amp; fastboot boot out/phase2.3/elden-phase2-embed-boot.img</code>. Revision: `509bc088641cb6d56d2a28b5526adb72dc88d51d`.
- `device`: [2026-11-01: two RAM cold boots of the scaled image 3dc8ae9611ec899ff14d50032ecd0ce2dd1035b3af9f9d3183bbab6cd41bcd93 printed DARWINBOOT: ARM64 va=0xFFFFFFF00427C000 pa=0xB927C000 args=0xBDB58000 entry=0xBC3ED488 owned=0x10000000, video base=0xFC800000 1904x3040 row 7616 depth 32, and inputs validated; exiting boot services, then the top 1/16 green band. The EL/input check passed and the window was allocated; no kernel output followed.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2.4-STATUS.md)
  Command: <code>fastboot boot out/phase2.3/elden-phase2-embed-boot.img (select xnu) twice</code>. Revision: `da1d077cf6856e3f2621785f4a612f2c5ebae260`.
- `host`: [2026-11-01: probe kernel 54,050,912 bytes a8f04b455996a4656a3055254c127e42f0676187c9550aa0b5fa57bbbe94e2d9 with entry 0xFFFFFFF0073ED488 branching to stub 0xFFFFFFF008588000 and back to 0xFFFFFFF0073EF05C; preflight accepted 16 segments and the ADT; FAT payload 065282a2... and image a4ad1fc7... passed the v4/FAT16/FV checks and match the probe bytes. Host evidence only; the probe image has not been booted.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2.4-STATUS.md)
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

- 2026-11-07: panic duplication is fixed and device-confirmed. New generic MIT DWC3 core plus guarded elden adapter, nonblocking console ring, bounded panic drain, session-bound status and PID1 EL0 syscall observation are built; CDC hardware remains unqualified.
- 2026-11-06 prerequisites: final EFI31744-byte application passes FDT mailbox, parent metadata and memory-report contracts, and reaches the same XNU registration return1 through the neutral-debug AAVMF driver. Known-read expectations are prepared but were not sampled on the tablet.
- 2026-11-06 host: source GOP console kernel/archives/prelink completed; separate read-only UFS root-check archive compiled with inherited identity DMA and LUN selection. TWRP/Linux EFI prototype and userdata/ESP design remain hardware-unverified. Details and bounded evidence in docs/NIGHT-BRINGUP-20261106.md; no stock index change or device write.
- 2026-11-05 offline: marker menu fallback is 600 seconds; NativeUfs probe 2 deliberately panics to display read-only GCC/UFS diagnostics. Probes 7/8 inspect SMMU/CB; SM8750 rejects probe 3. This changes acceptance wording, not the driver. See docs/OFFLINE-PAYLOAD-20261105.md.
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

- Build and test the 4 KiB ARM64e macOS kernel handoff after the passing standalone translation and PAC probes.
- Qualify the opt-in UniXNU firmware command menu over a physical EFI serial port, then bring up a pre-boot USB CDC transport for the MacBook cable.
- Run the PC CDC logger before boot. Require actual bytes, matching session, both mount results and repeated PID1 user-trap status; do not infer success from a launchd filename.

### Evidence

- `host`: [Base revision plus the Recovery USB adapter and retained log reader. DWC3 host tests, retained-log replay, 4 KiB ARM64e link, Recovery prelink, payload and AVB checks passed. USB enumeration and live log capture are pending on Elden.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Build Elden Recovery with --recovery-usb-core and verify the RAM and signed boot_a images</code>. Revision: `06cc83d15dc86b40c492fea2267eb0a0d02fbe64`.
- `device`: [PID 1 exited because dyld could not load libSystem.B.dylib. Read-only host inspection found the library in the paired ARM64e cache map, so the cache selection or mapping still needs diagnosis.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Match the owner-captured PID 1 panic UUID to the installed Recovery kernel</code>. Revision: `06cc83d15dc86b40c492fea2267eb0a0d02fbe64`.
- `host`: [Base revision plus the Elden Recovery patch and menu. The 4 KiB ARM64e build, Recovery prelink, DarwinBoot preflight, embedded Linux/DTB/menu readback and slot A AVB verification passed. Both MacBook copies matched SHA-256. Recovery services and Linux installed rootfs remain unverified with this image.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Build the combined Recovery without Ignition and Linux console retention images</code>. Revision: `71e0c4fdc4af6d8af718d103c6f9e4822dc9acb7`.
- `device`: [Linux reached early kernel startup, initialized memory, GICv3 and its architected timer, then registered tty0 and disabled the efifb boot console. The photo ends there and rootfs/userspace remain unverified.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Select Elden Linux - installed rootfs from the combined diagnostic image</code>. Revision: `2725e4f616cde07a3003a7584e9d14278aaa8af6`.
- `host`: [Base revision plus the opt-in keep\_bootcon change. Verified all three forced command-line copies and the raw Android v4 packed image, including Linux, DTB and menu readback. Tablet test pending.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Build and verify elden-linux-retained-console-ram.img</code>. Revision: `2725e4f616cde07a3003a7584e9d14278aaa8af6`.
- `device`: [At 127 seconds, all 67 recorded instruction faults completed and the last had VM result 0. SVC trace reported 50 of 52 completed and no completion for its latest sysctl \(202\). The earlier boot photo shows the Darwin Ignition banner. Recovery services and WindowServer still had zero starts. The specific sysctl remains unconfirmed on hardware.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Boot Recovery Framebuffer Test from the combined diagnostic image and capture PID 1 results</code>. Revision: `a458069b90aa62072e93bf7cfe1dad1554dc6e79`.
- `device`: [PID 1 remained at one start and zero exits with unchanged counts of 179 EL0 synchronous exceptions and 52 SVCs. The last syscall was sysctl, and the last non-SVC syndrome recorded was an EL0 level 3 instruction translation fault. Recovery services and WindowServer had zero starts.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Compare tablet PID 1 reports 30 seconds apart</code>. Revision: `ca89dd848a719d877d72288fa2df036b884d175b`.
- `host`: [Base revision plus the PID 1 trace patch. The new RAM image records instruction fault addresses and VM results, plus syscall handler returns and errno. The build, matching Recovery module set, storage and display ABI, DarwinBoot preflight and raw boot image checks passed.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Build and verify elden-macos26-pid1-fault-ram.img</code>. Revision: `ca89dd848a719d877d72288fa2df036b884d175b`.
- `device`: [Bootloader fastboot accepted the RAM image on the tablet. The on-screen PID 1 result is pending.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>fastboot boot elden-macos26-4k-recovery-pid1-trace-ram.img</code>. Revision: `1241b6e42385bf4ad7afc9c48f3f39df0a5ab322`.
- `host`: [The opt-in trace records return from the initial exec, PID 1 synchronous EL0 traps, syscall entries, and the launchd main acknowledgment. Device execution remains pending.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>compile the PID 1 trace and verify its report symbol</code>. Revision: `0a0254a5efb72452bdb4622b567b5727bb2a69fb`.
- `device`: [The screen remained at launchd exec after 153 seconds with one PID 1 exec, zero exits, and zero recorded Recovery service starts. No PID 1 stdout or stderr appears in the capture.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>select Elden macOS 26.5 - Recovery PID 1 Log in image 76d640cd…</code>. Revision: `ed8f382d36ea0d3ebaa3a1582aa8e03410c9645d`.
- `host`: [The isolated 4 KiB ARM64e source kernel linked at 0xfffffff007004000 with 38-bit bootstrap translation. Its SHA-256 is 27a8b2c7… and the verified RAM image is 3e64fc1a…. The on-device loader's ARM64e admission checks both PAC features.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>scripts/build-elden-macos26-bootstrap.py; scripts/darwinboot_preflight.py --arm64e; scripts/verify_phase2_artifact.py</code>. Revision: `ca57db73c066162323e77156a9f0f1d72b1de4ff`.
- `device`: [The tablet entered the macOS source kernel and lit bootstrap stages 0 through C green. D through F were blue mapping indicators. Kernel entry is confirmed. The first translated instruction, arm\_init, and Recovery media remain unverified.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>fastboot boot elden-macos26-4k-ram.img and select Elden macOS 26.5 - 4 KiB Kernel Entry</code>. Revision: `ca57db73c066162323e77156a9f0f1d72b1de4ff`.
- `host`: [The retest derives framebuffer descriptor geometry from XNU's selected granule. Disassembly confirmed L1 shift 30 and L2 shift 21 with 9 index bits. The three Elden framebuffer blocks and the embedded RAM image 1f6faa01… passed host checks.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Rebuild with the 4 KiB bootstrap trace overlay and verify elden-macos26-4k-r2-ram.img</code>. Revision: `dbbd614ab15e97b1c4b93aac1f471771ddba8782`.
- `device`: [The device panic UUID FB8F5446-4A2F-3991-916F-148E0D3DB677 matched the retest. XNU passed arm\_init and reached kmem\_range\_init. The 128 GiB macOS zone claim exceeded the approximately 46 GiB hole, producing a wrapped private data claim. Recovery storage was not in this image.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>RAM boot elden-macos26-4k-r2-ram.img and select Elden macOS 26.5 - 4 KiB Kernel Entry</code>. Revision: `dbbd614ab15e97b1c4b93aac1f471771ddba8782`.
- `host`: [The linked startup spec now claims 24 GiB for zones. The build, firmware input preflight, embedded image checks, and MacBook checksum passed for image 7a4c686c…. The owner-operated menu test is a separate checkpoint.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Rebuild the small-map kernel and verify elden-macos26-4k-r3-ram.img</code>. Revision: `ca57db73c066162323e77156a9f0f1d72b1de4ff`.
- `device`: [Panic UUID 3021AE3E-E615-31E6-9E7C-3A85656F42E0 confirmed the small-map kernel passed kmem\_range\_init and reached IOKit. The first data abort dereferenced a null interrupt-parent entry in IODTGetICellCounts.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>RAM boot elden-macos26-4k-r3-ram.img and select the kernel</code>. Revision: `ca57db73c066162323e77156a9f0f1d72b1de4ff`.
- `host`: [The GIC AAPL,phandle matches the existing phandle and the UFS interrupt-parent. The three-cell IRQ specifier is unchanged. The embedded image b3dd3c4a… passed preflight and byte comparison.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Generate and inspect the Elden ADT with the interrupt phandle overlay</code>. Revision: `95ad78129203442c3c14c02336303adbddf8d0a3`.
- `device`: [The device passed IOKit interrupt-parent parsing and advanced to platform UUID setup. The next data abort at 0xfffffff007a8bb68 was SHA1Init dereferencing the absent corecrypto provider.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>RAM boot elden-macos26-4k-r4-ram.img and select the kernel</code>. Revision: `ca57db73c066162323e77156a9f0f1d72b1de4ff`.
- `host`: [The paired dSYM and 15-module prelink passed relocation and DarwinBoot input checks. Kernel 4d561d48… has 144975 chained pointers, 62884 authenticated, and no instruction blockers. Image b6dd5633… passed embedded payload checks and the MacBook checksum.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>emit_macos26_security.py --elden-bootstrap --recovery-components and verify elden-macos26-4k-r5-ram.img</code>. Revision: `ca57db73c066162323e77156a9f0f1d72b1de4ff`.
- `device`: [The device passed the previous SHA1 initialization fault and reached ArmCpu startup. Panic UUID 3021AE3E-E615-31E6-9E7C-3A85656F42E0 reported CPU 0 registration failed: 5. The original lookup masks Aff2, aliasing ADT affinities 0x0 and 0x10000 when cpus=1.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>RAM boot elden-macos26-4k-r5-ram.img and select the Recovery Components entry</code>. Revision: `ca57db73c066162323e77156a9f0f1d72b1de4ff`.
- `host`: [The ADT contains one boot CPU match under the Aff2-inclusive mask. Disassembly of ml\_get\_cpu\_number confirms the 24-bit mask, and the 15-module prelink and embedded image checks passed. The retest UUID is 4BC95A0C-8278-3B67-A060-99E592519074.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Rebuild the Elden source kernel, emit paired modules, and verify elden-macos26-4k-r6-ram.img</code>. Revision: `ca57db73c066162323e77156a9f0f1d72b1de4ff`.
- `device`: [Panic UUID 4BC95A0C-8278-3B67-A060-99E592519074 passed CPU registration. The paired dSYM resolves the next panic to the ml\_unsafe\_kernel\_text assertion at machine\_routines.c:3384.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>RAM boot elden-macos26-4k-r6-ram.img and select the Recovery Components entry</code>. Revision: `ca57db73c066162323e77156a9f0f1d72b1de4ff`.
- `host`: [The only non-ephemeral ADT change was the little-endian u32 policy value 1 for kernel-ctrr-to-be-enabled. The kernel and firmware hashes match the previous candidate, and image a58bff66… passed the embedded FAT and MacBook checksum checks.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Generate the Elden ADT with the restrictive text policy and verify elden-macos26-4k-r7-ram.img</code>. Revision: `95ad78129203442c3c14c02336303adbddf8d0a3`.
- `device`: [The owner photo shows PE\_lockdown\_iokit, successful APFS module loading and registration, and IOFindBSDRoot waiting on the fallback Apple\_HFS IOMedia match. The text-policy assertion is cleared. No Recovery root was attached and no userspace launch is shown. NVRAM sync reports no controller.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>RAM boot elden-macos26-4k-r7-ram.img and select the Recovery Components entry</code>. Revision: `43bc768e965363f0d2c73838b01caf246e5431cc`.
- `device`: [Image 8f4103d1… ran at EL1 on Elden. Both direct aliases returned the expected PCs and data read back as 0x5757. Execution, register readback and firmware restoration all passed. XNU was not part of this probe.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Select the 4 KiB 47-bit control and photograph the result</code>. Revision: `c1bc42e59c647d5cedbf2a3a0ed3c5787747bbc2`.
- `device`: [Elden returned bank-switch=PASS flags=7FFF expected=7FFF and EFI Success. Boot-CPU address and generic PAC, key discrimination, and firmware key/SCTLR restoration passed. XNU task and thread PAC remains unverified.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>RAM-boot 800e8b7e… and select the EL1 PAC probe</code>. Revision: `c1bc42e59c647d5cedbf2a3a0ed3c5787747bbc2`.
- `device`: [Active TCR 0x475113514 and TTBR1 0xccc64000 matched, and firmware restoration passed. The first direct fetch at 0xffff800000004000 faulted with ESR 0x86000002. EL1 MMFR0 0x2100122100001024 reports no stage-1 16 KiB support and reports 4 KiB support.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Select the direct 16 KiB execution probe and photograph the result</code>. Revision: `5661c8899873d82d9ca45113f90f7f6ce39decf6`.
- `device`: [The Elden bootloader accepted the transfer and RAM boot of 4 KiB control image 8f4103d1…. The linked EFI and independent 47-bit 4 KiB table walk passed host checks. On-screen execution is pending.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>fastboot boot ~/Downloads/elden-el1-native47-4k-ram.img (MacBook USB)</code>. Revision: `3ee06f7bd7a8284c55be6db4a52f96d4834abc88`.
- `host`: [The opt-in firmware menu accepts help, list, status and configured boot IDs via EFI Serial I/O. Sanitized host parser tests, firmware link, phase 2.3 checks and the MacBook checksum passed for image 6fb0e19c…. Physical TTY and pre-boot USB CDC are unverified.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Apply the serial menu overlay, build_phase2_firmware.py --output-dir out/elden-tty/firmware, and verify the packaged RAM image</code>. Revision: `c62bf12595f9a86c1b7282cf12d5af40b441fdac`.
- `device`: [Tablet reached EL1 and restored firmware state. The first AT S1E1R raised ESR 0x96000010 with FAR 0xffff800000004000 and ELR 0xcccb80a8 before either indirect call.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Select the EL1 16K 47-bit probe after the Elden RAM boot and photograph the result</code>. Revision: `2bba508f26d6bac75d3766e537b765bdb7756e10`.
- `host`: [The direct-execution overlay builds against the pinned reference and its two indirect calls are present without AT instructions in the temporary translation phase. Image 6ec54f8b… passed structural checks and MacBook copy verification. The tablet result is pending.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>Build the direct EL1 follow-up and verify it with scripts/verify_phase2_artifact.py</code>. Revision: `ca57db73c066162323e77156a9f0f1d72b1de4ff`.
- `device`: [Elden bootloader fastboot returned OKAY for the transfer and boot of direct-execution image 6ec54f8b…. The on-screen result is pending.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>fastboot boot ~/Downloads/elden-el1-native47-direct-ram.img (MacBook USB)</code>. Revision: `4d25676a90f77263b306b5d73177efa9ee836995`.
- `host`: [2026-11-10: QEMU 11.1.1 booted ARM64 UEFI and passed all six reference EL1 cases for PAC, 16 KiB translation, and 47-bit execution. Evidence covers the emulator and standalone probes.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>python scripts/test_el1_native.py and python scripts/test_el1_native.py --layout47 (macOS-ForSheng reference, with Clang and QEMU paths)</code>. Revision: `ca57db73c066162323e77156a9f0f1d72b1de4ff`.
- `host`: [2026-11-10: BaseSystem identified as macOS 26.5 build 25F71 with ARM64e launchd and dyld. The raw Recovery disk and manifest-matched root hash were prepared for QEMU.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>python scripts/prepare_macos26_recovery.py and python scripts/prepare_macos26_block.py (macOS-ForSheng reference, with verified 25F71 inputs)</code>. Revision: `ca57db73c066162323e77156a9f0f1d72b1de4ff`.
- `host`: [2026-11-10: The Apple silicon build host linked the macOS 26.5 kernel and paired dSYM. The kernel reached arm\_init through QEMU UEFI and DarwinBoot, with matched instructions and 16 KiB / 47-bit EL1 translation.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>python scripts/observe_macos26_kernel.py --checkpoint arm_init (macOS-ForSheng reference, with the linked ARM64e kernel and EFI firmware)</code>. Revision: `ca57db73c066162323e77156a9f0f1d72b1de4ff`.
- `host`: [2026-11-10: QEMU mounted the paired 25F71 APFS BaseSystem and executed the original launchd LC\_MAIN entry in EL0. Recovery services started. WindowServer restarted and the language chooser had zero starts.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/MACOS-RECOVERY-BRINGUP.md)
  Command: <code>python scripts/observe_macos26_kernel.py --checkpoint thread_setentrypoint --follow-init-entry --follow-launchd-main --let-vector-log (macOS-ForSheng reference, with the paired QEMU Recovery inputs)</code>. Revision: `ca57db73c066162323e77156a9f0f1d72b1de4ff`.
- `host`: [Base revision plus local working-tree patches. 2026-11-07: panic duplication is fixed and device-confirmed. New generic MIT DWC3 core plus guarded elden adapter, nonblocking console ring, bounded panic drain, session-bound status and PID1 EL0 syscall observation are built; CDC hardware remains unqualified.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/STARTUP-USB-CANDIDATE-20261107.md)
  Command: <code>python edl_work/audit_startup_candidates.py (Y700 work repository)</code>. Revision: `33b55083a0b61630f71478230f648606163115eb`.
- `source`: [Panic duplicates originate from console output plus PE\_kputc pointing to console\_write\_unbuffered. Both panic entry points now skip only that aliased second sink; panic buffer and independent future USB sink are preserved. Build and hardware checks pending.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PANIC-CONSOLE-ALIAS-20261107.md)
- `host`: [2026-11-06 prerequisites: final EFI31744-byte application passes FDT mailbox, parent metadata and memory-report contracts, and reaches the same XNU registration return1 through the neutral-debug AAVMF driver. Known-read expectations are prepared but were not sampled on the tablet. Source revision plus local working-tree changes.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PREREQUISITES-20261106.md)
  Command: <code>.venv/bin/python scripts/build-payload-loader.py</code>. Revision: `33b55083a0b61630f71478230f648606163115eb`.
- `host`: [2026-11-06 host: source GOP console kernel/archives/prelink completed; separate read-only UFS root-check archive compiled with inherited identity DMA and LUN selection. TWRP/Linux EFI prototype and userdata/ESP design remain hardware-unverified. Details and bounded evidence in docs/NIGHT-BRINGUP-20261106.md; no stock index change or device write. Revision plus local working-tree patches.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/NIGHT-BRINGUP-20261106.md)
  Command: <code>.venv/bin/python third_party/UniXNU/unixnu build kernel -D . -j4</code>. Revision: `33b55083a0b61630f71478230f648606163115eb`.
- `host`: [2026-11-05 offline: marker menu fallback is 600 seconds; NativeUfs probe 2 deliberately panics to display read-only GCC/UFS diagnostics. Probes 7/8 inspect SMMU/CB; SM8750 rejects probe 3. This changes acceptance wording, not the driver. See docs/OFFLINE-PAYLOAD-20261105.md. Source revision plus uncommitted local packaging changes.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/OFFLINE-PAYLOAD-20261105.md)
  Command: <code>.venv/bin/python scripts/build_offline_ufs_packet.py --fd out/phase3/old-fd-verified.bin --source-payload out/phase3/payload-fat16.img --kernel third_party/UniXNU/out/elden/ipados-17.7.11-21H461/elden-ufs_probe/kernel/kernel.macho</code>. Revision: `33b55083a0b61630f71478230f648606163115eb`.
- `source`: [Historical phase 1 size/hash table. The local-only out/build.json is absent on this checkout; this reference does not certify a new phase 1 build.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE1-STATUS.md)
- `source`: [The elden Linux reference now matches soc/sm8750/soc.toml at h0cheung/tb322fc-linux-kernel 6f97250ead155fc3b980856323e99a4623dae73d.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/unixnu.lock)
- `host`: [2026-10-25: a fresh phase 1 rebuild completed in 6:46 and passed static Android v3, shim, FD, embedded FAT and module checks. Image SHA-256 was 94b6a6315b04fc9d276bc15e9519107be292244380fc3bf139f5af6c96a3bb0a and FD SHA-256 was e5420517d55f4b638c07617a252d3a65c95cfb731584dcb10dd1d98bae412580; no device boot was performed.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2-STATUS.md)
  Command: <code>.venv/bin/python scripts/build_phase1.py --skip-submodules --crypto-path $PWD/.cache/phase1/basecrypto</code>. Revision: `dffc3020a85830d0d981a85871d9ab31aac5827d`.
- `device`: [2026-10-25: owner confirmed two RAM cold boots of image 94b6a6315b04fc9d276bc15e9519107be292244380fc3bf139f5af6c96a3bb0a; both reached the usable UniXNU menu and stock Android resumed after exit. This evidence covers phase 1 only.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2-STATUS.md)
  Command: <code>fastboot boot out/elden-phase1.img</code>. Revision: `dffc3020a85830d0d981a85871d9ab31aac5827d`.
- `host`: [2026-10-25: DTC 1.8.1-gf99e3af0 generated a 1,557-byte DTB with SHA-256 60316b6d4e753610610126d691f6d39ba54edd21e9b02875ec034e81e27a4371; round-trip inspection found the expected compatible strings, CPU MPIDRs, PSCI, GICv3, timer and DRAM data.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2-STATUS.md)
  Command: <code>.cache/dtc-src/dtc -I dts -O dtb -i soc/sm8750/dts -o /tmp/elden-phase2.0.dtb dts/elden.dts</code>. Revision: `f99e3af0ecb67a9085478a9b8ddbcc25aa64931d`.
- `host`: [2026-10-25: live-FDT audit produced a 13,152-byte ADT. Independent checks passed for C2400000+10000000 RAM/reservation/initrd coverage, UEFI DXE conventional memory, framebuffer, eight MPIDRs, one running boot CPU, GIC, timer, CHRP NVRAM, optional placeholders and sleep-disabled=1. Report: .cache/phase2.1-live/audit.json.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2.1-STATUS.md)
  Command: <code>.venv/bin/python scripts/phase2_1_audit.py --firmware-dtb .cache/device/elden-live.fdt --output-dir .cache/phase2.1-live</code>. Revision: `16e592abee8a550dec8154ed1f38b5ebc4f16213`.
- `host`: [2026-10-25: native kernel audited as arm64/iOS 17 with 4 KiB TG0 and TG1; 1,010 target objects passed; the pinned prelink XML lexer accepted 7,730 tags. No device checkpoint is claimed.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2.2-STATUS.md)
  Command: <code>python3 scripts/audit-xnu-kernel.py build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/mach.development.bcm2837.unstripped.noctf &amp;&amp; python3 scripts/audit-xnu-objects.py &amp;&amp; python3 scripts/check-prelink-xml.py ../kernel/kernel.macho</code>. Revision: `c91a2191fdf591a401a03027ed8b7fbfdbcad3a7`.
- `device`: [2026-11-01: owner booted both phase 2.3 embed-payload images; each reached the UniXNU menu with the green payload checkpoint, printed config: \\EFI\\UniXNU\\unixnu.toml and listed the ELDEN 2.3 INITRD 56M entry, proving the payload HOB, BlockIo, FAT16 mount and config discovery chain on device.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE2.3-STATUS.md)
  Command: <code>fastboot boot out/phase2.3/elden-phase2-embed-probe.img &amp;&amp; fastboot boot out/phase2.3/elden-phase2-embed-boot.img</code>. Revision: `509bc088641cb6d56d2a28b5526adb72dc88d51d`.
- `device`: [Screen capture of the phase 2.3 56 MiB payload menu before the scale fix: config read from the embedded volume, entries ELDEN 2.3 INITRD 56M and Restart, green checkpoint band, footer truncated at scale 7.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/assets/phase23-menu-embed-20261101.jpg)
  Command: <code>fastboot boot out/phase2.3/elden-phase2-embed-boot.img</code>. Revision: `509bc088641cb6d56d2a28b5526adb72dc88d51d`.
- `device`: [Two cold boots reached DISPLAY OK, INPUT OK, config loaded and menu shown.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/docs/PHASE1-STATUS.md)
  Command: <code>fastboot boot out/elden-phase1.img</code>. Revision: `c591b1a0a471f24978aba25c56c8f6ec9bd06668`.
- `device`: [Screen capture shows the rendered UniXNU menu on the tablet.](https://github.com/TAY0123/UNIXNU_elden/blob/d2759a06f3713ed97c347824a4f100ce83269949/assets/phase1-menu-20261025.jpg)
  Command: <code>fastboot boot out/elden-phase1.img</code>. Revision: `c591b1a0a471f24978aba25c56c8f6ec9bd06668`.

</div>
