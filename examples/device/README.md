# Device template

Follow [Port a device](https://unixnu.com/porting/) from input collection through publication. Complete the [driver adaptation checklist](https://unixnu.com/porting/drivers) before selecting board-dependent components.

This template selects shared SM8550 and iPadOS 17.7.11 support. Complete the
hardware inputs before building.

1. Copy this directory to `UniXNU-<device>` and read `AGENTS.md`.
2. Set the board name, description, firmware paths, and complete component selection. Add the shared `UniXNURamDiskDxe` and filesystem dependencies to the firmware DSC and FDF using the [firmware integration guide](https://unixnu.com/porting/uefi-firmware#required-integration).
3. Pin a reviewed SoC commit in `feeds.toml`.
4. Rename `configs/example_defconfig` and `dts/board.dts` for the board, then update `kernel.defconfig` and `device_tree.source`. Fill the DTS model, compatible values, memory map, CPU selection, and peripherals.
5. Pin the official firmware archive in `board.toml` `[firmware.image]` and list the extracted inputs and hashes in `proprietary-files.txt`; extracted firmware lives in no repository.
6. Set partition geometry and payload inputs from the device's records.
7. Match the identity in `porting.toml` to `board.toml`. Cover every selected component and dependency, with board-specific ownership paths, findings and completion criteria.
8. Enable the template CI workflows and require the `Porting record` check on the official device branch.
9. Set `example = false`, then run `scripts/package.sh --check --os <profile>` and fix what it reports. Commit the generated `unixnu.lock`; keep local overrides in the ignored `local.toml`.
10. Complete the shared [repository checklist](https://unixnu.com/porting/device-repository#completion), build and record results, then follow [publication](https://unixnu.com/porting/device-repository#publish). Add the **`unixnu` GitHub topic** and verify it appears in the repository topics.

The zero memory range and `REQUIRED_` values identify inputs to complete.
`patches/xnu/series` lists board patches in application order. `package/` contains
board packaging. Shared resources come from the selected SoC and component sources.

- [Device repository](https://unixnu.com/porting/device-repository)
- [Device tree](https://unixnu.com/porting/device-tree)
- [Component catalog](https://unixnu.com/reference/components)
- [Migration](https://unixnu.com/porting/migration)

`porting.toml` is the shared maintainer and agent record. Publish it with
`board.toml` and the `unixnu` topic. The central catalog workflow pins the
source and generates both language editions twice daily. Put board driver
submodules in this device repository. See the [record guide](https://unixnu.com/porting/records)
and [UFS guide](https://unixnu.com/porting/ufs).

```sh
python3 scripts/porting-record.py check --device ../UniXNU-example
```

Run this command from UniXNU.

## Local builds and boot diagnosis

Copy `unixnu.example.toml` to `unixnu.local.toml` in the main checkout and fill
in device inputs using the [configuration reference](https://unixnu.com/reference/configuration#local-build-inputs).
Read [boot arguments](https://unixnu.com/xnu/boot-arguments#apply-arguments)
before changing the command line. Rebuild the payload and boot image after
argument changes. Use the [green-bar diagnosis](https://unixnu.com/guide/debugging#green-bar)
for stalls at loader handoff. Record the last confirmed stage and relevant logs.
