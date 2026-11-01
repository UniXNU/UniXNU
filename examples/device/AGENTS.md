# Device agent guide

This repository owns the board DTS, peripheral wiring, component selections,
firmware inputs, partition layout, and packaging.

## Read first

Read this README and the following UniXNU documentation before changing the port:

| Task | Required reading |
| --- | --- |
| Every port | [Porting](https://unixnu.com/porting/), [device repository](https://unixnu.com/porting/device-repository), [component catalog](https://unixnu.com/reference/components), UniXNU `components.toml` |
| Hardware | [Device tree](https://unixnu.com/porting/device-tree), [matching](https://unixnu.com/drivers/device-tree-matching), selected SoC README, AGENTS, soc.toml and DTSI |
| Component | Its site page, README, catalog build command, dependencies and source |
| Kernel | [Source and patches](https://unixnu.com/xnu/source-and-patches), [patch reference](https://unixnu.com/xnu/patch-reference), selected OS profile |
| Images | [Prelink](https://unixnu.com/concepts/prelink), [payload](https://unixnu.com/concepts/payload), [UEFI](https://unixnu.com/porting/uefi-firmware) |
| Verification | [Building](https://unixnu.com/building), [bring-up](https://unixnu.com/porting/bring-up) |
| Migration | [Migration](https://unixnu.com/porting/migration) |

## Work

Search the catalog and inspect existing component interfaces before adding code.
Match hardware scope, OS ABI, and board dependencies. Shared SoC resources and
operations belong in the selected SoC repository. Reusable drivers and libraries
belong in their component repositories. Use canonical component IDs and preserve
runtime identifiers recorded in the catalog.

Replace every `REQUIRED_` value, set the board name and firmware paths, and select
the complete dependency set. Verify memory ranges, CPU affinities, interrupts,
firmware hashes, and partition geometry from board evidence. Set `example = false`
after completing the inputs. Pin the SoC commit and inspect resolved profiles.

Build with the packaging script from the device repository; every value it needs
comes from board.toml ([package], [os_overrides], the sections the steps read):

```sh
scripts/package.sh --check --os <profile>              # deps, preflight, patches; stops before building
scripts/package.sh --os <profile> --uefi ../uefi-example
```

The platform seed (`UNIXNU_UNIQUE_CHIP_ID`) and the firmware checkout are not in
any repository. `.github/workflows/package.yml` runs the same script on a macOS
runner: run it in a fork, set the seed as the fork's secret, download the images,
then delete the run.

For a Mu-Silicium initrd payload, include `UniXNURamDiskDxe`, DiskIoDxe and
FAT support in the firmware DSC and FDF. Follow
[required firmware integration](https://unixnu.com/porting/uefi-firmware#required-integration)
before building the firmware and boot image.

Record commands, revisions, output paths, results, and unresolved inputs.
Report hardware boot, storage, display, input, and GPU results separately.
Finish both new ports and migrations with the same
[repository checklist](https://unixnu.com/porting/device-repository#completion).
Follow [publication](https://unixnu.com/porting/device-repository#publish), add
the `unixnu` GitHub topic, and update the device revision in UniXNU's
`devices.toml`. Keep this README concise.

## Porting record

Read the device's `porting.toml` and the
[record guide](https://unixnu.com/porting/records) before implementation.
For storage, also read the [UFS guide](https://unixnu.com/porting/ufs).
Update each affected area's findings or evidence with its code change.
The documentation site renders this same record. Follow its schema and
completion levels for both maintainer and agent work.

## Local builds and boot diagnosis

Copy `unixnu.example.toml` to `unixnu.local.toml` in the main checkout and fill
in device inputs using the [configuration reference](https://unixnu.com/reference/configuration#local-build-inputs).
Read [boot arguments](https://unixnu.com/xnu/boot-arguments#apply-arguments)
before changing the command line. Rebuild the payload and boot image after
argument changes. Use the [green-bar diagnosis](https://unixnu.com/guide/debugging#green-bar)
for stalls at loader handoff. Record the last confirmed stage and relevant logs.

## Hardware adaptation

Follow [Port a device](https://unixnu.com/porting/) in order. Read the
[driver adaptation checklist](https://unixnu.com/porting/drivers) before selecting
components. Follow each subsystem guide for board inputs, implementation paths,
archive integration and expected results. Include board-package services such as
brightness, buttons, Wi-Fi, DSP, battery and CPU frequency in the porting record.
