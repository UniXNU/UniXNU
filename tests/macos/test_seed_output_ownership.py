#!/usr/bin/env python3
"""Keep newly created seed output directories writable by the build user."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import call, patch

SOURCE = Path(__file__).resolve().parents[2] / 'scripts/make-macos-data-seed.py'
sys.path.insert(0, str(SOURCE.parent))
spec = importlib.util.spec_from_file_location('seed_output', SOURCE)
seed = importlib.util.module_from_spec(spec)
with patch.dict(sys.modules, {'packed_ramdisk': types.ModuleType('packed_ramdisk')}):
    spec.loader.exec_module(seed)


class SeedOutputOwnershipTest(unittest.TestCase):
    def test_only_new_directories_are_returned_to_the_caller(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(seed.os, 'chown') as chown:
            root = Path(directory)
            target = root / 'new/runtime'
            seed.prepare_output_directory(target, ('501', '20'))
            self.assertTrue(target.is_dir())
            self.assertEqual(chown.call_args_list, [call(root / 'new', 501, 20), call(target, 501, 20)])

    def test_existing_directory_is_unchanged(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(seed.os, 'chown') as chown:
            seed.prepare_output_directory(Path(directory), ('501', '20'))
            chown.assert_not_called()

    def test_direct_root_invocation_keeps_root_ownership(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(seed.os, 'chown') as chown:
            target = Path(directory) / 'runtime'
            seed.prepare_output_directory(target, (None, None))
            self.assertTrue(target.is_dir())
            chown.assert_not_called()

    def test_file_in_output_path_is_refused(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(seed.os, 'chown') as chown:
            target = Path(directory) / 'file'
            target.touch()
            with self.assertRaises(NotADirectoryError):
                seed.prepare_output_directory(target / 'runtime', ('501', '20'))
            chown.assert_not_called()


if __name__ == '__main__':
    unittest.main()
