#!/usr/bin/env python3
"""Build the owner-signed Adreno userspace pieces for ARM64/iOS 17: the Metal plugin bundle (drivers/AdrenoMetal/NativeAdrenoMetalPlugin.mm)
and the launchd probe daemon with its job plist (NativeAdrenoProbeDaemon.cpp).

Output (ignored, never committed): build/adreno-metal-plugin/NativeAdrenoMetal.bundle with a 4 KiB-page ad-hoc signature, and
trust.json with its CDHash. The bundle is staged into the Data seed by add-gpu-plugin-data.py and trusted through an extra
owner trust module (make-owner-trust-bundle.py); neither changes the original trust modules, AMFI or any Apple signature."""
import argparse
import json
import plistlib
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# --target ios27: the arm64e build for iPadOS 27 (24A446), whose render server is an arm64e process.
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--target', choices=('ios', 'ios27'), default='ios')
parser.add_argument('--no-replay', action='store_true', help='omit the optional host simulation capture used by diagnostic probes')
args = parser.parse_args()
IOS27 = args.target == 'ios27'
OUT = ROOT / ('build/adreno-metal-plugin27' if IOS27 else 'build/adreno-metal-plugin')
bundle = OUT / 'NativeAdrenoMetal.bundle'
if OUT.exists():
    shutil.rmtree(OUT)
bundle.mkdir(parents=True)
sdk = subprocess.check_output(['xcrun', '--sdk', 'iphoneos', '--show-sdk-path'], text=True).strip()
base = ['xcrun', 'clang', '-target', 'arm64e-apple-ios27.0' if IOS27 else 'arm64-apple-ios17.0', '-isysroot', sdk, '-O2', '-g', '-Wall', '-Wextra', '-Werror',
        '-fstack-protector-strong']
VULKAN_INCLUDE = ROOT / '.cache/mesa-work/include'
TURNIP = ROOT / ('build/mesa-tu-ios27' if IOS27 else 'build/mesa-tu-ios') / 'src/freedreno/vulkan/libvulkan_freedreno.dylib'
if not TURNIP.is_file():
    raise SystemExit('Build Turnip first: python3 scripts/build-turnip-darwin.py --target ' + ('ios27' if IOS27 else 'ios'))
subprocess.run(['python3', ROOT / 'scripts/gen-turnip-smoke-shaders.py'], check=True)
# Turnip's first submission, recorded on the host, for the plugin's prefix replay (build/turnip-smoke/TurnipReplay.h).
if args.no_replay:
    (ROOT / 'build/turnip-smoke/TurnipReplay.h').unlink(missing_ok=True)
else:
    subprocess.run(['python3', ROOT / 'scripts/gen-turnip-replay.py'], check=True)
BRIDGE_TARGET = 'ios27' if IOS27 else 'ios'
subprocess.run(['python3', ROOT / 'scripts/build-adreno-metal-bridge.py', '--target', BRIDGE_TARGET], check=True)
BRIDGE = ROOT / 'build/adreno-metal-bridge' / BRIDGE_TARGET / 'libadreno_metal_bridge.a'
# arm64e: the Rust objects' imports that take a callback go through the signing wrappers of RustPacBoundary.c, and their indirect branches
# are routed through its stripping trampolines after the link (scripts/rust-pac-rewrite.py).
link_extra, PAC_RENAMES = [], {'_pthread_create': '_nmb_pac_pthread_create', '__tlv_atexit': '_nmb_pac_tlv_atexit',
                               '_atexit': '_nmb_pac_atexit', '__dyld_register_func_for_add_image': '_nmb_pac_dyld_register_func_for_add_image',
                               '__Unwind_Backtrace': '_nmb_pac_Unwind_Backtrace', '_dlsym': '_nmb_pac_dlsym'}
if IOS27:
    objcopy = next(p for p in ['/opt/homebrew/opt/llvm/bin/llvm-objcopy', shutil.which('llvm-objcopy') or ''] if p and Path(p).exists())
    pac_bridge = OUT / 'libadreno_metal_bridge_pac.a'
    subprocess.run([objcopy, *[f'--redefine-sym={a}={b}' for a, b in PAC_RENAMES.items()], BRIDGE, pac_bridge], check=True)
    BRIDGE = pac_bridge
    boundary = OUT / 'RustPacBoundary.o'
    subprocess.run([*base, '-std=c11', '-I', VULKAN_INCLUDE, '-c', ROOT / 'drivers/AdrenoMetal/bridge/RustPacBoundary.c', '-o', boundary],
                   check=True)
    link_extra = [boundary, '-Wl,-map,' + str(OUT / 'NativeAdrenoMetal.map')]
