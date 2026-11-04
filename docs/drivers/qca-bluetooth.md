# QcaBluetooth

QcaBluetooth connects a Qualcomm WCN7850 UART controller to Apple's Bluetooth
stack. Board integration lives in `UniXNU-sheng`; the component is under
`drivers/QcaBluetooth` during development.

## Layers

The board supplies WCN power ownership, clocks, pins, DMA mappings and IRQs.
`WcnPower.h` exposes independent Wi-Fi and Bluetooth votes over the shared
six supplies. The last owner releases them; Bluetooth-only startup skips the
PCIe bus vote. Wi-Fi's startup uses this ownership path.
The driver runs the locked Linux `btqca.c` initialization, H4 framing and IBS.
UART.SK/Skywalk carries H4 bytes to `bluetoothd`; BlueTool requests controller
startup through `kern.sheng_bt_control`. Apple's stack owns scanning, pairing,
keys, BLE and audio profiles.

GENI uses four 2048-byte RX buffers and one 4096-byte TX buffer. Hard IRQ
masks its line and wakes the worker. RX backpressure retains buffer ownership
and stops RFR when full. TX completion checks DMA and wire drain. IBS control
bytes enter only between complete H4 packets. Physical clock-off requires
completed RX quiescence and an armed hardware wake source.

The board stages hashed firmware under `firmware/qca` in the Data addon.
`package/BluetoothFirmware.h` defines the same path used by
`scripts/stage-bluetooth-firmware.py`. VFS reads wait for addon installation.

## Build and checks

From the component checkout:

```sh
python3 tools/test-runtime.py
python3 tools/test-geni.py
python3 tools/check-kernel.py /path/to/assembled/tree
python3 tools/build-bluetool.py
```

Runtime and DMA simulations pass ASan/UBSan. The protocol, Linux adapter,
original `btqca.c`, DMA engine, Skywalk transport and board firmware reader
compile with the iPadOS 27 arm64e kernel command. Their references exist in the
selected kernel. BlueTool compiles and passes code-signature verification.
The board power check covers both radio startup orders, independent release,
idempotent votes and failed transitions; the Wi-Fi consumer compiles for arm64e.

Board resource binding, runtime packaging and the iPadOS 27 native controller
adapter remain in development. Hardware scanning, pairing, audio, power and
Wi-Fi coexistence measurements are pending.

Sources: [Linux](https://github.com/ianchb/sm8550-mainline),
[Debian sheng](https://github.com/ianchb/debian-sheng),
[Renoir UART.SK reference](https://github.com/daimile2/renoir_xnu_bluethooth).
