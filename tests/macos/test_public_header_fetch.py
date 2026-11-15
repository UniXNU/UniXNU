#!/usr/bin/env python3
"""Exercise public-header restoration when GitHub's directory API is limited."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
import urllib.error
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[2] / 'scripts/prepare-xnu-source.py'
spec = importlib.util.spec_from_file_location('public_headers', SOURCE)
headers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(headers)


class PublicHeaderFetchTest(unittest.TestCase):
    def setUp(self):
        self.directory = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(contextlib.redirect_stdout(io.StringIO()))

    def test_limited_api_uses_the_same_tag_and_caches_the_listing(self):
        cache = self.directory / 'headers.json'
        entries = [{'type': 'file', 'name': 'Example.h'}]
        error = urllib.error.HTTPError('https://api.github.com', 403, 'rate limited', {}, None)
        with patch.object(headers, 'fetch', side_effect=error) as fetch, \
                patch.object(headers, 'archive_entries', return_value=entries) as archive:
            self.assertEqual(headers.directory_entries(cache, 'iokit/DriverKit', 'xnu-test'), entries)
            self.assertEqual(headers.directory_entries(cache, 'iokit/DriverKit', 'xnu-test'), entries)
        self.assertEqual(fetch.call_count, 1)
        archive.assert_called_once_with('iokit/DriverKit', 'xnu-test')
        self.assertEqual(json.loads(cache.read_text()), entries)

    def test_missing_directory_does_not_fall_back(self):
        error = urllib.error.HTTPError('https://api.github.com', 404, 'not found', {}, None)
        with patch.object(headers, 'fetch', side_effect=error), patch.object(headers, 'archive_entries') as archive:
            with self.assertRaises(urllib.error.HTTPError):
                headers.directory_entries(self.directory / 'headers.json', 'missing', 'xnu-test')
        archive.assert_not_called()

    def test_archive_listing_preserves_blob_verification(self):
        data = b'public header fixture\n'
        archive = self.directory / 'xnu-public-headers-xnu-test.tar.gz'
        with tarfile.open(archive, 'w:gz') as target:
            for name in ('iokit/DriverKit/Example.h', 'iokit/DriverKit/crypto/Nested.h', 'iokit/DriverKit/README'):
                entry = tarfile.TarInfo('xnu-xnu-test/' + name)
                entry.size = len(data)
                target.addfile(entry, io.BytesIO(data))
        with patch.object(headers, 'CACHE', self.directory / 'listing.json'), \
                patch.object(headers, 'fetch', return_value=data):
            entries = headers.archive_entries('iokit/DriverKit', 'xnu-test')
            self.assertEqual([entry['name'] for entry in entries], ['Example.h'])
            digest = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
            self.assertEqual(entries[0]['sha'], digest)
            output = self.directory / 'restored'
            self.assertEqual(headers.restore(entries[0], output, 'xnu-test')['git_blob'], digest)
            self.assertEqual((output / 'Example.h').read_bytes(), data)

    def test_corrupt_archive_is_not_published(self):
        with patch.object(headers, 'CACHE', self.directory / 'listing.json'), \
                patch.object(headers, 'fetch', return_value=b'incomplete download'):
            with self.assertRaises(tarfile.ReadError):
                headers.archive_entries('iokit/DriverKit', 'xnu-test')
        self.assertFalse((self.directory / 'xnu-public-headers-xnu-test.tar.gz').exists())


if __name__ == '__main__':
    unittest.main()
