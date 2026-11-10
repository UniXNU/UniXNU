#!/usr/bin/env python3
"""Pack the owner-built Adreno Metal plugin into a GPU addon file for the boot payload.

  make-gpu-addon.py [--publish] [--no-daemon] [--prefix addons|GPUBundles] [--wallpaper DIR] [--wallpaper-floating DIR] [--prime-list FILE] [--pipeline-pack FILE] [--cache-export] OUTPUT

The files are the ones add-gpu-plugin-data.py stages into a Data seed, with the same paths below /private/var/ngpu and the same modes:
addons/NativeAdrenoMetal.bundle/*, addons/NativeAdrenoMetal.publish (--publish),
bin/adrenoprobed and daemons/*.plist. --wallpaper adds the files of DIR (scripts/make-wallpaper-overlay.py) as wallpaper/*, which the
kernel mounts over the default wallpaper's layered animation; --wallpaper-floating DIR as wallpaper-floating/*, mounted over the same
wallpaper's floating layer (iPadOS 27). --prime-list adds FILE (the absolute paths of the OS image's .metallib
files, one per line) as addons/NativeAdrenoMetal.primelist, the libraries the render server compiles ahead (PrimeShaders.h). The payload carries the file next to the kernel (unixnu build payload --gpu-addon), the loader
hands it to the kernel as /chosen/memory-map/GpuAddon, and the kernel writes every file whose content or mode differs into the mounted
Data volume before its addon mounts (gpu-addon=1). The Data seed then no longer changes with the plugin, so its persistent store
(whose identity is the seed's content) survives a plugin rebuild. The kernel creates missing directories.

The data of every file is zlib-compressed: the payload FAT (the boot image's ramdisk) has to stay at 192 MiB, which the tablet's boot
loader accepts (a 256 MiB ramdisk does not start the firmware), and the kernel and the Data seed already take most of it.

Layout, little endian: "NGPUADD2", u32 count, u32 0, u64 total bytes; per file u32 path bytes (with its NUL, at most 160), u32 mode,
u64 size, u64 compressed size, the path padded to 8 bytes, the zlib stream padded to 8 bytes."""
import os
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# ADRENO_PLUGIN_DIR: another plugin build (build/adreno-metal-plugin27 for iPadOS 27).
PLUGIN = Path(os.environ.get('ADRENO_PLUGIN_DIR') or ROOT / 'build/adreno-metal-plugin')
BUNDLE = PLUGIN / 'NativeAdrenoMetal.bundle'


def pad(data):
    return data + bytes(-len(data) % 8)


