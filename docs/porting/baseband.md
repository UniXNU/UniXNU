# Baseband and cellular adaptation

Wi-Fi-only tablets without a cellular modem can skip this page. Set the cellular area of `porting.toml` to `not-applicable` and give the hardware reason in `limits`.

The example is [QcomBaseband](/drivers/qcom-baseband), written by **HoshinoYumeka ([@chiba233](https://github.com/chiba233))**. It connects iOS's ABM, BBUpdater and CommCenter to a Qualcomm modem. Its Coachz example targets SC7180, IPA v4.2 and iOS 17 (21H461).

Start after [platform memory and DMA](/porting/platform). Identify the modem, its control transport, data engine, firmware, SIM connection and EFS/NV storage.

## 1. Separate the layers {#layers}

| Layer | Responsibility | Example |
| --- | --- | --- |
| SoC and board | Power, clocks, reserved memory, modem firmware boot, interrupts, DMA and EFS/NV access | MBA/MPSS, SMEM/SMP2P, GLINK/QRTR and rmtfs |
| Control bridge | QMUX framing, QMI client allocation, service discovery and reply routing | `baseband/coachz_bb_qmux.h` |
| iOS interface | Baseband services, channels, asynchronous reads/writes and boot exchange | `baseband/coachz_baseband.cpp`, `coachz_bb_channels.h`, `coachz_bb_sahara.h` |
| Data path | IPA/GSI, QMAP muxes and OS network-interface delivery | `ipa/` and `platform/coachz/coachz_modem.c` |

Source is in [UniXNU/QcomBaseband](https://github.com/UniXNU/QcomBaseband). Keep the board's register addresses, DMA layout and firmware policy in its device or SoC repository.

SC7180 carries QMI over GLINK/QRTR. The bridge presents the Apple PCIe baseband class names to iOS over that transport. A modem reached through PCIe/MHI needs its corresponding board transport.

## 2. Boot the modem and establish QMI {#modem-startup}

1. Record modem rails, resets, clocks, interconnect requests, interrupts, firmware memory and SMMU streams. Supply DMA addresses and cache maintenance for the selected translation mode.
2. Load the board's MBA/MPSS firmware and provide its factory FSG/EFS/NV data. The Coachz reference reads FSG from the eMMC hardware boot partition and checks the device's stored digest. Confirm modem startup, identity and SMP2P ready indications.
3. Start GLINK/QRTR, follow service announcements and removals, and verify QMI requests and replies. The board owns QRTR ports, polling and reset recovery.
4. For the IPA v4.2 example, configure IPA before modem startup, run GSI/endpoint setup on `ipa-setup-ready`, then complete INIT_DRIVER and INIT_COMPLETE over QMI. The Coachz adapter starts its modem TX/RX channels at this boundary.

Record firmware sources, hashes and packaging paths in `proprietary-files.txt`. Qualcomm modem images, EFS/NV contents and the Apple `.bbfw` used by ABM are separate inputs.

**Result:** the modem runs, its QMI services respond, and IPA initialization completes.

## 3. Connect the iOS bridge {#ios-bridge}

Read `baseband/QcomBaseband.h` and the [Coachz integration](https://github.com/UniXNU/QcomBaseband/blob/main/platform/coachz/README.md).

1. Publish `AppleBaseband`, `AppleBasebandPCIControl`, and one `AppleBasebandPCIInterface` per channel. Set and match `ABPInterfaceProtocol` for names such as `pbl`, `sahara`, `qmux1` and `qmux2`. Keep UserClient names, selectors, argument sizes and asynchronous completion shapes aligned with the selected OS.
2. Supply `coachz_baseband_configure(send, del_client)`. Forward QRTR service changes and messages through `coachz_baseband_new_server`, `coachz_baseband_del_server` and `coachz_baseband_qrtr`. Call `coachz_baseband_poll` on the transport worker.
3. CTL allocates QMI clients and local QRTR ports. Ordinary service messages cross the QMUX/QRTR bridge. The bridge handles BSP activation and VINYL Tape requests; other Apple-private requests receive `QMI_ERR_NOT_SUPPORTED`. Activation indications include service-provisioned and accepted-slot states. BSP 0xb001 returns the chip ID and serial already reported over BHI. Carrier-bundle PRI/GRI segments (BSP 0xa000, SetConfig 0xe00d) are acknowledged with the next expected segment number, discarded, and followed by FileTransferStatus 0xa001; CommCenter then caches the configuration and stops resetting the baseband.
4. Add the selected cellular ADT nodes and product properties so launchd selects the cellular CommCenter job. The reference uses `/chosen/coachz-baseband`, `/baseband`, `baseband-chipset = mav16` and root `compatible = J121AP`; its display identity properties stay unchanged. Adapt these identities to the chosen IPSW and baseband ABI.
5. Package and mount the Apple firmware where ABM and BBUpdater look for it. The reference's SAHARA endpoint consumes that boot exchange while the Qualcomm modem continues running its own firmware.
6. Publish the PDP manager services required by CommCenter. Check ABM boot completion, QMUX clients, SIM status, modem identity and Settings > Cellular separately.

The bridge queues up to 1,024 frames per channel for ABM. Each channel logs queue depth and message headers for its first 32 dropped frames. Check queue drops during cold boot and registration.

Observe CommCenter's EF_ICCID and EF_IMSI reads. Convert their values to reading-order BCD and publish activation TLVs `0x42` and `0x43` so carrier matching receives both identifiers.

**Result:** CommCenter communicates with the actual modem and reads its SIM and identity.

## 4. Connect cellular data {#data-path}

A modem's `kOnline` state means its radio is online. Check NAS registration, the serving network and packet-service attachment for network registration.

`coachz_bb_data.h` opens the IPA hardware port with DPM and configures WDA raw IP/QMAPv4 before the first WDS client binds. It translates WDS/QOS endpoint fields from Apple PCIe `{3, 4}` to embedded `{4, 1}` and supplies the endpoint for mux-only requests. Bind the WDS session to a QMAP mux, then start a data call. Connect the returned address, routes, DNS and MTU to `pdp_ip`. Route each QMAP mux to the corresponding interface, and pair DMA completion with buffer ownership. Exercise transmit, receive, disconnect, flight mode and modem reset. eSIM needs its UIM/APDU and VINYL flow in addition to the physical-SIM path.

The Coachz example displays IMEI, ICCID and modem firmware with its factory FSG. A valid SIM registers on LTE roaming with CS/PS attached; the operator and signal bars appear directly after a cold boot. DPM/WDA setup and WDS/QOS bindings succeed. The SIM matches its carrier bundle, LTE is shown and cellular IPv4 web loading works, including after PDP reconnects. The pinned CommCenter blocks the Internet context without an Apple postponement ticket; [`coachz_cellular_compat.py`](https://github.com/UniXNU/QcomBaseband/blob/main/platform/coachz/README.md#commcenter-compatibility-copy) builds a hash-checked patched copy, its signature and trust cache for that condition. The firmware archive, ADT digest and trust cache set carry them. IPv6 data, APN editing and long sessions are pending. EFS writes remain in memory until reboot.

`coachz_bb_pdp.cpp`, included by `coachz_baseband.cpp`, registers `pdp_ip0` through `pdp_ip3` for QMAP muxes 1 through 4 with MTU 1492. WDS bind, IP-family, start, stop and status replies control each family independently. Supply `coachz_modem_data_send` and `coachz_modem_data_receiver` from `QcomBaseband.h` on the QRTR/IPA owner thread; the Coachz adapter implements both. Register `PF_INET` and `PF_INET6` protocol plumbers on the interface so CommCenter can reattach a family after it unloads the old context; the initial attach uses the same callback. Verify IPv4 and IPv6 separately, including disconnect of one family while the other remains active.

`coachz_bb_esim.h` discovers real eUICC slots and carries VINYL Tape through ISD-R logical-channel APDUs. Preserve capability TLV `0x21` in card-status replies and indications. Legacy GetCsn returns `0x204` to complete native driver initialization; EID/capability requests read TLV `0x01`, and Tape results use an 11-byte header.

Challenge, authentication and download preparation retain the owning client's channel. Terminal operations, errors, disconnect and 180 seconds of inactivity close it and restore the original slot mapping. Recovery queries return an empty record set. A four-entry read-only ES10 cache answers repeated queries without a physical-slot switch; state-changing card commands clear it. The host models pass. Coachz shows eSIM in Settings with an incomplete page; profile provisioning remains unverified. Test cellular traffic with a SIM that has an active data plan.

## 5. Build and record {#build}

Add `QcomBaseband` to the device's existing component selection. Its normal archive command is `component:QcomBaseband`. For the Coachz IPA adapter, use `build-qcom-baseband.py --coachz` in the kernel archive recipe.

When updating QcomBaseband, pin the same commit in `components.toml` and the main repository's `drivers/QcomBaseband` submodule.

From the resolved target tree after building XNU:

```sh
python3 scripts/build-qcom-baseband.py --coachz
```

The output is `build/qcom-baseband/libQcomBaseband.a`. The recipe compiles `coachz_ipa_config.c`, `coachz_gsi.c` and `coachz_modem.c` with the C compile record, and `coachz_baseband.cpp` with the C++ record. `coachz_modem.c` includes the command, RX and modem implementations as one translation unit. The PDP source is included by the baseband C++ unit.

Link the archive and connect its IOKit class initialization and startup calls using [driver build integration](/porting/drivers#build-integration). Record modem boot, QMI, SIM identity, registration, data, reset and eSIM as separate checkpoints in `porting.toml`.

Continue with [DSP, audio and power](/porting/power), or return to the [driver checklist](/porting/drivers).
