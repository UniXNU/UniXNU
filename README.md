# ios-sweet

**Apple's iOS 16 running on a Xiaomi Mi 10.**

This project ports Apple's open-source XNU kernel (xnu-8796, the iOS 16 generation) to the Xiaomi Mi 10 (`umi`, Qualcomm SM8250 / Snapdragon 865). On top of it runs the **unmodified iOS 16.7.16 (20H392) userland of the iPhone X**: launchd, the system daemons, backboardd, SpringBoard and the stock apps.

As of **2026-10-31** the phone boots to the **iOS home screen** with the stock apps. Touch, the buttons, Wi-Fi in Settings (open and WPA2 networks), the brightness slider and auto-brightness work, the battery shows its real charge, and the Adreno 650 GPU is being brought up.

> Experimental bring-up, not a usable phone OS. Many things are missing or stubbed (see below), and Apple's security model is mostly switched off. It installs into the `userdata` partition and so **erases Android's user data**.

The project started on the Redmi Note 10 Pro (`sweet`, SM7150), hence its name; the same kernel still boots there (home screen, touch, buttons, no Wi-Fi). It picks the board at runtime from the device tree. The `sweet` steps are in the git history and [`NOTES.md`](NOTES.md).

## What works

| Area | State |
| --- | --- |
| Boot | Stock Xiaomi bootloader → `fastboot boot` of our shim → XNU. The shim image can also be flashed to `boot` so iOS starts on its own |
| CPU | All 8 cores (4× Cortex-A55, 3× A77, 1× A77 prime) via PSCI, 16K pages, GICv3 interrupts, timers |
| Storage | Own UFS host driver; the iOS root is a journaled HFS+ volume in `userdata`, read/write |
| iOS userland | Real iPhone X 16.7.16 root filesystem and shared cache; launchd, the system daemons and the 31 removable stock apps |
| Display | Kernel IOSurface + IOMobileFramebuffer (`AppleCLCD`) services; CoreAnimation frames go to the 1080×2340 AMOLED panel. Presented to iOS as an iPhone X panel (1125×2436) |
| Brightness | `AppleARMBacklight` for CoreBrightness; the Control Center and Settings slider set the panel level with DCS 0x51 over DSI; the panel goes dark on lock and comes back with the power button; auto-brightness from the ambient light sensor (SLPI firmware booted by the kernel, read through QRTR/SEE) |
| Night Shift | iOS's display color matrix goes to the display controller's color correction (DSPP PCC) |
| GUI | backboardd, SpringBoard, lock screen, home screen, Control Center, notification center, Settings, wallpapers |
| Touch | ST FTM5 over I²C (GENI with GPI DMA), delivered as HID digitizer events |
| Buttons | Power, volume up/down (PMIC through SPMI) as HID keys; lock/wake works |
| Battery | IOPMPowerSource from the PM8150B fuel gauge: real percentage, voltage, current and charging state |
| Wi-Fi | QCA6390 over PCIe + MHI with an in-kernel driver (firmware boot, WMI, data path, WPA2-PSK handshake); wifid and Settings scan and join open and WPA2-PSK networks on 2.4 GHz |
| Audio | The ADSP (booted by the kernel, APR to its AFE / ASM / ADM services) plays through tertiary MI2S (SD1) into the two CS35L41 amps; iOS's audio server reaches it through our `SweetAudio.driver` HAL plug-in and `/dev/sweet-audio` (`sweetadsp=1 sweetamp=1 sweetaudio=1`); ringtones and system sounds play from the speaker, ~3.5 min after boot |
| Location | Works: Wi-Fi positioning (Weather shows the city for My Location; Maps asks for permission), since fairplayd.H2 was taken out of launchd's job list. No GPS receiver yet |
| USB | ECM gadget (USB Ethernet) with a live kernel log and a small kernel file server for development |
| GPU | Adreno 650 powered through GMU/RPMh, zap shader authenticated by TrustZone, command processor running our command streams; a Metal path over Mesa's turnip is experimental (`sweetmtl`) |
| Device identity | iPhone X (`iPhone10,3` / `D22AP`): no Home button, gesture UI |
| Activation | Native "Hactivation" path of mobileactivationd, chosen through device-tree security status. No Apple servers involved |

## What does not work (yet)

