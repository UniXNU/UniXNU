#!/usr/bin/env python3
"""Exercise actual FAT capacity, round trips and failed-copy publication."""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from unixnu.payload import EPOCH, write_volume
from unixnu.util import Error

MIB = 1 << 20


@unittest.skipUnless(shutil.which('mformat') and shutil.which('mcopy'), 'mtools required')
class PayloadVolumeTests(unittest.TestCase):
    def test_more_than_95_percent_fits_and_round_trips(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stage = root / 'stage'
            stage.mkdir()
            source = stage / 'kernel-with-long-name.bin'
            with source.open('wb') as stream:
                stream.write(b'payload-start')
                stream.truncate(61 * MIB)
                stream.seek(-11, os.SEEK_END)
                stream.write(b'payload-end')
            os.utime(source, (EPOCH, EPOCH))
            image = root / 'payload.img'
            self.assertGreater(source.stat().st_size, 64 * MIB * 0.95)
            write_volume(stage, image, 'PAYLOAD', 64)
            self.assertEqual(image.stat().st_size, 64 * MIB)
            restored = root / 'restored.bin'
            subprocess.run(['mcopy', '-i', image, '::/' + source.name, restored], check=True)
            self.assertEqual(hashlib.sha256(restored.read_bytes()).digest(),
                             hashlib.sha256(source.read_bytes()).digest())

    def test_disk_full_preserves_previous_image_and_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stage = root / 'stage'
            stage.mkdir()
            source = stage / 'too-large.bin'
            with source.open('wb') as stream:
                stream.truncate(65 * MIB)
            image = root / 'payload.img'
            image.write_bytes(b'previous-complete-payload')
            with self.assertRaisesRegex(Error, 'previous image retained'):
                write_volume(stage, image, 'PAYLOAD', 64)
            self.assertEqual(image.read_bytes(), b'previous-complete-payload')
            self.assertEqual(source.stat().st_size, 65 * MIB)
            self.assertFalse(list(root.glob('.payload-*')))

    def test_invalid_size_preserves_previous_image(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image = root / 'payload.img'
            image.write_bytes(b'previous')
            with self.assertRaisesRegex(Error, 'positive'):
                write_volume(root, image, 'PAYLOAD', 0)
            self.assertEqual(image.read_bytes(), b'previous')


if __name__ == '__main__':
    unittest.main()
