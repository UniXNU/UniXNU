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
| `brightness-nits` | Signed 16.16 nits. Zero or less turns the LEDs off; other values map proportionally to a level of at least 1 |
| `brightness`, `FadePeriod` | A level and a fade in 16.16 seconds, at most 5 s, stepped every 16 ms |

Other keys, such as `brightness-nits-cap`, succeed with no effect. Requests reach the work loop through a timer, so `backboardd` never waits for a transfer.

The range is 2, 140 and 500 nits. The panel's luminance has not been measured, so these values set the slider's scale, not an absolute brightness.

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