- **No Bluetooth, cellular, camera, motion sensors or SEP / Face ID**, and no GPS receiver (location itself works, from Wi-Fi). Daemons for them start and fail or keep relaunching.
- **No True Tone**: the light sensor reports brightness only, not color.
- **No microphones** yet, and the earpiece speaker is not used as a second channel.
- **No hardware video decoding** (VideoToolbox / AVD), so videos do not play; music apps never reached the audio system in tests.
- **Wi-Fi** is 2.4 GHz only, legacy rates, no WPA3.
- **GPU** rendering is not reliable yet (fence timeouts); CoreAnimation mostly renders on the CPU.
- **No App Store, no Apple ID.**
- **Security is off:** permissive code signing (AMFI) and sandbox policies, a stub AppleKeyStore, no data protection. Do not put anything personal on it.

## Status and to do

Feature by feature, with what is missing and planned next: [`Status.md`](Status.md).

## How it boots

```
ABL (stock Xiaomi bootloader, unlocked)
  -> fastboot boot umi.img                     (temporary; or flashed to boot)
     -> shim: own MMU setup, reads the live FDT, loads the payload from the ramdisk
        -> XNU Mach-O + generated Apple Device Tree (ADT) + boot-args
           -> XNU -> UFS driver -> HFS+ root in the userdata partition
              -> dyld + shared cache -> launchd -> daemons -> backboardd + SpringBoard
```

The kernel draws its console into the framebuffer that ABL leaves at `0x9c000000`, keeps a persistent 4 MiB log ring at the end of `userdata`, and with `sweetusb=2` streams it live over USB Ethernet.

## How to do it yourself

You need a Xiaomi Mi 10 (`umi`) with an **unlocked bootloader**, a Mac or Linux PC, and a GitHub account for the kernel build. **Everything on `userdata` is lost.** Bootloaders, recovery, modem and persist partitions are never touched. The detailed Mi 10 notes are in [`docs/UMI.md`](docs/UMI.md).

### 0. Back up the phone

Boot TWRP (or any recovery with adb root) temporarily and pull at least `persist`, `modemst1`, `modemst2`, `fsg`, `fsc` and `boot`, `dtbo`, `vbmeta`. They contain per-device calibration data and identifiers. Keep them off git.

The shim needs the stock DTB. Unpack your phone's stock `boot.img`:

```sh
python3 tools/unpack_bootv2.py backup/boot.img /tmp/b && mkdir -p dtb/umi && cp /tmp/b/dtb dtb/umi/dtb
```

### 1. Build the kernel

The kernel builds on GitHub's macOS runners with [blacktop/darwin-xnu-build](https://github.com/blacktop/darwin-xnu-build). The workflow fetches xnu-8796, applies `xnu/patches/` in order, and also stages the pinned open-source libpthread, HFS and BearSSL sources it needs. Fork the repo (public repos get free macOS minutes) and run:

```sh
gh workflow run xnu.yml -R YOU/ios-sweet
gh run download RUN_ID -R YOU/ios-sweet -n xnu-kernel -D xnu/out
```

Once you have the CI build tree, `tools/build-kernel-local.sh` rebuilds incrementally on a Mac (see its header).

### 2. Build the iOS root image

Download the iPhone X (iPhone10,3) iOS 16.7.16 (20H392) IPSW from Apple. Then, on Linux, with `apfs-fuse`, `hfsprogs` and sudo:

```sh
# OS, SystemOS and AppOS disk images from the IPSW (see BuildManifest.plist for their names)
tools/mkiosroot.sh OS.dmg SystemOS.dmg AppOS.dmg ios16-root.img 16G
sudo fsck.hfsplus -fy ios16-root.img
sudo mount -t hfsplus -o loop,force ios16-root.img /mnt/iosroot
sudo python3 tools/sweet-root-tweaks.py /mnt/iosroot
sudo umount /mnt/iosroot
```

`mkiosroot.sh` copies the OS volume and both cryptexes into one case-sensitive journaled HFS+ volume. It adds the dyld cache links, the plain system keybag and the log directories the daemons expect. `sweet-root-tweaks.py` applies the bring-up changes: it skips Setup, seeds the activation state, removes the baseband daemon, disables the watchdogs that kill slow apps, and so on. The script's header explains each change.

