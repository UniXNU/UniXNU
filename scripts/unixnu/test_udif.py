#!/usr/bin/env python3
"""Offline tests of udif.py with small synthetic disk images: chunk types, partition order, raw images, refusals.

    python3 scripts/unixnu/test_udif.py
"""
import bz2
import os
from pathlib import Path
import plistlib
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from unixnu import udif  # noqa: E402
from unixnu.util import Error  # noqa: E402

SECTOR = udif.SECTOR


def lzfse_tool():
    path = Path(os.environ.get('UNIXNU_TOOLCHAIN', '/opt/unixnu-linux')) / 'bin/lzfse'
    return str(path) if path.is_file() else shutil.which('lzfse')


def write_udif(path, partitions):
    """partitions: [(name, first_sector, [(kind, sectors, stored_bytes)])], written in the given order."""
    fork, tables = bytearray(), []
    for name, first, chunks in partitions:
        entries, sector = [], 0
        for kind, sectors, stored in chunks:
            entries.append(struct.pack('>IIQQQQ', kind, 0, sector, sectors, len(fork), len(stored)))
            fork += stored
            sector += sectors
        entries.append(struct.pack('>IIQQQQ', udif.TERMINATOR, 0, sector, 0, len(fork), 0))
        mish = bytearray(0xcc)
        mish[0:4] = b'mish'
        struct.pack_into('>IQQQ', mish, 4, 1, first, sector, 0)
        struct.pack_into('>I', mish, 0xc8, len(entries))
        tables.append({'Name': name, 'Data': bytes(mish) + b''.join(entries)})
    plist = plistlib.dumps({'resource-fork': {'blkx': tables}})
    sectors = max(first + sum(c[1] for c in chunks) for _, first, chunks in partitions)
    koly = bytearray(udif.TRAILER)
    koly[0:4] = b'koly'
    struct.pack_into('>III', koly, 4, 4, udif.TRAILER, 1)
    struct.pack_into('>QQ', koly, 0x18, 0, len(fork))
    struct.pack_into('>QQ', koly, 0xd8, len(fork), len(plist))
    struct.pack_into('>Q', koly, 0x1ec, sectors)
    Path(path).write_bytes(bytes(fork) + plist + bytes(koly))


class Udif(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / 'test.dmg'

    def tearDown(self):
        self.dir.cleanup()

    def raw(self, image):
        return b''.join(image.blocks())

    def test_chunk_types_and_partition_order(self):
        a, b, c = os.urandom(SECTOR), os.urandom(3 * SECTOR), os.urandom(2 * SECTOR)
        # The second partition comes first in the plist; the disk is laid out by sector.
        write_udif(self.path, [
            ('second', 4, [(udif.ZLIB, 3, zlib.compress(b)), (udif.BZIP2, 2, bz2.compress(c))]),
            ('first', 0, [(udif.RAW, 1, a), (udif.ZERO_FILL, 2, b''), (udif.IGNORE, 1, b'')]),
        ])
        image = udif.Image(self.path)
        self.assertEqual(image.size, 9 * SECTOR)
        self.assertEqual(self.raw(image), a + bytes(3 * SECTOR) + b + c)

    def test_lzfse_chunk(self):
        tool = lzfse_tool()
        if not tool:
            self.skipTest('no lzfse tool')
        data = os.urandom(SECTOR) + bytes(7 * SECTOR)
        stored = subprocess.run([tool, '-encode'], input=data, capture_output=True, check=True).stdout
        write_udif(self.path, [('disk', 0, [(udif.LZFSE, 8, stored)])])
        self.assertEqual(self.raw(udif.Image(self.path)), data)

    def test_raw_image_is_its_own_disk(self):
        data = os.urandom(3 * 4096)
        self.path.write_bytes(data)
        image = udif.Image(self.path)
        self.assertEqual(image.size, len(data))
        self.assertEqual(self.raw(image), data)

    def test_gap_is_refused(self):
        write_udif(self.path, [('a', 0, [(udif.RAW, 1, bytes(SECTOR))]), ('b', 2, [(udif.RAW, 1, bytes(SECTOR))])])
        with self.assertRaisesRegex(Error, 'no chunk covers'):
            udif.Image(self.path)

    def test_unsupported_chunk_is_refused(self):
        write_udif(self.path, [('adc', 0, [(0x80000004, 1, b'\x00')])])
        with self.assertRaisesRegex(Error, 'unsupported chunk type'):
            udif.Image(self.path)

    def test_short_chunk_is_refused(self):
        write_udif(self.path, [('short', 0, [(udif.ZLIB, 2, zlib.compress(bytes(SECTOR)))])])
        with self.assertRaisesRegex(Error, 'gives 512 bytes, not 1024'):
            self.raw(udif.Image(self.path))


if __name__ == '__main__':
    unittest.main()
