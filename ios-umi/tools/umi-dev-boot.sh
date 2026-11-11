#!/bin/bash
# tools/umi-dev-boot.sh K TAG [extra boot-args]: build kernel out-K into shim/out/umi-K-TAG.img and fastboot boot it
set -eu
SP=${SWEET_TOOLBIN:?set SWEET_TOOLBIN to the dir holding bin/ (aarch64-linux-gnu-gcc wrapper, mkbootimg)}
export PATH="$SP/bin:$PATH" ANDROID_SERIAL=${UMI_SERIAL:?set UMI_SERIAL to the phone serial shown by fastboot devices}
cd "$(dirname "$0")/.."
K=$1 TAG=$2; shift 2
base='debug=0xc serial=3 cpus=8 keepsyms=1 -enable_kprintf_spam -noprogress rd=ufsroot0 unentitled_ios_sim_launch=1 ignition_level=1 wdt_test=no_user_checkin ufsrw=1 rootrw=1 launchd_unsecure_cache=1 wdt=-1 sweetfb_noconsole=1 sweetfb_hz=30 sweetfb_direct=1 ufslogsecs=2'
kern=$(find xnu/out-$K -name 'kernel.development.sweet' | head -1)
python3 tools/mkpayload.py "$kern" shim/out/umi.adt shim/out/payload-$TAG.bin --cmdline "$base $*" >/dev/null
BOARD=umi bash shim/build.sh ../shim/out/payload-$TAG.bin >/dev/null 2>&1
cp shim/out/shim-boot.img shim/out/umi-$K-$TAG.img
if adb get-state >/dev/null 2>&1; then adb reboot bootloader; fi
for i in $(seq 1 60); do fastboot devices 2>/dev/null | grep -q ${UMI_SERIAL} && break; sleep 2; done
fastboot -s ${UMI_SERIAL} boot shim/out/umi-$K-$TAG.img 2>&1 | tail -1
