# Requirements

## Procedure {#procedure}

1. Choose the [host toolchain](#host) for the steps you will run. Complete the macOS or Linux instructions and confirm the required tools are available.
2. Collect the [external inputs](#external-inputs) for the selected OS profile: IPSW/kernelcache, trust cache, Data seed and driver ABI inputs where required. Record their paths and versions.
3. Check the [device inputs](#device): device repository, firmware repository and target DTB. Save paths in [local configuration](/reference/configuration#local-build-inputs).
4. Continue with [Build and boot](/building). Run `./unixnu status --json` after selecting the defconfig; the device, OS profile and source paths must match the inputs above.

## Host

The build driver supports macOS and Linux. On macOS, the kernel step uses Xcode and the `iphoneos` SDK. On Linux, use the [Linux toolchain](#linux). `--skip-setup` and Data seed resizing use macOS image tools.

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

### Linux

On Linux the kernel step builds with upstream clang and an open source Mach-O toolchain instead of Xcode. `scripts/linux/setup-toolchain.py` installs it once, as root, under `/opt/unixnu-linux` (or the prefix given as its argument or in `UNIXNU_TOOLCHAIN`):

| Tool | Source |
| --- | --- |
| clang with the `__builtin_xnu_type_*` builtins that xnu's `kalloc.h` needs | llvm-project with `scripts/linux/llvm-xnu-builtin-type.patch` |
| ld64, libtool, nm, lipo | cctools-port `1030.6.3-ld64-956.6` |
| mig, iig | bootstrap_cmds-138, iig-port |
| `xcrun`, `plutil`, `codesign`, Command Line Tools layout | shims in `scripts/linux` |
| lzfse | lzfse, for the kernelcache |

The installer runs on glibc Linux hosts. It detects the distribution through `/etc/os-release` and installs dependencies with its package manager:

| Package manager | Distribution family |
| --- | --- |
| apt | Debian, Ubuntu and derivatives |
| dnf | Fedora and RHEL derivatives |
| pacman | Arch Linux and derivatives |
| zypper | openSUSE and SUSE |

Use the distribution's enabled repositories for Clang, LLVM development files, libclang, libbsd, UUID, OpenSSL and zlib development packages. The installer also installs mtools and dtc for payload and device-tree commands. Package availability depends on the configured repositories. Keep the system and package databases current through the distribution's normal update procedure.

```sh
# Preview the dependency commands.
scripts/linux/setup-toolchain.py --print-packages
# Install dependencies and build the toolchain.
sudo scripts/linux/setup-toolchain.py
# Check installed tools, headers and library linking.
scripts/linux/setup-toolchain.py --check
```

`--package-manager apt|dnf|pacman|zypper` selects an installer explicitly. For another distribution or an environment with dependencies prepared separately, use:

```sh
scripts/linux/setup-toolchain.py --package-manager pacman --print-packages
sudo scripts/linux/setup-toolchain.py --package-manager none --llvm-config /path/to/llvm-config
```

`--llvm-config FILE` or `LLVM_CONFIG` selects the host LLVM installation. Its `clang`, `clang++`, libclang and resource headers are resolved together. XNU's patched Clang is built from the pinned LLVM source. `-j N` sets the build parallelism. The optional positional argument selects the install prefix, which defaults to `/opt/unixnu-linux` or `UNIXNU_TOOLCHAIN`.

The script writes `xcrun`, `plutil` and `codesign` shims to `/usr/bin`, where XNU's makefiles call them. Mach-O archives, libdispatch and BlocksRuntime live under the toolchain prefix. Building Clang takes most of the setup time. The userdata step runs on Linux; `--skip-setup` and `seed-data-grow` require macOS.

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

For the sheng target, review the [ABI, SDK, firmware, and image input inventory](/porting/migration#build-inputs) before starting the full build.
