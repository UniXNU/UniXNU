# Wi-Fi adaptation

Start with [platform interrupts and DMA](/porting/platform). Identify the actual
radio, PCI ID, firmware and board-data variant. Read [Ath12kWifi](/drivers/ath12k-wifi)
and its `include/nw_abi.h` before implementing callbacks.

Use [driver build integration](/porting/drivers#build-integration) to connect
initialization, archive recipes and the OS ABI, then run this page's hardware checks.

## Sources and interfaces {#source-map}

These links identify reviewed source revisions. Match interfaces to the selected
SoC, component and OS versions. The linked device sources provide board integration
examples.

| Implementation | Source | What to read and implement |
| --- | --- | --- |
| Reusable interface | [nw_abi.h](https://github.com/UniXNU/Ath12kWifi/blob/f6bf561f92cc42761bdd417fce1d53fe1db9477c/include/nw_abi.h#L9) | `lx_platform`, `nw_board`, `nw_wifi_events` and station calls |
| Worker implementation | [nw_wifi.c](https://github.com/UniXNU/Ath12kWifi/blob/f6bf561f92cc42761bdd417fce1d53fe1db9477c/src/nw_wifi.c) | `nw_wifi_start/step/stop` and event dispatch |
| Hardware integration | [WifiProbe.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/WifiProbe.cpp) | PCIe, MSI, DMA allocation and firmware access callbacks |
| OS integration | [WifiNet.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/WifiNet.cpp) | Network service, Apple80211 requests and receive/transmit ownership |

## 1. Separate the integration layers


Read the [board sources](https://github.com/UniXNU/UniXNU-sheng/tree/main/package).
The reference connects WCN7850 to SM8550 PCIe0. The component also contains QCC2072 and
QCN9274 definitions. Match the endpoint's hardware revision and firmware support
in the driver before selecting a device definition.

## 2. Bring up the PCIe endpoint

Record controller/PHY windows, lane count, reset sequence, WLAN enable, PERST,
reference clock, regulators, interconnect votes, SMMU streams and MSI routing.
The reference stores these as C++ constants and tables in the board package.

1. Inspect powered and clocked register state.
2. Apply the board's rails, clocks, PHY configuration and reset sequence.
3. Train the link and read the endpoint vendor/device ID.
4. Assign and map the BAR; inspect PCI capabilities and enable the required
   memory and bus-master operations.
5. Establish the endpoint DMA range and prove that allocated buffers are
   reachable with the selected cache policy.
6. Attach MSI and confirm delivery before relying on interrupt-driven progress.

**Expected result:** the correct endpoint, readable BAR, usable DMA and delivered
interrupts. The reference probe uses `sheng-wifi` to select stages; stage 1 inspects
handoff state, stage 2 starts the link and stage 4 inspects the endpoint.
The current endpoint path enters the reusable stack at stage 5 or higher; that
stack performs its MHI and firmware startup. Read the stage's
source before enabling it on a new board.

## 3. Supply the component callbacks

Implement `lx_platform` from `nw_abi.h`: time, sleep, polling, logging, allocation,
DMA allocation/mapping/synchronization and `fw_get`. Implement `nw_board`: mapped
BAR, PCI identity, config-space access and MSI target.

The reference implementation uses `native_ufs_extra_*` for its DMA arena and
`native_ufs_part_*` for firmware access. A port with another storage or DMA
implementation must supply equivalent board services. Record firmware filenames,
board data and calibration provenance in `proprietary-files.txt`.

Call `nw_wifi_start`, then service `nw_wifi_step` from the board worker. Event
callbacks run from that worker and must return promptly. Inspect `nw_wifi_stats`,
`nw_wifi_where`, board MSI counts and the firmware log when progress stops.

Preserve callback ownership from `nw_abi.h`: `dma_alloc` returns zeroed CPU
memory and an endpoint-reachable bus address; `dma_map` returns 0 for buffers
outside the DMA window; `dma_sync` handles the transfer direction. `fw_get`
returns data and length by filename and keeps the data valid while consumed.
Install `nw_wifi_events` before starting the worker; continue stepping while
`nw_wifi_step` returns nonzero. Copy receive data into OS-owned storage before
returning when delivery continues asynchronously. On shutdown, stop new submissions,
stop the worker and component, then release BAR, MSI and DMA resources.

**Expected result:** firmware and QRTR services start, then scanning reports BSS
entries. Firmware startup and successful scanning are separate checkpoints.

## 4. Connect the OS network interface

Adapt `WifiNet.cpp` to the selected XNU and wireless-framework ABI. Connect
`nw_wifi_scan`, `nw_wifi_connect`, `nw_wifi_tx` and receive/link events to the OS.
Provide the device MAC identity, channel/regulatory data and request layouts
required by the selected userland.

Select Ath12kWifi in the complete component list. The reference builds its objects through
`build-ath12k-wifi.py`, called by `build-gop-legacy-display.py`, which also links
`WifiProbe.cpp` and `WifiNet.cpp`. Inspect the assembled target tree:

```sh
rg -n 'struct lx_platform|struct nw_board|nw_wifi_' drivers/Ath12kWifi/include/nw_abi.h
rg -n 'nativewifi|wifi_module_objs|WifiNet|WifiProbe' scripts/build-gop-legacy-display.py
```

Rebuild the kernel, payload and boot image using [Building](/building).

**Expected result:** scan, authentication, association, address configuration,
receive and transmit each succeed. Record access-point settings, firmware,
reconnect behavior and sustained traffic separately in the network record.

## WCN7850 reference {#sheng}

The reference joins WPA2-Personal networks, gets an address by DHCP and loads web pages.
`sheng-wifi=5` starts Wi-Fi; `sheng-wifi-aj=0` leaves the join to Settings.

| Area | Finding |
| --- | --- |
| Power | Each of the six PMU rails needs RPMh mode, voltage and enable requests. Without the mode request two rails stay off and the link never trains. |
| PCIe | PCIe0 trains at Gen2 x1; the endpoint reads `17cb:1107`. |
| Interrupts | The chip's MSIs go through PCIe0's own MSI receiver to SPI 141, so the worker sleeps between interrupts. |
| Firmware | c7-00108 runs; c2-00259 hangs in its demand pager. The firmware reports a zero MAC, so the board makes one from the chip ID. |
| Scan | 6 GHz is left out: its 59 passive channels would take most of the scan time. |
| Association | The peer entry uses the access point's own HT and VHT capability, not this radio's. Join and the four-way handshake take about 100 ms. |
| Link | A firmware beacon miss is ignored while frames still arrive within 5 s. Frames at VHT MCS 10 and 11 are dropped. |
| System | The system cannot store the network password, so it does not treat the network as known. |

## Next step

Continue with [baseband and cellular](/porting/baseband) on devices with a modem,
or [DSP, audio and power](/porting/power). Return to the
[driver checklist](/porting/drivers).
