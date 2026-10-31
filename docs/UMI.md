# ios-sweet on the Xiaomi Mi 10 (umi)

The same kernel runs on the Mi 10 (`umi`, Snapdragon 865 / SM8250). It picks the
umi hardware at runtime from the device tree (`tools/mkadt.py --board umi` adds
`xiaomi,umi` to the root compatible). Work happens on branch `umi`; the engineering
log is the umi section at the top of `NOTES.md`.

Status (2026-10-31): iOS 16.7.16 (iPhone X userland) boots to the home screen with the stock
apps. Touch, buttons, USB Ethernet + live log, Wi-Fi in Settings (open + WPA2-PSK, 0201-0203) and
the brightness slider (0205) and auto-brightness (0213-0214) work; the Adreno 650 is being brought up. Scripts that talk to the
phone need `UMI_SERIAL` set to its serial (`fastboot devices`).

## What is not in git

| What | Where it came from | Rebuild on a new PC |
| --- | --- | --- |
| Partition backups (persist, modemst, fsg, fsc, boot, dtbo, vbmeta, recovery), live DT dumps | the phone, 2026-10-20 | **Copy `~/ios-umi-backup/` by hand.** Contains IMEI/calibration/serials: never upload it |
| `dtb/umi/dtb` | the DTB inside the stock `boot.img` | `python3 tools/unpack_bootv2.py ~/ios-umi-backup/boot.img /tmp/b && mkdir -p dtb/umi && cp /tmp/b/dtb dtb/umi/dtb` |
| `research/ipsw-x/d22ap.adt` | Apple's iPhone X device tree | `tools/extract-d22ap-adt.py` (needs pyliblzfse, see the script) |
| iOS root image | Apple's IPSW | **Not needed while the phone keeps its current `userdata`.** Otherwise see "Rebuild the iOS root" |
| Kernel | CI artifact | `gh run download RUN -R qcom-toolbox/ios-sweet -n xnu-kernel -D xnu/out-NAME` |

## Tools on a new PC

`aarch64-linux-gnu-gcc`, `mkbootimg` (or AOSP `mkbootimg.py`), `fastboot`/`adb`, `gh`
logged in to the fork's account, Python 3. For the root image only: `hfsprogs`,
`apfs-fuse` (built from source: `cmake -DCMAKE_POLICY_VERSION_MINIMUM=3.5
-DCMAKE_CXX_FLAGS="-include cstdint"`), `img2simg`.

## Build and boot

```sh
gh workflow run xnu.yml -R qcom-toolbox/ios-sweet --ref umi        # ~40 min on macOS runners
gh run download RUN -R qcom-toolbox/ios-sweet -n xnu-kernel -D xnu/out-latest
tools/umi-boot-image.sh xnu/out-latest/kernel.development.sweet umi.img          # touch + keys
tools/umi-boot-image.sh xnu/out-latest/kernel.development.sweet umi-usb.img sweetusb=2   # + USB Ethernet
fastboot boot umi.img
```

Nothing is flashed by `fastboot boot`. The lock screen appears after ~1-2 minutes;
touch starts ~45 s after the kernel finds the UFS root.

## Reading the kernel log

- From TWRP (any normal reboot lands there, because Android has no data):
  `tools/sweet-log-pull.sh research/logs/NAME.txt` (reads the last 4 MiB of userdata).
- Live over USB (boot-arg `sweetusb=2`, works since 0114): on Linux `tools/sweet-usbnet.sh research/logs/NAME.txt`.
  On macOS the phone appears as an AppleUserECM interface with MAC 02:00:5e:77:ee:01 (`ifconfig` shows which enN);
  give it the host address with `sudo ifconfig enN inet 192.168.7.1 netmask 255.255.255.0 alias`, then
  `ping 192.168.7.2` and `nc -ul 5140 >> research/logs/NAME.txt` for the live console.
- Symbolicate user-space addresses: mount the SystemOS cryptex read-only with
  `apfs-fuse -o ro`, then `ipsw dyld a2s .../dyld_shared_cache_arm64 <addr - slide>`.

## Phone handling

- **USB:** use a rear port and a good cable. Front-panel ports gave `error -71` and failed
  bulk transfers. A low battery also breaks fastboot transfers: charge before flashing.
- **Restart into:** fastboot = Power + Volume down, TWRP = Power + Volume up.
- **In TWRP never "Format Data" or wipe:** `userdata` holds the iOS root.
- After `fastboot flash`, the bootloader answers nothing until it is restarted.

## Rebuild the iOS root (erases userdata)

README step 2 with `tools/mkiosroot.sh` and `tools/sweet-root-tweaks.py`. The three
images for D22AP 20H392 are OS `087-86698-044.dmg`, SystemOS `087-86593-047.dmg`,
AppOS `087-86715-047.dmg` (`tools/remotezip.py IPSW NAME DIR` fetches one member).
The Linux `fsck_hfs` "Volume header needs minor repair" message after a successful
repair is expected. Flash with `fastboot -S 512M flash userdata ios16-root.img`
(the raw image; `-S` on a `.simg` fails with "Error reading sparse file").
