#!/bin/bash
# phone/build-sweet-telephonyd.sh: build sweet-telephonyd (phone/sweet-telephonyd/sweet_telephonyd.m), the stand-in for
# CommCenter, for the phone's iOS user space (iPhoneOS SDK, arm64, ad-hoc signed with ldid) and, with "install", put it
# on the phone as /usr/local/bin/sweet-telephonyd through tools/umi-files.py (rm before put, read back and compared).
# Its launchd job: phone/sweet-telephonyd/com.sweet.telephonyd.plist (installed with tools/patch-launchd-plist.py).
set -eu
cd "$(dirname "$0")/.."
sdk=$(xcrun --sdk iphoneos --show-sdk-path)
mkdir -p phone/out
xcrun --sdk iphoneos clang -arch arm64 -isysroot "$sdk" -miphoneos-version-min=16.0 \
    -O2 -Wall -Wextra -Werror -Wno-unused-parameter -fobjc-arc \
    -framework Foundation \
    -o phone/out/sweet-telephonyd phone/sweet-telephonyd/sweet_telephonyd.m
/opt/local/bin/ldid -S phone/out/sweet-telephonyd
echo "built phone/out/sweet-telephonyd"
if [ "${1:-}" = install ]; then
	tools/umi-files.py mkdir /usr/local/bin 755 || true
	tools/umi-files.py rm /usr/local/bin/sweet-telephonyd || true
	tools/umi-files.py put phone/out/sweet-telephonyd /usr/local/bin/sweet-telephonyd 755
	tools/umi-files.py get /usr/local/bin/sweet-telephonyd phone/out/sweet-telephonyd.readback
	cmp phone/out/sweet-telephonyd phone/out/sweet-telephonyd.readback
	echo "installed and read back: /usr/local/bin/sweet-telephonyd"
fi
