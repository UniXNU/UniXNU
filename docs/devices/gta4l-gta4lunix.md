# Samsung Galaxy Tab A7 10.4 \(2020\) \(gta4lunix\)

[gta4lunix/UniXNU-gta4l](https://github.com/gta4lunix/UniXNU-gta4l)

<div v-pre>

Samsung Galaxy Tab A7 10.4 \(2020\) Format 2 migration; PMGR-linked host kernel, tablet RAM-root/EL0 fixture success and bounded QEMU checkpoints, eMMC bring-up pending.

Source record: [porting.toml](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/porting.toml), `53d3a82d1f81f0f3a28212b0981d5e82dc2577b9`.

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

Components: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`, `DarwinBoot`.

### Hardware and dependencies

- Format 2 architecture, SM6115 SoC, iPadOS 17.7.11 21H461 and device profiles; board.toml and configs/gta4l\_defconfig; the shared SM6115 DTSI.

### Configuration

- board.toml schema\_version=2, soc\_source=sm6115 and os\_profile=ipados-17.7.11-21H461; CONFIG\_XNU\_NATIVE\_PAN=n; CONFIG\_XNU\_ARMCPU=y and CONFIG\_XNU\_NATIVE\_ARCH\_TIMER=y; output out/gta4l/ipados-17.7.11-21H461/gta4l.

### Procedure

- ./unixnu defconfig gta4l\_defconfig -D ../UniXNU-gta4l; ./unixnu fetch -D ../UniXNU-gta4l; ./unixnu status --json -D ../UniXNU-gta4l; ./unixnu build kernel -D ../UniXNU-gta4l.

### Development findings

- The SM6115 Cortex-A73/A53 cores are ARMv8.0 and do not implement PAN; the shared ARM64 profile enables PAN, so the board overrides CONFIG\_XNU\_NATIVE\_PAN=n. TB128FU records the same undefined-instruction failure and the same override.
- The Format 2 resolver selects the expected arch/SM6115/OS/device layers and the output path above; the PT\_LOAD/ADT records are built from dts/gta4l.dts and the shared SM6115 DTSI.
- The TB128FU device repository \(xVanTuring/UniXNU-tb128fu\) is the pinned reference for the timer, IPI and PMGR questions; docs/tb128fu-comparison.md records its credit, revisions and the limits on reuse.
- The .circleci workflow credential patch is scoped to trusted HTTPS GitHub hosts and strips the token headers on cross-host redirects; the porting record owns the removed gemini-code helper path so the gate accepts its deletion.
- The SM6115 SoC feed now points at gta4lunix/UniXNU-sm6115-common; the pinned commit is unchanged.

### Completion criteria

- All source pins resolve; every selected component has a record; status shows the intended overrides and patch order.

### Current limits

- The host kernel build and prelink pass. The successful tablet RAM-root image uses a test-scoped ad-hoc signed fixture and owner trust bundle; it is not an authenticated-root or production security result.

### Next action

- Use the explicit diagnostic payload builder and the mandatory payload/ADT contract for raw RAM-root images; keep the pinned v5 baseline and the byte-identical v2 reproduction. The next packaging change is required only for a new documented baseline or payload format.

### Evidence

- `source`: [Records the RAM-root report fixture result: PID 1, 4096-byte pages and mockfs exec; image sha256 45ecc93049757e97a8d71edb776f67e69df5c9c58be13543295c154637273e24; artifact out/gta4l/ram-root-report-evidence/ \(gitignored\).](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/docs/build-revisions.md)

## Firmware and boot {#firmware}

`planned`

### Hardware and dependencies

- Identify the firmware and boot hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for firmware and boot.

### Procedure

- Follow the firmware and boot stage in the porting guide and record the actual commands.

### Development findings

- Collect the first firmware and boot observation, its cause when established, and the resulting implementation decision.

### Completion criteria

- Firmware image builds, enters UniXNU, publishes the framebuffer and preserves the documented memory reservations.

### Current limits

- Hardware inputs and implementation are pending for this example board.

### Next action

- Inventory the required firmware and boot inputs before implementation.

### Evidence

Collect evidence using the next action.

## CPU and interrupts {#cpu}

`planned`

Components: `ArmCpu`.

### Hardware and dependencies

- SM6115: four Cortex-A53 and four Cortex-A73 cores, PSCI 1.0 SMC, GICv3 distributor 0xf200000 and redistributor 0xf300000 with 0x20000 stride, 19.2 MHz timebase, timer PPIs 1/2/3/0.

### Configuration

- CONFIG\_XNU\_ARMCPU=y, CONFIG\_XNU\_NATIVE\_ARCH\_TIMER=y, CONFIG\_XNU\_NATIVE\_PAN=n; dts/sm6115.dtsi timer interrupts &lt;1 1&gt;, &lt;1 2&gt;, &lt;1 3&gt;, &lt;1 0&gt;; candidate boot argument armcpu-timer-intid=19.

### Procedure

- Boot the boot CPU first with the timer diagnostic counters; compare INTID 27 and INTID 19; test SGI delivery before enabling any SPI-IPI workaround.

### Development findings

- The live timer specifiers match TB128FU: PPI 3 is the EL1 virtual timer, so INTID 19 is the gta4l candidate. The current ArmCpu default is 27 and INTID 27 may be another asserted source on this SoC; this is not yet measured on gta4l.
- TB128FU found SGIs undelivered and used software-pended SPIs 504..511 \(INTIDs 536..543\). Its GIC capacity and unused-line inventory do not transfer to gta4l; do not enable SPI IPIs before measuring ours.
- The TB128FU ArmCpu fork does not retain GICv2. Port only its timer/IPI mechanisms with per-device defaults so the shared GICv2 path stays intact.

### Completion criteria

- Every enabled CPU reaches its entry checkpoint and timer/IPI handling works on each enabled CPU.

### Current limits

- The kernel links on the host and the boot CPU ran the bounded fs/timer fixture on the tablet; that fixture's single blocking poll does not establish sustained timer stability. Secondary-CPU bring-up and IPI delivery are untested.

### Next action

- Port the timer selection with the 27 default, test INTID 19 on the boot CPU, and record the interrupt counters before starting secondary CPUs.

### Evidence

Collect evidence using the next action.

## Memory and DMA {#memory}

`planned`

### Hardware and dependencies

- Captured SM-T505N FDT memory map; DarwinBoot/firmware reservations; 3 GiB dram\_info; ADT generator's one-range requirement.

### Configuration

- dts/gta4l.dts memory@40000000 reg = &lt;0 0x40000000 0 0xc0000000&gt;; board.toml payload dram\_size=0xC0000000 and payload.adt owned\_memory\_size=0x80000000.

### Procedure

- Compare the three live banks, the ADT span and the firmware reserved-memory map; confirm the free window before any hardware test.

### Development findings

- The live FDT reports three banks: 0x40000000+0x3e580000, 0x80000000+0x20000000 and 0xa0000000+0x60000000, with a hole at 0x7e580000..0x80000000. The ADT generator requires one range, so 0x40000000+0xc0000000 is a physical span that includes the hole, not a contiguous free map.
- After the live no-map regions and the Mu-Silicium DDR reservations, the largest contiguous free run is 0x80000000..0x100000000 \(2 GiB\). DarwinBoot requests that window; the previous 3 GiB request had no qualifying run and would stop at NO WINDOW.
- The captured unit reports 3 GiB; TB128FU's 0x180000000 span and 0x100000000 owned window describe a different memory population and must not be copied.

### Completion criteria

- All handoff regions are accounted for and each enabled DMA engine accesses its allocated range with the documented cache policy.

### Current limits

- The 2 GiB window is a static derivation from the live FDT and Mu-Silicium map; the runtime UEFI map has not been observed on the tablet. The first boot must validate DarwinBoot's allocation.

### Next action

- Boot the diagnostic image with the 2 GiB request and capture DarwinBoot's BIG RUN/FREE rows if it fails; do not change the window without those rows.

### Evidence

Collect evidence using the next action.

## Storage and root {#storage}

`planned`

### Hardware and dependencies

- Identify the storage and root hardware, resources and existing component interfaces for this board. Reference-only inputs: limonabisi/linux-gta4l gta4l-7.2 at cf5f763f0ef8a5b4d8bb4163833cba1160c51894 \(board DTS credits V6lhost; SoC DTSI credits Iskren Chernev\) and itsChris122/UniXNU-guamp at 6be83ac10b4eee84d504266bb8d12ef64a083acc and Dracen-W/NativeEmmc at 4980f1070b0c822dedb9eb350df710a57df28590 \(maintainer Dracen; catalog community-native-emmc; static audit in docs/native-emmc-reference-audit.md\). No reference code is imported.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for storage and root.

### Procedure

- Read the live FDT, primary/backup GPT and recovery sysfs read-only; validate GPT CRCs and array equality with scripts/verify-gpt.py; resolve controller resources from the stock FDT before implementation.

### Development findings

- RAM-backed mockfs root and a signed static EL0 fixture succeeded on the tablet without the AMFI bypass arguments: PID 1 and 4096-byte page-size syscall observed. The fs/timer fixture then passed with reads of distinct 4 KiB pages, seek/reopen/EOF and one blocking poll\(\) timeout. These are bounded fixture results, not an eMMC or authenticated-root result.
- Recovery inventory: eMMC is mmcblk0 at /sys/firmware/devicetree/base/soc/sdhci@4744000, compatible qcom,sdhci-msm-v5/qcom,sdhci-msm-cqe; registers are 0x4744000+0x1000, 0x4745000+0x1000 and 0x4748000+0x8000; clocks are iface\_clk, core\_clk and ice\_core\_clk; reset is core\_reset; supplies are vdd and vdd-io. Recovery reports HS400 Enhanced Strobe, CQHCI and 64-bit ADMA.
- The eMMC is a 29.1 GiB DX68MB \(Samsung CID 150100445836384d42009005f4661900, CSD d02701320f5903fff6dbffef8e404000, 61,071,360 logical 512-byte sectors\). The live FDT matches the pinned stock FDT and the CRC-valid primary/backup GPTs agree on 80 partitions. These are recovery observations, not an XNU driver result.
- The corrected v5 observation-only snapshot ran on the tablet and reported v=10000072 \(major 1, minor 0x72\), sv=7202, c=742dc8b2, c1=0000808f, ps=01f800f0, clk=0003, pwr=00, hc=00, hc2=0000, is=00000000 and ie=00000000. This establishes the v5 version offset and the gated map/read/panic path, not card protocol or storage access.
- A separate read-only XNU handoff audit now observes the SM6115 GCC SDCC1 reset/branch/RCG state and the v5 vendor power status/mask, capability and DLL state without writing or acknowledging power requests. Its first boot image was withdrawn after a BOOT-only packaging failure \(minimal DTB instead of the working v5 boot DTB\); the pre-flash BOOT partition was restored and confirmed, and a corrected image preserving the v5 boot header, firmware, boot DTB and boot kernel section exactly then booted and completed the read-only audit. It reports bcr=00000000, ac=00004221, ahb=00000001, ice=00004229, cmd=00000000, cfg=00000401, m=00000001, n=000000fe, d=000000fd, clk=0003, pwr=00, pst=00000000, pm=00000000 and dll=00000000. This is register-level handoff evidence, not card or storage access.
- The bounded host-local init probe is implemented in package/Gta4lSdhciHostInit.c/.h and compiled into the diagnostic archive \(archive sha256 3cccb9e9d25a7e93b470c718e50b53edf50b975956259b37c851538f9c730b0f; host-init object sha256 2dac8c6e09d510e2d2c052aa599f630eec7950cc932547dd71657de793c7f2b9\). It writes only SDHCI interrupt enable/signal enable \(0x34/0x38\), standard software reset \(0x2F\) and clock control \(0x2C\); disassembly shows no other MMIO stores. scripts/test-gta4l-sdhci-host-init.py passes its allowlist, write-contract, conflict and bounded-wait self-test; the audit hardened its MMIO check to reject reordered volatile qualifiers, typedef-hidden stores, whitespace-split stores, pointer-index stores and non-volatile pointer casts and added matching self-test cases; those source patterns are guardrails, not a proof of absence. scripts/test-gta4l-sdhci-host-init-sim.py replaces the production MMIO helpers with logging hooks, asserts the exact write sequence, records every read and write so a same-value transient write is rejected, and disassembles the run function to confirm a pointer-index mutation adds memory stores the event trace would not see. and covers conflicting arguments, an absent boot argument, an SDHCI map failure, a GCC-only map failure, bus power, reset timeout, unstable clock, interrupt suppression with nonzero enable registers, an ignored interrupt-clear failure, a pending vendor power request, a device-side vendor change, GCC reset/branch/RCG preconditions, delayed reset/clock completion, post-reset state changes and a stuck clock counter. The completion line is now HOST INIT REPORT with an explicit "vendor state reported, not enforced" qualifier; the historical tablet transcript keeps its earlier HOST INIT OK wording. The kernel relink succeeded \(kernel sha256 ba52b6500ec3d064d173fa06fba23cb42aa4850c0bddd0df9a4178666c084646\) and bsd\_init calls preflight/audit/snapshot/host-init in order. The first 80 MiB payload inherited packed\_data\_ramdisk=true, so its ADT reserved PackedRAMDisk while the raw N4KROOT scratch-data.img reports RamdiskPacked=FALSE; DarwinBoot returned EFI\_COMPROMISED\_DATA at the UniXNU picker. BOOT was rolled back byte-for-byte \(pre-flash backup 55d80d52a7246acec8277a8aeb40e38b2b2aac1eadef1e5d439579d86a7cd701; failed readback 73b7a586ee2498277dc77adc7b81714afa0662d36c8dfc48b8c0a2ec456e01b6; rollback readback 55d80d52a7246acec8277a8aeb40e38b2b2aac1eadef1e5d439579d86a7cd701\). The corrected payload sets packed\_data\_ramdisk=false; its ADT reserves RAMDisk, payload sha256 0afaae8d66251d61c74d80427289da5e79551e52652e5236adaac55c6c8ac8b1, boot image sha256 d4aee57a9d1874d23dc010b7de43384ace6ab29241f5ee18cb10f0a561bab133, and both the 18-check boot-image gate and scripts/check-gta4l-payload.py pass. Corrected v2 was then flashed to BOOT; the image-byte readback matches d4aee57a9d1874d23dc010b7de43384ace6ab29241f5ee18cb10f0a561bab133, the full partition readback is 7ff725aacfbd5e205f98c6c71229e59908e432491cda91d2257f566d2925874a, and the readback gate is 18/18 with the extracted payload contract passing. The owner's manual boot then completed the host-local probe: reset=00, clk=0003, pwr=00, ie=00000000, se=00000000, and unchanged vendor values g=00f04003, pst=00000000, pm=00000000, vs=00300a0c, ddr=80040873, dll=00000000. The GCC row is the pre-write capture. No card command, data transfer, DMA, storage write, bus-power enable or card-clock enable was issued. This is controller-local evidence, not PM6125 L24/L11 rail state. Evidence: out/gta4l/ram-root-sdhci-host-init-evidence/host-init-success.txt and host-init-success-photo.jpg \(photo sha256 672ecf61d0cb3e5675c5f511e88f3250a3f507afaf0acad84ee3153d97acc967\).
- The pinned mainline gta4l port at cf5f763f0ef8a5b4d8bb4163833cba1160c51894 enables sdhc\_1 without vmmc-supply or vqmmc-supply; pm6125\_l24a and pm6125\_l11a are defined but unreferenced, while only sdhc\_2 uses L22/L5. Its RPM path is GLINK over sram@45f0000 \(qcom,glink-smd-rpm\), not the live FDT's legacy qcom,rpm-smd node. This is a retained-rail design, not proof of the XNU-time rail state.
- The mainline qcom\_smd-regulator driver exposes cached is\_enabled and uV only; it has no RPM query or PMIC register read. qcom\_glink\_rpm\_probe writes zero to the TX head and RX tail and sends a GLINK version command, and opening rpm\_requests requires an open/intent handshake. A read-only XNU audit can inspect the RPM message-RAM TOC and FIFO pointers but cannot derive L24/L11 voltage or enable state, and must not reset the FIFOs or ring the mailbox.
- Step 4 records the board-level electrical-contract assessment in docs/sdhc-electrical-contract.md. It selects a bus-power-only candidate and finds all nine safety-critical areas \(E1–E9\) blocking: supply voltage/absmax, IO compatibility, current/loading, transients, sequencing, back-powering, retention, fault handling and recovery. DT ranges and current levels are operating intent, not measurements. Step 5 adds a versioned access trace, 33 deterministic scenarios, ten negative-control mutations and a separate-implementation oracle \(same author\) for the existing controller-local probe only; the oracle derives its rules from the header and write contract rather than the harness arrays. All host tests pass, but they do not cover bus-power or card-clock activation.
- Step 6 records a dated NO-GO decision in docs/sdhc-decision-memo.md for sdhc-bus-power-activation. The gate table fails electrical contract, starting state, access policy, software behavior for that candidate, independent assessment, recovery and authorization. No bus-power-only implementation, image, access policy or measurement exists; the host-local diagnostic approval does not transfer.
- The Dracen-W/NativeEmmc audit \(commit 4980f1070b0c822dedb9eb350df710a57df28590, maintainer Dracen\) is a host-only static review of a MediaTek MT6768 MSDC driver, not a Qualcomm SDHCI v5 port: its register map, command encoding, FIFO path and hardcoded userdata LBA are not transferable. Its staged boot arguments, IOBlockStorageDevice shape, write rejection, global controller lock, fail-closed manifest checks and exact-one-match IOMedia lookup are useful design references. The audit also records a completion gap \(success after draining bytes without XFER\_COMPL\), an unconfirmed stop-on-error path, no R1 card-status check, no window content-hash verification, and a source/license mismatch \(BSD-2-Clause-Patent versus BSD-2-Clause LICENSE\). No code was imported, built or run, and the repository documents no hardware result.
- The consolidated power/pad dependency report \(docs/sdhc-power-pad-dependency-report.md\) corrects the SdccDxe controller-local handshake: it sets the SDHCI bus-power bit, resets the controller, and writes the IO\_SUCCESS \(4\) or BUS\_SUCCESS \(1\) result bit to CORE\_PWRCTL\_CTL after bounded status/clear polls \(up to 10,001 reads each\) and a 10,000-read reset self-clear poll, with no PMIC/LDO/RPM action; CORE\_PWRCTL\_CTL carries success/fail results, not the BUS\_OFF/IO\_LOW request bits, which live in CORE\_PWRCTL\_STATUS. It is not a bus-power-on regulator sequence. The pinned pinctrl driver and sm6115.dtsi map the UEFI 0x9fe4 write at 0x575000 to the SDC1 QDSD group at west+0x75000, and the value matches the vendor sdc1\_\*\_on drive/pull fields, closing only the write-to-pad mapping part of E2. L24/L11 physical state, the SDC1 pad domain and actual levels, PM6125 fault semantics, electrical sequencing and recovery, and the CX/ICC/SMMU state remain unmeasured. No electrical E/S gate closes and the bus-power decision remains NO-GO; the next step is a measurement-only baseline or the missing datasheets, schematic, safe test points and recovery procedure. A host-only regression test, scripts/test-gta4l-sdccdxe-decode.py, pins the SdccDxe hash and the handshake instruction words and checks the captured-status selection, the three non-aborting timeout paths, the loop bounds and the TLMM pad decode; it does not execute firmware.
- The 2026-10-31 porting-approach reassessment records the owner-directed decision that software porting may proceed with the mainline Linux, vendor/LineageOS and captured-firmware stack as the reference, that electrical characterization is not a porting prerequisite, and that the NO-GO applies only to the on-device bus-power activation operation. It lists the dependencies to reproduce and keeps the residual electrical, RPM-retention, UEFI-volume and boot-medium risks open; no E1-E9 or S1-S4 gate is marked closed.

### Completion criteria

- Host: register, clock, link and SMMU facts match the board inventory.
- Reads: SCSI capacity, GPT and known blocks are correct; OS/SystemOS windows stay within userdata.
- Root: the configured volume mounts and launchd starts. Persistence: writes survive reboot within the allocated Data region.

### Current limits

- No XNU eMMC driver or XNU block-device result exists yet. Recovery inventory is read-only evidence and does not establish register, clock, DMA, power-domain or SMMU behavior under XNU. Recovery regulator state is not the XNU handoff state; the L24 reading was internally inconsistent \(state=disabled with num\_users=1 and microvolts=2960000\), so it does not prove the eMMC VDD rail is on at the audit point in bsd\_init.
- The v5 snapshot and handoff audit are register-level diagnostics. They do not establish the PMIC L24/L11 state, VDDCX power domain, interconnect bandwidth, SMMU stream ID or card protocol state.
- The pinned mainline port is source evidence only. Its no-supply sdhc\_1 design does not measure L24/L11 at XNU handoff and is not an XNU regulator control or readback path; the separate SPMI map in docs/pm6125-register-map.md is a register map, not an implemented readback.
- The NativeEmmc audit is static source review only. It does not establish that the reviewed driver builds, probes or reads on any device, and its MediaTek MSDC target does not exercise the gta4l SDHCI v5/CQE/ICE path, clock/reset/power sequencing, interconnect or SMMU. Its firmware-left-controller assumption is not satisfied by the gta4l handoff, and its hardcoded LBA and UUIDs are image-specific.

### Next action

- The host-local milestone is complete and the mainline RPM/regulator source trace is recorded in docs/rpm-power-interface.md. The pinned port has no L24/L11 consumer and no RPM readback; it relies on retained firmware rails. A separate SPMI readback map is recorded in docs/pm6125-register-map.md. Keep bus power and card clock off and issue no card commands, DMA or storage writes. Do not implement an RPM vote, SPMI regulator write or bus-power acknowledgement to learn the state. Next decision: accept a retained-rail contract only with the written board-level electrical contract and a direct rail measurement; a PMIC readback reports commanded state, not measured voltage, and substitutes for neither; the Mu-Silicium exit trace in docs/firmware-handoff.md shows the handoff writes no LDO control register but does not measure the rails, so it does not unblock the power stage. Keep the working RAM root throughout. Step 4 records the electrical-contract gap assessment in docs/sdhc-electrical-contract.md and Step 6 records NO-GO in docs/sdhc-decision-memo.md; do not treat the passing host-local tests or the oracle as permission for bus-power or card-clock activation. The next legitimate work is host-only evidence acquisition \(datasheets, schematic, firmware/RPM analysis\) and, only under a separately approved measurement procedure, direct rail/pad measurement. A bounded RPM/XBL static trace is recorded in docs/power-retention-evidence.md §7: it identifies the RPM LDOA resource tables for L11/L24, finds no referenced static table or stored pointer/resolvable PC-relative literal that selects either rail in the bounded scan, and finds no direct L11/L24 voltage, mode or enable write in the traced paths; the setter's class object and per-id array are built at runtime, and the runtime policy, PBS semantics and retention remain unresolved, so E7 stays blocking. The NativeEmmc audit in docs/native-emmc-reference-audit.md is a design reference for a future read-only XNU block device; it does not authorize controller commands, bus power or card clock, and it does not change the E7 or storage gates.

### Evidence

- `source`: [Decodes the recovery eMMC inventory: mmcblk0 at sdhci@4744000, v5/CQE, HS400 Enhanced Strobe, 64-bit ADMA; artifacts under out/gta4l/ram-root-fs-timer-evidence/ \(gitignored\). Records the KMDX60018M-B425 candidate \(32 GB eMMC 5.1 + 24 Gb LPDDR4X, 254FBGA\) from a Samsung product brief and a public UFI log, with the exact installed part and electrical limits still unresolved; also credits the Dracen-W/NativeEmmc reference and links its static audit.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/docs/emmc-reference.md)
- `source`: [Records the fs/timer fixture pass and the validated GPT inventory; image sha256 c12e601eceb8e5b5b9cf7a028c0f404653b67dc5ff5577813293673d2dea2b3a.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/docs/build-revisions.md)
- `source`: [Records the v5 observation-only snapshot \(version, capabilities, vendor power status\) and its artifact.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/docs/sdhci-snapshot.md)
- `source`: [Records the read-only GCC and vendor power handoff audit without acknowledging power requests.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/docs/sdhci-handoff-audit.md)
- `source`: [Records the bounded host-local init probe and its controller-local result.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/docs/sdhci-host-init.md)
- `source`: [Records the Step 4 board-level electrical-contract assessment for the bus-power-only candidate: nine blocking safety-critical areas \(E1–E9\) and the evidence-acquisition requirements.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/docs/sdhc-electrical-contract.md)
- `source`: [Separate-implementation host oracle \(same author\) for the controller-local access policy; derives read/write rules from the header and write contract, validates 33 traces, checks prerequisite values, interrupt-suppression confirmation on both initial-value paths, universal stage-local poll bounds, reset-clear ordering, the reset-to-clock observation window, the stable clock poll completion and immediate final confirmation before downstream accesses, the eleven required final stage-4 observations, and post-reset state, rejects ten source mutations plus forty-one synthetic trace controls, and accepts the valid initially-zero interrupt baseline.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/scripts/oracle-gta4l-sdhci-host-init.py)
- `source`: [Records the dated Step 6 NO-GO decision, the E1-E9/S1-S4 blocker dispositions and the separated baseline-measurement, controlled-activation and capability-approval gates for sdhc-bus-power-activation.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/docs/sdhc-decision-memo.md)
- `source`: [Host-only static audit of Dracen-W/NativeEmmc at 4980f1070b0c822dedb9eb350df710a57df28590: credits Dracen, separates reusable XNU block-device patterns from MediaTek MSDC-specific code, records completion/error-path and license findings, and proposes a host-only test plan without importing code or adding hardware evidence.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/docs/native-emmc-reference-audit.md)
- `source`: [Inventories the missing PM6125/eMMC/board documents and links each storage-blocking electrical and procedural gate to its canonical closure criterion; revision 2 separates staged approvals from gate closure, marks roles proposed, adds claim-level source references and the SPMI-arbiter gaps, and prepares the Phase 2 acquisition register; revision 3 completes shared-consumer and parent-supply tracking, separates USID, runtime-APID and descriptor-base evidence, and maps acquisition items to gates; revision 4 aligns the descriptor-base item with the 0x8878 override path and extends measurement tracking to E5-E7; revision 5 records the pinned-image descriptor-base scan; revision 6 corrects its scope after an audit, adds pointer-chain, overlap and pre/post-index controls, and leaves internal indirect/computed and runtime/external writers open; revision 7 strengthens the scan with XZR/SP separation, pointer-slot invalidation, a strict unsupported-instruction stop, and unresolved load/store, revisited-state and truncation reporting; revision 8 keeps conditional-branch paths independent, propagates their invalidation at function return, and stops seeding XZR roots; revision 9 records the exact-build package comparison and the vendor BUS\_ON trace; revision 10 narrows those claims after the broad host-only audit \(four full and six prefix BL matches, the rpm-smd-regulator backend and path caveats, and 64-bit scanner wrapping with unchanged result sets\); revision 11 records the official Samsung CXG1/CWI2 source comparison and the card-detect difference, the non-applicability of the inspected SM-T505 family pages, and the KMDX60018M-B425 candidate with its unresolved datasheet; no gate is closed and NO-GO remains.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/docs/sdhc-evidence-gap-checklist.md)
- `source`: [Records the owner-directed reassessment: software porting proceeds with the Linux/LineageOS/vendor and captured-firmware stack as the reference; the NO-GO is narrowed to the on-device bus-power activation operation, which still requires written owner approval and a verified EFS/CPEFS backup; dependencies to reproduce and residual risks are listed without closing any gate.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/docs/porting-approach-reassessment-2026-10-31.md)

## Display {#display}

`planned`

### Hardware and dependencies

- Identify the display hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for display.

### Procedure

- Follow the display stage in the porting guide and record the actual commands.

### Development findings

- Collect the first display observation, its cause when established, and the resulting implementation decision.

### Completion criteria

- A known frame appears with correct geometry and colors, then userland presentation and backlight controls work.

### Current limits

- Hardware inputs and implementation are pending for this example board.

### Next action

- Inventory the required display inputs before implementation.

### Evidence

Collect evidence using the next action.

## Input {#input}

`planned`

### Hardware and dependencies

- Identify the input hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for input.

### Procedure

- Follow the input stage in the porting guide and record the actual commands.

### Development findings

- Collect the first input observation, its cause when established, and the resulting implementation decision.

### Completion criteria

- Touches map to the display, simultaneous contacts keep stable IDs, release events arrive, and buttons produce expected HID reports.

### Current limits

- Hardware inputs and implementation are pending for this example board.

### Next action

- Inventory the required input inputs before implementation.

### Evidence

Collect evidence using the next action.

## GPU {#gpu}

`planned`

### Hardware and dependencies

- Identify the gpu hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for gpu.

### Procedure

- Follow the gpu stage in the porting guide and record the actual commands.

### Development findings

- Collect the first gpu observation, its cause when established, and the resulting implementation decision.

### Completion criteria

- GPU submissions complete, mapping/fence handling is correct, a known image renders, and the selected Metal client presents it.

### Current limits

- Hardware inputs and implementation are pending for this example board.

### Next action

- Inventory the required gpu inputs before implementation.

### Evidence

Collect evidence using the next action.

## Network {#network}

`planned`

### Hardware and dependencies

- Identify the network hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for network.

### Procedure

- Follow the network stage in the porting guide and record the actual commands.

### Development findings

- Collect the first network observation, its cause when established, and the resulting implementation decision.

### Completion criteria

- Scanning, association, address configuration and sustained receive/transmit traffic pass with the selected firmware.

### Current limits

- Hardware inputs and implementation are pending for this example board.

### Next action

- Inventory the required network inputs before implementation.

### Evidence

Collect evidence using the next action.

## Audio {#audio}

`planned`

### Hardware and dependencies

- Identify the audio hardware, resources and existing component interfaces for this board.

### Configuration

- Record the board.toml fields, DTS properties and defconfig values used for audio.

### Procedure

- Follow the audio stage in the porting guide and record the actual commands.

### Development findings

- Collect the first audio observation, its cause when established, and the resulting implementation decision.

### Completion criteria

- Each declared route carries the selected audio format through playback or capture and handles start/stop correctly.

### Current limits

- Hardware inputs and implementation are pending for this example board.

### Next action

- Inventory the required audio inputs before implementation.

### Evidence

Collect evidence using the next action.

## Power {#power}

`planned`

### Hardware and dependencies

- Original ApplePMGR consumer in the prelinked kernel; TB128FU original-PMGR bridge reference; gta4l PMIC, RPMh/RPM and clock resources are not yet inventoried.

### Configuration

- CONFIG\_XNU\_SHENG\_PMGR=y; board.toml archives append build-platform-power.py; device series applies patches/xnu/sheng-platform-power.patch; package/ShengPlatformPower.cpp and scripts/build-platform-power.py are adapted with credit from TB128FU a9c3863.

### Procedure

- Run the bridge audit against the original kernelcache and prelinked kernel, then boot with sheng-pmgr=2 and no AMFI bypass for the first bounded test.

### Development findings

- TB128FU's ShengPlatformPower bridge publishes the original ApplePMGRNub through an ABI-audited provider, reads and writes no hardware, and fails unsupported power operations explicitly.
- The audit passes against our original kernelcache f18b4df865405f2a287b84977d7aca745e056d656d9fc9df1662970ce2969de7 and prelinked kernel. The PMGR-linked kernel sha256 is dc8184da757b5323d2f4fb6c7ac1d588790b3d44d583c6d6fd24897cdbbcfe60; bsd\_init.o has XNU\_SHENG\_PMGR=1 and the kernel contains ShengPlatformPower and sheng\_pmgr\_run.
- QEMU TCG with sheng-pmgr=2 and no AMFI bypass reaches \_bsd\_init, \_sheng\_pmgr\_run and \_IOKitBSDInit with no AMFI 'No PMGR' panic and no \_panic checkpoint; it stalls at \_ml\_get\_timebase before \_vfs\_mountroot. Publication was not read back independently.
- The live FDT resolves /soc/sdhci@4744000 vdd-supply to phandle 0x1f7 \(/soc/qcom,rpm-smd/rpm-regulator-ldoa24/regulator-l24, pm6125\_l24\) and vdd-io-supply to 0x1f0 \(/soc/qcom,rpm-smd/rpm-regulator-ldoa11/regulator-l11, pm6125\_l11\). It reports L24 2,704,000-3,600,000 uV with init 2,704,000, L11 1,704,000-1,952,000 uV with init 1,704,000, SDHCI vdd level 2,960,000 uV, vdd-io level 1,800,000 uV, and qcom,vdd-io-always-on/lpm-sup booleans. No XNU RPM/RPMh/SPMI/regulator component exists; ShengPlatformPower is the Apple PMGR bridge, not a Qualcomm regulator driver. There is no supported XNU path to enable or set L24/L11, so the first host-local SDHCI probe keeps bus power and card clock off and reports the power stage blocked.
- The Mu-Silicium SDCC DXE ExitBootServices handler at SdccDxe.efi 0x81a8 configures the SDC1/SDC2 TLMM pads \(0x00575000/0x00973000\), sets SDHCI bus power, runs the v5 reset/power handshake \(0x240/0x248/0x24c\) and writes vendor registers; the reset clears the standard power and clock registers and the handler does not re-enable bus power, but has no PMIC/SPMI/LDO/RPM-request path. PmicDxeLa.efi 0x4220 locates the PMIC protocol GUID cea4489f-da0d-43d9-a3b2-766977a109f7 and calls the interface entry at 0x41ec, which issues SPMI writes at register bytes 0x14, 0x16 and 0xd1 only. Those addresses cannot reach the PM6125 LDO control registers 0x40/0x41/0x45/0x46/0x48/0x4c/0x61, so the two traced callees cannot directly write the L11/L24 enable or voltage registers. That is a direct-address exclusion, not proof that the callback leaves the rails unchanged: the 0x28 entry performs a read/modify/write of the arbiter IRQ clear register \(v5 interpretation\) over bitmap-selected APIDs \(instruction sequence resolved; runtime bitmap unresolved\), and for peripherals with the PMIC interrupt layout 0x14/0x16 are QPNPINT\_REG\_LATCHED\_CLR and QPNPINT\_REG\_EN\_CLR, so the writes clear latched interrupts and mask interrupt delivery. The 0xd1 value is u16&gt;&gt;14, so it can be 0-3, not necessarily zero. uefiplat.cfg has no LDO entries. During initialization the same IRQ status/clear routine runs via 0x266c -&gt; 0x2d90, and 0x2d90 then calls 0x2ec8 with w3=0, which clears access-enable bit 0 for entries that pass its checks. The recovery path \(0x27bc -&gt; 0x3904\) writes arbiter owner/APID registers at base+apid\*4+0xa700 and base+apid\*4+0x40900 when its conditions permit, though it is not proven to have run during the recorded boot. A null configuration pointer in the 0x120a8 exit callee reaches a non-returning self-loop, so the callback can hang instead of returning an error. See docs/firmware-handoff.md.
- qcom\_spmi-regulator.c carries a PM6125 regulator table giving L11 peripheral 0x4a and L24 peripheral 0x57, with the common layout VOLTAGE\_RANGE 0x40, VOLTAGE\_SET 0x41, MODE 0x45 and ENABLE 0x46, so L11 enable is address 0x4a46 and L24 enable is 0x5746. The board DTS uses qcom,rpm-pm6125-regulators rather than qcom,pm6125-regulators, so the proven path is RPM-owned regulation, not AP-side SPMI access. Three limits keep this from being a ready probe: the vendor live.dts bounds the LDO USID to 0 or 1 but has no regulator subnode, so no pinned source chooses between them; voltage encoding is ops-dependent, with ldo/smps on the range/selector getter and ftsmps426/hfs430/hfsmps on the two-byte millivolt getter, and both getters return a software selector rather than microvolts; and pmic\_arb\_read\_cmd issues the command with writel\_relaxed into the observer window, where the 1000 us bound covers only the transaction poll, not the APID mapping walks. The audit in docs/pmic-audit.md blocks the probe: identity, the runtime callback state and the board-level electrical contract are all unresolved.
- docs/linux-regulator-lifecycle.md reconstructs the pinned board's power path with each statement tagged source-established, conditional or unknown. Only the board file has a regulators node; sdhc\_1 has no vmmc-supply or vqmmc-supply; L11/L24 have DT min/max and regulator-allow-set-load but no regulator-boot-on, no regulator-always-on and no consumer, and their vdd\_l9\_l11/vdd\_l23\_l24 parent supply has no matching regulator, so regulator\_resolve\_supply may substitute the dummy regulator under full constraints, but registration does not depend on that substitution. Registration sets apply\_uV and calls set\_voltage, but rpm\_reg\_write\_active includes uv only when the cached is\_enabled is set, so no RPM packet is sent; always\_on/boot\_on are false, so registration does not enable either rail; the 30 s regulator\_late\_cleanup then reads the cached is\_enabled of 0 and skips the disable. mmc\_regulator\_get\_supply keeps -ENODEV error pointers, sdhci\_msm\_set\_regulator\_caps therefore writes no core\_vendor\_spec pad switch, sdhci\_msm\_set\_pincfg calls pinctrl which returns 0 without applying a state, and the power IRQ acknowledges CORE\_PWRCTL\_BUS\_SUCCESS after set\_vmmc/set\_vqmmc return 0. The probe does reset core\_vendor\_spec to 0xa9c and later paths rewrite other bits of it. Linux attempts RPM votes for VDDCX corners and interconnect bandwidth through rpmpd, OPP and icc-rpm, but none for L11/L24; a failed OPP call at probe is only warned about. The AP therefore never learns the rail state.
- Host-only dependency tracing corrects the sdhc\_1 prerequisite record: the probe requests VDDCX SVS\_PLUS and the genpd attach enters the rpmpd send path, but genpd aggregates across attached devices and subdomains and the provider caches that aggregate, which may be higher than SVS\_PLUS, and a pre-sync aggregate may emit max\_state and physical voltage is unmeasured; PIO does not use the SDHC DMA master; SMMU stream 0xc0 state is unknown; the TLMM SDC2 write target is 0x00973000; and the L11/L24 handoff state remains unmeasured. Pinned-revision MMC/SDHCI/genpd/ICC sources establish the power-request chain through sdhci\_set\_power\_noreg, genpd power-on at attach, and that both SDHC interconnect paths attempt RPM master/slave and bus-clock votes \(the cpu-sdhc path is not local-only\). PIO uses CPU MMIO rather than the SDHC DMA master. Physical rail/CX voltage and SMMU state remain unmeasured. The power stage stays blocked.
- Step 4 records the candidate-specific electrical-contract assessment in docs/sdhc-electrical-contract.md. For sdhc-bus-power-activation every safety-critical area is blocking: supply voltage/absmax, IO compatibility, current/loading, transients, sequencing, back-powering, retention, fault handling and recovery. The document also records the evidence-acquisition requirements and proposed measurement requirements without executing them; PMIC readback is explicitly not a substitute for physical voltage or power-good evidence.
- Step 5 verifies only the existing controller-local probe: 33 deterministic scenarios pass, ten negative-control mutations are rejected by the simulator, and the separate-implementation oracle \(same author\) validates all 33 traces, rejects the same ten mutations plus forty-one synthetic trace controls, and accepts the valid initially-zero interrupt baseline. The oracle derives its policy from the header and write contract, not the harness allowlists. The policy still prohibits bus-power enable, card-clock enable, power-status acknowledgement and PMIC/RPM/SPMI activity.
- Step 6 records the dated NO-GO decision in docs/sdhc-decision-memo.md. The gate table fails electrical contract, starting state, access policy, software behavior for the bus-power-only candidate, independent assessment, recovery and authorization. Blockers use canonical E1-E9 \(electrical-contract areas\) and S1-S4 \(software, provenance, independent assessment, authorization\) identifiers. No approval request is made because the technical prerequisites are not met.
- The stock-firmware analysis archive supplied by https://github.com/NoNameBuilder was audited in docs/stock-firmware-analysis-audit.md. All 214 manifest-listed files match their hashes, but the supplied XBL executable bytes and device-tree overlays differ from the captured image and live FDT, so its code-level conclusions do not transfer automatically. Its XBL program-header layout prompted correction of our missing 0x5fc00000 LOAD range; its LCDB voltage, PMIC interrupt-specifier, XBL address and disassembly-coverage claims were corrected. It adds no rail, pad or power measurement and closes no gate.
- A bounded, reproducible host-only scan of the captured rpm.img \(scripts/analyze-gta4l-rpm-ldoa.py; image sha256 272bebd3ddd7ef223d6e95e9b4cd30385a3df0eb4fa7beae6b622f457b4937c6\) finds exactly one stored pointer to the L11 name record \(0x46966a8, the dead selector slot\), none to L24, one to the selector array \(from the unreferenced group table at 0x46966fc\), one to the voltage table \(the descriptor at 0x4696c40\), one to the descriptor \(0x4697f10 inside the 0x4697e20 boundary table\), and none to 0x4697f10 or the group table. The class table at 0x4695774 is zero in the linked image and the setter's class object is built at runtime by 0x46996c4, so the runtime count and id bounds are conditional. This is a stored-word scan, not a control-flow reachability result.

### Completion criteria

- Declared power controls and battery readings match observations; each claimed sleep/resume transition restores its dependent peripherals.

### Current limits

- No power backend \(clocks, sleep, reset\) is implemented. The bridge is runtime-unqualified and the QEMU stall is unresolved. The RAM-root fixture booted through the PMGR-linked kernel without AMFI bypass arguments; PMGR publication and power operations remain unqualified.
- The firmware trace shows the Mu-Silicium PMIC exit path reaches only the SPMI write and the 0x28 entry and writes register bytes 0x14, 0x16 and 0xd1, which cannot directly reach the LDO control registers 0x40/0x41/0x45/0x46/0x48/0x4c/0x61; it does not measure the rails, does not resolve the runtime 0x28 bitmap or the clear-register read-back, and can clear latched PMIC interrupts and mask interrupt delivery on peripherals using the QPNPINT layout. The SPMI map reports commanded state only, supplies no power-good bit, leaves the LDO USID unresolved, and depends on a subtype read for voltage decoding. An SPMI read is a transport bring-up: it needs arbiter version detection, an APID owner-table parse and one observer command write per transaction, and the 1000 us bound covers only the transaction poll. The board-level electrical contract, including absolute maximums, consumer topology and safe sequencing, is not established, so docs/pmic-audit.md blocks live PMIC access. The LDOA reference analysis is a stored-word scan: it does not exclude computed addresses, runtime relocation or aliasing, and the class object is runtime-built.

### Next action

- Capture a separate PMGR publication/power result on the tablet; do not claim power support from the bridge or from the RAM-root fixture. Keep bus power and the SDHCI card clock off until the retained-rail electrical contract and a direct rail measurement are established; a new RPM/SPMI/regulator path is not required merely to match the pinned design. See docs/sdhci-host-init.md. The Mu-Silicium exit trace is recorded in docs/firmware-handoff.md and does not unblock the power stage. Live PMIC/SPMI access is blocked by docs/pmic-audit.md: the L11/L24 slave assignment is unresolved between USID 0 and 1 \(bounded to that pair and not selected by any pinned source in docs/pm6125-usid-research.md\), the runtime 0x28 bitmap, the clear-register read-back value and the indirect callback paths remain unresolved, the voltage getters return software selectors rather than microvolts, and the board-level electrical contract is absent. Do not scan candidate slaves or substitute a USID. The next legitimate step is host-side: try to reconstruct the working RPM-owned Linux path and its assumptions from pinned sources rather than inventing AP-side SPMI access. That reconstruction is recorded in docs/linux-regulator-lifecycle.md and shows the AP never enables, disables or reads L11/L24. Remaining host-side questions are what the RPM firmware does across suspend and shutdown, whether the handoff rail state is guaranteed or incidental, which other consumers share the two supplies, and what the board-level electrical contract requires. docs/power-path-decision.md inventories that contract gap and selects the retained-rail RPM-owned path over AP-side SPMI; it does not authorize a live test. docs/sdhc-dependency-trace.md records the corrected remaining prerequisites and lists the fetched pinned-revision sources with hashes; passing the controller-local gate does not establish power, card-command, DMA or tuning readiness. Step 4 records the candidate-specific contract assessment in docs/sdhc-electrical-contract.md and Step 6 records NO-GO in docs/sdhc-decision-memo.md. The passing host-local scenarios, mutations and oracle are software evidence only; they do not authorize bus-power or card-clock activation. The next legitimate work is host-only evidence acquisition and, separately, an owner-approved measurement-only procedure that does not activate SDHC; approval of that measurement does not approve a controlled activation or the bus-power capability \(docs/sdhc-decision-memo.md §6.2-§6.4\). The current-tree evidence baseline is in docs/evidence-baseline.md. The stock-firmware analysis supplied by https://github.com/NoNameBuilder and its audit are recorded in docs/stock-firmware-analysis-audit.md; they are cross-check material and do not authorize live access.

### Evidence

- `source`: [Records the RPM-owned regulator path, why the AP never enables, disables or reads L11/L24, the bounded captured-image trace of the RPM LDOA resource tables, and the runtime registration of the LDOA parser and aggregator that keep a latched per-id state \(the separately traced 0x46166c8/0x46168dc pair is the smpa class\).](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/docs/rpm-power-interface.md)
- `source`: [Records the transition-by-transition retention gaps and the bounded RPM/XBL static trace: LDOA tables for both rails, no traced L11/L24 voltage/mode/enable write, and no retention result.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/docs/power-retention-evidence.md)
- `source`: [Audits the stock-firmware analysis supplied by https://github.com/NoNameBuilder: 214/214 manifest hashes match, but the supplied XBL executable bytes and DT overlays differ from the captured image and live FDT; records the useful XBL layout lead, the corrected LCDB voltage/IRQ/XBL-address/disassembly-coverage claims, the RPM listing build mismatch and the absence of any rail or power measurement. Section 7 compares an exact-build SM-T505N package with the capture: four BL images and both AP images match in full, six BL images match on their decompressed prefixes with unexplained nonzero trailing bytes, the TWRP recovery differs as expected, and the vbmeta mismatch remains unresolved; the archive and region code stay outside the repository.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/docs/stock-firmware-analysis-audit.md)
- `source`: [Records the PMIC/SPMI audit corrections and the live-access blockers.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/docs/pmic-audit.md)
- `source`: [Inventories the pinned PM6125 identity, rail numbering and vendor consumer assignment; the USID and electrical contract remain unresolved.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/docs/pm6125-identity-evidence.md)
- `source`: [Records the instruction-level SPMIDxe +0x28 trace, the access-type direct-address exclusion, the initialization access-enable clear, the recovery arbiter owner/APID writes, the non-returning exit-callback configuration path, and the bounded descriptor-base scan \(one read, no write intersecting \[0x8878,0x8880\); 64-bit register/effective-address wrapping, paired access/writeback and boundary-crossing handling, pointer-slot invalidation, independent conditional-branch paths and a strict unsupported-instruction stop; internal indirect/computed and runtime/external writers unresolved\).](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/docs/spmi-0x28-analysis.md)
- `source`: [Host-only, hash-pinned static check of the SPMIDxe descriptor-base override: verifies the 0x38b0 read/override words, the 0x38c8 caller and .data layout, follows initial .data pointers, pre/post-index addressing and bounded direct BL recursion, distinguishes XZR from SP, does not seed XZR roots, keeps conditional-branch paths independent, propagates their invalidation at function return, invalidates .data pointer slots overwritten in the path or by modeled calls, stops at instructions outside its register-only whitelist, detects writes intersecting the 8-byte override, resolves the known caller stores at 0x38bc/0x38f4, reports unresolved non-stack loads and stores and every scan truncation, and includes pointer-chain, overlap, partial-store, call-clobber, 64-bit ADD/SUB and effective-address wrapping, paired access/writeback, address-space-boundary, XZR/SP, XZR-root, ADR-XZR, branch-separation, revisit, stale-pointer, cross-call, truncation and decoder controls; all six result sets are unchanged from the audited 4c447b9 baseline; it does not execute firmware.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/scripts/test-gta4l-spmidxe-descriptor-base.py)
- `source`: [Records the L11/L24 SPMI base addresses, common offsets and voltage-decoding caveats.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/docs/pm6125-register-map.md)
- `source`: [Records the Mu-Silicium exit trace and the booted-image provenance for the three drivers.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/docs/firmware-handoff.md)
- `source`: [Records the current-tree revision, dirty/untracked inventory, relevant file hashes, pinned-source cache provenance and the distinction between the current tree, the local firmware volume and the previously booted image.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/docs/evidence-baseline.md)
- `source`: [Records the host-init probe result and the retained-rail contract limits.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/docs/sdhci-host-init.md)
- `source`: [Pins the vendor LineageOS kernel and board overlay and traces the stock BUS\_ON path: controller clock, BUS\_ON, L24, L11, pads, IO high, then a BUS\_SUCCESS or BUS\_FAIL acknowledgement; the core can time out after 5,000 ms and continues, and the card clock is programmed after the 10 ms core power delay and after check\_power\_status returns. RPM votes are aggregated by rpm-smd-regulator.c across consumers and active/sleep sets; the AP sees only cached per-consumer requests. Official Samsung CXG1/CWI2 source \(kernel 4.19.157; relevant files byte-identical\) confirms the power/regulator logic but omits the LineageOS card-detect early-fail/cleanup blocks; the exact CXB1 source is unavailable and the archive contains no vendor DTS. The captured DT declares no regulator enable-time/ramp delay, but framework, RPM acknowledgement and firmware sequencing delays remain unmeasured. Software order only; no electrical order, limit or measurement.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/docs/vendor-sdhc-power-sequence.md)
- `source`: [Host-only extractor and --validate gate used for the booted-image provenance. The gate now rejects a declared kernel overrun, an invalid appended DTB header/size/bounds, a malformed trailing outer FFS entry, and non-erased trailing FV bytes, and it validates the whole outer stream before accepting the inner FV.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/scripts/extract-gta4l-firmware.py)
- `source`: [Self-test for the extractor gate: pins the committed 90-module inventory, checks the three driver hashes, and rejects kernel overruns, invalid DTBs, malformed trailing outer FFS entries, non-erased tails, malformed sections and corrupt gzip end to end.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/scripts/test-extract-gta4l-firmware.py)
- `source`: [Inventories the missing board-level electrical contract and recommends the retained-rail RPM-owned path over AP-side SPMI, without authorizing a live test.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/docs/power-path-decision.md)
- `source`: [Bounds the L11/L24 SPMI USID to &\#123;0,1&\#125; from pinned DT evidence and records that no pinned source selects one, so the RPM path is not exercised by the USID question.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/docs/pm6125-usid-research.md)
- `source`: [Records transition-by-transition RPM retention evidence: no AP vote for L11/L24, VDDCX/interconnect votes differ, the UEFI exit path is not passive, and retention across handoff, suspend, shutdown and reboot remains unestablished.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/docs/power-retention-evidence.md)
- `source`: [Records the sdhc\_1 dependencies beyond L11/L24 \(VDDCX corner, interconnect, GCC branches/reset, TLMM pads, SMMU stream 0xc0, IRQs\) and which are present at handoff versus absent in XNU.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/docs/sdhc-dependency-trace.md)
- `source`: [Records the Step 4 board-level electrical-contract assessment for the bus-power-only candidate: nine blocking safety-critical areas \(E1–E9\) and the evidence-acquisition requirements.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/docs/sdhc-electrical-contract.md)
- `source`: [Separate-implementation host oracle \(same author\) for the controller-local access policy; derives read/write rules from the header and write contract, validates 33 traces, checks prerequisite values, interrupt-suppression confirmation on both initial-value paths, universal stage-local poll bounds, reset-clear ordering, the reset-to-clock observation window, the stable clock poll completion and immediate final confirmation before downstream accesses, the eleven required final stage-4 observations, and post-reset state, rejects ten source mutations plus forty-one synthetic trace controls, and accepts the valid initially-zero interrupt baseline.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/scripts/oracle-gta4l-sdhci-host-init.py)
- `source`: [Records the dated Step 6 NO-GO decision, the E1-E9/S1-S4 blocker dispositions and the separated baseline-measurement, controlled-activation and capability-approval gates for sdhc-bus-power-activation.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/docs/sdhc-decision-memo.md)
- `source`: [Host-only, hash-pinned analysis of the captured RPM LDOA tables: ELF/LOAD/PT\_NULL layout checks, full selector/group/voltage/descriptor/boundary validation, Thumb-aware stored-pointer counts for L11/L24, PT\_LOAD-only scanning, the linked-zero class table, and optional --code checks for the documented Thumb callback literals, class registration and direct call sites.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/scripts/analyze-gta4l-rpm-ldoa.py)
- `source`: [Synthetic-image self-test for the RPM LDOA analyzer: anchors, Thumb reference counts, PT\_NULL exclusion, code attribution, wrong hash/mapping, changed selector/voltage/boundary, altered callback/class/call-edge controls and deterministic output without private firmware.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/scripts/test-gta4l-rpm-ldoa-analysis.py)
- `source`: [Links every canonical E1-E9/S1-S4 gate to established evidence, missing input, acquisition route, proposed role, closure criterion, informational cross-dependencies and unresolved contradictions; revision 2 adds staged-approval separation, claim-level references and the Phase 2 acquisition register; revision 3 adds shared-consumer and parent-supply tracking plus separate USID, runtime-APID and descriptor-base items with gate mappings; revision 4 aligns the descriptor-base item with the 0x8878 override path and extends measurement tracking to E5-E7; revision 5 records the pinned-image descriptor-base scan; revision 6 corrects its scope after an audit, adds pointer-chain, overlap and pre/post-index controls, and leaves internal indirect/computed and runtime/external writers open; revision 7 strengthens the scan with XZR/SP separation, pointer-slot invalidation, a strict unsupported-instruction stop, and unresolved load/store, revisited-state and truncation reporting; revision 8 keeps conditional-branch paths independent, propagates their invalidation at function return, and stops seeding XZR roots; revision 9 records the exact-build package comparison and the vendor BUS\_ON trace; revision 10 narrows those claims after the broad host-only audit \(four full and six prefix BL matches, the rpm-smd-regulator backend and path caveats, and 64-bit scanner wrapping with unchanged result sets\); revision 11 records the official Samsung CXG1/CWI2 source comparison and the card-detect difference, the non-applicability of the inspected SM-T505 family pages, and the KMDX60018M-B425 candidate with its unresolved datasheet; no gate is closed and NO-GO remains.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/docs/sdhc-evidence-gap-checklist.md)

## Image assembly {#packaging}

`planned`

### Hardware and dependencies

- Format 2 kernel step, archive builders, prelink, payload and boot image; 192 MiB payload size; iPad7,1 17.7.11 21H461 kernelcache.

### Configuration

- board.toml payload size\_mib=192, loader=firmware, panic\_screen=true, dram\_size=0xC0000000; CONFIG\_XNU\_BUILD\_ARCHIVES=y; output out/gta4l/ipados-17.7.11-21H461/gta4l.

### Procedure

- ./unixnu build kernel -D ../UniXNU-gta4l; ./unixnu build package; ./unixnu build firmware; ./unixnu build payload; ./unixnu bootimg.
- For a raw RAM-root diagnostic payload, use scripts/build-gta4l-diagnostic-payload.py --diagnostic host-init with the data ramdisk, owner trust cache and unique chip ID. It copies the device tree, sets payload size and packed\_data\_ramdisk=false, runs the payload step, and checks the ADT contract without modifying the tracked board.toml.
- For a diagnostic image, use scripts/package-gta4l-diagnostic.py with the pinned v5 baseline and the payload; it preserves the header, firmware, boot DTB and boot kernel section, recomputes the boot-image ID, requires the payload/ADT contract, and runs scripts/check-gta4l-boot-image.py. Run scripts/test-gta4l-boot-image.py, scripts/test-gta4l-diagnostic-package.py and scripts/test-gta4l-sdhci-host-init-sim.py before flashing.
- To replay the historical payload, run scripts/build-gta4l-diagnostic-payload.py with the audit board snapshot and --kernel; set SOURCE\_DATE\_EPOCH=1793180892 for the historical FAT timestamp, and use scripts/normalize-gta4l-adt-seed.py for the fail-closed seed comparison into a new output path; it refuses an existing output and candidate/reference aliases. docs/payload-build-recipe.md records the inputs, the clean hash, the seed-normalized comparison and the preserved out/gta4l/payload-testbuild-evidence directory.

### Development findings

- The PMGR-linked kernel/prelink pass: kernel.macho is a 49 MiB Mach-O arm64 image with SHA-256 dc8184da757b5323d2f4fb6c7ac1d588790b3d44d583c6d6fd24897cdbbcfe60; link.filelist has 1006 entries and none are missing. The earlier no-bridge hash was ef85af5417ace24e7b96f6c5a3224d2e7c40a163c1532bf2586f23fb5dd5f8bd.
- The full ordered archive plan is required: replacing it with only build-platform-power.py dropped the NativeAES bindings and failed the final link. board.toml now keeps the architecture list and appends the PMGR builder.
- The fresh tree first stopped in prepare-xnu-source.py while fetching omitted DriverKit headers; the retry-safe fetch restored 26 headers. The earlier Format 1 corecrypto failure was stale state, not a missing bootstrap object set.
- The corrected v2 audit image preserved the v5 boot header, firmware, boot DTB and boot kernel section exactly but was produced by temporary board.toml substitution. scripts/build-gta4l-diagnostic-payload.py now replaces that path for raw payloads by copying the device tree and forcing the explicit size and packed-data flags; scripts/package-gta4l-diagnostic.py takes the pinned baseline and a named payload as explicit inputs.
- scripts/package-gta4l-diagnostic.py now packages from the pinned v5 baseline and a named payload without modifying board.toml. It preserves the header page, firmware, boot kernel section and boot DTB, replaces only the ramdisk, recomputes the Android boot-image SHA-1 ID, and runs the component gate. Reproducing v2 from the v5 baseline and audit payload is byte-identical: a34519c66820eb5f1f4c4790be5e10233ffd4c8a4ece2df4768e7dca151c8546.
- scripts/check-gta4l-boot-image.py now checks the header page excluding the deterministic ID, the recomputed ID, zero kernel padding, absence of trailing data, the appended FDT total size, the Qualcomm ID properties and an optional expected payload hash. scripts/test-gta4l-boot-image.py covers exact pass, payload-only replacement, minimal-DTB substitution, a different valid DTB, a changed header field, a wrong ID, nonzero padding, trailing data, a short ramdisk, a wrong expected payload and a malformed image.
- An independent ABL/LinuxLoader-oriented check with bootimg\_tool.py, provided by https://github.com/NoNameBuilder, confirmed the v2 header, appended FDT and Qualcomm ID properties and rejected the v1 DTB. The tool is recorded as external evidence, not vendored; its outer FV/LZMA checks also fail on the known-good v5 image and are not used as a gate.
- scripts/check-gta4l-payload.py now checks the ADT memory-map placeholder against the actual scratch-data.img layout and checks unixnu.toml diagnostic arguments. Its self-test rejects the failed packed/raw mismatch and passes corrected v2. The failed host-init payload was packaged as PackedRAMDisk while the raw N4KROOT fixture reports RamdiskPacked=FALSE; DarwinBoot returned EFI\_COMPROMISED\_DATA at the UniXNU picker. Corrected v2 reserves RAMDisk and passes both the payload checker and the 18-check boot-image gate.
- scripts/build-gta4l-diagnostic-payload.py makes the former temporary diagnostic board explicit and reproducible: it copies the device tree, forces payload.size\_mib=80 and packed\_data\_ramdisk=false, runs the normal payload step, copies the result, and requires the payload contract before writing a manifest. The tracked board.toml remains at 192 MiB packed.
- scripts/package-gta4l-diagnostic.py now runs scripts/check-gta4l-payload.py before publishing and records the contract result in the manifest. scripts/test-gta4l-diagnostic-package.py rejects a wrong expected diagnostic and the retained packed/raw failed payload; the valid audit payload still reproduces the v2 image byte-for-byte.
- scripts/test-gta4l-sdhci-host-init-sim.py compiles the production host-init source against a fake MMIO window and minimal kernel-header stubs, replaces only the six MMIO helpers with logging hooks, and records every read and write. It exercises conflicting arguments, an absent boot argument, a failed mapping, bus power already on, reset timeout, unstable clock, a pending vendor power request and a device-side vendor change; it asserts the exact write sequence, rejects any access outside the allowlist, and rejects an injected same-value POWER\_CONTROL write that leaves final memory unchanged.
- The historical-host payload replay reproduces every payload byte except the 64-byte ADT random-seed: the clean payload 1d15ea68cd570382ed4ba7b426aa4fb29cf5c303124a289af16451248a8975ff differs from the historical 31b78bec7529706407f682e64dbc9c4c990e86009025174fd3f791606b29ea31 only at 0x30e3b78, and the fail-closed seed-normalized payload is byte-identical. Packaging the normalized payload against the v5 baseline reproduces the historical audit v2 image a34519c66820eb5f1f4c4790be5e10233ffd4c8a4ece2df4768e7dca151c8546 byte-for-byte; the clean payload packages to 037ba650847caa0cb32ac14a99c13736ae2ae6196700344531a224590c6694eb, differing in the derived image ID and the seed. docs/payload-build-recipe.md records the pinned inputs. A second controlled clean build \(payload c697903b74279b6cadf364b94871a6125b42229cbdedf250bfcb62331b8d3d4c, boot 60ad9d056b439a2c53f82dddcefc6ac9ec0df0a5b323ff9cdcebc3d76e15e8f8\) passed both gates and normalization again reproduced 31b78bec... and a34519c6... byte-for-byte. A clean bit-exact build needs a supported ADT seed pin, which the pinned UniXNU does not provide. The controlled build is preserved at out/gta4l/payload-testbuild-evidence with provenance.json and a verified SHA256SUMS.
- The linked kernel 3103e067575d94d878485de464ee0173b07ab2f02215d3abae6fb962c1c59064 is reproduced byte-for-byte from the pinned source and patches with the historical build date, personality, object and archive-member mtimes and RC\_ProjectSourceVersion=10063.141.1; the prelink outputs 452026b2d8bbfaaa5b6ebc97ce235f396a8929b50d3957eff4c655eddd30ca86 and 9f70ad6594f539f447029d5714c0cd065b14b3c5e84b54dfd7c8d5b5c22572e8 are regenerated from it \(docs/kernel-build-recipe.md sections 6-7\).

### Completion criteria

- Kernel and prelink succeed, payload contains all declared inputs, and the boot image matches the bootloader format and size limit.

### Current limits

- The PMGR kernel host build/prelink and one QEMU checkpoint run pass. Payload and boot images have been built from this kernel, and the RAM-root report fixture booted on the tablet; it is not an authenticated-root result.
- The payload replay starts from the historical prelinked kernel; the kernel compile/link is replayed separately in docs/kernel-build-recipe.md, and a clean bit-exact payload build remains not established.

### Next action

- Use the explicit diagnostic payload builder and the mandatory payload/ADT contract for raw RAM-root images; keep the pinned v5 baseline and the byte-identical v2 reproduction. The clean payload build is not bit-exact because the ADT random-seed is fresh; use the documented seed-normalized comparison for provenance and do not present it as a clean build. A supported seed pin remains host-only work.

### Evidence

- `source`: [Records the RAM-root report image sha256 45ecc93049757e97a8d71edb776f67e69df5c9c58be13543295c154637273e24 and the fs/timer image sha256 c12e601eceb8e5b5b9cf7a028c0f404653b67dc5ff5577813293673d2dea2b3a \(flashed; the fs/timer fixture then passed on the tablet with RAMROOT-FST PASS: pid=1 page=4096 fs=read+seek+eof timer=poll\), with their gitignored artifact directories.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/docs/build-revisions.md)
- `source`: [Records the historical-host payload replay: the clean payload 1d15ea68... differs from 31b78bec... only in the 64-byte ADT random-seed; the fail-closed seed-normalized payload is byte-identical, and packaging it reproduces the audit v2 image a34519c6... byte-for-byte. A second controlled clean build \(c697903b..., boot 60ad9d05...\) repeated the result. The build is preserved at out/gta4l/payload-testbuild-evidence with provenance.json and SHA256SUMS.](https://github.com/gta4lunix/UniXNU-gta4l/blob/53d3a82d1f81f0f3a28212b0981d5e82dc2577b9/docs/payload-build-recipe.md)

## Diagnostics {#diagnostics}

`planned`

### Hardware and dependencies

- Build logs for the fresh Format 2 tree; the shared prepare-xnu-source.py fetch path; the TB128FU reference revisions.

### Configuration

- UNIXNU\_XNU\_TAG=xnu-10063.141.1 and the pinned source revision; GITHUB\_TOKEN can be supplied to prepare-xnu-source.py but is not required.

### Procedure

- Run the kernel build with a log; on a fetch failure, preserve the log and retry with the retry-safe prepare-xnu-source.py; compare failures across clean output trees.

### Development findings

- prepare-xnu-source.py used four threads with a 30 s TLS timeout and no retry. A GitHub raw fetch timed out during the first Format 2 kernel build, before any XNU compilation. The shared script now retries transient failures with a 60 s timeout and exponential backoff; scripts/test\_prepare\_xnu\_source.py covers the retry and non-retry paths.
- The clean build completed with exit 0. The PMGR kernel.macho hash dc8184da757b5323d2f4fb6c7ac1d588790b3d44d583c6d6fd24897cdbbcfe60, 1006/1006 link objects and XNU\_NATIVE\_PAN=0 records are in docs/build-revisions.md.
- QEMU TCG reached \_bsd\_init, \_sheng\_pmgr\_run and \_IOKitBSDInit with sheng-pmgr=2 and no AMFI bypass, then timed out at \_ml\_get\_timebase before \_vfs\_mountroot; the PMGR archive audit and build report are retained.
- scripts/test-gta4l-diagnostic-payload.py checks the diagnostic payload builder with temporary stand-ins \(forced size, packed\_data\_ramdisk=false, the contract failure path and the command line\) without building a payload or touching board.toml; scripts/test-gta4l-sdccdxe-decode.py and scripts/test-gta4l-spmidxe-descriptor-base.py pin the firmware handoff and descriptor-base scan results. All are host-only and execute no firmware.

### Completion criteria

- Each claimed milestone has a reproducible command, a matching source/image revision and an accessible result.

### Current limits

- The retry test is a host unit test; the kernel/QEMU result is host-only. The QEMU serial layer has no Apple-compatible UART. The tablet result is a panic-screen report, not a serial log.

### Next action

- Preserve the QEMU evidence and the tablet panic-screen result; qualify the fs/timer diagnostic separately.

### Evidence

Collect evidence using the next action.

</div>
