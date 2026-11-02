#!/usr/bin/env python3
"""Verify first-frame wallpaper freeze with GPU pixels and real callback state."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--reuse-bridge', action='store_true', help='use the already built, matching host bridge')
args = parser.parse_args()
if not args.reuse_bridge:
    subprocess.run([sys.executable, ROOT / 'scripts/build-adreno-metal-bridge.py', '--target', 'host'], check=True)
kit = ROOT / 'drivers/AdrenoMetal'
out = ROOT / 'build/wallpaper-freeze-host'
out.mkdir(exist_ok=True, parents=True)
exe = out / 'MercuryPosterExtension'
subprocess.run(['xcrun', 'clang++', '-std=c++17', '-fobjc-arc', '-O1', '-Wall', '-Wextra', '-Werror',
                '-Wno-unused-parameter', '-Wno-deprecated-declarations', '-I', kit,
                kit / 'NativeBridgeMetalFrontend.mm', kit / 'bridge/wallpaper_freeze_host.mm',
                ROOT / 'build/adreno-metal-bridge/host/libadreno_metal_bridge.a',
                '-framework', 'Foundation', '-framework', 'Metal', '-framework', 'IOSurface', '-o', exe], check=True)
for name, mode in [('MercuryPosterExtension', 'freeze'), ('MercuryPosterExtension', 'disabled'),
                   ('MercuryPosterExtension', 'absent'), ('backboardd', 'unaffected'), ('PosterBoard', 'unaffected')]:
    program = out / name
    if program != exe and not program.exists():
        program.symlink_to(exe)
    cache = out / (name + '-' + mode)
    cache.mkdir(exist_ok=True)
    result = subprocess.run([program, '/opt/homebrew/lib/libMoltenVK.dylib', cache, mode],
                            capture_output=True, text=True, timeout=45)
    (out / (name + '-' + mode + '.log')).write_text(result.stdout + result.stderr)
    print(result.stdout, end='', flush=True)
    if result.returncode:
        raise SystemExit(result.stderr[-4000:] or f'{name}/{mode} exited {result.returncode}')
