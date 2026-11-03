# Ath12kWifi

Ath12kWifi runs Linux ath12k, mac80211 and cfg80211 on XNU. It uses MHI,
QRTR and QMI for device startup and wpa_supplicant 2.12 for userspace
SME/WPA authentication. Ordinary network packets stay in the kernel.

| Field | Value |
| --- | --- |
| Repository | [UniXNU/Ath12kWifi](https://github.com/UniXNU/Ath12kWifi) |
| Sources | Pinned Linux v7.0.14, matching headers and supplicant 2.12 |
| Board inputs | Power, PCIe, BARs, MSI, DMA, firmware and network interface |
| Native interface | `include/nw_abi.h`, `org.unixnu.wifi.control` |
| Selected profiles | Open and WPA2-PSK with PMF |

Follow the [network adaptation procedure](/porting/network) for board inputs
and build integration. The [catalog](/reference/components) records dependencies.

## Runtime and performance

The production manifest starts cfg80211/mac80211 before ath12k and selects
the mainline station runtime. The native control broker serializes scan,
authentication, association, key, EAPOL and radio commands on the wireless
worker. Owner IDs and connection generations associate events with active requests.

The supplicant owns password derivation, handshake and rekey. Profiles live
in RAM; wifid supplies network selection and OS-saved credentials. Radio
power-on waits for that selection. Closing an owner releases its interface.

mac80211 supplies aggregation, reordering, FQ and AQL. DMA clones and A-MSDU
fragments share storage. TX copies directly from the retained mbuf into DMA;
RX copies fragments into aligned cached mbufs and submits up to 64 frames
per batch. NAPI has a 256-packet/2 ms budget; work dispatch has a 64-item/2 ms
budget. MSI and pending deadlines control worker sleep. Cached counters
provide PHY rate and RSSI without firmware statistics requests.

## sheng on iPadOS 27

WifiProbe supplies board hardware operations; WifiNet exposes en0 and
Apple80211. WCN7850 is exported as `/arm-io/wlan`, satisfying the stock
24A446 wifid job's device-tree condition. The DMA window is 128 MiB.

The signed supplicant runs at `/usr/libexec/unixnu-wpa_supplicant` through a
read-only Data-backed overlay. Its configuration is under
`/private/var/ngpu/etc/wifi/`. Packaging merges its job into the OS launchd
cache, preserves stock jobs, serializes with Apple `plutil binary1`, and
packages the matching detached signature and trust hashes.

Firmware loads through VFS from
`/private/var/ngpu/firmware/ath12k/WCN7850/hw2.0/` after addon installation.
The board's `package/WifiFirmware.h` defines both the loader and packer path;
`firmware/wcn7850/manifest.json` pins file sizes and SHA-256 hashes.

WifiNet accepts 592-byte and 656-byte association requests. The 24A446
asynchronous result contains 540 initialized bytes, with result and validity
at 0x214/0x218. Explicit joins complete after port authorization. Cancellation
completes a pending request once; unanswered joins expire after 30 seconds.
Disconnect and power-off publish BSD and Apple80211 link-down events.

RSSI comes from the association BSS and a peer-cache refresh once per second.
Changes of at least 3 dB publish link updates. SNR is floored at zero.

| Setting | Current behavior |
| --- | --- |
| `sheng-wifi=5` | Start the mainline Wi-Fi stack |
| `sheng-wifi-aj=0` | Let Settings/wifid select networks |
| `log-wifi=1` | Enable Wi-Fi diagnostics |
| `log-gpu=0 log-display=0` | Skip GPU/display diagnostic collection |
| Automatic reset | Disabled in the current temporary image |

## Verification

From Ath12kWifi, run the checks affected by a change:

```sh
python3 tools/fetch-sources.py --check
python3 tools/test-mainline-runtime.py
python3 tools/test-supplicant.py
python3 tools/test-cfg80211-control.py
python3 tools/check-mainline-link.py --build-report FILE --kernel FILE
```

Host fixtures pass ASan/UBSan with simulated radio operations. The core
lifecycle releases 287 tracked allocations. Production auditing covers
125 objects and 13 XNU imports, with zero missing imports or duplicate definitions.
Board fixtures cover Apple80211, event allocation, RX batching and VFS reads.
The kernel, payload, signatures, firmware files and packed boot image pass checks.

Device verification covers Wi-Fi toggling, SSID scanning, WPA2 association,
DHCP, traffic and join-result delivery. Current device checks pending:
cancellation/timeout completion, signal display, Data firmware startup,
throughput, jitter and heat. See the [sheng network record](/devices/sheng#network).