def main():
    no_daemon = '--no-daemon' in sys.argv[1:]
    args = [a for a in sys.argv[1:] if a not in ('--publish', '--no-daemon')]
    publish = '--publish' in sys.argv[1:]
    wallpaper = None
    floating = None
    if '--wallpaper-floating' in args:
        at = args.index('--wallpaper-floating')
        floating = Path(args[at + 1])
        del args[at:at + 2]
        if not floating.is_dir():
            sys.exit('--wallpaper-floating takes a directory')
    if '--wallpaper' in args:
        at = args.index('--wallpaper')
        wallpaper = Path(args[at + 1])
        del args[at:at + 2]
        if not wallpaper.is_dir():
            sys.exit('--wallpaper takes a directory')
    prime_list = None
    if '--prime-list' in args:
        at = args.index('--prime-list')
        prime_list = Path(args[at + 1])
        del args[at:at + 2]
        lines = prime_list.read_text().split()
        if not lines or any(not line.startswith('/') or not line.endswith('.metallib') for line in lines):
            sys.exit('--prime-list takes a file of absolute .metallib paths')
    # --prefix DIR: the directory below the install root the plugin files go to (addons/ on iPadOS, below /private/var/ngpu;
    # GPUBundles/ on macOS, which the kernel writes to /Library/GPUBundles and protects for IOGPU's trust check).
    prefix = 'addons'
    if '--prefix' in args:
        at = args.index('--prefix')
        prefix = args[at + 1]
        del args[at:at + 2]
        if prefix not in ('addons', 'GPUBundles'):
            sys.exit('--prefix takes addons or GPUBundles')
    cache_export = '--cache-export' in args
    if cache_export:
        args.remove('--cache-export')
    pipeline_pack = None
    if '--pipeline-pack' in args:
        at = args.index('--pipeline-pack')
        pipeline_pack = Path(args[at + 1])
        del args[at:at + 2]
        if pipeline_pack.read_bytes()[:8] != b'SHEXP001':
            sys.exit('--pipeline-pack takes a SHEXP001 pack (scripts/make-m2vpack.py)')
    if len(args) != 1:
        sys.exit(__doc__)
    output = Path(args[0]).resolve()
    if output.exists():
        sys.exit('Refuse to overwrite ' + str(output))
    # iOS keeps a flat bundle; macOS keeps the executable in Contents/MacOS. The addon carries either layout as built.
    if not (BUNDLE / 'NativeAdrenoMetal').is_file() and not (BUNDLE / 'Contents/MacOS/NativeAdrenoMetal').is_file():
        sys.exit('Build the plugin first: python3 scripts/build-adreno-metal-plugin.py')
    files = []
    for path in sorted(p for p in BUNDLE.rglob('*') if p.is_file()):
        mode = 0o755 if path.name in ('NativeAdrenoMetal', 'libvulkan_freedreno.dylib') else 0o644
        files.append((f'{prefix}/NativeAdrenoMetal.bundle/' + path.relative_to(BUNDLE).as_posix(), mode, path.read_bytes()))
    if publish:
        files.append((f'{prefix}/NativeAdrenoMetal.publish', 0o644, b'1\n'))
    if prime_list:
        files.append((f'{prefix}/NativeAdrenoMetal.primelist', 0o644, prime_list.read_bytes()))
    if cache_export:   # the plugin sends its cache directory to the UFS log (CacheExport.h)
        files.append((f'{prefix}/NativeAdrenoMetal.cacheexport', 0o644, b'1\n'))
    if pipeline_pack:
        files.append((f'{prefix}/NativeAdrenoMetal.m2vpack', 0o644, pipeline_pack.read_bytes()))
    # --no-daemon: only the plugin (iPadOS 27 runs no probe daemon and keeps its launchd jobs).
    if not no_daemon:
        files.append(('bin/adrenoprobed', 0o755, (PLUGIN / 'adrenoprobed').read_bytes()))
    for plist in sorted(PLUGIN.glob('*.plist')) if not no_daemon else []:
        if not plist.name.endswith('-entitlements.plist'):   # build input, not a launchd job
            files.append(('daemons/' + plist.name, 0o644, plist.read_bytes()))
    if wallpaper:
        for path in sorted(p for p in wallpaper.rglob('*') if p.is_file()):
            files.append(('wallpaper/' + path.relative_to(wallpaper).as_posix(), 0o644, path.read_bytes()))
    if floating:
        for path in sorted(p for p in floating.rglob('*') if p.is_file()):
            files.append(('wallpaper-floating/' + path.relative_to(floating).as_posix(), 0o644, path.read_bytes()))
    body = b''
    for name, mode, data in files:
        encoded = name.encode() + b'\0'
        if len(encoded) > 160 or '..' in name.split('/') or name.startswith('/'):
            sys.exit('Bad addon path ' + name)
        packed = zlib.compress(data, 9)
        body += struct.pack('<IIQQ', len(encoded), mode, len(data), len(packed)) + pad(encoded) + pad(packed)
    blob = b'NGPUADD2' + struct.pack('<IIQ', len(files), 0, 24 + len(body)) + body
    output.write_bytes(blob)
    for name, mode, data in files:
        print(f'{mode:o} {len(data):>10} {name}')
    print(f'{output}: {len(files)} files, {len(blob)} bytes')


if __name__ == '__main__':
    main()
