# Troubleshooting

## Procedure {#procedure}

1. Save the failing command and first error. For a boot failure, record the last confirmed [bring-up stage](/porting/bring-up).
2. Run `./unixnu status --json` to confirm the device, source origins, OS profile and output directory. Inspect the corresponding [log](#logs) or [report](#inspect-a-report).
3. Find the symptom in the build, IPSW or boot table below. Check the named input before applying its action.
4. Repeat the failed step with the corrected input. Repack the boot image after changing firmware or payload. Record whether the original error is resolved and which checkpoint now completes.
5. If the cause remains undetermined, save an [evidence bundle](/guide/debugging#evidence-bundle) with the command, revisions and logs for investigation.

## Early boot checks

- A top green bar marks DarwinBoot's handoff before the kernel branch. Follow the [green-bar diagnosis](/guide/debugging#green-bar).
- To apply changed boot arguments, rebuild the payload and boot image, then boot that image. Follow [apply boot arguments](/xnu/boot-arguments#apply-arguments).
- Save firmware and image paths in [unixnu.local.toml](/reference/configuration#local-build-inputs) for `./unixnu firmware`, `./unixnu kernel`, and `./unixnu bootimg`.

## Build

| Symptom | Check | Action |
| --- | --- | --- |
| `no device repository` | `-D` or `UNIXNU_DEVICE` | Pass the device repository |
| `has no board.toml` | Device repository layout | Create `board.toml` |
| `is an EXAMPLE device repository` | `[board] example` | Complete the template inputs and remove `board.example = true` |
| `no configuration` | `out/<device>/<os_profile>/<config>/.config` | Run `unixnu defconfig NAME` |
| `no Mu-Silicium checkout` | `--uefi` path | Pass a checkout with `Resources/Scripts/mkbootimg.py` |
| `is not a Mu-Silicium checkout` | Path | Point `--uefi` at the root of the checkout |
| `no edk2 tree` | `--edk2` or fetched edk2 | Run `unixnu fetch` or pass a Mu_Basecore tree |
| Missing archive in the kernel step | `[kernel] archives` and `logs/archive-NN-*.log` | Fix the builder entry or supply the archive |
| `no builder makes it` | The named `*_ARCHIVE` path | Add a builder to `[kernel] archives` or place the archive in the build tree |
| `kernelcache not found` | `--kernelcache` or IPSW | Fetch the IPSW or pass the file |
| `does not match the kernelcache` | `[kernel.prelink] kernelcache_sha256` | Use the pinned image |
| Firmware volume size mismatch | `[uefi_fd] size` | Rebuild the firmware or correct the config |
| Payload larger than `size_mib` | `[payload] size_mib` | Raise the size or remove files |
| `not one of the trust caches this board accepts` | `[payload] trust_cache_sha256` | Use an accepted bundle or pass the owner-signed bundle with `--owner-trust-cache` |
| `unsupported kernel argument` | Argument characters | Use letters, digits, `_`, `.`, `-` |
| `command line is ... bytes` | Argument count | Shorten the line to 1000 bytes |

## IPSW

| Symptom | Check | Action |
| --- | --- | --- |
| `this IPSW is ...` | Product, version, build | Use the image the board describes |
| `no Erase build identity` | Device class, chip ID, board ID | Correct the identity values |
| `does not support range requests` | Remote URL | Use a server with range support or a local file |
| `differs from the pinned sha256` | `[ipsw.sha256]` | Use the pinned member or update the pin |
| `expected exactly one arm64 slice` | Kernelcache | Use an ARM64 kernelcache |

## Boot

| Symptom | Check | Action |
| --- | --- | --- |
| `fastboot` does not see the device | Driver, cable, bootloader mode | Install the USB driver and reboot to bootloader |
| Image starts and resets | Boot image header, base and size | Check the Mu-Silicium config and BootShim flags |
| Firmware stalls | Last firmware log and initialized resources | Capture the output, reset to bootloader and follow [bring-up](/porting/bring-up) |
| No display | GOP driver | Use `console = "text"` or a serial console |
| No menu | Configuration path | Place `unixnu.toml` at `\EFI\UniXNU\unixnu.toml` |
| No boot entry | Payload volume | Check `boot.json` for a nonzero `ramdisk_bytes`, the FD for UniXNURamDiskDxe/DiskIoDxe/FAT, the FDT initrd range, and `EFI/UniXNU/unixnu.toml`. Follow [payload discovery](/porting/uefi-firmware#payload-discovery). |
| Driver failed | First failure reason in the menu | Fix the driver path or its dependencies |
| `no loader protocol installed` | DarwinBoot in the firmware volume | Add DarwinBoot to the FDF or the payload |
| `loader revision 1 cannot accept kexts` | Loader revision | Use a revision 2 loader or remove the kexts |
| `boot refused: ...; firmware retained` | DarwinBoot log | Check the kernel, ADT, trust cache and placeholders |
| Kernel panics at entry | Page tables, kernel window, boot arguments | Use the QEMU fixture and the boot progress log |
| Panic names a provider | Device tree node or driver archive | Add the node or enable the driver |
| No root device | Userdata image, UUID, capacity | Flash the image, check the UUID and window offsets |
| Data store window refused | Seed size, `log-reserve`, root image | Recalculate root, Data and log allocations; select a seed size that fits |
| Display assertion in userland | Display provider and boot arguments | Check the display driver and the focus arguments |

## Logs

| Source | Location |
| --- | --- |
| Build | `out/<device>/<os_profile>/<config>/logs/` |
| Boot manager | Serial console, `UNIXNU:` lines |
| Loader | Serial console, `DARWINBOOT:` lines |
| Kernel | Serial console |
| QEMU | `--log` file and the `.clean.log` companion |

## Inspect a report

```sh
jq . out/<device>/<os_profile>/<config>/boot/boot.json
jq . out/<device>/<os_profile>/<config>/payload/payload.json
jq . out/<device>/<os_profile>/<config>/userdata/userdata-root.json
```

The reports record the input hashes. Compare them with the files you supplied.

## Module origin

```sh
./unixnu status
```

The output lists every module and its origin. A local module is marked and reported as not pinned.

## Next steps

- [Build](/building)
- [Boot the image](/guide/boot)
- [Bring-up order](/porting/bring-up)
