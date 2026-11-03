"""Android vendor_boot v4: replace the vendor ramdisk, keep everything else stock.

GKI devices carry no ramdisk in `boot` (ramdisk_size is 0) and a vendor ABL
rejects one there, so anything large that has to reach the bootloader belongs in
`vendor_boot`'s vendor ramdisk. This rebuilds that image from the stock one:
the device tree, the ramdisk table, the bootconfig and the vbmeta blob are
copied verbatim, and only the ramdisk bytes, the header's vendor_ramdisk_size,
the ramdisk address and each table entry's size/offset change. The AVB footer at
the end of the partition is retargeted, because the vbmeta blob moves.

Layout as written by the stock images this was checked against:

    header (2128 B, padded to the page)
    vendor ramdisk            @ page
    dtb                       @ page-align(ramdisk end)
    vendor ramdisk table      @ page-align(dtb end)   entry = size, offset, type
    bootconfig                @ page-align(table end)
    vbmeta                    @ page-align(bootconfig end)
    AVB footer                last 64 bytes, big endian

--verify-against rebuilds an image from the stock ramdisk and requires the
result to equal the stock image byte for byte. Run it once per device before
trusting the tool with a rewritten ramdisk.
"""
import hashlib
import json
import struct
from pathlib import Path

from .util import Error, log

PAGE = 4096
VERSION = 4
HEADER_MAGIC = b'VNDRBOOT'
TABLE_OFFSET = 28 + 2048 + 4 + 16 + 8 + 8
FOOTER_MAGIC = b'AVBf'


def align(value, alignment=PAGE):
    return -(-value // alignment) * alignment


def parse(stock):
    """Split a vendor_boot v4 image into the parts this tool moves and copies."""
    data = stock
    if data[:8] != HEADER_MAGIC:
        raise Error('not a vendor_boot image: header magic missing')
    version, page = struct.unpack_from('<2I', data, 8)
    if version != VERSION:
        raise Error(f'vendor_boot v{version} is not supported; only v4 has the ramdisk table')
    if page != PAGE:
        raise Error(f'unexpected vendor_boot page size {page}')
    ramdisk_size = struct.unpack_from('<I', data, 24)[0]
    ramdisk_address = struct.unpack_from('<I', data, 20)[0]
    dtb_size = struct.unpack_from('<I', data, 2100)[0]
    table_size, table_count, table_entry, bootconfig_size = struct.unpack_from('<4I', data, TABLE_OFFSET)

    dtb_start = align(PAGE + ramdisk_size)
    table_start = align(dtb_start + dtb_size)
    bootconfig_start = align(table_start + table_size)
    vbmeta_start = align(bootconfig_start + bootconfig_size)

    footer = data[-64:]
    vbmeta = b''
    if footer[:4] == FOOTER_MAGIC:
        _major, _minor = struct.unpack_from('<2I', footer, 4)
        _original, vbmeta_offset, vbmeta_size = struct.unpack_from('>3Q', footer, 12)
        if vbmeta_offset + vbmeta_size > len(data):
            raise Error('AVB footer points outside the image')
        vbmeta = data[vbmeta_offset:vbmeta_offset + vbmeta_size]

    return {
        'header': data[:PAGE],
        'ramdisk': data[PAGE:PAGE + ramdisk_size],
        'ramdisk_address': ramdisk_address,
        'dtb': data[dtb_start:dtb_start + dtb_size],
        'table': bytearray(data[table_start:table_start + table_size]),
        'table_count': table_count,
        'table_entry': table_entry,
        'bootconfig': data[bootconfig_start:bootconfig_start + bootconfig_size],
        'vbmeta': vbmeta,
        'footer': footer,
        'partition_bytes': len(data),
    }


def pack(parts, ramdisk, ramdisk_address=None):
    """Lay the image out again around a new ramdisk."""
    dtb_start = align(PAGE + len(ramdisk))
    table_start = align(dtb_start + len(parts['dtb']))
    bootconfig_start = align(table_start + len(parts['table']))
    vbmeta_start = align(bootconfig_start + len(parts['bootconfig']))
    total = vbmeta_start + len(parts['vbmeta'])
    if total > parts['partition_bytes']:
        raise Error(f'image needs {total} bytes but the partition holds {parts["partition_bytes"]}')

    header = bytearray(parts['header'])
    struct.pack_into('<I', header, 24, len(ramdisk))
    address = parts['ramdisk_address'] if ramdisk_address is None else ramdisk_address
    struct.pack_into('<I', header, 20, address)
    table = bytearray(parts['table'])
    for index in range(parts['table_count']):
        struct.pack_into('<2I', table, index * parts['table_entry'], len(ramdisk), 0)

    image = bytearray(parts['partition_bytes'])
    image[0:PAGE] = header
    image[PAGE:PAGE + len(ramdisk)] = ramdisk
    image[dtb_start:dtb_start + len(parts['dtb'])] = parts['dtb']
    image[table_start:table_start + len(table)] = table
    image[bootconfig_start:bootconfig_start + len(parts['bootconfig'])] = parts['bootconfig']
    image[vbmeta_start:vbmeta_start + len(parts['vbmeta'])] = parts['vbmeta']
    if parts['vbmeta']:
        footer = bytearray(parts['footer'])
        struct.pack_into('>3Q', footer, 12, vbmeta_start, vbmeta_start, len(parts['vbmeta']))
        image[-64:] = footer
    return bytes(image), {'ramdisk_bytes': len(ramdisk), 'ramdisk_address': address, 'dtb_offset': dtb_start,
                          'table_offset': table_start, 'bootconfig_offset': bootconfig_start,
                          'vbmeta_offset': vbmeta_start}


def build(stock, ramdisk, output=None, ramdisk_address=None, verify_against=False):
    """Write a vendor_boot image whose vendor ramdisk is `ramdisk`."""
    stock = Path(stock)
    if not stock.is_file():
        raise Error(f'stock vendor_boot not found: {stock}')
    stock_bytes = stock.read_bytes()
    parts = parse(stock_bytes)

    if verify_against:
        # Rebuild from the stock ramdisk: anything but an identical image means the
        # layout assumptions above are wrong for this device.
        rebuilt, _ = pack(parts, parts['ramdisk'], parts['ramdisk_address'])
        if rebuilt != stock_bytes:
            raise Error('repacking the stock ramdisk did not reproduce the stock image; '
                        'the layout of this vendor_boot is not the one this tool assumes')
        log(f'vendor_boot: {stock.name} reproduces byte for byte from its own ramdisk')

    if ramdisk in (None, 'none', ''):
        payload = b''
    elif isinstance(ramdisk, (bytes, bytearray)):
        payload = bytes(ramdisk)
    else:
        path = Path(ramdisk)
        if not path.is_file():
            raise Error(f'ramdisk not found: {path}')
        payload = path.read_bytes()

    image, report = pack(parts, payload, ramdisk_address)
    out = Path(output) if output else stock.with_name('vendor_boot.img')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(image)

    report.update(image_sha256=hashlib.sha256(image).hexdigest(), image_bytes=len(image),
                  stock_sha256=hashlib.sha256(stock_bytes).hexdigest(), stock=stock.name)
    (out.parent / 'vendor_boot.json').write_text(json.dumps(report, indent=2) + '\n')
    log(f'vendor_boot: {out} ({len(image)} bytes), ramdisk {len(payload)} bytes at 0x{PAGE:x}, '
        f'address 0x{report["ramdisk_address"]:x}')
    return out
