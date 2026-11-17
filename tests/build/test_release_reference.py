"""Keep compilation failures distinct from repairable comparison-link failures."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('release_reference', ROOT / 'scripts/build-fileset-release-reference.py')
reference = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reference)


class ReleaseReferenceTests(unittest.TestCase):
    def test_reference_uses_the_same_iokit_abi_as_its_archives(self):
        self.assertEqual(reference.target_define('macosx'), '-DXNU_TARGET_OS_OSX')
        self.assertEqual(reference.target_define('ios'), '-DXNU_TARGET_OS_IOS')
        with self.assertRaises(SystemExit):
            reference.target_define('unknown')

    def test_compiler_error_wins_over_missing_or_stale_filelist(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            error = 'source/osfmk/arm64/sleh.c:615:3: error: call to undeclared function add_saved_state_pc'
            for stale in (False, True):
                if stale:
                    (directory / 'nonltolink.filelist').write_text('old.o\n')
                with self.assertRaises(SystemExit) as caught:
                    reference.require_link_phase(directory, True, 2, error, directory / 'build.log')
                self.assertIn(error, str(caught.exception))

    def test_missing_filelist_reports_log_without_reading_it(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            with self.assertRaises(SystemExit) as caught:
                reference.require_link_phase(directory, False, 2, 'make failed', directory / 'build.log')
            self.assertIn('Link input list was not generated', str(caught.exception))
            self.assertIn('build.log', str(caught.exception))

    def test_link_failure_can_repair_exports_with_complete_inputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            for lto, filename in [(True, 'nonltolink.filelist'), (False, 'link.filelist')]:
                (directory / filename).write_text('current.o\n')
                reference.require_link_phase(directory, lto, 2, 'Undefined symbols for architecture arm64e',
                                             directory / 'build.log')


if __name__ == '__main__':
    unittest.main()
