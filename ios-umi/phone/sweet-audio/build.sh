#!/bin/bash
# phone/sweet-audio/build.sh: build SweetAudio.driver (the umi speaker for iOS's audio server, an AudioServerPlugIn
# talking to the kernel's /dev/sweet-audio) for the phone's iOS 16 user space: iPhoneOS SDK, arm64, ad-hoc code
# signature with ldid (the SWEET AMFI policy makes signed root binaries platform binaries).
#   phone/sweet-audio/build.sh            -> phone/out/SweetAudio.driver
#   phone/sweet-audio/build.sh install    -> also put it in /System/Library/Audio/Plug-Ins/HAL/ (tools/umi-files.py)
set -eu
cd "$(dirname "$0")/../.."
sdk=$(xcrun --sdk iphoneos --show-sdk-path)
out=phone/out/SweetAudio.driver
rm -rf "$out"
mkdir -p "$out"
clang -arch arm64 -isysroot "$sdk" -miphoneos-version-min=16.0 -O2 -Wall -Wextra -bundle \
    -framework CoreFoundation -o "$out/SweetAudio" phone/sweet-audio/SweetAudio.c
cp phone/sweet-audio/Info.plist "$out/Info.plist"
/opt/local/bin/ldid -S "$out/SweetAudio"
echo "built $out"
if [ "${1:-}" = install ]; then
	hal=/System/Library/Audio/Plug-Ins/HAL/SweetAudio.driver
	tools/umi-files.py rm "$hal/SweetAudio" 2>/dev/null || true
	tools/umi-files.py rm "$hal/Info.plist" 2>/dev/null || true
	tools/umi-files.py mkdir "$hal" 755
	tools/umi-files.py put "$out/Info.plist" "$hal/Info.plist" 644
	tools/umi-files.py put "$out/SweetAudio" "$hal/SweetAudio" 755
	echo "installed $hal (loaded by mediaserverd at its next start)"
fi
