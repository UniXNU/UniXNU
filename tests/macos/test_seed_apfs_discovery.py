#!/usr/bin/env python3
"""Check delayed APFS publication without selecting another attached image."""
import contextlib
import importlib.util
import io
from pathlib import Path
import plistlib
import subprocess
import sys
import types
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[2] / 'scripts/seed-data-grow.py'
spec = importlib.util.spec_from_file_location('seed_grow', SOURCE)
grow = importlib.util.module_from_spec(spec)
with patch.dict(sys.modules, {'packed_ramdisk': types.ModuleType('packed_ramdisk')}):
    spec.loader.exec_module(grow)

UUID = 'CD519F1E-E281-449F-BBD7-12CE23DA617C'


def listing(store='disk99', identity=UUID, container='disk100'):
    return plistlib.dumps({'Containers': [{'ContainerReference': container, 'APFSContainerUUID': identity,
                                          'PhysicalStores': [{'DeviceIdentifier': store}]}]})


class SeedApfsDiscoveryTest(unittest.TestCase):
    def setUp(self):
        self.enterContext(contextlib.redirect_stdout(io.StringIO()))
        self.now = 0
        self.enterContext(patch.object(grow.time, 'monotonic', side_effect=lambda: self.now))
        self.sleep = self.enterContext(patch.object(grow.time, 'sleep', side_effect=self.advance))

    def advance(self, seconds):
        self.now += seconds

    def test_ready_container_does_not_sleep(self):
        with patch.object(grow.subprocess, 'check_output', return_value=listing()):
            self.assertEqual(grow.wait_for_container('disk99', UUID), 'disk100')
        self.sleep.assert_not_called()

    def test_waits_for_delayed_publication(self):
        with patch.object(grow.subprocess, 'check_output', side_effect=[
                plistlib.dumps({}), listing('disk1s2', container='disk2'), listing()]) as query:
            self.assertEqual(grow.wait_for_container('disk99', UUID), 'disk100')
        self.assertEqual(query.call_count, 3)
        self.assertEqual(self.now, 1)

    def test_transient_query_failures_are_retried(self):
        with patch.object(grow.subprocess, 'check_output', side_effect=[
                subprocess.CalledProcessError(1, ['diskutil']), subprocess.TimeoutExpired(['diskutil'], 1), listing()]):
            self.assertEqual(grow.wait_for_container('disk99', UUID), 'disk100')

    def test_other_store_and_same_uuid_do_not_match(self):
        with patch.object(grow.subprocess, 'check_output', return_value=listing('disk990')), \
                self.assertRaisesRegex(SystemExit, r'disk99 after 1s;.*observed disk100:disk990'):
            grow.wait_for_container('disk99', UUID, timeout=1)
        self.assertEqual(self.now, 1)

    def test_wrong_uuid_is_refused(self):
        with patch.object(grow.subprocess, 'check_output', return_value=listing(identity='other')), \
                self.assertRaisesRegex(SystemExit, 'UUID mismatch'):
            grow.wait_for_container('disk99', UUID)
        self.sleep.assert_not_called()

    def test_ambiguous_store_is_refused(self):
        duplicate = plistlib.loads(listing())
        duplicate['Containers'] *= 2
        with patch.object(grow.subprocess, 'check_output', return_value=plistlib.dumps(duplicate)), \
                self.assertRaisesRegex(SystemExit, 'Multiple APFS containers'):
            grow.wait_for_container('disk99', UUID)


if __name__ == '__main__':
    unittest.main()
