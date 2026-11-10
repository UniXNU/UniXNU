#!/usr/bin/env python3
"""Make a Data seed whose APFS container fills the tablet's storage: grow the container of an existing packed seed (DBRDISK1) to a chosen size.

  seed-data-grow.py (--gib N | --auto [--userdata-bytes BYTES]) [--reserve-mib 1024] BASE.dbr OUTPUT.dbr

The same device ships with different storage sizes, so the size is chosen per build:
  --gib N        a container of exactly N GiB;
  --auto         sized from the tablet's userdata partition: asks a tablet in fastboot (`fastboot getvar partition-size:userdata`, read only) or takes
                 --userdata-bytes, and leaves out the root image (build/userdata-root/userdata-root.json), a 4 MiB guard, the log reserve
                 (--reserve-mib, the log-reserve value of the image, default 1024; 0 = none) and the store's own header and bitmap, then
                 rounds down to a whole GiB and keeps one more GiB free.
The container is grown on this Mac (a sparse raw image attached without mounting, `diskutil apfs resizeContainer`), then packed again: the output
keeps only the nonzero pages, so it is about as big as BASE. The volume UUID is unchanged. The result is a different disk for the persistent
store (the seed identity covers the size), so the Data of earlier images starts again. BASE is not modified; nothing is written to Git.
The kernel refuses a seed whose store window does not fit the real partition, so an image built for a larger tablet cannot damage a smaller one."""
import argparse
import json
import os
import plistlib
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'drivers/DarwinBoot/Test'))
import packed_ramdisk

GIB = 1024**3
MIB = 1024**2
GUARD_BLOCKS = 1024                      # NativeUfs keeps the store this far (4 KiB blocks) from the root image
MAX_GIB = 1024                           # packed_ramdisk.MAX_LOGICAL


def userdata_bytes_from_fastboot():
    result = subprocess.run(['fastboot', 'getvar', 'partition-size:userdata'], capture_output=True, text=True, timeout=30)
    match = re.search(r'partition-size:userdata:\s*(0x[0-9a-fA-F]+|\d+)', result.stdout + result.stderr)
    if not match:
        sys.exit('No tablet in fastboot answered partition-size:userdata; give --gib N or --userdata-bytes BYTES')
    return int(match.group(1), 0)


def root_image_bytes():
    report = ROOT / 'build/userdata-root/userdata-root.json'
    if report.exists():
        for key in ('image_bytes', 'bytes', 'size'):
            value = json.loads(report.read_text()).get(key)
            if isinstance(value, int):
                return value
    image = ROOT / 'build/userdata-root/userdata-root.img'
    if image.exists():
        return image.stat().st_size
    sys.exit('The root image size is unknown: build/userdata-root/userdata-root.json is missing')


def store_blocks(pages):
    bitmap = (pages + 8 * 4096 - 1) // (8 * 4096)
    return 1 + bitmap + pages


def auto_gib(userdata, reserve_mib):
    avail = userdata - ((root_image_bytes() + 4095) // 4096 + GUARD_BLOCKS) * 4096 - reserve_mib * MIB
    if avail <= 0:
        sys.exit('The userdata partition is too small for the root image and the reserve')
    gib = avail // GIB
    while gib > 0 and store_blocks(gib * GIB // 4096) * 4096 > avail:
        gib -= 1
    return gib - 1                         # one GiB of margin


def run(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    size = parser.add_mutually_exclusive_group(required=True)
    size.add_argument('--gib', type=int)
    size.add_argument('--auto', action='store_true')
    parser.add_argument('--userdata-bytes', type=lambda v: int(v, 0))
    parser.add_argument('--reserve-mib', type=int, default=1024)
    parser.add_argument('base', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if args.output.exists():
        sys.exit('Refuse to overwrite ' + str(args.output))
    if args.auto:
        gib = auto_gib(args.userdata_bytes or userdata_bytes_from_fastboot(), args.reserve_mib)
    else:
        gib = args.gib
    if not 3 <= gib <= MAX_GIB:
        sys.exit(f'{gib} GiB is outside 3..{MAX_GIB}')
    target = gib * GIB
    blob = args.base.read_bytes()
    logical, extents = packed_ramdisk.regions(blob)
    if target <= logical:
        sys.exit(f'The seed already holds {logical // GIB} GiB; growing needs a larger size')
    with tempfile.TemporaryDirectory(prefix='data-grow-', dir=str(ROOT / 'build')) as scratch:
        raw = Path(scratch) / 'seed.raw'
        with raw.open('wb') as handle:
            handle.truncate(target)
            for offset, data in extents:
                handle.seek(offset)
                handle.write(data)
        attached = run('hdiutil', 'attach', '-imagekey', 'diskimage-class=CRawDiskImage', '-nomount', '-nobrowse', str(raw))
        store = re.match(r'(/dev/disk\d+)', attached).group(1).split('/')[-1]
        try:
            listing = plistlib.loads(subprocess.check_output(['diskutil', 'apfs', 'list', '-plist']))
            container = None
            for entry in listing['Containers']:
                if any(s['DeviceIdentifier'] == store for s in entry.get('PhysicalStores', [])):
                    container = entry['ContainerReference']
            if not container:
                sys.exit('No APFS container found on the attached seed')
            run('diskutil', 'apfs', 'resizeContainer', container, '0')
        finally:
            subprocess.run(['hdiutil', 'detach', store, '-force'], capture_output=True)
        header = raw.open('rb').read(4096)
        if header[32:36] != b'NXSB':
            sys.exit('The grown image does not start with an APFS container')
        block_size = int.from_bytes(header[36:40], 'little')
        blocks = int.from_bytes(header[40:48], 'little')
        if block_size != 4096 or blocks * block_size > target or blocks * block_size < target - 64 * MIB:
            sys.exit(f'The container is {blocks * block_size} bytes, not the {target} asked for')
        metadata = packed_ramdisk.pack(raw, args.output)
    report = dict(base=str(args.base), gib=gib, container_bytes=blocks * block_size, **metadata)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
