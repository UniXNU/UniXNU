# macOS profile

`macos-27.3-26C5035r` builds a kernel for macOS 27.3 user space. It is an
[arm64e profile](/porting/arm64e), so the device must pass the arm64e
requirements. One device repository serves the iPadOS and macOS profiles: the
macOS values sit in `[os_overrides."macos-27.3-26C5035r"]` of `board.toml`, and
an iPadOS build never reads them.

This page follows [Port a device](/porting/steps) and names what differs for
macOS. Every step not named here is the same as for iPadOS.

## What the profile supplies {#profile}

`profiles/os/macos-27.3-26C5035r/profile.toml` in UniXNU:

| Table | Content |
| --- | --- |
| `[os]` | XNU `12377.121.6` with `target = "macosx"`. The kernel is compiled with `XNU_TARGET_OS_OSX` on the machine configuration, memory layout and link address of the iPadOS kernel |
| `[ipsw]` | `UniversalMac_27.3_26C5035r_Restore.ipsw`, product `Mac17,11`. `fetch` lists the kernelcache, the device tree and the static, system and application trust caches |
| `[kernel.prelink]` | The `kernelcache_sha256` pin, the `roots` of the macOS startup closure and `early_security_init`. A root with a leading `!` is left out of the closure. The collection keeps its symbol tables and its linked addresses, so there is no `slide` |
| `[adt]` | The Mac17,11 identity, the `/chosen` boot volume UUIDs and the `asmb` boot policy |
| `[userdata]` | Three windows: `OS`, `SystemOS` (`Cryptex1,SystemOS`) and `App` (`Cryptex1,AppOS`) |
| `[root]`, `[payload.adt]` | Volume UUIDs and image digests of the three windows, and the root volume UUID |

`configs/macos.config` and `patches/xnu/series` beside it hold the kernel
configuration and the patch series: the Darwin 26 system calls and kernel
interfaces, the macOS machine options, the Data firmlinks, the VM and Hardware
volumes on Data, and the application cryptex mount.

## 1. Check the host and inputs {#inputs}

A macOS build runs on a Mac with Xcode. In addition to the
[common requirements](/guide/requirements):

