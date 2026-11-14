#!/usr/bin/env python3
"""Exercise Data seed tools with fresh output paths and mocked macOS disk tools."""
import contextlib
import hashlib
import importlib.util
import io
from pathlib import Path
import plistlib
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]


def load(script):
    spec = importlib.util.spec_from_file_location(script, ROOT / 'scripts' / script)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {'packed_ramdisk': types.ModuleType('packed_ramdisk')}):
        spec.loader.exec_module(module)
    return module


class SeedWorkdirTest(unittest.TestCase):
    def setUp(self):
        self.temporary = self.enterContext(tempfile.TemporaryDirectory())
        self.root = Path(self.temporary).resolve()
        self.base = self.root / 'base.dbr'
        self.base.write_bytes(b'original seed')
        self.output = self.root / 'nested/output/data.dbr'
        self.header = bytearray(4096)
        self.header[32:36] = b'NXSB'
        self.header[36:40] = (4096).to_bytes(4, 'little')
        self.pack = Mock(side_effect=self.pack_image)
        self.packed = types.SimpleNamespace(regions=lambda _blob: (4 << 20, [(0, self.header)]), pack=self.pack,
                                            inspect=lambda _base: ({'sha256': hashlib.sha256(self.base.read_bytes()).hexdigest()}, self.header))
        self.enterContext(contextlib.redirect_stdout(io.StringIO()))

    def pack_image(self, raw, output):
        self.assertEqual(raw.parent.parent, self.output.parent)
        with raw.open('rb') as handle:
            self.assertEqual(handle.read(36)[32:36], b'NXSB')
        output.write_bytes(b'new packed seed')
        return {'bytes': raw.stat().st_size}

    def module(self, script):
        module = load(script)
        module.ROOT = self.root / 'checkout'
        module.packed_ramdisk = self.packed
        return module

    def grow(self, failure=None):
        module = self.module('seed-data-grow.py')
        raw = None

        def disk_command(*args):
            nonlocal raw
            if args[:2] == ('hdiutil', 'attach'):
                raw = Path(args[-1])
                return '/dev/disk99 Apple_APFS\n'
            self.assertEqual(args, ('diskutil', 'apfs', 'resizeContainer', 'disk100', '0'))
            if failure == 'resize':
                raise subprocess.CalledProcessError(1, args)
            with raw.open('r+b') as handle:
                handle.seek(40)
                handle.write((raw.stat().st_size // 4096).to_bytes(8, 'little'))

        listing = plistlib.dumps({'Containers': [{'ContainerReference': 'disk100',
                                 'PhysicalStores': [{'DeviceIdentifier': 'disk99'}]}]})
        detach = Mock(return_value=subprocess.CompletedProcess([], 0))
        if failure == 'detach':
            detach.side_effect = subprocess.CalledProcessError(1, ['hdiutil', 'detach'])
        with patch.object(sys, 'argv', ['grow', '--gib', '3', str(self.base), str(self.output)]), \
                patch.object(module, 'run', side_effect=disk_command), \
                patch.object(module.subprocess, 'check_output', return_value=listing), \
                patch.object(module.subprocess, 'run', detach):
            module.main()
        self.assertEqual(detach.call_args.kwargs['check'], True)
        self.assertFalse((module.ROOT / 'build').exists())

    def test_grow_without_repository_build_or_output_directory(self):
        self.grow()
        self.assertEqual(self.output.read_bytes(), b'new packed seed')
        self.assertEqual(self.base.read_bytes(), b'original seed')
        self.assertFalse(list(self.output.parent.glob('data-grow-*')))

    def test_resize_failure_preserves_input_without_publishing_output(self):
        with self.assertRaises(subprocess.CalledProcessError):
            self.grow('resize')
        self.pack.assert_not_called()
        self.assertFalse(self.output.exists())
        self.assertEqual(self.base.read_bytes(), b'original seed')

    def test_detach_failure_prevents_packing(self):
        with self.assertRaises(subprocess.CalledProcessError):
            self.grow('detach')
        self.pack.assert_not_called()
        self.assertFalse(self.output.exists())

    def test_existing_output_is_preserved(self):
        module = self.module('seed-data-grow.py')
        self.output.parent.mkdir(parents=True)
        self.output.write_bytes(b'existing installation')
        with patch.object(sys, 'argv', ['grow', '--gib', '3', str(self.base), str(self.output)]), self.assertRaises(SystemExit):
            module.main()
        self.assertEqual(self.output.read_bytes(), b'existing installation')

    def stage(self, script):
        module = self.module(script)
        if script == 'add-gpu-plugin-data.py':
            module.BUNDLE = module.ROOT / 'build/adreno-metal-plugin/NativeAdrenoMetal.bundle'
            module.BUNDLE.mkdir(parents=True)
            (module.BUNDLE / 'NativeAdrenoMetal').write_bytes(b'test plugin')
            (module.BUNDLE.parent / 'adrenoprobed').write_bytes(b'test daemon')
            (module.BUNDLE.parent / 'trust.json').write_text('{}')

        def attach(args):
            mount = Path(args[args.index('-mountpoint') + 1])
            (mount / 'mobile').mkdir()
            return plistlib.dumps({'system-entities': [{'dev-entry': '/dev/disk99'}]})

        with patch.object(sys, 'argv', [script, str(self.base), str(self.output)]), \
                patch.object(module.subprocess, 'check_output', side_effect=attach), \
                patch.object(module.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0)):
            module.main()
        self.assertEqual(self.output.read_bytes(), b'new packed seed')
        self.assertEqual(self.base.read_bytes(), b'original seed')

    def test_skip_setup_with_fresh_directories(self):
        self.stage('seed-data-skip-setup.py')

    def test_plugin_staging_with_nested_output_directory(self):
        self.stage('add-gpu-plugin-data.py')


if __name__ == '__main__':
    unittest.main()
