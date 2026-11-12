"""Userdata payload: the raw image for the device's `userdata` partition.

It holds the unchanged OS and SystemOS disk images of the IPSW, byte for byte, behind a small manifest
(the SHNGROOT layout the native UFS root driver reads):

    0x000000  manifest block (4096 bytes), zero padding to 1 MiB
    0x100000  window "OS"        the whole attached OS disk image, 1 MiB aligned
    ....      window "SystemOS"  the whole attached SystemOS disk image, 1 MiB aligned

    ....      data objects (--object NAME=FILE[:OFFSET]), each 1 MiB aligned

Manifest (little endian): "SHNGROOT", u32 version, u32 count, u64 image_bytes, then `count` 128-byte entries
{char name[32], u64 offset, u64 size, u32 block_size, u32 flags, u8 sha256[32], 40 reserved},
and at byte 4064 the SHA-256 of bytes 0..4063. A window has block_size 512 and flags 1 (read-only block device).
Version 2 adds data objects with block_size 4096 and flags 3: the kernel reads them itself and never publishes
them as block devices (the hash tables of header-only root policies, firmware). Version 1 holds windows only.

The OS profile lists the windows ([userdata] windows; optional ones are skipped when the IPSW lacks them) and the
device sets the partition geometry. The images come from the IPSW (a local file or a remote URL, see ipsw.py),
are decrypted when the IPSW ships them as AEA, and are checked against the pins of board.toml. The raw disk of each disk image is read without mounting: attached read-only with hdiutil on macOS,
decoded by udif.py on other hosts. Nothing is flashed: the report prints the fastboot command, to be run by the user.
"""
import contextlib
import hashlib
import json
import platform
import plistlib
import re
import struct
import subprocess
from pathlib import Path

from . import udif
from .ipsw import Ipsw
from .util import Error, log, run, sha256_file, tool

MIB = 1 << 20
CHUNK = 8 * MIB


def paths(ctx):
    out = ctx.work / 'userdata'
    return out, out / 'userdata-root.img', out / 'userdata-root.json'


def image_size(dmg):
    if platform.system() != 'Darwin':
        return udif.Image(dmg).size
    info = subprocess.run(['hdiutil', 'imageinfo', '-plist', str(dmg)], capture_output=True, check=True).stdout
    return plistlib.loads(info)['Size Information']['Total Bytes']


def attach(dmg):
    """Attach read-only without mounting; return the whole-disk device."""
    out = subprocess.run(['hdiutil', 'attach', '-nomount', '-readonly', '-noverify', '-noautofsck', str(dmg)],
                         capture_output=True, text=True, check=True).stdout
    for line in out.splitlines():
        match = re.match(r'(/dev/disk\d+)\s', line)
        if match:
            return match.group(1)
    raise Error('could not find the attached disk device')


def disk_blocks(dmg, size):
    """The raw disk of a disk image, in order: hdiutil's /dev/rdiskN on macOS, udif.py on other hosts."""
    if platform.system() != 'Darwin':
        yield from udif.Image(dmg).blocks()
        return
    device = attach(dmg)
    try:
        raw = device.replace('/dev/disk', '/dev/rdisk')
        done = 0
        with open(raw, 'rb', buffering=0) as handle:
            while done < size:
                want = min(CHUNK, size - done)
                data = handle.read(want)
                if len(data) != want:
                    raise Error(f'short read from {raw} at {done}')
                yield data
                done += want
    finally:
        subprocess.run(['hdiutil', 'detach', device], capture_output=True)


