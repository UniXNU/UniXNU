"""Reject incomplete EDK II toolchains before kernel work starts."""
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from unixnu import firmware, util


class FirmwareToolchainTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name).resolve() / 'LLVM tools'
        self.directory.mkdir()
        for name in util.CLANGPDB_TOOLS:
            binary = self.directory / name
            binary.write_text('#!/bin/sh\nexit 0\n')
            binary.chmod(0o755)

    def versions(self, command, **kwargs):
        return 'clang version 23.1.3' if Path(command[0]).name == 'clang' else 'LLD 23.1.3'

    def test_prefix_is_normalized_with_or_without_trailing_slash(self):
        with patch.object(util, 'run', side_effect=self.versions):
            for value in (str(self.directory), str(self.directory) + '/'):
                self.assertEqual(util.validate_clang_bin(value), str(self.directory) + '/')

    def test_missing_compiler_is_rejected_before_invoking_tools(self):
        (self.directory / 'clang').unlink()
        with patch.object(util, 'run') as run, self.assertRaisesRegex(util.Error, 'tool missing'):
            util.validate_clang_bin(self.directory)
        run.assert_not_called()

    def test_nonexecutable_auxiliary_tool_is_rejected(self):
        (self.directory / 'llvm-rc').chmod(0o644)
        with self.assertRaisesRegex(util.Error, 'not executable'):
            util.validate_clang_bin(self.directory)

    def test_mixed_releases_are_rejected(self):
        with patch.object(util, 'run', side_effect=['clang version 21.0.0', 'LLD 23.1.3']):
            with self.assertRaisesRegex(util.Error, 'matching LLVM and LLD'):
                util.validate_clang_bin(self.directory)

    def test_unknown_version_is_rejected(self):
        with patch.object(util, 'run', side_effect=['unknown compiler', 'LLD 23.1.3']):
            with self.assertRaisesRegex(util.Error, 'matching LLVM and LLD'):
                util.validate_clang_bin(self.directory)

    def test_explicit_environment_prefix_is_validated(self):
        ctx = SimpleNamespace(work=self.directory.parent, option=lambda *args: os.environ.get('CLANG_BIN'))
        with patch.dict(os.environ, {'CLANG_BIN': str(self.directory)}):
            with patch.object(util, 'run', side_effect=self.versions):
                firmware.preflight_toolchain(ctx)
        self.assertEqual(ctx.firmware_clang_bin, str(self.directory) + '/')
        (self.directory / 'clang').unlink()
        with patch.dict(os.environ, {'CLANG_BIN': str(self.directory)}):
            with self.assertRaisesRegex(util.Error, 'tool missing'):
                firmware.preflight_toolchain(ctx)

    def test_configured_prefix_is_validated(self):
        ctx = SimpleNamespace(work=self.directory.parent, option=lambda *args: str(self.directory))
        with patch.object(util, 'run', side_effect=self.versions):
            firmware.preflight_toolchain(ctx)
        self.assertEqual(ctx.firmware_clang_bin, str(self.directory) + '/')


if __name__ == '__main__':
    unittest.main()
