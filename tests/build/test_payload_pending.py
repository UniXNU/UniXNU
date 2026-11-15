#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Do not package an old payload after a failed replacement build."""
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from unixnu import cli, payload
from unixnu.util import Error


class PayloadPendingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='payload-pending-test-')
        self.addCleanup(self.temp.cleanup)
        self.ctx = SimpleNamespace(work=Path(self.temp.name), tree=Path(self.temp.name), board={},
            args=SimpleNamespace(steps=['payload'], dry_run=False, fd='firmware.fd', target=None, output=None, ramdisk=None),
            refuse_example=lambda: None, option=lambda *args: Path('hardware.dtb'))
        self.out, self.image, _ = payload.paths(self.ctx)
        self.out.mkdir()
        self.image.write_bytes(b'old payload')

    def failed_build(self, step):
        with patch.object(cli, 'prepare', return_value={}), patch.object(cli.runtime, 'prepare'), patch.object(cli.payload, 'build'):
            with patch.object(cli if step == 'prepare' else cli.runtime if step == 'runtime' else cli.payload,
                              'prepare' if step in ('prepare', 'runtime') else 'build', side_effect=Error('test failure')):
                with self.assertRaises(Error):
                    cli.cmd_build(self.ctx)
        self.assertEqual(self.image.read_bytes(), b'old payload')
        with patch.object(cli, 'need_uefi', return_value=Path('uefi')), patch.object(cli.bootimg, 'build') as pack:
            with self.assertRaisesRegex(Error, 'latest payload build did not complete'):
                cli.cmd_bootimg(self.ctx)
            pack.assert_not_called()

    def test_failed_prepare_does_not_package_old_payload(self):
        self.failed_build('prepare')

    def test_failed_runtime_does_not_package_old_payload(self):
        self.failed_build('runtime')

    def test_failed_payload_does_not_package_old_payload(self):
        self.failed_build('payload')

    def test_explicit_managed_payload_is_also_refused(self):
        payload.begin_build(self.ctx)
        self.ctx.args.ramdisk = str(self.image)
        with patch.object(cli, 'need_uefi', return_value=Path('uefi')):
            with self.assertRaisesRegex(Error, 'latest payload build did not complete'):
                cli.cmd_bootimg(self.ctx)

    def test_successful_retry_clears_pending_state(self):
        payload.begin_build(self.ctx)
        def build(ctx):
            self.assertTrue((self.out / '.build-pending').exists())
            self.image.write_bytes(b'new payload')
        with patch.object(cli, 'prepare', return_value={}), patch.object(cli.runtime, 'prepare'), patch.object(cli.payload, 'build', side_effect=build):
            cli.cmd_build(self.ctx)
        payload.require_complete(self.ctx)
        with patch.object(cli, 'need_uefi', return_value=Path('uefi')), patch.object(cli.bootimg, 'build') as pack:
            cli.cmd_bootimg(self.ctx)
            pack.assert_called_once()
        self.assertEqual(self.image.read_bytes(), b'new payload')

    def test_empty_menu_ramdisk_does_not_use_managed_payload(self):
        payload.begin_build(self.ctx)
        self.ctx.args.ramdisk = 'none'
        with patch.object(cli, 'need_uefi', return_value=Path('uefi')), patch.object(cli.bootimg, 'build') as pack:
            cli.cmd_bootimg(self.ctx)
            self.assertIsNone(pack.call_args.args[4])


if __name__ == '__main__':
    unittest.main()
