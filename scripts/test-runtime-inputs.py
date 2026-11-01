#!/usr/bin/env python3
"""Regressions for first-install input handling and fileset startup gaps."""
import argparse
import copy
import json
from pathlib import Path
import struct
import tempfile
import unittest
import uuid
from unittest.mock import patch

from unixnu.config import parse_config
from unixnu.kernel import check_prelink_regressions
from unixnu import runtime
from unixnu.util import Error

ROOT = Path(__file__).resolve().parents[1]
IDENTITY = '2A5E9027-D9E1-40F9-983C-41BD3F1994F5'


def seed(path):
    block = bytearray(4096)
    block[32:36] = b'APSB'
    block[240:256] = uuid.UUID(IDENTITY).bytes
    path.write_bytes(struct.pack('<8sIIQQ', b'DBRDISK1', 1, 4096, 4096, 1) + struct.pack('<QQ', 0, 4096) + block)


class RuntimeInputs(unittest.TestCase):
    def context(self, out, explicit=True):
        work = out / 'runtime'
        work.mkdir()
        data = work / 'data.dbr'
        seed(data)
        trust, addon = work / 'trust.bundle', work / 'addon.bin'
        trust.write_bytes(b'trust')
        addon.write_bytes(b'NGPUADD2')
        config = out / '.config'
        config.write_text(f'CONFIG_XNU_OWNER_DATA_MOUNT=y\nCONFIG_XNU_OWNER_DATA_VOLUME_UUID="{IDENTITY}"\n')
        return argparse.Namespace(
            board={'payload': {'runtime': {'tool': 'scripts/build-boot-runtime.py'}}},
            tree=ROOT, device=out, work=out, config_path=config,
            need_config=lambda: parse_config(config.read_text()),
            args=argparse.Namespace(data_ramdisk=str(data) if explicit else None,
                                    owner_trust_cache=str(trust), trust_cache=None, gpu_addon=str(addon), init_data=False))

    def test_reuse_keeps_seed_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            ctx = self.context(Path(td))
            before = Path(ctx.args.data_ramdisk).read_bytes()
            with patch.object(runtime, 'Ipsw', side_effect=AssertionError('must not fetch or regenerate explicit inputs')):
                runtime.prepare(ctx, kernel_build=True)
            self.assertEqual(Path(ctx.args.data_ramdisk).read_bytes(), before)
            self.assertEqual(runtime.seed_uuid(ROOT, Path(ctx.args.data_ramdisk)), IDENTITY)

    def test_missing_cache_requires_first_install(self):
        with tempfile.TemporaryDirectory() as td:
            ctx = self.context(Path(td), explicit=False)
            (ctx.work / 'runtime/data.dbr').unlink()
            with patch.object(runtime, 'Ipsw', side_effect=AssertionError('must fail before fetching')):
                with self.assertRaisesRegex(Error, 'FIRST installation'):
                    runtime.prepare(ctx, kernel_build=True)

    def test_payload_cannot_change_compiled_uuid(self):
        with tempfile.TemporaryDirectory() as td:
            ctx = self.context(Path(td))
            ctx.config_path.write_text('CONFIG_XNU_OWNER_DATA_VOLUME_UUID="00000000-0000-0000-0000-000000000000"\n')
            with self.assertRaisesRegex(Error, 'rebuild the kernel'):
                runtime.prepare(ctx)
            runtime.prepare(ctx, kernel_build=True)
            self.assertEqual(ctx.need_config()['XNU_OWNER_DATA_VOLUME_UUID'], IDENTITY)

    def test_new_gap_rejected_but_resolved_gap_allowed(self):
        policy = dict(missing={}, stubbed={'owner': {'0x1000': 1}}, required_original_branches=['adapter'])
        record = dict(collection_slide='0x100', missing={}, stubbed={'owner': {'0x1100': 1}},
                      native_original_branches=[{'symbol': 'adapter'}])
        check_prelink_regressions(record, policy)
        worse = copy.deepcopy(record)
        worse['stubbed']['owner']['0x1200'] = 1
        with self.assertRaisesRegex(Error, 'prelink regression'):
            check_prelink_regressions(worse, policy)
        record['stubbed'] = {}
        check_prelink_regressions(record, policy)
        record['native_original_branches'] = []
        with self.assertRaisesRegex(Error, 'adapter branch'):
            check_prelink_regressions(record, policy)


if __name__ == '__main__':
    unittest.main()