pm4 = OUT / 'AdrenoPM4.o'
subprocess.run([*base, '-std=c11', '-c', ROOT / 'kits/AdrenoPM4/AdrenoPM4.c', '-o', pm4], check=True)
exe = bundle / 'NativeAdrenoMetal'
# The OS image's .metallib paths (build/prime-list.txt, one per line), carried in the executable's __DATA,__primelist section as well: the
# render server's sandbox may refuse to read the list file beside the bundle, and the plugin then primes from this copy (PrimeShaders.h).
PRIME_LIST = ROOT / 'build/prime-list.txt'
prime_section = [f'-Wl,-sectcreate,__DATA,__primelist,{PRIME_LIST}'] if PRIME_LIST.is_file() else []
subprocess.run([*(['xcrun', 'clang++'] + base[2:]), '-std=c++17', '-fobjc-arc', '-Wno-deprecated-declarations', '-bundle',
                '-I', ROOT / 'drivers/Adreno740', '-I', ROOT / 'kits/AdrenoPM4', '-I', VULKAN_INCLUDE, '-I', ROOT / 'build/turnip-smoke',
                '-x', 'objective-c++', ROOT / 'drivers/AdrenoMetal/NativeAdrenoMetalPlugin.mm',
                ROOT / 'drivers/AdrenoMetal/NativeBridgeMetalFrontend.mm', '-x', 'none', pm4, BRIDGE,
                *link_extra, '-Wl,-dead_strip', *prime_section, '-lobjc', '-framework', 'Foundation', '-framework', 'Metal', '-framework', 'IOSurface', '-o', exe],
               check=True)
if IOS27:
    subprocess.run(['python3', ROOT / 'scripts/rust-pac-rewrite.py', exe, OUT / 'NativeAdrenoMetal.map', 'libadreno_metal_bridge_pac.a'],
                   check=True)
subprocess.run(['strip', '-x', exe], check=True)
# The linker writes the debug symbols of the Rust bridge next to the executable; keep them beside the bundle, not in the image.
symbols = OUT / 'NativeAdrenoMetal.dSYM'
shutil.rmtree(symbols, ignore_errors=True)
if (bundle / 'NativeAdrenoMetal.dSYM').exists():
    shutil.move(bundle / 'NativeAdrenoMetal.dSYM', symbols)
# Turnip (the real Mesa Vulkan driver with the native Darwin kernel backend) travels inside the plugin bundle, signed on its own with 4 KiB pages so its
# CDHash can be trusted like the plugin's. It is signed before the bundle so the bundle's resource seal covers the final bytes.
turnip_lib = bundle / 'libvulkan_freedreno.dylib'
shutil.copyfile(TURNIP, turnip_lib)
subprocess.run(['strip', '-x', turnip_lib], check=True)
subprocess.run(['codesign', '--force', '--sign', '-', '--pagesize', '4096', '--identifier', 'org.blu-sharky.turnip', turnip_lib], check=True)
turnip_detail = subprocess.run(['codesign', '--display', '--verbose=4', turnip_lib], capture_output=True, text=True, check=True).stderr
turnip_cdhash = re.search(r'^CDHash=([a-f0-9]{40})$', turnip_detail, re.M)[1]
assert re.search(r'^Page size=4096$', turnip_detail, re.M)
(bundle / 'Info.plist').write_bytes(plistlib.dumps(dict(
    CFBundleIdentifier='org.blu-sharky.NativeAdrenoMetal', CFBundleExecutable='NativeAdrenoMetal', CFBundlePackageType='BNDL',
    CFBundleVersion='1', CFBundleShortVersionString='1', NSPrincipalClass='NativeAdrenoMetalDevice',
    MinimumOSVersion='27.0' if IOS27 else '17.0'), fmt=plistlib.FMT_XML))
subprocess.run(['codesign', '--force', '--sign', '-', '--pagesize', '4096', '--identifier', 'org.blu-sharky.NativeAdrenoMetal',
                bundle], check=True)
