# Brightness interface

This page lists what the OS expects from the backlight service that
[display adaptation](/porting/display#_4-adapt-and-enable-brightness) builds.
The values are those of the sheng service in `AppleARMBacklight.cpp`.

## Service identity

`AppleARMPlatform` already defines `AppleARMBacklight`, so the board class has
its own name and its `getMetaClass` answers the `AppleARMBacklight` metaclass.
CoreBrightness takes the service for the built-in display's backlight through
that answer, and the sandbox applies the profile of that class.

## Published properties

| Property | Read by | Content |
| --- | --- | --- |
| `backlight-control` | CoreBrightness | `true` |
| `IODisplayParameters.brightness` | iPadOS 17 | `min`, `max`, `value` as levels |
| `IODisplayParameters.BrightnessMilliNits` | iPadOS 27 | `min`, `max`, `value` in millinits |
| `backlight-marketing-table` | iPadOS 27 | Signed 16.16 nits at equally spaced slider positions. Display creation fails without it |
| `LmaxProduct` | iPadOS 27 | 4 bytes of 16.16 nits. At zero every slider position means the maximum |
| `LmidProduct`, `LminProduct` | iPadOS 27 | Numbers in nits |
| `backlight-calibration-parameters` | iPadOS 27 | `lMinProduct`, `lMidProduct`, `lMaxProduct`, `lMinPanel`, `lMidPanel`, `lMaxPanel` as 16.16 nits |

## Accepted requests

| Property | Effect |
| --- | --- |
| `brightness-nits` | Signed 16.16 nits. Zero or less turns the LEDs off; other values map proportionally to a level of at least 1 |
| `brightness`, `FadePeriod` | A level and a fade in 16.16 seconds, at most 5 s, stepped every 16 ms |

Other keys succeed with no effect. Requests reach the work loop through a
timer, so the caller never waits for a transfer.

## Virtual platform on iPadOS 27

A board that sets the ADT property `vmm-present` makes MobileGestalt answer
`IsVirtualDevice`. CoreBrightness then selects a control that drops every
brightness request. `scripts/appsync/BacklightMode.m` gives `backboardd` the
mode of a physical device. It loads through the
[AppSync adapter](/concepts/security#user-application-installation).

## Boot arguments

| Argument | Effect |
| --- | --- |
| `backlight=1` | Starts the service |
| `backlight-control=0` | Leaves out `backlight-control` and the metaclass answer |
| `log-display=1` | Adds the `L` rows to the boot log |

## Verification

1. The system log shows `[UniXNU backlight] physical brightness control selected`.
2. The `L` row shows `st=4`, and `xerr` stays 0.
3. Moving the slider raises `req` and changes `lvl` and the panel.
4. Sleep turns the backlight off and wake restores it.

Record the result in the display area, then continue with [input](/porting/input).
