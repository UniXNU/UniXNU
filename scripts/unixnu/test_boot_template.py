#!/usr/bin/env python3
"""Offline firmware transport regressions with small synthetic firmware volumes."""
import gzip
import hashlib
import lzma
import os
from pathlib import Path
import struct
import sys
import tempfile
from types import SimpleNamespace
import unittest
import uuid
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from unixnu import boot_template as template
from unixnu import bootimg
from unixnu import cli
from unixnu.config import Context
from unixnu.util import Error

LOADER = '1b64af87-8415-4b57-9b16-680d70913b9f'
OTHER = '11111111-2222-3333-4444-555555555555'


def section(kind, body):
    return (len(body) + 4).to_bytes(3, 'little') + bytes([kind]) + body


def file(guid, body, kind=7):
    header = bytearray(uuid.UUID(guid).bytes_le + b'\0\xaa' + bytes([kind, 0]) + b'\0\0\0\xf8')
    template.put24(header, 20, 24 + len(body))
    template.file_checksum(header)
    return bytes(header) + body


def fv(files, size=None):
    data = bytearray(72)
    for item in files:
        data.extend(b'\xff' * (template.align(len(data), 8) - len(data)))
        data.extend(item)
    length = size or template.align(len(data), 4096)
    data.extend(b'\xff' * (length - len(data)))
    struct.pack_into('<Q', data, 32, length)
    data[40:44] = b'_FVH'
    struct.pack_into('<H', data, 48, 72)
    struct.pack_into('<II', data, 56, length // 4096, 4096)
    struct.pack_into('<H', data, 50, (-sum(struct.unpack_from('<36H', data))) & 65535)
    return bytes(data)


def firmware(pe=b'MZold'):
    inner = fv([file(LOADER, section(0x10, pe)), file(OTHER, section(0x10, b'MZuntouched'))])
    expanded = section(0x19, b'') + section(0x17, inner)
    compressed = lzma.compress(expanded, format=lzma.FORMAT_ALONE)
    guided = template.LZMA_GUID + struct.pack('<HH', 24, 1) + compressed
    return fv([file(OTHER, section(2, guided), kind=0x0b)], size=65536)


def boot_image(fd, ramdisk=b'payload'):
    shim = bytearray(192)
    shim[56:60] = b'ARMd'
    kernel = gzip.compress(bytes(shim) + fd, mtime=0) + b'\xd0\x0d\xfe\xed\0\0\0\x08'
    header = bytearray(4096)
    header[:8] = b'ANDROID!'
    struct.pack_into('<10I', header, 8, len(kernel), 0x8000, len(ramdisk), 0x1000000, 0, 0,
                     0x1e00000, 4096, 0, 0x220001a8)
    return bytes(header) + kernel + b'\0' * (template.align(len(kernel), 4096) - len(kernel)) + ramdisk


class BootTemplate(unittest.TestCase):
    def test_template_boot_image_needs_no_external_device_tree(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'Resources/Scripts').mkdir(parents=True)
            (root / 'Resources/Scripts/mkbootimg.py').touch()
            source = root / 'source.fd'
            source.write_bytes(firmware(b'MZcurrent'))
            archive = root / 'template.xz'
            archive.write_bytes(lzma.compress(boot_image(firmware())))
            spec = {'sha256': hashlib.sha256(archive.read_bytes()).hexdigest(), 'loader_guid': LOADER}
            ctx = SimpleNamespace(board={'bootimg': {'template': spec}}, work=root)

            def pack(command, **kwargs):
                kernel = Path(command[command.index('--kernel') + 1]).read_bytes()
                ramdisk = Path(command[command.index('--ramdisk') + 1]).read_bytes()
                header = bytearray(4096)
                header[:8] = b'ANDROID!'
                struct.pack_into('<10I', header, 8, len(kernel), 0x8000, len(ramdisk), 0x1000000 if ramdisk else 0,
                                 0, 0, 0x1e00000, 4096, 0, 0x220001a8)
                Path(command[command.index('-o') + 1]).write_bytes(
                    bytes(header) + kernel + b'\0' * (template.align(len(kernel), 4096) - len(kernel)) + ramdisk)

            with patch.dict('os.environ', UNIXNU_BOOT_TEMPLATE=str(archive)), \
                 patch.object(bootimg, 'settings', return_value=({}, 0, source.stat().st_size, True, {})), \
                 patch.object(bootimg, 'run', side_effect=pack):
                for dtb in (None, root / 'missing.dtb'):
                    with self.subTest(dtb=dtb):
                        output = bootimg.build(ctx, root, source, dtb)
                        _, selected, tree, _ = template.parse_boot_image(output.read_bytes())
                        self.assertEqual(template.loader_pe(selected, LOADER), b'MZcurrent')
                        self.assertEqual(tree, template.parse_boot_image(boot_image(firmware()))[2])

    def test_native_boot_image_still_requires_a_device_tree(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'Resources/Scripts').mkdir(parents=True)
            (root / 'Resources/Scripts/mkbootimg.py').touch()
            source = root / 'source.fd'
            source.write_bytes(b'F')
            ctx = SimpleNamespace(board={}, work=root)
            with patch.object(bootimg, 'settings', return_value=({}, 0, 1, True, {})):
                for dtb in (None, root / 'missing.dtb'):
                    with self.subTest(dtb=dtb), self.assertRaisesRegex(Error, r'device tree \(--dtb\) not found'):
                        bootimg.build(ctx, root, source, dtb)

    def test_bootimg_device_tree_option_precedence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for explicit, environment, configured, expected in (
                ('flag.dtb', 'env.dtb', 'board.dtb', Path('flag.dtb').resolve()),
                (None, 'env.dtb', 'board.dtb', Path('env.dtb').resolve()),
                (None, None, 'board.dtb', root / 'board.dtb'),
                (None, None, None, None),
            ):
                args = SimpleNamespace(fd='source.fd', dtb=explicit, ramdisk='none', output=None, target='DEBUG')
                ctx = SimpleNamespace(args=args, board={'bootimg': {'dtb': configured}}, tree=root)
                ctx.refuse_example = lambda: None
                ctx.option = lambda flag, env=None: Context.option(ctx, flag, env)
                env = {'UNIXNU_DTB': environment} if environment else {}
                with self.subTest(explicit=explicit, environment=environment, configured=configured), \
                     patch.dict(os.environ, env, clear=True), \
                     patch.object(cli, 'need_uefi', return_value=root), \
                     patch.object(bootimg, 'build') as build:
                    cli.cmd_bootimg(ctx)
                    self.assertEqual(build.call_args.args[3], expected)

    def test_larger_loader_preserves_every_other_module(self):
        source = firmware()
        updated, report = template.replace_loader(source, b'MZ' + b'new' * 4000, LOADER)
        self.assertEqual(len(updated), len(source))
        self.assertEqual(template.loader_pe(updated, LOADER), b'MZ' + b'new' * 4000)
        before = template.fv_files(template.compressed_volume(source)[4], 8)[2]
        after = template.fv_files(template.compressed_volume(updated)[4], 8)[2]
        self.assertEqual(before[1][2], after[1][2])
        self.assertEqual(report['preserved_modules'], 1)

    def test_header_metadata_is_read_from_offset_44(self):
        _, _, _, image = template.parse_boot_image(boot_image(firmware()))
        self.assertEqual(image['encoded_os_version'], 0x220001a8)
        self.assertEqual(image['os_version'], '17.0.0')
        self.assertEqual(image['os_patch_level'], '2026-08-01')

    def test_corrupt_firmware_checksum_is_rejected(self):
        data = bytearray(firmware())
        data[44] ^= 1
        with self.assertRaisesRegex(Error, 'checksum'):
            template.loader_pe(data, LOADER)

    def test_missing_loader_is_rejected(self):
        with self.assertRaisesRegex(Error, 'exactly one'):
            template.loader_pe(firmware(), '00000000-0000-0000-0000-000000000000')

    def test_truncated_firmware_and_boot_image_are_rejected(self):
        for data in (b'', firmware()[:100]):
            with self.assertRaises(Error):
                template.loader_pe(data, LOADER)
        with self.assertRaises(Error):
            template.parse_boot_image(boot_image(firmware())[:4100])

    def test_invalid_loader_and_extended_file_attributes_are_rejected(self):
        with self.assertRaisesRegex(Error, 'PE image'):
            template.replace_loader(firmware(), b'not an executable', LOADER)
        data = bytearray(firmware())
        data[72 + 19] = 0x38
        with self.assertRaisesRegex(Error, 'attributes'):
            template.loader_pe(data, LOADER)

    def test_wrong_template_pin_is_rejected_without_download(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'template.xz'
            path.write_bytes(b'wrong bytes')
            with patch.dict('os.environ', UNIXNU_BOOT_TEMPLATE=str(path)):
                with self.assertRaisesRegex(Error, 'checksum'):
                    template.template_file(SimpleNamespace(), {'sha256': '0' * 64})

    def test_template_preparation_uses_current_loader(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'template.xz'
            path.write_bytes(lzma.compress(boot_image(firmware()), format=lzma.FORMAT_XZ))
            spec = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'loader_guid': LOADER}
            with patch.dict('os.environ', UNIXNU_BOOT_TEMPLATE=str(path)):
                _, fd, _, _, report = template.prepare(SimpleNamespace(), spec, firmware(b'MZcurrent'))
            self.assertEqual(template.loader_pe(fd, LOADER), b'MZcurrent')
            self.assertEqual(report['loader_bytes'], len(b'MZcurrent'))

    def test_boot_verification_rejects_changed_os_metadata_or_ramdisk_address(self):
        data = boot_image(firmware())
        combined, _, tree, image = template.parse_boot_image(data)
        combined += firmware()
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            ramdisk = directory / 'payload'
            ramdisk.write_bytes(b'payload')
            path = directory / 'boot.img'
            path.write_bytes(data)
            bootimg.verify(path, combined, tree, ramdisk, image)
            for offset in (20, 44):
                changed = bytearray(data)
                changed[offset] ^= 1
                path.write_bytes(changed)
                with self.assertRaises(Error):
                    bootimg.verify(path, combined, tree, ramdisk, image)

    def test_failed_repack_preserves_the_previous_boot_image(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'Resources/Scripts').mkdir(parents=True)
            (root / 'Resources/Scripts/mkbootimg.py').touch()
            fd, tree, output = root / 'source.fd', root / 'tree.dtb', root / 'boot.img'
            fd.write_bytes(b'F')
            tree.write_bytes(b'T')
            output.write_bytes(b'previous verified image')
            ctx = SimpleNamespace(board={'bootimg': {'template': {'enabled': True}, 'max_image_bytes': 4}}, work=root)

            def oversized(command, **kwargs):
                Path(command[command.index('-o') + 1]).write_bytes(b'oversized')

            with patch.object(bootimg, 'settings', return_value=({'header_version': 0}, 0, 1, True, {})), \
                 patch.object(template, 'prepare', return_value=(b'S', b'F', b'T', {}, {})), \
                 patch.object(bootimg, 'run', side_effect=oversized):
                with self.assertRaisesRegex(Error, 'qualified limit'):
                    bootimg.build(ctx, root, fd, tree, output=output)
            self.assertEqual(output.read_bytes(), b'previous verified image')


if __name__ == '__main__':
    unittest.main()
