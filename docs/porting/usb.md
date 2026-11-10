# USB adaptation

Complete [platform interrupts and DMA](/porting/platform) first. [QcomDwc3](https://github.com/UniXNU/QcomDwc3)
derives from Apple's `AppleUSBXDCI` and `AppleUSBXHCI`. The port supplies the register
window, interrupt, power and PHYs. Apple's USB stacks, `configd` and `lockdownd` run
unchanged.

Use [driver build integration](/porting/drivers#build-integration) to connect the
recipe, then run this page's checks.

## Sources and interfaces {#source-map}

| Implementation | Source | What to read and implement |
| --- | --- | --- |
| Controller | [QcomDwc3.cpp](https://github.com/UniXNU/QcomDwc3/blob/e4efe95c903a737e0f5955e5b50a8fb4d2a7d718/QcomDwc3.cpp) | `bringUp`, `qcom_dwc3_publish`, class overrides and role changes |
| PHYs | [QcomEusb2Phy.h](https://github.com/UniXNU/QcomDwc3/blob/e4efe95c903a737e0f5955e5b50a8fb4d2a7d718/QcomEusb2Phy.h), [QcomQmpUsb3.h](https://github.com/UniXNU/QcomDwc3/blob/e4efe95c903a737e0f5955e5b50a8fb4d2a7d718/QcomQmpUsb3.h) | eUSB2, repeater and QMP sequences |
| Cable role | [QcomUcsi.h](https://github.com/UniXNU/QcomDwc3/blob/e4efe95c903a737e0f5955e5b50a8fb4d2a7d718/QcomUcsi.h), [ShengBattery.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/ce0c600fa015964d4ecb6af864fa2ab66efa915f/package/ShengBattery.cpp) | UCSI messages over the charger's GLINK channel |
| Board entry | [UsbProbe.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/ce0c600fa015964d4ecb6af864fa2ab66efa915f/package/UsbProbe.cpp) | Kext loads and class registration |
| Build | [build-gop-legacy-display-27.py](https://github.com/UniXNU/UniXNU-sheng/blob/ce0c600fa015964d4ecb6af864fa2ab66efa915f/scripts/build-gop-legacy-display-27.py), [board.toml](https://github.com/UniXNU/UniXNU-sheng/blob/ce0c600fa015964d4ecb6af864fa2ab66efa915f/board.toml) | Generated class header and prelink roots |

The hardware sequences follow [mainline Linux](https://github.com/ianchb/sm8550-mainline).

## 1. Collect the hardware inputs

Read these from the target's DTS and clock definitions:

| Input | sheng value |
| --- | --- |
| DWC3 base and Apple register window | `0x0a600000`, window at base + `0xc000` |
| Interrupt | GIC INTID 165 |
| SMMU stream | `0x40` |
| eUSB2 reference clock | 38.4 MHz |
| PHYs and rails | eUSB2 PHY, PMIC repeater, QMP combo PHY, retimer, GDSCs, RPMh rails |

The SoC values are constants in `QcomDwc3.cpp`. Generate a QMP table for another SoC from
its Linux tree, in the device repository:

```sh
python3 scripts/gen-qmp-usb3-table.py LINUX_TREE drivers/QcomDwc3/QcomQmpUsb3.h
```

## 2. Bring up the controller

`bringUp` runs in this order and stores each step in `native_usb_stats[0]`. A negative
value is the step that failed.

| Stage | Step |
| --- | --- |
| 1 | Map the clock, TCSR, PHY and QSCRATCH windows |
| 2 | Vote the rails |
| 3 | Enable the GDSCs |
| 4 | Enable clocks and release resets |
| 5 | Create the stream's SMMU context |
| 6 | Start the repeater |
| 7 | Start the eUSB2 PHY, then the QMP PHY; fall back to the UTMI clock if QMP does not start |
| 8 | Read the core ID through the register window |
| 9 | Hardware ready |

`AppleUSBXDCI` does no cache maintenance. Give the controller's stream a stage 1 identity
context with write-back inner shareable blocks.

**Expected result:** stage 9 with a DWC3 core ID in `native_usb_stats[1]`.

## 3. Register the classes

The board starts one worker thread when `usb` is set. It runs:

1. `qcom_dwc3_bring_up`.
2. `OSKextLoadKextWithIdentifier` for `com.apple.driver.AppleUSBXDCI` and
   `com.apple.driver.usb.AppleUSBXHCI`. `AppleUSBXDCI` has no personality, so nothing else
   loads it.
3. `OSMetaClass::preModLoad`, the driver's static initializer and `postModLoad`.
4. `qcom_dwc3_publish`, which attaches the provider nub and starts the device stack.

Add the USB stacks to the prelink roots in `[kernel.prelink]` of `board.toml`.

The class layouts come from the selected kernelcache. `scripts/gen-usb27-abi.py` and
`scripts/gen-usb27-host-abi.py` write `scripts/usb-xdci-24A446.json` and
`scripts/usb-xhci-24A446.json`. Both scripts name the 24A446 kernelcache and class
addresses; change these for another OS build.

Keep two overrides when the layouts change:

- Slot 179 of `AppleUSBXDCI` returns false without an `IOPort` transport object.
- In host mode the xHCI subclass answers on for the family's desired power, and the device
  stack answers 0.

**Expected result:** stage 12, and `IOUSBDeviceFamily` starts on the nub.

## 4. Connect the cable role

Call these from the board's charger driver:

| Function | Use |
| --- | --- |
| `qcom_dwc3_vbus(int)` | The charger's USB online value |
| `qcom_ucsi_start`, `qcom_ucsi_receive`, `qcom_ucsi_tick` | Send each returned message on the GLINK channel |
| `qcom_ucsi_polling` | True while the driver needs the 20 ms timer |

A host on the cable selects the device role and a peripheral selects the host role. With
no answer from either source, the device role runs. Check the UCSI client from
`drivers/QcomDwc3/tests`:

```sh
clang++ -std=c++17 -I.. ucsi_host.cpp && ./a.out
```

## 5. Answer the Mac's pairing checks

| Answer | Where |
| --- | --- |
| `chip-id` | `[payload.adt]` in `board.toml` |
| `board-id`, `security-domain` | `adt.chosen.u32` in the OS profile |
| One file system number for `/System` and system daemons | [`native-union-statfs-fsid`](/xnu/patch-reference) |
| Lock state 3 | [`aks-sls=3`](/xnu/boot-arguments) |

Use the model's row in the device map inside `MobileDevice.framework` for the three IDs.

## 6. Build and verify

From the UniXNU checkout, with `usb=1` and `log-sys=1` in the board's boot arguments:

```sh
./unixnu build kernel payload -D ../UniXNU-<device> --os <profile>
./unixnu bootimg -D ../UniXNU-<device> --os <profile> --dtb <device>.dtb -o boot.img
fastboot boot boot.img
```

Connect the device to a Mac:

```sh
ioreg -p IOUSB -l -w0 | grep -E 'idVendor|idProduct|Device Speed'
```

**Expected result:** the Mac lists the device, with `Device Speed` 4 on a USB 3 cable.
Unlock it and tap Trust; the Mac then reports it as paired and starts a lockdown session.
[Capture the log](/porting/log-capture) to read the `[usb]` rows.

| Symptom | Check |
| --- | --- |
| Chirp passes, high-speed data fails | eUSB2 reference clock table |
| `ep0OutEventOccurred: event 0` | Stage 1 SMMU context |
| PAC panic while creating the TRB pool | `AppleUSBXDCI` kext load before class registration |
| `bNumConfigurations` is 0 and the host resets | Slot 179 |
| The Mac asks for a software update | `chip-id`, `board-id`, `security-domain` |
| `UserDeniedPairing` with no dialog on the panel | File system number of `/System` |
| A passcode prompt after Trust | Lock state |

To test host mode, set `usb-host=<s>` to force it after a delay and
`usb-back=<s>` to return to the cable's role. Record device results as described in
[Porting record](/porting/records).

## Next step

Continue with [baseband and cellular](/porting/baseband) on devices with a modem, or
[DSP, audio and power](/porting/power).
