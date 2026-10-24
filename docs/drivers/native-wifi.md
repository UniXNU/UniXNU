# NativeWifi

Wi-Fi driver for the Qualcomm WCN7850 on sheng. It compiles the Linux ath12k, MHI and QMI sources over its own compatibility layer and adds its own station layer (scan, join, WPA2-Personal, data path). UniXNU-sheng powers the chip, trains PCIe0 and attaches the module to iPadOS as `en0`.

| Repository | Path | Contents |
| --- | --- | --- |
| [NativeWifi](https://github.com/UniXNU/NativeWifi) | `src/nw_sta.c` | Station layer |
| NativeWifi | `shim/` | Linux compatibility layer |
| NativeWifi | `include/nw_abi.h` | Module and board interface |
| NativeWifi | `tools/prepare.sh` | Fetches and patches the driver sources |
| [UniXNU-sheng](https://github.com/UniXNU/UniXNU-sheng) | `package/WifiProbe.cpp` | Power, PCIe0, firmware, DMA, MSI, module thread |
| UniXNU-sheng | `package/WifiNet.cpp` | `en0` and the system's Wi-Fi requests |

Status: joins WPA2-Personal, gets DHCP, Safari loads pages. Throughput is low.

## Boot arguments

| Argument | Meaning |
| --- | --- |
| `sheng-wifi=5` | Start Wi-Fi. Without it the module never runs. |
| `sheng-wifi-aj=0` | No join at boot; Settings joins. |

## Facts

### Bring-up

- Each of the six PMU rails needs RPMh mode, voltage and enable requests. Without the mode request two rails stay off and the link never trains.
- PCIe0 reaches L0 at Gen2 x1. The endpoint reads `17cb:1107`.
- Firmware c2-00259 hangs in its demand pager. Firmware c7-00108 works and is used.
- The firmware reports a zero MAC. The board supplies one made from the chip ID.
- For development the firmware is read from the spare `oops` partition.

### Station

- 6 GHz is left out of the scan (its 59 passive channels took most of an 11 s scan).
- A firmware beacon miss is ignored while frames still arrive within 5 s.
- Join and the four-way handshake complete in about 100 ms.

### Link rate

- Up to i475 the association had no HT or VHT: phymode 11g, about 20 Mbit/s.
- i477 negotiates HT, VHT and the access point's width (80 MHz). But the peer entry carried this radio's capability, and 596 of 863 transmitted frames were never acknowledged.
- i478 uses the access point's own capability. Almost every frame is acknowledged.
- The access point sends some frames at VHT MCS 10/11. The driver drops them (about 70 per run).

### Interrupts and throughput

- Until i479 the chip's MSIs went to an unwatched memory page and a thread polled the module every 1 ms.
- i479 polled without sleeping while traffic flowed. No speed gain.
- i480 routes the MSIs through PCIe0's own MSI receiver to SPI 141. The thread now sleeps between interrupts: 16 vectors, a few tens of interrupts per second when idle.
- i480 speed test (5 GHz, 80 MHz, -73 dBm): about 12 Mbit/s down, 24 Mbit/s up, under 1 % transmit loss.
- i480 DHCP: address within 31 s of boot.

### System Wi-Fi daemon

- In i478 the daemon took over, left the boot join and scanned until a manual join at 85 s. It did not leave in i480.
- The system cannot store the network password (keychain error -25291).

### Heat

- The hot processes are `coreduetd` (pid 102) and pid 43, not the Wi-Fi thread.

## Guesses

- The throughput limit is in the receive path to `ifnet_input` (one copied frame per call) or in the TCP window.
- The daemon leaves the boot join because the network is not stored as known.
- The heat comes from system daemons and the GPU path.

## Plan

1. Count frames per second at each receive stage during a speed test.
2. Pass received frames to the stack in chains, without the extra copy.
3. Load the firmware from files instead of `oops`, then restore `oops`.
4. Later: 6 GHz, Wi-Fi 6/7 capability, power save.

## Build

`unixnu build kernel` compiles the module with UniXNU-sheng's `scripts/build-native-wifi.py`, from `drivers/NativeWifi` in UniXNU-sheng or `NATIVE_WIFI_DIR`.
