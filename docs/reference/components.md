# Component catalog

`components.toml` in UniXNU records the maintained components. Profiles select
canonical IDs through `[components] include`. The resolver adds dependencies
and orders their build commands before their consumers.


## Find and select an implementation

1. Find the capability in the [driver adaptation checklist](/porting/drivers).
2. Search `components.toml` for its ID, then read the implementation and its board dependencies.
3. Compare hardware and OS ABI inputs; use the linked adaptation procedure to fill missing board hooks.
4. Select it in the device profile, add the required archive/integration step and inspect the result:

```sh
./unixnu status --json
```

Continue with [Building](/building) after the dependencies and source revisions match the intended port.


## Fields

| Field | Meaning |
| --- | --- |
| `id` | Canonical component ID |
| `kind`, `path` | Module kind and checkout path |
| `repository`, `revision` | Source repository and pinned revision |
| `legacy_name` | Accepted official compatibility name |
| `function` | Capability provided by the component |
| `scope` | Implementation scope |
| `hardware` | Required controllers, protocols, or GPU family |
| `os_abi` | XNU or userland ABI requirements |
| `board_dependencies` | Firmware, wiring, memory, or policy inputs |
| `verified_devices` | Devices with recorded hardware results |
| `dependencies` | Component IDs built first |
| `build_stage` | Kernel, payload, firmware, prelink, or embedded integration |
| `build` | Build command arguments |
| `outputs` | Paths produced in the target tree |
| `runtime_identifiers` | Source filenames, classes, bundle/plugin IDs, symbols, protocols |

Implementation scope and hardware verification are separate fields. Adreno740
implements the A740 GPU interface used by SM8550. AdrenoMetal provides the Metal frontend through metal2vulkan
and Turnip, with dependencies on the kernel interface and OS ABI.

## Selection

```toml
[components]
include = ["ArmDTPlatform", "ArmCpu", "Adreno740", "AdrenoMetal", "GopFramebuffer"]
```

Kernel-stage recipes run in dependency order. `[kernel] archives` can place `component:<ID>` markers among auxiliary commands. Payload, firmware, prelink, and embedded entries describe their corresponding integration stages.

The device's `include` array replaces the inherited array. List the required
selection in full; dependencies are added by the resolver. Inspect the resolved
selection, source revisions, local overrides, and build order:

```sh
./unixnu status --json -D /path/to/device
```

Search this catalog, the [component pages](/drivers/repositories), the README,
and source before implementing a capability. Match interfaces, hardware scope,
OS requirements, and board inputs.

## Source identity

Official compatibility names resolve using the repository identity recorded in
the catalog. For example, the official `UniXNU/NativeAdreno` source resolves to
`Adreno740`. A source such as `another-owner/NativeAdreno` retains its own
identity and selection. Check the remote and revision before editing a feed.

The [migration table](/porting/migration#component-names) lists accepted names.
Source filenames and runtime identifiers keep the values used by their ABI.
For example, the `AdrenoMetal` component stages `NativeAdrenoMetal` plugin files.
