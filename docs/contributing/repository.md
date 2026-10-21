# Repository layout

The base repository and every device repository share the same layout.

```
UniXNU/
  unixnu                  entry point
  scripts/unixnu/         build driver
  package/                UniXNU EDK II package
  drivers/                built-in XNU drivers
  kits/                   kernel libraries
  patches/                XNU, libpthread and Mesa patches
  scripts/                build and verification scripts
  docs/                   this site
  assets/                 logos
  feeds.toml              pinned external sources
  .gitmodules             module submodules
  examples/device/        sample device repository
```

Drivers and kits are independent public repositories under the UniXNU organization. They are included as submodules. Clone with `--recurse-submodules`, or run `git submodule update --init --recursive`.

## Module kinds

| Kind | Directory | Contents |
| --- | --- | --- |
| driver | `drivers/<Name>` | XNU driver source and reference plist |
| kit | `kits/<Name>` | Kernel library |
| patch | `patches/<Name>` | Patch set |
| script | `scripts/` | Build and verification scripts |
| package | `package/` | UniXNU package |
| refer | fetched tree | Apple source or edk2 |

A device repository can supply any kind. Its module overrides the base module with the same name.

## Resolution order

1. `--local-module [KIND:]NAME=PATH`
2. `--local-<kind> DIR`
3. `--local DIR`
4. a `local` key in `feeds.toml` or `local.toml`
5. the device repository
6. the base repository, including its module submodules
7. a git source in `feeds.toml`

## Build tree

`unixnu tree` writes `out/<board>/tree`:

```
tree/
  drivers/  kits/  patches/  refer/
  scripts/  package/
  build/    .cache/
```

Symbolic links point at the selected modules. Scripts are copied. The device `package/` appears as `kits/<board.kit>`.

## Scripts

The build scripts locate the tree from their own path. A script in `scripts/` can read `ROOT`, `build/`, `.cache/`, `refer/`, `drivers/`, `kits/`, `patches/` and `package/`.

## Add a module

Every repository in the organization carries the `unixnu` topic.

1. Create a public repository under the UniXNU organization.
2. Add the `unixnu` topic in the repository settings.
3. Add it as a submodule under `drivers/` or `kits/`.
4. Reference it from the board file or the kernel script.
5. Document the module in the matching section.

After a device port, contribute the device page and the porting notes to this repository.

## Commit scope

A commit changes one subject:

| Prefix | Subject |
| --- | --- |
| `feat(<area>)` | New capability |
| `fix(<area>)` | Defect repair |
| `docs` | Documentation |
| `build(<area>)` | Build system |
| `chore` | Cleanup |

The commit message describes the change. The documentation describes the current state.

## Next steps

- [Device repository](/porting/device-repository)
- [Documentation site](/contributing/documentation)
- [Build](/building)