The device tree builder copies `/product` from the real iPhone X device tree, which MobileGestalt needs: `tools/extract-d22ap-adt.py` extracts it (see the script).

### 3. Build the boot image

Needs `aarch64-linux-gnu-gcc` (or the LLVM wrappers described in `NOTES.md`) and `mkbootimg`.

```sh
tools/umi-boot-image.sh xnu/out/kernel.development.sweet umi.img                # touch, keys, 8 cores
tools/umi-boot-image.sh xnu/out/kernel.development.sweet umi-usb.img sweetusb=2   # + USB Ethernet / live log
```

What the less obvious boot-args do:

| Boot-arg | Effect |
| --- | --- |
| `rd=ufsroot0 ufsrw=1 rootrw=1` | Root on the `userdata` partition, writable |
| `cpus=8` | Start all eight cores; `cpus=1` is the safe fallback |
| `launchd_unsecure_cache=1` | launchd accepts its job cache without AMFI |
| `wdt=-1 wdt_test=no_user_checkin` | No hardware watchdog |
| `sweetfb_noconsole=1` | Stop drawing kernel text over the GUI. It still goes to the persistent log; panics are drawn |
| `sweetusb=2` | USB Ethernet gadget with the live log (UDP port 5140) and the file server |
| `sweetwlan=8 sweetwlanssid=NAME` | Bring up the QCA6390; optionally join a network at boot (`_` = space) |
| `sweetbattery=2` | Real fuel-gauge readings |
| `sweetbl=0`, `sweetbl_maxnits=N` | Backlight service off; nits of the top panel level (default 420) |
| `sweetsample=name,...` | Print user stack samples of these processes (16-character names) |

### 4. Flash the root and boot

```sh
fastboot -S 512M flash userdata ios16-root.img   # the raw image; do not unplug
# Xiaomi's fastboot often hangs after a large flash: re-enter fastboot with Power + Volume down
fastboot boot umi.img                            # send it again if the first one does not take
```

The lock screen appears after about 1–2 minutes. Swipe up to unlock. To get back to fastboot, hold Power + Volume down. Plug the phone straight into the computer: USB hubs drop it.

### 5. Read the kernel log

