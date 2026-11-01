"""A cached comparison kernel must belong to the requested build inputs."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    'reference', Path(__file__).with_name('build-fileset-release-reference.py'))
reference = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reference)


class ReferenceCacheTests(unittest.TestCase):
    def test_lto_filelist_paths_are_relative_to_the_object_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'nonltolink.filelist').write_text('lastkernelconstructor.o\nnonlto.o\n')
            self.assertEqual(reference.linked_objects(root, True),
                             [str(root / name) for name in
                              ('lastkernelconstructor.o', 'nonlto.o', 'justlto.o')])

    def test_builder_rebuilds_snapshot_as_lto_then_reuses_matching_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            files = ['.cache/xnu-work/osfmk/arm64/sleh.c',
                     '.cache/xnu-work/config/Private.exports',
                     '.cache/xnu-work/config/Private.arm64.exports',
                     '.cache/fakeroot/usr/include/header.h',
                     'build/corecrypto-2023/libcorecrypto_kernel_noasm-namespaced.a',
                     'build/libpthread-kernel/libpthread_kernel.a',
                     'build/armdt-platform/libArmDTPlatform.a',
                     'build/armcpu/libArmCpu.a']
            for name in files:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('')
            builds = []

            def make(command, **kwargs):
                if command[:2] == ['xcrun', 'nm']:
                    return SimpleNamespace(returncode=0, stdout='')
                values = dict(arg.split('=', 1) for arg in command if '=' in arg)
                mode = values['BUILD_LTO']
                builds.append(mode)
                output = Path(values['OBJROOT']) / 'RELEASE_ARM64_BCM2837'
                output.mkdir(parents=True, exist_ok=True)
                if mode == '1':
                    (output / 'nonltolink.filelist').write_text('')
                    (output / 'justlto.o').write_bytes(b'object')
                else:
                    (output / 'link.filelist').write_text('')
                (output / 'mach.release.bcm2837.unstripped').write_text(mode)
                return SimpleNamespace(returncode=0)

            argv = ['reference', '--tree', str(root)]
            with patch.object(reference.subprocess, 'run', side_effect=make), \
                    patch.object(reference.subprocess, 'check_output', return_value='compiler'), \
                    patch('sys.argv', argv):
                reference.main()
                self.assertEqual(builds, ['0', '0'])
                argv.append('--lto')
                reference.main()
                self.assertEqual(builds, ['0', '0', '1', '1'])
                reference.main()
                self.assertEqual(builds, ['0', '0', '1', '1'])
                final = root / 'build/xnu/fileset-reference/mach.release.bcm2837.unstripped.noctf'
                self.assertEqual(final.read_text(), '1')

    def test_old_snapshot_cannot_satisfy_lto_request(self):
        with tempfile.TemporaryDirectory() as directory:
            final = Path(directory) / 'reference'
            record = Path(directory) / 'record.json'
            final.write_bytes(b'comparison kernel')
            snapshot = {'mode': 'snapshot', 'source': 'old'}
            self.assertFalse(reference.reusable(final, record, snapshot))
            record.write_text(json.dumps({'inputs': snapshot, 'sha256': reference.file_hash(final)}))
            self.assertTrue(reference.reusable(final, record, snapshot))
            self.assertFalse(reference.reusable(final, record, dict(snapshot, mode='lto')))
            self.assertFalse(reference.reusable(final, record, dict(snapshot, source='changed')))
            final.write_bytes(b'corrupt kernel')
            self.assertFalse(reference.reusable(final, record, snapshot))

    def test_source_content_and_linked_sdk_headers_invalidate_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'source'
            source.mkdir()
            header = source / 'header.h'
            header.write_text('old')
            timestamp = header.stat().st_mtime_ns
            first = reference.tree_hash(source)
            header.write_text('new')
            os.utime(header, ns=(timestamp, timestamp))
            self.assertNotEqual(first, reference.tree_hash(source))
            sdk = root / 'sdk'
            sdk.mkdir()
            (sdk / 'include').symlink_to(source, target_is_directory=True)
            first = reference.tree_hash(sdk)
            header.write_text('next')
            self.assertNotEqual(first, reference.tree_hash(sdk))


if __name__ == '__main__':
    unittest.main()
