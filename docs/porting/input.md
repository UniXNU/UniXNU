# Touch and button adaptation

Complete [display geometry](/porting/display) and [interrupt/DMA setup](/porting/platform).
Record touch-controller model, firmware, matrix geometry, physical orientation,
bus wiring, reset/IRQ pins and the OS HID ABI.

Use [driver build integration](/porting/drivers#build-integration) to connect
initialization, archive recipes and the OS ABI, then run this page's hardware checks.

## Sources and interfaces {#source-map}

These links identify reviewed source revisions. Match interfaces to the selected
SoC, component and OS versions. The linked device sources provide board integration
examples.

| Implementation | Source | What to read and implement |
| --- | --- | --- |
| Bus and sensor | [GeniSpi.h](https://github.com/UniXNU/QcomGeniSpi/blob/eac47baefe6a5d2368a70351e6ad1b6361bedbe2/GeniSpi.h), [NvtProtocol.h](https://github.com/UniXNU/ShengNovatekTouch/blob/a1a6f2b1912b3cde2dcbe96439e5833b9ab250f4/NvtProtocol.h#L24) | `nvt_bus`, chip identification, firmware download and frame reads |
| Contact processing | [NvtTouchCore.c](https://github.com/UniXNU/ShengNovatekTouch/blob/a1a6f2b1912b3cde2dcbe96439e5833b9ab250f4/NvtTouchCore.c) | Matrix processing and contact tracking for the supported sensor |
| Board integration | [TouchBoard.h](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/TouchBoard.h), [TouchProbe.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/TouchProbe.cpp) | Power/reset, transport callbacks, interrupt handling and coordinates |
| OS reports | [NativeHidInput.cpp](https://github.com/UniXNU/ShengHidInput/blob/5f3a37cec0c3fc4234b10726b25489a55f0d77ef/NativeHidInput.cpp#L125), [ButtonProbe.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/ButtonProbe.cpp) | `IOHIDDevice`, report descriptors, coherent contact snapshots and button events |

## 1. Select the transport and sensor protocol

Read [QcomGeniSpi](/drivers/qcom-geni-spi),
[ShengNovatekTouch](/drivers/sheng-novatek-touch) and
[ShengHidInput](/drivers/sheng-hid-input). Their responsibilities are:


For a different sensor, implement its identification, firmware and report
protocol. For a different bus controller, implement the transfer/delay callbacks
used by `nvt_bus` when reusing the Novatek protocol.

Implement `nvt_bus.xfer` as one full-duplex transfer with chip select held
throughout. Supply caller-owned buffers and the delay callback from `NvtProtocol.h`.
Call `nvt_identify`, `nvt_fw_parse`, `nvt_download_firmware` and `nvt_read_frame`
in that order, checking each return code. On download failure, preserve stage,
CRC and SRAM-readback diagnostics before retrying. Publish decoded coordinates,
IDs and contact count as one coherent frame for the HID consumer.

## 2. Adapt the board path

1. Define the target's controller windows, bus mode/rate, GPIOs, interrupt and
   SMMU stream from its DTS and clock/pin definitions. `TouchBoard.h` is a board
   data-layout reference.
2. Implement power/reset ownership and verify engine firmware, pins and clocks.
3. Set DMA addressing and cache maintenance for the target SMMU context.
4. Read the chip ID, then load its firmware and check the returned geometry.
5. Decode complete frames and map coordinates to the display's orientation.
6. Check stable contact IDs, simultaneous contacts, edge behavior and release.

The Novatek processing core uses a 40 × 60 matrix. Verify geometry and bounds
when adapting its firmware or processing core. Firmware extraction is owned by
the device's `scripts/gen-touch-firmware.py` and proprietary-file inventory.

The reference probe arguments `sheng-touch=1`, `2`, `3` and `4` select resource inspection, clocks/pins,
controller identification, then firmware/scanning. Use those stages only after
adapting the hardware values consumed by that stage.

**Expected result:** coherent contact frames in display coordinates, including
lift events. The HID layer consumes `native_touch_*` through a sequence counter;
preserve snapshot consistency when replacing the producer.

## 3. Publish HID reports

Qualify IOHIDFamily methods and object layouts against the selected kernelcache.
The reference archive recipe uses a prelinked candidate and ABI records; see
[build inputs](/porting/migration#build-inputs). Adapt the report descriptor,
logical coordinate ranges and contact limits to the sensor.

Select the sensor, transport and HID components in the complete component list.
The reference display recipe links the sensor and bus objects; its HID recipe binds
the OS interface. `sheng-touch-hid=1` enables its touch publication path.
From the assembled target tree, inspect their integration:

```sh
rg -n 'TouchProbe|GeniSpi|NvtProtocol|NvtTouchCore|NvtFirmware' scripts/build-gop-legacy-display.py
rg -n 'native_touch_|ReportDescriptor' drivers/ShengHidInput/NativeHidInput.cpp
```

**Expected result:** the OS receives correct down, move and up reports for each
contact, and UI gestures follow the panel orientation.

## 4. Adapt physical buttons

Use `ButtonProbe.cpp` in the [source map](#source-map) as a reference for
interrupt sampling and HID button events.

Map the target's GPIO or PMIC inputs, polarity, ownership, interrupt routing and
acknowledgement. Access only the PMIC peripherals owned by the selected execution
environment. Adapt `BootResetCore.h` helpers where the SPMI controller differs.
Connect press/release state to the HID consumer report. The reference uses report 2 bits
for Power, Volume Increment and Volume Decrement and enables this with
`sheng-buttons=1`.

**Expected result:** every press and release produces the expected report,
including held and simultaneous buttons, with bounded interrupt activity.

## Next step

Rebuild through [Building](/building), record touch and buttons separately, then
continue with [GPU adaptation](/porting/gpu).

For the arm64e public-source build path and its current linking/runtime limits, see [public-source driver builds](/porting/migration#source-drivers). Historical iOS 17 device results do not qualify this path.