def build(ctx, dry_run=False):
    log('userdata payload')
    spec = ctx.board.get('userdata')
    if not spec:
        raise Error('board.toml has no [userdata]')
    if platform.system() == 'Darwin':
        tool('hdiutil', 'the disk images are attached with macOS hdiutil')
    source = Ipsw(ctx)
    capacity = (spec['last_lba'] - spec['first_lba'] + 1) * spec.get('lba_bytes', 4096)
    windows = []
    for window in spec.get('windows', []):
        try:
            source.member(window['component'])
        except Error:
            if not window.get('optional'):
                raise
            log(f'userdata: {window["name"]} skipped, {window["component"]} is not in this IPSW')
            continue
        windows.append(window)
    if not windows:
        raise Error('[userdata] windows selects no disk image; the OS profile defines them')
    if dry_run:
        for window in windows:
            name, size, _ = source.info(window['component'])
            log(f'userdata: {window["name"]} would be extracted from {name} ({size >> 20} MiB)')
        log('userdata: dry run, nothing extracted or written')
        return None
    sources = [(window['name'], source.disk_image(window['component'])) for window in windows]
    layout, cursor = [], MIB
    for name, dmg in sources:
        size = image_size(dmg)
        layout.append((name, cursor, size))
        cursor += (size + MIB - 1) // MIB * MIB
    objects = []
    for spec_text in getattr(ctx.args, 'object', None) or []:
        name, sep, rest = spec_text.partition('=')
        file_text, _, skip_text = rest.partition(':')
        path = Path(file_text).expanduser()
        if not sep or not name or len(name.encode()) > 31 or not path.is_file():
            raise Error(f'--object {spec_text}: expected NAME=FILE[:OFFSET] with an existing file and a name under 32 bytes')
        skip = int(skip_text, 0) if skip_text else 0
        size = path.stat().st_size - skip
        if skip < 0 or size <= 0:
            raise Error(f'--object {spec_text}: offset outside the file')
        objects.append((name, cursor, size, path, skip))
        cursor += (size + MIB - 1) // MIB * MIB
    if len(layout) + len(objects) > 8 or len(layout) > 4 or len(objects) > 4:
        raise Error('the root manifest holds at most 4 windows and 4 data objects')
    total = cursor
    log(f'userdata: image {total} bytes ({total / 2**30:.2f} GiB) in a partition of {capacity} bytes')
    if total > capacity:
        raise Error('the image is larger than the userdata partition')
    for name, dmg in sources:
        log(f'userdata: {name} from {dmg.name}')
    out, image, report = paths(ctx)
    out.mkdir(parents=True, exist_ok=True)
    entries = []
    with image.open('wb') as target:
        target.truncate(total)
        for (name, offset, size), (_, dmg) in zip(layout, sources):
            digest = hashlib.sha256()
            target.seek(offset)
            done = 0
            with contextlib.closing(disk_blocks(dmg, size)) as blocks:
                for data in blocks:
                    digest.update(data)
                    target.write(data)
                    done += len(data)
            if done != size:
                raise Error(f'{dmg.name}: {done} bytes of raw disk, expected {size}')
            entries.append((name, offset, size, digest.digest()))
            log(f'userdata: {name} {size} bytes at {offset:#x} sha256 {digest.hexdigest()}')
        object_entries = []
        for name, offset, size, path, skip in objects:
            with path.open('rb') as handle:
                handle.seek(skip)
                data = handle.read(size)
            if len(data) != size:
                raise Error(f'{path}: short read for object {name}')
            target.seek(offset)
            target.write(data)
            object_entries.append((name, offset, size, hashlib.sha256(data).digest()))
            log(f'userdata: object {name} {size} bytes at {offset:#x} from {path.name}')
        header = bytearray(4096)
        header[0:8] = b'SHNGROOT'
        struct.pack_into('<IIQ', header, 8, 2 if object_entries else 1, len(entries) + len(object_entries), total)
        rows = [(e, 512, 1) for e in entries] + [(e, 4096, 3) for e in object_entries]
        for index, ((name, offset, size, digest), block, flags) in enumerate(rows):
            struct.pack_into('<32sQQII32s40s', header, 24 + 128 * index, name.encode(), offset, size, block, flags, digest, bytes(40))
        header[4064:4096] = hashlib.sha256(bytes(header[:4064])).digest()
        target.seek(0)
        target.write(header)
    data = {'image_bytes': total, 'image_sha256': sha256_file(image), 'manifest_sha256': hashlib.sha256(bytes(header)).hexdigest(),
            'windows': [{'name': n, 'offset': o, 'size': s, 'sha256': d.hex()} for n, o, s, d in entries],
            'objects': [{'name': n, 'offset': o, 'size': s, 'sha256': d.hex()} for n, o, s, d in object_entries],
            'userdata_bytes': capacity, 'flash_command': f'fastboot flash userdata {image}',
            'source': 'remote' if source.remote else 'local', 'hardware_tested': False}
    report.write_text(json.dumps(data, indent=2) + '\n')
    log(f'userdata: {image}')
    log(f'flash it yourself with: {data["flash_command"]}')
    return image
