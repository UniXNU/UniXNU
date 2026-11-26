# ShengBacklight

ShengBacklight connects the two KTZ8866 backlight controllers of the sheng panel to CoreBrightness.

[Source](https://github.com/UniXNU/UniXNU-sheng/blob/main/package/AppleARMBacklight.cpp).

## Status

Device: Xiaomi Pad 6S Pro (sheng).

| OS | State | Features |
| --- | --- | --- |
| iPadOS 17 | Working | Manual brightness, backlight off on sleep |
| iPadOS 27.0.1 (24A446) | Working | Manual brightness |
| iPadOS 27.0.1 (24A446) | Not verified | Backlight off on sleep |

## Hardware

Both controllers sit at I2C address 0x11: one on QUP wrap 1 serial engine 1 (`0xa84000`, SPI 354) and one on the I2C hub engine 2 (`0x988000`, SPI 466). They receive the same 11-bit level, 0 to 2047, in `BL_BRT_LSB` (0x04, bits 2:0) and `BL_BRT_MSB` (0x05).

The engines keep the firmware, clock and SCL timing the boot loader left. Transfers advance on interrupts in the [GENI I2C core](/porting/display#_4-adapt-and-enable-brightness), with a 25 ms deadline per step. A newer level replaces one not yet written.

## Service

`AppleARMPlatform` already defines `AppleARMBacklight`, so the class is `ShengBacklight` and `getMetaClass` answers the `AppleARMBacklight` metaclass. CoreBrightness takes the service for the built-in display's backlight through that answer, and the sandbox applies the profile for that class. `NativeSandboxGrantProcess` lets `backboardd` set the properties the profile refuses.

Published properties:

| Property | Read by | Content |
| --- | --- | --- |
| `backlight-control` | CoreBrightness | `true` |
| `IODisplayParameters.brightness` | iPadOS 17 | `min`, `max`, `value` as levels |
| `IODisplayParameters.BrightnessMilliNits` | `BrightnessControl`, iPadOS 27 | `min`, `max`, `value` in millinits |
| `backlight-marketing-table` | CoreBrightness, iPadOS 27 | Signed 16.16 nits at equally spaced slider positions. Display creation fails without it |
| `LmaxProduct` | `BrightnessControl`, iPadOS 27 | 4 bytes of 16.16 nits. At zero the slider table rescales to infinity and every position means the maximum |
| `LmidProduct`, `LminProduct` | `BrightnessControl`, iPadOS 27 | Numbers in nits |
| `backlight-calibration-parameters` | CoreBrightness, iPadOS 27 | `lMinProduct`, `lMidProduct`, `lMaxProduct`, `lMinPanel`, `lMidPanel`, `lMaxPanel` as 16.16 nits |

Accepted requests:

| Property | Effect |
| --- | --- |
| `brightness-nits` | Signed 16.16 nits. iPadOS maps positive values proportionally to levels of at least 1 and turns the LEDs off at zero or below. macOS uses the response curve below |
| `brightness`, `FadePeriod` | A level and a fade in 16.16 seconds, at most 5 s, stepped every 16 ms |

Other keys, such as `brightness-nits-cap`, succeed with no effect. Requests reach the work loop through a timer, so `backboardd` never waits for a transfer.

The published minimum, midpoint and maximum are 15, 140 and 500 nits. The panel's luminance has not been measured, so these values set the control scale, not an absolute brightness.

## macOS response curve

On macOS, runtime register snapshots on both `KTZ8866A` and `KTZ8866B` confirm `CFG1` (`0x02`) = `0xB3` (`bit 3 = 0`, exponential mapping; `bit 0 = 1`, PWM enabled), `CFG2` (`0x03`) = `0xCD`, and `CurrentReg` (`0x15`) = `0xE9`. Requests between 15 and 500 nits map to hardware levels 892 to 2047 by inverting the KTZ8866 exponential response (`nits(code) = 1.003040572^code`) using a Q24 fixed-point binary-exponentiation table (`milliNitsForLevel`) and integer binary search (`levelForNits`). Requests at or below 15 nits retain level 892 (~3.0% current); requests at or above 500 nits retain level 2047 (100% current). `BrightnessMilliNits.value` uses `milliNitsForLevel` so the published value stays on the physical control scale. Sleep and lid closure still turn the backlight off through their existing path.

`scripts/check-backlight-curve-host.py` in the device repository checks production functions with ASan/UBSan for monotonicity, bounds, roundtrip accuracy, exponential inverse matching, and unchanged iPadOS behavior. Photometer luminance and subjective visual acceptance on hardware remain to be verified by the user.

## Controller diagnostics on macOS

`IODisplayParameters` reports the requested control scale before the I2C write completes. It is not a hardware readback or a luminance measurement. `LastRequestedNitsFixed` records the original signed 16.16 request as 32 bits; `LastRequestWasNits` distinguishes it from a raw level request.

When both engines are idle and the fade has finished, a timer samples the fixed registers 0x02, 0x03, 0x15, 0x04 and 0x05 once per second. `KTZ8866A` and `KTZ8866B` publish separate snapshots with validity, sequence and error state. A new level or a sleep/lid transition invalidates an unfinished snapshot; the current bounded transfer ends before brightness writes resume. Optional diagnostic failures do not prevent service publication.

`ValidMask` bits 0 through 4 correspond to 0x02, 0x03, 0x15, 0x04 and 0x05. A complete sample has `ValidMask=31`, `SnapshotValid=true` and `InProgress=false`. Invalid raw keys are omitted. The snapshots distinguish `SnapshotTarget`, `LastSuccessfulWrite` and `ReadbackLevel`. Use `LastSuccessfulWriteValid` before interpreting the successful-write field, and compare a completed snapshot with its target and sequence. A successful write alone does not prove a later hardware readback.

In register 0x02, bit 3 selects linear mapping when set and exponential mapping when clear; bit 0 enables PWM. Register 0x15 bits 7:3 select full-scale LED current. The driver reads these settings without changing them. Reset defaults do not establish the inherited runtime mode. The `KTZ` boot-log rows describe these controllers; the existing `L path` and `L2` mode fields describe GENI interrupt attachment.

## Brightness control on iPadOS 27

The board sets the ADT property `vmm-present` for AMFI, which makes MobileGestalt answer `IsVirtualDevice`. CoreBrightness then selects `VMBLControl`, which drops every brightness request. Many other frameworks read the same answer, so it stays true.

`scripts/appsync/BacklightMode.m` changes only `backboardd`: `-[BrightnessSystemInternal initBLControl:]` receives mode 1, the mode of a physical device, instead of 3. It loads through the AppSync adapter, which replaces `/usr/libexec/backboardd` with a signed copy.

## Configuration

| Boot argument | Effect |
| --- | --- |
| `backlight=1` | Starts the driver |
| `backlight-control=0` | Leaves out `backlight-control` and the metaclass answer |
| `log-display=1` | Adds the `L` rows to the boot log |

## Verification

1. The system log shows `[UniXNU backlight] physical brightness control selected` and `Set Default 1 BLControl`.
2. The `L` row shows `st=4`, and `xerr` stays 0.
3. Moving the slider raises `req` and changes `lvl` and the panel.
4. Sleep turns the backlight off and wake restores it.
