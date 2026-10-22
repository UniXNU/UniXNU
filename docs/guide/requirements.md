# Requirements

## Host

The build driver runs on macOS. The kernel step invokes `xcodebuild` with the `iphoneos` SDK, and the `--skip-setup` option invokes `hdiutil`.

| Tool | Used by | Install |
| --- | --- | --- |
| macOS with Xcode | kernel, skip-setup, seed-data-grow | App Store or developer.apple.com |
| Python 3.11 or newer | every step | python.org or Homebrew |
| git, make | fetch, firmware | Xcode command line tools or Homebrew |
| cmake, ninja | kernel references | `brew install cmake ninja` |
| unifdef | libdispatch headers | `brew install unifdef` |
| LLVM with lld | kernel, firmware, boot image | `brew install llvm` |
| mtools | payload volume | `brew install mtools` |
| dtc | device tree properties | `brew install dtc` |
| fastboot | seed-data-grow `--auto`, userdata flash | Android platform tools |
| QEMU and AAVMF | optional smoke tests | `brew install qemu` |

The driver finds the keg-only Homebrew LLVM at `/opt/homebrew/opt/llvm/bin` without `PATH` changes. Other tools must be on `PATH`.

Network access is required for `unixnu fetch`, which updates the module submodules and fetches Apple source references and a Mu_Basecore tree.

Without a Mac, the `macOS build` workflow runs the Mac-only steps on a GitHub macOS runner. See [Build](/building#macos-runner).

## External inputs

These inputs live outside the UniXNU repositories.

| Input | Used by | Option | Environment |
| --- | --- | --- | --- |
| Mu-Silicium checkout for the device | firmware, boot image | `--uefi DIR` | `UNIXNU_UEFI` |
| Target IPSW, local file or HTTPS URL | kernel prelink, userdata | `--ipsw PATH_OR_URL` | `UNIXNU_IPSW` |
| Decompressed kernelcache | kernel prelink | `--kernelcache FILE` | `UNIXNU_KERNELCACHE` |
| Compiled device tree | boot image | `--dtb FILE` | `UNIXNU_DTB` |
| Trust cache bundle | payload | `--trust-cache FILE` | |
| Owner trust cache bundle | payload | `--owner-trust-cache FILE` | |
| Data ramdisk seed | payload | `--data-ramdisk FILE` | |
| Platform seed | payload | `--unique-chip-id HEX` | `UNIXNU_UNIQUE_CHIP_ID` |
| Prebuilt static archives | kernel | `--kernel FILE` for the payload, archives in the build tree | |
| edk2 or Mu_Basecore tree | package, firmware | `--edk2 DIR` | `UNIXNU_EDK2` |

### Target IPSW

The sheng board keeps iPadOS 17.7.11 as its default target. The iPhone X iOS 16.7.16 image is a second target and does not replace it.

| Target | Version | Build | Restore image |
| --- | --- | --- | --- |
| iPadOS, sheng default | 17.7.11 | 21H461 | [iPad_Pro_HFR_17.7.11_21H461_Restore.ipsw](https://updates.cdn-apple.com/2025SpringFCS/fullrestores/122-77166/DCA6CFE8-90E9-4B92-880D-3DE171798E40/iPad_Pro_HFR_17.7.11_21H461_Restore.ipsw) |
| iOS, iPhone X | 16.7.16 | 20H392 | [iPhone10,3,iPhone10,6_16.7.16_20H392_Restore.ipsw](https://updates.cdn-apple.com/2025FallFCS/fullrestores/122-77006/1158E502-D76D-4226-AA06-ED5E30CD1111/iPhone10,3,iPhone10,6_16.7.16_20H392_Restore.ipsw) |

`[ipsw] url` in the device repository is the default. `--ipsw` or `UNIXNU_IPSW` overrides it. Download the image outside the repository.

The device repository supplies the board description, the kernel defconfig and the archive builders listed in `[kernel] archives`.

## Device

The device needs:

- An unlockable bootloader that accepts `fastboot boot`.
- A UEFI port that provides a framebuffer, input, block I/O and file system access.
- A UART or USB transport for logs during bring-up.
- Enough RAM for the kernel window, the payload and the userdata image.
- The target OS restore image and a matching device identity.

## Next steps

- [Build](/building) describes the commands that consume these inputs.
- [Device repository](/porting/device-repository) describes the board file.
- [Devices](/devices/) lists device repositories and their specific inputs.