subprocess.run(['codesign', '--verify', '--strict', bundle], check=True)
detail = subprocess.run(['codesign', '--display', '--verbose=4', bundle], capture_output=True, text=True, check=True).stderr
cdhash = re.search(r'^CDHash=([a-f0-9]{40})$', detail, re.M)[1]
assert re.search(r'^Page size=4096$', detail, re.M), 'the signature must use 4 KiB pages'
header = exe.read_bytes()[:16]
magic, cputype, subtype = int.from_bytes(header[0:4], 'little'), int.from_bytes(header[4:8], 'little'), int.from_bytes(header[8:12], 'little')
assert (magic, cputype, subtype & 0xffffff) == (0xfeedfacf, 0x100000c, 2 if IOS27 else 0), 'expected an arm64e (27) or ARM64 (17) Mach-O'
# The probe daemon (launchd starts it as an owner job). The original platform sandbox policy refuses IOServiceOpen for any user-client class
# a process has not been granted (the same refusal an unentitled consumer got in the offline owner tests), so it carries exactly the grant that
# worked there: com.apple.security.iokit-user-client-class naming the one class it opens, plus no-container.
entitlements = OUT / 'adrenoprobed-entitlements.plist'
# The logging grants let it read the whole unified log for the export (NativeOsLogExport.mm).
entitlements.write_bytes(plistlib.dumps({'com.apple.private.security.no-container': True,
                                         'com.apple.security.iokit-user-client-class': ['AGXDeviceUserClient'],
                                         'com.apple.private.logging.admin': True, 'com.apple.private.logging.diagnostic': True,
                                         'com.apple.private.logging.stream': True}))
daemon = OUT / 'adrenoprobed'
subprocess.run(['xcrun', 'clang++', *base[2:], '-std=c++17', '-I', ROOT / 'drivers/Adreno740', '-I', ROOT / 'kits/AdrenoPM4', '-I', VULKAN_INCLUDE,
                '-I', ROOT / 'build/turnip-smoke',
                ROOT / 'drivers/AdrenoMetal/NativeAdrenoProbeDaemon.cpp', '-x', 'objective-c++', '-fobjc-arc',
                ROOT / 'drivers/AdrenoMetal/NativeOsLogExport.mm', '-x', 'none', pm4, '-framework', 'Foundation', '-lz', '-o', daemon], check=True)
subprocess.run(['codesign', '--force', '--sign', '-', '--pagesize', '4096', '--identifier', 'org.blu-sharky.adrenoprobed',
                '--entitlements', entitlements, daemon], check=True)
actual = plistlib.loads(subprocess.check_output(['codesign', '-d', '--entitlements', ':-', str(daemon)], stderr=subprocess.DEVNULL))
assert actual == plistlib.loads(entitlements.read_bytes()), 'the signed entitlement set differs'
subprocess.run(['codesign', '--verify', '--strict', daemon], check=True)
detail = subprocess.run(['codesign', '--display', '--verbose=4', daemon], capture_output=True, text=True, check=True).stderr
daemon_cdhash = re.search(r'^CDHash=([a-f0-9]{40})$', detail, re.M)[1]
assert re.search(r'^Page size=4096$', detail, re.M)
(OUT / 'org.blu-sharky.adrenoprobed.plist').write_bytes(plistlib.dumps(dict(
    Label='org.blu-sharky.adrenoprobed', ProgramArguments=['/private/var/ngpu/bin/adrenoprobed'], RunAtLoad=True,
    KeepAlive=False, ThrottleInterval=30, UserName='root', StandardErrorPath='/dev/null'), fmt=plistlib.FMT_XML))
# launchd may enumerate the directory without our overlay's new names, so the same job is also offered under the name of an existing,
# non-essential RunAtLoad job (the display FDR loader: root, no MachServices): the overlay answers a lookup of that name first.
(OUT / 'com.apple.iomfb_fdr_loader.plist').write_bytes(plistlib.dumps(dict(
    Label='com.apple.iomfb_fdr_loader', ProgramArguments=['/private/var/ngpu/bin/adrenoprobed'], RunAtLoad=True,
    KeepAlive=False, LimitLoadToSessionType='System', ProcessType='Interactive', StandardErrorPath='/dev/null'), fmt=plistlib.FMT_XML))
# Bluetooth is unused on this board; its job is RunAtLoad and was seen to be exec'd on every boot (the exec observer lists bluetoothd).
(OUT / 'com.apple.bluetoothd.plist').write_bytes(plistlib.dumps(dict(
    Label='com.apple.bluetoothd', ProgramArguments=['/private/var/ngpu/bin/adrenoprobed'], RunAtLoad=True, KeepAlive=False,
    ProcessType='Interactive', StandardErrorPath='/dev/null'), fmt=plistlib.FMT_XML))
(OUT / 'trust.json').write_text(json.dumps(dict(cdhash=cdhash, daemon_cdhash=daemon_cdhash, turnip_cdhash=turnip_cdhash, bundle='NativeAdrenoMetal.bundle',
    executable_bytes=exe.stat().st_size, purpose='owner-built plugin and probe daemon; trusted only through an extra owner trust module'),
    indent=2) + '\n')
print('PASS: Adreno plugin bundle and probe daemon built and 4K-signed, CDHashes', cdhash, daemon_cdhash, turnip_cdhash)
