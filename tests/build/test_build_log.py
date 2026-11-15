#!/usr/bin/env python3
"""Check prefix colors, raw logs, streaming prompts and command exit status."""
import importlib.util
import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import sys
import tempfile
import time
import unittest
import pty

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('build_log', ROOT / 'scripts/build-log.py')
LOG = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LOG)


class BuildLogTest(unittest.TestCase):
    def terminal(self, command, environment):
        master, slave = pty.openpty()
        child = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=slave, stderr=slave, env=environment)
        os.close(slave)
        output = bytearray()
        try:
            deadline = time.monotonic() + 8
            with selectors.DefaultSelector() as selector:
                selector.register(master, selectors.EVENT_READ)
                while time.monotonic() < deadline:
                    if not selector.select(timeout=0.1):
                        continue
                    try:
                        chunk = os.read(master, 65536)
                    except OSError:
                        break
                    if not chunk:
                        break
                    output.extend(chunk)
            return child.wait(timeout=2), bytes(output)
        finally:
            os.close(master)
            if child.poll() is None:
                child.kill()
                child.wait()

    def test_standard_entry_colors_without_wrapper(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            device = root / 'device'
            (device / 'configs').mkdir(parents=True)
            (device / 'board.toml').write_text('[board]\nname = "fixture"\n')
            (device / 'configs/fixture_defconfig').write_text('CONFIG_XNU_NATIVE_UFS=y\n')
            command = [sys.executable, ROOT / 'unixnu', 'defconfig', 'fixture_defconfig',
                       '-D', device, '--out', root / 'out']
            environment = {key: value for key, value in os.environ.items() if key != 'NO_COLOR'}
            environment['TERM'] = 'xterm-256color'
            code, output = self.terminal(command, environment)
            self.assertEqual(code, 0)
            self.assertIn(b'\x1b[94m== configuration', output)
            for changes in ({'NO_COLOR': '1'}, {'TERM': 'dumb'}):
                with self.subTest(changes=changes):
                    code, output = self.terminal(command, dict(environment, **changes))
                    self.assertEqual(code, 0)
                    self.assertNotIn(b'\x1b[', output)
            result = subprocess.run(command, capture_output=True, env=environment)
            self.assertEqual(result.returncode, 0)
            self.assertNotIn(b'\x1b[', result.stdout + result.stderr)
            code, output = self.terminal([sys.executable, ROOT / 'unixnu', 'status', '--json',
                                          '-D', device, '--out', root / 'out'], environment)
            self.assertEqual(code, 0)
            self.assertNotIn(b'\x1b[', output)
            record = json.loads(output[output.index(b'{'):])
            self.assertEqual(record['name'], 'fixture')

    def test_prefix_colors_and_unchanged_text(self):
        for line, color in (('[INFO] Compiling', 'info'), ('[OK] Done', 'ok'),
                            ('[WARN] Retry', 'warning'), ('[FAILED] Compiler', 'error'),
                            ('[notice] A new release of pip is available', 'info'),
                            ('Processing /tmp/pip.whl', 'info'), ('Collecting setuptools', 'info'),
                            ('Installing collected packages: pip', 'info'),
                            ('Successfully installed pip-26.3', 'ok'), ('Successfully uninstalled pip-26.2.2', 'ok'),
                            ('Successfull', 'ok'), ('Using cached wheel.whl', 'ok'),
                            ('Requirement already satisfied: pip', 'ok'),
                            ('== fetch - source', 'info'), ('==> Downloading dependency', 'info'),
                            ('== payload: payload.img', 'info'), ('+ clang -c source.c', 'info'),
                            ('PASS: fixture', 'ok'), ('FAIL: fixture', 'error'),
                            ('** BUILD SUCCEEDED **', 'ok'), ('** BUILD FAILED **', 'error'),
                            ('CMake Warning at CMakeLists.txt:4', 'warning'),
                            ('unixnu: clang failed (1)', 'error'),
                            ('== build - kernel - complete', 'ok'), ('1/5 - Sources', 'info'),
                            ('source.c:4:2: fatal error: missing header', 'error'),
                            ('source.c:4:2: warning: unused', 'warning')):
            with self.subTest(line=line):
                rendered = LOG.render(line, True)
                self.assertIn(LOG.COLORS[color], rendered)
                self.assertEqual(LOG.ANSI.sub('', rendered), line)
                self.assertEqual(LOG.render(line, False), line)

    def test_mixed_and_continued_pip_notices(self):
        text = 'Successfully installed pip [notice] A new release is available\n'
        rendered = LOG.render(text, True)
        self.assertIn('\033[92mSuccessfully installed\033[0m', rendered)
        self.assertIn('\033[94m[notice]\033[0m', rendered)
        self.assertEqual(LOG.ANSI.sub('', rendered), text)
        self.assertIn('\033[94m[notice]', LOG.render(' [notice] update', True, line_start=False))
        for line in ('/tmp/error/input.c', 'pip-26.2.2-py3-none-any.whl', '50% 1024/2048 bytes'):
            self.assertEqual(LOG.render(line, True), line)

    def test_output_and_exit_code(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / 'build.log'
            code = "import sys;sys.stdout.write('[INFO] run\\r50%\\r100%\\n');sys.stdout.flush();sys.stderr.write('[ERROR] failed\\n');sys.exit(7)"
            result = subprocess.run([sys.executable, ROOT / 'scripts/build-log.py', '--log', log,
                                     '--color', 'always', '--', sys.executable, '-c', code],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    env={key: value for key, value in os.environ.items() if key != 'NO_COLOR'})
            self.assertEqual(result.returncode, 7)
            self.assertIn(b'\x1b[94m[INFO]', result.stdout)
            self.assertIn(b'\x1b[91m[ERROR]', result.stdout)
            self.assertEqual(log.read_bytes(), b'[INFO] run\r50%\r100%\n[ERROR] failed\n')
            self.assertEqual(LOG.ANSI.sub('', result.stdout.decode()).encode(), log.read_bytes())

    def test_no_color_and_nonterminal_output(self):
        with tempfile.TemporaryDirectory() as directory:
            for mode, no_color in (('auto', False), ('always', True)):
                environment = {key: value for key, value in os.environ.items() if key != 'NO_COLOR'}
                if no_color:
                    environment['NO_COLOR'] = '1'
                with self.subTest(mode=mode, no_color=no_color):
                    result = subprocess.run([sys.executable, ROOT / 'scripts/build-log.py',
                                             '--log', Path(directory) / 'build.log', '--color', mode, '--',
                                             sys.executable, '-c', "print('[OK] Done')"],
                                            capture_output=True, env=environment)
                    self.assertEqual(result.returncode, 0)
                    self.assertEqual(result.stdout, b'[OK] Done\n')

    def test_partial_prompt_and_interrupt(self):
        with tempfile.TemporaryDirectory() as directory:
            code = "import time;print('Prompt: ',end='',flush=True);time.sleep(30)"
            child = subprocess.Popen([sys.executable, ROOT / 'scripts/build-log.py', '--log', Path(directory) / 'build.log',
                                      '--', sys.executable, '-c', code],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                with selectors.DefaultSelector() as selector:
                    selector.register(child.stdout, selectors.EVENT_READ)
                    self.assertTrue(selector.select(timeout=3), 'partial prompt was buffered')
                    self.assertEqual(os.read(child.stdout.fileno(), 8), b'Prompt: ')
                child.send_signal(signal.SIGINT)
                child.communicate(timeout=5)
                self.assertEqual(child.returncode, 130)
            finally:
                if child.poll() is None:
                    child.kill()
                    child.communicate()


if __name__ == '__main__':
    unittest.main()
