# Novatek NT36532E touch driver

Start with the [adaptation procedure](/porting/input) for board inputs, source changes, build integration and verification order.

ShengNovatekTouch is an independent UniXNU module, included by UniXNU-sheng. It is a complete touch driver for the Novatek NT36532E controller and a worked example for new touch drivers.

| Repository | Path | Contents |
| --- | --- | --- |
| [ShengNovatekTouch](https://github.com/UniXNU/ShengNovatekTouch) | `NvtTouchCore.c` | Pure touch processing |
| ShengNovatekTouch | `NvtProtocol.c` | Controller protocol |
| ShengNovatekTouch | `NvtProtocol.h` | Protocol constants and bus interface |
| [QcomGeniSpi](https://github.com/UniXNU/QcomGeniSpi) | `GeniSpi.c` | GENI SPI engine |
| [UniXNU-sheng](https://github.com/UniXNU/UniXNU-sheng) | `package/TouchBoard.h` | Board constants and clock helpers |
| UniXNU-sheng | `package/TouchProbe.cpp` | Kernel probe and frame loop |
| UniXNU-sheng | `package/TouchBoardTests.c` | Host tests for the board helpers |
| [ShengHidInput](https://github.com/UniXNU/ShengHidInput) | `NativeHidInput.cpp` | HID digitizer source |

## Two layers

The driver separates pure logic from hardware access.

```
NvtTouchCore.c      matrix to contacts, no allocation, no I/O
NvtProtocol.c       chip identification, firmware, frames, through nvt_bus
TouchProbe.cpp      MMIO, clocks, pins, DMA, SMMU, threads
NativeHidInput.cpp  contacts to HID reports
```

The pure core and the protocol take a `struct nvt_bus`:

```c
struct nvt_bus {
  void *ctx;
  int (*xfer)(void *ctx, const uint8_t *tx, uint8_t *rx, size_t len);
  void (*delay)(void *ctx, unsigned ms);
};
```

The host tests supply a fake bus. The kernel probe supplies the GENI SPI transfer.

## Touch processing

`NvtTouchCore.c` processes a 40 by 60 matrix of 16-bit values:

1. Collect 72 startup frames.
2. Form a per-node reference from the median of the startup frames.
3. Subtract the reference to get a delta matrix.
4. Label nodes above the noise floor by steepest ascent.
5. Find local maxima and form blobs.
6. Reject blobs above the palm node count.
7. Compute a weighted centroid per blob.
8. Apply edge compensation.
9. Track contacts across frames with a radius and a down/up threshold.
10. Report contacts from the second frame of a slot.

The core has no allocation. Its scratch arrays live in `struct nvt_touch_core`, which the probe allocates once. The comments record why: kernel thread stacks are 16 KiB and the scratch is larger.

## Controller protocol

`NvtProtocol.c` provides:

| Function | Purpose |
| --- | --- |
| `nvt_identify` | Read the chip id and select the map |
| `nvt_fw_parse` | Parse the firmware image into ILM and DLM parts |
| `nvt_download_firmware` | Reset the bootloader, write the parts, verify the SRAM |
| `nvt_start_scanning` | Read the firmware version and matrix geometry |
| `nvt_peek_frame_header` | Read the 32-byte THP header |
| `nvt_read_frame` | Read a complete THP frame |
| `nvt_frame_header_valid` | Reject a torn frame |
| `nvt_frame_matrix` | Decode the matrix |

The transfer length, read maximum and frame length are constants from the vendor protocol.

## Board constants

`TouchBoard.h` holds every address and bit with a source comment:

| Group | Examples |
| --- | --- |
| QUP wrapper and serial engine | Base addresses and sizes |
| SMMU | Stream ID and apps SMMU base |
| GCC | Vote registers, halt registers, DFS levels |
| TLMM | GPIO numbers, function, drive strength |
| SPI | Mode and maximum frequency |

The clock helpers are pure functions. `tb_choose_clock` selects the DFS level and divider that give the highest rate not above the target. The host tests cover the divider arithmetic.

## Probe stages

The probe is off by default. The boot argument `sheng-touch=<n>` selects a stage:

| Stage | Work |
| --- | --- |
| 1 | Read GCC branches, DFS levels, pins and the serial engine identity |
| 2 | Vote and wait for the QUP clocks, configure the pins |
| 3 | Initialize GENI SPI, select the clock, identify the chip |
| 4 | Download the firmware, start scanning, process frames |

Each stage reports on the diagnostic page. The first failure stops the sequence.

## Hardware path

1. Vote for GPLL0 and the QUP branches in GCC.
2. Wait for the branch clocks to leave the off state.
3. Configure the SPI pins in TLMM.
4. Map the QUP wrapper and the serial engine.
5. Initialize GENI SPI.
6. Select the DFS level and divider.
7. Allocate a physically contiguous DMA buffer.
8. Map the buffer through the apps SMMU with a bypass stream.
9. Maintain the cache around each transfer.
10. Reset the touch bootloader and download the firmware.
11. Poll the THP header, read complete frames and publish contacts.

The SMMU mapping follows the same bypass model as the UFS driver. The DMA buffer is cached, and the driver performs explicit clean and invalidate operations around each transfer.

## HID publication

The probe publishes contacts through globals:

```c
volatile uint32_t native_touch_seq;
volatile uint32_t native_touch_count;
volatile int native_touch_xs[NVT_SLOTS];
volatile int native_touch_ys[NVT_SLOTS];
volatile int native_touch_ids[NVT_SLOTS];
```

The writer increments the sequence before and after the update, so the reader detects a torn snapshot. `ShengHidInput` reads the snapshot and emits digitizer reports.

## Adapting the example

1. Keep the pure processing layer separate from the bus.
2. Put every board constant in a header with its source.
3. Run the existing host checks for the reused processing and clock helpers.
4. Add a staged boot argument so each hardware step is observable.
5. Publish contacts through a sequence counter and a fixed size snapshot.
6. Keep the driver off by default until a boot log shows each stage.

## Next steps

- [XNU drivers](/drivers/xnu-drivers)
- [Device tree matching](/drivers/device-tree-matching)
- [Reference device record](/devices/sheng)
