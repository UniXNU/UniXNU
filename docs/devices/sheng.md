# Xiaomi Pad 6S Pro (sheng)

sheng is the Xiaomi Pad 6S Pro with the SM8550 SoC. It is one device port among the devices listed in [Supported devices](/devices/).

| Repository | Contents |
| --- | --- |
| [UniXNU-sheng](https://github.com/UniXNU/UniXNU-sheng) | Board file, defconfig, device scripts, touch driver and package |
| [uefi-sheng](https://github.com/UniXNU/uefi-sheng) | Mu-Silicium UEFI port |

## Board

```toml
[board]
name = "sheng"
soc = "SM8550"
description = "Xiaomi Pad 6S Pro"
kit = "sheng"
```

The output directory is `out/sheng/`.

## IPSW

```toml
[ipsw]
url = "https://updates.cdn-apple.com/2025SpringFCS/fullrestores/122-77166/DCA6CFE8-90E9-4B92-880D-3DE171798E40/iPad_Pro_HFR_17.7.11_21H461_Restore.ipsw"
product = "iPad7,1"
version = "17.7.11"
build = "21H461"
device_class = "j120ap"
chip_id = 0x8011
board_id = 12
fetch = ["KernelCache", "DeviceTree", "StaticTrustCache", "Cryptex1,SystemTrustCache"]
```

The board uses the unchanged iPad7,1 iPadOS 17.7.11 restore image. The member pins:

```toml
[ipsw.sha256]
"044-76040-038.dmg" = "3f99b859c9728379110b66657c7b15285bcb1925ad8b5726542e2cdcf8b1028d"
"044-76034-038.dmg" = "b4908cde41d23e6bc05e6af51a2c9eeb00cf0f863a6a18b1600c96a3fd70414f"
```

## Userdata

```toml
[userdata]
first_lba = 0x2f3840
last_lba = 0x3d0abfa
lba_bytes = 4096
windows = [
  { name = "OS", component = "OS" },
  { name = "SystemOS", component = "Cryptex1,SystemOS" },
]
```

The LBAs come from the GPT entry named `userdata` on the device.

## Kernel

```toml
[kernel]
defconfig = "sheng_defconfig"

[kernel.prelink]
tool = "kits/NativePrelink/emit_prelink.py"
kernel = "build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/mach.development.bcm2837.unstripped.noctf"
kernelcache_sha256 = "f18b4df865405f2a287b84977d7aca745e056d656d9fc9df1662970ce2969de7"
slide = "-0x1000000"
early_security_init = "com.apple.driver.AppleMobileFileIntegrity=0xfffffff005ab4ae0"
```

The prelink roots:

```
com.apple.AppleFSCompression.AppleFSCompressionTypeZlib
com.apple.driver.AppleARMPlatform
com.apple.driver.AppleARMWatchdogTimer
com.apple.driver.AppleAudioClockLibs
com.apple.driver.AppleEffaceableStorage
com.apple.driver.AppleIISController
com.apple.driver.AppleM2ScalerCSCDriver
com.apple.driver.AppleMobileFileIntegrity
com.apple.driver.ApplePMGR
com.apple.driver.IODARTFamily
com.apple.filesystems.apfs
com.apple.iokit.CoreAnalyticsFamily
com.apple.iokit.IOAVFamily
com.apple.iokit.IOAudio2Family
com.apple.iokit.IOCECFamily
com.apple.iokit.IOCryptoAcceleratorFamily
com.apple.iokit.IOGPUFamily
com.apple.iokit.IOHDCPFamily
com.apple.iokit.IOMobileGraphicsFamily
com.apple.iokit.IOReportFamily
com.apple.iokit.IOSlowAdaptiveClockingFamily
com.apple.iokit.IOStorageFamily
com.apple.iokit.IOSurface
com.apple.kec.Libm
com.apple.kec.corecrypto
com.apple.kext.AppleMatch
com.apple.kext.CoreTrust
com.apple.security.AppleImage4
com.apple.security.sandbox
com.apple.iokit.IOHIDFamily
com.apple.iokit.IOHIDEventDriver
```

## Defconfig

`sheng_defconfig` enables:

```
CONFIG_XNU_SOURCE_CORECRYPTO14=y
CONFIG_XNU_SOURCE_PTHREAD=y
CONFIG_XNU_ARM_DT_PLATFORM=y
CONFIG_XNU_ARMCPU=y
CONFIG_XNU_NATIVE_UFS=y
CONFIG_XNU_NATIVE_AES=y
CONFIG_XNU_NATIVE_VIRTIO_BLOCK=y
CONFIG_XNU_NATIVE_RAM_BLOCK=y
CONFIG_XNU_TRUST_CACHE_RUNTIME=y
CONFIG_XNU_SOURCE_MOCKFS=y
CONFIG_XNU_NATIVE_CS_HASH_CACHE=y
CONFIG_XNU_VERIFIED_ROOT_PROBE=y
CONFIG_XNU_OWNER_ROOT_AUDIT=y
CONFIG_XNU_OWNER_ROOT_TRUST=y
CONFIG_XNU_SHENG_PMGR=y
CONFIG_XNU_OWNER_CACHE_MOUNT=y
CONFIG_XNU_OWNER_CACHE_STARTUP=y
CONFIG_XNU_OWNER_BOOT_MANIFEST=y
CONFIG_XNU_OWNER_DATA_MOUNT=y
CONFIG_XNU_OWNER_UNION_SYSTEMOS=y
CONFIG_XNU_DT_PANIC_REGION=y
CONFIG_XNU_ZONE_PGZ_ALIGNMENT_PROBE=y
CONFIG_XNU_NATIVE_ARCH_TIMER=y
CONFIG_XNU_NATIVE_PAN=y
CONFIG_XNU_BOOT_PROGRESS=y
CONFIG_XNU_NATIVE_LEGACY_DISPLAY=y
CONFIG_XNU_NATIVE_ADRENO=y
CONFIG_XNU_CRYPTO_BOOTSTRAP="prelinked"
```

The board sets the scratch Data volume UUID:

```
CONFIG_XNU_OWNER_DATA_VOLUME_UUID="18AB5557-DC2D-469B-8758-855E60F5B0DF"
```

## GPU

The GPU path is documented in [Adreno 740 driver](/drivers/native-adreno). The board enables it with `sheng-gpu-power=9`, `sheng-gpu-metal=1` and `sheng-gpu-addon=1`.

Runtime chain: Metal, NativeMetal, metal2vulkan (AIR to SPIR-V), Turnip (SPIR-V to NIR to IR3), NativeAdreno, GMU and CP, Adreno 740, GPU composite into scanout, NativeMobileDisplay.

| Step | State |
| --- | --- |
| GMU cold start, HFI and power votes | works |
| GPU context and CP commands | works |
| Native 4 KiB SMMU context | active |
| Metal plugin discovery | works |
| GPU frame copy into scanout | works, pixel-identical |
| Render server compositing | works |
| Per-process Metal devices | works |
| GPU-composited desktop | works |

The plugin is published to backboardd with `add-gpu-plugin-data.py --publish`, so CARenderServer composites the system UI through the Adreno 740. `--clients` gives listed processes their own device and driver connection; up to two also get a GPU window. The driver compiles each UI shader variant on the device and reuses exported pipeline caches on later boots.

## Firmware

```toml
[firmware]
config = "sheng"
dsc = "Platforms/Xiaomi/shengPkg/sheng.dsc"
fd = "Build/shengPkg/{target}_CLANGPDB/FV/SILICIUM_UEFI.fd"
preflight = ["scripts/check-sheng.py"]
submodules = ["Common/Mu", "Common/Mu_OEM_Sample", "Silicium-ACPI", "Silicon/Silicium/OpensslPkg/Library/OpensslLib/openssl"]
patches = ["Resources/MuPatches/Gic-Spurious.patch"]
```

The package path list covers the Mu-Silicium tree, the UniXNU package, DarwinBoot, edk2, Mu, Mu OEM samples, Qualcomm, Silicium and ACPI.

The defines:

```toml
[firmware.defines]
ENABLE_SECUREBOOT = "1"
DEVICE_MODEL = "sheng"
MEMORY_PROTECTION = "TRUE"
SHIP_MODE = "FALSE"
BUILDID_STRING = "sheng-research"
```

## Payload

```toml
[payload]
volume = "SHENGESP"
size_mib = 192
loader = "firmware"
title = "sheng first boot: source 4K XNU to console"
dram_size = "0x80000000"
skip_setup_tool = "scripts/seed-data-skip-setup.py"
panic_screen = true
trust_cache_sha256 = [
  "7416ca4f8377146626bb284e2133c76bee6cb4e3ee0af5d648b186235a7323a7",
  "8900d6a93d7a59ce1a872a5c081e559f4240a218f97e12d44d22dda46644d68f",
]
```

The kernel arguments cover the platform, storage, display, input, GPU, diagnostics and owner root paths. The full list is in the board file.

The ADT:

```toml
[payload.adt]
tool = "scripts/make-sheng-adt.py"
chip_id = "207"
owned_memory_size = "0x130000000"
root_match_volume_uuid = "04769D26-2CA0-4825-B443-E2E5F88300F2"
cpu_regs = "0,0x100,0x200,0x300,0x400,0x500,0x600,0x700"
packed_data_ramdisk = true
ipad_identity = true
unique_chip_id = "required"
```

The boot image adds a splash region that the stock ABL expects:

```toml
[[bootimg.dtb_node]]
path = "/reserved-memory/splash_region"
props = [
  { name = "label", type = "s", value = "cont_splash_region" },
  { name = "reg", type = "x", value = ["0x0", "0xb8000000", "0x0", "0x2b00000"] },
]
```

## Build

```sh
git clone --recurse-submodules https://github.com/UniXNU/UniXNU
git clone --recurse-submodules https://github.com/UniXNU/UniXNU-sheng
git clone https://github.com/UniXNU/uefi-sheng
cd UniXNU

# For an existing clone:
git submodule update --init --recursive

./unixnu defconfig sheng_defconfig -D ../UniXNU-sheng
./unixnu fetch
./unixnu ipsw fetch
./unixnu build kernel
./unixnu build package
./unixnu build firmware --uefi ../uefi-sheng
./unixnu build payload --unique-chip-id <hex> --trust-cache <bundle> --data-ramdisk <seed>
./unixnu bootimg --uefi ../uefi-sheng --dtb <sheng.dtb>
```

The platform seed, trust cache and Data seed are device inputs. The board reports the accepted trust cache hashes.

To use the tablet's full storage, grow the Data seed with `python3 scripts/seed-data-grow.py --auto <seed>.dbr <output>.dbr`. With `sheng-data-persist=2`, the store writes through to the end of userdata, below the 1024 MiB log reserve.

## Boot

```sh
fastboot boot out/sheng/boot/boot.img
```

The first boot uses the userdata image:

```sh
./unixnu build userdata
fastboot flash userdata out/sheng/userdata/userdata-root.img
fastboot reboot bootloader
fastboot boot out/sheng/boot/boot.img
```

## macOS

The board file points at an iPadOS restore image. To boot macOS on the same board, point `[ipsw]` at a macOS restore image and update the product, version, build, device class, chip ID, board ID and member pins. Set `[userdata] windows` to `OS` and `Cryptex1,SystemOS`. The kernel, payload, boot image and userdata steps stay the same.

## Device support

| Feature | State | Notes |
| --- | --- | --- |
| Touch | ✅ | Novatek NT36532E |
| Display | ✅ | |
| UFS | ✅ | Native UFS root |
| Wi-Fi | ❌ | |
| Bluetooth | ❌ | |
| Camera | ❌ | |
| GPU | ✅ | Native Metal, GPU compositing, per-process devices and exported pipeline caches |
| USB | ❌ | |
| Audio | ❌ | |
| Sensors | ❌ | |
| Battery driver | ❌ | |
| MiPPS | ❌ | |
| Suspend and resume | ❌ | |

✅ available, ⚠️ partial, ❌ not available. The same table is in the [UniXNU-sheng README](https://github.com/UniXNU/UniXNU-sheng#device-support).

## Observed state

| Stage | State |
| --- | --- |
| Stock ABL loads the boot image and BootShim starts the UEFI firmware | works |
| Silicium UEFI and UniXNU start | works; Silicium stalls at random and a retry of the same image starts it |
| UniXNU reads the payload volume | works |
| XNU and userland | the original iPadOS userland runs from the IPSW; Setup and Hello can be skipped, and SpringBoard, the lock screen, the home screen and Settings are reached |
| Touch | accepted by SpringBoard and backboardd |
| UFS | native UFS root works |
| Desktop rendering | GPU-composited through the native Metal device; the render server and listed clients use it |
| GPU | native Metal device, GPU compositing, per-process clients and pipeline caches work |

The touch driver is documented in [Novatek touch driver](/drivers/native-novatek-touch).

## Device specifics

- The stock ABL powers the panel off when the device tree has no splash region. The boot image adds `/reserved-memory/splash_region`.
- The platform seed lives outside the repositories. Supply it with `--unique-chip-id`.
- The `sheng-pmgr=2` argument is required for the native UFS root path. The payload step refuses a kernel without the linked PMGR integration when `native-ufs-root=1`.
- The trust cache bundle must be one of the two accepted hashes.
- The Data seed is an input to the payload step.

## Next steps

- [Porting](/porting/)
- [Adreno 740 driver](/drivers/native-adreno)
- [Novatek touch driver](/drivers/native-novatek-touch)
- [Unattended test cycle](/devices/sheng-unattended-test)
- [Troubleshooting](/reference/troubleshooting)
