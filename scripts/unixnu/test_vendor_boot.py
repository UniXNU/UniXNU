#!/usr/bin/env python3
"""Offline tests of vendor_boot.py with a synthetic v4 image: repacking, the ramdisk
address, the partition limit and the refusals.

    python3 scripts/unixnu/test_vendor_boot.py
"""
import struct
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from unixnu import vendor_boot

PAGE = 4096


def build_stock(ramdisk=b'R' * 0x3000, dtb=b'D' * 0x800, bootconfig=b'BC' * 8, vbmeta=b'V' * 640,
                partition=0x100000):
    """A vendor_boot v4 laid out the way the stock images are: parts page aligned and
    an AVB footer in the last 64 bytes pointing at the vbmeta blob."""
    header = bytearray(PAGE)
    header[0:8] = b'VNDRBOOT'
    struct.pack_into('<2I', header, 8, 4, PAGE)
    struct.pack_into('<I', header, 20, 0x01000000)      # ramdisk address
    struct.pack_into('<I', header, 24, len(ramdisk))    # vendor ramdisk size
    struct.pack_into('<I', header, 2100, len(dtb))      # dtb size
    table = bytearray(108)
    struct.pack_into('<2I', table, 0, len(ramdisk), 0)
    struct.pack_into('<4I', header, vendor_boot.TABLE_OFFSET, len(table), 1, 108, len(bootconfig))

    dtb_at = vendor_boot.align(PAGE + len(ramdisk))
    table_at = vendor_boot.align(dtb_at + len(dtb))
    bootconfig_at = vendor_boot.align(table_at + len(table))
    vbmeta_at = vendor_boot.align(bootconfig_at + len(bootconfig))
    image = bytearray(max(partition, vendor_boot.align(vbmeta_at + len(vbmeta))))
    image[0:PAGE] = header
    image[PAGE:PAGE + len(ramdisk)] = ramdisk
    image[dtb_at:dtb_at + len(dtb)] = dtb
    image[table_at:table_at + len(table)] = table
    image[bootconfig_at:bootconfig_at + len(bootconfig)] = bootconfig
    image[vbmeta_at:vbmeta_at + len(vbmeta)] = vbmeta
    footer = bytearray(64)
    footer[0:4] = b'AVBf'
    struct.pack_into('>3Q', footer, 12, vbmeta_at, vbmeta_at, len(vbmeta))
    image[-64:] = footer
    return bytes(image)


class VendorBoot(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.stock = self.dir / 'stock.img'
        self.stock.write_bytes(build_stock())

    def tearDown(self):
        self.tmp.cleanup()

    def test_repacking_the_stock_ramdisk_is_byte_identical(self):
        parts = vendor_boot.parse(self.stock.read_bytes())
        rebuilt, report = vendor_boot.pack(parts, parts['ramdisk'], parts['ramdisk_address'])
        self.assertEqual(rebuilt, self.stock.read_bytes())
        self.assertEqual(report['ramdisk_bytes'], len(parts['ramdisk']))

    def test_verify_against_accepts_the_stock_image(self):
        out = self.dir / 'out.img'
        vendor_boot.build(self.stock, b'R' * 0x3000, out, verify_against=True)
        self.assertEqual(out.read_bytes(), self.stock.read_bytes())

    def test_a_larger_ramdisk_moves_the_parts_and_updates_the_table(self):
        ramdisk = b'N' * 0x9000
        out = self.dir / 'big.img'
        vendor_boot.build(self.stock, ramdisk, out)
        data = out.read_bytes()
        self.assertEqual(data[PAGE:PAGE + len(ramdisk)], ramdisk)
        self.assertEqual(struct.unpack_from('<I', data, 24)[0], len(ramdisk))
        table_at = vendor_boot.align(vendor_boot.align(PAGE + len(ramdisk)) + 0x800)
        self.assertEqual(struct.unpack_from('<2I', data, table_at), (len(ramdisk), 0))
        parts = vendor_boot.parse(data)
        self.assertEqual(parts['dtb'], b'D' * 0x800)
        self.assertEqual(parts['bootconfig'], b'BC' * 8)

    def test_the_ramdisk_address_is_relocated_on_request(self):
        out = self.dir / 'addr.img'
        vendor_boot.build(self.stock, b'N' * 0x1000, out, ramdisk_address=0x40000000)
        self.assertEqual(struct.unpack_from('<I', out.read_bytes(), 20)[0], 0x40000000)

    def test_a_ramdisk_past_the_partition_is_refused(self):
        with self.assertRaises(vendor_boot.Error):
            vendor_boot.build(self.stock, b'N' * len(self.stock.read_bytes()), self.dir / 'x.img')

    def test_an_image_that_is_not_vendor_boot_is_refused(self):
        with self.assertRaises(vendor_boot.Error):
            vendor_boot.parse(b'ANDROID!' + b'\0' * PAGE)

    def test_an_empty_ramdisk_is_allowed(self):
        out = self.dir / 'empty.img'
        vendor_boot.build(self.stock, None, out)
        self.assertEqual(struct.unpack_from('<I', out.read_bytes(), 24)[0], 0)


if __name__ == '__main__':
    unittest.main()
