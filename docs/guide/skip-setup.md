# Skip Setup

Requires macOS image tools, a matching packed Data seed and the board's `skip_setup_tool`. Prepare them through [Building](/building). After the payload command below, run `./unixnu bootimg` and boot the newly packed image.

A fresh Data seed starts the Setup app on first boot. The payload can mark Setup as done before the image is written, so the device boots to SpringBoard.

## Procedure {#procedure}

1. Prepare a matching Data seed, macOS image tools and the device's `skip_setup_tool`. Check the [build version](#build-version) and [ADT identity](#device-tree) against the selected IPSW.
2. If the seed needs resizing, complete [Data-volume preparation](/guide/userdata#data-volume) first. Record the chosen seed path.
3. Run the [payload command](#command) with `--skip-setup` and the required device inputs. Check [output](#output): `payload.json` must contain `"skip_setup": true`.
4. Run `./unixnu bootimg`, boot the new image and perform [verification](#verify). Record the seed, image revision and observed userland stage.

## Command

```sh
./unixnu build payload \
  --data-ramdisk data.dbr \
  --skip-setup \
  --trust-cache trustcache.img \
  --unique-chip-id <hex>
```

`--skip-setup` requires `--data-ramdisk`. The payload step reads `[payload] skip_setup_tool` from the board file and runs it on a copy of the seed.

```toml
[payload]
skip_setup_tool = "scripts/seed-data-skip-setup.py"
skip_setup_args = ["--no-auto-dim"]
```

`skip_setup_args` is optional and passed to the tool after the two paths. The original seed stays unchanged. The payload uses the edited copy as `Payloads/scratch-data.img`.

Grow the seed first with `scripts/seed-data-grow.py` when the tablet's storage is larger than the seed. The payload edits the grown seed and keeps its size.

## What the tool changes

`scripts/seed-data-skip-setup.py` expands the packed APFS Data seed, attaches it read-write, merges preferences into `/private/var/mobile/Library/Preferences`, and packs the result again.

| Preference file | Values |
| --- | --- |
| `com.apple.purplebuddy` | `SetupDone = true`, `SetupFinishedAllSteps = true`, `SetupVersion = 11`, `daemonizeNeedsToRun = false` |
| `com.apple.purplebuddy.notbackedup` | Every mini-buddy flag is `false`: diagnostics, HSA2, keychain sync, Mesa, payment, standard, silent ICDP |
| `com.apple.managedconfiguration.notbackedup` | `LockdownActivationIndicatesCloudConfigurationAvailable = false` |
| `com.apple.springboard` | `BKNoWatchdogs = true`, `FBLaunchWatchdogExceptions = { com.apple.purplebuddy: 100 }`, `MCForceShowCloudConfigurationUI = false` |
| `com.apple.migration` | `LastSystemVersion = 21H461`, `DMUserDataDisposition = { SyntheticDidUpgrade = false, buildVersion = 21H461 }` |

`--no-auto-dim` also sets `SBDisableAutoDim`, `SBDontDimOrLockOnAC` and `SBDisableIdleSleep` in `com.apple.springboard`, as UniXNU-qemu's root builder does. A board without buttons or a working idle timer otherwise turns its display off about 30 seconds after SpringBoard starts and puts the system to sleep.

The tool also creates these directories under `/private/var/containers`:

```
Bundle
Data/System
Shared/SystemGroup
Temp
```

The volume UUID stays the same. The APFS container magic is checked again after the edit.

## Build version

The script sets:

```python
BUILD, VERSION = '21H461', '17.7.11'
```

Update both values when the board targets a different iOS build. `LastSystemVersion` and `DMUserDataDisposition.buildVersion` must match the IPSW.

## Device tree

The supplied format 2 OS profile sets these typed `/chosen` properties. Format 1 ADT tools select them through `--ipad-identity`:

| Property | Value |
| --- | --- |
| `certificate-production-status` | `0` |
| `effective-production-status-ap` | `0` |
| `certificate-security-mode` | `1` |
| `effective-security-mode-sep` | `1` |

These describe a development-fused, undemoted board. `mobileactivationd` reads them through MobileGestalt and takes its native activation path without an activation record. The other identity properties and their cached answers are in [MobileGestalt identity](/guide/mobilegestalt).

## Jobs

Setup depends on services that do not run on this platform. The board disables them with boot arguments:

```
sheng-disable-jobs=com.apple.identityservicesd,com.apple.locationd,com.apple.CommCenter,com.apple.iconservices.iconservicesagent
```

`com.apple.CommCenter` is the cellular service. The list is board specific. Keep the services the userland needs and remove the ones that block the first boot.

## Output

The payload directory contains:

```
out/<device>/<os_profile>/<config>/payload/data-skip-setup-<hash>.dbr
out/<device>/<os_profile>/<config>/payload/payload.img
out/<device>/<os_profile>/<config>/payload/payload.json
```

`payload.json` records:

| Field | Meaning |
| --- | --- |
| `data_ramdisk_sha256` | Hash of the edited seed |
| `skip_setup` | `true` |
| `payload_sha256` | Payload image hash |

The edited seed is cached by the hash of the original and of `skip_setup_args`. A different seed or different arguments produce a new file.

## Verify

1. Build the payload with `--skip-setup`.
2. Check `payload.json` has `"skip_setup": true`.
3. Run `./unixnu bootimg`, then boot the newly packed image.
4. The log reaches SpringBoard instead of the Setup pages.

The reference implementation is `scripts/seed-data-skip-setup.py` in this repository.

## Next steps

- [Boot the image](/guide/boot)
- [Userdata image](/guide/userdata)
- [Payload](/concepts/payload)
