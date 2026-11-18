"""The macOS desktop image drops the icon stores once whenever the GPU plugin's build record changes."""
from pathlib import Path
import importlib.util
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('build_boot_runtime', ROOT / 'scripts/build-boot-runtime.py')
RUNTIME = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNTIME)

BUILD = 'Library/GPUBundles/NativeAdrenoMetal.bundle/Contents/Resources/gpu-build.json'
SYSTEM_STORE = 'Library/Caches/com.apple.iconservices.store'
USER_CACHE = 'private/var/folders/qy/abc/C'
STAMP = 'private/var/db/unixnu/icon-cache-build'


class IconCacheJob(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)

    def tearDown(self):
        self.directory.cleanup()

    def stores(self):
        """The icon stores of the system and one user, another cache of that user, and the plugin's own cache of the agent."""
        paths = [self.root / SYSTEM_STORE / 'a.isdata', self.root / USER_CACHE / 'com.apple.iconservices/store.index',
                 self.root / USER_CACHE / 'com.apple.iconservices.store/b.isdata',
                 self.root / USER_CACHE / 'com.apple.dock.iconcache',
                 self.root / USER_CACHE / 'com.apple.iconservicesagent/com.apple.metal/m2v/pipelines.log']
        for path in paths:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('kept\n')
        return paths

    def build(self, text):
        path = self.root / BUILD
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def clear(self):
        command = RUNTIME.ICON_CACHE_FUNCTION + 'restart_icon_services() { :; }\nclear_stale_icon_caches "$1"'
        return subprocess.run(['/bin/sh', '-c', command, 'test', str(self.root)],
                              capture_output=True, text=True).returncode

    def test_stores_go_once_per_plugin_build_and_other_caches_stay(self):
        system, index, user, dock, pipelines = self.stores()
        self.build('{"component": "one"}\n')
        self.assertEqual(self.clear(), 0)
        self.assertFalse(system.exists() or index.exists() or user.exists())
        self.assertFalse((self.root / SYSTEM_STORE).exists())
        self.assertTrue(dock.exists() and pipelines.exists())
        self.assertTrue((self.root / STAMP).read_text().strip())

        system, index, user, _, _ = self.stores()
        self.assertEqual(self.clear(), 0)
        self.assertTrue(system.exists() and index.exists() and user.exists())

        self.build('{"component": "two"}\n')
        self.assertEqual(self.clear(), 0)
        self.assertFalse(system.exists() or index.exists() or user.exists())
        self.assertEqual(self.clear(), 0)

    def test_an_image_without_the_plugin_keeps_its_stores(self):
        paths = self.stores()
        self.assertEqual(self.clear(), 0)
        self.assertTrue(all(path.exists() for path in paths))
        self.assertFalse((self.root / STAMP).exists())

    def test_the_job_runs_as_root_at_boot_for_manual_sessions(self):
        job = RUNTIME.icon_cache_job()
        self.assertEqual(job['Label'], 'org.unixnu.icon-cache.generation')
        self.assertIs(job['RunAtLoad'], True)
        self.assertNotIn('UserName', job)
        self.assertEqual(job['ProgramArguments'][:2], ['/bin/sh', '-c'])
        command = job['ProgramArguments'][2]
        self.assertTrue(command.startswith(RUNTIME.ICON_CACHE_FUNCTION))
        self.assertIn('/private/var/ngpu/test/share/manual-session', command)


if __name__ == '__main__':
    unittest.main()