| Input | Source |
| --- | --- |
| macOS SDK | Xcode. The boot shim and the device recipes that use macOS family headers compile with `xcrun --sdk macosx` |
| IPSW | `[ipsw] url` of the profile, or `--ipsw` |
| Kernelcache | Extracted from the IPSW and checked against `kernelcache_sha256` |
| Trust caches | `[payload.runtime] trust_components` names the IPSW members that go into the owner trust bundle |
| Data seed | Made once as root from the system volume, see [step 4](#data-seed) |
| Root access | `sudo` for the Data seed |

## 2. Add the macOS values to the device repository {#device}

Add a defconfig for the profile, map it in `[package.defconfig]`, and put every
value that differs under the override. The
[sheng board file](https://github.com/UniXNU/UniXNU-sheng/blob/00ba90984e831e4c6ce30ec3d8a56e6434e9f1af/board.toml)
is a complete example.

```toml
[package.defconfig]
"macos-27.3-26C5035r" = "<device>_macos_defconfig"

[os_overrides."macos-27.3-26C5035r"]
remove = ["payload.install", "payload.skip_setup_tool", "payload.runtime.appsync"]

[os_overrides."macos-27.3-26C5035r".kernel]
defconfig = "<device>_macos_defconfig"
config_fragments = ["arch:configs/common.config", "os:configs/macos.config"]
archives = ["<every archive recipe of the macOS kernel, in order>"]

[os_overrides."macos-27.3-26C5035r".components]
include = ["<every component of the macOS kernel>"]

[os_overrides."macos-27.3-26C5035r".payload]
size_mib = 200
kernel_args = ["<every kernel argument of the macOS image>"]

[os_overrides."macos-27.3-26C5035r".payload.adt]
chip_id = "6050"

[os_overrides."macos-27.3-26C5035r".payload.runtime]
target = "macos27"
build = "26C5035r"
data_seed_tool = "scripts/make-macos-data-seed.py"
data_gib = 210
skip_setup = false
boot_shims = true
```

| Key | macOS value |
| --- | --- |
| `[package.defconfig]` | The defconfig that `--os` and the packaging script select for the profile |
| `kernel.config_fragments` | `os:configs/macos.config` |
| `kernel.patch_series` | No override when the board list uses the `os:` prefix: `os:patches/xnu/series` resolves to the macOS series |
| `kernel.archives`, `components.include`, `payload.kernel_args` | Complete lists. Arrays replace the board arrays |
| `kernel.prelink.roots` | Not set. The profile list applies. A board list for another profile belongs in that profile's override, because a board value replaces the profile list |
| `payload.size_mib` | Room for the kernel collection, the Data seed and the addon |
| `payload.adt.chip_id` | `6050`, the chip of Mac17,11 |
| `payload.runtime.target`, `build` | `macos27` and `26C5035r` |
| `payload.runtime.data_seed_tool` | The seed script that runs as root |
| `payload.runtime.data_gib` | Size of the Data volume. The persistent Data store must not overlap the root image in `userdata` |
| `payload.runtime.skip_setup` | `true` adds `--skip-setup` to the seed command |
| `payload.runtime.boot_shims` | Adds the owner `apfs_boot_util` to the addon, for `apfs-boot-shim=1` |
| `payload.runtime.gpu_addon` | `true` builds the Metal plugin for macOS. With `gpu-addon=1` the kernel writes it to `/Library/GPUBundles` on Data |
| `remove` | Board keys that apply to iPadOS only, such as the install entry, `payload.skip_setup_tool` and `payload.runtime.appsync` |

On sheng the macOS defconfig differs from the iPadOS 27 one only in the Data
volume UUID, which the build writes from the seed. The Mac17,11 identity comes
from the profile.

Kernel arguments that the macOS patch series adds:

| Argument | Effect |
| --- | --- |
| `vc-text=1` | Draws the kernel console as text on the boot framebuffer and mirrors it to the serial console |
| `exec-log=1` | Prints every image activation and every exit with its wait status and reason. Diagnostic, off by default |
| `apfs-boot-shim=1` | Shows the addon's `apfs_boot_util` over the system's for launchd's mount boot tasks. Needs `boot_shims = true` |
| `timebase-hz=24000000` | Gives user space a 24 MHz timebase when the hardware counter runs at another rate |
| `gpu-addon=1` | Writes the Metal plugin to `/Library/GPUBundles` |

## 3. Select the profile {#select}

`--os` applies to one command. Pass it to every command of a macOS build, or
set `board.os_profile` on a board that builds macOS only. `macos-27` resolves to
`macos-27.3-26C5035r`, and the output directory is
`out/<device>/macos-27.3-26C5035r/<config>/`.

```sh
./unixnu defconfig <device>_macos_defconfig -D ../UniXNU-<device> --os macos-27
./unixnu fetch --os macos-27
./unixnu ipsw info --os macos-27
./unixnu status --json --os macos-27
```

`ipsw info` shows `27.3 (26C5035r)`. `status` shows the macOS profile root, the
merged override and the patch order.

## 4. Make the Data seed {#data-seed}

Build the kernel and the payload in one command, so the kernel build binds the
seed's volume UUID:

```sh
./unixnu build kernel payload --os macos-27
```

Without a seed the command stops before compiling and prints:

```sh
sudo python3 <tree>/scripts/make-macos-data-seed.py <OS image> <output>/runtime/data.dbr --gib <data_gib>
```

Run it, then repeat the build. The script copies
`/System/Library/Templates/Data` of the system volume with its file owners.
Optional arguments:

| Argument | Effect |
| --- | --- |
| `--skip-setup` | Marks Setup Assistant done |
| `--user NAME:PASSWORD` | Adds a local administrator and its home |
| `--keyboard-type PRODUCT-VENDOR-COUNTRY=TYPE` | Records a keyboard layout type, so Keyboard Setup Assistant does not ask |
| `--volume-uuid UUID` | Gives the Data volume a fixed UUID, so a new seed replaces an older one without a kernel build |

Keep `runtime/data.dbr` for every later build of the installation. A payload
build with a seed whose UUID differs from the compiled configuration stops and
asks for a kernel build. The kernel mounts the seed at `/System/Volumes/Data`
and sets the firmlinks of `/usr/share/firmlinks`.

## 5. Build the images {#build}

```sh
./unixnu build kernel payload --os macos-27
./unixnu build package --os macos-27
./unixnu build firmware --os macos-27
./unixnu build userdata --os macos-27 --dry-run
./unixnu build userdata --os macos-27
./unixnu bootimg --os macos-27
```

The packaging script runs the same steps except userdata:

```sh
scripts/package.sh --os macos-27 --uefi ../uefi-<device>
```

| Step | macOS difference |
| --- | --- |
| Kernel | `XNU_TARGET_OS_OSX`, the macOS series and the prelink against the macOS kernel collection |
| Payload | The Mac17,11 ADT, the owner trust bundle and the addon built for `macos27` |
| Userdata | Three windows. Check the dry-run capacity against `data_gib` |
| Package, firmware, boot image | None |

A board that links owner root policies (`CONFIG_XNU_SOURCE_STORAGE=y`) needs a
signed policy for each window. `scripts/make-root-policies.py --tree TREE
--output POLICIES --window NAME=IMAGE:VOLUME_UUID` writes
`POLICIES/NAME/manifest.header.bin`, `trusted-key.bin` and `verification.json`,
and the hash table `TREE/build/verified-root-NAME/hashes.bin`. `IMAGE` holds the
window's bytes; its SHA-256 equals `[root] <window>_image_sha256` of the
profile. The storage archive recipe reads the policy directory named by its
`--policy-dir` argument.
With `CONFIG_XNU_SOURCE_STORAGE_TABLES="userdata"`, add each hash table to the
userdata image as `--object NAME.vroot=FILE`.

## 6. Adapt the drivers {#drivers}

Follow [driver adaptation](/porting/drivers) in the same order. The macOS
kernel collection has its own class layouts, and macOS user space expects some
services that iPadOS does not. The sheng port shows each case:

| Area | macOS adaptation |
| --- | --- |
| Private class bindings | A fixture per build for each bound class family, `scripts/<family>-26C5035r.json`. `scripts/gen-board-abi.py` writes them from the symbols of the collection, and the display recipe selects them by build |
| Crypto | `SoftwareAES` joins `components.include` and `kernel.archives`, compiled against the 26C5035r class layout. A board probe registers it, because AppleImage4 waits for an `IOAESAccelerator` service |
| Network | `en0` is an `IOEthernetController` of the original IONetworkingFamily, started with `ethernet=1`. It carries the Wi-Fi module's frames. The TimeSync clock takes its identifier from the address of an Ethernet or 802.11 interface, and WindowServer waits for that clock. The supplicant is built for macOS and its job is a plist in `/Library/LaunchDaemons` |
| Input | The HID device starts with `offline-hid-home=1`. WindowServer pairs the touch screen with the display through the service's `displayUUID`, the UUID the framebuffer publishes as `IOMFBUUID` |
| Keyboard cover | A keyboard and a pointer: relative motion, scroll steps and two buttons, without the Keyboard Power usage |
| GPU | The plugin is built as a macOS bundle with its executable in `Contents/MacOS` |
| Audio | The audio server plug-in is a macOS driver bundle in `/Library/Audio/Plug-Ins/HAL` |
| Bluetooth | The daemon opens the serial device `/dev/cu.BLTH`. The board's daemon, BlueTool and capability library sit in the addon's `sbin` and `lib`, shown over `/usr/sbin` and `/usr/lib` |
| Firmware images in the kernel | Placed in `__DATA,__firmware` |

## 7. Boot and check {#bring-up}

Flash the userdata image and boot as in [Boot the image](/guide/boot). The
[bring-up order](/porting/bring-up) applies with these macOS checkpoints:

| Stage | Check |
| --- | --- |
| Storage and root | The partition scheme publishes `OS`, `SystemOS` and `App`. The root is the read-only system volume with SystemOS mounted over it |
| Data | Data mounts at `/System/Volumes/Data`. `/System/Volumes/VM` and `/System/Volumes/Hardware` resolve into it |
| Cryptexes | The OS cryptex view and the App cryptex appear below `/System/Volumes/Preboot/Cryptexes` |
| Userland | launchd finishes its boot tasks and WindowServer presents the login window or Setup Assistant |

`vc-text=1` keeps the kernel log on the panel. `exec-log=1` names a boot task
that fails.

## 8. Record the results {#record}

`device.os_profile` in `porting.toml` equals `board.os_profile`, the default
profile of the board. A board that serves several profiles keeps one record:
write the macOS configuration, findings and evidence into the same areas and
name the profile and build in each entry. See [porting records](/porting/records).
