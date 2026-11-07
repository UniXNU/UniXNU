# QcaBluetooth

QcaBluetooth connects a Qualcomm WCN7850 UART controller to Apple's Bluetooth
stack.

[Source repository](https://github.com/UniXNU/QcaBluetooth).

## Status

Device: Xiaomi Pad 6S Pro (sheng), iPadOS 27.0.1 (24A446).

| State | Features |
| --- | --- |
| Working | Pairing, reconnection after reboot, power toggle, A2DP playback, AirPods noise control and battery, use alongside Wi-Fi |
| Not tested | Calls and microphone (HFP/SCO), sleep and wake |
| Unavailable | Features that need Apple vendor commands |

## Layers

The driver runs the locked Linux `btqca.c` initialization, H4 framing and IBS.
UART.SK/Skywalk carries H4 bytes to `bluetoothd`. Apple's stack owns scanning,
pairing, keys, BLE and audio profiles.

GENI uses four 2048-byte RX buffers and one 4096-byte TX buffer. Hard IRQ masks
its line and wakes the worker. RX backpressure retains buffer ownership and stops
RFR when full. TX completion checks DMA and wire drain. IBS control bytes enter
only between complete H4 packets. Clock-off requires RX quiescence and an armed
hardware wake source.

| Sysctl | Meaning |
| --- | --- |
| `kern.qbt_boot` | Controller state |
| `kern.qbt_power_on` | Reading starts the controller and returns the result |
| `kern.qbt_firmware` | Loaded firmware name |

All three are read-only because BlueTool's sandbox denies sysctl writes.
Connecting to UART.SK also starts a stopped controller.

## Board integration

The full procedure is in [Bluetooth adaptation](/porting/bluetooth).

The board supplies WCN power, clocks, pins, DMA mappings, IRQs and firmware.
`WcnPower.h` keeps independent Wi-Fi and Bluetooth votes over the shared supplies;
the last owner releases them.

On sheng, `sheng-bluetooth=1` starts the UART14 worker after the Data addon
installs. It binds GENI SE6 at 0x898000, IRQ 493 and QUP2 DMA SID 0x423. An exact
51.2 MHz source gives 3.2 Mbaud. DMA buffers use the firmware-managed bypass bank
shared with touch and audio. GPIO79 wakes the gated UART. The UART needs
protocol-2 microcode from the boot firmware.

The board exports `/arm-io/bluetooth` and a matching IOService before userland
starts, with H4 encoding, baud rate and a stable private address.

## Native adapter

The iPadOS 27 adapter is locked to one `bluetoothd` binary:

- Every product runs as controller type zero with standard HCI initialization.
- Capabilities follow Supported Commands and LE Features. Advertising capacity
  comes from 0x203b, capped at six sets.
- Extended scanning uses 0x2041 and 0x2042. Random addresses are sent before a
  scan or an advertising set starts.
- The patch keeps authenticated fixups and PACIBSP entry pads.

`payload.runtime` selects `build-bluetooth-userspace.py`, which stages signed
BlueTool, `bluetoothd` and `QcaBTType0.dylib` with pinned firmware. Read-only
unions expose them under `/usr/lib` and `/usr/sbin`. Wi-Fi and Bluetooth share
one signed launchd cache.

Pairing keys need the keychain, which needs [AppleKeyStoreState](/drivers/apple-key-store-state)
key wrapping.

## Audio

The audio overlay hides the system HAL plug-in directory. List
`BTAudioHALPlugin.driver` in `audio_system_plugins` under `payload.runtime`, and
the runtime builder copies the unchanged bundle from the OS image.

## Build and checks

```sh
python3 tools/test-runtime.py
python3 tools/test-geni.py
python3 tools/build-bluetool.py
python3 tools/build-type0.py
python3 tools/check-kernel.py /path/to/tree --record <kernel source compile record> \
    --extra-source <board source> --board-export <symbol>
```

Run these from the component checkout. `native-ios27.md` lists the native adapter
checks. From the workspace root, the sheng board checks are:

```sh
python3 UniXNU-sheng/scripts/check-bluetooth-platform.py
python3 UniXNU-sheng/scripts/check-bluetooth-shared.py
python3 UniXNU-sheng/scripts/check-bluetooth-board.py /path/to/tree
python3 UniXNU-sheng/scripts/check-bluetooth-runtime.py
```

`log-bluetooth=1` adds initialization messages to the boot log's `[bluetooth]`
rows, and `log-bluetooth=2` adds process and controller output rows.

Supply the installation inputs from [Runtime inputs](/porting/packaging#runtime-inputs-for-ios-27),
then follow [Boot image](/concepts/payload).

Sources: [Linux](https://github.com/ianchb/sm8550-mainline),
[Debian sheng](https://github.com/ianchb/debian-sheng),
[Renoir UART.SK reference](https://github.com/daimile2/renoir_xnu_bluethooth).
