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

`sheng-bluetooth=1` starts the UART14 worker after addon installation. The board
binds GENI SE6 at 0x898000, IRQ 493 and QUP2 DMA SID 0x423. SM8550 operations
select the exact 51.2 MHz source for 3.2 Mbaud and map a 32 KiB DMA aperture
with native 4 KiB pages. Configuration locks coordinate clock votes and SMMU
allocation with touch and audio. GPIO79 wakes the gated UART through the shared
TLMM IRQ. The UART requires protocol-2 microcode from the boot firmware.

The board exports a Bluetooth device-tree node and a matching IOService before
userland starts. H4 UART.SK encoding and 3.2 Mbaud use four-byte little-endian
properties. Both carry the stable private address derived from the platform
identity. The Linux boundary converts the public address to bdaddr_t order.

The resolved QcaBluetooth checkout supplies both kernel and userland builds.
UART clock-restore failures end the transport with the original error and stop
forwarding and retries.

Controller shutdown and faults wake both UART.SK rings. Their synchronization
callbacks return the controller error before moving data. Notifications retain
the rings until completion so disconnect can drain them.

The worker retains its DMA memory, services bounded batches and sleeps on IRQ,
ring-space or deadline events. Hardware faults abort command waiters immediately.
The `[bluetooth]` boot-log row records phase, transfers, sleep, power ownership
and SMMU status. `log-bluetooth=1` adds initialization messages.

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

From the workspace root, board checks are:

```sh
python3 UniXNU-sheng/scripts/check-bluetooth-platform.py
python3 UniXNU-sheng/scripts/check-bluetooth-shared.py
python3 UniXNU-sheng/scripts/check-bluetooth-board.py /path/to/assembled/tree
```

The platform model checks frequency ratios, DFS handoff, independent DMA tables,
ASID conflicts and timeout bounds. The shared-resource model checks IRQ dispatch,
concurrent registration and UART/audio clock ownership. UART14, ArmCpu, touch,
audio and boot-log sources compile for the selected target; the build recipe
compiles eight protocol and SoC objects into the board archive inputs.

The version-locked iPadOS 27 adapter selects controller type zero and retains
standard HCI initialization. Capabilities follow Supported Commands and LE
Features, including coded and 2M PHY. An asynchronous 0x203b query supplies
advertising capacity, capped at the native array's six records. Model getters,
configuration caches, lower flags and broadcaster mode receive the same values.
Normal packet traffic stays in UART.SK and the native stack.

The offline patch retains authenticated fixup metadata and PACIBSP entry pads.
It passes 144 native instruction cases at two ASLR slides; PAC operations are
modeled without device keys. The production publisher passes 58 ASan/UBSan HCI
and policy cases. `tools/build-type0.py` builds and signs the arm64e library.
The board's `payload.runtime` selects `build-bluetooth-userspace.py` for ios27.
It stages signed BlueTool, bluetoothd and QcaBTType0.dylib with pinned firmware.
The native daemon keeps its original identifier and entitlements. Read-only
unions expose /usr/lib and /usr/sbin entries, with the library mounted first.
BlueTool keeps its Mach service and runs as root with transactions enabled.
Wi-Fi and Bluetooth share one signed launchd cache; other native jobs remain
unchanged. Missing code hashes are appended to the preserved trust bundle.

`check-bluetooth-runtime.py` validates the packed addon, signatures, firmware,
launchd jobs, trust modules and original Data seed. The combined addon verifies
45 files, three signed Bluetooth binaries and 716 launchd jobs. Host libxpc
accepts the cache. The complete kernel, fileset, FAT payload and temporary boot
image build successfully with the explicit local component. The packed payload
contains the Bluetooth exports, H4/baud properties, signed runtime and preserved
Data seed, with automatic reset disabled. Device scanning, pairing, audio,
power and coexistence measurements are pending.

The current device boot reaches the overlays, then launchd reports `No service cache`.
The loader trusts and sends both the Bluetooth cache and the Wi-Fi baseline;
launchd rejects both at its cache parser. All 715 system jobs remain present.
The opt-in `sheng-cache-log=1` diagnostic records the actual parser input length
and hash on a matched 24A446 failure stack.

Bluetooth DMA allocation reports context-bank ENOSPC with 98 free stream slots.
The allocator accepts disabled banks by SCTLR.M and retains selection evidence
without extra MMIO scans. Register simulation and target compilation pass;
device startup, feature and performance measurements remain pending.

Select the local component from the UniXNU checkout:

```sh
./unixnu build kernel payload -D /path/to/UniXNU-sheng --os 27 \
  --local-module driver:QcaBluetooth=/path/to/QcaBluetooth
```

Supply the preserved installation inputs from [Runtime inputs](/porting/packaging#runtime-inputs-for-ios-27),
then follow [Boot image](/concepts/payload) for temporary device startup.

Sources: [Linux](https://github.com/ianchb/sm8550-mainline),
[Debian sheng](https://github.com/ianchb/debian-sheng),
[Renoir UART.SK reference](https://github.com/daimile2/renoir_xnu_bluethooth).
