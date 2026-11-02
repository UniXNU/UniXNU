#!/bin/bash
# Build a Mi 10 (umi) boot image: ADT + kernel payload + shim, for `fastboot boot`.
#   tools/umi-boot-image.sh KERNEL OUT.img [EXTRA BOOT-ARGS...]
# Needs dtb/umi/dtb (from the phone's stock boot.img, see docs/UMI.md),
# research/ipsw-x/d22ap.adt (tools/extract-d22ap-adt.py), aarch64-linux-gnu-gcc
# and mkbootimg. Extra boot-args are appended, e.g. sweetusb=2 or sweettouch=0.
set -euo pipefail
[[ $# -ge 2 ]] || { sed -n '2,6p' "$0"; exit 2; }
kernel=$(realpath "$1") out=$(cd "$(dirname "$2")" && pwd)/$(basename "$2")
shift 2
cd "$(dirname "$0")/.."
[[ -f dtb/umi/dtb ]] || { echo "missing dtb/umi/dtb" >&2; exit 1; }
[[ -f research/ipsw-x/d22ap.adt ]] || echo "warning: no research/ipsw-x/d22ap.adt, ADT without /product" >&2

# The boot that reaches the iOS lock screen with touch and keys (NOTES.md, umi section).
cmdline='debug=0xc serial=3 cpus=8 keepsyms=1 -enable_kprintf_spam -noprogress rd=ufsroot0'
cmdline+=' unentitled_ios_sim_launch=1 ignition_level=1 wdt_test=no_user_checkin ufsrw=1 rootrw=1'
cmdline+=' launchd_unsecure_cache=1 wdt=-1 sweetfb_noconsole=1 sweetfb_hz=30 sweetfb_direct=1'
cmdline+=" ${*:-sweetusb=0}"
# shim/loader.c BOOT_LINE_LENGTH 608 (XNU's limit): a longer line loses its last arguments silently
if [ ${#cmdline} -gt 607 ]; then
	echo "boot-args are ${#cmdline} characters, the limit is 607: drop some" >&2
	exit 1
fi

mkdir -p shim/out
python3 tools/mkadt.py shim/out/umi.adt --highmem --board umi
python3 tools/mkpayload.py "$kernel" shim/out/umi.adt shim/out/payload-umi.bin --cmdline "$cmdline"
BOARD=umi shim/build.sh ../shim/out/payload-umi.bin >/dev/null
cp shim/out/shim-boot.img "$out"
echo "$out"
echo "boot-args: $cmdline"
