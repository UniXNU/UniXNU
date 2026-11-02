# Baseband and cellular adaptation

Wi-Fi-only tablets without a cellular modem can skip this page. Set the cellular area of `porting.toml` to `not-applicable` and give the hardware reason in `limits`.

The example is [QcomBaseband](/drivers/qcom-baseband), written by **HoshinoYumeka ([@chiba233](https://github.com/chiba233))**. It connects iPadOS's ABM, BBUpdater and CommCenter to a Qualcomm modem. Its Coachz example targets SC7180, IPA v4.2 and iPadOS 17 (21H461).

Start after [platform memory and DMA](/porting/platform). Identify the modem, its control transport, data engine, firmware, SIM connection and EFS/NV storage.

## 1. Separate the layers {#layers}

| Layer | Responsibility | Example |
| --- | --- | --- |
| SoC and board | Power, clocks, reserved memory, modem firmware boot, interrupts, DMA and EFS/NV access | MBA/MPSS, SMEM/SMP2P, GLINK/QRTR and rmtfs |
| Control bridge | QMUX framing, QMI client allocation, service discovery and reply routing | `baseband/coachz_bb_qmux.h` |
| iPadOS interface | Baseband services, channels, asynchronous reads/writes and boot exchange | `baseband/coachz_baseband.cpp`, `coachz_bb_channels.h`, `coachz_bb_sahara.h` |
| Data path | IPA/GSI, QMAP muxes and OS network-interface delivery | `ipa/` and `platform/coachz/coachz_modem.c` |

Source is in [UniXNU/QcomBaseband](https://github.com/UniXNU/QcomBaseband). Keep the board's register addresses, DMA layout and firmware policy in its device or SoC repository.

SC7180 carries QMI over GLINK/QRTR. The bridge presents the Apple PCIe baseband class names to iPadOS over that transport. A modem reached through PCIe/MHI needs its corresponding board transport.

## 2. Boot the modem and establish QMI {#modem-startup}

1. Record modem rails, resets, clocks, interconnect requests, interrupts, firmware memory and SMMU streams. Supply DMA addresses and cache maintenance for the selected translation mode.
2. Load the board's MBA/MPSS firmware and provide EFS/NV storage. Confirm modem startup and the SMP2P ready indications.
3. Start GLINK/QRTR, follow service announcements and removals, and verify QMI requests and replies. The board owns QRTR ports, polling and reset recovery.
4. For the IPA v4.2 example, configure IPA before modem startup, run GSI/endpoint setup on `ipa-setup-ready`, then complete INIT_DRIVER and INIT_COMPLETE over QMI. The Coachz adapter starts its modem TX/RX channels at this boundary.

Record firmware sources, hashes and packaging paths in `proprietary-files.txt`. Qualcomm modem images, EFS/NV contents and the Apple `.bbfw` used by ABM are separate inputs.

**Result:** the modem runs, its QMI services respond, and IPA initialization completes.

## 3. Connect the iPadOS bridge {#ios-bridge}

Read `baseband/QcomBaseband.h` and the [Coachz integration](https://github.com/UniXNU/QcomBaseband/blob/main/platform/coachz/README.md).

1. Publish `AppleBaseband`, `AppleBasebandPCIControl`, and one `AppleBasebandPCIInterface` per channel. Set and match `ABPInterfaceProtocol` for names such as `pbl`, `sahara`, `qmux1` and `qmux2`. Keep UserClient names, selectors, argument sizes and asynchronous completion shapes aligned with the selected OS.
2. Supply `coachz_baseband_configure(send, del_client)`. Forward QRTR service changes and messages through `coachz_baseband_new_server`, `coachz_baseband_del_server` and `coachz_baseband_qrtr`. Call `coachz_baseband_poll` on the transport worker.
3. CTL allocates QMI clients and local QRTR ports. Ordinary service messages cross the QMUX/QRTR bridge; Apple-private service requests currently receive `QMI_ERR_NOT_SUPPORTED`.
4. Add the selected cellular ADT nodes and product properties so launchd selects the cellular CommCenter job. The reference uses `/chosen/coachz-baseband`, `/baseband`, `baseband-chipset = mav16` and root `compatible = J121AP`; its display identity properties stay unchanged. Adapt these identities to the chosen IPSW and baseband ABI.
5. Package and mount the Apple firmware where ABM and BBUpdater look for it. The reference's SAHARA endpoint consumes that boot exchange while the Qualcomm modem continues running its own firmware.
6. Publish the PDP manager services required by CommCenter. Check ABM boot completion, QMUX clients, SIM status, modem identity and Settings > Cellular separately.

**Result:** CommCenter communicates with the actual modem and reads its SIM and identity.

## 4. Connect cellular data {#data-path}

A modem's `kOnline` state means its radio is online. Check NAS registration, the serving network and packet-service attachment for network registration.

Configure WDA data format, bind the WDS session to a QMAP mux, and start a data call. Connect the returned address, routes, DNS and MTU to `pdp_ip`. Route each QMAP mux to the corresponding interface, and pair DMA completion with buffer ownership. Exercise transmit, receive, disconnect, flight mode and modem reset. eSIM needs its UIM/APDU and VINYL flow in addition to the physical-SIM path.

The current Coachz example reaches SIM recognition and displays modem firmware. Its modem reports no IMEI with the current empty EFS image, so CommCenter leaves the SIM disabled. ICCID, network registration, `pdp_ip` data delivery and eSIM remain unfinished.

## 5. Build and record {#build}

Add `QcomBaseband` to the device's existing component selection. Its normal archive command is `component:QcomBaseband`. For the Coachz IPA adapter, use `build-qcom-baseband.py --coachz` in the kernel archive recipe.

From the resolved target tree after building XNU:

```sh
python3 scripts/build-qcom-baseband.py --coachz
```

The output is `build/qcom-baseband/libQcomBaseband.a`. The recipe compiles `coachz_ipa_config.c`, `coachz_gsi.c` and `coachz_modem.c` with the C compile record, and `coachz_baseband.cpp` with the C++ record. `coachz_modem.c` includes the command, RX and modem implementations as one translation unit.

Link the archive and connect its IOKit class initialization and startup calls using [driver build integration](/porting/drivers#build-integration). Record modem boot, QMI, SIM identity, registration, data, reset and eSIM as separate checkpoints in `porting.toml`.

Continue with [DSP, audio and power](/porting/power), or return to the [driver checklist](/porting/drivers).
