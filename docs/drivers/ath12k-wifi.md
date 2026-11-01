# Ath12kWifi

Start with the [adaptation procedure](/porting/network) for board inputs, source changes, build integration and verification order.

Ath12kWifi implements an ath12k-based Wi-Fi stack with PCI, MHI, QRTR, and
board-supplied interfaces. The source includes QCC2072, QCN9274, and WCN7850
hardware definitions.

| Field | Value |
| --- | --- |
| Repository | [UniXNU/Ath12kWifi](https://github.com/UniXNU/Ath12kWifi) |
| Function | ath12k Wi-Fi transport and driver integration |
| Board inputs | PCI access, interrupts, firmware and board callbacks |
| Hardware verification | Record device-specific results in the device page |

Read the component README and `nw_board` interfaces before selecting it. The
catalog records its source revision, OS requirements, build command, and outputs.
Use the component's host checks and the board's network verification procedure.

## State on sheng (WCN7850)

Ath12kWifi compiles the Linux ath12k, MHI and QMI sources over its own compatibility layer (`shim/`) and adds a station layer (`src/nw_sta.c`: scan, join, WPA2-Personal, data path). The board interface is `include/nw_abi.h`. `tools/prepare.sh` fetches and patches the driver sources. UniXNU-sheng powers the chip, trains PCIe0 and attaches the module to iPadOS as `en0` (`package/WifiProbe.cpp`: power, PCIe0, firmware, DMA, MSI, module thread; `package/WifiNet.cpp`: `en0` and the system's Wi-Fi requests).

Status: joins WPA2-Personal, gets DHCP, Safari loads pages. Throughput is low.

| Boot argument | Meaning |
| --- | --- |
| `sheng-wifi=5` | Start Wi-Fi. Without it the module never runs. |
| `sheng-wifi-aj=0` | No join at boot; Settings joins. |

### iPadOS 27 service startup

The sheng board DTS exports WCN7850 as `/arm-io/wlan` using
`unixnu,adt-name = "wlan"`. The stock 24A446 `com.apple.wifid` job checks
`_LimitLoadToDeviceTree` before launchd loads it. Without a matching node,
the kernel's `join.txt` path can still connect and exchange packets while
Settings shows an empty Wi-Fi page and cannot enable the switch.
`/chosen/mac-address-wifi0` and the IOService network objects do not satisfy
this device-tree condition.

The 27 payload defaults include `sheng-wifi=5`. After changing the DTS,
rebuild the payload and boot image, then inspect the ADT inside the image.
Settings on sheng can toggle Wi-Fi and list SSIDs. Manual test images
should omit `sheng-autoreset`.

WifiNet supports both 592-byte legacy and 656-byte 24A446 association
requests and validates credentials before authentication. Manual WPA2
association and DHCP have device confirmation.

Power-off and disconnect publish link-down notifications and hide stale
connection state. Repeated joins preserve completion; switching networks
waits for teardown before queuing a new join. Authentication queries report
WPA2 personal as 0x10. Host regression with AddressSanitizer and
UndefinedBehaviorSanitizer, the kernel/payload build and packed-image
checks pass. The current image awaits device validation of joining,
network switching, the Wi-Fi icon and password-sheet dismissal.

Throughput is low and remains under investigation. Use `log-wifi=1` for
join diagnostics and `sheng-wifi-aj=0` to disable driver auto-join.

### Facts

- Each of the six PMU rails needs RPMh mode, voltage and enable requests. Without the mode request two rails stay off and the link never trains.
- PCIe0 reaches L0 at Gen2 x1. The endpoint reads `17cb:1107`.
- Firmware c2-00259 hangs in its demand pager. Firmware c7-00108 works and is used.
- The firmware reports a zero MAC. The board supplies one made from the chip ID.
- For development the firmware is read from the spare `oops` partition.
- 6 GHz is left out of the scan: its 59 passive channels took most of an 11 s scan.
- A firmware beacon miss is ignored while frames still arrive within 5 s.
- Join and the four-way handshake complete in about 100 ms.
- Without HT and VHT in the association the link ran phymode 11g, about 20 Mbit/s. With the access point's width (80 MHz) but this radio's capability in the peer entry, 596 of 863 transmitted frames were never acknowledged. With the access point's own capability almost every frame is acknowledged.
- The access point sends some frames at VHT MCS 10/11. The driver drops them (about 70 per run).
- With the chip's MSIs on an unwatched page, a thread polled the module every 1 ms. Routing them through PCIe0's own MSI receiver to SPI 141 lets the thread sleep between interrupts: 16 vectors, a few tens of interrupts per second when idle.
- Speed test (5 GHz, 80 MHz, -73 dBm): about 12 Mbit/s down, 24 Mbit/s up, under 1 % transmit loss. DHCP gives an address within 31 s of boot.
- The system Wi-Fi daemon takes over from the boot join and scans until a manual join. The system cannot store the network password (keychain error -25291).
- The hot processes are `coreduetd` and one other system process, not the Wi-Fi thread.

### Guesses

- The throughput limit is in the receive path to `ifnet_input` (one copied frame per call) or in the TCP window.
- The daemon leaves the boot join because the network is not stored as known.
- The heat comes from system daemons and the GPU path.

### Plan

1. Count frames per second at each receive stage during a speed test.
2. Pass received frames to the stack in chains, without the extra copy.
3. Load the firmware from files instead of `oops`, then restore `oops`.
4. Later: 6 GHz, Wi-Fi 6/7 capability, power save.

### Build

`unixnu build kernel` compiles the module with UniXNU-sheng's `scripts/build-ath12k-wifi.py`, from `drivers/Ath12kWifi` in UniXNU-sheng or `ATH12K_WIFI_DIR`.
