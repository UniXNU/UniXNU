#!/usr/bin/env python3
"""Offline tests: GPT preservation, size rounding, ADB selection and failure ordering."""
import hashlib
import io
import json
import os
from pathlib import Path
import shlex
import shutil
import struct
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch
import uuid
import zlib

from gpt import GPT, size_bytes
from partition import ADB, expected_blocks, prepare

HERE = Path(__file__).resolve().parent


def fixture(sector=4096, count=128, total=None, user_start=None):
    total = total or 64 * (1 << 30) // sector
    blocks = max(16384, count * 128) // sector
    table = bytearray(blocks * sector)
    for i, name, start, end in ((0, 'metadata', 2 + blocks, (1 << 20) // sector - 1),
                               (1, 'userdata', user_start or (1 << 20) // sector, total - 1 - blocks - 1)):
        offset = i * 128
        table[offset:offset + 16] = uuid.uuid4().bytes_le
        table[offset + 16:offset + 32] = uuid.uuid4().bytes_le
        struct.pack_into('<QQQ', table, offset + 32, start, end, 0x1000000000000000)
        label = name.encode('utf-16-le')
        table[offset + 56:offset + 56 + len(label)] = label
    guid = uuid.uuid4().bytes_le

    def hdr(lba, other, entries):
        result = bytearray(sector)
        struct.pack_into('<8sIIIIQQQQ16sQIII', result, 0, b'EFI PART', 0x10000, 92, 0, 0,
                         lba, other, 2 + blocks, total - blocks - 2, guid, entries, count, 128,
                         zlib.crc32(table[:count * 128]))
        struct.pack_into('<I', result, 16, zlib.crc32(result[:92]))
        return result

    mbr = bytearray(sector)
    mbr[450] = 0xee
    mbr[510:512] = b'\x55\xaa'
    return GPT(bytes(mbr + hdr(1, total - 1, 2) + table),
               bytes(table + hdr(total - 1, 1, total - 1 - blocks)), sector, total)


class LayoutTests(unittest.TestCase):
    def test_recorded_oneplus_geometry(self):
        old = fixture(4096, 32, total=61706240, user_start=4020972)
        _, _, layout = old.split(64 << 30, 2)
        self.assertEqual(layout['unixnu_start'], 44928768)
        self.assertEqual(layout['unixnu_end'], 61705983)
        self.assertEqual(layout['new_userdata_bytes'] // 4096, 40907796)
        self.assertEqual(layout['old_userdata_bytes'] // 4096, 57685263)

    def test_small_entry_array_keeps_reserved_gpt_space(self):
        old = fixture(4096, 32)
        self.assertEqual(old.h['blocks'], 4)
        p, b, _ = old.split(8 << 30, 2)
        new = GPT(p, b, 4096, old.total)
        self.assertEqual(new.primary[3 * 4096:], old.primary[3 * 4096:])
        self.assertEqual(new.backup[4096:-4096], old.backup[4096:-4096])

    def test_preserve_existing_entries_and_guids(self):
        for sector in (512, 4096):
            old = fixture(sector)
            p, b, layout = old.split(8 << 30, 2)
            new = GPT(p, b, sector, old.total)
            self.assertEqual(new.table[:128], old.table[:128])
            self.assertEqual(new.table[128:168], old.table[128:168])
            self.assertEqual(new.table[176:256], old.table[176:256])
            self.assertEqual(new.primary[:sector], old.primary[:sector])
            self.assertEqual(new.h['guid'], old.h['guid'])
            self.assertEqual(layout['unixnu_start'] * sector % (1 << 20), 0)
            self.assertEqual(layout['unixnu_bytes'], 8 << 30)
            self.assertLess(layout['tail_gap_bytes'], 1 << 20)
            self.assertEqual(layout['new_userdata_bytes'] + layout['unixnu_bytes'] + layout['tail_gap_bytes'],
                             layout['old_userdata_bytes'])
            with self.assertRaisesRegex(ValueError, 'already exists'):
                new.split(4 << 30, 2)

    def test_reject_bad_gpt_and_size(self):
        old = fixture()
        for offset in (4096 + 16, 8192 + 32):
            bad = bytearray(old.primary)
            bad[offset] ^= 1
            with self.assertRaises(ValueError):
                GPT(bytes(bad), old.backup, old.sector, old.total)
        with self.assertRaisesRegex(ValueError, 'identity'):
            old.split(8 << 30, 1)
        with self.assertRaises(ValueError):
            old.split(128 << 30, 2)
        for size in ('0', '-1', 'nan', 'inf', 'garbage', '0.000001'):
            with self.assertRaises(ValueError):
                size_bytes(size)
        self.assertEqual(size_bytes('1.5'), 3 << 29)

    def test_section_rounding(self):
        self.assertEqual(expected_blocks(57685263, 40907796), 40907535)
        for rem in range(512):
            old = 20000 * 512 + rem
            limit = 9000 * 512 + 101
            result = expected_blocks(old, limit)
            self.assertLessEqual(result, limit)
            self.assertEqual((old - result) % 512, 0)
            self.assertLess(limit - result, 512)
        self.assertEqual(expected_blocks(40907535, 40907796), 40907535)

    def test_adb_selection(self):
        for listing in ('', 'a\tunauthorized\n', 'a\tdevice\nb\tdevice\n'):
            with patch('partition.subprocess.run', return_value=subprocess.CompletedProcess([], 0, 'List of devices attached\n' + listing)):
                with self.assertRaises(ValueError):
                    ADB('adb')
        with patch('partition.subprocess.run', return_value=subprocess.CompletedProcess([], 0, 'List of devices attached\na\trecovery\nb\tdevice\n')):
            self.assertEqual(ADB('adb', 'a').serial, 'a')


class HostTests(unittest.TestCase):
    def test_apply_requires_confirmation_without_a_backup_flag(self):
        gpt = fixture()
        user = gpt.entries[1]
        part_bytes = (user['end'] - user['start'] + 1) * 4096
        info = dict(index=2, disk='/dev/block/testdisk', raw='/dev/block/testpart',
                    hardware_serial='test', kernel='test-kernel', total_bytes=gpt.total * 4096,
                    sector=4096, machine='aarch64')
        fs = dict(partition_bytes=part_bytes, blocks=part_bytes // 4096,
                  available_blocks=part_bytes // 4096, mapped='/dev/block/dm-0')
        for command, confirm in (('plan', 'wrong'), ('apply', 'wrong'), ('apply', 'test unixnu 8589934592')):
            with tempfile.TemporaryDirectory() as name:
                root = Path(name)
                elf = bytearray(64)
                elf[:4], elf[5] = b'\x7fELF', 1
                struct.pack_into('<H', elf, 18, 183)
                (root / 'helper').write_bytes(elf)
                calls = []

                def shell(cmd):
                    calls.append(cmd)
                    if ' probe ' in cmd:
                        return json.dumps(fs)
                    if cmd.startswith('cat '):
                        return str(user['start'] * 8)
                    return ''

                adb = SimpleNamespace(executable='adb', serial='test', shell=shell, push=lambda *a: None,
                                      run=lambda *a: calls.append(' '.join(a)))
                args = SimpleNamespace(helper=root / 'helper', output=root / 'bundle', size_gib='8',
                                       command=command)
                def snapshot(*_):
                    return SimpleNamespace(primary=(root / 'bundle/gpt-primary.after').read_bytes(),
                                           backup=(root / 'bundle/gpt-backup.after').read_bytes())

                with redirect_stdout(io.StringIO()), patch('builtins.input', return_value=confirm), \
                        patch('partition.snapshot', side_effect=snapshot), \
                        patch('partition.subprocess.Popen') as process:
                    process.return_value.stdout = []
                    process.return_value.wait.return_value = 0
                    if command == 'apply' and confirm == 'wrong':
                        with self.assertRaisesRegex(ValueError, 'confirmation'):
                            prepare(adb, args, info, gpt)
                    else:
                        prepare(adb, args, info, gpt)
                    if command == 'apply' and confirm != 'wrong':
                        process.assert_called_once()
                        self.assertIn('twrp.sh apply', process.call_args.args[0][-1])
                    else:
                        process.assert_not_called()
                plan = json.loads((root / 'bundle/plan.json').read_text())
                self.assertEqual(plan['layout']['unixnu_bytes'], 8 << 30)
                self.assertNotIn(b'\r', (root / 'bundle/plan.env').read_bytes())
                self.assertTrue(any('twrp.sh check' in call for call in calls))
                self.assertFalse(any('twrp.sh apply' in call for call in calls))


class PortableHelperTests(unittest.TestCase):
    def test_self_test_build_rejects_device_operations(self):
        with tempfile.TemporaryDirectory() as name:
            executable = str(Path(name) / 'f2fs-shrink')
            compiler = shlex.split(os.environ.get('CC', 'cc'))
            subprocess.run([*compiler, '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
                            '-DF2FS_SELF_TEST_ONLY', str(HERE / 'f2fs-shrink.c'), '-o', executable], check=True)
            result = subprocess.run([executable, 'self-test'], capture_output=True, text=True, check=True)
            self.assertIn('PASS: F2FS section rounding', result.stdout)
            for args in (['probe', '/dev/block/test'], ['shrink', '/dev/block/test', '100', '100', '50'],
                         ['offline', '/dev/block/test', '100', '50', '50', '/dev/block/dm-0']):
                result = subprocess.run([executable, *args], capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)
                self.assertIn('self-test only', result.stderr)


class RecoveryTests(unittest.TestCase):
    def run_recovery(self, failure='', action='apply'):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            bindir = root / 'bin'
            bindir.mkdir()
            gpt = fixture()
            p, b, layout = gpt.split(8 << 30, 2)
            for file, data in (('gpt-primary.before', gpt.primary), ('gpt-backup.before', gpt.backup),
                               ('gpt-primary.after', p), ('gpt-backup.after', b),
                               ('disk-primary', gpt.primary), ('disk-backup', gpt.backup)):
                (root / file).write_bytes(data)
            values = dict(DISK='/dev/block/testdisk', RAW='/dev/block/testpart', MAPPED='/dev/block/dm-0',
                          HARDWARE_SERIAL='test', KERNEL='test-kernel', DISK_BYTES=123, SECTOR=4096,
                          BACKUP_LBA=gpt.total - 1 - gpt.h['blocks'], PRIMARY_BLOCKS=6, BACKUP_BLOCKS=5,
                          OLD_BYTES=100, OLD_BLOCKS=100, EXPECTED_BLOCKS=50, LIMIT_BLOCKS=50,
                          USER_START_512=2048, CONFIRM='test unixnu 123')
            (root / 'plan.env').write_text(''.join(f'{k}={shlex.quote(str(v))}\n' for k, v in values.items()))
            shutil.copyfile(HERE / 'twrp.sh', root / 'twrp.sh')
            fake = '''#!/usr/bin/env python3
import hashlib, os, pathlib, sys
cmd = pathlib.Path(sys.argv[0]).name
args = sys.argv[1:]
failure = os.environ.get('TEST_FAILURE', '')
with open('calls', 'a') as log: log.write(cmd + ' ' + ' '.join(args) + '\\n')
if cmd == 'id': print('0')
elif cmd == 'getprop': print({'ro.twrp.version':'test', 'ro.serialno':'test'}.get(args[0], ''))
elif cmd == 'uname': print('test-kernel')
elif cmd == 'readlink': print('/dev/block/testpart')
elif cmd == 'blockdev': print(4096 if args[0] == '--getss' else (100 if args[1].endswith('testpart') else 123))
elif cmd == 'cat': print('2048')
elif cmd == 'umount': sys.exit(1 if failure == 'unmount' else 0)
elif cmd == 'f2fs-shrink': sys.exit(1 if failure == args[0] else 0)
elif cmd == 'sha256sum':
    for line in pathlib.Path(args[-1]).read_text().splitlines():
        digest, name = line.split('  ', 1)
        if hashlib.sha256(pathlib.Path(name).read_bytes()).hexdigest() != digest: sys.exit(1)
elif cmd == 'mkdir':
    target = 'global-lock' if args[0] == '/tmp/unixnu-dual.lock' else args[0]
    if failure == 'locked' and target == 'global-lock': sys.exit(1)
    pathlib.Path(target).mkdir()
elif cmd == 'dd':
    opts = dict(arg.split('=', 1) for arg in args)
    if opts['if'].startswith('/dev/'):
        source = 'disk-backup' if 'skip' in opts else 'disk-primary'
        pathlib.Path(opts['of']).write_bytes(pathlib.Path(source).read_bytes())
    else:
        target = 'disk-backup' if 'seek' in opts else 'disk-primary'
        data = pathlib.Path(opts['if']).read_bytes()
        if failure == 'readback' and target == 'disk-backup': data = bytes(len(data))
        pathlib.Path(target).write_bytes(data)
'''
            for command in ('id', 'getprop', 'uname', 'readlink', 'blockdev', 'cat', 'umount', 'dd', 'sync', 'mkdir', 'sha256sum'):
                (bindir / command).write_text(fake)
                (bindir / command).chmod(0o700)
            (root / 'f2fs-shrink').write_text(fake)
            (root / 'f2fs-shrink').chmod(0o700)
            files = ('plan.env', 'twrp.sh', 'f2fs-shrink', 'gpt-primary.before', 'gpt-backup.before', 'gpt-primary.after', 'gpt-backup.after')
            (root / 'SHA256SUMS').write_text(''.join(f'{hashlib.sha256((root / f).read_bytes()).hexdigest()}  {f}\n' for f in files))
            if failure == 'stale':
                (root / 'disk-primary').write_bytes(bytes(len(gpt.primary)))
            env = dict(os.environ, PATH=str(bindir) + ':' + os.environ['PATH'], TEST_FAILURE=failure)
            result = subprocess.run(['sh', str(root / 'twrp.sh'), action, 'test unixnu 123'], env=env,
                                    cwd=root, capture_output=True, text=True)
            calls = (root / 'calls').read_text()
            return result, calls

    def test_no_writes_on_check(self):
        result, calls = self.run_recovery(action='check')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('of=/dev/', calls)
        self.assertNotIn('f2fs-shrink shrink', calls)

    def test_failure_blocks_gpt_writes(self):
        for failure in ('stale', 'locked', 'shrink', 'unmount', 'offline'):
            result, calls = self.run_recovery(failure)
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn('of=/dev/', calls, failure)

    def test_backup_failure_blocks_primary(self):
        result, calls = self.run_recovery('readback')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('dd if=gpt-backup.after of=/dev/', calls)
        self.assertNotIn('dd if=gpt-primary.after of=/dev/', calls)

    def test_success_order(self):
        result, calls = self.run_recovery()
        self.assertEqual(result.returncode, 0, result.stderr)
        stages = ('f2fs-shrink shrink', 'umount /data', 'f2fs-shrink offline',
                  'dd if=gpt-backup.after of=/dev/', 'dd if=gpt-primary.after of=/dev/')
        offsets = [calls.index(s) for s in stages]
        self.assertEqual(offsets, sorted(offsets))


if __name__ == '__main__':
    unittest.main()