- **Live (USB Ethernet, `sweetusb=2`):** on a Mac run `sudo tools/umi-usbnet.sh` after each boot (gives the host 192.168.7.1), then receive UDP port 5140 with a small Python receiver (`nc` drops the stream when the phone's source port changes). `tools/umi-files.py get/put/rm/list` reads and writes phone files over the same link.
- **From TWRP:** `tools/umi-log-pull.sh NAME` reads the persistent ring from the end of `userdata` (export `UMI_SERIAL` first).

The log contains crash reports with backtraces (`CRASH name ...`), IOKit traces, and the drivers' `SWEET ...` lines. `tools/sweet-crash.py` symbolicates them against the shared cache.

## Repository layout

| Path | What |
| --- | --- |
| `shim/` | Bare-metal boot shim (C + asm) packed as an Android boot.img v2 |
| `xnu/patches/` | The XNU patch series (applied in order by CI), plus staging scripts for libpthread, HFS and BearSSL |
| `.github/workflows/xnu.yml` | Kernel CI build |
| `tools/mkadt.py` | Generates the Apple Device Tree from the board's MMIO layout and the iPhone X identity (`--board umi`) |
| `tools/mkpayload.py` | Packs kernel + ADT + boot-args into the shim payload |
| `tools/umi-boot-image.sh` | Kernel → bootable `umi.img` |
| `tools/build-kernel-local.sh` | Incremental local kernel build on a Mac |
| `tools/mkiosroot.sh`, `sweet-root-tweaks.py` | Build the HFS+ iOS root from the IPSW images and apply the bring-up changes |
| `tools/umi-usbnet.sh`, `umi-files.py`, `umi-log-pull.sh` | Live log, phone files, persistent log |
| `tools/sweet-crash.py` | Symbolicate console crash reports |
| `docs/UMI.md` | Mi 10 build, boot and phone-handling notes; `docs/GPU-HANDOFF.md` for the GPU work |
| `NOTES.md` | Detailed engineering log: every boot, crash and decision, plus hardware facts |

Not in git: partition backups, live device trees, recovery images, Apple firmware and root images, Wi-Fi/GPU firmware pulled from the phone, and downloaded or generated build trees. They contain device identifiers and calibration data, or Apple's and Qualcomm's copyrighted files.

## Kernel patches

| # | What |
| --- | --- |
| 0001–0034 | Toolchain compatibility, SWEET machine config, non-PAC arm64, early framebuffer console, device-tree platform expert, libpthread and BearSSL, RAM-disk root, minimal AMFI, HFS+, UFS host driver and read/write root |
| 0035–0069 | Entitlements, AppleKeyStore stub, IOWatchdog, IOSurface + IOMobileFramebuffer, diagnostics (persistent log, IOKit trace, stack sampler), Sandbox policy, HID events, iPhone X identity, SMP |
| 0070–0082 | USB ECM gadget and live log, 8 cores, display power, GIC clean slate |
| 0083–0112 | Mi 10 touch (FTM5 over GENI + GPI DMA), keys, PMIC boost rail, direct scanout through the display SMMU, USB on umi, IOKit quiesce |
| 0113–0154 | QCA6390 Wi-Fi: PCIe, MHI firmware boot, QMI/WLFW, copy engines, HTC/WMI, scan, join, data path, DHCP, BSD interface, IOKit entries |
| 0155–0159 | Battery (PM8150B fuel gauge), LaunchServices/MobileGestalt resets, AMFI policy interface (wallpapers) |
| 0160–0200 | Adreno 650 bring-up: GMU, RPMh, SMMU, zap shader via TrustZone, command processor, buffer objects and fences, user client for Mesa |
| 0201–0203 | Apple80211 for wifid (from ios-flame / HackiOS), the QCA6390 as wifid's station, WPA2-PSK |
| 0204–0207 | File server LIST; backlight (CoreBrightness → DCS 0x51 over DSI); panel dark while the display is off; Night Shift through the MDP's PCC |
| 0208–0214 | SLPI sensor DSP: firmware boot via TrustZone, SMEM/SMP2P/GLINK, QRTR and service locator, FastRPC config server, SEE ambient light client, Apple ALS HID service for auto-brightness |

## Key hardware facts (Mi 10)

- SoC SM8250: 4× A55 + 4× A77 brought up through PSCI `CPU_ON`; GICv3, 19.2 MHz timer, ARMv8.2 without pointer authentication.
- Panel: Samsung AMOLED 1080×2340, DSC command mode on DSI0 (`0xae94000`) with MDP autorefresh left on by ABL; brightness is DCS 0x51, 11-bit big-endian (2..2047). The display SMMU context does not translate.
- Touch: ST FTM5 on GENI I²C with GPI DMA; needs the PM8150B GPIO 5 boost rail.
- Buttons: PON block on PM8150 over SPMI (PMIC arbiter v5).
- Wi-Fi: QCA6390 on PCIe0, MHI + QMI firmware handshake, ath11k-style host rings.
- GPU: Adreno 650 (chip 6.5.0.2) behind GMU 0x3d6a000; the hypervisor only accepts the device tree's own SMMU stream pairs.

More in [`NOTES.md`](NOTES.md) and [`docs/UMI.md`](docs/UMI.md).

## Credits

Built on Apple's open-source releases (xnu, IOHIDFamily, libpthread, hfs), [BearSSL](https://bearssl.org), [blacktop/darwin-xnu-build](https://github.com/blacktop/darwin-xnu-build), [ipsw](https://github.com/blacktop/ipsw), Qualcomm/Xiaomi's published Linux kernel sources and mainline Linux (msm DRM/DSI, ath11k, MHI, freedreno) for the hardware details, [Mesa](https://mesa3d.org) (freedreno / turnip), HackiOS by OOSEX GANG (Adreno bring-up base, Apple80211 code, APSL 2.0), [ios-flame](https://github.com/NWylynko/ios-flame) (Pixel 4 port, Wi-Fi integration), the original `sweet` port's contributors, and [TWRP](https://twrp.me) / [OrangeFox Recovery](https://orangefox.download). iOS itself is Apple's and is not distributed here.

## License

MIT for this repository's own code and docs ([`LICENSE`](LICENSE)). The XNU patches in `xnu/patches/` modify
Apple's APSL 2.0 kernel and stay under the APSL 2.0; staged and third-party code keeps its own license. No Apple
software is included.
