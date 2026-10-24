"""The raw disk of an Apple disk image (.dmg), read without hdiutil: the bytes `hdiutil attach` exposes as /dev/rdiskN.

A UDIF image ends with a 512-byte `koly` trailer that points at a property list. Its `blkx` entries are `mish` tables,
one per partition of the disk; each table lists chunks of 512-byte sectors and where their stored bytes are in the data
fork. Raw chunks are copied, zero-fill and ignored chunks read as zeros, and zlib, bzip2 and LZFSE chunks are
decompressed (LZFSE with Apple's reference `lzfse` tool). The chunks must cover the disk from sector 0 to the sector
count of the trailer without a gap. A file without a `koly` trailer is a raw disk image (UDRW), which is its own raw disk:
the SystemOS cryptex of an IPSW is one.
"""
import bz2
import plistlib
import struct
import subprocess
import zlib

from .util import Error, lzfse

SECTOR = 512
TRAILER = 512
COPY = 8 << 20
ZERO_FILL, RAW, IGNORE = 0x00000000, 0x00000001, 0x00000002
COMMENT, TERMINATOR = 0x7ffffffe, 0xffffffff
ZLIB, BZIP2, LZFSE = 0x80000005, 0x80000006, 0x80000007


class Image:
    """A disk image: `size` is the raw disk in bytes, `blocks()` yields it in order."""

    def __init__(self, path):
        self.path = path
        self.chunks = None
        with open(path, 'rb') as image:
            image.seek(0, 2)
            length = image.tell()
            if length >= TRAILER:
                image.seek(length - TRAILER)
                koly = image.read(TRAILER)
            else:
                koly = b''
            if koly[:4] != b'koly':
                self.size = length
                return
            data_fork, = struct.unpack_from('>Q', koly, 0x18)
            plist_offset, plist_length = struct.unpack_from('>QQ', koly, 0xd8)
            sectors, = struct.unpack_from('>Q', koly, 0x1ec)
            image.seek(plist_offset)
            plist = plistlib.loads(image.read(plist_length))
        self.size = sectors * SECTOR
        chunks = []
        for table in plist.get('resource-fork', {}).get('blkx', []):
            mish = table['Data']
            if mish[:4] != b'mish':
                raise Error(f'{path}: blkx {table.get("Name")!r} is not a mish table')
            first, = struct.unpack_from('>Q', mish, 8)
            base, = struct.unpack_from('>Q', mish, 0x18)
            count, = struct.unpack_from('>I', mish, 0xc8)
            for index in range(count):
                kind, _, sector, length, offset, stored = struct.unpack_from('>IIQQQQ', mish, 0xcc + 40 * index)
                if kind not in (COMMENT, TERMINATOR):
                    chunks.append(((first + sector) * SECTOR, length * SECTOR, kind, data_fork + base + offset, stored))
        chunks.sort()
        position = 0
        for start, length, kind, _, _ in chunks:
            if start != position:
                raise Error(f'{path}: no chunk covers bytes {position}..{start}')
            if kind not in (ZERO_FILL, RAW, IGNORE, ZLIB, BZIP2, LZFSE):
                raise Error(f'{path}: unsupported chunk type {kind:#x} at byte {start}')
            position += length
        if position != self.size:
            raise Error(f'{path}: the chunks cover {position} bytes, the trailer {self.size}')
        self.chunks = chunks

    def blocks(self):
        decoder = None
        with open(self.path, 'rb') as image:
            if self.chunks is None:
                while block := image.read(COPY):
                    yield block
                return
            for start, length, kind, offset, stored in self.chunks:
                if kind in (ZERO_FILL, IGNORE):
                    data = bytes(length)
                else:
                    image.seek(offset)
                    data = image.read(stored)
                    if kind == ZLIB:
                        data = zlib.decompress(data)
                    elif kind == BZIP2:
                        data = bz2.decompress(data)
                    elif kind == LZFSE:
                        decoder = decoder or lzfse()
                        data = subprocess.run([decoder, '-decode'], input=data, capture_output=True, check=True).stdout
                if len(data) != length:
                    raise Error(f'{self.path}: the chunk at byte {start} gives {len(data)} bytes, not {length}')
                yield data
