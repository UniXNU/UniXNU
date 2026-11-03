# Select and add SoC support

A SoC repository supplies hardware descriptions and platform code shared by
boards using the same chip. Follow these steps before completing the
[device repository](/porting/device-repository).

## 1. Identify the hardware and existing support

Record the SoC model and revision, CPU topology, interrupt controller, timers,
IOMMUs and peripheral controllers from the vendor DTS, firmware and source.
Read the [component catalog](/reference/components), then inspect candidate
`UniXNU-<soc>-common` repositories: `README.md`, `AGENTS.md`, `soc.toml`, DTSI,
configuration fragments, patches and platform code.

For each candidate, compare register ranges, interrupt numbers, controller
revisions, firmware interfaces and OS ABI. Check the linked device records for
hardware results. [SM8550](#sm8550) is one available implementation.

**Result:** a matching SoC repository and reviewed commit, or a list of shared
hardware and platform work needed for a new repository.

## 2. Assign configuration to its owner

| Owner | Contents |
| --- | --- |
| ARM64 profile | Common architecture configuration and XNU patches |
| SoC repository | CPU topology, controller resources, shared platform operations and SoC patches |
| Device repository | Enabled CPUs/peripherals, RAM and reservations, wiring, firmware selection, power policy, display and partitions |
| OS profile | XNU/IPSW versions, Apple identity, prelink roots, ABI requirements and version-specific patches |
| Component repository | Drivers and libraries selected by interface, hardware scope and dependencies |

Put reusable controller code in components. The SoC profile selects compatible
implementations; the board supplies their required inputs and records its own
verification. Review the [driver adaptation checklist](/porting/drivers) for each
selected capability.

**Result:** every setting and source file has an owner. Existing support can
proceed to step 4; a new SoC needs the repository in step 3.

## 3. Create shared support for a new SoC

Use the chip's standard identifier in `UniXNU-<soc>-common`. From the parent of
the intended repository, set `SOC` to that identifier and create the directories:

```sh
SOC=mychip
SOC_REPO="UniXNU-$SOC-common"
mkdir -p "$SOC_REPO/configs" "$SOC_REPO/dts" "$SOC_REPO/patches/xnu" "$SOC_REPO/kits"
```

Complete this structure:

```text
UniXNU-<soc>-common/
  AGENTS.md
  README.md
  soc.toml
  configs/<soc>.config
  dts/<soc>.dtsi
  patches/xnu/series
  kits/
```

1. Write `soc.toml` with `schema_version = 2`, `[soc] name`, description and the
   source repository/revision used for hardware data. List reviewed components
   in `[components] include` using canonical catalog IDs.
2. Describe confirmed shared resources in `dts/<soc>.dtsi`. Follow the
   [device-tree procedure](/porting/device-tree#procedure) for bindings, address
   translation, interrupts and references. The board DTS includes this file and
   supplies the board's memory and peripheral configuration.
3. Add shared kernel settings to `configs/<soc>.config`. Put ordered SoC patches
   in `patches/xnu/series`; an empty series is valid when none are needed.
4. Put shared platform operations in `kits/` and connect their sources or archives
   through the [build configuration](/reference/configuration). Review every
   hardware address and firmware operation against this SoC's sources.
5. Write a concise README with scope, inputs, build commands and verified devices.
   Root `AGENTS.md` lists responsibilities and required reading. Link detailed
   instructions to this documentation site.
6. Publish the repository and select a reviewed commit for the device's feed.

**Result:** a versioned SoC profile whose hardware values have identified sources.

## 4. Select the profile from a device

In the device's `feeds.toml`, add a pinned source. Replace the example name, URL
and commit with the selected repository:

```toml
[[source]]
name = "mychip"
kind = "soc"
git = "https://github.com/<owner>/UniXNU-mychip-common"
commit = "<reviewed 40-character commit>"
```

In the existing `board.toml` tables, set:

```toml
[board]
soc = "mychip"
soc_source = "mychip"
os_profile = "<selected OS profile>"

[device_tree]
source = "device:dts/board.dts"
include_dirs = ["soc:dts"]
```

Set the board DTS include to the selected `<soc>.dtsi`. Update
`[kernel] config_fragments` to include `soc:configs/<soc>.config` and
`patch_series` to include `soc:patches/xnu/series` in the intended order.
Keep the complete ARM64, SoC, OS and device lists: tables merge by key, while
ordinary arrays replace earlier arrays. The same rule applies to component
selections and archive lists.

**Result:** the board names a pinned SoC source, matching DTSI and configuration
fragments. Follow [OS profile and patch requirements](/xnu/source-and-patches)
when selecting or creating the OS profile.

## 5. Resolve and verify the combination

From the main UniXNU checkout:

```sh
./unixnu defconfig <device>_defconfig -D ../UniXNU-<device>
./unixnu fetch
./unixnu status --json
./unixnu tree
```

Check the SoC revision, selected profiles, components, overrides and patch order
in `status`. Inspect the assembled tree, then follow [device-tree compilation](/porting/device-tree#procedure),
[driver adaptation](/porting/drivers) and [building](/building).
Record each board's [bring-up checkpoints](/porting/bring-up) and
[log evidence](/porting/log-capture) separately from build results.

**Result:** resolved sources, a compiled hardware description and a board-specific
verification record. Continue with [Port a device](/porting/steps).

## SM8550 example {#sm8550}

[`UniXNU-sm8550-common`](https://github.com/UniXNU/UniXNU-sm8550-common)
provides `soc.toml`, `configs/sm8550.config`, `dts/sm8550.dtsi`, platform
operations and XNU patch series. Read those files and its root `AGENTS.md` before
selecting it. Pin the repository in the device's feed and include its DTSI.

Adreno740 and AdrenoMetal cover A740/SM8550 interfaces. Each board supplies
firmware, power, reserved-memory and display inputs. The [reference device record](/devices/sheng)
contains its GPU hardware results; its device profile also selects its UFS,
touch and HID implementations. Check those components' board dependencies when
reusing them. Use the [migration guide](/porting/migration) for an existing port.
