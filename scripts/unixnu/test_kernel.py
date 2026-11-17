"""Native-only kernel staging must not fetch or prelink the original kernelcache."""
import hashlib
import json
from pathlib import Path
import struct
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from unixnu import kernel
from unixnu.cli import parser
from unixnu.util import Error


class NativeKernelTests(unittest.TestCase):
    def test_prelink_failure_preserves_previous_output_and_keeps_diagnostics(self):
        self.check_prelink_publication(fail=True)

    def test_prelink_success_publishes_image_and_relocates_record_paths(self):
        self.check_prelink_publication(fail=False)

    def check_prelink_publication(self, fail):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, cache = root / 'native', root / 'cache'
            source.write_bytes(b'native')
            cache.write_bytes(b'cache')
            ctx = SimpleNamespace(tree=root, work=root, logs=root, args=SimpleNamespace(skip_prelink=False),
                                  option=lambda *args: cache,
                                  board={'kernel': {'prelink': {'kernel': 'native', 'tool': 'emit.py', 'slide': '0'}}})
            output = root / 'kernel/kernel.macho'
            output.parent.mkdir()
            output.write_bytes(b'old image')
            output.with_suffix('.json').write_text('{"old": true}')
            output.with_suffix('.map.json').write_text('{"cached": true}')

            def emit(command, **kwargs):
                self.assertEqual(output.read_bytes(), b'old image')
                candidate = command[command.index('--output') + 1]
                self.assertNotEqual(candidate, output)
                self.assertFalse(candidate.exists())
                self.assertEqual(json.loads(candidate.with_suffix('.map.json').read_text()), {'cached': True})
                candidate.with_suffix('.json').write_text(json.dumps({
                    'output': str(candidate.resolve()), 'map': str(candidate.with_suffix('.map.json').resolve())}))
                candidate.write_bytes(b'new image')
                if fail:
                    raise Error('incomplete pairing')

            with patch.object(kernel, 'run', side_effect=emit):
                if fail:
                    with self.assertRaisesRegex(Error, 'incomplete pairing'):
                        kernel.prelink(ctx)
                    self.assertEqual(output.read_bytes(), b'old image')
                    self.assertEqual(json.loads(output.with_suffix('.json').read_text()), {'old': True})
                else:
                    self.assertEqual(kernel.prelink(ctx, adreno_abi='built ABI'), output)
                    self.assertEqual(output.read_bytes(), b'new image')
            report = json.loads(output.with_suffix('.failed.json' if fail else '.json').read_text())
            self.assertEqual(report['output'], str(output.resolve()))
            self.assertEqual(report['map'], str(output.with_suffix('.map.json').resolve()))
            if not fail:
                self.assertEqual(report['adreno_abi_sha256'], 'built ABI')
            self.assertEqual(list(output.parent.glob('.prelink-*')), [])

    def test_skip_prelink_keeps_bytes_and_does_not_fetch_ipsw(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = struct.pack('<8I', 0xfeedfacf, 0x100000c, 2, 2, 0, 0, 0, 0) + b'native seal'
            source = root / 'native'
            source.write_bytes(data)
            ctx = SimpleNamespace(tree=root, work=root / 'out',
                                  args=parser().parse_args(['prelink', '--skip-prelink']),
                                  board={'kernel': {'prelink': {'kernel': 'native'}}})
            with patch.object(kernel.ipsw, 'Ipsw', side_effect=AssertionError('must not fetch')):
                output = kernel.prelink(ctx, adreno_abi='built ABI')
                kernel.prelink(ctx)
                kernel.require_adreno_abi(output, 'built ABI')
                source.write_bytes(data + b'different kernel')
                kernel.prelink(ctx)
                with self.assertRaisesRegex(Error, 'does not match the Adreno ABI'):
                    kernel.require_adreno_abi(output, 'built ABI')
                source.write_bytes(data)
                kernel.prelink(ctx, adreno_abi='built ABI')
            self.assertEqual(output.read_bytes(), data)
            report = json.loads(output.with_suffix('.json').read_text())
            self.assertTrue(report['prelink_skipped'])
            self.assertFalse(report['kernelcache_kexts_added'])
            self.assertEqual(report['candidate_sha256'], hashlib.sha256(data).hexdigest())

    def test_source_gpu_addon_requires_matching_abi_and_kernel(self):
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / 'kernel.macho'
            image.write_bytes(b'prepared kernel')
            record = image.with_suffix('.json')
            metadata = {'candidate_sha256': hashlib.sha256(image.read_bytes()).hexdigest()}
            record.write_text(json.dumps(metadata))
            with self.assertRaisesRegex(Error, 'does not match the Adreno ABI'):
                kernel.require_adreno_abi(image, 'new ABI')
            metadata['adreno_abi_sha256'] = 'old ABI'
            record.write_text(json.dumps(metadata))
            with self.assertRaisesRegex(Error, 'does not match the Adreno ABI'):
                kernel.require_adreno_abi(image, 'new ABI')
            metadata['adreno_abi_sha256'] = 'new ABI'
            record.write_text(json.dumps(metadata))
            kernel.require_adreno_abi(image, 'new ABI')
            image.write_bytes(b'replaced kernel')
            with self.assertRaisesRegex(Error, 'does not match the Adreno ABI'):
                kernel.require_adreno_abi(image, 'new ABI')

    def test_bad_input_preserves_previous_image_and_record(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, output = root / 'input', root / 'kernel.macho'
            output.write_bytes(b'previous')
            output.with_suffix('.json').write_text('{}')
            for data in (b'bad', struct.pack('<8I', 0xfeedfacf, 0x100000c, 2, 12, 0, 0, 0, 0)):
                source.write_bytes(data)
                with self.assertRaisesRegex(Error, 'MH_EXECUTE'):
                    kernel.stage_native(source, output)
                self.assertEqual(output.read_bytes(), b'previous')
                self.assertEqual(output.with_suffix('.json').read_text(), '{}')


if __name__ == '__main__':
    unittest.main()
