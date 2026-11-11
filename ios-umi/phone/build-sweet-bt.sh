#!/bin/bash
# phone/build-sweet-bt.sh: build libsweet-bt.dylib (phone/sweet-bt/sweet_bt_inject.c) for the phone's iOS user space
# (iPhoneOS SDK, arm64, ad-hoc signed with ldid) and, with "install", put it on the phone as
# /usr/local/lib/libsweet-bt.dylib through tools/umi-files.py (rm before put, read back and compared).
# The kernel inserts it with boot-arg sweetinject=/usr/local/lib/libsweet-bt.dylib,bluetoothd,BlueTool (sweetbt=6).
set -eu
cd "$(dirname "$0")/.."
sdk=$(xcrun --sdk iphoneos --show-sdk-path)
mkdir -p phone/out
xcrun --sdk iphoneos clang -arch arm64 -isysroot "$sdk" -miphoneos-version-min=16.0 \
    -O2 -Wall -Wextra -Werror -dynamiclib -install_name /usr/local/lib/libsweet-bt.dylib \
    -framework IOKit -framework CoreFoundation \
    -o phone/out/libsweet-bt.dylib phone/sweet-bt/sweet_bt_inject.c
/opt/local/bin/ldid -S phone/out/libsweet-bt.dylib
echo "built phone/out/libsweet-bt.dylib"
if [ "${1:-}" = install ]; then
	tools/umi-files.py mkdir /usr/local/lib 755 || true
	tools/umi-files.py rm /usr/local/lib/libsweet-bt.dylib || true
	tools/umi-files.py put phone/out/libsweet-bt.dylib /usr/local/lib/libsweet-bt.dylib 755
	tools/umi-files.py get /usr/local/lib/libsweet-bt.dylib phone/out/libsweet-bt.readback
	cmp phone/out/libsweet-bt.dylib phone/out/libsweet-bt.readback
	echo "installed and read back: /usr/local/lib/libsweet-bt.dylib"
fi
