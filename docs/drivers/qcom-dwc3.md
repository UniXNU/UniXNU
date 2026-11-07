# QcomDwc3

QcomDwc3 runs Apple's USB device and host stacks on a Qualcomm DWC3 controller.

[Source repository](https://github.com/UniXNU/QcomDwc3).

## Status

Device: Xiaomi Pad 6S Pro (sheng), iPadOS 27.0.1 (24A446).

| State | Features |
| --- | --- |
| Working | Enumeration at 10 Gbps on a USB 3 cable and 480 Mbps on a USB 2 cable, re-enumeration, Trust dialog, pairing with a Mac, lockdown sessions and service start |
| Partial | Host mode: Apple's xHCI stack runs and completes commands; enumerating a peripheral is not verified |
| Not tested | Sustained transfers, app installation, the reverse cable orientation on USB 3 |

`fairplayd.A2` and `adid` stay disabled. With both enabled, SpringBoard does not finish starting.

## Layers

`QcomDwc3Xdci` derives from `AppleUSBXDCI` and `QcomDwc3Xhci` from `AppleUSBXHCI`. Each supplies the register window, interrupt, power and PHYs. `IOUSBDeviceFamily`, `AppleUSBDeviceMux`, `IOUSBHostFamily`, `USBDeviceConfiguration` and `lockdownd` run unchanged.

UCSI over the charger's GLINK channel reports the cable partner: a host selects device mode and a peripheral selects host mode. Until UCSI answers, the charger's online value stands in for a host. One role runs at a time, with a core soft reset between roles.

## Board integration

The board supplies the eUSB2 repeater, QMP PHY, retimer, rails and SMMU context. On sheng, `sheng-usb=1` starts the driver. The eUSB2 reference is 38.4 MHz. Stream 0x40 uses its own stage 1 context with write-back inner shareable blocks, because `AppleUSBXDCI` does no cache maintenance.

`AppleUSBXDCI` has no personality, so the driver loads the kext before registering its subclass. The prelink roots add the device and host stacks and leave out `AppleOnboardSerial` and `AppleSMC`, which the host stack only names in a metaclass comparison.

## Configuration

| Boot argument | Effect |
| --- | --- |
| `sheng-usb=1` | Runs the driver |
| `sheng-usb=2` | Adds register sampling |
| `sheng-usb=3` | Also takes the controller off the bus and back once |
| `sheng-usb-host=<s>` | Forces host mode after a delay |
| `sheng-usb-back=<s>` | Returns to the cable's role after that |
| `log-sys=1` | Adds the `[usb]` rows of `native_usb_stats` to the boot log |

## Adapting to another board

The full procedure is in [USB adaptation](/porting/usb).

1. Supply the repeater, PHY, retimer and rail sequences, and the eUSB2 reference rate. With a wrong rate chirp passes and high-speed data fails.
2. Give the controller's stream a coherent stage 1 context.
3. Provide `qcom_dwc3_vbus()` and the UCSI channel.
4. Add the USB stacks to the OS profile's prelink roots.
5. After a kernelcache change, regenerate the class layouts with `scripts/gen-usb27-abi.py` and `scripts/gen-usb27-host-abi.py`.

Keep these two overrides when the layouts change:

- Slot 179 of `AppleUSBXDCI` stays false without an `IOPort` transport object. True leaves `bNumConfigurations` at 0.
- In host mode the xHCI subclass answers on for the family's desired power, and the device stack answers 0.

## Pairing with a Mac

A Mac and `lockdownd` need these system answers:

| Answer | Source | Effect |
| --- | --- | --- |
| `chip-id`, `board-id`, `security-domain` in `/chosen` | Board and OS profile | MobileDevice finds the model in its device map and needs no software update |
| One file system number for `/System` and system daemons | [`native-union-statfs-fsid`](/xnu/patch-reference) | SpringBoard accepts the daemon's `CFUserNotification` and shows Trust |
| Lock state 3, no passcode | [`sheng-aks-sls=3`](/drivers/apple-key-store-state) | `lockdownd` completes Trust without asking for a passcode |

## Verification

1. Boot and connect the tablet to a Mac.
2. Unlock the tablet and tap Trust.
3. The Mac reports the device as paired and lockdown sessions start.
