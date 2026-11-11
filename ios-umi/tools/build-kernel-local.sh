#!/bin/bash
# tools/build-kernel-local.sh: build kernel.development.sweet on this Mac (no CI, no Xcode 15).
#
# One-time setup (already done on this Mac; the parts are in xnu-work/):
#   - bt/            the CI "buildtree" artifact: patched xnu source (the git repo, patches 0001-01NN)
#                    + build/xnu.obj with every generated file (mig, iig, yacc, installhdrs exports)
#   - work/dtrace    apple-oss dtrace-397, built with xcodebuild: ctfconvert/ctfmerge/ctfdump
#                    -> bt/fakeroot/usr/local/bin (Xcode 27 is fine: host tools)
#   - work/libdispatch  apple-oss libdispatch-1415.140.2, libfirehose_kernel target, arm64, with
#                    xcodeconfig/libfirehose_kernel.xcconfig header search paths pointed at the
#                    buildtree (EXPORT_HDRS, EXTERNAL_HEADERS, Kernel PrivateHeaders symlinks into
#                    bt/xnu) and the KERNEL-variant firehose headers (work/firehose-kernel-hdrs)
#                    -> bt/fakeroot/usr/local/lib/kernel/libfirehose_kernel.a
#   - libcc_kext.a   copied from the toolchain's libclang_rt.cc_kext.a (the 27 SDK dropped
#                    Kernel.framework/Libraries) -> bt/fakeroot/usr/local/lib/kernel
#   - kdk/KDKROOT    KDK 13.5 22G74, unpacked from the public dortania mirror (pkgutil expand +
#                    pbzx decode + cpio, no sudo): System/Library/KernelSupport libs
#   - bt/build/xnu.obj  all /Users/runner/... CI paths rewritten to the local bt/ and every file
#                    touched (nothing regenerates, so Xcode 27's incompatible iig never runs)
#
# The build is incremental: edit the source under bt/xnu (git commits happen there), re-run,
# only what changed recompiles. The kernel lands in
#   bt/build/xnu.obj/DEVELOPMENT_ARM64_SWEET/kernel.development.sweet
set -eu
XW=$HOME/ios-sweet-port/xnu-work
cd "$XW/bt/xnu"
make install -j16 VERBOSE=YES \
    CTFCONVERT="$XW/bt/fakeroot/usr/local/bin/ctfconvert" \
    CTFMERGE="$XW/bt/fakeroot/usr/local/bin/ctfmerge" \
    CTFDUMP="$XW/bt/fakeroot/usr/local/bin/ctfdump" \
    SDKROOT="$(xcrun --sdk macosx --show-sdk-path)" \
    TARGET_CONFIGS="DEVELOPMENT ARM64 SWEET" \
    CONCISE=0 BUILD_WERROR=0 BUILD_LTO=0 \
    SRCROOT="$XW/bt/xnu" OBJROOT="$XW/bt/build/xnu.obj" SYMROOT="$XW/bt/build/xnu.sym" \
    DSTROOT="$XW/work/dst" FAKEROOT_DIR="$XW/bt/fakeroot" KDKROOT="$XW/kdk/KDKROOT" \
    TIGHTBEAMC=tightbeamc-not-supported RC_DARWIN_KERNEL_VERSION=22.6.0 "$@"
echo
ls -la "$XW/bt/build/xnu.obj/DEVELOPMENT_ARM64_SWEET/kernel.development.sweet"
