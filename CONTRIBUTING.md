# Contributing to UniXNU

Read the [documentation](https://unixnu.com) before changing the build driver, the kernel patches or a device port. The [repository layout](https://unixnu.com/contributing/repository) page describes the module system.

## Repository scope

| Repository | Changes |
| --- | --- |
| `UniXNU` | Build driver, UEFI boot manager, DarwinBoot, generic drivers, kits, patches and documentation |
| `UniXNU-<device>` | Board file, defconfig, device scripts, device drivers and package |
| `uefi-<device>` | Mu-Silicium UEFI port |

A change that applies to one board belongs in the device repository. A change that applies to the stack belongs in this repository.

## Repository topics

Every repository in the UniXNU organization carries the `unixnu` topic. Add the topic before a repository is linked from the documentation or used as a module.

## Private blobs

Do not commit Apple IPSW files, kernelcaches, disk images, trust caches, Data seeds, vendor firmware or other proprietary binaries. Keep them in a local cache or external storage. The macOS runner deletes these inputs after the artifacts are uploaded.

## Development

```sh
git clone https://github.com/UniXNU/UniXNU
cd UniXNU
./unixnu defconfig <name> -D ../UniXNU-<device>
./unixnu fetch
./unixnu build kernel package firmware payload
./unixnu bootimg --uefi ../uefi-<device> --dtb <board>.dtb
```

Use `--local-module` or `--local` to test a module from a working directory without committing it.

## Change guidelines

- State the current behavior in the code and documentation.
- Keep one subject per commit.
- Add a test when it prevents a failure a future edit would introduce. A behavior visible on every run needs no assertion.
- Put device-specific values in the device repository.
- Put stack-wide behavior in `UniXNU`.
- Keep the English and Simplified Chinese documentation pages in sync.

## Commit messages

```
feat(<area>): <summary>
fix(<area>): <summary>
docs: <summary>
build(<area>): <summary>
chore: <summary>
```

The message describes the change. The documentation describes the resulting state.

## Kernel patches

1. Edit `.cache/xnu-work` after a first kernel build.
2. Generate the patch with `git diff`.
3. Name it so the apply order is correct.
4. Rebuild the kernel and the prelink.
5. Record the kernelcache pin if the ABI changed.

Late patches use the `zzy-` and `zzz-` prefixes.

## Drivers

- Built-in XNU drivers compile against the recorded XNU flags in `*.cpo.json`.
- UEFI drivers use the EDK II module layout.
- Kext bundles keep the standard bundle layout.
- A driver that touches hardware reports each stage through a boot argument while it is under bring-up.

## Documentation

After a device port, contribute the device page and the porting notes to this repository.

The documentation source is in `docs/`. The site is bilingual:

| Locale | Path |
| --- | --- |
| English | `docs/` |
| Simplified Chinese | `docs/zh/` |

```sh
cd docs
npm install
npm run dev
npm run build
```

Add a page to both locales and to the sidebar in `docs/.vitepress/config.mts`.

## Security

Report a security issue privately to the maintainers. Do not open a public issue for a trust cache, code signing or boot policy defect.

## License

Contributions are licensed under BSD-2-Clause-Patent. The `LICENSE` file in each directory applies to that directory.
