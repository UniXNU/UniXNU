#!/usr/bin/env python3
"""Verify raw firmware downloads retain both pinned content identities."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[2] / 'scripts/fetch-adreno-inputs.py'
spec = importlib.util.spec_from_file_location('adreno_inputs', SOURCE)
inputs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inputs)


class AdrenoInputFetchTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.data = b'firmware fixture'
        self.expected = {'bytes': len(self.data), 'sha256': hashlib.sha256(self.data).hexdigest()}
        self.blob = hashlib.sha1(b'blob ' + str(len(self.data)).encode() + b'\0' + self.data).hexdigest()

    def item(self, blob=None):
        return (self.root / 'firmware/input.bin', 'https://raw.githubusercontent.com/owner/repo/pin/input.bin',
                self.expected, self.blob if blob is None else blob, None)

    def test_raw_download_checks_git_blob_without_api_decoding(self):
        with patch.object(inputs, 'download', return_value=self.data):
            self.assertEqual(inputs.fetch(self.item()), len(self.data))
        self.assertEqual(self.item()[0].read_bytes(), self.data)
        self.assertFalse(list(self.root.rglob('*.part')))

    def test_bad_content_is_not_published(self):
        with patch.object(inputs, 'download', return_value=b'wrong'), self.assertRaisesRegex(ValueError, 'hash/size'):
            inputs.fetch(self.item())
        self.assertFalse(self.item()[0].exists())

    def test_bad_git_identity_is_not_published(self):
        with patch.object(inputs, 'download', return_value=self.data), self.assertRaisesRegex(ValueError, 'Git blob'):
            inputs.fetch(self.item(blob='0' * 40))
        self.assertFalse(self.item()[0].exists())

    def test_valid_cache_does_not_download(self):
        path = self.item()[0]
        path.parent.mkdir()
        path.write_bytes(self.data)
        with patch.object(inputs, 'download', side_effect=AssertionError('unexpected network access')):
            self.assertEqual(inputs.fetch(self.item()), len(self.data))


if __name__ == '__main__':
    unittest.main()
