import importlib.util
import json
from pathlib import Path
import struct
import sys
import tempfile
from types import SimpleNamespace
import unittest
import zlib

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
from macos_container import (PAGE, addon_entries, addon_path, copy_sparse, empty_seed, header,
                             mark_data, read_layout, seed_digest, bind_payload, apfs_checksum, mark_empty_xart)
from unixnu import userdata


class ContainerTests(unittest.TestCase):
    def fixture(self, directory, logical=3 << 30):
        pages = logical // PAGE
        offset = (1 + (pages + PAGE * 8 - 1) // (PAGE * 8)) * PAGE
        store = directory / 'data-store.img'
        with store.open('wb') as handle:
            handle.truncate(offset + logical)
            handle.write(header(pages, seed_digest(logical)))
            handle.seek(offset + 32)
            handle.write(b'NXSB')
            handle.seek(offset + logical - PAGE)
            handle.write(b'last-page')
        mark_data(store, offset, logical)
        (directory / 'scratch-data.img').write_bytes(empty_seed(logical))
        layout = dict(format='UniXNU.NativeAPFS.v1', bytes=logical, window_offset=offset,
                      **{name: dict(index=i, uuid=f'00000000-0000-0000-0000-{i:012d}')
                         for i, name in enumerate(('system', 'data', 'preboot', 'vm', 'update', 'hardware', 'xart'), 1)})
        (directory / 'disk.json').write_text(json.dumps(layout))
        return layout

    def test_payload_uses_the_restored_system_identity(self):
        with tempfile.TemporaryDirectory() as td:
            directory = Path(td)
            layout = self.fixture(directory)
            layout['source_system_uuid'] = 'SOURCE'
            (directory / 'disk.json').write_text(json.dumps(layout))
            ctx = SimpleNamespace(args=SimpleNamespace(apfs_container=str(directory)), board=dict(
                userdata=dict(source_system_uuid='SOURCE'), payload=dict(runtime=dict(container_layout=True, data_gib=3))))
            bind_payload(ctx)
            actual = layout['system']['uuid']
            self.assertEqual(ctx.board['payload']['adt']['root_match_volume_uuid'], actual)
            self.assertEqual(ctx.board['adt']['chosen']['string']['boot-uuid'], actual)
            self.assertEqual(ctx.board['adt']['chosen']['string']['apfs-preboot-uuid'], actual)
            with self.assertRaisesRegex(ValueError, 'IPSW System UUID'):
                read_layout(directory, expected_source_uuid='WRONG')

    def test_kernel_header_keeps_legacy_manifest_requirements(self):
        import subprocess
        text = (SCRIPTS / 'build-xnu-4k-baseline.sh').read_text()
        code = text.split("<<'PY_DATA_UUID'\n", 1)[1].split('\nPY_DATA_UUID', 1)[0]
        with tempfile.TemporaryDirectory() as td:
            header_path = Path(td) / 'owner.h'
            args = [str(header_path), '0', '1', '', '', '', '1', '']
            native = subprocess.run([sys.executable, '-c', code, *args, '1'], capture_output=True, text=True)
            self.assertEqual(native.returncode, 0, native.stderr)
            self.assertNotIn('XNU_OWNER_ROOT_VOLUME_UUID', header_path.read_text())
            legacy = subprocess.run([sys.executable, '-c', code, *args, '0'], capture_output=True, text=True)
            self.assertNotEqual(legacy.returncode, 0)
            self.assertIn('XNU_OWNER_ROOT_VOLUME_UUID', legacy.stderr)

    def test_xart_changes_only_empty_volume_role_and_checksum(self):
        import uuid
        identity = uuid.uuid4()
        block = bytearray(PAGE)
        struct.pack_into('<QQII', block, 8, 123, 9, 0x4000000d, 0)
        block[32:36] = b'APSB'
        block[240:256] = identity.bytes
        struct.pack_into('<Q', block, 192, 1)
        block[:8] = apfs_checksum(block[8:])
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'container'
            path.write_bytes(bytes(PAGE) + block + bytes(PAGE))
            self.assertEqual(mark_empty_xart(path, PAGE, 2 * PAGE, str(identity)), 1)
            result = path.read_bytes()
            changed = bytearray(result[PAGE:2 * PAGE])
            self.assertEqual(struct.unpack_from('<H', changed, 964)[0], 0x100)
            self.assertEqual(changed[:8], apfs_checksum(changed[8:]))
            changed[:8] = block[:8]
            struct.pack_into('<H', changed, 964, 0)
            self.assertEqual(changed, block)
            self.assertEqual(result[:PAGE], bytes(PAGE))
            struct.pack_into('<Q', block, 184, 1)
            block[:8] = apfs_checksum(block[8:])
            path.write_bytes(bytes(PAGE) + block + bytes(PAGE))
            before = path.read_bytes()
            with self.assertRaisesRegex(ValueError, 'new empty'):
                mark_empty_xart(path, PAGE, 2 * PAGE, str(identity))
            self.assertEqual(path.read_bytes(), before)

    def test_seed_identity_matches_driver_format(self):
        import hashlib
        logical = 210 << 30
        self.assertEqual(len(empty_seed(logical)), 32)
        self.assertEqual(seed_digest(logical), hashlib.sha256(b'SHNGSEED2' + struct.pack('<Q', logical)).hexdigest())
        block = header(logical // PAGE, seed_digest(logical))
        self.assertEqual(struct.unpack_from('<I', block, 60)[0], zlib.crc32(block[:60]))

    def test_store_bitmap_and_sparse_userdata_placement(self):
        with tempfile.TemporaryDirectory() as td:
            directory = Path(td)
            layout = self.fixture(directory)
            read_layout(directory, layout['system']['uuid'], 3)
            out = directory / 'out'
            spec = dict(first_lba=100, last_lba=100 + (5 << 30) // PAGE - 1, lba_bytes=PAGE, log_reserve_mib=1024)
            ctx = SimpleNamespace(tree=SCRIPTS.parent, work=out, args=SimpleNamespace(apfs_container=str(directory), object=[]),
                                  board=dict(payload=dict(runtime=dict(data_gib=3)), root=dict(os_volume_uuid=layout['system']['uuid'])))
            image = userdata.build_container(ctx, spec)
            report = json.loads((out / 'userdata/userdata-root.json').read_text())
            expected = (4 << 30) - (directory / 'data-store.img').stat().st_size
            self.assertEqual(report['store_offset'], expected)
            with image.open('rb') as handle:
                manifest = handle.read(PAGE)
                self.assertEqual(struct.unpack_from('<IIQ', manifest, 8), (3, 0, PAGE))
                handle.seek(expected + layout['window_offset'] + 32)
                self.assertEqual(handle.read(4), b'NXSB')
                handle.seek((4 << 30) - PAGE)
                self.assertEqual(handle.read(9), b'last-page')
            self.assertEqual(image.stat().st_size, 4 << 30)
            self.assertLess(image.stat().st_blocks * 512, 2 << 20)

    def test_native_store_clones_at_its_userdata_offset(self):
        with tempfile.TemporaryDirectory() as td:
            directory = Path(td)
            layout = self.fixture(directory)
            store = directory / 'data-store.img'
            base = (4 << 30) - store.stat().st_size
            embedded = directory / 'embedded.img'
            with embedded.open('wb') as target:
                target.truncate(4 << 30)
                copy_sparse(store, target, base)
            embedded.replace(store)
            layout['store_offset'] = base
            (directory / 'disk.json').write_text(json.dumps(layout))
            read_layout(directory, expected_gib=3)
            ctx = SimpleNamespace(tree=SCRIPTS.parent, work=directory / 'out',
                args=SimpleNamespace(apfs_container=str(directory), object=[]),
                board=dict(payload=dict(runtime=dict(data_gib=3))))
            spec = dict(first_lba=0, last_lba=(5 << 30) // PAGE - 1, log_reserve_mib=1024)
            image = userdata.build_container(ctx, spec)
            with image.open('rb') as target, store.open('rb') as source:
                self.assertEqual(target.read(8), b'SHNGROOT')
                self.assertEqual(source.read(8), bytes(8))
                target.seek(base)
                self.assertEqual(target.read(8), b'SHNGDATA')
            self.assertLess(image.stat().st_blocks * 512, 2 << 20)

    def test_foreign_seed_size_and_root_are_refused(self):
        with tempfile.TemporaryDirectory() as td:
            directory = Path(td)
            self.fixture(directory)
            with self.assertRaisesRegex(ValueError, 'System UUID'):
                read_layout(directory, 'wrong')
            with self.assertRaisesRegex(ValueError, 'size'):
                read_layout(directory, expected_gib=4)
            (directory / 'scratch-data.img').write_bytes(b'foreign')
            with self.assertRaisesRegex(ValueError, 'empty packed seed'):
                read_layout(directory)

    def test_missing_superblock_or_role_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            directory = Path(td)
            layout = self.fixture(directory)
            with (directory / 'data-store.img').open('r+b') as handle:
                handle.seek(PAGE)
                handle.write(b'\0')
            with self.assertRaisesRegex(ValueError, 'superblock'):
                read_layout(directory)
            self.fixture(directory)
            del layout['xart']
            (directory / 'disk.json').write_text(json.dumps(layout))
            with self.assertRaisesRegex(ValueError, 'xart'):
                read_layout(directory)

    def test_addon_routing_and_traversal(self):
        def pack(name):
            raw, body = name.encode() + b'\0', zlib.compress(b'payload')
            row = struct.pack('<IIQQ', len(raw), 0o755, 7, len(body)) + raw + bytes(-len(raw) % 8)
            row += body + bytes(-len(body) % 8)
            return struct.pack('<8sIIQ', b'NGPUADD2', 1, 0, 24 + len(row)) + row
        with tempfile.TemporaryDirectory() as td:
            file = Path(td) / 'addon'
            file.write_bytes(pack('sbin/BlueTool'))
            self.assertEqual(addon_entries(file)[0], ('sbin/BlueTool', 0o755, b'payload'))
            self.assertEqual(addon_path('sbin/BlueTool', True), 'usr/sbin/BlueTool')
            self.assertEqual(addon_path('Library/LaunchDaemons/wifi.plist', False), 'Library/LaunchDaemons/wifi.plist')
            self.assertEqual(addon_path('GPUBundles/Metal.bundle/Contents/MacOS/Metal', True),
                             'System/Library/Extensions/Metal.bundle/Contents/MacOS/Metal')
            file.write_bytes(pack('../escape'))
            with self.assertRaisesRegex(ValueError, 'path'):
                addon_entries(file)


if __name__ == '__main__':
    unittest.main()
