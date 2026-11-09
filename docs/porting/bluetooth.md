# Bluetooth adaptation

Complete [platform interrupts and DMA](/porting/platform) and supply the
[runtime inputs](/porting/packaging#runtime-inputs-for-ios-27). [QcaBluetooth](https://github.com/UniXNU/QcaBluetooth)
runs the Linux `btqca.c` initialization over a GENI UART and carries H4 bytes to Apple's
`bluetoothd` through UART.SK. Apple's stack owns scanning, pairing, keys, BLE and audio
profiles.

Use [driver build integration](/porting/drivers#build-integration) to connect the
recipe, then run this page's checks.

## Sources and interfaces {#source-map}

| Implementation | Source | What to read and implement |
| --- | --- | --- |
| Protocol core | [qbt.h](https://github.com/UniXNU/QcaBluetooth/blob/22ff97f93416452335bb61badb14c762da653487/include/qbt.h) | `qbt_platform` callbacks, `qbt_create`, `qbt_boot`, `qbt_step`, `qbt_deadline` |
| UART | [qbt_geni.h](https://github.com/UniXNU/QcaBluetooth/blob/22ff97f93416452335bb61badb14c762da653487/include/qbt_geni.h) | GENI DMA, IRQ service, drain and quiesce |
| Kernel pipe | [qbt_transport.h](https://github.com/UniXNU/QcaBluetooth/blob/22ff97f93416452335bb61badb14c762da653487/include/qbt_transport.h) | UART.SK operations and power requests |
| Board integration | [BluetoothProbe.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/ce0c600fa015964d4ecb6af864fa2ab66efa915f/package/BluetoothProbe.cpp), [WcnPower.h](https://github.com/UniXNU/UniXNU-sheng/blob/ce0c600fa015964d4ecb6af864fa2ab66efa915f/package/WcnPower.h) | Resources, power order, worker and shared supplies |
| Native stack | [native-ios27.md](https://github.com/UniXNU/QcaBluetooth/blob/22ff97f93416452335bb61badb14c762da653487/native-ios27.md) | `bluetoothd` routing, scanning and capabilities |

## 1. Collect the hardware inputs

Read these from the target's DTS:

| Input | sheng value |
| --- | --- |
| UART | QUP2 SE6 at `0x898000`, GIC INTID 493 |
| DMA stream | Apps SMMU `0x423` |
| CTS, RTS, TX, RX | GPIO 76, 77, 78, 79 |
| `BT_EN` | GPIO 81 |
| Wake source | GPIO 79 |
| Serial clock and rate | 51.2 MHz, 16x oversampling, 3.2 Mbaud |
| Firmware | `hmtbtfw20.tlv`, `hmtnv20.bin` |

Pin the firmware in `firmware/bluetooth/manifest.json` and stage it in the device repository:

```sh
python3 scripts/stage-bluetooth-firmware.py OUTPUT --source FIRMWARE_QCA_DIRECTORY
```

The UART needs protocol 2 microcode from the boot firmware. `powerOn` returns `ENXIO` when
the engine reports another protocol.

## 2. Implement the power path

Share the WCN supplies with Wi-Fi through `sheng_wcn_power_get` and `sheng_wcn_power_put`.
Each radio holds one vote, and the last owner releases the supplies.

`powerOn` runs in this order:

1. Map the resources and set up 32 KiB of DMA buffers through `smmu_plan_bypass` and
   `smmu_configure_bypass`, holding `AppsSmmuLock`.
2. Take the Bluetooth power vote.
3. Hold `BT_EN` low for 100 ms, then enable the serial clock.
4. Check the QUP version and protocol, then prepare the engine.
5. Attach the UART interrupt and the wake interrupt.
6. Raise `BT_EN`, wait 60 ms, then enable the pin pulls.
7. Call `qbt_geni_start`, then `qbt_boot` with the rate and address.

`powerOff` shuts the controller down, quiesces the engine, lowers `BT_EN` and releases the vote.
Return the first error so a failed step reaches `qbt_transport_power_result`.

## 3. Start the worker

Call `sheng_bluetooth_probe` from the late platform probe. The worker:

1. Fills `qbt_platform` and calls `qbt_create`, then `qbt_transport_init`.
2. Waits for the Data addon, since the firmware reader needs it.
3. Moves bytes between `qbt_transport` and `qbt_transmit`, and sleeps until the earlier of
   `qbt_deadline` and `qbt_geni_deadline`.

## 4. Publish the controller

Add the node to the device tree:

```text
bluetooth {
    device_type = "bluetooth";
    compatible = "qcom,wcn7850-bt";
    unixnu,adt-name = "bluetooth";
    transport-encoding = <1>;
    transport-speed = <3200000>;
    status = "okay";
};
```

Before userland starts, the board sets `local-mac-address` and `/chosen/mac-address-bluetooth0`
and registers an `IOService` named `bluetooth` with the same properties.

## 5. Connect the native stack

Set these under `payload.runtime` in `board.toml`:

```toml
audio_system_plugins = ["BTAudioHALPlugin.driver"]
bluetooth_tool = "scripts/build-bluetooth-userspace.py"
bluetooth_target = "ios27"
```

The tool stages signed BlueTool, `bluetoothd` and `QcaBTType0.dylib` with the firmware.
`patches/xnu-12377/sheng-bluetooth-runtime.patch` mounts them over `/usr/lib` and `/usr/sbin`.
`audio_system_plugins` keeps the Bluetooth HAL plug-in visible through the audio overlay.

The adapter is locked to one `bluetoothd` hash. For another OS build, follow
[native-ios27.md](https://github.com/UniXNU/QcaBluetooth/blob/22ff97f93416452335bb61badb14c762da653487/native-ios27.md)
and locate its patch sites again.

Pairing keys need the keychain, which needs [AppleKeyStoreState](/drivers/apple-key-store-state).
The board returns `/chosen/unique-chip-id` through `native_aks_device_id`.

## 6. Build and verify

From the workspace root:

```sh
python3 UniXNU-<device>/scripts/check-bluetooth-platform.py
python3 UniXNU-<device>/scripts/check-bluetooth-shared.py
python3 UniXNU-<device>/scripts/check-wcn-power.py
```

From the UniXNU checkout, with `sheng-bluetooth=1` and `log-bluetooth=2` in the board's boot
arguments:

```sh
./unixnu build kernel payload -D ../UniXNU-<device> --os <profile>
./unixnu bootimg -D ../UniXNU-<device> --os <profile> --dtb <device>.dtb -o boot.img
fastboot boot boot.img
```

**Expected result:** after [capturing the log](/porting/log-capture), `[bluetooth]` shows
`state=2 error=0` and `[bluetooth proc]` shows one `bluetoothd` start. In Settings, turn
Bluetooth on, pair an accessory and play audio. Restart and confirm it reconnects without
pairing again.

| Symptom | Check |
| --- | --- |
| Settings item stays gray | `bluetoothd` launchd job and the `[bluetooth proc]` restart count |
| `[bluetooth uart]` shows faults or errors | Serial clock rate, DMA mapping and pins |
| Pairing keys are lost or `bluetoothd` reports a keychain problem | AppleKeyStoreState key wrapping |
| Audio stays on the speaker | `audio_system_plugins` |

Record device results as described in [Porting record](/porting/records).

## Next step

Continue with [USB](/porting/usb).
