#!/bin/bash
# phone/build-gpu-test.sh: cross-compile sweet-gpu-test for the phone's iOS user space
# (iPhoneOS SDK, arm64, ad-hoc code signature with ldid: the SWEET AMFI policy makes signed
# root binaries platform binaries) and install it with tools/umi-files.py.
set -eu
cd "$(dirname "$0")/.."
sdk=$(xcrun --sdk iphoneos --show-sdk-path)
clang -arch arm64 -isysroot "$sdk" -miphoneos-version-min=16.0 \
    -framework IOKit -framework CoreFoundation \
    -o phone/out/sweet-gpu-test phone/sweet-gpu-test.c -Iphone
mkdir -p phone/out
/opt/local/bin/ldid -S phone/out/sweet-gpu-test
echo "built phone/out/sweet-gpu-test"
if [ "${1:-}" = install ]; then
	tools/umi-files.py mkdir /private/var/sweet 755
	tools/umi-files.py put phone/out/sweet-gpu-test /private/var/sweet/sweet-gpu-test 755
	tools/umi-files.py put phone/com.sweet.gputest.plist /System/Library/LaunchDaemons/com.sweet.gputest.plist 644
	echo "installed on the phone: /private/var/sweet/sweet-gpu-test + the LaunchDaemon (runs at the next boot)"
fi
