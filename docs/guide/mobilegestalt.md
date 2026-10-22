# MobileGestalt identity

MobileGestalt answers device queries from the Apple device tree (ADT). The payload writes the ADT at build time, so identity changes leave the signed kernel and the userland image untouched.

## Properties

| Property | Node | Example | Effect |
| --- | --- | --- | --- |
| `model` | root | `iPad7,1` | `hw.product` and `hw.machine`; selects the device class by prefix |
| `target-type` | root | `J120` | `hw.target`; hardware model string |
| `product-name` | `/product` | `iPad Pro (12.9-inch) (2nd generation)` | product name reported by the platform expert |
| `product-description` | `/product` | `iPad Pro (12.9-inch) (2nd generation)` | product description |
| `artwork-device-idiom` | `/product` | `pad` | interface family; use `phone` for an iPhone |
| `artwork-device-subtype` | `/product` | `2732` | artwork geometry |
| `artwork-scale-factor` | `/product` | `2` | artwork scale |
| `artwork-display-gamut` | `/product` | `P3` | display gamut |
| `compatible-device-fallback` | `/product` | `iPad6,7` | fallback device |
| `thin-bezel` | `/product` | `1` | bezel class |
| `button-names` | `/buttons` | `hold`, `voldown`, `volup` | available buttons; omit `menu` without a Home button |
| `home-button-type` | `/buttons` | `2` | no mechanical Home button, swipe gestures |
| `certificate-production-status` | `/chosen` | `0` | activation security status |
| `effective-production-status-ap` | `/chosen` | `0` | activation security status |
| `certificate-security-mode` | `/chosen` | `1` | activation security mode |
| `effective-security-mode-sep` | `/chosen` | `1` | activation security mode |
| `display-scale` | `/chosen` | `2` | scale read by MobileGestalt |

`DeviceClass` compares `hw.product` by prefix with `iPhone`, `iPod`, `iPad`, `AppleTV`, `Watch` and other families. A name outside those prefixes falls back to `iPod`. The root `model` property supplies `hw.product`, so set it together with the `/product` values.

## Full-screen gestures

Use a device without a Home button:

- root `model` and `target-type` from a home-button-less device
- `/buttons` without a `menu` entry
- `home-button-type = 2`

SpringBoard reads the value through `BSPlatform homeButtonType`. With value 2 the lock screen uses the swipe-up gesture. On sheng, a swipe up from the lock screen reaches the passcode view and the passcode view names the device as an iPad.

## iPadOS and iOS

The ADT identity and the userland image belong to the same device family. Use a pad identity with an iPadOS root and a phone identity with an iOS root.

| Target | `model` | `target-type` | `product-name` | `artwork-device-idiom` |
| --- | --- | --- | --- | --- |
| iPadOS | `iPad7,1` | `J120` | `iPad Pro (12.9-inch) (2nd generation)` | `pad` |
| iOS | `iPhone10,3` | `D22` | `iPhone X` | `phone` |

The restore images are listed in [Requirements](/guide/requirements#target-ipsw).

On a UniXNU board, `[payload.adt] ipad_identity = true` passes `--ipad-identity` to the board ADT tool, and the tool writes the iPad identity. For an iPhone target, write the phone values in the ADT tool or add a board option that selects them.

The identity describes the hardware to the userland. The installed system still comes from the IPSW, so an iPadOS root stays iPadOS and an iOS root stays iOS.

Leave the root `compatible` strings as the board's own. An Apple board name can match original platform kexts and select a path the port does not implement.

## Apply

1. Edit the board ADT tool or set `ipad_identity`.
2. Rebuild the payload.
3. Clear the cached answers.
4. Boot and check the device name, lock hint, swipe up and keyboard layout.

A Python ADT tool can write the nodes directly:

```python
node('buttons', [
    ('compatible', b'buttons\0'),
    ('device_type', b'buttons\0'),
    ('button-names', b'hold\0voldown\0volup\0'),
    ('home-button-type', struct.pack('<I', 2)),
])
node('product', [
    ('product-name', b'iPad Pro (12.9-inch) (2nd generation)\0'),
    ('product-description', b'iPad Pro (12.9-inch) (2nd generation)\0'),
    ('artwork-device-idiom', b'pad\0'),
    ('artwork-device-subtype', struct.pack('<I', 2732)),
    ('artwork-scale-factor', struct.pack('<I', 2)),
    ('artwork-display-gamut', b'P3\0'),
    ('compatible-device-fallback', b'iPad6,7\0'),
    ('thin-bezel', struct.pack('<I', 1)),
])
```

## Cached answers

MobileGestalt writes answers to `/private/var/containers/Shared/SystemGroup/systemgroup.com.apple.mobilegestaltcache/Library/Caches/com.apple.MobileGestalt.plist`. The cache is keyed by build and platform UUID, so a changed identity can keep the old class and Home button answers. Delete the file or rebuild the Data volume after an identity change. The preference files `/var/mobile/Library/Preferences/com.apple.MobileGestalt.plist` and `com.apple.mobilegestalt.plist` carry the same domain.

## Next steps

- [Device tree](/porting/device-tree)
- [Payload](/concepts/payload)
- [Skip Setup](/guide/skip-setup)
