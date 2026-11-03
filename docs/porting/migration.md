# Migrate a device port

## Why migrate

Format 2 lets devices reuse SoC support, OS profiles and component build recipes.
A shared SoC repository holds controller resources and platform operations;
each device repository supplies its wiring, firmware selections and board policy.
This keeps common fixes in one place and makes the inputs for another device
explicit. The component catalog identifies each implementation's hardware and
ABI requirements. Separate output directories keep each device, OS profile and
configuration's patched kernel and generated files together.

Follow this guide to convert an existing device repository to format 2. The
result is a pinned SoC source, a board DTS, a complete component selection and
repeatable kernel, firmware and payload commands. A new port starts with
[Port a device](/porting/steps). An existing format 2 port can use the checks below
to review its configuration. Both workflows finish with the same
[repository requirements and publication steps](/porting/device-repository#completion),
including the `unixnu` GitHub topic.

## Before you start

Read the root `AGENTS.md` in the repositories you will edit, the
[repository specification](/porting/device-repository), and the
[component catalog](/reference/components). Prepare the
[host tools](/guide/requirements). Run commands from the main UniXNU checkout
in the same shell. Replace these values with your existing device and defconfig:

```sh
DEVICE=myboard
DEVICE_DIR="../UniXNU-$DEVICE"
DEFCONFIG="${DEVICE}_defconfig"
MIGRATION_DIR="$PWD/out/migration-$DEVICE"
mkdir -p "$MIGRATION_DIR"
```

`examples/device/` supplies individual file examples. Edit the existing port
in place, preserving its hardware values, patches, scripts and source pins.

## 1. Record the current configuration

```sh
git -C "$DEVICE_DIR" status --short
git -C "$DEVICE_DIR" submodule status --recursive
python3 - "$DEVICE_DIR/board.toml" <<'PYCODE'
import pathlib, sys, tomllib
board = tomllib.loads(pathlib.Path(sys.argv[1]).read_text())
print("schema_version:", board.get("schema_version", 1))
print("defconfig:", board.get("kernel", {}).get("defconfig"))
PYCODE
./unixnu status --json -D "$DEVICE_DIR" > "$MIGRATION_DIR/before.json"
cp "$DEVICE_DIR/board.toml" "$MIGRATION_DIR/board-before.toml"
```

A missing `schema_version` selects format 1. Record local edits and untracked
files, and save the intended source changes in your working branch before
moving files. If `status` fails, resolve its missing source or configuration
first so the report captures the starting configuration.

Inventory `.gitmodules`, `feeds.toml`, `local.toml`, `unixnu.lock`, build scripts,
CI, firmware DSC/FDF files and documentation. For each component, record its
origin URL, checked-out commit, local changes, consumers and build outputs:

```sh
rg -n 'Native|drivers/|kits/|archives|patches|make-.*-adt' "$DEVICE_DIR"
git -C <component-checkout> remote get-url origin
git -C <component-checkout> rev-parse HEAD
git -C <component-checkout> status --short
```

**Result:** a saved configuration and an inventory linking each capability to
its source, revision and external inputs.

## 2. Select the SoC and OS profiles

Follow [SoC support](/porting/soc-support) to select or create a matching shared
repository. Check its `soc.toml`, configuration fragments, DTSI and patch series,
then select a reviewed commit.

Assign the port's existing settings to these locations:

| Settings | Location |
| --- | --- |
| Common ARM64 configuration and patches | `UniXNU/profiles/arch/arm64/` |
| SoC registers, interrupts, CPU topology and platform operations | `UniXNU-<soc>-common` |
| XNU/IPSW versions, prelink roots, ABI and OS fixes | `UniXNU/profiles/os/<profile>/` |
| Board wiring, enabled peripherals, firmware and power policy | Device DTS, `board.toml` and `package/` |
| Partition layout and image parameters | Device `board.toml` |
| Reusable driver recipes and dependencies | `UniXNU/components.toml` and component repositories |
| Private firmware sources and hashes | Device `proprietary-files.txt` |

Compare existing settings with each selected profile before moving them.
Retain board overrides where they differ. Select an OS profile matching the
port's kernelcache and ABI inputs; follow [prelink](/concepts/prelink) when
creating a profile for another OS version.

For the SM8550 example, inspect a local checkout and obtain its exact revision:

```sh
SOC_DIR=../UniXNU-sm8550-common
```

If the checkout is absent, create it:

```sh
git clone https://github.com/UniXNU/UniXNU-sm8550-common "$SOC_DIR"
```

Inspect the selected checkout:

```sh
git -C "$SOC_DIR" rev-parse HEAD
git -C "$SOC_DIR" status --short
```

In the device's `feeds.toml`, add this
entry and replace `REQUIRED_SOC_COMMIT` with the reviewed 40-character commit:

```toml
[[source]]
name = "sm8550"
kind = "soc"
git = "https://github.com/UniXNU/UniXNU-sm8550-common"
commit = "REQUIRED_SOC_COMMIT"
```

Keep other required sources. Published builds use committed source pins.
For local SoC edits, pass `--local-module soc:sm8550=../UniXNU-sm8550-common`
to the commands that resolve the device and record that override.

**Result:** a pinned SoC source and a selected OS profile, with each setting's
owner identified.

## 3. Match component names to their sources {#component-names}

| Accepted official input | Canonical ID |
| --- | --- |
| `NativeAdreno` | `Adreno740` |
| `NativeMetal` | `AdrenoMetal` |
| `NativeUfs` | `ShengUfs` |
| `NativeHidInput` | `ShengHidInput` |
| `NativeNovatekTouch` | `ShengNovatekTouch` |
| `NativeGeniSpi` | `QcomGeniSpi` |
| `NativeMobileDisplay` | `GopFramebuffer` |
| `NativeAES` | `SoftwareAES` |
| `NativeKeyStoreEvents` | `AppleKeyStoreState` |
| `NativeRamBlock` | `RamBlock` |
| `NativeVirtioBlock` | `VirtioMmioBlock` |
| `NativeVirtioConsole` | `VirtioMmioConsole` |
| `NativePrelink` | `XnuPrelink` |
| `NativeWifi` | `Ath12kWifi` |

Apply canonical IDs to official repository URLs, checkouts, feeds, dependency
lists, build entry points, archives, build directories, CI, and documentation.
Keep the source filenames, runtime classes, bundle IDs, plugin filenames,
exported symbols, and protocol IDs recorded in `runtime_identifiers`.

Adreno740 provides the A740 kernel GPU interface. AdrenoMetal provides the Metal
frontend. Their metadata records A740/SM8550 scope and per-device verification.
The board supplies firmware, power policy, memory adjustments, and display
integration.

Match each origin URL to the catalog before renaming it. A community fork
retains its repository identity and pinned revision. Add its metadata and
recipe to the maintained catalog when selecting it as a separate component.

For each official component being renamed:

1. Move an existing submodule with `git -C "$DEVICE_DIR" mv <old-path> <new-path>`; Git updates its `.gitmodules` path.
2. Update its `.gitmodules` URL or its `feeds.toml` entry to the catalog values.
3. Run `git -C "$DEVICE_DIR" submodule sync --recursive` after editing `.gitmodules`.
4. Update its component ID, script names, archive paths and consumers using the catalog recipe and `outputs`.
5. Compare the checkout's commit and local edits with the inventory from step 1.

Use the [driver adaptation checklist](/porting/drivers) to map storage, GPU,
Wi-Fi, brightness, input, audio and power to their implementations. Check
board-package code as well as standalone repositories.

**Result:** every selected component resolves to the intended source and build
recipe, with its hardware and board dependencies recorded.

## 4. Edit board.toml and the kernel inputs

Add `schema_version = 2` before the first table. Merge the following fields
into the existing tables. This example selects SM8550 and iPadOS 17.7.11;
replace the device name, kit, defconfig and DTS path with your port's values:

```toml
schema_version = 2

[board]
name = "myboard"
kit = "myboard"
soc = "SM8550"
soc_source = "sm8550"
os_profile = "ipados-17.7.11-21H461"

[components]
include = ["ArmDTPlatform", "ArmCpu", "SoftwareAES", "XnuPrelink", "DarwinBoot"]

[kernel]
defconfig = "myboard_defconfig"
config_fragments = ["arch:configs/common.config", "soc:configs/sm8550.config", "os:configs/ipados.config"]
patch_series = ["arch:patches/xnu/series", "soc:patches/xnu/series", "os:patches/xnu/series", "device:patches/xnu/series"]

[device_tree]
source = "device:dts/myboard.dts"
include_dirs = ["soc:dts"]
```

Complete these edits before running the resolver:

1. Extend `components.include` with the port's complete driver selection from step 3.
2. Keep `configs/<defconfig>` and its required flags. Shared fragments apply in
   list order; the selected device defconfig applies last.
3. Create `patches/xnu/series`. List each board patch on its own line, relative
   to that directory. An empty series is valid when all patches come from shared profiles.
4. Compare the inherited archive plan with the port's required archive builders.
   When setting `kernel.archives`, include the full ordered plan. Use
   `component:<ID>` for catalog recipes and bare script names for auxiliary builders.
   The [reference board file](https://github.com/UniXNU/UniXNU-sheng/blob/main/board.toml)
   shows an explicit plan containing both.
5. Keep the board's firmware paths, partition layout, boot image settings and
   payload policy. Put OS properties in the selected OS profile and board-specific
   ADT overrides in the device's typed `[adt]` tables.

**Tables merge by key; arrays replace inherited arrays.** This applies to
components, fragments, patch series and archives. Include every required array
entry in an override. Each selected kernel-stage recipe must be covered by an
explicit archive plan. Dependencies determine component build order.

**Result:** the device selects four profile layers, a complete component set,
ordered kernel inputs and its existing board-specific settings.

## 5. Convert the hardware description to DTS

Read the [device-tree specification](/porting/device-tree) and
[driver matching rules](/drivers/device-tree-matching). Inspect the port's ADT
script and the properties read by its drivers. Convert them in this order:

| Input | Action |
| --- | --- |
| CPU, GIC, timer and shared controller resources | Reuse or add them in the SoC DTSI |
| Board memory, CPU selection, peripherals and reservations | Define them in `dts/<device>.dts` |
| Nodes read by XNU drivers | Preserve matching names through `unixnu,adt-name` and compatible properties |
| Address ranges, interrupts and references | Set parent cell widths, `ranges`, interrupt providers and reference argument counts |
| Apple identity and typed OS properties | Define them in the OS `[adt]` tables |
| Root volume UUID and payload handoff options | Keep them in device `[payload.adt]` |

Include the selected SoC DTSI from the board DTS. Use verified values from the
target board. With the selected SoC checkout available, compile it:

```sh
dtc -I dts -O dtb -i "$SOC_DIR/dts" \
  -o "$MIGRATION_DIR/hardware.dtb" "$DEVICE_DIR/dts/$DEVICE.dts"
```

Adjust the filename to `[device_tree] source`. Resolve compiler errors and
review warnings against the bindings. Format 2 uses this hardware description
with the common ADT generator during `./unixnu payload`. The generator adds
NVRAM, entropy and payload handoff properties.

**Result:** a compiled hardware DTB with the resources and properties required
by the selected drivers.

## 6. Resolve the migrated configuration

```sh
./unixnu defconfig "$DEFCONFIG" -D "$DEVICE_DIR"
./unixnu fetch -D "$DEVICE_DIR"
./unixnu status --json -D "$DEVICE_DIR" > "$MIGRATION_DIR/after.json"
./unixnu tree -D "$DEVICE_DIR"
python3 - "$MIGRATION_DIR/after.json" <<'PYCODE'
import json, pathlib, sys
status = json.loads(pathlib.Path(sys.argv[1]).read_text())
for key in ("output", "configuration", "profiles", "components", "patch_order"):
    print(key, json.dumps(status.get(key), indent=2))
PYCODE
```

Check the report against steps 1 through 5:

- Profiles resolve in ARM64, SoC, OS and device order.
- Sources, revisions and local overrides match the inventory.
- Component scope and dependencies match the board.
- Patch prerequisites appear before their consumers; each patch appears once.
- `output` points to `out/<device>/<os_profile>/<config>/`.

Update local scripts and CI to use that `output` path and the shared resolver.
The assembled `tree/` contains shared scripts, selected modules and the device
package at `kits/<board.kit>`. Review retained private scripts for required
helper files and source paths.

**Result:** the resolved configuration and assembled tree match the migration
inventory. Use this output directory in subsequent log and artifact checks.

## 7. Prepare firmware and local build inputs

In the device's UEFI DSC and FDF, include UniXNU, UniXNUDxe, DarwinBoot,
`UniXNURamDiskDxe`, DiskIoDxe and FAT support. Follow the module paths and library
mappings in [required firmware integration](/porting/uefi-firmware#required-integration).
Check `[firmware]` in `board.toml` against that checkout's configuration, DSC,
FD path and package paths.

If `unixnu.local.toml` exists, edit it. Otherwise copy `unixnu.example.toml` to
that path. Under `[build]`, set the device and firmware checkout, firmware DTB,
kernelcache and the payload inputs required by the port. The
[local configuration reference](/reference/configuration#local-build-inputs)
lists the keys. Store private inputs in local paths and record their source
and version in the porting record. For example, fill these values with the
actual paths and seed for the port:

```toml
[build]
device = "../UniXNU-myboard"
uefi = "../uefi-myboard"
dtb = "/path/to/firmware.dtb"
kernelcache = "/path/to/kernelcache"
unique_chip_id = "REQUIRED_DEVICE_SEED"
trust_cache = "/path/to/trustcache.bundle"
data_ramdisk = "/path/to/data-seed.dbr"
```

Include trust-cache and Data-seed entries when the selected payload needs them.

For `panic_screen = true`, the firmware checkout supplies
`FrameBufferSerialPortLib/Font.h`; the main UniXNU checkout supplies the entry
probe and renderer. See [panic screen inputs](/guide/debugging#panic-screen).

### Build inputs {#build-inputs}

Prepare the inputs used by the selected archive and image recipes:

- A full Xcode installation with the iPhoneOS SDK.
- `storage-abi/interface-audit.json` and its matching storage ABI inputs.
- Qualified `build/xnu-prelink/*candidate.macho` files and their JSON ABI records for the HID and display builders.
- VerifiedRoot and verified VirtIO policy archives required by the selected configuration.
- Board firmware listed in `proprietary-files.txt`, including the GPU firmware.
- `.cache/mesa-work`, built Turnip, and metal2vulkan inputs for the Metal plugin.
- The selected IPSW members, platform seed, trust-cache bundle, Data seed, and firmware DTB.

Use the selected recipes and the subsystem guides linked from
[driver adaptation](/porting/drivers) to identify the required inputs.

**Result:** firmware integration and local input paths are complete. Record
missing inputs with the build step that needs them.

## 8. Build in dependency order

Run each command after the previous one succeeds:

```sh
./unixnu ipsw fetch -D "$DEVICE_DIR"
./unixnu kernel -D "$DEVICE_DIR"
./unixnu build package -D "$DEVICE_DIR"
./unixnu firmware -D "$DEVICE_DIR"
./unixnu payload -D "$DEVICE_DIR"
./unixnu bootimg -D "$DEVICE_DIR"
```

The shorthand commands read `unixnu.local.toml`. Use [Building](/building) for
root-image preparation and component-specific build prerequisites. After any
boot-argument change, rebuild the payload and boot image.

| Output relative to the resolved directory | Check |
| --- | --- |
| `.config` | Required device flags and archive paths |
| `tree/.cache/xnu-work/` | Target-local patched XNU sources |
| `kernel/kernel.macho` | Successful kernel link and prelink |
| `device-tree/hardware.dtb` | Board hardware compilation during payload assembly |
| `payload/payload.img` | Kernel, ADT and configured optional inputs |
| `payload/payload.json` | Effective boot arguments and payload inputs |
| `boot/boot.img` | Firmware, firmware DTB and payload packaged successfully |
| `logs/` | Logs for the commands above |

The FD is written to the path configured by `[firmware] fd` in the firmware
checkout. Read the output path and inspect the packaged files:

```sh
OUTPUT_DIR=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["output"])' "$MIGRATION_DIR/after.json")
mtype -i "$OUTPUT_DIR/payload/payload.img" ::/EFI/UniXNU/unixnu.toml
mcopy -i "$OUTPUT_DIR/payload/payload.img" \
  ::/EFI/UniXNU/Payloads/kernel.macho.adt "$MIGRATION_DIR/kernel.macho.adt"
```

Check the effective [boot arguments](/xnu/boot-arguments#apply-arguments).
Keep the extracted ADT with the hardware DTB for review against the
[required nodes](/porting/device-tree#required-nodes) and driver matching rules.

**Result:** record each successful build with its output and log. Keep pending
steps and their required inputs explicit.

## 9. Update the porting record, CI and documentation

Add `porting.toml` and `.github/workflows/porting-record.yml` from the template
when absent; update existing copies in place. Merge the template `.gitignore`
rules and add `local.toml.example` with documented local overrides. Fill the board identity, selected
components, source revisions, configuration, procedure and evidence for each
area. Follow [porting records](/porting/records), then run:

```sh
python3 scripts/porting-record.py check --device "$DEVICE_DIR"
npm --prefix docs run build
```

Update the device README and root `AGENTS.md` with the current commands and
required reading. Update affected English and Chinese site pages, component
references, CI paths and firmware instructions. Complete the shared
[repository checklist](/porting/device-repository#completion), then follow
[publication](/porting/device-repository#publish) to push the device commit,
add the **`unixnu` GitHub topic**, check CI and pin the site record.
Compare the resolved configuration from step 6 with these requirements and
the inventory from step 1. The completed repository uses the same layout,
source pinning, build interfaces, records and publication steps as a new port.

Use this report when handing the migration to another maintainer or agent:

```text
Device, defconfig and OS profile:
Source revisions and local overrides:
Component selection and patch order:

Host checks:
  Command | Result | Output or log
  Configuration and source resolution:
  DTS and ADT:
  Kernel and prelink:
  Package and firmware:
  Payload and boot image:
  Porting record and documentation:

Device observations:
  Device, firmware and image revision:
  Boot / storage / display / input / GPU / network / audio / power:

Pending work:
  Required input or action | Affected step | Evidence
```

Host build results and device observations have separate entries. Use the
[bring-up sequence](/porting/bring-up) when recording device results and the
[QEMU guide](/reference/qemu) for common boot checkpoints.

## Complete SM8550 example

[UniXNU-sheng](https://github.com/UniXNU/UniXNU-sheng) provides a maintained
format 2 example. Read its `board.toml`, `feeds.toml`, `configs/sheng_defconfig`,
`dts/sheng.dts`, `patches/xnu/series`, `package/` and `porting.toml` together.
Its shared source is
[UniXNU-sm8550-common](https://github.com/UniXNU/UniXNU-sm8550-common),
its OS profile is `profiles/os/ipados-17.7.11-21H461/`, and its firmware is
[uefi-sheng](https://github.com/UniXNU/uefi-sheng).

Set `DEVICE`, `DEVICE_DIR` and `DEFCONFIG` from the selected device repository,
then follow steps 6 through 9 with the [build inputs](#build-inputs).
Outputs use `out/<device>/<os_profile>/<config>/`. The selected profile supplies
the GPU, storage, input, display and image components. Record results in the
device's `porting.toml`.

## Next steps

- [Driver adaptation](/porting/drivers): complete each subsystem's board inputs and integration.
- [Bring-up order](/porting/bring-up): record checkpoints using the built images.
- [Debugging](/guide/debugging): investigate failed builds and boot stages.

## Public-source storage and input builds {#source-drivers}

For the `ipados-27.0.1-24A446` profile, `build-sheng-source-drivers.py` compiles
ShengUfs, ShengHidInput and the board input transport using the prepared XNU
12377 C/C++ recipes. The profile pins IOStorageFamily 337.100.1 and IOHIDFamily
2238.120.5 from Apple's [macOS 26.5 source manifest](https://github.com/apple-oss-distributions/distribution-macOS/blob/83390100289cedfe669c31a96c94326d31afa1ed/release.json).
Apple's [iOS 26.5 manifest](https://github.com/apple-oss-distributions/distribution-iOS/blob/f92ef8bfffdb54c4aa4709717e3609f1647f59ed/release.json)
does not publish these families. The public macOS pins are source inputs, not
proof of compatibility with the stripped iOS or iPadOS binaries.

From UniXNU, with a prepared kernel tree, clean source checkouts at the profile
pins and extracted Novatek firmware in the device cache, run the reference builder:

```sh
python3 scripts/build-sheng-source-drivers.py \
  --tree /path/to/resolved/tree \
  --device /path/to/device \
  --storage-source out/driver-sources/IOStorageFamily \
  --hid-source out/driver-sources/IOHIDFamily \
  --with-storage-family
```

Obtain the source checkouts from the `git`, `ref` and `commit` entries in the
OS profile. `--touch-firmware` can select another extracted firmware file.
The builder rejects an incorrect source revision, a modified source checkout,
a mismatched kernel object target or empty firmware. Each object is checked for
arm64e and the iOS deployment version; commands, dependency hashes, compiler
warnings, firmware identity and remaining imports are recorded under
`build/sheng-source-drivers` in the target tree.

`--with-storage-family` builds the 14 public kernel C++ sources plus the IIG
implementation generated with Apple's DriverKit SDK. Apple source warnings are
recorded and do not become errors. The input transport archive includes board
touch/buttons, GENI SPI, Novatek protocol/contact processing and firmware,
without requiring the legacy display builder. HID uses `IOHIDDevice.h` and
`kIOHIDReportTypeInput`; this source mode does not install the Darwin 23 virtual
table edge-event patch. The original HID builder rejects arm64e targets.

These are relocatable archives, not a boot image. The report keeps
`link_qualified`, `runtime_qualified` and `edge_gestures_qualified` false.
HID diagnostics/startup, verified-root policy/crypto linkage, metaclass
registration, target-family dependencies and retained APFS consumers still
need integration. Do not register source and original copies of the same
IOKit class together. The public HID checkout lacks `IOHIDEventTypes.h` and
`IOHIDEventStructDefs.h`; its device implementation also requires private
reporting/analytics headers. A successful input-device compile does not mean
the full IOHIDFamily can be built from this release alone.

Storage header preparation now validates the selected source commit on each
archive build and replaces its generated header tree, preventing an earlier
OS profile's headers from surviving a source switch. Existing iOS 17 ABI and
device evidence must remain labeled with that OS version.
