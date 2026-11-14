#!/usr/bin/env python3
"""Check administrator identity and credential input without attaching images."""
import argparse
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import plistlib
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[2] / 'scripts/make-macos-data-seed.py'
SPEC = importlib.util.spec_from_file_location('data_seed', SOURCE)
SEED = importlib.util.module_from_spec(SPEC)
# Image packing is outside this host fixture; the account functions are unchanged.
with patch.dict(sys.modules, {'packed_ramdisk': types.ModuleType('packed_ramdisk')}):
    SPEC.loader.exec_module(SEED)


class AccountTest(unittest.TestCase):
    def options(self, user=None, stdin=False, real_name=None):
        return argparse.Namespace(user=user, user_stdin=stdin, real_name=real_name)

    def test_private_input_and_colon_password(self):
        args = self.options(stdin=True, real_name='UniXNU')
        with patch.object(sys, 'stdin', io.StringIO(json.dumps({'name': 'unixnu', 'password': 'a:b c'}))):
            SEED.read_account(argparse.ArgumentParser(), args)
        self.assertEqual(args.user, 'unixnu:a:b c')

    def test_invalid_accounts_and_redacted_errors(self):
        for user in ('../escape:secret', 'root:secret', 'unixnu:', 'unixnu', 'unixnu:a\0b'):
            with self.subTest(user=user), contextlib.redirect_stderr(io.StringIO()) as errors:
                with self.assertRaises(SystemExit):
                    SEED.read_account(argparse.ArgumentParser(), self.options(user=user))
                self.assertNotIn('secret', errors.getvalue())

    def test_invalid_json(self):
        for data in ('{}', '[]', 'null', '{"name":2,"password":"secret"}',
                     '{"name":"bad:name","password":"secret"}', 'not json'):
            with self.subTest(data=data), patch.object(sys, 'stdin', io.StringIO(data)):
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    SEED.read_account(argparse.ArgumentParser(), self.options(stdin=True))

    def test_display_name_requires_account(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            SEED.read_account(argparse.ArgumentParser(), self.options(real_name='UniXNU'))

    def test_record_display_name_and_auto_login_use_separate_fields(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(SEED.os, 'chown'):
            root = Path(directory)
            node = root / SEED.DSLOCAL
            (node / 'groups').mkdir(parents=True)
            for group in ('admin', 'staff'):
                (node / 'groups' / (group + '.plist')).write_bytes(plistlib.dumps({'users': ['existing']}))
            SEED.add_user(node, 'unixnu', 'test-only-password', real_name='UniXNU')
            SEED.add_auto_login(root, 'unixnu', 'test-only-password')
            user = plistlib.loads((node / 'users/unixnu.plist').read_bytes())
            self.assertEqual(user['name'], ['unixnu'])
            self.assertEqual(user['realname'], ['UniXNU'])
            self.assertEqual(user['home'], ['/Users/unixnu'])
            login = plistlib.loads((root / SEED.LOGINWINDOW_PREFS).read_bytes())
            self.assertEqual(login['autoLoginUser'], 'unixnu')
            self.assertNotIn(b'test-only-password', (node / 'users/unixnu.plist').read_bytes())
            for group in ('admin', 'staff'):
                record = plistlib.loads((node / 'groups' / (group + '.plist')).read_bytes())
                self.assertEqual(record['users'], ['existing', 'unixnu'])
            self.assertEqual((root / SEED.KCPASSWORD).stat().st_mode & 0o777, 0o600)


if __name__ == '__main__':
    unittest.main()
