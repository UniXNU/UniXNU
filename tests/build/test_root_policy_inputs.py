"""Reject mixed root policy evidence before any component compilation."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from unixnu import kernel, root_policies
from unixnu.util import Error


class RootPolicyInputTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.digest = 'ab' * 32
        self.identity = '84581E99-85BE-4957-AC53-2947E887B3E4'
        self.key = b'k' * 395
        self.header = bytearray(544)
        self.header[56:88] = bytes.fromhex(self.digest)
        self.record = dict(image_bytes=4096, blocks_verified=1, image_sha256=self.digest,
                           volume_uuid=self.identity, generation=1,
                           trusted_key_sha256=hashlib.sha256(self.key).hexdigest(),
                           real_c_signature_and_block_verification=True, original_image_modified=False)
        self.write()

    def write(self):
        (self.root / 'verification.json').write_text(json.dumps(self.record))
        (self.root / 'trusted-key.bin').write_bytes(self.key)
        (self.root / 'manifest.header.bin').write_bytes(self.header)

    def test_matching_record_is_preserved(self):
        result = root_policies.validate(self.root, self.digest, self.identity)
        self.assertEqual(json.loads(result['verification.json']), self.record)
        self.assertEqual(result['trusted-key.bin'], self.key)

    def test_repository_key_cannot_replace_installation_key(self):
        (self.root / 'trusted-key.bin').write_bytes(b'x' * 395)
        with self.assertRaisesRegex(Error, 'do not match'):
            root_policies.validate(self.root, self.digest, self.identity)

    def test_invalid_record_or_header_is_refused(self):
        for field, value in [('image_sha256', 'cd' * 32), ('volume_uuid', '00000000-0000-0000-0000-000000000000'),
                             ('blocks_verified', 2), ('real_c_signature_and_block_verification', False),
                             ('original_image_modified', True)]:
            with self.subTest(field=field):
                original = self.record[field]
                self.record[field] = value
                self.write()
                with self.assertRaises(Error):
                    root_policies.validate(self.root, self.digest, self.identity)
                self.record[field] = original
        self.write()
        (self.root / 'manifest.header.bin').write_bytes(self.header[:-1])
        with self.assertRaises(Error):
            root_policies.validate(self.root, self.digest, self.identity)

    def test_local_manifest_requires_native_authentication(self):
        (self.root / 'manifest.bin').write_bytes(self.header + bytes(32))
        with self.assertRaisesRegex(Error, 'host verifier is required'):
            root_policies.validate(self.root, self.digest, self.identity, full=True)

    def test_component_input_errors_are_aggregated(self):
        spec = dict(id='Driver', kind='driver', source_files=['missing.cpp'])
        ctx = SimpleNamespace(tree=self.root, board={}, component_specs=[spec],
                              modules={('driver', 'Driver'): SimpleNamespace(path=self.root)})
        with patch.object(kernel, 'archive_plan', return_value=[('script', 'missing.py')]):
            with self.assertRaises(Error) as caught:
                kernel.preflight(ctx)
        self.assertIn('missing.py', str(caught.exception))
        self.assertIn('Driver/missing.cpp', str(caught.exception))

    def test_payload_and_runtime_builders_are_checked_early(self):
        ctx = SimpleNamespace(tree=self.root, component_specs=[dict(id='Metal', kind='driver',
                              build_stage='payload', build=['plugin.py'])],
                              board=dict(payload=dict(runtime=dict(wifi_tool='scripts/wifi.py'))),
                              modules={('driver', 'Metal'): SimpleNamespace(path=self.root)})
        with patch.object(kernel, 'archive_plan', return_value=[]):
            with self.assertRaises(Error) as caught:
                kernel.preflight(ctx)
        self.assertIn('plugin.py', str(caught.exception))
        self.assertIn('scripts/wifi.py', str(caught.exception))


if __name__ == '__main__':
    unittest.main()
