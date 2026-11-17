"""The standard macOS addon carries the application and its per-user registration job."""
from pathlib import Path
import os
import plistlib
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

ROOT = Path(__file__).resolve().parents[2]


def entries(path):
    data = path.read_bytes()
    assert data[:8] == b'NGPUADD2'
    count, _, size = struct.unpack_from('<IIQ', data, 8)
    assert size == len(data)
    at, files = 24, {}
    for _ in range(count):
        length, mode, size, packed = struct.unpack_from('<IIQQ', data, at)
        at += 24
        name = data[at:at + length - 1].decode()
        at += (length + 7) & ~7
        body = zlib.decompress(data[at:at + packed])
        assert len(body) == size
        files[name] = mode, body
        at += (packed + 7) & ~7
    assert at == len(data)
    return files


class ShaderCacheAddon(unittest.TestCase):
    def fixture(self, root):
        plugin = root / 'NativeAdrenoMetal.bundle/Contents/MacOS/NativeAdrenoMetal'
        plugin.parent.mkdir(parents=True)
        plugin.write_bytes(b'plugin fixture')
        contents = root / 'Shader Cache.app/Contents'
        (contents / 'MacOS').mkdir(parents=True)
        for name in ('ShaderCache', 'ShaderCacheWorker', 'ShaderCacheRegister'):
            (contents / 'MacOS' / name).write_bytes(name.encode())
        (contents / 'Info.plist').write_bytes(plistlib.dumps({'CFBundleIdentifier':'org.unixnu.ShaderCache'}))

    def pack(self, root, prefix):
        output = root / 'addon.bin'
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/make-gpu-addon.py'),
            '--no-daemon', '--prefix', prefix, str(output)],
            env=dict(os.environ, ADRENO_PLUGIN_DIR=str(root)), capture_output=True, text=True)
        return result, output

    def test_macos_installs_the_real_application_and_session_job(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            result, output = self.pack(root, 'GPUBundles')
            self.assertEqual(result.returncode, 0, result.stderr)
            files = entries(output)
            executable = 'Applications/Shader Cache.app/Contents/MacOS/'
            self.assertEqual(files[executable + 'ShaderCacheRegister'][0], 0o755)
            self.assertEqual(files[executable + 'ShaderCacheWorker'][1], b'ShaderCacheWorker')
            self.assertFalse(any(name.startswith('GPUBundles/Shader Cache.app/') for name in files))
            job_mode, job_data = files['Library/LaunchAgents/org.unixnu.ShaderCache.register.plist']
            job = plistlib.loads(job_data)
            self.assertEqual(job_mode, 0o644)
            self.assertEqual(job['ProgramArguments'], ['/' + executable + 'ShaderCacheRegister'])
            self.assertTrue(job['RunAtLoad'])
            self.assertEqual(job['LimitLoadToSessionType'], 'Aqua')
            self.assertNotIn('UserName', job)
            self.assertNotIn('KeepAlive', job)

    def test_ipados_does_not_get_the_macos_application_or_agent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            result, output = self.pack(root, 'addons')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(any(name.startswith(('Applications/', 'Library/LaunchAgents/')) for name in entries(output)))

    def test_missing_registration_helper_refuses_an_incomplete_package(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            (root / 'Shader Cache.app/Contents/MacOS/ShaderCacheRegister').unlink()
            result, output = self.pack(root, 'GPUBundles')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('registration helper', result.stderr)
            self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
